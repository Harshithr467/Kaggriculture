"""Play our agent against a public notebook agent, live, both seats.

This is the honest complement to `spar.py`. There, opponents are recorded action
streams that cannot react; here both sides are real code, so the opponent's
market layer fights back. That is the part `spar.py` structurally cannot test
and the part the top agents are most likely to be winning on.

    python spar_live.py kernels/rayk_c95.py --seeds 901-912

Two caveats worth keeping in front of the result:

 -  a published notebook artifact is not necessarily the author's live
    submission. Several of these notebooks say so outright.
 -  the town is NOT pinned here, and both agents' actions perturb the RNG
    stream that draws it, so absolute banks are not comparable across
    opponents -- only the win column is.
"""
import argparse
import io
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_seeds(text):
    out = []
    for chunk in text.split(","):
        if "-" in chunk:
            lo, hi = chunk.split("-")
            out.extend(range(int(lo), int(hi) + 1))
        else:
            out.append(int(chunk))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("opponents", nargs="+")
    ap.add_argument("--ref", default="agent_combined.py")
    ap.add_argument("--seeds", default="901-906")
    args = ap.parse_args()

    import benchmark_pool as BP
    from kaggle_environments import make

    seeds = parse_seeds(args.seeds)
    print(f"{args.ref} vs {len(args.opponents)} opponent(s), "
          f"{len(seeds)} seeds x 2 seats\n")

    for path in args.opponents:
        wins, margins = 0, []
        for seed in seeds:
            for seat in (0, 1):
                us = BP._get_agent(args.ref)
                BP._restore(us, BP._pristine_state[args.ref])
                them = BP._get_agent(path)
                pair = [us.agent, them.agent] if seat == 0 else [them.agent, us.agent]
                env = make("kaggriculture", configuration={"seed": seed}, debug=False)
                env.run(pair)
                farms = env.steps[-1][0].observation["farms"]
                mine = farms[seat].get("money")
                theirs = farms[1 - seat].get("money")
                wins += mine > theirs
                margins.append(mine - theirs)
        games = len(margins)
        mean = sum(margins) / games
        worst = min(margins)
        print(f"{os.path.basename(path):<46}{wins:>3}W-{games - wins:<3}L"
              f"  {100 * wins / games:>5.1f}%   mean {mean:>+9,.0f}"
              f"   worst {worst:>+9,.0f}")


if __name__ == "__main__":
    main()
