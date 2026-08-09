import sys


TOTAL_DAYS = 30
TURNS_PER_DAY = 24
TRAVEL_COST = 8.0
MAX_MARKET_ORDERS = 10
PASS_RESPONSE = {"farmer": ["PASS"], "hands": [], "market": []}
_MEMORY = {}
_MARKET_MEMORY = {}

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
        "max_day": 8,
        "max_yield": 4,
        "ongoing": True,
    },
    "STRAWBERRY": {
        "seed_cost": 100,
        "base_price": 120,
        "first_day": 10,
        "max_day": 10,
        "max_yield": 4,
        "ongoing": True,
    },
    "MELON": {
        "seed_cost": 80,
        "base_price": 250,
        "first_day": 10,
        "max_day": 12,
        "max_yield": 6,
        "ongoing": False,
    },
}

ANIMALS = {
    "GOOSE": {"cost": 300, "product": "EGG", "structure": "COOP", "base_target": 3},
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
    market_signals = update_market_signals(obs)
    roles = build_role_plan(obs, me, pressure, market_signals)
    jobs = build_jobs(obs, me, private, roles, pressure)
    assignments = assign_jobs(obs, me, private, jobs)
    market_orders = build_market_orders(obs, me, private, roles, pressure, market_signals)

    workers = [tuple(me["farmer"])] + [tuple(hand) for hand in me.get("hands", [])]
    inventories = private.get("inventories", [])
    actions = []
    for index, worker in enumerate(workers):
        inventory = inventories[index] if index < len(inventories) else {}
        job = assignments.get(index)
        drop_action = action_for_profitable_drop(
            worker,
            inventory,
            job,
            len(me["tiles"]),
            obs.get("day", 0),
            obs.get("hour", 0),
            me.get("money", 0),
            obs["market"]["prices"],
            pressure,
        )
        actions.append(drop_action or action_for_job(worker, inventory, job, len(me["tiles"])))

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": market_orders[:MAX_MARKET_ORDERS],
    }


def update_market_signals(obs):
    player = obs.get("player", 0)
    step = obs.get("step", obs.get("day", 0) * TURNS_PER_DAY + obs.get("hour", 0))
    prices = obs["market"]["prices"]
    memory = _MARKET_MEMORY.get(player, {})
    if step <= memory.get("step", -1):
        memory = {}

    peaks = dict(memory.get("peaks", {}))
    previous = memory.get("prices", prices)
    for item, price in prices.items():
        peaks[item] = max(price, peaks.get(item, price))

    _MARKET_MEMORY[player] = {"step": step, "peaks": peaks, "prices": dict(prices)}
    return {
        item: {
            "drawdown": max(0.0, (peaks[item] - price) / max(1, peaks[item])),
            "change": (price - previous.get(item, price)) / max(1, previous.get(item, price)),
        }
        for item, price in prices.items()
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


def build_role_plan(obs, me, pressure, market_signals=None):
    day = obs.get("day", 0)
    quadrant_count = len(me.get("unlocked_quadrants", []))
    prices = obs["market"]["prices"]

    owned_tiles = []
    for y, row in enumerate(me["tiles"]):
        for x, tile in enumerate(row):
            if tile != "LOCKED":
                owned_tiles.append((x, y))

    owned_tiles.sort(key=lambda pos: (distance_to_shed(pos, len(me["tiles"])), pos[1], pos[0]))
    crop_mix = crop_targets(
        day,
        len(owned_tiles),
        quadrant_count,
        prices,
        pressure,
        obs["market"].get("inventory", {}),
        obs.get("town", {}).get("unlocked_shops", []),
        market_signals or {},
    )
    animal_plan = animal_targets(day, quadrant_count, prices, market_signals)

    # Wheat is the cheap fallback for acreage not reserved for premium crops.
    # This prevents empty plots from becoming weeds without displacing the
    # higher-value planting jobs below.
    roles = {pos: "WHEAT" for pos in owned_tiles}
    remaining = list(owned_tiles)

    # Existing infrastructure keeps its purpose when new closer-to-shed land
    # unlocks; otherwise role re-sorting strands paid-for coops and pastures.
    animal_remaining = dict(animal_plan)
    for pos in list(remaining):
        x, y = pos
        tile = me["tiles"][y][x]
        if not isinstance(tile, dict):
            continue
        animal = tile.get("animal")
        if animal == "GOOSE" or tile.get("kind") == "COOP":
            roles[pos] = "COOP_GOOSE"
            animal_remaining["GOOSE"] = max(0, animal_remaining["GOOSE"] - 1)
            remaining.remove(pos)
        elif animal in ("COW", "SHEEP"):
            roles[pos] = f"PASTURE_{animal}"
            animal_remaining[animal] = max(0, animal_remaining[animal] - 1)
            remaining.remove(pos)

    for pos in list(remaining):
        x, y = pos
        tile = me["tiles"][y][x]
        if not (isinstance(tile, dict) and tile.get("kind") == "PASTURE"):
            continue
        if animal_remaining["COW"] <= 0 and animal_remaining["SHEEP"] <= 0:
            roles[pos] = "IDLE"
            remaining.remove(pos)
            continue
        animal = "COW" if animal_remaining["COW"] >= animal_remaining["SHEEP"] else "SHEEP"
        roles[pos] = f"PASTURE_{animal}"
        animal_remaining[animal] = max(0, animal_remaining[animal] - 1)
        remaining.remove(pos)

    # Preserve established crop blocks after expansion. Reassigning old plants
    # made workers repeatedly cross the shed and left the new plot unattended.
    crop_remaining = dict(crop_mix)
    for pos in list(remaining):
        x, y = pos
        tile = me["tiles"][y][x]
        if not (isinstance(tile, dict) and tile.get("kind") == "PLANT"):
            continue
        crop = tile.get("crop")
        if crop not in CROPS:
            continue
        roles[pos] = crop
        crop_remaining[crop] = max(0, crop_remaining.get(crop, 0) - 1)
        remaining.remove(pos)

    for pos in take_front(remaining, animal_remaining["GOOSE"]):
        roles[pos] = "COOP_GOOSE"
    for pos in take_front(remaining, animal_remaining["COW"]):
        roles[pos] = "PASTURE_COW"
    for pos in take_front(remaining, animal_remaining["SHEEP"]):
        roles[pos] = "PASTURE_SHEEP"
    for pos in take_front(remaining, crop_remaining["WHEAT"]):
        roles[pos] = "WHEAT"
    for pos in take_front(remaining, crop_remaining["STRAWBERRY"]):
        roles[pos] = "STRAWBERRY"
    for pos in take_front(remaining, crop_remaining["TOMATO"]):
        roles[pos] = "TOMATO"
    for pos in take_back(remaining, crop_remaining["MELON"]):
        roles[pos] = "MELON"
    for pos in take_front(remaining, crop_remaining["CARROT"]):
        roles[pos] = "CARROT"

    return roles


def crop_targets(day, owned_count, quadrant_count, prices, pressure, market_inventory, shops, market_signals=None):
    animal_slots = sum(animal_targets(day, quadrant_count, prices, market_signals).values())
    crop_slots = max(0, owned_count - animal_slots)
    wheat_targets = {1: 14, 2: 3, 3: 3, 4: 3}
    melon_targets = {1: 3, 2: 8, 3: 12, 4: 17}
    strawberry_targets = {1: 0, 2: 12, 3: 24, 4: 43}

    wheat = min(crop_slots, wheat_targets.get(quadrant_count, 3))
    melon = melon_targets.get(quadrant_count, 0) if day <= 18 and prices.get("MELON", 250) >= 55 else 0
    strawberry = (
        strawberry_targets.get(quadrant_count, 0)
        if day >= 4 and day <= 19 and prices.get("STRAWBERRY", 120) >= 25
        else 0
    )
    tomato = 0

    # Compete for the premium market with the less crowded crop instead of
    # mirroring an opponent's fixed build. Visible near-term supply is more
    # reliable than trying to identify a named strategy from a few early tiles.
    melon_glut = opponent_glut_factor("MELON", pressure)
    strawberry_glut = opponent_glut_factor("STRAWBERRY", pressure)
    if quadrant_count >= 2 and day <= 18:
        if strawberry_glut > melon_glut + 0.18:
            shift = min(8, strawberry)
            strawberry -= shift
            melon += shift
        elif melon_glut > strawberry_glut + 0.18:
            shift = min(6, melon)
            melon -= shift
            strawberry += shift

    reserved = wheat + strawberry + melon
    if reserved > crop_slots and reserved > 0:
        overflow = reserved - crop_slots
        strawberry = max(0, strawberry - overflow)

    return {
        "WHEAT": wheat,
        "CARROT": 0,
        "STRAWBERRY": strawberry,
        "TOMATO": tomato,
        "MELON": melon,
    }


def animal_targets(day, quadrant_count, prices=None, market_signals=None):
    targets = {
        1: {"GOOSE": 0, "COW": 4, "SHEEP": 4},
        2: {"GOOSE": 0, "COW": 5, "SHEEP": 3},
        3: {"GOOSE": 0, "COW": 7, "SHEEP": 5},
        4: {"GOOSE": 0, "COW": 8, "SHEEP": 6},
    }
    result = dict(targets.get(quadrant_count, targets[4]))
    prices = prices or {}
    market_signals = market_signals or {}
    if product_market_crashed("MILK", prices, market_signals):
        result["COW"] = 0
    if product_market_crashed("WOOL", prices, market_signals):
        result["SHEEP"] = 0
    return result


def product_market_crashed(product, prices, market_signals):
    signal = market_signals.get(product, {})
    base = PRODUCT_BASE_PRICE[product]
    return signal.get("drawdown", 0.0) >= 0.14 or prices.get(product, base) <= base * 0.45


def build_jobs(obs, me, private, roles, pressure):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    days_left = TOTAL_DAYS - day
    prices = obs["market"]["prices"]
    land_cost = next_land_cost(me)
    liquidity_bonus = 550.0 if land_cost and day <= 12 and me.get("money", 0) < land_cost + 500 else 80.0
    jobs = []

    inventories = private.get("inventories", [])
    total_items = total_accessible_items(me, private)
    seed_stock = {crop: private.get("seeds", {}).get(crop, 0) for crop in CROPS}
    plant_candidates = []
    fertilize_candidates = []

    for y, row in enumerate(me["tiles"]):
        for x, tile in enumerate(row):
            if tile == "LOCKED":
                continue

            pos = (x, y)
            role = roles.get(pos, "CARROT")

            if tile is None:
                if role.startswith("PASTURE_"):
                    jobs.append(make_job(pos, ["BUILD_PASTURE"], 420.0 if day < 18 else 120.0))
                elif role == "COOP_GOOSE":
                    jobs.append(make_job(pos, ["BUILD_COOP"], 420.0 if day < 18 else 120.0))
                elif role in CROPS:
                    crop = role
                    value = plant_value(crop, prices, pressure, day, hour)
                    if value > 0:
                        # Newly unlocked premium acreage must be established
                        # quickly enough to reach its first harvest window.
                        if crop in {"STRAWBERRY", "MELON"} and day <= 15:
                            value += 280.0
                        plant_candidates.append((pos, crop, value))
                continue

            if not isinstance(tile, dict):
                continue

            kind = tile.get("kind")
            if kind == "WEED":
                jobs.append(make_job(pos, ["DIG"], 420.0 if day < 24 else 180.0))
                continue

            if kind == "PLANT":
                crop = tile["crop"]
                age = day - tile.get("planted_day", day)
                data = CROPS[crop]
                yield_units = tile.get("yield_units", 0)
                dry = tile.get("consecutive_unwatered", 0)

                if should_harvest(tile, crop, age, day):
                    value = (
                        yield_units * prices.get(crop, data["base_price"])
                        + harvest_bonus(crop, day, days_left)
                        + liquidity_bonus
                    )
                    jobs.append(make_job(pos, ["HARVEST"], value))
                    continue

                fertilize_value = fertilizer_job_value(crop, tile, age, day, prices)
                if fertilize_value > 0:
                    fertilize_candidates.append(
                        make_job(pos, ["FERTILIZE"], fertilize_value, requires={"FERTILIZER": 1})
                    )

                if should_water(tile, crop, age):
                    jobs.append(make_job(pos, ["WATER"], water_job_value(crop, age, dry, day, days_left)))

                if yield_units > 0 and data["ongoing"]:
                    value = (
                        yield_units * prices.get(crop, data["base_price"])
                        + harvest_bonus(crop, day, days_left)
                        + liquidity_bonus
                    )
                    jobs.append(make_job(pos, ["HARVEST"], value))

                if days_left <= 2 and yield_units == 0 and age >= data["first_day"]:
                    jobs.append(make_job(pos, ["DIG"], 24.0))
                continue

            if kind in ("PASTURE", "COOP"):
                desired_animal = role.split("_", 1)[1] if role.startswith(("PASTURE_", "COOP_")) else None
                animal = tile.get("animal")
                if animal is None:
                    if desired_animal and total_items.get(desired_animal, 0) > 0:
                        jobs.append(make_job(pos, ["PLACE", desired_animal, 1], 700.0, requires={desired_animal: 1}))
                    continue

                if not tile.get("fed_today", False):
                    urgency = 2200.0 if tile.get("consecutive_unfed", 0) >= 1 else 900.0 + hour * 45.0
                    jobs.append(make_job(pos, ["FEED"], urgency, requires={"WHEAT": 1}))
                if not tile.get("cared_today", False):
                    jobs.append(make_job(pos, ["CARE"], 250.0 + hour * 22.0))
                if tile.get("fertilizer_available", False):
                    jobs.append(make_job(pos, ["COLLECT_FERTILIZER"], 135.0))
                if tile.get("yield_units", 0) > 0:
                    product = ANIMALS[animal]["product"]
                    value = (
                        tile.get("yield_units", 0) * prices.get(product, PRODUCT_BASE_PRICE[product])
                        + 80.0
                        + liquidity_bonus
                    )
                    jobs.append(make_job(pos, ["HARVEST"], value))

    if hour <= 18:
        plant_candidates.sort(key=lambda item: (-item[2], item[0][1], item[0][0]))
        for pos, crop, value in plant_candidates:
            if seed_stock.get(crop, 0) <= 0:
                continue
            seed_stock[crop] -= 1
            jobs.append(make_job(pos, ["PLANT", crop], value))

    fertilizer_available = total_items.get("FERTILIZER", 0)
    fertilize_candidates.sort(key=lambda job: job["value"], reverse=True)
    jobs.extend(fertilize_candidates[:fertilizer_available])

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
    if age < data["first_day"]:
        return False
    if age >= data["max_day"]:
        return True
    if day >= TOTAL_DAYS - 1:
        return True
    return False


def should_water(tile, crop, age):
    data = CROPS[crop]
    if tile.get("watered_today", False):
        return False
    if tile.get("consecutive_unwatered", 0) >= 1:
        return True
    if data["ongoing"]:
        return tile.get("fertilized_until_day", -1) >= tile.get("planted_day", 0) + age
    window_start = (data["max_day"] + 1) // 2
    return window_start <= age <= data["max_day"]


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
    value = 1500.0 if dry >= 1 else 115.0
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

    net_value = data["max_yield"] * prices.get(crop, data["base_price"]) - data["seed_cost"]
    time_factor = max(0.35, (TURNS_PER_DAY - hour - 1) / TURNS_PER_DAY)
    value = 100.0 + net_value * time_factor / 3.0

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


def fertilizer_job_value(crop, tile, age, day, prices):
    schedules = {"TOMATO": (8, 1, 4), "STRAWBERRY": (10, 2, 4)}
    if crop not in schedules or tile.get("fertilized_until_day", -1) >= day:
        return 0.0
    first, interval, count = schedules[crop]
    last = first + interval * (count - 1)
    if age < first - 1 or age > last:
        return 0.0
    bonus_yields = sum(
        1
        for future_age in range(age + 1, min(last, age + 3) + 1)
        if future_age >= first and (future_age - first) % interval == 0
    )
    gain = bonus_yields * prices.get(crop, CROPS[crop]["base_price"])
    fertilizer_price = prices.get("FERTILIZER", PRODUCT_BASE_PRICE["FERTILIZER"])
    if gain <= fertilizer_price * 1.20:
        return 0.0
    return 180.0 + gain - fertilizer_price


def build_market_orders(obs, me, private, roles, pressure, market_signals=None):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    prices = obs["market"]["prices"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    money = int(me.get("money", 0))
    orders = []
    cash_floor = operating_cash_floor(day, len(me.get("unlocked_quadrants", [])))

    current_load = shed_load(shed)
    fertilizer_reserve = desired_fertilizer_reserve(me, day, prices)
    feed_reserve = desired_wheat_buffer(obs, me, private)
    for item, count in sorted(shed.items(), key=lambda pair: sell_priority(pair[0], prices, pressure, day), reverse=True):
        if count <= 0 or item in ANIMALS:
            continue
        if item == "WHEAT":
            sell_count = count - feed_reserve
        elif item == "FERTILIZER":
            sell_count = count - fertilizer_reserve
        else:
            sell_count = count
        if sell_count <= 0:
            continue
        reserve = reserve_price(item, day, current_load, pressure)
        crashed_product = item in {"MILK", "WOOL"} and product_market_crashed(
            item, prices, market_signals or {}
        )
        if prices.get(item, 0) >= reserve or crashed_product or day >= TOTAL_DAYS - 2:
            orders.append(["SELL", item, int(sell_count)])

    planned_spend = 0
    projected_money = money

    if hour <= 2:
        desired_hands = desired_hand_count(obs, me, roles)
        current_hands = len(me.get("hands", []))
        hires_today = me.get("hires_today", 0)
        hire_needed = max(0, desired_hands - max(current_hands, hires_today))

        for extra_index in range(hire_needed):
            cost = fib_cost(hires_today + extra_index + 1)
            # Payroll is what protects existing capital; investment purchases
            # must respect the larger cash floor, but cheap daily hires may use it.
            if projected_money - cost < 100:
                break
            projected_money -= cost
            planned_spend += cost
            orders.append(["HIRE"])

    wheat_deficit = desired_wheat_buffer(obs, me, private) - total_accessible_items(me, private).get("WHEAT", 0)
    wheat_price = prices.get("WHEAT", 25)
    wheat_budget = max(0, money - planned_spend - 200)
    buy_amount = min(10, wheat_deficit, wheat_budget // max(1, wheat_price))
    if buy_amount > 0:
        planned_spend += wheat_price * buy_amount
        projected_money -= wheat_price * buy_amount
        orders.append(["BUY_PRODUCT", "WHEAT", int(buy_amount)])

    land_cost = next_land_cost(me)
    # The strongest replay unlocks land before fully funding its seed plan.
    # Delaying a quadrant costs more production than delaying a few seeds.
    if should_buy_land(day, money - planned_spend, land_cost, me, prices, pressure):
        planned_spend += land_cost
        projected_money -= land_cost
        orders.append(["BUY_LAND"])

    if hour <= 2:
        animal_orders = desired_animal_buys(obs, me, private, roles, market_signals)
        for animal, amount in animal_orders:
            for _ in range(amount):
                cost = ANIMALS[animal]["cost"]
                if money - planned_spend < cost + cash_floor:
                    break
                planned_spend += cost
                orders.append(["BUY_ANIMAL", animal, 1])

    budget = max(0, money - planned_spend - cash_floor)
    for crop, deficit in prioritized_seed_orders(me, roles, seeds, prices, pressure, day):
        if deficit <= 0 or budget < CROPS[crop]["seed_cost"]:
            continue
        affordable = min(deficit, 12, budget // CROPS[crop]["seed_cost"])
        if affordable <= 0:
            continue
        budget -= affordable * CROPS[crop]["seed_cost"]
        orders.append(["BUY_SEED", crop, int(affordable)])
        if len(orders) >= MAX_MARKET_ORDERS:
            break

    return orders[:MAX_MARKET_ORDERS]


def desired_animal_buys(obs, me, private, roles, market_signals=None):
    target = {"GOOSE": 0, "COW": 0, "SHEEP": 0}
    for role in roles.values():
        if role == "COOP_GOOSE":
            target["GOOSE"] += 1
        elif role == "PASTURE_COW":
            target["COW"] += 1
        elif role == "PASTURE_SHEEP":
            target["SHEEP"] += 1

    current = {"GOOSE": 0, "COW": 0, "SHEEP": 0}
    for row in me["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and tile.get("animal") in current:
                current[tile["animal"]] += 1

    total_items = total_accessible_items(me, private)
    orders = []
    for animal in ("GOOSE", "COW", "SHEEP"):
        product = ANIMALS[animal]["product"]
        if product in {"MILK", "WOOL"} and product_market_crashed(
            product, obs["market"]["prices"], market_signals or {}
        ):
            continue
        available = current[animal] + total_items.get(animal, 0)
        deficit = max(0, target[animal] - available)
        if deficit > 0:
            orders.append((animal, 1))
    return orders


def desired_wheat_buffer(obs, me, private):
    animals = 0
    for row in me["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and tile.get("animal"):
                animals += 1
    if animals == 0:
        return 4
    return max(6, animals + 3)


def desired_fertilizer_reserve(me, day, prices):
    profitable = 0
    for row in me["tiles"]:
        for tile in row:
            if not (isinstance(tile, dict) and tile.get("kind") == "PLANT"):
                continue
            crop = tile.get("crop")
            age = day - tile.get("planted_day", day)
            if fertilizer_job_value(crop, tile, age, day, prices) > 0:
                profitable += 1
    return min(6, profitable)


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
        deficit = max(0, min(needed, 12) - have)
        if deficit <= 0:
            continue
        if day >= TOTAL_DAYS - CROPS[crop]["first_day"]:
            continue
        score = plant_value(crop, prices, pressure, day, 0)
        items.append((score, crop, deficit))
    items.sort(reverse=True)
    return [(crop, deficit) for score, crop, deficit in items if score > 0]


def should_buy_land(day, available_money, land_cost, me=None, prices=None, pressure=None):
    if not land_cost:
        return False
    earliest_day = {1000: 4, 2000: 6, 4000: 10}.get(land_cost, 30)
    if land_cost == 4000:
        owned = [tile for row in me.get("tiles", []) for tile in row if tile != "LOCKED"] if me else []
        utilization = sum(tile is not None for tile in owned) / max(1, len(owned))
        premium_price = max((prices or {}).get("MELON", 0) / 250.0, (prices or {}).get("STRAWBERRY", 0) / 120.0)
        premium_pressure = max(
            opponent_glut_factor("MELON", pressure or {}),
            opponent_glut_factor("STRAWBERRY", pressure or {}),
        )
        return (
            day <= 12
            and available_money >= 12000
            and utilization >= 0.92
            and premium_price >= 1.35
            and premium_pressure <= 0.45
        )
    return day >= earliest_day and available_money >= land_cost + 75


def operating_cash_floor(day, quadrant_count):
    if day < 10:
        return 400
    if day < 24:
        return 500
    return 250


def desired_hand_count(obs, me, roles):
    quadrant_count = len(me.get("unlocked_quadrants", []))
    return {1: 7, 2: 9, 3: 12, 4: 13}.get(quadrant_count, 13)


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

    if item in {"MELON", "STRAWBERRY", "MILK", "WOOL"}:
        fraction = min(fraction, 0.22)
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


def assign_jobs(obs, me, private, jobs):
    workers = [tuple(me["farmer"])] + [tuple(hand) for hand in me.get("hands", [])]
    if not workers or not jobs:
        return {}
    inventories = private.get("inventories", [])
    shed = private.get("shed", {})
    player = obs.get("player", 0)
    step = obs.get("step", obs.get("day", 0) * TURNS_PER_DAY + obs.get("hour", 0))
    memory = _MEMORY.get(player, {})
    if step <= memory.get("step", -1):
        memory = {}
    previous = memory.get("targets", {})
    active_quadrants = [str(value).upper() for value in me.get("unlocked_quadrants", [])]

    def key_for(job):
        return (job["pos"], tuple(job["action"]))

    def route_distance(worker_index, job):
        worker = workers[worker_index]
        inv = inventories[worker_index] if worker_index < len(inventories) else {}
        missing = [item for item, count in job.get("requires", {}).items() if inv.get(item, 0) < count]
        if not missing:
            return manhattan(worker, job["pos"])
        if any(shed.get(item, 0) <= 0 for item in missing):
            return None
        access = min(
            shed_tiles(len(me["tiles"])),
            key=lambda pos: manhattan(worker, pos) + manhattan(pos, job["pos"]),
        )
        return manhattan(worker, access) + 1 + manhattan(access, job["pos"])

    def zone_penalty(worker_index, job):
        if worker_index == 0 or len(active_quadrants) <= 1:
            return 0.0
        action = job["action"][0]
        urgent = job["value"] >= 700 or action in {"FEED", "PLACE"}
        if urgent:
            return 0.0
        home = active_quadrants[(worker_index - 1) % len(active_quadrants)]
        return 52.0 if quadrant_for_pos(job["pos"], len(me["tiles"])) != home else 0.0

    pairs = []
    for worker_index in range(len(workers)):
        for job_index, job in enumerate(jobs):
            distance = route_distance(worker_index, job)
            if distance is None:
                continue
            sticky = 165.0 if previous.get(worker_index) == key_for(job) else 0.0
            score = job["value"] + sticky - distance * TRAVEL_COST - zone_penalty(worker_index, job)
            if score > 0:
                pairs.append((score, -distance, worker_index, job_index))

    assignments = {}
    used_jobs = set()
    for _score, _distance, worker_index, job_index in sorted(pairs, reverse=True):
        if worker_index in assignments or job_index in used_jobs:
            continue
        assignments[worker_index] = jobs[job_index]
        used_jobs.add(job_index)
        if len(assignments) >= len(workers):
            break

    _MEMORY[player] = {
        "step": step,
        "targets": {index: key_for(job) for index, job in assignments.items()},
    }
    return assignments


def action_for_job(worker, inventory, job, board_size):
    if not job:
        return ["PASS"]

    requires = job.get("requires", {})
    for item, count in requires.items():
        if inventory.get(item, 0) < count:
            shed_target = nearest_shed_tile(worker, board_size)
            if worker == shed_target:
                batch = 6 if item == "WHEAT" else 2
                return ["PICKUP", item, max(count, batch)]
            return [step_toward(worker, shed_target)]

    if worker == job["pos"]:
        return job["action"]
    return [step_toward(worker, job["pos"])]


def action_for_profitable_drop(worker, inventory, job, board_size, day, hour, money, prices, pressure):
    sale_items = {
        item: count
        for item, count in inventory.items()
        if count > 0 and item in {"CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"}
    }
    sale_load = sum(sale_items.values())
    urgent_job = (
        job
        and job["action"][0] in {"FEED", "WATER", "PLANT", "PLACE", "BUILD_PASTURE", "BUILD_COOP"}
        and job.get("value", 0) >= 700
    )
    if sale_load <= 0 or urgent_job:
        return None
    if day < TOTAL_DAYS - 2 and any(
        prices.get(item, 0) < reserve_price(item, day, 0.0, pressure) for item in sale_items
    ):
        return None
    threshold = 4 if money < 1200 else 8
    if hour >= 20:
        threshold = 1
    if sale_load < threshold:
        return None
    shed_target = nearest_shed_tile(worker, board_size)
    if worker == shed_target:
        return ["DROP"]
    return [step_toward(worker, shed_target)]


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


def quadrant_for_pos(pos, board_size):
    half = board_size // 2
    north_south = "N" if pos[1] < half else "S"
    west_east = "W" if pos[0] < half else "E"
    return north_south + west_east


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
