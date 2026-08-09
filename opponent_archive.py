from benchmark_versions import VERSIONS, load_module


_STRATEGY = load_module("archived_v5_opponent", VERSIONS["v5"])


def forced_agent(obs, mode):
    return _STRATEGY.run_strategy(obs, forced_mode=mode)
