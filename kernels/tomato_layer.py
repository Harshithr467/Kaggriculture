
# ---------------------------------------------------------------------------
# Tomato programme: a crew, not a crop swap.
#
# The public v9/4 notebook documents tomatoes as its largest unsolved hole --
# the farms that beat it hold ~10 tomato tiles by day 20 while it holds ~1.6 --
# and reports three failed attempts: a tomato overlay on the route's wheat
# tiles (0 gained / 85 lost), a 20-tile patch on new land (0 / 56, "the crews
# cannot water 20 more tiles"), and loosening the existing gate (+4 / -11).
# Its conclusion: "a tomato program needs a different labour plan, not just a
# different crop choice."
#
# This layer supplies the labour instead of borrowing it, on three measured
# facts:
#
#  1. FERTILIZE doubles an ongoing crop's output. _daily_refresh_plants adds
#     `2 if fertilized else 1` per production event, where `fertilized` also
#     requires the tile to have been watered that day. Measured on one tile
#     planted day 12: TOMATO 4 -> 8 units, STRAWBERRY 4 -> 8. Non-ongoing crops
#     gain far less through the WATER path (WHEAT 3 -> 4, CARROT 2 -> 3, MELON
#     none). So a fertilized tomato tile is worth two unfertilized ones, which
#     halves the tile count -- and the labour -- for a given yield.
#
#  2. The tape is labour-bound, not cash-bound. It caps at 11 hands from day 10
#     while holding 19k on day 12 and 80k on day 26, and idles under 5% of its
#     actions from day 15 on. Hands cost fib(n) with farmHandCostMult 1, so the
#     12th, 13th and 14th hands of a day cost 144, 233 and 377 -- against ~640
#     for one fertilized tomato tile's output.
#
#  3. Nothing consumes FERTILIZER. No shop lists it and TOWN_CENTER_PRODUCTS
#     excludes it, so the surplus the animals generate is free.
#
# The hands this layer hires are ones the tape never asked for, and they work
# tiles the tape never planted. The tape's own crew and schedule are untouched:
# we only fill action slots past its hand count, and only append market orders.
# ---------------------------------------------------------------------------

TOM_ENABLE = True
TOM_START_DAY = 15          # begin hiring and planting
TOM_TILES = 12              # target tomato tiles
TOM_MAX_HANDS = 14          # hire up to this many hands total
TOM_CASH_RESERVE = 6000     # never hire or buy seed below this
TOM_SEED_BATCH = 12
TOM_FERT_CARRY = 3          # fertilizer a new hand picks up before leaving the shed
TOM_LAST_PLANT_DAY = 19     # planting later than this cannot reach 4 production days
TOM_SELL_FROM_DAY = 23

_TOM_PARENT = agent
del agent

_TOM_STATE = {}


def _tom_state(seat):
    st = _TOM_STATE.get(seat)
    if st is None or st.get("_seat") != seat:
        st = {"_seat": seat, "mine": set(), "base_hands": None, "bought": 0}
        _TOM_STATE[seat] = st
    return st


def _tom_step_toward(pos, target):
    """One orthogonal step from pos toward target; None when already there."""
    px, py = pos[0], pos[1]
    tx, ty = target
    if px == tx and py == ty:
        return None
    if px != tx:
        return "EAST" if tx > px else "WEST"
    return "SOUTH" if ty > py else "NORTH"


def _tom_shed_tiles(n):
    half = n // 2
    return [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]


def _tomato_layer(action, obs):
    seat = int(obs.get("player", 0))
    st = _tom_state(seat)
    step = int(obs["step"])
    day, hour = step // 24, step % 24
    farm = obs["farms"][seat]
    priv = obs["private"]
    tiles = farm["tiles"]
    size = len(tiles)
    money = farm.get("money", 0)
    hands = farm.get("hands") or []

    # The tape's own crew size, frozen the first time we look. Everything past
    # this index is ours; everything below it we never touch.
    if st["base_hands"] is None:
        if day < TOM_START_DAY:
            st["base_hands"] = len(hands)
            return action
        st["base_hands"] = len(hands)
    base = st["base_hands"]
    if day < TOM_START_DAY:
        st["base_hands"] = max(base, len(hands))
        return action

    orders = action.setdefault("market", [])
    room = lambda: len(orders) < 10

    # ---- seeds. PLANT consumes private["seeds"] directly, so no pickup needed.
    seeds = (priv.get("seeds") or {}).get("TOMATO", 0)
    if (day <= TOM_LAST_PLANT_DAY and seeds < TOM_SEED_BATCH
            and st["bought"] < TOM_SEED_BATCH * 2
            and money > TOM_CASH_RESERVE + 50 * TOM_SEED_BATCH and room()):
        want = TOM_SEED_BATCH - seeds
        orders.append(["BUY_SEED", "TOMATO", want])
        st["bought"] += want

    # ---- crew. Hire only past the tape's cap, and only while cash is deep.
    if (hour < 20 and len(hands) < TOM_MAX_HANDS
            and money > TOM_CASH_RESERVE and day <= 29 and room()):
        orders.append(["HIRE"])

    # ---- find our tomato tiles and the empty ground we may plant on
    tomato, empty = [], []
    for y in range(size):
        for x in range(size):
            t = tiles[y][x]
            if isinstance(t, dict):
                if t.get("crop") == "TOMATO":
                    tomato.append((x, y, t))
            elif t is None:
                empty.append((x, y))
    st["mine"] = {(x, y) for x, y, _ in tomato}

    # ---- sell what we hold; the book is scarce because nobody plants tomatoes
    shed_tom = (priv.get("shed") or {}).get("TOMATO", 0)
    if shed_tom > 0 and day >= TOM_SELL_FROM_DAY and room():
        if not any(o[:2] == ["SELL", "TOMATO"] for o in orders if len(o) > 1):
            orders.append(["SELL", "TOMATO", shed_tom])

    # ---- our hands: indices base..len(hands)-1
    hand_actions = action.setdefault("hands", [])
    while len(hand_actions) < len(hands):
        hand_actions.append(["PASS"])
    inventories = priv.get("inventories") or []
    shed_set = set(_tom_shed_tiles(size))

    # tiles that want work today, most urgent first
    need = []
    for x, y, t in tomato:
        if t.get("yield_units", 0) > 0:
            need.append((0, x, y, "HARVEST"))
        elif not t.get("watered_today"):
            need.append((1, x, y, "WATER"))
        elif t.get("fertilized_until_day", -1) < day:
            need.append((2, x, y, "FERTILIZE"))
    need.sort()

    claimed = set()
    for i in range(base, len(hands)):
        pos = hands[i]
        if not pos:
            continue
        inv = inventories[i + 1] if i + 1 < len(inventories) else {}
        here = tiles[pos[1]][pos[0]] if 0 <= pos[1] < size and 0 <= pos[0] < size else None
        cell = (pos[0], pos[1])

        # a fresh hand stands on the shed: take fertilizer before walking out
        if cell in shed_set and inv.get("FERTILIZER", 0) < TOM_FERT_CARRY:
            if (priv.get("shed") or {}).get("FERTILIZER", 0) > 0:
                hand_actions[i] = ["PICKUP", "FERTILIZER", TOM_FERT_CARRY]
                continue

        # standing on one of our tomato tiles -> work it
        if isinstance(here, dict) and here.get("crop") == "TOMATO":
            if here.get("yield_units", 0) > 0:
                hand_actions[i] = ["HARVEST"]
                continue
            if not here.get("watered_today"):
                hand_actions[i] = ["WATER"]
                continue
            if here.get("fertilized_until_day", -1) < day and inv.get("FERTILIZER", 0) > 0:
                hand_actions[i] = ["FERTILIZE"]
                continue

        # empty ground and seeds in hand -> plant, while the crop can still finish
        if (here is None and cell not in claimed and day <= TOM_LAST_PLANT_DAY
                and len(tomato) + len(claimed) < TOM_TILES
                and (priv.get("seeds") or {}).get("TOMATO", 0) > len(claimed)):
            hand_actions[i] = ["PLANT", "TOMATO"]
            claimed.add(cell)
            continue

        # otherwise walk to the most urgent job, or to the nearest empty tile
        target = None
        for _, x, y, _op in need:
            if (x, y) not in claimed:
                target = (x, y)
                claimed.add((x, y))
                break
        if target is None and day <= TOM_LAST_PLANT_DAY and len(tomato) < TOM_TILES and empty:
            empty.sort(key=lambda e: abs(e[0] - pos[0]) + abs(e[1] - pos[1]))
            for e in empty:
                if e not in claimed:
                    target = e
                    claimed.add(e)
                    break
        if target is None:
            hand_actions[i] = ["PASS"]
            continue
        move = _tom_step_toward(pos, target)
        hand_actions[i] = [move] if move else ["PASS"]

    return action


def agent(obs, configuration=None):
    action = _TOM_PARENT(obs, configuration)
    if not TOM_ENABLE:
        return action
    try:
        return _tomato_layer(action, obs)
    except Exception:
        # A broken overlay must never cost a game the tape would have won.
        return action


agent = globals().pop('agent')
