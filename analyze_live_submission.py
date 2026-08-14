"""Download and analyse the live Kaggle replays for one submission.

Self-contained: fetches the episode list, downloads any replays not already on
disk, then reports win rate, score split, the closest losses (the winnable
ones), where actions go, and how much of the market each side left unsold.

    python analyze_live_submission.py 55397388
    python analyze_live_submission.py 55397388 --min-episodes 40

`--min-episodes N` exits without analysing if fewer than N episodes exist yet,
so this is safe to run on a schedule while a submission is still accumulating
games.
"""
import argparse
import collections
import csv
import glob
import json
import os
import subprocess
import sys

# Team names routinely contain non-ASCII characters (e.g. "Lê Quốc Duy"), and the
# default console encoding on Windows (cp1252) can't print them -- reconfigure
# stdout so this doesn't crash mid-report on a scheduled run.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT = os.path.dirname(os.path.abspath(__file__))
KAGGLE = os.path.join(PROJECT, ".venv", "Scripts", "kaggle.exe")
if not os.path.exists(KAGGLE):
    KAGGLE = "kaggle"
DATA = os.path.join(PROJECT, "kaggle_episode_data")
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
MARKET_I0 = 10000
COMPETITION = "kaggriculture"


def run_kaggle(args):
    proc = subprocess.run([KAGGLE] + args, capture_output=True, text=True)
    if proc.returncode != 0 and not proc.stdout.strip():
        raise RuntimeError(f"kaggle {' '.join(args)} failed: {proc.stderr[:400]}")
    return proc.stdout


def episode_ids(submission):
    out = run_kaggle(["competitions", "episodes", str(submission), "-v"])
    ids = []
    for row in csv.DictReader(line for line in out.splitlines() if line.strip()):
        value = (row.get("id") or "").strip()
        if value.isdigit():
            ids.append(value)
    return ids


def download_missing(submission, ids):
    target = os.path.join(DATA, "replays", str(submission))
    os.makedirs(target, exist_ok=True)
    fetched = 0
    for episode in ids:
        path = os.path.join(target, f"episode-{episode}-replay.json")
        if os.path.exists(path):
            continue
        try:
            run_kaggle(["competitions", "replay", episode, "-p", target])
            fetched += 1
        except Exception as exc:                      # a single bad episode is not fatal
            print(f"  ! could not fetch {episode}: {exc}")
    return target, fetched


def load(directory):
    games = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        try:
            raw = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        steps = raw.get("steps") or []
        if not steps:
            continue
        rewards = [s.get("reward") for s in steps[-1]]
        if any(r is None for r in rewards):
            continue
        names = (raw.get("info", {}) or {}).get("TeamNames") or ["P0", "P1"]
        games.append({"path": path, "names": names, "rewards": rewards, "steps": steps})
    return games


def census(steps, seat, from_day=0):
    ops = collections.Counter()
    for i, st in enumerate(steps):
        if i // 24 < from_day:
            continue
        action = st[seat].get("action")
        if not isinstance(action, dict):
            continue
        for unit in [action.get("farmer", ["PASS"])] + list(action.get("hands", []) or []):
            if isinstance(unit, list) and unit:
                ops[unit[0]] += 1
    return ops


def summarise(ops, label):
    total = sum(ops.values()) or 1
    moves = sum(ops[m] for m in MOVES)
    print(f"  {label}: {total:,} actions, {100*moves/total:.1f}% movement, "
          f"{100*ops['PASS']/total:.1f}% PASS")
    print("    ", {k: v for k, v in ops.most_common(14) if k not in MOVES})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("submission")
    parser.add_argument("--min-episodes", type=int, default=0)
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()

    print(f"=== live analysis: submission {args.submission} ===")
    ids = episode_ids(args.submission)
    print(f"episodes available: {len(ids)}")
    if len(ids) < args.min_episodes:
        print(f"fewer than {args.min_episodes} episodes; nothing to do yet.")
        return 0

    directory = os.path.join(DATA, "replays", str(args.submission))
    if not args.skip_download:
        directory, fetched = download_missing(args.submission, ids)
        print(f"downloaded {fetched} new replays into {directory}")

    games = load(directory)
    if not games:
        print("no usable replays on disk.")
        return 1

    # Our team is the name common to every replay.
    seen = collections.Counter()
    for g in games:
        for name in set(g["names"]):
            seen[name] += 1
    me = seen.most_common(1)[0][0]
    print(f"our team: {me!r}   usable replays: {len(games)}")
    print()

    wins, losses = [], []
    ours_all = collections.Counter()
    ours_late = collections.Counter()
    theirs_late = collections.Counter()
    idle_ours, idle_theirs = [], []
    final_inventory = collections.Counter()

    for g in games:
        seat = 0 if g["names"][0] == me else 1
        opp = 1 - seat
        mine, theirs = g["rewards"][seat], g["rewards"][opp]
        record = {
            "ep": os.path.basename(g["path"]).split("-")[1],
            "opp": g["names"][opp],
            "seat": seat,
            "mine": mine,
            "theirs": theirs,
            "margin": mine - theirs,
        }
        (wins if mine > theirs else losses).append(record)

        ours_all.update(census(g["steps"], seat))
        ours_late.update(census(g["steps"], seat, from_day=24))
        theirs_late.update(census(g["steps"], opp, from_day=24))

        idx = min(26 * 24 + 12, len(g["steps"]) - 1)
        obs = g["steps"][idx][0]["observation"]
        for s, bucket in ((seat, idle_ours), (opp, idle_theirs)):
            tiles = obs["farms"][s]["tiles"]
            empty = sum(1 for row in tiles for t in row if t is None)
            weeds = sum(1 for row in tiles for t in row
                        if isinstance(t, dict) and t.get("kind") == "WEED")
            owned = sum(1 for row in tiles for t in row if t != "LOCKED")
            bucket.append((empty, weeds, owned))

        for item, value in g["steps"][-1][0]["observation"]["market"]["inventory"].items():
            final_inventory[item] += value - MARKET_I0

    n = len(wins) + len(losses)
    print(f"RECORD  {len(wins)}W-{len(losses)}L   win rate {100*len(wins)/n:.1f}%   ({n} episodes)")
    print(f"  our avg {sum(r['mine'] for r in wins+losses)/n:,.0f}   "
          f"opponent avg {sum(r['theirs'] for r in wins+losses)/n:,.0f}")
    if wins:
        print(f"  in wins   {sum(r['mine'] for r in wins)/len(wins):,.0f} vs {sum(r['theirs'] for r in wins)/len(wins):,.0f}")
    if losses:
        print(f"  in losses {sum(r['mine'] for r in losses)/len(losses):,.0f} vs {sum(r['theirs'] for r in losses)/len(losses):,.0f}")
    print()

    if losses:
        print("CLOSEST LOSSES (most winnable):")
        for r in sorted(losses, key=lambda z: -z["margin"])[:10]:
            print(f"  ep {r['ep']} seat{r['seat']}  {r['mine']:>8,.0f} vs {r['theirs']:>8,.0f}  {r['margin']:>+9,.0f}  {r['opp']}")
        print()
        print("WORST LOSSES (structural mismatches):")
        for r in sorted(losses, key=lambda z: z["margin"])[:5]:
            print(f"  ep {r['ep']} seat{r['seat']}  {r['mine']:>8,.0f} vs {r['theirs']:>8,.0f}  {r['margin']:>+9,.0f}  {r['opp']}")
        print()
    if wins:
        print("BIGGEST WINS (what to protect):")
        for r in sorted(wins, key=lambda z: -z["margin"])[:5]:
            print(f"  ep {r['ep']} seat{r['seat']}  {r['mine']:>8,.0f} vs {r['theirs']:>8,.0f}  {r['margin']:>+9,.0f}  {r['opp']}")
        print()

    print("ACTION CENSUS")
    summarise(ours_all, "all days, ours ")
    summarise(ours_late, "days 24-29, ours")
    summarise(theirs_late, "days 24-29, opps")
    late_total = sum(ours_late.values()) or 1
    all_total = sum(ours_all.values()) or 1
    print(f"  endgame DIG check: {ours_late['DIG']:,} of {ours_all['DIG']:,} total digs "
          f"({100*ours_late['DIG']/max(1, ours_all['DIG']):.0f}% in days 24-29)")
    print(f"  movement: {100*sum(ours_all[m] for m in MOVES)/all_total:.1f}% overall, "
          f"{100*sum(ours_late[m] for m in MOVES)/late_total:.1f}% late")
    print()

    for label, bucket in (("ours", idle_ours), ("opps", idle_theirs)):
        if not bucket:
            continue
        e = sum(x[0] for x in bucket) / len(bucket)
        w = sum(x[1] for x in bucket) / len(bucket)
        o = sum(x[2] for x in bucket) / len(bucket)
        print(f"day 26 {label}: {e:.1f} empty + {w:.1f} weed of {o:.1f} owned ({100*(e+w)/max(1,o):.0f}% idle)")
    print()
    print("avg final market inventory vs equilibrium (negative = demand we never met):")
    for item, value in sorted(final_inventory.items(), key=lambda kv: kv[1]):
        print(f"  {item:<11} {value/n:>+9.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
