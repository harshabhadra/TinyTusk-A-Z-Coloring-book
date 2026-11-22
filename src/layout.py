"""Page template (brief section 6). All positions in inches from the TOP-LEFT of the 8.5x11 page.

Usage: python3 src/layout.py A          -> pages/A.pdf (+ pages/A.png preview)
Needs: clean/A.png, colored/A.png, colored/A.json
"""
import json, math, os, subprocess, sys
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from palette import PALETTE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
for n in ("Bold", "SemiBold", "Medium"):
    pdfmetrics.registerFont(TTFont(f"Fredoka-{n}", f"fonts/Fredoka-{n}.ttf"))
# big outline letters use Baloo 2 (standard B, single-storey g); labels use Fredoka
LETTER_FONT = "Baloo2-ExtraBold"
pdfmetrics.registerFont(TTFont(LETTER_FONT, f"fonts/{LETTER_FONT}.ttf"))


def _glyph_bounds():
    """Highest and lowest ink over all 52 letters, in em units (for one shared size and baseline)."""
    from fontTools.ttLib import TTFont as FT
    f = FT(f"fonts/{LETTER_FONT}.ttf"); cmap = f.getBestCmap(); glyf = f["glyf"]; upm = f["head"].unitsPerEm
    ys = []
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
        g = glyf[cmap[ord(ch)]]; g.recalcBounds(glyf); ys += [g.yMin / upm, g.yMax / upm]
    return max(ys), min(ys)


GLYPH_TOP, GLYPH_BOT = _glyph_bounds()

W, H = 8.5, 11.0
PT = 72
CAP = 0.70                       # Fredoka cap height / em

# --- fixed geometry (identical on every page) ---------------------------------
BORDER = (0.5, 0.5, 8.0, 10.5)   # x0, y0, x1, y1
BORDER_W, BORDER_R = 4, 0.25
INNER_L, INNER_R = 0.8, 7.7      # content left/right edges
BAND_TOP, BAND_BOT = 0.75, 2.95  # top band
LETTER_CAP = 1.45                # outline "Aa" cap height
LETTER_COL = (0.8, 3.45)        # outline "Aa" column
MID_COL = (3.6, 5.65)           # label + colour check column
REF_BOX = (5.8, 0.85, 7.7, 2.85) # colored reference box (x0,y0,x1,y1)
DRAW_BOX = (0.85, 3.1, 7.65, 9.4)  # 6.8 x 6.3 drawing area
FOOT_TOP = 9.7                   # footer: 9.7 -> 10.5 (border)
PILL_FILL = HexColor("#FFF3B0")
INK = black

ANIMALS = dict(line.split(":") for line in """A:Alligator B:Bear C:Camel D:Dolphin E:Elephant F:Frog G:Giraffe H:Hippo
I:Iguana J:Jellyfish K:Koala L:Lion M:Monkey N:Narwhal O:Owl P:Panda Q:Quail R:Rabbit S:Sloth T:Tiger U:Urial
V:Vulture W:Whale X:X-ray_fish Y:Yak Z:Zebra""".split())
ANIMALS = {k: v.replace("_", " ") for k, v in ANIMALS.items()}


class Page:
    def __init__(self, c):
        self.c = c

    # top-left inch coordinates -> reportlab points
    def X(self, x): return x * PT
    def Y(self, y): return (H - y) * PT

    def rrect(self, x0, y0, x1, y1, r, stroke=1, fill=0):
        self.c.roundRect(self.X(x0), self.Y(y1), (x1 - x0) * PT, (y1 - y0) * PT, r * PT, stroke=stroke, fill=fill)

    def image(self, path, box):
        x0, y0, x1, y1 = box
        from PIL import Image
        im = Image.open(path)
        im = im.convert("L") if im.mode in ("1", "L") else im.convert("RGB")
        img = ImageReader(im); iw, ih = img.getSize()
        s = min((x1 - x0) / iw, (y1 - y0) / ih)
        w, h = iw * s, ih * s
        x, y = x0 + (x1 - x0 - w) / 2, y0 + (y1 - y0 - h) / 2
        self.c.drawImage(img, self.X(x), self.Y(y + h), w * PT, h * PT, mask=None)

    def border(self):
        c = self.c
        c.setStrokeColor(INK); c.setLineWidth(BORDER_W)
        # stroke centred on the 0.5" margin line, inset by half the line so no ink goes outside the margin
        hw = BORDER_W / 2 / PT
        x0, y0, x1, y1 = BORDER
        self.rrect(x0 + hw, y0 + hw, x1 - hw, y1 - hw, BORDER_R)

    def outline_text(self, text, x, y_base, size, font="Fredoka-Bold", width=3):
        c = self.c
        c.saveState()                                     # text render mode must not leak to later text
        t = c.beginText(); t.setTextRenderMode(2)          # fill + stroke
        t.setFont(font, size); t.setTextOrigin(self.X(x), self.Y(y_base))
        c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(width); c.setLineJoin(1)
        t.textOut(text); c.drawText(t)
        c.restoreState()

    def fit_text(self, text, font, size, max_w_in, min_size=14):
        while size > min_size and pdfmetrics.stringWidth(text, font, size) / PT > max_w_in:
            size -= 0.5
        return size

    # --- footer: line-art grass + flowers (colorable), page number circle -------
    def footer(self, num):
        c = self.c
        c.setStrokeColor(INK); c.setLineWidth(2); c.setLineJoin(1); c.setLineCap(1); c.setFillColor(white)
        base, top = 10.28, 9.98
        x0, x1 = 0.8, 7.7
        cx = W / 2
        gap = 0.42
        for a, b in ((x0, cx - gap), (cx + gap, x1)):
            p = c.beginPath(); p.moveTo(self.X(a), self.Y(base))
            n = max(1, round((b - a) / 0.22)); step = (b - a) / n
            for i in range(n):
                xa = a + i * step
                hgt = top + (0.06 if i % 3 == 1 else 0)
                p.lineTo(self.X(xa + step * 0.5), self.Y(hgt))
                p.lineTo(self.X(xa + step), self.Y(base))
            c.drawPath(p, stroke=1, fill=0)
            c.line(self.X(a), self.Y(base), self.X(b), self.Y(base))
        # flowers on stems
        for fx in (1.3, 2.6, 3.4, 5.1, 5.9, 7.2):
            stem_top = 9.86
            c.line(self.X(fx), self.Y(base), self.X(fx), self.Y(stem_top))
            r_pet, d = 0.065, 0.085
            for k in range(5):
                ang = math.radians(90 + k * 72)
                c.circle(self.X(fx + d * math.cos(ang)), self.Y(stem_top - 0.02 - d * math.sin(ang)), r_pet * PT, stroke=1, fill=1)
            c.circle(self.X(fx), self.Y(stem_top - 0.02), 0.05 * PT, stroke=1, fill=1)
        # page number
        cy = 10.08
        c.setLineWidth(2.5); c.circle(self.X(cx), self.Y(cy), 0.24 * PT, stroke=1, fill=1)
        c.setFillColor(INK); c.setFont("Fredoka-SemiBold", 15)
        c.drawCentredString(self.X(cx), self.Y(cy) - 15 * CAP / 2, str(num))

    # --- letter page ------------------------------------------------------------
    def letter_page(self, L, num):
        c = self.c
        animal = ANIMALS[L]
        colors = json.load(open(f"colored/{L}.json"))["colors_used"]
        self.border()

        # big outline letters: one size and baseline for every page, sized so the tallest
        # ascender and deepest descender (f, g, j, p, q, y) stay inside the band; very wide pairs
        # (Mm, Ww) shrink horizontally-centred around the same baseline
        lx0, lx1 = LETTER_COL
        pair = L + L.lower()
        band_h = BAND_BOT - BAND_TOP - 0.1
        size = min(LETTER_CAP * PT / CAP, band_h * PT / (GLYPH_TOP - GLYPH_BOT))
        base = BAND_TOP + 0.05 + GLYPH_TOP * size / PT
        size_w = min(size, (lx1 - lx0) * PT / (pdfmetrics.stringWidth(pair, LETTER_FONT, size) / size))
        if size_w < size:                       # keep the shrunk pair vertically centred on the normal one
            base -= (GLYPH_TOP + GLYPH_BOT) / 2 * (size - size_w) / PT
            size = size_w
        lw = pdfmetrics.stringWidth(pair, LETTER_FONT, size) / PT
        self.outline_text(pair, (lx0 + lx1 - lw) / 2, base, size, font=LETTER_FONT)

        # middle column: two-line label pill
        mx0, mx1 = MID_COL
        mw, mcx = mx1 - mx0, (mx0 + mx1) / 2
        py0, py1 = 0.85, 1.75
        c.setFillColor(PILL_FILL); c.setStrokeColor(INK); c.setLineWidth(2)
        self.rrect(mx0, py0, mx1, py1, 0.3, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Fredoka-Medium", 16)
        c.drawCentredString(self.X(mcx), self.Y(py0 + 0.36), f"{L} is for")
        fs = self.fit_text(animal, "Fredoka-Bold", 22, mw - 0.3, 16)
        c.setFont("Fredoka-Bold", fs)
        c.drawCentredString(self.X(mcx), self.Y(py0 + 0.72), animal)

        # "Check your colors" box
        by0, by1 = 1.9, 2.85
        c.setLineWidth(1.5); c.setDash(4, 3)
        self.rrect(mx0, by0, mx1, by1, 0.15)
        c.setDash()
        c.setFont("Fredoka-SemiBold", 13)
        c.drawCentredString(self.X(mcx), self.Y(by0 + 0.3), "Check your colors")
        dr, gapd = 0.12, 0.08
        n = len(colors)
        total = n * 2 * dr + (n - 1) * gapd
        x = mcx - total / 2 + dr
        for name in colors:
            c.setFillColor(HexColor(PALETTE[name])); c.setStrokeColor(INK); c.setLineWidth(1.2)
            c.circle(self.X(x), self.Y(by0 + 0.64), dr * PT, stroke=1, fill=1)
            x += 2 * dr + gapd
        c.setFillColor(INK)

        # colored reference
        self.image(f"colored/{L}.png", REF_BOX)
        # main drawing
        self.image(f"clean/{L}.png", DRAW_BOX)
        self.footer(num)


def build(letter, out_dir="pages"):
    num = 3 + ord(letter) - ord("A")
    pdf = f"{out_dir}/{letter}.pdf"
    c = canvas.Canvas(pdf, pagesize=(W * PT, H * PT))
    c.setTitle(f"{letter} is for {ANIMALS[letter]}"); c.setAuthor("TinyTusk")
    Page(c).letter_page(letter, num)
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "100", "-singlefile", pdf, pdf[:-4]], check=True)
    print(pdf)


if __name__ == "__main__":
    for L in sys.argv[1:]:
        build(L.upper())
