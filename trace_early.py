"""Where the first ten days of money go, ours against a stronger agent's.

Mining 508 episodes put us at $932 on day 10 where the strongest 101 seats hold
~$5,825 and the shared public agent holds ~$6,070. Delaying land purchases did
not close it (-1,578) and neither did any other single constant, so this stops
guessing at the knob and reads the actual cash flow: every market order, priced,
bucketed by day, for both seats of a replay.

    python trace_early.py --replay kaggle_episode_data/replays/top1_thunder/<f>.json
    python trace_early.py --local 3          # run our agent locally and trace it

Income cannot be read from orders alone -- SELL orders are attempts and the
market rejects what the shed cannot cover -- so income is taken as the residual
of the money curve against priced spending, which is exact by construction.
"""
import argparse
import collections
import glob
import json
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LAND_PRICES = [1000, 2000, 4000]
ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
LAST_DAY = 10


def trace_seat(steps, seat, label):
    """Print a per-day cash ledger for one seat."""
    spend = collections.defaultdict(lambda: collections.Counter())
    money_at = {}
    hires_seen = collections.Counter()      # per-day hire index, for fib pricing
    quads_bought = 0

    for step in steps:
        if seat >= len(step):
            continue
        entry = step[seat]
        obs = entry.get("observation") or {}
        day = obs.get("day")
        if day is None or day > LAST_DAY:
            continue
        farms = obs.get("farms")
        if isinstance(farms, list) and len(farms) > seat and isinstance(farms[seat], dict):
            money_at[day] = farms[seat].get("money", 0)

        for order in ((entry.get("action") or {}).get("market") or []):
            if not order:
                continue
            kind = order[0]
            if kind == "HIRE":
                # Cost is fib(n-th hire *that day*); the crew resets nightly.
                n = hires_seen[day]
                spend[day]["hands"] += FIB[min(n, len(FIB) - 1)]
                hires_seen[day] += 1
            elif kind == "BUY_LAND":
                if quads_bought < len(LAND_PRICES):
                    spend[day]["land"] += LAND_PRICES[quads_bought]
                    quads_bought += 1
            elif kind == "BUY_ANIMAL" and len(order) > 2:
                spend[day]["animals"] += ANIMAL_COST.get(order[1], 0) * int(order[2])
            elif kind == "BUY_SEED" and len(order) > 2:
                spend[day]["seed"] += SEED_COST.get(order[1], 0) * int(order[2])
            elif kind == "BUY_PRODUCT" and len(order) > 2:
                # Wheat for feed, or fertilizer; priced at base, close enough.
                spend[day]["feed"] += (25 if order[1] == "WHEAT" else 100) * int(order[2])

    days = sorted(money_at)
    if not days:
        print(f"  {label}: no observations")
        return
    print(f"\n  {label}")
    print(f"    {'day':>4}{'money':>9}{'delta':>9}{'land':>7}{'animals':>9}"
          f"{'seed':>7}{'feed':>7}{'hands':>7}{'income':>9}")
    prev = None
    tot = collections.Counter()
    for d in days:
        s = spend[d]
        out = s["land"] + s["animals"] + s["seed"] + s["feed"] + s["hands"]
        delta = "" if prev is None else money_at[d] - prev
        # money(d) = money(d-1) - spend(d-1..d) + income; orders are attempts, so
        # this is an upper bound on spend and a lower bound on income.
        income = "" if prev is None else f"{money_at[d] - prev + out:,.0f}"
        print(f"    {d:>4}{money_at[d]:>9,.0f}{delta if delta == '' else f'{delta:>+9,.0f}'}"
              f"{s['land']:>7,}{s['animals']:>9,}{s['seed']:>7,}{s['feed']:>7,}"
              f"{s['hands']:>7,}{income:>9}")
        for k, v in s.items():
            tot[k] += v
        prev = money_at[d]
    print(f"    {'tot':>4}{'':>9}{'':>9}{tot['land']:>7,}{tot['animals']:>9,}"
          f"{tot['seed']:>7,}{tot['feed']:>7,}{tot['hands']:>7,}")


def seat_totals(steps, seat):
    """(day-0 spend, cumulative spend to LAST_DAY, money curve) for one seat."""
    d0 = collections.Counter()
    cum = collections.Counter()
    money_at = {}
    hires_seen = collections.Counter()
    quads_bought = 0
    for step in steps:
        if seat >= len(step):
            continue
        entry = step[seat]
        obs = entry.get("observation") or {}
        day = obs.get("day")
        if day is None or day > LAST_DAY:
            continue
        farms = obs.get("farms")
        if isinstance(farms, list) and len(farms) > seat and isinstance(farms[seat], dict):
            money_at[day] = farms[seat].get("money", 0)
        for order in ((entry.get("action") or {}).get("market") or []):
            if not order:
                continue
            k, amount, bucket = order[0], 0, None
            if k == "HIRE":
                bucket, amount = "hands", FIB[min(hires_seen[day], len(FIB) - 1)]
                hires_seen[day] += 1
            elif k == "BUY_LAND" and quads_bought < len(LAND_PRICES):
                bucket, amount = "land", LAND_PRICES[quads_bought]
                quads_bought += 1
            elif k == "BUY_ANIMAL" and len(order) > 2:
                bucket, amount = "animals", ANIMAL_COST.get(order[1], 0) * int(order[2])
            elif k == "BUY_SEED" and len(order) > 2:
                bucket, amount = "seed", SEED_COST.get(order[1], 0) * int(order[2])
            elif k == "BUY_PRODUCT" and len(order) > 2:
                bucket, amount = "feed", (25 if order[1] == "WHEAT" else 100) * int(order[2])
            if bucket:
                cum[bucket] += amount
                if day == 0:
                    d0[bucket] += amount
    return d0, cum, money_at


def aggregate(paths, mine):
    """Rank every seat by final score and show what the bands spend early."""
    seats = []
    for i, path in enumerate(paths, 1):
        try:
            raw = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        steps = raw.get("steps") or []
        if len(steps) < 2:
            continue
        teams = (raw.get("info", {}) or {}).get("TeamNames") or ["?", "?"]
        rewards = [s.get("reward") for s in steps[-1]]
        if any(r is None for r in rewards):
            continue
        for seat in (0, 1):
            d0, cum, money = seat_totals(steps, seat)
            seats.append({"team": teams[seat] if seat < len(teams) else "?",
                          "score": rewards[seat], "d0": d0, "cum": cum,
                          "money10": money.get(LAST_DAY, 0)})
        if i % 25 == 0:
            print(f"  {i}/{len(paths)}")

    if not seats:
        print("no seats parsed")
        return
    seats.sort(key=lambda s: -s["score"])
    n = len(seats)
    bands = [("top 10%", seats[:max(1, n // 10)]),
             ("top 25%", seats[:max(1, n // 4)]),
             ("middle", seats[n // 4: 3 * n // 4]),
             ("bottom 25%", seats[-max(1, n // 4):])]
    if mine:
        ours = [s for s in seats if mine.lower() in s["team"].lower()]
        if ours:
            bands.append((f"YOU ({len(ours)})", ours))

    def mean(rs, get):
        return sum(get(r) for r in rs) / len(rs)

    print(f"\n{n} seats from {len(paths)} replays\n")
    print(f"  {'band':<14}{'score':>10}{'$ d10':>9}"
          f"{'--- day 0 ---':>20}{'--- through day 10 ---':>32}")
    print(f"  {'':<14}{'':>10}{'':>9}{'animals':>10}{'seed':>10}"
          f"{'animals':>10}{'seed':>8}{'land':>8}{'feed':>7}")
    for label, rs in bands:
        print(f"  {label:<14}{mean(rs, lambda r: r['score']):>10,.0f}"
              f"{mean(rs, lambda r: r['money10']):>9,.0f}"
              f"{mean(rs, lambda r: r['d0']['animals']):>10,.0f}"
              f"{mean(rs, lambda r: r['d0']['seed']):>10,.0f}"
              f"{mean(rs, lambda r: r['cum']['animals']):>10,.0f}"
              f"{mean(rs, lambda r: r['cum']['seed']):>8,.0f}"
              f"{mean(rs, lambda r: r['cum']['land']):>8,.0f}"
              f"{mean(rs, lambda r: r['cum']['feed']):>7,.0f}")

    # Per-team, so no single agent's style is mistaken for a general rule.
    byteam = collections.defaultdict(list)
    for s in seats:
        byteam[s["team"]].append(s)
    board = sorted(((sum(x["score"] for x in v) / len(v), len(v), t)
                    for t, v in byteam.items() if len(v) >= 3), reverse=True)
    print(f"\n  {'team':<28}{'n':>4}{'score':>10}{'d0 animals':>12}{'d0 seed':>9}"
          f"{'d10 animals':>13}{'$ d10':>9}")
    for sc, cnt, t in board[:16]:
        v = byteam[t]
        print(f"  {t[:27]:<28}{cnt:>4}{sc:>10,.0f}"
              f"{mean(v, lambda r: r['d0']['animals']):>12,.0f}"
              f"{mean(v, lambda r: r['d0']['seed']):>9,.0f}"
              f"{mean(v, lambda r: r['cum']['animals']):>13,.0f}"
              f"{mean(v, lambda r: r['money10']):>9,.0f}")


def from_replay(path):
    raw = json.load(open(path, encoding="utf-8"))
    teams = (raw.get("info", {}) or {}).get("TeamNames") or ["seat0", "seat1"]
    rewards = [s.get("reward") for s in raw["steps"][-1]]
    print(f"\n{os.path.basename(path)}")
    for seat in (0, 1):
        r = rewards[seat] if seat < len(rewards) else 0
        trace_seat(raw["steps"], seat, f"{teams[seat]}  (final {r:,.0f})")


def from_local(seed):
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(["main.py", "main.py"])
    steps = env.steps
    rewards = [s.get("reward") for s in steps[-1]]
    print(f"\nlocal game, seed {seed}")
    for seat in (0, 1):
        trace_seat(steps, seat, f"ours seat{seat}  (final {rewards[seat]:,.0f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", default=None)
    ap.add_argument("--dir", default=None, help="trace the first replay in a directory")
    ap.add_argument("--local", type=int, default=None, help="seed to run locally")
    ap.add_argument("--aggregate", nargs="*", default=None,
                    help="directories to rank by score instead of tracing one game")
    ap.add_argument("--mine", default=None)
    args = ap.parse_args()

    if args.aggregate is not None:
        paths = []
        for d in args.aggregate:
            paths += sorted(glob.glob(os.path.join(d, "**", "*.json"), recursive=True))
        aggregate(paths, args.mine)
        return
    if args.dir:
        files = sorted(glob.glob(os.path.join(args.dir, "**", "*.json"), recursive=True))
        if files:
            from_replay(files[0])
    if args.replay:
        from_replay(args.replay)
    if args.local is not None:
        from_local(args.local)


if __name__ == "__main__":
    main()
