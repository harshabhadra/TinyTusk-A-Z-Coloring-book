"""Step 5.4-5.5: flood-fill closed regions of clean line art with palette colours.

Spec file specs/A.json:
{
  "animal": "Alligator",
  "default": "Light green",          # every interior region not listed below (or null = stay white)
  "fills": {                         # seed points as fractions of image width/height
    "Yellow": [[0.50, 0.70]],
    "white":  [[0.40, 0.30], [0.60, 0.30]]   # eye whites etc. stay white
  }
}

Usage:
  python3 src/color.py regions clean/A.png              -> clean/A_regions.png (numbered map for picking seeds)
  python3 src/color.py fill clean/A.png specs/A.json colored/A.png
Writes colored/A.png and colored/A.json  {"colors_used": [...]} (used for the "Check your colors" dots).
"""
import json, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from palette import rgb, ORDER


def labels(clean_path):
    ink = np.array(Image.open(clean_path).convert("L")) < 128
    n, lab, stats, cent = cv2.connectedComponentsWithStats((~ink).astype(np.uint8), connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    interior = [i for i in range(1, n) if i not in border]
    return ink, lab, stats, cent, interior


def regions(clean_path):
    ink, lab, stats, cent, interior = labels(clean_path)
    h, w = ink.shape
    rng = np.random.default_rng(1)
    out = np.full((h, w, 3), 255, np.uint8)
    for i in interior:
        out[lab == i] = rng.integers(120, 245, 3)
    out[ink] = 0
    im = Image.fromarray(out); d = ImageDraw.Draw(im)
    f = ImageFont.truetype("fonts/Fredoka-Bold.ttf", 34)
    for i in interior:
        cx, cy = cent[i]
        if lab[int(cy), int(cx)] != i:          # centroid outside a concave region: use any pixel
            ys, xs = np.nonzero(lab == i); cy, cx = ys[len(ys) // 2], xs[len(xs) // 2]
        d.text((cx, cy), f"{cx / w:.2f},{cy / h:.2f}", fill=(200, 0, 0), font=f, anchor="mm")
    dst = clean_path.rsplit(".", 1)[0] + "_regions.png"
    im.save(dst); print(dst, f"({len(interior)} regions)")


def fill(clean_path, spec_path, dst):
    spec = json.load(open(spec_path))
    ink, lab, stats, cent, interior = labels(clean_path)
    h, w = ink.shape
    assign = {}
    for color, pts in spec.get("fills", {}).items():
        for fx, fy in pts:
            x, y = int(fx * w), int(fy * h)
            i = lab[y, x]
            if i == 0 or i not in interior:
                sys.exit(f"seed {fx},{fy} for {color} is on a line or outside the animal")
            assign[i] = color
    default = spec.get("default")
    out = np.full((h, w, 3), 255, np.uint8)
    used = set()
    for i in interior:
        c = assign.get(i, default)
        if c and c != "white":
            out[lab == i] = rgb(c); used.add(c)
    out[ink] = 0
    Image.fromarray(out).save(dst, dpi=(300, 300))
    used = [c for c in ORDER if c in used]
    json.dump({"animal": spec["animal"], "colors_used": used}, open(dst.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print(dst, used)


if __name__ == "__main__":
    if sys.argv[1] == "regions":
        regions(sys.argv[2])
    else:
        fill(*sys.argv[2:5])
