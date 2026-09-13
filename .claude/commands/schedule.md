---
description: The daily 09:00 Kaggriculture check - standing, replays, leaderboard movement, new public work, and one concrete proposal.
---

# Daily check

Run this every morning. Steps 1–4 are mechanical and scripted; step 5 is the one that
matters and is yours to do.

Read [/goal](goal.md) first if you have not this session — it carries the promotion
rules and the reason overall win rate is not the metric.

## 1. Run the scripted half

```bash
python daily_report.py
```

This downloads today's leaderboard, diffs the top 10 and top 25 against the last
snapshot, lists our live submissions and ratings, downloads every new replay for our
best-rated live submission, and writes `reports/daily-YYYY-MM-DD.md`.

It takes a while — the replay download is the slow part. `--no-replays` skips it for a
quick standing check.

## 2. Report the standing

From the report, state plainly:

- our rank and rating, and the change since the last check
- each live submission and its rating (only the latest 2 are rated)
- days remaining to **2026-09-30**
- wins, losses and overall win rate for the best live submission

## 3. Report the number that actually matters

The report prints a win-rate table bucketed by the opponent's current rank. **Lead
with that, not the overall win rate.** Overall win rate mostly measures how far up the
ladder we have climbed; the top buckets measure whether we are getting better.

If the top buckets have not moved since the last check, say so directly. A rising
overall win rate with flat top buckets is not progress.

Also list the losses to ranked opponents — those replays are the study material.

## 4. Check what other people published

The report lists new notebooks on the Code tab. Also check the Discussion tab, which
the CLI covers only partly:

```bash
.venv/Scripts/kaggle.exe kernels list --competition kaggriculture --sort-by dateRun --page-size 30
.venv/Scripts/kaggle.exe forums topics --help
```

Pull anything that looks like a strategy writeup or a scoring agent:

```bash
.venv/Scripts/kaggle.exe kernels pull <ref> -p kernels/
```

Judge them against what we already know — several public notebooks transcribe the
CARROT/TOMATO/EGG price curves as log/linear when the engine uses `hinge`, and are
wrong on exactly the side of the curve that pays. Do not import a claim without
checking it against `kaggriculture.py`.

## 5. Propose one change, aimed at the top buckets

This is the point of the whole routine. Using the day's losses to ranked opponents,
propose **one** concrete change, and say what result would falsify it.

Then test it properly before recommending anything:

```bash
python ladder.py --pool "kernels/candidate.py#new" "kernels/<incumbent>.py#live" \
    --seeds <a block never used before> --workers 11
```

Both seats, fresh seeds, incumbent as veto. Do not recommend a submission on local
pool percentages or on `bench_losses.py` — see [/goal](goal.md) for why both have
misled us, with numbers.

## Keeping the seed ledger honest

Every screening block must be one no candidate has seen. Used so far:

```
9000-9009, 9700-9724, 9800-9819    early ladder work
71001-71008, 71101-71108, 71201-71212, 71301-71308   V4 development (external)
72001-72020, 72101-72120           V4 final blocks (external)
81001-81004, 81101-81112, 81201-81212, 81301-81312   V5 development (external)
83001-83020, 83101-83120           V5 final blocks (external)
88000-88039, 88100-88119, 88200-88219   our V4 screening
91000-91039, 91100-91119           our V5 screening
```

Pick the next unused block and append it here.
