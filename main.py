#!/usr/bin/env python3
"""Round 2 entry: a clean modern newspaper front page for Sunday 22 November 2026.

Draws the whole page with the Python standard library only (zlib + struct
for the PNG encoder) and writes entry.png. Output is byte-identical on
every run: no time, no randomness, no network.
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (253, 247, 236)
INK = (26, 26, 24)
RED = (158, 27, 26)
NAVY = (31, 58, 86)
SLATE = (88, 94, 102)
TAN = (201, 191, 169)
LAND = (196, 184, 158)
OCEAN = (214, 226, 231)
LIGHT = (238, 231, 218)
BLUE = (70, 110, 140)
ORANGE = (206, 104, 40)
GREEN = (74, 110, 72)
GOLD = (176, 138, 52)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(buf, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


class Page:
    def __init__(self):
        self.buf = bytearray(W * H * 3)
        for i in range(W * H):
            self.buf[i * 3:i * 3 + 3] = bytes(PAPER)

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        for yy in range(y0, y1):
            base = (yy * W + x0) * 3
            row = bytes(c) * (x1 - x0)
            self.buf[base:base + len(row)] = row

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            d = r * r - (yy - cy) ** 2
            half = int(d ** 0.5) if d > 0 else 0
            self.rect(cx - half, yy, half * 2 + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            t = 1 - ((yy - cy) / ry) ** 2
            half = int(rx * t ** 0.5) if t > 0 else 0
            self.rect(cx - half, yy, half * 2 + 1, 1, c)

    def poly(self, pts, c):
        ys = sorted(set(p[1] for p in pts))
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.rect(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), 1, c)


# 5x7 bitmap font. '#' is ink, '.' is blank. Lowercase letters sit on rows
# 2-6 (x-height 5) with descenders reaching row 6.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", "01100", "01100"),
    ",": (".....", ".....", ".....", ".....", "01100", "00100", "01000"),
    ":": (".....", "01100", "01100", ".....", "01100", "01100", "....."),
    ";": (".....", "01100", "01100", ".....", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", ".....", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", ".....", "00100"),
    "-": (".....", ".....", ".....", "11111", ".....", ".....", "....."),
    "'": ("00100", "00100", "01000", ".....", ".....", ".....", "....."),
    '"': ("01010", "01010", ".....", ".....", ".....", ".....", "....."),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": (".....", "00100", "00100", "11111", "00100", "00100", "....."),
    "=": (".....", ".....", "11111", ".....", "11111", ".....", "....."),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "*": (".....", "10101", "01110", "11111", "01110", "10101", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "11111"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

FONT.update({
    "a": (".....", ".....", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": (".....", ".....", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": (".....", ".....", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": (".....", ".....", "01111", "10001", "10001", "01111", "00001"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", ".....", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", ".....", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": (".....", ".....", "11010", "10101", "10101", "10101", "10101"),
    "n": (".....", ".....", "11110", "10001", "10001", "10001", "10001"),
    "o": (".....", ".....", "01110", "10001", "10001", "10001", "01110"),
    "p": (".....", ".....", "11110", "10001", "10001", "11110", "10000"),
    "q": (".....", ".....", "01111", "10001", "10001", "01111", "00001"),
    "r": (".....", ".....", "10110", "11001", "10000", "10000", "10000"),
    "s": (".....", ".....", "01111", "10000", "01110", "00001", "11110"),
    "t": ("00100", "00100", "11110", "00100", "00100", "00100", "00110"),
    "u": (".....", ".....", "10001", "10001", "10001", "10011", "01101"),
    "v": (".....", ".....", "10001", "10001", "10001", "01010", "00100"),
    "w": (".....", ".....", "10001", "10101", "10101", "10101", "01010"),
    "x": (".....", ".....", "10001", "01010", "00100", "01010", "10001"),
    "y": (".....", ".....", "10001", "10001", "01010", "00100", "00100"),
    "z": (".....", ".....", "11111", "00010", "00100", "01000", "11111"),
})


def adv(s):
    return 5 * s + max(1, s // 2)


def text_w(s, txt):
    return len(txt) * adv(s)


def draw_text(pg, x, y, s, c, txt):
    a = adv(s)
    for ch in txt:
        g = FONT.get(ch)
        if g is None:
            x += a
            continue
        for r, row in enumerate(g):
            for col, bit in enumerate(row):
                if bit == "1":
                    pg.rect(x + col * s, y + r * s, s, s, c)
        x += a
    return x


def draw_center(pg, cx, y, s, c, txt):
    draw_text(pg, cx - text_w(s, txt) // 2, y, s, c, txt)


def wrap(txt, s, maxw):
    a = adv(s)
    per = max(1, maxw // a)
    words, lines, cur = txt.split(" "), [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if len(trial) <= per:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def block(pg, x, y, s, c, txt, maxw, leading=None):
    lead = leading if leading is not None else 7 * s + 4
    for ln in wrap(txt, s, maxw):
        draw_text(pg, x, y, s, c, ln)
        y += lead
    return y


# Simplified continent outlines as (lon, lat) points.
N_AMERICA = [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-130, 54),
             (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
             (-105, 20), (-97, 16), (-90, 14), (-83, 9), (-79, 9), (-81, 13),
             (-87, 21), (-91, 19), (-97, 26), (-93, 30), (-84, 30), (-81, 25),
             (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-65, 44), (-60, 47),
             (-55, 52), (-60, 55), (-65, 60), (-78, 62), (-85, 66), (-95, 69),
             (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 65), (-32, 68), (-25, 70),
             (-22, 76), (-30, 80), (-45, 80), (-58, 76), (-60, 70)]
S_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
             (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
             (-70, -54), (-66, -55), (-68, -50), (-65, -45), (-62, -41),
             (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-39, -17),
             (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4),
             (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-76, 10)]
AFRICA = [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36),
          (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (35, 28),
          (37, 22), (39, 18), (43, 12), (48, 11), (51, 10), (46, 5),
          (42, 0), (40, -5), (40, -10), (36, -18), (33, -26), (28, -33),
          (20, -35), (17, -32), (15, -27), (12, -18), (13, -12), (12, -6),
          (9, 4), (4, 6), (-3, 5), (-8, 5), (-13, 8)]
EURASIA = [(-10, 36), (-9, 43), (-2, 44), (-4, 48), (-1, 50), (2, 51),
           (5, 53), (8, 55), (10, 57), (8, 58), (5, 60), (5, 62), (10, 64),
           (13, 66), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68),
           (45, 68), (50, 69), (55, 69), (60, 69), (65, 70), (70, 71),
           (75, 72), (80, 73), (85, 74), (90, 75), (100, 76), (110, 74),
           (120, 73), (130, 72), (140, 72), (150, 70), (160, 70), (170, 67),
           (178, 65), (178, 62), (170, 60), (162, 60), (158, 55), (155, 60),
           (150, 60), (145, 59), (142, 55), (140, 50), (138, 45), (135, 43),
           (130, 42), (127, 40), (126, 38), (122, 38), (120, 35), (122, 30),
           (120, 28), (115, 23), (110, 20), (108, 18), (105, 10), (103, 8),
           (100, 8), (98, 10), (95, 15), (92, 16), (90, 22), (88, 22),
           (86, 20), (83, 18), (80, 15), (77, 8), (75, 12), (73, 16),
           (70, 20), (68, 23), (66, 25), (62, 25), (58, 26), (56, 27),
           (52, 26), (50, 29), (48, 30), (44, 29), (40, 28), (38, 25),
           (35, 29), (34, 28), (32, 29), (30, 31), (27, 37), (25, 37),
           (22, 37), (20, 39), (18, 40), (15, 40), (12, 44), (10, 44),
           (8, 44), (6, 43), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
           (1, 51), (-2, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
         (141, 41), (142, 44), (140, 45), (139, 42), (137, 38), (135, 35),
         (133, 34), (131, 32)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]
BORNEO = [(109, 1), (110, -2), (113, -3), (117, -1), (119, 1), (117, 4),
          (114, 4), (110, 3)]
SUMATRA = [(95, 5), (98, 3), (100, 0), (103, -3), (105, -5), (104, -6),
           (102, -4), (100, -1), (97, 3)]
JAVA = [(105, -6), (108, -7), (112, -7), (114, -8), (111, -7), (107, -7)]
NEW_GUINEA = [(131, -1), (135, -2), (138, -4), (141, -5), (145, -7),
              (148, -9), (146, -8), (142, -8), (138, -7), (135, -4),
              (132, -2)]
MADAGASCAR = [(-44, -16), (-43, -20), (-44, -25), (-47, -25), (-50, -16),
              (-49, -13), (-47, -14)]
PHILIPPINES = [(120, 18), (121, 16), (122, 14), (121, 11), (123, 10),
               (122, 13)]
CONTINENTS = [N_AMERICA, GREENLAND, S_AMERICA, AFRICA, EURASIA, BRITAIN,
              JAPAN, AUSTRALIA, BORNEO, SUMATRA, JAVA, NEW_GUINEA,
              MADAGASCAR, PHILIPPINES]


def draw_map(pg, mx, my, mw, mh):
    pg.rect(mx, my, mw, mh, OCEAN)
    pg.rect(mx, my, mw, 2, INK)
    pg.rect(mx, my + mh - 2, mw, 2, INK)
    pg.rect(mx, my, 2, mh, INK)
    pg.rect(mx + mw - 2, my, 2, mh, INK)
    sx = mw / 360.0
    sy = mh / 120.0
    for land in CONTINENTS:
        pts = []
        for lon, lat in land:
            pts.append((mx + int((lon + 170) * sx),
                        my + int((75 - lat) * sy)))
        pg.poly(pts, LAND)
    return sx, sy


def draw_pin(pg, mx, my, sx, sy, lon, lat, num, dx=0, dy=0):
    tx = mx + int((lon + 170) * sx)
    ty = my + int((75 - lat) * sy)
    cx, cy = tx + dx, ty + dy
    if dx or dy:
        pg.line(tx, ty, cx, cy, RED, 2)
    pg.circle(cx, cy, 10, (255, 255, 255))
    pg.circle(cx, cy, 9, RED)
    draw_center(pg, cx, cy - 4, 1, (255, 255, 255), str(num))
    return cx, cy


def illo_gulf(pg, x, y, w, h):
    pg.rect(x, y, w, h, NAVY)
    pg.rect(x, y + h - 16, w, 16, (24, 44, 66))
    pg.rect(x + 8, y + h - 34, 34, 18, SLATE)
    pg.rect(x + 48, y + h - 30, 22, 14, SLATE)
    pg.rect(x + 76, y + h - 38, 16, 22, SLATE)
    pg.rect(x + 100, y + h - 28, 26, 12, SLATE)
    pg.rect(x + 132, y + h - 32, 30, 16, SLATE)
    pg.rect(x + 168, y + h - 26, 24, 10, SLATE)
    pg.rect(x + 198, y + h - 36, 18, 20, SLATE)
    pg.rect(x + 222, y + h - 30, 28, 14, SLATE)
    pg.rect(x + 256, y + h - 34, 22, 18, SLATE)
    for tx, ty in [(30, 8), (120, 4), (210, 10), (270, 6)]:
        pg.circle(x + tx, y + ty, 2, (255, 255, 255))
    pg.line(x + 20, y + h - 34, x + 90, y + 12, (255, 255, 255), 2)
    pg.line(x + 120, y + h - 30, x + 180, y + 8, (255, 255, 255), 2)
    pg.line(x + 220, y + h - 36, x + 268, y + 14, (255, 255, 255), 2)
    for cx, cy in [(90, 12), (180, 8), (268, 14)]:
        pg.circle(x + cx, y + cy, 4, ORANGE)
        pg.circle(x + cx, y + cy, 2, (255, 220, 120))
    pg.line(x + 84, y + 6, x + 96, y + 18, ORANGE, 2)
    pg.line(x + 96, y + 6, x + 84, y + 18, ORANGE, 2)


def illo_cop(pg, x, y, w, h):
    pg.rect(x, y, w, h, (222, 226, 220))
    pg.rect(x, y + h - 12, w, 12, (178, 172, 158))
    pg.ellipse(x + w // 2, y + 28, w // 2 - 14, 9, (122, 84, 52))
    pg.ellipse(x + w // 2, y + 26, w // 2 - 14, 9, (146, 104, 64))
    for i, fc in enumerate([RED, BLUE, GREEN, GOLD, NAVY, ORANGE]):
        fx = x + 18 + i * 46
        pg.rect(fx, y + 3, 26, 11, fc)
        pg.vline(fx + 26, y + 3, 11, INK, 2)
    for i in range(7):
        cx = x + 24 + i * 40
        pg.rect(cx, y + 38, 26, 6, NAVY)
    pg.rect(x + w // 2 - 16, y + 21, 32, 11, (255, 255, 255))
    draw_center(pg, x + w // 2, y + 22, 2, RED, "1.5C")


def illo_vote(pg, x, y, w, h):
    pg.rect(x, y, w, h, (226, 232, 236))
    for i, bh in enumerate([12, 18, 14, 20, 16, 19, 13]):
        bx = x + 12 + i * 40
        pg.rect(bx, y + h - 16 - bh, 26, bh, SLATE)
        pg.rect(bx + 5, y + h - 22 - bh + 6, 6, 5, (255, 255, 255))
    pg.circle(x + w - 30, y + 10, 8, GOLD)
    pg.rect(x + w // 2 - 40, y + h - 16, 80, 14, RED)
    pg.rect(x + w // 2 - 40, y + h - 18, 80, 3, (120, 20, 20))
    pg.rect(x + w // 2 - 10, y + h - 30, 20, 13, (255, 255, 255))
    pg.line(x + w // 2 - 7, y + h - 22, x + w // 2 - 2, y + h - 18, INK, 2)
    pg.line(x + w // 2 - 2, y + h - 18, x + w // 2 + 7, y + h - 27, INK, 2)


MX = 28
CW = 968

HERO = [
    ("Gulf: Strikes", "Iran hits US bases in the Gulf",
     "Iran fired missiles and drones at US sites in Kuwait and Bahrain. "
     "US command says defences stopped them.",
     "Reuters, AP", "gulf"),
    ("Climate: COP31", "COP31 nears a deal in Antalya",
     "Two days over time, the president tabled a text he says all sides "
     "can accept, for approval on Sunday.",
     "Reuters", "cop"),
    ("Hong Kong: Vote", "Hong Kong votes for 723 seats",
     "Polls opened at 9am for 723 seats on the Election Committee, which "
     "picks the next chief executive.",
     "China Daily", "vote"),
]

SECOND = [
    ("Myanmar: Quake", "Quake of 4.1 shakes Myanmar",
     "A 4.1 quake struck early on Sunday.", "ANI"),
    ("UAE: Visit", "UAE meets US security chief",
     "UAE president receives US security chief.", "ANI, WAM"),
    ("Finland: Fire", "Russian ship hit by drone",
     "Russian ship burned in the Gulf of Finland.", "ANI"),
    ("Israel: Politics", "Eisenkot opens talks with Likud",
     "Yashar chief Eisenkot invited Likud to talks.", "ANI"),
    ("Ukraine: NATO", "Zelenskyy: NATO call",
     "Zelenskyy: NATO is the clearest guarantee.", "ANI"),
]

BRIEFS = [
    "Tehran: US blockade is hostile (ANI)",
    "Araghchi: Hormuz can reopen (ANI)",
    "Envoy recalls India's 1971 role (ANI)",
    "Cummins keeps Test captaincy (Jagran)",
    "Jeddah halt runs to Nov 24 (Jagran)",
    "William's forest staff plan (Jagran)",
    "ICMR seals 100 tech transfers (Jagran)",
    "Japan to train in India first (Jagran)",
    "Crude oil futures fall over 3% (Jagran)",
    "Estonia closure rush begins (Reuters)",
    "Missiles downed over Riyadh (Coalition)",
    "Newcastle hold Arsenal 2-2 (Times)",
    "Leeds thrash Chelsea 4-1 (Times)",
    "Ladakh 70% poll turnout (Dailyworld)",
    "Nadal joins Real board (Dailyworld)",
    "Cricketer Chahal joins BJP (Vanguard)",
    "India's H5N1 chicken vaccine (Vanguard)",
    "DGCA tightens SpiceJet watch (Vanguard)",
    "Hockey coach Bhangu dies at 86 (Jagran)",
    "Advani wins snooker opener (Jagran)",
    "India 486/4, lead NZ by 118 (Jagran)",
    "Adani Ports buys Evos (Sunvilla)",
    "SCO dialogue sessions in Delhi (AIR)",
    "Chandigarh polls on Dec 23 (Sunvilla)",
    "Bagheera missiles fired (Sunvilla)",
    "Zelenskyy calls Modi (Sunvilla)",
    "Russia eyes India energy (Sunvilla)",
]

STATS = [
    ("14", "COP31 day", "in Antalya"),
    ("8", "US sites Iran", "claims it hit"),
    ("5,700", "Hong Kong", "voters"),
    ("856", "candidates", "for 723 seats"),
    ("4.1", "Myanmar quake", "magnitude"),
    ("3", "missiles", "shot down"),
]

PINS = [
    (50.5, 26.2, 0, 16), (30.7, 36.9, -16, 6), (114.2, 22.3, 0, 0),
    (96.2, 19.7, 0, 0), (54.4, 24.5, 0, 0), (24.9, 60.2, -16, -2),
    (34.8, 32.1, 10, 12), (30.5, 50.4, 0, -12), (51.4, 35.7, -12, -14),
    (56.3, 27.0, 16, 8), (77.2, 28.6, 0, 0), (151.2, -33.9, 0, 0),
    (39.2, 21.5, 0, 0),
]

PIN_KEY = [
    "1 Bahrain, 2 Antalya",
    "3 Hong Kong, 4 Myanmar",
    "5 Abu Dhabi, 6 Finland",
    "7 Tel Aviv, 8 Kyiv",
    "9 Tehran, 10 Hormuz",
    "11 Delhi, 12 Sydney",
    "13 Jeddah",
]

DATE_CHECK = (
    "Date check - left out, not Sunday's news: Peru quake M6.9 "
    "(Fri 20 Nov, USGS); El Chapo Isidro seized (Fri night, Reuters); "
    "EU-Indonesia deal signed (Sat, Reuters); Ranchi flights cut "
    "(Sat, PTI); Trump, Xi and Putin met (Thu, AP); UN killer-robot "
    "talks ended (Sat, AP)."
)

SOURCES = (
    "Sources: Reuters, AP, ANI, China Daily, Hong Kong REO, PTI, USGS, "
    "Euronews, The Times, Jagran, AIR, Vanguard, Sunvilla, Dailyworld, "
    "Coalition."
)

N_STORIES = 3 + len(SECOND) + len(BRIEFS)


def badge(pg, x, y, num):
    pg.rect(x, y, 18, 18, RED)
    draw_text(pg, x + 4, y + 2, 2, (255, 255, 255), str(num))


def build():
    pg = Page()
    y = 12
    # Masthead kicker line.
    draw_text(pg, MX, y, 2, RED, "The World in One Day")
    right = "%d stories - Every one dated Sunday 22 November 2026" % N_STORIES
    draw_text(pg, MX + CW - text_w(2, right), y, 2, INK, right)
    y += 18
    draw_text(pg, MX, y, 5, INK, "Sunday 22 November 2026")
    y += 38
    draw_text(pg, MX, y, 2, INK,
              "Iran strikes US bases in the Gulf, COP31 nears a deal, "
              "and Hong Kong votes.")
    y += 18
    pg.hline(MX, y, CW, INK, 3)
    y += 4
    pg.hline(MX, y, CW, INK, 1)
    y += 8
    # Stat strip.
    bw = 156
    for i, (num, l1, l2) in enumerate(STATS):
        bx = MX + i * 162
        pg.rect(bx, y, bw, 56, LIGHT)
        pg.rect(bx, y, bw, 2, RED)
        draw_center(pg, bx + bw // 2, y + 5, 3, INK, num)
        draw_center(pg, bx + bw // 2, y + 26, 2, INK, l1)
        draw_center(pg, bx + bw // 2, y + 42, 2, SLATE, l2)
    y += 56
    y += 6
    # Hero row.
    hw = 312
    hero_top = y
    for i, (kick, head, summ, src, kind) in enumerate(HERO):
        hx = MX + i * (hw + 16)
        badge(pg, hx, y, i + 1)
        draw_text(pg, hx + 24, y + 2, 2, RED, kick)
        hy = y + 22
        for ln in wrap(head, 4, hw):
            draw_text(pg, hx, hy, 4, INK, ln)
            hy += 30
        hy += 3
        if kind == "gulf":
            illo_gulf(pg, hx, hy, hw, 44)
        elif kind == "cop":
            illo_cop(pg, hx, hy, hw, 44)
        else:
            illo_vote(pg, hx, hy, hw, 44)
        hy += 44 + 4
        hy = block(pg, hx, hy, 2, INK, summ, hw, 16)
        hy += 2
        draw_text(pg, hx, hy, 2, SLATE, "Source: " + src)
    y = hero_top + 248
    pg.hline(MX, y, CW, INK, 1)
    y += 8
    # Second row.
    sw = 185
    for i, (kick, head, summ, src) in enumerate(SECOND):
        sx = MX + i * (sw + 10)
        draw_text(pg, sx, y, 2, RED, kick)
        sy = y + 16
        for ln in wrap(head, 2, sw):
            draw_text(pg, sx, sy, 2, INK, ln)
            sy += 16
        sy += 2
        sy = block(pg, sx, sy, 2, INK, summ, sw, 16)
        sy += 2
        draw_text(pg, sx, sy, 2, SLATE, "Source: " + src)
    y += 130
    pg.hline(MX, y, CW, INK, 1)
    y += 6
    # Map panel.
    map_y = y
    draw_text(pg, MX, y, 3, INK, "Where Sunday happened")
    y += 24
    mx, my, mw, mh = MX, y, 560, 108
    sx, sy = draw_map(pg, mx, my, mw, mh)
    for i, (lon, lat, dx, dy) in enumerate(PINS):
        draw_pin(pg, mx, my, sx, sy, lon, lat, i + 1, dx, dy)
    kx = MX + 580
    draw_text(pg, kx, map_y + 24, 2, RED, "Numbered pins: stories 1-13")
    ky = map_y + 44
    for ln in PIN_KEY:
        draw_text(pg, kx, ky, 2, INK, ln)
        ky += 15
    y = map_y + 130
    pg.hline(MX, y, CW, INK, 1)
    y += 6
    # Also section.
    draw_text(pg, MX, y, 3, INK,
              "Also on Sunday 22 November - 27 more stories")
    y += 22
    half = (len(BRIEFS) + 1) // 2
    for col in range(2):
        cx = MX + col * 492
        cy = y
        for j, txt in enumerate(BRIEFS[col * half:(col + 1) * half]):
            num = 14 + col * half + j
            draw_text(pg, cx, cy, 2, INK, "%d. %s" % (num, txt))
            cy += 15
    y += half * 15 + 4
    pg.hline(MX, y, CW, INK, 1)
    y += 6
    # Date check footer.
    y = block(pg, MX, y, 2, RED, DATE_CHECK, CW, 15)
    y += 3
    y = block(pg, MX, y, 2, SLATE, SOURCES, CW, 15)
    print("final y:", y, "stories:", N_STORIES)
    return pg


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if len(sys.argv) > 1:
        path = sys.argv[1]
    elif outdir:
        path = os.path.join(outdir, "entry.png")
    else:
        path = "entry.png"
    pg = build()
    save_png(pg.buf, path)
    print("wrote", path)


if __name__ == "__main__":
    main()
