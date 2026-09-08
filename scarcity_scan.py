"""How far below equilibrium does each product's market inventory actually go?

Three products -- CARROT, TOMATO, EGG -- use the engine's `hinge` shape on the
scarce side of the price curve. Hinge is flat-ish until inventory drops T below
equilibrium and then runs away quadratically (HINGE_GAIN = 8). Every other
product uses linear/sqrt/log, which are tame in both directions.

That asymmetry is only worth money if the market really does go scarce. The
town drains inventory on a fixed clock whether or not anyone supplies it, so
this walks real replays and reports, per product, the deepest scarcity reached
and what the engine would have paid there.

    python scarcity_scan.py kaggle_episode_data/daily/2026-08-20

Note the two public agent notebooks that embed a copy of the price table both
transcribe CARROT, TOMATO and EGG as log/linear/linear instead of hinge, so
their own impact estimates are wrong on exactly this side of the curve.
"""
import argparse
import collections
import glob
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS, market_price)

HINGE = [i for i, p in MARKET_PARAMS.items() if p["below_func"] == "hinge"]


def scan(paths):
    deepest = collections.defaultdict(list)
    peak = collections.defaultdict(list)
    for path in paths:
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        low, high = {}, {}
        for frame in d.get("steps", []):
            inv = ((frame[0].get("observation") or {}).get("market") or {}).get("inventory")
            if not inv:
                continue
            for item, qty in inv.items():
                if item not in low or qty < low[item]:
                    low[item] = qty
                if item not in high or qty > high[item]:
                    high[item] = qty
        for item, qty in low.items():
            deepest[item].append(qty)
        for item, qty in high.items():
            peak[item].append(qty)
    return deepest, peak


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.folder, "*.json")))
    deepest, peak = scan(paths)
    if not deepest:
        raise SystemExit(f"no market inventory found under {args.folder}")

    print(f"{len(paths)} replays\n")
    print("SCARCE SIDE -- what the market pays when nobody supplies it")
    print(f"{'item':<12}{'shape':<8}{'median low':>12}{'worst low':>11}"
          f"{'price@med':>11}{'price@worst':>13}{'x base':>8}")
    for item, params in MARKET_PARAMS.items():
        lows = sorted(deepest.get(item, []))
        if not lows:
            continue
        median = lows[len(lows) // 2]
        worst = lows[0]
        p_med = market_price(item, median)
        p_worst = market_price(item, worst)
        print(f"{item:<12}{params['below_func']:<8}{median:>12,}{worst:>11,}"
              f"{p_med:>11,}{p_worst:>13,}{p_worst / params['base']:>8.1f}")

    print("\nGLUT SIDE -- what our own selling does to the price")
    print(f"{'item':<12}{'shape':<8}{'median high':>13}{'worst high':>12}"
          f"{'price@med':>11}{'price@worst':>13}{'% of base':>11}")
    for item, params in MARKET_PARAMS.items():
        highs = sorted(peak.get(item, []))
        if not highs:
            continue
        median = highs[len(highs) // 2]
        worst = highs[-1]
        p_med = market_price(item, median)
        p_worst = market_price(item, worst)
        print(f"{item:<12}{params['above_func']:<8}{median:>13,}{worst:>12,}"
              f"{p_med:>11,}{p_worst:>13,}{100 * p_worst / params['base']:>10.0f}%")

    print("\nhinge products (runaway when scarce):", ", ".join(HINGE))
    for item in HINGE:
        p = MARKET_PARAMS[item]
        print(f"\n  {item}: base {p['base']}, T {p['T']}, below_target {p['below_target']}")
        for u in (1, 2, 3, 4):
            inv = p["I0"] - u * p["T"]
            print(f"    {u}xT below equilibrium (inv {inv:,}): "
                  f"{market_price(item, inv):>6,}  = {market_price(item, inv) / p['base']:.0f}x base")


if __name__ == "__main__":
    main()
