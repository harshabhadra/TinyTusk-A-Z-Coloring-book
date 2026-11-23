# TinyTusk Learning Series branding

Shared by the three series books: `TinyTusk-ABC-Letter-Tracing-Workbook/`, `Trace-and-Write-the-Alphabet/` and
`TinyTusk-A-to-Z-Animals-Color-by-Number/`. The original A to Z coloring book (repo root) is in KDP review and is
**not** rebuilt with this branding; its cover only appears as a thumbnail in the series strip and promo page.

| File | What it is |
|---|---|
| `logo.png` | **Placeholder** logo (the mascot's head in a round badge). Replace with the real logo: square PNG, transparent background, then run `build_series.sh`. |
| `mascot.png`, `mascot_line.png` | Baby elephant mascot (colour for covers, line art for interiors), cut out of `../colored/E.png` and `../clean/E.png` |
| `series/<book>.png` | Front-cover thumbnails, refreshed by each book's `cover.py` |
| `brand.py` | Series lockup, shared back-cover layout, spine text, copyright page, "More TinyTusk books" page, mascot speech bubbles |
| `make_placeholders.py` | Makes the mascot cut-outs and the placeholder logo (`--mascot-only` keeps your logo) |
| `build_series.sh` | Rebuilds all three books' covers (twice, so every series strip has the latest covers) and interiors |

What every series book gets:
- **Front:** the same "TinyTusk / Learning Series" lockup with the logo in the bottom-right corner.
- **Spine:** "TinyTusk • short title" only where KDP allows spine text (more than 79 pages): Trace & Write (82 pages).
  ABC Tracing (62) and Color by Number (40) are too thin, so their spines stay plain.
- **Back:** same layout on all: headline, blurb card with bullets, 4 inside pages, "Collect the TinyTusk Learning
  Series!" strip with the mascot and the other books' covers, lockup + "Published by TinyTusk Books" + age pill,
  and an empty barcode area bottom-right.
- **Inside:** copyright page (page 2, TinyTusk Books imprint), the mascot on the title/name/certificate pages, and a
  "More TinyTusk books" last page.
- **Cover colours:** ABC Tracing sky blue, Trace & Write warm yellow, Color by Number mint.

KDP listing (enter these on the KDP details page): Author / contributor **TinyTusk Books**,
Series name **TinyTusk Learning Series**.
