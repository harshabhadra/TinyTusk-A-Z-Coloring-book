# TinyTusk — Trace & Write the Alphabet

Third book in the TinyTusk Learning Series (shared branding in `../brand/`): a practice-heavy handwriting workbook. Where *TinyTusk ABC Letter Tracing Workbook* gives each
letter a two-page Aa spread with an animal to color, this book gives **every uppercase and every lowercase letter its
own full page** of fading practice rows, then moves on to words and sentences. The animals are small accents only.

Reuses the coloring book's fonts, page frame/footer (`../src/layout.py`, `../src/frontmatter.py`), the 26 cleaned
animals (`../clean/`) and the coloured animals (`../colored/`, cover only). No new art. Nothing outside this folder
is changed. `src/strokes.py` is a copy of the tracing workbook's stroke letters (plus `.`) so this book builds on its own.

**Specs:** 8.5 × 11 in, no bleed, 0.5 in safe margin, **black & white interior** (white paper), 82 pages, fonts embedded.

| Pages | Contents |
|---|---|
| 1 | Title |
| 2 | Copyright page (TinyTusk Books imprint, logo, mascot) |
| 3 | "This book belongs to" + how to use this book, with the TinyTusk elephant |
| 4 | My Alphabet Animals chart (A–Z) |
| 5–30 | Uppercase A–Z, one page each: big letter with stroke numbers/arrows, animal accent, 6 rows (model + dashed, dashed, dashed/dots, dots only, model + blank, blank) |
| 31–32 | Uppercase review: trace the ABCs; fill in the missing letters + what comes next |
| 33–58 | Lowercase a–z, same layout |
| 59–60 | Lowercase review, same as 31–32 |
| 61–62 | Match big and small letters |
| 63–75 | First words: two words for each letter (ant, apple, bus, bat …), two letters per page |
| 76–79 | Trace and write 12 short sentences about the animals |
| 80 | "Alphabet Champion!" certificate |
| 81 | Extra practice lines |
| 82 | More TinyTusk books |

```bash
python3 Trace-and-Write-the-Alphabet/src/pages.py      # all pages -> pages/*.pdf + .png previews (or: pages.py A b)
python3 Trace-and-Write-the-Alphabet/src/interior.py   # interior.pdf + checks (count, size, fonts, margin, no colour ink)
python3 Trace-and-Write-the-Alphabet/src/cover.py      # cover.pdf (spine 82 × 0.002252 in, spine text "TinyTusk • Trace & Write the Alphabet", B&W white paper — confirm with KDP's calculator)
```
