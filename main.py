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
    roles = build_role_plan(obs, me)
    jobs = build_jobs(obs, me, private, roles)
    assignments = assign_jobs(me, jobs)
    market_orders = build_market_orders(obs, me, private, roles)

    workers = [tuple(me["farmer"])] + [tuple(hand) for hand in me.get("hands", [])]
    actions = [action_for_job(worker, assignments.get(index)) for index, worker in enumerate(workers)]

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": market_orders[:MAX_MARKET_ORDERS],
    }


def build_role_plan(obs, me):
    day = obs.get("day", 0)
    board = me["tiles"]
    prices = obs["market"]["prices"]

    owned_tiles = []
    for y, row in enumerate(board):
        for x, tile in enumerate(row):
            if tile != "LOCKED":
                owned_tiles.append((x, y))

    owned_tiles.sort(key=lambda pos: (distance_to_shed(pos, len(board)), pos[1], pos[0]))
    targets = crop_targets(day, len(owned_tiles), len(me.get("unlocked_quadrants", [])), prices)

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


def crop_targets(day, owned_count, quadrant_count, prices):
    if day < 5:
        wheat = min(6, max(4, owned_count // 4))
        return {
            "WHEAT": wheat,
            "CARROT": max(0, owned_count - wheat),
            "STRAWBERRY": 0,
            "TOMATO": 0,
            "MELON": 0,
        }

    wheat = min(6 if quadrant_count == 1 else 8, max(4, owned_count // 6))
    strawberry = 0 if day < 8 else min(12 if quadrant_count == 1 else 20, max(4, owned_count // 3))
    tomato = 0 if day < 12 else min(6 if quadrant_count == 1 else 10, max(2, owned_count // 7))
    melon = 0 if day < 6 else min(6 if quadrant_count == 1 else 10, max(2, owned_count // 6))

    if prices.get("STRAWBERRY", CROPS["STRAWBERRY"]["base_price"]) >= 150:
        strawberry += 3
    elif prices.get("STRAWBERRY", CROPS["STRAWBERRY"]["base_price"]) <= 100:
        strawberry = max(0, strawberry - 3)

    if prices.get("MELON", CROPS["MELON"]["base_price"]) <= 170 or day >= 20:
        melon = max(0, melon - 2)

    reserved = wheat + strawberry + tomato + melon
    if reserved > owned_count and reserved > 0:
        scale = owned_count / reserved
        wheat = int(wheat * scale)
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


def build_jobs(obs, me, private, roles):
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
                value = plant_value(crop, prices, day, hour)
                if value > 0:
                    plant_candidates.append((pos, crop, value))
                continue

            if not isinstance(tile, dict):
                continue

            kind = tile.get("kind")
            if kind == "WEED":
                jobs.append(make_job(pos, ["DIG"], 45.0))
                continue
            if kind != "PLANT":
                continue

            crop = tile["crop"]
            age = day - tile.get("planted_day", day)
            data = CROPS[crop]
            yield_units = tile.get("yield_units", 0)
            dry = tile.get("consecutive_unwatered", 0)

            if should_harvest(tile, crop, age, day):
                value = yield_units * prices.get(crop, data["base_price"]) + 30.0
                jobs.append(make_job(pos, ["HARVEST"], value))
                continue

            if should_water(tile, crop, age):
                water_value = 75.0 if dry >= 1 else 40.0
                if not data["ongoing"] and age >= max(1, (data["max_day"] + 1) // 2):
                    water_value += 20.0
                jobs.append(make_job(pos, ["WATER"], water_value))

            if yield_units > 0 and data["ongoing"]:
                value = yield_units * prices.get(crop, data["base_price"]) + 25.0
                jobs.append(make_job(pos, ["HARVEST"], value))

            if days_left <= 2 and yield_units == 0 and age >= data["first_day"]:
                jobs.append(make_job(pos, ["DIG"], 20.0))

    if hour <= TURNS_PER_DAY - 4:
        plant_candidates.sort(key=lambda item: (-item[2], item[0][1], item[0][0]))
        for pos, crop, value in plant_candidates:
            if seed_stock.get(crop, 0) <= 0:
                continue
            seed_stock[crop] -= 1
            jobs.append(make_job(pos, ["PLANT", crop], value))

    return jobs


def should_harvest(tile, crop, age, day):
    data = CROPS[crop]
    yield_units = tile.get("yield_units", 0)
    if yield_units <= 0:
        return False
    if data["ongoing"]:
        return True
    if age >= data["max_day"]:
        return True
    if day >= TOTAL_DAYS - 2:
        return True
    return False


def should_water(tile, crop, age):
    data = CROPS[crop]
    if tile.get("watered_today", False):
        return False
    if data["ongoing"]:
        return tile.get("consecutive_unwatered", 0) >= 1 or age < data["first_day"]
    return True


def plant_value(crop, prices, day, hour):
    data = CROPS[crop]
    if day >= TOTAL_DAYS - data["first_day"]:
        return -1.0

    value = data["max_yield"] * prices.get(crop, data["base_price"]) - data["seed_cost"]
    time_weight = max(0.25, (TURNS_PER_DAY - hour - 1) / TURNS_PER_DAY)

    if crop == "CARROT" and day < 5:
        value *= 1.25
    if crop == "WHEAT" and day < 5:
        value *= 1.15
    if crop == "MELON" and day >= 18:
        value *= 0.45
    if crop == "STRAWBERRY" and day >= 22:
        value *= 0.75

    return value * time_weight / 10.0


def build_market_orders(obs, me, private, roles):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    prices = obs["market"]["prices"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    money = int(me.get("money", 0))
    orders = []

    current_load = shed_load(shed)
    for item, count in sorted(shed.items()):
        if count <= 0:
            continue
        reserve = reserve_price(item, day, current_load)
        if prices.get(item, 0) >= reserve or day >= TOTAL_DAYS - 2:
            orders.append(["SELL", item, int(count)])

    if hour == 0:
        desired_hands = desired_hand_count(obs, me, roles)
        current_hands = len(me.get("hands", []))
        hires_today = me.get("hires_today", 0)
        hire_needed = max(0, desired_hands - max(current_hands, hires_today))
        projected_money = money - reserved_seed_budget(roles, private)

        for extra_index in range(hire_needed):
            cost = fib_cost(hires_today + extra_index + 1)
            if projected_money - cost < 200:
                break
            projected_money -= cost
            orders.append(["HIRE"])

        land_cost = next_land_cost(me)
        if land_cost and 4 <= day <= 18 and money >= land_cost + 1200:
            orders.append(["BUY_LAND"])

    for crop, needed in empty_tiles_by_role(me, roles).items():
        have = seeds.get(crop, 0)
        deficit = max(0, needed - have)
        if deficit <= 0:
            continue
        if day >= TOTAL_DAYS - CROPS[crop]["first_day"]:
            continue
        orders.append(["BUY_SEED", crop, int(deficit)])

    return orders[:MAX_MARKET_ORDERS]


def desired_hand_count(obs, me, roles):
    day = obs.get("day", 0)
    open_tiles = len(roles)
    target = 2 if day < 5 else 4

    if len(me.get("unlocked_quadrants", [])) >= 2:
        target += 1
    if day >= 10:
        target += 1
    if open_tiles >= 40:
        target += 1

    return min(7, target)


def reserved_seed_budget(roles, private):
    seeds = private.get("seeds", {})
    needed = 0
    role_counts = {}

    for crop in roles.values():
        role_counts[crop] = role_counts.get(crop, 0) + 1

    for crop, count in role_counts.items():
        shortfall = max(0, min(6, count // 4) - seeds.get(crop, 0))
        needed += shortfall * CROPS[crop]["seed_cost"]

    return needed


def empty_tiles_by_role(me, roles):
    counts = {}
    for (x, y), crop in roles.items():
        if me["tiles"][y][x] is None:
            counts[crop] = counts.get(crop, 0) + 1
    return counts


def reserve_price(item, day, load):
    base = base_price_for_item(item)
    fraction = RESERVE_FRAC.get(item, 0.40)
    days_left = TOTAL_DAYS - day

    if days_left <= 2:
        return 0.0
    if days_left <= 7:
        fraction *= (days_left - 2) / 5.0
    if load > 0.75:
        fraction *= 0.6

    return base * fraction


def base_price_for_item(item):
    if item in CROPS:
        return CROPS[item]["base_price"]
    return {"EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100}.get(item, 25)


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
    pairs = []

    for worker_index, worker in enumerate(workers):
        for job_index, job in enumerate(jobs):
            distance = manhattan(worker, job["pos"])
            score = job["value"] - distance * TRAVEL_COST
            if score > 0:
                pairs.append((score, worker_index, job_index))

    pairs.sort(key=lambda item: (-item[0], item[1], item[2]))

    used_workers = set()
    used_jobs = set()
    assignments = {}

    for _score, worker_index, job_index in pairs:
        if worker_index in used_workers or job_index in used_jobs:
            continue
        assignments[worker_index] = jobs[job_index]
        used_workers.add(worker_index)
        used_jobs.add(job_index)

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
