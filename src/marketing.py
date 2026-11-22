"""Social media kit from the book's own art.
Usage: python3 src/marketing.py  -> marketing/*.png, marketing/reel_a_to_z.mp4, marketing/free_coloring_page_A.pdf
"""
import os, string, subprocess, shutil, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

os.makedirs("marketing", exist_ok=True)
OUT = "marketing"
ANIMALS = dict(zip(string.ascii_uppercase, """Alligator Bear Camel Dolphin Elephant Frog Giraffe Hippo Iguana Jellyfish Koala Lion
Monkey Narwhal Owl Panda Quail Rabbit Sloth Tiger Urial Vulture Whale X-ray_fish Yak Zebra""".split()))
ANIMALS = {k: v.replace("_", " ") for k, v in ANIMALS.items()}

SKY = (170, 222, 244)
CREAM = (255, 249, 230)
PILL = (255, 243, 176)
INK = (33, 33, 33)
WHITE = (255, 255, 255)
PAL = {"Red": (229, 57, 53), "Orange": (251, 140, 0), "Yellow": (253, 216, 53), "Light green": (124, 179, 66),
       "Dark blue": (30, 90, 168), "Purple": (142, 36, 170), "Pink": (244, 143, 177), "Light blue": (79, 195, 247)}
RAINBOW = [PAL[k] for k in ("Red", "Orange", "Yellow", "Light green", "Light blue", "Purple", "Pink")]


def font(name, size):
    return ImageFont.truetype({"baloo": "fonts/Baloo2-ExtraBold.ttf", "bold": "fonts/Fredoka-Bold.ttf",
                               "semi": "fonts/Fredoka-SemiBold.ttf", "med": "fonts/Fredoka-Medium.ttf"}[name], size)


def text(d, xy, s, f, fill=INK, stroke=0, stroke_fill=INK, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)


def fit(s, name, size, max_w):
    while size > 10 and font(name, size).getlength(s) > max_w:
        size -= 2
    return font(name, size)


def rainbow_title(img, cx, y, s, size, stroke=8):
    """Each letter its own colour with a thick dark outline, centred on cx."""
    d = ImageDraw.Draw(img); f = font("baloo", size)
    x = cx - f.getlength(s) / 2; k = 0
    for ch in s:
        col = WHITE if ch == " " else RAINBOW[k % len(RAINBOW)]
        if ch != " ": k += 1
        d.text((x, y), ch, font=f, fill=col, stroke_width=stroke, stroke_fill=INK, anchor="ls")
        x += f.getlength(ch)


def pill(img, cx, cy, s, f, fill=PILL, pad=(40, 18), width=5):
    d = ImageDraw.Draw(img)
    w = f.getlength(s) + 2 * pad[0]; h = f.size + 2 * pad[1]
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, fill=fill, outline=INK, width=width)
    text(d, (cx, cy), s, f)


def cutout(path):
    """Coloured reference with its outside white made transparent (inside whites, like eyes, stay)."""
    im = Image.open(path).convert("RGB"); a = np.array(im)
    white = (a > 245).all(axis=2)
    lab, _ = ndimage.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    outside = np.isin(lab, list(edge))
    rgba = np.dstack([a, np.where(outside, 0, 255).astype(np.uint8)])
    out = Image.fromarray(rgba, "RGBA")
    return out.crop(out.getbbox())


def paste_fit(img, src, box, shadow=False):
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / src.width, (y1 - y0) / src.height)
    src = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.LANCZOS)
    x = int(x0 + (x1 - x0 - src.width) / 2); y = int(y0 + (y1 - y0 - src.height) / 2)
    if shadow:
        sh = Image.new("RGBA", (src.width + 60, src.height + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((30, 30, 30 + src.width, 30 + src.height), fill=(0, 0, 0, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        img.paste(sh, (x - 30 + 14, y - 30 + 18), sh)
    img.paste(src, (x, y), src if src.mode == "RGBA" else None)
    return (x, y, x + src.width, y + src.height)


def grass(img, top, color=(155, 201, 95)):
    d = ImageDraw.Draw(img); w, h = img.size
    pts = [(0, h)] + [(x, top + 18 * np.sin(np.pi * x / w * 2)) for x in range(0, w + 1, 20)] + [(w, h)]
    d.polygon(pts, fill=color)
    rng = np.random.default_rng(3)
    for _ in range(int(w / 70)):
        fx, fy = rng.uniform(20, w - 20), rng.uniform(top + 30, h - 20)
        for k in range(5):
            a = np.radians(90 + 72 * k)
            d.ellipse((fx + 13 * np.cos(a) - 10, fy - 13 * np.sin(a) - 10, fx + 13 * np.cos(a) + 10, fy - 13 * np.sin(a) + 10),
                      fill=WHITE, outline=INK, width=2)
        d.ellipse((fx - 8, fy - 8, fx + 8, fy + 8), fill=PAL["Yellow"], outline=INK, width=2)


def render(pdf, dpi, page=None, crop_in=None):
    with tempfile.TemporaryDirectory() as t:
        args = ["pdftoppm", "-png", "-r", str(dpi), "-singlefile"]
        if page: args += ["-f", str(page), "-l", str(page)]
        subprocess.run(args + [pdf, f"{t}/p"], check=True)
        im = Image.open(f"{t}/p.png").convert("RGB")
    if crop_in:
        im = im.crop(tuple(round(v * dpi) for v in crop_in))
    return im


# --- source art ---------------------------------------------------------------------
FRONT = render("cover.pdf", 200, crop_in=(8.6954, 0.125, 17.1954, 11.125))     # front cover, trimmed
FRONT.save(f"{OUT}/front_cover.png")
REFS = {L: cutout(f"colored/{L}.png") for L in string.ascii_uppercase}
PAGE = {L: render(f"pages/{L}.pdf", 150) for L in "AEL"}
CLEAN_A = Image.open("clean/A.png").convert("RGB")


# --- 1. launch post (square) ----------------------------------------------------------
def launch_post():
    img = Image.new("RGB", (1080, 1080), SKY); d = ImageDraw.Draw(img)
    grass(img, 900)
    paste_fit(img, FRONT, (60, 120, 540, 900), shadow=True)
    cx = 805
    d.ellipse((cx - 95, 60, cx + 95, 250), fill=PAL["Red"], outline=INK, width=6)
    text(d, (cx, 155), "NEW!", font("baloo", 64), fill=WHITE, stroke=4)
    text(d, (cx, 330), "My First", font("bold", 56), fill=WHITE, stroke=5)
    rainbow_title(img, cx, 455, "A to Z", 118, stroke=7)
    text(d, (cx, 520), "Animals", font("baloo", 82), fill=PAL["Purple"], stroke=6)
    text(d, (cx, 610), "Copy  ·  Color  ·  Learn", font("semi", 34))
    text(d, (cx, 668), "26 cute baby animals", font("med", 32))
    text(d, (cx, 712), "for ages 3–8", font("med", 32))
    pill(img, cx, 815, "Now on Amazon", font("bold", 42), fill=PAL["Yellow"])
    img.save(f"{OUT}/01_launch_post_1080x1080.png")


# --- 2. carousel (4:5) -------------------------------------------------------------------
def slide_base(bg=CREAM):
    img = Image.new("RGB", (1080, 1350), bg)
    ImageDraw.Draw(img).rounded_rectangle((24, 24, 1056, 1326), radius=40, outline=INK, width=6)
    return img


def carousel():
    # 1 hook
    img = slide_base(SKY); d = ImageDraw.Draw(img)
    text(d, (540, 170), "Learn the ABCs", font("baloo", 96), fill=WHITE, stroke=7)
    text(d, (540, 290), "with 26 baby animals!", font("baloo", 70), fill=PAL["Yellow"], stroke=6)
    for i, L in enumerate("AEGLPZ"):
        x0 = 90 + (i % 3) * 300; y0 = 400 + (i // 3) * 380
        paste_fit(img, REFS[L], (x0, y0, x0 + 300, y0 + 300))
        text(d, (x0 + 150, y0 + 335), f"{L} is for {ANIMALS[L]}", font("semi", 30))
    text(d, (540, 1250), "Swipe for more  »", font("bold", 40))
    img.save(f"{OUT}/02_carousel_1_hook.png")

    # 2 how it works
    img = slide_base(); d = ImageDraw.Draw(img)
    text(d, (540, 120), "How it works", font("baloo", 90), fill=PAL["Orange"], stroke=6)
    box = paste_fit(img, PAGE["A"], (60, 210, 620, 1290), shadow=True)
    steps = [("1", "Color the big", "hollow letters", PAL["Red"]),
             ("2", "Copy the small", "colored picture", PAL["Light green"]),
             ("3", "Match the", "color dots", PAL["Dark blue"])]
    for i, (n, a, b, col) in enumerate(steps):
        y = 330 + i * 300
        d.ellipse((665, y - 50, 765, y + 50), fill=col, outline=INK, width=5)
        text(d, (715, y), n, font("baloo", 64), fill=WHITE, stroke=3)
        text(d, (785, y - 22), a, font("semi", 31), anchor="lm"); text(d, (785, y + 22), b, font("semi", 31), anchor="lm")
    img.save(f"{OUT}/02_carousel_2_how_it_works.png")

    # 3 color it like this
    img = slide_base(); d = ImageDraw.Draw(img)
    text(d, (540, 130), "Color it...", font("baloo", 90), fill=PAL["Dark blue"], stroke=6)
    paste_fit(img, CLEAN_A, (120, 220, 960, 700))
    text(d, (540, 790), "...like this!", font("baloo", 90), fill=PAL["Light green"], stroke=6)
    paste_fit(img, REFS["A"], (220, 860, 860, 1290))
    img.save(f"{OUT}/02_carousel_3_before_after.png")

    # 4 meet all 26
    img = slide_base(SKY); d = ImageDraw.Draw(img)
    text(d, (540, 115), "Meet all 26!", font("baloo", 96), fill=WHITE, stroke=7)
    cols, cw, chh = 5, 196, 180
    for i, L in enumerate(string.ascii_uppercase):
        r, c = divmod(i, cols)
        if r == 5: c += 2                                   # last row: centre the single Z
        x0 = 50 + c * cw; y0 = 200 + r * chh
        d.rounded_rectangle((x0 + 4, y0 + 4, x0 + cw - 4, y0 + chh - 4), radius=22, fill=WHITE, outline=INK, width=3)
        paste_fit(img, REFS[L], (x0 + 18, y0 + 14, x0 + cw - 18, y0 + chh - 52))
        text(d, (x0 + cw / 2, y0 + chh - 30), f"{L}  {ANIMALS[L]}", fit(f"{L}  {ANIMALS[L]}", "semi", 24, cw - 20))
    img.save(f"{OUT}/02_carousel_4_all_26.png")

    # 5 call to action
    img = slide_base(SKY); d = ImageDraw.Draw(img)
    grass(img, 1150)
    paste_fit(img, FRONT, (250, 90, 830, 840), shadow=True)
    text(d, (540, 905), "Now on Amazon!", font("baloo", 86), fill=WHITE, stroke=7)
    text(d, (540, 990), "Search “My First A to Z Animals”", font("semi", 38))
    text(d, (540, 1050), "Ages 3–8  ·  8.5 × 11 in  ·  26 animals", font("med", 34))
    img.save(f"{OUT}/02_carousel_5_cta.png")


# --- 3. story (9:16) -------------------------------------------------------------------------
def story():
    img = Image.new("RGB", (1080, 1920), SKY); d = ImageDraw.Draw(img)
    grass(img, 1650)
    text(d, (540, 180), "NEW BOOK!", font("baloo", 110), fill=PAL["Red"], stroke=7)
    paste_fit(img, FRONT, (150, 280, 930, 1300), shadow=True)
    text(d, (540, 1410), "26 cute baby animals to", font("semi", 46))
    text(d, (540, 1470), "copy, color & learn A to Z", font("semi", 46))
    pill(img, 540, 1580, "Link in bio", font("bold", 50), fill=PAL["Yellow"])
    img.save(f"{OUT}/03_story_1080x1920.png")


# --- 4. Pinterest pin (2:3) -------------------------------------------------------------------
def pin():
    img = Image.new("RGB", (1000, 1500), CREAM); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1000, 330), fill=SKY)
    text(d, (500, 95), "ABC Coloring Book", font("baloo", 84), fill=WHITE, stroke=6)
    text(d, (500, 190), "for Toddlers & Preschoolers", font("bold", 50), fill=INK)
    text(d, (500, 268), "26 baby animals to copy & color", font("med", 38))
    paste_fit(img, PAGE["L"], (50, 380, 560, 1080), shadow=True)
    paste_fit(img, FRONT, (600, 420, 960, 900), shadow=True)
    paste_fit(img, REFS["L"], (620, 920, 940, 1180))
    d.rectangle((0, 1220, 1000, 1500), fill=SKY)
    text(d, (500, 1300), "My First A to Z Animals", font("baloo", 64), fill=WHITE, stroke=5)
    text(d, (500, 1385), "Copy Coloring Book  ·  Ages 3–8", font("semi", 40))
    text(d, (500, 1445), "Available on Amazon", font("bold", 36), fill=PAL["Dark blue"])
    img.save(f"{OUT}/04_pinterest_pin_1000x1500.png")


# --- 5. reel: A to Z flash (9:16, ~16 s) ---------------------------------------------------------
def reel():
    tmp = tempfile.mkdtemp(); fps = 30; n = 0
    def emit(img, frames):
        nonlocal n
        for _ in range(frames):
            img.save(f"{tmp}/f{n:05d}.png"); n += 1
    # intro
    img = Image.new("RGB", (1080, 1920), SKY); d = ImageDraw.Draw(img); grass(img, 1650)
    text(d, (540, 760), "A to Z", font("baloo", 220), fill=PAL["Yellow"], stroke=10)
    text(d, (540, 960), "in 26 cute animals!", font("baloo", 90), fill=WHITE, stroke=7)
    emit(img, int(1.5 * fps))
    for i, L in enumerate(string.ascii_uppercase):
        img = Image.new("RGB", (1080, 1920), RAINBOW[i % len(RAINBOW)]); d = ImageDraw.Draw(img)
        d.rounded_rectangle((90, 200, 990, 1720), radius=60, fill=WHITE, outline=INK, width=8)
        text(d, (540, 470), L + L.lower(), font("baloo", 300), fill=RAINBOW[i % len(RAINBOW)], stroke=10)
        paste_fit(img, REFS[L], (170, 650, 910, 1390))
        text(d, (540, 1530), f"{L} is for {ANIMALS[L]}", fit(f"{L} is for {ANIMALS[L]}", "baloo", 96, 820), stroke=0)
        emit(img, int(0.45 * fps))
    # end card
    img = Image.new("RGB", (1080, 1920), SKY); d = ImageDraw.Draw(img); grass(img, 1650)
    paste_fit(img, FRONT, (190, 200, 890, 1110), shadow=True)
    text(d, (540, 1260), "My First A to Z Animals", font("baloo", 76), fill=WHITE, stroke=6)
    text(d, (540, 1360), "Copy Coloring Book · Ages 3–8", font("semi", 48))
    pill(img, 540, 1490, "Now on Amazon", font("bold", 56), fill=PAL["Yellow"])
    emit(img, int(3 * fps))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/f%05d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", f"{OUT}/05_reel_a_to_z_1080x1920.mp4"], check=True)
    shutil.rmtree(tmp)
    return n / fps


# --- 6. free printable sample page --------------------------------------------------------------
def free_page():
    pg = render("pages/A.pdf", 300)
    d = ImageDraw.Draw(pg)
    text(d, (pg.width / 2, int(10.78 * 300)), "Free sample page from “My First A to Z Animals” by TinyTusk · available on Amazon",
         font("med", 34))
    pg.save(f"{OUT}/06_free_coloring_page_A.pdf", resolution=300)


if __name__ == "__main__":
    launch_post(); carousel(); story(); pin()
    secs = reel(); free_page()
    print(f"done; reel {secs:.1f} s")
    print("\n".join(sorted(os.listdir(OUT))))
