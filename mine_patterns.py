"""Extract one feature row per seat per episode, then say what correlates with winning.

Two things make this different from the earlier per-opponent tools:

* It reads **state**, not action attempts. A replay records 589 HIRE orders in a
  game that ends with 11 hands -- the market rejects most of them. Anything
  counted from the action stream (hires, land, animals) is an attempt; anything
  counted off `observation.farms[seat]` is what actually happened.
* It **streams**. The daily dumps are ~21 GB a day and ~320 GB across the
  manifest, so `--date` downloads an episode, extracts its row, and deletes the
  file. Net disk stays flat and the feature CSV is a few hundred KB.

    python mine_patterns.py --dirs kaggle_episode_data/replays        # on disk
    python mine_patterns.py --date 2026-08-13 --sample 120            # stream
    python mine_patterns.py --report                                  # analyse

Rows accumulate in kaggle_episode_data/patterns.csv across runs, keyed by
(episode, seat), so repeated runs add data instead of replacing it.
"""
import argparse
import collections
import csv
import glob
import json
import math
import os
import statistics
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = os.path.join(PROJECT, "kaggle_episode_data", "patterns.csv")
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]
PRODUCTS = CROPS + ["EGG", "MILK", "WOOL", "FERTILIZER"]
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
SNAPSHOT_DAYS = [5, 10, 15, 20, 25, 30]

FIELDS = (
    ["episode", "seat", "team", "score", "opp_score", "won", "margin"]
    + [f"hands_d{d}" for d in SNAPSHOT_DAYS]
    + [f"quads_d{d}" for d in SNAPSHOT_DAYS]
    + [f"money_d{d}" for d in SNAPSHOT_DAYS]
    + [f"tiles_{c}" for c in CROPS]
    + [f"peak_{c}" for c in CROPS]
    + [f"animals_{a}" for a in ANIMALS]
    # hands_peak, not a final-day count: the crew is cleared every night and
    # re-hired each morning, so sampling the last observation of day 30 reads
    # whatever is left after the season stops re-hiring. That artifact made
    # fistyee look like a 4-hand agent when it runs 13 mid-season.
    + ["plant_total", "first_melon_day", "first_animal_day", "quads_final", "hands_peak"]
    + ["act_total", "act_move", "act_pass", "act_water", "act_harvest", "act_plant",
       "act_care", "act_feed", "act_dig", "act_fertilize", "act_collect_fert",
       "act_pickup", "act_drop", "act_place", "act_build"]
    + ["move_share", "pass_share", "work_share"]
    + [f"sold_{p}" for p in PRODUCTS]
    + ["sold_total", "sell_orders", "buy_seed_orders", "buy_product_orders"]
)


def tile_iter(farm):
    for row in farm.get("tiles") or []:
        if not isinstance(row, list):
            continue
        for cell in row:
            yield cell


def snapshot(farm):
    """(hands, quadrants, money, crop tile counts, animal counts)."""
    crops = collections.Counter()
    animals = collections.Counter()
    for cell in tile_iter(farm):
        if not isinstance(cell, dict):
            continue
        if cell.get("kind") == "PLANT":
            crops[cell.get("crop")] += 1
        elif "animal" in cell:
            animals[cell["animal"]] += 1
    return (len(farm.get("hands") or []), len(farm.get("unlocked_quadrants") or []),
            int(farm.get("money", 0)), crops, animals)


def extract(path):
    """Feature rows for both seats of one episode, or []."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    steps = raw.get("steps") or []
    if len(steps) < 2:
        return []
    teams = (raw.get("info", {}) or {}).get("TeamNames") or ["?", "?"]
    rewards = [s.get("reward") for s in steps[-1]]
    if any(r is None for r in rewards):
        return []
    episode = os.path.splitext(os.path.basename(path))[0]
    episode = episode.replace("episode-", "").replace("-replay", "")

    rows = []
    for seat in (0, 1):
        row = {k: 0 for k in FIELDS}
        row.update(episode=episode, seat=seat, team=teams[seat] if seat < len(teams) else "?",
                   score=round(rewards[seat]), opp_score=round(rewards[1 - seat]),
                   won=int(rewards[seat] > rewards[1 - seat]),
                   margin=round(rewards[seat] - rewards[1 - seat]),
                   first_melon_day=-1, first_animal_day=-1)

        peak = collections.Counter()
        planted_seen = 0
        by_day = {}
        for step in steps:
            if seat >= len(step):
                continue
            entry = step[seat]
            obs = entry.get("observation") or {}
            day = obs.get("day")
            farms = obs.get("farms")
            if isinstance(farms, list) and len(farms) > seat and isinstance(farms[seat], dict):
                farm = farms[seat]
                hands, quads, money, crops, animals = snapshot(farm)
                if day is not None:
                    by_day[day] = (hands, quads, money)
                for c in CROPS:
                    peak[c] = max(peak[c], crops[c])
                for a in ANIMALS:
                    row[f"animals_{a}"] = max(row[f"animals_{a}"], animals[a])
                if crops["MELON"] and row["first_melon_day"] < 0 and day is not None:
                    row["first_melon_day"] = day
                if sum(animals.values()) and row["first_animal_day"] < 0 and day is not None:
                    row["first_animal_day"] = day
                row["quads_final"] = max(row["quads_final"], quads)
                row["hands_peak"] = max(row["hands_peak"], hands)

            action = entry.get("action") or {}
            cmds = [action.get("farmer") or []] + [h or [] for h in (action.get("hands") or [])]
            for cmd in cmds:
                if not cmd:
                    continue
                op = cmd[0]
                row["act_total"] += 1
                if op in MOVES:
                    row["act_move"] += 1
                elif op == "PASS":
                    row["act_pass"] += 1
                elif op == "WATER":
                    row["act_water"] += 1
                elif op == "HARVEST":
                    row["act_harvest"] += 1
                elif op == "PLANT":
                    row["act_plant"] += 1
                    planted_seen += 1
                    if len(cmd) > 1 and cmd[1] in CROPS:
                        row[f"tiles_{cmd[1]}"] += 1
                elif op == "CARE":
                    row["act_care"] += 1
                elif op == "FEED":
                    row["act_feed"] += 1
                elif op == "DIG":
                    row["act_dig"] += 1
                elif op == "FERTILIZE":
                    row["act_fertilize"] += 1
                elif op == "COLLECT_FERTILIZER":
                    row["act_collect_fert"] += 1
                elif op == "PICKUP":
                    row["act_pickup"] += 1
                elif op == "DROP":
                    row["act_drop"] += 1
                elif op == "PLACE":
                    row["act_place"] += 1
                elif op.startswith("BUILD_"):
                    row["act_build"] += 1

            for order in (action.get("market") or []):
                if not order:
                    continue
                kind = order[0]
                if kind == "SELL":
                    row["sell_orders"] += 1
                    if len(order) > 2 and order[1] in PRODUCTS:
                        try:
                            row[f"sold_{order[1]}"] += int(order[2])
                        except (TypeError, ValueError):
                            pass
                elif kind == "BUY_SEED":
                    row["buy_seed_orders"] += 1
                elif kind == "BUY_PRODUCT":
                    row["buy_product_orders"] += 1

        for c in CROPS:
            row[f"peak_{c}"] = peak[c]
        row["plant_total"] = planted_seen
        row["sold_total"] = sum(row[f"sold_{p}"] for p in PRODUCTS)
        act = row["act_total"] or 1
        row["move_share"] = round(row["act_move"] / act, 4)
        row["pass_share"] = round(row["act_pass"] / act, 4)
        row["work_share"] = round(1 - (row["act_move"] + row["act_pass"]) / act, 4)
        for d in SNAPSHOT_DAYS:
            # Days are 1-based; fall back to the latest day at or before d.
            pick = max((k for k in by_day if k <= d), default=None)
            if pick is not None:
                h, q, m = by_day[pick]
                row[f"hands_d{d}"], row[f"quads_d{d}"], row[f"money_d{d}"] = h, q, m
        rows.append(row)
    return rows


def load_existing():
    if not os.path.exists(OUT):
        return {}
    with open(OUT, encoding="utf-8") as fh:
        return {(r["episode"], r["seat"]): r for r in csv.DictReader(fh)}


def save(rows):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writeheader()
        for r in rows.values():
            w.writerow(r)


def harvest_dirs(dirs, store):
    files = []
    for d in dirs:
        files += sorted(glob.glob(os.path.join(d, "**", "*.json"), recursive=True))
    added = 0
    for i, path in enumerate(files, 1):
        episode = os.path.splitext(os.path.basename(path))[0]
        episode = episode.replace("episode-", "").replace("-replay", "")
        if (episode, "0") in store or (episode, 0) in store:
            continue
        try:
            for row in extract(path):
                store[(row["episode"], row["seat"])] = row
                added += 1
        except Exception as exc:
            print(f"  ! {os.path.basename(path)}: {exc}")
        if i % 25 == 0:
            print(f"  {i}/{len(files)}  (+{added} rows)")
    return added


def harvest_date(date, sample, store):
    """Download, extract, delete -- so a 21 GB day costs ~31 MB of disk at a time."""
    from fetch_daily_episodes import list_files, fetch
    slug = f"kaggle/kaggriculture-episodes-{date}"
    tmp = os.path.join(PROJECT, "kaggle_episode_data", "daily", "_stream")
    os.makedirs(tmp, exist_ok=True)
    print(f"listing {slug} ...")
    names = list_files(slug, sample)
    print(f"  {len(names)} episodes; streaming one at a time")
    added = 0
    for i, name in enumerate(names, 1):
        episode = name[:-5]
        if (episode, "0") in store or (episode, 0) in store:
            continue
        path = fetch(slug, name, tmp)
        if not path:
            continue
        try:
            for row in extract(path):
                store[(row["episode"], row["seat"])] = row
                added += 1
        except Exception as exc:
            print(f"  ! {name}: {exc}")
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
        if i % 10 == 0:
            print(f"  {i}/{len(names)}  (+{added} rows)")
    return added


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else 0.0


NUMERIC = [f for f in FIELDS if f not in ("episode", "seat", "team", "score", "opp_score",
                                          "won", "margin")]


def report(store, mine):
    rows = []
    for r in store.values():
        try:
            rows.append({k: (v if k in ("episode", "team") else float(v)) for k, v in r.items()})
        except (TypeError, ValueError):
            continue
    if len(rows) < 8:
        print(f"only {len(rows)} rows -- harvest more before reporting")
        return

    scores = [r["score"] for r in rows]
    print(f"\n{len(rows)} seat-rows from {len({r['episode'] for r in rows})} episodes")
    print(f"score  min {min(scores):,.0f}   median {statistics.median(scores):,.0f}   "
          f"max {max(scores):,.0f}")

    # --- what correlates with the score itself -------------------------------
    print("\n" + "=" * 74)
    print("FEATURE vs SCORE   (Pearson r over all seats; |r| > .30 is worth a look)")
    print("=" * 74)
    corr = []
    for f in NUMERIC:
        col = [r[f] for r in rows]
        if len(set(col)) < 2:
            continue
        corr.append((pearson(col, scores), f))
    corr.sort(key=lambda t: -abs(t[0]))
    for r_, f in corr[:22]:
        bar = "#" * int(abs(r_) * 40)
        print(f"  {f:<22}{r_:+.3f}  {bar}")

    # --- top decile vs bottom decile -----------------------------------------
    ranked = sorted(rows, key=lambda r: -r["score"])
    k = max(3, len(ranked) // 10)
    top, bot = ranked[:k], ranked[-k:]
    print("\n" + "=" * 74)
    print(f"TOP {k} SEATS vs BOTTOM {k}"
          + (f"   vs YOU ({mine})" if mine else ""))
    print("=" * 74)
    ours = [r for r in rows if mine and mine.lower() in r["team"].lower()]
    head = f"  {'feature':<22}{'top':>12}{'bottom':>12}"
    if ours:
        head += f"{'you':>12}{'you vs top':>13}"
    print(head + f"\n  {'-' * (len(head) - 2)}")
    # sold_* and every act_* are *attempts*: the market silently rejects a SELL
    # the shed cannot cover, and some agents spam huge quantities every turn
    # (one cluster "sells" 13,000 melon a game). Treat them as intent, never as
    # volume. Everything read off farm state is real.
    interesting = [
        "score", "hands_peak", "quads_d5", "quads_final", "money_d10", "money_d20", "money_d25",
        "plant_total", "peak_WHEAT", "peak_STRAWBERRY", "peak_MELON", "peak_TOMATO",
        "peak_CARROT", "animals_GOOSE", "animals_COW", "animals_SHEEP",
        "first_melon_day", "move_share", "work_share", "pass_share",
        "act_care", "act_water", "act_harvest", "act_fertilize", "act_dig",
        "sold_total", "sell_orders",
    ]
    for f in interesting:
        t = statistics.mean(r[f] for r in top)
        b = statistics.mean(r[f] for r in bot)
        line = f"  {f:<22}{t:>12,.1f}{b:>12,.1f}"
        if ours:
            o = statistics.mean(r[f] for r in ours)
            delta = o - t
            line += f"{o:>12,.1f}{delta:>+13,.1f}"
        print(line)

    # --- head-to-head: winner minus loser, same episode ----------------------
    print("\n" + "=" * 74)
    print("WINNER minus LOSER, paired within each episode")
    print("=" * 74)
    pairs = collections.defaultdict(list)
    for r in rows:
        pairs[r["episode"]].append(r)
    diffs = collections.defaultdict(list)
    n_pairs = 0
    for eps in pairs.values():
        if len(eps) != 2:
            continue
        w, l = (eps[0], eps[1]) if eps[0]["score"] > eps[1]["score"] else (eps[1], eps[0])
        n_pairs += 1
        for f in NUMERIC:
            diffs[f].append(w[f] - l[f])
    ranked_d = []
    for f, vals in diffs.items():
        if not vals:
            continue
        m = statistics.mean(vals)
        sd = statistics.pstdev(vals) or 1e-9
        ranked_d.append((abs(m / sd), m, f))          # effect size, not raw size
    ranked_d.sort(reverse=True)
    print(f"  {n_pairs} paired episodes; ranked by effect size (mean / sd)")
    print(f"  {'feature':<22}{'mean diff':>13}{'effect':>9}")
    for eff, m, f in ranked_d[:18]:
        print(f"  {f:<22}{m:>+13,.1f}{eff:>9.2f}")

    # --- team leaderboard ----------------------------------------------------
    print("\n" + "=" * 74)
    print("TEAMS BY MEAN SCORE  (>=3 seat-rows)")
    print("=" * 74)
    byteam = collections.defaultdict(list)
    for r in rows:
        byteam[r["team"]].append(r)
    board = [(statistics.mean(v["score"] for v in vs), len(vs), t)
             for t, vs in byteam.items() if len(vs) >= 3]
    board.sort(reverse=True)
    print(f"  {'team':<30}{'n':>5}{'mean':>11}{'hands':>7}{'quads':>7}{'move%':>7}{'care':>7}")
    for mean, n, t in board[:20]:
        vs = byteam[t]
        print(f"  {t[:29]:<30}{n:>5}{mean:>11,.0f}"
              f"{statistics.mean(v['hands_final'] for v in vs):>7.1f}"
              f"{statistics.mean(v['quads_final'] for v in vs):>7.1f}"
              f"{statistics.mean(v['move_share'] for v in vs) * 100:>7.1f}"
              f"{statistics.mean(v['act_care'] for v in vs):>7.0f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="*", default=[], help="directories of replay JSON")
    ap.add_argument("--date", default=None, help="stream a day's dump: download, extract, delete")
    ap.add_argument("--sample", type=int, default=60)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--mine", default=None, help="your team name, to contrast against the field")
    args = ap.parse_args()

    store = load_existing()
    print(f"{len(store)} rows already in {os.path.relpath(OUT, PROJECT)}")

    added = 0
    if args.dirs:
        added += harvest_dirs(args.dirs, store)
    if args.date:
        added += harvest_date(args.date, args.sample, store)
    if added:
        save(store)
        print(f"+{added} rows -> {len(store)} total")

    if args.report or not (args.dirs or args.date):
        report(store, args.mine)


if __name__ == "__main__":
    main()
