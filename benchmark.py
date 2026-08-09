from local_test import run_game


def benchmark(opponents=("starter", "self", "strong", "rank1"), seeds=range(5), steps=720):
    for opponent in opponents:
        rewards = []
        wins = 0
        print(f"\n=== opponent={opponent} ===")
        for seed in seeds:
            env = run_game(opponent=opponent, seed=seed, steps=steps, quiet_engine_warnings=True)
            final_step = env.steps[-1]
            my_reward = final_step[0].reward
            opp_reward = final_step[1].reward
            rewards.append(my_reward)
            wins += 1 if my_reward > opp_reward else 0
            print(f"seed={seed} mine={my_reward} opp={opp_reward}")

        avg_reward = sum(rewards) / max(1, len(rewards))
        print(f"avg_reward={avg_reward:.1f} wins={wins}/{len(rewards)}")


if __name__ == "__main__":
    benchmark()
