"""Assemble My-First-ABC-Letter-Tracing-Workbook/interior.pdf (60 pages) and check it against KDP specs.
Order: 1 title, 2 name, 3-5 pencil warm-ups, 6-57 letters (A on 6-7 as a left/right spread ... Z on 56-57),
58 uppercase review, 59 lowercase review, 60 certificate.
Checks: page count/size, fonts embedded, nothing outside the 0.5 in margin, black & white only (no colour ink).
Usage: python3 My-First-ABC-Letter-Tracing-Workbook/src/interior.py
"""
import os, string, subprocess, tempfile
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BOOK)
PAGES = 60
order = ["01_title", "02_name", "03_warmup_lines", "04_warmup_zigzag", "05_warmup_curves"]
for i, L in enumerate(string.ascii_uppercase):
    n = 6 + 2 * i
    order += [f"{n:02d}_{L}", f"{n + 1:02d}_{L}_practice"]
order += ["58_review_upper", "59_review_lower", "60_certificate"]

w = PdfWriter()
for n in order:
    w.add_page(PdfReader(f"pages/{n}.pdf").pages[0])
w.add_metadata({"/Title": "My First ABC Letter Tracing Workbook", "/Author": "TinyTusk"})
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
