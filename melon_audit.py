"""Are our melons actually watered inside their bonus window?

A melon starts at 1 yield unit. Watering it while its age is between
`(max_yield_day + 1) // 2` and `max_yield_day` -- ages 6..12 at the default
config -- adds +1 per watered day, +2 if fertilized, capped at `max_yield` 6.
So a fully watered melon harvests 6 units and a neglected one harvests 1.

Rayk Kretzschmar's findings notebook lists "CARE ranked above melon WATER" as
the single highest-frequency bug in the field, costing roughly 70 units instead
of 96 across 16 tiles, and it is silent: nothing errors, the harvest is just
small. Our route plants 19 melons, so it is worth checking rather than assuming.

    python melon_audit.py --seed 901
"""
import argparse
import collections
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS

MELON = CROPS["MELON"]
WINDOW_START = (MELON["max_yield_day"] + 1) // 2
WINDOW_END = MELON["max_yield_day"]
CAP = MELON["max_yield"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="agent_combined.py")
    ap.add_argument("--opponent", default="kernels/rayk_c95.py")
    ap.add_argument("--seed", type=int, default=901)
    ap.add_argument("--seat", type=int, default=0)
    args = ap.parse_args()

    import benchmark_pool as BP
    from kaggle_environments import make

    us = BP._get_agent(args.ref)
    BP._restore(us, BP._pristine_state[args.ref])
    them = BP._get_agent(args.opponent)
    pair = ([us.agent, them.agent] if args.seat == 0
            else [them.agent, us.agent])
    env = make("kaggriculture", configuration={"seed": args.seed}, debug=False)
    env.run(pair)

    print(f"melon window is ages {WINDOW_START}..{WINDOW_END}, cap {CAP} units\n")

    # Peak yield_units reached by each melon tile before it left the board.
    peak = {}
    planted = {}
    turns_per_day = 24
    for i, frame in enumerate(env.steps):
        obs = frame[0].observation
        farm = obs["farms"][args.seat]
        day = i // turns_per_day
        for y, row in enumerate(farm.get("tiles") or []):
            for x, tile in enumerate(row):
                if not isinstance(tile, dict) or tile.get("crop") != "MELON":
                    continue
                units = tile.get("yield_units", 0)
                key = (x, y, tile.get("planted_day"))
                planted.setdefault(key, day)
                if units > peak.get(key, 0):
                    peak[key] = units

    if not peak:
        print("no melon tiles seen")
        return

    hist = collections.Counter(peak.values())
    total = sum(peak.values())
    best = CAP * len(peak)
    print(f"{len(peak)} melon tiles, peak yield units reached:")
    for units in sorted(hist):
        bar = "#" * hist[units]
        print(f"  {units} unit(s): {hist[units]:>3}  {bar}")
    print(f"\nharvestable units {total} of a possible {best}"
          f"   ({100 * total / best:.0f}% of cap)")
    if total < best:
        print(f"missing {best - total} units "
              f"= roughly {(best - total) * 250:,} coins at melon base price")


if __name__ == "__main__":
    main()
