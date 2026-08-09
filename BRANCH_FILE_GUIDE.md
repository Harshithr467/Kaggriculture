# Branch File Guide

## Scope

This document describes the files currently present in the working tree for branch
`codex/rank-1-strategy` as of August 9, 2026. It covers both files already tracked by
Git and newer uncommitted files created during replay analysis and agent tuning.

The working tree is not clean. `main.py`, `analyze_game.py`, `benchmark.py`, and
`local_test.py` have changes that are not committed. The newer Kaggle analysis tools,
opponent wrappers, CSV files, and downloaded replays are also untracked. A file being
described here does not mean it is safely stored in Git history.

The `.git/` repository database and the approximately 40,000 dependency files under
`.venv/` are not documented individually. They are repository internals and installed
third-party packages rather than project source files.

## Project Flow

```text
Kaggle observation
       |
       v
main.agent(obs)
       |
       v
run_strategy
       |
       +-- market history and opponent pressure
       +-- tile role plan
       +-- farm job generation
       +-- worker-to-job assignment
       +-- market buy/sell decisions
       |
       v
Kaggle action dictionary
```

Only `main.py` is required for a normal single-file Kaggle submission. The analysis,
benchmark, replay, and opponent files are local development tools.

## Submission Agent

### `main.py`

The standalone competition agent. Its last function is `agent(obs)`, which satisfies
Kaggle's requirement that the last `def` accept an observation and return an action.
The agent is based on the recovered Unlabeled v4 design, not the Rank 1 strategy.

The current strategy:

- Uses wheat as a cheap filler so unlocked acreage does not remain empty and grow weeds.
- Preserves established crop and animal blocks when more land is unlocked.
- Uses visible opponent crops to shift production between melon and strawberry.
- Uses market peak memory to detect milk and wool price collapses.
- Stops buying the affected animal after a product-market crash and liquidates shed stock.
- Normally stops at three plots. Fourth land requires an exceptional early, wealthy,
  highly utilized, high-price, low-pressure state.
- Hires more hands as land expands: targets 7, 9, 12, and 13 hands for one through four plots.
- Uses sticky greedy job assignment with soft quadrant ownership. Routine workers remain
  local, but urgent feeding, placement, or high-value work can cross quadrants.
- Uses a safe exception wrapper that returns a PASS response rather than crashing a match.

Important constants and data tables:

| Name | Purpose |
|---|---|
| `TOTAL_DAYS`, `TURNS_PER_DAY` | Defines the 30-day, 24-turn-per-day season. |
| `CROPS` | Seed cost, base price, maturity, yield, and ongoing-harvest rules for each crop. |
| `ANIMALS` | Purchase cost, output product, structure type, and baseline information. |
| `LAND_COSTS` | Costs for the second, third, and fourth quadrants. |
| `RESERVE_FRAC` | Minimum relative sell-price targets before endgame and pressure adjustments. |
| `_MEMORY` | Per-player worker target memory used to reduce target switching. |
| `_MARKET_MEMORY` | Per-player price peaks and previous prices; resets at a new episode. |

Function reference:

| Function | Responsibility |
|---|---|
| `run_strategy` | Coordinates all planning stages and builds the final farmer, hands, and market response. |
| `update_market_signals` | Tracks price peaks, drawdowns, and one-turn price changes. |
| `estimate_opponent_pressure` | Estimates future market supply from visible opponent crops. |
| `imminent_supply_score` | Scores how close one opponent crop tile is to producing supply. |
| `build_role_plan` | Assigns each owned tile to wheat, premium crops, pasture, coop, or idle use. |
| `crop_targets` | Chooses base wheat, melon, and strawberry quantities and shifts away from crowded crops. |
| `animal_targets` | Sets cow and sheep limits by land count and disables purchases after price crashes. |
| `product_market_crashed` | Detects a 14% peak drawdown or a severe absolute price collapse. |
| `build_jobs` | Converts farm state and tile roles into build, plant, water, harvest, feed, care, collect, fertilize, and dig jobs. |
| `total_accessible_items` | Totals items in the shed and all worker inventories. |
| `should_harvest` | Determines when ongoing and one-time crops should be harvested. |
| `should_water` | Determines whether watering can improve or protect crop output. |
| `harvest_bonus` | Adds urgency and crop-specific value to harvest jobs. |
| `water_job_value` | Values watering based on dryness, crop maturity, and remaining days. |
| `plant_value` | Estimates planting value from yield, price, timing, and opponent pressure. |
| `fertilizer_job_value` | Uses fertilizer only when expected premium-crop gains exceed its cost. |
| `build_market_orders` | Sells inventory and budgets hires, wheat, land, animals, and seeds. |
| `desired_animal_buys` | Compares assigned structures with owned or carried animals. |
| `desired_wheat_buffer` | Reserves enough wheat to keep animals fed. |
| `desired_fertilizer_reserve` | Keeps only the fertilizer likely to be used profitably. |
| `sell_priority` | Sorts shed inventory by current profitability and endgame urgency. |
| `prioritized_seed_orders` | Buys seeds for empty assigned tiles in value order. |
| `should_buy_land` | Controls expansion and applies the strict fourth-land gate. |
| `operating_cash_floor` | Protects cash needed for normal farm operation. |
| `desired_hand_count` | Increases worker targets with unlocked land. |
| `reserved_seed_budget` | Estimates cash needed for near-term seed purchases. |
| `empty_tiles_by_role` | Counts unfilled tiles assigned to each crop. |
| `reserve_price` | Calculates dynamic sell thresholds. |
| `opponent_glut_factor` | Converts visible opponent supply into a crop-specific penalty. |
| `base_price_for_item` | Returns the reference price for crops and products. |
| `shed_load` | Measures shed utilization against its 100-item capacity. |
| `next_land_cost` | Returns the price of the next quadrant or `None`. |
| `fib_cost` | Calculates the increasing same-day hire cost. |
| `assign_jobs` | Greedily matches workers to unique jobs using distance, target stickiness, and quadrant penalties. |
| `action_for_job` | Moves toward a job, visits the shed for required items, or executes the job. |
| `action_for_profitable_drop` | Returns carried sale goods to a shed when the load and market justify the trip. |
| `nearest_shed_tile`, `shed_tiles` | Locates the central shed access tiles. |
| `step_toward` | Produces one cardinal movement action toward a destination. |
| `distance_to_shed`, `manhattan` | Supplies routing distance calculations. |
| `quadrant_for_pos` | Maps a board coordinate to NW, NE, SW, or SE. |
| `take_front`, `take_back` | Removes role-assignment slices from an ordered tile list. |
| `make_job` | Creates the internal job dictionary format. |
| `agent` | Kaggle entrypoint and final exception boundary. |

## Local Execution And Tests

### `local_test.py`

Creates a local `kaggriculture` environment, resolves friendly opponent aliases, runs
`main.py` as player 0, and prints both final statuses and rewards. Its command-line
arguments are opponent name followed by seed.

```powershell
.\.venv\Scripts\python.exe local_test.py random 0
.\.venv\Scripts\python.exe local_test.py rank1 0
```

Aliases include `self`, `strong`, `rank1`, `three-premium`, `balanced-proxy`, and
`crop-rush`. Import and environment startup output is redirected to hide the unrelated
OpenSpiel game-list warnings where possible.

### `benchmark.py`

Runs repeated full seasons through `local_test.run_game`. The default matrix tests
`starter`, self-play, `strong`, and the archived Rank1 proxy over seeds 0 through 4.
It reports each score, average agent reward, and wins per opponent.

### `smoke_test.py`

Builds a minimal synthetic day-zero observation and calls `main.agent`. It verifies
that the result is a dictionary with correctly typed `farmer`, `hands`, and `market`
sections. It checks interface shape, not strategic quality or environment legality.

### `analyze_game.py`

Runs one local game against `starter`, prints daily money, hands, crop/animal counts,
shed contents, seeds, carried inventory, and prices. It also inspects role allocation
at selected midgame steps and prints early feeding and goose-related actions. This is
useful for debugging why a local score occurred.

## Controlled Opponents

### `opponent_strong.py`

A hand-written premium-crop opponent that reuses low-level helpers from `main.py` but
has its own role plan and market policy. It begins crop-heavy, adds melon and strawberry,
introduces animals later, uses only four to eight hands, expands with cash buffers, and
prioritizes premium-seed purchases. It is independent of the archived forced modes.

### `opponent_archive.py`

Loads the recovered Unlabeled v5 source through `benchmark_versions.load_module` and
exposes `forced_agent(obs, mode)`. This keeps Rank1-derived test behavior outside the
submitted `main.py`.

Important: the v4 and v5 references are unreachable Git blob objects, not commits.
`git gc` may eventually delete them. The current object IDs are:

- v4: `21a5707143e805d838a1a0f8d096365de26aa8cd`
- v5: `383db66fc9d982f489753ac9864ec69613102442`

### `opponent_rank1.py`

Thin wrapper that runs archived mode `RANK1`, a fixed fast-expansion replay-derived proxy.

### `opponent_three_premium.py`

Thin wrapper that runs archived mode `THREE_PREMIUM`, emphasizing three-land premium crops.

### `opponent_balanced_proxy.py`

Thin wrapper that runs archived mode `BALANCED_PROXY`, combining crops and animal production.

### `opponent_crop_rush.py`

Thin wrapper that runs archived mode `CROP_RUSH`, emphasizing rapid premium-crop production.

## Version And Replay Benchmarks

### `benchmark_versions.py`

Dynamically loads four agent snapshots:

| Label | Source |
|---|---|
| `v3` | Committed file `c17addc:main.py`. |
| `v4` | Recovered blob immediately preceding the Unlabeled v4 submission. |
| `v5` | Recovered blob containing archived forced opponent modes. |
| `current` | Working-tree `main.py`. |

Each candidate plays archived Rank1, three-premium, balanced, and crop-rush modes from
both player seats. It reports win rate, average reward, and average margin. Because a
full 720-turn game is expensive, `--seeds 1` is appropriate for a quick gate and larger
seed counts should be reserved for final validation.

### `benchmark_replay_opponents.py`

Runs a candidate against action streams extracted from the 31 real Kaggle replays for
submission `55368998`. It restores each episode's original random seed and seat. The
`--verify` option runs both original action streams and checks that the replay result is
reproduced exactly. This tool produced the 26/31 retrospective result for current
`main.py`.

Recorded action streams do not react to the candidate's changed market behavior, so
this is a strong regression test but not a guaranteed forecast of live win rate.

```powershell
.\.venv\Scripts\python.exe benchmark_replay_opponents.py current --outcome LOSS
.\.venv\Scripts\python.exe benchmark_replay_opponents.py current --outcome WIN
```

## Replay Analysis Tools

### `analyze_replays.py`

Processes every `replays/episode-*-replay.json` file. For both players it reports final
and maximum money, land-unlock days, peak farm contents, important purchases, and counts
of planting, watering, harvesting, feeding, and care actions.

### `analyze_strategy_replay.py`

Detailed one-replay command-line analyzer. It prints all market totals, unit operation
totals, and selected daily snapshots containing money, land, hands, empty tiles, farm
contents, shed contents, seeds, carried items, and premium-market prices.

### `compare_rank_replays.py`

Compares one or more replay files with emphasis on Rank 1-style behavior. It summarizes
movement versus productive work, passes, drops, hires, premium purchases and sales,
land timing, peak crops and animals, final utilization, and checkpoint timelines.

### `analyze_kaggle_history.py`

Authenticates with the Kaggle API and queries public episodes for six known submissions.
It calculates per-submission and overall win rates, average rewards, seats, margins, and
opponents, then rewrites `kaggle_episode_data/episode_results.csv`. Network access and
valid Kaggle credentials are required.

### `analyze_replay_set.py`

Processes all downloaded replays for submission `55368998` from our agent's perspective.
It writes `replay_metrics_55368998.csv` with movement, productive work, market totals,
land timing, peak crops and animals, and empty/weed snapshots on selected days. It also
prints win-versus-loss averages and losses ordered by margin.

### `analyze_kaggle_opponents.py`

Processes the same replay set from each opponent's perspective. It compares opponents
we beat with opponents that beat us and assigns coarse labels such as `ONE_LAND_MELON`,
`PREMIUM_BALANCED`, `STRAWBERRY_RUSH`, and `ANIMAL_HEAVY`.

## CSV Data

All files in `kaggle_episode_data/` are generated analysis inputs or outputs and are
currently untracked.

| File | Purpose |
|---|---|
| `episodes_55357136.csv` | Raw episode listing for submission Trial 1. |
| `episodes_55359246.csv` | Raw episode listing for submission Better version. |
| `episodes_55361835.csv` | Raw episode listing for Market-aware route v3. |
| `episodes_55364717.csv` | Raw episode listing for Unlabeled v4. |
| `episodes_55367754.csv` | Raw episode listing for Unlabeled v5. |
| `episodes_55368998.csv` | Raw episode listing for Rank1 hybrid ripple v1. |
| `episode_results.csv` | Normalized 156-episode history with submission, opponent, seat, rewards, margin, and outcome. |
| `replay_metrics_55368998.csv` | Action-level metrics generated from the 31 downloaded current-submission replays. |

## Current Submission Replays

Every JSON file under `kaggle_episode_data/replays/55368998/` stores the complete
configuration, random seed, player metadata, 720 steps of observations/actions, final
statuses, and rewards for one real Kaggle episode. These files are large and untracked.

| File | Original result | Opponent | Our reward | Opponent reward |
|---|---:|---|---:|---:|
| `episode-91226389-replay.json` | WIN | ceh | 69,345 | 39,202 |
| `episode-91227049-replay.json` | LOSS | tehyoni | 58,476 | 64,880 |
| `episode-91227955-replay.json` | WIN | dprinzensteiner | 71,566 | 45,927 |
| `episode-91228843-replay.json` | WIN | Madhur Sabherwal | 64,969 | 42,498 |
| `episode-91229719-replay.json` | WIN | Guruprasad Parasnis | 67,805 | 67,428 |
| `episode-91230603-replay.json` | LOSS | T88 | 65,632 | 81,068 |
| `episode-91231520-replay.json` | LOSS | Mark Holloway | 44,826 | 58,090 |
| `episode-91232419-replay.json` | LOSS | Luc Mantoux | 74,814 | 77,964 |
| `episode-91233309-replay.json` | WIN | Mohit Shirke | 70,467 | 56,856 |
| `episode-91234198-replay.json` | WIN | Imran Ahamed | 67,937 | 45,007 |
| `episode-91235082-replay.json` | WIN | CHRISTOPHER CRILLY | 37,890 | 28,010 |
| `episode-91235980-replay.json` | WIN | knadithyavr | 52,061 | 41,895 |
| `episode-91236911-replay.json` | LOSS | Mathijs Deelen | 64,345 | 77,065 |
| `episode-91237771-replay.json` | LOSS | Yuta Tomimasu | 68,270 | 70,233 |
| `episode-91238674-replay.json` | LOSS | Speedrun retirement | 75,120 | 85,057 |
| `episode-91239571-replay.json` | WIN | t@got@go | 51,698 | 47,577 |
| `episode-91240461-replay.json` | LOSS | Harsha Vardhan | 74,966 | 81,867 |
| `episode-91241379-replay.json` | WIN | Pat | 49,597 | 35,153 |
| `episode-91242269-replay.json` | WIN | Richard G Atkinson | 80,969 | 77,895 |
| `episode-91243167-replay.json` | LOSS | Alvaro Llamojha | 52,837 | 54,273 |
| `episode-91244063-replay.json` | LOSS | Nguyen Phuc Gia Bao | 69,611 | 84,623 |
| `episode-91244998-replay.json` | LOSS | F4 | 91,729 | 92,528 |
| `episode-91245897-replay.json` | WIN | Roberto Garcia | 57,377 | 48,803 |
| `episode-91246792-replay.json` | LOSS | Ayush Roy | 55,660 | 56,995 |
| `episode-91254768-replay.json` | LOSS | Gabriele Giacometti | 44,559 | 49,543 |
| `episode-91285083-replay.json` | WIN | Versilogic | 47,243 | 39,649 |
| `episode-91299082-replay.json` | WIN | Friaseus | 51,589 | 40,967 |
| `episode-91323460-replay.json` | WIN | Ruben Maya | 59,438 | 28,048 |
| `episode-91325985-replay.json` | LOSS | Tianfang Li | 59,748 | 144,897 |
| `episode-91337981-replay.json` | LOSS | MarvelousXun | 55,713 | 69,308 |
| `episode-91345890-replay.json` | WIN | MoongladeAI | 79,338 | 48,779 |

## Earlier Replay Samples

The five tracked files under `replays/` are older real-match samples used by
`analyze_replays.py`. Each has the same full Kaggle replay structure.

| File | Players | Rewards |
|---|---|---|
| `replays/episode-91112137-replay.json` | Jia Chen vs Harshith revuru | 27,828 vs 9,650 |
| `replays/episode-91113043-replay.json` | fatariq vs Harshith revuru | 24,678 vs 14,810 |
| `replays/episode-91120915-replay.json` | Harshith revuru vs Universal Entropy | 23,077 vs 8,908 |
| `replays/episode-91124245-replay.json` | Harshith revuru vs Hyezir4 | 29,900 vs 6,214 |
| `replays/episode-91130530-replay.json` | Ronel maamoc vs Harshith revuru | 7,920 vs 712 |

## Documentation Files

### `README.md`

Currently contains only the project heading `New-project`. It does not explain setup,
strategy, testing, or submission. This branch guide is the substantive documentation.

### `starter_agent_notes.md`

Historical notes for the original crop-first starter. They describe the early role/job
architecture and list upgrades that were missing at that time. Several statements are
now obsolete: the current agent has animals, opponent pressure, market memory, replay
testing, and phase-specific tuning.

### `BRANCH_FILE_GUIDE.md`

This document. It is the inventory, architecture overview, and operational map for the
current branch working tree.

The original `AGENTS.md`, strategy notebook, and source `README.md` from the Downloads
folder are external references. They are not files in this Git working tree.

## Generated Python Cache Files

`__pycache__/` contains bytecode generated automatically when Python imports or compiles
modules. These files do not contain independent strategy logic and should not be edited
or submitted. Python recreates them as needed.

Current cache files correspond to these modules and runtimes:

```text
analyze_game.cpython-313.pyc
analyze_replay_set.cpython-313.pyc
analyze_replays.cpython-313.pyc
analyze_strategy_replay.cpython-313.pyc
benchmark.cpython-312.pyc
benchmark.cpython-313.pyc
benchmark_replay_opponents.cpython-313.pyc
benchmark_versions.cpython-313.pyc
compare_rank_replays.cpython-313.pyc
local_test.cpython-312.pyc
local_test.cpython-313.pyc
main.cpython-312.pyc
main.cpython-313.pyc
opponent_archive.cpython-313.pyc
opponent_balanced_proxy.cpython-313.pyc
opponent_crop_rush.cpython-313.pyc
opponent_rank1.cpython-313.pyc
opponent_strong.cpython-312.pyc
opponent_strong.cpython-313.pyc
opponent_three_premium.cpython-313.pyc
```

Some cache files are currently tracked and modified, while others are untracked. They
should eventually be removed from version control and covered by `.gitignore`.

## Environment And Repository Internals

### `.venv/`

Local Python virtual environment containing Python, pip, `kaggle`,
`kaggle_environments`, OpenSpiel, and their dependencies. It is machine-specific,
contains roughly 40,000 files, and must not be uploaded to Kaggle or committed.

### `.git/`

Git metadata containing branches, commits, objects, and the index. It currently also
contains the unreachable v4 and v5 source blobs used by local archived opponents.
Deleting `.git/` or running aggressive garbage collection can break those local tools.

## What To Submit

Submit only `main.py` for the current single-file agent:

```powershell
.\.venv\Scripts\kaggle.exe competitions submit kaggriculture -f main.py -m "Adaptive v4 routing and market strategy"
```

Do not include replay JSON files, CSV analysis outputs, opponent agents, benchmark
scripts, `.venv/`, `.git/`, or `__pycache__/` in the Kaggle submission.
