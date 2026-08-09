import argparse
import contextlib
import csv
import io
import json
from pathlib import Path

from benchmark_versions import VERSIONS, load_module


DATA_DIR = Path("kaggle_episode_data")
LATEST_SUBMISSION = "55368998"


def replay_agent(actions):
    def play(obs):
        # Replay step zero is the initialized PASS state. The action shown on
        # the following state is the response originally made to this step.
        index = min(int(obs.get("step", 0)) + 1, len(actions) - 1)
        return actions[index]

    return play


def make_env(replay):
    configuration = dict(replay["configuration"])
    configuration["seed"] = replay.get("info", {}).get("seed")
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        from kaggle_environments import make

        return make("kaggriculture", configuration=configuration, debug=False)


def run_agents(replay, agents):
    env = make_env(replay)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        env.run(agents)
    return [state.reward or 0 for state in env.steps[-1]]


def load_episodes(outcome):
    with (DATA_DIR / "episode_results.csv").open(newline="", encoding="utf-8") as source:
        rows = [
            row
            for row in csv.DictReader(source)
            if row["submission_id"] == LATEST_SUBMISSION and row["outcome"] == outcome
        ]
    return sorted(rows, key=lambda row: abs(float(row["margin"])))


def benchmark(version_name, outcome="LOSS", verify=False, limit=None):
    candidate = load_module(f"candidate_{version_name}", VERSIONS[version_name])
    wins = 0
    margins = []
    reproduced = 0

    rows = load_episodes(outcome)
    if limit is not None:
        rows = rows[:limit]
    for row in rows:
        episode_id = row["episode_id"]
        path = DATA_DIR / "replays" / LATEST_SUBMISSION / f"episode-{episode_id}-replay.json"
        with path.open(encoding="utf-8") as source:
            replay = json.load(source)

        seat = int(row["seat"])
        opponent_seat = 1 - seat
        opponent_actions = [step[opponent_seat].get("action") for step in replay["steps"]]
        agents = [None, None]
        agents[seat] = candidate.agent
        agents[opponent_seat] = replay_agent(opponent_actions)
        rewards = run_agents(replay, agents)
        margin = rewards[seat] - rewards[opponent_seat]
        wins += margin > 0
        margins.append(margin)

        if verify:
            original_agents = []
            for player in (0, 1):
                actions = [step[player].get("action") for step in replay["steps"]]
                original_agents.append(replay_agent(actions))
            replayed = run_agents(replay, original_agents)
            expected = [replay["rewards"][0], replay["rewards"][1]]
            reproduced += all(abs(a - b) < 0.01 for a, b in zip(replayed, expected))

        print(
            f"episode={episode_id} opponent={row['opponent']!r} "
            f"mine={rewards[seat]:.0f} opp={rewards[opponent_seat]:.0f} margin={margin:.0f} "
            f"outcome={'WIN' if margin > 0 else 'LOSS'}"
        )

    games = len(margins)
    print(
        f"TOTAL version={version_name} flipped={wins}/{games} "
        f"rate={100.0 * wins / max(1, games):.1f}% avg_margin={sum(margins) / max(1, games):.1f}"
    )
    if verify:
        print(f"reproduction_exact={reproduced}/{games}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("version", choices=VERSIONS)
    parser.add_argument("--outcome", choices=("WIN", "LOSS"), default="LOSS")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    benchmark(args.version, outcome=args.outcome, verify=args.verify, limit=args.limit)
