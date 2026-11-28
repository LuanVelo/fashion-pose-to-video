"""Frame-0 candidates and automatic selection (EXP-007). Part of generation, not of the approval (approval stays human).

stage1 <name> <product rel IN> <pose rel IN> <prompt-file|-> <seed> [<seed> ...]
    Sends only W5 v20's stage 1 (the nodes SaveImage 123 needs) once per image seed, ~3-10 s each. Frames go to
    OUT/motion/<name>/s<seed>/frame0_*.png. <prompt-file>: optional stage-1 prompt text (node 104 string_a), '-' = keep.
score <skeleton keypoints.json> <frame0.png> [<frame0.png> ...]
    SDPose keypoints of each frame 0 (pose_keypoints.py, in-process) vs the skeleton's frame 0: mean distance of
    nose, shoulders, elbows, wrists, hips, knees, ankles, normalized by the skeleton body height, plus the worst
    wrist / elbow. Prints a ranking (lower = closer to the skeleton). Free ComfyUI's VRAM before (POST /free).
"""
import sys, os, json, glob, time, urllib.request
import numpy as np

API = "http://127.0.0.1:8188"
OUT = r"D:\Comfy-Desktop\ComfyUI-Shared\output\motion"
W5 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workflows", "W5_quality_v20_api.json")
JOINTS = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
ARMS = [3, 4, 6, 7]


def stage1_graph():
    g = json.load(open(W5))
    keep, todo = set(), ["123"]
    while todo:
        k = todo.pop()
        if k in keep:
            continue
        keep.add(k)
        todo += [v[0] for v in g[k]["inputs"].values() if isinstance(v, list)]
    return {k: v for k, v in g.items() if k in keep}


def stage1(name, product, pose, prompt_file, seeds):
    ids = []
    for s in seeds:
        g = json.loads(json.dumps(stage1_graph()))
        g["1"]["inputs"]["value"] = f"{name}/s{s}"
        g["2"]["inputs"]["string_a"] = "motion/"
        g["5"]["inputs"]["image"] = product
        g["210"]["inputs"]["file"] = pose
        g["120"]["inputs"]["noise_seed"] = int(s)
        if prompt_file != "-":
            g["104"]["inputs"]["string_a"] = open(prompt_file, encoding="utf-8").read().strip()
        req = urllib.request.Request(API + "/prompt", data=json.dumps({"prompt": g, "client_id": "frame0"}).encode(),
                                     headers={"Content-Type": "application/json"})
        r = json.loads(urllib.request.urlopen(req).read())
        if r.get("node_errors"):
            print(s, r["node_errors"])
        ids.append(r["prompt_id"])
    for pid in ids:
        while pid not in json.loads(urllib.request.urlopen(f"{API}/history/{pid}").read()):
            time.sleep(1)
    print(len(ids), "frames 0 ->", os.path.join(OUT, name))


def body(path):
    f = json.load(open(path))[0]
    b = np.array(f["people"][0]["pose_keypoints_2d"]).reshape(-1, 3)
    b[:, 0] /= f["canvas_width"]
    b[:, 1] /= f["canvas_height"]
    return b


def score(skel_json, frames):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import pose_keypoints
    sk = body(skel_json)
    h = max(sk[10, 1], sk[13, 1]) - sk[0, 1]
    rows = []
    for fr in frames:
        kp = fr[:-4] + "_kp.json"
        if not os.path.exists(kp):
            pose_keypoints.extract(fr, kp, 1, "576x1024")
        b = body(kp)
        ok = [j for j in JOINTS if b[j, 2] >= 0.5 and sk[j, 2] >= 0.5]
        d = {j: float(np.linalg.norm(b[j, :2] - sk[j, :2]) / h) for j in ok}
        rows.append((float(np.mean(list(d.values()))), max(d.get(j, 1.0) for j in ARMS), len(ok), fr))
    for mean, arm, n, fr in sorted(rows):
        print(f"{mean:.3f}  worst arm joint {arm:.3f}  joints {n:2d}  {fr}")


if __name__ == "__main__":
    if sys.argv[1] == "stage1":
        stage1(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6:])
    elif sys.argv[1] == "score":
        score(sys.argv[2], sys.argv[3:])
