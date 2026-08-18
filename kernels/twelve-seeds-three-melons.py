# Twelve Seeds, Three Melons

*Field notes from a 600-Elo Kaggriculture farm. Not a medal writeup.*

This started as a postmortem of the two agents I actually put on the leaderboard. Someone upvoted it, so here is the next chapter: **v2–v5 never left the laptop**, and that is the interesting part.

| | **v0** | **v1** | **v2–v5** |
|---|---|---|---|
| On the board | 18 Aug 2026, 10:41 UTC | 18 Aug 2026, 11:34 UTC | not submitted |
| Public score | **548.7** | **609.8** | — |
| Idea | 8 cows + 4 sheep, a tiny learned market head | Copy the gold *calendar* | Make the calendar *exist* on the tiles |
| What happened | Animals existed. Melons did not. | I bought 12 melon seeds. I grew **3**. | 12 melons finally grew. Rating still would not. |

Bronze is roughly the top 10% of a 5,000-team board (around 2,200+). v0/v1 live in the starting-μ neighborhood. I am writing this because the engine fails *silently*, and because beating `starter` is a different sport from beating a gold opening.

If you only take one thing from v0/v1: **`yield_units > 0` does not mean HARVEST will work.**

If you only take one thing from v2–v5: **a local $69k vs `starter` is a veto line, not a bronze proof.**

## The game in one screen

Two farms, 30 days × 24 hours, bank cash at the buzzer. Unsold shed inventory is worth zero. Elo updates from win / loss / draw only — the margin does not matter.

| | |
|---|---|
| Start | $3,000, NW quadrant unlocked, one farmer |
| Land | NE $1,000 / SW $2,000 / SE $4,000 |
| Hire | Fibonacci 1, 1, 2, 3, 5… **resets every dawn**; hands vanish at dusk |
| Plant day | `consecutive_unwatered` starts at **1**. Skip water → weed tonight |
| Same-turn overplant | If you issue more `PLANT X` than you have seeds of X **this hour**, **every** X plant fails |
| Feed | Wheat must be in the **unit inventory**, not the shed |
| Rating | New agents start near μ = 600, then get a burst of games against similar scores |

Official tables live in the competition `README` / `AGENTS.md` and in `kaggle_environments==1.32.7`. I am not pasting anyone else's agent.

from kaggle_environments.envs.kaggriculture.kaggriculture import ANIMALS, CROPS

print("CROPS")
for name, row in CROPS.items():
    kind = "ongoing" if row["ongoing"] else "one-shot"
    print(
        f"  {name:12s} seed=${row['seed']:<4}  first={row['first_yield_day']:<2}  "
        f"max_day={row['max_yield_day']:<2}  max_yield={row['max_yield']}  {kind}"
    )

print("\nANIMALS")
for name, row in ANIMALS.items():
    print(
        f"  {name:12s} ${row['cost']}  {row['structure']:8s}  "
        f"first={row['first_yield_day']}  every {row['interval']}d  → {row['product']}"
    )

Melon is a **one-shot** crop: `first_yield_day = 10`, `max_yield_day = 12`, seed $80, base price $250. Wheat is cheap feed (`$10` seed, first yield on day 2). Cows make milk every 2 days after day 8; sheep make wool every 3 days after day 6. That is the whole economy in one paragraph.

## What medal farms actually do (from public replays)

I watched public gold replays and a sample of silver ones. I did **not** copy notebooks. The opening is boringly consistent:

- **Day 1:** 2 cows, 2 sheep, **12 melons**, **7 wheat**, NW only. Cash near empty.
- **Day 7:** buy NE.
- **Day 8:** herd around 6 cows / 3 sheep, still ~12–20 melons, ~8 strawberries.
- **Day 11:** harvest the melon patch. That is the first real banknote — on the order of **$15k**, not $600.

Then they split:

- **Gold-looking fork:** lock cows around **6**, grow sheep to **10–12**, buy SE after the melon payday.
- **Silver-looking fork:** push cows to **8–10**, freeze sheep at 4, skip SE.

Elo is a win-rate ladder. Dumping milk / wool / melon until the price is $1 makes both farms poor. You can "win" a $1,200 vs $800 game and still not climb.

## v0 — the 8-cow factory

**Goal:** 8 cows, 4 sheep, wheat to feed them, sell milk / wool / fertilizer when the price is not on the floor. A small discrete head for market timing; the field was scripted.

**What actually worked**

- Livestock got onto pastures. Wheat got into the ground. The farm *existed*.
- Locally it crushed `starter` / `random`. That number is meaningless on this board. Those agents do not play the gold opening.

**What did not**

- No melon IPO. No berry engine. No SE.
- Against anyone who *did* plant 12 melons, v0 was a dairy that showed up to a fruit fight.
- Public score settled around **548.7** after the first wave of games.

v0 is the agent I would still use as a sparring partner. It is not the agent I would still submit.

## v1 — I wrote the gold calendar and missed the plants

v1 was supposed to be the gold fork: melon IPO, strawberries after NE, cow cap when the opponent is already flooding milk, sheep expansion, SE after the payday.

The market orders on hour 1 were correct:

```text
BUY_SEED MELON 12
BUY_SEED WHEAT 7
BUY_ANIMAL SHEEP 2
BUY_ANIMAL COW 2
HIRE × 8
```

Seeds were in the pocket. The plants were not in the dirt.

Workers spent the morning hauling animals and building pastures. The first melon went down around **hour 10**. Day 1 ended on **3 melons and 2 wheat**, nine melon seeds still unused. Cash hit a few dollars, so **day 2 could not hire**. Those nine seeds sat through a full day of sun.

Public episodes (first 10 games): **5 wins, 5 losses**. Wins were against farms that also were not real. Losses were against farms that were.

| Opponent | Us | Them |
|---|---:|---:|
| Albert Yu | 71,668 | 41,170 |
| zhaowang | 71,459 | 40,004 |
| PromptEngineer48 | 60,595 | 28,117 |
| toshiconner | 50,558 | 35,693 |
| dlougen | 47,990 | 651 |
| Huseyin Battal | 52,829 | 58,491 |
| Dimas Renggana | 51,880 | 70,340 |
| Sushant Kumar | 43,223 | 63,310 |
| Siddharth Kumar Gopal | 23,257 | 83,779 |
| Manuel Pérez | **6,682** | 39,843 |

$6,682 is not a "close game." That is an opening that never happened. Score after the burst: **609.8**.

A calendar is not a policy. The policy has to *walk to an empty tile, PLANT, and WATER before dusk*.

## Three silent failures

Illegal actions in this engine are no-ops. The unit still burns the hour. That is the whole genre of bug.

### 1. Same-turn overplant wipes the crop

If eight hands all `PLANT MELON` and you only have five seeds **this hour**, you do not get five plants. You get zero. Budget the plants before you emit the actions. The official README states this; I still had to learn it the expensive way.

### 2. Planting day already counts as dry

```text
consecutive_unwatered = 1   # set in _new_plant
```

Skip water on the same day and the tile is a weed at midnight. "I will water tomorrow" is a eulogy.

### 3. The harvest that never happened

This is the one that ate v1 after I "fixed" planting.

One-shot crops (wheat, carrot, melon) spawn with **`yield_units = 1`**. Ongoing crops spawn with 0. A greedy policy that says `if yield_units > 0: HARVEST` will stand on a day-0 melon and harvest **every hour for ten days**.

The engine then does this:

from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS

# From kaggle_environments 1.32.7 — HARVEST, abbreviated.
# One-shot crops spawn with yield_units = 1, so this branch is live from hour one.
# If age < first_yield_day, HARVEST returns without removing the plant.
# Your worker still used the turn.

print("melon first_yield_day =", CROPS["MELON"]["first_yield_day"])
print("wheat first_yield_day =", CROPS["WHEAT"]["first_yield_day"])
print("one-shot spawn yield_units = 1")
print("ongoing spawn yield_units = 0")
print()
print("Watering bonus window for one-shot crops starts at ceil(max_yield_day / 2).")
print("melon bonus water: days", (CROPS["MELON"]["max_yield_day"] + 1) // 2, "to", CROPS["MELON"]["max_yield_day"])
print("Do not pull the patch on day 0 because the integer looks ripe.")

Gate harvest on **age**, not on `yield_units` alone:

```text
age = day - planted_day
harvestable = yield_units > 0 and age >= first_yield_day
```

For melon I would wait even longer: the watering bonus window is days 6–12. Gold farms pull around day 11, not day 10 with a single fruit in the basket.

A worker standing on an unripe melon saying HARVEST is indistinguishable from a worker who is AFK — except the AFK worker might wander off and water something.

## v2 — twelve melons, cows in the shed

v1's bug was "seeds in the pocket." v2 actually planted and watered the patch. Twelve melons reached yield 6. Locally that looks like a win.

It still lost to my own v0/v1 in the laptop, for two boring reasons:

1. **The herd never left the shed.** Day 0 spent the bodies on fruit. Cows and sheep sat in storage while pastures waited. New animals can skip a feed on day one; they cannot skip *placement*.
2. **The melon payday bought three quadrants in one afternoon.** Day 12 cash unlocked NE + SW + SE together. Suddenly there was dirt, no labor, and a watering list that did not fit in 24 hours.

A calendar that says "12 melons" is still a calendar. Someone has to walk the cow to a pasture *and* refuse to spend the IPO on three maps at once.

## v3 — one land per day, livestock before the dump

The smallest rules that actually moved the farm:

- **One `BUY_LAND` per calendar day.** Same hour: sell first, then buy land, so the melon check can pay for NE. The engine processes market orders in list order.
- **Place shed livestock before you SELL a backpack of fruit.** DROP/SELL is greedy. Cows waiting in the shed are free losses.
- Keep per-tile melon watering. Fall back to the old 8C4S factory only if the day-0 IPO failed.

v3 is the first version I would call "a farm" instead of "a shopping list." It is not a rating.

## v4 — pad the pastures the hour you buy NE

Gold replays put ~6 cows on *grass* by day 8, not 4 on grass and 2 in the shed. After NE, v4 builds up to 9 pastures the same day so the extra cows have a tile.

Hold 2 cows / 2 sheep until NE. One land per day. Do not tune against v0/v1 — they are the bottom of the pool and will bless any melon patch.

Local vs `starter`: on the order of **$60k**. I froze this file. It is still the best *adversarial* sparring partner I own. Later v5 only beats it **4 games in 8**. That 4/8 is worth more than a `starter` 8/8.

## v5 — delay the herd, lock 6 cows, then stop pretending checkpoints are Elo

v5 is the current laptop policy (I relabeled the file once; the weights did not change). Still **not submitted**. Daily submit slots are the expensive experiment. Local games are for not walking backwards.

The opening that finally hit the tiles:

- **Day 0:** buy 12 melon + 7 wheat. Do **not** place the 2C2S. Do **not** buy a feed bag. Animals can skip that first night; plants cannot.
- **Day 1:** PLACE, then buy wheat as feed.
- After NE: lock **6 cows**. That is the gold fork from the replays, not v0's 8-cow factory.
- Strawberries: at most 3 planters before day 8; one repair planter from day 12 if the patch is still short.

I built four snapshots vs `starter` only. They are a gold *calendar* tape, not official gates:

| Gate | When | Ask | v5 vs `starter` |
|---|---|---|---|
| C0 | day 1 hour 0 | 12 melon, 7 wheat **on tiles** | **8/8** |
| C1 | day 8 hour 0 | NE, 6C3S on grass, ≥10 live melon, ≥6 berry | **0/8** — dropped |
| C2 | day 11 hour 0 | still 6 cows, melon still up or ~72 in the shed | **7/8** |
| C3 | day 15 hour 0 | still 6 cows, ≥8 sheep, ≥8 berry | **6/8** |

Mean vs `starter`: about **$69k**, 8/8 wins. That number crushed my brain for a week. It does not crush a gold opening.

### C1 is a calendar obsession

Day 7–8 is the same 48 hours as "lock 6 cows" and "pay for NE." Labor, cash, and the 10-slot market are all full. I tried moving the berry seed gate, adding planters (3→5–6), waiting for wool before NE, leftover cash after NE, buying berry seeds on the NE hour. Every lever either kept C1 at 0/8 or knocked C2 from 7/8 to 0/8.

Eight berries over 30 days are about $4k. On a $69k `starter` mean that is 6%. I stopped. The cost of abandoning C1 is about zero. The cost of another ticket on it is a submit slot.

### The knob that looked like C3 and was not

Two failing seeds showed sheep escaping (`consecutive_unfed >= 2`), sheds empty of wheat by late morning, 9–13 animals unfed at dawn. The feed bag was `max(4, herd + 2)`. Carried wheat counts as inventory, so two haulers with 6 each can suppress the buy.

I raised the bag to `herd + 6` from day 12. **C3 went 6/8 → 3/8.** Mean cash went *up*. Extra wheat crowded out the eighth sheep. I reverted. I did not then raise the feeder cap. One failed axis is enough.

## What actually predicts a public score

| Opponent | v5 result | What it is worth |
|---|---|---|
| `starter` / `random` | 8/8, ~$69k | Did we bankrupt. Nothing else. |
| Frozen v4 | **4/8**, ~$46k | First number that is allowed to scare me |
| Public GitHub scripts | 8/8, they finish ~$24k–$42k | Bottom of the pool. Some of those authors sit near 550–900 Elo. |
| Public **gold-opening notebooks** (replay tapes + a weed patch) | **0/8 × 3**, they finish ~$119k–$124k, I finish ~$28k–$33k | This is the hole. Some of those authors sit on the gold/silver line. |

The tapes are not a thinking policy. They still execute 8 cows / 4 sheep (or 9/4) on three quadrants, dump produce, and my $69k `starter` farm becomes a $30k farm. A few games I ended under $8k. That is a milk-and-melon war, not a missing strawberry on day 8.

I am not pasting those notebooks and I am not pasting v5. Everyone who clones a high-vote tape is already in the same queue. The lesson is the matchup, not the gist.

This strategy family — 6-cow lock, delayed herd, calendar vs `starter` — does not look like stable bronze to me. The missing pieces are ones the laptop cannot grade: selling into an opponent who actually dumps, logistics after herd 12, and a late-game engine after SE. None of those are "hire two more berry planters on day 7."

Submit slots are the eval. Local gates are the fail-closed switch.

## What I changed my mind about

1. **Local vs `starter` is a smoke test, not a rating.** 20/20 and $69k mean you did not crash. They do not mean you can beat the opening that medal replays — and the public notebooks cloned from them — actually play.
2. **Buy seeds, then plant, then water, then animals.** Livestock can wait in the shed overnight. Melons cannot wait in the pocket, and they cannot wait for a feed bag either.
3. **Keep a cash floor on day 0.** Fibonacci hires plus 12 × $80 seeds plus two sheep will spend you into a day-1 lockout.
4. **Do not harvest a one-shot crop because the integer is 1.** Read `first_yield_day`.
5. **Win rate, not museum cash.** Flooding the shared market to $1 is how two "rich" farms both stay at 600 μ. Against a gold tape, my museum cash is the thing that dies first.
6. **SE is a post-IPO buy, and maybe later than that.** If you already cannot feed 9–13 animals at dawn, unlocking 25 more tiles is a watering sentence.
7. **One land per day. Same-hour SELL then BUY_LAND.** Three quadrants in one afternoon is how v2 died.
8. **Lock 6 cows.** The 8-cow factory was v0. The medal median in the replays I watched did not do that in a milk war.
9. **Do not tune against v0/v1.** They bless any melon patch. Tune against your last frozen self, then against a public gold opening, then spend a submit.
10. **Drop a checkpoint that only the calendar wants.** C1 berries were 6% of a `starter` mean and 100% of a labor collision.

I am still not dropping a third agent in this notebook. The point is the autopsy. v5 stays on the laptop until a submit slot is worth more than another local knob.

## If you are about to submit tonight

- Count live melon tiles at day-1 dawn, not seeds in `private`.
- Count how many `PLANT MELON` you emit **this hour**.
- If a unit repeats `HARVEST` on the same plant for more than one hour, log the plant's `planted_day`. You are probably in bug #3.
- Watch one of your own public replays before you trust a local 20/20.
- If you added a "bronze checkpoint" vs `starter`, keep it as a veto. Play your last frozen self, then a public gold opening, before you spend the slot.
- If day 7–8 is already herd + NE, do not also demand 6 berries on that dawn. I already paid that tuition.

The engine is the spec. Replays are the meta. `starter` is a unit test. Public gold notebooks are a different unit test, and they are the one I was missing.

If this saved you from a three-melon opening — or from a $69k `starter` mean — an upvote is appreciated. If your day-1 plant count is also embarrassing, drop it in the comments.
