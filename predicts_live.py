"""Does local benchmarking predict the leaderboard? Round-robin our own history.

Every candidate so far has been accepted or rejected on local games, and twice
now a change validated locally has moved the live rating by nothing. Before
spending the remaining weeks tuning against a local number, it is worth asking
whether that number predicts the only one that counts.

Five submissions have both a settled live rating and a known git revision, so
they are a labelled set. Play them round-robin against each other, rank them by
local win rate, and compare that ranking to the live one. If the two agree, the
local benchmark is a usable filter and tuning against it is rational. If they
do not, every local result is a coin flip dressed up as evidence, and the only
honest loop is submit-and-measure.

    python predicts_live.py --seeds 900 901 902 903 904 905 906 907
"""
import argparse
import itertools
import os
import statistics
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

from benchmark_pool import run                                      # noqa: E402

# (git revision, submission id, settled live rating). Ratings read 2026-08-16;
# the two most recent are still moving, which is noted in the output.
SUBMISSIONS = [
    ("c34629c", "55387160", 822.9),
    ("229c184", "55397388", 892.0),
    ("f454950", "55414416", 851.8),
    ("cc1f527", "55514059", 838.4),
    ("465fbf0", "55536047", 866.2),
]


def spearman(xs, ys):
    """Rank correlation, which is what we care about -- ordering, not spacing."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int,
                    default=[900, 901, 902, 903, 904, 905, 906, 907])
    ap.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 4))
    args = ap.parse_args()

    refs = [r for r, _s, _e in SUBMISSIONS]
    pairs = list(itertools.combinations(refs, 2))
    print(f"round-robin over {len(refs)} submissions, {len(pairs)} pairings, "
          f"seeds {args.seeds}")
    print(f"{len(pairs) * len(args.seeds) * 2} games\n")

    wins = {r: 0.0 for r in refs}
    games = {r: 0 for r in refs}
    scores = {r: [] for r in refs}
    head_to_head = {}

    for a, b in pairs:
        # `a` is the candidate, `b` the opponent; both seats are played inside run().
        rows = run([(a, a, None)], args.seeds, [b], args.workers)
        aw = 0
        for _label, _opp, _seed, _seat, mine, theirs in rows:
            games[a] += 1
            games[b] += 1
            scores[a].append(mine)
            scores[b].append(theirs)
            if mine > theirs:
                wins[a] += 1
                aw += 1
            elif theirs > mine:
                wins[b] += 1
            else:
                wins[a] += 0.5
                wins[b] += 0.5
        head_to_head[(a, b)] = (aw, len(rows))
        print(f"  {a} vs {b}: {aw}/{len(rows)}", flush=True)

    local = {r: wins[r] / games[r] for r in refs}
    live = {r: e for r, _s, e in SUBMISSIONS}
    sub = {r: s for r, s, _e in SUBMISSIONS}

    print(f"\n{'revision':<10}{'submission':>12}{'live':>9}{'local win%':>12}"
          f"{'mean score':>12}")
    for r in sorted(refs, key=lambda r: -live[r]):
        print(f"  {r:<8}{sub[r]:>12}{live[r]:>9.1f}{100*local[r]:>11.1f}%"
              f"{statistics.mean(scores[r]):>12,.0f}")

    xs = [local[r] for r in refs]
    ys = [live[r] for r in refs]
    rho = spearman(xs, ys)
    print(f"\nSpearman rank correlation, local win rate vs live rating: {rho:+.2f}")
    if rho >= 0.7:
        print("  Local ordering matches live. Tuning against the pool is rational.")
    elif rho >= 0.3:
        print("  Weak agreement. Local results are a soft filter, not evidence;\n"
              "  expect roughly half of locally validated changes to do nothing live.")
    else:
        print("  Local ordering does NOT match live. Every local verdict so far is\n"
              "  close to a coin flip about the leaderboard, and the only honest\n"
              "  loop is submit-and-measure at the pace the rating settles.")
    print("\nCaveat: five points, and the two newest ratings are still moving.\n"
          "A rank correlation on n=5 is indicative, not conclusive.")


if __name__ == "__main__":
    main()
