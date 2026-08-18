"""Build the combined agent: the public V14 route + our counters.

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

* The route's sale SIZING is not adaptive at all. Prices are recomputed per
  unit, so a 54-unit order walks the ladder down and every unit after the first
  fetches less. Measured over a full route-vs-route game on seed 600, the
  schedule walks its own core products into the floor and keeps selling:

      day 21   MILK $1     MELON $1
      day 24   STRAWBERRY $1
      day 29   the route sells 54 MILK, at $5 a unit

  The obvious read is that it should meter: the town eats every product every
  four steps, so a crashed price recovers on its own -- wool goes $1 -> $72 ->
  $133 -> $174 -> $196 over four days with nobody's help. THAT READ IS WRONG,
  and expensively so. Metering scheduled sales behind a price floor, with the
  deferred units carried forward and liquidated on the last day:

      floor 0.00 x base (control)  15/16   our 92,252   theirs  90,845
      floor 0.25 x base             0/16   our 68,396   theirs 120,160
      floor 0.40 x base             0/16   our 65,824   theirs 121,475
      floor 0.55 x base             0/16   our 58,442   theirs 125,336

  Not a wobble: zero wins, and the opponent gets $30k RICHER as we get $26k
  poorer. The price is at $1 because both players are racing each other down a
  shared ladder, and every unit held back is a unit of the ladder conceded. The
  crash is not a mistake to be avoided, it is the outcome of a race, and the
  only thing that pays is reaching the top of the ladder first.

  So the third layer runs the other way: sell pure-output stock the moment it
  is worth selling, ahead of the recorded schedule. WHEAT and FERTILIZER are
  excluded, because the route's shed wheat is animal feed and its fertilizer
  is an input -- a seller that emptied the shed would sell the herd's dinner.

* The route's HERD is correct, and the argument that it is not is a trap worth
  writing down. Price decay shapes differ wildly, and the revenue available
  from I0 before a product's price hits $1 looks damning for the route's
  choices:

      EGG        $77,221     never halves      (log, target 0.20)
      MELON      $26,485     dead at 159 units (sq,  target 3.60)
      WOOL        $7,928     dead at  60 units (sq,  target 3.20)
      MILK        $6,181     dead at  77 units (linear, target 1.60)

  The route buys 8 cows and 4 sheep and no geese, so it aims at the two
  smallest purses on the board while EGG -- flat curve, and 300 units SHORT at
  $68 by day 29 because the town eats eggs all season and nobody restocks --
  goes untouched. Swapping the herd to geese is a clean rewrite: BUILD_COOP and
  BUILD_PASTURE both cost nothing, FEED/CARE/HARVEST are animal-agnostic, and
  a goose is cheaper than a cow and yields daily from day 4 instead of every
  other day from day 8. It works mechanically -- 13 coops, 9 geese, 281 eggs
  sold -- and it loses 0 of 16, at -$47,421.

  THAT TABLE IS A SNAPSHOT, NOT A BUDGET. The town consumes every product every
  four steps for the whole season, so the purses refill continuously; the
  "dead at 77 units" figure describes one instant, not thirty days. What
  actually decides an animal is its yield times its base price:

      COW    $400 -> 11 productions x2 =  22 MILK @ $160 ~ $3,520
      SHEEP  $500 ->  8 productions x2 =  16 WOOL @ $200 ~ $3,200
      GOOSE  $300 -> 26 productions x2 =  52 EGG  @ $50  ~ $2,600, and capped
                     at 4 held, so it needs harvesting every other day to hit
                     even that -- we got 31 eggs a goose, not 52

  Cows win, and vacating milk and wool hands the opponent an uncontested run at
  both. Static purse size was the wrong statistic.

* The route's CROPS have exactly one gap the schedule can absorb, and it is
  the only structural change here that survived. The route grows WHEAT, MELON
  and STRAWBERRY; it never grows CARROT, TOMATO or EGG, so in a field of route
  clones the town eats those three all season with nobody restocking. A
  route-vs-route game ends with carrot 408 units short at $65 while wheat sits
  at $42.

  There is no slack to exploit that with -- the route is 95% busy across 6,650
  unit-turns and acts on every one of its 75 unlocked tiles -- so the only
  lever is substitution, and the crop calendars barely overlap:

      WHEAT   waters at ages 2-4, tile survives to age 5
      CARROT  waters at ages 2-3, tile starts decaying at age 4

  128 of the route's 143 wheat plantings are lifted at age 4, where a carrot
  would already be rotting. The other 13 are the end-of-season batch, planted
  day 26 and lifted day 29, watered at ages 2 and 3 -- a carrot's entire yield
  window. Those 13 swap cleanly, and the set is identical on seeds 600, 611 and
  622, so it is schedule-driven rather than seed-driven.

      seeds 600-615   31/32 -> 32/32,  our score +$602, theirs +$75
      seeds 700-719   +$783 a game, sd $1,762, t = 2.81, better in 26 of 40

  Both numbers move the same way and the opponent's does not move at all,
  which is what a change that adds revenue rather than taking it looks like.

* The MELON OPENING, which is the single biggest gap in the live record, does
  NOT transplant. It is worth writing down at length because it is the most
  expensive-looking opportunity on the board and it is a trap.

  Across 39 live losses melon is the primary cause in 17 of them, and the gap is
  +13,584 in fifteen separate games against fifteen different opponents. The
  same number every time, because it is structural: they plant 12 melons on day
  0 and harvest into a virgin $250 market on day 10; we plant 5, then 14 more on
  days 10-11 that ripen on day 20 into a market that died on day 11 and fetch
  about $500 in total.

  Copying it needs ground, seed and hands, and the route has none of the three:

    GROUND. Of NW's 25 tiles, 19 are planted and the other 6 are pastures with
    animals on them. An extra melon must displace a crop, and the cheapest are
    three tiles the route plants with STRAWBERRY on day 3 -- but strawberry is
    our single best market at about $244 a unit, so per tile-day it is a wash
    before any costs.

    SEED. The route LOOKS like it has spare melon seed: it orders 8 on day 0 and
    plants 5. It does not. The day-0 order is cash-clipped -- 5 requested at step
    0, only 2 clear -- and the farm is on $4 by day 1 and never has $80 spare
    again until day 5, by which point a melon ripens on day 15 and misses the
    window. Requested quantities are not delivered quantities. The first version
    of this layer planted nothing at all for exactly this reason.

    HANDS. Hiring is the one clean insertion point, because hands are re-hired
    nightly at fib(hires_today) and the route addresses them by index, so one
    more hand than it expects is ours outright. It costs $8 on day 0 and $1-$21
    a day through day 9 -- but $610 on day 10, when the roster hits 14.

  All of it was built and it works mechanically: three melons planted on days
  1-3, grown to the full 6 units each, harvested on day 11 and sold on day 11.
  It still loses every game.

      MELON_PATCH ()                      100.0% wins   our 92,959
      MELON_PATCH 3 tiles, no seed         56.2% wins   our 91,328
      MELON_PATCH 3 tiles, funded          0.0% wins   our 85,172, theirs 107,591

  Both halves lose independently. Merely carrying the extra hand costs $1,631
  and forty-four points of win rate in hire fees. Funding the seed by dropping
  one of the four day-0 sheep costs another $6,156 and hands the opponent
  $14,632 -- one sheep is roughly 16 wool at $200, and the three strawberry
  tiles were worth more than the melon that replaced them.

  The conclusion is the same one the lifted-route experiment reached from the
  other direction: the day-0 melon opening is not a module. It comes bundled
  with 2 cows instead of 1, 2 sheep instead of 4, all four quadrants, and
  strawberry displaced to land we never buy. Copying one piece of a plan into a
  plan built on different assumptions costs more than it gains.

* NO_BUY_LAST_DAYS has no home either: the route's only late purchases are
  HIRE orders on step 696, and hands are re-hired daily and cost a few dollars,
  so gating them buys nothing.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOOKAHEAD_VALUE = 3
EAGER_FLOOR_FRAC_VALUE = 0.30
HERD_SWAP_VALUE = {}
PASTURE_TILT_VALUE = None

# (route step, hand index) of every WHEAT planting the route harvests at age 3
# rather than its usual age 4 -- the end-of-season batch, planted day 26 and
# lifted day 29 -- and which it also waters at ages 2 and 3, which is a carrot's
# whole yield window. Produced by analyse_plantings.py, identical on seeds 600,
# 611 and 622, and every entry verified to be a PLANT WHEAT in the recording.
CARROT_SWAP_VALUE = (
    (629, 9), (633, 7), (633, 10), (633, 11), (634, 9), (635, 6), (638, 10),
    (639, 5), (639, 9), (641, 0), (641, 6), (645, 5), (645, 10),
)
# Bought a day early: unit actions resolve before the market each turn, and
# PLANT is atomic per crop -- if a turn asks to plant more of a crop than there
# is seed for, EVERY plant of that crop that turn is dropped.
CARROT_SEED_STEP_VALUE = 600

# Tiles borrowed for an early melon patch, and when to lift it.
#
# The route plants 5 melons on day 0 and 14 more on days 10-11. The first batch
# harvests on day 10 into a virgin $250 market; the second harvests on day 20
# into a market that died on day 11 and is worth about $500 in total. Every
# opponent that beats us plants 12 on day 0.
#
# There is no spare ground to copy them with. Of the NW quadrant's 25 tiles, 19
# are planted and the remaining 6 are pastures with animals on them, so an extra
# melon has to displace a crop. These three are the cheapest: the route first
# plants them on day 3, with STRAWBERRY that then sits until day 19.
#
# () disables it exactly and is the A/B control.
MELON_PATCH_VALUE = ()   # measured and switched OFF; see the module docstring
MELON_PATCH_PLANT_DAY_VALUE = 1     # not day 0: PLANT is atomic per crop per turn,
                                    # and colliding with the route's own melon
                                    # planting would drop BOTH sets
MELON_PATCH_HARVEST_DAY_VALUE = 11  # planted day 1, first yield day 11

# Where the seed money comes from. The route looks like it has spare melon seed
# -- it orders 8 on day 0 and plants 5 -- but it does not: the day-0 order is
# CASH-CLIPPED. It asks for 5 melon at step 0 and only 2 clear, then 3 more at
# step 1, and the farm is down to $4 by day 1 and never has $80 spare again
# until day 5, by which point a melon would ripen on day 15 and miss the window
# entirely. Requested quantities are not delivered quantities; that mistake cost
# the first version of this layer, which planted nothing at all.
#
# So the seed has to be paid for on day 0, and the only slack on day 0 is the
# herd. The route buys 1 cow and 4 sheep for $2,400; every opponent that beats
# us buys 2 and 2 and puts the difference into melon. One sheep is $500, which
# is six melon seeds with change.
MELON_PATCH_SHEEP_CUT_VALUE = 1

src = io.open(os.path.join(HERE, "route_agent.py"), encoding="utf-8").read()

# ---------------------------------------------------------------- layer two
OLD_LOOKAHEAD = """def _next_sale_qty(step, item):
    future = step + 1
    if not 0 <= future < len(_ROUTE):
        return 0
    return sum((max(0, int(order[2])) for order in _ROUTE[future].get('market') or [] if len(order) >= 3 and order[0] == 'SELL' and (order[1] == item)))"""

NEW_LOOKAHEAD = f'''# How many steps ahead of the recorded schedule to pull a premium sale.
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

assert OLD_LOOKAHEAD in src, "route_agent.py does not match the expected shape"
combined = src.replace(OLD_LOOKAHEAD, NEW_LOOKAHEAD, 1)

# ---------------------------------------------------------------- layer three
MARKET_LAYER = f'''

# ----------------------------------------------------------------------------
# Market model, transcribed from kaggle_environments/envs/kaggriculture at
# 1.32.7. The agent is handed market.inventory and market.prices in full, so it
# can price a sale exactly instead of guessing. Prices are recomputed per unit
# inside the order, which is the whole reason sale sizing matters.
# ----------------------------------------------------------------------------
_MKT_I0 = 10000
_MKT_PRICE_FLOOR = 1
_MKT_HINGE_GAIN = 8.0

# item: (base, T, below_func, below_target, above_func, above_target)
_MKT_PARAMS = {{
    'WHEAT':      (25, 400, 'sqrt', 0.80, 'log', 0.20),
    'CARROT':     (35, 450, 'hinge', 1.00, 'sqrt', 0.70),
    'TOMATO':     (60, 200, 'hinge', 0.40, 'sqrt', 0.60),
    'STRAWBERRY': (120, 100, 'sqrt', 0.70, 'linear', 1.60),
    'MELON':      (250, 300, 'log', 0.20, 'sq', 3.60),
    'EGG':        (50, 332, 'hinge', 0.40, 'log', 0.20),
    'MILK':       (160, 122, 'sqrt', 0.60, 'linear', 1.60),
    'WOOL':       (200, 105, 'log', 0.20, 'sq', 3.20),
    'FERTILIZER': (100, 200, 'linear', 0.40, 'linear', 0.40),
}}


def _mkt_shape(func, x, T=None):
    x = max(0.0, x)
    if func == 'linear':
        return x
    if func == 'sq':
        return x * x
    if func == 'sqrt':
        return math.sqrt(x)
    if func == 'log':
        return math.log(1.0 + x)
    if func == 'hinge':
        if not T or T <= 0:
            return x
        u = x / T
        return u + _MKT_HINGE_GAIN * max(0.0, u - 1.0) ** 2
    return x


def _mkt_price(item, inventory):
    p = _MKT_PARAMS.get(item)
    if p is None:
        return _MKT_PRICE_FLOOR
    base, T, below_f, below_t, above_f, above_t = p
    if inventory < _MKT_I0:
        amp = below_t * base / _mkt_shape(below_f, T, T)
        price = base + amp * _mkt_shape(below_f, _MKT_I0 - inventory, T)
    else:
        amp = above_t * base / _mkt_shape(above_f, T, T)
        price = base - amp * _mkt_shape(above_f, inventory - _MKT_I0, T)
    return max(_MKT_PRICE_FLOOR, int(round(price)))


# Exactly the products the recording has no SELL order for anywhere in its 720
# steps. That restriction is the whole safety argument: this layer can only add
# sales the schedule was never going to make, so it cannot disturb the tuned
# timing of the ones it does make. Applying it to the route's own products
# instead costs money monotonically -- measured against stock, floor 0.90 loses
# $1,456 and floor 0.0 loses $3,761, with the opponent's score unmoved, so it
# is pure self-harm. Without this layer a swapped herd's eggs would sit in the
# shed until the buzzer and score nothing.
EAGER_SELL_ITEMS = ('EGG', 'CARROT', 'TOMATO')

# Sell that stock while a unit still fetches this fraction of base. None
# disables the layer exactly and is the A/B control.
EAGER_FLOOR_FRAC = {EAGER_FLOOR_FRAC_VALUE!r}


def _affordable_units(item, inventory, want, floor_frac):
    """How many of `want` units still clear the floor, walking the ladder down."""
    p = _MKT_PARAMS.get(item)
    if p is None:
        return want
    floor = p[0] * floor_frac
    sold = 0
    inv = inventory
    while sold < want:
        price = _mkt_price(item, inv)
        if price < floor:
            break
        sold += 1
        # The environment only counts a sale into supply when it clears $1.
        if price > _MKT_PRICE_FLOOR:
            inv += 1
    return sold


def _eager_sell(action, obs, step):
    """Sell pure-output stock ahead of the recorded schedule while it pays."""
    if EAGER_FLOOR_FRAC is None:
        return action

    market_view = _value(obs, 'market', {{}}) or {{}}
    inventory = _value(market_view, 'inventory', {{}}) or {{}}
    private = _value(obs, 'private', {{}}) or {{}}
    shed = _value(private, 'shed', {{}}) or {{}}

    action = _copy_plan(action)
    market = [list(order) for order in action.get('market') or []]

    for item in EAGER_SELL_ITEMS:
        already = _market_sell_qty(action, item)
        spare = (max(0, int(_value(shed, item, 0) or 0))
                 - _pickup_holdback(action, item) - already)
        if spare <= 0:
            continue
        # Our own scheduled units go down the ladder first, so price the extra
        # ones from where that order leaves the market.
        inv = int(_value(inventory, item, _MKT_I0) or _MKT_I0) + already
        extra = _affordable_units(item, inv, spare, EAGER_FLOOR_FRAC)
        if extra <= 0:
            continue
        existing = next((o for o in market
                         if len(o) >= 3 and o[0] == 'SELL' and o[1] == item), None)
        if existing is not None:
            existing[2] = max(0, int(existing[2])) + extra
        elif len(market) < 10:
            market.append(['SELL', item, extra])

    action['market'] = market[:10]
    return action
'''

HERD_LAYER = f'''

# ----------------------------------------------------------------------------
# Herd swap: rewrite the recording itself, once, at import.
#
# The route's animal program is 8 cows and 4 sheep, which is up to 176 milk and
# 64 wool aimed at purses worth $6,181 and $7,928. Eggs have a log price curve
# with a 0.20 target -- so shallow it is effectively flat -- and the town eats
# them all season with nobody restocking. This retargets the same choreography.
#
# All-or-nothing by design: PLACE only succeeds when the worker is standing on
# a structure matching the animal, so converting some pastures to coops while
# still placing cows would silently drop those animals on the floor. The
# rewrite therefore refuses unless every animal the route places is covered.
#
# {{}} disables it exactly and is the A/B control.
# ----------------------------------------------------------------------------
HERD_SWAP = {HERD_SWAP_VALUE!r}

_ANIMAL_STRUCTURE = {{'COW': 'PASTURE', 'SHEEP': 'PASTURE', 'GOOSE': 'COOP'}}
_BUILD_OP = {{'PASTURE': 'BUILD_PASTURE', 'COOP': 'BUILD_COOP'}}
_ANIMAL_ORDER_OPS = ('PLACE', 'PICKUP', 'DROP')

# The recording as published, kept so the swap can be re-derived rather than
# accumulated. Rewriting _ROUTE in place would make HERD_SWAP a one-shot import
# side effect, and a sweep that sets it between games would read the previous
# game's herd.
_ROUTE_STOCK = copy.deepcopy(_ROUTE)
_EDITS_APPLIED = None


# ----------------------------------------------------------------------------
# Carrot swap: the one substitution the schedule can absorb.
#
# The route is 95% busy and acts on every unlocked tile, so there is no slack to
# grow anything extra in. Substitution is the only lever, and it is tightly
# constrained: WHEAT waters at ages 2-4 and its tile survives to age 5, CARROT
# waters at ages 2-3 and its tile starts decaying at age 4. Of 141 wheat
# plantings, 128 are lifted at age 4 -- a carrot there would already be rotting.
# The other 13 are the end-of-season batch, planted day 26 and lifted day 29,
# and those fit a carrot exactly.
#
# It is worth doing because nobody in a field of route clones grows carrots, so
# the town eats them all season with no restocking: a route-vs-route game ends
# with carrot 408 units short at $65 while wheat sits at $42. Selling carrot
# instead of wheat also stops us competing with ourselves in the wheat market.
# () disables it exactly and is the A/B control.
# ----------------------------------------------------------------------------
CARROT_SWAP = {CARROT_SWAP_VALUE!r}
CARROT_SEED_STEP = {CARROT_SEED_STEP_VALUE}


def _swap_carrot():
    if not CARROT_SWAP:
        return
    planted = 0
    for step, hand in CARROT_SWAP:
        if not 0 <= step < len(_ROUTE):
            continue
        hands = _ROUTE[step].get('hands') or []
        if not 0 <= hand < len(hands):
            continue
        unit = hands[hand]
        if unit and len(unit) >= 2 and unit[0] == 'PLANT' and unit[1] == 'WHEAT':
            unit[1] = 'CARROT'
            planted += 1
    if planted and 0 <= CARROT_SEED_STEP < len(_ROUTE):
        market = _ROUTE[CARROT_SEED_STEP].setdefault('market', [])
        if len(market) < 10:
            market.append(['BUY_SEED', 'CARROT', planted])


def _swap_melon_seed():
    """Pay for the patch out of the day-0 herd, in the recording itself."""
    if not MELON_PATCH or not MELON_PATCH_SHEEP_CUT:
        return
    cut = MELON_PATCH_SHEEP_CUT
    for trace in _ROUTE[:24]:
        for order in trace.get('market') or []:
            if (len(order) >= 3 and order[0] == 'BUY_ANIMAL'
                    and order[1] == 'SHEEP' and cut > 0):
                take = min(cut, max(0, int(order[2]) - 1))
                order[2] = int(order[2]) - take
                cut -= take
    # Melon seed is $80; a sheep is $500. Buy the patch and leave the change,
    # because day 0 is already spending to the last dollar.
    for trace in _ROUTE[:24]:
        for order in trace.get('market') or []:
            if len(order) >= 3 and order[0] == 'BUY_SEED' and order[1] == 'MELON':
                order[2] = int(order[2]) + len(MELON_PATCH)
                return


def _apply_route_edits():
    """Rebuild _ROUTE from the published recording under the current edits."""
    global _ROUTE, _EDITS_APPLIED
    key = (tuple(sorted(HERD_SWAP.items())), tuple(CARROT_SWAP), CARROT_SEED_STEP,
           tuple(MELON_PATCH), MELON_PATCH_SHEEP_CUT)
    if _EDITS_APPLIED == key:
        return
    _EDITS_APPLIED = key
    _ROUTE = copy.deepcopy(_ROUTE_STOCK)
    _swap_carrot()
    _swap_melon_seed()
    _swap_herd()


def _swap_herd():
    if not HERD_SWAP:
        return

    placed = set()
    for trace in _ROUTE:
        for unit in [trace.get('farmer')] + list(trace.get('hands') or []):
            if unit and len(unit) >= 2 and unit[0] == 'PLACE' and unit[1] in _ANIMAL_STRUCTURE:
                placed.add(unit[1])
        for order in trace.get('market') or []:
            if order and order[0] == 'BUY_ANIMAL' and len(order) >= 2:
                placed.add(order[1])
    # A partial swap would strand animals: PLACE only succeeds on a structure
    # matching the animal, so a cow placed on a converted coop is money burnt.
    if not placed or not placed.issubset(HERD_SWAP):
        return
    targets = {{_ANIMAL_STRUCTURE[HERD_SWAP[a]] for a in placed}}
    if len(targets) != 1:
        return
    build_op = _BUILD_OP[next(iter(targets))]
    old_builds = {{op for op in _BUILD_OP.values() if op != build_op}}

    for trace in _ROUTE:
        for unit in [trace.get('farmer')] + list(trace.get('hands') or []):
            if not unit:
                continue
            if unit[0] in old_builds:
                unit[0] = build_op
            elif (unit[0] in _ANIMAL_ORDER_OPS and len(unit) >= 2
                  and unit[1] in HERD_SWAP):
                unit[1] = HERD_SWAP[unit[1]]
        for order in trace.get('market') or []:
            if order and order[0] == 'BUY_ANIMAL' and len(order) >= 2 and order[1] in HERD_SWAP:
                order[1] = HERD_SWAP[order[1]]


# ----------------------------------------------------------------------------
# Early melon patch, worked by a hand the route does not know exists.
#
# Melon is the steepest curve on the board (sq, target 3.60: $250 at the top,
# dead at 158 units), so the day-10 harvest is the single richest moment in the
# game and it goes to whoever brings the most fruit. Across 15 losses to 15
# different opponents the melon gap is +13,584 -- the same number every time,
# because they plant 12 on day 0 and we plant 5.
#
# The insertion point is hiring. Hands are cleared and re-hired nightly at
# fib(hires_today), so one MORE hand than the recording expects costs $8 on day
# 0 and $1-$21 a day through day 9. The route addresses its hands by index and
# _match_hands pads the rest with PASS, so that extra slot is ours outright --
# no desynchronisation risk, unlike stealing an idle turn from a hand the route
# is going to move next turn.
#
# What it cannot do is conjure ground. NW is full, so the patch displaces three
# strawberries, and strawberry is our best market at roughly $244 a unit. That
# makes this a genuine trade rather than free money, which is why it is a
# measured switch and not a rewrite.
# ----------------------------------------------------------------------------
MELON_PATCH = {MELON_PATCH_VALUE!r}
MELON_PATCH_PLANT_DAY = {MELON_PATCH_PLANT_DAY_VALUE}
MELON_PATCH_HARVEST_DAY = {MELON_PATCH_HARVEST_DAY_VALUE}
MELON_PATCH_SHEEP_CUT = {MELON_PATCH_SHEEP_CUT_VALUE}


def _shed_tiles(farm):
    size = len(_value(farm, 'tiles', []) or []) or 10
    half = size // 2
    return ((half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half))


def _step_toward(pos, target):
    x, y = int(pos[0]), int(pos[1])
    tx, ty = int(target[0]), int(target[1])
    if x < tx:
        return ['EAST']
    if x > tx:
        return ['WEST']
    if y < ty:
        return ['SOUTH']
    if y > ty:
        return ['NORTH']
    return None


def _patch_job(farm, private, idx, pos, day):
    """One order for a spare hand: plant, water, harvest, or carry to the shed."""
    inventories = list(_value(private, 'inventories', []) or [])
    inv = inventories[idx] if idx < len(inventories) else {{}}
    carrying = int(_value(inv, 'MELON', 0) or 0)
    if carrying > 0:
        sheds = _shed_tiles(farm)
        if tuple(pos) in sheds:
            return ['DROP']
        return _step_toward(pos, sheds[0])

    seeds = _value(private, 'seeds', {{}}) or {{}}
    have_seed = int(_value(seeds, 'MELON', 0) or 0)

    for tile_xy in MELON_PATCH:
        tile = _tile(farm, tile_xy)
        ripe = (isinstance(tile, dict) and tile.get('kind') == 'PLANT'
                and tile.get('crop') == 'MELON')
        if day >= MELON_PATCH_HARVEST_DAY and ripe:
            if int(tile.get('yield_units', 0) or 0) <= 0:
                continue
            return ['HARVEST'] if tuple(pos) == tile_xy else _step_toward(pos, tile_xy)
        if day >= MELON_PATCH_HARVEST_DAY:
            continue
        if tile is None and have_seed > 0 and day >= MELON_PATCH_PLANT_DAY:
            return ['PLANT', 'MELON'] if tuple(pos) == tile_xy else _step_toward(pos, tile_xy)
        # Two consecutive dry days turns the tile to weed, and every watered day
        # from age 6 on is another unit of fruit, so water whatever is dry.
        if ripe and not tile.get('watered_today'):
            return ['WATER'] if tuple(pos) == tile_xy else _step_toward(pos, tile_xy)
    return None


_ROUTE_HANDS_PER_DAY = {{}}


def _routed_hands(step):
    """How many hands the recording addresses on this step's DAY.

    Not len(_ROUTE[step]['hands']): that list is 0 long at hour 0 and only 7
    long at hour 1 of day 10, when the roster is 14. Reading it per step made
    this layer hand melon jobs to seven hands the route was relying on, at the
    single busiest moment of the game.
    """
    day = step // 24
    if day not in _ROUTE_HANDS_PER_DAY:
        lo, hi = day * 24, min((day + 1) * 24, len(_ROUTE))
        _ROUTE_HANDS_PER_DAY[day] = max(
            (len(_ROUTE[s].get('hands') or []) for s in range(lo, hi)), default=0)
    return _ROUTE_HANDS_PER_DAY[day]


def _melon_patch(action, obs, step):
    if not MELON_PATCH:
        return action
    day = step // 24
    if day > MELON_PATCH_HARVEST_DAY + 2:
        return action

    seat = _player(obs)
    farm = _farm_view(obs, seat)
    hands = list(_value(farm, 'hands', []) or [])
    routed = _routed_hands(step)
    private = _value(obs, 'private', {{}}) or {{}}
    action = _copy_plan(action)
    market = [list(o) for o in action.get('market') or []]

    # Keep exactly one hand more than the recording addresses.
    if len(hands) <= routed and len(market) < 10:
        market.append(['HIRE'])

    # The recording sells melon on day 10 and then not again until day 20, by
    # which point the market is dead. The patch ripens on day 11, so without
    # this its fruit would sit in the shed for nine days and fetch $1.
    if day >= MELON_PATCH_HARVEST_DAY:
        private_shed = _value(private, 'shed', {{}}) or {{}}
        held = max(0, int(_value(private_shed, 'MELON', 0) or 0))
        if held > 0 and not any(
                len(o) >= 3 and o[0] == 'SELL' and o[1] == 'MELON' for o in market):
            if len(market) < 10:
                market.append(['SELL', 'MELON', held])
    action['market'] = market[:10]

    plan = [list(h or ['PASS']) for h in (action.get('hands') or [])]
    while len(plan) < len(hands):
        plan.append(['PASS'])
    for idx in range(routed, len(hands)):
        # private.inventories is [farmer, *hands], so hand i is at i + 1.
        order = _patch_job(farm, private, idx + 1, hands[idx], day)
        if order:
            plan[idx] = order
    action['hands'] = plan
    return action

#
# The town's eight shops are drawn per episode WITH REPLACEMENT, so how much
# wool and milk the town eats is a per-game fact -- and it is handed to the
# agent in obs.town.unlocked_shops. The recording ignores it and buys the same
# 8 cows and 4 sheep every single game. Over 20 route-vs-route games, WOOL ends
# more than 50 units SHORT at around $240 in 9 of them, while MILK ends 74 units
# LONG at $5 in most. The herd is wrong in both directions at once.
#
# Episode 93781740 is what that costs. The town drew two YARN_STOREs -- single
# product, so two units a tick each -- and wool never fell below $246 all game.
# The opponent ran 8 sheep to our 4 and took $66,063 of wool to our $31,383.
# That one product is a bigger gap than the entire $34,001 match margin.
#
# COW and SHEEP both live on a PASTURE, so this is a rename and nothing more --
# no structure changes, no choreography changes, and PLACE cannot strand an
# animal on the wrong building the way the goose experiment could. Only the
# BUY is a decision; PICKUP and PLACE are corrected to whatever we actually
# hold, so the three can never disagree.
#
# It works, and it is switched OFF, because it wins money and loses games.
# Measured against the stock route over 32 seeds, 128 games:
#
#     PASTURE_TILT None   64/64 wins   our 93,628   theirs 91,222
#     PASTURE_TILT 1.0    54/64 wins   our 94,844   theirs 93,780
#
# In the games where it fires it is worth +$8,500 to +$9,000 and never once
# hurts our own score. It still costs ten wins, because vacating milk hands a
# cow-heavy opponent an uncontested run at it: our score goes up $1,216 and
# theirs goes up $2,558. The reward here is the bank balance but the RANKING is
# win-based, so a change that enriches both sides and the opponent more is a
# losing trade. 0.6, 1.0 and 1.6 all decide identically -- the wool/milk call is
# never close -- so this is the change itself failing, not the threshold.
#
# Left in, wired up and measured rather than deleted, because it is the correct
# response to a sheep-heavy FIELD and the wrong response to a clone. If the
# leaderboard fills with Jince-like builds that contest wool, it becomes right.
# ----------------------------------------------------------------------------
PASTURE_TILT = {PASTURE_TILT_VALUE!r}

# Day 0 buys 4 sheep and a cow before a single shop has opened, so there is
# nothing to react to; the first shop unlocks on day 3. Everything the route
# buys from here on is a live decision.
PASTURE_DECIDE_STEP = 72

_PASTURE_ANIMALS = ('COW', 'SHEEP')
_PASTURE_PRODUCT = {{'COW': 'MILK', 'SHEEP': 'WOOL'}}
_PASTURE_COST = {{'COW': 400, 'SHEEP': 500}}


def _town_rate(obs, item):
    """Units of `item` the town eats per shop tick, from the shops it has opened."""
    town = _value(obs, 'town', {{}}) or {{}}
    rate = 0
    for shop in list(_value(town, 'unlocked_shops', []) or []):
        products = _SHOP_DEMAND.get(shop, ())
        if item in products:
            rate += 2 if len(products) == 1 else 1
    return rate


def _preferred_pasture(obs):
    wool = _town_rate(obs, 'WOOL') * _MKT_PARAMS['WOOL'][0]
    milk = _town_rate(obs, 'MILK') * _MKT_PARAMS['MILK'][0]
    return 'SHEEP' if wool > milk * PASTURE_TILT else 'COW'


def _retarget_pasture(action, obs, step):
    if PASTURE_TILT is None:
        return action

    seat = _player(obs)
    farm = _farm_view(obs, seat)
    private = _value(obs, 'private', {{}}) or {{}}
    shed = _value(private, 'shed', {{}}) or {{}}
    inventories = list(_value(private, 'inventories', []) or [])
    action = _copy_plan(action)

    if step >= PASTURE_DECIDE_STEP:
        want = _preferred_pasture(obs)
        money = float(_value(farm, 'money', 0) or 0)
        for order in action.get('market') or []:
            if (len(order) >= 2 and order[0] == 'BUY_ANIMAL'
                    and order[1] in _PASTURE_ANIMALS and order[1] != want):
                # A sheep costs $100 more than a cow and the route runs its
                # balance down to double digits in the first week. A buy that
                # cannot be afforded is not a worse animal, it is no animal, so
                # only upgrade when the money is already in hand.
                if money >= _PASTURE_COST[want] * (int(order[2]) if len(order) > 2 else 1):
                    order[1] = want

    # PICKUP and PLACE are corrected to what we are actually holding rather than
    # decided again, so a purchase that was retargeted (or refused) still lines
    # up with the animal that reaches the pasture.
    units = [('farmer', action.get('farmer'))]
    units += [(i, h) for i, h in enumerate(action.get('hands') or [])]
    for idx, (_slot, unit) in enumerate(units):
        if not unit or len(unit) < 2 or unit[1] not in _PASTURE_ANIMALS:
            continue
        if unit[0] == 'PICKUP':
            if int(_value(shed, unit[1], 0) or 0) <= 0:
                other = next((a for a in _PASTURE_ANIMALS
                              if int(_value(shed, a, 0) or 0) > 0), None)
                if other:
                    unit[1] = other
        elif unit[0] == 'PLACE':
            inv = inventories[idx] if idx < len(inventories) else {{}}
            if int(_value(inv, unit[1], 0) or 0) <= 0:
                other = next((a for a in _PASTURE_ANIMALS
                              if int(_value(inv, a, 0) or 0) > 0), None)
                if other:
                    unit[1] = other
    return action


# Applied here, not next to its definition: the edits read MELON_PATCH and
# CARROT_SWAP, which are declared by layers further down the file.
_apply_route_edits()
'''

anchor = "\n\ndef agent(obs):"
assert anchor in combined, "route_agent.py has no agent() to anchor against"
combined = combined.replace(anchor, MARKET_LAYER + HERD_LAYER + anchor, 1)

OLD_CALL = "        action = _final_drop_cash(obs, action, step)"
NEW_CALL = ("        action = _final_drop_cash(obs, action, step)\n"
            "        action = _retarget_pasture(action, obs, step)\n"
            "        action = _melon_patch(action, obs, step)\n"
            "        action = _eager_sell(action, obs, step)")
assert OLD_CALL in combined, "agent() body does not match the expected shape"
combined = combined.replace(OLD_CALL, NEW_CALL, 1)

# The edits have to be re-read per game, not per import, or a sweep that sets
# one between games would play the previous game's recording.
OLD_HEAD = "    try:\n        step = min(max(0, int("
NEW_HEAD = "    try:\n        _apply_route_edits()\n        step = min(max(0, int("
assert OLD_HEAD in combined, "agent() prologue does not match the expected shape"
combined = combined.replace(OLD_HEAD, NEW_HEAD, 1)

# _mkt_shape needs math; the route imports base64/copy/json/zlib only.
assert combined.startswith('"""') or "import base64" in combined
combined = combined.replace("import base64", "import base64\nimport math", 1)

header = (
    '"""V14 route, adapted to the 1.32.7 market.\n\n'
    f'  * premium-sale preemption widened from 1 step to {LOOKAHEAD_VALUE}\n'
    f'  * the {len(CARROT_SWAP_VALUE)} end-of-season wheat plantings the schedule lifts at age 3\n'
    f'    grown as CARROT instead -- nobody in a field of route clones grows\n'
    f'    carrots, so the town ends 400 units short of them\n'
    f'  * CARROT/TOMATO/EGG sold off the real price ladder while a unit still\n'
    f'    fetches {EAGER_FLOOR_FRAC_VALUE!r} x base; the recording has no SELL order for any of\n'
    f'    the three, so this can only add sales, never retime the tuned ones\n\n'
    'See kernels/build_combined.py for what was and was not combined, and why."""\n'
)
combined = header + combined.split('"""', 2)[2].lstrip("\n")

out = os.path.join(os.path.dirname(HERE), "agent_combined.py")
io.open(out, "w", encoding="utf-8", newline="").write(combined)
print(f"wrote {out}  LOOKAHEAD={LOOKAHEAD_VALUE}  "
      f"EAGER_FLOOR_FRAC={EAGER_FLOOR_FRAC_VALUE!r}  HERD_SWAP={HERD_SWAP_VALUE}  "
      f"CARROT_SWAP={len(CARROT_SWAP_VALUE)} plantings  PASTURE_TILT={PASTURE_TILT_VALUE!r}  "
      f"MELON_PATCH={len(MELON_PATCH_VALUE)} tiles")
