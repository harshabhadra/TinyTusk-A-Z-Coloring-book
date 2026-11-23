"""Full-wrap paperback cover for "Trace & Write the Alphabet": back + spine + front, 0.125 in bleed.
No new art: the front uses the coloring book's coloured animals (../colored/) in round frames, and
stroke letters drawn like a tracing page. Warm yellow background so it is easy to tell apart from the
blue-sky / mint covers of the other TinyTusk books.

Usage: python3 Trace-and-Write-the-Alphabet/src/cover.py -> Trace-and-Write-the-Alphabet/cover.pdf
                                                          (+ Trace-and-Write-the-Alphabet/cover/cover_preview.png)
Assumed KDP values (confirm with KDP's cover calculator before upload):
  black & white interior, white paper: spine = pages x 0.002252 in; bleed 0.125 in.
  Spine text "TinyTusk • Trace & Write the Alphabet" (KDP allows spine text above 79 pages); at ~0.18 in
  wide the text is small (about 5 pt) after KDP's 0.0625 in clearance on each side.
"""
import math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(os.path.dirname(HERE)), "src"),
                os.path.join(os.path.dirname(os.path.dirname(HERE)), "brand")]
from reportlab.pdfgen import canvas                 # noqa: E402
from reportlab.lib.colors import HexColor, white    # noqa: E402
from reportlab.pdfbase import pdfmetrics            # noqa: E402
from reportlab.lib.utils import ImageReader         # noqa: E402
import layout                                       # noqa: E402 (fonts, chdir to repo root)
from layout import CAP                              # noqa: E402
from palette import PALETTE                         # noqa: E402
import strokes                                      # noqa: E402
import brand                                        # noqa: E402 (../../brand: series lockup, shared back, spine)
from pages import PAGES, KEY                        # noqa: E402

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
BG, BG2, INK = HexColor("#FFE9A8"), HexColor("#FFD66B"), HexColor("#212121")
PAPER_LINE, MID_LINE = HexColor("#E57373"), HexColor("#90A4AE")
FRONT_CX, BACK_CX = (FRONT_X0 + FRONT_X1) / 2, (BACK_X0 + BACK_X1) / 2
OUT = "Trace-and-Write-the-Alphabet"
P = lambda n: HexColor(PALETTE[n])


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
            k = 0
            for ch in s:
                c.saveState(); t = c.beginText(); t.setFont(font, size); t.setTextOrigin(self.X(x), self.Y(y))
                if pass_ == "stroke":
                    t.setTextRenderMode(1); c.setStrokeColor(stroke); c.setLineWidth(width); c.setLineJoin(1)
                else:
                    t.setTextRenderMode(0); c.setFillColor(fills[k % len(fills)])
                t.textOut(ch); c.drawText(t); c.restoreState()
                x += pdfmetrics.stringWidth(ch, font, size) / PT
                if ch != " ":
                    k += 1

    def rrect(self, x0, y0, x1, y1, r, fill=None, width=2.5, stroke=INK):
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
            y += sz * CAP / PT; self.text(s, cx, y, font, sz); y += 0.06

    def handwriting_lines(self, x0, x1, base, u):
        c = self.c
        c.saveState(); c.setLineCap(1)
        c.setStrokeColor(MID_LINE); c.setLineWidth(2)
        c.line(self.X(x0), self.Y(base - 2 * u), self.X(x1), self.Y(base - 2 * u))
        c.setDash(8, 7); c.line(self.X(x0), self.Y(base - u), self.X(x1), self.Y(base - u)); c.setDash()
        c.setStrokeColor(PAPER_LINE); c.setLineWidth(2.5)
        c.line(self.X(x0), self.Y(base), self.X(x1), self.Y(base))
        c.restoreState()

    def tracing_letter(self, ch, x, base, u, color, solid=True):
        """Fat coloured stroke letter with a dark outline and a white dashed centre line (solid=True),
        or a grey dashed letter still to be traced (solid=False)."""
        c = self.c
        if solid:
            layers = ((INK, u * PT * 0.36, None), (color, u * PT * 0.27, None), (white, u * PT * 0.05, (7, 8)))
        else:
            layers = ((HexColor("#9E9E9E"), u * PT * 0.09, (u * PT * 0.16, u * PT * 0.16)),)
        for col, lw, dash in layers:
            c.saveState(); c.setStrokeColor(col); c.setFillColor(col); c.setLineWidth(lw); c.setLineCap(1); c.setLineJoin(1)
            if dash: c.setDash(*dash)
            for pts, is_dot in strokes.polylines(ch):
                Q = [(self.X(x + gx * u), self.Y(base - gy * u)) for gx, gy in pts]
                if is_dot:
                    c.circle(*Q[0], lw / 2, stroke=0, fill=1); continue
                p = c.beginPath(); p.moveTo(*Q[0])
                for q in Q[1:]: p.lineTo(*q)
                c.drawPath(p, stroke=1, fill=0)
            c.restoreState()

    def animal_circle(self, L, cx, cy, r, ring):
        c = self.c
        c.setFillColor(white); c.setStrokeColor(ring); c.setLineWidth(7)
        c.circle(self.X(cx), self.Y(cy), r * PT, stroke=1, fill=1)
        c.saveState()
        p = c.beginPath(); p.circle(self.X(cx), self.Y(cy), (r - 0.03) * PT); c.clipPath(p, stroke=0, fill=0)
        img = ImageReader(f"colored/{L}.png"); iw, ih = img.getSize()
        s = (2 * r * 0.86) / max(iw, ih)
        w, h = iw * s, ih * s
        c.drawImage(img, self.X(cx - w / 2), self.Y(cy + h / 2 + 0.02), w * PT, h * PT)
        c.restoreState()
        c.setStrokeColor(INK); c.setLineWidth(2.5); c.setFillColor(white)
        c.circle(self.X(cx), self.Y(cy), (r + 0.05) * PT, stroke=1, fill=0)
        # letter tag
        tx, ty = cx + r * 0.72, cy - r * 0.72
        c.setFillColor(ring); c.circle(self.X(tx), self.Y(ty), 0.27 * PT, stroke=1, fill=1)
        self.text(L, tx, ty + 24 * CAP / PT / 2, "Fredoka-Bold", 24, white)

    def background(self):
        c = self.c
        c.setFillColor(BG); c.rect(0, 0, W * PT, H * PT, stroke=0, fill=1)
        # soft polka dots
        c.setFillColor(BG2)
        for i in range(0, 40):
            for j in range(0, 25):
                if (i + j) % 2 == 0:
                    c.circle(self.X(0.25 + i * 0.45), self.Y(0.25 + j * 0.47), 0.05 * PT, stroke=0, fill=1)

    def front(self):
        c = self.c
        cx = FRONT_CX
        self.outlined("Trace & Write", cx, 1.45, layout.LETTER_FONT, 66,
                      [P("Red"), P("Orange"), P("Light green"), P("Light blue"), P("Purple"), P("Pink")], width=7)
        self.outlined("the Alphabet", cx, 2.55, layout.LETTER_FONT, 66, [P("Dark blue")], width=7)
        # writing-paper card with traced letters
        x0, x1 = FRONT_X0 + 0.65, FRONT_X1 - 0.65
        self.rrect(x0, 2.9, x1, 5.05, 0.25, fill=white, width=3.5)
        u = 0.56
        base = 3.2 + 2 * u + 0.12
        self.handwriting_lines(x0 + 0.2, x1 - 0.2, base, u)
        seq = [("A", "Red", True), ("a", "Red", True), ("B", "Orange", True), ("b", "Orange", False),
               ("C", "Light green", True), ("c", "Light green", False)]
        gap, pair_gap = 0.22, 0.5
        widths = [strokes.width(ch) * u for ch, _, _ in seq]
        tot = sum(widths) + gap * 3 + pair_gap * 2
        x = cx - 0.35 - tot / 2
        for k, ((ch, col, solid), wd) in enumerate(zip(seq, widths)):
            self.tracing_letter(ch, x, base, u, P(col), solid)
            x += wd + (pair_gap if k % 2 else gap)
        # pencil, finishing the last letter
        self.pencil(x - pair_gap + 0.12, base - 0.05, 1.25)
        # subtitle pill
        sub = "Uppercase, Lowercase, Words & Sentences"
        pw = pdfmetrics.stringWidth(sub, "Fredoka-Bold", 21) / PT + 0.7
        self.rrect(cx - pw / 2, 5.3, cx + pw / 2, 5.85, 0.27, fill=P("Purple"), width=3)
        self.text(sub, cx, 5.575 + 21 * CAP / PT / 2, "Fredoka-Bold", 21, white)
        self.text(f"{PAGES}-page handwriting workbook with 26 baby animals", cx, 6.25, "Fredoka-SemiBold", 17)
        # animals
        spots = [("A", 1.55, 7.55, P("Light green")), ("L", 3.35, 7.25, P("Orange")), ("P", 5.15, 7.25, P("Pink")),
                 ("E", 6.95, 7.55, P("Light blue")), ("G", 2.45, 9.25, P("Yellow")), ("Z", 4.25, 9.35, P("Purple")),
                 ("R", 6.05, 9.25, P("Red"))]
        for L, ax, ay, col in spots:
            self.animal_circle(L, FRONT_X0 + ax, ay, 0.78, col)
        self.badge(FRONT_X0 + SAFE + 0.68, TRIM_Y1 - SAFE - 0.95, 0.66,
                   [("Ages", "Fredoka-SemiBold", 16), ("3–5", "Fredoka-Bold", 28)], P("Yellow"))
        brand.front_lockup(self, FRONT_X1, TRIM_Y1, SAFE)

    def pencil(self, tip_x, tip_y, length):
        """Simple yellow pencil lying at 35 degrees, tip at (tip_x, tip_y)."""
        c = self.c
        a = math.radians(35)
        dx, dy = math.cos(a), -math.sin(a)        # towards the eraser (up-right on the page)
        nx, ny = -dy, dx
        w = 0.13
        def pt(t, s): return (self.X(tip_x + dx * t + nx * s), self.Y(tip_y + dy * t + ny * s))
        def poly(pts, fill):
            p = c.beginPath(); p.moveTo(*pts[0])
            for q in pts[1:]: p.lineTo(*q)
            p.close(); c.setFillColor(fill); c.setStrokeColor(INK); c.setLineWidth(2); c.setLineJoin(1)
            c.drawPath(p, stroke=1, fill=1)
        poly([pt(0.32, -w), pt(length, -w), pt(length, w), pt(0.32, w)], P("Yellow"))
        poly([pt(length, -w), pt(length + 0.12, -w), pt(length + 0.12, w), pt(length, w)], HexColor("#B0BEC5"))
        poly([pt(length + 0.12, -w), pt(length + 0.3, -w), pt(length + 0.3, w), pt(length + 0.12, w)], P("Pink"))
        poly([pt(0, 0), pt(0.32, -w), pt(0.32, w)], HexColor("#F3D9B1"))
        poly([pt(0, 0), pt(0.1, -w * 0.31), pt(0.1, w * 0.31)], INK)

    def back(self, thumbs):
        brand.back(self, KEY, BACK_X0 + SAFE + 0.15, BACK_X1 - SAFE - 0.15,
                   "Lots of practice, one letter at a time!",
                   ["Every letter gets its own full page, first in uppercase",
                    "and then in lowercase. Six rows on each page go step by",
                    "step from grey dashed letters, to start dots, to empty",
                    "lines, so children build confidence as they write."],
                   ["52 letter pages: A–Z, then a–z",
                    "Stroke numbers, arrows and start dots",
                    "Missing letters, what comes next & matching",
                    "52 first words and 12 short sentences to trace",
                    "Alphabet animal chart and a certificate",
                    "Large 8.5 × 11 in pages, for ages 3–5"],
                   thumbs, "Ages 3–5", shadow=BG2, accent=P("Yellow"), trim_y1=TRIM_Y1, safe=SAFE)

    def spine(self):
        c = self.c
        c.setFillColor(BG); c.rect(self.X(BACK_X1 - 0.1), 0, (SPINE + 0.2) * PT, H * PT, stroke=0, fill=1)
        brand.spine(self, BACK_X1, SPINE_X1, PAGES, "Trace & Write the Alphabet", H)

def build():
    os.makedirs(f"{OUT}/cover", exist_ok=True)
    thumbs = []
    for n in ("05_upper_A", "39_lower_g", "32_missing_upper", "76_sentences_1"):
        t = f"{OUT}/cover/thumb_{n}"
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-singlefile", f"{OUT}/pages/{n}.pdf", t], check=True)
        thumbs.append(t + ".png")
    c = canvas.Canvas(f"{OUT}/cover.pdf", pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setTitle("Trace & Write the Alphabet - cover"); c.setAuthor(brand.IMPRINT)
    cv = Cover(c); cv.background(); cv.spine(); cv.back(thumbs); cv.front()
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "60", "-singlefile", f"{OUT}/cover.pdf", f"{OUT}/cover/cover_preview"], check=True)
    brand.render_front(f"{OUT}/cover.pdf", KEY)
    print(f"cover.pdf  {W:.4f} x {H:.4f} in  (spine {SPINE} in for {PAGES} pages)")


if __name__ == "__main__":
    build()
