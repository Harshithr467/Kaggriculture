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

LAND_COSTS = [1000, 2000, 4000]
SEED_PRIORITY = ["CARROT", "WHEAT", "STRAWBERRY", "MELON", "TOMATO"]
PRODUCT_BASE_PRICE = {"EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100}
PRESSURE_SCALE = {"WHEAT": 12.0, "CARROT": 10.0, "TOMATO": 8.0, "STRAWBERRY": 6.0, "MELON": 5.0}
GLUT_SENSITIVITY = {"WHEAT": 0.15, "CARROT": 0.30, "TOMATO": 0.55, "STRAWBERRY": 0.90, "MELON": 1.10}
ENDGAME_DAYS = {"WHEAT": 2, "CARROT": 2, "TOMATO": 4, "STRAWBERRY": 5, "MELON": 6}

RESERVE_FRAC = {
    "WHEAT": 0.45,
    "CARROT": 0.40,
    "TOMATO": 0.55,
    "STRAWBERRY": 0.70,
    "MELON": 0.78,
    "EGG": 0.45,
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
    actions = [action_for_job(worker, assignments.get(index)) for index, worker in enumerate(workers)]

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
    prices = obs["market"]["prices"]

    owned_tiles = []
    for y, row in enumerate(me["tiles"]):
        for x, tile in enumerate(row):
            if tile != "LOCKED":
                owned_tiles.append((x, y))

    owned_tiles.sort(key=lambda pos: (distance_to_shed(pos, len(me["tiles"])), pos[1], pos[0]))
    targets = crop_targets(day, len(owned_tiles), len(me.get("unlocked_quadrants", [])), prices, pressure)

    roles = {pos: "CARROT" for pos in owned_tiles}
    remaining = list(owned_tiles)

    for pos in take_front(remaining, targets["WHEAT"]):
        roles[pos] = "WHEAT"
    for pos in take_front(remaining, targets["STRAWBERRY"]):
        roles[pos] = "STRAWBERRY"
    for pos in take_front(remaining, targets["TOMATO"]):
        roles[pos] = "TOMATO"
    for pos in take_back(remaining, targets["MELON"]):
        roles[pos] = "MELON"

    return roles


def crop_targets(day, owned_count, quadrant_count, prices, pressure):
    if day < 4:
        wheat = min(3, max(2, owned_count // 10))
        return {
            "WHEAT": wheat,
            "CARROT": max(0, owned_count - wheat),
            "STRAWBERRY": 0,
            "TOMATO": 0,
            "MELON": 0,
        }

    wheat = min(6 if quadrant_count == 1 else 8, max(3, owned_count // 7))
    strawberry = 0 if day < 7 else min(14 if quadrant_count == 1 else 24, max(4, owned_count // 3))
    tomato = 0 if day < 11 else min(6 if quadrant_count == 1 else 10, max(2, owned_count // 8))
    melon = 0 if day < 6 else min(5 if quadrant_count == 1 else 9, max(2, owned_count // 7))

    strawberry += price_signal_bonus("STRAWBERRY", prices)
    melon += price_signal_bonus("MELON", prices)
    tomato += price_signal_bonus("TOMATO", prices)

    strawberry -= min(8, int(pressure["STRAWBERRY"] / PRESSURE_SCALE["STRAWBERRY"]))
    melon -= min(5, int(pressure["MELON"] / PRESSURE_SCALE["MELON"]))
    tomato -= min(4, int(pressure["TOMATO"] / PRESSURE_SCALE["TOMATO"]))

    if day >= 20:
        melon = max(0, melon - 3)
    if day >= 23:
        strawberry = max(0, strawberry - 4)
        tomato = max(0, tomato - 2)

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


def price_signal_bonus(crop, prices):
    base = CROPS[crop]["base_price"]
    price = prices.get(crop, base)
    if price >= base * 1.35:
        return 3
    if price >= base * 1.15:
        return 1
    if price <= base * 0.85:
        return -2
    return 0


def build_jobs(obs, me, private, roles, pressure):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    days_left = TOTAL_DAYS - day
    prices = obs["market"]["prices"]
    jobs = []

    seed_stock = {crop: private.get("seeds", {}).get(crop, 0) for crop in CROPS}
    plant_candidates = []

    for y, row in enumerate(me["tiles"]):
        for x, tile in enumerate(row):
            if tile == "LOCKED":
                continue

            pos = (x, y)
            if tile is None:
                crop = roles.get(pos, "CARROT")
                value = plant_value(crop, prices, pressure, day, hour)
                if value > 0:
                    plant_candidates.append((pos, crop, value))
                continue

            if not isinstance(tile, dict):
                continue

            kind = tile.get("kind")
            if kind == "WEED":
                jobs.append(make_job(pos, ["DIG"], 55.0 if day < 10 else 42.0))
                continue
            if kind != "PLANT":
                continue

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
                value = water_job_value(crop, age, dry, day, days_left)
                jobs.append(make_job(pos, ["WATER"], value))

            if yield_units > 0 and data["ongoing"]:
                value = yield_units * prices.get(crop, data["base_price"]) + harvest_bonus(crop, day, days_left)
                jobs.append(make_job(pos, ["HARVEST"], value))

            if days_left <= 2 and yield_units == 0 and age >= data["first_day"]:
                jobs.append(make_job(pos, ["DIG"], 25.0))

    if hour <= TURNS_PER_DAY - 3:
        plant_candidates.sort(key=lambda item: (-item[2], item[0][1], item[0][0]))
        for pos, crop, value in plant_candidates:
            if seed_stock.get(crop, 0) <= 0:
                continue
            seed_stock[crop] -= 1
            jobs.append(make_job(pos, ["PLANT", crop], value))

    return jobs


def harvest_bonus(crop, day, days_left):
    bonus = 28.0
    if crop == "CARROT" and day < 6:
        bonus += 18.0
    if crop == "WHEAT" and day < 5:
        bonus += 12.0
    if days_left <= ENDGAME_DAYS.get(crop, 3):
        bonus += 25.0
    return bonus


def water_job_value(crop, age, dry, day, days_left):
    data = CROPS[crop]
    value = 90.0 if dry >= 1 else 48.0
    if not data["ongoing"] and age >= max(1, (data["max_day"] + 1) // 2):
        value += 28.0
    if crop == "CARROT" and day < 6:
        value += 15.0
    if crop == "MELON" and days_left <= 8:
        value += 8.0
    return value


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


def plant_value(crop, prices, pressure, day, hour):
    data = CROPS[crop]
    if day >= TOTAL_DAYS - data["first_day"]:
        return -1.0

    value = data["max_yield"] * prices.get(crop, data["base_price"]) - data["seed_cost"]
    value *= max(0.25, (TURNS_PER_DAY - hour - 1) / TURNS_PER_DAY)
    value /= 10.0

    if crop == "CARROT" and day < 6:
        value *= 1.45
    elif crop == "WHEAT" and day < 5:
        value *= 1.20
    elif crop == "STRAWBERRY":
        value *= 1.05

    value *= max(0.40, 1.0 - opponent_glut_factor(crop, pressure))

    if day >= TOTAL_DAYS - ENDGAME_DAYS.get(crop, 2):
        value *= 0.25
    elif crop == "MELON" and day >= 18:
        value *= 0.45
    elif crop == "STRAWBERRY" and day >= 22:
        value *= 0.70
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
            if projected_money - cost < 120:
                break
            projected_money -= cost
            planned_spend += cost
            orders.append(["HIRE"])

        land_cost = next_land_cost(me)
        if should_buy_land(day, money - planned_spend, land_cost, pressure):
            planned_spend += land_cost
            orders.append(["BUY_LAND"])

    budget = max(0, money - planned_spend - 100)
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


def should_buy_land(day, available_money, land_cost, pressure):
    if not land_cost:
        return False
    if day < 3 or day > 18:
        return False
    pressure_penalty = pressure["STRAWBERRY"] + pressure["MELON"]
    buffer = 850 if day < 8 else 1100
    if pressure_penalty > 10:
        buffer += 200
    return available_money >= land_cost + buffer


def desired_hand_count(obs, me, roles):
    day = obs.get("day", 0)
    open_tiles = len(roles)

    if day < 2:
        target = 3
    elif day < 5:
        target = 4
    else:
        target = 5

    if len(me.get("unlocked_quadrants", [])) >= 2:
        target += 1
    if day >= 10:
        target += 1
    if open_tiles >= 45:
        target += 1

    return min(7, target)


def reserved_seed_budget(roles, private):
    seeds = private.get("seeds", {})
    needed = 0
    role_counts = {}

    for crop in roles.values():
        role_counts[crop] = role_counts.get(crop, 0) + 1

    for crop, count in role_counts.items():
        shortfall = max(0, min(8, count // 4) - seeds.get(crop, 0))
        needed += shortfall * CROPS[crop]["seed_cost"]

    return needed


def empty_tiles_by_role(me, roles):
    counts = {}
    for (x, y), crop in roles.items():
        if me["tiles"][y][x] is None:
            counts[crop] = counts.get(crop, 0) + 1
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

    job_cap = min(len(jobs), max(len(workers) + 6, len(workers) * 2))
    selected_jobs = [job_index for _, job_index in sorted(max_per_job, reverse=True)[:job_cap] if _ > 0]
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


def action_for_job(worker, job):
    if not job:
        return ["PASS"]

    target = job["pos"]
    if worker == target:
        return job["action"]
    return [step_toward(worker, target)]


def step_toward(src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]

    if abs(dx) >= abs(dy) and dx != 0:
        return "EAST" if dx > 0 else "WEST"
    if dy != 0:
        return "SOUTH" if dy > 0 else "NORTH"
    return "PASS"


def distance_to_shed(pos, board_size):
    half = board_size // 2
    shed_adjacent = [
        (half - 1, half - 1),
        (half, half - 1),
        (half - 1, half),
        (half, half),
    ]
    return min(manhattan(pos, tile) for tile in shed_adjacent)


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


def make_job(pos, action, value):
    return {"pos": pos, "action": action, "value": value}


def agent(obs):
    try:
        return run_strategy(obs)
    except Exception as exc:  # pragma: no cover
        print(f"AGENT ERROR: {exc}", file=sys.stderr)
        return PASS_RESPONSE
