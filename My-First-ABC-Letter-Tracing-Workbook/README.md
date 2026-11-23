# TinyTusk ABC Letter Tracing Workbook

Second book in the TinyTusk Learning Series (shared branding in `../brand/`). Reuses the coloring book's fonts, page frame/footer (`../src/layout.py`,
`../src/frontmatter.py`), the 26 cleaned animals (`../clean/`) and the cover art (`../cover/front_art_300dpi.png`).
Nothing in the coloring book's folders is changed.

**Specs:** 8.5 × 11 in, no bleed, 0.5 in safe margin, **black & white interior** (white paper), 62 pages, fonts embedded.

| Pages | Contents |
|---|---|
| 1 | Title |
| 2 | Copyright page (TinyTusk Books imprint, logo, mascot) |
| 3 | "This book belongs to" + name practice, with the TinyTusk elephant |
| 4–6 | Pencil warm-ups: lines, slants & zigzags, waves & loops |
| 7–58 | Two pages per letter (left: big dashed Aa with stroke numbers, arrows and the animal to color + practice rows; right: write-it-yourself rows, the animal word to trace, find-the-letter balloons) |
| 59–60 | Trace the whole alphabet (upper, lower) + blank rows |
| 61 | "Super writer!" certificate |
| 62 | More TinyTusk books |

Letters are drawn from single-stroke (centre-line) shapes in `src/strokes.py`, simple school "ball and stick" style,
so children trace one line rather than an outline.

```bash
python3 My-First-ABC-Letter-Tracing-Workbook/src/pages.py        # all pages -> My-First-ABC-Letter-Tracing-Workbook/pages/*.pdf + .png previews (or: pages.py A B)
python3 My-First-ABC-Letter-Tracing-Workbook/src/interior.py     # My-First-ABC-Letter-Tracing-Workbook/interior.pdf + checks (size, fonts, margin, no colour ink)
python3 My-First-ABC-Letter-Tracing-Workbook/src/cover.py        # My-First-ABC-Letter-Tracing-Workbook/cover.pdf (spine 62 × 0.002252 in, no spine text under 80 pages, B&W white paper — confirm with KDP's calculator)
```
