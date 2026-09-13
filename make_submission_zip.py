"""Package one submission's own live replays, with a manifest, for handoff.

    python make_submission_zip.py --submission 56127567 --out replays-56127567.zip

Unlike make_top25_zip.py, which gathers other teams' games out of the daily
dumps, this packages OUR games: every episode the given submission played. The
manifest records which seat we held, both banks, the result and the opponent's
current leaderboard rank, so the recipient can sort by "lost to a strong team"
without opening a 720-frame JSON.

MIRROR GAMES. A replay carries only team names, never submission ids, so in a
game where both seats are ours there is no way to tell which seat was this
submission. analyze_live_submission.py resolves that by assuming seat 0, which
silently credits half those games to the wrong bot. Here they are labelled M
and excluded from the record instead.
"""
import argparse
import collections
import csv
import glob
import io
import json
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ap = argparse.ArgumentParser()
ap.add_argument("--submission", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--team", default="Harshith revuru")
ap.add_argument("--rating", default="", help="live rating, quoted in the README")
args = ap.parse_args()

SRC = os.path.join("kaggle_episode_data", "replays", args.submission)
paths = sorted(glob.glob(os.path.join(SRC, "*.json")))
if not paths:
    raise SystemExit("no replays under " + SRC)

lb = sorted(glob.glob("kaggle_episode_data/kaggriculture-publicleaderboard-*.csv"))[-1]
rank = {}
for row in csv.DictReader(io.open(lb, encoding="utf-8-sig")):
    rank[row["TeamName"]] = int(row["Rank"])

man = []
wins = losses = ties = mirrors = 0
ours_tot = opps_tot = 0
win_ours = win_opps = loss_ours = loss_opps = 0
skipped = []

for path in paths:
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception as exc:
        skipped.append((os.path.basename(path), str(exc)[:60]))
        continue
    names = d.get("info", {}).get("TeamNames") or ["?", "?"]
    rewards = d.get("rewards") or [0, 0]
    ep = os.path.basename(path)
    for junk in ("episode-", "-replay.json", ".json"):
        ep = ep.replace(junk, "")

    if names[0] == names[1] == args.team:
        mirrors += 1
        man.append({"episode": ep, "seat": "", "result": "M",
                    "our_bank": "", "opp_bank": "", "margin": "",
                    "opponent": args.team, "opp_rank": rank.get(args.team, ""),
                    "file": "replays/%s.json" % ep})
        continue

    seat = 0 if names[0] == args.team else 1
    ours = rewards[seat] or 0
    opps = rewards[1 - seat] or 0
    opp = names[1 - seat]
    result = "W" if ours > opps else ("L" if ours < opps else "T")
    if result == "W":
        wins += 1
        win_ours += ours
        win_opps += opps
    elif result == "L":
        losses += 1
        loss_ours += ours
        loss_opps += opps
    else:
        ties += 1
    ours_tot += ours
    opps_tot += opps
    man.append({"episode": ep, "seat": seat, "result": result,
                "our_bank": int(ours), "opp_bank": int(opps),
                "margin": int(ours - opps), "opponent": opp,
                "opp_rank": rank.get(opp, ""),
                "file": "replays/%s.json" % ep})

rated = wins + losses + ties
man.sort(key=lambda r: (r["margin"] == "", r["margin"]))

fmt = "{:,.0f}".format
print("%d replays: %d rated, %d mirror" % (len(man), rated, mirrors))
print("RECORD  %dW-%dL-%dT   win rate %.1f%%" % (
    wins, losses, ties, 100.0 * wins / max(1, rated)))
print("  our avg %s   opponent avg %s" % (
    fmt(ours_tot / max(1, rated)), fmt(opps_tot / max(1, rated))))
if wins:
    print("  in wins   %s vs %s" % (fmt(win_ours / wins), fmt(win_opps / wins)))
if losses:
    print("  in losses %s vs %s" % (fmt(loss_ours / losses), fmt(loss_opps / losses)))
if skipped:
    print("skipped %d unreadable: %s" % (len(skipped), skipped[:3]))

ranked = sorted((r for r in man if r["opp_rank"] != "" and r["result"] != "M"),
                key=lambda r: r["opp_rank"])
print("\ngames against currently-ranked teams: %d" % len(ranked))
for r in ranked[:20]:
    print("  #%-5s %-28s %s %+10s" % (r["opp_rank"], r["opponent"][:28],
                                      r["result"], fmt(r["margin"])))

BUCKETS = [(1, 50), (51, 200), (201, 500), (501, 1000), (1001, 10 ** 9)]
bucket_lines = []
rated_rows = [r for r in man if r["result"] in ("W", "L")]
for lo, hi in BUCKETS:
    sel = [r for r in rated_rows
           if r["opp_rank"] != "" and lo <= int(r["opp_rank"]) <= hi]
    if not sel:
        continue
    w = sum(r["result"] == "W" for r in sel)
    name = "%d-%d" % (lo, hi) if hi < 10 ** 9 else "%d+" % lo
    bucket_lines.append("    %-12s %4d-%-4d %7.1f%%" % (name, w, len(sel) - w,
                                                        100.0 * w / len(sel)))
unranked = [r for r in rated_rows if r["opp_rank"] == ""]
if unranked:
    w = sum(r["result"] == "W" for r in unranked)
    bucket_lines.append("    %-12s %4d-%-4d %7.1f%%" % (
        "unranked", w, len(unranked) - w, 100.0 * w / len(unranked)))
print("\nwin rate by opponent's CURRENT leaderboard rank")
print("    %-12s %8s %8s" % ("rank", "W-L", "win%"))
print("\n".join(bucket_lines))

losers = collections.Counter(r["opponent"] for r in man if r["result"] == "L")
if losers:
    print("\nlost to (most often first):")
    for name, n in losers.most_common(10):
        rk = rank.get(name, "")
        print("  %-30s %2d  %s" % (name[:30], n, ("#%s" % rk) if rk else "unranked"))

readme = """# Kaggriculture: live replays of submission {sub}

{n} episodes played on the public ladder, both seats, against whatever the
matchmaker paired us with. Leaderboard snapshot: {lb}

    rated games   {rated}   ({wins}W-{losses}L-{ties}T, {pct:.1f}%)
    mirror games  {mirrors}   (both seats ours -- see below)
    our bank      {avg_ours} average
    opponent      {avg_opps} average
    in wins       {wo} vs {wt}
    in losses     {lo} vs {lt}
{rating}
## What is in here

    replays/<episode>.json   full episode: 720 steps, both players' complete
                             action streams, market inventory every step
    manifest.csv             episode, our seat, result, both banks, margin,
                             opponent and their CURRENT leaderboard rank,
                             sorted worst margin first
    leaderboard.csv          the snapshot above

## Where the losses actually are

Win rate split by the opponent's CURRENT leaderboard rank:

    {buckets}

This is the single most useful cut in the bundle. The headline win rate is
carried almost entirely by games against the long tail; against ranked
opposition this agent is behind. Optimising against the average opponent in
this dataset therefore optimises against the wrong opponent -- the games that
decide rating are the ones in the top buckets, and there are far fewer of them.

Two caveats on that table. Ranks are measured today, not on the day the game
was played, so an opponent who has since climbed or fallen is filed under where
they are now. And the top buckets are small, so read the direction, not the
decimal.

## Mirror games are excluded from the record

A replay carries team names, never submission ids. In a game where both seats
belong to us there is no way to tell which seat this submission held, so those
{mirrors} episodes are labelled `M` in the manifest and left out of the record
above. The replays are still included -- they are perfectly good games, just
not attributable. Any tool that assumes seat 0 in a mirror is crediting half of
them to the wrong bot.

## How to read the win rate

Win rate on the ladder is NOT the quality signal. Matchmaking pairs by rating,
so every agent converges toward ~50% as its rating finds its level. The rating
is the signal.

A win rate well above 50% means the agent is still climbing and has not yet met
its equilibrium opponents. It does not mean the agent is that much better than
the field. Conversely, a fresh submission looking "worse" in its first hours is
usually just behind on games played.

## Mechanics worth knowing before optimising against this data

 -  Reward is the final bank balance, but ranking is win-based (Elo live,
    Bradley-Terry after the deadline). Coin margin buys nothing: a +100k
    blowout and a +1 squeaker are the same rating point.
 -  Only the latest 2 submissions are live, and the final standing shows your
    BEST bot, so a weak second slot cannot drag you down.
 -  The market resolves slot-by-slot in lockstep across both players. Same slot
    is an exact tie; one slot earlier takes the solo price. Splitting a product
    across slots is strictly worse than concentrating it.
 -  CARROT, TOMATO and EGG use a `hinge` shape on the scarce side of the price
    curve (u + 8*max(0, u-1)^2), reaching 15x and 11x base in real games. Every
    other product caps near 2x. Two public notebooks transcribe those three as
    log/linear and are wrong on exactly this side of the curve.
 -  Nothing consumes FERTILIZER. No shop buys it and the town centre excludes
    it (`TOWN_CENTER_PRODUCTS = [p for p in PRODUCTS if p != "FERTILIZER"]`).
    Its price only falls, 100 -> 11.
 -  `ongoing` crops are not perennial: reaching max_yield sets a death step.
    Tomato yields 4 units over 4 days, strawberry 4 over 8.
 -  Two consecutive unwatered days produce a WEED.
 -  BUY_PRODUCT is quoted at post-buy inventory, so a buy/sell round trip nets
    zero by design. There is no market arbitrage. Measured: buy 39.2, sell 40.0.
 -  Wheat yields 6 fertilized, 4 unfertilized. One FERTILIZE covers day, day+1
    and day+2 -- exactly wheat's window -- and spends from the worker's own
    inventory, not the shed.
 -  Shed cap is 100 and overflow is destroyed. Step 718 executes, 719 does not.

## The honest caveat about replay-lifting

Reconstructing a strong opponent's route from its recorded tape has worked for
us once in four attempts. Lifted routes from ReCurSiON, Ryo Hasegawa and Arman
Tuganbaev each lost 0-6 on held-out seeds. A lifted MiMi route went 6/6 on the
seeds it was chosen with and then 8-32 on twenty fresh ones.

The reason is mechanical: a tape contains the actions the donor took, and
substituting a different crop only works where those existing actions already
fit the new crop's calendar. That is why swapping end-of-season wheat for
carrot pays -- carrot waters at ages 2-3 and the route lifts wheat at age 3 --
and why the other eight substitutions we tried did not.

Screen any candidate on seeds it was never selected on, both seats, against the
agent it would replace. Selection-set results are a coin flip you get to keep
flipping.

## Benchmark validity, the short version

Replaying recorded opponent tapes detects breakage reliably and cannot rank
comparable agents. Fixed tapes do not react, so what that measures is a bigger
absolute bank against a frozen field -- a different quantity from win
probability against a live one. Trust a large negative there. Do not promote on
a positive without live code-vs-code on fresh seeds, both seats.
""".format(
    sub=args.submission, n=len(man), lb=os.path.basename(lb), rated=rated,
    wins=wins, losses=losses, ties=ties, pct=100.0 * wins / max(1, rated),
    mirrors=mirrors,
    avg_ours=fmt(ours_tot / max(1, rated)), avg_opps=fmt(opps_tot / max(1, rated)),
    wo=fmt(win_ours / max(1, wins)), wt=fmt(win_opps / max(1, wins)),
    lo=fmt(loss_ours / max(1, losses)), lt=fmt(loss_opps / max(1, losses)),
    rating=("    live rating  %s\n" % args.rating) if args.rating else "",
    buckets="\n    ".join(["%-12s %8s %8s" % ("rank", "W-L", "win%")]
                          + [l.strip() for l in bucket_lines]))

buf = io.StringIO()
writer = csv.DictWriter(buf, fieldnames=list(man[0].keys()), lineterminator="\n")
writer.writeheader()
writer.writerows(man)

raw = sum(os.path.getsize(p) for p in paths)
with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for i, r in enumerate(man, 1):
        src = os.path.join(SRC, "episode-%s-replay.json" % r["episode"])
        if not os.path.exists(src):
            src = os.path.join(SRC, "%s.json" % r["episode"])
        z.write(src, arcname=r["file"])
        if i % 25 == 0 or i == len(man):
            print("  %d/%d  archive %s MB" % (
                i, len(man), fmt(os.path.getsize(args.out) / 1048576)), flush=True)
    z.writestr("manifest.csv", buf.getvalue())
    z.writestr("README.md", readme)
    z.write(lb, arcname="leaderboard.csv")

size = os.path.getsize(args.out)
print("\nwrote %s" % args.out)
print("%s MB from %s MB raw (%.0f:1)" % (fmt(size / 1048576), fmt(raw / 1048576),
                                         raw / max(1, size)))
