---
description: The standing Kaggriculture objective, what is known, and the promotion rules. Read this before proposing any agent change.
---

# Goal

Reach a top-10 finish in Kaggriculture — roughly **2,900–3,000 rating points** — by the
final submission deadline, **2026-09-30**.

## Read this part before you promise a win rate

The user's stated target is "90–100% win rate *and* 2,900–3,000 points". Those two
cannot both hold, and it matters for how work gets prioritised.

Matchmaking pairs by rating. At equilibrium your opponents are your own strength, so
win rate converges to ~50% for everyone. **At 3,000 points you will win about half
your games.** A 90% win rate only happens while climbing through a field beneath you.

So treat **rating as the goal and win rate as a diagnostic**, and never report a high
overall win rate as progress. The diagnostic that actually tracks the goal is the win
rate split by opponent rank. Measured on V3's 140 live games:

```
opp rank      W-L      win%
1-50          0-1       0.0%
51-200        1-2      33.3%
201-500       3-7      30.0%
501-1000      2-6      25.0%
1001+        82-36     69.5%
```

The 62.9% headline was almost entirely the long tail. **Beating weak opponents is
solved. Progress means moving the top buckets.**

## Where we are

| version | submitted | rating | note |
|---|---|---|---|
| V2 | 2026-09-08 | 1566.4 | lifted public route + overlay |
| V3 | 2026-09-09 | 1668.0 | route rebuilt from Fih/yuki replays |
| V4 | 2026-09-11 | 1719.8 | opening selector, turn-240 rule, geese→cows |
| V5 | pending | — | receding-horizon livestock planner + opponent model |

Increments are +102, +52. **They are shrinking, not holding at 100.** Extrapolated,
this path arrives near 1,900 by the deadline — about 1,100 short.

## Why incremental tuning cannot close the gap

Final banks of top-ranked teams, measured from their own replays:

```
pooled top-25 opponents   mean 98,407
our V3                    mean 97,695
```

**We are at production parity with the leaderboard's best, within 1%.** Our best game
is 159,210; theirs is 158,451. The town's demand is roughly fixed and the market
resolves in lockstep between both players, so total extractable value is capped and
everyone competent is against the same ceiling.

The gap is therefore *not* "grow more". It is visible here:

```
V3 in wins    99,961 vs  80,111   margin +19,850
V3 in losses  93,860 vs 101,825   margin  -7,965
```

Wins are blowouts, losses are narrow. Ranking is win-based, so **every coin of that
+19,850 surplus is wasted** — a 1-coin win scores the same. The lever is converting
narrow losses into narrow wins, which is a consistency and adaptation problem.

## Thousand-point jumps are real, and here is what they look like

Observed on 2026-09-12: `M & M & P & Q` moved **+1,155 places and +953.9 points in one
day**; `Civitasmass` +660 places and +472.2. Those are step changes from submitting a
materially different agent — not tuning. So the user's ambition is achievable in
principle, but only by changing what the agent *is*, not by another overlay on the
same route.

## Promotion rules — do not skip these

1. **Held-out seeds only.** Never promote on the seeds a candidate was selected with.
   A lifted MiMi route went 6/6 on its selection seeds and then **8-32** on twenty
   fresh ones.
2. **Both seats, always.** The market resolves player 0 first on each unit, so a
   one-seat test can reverse the winner.
3. **The incumbent is a veto opponent.** A candidate that wins a pool but loses to the
   agent it would replace has not earned the slot. Use
   `python ladder.py --pool "cand.py#C" "incumbent.py#I" --seeds <fresh> `.
4. **Never promote on `bench_losses.py`.** It replays fixed tapes that cannot react;
   it detects breakage reliably and ranks comparable agents *wrongly* — it had the
   sign wrong on MiMi by 24 wins. Trust a large negative. Ignore a positive.
5. **Local pool win rate is the number that has misled us most.** Weight results
   against *ranked live opponents* far above any local pool percentage.

## Submission mechanics

Only the **latest 2** submissions are rated; each new one retires the older. The final
standing counts your **best** bot, so a weaker new submission cannot drag you down —
it displaces the older slot, and the floor stays at your best live agent.

## What to do when this command is invoked

1. Run `python daily_report.py` (or read today's `reports/daily-*.md` if it already ran).
2. State the current rating, the rank-bucket split, and days remaining.
3. Propose the single highest-leverage change aimed at the **top buckets**, not the
   overall win rate — and say what would falsify it.
4. If a candidate exists, run the ladder against the live incumbent on fresh seeds,
   both seats, and report the veto result before recommending submission.

See also: [/schedule](schedule.md) for the daily routine.
