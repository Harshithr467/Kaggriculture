# Kaggriculture handoff — start here

## The one thing that will trip you up

Kaggle requires the submitted file to be named `main.py`. That has produced two
files in this project with confusingly similar roles. **They are different
agents and one is much stronger.**

| file here | what it is | strength |
| --- | --- | --- |
| `ROUTE_AGENT_this_is_the_1305_one.py` | frozen 720-step action tape + adaptive layers. **This is what we actually submit** (renamed to `main.py`). | **1304.9** |
| `POLICY_AGENT_cmaes_864.py` | live CMA-ES policy, no tape. Abandoned lineage, but the better architecture long term. | **864**, loses 2-38 head to head |

Optimising the policy agent thinking it is our submission is the single most
expensive mistake available here.

## Read in this order

1. **`HANDOFF.md`** — the brief. §0 is the file confusion above, §1b is the live
   record and the core diagnostic, §7 is our own mistakes (audit these), §11 is
   where to go next.
2. **`REQUIREMENTS-to-beat-the-incumbent.md`** — measured thresholds a challenger
   has to hit, per product, plus the promotion protocol.
3. **`kaggriculture-methods-report.pdf`** — the same record in 3 pages if you
   want the short version.

## The situation in five lines

- Deadline **2026-09-30**; games run ~2 more weeks; final Bradley-Terry after.
- We are at **1304.9**, ~#2,400 of 7,896. Leader is 2991.3.
- We **lost ~400 rating points in two weeks without changing any code.**
- Across 442 live episodes our bank is flat at ~86k while opponents who beat us
  bank ~95k. The agent did not degrade — **the field overtook it.**
- Target: about **8,000 coins a game of production**.

## `opponents/`

Runnable opponents, all stdlib-only, all exposing `agent(obs)`.

**These are other people's work, not ours.** `rayk_c92/c94/c95.py` are decoded
from Rayk Kretzschmar's public notebook; `15-16-strict-future-v25-meta-reset__main.py`
is Kaito Fukami's published artifact; the four `agent_*.py` files are routes
lifted from other teams' public replays. All public and permitted to use, but do
not mistake any of them for our agent, and if one ever ships it needs disclosing
as a lift.

Note: these published artifacts are **much weaker than their authors' live
ratings** — several are marked "not submitted" in their own notebooks. Our agent
beats them 58-2 while sitting 1,000 points below them on the ladder.

## `tools/`

- **`ladder.py`** — the good instrument. Live code vs live code, both seats,
  held-out seeds, Bradley-Terry, town pinned, entrants can carry constant
  overrides, veto opponent supported. **Use this to decide anything.**
- `diversity.py` — per-game outcome agreement between two candidates.
- `wasted_actions.py` — audits no-op field actions against the engine's own
  preconditions. This is what produced the 15.5%-wasted-turns finding behind
  the fusion idea in §11.
- `fixed_town.py` — common random numbers for the town. **Use it whenever
  comparing variants**, or your numbers mean nothing (agent actions perturb the
  RNG that draws the shops).
- `sale_race.py`, `scarcity_scan.py`, `route_census.py` — market and field
  analysis.
- `benchmark_pool.py` — agent loading helper the others import.

They expect `kaggle_environments` with the `kaggriculture` env installed, and
paths relative to a project root. Treat them as reference implementations; the
**protocol** in `HANDOFF.md` §10 matters more than the code.

## The rule that cost us the most

**Never promote a candidate on a positive result from a replay benchmark.** Ours
scored a candidate **+24 wins** over the agent that then beat it **32-8** on
held-out seeds. Wrong sign, not noise. Decide on seeds the candidate has never
seen, both seats, with the incumbent as a veto opponent.
