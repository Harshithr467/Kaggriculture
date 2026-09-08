"""Fetch and index episodes from Kaggle's daily public episode datasets.

Kaggle publishes every episode each day as a dataset of ~700 individual JSON
files, ~31 MB each (~21 GB per day). Downloading a whole day is almost entirely
waste, since only a handful of episodes involve any given agent. This pulls a
sample, indexes who played and what they scored, and then lets you fetch more
episodes for specific teams.

    # what teams appear in a day, and how do they score?
    python fetch_daily_episodes.py 2026-08-13 --sample 20

    # having found a team, pull more of its games
    python fetch_daily_episodes.py 2026-08-13 --sample 120 --team "fistyee"

    # just list what is already indexed
    python fetch_daily_episodes.py 2026-08-13 --index-only

Downloaded files land in kaggle_episode_data/daily/<date>/ and the index is
kept in kaggle_episode_data/daily/<date>_index.csv so repeat runs skip work.
"""
import argparse
import collections
import csv
import json
import os
import subprocess
import sys
import zipfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT = os.path.dirname(os.path.abspath(__file__))
KAGGLE = os.path.join(PROJECT, ".venv", "Scripts", "kaggle.exe")
if not os.path.exists(KAGGLE):
    KAGGLE = "kaggle"
ROOT = os.path.join(PROJECT, "kaggle_episode_data", "daily")


def run(args, timeout=900):
    # Team names carry non-ASCII characters and Windows defaults subprocess
    # decoding to cp1252, which raises mid-read and kills the reader thread.
    return subprocess.run([KAGGLE] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def list_files(slug, limit):
    """Episode filenames in the dataset, following pagination."""
    names, token = [], None
    while len(names) < limit:
        args = ["datasets", "files", slug, "--csv"]
        if token:
            args += ["--page-token", token]
        out = run(args).stdout
        rows = [r for r in out.splitlines() if r.strip()]
        token = None
        body = []
        for r in rows:
            if r.startswith("Next Page Token = "):
                token = r.split(" = ", 1)[1].strip()
            else:
                body.append(r)
        got = 0
        for row in csv.DictReader(body):
            name = (row.get("name") or "").strip()
            if name.endswith(".json"):
                names.append(name)
                got += 1
        if not token or not got:
            break
    return names[:limit]


def fetch(slug, name, target):
    path = os.path.join(target, name)
    if os.path.exists(path):
        return path
    res = run(["datasets", "download", "-d", slug, "-f", name, "-p", target, "--force"])
    if os.path.exists(path):
        return path
    z = path + ".zip"
    if os.path.exists(z):
        try:
            with zipfile.ZipFile(z) as zf:
                zf.extractall(target)
            os.remove(z)
        except Exception:
            pass
    if os.path.exists(path):
        return path
    print(f"  ! {name}: {(res.stderr or res.stdout or '')[:120].strip()}")
    return None


def summarise(path):
    """(team_a, score_a, team_b, score_b) or None."""
    try:
        raw = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    steps = raw.get("steps") or []
    if not steps:
        return None
    rewards = [s.get("reward") for s in steps[-1]]
    if any(r is None for r in rewards):
        return None
    names = (raw.get("info", {}) or {}).get("TeamNames") or ["?", "?"]
    return names[0], rewards[0], names[1], rewards[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("date", help="YYYY-MM-DD, must match a manifest row")
    ap.add_argument("--sample", type=int, default=20, help="episodes to consider")
    ap.add_argument("--team", default=None, help="only keep episodes featuring this team")
    ap.add_argument("--index-only", action="store_true")
    args = ap.parse_args()

    slug = f"kaggle/kaggriculture-episodes-{args.date}"
    target = os.path.join(ROOT, args.date)
    os.makedirs(target, exist_ok=True)
    index_path = os.path.join(ROOT, f"{args.date}_index.csv")

    index = {}
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                index[row["episode"]] = row

    if not args.index_only:
        print(f"listing {slug} ...")
        names = list_files(slug, args.sample)
        print(f"  {len(names)} filenames; fetching (~31 MB each, "
              f"~{len(names) * 31 / 1024:.1f} GB if all new)")
        for i, name in enumerate(names, 1):
            episode = name[:-5]
            if episode in index:
                continue
            path = fetch(slug, name, target)
            if not path:
                continue
            got = summarise(path)
            if got:
                index[episode] = {"episode": episode, "team_a": got[0], "score_a": f"{got[1]:.0f}",
                                  "team_b": got[2], "score_b": f"{got[3]:.0f}"}
            if args.team and got and args.team not in (got[0], got[2]):
                os.remove(path)          # not who we wanted; reclaim 31 MB
            if i % 10 == 0:
                print(f"  {i}/{len(names)}")
        with open(index_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, ["episode", "team_a", "score_a", "team_b", "score_b"])
            w.writeheader()
            for row in index.values():
                w.writerow(row)

    print()
    print(f"indexed {len(index)} episodes for {args.date}")
    kept = len([f for f in os.listdir(target) if f.endswith(".json")])
    print(f"{kept} replay files on disk in {target}")

    tally = collections.Counter()
    best = {}
    for row in index.values():
        for team, score in ((row["team_a"], float(row["score_a"])),
                            (row["team_b"], float(row["score_b"]))):
            tally[team] += 1
            best[team] = max(best.get(team, 0), score)
    print()
    print(f"{'team':<32}{'games':>7}{'best score':>12}")
    for team, n in tally.most_common(25):
        print(f"{team[:31]:<32}{n:>7}{best[team]:>12,.0f}")


if __name__ == "__main__":
    main()
