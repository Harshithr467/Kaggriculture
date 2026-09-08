# Branch File Guide — `codex/rank-1-strategy`

The agent for the Kaggle **Kaggriculture** competition, plus the tooling used to
measure it. Only `main.py` is submitted; everything else is local analysis.

## Quick reference

```powershell
# validate a change (the only measurement worth trusting)
.\.venv\Scripts\python.exe benchmark_ab.py 5 6 7 8 9 10 11
.\.venv\Scripts\python.exe benchmark_sweep.py TRAVEL_DIVISOR 4 12 25 --seeds 20 21 22

# look at live results
.\.venv\Scripts\python.exe analyze_live_submission.py <submission_id> --min-episodes 40
.\.venv\Scripts\python.exe analyze_opponents.py <submission_id> --close 15000

# study an opponent
.\.venv\Scripts\python.exe profile_team.py kaggle_episode_data\replays\<dir>
.\.venv\Scripts\python.exe reconstruct_policy.py <replay.json>

# submit
.\.venv\Scripts\kaggle.exe competitions submit kaggriculture -f main.py -m "message"
```

## The agent

### `main.py`
The whole submission: a single file whose last `def` is `agent(obs)`. Flow is
`run_strategy` → tile role plan → job list → worker assignment → market orders.

Constants worth knowing, all near the top and all deliberately module-level so
`benchmark_sweep.py` can vary them:

| Name | What it controls |
|---|---|
| `GLUT_ALLOWANCE` | How far past market equilibrium each product may be pushed before we hold. The entire sell policy. |
| `TRAVEL_DIVISOR` | How steeply distance discounts a job's value. Worth ~+17,000/game; see below. |
| `ANIMAL_TOTAL_CAP` | Herd ceiling by quadrant count, sized to what the crew can tend. |
| `MARGINAL_ACTION_VALUE` | Opportunity cost charged against each animal's daily upkeep. |
| `OUT_OF_ZONE_FACTOR`, `STICKY_FACTOR` | Quadrant preference and commitment to an in-progress walk. |

## Measurement

### `benchmark_ab.py`
Plays the working tree against any git revision across a seed list, **both seats
per seed**. This is the only trustworthy measurement in the project.

Both seats are not optional: on seed 0 the same agent playing itself wins by
9,869 in one seat and loses by 9,869 in the other, so a single-seat run can
invent a 10k effect out of nothing.

Per-game variance is about ±4,000. A 12-game sweep cannot distinguish a real
+3,000 from noise — this produced four false positives during tuning, including
one that looked like 10/12 and +8,445 before settling at 50% over 28 games.
**Require two independent seed sets, 20+ games, with agreeing magnitudes**
before believing anything under about +10,000.

### `benchmark_sweep.py`
Sweeps one module-level constant over several values in a single run. Finding
`TRAVEL_DIVISOR` this way was worth ~+17,000/game after three hand-reasoned
attempts at the same problem all measured negative. If the constant you want is
buried inside a function, lift it to module level first.

### `smoke_test.py`
Builds a synthetic day-zero observation and checks `agent()` returns a
correctly-shaped dict. Interface only, not strategy.

### `local_test.py`
One local game against `random`, `starter`, `self` or `opponent_strong.py`.
Useful for a quick sanity check; **not** a measurement — scores against `random`
are noise.

### `opponent_strong.py`
A hand-written premium-crop opponent, independent of `main.py`'s strategy.
Useful as a third party when checking that a change is not merely overfitting to
the A/B baseline.

## Replay analysis

### `analyze_live_submission.py`
Downloads any replays not yet on disk for a submission, then reports win rate,
score split, closest and worst losses, action census overall and for days 24–29,
endgame idle land versus the opponent's, and average final market inventory.
`--min-episodes N` makes it a safe no-op while a submission is still playing, so
it can run on a schedule.

### `analyze_opponents.py`
Extracts a comparable feature vector for **both** seats of every replay and
aggregates by outcome, so "what beats us" reads directly against "what we do".
This found the animal-tending gap behind the herd-cap change.

### `profile_team.py`
Averages one team's build across many replays. A single replay confuses policy
with seed luck; averaging separates them.

### `reconstruct_policy.py`
Dumps one player's complete economic policy from a single replay. Replays record
**both** seats' private state — shed, seeds, per-worker inventories — plus every
market order issued, so an opponent's strategy is almost fully recoverable.

### `audit_fertilizer.py`
Counts, per team, which crops get `FERTILIZE` actions and the mean units per
`HARVEST`. Commands carry no coordinate — a worker acts on the tile it stands on
— so it pairs each command with that worker's recorded position. This is how we
found that the rank-1 agent fertilizes wheat ~14 times a game and we never did.

### `verify_market_model.py`
Confirms the environment Kaggle runs uses the same price curves as the local
package (it does: 4,059 inventory/price points across 25 live episodes, zero
mismatches), recovers the curve parameters from replay data alone, and prints
the glut thresholds that `GLUT_ALLOWANCE` is derived from.

## Data

`kaggle_episode_data/` holds small CSV episode listings (tracked) and downloaded
replay JSON (**not** tracked — several GB, re-downloadable via
`analyze_live_submission.py`).

## Verified game facts

Taken from the environment source, not the competition docs, which are wrong on
several of these:

- **Final reward is bank balance only.** Unsold shed stock scores zero, so full
  liquidation before the end is mandatory.
- **EGG and WHEAT never meaningfully crash** (logarithmic glut curves; 1600
  units past equilibrium still price at $37 / $19). MILK, WOOL and STRAWBERRY
  hit the $1 floor within ~60 units; MELON within ~158.
- Market inventory starts at 10,000 per product. Price rises below that and
  falls above. The town drains supply all season, so most products finish below
  equilibrium and sell **above** base price.
- Town shops are drawn **with replacement**, capped at 8 instances — a game with
  three YARN_STOREs wants triple the wool. **Melon has no shop demand at all**;
  only the town centre buys it.
- Quadrants are 5×5 on a 10×10 board (not 8×8), and there is no day-10/day-20
  scaling of town-centre demand.
- **CARE banks a full extra unit** onto an animal's next production: $160–250
  for one action on a cow or sheep, the highest-value single action in the game.

## What has been tried

Kept (all measured head-to-head, both seats, multiple seed sets):

| Change | Result |
|---|---|
| Melon-first opening, inventory-based selling, demand-driven herd | 17/24, +14.6% |
| `TRAVEL_DIVISOR` 0.85 → 12.0 | 24/24, ~+17,000 |
| `ANIMAL_TOTAL_CAP` 17 → 15 | 29/40, +3,040 |
| Endgame waste (no digging or watering that cannot pay off) | wash; kept as correctness |

Falsified — do not retry without a new mechanism:

| Hypothesis | Result |
|---|---|
| Geese / lower `MARGINAL_ACTION_VALUE` | 0/12 twice, at both travel divisors |
| Raise `ANIMAL_TOTAL_CAP` | monotonically worse |
| Cap late wheat below 60 | monotonically worse; the day-18 pivot is fine |
| Crew sized to estimated workload | 0/24; hands are near-free versus action value |
| Per-worker territories (serpentine blocks) | 9/24, −883 |
| Re-weight animal jobs to raise tending | 1/12, −7,683 |
| Copy rank-1's build (no carrot/tomato, strawberry 36, three quadrants) | 29/48, +216 — a wash |
| Move `LATE_WHEAT_PIVOT_DAY` earlier | +3,482 on seeds 150–155, −1,206 on 160–167 — noise |
| Fertilize wheat and carrot (a genuine +100% per tile) | 0/16, −14,092 at the loosest threshold |

The pattern: every win came from finding a **mis-set number in our own code**,
usually after instrumenting the agent. Copying stronger opponents failed seven
times; restructuring the scheduler failed five. Diagnostic metrics improving is
not evidence — the crew-sizing change improved every intermediate metric and
lost 24 games straight.

Fertilizing wheat is the sharpest example of why an opponent's move is not
evidence on its own. The mechanic is real, the doubling is real, and the rank-1
agent does it every game — and copying it still lost 16 games out of 16. Our
action economy is not theirs.
