"""Lift an opponent's 720-step recording out of a downloaded replay.

Every replay carries the full action stream for both seats, so a route agent's
entire plan is public the moment it plays a game. Ours is a generation behind:
we plant 5 melons on day 0 and 14 more on day 10 that ripen into a dead market,
while all four opponents examined plant 12 on day 0 and none after day 7. That
one difference is worth about $13,800 a game.

    python kernels/extract_route.py REPLAY.json [--out kernels/route_v15.py]

The lifted trace is what the agent EMITTED, so it carries that episode's
weed repairs -- a DIG substituted for a blocked PLANT, then the schedule shifted
by one for a few steps. Replayed on another seed those land on different tiles.

MEASURED, AND IT DOES NOT TRANSPLANT. iVl44d's route, lifted and run inside our
wrapper on eight fresh seeds:

    vs agent_combined.py    6/16 wins   77,313 against 89,472
    vs stock route_agent    6/16 wins   77,290 against 90,222

Twelve thousand dollars WORSE than the route it beat in its own episode. The
weed contamination is not the reason -- there are only 26 DIGs and every one is
after day 18, so the melon opening that makes it good is clean. The likelier
cause is cash. Its day-0 order spends about $2,980 of the $3,000 float
(2 cows, 2 sheep, 12 melon seed, 7 wheat seed, 6 bought wheat), and the price of
that bought wheat depends on what the OTHER player is doing. Against a different
opponent the opening costs a few dollars more, one order fails, and the whole
season is built on the wrong footing. It also buys land on days 6, 11 and 12 --
all four quadrants, $7,000 -- which only works if the melon money arrives on
time.

So a recording is not a strategy: it is a strategy plus the exact game it was
recorded in. Lifting the plan needs the agent that adapts it, and that part is
not in the replay.
"""
import argparse
import base64
import collections
import io
import json
import os
import re
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))


def lift(path, ours="Harshith revuru"):
    d = json.load(io.open(path, encoding="utf-8"))
    names = d["info"]["TeamNames"]
    seat = 1 if names[0] == ours else 0
    steps = d["steps"]

    # steps[i].action is the action that PRODUCED state i, so it was chosen at
    # step i-1 and belongs at route index i-1.
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
    return route[:720], names[seat], d["rewards"][seat], d["rewards"][1 - seat]


def summarise(route):
    plant = collections.defaultdict(collections.Counter)
    animals = collections.Counter()
    for step, tr in enumerate(route):
        for u in [tr["farmer"]] + tr["hands"]:
            if len(u) > 1 and u[0] == "PLANT":
                plant[u[1]][step // 24] += 1
        for o in tr["market"]:
            if o[0] == "BUY_ANIMAL" and len(o) > 2:
                animals[o[1]] += int(o[2])
    return plant, animals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("--out", default=os.path.join(HERE, "route_lifted.py"))
    ap.add_argument("--ours", default="Harshith revuru")
    args = ap.parse_args()

    route, name, score, theirs = lift(args.replay, args.ours)
    plant, animals = summarise(route)
    print(f"lifted {name}: scored {score:,.0f} against our {theirs:,.0f}")
    for crop, days in sorted(plant.items()):
        print(f"  {crop:<11} by day {dict(sorted(days.items()))}")
    print(f"  animals {dict(animals)}")

    blob = base64.b85encode(zlib.compress(
        json.dumps(route, separators=(",", ":")).encode(), 9)).decode()

    scaffold = io.open(os.path.join(HERE, "route_agent.py"), encoding="utf-8").read()
    new, n = re.subn(r"b85decode\('[^']+'\)", f"b85decode('{blob}')", scaffold, count=1)
    if n != 1:
        raise SystemExit("could not find the route blob in route_agent.py")
    header = (f'"""Route lifted from {os.path.basename(args.replay)} '
              f'({name}, scored {score:,.0f}).\n\n'
              f'Built by kernels/extract_route.py. This is the opponent\'s own\n'
              f'recording, replayed inside our wrapper."""\n')
    new = header + new.split('"""', 2)[2].lstrip("\n")
    io.open(args.out, "w", encoding="utf-8", newline="").write(new)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
