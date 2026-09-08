"""Common random numbers for the town, so two agent variants play the same game.

THE PROBLEM THIS SOLVES

The environment re-seeds per day, which looks reproducible:

    rng = random.Random((seed * 1_000_003) ^ day)
    for player_id, farm in enumerate(obs0.farms):
        ...
        _spawn_weeds(farm, board_size, weed_chance, rng)     # consumes draws
    ...
    town["unlocked_shops"].append(rng.choice(sorted(SHOPS))) # from what is left

Weed spawning walks every unlocked tile of BOTH farms and draws from that same
stream, so how many draws it consumes depends on how much land the agents
bought and what they planted. Change your agent and you change the stream
position the shop draw lands on -- so you change which shops the town opens.

Measured on seed 600, one constant changed in our own agent:

    ROLE_MISMATCH_FACTOR 1.0 -> YARN_STOREx2, SMOOTHIE_SHOPx2, FARMERS_MARKETx1
    ROLE_MISMATCH_FACTOR 0.6 -> no yarn store at all, SMOOTHIE_SHOPx3, ICE_CREAMx2

Those are different games. Wool is the richest market in the first and absent
from the second. Comparing the two agents' scores compares two economies, and
"our score went up $8,399" meant the dice landed differently.

WHAT IS AND IS NOT AFFECTED

Win/loss is still sound without this: both players face the same town inside any
one game, so the head-to-head is fair, and over many seeds win rate is a valid
comparison. It is ABSOLUTE SCORES between variants that are not comparable --
and margin only partly, since a rich town lifts both farms.

WHAT THIS DOES

Draws the shop from a stream of its own, so a seed names one town no matter how
the agents behave. This is a benchmarking control -- common random numbers, the
standard trick for comparing policies on a stochastic simulator -- not a change
to the real game. Never enable it when reproducing a live episode.

    import fixed_town
    fixed_town.enable()      # idempotent, process-local
"""
import random

_ORIGINAL = None


def enable():
    """Make the town's shop draw independent of agent behaviour."""
    global _ORIGINAL
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    if _ORIGINAL is not None:
        return
    _ORIGINAL = K._end_of_day

    def patched(state, env, day):
        town = state[0].observation.town
        before = len(town.get("unlocked_shops", []))
        _ORIGINAL(state, env, day)
        shops = town.get("unlocked_shops", [])
        if len(shops) > before:
            # The env just drew one from the shared stream; replace it with one
            # from a stream nothing else touches. Same distribution, same count,
            # same day -- but no longer a function of how the farms were played.
            seed = env.info.get("seed", 0) or 0
            rng = random.Random((int(seed) * 7_919) ^ day)
            shops[-1] = rng.choice(sorted(K.SHOPS))

    K._end_of_day = patched


def disable():
    global _ORIGINAL
    if _ORIGINAL is None:
        return
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    K._end_of_day = _ORIGINAL
    _ORIGINAL = None
