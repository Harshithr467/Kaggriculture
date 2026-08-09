import sys


TOTAL_DAYS = 30
TURNS_PER_DAY = 24
TRAVEL_COST = 8.0
ROUTINE_TRAVEL_COST = 40.0
MAX_MARKET_ORDERS = 10
PASS_RESPONSE = {"farmer": ["PASS"], "hands": [], "market": []}
_MEMORY = {}
_MARKET_MEMORY = {}
_STRATEGY_MEMORY = {}

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


def run_strategy(obs, forced_mode=None):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    pressure = estimate_opponent_pressure(obs)
    market_signals = update_market_signals(obs)
    mode = forced_mode or select_strategy_mode(obs)
    roles = build_role_plan(obs, me, pressure, market_signals, mode)
    jobs = build_jobs(obs, me, private, roles, pressure, mode)
    assignments = assign_jobs(obs, me, private, jobs)
    market_orders = build_market_orders(obs, me, private, roles, pressure, market_signals, mode)

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
            market_signals,
            mode,
        )
        actions.append(drop_action or action_for_job(worker, inventory, job, len(me["tiles"])))

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": market_orders[:MAX_MARKET_ORDERS],
    }


def select_strategy_mode(obs):
    player = obs.get("player", 0)
    step = obs.get("step", obs.get("day", 0) * TURNS_PER_DAY + obs.get("hour", 0))
    memory = _STRATEGY_MEMORY.get(player, {})
    if step <= memory.get("step", -1):
        memory = {}
    mode = memory.get("mode", "RANK1_HYBRID")

    if mode == "RANK1_HYBRID" and obs.get("day", 0) >= 4:
        opponent = next(farm for index, farm in enumerate(obs["farms"]) if index != player)
        opponent_land = len(opponent.get("unlocked_quadrants", []))
        day = obs.get("day", 0)
        opponent_hands = len(opponent.get("hands", []))
        fast_land = (
            day <= 4 and opponent_land >= 2 and opponent_hands >= 6
        ) or (
            day <= 7 and opponent_land >= 3 and opponent_hands >= 7
        )
        if fast_land:
            mode = "COUNTER"

    if mode == "COUNTER" and 9 <= obs.get("day", 0) <= 12:
        prices = obs["market"]["prices"]
        product_strength = (prices.get("MILK", 160) / 160.0 + prices.get("WOOL", 200) / 200.0) / 2.0
        if product_strength >= 0.95:
            mode = "RACE"

    _STRATEGY_MEMORY[player] = {"step": step, "mode": mode}
    return mode


def update_market_signals(obs):
    player = obs.get("player", 0)
    step = obs.get("step", obs.get("day", 0) * TURNS_PER_DAY + obs.get("hour", 0))
    prices = obs["market"]["prices"]
    memory = _MARKET_MEMORY.get(player, {})
    if step <= memory.get("step", -1):
        memory = {}
    peaks = dict(memory.get("peaks", {}))
    for item, price in prices.items():
        peaks[item] = max(price, peaks.get(item, price))
    _MARKET_MEMORY[player] = {"step": step, "peaks": peaks}
    return {
        item: max(0.0, (peak - prices.get(item, peak)) / max(1, peak))
        for item, peak in peaks.items()
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


def build_role_plan(obs, me, pressure, market_signals=None, mode="RANK1_HYBRID"):
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
        mode,
    )
    animal_plan = animal_targets(day, quadrant_count, prices, mode)
    crop_remaining = dict(crop_mix)

    # Any acreage not reserved for a higher-value role becomes cheap wheat.
    # Its low job priority lets workers establish it gradually without stealing
    # time from premium crops or animal care.
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

    # Keep established crop blocks stable across land expansions. Re-sorting
    # every tile made workers cross the farm and created duplicate melon plots.
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


def crop_targets(
    day, owned_count, quadrant_count, prices, pressure, market_inventory, shops, market_signals=None, mode="RANK1_HYBRID"
):
    animal_slots = sum(animal_targets(day, quadrant_count, prices, mode).values())
    crop_slots = max(0, owned_count - animal_slots)
    market_signals = market_signals or {}
    if mode == "THREE_PREMIUM":
        wheat_targets = {1: 7, 2: 7, 3: 7, 4: 7}
        melon_targets = {1: 12, 2: 12, 3: 12, 4: 12}
        strawberry_targets = {1: 0, 2: 19, 3: 42, 4: 42}
    elif mode == "BALANCED_PROXY":
        wheat_targets = {1: 11, 2: 10, 3: 35, 4: 35}
        melon_targets = {1: 5, 2: 9, 3: 5, 4: 5}
        strawberry_targets = {1: 0, 2: 12, 3: 21, 4: 21}
    elif mode == "CROP_RUSH":
        wheat_targets = {1: 0, 2: 17, 3: 17, 4: 17}
        melon_targets = {1: 18, 2: 19, 3: 19, 4: 19}
        strawberry_targets = {1: 6, 2: 14, 3: 14, 4: 14}
    elif mode == "COUNTER":
        wheat_targets = {1: 14, 2: 14, 3: 17, 4: 21}
        melon_targets = {1: 3, 2: 10, 3: 10, 4: 12}
        strawberry_targets = {1: 0, 2: 16, 3: 33, 4: 38}
    else:
        # Replay winners establish nearly full premium blocks before day 13.
        # Seven wheat tiles cover feed while strawberries occupy persistent
        # acreage and melons provide the earlier lump-sum return.
        wheat_targets = {1: 14, 2: 7, 3: 7, 4: 7}
        melon_targets = {1: 3, 2: 12, 3: 10, 4: 14}
        strawberry_targets = {1: 0, 2: 19, 3: 40, 4: 54}

    wheat = min(crop_slots, wheat_targets.get(quadrant_count, 3))
    melon = melon_targets.get(quadrant_count, 0) if day <= 18 and prices.get("MELON", 250) >= 55 else 0
    strawberry = (
        strawberry_targets.get(quadrant_count, 0)
        if day >= 4 and day <= 19 and prices.get("STRAWBERRY", 120) >= 25
        else 0
    )
    tomato = 0

    if day >= 8 and (prices.get("MELON", 250) < 150 or pressure.get("MELON", 0) >= 12):
        melon = min(melon, 4)
    if day >= 8 and (prices.get("STRAWBERRY", 120) < 75 or pressure.get("STRAWBERRY", 0) >= 24):
        strawberry = min(strawberry, 18)
    if market_signals.get("MILK", 0.0) >= 0.15 or market_signals.get("WOOL", 0.0) >= 0.18:
        # Shift new acreage toward whichever premium crop still has the best
        # price and the least visible incoming opponent supply.
        melon_score = prices.get("MELON", 0) / 250.0 / (1.0 + pressure.get("MELON", 0) / 12.0)
        strawberry_score = prices.get("STRAWBERRY", 0) / 120.0 / (1.0 + pressure.get("STRAWBERRY", 0) / 24.0)
        if day <= 18 and melon_score > strawberry_score * 1.08:
            melon = min(melon_targets.get(quadrant_count, 0), crop_slots)
        elif day <= 19 and prices.get("STRAWBERRY", 0) >= 90:
            strawberry = min(strawberry_targets.get(quadrant_count, 0), crop_slots)

    reserved = wheat + strawberry + melon
    if reserved > crop_slots:
        overflow = reserved - crop_slots
        strawberry = max(0, strawberry - overflow)
    elif reserved < crop_slots:
        wheat += crop_slots - reserved

    return {
        "WHEAT": wheat,
        "CARROT": 0,
        "STRAWBERRY": strawberry,
        "TOMATO": tomato,
        "MELON": melon,
    }


def animal_targets(day, quadrant_count, prices=None, mode="RANK1_HYBRID"):
    prices = prices or {}
    if mode == "THREE_PREMIUM":
        return {"GOOSE": 0, "COW": 8 if quadrant_count >= 3 else 4, "SHEEP": 6 if quadrant_count >= 3 else 2}
    if mode == "BALANCED_PROXY":
        return {"GOOSE": 0, "COW": 8 if quadrant_count >= 3 else 3, "SHEEP": 6 if quadrant_count >= 3 else 1}
    if mode == "CROP_RUSH":
        return {"GOOSE": 0, "COW": 1, "SHEEP": 0}
    if mode == "COUNTER" and quadrant_count >= 3:
        milk_strength = prices.get("MILK", 160) / 160.0
        wool_strength = prices.get("WOOL", 200) / 200.0
        if wool_strength > milk_strength + 0.12:
            return {"GOOSE": 0, "COW": 6, "SHEEP": 10}
        if milk_strength > wool_strength + 0.12:
            return {"GOOSE": 0, "COW": 11, "SHEEP": 4}
        return {"GOOSE": 0, "COW": 9, "SHEEP": 6}
    targets = {
        1: {"GOOSE": 0, "COW": 4, "SHEEP": 4},
        2: {"GOOSE": 0, "COW": 5, "SHEEP": 3},
        3: {"GOOSE": 0, "COW": 7, "SHEEP": 7},
        4: {"GOOSE": 0, "COW": 10, "SHEEP": 9},
    }
    return targets.get(quadrant_count, targets[4])


def build_jobs(obs, me, private, roles, pressure, mode="RANK1_HYBRID"):
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
    empty_owned = sum(tile is None for row in me["tiles"] for tile in row)

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
                        defensive_fill = mode in {"COUNTER", "THREE_PREMIUM", "BALANCED_PROXY", "CROP_RUSH"}
                        if crop in {"STRAWBERRY", "MELON"} and day <= 15:
                            expansion_bonus = 600.0 if empty_owned >= 8 else 280.0
                            value += expansion_bonus if mode == "RANK1_HYBRID" or defensive_fill else 280.0
                        elif crop == "WHEAT" and day <= 27 and defensive_fill:
                            value += 380.0 if empty_owned >= 8 else 180.0
                        plant_candidates.append((pos, crop, value))
                continue

            if not isinstance(tile, dict):
                continue

            kind = tile.get("kind")
            if kind == "WEED":
                weed_value = 520.0 if day < 27 else 160.0
                if mode in {"RANK1_HYBRID", "RACE", "RANK1"}:
                    weed_value = 520.0 if day < 27 else 180.0
                jobs.append(make_job(pos, ["DIG"], weed_value))
                continue

            if kind == "PLANT":
                crop = tile["crop"]
                age = day - tile.get("planted_day", day)
                data = CROPS[crop]
                yield_units = tile.get("yield_units", 0)
                dry = tile.get("consecutive_unwatered", 0)

                # A ripe ongoing crop can still become a weed tonight. Water
                # it before harvesting when it has already missed one day.
                needs_water = should_water(tile, crop, age)
                if data["ongoing"] and needs_water and dry >= 1:
                    jobs.append(make_job(pos, ["WATER"], water_job_value(crop, age, dry, day, days_left)))
                    continue

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

                if needs_water:
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

    planting_deadline = 21 if mode in {"COUNTER", "THREE_PREMIUM", "BALANCED_PROXY", "CROP_RUSH"} and day <= 15 else 18
    if hour <= planting_deadline:
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


def build_market_orders(obs, me, private, roles, pressure, market_signals=None, mode="RANK1_HYBRID"):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    prices = obs["market"]["prices"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    money = int(me.get("money", 0))
    market_signals = market_signals or {}
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
        if item in {"MILK", "WOOL"} and product_market_crashed(item, market_signals, mode):
            reserve = 0.0
        if prices.get(item, 0) >= reserve or day >= TOTAL_DAYS - 2:
            orders.append(["SELL", item, int(sell_count)])

    planned_spend = 0
    projected_money = money
    planned_seed_stock = dict(seeds)

    if hour <= 2:
        desired_hands = desired_hand_count(obs, me, roles, mode)
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
    if should_buy_land(day, money - planned_spend, land_cost, me, prices, pressure, mode):
        planned_spend += land_cost
        projected_money -= land_cost
        orders.append(["BUY_LAND"])

    if hour <= 2:
        animal_orders = desired_animal_buys(obs, me, private, roles, market_signals, mode)
        for animal, amount in animal_orders:
            for _ in range(amount):
                cost = ANIMALS[animal]["cost"]
                if money - planned_spend < cost + cash_floor:
                    break
                planned_spend += cost
                orders.append(["BUY_ANIMAL", animal, 1])

    budget = max(0, money - planned_spend - cash_floor)
    for crop, deficit in prioritized_seed_orders(me, roles, planned_seed_stock, prices, pressure, day):
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


def desired_animal_buys(obs, me, private, roles, market_signals=None, mode="RANK1_HYBRID"):
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
    prices = obs["market"]["prices"]
    market_signals = market_signals or {}
    orders = []
    for animal in ("GOOSE", "COW", "SHEEP"):
        available = current[animal] + total_items.get(animal, 0)
        product = ANIMALS[animal]["product"]
        product_price = prices.get(product, PRODUCT_BASE_PRICE[product])
        crash_limit = 0.15 if animal == "COW" else 0.18
        price_floor = PRODUCT_BASE_PRICE[product] * (0.85 if animal == "COW" else 0.78)
        if mode in {"RANK1_HYBRID", "COUNTER", "RACE"} and (
            market_signals.get(product, 0.0) >= crash_limit or product_price < price_floor
        ):
            target[animal] = min(target[animal], available)
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


def product_market_crashed(product, market_signals, mode="RANK1_HYBRID"):
    if mode not in {"RANK1_HYBRID", "COUNTER", "RACE"}:
        return False
    threshold = 0.15 if product == "MILK" else 0.18
    return market_signals.get(product, 0.0) >= threshold


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


def should_buy_land(day, available_money, land_cost, me=None, prices=None, pressure=None, mode="RANK1_HYBRID"):
    if not land_cost:
        return False
    earliest_day = {1000: 4, 2000: 6, 4000: 10}.get(land_cost, 30)
    if day < earliest_day or available_money < land_cost + 75:
        return False
    if me is None:
        return land_cost != 4000

    owned = [tile for row in me["tiles"] for tile in row if tile != "LOCKED"]
    occupied = sum(tile is not None for tile in owned)
    utilization = occupied / max(1, len(owned))
    if mode == "RANK1":
        return day >= earliest_day and available_money >= land_cost + 75
    if mode in {"RANK1_HYBRID", "RACE"} and land_cost != 4000:
        return day >= earliest_day and available_money >= land_cost + 75
    if mode in {"THREE_PREMIUM", "BALANCED_PROXY"}:
        if land_cost == 1000:
            return day >= 7 and available_money >= land_cost + 75
        if land_cost == 2000:
            return day >= 11 and available_money >= land_cost + 75
        return False
    if mode == "CROP_RUSH":
        return land_cost == 1000 and day >= 11 and available_money >= land_cost + 75
    if mode == "COUNTER":
        if land_cost == 1000:
            return day >= 6 and (utilization >= 0.72 or day >= 7)
        if land_cost == 2000:
            return day >= 10 and (utilization >= 0.70 or day >= 11)
        return False

    if land_cost == 1000:
        return utilization >= 0.78 or day >= 6
    if land_cost == 2000:
        return utilization >= 0.76 or day >= 9

    prices = prices or {}
    pressure = pressure or {}
    premium_market = (
        prices.get("STRAWBERRY", 0) >= 180 and pressure.get("STRAWBERRY", 0) < 12
    ) or (
        prices.get("MELON", 0) >= 260 and pressure.get("MELON", 0) < 8
    )
    worker_capacity = len(me.get("hands", [])) >= 10
    return day <= 14 and available_money >= land_cost + 2500 and utilization >= 0.85 and worker_capacity and premium_market


def operating_cash_floor(day, quadrant_count):
    if day < 10:
        return 400
    if day < 24:
        return 500
    return 250


def desired_hand_count(obs, me, roles, mode="RANK1_HYBRID"):
    quadrant_count = len(me.get("unlocked_quadrants", []))
    if mode == "THREE_PREMIUM":
        return {1: 5, 2: 8, 3: 11}.get(quadrant_count, 11)
    if mode == "BALANCED_PROXY":
        return 6 if quadrant_count == 1 else 10 if quadrant_count == 2 else 12
    if mode == "CROP_RUSH":
        return 6 if obs.get("day", 0) < 11 else 12
    if mode == "COUNTER" and quadrant_count >= 3:
        day = obs.get("day", 0)
        return 10 if day < 14 else 13 if day < 21 else 12
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
    board_size = len(me["tiles"])
    active_quadrants = [
        quadrant
        for quadrant in ("NW", "NE", "SW", "SE")
        if quadrant in me.get("unlocked_quadrants", [])
    ]

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
            shed_tiles(board_size),
            key=lambda pos: manhattan(worker, pos) + manhattan(pos, job["pos"]),
        )
        return manhattan(worker, access) + 1 + manhattan(access, job["pos"])

    pair_scores = {}
    for worker_index in range(len(workers)):
        for job_index, job in enumerate(jobs):
            distance = route_distance(worker_index, job)
            if distance is None:
                continue
            sticky = 95.0 if previous.get(worker_index) == key_for(job) else 0.0
            deadline = is_deadline_job(job)
            affinity = 0.0
            if worker_index > 0 and active_quadrants and not deadline:
                home, lane = worker_ripple_lane(worker_index, active_quadrants, board_size)
                job_quadrant = quadrant_for_pos(job["pos"], board_size)
                affinity = 45.0 - abs(job["pos"][0] - lane) * 20.0 if home == job_quadrant else -140.0
            travel_cost = TRAVEL_COST if deadline else ROUTINE_TRAVEL_COST
            pair_scores[(worker_index, job_index)] = job["value"] + sticky + affinity - distance * travel_cost

    assignments = {}
    used_jobs = set()

    # Globally match only jobs that can cause permanent loss if delayed. This
    # avoids the old greedy scheduler sending every nearby worker elsewhere.
    urgent_jobs = [index for index, job in enumerate(jobs) if is_deadline_job(job)]
    if urgent_jobs:
        urgent_scores = []
        for worker_index in range(len(workers)):
            row = [pair_scores.get((worker_index, job_index), -1_000_000.0) for job_index in urgent_jobs]
            row.extend(0.0 for _ in workers)
            urgent_scores.append(row)
        for worker_index, column in enumerate(maximum_score_assignment(urgent_scores)):
            if column is None or column >= len(urgent_jobs):
                continue
            job_index = urgent_jobs[column]
            if pair_scores.get((worker_index, job_index), 0.0) <= 0:
                continue
            assignments[worker_index] = jobs[job_index]
            used_jobs.add(job_index)

    # Routine jobs retain the stable route-aware ordering that performed best
    # in benchmarks, after all deadline work has workers reserved.
    pairs = []
    for (worker_index, job_index), score in pair_scores.items():
        if worker_index in assignments or job_index in used_jobs or score <= 0:
            continue
        distance = route_distance(worker_index, jobs[job_index])
        pairs.append((score, -distance, worker_index, job_index))
    for _score, _distance, worker_index, job_index in sorted(pairs, reverse=True):
        if worker_index in assignments or job_index in used_jobs:
            continue
        assignments[worker_index] = jobs[job_index]
        used_jobs.add(job_index)

    _MEMORY[player] = {
        "step": step,
        "targets": {index: key_for(job) for index, job in assignments.items()},
    }
    return assignments


def maximum_score_assignment(scores):
    """Return the globally optimal unique column for each worker."""
    row_count = len(scores)
    column_count = len(scores[0]) if scores else 0
    if row_count == 0 or column_count == 0:
        return []

    # Hungarian algorithm for a rectangular matrix where rows <= columns.
    u = [0.0] * (row_count + 1)
    v = [0.0] * (column_count + 1)
    matching = [0] * (column_count + 1)
    previous_column = [0] * (column_count + 1)

    for row in range(1, row_count + 1):
        matching[0] = row
        current_column = 0
        minimum = [float("inf")] * (column_count + 1)
        used = [False] * (column_count + 1)
        while True:
            used[current_column] = True
            current_row = matching[current_column]
            delta = float("inf")
            next_column = 0
            for column in range(1, column_count + 1):
                if used[column]:
                    continue
                cost = -scores[current_row - 1][column - 1]
                reduced = cost - u[current_row] - v[column]
                if reduced < minimum[column]:
                    minimum[column] = reduced
                    previous_column[column] = current_column
                if minimum[column] < delta:
                    delta = minimum[column]
                    next_column = column
            for column in range(column_count + 1):
                if used[column]:
                    u[matching[column]] += delta
                    v[column] -= delta
                else:
                    minimum[column] -= delta
            current_column = next_column
            if matching[current_column] == 0:
                break
        while True:
            next_column = previous_column[current_column]
            matching[current_column] = matching[next_column]
            current_column = next_column
            if current_column == 0:
                break

    result = [None] * row_count
    for column in range(1, column_count + 1):
        if matching[column] > 0:
            result[matching[column] - 1] = column - 1
    return result


def is_deadline_job(job):
    action = job["action"][0]
    value = job.get("value", 0)
    return action == "FEED" and value >= 2000 or action == "WATER" and value >= 1400


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


def action_for_profitable_drop(
    worker, inventory, job, board_size, day, hour, money, prices, pressure, market_signals=None, mode="RANK1_HYBRID"
):
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
    market_signals = market_signals or {}
    if day < TOTAL_DAYS - 2 and any(
        prices.get(item, 0) < reserve_price(item, day, 0.0, pressure)
        and not (item in {"MILK", "WOOL"} and product_market_crashed(item, market_signals, mode))
        for item in sale_items
    ):
        return None
    threshold = 8 if money < 1200 else 14
    if hour >= 22:
        threshold = 6
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
    horizontal = "W" if pos[0] < half else "E"
    vertical = "N" if pos[1] < half else "S"
    return vertical + horizontal


def worker_ripple_lane(worker_index, active_quadrants, board_size):
    quadrant_index = (worker_index - 1) % len(active_quadrants)
    lane_index = (worker_index - 1) // len(active_quadrants)
    quadrant = active_quadrants[quadrant_index]
    half = board_size // 2
    if quadrant.endswith("W"):
        lane = max(0, half - 1 - lane_index)
    else:
        lane = min(board_size - 1, half + lane_index)
    return quadrant, lane


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
