import csv
import json
import statistics
from collections import Counter
from pathlib import Path


SUBMISSION_ID = "55368998"
TEAM_NAME = "Harshith revuru"
DATA_DIR = Path("kaggle_episode_data")
REPLAY_DIR = DATA_DIR / "replays" / SUBMISSION_ID
RESULTS_FILE = DATA_DIR / "episode_results.csv"
METRICS_FILE = DATA_DIR / f"replay_metrics_{SUBMISSION_ID}.csv"
CHECK_DAYS = (5, 8, 10, 12, 14, 18, 22, 26, 29)


def farm_snapshot(farm):
    counts = Counter()
    empty = 0
    weeds = 0
    for row in farm["tiles"]:
        for tile in row:
            if tile == "LOCKED":
                continue
            if tile is None:
                empty += 1
            elif tile.get("kind") == "WEED":
                weeds += 1
            elif tile.get("kind") == "PLANT":
                counts[tile["crop"]] += 1
            elif tile.get("animal"):
                counts[tile["animal"]] += 1
    return empty, weeds, counts


def replay_metrics(path, result):
    with path.open(encoding="utf-8") as handle:
        replay = json.load(handle)
    names = [agent["Name"] for agent in replay["info"]["Agents"]]
    player = names.index(TEAM_NAME)
    opponent = names[1 - player]
    actions = Counter()
    market = Counter()
    snapshots = {}
    land_days = []
    previous_land = 1
    crop_peaks = Counter()
    animal_peaks = Counter()
    max_hands = 0

    for states in replay["steps"]:
        state = states[player]
        action = state.get("action") or {}
        for unit_action in [action.get("farmer", [])] + list(action.get("hands", [])):
            if unit_action:
                actions[unit_action[0]] += 1
        for order in action.get("market", []):
            if not order:
                continue
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
        for crop in ("WHEAT", "MELON", "STRAWBERRY", "TOMATO"):
            crop_peaks[crop] = max(crop_peaks[crop], counts[crop])
        for animal in ("COW", "SHEEP"):
            animal_peaks[animal] = max(animal_peaks[animal], counts[animal])
        if obs.get("hour") == 23 and obs.get("day") in CHECK_DAYS:
            snapshots[obs["day"]] = (empty, weeds, counts)

    movement = sum(actions[action] for action in ("NORTH", "SOUTH", "EAST", "WEST"))
    productive = sum(actions.values()) - movement - actions["PASS"]
    row = {
        "episode_id": result["episode_id"],
        "outcome": result["outcome"],
        "seat": player,
        "opponent": opponent,
        "reward": int(float(result["reward"])),
        "opponent_reward": int(float(result["opponent_reward"])),
        "margin": int(float(result["margin"])),
        "movement": movement,
        "productive": productive,
        "move_per_productive": movement / max(1, productive),
        "pass": actions["PASS"],
        "plant": actions["PLANT"],
        "water": actions["WATER"],
        "harvest": actions["HARVEST"],
        "pickup": actions["PICKUP"],
        "drop": actions["DROP"],
        "dig": actions["DIG"],
        "max_hands": max_hands,
        "final_land": previous_land,
        "land_days": "/".join(map(str, land_days)),
        "peak_wheat": crop_peaks["WHEAT"],
        "peak_melon": crop_peaks["MELON"],
        "peak_strawberry": crop_peaks["STRAWBERRY"],
        "peak_tomato": crop_peaks["TOMATO"],
        "peak_cow": animal_peaks["COW"],
        "peak_sheep": animal_peaks["SHEEP"],
        "bought_land": market[("BUY_LAND", "")],
        "bought_wheat": market[("BUY_PRODUCT", "WHEAT")],
        "sold_melon": market[("SELL", "MELON")],
        "sold_strawberry": market[("SELL", "STRAWBERRY")],
        "sold_milk": market[("SELL", "MILK")],
        "sold_wool": market[("SELL", "WOOL")],
    }
    for day in CHECK_DAYS:
        empty, weeds, counts = snapshots.get(day, (0, 0, Counter()))
        row[f"d{day}_empty"] = empty
        row[f"d{day}_weeds"] = weeds
        row[f"d{day}_strawberry"] = counts["STRAWBERRY"]
        row[f"d{day}_melon"] = counts["MELON"]
    return row


def average(rows, field):
    return statistics.mean(float(row[field]) for row in rows) if rows else 0.0


def main():
    with RESULTS_FILE.open(newline="", encoding="utf-8") as handle:
        results = {
            row["episode_id"]: row
            for row in csv.DictReader(handle)
            if row["submission_id"] == SUBMISSION_ID
        }
    metrics = []
    for episode_id, result in results.items():
        path = REPLAY_DIR / f"episode-{episode_id}-replay.json"
        if path.exists():
            metrics.append(replay_metrics(path, result))

    with METRICS_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=metrics[0].keys())
        writer.writeheader()
        writer.writerows(sorted(metrics, key=lambda row: int(row["episode_id"])))

    print(f"saved={METRICS_FILE} replays={len(metrics)}")
    fields = [
        "reward", "movement", "productive", "move_per_productive", "pass", "plant", "water",
        "harvest", "pickup", "drop", "dig", "max_hands", "final_land", "peak_wheat", "peak_melon",
        "peak_strawberry", "peak_cow", "peak_sheep", "sold_melon", "sold_strawberry", "sold_milk",
        "sold_wool", "d8_empty", "d10_empty", "d12_empty", "d14_empty", "d18_empty", "d22_empty",
    ]
    for outcome in ("WIN", "LOSS"):
        selected = [row for row in metrics if row["outcome"] == outcome]
        print(f"\n{outcome} count={len(selected)}")
        for field in fields:
            print(f"  {field}={average(selected, field):.2f}")
        opponents = Counter(row["opponent"] for row in selected)
        print("  opponents=" + ", ".join(f"{name}:{count}" for name, count in opponents.most_common()))

    print("\nlosses_by_margin:")
    losses = sorted((row for row in metrics if row["outcome"] == "LOSS"), key=lambda row: row["margin"])
    for row in losses:
        print(
            f"  episode={row['episode_id']} opponent={row['opponent']!r} margin={row['margin']} "
            f"reward={row['reward']} movement={row['movement']} d12_empty={row['d12_empty']} "
            f"straw_peak={row['peak_strawberry']} land_days={row['land_days']}"
        )


if __name__ == "__main__":
    main()
