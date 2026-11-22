# Comparativo de N videos lado a lado, com rotulos (ex.: v1 x v4). Fora do ComfyUI.
# Uso: python -I -X utf8 W4_compara_versoes.py <saida.mp4> <rotulo1> <video1> <rotulo2> <video2> [...]
# Todos os paineis na mesma altura (a do maior video); alinhamento por amostragem uniforme no numero de frames do 1o.
import sys, av, numpy as np
from PIL import Image, ImageDraw, ImageFont

# Opcoes (antes de <saida.mp4>): --altura=N (altura dos paineis; padrao = maior video)
#                                --frames=N (quadros na saida; padrao = do 1o video)
opts = {a[2:].split("=")[0]: int(a.split("=")[1]) for a in sys.argv[1:] if a.startswith("--")}
args = [a for a in sys.argv[1:] if not a.startswith("--")]
out_p = args[0]
pairs = list(zip(args[1::2], args[2::2]))
LABEL_H, GAP = 44, 8

def frames(p):
    c = av.open(p); fr = [f.to_image() for f in c.decode(video=0)]; c.close(); return fr

vids = [(lab, frames(p)) for lab, p in pairs]
H = opts.get("altura", max(f[0].height for _, f in vids))
H -= H % 2
n = opts.get("frames", len(vids[0][1]))
def fit(im):
    w = round(im.width * H / im.height / 2) * 2
    return im.resize((w, H), Image.LANCZOS)
ws = [fit(f[0]).width for _, f in vids]
W = sum(ws) + GAP * (len(vids) - 1); W += W % 2
font = ImageFont.truetype("arial.ttf", 26)

out = av.open(out_p, "w")
vs = out.add_stream("libx264", rate=24); vs.width, vs.height, vs.pix_fmt = W, H + LABEL_H, "yuv420p"
vs.options = {"crf": "16"}
for i in range(n):
    cv = Image.new("RGB", (W, H + LABEL_H), (18, 18, 18)); d = ImageDraw.Draw(cv); x = 0
    for (lab, fr), w in zip(vids, ws):
        j = round(i * (len(fr) - 1) / (n - 1)); cv.paste(fit(fr[j]), (x, LABEL_H))
        d.text((x + (w - d.textlength(lab, font=font)) / 2, 8), lab, fill=(235, 235, 235), font=font); x += w + GAP
    for p in vs.encode(av.VideoFrame.from_ndarray(np.asarray(cv), format="rgb24")): out.mux(p)
for p in vs.encode(): out.mux(p)
out.close()
print("ok", out_p, f"{W}x{H + LABEL_H}", n, "frames")
