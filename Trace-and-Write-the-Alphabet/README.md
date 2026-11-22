# TinyTusk — Trace & Write the Alphabet

Third TinyTusk book: a practice-heavy handwriting workbook. Where *My First ABC Letter Tracing Workbook* gives each
letter a two-page Aa spread with an animal to color, this book gives **every uppercase and every lowercase letter its
own full page** of fading practice rows, then moves on to words and sentences. The animals are small accents only.

Reuses the coloring book's fonts, page frame/footer (`../src/layout.py`, `../src/frontmatter.py`), the 26 cleaned
animals (`../clean/`) and the coloured animals (`../colored/`, cover only). No new art. Nothing outside this folder
is changed. `src/strokes.py` is a copy of the tracing workbook's stroke letters (plus `.`) so this book builds on its own.

**Specs:** 8.5 × 11 in, no bleed, 0.5 in safe margin, **black & white interior** (white paper), 80 pages, fonts embedded.

| Pages | Contents |
|---|---|
| 1 | Title |
| 2 | "This book belongs to" + how to use this book |
| 3 | My Alphabet Animals chart (A–Z) |
| 4–29 | Uppercase A–Z, one page each: big letter with stroke numbers/arrows, animal accent, 6 rows (model + dashed, dashed, dashed/dots, dots only, model + blank, blank) |
| 30–31 | Uppercase review: trace the ABCs; fill in the missing letters + what comes next |
| 32–57 | Lowercase a–z, same layout |
| 58–59 | Lowercase review, same as 30–31 |
| 60–61 | Match big and small letters |
| 62–74 | First words: two words for each letter (ant, apple, bus, bat …), two letters per page |
| 75–78 | Trace and write 12 short sentences about the animals |
| 79 | "Alphabet Champion!" certificate |
| 80 | Extra practice lines |

```bash
python3 Trace-and-Write-the-Alphabet/src/pages.py      # all pages -> pages/*.pdf + .png previews (or: pages.py A b)
python3 Trace-and-Write-the-Alphabet/src/interior.py   # interior.pdf + checks (count, size, fonts, margin, no colour ink)
python3 Trace-and-Write-the-Alphabet/src/cover.py      # cover.pdf (spine 80 × 0.002252 in, B&W white paper — confirm with KDP's calculator)
```
