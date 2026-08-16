"""Sequential test: play only as many games as the decision actually needs.

Every A/B here has used a fixed number of games -- 96 a stage, 192 for the
CMA-ES triple -- chosen in advance and read once at the end. That wastes games
twice over. A hopeless candidate is obvious after twenty and still gets its
ninety-six; a strong one is obvious after sixty and still gets ninety-six. And
reading a fixed-sample test on a result you chose to look at quietly inflates
the false-positive rate, which is exactly how run one of the optimiser produced
a "+24 point" candidate that was worth nothing.

This is the tool chess engines use for the same problem -- Fishtest decides
whether a Stockfish patch is worth keeping from noisy game results -- adapted
to our pooled, paired setup.

    python sprt.py --sweep ANIMAL_MARGIN_BIAS.SHEEP 2.7289 3.2
    python sprt.py --sweep TRAVEL_DIVISOR 16.6979 20.0 --h1 0.57
    python sprt.py --champion-ref f454950            # candidate = working tree


HOW THE PAIRING WORKS

Candidate and champion play the *same* games: same seeds, same opponents from
the pool, both seats. Each (opponent, seed, seat) is then one matched pair:

    candidate won it and champion lost it   -> candidate scores 1
    both won it, or both lost it            -> 0.5, a draw
    candidate lost it and champion won it   -> 0

Pairing this way removes the game-to-game variance that dominates raw win rates
-- both sides face the identical shop draw and the identical opponent -- so a
pair is far more informative than two independent games. Most pairs come back
as draws, which is the point: they cost almost no information but also add
almost no variance, and the test converges on the pairs that actually differ.


THE TEST

H0: the candidate scores 0.50 against the champion (no better)
H1: the candidate scores `--h1` (default 0.55, a real but modest improvement)

After each batch it updates a log-likelihood ratio and stops as soon as the LLR
crosses a bound set by the error rates (alpha = beta = 0.05 gives +/-2.94).
Unlike a fixed-sample test, the error rates hold *despite* looking after every
batch -- that is the whole point of a sequential test, and why it is safe to
watch it run.

The LLR uses the generalised SPRT with the variance estimated from the observed
pairs, which is the standard practical form when the outcome is a score rather
than a plain win or loss.
"""
import argparse
import math
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

from benchmark_pool import DEFAULT_POOL, run                       # noqa: E402


def bounds(alpha, beta):
    """(lower, upper) log-likelihood-ratio bounds. Cross low -> accept H0."""
    return math.log(beta / (1 - alpha)), math.log((1 - beta) / alpha)


def llr(scores, s0, s1):
    """Generalised SPRT log-likelihood ratio for a sequence of pair scores.

    Variance is estimated from the observations rather than assumed, which is
    what makes this usable when most pairs are draws and the spread is nothing
    like a coin flip's.
    """
    n = len(scores)
    if n < 2:
        return 0.0
    mean = sum(scores) / n
    var = sum((s - mean) ** 2 for s in scores) / n
    if var <= 1e-12:
        # Every pair identical. With no spread the test cannot discriminate;
        # report no evidence rather than dividing by ~zero.
        return 0.0
    return n * (s1 - s0) * (mean - (s0 + s1) / 2.0) / var


def pair_batch(rows):
    """Match candidate rows to champion rows on (opponent, seed, seat)."""
    cand, champ = {}, {}
    for label, opp, seed, seat, mine, theirs in rows:
        (cand if label == "candidate" else champ)[(opp, seed, seat)] = mine > theirs
    scores = []
    for key, cand_won in cand.items():
        if key not in champ:
            continue
        champ_won = champ[key]
        if cand_won and not champ_won:
            scores.append(1.0)
        elif champ_won and not cand_won:
            scores.append(0.0)
        else:
            scores.append(0.5)
    return scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", nargs=3, metavar=("PATH", "CHAMPION", "CANDIDATE"),
                    help="constant path, champion value, candidate value")
    ap.add_argument("--champion-ref", default=None,
                    help="git revision for the champion instead of a constant value")
    ap.add_argument("--h1", type=float, default=0.55,
                    help="pair score under H1; 0.55 is a real but modest gain")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--beta", type=float, default=0.05)
    ap.add_argument("--seed-start", type=int, default=600)
    ap.add_argument("--batch-seeds", type=int, default=2)
    ap.add_argument("--max-games", type=int, default=400)
    ap.add_argument("--pool", nargs="*", default=DEFAULT_POOL)
    ap.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 4))
    args = ap.parse_args()

    if args.sweep:
        path, champ_raw, cand_raw = args.sweep
        champ_over = ((path, eval(champ_raw)),)
        cand_over = ((path, eval(cand_raw)),)
        champ_ref = None
        what = f"{path}: {champ_raw} -> {cand_raw}"
    elif args.champion_ref:
        champ_over = cand_over = None
        champ_ref = args.champion_ref
        what = f"working tree vs {args.champion_ref}"
    else:
        sys.exit("give --sweep PATH CHAMPION CANDIDATE, or --champion-ref REV")

    low, high = bounds(args.alpha, args.beta)
    per_batch = len(args.pool) * args.batch_seeds * 2
    print(f"SPRT  {what}")
    print(f"  H0 pair score 0.500   H1 {args.h1:.3f}   "
          f"alpha {args.alpha}  beta {args.beta}")
    print(f"  bounds [{low:+.3f}, {high:+.3f}]   pool {args.pool}")
    print(f"  {per_batch} games per side per batch, cap {args.max_games} per side\n")
    print(f"  {'games':>6}{'W':>5}{'D':>5}{'L':>5}{'score':>8}{'LLR':>9}")

    scores = []
    seed = args.seed_start
    played = 0
    while played < args.max_games:
        seeds = list(range(seed, seed + args.batch_seeds))
        seed += args.batch_seeds
        # The candidate is always the working tree; only the champion may come
        # from a git revision. Both sides get the same seeds in the same call,
        # which is what makes the pairing exact.
        rows = run([("candidate", None, cand_over),
                    ("champion", champ_ref, champ_over)],
                   seeds, args.pool, args.workers)
        scores += pair_batch(rows)
        played += per_batch

        w = sum(1 for s in scores if s == 1.0)
        d = sum(1 for s in scores if s == 0.5)
        l = sum(1 for s in scores if s == 0.0)
        value = llr(scores, 0.5, args.h1)
        mean = sum(scores) / len(scores) if scores else 0.5
        print(f"  {played:>6}{w:>5}{d:>5}{l:>5}{mean:>8.3f}{value:>9.3f}", flush=True)

        if value >= high:
            print(f"\n  ACCEPT the candidate. LLR {value:+.3f} crossed {high:+.3f} "
                  f"after {played} games a side.")
            print(f"  {w} pairs to the candidate, {l} to the champion, {d} drawn.")
            return
        if value <= low:
            print(f"\n  REJECT the candidate. LLR {value:+.3f} crossed {low:+.3f} "
                  f"after {played} games a side.")
            print(f"  {w} pairs to the candidate, {l} to the champion, {d} drawn.")
            return

    print(f"\n  INCONCLUSIVE at the {args.max_games}-game cap. "
          f"LLR {llr(scores, 0.5, args.h1):+.3f} is still inside "
          f"[{low:+.3f}, {high:+.3f}].")
    print("  That is a result too: the effect, if any, is smaller than H1. "
          "Raise --max-games, or lower --h1 to test for a smaller gain.")


if __name__ == "__main__":
    main()
