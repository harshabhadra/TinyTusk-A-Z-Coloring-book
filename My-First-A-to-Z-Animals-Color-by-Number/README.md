# My First A to Z Animals Color by Number

Fourth TinyTusk book: 26 colour-by-number pages made from the A to Z book's existing line art and colour
specs (no new art). 38 pages, 8.5" × 11", premium color interior (guess), no bleed, ages 4–8 (guess).

| Pages | Contents |
|---|---|
| 1 | Title page |
| 2 | "This book belongs to" (A to Z book design) |
| 3 | How to color by number + the 12 crayons |
| 4–29 | A–Z: numbered line art + crayon colour key |
| 30 | "Well done!" certificate |
| 31–37 | Full-colour answer key (the A to Z book's `colored/` pictures) |
| 38 | Blank |

How the numbers are made (`src/puzzle.py`):
- every region's colour comes from `../specs/<L>.json`, exactly as `../src/color.py` used it for `../colored/<L>.png`
- each page numbers its own colours 1..n in palette order, so numbers are single digits (max 5)
- a number goes at the widest point of its region, 9–18 pt depending on room; big or ring-shaped regions get up to 4 numbers
- regions too small for a 9 pt number are printed already coloured
- regions the spec leaves white get no number

```bash
python3 src/puzzle.py      # art/<L>_puzzle.png + art/<L>_numbers.json + pages/A-Z
python3 src/extras.py      # title, name, how-to, certificate, answer key, blank
python3 src/interior.py    # interior.pdf + KDP checks (same as ../src/interior.py)
python3 src/cover.py       # cover.pdf (spine 38 x 0.002347 in, no spine text)
```

Reuses `../src/layout.py`, `../src/frontmatter.py`, `../src/cover.py`, `../src/palette.py`, `../fonts`, `../clean`,
`../specs`, `../colored`; nothing outside this folder is changed.
