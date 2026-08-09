from opponent_archive import forced_agent


def agent(obs):
    """Replay-derived proxy for Rank 1's fixed fast-expansion strategy."""
    return forced_agent(obs, "RANK1")
