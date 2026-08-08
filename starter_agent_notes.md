## Starter Agent Notes

This first pass is intentionally a crop-first baseline built from the Kaggriculture README, the AGENTS getting-started guide, and the strategy notebook architecture.

What it does:
- Keeps the submission in a single `main.py` with a safe `agent(obs)` wrapper.
- Uses a role-planning step to assign owned tiles to crops.
- Uses a job list plus greedy worker-to-job assignment each turn.
- Sells shed inventory with simple reserve prices and starts a basic endgame glide path.
- Buys seeds, hires cheap early hands, and unlocks land when cash permits.

What it does not do yet:
- No animals yet.
- No opponent-aware market prediction yet.
- No Hungarian assignment yet.
- No price-history memory across turns or phase-specific fine tuning.

Best next upgrades, in order:
1. Add local self-play evaluation against `random`, `pass`, and `starter`.
2. Replace greedy assignment with Hungarian matching.
3. Add opponent-aware glut prediction before planting premium crops.
4. Add a small animal program with strict feed/care priority.
5. Tune crop targets and reserve prices from replay reviews.
