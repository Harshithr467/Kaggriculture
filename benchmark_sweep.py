"""Sweep a module-level constant in main.py against the committed baseline.

Finding the right TRAVEL_DIVISOR this way was worth ~+17,000 a game, and it is
also how the geese hypothesis was falsified in one run. Sweeping beats guessing:
pick the parameter that most directly controls the behaviour you suspect, try
several values at once, and read the shape of the curve rather than any single
cell.

    python benchmark_sweep.py TRAVEL_DIVISOR 4 12 25
    python benchmark_sweep.py MARGINAL_ACTION_VALUE 18 10 3 --seeds 20 21 22
    python benchmark_sweep.py ANIMAL_TOTAL_CAP "{1:5,2:12,3:19,4:22}"

Values are eval'd, so dicts and tuples work. Confirm any winner on a second,
unseen seed set before believing it -- a 10-game result is well inside noise.
"""
import argparse
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

from benchmark_ab import load_agent_from_git, play      # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="module-level constant in main.py")
    parser.add_argument("values", nargs="+", help="values to try (python literals)")
    parser.add_argument("--seeds", nargs="*", type=int, default=[0, 1, 2, 3, 4])
    parser.add_argument("--ref", default="HEAD")
    args = parser.parse_args()

    baseline = load_agent_from_git(args.ref)
    import main as current

    if not hasattr(current, args.name):
        sys.exit(f"main.py has no module-level constant {args.name!r}. "
                 "Lift it out of its function first so it can be swept.")

    original = getattr(current, args.name)
    print(f"sweeping {args.name}   baseline {args.ref} = {getattr(baseline, args.name, '?')}   "
          f"seeds {args.seeds}")
    print(f"{'value':>30}{'wins':>9}{'avg cur':>12}{'avg base':>12}{'margin':>12}")
    try:
        for raw in args.values:
            setattr(current, args.name, eval(raw))
            wins = cur_total = base_total = games = 0
            for seed in args.seeds:
                for seat in (0, 1):
                    mine, theirs = play(current.agent, baseline.agent, seed, seat)
                    cur_total += mine
                    base_total += theirs
                    wins += mine > theirs
                    games += 1
            print(f"{raw:>30}{wins:>6}/{games:<3}{cur_total/games:>12,.0f}"
                  f"{base_total/games:>12,.0f}{(cur_total-base_total)/games:>+12,.0f}", flush=True)
    finally:
        setattr(current, args.name, original)


if __name__ == "__main__":
    main()
