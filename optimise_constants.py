"""Search several of main.py's constants jointly, against the opponent pool.

Every improvement this project has found came from one mis-set number, and
every one was found by sweeping a single constant while holding the rest still.
That method cannot see interactions, and the interactions are where the
remaining value is: weighting sheep up was worth +12.5 points of win rate only
because the margin ranking and room_cap interact, which no single-constant
sweep would have revealed.

    python optimise_constants.py --budget 60 --seeds 400 401 402 403
    python optimise_constants.py --resume --budget 40
    python optimise_constants.py --validate best      # on held-out seeds

CMA-ES, implemented here rather than pulled in, because the search is small
(6-8 noisy continuous dimensions) and the dependency is not worth it.


READ THIS BEFORE RUNNING IT: THE FIRST RUN SELECTED PURE NOISE

63 evaluations of 32 games each, six dimensions, search seeds 400-403. The best
candidate scored 90.6% on the search seeds and 64.6% on held-out seeds 410-415,
against 66.7% for the shipped constants -- a 26-point collapse, and 2.1 points
WORSE than changing nothing.

That is not bad luck, it is arithmetic. 32 games puts the standard error on a
win rate at 8.8 points. Simulating 63 candidates that are all secretly
identical at 66%, the best-looking one scores 84.5% on average and 90.6% at the
95th percentile. The observed winner scored 90.6%. Every point of its apparent
edge is explained by taking the maximum of 63 noisy draws.

To resolve a true 5-point difference you need a standard error near 1.5 points,
which is about 1,100 games per evaluation -- roughly 35x what this run used. A
60-evaluation search would then cost days, not hours.

So: do not run this with a small --seeds list. Either give each evaluation
enough games to see through the noise (10+ seeds, and expect an overnight run),
or cut the search to two or three dimensions. The honest conclusion from run
one is that single-constant sweeps confirmed on two independent seed sets --
the method this project already uses -- extract more signal per CPU-hour than
joint search does at any budget we can afford.

The holdout is what caught this, so never read a result off the search seeds.


THE OBJECTIVE, WHICH IS THE PART THAT MATTERS

The environment's reward is the final bank balance, but the competition ranks
on *wins* -- ELO while it runs, Bradley-Terry after. Those disagree, and not
subtly: restricting melon sales was worth +772 of our own money and -34 points
of win rate. Optimising money would have taken that trade and lost the season.

Optimising raw win rate instead has its own problem. It is one bit per game
against a per-game noise of roughly +/-4,000, so a 128-game evaluation resolves
almost nothing and CMA-ES would chase sampling noise.

So the objective is a soft win:

    fitness = mean over games of  sigmoid(margin / TEMPERATURE)

which is monotone in win probability, continuous enough to give the search a
gradient, and -- because sigmoid saturates -- pays nothing extra for winning a
game that was already won. That last property is the one we actually need. Live
replays have us outscoring opponents by +2,176 a game while winning about half:
we win large and lose narrow, and ELO pays nothing for the size of a win. A
money objective would reward exactly the pathology we already have.
"""
import argparse
import json
import math
import os
import random
import statistics
import sys

import numpy as np

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

from benchmark_pool import DEFAULT_POOL, run                       # noqa: E402

STATE = os.path.join(PROJECT, "kaggle_episode_data", "optimiser_state.json")
TEMPERATURE = 8000.0        # margin at which a game counts ~0.73 of a win

# (dotted path, low, high, round-to-int). Chosen for known live impact and for
# being continuous enough that a search can move them; caps that must stay
# integral are rounded. Keep this list short -- each evaluation is ~128 games.
SPACE = [
    ("ANIMAL_MARGIN_BIAS.SHEEP",  0.8,  3.5, False),
    ("ANIMAL_MARGIN_BIAS.COW",    0.5,  1.6, False),
    ("TRAVEL_DIVISOR",            6.0, 22.0, False),
    ("MARGINAL_ACTION_VALUE",    14.0, 45.0, False),
    ("ANIMAL_TOTAL_CAP.3",        9.0, 17.0, True),
    ("GLUT_ALLOWANCE.MELON",     80.0, 260.0, True),
]


def to_overrides(vector):
    out = []
    for (path, lo, hi, as_int), raw in zip(SPACE, vector):
        value = float(min(hi, max(lo, raw)))
        out.append((path, int(round(value)) if as_int else round(value, 4)))
    return tuple(out)


def fitness(vector, seeds, pool, workers):
    """Soft win rate in [0, 1], plus the plain numbers for reporting."""
    overrides = to_overrides(vector)
    rows = run([("cand", None, overrides)], seeds, pool, workers)
    soft, wins, ours, theirs = [], 0, [], []
    for _label, _opp, _seed, _seat, mine, opp in rows:
        soft.append(1.0 / (1.0 + math.exp(-(mine - opp) / TEMPERATURE)))
        wins += mine > opp
        ours.append(mine)
        theirs.append(opp)
    return (statistics.mean(soft), wins / len(rows),
            statistics.mean(ours), statistics.mean(theirs), overrides)


def cma_es(x0, sigma0, budget, evaluate, log):
    """Compact CMA-ES. Maximises `evaluate`."""
    n = len(x0)
    lam = 4 + int(3 * math.log(n))          # population
    mu = lam // 2
    weights = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1))
    weights /= weights.sum()
    mueff = 1.0 / np.sum(weights ** 2)

    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n)
    cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3) ** 2 + mueff)
    cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
    damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs
    chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n ** 2))

    xmean = np.array(x0, dtype=float)
    sigma = float(sigma0)
    pc = np.zeros(n)
    ps = np.zeros(n)
    B = np.eye(n)
    D = np.ones(n)
    C = np.eye(n)
    gen = 0
    used = 0
    best = (-1.0, None)

    while used + lam <= budget:
        gen += 1
        offspring = []
        for _ in range(lam):
            z = np.random.randn(n)
            x = xmean + sigma * (B @ (D * z))
            score = evaluate(x)
            used += 1
            offspring.append((score, x, z))
            if score > best[0]:
                best = (score, x.copy())
        offspring.sort(key=lambda t: -t[0])
        log(gen, used, offspring, best, sigma)

        xold = xmean.copy()
        xmean = sum(w * o[1] for w, o in zip(weights, offspring[:mu]))
        zmean = sum(w * o[2] for w, o in zip(weights, offspring[:mu]))

        ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * (B @ zmean)
        hsig = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * gen)) / chiN < 1.4 + 2 / (n + 1)
        pc = (1 - cc) * pc + hsig * math.sqrt(cc * (2 - cc) * mueff) * (xmean - xold) / sigma

        artmp = np.array([(o[1] - xold) / sigma for o in offspring[:mu]])
        C = ((1 - c1 - cmu) * C
             + c1 * (np.outer(pc, pc) + (not hsig) * cc * (2 - cc) * C)
             + cmu * artmp.T @ (weights[:, None] * artmp))
        sigma *= math.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))

        C = np.triu(C) + np.triu(C, 1).T
        eigvals, B = np.linalg.eigh(C)
        D = np.sqrt(np.maximum(eigvals, 1e-20))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=40, help="evaluations (each ~128 games)")
    ap.add_argument("--seeds", nargs="*", type=int, default=[400, 401, 402, 403])
    ap.add_argument("--holdout", nargs="*", type=int, default=[410, 411, 412, 413, 414, 415])
    ap.add_argument("--pool", nargs="*", default=DEFAULT_POOL)
    ap.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 4))
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--validate", default=None, help="'best' to re-check the saved best")
    args = ap.parse_args()

    import main as agent
    defaults = []
    for path, lo, hi, _as_int in SPACE:
        name, _, key = path.partition(".")
        value = getattr(agent, name)
        if key:
            holder = value
            value = holder.get(type(next(iter(holder)))(key)) if holder else None
        defaults.append(float(value))

    state = {}
    if (args.resume or args.validate) and os.path.exists(STATE):
        state = json.load(open(STATE, encoding="utf-8"))

    if args.validate:
        history = state.get("history") or []
        if not history:
            sys.exit("no saved history; run a search first")

        def as_vector(entry):
            """history entries store overrides by path; SPACE order is what fitness wants."""
            d = entry["overrides"]
            return [float(d[path]) for path, _lo, _hi, _ai in SPACE]

        best_soft = max(history, key=lambda h: h["soft"])
        # Win rate is the real objective -- soft fitness only smooths the search
        # signal, and at this temperature it still pays a little for margin, so
        # its argmax is not always the argmax of wins. Break ties on soft.
        best_win = max(history, key=lambda h: (h["win_rate"], h["soft"]))

        candidates = [("shipped", defaults),
                      ("best-soft", as_vector(best_soft)),
                      ("best-win", as_vector(best_win))]
        print(f"validating on held-out seeds {args.holdout} "
              f"({len(args.pool) * len(args.holdout) * 2} games each)\n")
        print(f"  {'candidate':<11}{'soft':>7}{'win%':>8}{'ours':>10}{'theirs':>10}"
              f"{'search win%':>13}")
        results = {}
        for label, v in candidates:
            soft, wr, ours, theirs, ov = fitness(v, args.holdout, args.pool, args.workers)
            results[label] = (soft, wr, dict(ov))
            searched = ("-" if label == "shipped"
                        else f"{100 * (best_soft if label == 'best-soft' else best_win)['win_rate']:.1f}")
            print(f"  {label:<11}{soft:>7.3f}{100*wr:>8.1f}{ours:>10,.0f}{theirs:>10,.0f}"
                  f"{searched:>13}")
        print()
        for label in ("best-soft", "best-win"):
            print(f"  {label}: {results[label][2]}")
        base = results["shipped"][1]
        print()
        for label in ("best-soft", "best-win"):
            got, searched = results[label][1], None
            print(f"  {label:<10} holdout {100*got:5.1f}% vs shipped {100*base:5.1f}%  "
                  f"-> {100*(got-base):+.1f}pp")
        print("\nA candidate that beat the search seeds but not the holdout is "
              "overfitting, not a finding.")
        return

    print(f"space:")
    for (path, lo, hi, _), d in zip(SPACE, defaults):
        print(f"  {path:<28}{d:>8.2f}   in [{lo}, {hi}]")
    print(f"\nbudget {args.budget} evaluations x {len(args.pool)*len(args.seeds)*2} games")
    print(f"objective: mean sigmoid(margin / {TEMPERATURE:.0f}) -- soft win rate\n")

    history = state.get("history", []) if args.resume else []
    seen = {}

    def evaluate(vec):
        key = json.dumps([round(float(x), 4) for x in vec])
        if key in seen:
            return seen[key]
        soft, wr, ours, theirs, ov = fitness(vec, args.seeds, args.pool, args.workers)
        seen[key] = soft
        history.append({"overrides": dict(ov), "soft": soft, "win_rate": wr,
                        "ours": ours, "theirs": theirs})
        json.dump({"history": history,
                   "best_vector": max(history, key=lambda h: h["soft"])["overrides"]},
                  open(STATE, "w", encoding="utf-8"), indent=1)
        return soft

    def log(gen, used, offspring, best, sigma):
        top = history[-1] if history else {}
        print(f"gen {gen:>3}  evals {used:>3}/{args.budget}  "
              f"best soft {best[0]:.3f}  sigma {sigma:.3f}", flush=True)
        for h in sorted(history[-len(offspring):], key=lambda h: -h["soft"])[:2]:
            print(f"        soft {h['soft']:.3f}  win {100*h['win_rate']:5.1f}%  "
                  f"{h['overrides']}", flush=True)

    # Search in normalised units so every dimension moves at a comparable rate.
    scale = np.array([(hi - lo) for _, lo, hi, _ in SPACE], dtype=float)
    lo_v = np.array([lo for _, lo, _, _ in SPACE], dtype=float)
    x0 = (np.array(defaults) - lo_v) / scale

    def evaluate_norm(xn):
        return evaluate(lo_v + np.clip(xn, 0.0, 1.0) * scale)

    random.seed(0)
    np.random.seed(0)
    best_score, best_norm = cma_es(x0, 0.25, args.budget, evaluate_norm, log)

    best = lo_v + np.clip(best_norm, 0.0, 1.0) * scale
    print(f"\nbest soft fitness {best_score:.3f}")
    print(f"  {dict(to_overrides(best))}")
    json.dump({"history": history, "best_vector": list(best)},
              open(STATE, "w", encoding="utf-8"), indent=1)
    print(f"\nstate -> {os.path.relpath(STATE, PROJECT)}")
    print("Now run --validate best on held-out seeds. The search set is tuned on; "
          "a gain that does not survive the holdout is overfitting, not a finding.")


if __name__ == "__main__":
    main()
