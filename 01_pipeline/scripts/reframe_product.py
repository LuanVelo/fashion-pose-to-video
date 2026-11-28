"""Reframe a product photo to the framing of a pose skeleton (plan H-c, EXP-003). Part of the future prep step.

EXP-002 showed that every skeleton point that does not sit on the body becomes an extra object (face on the neck,
third shoe), and that enlarging the skeleton pushes the body to the frame edges. Here the skeleton stays as it is
and the product photo is brought to it: the person is scaled and placed so that
  - the person's eye line (top of the person + EYE_LINE x height) is at the skeleton's head (highest drawn point, frame 0)
  - the person's feet are at the skeleton's feet (lowest drawn point, frame 0)
  - the person's center x is at the skeleton's center x
on a 9:16 canvas filled with the photo's own background color (median of its border), with a soft blend at the seams.

Usage (ComfyUI's Python):
  python -I -X utf8 reframe_product.py <product image> <pose.mp4> <out.png> [<overlay.jpg>] [--size 1088x1920]
"""
import sys
import av, numpy as np
from PIL import Image, ImageFilter

EYE_LINE = 0.055
FEET_MARGIN = 0.005


def person_box(a):
    a = a.astype(np.int16)
    border = np.concatenate([a[:8].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    bg = np.median(border, 0)
    m = np.abs(a - bg).sum(2) > 60
    rows = np.where(m.sum(1) > 3)[0]
    return rows.min(), rows.max(), float(np.median(np.where(m)[1])), bg


def skel_box(a):
    m = a.max(2) > 40
    rows = np.where(m.any(1))[0]
    H, W = m.shape
    return rows.min() / H, rows.max() / H, float(np.median(np.where(m)[1])) / W


def main(product, pose, out, overlay=None, size="1088x1920"):
    CW, CH = map(int, size.split("x"))
    c = av.open(pose)
    sk0 = next(c.decode(video=0)).to_ndarray(format="rgb24")
    c.close()
    s_top, s_bot, s_cx = skel_box(sk0)

    img = Image.open(product).convert("RGB")
    a = np.asarray(img)
    ptop, pbot, pcx, bg = person_box(a)
    ph = pbot - ptop
    eye = ptop + EYE_LINE * ph
    feet = pbot - FEET_MARGIN * ph
    k = ((s_bot - s_top) * CH) / (feet - eye)          # source px -> canvas px
    ox = s_cx * CW - pcx * k
    oy = s_top * CH - eye * k

    small = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
    canvas = Image.new("RGB", (CW, CH), tuple(int(x) for x in bg))
    # soft seam: the pasted photo fades into the background over 24 px at its own borders
    mask = Image.new("L", small.size, 0)
    mask.paste(255, (24, 24, small.width - 24, small.height - 24))
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    # keep full opacity where the photo touches the canvas border (no fade outside the canvas)
    canvas.paste(small, (round(ox), round(oy)), mask)
    canvas.save(out)

    m_top = (eye * k + oy) / CH - EYE_LINE * ph * k / CH
    cut = (ptop * k + oy) < 0 or (pbot * k + oy) > CH
    print(f"scale {k:.3f}; person in canvas: top {(ptop * k + oy) / CH:.3f} bottom {(pbot * k + oy) / CH:.3f} "
          f"(skeleton head {s_top:.3f}, feet {s_bot:.3f}, cx {s_cx:.3f}); person cut by the canvas: {cut}")
    if overlay:
        sk = Image.fromarray(sk0).resize((CW, CH))
        msk = Image.fromarray(((np.asarray(sk).max(2) > 40) * 255).astype(np.uint8))
        ov = canvas.copy()
        ov.paste(sk, (0, 0), msk)
        ov.save(overlay, quality=90)


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--size")]
    size = next((x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--size=")), "1088x1920")
    main(*args[:4], size=size)
