import sys

import main as base


PASS_RESPONSE = {"farmer": ["PASS"], "hands": [], "market": []}


def run_strategy(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    pressure = base.estimate_opponent_pressure(obs)
    roles = build_role_plan(obs, me, pressure)
    jobs = base.build_jobs(obs, me, private, roles, pressure)
    assignments = base.assign_jobs(obs, me, private, jobs)
    market_orders = build_market_orders(obs, me, private, roles, pressure)

    workers = [tuple(me["farmer"])] + [tuple(hand) for hand in me.get("hands", [])]
    inventories = private.get("inventories", [])
    actions = []
    for index, worker in enumerate(workers):
        inventory = inventories[index] if index < len(inventories) else {}
        actions.append(base.action_for_job(worker, inventory, assignments.get(index), len(me["tiles"])))

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": market_orders[:base.MAX_MARKET_ORDERS],
    }


def build_role_plan(obs, me, pressure):
    day = obs.get("day", 0)
    quadrant_count = len(me.get("unlocked_quadrants", []))
    prices = obs["market"]["prices"]

    owned_tiles = []
    for y, row in enumerate(me["tiles"]):
        for x, tile in enumerate(row):
            if tile != "LOCKED":
                owned_tiles.append((x, y))

    owned_tiles.sort(key=lambda pos: (base.distance_to_shed(pos, len(me["tiles"])), pos[1], pos[0]))
    crop_mix = crop_targets(day, len(owned_tiles), quadrant_count, prices, pressure)
    animal_plan = animal_targets(day, quadrant_count)

    roles = {pos: "CARROT" for pos in owned_tiles}
    remaining = list(owned_tiles)

    for pos in base.take_front(remaining, animal_plan["COW"]):
        roles[pos] = "PASTURE_COW"
    for pos in base.take_front(remaining, animal_plan["SHEEP"]):
        roles[pos] = "PASTURE_SHEEP"
    for pos in base.take_front(remaining, crop_mix["WHEAT"]):
        roles[pos] = "WHEAT"
    for pos in base.take_front(remaining, crop_mix["STRAWBERRY"]):
        roles[pos] = "STRAWBERRY"
    for pos in base.take_back(remaining, crop_mix["MELON"]):
        roles[pos] = "MELON"
    for pos in base.take_front(remaining, crop_mix["TOMATO"]):
        roles[pos] = "TOMATO"

    return roles


def crop_targets(day, owned_count, quadrant_count, prices, pressure):
    if day < 6:
        wheat = min(3, max(2, owned_count // 12))
        melon = 0 if day < 3 else min(2, max(1, owned_count // 14))
        return {
            "WHEAT": wheat,
            "CARROT": max(0, owned_count - wheat - melon),
            "STRAWBERRY": 0,
            "TOMATO": 0,
            "MELON": melon,
        }

    wheat = 3 if quadrant_count == 1 else 4
    wheat = max(2, min(wheat, owned_count // 5))

    melon = 4 if quadrant_count == 1 else 7
    strawberry = 0
    tomato = 0

    if quadrant_count >= 2 or day >= 10:
        strawberry = 7 if quadrant_count == 2 else 11
    if quadrant_count >= 3 or day >= 16:
        tomato = 2 if quadrant_count == 3 else 4

    if prices.get("MELON", base.CROPS["MELON"]["base_price"]) >= 220:
        melon += 1
    if prices.get("STRAWBERRY", base.CROPS["STRAWBERRY"]["base_price"]) >= 145:
        strawberry += 2

    # Keep this opponent committed to premium crops, but not suicidal.
    melon -= min(2, int(pressure["MELON"] / 10))
    strawberry -= min(2, int(pressure["STRAWBERRY"] / 10))
    tomato -= min(1, int(pressure["TOMATO"] / 12))

    if day >= 22:
        melon = max(2, melon - 2)
        strawberry = max(4, strawberry - 3)
        tomato = max(0, tomato - 1)

    melon = max(2 if day < 18 else 1, melon)
    strawberry = max(0, strawberry)
    tomato = max(0, tomato)

    reserved = wheat + strawberry + tomato + melon
    if reserved > owned_count and reserved > 0:
        scale = owned_count / reserved
        wheat = max(2, int(wheat * scale))
        strawberry = int(strawberry * scale)
        tomato = int(tomato * scale)
        melon = max(1, int(melon * scale))

    carrot = max(0, owned_count - wheat - strawberry - tomato - melon)
    return {
        "WHEAT": wheat,
        "CARROT": carrot,
        "STRAWBERRY": strawberry,
        "TOMATO": tomato,
        "MELON": melon,
    }


def animal_targets(day, quadrant_count):
    if quadrant_count < 2 or day < 12:
        return {"COW": 0, "SHEEP": 0}
    if quadrant_count == 2 and day < 18:
        return {"COW": 2, "SHEEP": 2}
    if quadrant_count == 3 and day < 22:
        return {"COW": 3, "SHEEP": 3}
    return {"COW": 3, "SHEEP": 4}


def build_market_orders(obs, me, private, roles, pressure):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    prices = obs["market"]["prices"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    money = int(me.get("money", 0))
    orders = []

    current_load = base.shed_load(shed)
    for item, count in sorted(shed.items(), key=lambda pair: sell_priority(pair[0], prices, day), reverse=True):
        if count <= 0:
            continue
        reserve = reserve_price(item, day, current_load)
        if prices.get(item, 0) >= reserve or day >= base.TOTAL_DAYS - 2:
            orders.append(["SELL", item, int(count)])

    planned_spend = 0
    if hour == 0:
        desired_hands = desired_hand_count(me, roles)
        current_hands = len(me.get("hands", []))
        hires_today = me.get("hires_today", 0)
        hire_needed = max(0, desired_hands - max(current_hands, hires_today))
        projected_money = money - base.reserved_seed_budget(roles, private)

        for extra_index in range(hire_needed):
            cost = base.fib_cost(hires_today + extra_index + 1)
            if projected_money - cost < 50:
                break
            projected_money -= cost
            planned_spend += cost
            orders.append(["HIRE"])

        land_cost = base.next_land_cost(me)
        if should_buy_land(day, money - planned_spend, land_cost):
            planned_spend += land_cost
            orders.append(["BUY_LAND"])

        wheat_deficit = desired_wheat_buffer(me, private) - base.total_accessible_items(me, private).get("WHEAT", 0)
        if wheat_deficit > 0 and money - planned_spend > prices.get("WHEAT", 25) * wheat_deficit + 50:
            buy_amount = min(16, wheat_deficit)
            planned_spend += prices.get("WHEAT", 25) * buy_amount
            orders.append(["BUY_PRODUCT", "WHEAT", int(buy_amount)])

        for animal, amount in desired_animal_buys(me, private, roles):
            for _ in range(amount):
                cost = base.ANIMALS[animal]["cost"]
                if money - planned_spend < cost + 50:
                    break
                planned_spend += cost
                orders.append(["BUY_ANIMAL", animal, 1])

    budget = max(0, money - planned_spend - 40)
    for crop, deficit in prioritized_seed_orders(me, roles, seeds, prices, pressure, day):
        if deficit <= 0 or budget < base.CROPS[crop]["seed_cost"]:
            continue
        affordable = min(deficit, budget // base.CROPS[crop]["seed_cost"])
        if affordable <= 0:
            continue
        budget -= affordable * base.CROPS[crop]["seed_cost"]
        orders.append(["BUY_SEED", crop, int(affordable)])
        if len(orders) >= base.MAX_MARKET_ORDERS:
            break

    return orders[:base.MAX_MARKET_ORDERS]


def prioritized_seed_orders(me, roles, seeds, prices, pressure, day):
    empty_counts = base.empty_tiles_by_role(me, roles)
    priority = ["MELON", "STRAWBERRY", "WHEAT", "CARROT", "TOMATO"]
    items = []
    for crop in priority:
        needed = empty_counts.get(crop, 0)
        have = seeds.get(crop, 0)
        deficit = max(0, needed - have)
        if deficit <= 0:
            continue
        if day >= base.TOTAL_DAYS - base.CROPS[crop]["first_day"]:
            continue
        score = plant_value(crop, prices, pressure, day)
        items.append((score, crop, deficit))
    items.sort(reverse=True)
    return [(crop, deficit) for score, crop, deficit in items if score > 0]


def plant_value(crop, prices, pressure, day):
    base_value = base.plant_value(crop, prices, pressure, day, 0)
    if crop == "MELON":
        return base_value * 1.35
    if crop == "STRAWBERRY":
        return base_value * 1.20
    if crop == "CARROT":
        return base_value * 0.85
    return base_value


def desired_animal_buys(me, private, roles):
    target = {"COW": 0, "SHEEP": 0}
    for role in roles.values():
        if role == "PASTURE_COW":
            target["COW"] += 1
        elif role == "PASTURE_SHEEP":
            target["SHEEP"] += 1

    current = {"COW": 0, "SHEEP": 0}
    for row in me["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and tile.get("animal") in current:
                current[tile["animal"]] += 1

    total_items = base.total_accessible_items(me, private)
    orders = []
    for animal in ("COW", "SHEEP"):
        available = current[animal] + total_items.get(animal, 0)
        deficit = max(0, target[animal] - available)
        if deficit > 0:
            orders.append((animal, min(deficit, 2)))
    return orders


def desired_wheat_buffer(me, private):
    animals = 0
    for row in me["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and tile.get("animal"):
                animals += 1
    return max(8, animals * 2)


def desired_hand_count(me, roles):
    quadrants = len(me.get("unlocked_quadrants", []))
    target = 4
    if quadrants >= 2:
        target += 1
    if quadrants >= 3:
        target += 1
    if quadrants >= 4:
        target += 1
    pasture_roles = sum(1 for role in roles.values() if role.startswith("PASTURE_"))
    if pasture_roles >= 4:
        target += 1
    return min(8, target)


def should_buy_land(day, available_money, land_cost):
    if not land_cost:
        return False
    if day < 2 or day > 22:
        return False
    buffer = 650 if day < 8 else 900
    return available_money >= land_cost + buffer


def reserve_price(item, day, load):
    base_price = base.base_price_for_item(item)
    fraction = base.RESERVE_FRAC.get(item, 0.4)
    days_left = base.TOTAL_DAYS - day

    if item == "MELON":
        fraction *= 0.82
    elif item == "STRAWBERRY":
        fraction *= 0.88
    elif item in ("MILK", "WOOL"):
        fraction *= 1.05

    if days_left <= 6:
        fraction *= 0.8
    if days_left <= 3:
        fraction *= 0.45
    if load > 0.75:
        fraction *= 0.65
    if days_left <= 2:
        return 0.0
    return base_price * fraction


def sell_priority(item, prices, day):
    base_price = base.base_price_for_item(item)
    score = prices.get(item, base_price) / max(1, base_price)
    if item == "MELON":
        score += 1.5
    elif item == "STRAWBERRY":
        score += 1.0
    elif item in ("MILK", "WOOL"):
        score += 0.4
    if base.TOTAL_DAYS - day <= 5:
        score += 0.8
    return score


def agent(obs):
    try:
        return run_strategy(obs)
    except Exception as exc:  # pragma: no cover
        print(f"STRONG OPPONENT ERROR: {exc}", file=sys.stderr)
        return PASS_RESPONSE
