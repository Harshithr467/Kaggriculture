"""Who actually captures the price on each product, and by how much?

The four premium products collapse to a price of 1 once the shared book gluts,
so a game is largely decided by who sells into the book first. This replays one
live game and reports, per product and per player, units sold and the realised
average price per unit -- reconstructed by walking the engine's own per-unit
repricing over the market inventory as it stood before each turn.

    python sale_race.py --opponent kernels/rayk_c95.py --seed 901

A large realised-price gap on MELON / MILK / STRAWBERRY / WOOL means one side is
consistently reaching the book first. That is the thing slot ordering and the
one-turn shift are meant to buy, so it is worth knowing whether we already have
it before building either.
"""
import argparse
import collections
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS, market_price)

PREMIUM = ("MELON", "MILK", "STRAWBERRY", "WOOL")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="agent_combined.py")
    ap.add_argument("--opponent", default="kernels/rayk_c95.py")
    ap.add_argument("--seed", type=int, default=901)
    args = ap.parse_args()

    import benchmark_pool as BP
    from kaggle_environments import make

    us = BP._get_agent(args.ref)
    BP._restore(us, BP._pristine_state[args.ref])
    them = BP._get_agent(args.opponent)
    env = make("kaggriculture", configuration={"seed": args.seed}, debug=False)
    env.run([us.agent, them.agent])

    units = [collections.Counter(), collections.Counter()]
    revenue = [collections.Counter(), collections.Counter()]
    first_slot = [collections.defaultdict(list), collections.defaultdict(list)]

    for i in range(len(env.steps) - 1):
        inv = dict(((env.steps[i][0].observation.get("market") or {})
                    .get("inventory") or {}))
        queues = []
        for seat in (0, 1):
            action = env.steps[i + 1][seat].action
            m = action.get("market") or [] if isinstance(action, dict) else []
            queues.append(list(m)[:10])
            for slot, order in enumerate(queues[seat]):
                if (isinstance(order, (list, tuple)) and len(order) >= 3
                        and order[0] == "SELL" and order[1] in PREMIUM
                        and int(order[2]) > 0):
                    first_slot[seat][order[1]].append(slot)

        # Replay the engine's slot-by-slot lockstep to price each unit.
        for slot in range(max(len(q) for q in queues) if queues else 0):
            live = {}
            for seat in (0, 1):
                if slot < len(queues[seat]):
                    o = queues[seat][slot]
                    if (isinstance(o, (list, tuple)) and len(o) >= 3
                            and o[0] == "SELL" and o[1] in MARKET_PARAMS):
                        live[seat] = [o[1], int(o[2])]
            while any(v[1] > 0 for v in live.values()):
                quotes = {s: market_price(v[0], inv.get(v[0], 10000))
                          for s, v in live.items() if v[1] > 0}
                for seat, price in quotes.items():
                    item = live[seat][0]
                    units[seat][item] += 1
                    revenue[seat][item] += price
                    live[seat][1] -= 1
                    if price > 1:
                        inv[item] = inv.get(item, 10000) + 1

    print(f"seed {args.seed}   us = {args.ref}   them = "
          f"{os.path.basename(args.opponent)}\n")
    print(f"{'item':<12}{'our units':>10}{'our avg':>9}{'their units':>13}"
          f"{'their avg':>11}{'our slot':>10}{'their slot':>12}")
    for item in PREMIUM:
        ou, tu = units[0][item], units[1][item]
        oa = revenue[0][item] / ou if ou else 0
        ta = revenue[1][item] / tu if tu else 0
        os_ = first_slot[0][item]
        ts_ = first_slot[1][item]
        oslot = sum(os_) / len(os_) if os_ else float("nan")
        tslot = sum(ts_) / len(ts_) if ts_ else float("nan")
        print(f"{item:<12}{ou:>10,}{oa:>9,.0f}{tu:>13,}{ta:>11,.0f}"
              f"{oslot:>10.1f}{tslot:>12.1f}")

    for seat, label in ((0, "us"), (1, "them")):
        total = sum(revenue[seat].values())
        prem = sum(revenue[seat][i] for i in PREMIUM)
        print(f"\n{label:<6} total sale revenue {total:>12,}"
              f"   of which premium {prem:>12,}")


if __name__ == "__main__":
    main()
