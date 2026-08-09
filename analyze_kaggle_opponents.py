import csv
import json
import statistics
from collections import Counter
from pathlib import Path

from analyze_replay_set import CHECK_DAYS, farm_snapshot


SUBMISSION_ID = "55368998"
TEAM_NAME = "Harshith revuru"
DATA_DIR = Path("kaggle_episode_data")
REPLAY_DIR = DATA_DIR / "replays" / SUBMISSION_ID


def participant_metrics(replay, player):
    actions = Counter()
    market = Counter()
    peaks = Counter()
    snapshots = {}
    land_days = []
    previous_land = 1
    max_hands = 0

    for states in replay["steps"]:
        state = states[player]
        action = state.get("action") or {}
        for unit_action in [action.get("farmer", [])] + list(action.get("hands", [])):
            if unit_action:
                actions[unit_action[0]] += 1
        for order in action.get("market", []):
            if order:
                item = order[1] if len(order) > 1 else ""
                amount = order[2] if len(order) > 2 else 1
                market[(order[0], item)] += amount

        obs = state.get("observation") or {}
        if not obs:
            continue
        farm = obs["farms"][player]
        land = len(farm.get("unlocked_quadrants", []))
        if land > previous_land:
            land_days.extend([obs.get("day", 0)] * (land - previous_land))
            previous_land = land
        max_hands = max(max_hands, len(farm.get("hands", [])))
        empty, weeds, counts = farm_snapshot(farm)
        for item in ("WHEAT", "MELON", "STRAWBERRY", "TOMATO", "COW", "SHEEP"):
            peaks[item] = max(peaks[item], counts[item])
        if obs.get("hour") == 23 and obs.get("day") in CHECK_DAYS:
            snapshots[obs["day"]] = (empty, weeds, counts)

    movement = sum(actions[action] for action in ("NORTH", "SOUTH", "EAST", "WEST"))
    productive = sum(actions.values()) - movement - actions["PASS"]
    return {
        "movement": movement,
        "productive": productive,
        "move_per_productive": movement / max(1, productive),
        "plant": actions["PLANT"],
        "water": actions["WATER"],
        "harvest": actions["HARVEST"],
        "pickup": actions["PICKUP"],
        "drop": actions["DROP"],
        "max_hands": max_hands,
        "final_land": previous_land,
        "land_days": "/".join(map(str, land_days)),
        "peak_wheat": peaks["WHEAT"],
        "peak_melon": peaks["MELON"],
        "peak_strawberry": peaks["STRAWBERRY"],
        "peak_tomato": peaks["TOMATO"],
        "peak_cow": peaks["COW"],
        "peak_sheep": peaks["SHEEP"],
        "sold_melon": market[("SELL", "MELON")],
        "sold_strawberry": market[("SELL", "STRAWBERRY")],
        "sold_milk": market[("SELL", "MILK")],
        "sold_wool": market[("SELL", "WOOL")],
        "d12_empty": snapshots.get(12, (0, 0, Counter()))[0],
        "d18_empty": snapshots.get(18, (0, 0, Counter()))[0],
    }


def average(rows, field):
    return statistics.mean(float(row[field]) for row in rows) if rows else 0.0


def strategy_label(metrics):
    if metrics["final_land"] == 1 and metrics["peak_melon"] >= 15:
        return "ONE_LAND_MELON"
    if metrics["peak_strawberry"] >= 35 and metrics["peak_cow"] + metrics["peak_sheep"] >= 10:
        return "PREMIUM_BALANCED"
    if metrics["peak_strawberry"] >= 35:
        return "STRAWBERRY_RUSH"
    if metrics["peak_cow"] + metrics["peak_sheep"] >= 15:
        return "ANIMAL_HEAVY"
    return "OTHER"


def main():
    with (DATA_DIR / "episode_results.csv").open(newline="", encoding="utf-8") as handle:
        results = {
            row["episode_id"]: row
            for row in csv.DictReader(handle)
            if row["submission_id"] == SUBMISSION_ID
        }

    rows = []
    for episode_id, result in results.items():
        path = REPLAY_DIR / f"episode-{episode_id}-replay.json"
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as handle:
            replay = json.load(handle)
        names = [agent["Name"] for agent in replay["info"]["Agents"]]
        mine = names.index(TEAM_NAME)
        opponent = 1 - mine
        metrics = participant_metrics(replay, opponent)
        metrics.update(
            {
                "episode_id": episode_id,
                "outcome": result["outcome"],
                "opponent": names[opponent],
                "opponent_reward": int(float(result["opponent_reward"])),
            }
        )
        metrics["strategy"] = strategy_label(metrics)
        rows.append(metrics)

    fields = [
        "opponent_reward", "movement", "productive", "move_per_productive", "plant", "water", "harvest",
        "pickup", "drop", "max_hands", "final_land", "peak_wheat", "peak_melon", "peak_strawberry",
        "peak_tomato", "peak_cow", "peak_sheep", "sold_melon", "sold_strawberry", "sold_milk", "sold_wool",
        "d12_empty", "d18_empty",
    ]
    for outcome in ("WIN", "LOSS"):
        selected = [row for row in rows if row["outcome"] == outcome]
        print(f"\nOPPONENTS_WHEN_WE_{outcome} count={len(selected)}")
        for field in fields:
            print(f"  {field}={average(selected, field):.2f}")
        print("  strategies=" + str(Counter(row["strategy"] for row in selected)))

    print("\nLOSS_OPPONENT_DETAILS")
    for row in sorted((row for row in rows if row["outcome"] == "LOSS"), key=lambda item: -item["opponent_reward"]):
        print(
            f"  episode={row['episode_id']} name={row['opponent']!r} reward={row['opponent_reward']} "
            f"strategy={row['strategy']} land={row['final_land']} days={row['land_days']} hands={row['max_hands']} "
            f"straw={row['peak_strawberry']} melon={row['peak_melon']} cow={row['peak_cow']} sheep={row['peak_sheep']} "
            f"movement={row['movement']} ratio={row['move_per_productive']:.2f} d12_empty={row['d12_empty']}"
        )


if __name__ == "__main__":
    main()
