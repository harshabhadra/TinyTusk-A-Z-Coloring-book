"""Amazon A+ Content images for the three TinyTusk Learning Series books, plus shared series images.
Usage (from the repo root):  python3 brand/aplus.py
Output:
  <book>/aplus/01_header_970x600.jpg ... 04_skills_970x600.jpg   one set per book
  brand/aplus/                                                    shared: series banners, logo, comparison chart

Sizes are the image sizes of KDP's A+ Content modules (KDP > Marketing > A+ Content):
  Standard Image Header with Text ............ 970 x 600
  Standard Image & Light/Dark Text Overlay ... 970 x 300
  Standard Company Logo ...................... 600 x 180
  Standard Comparison Chart .................. 150 x 300 (one per book)
Drawn at 2x, downscaled, saved as JPEG (well under KDP's 2 MB limit).

Built only from the books' own pages, covers and art (no new artwork). Logos come from brand/aplus/logos/ (Sima's horizontal,
stacked, badge and mascot files); replace a file there and run this script again.
A+ rules kept: no prices, reviews, rankings, "best"/"#1", "new", links, or "buy now" style wording.
"""
import os, string, subprocess, tempfile, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
S = 2                                    # supersampling

INK, WHITE, CREAM, PILL = (33, 33, 33), (255, 255, 255), (255, 249, 230), (255, 243, 176)
GREY = (85, 85, 85)
PAL = {"Red": (229, 57, 53), "Orange": (251, 140, 0), "Yellow": (253, 216, 53), "Light green": (124, 179, 66),
       "Dark blue": (30, 90, 168), "Purple": (142, 36, 170), "Pink": (244, 143, 177), "Light blue": (79, 195, 247),
       "Green": (67, 160, 71)}
ANIMALS = dict(zip(string.ascii_uppercase, """Alligator Bear Camel Dolphin Elephant Frog Giraffe Hippo Iguana
Jellyfish Koala Lion Monkey Narwhal Owl Panda Quail Rabbit Sloth Tiger Urial Vulture Whale X-ray_fish Yak Zebra"""
                   .split()))

FONTS = {"baloo": "fonts/Baloo2-ExtraBold.ttf", "bold": "fonts/Fredoka-Bold.ttf",
         "semi": "fonts/Fredoka-SemiBold.ttf", "med": "fonts/Fredoka-Medium.ttf"}


def font(name, size): return ImageFont.truetype(FONTS[name], int(size))


def fit(s, name, size, max_w):
    while size > 10 and font(name, size).getlength(s) > max_w:
        size -= 2
    return font(name, size)


def text(d, xy, s, f, fill=INK, stroke=0, stroke_fill=INK, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)


def wrap(s, f, max_w):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= max_w: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur] if cur else lines


def pill(img, cx, cy, s, f, fill=PILL, pad=(36, 16), width=5, color=INK):
    d = ImageDraw.Draw(img)
    w = f.getlength(s) + 2 * pad[0]; h = f.size + 2 * pad[1]
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, fill=fill, outline=INK, width=width)
    text(d, (cx, cy + 2), s, f, fill=color)
    return w


def shadow_under(img, box, r=0, blur=16, off=(12, 16), alpha=80):
    x0, y0, x1, y1 = [int(v) for v in box]
    pad = blur * 3
    sh = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad, pad + x1 - x0, pad + y1 - y0), radius=r, fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(sh, (x0 - pad + off[0], y0 - pad + off[1]), sh)


def paste_fit(img, src, box, shadow=False, border=0, align="c", valign="c"):
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / src.width, (y1 - y0) / src.height)
    src = src.resize((max(1, round(src.width * s)), max(1, round(src.height * s))), Image.LANCZOS)
    x = {"c": int(x0 + (x1 - x0 - src.width) / 2), "l": int(x0), "r": int(x1 - src.width)}[align]
    y = {"c": int(y0 + (y1 - y0 - src.height) / 2), "t": int(y0), "b": int(y1 - src.height)}[valign]
    if shadow: shadow_under(img, (x, y, x + src.width, y + src.height))
    img.paste(src, (x, y), src if src.mode == "RGBA" else None)
    if border:
        ImageDraw.Draw(img).rectangle((x, y, x + src.width - 1, y + src.height - 1), outline=INK, width=border)
    return (x, y, x + src.width, y + src.height)


def render(pdf, dpi=200):
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile", pdf, f"{t}/p"], check=True)
        return Image.open(f"{t}/p.png").convert("RGB")


_cut = {}


def cutout(path):
    """Art with the outside white made transparent (inside whites, like eyes, stay)."""
    if path not in _cut:
        im = Image.open(path).convert("RGB"); a = np.array(im)
        white = (a > 240).all(axis=2)
        lab, _ = ndimage.label(white)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        out = Image.fromarray(np.dstack([a, np.where(np.isin(lab, list(edge)), 0, 255).astype(np.uint8)]), "RGBA")
        _cut[path] = out.crop(out.getbbox())
    return _cut[path]


def animal(L): return cutout(f"colored/{L}.png")


LOGOS = "brand/aplus/logos"          # Sima's TinyTusk logos (white made transparent); swap files, re-run


def logo_img(kind="horizontal"):
    im = Image.open(f"{LOGOS}/{kind}.png").convert("RGBA")
    return im.crop(im.getbbox())


def mascot(): return logo_img("mascot")


def lockup(img, x, y, h, anchor="l"):
    """White pill: [horizontal TinyTusk logo] | LEARNING / SERIES. (x, y) = left-centre ('l') or centre ('c')."""
    d = ImageDraw.Draw(img)
    lg = logo_img()
    lh = h * 0.80; lw = lg.width * lh / lg.height
    f2 = font("bold", h * 0.20)
    tw = max(f2.getlength("LEARNING"), f2.getlength("SERIES"))
    w = h * 0.30 + lw + h * 0.22 + tw + h * 0.40
    x0 = x if anchor == "l" else x - w / 2
    y0 = y - h / 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=h / 2, fill=WHITE, outline=INK, width=max(3, int(h * 0.04)))
    paste_fit(img, lg, (x0 + h * 0.30, y0 + h * 0.10, x0 + h * 0.30 + lw, y0 + h * 0.90))
    sx = x0 + h * 0.30 + lw + h * 0.11
    d.line((sx, y0 + h * 0.25, sx, y0 + h * 0.75), fill=(200, 200, 200), width=max(2, int(h * 0.025)))
    tx = sx + h * 0.13
    text(d, (tx, y0 + h * 0.48), "LEARNING", f2, fill=GREY, anchor="ls")
    text(d, (tx, y0 + h * 0.72), "SERIES", f2, fill=GREY, anchor="ls")
    return x0 + w


def check(d, cx, cy, r, color):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color, outline=INK, width=4)
    d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)],
           fill=WHITE, width=max(4, int(r * 0.28)), joint="curve")


def number_badge(d, cx, cy, r, n, color):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color, outline=INK, width=5)
    text(d, (cx, cy + 3), str(n), font("baloo", r * 1.25), fill=WHITE, stroke=3)


def canvas(w, h, bg):
    return Image.new("RGB", (w * S, h * S), bg)


def save(img, path, w, h):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = img.resize((w, h), Image.LANCZOS)
    img.save(path, quality=92, optimize=True, dpi=(72, 72))
    assert img.size == (w, h)


def front(cover_pdf, dpi=200):
    im = render(cover_pdf, dpi)
    W = im.width / dpi
    return im.crop((round((W - 0.125 - 8.5) * dpi), round(0.125 * dpi), round((W - 0.125) * dpi),
                    round(11.125 * dpi)))


def crop_frac(im, box):
    w, h = im.size
    return im.crop((round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)))


# ---- the three books --------------------------------------------------------------------------------------
BOOKS = {
    "abc-tracing": dict(
        dir="TinyTusk-ABC-Letter-Tracing-Workbook", bg=(170, 222, 244), deep=(127, 184, 211), accent=PAL["Purple"],
        title=["TinyTusk ABC", "Letter Tracing Workbook"],
        headline=["Trace, write & color", "from A to Z!"],
        bullets=["Uppercase and lowercase letters", "Start dots, numbers and arrows", "26 baby animals to color"],
        ages="Ages 3–5", facts="62 pages  ·  large 8.5 × 11 in  ·  black & white",
        inside=[("04_warmup_lines", "Pencil warm-ups"), ("07_A", "Big letters to trace"),
                ("08_A_practice", "Now write it!"), ("59_review_upper", "ABC review")],
        inside_head="What's inside",
        samples=dict(full=("07_A", "Two pages for every letter"),
                     zooms=[("07_A", (0.08, 0.15, 0.92, 0.44), "Numbered dots and arrows show where to start"),
                            ("08_A_practice", (0.05, 0.67, 0.95, 0.83), "Find the letter and color the balloons")]),
        skills=[("04_warmup_lines", (0.08, 0.50, 0.92, 0.82), "Pencil control", "Lines, zigzags and curves warm up little hands", PAL["Orange"]),
                ("07_A", (0.08, 0.47, 0.92, 0.83), "Letter formation", "Trace each letter the right way, step by step", PAL["Light blue"]),
                ("08_A_practice", (0.06, 0.42, 0.92, 0.66), "First words", "Trace each animal's name, Alligator to Zebra", PAL["Light green"]),
                ("08_A_practice", (0.06, 0.67, 0.92, 0.83), "Letter recognition", "Spot big and small letters in fun games", PAL["Pink"])],
        skills_head="Skills your child builds"),
    "trace-write": dict(
        dir="Trace-and-Write-the-Alphabet", bg=(255, 233, 168), deep=(255, 214, 107), accent=PAL["Dark blue"],
        title=["Trace & Write", "the Alphabet"],
        headline=["Lots of practice,", "one letter at a time!"],
        bullets=["52 letter pages: A–Z and a–z", "52 first words, 12 short sentences", "Letter games and a certificate"],
        ages="Ages 3–5", facts="82 pages  ·  large 8.5 × 11 in  ·  black & white",
        inside=[("04_chart", "Alphabet animal chart"), ("05_upper_A", "Uppercase A–Z"), ("39_lower_g", "Lowercase a–z"),
                ("76_sentences_1", "Words & sentences")],
        inside_head="What's inside",
        samples=dict(full=("05_upper_A", "A full page for every letter"),
                     zooms=[("05_upper_A", (0.08, 0.125, 0.95, 0.33), "Stroke numbers, arrows and an animal friend"),
                            ("05_upper_A", (0.08, 0.33, 0.95, 0.62), "Rows go from dashed letters to start dots")]),
        skills=[("05_upper_A", (0.08, 0.33, 0.95, 0.62), "Handwriting", "Six rows a page, from tracing to writing alone", PAL["Orange"]),
                ("32_missing_upper", (0.08, 0.15, 0.95, 0.395), "Alphabet order", "Fill in missing letters and what comes next", PAL["Light blue"]),
                ("61_match_1", (0.06, 0.14, 0.95, 0.42), "Big & small letters", "Match each uppercase letter to its lowercase", PAL["Light green"]),
                ("76_sentences_1", (0.06, 0.08, 0.95, 0.38), "Words & sentences", "Trace first words and short, simple sentences", PAL["Pink"])],
        skills_head="Skills your child builds"),
    "color-by-number": dict(
        dir="TinyTusk-A-to-Z-Animals-Color-by-Number", bg=(203, 239, 224), deep=(125, 191, 164), accent=PAL["Dark blue"],
        title=["TinyTusk A to Z Animals", "Color by Number"],
        headline=["Match the numbers,", "color the animals!"],
        bullets=["26 baby animals, A to Z", "Easy numbers 1 to 5", "Full-color answer key"],
        ages="Ages 4–8", facts="40 pages  ·  large 8.5 × 11 in  ·  printed in color",
        inside=[("04_how_to", "How to color by number"), ("A", "26 animal pictures"),
                ("32_answers", "Full-color answer key"), ("31_certificate", "Well done certificate")],
        inside_head="What's inside",
        samples=dict(full=("L", "One big animal for every letter"),
                     zooms=[("L", (0.03, 0.08, 0.95, 0.25), "A crayon color key on every page"),
                            ("32_answers", (0.05, 0.08, 0.95, 0.50), "Check the colors in the answer key")]),
        skills=[("L", (0.12, 0.30, 0.88, 0.66), "Number recognition", "Spot the numbers 1 to 5 in each picture", PAL["Orange"]),
                ("04_how_to", (0.10, 0.25, 0.90, 0.48), "Color matching", "Match each number to its crayon in the key", PAL["Light blue"]),
                ("A", (0.12, 0.245, 0.90, 0.62), "Fine motor skills", "Big spaces and bold lines, made for little hands", PAL["Light green"]),
                ("04_chart", None, "Animal friends", "Meet a baby animal for every letter, A to Z", PAL["Pink"])],
        skills_head="Skills your child builds"),
}


def page(b, name, dpi=200):
    return render(f"{b['dir']}/pages/{name}.pdf", dpi)


def title_bar(img, s, color, y=110, size=92, max_w=1800):
    d = ImageDraw.Draw(img)
    text(d, (img.width / 2, y), s, fit(s, "baloo", size, max_w), fill=color, stroke=7)


# ---- 1. header ------------------------------------------------------------------------------------------
def header(key, b, cover):
    img = canvas(970, 600, b["bg"]); d = ImageDraw.Draw(img)
    # soft hill along the bottom
    d.ellipse((-400, 1020, 2340, 1700), fill=b["deep"])
    # cover on the right, slightly tilted
    cv = cover.copy(); cv.thumbnail((900, 1040), Image.LANCZOS)
    cv = cv.convert("RGBA")
    ImageDraw.Draw(cv).rectangle((0, 0, cv.width - 1, cv.height - 1), outline=INK, width=3)
    rot = cv.rotate(-4, resample=Image.BICUBIC, expand=True)
    cx, cy = 1490, 600
    shadow_under(img, (cx - cv.width / 2, cy - cv.height / 2, cx + cv.width / 2, cy + cv.height / 2), blur=20,
                 off=(18, 22), alpha=90)
    img.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), rot)
    # text block on the left
    lx = 90
    f = font("baloo", 104)
    for i, s in enumerate(b["headline"]):
        f = fit(s, "baloo", 104, 1010)
        text(d, (lx, 200 + i * 120), s, f, fill=WHITE if i == 0 else PAL["Yellow"], stroke=8, anchor="ls")
    y = 410
    for s in b["bullets"]:
        check(d, lx + 30, y, 30, PAL["Light green"])
        text(d, (lx + 82, y + 2), s, fit(s, "bold", 52, 920), anchor="lm")
        y += 92
    pw = pill(img, lx + 150, 720, b["ages"], font("bold", 50), fill=PAL["Yellow"])
    pill(img, lx + 150 + pw / 2 + 40 + font("bold", 44).getlength(b["facts"].split("·")[0].strip()) / 2 + 36, 720,
         b["facts"].split("·")[0].strip(), font("bold", 44), fill=WHITE)
    # mascot + series lockup bottom-left
    paste_fit(img, mascot(), (60, 820, 330, 1170))
    lockup(img, 360, 1040, 150)
    save(img, f"{b['dir']}/aplus/01_header_970x600.jpg", 970, 600)


# ---- 2. what's inside -------------------------------------------------------------------------------------
def inside(key, b):
    img = canvas(970, 600, CREAM); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, img.width, 200), fill=b["bg"])
    title_bar(img, b["inside_head"], WHITE, y=102)
    n = len(b["inside"]); gap = 56; pw = (img.width - 140 - gap * (n - 1)) / n
    top = 240
    for k, (pg, label) in enumerate(b["inside"]):
        x0 = 70 + k * (pw + gap)
        box = paste_fit(img, page(b, pg, 150), (x0, top, x0 + pw, top + pw * 11 / 8.5), shadow=True, border=2)
        f = fit(label, "bold", 50, pw + 40)
        text(d, (x0 + pw / 2, box[3] + 62), label, f)
    pill(img, img.width / 2, 1020, b["facts"], font("bold", 50), fill=WHITE, pad=(50, 22))
    paste_fit(img, mascot(), (img.width - 250, 920, img.width - 40, 1190))
    paste_fit(img, mascot().transpose(Image.FLIP_LEFT_RIGHT), (40, 920, 250, 1190))
    save(img, f"{b['dir']}/aplus/02_whats_inside_970x600.jpg", 970, 600)


# ---- 3. sample pages: a full page and two close-ups -----------------------------------------------------------
def samples(key, b):
    img = canvas(970, 600, WHITE); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 820, img.height), fill=b["bg"])
    full, cap = b["samples"]["full"]
    box = paste_fit(img, page(b, full, 150), (70, 70, 750, 1060), shadow=True, border=2)
    text(d, ((box[0] + box[2]) / 2, 1130), cap, fit(cap, "bold", 46, 720))
    colors = [PAL["Orange"], PAL["Light blue"]]
    for i, (pg, crop, label) in enumerate(b["samples"]["zooms"]):
        im = crop_frac(page(b, pg, 300), crop)
        x0, x1 = 930, 1880
        y0 = 80 + i * 560
        bx = paste_fit(img, im, (x0, y0, x1, y0 + 420), valign="t")
        d.rounded_rectangle((bx[0] - 8, bx[1] - 8, bx[2] + 8, bx[3] + 8), radius=20, outline=colors[i], width=10)
        number_badge(d, bx[0] - 4, bx[1] - 4, 42, i + 1, colors[i])
        text(d, ((bx[0] + bx[2]) / 2, bx[3] + 58), label, fit(label, "bold", 46, x1 - x0))
    save(img, f"{b['dir']}/aplus/03_sample_pages_970x600.jpg", 970, 600)


# ---- 4. skills ------------------------------------------------------------------------------------------------
def skills(key, b):
    img = canvas(970, 600, b["bg"]); d = ImageDraw.Draw(img)
    title_bar(img, b["skills_head"], WHITE, y=105)
    gap = 40; cw = (img.width - 120 - gap) / 2; ch = (1160 - 210 - gap) / 2
    for k, (pg, crop, head, line, col) in enumerate(b["skills"]):
        r, c = divmod(k, 2)
        x0 = 60 + c * (cw + gap); y0 = 210 + r * (ch + gap)
        shadow_under(img, (x0, y0, x0 + cw, y0 + ch), r=36, blur=10, off=(6, 8), alpha=50)
        d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=36, fill=WHITE, outline=INK, width=5)
        d.rounded_rectangle((x0, y0, x0 + 34, y0 + ch), radius=36, fill=col, outline=INK, width=5)
        d.rectangle((x0 + 18, y0 + 5, x0 + 36, y0 + ch - 5), fill=WHITE)
        d.line((x0 + 18, y0 + 3, x0 + 18, y0 + ch - 3), fill=INK, width=5)
        ib = (x0 + 46, y0 + 26, x0 + 520, y0 + ch - 26)
        if crop is None:                                    # baby animals instead of a page
            for j, L in enumerate("AEGLPZ"):
                rr, cc = divmod(j, 3); w = (ib[2] - ib[0]) / 3; h = (ib[3] - ib[1]) / 2
                paste_fit(img, animal(L), (ib[0] + cc * w + 8, ib[1] + rr * h + 8, ib[0] + (cc + 1) * w - 8, ib[1] + (rr + 1) * h - 8))
        else:
            paste_fit(img, crop_frac(page(b, pg, 300), crop), ib)
        tx0, tx1 = x0 + 545, x0 + cw - 30
        f = font("semi", 38); lines = wrap(line, f, tx1 - tx0)
        fh = font("baloo", 54); hl = wrap(head, fh, tx1 - tx0)
        hy = y0 + ch / 2 - (len(hl) * 62 + 20 + len(lines) * 48) / 2
        for j, s_ in enumerate(hl):
            text(d, (tx0, hy + 31 + j * 62), s_, fh, fill=col, stroke=4, anchor="lm")
        hy += len(hl) * 62 + 20
        for j, s_ in enumerate(lines):
            text(d, (tx0, hy + 24 + j * 48), s_, f, anchor="lm")
    save(img, f"{b['dir']}/aplus/04_skills_970x600.jpg", 970, 600)


# ---- shared series images ----------------------------------------------------------------------------------------
SERIES = [("az-coloring", "cover.pdf", "My First A to Z Animals", "Copy Coloring Book", "Ages 3–8", "Copy & color"),
          ("abc-tracing", "TinyTusk-ABC-Letter-Tracing-Workbook/cover.pdf", "TinyTusk ABC", "Letter Tracing Workbook", "Ages 3–5", "Trace & write"),
          ("trace-write", "Trace-and-Write-the-Alphabet/cover.pdf", "Trace & Write", "the Alphabet", "Ages 3–5", "Handwriting"),
          ("color-by-number", "TinyTusk-A-to-Z-Animals-Color-by-Number/cover.pdf", "TinyTusk A to Z Animals", "Color by Number", "Ages 4–8", "Color by number")]


def series_banner(covers, w, h, path):
    img = canvas(w, h, (170, 222, 244)); d = ImageDraw.Draw(img)
    W, H = img.size
    d.ellipse((-300, H - 140, W + 300, H + 500), fill=(155, 201, 95))
    tall = h == 600
    head = "Collect the TinyTusk Learning Series"
    if tall:
        text(d, (W / 2, 110), head, fit(head, "baloo", 96, W - 160), fill=WHITE, stroke=7)
        cw, top, ch = 370, 200, 479
        xs = [W / 2 + (k - 1.5) * (cw + 70) for k in range(4)]
        for k, (key, _, t, sub, ages, _) in enumerate(SERIES):
            c = covers[key]; x = xs[k]
            paste_fit(img, c, (x - cw / 2, top, x + cw / 2, top + ch), shadow=True, border=3)
            text(d, (x, top + ch + 55), t, fit(t, "bold", 40, cw + 40))
            text(d, (x, top + ch + 103), sub, fit(sub, "semi", 36, cw + 40))
            pill(img, x, top + ch + 175, ages, font("bold", 36), fill=WHITE, pad=(26, 10), width=4)
        paste_fit(img, mascot(), (W - 330, H - 330, W - 40, H - 30))
        lockup(img, 60, H - 100, 130)
    else:
        lx = 60
        text(d, (lx, 150), "Collect the", font("baloo", 74), fill=WHITE, stroke=6, anchor="ls")
        text(d, (lx, 250), "TinyTusk", font("baloo", 104), fill=PAL["Yellow"], stroke=7, anchor="ls")
        text(d, (lx, 330), "Learning Series", font("baloo", 68), fill=WHITE, stroke=6, anchor="ls")
        text(d, (lx, 410), "Fun first books for little hands", font("semi", 38), anchor="ls")
        paste_fit(img, mascot(), (lx, 430, lx + 170, 590), align="l")
        cw, ch = 230, 297
        x = 700
        for k, (key, *_rest) in enumerate(SERIES):
            paste_fit(img, covers[key], (x, 160, x + cw, 160 + ch), shadow=True, border=3)
            pill(img, x + cw / 2, 520, SERIES[k][4], font("bold", 30), fill=WHITE, pad=(20, 8), width=3)
            x += cw + 72
    save(img, path, w, h)


def logo_module(path):
    """Standard Company Logo module: the horizontal TinyTusk logo with the series name."""
    img = canvas(600, 180, WHITE); d = ImageDraw.Draw(img)
    paste_fit(img, logo_img(), (30, 30, 760, 330))
    text(d, (790, 150), "Learning", font("baloo", 92), fill=GREY, anchor="ls")
    text(d, (790, 255), "Series", font("baloo", 92), fill=GREY, anchor="ls")
    save(img, path, 600, 180)


def comparison(covers, key, path):
    """150 x 300 image for the Standard Comparison Chart module: the front cover on the series colour."""
    img = canvas(150, 300, WHITE)
    paste_fit(img, covers[key], (16, 16, 280, 584), shadow=True, border=2)
    save(img, path, 150, 300)


if __name__ == "__main__":
    only = sys.argv[1:]
    covers = {k: front(p) for k, p, *_ in SERIES}
    for key, b in BOOKS.items():
        if only and key not in only: continue
        header(key, b, covers[key]); inside(key, b); samples(key, b); skills(key, b)
    if not only or "series" in only:
        series_banner(covers, 970, 300, "brand/aplus/series_banner_970x300.jpg")
        series_banner(covers, 970, 600, "brand/aplus/series_banner_970x600.jpg")
        logo_module("brand/aplus/logo_600x180.jpg")
        for k, *_ in SERIES:
            comparison(covers, k, f"brand/aplus/compare_{k}_150x300.jpg")
    for d in [b["dir"] + "/aplus" for b in BOOKS.values()] + ["brand/aplus"]:
        for f in sorted(os.listdir(d)):
            if f.endswith(".jpg"):
                im = Image.open(f"{d}/{f}"); print(f"{d}/{f}", im.size, f"{os.path.getsize(f'{d}/{f}') / 1024:.0f} KB")
