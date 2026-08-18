"""Every loss for one submission: who beat us, how, and with what.

Runs the exact ledger (replay_ledger's instrumented environment replay) over
every losing episode, fingerprints the opponent's build, and attributes the
defeat to the product that actually carried it.

    python analyse_losses.py 55563850
    python analyse_losses.py 55563850 --csv losses.csv

Ranks come from the most recent leaderboard CSV in kaggle_episode_data/.
"""
import argparse
import collections
import csv
import glob
import io
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)
OURS = "Harshith revuru"


def leaderboard():
    files = sorted(glob.glob(os.path.join(
        PROJECT, "kaggle_episode_data", "kaggriculture-publicleaderboard-*.csv")))
    if not files:
        return {}
    rows = csv.DictReader(io.open(files[-1], encoding="utf-8-sig"))
    return {r["TeamName"]: (r["Rank"], r["Score"]) for r in rows}


def fingerprint(actions):
    """What build is this? Read it off the action stream."""
    plant = collections.defaultdict(collections.Counter)
    animals = collections.Counter()
    bought = collections.Counter()
    land = []
    ops = collections.Counter()
    hands = 0
    for step, act in enumerate(actions):
        if not isinstance(act, dict):
            continue
        hands = max(hands, len(act.get("hands") or []))
        for u in [act.get("farmer")] + list(act.get("hands") or []):
            if not u:
                continue
            ops[u[0]] += 1
            if len(u) > 1 and u[0] == "PLANT":
                plant[u[1]][step // 24] += 1
        for o in act.get("market") or []:
            if not o:
                continue
            if o[0] == "BUY_ANIMAL" and len(o) > 2:
                animals[o[1]] += int(o[2])
            elif o[0] == "BUY_PRODUCT" and len(o) > 2:
                bought[o[1]] += int(o[2])
            elif o[0] == "BUY_LAND":
                land.append(step // 24)
    melon = plant["MELON"]
    return {
        "melon_day0": sum(v for k, v in melon.items() if k <= 3),
        "melon_late": sum(v for k, v in melon.items() if k >= 8),
        "melon_sched": dict(sorted(melon.items())),
        "cow": animals["COW"], "sheep": animals["SHEEP"], "goose": animals["GOOSE"],
        "wheat_bought": bought["WHEAT"],
        "land_days": land, "hands": hands,
        "pass_pct": round(100 * ops["PASS"] / max(1, sum(ops.values()))),
        "total_ops": sum(ops.values()),
    }


def archetype(fp):
    tags = []
    if fp["melon_day0"] >= 10:
        tags.append("day-0 melon (new route)")
    elif fp["melon_day0"] <= 6 and fp["melon_late"] >= 8:
        tags.append("day-10 melon (our generation)")
    if fp["sheep"] >= 8:
        tags.append(f"sheep-heavy x{fp['sheep']}")
    elif fp["cow"] >= 9:
        tags.append(f"cow-heavy x{fp['cow']}")
    if fp["wheat_bought"] >= 500:
        tags.append(f"buys feed ({fp['wheat_bought']}w)")
    if len(fp["land_days"]) >= 3:
        tags.append("all 4 quadrants")
    if not tags:
        tags.append("unclassified")
    return ", ".join(tags)


def one(path):
    import replay_ledger as RL
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as K

    d = json.load(io.open(path, encoding="utf-8"))
    names = d["info"]["TeamNames"]
    if OURS not in names:
        return None
    us = names.index(OURS)
    them = 1 - us
    if d["rewards"][us] >= d["rewards"][them]:
        return None

    steps = d["steps"]
    recorded = [[None] * len(steps) for _ in (0, 1)]
    for i in range(1, len(steps)):
        for p in (0, 1):
            recorded[p][i - 1] = steps[i][p].get("action")

    revenue = [collections.Counter(), collections.Counter()]
    spend = [collections.Counter(), collections.Counter()]
    ident = {}
    original, original_market = K._commit_unit, K._process_market

    def traced(op, item, price, farm, private, market, shed_capacity=100):
        ok = original(op, item, price, farm, private, market, shed_capacity)
        if ok:
            p = ident.get(id(private))
            if p is not None:
                (revenue if op == "SELL" else spend)[p][item] += price
        return ok

    def traced_market(state, env):
        ident.clear()
        for p, s in enumerate(state):
            ident[id(s.observation.private)] = p
        return original_market(state, env)

    K._commit_unit, K._process_market = traced, traced_market
    try:
        env = make("kaggriculture", configuration={"seed": d["info"]["seed"]}, debug=False)
        env.run([RL.playback(recorded[0]), RL.playback(recorded[1])])
        final = [env.steps[-1][0].observation["farms"][p].get("money") for p in (0, 1)]
        exact = [round(x) for x in final] == [round(x) for x in d["rewards"]]
        shops = collections.Counter(env.steps[-1][0].observation["town"]["unlocked_shops"])
    finally:
        K._commit_unit, K._process_market = original, original_market

    # Net gap per product: their revenue minus ours, less what each spent on it.
    net = {}
    for item in set(revenue[0]) | set(revenue[1]) | set(spend[0]) | set(spend[1]):
        mine = revenue[us][item] - spend[us][item]
        theirs = revenue[them][item] - spend[them][item]
        net[item] = theirs - mine
    ranked = sorted(net.items(), key=lambda kv: -kv[1])

    fp = fingerprint(recorded[them])
    return {
        "episode": os.path.splitext(os.path.basename(path))[0],
        "opponent": names[them],
        "ours": d["rewards"][us], "theirs": d["rewards"][them],
        "margin": d["rewards"][us] - d["rewards"][them],
        "exact": exact,
        "cause": ranked[0][0], "cause_$": round(ranked[0][1]),
        "cause2": ranked[1][0], "cause2_$": round(ranked[1][1]),
        "gaps": {k: round(v) for k, v in ranked[:5]},
        "shops": dict(shops),
        "archetype": archetype(fp), **fp,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("submission")
    ap.add_argument("--csv", default=None)
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    folder = os.path.join(PROJECT, "kaggle_episode_data", "replays", args.submission)
    paths = sorted(glob.glob(os.path.join(folder, "*.json")))
    print(f"{len(paths)} replays in {folder}")

    lb = leaderboard()
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(one, paths), 1):
            if r:
                rows.append(r)
            if i % 20 == 0:
                print(f"  {i}/{len(paths)} scanned, {len(rows)} losses", flush=True)

    rows.sort(key=lambda r: r["margin"])
    bad = [r for r in rows if not r["exact"]]
    print(f"\n{len(rows)} losses; ledger reproduces final money exactly in "
          f"{len(rows) - len(bad)}/{len(rows)}")

    print(f"\n{'episode':>9} {'opponent':<22}{'rank':>6}{'margin':>10}"
          f"  {'lost on':<26}archetype")
    for r in rows:
        rank = lb.get(r["opponent"], ("?", "?"))[0]
        cause = f"{r['cause']} {r['cause_$']:+,}"
        print(f"{r['episode']:>9} {r['opponent'][:21]:<22}{rank:>6}{r['margin']:>+10,.0f}"
              f"  {cause:<26}{r['archetype']}")

    print("\n=== what beat us, by product (net of their spend)")
    tally = collections.Counter(r["cause"] for r in rows)
    money = collections.Counter()
    for r in rows:
        for k, v in r["gaps"].items():
            if v > 0:
                money[k] += v
    for item, n in tally.most_common():
        print(f"  {item:<12} primary cause in {n:>2} of {len(rows)} losses;"
              f" total gap across all losses ${money[item]:,}")

    print("\n=== opponent archetypes among the losses")
    for a, n in collections.Counter(r["archetype"] for r in rows).most_common():
        print(f"  {n:>2}x  {a}")
    print("\n  day-0 melon opener: "
          f"{sum(1 for r in rows if r['melon_day0'] >= 10)} of {len(rows)} losses")
    print(f"  sheep >= 8:         {sum(1 for r in rows if r['sheep'] >= 8)} of {len(rows)}")
    print(f"  all four quadrants: {sum(1 for r in rows if len(r['land_days']) >= 3)} of {len(rows)}")

    if args.csv:
        with io.open(args.csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["episode", "opponent", "rank", "lb_score", "ours", "theirs",
                        "margin", "cause", "cause_$", "cause2", "cause2_$",
                        "archetype", "melon_day0", "melon_late", "cow", "sheep",
                        "wheat_bought", "quadrants", "hands", "pass_pct", "shops"])
            for r in rows:
                rank, sc = lb.get(r["opponent"], ("", ""))
                w.writerow([r["episode"], r["opponent"], rank, sc, r["ours"], r["theirs"],
                            r["margin"], r["cause"], r["cause_$"], r["cause2"],
                            r["cause2_$"], r["archetype"], r["melon_day0"],
                            r["melon_late"], r["cow"], r["sheep"], r["wheat_bought"],
                            len(r["land_days"]) + 1, r["hands"], r["pass_pct"],
                            json.dumps(r["shops"])])
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()
