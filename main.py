import sys


TOTAL_DAYS = 30
TURNS_PER_DAY = 24
TRAVEL_COST = 8.0
MAX_MARKET_ORDERS = 10
PASS_RESPONSE = {"farmer": ["PASS"], "hands": [], "market": []}

CROPS = {
    "WHEAT": {
        "seed_cost": 10,
        "base_price": 25,
        "first_day": 2,
        "max_day": 4,
        "max_yield": 6,
        "ongoing": False,
    },
    "CARROT": {
        "seed_cost": 20,
        "base_price": 35,
        "first_day": 2,
        "max_day": 3,
        "max_yield": 4,
        "ongoing": False,
    },
    "TOMATO": {
        "seed_cost": 50,
        "base_price": 60,
        "first_day": 8,
        "max_day": 11,
        "max_yield": 4,
        "ongoing": True,
    },
    "STRAWBERRY": {
        "seed_cost": 100,
        "base_price": 120,
        "first_day": 10,
        "max_day": 16,
        "max_yield": 4,
        "ongoing": True,
    },
    "MELON": {
        "seed_cost": 80,
        "base_price": 250,
        "first_day": 10,
        "max_day": 10,
        "max_yield": 6,
        "ongoing": False,
    },
}

ANIMALS = {
    "COW": {"cost": 400, "product": "MILK", "structure": "PASTURE", "base_target": 2},
    "SHEEP": {"cost": 500, "product": "WOOL", "structure": "PASTURE", "base_target": 2},
}

LAND_COSTS = [1000, 2000, 4000]
SEED_PRIORITY = ["CARROT", "WHEAT", "STRAWBERRY", "MELON", "TOMATO"]
PRODUCT_BASE_PRICE = {"EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100}
PRESSURE_SCALE = {"WHEAT": 12.0, "CARROT": 10.0, "TOMATO": 8.0, "STRAWBERRY": 6.0, "MELON": 5.0}
GLUT_SENSITIVITY = {"WHEAT": 0.15, "CARROT": 0.30, "TOMATO": 0.55, "STRAWBERRY": 0.95, "MELON": 1.15}
ENDGAME_DAYS = {"WHEAT": 2, "CARROT": 2, "TOMATO": 4, "STRAWBERRY": 5, "MELON": 6}

RESERVE_FRAC = {
    "WHEAT": 0.45,
    "CARROT": 0.40,
    "TOMATO": 0.55,
    "STRAWBERRY": 0.70,
    "MELON": 0.78,
    "MILK": 0.65,
    "WOOL": 0.65,
    "FERTILIZER": 0.35,
}


def run_strategy(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    pressure = estimate_opponent_pressure(obs)
    roles = build_role_plan(obs, me, pressure)
    jobs = build_jobs(obs, me, private, roles, pressure)
    assignments = assign_jobs(me, jobs)
    market_orders = build_market_orders(obs, me, private, roles, pressure)

    workers = [tuple(me["farmer"])] + [tuple(hand) for hand in me.get("hands", [])]
    inventories = private.get("inventories", [])
    actions = []
    for index, worker in enumerate(workers):
        inventory = inventories[index] if index < len(inventories) else {}
        actions.append(action_for_job(worker, inventory, assignments.get(index), len(me["tiles"])))

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": market_orders[:MAX_MARKET_ORDERS],
    }


def estimate_opponent_pressure(obs):
    player = obs["player"]
    day = obs.get("day", 0)
    pressure = {crop: 0.0 for crop in CROPS}

    for farm_index, farm in enumerate(obs["farms"]):
        if farm_index == player:
            continue
        for row in farm["tiles"]:
            for tile in row:
                if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
                    continue
                crop = tile.get("crop")
                if crop not in CROPS:
                    continue
                age = day - tile.get("planted_day", day)
                pressure[crop] += imminent_supply_score(tile, crop, age)

    return pressure


def imminent_supply_score(tile, crop, age):
    data = CROPS[crop]
    yield_units = tile.get("yield_units", 0)

    if data["ongoing"]:
        if yield_units > 0:
            return 1.0 + min(2.0, yield_units / 2.0)
        if age >= data["first_day"] - 1:
            return 0.5
        return 0.0

    if yield_units > 0:
        return 1.0 + min(2.0, yield_units / 3.0)
    if age >= data["max_day"] - 1:
        return 0.8
    if age >= data["first_day"]:
        return 0.35
    return 0.0


def build_role_plan(obs, me, pressure):
    day = obs.get("day", 0)
    quadrant_count = len(me.get("unlocked_quadrants", []))
    prices = obs["market"]["prices"]

    owned_tiles = []
    for y, row in enumerate(me["tiles"]):
        for x, tile in enumerate(row):
            if tile != "LOCKED":
                owned_tiles.append((x, y))

    owned_tiles.sort(key=lambda pos: (distance_to_shed(pos, len(me["tiles"])), pos[1], pos[0]))
    crop_mix = crop_targets(day, len(owned_tiles), quadrant_count, prices, pressure)
    animal_plan = animal_targets(day, quadrant_count)

    roles = {pos: "CARROT" for pos in owned_tiles}
    remaining = list(owned_tiles)

    for pos in take_front(remaining, animal_plan["COW"]):
        roles[pos] = "PASTURE_COW"
    for pos in take_front(remaining, animal_plan["SHEEP"]):
        roles[pos] = "PASTURE_SHEEP"
    for pos in take_front(remaining, crop_mix["WHEAT"]):
        roles[pos] = "WHEAT"
    for pos in take_front(remaining, crop_mix["STRAWBERRY"]):
        roles[pos] = "STRAWBERRY"
    for pos in take_front(remaining, crop_mix["TOMATO"]):
        roles[pos] = "TOMATO"
    for pos in take_back(remaining, crop_mix["MELON"]):
        roles[pos] = "MELON"

    return roles


def crop_targets(day, owned_count, quadrant_count, prices, pressure):
    if day < 4:
        wheat = min(4, max(2, owned_count // 10))
        return {
            "WHEAT": wheat,
            "CARROT": max(0, owned_count - wheat),
            "STRAWBERRY": 0,
            "TOMATO": 0,
            "MELON": min(2, max(0, owned_count // 12)),
        }

    wheat = 5 if quadrant_count == 1 else 7
    wheat = max(3, min(wheat, owned_count // 4))

    melon = 0
    if day >= 5:
        melon = 3 if quadrant_count == 1 else 5
        if day >= 16:
            melon -= 1
        if day >= 20:
            melon -= 2

    strawberry = 0
    if quadrant_count >= 2 or day >= 9:
        strawberry = 8 if quadrant_count == 2 else 12
        if prices.get("STRAWBERRY", CROPS["STRAWBERRY"]["base_price"]) >= 150:
            strawberry += 2

    tomato = 0
    if quadrant_count >= 3 or day >= 14:
        tomato = 4 if quadrant_count == 3 else 6

    strawberry -= min(6, int(pressure["STRAWBERRY"] / PRESSURE_SCALE["STRAWBERRY"]))
    melon -= min(3, int(pressure["MELON"] / PRESSURE_SCALE["MELON"]))
    tomato -= min(3, int(pressure["TOMATO"] / PRESSURE_SCALE["TOMATO"]))

    if prices.get("MELON", CROPS["MELON"]["base_price"]) <= 180:
        melon -= 1
    if day >= 23:
        strawberry -= 3
        tomato -= 2

    wheat = max(2, wheat)
    strawberry = max(0, strawberry)
    tomato = max(0, tomato)
    melon = max(0, melon)

    reserved = wheat + strawberry + tomato + melon
    if reserved > owned_count and reserved > 0:
        scale = owned_count / reserved
        wheat = max(2, int(wheat * scale))
        strawberry = int(strawberry * scale)
        tomato = int(tomato * scale)
        melon = max(0, owned_count - wheat - strawberry - tomato)

    return {
        "WHEAT": wheat,
        "CARROT": max(0, owned_count - wheat - strawberry - tomato - melon),
        "STRAWBERRY": strawberry,
        "TOMATO": tomato,
        "MELON": melon,
    }


def animal_targets(day, quadrant_count):
    if quadrant_count < 2 or day < 8:
        return {"COW": 0, "SHEEP": 0}
    if quadrant_count == 2 and day < 15:
        return {"COW": 2, "SHEEP": 2}
    return {"COW": 3, "SHEEP": 3}


def build_jobs(obs, me, private, roles, pressure):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    days_left = TOTAL_DAYS - day
    prices = obs["market"]["prices"]
    jobs = []

    inventories = private.get("inventories", [])
    total_items = total_accessible_items(me, private)
    seed_stock = {crop: private.get("seeds", {}).get(crop, 0) for crop in CROPS}
    plant_candidates = []

    for y, row in enumerate(me["tiles"]):
        for x, tile in enumerate(row):
            if tile == "LOCKED":
                continue

            pos = (x, y)
            role = roles.get(pos, "CARROT")

            if tile is None:
                if role.startswith("PASTURE_"):
                    jobs.append(make_job(pos, ["BUILD_PASTURE"], 150.0 if day < 18 else 90.0))
                else:
                    crop = role
                    value = plant_value(crop, prices, pressure, day, hour)
                    if value > 0:
                        plant_candidates.append((pos, crop, value))
                continue

            if not isinstance(tile, dict):
                continue

            kind = tile.get("kind")
            if kind == "WEED":
                jobs.append(make_job(pos, ["DIG"], 52.0 if day < 12 else 40.0))
                continue

            if kind == "PLANT":
                crop = tile["crop"]
                age = day - tile.get("planted_day", day)
                data = CROPS[crop]
                yield_units = tile.get("yield_units", 0)
                dry = tile.get("consecutive_unwatered", 0)

                if should_harvest(tile, crop, age, day):
                    value = yield_units * prices.get(crop, data["base_price"]) + harvest_bonus(crop, day, days_left)
                    jobs.append(make_job(pos, ["HARVEST"], value))
                    continue

                if should_water(tile, crop, age):
                    jobs.append(make_job(pos, ["WATER"], water_job_value(crop, age, dry, day, days_left)))

                if yield_units > 0 and data["ongoing"]:
                    value = yield_units * prices.get(crop, data["base_price"]) + harvest_bonus(crop, day, days_left)
                    jobs.append(make_job(pos, ["HARVEST"], value))

                if days_left <= 2 and yield_units == 0 and age >= data["first_day"]:
                    jobs.append(make_job(pos, ["DIG"], 24.0))
                continue

            if kind == "PASTURE":
                desired_animal = role.split("_", 1)[1] if role.startswith("PASTURE_") else None
                animal = tile.get("animal")
                if animal is None:
                    if desired_animal and total_items.get(desired_animal, 0) > 0:
                        jobs.append(make_job(pos, ["PLACE", desired_animal, 1], 260.0, requires={desired_animal: 1}))
                    continue

                if not tile.get("fed_today", False):
                    jobs.append(make_job(pos, ["FEED"], 950.0, requires={"WHEAT": 1}))
                if not tile.get("cared_today", False):
                    jobs.append(make_job(pos, ["CARE"], 180.0))
                if tile.get("fertilizer_available", False):
                    jobs.append(make_job(pos, ["COLLECT_FERTILIZER"], 135.0))
                if tile.get("yield_units", 0) > 0:
                    product = ANIMALS[animal]["product"]
                    value = tile.get("yield_units", 0) * prices.get(product, PRODUCT_BASE_PRICE[product]) + 80.0
                    jobs.append(make_job(pos, ["HARVEST"], value))

    if hour <= TURNS_PER_DAY - 3:
        plant_candidates.sort(key=lambda item: (-item[2], item[0][1], item[0][0]))
        for pos, crop, value in plant_candidates:
            if seed_stock.get(crop, 0) <= 0:
                continue
            seed_stock[crop] -= 1
            jobs.append(make_job(pos, ["PLANT", crop], value))

    return jobs


def total_accessible_items(me, private):
    total = {}
    for item, count in private.get("shed", {}).items():
        total[item] = total.get(item, 0) + count
    for inventory in private.get("inventories", []):
        if not isinstance(inventory, dict):
            continue
        for item, count in inventory.items():
            total[item] = total.get(item, 0) + count
    return total


def should_harvest(tile, crop, age, day):
    data = CROPS[crop]
    yield_units = tile.get("yield_units", 0)
    if yield_units <= 0:
        return False
    if data["ongoing"]:
        return True
    if age >= data["max_day"]:
        return True
    if day >= TOTAL_DAYS - ENDGAME_DAYS.get(crop, 2):
        return True
    return False


def should_water(tile, crop, age):
    data = CROPS[crop]
    if tile.get("watered_today", False):
        return False
    if data["ongoing"]:
        return tile.get("consecutive_unwatered", 0) >= 1 or age < data["first_day"]
    return True


def harvest_bonus(crop, day, days_left):
    bonus = 30.0
    if crop == "CARROT" and day < 6:
        bonus += 20.0
    if crop == "MELON":
        bonus += 25.0
    if days_left <= ENDGAME_DAYS.get(crop, 2):
        bonus += 25.0
    return bonus


def water_job_value(crop, age, dry, day, days_left):
    data = CROPS[crop]
    value = 95.0 if dry >= 1 else 50.0
    if not data["ongoing"] and age >= max(1, (data["max_day"] + 1) // 2):
        value += 28.0
    if crop == "CARROT" and day < 6:
        value += 16.0
    if crop == "MELON" and days_left <= 8:
        value += 8.0
    return value


def plant_value(crop, prices, pressure, day, hour):
    data = CROPS[crop]
    if day >= TOTAL_DAYS - data["first_day"]:
        return -1.0

    value = data["max_yield"] * prices.get(crop, data["base_price"]) - data["seed_cost"]
    value *= max(0.25, (TURNS_PER_DAY - hour - 1) / TURNS_PER_DAY)
    value /= 10.0

    if crop == "CARROT" and day < 6:
        value *= 1.55
    elif crop == "WHEAT" and day < 8:
        value *= 1.18
    elif crop == "STRAWBERRY":
        value *= 1.05
    elif crop == "MELON":
        value *= 1.10

    value *= max(0.35, 1.0 - opponent_glut_factor(crop, pressure))

    if day >= TOTAL_DAYS - ENDGAME_DAYS.get(crop, 2):
        value *= 0.25
    elif crop == "MELON" and day >= 18:
        value *= 0.55
    elif crop == "STRAWBERRY" and day >= 22:
        value *= 0.72
    elif crop == "TOMATO" and day >= 23:
        value *= 0.70

    return value


def build_market_orders(obs, me, private, roles, pressure):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    prices = obs["market"]["prices"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    money = int(me.get("money", 0))
    orders = []

    current_load = shed_load(shed)
    for item, count in sorted(shed.items(), key=lambda pair: sell_priority(pair[0], prices, pressure, day), reverse=True):
        if count <= 0:
            continue
        reserve = reserve_price(item, day, current_load, pressure)
        if prices.get(item, 0) >= reserve or day >= TOTAL_DAYS - 2:
            orders.append(["SELL", item, int(count)])

    planned_spend = 0
    if hour == 0:
        desired_hands = desired_hand_count(obs, me, roles)
        current_hands = len(me.get("hands", []))
        hires_today = me.get("hires_today", 0)
        hire_needed = max(0, desired_hands - max(current_hands, hires_today))
        projected_money = money - reserved_seed_budget(roles, private)

        for extra_index in range(hire_needed):
            cost = fib_cost(hires_today + extra_index + 1)
            if projected_money - cost < 100:
                break
            projected_money -= cost
            planned_spend += cost
            orders.append(["HIRE"])

        land_cost = next_land_cost(me)
        if should_buy_land(day, money - planned_spend, land_cost):
            planned_spend += land_cost
            orders.append(["BUY_LAND"])

        wheat_deficit = desired_wheat_buffer(obs, me, private) - total_accessible_items(me, private).get("WHEAT", 0)
        if wheat_deficit > 0 and money - planned_spend > prices.get("WHEAT", 25) * wheat_deficit + 100:
            buy_amount = min(10, wheat_deficit)
            planned_spend += prices.get("WHEAT", 25) * buy_amount
            orders.append(["BUY_PRODUCT", "WHEAT", int(buy_amount)])

        animal_orders = desired_animal_buys(obs, me, private, roles)
        for animal, amount in animal_orders:
            for _ in range(amount):
                cost = ANIMALS[animal]["cost"]
                if money - planned_spend < cost + 100:
                    break
                planned_spend += cost
                orders.append(["BUY_ANIMAL", animal, 1])

    budget = max(0, money - planned_spend - 80)
    for crop, deficit in prioritized_seed_orders(me, roles, seeds, prices, pressure, day):
        if deficit <= 0 or budget < CROPS[crop]["seed_cost"]:
            continue
        affordable = min(deficit, budget // CROPS[crop]["seed_cost"])
        if affordable <= 0:
            continue
        budget -= affordable * CROPS[crop]["seed_cost"]
        orders.append(["BUY_SEED", crop, int(affordable)])
        if len(orders) >= MAX_MARKET_ORDERS:
            break

    return orders[:MAX_MARKET_ORDERS]


def desired_animal_buys(obs, me, private, roles):
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

    total_items = total_accessible_items(me, private)
    orders = []
    for animal in ("COW", "SHEEP"):
        available = current[animal] + total_items.get(animal, 0)
        deficit = max(0, target[animal] - available)
        if deficit > 0:
            orders.append((animal, min(deficit, 2)))
    return orders


def desired_wheat_buffer(obs, me, private):
    animals = 0
    for row in me["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and tile.get("animal"):
                animals += 1
    if animals == 0:
        return 6
    return max(8, animals * 2)


def sell_priority(item, prices, pressure, day):
    base = base_price_for_item(item)
    price = prices.get(item, base)
    score = price / max(1, base)
    if item in CROPS:
        score += opponent_glut_factor(item, pressure)
        if TOTAL_DAYS - day <= ENDGAME_DAYS.get(item, 2):
            score += 1.0
    return score


def prioritized_seed_orders(me, roles, seeds, prices, pressure, day):
    empty_counts = empty_tiles_by_role(me, roles)
    items = []
    for crop in SEED_PRIORITY:
        needed = empty_counts.get(crop, 0)
        have = seeds.get(crop, 0)
        deficit = max(0, needed - have)
        if deficit <= 0:
            continue
        if day >= TOTAL_DAYS - CROPS[crop]["first_day"]:
            continue
        score = plant_value(crop, prices, pressure, day, 0)
        items.append((score, crop, deficit))
    items.sort(reverse=True)
    return [(crop, deficit) for score, crop, deficit in items if score > 0]


def should_buy_land(day, available_money, land_cost):
    if not land_cost:
        return False
    if day < 3 or day > 20:
        return False
    buffer = 700 if day < 8 else 1000
    return available_money >= land_cost + buffer


def desired_hand_count(obs, me, roles):
    quadrant_count = len(me.get("unlocked_quadrants", []))
    day = obs.get("day", 0)
    target = 4 if day < 4 else 5

    if quadrant_count >= 2:
        target += 1
    if quadrant_count >= 3:
        target += 1
    if quadrant_count >= 4:
        target += 1

    pasture_roles = sum(1 for role in roles.values() if role.startswith("PASTURE_"))
    if pasture_roles >= 4:
        target += 1

    return min(8, target)


def reserved_seed_budget(roles, private):
    seeds = private.get("seeds", {})
    needed = 0
    role_counts = {}
    for crop in roles.values():
        if crop in CROPS:
            role_counts[crop] = role_counts.get(crop, 0) + 1
    for crop, count in role_counts.items():
        shortfall = max(0, min(8, count // 4) - seeds.get(crop, 0))
        needed += shortfall * CROPS[crop]["seed_cost"]
    return needed


def empty_tiles_by_role(me, roles):
    counts = {}
    for (x, y), role in roles.items():
        if me["tiles"][y][x] is None and role in CROPS:
            counts[role] = counts.get(role, 0) + 1
    return counts


def reserve_price(item, day, load, pressure):
    base = base_price_for_item(item)
    fraction = RESERVE_FRAC.get(item, 0.40)
    days_left = TOTAL_DAYS - day

    if item in CROPS:
        fraction *= max(0.35, 1.0 - opponent_glut_factor(item, pressure) * 0.7)
        if days_left <= ENDGAME_DAYS.get(item, 2):
            fraction *= 0.35
        elif days_left <= ENDGAME_DAYS.get(item, 2) + 3:
            fraction *= 0.65
    else:
        if days_left <= 3:
            fraction *= 0.45

    if days_left <= 2:
        return 0.0
    if load > 0.75:
        fraction *= 0.6

    return base * fraction


def opponent_glut_factor(crop, pressure):
    return min(1.2, pressure.get(crop, 0.0) / PRESSURE_SCALE[crop]) * GLUT_SENSITIVITY[crop]


def base_price_for_item(item):
    if item in CROPS:
        return CROPS[item]["base_price"]
    return PRODUCT_BASE_PRICE.get(item, 25)


def shed_load(shed):
    return sum(max(0, count) for count in shed.values()) / 100.0


def next_land_cost(me):
    unlocked = len(me.get("unlocked_quadrants", []))
    if unlocked >= 4:
        return None
    return LAND_COSTS[unlocked - 1]


def fib_cost(index):
    a, b = 1, 1
    if index <= 2:
        return 1
    for _ in range(3, index + 1):
        a, b = b, a + b
    return b


def assign_jobs(me, jobs):
    workers = [tuple(me["farmer"])] + [tuple(hand) for hand in me.get("hands", [])]
    if not workers or not jobs:
        return {}

    scored_pairs = {}
    max_per_job = []
    for job_index, job in enumerate(jobs):
        best = 0.0
        for worker_index, worker in enumerate(workers):
            score = job["value"] - manhattan(worker, job["pos"]) * TRAVEL_COST
            if score > 0:
                scored_pairs[(worker_index, job_index)] = score
                best = max(best, score)
        max_per_job.append((best, job_index))

    if not scored_pairs:
        return {}

    job_cap = min(len(jobs), max(len(workers) + 8, len(workers) * 2))
    selected_jobs = [job_index for best, job_index in sorted(max_per_job, reverse=True)[:job_cap] if best > 0]
    if not selected_jobs:
        return {}

    worker_options = {}
    for worker_index in range(len(workers)):
        options = []
        for local_index, job_index in enumerate(selected_jobs):
            score = scored_pairs.get((worker_index, job_index), 0.0)
            if score > 0:
                options.append((score, local_index, job_index))
        options.sort(reverse=True)
        worker_options[worker_index] = options[:8]

    worker_order = sorted(
        range(len(workers)),
        key=lambda idx: (len(worker_options[idx]), -worker_options[idx][0][0] if worker_options[idx] else 0.0),
    )

    memo = {}

    def best_score(order_index, used_mask):
        key = (order_index, used_mask)
        if key in memo:
            return memo[key]
        if order_index >= len(worker_order):
            memo[key] = (0.0, -1)
            return memo[key]

        worker_index = worker_order[order_index]
        best_total = 0.0
        best_choice = -1

        skip_total, _ = best_score(order_index + 1, used_mask)
        best_total = skip_total

        for score, local_index, _job_index in worker_options[worker_index]:
            bit = 1 << local_index
            if used_mask & bit:
                continue
            future_total, _ = best_score(order_index + 1, used_mask | bit)
            total = score + future_total
            if total > best_total:
                best_total = total
                best_choice = local_index

        memo[key] = (best_total, best_choice)
        return memo[key]

    assignments = {}
    used_mask = 0
    for order_index in range(len(worker_order)):
        worker_index = worker_order[order_index]
        _score, choice = best_score(order_index, used_mask)
        if choice < 0:
            continue
        used_mask |= 1 << choice
        assignments[worker_index] = jobs[selected_jobs[choice]]

    return assignments


def action_for_job(worker, inventory, job, board_size):
    if not job:
        return ["PASS"]

    requires = job.get("requires", {})
    for item, count in requires.items():
        if inventory.get(item, 0) < count:
            shed_target = nearest_shed_tile(worker, board_size)
            if worker == shed_target:
                return ["PICKUP", item, count]
            return [step_toward(worker, shed_target)]

    if worker == job["pos"]:
        return job["action"]
    return [step_toward(worker, job["pos"])]


def nearest_shed_tile(worker, board_size):
    return min(shed_tiles(board_size), key=lambda tile: manhattan(worker, tile))


def shed_tiles(board_size):
    half = board_size // 2
    return [
        (half - 1, half - 1),
        (half, half - 1),
        (half - 1, half),
        (half, half),
    ]


def step_toward(src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    if abs(dx) >= abs(dy) and dx != 0:
        return "EAST" if dx > 0 else "WEST"
    if dy != 0:
        return "SOUTH" if dy > 0 else "NORTH"
    return "PASS"


def distance_to_shed(pos, board_size):
    return min(manhattan(pos, tile) for tile in shed_tiles(board_size))


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def take_front(items, count):
    count = max(0, min(count, len(items)))
    chosen = items[:count]
    del items[:count]
    return chosen


def take_back(items, count):
    count = max(0, min(count, len(items)))
    if count == 0:
        return []
    chosen = items[-count:]
    del items[-count:]
    return chosen


def make_job(pos, action, value, requires=None):
    return {"pos": pos, "action": action, "value": value, "requires": requires or {}}


def agent(obs):
    try:
        return run_strategy(obs)
    except Exception as exc:  # pragma: no cover
        print(f"AGENT ERROR: {exc}", file=sys.stderr)
        return PASS_RESPONSE
