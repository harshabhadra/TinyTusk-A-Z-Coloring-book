"""Step 5.1-5.3: raw AI line art -> clean pure black/white line art sized for the drawing area.

Usage: python3 src/clean.py raw/A_alligator_v1.png clean/A.png [--box W H]
Writes the PNG (1-bit, 300 dpi) and a .json report next to it.
"""
import argparse, json, sys
import numpy as np
import cv2

DPI = 300
TARGET_STROKE_PX = 14      # ~3.4 pt at 300 dpi (brief: 3-4 pt)
BOX_IN = (6.8, 6.3)        # drawing area, inches (see layout.py)


def remove_small(mask, min_area):
    """Drop connected components of `mask` (bool) smaller than min_area px."""
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    keep = np.zeros(n, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= min_area
    return keep[lab]


def stroke_width(ink):
    """Median full stroke width in px, measured along the stroke centre lines."""
    dist = cv2.distanceTransform(ink.astype(np.uint8), cv2.DIST_L2, 5)
    # local maxima of the distance map approximate the skeleton
    dil = cv2.dilate(dist, np.ones((3, 3), np.uint8))
    ridge = (dist > 0.5) & (dist >= dil - 1e-6)
    vals = dist[ridge]
    return float(2 * np.median(vals)) if vals.size else 0.0


def clean(src, dst, box_in=BOX_IN, solid_boxes=(), original_boxes=()):
    img = cv2.imread(src, cv2.IMREAD_UNCHANGED)
    if img is None:
        sys.exit(f"cannot read {src}")
    if img.ndim == 3 and img.shape[2] == 4:          # transparent PNG -> white bg
        a = img[:, :, 3:4] / 255.0
        img = (img[:, :, :3] * a + 255 * (1 - a)).astype(np.uint8)
    gray = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. threshold + specks
    ink = gray < 150
    ink = remove_small(ink, 60)                       # black specks
    holes = remove_small(~ink, 40)                    # tiny white pinholes inside lines
    ink = ~holes

    # 2. close small gaps in outlines
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    ink = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, k).astype(bool)

    # 3. crop to drawing, scale to fit the box
    ys, xs = np.nonzero(ink)
    ink = ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bw, bh = int(box_in[0] * DPI), int(box_in[1] * DPI)
    s = min(bw / ink.shape[1], bh / ink.shape[0])
    new = (round(ink.shape[1] * s), round(ink.shape[0] * s))
    g = cv2.resize((~ink).astype(np.uint8) * 255, new, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    g = cv2.GaussianBlur(g, (3, 3), 0)                # smooth jaggies before re-threshold
    ink = g < 128

    # normalise line weight: redraw every stroke at TARGET width from its centre line,
    # so thick outer lines get thinner and thin inner lines get thicker (no lines lost).
    # Solid black areas (pupils, nostrils) wider than a stroke are kept as they are.
    before = stroke_width(ink)
    orig_ink = ink.copy()
    from skimage.morphology import skeletonize
    skel = skeletonize(ink)
    kk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (TARGET_STROKE_PX, TARGET_STROKE_PX))
    lines = cv2.dilate(skel.astype(np.uint8), kk).astype(bool)
    d = int(max(before, TARGET_STROKE_PX) * 2.4) | 1   # bigger than any line junction
    blobs = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d))).astype(bool)
    # thick line junctions survive the opening as small lumps: drop shapes smaller than ~d x d
    n, lab, st, _ = cv2.connectedComponentsWithStats(blobs.astype(np.uint8), connectivity=8)
    small = np.zeros(n, bool); small[1:] = st[1:, cv2.CC_STAT_AREA] < d * d
    blobs &= ~small[lab]
    # spec "solid_boxes": areas (fractions of the output) where thinner solid shapes count as solid,
    # e.g. an open black mouth that tapers
    hh, ww = ink.shape
    for x0, y0, x1, y1 in solid_boxes:
        ds = int(max(before, TARGET_STROKE_PX) * 1.3) | 1
        box = np.zeros_like(ink); box[int(y0 * hh):int(y1 * hh), int(x0 * ww):int(x1 * ww)] = True
        bb = (box & cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN,
                                     cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ds, ds))).astype(bool)).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(bb, connectivity=8)
        big = np.zeros(n, bool); big[1:] = st[1:, cv2.CC_STAT_AREA] >= 4 * ds * ds
        blobs |= big[lab]
    ink = lines | blobs
    # inside solid black areas (incl. their white highlight holes) use the original pixels,
    # so eye highlights keep their round shape
    from scipy.ndimage import binary_fill_holes
    near_blobs = cv2.dilate(binary_fill_holes(blobs).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    ink = np.where(near_blobs, orig_ink, ink)
    # separate black shapes that are mostly solid (pupils, nostrils) are copied unchanged
    n, lab, stats, _ = cv2.connectedComponentsWithStats(orig_ink.astype(np.uint8), connectivity=8)
    solid = np.bincount(lab[blobs], minlength=n) / np.maximum(stats[:, cv2.CC_STAT_AREA], 1)
    keep = solid > 0.5
    keep[0] = False
    ink = (ink & ~keep[lab]) | (orig_ink & keep[lab])
    # spec "original_boxes": copy the original pixels unchanged (detailed eyes the rules above garble)
    for x0, y0, x1, y1 in original_boxes:
        sl = (slice(int(y0 * hh), int(y1 * hh)), slice(int(x0 * ww), int(x1 * ww)))
        ink[sl] = orig_ink[sl]
    g = cv2.GaussianBlur(np.where(ink, 0, 255).astype(np.uint8), (7, 7), 0)   # smooth skeleton wobble
    ink = g < 128
    after = stroke_width(ink)

    # report: interior regions and fiddly ones (< 0.2" x 0.2" area)
    white = (~ink).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(white, connectivity=4)
    h, w = ink.shape
    border_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    tiny_px = (0.2 * DPI) ** 2
    interior = [i for i in range(1, n) if i not in border_labels]
    tiny = [i for i in interior if stats[i, cv2.CC_STAT_AREA] < tiny_px]

    out = np.where(ink, 0, 255).astype(np.uint8)
    cv2.imwrite(dst, out)
    from PIL import Image
    Image.open(dst).convert("1").save(dst, dpi=(DPI, DPI))
    rep = {
        "src": src, "size_px": [w, h], "size_in": [round(w / DPI, 2), round(h / DPI, 2)],
        "stroke_px_before": round(before, 1), "stroke_px_after": round(after, 1),
        "stroke_pt_after": round(after / DPI * 72, 2),
        "interior_regions": len(interior), "tiny_regions": len(tiny),
    }
    json.dump(rep, open(dst.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--box", nargs=2, type=float, default=BOX_IN)
    ap.add_argument("--spec", help="specs/X.json (uses its solid_boxes)")
    a = ap.parse_args()
    sp = json.load(open(a.spec)) if a.spec else {}
    print(json.dumps(clean(a.src, a.dst, tuple(a.box), sp.get("solid_boxes", []), sp.get("original_boxes", [])), indent=2))
