"""TinyTusk series branding shared by the three new books (ABC Letter Tracing, Trace & Write, Color by Number).

The original A-Z coloring book is in KDP review and is NOT built from this module (its files stay as they are);
it only appears here as a cover thumbnail in the "Collect the series" strip and on the "More TinyTusk books" page.

Swappable files (same name, any size, PNG with transparency is best):
  brand/logo.png          the TinyTusk logo (currently a PLACEHOLDER made by brand/make_placeholders.py)
  brand/mascot.png        the baby elephant mascot in colour (cut out of ../colored/E.png), used on covers
  brand/mascot_line.png   the mascot as line art (cut out of ../clean/E.png), used inside the books
  brand/series/<key>.png  front-cover thumbnails, refreshed by each book's cover.py (render_front)

Everything takes a "page" object with .c (reportlab canvas), .X(x) and .Y(y) (inches from the top-left),
so it works on the cover classes and on the interior page classes alike.
"""
import os, subprocess, tempfile
from PIL import Image
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics

BRAND = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BRAND)
PT = 72
CAP = 0.70
INK = HexColor("#212121")
SERIES = "TinyTusk Learning Series"
IMPRINT = "TinyTusk Books"
YEAR = 2026

# the whole series, in "Collect the series" order. key -> cover.pdf (relative to the repo)
BOOKS = [
    dict(key="az-coloring", cover="cover.pdf", title="My First A to Z Animals", sub="Copy Coloring Book",
         line="Copy & color 26 cute baby animals", ages="Ages 3–8"),
    dict(key="abc-tracing", cover="TinyTusk-ABC-Letter-Tracing-Workbook/cover.pdf",
         title="TinyTusk ABC", sub="Letter Tracing Workbook", line="Trace, write & color A to Z", ages="Ages 3–5"),
    dict(key="trace-write", cover="Trace-and-Write-the-Alphabet/cover.pdf",
         title="Trace & Write", sub="the Alphabet", line="Lots of handwriting practice", ages="Ages 3–5"),
    dict(key="color-by-number", cover="TinyTusk-A-to-Z-Animals-Color-by-Number/cover.pdf",
         title="TinyTusk A to Z Animals", sub="Color by Number", line="Match the numbers, color the animals",
         ages="Ages 4–8"),
]


def others(key):
    return [b for b in BOOKS if b["key"] != key]


# ---- images ----------------------------------------------------------------------------------------
_cache = {}


def _img(path, gray=False):
    k = (path, gray)
    if k not in _cache:
        im = Image.open(path)
        if gray:
            if im.mode == "RGBA":
                a = im.getchannel("A"); im = Image.merge("LA", (im.convert("L"), a))
            else:
                im = im.convert("L")
        else:
            im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
        _cache[k] = im
    return _cache[k]


def draw_img(p, path, box, gray=False, align="c"):
    """Fit an image into box (x0, y0, x1, y1). Returns the drawn box."""
    im = _img(path, gray)
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / im.width, (y1 - y0) / im.height)
    w, h = im.width * s, im.height * s
    x = {"c": x0 + (x1 - x0 - w) / 2, "l": x0, "r": x1 - w}[align]
    y = y0 + (y1 - y0 - h) / 2
    if im.mode == "LA":                     # reportlab can't mask LA: flatten onto white (interiors are white)
        bg = Image.new("L", im.size, 255); bg.paste(im.getchannel("L"), mask=im.getchannel("A")); im = bg
    p.c.drawImage(ImageReader(im), p.X(x), p.Y(y + h), w * PT, h * PT, mask="auto")
    return x, y, x + w, y + h


def logo(gray=False): return f"{BRAND}/logo.png"
def mascot(line=False): return f"{BRAND}/mascot_line.png" if line else f"{BRAND}/mascot.png"


def series_thumb(key): return f"{BRAND}/series/{key}.png"


def render_front(cover_pdf, key, trim_w=8.5, trim_h=11.0, bleed=0.125, dpi=110):
    """Render the front panel of a full-wrap cover PDF to brand/series/<key>.png."""
    os.makedirs(f"{BRAND}/series", exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile", cover_pdf, f"{d}/c"], check=True)
        im = Image.open(f"{d}/c.png").convert("RGB")
    W = im.width / dpi
    x0 = (W - bleed - trim_w) * dpi
    im.crop((round(x0), round(bleed * dpi), round((W - bleed) * dpi), round((bleed + trim_h) * dpi))) \
      .save(series_thumb(key))


# ---- text helpers ------------------------------------------------------------------------------------
def text(p, s, x, y, font, size, color=INK, anchor="c"):
    c = p.c; c.setFillColor(color); c.setFont(font, size)
    {"c": c.drawCentredString, "l": c.drawString, "r": c.drawRightString}[anchor](p.X(x), p.Y(y), s)


def fit(s, font, size, max_w, min_size=6):
    while size > min_size and pdfmetrics.stringWidth(s, font, size) / PT > max_w:
        size -= 0.5
    return size


def wrap(s, font, size, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) / PT <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur] if cur else lines


def rrect(p, x0, y0, x1, y1, r, fill=None, stroke=INK, width=2.5):
    c = p.c
    if fill is not None: c.setFillColor(fill)
    if stroke is not None: c.setStrokeColor(stroke); c.setLineWidth(width)
    c.roundRect(p.X(x0), p.Y(y1), (x1 - x0) * PT, (y1 - y0) * PT, r * PT,
                stroke=1 if stroke is not None else 0, fill=1 if fill is not None else 0)


# ---- the series lockup: [logo] TinyTusk / Learning Series -----------------------------------------
LOCKUP_H = 0.62


def lockup_width(h=LOCKUP_H):
    tw = max(pdfmetrics.stringWidth("TinyTusk", "Fredoka-Bold", h * 34) / PT,
             pdfmetrics.stringWidth("LEARNING SERIES", "Fredoka-SemiBold", h * 13) / PT)
    return h * 0.18 + h * 0.86 + h * 0.15 + tw + h * 0.32


def lockup(p, x1, y1, h=LOCKUP_H, anchor="r", gray=False, fill=white):
    """White pill with the logo and 'TinyTusk / LEARNING SERIES'. (x1, y1) = bottom-right corner (anchor 'r')
    or bottom-left corner (anchor 'l'). The same lockup sits in the same corner of every front cover."""
    w = lockup_width(h)
    x0 = x1 - w if anchor == "r" else x1
    y0 = y1 - h
    rrect(p, x0, y0, x0 + w, y1, h / 2, fill=fill, width=2.2)
    lx = x0 + h * 0.18
    draw_img(p, logo(), (lx, y0 + h * 0.07, lx + h * 0.86, y1 - h * 0.07), gray=gray)
    tx = lx + h * 0.86 + h * 0.15
    text(p, "TinyTusk", tx, y0 + h * 0.56, "Fredoka-Bold", h * 34, anchor="l")
    text(p, "LEARNING SERIES", tx, y0 + h * 0.84, "Fredoka-SemiBold", h * 13, color=HexColor("#555555"), anchor="l")
    return x0, y0, x0 + w, y1


# ---- mascot with a speech bubble -----------------------------------------------------------------------
def mascot_tip(p, box, say, line=False, side="r", size=15, bubble_w=3.0, fill=white, gray=False):
    """Mascot drawn in box; a speech bubble with `say` to its right (side='r') or left (side='l')."""
    mx0, my0, mx1, my1 = draw_img(p, mascot(line), box, gray=gray)
    font = "Fredoka-SemiBold"
    lines = wrap(say, font, size, bubble_w - 0.4)
    lh = size * 1.25 / PT
    bh = len(lines) * lh + 0.32
    cy = my0 + (my1 - my0) * 0.35
    by0 = max(cy - bh / 2, my0 - 0.1)
    bx0 = mx1 + 0.12 if side == "r" else mx0 - 0.12 - bubble_w
    bx1 = bx0 + bubble_w
    c = p.c
    c.setLineJoin(1)
    rrect(p, bx0, by0, bx1, by0 + bh, 0.18, fill=fill, width=2)
    # tail towards the mascot
    tx = bx0 if side == "r" else bx1
    d = -1 if side == "r" else 1
    ty = by0 + bh * 0.55
    path = c.beginPath()
    path.moveTo(p.X(tx), p.Y(ty - 0.1)); path.lineTo(p.X(tx + d * 0.2), p.Y(ty + 0.02)); path.lineTo(p.X(tx), p.Y(ty + 0.1))
    c.setFillColor(fill); c.setStrokeColor(INK); c.setLineWidth(2); c.drawPath(path, stroke=1, fill=1)
    c.setStrokeColor(fill); c.setLineWidth(3); c.line(p.X(tx), p.Y(ty - 0.085), p.X(tx), p.Y(ty + 0.085))
    y = by0 + 0.16 + size * CAP / PT
    for s in lines:
        text(p, s, (bx0 + bx1) / 2, y, font, size); y += lh
    return bx0, by0, bx1, by0 + bh


# ---- covers ---------------------------------------------------------------------------------------------
def front_lockup(p, front_x1, trim_y1, safe=0.25):
    """Series lockup in the bottom-right corner of the front cover (same spot on every book)."""
    return lockup(p, front_x1 - safe, trim_y1 - safe)


def spine(p, x0, x1, pages, short, H, color=INK, min_pages=80):
    """Spine text, only when KDP allows it (KDP: more than 79 pages) and keeping 0.0625 in clear each side."""
    if pages < min_pages:
        return False
    c = p.c
    avail = (x1 - x0) - 2 * 0.0625
    s = f"TinyTusk  •  {short}"
    size = avail * PT / 0.95            # Fredoka cap height + descender ~ 0.95 em
    c.saveState()
    c.translate(p.X((x0 + x1) / 2), p.Y(H / 2))
    c.rotate(-90)
    c.setFillColor(color); c.setFont("Fredoka-Bold", size)
    c.drawCentredString(0, -size * (CAP - 0.2) / 2, s)
    c.restoreState()
    return size


def back(p, key, x0, x1, headline, blurb, bullets, thumbs, ages, inside_label="Inside: pages like these",
         shadow=HexColor("#BBBBBB"), accent=None, strip_fill=HexColor("#FFFFFF"), trim_y1=11.125, safe=0.25,
         bullet_color=HexColor("#F5A030")):
    """The shared back-cover layout:
         headline / white blurb card with bullets / 4 page thumbnails / "Collect the series" strip /
         series lockup + imprint + age pill bottom-left / empty barcode area bottom-right (KDP prints it there).
    x0, x1: usable back-panel edges (inches from the left of the full cover)."""
    c = p.c
    cx = (x0 + x1) / 2
    size = fit(headline, "Fredoka-Bold", 27, x1 - x0)
    text(p, headline, cx, 1.05, "Fredoka-Bold", size)
    rrect(p, x0, 1.3, x1, 4.75, 0.25, fill=white)
    y = 1.78
    for line in blurb:
        text(p, line, cx, y, "Fredoka-Medium", fit(line, "Fredoka-Medium", 15, x1 - x0 - 0.4)); y += 0.29
    y += 0.1
    step = min(0.29, (4.6 - y) / max(1, len(bullets)))
    for b in bullets:
        c.setFillColor(bullet_color); c.setStrokeColor(INK); c.setLineWidth(1.2)
        c.circle(p.X(x0 + 0.5), p.Y(y - 0.07), 0.07 * PT, stroke=1, fill=1)
        text(p, b, x0 + 0.7, y, "Fredoka-Medium", 14, anchor="l"); y += step
    # inside pages
    tw = 1.25; th = tw * 11 / 8.5; gap = (x1 - x0 - 4 * tw) / 3; ty = 4.98
    for i, path in enumerate(thumbs):
        tx = x0 + i * (tw + gap)
        c.setFillColor(shadow); c.rect(p.X(tx + 0.05), p.Y(ty + th + 0.05), tw * PT, th * PT, stroke=0, fill=1)
        c.drawImage(ImageReader(path), p.X(tx), p.Y(ty + th), tw * PT, th * PT)
        c.setStrokeColor(INK); c.setLineWidth(1.3); c.rect(p.X(tx), p.Y(ty + th), tw * PT, th * PT, stroke=1, fill=0)
    text(p, inside_label, cx, ty + th + 0.3, "Fredoka-SemiBold", 13)
    # collect the series
    sy0, sy1 = 7.2, 9.45
    rrect(p, x0, sy0, x1, sy1, 0.25, fill=strip_fill)
    text(p, f"Collect the {SERIES}!", cx + 0.55, sy0 + 0.36, "Fredoka-Bold", 17)
    draw_img(p, mascot(), (x0 + 0.08, sy0 + 0.3, x0 + 1.45, sy1 - 0.08))
    books = others(key)
    ctw = 1.05; cth = ctw * 11 / 8.5
    area0, area1 = x0 + 1.6, x1 - 0.2
    cg = (area1 - area0 - len(books) * ctw) / max(1, len(books) - 1) if len(books) > 1 else 0
    cy0 = sy0 + 0.52
    for i, b in enumerate(books):
        tx = area0 + i * (ctw + cg)
        c.setFillColor(shadow); c.rect(p.X(tx + 0.04), p.Y(cy0 + cth + 0.04), ctw * PT, cth * PT, stroke=0, fill=1)
        if os.path.exists(series_thumb(b["key"])):
            c.drawImage(ImageReader(series_thumb(b["key"])), p.X(tx), p.Y(cy0 + cth), ctw * PT, cth * PT)
        c.setStrokeColor(INK); c.setLineWidth(1.2); c.rect(p.X(tx), p.Y(cy0 + cth), ctw * PT, cth * PT, stroke=1, fill=0)
    # bottom-left: lockup, imprint, ages; bottom-right: barcode area
    by1 = trim_y1 - safe
    lx0, ly0, lx1, ly1 = lockup(p, x0, by1 - 0.3, anchor="l")
    text(p, f"Published by {IMPRINT}", x0 + 0.1, by1 - 0.02, "Fredoka-Medium", 11, anchor="l")
    aw = pdfmetrics.stringWidth(ages, "Fredoka-Bold", 18) / PT + 0.5
    rrect(p, lx1 + 0.2, ly0 + 0.08, lx1 + 0.2 + aw, ly1 - 0.08, (ly1 - ly0 - 0.16) / 2,
          fill=accent or HexColor("#FFE066"), width=2.2)
    text(p, ages, lx1 + 0.2 + aw / 2, (ly0 + ly1) / 2 + 18 * CAP / PT / 2, "Fredoka-Bold", 18)
    bx1 = x1 + 0.15                      # back panel right safe edge
    c.setFillColor(white); c.rect(p.X(bx1 - 2.0), p.Y(by1), 2.0 * PT, 1.2 * PT, stroke=0, fill=1)


# ---- interior pages ---------------------------------------------------------------------------------------
def copyright_page(p, title, gray=True, extra=()):
    """Copyright / imprint page (page 2). p is a frontmatter.Front-style page (border, centred, footer)."""
    p.border()
    draw_img(p, logo(), (3.25, 1.2, 5.25, 3.2), gray=gray)
    p.centred(title, 3.9, "Fredoka-Bold", 24)
    p.centred(f"Part of the {SERIES}", 4.35, "Fredoka-SemiBold", 16)
    lines = [f"Published by {IMPRINT}",
             f"Text, design and illustrations © {YEAR} {IMPRINT}. All rights reserved.",
             "No part of this book may be copied, scanned or shared without written permission,",
             "except for coloring and writing in it at home or in your own classroom.",
             f"First edition {YEAR}.", *extra,
             "Find more TinyTusk books on Amazon: search “TinyTusk”."]
    y = 5.05
    for s in lines:
        p.centred(s, y, "Fredoka-Medium", 12.5, max_w=6.6, min_size=9); y += 0.32
    mascot_tip(p, (1.3, 7.2, 3.1, 9.35), "Hi! I'm the TinyTusk elephant. Let's learn together!", line=True,
               bubble_w=3.6, size=16)
    p.footer()


def more_books_page(p, key, gray=True, footer_num=None):
    """Last page: the other books in the series."""
    p.border()
    p.outline_centred("More TinyTusk books", 1.55, 54)
    p.centred(f"Collect the whole {SERIES}!", 2.1, "Fredoka-SemiBold", 18)
    books = others(key)
    tw = 1.85; th = tw * 11 / 8.5
    gap = (6.8 - len(books) * tw) / (len(books) - 1)
    c = p.c
    for i, b in enumerate(books):
        x = 0.85 + i * (tw + gap); y = 2.5
        if os.path.exists(series_thumb(b["key"])):
            draw_img(p, series_thumb(b["key"]), (x, y, x + tw, y + th), gray=gray)
        c.setStrokeColor(black); c.setLineWidth(1.5); c.rect(p.X(x), p.Y(y + th), tw * PT, th * PT, stroke=1, fill=0)
        cx = x + tw / 2
        for k, s in enumerate(wrap(b["title"] + " " + b["sub"], "Fredoka-Bold", 13, tw + 0.2)):
            text(p, s, cx, y + th + 0.32 + k * 0.22, "Fredoka-Bold", 13, color=black)
        text(p, b["ages"], cx, y + th + 0.95, "Fredoka-Medium", 12, color=black)
    mascot_tip(p, (1.1, 7.25, 3.0, 9.45), "Which one will you do next? Ask a grown-up to search “TinyTusk” on Amazon!",
               line=True, bubble_w=3.9, size=15)
    p.footer(footer_num)
