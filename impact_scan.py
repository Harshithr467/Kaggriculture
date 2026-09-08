"""How much does our SELL ordering cost us inside a single turn?

The market reprices per unit inside an order, and orders resolve in the order we
submit them. So two SELLs of the same total quantity can fetch different sums
depending only on which goes first: whichever sells into the thinner book gets
the better average price, and the other eats the depression it caused.

This walks a real game, and at every turn where we submit two or more SELLs it
computes what our submitted order earned versus what the best permutation would
have earned, using the engine's own `market_price` -- including the `hinge`
shape, which the two public agents that embed a copy of the price table get
wrong for CARROT, TOMATO and EGG.

    python impact_scan.py --seed 901

The number this prints is an UPPER BOUND on what pure reordering can win, and
only for our own side of the book. It ignores the opponent entirely: both
players commit against the same pre-commit inventory and the engine interleaves
them, so a real reorder also races the opponent's orders. That part cannot be
measured here -- it needs live play.
"""
import argparse
import itertools
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS, market_price)


def proceeds(orders, inventory):
    """Revenue from running SELL orders in sequence, repricing per unit."""
    inv = dict(inventory)
    total = 0
    for _, item, qty in orders:
        for _ in range(int(qty)):
            price = market_price(item, inv.get(item, 10000))
            total += price
            if price > 1:
                inv[item] = inv.get(item, 10000) + 1
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="agent_combined.py")
    ap.add_argument("--opponent", default="kernels/rayk_c95.py")
    ap.add_argument("--seed", type=int, default=901)
    ap.add_argument("--seat", type=int, default=0)
    ap.add_argument("--max-perm", type=int, default=6,
                    help="brute-force permutations up to this many SELL lines")
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

    turns = 0
    gap_total = 0
    worst = (0, None)
    for i in range(len(env.steps) - 1):
        obs = env.steps[i][0].observation
        action = env.steps[i + 1][args.seat].action
        if not isinstance(action, dict):
            continue
        sells = [tuple(o) for o in (action.get("market") or [])
                 if isinstance(o, (list, tuple)) and len(o) >= 3
                 and o[0] == "SELL" and o[1] in MARKET_PARAMS
                 and int(o[2]) > 0]
        if len(sells) < 2:
            continue
        inventory = (obs.get("market") or {}).get("inventory") or {}
        mine = proceeds(sells, inventory)
        if len(sells) <= args.max_perm:
            best = max(proceeds(p, inventory) for p in itertools.permutations(sells))
        else:
            # too many lines to brute force: greedily take the highest quote first
            greedy = sorted(sells, key=lambda o: -market_price(
                o[1], inventory.get(o[1], 10000)))
            best = proceeds(greedy, inventory)
        turns += 1
        gap = best - mine
        gap_total += gap
        if gap > worst[0]:
            worst = (gap, (i, sells))

    print(f"seed {args.seed} seat {args.seat} vs {os.path.basename(args.opponent)}\n")
    print(f"turns submitting 2+ SELLs      {turns}")
    print(f"revenue left on the table      {gap_total:,} coins")
    if turns:
        print(f"average per such turn          {gap_total / turns:,.1f} coins")
    if worst[1]:
        step, sells = worst[1]
        print(f"\nworst single turn: step {step}, {worst[0]:,} coins")
        for o in sells:
            print(f"    {o[0]} {o[1]} {o[2]}")
    print("\nUpper bound on same-turn reordering only; ignores the opponent's "
          "orders,\nwhich interleave with ours against the same pre-commit "
          "inventory.")


if __name__ == "__main__":
    main()
