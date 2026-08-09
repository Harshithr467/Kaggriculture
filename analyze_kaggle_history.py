import csv
from collections import Counter
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi


SUBMISSIONS = {
    55357136: "Trial 1",
    55359246: "Better version",
    55361835: "Market-aware route v3",
    55364717: "Unlabeled v4",
    55367754: "Unlabeled v5",
    55368998: "Rank1 hybrid ripple v1",
}

OUTPUT = Path("kaggle_episode_data") / "episode_results.csv"


def outcome(my_reward, opponent_reward):
    if my_reward > opponent_reward:
        return "WIN"
    if my_reward < opponent_reward:
        return "LOSS"
    return "TIE"


def main():
    api = KaggleApi()
    api.authenticate()
    rows = []

    for submission_id, description in SUBMISSIONS.items():
        for episode in api.competition_list_episodes(submission_id):
            if str(episode.type).split(".")[-1] != "EPISODE_TYPE_PUBLIC":
                continue
            agents = list(episode.agents or [])
            mine = next((agent for agent in agents if agent.submission_id == submission_id), None)
            opponent = next((agent for agent in agents if agent.submission_id != submission_id), None)
            if mine is None or opponent is None:
                continue
            result = outcome(mine.reward, opponent.reward)
            rows.append(
                {
                    "submission_id": submission_id,
                    "description": description,
                    "episode_id": episode.id,
                    "create_time": episode.create_time.isoformat(),
                    "seat": mine.index,
                    "reward": mine.reward,
                    "opponent": opponent.team_name,
                    "opponent_submission_id": opponent.submission_id,
                    "opponent_reward": opponent.reward,
                    "margin": mine.reward - opponent.reward,
                    "outcome": result,
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (row["submission_id"], row["episode_id"])))

    print(f"saved={OUTPUT} episodes={len(rows)}")
    for submission_id, description in SUBMISSIONS.items():
        selected = [row for row in rows if row["submission_id"] == submission_id]
        counts = Counter(row["outcome"] for row in selected)
        decided = counts["WIN"] + counts["LOSS"]
        win_rate = 100.0 * counts["WIN"] / decided if decided else 0.0
        average = sum(row["reward"] for row in selected) / len(selected) if selected else 0.0
        print(
            f"submission={submission_id} label={description!r} episodes={len(selected)} "
            f"wins={counts['WIN']} losses={counts['LOSS']} ties={counts['TIE']} "
            f"win_rate={win_rate:.1f}% avg_reward={average:.1f}"
        )

    counts = Counter(row["outcome"] for row in rows)
    decided = counts["WIN"] + counts["LOSS"]
    print(
        f"overall episodes={len(rows)} wins={counts['WIN']} losses={counts['LOSS']} ties={counts['TIE']} "
        f"win_rate={100.0 * counts['WIN'] / decided:.1f}%"
    )

    latest_id = max(SUBMISSIONS)
    losses = [row for row in rows if row["submission_id"] == latest_id and row["outcome"] == "LOSS"]
    print("latest_losses=" + ",".join(str(row["episode_id"]) for row in losses))


if __name__ == "__main__":
    main()
