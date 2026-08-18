"""What is on every tile, every day, for one seat -- and what is idle.

The melon opening is worth about $13,600 a game (fifteen separate losses, all
with a MELON gap of +13,584): the field plants 12 melons on day 0 and harvests
into a virgin $250 market on day 10, we plant 5 and put 14 more in on day 10
that ripen on day 20 into a market that died on day 11.

Before that can be fixed, three things have to be known rather than assumed:
which tiles are free early, how much worker time is genuinely idle on the days a
melon needs watering, and what the tiles the melon would displace are earning.

    python tile_timeline.py            # occupancy grid, days 0-13
    python tile_timeline.py --days 30
    python tile_timeline.py --agent agent_combined.py
"""
import argparse
import collections
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

from kaggle_environments import make                                # noqa: E402

TURNS_PER_DAY = 24
SEAT = 0
GLYPH = {"WEED": "w", "PASTURE": "P", "COOP": "C", None: ".", "LOCKED": " "}
CROP = {"WHEAT": "W", "MELON": "M", "STRAWBERRY": "S", "CARROT": "c", "TOMATO": "t"}


def cell(tile):
    if tile == "LOCKED":
        return " "
    if tile is None:
        return "."
    if not isinstance(tile, dict):
        return "?"
    kind = tile.get("kind")
    if kind == "PLANT":
        return CROP.get(tile.get("crop"), "p")
    if "animal" in tile:
        return {"COW": "1", "SHEEP": "2", "GOOSE": "3"}.get(tile["animal"], "a")
    return GLYPH.get(kind, "?")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default=os.path.join("kernels", "route_agent.py"))
    ap.add_argument("--seed", type=int, default=600)
    ap.add_argument("--days", type=int, default=14)
    args = ap.parse_args()

    path = args.agent if os.path.isabs(args.agent) else os.path.join(PROJECT, args.agent)
    env = make("kaggriculture", configuration={"seed": args.seed}, debug=False)
    env.run([path, os.path.join(PROJECT, "kernels", "route_agent.py")])

    print(f"{args.agent} on seed {args.seed}\n"
          f"legend: . empty   W wheat  M melon  S strawberry  c carrot  "
          f"P pasture  1 cow  2 sheep  w weed  (space) locked\n")

    for day in range(min(args.days, 30)):
        step = day * TURNS_PER_DAY
        obs = env.steps[step][SEAT].observation
        farm = (obs.get("farms") or [{}])[SEAT]
        tiles = farm.get("tiles") or []
        counts = collections.Counter()
        for row in tiles:
            for t in row:
                counts[cell(t)] += 1
        money = farm.get("money", 0)
        print(f"day {day:>2}  ${money:>9,.0f}   hands {len(farm.get('hands') or []):>2}"
              f"   empty {counts['.']:>2}  wheat {counts['W']:>2}  melon {counts['M']:>2}"
              f"  straw {counts['S']:>2}  weed {counts['w']:>2}")
        for row in tiles:
            print("        " + " ".join(cell(t) for t in row))
        print()

    # Idle unit-turns per day: what a new job could actually be built from.
    print(f"{'day':>4}{'unit-turns':>12}{'busy':>8}{'idle':>8}{'idle %':>9}")
    for day in range(min(args.days, 30)):
        busy = idle = 0
        for step in range(day * TURNS_PER_DAY, (day + 1) * TURNS_PER_DAY):
            if step + 1 >= len(env.steps):
                break
            act = env.steps[step + 1][SEAT].action
            if not isinstance(act, dict):
                continue
            for u in [act.get("farmer")] + list(act.get("hands") or []):
                if not u or u[0] == "PASS":
                    idle += 1
                else:
                    busy += 1
        print(f"{day:>4}{busy + idle:>12}{busy:>8}{idle:>8}"
              f"{100 * idle / max(1, busy + idle):>8.0f}%")


if __name__ == "__main__":
    main()
