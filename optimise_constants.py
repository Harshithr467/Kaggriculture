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


THE OBJECTIVE

The environment's reward is the final bank balance, but the competition ranks
on *wins* -- ELO while it runs, Bradley-Terry after -- and the two disagree
sharply. Restricting melon sales was worth +772 of our own money and -34 points
of win rate; sheep bias past 1.7 keeps earning more while winning less.
Optimising money takes those trades and loses the season.

So win rate is the objective, ties counted as half:

    fitness = (wins + 0.5*ties)/games + (0.5/games) * mean tanh(margin / 20000)

The margin term is bounded in [-1, 1] and scaled to half of one game's worth of
win rate, so it can only break a tie between candidates with identical records.
It cannot reorder two candidates that differ by even a single game.

Run one used mean sigmoid(margin / 8000) instead, on the theory that a smooth
objective gives the search a usable gradient. It does, but it is a proxy: its
argmax there was a 65.6% candidate while a 78.1% one ranked below it. A proxy
that disagrees with the target on its own top candidates is not worth its
smoothness.
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

# One state file per (space, objective). Sharing one file made a route/replay
# run print the policy run's constants and seed ranges back at us, because
# the generation log reads history entries by generation number alone.
STATE = os.path.join(PROJECT, "kaggle_episode_data", "optimiser_state.json")


def state_path(space, objective):
    if space == "policy" and objective == "pool":
        return STATE          # the original run, kept where it was
    return os.path.join(PROJECT, "kaggle_episode_data",
                        f"optimiser_state_{space}_{objective}.json")

# Margin only ever breaks a tie. With `games` per evaluation the win rate moves
# in steps of 1/games, so keeping the margin term strictly under that step makes
# it arithmetically impossible for a lower win rate to outrank a higher one --
# which is the property run one's sigmoid objective did not have, and why its
# argmax was a 65.6% candidate while a 78.1% one sat below it.
MARGIN_WEIGHT_FRACTION = 0.5      # of one win, at most
MARGIN_SCALE = 20000.0            # tanh scale, so the term is bounded in [-1, 1]

# Seeds the search may draw from, and seeds it must never see. Generations draw
# a fresh slice of the bank so no candidate can overfit a fixed set -- run one
# reused four seeds for all 63 evaluations and its winner collapsed 26 points on
# the holdout.
SEED_BANK = list(range(400, 460))
HOLDOUT_SEEDS = list(range(500, 530))

# Three dimensions, not six: at the games-per-evaluation we can afford, every
# extra dimension costs resolution we do not have. These three have the largest
# measured behavioural effect, and run one pushed MARGINAL_ACTION_VALUE hard
# against its upper bound, which is worth resolving.
# Bounds matter more than they look. ANIMAL_MARGIN_BIAS.SHEEP enters only
# through a sort order, so once it is large enough to put sheep ahead of cows at
# any realistic price the agent stops responding to it: measured, every value
# from about 1.6 to 3.5 produces byte-identical games. Searching [0.8, 3.5] spent
# roughly seventy percent of that axis on a single behaviour, which is why the
# search happily returned 2.7289 -- a number that does nothing 2.0 would not.
# Run --check-space before trusting a new dimension.
# Two search spaces, because there are two agents. "policy" tunes main.py, the
# hand-written engine these constants were written for. "route" tunes the knobs
# agent_combined.py actually has -- and there are only two of them, because the
# route is a RECORDING: its behaviour lives in 720 recorded steps, not in
# constants. That thinness is the finding, not an oversight. CMA-ES over two
# dimensions is barely worth the machinery; the search that matters is discrete
# and over the trace itself.
# Parameters whose whole effect is how we behave RELATIVE to the opponent. The
# replay objective freezes the opponent, so it scores these as free money: it
# rated LOOKAHEAD 5 at +6 net wins where a live opponent has it at -3.1pp, and
# LOOKAHEAD 7 at +5 where live has it at -12.5pp. Tune them against a pool that
# can fight back.
REACTIVE_PARAMS = {"LOOKAHEAD", "EAGER_FLOOR_FRAC"}

SPACES = {
    "policy": [
        ("ANIMAL_MARGIN_BIAS.SHEEP",  0.8,  2.2, False),
        ("MARGINAL_ACTION_VALUE",    14.0, 60.0, False),
        ("TRAVEL_DIVISOR",            6.0, 22.0, False),
    ],
    "route": [
        ("LOOKAHEAD",          1.0, 8.0, True),
        ("EAGER_FLOOR_FRAC",   0.0, 1.2, False),
    ],
}
SPACE = SPACES["policy"]


def to_overrides(vector):
    out = []
    for (path, lo, hi, as_int), raw in zip(SPACE, vector):
        value = float(min(hi, max(lo, raw)))
        out.append((path, int(round(value)) if as_int else round(value, 4)))
    return tuple(out)


def generation_seeds(gen, count):
    """A fresh slice of the bank per generation; every candidate in a generation
    shares it, so candidates are compared on identical games (common random
    numbers) while the search as a whole cannot memorise one seed set."""
    start = (gen * count) % len(SEED_BANK)
    doubled = SEED_BANK + SEED_BANK
    return doubled[start:start + count]


def evaluate_candidate_replay(vector, generation, agent, submission,
                              wins_per_eval, workers):
    """Fitness from the games we actually played, against the agents that played them.

    See bench_losses.py. Fitness is the win rate over a rotating slice of live
    episodes -- all 39 losses every time plus `wins_per_eval` of the 99 wins --
    so a candidate is judged on flips gained MINUS wins given back, which is the
    quantity the ladder pays for. Money is reported and never allowed to outrank
    a single game.

    Absolute fitness is not comparable between generations, because the slice
    rotates; within a generation every candidate sees the same episodes. Same
    trade the seed bank makes, for the same reason.
    """
    import bench_losses as BL
    overrides = to_overrides(vector)
    indices = BL.fitness_indices(submission, wins_per_eval, generation)
    r = BL.evaluate(cand_ref=agent, overrides=overrides, submission=submission,
                    indices=indices, workers=workers)
    return {
        "overrides": dict(overrides),
        "fitness": r["fitness"], "win_rate": r["win_rate"],
        "games": r["games"], "wins": r["wins"], "losses": r["games"] - r["wins"],
        "ties": r["ties"], "flipped": r["flipped"], "given_back": r["given_back"],
        "money_per_game": r["money_per_game"],
        "ours": 0.0, "theirs": 0.0, "mean_margin": r["money_per_game"],
        "median_margin": r["money_per_game"], "norm_margin": 0.0,
        "win_rate_by_opponent": {}, "margin_by_seed": {}, "seeds": [],
    }


def evaluate_candidate(vector, seeds, pool, workers):
    """Head-to-head record for one candidate. Win rate is the objective."""
    overrides = to_overrides(vector)
    rows = run([("cand", None, overrides)], seeds, pool, workers)

    wins = losses = ties = 0
    margins, ours, theirs = [], [], []
    per_opponent = {}
    per_seed = {}
    for _label, opp_ref, seed, seat, mine, opp in rows:
        d = mine - opp
        if d > 0:
            wins += 1
        elif d < 0:
            losses += 1
        else:
            ties += 1
        margins.append(d)
        ours.append(mine)
        theirs.append(opp)
        b = per_opponent.setdefault(opp_ref, [0, 0])
        b[0] += (d > 0) + 0.5 * (d == 0)
        b[1] += 1
        per_seed.setdefault(str(seed), []).append(round(d))

    n = len(rows)
    win_rate = (wins + 0.5 * ties) / n
    norm_margin = statistics.mean(math.tanh(m / MARGIN_SCALE) for m in margins)
    # Bounded strictly below one game's worth of win rate: a tiebreaker, never
    # a thumb heavy enough to reorder two candidates with different records.
    fitness_value = win_rate + (MARGIN_WEIGHT_FRACTION / n) * norm_margin

    return {
        "overrides": dict(overrides),
        "fitness": fitness_value,
        "win_rate": win_rate,
        "games": n, "wins": wins, "losses": losses, "ties": ties,
        "ours": statistics.mean(ours), "theirs": statistics.mean(theirs),
        "mean_margin": statistics.mean(margins),
        "median_margin": statistics.median(margins),
        "norm_margin": norm_margin,
        "win_rate_by_opponent": {k: round(v[0] / v[1], 3) for k, v in per_opponent.items()},
        "margin_by_seed": per_seed,
        "seeds": list(seeds),
    }


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
            score = evaluate(x, gen)
            used += 1
            offspring.append((score, x, z))
            if score > best[0]:
                best = (score, x.copy())
        offspring.sort(key=lambda t: -t[0])
        log(gen, used, offspring, best, sigma, xmean)

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


# Game facts and structural constants: changing these does not tune the policy,
# it describes a different game. Excluded from the dead-range probe.
NOT_TUNABLE = {
    "TOTAL_DAYS", "TURNS_PER_DAY", "MAX_MARKET_ORDERS", "MARKET_I0", "CROPS",
    "ANIMALS", "PRODUCT_BASE_PRICE", "SHOPS", "LAND_COSTS", "SEED_PRIORITY",
    "SPAWN_QUADRANTS", "DAILY_ANIMAL_YIELD", "ANIMAL_FIRST_YIELD", "CROP_CYCLE",
    "PASS_RESPONSE", "SHOP_UNLOCK_INTERVAL", "MAX_SHOP_INSTANCES",
    "EXPECTED_SHOP_DEMAND", "ONGOING_INTERVAL",
}


def tunable_entries(agent):
    """(path, current value) for every numeric policy constant, dicts expanded."""
    out = []
    for name in sorted(dir(agent)):
        if name.startswith("_") or not name.isupper() or name in NOT_TUNABLE:
            continue
        value = getattr(agent, name)
        if isinstance(value, bool):
            out.append((name, value))
        elif isinstance(value, (int, float)):
            out.append((name, value))
        elif isinstance(value, dict):
            for key, inner in value.items():
                if isinstance(inner, (int, float)) and not isinstance(inner, bool):
                    out.append((f"{name}.{key}", inner))
    return out


def perturbations(path, value):
    """Two values either side of the current one, chosen to be meaningful."""
    if isinstance(value, bool):
        return [not value]
    if value > 10000:
        # An allowance this large is "never hold back". Halving it is still
        # never, so probe with a finite cap that could actually bind.
        return [300, 2000]
    lo, hi = value * 0.6, value * 1.6
    if isinstance(value, int):
        lo, hi = int(round(lo)), int(round(hi))
        if lo == value:
            lo = value - 1
        if hi == value:
            hi = value + 1
        if "DAY" in path:                    # keep day thresholds inside the season
            lo, hi = max(0, lo), min(29, hi)
    if abs(hi - value) < 1e-9 and abs(lo - value) < 1e-9:
        return []
    return [v for v in (lo, hi) if abs(v - value) > 1e-9]


def check_all(pool, seeds, workers):
    """Which constants does the agent actually respond to, near their current values?"""
    import main as agent
    entries = tunable_entries(agent)
    labels = [("BASE", None, None)]
    meta = {}
    for path, value in entries:
        for variant in perturbations(path, value):
            label = f"{path}={variant!r}"
            labels.append((label, None, ((path, variant),)))
            meta[label] = (path, value, variant)

    games = len(pool) * len(seeds) * 2
    print(f"probing {len(entries)} constants, {len(labels) - 1} perturbations, "
          f"{games} games each = {len(labels) * games} games")
    print("identical scores on identical seeds mean identical games\n")
    rows = run(labels, seeds, pool, workers)

    by = {}
    for label, opp, seed, seat, mine, _theirs in rows:
        by.setdefault(label, {})[(opp, seed, seat)] = mine
    base = by.get("BASE", {})
    keys = list(base)

    results = {}
    for label, (path, value, variant) in meta.items():
        got = by.get(label, {})
        differ = sum(1 for k in keys if abs(got.get(k, base[k]) - base[k]) > 1e-9)
        results.setdefault(path, []).append((variant, differ, value))

    dead, weak, live = [], [], []
    for path, trials in sorted(results.items()):
        total = sum(d for _v, d, _c in trials)
        (dead if total == 0 else weak if total <= 1 else live).append((path, trials))

    for title, group in (("NO EFFECT either direction -- dead knob", dead),
                         ("BARELY responds (1 game of %d)" % (len(keys) or 1), weak),
                         ("responds", live)):
        print(f"\n{title}: {len(group)}")
        for path, trials in group:
            cur = trials[0][2]
            shown = "  ".join(f"{v!r}->{d}/{len(keys)}" for v, d, _c in trials)
            print(f"  {path:<30} now {cur!r:<10} {shown}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--objective", choices=("pool", "replay"), default="pool",
                    help="'pool' plays fresh seeds against our own history; "
                         "'replay' re-plays the live episodes against the agents "
                         "that actually played them")
    ap.add_argument("--space", choices=tuple(SPACES), default="policy")
    ap.add_argument("--agent", default=None,
                    help="module to tune (file or git ref); default main.py")
    ap.add_argument("--submission", default="55563850",
                    help="replay objective: which submission's episodes to use")
    ap.add_argument("--wins-per-eval", type=int, default=30,
                    help="replay objective: wins sampled per evaluation, on top "
                         "of all 39 losses")
    ap.add_argument("--budget", type=int, default=35, help="evaluations")
    ap.add_argument("--seeds-per-eval", type=int, default=10)
    ap.add_argument("--holdout", nargs="*", type=int, default=HOLDOUT_SEEDS[:12])
    ap.add_argument("--pool", nargs="*", default=DEFAULT_POOL)
    ap.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 4))
    ap.add_argument("--validate", action="store_true",
                    help="stage-2 check of the search leader on held-out seeds")
    ap.add_argument("--promote", action="store_true",
                    help="stage-3 check on further holdout seeds, before shipping")
    ap.add_argument("--check-space", action="store_true",
                    help="verify each dimension actually changes behaviour before searching")
    ap.add_argument("--check-all", action="store_true",
                    help="probe every tunable constant in main.py for dead range")
    args = ap.parse_args()
    globals()["SPACE"] = SPACES[args.space]
    globals()["STATE"] = state_path(args.space, args.objective)
    if args.objective == "replay":
        bad = sorted(REACTIVE_PARAMS.intersection(p for p, *_ in SPACE))
        if bad:
            raise SystemExit(
                f"{', '.join(bad)} govern how we act relative to the opponent, and "
                f"the replay objective freezes the opponent, so it scores them as "
                f"free money (it rated LOOKAHEAD 5 at +6 net wins; live it is "
                f"-3.1pp). Tune these with --objective pool.")
    if args.objective == "replay" and args.space == "policy":
        raise SystemExit("--objective replay tunes the route agent; pass "
                         "--space route --agent agent_combined.py")

    if args.check_all:
        check_all(args.pool[:2], [600, 601], args.workers)
        return

    if args.check_space:
        # A dimension the agent does not respond to across most of its range is
        # budget thrown away, and it makes the search look like it is exploring
        # when it is not. Three points per axis, identical seeds, compare our own
        # final scores: identical scores mean identical games.
        seeds = [600, 601]
        pool = args.pool[:2]
        print("checking each dimension actually moves the agent")
        print("(same seeds, same opponents; identical scores mean identical games)\n")
        for path, lo, hi, _ai in SPACE:
            mid = (lo + hi) / 2
            labels = [(f"{v:g}", None, ((path, v),)) for v in (lo, mid, hi)]
            rows = run(labels, seeds, pool, args.workers)
            by = {}
            for label, opp, seed, seat, mine, _ in rows:
                by.setdefault(label, {})[(opp, seed, seat)] = mine
            keys = list(next(iter(by.values())))
            # Label order, not dict-insertion order: rows come back in whatever
            # order the worker pool finishes them, which printed "14 vs 6".
            names = [label for label, _ref, _ov in labels]
            print(f"  {path}")
            for a, b in ((0, 1), (1, 2), (0, 2)):
                d = sum(1 for k in keys if abs(by[names[a]][k] - by[names[b]][k]) > 1e-9)
                flag = "   <- NO EFFECT, narrow the bounds" if d == 0 else ""
                print(f"    {names[a]:>8} vs {names[b]:>8}: {d}/{len(keys)} games differ{flag}")
        return

    if args.agent:
        import benchmark_pool as _bp
        agent = _bp._get_agent(args.agent)
    else:
        import main as agent
    defaults = []
    for path, _lo, _hi, _ai in SPACE:
        name, _, key = path.partition(".")
        value = getattr(agent, name)
        if key:
            value = value[type(next(iter(value)))(key)]
        defaults.append(float(value))

    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    history = [h for h in state.get("history", []) if "win_rate" in h and "fitness" in h]

    if args.validate or args.promote:
        if not history:
            sys.exit("no usable history; run a search first")
        seeds = args.holdout if args.validate else HOLDOUT_SEEDS[12:24]
        stage = "stage-2 validation" if args.validate else "stage-3 promotion"
        best = max(history, key=lambda h: (h["win_rate"], h["fitness"]))
        vec = [float(best["overrides"][p]) for p, _l, _h, _a in SPACE]
        print(stage + ": seeds " + str(seeds))
        print("  " + str(len(args.pool) * len(seeds) * 2) + " games per candidate\n")
        out = {}
        for label, v in (("champion", defaults), ("candidate", vec)):
            r = evaluate_candidate(v, seeds, args.pool, args.workers)
            out[label] = r
            print("  %-10s win %5.1f%%  (%dW-%dL-%dT)  ours %8s  theirs %8s  med margin %+8s"
                  % (label, 100 * r["win_rate"], r["wins"], r["losses"], r["ties"],
                     format(r["ours"], ",.0f"), format(r["theirs"], ",.0f"),
                     format(r["median_margin"], ",.0f")))
            print("             by opponent " + str(r["win_rate_by_opponent"]))
        print("\n  candidate " + str(best["overrides"]))
        d = out["candidate"]["win_rate"] - out["champion"]["win_rate"]
        n = out["candidate"]["games"]
        se = math.sqrt(0.5 / n)
        print("\n  search win rate was %.1f%%; holdout %.1f%% vs champion %.1f%%  -> %+.1fpp"
              % (100 * best["win_rate"], 100 * out["candidate"]["win_rate"],
                 100 * out["champion"]["win_rate"], 100 * d))
        verdict = "inside noise" if abs(d) < 2 * se else "outside 2 SE"
        print("  standard error on that difference is about %.1fpp, so this is %s."
              % (100 * se, verdict))
        state["last_" + ("validation" if args.validate else "promotion")] = {
            "champion": out["champion"], "candidate": out["candidate"]}
        json.dump(state, open(STATE, "w", encoding="utf-8"), indent=1)
        return

    if args.objective == "replay":
        import bench_losses as _bl
        games = len(_bl.fitness_indices(args.submission, args.wins_per_eval, 0))
    else:
        games = len(args.pool) * args.seeds_per_eval * 2
    print("space:")
    for (path, lo, hi, _), d in zip(SPACE, defaults):
        print("  %-28s%8.2f   in [%s, %s]" % (path, d, lo, hi))
    print("\nbudget %d evaluations x %d games = %d games"
          % (args.budget, games, args.budget * games))
    if args.objective == "replay":
        print(f"objective: win rate over live episodes from {args.submission}, "
              f"replayed against the opponents' own recorded actions")
        print(f"  all 39 losses every evaluation, plus {args.wins_per_eval} of the "
              f"99 wins, rotating by generation")
        print("  a flip gained and a win given back count the same, which is the "
              "point: PASTURE_TILT scored +$2,945 a game and -7 wins")
    else:
        print("objective: win rate (ties 0.5); margin can only break exact ties")
    if args.objective != "replay":
        print("seeds rotate per generation from a bank of %d; holdout %d-%d never searched"
              % (len(SEED_BANK), HOLDOUT_SEEDS[0], HOLDOUT_SEEDS[-1]))
    se = math.sqrt(0.25 / games)
    print("standard error per evaluation ~%.1fpp; with %d candidates expect the best"
          % (100 * se, args.budget))
    print("to look ~%.0fpp better than it is, so the search output is a shortlist."
          % (100 * 2.2 * se))
    print("Stage 2 (--validate) and stage 3 (--promote) decide.\n")

    generations = []
    scale = np.array([(hi - lo) for _, lo, hi, _ in SPACE], dtype=float)
    lo_v = np.array([lo for _, lo, _, _ in SPACE], dtype=float)
    x0 = (np.array(defaults) - lo_v) / scale

    def evaluate(xn, gen):
        vec = lo_v + np.clip(xn, 0.0, 1.0) * scale
        if args.objective == "replay":
            r = evaluate_candidate_replay(vec, gen, args.agent, args.submission,
                                          args.wins_per_eval, args.workers)
        else:
            seeds = generation_seeds(gen, args.seeds_per_eval)
            r = evaluate_candidate(vec, seeds, args.pool, args.workers)
        r["generation"] = gen
        history.append(r)
        json.dump({"history": history, "generations": generations},
                  open(STATE, "w", encoding="utf-8"), indent=1)
        return r["fitness"]

    def log(gen, used, offspring, best, sigma, xmean):
        rows = sorted([h for h in history if h.get("generation") == gen],
                      key=lambda h: -h["fitness"])
        generations.append({
            "generation": gen, "evals_used": used, "sigma": float(sigma),
            "mean": dict(to_overrides(lo_v + np.clip(xmean, 0, 1) * scale)),
            "best_fitness": float(best[0]),
            "gen_best_win_rate": rows[0]["win_rate"] if rows else None,
            "gen_median_win_rate": (statistics.median(h["win_rate"] for h in rows)
                                    if rows else None),
            "seeds": rows[0]["seeds"] if rows else [],
        })
        # The replay objective has no seeds -- it plays fixed recorded episodes --
        # so name the sample it did use instead of indexing an empty list.
        seeds = rows[0]["seeds"] if rows else []
        sample = (f"seeds {seeds[0]}-{seeds[-1]}" if seeds
                  else f"{rows[0]['games']} live episodes" if rows else "no games")
        print("gen %2d  evals %3d/%d  sigma %.3f  %s"
              % (gen, used, args.budget, sigma, sample), flush=True)
        for h in rows[:2]:
            extra = ("  flips %+d/-%d" % (h["flipped"], h["given_back"])
                     if "flipped" in h else "")
            print("       win %5.1f%%  (%dW-%dL)  med margin %+8s%s  %s"
                  % (100 * h["win_rate"], h["wins"], h["losses"],
                     format(h["median_margin"], ",.0f"), extra, h["overrides"]),
                  flush=True)

    lam = 4 + int(3 * math.log(len(SPACE)))
    if args.budget < lam:
        sys.exit(f"--budget {args.budget} is below the population size {lam} for "
                 f"{len(SPACE)} dimensions, so no generation can complete. "
                 f"Use --budget {lam} or more (a multiple of {lam} is tidiest).")

    random.seed(0)
    np.random.seed(0)
    cma_es(x0, 0.30, args.budget, evaluate, log)

    if not history:
        sys.exit("no evaluations completed")
    best = max(history, key=lambda h: (h["win_rate"], h["fitness"]))
    print("\nsearch shortlist leader: win %.1f%%  %s"
          % (100 * best["win_rate"], best["overrides"]))
    json.dump({"history": history, "generations": generations},
              open(STATE, "w", encoding="utf-8"), indent=1)
    print("\nThis is a shortlist, not a result. Run --validate, then --promote.")


if __name__ == "__main__":
    main()
