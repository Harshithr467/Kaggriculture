"""Head-to-head A/B: working-tree main.py against the committed baseline.

This is the only measurement in this project worth trusting. Scores against the
`random` opponent are noise, and single games are noise: per-game variance is
roughly +/-4,000 even between identical-strength agents, and the episode seed is
not fully pinned by `configuration.seed`. Both seats are played for every seed
so seat advantage cancels.

    python benchmark_ab.py 0 1 2 3 4
    python benchmark_ab.py 5 6 7 8 9 10 11        # unseen seeds
    python benchmark_ab.py --ref c34629c 0 1 2    # against an older commit

Require at least 20 games across 8+ seeds, on seeds not used for tuning, before
believing a result. A 720-turn game takes 1-2 minutes, so a 24-game run is
roughly 30-45 minutes -- start it in the background.
"""
import argparse
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

_quiet = io.StringIO()
with contextlib.redirect_stdout(_quiet), contextlib.redirect_stderr(_quiet):
    from kaggle_environments import make


def load_agent_from_git(ref):
    """Import an agent from a git revision without disturbing the working tree."""
    source = subprocess.run(
        ["git", "show", f"{ref}:main.py"],
        cwd=PROJECT, capture_output=True, text=True, check=True,
    ).stdout
    path = os.path.join(tempfile.gettempdir(), f"baseline_{ref.replace('/', '_')}.py")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(source)
    spec = importlib.util.spec_from_file_location(f"baseline_{abs(hash(ref))}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def play(agent_a, agent_b, seed, seat):
    """Return (a_reward, b_reward) with agent_a seated at `seat`."""
    agents = [agent_a, agent_b] if seat == 0 else [agent_b, agent_a]
    with contextlib.redirect_stdout(_quiet), contextlib.redirect_stderr(_quiet):
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run(agents)
    rewards = [s.reward for s in env.steps[-1]]
    return (rewards[0], rewards[1]) if seat == 0 else (rewards[1], rewards[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("seeds", nargs="*", type=int, default=[0, 1, 2, 3, 4])
    parser.add_argument("--ref", default="HEAD", help="git revision to use as the baseline")
    args = parser.parse_args()
    seeds = args.seeds or [0, 1, 2, 3, 4]

    baseline = load_agent_from_git(args.ref)
    import main as current

    print(f"current (working tree) vs {args.ref}   seeds {seeds}")
    print(f"{'seed':>5}{'seat':>6}{'current':>11}{'baseline':>11}{'margin':>11}  result")
    wins = current_total = baseline_total = games = 0
    for seed in seeds:
        for seat in (0, 1):
            mine, theirs = play(current.agent, baseline.agent, seed, seat)
            current_total += mine
            baseline_total += theirs
            games += 1
            won = mine > theirs
            wins += won
            print(f"{seed:>5}{seat:>6}{mine:>11,.0f}{theirs:>11,.0f}{mine-theirs:>+11,.0f}"
                  f"  {'WIN' if won else 'loss'}", flush=True)

    print()
    print(f"current wins {wins}/{games}  ({100*wins/games:.0f}%)")
    print(f"avg current {current_total/games:,.0f}   avg baseline {baseline_total/games:,.0f}   "
          f"avg margin {(current_total-baseline_total)/games:+,.0f}")
    if games < 20:
        print(f"NOTE: only {games} games -- too few to trust. Use 8+ seeds.")


if __name__ == "__main__":
    main()
