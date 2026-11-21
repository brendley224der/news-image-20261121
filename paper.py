"""paper.py -- pure-stdlib drawing kit for a one-page newspaper front page.

Everything here is written fresh for this entry: a tiny RGB canvas, a
hand-made 5x7 bitmap font, simple shape primitives and a deterministic
PNG writer (zlib, fixed settings, no timestamps anywhere).
"""

import struct
import zlib

W, H = 1024, 1024

# Newsprint palette.
PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (176, 30, 30)
DARKRED = (140, 20, 20)
BLUE = (30, 58, 110)
NAVY = (16, 28, 54)
GREY = (96, 92, 82)
LIGHT = (233, 226, 210)
CREAM = (255, 252, 244)
GOLD = (176, 132, 30)


class Canvas:
    """An RGB pixel buffer with a few drawing primitives."""

    def __init__(self, w=W, h=H, bg=PAPER):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        if fill:
            for yy in range(cy - r, cy + r + 1):
                half = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
                self.fill_rect(cx - half, yy, half * 2 + 1, 1, c)
            return
        x = 0
        y = r
        d = 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def png_bytes(self):
        """Encode the canvas as a deterministic PNG."""
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter: none
            raw += self.px[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp)
                + chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
# Uppercase, lowercase, digits and the punctuation the copy needs.
# ---------------------------------------------------------------------------

FONT = {
    'A': ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".###."),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".###."),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': ("....#", ".....", "..###", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': ("..#..", "..#..", ".###.", "..#..", "..#..", "..#..", "...#."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ':': (".....", ".....", ".##..", ".....", ".....", ".##..", "....."),
    ';': (".....", ".....", ".##..", ".....", ".##..", ".##..", "..#.."),
    "'": (".....", "..#..", "..#..", "..#..", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#..##", "#..##"),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '$': ("..#..", ".###.", "#.#..", ".###.", "..#.#", ".###.", "..#.."),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '*': (".....", ".....", "#.#.#", ".###.", "#.#.#", ".....", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

CHAR_W = 5
CHAR_H = 7


def text_width(s, scale):
    """Pixel width of a string at a scale (advance is 6 cells per char)."""
    return len(s) * 6 * scale


def draw_text(cv, x, y, s, scale, color):
    """Draw a string with its top-left corner at (x, y). Unknown chars
    are skipped (drawn as a space)."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is not None:
            for row in range(CHAR_H):
                bits = glyph[row]
                for col in range(CHAR_W):
                    if bits[col] == '#':
                        cv.fill_rect(cx + col * scale, y + row * scale,
                                     scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap_text(s, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    unit = 6 * scale
    words = s.split(' ')
    lines = []
    cur = ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if len(trial) * unit <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, max_width, scale, color, leading=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    if leading is None:
        leading = 7 * scale + 4
    for line in wrap_text(s, max_width, scale):
        draw_text(cv, x, y, line, scale, color)
        y += leading
    return y


# ---------------------------------------------------------------------------
# Small drawn pictures for the story boxes. All coordinates are local to a
# box (x, y, w, h); every shape is built from the primitives above.
# ---------------------------------------------------------------------------

def draw_burst(cv, cx, cy, r, color, color2=None):
    """A starburst: 12 spikes from the centre, with a filled core."""
    for k in range(12):
        ang = k * 30.0
        import math
        rad = ang * math.pi / 180.0
        x1 = cx + int(r * 0.45 * math.cos(rad))
        y1 = cy + int(r * 0.45 * math.sin(rad))
        x2 = cx + int(r * math.cos(rad))
        y2 = cy + int(r * math.sin(rad))
        cv.line(x1, y1, x2, y2, color)
        x3 = cx + int(r * 0.28 * math.cos(rad + 0.26))
        y3 = cy + int(r * 0.28 * math.sin(rad + 0.26))
        cv.line(cx, cy, x3, y3, color)
    cv.circle(cx, cy, max(3, r // 4), color, fill=True)
    if color2 is not None:
        cv.circle(cx, cy, max(2, r // 7), color2, fill=True)


def draw_chart(cv, x, y, w, h, color, up=False):
    """A tiny line chart inside a box: axes plus a jagged line."""
    cv.rect(x, y, w, h, GREY, 1)
    cv.line(x + 6, y + h - 8, x + w - 6, y + h - 8, GREY)
    cv.line(x + 6, y + 6, x + 6, y + h - 8, GREY)
    n = 7
    pts = []
    for i in range(n):
        px = x + 8 + (w - 20) * i // (n - 1)
        if up:
            py = y + h - 12 - (h - 24) * i // (n - 1)
        else:
            py = y + 10 + (h - 24) * i // (n - 1)
        # jagged steps so the line is not a straight diagonal
        jog = ((i * 37) % 7) - 3
        pts.append((px, py + jog))
    for i in range(n - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color)
        cv.line(pts[i][0], pts[i][1] + 1, pts[i + 1][0], pts[i + 1][1] + 1, color)
    for px, py in pts:
        cv.circle(px, py, 2, color, fill=True)


def draw_spiral(cv, cx, cy, r, color):
    """A cyclone: concentric broken rings around a calm eye."""
    for k in range(5):
        rr = r - k * (r // 5)
        if rr < 4:
            break
        # draw most of each ring, leaving a gap that rotates per ring
        gap = k * 55
        for deg in range(360):
            if (deg - gap) % 360 < 55:
                continue
            import math
            rad = deg * math.pi / 180.0
            cv.set(cx + int(rr * math.cos(rad)),
                   cy + int(rr * math.sin(rad)), color)
    cv.circle(cx, cy, max(3, r // 6), PAPER, fill=True)
    cv.circle(cx, cy, max(2, r // 9), color, fill=True)


def draw_capsule(cv, x, y, w, h, c1, c2):
    """A pill capsule lying flat: two half-capsules, two colours."""
    r = h // 2
    cv.circle(x + r, y + r, r, c1, fill=True)
    cv.circle(x + w - r, y + r, r, c2, fill=True)
    cv.fill_rect(x + r, y, w - 2 * r, h, c1)
    cv.fill_rect(x + w // 2, y, w // 2 - r, h, c2)
    cv.circle(x + r, y + r, r, INK)
    cv.circle(x + w - r, y + r, r, INK)
    cv.hline(x + r, y, w - 2 * r, INK)
    cv.hline(x + r, y + h - 1, w - 2 * r, INK)


def draw_flags(cv, x, y, w, h):
    """Three small flags side by side: US, China, Russia."""
    fw = w // 3 - 6
    fh = h
    # US: red/white stripes with a blue corner
    fx = x
    for s in range(7):
        c = RED if s % 2 == 0 else CREAM
        cv.fill_rect(fx, y + fh * s // 7, fw, fh // 7 + 1, c)
    cv.fill_rect(fx, y, fw // 2, fh // 2, BLUE)
    cv.rect(fx, y, fw, fh, INK, 1)
    # China: red field, gold stars
    fx = x + w // 3 + 3
    cv.fill_rect(fx, y, fw, fh, RED)
    cv.circle(fx + fw // 4, y + fh // 4, 4, GOLD, fill=True)
    cv.circle(fx + fw // 2, y + fh // 5, 2, GOLD, fill=True)
    cv.circle(fx + fw // 2 + 6, y + fh // 3, 2, GOLD, fill=True)
    cv.rect(fx, y, fw, fh, INK, 1)
    # Russia: white / blue / red tricolour
    fx = x + 2 * (w // 3 + 3)
    cv.fill_rect(fx, y, fw, fh // 3, CREAM)
    cv.fill_rect(fx, y + fh // 3, fw, fh // 3, BLUE)
    cv.fill_rect(fx, y + 2 * fh // 3, fw, fh - 2 * fh // 3, RED)
    cv.rect(fx, y, fw, fh, INK, 1)


def draw_stamp(cv, x, y, w, h, word, color=RED):
    """A rubber-stamp box with a word in it."""
    cv.rect(x, y, w, h, color, 2)
    cv.rect(x + 3, y + 3, w - 6, h - 6, color, 1)
    tw = text_width(word, 2)
    draw_text(cv, x + (w - tw) // 2, y + (h - 14) // 2, word, 2, color)
