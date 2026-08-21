"""Replay the games we actually lost, against the agents that actually beat us.

The pool in benchmark_pool.py is our own commit history plus the stock public
route. That was the right sparring partner in July; it is now roughly a third of
what we meet. Of 39 live losses, 31 are to a newer route generation that plants
12 melons on day 0, and it comes in two forks -- one cow-heavy, one sheep-heavy
-- neither of which is in the pool.

Every replay carries the opponent's full 720-step action stream, and these
agents are ~95% open-loop recordings, so their side of the game can simply be
played back. This asks the only question that matters on a win-rate ladder:
would this change have flipped a game I actually lost?

    python bench_losses.py 55563850                       # working tree
    python bench_losses.py 55563850 --ref agent_combined.py
    python bench_losses.py 55563850 --sweep LOOKAHEAD 3 4
    python bench_losses.py 55563850 --verify              # is the harness faithful?

WHAT THIS IS NOT

The played-back opponent does not react. Their farm plan is a recording so that
costs little, but their sale timing is adaptive -- V14 front-runs its own
schedule -- and a frozen opponent cannot front-run back. So this flatters
changes that would provoke a response, and a flip here is weaker evidence than a
flip against a live agent. Treat it as a screen, then confirm survivors against
the live pool.

Nor is it the same game twice. Weed spawning draws from the same RNG stream as
the town's shop unlocks, so once our actions differ the shop draw can differ
too. --verify measures exactly how much that costs: it replays our own recorded
actions and checks the result still reproduces.
"""
import argparse
import collections
import csv
import glob
import io
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)
OURS = "Harshith revuru"


def load_case(path):
    """(seed, our seat, our recorded actions, their recorded actions, scores)."""
    d = json.load(io.open(path, encoding="utf-8"))
    names = d["info"]["TeamNames"]
    if OURS not in names:
        return None
    us = names.index(OURS)
    steps = d["steps"]
    acts = [[None] * len(steps) for _ in (0, 1)]
    for i in range(1, len(steps)):
        for p in (0, 1):
            acts[p][i - 1] = steps[i][p].get("action")
    return {
        "episode": os.path.splitext(os.path.basename(path))[0],
        "seed": d["info"]["seed"],
        "seat": us,
        "ours": acts[us],
        "theirs": acts[1 - us],
        "recorded": (d["rewards"][us], d["rewards"][1 - us]),
        "opponent": names[1 - us],
    }


def _job(args):
    label, cand_ref, override, path, verify, was_loss = args
    import benchmark_pool as BP
    from replay_ledger import playback
    from kaggle_environments import make

    case = load_case(path)
    if case is None:
        return None

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
    final = env.steps[-1][0].observation["farms"]
    mine = final[seat].get("money")
    theirs = final[1 - seat].get("money")
    shops = tuple(sorted(env.steps[-1][0].observation["town"]["unlocked_shops"]))
    return {
        "label": label, "episode": case["episode"], "opponent": case["opponent"],
        "seat": seat, "mine": mine, "theirs": theirs,
        "rec_mine": case["recorded"][0], "rec_theirs": case["recorded"][1],
        "shops": shops, "was_loss": was_loss,
    }


def case_paths(folder, only_losses):
    """Losses only, or every game.

    Losses alone are a BIASED sample: they can only show a change winning and
    never show it giving a win back, which is precisely how PASTURE_TILT looked
    free here while costing ten wins in sixty-four against the stock route. Win
    rate needs both halves.
    """
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
        d = json.load(io.open(path, encoding="utf-8"))
        names = d["info"]["TeamNames"]
        if OURS not in names:
            continue
        us = names.index(OURS)
        lost = d["rewards"][us] < d["rewards"][1 - us]
        if lost or not only_losses:
            out.append((path, lost))
    return out


def report(rows, label, baseline=None):
    rows = [r for r in rows if r["label"] == label]
    won = [r for r in rows if r["mine"] > r["theirs"]]
    was_loss = [r for r in rows if r["was_loss"]]
    was_win = [r for r in rows if not r["was_loss"]]
    flipped = [r for r in was_loss if r["mine"] > r["theirs"]]
    dropped = [r for r in was_win if r["mine"] <= r["theirs"]]
    gained = sum(r["mine"] - r["rec_mine"] for r in rows) / max(1, len(rows))

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
    ap.add_argument("--sweep", nargs="+", default=None,
                    metavar=("CONSTANT", "VALUE"))
    ap.add_argument("--verify", action="store_true",
                    help="replay OUR recorded actions too; the result should "
                         "reproduce the recorded loss")
    ap.add_argument("--all", action="store_true",
                    help="replay every game, not just the losses -- needed to see "
                         "wins a change gives back")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    folder = os.path.join(PROJECT, "kaggle_episode_data", "replays", args.submission)
    cases = case_paths(folder, only_losses=not args.all)
    print(f"{len(cases)} games in {args.submission} "
          f"({sum(1 for _p, lost in cases if lost)} of them losses)")

    if args.verify:
        labels = [("verify (our own recorded actions)", None, None)]
    elif args.sweep:
        name, raw = args.sweep[0], args.sweep[1:]
        labels = [(f"{name}={v}", args.ref, (name, eval(v))) for v in raw]
    else:
        labels = [(args.ref or "working tree", args.ref, None)]

    jobs = [(label, ref, ov, p, args.verify, lost)
            for (label, ref, ov) in labels for p, lost in cases]
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(_job, jobs), 1):
            if r:
                rows.append(r)
            if i % 20 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)} games", flush=True)

    if args.verify:
        rec = [r for r in rows if r["mine"] < r["theirs"]]
        exact = [r for r in rows if round(r["mine"]) == round(r["rec_mine"])]
        print(f"\nHARNESS CHECK across {len(rows)} games")
        print(f"  still a loss in {len(rec)} of {len(rows)} "
              f"({100 * len(rec) / max(1, len(rows)):.0f}%)")
        print(f"  final money reproduces exactly in {len(exact)} of {len(rows)}")
        print("  A loss that does not reproduce is a game whose RNG stream moved;"
              " those cases are noise in every later run.")
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
                            int(r["mine"] > r["theirs"])])
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()
