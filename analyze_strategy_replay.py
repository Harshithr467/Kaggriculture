import json
import sys
from collections import Counter


def farm_counts(farm):
    counts = Counter()
    for row in farm["tiles"]:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT":
                counts[tile["crop"]] += 1
            elif tile.get("animal"):
                counts[tile["animal"]] += 1
            elif tile.get("kind") in {"COOP", "PASTURE", "WEED"}:
                counts[tile["kind"]] += 1
    return counts


def nonzero(values):
    return {key: value for key, value in values.items() if value}


def analyze(path):
    with open(path, encoding="utf-8") as handle:
        replay = json.load(handle)
    names = [agent["Name"] for agent in replay["info"]["Agents"]]
    print(f"episode={replay['info']['EpisodeId']} names={names} rewards={replay['rewards']}")

    for player, name in enumerate(names):
        market = Counter()
        unit_ops = Counter()
        daily = {}
        for step, states in enumerate(replay["steps"]):
            state = states[player]
            action = state.get("action") or {}
            for unit_action in [action.get("farmer", [])] + list(action.get("hands", [])):
                if unit_action:
                    unit_ops[unit_action[0]] += 1
            for order in action.get("market", []):
                if not order:
                    continue
                item = order[1] if len(order) > 1 else ""
                amount = order[2] if len(order) > 2 else 1
                market[(order[0], item)] += amount

            obs = state.get("observation") or {}
            if obs.get("hour") != 23:
                continue
            farm = obs["farms"][player]
            private = obs.get("private", {})
            daily[obs["day"]] = {
                "money": int(farm["money"]),
                "land": len(farm.get("unlocked_quadrants", [])),
                "hands": len(farm.get("hands", [])),
                "farm": nonzero(farm_counts(farm)),
                "shed": nonzero(private.get("shed", {})),
                "seeds": nonzero(private.get("seeds", {})),
                "carried": sum(sum(inv.values()) for inv in private.get("inventories", [])),
                "prices": obs["market"]["prices"],
                "empty": sum(tile is None for row in farm["tiles"] for tile in row),
            }

        print(f"\nplayer={player} name={name!r}")
        print("market totals:")
        for key, value in sorted(market.items()):
            print(f"  {key[0]} {key[1]} = {value}")
        movement = sum(unit_ops[op] for op in ("NORTH", "SOUTH", "EAST", "WEST"))
        productive = sum(unit_ops.values()) - movement - unit_ops["PASS"]
        print(f"unit totals: movement={movement} productive={productive} pass={unit_ops['PASS']} all={dict(unit_ops)}")
        print("daily snapshots:")
        for day in sorted(daily):
            if day <= 12 or day % 2 == 0 or day >= 27:
                row = daily[day]
                print(
                    f"  d{day:02d} money={row['money']:6d} land={row['land']} hands={row['hands']:2d} "
                    f"empty={row['empty']:2d} farm={row['farm']} shed={row['shed']} seeds={row['seeds']} "
                    f"carried={row['carried']} prices={{'MELON': {row['prices'].get('MELON')}, "
                    f"'STRAWBERRY': {row['prices'].get('STRAWBERRY')}, 'MILK': {row['prices'].get('MILK')}, "
                    f"'WOOL': {row['prices'].get('WOOL')}}}"
                )


if __name__ == "__main__":
    analyze(sys.argv[1])
