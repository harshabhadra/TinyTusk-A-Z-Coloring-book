"""TinyTusk "Trace & Write the Alphabet": every interior page (80 pages).

A practice-heavy handwriting workbook: one full page per uppercase letter, one per lowercase letter,
each with six rows that fade from dashed letters -> start dots -> blank lines; then words and short sentences.
The 26 baby animals appear as small accents (no colouring pages).

Reuses the coloring book's page frame, footer, fonts and cleaned animals (../../src, ../../clean).
Black & white interior, 8.5 x 11 in, no bleed, 0.5 in safe margin.

Usage:  python3 Trace-and-Write-the-Alphabet/src/pages.py          -> Trace-and-Write-the-Alphabet/pages/*.pdf + .png
        python3 Trace-and-Write-the-Alphabet/src/pages.py A b      (just those letter pages)
"""
import math, os, random, string, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(os.path.dirname(BOOK), "src")]
from reportlab.pdfgen import canvas                # noqa: E402
from reportlab.lib.colors import Color, white, black  # noqa: E402
from reportlab.pdfbase import pdfmetrics           # noqa: E402
import layout                                      # noqa: E402  (registers fonts; chdir to repo root)
from layout import W, H, PT, CAP, ANIMALS          # noqa: E402
from frontmatter import Front                      # noqa: E402
import strokes                                     # noqa: E402

OUT = "Trace-and-Write-the-Alphabet/pages"
INK = black
GUIDE = Color(0.55, 0.55, 0.55)
TRACE = Color(0.45, 0.45, 0.45)
PILL = Color(0.92, 0.92, 0.92)
TITLE = "Trace & Write the Alphabet"
AUTHOR = "TinyTusk"

# two simple words per letter for the words section (all lowercase, stroke letters only)
WORDS = dict(a=("ant", "apple"), b=("bus", "bat"), c=("cat", "cup"), d=("dog", "duck"), e=("egg", "elf"),
             f=("fish", "fan"), g=("goat", "gift"), h=("hat", "hen"), i=("ink", "igloo"), j=("jam", "jet"),
             k=("kite", "key"), l=("leaf", "log"), m=("moon", "mop"), n=("nest", "net"), o=("ox", "otter"),
             p=("pig", "pen"), q=("queen", "quilt"), r=("ring", "rain"), s=("sun", "sock"), t=("tree", "top"),
             u=("up", "umbrella"), v=("van", "vest"), w=("web", "wig"), x=("fox", "box"), y=("yarn", "yo-yo"),
             z=("zoo", "zip"))
SENTENCES = [("L", "I see a lion."), ("F", "The frog can hop."), ("B", "A bear is big."),
             ("O", "The owl is up."), ("P", "I like the panda."), ("W", "A whale can swim."),
             ("T", "The tiger can run."), ("Y", "The yak is fun."), ("K", "A koala naps."),
             ("C", "The camel is tall."), ("Z", "A zebra is fast."), ("R", "I hug the rabbit.")]

# ---- page map ----------------------------------------------------------------------------------
UPPER0 = 4            # A on page 4 ... Z on 29
LOWER0 = 32           # a on page 32 ... z on 57
WORDS0 = 62           # 13 pages, two letters each: 62..74
SENT0 = 75            # 4 pages: 75..78
PAGES = 80


def page_order():
    o = ["01_title", "02_name", "03_chart"]
    o += [f"{UPPER0 + i:02d}_upper_{L}" for i, L in enumerate(string.ascii_uppercase)]
    o += ["30_review_upper", "31_missing_upper"]
    o += [f"{LOWER0 + i:02d}_lower_{L.lower()}" for i, L in enumerate(string.ascii_uppercase)]
    o += ["58_review_lower", "59_missing_lower", "60_match_1", "61_match_2"]
    o += [f"{WORDS0 + i:02d}_words_{string.ascii_lowercase[2 * i]}{string.ascii_lowercase[2 * i + 1]}" for i in range(13)]
    o += [f"{SENT0 + i:02d}_sentences_{i + 1}" for i in range(4)]
    o += ["79_certificate", "80_extra_practice"]
    assert len(o) == PAGES
    return o


class TP(Front):
    # ---- handwriting guide: cap line, dashed midline, baseline, optional descender line ----------
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

    # ---- one stroke letter (style: dash | solid | start | blank) -----------------------------------
    def letter(self, ch, x, base, u, style="dash", numbers=False, lw=None, dots=None):
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
                if style != "start" or ch == ".":
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
        c = self.c
        sx, sy = P(*pts[0])
        j = 1
        while j < len(pts) - 1 and math.dist(P(*pts[0]), P(*pts[j])) < upt * 0.12:
            j += 1
        ex, ey = P(*pts[j]); dx, dy = ex - sx, ey - sy; d = math.hypot(dx, dy) or 1; dx, dy = dx / d, dy / d
        r = max(7, upt * 0.1)
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
        acc, seg = 0.0, [pts[0]]
        for q in pts[1:]:
            acc += math.dist(P(*seg[-1]), P(*q)); seg.append(q)
            if acc > upt * 0.42:
                break
        off = lw * 0.5 + 6
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

    def header_pill(self, text, cy=1.05, size=24, x0=None, x1=None):
        c = self.c
        w = pdfmetrics.stringWidth(text, "Fredoka-Bold", size) / PT + 0.7
        h = 0.6
        cx = W / 2 if x0 is None else (x0 + x1) / 2
        c.setFillColor(PILL); c.setStrokeColor(INK); c.setLineWidth(2.5)
        self.rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, h / 2, stroke=1, fill=1)
        c.setFillColor(INK); c.setFont("Fredoka-Bold", size)
        c.drawCentredString(self.X(cx), self.Y(cy + size * CAP / PT / 2), text)

    def text(self, s, x, y, font="Fredoka-Medium", size=13, anchor="l"):
        c = self.c; c.setFillColor(INK); c.setFont(font, size)
        {"c": c.drawCentredString, "l": c.drawString, "r": c.drawRightString}[anchor](self.X(x), self.Y(y), s)

    def row(self, item, base, u, plan, x0=0.95, x1=7.55, gap=None, desc=True, lead=0.2):
        self.guide(x0, x1, base, u, desc)
        gap = gap if gap is not None else (0.6 if len(item) == 1 else 1.2)
        wid = strokes.word_width(item, 0.35) * u
        x = x0 + lead
        for st in plan:
            if x + wid > x1 - 0.1:
                break
            dots = None if len(item) == 1 else (False if st != "start" else None)
            self.word(item, x, base, u, st, dots=dots)
            x += wid + gap * u

    # ======================================================================================
    # one page per letter: six rows that fade from tracing to writing on your own
    FADE = [["solid"] + ["dash"] * 30,
            ["dash"] * 30,
            ["dash", "start"] * 15,
            ["start"] * 30,
            ["solid"],
            []]

    def letter_page(self, ch, n):
        c = self.c
        upper = ch.isupper()
        L = ch.upper()
        animal = ANIMALS[L]
        self.border()
        self.header_pill(f"Uppercase {ch}" if upper else f"Lowercase {ch}", cy=1.05, size=26)
        # demo letter with stroke numbers + arrows
        u = 0.66 if upper else 0.6
        base = 1.55 + 2 * u
        wd = strokes.width(ch) * u
        gx0, gx1 = 0.95, 3.3
        self.guide(gx0, gx1, base, u, desc=not upper)
        self.letter(ch, (gx0 + gx1) / 2 - wd / 2, base, u, "dash", numbers=True, lw=7)
        # how-to steps
        sx = 3.5
        self.text("How to write it:", sx, 1.85, "Fredoka-SemiBold", 15)
        for i, s in enumerate(("Start at the big dot.", "Follow the numbers", "and arrows.",
                               "Trace the grey letters,", "then write your own!")):
            self.text(s, sx, 2.17 + i * 0.25, "Fredoka-Medium", 12.5)
        # animal accent
        self.image(f"clean/{L}.png", (5.85, 1.45, 7.55, 2.95))
        self.text(f"{ch} is for {animal if upper else animal.lower()}", 6.7, 3.25, "Fredoka-SemiBold", 13, "c")
        # six fading rows
        if upper:
            u, pitch, first = 0.32, 0.98, 3.6 + 0.64 + 0.05
        else:
            u, pitch, first = 0.28, 0.99, 3.6 + 0.56 + 0.05
        for i, plan in enumerate(self.FADE):
            self.row(ch, first + i * pitch, u, plan, desc=not upper, gap=0.7)
        self.footer(n)

    def review(self, upper, n):
        self.border()
        self.header_pill("Trace the ABCs" if upper else "Trace the abcs", cy=1.05, size=26)
        letters = string.ascii_uppercase if upper else string.ascii_lowercase
        u = 0.34
        b = 1.65 + 2 * u
        x0, x1 = 0.95, 7.55
        i = 0
        while i < len(letters):
            self.guide(x0, x1, b, u, desc=not upper)
            x = x0 + 0.2
            while i < len(letters) and x + strokes.width(letters[i]) * u < x1 - 0.1:
                x += self.letter(letters[i], x, b, u, "dash") + 1.0 * u
                i += 1
            b += 3 * u + 0.2
        self.centred("Now write them all by yourself!", b - 2 * u + 0.05, "Fredoka-SemiBold", 15)
        b += 0.25
        while b + (u if not upper else 0) < 9.55:
            self.guide(x0, x1, b, u, desc=not upper)
            b += 3 * u + 0.2
        self.footer(n)

    def missing(self, upper, n):
        c = self.c
        self.border()
        self.header_pill("Fill in the missing letters", cy=1.05, size=24)
        self.centred("Some letters ran away! Write them in the empty boxes.", 1.72, "Fredoka-Medium", 14)
        letters = string.ascii_uppercase if upper else string.ascii_lowercase
        rng = random.Random(7 if upper else 11)
        gaps = set()
        for start in range(1, 26, 3):                        # one gap in every run of three (never 'A')
            gaps.add(min(25, start + rng.randrange(3)))
        u = 0.32
        cell = 0.92
        x0 = (W - 7 * cell) / 2
        b = 2.15 + 2 * u
        for r in range(4):
            row = letters[r * 7:(r + 1) * 7]
            self.guide(0.95, 7.55, b, u, desc=not upper)
            for k, ch in enumerate(row):
                cx = x0 + (k + 0.5) * cell
                if letters.index(ch) in gaps:
                    c.setStrokeColor(INK); c.setLineWidth(1.4); c.setDash(3, 3)
                    self.rrect(cx - 0.34, b - 2 * u - 0.1, cx + 0.34, b + (u if not upper else 0) + 0.06, 0.1)
                    c.setDash()
                else:
                    wd = strokes.width(ch) * u
                    self.letter(ch, cx - wd / 2, b, u, "solid", dots=False)
            b += (2 * u + 0.45) if upper else (3 * u + 0.25)
        # what comes next?
        b -= 2 * u - 0.15
        self.text("What comes next? Write the letter.", 0.95, b, "Fredoka-SemiBold", 15)
        picks = rng.sample(range(25), 3)
        u2 = 0.3
        for k, i in enumerate(sorted(picks)):
            col, rr = k % 3, k // 3
            bx = 0.95 + col * 2.22
            by = b + 0.35 + 2 * u2 + rr * 1.25
            self.guide(bx, bx + 2.0, by, u2, desc=not upper)
            ch = letters[i]
            self.letter(ch, bx + 0.25, by, u2, "solid", dots=False)
            c.setStrokeColor(INK); c.setLineWidth(1.4); c.setDash(3, 3)
            self.rrect(bx + 1.15, by - 2 * u2 - 0.08, bx + 1.75, by + (u2 if not upper else 0) + 0.05, 0.08)
            c.setDash()
        self.footer(n)

    def match(self, part, n):
        c = self.c
        self.border()
        self.header_pill("Match big and small letters", cy=1.05, size=24)
        self.centred("Draw a line from each big letter to its small letter.", 1.72, "Fredoka-Medium", 14)
        letters = string.ascii_uppercase[:13] if part == 1 else string.ascii_uppercase[13:]
        rng = random.Random(part * 5)
        right = list(letters)
        while any(a == b for a, b in zip(letters, right)):
            rng.shuffle(right)
        top, step, r = 2.3, 0.56, 0.22
        lx, rx = 2.2, 6.3
        for i, (a, b) in enumerate(zip(letters, right)):
            cy = top + i * step
            for x, ch, dot_dx in ((lx, a, 0.38), (rx, b.lower(), -0.38)):
                c.setStrokeColor(INK); c.setFillColor(white); c.setLineWidth(1.8)
                c.circle(self.X(x), self.Y(cy), r * PT, stroke=1, fill=1)
                c.setFillColor(INK); c.setFont("Fredoka-Bold", 22)
                c.drawCentredString(self.X(x), self.Y(cy) - 22 * CAP / 2, ch)
                c.circle(self.X(x + dot_dx), self.Y(cy), 3.2, stroke=0, fill=1)
        # small animal accents in the corners of the matching area
        L1, L2 = ("A", "M") if part == 1 else ("N", "Z")
        self.image(f"clean/{L1}.png", (0.85, 8.45, 1.85, 9.5))
        self.image(f"clean/{L2}.png", (6.65, 8.45, 7.65, 9.5))
        self.footer(n)

    def words_page(self, i, n):
        c = self.c
        a, b = string.ascii_lowercase[2 * i], string.ascii_lowercase[2 * i + 1]
        self.border()
        self.header_pill(f"Words with {a} and {b}", cy=1.05, size=24)
        self.image(f"clean/{a.upper()}.png", (0.85, 0.72, 1.75, 1.45))
        self.image(f"clean/{b.upper()}.png", (6.75, 0.72, 7.65, 1.45))
        u, pitch = 0.26, 0.9
        y = 1.75
        for ch in (a, b):
            for w in WORDS[ch]:
                ends = ch == "x"
                self.text(f"{w}" + ("   (ends with x)" if ends else ""), 0.95, y + 0.05, "Fredoka-SemiBold", 13)
                ww = strokes.word_width(w, 0.35) * u
                gap = 1.3
                reps = int((7.45 - 0.95 - 0.2 + gap * u) // (ww + gap * u))
                b1 = y + 0.2 + 2 * u
                self.row(w, b1, u, ["solid"] + ["dash"] * (reps - 1), gap=gap)
                self.row(w, b1 + pitch, u, ["dash"] + ["blank"] * 9, gap=gap)
                y = b1 + pitch + u + 0.17
        self.footer(n)

    def sentences_page(self, k, n):
        self.border()
        self.header_pill("Trace and write the sentence", cy=1.05, size=24)
        x0, x1 = 2.0, 7.55
        y = 1.6
        for L, s in SENTENCES[3 * k:3 * k + 3]:
            units = strokes.word_width(s, 0.35)
            u = min(0.22, (x1 - x0 - 0.35) / units)
            self.image(f"clean/{L}.png", (0.85, y + 0.1, 1.85, y + 1.3))
            b = y + 0.1 + 2 * u
            self.row(s, b, u, ["dash"], x0=x0, x1=x1, gap=1)
            self.row(s, b + 3 * u + 0.1, u, ["dash"], x0=x0, x1=x1, gap=1)
            self.row(s, b + 2 * (3 * u + 0.1), u, [], x0=x0, x1=x1)
            y = b + 2 * (3 * u + 0.1) + u + 0.2
        self.footer(n)

    # ---- front matter ------------------------------------------------------------------------
    def title_page(self):
        self.border()
        self.outline_centred("Trace & Write", 1.75, 64)
        self.outline_centred("the Alphabet", 2.85, 64)
        self.header_pill("Uppercase  •  Lowercase  •  Words", cy=3.45, size=20)
        self.centred("Handwriting practice from A to Z, with the TinyTusk baby animals", 4.15, "Fredoka-Medium", 16)
        u = 0.5
        base = 4.55 + 2 * u
        self.guide(1.0, 7.5, base, u)
        x = 1.4
        for p in ("Aa", "Bb", "Cc"):
            for ch in p:
                x += self.letter(ch, x, base, u, "dash", lw=4) + 0.15
            x += 0.45
        boxes = [(0.95 + i * 1.33, 6.9, 0.95 + i * 1.33 + 1.25, 8.4) for i in range(5)]
        for L, bx in zip("ABCDE", boxes):
            self.image(f"clean/{L}.png", bx)
        self.centred("Ages 3–5", 9.05, "Fredoka-Bold", 22)
        self.c.setFont("Fredoka-Medium", 14)
        self.c.drawRightString(self.X(7.7), self.Y(10.25), f"by {AUTHOR}")

    def name_page(self):
        c = self.c
        self.border()
        self.outline_centred("This book belongs to", 1.7, 46)
        c.setFillColor(PILL); c.setStrokeColor(INK); c.setLineWidth(3)
        self.rrect(1.2, 2.05, 7.3, 3.2, 0.35, stroke=1, fill=1)
        self.line_for_name(1.7, 6.8, 2.85)
        self.centred("How to use this book", 3.95, "Fredoka-Bold", 22)
        tips = ["1.  Each letter has its own page. Do one page a day.",
                "2.  Trace the big letter with a finger first, following the numbers.",
                "3.  Hold the pencil and trace the grey dashed letters.",
                "4.  Next, start at each dot and write the letter.",
                "5.  On the empty lines, write the letter all by yourself!",
                "6.  Say the letter's sound and the animal's name out loud."]
        for i, t in enumerate(tips):
            self.text(t, 1.05, 4.5 + i * 0.42, "Fredoka-Medium", 15)
        self.text("Grown-ups: short, happy sessions work best. Praise effort, not perfection.",
                  W / 2, 7.25, "Fredoka-Medium", 12.5, "c")
        self.image("clean/K.png", (1.0, 7.6, 2.6, 9.55))
        self.image("clean/P.png", (3.45, 7.6, 5.05, 9.55))
        self.image("clean/S.png", (5.9, 7.6, 7.5, 9.55))
        self.footer()

    def chart(self):
        c = self.c
        self.border()
        self.header_pill("My Alphabet Animals", cy=1.05, size=26)
        cols, rows = 4, 7
        x0, x1, y0, y1 = 0.85, 7.65, 1.5, 9.6
        cw, ch_ = (x1 - x0) / cols, (y1 - y0) / rows
        for i, L in enumerate(string.ascii_uppercase + "  "):
            r, k = divmod(i, cols)
            if i >= 26:
                continue
            if i >= 24:                     # Y and Z centred on the last row
                k += 1
            bx, by = x0 + k * cw, y0 + r * ch_
            c.setStrokeColor(GUIDE); c.setLineWidth(1)
            self.rrect(bx + 0.04, by + 0.04, bx + cw - 0.04, by + ch_ - 0.04, 0.1)
            self.image(f"clean/{L}.png", (bx + 0.08, by + 0.1, bx + 0.85, by + ch_ - 0.1))
            c.setFillColor(INK); c.setFont("Fredoka-Bold", 26)
            c.drawString(self.X(bx + 0.92), self.Y(by + 0.6), L + L.lower())
            name = ANIMALS[L]
            fs = self.fit_text(name, "Fredoka-Medium", 11.5, cw - 0.95, 8)
            c.setFont("Fredoka-Medium", fs)
            c.drawString(self.X(bx + 0.92), self.Y(by + 0.92), name)
        self.footer(3)

    def certificate(self):
        c = self.c
        self.border()
        c.setStrokeColor(INK); c.setLineWidth(2)
        self.rrect(0.8, 0.8, 7.7, 9.55, 0.2)
        self.outline_centred("Alphabet Champion!", 2.0, 64, max_w=6.2)
        self.star(W / 2, 3.6, 1.2, 0.52)
        self.centred("A-Z", 3.8, "Fredoka-Bold", 28)
        self.centred("Well done,", 5.35, "Fredoka-SemiBold", 22)
        self.line_for_name(1.6, 6.9, 6.25)
        self.centred("You can write every big and small letter from A to Z!", 6.95, "Fredoka-Medium", 17)
        self.line_for_name(1.6, 3.9, 8.0); self.line_for_name(4.6, 6.9, 8.0)
        c.setFont("Fredoka-Medium", 13)
        c.drawCentredString(self.X(2.75), self.Y(8.3), "date")
        c.drawCentredString(self.X(5.75), self.Y(8.3), "signed")
        self.image("clean/L.png", (1.0, 2.6, 2.4, 4.4))
        self.image("clean/E.png", (6.1, 2.6, 7.5, 4.4))
        self.footer()

    def extra(self):
        self.border()
        self.header_pill("Extra practice", cy=1.05, size=26)
        u = 0.34
        b = 1.6 + 2 * u
        while b + u < 9.6:
            self.guide(0.95, 7.55, b, u)
            b += 3 * u + 0.2
        self.footer(80)


def make(name, fn, *args):
    pdf = f"{OUT}/{name}.pdf"
    c = canvas.Canvas(pdf, pagesize=(W * PT, H * PT), initialFontName="Fredoka-Medium")
    c.setAuthor(AUTHOR); c.setTitle(f"{TITLE} - {name}")
    fn(TP(c), *args)
    c.showPage(); c.save()
    subprocess.run(["pdftoppm", "-png", "-r", "100", "-singlefile", pdf, pdf[:-4]], check=True)
    print(pdf)


def build_letter(ch):
    i = ord(ch.upper()) - ord("A")
    if ch.isupper():
        make(f"{UPPER0 + i:02d}_upper_{ch}", TP.letter_page, ch, UPPER0 + i)
    else:
        make(f"{LOWER0 + i:02d}_lower_{ch}", TP.letter_page, ch, LOWER0 + i)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    todo = sys.argv[1:]
    if not todo:
        make("01_title", TP.title_page)
        make("02_name", TP.name_page)
        make("03_chart", TP.chart)
        make("30_review_upper", TP.review, True, 30)
        make("31_missing_upper", TP.missing, True, 31)
        make("58_review_lower", TP.review, False, 58)
        make("59_missing_lower", TP.missing, False, 59)
        make("60_match_1", TP.match, 1, 60)
        make("61_match_2", TP.match, 2, 61)
        for i in range(13):
            a, b = string.ascii_lowercase[2 * i], string.ascii_lowercase[2 * i + 1]
            make(f"{WORDS0 + i:02d}_words_{a}{b}", TP.words_page, i, WORDS0 + i)
        for k in range(4):
            make(f"{SENT0 + k:02d}_sentences_{k + 1}", TP.sentences_page, k, SENT0 + k)
        make("79_certificate", TP.certificate)
        make("80_extra_practice", TP.extra)
        todo = list(string.ascii_uppercase + string.ascii_lowercase)
    for ch in todo:
        build_letter(ch)
