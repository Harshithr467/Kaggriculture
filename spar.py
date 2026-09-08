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

--dir builds a POOL, which is the honest version of this. Kaggle publishes every
episode daily, so a 60-episode sample of one day held 16 teams inside the top 60
-- opponents matchmaking will never show us, across many seeds and many town
draws. One replay is one opponent on one seed in ONE TOWN, and the town decides
which build looks good in it: the first rank-1 replay analysed here drew four
smoothie shops and no yarn store, which is exactly the town a 12-cow herd wants.

READ THE POOL RESULT WITH THE BLIND SPOT IN MIND

Against 55 matches with 21 top-60 agents the shipped agent goes 36W-19L, 65.5%,
mean margin +160. That is NOT a claim that we beat the top 60. Every opponent
here is frozen: their farm plan is a recording and replays faithfully, but their
market layer is adaptive and cannot fight back. These are the best agents in the
competition, and the adaptive market play is the most likely thing that makes
them best -- so this setting removes exactly the part we would lose to. The
mean margin of +160 over 55 games says these are knife-edge games even with
that advantage handed to us.

What it does support: our farm's PRODUCTION is competitive with the top of the
board. The rating gap is not a gap in what we grow.
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


def leaderboard():
    import csv, glob
    files = sorted(glob.glob(os.path.join(
        PROJECT, "kaggle_episode_data", "kaggriculture-publicleaderboard-*.csv")))
    if not files:
        return {}
    return {r["TeamName"]: (int(r["Rank"]), float(r["Score"]))
            for r in csv.DictReader(io.open(files[-1], encoding="utf-8-sig"))}


def build_pool(folder, max_rank):
    """Every replay in `folder` becomes a match against its best-ranked player.

    Kaggle publishes every episode daily, so a 60-episode sample of one day
    already contains 16 teams inside the top 60 -- opponents matchmaking will
    never show us, across many seeds and many town draws. That is the point: one
    replay is one opponent on one seed in one town, and the town it drew decides
    which build looks good in it.
    """
    import glob
    lb = leaderboard()
    cases = []
    for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        names = d.get("info", {}).get("TeamNames") or []
        ranked = sorted(((lb.get(n, (10 ** 9, 0))[0], i, n) for i, n in enumerate(names)))
        if not ranked or ranked[0][0] > max_rank:
            continue
        rank, them, name = ranked[0]
        steps = d["steps"]
        cases.append({
            "seed": d["info"]["seed"],
            "actions": [steps[i][them].get("action") for i in range(1, len(steps))],
            "shops": list((steps[-1][0]["observation"].get("town") or {})
                          .get("unlocked_shops") or []),
            "their_score": d["rewards"][them],
            "other_score": d["rewards"][1 - them],
            "other_name": names[1 - them],
            "their_seat": them,
            "name": name, "rank": rank,
        })
    return cases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("replay", nargs="?")
    ap.add_argument("--opponent")
    ap.add_argument("--dir", help="folder of replays to build a pool from")
    ap.add_argument("--max-rank", type=int, default=60)
    ap.add_argument("--ref", default="agent_combined.py")
    ap.add_argument("--sweep", nargs="+", default=None, metavar=("CONSTANT", "VALUE"))
    args = ap.parse_args()

    if args.dir:
        return run_pool(args)
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


def run_pool(args):
    cases = build_pool(args.dir, args.max_rank)
    if not cases:
        raise SystemExit(f"no replays in {args.dir} with a player ranked <= {args.max_rank}")
    names = collections.Counter(f"{c['name']} (#{c['rank']})" for c in cases)
    print(f"{len(cases)} matches against {len(names)} top-{args.max_rank} agents")
    print("  " + ", ".join(f"{k} x{v}" for k, v in names.most_common()) + "\n")

    if args.sweep:
        name, raw = args.sweep[0], args.sweep[1:]
        labels = [(f"{name}={v}", ((name, eval(v)),)) for v in raw]
    else:
        labels = [(args.ref, None)]

    base = None
    for label, ov in labels:
        wins, margins, per = 0, [], {}
        for c in cases:
            mine, theirs = run_one(c, args.ref, ov)
            wins += mine > theirs
            margins.append(mine - theirs)
            per.setdefault(c["name"], []).append(mine > theirs)
        mean = sum(margins) / len(margins)
        line = (f"{label[:40]:<42}{wins:>3}W-{len(cases) - wins:<3}L"
                f"  {100 * wins / len(cases):>5.1f}%   mean margin {mean:>+9,.0f}")
        if base is not None:
            line += f"   net {wins - base:+d} wins"
        else:
            base = wins
        print(line)
    return None


if __name__ == "__main__":
    main()
