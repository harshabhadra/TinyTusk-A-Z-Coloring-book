"""Amazon A+ Content images (KDP > Marketing > A+ Content).
Usage: python3 src/aplus.py -> marketing/aplus/*.jpg

Sizes = the module image sizes in A+ Content Manager (Basic):
  Standard Image Header with Text ...... 970 x 600
  Standard Company Logo ................ 600 x 180
  Standard Three Images & Text ......... 300 x 300 (x3)
Drawn at 2x and downscaled; saved as high-quality JPEG (< 2 MB each).
A+ rules respected: no prices, promotions, reviews, links, "buy now" or "best".
"""
import os, string
from PIL import Image, ImageDraw
from marketing import (FRONT, REFS, PAGE, CLEAN_A, ANIMALS, SKY, CREAM, PILL, INK, WHITE, PAL, RAINBOW,
                       font, text, fit, rainbow_title, pill, paste_fit, grass, render, cutout)

OUT = "marketing/aplus"
os.makedirs(OUT, exist_ok=True)
S = 2                                                     # draw at 2x


def canvas(w, h, bg):
    return Image.new("RGB", (w * S, h * S), bg)


def save(img, name, w, h):
    img.resize((w, h), Image.LANCZOS).save(f"{OUT}/{name}.jpg", quality=92, optimize=True)


def front_art_only():
    """The cover art without the title, for banners: bottom 60% of the generated art."""
    art = Image.open("cover/front_art_300dpi.png").convert("RGB")
    return art.crop((0, int(art.height * 0.40), art.width, art.height))


def banner_header():
    img = canvas(970, 600, SKY); d = ImageDraw.Draw(img)
    art = front_art_only()
    w = 1120; h = int(art.height * w / art.width)
    art = art.resize((w, h), Image.LANCZOS).convert("RGBA")
    # continue the art's grass to the left edge so the hill doesn't stop in mid-air
    import numpy as np
    px = np.array(art.convert("RGB")).astype(int)
    col = px[:, 3]
    green = np.nonzero((col[:, 1] > col[:, 0] + 25) & (col[:, 1] > col[:, 2] + 25))[0]
    gy = int(green.min()); gcol = tuple(int(v) for v in px[min(gy + 60, h - 1), 3])
    ax, ay = 970 * S - w, 600 * S - h
    ImageDraw.Draw(img).rectangle((0, ay + gy, ax + 4, 600 * S), fill=gcol)
    img.paste(art, (ax, ay))
    text(d, (470, 250), "Learn the ABCs", font("baloo", 120), fill=WHITE, stroke=8)
    text(d, (470, 390), "with 26 cute", font("baloo", 96), fill=PAL["Yellow"], stroke=7)
    text(d, (470, 510), "baby animals!", font("baloo", 96), fill=PAL["Yellow"], stroke=7)
    text(d, (470, 650), "Copy  ·  Color  ·  Learn", font("bold", 60))
    pill(img, 470, 800, "For ages 3–8", font("bold", 56), fill=WHITE, width=6)
    pill(img, 470, 950, "26 animals from A to Z", font("bold", 50), fill=PILL, width=6)
    save(img, "01_header_970x600", 970, 600)


def banner_how():
    img = canvas(970, 600, CREAM); d = ImageDraw.Draw(img)
    text(d, (970, 110), "Every page, three fun steps", font("baloo", 92), fill=PAL["Orange"], stroke=6)
    paste_fit(img, PAGE["A"], (90, 200, 830, 1160), shadow=True)
    steps = [("1", "Color the big hollow letters", "Trace and learn each letter shape", PAL["Red"]),
             ("2", "Copy the small colored picture", "A ready-made guide to follow", PAL["Light green"]),
             ("3", "Match the color dots", "Find the right crayons every time", PAL["Dark blue"])]
    for i, (n, a, b, col) in enumerate(steps):
        y = 360 + i * 270
        d.ellipse((930, y - 75, 1080, y + 75), fill=col, outline=INK, width=8)
        text(d, (1005, y + 4), n, font("baloo", 100), fill=WHITE, stroke=4)
        text(d, (1120, y - 32), a, fit(a, "bold", 54, 780), anchor="lm")
        text(d, (1120, y + 38), b, fit(b, "med", 44, 780), anchor="lm")
    save(img, "02_how_it_works_970x600", 970, 600)


def banner_before_after():
    img = canvas(970, 600, WHITE); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 970 * S, 150), fill=SKY)
    text(d, (970, 80), "A big picture to color + a small one to copy", font("baloo", 74), fill=WHITE, stroke=6)
    for k, L in enumerate("LP"):
        x0 = 60 + k * 960
        paste_fit(img, Image.open(f"clean/{L}.png").convert("RGB"), (x0, 220, x0 + 460, 1080))
        text(d, (x0 + 560, 640), "→" if False else "»", font("baloo", 140), fill=PAL["Orange"])
        paste_fit(img, REFS[L], (x0 + 640, 380, x0 + 860, 900))
        text(d, (x0 + 430, 1140), f"{L} is for {ANIMALS[L]}", font("bold", 52))
    d.line((970, 220, 970, 1160), fill=(200, 200, 200), width=4)
    save(img, "03_color_and_copy_970x600", 970, 600)


def banner_all26():
    img = canvas(970, 600, SKY); d = ImageDraw.Draw(img)
    text(d, (970, 95), "Meet all 26 baby animals, from Alligator to Zebra", fit("Meet all 26 baby animals, from Alligator to Zebra", "baloo", 76, 1860), fill=WHITE, stroke=6)
    cols, cw, ch = 13, 144, 500
    for i, L in enumerate(string.ascii_uppercase):
        r, c = divmod(i, cols)
        x0 = 34 + c * cw; y0 = 175 + r * ch
        d.rounded_rectangle((x0 + 5, y0 + 5, x0 + cw - 5, y0 + ch - 20), radius=26, fill=WHITE, outline=INK, width=4)
        text(d, (x0 + cw / 2, y0 + 70), L, font("baloo", 80), fill=RAINBOW[i % len(RAINBOW)], stroke=4)
        paste_fit(img, REFS[L], (x0 + 14, y0 + 130, x0 + cw - 14, y0 + 380))
        text(d, (x0 + cw / 2, y0 + 430), ANIMALS[L], fit(ANIMALS[L], "semi", 30, cw - 20))
    save(img, "04_all_26_animals_970x600", 970, 600)


def banner_inside():
    img = canvas(970, 600, CREAM); d = ImageDraw.Draw(img)
    text(d, (970, 100), "What's inside", font("baloo", 100), fill=PAL["Purple"], stroke=6)
    items = [("00_title", "Title page"), ("01_name", "“This book belongs to”"),
             ("E", "26 letter pages"), ("29_certificate", "“Well done!” certificate")]
    for k, (pg, label) in enumerate(items):
        x0 = 70 + k * 460
        im = render(f"pages/{pg}.pdf", 100)
        paste_fit(img, im, (x0, 200, x0 + 400, 920), shadow=True)
        text(d, (x0 + 200, 965), label, fit(label, "bold", 46, 430))
    text(d, (970, 1110), "30 pages  ·  large 8.5 × 11 in  ·  printed in color", font("semi", 52))
    save(img, "05_whats_inside_970x600", 970, 600)


def logo():
    img = canvas(600, 180, WHITE); d = ImageDraw.Draw(img)
    paste_fit(img, REFS["E"], (30, 20, 330, 340))
    x = 360
    for k, ch in enumerate("TinyTusk"):
        f = font("baloo", 170)
        d.text((x, 270), ch, font=f, fill=RAINBOW[k % len(RAINBOW)], stroke_width=8, stroke_fill=INK, anchor="ls")
        x += f.getlength(ch)
    text(d, (360, 320), "fun first books for little hands", font("semi", 34), anchor="lm")
    save(img, "06_logo_600x180", 600, 180)


def tiles():
    data = [("07_tile_big_shapes", "F", "Big shapes,", "thick lines", PAL["Light green"]),
            ("08_tile_copy_colors", "L", "Copy the", "colored picture", PAL["Orange"]),
            ("09_tile_learn_letters", None, "Learn every", "letter A to Z", PAL["Purple"])]
    for name, L, a, b, col in data:
        img = canvas(300, 300, WHITE); d = ImageDraw.Draw(img)
        d.rounded_rectangle((8, 8, 592, 592), radius=40, fill=CREAM, outline=col, width=10)
        if L == "F":
            paste_fit(img, Image.open("clean/F.png").convert("RGB"), (90, 50, 510, 400))
        elif L:
            paste_fit(img, REFS[L], (110, 50, 490, 400))
        else:
            text(d, (300, 230), "Aa Bb Cc", font("baloo", 120), fill=WHITE, stroke=6)
        text(d, (300, 460), a, font("bold", 48)); text(d, (300, 520), b, font("bold", 48))
        save(img, f"{name}_300x300", 300, 300)


if __name__ == "__main__":
    banner_header(); banner_how(); banner_before_after(); banner_all26(); banner_inside(); logo(); tiles()
    for f in sorted(os.listdir(OUT)):
        im = Image.open(f"{OUT}/{f}"); print(f, im.size, f"{os.path.getsize(f'{OUT}/{f}') / 1024:.0f} KB")
