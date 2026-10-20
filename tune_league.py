"""Tune a route agent's reflex constants against a league of real opponents.

    python tune_league.py --screen            # one-at-a-time sensitivity
    python tune_league.py --search --iters 40 # (1+lambda) search over the survivors
    python tune_league.py --validate "V9_CARROT_RATIO=1.4,CROP_MIN_PRICE=50"

WHY THIS SHAPE

This is the surviving half of the opponent-modelling / MPC / league / CMA-ES
plan, after the parts that this game has already refuted.

Planning is out. The v9/4 author built a from-scratch demand-driven planner and
scored 990-1,578 live against 2,945 for the tape; our own planner agent (V5)
scored 1,448. Two independent attempts, same band. A 720-step season also costs
2-9 s to simulate once, against a 1 s per-action budget, so MPC over the real
engine cannot run at all -- it would need a surrogate model nobody has built.

What is left is the part that fits a tape architecture: a LEAGUE of real
opponents, and a SEARCH over the reflex constants that sit on top of the tape.

THE LEAGUE IS THE POINT

Our local ladders have twice predicted a gain that did not survive contact with
the live field:

    MiMi's lifted route   +24 wins on recorded tapes -> 8-32 on held-out seeds
    V5 over V4            60-10 on held-out seeds    -> +19 live rating points

Both failures share a cause: the pool. Reconstructions of opponents, and our
own lineage, are not the field. The league below is made only of agents that
actually scored on the public ladder, which is the closest stand-in we have.

A candidate must beat the incumbent AND not lose ground against the league,
on seeds it was never screened on, both seats. Search on one block, confirm on
another. The screen block is deliberately small and the confirm block large:
screening is for ranking, confirmation is for deciding.
"""
import argparse
import itertools
import os
import random
import subprocess
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "kernels/pub_2945.py"

# Only agents with a real public-ladder score. Ordered strongest first.
LEAGUE = [
    ("kernels/pub_2945.py", "2945 stock"),
    ("kernels/pub_v50.py", "V50"),
    ("kernels/pub_2749.py", "2749 melon"),
    ("kernels/public_lb2727.py", "2727 V37"),
]

# name -> values to screen. Centre value first; it must be the shipped default.
KNOBS = {
    "V9_FERT_CROPS": [("WHEAT", "CARROT"), (), ("CARROT",), ("WHEAT",)],
    "V9_FERT_AGES": [(1,), (1, 2), (2,)],
    "V9_FERT_FIRST_DAY": [16, 12, 20],
    "V9_CARROT_RATIO": [1.8, 1.4, 2.2],
    "V9_CARROT_FIRST_DAY": [10, 8, 13],
    "CROP_MIN_PRICE": [70, 50, 90],
    "V9_RACE_DEFAULT": [40, 20, 60],
    "V9_HERD_MIN_WOOL": [150, 120, 180],
    "V9_HERD_MIN_MILK": [150, 120, 180],
    "V9_COURIER_FROM_HOUR": [12, 8, 16],
}

SCREEN_SEEDS = "97000-97019"
CONFIRM_SEEDS = "98000-98039"


def fmt(overrides):
    return ",".join("%s=%r" % (k, v) for k, v in overrides.items())


def run_ladder(overrides, seeds, pool, workers, label="cand"):
    """Play the override set against `pool`. Returns (wins, losses, per-opponent)."""
    spec = BASE + (":" + fmt(overrides) if overrides else "") + "#" + label
    cmd = [sys.executable, "ladder.py", "--challenger", spec,
           "--pool"] + ["%s#%s" % (p, n) for p, n in pool] + \
          ["--seeds", seeds, "--workers", str(workers)]
    out = subprocess.run(cmd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", cwd=PROJECT).stdout
    wins = losses = 0
    per = {}
    for line in out.splitlines():
        if " vs " not in line or "mean" not in line:
            continue
        left, rest = line.strip().split(" vs ", 1)
        parts = left.split()
        rec = parts[-1]
        try:
            a, b = (int(x) for x in rec.split("-"))
        except ValueError:
            continue
        row = " ".join(parts[:-1])
        opp = rest.split("  mean")[0].strip()
        if row.startswith(label):
            wins += a; losses += b; per[opp] = (a, b)
        elif opp.startswith(label):
            wins += b; losses += a; per[row] = (b, a)
    return wins, losses, per


def screen(workers):
    print("SENSITIVITY SCREEN -- each knob moved alone, against the whole league")
    print("seeds %s, both seats\n" % SCREEN_SEEDS)
    base_w, base_l, _ = run_ladder({}, SCREEN_SEEDS, LEAGUE[1:], workers, "stock")
    print("stock baseline vs league: %d-%d (%.1f%%)\n" % (
        base_w, base_l, 100.0 * base_w / max(1, base_w + base_l)))
    rows = []
    for name, values in KNOBS.items():
        for v in values[1:]:
            w, l, _ = run_ladder({name: v}, SCREEN_SEEDS, LEAGUE[1:], workers, "cand")
            delta = w - base_w
            rows.append((delta, name, v, w, l))
            print("  %-24s %-18r %4d-%-4d  %+d" % (name, v, w, l, delta))
    rows.sort(reverse=True)
    print("\nranked by win delta against the league:")
    for delta, name, v, w, l in rows:
        print("  %+4d  %s=%r" % (delta, name, v))
    print("\nA positive here is a CANDIDATE, not a result. Confirm the best few "
          "on %s before believing any of it." % CONFIRM_SEEDS)
    return rows


def search(iters, workers, seed=7):
    """(1+lambda) hill climb over the knobs -- the method that built LB2448."""
    rng = random.Random(seed)
    best = {}
    best_w, best_l, _ = run_ladder(best, SCREEN_SEEDS, LEAGUE[1:], workers, "stock")
    print("start: stock %d-%d" % (best_w, best_l))
    for it in range(1, iters + 1):
        cand = dict(best)
        name = rng.choice(list(KNOBS))
        cand[name] = rng.choice(KNOBS[name][1:])
        if cand == best:
            continue
        w, l, _ = run_ladder(cand, SCREEN_SEEDS, LEAGUE[1:], workers, "cand")
        keep = w > best_w
        print("  %02d  %-46s %4d-%-4d %s" % (it, fmt(cand)[:46], w, l,
                                             "KEEP" if keep else ""))
        if keep:
            best, best_w, best_l = cand, w, l
    print("\nbest on the screen block: %s  (%d-%d)" % (fmt(best) or "stock", best_w, best_l))
    return best


def validate(overrides, workers):
    print("CONFIRMATION on held-out seeds %s, both seats" % CONFIRM_SEEDS)
    print("candidate: %s\n" % (fmt(overrides) or "stock"))
    w, l, per = run_ladder(overrides, CONFIRM_SEEDS, LEAGUE, workers, "cand")
    for opp, (a, b) in sorted(per.items()):
        flag = "" if a >= b else "   <-- loses this matchup"
        print("  vs %-16s %3d-%-3d%s" % (opp, a, b, flag))
    print("\n  total %d-%d (%.1f%%)" % (w, l, 100.0 * w / max(1, w + l)))
    inc = per.get("2945 stock")
    if inc is None:
        print("\n  incumbent not in the pool -- rerun with the full league")
    elif inc[0] <= inc[1]:
        print("\n  VETO: does not beat the incumbent it would replace (%d-%d). "
              "Do not submit." % inc)
    else:
        print("\n  veto clear: beats the incumbent %d-%d" % inc)
    return w, l


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen", action="store_true")
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--validate")
    ap.add_argument("--iters", type=int, default=30)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    if args.screen:
        screen(args.workers)
    elif args.search:
        best = search(args.iters, args.workers)
        if best:
            validate(best, args.workers)
    elif args.validate:
        ov = {}
        for chunk in args.validate.split(","):
            k, _, v = chunk.partition("=")
            ov[k.strip()] = eval(v.strip())
        validate(ov, args.workers)
    else:
        ap.error("pick --screen, --search or --validate")


if __name__ == "__main__":
    main()
