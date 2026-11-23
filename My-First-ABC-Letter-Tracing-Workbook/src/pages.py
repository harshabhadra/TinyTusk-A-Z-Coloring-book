"""TinyTusk ABC Letter Tracing Workbook: every interior page.

Reuses the coloring book's page frame, footer, fonts and the 26 cleaned line-art animals (../../src, ../../clean).
Black & white interior (pure black ink + greys), 8.5 x 11 in, no bleed, 0.5 in safe margin.

Usage (from anywhere):  python3 My-First-ABC-Letter-Tracing-Workbook/src/pages.py   -> My-First-ABC-Letter-Tracing-Workbook/pages/*.pdf (+ .png previews)
                        python3 My-First-ABC-Letter-Tracing-Workbook/src/pages.py A B  (just those letter spreads)
"""
import os, random, string, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)                       # My-First-ABC-Letter-Tracing-Workbook/
sys.path[:0] = [HERE, os.path.join(os.path.dirname(BOOK), "src"), os.path.join(os.path.dirname(BOOK), "brand")]
from reportlab.pdfgen import canvas                # noqa: E402
from reportlab.lib.colors import Color, white, black  # noqa: E402
from reportlab.pdfbase import pdfmetrics           # noqa: E402
import layout                                      # noqa: E402  (registers fonts; chdir to repo root)
from layout import Page, W, H, PT, CAP, ANIMALS    # noqa: E402
from frontmatter import Front                      # noqa: E402
import strokes                                     # noqa: E402
import brand                                       # noqa: E402  (../../brand: logo, mascot, series pages)

OUT = "My-First-ABC-Letter-Tracing-Workbook/pages"
INK = black
GUIDE = Color(0.55, 0.55, 0.55)        # guide lines
TRACE = Color(0.45, 0.45, 0.45)        # dashed letters
PILL = Color(0.92, 0.92, 0.92)         # light grey fill (B&W interior, replaces the yellow)
TITLE = "TinyTusk ABC Letter Tracing Workbook"
AUTHOR = "TinyTusk Books"

KEY = "abc-tracing"                     # this book in brand.BOOKS
FRONT = ["01_title", "02_copyright", "03_name", "04_warmup_lines", "05_warmup_zigzag", "06_warmup_curves"]
BACK = ["59_review_upper", "60_review_lower", "61_certificate", "62_more_books"]
PAGES = 62


def letter_pages(L):
    n = 7 + 2 * (ord(L) - ord("A"))
    return n, n + 1                     # left page (big letters + animal), right page (practice)


class TP(Front):
    """Tracing page helpers on top of the coloring book's Page/Front."""

    # ---- handwriting guide: cap line, dashed midline, baseline, descender line -------------
    def guide(self, x0, x1, base, u, desc=True):
        c = self.c
        c.saveState(); c.setLineCap(1)
        c.setStrokeColor(GUIDE)
        c.setLineWidth(1.2); c.line(self.X(x0), self.Y(base - 2 * u), self.X(x1), self.Y(base - 2 * u))
        c.setDash(5, 4); c.setLineWidth(1); c.line(self.X(x0), self.Y(base - u), self.X(x1), self.Y(base - u))
        c.setDash(); c.setStrokeColor(INK); c.setLineWidth(1.6)
        c.line(self.X(x0), self.Y(base), self.X(x1), self.Y(base))
        if desc:
            c.setStrokeColor(GUIDE); c.setDash(1, 4); c.setLineWidth(1)
            c.line(self.X(x0), self.Y(base + u), self.X(x1), self.Y(base + u))
        c.restoreState()

    # ---- one stroke letter -------------------------------------------------------------------
    def letter(self, ch, x, base, u, style="dash", numbers=False, lw=None, dots=None):
        """style: 'dash' (grey dashes to trace), 'solid' (black model), 'start' (start dots only),
        'blank' (nothing). numbers=True adds numbered badges + direction arrows (big letters).
        Returns the letter's ink width in inches."""
        if ch == " " or style == "blank":
            return strokes.width(ch) * u
        c = self.c
        upt = u * PT
        lw = lw or max(1.6, upt * 0.075)
        dots = (style == "start" or numbers or style == "solid") if dots is None else dots
        c.saveState(); c.setLineCap(1); c.setLineJoin(1)
        P = lambda gx, gy: (self.X(x + gx * u), self.Y(base - gy * u))
        badges = []
        for k, (pts, is_dot) in enumerate(strokes.polylines(ch), 1):
            if is_dot:
                c.setFillColor(INK if style == "solid" else TRACE)
                if style != "start":
                    c.circle(*P(*pts[0]), lw * 0.9, stroke=0, fill=1)
                continue
            if style in ("dash", "solid"):
                c.setStrokeColor(INK if style == "solid" else TRACE); c.setLineWidth(lw)
                c.setDash() if style == "solid" else c.setDash(lw * 1.6, lw * 1.7)
                p = c.beginPath(); p.moveTo(*P(*pts[0]))
                for q in pts[1:]:
                    p.lineTo(*P(*q))
                c.drawPath(p, stroke=1, fill=0)
            if dots:
                c.setDash(); c.setFillColor(INK)
                c.circle(*P(*pts[0]), max(2.0, lw * 0.8), stroke=0, fill=1)
            if numbers:
                self._badge_arrow(pts, k, P, upt, badges, lw)
        c.restoreState()
        return strokes.width(ch) * u

    def _badge_arrow(self, pts, k, P, upt, badges, lw):
        import math
        c = self.c
        sx, sy = P(*pts[0])
        # direction of travel at the start (in page points)
        j = 1
        while j < len(pts) - 1 and math.dist(P(*pts[0]), P(*pts[j])) < upt * 0.12:
            j += 1
        ex, ey = P(*pts[j]); dx, dy = ex - sx, ey - sy; d = math.hypot(dx, dy) or 1; dx, dy = dx / d, dy / d
        r = max(7, upt * 0.1)
        # badge behind the start point; if that bumps into another badge, try the sides
        dist = r + lw * 0.9 + 2
        cands = [(-dx, -dy), (-dy, dx), (dy, -dx), (-dx - dy, -dy + dx), (-dx + dy, -dy - dx)]
        for vx, vy in cands:
            n = math.hypot(vx, vy); bx, by = sx + vx / n * dist, sy + vy / n * dist
            if all(math.dist((bx, by), b) > 2.3 * r for b in badges):
                break
        badges.append((bx, by))
        c.setDash(); c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(1.3)
        c.circle(bx, by, r, stroke=1, fill=1)
        c.setFillColor(INK); fs = r * 1.35; c.setFont("Fredoka-SemiBold", fs)
        c.drawCentredString(bx, by - fs * CAP / 2, str(k))
        # small solid arrow alongside the first part of the stroke, showing which way to go
        acc, seg = 0.0, [pts[0]]
        for q in pts[1:]:
            acc += math.dist(P(*seg[-1]), P(*q)); seg.append(q)
            if acc > upt * 0.42:
                break
        off = lw * 0.5 + 6
        # put the arrow on the side away from the badge
        side = 1 if ((bx - sx) * -dy + (by - sy) * dx) < 0 else -1
        ap = []
        for i, q in enumerate(seg):
            qx, qy = P(*q)
            a_ = seg[min(i + 1, len(seg) - 1)]; b_ = seg[max(i - 1, 0)]
            tx, ty = P(*a_)[0] - P(*b_)[0], P(*a_)[1] - P(*b_)[1]; tn = math.hypot(tx, ty) or 1
            ap.append((qx + side * -ty / tn * off, qy + side * tx / tn * off))
        if len(ap) < 2 or acc < upt * 0.2:
            return
        c.setStrokeColor(INK); c.setLineWidth(1.6); c.setLineCap(1)
        p = c.beginPath(); p.moveTo(*ap[1] if len(ap) > 2 else ap[0])
        for q in ap[2:]:
            p.lineTo(*q)
        c.drawPath(p, stroke=1, fill=0)
        (x1, y1), (x2, y2) = ap[-2], ap[-1]
        tx, ty = x2 - x1, y2 - y1; tn = math.hypot(tx, ty) or 1; tx, ty = tx / tn, ty / tn
        h = 5.5
        p = c.beginPath(); p.moveTo(x2 + tx * 2, y2 + ty * 2)
        p.lineTo(x2 - tx * h - ty * h * 0.6, y2 - ty * h + tx * h * 0.6)
        p.lineTo(x2 - tx * h + ty * h * 0.6, y2 - ty * h - tx * h * 0.6); p.close()
        c.setFillColor(INK); c.drawPath(p, stroke=0, fill=1)

    def word(self, w, x, base, u, style="dash", gap=0.35, dots=None):
        for ch in w:
            x += self.letter(ch, x, base, u, style, dots=dots) + gap * u
        return x

    def header_pill(self, text, cy=1.1, size=24, sub=None):
        """Grey pill with a title, centred near the top of the page."""
        c = self.c
        w = pdfmetrics.stringWidth(text, "Fredoka-Bold", size) / PT + 0.7
        h = 0.62
        c.setFillColor(PILL); c.setStrokeColor(INK); c.setLineWidth(2.5)
        self.rrect(W / 2 - w / 2, cy - h / 2, W / 2 + w / 2, cy + h / 2, h / 2, stroke=1, fill=1)
        c.setFillColor(INK); c.setFont("Fredoka-Bold", size)
        c.drawCentredString(self.X(W / 2), self.Y(cy + size * CAP / PT / 2), text)
        if sub:
            self.centred(sub, cy + h / 2 + 0.33, "Fredoka-Medium", 14)

    # ---- practice row: letters (or a word) repeated along one guide ---------------------------
    def row(self, item, base, u, plan, x0=0.95, x1=7.55, gap=None):
        """plan: one style per repetition ('solid', 'dash', 'start', 'blank'); repetitions that don't
        fit are dropped. Words never get start dots except on the black model."""
        self.guide(x0, x1, base, u)
        gap = gap if gap is not None else (0.6 if len(item) == 1 else 1.2)
        wid = strokes.word_width(item, 0.35) * u
        x = x0 + 0.2
        for st in plan:
            if x + wid > x1 - 0.1:
                break
            dots = None if len(item) == 1 or " " in item else (False if st != "start" else None)
            self.word(item, x, base, u, st, dots=dots)
            x += wid + gap * u

    # ======================================================================================
    def letter_left(self, L):
        """Big Aa with stroke numbers and arrows + the animal to colour + one row of each."""
        c = self.c
        n, _ = letter_pages(L)
        animal = ANIMALS[L]
        self.border()
        self.header_pill(f"{L} is for {animal}", cy=1.12, size=26)
        u = 1.05
        base = 1.75 + 2 * u + 0.12
        up, lo = L, L.lower()
        wu, wl = strokes.width(up) * u, strokes.width(lo) * u
        x = 1.25
        x2 = x + wu + 0.6
        gx1 = x2 + wl + 0.45
        self.guide(0.85, gx1, base, u)
        self.letter(up, x, base, u, "dash", numbers=True, lw=8)
        self.letter(lo, x2, base, u, "dash", numbers=True, lw=8)
        # animal (line art to colour) to the right of the letters
        self.image(f"clean/{L}.png", (gx1 + 0.1, 1.6, 7.65, base + u))
        c.setFillColor(INK); c.setFont("Fredoka-Medium", 13)
        c.drawCentredString(self.X(W / 2), self.Y(base + u + 0.45),
                            "Trace with your finger, then with a pencil. Start at the dot and follow the arrows!")
        u2 = 0.36
        b = base + u + 0.75 + 2 * u2
        for item, plan in ((up, ["solid"] + ["dash"] * 14), (lo, ["solid"] + ["dash"] * 16),
                           (up + " " + lo, ["solid"] + ["dash"] * 8)):
            self.row(item, b, u2, plan, gap=0.6 if len(item) == 1 else 1.0)
            b += 3 * u2 + 0.24
        self.footer(n)

    def letter_right(self, L):
        """Practice on your own, the animal word, and a find-the-letter game."""
        c = self.c
        _, n = letter_pages(L)
        animal = ANIMALS[L]
        self.border()
        self.header_pill(f"Now you write {L} and {L.lower()}!", cy=1.12, size=24)
        u = 0.34
        b = 1.68 + 2 * u
        for item in (L, L.lower()):
            plan = ["solid", "dash", "dash", "start"] + ["blank"] * 12
            self.row(item, b, u, plan, gap=0.6 if len(item) == 1 else 1.0)
            b += 3 * u + 0.2
        b += 0.2
        uw = 0.34 if strokes.word_width(animal, 0.35) * 0.34 < 3.1 else 0.3
        c.setFillColor(INK); c.setFont("Fredoka-SemiBold", 15)
        c.drawString(self.X(0.95), self.Y(b + 0.08), f"Trace the word:  {animal}")
        b += 0.3 + 2 * uw
        self.row(animal, b, uw, ["solid", "dash"], gap=1.0)
        b += 3 * uw + 0.2
        self.row(animal, b, uw, ["dash", "blank"], gap=1.0)
        b += 3 * uw + 0.1
        # find-the-letter game
        c.setFillColor(INK); c.setFont("Fredoka-SemiBold", 15)
        c.drawString(self.X(0.95), self.Y(b + 0.08), f"Color every balloon with {L} or {L.lower()} in it!")
        rng = random.Random(ord(L))
        others = [ch for ch in string.ascii_letters if ch.lower() != L.lower() and ch not in "lIiJjOo0"]
        cells = [L, L.lower(), L, L.lower()] + rng.sample(others, 5)
        rng.shuffle(cells)
        r = 0.32
        cols = len(cells)
        for i, ch in enumerate(cells):
            cx = 1.3 + i * (5.9 / (cols - 1))
            cy = b + 0.35 + r + (0.14 if i % 2 else 0)
            c.setStrokeColor(INK); c.setLineWidth(1.3)
            c.line(self.X(cx), self.Y(cy + r), self.X(cx + (0.05 if i % 2 else -0.05)), self.Y(cy + r + 0.32))
            c.setFillColor(white); c.setLineWidth(2)
            c.ellipse(self.X(cx - r), self.Y(cy + r * 1.1), self.X(cx + r), self.Y(cy - r * 1.1), stroke=1, fill=1)
            c.setFillColor(INK); c.setFont("Fredoka-Bold", 28)
            c.drawCentredString(self.X(cx), self.Y(cy) - 28 * CAP / 2, ch)
        self.footer(n)

    # ---- front matter ------------------------------------------------------------------------
    def title_page(self):
        self.border()
        self.outline_centred("TinyTusk ABC", 1.75, 62)
        self.header_pill("Letter Tracing Workbook", cy=2.45, size=26)
        self.centred("Trace, write & color the alphabet with 26 baby animals", 3.25, "Fredoka-Medium", 17)
        # a traced "Aa Bb Cc" on a guide
        u = 0.55
        base = 3.65 + 2 * u
        self.guide(1.0, 7.5, base, u)
        x = 1.35
        for p in ("Aa", "Bb", "Cc"):
            for ch in p:
                x += self.letter(ch, x, base, u, "dash", lw=4) + 0.18
            x += 0.45
        boxes = [(0.95, 6.0, 2.95, 8.25), (3.25, 6.0, 5.25, 8.25), (5.55, 6.0, 7.55, 8.25)]
        for L, bx in zip("ABC", boxes):
            self.image(f"clean/{L}.png", bx)
        self.centred("Ages 3–5", 9.0, "Fredoka-Bold", 22)
        brand.lockup(self, 7.7, 10.3, gray=True)

    def name_page(self):
        self.border()
        self.outline_centred("This book", 1.85, 60)
        self.outline_centred("belongs to", 2.95, 60)
        c = self.c
        c.setFillColor(PILL); c.setStrokeColor(INK); c.setLineWidth(3)
        self.rrect(1.2, 3.35, 7.3, 4.85, 0.4, stroke=1, fill=1)
        self.line_for_name(1.7, 6.8, 4.45)
        self.centred("my name", 4.75, "Fredoka-Medium", 12)
        self.centred("Practice writing your name:", 5.55, "Fredoka-SemiBold", 18)
        u = 0.36
        for b in (6.45, 7.75):
            self.guide(0.95, 7.55, b, u)
        brand.mascot_tip(self, (1.0, 8.05, 2.55, 9.55), "Write your name, then let's trace together!",
                         line=True, bubble_w=3.6, size=16)
        self.footer()

    def warmup(self, kind, n):
        """Pencil warm-up: dashed paths from an animal to a star."""
        c = self.c
        self.border()
        titles = {"lines": ("Pencil warm-up: lines", "Trace each path from the animal to the star."),
                  "zigzag": ("Warm-up: slants & zigzags", "Go slowly and stay on the dashes."),
                  "curves": ("Warm-up: waves & loops", "Curvy lines help with letters like S, C and O.")}
        t, sub = titles[kind]
        self.header_pill(t, cy=1.12, size=24, sub=sub)
        animals = {"lines": "BDHKMP", "zigzag": "CGJNST", "curves": "OQUVWY"}[kind]
        rows = 6
        top, step = 2.15, 1.22
        import math
        for i, L in enumerate(animals[:rows]):
            cy = top + i * step + 0.45
            self.image(f"clean/{L}.png", (0.95, cy - 0.5, 1.95, cy + 0.5))
            self.star(7.15, cy, 0.34, 0.15, width=2.5)
            x0, x1 = 2.15, 6.65
            pts = []
            N = 240
            for k in range(N + 1):
                t_ = k / N; x = x0 + (x1 - x0) * t_
                if kind == "lines":
                    y = cy
                    if i >= 3:              # last three rows: up-and-down steps for vertical strokes
                        pass
                elif kind == "zigzag":
                    per = [0.9, 0.75, 0.6, 0.9, 0.6, 0.5][i]
                    ph = (x - x0) / per
                    tri = 2 * abs(ph - math.floor(ph + 0.5))
                    amp = 0.32
                    y = cy + amp * (tri * 2 - 1) if i % 3 != 2 else cy + amp * (1 if int(ph * 2) % 2 else -1)
                else:
                    per = [1.5, 1.1, 0.9, 1.5, 1.1, 0.9][i]
                    y = cy - 0.3 * math.sin(2 * math.pi * (x - x0) / per)
                pts.append((x, y))
            if kind == "zigzag" and i % 3 == 2:        # square "castle" wave
                pts = []
                x, up = x0, False
                pts.append((x, cy + 0.3))
                while x < x1 - 0.01:
                    y = cy - 0.3 if up else cy + 0.3
                    pts.append((x, y)); x = min(x1, x + 0.45); pts.append((x, y)); up = not up
            if kind == "curves" and i >= 3:            # loops
                pts = []
                R = [0.28, 0.24, 0.2][i - 3]
                adv = R * 1.9
                n_loops = int((x1 - x0 - 2 * R) / adv)
                for k in range(n_loops * 60 + 1):
                    a = 2 * math.pi * k / 60
                    pts.append((x0 + R + adv * k / 60 - R * math.cos(a) + R - R, cy - R * math.sin(a) * 1.0))
                pts = [(x0 + adv * k / 60 + R * (1 - math.cos(2 * math.pi * k / 60)), cy - R * math.sin(2 * math.pi * k / 60))
                       for k in range(n_loops * 60 + 1)]
            if kind == "lines" and i >= 3:             # vertical strokes
                c.saveState(); c.setStrokeColor(TRACE); c.setLineWidth(3.5); c.setLineCap(1); c.setDash(5, 6)
                for k in range(9):
                    xx = 2.4 + k * 0.5
                    h = [0.4, 0.45, 0.45][i - 3]
                    if i == 4:
                        c.line(self.X(xx - 0.15), self.Y(cy - h), self.X(xx + 0.15), self.Y(cy + h))
                    elif i == 5:
                        c.line(self.X(xx + 0.15), self.Y(cy - h), self.X(xx - 0.15), self.Y(cy + h))
                    else:
                        c.line(self.X(xx), self.Y(cy - h), self.X(xx), self.Y(cy + h))
                    c.setFillColor(INK); c.circle(self.X(xx + (0 if i == 3 else (-0.15 if i == 4 else 0.15))), self.Y(cy - h), 3, stroke=0, fill=1)
                c.restoreState()
                continue
            c.saveState(); c.setStrokeColor(TRACE); c.setLineWidth(3.5); c.setLineCap(1); c.setLineJoin(1)
            c.setDash(5, 6)
            p = c.beginPath(); p.moveTo(self.X(pts[0][0]), self.Y(pts[0][1]))
            for q in pts[1:]:
                p.lineTo(self.X(q[0]), self.Y(q[1]))
            c.drawPath(p, stroke=1, fill=0)
            c.setFillColor(INK); c.circle(self.X(pts[0][0]), self.Y(pts[0][1]), 4, stroke=0, fill=1)
            c.restoreState()
        self.footer(n)

    def review(self, upper, n):
        self.border()
        t = "Trace the ABCs: big letters" if upper else "Trace the abcs: small letters"
        self.header_pill(t, cy=1.12, size=24)
        letters = string.ascii_uppercase if upper else string.ascii_lowercase
        u = 0.36
        b = 1.75 + 2 * u
        x0, x1 = 0.95, 7.55
        i = 0
        rows = 0
        while i < len(letters):
            self.guide(x0, x1, b, u)
            x = x0 + 0.2
            while i < len(letters) and x + strokes.width(letters[i]) * u < x1 - 0.1:
                x += self.letter(letters[i], x, b, u, "dash") + 1.0 * u
                i += 1
            b += 3 * u + 0.22; rows += 1
        self.centred("Now write them all by yourself!", b - 2 * u + 0.1, "Fredoka-SemiBold", 15)
        b += 0.3
        while b + u < 9.6:
            self.guide(x0, x1, b, u)
            b += 3 * u + 0.22
        self.footer(n)

    def certificate(self):
        self.border()
        c = self.c
        c.setStrokeColor(INK); c.setLineWidth(2)
        self.rrect(0.8, 0.8, 7.7, 9.55, 0.2)
        self.outline_centred("Super writer!", 2.05, 72)
        self.star(W / 2, 3.65, 1.25, 0.55)
        self.centred("ABC", 3.85, "Fredoka-Bold", 30)
        self.centred("This certificate is awarded to", 5.45, "Fredoka-SemiBold", 22)
        self.line_for_name(1.6, 6.9, 6.35)
        self.centred("for tracing and writing every letter from A to Z!", 7.05, "Fredoka-Medium", 18)
        self.line_for_name(1.6, 3.9, 8.1); self.line_for_name(4.6, 6.9, 8.1)
        c.setFont("Fredoka-Medium", 13)
        c.drawCentredString(self.X(2.75), self.Y(8.4), "date")
        c.drawCentredString(self.X(5.75), self.Y(8.4), "signed")
        for x, y, r in ((1.5, 3.2, 0.32), (7.0, 3.2, 0.32), (1.9, 4.4, 0.2), (6.6, 4.4, 0.2)):
            self.star(x, y, r, r * 0.45, width=2.5)
        self.image("clean/Z.png", (1.0, 8.55, 2.2, 9.45))
        self.image(brand.mascot(line=True), (6.3, 8.5, 7.5, 9.45))
        self.footer()

    # Front.pill uses the yellow fill; keep the interior black & white
    def pill(self, *a, **k):
        raise NotImplementedError


def make(name, fn, *args):
    pdf = f"{OUT}/{name}.pdf"
    c = canvas.Canvas(pdf, pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setAuthor(AUTHOR); c.setTitle(f"{TITLE} - {name}")
    fn(TP(c), *args)
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "100", "-singlefile", pdf, pdf[:-4]], check=True)
    print(pdf)


def build_letter(L):
    a, b = letter_pages(L)
    make(f"{a:02d}_{L}", TP.letter_left, L)
    make(f"{b:02d}_{L}_practice", TP.letter_right, L)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    todo = [a.upper() for a in sys.argv[1:]]
    if not todo:
        make("01_title", TP.title_page)
        make("02_copyright", brand.copyright_page, TITLE)
        make("03_name", TP.name_page)
        make("04_warmup_lines", TP.warmup, "lines", 4)
        make("05_warmup_zigzag", TP.warmup, "zigzag", 5)
        make("06_warmup_curves", TP.warmup, "curves", 6)
        make("59_review_upper", TP.review, True, 59)
        make("60_review_lower", TP.review, False, 60)
        make("61_certificate", TP.certificate)
        make("62_more_books", brand.more_books_page, KEY)
        todo = list(string.ascii_uppercase)
    for L in todo:
        build_letter(L)
