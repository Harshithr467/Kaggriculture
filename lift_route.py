"""Build a candidate agent from another team's recorded route.

Takes agent_combined.py and swaps only the embedded `_ROUTE` blob for a route
lifted from a top team's replay, leaving every wrapper in place: weed repair,
hand matching, premium preemption, the eager seller, the terminal cash drop.
Route-specific edits are switched off, because CARROT_SWAP's (step, hand) pairs
address OUR tape and mean nothing on someone else's.

    python lift_route.py --team "ReCurSiON" --out kernels/agent_recursion.py

WHICH EPISODE. A recording is a strategy plus the exact game it was recorded in,
so the choice matters. This picks, among the episodes carrying the team's
dominant opening hash, the one with the fewest DIG actions -- weed repair
substitutes a DIG and then shifts that actor's schedule for several steps, and
those shifts are contamination that will not match a new seed's weeds.

WHAT TO EXPECT. Lifting has a poor record: our previous attempt scored 6/16, and
Kaito Fukami reports a frozen top trace scoring 0/50. The usual cause is cash --
a day-0 order that spends nearly the whole $3,000 float depends on what the
opponent does to the wheat price, and one failed order derails the season.

MEASURED, 2026-08-24, four teams lifted with this script and played against the
incumbent on three pinned seeds both seats:

    ReCurSiON       (#17)   0/6    -4,442
    Ryo Hasegawa    (#1)    0/6    -6,486
    Arman Tuganbaev (#4)    0/6   -11,098
    MiMi            (#5)    6/6    +1,632

Note that RANK DOES NOT PREDICT TRANSPLANTABILITY -- the top-rated agent's route
was the second worst of the four.

And MiMi, the one that looked good, did not survive the test that counts. It
scored 233W-127L on the 360-game replay benchmark against the incumbent's
209W-151L, then lost to that same incumbent 8-32 on twenty HELD-OUT seeds. Three
seeds is not a screen, it is a coin flip you get to keep flipping. Decide on
seeds the candidate has never seen, or this script will hand you a regression
wearing a +24.
"""
import argparse
import base64
import collections
import glob
import io
import json
import os
import re
import sys
import zlib

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import route_census as RC


def episodes(folders, team):
    out = []
    for folder in folders:
        for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
            try:
                d = json.load(io.open(path, encoding="utf-8"))
            except Exception:
                continue
            names = d.get("info", {}).get("TeamNames") or []
            if team not in names or len(d.get("steps") or []) < 700:
                continue
            out.append((path, d, names.index(team)))
    return out


def lift(steps, seat):
    route = []
    for i in range(1, len(steps)):
        act = steps[i][seat].get("action")
        if not isinstance(act, dict):
            act = {}
        route.append({
            "farmer": list(act.get("farmer") or ["PASS"]),
            "hands": [list(h or ["PASS"]) for h in (act.get("hands") or [])],
            "market": [list(o) for o in (act.get("market") or []) if o],
        })
    while len(route) < 720:
        route.append({"farmer": ["PASS"], "hands": [], "market": []})
    return route[:720]


def digs(route):
    return sum(1 for tr in route
               for u in [tr["farmer"]] + tr["hands"] if u and u[0] == "DIG")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", required=True)
    ap.add_argument("--folder", nargs="+", default=sorted(
        glob.glob(os.path.join(PROJECT, "kaggle_episode_data", "daily", "2026-*"))))
    ap.add_argument("--base", default=os.path.join(PROJECT, "agent_combined.py"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    found = [(p, d, s) for p, d, s in episodes(args.folder, args.team)
             if os.path.isdir(os.path.dirname(p))]
    if not found:
        raise SystemExit(f"no replays for {args.team!r}")

    # Group by opening hash and keep the dominant family.
    by_open = collections.defaultdict(list)
    for path, d, seat in found:
        f, _ = RC.hashes(d["steps"], seat, limit=24)
        by_open[f].append((path, d, seat))
    opening, family = max(by_open.items(), key=lambda kv: len(kv[1]))
    print(f"{args.team}: {len(found)} episodes, {len(by_open)} opening(s); "
          f"using {opening} with {len(family)} episodes")

    scored = []
    for path, d, seat in family:
        route = lift(d["steps"], seat)
        scored.append((digs(route), -d["rewards"][seat], path, route, d, seat))
    scored.sort()
    ndig, negbank, path, route, d, seat = scored[0]
    print(f"chose {os.path.basename(path)} seat {seat}: {ndig} DIGs, "
          f"banked {d['rewards'][seat]:,.0f} vs {d['rewards'][1 - seat]:,.0f}")

    plants = collections.Counter()
    animals = collections.Counter()
    for tr in route:
        for u in [tr["farmer"]] + tr["hands"]:
            if len(u) > 1 and u[0] == "PLANT":
                plants[u[1]] += 1
        for o in tr["market"]:
            if o[0] == "BUY_ANIMAL" and len(o) > 2:
                animals[o[1]] += int(o[2])
    print(f"  plantings: {dict(plants)}")
    print(f"  animals:   {dict(animals)}")

    blob = base64.b85encode(zlib.compress(
        json.dumps(route, separators=(",", ":")).encode("utf-8"), 9)).decode("ascii")

    src = io.open(args.base, encoding="utf-8").read()
    pattern = re.compile(r"(_ROUTE = json\.loads\(zlib\.decompress\(base64\.b85decode\(')"
                         r"[^']*('\)\)\.decode\('utf-8'\)\))")
    if not pattern.search(src):
        raise SystemExit("could not find the _ROUTE blob in the base agent")
    src = pattern.sub(lambda m: m.group(1) + blob + m.group(2), src, count=1)

    # Our tape's edits address our tape's steps; they are meaningless here.
    for name, off in (("CARROT_SWAP", "()"), ("TOMATO_SWAP", "()"),
                      ("MELON_PATCH", "()"), ("HERD_SWAP", "{}"),
                      ("CARROT_PRICE_GATE", "None")):
        src = re.sub(rf"^{name} = .*$", f"{name} = {off}", src, count=1, flags=re.M)

    header = (f'"""{args.team}\'s route, lifted from episode '
              f'{os.path.basename(path)} seat {seat}.\n\n'
              f'Generated by lift_route.py. The farm plan is that team\'s public\n'
              f'recorded behaviour; the wrapper around it is ours. Route-specific\n'
              f'edits are disabled because they address our own tape\'s steps.\n"""\n')
    src = header + src.split('"""', 2)[2].lstrip("\n")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    io.open(args.out, "w", encoding="utf-8", newline="").write(src)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
