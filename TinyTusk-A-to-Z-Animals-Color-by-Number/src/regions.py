"""Read the A-Z book's clean line art + colour specs and work out every region's colour,
size and the best spot for its number.  Nothing in the A-Z book's folders is changed.

regions(L) -> dict with
  ink      : bool array (True = line)
  lab      : region label array
  regions  : list of {id, color, area, r (max inscribed radius px), x, y (best number spot px)}
"""
import json, os, sys
import numpy as np
import cv2
from PIL import Image

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(BOOK)


SPREAD = 480          # px (1.6 in): extra numbers only this far from the others
EXTRA_MIN_R = 40      # px: an extra number needs this much room
MAX_SPOTS = 4


def load_clean(L, close_width=15):
    spec = json.load(open(f"{REPO}/specs/{L}.json"))
    im = np.array(Image.open(f"{REPO}/clean/{L}.png").convert("L"))
    h, w = im.shape
    for x1, y1, x2, y2 in spec.get("close", []):       # same gap closing as ../src/color.py (idempotent)
        cv2.line(im, (round(x1 * w), round(y1 * h)), (round(x2 * w), round(y2 * h)), 0, close_width, cv2.LINE_AA)
    return spec, im < 128


def regions(L):
    spec, ink = load_clean(L)
    h, w = ink.shape
    n, lab, stats, cent = cv2.connectedComponentsWithStats((~ink).astype(np.uint8), connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    interior = [i for i in range(1, n) if i not in border]
    assign = {}
    for color, boxes in spec.get("fill_boxes", {}).items():
        for x0, y0, x1, y1 in boxes:
            for i in interior:
                cx, cy = cent[i]
                if x0 * w <= cx <= x1 * w and y0 * h <= cy <= y1 * h:
                    assign[i] = color
    for color, pts in spec.get("fills", {}).items():
        for fx, fy in pts:
            x, y = int(fx * w), int(fy * h)
            i = lab[y, x]
            if i == 0:
                ys, xs = np.nonzero(lab[max(0, y - 25):y + 26, max(0, x - 25):x + 26] > 0)
                if ys.size:
                    k = np.argmin((ys - min(y, 25)) ** 2 + (xs - min(x, 25)) ** 2)
                    i = lab[max(0, y - 25) + ys[k], max(0, x - 25) + xs[k]]
            if i in interior:
                assign[i] = color
    default = spec.get("default")
    dist = cv2.distanceTransform((~ink).astype(np.uint8), cv2.DIST_L2, 5)
    out = []
    for i in interior:
        c = assign.get(i, default) or "white"
        x0, y0, bw, bh = stats[i, :4]
        sub = np.where(lab[y0:y0 + bh, x0:x0 + bw] == i, dist[y0:y0 + bh, x0:x0 + bw], 0)
        k = np.argmax(sub); yy, xx = divmod(k, bw)
        r0 = float(sub[yy, xx])
        # extra number spots for big, spread-out regions (rings, long bodies): next widest point
        # at least SPREAD px from every spot so far, while it still has room for a clear number
        spots = [(int(x0 + xx), int(y0 + yy), r0)]
        gy, gx = np.mgrid[0:bh, 0:bw]
        while len(spots) < MAX_SPOTS:
            for sx, sy, _ in spots[-1:]:
                sub[(gx - (sx - x0)) ** 2 + (gy - (sy - y0)) ** 2 < SPREAD ** 2] = 0
            k = np.argmax(sub); yy, xx = divmod(k, bw)
            if sub[yy, xx] < EXTRA_MIN_R:
                break
            spots.append((int(x0 + xx), int(y0 + yy), float(sub[yy, xx])))
        out.append(dict(id=int(i), color=c, area=int(stats[i, 4]), r=r0,
                        x=spots[0][0], y=spots[0][1], spots=spots))
    return dict(animal=spec["animal"], ink=ink, lab=lab, regions=out, size=(w, h))


if __name__ == "__main__":
    import string
    for L in sys.argv[1:] or string.ascii_uppercase:
        d = regions(L)
        rs = [r for r in d["regions"] if r["color"] != "white"]
        for thr in (20, 27, 35):
            pass
        print(L, d["animal"], "colored:", len(rs), "r>=27:", sum(r["r"] >= 27 for r in rs),
              "r 12-27:", sum(12 <= r["r"] < 27 for r in rs), "r<12:", sum(r["r"] < 12 for r in rs),
              "colors:", sorted({r["color"] for r in rs}))
