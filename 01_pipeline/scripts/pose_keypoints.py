"""Pose keypoints as numbers, with ComfyUI's own SDPose code (no custom nodes). EXP-004.

ComfyUI computes OpenPose keypoints in SDPoseKeypointExtractor but no native node saves them. This script imports
ComfyUI's nodes in-process and:
  extract <video|image> <out.json> [--frames=124] [--size=576x1024]
      runs SDPose (sdpose_wholebody_fp16, like W1 v3) on the frames (uniformly resampled to N frames for a video)
      resized to the given canvas, and writes the OpenPose frames JSON (canvas_width, canvas_height, people[...]).
  draw <in.json> <out.mp4>
      draws the keypoints with ComfyUI's SDPoseDrawKeypoints and the W1 v3 settings
      (body + hands + feet + head, no face, stick width 4, score threshold 0.5), 24 fps.

Free ComfyUI's VRAM first (POST /free) when the server holds big models. Run with ComfyUI's Python:
  python -I -X utf8 pose_keypoints.py extract <in> <out.json>
"""
import sys, os, json
from fractions import Fraction

COMFY = r"D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI"
CKPT = r"D:\Comfy-Desktop\ComfyUI-Shared\models\checkpoints\sdpose_wholebody_fp16.safetensors"
sys.path.insert(0, COMFY)

import numpy as np, torch, av  # noqa: E402
from PIL import Image  # noqa: E402

DRAW = dict(draw_body=True, draw_hands=True, draw_face=False, draw_feet=True, stick_width=4, face_point_size=2,
            score_threshold=0.5, draw_head=True)


def load_frames(path, n, W, H):
    if path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        ims = [Image.open(path).convert("RGB")]
    else:
        c = av.open(path)
        ims = [f.to_image() for f in c.decode(video=0)]
        c.close()
        if len(ims) != n:
            idx = [round(i * (len(ims) - 1) / (n - 1)) for i in range(n)]
            ims = [ims[i] for i in idx]
    arr = np.stack([np.asarray(im.resize((W, H), Image.LANCZOS), dtype=np.float32) / 255.0 for im in ims])
    return torch.from_numpy(arr)


def extract(src, out, n=124, size="576x1024"):
    import comfy.sd, comfy.sample  # noqa: F401  (the extractor calls comfy.sample.sample)
    from comfy_extras.nodes_sdpose import SDPoseKeypointExtractor
    W, H = map(int, size.split("x"))
    images = load_frames(src, n, W, H)
    model, _, vae, *_ = comfy.sd.load_checkpoint_guess_config(CKPT, output_vae=True, output_clip=False)
    with torch.inference_mode():  # ComfyUI runs nodes in inference mode
        res = SDPoseKeypointExtractor.execute(model, vae, images, 16)
    kp = res.result[0] if hasattr(res, "result") else res[0]
    json.dump(kp, open(out, "w"))
    people = sum(len(f["people"]) for f in kp)
    print(f"{len(kp)} frames, {people} people detected, canvas {kp[0]['canvas_width']}x{kp[0]['canvas_height']} -> {out}")


def draw(src, out):
    from comfy_extras.nodes_sdpose import SDPoseDrawKeypoints
    kp = json.load(open(src))
    with torch.inference_mode():
        res = SDPoseDrawKeypoints.execute(kp, **DRAW)
    img = (res.result[0] if hasattr(res, "result") else res[0]).numpy()
    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    o = av.open(out, "w")
    v = o.add_stream("libx264", rate=24)
    v.height, v.width = img.shape[1:3]
    v.pix_fmt, v.options = "yuv420p", {"crf": "10"}
    for i, a in enumerate(img):
        f = av.VideoFrame.from_ndarray(np.ascontiguousarray(a), format="rgb24")
        f.pts, f.time_base = i, Fraction(1, 24)
        for pk in v.encode(f):
            o.mux(pk)
    for pk in v.encode():
        o.mux(pk)
    o.close()
    print(f"{len(img)} frames drawn -> {out}")


if __name__ == "__main__":
    opts = {a[2:].split("=")[0]: a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--")}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args[0] == "extract":
        extract(args[1], args[2], int(opts.get("frames", 124)), opts.get("size", "576x1024"))
    elif args[0] == "draw":
        draw(args[1], args[2])
