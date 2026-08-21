"""Score a candidate against the agents that actually beat us, on the real games.

The pool in benchmark_pool.py is our own commit history plus the stock public
route. That was the right sparring partner in July; it is now roughly a third of
what we meet. Of 39 live losses, 31 are to a newer route generation that plants
12 melons on day 0, in two forks -- one cow-heavy, one sheep-heavy -- neither of
which is in the pool.

Every replay carries the opponent's full 720-step action stream, and these
agents are ~95% open-loop recordings, so their side can simply be played back.
This asks the only question a win-rate ladder cares about: would this change
have flipped a game I actually lost, and what would it have cost me elsewhere?

    python bench_losses.py 55563850 --all                 # working tree, full record
    python bench_losses.py 55563850 --all --ref agent_combined.py
    python bench_losses.py 55563850 --all --sweep LOOKAHEAD 3 4
    python bench_losses.py 55563850 --verify              # is the harness faithful?

USE --all. Sampling only the games we lost is biased: it can show a change
winning and can never show it giving a win back. PASTURE_TILT looked free on the
losses alone (+4 flips, +$1,404 a game, nothing given up) and cost seven wins
once the other 99 games were included.

DO NOT TUNE FRONT-RUNNING WITH THIS. MEASURED.

The first thing the optimiser found on this objective was LOOKAHEAD 5-7, worth
"+6 net wins". Against a live opponent that front-runs back it is a regression,
and the ordering is exactly inverted:

                     this benchmark        live stock route
    LOOKAHEAD 3        74.6%  baseline       93.8%  baseline
    LOOKAHEAD 5        79.0%  net +6 wins    90.6%  -3.1pp
    LOOKAHEAD 7        78.3%  net +5 wins    81.2%  -12.5pp

A frozen opponent cannot race us down the price ladder, so out-preempting one
is free here and costly in a real game. The optimiser did not find a better
agent, it found this evaluator's blind spot -- which is what search does to any
proxy. optimise_constants.py refuses to tune anything in REACTIVE_PARAMS on the
replay objective for this reason.

Any parameter governing how we behave RELATIVE to the opponent -- sale timing,
preemption, market racing -- belongs to benchmark_pool.py, not here. This
benchmark is trustworthy for changes to what we GROW, BUILD or OWN, where the
opponent's reaction is not the mechanism.

WHAT THIS IS NOT

The played-back opponent does not react. Their farm plan is a recording so that
costs little, but their sale timing is adaptive -- V14 front-runs its own
schedule -- and a frozen opponent cannot front-run back. So this flatters
changes that would provoke a response. Treat it as the primary screen, then
confirm survivors against the live pool.

Nor is it the same game twice: weed spawning draws from the same RNG stream as
the town's shop unlocks, so once our actions differ the shop draw can differ
too. --verify measures that directly by replaying our own recorded actions; it
reproduces the recorded final money exactly in 39 of 39, and the submitted agent
replays to 0 flips and +$0, so the floor is clean.
"""
import argparse
import collections
import csv
import glob
import gzip
import io
import json
import os
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)
DATA = os.path.join(PROJECT, "kaggle_episode_data")
OURS = "Harshith revuru"


# ---------------------------------------------------------------- case cache
# A replay is 31 MB and the part we need -- seed, seats, both action streams,
# final money -- is 0.24 MB of it. Re-parsing the full set costs ~56 seconds of
# JSON per evaluation and 4.3 GB of reads, which is most of the cost of a run
# and all of it waste. Extract once, then evaluations are pure simulation.

def cache_path(submission):
    return os.path.join(DATA, f"replay_cache_{submission}.json.gz")


def build_cache(submission):
    folder = os.path.join(DATA, "replays", str(submission))
    paths = sorted(glob.glob(os.path.join(folder, "*.json")))
    if not paths:
        raise SystemExit(f"no replays in {folder}")
    cases = []
    for i, path in enumerate(paths, 1):
        d = json.load(io.open(path, encoding="utf-8"))
        names = d["info"]["TeamNames"]
        if OURS not in names:
            continue
        us = names.index(OURS)
        steps = d["steps"]
        acts = [[None] * len(steps) for _ in (0, 1)]
        for s in range(1, len(steps)):
            for p in (0, 1):
                acts[p][s - 1] = steps[s][p].get("action")
        cases.append({
            "episode": os.path.splitext(os.path.basename(path))[0],
            "seed": d["info"]["seed"], "seat": us,
            "ours": acts[us], "theirs": acts[1 - us],
            "rec_mine": d["rewards"][us], "rec_theirs": d["rewards"][1 - us],
            "opponent": names[1 - us],
            "was_loss": d["rewards"][us] < d["rewards"][1 - us],
        })
        if i % 20 == 0:
            print(f"  cached {i}/{len(paths)}", flush=True)
    out = cache_path(submission)
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        json.dump(cases, fh)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB, {len(cases)} games)")
    return cases


def load_cases(submission, rebuild=False):
    path = cache_path(submission)
    if rebuild or not os.path.exists(path):
        return build_cache(submission)
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


_WORKER_CASES = {}


def _worker_cases(submission):
    """Loaded once per worker process, not once per game."""
    if submission not in _WORKER_CASES:
        _WORKER_CASES[submission] = load_cases(submission)
    return _WORKER_CASES[submission]


# ---------------------------------------------------------------- one game

def _job(args):
    label, cand_ref, override, submission, index, verify = args
    import benchmark_pool as BP
    from replay_ledger import playback
    from kaggle_environments import make

    case = _worker_cases(submission)[index]

    if verify:
        mine_agent = playback(case["ours"])
    else:
        module = BP._get_agent(cand_ref)
        BP._restore(module, BP._pristine_state[cand_ref])
        if override:
            pairs = override if isinstance(override[0], (tuple, list)) else [override]
            for name, value in pairs:
                BP.apply_override(module, name, value)
        mine_agent = module.agent

    theirs_agent = playback(case["theirs"])
    seat = case["seat"]
    agents = [mine_agent, theirs_agent] if seat == 0 else [theirs_agent, mine_agent]

    env = make("kaggriculture", configuration={"seed": case["seed"]}, debug=False)
    env.run(agents)
    farms = env.steps[-1][0].observation["farms"]
    return {
        "label": label, "episode": case["episode"], "opponent": case["opponent"],
        "seat": seat, "mine": farms[seat].get("money"),
        "theirs": farms[1 - seat].get("money"),
        "rec_mine": case["rec_mine"], "rec_theirs": case["rec_theirs"],
        "was_loss": case["was_loss"],
    }


def play(label, cand_ref, override, submission, indices, workers=10,
         verify=False, progress=True):
    jobs = [(label, cand_ref, override, submission, i, verify) for i in indices]
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for n, r in enumerate(ex.map(_job, jobs), 1):
            rows.append(r)
            if progress and (n % 25 == 0 or n == len(jobs)):
                print(f"  {n}/{len(jobs)} games", flush=True)
    return rows


# ---------------------------------------------------------------- fitness

def evaluate(cand_ref=None, overrides=None, submission="55563850",
             indices=None, workers=10, progress=False):
    """Net record over replayed live episodes, shaped for an optimiser.

    Fitness is WINS, because the ladder pays for wins: a change worth $2,945 a
    game and minus seven wins is a loss. Money is reported but only ever breaks
    an exact tie in the win count.
    """
    cases = load_cases(submission)
    if indices is None:
        indices = range(len(cases))
    indices = list(indices)
    rows = play("fitness", cand_ref, overrides, submission, indices,
                workers=workers, progress=progress)

    wins = sum(1 for r in rows if r["mine"] > r["theirs"])
    ties = sum(1 for r in rows if r["mine"] == r["theirs"])
    n = len(rows)
    flipped = sum(1 for r in rows if r["was_loss"] and r["mine"] > r["theirs"])
    given = sum(1 for r in rows if not r["was_loss"] and r["mine"] <= r["theirs"])
    money = statistics.mean(r["mine"] - r["rec_mine"] for r in rows) if rows else 0.0
    win_rate = (wins + 0.5 * ties) / max(1, n)
    return {
        "fitness": win_rate + 1e-9 * money,   # money cannot outweigh one game
        "win_rate": win_rate, "games": n, "wins": wins, "ties": ties,
        "flipped": flipped, "given_back": given, "money_per_game": money,
        "episodes": [r["episode"] for r in rows],
    }


def fitness_indices(submission, wins_per_eval=30, generation=0):
    """All losses every time, plus a rotating slice of the wins.

    Losses are where flips come from and there are only 39, so they are cheap to
    keep whole. The 99 wins are where a change gives something back, and 101 of
    138 episodes did not move at all under an aggressive perturbation, so paying
    for every win on every candidate is mostly waste. Rotating the slice keeps
    the search from fitting one fixed subset, the same reason the seed bank in
    optimise_constants.py rotates.

    Within a generation every candidate sees the SAME episodes, so comparisons
    stay paired; across generations they differ, so fitness is not comparable
    between generations. Validate on the full set.
    """
    cases = load_cases(submission)
    losses = [i for i, c in enumerate(cases) if c["was_loss"]]
    wins = [i for i, c in enumerate(cases) if not c["was_loss"]]
    if wins_per_eval >= len(wins):
        return losses + wins
    start = (generation * wins_per_eval) % len(wins)
    slice_ = [wins[(start + k) % len(wins)] for k in range(wins_per_eval)]
    return losses + slice_


# ---------------------------------------------------------------- reporting

def report(rows, label, baseline=None):
    rows = [r for r in rows if r["label"] == label]
    won = [r for r in rows if r["mine"] > r["theirs"]]
    was_loss = [r for r in rows if r["was_loss"]]
    was_win = [r for r in rows if not r["was_loss"]]
    flipped = [r for r in was_loss if r["mine"] > r["theirs"]]
    dropped = [r for r in was_win if r["mine"] <= r["theirs"]]
    gained = statistics.mean(r["mine"] - r["rec_mine"] for r in rows) if rows else 0

    print(f"\n{label}")
    print(f"  record {len(won)}W-{len(rows) - len(won)}L of {len(rows)} replayed"
          f"   ({100 * len(won) / max(1, len(rows)):.1f}%)")
    print(f"  lost games flipped:   {len(flipped)} of {len(was_loss)}")
    if was_win:
        print(f"  won games given back: {len(dropped)} of {len(was_win)}")
    print(f"  our score vs the recorded game: {gained:+,.0f} a game")
    for title, group in (("flipped", flipped), ("GIVEN BACK", dropped)):
        if group:
            print(f"  {title}:")
            for r in sorted(group, key=lambda r: r["theirs"] - r["mine"])[:12]:
                was = r["rec_mine"] - r["rec_theirs"]
                now = r["mine"] - r["theirs"]
                print(f"    {r['opponent'][:24]:<26} was {was:>+9,.0f}  now {now:>+9,.0f}")
            if len(group) > 12:
                print(f"    ... and {len(group) - 12} more")
    if baseline is not None:
        base_won = {r["episode"] for r in baseline if r["mine"] > r["theirs"]}
        now_won = {r["episode"] for r in won}
        print(f"  VERSUS CONTROL: {len(now_won - base_won)} gained, "
              f"{len(base_won - now_won)} lost, "
              f"net {len(now_won) - len(base_won):+d} wins")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("submission")
    ap.add_argument("--ref", default=None, help="candidate file or git revision")
    ap.add_argument("--sweep", nargs="+", default=None, metavar=("CONSTANT", "VALUE"))
    ap.add_argument("--verify", action="store_true",
                    help="replay OUR recorded actions too; should reproduce exactly")
    ap.add_argument("--all", action="store_true",
                    help="replay every game, not just the losses -- needed to see "
                         "wins a change gives back")
    ap.add_argument("--rebuild-cache", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    cases = load_cases(args.submission, rebuild=args.rebuild_cache)
    indices = [i for i, c in enumerate(cases) if args.all or c["was_loss"]]
    n_loss = sum(1 for i in indices if cases[i]["was_loss"])
    print(f"{len(indices)} games from {args.submission} ({n_loss} of them losses)")

    if args.verify:
        labels = [("verify (our own recorded actions)", None, None)]
    elif args.sweep:
        name, raw = args.sweep[0], args.sweep[1:]
        labels = [(f"{name}={v}", args.ref, (name, eval(v))) for v in raw]
    else:
        labels = [(args.ref or "working tree", args.ref, None)]

    rows = []
    for label, ref, ov in labels:
        rows += play(label, ref, ov, args.submission, indices,
                     workers=args.workers, verify=args.verify)

    if args.verify:
        rec = [r for r in rows if r["mine"] < r["theirs"]]
        exact = [r for r in rows if round(r["mine"]) == round(r["rec_mine"])]
        print(f"\nHARNESS CHECK across {len(rows)} games")
        print(f"  still a loss in {len(rec)} of {len(rows)}")
        print(f"  final money reproduces exactly in {len(exact)} of {len(rows)}")
    else:
        base = None
        for i, (label, _r, _o) in enumerate(labels):
            got = report(rows, label, baseline=base)
            if i == 0:
                base = got

    if args.csv:
        with io.open(args.csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["label", "episode", "opponent", "seat", "mine", "theirs",
                        "rec_mine", "rec_theirs", "was_loss", "won"])
            for r in rows:
                w.writerow([r["label"], r["episode"], r["opponent"], r["seat"],
                            r["mine"], r["theirs"], r["rec_mine"], r["rec_theirs"],
                            int(r["was_loss"]), int(r["mine"] > r["theirs"])])
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()
