"""Compare our build against our opponents', split by outcome.

For every replay, extract a comparable feature vector for both seats (land
timing, peak crop and animal counts, labour, action mix, endgame idle land),
then aggregate four groups:

    us / winners      - what beat us
    us / losers       - what we beat
    them / winners    - the opponents who beat us
    them / losers     - the opponents we beat

The interesting column is "what beat us" versus "what we do", restricted to
close games, where a single difference plausibly decided it.

    python analyze_opponents.py 55397388
    python analyze_opponents.py 55397388 --close 15000
"""
import argparse
import collections
import glob
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT = os.path.dirname(os.path.abspath(__file__))
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]
TURNS = 24


def features(steps, seat):
    """Feature vector for one player across one game."""
    peak_crop = {c: 0 for c in CROPS}
    peak_animal = {a: 0 for a in ANIMALS}
    quad_day = {}
    hands = []
    idle26 = (0, 0, 1)
    for day in range(30):
        idx = min(day * TURNS + 12, len(steps) - 1)
        farm = steps[idx][0]["observation"]["farms"][seat]
        crops = collections.Counter()
        animals = collections.Counter()
        empty = weeds = owned = 0
        for row in farm["tiles"]:
            for t in row:
                if t != "LOCKED":
                    owned += 1
                if t is None:
                    empty += 1
                elif isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        crops[t["crop"]] += 1
                    elif t.get("kind") == "WEED":
                        weeds += 1
                    elif t.get("animal"):
                        animals[t["animal"]] += 1
        for c in CROPS:
            peak_crop[c] = max(peak_crop[c], crops[c])
        for a in ANIMALS:
            peak_animal[a] = max(peak_animal[a], animals[a])
        q = len(farm["unlocked_quadrants"])
        quad_day.setdefault(q, day)
        if 8 <= day <= 26:
            hands.append(len(farm["hands"]))
        if day == 26:
            idle26 = (empty, weeds, owned)

    ops = collections.Counter()
    for st in steps:
        action = st[seat].get("action")
        if not isinstance(action, dict):
            continue
        for unit in [action.get("farmer", ["PASS"])] + list(action.get("hands", []) or []):
            if isinstance(unit, list) and unit:
                ops[unit[0]] += 1
    total = sum(ops.values()) or 1

    row = {
        "quads_end": max(quad_day) if quad_day else 1,
        "day_q2": quad_day.get(2, 99),
        "day_q3": quad_day.get(3, 99),
        "day_q4": quad_day.get(4, 99),
        "hands": sum(hands) / max(1, len(hands)),
        "move%": 100.0 * sum(ops[m] for m in MOVES) / total,
        "pass%": 100.0 * ops["PASS"] / total,
        "actions": total,
        "idle26%": 100.0 * (idle26[0] + idle26[1]) / max(1, idle26[2]),
        "owned26": idle26[2],
    }
    for c in CROPS:
        row["pk_" + c[:4].lower()] = peak_crop[c]
    for a in ANIMALS:
        row["pk_" + a[:3].lower()] = peak_animal[a]
    for op in ("WATER", "HARVEST", "PLANT", "FERTILIZE", "CARE", "COLLECT_FERTILIZER"):
        row[op[:5].lower()] = ops[op]
    return row


def mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return sum(vals) / len(vals) if vals else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("submission")
    parser.add_argument("--close", type=int, default=15000,
                        help="margin under which a game counts as close")
    args = parser.parse_args()

    directory = os.path.join(PROJECT, "kaggle_episode_data", "replays", str(args.submission))
    paths = sorted(glob.glob(os.path.join(directory, "*.json")))
    if not paths:
        sys.exit(f"no replays in {directory}")

    games = []
    seen = collections.Counter()
    raw_games = []
    for path in paths:
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
        for nm in set(names):
            seen[nm] += 1
        raw_games.append((path, names, rewards, steps))
    me = seen.most_common(1)[0][0]

    for path, names, rewards, steps in raw_games:
        seat = 0 if names[0] == me else 1
        opp = 1 - seat
        mine, theirs = rewards[seat], rewards[opp]
        games.append({
            "ep": os.path.basename(path).split("-")[1],
            "opp_name": names[opp],
            "margin": mine - theirs,
            "mine": mine,
            "theirs": theirs,
            "us": features(steps, seat),
            "them": features(steps, opp),
        })

    losses = [g for g in games if g["margin"] < 0]
    wins = [g for g in games if g["margin"] >= 0]
    close_losses = [g for g in losses if abs(g["margin"]) <= args.close]

    print(f"our team {me!r} | {len(wins)}W-{len(losses)}L over {len(games)} games")
    print(f"close losses (within {args.close:,}): {len(close_losses)}")
    print()

    keys = ["quads_end", "day_q3", "day_q4", "hands", "move%", "pass%", "actions", "idle26%",
            "pk_whea", "pk_carr", "pk_toma", "pk_stra", "pk_melo",
            "pk_goo", "pk_cow", "pk_she",
            "water", "harve", "plant", "ferti", "care", "colle"]

    groups = [
        ("US in close losses", [g["us"] for g in close_losses]),
        ("THEM in close losses", [g["them"] for g in close_losses]),
        ("US in wins", [g["us"] for g in wins]),
        ("THEM in wins", [g["them"] for g in wins]),
    ]
    width = max(len(k) for k in keys) + 2
    header = " " * width + "".join(f"{name:>22}" for name, _ in groups)
    print(header)
    print("-" * len(header))
    for key in keys:
        line = f"{key:<{width}}"
        for _, rows in groups:
            line += f"{mean(rows, key):>22,.1f}"
        print(line)

    print()
    print("CLOSE LOSSES, per game (us -> them):")
    print(f"{'ep':>10}{'margin':>10}{'melon':>14}{'straw':>12}{'quads':>10}{'animals':>12}{'hands':>12}  opponent")
    for g in sorted(close_losses, key=lambda z: -z["margin"]):
        u, t = g["us"], g["them"]
        ua = u["pk_goo"] + u["pk_cow"] + u["pk_she"]
        ta = t["pk_goo"] + t["pk_cow"] + t["pk_she"]
        print(f"{g['ep']:>10}{g['margin']:>+10,.0f}"
              f"{u['pk_melo']:>7.0f}->{t['pk_melo']:<6.0f}"
              f"{u['pk_stra']:>5.0f}->{t['pk_stra']:<6.0f}"
              f"{u['quads_end']:>4.0f}->{t['quads_end']:<5.0f}"
              f"{ua:>6.0f}->{ta:<5.0f}"
              f"{u['hands']:>6.1f}->{t['hands']:<5.1f}  {g['opp_name']}")

    print()
    print("STRONGEST OPPONENTS (their score, regardless of outcome):")
    for g in sorted(games, key=lambda z: -z["theirs"])[:8]:
        t = g["them"]
        print(f"  ep {g['ep']}  they {g['theirs']:>8,.0f} vs us {g['mine']:>8,.0f}  "
              f"quads {t['quads_end']:.0f} (q3 d{t['day_q3']:.0f})  hands {t['hands']:.1f}  "
              f"melon {t['pk_melo']:.0f} straw {t['pk_stra']:.0f} tom {t['pk_toma']:.0f} "
              f"animals {t['pk_goo']+t['pk_cow']+t['pk_she']:.0f}  "
              f"move {t['move%']:.0f}%  {g['opp_name']}")


if __name__ == "__main__":
    main()
