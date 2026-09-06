"""Build the Kaggriculture methods report as a PDF.

Every number here is measured, and the source of each is named in the table so a
claim can be traced back to the run that produced it. Where an early measurement
was later contradicted, both appear -- the record is more useful than the
flattering version.
"""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "kaggriculture-methods-report.pdf")

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5b6470")
RULE = colors.HexColor("#d6dae0")
BAND = colors.HexColor("#f2f4f7")
GOOD = colors.HexColor("#0f766e")
BAD = colors.HexColor("#b3261e")
WARN = colors.HexColor("#8a5a00")

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Title"], fontName="Helvetica-Bold",
                    fontSize=20, leading=24, textColor=INK, alignment=TA_LEFT,
                    spaceAfter=2)
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontSize=9.5, leading=13,
                     textColor=MUTED, spaceAfter=14)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                    fontSize=12.5, leading=15, textColor=INK,
                    spaceBefore=15, spaceAfter=5)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontSize=9.2, leading=13,
                      textColor=INK, spaceAfter=7)
NOTE = ParagraphStyle("NOTE", parent=BODY, fontSize=8.4, leading=11.5,
                      textColor=MUTED)
CELL = ParagraphStyle("CELL", parent=styles["Normal"], fontSize=8.1, leading=10.4,
                      textColor=INK)
CELLR = ParagraphStyle("CELLR", parent=CELL, alignment=2)
HEAD = ParagraphStyle("HEAD", parent=CELL, fontName="Helvetica-Bold",
                      fontSize=8.1, textColor=colors.white)


def p(text, style=CELL):
    return Paragraph(text, style)


def table(rows, widths, aligns=None, zebra=True):
    data = [[p(c, HEAD) for c in rows[0]]]
    for r in rows[1:]:
        data.append([p(c) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("BOX", (0, 0), (-1, -1), 0.4, RULE),
    ]
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), BAND))
    t.setStyle(TableStyle(style))
    return t


def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title="Kaggriculture: methods tried, what worked, what did not",
        author="Harshith revuru",
    )
    S = []

    S.append(Paragraph("Kaggriculture: what we tried", H1))
    S.append(Paragraph(
        "A complete record of every method attempted, the measured result, and the peak "
        "performance reached. Competition runs 2026-07-29 to 2026-09-30. "
        "Report generated 2026-08-24.", SUB))

    # ---------------------------------------------------------------- peak
    S.append(Paragraph("Highest value achieved", H2))
    S.append(table([
        ["Measure", "Value", "Where"],
        ["<b>Best skill rating</b>", "<b>1747.4</b>",
         "submission 55563850 (lookahead 3), now retired"],
        ["Active ratings", "1698.9 and 1667.1",
         "55677927 and 55657021, both converged"],
        ["Best leaderboard rank", "~#1,069 of 6,046",
         "top 18% of the field"],
        ["<b>Highest single-game bank</b>", "<b>$172,590</b>",
         "vs pwdh2026, won by $99,884"],
        ["Largest winning margin", "$139,539",
         "vs Kaushik, banked $139,660"],
        ["Mean bank across 486 live games", "$90,696", "median $88,774"],
        ["Best live win rate", "54.6%",
         "55563850 over 269 games"],
    ], [46 * mm, 34 * mm, 98 * mm]))
    S.append(Spacer(1, 4))
    S.append(Paragraph(
        "The rating is the real score: the ladder counts only win, loss or tie, and the coin "
        "margin is discarded. A $172,590 bank and a $325 win move the rating identically.",
        NOTE))

    # ---------------------------------------------------------------- worked
    S.append(Paragraph("Methods that worked (all shipped, all re-validated)", H2))
    S.append(Paragraph(
        "Each edge was re-tested by playing the agent against the version of itself without "
        "that edge, live, both seats, on two disjoint blocks of seeds it had never been "
        "screened on. Combined records below.", BODY))
    S.append(table([
        ["Method", "What it does", "Held-out record", "Earlier estimate"],
        ["<b>Preemption lookahead 3</b>",
         "Sells a premium line up to 3 steps before the schedule's own sale",
         "<b>58-2</b>", "31/32, SPRT 7-0-1"],
        ["<b>Eager seller</b>",
         "Sells EGG, CARROT and TOMATO off the real price ladder while a unit still "
         "fetches 0.3x base",
         "<b>43-5</b>", "+51 wins"],
        ["<b>Carrot swap</b>",
         "Grows the 13 end-of-season wheat plantings as carrot instead",
         "<b>40-8</b>", "+12 wins"],
        ["<b>Carrot price gate</b>",
         "At day 26 picks carrot or wheat from the actual market, all 8 shops known",
         "<b>25-11</b>", "+3 wins"],
        ["Weed repair",
         "Substitutes DIG when a weed blocks a scheduled PLANT, then resyncs",
         "inherited", "in all top agents"],
    ], [34 * mm, 66 * mm, 27 * mm, 51 * mm]))
    S.append(Spacer(1, 4))
    S.append(Paragraph(
        "Why these worked and nothing else did: each one <b>adds output or sales using turns "
        "already spent</b>, or substitutes an action the route already performs. The carrot "
        "swap is the clearest case -- carrot waters at ages 2-3 and the route's end-of-season "
        "wheat is lifted at age 3, so carrot fits exactly the hole wheat leaves. It was never "
        "that carrot is a good crop.", NOTE))

    S.append(PageBreak())

    # ---------------------------------------------------------------- failed
    S.append(Paragraph("Methods that did not work", H2))
    S.append(Paragraph("Production and route changes", H2))
    S.append(table([
        ["Method", "Result", "Why it failed"],
        ["Melon patch (extra melon tiles)", "-99 wins",
         "Route carries choreography only for the assets it expects"],
        ["Goose herd swap", "-105 wins",
         "Same; eggs also glut on 2 shops at a $50 base"],
        ["Day-0 cow-for-sheep swap", "-$42k",
         "Ends with 5 empty pastures; PLACE needs a matching structure"],
        ["Pasture retargeting", "-2 wins", "No effect worth the risk"],
        ["<b>Tomato swap</b> (4 donor sets)", "<b>-146 to -190 wins</b>",
         "An <i>ongoing</i> crop yields max_yield units in TOTAL then dies -- "
         "tomato is 4 units at interval 1, worth half a strawberry tile"],
        ["Fertilize wheat, age 2", "-3,335 margin",
         "Two dry days turn a plant to WEED; wheat's window opens at age 2 so "
         "removing that watering kills it"],
        ["Fertilize wheat, age 3", "-96 (neutral)",
         "Arithmetically identical to not fertilizing"],
        ["Fourth quadrant (SE land)", "10-0 loss",
         "Tested by Rayk Kretzschmar over 450 games; we did not repeat it"],
        ["Role specialisation (CMA-ES)", "no effect",
         "Measured, left off; the +$8,399 was an RNG artifact worth $415"],
    ], [46 * mm, 26 * mm, 106 * mm]))

    S.append(Paragraph("Market and timing changes", H2))
    S.append(table([
        ["Method", "Result", "Why it failed"],
        ["Feed-buy ceiling (30 / 20 / 12)", "-44 / -49 / -105 wins",
         "The shed's wheat feeds the herd AND scheduled sales; at 12 the animals starve"],
        ["<b>Sale meter, price floor</b>", "<b>-26 / -32 / -47 wins</b>",
         "A price floor is not a rate limit: admits 32-40 units at equilibrium, "
         "0 once glutted, so it empties the shed early then goes inert"],
        ["<b>Sale meter, town rate cap</b>", "<b>-51 / -64 / -75 wins</b>",
         "Milk, strawberry and wool CLEAR the market. Selling earlier only raises "
         "average inventory, and average inventory sets average price"],
        ["Eager-sell fertilizer", "-151 wins",
         "The route fertilizes 100% of its strawberry from that same shed"],
        ["Eager-sell fertilizer + wheat", "-208 wins",
         "Gives back every win: shed wheat is the feed chain"],
        ["Front-running / SELL reordering", "0 coins available",
         "Both we and rivals already sell in slot ~0.3; the race is a dead heat"],
    ], [46 * mm, 30 * mm, 102 * mm]))

    S.append(Paragraph("Whole-agent replacements", H2))
    S.append(table([
        ["Method", "Result", "Note"],
        ["CMA-ES policy agent", "rating 841-892", "vs 1747 for the route agent"],
        ["Lifted route v15 (iVl44d)", "6/16", "$12k worse than the route it beat"],
        ["Lifted ReCurSiON (#17)", "0/6", "-4,442 a game"],
        ["Lifted Ryo Hasegawa (#1)", "0/6",
         "-6,486. <b>Rank does not predict transplantability</b>"],
        ["Lifted Arman Tuganbaev (#4)", "0/6", "-11,098 a game"],
        ["<b>Lifted MiMi (#5)</b>", "<b>6/6, then 8-32</b>",
         "Won on the 3 seeds it was picked with, lost badly on 20 held-out seeds"],
    ], [46 * mm, 30 * mm, 102 * mm]))

    S.append(PageBreak())

    # ---------------------------------------------------------------- lessons
    S.append(Paragraph("What the failures taught (the transferable part)", H2))
    S.append(table([
        ["Rule", "Evidence"],
        ["<b>Markets that clear cannot be gamed on timing.</b> Milk, strawberry and wool "
         "finish within ~40 units of equilibrium. When supply and absorption are both fixed, "
         "selling earlier only raises average inventory and lowers average price.",
         "Sale meter lost at every rate; turning it on raised mean market inventory and "
         "dropped our bank 84,230 to 79,879 with the opponent's unchanged"],
        ["<b>Selling early is free only where demand is never met.</b> Carrot ends -307, "
         "egg -230, tomato -225. Those are exactly what the eager seller targets.",
         "Eager seller +51 then 43-5; carrot swap 40-8"],
        ["<b>A crop substitution works only where the donor's existing actions fit the new "
         "crop's calendar.</b>",
         "Carrot fits wheat's age-3 lift and pays. Tomato, melon, geese all needed actions "
         "the recording does not contain: 0 for 8"],
        ["<b>An item the farm consumes is not surplus.</b>",
         "Fertilizer sells for 13 and still is not spare; wheat sells and still is the feed"],
        ["<b>Our replay benchmark detects breakage but cannot rank comparable agents.</b>",
         "It scored MiMi's route +24 wins over the incumbent that then beat it 32-8. "
         "Wrong sign, not noise"],
        ["<b>Decide on seeds the candidate has never seen.</b>",
         "MiMi went 6/6 on its screening seeds and 8-32 held out"],
    ], [78 * mm, 100 * mm]))

    # ---------------------------------------------------------------- state
    S.append(Paragraph("Current state", H2))
    S.append(table([
        ["Item", "Value"],
        ["Active submissions", "55677927 (1698.9) and 55657021 (1667.1)"],
        ["Shipped configuration",
         "LOOKAHEAD 3, EAGER_FLOOR_FRAC 0.3, CARROT_SWAP 13 plantings, "
         "CARROT_PRICE_GATE 1.0"],
        ["Disabled and kept as measured negatives",
         "METER_RATE, TOMATO_SWAP, FERTILIZE_WHEAT_AGE, HERD_SWAP, PASTURE_TILT, "
         "MELON_PATCH, FEED_BUY_CEILING"],
        ["Slot correlation",
         "<b>100%</b> -- the two submissions win and lose the identical games, so the "
         "second slot currently provides no hedge"],
        ["Final ranking rule",
         "Only the best-scoring bot is shown, so a weaker second submission cannot "
         "drag the team down"],
        ["Remaining timeline",
         "Final submission 2026-09-30; games continue ~2 weeks; board final ~2026-10-15"],
    ], [46 * mm, 132 * mm]))

    S.append(Spacer(1, 8))
    S.append(Paragraph(
        "Tally: 5 methods shipped and validated, 21 measured and rejected. The rejected work "
        "is the larger half of the record and the more useful one -- four of the six rules "
        "above came from failures, and the benchmark-validity finding came from the single "
        "false positive.", NOTE))

    doc.build(S)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
