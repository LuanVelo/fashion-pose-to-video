"""Detail sheet for the human review: every 12th frame, two crops at native resolution (upper body + hands, legs + feet).
Usage: python -I detail_sheet.py <video.mp4> <out.jpg> [step]"""
import av, sys
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]; STEP = int(sys.argv[3]) if len(sys.argv) > 3 else 12
c = av.open(src); fr = [(i, f.to_image()) for i, f in enumerate(c.decode(video=0)) if i % STEP == 0 or i == 123]; c.close()
tiles = []
for i, f in fr:
    w, h = f.size
    a = f.crop((int(w * .15), int(h * .12), int(w * .85), int(h * .6)))   # torso + hands
    b = f.crop((int(w * .15), int(h * .55), int(w * .85), int(h * .99)))  # legs + feet
    t = Image.new("RGB", (a.width, a.height + b.height + 4), "black"); t.paste(a, (0, 0)); t.paste(b, (0, a.height + 4))
    ImageDraw.Draw(t).text((5, 5), f"#{i}", fill="red")
    t = t.resize((int(t.width * 0.62), int(t.height * 0.62)))
    tiles.append(t)
cols = 6; W, H = tiles[0].size
sh = Image.new("RGB", (W * cols, H * ((len(tiles) + cols - 1) // cols)), "black")
for k, t in enumerate(tiles): sh.paste(t, ((k % cols) * W, (k // cols) * H))
sh.save(out, quality=85); print(sh.size)
