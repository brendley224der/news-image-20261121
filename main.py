"""main.py -- The World Today: Saturday 21 November 2026 in one image.

Renders a 1024x1024 newspaper front page (pure Python standard library)
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
Deterministic: fixed copy, no clock, no randomness, so two runs are
byte-identical.
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from paper import (Canvas, draw_text, draw_text_centered, draw_para,
                   draw_burst, draw_chart, draw_spiral, draw_capsule,
                   draw_flags, draw_stamp, text_width,
                   PAPER, INK, RED, BLUE, NAVY, GREY, LIGHT, CREAM, GOLD)

MARGIN = 36
RIGHT = 1024 - MARGIN


def masthead(cv):
    cv.hline(MARGIN, 20, RIGHT - MARGIN, INK, 3)
    draw_text_centered(cv, 512, 32, "THE WORLD TODAY", 7, INK)
    cv.hline(MARGIN, 88, RIGHT - MARGIN, INK, 1)
    draw_text_centered(cv, 512, 96, "SATURDAY, 21 NOVEMBER 2026", 3, INK)
    draw_text(cv, MARGIN, 96, "VOL. 1 - NO. 21", 2, GREY)
    tag = "PRICE: FREE"
    draw_text(cv, RIGHT - text_width(tag, 2), 96, tag, 2, GREY)
    cv.hline(MARGIN, 122, RIGHT - MARGIN, INK, 3)


def lead_art(cv, x, y, w, h):
    """Night sky over south-eastern Poland: a missile arc, bursts,
    and the ground below."""
    cv.fill_rect(x, y, w, h, NAVY)
    # stars
    for sx, sy in ((18, 14), (52, 30), (96, 10), (150, 26), (210, 12),
                   (268, 34), (320, 16), (120, 44), (240, 48), (300, 60)):
        cv.set(x + sx, y + sy, CREAM)
        cv.set(x + sx + 1, y + sy, CREAM)
    # missile trail arcing down from top right
    cv.line(x + w - 20, y + 8, x + w - 90, y + 62, CREAM)
    cv.line(x + w - 20, y + 9, x + w - 90, y + 63, CREAM)
    cv.line(x + w - 90, y + 62, x + w - 150, y + 96, CREAM)
    # bursts where the missiles came down
    draw_burst(cv, x + w - 150, y + 96, 34, (255, 120, 40), (255, 220, 90))
    draw_burst(cv, x + 70, y + 110, 20, (255, 120, 40), (255, 220, 90))
    # ground: dark hills and a few rooftops
    cv.fill_rect(x, y + h - 34, w, 34, (10, 18, 38))
    for gx, gy, gw in ((30, 0, 46), (110, 8, 38), (200, 2, 52), (290, 10, 40)):
        cv.fill_rect(x + gx, y + h - 34 - gy, gw, 34 + gy - 6, (10, 18, 38))
        cv.line(x + gx, y + h - 34 - gy, x + gx + gw // 2,
                y + h - 44 - gy, (10, 18, 38))
        cv.line(x + gx + gw // 2, y + h - 44 - gy, x + gx + gw,
                y + h - 34 - gy, (10, 18, 38))
    # caption strip
    cv.fill_rect(x, y + h - 16, w, 16, INK)
    draw_text(cv, x + 8, y + h - 14, "POLAND, FRIDAY NIGHT", 1, CREAM)


def lead(cv):
    y = 140
    draw_text(cv, MARGIN, y, "NATO CALLS IT A GRAVE VIOLATION", 2, RED)
    draw_text(cv, MARGIN, y + 22, "RUSSIAN MISSILES", 6, INK)
    draw_text(cv, MARGIN, y + 66, "LAND IN POLAND", 6, INK)
    lead_art(cv, 648, y + 4, 340, 176)
    body = ("POLAND - Two Russian cruise missiles and a suspected drone "
            "crashed in south-eastern Poland during a huge overnight "
            "attack on Ukraine that killed eight people. Prime Minister "
            "Donald Tusk called it a deliberate provocation. NATO said "
            "it was a grave violation of Polish airspace.")
    draw_para(cv, MARGIN, y + 118, body, 596, 2, INK)
    cap = ("Missiles came down near Nowy Lipowiec and Rudnik nad Sanem, "
           "close to allied war games.")
    draw_para(cv, 648, y + 188, cap, 340, 2, GREY)
    cv.hline(MARGIN, 405, RIGHT - MARGIN, INK, 2)


def column(cv, x, y, w, kicker, head1, head2, body, art):
    draw_text(cv, x, y, kicker, 2, RED)
    draw_text(cv, x, y + 20, head1, 3, INK)
    draw_text(cv, x, y + 43, head2, 3, INK)
    art(cv, x, y + 70, w, 62)
    draw_para(cv, x, y + 142, body, w, 2, INK, leading=17)


def three_columns(cv):
    y = 423
    col_w = 300
    xs = (MARGIN, MARGIN + 326, MARGIN + 652)
    column(cv, xs[0], y, col_w, "MARKETS",
           "WALL STREET", "SLUMPS",
           "US shares fell about 3.7% on Friday as AI and chip stocks "
           "sold off. The Dow entered correction territory. The Nasdaq "
           "lost more than 5%.",
           lambda c, x, yy, w, h: draw_chart(c, x, yy, w, h, RED))
    column(cv, xs[1], y, col_w, "EUROPE",
           "DENMARK EXPELS", "RUSSIAN ATTACHE",
           "Denmark expelled Russia's defence attache after its security "
           "service said Moscow plotted to kill rapper Kyivstoner near "
           "Copenhagen.",
           lambda c, x, yy, w, h: draw_stamp(c, x + 40, yy + 8, w - 80,
                                             h - 16, "EXPELLED"))
    column(cv, xs[2], y, col_w, "WEATHER",
           "CYCLONE AKVAN", "HITS ODISHA",
           "Cyclone Akvan crossed the Odisha coast near Gopalpur on "
           "Friday. More than 300,000 people were moved to 9,341 "
           "shelters. No major damage was reported.",
           lambda c, x, yy, w, h: draw_spiral(c, x + w // 2, yy + h // 2,
                                              28, BLUE))
    for gx in (MARGIN + 313, MARGIN + 639):
        cv.vline(gx, y, 254, LIGHT, 1)
    cv.hline(MARGIN, 685, RIGHT - MARGIN, INK, 2)


def two_columns(cv):
    y = 701
    # summit: headline, body on the left, three flags on the right
    draw_text(cv, MARGIN, y, "DIPLOMACY", 2, RED)
    draw_text(cv, MARGIN, y + 20, "TRUMP, XI AND PUTIN MEET", 3, INK)
    draw_para(cv, MARGIN, y + 46,
              "The first three-way summit in Shenzhen ended with a joint "
              "declaration, but few concrete results.",
              300, 2, INK, leading=17)
    draw_flags(cv, 352, y + 46, 148, 56)
    cv.vline(512, y, 142, LIGHT, 1)
    # pill: headline, body on the left, a capsule on the right
    draw_text(cv, 536, y, "HEALTH", 2, RED)
    draw_text(cv, 536, y + 20, "PILL HAILED AS CANCER", 3, INK)
    draw_text(cv, 536, y + 43, "BREAKTHROUGH", 3, INK)
    draw_para(cv, 536, y + 69,
              "A trial of the pill daraxonrasib found tumours stopped "
              "growing in nearly all patients.",
              300, 2, INK, leading=17)
    draw_capsule(cv, 852, y + 72, 120, 34, RED, CREAM)
    cv.hline(MARGIN, 860, RIGHT - MARGIN, INK, 2)


def also_today(cv):
    y = 874
    draw_text(cv, MARGIN, y, "ALSO TODAY", 2, RED)
    items = ("World Court: Myanmar committed genocide. UK and EU sign "
             "food, carbon and youth deals. Houthi missiles intercepted "
             "over Riyadh. India 159 for 1 vs New Zealand. Police "
             "sentenced over Zecler beating. 2027 Elantra unveiled.")
    draw_para(cv, MARGIN, y + 18, items, RIGHT - MARGIN, 2, INK)
    cv.hline(MARGIN, 960, RIGHT - MARGIN, INK, 1)
    draw_text_centered(cv, 512, 966,
                       "THE WORLD TODAY - SATURDAY 21 NOVEMBER 2026 - PAGE 1",
                       1, GREY)


def render():
    cv = Canvas()
    masthead(cv)
    lead(cv)
    three_columns(cv)
    two_columns(cv)
    also_today(cv)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = render().png_bytes()
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, sha256 %s)"
          % (path, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
