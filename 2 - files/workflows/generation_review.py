"""Review aid for one W5 generation: dense frame sheet + two automatic flags (they help the human review, they do not replace it).

Writes next to the generation's video, in OUT/motion/production/<name>/:
  review_sheet.jpg   every 8th frame (16 frames), with the frame number and both flag values on each tile
  review.json        per-frame values and the summary

Flags (computed on the person, found against the plain studio background):
  drift  = 1 - histogram intersection of the garment region (below the head) between frame 0 and frame t (0 = same colors)
  novel  = share of garment pixels whose color did not exist in frame 0 (new colors: stripes, a different garment)

Usage (ComfyUI's Python):  python -I -X utf8 generation_review.py <name> [<name> ...]
  <name> = generation folder under OUT/motion/production/ (subfolders allowed, e.g. pose-qa/caramel-tank-jeans_w-turn-03)
"""
import sys, os, glob, json
import av, numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = r"D:\Comfy-Desktop\ComfyUI-Shared\output\motion\production"
STEP, BINS = 8, 12


def garment_mask(a):
    """Person mask against the plain background (median of the frame border), without the head (top 18% of the body)."""
    border = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    bg = np.median(border, 0)
    m = np.abs(a.astype(np.int16) - bg).sum(2) > 60
    ys = np.where(m.any(1))[0]
    if len(ys) < 10:
        return m
    top, bot = ys.min(), ys.max()
    m[: top + int(0.18 * (bot - top))] = False
    return m


def hist(a, m):
    q = a[m].astype(np.int32) * BINS // 256
    idx = q[:, 0] * BINS * BINS + q[:, 1] * BINS + q[:, 2]
    h = np.bincount(idx, minlength=BINS ** 3).astype(np.float64)
    return h / max(h.sum(), 1)


def edge_share(a, m):
    """Share of strong edges inside the garment (body outline excluded): stripes and painted lines raise it."""
    from numpy.lib.stride_tricks import sliding_window_view
    g = a.astype(np.float32).mean(2)
    e = (np.abs(np.diff(g, axis=1))[:-1, :] + np.abs(np.diff(g, axis=0))[:, :-1]) > 40
    k = 7
    inner = sliding_window_view(np.pad(m[:-1, :-1], k // 2), (k, k)).all((2, 3))
    return float(e[inner].mean()) if inner.sum() > 500 else float("nan")


def review(name):
    gdir = os.path.join(OUT, name)
    vids = sorted(glob.glob(os.path.join(gdir, "video_0*.mp4")), key=os.path.getmtime)
    if not vids:
        raise SystemExit(f"no video in {gdir}")
    c = av.open(vids[-1])
    frames = [f.to_ndarray(format="rgb24") for f in c.decode(video=0)]
    c.close()
    h0 = hist(frames[0], garment_mask(frames[0]))
    known = h0 > 0.0005
    drift, novel, edge = [], [], []
    for a in frames:
        m = garment_mask(a)
        h = hist(a, m)
        drift.append(float(1 - np.minimum(h0, h).sum()))
        novel.append(float(h[~known].sum()))
        edge.append(edge_share(a, m))
    e0 = edge[0] if edge[0] and not np.isnan(edge[0]) else np.nanmean(edge)
    edge = [x / e0 if not np.isnan(x) else 0.0 for x in edge]
    bad_at = lambda i: drift[i] > DRIFT_LIMIT or novel[i] > NOVEL_LIMIT or edge[i] > EDGE_LIMIT
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    tiles = []
    for i in range(0, len(frames), STEP):
        im = Image.fromarray(frames[i])
        im = im.resize((round(im.width * 420 / im.height), 420))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, im.width, 26), fill=(170, 20, 20) if bad_at(i) else (20, 20, 20))
        d.text((6, 4), f"#{i} drift {drift[i]:.2f} new {novel[i]:.2f} edge {edge[i]:.1f}", fill=(255, 255, 255), font=font)
        tiles.append(im)
    cols = 8
    W, H = tiles[0].size
    sheet = Image.new("RGB", (W * cols, H * ((len(tiles) + cols - 1) // cols)), (0, 0, 0))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * W, (k // cols) * H))
    sheet.save(os.path.join(gdir, "review_sheet.jpg"), quality=85)
    flagged = [i for i in range(len(frames)) if bad_at(i)]
    summary = {"video": os.path.basename(vids[-1]), "frames": len(frames), "drift_max": round(max(drift), 3), "novel_max": round(max(novel), 3),
               "edge_p90": round(float(np.percentile(edge, 90)), 2), "flagged_frames": flagged,
               "limits": {"drift": DRIFT_LIMIT, "novel": NOVEL_LIMIT, "edge": EDGE_LIMIT}}
    json.dump({"summary": summary, "drift": [round(x, 4) for x in drift], "novel": [round(x, 4) for x in novel], "edge": [round(x, 3) for x in edge]},
              open(os.path.join(gdir, "review.json"), "w"), indent=1)
    flag = "FLAG" if len(flagged) >= 5 else "ok"
    print(f"{flag:<4} {name}: drift max {summary['drift_max']:.2f}, new colors max {summary['novel_max']:.2f}, edge p90 {summary['edge_p90']:.2f}, flagged frames {len(flagged)}")
    return summary


# Limits calibrated on known good vs known bad runs (CHANGELOG #69/#70); a flag means "look closely", not "fail".
# Calibration (12 runs): good runs drift <= 0.45, new <= 0.05, edge p90 <= 0.86; bad runs drift 0.75-0.90 or edge p90 1.5-2.0.
# A generation is flagged when at least 5 frames pass a limit.
DRIFT_LIMIT, NOVEL_LIMIT, EDGE_LIMIT = 0.50, 0.10, 1.25

if __name__ == "__main__":
    for n in sys.argv[1:]:
        review(n)
