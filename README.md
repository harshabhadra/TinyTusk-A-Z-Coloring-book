# TinyTusk — My First A to Z Animals Copy Coloring Book

Build pipeline for the 30-page KDP interior (8.5" × 11", premium color, no bleed) and cover.

| Folder | Contents |
|---|---|
| `raw/` | original Higgsfield downloads (`A_alligator_v1.png` …) |
| `clean/` | cleaned black & white line art, sized for the 6.8" × 6.3" drawing area at 300 dpi |
| `specs/` | per-letter colour spec (`A.json`: seed points → palette colour) |
| `colored/` | coloured reference versions + `colors_used` JSON |
| `pages/` | finished pages (PDF + PNG preview) |
| `cover/` | cover art and files |
| `fonts/` | Fredoka (SIL Open Font License, see `fonts/OFL-LICENSE.txt`), overlaps removed for outline letters |

## Per-letter workflow

```bash
python3 src/clean.py raw/A_alligator_v1.png clean/A.png     # B/W, despeckle, close gaps, crop, scale, ~3.4 pt lines
python3 src/color.py regions clean/A.png                     # numbered region map -> pick seed points
# write specs/A.json (see docstring in src/color.py)
python3 src/color.py fill clean/A.png specs/A.json colored/A.png
python3 src/layout.py A                                      # pages/A.pdf + pages/A.png
```

Requirements: Python 3, numpy, opencv-python-headless, pillow, reportlab, fonttools; `pdftoppm` for previews.
