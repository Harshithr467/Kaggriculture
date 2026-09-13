"""Package replays of the current top-N teams, with a manifest, for handoff.

    python make_top25_zip.py --top 25 --out top25-replays.zip

Writes one zip containing every replay on disk that features a current top-N
team, plus manifest.csv (which team, what rank, who they played, final banks)
and a README explaining what the data is and what it is not.
"""
import argparse, csv, glob, io, json, os, sys, zipfile, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ap = argparse.ArgumentParser()
ap.add_argument("--top", type=int, default=25)
ap.add_argument("--out", default="top25-replays.zip")
args = ap.parse_args()

lb = sorted(glob.glob("kaggle_episode_data/kaggriculture-publicleaderboard-*.csv"))[-1]
rows = list(csv.DictReader(io.open(lb, encoding="utf-8-sig")))
rank = {r["TeamName"]: (int(r["Rank"]), float(r["Score"])) for r in rows}
top = [(int(r["Rank"]), r["TeamName"], float(r["Score"])) for r in rows[:args.top]]
want = {n for _, n, _ in top}

# collect every on-disk replay featuring a wanted team
found = {}                                  # path -> index row
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
    for side, other in (("team_a", "team_b"), ("team_b", "team_a")):
        if r[side] in want:
            per[r[side]] += 1
    man.append({
        "episode": r["episode"], "day": r["day"],
        "team_a": r["team_a"], "rank_a": rank.get(r["team_a"], ("", ""))[0],
        "score_a": r["score_a"],
        "team_b": r["team_b"], "rank_b": rank.get(r["team_b"], ("", ""))[0],
        "score_b": r["score_b"],
        "file": "replays/%s.json" % r["episode"],
    })

print("%-5s %-30s %7s" % ("#", "team", "games"))
missing = []
for rk, name, sc in top:
    print("%-5d %-30s %7d" % (rk, name[:30], per[name]))
    if not per[name]:
        missing.append((rk, name))
print("\n%d replays covering %d of %d teams" % (len(found), sum(1 for _, n, _ in top if per[n]), args.top))

readme = """# Kaggriculture: replays of the current top %d

Leaderboard snapshot: %s
Packaged: %d replays covering %d of the top %d teams.

## What this is

Full official Kaggle episode replays. Each JSON has `info.TeamNames`,
`rewards` (final banks) and `steps`, where every frame carries both players'
observation and the action each submitted. So both sides' complete 720-step
action streams are recoverable, which is what makes a route reconstructable.

`manifest.csv` lists every episode with both teams, their current leaderboard
rank and their final bank.

## What this is not

* Not a full census. Kaggle publishes ~660 episodes a day across 8,400 teams;
  this is a sample of the ones featuring top-ranked teams on the days pulled.
* Not their source. A replay is behaviour in ONE game. Lifting a recorded tape
  and replaying it on new seeds has failed repeatedly -- three of four attempts
  lost outright in our own testing, and the rank-1 route was among the worst.
* Not stable. The top 10 turned over twice in a single day while this was being
  collected. Teams here may not be top-ranked by the time you read it.

## Two findings worth knowing before you dig in

1. Fingerprint teams by hashing DAY 0 ONLY. Full-season action hashes cannot
   distinguish a fixed tape from an adaptive agent, because weed spawns are
   random and any agent with weed repair shifts everything downstream. Our own
   known-fixed route produced 29 distinct full-season hashes over 91 games.

2. SpaTaro, ranked 1, played 15 different openings in 15 games. Every other top
   team we have censused ran exactly one. The leader appears to be genuinely
   adaptive rather than a frozen tape, which would mean route-lifting has a
   shelf life.
""" % (args.top, os.path.basename(lb), len(found),
       sum(1 for _, n, _ in top if per[n]), args.top)

with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for i, (p, r) in enumerate(sorted(found.items()), 1):
        z.write(p, arcname="replays/%s.json" % r["episode"])
        if i % 20 == 0 or i == len(found):
            print("  zipped %d/%d (%.0f MB)" % (i, len(found), os.path.getsize(args.out) / 1e6), flush=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, ["episode", "day", "team_a", "rank_a", "score_a",
                             "team_b", "rank_b", "score_b", "file"])
    w.writeheader()
    for m in man:
        w.writerow(m)
    z.writestr("manifest.csv", buf.getvalue())
    z.writestr("README.md", readme)
    z.write(lb, arcname="leaderboard.csv")

raw = sum(os.path.getsize(p) for p in found)
size = os.path.getsize(args.out)
print("\nwrote %s" % args.out)
print("%.0f MB from %.1f GB raw (%.0f:1)" % (size / 1e6, raw / 1e9, raw / max(size, 1)))
if missing:
    print("\nno replays for %d teams:" % len(missing))
    for rk, n in missing:
        print("   #%-3d %s" % (rk, n))
