import argparse
import contextlib
import io
import subprocess
import types


VERSIONS = {
    "v3": "c17addc:main.py",
    # Recovered Git object written immediately before Unlabeled v4 was submitted.
    "v4": "21a5707143e805d838a1a0f8d096365de26aa8cd",
    "v5": "383db66fc9d982f489753ac9864ec69613102442",
    "current": "main.py",
}

OPPONENT_MODES = ("RANK1", "THREE_PREMIUM", "BALANCED_PROXY", "CROP_RUSH")


def load_module(name, source_ref):
    if source_ref.endswith(".py") and ":" not in source_ref:
        with open(source_ref, encoding="utf-8") as source_file:
            source = source_file.read()
    else:
        source = subprocess.check_output(
            ["git", "show", source_ref], text=True, encoding="utf-8"
        )
    module = types.ModuleType(name)
    exec(compile(source, source_ref, "exec"), module.__dict__)
    return module


def make_env(seed):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        from kaggle_environments import make

        return make(
            "kaggriculture",
            configuration={"seed": seed, "episodeSteps": 720},
            debug=False,
        )


def forced_agent(module, mode):
    def play(obs):
        return module.run_strategy(obs, forced_mode=mode)

    return play


def run_match(ours, opponent, seed, seat):
    env = make_env(seed)
    agents = [ours, opponent] if seat == 0 else [opponent, ours]
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        env.run(agents)
    final = env.steps[-1]
    mine = final[seat].reward or 0
    theirs = final[1 - seat].reward or 0
    return mine, theirs


def benchmark(version_names, seeds):
    # Keep replay-derived opponent modes outside the submitted agent. The v5
    # snapshot contains those modes; current main.py intentionally does not.
    opponent_strategy = load_module("opponent_strategy", VERSIONS["v5"])
    rows = []

    for version_name in version_names:
        candidate = load_module(f"candidate_{version_name}", VERSIONS[version_name])
        for mode in OPPONENT_MODES:
            wins = 0
            margins = []
            rewards = []
            opponent = forced_agent(opponent_strategy, mode)
            for seed in seeds:
                for seat in (0, 1):
                    mine, theirs = run_match(candidate.agent, opponent, seed, seat)
                    wins += mine > theirs
                    margins.append(mine - theirs)
                    rewards.append(mine)
            games = len(margins)
            row = {
                "version": version_name,
                "opponent": mode,
                "games": games,
                "wins": wins,
                "win_rate": 100.0 * wins / games,
                "avg_reward": sum(rewards) / games,
                "avg_margin": sum(margins) / games,
            }
            rows.append(row)
            print(
                f"version={version_name:7} opponent={mode:14} "
                f"wins={wins}/{games} rate={row['win_rate']:5.1f}% "
                f"reward={row['avg_reward']:8.1f} margin={row['avg_margin']:8.1f}"
            )

        selected = [row for row in rows if row["version"] == version_name]
        games = sum(row["games"] for row in selected)
        wins = sum(row["wins"] for row in selected)
        weighted_reward = sum(row["avg_reward"] * row["games"] for row in selected) / games
        weighted_margin = sum(row["avg_margin"] * row["games"] for row in selected) / games
        print(
            f"TOTAL version={version_name:7} wins={wins}/{games} "
            f"rate={100.0 * wins / games:5.1f}% reward={weighted_reward:8.1f} "
            f"margin={weighted_margin:8.1f}\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--versions", nargs="+", default=list(VERSIONS))
    parser.add_argument("--seeds", type=int, default=3)
    args = parser.parse_args()
    benchmark(args.versions, range(args.seeds))
