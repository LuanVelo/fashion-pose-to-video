# Builds W5 v21 as TWO API workflows (TEST, not production; production stays W5 v20 until the user approves):
#   W5_frame0_v21_api.json  STAGE 1 only: product (reframed to the pose) + skeleton frame 0 -> first frame candidates.
#   W5_video_v21_api.json   STAGE 2 only: a CHOSEN first frame (LoadImage) + product + pose video -> video.
# Why split (EXP-007, 2026-11-28): the first frame decides most defects (extra hand, painted skeleton lines,
# garment changes) and costs ~3-10 s, the video ~3.5 min. Several first frames are generated, one is chosen
# (by people for now: "somos nós que checamos"), and only that one becomes a video.
# Changes vs v20 (only these):
#   - video prompt (node 215) = EXP-006 prompt: no "stripes", no "stands", pose-neutral motion sentence
#     (CHANGELOG #76; 9/12 clean, the 3 failures came from frame 0, fixed by choosing the frame 0).
#   - stage-1 prompt (node 104) += the arms/hands sentence of EXP-007 P1 (caramel w-turn-03: 4/6 good frames 0 vs 2/6).
#   - stage 2 reads the first frame from LoadImage (node 250) instead of the stage-1 decode (node 122).
#   - output folders: frame0 -> motion/frame0/<name>/, video -> motion/video/<name>/ (override per run).
# Built from W5_quality_v20_api.json (the v20 graph is the base; values unchanged otherwise).
# Usage: python -I -X utf8 build_W5_v21.py   (never overwrites)
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = "v21"
base = json.load(open(os.path.join(HERE, "W5_quality_v20_api.json"), encoding="utf-8"))

ARMS = ("Arms, hands and legs must be exactly as in image 2: if image 2 shows the arms hanging, no hand is in a pocket, "
        "behind the back or on the hip. The person has exactly two arms and two hands. ")
PROMPT_VID = base["215"]["inputs"]["value"]
PROMPT_VID = (PROMPT_VID.replace("stands full body", "is shown full body")
              .replace("same colors, fabric texture, stripes, length and fit", "same colors, fabric texture, length and fit")
              .replace("She moves naturally following the pose guide: subtle weight shifts, relaxed arms, calm confident expression.",
                       "She follows the pose guide exactly, with a calm confident expression."))
assert "stripes" not in PROMPT_VID and "follows the pose guide exactly" in PROMPT_VID


def closure(g, roots):
    keep, todo = set(), list(roots)
    while todo:
        k = todo.pop()
        if k in keep:
            continue
        keep.add(k)
        todo += [v[0] for v in g[k]["inputs"].values() if isinstance(v, list)]
    return {k: json.loads(json.dumps(g[k])) for k in sorted(keep, key=int)}


# --- stage 1
s1 = closure(base, ["123"])
s1["104"]["inputs"]["string_a"] = s1["104"]["inputs"]["string_a"].replace("Photorealistic photo.", ARMS + "Photorealistic photo.")
assert ARMS in s1["104"]["inputs"]["string_a"]
s1["2"]["inputs"]["string_a"] = "motion/frame0/"
s1["3"]["inputs"]["string_b"] = "/frame0"

# --- stage 2
g2 = json.loads(json.dumps(base))
g2["250"] = {"class_type": "LoadImage", "inputs": {"image": "motion/frame0/chosen.png"},
             "_meta": {"title": "CHOSEN first frame (from W5_frame0_v21)"}}
g2["217"]["inputs"]["image"] = ["250", 0]
g2["215"]["inputs"]["value"] = PROMPT_VID
g2["2"]["inputs"]["string_a"] = "motion/video/"
s2 = closure(g2, ["226"])

for name, g in (("W5_frame0", s1), ("W5_video", s2)):
    out = os.path.join(HERE, f"{name}_{VERSION}_api.json")
    if os.path.exists(out):
        raise SystemExit(f"ALREADY EXISTS: {out} - create a new version, never overwrite.")
    json.dump(g, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("written", out, len(g), "nodes")
