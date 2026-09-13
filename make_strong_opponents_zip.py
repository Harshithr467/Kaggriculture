"""Package every on-disk replay featuring a team that reached the top N on ANY
recent leaderboard snapshot.

    python make_strong_opponents_zip.py --top 25 --snapshots 3 --out strong.zip

Why the union rather than today's top 25: the board churns fast. Between the
2026-09-09 and 2026-09-11 snapshots, 18 of the top 25 were new names. Packaging
only today's top 25 therefore throws away replays of teams that were top 25
forty-eight hours ago and are still strong -- and today's new entrants mostly
have no replays on disk yet, so the "fresher" bundle is the emptier one.

The manifest carries each team's rank in every snapshot, so the recipient can
see who is rising, who is falling, and who has been there the whole time.
"""
import argparse
import collections
import csv
import glob
import io
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ap = argparse.ArgumentParser()
ap.add_argument("--top", type=int, default=25)
ap.add_argument("--snapshots", type=int, default=3,
                help="how many of the most recent leaderboard files to union")
ap.add_argument("--out", required=True)
args = ap.parse_args()

boards = sorted(glob.glob("kaggle_episode_data/kaggriculture-publicleaderboard-*.csv"))
boards = boards[-args.snapshots:]
if not boards:
    raise SystemExit("no leaderboard snapshots found")

# team -> {snapshot label: (rank, score)}
history = collections.defaultdict(dict)
want = set()
labels = []
for path in boards:
    label = os.path.basename(path).replace("kaggriculture-publicleaderboard-", "")
    label = label.replace(".csv", "").split("T")[0]
    labels.append(label)
    for row in csv.DictReader(io.open(path, encoding="utf-8-sig")):
        rk = int(row["Rank"])
        history[row["TeamName"]][label] = (rk, float(row["Score"]))
        if rk <= args.top:
            want.add(row["TeamName"])

print("snapshots: %s" % ", ".join(labels))
print("union of top %d across them: %d distinct teams\n" % (args.top, len(want)))

latest = labels[-1]
found = {}
for idx in sorted(glob.glob("kaggle_episode_data/daily/*_index.csv")):
    day = os.path.basename(idx).replace("_index.csv", "")
    for r in csv.DictReader(io.open(idx, encoding="utf-8-sig")):
        if r["team_a"] in want or r["team_b"] in want:
            p = "kaggle_episode_data/daily/%s/%s.json" % (day, r["episode"])
            if os.path.exists(p):
                found[p] = dict(r, day=day)

per = collections.Counter()
man = []
for p, r in sorted(found.items()):
    for side in ("team_a", "team_b"):
        if r[side] in want:
            per[r[side]] += 1

    def cell(team, key):
        h = history.get(team, {})
        return h.get(key, ("", ""))

    man.append({
        "episode": r["episode"], "day": r["day"],
        "team_a": r["team_a"], "score_a": r["score_a"],
        "rank_a_latest": cell(r["team_a"], latest)[0],
        "team_b": r["team_b"], "score_b": r["score_b"],
        "rank_b_latest": cell(r["team_b"], latest)[0],
        "ranks_a": " ".join("%s=%s" % (l, cell(r["team_a"], l)[0] or "-") for l in labels),
        "ranks_b": " ".join("%s=%s" % (l, cell(r["team_b"], l)[0] or "-") for l in labels),
        "file": "replays/%s.json" % r["episode"],
    })

print("%-6s %-30s %6s   %s" % ("games", "team", "latest", "rank history"))
covered = missing = 0
rows_txt = []
for team in sorted(want, key=lambda t: history[t].get(latest, (10 ** 9,))[0]):
    hist = " ".join("%s=%s" % (l, (history[team].get(l) or ("-",))[0]) for l in labels)
    cur = history[team].get(latest, ("-",))[0]
    line = "%-6d %-30s %6s   %s" % (per[team], team[:30], cur, hist)
    rows_txt.append(line)
    print(line)
    if per[team]:
        covered += 1
    else:
        missing += 1

print("\n%d replays covering %d of %d teams (%d have no replay on disk)"
      % (len(found), covered, len(want), missing))

readme = """# Kaggriculture: replays of recent top-{top} opponents

Union of the top {top} across {nsnap} leaderboard snapshots ({labels}):
{nteams} distinct teams, {nfiles} replays on disk covering {covered} of them.

## Why a union and not just today's top 25

The board churns fast. Between the last two snapshots here, most of the top 25
were new names. Packaging only the newest top 25 would discard replays of teams
that were top 25 two days ago and are still strong, while the new entrants
mostly have no replays collected yet -- so the fresher bundle is the emptier
one. The manifest gives each team's rank in every snapshot so you can tell a
riser from a faller.

## What is in here

    replays/<episode>.json   full episode: 720 steps, both players' complete
                             action streams, market inventory every step
    manifest.csv             episode, both teams, their final scores, their
                             latest rank, and their rank in each snapshot
    leaderboard.csv          the most recent snapshot

## Coverage, honestly

    {coverage}

Teams showing 0 games are not absent because they were skipped. Kaggle offers
no way to query the episode dataset by team, so the only way to find a specific
team's games is to download episodes and look. Teams that climbed into the top
{top} recently have few or no games in the dumps we have scanned.

## Reading these tapes

 -  Hash day 0 only to fingerprint a team's opening. Full-season hashes are
    useless -- our own fixed tape produced 29 distinct full-season hashes over
    91 games, because `_end_of_day` spawns weeds for both farms from the shared
    RNG stream before drawing the shop, so any action change reshuffles the
    economy downstream.
 -  The rank-1 team at the 09-09 snapshot (SpaTaro) played 15 different openings
    in 15 games. The leaders are adaptive, not running a fixed route, which puts
    a shelf life on anything lifted from a single tape.
 -  Reward is final bank balance; ranking is win-based. Coin margin buys nothing.

## What replay-lifting has actually done for us

Once in four attempts. Lifted routes from ReCurSiON, Ryo Hasegawa and Arman
Tuganbaev each lost 0-6 on held-out seeds. A lifted MiMi route went 6/6 on the
seeds it was chosen with, then 8-32 on twenty fresh ones.

A tape contains the actions the donor took. Substituting a crop only works
where those actions already fit the new crop's calendar -- which is why
swapping end-of-season wheat for carrot pays (carrot waters at ages 2-3; the
route lifts wheat at age 3) and the other eight substitutions we tried did not.

Treat these as evidence, not as answers.
""".format(top=args.top, nsnap=len(labels), labels=", ".join(labels),
           nteams=len(want), nfiles=len(found), covered=covered,
           coverage="\n    ".join(["%-6s %-30s %6s   %s"
                                   % ("games", "team", "latest", "rank history")]
                                  + rows_txt))

buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=list(man[0].keys()), lineterminator="\n")
w.writeheader()
w.writerows(man)

raw = sum(os.path.getsize(p) for p in found)
with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for i, (p, r) in enumerate(sorted(found.items()), 1):
        z.write(p, arcname="replays/%s.json" % r["episode"])
        if i % 20 == 0 or i == len(found):
            print("  zipped %d/%d (%s MB)" % (i, len(found),
                  "{:,.0f}".format(os.path.getsize(args.out) / 1048576)), flush=True)
    z.writestr("manifest.csv", buf.getvalue())
    z.writestr("README.md", readme)
    z.write(boards[-1], arcname="leaderboard.csv")

size = os.path.getsize(args.out)
print("\nwrote %s" % args.out)
print("%s MB from %s MB raw (%.0f:1)" % ("{:,.0f}".format(size / 1048576),
      "{:,.0f}".format(raw / 1048576), raw / max(1, size)))
