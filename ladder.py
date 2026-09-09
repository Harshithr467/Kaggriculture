"""Rank agents by playing them against each other, live, on seeds they have not seen.

WHY THIS EXISTS

bench_losses.py replays recorded opponent tapes on their own recorded seeds. It
detects breakage reliably, but it cannot rank comparable agents: MiMi's lifted
route scored 233W-127L there against our 209W-151L -- a convincing +24 wins --
and then lost to that same agent 8-32 on twenty held-out seeds. Not noisy, the
wrong sign. Fixed tapes cannot react, so what that benchmark rewards is a bigger
absolute bank against a frozen field, which is a different quantity from win
probability against a live one.

This plays real code against real code, both seats, and fits Bradley-Terry to
the head-to-head results rather than to coin margins -- because the ladder pays
for wins and a 140k bank that loses still loses rating.

    python ladder.py --pool agent_combined.py kernels/rayk_c95.py --seeds 9000-9009
    python ladder.py --pool "agent_combined.py:CARROT_PRICE_GATE=None" agent_combined.py
    python ladder.py --challenger kernels/agent_mimi.py --pool agent_combined.py

An entrant is a file path, optionally with overrides and a label:

    path                                 the file as it is
    path:NAME=VALUE,NAME=VALUE           the file with constants overridden
    path:NAME=VALUE#label                a readable name for the result table

THE RULES THIS HARNESS EXISTS TO ENFORCE

 -  Both seats, always. The market resolves player 0 first on each unit, so a
    one-seat test can reverse the apparent winner.
 -  Decide on seeds the candidate has never been screened on. Three seeds is not
    a screen, it is a coin flip you get to keep flipping -- MiMi went 6/6 on the
    seeds it was picked with.
 -  The incumbent is a VETO opponent. A candidate that wins the pool overall but
    loses to the agent it would replace has not earned the slot.
 -  The town is drawn from its own RNG stream (fixed_town), so a seed names one
    town regardless of how the agents behave. Without it, changing an agent
    changes which shops open and the two entrants play different economies.
"""
import argparse
import collections
import itertools
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- entrants

def parse_entrant(text):
    """`path[:NAME=VALUE,...][#label]` -> (label, path, ((name, value), ...))."""
    label = None
    if "#" in text:
        # Split on the FIRST '#', not the last: a label legitimately contains
        # one (e.g. "Mengfei Li #5 (2920)") while a path does not. rsplit here
        # silently produced a path of "kernels/opp.py#Mengfei Li" and a
        # spec_from_file_location of None, surfacing only as an
        # AttributeError on spec.loader inside a worker.
        text, label = text.split("#", 1)
    path, _, overrides = text.partition(":")
    pairs = []
    if overrides:
        for chunk in overrides.split(","):
            name, _, raw = chunk.partition("=")
            pairs.append((name.strip(), eval(raw.strip())))
    if label is None:
        label = os.path.basename(path)
        if pairs:
            label += " " + ",".join(f"{n}={v!r}" for n, v in pairs)
    return label, path, tuple(pairs)


def parse_seeds(text):
    out = []
    for chunk in text.split(","):
        if "-" in chunk:
            lo, hi = chunk.split("-")
            out.extend(range(int(lo), int(hi) + 1))
        else:
            out.append(int(chunk))
    return out


# ---------------------------------------------------------------- one game

_LOADED = {}


def _load(label, path, overrides):
    """One module object per ENTRANT, not per file.

    benchmark_pool caches a module per path, which is fatal here: two entrants
    that differ only by an override share a file, so building the second
    rebinds the constants the first is already holding. Every variant matchup
    then plays itself -- the symptom is an exact 0 mean margin and identical
    records across variants. Load the source into its own module namespace.
    """
    import importlib.util

    if label in _LOADED:
        return _LOADED[label]
    spec = importlib.util.spec_from_file_location(
        f"ladder_entrant_{abs(hash(label)):x}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, value in overrides:
        if not hasattr(module, name):
            raise SystemExit(f"{path} has no constant {name!r}")
        setattr(module, name, value)
    _LOADED[label] = module.agent
    return module.agent


def _job(args):
    (la, pa, oa), (lb, pb, ob), seed, seat = args
    import fixed_town
    from kaggle_environments import make

    fixed_town.enable()
    a, b = _load(la, pa, oa), _load(lb, pb, ob)
    pair = [a, b] if seat == 0 else [b, a]
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(pair)
    farms = env.steps[-1][0].observation["farms"]
    status = [str(s.status) for s in env.steps[-1]]
    return {
        "a": la, "b": lb, "seed": seed, "seat": seat,
        "abank": farms[seat].get("money"),
        "bbank": farms[1 - seat].get("money"),
        "ok": status == ["DONE", "DONE"], "status": status,
    }


# ---------------------------------------------------------------- ranking

def bradley_terry(wins, games, iters=500):
    """MM iteration for Bradley-Terry strengths, reported on a 400-point scale."""
    names = sorted(games)
    p = {n: 1.0 for n in names}
    for _ in range(iters):
        new = {}
        for i in names:
            denom = 0.0
            for j in names:
                n = games[i].get(j, 0)
                if n and (p[i] + p[j]) > 0:
                    denom += n / (p[i] + p[j])
            w = wins[i]
            new[i] = (w / denom) if denom > 0 and w > 0 else p[i] * 1e-6
        scale = sum(new.values()) / len(new)
        p = {n: max(v / scale, 1e-9) for n, v in new.items()}
    mean = sum(math.log10(v) for v in p.values()) / len(p)
    return {n: 1500 + 400 * (math.log10(v) - mean) for n, v in p.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", nargs="+", required=True)
    ap.add_argument("--challenger",
                    help="play this against every pool entrant instead of a full round robin")
    ap.add_argument("--seeds", default="9000-9009")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--veto", help="label that must not beat the challenger")
    args = ap.parse_args()

    pool = [parse_entrant(t) for t in args.pool]
    seeds = parse_seeds(args.seeds)
    if args.challenger:
        ch = parse_entrant(args.challenger)
        pairings = [(ch, e) for e in pool if e[0] != ch[0]]
        entrants = [ch] + [e for e in pool if e[0] != ch[0]]
    else:
        pairings = list(itertools.combinations(pool, 2))
        entrants = pool

    jobs = [(a, b, seed, seat)
            for a, b in pairings for seed in seeds for seat in (0, 1)]
    print(f"{len(entrants)} entrants, {len(pairings)} pairings, "
          f"{len(seeds)} seeds x 2 seats = {len(jobs)} games\n")
    for label, path, ov in entrants:
        print(f"  {label:<44} {path}")
    print()

    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for n, r in enumerate(ex.map(_job, jobs), 1):
            rows.append(r)
            if n % 20 == 0 or n == len(jobs):
                print(f"  {n}/{len(jobs)} games", flush=True)

    bad = [r for r in rows if not r["ok"]]
    if bad:
        print(f"\n!! {len(bad)} games did not finish DONE/DONE, "
              f"e.g. {bad[0]['a']} vs {bad[0]['b']} seed {bad[0]['seed']}: {bad[0]['status']}")

    wins = collections.Counter()
    games = collections.defaultdict(collections.Counter)
    head = collections.defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        a, b = r["a"], r["b"]
        games[a][b] += 1
        games[b][a] += 1
        margin = r["abank"] - r["bbank"]
        if margin > 0:
            wins[a] += 1
            head[(a, b)][0] += 1
        elif margin < 0:
            wins[b] += 1
            head[(a, b)][1] += 1
        else:
            wins[a] += 0.5
            wins[b] += 0.5
        head[(a, b)][2] += margin

    for label, _, _ in entrants:
        games.setdefault(label, collections.Counter())
        wins.setdefault(label, 0)

    bt = bradley_terry(wins, games)
    total = {n: sum(games[n].values()) for n in games}

    print("\n" + "=" * 74)
    print(f"{'agent':<44}{'W-L':>12}{'win%':>7}{'BT':>9}")
    degenerate = []
    for label in sorted(bt, key=lambda n: -bt[n]):
        n = total.get(label, 0)
        w = wins.get(label, 0)
        pct = 100 * w / n if n else 0
        mark = ""
        if n and (w == 0 or w == n):
            degenerate.append(label)
            mark = " *"
        print(f"{label[:43]:<44}{w:>6.0f}-{n - w:<5.0f}{pct:>6.1f}%{bt[label]:>9.0f}{mark}")
    if degenerate:
        # With no losses (or no wins) the likelihood has no interior maximum, so
        # the MM iteration walks off to infinity. The ORDER is still right; the
        # number is not a distance.
        print("\n  * undefeated or winless: its BT value is unbounded, "
              "read the order not the gap")

    print("\nhead to head (row beats column)")
    for (a, b), (wa, wb, margin) in sorted(head.items()):
        n = wa + wb
        print(f"  {a[:32]:<34}{wa:>3}-{wb:<3} vs {b[:28]:<30}"
              f"  mean {margin / max(1, n):>+9,.0f}")

    if args.veto:
        ch = entrants[0][0]
        for (a, b), (wa, wb, _) in head.items():
            pair = {a: wa, b: wb}
            if args.veto in pair and ch in pair and pair[args.veto] >= pair[ch]:
                print(f"\nVETO: {args.veto} is not beaten by {ch} "
                      f"({pair[ch]}-{pair[args.veto]}). Do not promote.")
                return
        print(f"\nveto clear: {ch} beats {args.veto}")


if __name__ == "__main__":
    main()
