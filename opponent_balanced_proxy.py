from opponent_archive import forced_agent


def agent(obs):
    return forced_agent(obs, "BALANCED_PROXY")
