import contextlib
import io
import sys


def _make_env(steps, seed, debug, quiet_engine_warnings=True):
    if quiet_engine_warnings:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
            return make("kaggriculture", configuration={"seed": seed, "episodeSteps": steps}, debug=debug)

    from kaggle_environments import make
    return make("kaggriculture", configuration={"seed": seed, "episodeSteps": steps}, debug=debug)


def run_game(opponent="random", seed=0, steps=720, debug=False, quiet_engine_warnings=True):
    env = _make_env(steps, seed, debug, quiet_engine_warnings=quiet_engine_warnings)
    opponent_ref = resolve_opponent(opponent)
    env.run(["main.py", opponent_ref])

    final_step = env.steps[-1]
    for index, state in enumerate(final_step):
        print(f"player={index} status={state.status} reward={state.reward}")

    return env


def resolve_opponent(opponent):
    """Friendly names for opponents; anything else is passed through.

    Built-in names `random`, `starter` and `pass` come from the environment.
    For a head-to-head against a previous version of our own agent, use
    benchmark_ab.py instead -- it loads any git revision and plays both seats.
    """
    aliases = {
        "self": "main.py",
        "strong": "opponent_strong.py",
        "stronger": "opponent_strong.py",
    }
    return aliases.get(opponent, opponent)


if __name__ == "__main__":
    opponent = sys.argv[1] if len(sys.argv) > 1 else "random"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    run_game(opponent=opponent, seed=seed)
