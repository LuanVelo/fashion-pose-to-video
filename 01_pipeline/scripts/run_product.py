"""Replicable flow for one e-commerce product photo x one catalog pose (W5 v21 split, TEST).

Steps (each one a command, so a batch of products can run step by step):
  prep    <product> <photo> <pose> ...      keypoints of the photo, photo reframed to each pose (keypoint mode)
  frame0  <product> <pose> [N]              N first-frame candidates (W5_frame0_v21, ~3-10 s each) + a contact page
  video   <product> <pose> <frame0 seed> [video seeds...]   video(s) from the CHOSEN first frame (W5_video_v21)
                                                             + report.mp4, review sheet and detail sheet per video
The choice of the first frame and the approval of the video are made by people (for now), on the pages written by
the frame0 and video steps. Everything else is automatic.

Folders (ComfyUI side):
  IN/motion/products/<product>_front.png                 product photo as received
  IN/motion/prep/<product>/                               photo keypoints, reframed photo per pose
  OUT/motion/frame0/<product>__<pose>/s<seed>/frame0_*.png + candidates.html
  IN/motion/frame0/<product>__<pose>.png                  the chosen first frame
  OUT/motion/video/<product>__<pose>/s<frame0 seed>-v<video seed>/video_*.mp4 (+ report, review, detail)
Poses need IN/motion/poses/<pose>/pose.mp4 and keypoints.json (pose_keypoints.py extract on original.mp4).

Usage (ComfyUI's Python): python -I -X utf8 run_product.py <step> ...
"""
import sys, os, json, glob, shutil, subprocess, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
IN = r"D:\Comfy-Desktop\ComfyUI-Shared\input"
OUT = r"D:\Comfy-Desktop\ComfyUI-Shared\output"
API = "http://127.0.0.1:8188"
WF = os.path.join(HERE, "..", "workflows")
SEEDS0 = [20261121, 1, 2, 3, 4, 5, 6, 7]


def run(*args):
    r = subprocess.run([PY, "-I", "-X", "utf8", *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return r.stdout


def queue(g, client):
    req = urllib.request.Request(API + "/prompt", data=json.dumps({"prompt": g, "client_id": client}).encode(),
                                 headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req).read())
    if r.get("node_errors"):
        raise SystemExit(str(r["node_errors"]))
    return r["prompt_id"]


def wait(ids):
    for pid in ids:
        while True:
            h = json.loads(urllib.request.urlopen(f"{API}/history/{pid}").read())
            if pid in h:
                if h[pid].get("status", {}).get("status_str") == "error":
                    print("ERROR in", pid, str(h[pid]["status"].get("messages"))[:400])
                break
            time.sleep(2)


def prep(product, photo, poses):
    d = os.path.join(IN, "motion", "prep", product)
    os.makedirs(d, exist_ok=True)
    kp = os.path.join(d, "photo_keypoints.json")
    if not os.path.exists(kp):
        from PIL import Image
        w, h = Image.open(photo).size
        run(os.path.join(HERE, "pose_keypoints.py"), "extract", photo, kp, f"--size=576x{round(576 * h / w)}")
    for pose in poses:
        out = os.path.join(d, f"{pose}.png")
        print(pose, run(os.path.join(HERE, "reframe_product.py"), photo, os.path.join(IN, "motion", "poses", pose, "pose.mp4"),
                        out, os.path.join(d, f"{pose}_overlay.jpg"), f"--kp-product={kp}",
                        f"--kp-pose={os.path.join(IN, 'motion', 'poses', pose, 'keypoints.json')}").strip())


def frame0(product, pose, n=6):
    g0 = json.load(open(os.path.join(WF, "W5_frame0_v21_api.json"), encoding="utf-8"))
    name = f"{product}__{pose}"
    ids = []
    for s in SEEDS0[:n]:
        g = json.loads(json.dumps(g0))
        g["1"]["inputs"]["value"] = f"{name}/s{s}"
        g["5"]["inputs"]["image"] = f"motion/prep/{product}/{pose}.png"
        g["210"]["inputs"]["file"] = f"motion/poses/{pose}/pose.mp4"
        g["120"]["inputs"]["noise_seed"] = s
        ids.append(queue(g, "run_product"))
    wait(ids)
    d = os.path.join(OUT, "motion", "frame0", name)
    cards = []
    for s in SEEDS0[:n]:
        f = sorted(glob.glob(os.path.join(d, f"s{s}", "frame0_*.png")))
        if f:
            rel = os.path.relpath(f[-1], d).replace("\\", "/")
            cards.append(f'<figure><a href="{rel}"><img src="{rel}"></a><figcaption>seed <b>{s}</b></figcaption></figure>')
    prod = os.path.relpath(os.path.join(IN, "motion", "prep", product, f"{pose}.png"), d).replace("\\", "/")
    html = (f"<!doctype html><meta charset=utf-8><title>{name} first frames</title><style>body{{font:14px system-ui;background:#111;color:#eee;margin:16px}}"
            "main{display:flex;flex-wrap:wrap;gap:10px}figure{margin:0;width:260px}img{width:100%;border-radius:4px}a{color:#8cf}</style>"
            f"<h3>{name} — first-frame candidates</h3><p>Check hands, arms, feet, face, the garment against the product. Then run:<br>"
            f"<code>run_product.py video {product} {pose} &lt;seed&gt;</code></p>"
            f"<main><figure><img src='{prod}'><figcaption>PRODUCT (reframed)</figcaption></figure>{''.join(cards)}</main>")
    open(os.path.join(d, "candidates.html"), "w", encoding="utf-8").write(html)
    print(len(cards), "candidates ->", os.path.join(d, "candidates.html"))


def video(product, pose, s0, vseeds):
    name = f"{product}__{pose}"
    src = sorted(glob.glob(os.path.join(OUT, "motion", "frame0", name, f"s{s0}", "frame0_*.png")))[-1]
    os.makedirs(os.path.join(IN, "motion", "frame0"), exist_ok=True)
    chosen = os.path.join(IN, "motion", "frame0", f"{name}__s{s0}.png")
    shutil.copy2(src, chosen)
    g0 = json.load(open(os.path.join(WF, "W5_video_v21_api.json"), encoding="utf-8"))
    ids, names = [], []
    for v in vseeds:
        g = json.loads(json.dumps(g0))
        run_name = f"{name}/s{s0}-v{v}"
        g["1"]["inputs"]["value"] = run_name
        g["5"]["inputs"]["image"] = f"motion/prep/{product}/{pose}.png"
        g["210"]["inputs"]["file"] = f"motion/poses/{pose}/pose.mp4"
        g["250"]["inputs"]["image"] = f"motion/frame0/{name}__s{s0}.png"
        g["221"]["inputs"]["noise_seed"] = v
        ids.append(queue(g, "run_product"))
        names.append(run_name)
    wait(ids)
    for rn in names:
        n = f"video/{rn}"
        run(os.path.join(HERE, "generation_report.py"), n, pose, f"motion/prep/{product}/{pose}.png")
        print(run(os.path.join(HERE, "generation_review.py"), n).strip())
        vid = sorted(glob.glob(os.path.join(OUT, "motion", n, "video_0*.mp4")))[-1]
        run(os.path.join(HERE, "detail_sheet.py"), vid, os.path.join(OUT, "motion", n, "detail_sheet.jpg"))
    print("videos ->", os.path.join(OUT, "motion", "video", name))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "prep":
        prep(a[1], a[2], a[3:])
    elif a[0] == "frame0":
        frame0(a[1], a[2], int(a[3]) if len(a) > 3 else 6)
    elif a[0] == "video":
        video(a[1], a[2], int(a[3]), [int(x) for x in a[4:]] or [20261121])
