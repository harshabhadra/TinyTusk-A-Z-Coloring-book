"""List open line ends in clean art (helps pick "close" segments for a spec).
Usage: python3 src/endpoints.py clean/D.png  -> prints x,y fractions and writes clean/D_ends.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.morphology import skeletonize
from scipy.ndimage import convolve

p = sys.argv[1]
ink = np.array(Image.open(p).convert("L")) < 128
h, w = ink.shape
sk = skeletonize(ink)
nb = convolve(sk.astype(int), np.ones((3, 3), int), mode="constant") - 1
ends = np.argwhere(sk & (nb == 1))
im = Image.open(p).convert("RGB"); d = ImageDraw.Draw(im)
f = ImageFont.truetype("fonts/Fredoka-Bold.ttf", 30)
for y, x in ends:
    d.ellipse((x - 12, y - 12, x + 12, y + 12), outline=(255, 0, 0), width=4)
    d.text((x + 14, y - 14), f"{x / w:.3f},{y / h:.3f}", fill=(0, 0, 255), font=f)
    print(f"{x / w:.3f},{y / h:.3f}")
im.save(p.rsplit(".", 1)[0] + "_ends.png")
