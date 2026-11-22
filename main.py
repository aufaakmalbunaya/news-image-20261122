#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE -- Sunday 22 November 2026.

A single-file, standard-library-only program that draws a dense newspaper
front page summing up the world's news of Sunday 22 November 2026 and
writes it as a 1024x1024 PNG.

Everything is drawn by hand: a small pixel-letter alphabet, flat filled
shapes, a dotted sketch map, and a PNG writer built from zlib and struct.
No third-party packages, no network, no clock, no randomness, so two runs
always produce the same bytes.

Run:  python3 main.py
Output: $MAKEFUN_OUTPUT_DIR/entry.png, or /output/entry.png when unset.
"""

import os
import struct
import zlib

PAGE_W = 1024
PAGE_H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 241, 227)   # warm off-white page
INK = (26, 23, 18)        # near-black ink
RED = (178, 34, 28)       # headline red
NAVY = (31, 58, 95)       # deep navy
TEAL = (14, 110, 110)     # teal
GOLD = (198, 138, 28)     # gold
GREEN = (46, 125, 62)     # green
SKY = (146, 196, 222)     # pale sky blue
NIGHT = (18, 28, 58)      # night sky
DUSK = (232, 178, 90)     # dusk orange
GREY = (120, 116, 108)    # mid grey
LIGHT_GREY = (210, 204, 190)
CREAM = (250, 244, 222)

# ------------------------------------------------------- pixel letterforms
# Each letter is 7 rows of 5 dots. '#' is ink, '.' is empty. I drew every
# shape below by hand on this 5-by-7 grid.
GLYPHS = {
    "A": ("..#..",
          ".#.#.",
          "#...#",
          "#...#",
          "#####",
          "#...#",
          "#...#"),
    "B": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#...#",
          "#...#",
          "####."),
    "C": (".####",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          ".####"),
    "D": ("####.",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "####."),
    "E": ("#####",
          "#....",
          "#....",
          "####.",
          "#....",
          "#....",
          "#####"),
    "F": ("#####",
          "#....",
          "#....",
          "####.",
          "#....",
          "#....",
          "#...."),
    "G": (".####",
          "#....",
          "#....",
          "#.###",
          "#...#",
          "#...#",
          ".###."),
    "H": ("#...#",
          "#...#",
          "#...#",
          "#####",
          "#...#",
          "#...#",
          "#...#"),
    "I": (".###.",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "J": ("..###",
          "...#.",
          "...#.",
          "...#.",
          "...#.",
          "#..#.",
          ".##.."),
    "K": ("#...#",
          "#..#.",
          "#.#..",
          "##...",
          "#.#..",
          "#..#.",
          "#...#"),
    "L": ("#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#####"),
    "M": ("#...#",
          "##.##",
          "#.#.#",
          "#.#.#",
          "#...#",
          "#...#",
          "#...#"),
    "N": ("#...#",
          "##..#",
          "#.#.#",
          "#..##",
          "#...#",
          "#...#",
          "#...#"),
    "O": (".###.",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "P": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#....",
          "#....",
          "#...."),
    "Q": (".###.",
          "#...#",
          "#...#",
          "#...#",
          "#.#.#",
          "#..#.",
          ".##.#"),
    "R": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#.#..",
          "#..#.",
          "#...#"),
    "S": (".####",
          "#....",
          "#....",
          ".###.",
          "....#",
          "....#",
          "####."),
    "T": ("#####",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#.."),
    "U": ("#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "V": ("#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".#.#.",
          "..#.."),
    "W": ("#...#",
          "#...#",
          "#...#",
          "#.#.#",
          "#.#.#",
          "##.##",
          "#...#"),
    "X": ("#...#",
          "#...#",
          ".#.#.",
          "..#..",
          ".#.#.",
          "#...#",
          "#...#"),
    "Y": ("#...#",
          "#...#",
          ".#.#.",
          "..#..",
          "..#..",
          "..#..",
          "..#.."),
    "Z": ("#####",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#....",
          "#####"),
}

DIGITS = {
    "0": (".###.",
          "#...#",
          "#..##",
          "#.#.#",
          "##..#",
          "#...#",
          ".###."),
    "1": ("..#..",
          ".##..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "2": (".###.",
          "#...#",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#####"),
    "3": ("####.",
          "....#",
          "....#",
          ".###.",
          "....#",
          "....#",
          "####."),
    "4": ("...#.",
          "..##.",
          ".#.#.",
          "#..#.",
          "#####",
          "...#.",
          "...#."),
    "5": ("#####",
          "#....",
          "####.",
          "....#",
          "....#",
          "#...#",
          ".###."),
    "6": (".###.",
          "#....",
          "#....",
          "####.",
          "#...#",
          "#...#",
          ".###."),
    "7": ("#####",
          "....#",
          "...#.",
          "...#.",
          "..#..",
          "..#..",
          "..#.."),
    "8": (".###.",
          "#...#",
          "#...#",
          ".###.",
          "#...#",
          "#...#",
          ".###."),
    "9": (".###.",
          "#...#",
          "#...#",
          ".####",
          "....#",
          "....#",
          ".###."),
}

MARKS = {
    " ": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".....",
          "....."),
    ".": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".##..",
          ".##.."),
    ",": (".....",
          ".....",
          ".....",
          ".....",
          ".##..",
          ".##..",
          ".#..."),
    ":": (".....",
          ".##..",
          ".##..",
          ".....",
          ".##..",
          ".##..",
          "....."),
    ";": (".....",
          ".##..",
          ".##..",
          ".....",
          ".##..",
          ".##..",
          ".#..."),
    "-": (".....",
          ".....",
          ".....",
          "#####",
          ".....",
          ".....",
          "....."),
    "$": ("..#..",
          ".####",
          "#.#.#",
          ".###.",
          "..#.#",
          "####.",
          "..#.."),
    "%": ("##..#",
          "##.#.",
          "...#.",
          "..#..",
          ".#...",
          "#.#.#",
          "#..##"),
    "'": ("..#..",
          "..#..",
          ".#...",
          ".....",
          ".....",
          ".....",
          "....."),
    "/": ("....#",
          "...#.",
          "...#.",
          "..#..",
          ".#...",
          ".#...",
          "#...."),
    "(": ("...##",
          "..#..",
          ".#...",
          ".#...",
          ".#...",
          "..#..",
          "...##"),
    ")": ("##...",
          "..#..",
          "...#.",
          "...#.",
          "...#.",
          "..#..",
          "##..."),
    "&": (".###.",
          "#...#",
          "#...#",
          ".##..",
          "#.#.#",
          "#..#.",
          ".##.#"),
    "+": (".....",
          "..#..",
          "..#..",
          "#####",
          "..#..",
          "..#..",
          "....."),
    "!": ("..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".....",
          "..#.."),
    "?": (".###.",
          "#...#",
          "....#",
          "...#.",
          "..#..",
          ".....",
          "..#.."),
    "=": (".....",
          ".....",
          "#####",
          ".....",
          "#####",
          ".....",
          "....."),
}

GLYPHS.update(DIGITS)
GLYPHS.update(MARKS)


def glyph_of(ch):
    """Return the 7-row pattern for a character, blank when unknown."""
    return GLYPHS.get(ch, MARKS[" "])


# ------------------------------------------------------------------- canvas
class Sheet:
    """A plain RGB pixel buffer with small drawing helpers."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.px = bytearray(background * (width * height))

    def dot(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = colour[0]
            self.px[i + 1] = colour[1]
            self.px[i + 2] = colour[2]

    def block(self, x, y, w, h, colour):
        """Fill a rectangle, clipped to the page."""
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = colour[0]
                self.px[i + 1] = colour[1]
                self.px[i + 2] = colour[2]

    def frame(self, x, y, w, h, colour, thick=1):
        self.block(x, y, w, thick, colour)
        self.block(x, y + h - thick, w, thick, colour)
        self.block(x, y, thick, h, colour)
        self.block(x + w - thick, y, thick, h, colour)

    def hline(self, x, y, w, colour, thick=1):
        self.block(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.block(x, y, thick, h, colour)

    def disc(self, cx, cy, r, colour):
        """A filled circle, drawn row by row."""
        for dy in range(-r, r + 1):
            span = int((r * r - dy * dy) ** 0.5)
            self.block(cx - span, cy + dy, span * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=2):
        for dy in range(-r, r + 1):
            span = int((r * r - dy * dy) ** 0.5)
            inner = int(max(0, (r - thick) ** 2 - dy * dy) ** 0.5) \
                if abs(dy) < r - thick else 0
            self.block(cx - span, cy + dy, span - inner, 1, colour)
            self.block(cx + inner + 1, cy + dy, span - inner, 1, colour)

    def triangle(self, x0, y0, x1, y1, x2, y2, colour):
        """A filled triangle, scanned one row at a time."""
        top = min(y0, y1, y2)
        bottom = max(y0, y1, y2)
        for yy in range(top, bottom + 1):
            cuts = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1),
                                     (x1, y1, x2, y2),
                                     (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    t = (yy - ay) / (by - ay)
                    cuts.append(ax + t * (bx - ax))
            if len(cuts) >= 2:
                left = int(min(cuts))
                right = int(max(cuts))
                self.block(left, yy, right - left + 1, 1, colour)

    # ------------------------------------------------------------ lettering
    def char(self, x, y, ch, scale, colour):
        rows = glyph_of(ch)
        for r in range(7):
            for c in range(5):
                if rows[r][c] == "#":
                    self.block(x + c * scale, y + r * scale,
                               scale, scale, colour)

    def text(self, x, y, s, scale, colour):
        """Draw a string; return the x where it ends."""
        cx = x
        for ch in s:
            self.char(cx, y, ch, scale, colour)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def text_centred(self, cx, y, s, scale, colour):
        w = self.text_width(s, scale)
        self.text(cx - w // 2, y, s, scale, colour)
        return w

    def wrap(self, s, max_w, scale):
        """Split a string into lines that fit max_w pixels at scale."""
        limit = max(1, max_w // (6 * scale))
        words = s.split(" ")
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if len(trial) <= limit:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, x, y, s, max_w, scale, colour, leading=None):
        """Draw wrapped text; return the y just below the last line."""
        step = (leading if leading is not None else 9 * scale)
        yy = y
        for line in self.wrap(s, max_w, scale):
            self.text(x, yy, line, scale, colour)
            yy += step
        return yy


# ---------------------------------------------------------------- PNG writer
def _chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload +
            struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def encode_png(sheet):
    """Pack the pixel buffer as a plain PNG: header, image data, end."""
    header = struct.pack(">IIBBBBB", sheet.w, sheet.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = sheet.w * 3
    for yy in range(sheet.h):
        raw.append(0)  # no filter on any scanline
        raw += sheet.px[yy * stride:(yy + 1) * stride]
    body = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) +
            _chunk(b"IDAT", body) + _chunk(b"IEND", b""))


# ===================================================================== data
# Every story carries the region and the field it belongs to. The two
# "day in numbers" panels are counted from this list at run time, so the
# bars can never disagree with the page.
# Regions: EUROPE, N. AMERICA, MIDDLE EAST, ASIA, AFRICA, S. AMERICA,
#          OCEANIA, WORLD. Fields: WAR + DIPLOMACY, MARKETS, SPORT,
#          TECH + SCIENCE, SOCIETY, CLIMATE + ENERGY.
STORIES = [
    # -- heroes (3)
    ("GULF IN FLAMES", "MIDDLE EAST", "WAR + DIPLOMACY"),
    ("EL CHAPO ISIDRO SEIZED", "N. AMERICA", "WAR + DIPLOMACY"),
    ("PERU QUAKE 6.9", "S. AMERICA", "SOCIETY"),
    # -- illustrated leads (12)
    ("DRONES HIT RUSSIAN SHIP", "EUROPE", "WAR + DIPLOMACY"),
    ("MISSILES HIT KRYVYI RIH", "EUROPE", "WAR + DIPLOMACY"),
    ("ESTONIA TO SHUT BORDER", "EUROPE", "WAR + DIPLOMACY"),
    ("TRUMP LANDS IN SHENZHEN", "ASIA", "WAR + DIPLOMACY"),
    ("EISENKOT CALLS LIKUD TALKS", "MIDDLE EAST", "WAR + DIPLOMACY"),
    ("BOLSONARO IN ICU", "S. AMERICA", "SOCIETY"),
    ("COP31 TALKS STALL", "WORLD", "CLIMATE + ENERGY"),
    ("FRENCH PROTESTS SHRINK", "EUROPE", "SOCIETY"),
    ("ENGLAND THRASH ALL BLACKS", "EUROPE", "SPORT"),
    ("FRANCE BEAT ARGENTINA", "EUROPE", "SPORT"),
    ("AUSSIES WIN FIRST T20", "OCEANIA", "SPORT"),
    ("VERSTAPPEN TAKES VEGAS POLE", "N. AMERICA", "SPORT"),
    # -- briefs (31)
    ("EU BUDGET PLAN $224B BELOW COMMISSION", "EUROPE", "MARKETS"),
    ("US LIMITS MILITARY CONTACT WITH CANADA", "N. AMERICA", "WAR + DIPLOMACY"),
    ("CHINA TO BAR YOUNG RED-CHIP FIRMS ABROAD", "ASIA", "MARKETS"),
    ("CRUDE OIL FUTURES FALL MORE THAN 3%", "EUROPE", "MARKETS"),
    ("MODI OPENS NITISH SETU BRIDGE IN BIHAR", "ASIA", "SOCIETY"),
    ("CYCLONE AKVAN: 14 FLIGHTS CUT AT RANCHI", "ASIA", "SOCIETY"),
    ("11 DIE FROM TAINTED ALCOHOL IN MANIPUR", "ASIA", "SOCIETY"),
    ("FBI DATABASE BREACH RAISES ALARM", "N. AMERICA", "TECH + SCIENCE"),
    ("BAHRAIN PROBES PATRIOT MISSILE CRASH", "MIDDLE EAST", "WAR + DIPLOMACY"),
    ("IRAN: QESHM BLASTS WERE US DISPOSAL", "MIDDLE EAST", "WAR + DIPLOMACY"),
    ("US AIRLINES WARNED OF AL-QAEDA THREAT", "N. AMERICA", "SOCIETY"),
    ("DUCHESS SHARES CANCER JOURNEY IN HEAL", "EUROPE", "SOCIETY"),
    ("GLACIER MELT REVEALS 4,000-YEAR-OLD RING", "WORLD", "TECH + SCIENCE"),
    ("WHALE GENOMES FROM DRONE-FLOWN BREATH", "WORLD", "TECH + SCIENCE"),
    ("US LAW ROUNDS CASH TO NEAREST 5 CENTS", "N. AMERICA", "MARKETS"),
    ("CUMMINS KEEPS AUSTRALIA TEST CAPTAINCY", "OCEANIA", "SPORT"),
    ("MAN CITY WINLESS; LEEDS THRASH CHELSEA", "EUROPE", "SPORT"),
    ("KANE OUT FOR MONTHS AFTER ANKLE SURGERY", "EUROPE", "SOCIETY"),
    ("HARDEN 51 PASSES KOBE FOR 3RD-MOST 50S", "N. AMERICA", "SPORT"),
    ("REAL MADRID POST RECORD $1.34B REVENUE", "EUROPE", "MARKETS"),
    ("NICHOLLS 175; JAISWAL 85; NZ 368", "OCEANIA", "SPORT"),
    ("PAKISTAN WIN BLIND ASIA CUP AMID BOYCOTT", "ASIA", "SPORT"),
    ("FIRST JAPAN LIVE-FIRE TRAINING IN INDIA", "ASIA", "WAR + DIPLOMACY"),
    ("WILLIAM INSURES 10,000 FOREST STAFF", "EUROPE", "SOCIETY"),
    ("ICMR COMPLETES 100 TECH TRANSFERS", "ASIA", "TECH + SCIENCE"),
    ("AIR INDIA EXTENDS JEDDAH BAN TO 24 NOV", "ASIA", "SOCIETY"),
    ("PSG WIN 3-2 AT NICE; DOUE SERIOUSLY HURT", "EUROPE", "SPORT"),
    ("IDF LAUNCHES NEW STRIKES IN LEBANON", "MIDDLE EAST", "WAR + DIPLOMACY"),
    ("UN: HODEIDAH STRIKES THREATEN AID LINE", "MIDDLE EAST", "WAR + DIPLOMACY"),
    ("RUSSIAN ATTACHE EXPELLED IN RAPPER PLOT", "EUROPE", "WAR + DIPLOMACY"),
    ("ZELENSKY: TALKS MUST DELIVER RESULTS", "EUROPE", "WAR + DIPLOMACY"),
]

REGION_ORDER = ["EUROPE", "N. AMERICA", "MIDDLE EAST", "ASIA",
                "AFRICA", "S. AMERICA", "OCEANIA", "WORLD"]
FIELD_ORDER = ["WAR + DIPLOMACY", "MARKETS", "SPORT",
               "TECH + SCIENCE", "SOCIETY", "CLIMATE + ENERGY"]

# Seven numbers across the top strip: (small label, big figure, small note).
TOP_NUMBERS = [
    ("PERU QUAKE", "6.9", "IN THE ANDES"),
    ("KILLED IN SINALOA", "11", "IN CARTEL RAID"),
    ("DRONES FIRED", "400", "110 MISSILES TOO"),
    ("FRANCE-ARGENTINA", "45-17", "NATIONS FINAL"),
    ("EU BUDGET CUT", "$224B", "BELOW COMMISSION"),
    ("HARDEN POINTS", "51", "PASSES KOBE"),
    ("MADRID REVENUE", "$1.34B", "A CLUB RECORD"),
]

# Hero panels: (scene key, headline lines, red sub-lines).
HEROES = [
    ("gulf",
     ["GULF IN FLAMES", "IRAN HITS KUWAIT"],
     ["BAHRAIN TARGETED TOO", "TANKER HIT: 1 MISSING"]),
    ("sinaloa",
     ["EL CHAPO ISIDRO", "SEIZED IN SINALOA"],
     ["CARTEL KINGPIN TAKEN", "11 KILLED IN AFTERMATH"]),
    ("peru",
     ["PERU SHAKEN", "QUAKE 6.9, ANDES"],
     ["NO DEAD REPORTED YET", "LIMA RESIDENTS FLEE"]),
]

# Lead panels: (scene key, tag, headline).
LEADS = [
    ("ship", "SHIP", "DRONES HIT RUSSIAN SHIP IN BALTIC"),
    ("barrage", "BARRAGE", "MISSILES HIT KRYVYI RIH"),
    ("border", "BORDER", "ESTONIA TO SHUT RUSSIA BORDER"),
    ("summit", "SUMMIT", "TRUMP LANDS IN SHENZHEN"),
    ("vote", "VOTE", "EISENKOT CALLS LIKUD TALKS"),
    ("hospital", "HOSPITAL", "BOLSONARO IN ICU"),
    ("climate", "CLIMATE", "COP31 TALKS STALL OVER ENERGY"),
    ("protest", "PROTEST", "FRENCH PROTESTS SHRINK"),
    ("rugby", "RUGBY", "ENGLAND THRASH ALL BLACKS"),
    ("rugby2", "RUGBY", "FRANCE BEAT ARGENTINA 45-17"),
    ("cricket", "CRICKET", "AUSSIES WIN FIRST T20"),
    ("f1", "F1", "VERSTAPPEN TAKES VEGAS POLE"),
]

# Dotted sketch map: '#' is land, '.' is sea. 48 columns, 20 rows.
# I sketched this by eye from a world map: Americas left, Europe and
# Africa in the middle, Asia right, Australia low on the right.
MAP_ROWS = [
    "........................................",
    "........................................",
    "..############......######...###########...",
    ".##############.....#######..#############.",
    ".###############.....######..############..",
    "..##############......####....##########...",
    "...############.......###.....########.....",
    "....##########......######.....######......",
    ".....########.......########....####.......",
    "......######.......##########....###.......",
    ".....#####........##########....##.........",
    ".....####..........########................",
    "......###...........######......####........",
    ".......##............####......######.......",
    ".......##.............###.......####........",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
]

# Numbered pins on the map: (number, x, y, legend word).
PINS = [
    (1, 95, 602, "SINALOA"),
    (2, 160, 635, "PERU"),
    (3, 322, 570, "BALTIC"),
    (4, 360, 588, "KRYVYI RIH"),
    (5, 348, 580, "POLAND"),
    (6, 346, 562, "ESTONIA"),
    (7, 392, 600, "KUWAIT"),
    (8, 505, 600, "SHENZHEN"),
    (9, 372, 606, "ISRAEL"),
    (10, 185, 625, "BRAZIL"),
    (11, 302, 588, "FRANCE"),
    (12, 286, 574, "TWICKENHAM"),
    (13, 70, 595, "LAS VEGAS"),
    (14, 470, 600, "BIHAR"),
    (15, 560, 630, "WELLINGTON"),
]


# ================================================================ scenes
# Each painter fills one small box (x, y, w, h) with a flat scene built
# from the same rectangles, discs and triangles as the rest of the page.

def _stars(sh, x, y, w, h, count, colour):
    """A row of tiny star dots spread across the top of a box."""
    for i in range(count):
        sx = x + 6 + (i * (w - 12)) // max(1, count - 1)
        sy = y + 4 + (i * 7) % max(1, h // 3)
        sh.block(sx, sy, 2, 2, colour)


def paint_gulf(sh, x, y, w, h):
    """Night sky over a burning sea: three low suns, dark water."""
    sh.block(x, y, w, h, NIGHT)
    _stars(sh, x, y, w, h, 9, CREAM)
    for cx, cy, r in ((x + w // 4, y + h // 3, 13),
                      (x + w // 2, y + h // 4, 10),
                      (x + 3 * w // 4, y + h // 3, 13)):
        sh.disc(cx, cy, r + 3, DUSK)
        sh.disc(cx, cy, r, GOLD)
        sh.disc(cx, cy, r - 5, (240, 200, 90))
    sh.block(x, y + 2 * h // 3, w, h // 3, NAVY)
    sh.hline(x, y + 2 * h // 3, w, GOLD, 2)
    for fx in (x + w // 5, x + w // 2, x + 4 * w // 5):
        sh.triangle(fx, y + h - 6, fx + 7, y + h - 6,
                    fx + 3, y + h - 22, RED)
        sh.triangle(fx + 2, y + h - 6, fx + 6, y + h - 6,
                    fx + 4, y + h - 14, GOLD)


def paint_sinaloa(sh, x, y, w, h):
    """A house at night under a searchlight."""
    sh.block(x, y, w, h, NIGHT)
    _stars(sh, x, y, w, h, 8, CREAM)
    sh.disc(x + 5 * w // 6, y + h // 4, 8, CREAM)
    sh.triangle(x + w // 2, y + h // 5, x + 5 * w // 6, y + h // 5,
                x + w // 2, y + h // 2, (250, 244, 200))
    hx, hy, hw, hh = x + w // 4, y + h // 2, w // 2, h // 2 - 4
    sh.block(hx, hy, hw, hh, (222, 200, 160))
    sh.triangle(hx - 6, hy, hx + hw + 6, hy, hx + hw // 2, hy - 14, RED)
    sh.block(hx + hw // 2 - 5, hy + hh - 16, 10, 16, (90, 50, 30))
    sh.block(hx + 6, hy + 6, 12, 10, GOLD)
    sh.block(hx + hw - 18, hy + 6, 12, 10, GOLD)
    sh.block(x, y + h - 4, w, 4, (40, 60, 40))


def paint_peru(sh, x, y, w, h):
    """Andean peaks at dawn with a low sun and a small village."""
    sh.block(x, y, w, h, (214, 226, 232))
    sh.disc(x + 5 * w // 6, y + h // 4, 11, GOLD)
    sh.disc(x + 5 * w // 6, y + h // 4, 7, DUSK)
    sh.triangle(x, y + h, x + w // 3, y + h,
                x + w // 6, y + h // 5, (90, 100, 120))
    sh.triangle(x + w // 4, y + h, x + 3 * w // 4, y + h,
                x + w // 2, y + h // 8, (60, 70, 95))
    sh.triangle(x + 3 * w // 5, y + h, x + w, y + h,
                x + 4 * w // 5, y + h // 4, (110, 118, 135))
    sh.triangle(x + w // 2 - 12, y + h // 8 + 10, x + w // 2 + 12,
                y + h // 8 + 10, x + w // 2, y + h // 8, CREAM)
    sh.block(x, y + 5 * h // 6, w, h // 6, (150, 130, 95))
    for bx in (x + w // 6, x + w // 2, x + 4 * w // 5):
        sh.block(bx, y + 5 * h // 6 - 8, 16, 8, (120, 80, 55))
        sh.triangle(bx - 2, y + 5 * h // 6 - 8, bx + 18,
                    y + 5 * h // 6 - 8, bx + 8, y + 5 * h // 6 - 15, RED)


def paint_ship(sh, x, y, w, h):
    """A grey ship on a blue sea with a drone strike flash."""
    sh.block(x, y, w, h, SKY)
    sh.block(x, y + 3 * h // 5, w, 2 * h // 5, (40, 90, 140))
    sh.block(x + w // 6, y + h // 2, 2 * w // 3, h // 6, (70, 75, 80))
    sh.triangle(x + w // 6, y + h // 2, x + w // 6, y + 2 * h // 3,
                x + w // 12, y + 2 * h // 3, (70, 75, 80))
    sh.block(x + w // 3, y + h // 5, 4, h // 3, INK)
    sh.block(x + w // 2, y + h // 4, 14, 8, RED)
    sh.disc(x + 3 * w // 4, y + h // 3, 9, GOLD)
    sh.disc(x + 3 * w // 4, y + h // 3, 5, RED)
    sh.disc(x + w // 4, y + h // 4, 3, INK)
    sh.disc(x + w // 3, y + h // 6, 2, INK)


def paint_barrage(sh, x, y, w, h):
    """Explosions over a dark skyline."""
    sh.block(x, y, w, h, NIGHT)
    _stars(sh, x, y, w, h, 7, CREAM)
    for bx, bw, bh in ((x + 4, 22, 26), (x + 30, 16, 34),
                       (x + 50, 26, 20), (x + 80, 18, 30),
                       (x + 102, 24, 24)):
        sh.block(bx, y + h - bh, bw, bh, (50, 52, 70))
    for ex, ey, r in ((x + w // 4, y + h // 3, 8),
                      (x + 3 * w // 4, y + h // 4, 10)):
        sh.disc(ex, ey, r + 3, DUSK)
        sh.disc(ex, ey, r, GOLD)
        sh.disc(ex, ey, r - 4, RED)
    sh.block(x, y + h - 4, w, 4, (30, 30, 40))


def paint_border(sh, x, y, w, h):
    """A red-and-white border barrier under a pale sky."""
    sh.block(x, y, w, h, (200, 214, 222))
    sh.block(x, y + 2 * h // 3, w, h // 3, (140, 150, 130))
    for i in range(6):
        col = RED if i % 2 == 0 else CREAM
        sh.block(x + 8 + i * (w - 16) // 6, y + h // 3,
                 (w - 16) // 6, 10, col)
    for px in (x + 10, x + w // 2 - 2, x + w - 14):
        sh.block(px, y + h // 3, 4, h // 3 + 6, INK)
    sh.block(x + w // 3, y + h // 6, w // 3, 12, NAVY)
    sh.block(x + w // 3 + 4, y + h // 6 + 3, w // 3 - 8, 3, CREAM)
    sh.block(x + w // 3 + 4, y + h // 6 + 7, w // 3 - 8, 3, CREAM)


def paint_summit(sh, x, y, w, h):
    """City towers at dusk with lit windows."""
    sh.block(x, y, w, h, (232, 180, 110))
    for bx, bw, bh in ((x + 6, 24, 44), (x + 36, 30, 58),
                       (x + 72, 22, 38), (x + 100, 28, 50)):
        sh.block(bx, y + h - bh, bw, bh, NAVY)
        for wy in range(y + h - bh + 6, y + h - 6, 10):
            for wx in range(bx + 5, bx + bw - 5, 9):
                sh.block(wx, wy, 4, 5, GOLD)
    sh.disc(x + w - 18, y + 14, 8, GOLD)
    sh.block(x, y + h - 4, w, 4, INK)


def paint_vote(sh, x, y, w, h):
    """A ballot box with a paper slip going in."""
    sh.block(x, y, w, h, (196, 214, 228))
    sh.block(x + w // 4, y + h // 3, w // 2, h // 2, NAVY)
    sh.block(x + w // 4 + 8, y + h // 3 - 4, w // 2 - 16, 4, INK)
    sh.block(x + w // 2 - 4, y + h // 6, 8, h // 6, CREAM)
    sh.block(x + w // 2 - 8, y + h // 6 - 4, 16, 4, RED)
    sh.block(x + w // 6, y + 2 * h // 3, w // 6, 4, RED)
    sh.block(x + 2 * w // 3, y + 2 * h // 3, w // 6, 4, RED)
    sh.block(x, y + h - 4, w, 4, (120, 110, 95))


def paint_hospital(sh, x, y, w, h):
    """A white hospital block with a red cross."""
    sh.block(x, y, w, h, (214, 228, 236))
    sh.block(x + w // 6, y + h // 4, 2 * w // 3, h // 2, CREAM)
    sh.block(x + w // 6, y + h // 4, 2 * w // 3, 5, NAVY)
    cx, cy = x + w // 2, y + h // 2
    sh.block(cx - 4, cy - 14, 8, 28, RED)
    sh.block(cx - 14, cy - 4, 28, 8, RED)
    for wx in (x + w // 6 + 8, x + w - w // 6 - 14):
        sh.block(wx, y + h // 4 + 12, 8, 8, SKY)
    sh.block(x, y + h - 4, w, 4, GREEN)


def paint_climate(sh, x, y, w, h):
    """A small green globe under a hot sun."""
    sh.block(x, y, w, h, SKY)
    sh.disc(x + 5 * w // 6, y + h // 5, 9, GOLD)
    sh.disc(x + w // 2, y + h // 2, 24, TEAL)
    sh.disc(x + w // 2 - 8, y + h // 2 - 6, 8, GREEN)
    sh.disc(x + w // 2 + 9, y + h // 2 + 7, 7, GREEN)
    sh.disc(x + w // 2 + 4, y + h // 2 - 10, 5, GREEN)
    sh.block(x + w // 6, y + h // 5, 22, 5, CREAM)
    sh.block(x + w // 6 + 6, y + h // 5 - 4, 12, 4, CREAM)
    sh.block(x + 2 * w // 3, y + 3 * h // 4, 24, 5, CREAM)


def paint_protest(sh, x, y, w, h):
    """A small crowd with placards."""
    sh.block(x, y, w, h, (222, 214, 196))
    sh.block(x + w // 5, y + h // 5, w // 4, 10, RED)
    sh.block(x + 3 * w // 5, y + h // 6, w // 4, 10, NAVY)
    sh.block(x + w // 5 + 8, y + h // 5 + 10, 3, 16, INK)
    sh.block(x + 3 * w // 5 + 8, y + h // 6 + 10, 3, 16, INK)
    for i in range(6):
        px = x + 8 + i * (w - 16) // 6
        sh.disc(px + 6, y + 2 * h // 3, 6, (200, 160, 120))
        sh.block(px, y + 2 * h // 3 + 6, 12, h // 4, (90, 90, 110)
                 if i % 2 else (140, 60, 55))
    sh.block(x, y + h - 4, w, 4, GREY)


def paint_pitch(sh, x, y, w, h, ball_x=None):
    """A green rugby pitch with posts and a ball."""
    sh.block(x, y, w, h, GREEN)
    sh.block(x + 6, y + 6, w - 12, h - 12, (56, 140, 72))
    sh.frame(x + 6, y + 6, w - 12, h - 12, CREAM, 1)
    sh.hline(x + 6, y + h // 2, w - 12, CREAM, 1)
    sh.disc(x + w // 2, y + h // 2, 7, CREAM)
    sh.ring(x + w // 2, y + h // 2, 7, GREEN, 5)
    px = x + w - 18
    sh.vline(px, y + 8, h - 16, CREAM, 2)
    sh.vline(px + 8, y + 8, h - 16, CREAM, 2)
    sh.hline(px, y + 8, 10, CREAM, 2)
    bx = ball_x if ball_x is not None else x + w // 3
    sh.disc(bx, y + 2 * h // 3, 7, CREAM)
    sh.disc(bx, y + 2 * h // 3, 4, INK)


def paint_cricket(sh, x, y, w, h):
    """Stumps, a bat and a red ball on a green outfield."""
    sh.block(x, y, w, h, (120, 170, 90))
    sh.block(x + w // 4, y + h // 4, w // 2, h // 2, (190, 170, 120))
    for i in range(3):
        sh.vline(x + w // 2 - 8 + i * 8, y + h // 5, 18, GOLD, 3)
    sh.hline(x + w // 2 - 8, y + h // 5 - 3, 22, GOLD, 2)
    sh.block(x + w // 4 + 6, y + h // 2, 8, 22, (150, 110, 60))
    sh.block(x + w // 4 + 8, y + h // 2 - 12, 4, 14, (150, 110, 60))
    sh.disc(x + 3 * w // 4, y + 3 * h // 4, 6, RED)
    sh.disc(x + w // 6, y + h // 6, 5, CREAM)


def paint_f1(sh, x, y, w, h):
    """A red race car under lights on a night track."""
    sh.block(x, y, w, h, NIGHT)
    _stars(sh, x, y, w, h, 6, CREAM)
    sh.block(x, y + 2 * h // 3, w, h // 3, (40, 42, 52))
    sh.hline(x, y + 2 * h // 3, w, GOLD, 2)
    sh.hline(x, y + 5 * h // 6, w, CREAM, 1)
    cx = x + w // 2
    sh.block(cx - 34, y + h // 2, 68, 10, RED)
    sh.block(cx - 12, y + h // 2 - 8, 26, 9, RED)
    sh.block(cx - 44, y + h // 2 - 2, 8, 12, INK)
    sh.disc(cx - 22, y + h // 2 + 12, 8, INK)
    sh.disc(cx + 22, y + h // 2 + 12, 8, INK)
    sh.disc(cx - 22, y + h // 2 + 12, 4, GREY)
    sh.disc(cx + 22, y + h // 2 + 12, 4, GREY)
    for i in range(4):
        for j in range(2):
            col = INK if (i + j) % 2 == 0 else CREAM
            sh.block(x + w - 22 + i * 4, y + 6 + j * 4, 4, 4, col)


SCENES = {
    "gulf": paint_gulf,
    "sinaloa": paint_sinaloa,
    "peru": paint_peru,
    "ship": paint_ship,
    "barrage": paint_barrage,
    "border": paint_border,
    "summit": paint_summit,
    "vote": paint_vote,
    "hospital": paint_hospital,
    "climate": paint_climate,
    "protest": paint_protest,
    "rugby": paint_pitch,
    "rugby2": paint_pitch,
    "cricket": paint_cricket,
    "f1": paint_f1,
}


# =============================================================== page build
def count_stories():
    """Count regions and fields from STORIES; both must add to the total."""
    regions = {name: 0 for name in REGION_ORDER}
    fields = {name: 0 for name in FIELD_ORDER}
    for _title, region, field in STORIES:
        regions[region] += 1
        fields[field] += 1
    total = len(STORIES)
    assert total == 46, "story list must hold 46 stories"
    assert sum(regions.values()) == total, "region counts must add to 46"
    assert sum(fields.values()) == total, "field counts must add to 46"
    return regions, fields


def draw_masthead(sh):
    sh.text_centred(512, 14, "THE WORLD IN ONE PICTURE", 6, INK)
    sh.text_centred(512, 62, "SUNDAY 22 NOVEMBER 2026", 4, RED)
    sh.text(16, 94, "NO. 326", 2, INK)
    sh.text_centred(512, 94, "ONE DAY - ONE PAGE - 46 STORIES", 2, INK)
    right = "MAKE.FUN DAILY"
    sh.text(1012 - sh.text_width(right, 2), 94, right, 2, INK)
    sh.hline(12, 112, 1000, INK, 2)


def draw_top_numbers(sh):
    y = 118
    h = 52
    x = 14
    for label, big, note in TOP_NUMBERS:
        sh.frame(x, y, 139, h, INK, 1)
        sh.text_centred(x + 69, y + 5, label, 1, INK)
        sh.text_centred(x + 69, y + 16, big, 3, RED)
        sh.text_centred(x + 69, y + 40, note, 1, INK)
        x += 143


def draw_heroes(sh):
    y = 174
    h = 150
    for i, (scene, heads, subs) in enumerate(HEROES):
        x = 12 + i * 334
        w = 328
        sh.frame(x, y, w, h, INK, 1)
        SCENES[scene](sh, x + 2, y + 2, w - 4, 62)
        sh.hline(x, y + 66, w, INK, 1)
        yy = y + 70
        for line in heads:
            sh.text(x + 8, yy, line, 3, INK)
            yy += 25
        yy = y + 118
        for line in subs:
            sh.text(x + 8, yy, line, 2, RED)
            yy += 16


def draw_leads(sh):
    for row in range(2):
        y = 330 + row * 106
        h = 100
        for col in range(6):
            lead = LEADS[row * 6 + col]
            scene, tag, head = lead
            x = 13 + col * 167
            w = 163
            sh.frame(x, y, w, h, INK, 1)
            SCENES[scene](sh, x + 2, y + 2, w - 4, 36)
            sh.hline(x, y + 40, w, INK, 1)
            sh.text(x + 6, y + 44, tag, 1, RED)
            sh.paragraph(x + 6, y + 52, head, w - 12, 2, INK, leading=15)


def draw_map(sh):
    x0, y0 = 12, 542
    w, h = 652, 164
    sh.frame(x0, y0, w, h, INK, 1)
    ox, oy = x0 + 10, y0 + 18
    for r, row in enumerate(MAP_ROWS):
        for c, cell in enumerate(row):
            if cell == "#":
                sh.block(ox + c * 13, oy + r * 5, 3, 3, NAVY)
    for num, px, py, _label in PINS:
        sh.disc(px, py, 8, RED)
        sh.ring(px, py, 8, CREAM, 1)
        word = str(num)
        sh.text(px - sh.text_width(word, 1) // 2, py - 4, word, 1, CREAM)
    legend = "  ".join("%d %s" % (n, lab) for n, _x, _y, lab in PINS)
    sh.paragraph(x0 + 10, y0 + 124, legend, w - 20, 1, INK, leading=11)


def draw_numbers(sh, regions, fields):
    x0, y0 = 670, 542
    w, h = 342, 164
    sh.frame(x0, y0, w, h, INK, 1)
    sh.text_centred(x0 + w // 2, y0 + 6, "THE DAY IN NUMBERS", 2, INK)
    sh.hline(x0 + 8, y0 + 24, w - 16, INK, 1)
    yy = y0 + 28
    for name in REGION_ORDER:
        val = regions[name]
        sh.text(x0 + 10, yy, name, 1, INK)
        bar_w = val * 150 // 16
        if bar_w:
            sh.block(x0 + 118, yy, bar_w, 7, TEAL)
        sh.text(x0 + 118 + 156, yy, str(val), 1, INK)
        yy += 9
    yy += 2
    for name in FIELD_ORDER:
        val = fields[name]
        sh.text(x0 + 10, yy, name, 1, INK)
        bar_w = val * 150 // 16
        if bar_w:
            sh.block(x0 + 118, yy, bar_w, 7, GOLD)
        sh.text(x0 + 118 + 156, yy, str(val), 1, INK)
        yy += 8


def draw_briefs(sh):
    sh.text(14, 712, "MORE FROM THE DAY", 2, INK)
    sh.hline(12, 730, 1000, INK, 2)
    briefs = [title for title, _r, _f in STORIES[15:]]
    left = briefs[:16]
    right = briefs[16:]
    for col_x, items in ((14, left), (522, right)):
        yy = 738
        for item in items:
            sh.block(col_x, yy + 1, 7, 7, RED)
            sh.text(col_x + 12, yy, item, 1, INK)
            yy += 14


def draw_footer(sh):
    sh.hline(12, 958, 1000, INK, 2)
    sh.text(14, 966,
            "NOT TODAY: THE ICJ MYANMAR RULING WAS 19 NOV - "
            "THE SHENZHEN TRILATERAL WAS 19 NOV - "
            "THE ANTHROPIC DEBUT WAS 19 NOV.", 1, INK)
    sh.text(14, 982,
            "ALL 46 STORIES HAPPENED OR WERE FIRST REPORTED "
            "ON SUNDAY 22 NOVEMBER 2026.", 1, INK)


def build_page():
    """Draw the whole front page and return (sheet, regions, fields)."""
    regions, fields = count_stories()
    sh = Sheet(PAGE_W, PAGE_H, PAPER)
    sh.frame(6, 6, 1012, 1012, INK, 2)
    draw_masthead(sh)
    draw_top_numbers(sh)
    draw_heroes(sh)
    draw_leads(sh)
    draw_map(sh)
    draw_numbers(sh, regions, fields)
    draw_briefs(sh)
    draw_footer(sh)
    return sh, regions, fields


def main():
    sh, regions, fields = build_page()
    data = encode_png(sh)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("stories: %d (heroes 3, leads 12, briefs 31)" % len(STORIES))
    print("regions: %s total %d"
          % (" ".join("%s=%d" % (k, regions[k]) for k in REGION_ORDER),
             sum(regions.values())))
    print("fields: %s total %d"
          % (" ".join("%s=%d" % (k, fields[k]) for k in FIELD_ORDER),
             sum(fields.values())))
    print("png: %d bytes, %dx%d" % (len(data), PAGE_W, PAGE_H))
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
