"""How many of our field actions change nothing?

Every unit gets one field op per turn, so a no-op is a turn spent buying nothing.
The engine silently ignores an op whose preconditions fail -- CARE on an animal
already cared for today, WATER on a tile already watered, HARVEST with no yield
ready, PICKUP of an item that is not there. Nothing errors and nothing in the
replay marks it.

This replays a game and, for every field op we issue, checks the same
precondition the engine checks, using the observation from the step BEFORE the
action. It reports what fraction of each op type did nothing.

    python wasted_actions.py --seed 901

Found this way: against Kaito Fukami's tape, which shares our exact day-0
opening, we issue 140 CARE actions across days 5-9 where he issues 47.
"""
import argparse
import collections
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return farm["tiles"][y][x]
    except (IndexError, TypeError, ValueError):
        return None


def is_noop(op, tile):
    """Mirror the engine's precondition for the ops worth auditing."""
    if op == "CARE":
        if not (isinstance(tile, dict) and "animal" in tile):
            return True, "no animal on tile"
        return bool(tile.get("cared_today")), "already cared today"
    if op == "WATER":
        if not (isinstance(tile, dict) and tile.get("kind") == "PLANT"):
            return True, "no plant on tile"
        return bool(tile.get("watered_today")), "already watered today"
    if op == "HARVEST":
        if not isinstance(tile, dict):
            return True, "nothing on tile"
        return int(tile.get("yield_units", 0) or 0) <= 0, "no yield ready"
    if op == "COLLECT_FERTILIZER":
        if not (isinstance(tile, dict) and "animal" in tile):
            return True, "no animal on tile"
        return not tile.get("fertilizer_available"), "nothing to collect"
    if op == "FERTILIZE":
        if not (isinstance(tile, dict) and tile.get("kind") == "PLANT"):
            return True, "no plant on tile"
        return False, ""
    return None, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="agent_combined.py")
    ap.add_argument("--opponent", default="kernels/rayk_c95.py")
    ap.add_argument("--seed", type=int, default=901)
    ap.add_argument("--seat", type=int, default=0)
    args = ap.parse_args()

    import benchmark_pool as BP
    import bench_losses as BL
    from kaggle_environments import make

    SHOPS = ["BAKERY", "BAKERY", "ICE_CREAM_SHOP", "ICE_CREAM_SHOP",
             "YARN_STORE", "YARN_STORE", "BRUNCH_SPOT", "FARMERS_MARKET"]
    us = BP._get_agent(args.ref)
    BP._restore(us, BP._pristine_state[args.ref])
    them = BP._get_agent(args.opponent)
    pair = ([us.agent, them.agent] if args.seat == 0 else [them.agent, us.agent])
    pin = BL._pin_town(SHOPS)
    try:
        env = make("kaggriculture", configuration={"seed": args.seed}, debug=False)
        env.run(pair)
    finally:
        BL._unpin_town(pin)

    total = collections.Counter()
    wasted = collections.Counter()
    reasons = collections.Counter()
    live = 0
    passes = 0

    for i in range(len(env.steps) - 1):
        obs = env.steps[i][0].observation
        farm = obs["farms"][args.seat]
        action = env.steps[i + 1][args.seat].action
        if not isinstance(action, dict):
            continue
        positions = [farm.get("farmer")] + list(farm.get("hands") or [])
        units = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
        for pos, unit in zip(positions, units):
            if not unit:
                continue
            op = unit[0]
            if op == "PASS":
                passes += 1
                continue
            live += 1
            total[op] += 1
            verdict, why = is_noop(op, tile_at(farm, pos))
            if verdict:
                wasted[op] += 1
                reasons[(op, why)] += 1

    print(f"seed {args.seed} seat {args.seat}\n")
    print(f"{'op':<22}{'issued':>9}{'no-op':>9}{'wasted':>9}")
    for op, n in total.most_common():
        w = wasted.get(op, 0)
        mark = f"{100 * w / n:>8.0f}%" if w else "        -"
        print(f"{op:<22}{n:>9,}{w:>9,}{mark}")
    print(f"\n{'live field actions':<22}{live:>9,}")
    print(f"{'PASS':<22}{passes:>9,}")
    print(f"{'audited no-ops':<22}{sum(wasted.values()):>9,}"
          f"   = {100 * sum(wasted.values()) / max(1, live):.1f}% of live actions")
    if reasons:
        print("\nwhy:")
        for (op, why), n in reasons.most_common(8):
            print(f"  {op:<20} {why:<26} {n:>6,}")


if __name__ == "__main__":
    main()
