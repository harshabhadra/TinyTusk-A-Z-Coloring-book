"""Make the mascot cut-outs and the PLACEHOLDER logo.
Usage: python3 brand/make_placeholders.py              (mascots + placeholder logo)
       python3 brand/make_placeholders.py --mascot-only (mascots only: keeps your real logo)
  brand/mascot.png       colour baby elephant (../colored/E.png) with a transparent background
  brand/mascot_line.png  line-art baby elephant (../clean/E.png) with a transparent background
  brand/logo.png         placeholder logo: the mascot's head in a round badge. Replace this file with the
                         real TinyTusk logo (square PNG, transparent background) and rebuild the covers/pages.
"""
import os, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw

BRAND = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BRAND)


def outside_mask(clean_path):
    ink = np.array(Image.open(clean_path).convert("L")) < 128
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    closed = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, k) > 0
    n, lab = cv2.connectedComponents((~closed).astype(np.uint8), connectivity=4)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    return np.isin(lab, border[border > 0])


def crop_alpha(im):
    return im.crop(im.getchannel("A").getbbox())


out = outside_mask(f"{REPO}/clean/E.png")
alpha = np.where(out, 0, 255).astype(np.uint8)
col = np.array(Image.open(f"{REPO}/colored/E.png").convert("RGB"))
mascot = crop_alpha(Image.fromarray(np.dstack([col, alpha]), "RGBA"))
mascot.save(f"{BRAND}/mascot.png")
line = np.array(Image.open(f"{REPO}/clean/E.png").convert("L"))
crop_alpha(Image.fromarray(np.dstack([line, line, line, alpha]), "RGBA")).save(f"{BRAND}/mascot_line.png")

if "--mascot-only" in sys.argv:
    sys.exit(0)

# placeholder logo: round sky-blue badge, ink ring, mascot head (top ~62 % of the cut-out)
S = 800
logo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(logo)
d.ellipse((8, 8, S - 8, S - 8), fill=(170, 222, 244, 255), outline=(33, 33, 33, 255), width=22)
head = mascot.crop((0, 0, mascot.width, int(mascot.height * 0.72)))
scale = (S * 0.86) / head.width
head = head.resize((int(head.width * scale), int(head.height * scale)), Image.LANCZOS)
inner = Image.new("RGBA", (S, S), (0, 0, 0, 0))
inner.paste(head, ((S - head.width) // 2, int(S * 0.97 - head.height)), head)
m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((30, 30, S - 30, S - 30), fill=255)
logo.paste(inner, (0, 0), Image.fromarray(np.minimum(np.array(inner.getchannel("A")), np.array(m))))
d = ImageDraw.Draw(logo)
d.ellipse((8, 8, S - 8, S - 8), outline=(33, 33, 33, 255), width=22)
logo.save(f"{BRAND}/logo.png")
print("brand/mascot.png, brand/mascot_line.png, brand/logo.png (placeholder)")
