"""Align a pose skeleton video to the person in a product photo (plan H-a, EXP-002).

Problem it fixes: W5 stage 1 keeps the framing of the product photo (person ~2-97% of the height), while the
catalog skeletons are smaller and lower. The skeleton's face points then fall on the person's neck (a second face is
painted there) and the limbs do not sit on the body.

What it does: one similarity transform (uniform scale + shift) for the whole video, computed on frame 0:
  - skeleton feet (lowest drawn point)  -> person's feet in the product photo
  - skeleton head (highest drawn point, ~eye/ear level) -> person's eye line (top of the person + EYE_LINE x height)
  - skeleton center x (median of drawn pixels) -> person's center x
The person is found against the plain studio background (median of the image border).
The product photo is mapped to the 9:16 frame like W5 does: it fills the height and is centered.

Usage (ComfyUI's Python):
  python -I -X utf8 align_skeleton.py <pose.mp4> <product image> <out pose.mp4> [<out overlay.jpg>]
Prints the transform and how many frames touch the frame edge after the transform.
"""
import sys
from fractions import Fraction
import av, numpy as np
from PIL import Image

EYE_LINE = 0.055      # eye/ear line below the top of the hair, as a share of the person's height
FEET_MARGIN = 0.005   # skeleton foot points sit just above the bottom of the shoes


def person_box(rgb):
    a = np.asarray(rgb, dtype=np.int16)
    border = np.concatenate([a[:8].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    m = np.abs(a - np.median(border, 0)).sum(2) > 60
    rows = np.where(m.sum(1) > 3)[0]
    H, W = m.shape
    return rows.min() / H, rows.max() / H, float(np.median(np.where(m)[1])) / W


def skel_box(a):
    m = a.max(2) > 40
    rows = np.where(m.any(1))[0]
    H, W = m.shape
    return rows.min() / H, rows.max() / H, float(np.median(np.where(m)[1])) / W


def main(src, product, dst, overlay=None):
    c = av.open(src)
    s = c.streams.video[0]
    rate = s.average_rate
    frames = [f.to_ndarray(format="rgb24") for f in c.decode(s)]
    c.close()
    H, W = frames[0].shape[:2]

    prod = Image.open(product).convert("RGB")
    ptop, pbot, pcx = person_box(prod)
    # map the product center x into the 9:16 frame (photo fills the height, centered)
    pw = prod.width * H / prod.height
    pcx_frame = (pcx * pw - (pw - W) / 2) / W

    stop, sbot, scx = skel_box(frames[0])
    t_top = ptop + EYE_LINE * (pbot - ptop)
    t_bot = pbot - FEET_MARGIN
    k = (t_bot - t_top) / (sbot - stop)
    # The whole video must stay inside the frame (a body cut by the frame breaks W5): cap the scale with the
    # union of all frames, keep the head on the target eye line, then shift only as much as needed to fit.
    ys, xs = [], []
    for a in frames:
        m = a.max(2) > 40
        if m.any():
            r, cc = np.where(m.any(1))[0], np.where(m.any(0))[0]
            ys += [r.min(), r.max()]
            xs += [cc.min(), cc.max()]
    uy0, uy1, ux0, ux1 = min(ys), max(ys), min(xs), max(xs)
    M = 0.01 * H
    k_fit = min((H - 2 * M) / (uy1 - uy0 + 1), (W - 2 * M) / (ux1 - ux0 + 1))
    capped = k > k_fit
    k = min(k, k_fit)
    dy = t_top * H - stop * H * k                      # head on the eye line
    dy = min(max(dy, M - uy0 * k), H - M - uy1 * k)    # ...unless that pushes a frame out
    dx = pcx_frame * W - scx * W * k
    dx = min(max(dx, M - ux0 * k), W - M - ux1 * k)

    out = av.open(dst, "w")
    v = out.add_stream("libx264", rate=rate)
    v.width, v.height, v.pix_fmt, v.options = W, H, "yuv420p", {"crf": "10"}
    edge = 0
    first = None
    for i, a in enumerate(frames):
        im = Image.fromarray(a).resize((round(W * k), round(H * k)), Image.LANCZOS)
        canvas = Image.new("RGB", (W, H))
        canvas.paste(im, (round(dx), round(dy)))
        b = np.asarray(canvas)
        m = b.max(2) > 40
        if m[:3].any() or m[-3:].any() or m[:, :3].any() or m[:, -3:].any():
            edge += 1
        if i == 0:
            first = canvas
        f = av.VideoFrame.from_ndarray(np.ascontiguousarray(b), format="rgb24")
        f.pts, f.time_base = i, Fraction(1) / rate
        for pk in v.encode(f):
            out.mux(pk)
    for pk in v.encode():
        out.mux(pk)
    out.close()

    if overlay:
        # product mapped to the 9:16 frame, with the aligned frame-0 skeleton on top
        p = prod.resize((round(pw), H), Image.LANCZOS)
        bg = Image.new("RGB", (W, H), (255, 255, 255))
        bg.paste(p, (round((W - pw) / 2), 0))
        sk = np.asarray(first)
        mask = Image.fromarray(((sk.max(2) > 40) * 255).astype(np.uint8))
        bg.paste(first, (0, 0), mask)
        bg.save(overlay, quality=90)
    new_top = (stop * H * k + dy) / H
    new_bot = (sbot * H * k + dy) / H
    print(f"scale {k:.3f}{' (capped to fit the whole video)' if capped else ''}, shift x {dx:+.0f} px, y {dy:+.0f} px; "
          f"person {ptop:.3f}-{pbot:.3f} (cx {pcx_frame:.3f}); skeleton frame 0 {stop:.3f}-{sbot:.3f} -> {new_top:.3f}-{new_bot:.3f} "
          f"(target {t_top:.3f}-{t_bot:.3f}); frames touching the edge: {edge}/{len(frames)}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
