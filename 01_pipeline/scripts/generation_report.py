"""One report per W5 generation: PRODUCT | ORIGINAL POSE VIDEO | SKELETON | GENERATED, side by side, in sync.

For each generation folder OUT/motion/<name>/ it writes:
  report.mp4   4 panels with labels, 24 fps, same length as the generated video (the product photo is a still panel)
and refreshes one local index page:
  OUT/motion/reports.html   every generation as a row (product image + the 3 videos playing in sync)

The original pose video is third-party (e-commerce) footage: reports stay local, never in the repository.

Usage (ComfyUI's Python):  python -I -X utf8 generation_report.py <name> <pose> <product image>
  <name>     generation folder under OUT/motion/, e.g. production/<product>_<pose> or experiments/EXP-001_<slug>/<product>__<pose>__s<seed>
  <pose>     pose folder under IN/motion/poses/
  <product>  product image path relative to IN/ (e.g. motion/products/caramel-tank-jeans_front.png)
  --index-only   only rebuild reports.html
"""
import sys, os, glob, json, html
from fractions import Fraction
import av, numpy as np
from PIL import Image, ImageDraw, ImageFont

IN_ROOT = r"D:\Comfy-Desktop\ComfyUI-Shared\input"
OUT = r"D:\Comfy-Desktop\ComfyUI-Shared\output\motion"
POSES = os.path.join(IN_ROOT, "motion", "poses")
PARKED = os.path.join(IN_ROOT, "motion", "poses_parked")


def pose_dir(pose):
    """The pose folder: input/motion/poses/<pose>, or input/motion/poses_parked/<group>/<pose> for rejected/untested poses."""
    for d in [os.path.join(POSES, pose)] + sorted(glob.glob(os.path.join(PARKED, "*", pose))):
        if os.path.isdir(d):
            return d
    raise SystemExit(f"pose not found: {pose}")
H = 960          # panel height
BAR = 36         # label bar height
REGISTRY = os.path.join(OUT, "reports.json")


def newest(pattern):
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    if not files:
        raise SystemExit(f"nothing found: {pattern}")
    return files[-1]


def frames(path):
    c = av.open(path)
    s = c.streams.video[0]
    out = [f.to_image().convert("RGB") for f in c.decode(s)]
    c.close()
    return out


def fit(im):
    return im.resize((round(im.width * H / im.height / 2) * 2, H), Image.LANCZOS)


def font():
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, 22)
        except OSError:
            pass
    return ImageFont.load_default()


def build(name, pose, product):
    gdir = os.path.join(OUT, name)
    gen = frames(newest(os.path.join(gdir, "video_0*.mp4")))
    skel = frames(os.path.join(pose_dir(pose), "pose.mp4"))
    orig_path = os.path.join(pose_dir(pose), "original.mp4")
    orig = frames(orig_path) if os.path.exists(orig_path) else None
    prod = fit(Image.open(os.path.join(IN_ROOT, product)).convert("RGB"))
    n = len(gen)
    pick = lambda seq, i: seq[min(round(i * (len(seq) - 1) / max(n - 1, 1)), len(seq) - 1)]
    panels = [("PRODUCT", lambda i: prod), ("ORIGINAL POSE VIDEO", (lambda i: fit(pick(orig, i))) if orig else (lambda i: Image.new("RGB", (round(H * 9 / 16), H)))),
              ("SKELETON", lambda i: fit(pick(skel, i))), ("GENERATED", lambda i: fit(gen[i]))]
    first = [p[1](0) for p in panels]
    W = sum(im.width for im in first) + 6 * (len(first) - 1)
    W += W % 2
    f = font()
    out_path = os.path.join(gdir, "report.mp4")
    o = av.open(out_path, "w")
    v = o.add_stream("libx264", rate=24)
    v.width, v.height, v.pix_fmt, v.options = W, H + BAR, "yuv420p", {"crf": "18"}
    for i in range(n):
        canvas = Image.new("RGB", (W, H + BAR), (17, 17, 17))
        d = ImageDraw.Draw(canvas)
        x = 0
        for label, get in panels:
            im = get(i)
            canvas.paste(im, (x, BAR))
            d.text((x + 8, 6), label, fill=(235, 235, 235), font=f)
            x += im.width + 6
        d.text((W - 260, 6), f"{pose} · frame {i + 1}/{n}", fill=(150, 150, 150), font=f)
        fr = av.VideoFrame.from_image(canvas)
        fr.pts, fr.time_base = i, Fraction(1, 24)
        for pk in v.encode(fr):
            o.mux(pk)
    for pk in v.encode():
        o.mux(pk)
    o.close()
    reg = json.load(open(REGISTRY, encoding="utf-8")) if os.path.exists(REGISTRY) else {}
    reg[name] = {"pose": pose, "product": product}
    json.dump(reg, open(REGISTRY, "w", encoding="utf-8"), indent=1)
    print("ok", out_path, f"{W}x{H + BAR}", n, "frames")


def index():
    reg = json.load(open(REGISTRY, encoding="utf-8")) if os.path.exists(REGISTRY) else {}
    rel = lambda p: os.path.relpath(p, OUT).replace("\\", "/")
    rows = []
    for name, r in sorted(reg.items()):
        gdir = os.path.join(OUT, name)
        vids = sorted(glob.glob(os.path.join(gdir, "video_0*.mp4")), key=os.path.getmtime)
        if not vids:
            continue
        rows.append({"name": name, "pose": r["pose"], "product": rel(os.path.join(IN_ROOT, r["product"])),
                     "original": rel(os.path.join(pose_dir(r["pose"]), "original.mp4")), "skeleton": rel(os.path.join(pose_dir(r["pose"]), "pose.mp4")),
                     "generated": rel(vids[-1]), "report": rel(os.path.join(gdir, "report.mp4"))})
    page = """<!doctype html><meta charset="utf-8"><title>W5 generations</title>
<style>body{font:14px system-ui,sans-serif;background:#111;color:#eee;margin:0}header{position:sticky;top:0;background:#1b1b1b;padding:10px 16px;z-index:2}
.row{display:flex;gap:6px;align-items:flex-start;padding:10px 16px;border-bottom:1px solid #333}.row>div{flex:1;text-align:center;font-size:11px;color:#aaa}
img,video{width:100%;background:#000;border-radius:4px;display:block}.t{flex:0 0 170px!important;text-align:left!important;color:#eee;font-size:13px}
button{background:#333;color:#eee;border:1px solid #555;border-radius:4px;padding:4px 10px;cursor:pointer}</style>
<header><b>W5 generations</b> · product | original pose video | skeleton | generated · click a row to play it in sync · <a style="color:#8cf" href="#" id="all">play all</a></header>
<main id="m"></main><script>
const R=__ROWS__; const m=document.getElementById("m");
for(const r of R){const d=document.createElement("div");d.className="row";
d.innerHTML=`<div class="t"><b>${r.name}</b><br>${r.pose}<br><a style="color:#8cf" href="${r.report}">report.mp4</a></div>
<div><img src="${r.product}">product</div><div><video src="${r.original}" muted loop playsinline preload="metadata"></video>original pose video</div>
<div><video src="${r.skeleton}" muted loop playsinline preload="metadata"></video>skeleton</div><div><video src="${r.generated}" muted loop playsinline preload="metadata"></video>generated</div>`;
const v=[...d.querySelectorAll("video")];d.onclick=e=>{if(e.target.tagName==="A")return;const on=v[0].paused;v.forEach(x=>{x.currentTime=0;on?x.play():x.pause()})};m.appendChild(d)}
document.getElementById("all").onclick=e=>{e.preventDefault();document.querySelectorAll("video").forEach(x=>{x.currentTime=0;x.play()})};
</script>"""
    path = os.path.join(OUT, "reports.html")
    open(path, "w", encoding="utf-8").write(page.replace("__ROWS__", json.dumps(rows)))
    print(len(rows), "generations ->", path)


if __name__ == "__main__":
    if sys.argv[1:] == ["--index-only"]:
        index()
    else:
        build(*sys.argv[1:4])
        index()
