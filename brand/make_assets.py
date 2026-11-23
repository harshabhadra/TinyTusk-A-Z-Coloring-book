"""Make the transparent brand images the build uses, from the source files in brand/logos/.
Usage: python3 brand/make_assets.py

Sources (Sima's final logo files, white backgrounds):
  brand/logos/round_badge.png      round "TinyTusk" badge          -> brand/badge.png       (front covers)
  brand/logos/horizontal_logo.png  mascot + "TinyTusk" side by side -> brand/logo_wide.png   (back covers, title pages)
  brand/logos/stacked_logo.png     mascot over "TinyTusk"          -> brand/logo_stacked.png (copyright pages)
  brand/logos/mascot_E.png         the mascot (same art as ../colored/E.png)
Mascot cut-outs (outline from ../clean/E.png):
  brand/mascot.png       colour mascot (covers)
  brand/mascot_line.png  line-art mascot (inside the books: B&W-safe and colourable)
"""
import os
import cv2
import numpy as np
from PIL import Image

BRAND = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BRAND)


def border_connected(mask):
    n, lab = cv2.connectedComponents(mask.astype(np.uint8), connectivity=4)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    return np.isin(lab, border[border > 0])


def crop_alpha(im):
    return im.crop(im.getchannel("A").getbbox())


def knock_out_white(src, dst):
    """White background connected to the image edge -> transparent; light anti-aliased edge pixels fade out."""
    rgb = np.array(Image.open(src).convert("RGB")).astype(int)
    light = rgb.min(axis=2)
    bg = border_connected(light > 235)
    near = cv2.dilate(bg.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    alpha = np.full(light.shape, 255, np.uint8)
    edge = near & ~bg
    alpha[edge] = np.clip((255 - light[edge]) * 255 // 60, 0, 255).astype(np.uint8)
    alpha[bg] = 0
    crop_alpha(Image.fromarray(np.dstack([rgb.astype(np.uint8), alpha]), "RGBA")).save(dst)


for src, dst in (("round_badge", "badge"), ("horizontal_logo", "logo_wide"), ("stacked_logo", "logo_stacked")):
    knock_out_white(f"{BRAND}/logos/{src}.png", f"{BRAND}/{dst}.png")

# mascot: outside of the closed outline in ../clean/E.png is transparent
ink = np.array(Image.open(f"{REPO}/clean/E.png").convert("L")) < 128
closed = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
alpha = np.where(border_connected(~closed), 0, 255).astype(np.uint8)
col = np.array(Image.open(f"{BRAND}/logos/mascot_E.png").convert("RGB"))
crop_alpha(Image.fromarray(np.dstack([col, alpha]), "RGBA")).save(f"{BRAND}/mascot.png")
line = np.array(Image.open(f"{REPO}/clean/E.png").convert("L"))
crop_alpha(Image.fromarray(np.dstack([line, line, line, alpha]), "RGBA")).save(f"{BRAND}/mascot_line.png")
print("brand/badge.png, logo_wide.png, logo_stacked.png, mascot.png, mascot_line.png")
