"""Pull public episodes and keep only those featuring a current top-N team.

fetch_daily_episodes.py --team filters for ONE team, downloading every episode
and deleting the misses. Chasing eight teams that way means eight full passes.
This does one pass and keeps an episode if either seat is any team we want,
stopping once every team has `--per-team` games.

    python pull_top10.py --dates 2026-09-08 2026-09-09 --top 10 --per-team 10

Episodes are ~31 MB each and most are discarded, so this is bandwidth-heavy by
nature: the dataset gives no way to query by team.
"""
import argparse, collections, csv, glob, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import fetch_daily_episodes as F


def leaderboard_top(n):
    lb = sorted(glob.glob("kaggle_episode_data/kaggriculture-publicleaderboard-*.csv"))[-1]
    rows = list(csv.DictReader(io.open(lb, encoding="utf-8-sig")))
    return [(int(r["Rank"]), r["TeamName"], float(r["Score"])) for r in rows[:n]], os.path.basename(lb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dates", nargs="+", required=True)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--per-team", type=int, default=10)
    ap.add_argument("--sample", type=int, default=400)
    args = ap.parse_args()

    top, lbname = leaderboard_top(args.top)
    want = {name for _, name, _ in top}
    print(f"leaderboard: {lbname}")
    print(f"chasing {len(want)} teams, {args.per_team} games each\n")

    have = collections.defaultdict(set)
    for idx in sorted(glob.glob("kaggle_episode_data/daily/*_index.csv")):
        day = os.path.basename(idx).replace("_index.csv", "")
        for r in csv.DictReader(io.open(idx, encoding="utf-8-sig")):
            for side in ("team_a", "team_b"):
                if r[side] in want:
                    p = f"kaggle_episode_data/daily/{day}/{r['episode']}.json"
                    if os.path.exists(p):
                        have[r[side]].add(p)
    for _, name, _ in top:
        print(f"  {name[:30]:<32}{len(have.get(name, ())):>3} already")

    for date in args.dates:
        need = [n for n in want if len(have.get(n, ())) < args.per_team]
        if not need:
            print("\nall teams satisfied")
            break
        slug = f"kaggle/kaggriculture-episodes-{date}"
        target = os.path.join(F.ROOT, date)
        os.makedirs(target, exist_ok=True)
        index_path = os.path.join(F.ROOT, f"{date}_index.csv")
        index = {}
        if os.path.exists(index_path):
            for row in csv.DictReader(io.open(index_path, encoding="utf-8")):
                index[row["episode"]] = row

        print(f"\n=== {date}: still need {len(need)} teams ===", flush=True)
        names = F.list_files(slug, args.sample)
        print(f"  {len(names)} filenames listed", flush=True)
        kept = 0
        for i, name in enumerate(names, 1):
            episode = name[:-5]
            path = os.path.join(target, name)
            if episode in index and not os.path.exists(path):
                continue                      # seen before, was discarded
            if not os.path.exists(path):
                if not F.fetch(slug, name, target):
                    continue
            got = F.summarise(path)
            if got:
                index[episode] = {"episode": episode, "team_a": got[0],
                                  "score_a": f"{got[1]:.0f}", "team_b": got[2],
                                  "score_b": f"{got[3]:.0f}"}
                hit = [t for t in (got[0], got[2]) if t in want]
                # BUG FIXED: this previously deleted an episode whose teams were
                # already satisfied, which destroyed replays collected on an
                # earlier run. Keep anything featuring a wanted team; only the
                # DOWNLOAD is capped by per_team, never the retention.
                keep = bool(hit)
                if keep:
                    for t in hit:
                        have[t].add(path)
                    kept += 1
                    print(f"  + {episode}  {got[0][:22]} vs {got[2][:22]}", flush=True)
                elif os.path.exists(path):
                    os.remove(path)
            elif os.path.exists(path):
                os.remove(path)
            if i % 25 == 0:
                short = sum(1 for n in want if len(have.get(n, ())) < args.per_team)
                print(f"  {i}/{len(names)} scanned, kept {kept}, {short} teams short", flush=True)
            if all(len(have.get(n, ())) >= args.per_team for n in want):
                print("  all teams satisfied", flush=True)
                break
        with io.open(index_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, ["episode", "team_a", "score_a", "team_b", "score_b"])
            w.writeheader()
            for row in index.values():
                w.writerow(row)

    print(f"\n{'#':<5}{'team':<32}{'games':>7}")
    for rank, name, _ in top:
        print(f"{rank:<5}{name[:31]:<32}{len(have.get(name, ())):>7}")


if __name__ == "__main__":
    main()
