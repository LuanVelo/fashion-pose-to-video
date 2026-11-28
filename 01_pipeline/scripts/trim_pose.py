"""Trim a catalog pose to its first N frames (EXP-011): pose.mp4, original.mp4 and keypoints.json.

Used when the end of a pose does something the flow cannot follow (e.g. a turn toward the back).
Old files are kept as .previous-<date>.

Usage: python -I -X utf8 trim_pose.py <pose folder> <frames>
"""
import sys, os, json, datetime
from fractions import Fraction
import av

STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def trim(src, dst, n, crf):
    c = av.open(src)
    s = c.streams.video[0]
    rate = s.average_rate
    o = av.open(dst, "w")
    v = o.add_stream("libx264", rate=rate)
    v.width, v.height, v.pix_fmt, v.options = s.width, s.height, "yuv420p", {"crf": str(crf)}
    for i, f in enumerate(c.decode(s)):
        if i >= n:
            break
        g = av.VideoFrame.from_image(f.to_image().convert("RGB"))
        g.pts, g.time_base = i, Fraction(1) / rate
        for p in v.encode(g):
            o.mux(p)
    for p in v.encode():
        o.mux(p)
    o.close()
    c.close()


def main(d, n):
    trim(os.path.join(d, "pose.mp4"), os.path.join(d, "pose.tmp.mp4"), n, 10)
    trim(os.path.join(d, "original.mp4"), os.path.join(d, "original.tmp.mp4"), n, 16)
    kp = json.load(open(os.path.join(d, "keypoints.json")))[:n]
    for name in ("pose.mp4", "original.mp4", "keypoints.json"):
        os.replace(os.path.join(d, name), os.path.join(d, f"{name}.previous-{STAMP}"))
    os.replace(os.path.join(d, "pose.tmp.mp4"), os.path.join(d, "pose.mp4"))
    os.replace(os.path.join(d, "original.tmp.mp4"), os.path.join(d, "original.mp4"))
    json.dump(kp, open(os.path.join(d, "keypoints.json"), "w"))
    print(os.path.basename(d), "->", n, "frames")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
