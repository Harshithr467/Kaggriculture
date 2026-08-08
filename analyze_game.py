import contextlib
import io


def summarize(obs, player):
    farm = obs["farms"][player]
    counts = {}
    for row in farm["tiles"]:
        for tile in row:
            if tile is None or tile == "LOCKED":
                continue
            if tile.get("kind") == "PLANT":
                key = tile["crop"]
            elif "animal" in tile:
                key = tile["animal"]
            else:
                key = tile.get("kind", "OTHER")
            counts[key] = counts.get(key, 0) + 1
    return farm["money"], len(farm.get("hands", [])), counts


def main():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        from kaggle_environments import make

        env = make("kaggriculture", configuration={"seed": 0, "episodeSteps": 720}, debug=True)
    env.run(["main.py", "starter"])
    for step in range(23, len(env.steps), 24):
        obs = env.steps[step][0].observation
        mine = summarize(obs, 0)
        opp = summarize(obs, 1)
        prices = obs["market"]["prices"]
        private = obs.get("private", {})
        shed = {k: v for k, v in private.get("shed", {}).items() if v}
        seeds = {k: v for k, v in private.get("seeds", {}).items() if v}
        carried = sum(sum(inv.values()) for inv in private.get("inventories", []))
        print(
            f"day={obs.get('day')} mine={mine} opp={opp} "
            f"shed={shed} seeds={seeds} carried={carried} prices={prices}"
        )
    final = env.steps[-1]
    for step, states in enumerate(env.steps):
        action = states[0].action
        if action and "GOOSE" in str(action):
            print(f"goose_action step={step} action={action}")
    print("final", [(state.status, state.reward) for state in final])


if __name__ == "__main__":
    main()
