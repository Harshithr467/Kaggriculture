"""Play our agent against one named opponent out of any replay.

Matchmaking pairs you near your own rating, so we have never met a top-10 agent
and have no idea how we do against one. A replay carries their full 720-step
action stream, so they can be played back and fought.

    python spar.py C:/path/95942616.json --opponent "Ryo Hasegawa"
    python spar.py ... --sweep CARROT_SWAP "()" "((629,9),...)"

WHAT THIS CAN AND CANNOT TELL YOU

It is ONE seed. A recording is a strategy plus the exact game it was recorded
in: replayed on another seed its plantings land on different tiles and its
purchases hit different prices, which is why a lifted route scored 6/16 when its
own episode had it winning. So this is faithful on the replay's own seed and
nowhere else -- a single sharp data point, not a distribution. Do not read a
sweep here as a tuning result; read it as "what happened in this one game".

The town is pinned to the recorded draw, so variants meet the same economy.
"""
import argparse
import collections
import io
import json
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(path, opponent):
    d = json.load(io.open(path, encoding="utf-8"))
    names = d["info"]["TeamNames"]
    if opponent not in names:
        raise SystemExit(f"{opponent!r} not in {names}")
    them = names.index(opponent)
    steps = d["steps"]
    acts = [steps[i][them].get("action") for i in range(1, len(steps))]
    shops = list((steps[-1][0]["observation"].get("town") or {})
                 .get("unlocked_shops") or [])
    return {
        "seed": d["info"]["seed"], "actions": acts, "shops": shops,
        "their_score": d["rewards"][them],
        "other_score": d["rewards"][1 - them],
        "other_name": names[1 - them],
        # Seat matters: the market resolves player 0 first on each unit.
        "their_seat": them,
    }


def run_one(case, ref, override, workers=None):
    import benchmark_pool as BP
    import bench_losses as BL
    from replay_ledger import playback
    from kaggle_environments import make

    module = BP._get_agent(ref)
    BP._restore(module, BP._pristine_state[ref])
    if override:
        for name, value in override:
            BP.apply_override(module, name, value)

    theirs = playback(case["actions"])
    seat = 1 - case["their_seat"]
    agents = [module.agent, theirs] if seat == 0 else [theirs, module.agent]

    pinned = BL._pin_town(case["shops"]) if case["shops"] else None
    try:
        env = make("kaggriculture", configuration={"seed": case["seed"]}, debug=False)
        env.run(agents)
    finally:
        if pinned is not None:
            BL._unpin_town(pinned)
    farms = env.steps[-1][0].observation["farms"]
    return farms[seat].get("money"), farms[1 - seat].get("money")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--ref", default="agent_combined.py")
    ap.add_argument("--sweep", nargs="+", default=None, metavar=("CONSTANT", "VALUE"))
    args = ap.parse_args()

    case = load(args.replay, args.opponent)
    print(f"{args.opponent} scored {case['their_score']:,.0f} in this episode, "
          f"beating {case['other_name']} on {case['other_score']:,.0f}")
    print(f"seed {case['seed']}, town pinned to {len(case['shops'])} recorded shops")
    print(f"town: {dict(collections.Counter(case['shops']))}\n")

    if args.sweep:
        name, raw = args.sweep[0], args.sweep[1:]
        labels = [(f"{name}={v}", ((name, eval(v)),)) for v in raw]
    else:
        labels = [(args.ref, None)]

    print(f"{'candidate':<44}{'us':>11}{'them':>11}{'margin':>11}  result")
    for label, ov in labels:
        mine, theirs = run_one(case, args.ref, ov)
        verdict = "WIN " if mine > theirs else "loss"
        print(f"{label[:43]:<44}{mine:>11,.0f}{theirs:>11,.0f}"
              f"{mine - theirs:>+11,.0f}  {verdict}")


if __name__ == "__main__":
    main()
