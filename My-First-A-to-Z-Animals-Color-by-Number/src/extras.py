"""Non-puzzle pages: 1 title, 2 name, 3 how to, 30 certificate, 31-37 answer key, 38 blank.
Name page and certificate are the A-Z book's own designs (../src/frontmatter.py).
Usage: python3 src/extras.py   (run src/puzzle.py first: it writes art/<L>_puzzle.png + numbers)
"""
import json, math, string, subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from common import *
from frontmatter import Front                 # ../src/frontmatter.py
from puzzle import Puzzle

LETTERS = string.ascii_uppercase


def info(L):
    return json.load(open(f"{ART_DIR}/{L}_numbers.json"))


class Extra(Front, Puzzle):
    def puzzle_pic(self, L, box):
        self.image(f"{ART_DIR}/{L}_puzzle.png", box)
        self.numbers(info(L), box)

    def title_page(self):
        self.border()
        self.outline_centred("My First", 1.6, 52)
        self.outline_centred("A to Z Animals", 2.65, 64)
        self.pill("Color by Number", 3.2)
        self.centred("26 cute baby animals to color by number", 3.95, "Fredoka-Medium", 18)
        boxes = [(0.9, 4.25, 4.15, 6.7), (4.35, 4.25, 7.6, 6.7),
                 (0.9, 6.85, 4.15, 9.3), (4.35, 6.85, 7.6, 9.3)]
        for L, b in zip("BEJW", boxes):
            self.puzzle_pic(L, b)
        self.centred(AGES, 9.62, "Fredoka-Bold", 20)
        self.c.setFont("Fredoka-Medium", 14)
        self.c.drawRightString(self.X(7.7), self.Y(10.25), f"by {AUTHOR}")

    def how_to(self):
        c = self.c
        self.border()
        self.outline_centred("How to color", 1.55, 54)
        self.outline_centred("by number", 2.5, 54)
        # example: numbered jellyfish -> arrow -> coloured jellyfish
        self.puzzle_pic("J", (0.95, 2.75, 3.75, 5.15))
        self.image(f"{REPO}/colored/J.png", (4.75, 2.75, 7.55, 5.15))
        c.setFillColor(HexColor(PALETTE["Orange"])); c.setStrokeColor(INK); c.setLineWidth(2); c.setLineJoin(1)
        ax, ay = 3.85, 3.95
        p = c.beginPath()
        for i, (dx, dy) in enumerate(((0, -0.12), (0.45, -0.12), (0.45, -0.26), (0.8, 0), (0.45, 0.26), (0.45, 0.12), (0, 0.12))):
            (p.moveTo if i == 0 else p.lineTo)(self.X(ax + dx), self.Y(ay + dy))
        p.close(); c.drawPath(p, stroke=1, fill=1)
        # three steps
        steps = ["Find a number in the picture.",
                 "Find the same number in the Color key.",
                 "Color the space with that crayon!"]
        y = 5.6
        for k, s in enumerate(steps, 1):
            c.setFillColor(PILL_FILL); c.setStrokeColor(INK); c.setLineWidth(2)
            c.circle(self.X(1.45), self.Y(y), 0.24 * PT, stroke=1, fill=1)
            c.setFillColor(INK); c.setFont("Fredoka-Bold", 20)
            c.drawCentredString(self.X(1.45), self.Y(y) - 20 * CAP / 2, str(k))
            c.setFont("Fredoka-SemiBold", 19)
            c.drawString(self.X(1.85), self.Y(y) - 19 * CAP / 2, s)
            y += 0.55
        # tips
        c.setFont("Fredoka-Medium", 14)
        for t in ["Spaces with no number stay white.",
                  "Tiny bits are already colored for you.",
                  "Check your picture with the answers at the back of the book."]:
            c.setFillColor(HexColor(PALETTE["Pink"])); c.setStrokeColor(INK); c.setLineWidth(1.2)
            c.circle(self.X(1.45), self.Y(y - 0.06), 0.07 * PT, stroke=1, fill=1)
            c.setFillColor(INK); c.drawString(self.X(1.7), self.Y(y), t); y += 0.3
        # crayons you need
        y += 0.15
        self.centred("The 12 crayons you need", y, "Fredoka-Bold", 16)
        cols, x0, cw = 4, 0.95, 1.7
        for k, name in enumerate(ORDER):
            row, col = divmod(k, cols)
            cx, cy = x0 + col * cw, y + 0.42 + row * 0.38
            self.crayon(cx, cy, name, length=0.55, h=0.22)
            fs = self.fit_text(name, "Fredoka-Medium", 12, cw - 0.68, 9)
            c.setFillColor(INK); c.setFont("Fredoka-Medium", fs)
            c.drawString(self.X(cx + 0.62), self.Y(cy) - fs * CAP / 2, name)

    def answers(self, letters, num):
        c = self.c
        self.border()
        self.outline_centred("Answer key", 1.45, 48)
        cells = [(0.85, 1.75, 4.2, 5.65), (4.3, 1.75, 7.65, 5.65),
                 (0.85, 5.75, 4.2, 9.65), (4.3, 5.75, 7.65, 9.65)]
        for L, (x0, y0, x1, y1) in zip(letters, cells):
            c.setStrokeColor(INK); c.setLineWidth(1.5); c.setDash(4, 3)
            self.rrect(x0, y0, x1, y1 - 0.05, 0.15); c.setDash()
            self.image(f"{REPO}/colored/{L}.png", (x0 + 0.15, y0 + 0.15, x1 - 0.15, y1 - 0.6))
            c.setFillColor(INK); c.setFont("Fredoka-Bold", 15)
            c.drawCentredString(self.X((x0 + x1) / 2), self.Y(y1 - 0.25),
                                f"{L} is for {ANIMALS[L]}  ·  page {4 + ord(L) - 65}")
        if len(letters) <= 2:                      # last page: a cheer in the empty half
            self.outline_centred("You did it!", 7.0, 60)
            self.star(W / 2, 8.35, 0.85, 0.38)
            for x, y, r in ((2.0, 8.0, 0.3), (6.5, 8.0, 0.3), (2.7, 9.0, 0.2), (5.8, 9.0, 0.2)):
                self.star(x, y, r, r * 0.45, width=2.5)
        self.footer(num)


def make(name, fn, *args):
    pdf = f"{PAGES_DIR}/{name}.pdf"
    c = canvas.Canvas(pdf, pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setAuthor(AUTHOR); c.setTitle(f"{TITLE} - {name}")
    if fn:
        fn(Extra(c), *args)
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "100", "-singlefile", pdf, pdf[:-4]], check=True)
    print(pdf)


if __name__ == "__main__":
    make("01_title", Extra.title_page)
    make("02_name", Extra.name_page)
    make("03_how_to", Extra.how_to)
    make("30_certificate", Extra.certificate)
    for k in range(7):
        make(f"{31 + k}_answers", Extra.answers, LETTERS[4 * k:4 * k + 4], 31 + k)
    make("38_blank", None)
