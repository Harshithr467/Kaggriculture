# Kaggriculture — Competition Specification

Everything the competition asks for, and how the game actually works.

**Every mechanic below is taken from the environment source**
(`.venv/Lib/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`)
and confirmed against live Kaggle replays, not from the competition
documentation. The docs are wrong in several places that change strategy — those
are listed in [§9](#9-where-the-official-docs-are-wrong).

---

## 1. The competition

| | |
|---|---|
| Name | Kaggriculture (Kaggle Featured, Simulation) |
| Prize | $50,000 USD |
| Deadline | **2026-09-30 23:59 UTC** |
| Field | ~3,695 teams |
| Submissions | 5 per day; **the two most recent are the active pair** |
| Final ranking | Bradley-Terry tournament, run two weeks after the deadline |
| Compute | 1.6 vCPU, 6.5 GiB RAM, **no GPU**, 1 s per turn |
| Size limit | 100 MiB |

Medal thresholds at 1,000+ teams: **bronze** top 10%, **silver** top 5%,
**gold** top 10 + 0.2% (≈ top 17 at this field size).

Scores are an ELO-style rating that **climbs as a submission plays more games**
and drifts ±20 afterwards. A fresh submission scoring below an older one is not
evidence of regression — it has simply played fewer episodes.

## 2. What you submit

A single `main.py` whose **last `def` is `agent(obs)`**, returning an action
dict. Multi-file submissions are a `tar.gz` with `main.py` at the root.

```powershell
kaggle competitions submit kaggriculture -f main.py -m "message"
```

`main.py` must be import-light — it runs inside the episode with a 1-second
per-turn budget.

## 3. Interface

```py
obs = {
  "player": int,              # 0 or 1
  "day":    int,              # 0-indexed
  "hour":   int,              # 0..23
  "farms":  [farm, farm],     # PUBLIC: both players' farms
  "market": {"inventory": {item: int}, "prices": {item: int}},
  "town":   {"unlocked_shops": [str]},
  "private": {                # yours only
     "shed":        {item: int},
     "seeds":       {crop: int},
     "inventories": [farmer_inv, hand_inv, ...],
  },
}

action = {
  "farmer": [op, *args],           # one op for the main farmer
  "hands":  [[op, *args], ...],    # one op per hired hand, in order
  "market": [[op, *args], ...],    # max 10 orders per turn
}
```

**Unit ops** — `NORTH` `SOUTH` `EAST` `WEST` `PASS`, `PLANT <crop>`, `WATER`,
`HARVEST`, `FERTILIZE`, `DIG`, `BUILD_COOP`, `BUILD_PASTURE`, `PLACE <item> [n]`,
`FEED`, `CARE`, `COLLECT_FERTILIZER`, `PICKUP <item> [n]`, `DROP`.

**Market ops** — `BUY_SEED`, `BUY_PRODUCT`, `BUY_ANIMAL`, `SELL`, `HIRE`,
`BUY_LAND`. Invalid actions are silent no-ops.

## 4. Board, season, money

- **720 turns** = 30 days × 24 turns.
- **10×10 board** split into four **5×5** quadrants. Only **NW** starts unlocked.
- Extra quadrants cost **$1,000 / $2,000 / $4,000**, always in order NE, SW, SE.
- Starting money **$3,000**.
- The **shed** is not a tile. "Shed-adjacent" means standing on `(4,4)`, `(5,4)`,
  `(4,5)` or `(5,5)` — one per quadrant.
- Locked tiles are **passable**; tile actions just no-op there.

### Scoring — the single most important rule

```py
s.reward = float(farms[player]["money"])
```

**Final reward is bank balance only.** Unsold shed stock is worth **zero**, so
everything must be liquidated before the season ends. A $1 sale on the last day
strictly beats holding.

## 5. Crops

| Crop | Seed | Base $ | First yield | Max-yield day | Interval | Max yield | Ongoing |
|---|---|---|---|---|---|---|---|
| WHEAT | 10 | 25 | day 2 | day 4 | — | 6 | no |
| CARROT | 20 | 35 | day 2 | day 3 | — | 4 | no |
| TOMATO | 50 | 60 | day 8 | day 8 | 1 | 4 | yes |
| STRAWBERRY | 100 | 120 | day 10 | day 10 | 2 | 4 | yes |
| MELON | 80 | 250 | day 10 | day 12 | — | 6 | no |

**Watering and yield (one-time crops).** The bonus window opens at
`(max_yield_day + 1) // 2`. Each watering inside it adds **+1** unit, or **+2**
if fertilized, capped at `max_yield`.

**Harvest is gated**: refused while `age < first_yield_day`, no matter how many
units have accumulated.

What fertilizer is actually worth, per crop:

| Crop | Plain peak | Fertilized peak | Gain |
|---|---|---|---|
| WHEAT | 4 | **6** | +2 (+50%) |
| CARROT | 3 | **4** | +1 |
| MELON | 6 | 6 | **nothing** |

Melon reaches its cap of 6 on plain watering by age 10 — exactly when harvest
first becomes legal. Fertilizer only gets there at age 8 and cannot be cashed
early, so it buys nothing.

**Ongoing crops** produce on a fixed schedule (`first_yield + k × interval`),
capped at `max_yield` total productions, then decay to a weed. Base 1 per
production, **2 if fertilized *and* watered that day**.

**Death and decay.** Plants need water daily; **two consecutive unwatered days
turn the tile into a weed**. A fresh plant starts at `consecutive_unwatered = 1`
— the planting day already counts, so a seed planted and not watered that same
day dies overnight. Past max lifespan, `yield_units` drops by 1 every other turn
until the tile becomes a weed.

**Weeds** spawn on empty unlocked tiles at 0.5% per tile per day. A weed is only
an occupied tile — it does not spread or damage anything.

**Atomic planting**: if the total `PLANT` requests for a crop in one turn exceed
seeds held, **all** of them are dropped.

## 6. Animals

| Animal | Cost | Structure | First yield | Interval | Max held | Product |
|---|---|---|---|---|---|---|
| GOOSE | 300 | COOP | day 4 | 1 day | 4 | EGG |
| COW | 400 | PASTURE | day 8 | 2 days | 6 | MILK |
| SHEEP | 500 | PASTURE | day 6 | 3 days | 6 | WOOL |

- **Feed costs 1 WHEAT per animal per day.** Two consecutive unfed days and the
  animal **escapes permanently**; the structure remains.
- **CARE banks +1 unit** onto the next scheduled production, but only on days the
  animal was both fed *and* cared for. This is the highest-value single action in
  the game: **$160–250** on a cow or sheep.
- **COLLECT_FERTILIZER** yields 1 per animal per day, for every surviving animal
  regardless of feeding. It does **not** accumulate — uncollected fertilizer is
  lost.
- A newly placed animal starts at `consecutive_unfed = 0`, so it survives its
  first day unfed.
- `DIG` cannot remove an occupied structure.

## 7. The market

Price is a pure function of market inventory:

```
price(inv) = base + sign · amp · f(|inv − I0|)      I0 = 10,000, floor $1
  sign = +1 below I0 (scarcity), −1 above (glut)
  amp  = target · base / f(T)
```

| Resource | Base | T | Below func | Below tgt | Above func | Above tgt |
|---|---|---|---|---|---|---|
| WHEAT | 25 | 400 | sqrt | 0.80 | log | 0.20 |
| CARROT | 35 | 450 | log | 0.20 | sqrt | 0.70 |
| TOMATO | 60 | 200 | linear | 0.40 | sqrt | 0.60 |
| STRAWBERRY | 120 | 100 | sqrt | 0.70 | linear | 1.60 |
| MELON | 250 | 300 | log | 0.20 | sq | 3.60 |
| EGG | 50 | 332 | linear | 0.40 | log | 0.20 |
| MILK | 160 | 122 | sqrt | 0.60 | linear | 1.60 |
| WOOL | 200 | 105 | log | 0.20 | sq | 3.20 |
| FERTILIZER | 100 | 200 | linear | 0.40 | linear | 0.40 |

*Verified against 4,059 inventory/price points from 25 live episodes: zero
mismatches. The competition servers use exactly these values.*

**How much each product absorbs before hitting the $1 floor:**

| Item | Units past equilibrium to $1 | Price at +25 / +50 / +100 / +200 |
|---|---|---|
| WHEAT | **unlimited** | 22 / 22 / 21 / 21 |
| EGG | **unlimited** | 44 / 43 / 42 / 41 |
| CARROT | 842 | 29 / 27 / 23 / 19 |
| TOMATO | 529 | 47 / 42 / 35 / 24 |
| FERTILIZER | 493 | 95 / 90 / 80 / 60 |
| MELON | 158 | 244 / 225 / 150 / **1** |
| MILK | 76 | 108 / 55 / **1** / 1 |
| STRAWBERRY | 62 | 72 / 24 / **1** / 1 |
| WOOL | 59 | 164 / 55 / **1** / 1 |

EGG and WHEAT use logarithmic glut curves and never meaningfully crash. The four
premium goods floor within ~60–160 units. **This asymmetry is the whole sell
policy.**

Other market rules:
- Only **WHEAT and FERTILIZER** can be bought back (`BUY_PRODUCT`).
- Orders process one unit at a time, concurrently across players.
- Buys quote at post-buy inventory, sells at pre-sell inventory, so an immediate
  buy-then-sell round trip nets exactly zero.
- A sale at the $1 floor does **not** add to market inventory.
- Max **10 orders per turn** — but quantity per order is unlimited, so this is
  rarely binding.
- `BUY_PRODUCT` and `BUY_ANIMAL` fail when the shed is full.

## 8. Town demand

Demand is the only thing that removes supply, so it sets what you can sell.

- **Shops** unlock every 3 days, **drawn with replacement**, capped at **8
  instances**. Each instance consumes 1 of each product it wants every 4 turns
  (6/day); **single-product shops consume double**.
- **Town centre** consumes 1 of every non-fertilizer product every 24 turns
  (1/day). **There is no scaling after day 10 or 20.**

| Shop | Wants |
|---|---|
| BAKERY | egg, wheat |
| PIZZA_SHOP | milk, tomato, wheat |
| BRUNCH_SPOT | egg, wheat, strawberry |
| YARN_STORE | **wool (2×)** |
| ICE_CREAM_SHOP | strawberry, milk, wheat |
| PET_CAFE | **carrot (2×)** |
| SMOOTHIE_SHOP | strawberry, milk |
| FARMERS_MARKET | wheat, carrot, tomato, strawberry |

Because shops are drawn with replacement, demand varies enormously between
games: wool demand ranges **1 to 37 per day** depending on how many YARN_STOREs
appear. **Melon appears in no shop at all** — only the town centre buys it, at
1/day, so melon gluts never recover.

Expected season totals (both players share these):

```
WHEAT 525   STRAWBERRY 426   CARROT 327   MILK 327
EGG 228     TOMATO 228       WOOL 228     MELON 30    FERTILIZER 0
```

## 9. Where the official docs are wrong

| Docs say | Actually |
|---|---|
| Score = money + inventory marked to market | **Money only.** Unsold stock scores zero. |
| Quadrants are 8×8 | **5×5** on a 10×10 board |
| Town centre scales 2× after day 10, 4× after day 20 | **No scaling.** Flat 1/product/day |
| `townCenterSellInterval` default 12 | Code default **24** |
| Animals produce nothing if not cared for | They produce the **base 1**; CARE only adds a banked bonus |

## 10. Workers

- One main farmer, plus hands hired **per day** (they vanish at end of day).
- Hire `n` costs `fib(n)`: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377…
  A full crew of ~14 is under $1,000/day, so hands are **cheap relative to what
  an action earns**.
- Hands spawn on shed-access tiles in **NWSE order**, so worker `i` starts in
  `["NW","NE","SW","SE"][i % 4]` — including on locked tiles, which is legal.
- All unit inventories **auto-drop into the shed at end of day**, so carrying
  harvest home costs nothing.
- **Shed capacity is 100 items**, and end-of-day **overflow is silently
  discarded** — this makes warehousing produce actively destructive.

## 11. Configuration defaults

| Parameter | Default |
|---|---|
| episodeSteps | 720 |
| actTimeout | 1 s |
| boardSize | 10 |
| startingMoney | 3000 |
| maxMarketOrdersPerTurn | 10 |
| turnsPerDay | 24 |
| shedCapacity | 100 |
| weedSpawnChance | 0.005 |
| townShopUnlockInterval | 3 |
| townShopSellInterval | 4 |
| townCenterSellInterval | 24 |
| farmHandCostMult | 1 |

## 12. Turn processing order

1. Validate actions
2. Apply all unit actions (both players simultaneously)
3. Process market queues (one unit at a time, concurrent across players)
4. Town consumption
5. End of day, if applicable: refresh plants → refresh animals → spawn weeds →
   drop inventories to shed → reset farmer/hands → unlock a shop
6. Refresh prices

---

See [BRANCH_FILE_GUIDE.md](BRANCH_FILE_GUIDE.md) for this agent's design, the
measurement rules that per-game variance forces, and the record of which
strategies have been tested and falsified.
