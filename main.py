#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE: Sunday 22 November 2026.

Draws a dense newspaper front page, 1024 by 1024 pixels, with the
Python standard library only. It sums up 46 stories that happened, or
were first reported, on Sunday 22 November 2026: three hero panels
(the Gulf in flames as Iran strikes US bases, the capture of cartel
kingpin El Chapo Isidro in Sinaloa, and a magnitude 6.9 earthquake
in the Peruvian Andes), twelve illustrated leads, a sketch world map
with fifteen numbered pins, and thirty-one one-line briefs, plus a
by-the-numbers strip and a date-check footer that names the big
stories that are NOT today's (the ICJ Myanmar ruling and the
Shenzhen trilateral were both 19 November; the Anthropic debut was
19 November too).

The program is deterministic: no clock, no randomness, no network.
It writes entry.png to $MAKEFUN_OUTPUT_DIR when that is set, and to
/output/entry.png otherwise.

Run:  python3 main.py
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (179, 35, 27)
NAVY = (20, 38, 77)
TEAL = (14, 110, 110)
GOLD = (201, 141, 32)
SKY = (168, 208, 232)
SKYNIGHT = (16, 28, 58)
GREY = (110, 108, 100)
LIGHT = (238, 231, 214)
GREEN = (46, 110, 58)
PITCH = (58, 128, 66)
CREAM = (253, 246, 227)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (224, 110, 20)
DARKRED = (120, 22, 18)
STEEL = (150, 158, 165)
SAND = (226, 205, 158)
DUST = (196, 178, 140)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def frame(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d - r * r) <= r:
                        self.set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=True)

    def ring(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=False)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        # filled triangle by scanline
        xs = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = xs
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / float(by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / float(cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / float(cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.hline(lo, y, hi - lo + 1, c)

    def poly(self, pts, c):
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            self.line(x0, y0, x1, y1, c)


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 bits. Lowercase maps to uppercase, so
# headlines stay in one clean case and M and W keep their shapes.
_G = {}


def _g(ch, rows):
    _G[ch] = tuple(int(r.replace("#", "1").replace(".", "0"), 2)
                   for r in rows)


_g("A", ("01110", "10001", "10001", "11111", "10001", "10001", "10001"))
_g("B", ("11110", "10001", "10001", "11110", "10001", "10001", "11110"))
_g("C", ("01110", "10001", "10000", "10000", "10000", "10001", "01110"))
_g("D", ("11110", "10001", "10001", "10001", "10001", "10001", "11110"))
_g("E", ("11111", "10000", "10000", "11110", "10000", "10000", "11111"))
_g("F", ("11111", "10000", "10000", "11110", "10000", "10000", "10000"))
_g("G", ("01110", "10001", "10000", "10111", "10001", "10001", "01111"))
_g("H", ("10001", "10001", "10001", "11111", "10001", "10001", "10001"))
_g("I", ("01110", "00100", "00100", "00100", "00100", "00100", "01110"))
_g("J", ("00111", "00010", "00010", "00010", "00010", "10010", "01100"))
_g("K", ("10001", "10010", "10100", "11000", "10100", "10010", "10001"))
_g("L", ("10000", "10000", "10000", "10000", "10000", "10000", "11111"))
_g("M", ("10001", "11011", "10101", "10101", "10001", "10001", "10001"))
_g("N", ("10001", "11001", "10101", "10011", "10001", "10001", "10001"))
_g("O", ("01110", "10001", "10001", "10001", "10001", "10001", "01110"))
_g("P", ("11110", "10001", "10001", "11110", "10000", "10000", "10000"))
_g("Q", ("01110", "10001", "10001", "10001", "10101", "10010", "01101"))
_g("R", ("11110", "10001", "10001", "11110", "10100", "10010", "10001"))
_g("S", ("01111", "10000", "10000", "01110", "00001", "00001", "11110"))
_g("T", ("11111", "00100", "00100", "00100", "00100", "00100", "00100"))
_g("U", ("10001", "10001", "10001", "10001", "10001", "10001", "01110"))
_g("V", ("10001", "10001", "10001", "10001", "10001", "01010", "00100"))
_g("W", ("10001", "10001", "10001", "10101", "10101", "11011", "10001"))
_g("X", ("10001", "10001", "01010", "00100", "01010", "10001", "10001"))
_g("Y", ("10001", "10001", "01010", "00100", "00100", "00100", "00100"))
_g("Z", ("11111", "00001", "00010", "00100", "01000", "10000", "11111"))
_g("0", ("01110", "10001", "10011", "10101", "11001", "10001", "01110"))
_g("1", ("00100", "01100", "00100", "00100", "00100", "00100", "01110"))
_g("2", ("01110", "10001", "00001", "00110", "01000", "10000", "11111"))
_g("3", ("11111", "00010", "00100", "00010", "00001", "10001", "01110"))
_g("4", ("00010", "00110", "01010", "10010", "11111", "00010", "00010"))
_g("5", ("11111", "10000", "11110", "00001", "00001", "10001", "01110"))
_g("6", ("01110", "10000", "10000", "11110", "10001", "10001", "01110"))
_g("7", ("11111", "00001", "00010", "00100", "01000", "01000", "01000"))
_g("8", ("01110", "10001", "10001", "01110", "10001", "10001", "01110"))
_g("9", ("01110", "10001", "10001", "01111", "00001", "00001", "01110"))
_g(" ", ("00000", "00000", "00000", "00000", "00000", "00000", "00000"))
_g(".", ("00000", "00000", "00000", "00000", "00000", "01100", "01100"))
_g(",", ("00000", "00000", "00000", "00000", "01100", "00100", "01000"))
_g(":", ("00000", "01100", "01100", "00000", "01100", "01100", "00000"))
_g(";", ("00000", "01100", "01100", "00000", "01100", "00100", "01000"))
_g("'", ("00100", "00100", "01000", "00000", "00000", "00000", "00000"))
_g("-", ("00000", "00000", "00000", "01110", "00000", "00000", "00000"))
_g("!", ("00100", "00100", "00100", "00100", "00100", "00000", "00100"))
_g("?", ("01110", "10001", "00001", "00110", "00100", "00000", "00100"))
_g("%", ("11001", "11010", "00010", "00100", "01000", "01011", "10011"))
_g("(", ("00010", "00100", "01000", "01000", "01000", "00100", "00010"))
_g(")", ("01000", "00100", "00010", "00010", "00010", "00100", "01000"))
_g("/", ("00001", "00010", "00010", "00100", "01000", "01000", "10000"))
_g("&", ("01100", "10010", "10100", "01000", "10101", "10010", "01101"))
_g("+", ("00000", "00100", "00100", "01110", "00100", "00100", "00000"))
_g("=", ("00000", "00000", "11111", "00000", "11111", "00000", "00000"))
_g("$", ("00100", "01111", "10100", "01110", "00101", "11110", "00100"))
_g("*", ("00000", "10101", "01110", "11111", "01110", "10101", "00000"))
_g("#", ("01010", "01010", "11111", "01010", "11111", "01010", "01010"))
_g("<", ("00010", "00100", "01000", "10000", "01000", "00100", "00010"))
_g(">", ("01000", "00100", "00010", "00001", "00010", "00100", "01000"))
_g("@", ("01110", "10001", "10111", "10101", "10110", "10000", "01110"))
_g("_", ("00000", "00000", "00000", "00000", "00000", "00000", "11111"))


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = _G.get(ch, _G["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.rect(cx + col * scale, y + row * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(s, scale, max_w):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(cv, x, y, lines, scale, color, lh=None):
    if lh is None:
        lh = 9 * scale
    for ln in lines:
        draw_text(cv, x, y, ln, scale, color)
        y += lh
    return y

# ---------------------------------------------------------------- stories
# Every story happened, or was first reported, on Sunday 22 Nov 2026.
# Region codes: EU Europe, NA North America, ME Middle East, AS Asia,
# AF Africa, OC Oceania, SA South America, WO World. Field codes: WAR
# war and diplomacy, MKT markets and business, SPT sport, TEC tech and
# science, SOC society and justice, CLI climate and energy.
HEROES = [
    ("GULF IN FLAMES",
     "IRAN HITS KUWAIT",
     ["BAHRAIN TARGETED TOO", "TANKER HIT; 1 MISSING"],
     "ME", "WAR"),
    ("EL CHAPO ISIDRO",
     "SEIZED IN SINALOA",
     ["CARTEL KINGPIN TAKEN", "11 KILLED IN AFTERMATH"],
     "NA", "SOC"),
    ("PERU SHAKEN",
     "QUAKE 6.9, ANDES",
     ["NO DEAD REPORTED YET", "LIMA RESIDENTS FLEE"],
     "SA", "SOC"),
]

LEADS = [
    ("DRONES HIT RUSSIAN SHIP IN BALTIC", "Drones strike a Russian "
     "cargo ship in the Baltic; Finland tightens security and Ukraine "
     "is the likely hand behind the attack.", "SHIP", "EU", "WAR"),
    ("MISSILES HIT KRYVYI RIH", "Russia hits Zelensky's hometown "
     "with ballistic missiles in one of the war's largest attacks: "
     "400 drones and 110 missiles, one falling in Poland.",
     "BARRAGE", "EU", "WAR"),
    ("ESTONIA TO SHUT RUSSIA BORDER", "Estonia moves to close its "
     "border with Russia; Moscow decries a new Iron Curtain.",
     "BORDER", "EU", "WAR"),
    ("TRUMP LANDS IN SHENZHEN", "Trump reaches Shenzhen for the "
     "APEC summit; a trilateral with Xi and Putin is planned. Trump "
     "says Putin wants peace; Zelensky calls Putin a killer.",
     "SUMMIT", "AS", "WAR"),
    ("EISENKOT CALLS LIKUD TALKS", "Israel coalition talks: "
     "Eisenkot invites Netanyahu's Likud to marathon talks.",
     "VOTE", "ME", "WAR"),
    ("BOLSONARO IN ICU", "Brazil's ex-president is admitted to "
     "intensive care with an acute bowel obstruction.",
     "HOSPITAL", "SA", "SOC"),
    ("COP31 TALKS STALL OVER ENERGY", "The climate talks are in "
     "impasse as the fight over energy stalls a deal.",
     "CLIMATE", "WO", "CLI"),
    ("FRENCH PROTESTS SHRINK", "A sixth straight Saturday of "
     "protests draws a lower turnout; police are jailed for racist "
     "violence in a landmark ruling.", "PROTEST", "EU", "SOC"),
    ("ENGLAND THRASH ALL BLACKS", "England thrash New Zealand "
     "after Moody faces the haka at Twickenham.", "RUGBY", "EU", "SPT"),
    ("FRANCE BEAT ARGENTINA 45-17", "France beat Argentina 45-17 "
     "to reach the Nations Championship final.", "RUGBY", "EU", "SPT"),
    ("AUSSIES WIN FIRST T20", "Australia clinch their first T20 "
     "win over England by 3 wickets: Brook 65, England 187.",
     "CRICKET", "OC", "SPT"),
    ("VERSTAPPEN TAKES VEGAS POLE", "Verstappen takes the Las "
     "Vegas Grand Prix pole; Antonelli is hit with a five-place "
     "grid penalty.", "F1", "NA", "SPT"),
]

BRIEFS = [
    ("EU BUDGET PLAN $224B BELOW COMMISSION", "EU", "MKT"),
    ("US LIMITS MILITARY CONTACT WITH CANADA", "NA", "WAR"),
    ("CHINA TO BAR YOUNG RED-CHIP FIRMS ABROAD", "AS", "MKT"),
    ("CRUDE OIL FUTURES FALL MORE THAN 3%", "WO", "MKT"),
    ("MODI OPENS NITISH SETU BRIDGE IN BIHAR", "AS", "SOC"),
    ("CYCLONE AKVAN: 14 FLIGHTS CUT AT RANCHI", "AS", "SOC"),
    ("11 DIE FROM TAINTED ALCOHOL IN MANIPUR", "AS", "SOC"),
    ("FBI DATABASE BREACH RAISES ALARM", "NA", "TEC"),
    ("BAHRAIN PROBES PATRIOT MISSILE CRASH", "ME", "WAR"),
    ("IRAN: QESHM BLASTS WERE US DISPOSAL", "ME", "WAR"),
    ("AIRLINES WARNED OF AL-QAEDA THREAT", "NA", "WAR"),
    ("DUCHESS SHARES CANCER JOURNEY IN HEAL", "EU", "SOC"),
    ("GLACIER MELT REVEALS 4,000-YEAR-OLD RING", "EU", "TEC"),
    ("WHALE GENOMES FROM DRONE-BLOWN BREATH", "WO", "TEC"),
    ("US LAW ROUNDS CASH TO NEAREST 5 CENTS", "NA", "MKT"),
    ("CUMMINS KEEPS AUSTRALIA TEST CAPTAINCY", "OC", "SOC"),
    ("MAN CITY WINLESS; LEEDS THRASH CHELSEA", "EU", "SPT"),
    ("KANE OUT FOR MONTHS AFTER ANKLE SURGERY", "EU", "SPT"),
    ("HARDEN 51, PASSES KOBE FOR 3RD-MOST 50S", "NA", "SPT"),
    ("REAL MADRID POST RECORD $1.34B REVENUE", "EU", "MKT"),
    ("NICHOLLS 175, JAISWAL 85; NZ 368", "OC", "SPT"),
    ("PAKISTAN WIN BLIND ASIA CUP AMID BOYCOTT", "AS", "SPT"),
    ("FIRST JAPAN LIVE-FIRE TRAINING IN INDIA", "AS", "WAR"),
    ("WILLIAM INSURES 10,000 FOREST STAFF", "EU", "SOC"),
    ("ICMR COMPLETES 100 TECH TRANSFERS", "AS", "TEC"),
    ("AIR INDIA EXTENDS JEDDAH BAN TO 24 NOV", "AS", "SOC"),
    ("PSG WIN 3-2 AT NICE; DOUE SERIOUSLY HURT", "EU", "SPT"),
    ("IDF LAUNCHES NEW STRIKES IN S. LEBANON", "ME", "WAR"),
    ("UN: HODEIDAH STRIKES THREATEN AID LINE", "ME", "WAR"),
    ("RUSSIAN ATTACHE EXPELLED IN RAPPER PLOT", "EU", "WAR"),
    ("ZELENSKY: TALKS MUST DELIVER RESULTS", "EU", "WAR"),
]

NUMBERS = [
    ("PERU QUAKE", "6.9", "in the Andes"),
    ("KILLED IN SINALOA", "11", "in cartel raid"),
    ("DRONES FIRED", "400", "110 missiles too"),
    ("FRANCE-ARGENTINA", "45-17", "Nations final"),
    ("EU BUDGET CUT", "$224B", "below Commission"),
    ("HARDEN POINTS", "51", "passes Kobe"),
    ("MADRID REVENUE", "$1.34B", "a club record"),
]

REGIONS = [("EUROPE", "EU"), ("N. AMERICA", "NA"), ("MIDDLE EAST", "ME"),
           ("ASIA", "AS"), ("AFRICA", "AF"), ("S. AMERICA", "SA"),
           ("OCEANIA", "OC"), ("WORLD", "WO")]
FIELDS = [("WAR + DIPLOMACY", "WAR"), ("MARKETS", "MKT"), ("SPORT", "SPT"),
          ("TECH + SCIENCE", "TEC"), ("SOCIETY", "SOC"),
          ("CLIMATE + ENERGY", "CLI")]

MAP_PINS = [
    (1, "SINALOA", 0.10, 0.42),
    (2, "PERU", 0.20, 0.68),
    (3, "BALTIC", 0.53, 0.12),
    (4, "KRYVYI RIH", 0.625, 0.24),
    (5, "POLAND", 0.565, 0.19),
    (6, "ESTONIA", 0.60, 0.06),
    (7, "KUWAIT", 0.64, 0.38),
    (8, "SHENZHEN", 0.80, 0.30),
    (9, "ISRAEL", 0.60, 0.32),
    (10, "BRAZIL", 0.27, 0.62),
    (11, "FRANCE", 0.51, 0.20),
    (12, "TWICKENHAM", 0.485, 0.10),
    (13, "LAS VEGAS", 0.17, 0.30),
    (14, "BIHAR", 0.72, 0.36),
    (15, "WELLINGTON", 0.93, 0.88),
]

# Coarse dotted world map, 48 columns by 24 rows, drawn from a rough
# outline. Each row is a string; '#' is land, '.' is sea.
MAP_ROWS = [
    "...########.............######################..",
    "..###########..........#######################..",
    "..############.........#######################..",
    "...###########........#######################...",
    "...###########........#####################.....",
    "....#########.........####################......",
    "....########..........#######.....##########....",
    "....########..........###########..########.....",
    ".....#####............########...####.####......",
    "......####.............########..###.####.......",
    "........###............#########.###.####.......",
    ".........###...........#########....#####.......",
    "..........####.........########......######.....",
    "..........#####.........######........######....",
    "..........#####.........#####.........######....",
    "..........#####.........#####...........####....",
    "..........#####.........#####..........######...",
    "...........####..........####..........######...",
    "...........####..........###............####....",
    "...........###...........###............####....",
    "...........###...........##.............##......",
    "...........##...............................##..",
    "...........##...................................",
    "................................................",
]

# ---------------------------------------------------------------- scenes
def scene_gulf(cv, x, y, w, h):
    # Night sea in the Gulf: tankers, flames, missile trails.
    cv.rect(x, y, w, h, SKYNIGHT)
    for sx, sy in [(8, 10), (30, 18), (55, 8), (80, 14), (20, 30),
                   (65, 28), (90, 10), (42, 12), (72, 36), (15, 44)]:
        cv.disc(x + sx * w // 100, y + sy * h // 100,
                max(1, w // 200), WHITE)
    cv.rect(x, y + h * 60 // 100, w, h * 40 // 100, (24, 68, 130))
    cv.hline(x, y + h * 60 // 100, w, WHITE, 1)
    # tanker hulls
    for tx, tw in [(8, 34), (52, 40)]:
        hx = x + tx * w // 100
        hw = w * tw // 100
        cv.rect(hx, y + h * 52 // 100, hw, h * 12 // 100, (40, 40, 48))
        cv.rect(hx + hw // 4, y + h * 40 // 100, hw // 6, h * 12 // 100,
                (40, 40, 48))
    # flames over the hulls
    for ex, ey, r in [(24, 38, 9), (70, 34, 11), (88, 44, 7)]:
        cx = x + ex * w // 100
        cy = y + ey * h // 100
        cv.disc(cx, cy, r * w // 200 + 3, ORANGE)
        cv.disc(cx, cy, r * w // 300 + 2, (255, 220, 90))
        for ang in range(0, 360, 45):
            dx = int((r + 8) * w / 200 * math.cos(math.radians(ang)))
            dy = int((r + 8) * h / 200 * math.sin(math.radians(ang)))
            cv.line(cx, cy, cx + dx, cy + dy, (255, 220, 90))
    cv.line(x + w * 12 // 100, y + h * 8 // 100,
            x + w * 26 // 100, y + h * 30 // 100, WHITE)
    cv.line(x + w * 86 // 100, y + h * 6 // 100,
            x + w * 70 // 100, y + h * 30 // 100, WHITE)


def scene_raid(cv, x, y, w, h):
    # Night raid in Sinaloa: searchlight, house, helicopter.
    cv.rect(x, y, w, h, (12, 16, 34))
    for sx, sy in [(10, 12), (30, 8), (55, 14), (78, 8), (92, 18)]:
        cv.disc(x + sx * w // 100, y + sy * h // 100, 2, WHITE)
    cv.rect(x, y + h * 68 // 100, w, h * 32 // 100, (26, 30, 26))
    hx = x + w * 34 // 100
    hw = w * 32 // 100
    cv.rect(hx, y + h * 48 // 100, hw, h * 34 // 100, (120, 100, 70))
    cv.tri(hx - 4, y + h * 48 // 100, hx + hw // 2, y + h * 34 // 100,
           hx + hw + 4, y + h * 48 // 100, DARKRED)
    for wy in range(y + h * 56 // 100, y + h * 76 // 100, h * 12 // 100):
        cv.rect(hx + 6, wy, 5, 6, (255, 230, 120))
        cv.rect(hx + hw - 11, wy, 5, 6, (255, 230, 120))
    # helicopter with a searchlight cone
    cx = x + w * 76 // 100
    cy = y + h * 20 // 100
    cv.rect(cx - 14, cy - 4, 28, 8, (60, 60, 70))
    cv.hline(cx - 22, cy - 8, 44, STEEL, 2)
    cv.disc(cx + 18, cy, 3, (60, 60, 70))
    cv.tri(cx - 6, cy + 4, cx + 6, cy + 4, x + w * 58 // 100,
           y + h * 62 // 100, (255, 240, 170))
    cv.disc(x + w * 58 // 100, y + h * 62 // 100, 5, (255, 240, 170))
    for kx in range(0, 100, 14):
        cv.disc(x + kx * w // 100, y + h * 90 // 100, 2, GOLD)


def scene_quake(cv, x, y, w, h):
    # The Andes shake: cracked ground, leaning houses, falling rock.
    cv.rect(x, y, w, h, (232, 214, 170))
    cv.disc(x + w * 82 // 100, y + h * 16 // 100, max(4, w // 16),
            (255, 236, 180))
    # mountain ridge
    cv.tri(x, y + h * 62 // 100, x + w * 26 // 100, y + h * 18 // 100,
           x + w * 52 // 100, y + h * 62 // 100, (90, 100, 110))
    cv.tri(x + w * 40 // 100, y + h * 62 // 100,
           x + w * 66 // 100, y + h * 10 // 100,
           x + w * 92 // 100, y + h * 62 // 100, (70, 80, 92))
    cv.tri(x + w * 20 // 100, y + h * 28 // 100,
           x + w * 26 // 100, y + h * 18 // 100,
           x + w * 32 // 100, y + h * 28 // 100, WHITE)
    # houses on a cracked street
    for bx, tilt in [(8, -2), (38, 3), (66, -3)]:
        bx0 = x + bx * w // 100
        cv.rect(bx0 + tilt, y + h * 62 // 100, w * 20 // 100,
                h * 22 // 100, (150, 120, 90))
        cv.tri(bx0 + tilt, y + h * 62 // 100,
               bx0 + tilt + w * 10 // 100, y + h * 52 // 100,
               bx0 + tilt + w * 20 // 100, y + h * 62 // 100, DARKRED)
    cv.rect(x, y + h * 84 // 100, w, h * 16 // 100, (110, 100, 84))
    zx = x + w * 30 // 100
    cv.line(zx, y + h * 84 // 100, zx + 8, y + h * 92 // 100, INK)
    cv.line(zx + 8, y + h * 92 // 100, zx - 4, y + h * 100 // 100, INK)
    zx = x + w * 70 // 100
    cv.line(zx, y + h * 84 // 100, zx - 8, y + h * 94 // 100, INK)
    cv.line(zx - 8, y + h * 94 // 100, zx + 6, y + h * 100 // 100, INK)
    for sx, sy in [(18, 24), (48, 16), (74, 22)]:
        cv.disc(x + sx * w // 100, y + sy * h // 100, 3, (120, 112, 100))


def scene_ship(cv, x, y, w, h):
    # A cargo ship in the Baltic under a drone swarm.
    cv.rect(x, y, w, h, (30, 60, 90))
    for sx, sy in [(12, 10), (38, 16), (66, 8), (88, 14), (24, 26)]:
        cv.disc(x + sx * w // 100, y + sy * h // 100, 2, WHITE)
    cv.rect(x, y + h * 64 // 100, w, h * 36 // 100, (16, 48, 80))
    for wy in range(y + h * 70 // 100, y + h, h * 9 // 100):
        cv.hline(x + w * 6 // 100, wy, w * 88 // 100, (90, 140, 180), 1)
    hx = x + w * 18 // 100
    cv.rect(hx, y + h * 46 // 100, w * 64 // 100, h * 18 // 100,
            (60, 66, 74))
    cv.rect(hx + w * 8 // 100, y + h * 34 // 100, w * 10 // 100,
            h * 12 // 100, (60, 66, 74))
    cv.rect(hx + w * 44 // 100, y + h * 38 // 100, w * 8 // 100,
            h * 8 // 100, (60, 66, 74))
    for cx in range(hx + 6, hx + w * 64 // 100 - 4, w * 8 // 100):
        cv.rect(cx, y + h * 50 // 100, 6, 5, (200, 170, 60))
    # drones: small crosses with a blast over the deck
    for dx, dy in [(30, 22), (58, 14), (82, 26)]:
        px = x + dx * w // 100
        py = y + dy * h // 100
        cv.hline(px - 5, py, 10, WHITE, 2)
        cv.vline(px, py - 5, 10, WHITE, 2)
        cv.disc(px, py, 2, RED)
    bx = x + w * 56 // 100
    by = y + h * 42 // 100
    cv.disc(bx, by, 9, ORANGE)
    cv.disc(bx, by, 5, (255, 220, 90))
    for ang in range(0, 360, 60):
        dx = int(15 * math.cos(math.radians(ang)))
        dy = int(15 * math.sin(math.radians(ang)))
        cv.line(bx, by, bx + dx, by + dy, (255, 220, 90))


def scene_barrage(cv, x, y, w, h):
    # Night city under a missile barrage, as in Kryvyi Rih.
    cv.rect(x, y, w, h, SKYNIGHT)
    for sx, sy in [(8, 8), (30, 20), (55, 6), (80, 16), (20, 34),
                   (65, 30), (90, 8), (42, 12), (72, 38), (15, 46)]:
        cv.disc(x + sx * w // 100, y + sy * h // 100,
                max(1, w // 200), WHITE)
    cv.rect(x, y + h * 62 // 100, w, h * 38 // 100, (24, 68, 130))
    for bx in (10, 40, 70):
        bx0 = x + bx * w // 100
        bw = w * 22 // 100
        cv.hline(bx0, y + h * 56 // 100, bw, WHITE, 2)
        for k in range(5):
            px = bx0 + k * bw // 4
            cv.vline(px, y + h * 56 // 100, h * 10 // 100, WHITE, 2)
        cv.line(bx0, y + h * 56 // 100, bx0 + bw // 2,
                y + h * 46 // 100, WHITE)
        cv.line(bx0 + bw // 2, y + h * 46 // 100, bx0 + bw,
                y + h * 56 // 100, WHITE)
    for ex, ey, r in [(28, 26, 9), (60, 18, 12), (84, 32, 8)]:
        cx = x + ex * w // 100
        cy = y + ey * h // 100
        cv.disc(cx, cy, r * w // 200 + 3, ORANGE)
        cv.disc(cx, cy, r * w // 300 + 2, (255, 220, 90))
        for ang in range(0, 360, 45):
            dx = int((r + 8) * w / 200 * math.cos(math.radians(ang)))
            dy = int((r + 8) * h / 200 * math.sin(math.radians(ang)))
            cv.line(cx, cy, cx + dx, cy + dy, (255, 220, 90))
    cv.line(x + w * 10 // 100, y + h * 8 // 100,
            x + w * 28 // 100, y + h * 24 // 100, WHITE)
    cv.line(x + w * 80 // 100, y + h * 6 // 100,
            x + w * 62 // 100, y + h * 20 // 100, WHITE)


def scene_border(cv, x, y, w, h):
    # A border crossing closes: barrier stripes and a stop sign.
    cv.rect(x, y, w, h, (214, 226, 210))
    cv.rect(x, y + h * 58 // 100, w, h * 30 // 100, (120, 120, 118))
    cv.hline(x, y + h * 72 // 100, w, WHITE, 3)
    for i in range(8):
        col = RED if i % 2 == 0 else WHITE
        cv.rect(x + w * (8 + i * 11) // 100, y + h * 34 // 100,
                w * 11 // 100, h * 12 // 100, col)
    cv.vline(x + w * 8 // 100, y + h * 46 // 100, h * 12 // 100, INK, 3)
    cv.vline(x + w * 90 // 100, y + h * 46 // 100, h * 12 // 100, INK, 3)
    cv.rect(x + w * 62 // 100, y + h * 10 // 100, w * 26 // 100,
            h * 20 // 100, WHITE)
    cv.frame(x + w * 62 // 100, y + h * 10 // 100, w * 26 // 100,
             h * 20 // 100, RED, 2)
    cv.rect(x + w * 30 // 100, y + h * 78 // 100, w * 40 // 100,
            h * 12 // 100, (40, 90, 60))
    cv.rect(x + w * 34 // 100, y + h * 70 // 100, w * 32 // 100,
            h * 8 // 100, (40, 90, 60))


def scene_summit(cv, x, y, w, h):
    # Shenzhen skyline at dusk, flags flying over the summit towers.
    cv.rect(x, y, w, h, (52, 44, 74))
    cv.disc(x + w * 80 // 100, y + h * 20 // 100, max(4, w // 18),
            (255, 226, 160))
    for bx, bw, bh, top in [(6, 16, 52, 0), (26, 18, 70, 1),
                            (48, 16, 58, 0), (68, 20, 78, 1),
                            (90, 8, 40, 0)]:
        bx0 = x + bx * w // 100
        cv.rect(bx0, y + h - h * bh // 100, w * bw // 100,
                h * bh // 100, (24, 24, 36))
        for wy in range(y + h - h * (bh - 8) // 100, y + h - 6,
                        h * 10 // 100):
            for wx in range(bx0 + 3, bx0 + w * bw // 100 - 4,
                            w * 6 // 100):
                cv.rect(wx, wy, 3, 4, (255, 220, 120))
        if top:
            cv.vline(bx0 + w * bw // 200, y + h - h * (bh + 10) // 100,
                     h * 10 // 100, WHITE, 1)
            cv.tri(bx0 + w * bw // 200, y + h - h * (bh + 10) // 100,
                   bx0 + w * bw // 200 + w * 8 // 100,
                   y + h - h * (bh + 7) // 100,
                   bx0 + w * bw // 200,
                   y + h - h * (bh + 4) // 100, RED)

def scene_vote(cv, x, y, w, h):
    # A ballot box with a ticked slip: coalition talks at the table.
    cv.rect(x, y, w, h, (226, 232, 244))
    cv.rect(x + w * 28 // 100, y + h * 34 // 100, w * 44 // 100,
            h * 52 // 100, NAVY)
    cv.rect(x + w * 38 // 100, y + h * 30 // 100, w * 24 // 100,
            h * 6 // 100, BLACK)
    cv.rect(x + w * 44 // 100, y + h * 12 // 100, w * 18 // 100,
            h * 18 // 100, WHITE)
    cv.frame(x + w * 44 // 100, y + h * 12 // 100, w * 18 // 100,
             h * 18 // 100, INK, 1)
    cv.line(x + w * 46 // 100, y + h * 22 // 100,
            x + w * 50 // 100, y + h * 27 // 100, RED)
    cv.line(x + w * 50 // 100, y + h * 27 // 100,
            x + w * 60 // 100, y + h * 14 // 100, RED)
    for kx in range(0, 100, 12):
        cv.disc(x + kx * w // 100, y + h * 88 // 100, 2, GOLD)


def scene_hospital(cv, x, y, w, h):
    # A hospital block under a red cross, patient ward below.
    cv.rect(x, y, w, h, (240, 232, 214))
    cv.tri(x + w * 18 // 100, y + h * 78 // 100,
           x + w * 50 // 100, y + h * 22 // 100,
           x + w * 82 // 100, y + h * 78 // 100, WHITE)
    cv.frame(x + w * 18 // 100, y + h * 22 // 100, w * 64 // 100,
             h * 56 // 100, INK, 2)
    cv.rect(x + w * 45 // 100, y + h * 34 // 100, w * 10 // 100,
            h * 26 // 100, RED)
    cv.rect(x + w * 40 // 100, y + h * 42 // 100, w * 20 // 100,
            h * 10 // 100, RED)
    cv.rect(x + w * 44 // 100, y + h * 78 // 100, w * 12 // 100,
            h * 16 // 100, (90, 70, 50))
    cv.disc(x + w * 14 // 100, y + h * 82 // 100, 4, TEAL)
    cv.disc(x + w * 86 // 100, y + h * 82 // 100, 4, TEAL)


def scene_climate(cv, x, y, w, h):
    # A warming globe between factories and a hot sun.
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + w * 84 // 100, y + h * 16 // 100, max(4, w // 18),
            (255, 214, 90))
    cx = x + w * 42 // 100
    cy = y + h * 52 // 100
    cv.disc(cx, cy, h * 34 // 100, (46, 130, 90))
    cv.rect(cx - h * 30 // 100, cy - h * 8 // 100, h * 22 // 100,
            h * 16 // 100, GREEN)
    cv.rect(cx + h * 2 // 100, cy + h * 4 // 100, h * 26 // 100,
            h * 12 // 100, (30, 90, 70))
    cv.rect(cx - h * 6 // 100, cy - h * 30 // 100, h * 10 // 100,
            h * 60 // 100, (30, 90, 70))
    for fx in (12, 78):
        fx0 = x + fx * w // 100
        cv.rect(fx0, y + h * 72 // 100, w * 8 // 100, h * 20 // 100, GREY)
        cv.rect(fx0 - 2, y + h * 64 // 100, w * 12 // 100, h * 8 // 100,
                GREY)
        cv.disc(fx0 + w * 4 // 100, y + h * 56 // 100, 5,
                (200, 200, 200))


def scene_protest(cv, x, y, w, h):
    # A street crowd with placards held high.
    cv.rect(x, y, w, h, (232, 228, 218))
    cv.rect(x, y + h * 70 // 100, w, h * 30 // 100, (150, 146, 138))
    for bx, bw, bh in [(6, 22, 46), (72, 20, 58)]:
        cv.rect(x + bx * w // 100, y + h - h * bh // 100,
                w * bw // 100, h * bh // 100, (120, 112, 100))
    # placards
    for px, py, col in [(22, 18, RED), (48, 12, NAVY), (74, 20, TEAL)]:
        px0 = x + px * w // 100
        py0 = y + py * h // 100
        cv.rect(px0, py0, w * 16 // 100, h * 14 // 100, col)
        cv.frame(px0, py0, w * 16 // 100, h * 14 // 100, INK, 1)
        cv.vline(px0 + w * 8 // 100, py0 + h * 14 // 100,
                 h * 22 // 100, INK, 2)
    # crowd heads
    for hx in range(10, 95, 11):
        cv.disc(x + hx * w // 100, y + h * 62 // 100, max(3, w // 30),
                (60, 50, 44))
        cv.rect(x + hx * w // 100 - 4, y + h * 68 // 100, 8,
                h * 12 // 100, (90, 80, 70))


def scene_rugby(cv, x, y, w, h):
    # A rugby pitch: posts, halfway line, and the oval ball.
    cv.rect(x, y, w, h, PITCH)
    cv.hline(x + w * 6 // 100, y + h * 50 // 100, w * 88 // 100, WHITE, 2)
    cv.ring(x + w * 50 // 100, y + h * 50 // 100, h * 16 // 100, WHITE)
    # goal posts at the top
    cv.vline(x + w * 42 // 100, y + h * 4 // 100, h * 22 // 100, WHITE, 3)
    cv.vline(x + w * 58 // 100, y + h * 4 // 100, h * 22 // 100, WHITE, 3)
    cv.hline(x + w * 42 // 100, y + h * 26 // 100, w * 16 // 100, WHITE, 3)
    # oval ball, low right
    bx = x + w * 68 // 100
    by = y + h * 70 // 100
    cv.disc(bx, by, max(4, w // 14), WHITE)
    cv.disc(bx, by, 3, BLACK)
    for dx, dy in [(-6, -2), (6, -3), (0, 6), (-5, 4), (6, 3)]:
        cv.disc(bx + dx, by + dy, 2, BLACK)
    cv.line(bx - 12, by - 8, bx + 12, by + 8, WHITE)


def scene_cricket(cv, x, y, w, h):
    # A cricket pitch: stumps, bat, and the red ball.
    cv.rect(x, y, w, h, PITCH)
    cv.rect(x + w * 38 // 100, y + h * 12 // 100, w * 24 // 100,
            h * 76 // 100, (196, 164, 110))
    for k in range(3):
        sx = x + w * (44 + k * 4) // 100
        cv.vline(sx, y + h * 18 // 100, h * 16 // 100, (255, 230, 120), 3)
    cv.hline(x + w * 42 // 100, y + h * 16 // 100, w * 14 // 100,
             (255, 230, 120), 2)
    cv.rect(x + w * 58 // 100, y + h * 52 // 100, w * 5 // 100,
            h * 26 // 100, (150, 100, 50))
    cv.rect(x + w * 56 // 100, y + h * 44 // 100, w * 9 // 100,
            h * 10 // 100, (150, 100, 50))
    cv.disc(x + w * 74 // 100, y + h * 70 // 100, max(3, w // 28), RED)
    cv.disc(x + w * 72 // 100, y + h * 68 // 100, 2, WHITE)
    cv.hline(x + w * 8 // 100, y + h * 88 // 100, w * 84 // 100, WHITE, 2)


def scene_f1(cv, x, y, w, h):
    # A race car under the lights on the Las Vegas Strip.
    cv.rect(x, y, w, h, (12, 12, 28))
    for lx in range(0, 100, 8):
        cv.disc(x + lx * w // 100, y + h * 10 // 100, 2, GOLD)
    cv.rect(x, y + h * 62 // 100, w, h * 24 // 100, (60, 60, 70))
    cv.hline(x, y + h * 62 // 100, w, WHITE, 2)
    cv.hline(x, y + h * 86 // 100, w, WHITE, 2)
    cx = x + w * 50 // 100
    cy = y + h * 72 // 100
    cv.rect(cx - w * 26 // 100, cy - h * 8 // 100, w * 52 // 100,
            h * 14 // 100, RED)
    cv.rect(cx - w * 8 // 100, cy - h * 16 // 100, w * 18 // 100,
            h * 10 // 100, DARKRED)
    for wx in (-22, 20):
        cv.disc(cx + wx * w // 100, cy + h * 8 // 100, max(3, w // 30),
                BLACK)
        cv.ring(cx + wx * w // 100, cy + h * 8 // 100, max(3, w // 30),
                STEEL)
    cv.line(cx + w * 26 // 100, cy, x + w, y + h * 40 // 100,
            (255, 240, 160))
    cv.line(cx + w * 26 // 100, cy + 2, x + w, y + h * 44 // 100,
            (255, 240, 160))


SCENES = {"GULF": scene_gulf, "RAID": scene_raid, "QUAKE": scene_quake,
          "SHIP": scene_ship, "BARRAGE": scene_barrage,
          "BORDER": scene_border, "SUMMIT": scene_summit,
          "VOTE": scene_vote, "HOSPITAL": scene_hospital,
          "CLIMATE": scene_climate, "PROTEST": scene_protest,
          "RUGBY": scene_rugby, "CRICKET": scene_cricket,
          "F1": scene_f1}
HERO_SCENES = ["GULF", "RAID", "QUAKE"]

# ---------------------------------------------------------------- layout
def count_by(items, idx):
    out = {}
    for it in items:
        out[it[idx]] = out.get(it[idx], 0) + 1
    return out


def build():
    cv = Canvas(W, H, PAPER)
    all_stories = [(h[3], h[4]) for h in HEROES]
    all_stories += [(l[3], l[4]) for l in LEADS]
    all_stories += [(b[1], b[2]) for b in BRIEFS]
    n = len(all_stories)
    reg = count_by(all_stories, 0)
    fld = count_by(all_stories, 1)

    cv.frame(4, 4, W - 8, H - 8, INK, 2)

    # masthead
    title = "THE WORLD IN ONE PICTURE"
    draw_text(cv, (W - text_w(title, 5)) // 2, 14, title, 5, INK)
    date = "SUNDAY 22 NOVEMBER 2026"
    draw_text(cv, (W - text_w(date, 3)) // 2, 56, date, 3, RED)
    sub = "ONE DAY - ONE PAGE - %d STORIES" % n
    draw_text(cv, (W - text_w(sub, 2)) // 2, 84, sub, 2, INK)
    draw_text(cv, 14, 84, "NO. 326", 2, GREY)
    draw_text(cv, W - 14 - text_w("MAKE.FUN DAILY", 2), 84,
              "MAKE.FUN DAILY", 2, GREY)
    cv.hline(8, 100, W - 16, INK, 2)

    # numbers strip: seven cells
    bw = 138
    for i, (label, value, note) in enumerate(NUMBERS):
        bx = 8 + i * (bw + 6)
        cv.frame(bx, 106, bw, 44, INK, 1)
        draw_text(cv, bx + (bw - text_w(label, 1)) // 2, 110, label, 1,
                  GREY)
        draw_text(cv, bx + (bw - text_w(value, 3)) // 2, 120, value, 3,
                  RED)
        draw_text(cv, bx + (bw - text_w(note, 1)) // 2, 142, note, 1, INK)

    # heroes
    hw = 330
    for i, (l1, l2, sublines, _r, _f) in enumerate(HEROES):
        hx = 8 + i * (hw + 8)
        hy = 156
        hh = 160
        cv.frame(hx, hy, hw, hh, INK, 2)
        SCENES[HERO_SCENES[i]](cv, hx + 2, hy + 2, hw - 4, 58)
        cv.hline(hx + 2, hy + 60, hw - 4, INK, 1)
        draw_text(cv, hx + 8, hy + 66, l1, 3, INK)
        draw_text(cv, hx + 8, hy + 93, l2, 3, INK)
        yy = hy + 124
        for sl in sublines:
            draw_text(cv, hx + 8, yy, sl, 2, RED)
            yy += 18

    # illustrated leads: two rows of six
    cw = 161
    for row in range(2):
        for col in range(6):
            k = row * 6 + col
            head, _deck, scene, _r, _f = LEADS[k]
            cx = 8 + col * (cw + 8)
            cy = 324 + row * 130
            cv.frame(cx, cy, cw, 122, INK, 1)
            SCENES[scene](cv, cx + 1, cy + 1, cw - 2, 54)
            cv.hline(cx + 1, cy + 55, cw - 2, INK, 1)
            draw_text(cv, cx + 5, cy + 58, scene, 1, RED)
            lines = wrap(head, 2, cw - 10)[:3]
            draw_lines(cv, cx + 5, cy + 68, lines, 2, INK, 17)

    # sketch world map with numbered pins
    mx, my, mw, mh = 8, 584, 640, 148
    cv.frame(mx, my, mw, mh, INK, 1)
    cell_w = mw // 48
    cell_h = mh // 24
    for r, rowstr in enumerate(MAP_ROWS):
        for c, ch in enumerate(rowstr):
            if ch == "#":
                cv.disc(mx + c * cell_w + cell_w // 2,
                        my + r * cell_h + cell_h // 2, 2, NAVY)
    for num, _name, fx, fy in MAP_PINS:
        px = mx + int(fx * mw)
        py = my + int(fy * mh)
        cv.disc(px, py, 7, RED)
        off = -5 if num >= 10 else -2
        draw_text(cv, px + off, py - 3, str(num), 1, WHITE)
    draw_text(cv, mx + 8, my + mh - 18,
              "1 SINALOA  2 PERU  3 BALTIC  4 KRYVYI RIH  5 POLAND  "
              "6 ESTONIA  7 KUWAIT  8 SHENZHEN", 1, INK)
    draw_text(cv, mx + 8, my + mh - 9,
              "9 ISRAEL  10 BRAZIL  11 FRANCE  12 TWICKENHAM  "
              "13 LAS VEGAS  14 BIHAR  15 WELLINGTON", 1, INK)

    # counts panel
    px0, py0, pw = 656, 584, 360
    cv.frame(px0, py0, pw, 148, INK, 1)
    draw_text(cv, px0 + 8, py0 + 6, "THE DAY IN NUMBERS", 2, INK)
    yy = py0 + 20
    for label, code in REGIONS:
        draw_text(cv, px0 + 8, yy, label, 1, INK)
        cnt = reg.get(code, 0)
        cv.rect(px0 + 108, yy + 1, cnt * 13, 5, TEAL)
        draw_text(cv, px0 + 108 + cnt * 13 + 5, yy, str(cnt), 1, INK)
        yy += 9
    yy += 2
    for label, code in FIELDS:
        draw_text(cv, px0 + 8, yy, label, 1, INK)
        cnt = fld.get(code, 0)
        cv.rect(px0 + 108, yy + 1, cnt * 13, 5, GOLD)
        draw_text(cv, px0 + 108 + cnt * 13 + 5, yy, str(cnt), 1, INK)
        yy += 9

    # briefs
    draw_text(cv, 8, 740, "MORE FROM THE DAY", 2, RED)
    cv.hline(8, 756, W - 16, INK, 1)
    cv.vline(512, 764, 224, GREY, 1)
    for i, (txt, _r, _f) in enumerate(BRIEFS):
        col = i // 16
        row = i % 16
        bx = 8 + col * 508
        by = 764 + row * 14
        cv.rect(bx, by + 4, 4, 4, RED)
        draw_text(cv, bx + 10, by, txt, 2, INK)

    # footer: date check
    cv.hline(8, 994, W - 16, INK, 1)
    draw_text(cv, 8, 1000,
              "NOT TODAY: THE ICJ MYANMAR RULING WAS 19 NOV - THE SHENZHEN "
              "TRILATERAL WAS 19 NOV - THE ANTHROPIC DEBUT WAS 19 NOV.",
              1, GREY)
    draw_text(cv, 8, 1010,
              "ALL %d STORIES HAPPENED OR WERE FIRST REPORTED ON SUNDAY "
              "22 NOVEMBER 2026." % n, 1, GREY)
    return cv


def main():
    cv = build()
    data = png_bytes(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as fh:
        fh.write(data)
    print("wrote", dst, len(data), "bytes", cv.w, "x", cv.h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
