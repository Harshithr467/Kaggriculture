# Autonomous 48-hour optimisation log

Started **2026-08-14**, ends **2026-08-16**. Checkpoints every 4 hours; the
schedule cancels itself at the end.

Rules this log holds itself to, carried over from `BRANCH_FILE_GUIDE.md`:

- One strategic change per checkpoint, or none. "No change justified" is a
  valid, expected result.
- Two independent seed sets, 20+ games, both seats, before believing anything
  under ~+10,000. Magnitudes must agree, not just signs.
- A real optimum has slopes. An isolated spike with losing neighbours is a seed
  set, not a finding.
- Final money and paired wins decide. An intermediate metric improving is not
  evidence — crew-sizing improved every intermediate metric and lost 24 straight.
- Never re-run a falsified idea without a genuinely new mechanism.

---

## Baseline at start

| | |
|---|---|
| Best commit | `cc1f527` |
| Live submission | 55414416 (873.4) |
| Previous submission | 55397388 (**892.0** — currently scoring higher) |
| Live record | 115/230 = **50.0%** |
| Live mean score | 76,702 vs opponents' 74,697 (margin **+2,005**) |
| Local validation | HEAD 13/20 (65%), +2,253/game vs pre-rework `a49c8d3` |

### Why the live win rate is 50%

Not a defect. ELO matchmaking pairs us against opponents of our own rating, so
50% *is* the equilibrium of a stable rating. The rating, not the win rate, is
the thing to move. Margin distribution over 230 live seats:

```
quartiles   -11,392        +30    +14,854
37% of games decided by under 10,000

  +2,000/game would flip  9 of 115 losses -> 53.9%
  +5,000/game            31              -> 63.5%
 +10,000/game            50              -> 71.7%
 +20,000/game            86              -> 87.4%
```

So the 80–90% target needs roughly **+20,000/game** against the present pool,
and the pool strengthens as we climb.

---

## Open methodological question (checkpoint 0)

Every A/B in this project has been **self-play**: our agent against our own
earlier commit. Both sides then hit the market with identical timing — both
dump melon the same day, both flood fertilizer, both leave wheat demand unmet.
Any change touching market volume or timing is judged in a world where the
opponent's supply is perfectly correlated with ours.

Several of the 13 falsified hypotheses were market-facing (melon glut,
fertilizing wheat, backfill crop, sell volume). If self-play distorts them, some
deserve re-testing. Running `BACKFILL_CROP` against structurally different
opponent `c34629c` (travel divisor 0.85, herd cap 17 — genuinely different
behaviour, comparable live strength at 822.9) on the same seeds 240–251 that
produced 11/24 and −1,424 under self-play.

---

## Checkpoint 0 — 2026-08-14, session start

**Current best**
- Commit: `cc1f527`
- Submission ID: 55414416
- Live episodes: 230 seats / 115 games
- Live win rate: 50.0%
- Validated local: 13/20 (65%), +2,253 vs `a49c8d3`

**Biggest remaining gap** — absolute score. We average 76,702; the strongest 101
seats of 508 mined episodes average 133,066. That is a **56,000/game** gap, and
+20,000 of it would be worth an 87% win rate against the current pool.

**Root-cause hypothesis** — no independent measure of strength. `benchmark_ab`
compares us to our own past self and `opponent_strong.py` imports `main`, so
every result to date measures *change*, not *level*. Thirteen consecutive
falsifications are consistent with a well-converged local optimum that we have
no instrument to see beyond.

**Evidence** — 13 sweeps, losses in both directions from current values; live
margin +2,005 against same-rated opponents; the one surviving change
(`ANIMAL_TOTAL_CAP` flat 14) came from a field-wide gradient across 310 seats
rather than from self-play intuition.

**Experiment performed** — two.

*1. Validation of HEAD against the actually-live agent* `f454950`, seeds 300–309:

```
14/20 (70%)   avg current 81,093   avg baseline 76,688   margin +4,405
```

Together with 13/20 and +2,253 against `a49c8d3` on seeds 260–269, that is two
independent seed sets with agreeing magnitudes. **Submitted as 55514059.**

*2. Self-play bias test.* `BACKFILL_CROP` on the same seeds 240–251, once against
HEAD and once against structurally different `c34629c`:

| backfill | vs HEAD | vs `c34629c` |
|---|---|---|
| CARROT | 10/24, +0 | 23/24, **+17,215** |
| WHEAT | 11/24, **−1,424** | 24/24, **+23,068** |

**Result: KEEP the submission; NO code change. Self-play bias is confirmed real.**
The same change is worth −1,424 against ourselves and +5,853 against a different
opponent — a sign flip, not a magnitude wobble.

The absolute scores stop this being a straight win, though. Under WHEAT *our own*
score falls, 77,226 → 71,618; the opponent's falls further, 60,011 → 48,550. So
wheat backfill does not make us stronger, it makes an opponent that depends on
the wheat market weaker. Against ELO and Bradley-Terry, which score wins rather
than money, denial still counts — but this is one opponent, and testing against
a single different agent is merely a different bias.

**Next highest-value investigation** — build a multi-opponent benchmark
(pool: HEAD, `a49c8d3`, `f454950`, `c34629c`) and average across it. Until that
exists, no market-facing result in this project is trustworthy in either
direction. Then re-test the market-facing falsifications under it: melon glut
allowance, fertilizing wheat, backfill crop, sell-volume caps.

Second priority, unaffected by the bias: `absorbable_units` projects the whole
season's town demand from today's shop count, and a flat multiplier could not
fix it (2.0 gave 13/16 then 10/20 with both neighbours losing). It needs the
`townShopUnlockInterval = 3` schedule modelled, which is work rather than a sweep.

---

## Checkpoint 0b — multi-opponent benchmark built and first re-test

`benchmark_pool.py` (`c78c4b5`) plays a candidate against four structurally
different builds, in parallel across processes, and reports win rate **and** our
own absolute score per opponent, flagging when the two disagree.

**First absolute strength reading this project has had.** Current agent vs pool,
seeds 240–247:

| opponent | wins | our score | their score | margin |
|---|---|---|---|---|
| HEAD (self-play) | 8/16 | 73,785 | 73,785 | +0 |
| `a49c8d3` | 9/16 | 73,418 | 73,129 | +289 |
| `f454950` | 11/16 | 73,484 | 71,356 | +2,128 |
| `c34629c` | 15/16 | 74,999 | 58,874 | +16,124 |
| **POOLED** | **43/64 (67.2%)** | **73,921** | 69,286 | **+4,635** |

Monotone against our own history, and exactly 50% against ourselves — the
instrument passes its sanity checks. **67.2% pooled is the number to ratchet.**

**Re-test: `BACKFILL_CROP`.**

| | vs HEAD | `a49c8d3` | `f454950` | `c34629c` | POOLED |
|---|---|---|---|---|---|
| WHEAT margin | −2,145 | −1,535 | +3,342 | **+20,428** | 57.8%, **−5,998** |

**Result: REVERT — falsification confirmed, and my earlier +23,068 was itself the
artifact.** The whole apparent gain sits against one opponent. Against three of
four builds wheat backfill is neutral-to-negative, and win rate and absolute
score now agree it is worse. Testing against a single different opponent was not
a fix for self-play bias, it was a second bias pointing the other way.

**Caveat on the pool itself.** `c34629c` scores 58,874 where our live opponents
average 74,697, so it is weaker than the field and we beat it 15/16. It earns its
place on structural difference, but any result that lives only in that column
should be treated as denial against one build rather than as strength. Watch for
a pooled verdict that is carried entirely by one row.

**Live result of 55514059: 918.5**, against 892.0 for the previous best
(55397388) and 873.4 for the submission it replaces (55414416). Highest recorded
on this project. Early scores move on few episodes, so treat it as encouraging
rather than settled — but the direction agrees with the local 14/20, which is
the first time a local verdict and a live score have been checked against each
other here.

**Next investigation** — re-test the two remaining market-facing falsifications
under the pool: `GLUT_ALLOWANCE` for melon, and `NONONGOING_FERT_MARGIN` for
fertilizing wheat. Both were judged under self-play. Then the `absorbable_units`
shop-unlock schedule, which the bias does not touch.

---
