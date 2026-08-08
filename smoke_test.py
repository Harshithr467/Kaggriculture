from main import agent


def make_obs():
    tiles = [["LOCKED" for _ in range(10)] for _ in range(10)]
    for y in range(5):
        for x in range(5):
            tiles[y][x] = None

    return {
        "player": 0,
        "step": 0,
        "day": 0,
        "hour": 0,
        "farms": [
            {
                "money": 3000,
                "tiles": tiles,
                "farmer": [4, 4],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
            {
                "money": 3000,
                "tiles": tiles,
                "farmer": [4, 4],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
        ],
        "market": {
            "inventory": {
                "WHEAT": 10000,
                "CARROT": 10000,
                "TOMATO": 10000,
                "STRAWBERRY": 10000,
                "MELON": 10000,
            },
            "prices": {
                "WHEAT": 25,
                "CARROT": 35,
                "TOMATO": 60,
                "STRAWBERRY": 120,
                "MELON": 250,
            },
        },
        "town": {"unlocked_shops": []},
        "private": {
            "shed": {},
            "seeds": {},
            "inventories": [{}],
        },
    }


def main():
    obs = make_obs()
    action = agent(obs)
    assert isinstance(action, dict)
    assert "farmer" in action and "hands" in action and "market" in action
    assert isinstance(action["farmer"], list)
    assert isinstance(action["hands"], list)
    assert isinstance(action["market"], list)
    print(action)


if __name__ == "__main__":
    main()
