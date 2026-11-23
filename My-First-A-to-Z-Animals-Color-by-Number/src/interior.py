"""Assemble interior.pdf (40 pages) and run the same KDP checks as the A-Z book (../src/interior.py).
Order: 1 title, 2 copyright, 3 name, 4 how to, 5-30 letters A-Z, 31 certificate, 32-38 answer key,
39 color the TinyTusk elephant, 40 more TinyTusk books.
Usage: python3 src/interior.py
"""
import string, subprocess, tempfile, os
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter
from common import BOOK, TITLE, AUTHOR, PAGES

os.chdir(BOOK)
order = ["01_title", "02_copyright", "03_name", "04_how_to"] + list(string.ascii_uppercase) + ["31_certificate"] \
    + [f"{n}_answers" for n in range(32, 39)] + ["39_color_the_elephant", "40_more_books"]
w = PdfWriter()
for n in order:
    w.add_page(PdfReader(f"pages/{n}.pdf").pages[0])
w.add_metadata({"/Title": TITLE, "/Author": AUTHOR})
with open("interior.pdf", "wb") as f:
    w.write(f)

# --- checks (same as the A-Z book) --------------------------------------------------
r = PdfReader("interior.pdf")
problems = []
print("pages:", len(r.pages))
if len(r.pages) != PAGES:
    problems.append(f"expected {PAGES} pages, got {len(r.pages)}")
for i, p in enumerate(r.pages, 1):
    wd, ht = float(p.mediabox.width) / 72, float(p.mediabox.height) / 72
    if abs(wd - 8.5) > 0.001 or abs(ht - 11) > 0.001:
        problems.append(f"page {i}: size {wd}x{ht}")
fonts = subprocess.run(["pdffonts", "interior.pdf"], capture_output=True, text=True).stdout.splitlines()[2:]
for line in fonts:
    cols = line.split()
    if "no" in cols[-5:-2]:
        problems.append("font not embedded: " + line)
print("fonts:", sorted({l.split()[0].split("+")[-1] for l in fonts}))
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["pdftoppm", "-r", "300", "-gray", "interior.pdf", f"{d}/p"], check=True)
    for i, fn in enumerate(sorted(os.listdir(d)), 1):
        a = np.array(Image.open(f"{d}/{fn}"))
        m = 150                                    # 0.5 in at 300 dpi
        band = np.concatenate([a[:m].ravel(), a[-m:].ravel(), a[:, :m].ravel(), a[:, -m:].ravel()])
        if band.min() < 250:
            problems.append(f"page {i}: ink outside the 0.5in margin")
print("size: %.1f MB" % (os.path.getsize("interior.pdf") / 1e6))
print("OK" if not problems else "\n".join(problems))
