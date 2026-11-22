"""Assemble interior.pdf (30 pages) and check it against the KDP specs in the brief.
Order: 1 title, 2 name, 3-28 letters A-Z, 29 certificate, 30 blank.
Usage: python3 src/interior.py
"""
import string, subprocess, tempfile, os
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter

order = ["00_title", "01_name"] + list(string.ascii_uppercase) + ["29_certificate", "30_blank"]
w = PdfWriter()
for n in order:
    w.add_page(PdfReader(f"pages/{n}.pdf").pages[0])
w.add_metadata({"/Title": "My First A to Z Animals Copy Coloring Book", "/Author": "TinyTusk"})
with open("interior.pdf", "wb") as f:
    w.write(f)

# --- checks -----------------------------------------------------------------------
r = PdfReader("interior.pdf")
problems = []
print("pages:", len(r.pages))
if len(r.pages) != 30:
    problems.append(f"expected 30 pages, got {len(r.pages)}")
for i, p in enumerate(r.pages, 1):
    wd, ht = float(p.mediabox.width) / 72, float(p.mediabox.height) / 72
    if abs(wd - 8.5) > 0.001 or abs(ht - 11) > 0.001:
        problems.append(f"page {i}: size {wd}x{ht}")
fonts = subprocess.run(["pdffonts", "interior.pdf"], capture_output=True, text=True).stdout.splitlines()[2:]
for line in fonts:
    cols = line.split()
    if "no" in cols[-5:-2]:                       # emb / sub / uni columns
        problems.append("font not embedded: " + line)
print("fonts:", sorted({l.split()[0].split("+")[-1] for l in fonts}))
# nothing may print outside the 0.5" margin: render at 300 dpi and look at the outer band
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
