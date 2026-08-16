"""Which of the route's wheat plantings could be carrots instead?

The route grows WHEAT, MELON and STRAWBERRY and nothing else, so CARROT, TOMATO
and EGG are consumed by the town all season and replaced by nobody. Measured
over a route-vs-route game on seed 600, carrot ends 408 units short at $65 and
climbing, against wheat's $33 -- and neither player has sold a single one.

Substituting is not free, because the trace is a recording and every tile is on
a schedule:

    WHEAT   max_yield_day 4, water window ages 2-4, tile dies at age 5
    CARROT  max_yield_day 3, water window ages 2-3, tile dies at age 4

So a carrot planted where wheat was planted is worth more per tile-day, but it
dies a day earlier. A swap is only safe when the route comes back to harvest
that tile by age 3. This walks a real game, pairs every PLANT with the HARVEST
that collects it, and reports which swaps survive.

    python analyse_plantings.py [seed]
"""
import collections
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

from kaggle_environments import make                                # noqa: E402

TURNS_PER_DAY = 24
SEAT = 0


def unit_orders(action):
    """(actor, order) for every unit in one submitted action."""
    yield "farmer", list((action or {}).get("farmer") or ["PASS"])
    for i, hand in enumerate((action or {}).get("hands") or []):
        yield i, list(hand or ["PASS"])


def unit_positions(farm):
    yield "farmer", tuple(farm.get("farmer") or (0, 0))
    for i, pos in enumerate(farm.get("hands") or []):
        yield i, tuple(pos or (0, 0))


def walk(seed):
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([os.path.join(PROJECT, "kernels", "route_agent.py")] * 2)

    open_at = {}        # tile -> planting record
    plantings = []
    # env.steps[i].action is the action that PRODUCED state i, so it was chosen
    # from the observation at i-1 and indexes _ROUTE at i-1. Reading positions
    # out of frame i instead reads where the worker ended up, not where it acted.
    for step in range(len(env.steps) - 1):
        obs = env.steps[step][SEAT].observation
        action = env.steps[step + 1][SEAT].action
        if not isinstance(action, dict):
            continue
        farm = (obs.get("farms") or [{}])[SEAT]
        pos_of = dict(unit_positions(farm))
        day = step // TURNS_PER_DAY

        for actor, order in unit_orders(action):
            if not order or order[0] not in ("PLANT", "WATER", "HARVEST"):
                continue
            tile = pos_of.get(actor)
            if tile is None:
                continue
            op = order[0]
            if op == "PLANT":
                rec = {"step": step, "day": day, "actor": actor, "tile": tile,
                       "crop": order[1] if len(order) > 1 else "?",
                       "waters": [], "harvest_day": None, "harvest_step": None}
                plantings.append(rec)
                open_at[tile] = rec
            elif op == "WATER":
                rec = open_at.get(tile)
                if rec is not None:
                    age = day - rec["day"]
                    if age not in rec["waters"]:
                        rec["waters"].append(age)
            elif op == "HARVEST":
                rec = open_at.get(tile)
                if rec is not None and rec["harvest_day"] is None:
                    rec["harvest_day"] = day
                    rec["harvest_step"] = step
                    open_at.pop(tile, None)
    return plantings


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    plantings = walk(seed)
    print(f"seed {seed}: {len(plantings)} plantings by seat {SEAT}\n")

    by_crop = collections.Counter(p["crop"] for p in plantings)
    print("plantings by crop: " + ", ".join(f"{k} {v}" for k, v in by_crop.most_common()))

    wheat = [p for p in plantings if p["crop"] == "WHEAT"]
    print(f"\nWHEAT plantings: {len(wheat)}")

    gaps = collections.Counter()
    for p in wheat:
        gaps[p["harvest_day"] - p["day"] if p["harvest_day"] is not None else None] += 1
    print("  harvest age (days from planting) -> count:")
    for age, n in sorted(gaps.items(), key=lambda kv: (kv[0] is None, kv[0])):
        label = "never harvested" if age is None else f"age {age}"
        print(f"    {label:<18} {n:>4}")

    # A carrot planted in a wheat slot needs watering at ages 2 and 3 and a
    # harvest by age 3; wheat's own schedule waters 2-4 and harvests at 4.
    safe = [p for p in wheat
            if p["harvest_day"] is not None
            and 2 <= p["harvest_day"] - p["day"] <= 3
            and 2 in p["waters"]]
    print(f"\n  swappable to CARROT (harvest by age 3, watered at age 2): "
          f"{len(safe)} of {len(wheat)}")

    water_shape = collections.Counter(tuple(sorted(p["waters"])) for p in wheat)
    print("\n  watering ages seen on wheat tiles:")
    for shape, n in water_shape.most_common(10):
        print(f"    {str(shape):<22} {n:>4}")

    print("\n  wheat plantings by day:")
    per_day = collections.Counter(p["day"] for p in wheat)
    safe_day = collections.Counter(p["day"] for p in safe)
    for day in sorted(per_day):
        print(f"    day {day:>2}: {per_day[day]:>3} planted, {safe_day[day]:>3} swappable")


if __name__ == "__main__":
    main()
