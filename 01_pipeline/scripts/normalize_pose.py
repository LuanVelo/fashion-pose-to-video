"""Normalize the framing of a catalog pose so any product photo fits it with margins (EXP-010).

Some skeletons fill the frame (head near the top, feet near the bottom). Reframing a product photo to them puts the
hat or the feet outside the 9:16 canvas. This scales the whole pose (skeleton video, original video and keypoints)
uniformly, anchored on the floor, so that over the whole clip:
  highest eye line >= EYE_TOP x H   and   lowest ankle <= FEET x H
(the framing of look-02 / w-turn-03, which work), and centers the mid-hip of frame 0 horizontally.
Poses that already fit are left unchanged. Old files are kept as .previous-<date>.

Usage: python -I -X utf8 normalize_pose.py <pose folder> [<pose folder> ...]
"""
import sys, os, json, datetime
from fractions import Fraction
import av, numpy as np
from PIL import Image

EYE_TOP, FEET = 0.145, 0.875   # framing of look-02 and w-turn-03 (eye 0.145-0.147, ankles 0.871-0.873)
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def frames(path):
    c = av.open(path)
    s = c.streams.video[0]
    out = [f.to_image().convert("RGB") for f in c.decode(s)]
    rate = s.average_rate
    c.close()
    return out, rate


def write(path, ims, rate, crf):
    o = av.open(path, "w")
    v = o.add_stream("libx264", rate=rate)
    v.width, v.height, v.pix_fmt, v.options = ims[0].width, ims[0].height, "yuv420p", {"crf": str(crf)}
    for i, im in enumerate(ims):
        f = av.VideoFrame.from_image(im)
        f.pts, f.time_base = i, Fraction(1) / rate
        for p in v.encode(f):
            o.mux(p)
    for p in v.encode():
        o.mux(p)
    o.close()


def transform(im, k, ox, oy, fill):
    W, H = im.size
    sm = im.resize((round(W * k), round(H * k)), Image.LANCZOS)
    out = Image.new("RGB", (W, H), fill)
    out.paste(sm, (round(ox), round(oy)))
    return out


def main(d):
    kp = json.load(open(os.path.join(d, "keypoints.json")))
    W, H = kp[0]["canvas_width"], kp[0]["canvas_height"]
    eyes, ank = [], []
    for f in kp:
        if not f["people"]:
            continue
        b = np.array(f["people"][0]["pose_keypoints_2d"]).reshape(-1, 3)
        e = [b[i, 1] for i in (14, 15) if b[i, 2] >= 0.5]
        a = [b[i, 1] for i in (10, 13) if b[i, 2] >= 0.5]
        eyes += e
        ank += a
    eye_min, ank_max = min(eyes), max(ank)
    k = min(1.0, (FEET - EYE_TOP) * H / (ank_max - eye_min))
    b0 = np.array(kp[0]["people"][0]["pose_keypoints_2d"]).reshape(-1, 3)
    hip_x = (b0[8, 0] + b0[11, 0]) / 2
    oy = FEET * H - ank_max * k if k < 1 else 0.0
    ox = W / 2 - hip_x * k if k < 1 else 0.0
    if k >= 0.999:
        print(os.path.basename(d), "fits, unchanged")
        return
    sk, rate = frames(os.path.join(d, "pose.mp4"))
    write(os.path.join(d, "pose.tmp.mp4"), [transform(im, k, ox, oy, (0, 0, 0)) for im in sk], rate, 10)
    og, orate = frames(os.path.join(d, "original.mp4"))
    fill = tuple(int(x) for x in np.median(np.asarray(og[0])[:6].reshape(-1, 3), 0))
    sx = og[0].width / W
    write(os.path.join(d, "original.tmp.mp4"), [transform(im, k, ox * sx, oy * sx, fill) for im in og], orate, 16)
    for f in kp:
        for p in f["people"]:
            for key in ("pose_keypoints_2d", "foot_keypoints_2d", "face_keypoints_2d", "hand_right_keypoints_2d", "hand_left_keypoints_2d"):
                a = np.array(p.get(key) or [], dtype=np.float64).reshape(-1, 3)
                if len(a):
                    m = a[:, 0] >= 0
                    a[m, 0] = a[m, 0] * k + ox
                    a[m, 1] = a[m, 1] * k + oy
                    p[key] = [float(x) for x in a.reshape(-1)]
    for name in ("pose.mp4", "original.mp4", "keypoints.json"):
        os.replace(os.path.join(d, name), os.path.join(d, f"{name}.previous-{STAMP}"))
    os.replace(os.path.join(d, "pose.tmp.mp4"), os.path.join(d, "pose.mp4"))
    os.replace(os.path.join(d, "original.tmp.mp4"), os.path.join(d, "original.mp4"))
    json.dump(kp, open(os.path.join(d, "keypoints.json"), "w"))
    print(f"{os.path.basename(d)}: scale {k:.3f}, eye line {eye_min / H:.3f} -> {(eye_min * k + oy) / H:.3f}, "
          f"ankles {ank_max / H:.3f} -> {(ank_max * k + oy) / H:.3f}")


if __name__ == "__main__":
    for d in sys.argv[1:]:
        main(d)
