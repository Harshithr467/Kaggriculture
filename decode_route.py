"""Decode the V14 route into a readable plan: what it does, turn by turn.

The route is 720 recorded steps of `{farmer, hands, market}`. Replaying it wins,
but nobody replaying it can say what it is doing, which makes it impossible to
improve deliberately or to know which parts are load-bearing. This turns the
trace back into a plan.

    python decode_route.py              # the whole season, day by day
    python decode_route.py --day 0      # one day, turn by turn
    python decode_route.py --workers    # what each worker slot does all season

Positions come from the trace only where an action implies one; the route
carries no coordinates, since a worker acts on the tile it is standing on.
"""
import argparse
import collections
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT, "kernels"))
sys.path.insert(0, PROJECT)

TURNS_PER_DAY = 24
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}


def load_route():
    import route_agent
    return route_agent._ROUTE


def unit_actions(trace):
    """Every unit action in one step: (slot, op, args)."""
    out = [("farmer", (trace.get("farmer") or ["PASS"]))]
    for i, h in enumerate(trace.get("hands") or []):
        out.append((f"hand{i}", list(h or ["PASS"])))
    return [(slot, a[0], a[1:]) for slot, a in out if a]


def day_summary(route):
    days = collections.defaultdict(lambda: {
        "ops": collections.Counter(), "market": collections.Counter(),
        "sold": collections.Counter(), "bought": collections.Counter(),
        "planted": collections.Counter(), "hands": 0})
    for step, trace in enumerate(route):
        d = days[step // TURNS_PER_DAY]
        d["hands"] = max(d["hands"], len(trace.get("hands") or []))
        for _slot, op, args in unit_actions(trace):
            d["ops"][op] += 1
            if op == "PLANT" and args:
                d["planted"][args[0]] += 1
        for order in (trace.get("market") or []):
            if not order:
                continue
            d["market"][order[0]] += 1
            if order[0] == "SELL" and len(order) > 2:
                d["sold"][order[1]] += int(order[2])
            elif order[0] in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL") and len(order) > 2:
                d["bought"][f"{order[0].split('_')[1]}:{order[1]}"] += int(order[2])
            elif order[0] in ("HIRE", "BUY_LAND"):
                d["bought"][order[0]] += 1
    return days


def print_season(route):
    days = day_summary(route)
    print(f"{len(route)} steps = {len(days)} days\n")
    print(f"{'day':>4}{'hands':>6}{'move':>6}{'water':>6}{'harv':>6}{'plant':>6}"
          f"{'care':>6}{'feed':>6}{'pass':>6}  {'planted':<22}{'sold'}")
    for day in sorted(days):
        d = days[day]
        o = d["ops"]
        move = sum(o[m] for m in MOVES)
        planted = " ".join(f"{k[:3]}x{v}" for k, v in d["planted"].most_common())
        sold = " ".join(f"{k[:4]}{v}" for k, v in d["sold"].most_common())
        print(f"{day:>4}{d['hands']:>6}{move:>6}{o['WATER']:>6}{o['HARVEST']:>6}"
              f"{o['PLANT']:>6}{o['CARE']:>6}{o['FEED']:>6}{o['PASS']:>6}  "
              f"{planted:<22}{sold}")

    print("\nbuild order (purchases by day):")
    for day in sorted(days):
        b = days[day]["bought"]
        if b:
            print(f"  day {day:>2}: " + ", ".join(f"{k} x{v}" for k, v in b.most_common()))


def print_day(route, day):
    lo, hi = day * TURNS_PER_DAY, (day + 1) * TURNS_PER_DAY
    print(f"day {day}, steps {lo}-{hi - 1}\n")
    for step in range(lo, min(hi, len(route))):
        trace = route[step]
        acts = unit_actions(trace)
        busy = [(s, op, a) for s, op, a in acts if op != "PASS"]
        market = trace.get("market") or []
        if not busy and not market:
            continue
        hour = step % TURNS_PER_DAY
        parts = [f"{s}:{op}{'' if not a else ' ' + ' '.join(map(str, a))}" for s, op, a in busy]
        line = f"  h{hour:>2}  " + "  ".join(parts)
        if market:
            line += "   | market: " + ", ".join(" ".join(map(str, o)) for o in market)
        print(line)


def print_workers(route):
    """What each slot spends the season doing."""
    slots = collections.defaultdict(collections.Counter)
    for trace in route:
        for slot, op, _a in unit_actions(trace):
            slots[slot][op] += 1
    print(f"{'slot':<8}{'total':>7}{'move':>7}{'water':>7}{'harv':>7}{'plant':>7}"
          f"{'care':>7}{'feed':>7}{'fert':>7}{'pass':>7}")
    def order(name):
        return -1 if name == "farmer" else int(name[4:])
    for slot in sorted(slots, key=order):
        c = slots[slot]
        total = sum(c.values())
        move = sum(c[m] for m in MOVES)
        print(f"{slot:<8}{total:>7}{move:>7}{c['WATER']:>7}{c['HARVEST']:>7}{c['PLANT']:>7}"
              f"{c['CARE']:>7}{c['FEED']:>7}{c['FERTILIZE']:>7}{c['PASS']:>7}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int, default=None)
    ap.add_argument("--workers", action="store_true")
    args = ap.parse_args()
    route = load_route()
    if args.workers:
        print_workers(route)
    elif args.day is not None:
        print_day(route, args.day)
    else:
        print_season(route)


if __name__ == "__main__":
    main()
