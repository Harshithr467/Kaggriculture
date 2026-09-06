# What a challenger must do to beat `agent_combined.py`

The incumbent is the route agent currently at **1698.9** (submission 55677927).
This is the specification any replacement has to meet, written as measured
thresholds rather than advice. Every number here came from a run in this repo
and names the tool that produced it.

Reference measurement: seed 9300, town pinned via `fixed_town`, opponent
`kernels/rayk_c95.py`, seat 0.

---

## Tier 0 — hard gates. Fail any one and nothing else matters.

| Requirement | Incumbent | How to check |
| --- | --- | --- |
| Entry point `main.py` exposing `agent(obs)` | yes | Kaggle loads the last callable |
| Standard library only | `base64, copy, json, math, zlib` | `grep '^import'` |
| Self-play validation ends `DONE/DONE`, 720 frames | passes | Kaggle runs this on upload; reproduce locally |
| Zero exceptions in the action pipeline | 0 across 4 games | run the body without the blanket `except` |
| Per-step time under the 1 s `actTimeout` | **126 ms max**, 0.24 ms median | time the agent inside a full game |
| Nothing unsold at the bell | shed `{}`, carried `{}` | unsold inventory scores **zero** |
| Herd never starves | — | an animal dies permanently after 2 unfed days |

The last two are where agents silently bleed. An animal lost on day 2 costs the
whole season's milk, and produce still in a hand's sack at step 719 is worth
nothing.

---

## Tier 1 — economic parity. This is the actual bar.

The incumbent generates **208,976 in sales revenue** on the reference game. The
uploaded policy candidate generated 140,855 — 33% less — and lost 2-38 across
the ladder. Per-product, this is where a challenger has to get to:

| Product | Incumbent units | Incumbent revenue | Candidate | Shortfall |
| --- | ---: | ---: | ---: | ---: |
| **MILK** | **397** | **91,510** | 276 u / 58,814 | **−32,696** |
| **WHEAT** | **486** | **20,664** | 69 u / 2,864 | **−17,800** |
| STRAWBERRY | 413 | 53,665 | 275 u / 47,307 | −6,358 |
| FERTILIZER | 300 | 15,803 | 178 u / 10,412 | −5,391 |
| WOOL | 218 | 7,074 | 34 u / 2,069 | −5,005 |
| MELON | 126 | 20,260 | 80 u / 17,201 | −3,059 |
| TOMATO | 0 | 0 | 21 u / 1,838 | +1,838 |
| CARROT | 0 | 0 | 10 u / 350 | +350 |
| **TOTAL** | | **208,976** | **140,855** | **−68,121** |

Milk alone is half the gap. Note the trap: the candidate ran **14 cows to the
incumbent's 8** and still sold 30% less milk. Herd size is not the constraint —
collection and sale throughput is.

### Labour utilisation

| | Incumbent | Candidate |
| --- | ---: | ---: |
| Live field actions | **6,349** | 5,494 |
| Wasted `PASS` turns | **323** (4.8%) | 1,027 (18.7%) |
| Hands on the roster | 10 | 12 |

A challenger must keep utilisation above ~95%. The candidate had *more* hands
and used them less. Hire cost is `fib(n)` per hire per day — about $143 for ten
hands for a whole day — so under-hiring is never the expensive mistake;
under-*using* is.

### The farm that produces those numbers

```
incumbent   8 COW, 4 SHEEP, 137 wheat tiles, 17 melon, 36 strawberry, 13 carrot
candidate  14 COW, 1 SHEEP, 19 strawberry, 1 wheat
```

The incumbent's wheat program is not optional. Wheat is 486 units of revenue
**and** the feed chain **and** the least glut-prone crop (5 shops demand it,
~30/day). The candidate abandoning wheat cost it 17,800 directly and starved its
own logistics.

---

## Tier 2 — what it takes to beat the field, not just us

Beating the incumbent gets you to ~1700. The top of the board is ~2,900–3,130.
From 105 live losses, the agents that beat us bank **130,000–141,000** where we
bank 112,000–127,000 — a real ~15% output gap at the top.

```
us 120,556   them 138,419    Alexander Gremyakov
us 126,471   them 140,212    dzjiann
us 127,568   them 141,157    Alperen Aydın
```

Our own mean across 486 live games is 90,696. So: ~90k is us, ~110k is a good
game, **~140k is the top**.

---

## Tier 3 — proof required before submission

A candidate is not promoted on a score. It is promoted on this:

1. **`ladder.py`, both seats, two disjoint held-out seed blocks.** Twenty seeds
   each, minimum. Seeds used to screen a candidate cannot be used to decide it.
2. **`agent_combined.py` as the veto opponent.** A candidate that wins a pool
   overall but loses to the agent it replaces has not earned the slot.
3. **At least two unrelated external families in the pool** — `rayk_c95.py`,
   `15-16-strict-future-v25-meta-reset__main.py`, one lifted route.
4. **Report per-opponent records, not the aggregate.** Win rate is
   pool-relative: Rayk C95 measured 10% in one pool and 76.9% in another, both
   correctly.

**Do not promote on `bench_losses.py`.** It replays frozen tapes and detects
breakage reliably, but it scored MiMi's route +24 wins over the agent that then
beat it 32-8. Wrong sign, not noise.

---

## Design constraints — the rules that cost us ten failed experiments

These are not style preferences. Each one is a measured negative.

| Rule | What it cost to learn |
| --- | --- |
| **Markets that clear cannot be gamed on timing.** Milk, strawberry and wool finish within ~40 units of equilibrium; selling earlier only raises average inventory, and average inventory sets average price. | Sale meter, −51 to −75 wins at every rate |
| **Selling early is free only where demand is never met** — carrot ends −307, egg −230, tomato −225. | The eager seller (+51, then 43-5) is built on exactly this |
| **A crop substitution works only where the donor's existing actions fit the new crop's calendar.** | Carrot fits wheat's age-3 lift and pays 40-8. Tomato, melon, geese needed actions the route lacks: 0 for 8 |
| **An `ongoing` crop yields `max_yield` units in total and then dies.** It is not a perennial. | Tomato swap, −146 to −190 wins |
| **You cannot remove a watering.** Two dry days turn a plant to WEED. | Fertilize-wheat swap, −3,335 margin |
| **An item the farm consumes is not surplus.** | Eager-selling fertilizer −151, plus wheat −208 |
| **Adding actions to a route with no idle capacity fails.** | Every production change: melon patch −99, geese −105, cow swap −$42k |
| **Rank does not predict transplantability.** | The rank-1 route was the second worst of four lifted |

---

## Where the remaining headroom actually is

Measured, unexploited, in rough order of size:

1. **Wheat is fertilizable for +2 units a tile.** Ours peaks at 3.80 of a cap
   of 6 and is never fertilized; the official table confirms "6 (4
   unfertilized)". 137 tiles × 2 units × ~44 = **~12,000 a game** — but it needs
   an *added* FERTILIZE from a worker who is idle, on the tile, and carrying a
   unit. Substituting a watering kills the plant.
2. **666 of our 967 CARE actions do nothing** — 442 on tiles with no animal.
   That is 10.5% of all field actions. Only ~38 are convertible in place;
   recovering the rest means moving workers.
3. **Fertilizer ends +437 oversupplied**, selling at ~13 against a base of 100,
   with no consumer in the game at all.
4. **The town varies enormously and we ignore it.** Wool demand is zero in 32%
   of games and up to 60/day in others; melon has *no* shop demand ever. The
   route produces the same mix regardless.

All four require authoring actions rather than substituting them, which is the
category that has failed eight times. That is the honest state of it: the
headroom is real, measured, and behind the one wall we have not found a way
through.

---

## Quick-start commands

```bash
python ladder.py --seeds 9300-9319 --workers 10 --pool \
  "path/to/candidate.py#candidate" \
  "agent_combined.py#INCUMBENT" \
  "kernels/rayk_c95.py#Rayk C95" \
  "kernels/15-16-strict-future-v25-meta-reset__main.py#Kaito v25"
```

```bash
python diversity.py --candidates "agent_combined.py#incumbent" "path/to/candidate.py#new" \
  --opponents kernels/rayk_c95.py kernels/agent_recursion.py --seeds 9400-9409
```

```bash
python wasted_actions.py --seed 9300
python sale_race.py --opponent kernels/rayk_c95.py --seed 9300
```
