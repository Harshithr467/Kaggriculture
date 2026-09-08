"""Compare several top agents' builds side by side.

One strong agent's build could be idiosyncratic. Where several independent top
agents converge on the same choice, that is evidence about the game rather than
about one author's taste -- and where they disagree, the choice probably does
not matter much.

    python compare_top_agents.py kaggle_episode_data/replays/top5 [more dirs...]
"""
import collections
import glob
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TURNS = 24
I0 = 10000
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]


def load_games(directories):
    games = []
    for directory in directories:
        for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
            try:
                raw = json.load(open(path, encoding="utf-8"))
            except Exception:
                continue
            steps = raw.get("steps") or []
            if not steps:
                continue
            rewards = [s.get("reward") for s in steps[-1]]
            if any(r is None for r in rewards):
                continue
            names = (raw.get("info", {}) or {}).get("TeamNames") or ["P0", "P1"]
            games.append((os.path.basename(path), names, rewards, steps))
    return games


def profile(steps, seat):
    peak = collections.Counter()
    quad_day = {}
    hands = []
    idle_mid = []
    for day in range(30):
        idx = min(day * TURNS + 12, len(steps) - 1)
        entry = steps[idx][seat].get("observation") or steps[idx][0]["observation"]
        farm = entry["farms"][seat]
        crop = collections.Counter()
        animal = collections.Counter()
        idle = owned = 0
        for row in farm["tiles"]:
            for t in row:
                if t != "LOCKED":
                    owned += 1
                if t is None:
                    idle += 1
                elif isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        crop[t["crop"]] += 1
                    elif t.get("kind") == "WEED":
                        idle += 1
                    elif t.get("animal"):
                        animal[t["animal"]] += 1
        for k in CROPS:
            peak[k] = max(peak[k], crop[k])
        for k in ANIMALS:
            peak[k] = max(peak[k], animal[k])
        quad_day.setdefault(len(farm["unlocked_quadrants"]), day)
        if 8 <= day <= 26:
            hands.append(len(farm["hands"]))
            idle_mid.append(100.0 * idle / max(1, owned))

    ops = collections.Counter()
    sells = collections.Counter()
    sell_inv = collections.defaultdict(list)
    for i, st in enumerate(steps):
        entry = st[seat]
        action = entry.get("action")
        if not isinstance(action, dict):
            continue
        for unit in [action.get("farmer", ["PASS"])] + list(action.get("hands") or []):
            if isinstance(unit, list) and unit:
                ops[unit[0]] += 1
        obs = entry.get("observation") or {}
        for order in (action.get("market") or [])[:10]:
            if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
                sells[order[1]] += int(order[2])
                inv = (obs.get("market") or {}).get("inventory", {}).get(order[1], I0)
                sell_inv[order[1]].append(inv - I0)

    total = sum(ops.values()) or 1
    animal_days = sum(peak[a] for a in ANIMALS) * 22 or 1
    return {
        "peak": peak,
        "q3": quad_day.get(3, 99),
        "q4": quad_day.get(4, 99),
        "maxq": max(quad_day) if quad_day else 1,
        "hands": sum(hands) / max(1, len(hands)),
        "idle": sum(idle_mid) / max(1, len(idle_mid)),
        "actions": total,
        "move": 100.0 * sum(ops[m] for m in MOVES) / total,
        "pass": 100.0 * ops["PASS"] / total,
        "ops": ops,
        "care_cov": 100.0 * ops["CARE"] / animal_days,
        "sells": sells,
        "sell_inv": {k: sorted(v)[len(v) // 2] for k, v in sell_inv.items() if v},
    }


games = load_games(sys.argv[1:])
# A top agent appears in every replay of its own batch; opponents appear once.
appearances = collections.Counter()
for _name, names, _r, _s in games:
    for nm in set(names):
        appearances[nm] += 1
agents = [nm for nm, c in appearances.items() if c >= 3]

print(f"{len(games)} replays; agents appearing 3+ times: {len(agents)}")
print()

summary = {}
for agent in agents:
    profiles = []
    scores = []
    wins = 0
    for _name, names, rewards, steps in games:
        if agent not in names:
            continue
        seat = names.index(agent)
        scores.append(rewards[seat])
        wins += rewards[seat] > rewards[1 - seat]
        profiles.append(profile(steps, seat))
    if not profiles:
        continue

    def avg(key, sub=None):
        vals = [(p["peak"][sub] if sub else p[key]) for p in profiles]
        return sum(vals) / len(vals)

    summary[agent] = {
        "n": len(profiles),
        "wins": wins,
        "score": sum(scores) / len(scores),
        "profiles": profiles,
        "avg": {k: avg(None, k) for k in CROPS + ANIMALS},
        "meta": {k: avg(k) for k in ("q3", "maxq", "hands", "idle", "actions", "move", "pass", "care_cov")},
    }

order = sorted(summary, key=lambda a: -summary[a]["score"])
head = f"{'agent':<26}{'n':>3}{'W':>4}{'score':>9}{'q3':>5}{'quads':>6}{'hands':>7}{'idle%':>7}{'move%':>7}{'pass%':>7}{'care%':>7}"
print(head)
print("-" * len(head))
for agent in order:
    s = summary[agent]
    m = s["meta"]
    print(f"{agent[:25]:<26}{s['n']:>3}{s['wins']:>4}{s['score']:>9,.0f}"
          f"{m['q3']:>5.0f}{m['maxq']:>6.1f}{m['hands']:>7.1f}{m['idle']:>7.1f}"
          f"{m['move']:>7.1f}{m['pass']:>7.1f}{m['care_cov']:>7.0f}")

print()
head2 = f"{'agent':<26}" + "".join(f"{c[:5]:>8}" for c in CROPS) + "".join(f"{a[:5]:>7}" for a in ANIMALS)
print(head2)
print("-" * len(head2))
for agent in order:
    a = summary[agent]["avg"]
    print(f"{agent[:25]:<26}" + "".join(f"{a[c]:>8.1f}" for c in CROPS)
          + "".join(f"{a[x]:>7.1f}" for x in ANIMALS))

print()
print("CONSENSUS across top agents (mean of per-agent means):")
for key in CROPS + ANIMALS:
    vals = [summary[a]["avg"][key] for a in order]
    lo, hi = min(vals), max(vals)
    mean = sum(vals) / len(vals)
    verdict = "AGREE" if (hi - lo) <= max(2.0, 0.25 * max(1.0, mean)) else "differ"
    print(f"  {key:<11} mean {mean:>6.1f}   range {lo:>5.1f}-{hi:<5.1f}  {verdict}")
