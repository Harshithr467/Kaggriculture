"""Build the combined agent: the public V14 route + our front-running counter.

What can and cannot be combined, measured rather than assumed:

* The route's PLAN (farmer and hand actions for all 720 turns) is a recording.
  It has no job scoring, no crop targets and no herd sizing, so none of our
  tuned constants -- TRAVEL_DIVISOR, MARGINAL_ACTION_VALUE, ANIMAL_MARGIN_BIAS,
  ANIMAL_TOTAL_CAP -- have anything to act on. They tune a policy engine the
  route does not contain.

* The route's SALE TIMING is adaptive, and that is the seam. Stock V14 advances
  its own scheduled premium sales by exactly one step, which is why two clones
  tie exactly: both preempt by the same amount. Advancing further wins every
  game against stock, because the finite purses (wool 59 units, milk 76, melon
  158) go to whoever reaches them first.

      seeds 720-727   lookahead 2: 16/16   lookahead 4: 16/16
      seeds 730-737   lookahead 2: 15/16   lookahead 3: 15/16   lookahead 4: 15/16

  Falls off at 8 (13/16), so the useful range is 2 to 4 and 3 is the middle of
  a measured plateau rather than the peak of a spike.

* NO_BUY_LAST_DAYS has no home either: the route's only late purchases are
  HIRE orders on step 696, and hands are re-hired daily and cost a few dollars,
  so gating them buys nothing.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOOKAHEAD_VALUE = 3

src = io.open(os.path.join(HERE, "route_agent.py"), encoding="utf-8").read()

OLD = """def _next_sale_qty(step, item):
    future = step + 1
    if not 0 <= future < len(_ROUTE):
        return 0
    return sum((max(0, int(order[2])) for order in _ROUTE[future].get('market') or [] if len(order) >= 3 and order[0] == 'SELL' and (order[1] == item)))"""

NEW = f'''# How many steps ahead of the recorded schedule to pull a premium sale.
# Stock V14 uses 1, so two clones preempt each other identically and tie to the
# dollar. Measured against stock over two independent seed sets, 2 to 4 wins 31
# of 32 games; 8 gives most of it back. See build_combined.py.
LOOKAHEAD = {LOOKAHEAD_VALUE}


def _next_sale_qty(step, item):
    total = 0
    for ahead in range(1, LOOKAHEAD + 1):
        future = step + ahead
        if not 0 <= future < len(_ROUTE):
            break
        total += sum((max(0, int(order[2])) for order in _ROUTE[future].get('market') or []
                      if len(order) >= 3 and order[0] == 'SELL' and (order[1] == item)))
    return total'''

assert OLD in src, "route_agent.py does not match the expected shape"
combined = src.replace(OLD, NEW, 1)

header = ('"""V14 route with the premium-sale preemption widened from 1 step to '
          f'{LOOKAHEAD_VALUE}.\n\nSee kernels/build_combined.py for what was and was not combined, '
          'and why."""\n')
combined = header + combined.split('"""', 2)[2].lstrip("\n")

out = os.path.join(os.path.dirname(HERE), "agent_combined.py")
io.open(out, "w", encoding="utf-8", newline="").write(combined)
print(f"wrote {out} with LOOKAHEAD={LOOKAHEAD_VALUE}")
