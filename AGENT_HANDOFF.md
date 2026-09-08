# Handoff briefing

Paste this into a new assistant's instructions to bring it up to speed.

---

You are improving a competition agent for the Kaggle **Kaggriculture** simulation
(two-player farming sim, 30 in-game days, scored on final bank balance).

Working directory: `C:\Users\viloh\OneDrive\Documents\ChatGPT\New project`
Branch: `codex/rank-1-strategy`. Python: `.\.venv\Scripts\python.exe`.
Kaggle CLI: `.\.venv\Scripts\kaggle.exe`.

**Read `COMPETITION_SPEC.md` first, then `BRANCH_FILE_GUIDE.md`.** The official
competition documentation is wrong in five places — most importantly it claims
unsold inventory counts toward your score. It does not. Reward is bank balance
only, so everything must be sold before the season ends. Trust the spec, which
was read from the environment source and verified against live replays.

`main.py` is the entire submission; everything else is local tooling.

## The measurement rules — do not skip these

Per-game variance is about **±4,000**, which is larger than most real effects.
This has produced **four false positives** so far, including one that looked like
10/12 wins and +8,445 before settling at 50% over 28 games.

- Validate with `benchmark_ab.py <seeds...>` — it plays the working tree against
  a git revision, **both seats per seed**. Both seats are mandatory: on seed 0 an
  agent playing *itself* wins by 9,869 in one seat and loses by 9,869 in the
  other, so a single-seat run can manufacture a 10k effect from nothing.
- Sweep one constant at a time with `benchmark_sweep.py NAME v1 v2 v3 --seeds ...`.
- **Require two independent seed sets, 20+ games total, with agreeing magnitudes**
  before believing anything under about +10,000. Use seeds you did not tune on.
- Scores against the `random` opponent are **not a signal**. Neither is any
  single game.
- Change **one thing at a time**, or you cannot attribute the result.
- Watch for no-op seeds: if both seats show mirrored margins (+X / −X), the change
  did nothing in that game and the aggregate win rate will understate a real
  effect. Separate triggering games from unaffected ones before concluding.

## What already worked (all committed and measured)

| Change | Result |
|---|---|
| Melon-first opening, inventory-based sell policy, demand-driven herd | 17/24, +14.6% |
| `TRAVEL_DIVISOR` 0.85 → 12.0 | 24/24, ~+17,000/game |
| `ANIMAL_TOTAL_CAP` 17 → 15 | 29/40, +3,040/game |
| Never buy the 4th quadrant | 16/16 on triggering games, +9,679 |

**Every one of these was a mis-set number in our own code, found by instrumenting
our agent.** None came from copying an opponent.

## What is already falsified — do not retry without a new mechanism

- Geese / lowering `MARGINAL_ACTION_VALUE` — 0/12 twice, at two different travel divisors
- Raising `ANIMAL_TOTAL_CAP` — monotonically worse
- Capping late wheat below 60 — monotonically worse
- Sizing the crew to estimated workload — 0/24 (hands are near-free vs action value)
- Per-worker territories / contiguous role blocks / stickiness tuning — all negative
- Re-weighting animal jobs to raise tending — 1/12
- Copying the rank-1 build wholesale (no carrot/tomato, strawberry 36, three quadrants) — 29/48, a wash
- **Warehousing produce for a better price — 0/12 and 1/12, about −17,000 and −21,000.**
  The shed holds 100 items and end-of-day overflow is silently discarded, so held
  stock destroys the next harvest. Our sell timing already matches the top agents'.

Five separate attempts to reduce movement all failed. Movement share does not
predict score: the top-scoring agent observed (121,056) spends **54.8%** of its
actions moving, while we spend 48.4% and score 77,000.

## The current best lead: the wheat gap

Measured against the rank-1 agent, per game:

```
              us    rank 1
WHEAT        109       427     <- 3.9x
STRAWBERRY   209       275     <- 1.3x
MILK         170       227     <- 1.3x
WOOL         124       157     <- 1.3x
```

Every product is a ~1.3× gap except wheat, which is nearly 4× — roughly
**$14,000 a game**, close to half the total deficit. They plant ~146 wheat seeds
to our ~98 and peak at 51 tiles to our 35. We both *buy* about the same amount
for feed, so the whole difference is grown surplus.

Two independent things to test separately:
1. **Tile count** — the plan allows 60 late-game wheat tiles but we only reach 35.
   Find what actually limits it: seed budget, plant-job priority against watering,
   or tiles not freeing up in time.
2. **Fertilizing wheat** — raises a wheat tile from 4 to 6 units (+50%) for one
   action. Neither we nor any top agent does this. Borderline on paper once you
   price the forgone fertilizer sale (~$60), so measure it.

Note: fertilizing **melon** gains nothing — it already reaches its cap of 6 on
plain watering by exactly the day harvest first becomes legal.

## Analysis tooling

- `analyze_live_submission.py <submission_id>` — live results, win rate, closest losses
- `analyze_opponents.py <submission_id>` — compares both seats by outcome
- `profile_team.py <replay_dir> [--team NAME]` — one team's build averaged across games
- `reconstruct_policy.py <replay.json>` — one player's full economic policy
- `compare_top_agents.py <dirs...>` — several top agents side by side
- `verify_market_model.py` — confirms the price curves match the live environment

Replays record **both** players' private state and every market order, so an
opponent's behaviour is almost fully observable. But their build is the *output*
of their scheduler, not an input — copying their tile counts into our agent has
failed every time it was tried.

## Constraints

- **Do not submit to Kaggle without asking.** Limit is 5/day and only the two most
  recent submissions count for the final tournament.
- Commit validated improvements with the measured result stated honestly, negative
  results included.
- When a change measures badly, **check the diff for a bug before discarding the
  hypothesis** — two apparent failures turned out to be bugs in the change itself.
- Prefer instrumenting before changing. Three attempts at the movement problem
  failed because they targeted guessed causes; tracing `assign_jobs` found the
  real one in a single run.

## Current standing

Rank ~1516 of 3,695. Deadline 2026-09-30. Gold is roughly top 17, so the realistic
near-term target is bronze (top 10%) rather than top 10.
