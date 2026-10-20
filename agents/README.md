# Submitted agents

Every agent we actually submitted to Kaggriculture, grouped by the technique it
used. File names are `<name>_<submission id>_final-<score>.py`, where the score
is the one on the final leaderboard after the 2026-09-30 deadline.

**Final standing: #2903 of 10,148 (top 28.6%), score 1324.4.**

| folder | technique | submissions | best final score |
|---|---|---|---|
| [1-policy-search-cmaes](1-policy-search-cmaes/) | hand-written policy, parameters tuned by CMA-ES | 11 | 892.0 |
| [2-route-replay](2-route-replay/) | replay a recorded 720-step route, repaired by reflex layers | 8 | 1747.4 |
| [3-public-lineage](3-public-lineage/) | a public Apache-2.0 agent, adopted wholesale | 1 | 1324.4 |

These are copies. The working files stay where the harness expects them
(`main.py`, `agent_combined.py`, `kernels/candidate_v*.py`), because
`bench_losses.py`, `ladder.py`, `diversity.py` and about ten other scripts
reference them by path.

## What the scores do and do not say

They are not comparable across dates. The field inflated faster than we
improved, and most of it happened in the final three weeks. Measured at fixed
ranks on the public leaderboard:

```
rank      09-11    09-13    change
1          3154     3249      +95
25         2894     2901       +7
1000       2256     2319      +63
2000       1604     1687      +83
```

The score needed to hold rank 2000 rose +83 in two days while ours rose +42.
`agent_combined`'s 1747.4 was set on 2026-08-16 against a much weaker field; it
is the highest number we ever held but not our strongest agent.

Only the latest two submissions stay rated, and the final standing takes the
better of those two. So the 1747.4 was retired long before the deadline and
never counted — the final 1324.4 came from the two slots live on 09-30.

## The three things worth keeping

**Route replay beat planning, decisively and twice.** Our planner-based V5
scored 1060 final. The author of the public 2945 agent built a from-scratch
demand-driven planner and measured it at 990-1,578 live, against 2,945 for
their tape. Two independent teams, same band. A full-season rollout also costs
2-9 s against a 1 s per-action budget, so planning cannot be done inside the
engine without a surrogate model nobody built.

**Crop substitution only works where the donor's actions already fit the new
crop's calendar.** Swapping end-of-season wheat for carrot paid, because carrot
waters at ages 2-3 and the route lifts wheat at age 3. The other eight
substitutions we tried did not. The public 2945 author hit the same wall from
the other side and wrote it the same way: "a tomato program needs a different
labour plan, not just a different crop choice."

**Benchmarks that cannot react will rank comparable agents wrongly.** Replaying
fixed opponent tapes had the *sign* wrong on a lifted MiMi route by 24 wins. A
live code-vs-code ladder on held-out seeds is the only measurement that tracked
reality -- and even that overpredicted V5 at 60-10 when it was worth 19 live
rating points, because the opponent pool was our own lineage rather than the
field.

See [../NOTES-meta-mechanics.md](../NOTES-meta-mechanics.md) for the engine
mechanics and [../HANDOFF.md](../HANDOFF.md) for the full experiment record.
