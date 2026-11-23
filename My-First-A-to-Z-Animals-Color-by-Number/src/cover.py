"""Full-wrap paperback cover: back + spine + front with 0.125" bleed (KDP).
Usage: python3 src/cover.py -> cover.pdf (+ cover/cover_preview.png)

Same assumed KDP values as the A-Z book (confirm with KDP's cover calculator before upload):
  premium color, white paper: spine = pages x 0.002347 in; bleed 0.125 in; no spine text under 80 pages.
Front: a big Lion, left half coloured, right half still numbered (shows what the book does).
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from common import BOOK, REPO, ART_DIR, PALETTE, CAP, LETTER_FONT, TITLE, AUTHOR
from regions import load_clean
import cv2
sys.path.insert(0, f"{REPO}/src")
from cover import Cover as AZCover               # ../src/cover.py: text helpers, badges
import puzzle

PAGES = 38
TRIM_W, TRIM_H = 8.5, 11.0
BLEED = 0.125
SPINE = round(PAGES * 0.002347, 4)
W = BLEED + TRIM_W + SPINE + TRIM_W + BLEED
H = BLEED + TRIM_H + BLEED
PT = 72
SAFE = 0.25
BACK_X0, BACK_X1 = BLEED, BLEED + TRIM_W
SPINE_X0, SPINE_X1 = BACK_X1, BACK_X1 + SPINE
FRONT_X0, FRONT_X1 = SPINE_X1, SPINE_X1 + TRIM_W
TRIM_Y0, TRIM_Y1 = BLEED, BLEED + TRIM_H
FRONT_CX = (FRONT_X0 + FRONT_X1) / 2
BACK_CX = (BACK_X0 + BACK_X1) / 2
BG = HexColor("#CBEFE0")                           # soft mint (A-Z book: sky blue, tracing book: yellow)
HILL = HexColor("#8FD08A")
INK = HexColor("#212121")
SUBTITLE = "26 Cute Baby Animals to Color by Number"
COVER_DIR = f"{BOOK}/cover"
os.makedirs(COVER_DIR, exist_ok=True)


def cutout(L, src):
    """RGBA of src (same size as ../clean/<L>.png) with the background outside the animal transparent."""
    _, ink = load_clean(L)
    n, lab = cv2.connectedComponents((~ink).astype(np.uint8), connectivity=4)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    outside = np.isin(lab, border[border > 0])
    rgb = np.array(Image.open(src).convert("RGB"))
    a = np.where(outside, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, a]), "RGBA")


class Cover(AZCover):
    def X(self, x): return x * PT
    def Y(self, y): return (H - y) * PT

    def img(self, im, box, clip=None):
        """Draw a PIL image fitted into box; clip = (x0, x1) inches keeps only that vertical strip."""
        c = self.c
        x0, y0, x1, y1 = box
        s = min((x1 - x0) / im.width, (y1 - y0) / im.height)
        w, h = im.width * s, im.height * s
        x, y = x0 + (x1 - x0 - w) / 2, y0 + (y1 - y0 - h) / 2
        c.saveState()
        if clip:
            p = c.beginPath(); p.rect(self.X(clip[0]), 0, (clip[1] - clip[0]) * PT, H * PT)
            c.clipPath(p, stroke=0, fill=0)
        c.drawImage(ImageReader(im), self.X(x), self.Y(y + h), w * PT, h * PT, mask="auto")
        c.restoreState()
        return x, y, s

    def background(self):
        c = self.c
        c.setFillColor(BG); c.rect(0, 0, W * PT, H * PT, stroke=0, fill=1)
        # rolling hill across back + spine + front
        p = c.beginPath(); p.moveTo(0, 0); p.lineTo(0, self.Y(9.6))
        for i in range(81):
            x = W * i / 80
            p.lineTo(self.X(x), self.Y(9.6 - 0.25 * math.sin(2 * math.pi * i / 80)))
        p.lineTo(W * PT, 0); p.close()
        c.setFillColor(HILL); c.drawPath(p, stroke=0, fill=1)
        # confetti dots
        rng = np.random.default_rng(7)
        cols = [HexColor(PALETTE[k]) for k in ("Red", "Orange", "Yellow", "Light blue", "Purple", "Pink")]
        for _ in range(70):
            x, y = rng.uniform(0, W), rng.uniform(0, 9.2)
            if abs(x - (SPINE_X0 + SPINE_X1) / 2) < 0.4:
                continue
            c.setFillColor(cols[rng.integers(len(cols))]); c.circle(self.X(x), self.Y(y), rng.uniform(0.03, 0.06) * PT, stroke=0, fill=1)

    def front(self):
        c = self.c
        cx = FRONT_CX
        c.setFillColor(BG); c.roundRect(self.X(cx - 3.3), self.Y(4.15), 6.6 * PT, 3.5 * PT, 0.3 * PT, stroke=0, fill=1)
        self.outlined("My First", cx, 1.05, "Fredoka-Bold", 46, [white], width=6)
        az = [HexColor(PALETTE[k]) for k in ("Red", "Orange", "Yellow", "Light green", "Light blue", "Purple")]
        self.outlined("A to Z", cx, 2.3, LETTER_FONT, 110, [az[0], white, az[1], az[2], white, az[3]], width=7)
        self.outlined("Animals", cx, 3.12, LETTER_FONT, 70, [HexColor(PALETTE["Dark blue"])], width=6)
        pw = pdfmetrics.stringWidth("Color by Number", "Fredoka-Bold", 30) / PT + 0.8
        self.rrect(cx - pw / 2, 3.32, cx + pw / 2, 3.98, 0.33, fill=HexColor("#FFF3B0"), width=3)
        self.text("Color by Number", cx, 3.65 + 30 * CAP / PT / 2, "Fredoka-Bold", 30)
        self.outlined(SUBTITLE, cx, 4.38, "Fredoka-SemiBold", 16, [INK], stroke=white, width=3)

        # big lion: white card, left half coloured, right half numbered
        box = (cx - 2.35, 4.65, cx + 2.35, 9.55)
        c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(3)
        c.roundRect(self.X(box[0] - 0.15), self.Y(box[3] + 0.15), (box[2] - box[0] + 0.3) * PT,
                    (box[3] - box[1] + 0.3) * PT, 0.3 * PT, stroke=1, fill=1)
        info = puzzle.plan("L")
        col = cutout("L", f"{REPO}/colored/L.png")
        num = Image.open(f"{ART_DIR}/L_puzzle.png").convert("RGB")
        x, y, s = self.img(col, box, clip=(0, cx))
        self.img(num, box, clip=(cx, W))
        c.setFillColor(HexColor("#3C3C3C"))
        for t in info["numbers"]:
            tx = x + t["x"] * s
            if tx > cx + 0.4:
                fs = min(24, t["pt"] * 1.3)
                c.setFont("Fredoka-SemiBold", fs)
                c.drawCentredString(self.X(tx), self.Y(y + t["y"] * s) - fs * CAP / 2, str(t["n"]))
        c.setStrokeColor(INK); c.setLineWidth(2); c.setDash(6, 5)
        c.line(self.X(cx), self.Y(box[1] + 0.1), self.X(cx), self.Y(box[3] - 0.1)); c.setDash()
        # crayon key chips under the card
        names = [n for _, n in info["key"]]
        chip_w = 0.72; gap = 0.18
        x0 = cx - (len(names) * chip_w + (len(names) - 1) * gap) / 2
        for k, name in enumerate(names):
            self.crayon(x0 + k * (chip_w + gap), 10.05, name, k + 1)
        # side animals (coloured cut-outs)
        for L, b in (("E", (FRONT_X0 + 0.25, 6.6, cx - 2.55, 8.1)), ("A", (FRONT_X0 + 0.2, 8.3, cx - 2.55, 10.3)),
                     ("Z", (cx + 2.55, 6.4, FRONT_X1 - 0.25, 8.2)), ("P", (cx + 2.55, 8.35, FRONT_X1 - 0.2, 10.3))):
            self.img(cutout(L, f"{REPO}/colored/{L}.png"), b)
        self.badge(FRONT_X0 + SAFE + 0.72, TRIM_Y0 + SAFE + 0.72, 0.72,
                   [("Ages", "Fredoka-SemiBold", 17), ("4–8", "Fredoka-Bold", 30)], HexColor(PALETTE["Yellow"]))
        self.badge(FRONT_X1 - SAFE - 0.72, TRIM_Y0 + SAFE + 0.72, 0.72,
                   [("26", "Fredoka-Bold", 30), ("pictures +", "Fredoka-SemiBold", 12), ("answer key", "Fredoka-SemiBold", 12)],
                   HexColor(PALETTE["Pink"]))
        self.text("by TinyTusk", FRONT_X1 - SAFE, TRIM_Y1 - SAFE, "Fredoka-SemiBold", 14, anchor="r")

    def crayon(self, x, cy, name, n, length=0.72, h=0.3):
        c = self.c
        c.setFillColor(HexColor(PALETTE[name])); c.setStrokeColor(INK); c.setLineWidth(1.8); c.setLineJoin(1)
        body = length * 0.76
        p = c.beginPath()
        p.moveTo(self.X(x), self.Y(cy - h / 2)); p.lineTo(self.X(x + body), self.Y(cy - h / 2))
        p.lineTo(self.X(x + length), self.Y(cy)); p.lineTo(self.X(x + body), self.Y(cy + h / 2))
        p.lineTo(self.X(x), self.Y(cy + h / 2)); p.close()
        c.drawPath(p, stroke=1, fill=1)
        dx = x + body * 0.45
        c.setFillColor(white); c.setLineWidth(1.4); c.circle(self.X(dx), self.Y(cy), (h / 2 - 0.025) * PT, stroke=1, fill=1)
        c.setFillColor(INK); c.setFont("Fredoka-Bold", 15)
        c.drawCentredString(self.X(dx), self.Y(cy) - 15 * CAP / 2, str(n))

    def back(self):
        c = self.c
        x0, x1 = BACK_X0 + SAFE + 0.15, BACK_X1 - SAFE - 0.15
        self.text("Match the numbers, color the animals!", BACK_CX, 1.05, "Fredoka-Bold", 25)
        self.rrect(x0, 1.35, x1, 4.6, 0.25, fill=white, width=2.5)
        blurb = ["Meet 26 cute baby animals, from a smiling Alligator",
                 "to a stripy Zebra! Find the number, pick the crayon",
                 "from the color key, and watch each animal come to life."]
        y = 1.85
        for line in blurb:
            self.text(line, BACK_CX, y, "Fredoka-Medium", 15); y += 0.3
        bullets = ["26 original baby animals, one for every letter",
                   "Easy numbers 1 to 5 and big spaces for little hands",
                   "A crayon color key on every page",
                   "Full-color answer key at the back",
                   "How-to page, name page and “Well done!” certificate",
                   "Large 8.5 × 11 in pages, for ages 4–8"]
        y += 0.1
        for b in bullets:
            c.setFillColor(HexColor(PALETTE["Orange"])); c.setStrokeColor(INK); c.setLineWidth(1.2)
            c.circle(self.X(x0 + 0.45), self.Y(y - 0.07), 0.07 * PT, stroke=1, fill=1)
            self.text(b, x0 + 0.65, y, "Fredoka-Medium", 14, anchor="l"); y += 0.3
        tw = 1.6; th = tw * 11 / 8.5; gap = (x1 - x0 - 4 * tw) / 3
        for i, name in enumerate(("A", "L", "T", "31_answers")):
            tx = x0 + i * (tw + gap); ty = 4.95
            c.setFillColor(HexColor("#7DBFA4")); c.rect(self.X(tx + 0.06), self.Y(ty + th + 0.06), tw * PT, th * PT, stroke=0, fill=1)
            c.drawImage(ImageReader(f"{COVER_DIR}/thumb_{name}.png"), self.X(tx), self.Y(ty + th), tw * PT, th * PT)
            c.setStrokeColor(INK); c.setLineWidth(1.5); c.rect(self.X(tx), self.Y(ty + th), tw * PT, th * PT, stroke=1, fill=0)
        self.text("Inside: 26 color-by-number pages and an answer key", BACK_CX, 4.95 + th + 0.38, "Fredoka-SemiBold", 13)
        for L, b in (("B", (x0, 8.0, x0 + 1.5, 9.9)), ("G", (x0 + 1.6, 7.75, x0 + 3.1, 9.9)),
                     ("M", (x0 + 3.2, 8.1, x0 + 4.7, 9.9)), ("O", (x0 + 4.8, 8.0, x0 + 6.1, 9.4))):
            self.img(cutout(L, f"{REPO}/colored/{L}.png"), b)
        bx1, by1 = BACK_X1 - SAFE, TRIM_Y1 - SAFE
        c.setFillColor(white); c.rect(self.X(bx1 - 2.0), self.Y(by1), 2.0 * PT, 1.2 * PT, stroke=0, fill=1)
        self.text("TinyTusk", x0, TRIM_Y1 - SAFE - 0.05, "Fredoka-Bold", 16, anchor="l")


def build():
    for name in ("A", "L", "T", "31_answers"):
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-singlefile", f"{BOOK}/pages/{name}.pdf", f"{COVER_DIR}/thumb_{name}"], check=True)
    pdf = f"{BOOK}/cover.pdf"
    c = canvas.Canvas(pdf, pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setTitle(f"{TITLE} - cover"); c.setAuthor(AUTHOR)
    cv = Cover(c)
    cv.background(); cv.back(); cv.front()
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "60", "-singlefile", pdf, f"{COVER_DIR}/cover_preview"], check=True)
    print(f"cover.pdf  {W:.4f} x {H:.4f} in  (spine {SPINE} in for {PAGES} pages)")


if __name__ == "__main__":
    build()
