"""Aggregate one team's policy across many replays.

A single replay confuses deliberate policy with seed luck. Averaging a team's
build across many games separates the two: what they do every game is strategy,
what varies is adaptation.

    python profile_team.py kaggle_episode_data/replays/top1_thunder
    python profile_team.py <dir> --team "THUNDER THUNDER"
"""
import argparse
import collections
import glob
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
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--team", default=None)
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.directory, "*.json")))
    games = []
    tally = collections.Counter()
    for path in files:
        try:
            raw = json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            print(f"skip {os.path.basename(path)}: {exc}")
            continue
        steps = raw.get("steps") or []
        if not steps:
            continue
        rewards = [s.get("reward") for s in steps[-1]]
        if any(r is None for r in rewards):
            continue
        names = (raw.get("info", {}) or {}).get("TeamNames") or ["P0", "P1"]
        for nm in set(names):
            tally[nm] += 1
        games.append((os.path.basename(path), names, rewards, steps))

    team = args.team or tally.most_common(1)[0][0]
    print(f"profiling {team!r} across {len(games)} replays "
          f"(appears in {tally[team]})")
    print()

    print(f"{'episode':>14}{'seat':>5}{'theirs':>10}{'opp':>10}{'result':>8}  opponent")
    wins = 0
    profiles = []
    for name, names, rewards, steps in games:
        if team not in names:
            continue
        seat = names.index(team)
        mine, theirs = rewards[seat], rewards[1 - seat]
        wins += mine > theirs
        print(f"{name:>14}{seat:>5}{mine:>10,.0f}{theirs:>10,.0f}"
              f"{'WIN' if mine > theirs else 'loss':>8}  {names[1-seat]}")
        profiles.append((seat, steps, mine))

    print()
    print(f"record {wins}/{len(profiles)}   avg score "
          f"{sum(p[2] for p in profiles)/max(1,len(profiles)):,.0f}")
    print()

    # ---- daily build, averaged
    print("AVERAGE BUILD BY DAY")
    print(f"{'day':>4}{'money':>10}{'hands':>7}{'quads':>7}"
          f"{'wheat':>7}{'carr':>6}{'tom':>6}{'straw':>7}{'melon':>7}"
          f"{'goose':>7}{'cow':>6}{'sheep':>7}{'idle':>6}")
    for day in range(30):
        acc = collections.Counter()
        n = 0
        for seat, steps, _ in profiles:
            idx = min(day * TURNS + 12, len(steps) - 1)
            if idx >= len(steps):
                continue
            obs = steps[idx][seat].get("observation") or steps[idx][0].get("observation")
            farm = obs["farms"][seat]
            crop = collections.Counter()
            animal = collections.Counter()
            idle = 0
            for row in farm["tiles"]:
                for t in row:
                    if t is None:
                        idle += 1
                    elif isinstance(t, dict):
                        if t.get("kind") == "PLANT":
                            crop[t["crop"]] += 1
                        elif t.get("kind") == "WEED":
                            idle += 1
                        elif t.get("animal"):
                            animal[t["animal"]] += 1
            acc["money"] += farm["money"]
            acc["hands"] += len(farm["hands"])
            acc["quads"] += len(farm["unlocked_quadrants"])
            acc["idle"] += idle
            for c in CROPS:
                acc[c] += crop[c]
            for a in ANIMALS:
                acc[a] += animal[a]
            n += 1
        if not n:
            continue
        print(f"{day:>4}{acc['money']/n:>10,.0f}{acc['hands']/n:>7.1f}{acc['quads']/n:>7.1f}"
              f"{acc['WHEAT']/n:>7.1f}{acc['CARROT']/n:>6.1f}{acc['TOMATO']/n:>6.1f}"
              f"{acc['STRAWBERRY']/n:>7.1f}{acc['MELON']/n:>7.1f}"
              f"{acc['GOOSE']/n:>7.1f}{acc['COW']/n:>6.1f}{acc['SHEEP']/n:>7.1f}{acc['idle']/n:>6.1f}")

    # ---- action census and market behaviour
    ops = collections.Counter()
    sells = collections.Counter()
    sell_inv = collections.defaultdict(list)
    sell_day = collections.defaultdict(list)
    buys = collections.Counter()
    land_days = []
    for seat, steps, _ in profiles:
        seen_q = {}
        for i, st in enumerate(steps):
            day = i // TURNS
            entry = st[seat]
            action = entry.get("action")
            obs = entry.get("observation") or {}
            farm = (obs.get("farms") or [None, None])[seat] if obs.get("farms") else None
            if farm:
                q = len(farm["unlocked_quadrants"])
                seen_q.setdefault(q, day)
            if not isinstance(action, dict):
                continue
            for unit in [action.get("farmer", ["PASS"])] + list(action.get("hands") or []):
                if isinstance(unit, list) and unit:
                    ops[unit[0]] += 1
            for order in (action.get("market") or [])[:10]:
                if not isinstance(order, list) or not order:
                    continue
                if order[0] == "SELL" and len(order) >= 3:
                    sells[order[1]] += int(order[2])
                    inv = (obs.get("market") or {}).get("inventory", {}).get(order[1], I0)
                    sell_inv[order[1]].append(inv - I0)
                    sell_day[order[1]].append(day)
                elif order[0] in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT") and len(order) >= 3:
                    buys[f"{order[0].split('_')[1][:4].lower()}:{order[1]}"] += int(order[2])
                elif order[0] == "HIRE":
                    buys["HIRE"] += 1
        land_days.append(seen_q)

    total = sum(ops.values()) or 1
    n = len(profiles)
    print()
    print(f"ACTION MIX (per game): {total/n:,.0f} actions, "
          f"{100*sum(ops[m] for m in MOVES)/total:.1f}% movement, {100*ops['PASS']/total:.1f}% PASS")
    print("  ", {k: round(v / n) for k, v in ops.most_common(14) if k not in MOVES})

    print()
    print("LAND TIMING (median day reaching N quadrants):")
    for q in (2, 3, 4):
        days = sorted(d[q] for d in land_days if q in d)
        if days:
            print(f"  {q} quadrants: day {days[len(days)//2]}   ({len(days)}/{n} games)")
        else:
            print(f"  {q} quadrants: never")

    print()
    print("MARKET BEHAVIOUR (per game averages)")
    print(f"{'product':<12}{'sold':>9}{'median inv at sale':>21}{'first day':>11}{'last day':>10}")
    for product in PRODUCTS:
        if product not in sells:
            continue
        invs = sorted(sell_inv[product])
        days = sorted(sell_day[product])
        print(f"{product:<12}{sells[product]/n:>9,.0f}{invs[len(invs)//2]:>+21,}"
              f"{days[0]:>11}{days[-1]:>10}")

    print()
    print("PURCHASES (per game):", {k: round(v / n, 1) for k, v in buys.most_common(16)})


if __name__ == "__main__":
    main()
