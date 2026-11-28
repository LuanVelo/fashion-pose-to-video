"""Per-bone pose retargeting (EXP-004): keep the motion of the source clip, use the body proportions of the target person.

Inputs are OpenPose keypoint JSON made by pose_keypoints.py (same 576x1024 canvas):
  source = the pose clip (124 frames), target = the (reframed) product photo (1 frame).
Method (Wan-Animate style, 2D):
  1. bone lengths on the target photo (longer of left/right, keypoints with score >= 0.5) and on source frame 0
     (the frame the product photo was reframed to, so the ratios hold proportions, not camera distance);
  2. ratio per bone = target / source; bones not visible on the target use the median ratio; the two segments of a
     limb share the larger ratio (foreshortening only shortens); one ratio for the head bones; clipped to [0.7, 1.4];
  3. every frame: walk the tree from the mid-hip, child = parent + source bone vector x ratio (angles and
     foreshortening kept); hands, feet and face points follow their wrist / ankle / nose, scaled by the
     forearm / shin / head ratio;
  4. shift each frame so the lowest foot point stays on the source's floor line, smoothed over 15 frames (the
     touching foot changes during turns; an unsmoothed shift makes the whole skeleton jump).
Writes the retargeted JSON, prints the ratio table and the checks (edge contact, new jumps).

Usage: python -I -X utf8 retarget_skeleton.py <source.json> <target.json> <out.json>
"""
import sys, json
import numpy as np

T = 0.5
# body (OpenPose 18): 0 nose 1 neck 2 Rsho 3 Relb 4 Rwri 5 Lsho 6 Lelb 7 Lwri 8 Rhip 9 Rkne 10 Rank 11 Lhip 12 Lkne 13 Lank 14 Reye 15 Leye 16 Rear 17 Lear
ROOT = -1  # virtual mid-hip
TREE = [  # (parent, child, bone name)
    (ROOT, 8, "hip"), (ROOT, 11, "hip"), (ROOT, 1, "torso"),
    (1, 2, "shoulder"), (1, 5, "shoulder"), (1, 0, "neck"),
    (2, 3, "upper_arm"), (5, 6, "upper_arm"), (3, 4, "forearm"), (6, 7, "forearm"),
    (8, 9, "thigh"), (11, 12, "thigh"), (9, 10, "shin"), (12, 13, "shin"),
    (0, 14, "eye"), (0, 15, "eye"), (14, 16, "ear"), (15, 17, "ear"),
]
CORE = [1, 2, 5, 8, 11]


def parse(person):
    a = lambda k, n: np.array(person.get(k) or [0] * (3 * n), dtype=np.float64).reshape(-1, 3)
    return {"body": a("pose_keypoints_2d", 18), "foot": a("foot_keypoints_2d", 6), "face": a("face_keypoints_2d", 70),
            "rh": a("hand_right_keypoints_2d", 21), "lh": a("hand_left_keypoints_2d", 21)}


def ok(p, i):
    return p["body"][i, 2] >= T and p["body"][i, 0] >= 0


def root(p):
    return (p["body"][8, :2] + p["body"][11, :2]) / 2


def pos(p, i):
    return root(p) if i == ROOT else p["body"][i, :2]


def valid(p, i):
    return (ok(p, 8) and ok(p, 11)) if i == ROOT else ok(p, i)


def lengths(p):
    L = {}
    for a, b, name in TREE:
        if valid(p, a) and valid(p, b):
            L[name] = max(L.get(name, 0), float(np.linalg.norm(pos(p, b) - pos(p, a))))
    return L


def main(src_path, tgt_path, out_path):
    src = json.load(open(src_path))
    tgt = parse(json.load(open(tgt_path))[0]["people"][0])
    S = [parse(f["people"][0]) if f["people"] else None for f in src]
    H = src[0]["canvas_height"]
    W = src[0]["canvas_width"]

    # source reference frame = frame 0 (the frame the product photo was reframed to), so the ratios hold proportions
    # only, not distance to the camera; if frame 0 misses a core joint, the nearest frame that has them all
    cand = [i for i, p in enumerate(S) if p is not None and all(ok(p, j) for j in CORE)]
    ref = min(cand)
    Ls, Lt = lengths(S[ref]), lengths(tgt)
    names = sorted({n for _, _, n in TREE})
    raw = {n: Lt[n] / Ls[n] for n in names if n in Ls and n in Lt and Ls[n] > 1}
    med = float(np.median(list(raw.values())))
    ratio = {n: raw.get(n, med) for n in names}
    # foreshortening only shortens: the two segments of a limb share the larger ratio
    for a, b in (("upper_arm", "forearm"), ("thigh", "shin")):
        ratio[a] = ratio[b] = max(ratio[a], ratio[b])
    # tiny head bones are noisy: one ratio for the head
    head = float(np.median([ratio["neck"], ratio["eye"], ratio["ear"]]))
    for n in ("neck", "eye", "ear"):
        ratio[n] = head
    ratio = {n: float(np.clip(r, 0.7, 1.4)) for n, r in ratio.items()}

    out_frames, new_frames, edge, jumps = [], [], 0, 0
    prev_new, prev_src = None, None
    for f, p in zip(src, S):
        if p is None:
            new_frames.append((f, None, None, None))
            continue
        new = {k: v.copy() for k, v in p.items()}
        npos = {ROOT: root(p)}
        for a, b, name in TREE:
            pa = npos.get(a)
            if pa is None:
                continue
            if valid(p, a) and p["body"][b, 0] >= 0:
                npos[b] = pa + (p["body"][b, :2] - pos(p, a)) * ratio[name]
            new["body"][b, :2] = npos.get(b, p["body"][b, :2])
        # rigid parts: follow their anchor, scaled
        def carry(arr, anchor_src, anchor_new, k):
            m = arr[:, 0] >= 0
            arr[m, :2] = anchor_new + (arr[m, :2] - anchor_src) * k
        carry(new["rh"], p["body"][4, :2], new["body"][4, :2], ratio["forearm"])
        carry(new["lh"], p["body"][7, :2], new["body"][7, :2], ratio["forearm"])
        carry(new["face"], p["body"][0, :2], new["body"][0, :2], ratio["neck"])
        carry(new["foot"][:3], p["body"][13, :2], new["body"][13, :2], ratio["shin"])
        carry(new["foot"][3:], p["body"][10, :2], new["body"][10, :2], ratio["shin"])
        # floor: lowest visible foot / ankle point keeps the source's y
        def lowest(q):
            ys = [q["foot"][i, 1] for i in range(6) if q["foot"][i, 2] >= T] + [q["body"][i, 1] for i in (10, 13) if q["body"][i, 2] >= T]
            return max(ys) if ys else None
        ls, ln = lowest(p), lowest(new)
        new_frames.append((f, p, new, (ls - ln) if ls is not None and ln is not None else None))

    # the foot that touches the floor changes during turns: smooth the vertical shift over time (running median,
    # 15 frames) so the skeleton does not jump when the lowest visible foot point switches
    raw_dy = np.array([d if d is not None else np.nan for *_, d in new_frames], dtype=np.float64)
    fill = np.where(np.isnan(raw_dy), np.nanmedian(raw_dy), raw_dy)
    smooth = np.array([np.median(fill[max(0, i - 7): i + 8]) for i in range(len(fill))])
    for (f, p, new, _), dy in zip(new_frames, smooth):
        if p is None:
            out_frames.append(f)
            continue
        for k in new:
            m = new[k][:, 0] >= 0
            new[k][m, 1] += dy
        # checks
        pts = np.concatenate([new[k][(new[k][:, 2] >= T) & (new[k][:, 0] >= 0), :2] for k in new])
        if len(pts) and (pts[:, 0].min() < 2 or pts[:, 1].min() < 2 or pts[:, 0].max() > W - 3 or pts[:, 1].max() > H - 3):
            edge += 1
        if prev_new is not None:
            vis = (new["body"][:, 2] >= T) & (prev_new["body"][:, 2] >= T)
            dn = np.linalg.norm(new["body"][vis, :2] - prev_new["body"][vis, :2], axis=1)
            ds = np.linalg.norm(p["body"][vis, :2] - prev_src["body"][vis, :2], axis=1)
            if len(dn) and (dn - ds).max() > 0.05 * H:
                jumps += 1
        prev_new, prev_src = new, p
        flat = lambda arr: [float(x) for x in arr.reshape(-1)]
        out_frames.append({"canvas_width": W, "canvas_height": H, "people": [{
            "pose_keypoints_2d": flat(new["body"]), "foot_keypoints_2d": flat(new["foot"]), "face_keypoints_2d": flat(new["face"]),
            "hand_right_keypoints_2d": flat(new["rh"]), "hand_left_keypoints_2d": flat(new["lh"])}]})
    json.dump(out_frames, open(out_path, "w"))
    print(f"source reference frame {ref}; ratios (target/source, clipped 0.7-1.4; median {med:.2f}):")
    print("  measured: " + ", ".join(f"{n} {raw[n]:.2f}" for n in names if n in raw))
    print("  used:     " + ", ".join(f"{n} {ratio[n]:.2f}" for n in names))
    print(f"frames touching the edge: {edge}; new joint jumps (> 5 % of the height beyond the source motion): {jumps}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
