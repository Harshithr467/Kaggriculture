# 3 - Public lineage

One submission, and not our own work.

`the-2945-farm_56369872_final-1324.py` is thomastschinkel's "The 2945 Farm"
(v9/4), taken byte-for-byte from the Apache-2.0 notebook *The 2945 Farm: 96% vs
the Top-10 Public Bots*, published 2026-09-19. The author states it is the exact
file behind their submission 56269928, which scored 2944.7. All upstream
Apache-2.0 notices are retained in the file, crediting yhay81, prvsiyan,
Dmitrii Gluzdov, Ahmed Berat Ozer, tetsutani and the kaggle-environments
contributors.

Submitted 2026-09-19 as 56369872. Using it was legitimate: the rules prohibit
private code sharing between teams, not public Apache-2.0 notebooks.

## What happened

| when | score | note |
|---|---|---|
| 09-19, 9 games | 1319.9 | provisional, 8W-1L, +40k average margin |
| 09-20 | 2463.8 | climbing hard |
| 09-30 final | **1324.4** | settled far below the author's 2944.7 |

It replaced our own lineage, which was then at 1448 and falling, and
immediately went 8-1. The peak reading of 2463.8 was real but did not hold.

## Why it did not reach 2,945

The author was candid that v9/4 went **0-36 against seven of the then top-10
teams**, and named the cause: from day 12 the farms that beat it hold ~10 tomato
tiles and sell 71 tomatoes at $114, while v9/4 sells 7 at $316. They asked
publicly for a fix and did not get one.

We worked that problem and found the economics do not close. Measured against
the engine:

- `FERTILIZE` doubles an ongoing crop's output, 4 -> 8 units, for tomato and
  strawberry only. Both top public agents already exploit this on strawberry
  and plant no tomatoes at all.
- The tape never buys the fourth quadrant: 25 tiles stay LOCKED all game while
  it holds 50-80k in cash. It is labour-bound, not cash-bound, and caps at 11
  hands.
- Hands vanish at midnight, so extra crew is a daily cost. Hands 12-14 cost 754
  coins every day.
- The tomato book is shallow. The town drains ~5/day, so season demand is ~120
  units. Selling 96 tomatoes returns 5,710-8,451 depending on the town.

Against ~8,800 in land and crew, that is break-even at best. Our attempt
(`kernels/candidate_v7.py`, unsubmitted) lost 14,541 coins a game.

## The one real tuning win, also unsubmitted

`kernels/candidate_v8.py` raises `V9_RACE_DEFAULT` from 40 to 48, which pins
the sale-race lookahead at its ceiling instead of letting it fall back whenever
our lead is thin. Against the stock agent on three disjoint held-out blocks,
both seats: 21-15, 57-17, 55-19 -- **133-51 (72.3%)** over 184 decisive games,
and 265-49 against a league of V50, 2749 and 2727. It was never submitted.
