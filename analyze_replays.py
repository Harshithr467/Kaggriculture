import glob
import json
from collections import Counter


def tile_counts(farm):
    counts = Counter()
    for row in farm["tiles"]:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT":
                counts[tile["crop"]] += 1
            elif tile.get("animal"):
                counts[tile["animal"]] += 1
    return counts


def analyze(path):
    with open(path, encoding="utf-8") as handle:
        replay = json.load(handle)

    names = [agent.get("Name", f"player-{i}") for i, agent in enumerate(replay["info"]["Agents"])]
    print(f"\nepisode={replay['id']} rewards={replay['rewards']} names={names}")
    for player, name in enumerate(names):
        peak = Counter()
        orders = Counter()
        actions = Counter()
        land_days = {}
        max_money = 0
        final_money = 0
        for states in replay["steps"]:
            state = states[player]
            obs = state.get("observation") or {}
            farms = obs.get("farms") or []
            if len(farms) > player:
                farm = farms[player]
                final_money = farm.get("money", final_money)
                max_money = max(max_money, final_money)
                day = obs.get("day", 0)
                for quadrant in farm.get("unlocked_quadrants", []):
                    land_days.setdefault(quadrant, day)
                current = tile_counts(farm)
                for item, count in current.items():
                    peak[item] = max(peak[item], count)

            action = state.get("action") or {}
            for unit_action in [action.get("farmer", [])] + list(action.get("hands", [])):
                if unit_action:
                    actions[unit_action[0]] += 1
            for order in action.get("market", []):
                if not order:
                    continue
                key = order[0] if len(order) == 1 else f"{order[0]}:{order[1]}"
                amount = order[2] if len(order) >= 3 and isinstance(order[2], (int, float)) else 1
                orders[key] += amount

        useful_orders = {k: v for k, v in orders.items() if k.startswith(("BUY_SEED", "BUY_ANIMAL", "BUY_LAND"))}
        print(
            f"player={player} name={name!r} final={final_money:.0f} max={max_money:.0f} "
            f"land_days={land_days} peak={dict(peak)} buys={useful_orders} "
            f"work={{'PLANT': {actions['PLANT']}, 'WATER': {actions['WATER']}, "
            f"'HARVEST': {actions['HARVEST']}, 'FEED': {actions['FEED']}, 'CARE': {actions['CARE']}}}"
        )


if __name__ == "__main__":
    for replay_path in sorted(glob.glob("replays/episode-*-replay.json")):
        analyze(replay_path)
