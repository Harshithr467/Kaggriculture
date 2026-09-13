"""Download exactly the episodes the index already says feature teams we want.

pull_top10.py scans a day's dataset blind, downloading ~31 MB per episode and
discarding most. But once a day has been indexed, we already know which episode
IDs feature which teams -- so we can fetch only those and waste nothing.

    python fetch_by_index.py --top 25 --per-team 10

Retention is never capped: an episode featuring a wanted team is always kept.
Capping retention by a quota is what deleted a previous run's collection.
"""
import argparse, collections, csv, glob, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import fetch_daily_episodes as F

ap = argparse.ArgumentParser()
ap.add_argument("--top", type=int, default=25)
ap.add_argument("--per-team", type=int, default=10)
args = ap.parse_args()

lb = sorted(glob.glob("kaggle_episode_data/kaggriculture-publicleaderboard-*.csv"))[-1]
rows = list(csv.DictReader(io.open(lb, encoding="utf-8-sig")))
top = [(int(r["Rank"]), r["TeamName"]) for r in rows[:args.top]]
want = {n for _, n in top}
print("leaderboard:", os.path.basename(lb), "| chasing top", args.top)

# episode -> (day, teams) from every index we have
cand = collections.defaultdict(list)          # team -> [(day, episode)]
ondisk = collections.defaultdict(set)
for idx in sorted(glob.glob("kaggle_episode_data/daily/*_index.csv")):
    day = os.path.basename(idx).replace("_index.csv", "")
    for r in csv.DictReader(io.open(idx, encoding="utf-8-sig")):
        for side in ("team_a", "team_b"):
            t = r[side]
            if t in want:
                p = "kaggle_episode_data/daily/%s/%s.json" % (day, r["episode"])
                if os.path.exists(p):
                    ondisk[t].add(p)
                else:
                    cand[t].append((day, r["episode"]))

todo = []
for _, name in top:
    need = args.per_team - len(ondisk[name])
    for day, ep in cand[name][:max(0, need)]:
        todo.append((day, ep, name))
# dedupe: one episode can serve two teams
seen = set(); jobs = []
for day, ep, name in todo:
    if (day, ep) in seen:
        continue
    seen.add((day, ep)); jobs.append((day, ep, name))

print("already on disk: %d episodes" % sum(len(v) for v in ondisk.values()))
print("to download    : %d episodes (~%.1f GB)\n" % (len(jobs), len(jobs) * 31 / 1024))

ok = 0
for i, (day, ep, name) in enumerate(jobs, 1):
    slug = "kaggle/kaggriculture-episodes-%s" % day
    target = os.path.join(F.ROOT, day)
    os.makedirs(target, exist_ok=True)
    if F.fetch(slug, "%s.json" % ep, target):
        ok += 1
    if i % 10 == 0 or i == len(jobs):
        print("  %d/%d fetched (%d ok)" % (i, len(jobs), ok), flush=True)

print()
print("%-5s %-30s %7s" % ("#", "team", "games"))
total = 0
for rank, name in top:
    n = 0
    for idx in sorted(glob.glob("kaggle_episode_data/daily/*_index.csv")):
        day = os.path.basename(idx).replace("_index.csv", "")
        for r in csv.DictReader(io.open(idx, encoding="utf-8-sig")):
            if name in (r["team_a"], r["team_b"]):
                if os.path.exists("kaggle_episode_data/daily/%s/%s.json" % (day, r["episode"])):
                    n += 1
    total += n
    print("%-5d %-30s %7d" % (rank, name[:30], n))
print("\ntotal replays for the top %d: %d" % (args.top, total))
