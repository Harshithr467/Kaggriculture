"""A/B a candidate against a POOL of structurally different opponents, in parallel.

Every earlier measurement here was self-play -- our agent against our own recent
commit -- so both sides hit the market on the same schedule and the opponent's
supply was perfectly correlated with ours. Measured 2026-08-14, that is not a
small distortion: BACKFILL_CROP="WHEAT" scored 11/24 and -1,424 against HEAD and
24/24 and +23,068 against c34629c, on identical seeds. A sign flip, not a wobble.

So this plays each candidate against several genuinely different builds and
reports per opponent as well as pooled.

    python benchmark_pool.py                              # working tree vs default pool
    python benchmark_pool.py --seeds 0 1 2 3 4 5 6 7
    python benchmark_pool.py --sweep BACKFILL_CROP '"CARROT"' '"WHEAT"'
    python benchmark_pool.py --pool HEAD c34629c --workers 4

TWO NUMBERS, NOT ONE. Win rate and our own score can move in opposite
directions: wheat backfill lifted the win rate against c34629c while lowering
our absolute score from 77,226 to 71,618, because it hurt an opponent leaning on
the wheat market more than it helped us. The reward in this competition is the
final bank balance, but the ranking is win-based (ELO live, Bradley-Terry
after), so both matter and a divergence between them is a finding, not a
rounding error. The report flags it.
"""
import argparse
import contextlib
import io
import os
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

# Structurally different on purpose: c34629c predates the travel-divisor fix and
# runs a herd cap of 17, a49c8d3 predates the animal-cap flattening, f454950 is
# what was live through mid-August. Similar strength, different builds.
DEFAULT_POOL = ["HEAD", "a49c8d3", "f454950", "c34629c"]

_agents = {}          # per-process cache: ref -> module


def _load_from_git(ref):
    """Like benchmark_ab.load_agent_from_git, but safe to call from many processes.

    That one writes to a fixed temp path per ref, so two workers loading the same
    revision race: one truncates the file while the other is importing it, and
    the half-executed module comes back without an `agent` attribute. The pid in
    the filename keeps each process to its own copy.
    """
    import importlib.util
    import subprocess
    import tempfile
    source = subprocess.run(
        ["git", "show", f"{ref}:main.py"],
        cwd=PROJECT, capture_output=True, text=True, check=True,
    ).stdout
    safe = ref.replace("/", "_")
    path = os.path.join(tempfile.gettempdir(), f"pool_{safe}_{os.getpid()}.py")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(source)
    spec = importlib.util.spec_from_file_location(f"pool_{safe}_{os.getpid()}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "agent"):
        raise SystemExit(f"revision {ref} has no agent() entry point")
    return module


def _get_agent(ref):
    """Cache by revision ONLY, never by (revision, override).

    `import main` hands back the one module object, so caching a module under
    (ref, override) would leave several cache entries pointing at the same
    object and every candidate would silently run with whichever override was
    applied last. Overrides are therefore re-applied per game, below.
    """
    if ref in _agents:
        return _agents[ref]
    if ref is None:
        import main as module
    else:
        module = _load_from_git(ref)
    _agents[ref] = module
    return module


def _run_one(job):
    label, cand_ref, override, opp_ref, seed, seat = job
    from benchmark_ab import play
    cand = _get_agent(cand_ref)
    if override:
        name, value = override
        if not hasattr(cand, name):
            raise SystemExit(f"{cand_ref or 'working tree'} has no constant {name!r}")
        setattr(cand, name, value)
    opp = _get_agent(opp_ref)
    if opp is cand:
        raise SystemExit(
            f"candidate and opponent resolve to the same module ({opp_ref}); "
            "the override would apply to both. Use a different --ref."
        )
    mine, theirs = play(cand.agent, opp.agent, seed, seat)
    return label, opp_ref, seed, seat, mine, theirs


def run(labels, seeds, pool, workers):
    """labels: list of (label, cand_ref, override). Returns rows."""
    jobs = [
        (label, ref, override, opp, seed, seat)
        for (label, ref, override) in labels
        for opp in pool
        for seed in seeds
        for seat in (0, 1)
    ]
    rows = []
    done = 0
    quiet = io.StringIO()
    with ProcessPoolExecutor(max_workers=workers) as pool_exec:
        futures = [pool_exec.submit(_run_one, j) for j in jobs]
        for fut in as_completed(futures):
            with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
                rows.append(fut.result())
            done += 1
            if done % 10 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)} games", flush=True)
    return rows


def summarise(rows, labels, pool, control):
    by = {}
    for label, opp, _seed, _seat, mine, theirs in rows:
        b = by.setdefault((label, opp), {"w": 0, "n": 0, "mine": [], "theirs": []})
        b["n"] += 1
        b["w"] += mine > theirs
        b["mine"].append(mine)
        b["theirs"].append(theirs)

    print()
    print(f"{'candidate':<22}{'opponent':<12}{'wins':>9}{'our score':>12}"
          f"{'their score':>13}{'margin':>11}")
    print("-" * 79)
    pooled = {}
    for label, _ref, _ov in labels:
        agg = {"w": 0, "n": 0, "mine": [], "theirs": []}
        for opp in pool:
            b = by.get((label, opp))
            if not b:
                continue
            m, t = statistics.mean(b["mine"]), statistics.mean(b["theirs"])
            print(f"{label:<22}{opp:<12}{b['w']}/{b['n']:<7}{m:>12,.0f}{t:>13,.0f}"
                  f"{m - t:>+11,.0f}")
            for k in ("w", "n"):
                agg[k] += b[k]
            agg["mine"] += b["mine"]
            agg["theirs"] += b["theirs"]
        m, t = statistics.mean(agg["mine"]), statistics.mean(agg["theirs"])
        pooled[label] = {"w": agg["w"], "n": agg["n"], "mine": m, "theirs": t}
        print(f"{label:<22}{'POOLED':<12}{agg['w']}/{agg['n']:<7}{m:>12,.0f}"
              f"{t:>13,.0f}{m - t:>+11,.0f}")
        print()

    if control is None or control not in pooled:
        return
    base = pooled[control]
    print(f"versus control {control!r}:")
    print(f"  {'candidate':<22}{'win rate':>11}{'d win rate':>12}"
          f"{'our score':>12}{'d our score':>13}")
    for label in pooled:
        p = pooled[label]
        wr, bwr = 100 * p["w"] / p["n"], 100 * base["w"] / base["n"]
        print(f"  {label:<22}{wr:>10.1f}%{wr - bwr:>+11.1f}{p['mine']:>12,.0f}"
              f"{p['mine'] - base['mine']:>+13,.0f}")
        if label != control and (wr - bwr) * (p["mine"] - base["mine"]) < 0:
            print(f"  {'':<22}^^ win rate and our own score DISAGREE -- this change "
                  f"trades money for wins or the reverse; decide deliberately.")
    n = base["n"]
    if n < 20:
        print(f"\nNOTE: {n} games per candidate is too few to trust. Use 8+ seeds.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[0, 1, 2, 3, 4, 5, 6, 7])
    ap.add_argument("--pool", nargs="*", default=DEFAULT_POOL)
    ap.add_argument("--sweep", nargs="+", default=None,
                    metavar=("CONSTANT", "VALUE"),
                    help="constant name followed by values (python literals)")
    ap.add_argument("--ref", default=None,
                    help="candidate git revision; default is the working tree")
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 4))
    args = ap.parse_args()

    if args.sweep:
        name, raw_values = args.sweep[0], args.sweep[1:]
        if not raw_values:
            raise SystemExit("--sweep needs at least one value after the constant name")
        labels = [(f"{name}={v}", args.ref, (name, eval(v))) for v in raw_values]
        control = labels[0][0]
    else:
        labels = [("working tree" if args.ref is None else args.ref, args.ref, None)]
        control = None

    print(f"pool {args.pool}   seeds {args.seeds}   "
          f"{len(labels)} candidate(s)   {args.workers} workers")
    print(f"{len(labels) * len(args.pool) * len(args.seeds) * 2} games total")
    rows = run(labels, args.seeds, args.pool, args.workers)
    summarise(rows, labels, args.pool, control)


if __name__ == "__main__":
    main()
