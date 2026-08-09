import json
import sys
from collections import Counter


def farm_counts(farm):
    counts = Counter()
    empty = 0
    for row in farm["tiles"]:
        for tile in row:
            if tile is None:
                empty += 1
            elif isinstance(tile, dict):
                if tile.get("kind") == "PLANT":
                    counts[tile.get("crop")] += 1
                elif tile.get("animal"):
                    counts[tile.get("animal")] += 1
                elif tile.get("kind") in {"PASTURE", "COOP", "WEED"}:
                    counts[tile.get("kind")] += 1
    return counts, empty


def summarize(path):
    with open(path, encoding="utf-8") as handle:
        replay = json.load(handle)

    episode = replay["info"]["EpisodeId"]
    names = [agent["Name"] for agent in replay["info"]["Agents"]]
    print(f"\nepisode={episode} rewards={replay['rewards']} names={names}")
    for player, name in enumerate(names):
        operations = Counter()
        market = Counter()
        land_days = []
        previous_land = 1
        peaks = Counter()
        final = None
        daily = {}

        for states in replay["steps"]:
            state = states[player]
            action = state.get("action") or {}
            for unit_action in [action.get("farmer", [])] + list(action.get("hands", [])):
                if unit_action:
                    operations[unit_action[0]] += 1
            for order in action.get("market", []):
                if not order:
                    continue
                item = order[1] if len(order) > 1 else ""
                amount = order[2] if len(order) > 2 else 1
                market[(order[0], item)] += amount

            obs = state.get("observation") or {}
            if not obs or obs.get("hour") != 23:
                continue
            farm = obs["farms"][player]
            counts, empty = farm_counts(farm)
            land = len(farm.get("unlocked_quadrants", []))
            if land > previous_land:
                land_days.extend([obs["day"]] * (land - previous_land))
                previous_land = land
            for item, count in counts.items():
                peaks[item] = max(peaks[item], count)
            daily[obs["day"]] = {
                "money": int(farm["money"]),
                "land": land,
                "hands": len(farm.get("hands", [])),
                "empty": empty,
                "counts": counts,
                "prices": obs["market"]["prices"],
            }
            final = daily[obs["day"]]

        movement = sum(operations[action] for action in ("NORTH", "SOUTH", "EAST", "WEST"))
        productive = sum(operations.values()) - movement - operations["PASS"]
        sales = {
            item: market[("SELL", item)]
            for item in ("WHEAT", "STRAWBERRY", "MELON", "MILK", "WOOL", "FERTILIZER")
        }
        buys = {
            item: market[("BUY_SEED", item)]
            for item in ("WHEAT", "STRAWBERRY", "MELON")
        }
        print(
            f"p{player} {name!r} reward={replay['rewards'][player]:.0f} land_days={land_days} "
            f"peak={dict(peaks)} movement={movement} productive={productive} pass={operations['PASS']} "
            f"hires={market[('HIRE', '')]} drops={operations['DROP']}"
        )
        print(f"  buys={buys} sales={sales}")
        if final:
            print(
                f"  final money={final['money']} land={final['land']} hands={final['hands']} "
                f"empty={final['empty']} farm={dict(final['counts'])}"
            )
        checkpoints = []
        for day in (0, 4, 7, 10, 14, 18, 22, 26, 29):
            row = daily.get(day)
            if row:
                checkpoints.append(
                    f"d{day}:{row['money']}/{row['land']}L/{row['hands']}H/{row['empty']}E/"
                    f"M{row['prices'].get('MELON')}/S{row['prices'].get('STRAWBERRY')}/"
                    f"Mi{row['prices'].get('MILK')}/W{row['prices'].get('WOOL')}"
                )
        print("  timeline " + " | ".join(checkpoints))


if __name__ == "__main__":
    for replay_path in sys.argv[1:]:
        summarize(replay_path)
