# Kaggriculture — full handoff

Written 2026-09-06 for a fresh agent picking this work up. Everything here is
measured unless marked otherwise.

## 0. If all you have is a single agent file, read this first

**There are two different agents in this project and they are not the same
lineage.** Getting this wrong means optimising the wrong thing.

| file | what it is | strength |
| --- | --- | --- |
| `agent_combined.py` | the **route agent** — a frozen 720-step action tape plus adaptive layers. **This is what we actually submit.** | currently **1304.9** |
| `main.py` | the **CMA-ES policy agent** — a live policy, no tape. Abandoned lineage. | peaked at **864**; loses **2-38** head to head |

Kaggle requires the submitted file to be named `main.py`, so `agent_combined.py`
is uploaded *as* `main.py`. The file literally named `main.py` in the project is
the weak one. If you were handed `main.py` and it is ~75 KB of policy code with
functions like `final_day_strategy`, you have the 864-rated agent, not the
1305-rated one.

Everything below marked with a file path refers to tooling in our repo that you
may not have. Where that happens the **measured result is inlined**, so you can
use the finding without the tool. Rebuild the tools if you want to re-measure —
the promotion protocol in §10 is the part that matters, not the code. Where an early claim was later
contradicted, both versions appear — the corrections are more useful than the
tidy version, and several are places where a second pair of eyes might find we
are still wrong.

**Read this section first if you read nothing else:** we ran ~11 substantive
experiments over two days and *all of them failed*. The only things that work
are four small edges shipped weeks ago. Meanwhile our rating fell 400 points
while we did nothing. So do not assume the search has been done well — assume
there is something we missed, and treat §7 (mistakes) as seriously as §5.

---

## 1. Situation

| | |
| --- | --- |
| Competition | Kaggriculture, Google/Kaggle, $50k, 10 × $5,000 prizes |
| Deadline | **2026-09-30** final submission; games run to ~2026-10-15; then final |
| Today | 2026-09-06 — **24 days left** |
| Our best active | **1304.9** (submission 55677927), ~#2,406 of 7,896, top 30% |
| Second active | 1257.6 (55657021) |
| Leader | 2991.3 — **gap of 1,686 points** |
| #1000 | 1940.3 — gap of 635 |

**Our rating is falling.** Two weeks ago these same two submissions were at
1698.9 and 1667.1. They lost ~400 points each without any code change. The agent
did not get worse; the field got better. Eight of the current top 15 were not in
the top 15 two weeks ago, several gaining 700–1,200 points.

A retired submission shows 1747.4, which is a *frozen* number from when it
stopped playing. It is not a better agent. We quoted it as an achievement for
some time; do not repeat that.

### Scoring rules (read from the official pages, quotes verified)

- Five submissions per day. **"Only the latest 2 submissions are tracked."**
- **"On the leaderboard, only your best-scoring bot will be shown."** So a
  weaker second submission cannot drag the team down.
- Each new submission **retires your oldest active one**.
- Final: *"Games will continue to run for approximately two weeks... A final
  Bradley-Terry tournament will be run on those episodes."* So the final score
  is decided by **post-deadline play**, not by the rating displayed now.
- Rating moves on **win/loss/tie only**. Coin margin is irrelevant. A $172,590
  win and a $325 win move it identically.
- Matchmaking pairs similar ratings, so win rate converges to ~50% for everyone.
  **The rating is the signal; the win rate is not.**
- Using another team's publicly-recorded route is *permitted* (only private code
  sharing between teams is banned). Attribution is a community norm here, not a
  rule.

### 1b. The live record — 442 episodes of submission 55677927

This is the most important diagnostic in the document.

```
RECORD  179W-263L   40.5%
  our avg bank   86,956      opponent avg   89,114
  in wins        86,244  vs  80,104
  in losses      87,441  vs  95,246
```

Split by episode age (oldest to newest quarter):

| slice | games | win rate | our mean bank |
| --- | ---: | ---: | ---: |
| oldest 25% | 90 | **56.7%** | 89,712 |
| 2nd 25% | 90 | 36.7% | 83,551 |
| 3rd 25% | 90 | 35.6% | 86,676 |
| newest 25% | 92 | **35.9%** | 84,350 |

**Read this carefully: our win rate halved while our production did not move.**
We bank ~85–90k in every slice, early and late, winning and losing. What changed
is the opposition — in losses they bank **95,246** to our 87,441.

The agent did not degrade. **The field overtook it.** That is the entire story of
the 400-point drop, and it explains why every market-layer and timing experiment
we ran came back neutral or negative: we were polishing the margins of a design
that had already been outgrown. The deficit is roughly **8,000 coins a game of
production**, not a subtlety of sale timing.

Loss structure (the shape of the problem):

```
10 losses under $305      -44, -70, -121, -169, -178, -240, -241, -245, -252, -304
worst losses            -35,670  -35,668  -32,164  -29,897  -28,630
biggest wins            +139,539  +86,910  +63,004  +53,078   <- all from the OLDEST episodes
```

Two separate populations. A large tail of games lost by **under $305** — those
are winnable by any consistent small edge. And a tail of **−30,000 structural
mismatches** against builds we simply cannot match. Note also that every one of
our biggest wins is from the earliest episodes, against weak opponents we no
longer meet.

---

## 2. The agent we ship

`agent_combined.py`, generated by `kernels/build_combined.py`. A frozen 720-step
action tape ("route") lifted from a public notebook around 2026-08-09, wrapped in
adaptive layers. **The tape is now ~4 weeks stale**, which is the most likely
single cause of the decay.

```
LOOKAHEAD            3          premium-sale preemption window
EAGER_FLOOR_FRAC     0.3        eager seller floor
EAGER_SELL_ITEMS     ('EGG','CARROT','TOMATO')
CARROT_SWAP          13 (step, hand) pairs
CARROT_PRICE_GATE    1.0
METER_RATE           None       disabled, measured negative
TOMATO_SWAP          ()         disabled, measured negative
FERTILIZE_WHEAT_AGE  None       disabled, measured negative
HERD_SWAP/PASTURE_TILT/MELON_PATCH/FEED_BUY_CEILING  all disabled
```

Farm it produces: 8 cows, 4 sheep, 137 wheat tiles, 17 melon, 36 strawberry,
13 carrot, 10–14 hands. Mean bank 90,696 across 486 live games.

---

## 3. What works (validated on held-out seeds, both seats, two disjoint blocks)

| Edge | Combined record vs itself-without | Original estimate |
| --- | ---: | --- |
| Preemption lookahead 3 (vs 1) | **58-2** | 31/32, SPRT 7-0-1 |
| Eager seller (EGG/CARROT/TOMATO at 0.3× base) | **43-5** | +51 wins |
| Carrot swap (13 end-of-season wheat → carrot) | **40-8** | +12 wins |
| Carrot price gate (pick crop from day-26 market) | **25-11** | +3 wins |
| Weed repair (DIG when a weed blocks a PLANT, resync) | inherited | in every top agent |

**Why these and nothing else:** each adds output or sales using turns already
spent, or substitutes an action the route already performs. The carrot swap is
the clean case — carrot waters at ages 2–3 and the route's end-of-season wheat is
lifted at age 3, so carrot fits exactly the hole wheat leaves. It was never that
carrot is a good crop.

---

## 4. What failed, with mechanisms

### Production / route changes

| Method | Result | Mechanism |
| --- | ---: | --- |
| Melon patch (extra melon tiles) | −99 wins | Route carries choreography only for the assets it expects |
| Goose herd swap | −105 wins | Same, plus eggs glut on 2 shops at a $50 base |
| Day-0 cow-for-sheep swap | −$42k | Ends with 5 empty pastures; `PLACE` needs a matching structure |
| Pasture retargeting | −2 wins | No effect |
| **Tomato swap** (4 donor sets) | **−146 to −190 wins** | An `ongoing` crop yields `max_yield` units **in total then dies**. Tomato = 4 units at interval 1, worth ~half a strawberry tile |
| Fertilize wheat, age 2 | −3,335 margin | Two dry days turn a plant to WEED; wheat's window opens at age 2, so removing that watering kills it |
| Fertilize wheat, age 3 | −96 (neutral) | Arithmetically identical to not fertilizing |
| Fourth quadrant (SE, $4,000) | 10-0 loss | Not our test — Rayk Kretzschmar, 450 games, three implementation families |
| Role specialisation (CMA-ES) | no effect | The apparent +$8,399 was an RNG artifact worth $415 |

### Market / timing changes

| Method | Result | Mechanism |
| --- | ---: | --- |
| Feed-buy ceiling (30/20/12) | −44/−49/−105 wins | Shed wheat feeds the herd **and** scheduled sales; at 12 the animals starve |
| Sale meter, price floor (0.85/0.70/0.50) | −26/−32/−47 | A price floor is not a rate limit: admits 32–40 units at equilibrium, 0 once glutted |
| **Sale meter, town rate cap (1.0/2.0/4.0)** | **−51/−64/−75** | Milk, strawberry, wool **clear** the market. Selling earlier only raises average inventory, and average inventory sets average price |
| Eager-sell fertilizer | −151 wins | The route fertilizes 100% of its strawberry from that same shed |
| Eager-sell fertilizer + wheat | −208 wins | Gives back *every* win — shed wheat is the feed chain |
| Front-running / SELL slot reordering | 0 coins available | We and rivals already sell in slot ~0.3; the race is a dead heat |

### Whole-agent replacements

| Method | Result | Note |
| --- | ---: | --- |
| CMA-ES policy agent (`main.py`) | 864 rating | vs 1747 for the route agent at the time |
| Policy agent + day-29 endgame block | 2-38 vs incumbent | **but 37-3 vs its own parent, +5,269/game** — the endgame idea is good, the base is not |
| Lifted route v15 (iVl44d) | 6/16 | $12k worse than the route it beat in its own episode |
| Lifted ReCurSiON (#17) | 0/6 | −4,442 a game |
| Lifted Ryo Hasegawa (#1) | 0/6 | −6,486. **Rank does not predict transplantability** |
| Lifted Arman Tuganbaev (#4) | 0/6 | −11,098 a game |
| Lifted MiMi (#5) | 6/6 then **8-32** | Won on its screening seeds, lost on held-out |

---

## 5. Verified engine mechanics (saves you re-deriving these)

From `.venv/Lib/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`.

- **Price curve.** Per-product shape each side of equilibrium (I0 = 10,000).
  Three products use `hinge` on the **scarce** side — CARROT, TOMATO, EGG —
  which is flat until inventory falls T below equilibrium then runs away
  quadratically (`HINGE_GAIN = 8.0`). Measured in live replays: CARROT reaches
  **15× base**, TOMATO **11×**. Every other product tops out near 2×.
- **Glut side collapses fast.** MELON, MILK, STRAWBERRY, WOOL all reach the
  $1 `PRICE_FLOOR` in ordinary games — strawberry needs only 63 units above
  equilibrium, wool 59, milk 76, melon 158. But this is the *momentary* price at
  the bottom of a dump; realised averages are 65–159.
- **End-of-season inventory** (126 live games, avg vs equilibrium):
  `CARROT −307, EGG −230, TOMATO −225, WHEAT −142, WOOL −27, STRAWBERRY +6,
  MILK +38, MELON +149, FERTILIZER +437`. Milk/strawberry/wool **clear**.
- **Nothing consumes FERTILIZER.** No shop lists it and
  `TOWN_CENTER_PRODUCTS = [p for p in PRODUCTS if p != "FERTILIZER"]`. Its price
  only ever falls: 100 on day 2 → 11 by day 29.
- **Town demand varies hugely by game.** Shops unlock `min(8, day//3)` **with
  replacement**. Measured per-day demand across 60 replays: WOOL 0–60 (**zero in
  32% of games**), CARROT 0–54, MILK 6–36, STRAWBERRY 6–42, **MELON always 0**
  (no shop buys melon; only the town centre, ~1/day).
- **Market resolves slot-by-slot in lockstep.** For slot *i*, both players are
  quoted the **same pre-commit inventory** and both commit. Verified: same slot
  = exact tie; one slot earlier takes the *solo* price and the later seller eats
  the whole depression; 1 slot ahead = 9 slots ahead; splitting one product
  across two slots is strictly worse.
- **`BUY_PRODUCT` is quoted at post-buy inventory**, so a buy/sell round trip
  against an unchanged market nets zero *by design*. Wheat "arbitrage" is not a
  thing (measured: buy 39.2, sell 40.0).
- **Ongoing crops die.** `production_count == max_yield` sets
  `max_lifespan_step`. Tomato = 4 units over 4 days then dead; strawberry = 4
  units over 8 days then dead. **`ongoing` does not mean perennial.**
- **Two consecutive unwatered days turn a plant to WEED.**
- **Wheat is 6 fertilized, 4 unfertilized** (official table). Ours peaks at 3.80
  and is never fertilized.
- **One FERTILIZE covers day, day+1, day+2** — exactly wheat's 2–4 window.
  It spends from the **worker's own inventory**, not the shed.
- **Shed cap 100**, non-seed items, overflow destroyed. Ours peaks at 96.
- **`SELL` spends from the shed; `HARVEST` fills the unit inventory.** No DROP
  means the market cannot see the goods.
- **Step 718 executes; action index 719 does not.**
- **`townCenterSellInterval` = 24** in the current config (was 12 in a legacy
  regime — some public agents branch on this).
- `maxMarketOrdersPerTurn` = 10, `actTimeout` = 1 s/step, hire cost `fib(n)` per
  hire per day (~$143 for ten hands).
- **RNG confound:** `_end_of_day` seeds one RNG, runs `_spawn_weeds` for BOTH
  farms (consuming a variable number of draws), *then* draws the shop. So your
  agent's actions change which shops open. Use `fixed_town.py` when comparing
  variants or your numbers are meaningless.

---

## 6. The field

Fingerprint teams by hashing **day 0 only**. Full-season hashes are useless —
our own known-fixed tape produces 29 distinct full-season hashes over 91 games
because weed repair shifts everything. (`route_census.py`)

As of 2026-08-22 (needs refreshing): one opening hash `8f9f531a1926` was shared
by **17 teams spanning ranks 6 to 222**. The top four each ran a *distinct*
opening. Our opening was byte-identical to Kaito Fukami's, who was ~1,000 rating
points above us at the time.

Public notebooks decoded and runnable as opponents in `kernels/`:
`rayk_c92.py`, `rayk_c94.py`, `rayk_c95.py`,
`15-16-strict-future-v25-meta-reset__main.py` (Kaito v25), plus four lifted
routes (`agent_mimi.py`, `agent_recursion.py`, `agent_ryo_hasegawa.py`,
`agent_arman_tuganbaev.py`). All stdlib-only, all expose `agent()`.

Caution: these published artifacts are much weaker than their authors' live
ratings suggest. Several are explicitly marked "not submitted" in their own
notebooks. Our agent beat them 58-2 while sitting 1,000 points below them.

---

## 7. Mistakes we made — audit these

This is the section most likely to contain your opportunity.

1. **We promoted on the wrong instrument for weeks.** `bench_losses.py` replays
   frozen opponent tapes on their recorded seeds. It scored a lifted route
   **+24 wins** over the agent that then beat it **32-8** on held-out seeds.
   Wrong sign, not noise. It detects breakage reliably; it cannot rank
   comparable agents. Every "+3 wins" style result before ~2026-08-24 was
   measured this way. We re-validated the four shipped edges afterwards and they
   held — but nothing else was re-checked.
2. **Two harness bugs, both found late.** (a) `benchmark_pool` caches one module
   per file path, so two entrants differing only by a constant override shared a
   namespace and *every variant matchup silently played itself* — tell was an
   exact 0.0 mean margin. (b) `fixed_town` materially changes answers: MiMi went
   10-10 with it and 8-32 without. Both are fixed in `ladder.py`, but assume
   other harnesses in this repo may still have similar flaws.
3. **We compared absolute banks across games for a long time.** Invalid — agent
   actions perturb the RNG that draws the town, so two variants play different
   economies. One "+$8,399 improvement" was worth $415 with the town pinned.
4. **We screened on 3 seeds and believed it.** MiMi went 6/6 on its screening
   seeds and 8-32 held out.
5. **We claimed production matched rank 1** on the strength of a *single*
   replay. Across 105 live losses it does not — top opponents bank 130–141k
   where we bank 112–127k.
6. **We diagnosed the tomato failure wrong first** (blamed watering; it was the
   ongoing production cap). The corrected mechanism is in §4.
7. **We built a "rate limit" that was a price floor** and reported its failure
   as evidence against metering. It was evidence against price floors.
8. **We let the rating decay unmonitored for two weeks.** −400 points. Nobody
   was watching the leaderboard while we optimised offline.

---

## 8. Rules we derived (may be wrong — test them)

- Markets that **clear** cannot be gamed on timing.
- Selling early is free only where demand is **never met** (carrot, egg, tomato).
- A crop substitution works only where the **donor's existing actions fit the new
  crop's calendar**.
- An item the farm **consumes** is not surplus (fertilizer, wheat).
- Adding actions to a route with no idle capacity fails — **0 for 8**.
- Rank does not predict transplantability.

---

## 9. Untried / unexploited, with measured sizes

1. **Refresh the base route from *current* top replays.** Ours is ~4 weeks
   stale and the field has moved twice since. We tried this on 2026-08-24 with
   2026-08-20 replays and 3 of 4 lifts lost outright — but the top 15 has since
   turned over almost completely. **This is the highest-prior item and it has not
   been retried against the current meta.**
2. **Fertilize wheat: ~12,000 a game.** 137 tiles × 2 units × ~44 realised.
   Needs an *added* FERTILIZE from a worker who is idle, standing on the tile,
   and carrying a unit. Substituting a watering kills the plant (measured).
3. **666 of 967 CARE actions do nothing** — 442 on tiles with no animal. 10.5%
   of all field actions. Only ~38 are convertible in place; the rest needs
   moving workers.
4. **Town-adaptive production.** Wool demand is 0 in 32% of games and up to
   60/day in others; we produce the same mix regardless. The observation exposes
   `unlocked_shops`, and `_town_drain_per_turn()` in `agent_combined.py` already
   computes per-item demand.
5. **The day-29 endgame block** in `kernels/candidate_endgame.py` is worth
   **37-3, +5,269/game** against its parent. It does not transfer to the route
   agent (which already banks everything), but the *idea* — same-turn deposit
   then liquidation — may generalise.
6. **A genuinely different agent.** Our two slots are **100% correlated** — they
   win and lose the identical games. No parameter change decorrelates. Since only
   the best bot counts, a second, structurally different agent is free
   optionality.

Items 2–4 all require **authoring actions in a route with no spare capacity**,
which is the wall we never got through. A policy agent has no such wall — but
ours rates 864. Reconciling those two facts may be the real problem.

---

## 10. Tools in the repo

| File | What it does |
| --- | --- |
| **`ladder.py`** | **The good instrument.** Live code vs live code, both seats, held-out seeds, Bradley-Terry, `fixed_town` on, entrants can carry constant overrides, veto opponent supported |
| `diversity.py` | Per-game outcome agreement between candidates — measures whether a second slot actually hedges |
| `bench_losses.py` | Replays recorded opponents. **Trust large negatives, never promote on a positive** |
| `route_census.py` | Fingerprints teams by day-0 opening hash; finds fixed tapes |
| `route_diff.py` | Diffs our route against a named team's, per day |
| `lift_route.py` | Builds a candidate from another team's replay, keeping our wrapper |
| `wasted_actions.py` | Audits no-op field actions against the engine's own preconditions |
| `sale_race.py` | Realised price per unit per product, ours vs theirs, plus slot indices |
| `scarcity_scan.py` | Scarce- and glut-side price extremes across replays |
| `melon_audit.py` | Melon watering-window yield check (we are clean at 100% of cap) |
| `spar_live.py` | Live head-to-head vs a named agent file, both seats |
| `fetch_daily_episodes.py` | Pulls and indexes Kaggle's daily public episodes |
| `analyze_live_submission.py` | Pulls all replays for one of our submissions and profiles them |
| `fixed_town.py` | Common random numbers for the town — **use when comparing variants** |
| `kernels/build_combined.py` | Generates `agent_combined.py`; every failed experiment is documented in-place next to its constant |

### Promotion protocol

1. `ladder.py`, both seats, **two disjoint held-out seed blocks**, 20 seeds each.
2. `agent_combined.py` as **veto** — losing to the agent you replace disqualifies.
3. Two unrelated external families in the pool.
4. Report per-opponent records; win rate is pool-relative (Rayk C95 measured 10%
   in one pool and 76.9% in another, both correct).
5. Check: DONE/DONE, zero exceptions, <1 s/step, stdlib only, nothing unsold.

```bash
python ladder.py --seeds 9300-9319 --workers 10 --pool \
  "candidate.py#candidate" "agent_combined.py#INCUMBENT" \
  "kernels/rayk_c95.py#C95" "kernels/15-16-strict-future-v25-meta-reset__main.py#Kaito"
```

---

## 11. Where to go next

Our track record is 0 for 11, so treat all of this as hypotheses with measured
premises, not as a plan that is known to work. Three tracks, in the order we
would spend time on them.

### Track A — the route agent (the one that is competitive now)

**A1. The tape is stale, and that is measured, not guessed.** §1b: production
flat at ~86k across 442 episodes while the field moved to ~95k in the games we
lose. The tape was lifted around 2026-08-09 and the top 15 has turned over
almost completely twice since.

**The target is specific: ~8,000 coins a game of production.** Not "be better".
For scale, the four edges we ship are worth a few hundred to ~2,000 each.

**A2. The untested variant: lift a current route AND rebuild the market layer
around it.** Every failed lift (ReCurSiON 0/6, Ryo 0/6, Arman 0/6, MiMi 6/6 then
8-32) kept *our* wrapper bolted onto *their* tape. A tape without its owner's
adaptive market layer is not that owner's agent, which is a plausible reason the
rank-1 route scored 0/6. Rayk Kretzschmar's public diary did exactly this
separation deliberately — refresh the field tape, then build a *new* market
controller for it (his C68 and C71) — and it was where his gains came from.
**Nobody here has tried it.**

**A3. Two distinct loss populations, attack the cheap one first.** §1b: ten
losses under **$305** (down to −$44), and a separate tail of **−30,000**
structural mismatches. The near-misses flip on almost nothing; the tail needs a
different farm. Do not average them together — they are different problems.

### Track B — the CMA-ES policy agent (the better architecture long run)

Currently 864 and losing 2-38 to the route agent, so it is not the play for a
24-day deadline. But the structural case for it is strong and worth stating,
because whoever works on this after the deadline should be investing here:

- **The route agent has a hard ceiling and a decay clock.** Its value is that
  someone else's plan is baked in. It cannot improve on its own — the only moves
  are re-lift (3 of 4 failed) or add layers (**0 for 8**, because the tape has no
  idle capacity). And it goes stale by construction: §1b is what that looks like.
- **A policy has no such ceiling.** Improvements generalise across game states
  instead of being pinned to one recorded season.
- **The evidence that it accepts improvement:** the day-29 endgame block added to
  it scored **37-3 against its own parent, +5,269 a game** — the largest single
  gain anyone produced in this project. The identical idea had *nowhere to go* in
  the route agent, which already banks everything.

What it needs is not subtle: **~30,000 coins a game of production** to reach
parity. Its measured deficit against the route agent on one reference game was
MILK −32,696 (it ran **14 cows to the route's 8 and still sold 30% less milk**),
WHEAT −17,800 (it had essentially no wheat program, which is both revenue and
the feed chain), and **1,027 wasted PASS turns against the route's 323**. Its
problem is throughput and labour utilisation, not strategy.

### Track C — fusing them

The most interesting direction, and the one with a measured premise nobody has
acted on. Three designs, best first.

**C1. Give the policy the turns the tape wastes.** This is the strong one.

We measured the route agent's action budget directly:

```
6,349 live field actions per game
  711 audited no-ops     (11.2%)  -- CARE on a tile with no animal (442),
                                     CARE already done today (224),
                                     WATER on a tile with no plant (30)
  323 PASS               ( 4.8%)
-----
~1,034 unit-turns a game, ~15.5% of the budget, doing nothing
```

Every idea that would pay — fertilizing wheat (**~12,000 a game**), reclaiming
CARE turns, town-adaptive production — died on the same wall: *the tape has no
spare actions*. But **15.5% of its actions are already spare; they are just
spent on nothing.**

The fusion: run the tape as the default, and when a unit's scheduled action
would be a **verified no-op** (check the engine's own precondition — the code is
in `wasted_actions.py` and the preconditions are listed in §5), hand that unit's
turn to the policy for that step.

Why this is different from all eight failures: it **does not add actions and does
not remove any**. The tape's real work is untouched, so the choreography cannot
desync — which was the mechanism behind melon patch, geese, cow swap and the
lifted routes. It only replaces actions that provably do nothing.

Caveat, stated honestly: a worker doing a no-op CARE is usually *parked somewhere
useless*, so the policy will often need to spend the turn moving before it can do
anything. We measured that only ~38 of the 711 no-ops sit on a tile where an
immediate useful action exists. So the gain is not 711 turns of free work — it is
711 turns of *freedom*, and the policy has to earn the rest back through better
positioning. That is exactly the kind of thing a policy is good at and a tape
cannot do at all.

**C2. Frozen field tape + policy market layer.** The public meta converged on
near-identical *field* plans and differentiated on *market execution* — Rayk's
own promotions changed ~20 field turns and **112 market turns**. Our market
orders are frozen in the tape. Replacing just the market half with a live policy
is a clean split along a seam the game already has, and it is what C68/C71 did.
Lower risk than C1, smaller ceiling.

**C3. Tape as a warm start for CMA-ES.** Use the tape's behaviour as an
imitation target, then let CMA-ES improve from there — the policy inherits a
competitive farm instead of learning one from scratch, which is where its 30,000
coin deficit comes from. This is the principled long-run answer and much too
slow for 24 days.

### If you only do one thing

**Before the deadline:** A2 (lift a current route *and* rebuild its market
layer). It attacks the measured problem and it is genuinely untested.

**If there is time for two:** add C1. It is the only idea we found that
sidesteps the 0-for-8 wall rather than running into it, and its premise —
15.5% of actions wasted — is measured rather than assumed.

**After the deadline, or if you have longer:** Track B. The route agent is a
rented lead and the rent goes up every week.
