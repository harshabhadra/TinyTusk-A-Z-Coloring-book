"""Build one or more letter pages end to end from their spec.
Usage: python3 src/build.py B C D      (spec field "raw" names the source image in raw/)
"""
import json, subprocess, sys

for L in sys.argv[1:]:
    L = L.upper()
    spec = f"specs/{L}.json"
    raw = json.load(open(spec))["raw"]
    run = lambda *a: subprocess.run(["python3", *a], check=True, capture_output=True, text=True).stdout
    rep = json.loads(run("src/clean.py", f"raw/{raw}", f"clean/{L}.png", "--spec", spec))
    run("src/color.py", "regions", f"clean/{L}.png", spec)
    out = run("src/color.py", "fill", f"clean/{L}.png", spec, f"colored/{L}.png")
    run("src/layout.py", L)
    print(f"{L}: {rep['stroke_pt_after']} pt, {rep['interior_regions']} regions ({rep['tiny_regions']} tiny) -> {out.strip()}")
