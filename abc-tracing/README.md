# TinyTusk — My First ABC Letter Tracing Workbook

Second book in the TinyTusk series. Reuses the coloring book's fonts, page frame/footer (`../src/layout.py`,
`../src/frontmatter.py`), the 26 cleaned animals (`../clean/`) and the cover art (`../cover/front_art_300dpi.png`).
Nothing in the coloring book's folders is changed.

**Specs:** 8.5 × 11 in, no bleed, 0.5 in safe margin, **black & white interior** (white paper), 60 pages, fonts embedded.

| Pages | Contents |
|---|---|
| 1 | Title |
| 2 | "This book belongs to" + name practice |
| 3–5 | Pencil warm-ups: lines, slants & zigzags, waves & loops |
| 6–57 | Two pages per letter (left: big dashed Aa with stroke numbers, arrows and the animal to color + practice rows; right: write-it-yourself rows, the animal word to trace, find-the-letter balloons) |
| 58–59 | Trace the whole alphabet (upper, lower) + blank rows |
| 60 | "Super writer!" certificate |

Letters are drawn from single-stroke (centre-line) shapes in `src/strokes.py`, simple school "ball and stick" style,
so children trace one line rather than an outline.

```bash
python3 abc-tracing/src/pages.py        # all pages -> abc-tracing/pages/*.pdf + .png previews (or: pages.py A B)
python3 abc-tracing/src/interior.py     # abc-tracing/interior.pdf + checks (size, fonts, margin, no colour ink)
python3 abc-tracing/src/cover.py        # abc-tracing/cover.pdf (spine 60 × 0.002252 in, B&W white paper — confirm with KDP's calculator)
```
