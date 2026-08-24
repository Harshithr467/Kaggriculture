"""How correlated are two candidate submissions?

Only two submissions stay active, so if both are the same design a meta shift
that beats one beats both. That is the concentration risk Rayk Kretzschmar names
directly: "two near-identical active submits -- meta shift kills both --
diversify the second slot."

But diversification is only worth paying for if the alternative is comparably
strong AND actually decorrelated. This measures the second half: each candidate
plays the SAME opponents on the SAME seeds, and we compare their win/loss
vectors game by game.

    python diversity.py --candidates agent_combined.py "agent_combined.py:CARROT_PRICE_GATE=None#no gate" \
        --opponents kernels/rayk_c95.py kernels/agent_mimi.py --seeds 9200-9209

Agreement near 100% means the second slot buys nothing: it wins and loses the
same games. What you want from a hedge is a candidate that loses games the
incumbent wins and wins games the incumbent loses -- disagreement -- while
staying close to it on overall win rate.
"""
import argparse
import collections
import itertools
import os
import sys
from concurrent.futures import ProcessPoolExecutor

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ladder import parse_entrant, parse_seeds, _load


def _job(args):
    (lc, pc, oc), (lo, po, oo), seed, seat = args
    import fixed_town
    from kaggle_environments import make

    fixed_town.enable()
    cand, opp = _load(lc, pc, oc), _load(lo, po, oo)
    pair = [cand, opp] if seat == 0 else [opp, cand]
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(pair)
    farms = env.steps[-1][0].observation["farms"]
    mine = farms[seat].get("money")
    theirs = farms[1 - seat].get("money")
    return {"cand": lc, "key": (lo, seed, seat),
            "win": mine > theirs, "margin": mine - theirs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", nargs="+", required=True)
    ap.add_argument("--opponents", nargs="+", required=True)
    ap.add_argument("--seeds", default="9200-9209")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    cands = [parse_entrant(t) for t in args.candidates]
    opps = [parse_entrant(t) for t in args.opponents]
    seeds = parse_seeds(args.seeds)

    jobs = [(c, o, s, seat)
            for c in cands for o in opps for s in seeds for seat in (0, 1)]
    print(f"{len(cands)} candidates x {len(opps)} opponents x {len(seeds)} seeds "
          f"x 2 seats = {len(jobs)} games\n")

    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for n, r in enumerate(ex.map(_job, jobs), 1):
            rows.append(r)
            if n % 20 == 0 or n == len(jobs):
                print(f"  {n}/{len(jobs)} games", flush=True)

    by = collections.defaultdict(dict)
    for r in rows:
        by[r["cand"]][r["key"]] = r["win"]

    print(f"\n{'candidate':<44}{'W-L':>10}{'win%':>8}")
    for label, _, _ in cands:
        v = by[label]
        w = sum(v.values())
        print(f"{label[:43]:<44}{w:>5}-{len(v) - w:<4}{100 * w / max(1, len(v)):>7.1f}%")

    print("\npairwise agreement (share of games with the SAME outcome)")
    print("lower is more diversified; ~100% means the second slot buys nothing\n")
    for (la, _, _), (lb, _, _) in itertools.combinations(cands, 2):
        a, b = by[la], by[lb]
        keys = sorted(set(a) & set(b))
        if not keys:
            continue
        same = sum(1 for k in keys if a[k] == b[k])
        a_only = sum(1 for k in keys if a[k] and not b[k])
        b_only = sum(1 for k in keys if b[k] and not a[k])
        print(f"  {la[:30]:<32} vs {lb[:30]:<32}")
        print(f"    agree {100 * same / len(keys):>5.1f}%   "
              f"{la[:18]}-only wins {a_only:>3}   {lb[:18]}-only wins {b_only:>3}")


if __name__ == "__main__":
    main()
