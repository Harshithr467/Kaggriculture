"""Where does our tape stop agreeing with a stronger agent that opens the same way?

The opening-hash census says our route and Kaito Fukami's share a byte-identical
day 0 -- almost certainly a common public ancestor -- while sitting about a
thousand rating points apart. That makes his games the most informative replays
available to us: the confound of "different farm entirely" is gone, so wherever
the two tapes diverge is a decision one of us changed.

    python route_diff.py --team "Kaito Fukami" --folder kaggle_episode_data/daily/2026-08-20

Reports the first step at which the field plans differ, then a per-day summary
of how much of each day differs, and the market orders each side issues.

Read the field diff with weeds in mind: a weed repair substitutes a DIG and then
shifts that actor's schedule, so isolated late-season differences are noise. A
divergence that starts on a fixed day and persists is a real plan change.
"""
import argparse
import collections
import glob
import io
import json
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def tape(steps, seat):
    field, market = [], []
    for i in range(1, len(steps)):
        action = steps[i][seat].get("action")
        if not isinstance(action, dict):
            field.append(None)
            market.append([])
            continue
        farmer = list(action.get("farmer") or ["PASS"])
        hands = [list(h or ["PASS"]) for h in (action.get("hands") or [])]
        field.append([farmer] + hands)
        market.append([list(o) for o in (action.get("market") or [])])
    return field, market


def find(folder, team):
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        names = d.get("info", {}).get("TeamNames") or []
        if team not in names or len(d.get("steps") or []) < 700:
            continue
        out.append((path, d, names.index(team)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", required=True)
    ap.add_argument("--folder", nargs="+",
                    default=["kaggle_episode_data/daily/2026-08-20"])
    ap.add_argument("--ref", default="agent_combined.py")
    args = ap.parse_args()

    found = []
    for folder in args.folder:
        found.extend(find(folder, args.team))
    if not found:
        raise SystemExit(f"no replays for {args.team!r}")

    import benchmark_pool as BP
    ours = BP._get_agent(args.ref)
    route = ours._ROUTE

    path, d, seat = found[0]
    theirs_field, theirs_market = tape(d["steps"], seat)
    print(f"{args.team}: {len(found)} replay(s), using {os.path.basename(path)}"
          f" seat {seat}, banked {d['rewards'][seat]:,.0f}\n")

    ours_field = []
    ours_market = []
    for step in range(min(len(route), len(theirs_field))):
        s = route[step]
        ours_field.append([list(s.get("farmer") or ["PASS"])]
                          + [list(h or ["PASS"]) for h in (s.get("hands") or [])])
        ours_market.append([list(o) for o in (s.get("market") or [])])

    n = min(len(ours_field), len(theirs_field))
    first = next((i for i in range(n) if ours_field[i] != theirs_field[i]), None)
    firstm = next((i for i in range(n) if ours_market[i] != theirs_market[i]), None)
    print(f"first FIELD difference : step {first}"
          f"{'' if first is None else f' (day {first // 24}, hour {first % 24})'}")
    print(f"first MARKET difference: step {firstm}"
          f"{'' if firstm is None else f' (day {firstm // 24}, hour {firstm % 24})'}\n")

    byday = collections.Counter()
    mbyday = collections.Counter()
    for i in range(n):
        if ours_field[i] != theirs_field[i]:
            byday[i // 24] += 1
        if ours_market[i] != theirs_market[i]:
            mbyday[i // 24] += 1
    print(f"{'day':>4}{'field steps differing':>24}{'market steps differing':>25}")
    for day in range(n // 24 + 1):
        f, m = byday.get(day, 0), mbyday.get(day, 0)
        if not f and not m:
            continue
        print(f"{day:>4}{f:>18} / 24{m:>19} / 24")

    print(f"\ntotal: {sum(byday.values())} of {n} field steps differ, "
          f"{sum(mbyday.values())} market steps")

    print("\nTHEIR market orders we never issue (by item and op):")
    theirs_ops = collections.Counter()
    ours_ops = collections.Counter()
    for i in range(n):
        for o in theirs_market[i]:
            theirs_ops[(o[0], o[1] if len(o) > 1 else "")] += int(o[2]) if len(o) > 2 else 1
        for o in ours_market[i]:
            ours_ops[(o[0], o[1] if len(o) > 1 else "")] += int(o[2]) if len(o) > 2 else 1
    keys = sorted(set(theirs_ops) | set(ours_ops))
    print(f"  {'op / item':<28}{'theirs':>9}{'ours':>9}{'delta':>9}")
    for k in keys:
        t, o = theirs_ops.get(k, 0), ours_ops.get(k, 0)
        if t == o:
            continue
        print(f"  {k[0] + ' ' + k[1]:<28}{t:>9,}{o:>9,}{t - o:>+9,}")


if __name__ == "__main__":
    main()
