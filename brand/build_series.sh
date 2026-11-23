#!/bin/sh
# Rebuild the three TinyTusk series books so every "Collect the series" strip and "More TinyTusk books" page
# shows the latest front covers. Run from the repo root after changing brand/logo.png or any cover.
# The original A-Z coloring book (repo root) is only read here, never rebuilt.
set -e
cd "$(dirname "$0")/.."
python3 brand/make_assets.py
python3 -c "import sys; sys.path.insert(0, 'brand'); import brand; brand.render_front('cover.pdf', 'az-coloring')"

# pass 1: covers (each refreshes brand/series/<book>.png); pass 2: covers again with every thumbnail present
for pass in 1 2; do
  python3 TinyTusk-ABC-Letter-Tracing-Workbook/src/cover.py
  (cd TinyTusk-A-to-Z-Animals-Color-by-Number/src && python3 cover.py)
  python3 Trace-and-Write-the-Alphabet/src/cover.py
done

# interiors (the last page shows the other books' covers)
python3 TinyTusk-ABC-Letter-Tracing-Workbook/src/pages.py
python3 TinyTusk-ABC-Letter-Tracing-Workbook/src/interior.py
(cd TinyTusk-A-to-Z-Animals-Color-by-Number/src && python3 extras.py && python3 interior.py)
python3 Trace-and-Write-the-Alphabet/src/pages.py
python3 Trace-and-Write-the-Alphabet/src/interior.py
