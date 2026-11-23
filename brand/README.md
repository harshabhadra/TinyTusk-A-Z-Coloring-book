# TinyTusk Learning Series branding

Shared by the three series books: `TinyTusk-ABC-Letter-Tracing-Workbook/`, `Trace-and-Write-the-Alphabet/` and
`TinyTusk-A-to-Z-Animals-Color-by-Number/`. The original A to Z coloring book (repo root) is in KDP review and is
**not** rebuilt with this branding; its cover only appears as a thumbnail in the series strip and promo page.

| File | What it is |
|---|---|
| `logos/round_badge.png`, `logos/horizontal_logo.png`, `logos/stacked_logo.png`, `logos/mascot_E.png` | Sima's final TinyTusk logo files (as delivered, white backgrounds). Other projects/threads should use these. |
| `badge.png`, `logo_wide.png`, `logo_stacked.png` | Transparent cut-outs of the three logos made by `make_assets.py`: badge on the front covers, horizontal logo on the back covers and interior title pages, stacked logo on the copyright pages |
| `mascot.png`, `mascot_line.png` | Baby elephant mascot (colour for covers, line art for interiors), cut out of `logos/mascot_E.png` and `../clean/E.png` |
| `series/<book>.png` | Front-cover thumbnails, refreshed by each book's `cover.py` |
| `brand.py` | Logo placement, shared back-cover layout, spine text, copyright page, "More TinyTusk books" page, mascot speech bubbles |
| `make_assets.py` | Remakes the cut-outs after a logo file in `logos/` changes |
| `build_series.sh` | Remakes the cut-outs, then rebuilds all three books' covers (twice, so every series strip has the latest covers) interiors and A+ images |
| `aplus.py`, `aplus/` | Amazon A+ Content images, built from the covers, pages and logo cut-outs (see `aplus/README.md`) |

What every series book gets:
- **Front:** the round TinyTusk badge (1.25 in) in the bottom-right corner, same spot on every book.
- **Spine:** "TinyTusk • short title" only where KDP allows spine text (more than 79 pages): Trace & Write (82 pages).
  The spine is only ~0.06 in tall inside KDP's clearance, too small for the logo artwork, so it is text in the logo's font.
  ABC Tracing (62) and Color by Number (40) are too thin, so their spines stay plain.
- **Back:** same layout on all: headline, blurb card with bullets, 4 inside pages, "Collect the TinyTusk Learning
  Series!" strip with the mascot and the other books' covers, horizontal logo + "Published by TinyTusk Books" + age pill,
  and an empty barcode area bottom-right.
- **Inside:** copyright page (page 2, stacked logo, TinyTusk Books imprint), horizontal logo on the title page, the mascot on the title/name/certificate pages, and a
  "More TinyTusk books" last page.
- **Cover colours:** ABC Tracing sky blue, Trace & Write warm yellow, Color by Number mint.

KDP listing (enter these on the KDP details page): Author / contributor **TinyTusk Books**,
Series name **TinyTusk Learning Series**.
