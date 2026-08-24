"""Which top team runs the same field schedule every game?

A replay carries both players' full 720-step action streams, so any route agent's
whole plan is public the moment it plays. But a top replay is behaviour under one
state path, not a portable policy: lifting one and running it on fresh seeds has
failed repeatedly -- ours scored 6/16, and Kaito reports a frozen top trace
scoring 0/50.

The filter that separates the two is REPEATABILITY. A team whose field actions
are byte-identical across several games against different opponents is running a
fixed tape, and a fixed tape transplants. A team whose actions differ game to
game is reacting to something, and freezing one of its games captures the
reaction, not the policy.

    python route_census.py kaggle_episode_data/daily/2026-08-20 --max-rank 60

Reports, per team: how many episodes, how many distinct field-action hashes, and
how many distinct market hashes. Look for `field variants == 1` across 3+ games.

Rayk Kretzschmar's notebook adds one more filter worth honouring: pick the
episode belonging to the team's LEADERBOARD-SCORING submission, not merely its
newest active one. Teams run two submissions and the newer is often the weaker
experiment. We cannot see submission ids per episode here, so treat a team with
two stable-but-different tapes as exactly that ambiguity.
"""
import argparse
import collections
import csv
import glob
import hashlib
import io
import json
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def leaderboard():
    files = sorted(glob.glob(os.path.join(
        PROJECT, "kaggle_episode_data", "kaggriculture-publicleaderboard-*.csv")))
    if not files:
        return {}
    return {r["TeamName"]: (int(r["Rank"]), float(r["Score"]))
            for r in csv.DictReader(io.open(files[-1], encoding="utf-8-sig"))}


def hashes(steps, seat, limit=None):
    """Separate hashes for the field plan and the market plan.

    `limit` caps how many steps are hashed. THE FULL-SEASON HASH IS USELESS FOR
    TELLING A FIXED TAPE FROM AN ADAPTIVE AGENT: weeds spawn randomly, and any
    agent with weed repair -- which is every serious one, including ours --
    shifts its actions around them. Our own known-fixed tape produces 29
    distinct full-season field hashes over 91 games.

    Weeds only spawn in the end-of-day refresh, so the first day is clean.
    Hashing steps 0..23 fingerprints the opening a route commits to before any
    randomness can touch it, which is what actually identifies a family.
    """
    field, market = [], []
    stop = len(steps) if limit is None else min(len(steps), limit + 1)
    for i in range(1, stop):
        action = steps[i][seat].get("action")
        if not isinstance(action, dict):
            field.append("~")
            market.append("~")
            continue
        farmer = action.get("farmer") or ["PASS"]
        hands = action.get("hands") or []
        field.append(repr([list(farmer)] + [list(h or ["PASS"]) for h in hands]))
        market.append(repr([list(o) for o in (action.get("market") or [])]))
    return (hashlib.sha256("|".join(field).encode()).hexdigest()[:12],
            hashlib.sha256("|".join(market).encode()).hexdigest()[:12])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--max-rank", type=int, default=60)
    ap.add_argument("--min-games", type=int, default=2)
    ap.add_argument("--opening", type=int, default=24,
                    help="hash only the first N steps; 0 = whole season")
    args = ap.parse_args()
    if args.opening == 0:
        args.opening = None

    lb = leaderboard()
    teams = collections.defaultdict(lambda: {"field": collections.Counter(),
                                             "market": collections.Counter(),
                                             "scores": [], "eps": []})
    paths = []
    for folder in args.folders:
        paths.extend(sorted(glob.glob(os.path.join(folder, "*.json"))))

    for path in paths:
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        names = d.get("info", {}).get("TeamNames") or []
        steps = d.get("steps") or []
        if len(steps) < 700:
            continue
        for seat, name in enumerate(names):
            rank = lb.get(name, (10 ** 9, 0))[0]
            if rank > args.max_rank:
                continue
            f, m = hashes(steps, seat, limit=args.opening)
            t = teams[name]
            t["field"][f] += 1
            t["market"][m] += 1
            t["scores"].append(d["rewards"][seat])
            t["eps"].append(os.path.basename(path))

    rows = []
    for name, t in teams.items():
        games = sum(t["field"].values())
        if games < args.min_games:
            continue
        rank, score = lb.get(name, (10 ** 9, 0))
        rows.append((len(t["field"]), -games, rank, name, games,
                     len(t["market"]), score,
                     sum(t["scores"]) / len(t["scores"]),
                     t["field"].most_common(1)[0]))

    rows.sort()
    print(f"{len(paths)} replays, {len(teams)} teams inside rank {args.max_rank}, "
          f"{len(rows)} with {args.min_games}+ games\n")
    print(f"{'rank':>5} {'team':<26}{'games':>6}{'field':>7}{'market':>7}"
          f"{'LB':>9}{'mean bank':>11}  top field hash")
    for fv, negg, rank, name, games, mv, score, bank, (fh, fn) in rows:
        flag = "  <== fixed tape" if fv == 1 and games >= 3 else ""
        print(f"{rank:>5} {name[:25]:<26}{games:>6}{fv:>7}{mv:>7}"
              f"{score:>9.1f}{bank:>11,.0f}  {fh} x{fn}{flag}")


if __name__ == "__main__":
    main()
