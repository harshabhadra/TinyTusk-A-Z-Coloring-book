"""Title page (1), name page (2), certificate (29) and blank last page (30).
Usage: python3 src/frontmatter.py   -> pages/00_title.pdf, 01_name.pdf, 29_certificate.pdf, 30_blank.pdf (+ PNG previews)
"""
import math, subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from layout import Page, W, H, PT, CAP, INK, PILL_FILL, LETTER_FONT

TITLE = "My First A to Z Animals"
SUBTITLE = "Copy Coloring Book"
TAGLINE = "26 cute baby animals to copy, color & learn the alphabet"
AUTHOR = "TinyTusk"


class Front(Page):
    def centred(self, text, y_base, font, size, max_w=6.6, min_size=12):
        size = self.fit_text(text, font, size, max_w, min_size)
        self.c.setFillColor(INK); self.c.setFont(font, size)
        self.c.drawCentredString(self.X(W / 2), self.Y(y_base), text)
        return size

    def outline_centred(self, text, y_base, size, font=LETTER_FONT, width=3, max_w=6.8):
        size = min(size, max_w * PT / (pdfmetrics.stringWidth(text, font, size) / size))
        w = pdfmetrics.stringWidth(text, font, size) / PT
        self.outline_text(text, W / 2 - w / 2, y_base, size, font=font, width=width)

    def pill(self, text, cy, font="Fredoka-Bold", size=24, pad=0.35, h=0.62):
        w = pdfmetrics.stringWidth(text, font, size) / PT + 2 * pad
        c = self.c
        c.setFillColor(PILL_FILL); c.setStrokeColor(INK); c.setLineWidth(2.5)
        self.rrect(W / 2 - w / 2, cy - h / 2, W / 2 + w / 2, cy + h / 2, h / 2, stroke=1, fill=1)
        c.setFillColor(INK); c.setFont(font, size)
        c.drawCentredString(self.X(W / 2), self.Y(cy + size * CAP / PT / 2), text)

    def line_for_name(self, x0, x1, y):
        c = self.c
        c.setStrokeColor(INK); c.setLineWidth(2); c.setDash(1, 6); c.setLineCap(1)
        c.line(self.X(x0), self.Y(y), self.X(x1), self.Y(y))
        c.setDash(); c.setLineCap(0)

    def star(self, cx, cy, r_out, r_in, width=4):
        c = self.c
        p = c.beginPath()
        for k in range(10):
            r = r_out if k % 2 == 0 else r_in
            a = math.radians(90 + k * 36)
            x, y = self.X(cx + r * math.cos(a)), self.Y(cy - r * math.sin(a))
            p.moveTo(x, y) if k == 0 else p.lineTo(x, y)
        p.close()
        c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(width); c.setLineJoin(1)
        c.drawPath(p, stroke=1, fill=1)

    # --- pages -------------------------------------------------------------------
    def title_page(self):
        self.border()
        self.outline_centred("My First", 1.65, 54)
        self.outline_centred("A to Z Animals", 2.75, 66)
        self.pill(SUBTITLE, 3.3)
        self.centred(TAGLINE, 4.05, "Fredoka-Medium", 18)
        # four animals (line art, to color) in a 2 x 2 grid
        boxes = [(0.9, 4.35, 4.15, 6.75), (4.35, 4.35, 7.6, 6.75),
                 (0.9, 6.9, 4.15, 9.3), (4.35, 6.9, 7.6, 9.3)]
        for L, b in zip("AELP", boxes):
            self.image(f"clean/{L}.png", b)
        self.centred("Ages 3\u20138", 9.62, "Fredoka-Bold", 20)
        self.c.setFont("Fredoka-Medium", 14)
        self.c.drawRightString(self.X(7.7), self.Y(10.25), f"by {AUTHOR}")

    def name_page(self):
        self.border()
        self.outline_centred("This book", 1.85, 60)
        self.outline_centred("belongs to", 2.95, 60)
        c = self.c
        # name plate
        c.setFillColor(PILL_FILL); c.setStrokeColor(INK); c.setLineWidth(3)
        self.rrect(1.2, 3.35, 7.3, 4.85, 0.4, stroke=1, fill=1)
        self.line_for_name(1.7, 6.8, 4.45)
        self.centred("my name", 4.75, "Fredoka-Medium", 12)
        # age + drawing frame
        self.centred("I am ______ years old", 5.55, "Fredoka-SemiBold", 22)
        c.setStrokeColor(INK); c.setLineWidth(2); c.setDash(6, 4)
        self.rrect(1.2, 5.95, 7.3, 9.45, 0.3)
        c.setDash()
        self.centred("Draw your favorite animal here!", 6.35, "Fredoka-SemiBold", 16)
        # two small helpers peeking in the corners of the frame
        self.image("clean/R.png", (5.75, 7.75, 7.15, 9.35))
        self.image("clean/F.png", (1.35, 8.1, 2.65, 9.35))
        self.footer()

    def certificate(self):
        self.border()
        c = self.c
        # double frame inside the border
        c.setStrokeColor(INK); c.setLineWidth(2)
        self.rrect(0.8, 0.8, 7.7, 9.55, 0.2)
        self.outline_centred("Well done!", 2.05, 78)
        self.star(W / 2, 3.65, 1.25, 0.55)
        self.centred("26", 3.85, "Fredoka-Bold", 34)
        self.centred("This certificate is awarded to", 5.45, "Fredoka-SemiBold", 22)
        self.line_for_name(1.6, 6.9, 6.35)
        self.centred("for coloring all 26 animals from A to Z!", 7.05, "Fredoka-Medium", 18)
        self.line_for_name(1.6, 3.9, 8.1); self.line_for_name(4.6, 6.9, 8.1)
        c.setFont("Fredoka-Medium", 13)
        c.drawCentredString(self.X(2.75), self.Y(8.4), "date")
        c.drawCentredString(self.X(5.75), self.Y(8.4), "signed")
        # little stars to color
        for x, y, r in ((1.5, 3.2, 0.32), (7.0, 3.2, 0.32), (1.9, 4.4, 0.2), (6.6, 4.4, 0.2)):
            self.star(x, y, r, r * 0.45, width=2.5)
        self.image("clean/E.png", (1.0, 8.55, 2.2, 9.45))
        self.image("clean/L.png", (6.3, 8.55, 7.5, 9.45))
        self.footer()


def make(name, fn):
    pdf = f"pages/{name}.pdf"
    c = canvas.Canvas(pdf, pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setAuthor(AUTHOR); c.setTitle(f"{TITLE} - {name}")
    if fn:
        fn(Front(c))
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "100", "-singlefile", pdf, pdf[:-4]], check=True)
    print(pdf)


if __name__ == "__main__":
    make("00_title", Front.title_page)
    make("01_name", Front.name_page)
    make("29_certificate", Front.certificate)
    make("30_blank", None)
