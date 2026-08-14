"""Who fertilizes what, and how many units a tile actually returns.

The environment grows non-ongoing crops (WHEAT, CARROT, MELON) only on the days
they are watered, inside the window

    (max_yield_day + 1) // 2  <=  age  <=  max_yield_day

adding 1 unit per watering, or 2 while fertilized. Wheat's window is ages 2-4,
so three waterings return 3 units unfertilized and 6 fertilized -- one
FERTILIZE covers `day`..`day+2`, exactly the whole window. Carrot is the same
shape (2 -> 4). Melon's window is ages 6-12 against a cap of 6, so fertilizer
buys it no extra units at all, only fewer waterings.

This walks replays and reports, per team, both halves of that: which crops they
spend FERTILIZE actions on, and the mean units per HARVEST, which reveals the
effect whether or not we identify the fertilize target correctly.

    python audit_fertilizer.py kaggle_episode_data/replays/top1_thunder
    python audit_fertilizer.py kaggle_episode_data/replays/top5 --team fistyee
"""
import argparse
import collections
import glob
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CROP_NAMES = {"WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"}


def tile_at(obs_farm, pos):
    """Tile dict at [y, x] of a farm's tile grid, or None."""
    try:
        y, x = pos
        return obs_farm["tiles"][y][x]
    except Exception:
        return None


def crop_of(tile):
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        return tile.get("crop")
    return None


def walk(path, stats):
    raw = json.load(open(path, encoding="utf-8"))
    teams = (raw.get("info", {}) or {}).get("TeamNames") or ["?", "?"]
    steps = raw.get("steps") or []

    for idx, team in enumerate(teams):
        st = stats[team]
        st["games"].add(os.path.basename(path))

        for step in steps:
            if idx >= len(step):
                continue
            entry = step[idx]
            action = entry.get("action") or {}
            obs = entry.get("observation") or {}
            # The farm state in this step is what the action is about to act on.
            farms = obs.get("farms") or obs.get("players")
            farm = None
            if isinstance(farms, list) and len(farms) > idx:
                farm = farms[idx]
            elif isinstance(obs.get("farm"), dict):
                farm = obs["farm"]
            if not isinstance(farm, dict) or "tiles" not in farm:
                continue

            # Commands carry no coordinate: a worker acts on the tile it is
            # standing on, so pair each command with that worker's position.
            pairs = [(action.get("farmer") or [], farm.get("farmer"))]
            hands_cmd = action.get("hands") or []
            hands_pos = farm.get("hands") or []
            for i, pos in enumerate(hands_pos):
                pairs.append((hands_cmd[i] if i < len(hands_cmd) else [], pos))

            for cmd, pos in pairs:
                if not cmd or pos is None:
                    continue
                op = cmd[0]
                if op not in ("FERTILIZE", "HARVEST", "WATER"):
                    continue
                tile = tile_at(farm, pos)
                crop = crop_of(tile)
                if not crop:
                    continue
                if op == "FERTILIZE":
                    st["fertilize"][crop] += 1
                elif op == "WATER":
                    st["water"][crop] += 1
                elif op == "HARVEST":
                    units = tile.get("yield_units", 0)
                    if units > 0:
                        st["harvests"][crop] += 1
                        st["units"][crop] += units


def blank():
    return {
        "games": set(),
        "fertilize": collections.Counter(),
        "harvests": collections.Counter(),
        "units": collections.Counter(),
        "water": collections.Counter(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="replay files or directories")
    ap.add_argument("--team", default=None, help="substring filter on team name")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, "**", "*.json"), recursive=True))
        else:
            files.append(p)

    stats = collections.defaultdict(blank)
    for f in files:
        try:
            walk(f, stats)
        except Exception as exc:
            print(f"  ! {os.path.basename(f)}: {exc}")

    rows = sorted(stats.items(), key=lambda kv: -len(kv[1]["games"]))
    for team, st in rows:
        if args.team and args.team.lower() not in team.lower():
            continue
        n = len(st["games"])
        if not st["harvests"]:
            continue
        print()
        print(f"{team}   ({n} game{'s' if n != 1 else ''})")
        print(f"  {'crop':<12}{'fert/g':>8}{'water/g':>9}{'harv/g':>8}{'units/g':>9}{'units/harvest':>15}")
        for crop in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"):
            h = st["harvests"][crop]
            if not h:
                continue
            print(f"  {crop:<12}{st['fertilize'][crop] / n:>8.1f}{st['water'][crop] / n:>9.1f}"
                  f"{h / n:>8.1f}{st['units'][crop] / n:>9.1f}{st['units'][crop] / h:>15.2f}")


if __name__ == "__main__":
    main()
