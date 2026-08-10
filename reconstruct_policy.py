"""Reconstruct a player's full economic policy from a replay.

Replays record both seats' private state (shed, seeds, inventories) and every
market order issued, so an opponent's strategy is almost entirely recoverable:
what they bought and when, how they paced sales against market inventory, when
they hired and expanded, and how their farm composition evolved.

    python reconstruct_policy.py <replay.json>            # profiles the higher scorer
    python reconstruct_policy.py <replay.json> --seat 1
"""
import argparse
import collections
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TURNS = 24
I0 = 10000
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]
PRODUCTS = CROPS + ["EGG", "MILK", "WOOL", "FERTILIZER"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("replay")
    parser.add_argument("--seat", type=int, default=None)
    args = parser.parse_args()

    raw = json.load(open(args.replay, encoding="utf-8"))
    steps = raw["steps"]
    names = (raw.get("info", {}) or {}).get("TeamNames") or ["P0", "P1"]
    rewards = [s.get("reward") for s in steps[-1]]
    seat = args.seat if args.seat is not None else (0 if rewards[0] >= rewards[1] else 1)

    print(f"{os.path.basename(args.replay)}")
    print(f"profiling seat {seat}: {names[seat]}  final {rewards[seat]:,.0f}   "
          f"(opponent {names[1-seat]} {rewards[1-seat]:,.0f})")
    print()

    # ---- market order stream, aggregated by day
    buys = collections.defaultdict(lambda: collections.Counter())   # day -> what
    sells = collections.defaultdict(lambda: collections.Counter())
    hires = collections.Counter()
    land = []
    for i, st in enumerate(steps):
        day = i // TURNS
        action = st[seat].get("action")
        if not isinstance(action, dict):
            continue
        for order in (action.get("market") or [])[:10]:
            if not isinstance(order, list) or not order:
                continue
            op = order[0]
            if op == "HIRE":
                hires[day] += 1
            elif op == "BUY_LAND":
                land.append(day)
            elif op == "SELL" and len(order) >= 3:
                sells[day][order[1]] += int(order[2])
            elif op in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT") and len(order) >= 3:
                buys[day][f"{op.split('_')[1][:4]}:{order[1]}"] += int(order[2])

    print("DAILY POLICY")
    print(f"{'day':>4}{'money':>9}{'hire':>6}{'hands':>6}{'q':>3}  "
          f"{'crops w/c/t/s/m':>18}{'animals g/c/s':>14}  buys / sells")
    for day in range(30):
        idx = min(day * TURNS + 12, len(steps) - 1)
        obs = steps[idx][seat]["observation"]
        farm = obs["farms"][seat]
        crop = collections.Counter()
        animal = collections.Counter()
        for row in farm["tiles"]:
            for t in row:
                if isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        crop[t["crop"]] += 1
                    elif t.get("animal"):
                        animal[t["animal"]] += 1
        b = " ".join(f"{k}x{v}" for k, v in sorted(buys[day].items()) if v)
        s = " ".join(f"{k[:4]}x{v}" for k, v in sorted(sells[day].items()) if v)
        line = (f"{day:>4}{farm['money']:>9,.0f}{hires[day]:>6}{len(farm['hands']):>6}"
                f"{len(farm['unlocked_quadrants']):>3}  "
                f"{crop['WHEAT']:>3}/{crop['CARROT']:>2}/{crop['TOMATO']:>2}/"
                f"{crop['STRAWBERRY']:>2}/{crop['MELON']:>2}      "
                f"{animal['GOOSE']:>3}/{animal['COW']:>2}/{animal['SHEEP']:>2}   ")
        extra = (b + ("  |  " + s if s else "")) if (b or s) else ""
        print(line + extra[:90])

    print()
    print(f"land bought on days: {land}")
    print(f"total hires: {sum(hires.values())}")

    # ---- sell pacing against market inventory
    print()
    print("SELL PACING (did they sell into scarcity or dump into glut?)")
    print(f"{'product':<12}{'total sold':>11}{'first day':>11}{'last day':>10}"
          f"{'median mkt inv at sale':>24}")
    for product in PRODUCTS:
        events = []
        for i, st in enumerate(steps):
            action = st[seat].get("action")
            if not isinstance(action, dict):
                continue
            for order in (action.get("market") or [])[:10]:
                if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL" and order[1] == product:
                    inv = st[seat]["observation"]["market"]["inventory"].get(product, I0)
                    events.append((i // TURNS, int(order[2]), inv))
        if not events:
            continue
        total = sum(e[1] for e in events)
        invs = sorted(e[2] for e in events)
        med = invs[len(invs) // 2] - I0
        print(f"{product:<12}{total:>11,}{events[0][0]:>11}{events[-1][0]:>10}{med:>+24,}")

    # ---- shed high-water mark: were they holding stock or clearing it?
    print()
    peak = collections.Counter()
    final = {}
    for i, st in enumerate(steps):
        shed = st[seat]["observation"].get("private", {}).get("shed", {})
        for k, v in shed.items():
            peak[k] = max(peak[k], v)
    final = steps[-1][seat]["observation"].get("private", {}).get("shed", {})
    print("peak shed holding:", {k: v for k, v in peak.most_common() if v})
    print("FINAL shed (scores zero):", {k: v for k, v in final.items() if v})


if __name__ == "__main__":
    main()
