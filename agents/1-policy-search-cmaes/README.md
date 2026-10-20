# 1 - Policy search, tuned by CMA-ES

A hand-written policy: score every candidate action each turn, take the best.
The numbers in that scoring function were then tuned by CMA-ES against held-out
seeds.

Eleven submissions, 2026-08-08 to 2026-08-16. Final scores 391.1 -> 892.0.

| submission | date | final score | change |
|---|---|---|---|
| 55357136 | 08-08 | 391.1 | first working agent |
| 55359246 | 08-08 | 412.4 | |
| 55361835 | 08-08 | 597.2 | |
| 55364717 | 08-09 | 682.5 | |
| 55367754 | 08-09 | 707.4 | |
| 55368998 | 08-09 | 695.5 | |
| 55387160 | 08-09 | 822.9 | |
| 55397388 | 08-10 | **892.0** | travel divisor 12.0 + endgame waste fixes |
| 55414416 | 08-10 | 851.8 | herd sized to tending capacity, cap 17->15 |
| 55514059 | 08-14 | 841.4 | three-quadrant cap + flat animal cap 14 |
| 55536047 | 08-15 | 859.7 | CMA-ES triple: sheep bias, action value, travel divisor |
| 55563100 | 08-16 | 864.1 | endgame no-buy gate (last 5 days) |

`cmaes_55563100_final-864.py` is the last of the line, byte-identical to
`handoff_bundle/POLICY_AGENT_cmaes_864.py`. Only this one file survives; the
earlier ten are in git history as successive versions of `main.py`.

## Why it stalled

CMA-ES tuned the policy well and the policy itself was the ceiling. Every
submission here sits between 391 and 892, while the first route-replay agent
scored 1747 nine days later. The optimiser can only move what the controller
exposes, and this controller chose one action at a time with no plan for the
season.

Worth noting the local measurements here were real but small: the CMA-ES triple
won 76.6% against 65.1% over 192 held-out games (p=0.013) and still scored
859.7, slightly *below* the agent it replaced. A genuine local win on a weak
architecture does not survive contact with a stronger field.
