"""Exact per-product ledger for a downloaded replay.

Reading the numbers off the action list does not work. Order quantities are what
was REQUESTED, and a sale stops the instant the shed runs dry -- in episode
93781740 our agent asks to sell 126 MELON and realises $12. Reconstructing the
market by hand does not work either, because unit actions run BEFORE the market
inside a turn, so the shed recorded in the observation is not the shed the sale
drew from.

So this replays the recorded actions through the real environment on the real
seed and instruments the environment's own _commit_unit. Every trade is logged
with the price it actually cleared at. The final money is checked against the
replay; if it matches, the ledger is exact by construction.

    python replay_ledger.py C:/path/to/93781740.json
"""
import collections
import io
import json
import os
import sys

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

from kaggle_environments import make                                # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K   # noqa: E402


def playback(recorded):
    """An agent that replays one seat's recorded actions, indexed by step."""
    def agent(obs):
        step = int(obs.get("step", 0) or 0)
        act = recorded[step] if step < len(recorded) else None
        if not isinstance(act, dict):
            return {"farmer": ["PASS"], "hands": [], "market": []}
        return act
    return agent


def main():
    path = sys.argv[1]
    d = json.load(io.open(path, encoding="utf-8"))
    steps = d["steps"]
    names = d["info"]["TeamNames"]
    seed = d["info"]["seed"]

    # env.steps[i].action is the action that PRODUCED state i, so the action
    # chosen at step s sits at index s+1.
    recorded = [[None] * len(steps) for _ in (0, 1)]
    for i in range(1, len(steps)):
        for p in (0, 1):
            recorded[p][i - 1] = steps[i][p].get("action")

    revenue = [collections.Counter(), collections.Counter()]
    units = [collections.Counter(), collections.Counter()]
    spend = [collections.Counter(), collections.Counter()]
    by_day = [collections.defaultdict(collections.Counter) for _ in (0, 1)]
    ident = {}
    clock = {"step": 0}

    original = K._commit_unit

    def traced(op, item, price, farm, private, market, shed_capacity=100):
        ok = original(op, item, price, farm, private, market, shed_capacity)
        if ok:
            p = ident.get(id(private))
            if p is not None:
                day = clock["step"] // 24
                if op == "SELL":
                    revenue[p][item] += price
                    units[p][item] += 1
                    by_day[p][day][item] += price
                else:
                    spend[p][f"{op.split('_')[1].lower()} {item.lower()}"] += price
                    by_day[p][day]["-" + item.lower()] -= price
        return ok

    original_market = K._process_market

    def traced_market(state, env):
        # Re-identify every step: the observation objects are rebuilt each turn,
        # so an id() map cached once goes stale after the first step and every
        # later trade is silently dropped from the ledger.
        ident.clear()
        for p, s in enumerate(state):
            ident[id(s.observation.private)] = p
        clock["step"] = int(K.get(state[0].observation, "step", 0))
        return original_market(state, env)

    K._commit_unit = traced
    K._process_market = traced_market
    try:
        env = make("kaggriculture", configuration={"seed": seed}, debug=False)
        env.run([playback(recorded[0]), playback(recorded[1])])
    finally:
        K._commit_unit = original
        K._process_market = original_market

    final = [(env.steps[-1][0].observation["farms"][p]).get("money") for p in (0, 1)]
    print(f"{names[0]} {d['rewards'][0]:,.0f}   vs   {names[1]} {d['rewards'][1]:,.0f}")
    print(f"replayed: {final[0]:,.0f} / {final[1]:,.0f}   "
          f"{'EXACT MATCH' if [round(x) for x in final] == [round(x) for x in d['rewards']] else 'MISMATCH -- ledger is approximate'}")

    items = sorted(set(revenue[0]) | set(revenue[1]),
                   key=lambda it: -(revenue[0][it] + revenue[1][it]))
    print(f"\n{'REVENUE':<14}{names[0][:13]:>21}{names[1][:13]:>21}{'gap':>12}")
    for it in items:
        a, b = revenue[0][it], revenue[1][it]
        print(f"  {it:<12}{a:>11,.0f} ({units[0][it]:>4}u){b:>11,.0f} "
              f"({units[1][it]:>4}u){a - b:>+12,.0f}")
    ta, tb = sum(revenue[0].values()), sum(revenue[1].values())
    print(f"  {'TOTAL':<12}{ta:>11,.0f}        {tb:>11,.0f}        {ta - tb:>+12,.0f}")

    print(f"\n{'SPEND':<14}{names[0][:13]:>21}{names[1][:13]:>21}")
    keys = sorted(set(spend[0]) | set(spend[1]), key=lambda k: -(spend[0][k] + spend[1][k]))
    for k in keys:
        print(f"  {k:<22}{spend[0][k]:>10,.0f}{spend[1][k]:>21,.0f}")
    sa, sb = sum(spend[0].values()), sum(spend[1].values())
    print(f"  {'TOTAL':<22}{sa:>10,.0f}{sb:>21,.0f}")
    print(f"\n  revenue - market spend    {ta - sa:>10,.0f}{tb - sb:>21,.0f}"
          f"      (rest is HIRE, BUY_LAND, and the $3,000 float)")

    top = [it for it in items[:4]]
    print(f"\n=== when the money was made, by day ({', '.join(top)})")
    print(f"{'day':>4}" + "".join(f"{it[:5] + ' A':>11}{it[:5] + ' B':>11}" for it in top))
    for day in range(30):
        cells = ""
        for it in top:
            cells += f"{by_day[0][day][it]:>11,.0f}{by_day[1][day][it]:>11,.0f}"
        if cells.strip(" ,0"):
            print(f"{day:>4}{cells}")
    print(f"   A = {names[0]}, B = {names[1]}")

    print("\n=== town draw this game")
    town = collections.Counter(env.steps[-1][0].observation["town"]["unlocked_shops"])
    demand = collections.Counter()
    for shop, n in town.items():
        prods = K.SHOPS[shop]
        for it in prods:
            demand[it] += n * (2 if len(prods) == 1 else 1)
    print(f"  shops: {dict(town)}")
    print(f"  units eaten per 4-step tick: {dict(demand.most_common())}")


if __name__ == "__main__":
    main()
