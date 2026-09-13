"""The mechanical half of the daily Kaggriculture check.

    python daily_report.py                 # full run
    python daily_report.py --no-replays    # leaderboard and diffs only, fast

Does the parts that are the same every day and produces a dated markdown
report under reports/. The judgement half -- reading new notebooks, deciding
what to change in the agent -- is for the session that runs this, not for the
script.

WHAT IT REPORTS AND WHY

Overall win rate is deliberately NOT the headline. Matchmaking pairs by rating,
so win rate converges toward 50% for everyone and mostly measures how far up
the ladder you have climbed, not how good the agent is. The number that tracks
the actual goal is the win rate against opponents ranked above us, which is
reported as a bucket table. As of 2026-09-11 that split was 6-16 against the
top 1,000 and 82-36 against everyone below -- the headline 62.9% was almost
entirely the long tail.
"""
import argparse
import collections
import csv
import datetime
import glob
import io
import json
import os
import re
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT)
KAGGLE = os.path.join(PROJECT, ".venv", "Scripts", "kaggle.exe")
if not os.path.exists(KAGGLE):
    KAGGLE = "kaggle"
DATA = os.path.join(PROJECT, "kaggle_episode_data")
COMP = "kaggriculture"
TEAM = "Harshith revuru"
DEADLINE = datetime.date(2026, 9, 30)
BUCKETS = [(1, 10), (11, 25), (26, 100), (101, 500), (501, 1000), (1001, 10 ** 9)]


def kaggle(args, timeout=900):
    # kaggle.exe is itself a Python script printing to a captured pipe; without
    # PYTHONIOENCODING it picks the console's charmap codec, hits the first
    # emoji in a title, and dies mid-output -- silently truncating whatever we
    # were about to parse (bit us on the Code-tab notebook listing).
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([KAGGLE] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout,
                       env=env)
    return p.stdout or ""


def fetch_leaderboard(today):
    """Download the current public leaderboard, return (path, rows)."""
    out = os.path.join(DATA, "kaggriculture-publicleaderboard-%s.csv" % today)
    if not os.path.exists(out):
        kaggle(["competitions", "leaderboard", COMP, "--download", "-p", DATA])
        z = os.path.join(DATA, "%s.zip" % COMP)
        if os.path.exists(z):
            with zipfile.ZipFile(z) as zf:
                # The archived name carries a ':' timestamp, illegal on NTFS.
                io.open(out, "wb").write(zf.read(zf.namelist()[0]))
            os.remove(z)
    rows = list(csv.DictReader(io.open(out, encoding="utf-8-sig")))
    return out, rows


def previous_leaderboard(today):
    paths = sorted(glob.glob(os.path.join(DATA, "kaggriculture-publicleaderboard-*.csv")))
    paths = [p for p in paths if today not in os.path.basename(p)]
    if not paths:
        return None, {}
    rows = list(csv.DictReader(io.open(paths[-1], encoding="utf-8-sig")))
    return paths[-1], {r["TeamName"]: (int(r["Rank"]), float(r["Score"])) for r in rows}


def submissions():
    text = kaggle(["competitions", "submissions", COMP, "--csv"])
    start = text.find("ref,")
    if start < 0:
        return []
    out = []
    for r in csv.DictReader(io.StringIO(text[start:])):
        try:
            score = float(r.get("publicScore") or "nan")
        except ValueError:
            score = float("nan")
        out.append({"ref": r.get("ref"), "file": r.get("fileName"),
                    "date": str(r.get("date"))[:19], "score": score})
    return out


def analyse_replays(ref, rank_of):
    """Download this submission's replays and score them by opponent rank."""
    subprocess.run([sys.executable, "analyze_live_submission.py", ref],
                   capture_output=True, text=True, timeout=7200)
    folder = os.path.join(DATA, "replays", ref)
    paths = sorted(glob.glob(os.path.join(folder, "*.json")))
    rows, mirrors = [], 0
    for path in paths:
        try:
            d = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        names = d.get("info", {}).get("TeamNames") or ["?", "?"]
        rewards = d.get("rewards") or [0, 0]
        if names[0] == names[1] == TEAM:
            mirrors += 1
            continue
        seat = 0 if names[0] == TEAM else 1
        ours, opps = rewards[seat] or 0, rewards[1 - seat] or 0
        opp = names[1 - seat]
        rows.append({"opp": opp, "rank": rank_of.get(opp),
                     "ours": ours, "opps": opps,
                     "res": "W" if ours > opps else ("L" if ours < opps else "T")})
    return rows, mirrors, len(paths)


def bucket_table(rows):
    out = []
    for lo, hi in BUCKETS:
        sel = [r for r in rows if r["rank"] and lo <= r["rank"] <= hi]
        if not sel:
            continue
        w = sum(r["res"] == "W" for r in sel)
        name = "%d-%d" % (lo, hi) if hi < 10 ** 9 else "%d+" % lo
        out.append((name, w, len(sel) - w, 100.0 * w / len(sel)))
    un = [r for r in rows if not r["rank"]]
    if un:
        w = sum(r["res"] == "W" for r in un)
        out.append(("unranked", w, len(un) - w, 100.0 * w / len(un)))
    return out


def new_notebooks(today):
    text = kaggle(["kernels", "list", "--competition", COMP,
                   "--sort-by", "dateRun", "--page-size", "30", "--csv"])
    start = text.find("ref,")
    seen_path = os.path.join(DATA, "seen_kernels.json")
    seen = set()
    if os.path.exists(seen_path):
        seen = set(json.load(io.open(seen_path, encoding="utf-8")))
    fresh, listed = [], []
    if start >= 0:
        for r in csv.DictReader(io.StringIO(text[start:])):
            ref = r.get("ref")
            if not ref:
                continue
            listed.append((ref, r.get("title", "")))
            if ref not in seen:
                fresh.append((ref, r.get("title", "")))
    json.dump(sorted({r for r, _ in listed} | seen),
              io.open(seen_path, "w", encoding="utf-8"))
    return fresh, listed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-replays", action="store_true")
    args = ap.parse_args()

    today = datetime.date.today().isoformat()
    days_left = (DEADLINE - datetime.date.today()).days
    lines = ["# Kaggriculture daily check - %s" % today,
             "",
             "%d days to the 2026-09-30 deadline." % days_left, ""]

    lb_path, rows = fetch_leaderboard(today)
    rank_of = {r["TeamName"]: int(r["Rank"]) for r in rows}
    score_of = {r["TeamName"]: float(r["Score"]) for r in rows}
    prev_path, prev = previous_leaderboard(today)

    ours_rank = rank_of.get(TEAM)
    ours_score = score_of.get(TEAM)
    p = prev.get(TEAM)
    delta = ""
    if p:
        delta = "  (was #%d / %.1f -> %+d places, %+.1f points)" % (
            p[0], p[1], p[0] - ours_rank, ours_score - p[1])
    lines += ["## Where we stand", "",
              "```",
              "rank   #%s of %d" % (ours_rank, len(rows)),
              "score  %.1f%s" % (ours_score, delta),
              "```", ""]

    subs = submissions()
    # The live pair is the two most recent submissions, full stop -- a brand new
    # one is live from the moment it lands even though Kaggle has not scored it
    # yet. Selecting by "has a score" instead would silently treat the freshly
    # retired third submission as live for the first few hours after a submit.
    live = subs[:2]
    rated_live = [s for s in live if s["score"] == s["score"]]
    lines += ["### Live submissions (only the latest 2 are rated; "
              "the final standing counts your best)", "", "```"]
    for s in subs[:4]:
        mark = "  LIVE" if s in live else ""
        score = "%8.1f" % s["score"] if s["score"] == s["score"] else " pending"
        lines.append("%-10s %-18s %-20s %s%s" % (
            s["ref"], s["file"], s["date"], score, mark))
    lines += ["```", ""]

    # ---- leaderboard movement
    for label, n in (("Top 10", 10), ("Top 25", 25)):
        lines += ["## %s" % label, "", "```",
                  "%-5s %-30s %9s  %s" % ("#", "team", "score", "change")]
        for r in rows[:n]:
            name = r["TeamName"]
            was = prev.get(name)
            if was is None:
                note = "NEW to the board" if not prev else "NEW"
            elif was[0] == int(r["Rank"]):
                note = "-"
            else:
                note = "%+d places, %+.1f" % (was[0] - int(r["Rank"]),
                                              float(r["Score"]) - was[1])
            lines.append("%-5s %-30s %9.1f  %s" % (
                r["Rank"], name[:30], float(r["Score"]), note))
        lines += ["```", ""]
        if n == 10:
            continue
        gone = [t for t, (rk, _) in prev.items()
                if rk <= n and rank_of.get(t, 10 ** 9) > n]
        if gone:
            lines += ["Dropped out of the top %d since %s: %s" % (
                n, os.path.basename(prev_path or "?"),
                ", ".join(sorted(gone)[:12])), ""]

    # ---- our agent's live record
    if not args.no_replays and rated_live:
        best = max(rated_live, key=lambda s: s["score"])
        lines += ["## Live record of our best rated submission (%s, %s, %.1f)"
                  % (best["ref"], best["file"], best["score"]), ""]
        rec, mirrors, total = analyse_replays(best["ref"], rank_of)
        w = sum(r["res"] == "W" for r in rec)
        l = sum(r["res"] == "L" for r in rec)
        t = sum(r["res"] == "T" for r in rec)
        n = max(1, len(rec))
        lines += ["```",
                  "replays on disk   %d  (%d rated, %d mirror)" % (total, len(rec), mirrors),
                  "record            %dW-%dL-%dT   %.1f%%" % (w, l, t, 100.0 * w / n),
                  "our avg bank      %s" % format(sum(r["ours"] for r in rec) / n, ",.0f"),
                  "opponent avg      %s" % format(sum(r["opps"] for r in rec) / n, ",.0f"),
                  "```", "",
                  "### The number that actually tracks the goal", "", "```",
                  "%-12s %9s %8s" % ("opp rank", "W-L", "win%")]
        for name, bw, bl, pct in bucket_table(rec):
            lines.append("%-12s %4d-%-4d %7.1f%%" % (name, bw, bl, pct))
        lines += ["```", "",
                  "Beating the long tail is already solved. Progress means moving "
                  "the top buckets.", ""]
        losses = sorted((r for r in rec if r["res"] == "L" and r["rank"]),
                        key=lambda r: r["rank"])[:10]
        if losses:
            lines += ["### Losses to ranked opponents (the ones worth studying)",
                      "", "```"]
            for r in losses:
                lines.append("#%-6s %-28s %9s vs %9s  %+9s" % (
                    r["rank"], r["opp"][:28], format(r["ours"], ",.0f"),
                    format(r["opps"], ",.0f"), format(r["ours"] - r["opps"], ",.0f")))
            lines += ["```", ""]

    # ---- new public work
    fresh, listed = new_notebooks(today)
    lines += ["## Code tab", ""]
    if fresh:
        lines += ["New since the last check:", ""]
        lines += ["- `%s` - %s" % (ref, title) for ref, title in fresh]
    else:
        lines += ["Nothing new since the last check."]
    lines += ["", "Pull anything promising with "
              "`.venv/Scripts/kaggle.exe kernels pull <ref> -p kernels/`.", ""]

    os.makedirs("reports", exist_ok=True)
    out = os.path.join("reports", "daily-%s.md" % today)
    io.open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("\nwrote %s" % out)


if __name__ == "__main__":
    main()
