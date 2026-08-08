import contextlib
import io


def _make_env(steps, seed, debug, quiet_engine_warnings=True):
    if quiet_engine_warnings:
        with contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
            return make("kaggriculture", configuration={"seed": seed, "episodeSteps": steps}, debug=debug)

    from kaggle_environments import make
    return make("kaggriculture", configuration={"seed": seed, "episodeSteps": steps}, debug=debug)


def run_game(opponent="random", seed=0, steps=720, debug=False, quiet_engine_warnings=True):
    env = _make_env(steps, seed, debug, quiet_engine_warnings=quiet_engine_warnings)
    env.run(["main.py", opponent])

    final_step = env.steps[-1]
    for index, state in enumerate(final_step):
        print(f"player={index} status={state.status} reward={state.reward}")

    return env


if __name__ == "__main__":
    run_game()
