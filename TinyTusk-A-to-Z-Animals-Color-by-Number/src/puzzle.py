"""Colour-by-number letter pages (4-29).

For every region of the A-Z book's line art the colour comes from ../specs/<L>.json (the same spec
that made ../colored/<L>.png, which becomes the answer key).  Each page numbers its own colours
1..n in palette order, so every number is a single digit.
  * regions big enough get a number at the widest point (size scales with the space, 8-16 pt)
  * regions too small for a readable number are printed already coloured
  * regions the spec leaves white get no number
Usage: python3 src/puzzle.py [A B ...]   -> art/<L>_puzzle.png, art/<L>_numbers.json, pages/<L>.pdf/.png
"""
import json, string, subprocess, sys
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from common import *
from regions import regions
from palette import rgb

DRAW_BOX = (0.85, 2.6, 7.65, 9.55)
NUM_FONT = "Fredoka-SemiBold"
NUM_COLOR = HexColor("#3C3C3C")
MIN_PT, MAX_PT = 9, 18
LINE_PAD_PT = 1.5                       # clear space between a number and the lines


def number_size(r_px, s):
    """Largest font size (pt) whose digit fits a circle of r_px (image px) at scale s (in/px)."""
    room = r_px * s * PT - LINE_PAD_PT
    return min(MAX_PT, room / 0.5)       # a Fredoka digit's half-diagonal is ~0.46 em


def plan(L):
    d = regions(L)
    w, h = d["size"]
    _, _, s = placement(w, h, DRAW_BOX)
    colours = [c for c in ORDER if any(r["color"] == c for r in d["regions"])]
    num = {c: i + 1 for i, c in enumerate(colours)}
    labels, pre = [], []
    for r in d["regions"]:
        if r["color"] == "white":
            continue
        if number_size(r["r"], s) >= MIN_PT:
            for x, y, rr in r["spots"]:
                labels.append(dict(x=x, y=y, n=num[r["color"]], pt=round(number_size(rr, s), 1)))
        else:
            pre.append(r)
    # line art with the tiny regions already coloured
    art = np.full((h, w, 3), 255, np.uint8)
    for r in pre:
        art[d["lab"] == r["id"]] = rgb(r["color"])
    art[d["ink"]] = 0
    # The source art is ~1890 px tall but printed ~6.95 in tall (only ~272 ppi), which KDP flags as low
    # resolution. The ink is hard-edged, so a 2x nearest-neighbour copy (~545 ppi) looks the same and passes.
    # Same aspect ratio, so placement() and the number positions (in source px) are unchanged.
    Image.fromarray(art).resize((w * 2, h * 2), Image.NEAREST).save(f"{ART_DIR}/{L}_puzzle.png", dpi=(600, 600))
    info = dict(animal=d["animal"], key=[[num[c], c] for c in colours], numbers=labels,
                precolored=len(pre), size=[w, h])
    json.dump(info, open(f"{ART_DIR}/{L}_numbers.json", "w"), indent=1)
    return info


class Puzzle(Page):
    def numbers(self, info, box=DRAW_BOX, only=None):
        """Draw the region numbers onto an image placed in box (only: predicate on x px)."""
        c = self.c
        w, h = info["size"]
        x0, y0, s = placement(w, h, box)
        c.setFillColor(NUM_COLOR)
        for t in info["numbers"]:
            if only and not only(t):
                continue
            c.setFont(NUM_FONT, t["pt"])
            c.drawCentredString(self.X(x0 + t["x"] * s), self.Y(y0 + t["y"] * s) - t["pt"] * CAP / 2, str(t["n"]))

    def crayon(self, x, cy, name, n=None, length=0.62, h=0.26):
        """Crayon swatch (body + tip) in the palette colour, with the number in a white dot."""
        c = self.c
        c.setFillColor(HexColor(PALETTE[name])); c.setStrokeColor(INK); c.setLineWidth(1.4); c.setLineJoin(1)
        body = length * 0.76
        p = c.beginPath()
        p.moveTo(self.X(x), self.Y(cy - h / 2)); p.lineTo(self.X(x + body), self.Y(cy - h / 2))
        p.lineTo(self.X(x + length), self.Y(cy)); p.lineTo(self.X(x + body), self.Y(cy + h / 2))
        p.lineTo(self.X(x), self.Y(cy + h / 2)); p.close()
        c.drawPath(p, stroke=1, fill=1)
        if n is not None:
            dx = x + body * 0.45
            c.setFillColor(white); c.setLineWidth(1.2)
            c.circle(self.X(dx), self.Y(cy), (h / 2 - 0.02) * PT, stroke=1, fill=1)
            c.setFillColor(INK); c.setFont("Fredoka-Bold", 13)
            c.drawCentredString(self.X(dx), self.Y(cy) - 13 * CAP / 2, str(n))

    def key(self, entries, box):
        """Colour key: numbered crayons, one or two columns."""
        c = self.c
        x0, y0, x1, y1 = box
        c.setStrokeColor(INK); c.setLineWidth(2)
        self.rrect(x0, y0, x1, y1, 0.18, stroke=1, fill=0)
        c.setFillColor(INK); c.setFont("Fredoka-Bold", 15)
        c.drawCentredString(self.X((x0 + x1) / 2), self.Y(y0 + 0.3), "Color key")
        cols = 1 if len(entries) <= 3 else 2
        rows = -(-len(entries) // cols)
        top, bot = y0 + 0.45, y1 - 0.08
        rh = (bot - top) / 3
        top += (3 - rows) * rh / 2
        cw = (x1 - x0 - 0.2) / cols
        for k, (n, name) in enumerate(entries):
            col, row = divmod(k, rows)
            ex = x0 + 0.12 + col * cw + (0.7 if cols == 1 else 0)
            cy = top + (row + 0.5) * rh
            self.crayon(ex, cy, name, n)
            c.setFillColor(INK)
            fs = self.fit_text(name, "Fredoka-SemiBold", 13, cw - 0.78, 10)
            c.setFont("Fredoka-SemiBold", fs)
            c.drawString(self.X(ex + 0.7), self.Y(cy) - fs * CAP / 2, name)

    def letter_page(self, L, num, info):
        c = self.c
        self.border()
        # big outline "Aa" (same font as the A-Z book), smaller band
        pair = L + L.lower()
        lx0, lx1, base = 0.8, 2.3, 1.95
        size = 1.0 * PT / CAP
        size = min(size, (lx1 - lx0) * PT / (pdfmetrics.stringWidth(pair, LETTER_FONT, size) / size))
        lw = pdfmetrics.stringWidth(pair, LETTER_FONT, size) / PT
        self.outline_text(pair, (lx0 + lx1 - lw) / 2, base, size, font=LETTER_FONT)
        # label pill
        mx0, mx1 = 2.38, 3.95
        mcx = (mx0 + mx1) / 2
        py0, py1 = 0.95, 1.85
        c.setFillColor(PILL_FILL); c.setStrokeColor(INK); c.setLineWidth(2)
        self.rrect(mx0, py0, mx1, py1, 0.3, stroke=1, fill=1)
        c.setFillColor(INK); c.setFont("Fredoka-Medium", 15)
        c.drawCentredString(self.X(mcx), self.Y(py0 + 0.35), f"{L} is for")
        fs = self.fit_text(info["animal"], "Fredoka-Bold", 21, mx1 - mx0 - 0.2, 14)
        c.setFont("Fredoka-Bold", fs)
        c.drawCentredString(self.X(mcx), self.Y(py0 + 0.72), info["animal"])
        c.setFont("Fredoka-Medium", 10)
        c.drawCentredString(self.X((0.8 + mx1) / 2), self.Y(2.3), "Color each space with the crayon for its number.")
        # key
        self.key(info["key"], (4.05, 0.8, 7.7, 2.45))
        # picture + numbers
        self.image(f"{ART_DIR}/{L}_puzzle.png", DRAW_BOX)
        self.numbers(info)
        self.footer(num)


def build(L):
    info = plan(L)
    num = FIRST_LETTER_PAGE + ord(L) - ord("A")
    pdf = f"{PAGES_DIR}/{L}.pdf"
    c = canvas.Canvas(pdf, pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setTitle(f"{L} is for {info['animal']}"); c.setAuthor(AUTHOR)
    Puzzle(c).letter_page(L, num, info)
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "100", "-singlefile", pdf, pdf[:-4]], check=True)
    sizes = [t["pt"] for t in info["numbers"]]
    print(f"{L}: {len(info['key'])} colours, {len(sizes)} numbers ({min(sizes)}-{max(sizes)} pt), {info['precolored']} pre-coloured")


if __name__ == "__main__":
    for L in sys.argv[1:] or string.ascii_uppercase:
        build(L.upper())
