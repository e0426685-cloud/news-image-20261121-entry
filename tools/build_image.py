#!/usr/bin/env python3
"""Render the front page for Saturday 21 November 2026.

Draws a one-page newspaper digest (1024x1024 PNG) from the stories
below. Every story was reported on 21 November 2026. The drawing is
deterministic: fixed palette, fixed fonts, fixed layout, no
timestamps, no randomness.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "entry.png")

W, H = 1024, 1024
PAPER = (253, 251, 243)
INK = (17, 17, 17)
FAINT = (90, 86, 76)
RED = (163, 18, 18)
BLUE = (20, 58, 107)
RULE = (40, 38, 32)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, width, text, fnt, fill=INK, leading=1.28):
    """Draw wrapped paragraph, return y just below it."""
    size = fnt.size
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(size * leading)
    return y


def headline(draw, x, y, width, text, fnt, fill=INK, leading=1.04):
    size = fnt.size
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(size * leading)
    return y


def rule(draw, x, y, width, weight=2):
    draw.line([(x, y), (x + width, y)], fill=RULE, width=weight)
    return y + weight


def kicker(draw, x, y, text, color=RED, size=16):
    fnt = font(SANS_B, size)
    draw.text((x, y), text.upper(), font=fnt, fill=color)
    return y + size + 6


def skyline(draw, x, y, w, h):
    """Stylised night sky over south-east Poland; all marks stay inside."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 24, 46))
    for sx, sy, r in [(x + 40, y + 18, 2), (x + 130, y + 36, 2),
                      (x + 230, y + 14, 3), (x + 330, y + 32, 2),
                      (x + 430, y + 20, 2), (x + 520, y + 38, 2),
                      (x + 620, y + 16, 2), (x + 720, y + 34, 2)]:
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(240, 230, 180))
    # two missile arcs, bounded inside the panel, right of the flag label
    draw.arc([x + 380, y + 16, x + 620, y + h + 30], start=195, end=335,
             fill=(255, 200, 90), width=4)
    draw.arc([x + 620, y + 22, x + 860, y + h + 40], start=200, end=340,
             fill=(255, 220, 140), width=3)
    draw.ellipse([x + 602, y + 46, x + 614, y + 58], fill=(255, 210, 110))
    draw.ellipse([x + 842, y + 52, x + 852, y + 62], fill=(255, 220, 140))
    # ground line and Polish flag, with labels clear of the arcs
    gy = y + h - 10
    draw.line([(x, gy), (x + w, gy)], fill=(120, 130, 160), width=2)
    draw.rectangle([x + 24, gy - 36, x + 104, gy - 18], fill=(255, 255, 255))
    draw.rectangle([x + 24, gy - 18, x + 104, gy], fill=(220, 20, 60))
    draw.text((x + 116, gy - 34), "NOWY LIPOWIEC, POLAND",
              font=font(SANS_B, 14), fill=(235, 235, 235))
    draw.text((x + 116, gy - 16), "Two missiles and a drone came down",
              font=font(SANS, 14), fill=(200, 205, 220))
    # NATO compass star
    cx, cy = x + w - 52, y + 30
    draw.polygon([(cx, cy - 20), (cx + 6, cy - 6), (cx + 20, cy),
                  (cx + 6, cy + 6), (cx, cy + 20), (cx - 6, cy + 6),
                  (cx - 20, cy), (cx - 6, cy - 6)], fill=(180, 200, 235))
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(16, 24, 46))


def market_bars(draw, x, y, w, h):
    """Falling bars for the markets story; numbers are in the text."""
    draw.rectangle([x, y, x + w, y + h], fill=(245, 238, 226))
    vals = [0.85, 0.70, 0.58, 0.64, 0.44, 0.30]
    bw = w // len(vals)
    for i, v in enumerate(vals):
        bh = int((h - 16) * v)
        bx = x + i * bw + 8
        draw.rectangle([bx, y + h - 8 - bh, bx + bw - 16, y + h - 8],
                       fill=RED if i >= 4 else (120, 40, 40))


def climate_sun(draw, x, y, w, h):
    """Sun over a dry plain for the COP31 story."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 240, 228))
    draw.text((x + 8, y + 6), "ANTALYA, TURKIYE",
              font=font(SANS_B, 14), fill=(90, 70, 20))
    draw.ellipse([x + w // 2 - 24, y + 8, x + w // 2 + 24, y + 56],
                 fill=(224, 150, 40))
    draw.rectangle([x, y + h - 10, x + w, y + h - 6], fill=(150, 120, 60))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 30
    cw = W - 2 * mx

    # ---- masthead ----
    d.text((W // 2, 18), "THE WORLD TODAY", font=font(SERIF_B, 56),
           fill=INK, anchor="ma")
    rule(d, mx, 92, cw, 3)
    d.text((mx, 100), "SATURDAY 21 NOVEMBER 2026",
           font=font(SANS_B, 19), fill=RED)
    d.text((W - mx, 100), "ONE DAY  -  ONE IMAGE  -  THE WORLD IN A PAGE",
           font=font(SANS_B, 14), fill=FAINT, anchor="ra")
    rule(d, mx, 128, cw, 2)

    # ---- lead story ----
    y = 140
    y = kicker(d, mx, y, "Poland  -  Nato  -  Ukraine")
    y = headline(d, mx, y, cw, "RUSSIAN MISSILES LAND IN POLAND",
                 font(SERIF_B, 46))
    y = headline(d, mx, y + 2, cw,
                 "NATO calls it a grave violation; Warsaw says provocation",
                 font(SERIF, 22), fill=(50, 48, 42))
    y += 4
    skyline(d, mx, y, cw, 84)
    y += 92
    y = para(d, mx, y, cw,
             "Two Russian missiles and a suspected drone came down in south-east "
             "Poland early on Friday, during a huge Russian attack on Ukraine. "
             "Prime Minister Donald Tusk said it does not look like an accident: "
             "the weapons fell near allied war games. NATO chief Mark Rutte, due "
             "in Warsaw, called it a grave violation of Polish airspace. In "
             "Ukraine, the barrage of 400 drones and 110 missiles killed at "
             "least eight people.",
             font(SANS, 17), leading=1.28)
    y += 6
    rule(d, mx, y, cw, 2)
    y += 10

    # ---- second row: markets + climate ----
    half = (cw - 24) // 2
    y0 = y
    x2 = mx + half + 24
    y = kicker(d, mx, y, "Markets  -  New York")
    y = headline(d, mx, y, half, "WALL STREET SLUMPS",
                 font(SERIF_B, 26))
    market_bars(d, mx, y + 4, half, 64)
    y = para(d, mx, y + 76, half,
             "US stocks fell sharply on Friday. The S&P 500 dropped 3.7% and the "
             "Nasdaq fell 5.3%, both into correction territory, as Nvidia slid "
             "about 14% after reports that the SEC is probing its accounting.",
             font(SANS, 16), leading=1.28)
    y2 = kicker(d, x2, y0, "Climate  -  Antalya")
    y2 = headline(d, x2, y2, half, "COP31 INTO OVERTIME",
                  font(SERIF_B, 26))
    climate_sun(d, x2, y2 + 4, half, 64)
    y2 = para(d, x2, y2 + 76, half,
              "UN climate talks in Antalya ran past their scheduled close as "
              "nearly 200 nations split over a draft deal that drops all mention "
              "of fossil fuels. France and Panama led a bloc demanding a "
              "stronger accord on fossil fuels and finance.",
              font(SANS, 16), leading=1.28)
    y = max(y, y2) + 8
    rule(d, mx, y, cw, 2)
    y += 10

    # ---- third row: six short items in three columns ----
    colw = (cw - 48) // 3
    items = [
        ("The Hague  -  Justice",
         "MYANMAR: ACT NOW",
         "Rights groups pressed for action after the World Court found Myanmar "
         "committed genocide against the Rohingya."),
        ("India  -  Weather & markets",
         "AKVAN WEAKENS; NSE 5TH",
         "Cyclone Akvan weakened after crossing the Odisha coast. The NSE passed "
         "Nasdaq as the world's fifth-largest exchange."),
        ("Cyber  -  Banks",
         "BANKS HIT BY BREACH",
         "JPMorgan Chase, Visa and Mastercard said third-party vendors were hit "
         "in a cyberattack. Core networks were unaffected."),
        ("Washington  -  Tech & war",
         "BRING BACK HUANG",
         "President Trump urged Nvidia to bring back former chief Jensen Huang. "
         "His team wants a Ukraine peace deal by early January."),
        ("Sport  -  Cricket & chess",
         "INDIA FIGHT BACK",
         "India reached 159 for 1 in Wellington after Nicholls' 175 for New "
         "Zealand. Carlsen's gamble kept him above 2800."),
        ("Europe  -  Borders & Gulf",
         "ESTONIA SHUTS BORDER",
         "Estonia shut border crossings with Russia after suspected arson "
         "sabotage. A tanker was struck in the Strait of Hormuz."),
    ]
    top = y
    row_h = 112
    for i, (kick, head, body) in enumerate(items):
        cx = mx + (i % 3) * (colw + 24)
        cy = top + (i // 3) * row_h
        cy = kicker(d, cx, cy, kick, color=BLUE, size=14)
        cy = headline(d, cx, cy, colw, head, font(SERIF_B, 18))
        para(d, cx, cy + 2, colw, body, font(SANS, 14), leading=1.25)
    y = top + 2 * row_h + 4
    rule(d, mx, y, cw, 2)
    y += 8

    # ---- footer: also today ----
    y = para(d, mx, y, cw,
             "ALSO TODAY:  Hyundai unveils the 2027 Elantra at the Los Angeles "
             "Auto Show  -  A pill hailed as a breakthrough for pancreatic cancer "
             " -  Nepal PM Balendra Shah visits India on 22-23 November  -  US "
             "sanctions four Iranians over oil revenues.",
             font(SANS, 14), fill=(60, 58, 50), leading=1.25)
    assert y <= H - 40, "footer overflow: y=%d" % y
    rule(d, mx, H - 34, cw, 2)
    d.text((mx, H - 26), "THE WORLD TODAY  -  Saturday 21 November 2026  -  "
           "Every story above was reported on 21 November 2026.",
           font=font(SANS, 13), fill=FAINT)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    sys.exit(main())
