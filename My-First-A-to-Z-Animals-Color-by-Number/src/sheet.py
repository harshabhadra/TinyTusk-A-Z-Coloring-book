"""Contact sheet of page PNGs: python3 src/sheet.py out.png cols width a.png b.png ..."""
import sys
from PIL import Image
out, cols, tw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ims = [Image.open(p).convert("RGB") for p in sys.argv[4:]]
th = round(tw * ims[0].height / ims[0].width)
rows = -(-len(ims) // cols)
sheet = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + 16) + 16), (225, 225, 225))
for k, im in enumerate(ims):
    im = im.resize((tw, round(tw * im.height / im.width)), Image.LANCZOS)
    sheet.paste(im, (16 + (k % cols) * (tw + 16), 16 + (k // cols) * (th + 16)))
sheet.save(out)
