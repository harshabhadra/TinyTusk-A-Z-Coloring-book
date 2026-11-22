"""Full-wrap paperback cover for the ABC tracing workbook: back + spine + front, 0.125 in bleed.
Reuses the coloring book's front art (cover/front_art_300dpi.png) so the two books look like one series.
Usage: python3 My-First-ABC-Letter-Tracing-Workbook/src/cover.py -> My-First-ABC-Letter-Tracing-Workbook/cover.pdf (+ My-First-ABC-Letter-Tracing-Workbook/cover/cover_preview.png)

Assumed KDP values (confirm with KDP's cover calculator before upload):
  black & white interior, white paper: spine = pages x 0.002252 in; bleed 0.125 in; no spine text under 80 pages.
"""
import math, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(os.path.dirname(HERE)), "src")]
from reportlab.pdfgen import canvas                 # noqa: E402
from reportlab.lib.colors import HexColor, white    # noqa: E402
from reportlab.pdfbase import pdfmetrics            # noqa: E402
from reportlab.lib.utils import ImageReader         # noqa: E402
import layout                                       # noqa: E402 (fonts, chdir to repo root)
from layout import CAP                              # noqa: E402
from palette import PALETTE                         # noqa: E402
import strokes                                      # noqa: E402

PAGES = 60
TRIM_W, TRIM_H, BLEED = 8.5, 11.0, 0.125
SPINE = round(PAGES * 0.002252, 4)
W = BLEED + TRIM_W + SPINE + TRIM_W + BLEED
H = BLEED + TRIM_H + BLEED
PT = 72
SAFE = 0.25
BACK_X0, BACK_X1 = BLEED, BLEED + TRIM_W
SPINE_X1 = BACK_X1 + SPINE
FRONT_X0, FRONT_X1 = SPINE_X1, SPINE_X1 + TRIM_W
TRIM_Y1 = BLEED + TRIM_H
SKY, GRASS, INK = HexColor("#AADEF4"), HexColor("#9BC95F"), HexColor("#212121")
FRONT_CX, BACK_CX = (FRONT_X0 + FRONT_X1) / 2, (BACK_X0 + BACK_X1) / 2
OUT = "My-First-ABC-Letter-Tracing-Workbook"
SUBTITLE = "Trace, Write & Color the Alphabet with 26 Cute Baby Animals"


class Cover:
    def __init__(self, c): self.c = c
    def X(self, x): return x * PT
    def Y(self, y): return (H - y) * PT

    def text(self, s, x, y, font, size, color=INK, anchor="c"):
        c = self.c; c.setFillColor(color); c.setFont(font, size)
        {"c": c.drawCentredString, "l": c.drawString, "r": c.drawRightString}[anchor](self.X(x), self.Y(y), s)

    def outlined(self, s, cx, y, font, size, fills, stroke=INK, width=5):
        c = self.c
        total = pdfmetrics.stringWidth(s, font, size) / PT
        for pass_ in ("stroke", "fill"):
            x = cx - total / 2
            for i, ch in enumerate(s):
                c.saveState(); t = c.beginText(); t.setFont(font, size); t.setTextOrigin(self.X(x), self.Y(y))
                if pass_ == "stroke":
                    t.setTextRenderMode(1); c.setStrokeColor(stroke); c.setLineWidth(width); c.setLineJoin(1)
                else:
                    t.setTextRenderMode(0); c.setFillColor(fills[i % len(fills)])
                t.textOut(ch); c.drawText(t); c.restoreState()
                x += pdfmetrics.stringWidth(ch, font, size) / PT

    def rrect(self, x0, y0, x1, y1, r, fill=None, width=2.5):
        c = self.c
        if fill is not None: c.setFillColor(fill)
        c.setStrokeColor(INK); c.setLineWidth(width)
        c.roundRect(self.X(x0), self.Y(y1), (x1 - x0) * PT, (y1 - y0) * PT, r * PT,
                    stroke=1 if width else 0, fill=1 if fill is not None else 0)

    def badge(self, cx, cy, r, lines, fill):
        c = self.c
        c.setFillColor(fill); c.setStrokeColor(INK); c.setLineWidth(3)
        c.circle(self.X(cx), self.Y(cy), r * PT, stroke=1, fill=1)
        y = cy - sum(sz for _, _, sz in lines) * CAP / PT / 2 - 0.04 * (len(lines) - 1) / 2
        for s, font, sz in lines:
            y += sz * CAP / PT; self.text(s, cx, y, font, sz); y += 0.06

    def tracing_letter(self, ch, x, base, u, color):
        """Fat coloured stroke letter with a dark outline and a white dashed centre line (like a tracing page)."""
        c = self.c
        for col, lw, dash in ((INK, u * PT * 0.42, None), (color, u * PT * 0.32, None), (white, u * PT * 0.06, (8, 9))):
            c.saveState(); c.setStrokeColor(col); c.setFillColor(col); c.setLineWidth(lw); c.setLineCap(1); c.setLineJoin(1)
            if dash: c.setDash(*dash)
            for pts, is_dot in strokes.polylines(ch):
                P = [(self.X(x + gx * u), self.Y(base - gy * u)) for gx, gy in pts]
                if is_dot:
                    c.circle(*P[0], lw / 2, stroke=0, fill=1); continue
                p = c.beginPath(); p.moveTo(*P[0])
                for q in P[1:]: p.lineTo(*q)
                c.drawPath(p, stroke=1, fill=0)
            c.restoreState()

    def background(self):
        c = self.c
        c.setFillColor(SKY); c.rect(0, 0, W * PT, H * PT, stroke=0, fill=1)
        p = c.beginPath(); p.moveTo(0, 0); p.lineTo(0, self.Y(9.35))
        for i in range(41):
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
        c.drawImage(ImageReader("cover/front_art_300dpi.png"), self.X(FRONT_X0), 0, (W - FRONT_X0) * PT, H * PT)
        cx = FRONT_CX
        self.outlined("My First", cx, 1.0, "Fredoka-Bold", 48, [white], width=6)
        # big ABC drawn as tracing letters
        u = 0.62; gap = 0.42
        ws = [strokes.width(ch) * u for ch in "ABC"]
        x = cx - (sum(ws) + 2 * gap) / 2
        for ch, wd, col in zip("ABC", ws, ("Red", "Orange", "Light green")):
            self.tracing_letter(ch, x, 2.45, u, HexColor(PALETTE[col])); x += wd + gap
        self.outlined("Letter Tracing", cx, 3.32, layout.LETTER_FONT, 62, [HexColor(PALETTE["Purple"])], width=6)
        pw = pdfmetrics.stringWidth("Workbook", "Fredoka-Bold", 26) / PT + 0.8
        self.rrect(cx - pw / 2, 3.5, cx + pw / 2, 4.06, 0.28, fill=HexColor("#FFF3B0"), width=3)
        self.text("Workbook", cx, 3.78 + 26 * CAP / PT / 2, "Fredoka-Bold", 26)
        self.outlined(SUBTITLE, cx, 4.42, "Fredoka-SemiBold", 15, [INK], stroke=white, width=3)
        self.badge(FRONT_X0 + SAFE + 0.72, BLEED + SAFE + 0.72, 0.72,
                   [("Ages", "Fredoka-SemiBold", 17), ("3–5", "Fredoka-Bold", 30)], HexColor(PALETTE["Yellow"]))
        self.badge(FRONT_X1 - SAFE - 0.72, BLEED + SAFE + 0.72, 0.72,
                   [("60", "Fredoka-Bold", 30), ("pages of", "Fredoka-SemiBold", 12), ("practice", "Fredoka-SemiBold", 12)],
                   HexColor(PALETTE["Pink"]))
        self.text("by TinyTusk", FRONT_X1 - SAFE, TRIM_Y1 - SAFE, "Fredoka-SemiBold", 15, anchor="r")

    def back(self, thumbs):
        c = self.c
        x0, x1 = BACK_X0 + SAFE + 0.15, BACK_X1 - SAFE - 0.15
        self.text("Trace, write & color from A to Z!", BACK_CX, 1.05, "Fredoka-Bold", 27)
        self.rrect(x0, 1.35, x1, 5.05, 0.25, fill=white)
        blurb = ["Little hands learn their letters with 26 cute baby",
                 "animals! Each letter gets two pages: big dashed letters",
                 "with numbered start dots and arrows, rows of practice,",
                 "the animal's name to trace, and a picture to color."]
        y = 1.85
        for line in blurb:
            self.text(line, BACK_CX, y, "Fredoka-Medium", 15); y += 0.3
        bullets = ["Uppercase and lowercase, A to Z",
                   "Start dots, stroke numbers and arrows",
                   "Pencil warm-ups: lines, zigzags, waves and loops",
                   "Trace-the-word and find-the-letter games",
                   "Large 8.5 × 11 in pages, for ages 3–5"]
        y += 0.15
        for b in bullets:
            c.setFillColor(HexColor(PALETTE["Orange"])); c.setStrokeColor(INK); c.setLineWidth(1.2)
            c.circle(self.X(x0 + 0.55), self.Y(y - 0.07), 0.07 * PT, stroke=1, fill=1)
            self.text(b, x0 + 0.75, y, "Fredoka-Medium", 14, anchor="l"); y += 0.3
        tw = 1.6; th = tw * 11 / 8.5; gap = (x1 - x0 - 4 * tw) / 3
        for i, path in enumerate(thumbs):
            tx = x0 + i * (tw + gap); ty = 5.45
            c.setFillColor(HexColor("#7FB8D3")); c.rect(self.X(tx + 0.06), self.Y(ty + th + 0.06), tw * PT, th * PT, stroke=0, fill=1)
            c.drawImage(ImageReader(path), self.X(tx), self.Y(ty + th), tw * PT, th * PT)
            c.setStrokeColor(INK); c.setLineWidth(1.5); c.rect(self.X(tx), self.Y(ty + th), tw * PT, th * PT, stroke=1, fill=0)
        self.text("Inside: pages like these", BACK_CX, 5.45 + th + 0.38, "Fredoka-SemiBold", 13)
        bx1, by1 = BACK_X1 - SAFE, TRIM_Y1 - SAFE
        c.setFillColor(white); c.rect(self.X(bx1 - 2.0), self.Y(by1), 2.0 * PT, 1.2 * PT, stroke=0, fill=1)
        self.text("TinyTusk", x0, TRIM_Y1 - SAFE - 0.05, "Fredoka-Bold", 16, anchor="l")


def build():
    os.makedirs(f"{OUT}/cover", exist_ok=True)
    thumbs = []
    for n in ("06_A", "07_A_practice", "18_G", "03_warmup_lines"):
        t = f"{OUT}/cover/thumb_{n}"
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-singlefile", f"{OUT}/pages/{n}.pdf", t], check=True)
        thumbs.append(t + ".png")
    c = canvas.Canvas(f"{OUT}/cover.pdf", pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setTitle("My First ABC Letter Tracing Workbook - cover"); c.setAuthor("TinyTusk")
    cv = Cover(c); cv.background(); cv.back(thumbs); cv.front()
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "60", "-singlefile", f"{OUT}/cover.pdf", f"{OUT}/cover/cover_preview"], check=True)
    print(f"cover.pdf  {W:.4f} x {H:.4f} in  (spine {SPINE} in for {PAGES} pages)")


if __name__ == "__main__":
    build()
