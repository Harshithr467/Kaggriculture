# What the top notebooks know, and what this branch does about it

## Result: every shipped edge validated on held-out seeds

`ladder.py` plays live code against live code, both seats, on seeds the
candidates were never screened on, with the town on its own RNG stream. Each
edge entered against the version of the agent without it. Two disjoint blocks:

| ablation | seeds 9000-9009 | seeds 9100-9119 | combined |
| --- | ---: | ---: | ---: |
| shipped vs LOOKAHEAD=1 | 20-0 | 38-2 | **58-2** |
| shipped vs no eager seller | 11-1 | 32-4 | **43-5** |
| shipped vs no carrot swap | 11-1 | 29-7 | **40-8** |
| shipped vs no price gate | 11-3 | 14-8 | **25-11** |

Consistent ordering across both blocks: lookahead 3 is the largest edge, then
the eager seller, then the carrot swap, then the price gate. The gate is the
weakest at 25-11 with a mean margin of +58 to +244 — small, but on the right
side of zero and significant (p ≈ 0.014 on the decisive games).

Pairings summing to fewer than the full game count are exact ties, and they are
legitimate between near-identical variants: when the price gate picks wheat, the
gated and ungated agents make identical decisions and play an identical game.
Ties between genuinely *different* agents are the bug signature described below.

**I predicted this would come out the other way** — that the old benchmark's
+3 and +12 figures were noise and reverting would be the honest gain. Wrong.
`bench_losses` is unreliable for *ranking* comparable agents, which is not the
same as being wrong about our own agent's edges. I conflated the two.

Two harness bugs found and fixed along the way, both worth remembering:

- `benchmark_pool` caches one module per file path, so entrants differing only
  by an override shared a namespace and every variant matchup silently played
  itself. Tell: an exact 0.0 mean margin and identical records across variants.
- `fixed_town` materially changes answers. MiMi's route went 10-10 against our
  agent with it and 8-32 without. For comparing variants it is the correct
  control; for estimating real win rate the live dynamics are what happen.
  Report both.


Four notebooks pulled on 2026-08-23:

| Notebook | Author | What it actually contains |
| --- | --- | --- |
| `kaggriculture-findings-from-zero-to-top-meta` | Rayk Kretzschmar | 56 cells of engine mechanics, a full build diary c14→C95, and three complete agent sources |
| `15-16-strict-future-v25-meta-reset` | Kaito Fukami | Meta census, negative ablations, one complete agent source |
| `v111-8c4s-economic-core-premium-lead` | Deniz Eryilmaz | 8C/4S route + one-turn premium front-run |
| `v16-rc5-high-score-8c-4s-premium-market-lead` | boatlee | **byte-identical to the above** — one is a fork |

Only three distinct notebooks. All four ship their agent as an embedded
base85/base64+zlib blob; all four decode cleanly and every SHA-256 matches the
value the notebook asserts. Decoded and kept:

```
kernels/rayk_c92.py                              70,317 b   7b13e693…
kernels/rayk_c94.py                              75,078 b   7b0e5a7b…
kernels/rayk_c95.py                              75,098 b   489f5d19…
kernels/15-16-strict-future-v25-meta-reset__main.py  21,330 b   9bdfbafb…
```

All are stdlib-only and expose `agent()`, so they run directly as sparring
partners. That is the single largest immediate gain here: we now have four
real, adaptive top-meta opponents instead of frozen replay tapes.

---

## 0. The finding that reframes everything: the premium market is worth 1 coin

Reading the notebooks sent me to the price table, and the price table says
something none of the notebooks state outright. Measured peak market inventory
across the same 60 live replays (`scarcity_scan.py`, glut side):

| item | glut shape | worst peak inv | price there | % of base |
| --- | --- | ---: | ---: | ---: |
| MELON | sq | 10,158 | **1** | **0%** |
| STRAWBERRY | linear | 10,063 | **1** | **1%** |
| MILK | linear | 10,077 | **1** | **1%** |
| WOOL | sq | 10,060 | **1** | **0%** |
| FERTILIZER | linear | 10,494 | **1** | 1% |
| EGG | log | 10,026 | 44 | 88% |
| CARROT | sqrt | 10,020 | 30 | 86% |
| WHEAT | log | 10,077 | 21 | 84% |
| TOMATO | sqrt | **10,000** | **60** | **100%** |

The four products the entire top of the leaderboard organises its farm
around — MELON, MILK, STRAWBERRY, WOOL — reach the engine's `PRICE_FLOOR` of
**1 coin** in ordinary games. They collapse fast: strawberry needs only 63
units above equilibrium to hit the floor, wool 59, milk 76, melon 158.

That is a statement about the *momentary* price at the bottom of a dump, not
about the average unit — see §0a, which measures what we actually realise and
corrects the overreach. The important part is the steepness: a single sale of
30 strawberries moves the price roughly half the way to zero, and the market
only recovers as the town drains it back.

And **TOMATO never gluts at all.** Its peak inventory across 60 replays is
exactly 10,000 — equilibrium, never exceeded, because essentially nobody grows
it. It is the only product in the game whose price is uncontested, and its
scarce side reaches 660 (§1).

## 0a. What we actually realise, and the real lever: sell rate, not sell timing

Measured on a live game against C95, seed 901 (`sale_race.py`), reconstructing
the engine's per-unit repricing:

| item | our units | our avg | their units | their avg | our slot | their slot |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MELON | 126 | 149 | 114 | 140 | 0.1 | 0.3 |
| MILK | 397 | 65 | 218 | 76 | 0.5 | 0.4 |
| STRAWBERRY | 413 | 88 | 299 | 88 | 0.7 | 0.3 |
| WOOL | 216 | 159 | 188 | 156 | 0.4 | 0.1 |

Two things fall out, and both cut against what I wrote above.

**The slot race is already a tie.** Both agents put premium SELLs in slot ~0.3.
Realised prices are within a few percent of each other on every product. There
is no front-running edge left to win here — the field has already converged on
slot 0, and §3 shows same-slot is an exact tie by construction. Our 30k margin
comes from selling *more units at the same price*, not from better timing.

**So premium production does still pay** — my "worth approximately nothing"
above was wrong. What is true is that we realise **41% of base on milk**
(65 vs 160), 73% on strawberry, 80% on wool. The loss is self-inflicted
depression, and it is enormous in absolute terms.

Now the part that matters. Sale rate versus the town's absorption rate, same
game (town drew 2 bakeries, 2 ice cream shops, 2 yarn stores, 1 brunch spot,
1 farmers market):

| item | turns used | units | max in one turn | our units/turn | town drain/turn |
| --- | ---: | ---: | ---: | ---: | ---: |
| MILK | 61 | 397 | **24** | 0.55 | 0.50 |
| STRAWBERRY | 33 | 413 | **30** | 0.57 | **1.00** |
| WOOL | 23 | 216 | **18** | 0.30 | **1.00** |
| MELON | 15 | 126 | 15 | 0.17 | 0.00 |

**For strawberry and wool, the town's demand exceeds our entire production
rate.** The town would absorb every unit we grow at close to base price. We
instead deliver them in 33 and 23 bursts of up to 30 and 18 units, cratering our
own price each time, and we use 33 turns out of 720.

Rough size of the prize on this one game, if sales were spread to match the
drain instead of dumped:

```
STRAWBERRY   413 x (120 - 88)  ~ 13,200
WOOL         216 x (200 - 159) ~  8,900
MILK         397 x (160 - 65)  ~ 37,700   (drain 0.50 vs our 0.55 -- only partly reachable)
```

Even capturing a fraction of that dwarfs everything this project has tuned to
date; our best measured additive gains have been around $2,000. And it is a
pure timing change — same production, same total liquidation, more turns used.
That is precisely the class of change our own six-failures-out-of-six rule says
*works*: it adds no assets and buys nothing, it only spends turns already idle.

MELON is the exception and stays a dump: no shop in that town buys melon, so
only the town centre takes 1/day and there is nothing to spread into.

### Calibration from 126 live games of the current submission

Average end-of-season market inventory relative to equilibrium, across the
126 replays of 55677927 (negative = demand nobody ever met):

```
CARROT      -307      WOOL         -27      MELON       +149
EGG         -230      STRAWBERRY    +6      FERTILIZER  +437
TOMATO      -225      MILK         +38
WHEAT       -142
```

This is the single best check on the thesis, and it passes. **Strawberry, milk
and wool finish the season within ~40 units of equilibrium** — over 30 days the
town absorbs essentially everything we grow of them. So none of the value we
lose is to overproduction; all of it is in the *path*. We deliver a season's
worth of supply that the town genuinely wants, but we deliver it in spikes and
sell into the craters we just dug. Smoothing the delivery should recover most of
the gap rather than a token part of it.

It also bounds a claim I made too enthusiastically in §1. TOMATO ends **225**
below equilibrium, not the 600+ of the worst observed case. At T=200 that is a
price near **90 against a base of 60** — real, persistent, uncontested, but
about 1.5× base as a planning number, not 11×. Growing tomato and selling into
that gap would push inventory back toward equilibrium as we went, so the honest
estimate is a few hundred units at an average somewhat above base: worth having,
not transformative. The 11× figure is the tail, not the expectation.

Two smaller things fall out. **FERTILIZER ends +437 oversupplied**, which at its
linear curve means the last of it sells for about 13 against a base of 100 — we
are giving it away. And CARROT/EGG/TOMATO all ending deeply short is the same
hinge story from §1, now confirmed as the steady state of a real season rather
than a worst case.

## 1. Three products have a runaway price when scarce

The engine's price curve uses a per-product shape on each side of equilibrium.
Eight of the nine products use `linear`, `sqrt` or `log`, which are tame. Three
— **CARROT, TOMATO and EGG** — use `hinge` on the scarce side:

```python
u = (I0 - inventory) / T
shape = u + 8.0 * max(0, u - 1) ** 2      # HINGE_GAIN = 8.0
```

Flat until inventory falls `T` below equilibrium, then quadratic. Measured on
the 60 live replays from 2026-08-20 (`scarcity_scan.py`):

| item | shape | median low | worst low | price @ worst | × base |
| --- | --- | ---: | ---: | ---: | ---: |
| CARROT | **hinge** | 9,719 | 9,002 | **528** | **15.1** |
| TOMATO | **hinge** | 9,790 | 9,466 | **660** | **11.0** |
| EGG | **hinge** | 9,790 | 9,466 | 141 | 2.8 |
| WHEAT | sqrt | 9,449 | 9,174 | 54 | 2.2 |
| STRAWBERRY | sqrt | 9,885 | 9,729 | 258 | 2.1 |
| MILK | sqrt | 9,977 | 9,736 | 301 | 1.9 |
| WOOL | log | 9,993 | 9,391 | 255 | 1.3 |
| MELON | log | 9,989 | 9,989 | 272 | 1.1 |
| FERTILIZER | linear | 10,000 | 10,000 | 100 | 1.0 |

Every non-hinge product tops out around **2× base**. CARROT reaches **15×** and
TOMATO **11×** in real games. This is the only place in the economy where a
price runs away, and it happens on the two crops the field has essentially
abandoned.

The town drains inventory on a fixed clock whether or not anyone supplies it —
`townShopSellInterval` 4 with single-product shops pulling double, plus the town
centre once a day. So the scarcity is *manufactured by the town*, arrives on
schedule, and is not contested.

**Both public agents that embed a copy of the price table get this wrong.**
Kaito's `_MARKET_PARAMS` transcribes CARROT/TOMATO/EGG `below_func` as
`log`/`linear`/`linear`; his `_shape` does not implement `hinge` at all and
would raise on it. Their price-impact estimates are therefore wrong on exactly
the side of the curve where the money is. That is not a small transcription
slip — it is the one part of the table worth copying carefully.

This also retroactively explains our own `CARROT_PRICE_GATE`, which measured
+3 wins with none given back and which we shipped without knowing why it worked.

## 2. The whole field is one route, and the fight is over sale timing

Kaito's census of public 2026-08-09 traces: the v23 day-0 signature appears in
**3/5** of the top 5, **6/10** of the top 10, **22/30** of the top 30. Rayk's
independent 9 August pull of 200 episodes found a **single field hash in 144
episodes across 40 teams**, with ranks 3–20 "99–100% identical on field
actions."

The modal opening is 5 hires, 2 cows, 2 sheep, 7 wheat seeds, 12 melon seeds,
5 purchased wheat. Mature farms land near 8 cows / 6 sheep, 3 quadrants, 12
hands.

Rayk's own diary makes the consequence explicit — his promotions changed
almost no field structure and enormous amounts of market timing:

> c18 changes only 20 pre-terminal field turns from c16 but **112 market turns**.

This is the strongest external confirmation of the rule we derived empirically
and painfully over six structural failures: **changes to what the route buys or
owns fail; changes to when output is sold work.**

## 3. Front-running is real, it is worth measurable wins, and we don't have it

Both surviving notebook families implement it, by different means:

**Kaito — reorder existing SELL slots by price impact.** Never creates,
deletes or resizes a SELL; only permutes them within their existing slots,
ranked by `qty × (quote_now − quote_after_this_sale)`. Screened at 46/50 for
the route alone versus **48/50** with the ordering.

**Deniz/boatlee — shift a premium sale one turn earlier.** For MELON, MILK,
STRAWBERRY and WOOL: if step+1 has a scheduled SELL, the town has no demand
this turn, and the shed holds free stock, sell it now and subtract exactly that
quantity from the step+1 order. Total liquidation is unchanged; only timing
moves.

### What the engine actually does, which neither notebook spells out

`_process_market` walks the two players' market queues **slot by slot in
lockstep**. For slot `i` it quotes player 0's slot-`i` order and player 1's
slot-`i` order against the *same* pre-commit inventory, commits both a unit at a
time, and only then moves to slot `i+1`. Verified directly on an isolated
market (12 melons each, both players):

```
p0 slot 0, p1 slot 0   ->   2,980  vs  2,980      tie, exactly
p0 slot 0, p1 slot 1   ->   2,996  vs  2,962      +34 to the earlier slot
p0 slot 0, p1 slot 3   ->   2,996  vs  2,962      +34  (same as slot 1)
p0 slot 0, p1 slot 9   ->   2,996  vs  2,962      +34  (same again)
solo sale, no opponent ->   2,996
```

Three consequences, none of them obvious from the notebooks:

1. **Same slot is a perfect tie.** Both players get the identical pre-commit
   quote on every unit. Nobody front-runs anybody.
2. **One slot earlier takes the whole prize.** The earlier seller gets exactly
   the *solo* price — as if the opponent were not there — and the later seller
   eats the entire depression. Being 1 slot ahead is worth the same as being 9
   ahead; the gap size does not matter, only who is first.
3. **Splitting an order across slots is strictly worse** than one slot
   (2,973 vs 2,985 for 12 units as 6+6), because the second half sells into the
   hole the first half dug.

So "front-running" here is not a subtle impact calculation — it is *slot index*.
This also explains a null result: `impact_scan.py` finds our current agent
leaves **0 coins** on the table across 35 multi-SELL turns, because every one of
our SELL lines is a distinct product and permuting non-interacting lines cannot
change anything. Kaito's impact ranking cannot be earning its 46/50→48/50 from
own-book impact either. What it does is push the contested product into a lower
slot index, and that is the whole effect.

Rayk arrived at the same place from the loss side. Of C92's 103 captured live
games, **11 losses shared the same field hash as the winner** — identical
production, reversed by roughly 5,300–5,700 coins purely because the opponent
sold one turn earlier. His fix was the same conservation rule, and the variant
that won was the *narrower* one: fertilizer-only capped at 10 beat
wheat+fertilizer **6-0 with a mean margin of 27 coins**.

That last number is the whole competition in miniature. Our own loss
distribution says the same thing — median margin $2,756, 39% under $2,000.

## 4. Engine details worth having in writing

Verified against our local `kaggriculture.py`, not taken on trust:

- **Melon watering window.** `max_yield_day` 12 → window is ages
  `(12+1)//2 = 6` through 12. A melon starts at 1 unit, gains +1 per watered
  in-window day (+2 fertilized), capped at 6. Full watering therefore maxes out
  around age 10, not 12. Rayk lists "CARE ranked above melon WATER" as his
  single highest-frequency bug: it yields ~70 units instead of ~96 on 16 tiles,
  silently. **Checked, and we do not have it** — `melon_audit.py` on seeds 901
  and 903, both seats: 17 of 17 melon tiles reach the full 6 units, 102/102,
  100% of cap. Our route plants 19 and lands 17, so the ~2 that go missing are
  worth a look, but the watering itself is clean. This kills the hypothesis
  that bad watering explains the −99 melon-patch result.
- **`SELL` only sees the shed.** `HARVEST` puts goods in the *unit inventory*;
  `SELL` spends from the *shed*. No `DROP` means the market cannot see the
  goods until end-of-day auto-drop, usually too late to fund same-turn buys.
- **Fertilizer is sellable.** The competition text emphasises buying it; the
  generic `SELL` path accepts it. Every animal produces it daily.
- **Land.** NE $1k, SW $2k, SE $4k. Rayk tested the fourth quadrant across
  three implementation families and 450 games: **every variant lost 10-0 to
  C92**, and three fully productive Seb four-quadrant routes also lost 10-0, by
  mean margins of 14,608 / 29,016 / 36,980. Do not buy SE.
- **Hiring.** Cost is `fib(n)` for the n-th hire *that day*; ~10 hands costs
  about $143 for a full day of parallelism. Under-hiring early is more
  expensive than over-hiring inside the cheap region.
- **Step 718 executes; action index 719 does not.** Terminal cleanup has two
  usable turns, not one.
- **`townCenterSellInterval` has two regimes.** 12 is legacy (town-centre
  demand multiplies ×2 after day 10 and ×4 after day 20); 24 is the current
  rebalance (flat all season). **Our local env is already on 24** — checked, no
  mismatch. Kaito shipped a version that detects and branches on this, having
  been burned by tuning under the wrong default.
- **Shed capacity 100**, non-seed items, overflow destroyed.
- **`BUY_PRODUCT` is WHEAT and FERTILIZER only.**

## 5. Two process corrections aimed straight at us

**Rayk audited C70 and found it went 83-5 with a +14,196 mean margin — and its
rating had plateaued.** His conclusion:

> Kaggle rating rewards wins, not surplus coins. C70 already crushed weaker
> agents, while its rigid route and largely fixed sell timing failed to convert
> the few close games that mattered.

We have exactly this shape: production matching rank 1 (137,654 vs 138,170) and
a rating that will not move. The margin is not the problem and never was.

**A horizon sweep won its restricted finalist gate and then lost 0-6 to its own
parent on fresh seeds.** Aggregate wins against weak historical agents hid a
regression against the agent that mattered. Rayk's protocol answers this
directly, and we should adopt the veto rule:

> Play the incumbent and the unmodified parent on disjoint seeds, both seats.
> **Treat a loss to either as a veto, even if aggregate wins look strong.**

Also from his checklist, and pointed at a mistake we have already made once:
select replays belonging to the *leaderboard-scoring* submission, not merely
the team's newest active one. Teams run two submissions and the newer one is
often the weaker experiment.

And one we should heed on the submission slots: *"two near-identical active
submits — meta shift kills both — diversify the second slot."* Both our active
submissions are carrot-swap agents differing by one gate.

---

## What this branch will do

The theme is that we have been tuning a route while the actual contest is over
market timing and a price curve we had not read closely.

**1. Adopt the four decoded agents as the live sparring pool.**
`spar_live.py` plays them for real, both seats. This is the test `spar.py`
structurally cannot do: its opponents are recorded tapes whose market layer
cannot react, which removes exactly the part we would lose to. Any claim about
front-running has to be made here, not on the replay benchmark.

**2. ~~Spread premium sales to match the town's drain rate.~~ TESTED, AND WRONG.**
Both instruments lost over 360 replayed games, monotonically:

```
price floor  0.85 / 0.70 / 0.50   net  -26 / -32 / -47 wins
rate cap     1.0  / 2.0  / 4.0    net  -51 / -64 / -75 wins
```

Mechanism, measured directly: turning the meter on **raises** mean market
inventory (MILK 10015.5→10016.1, STRAWBERRY 9978.8→9980.3, WOOL 9995.2→9996.9)
and drops our bank 84,230→79,879 with the opponent's unchanged.

The reason generalises, and it is the most useful thing on this branch:
**these markets clear.** Milk, strawberry and wool finish within ~40 units of
equilibrium. When total supply and total absorption are both fixed, selling
earlier can only raise the average inventory the market carries — and average
inventory is what sets average price. There is no timing free lunch on a
product that clears. The gap between 88 realised and 120 base is not a
scheduling error; it is the intrinsic cost of pushing 413 units through a
market whose equilibrium price only holds for small quantities.

**The corollary is where the money is.** Selling early *is* free on a product
with persistent unmet demand, because its price never collapses. Those are
exactly the ones that end below equilibrium — CARROT −307, EGG −230,
TOMATO −225 — and exactly the ones `EAGER_SELL_ITEMS` already targets (+51
wins) and `CARROT_SWAP` already exploits (+12). Every result this project has
ever gotten now fits one rule:

> Timing is not the lever on products that clear.
> Production is the lever, on the products that don't.

Superseded plan, kept for the record:
The headline work item, from §0a. STRAWBERRY and WOOL sales currently arrive in
23–33 bursts of up to 30 units when the town would absorb our entire output at
near base price if it were spread. Split each scheduled premium SELL into a rate
capped at roughly the measured drain, and carry the remainder forward into the
idle turns that follow — of which there are hundreds.

Conservation rule, same as the notebooks use: total liquidation unchanged, only
the schedule moves. Constraints to respect — the shed caps at 100 non-seed items
and overflow is *destroyed*, so the carry must never let inventory build; and
`maxMarketOrdersPerTurn` is 10, which is not close to binding. Exempt MELON,
which has no shop demand and has to be dumped.

Compute the cap from the observed town, not a constant: `unlocked_shops` is in
the observation, single-product shops pull double, and the drain is
`turnsPerDay / townShopSellInterval` per instance. That makes this genuinely
town-adaptive in the way the carrot gate already is.

**3. ~~Win the slot race.~~ Measured, and it is already tied.**
Both we and C95 place premium SELLs in slot ~0.3 with realised prices within a
few percent. `impact_scan.py` separately finds 0 coins available from permuting
our own lines. Kaito's 46/50→48/50 is presumably won against opponents that are
*not* already at slot 0; against the current field there is nothing here. Do not
build it. Recheck if the field's slot discipline ever slips.

The one-turn shift (Deniz, Rayk C95) is the same story: it buys a turn's head
start in a race that is currently a dead heat. It becomes interesting only as a
tiebreak once item 2 changes when we are in the book at all.

**4. ~~Test TOMATO as the uncontested-price play.~~ TESTED. −146 WINS.**

```
control                  209W-151L   58.1%   +804/game
10 strawberry -> tomato   63W-297L   17.5%   -3,017/game   net -146 wins
```

135 of 195 wins given back. On a town-pinned seed the margin swings +2,642 to
−6,598. Wheat donors were worse still: bank 84,230 → 67,075.

**Correction: I first blamed watering, and that was wrong.** The tiles were
watered fine. The real mechanism is the **ongoing production cap** in
`_daily_refresh_plants`:

```python
production_count = days_since_first // interval + 1
if production_count > cd["max_yield"]: continue
...
if production_count == cd["max_yield"]:
    tile["max_lifespan_step"] = (next_day + 1) * turns_per_day
```

An `ongoing` crop yields `max_yield` units **in total and then dies**. It is not
a perennial — the flag reads like one and isn't. Tomato is 4 units at
`interval` 1, so it produces four days running and is gone. Strawberry is also
4 units but at `interval` 2, spreading them over eight days.

So a tomato tile is worth about **half a strawberry tile**: four units at base
60 against four at base 120. The scarcity premium doesn't close it — tomato
realises ~90 and strawberry ~88, so 360 against 352, parity at best — and the
tile dies early, so the route's later actions on it misfire. Both donor sets
died exactly on this schedule: wheat donors planted day 4 died day 16,
strawberry donors planted day 7 lasted 11 days.

**The rule that survives:** before believing any `ongoing` crop will pay rent
all season, check `max_yield` against `interval`. And substituting a crop works
only where the donor's *existing actions fit the new crop's calendar* — which is
exactly why `CARROT_SWAP` works and nothing else has: carrot waters at ages 2–3
and the route's end-of-season wheat is lifted at age 3.

Superseded rationale:
This is now the most interesting idea on the list rather than a leftover. Tomato
is the only product in the game that **never gluts** — peak inventory across 60
replays is exactly equilibrium — while its `hinge` scarce side reaches 660, 11×
base. It is `ongoing` with `first_yield_day` 8 and `interval` 1, so tiles
planted early pay every day for the back half of the season, into a price nobody
is competing for. Contrast with milk and wool, which we fight over and sell at 1.
The blocker is that it has no home in the current route, which is exactly why it
belongs on a branch allowed to move tiles rather than bolt on another layer.

**Ordering note.** 2 is the branch and should be built first — it is the largest
measured opportunity in the project and it is a pure timing change, the class
that has always worked for us. 4 has real upside but real cost: it means giving
up tiles that currently grow something, and our record on changing what the
route owns is zero for six. It gets tested last, with the town pinned.

### A caveat on the 58-2

`spar_live.py` over 10 seeds and both seats: **18-2 vs C95** (mean +2,111,
worst −196), **20-0 vs C92** (+24,104), **20-0 vs Kaito v25** (+34,868).

This does not mean we are stronger than the top of the board, and it should not
be quoted as if it did. Our live rating is ~1783 against their ~3000, and the
ladder is ground truth. Things that are true and reconcile it:

- C92 and C94 are both explicitly marked *not submitted* in Rayk's own notebook.
  C95 is the one he selected — and C95 is exactly the one that is close.
- Their banks here (78–93k) match the levels their own notebooks document, so
  they are not malfunctioning. I checked the obvious harness bug: Kaito's agent
  does receive the real `configuration` and correctly selects the rebalance
  regime.
- Every one of these agents is a frozen 720-step tape plus a thin adaptive
  layer. Seeds 901–910 are seeds none of those tapes were fitted on. Rayk's own
  notebook warns that a frozen top-agent trace scored 0/50 on transfer, and our
  own lifted route scored 6/16.

Treat it as evidence that our *production and liquidation volume* is competitive
and that C95 is the only one of the three worth using as a veto opponent.

**5. ~~Audit the melon water window.~~ Done — we are clean at 100% of cap.**
Kept in §4 as a verified negative. The open remnant is small: the route plants
19 melons and 17 survive to harvest.

### Rules this branch inherits

- Both seats, always. Shared-market games are not symmetric.
- The incumbent and the unmodified parent are **veto** opponents.
- Freeze parameters, then run one untouched seed block.
- The town must be pinned when comparing variants — agent actions perturb the
  RNG stream that draws the shops, and we have already burned ourselves once
  reading an $8,399 gain that was $415 with the town held fixed.
- Report per-opponent records, not aggregates.
- Optimise win conversion in close games. A bigger margin in a game we already
  win is worth nothing.

### Attribution

The route backbones in all four notebooks are reconstructed from other
competitors' public replays, and each notebook says so. Nothing lifted is
submitted from this branch; these agents are here as opponents and as
documentation of mechanics. Our own `kernels/route_v15.py` — an opponent's plan
lifted from a replay, measured worse, never submitted — should be deleted for
the same reason.
