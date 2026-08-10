"""Verify the market price model against real Kaggle replays, then report the
strategy thresholds it implies.

The six curve parameters per product are constants in the environment source
(MARKET_PARAMS in kaggriculture.py), not something to infer. What is worth
checking is whether the environment Kaggle actually runs uses those same
values: if the competition servers differed from the local pip package, every
glut threshold the agent trades on would be wrong.

Live replays record market inventory and price at every one of 720 steps, so
they settle it. This script:

  1. replays every (item, inventory) -> price pair from downloaded episodes and
     compares against the local model, reporting any mismatch
  2. independently recovers `base` and `T` from the data, to show the constants
     are identifiable from observation alone
  3. prints the derived thresholds that actually drive decisions -- how many
     units past equilibrium each product survives, and the revenue collected
     walking it to the floor

    python verify_market_model.py
    python verify_market_model.py --replays kaggle_episode_data/replays/55397388
"""
import argparse
import collections
import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaggle_environments.envs.kaggriculture.kaggriculture import (  # noqa: E402
    MARKET_PARAMS, PRODUCTS, market_price,
)

I0 = 10000
SHAPES = {
    "linear": lambda x: x,
    "sq": lambda x: x * x,
    "sqrt": math.sqrt,
    "log": lambda x: math.log(1.0 + x),
    "log10": lambda x: math.log10(1.0 + x),
}


def collect_observations(directory, limit):
    """Every distinct (item, inventory, price) the replays ever showed."""
    seen = collections.defaultdict(dict)      # item -> {inventory: price}
    files = sorted(glob.glob(os.path.join(directory, "*.json")))[:limit]
    for path in files:
        try:
            raw = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        for step in raw.get("steps") or []:
            market = step[0].get("observation", {}).get("market")
            if not market:
                continue
            inventory = market.get("inventory") or {}
            prices = market.get("prices") or {}
            for item, inv in inventory.items():
                if item in prices:
                    seen[item][inv] = prices[item]
    return seen, len(files)


def recover_params(item, samples):
    """Recover base and T from observed (inventory, price) pairs alone."""
    base = samples.get(I0)
    spec = MARKET_PARAMS[item]
    # Solve T from any point on each side: price = base +/- target*base*f(d)/f(T)
    recovered = {}
    for side, sign in (("below", +1), ("above", -1)):
        func = SHAPES[spec[side + "_func"]]
        target = spec[side + "_target"]
        estimates = []
        for inv, price in samples.items():
            d = (I0 - inv) if sign > 0 else (inv - I0)
            if d <= 0 or price <= 1:
                continue
            move = (price - (base if base else spec["base"])) * sign
            if move <= 0:
                continue
            # move = target*base*f(d)/f(T)  ->  f(T) = target*base*f(d)/move
            f_t = target * (base or spec["base"]) * func(d) / move
            # invert the shape to get T
            if spec[side + "_func"] == "linear":
                estimates.append(f_t)
            elif spec[side + "_func"] == "sq":
                estimates.append(math.sqrt(f_t))
            elif spec[side + "_func"] == "sqrt":
                estimates.append(f_t * f_t)
            elif spec[side + "_func"] == "log":
                estimates.append(math.exp(f_t) - 1.0)
        if estimates:
            estimates.sort()
            recovered[side] = estimates[len(estimates) // 2]
    return base, recovered


def glut_profile(item):
    """Units sellable past equilibrium before the $1 floor, and the revenue."""
    inv = I0
    revenue = 0.0
    units = 0
    while units < 500000:
        price = market_price(item, inv)
        if price <= 1:
            break
        revenue += price
        inv += 1
        units += 1
    return units, revenue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", default=None)
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()

    project = os.path.dirname(os.path.abspath(__file__))
    directory = args.replays or os.path.join(
        project, "kaggle_episode_data", "replays", "55397388")

    print("=== 1. does the environment Kaggle runs match the local model? ===")
    samples, n_files = collect_observations(directory, args.limit)
    if not samples:
        print(f"no replays found in {directory}; skipping verification")
    else:
        total = mismatches = 0
        worst = (0, None)
        for item, points in samples.items():
            if item not in MARKET_PARAMS:
                continue
            for inv, observed in points.items():
                predicted = market_price(item, inv)
                total += 1
                delta = abs(predicted - observed)
                if delta:
                    mismatches += 1
                    if delta > worst[0]:
                        worst = (delta, (item, inv, observed, predicted))
        print(f"checked {total:,} distinct (item, inventory) points from {n_files} live episodes")
        if mismatches == 0:
            print("PERFECT MATCH -- the competition servers use these exact parameters.")
        else:
            print(f"{mismatches:,} mismatches ({100*mismatches/total:.2f}%), worst {worst[0]}: {worst[1]}")

    print()
    print("=== 2. parameters recovered from replay data alone ===")
    print(f"{'item':<12}{'base obs':>10}{'base src':>10}{'T below':>10}{'T above':>10}{'T src':>8}")
    for item in PRODUCTS:
        if item not in samples:
            continue
        base, recovered = recover_params(item, samples[item])
        spec = MARKET_PARAMS[item]
        below = recovered.get("below")
        above = recovered.get("above")
        print(f"{item:<12}{(base if base else 0):>10}{spec['base']:>10}"
              f"{(f'{below:.0f}' if below else '-'):>10}"
              f"{(f'{above:.0f}' if above else '-'):>10}{spec['T']:>8}")
    print("(blank T means the replays never pushed that side far enough to solve for it)")

    print()
    print("=== 3. what the curves imply for strategy ===")
    header = (f"{'item':<12}{'base':>6}{'units to $1':>13}{'glut revenue':>14}"
              f"{'P(+25)':>8}{'P(+50)':>8}{'P(+100)':>9}{'P(+200)':>9}")
    print(header)
    print("-" * len(header))
    for item in PRODUCTS:
        units, revenue = glut_profile(item)
        cap = "unlimited" if units >= 500000 else f"{units:,}"
        print(f"{item:<12}{MARKET_PARAMS[item]['base']:>6}{cap:>13}{revenue:>14,.0f}"
              f"{market_price(item, I0+25):>8}{market_price(item, I0+50):>8}"
              f"{market_price(item, I0+100):>9}{market_price(item, I0+200):>9}")


if __name__ == "__main__":
    main()
