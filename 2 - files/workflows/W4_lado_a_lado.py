# W4 - comparativo lado a lado: original | esqueleto | gerado (para aprovacao).
# Roda fora do ComfyUI (so le/grava arquivos). Uso:
#   python -I -X utf8 W4_lado_a_lado.py <original.mp4> <pose.mp4> <gerado.mp4> <saida.mp4>
# Alinhamento: o gerado tem N frames (24 fps); original e pose sao amostrados de forma uniforme
# nos mesmos N pontos - igual ao VideoFrameSample(uniform) usado no W3a. Audio vem do gerado.
import sys, av, numpy as np
from PIL import Image, ImageDraw, ImageFont

orig_p, pose_p, gen_p, out_p = sys.argv[1:5]
H = 864          # altura comum dos 3 paineis
GAP = 8
LABEL_H = 40

def frames(path):
    c = av.open(path)
    fr = [f.to_image() for f in c.decode(video=0)]
    c.close()
    return fr

def fit(img, h):
    w = round(img.width * h / img.height / 2) * 2
    return img.resize((w, h), Image.LANCZOS)

orig, pose, gen = frames(orig_p), frames(pose_p), frames(gen_p)
n = len(gen)
idx = lambda m: [round(i * (m - 1) / (n - 1)) for i in range(n)]
io, ip = idx(len(orig)), idx(len(pose))

w_o, w_p, w_g = fit(orig[0], H).width, fit(pose[0], H).width, fit(gen[0], H).width
W = w_o + w_p + w_g + 2 * GAP
W += W % 2
try:
    font = ImageFont.truetype("arial.ttf", 22)
except OSError:
    font = ImageFont.load_default()

gin = av.open(gen_p)
fps = gin.streams.video[0].average_rate or 24
out = av.open(out_p, "w")
vs = out.add_stream("libx264", rate=fps)
vs.width, vs.height, vs.pix_fmt = W, H + LABEL_H, "yuv420p"
vs.options = {"crf": "18"}
a_in = gin.streams.audio[0] if gin.streams.audio else None
a_out = out.add_stream("aac", rate=a_in.rate) if a_in else None

for i in range(n):
    canvas = Image.new("RGB", (W, H + LABEL_H), (18, 18, 18))
    x = 0
    for img, label in ((fit(orig[io[i]], H), "ORIGINAL"), (fit(pose[ip[i]], H), "ESQUELETO"), (fit(gen[i], H), "GERADO")):
        canvas.paste(img, (x, LABEL_H))
        d = ImageDraw.Draw(canvas)
        tw = d.textlength(label, font=font)
        d.text((x + (img.width - tw) / 2, 8), label, fill=(235, 235, 235), font=font)
        x += img.width + GAP
    for p in vs.encode(av.VideoFrame.from_ndarray(np.asarray(canvas), format="rgb24")):
        out.mux(p)
for p in vs.encode():
    out.mux(p)

if a_in:
    gin.seek(0)
    for f in gin.decode(audio=0):
        f.pts = None
        for p in a_out.encode(f):
            out.mux(p)
    for p in a_out.encode():
        out.mux(p)
out.close(); gin.close()
print("ok", out_p, f"{W}x{H + LABEL_H}", n, "frames", float(fps), "fps", "com audio" if a_in else "sem audio")
