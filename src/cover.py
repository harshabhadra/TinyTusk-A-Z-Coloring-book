"""Full-wrap paperback cover: back + spine + front with 0.125" bleed (KDP).
Usage: python3 src/cover.py -> cover.pdf (+ cover/cover_preview.png)

Assumed KDP values (confirm with KDP's cover calculator before upload):
  premium color, white paper: spine = pages x 0.002347 in; bleed 0.125 in; no spine text under 80 pages.
"""
import math, os, subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from layout import CAP, LETTER_FONT          # registers the fonts
from palette import PALETTE

PAGES = 30
TRIM_W, TRIM_H = 8.5, 11.0
BLEED = 0.125
SPINE = round(PAGES * 0.002347, 4)
W = BLEED + TRIM_W + SPINE + TRIM_W + BLEED
H = BLEED + TRIM_H + BLEED
PT = 72
SUBTITLE = "26 Cute Baby Animals to Copy, Color & Learn the Alphabet"
SAFE = 0.25                                       # text distance from trim / spine edges (brief)

BACK_X0, BACK_X1 = BLEED, BLEED + TRIM_W          # back trim area
SPINE_X0, SPINE_X1 = BACK_X1, BACK_X1 + SPINE
FRONT_X0, FRONT_X1 = SPINE_X1, SPINE_X1 + TRIM_W
TRIM_Y0, TRIM_Y1 = BLEED, BLEED + TRIM_H
SKY = HexColor("#AADEF4")                         # sampled from the front art
GRASS = HexColor("#9BC95F")
INK = HexColor("#212121")
FRONT_CX = (FRONT_X0 + FRONT_X1) / 2
BACK_CX = (BACK_X0 + BACK_X1) / 2


class Cover:
    def __init__(self, c):
        self.c = c

    def X(self, x): return x * PT
    def Y(self, y): return (H - y) * PT

    def text(self, s, x, y, font, size, color=INK, anchor="c"):
        c = self.c; c.setFillColor(color); c.setFont(font, size)
        {"c": c.drawCentredString, "l": c.drawString, "r": c.drawRightString}[anchor](self.X(x), self.Y(y), s)

    def outlined(self, s, cx, y, font, size, fills, stroke=INK, width=5):
        """Centred text, each character its own fill colour, thick dark outline under a clean fill."""
        c = self.c
        total = pdfmetrics.stringWidth(s, font, size) / PT
        for pass_ in ("stroke", "fill"):
            x = cx - total / 2
            for i, ch in enumerate(s):
                c.saveState()
                t = c.beginText(); t.setFont(font, size); t.setTextOrigin(self.X(x), self.Y(y))
                if pass_ == "stroke":
                    t.setTextRenderMode(1); c.setStrokeColor(stroke); c.setLineWidth(width); c.setLineJoin(1)
                else:
                    t.setTextRenderMode(0); c.setFillColor(fills[i % len(fills)])
                t.textOut(ch); c.drawText(t); c.restoreState()
                x += pdfmetrics.stringWidth(ch, font, size) / PT

    def rrect(self, x0, y0, x1, y1, r, fill=None, stroke=INK, width=2.5):
        c = self.c
        if fill is not None: c.setFillColor(fill)
        c.setStrokeColor(stroke); c.setLineWidth(width)
        c.roundRect(self.X(x0), self.Y(y1), (x1 - x0) * PT, (y1 - y0) * PT, r * PT,
                    stroke=1 if width else 0, fill=1 if fill is not None else 0)

    def badge(self, cx, cy, r, lines, fill):
        c = self.c
        c.setFillColor(fill); c.setStrokeColor(INK); c.setLineWidth(3)
        c.circle(self.X(cx), self.Y(cy), r * PT, stroke=1, fill=1)
        y = cy - sum(sz for _, _, sz in lines) * CAP / PT / 2 - 0.04 * (len(lines) - 1) / 2
        for s, font, sz in lines:
            y += sz * CAP / PT
            self.text(s, cx, y, font, sz)
            y += 0.06

    # ---------------------------------------------------------------------------------
    def background(self):
        c = self.c
        c.setFillColor(SKY); c.rect(0, 0, W * PT, H * PT, stroke=0, fill=1)        # back + spine sky
        # back: grassy hill along the bottom, with a few flowers (vector)
        p = c.beginPath(); p.moveTo(0, 0); p.lineTo(0, self.Y(9.35))
        for i in range(0, 41):
            x = BACK_X1 * i / 40 + 0.01
            p.lineTo(self.X(x), self.Y(9.35 - 0.22 * math.sin(math.pi * i / 40)))
        p.lineTo(self.X(SPINE_X1), self.Y(9.13)); p.lineTo(self.X(SPINE_X1), 0); p.close()
        c.setFillColor(GRASS); c.drawPath(p, stroke=0, fill=1)
        for fx, fy, col in ((0.9, 10.1, "Yellow"), (1.9, 10.6, "Pink"), (3.0, 10.0, "Yellow"),
                            (4.1, 10.55, "Pink"), (5.2, 10.05, "Yellow")):
            for k in range(5):
                a = math.radians(90 + 72 * k)
                c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(1.2)
                c.circle(self.X(fx + 0.1 * math.cos(a)), self.Y(fy - 0.1 * math.sin(a)), 0.08 * PT, stroke=1, fill=1)
            c.setFillColor(HexColor(PALETTE[col])); c.circle(self.X(fx), self.Y(fy), 0.065 * PT, stroke=1, fill=1)

    def front(self):
        c = self.c
        c.drawImage(ImageReader("cover/front_art_300dpi.png"), self.X(FRONT_X0), 0,
                    (W - FRONT_X0) * PT, H * PT)
        cx = FRONT_CX
        self.outlined("My First", cx, 0.97, "Fredoka-Bold", 50, [white], width=6)
        az = [HexColor(PALETTE[k]) for k in ("Red", "Orange", "Yellow", "Yellow", "Light green", "Dark blue")]
        self.outlined("A to Z", cx, 2.33, LETTER_FONT, 118, [az[0], white, az[1], az[2], white, az[4]], width=7)
        self.outlined("Animals", cx, 3.16, LETTER_FONT, 74, [HexColor(PALETTE["Purple"])], width=6)
        # pill: Copy Coloring Book
        pw = pdfmetrics.stringWidth("Copy Coloring Book", "Fredoka-Bold", 26) / PT + 0.7
        self.rrect(cx - pw / 2, 3.38, cx + pw / 2, 3.94, 0.28, fill=HexColor("#FFF3B0"), width=3)
        self.text("Copy Coloring Book", cx, 3.66 + 26 * CAP / PT / 2, "Fredoka-Bold", 26)
        # subtitle (dark text with a thin white outline so it stays readable over the art)
        self.outlined(SUBTITLE, cx, 4.3, "Fredoka-SemiBold", 16, [INK], stroke=white, width=3)
        # badges in the top corners of the sky
        self.badge(FRONT_X0 + SAFE + 0.72, TRIM_Y0 + SAFE + 0.72, 0.72,
                   [("Ages", "Fredoka-SemiBold", 17), ("3-8".replace("-", "–"), "Fredoka-Bold", 30)],
                   HexColor(PALETTE["Yellow"]))
        self.badge(FRONT_X1 - SAFE - 0.72, TRIM_Y0 + SAFE + 0.72, 0.72,
                   [("26", "Fredoka-Bold", 30), ("animals to", "Fredoka-SemiBold", 12), ("copy & color", "Fredoka-SemiBold", 12)],
                   HexColor(PALETTE["Pink"]))
        self.text("by TinyTusk", FRONT_X1 - SAFE, TRIM_Y1 - SAFE, "Fredoka-SemiBold", 15, color=INK, anchor="r")

    def back(self):
        c = self.c
        x0, x1 = BACK_X0 + SAFE + 0.15, BACK_X1 - SAFE - 0.15
        self.text("Copy, color & learn from A to Z!", BACK_CX, 1.05, "Fredoka-Bold", 27)
        self.rrect(x0, 1.35, x1, 5.05, 0.25, fill=white, width=2.5)
        blurb = ["Meet 26 cute baby animals, from a smiling Alligator",
                 "to a stripy Zebra! Every page has a big outline picture",
                 "to color, a small colored picture to copy, and the",
                 "letter in big hollow shapes to color too."]
        y = 1.85
        for line in blurb:
            self.text(line, BACK_CX, y, "Fredoka-Medium", 15); y += 0.3
        bullets = ["26 original baby animals, one for every letter",
                   "Big shapes and thick lines for little hands",
                   "“Check your colors” dots to match the crayons",
                   "A name page and a “Well done!” certificate",
                   "Large 8.5 × 11 in pages, for ages 3–8"]
        y += 0.15
        for b in bullets:
            c.setFillColor(HexColor(PALETTE["Orange"])); c.setStrokeColor(INK); c.setLineWidth(1.2)
            c.circle(self.X(x0 + 0.55), self.Y(y - 0.07), 0.07 * PT, stroke=1, fill=1)
            self.text(b, x0 + 0.75, y, "Fredoka-Medium", 14, anchor="l"); y += 0.3
        # sample pages
        tw = 1.6; th = tw * 11 / 8.5; gap = (x1 - x0 - 4 * tw) / 3
        for i, L in enumerate("AELP"):
            tx = x0 + i * (tw + gap); ty = 5.45
            c.setFillColor(HexColor("#7FB8D3")); c.rect(self.X(tx + 0.06), self.Y(ty + th + 0.06), tw * PT, th * PT, stroke=0, fill=1)
            c.drawImage(ImageReader(f"cover/thumb_{L}.png"), self.X(tx), self.Y(ty + th), tw * PT, th * PT)
            c.setStrokeColor(INK); c.setLineWidth(1.5); c.rect(self.X(tx), self.Y(ty + th), tw * PT, th * PT, stroke=1, fill=0)
        self.text("Inside: 26 letter pages like these", BACK_CX, 5.45 + th + 0.38, "Fredoka-SemiBold", 13)
        # barcode area (KDP prints the barcode here): white box, nothing else inside
        bx1, by1 = BACK_X1 - SAFE, TRIM_Y1 - SAFE
        c.setFillColor(white); c.rect(self.X(bx1 - 2.0), self.Y(by1), 2.0 * PT, 1.2 * PT, stroke=0, fill=1)
        self.text("TinyTusk", x0, TRIM_Y1 - SAFE - 0.05, "Fredoka-Bold", 16, anchor="l")


def build():
    os.makedirs("cover", exist_ok=True)
    c = canvas.Canvas("cover.pdf", pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setTitle("My First A to Z Animals Copy Coloring Book - cover"); c.setAuthor("TinyTusk")
    cv = Cover(c)
    cv.background(); cv.back(); cv.front()
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "60", "-singlefile", "cover.pdf", "cover/cover_preview"], check=True)
    print(f"cover.pdf  {W:.4f} x {H:.4f} in  (spine {SPINE} in for {PAGES} pages)")


if __name__ == "__main__":
    build()
