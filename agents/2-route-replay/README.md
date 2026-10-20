# 2 - Route replay with reflex layers

Replay a recorded 720-step action schedule, then let a stack of small layers
edit it as the game diverges. Each layer reads the public observation, changes
one kind of decision, and passes the action to the next.

Eight submissions, 2026-08-16 to 2026-09-13. This is the family that worked.

| file | submission | date | final score | what changed |
|---|---|---|---|---|
| `route_combined_55563850_final-1747.py` | 55563850 | 08-16 | **1747.4** | V14 route + preemption lookahead 1->3 |
| (not archived) | 55657021 | 08-21 | 1252.5 | 13 end-of-season wheat slots grown as carrot |
| (not archived) | 55677927 | 08-21 | 1211.2 | carrot-or-wheat chosen from the day-26 market |
| `v2_56089373_final-1566.py` | 56089373 | 09-08 | 1566.4 | rebuilt on Arlene's public route + sale overlay |
| `v3_56127567_final-1664.py` | 56127567 | 09-09 | 1664.5 | farm programs rebuilt from Fih / yuki0731 replays |
| `v4_56173004_final-1415.py` | 56173004 | 09-11 | 1414.8 | opening selector, turn-240 rule, geese -> cows |
| `v5_56195164_final-1060.py` | 56195164 | 09-13 | 1060.2 | receding-horizon livestock planner |

The two August variants between 1747 and 1566 were overwritten in place rather
than kept as separate files; they are in git history.

## The arc

1747 down to 1060 looks like decline and mostly is not. The agent at 1747 was
rated against the field of 2026-08-16. By mid-September the score needed to
hold the same rank had risen several hundred points. V3 at 1664 was a
substantially stronger agent than the 1747 one.

V5 is the real regression, and an instructive one. It replaced V4's fixed
livestock rule with a receding-horizon planner, beat V4 **60-10** on 40
held-out seeds in both seats, went **152-8** in a five-way round robin, and
flipped 25 of 53 recorded live losses with none given back. Live it was worth
about 19 rating points and finished *below* V4.

That is the clearest lesson in this folder: a local ladder is only as good as
its opponent pool. Ours was our own lineage plus reconstructions, which is not
the field.

## Measured negatives, so nobody repeats them

- tomato substitution, four donor sets: -146 to -190 wins
- fertilize wheat at age 2: -3,335 margin; at age 3: -96
- sale meter price floor: -26 / -32 / -47 wins; rate cap: -51 / -64 / -75
- eager-sell fertilizer: -151; plus wheat: -208
- lifted routes from ReCurSiON, Ryo Hasegawa, Arman Tuganbaev: 0-6 each
- lifted MiMi route: 6/6 on its selection seeds, then 8-32 on fresh ones
- V4's forced step-0 wheat buy: 2-2, mean margin exactly zero, 36 of 40 drawn
