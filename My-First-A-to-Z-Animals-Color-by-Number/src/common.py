"""Shared setup: paths, fonts and the page class reused from the A-Z book (../src/layout.py)."""
import os, sys
BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(BOOK)
sys.path.insert(0, f"{REPO}/src")
sys.path.insert(0, f"{BOOK}/src")
import layout                                   # registers fonts (and chdirs to the repo root)
from layout import Page, W, H, PT, CAP, INK, PILL_FILL, LETTER_FONT, ANIMALS, BORDER
from palette import PALETTE, ORDER

TITLE = "My First A to Z Animals Color by Number"
AUTHOR = "TinyTusk"
AGES = "Ages 4–8"                          # guess
PAGES_DIR = f"{BOOK}/pages"
ART_DIR = f"{BOOK}/art"
os.makedirs(PAGES_DIR, exist_ok=True); os.makedirs(ART_DIR, exist_ok=True)


def placement(img_w, img_h, box, dpi=300):
    """Where Page.image() puts an image of img_w x img_h px inside box: (x, y, scale in/px)."""
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / img_w, (y1 - y0) / img_h)
    return x0 + (x1 - x0 - img_w * s) / 2, y0 + (y1 - y0 - img_h * s) / 2, s
