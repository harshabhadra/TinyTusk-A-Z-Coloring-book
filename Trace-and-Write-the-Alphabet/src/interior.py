"""Assemble Trace-and-Write-the-Alphabet/interior.pdf (82 pages, order from pages.page_order()) and check it
against KDP specs: page count/size, fonts embedded, nothing outside the 0.5 in margin, black & white only.
Same checks as the other TinyTusk books.
Usage: python3 Trace-and-Write-the-Alphabet/src/interior.py
"""
import os, sys, subprocess, tempfile
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BOOK)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pages import page_order, PAGES  # noqa: E402
os.chdir(BOOK)
order = page_order()

w = PdfWriter()
for n in order:
    w.add_page(PdfReader(f"pages/{n}.pdf").pages[0])
w.add_metadata({"/Title": "Trace & Write the Alphabet", "/Author": "TinyTusk Books"})
with open("interior.pdf", "wb") as f:
    w.write(f)

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
    if "no" in line.split()[-5:-2]:
        problems.append("font not embedded: " + line)
print("fonts:", sorted({l.split()[0].split("+")[-1] for l in fonts}))
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["pdftoppm", "-r", "300", "interior.pdf", f"{d}/p"], check=True)
    for i, fn in enumerate(sorted(os.listdir(d)), 1):
        rgb = np.asarray(Image.open(f"{d}/{fn}").convert("RGB")).astype(int)
        a = rgb.min(axis=2)
        m = 150                                    # 0.5 in at 300 dpi
        band = np.concatenate([a[:m].ravel(), a[-m:].ravel(), a[:, :m].ravel(), a[:, -m:].ravel()])
        if band.min() < 250:
            problems.append(f"page {i}: ink outside the 0.5in margin")
        if (rgb.max(axis=2) - rgb.min(axis=2)).max() > 8:
            problems.append(f"page {i}: colour ink on a black & white interior")
print("size: %.1f MB" % (os.path.getsize("interior.pdf") / 1e6))
print("OK" if not problems else "\n".join(problems))
