# Builds W1_extract-pose_v3_api.json. PRODUCTION 1/3 - pose extraction for the CATALOG.
# v3 = W1 v2 with English labels and English output folder (motion/catalog/). Same graph and values.
# Skeleton in the format the generation step uses (same as W5 v9): no 68 face points (draw_face=False),
# WITH head (draw_head=True; without the head the union ControlNet draws the skeleton lines onto the clothes - CHANGELOG #28),
# 124 frames at 24 fps. The clip is chosen in SECONDS (start + length) and converted to frames with the video's fps,
# so any source fps works. If the video ends early, the clip is cut at the end (no error).
#   Output in OUT/motion/catalog/<pose-name>/: pose_*.mp4, original_*.mp4 (same 124 frames, 24 fps, no audio),
#   keyframes/pose_* and keyframes/original_* (4 each, catalog thumbnails).
#   After running: `catalog.py pose <pose-name>` copies it to IN/motion/poses/<pose-name>/ (W5 reads it from there).
# Usage: python -I -X utf8 build_W1_v3.py  -> writes W1_extract-pose_v3_api.json in this folder.
# Versioning: never overwrite; a new version is a new file (_v4...).
import json, os

VERSION = "v3"
LENGTH, FPS = 124, 24          # same format as the W5 video (124 = 17n+5 -> 5.17 s)

g = {}
def n(i, cls, inputs, title=None):
    g[str(i)] = {"class_type": cls, "inputs": inputs}
    if title:
        g[str(i)]["_meta"] = {"title": title}

# ---------- Common ----------
n(1, "PrimitiveString", {"value": "look-02"}, "Pose name (becomes the catalog folder)")
n(2, "StringConcatenate", {"string_a": "motion/catalog/", "string_b": ["1", 0], "delimiter": ""}, "Base folder")
n(3, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/pose", "delimiter": ""}, "Pose prefix")
n(4, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/original", "delimiter": ""}, "Original prefix")
n(5, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/keyframes/pose", "delimiter": ""}, "Pose keyframes prefix")
n(6, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/keyframes/original", "delimiter": ""}, "Original keyframes prefix")

# ---------- Clip ----------
n(10, "LoadVideo", {"file": "fashion-lookbook-look-02-video.mp4"}, "Reference video")
n(11, "GetVideoComponents", {"video": ["10", 0]}, "Read video fps")
n(12, "PrimitiveFloat", {"value": 0.0}, "Clip start (seconds)")
n(13, "PrimitiveFloat", {"value": 5.2}, "Clip length (seconds; 5.2 ~ 124 frames at 24 fps)")  # the UI rounds to 0.1
n(14, "ComfyMathExpression", {"expression": "round(a * b)", "values.a": ["12", 0], "values.b": ["11", 2]}, "Start in frames")
n(15, "ComfyMathExpression", {"expression": "max(1, round(a * b))", "values.a": ["13", 0], "values.b": ["11", 2]}, "Length in frames")
n(16, "VideoTemporalCrop", {"video": ["10", 0], "start_frame": ["14", 1], "length": ["15", 1]}, "Cut the clip")
n(17, "VideoFrameSample", {"video": ["16", 0], "num_frames": LENGTH, "strategy": "uniform", "seed": 0}, "Resample to 124 frames")
n(18, "GetVideoComponents", {"video": ["17", 0]})

# ---------- Skeleton (same parameters as W5 v9) ----------
n(20, "CheckpointLoaderSimple", {"ckpt_name": "sdpose_wholebody_fp16.safetensors"})
n(21, "ResizeImageMaskNode", {"input": ["18", 0], "resize_type": "scale longer dimension", "resize_type.longer_size": 1024, "scale_method": "lanczos"})
n(22, "ResizeImageMaskNode", {"input": ["21", 0], "resize_type": "scale to multiple", "resize_type.multiple": 32, "scale_method": "area"}, "32 px grid")
n(23, "SDPoseKeypointExtractor", {"model": ["20", 0], "vae": ["20", 2], "image": ["22", 0], "batch_size": 16})
n(24, "SDPoseDrawKeypoints", {"keypoints": ["23", 0], "draw_body": True, "draw_hands": True, "draw_face": False,
                               "draw_feet": True, "stick_width": 4, "face_point_size": 2, "score_threshold": 0.5,
                               "draw_head": True}, "Skeleton without face, WITH head (never turn the head off)")

# ---------- Outputs ----------
n(30, "CreateVideo", {"images": ["24", 0], "fps": FPS})
n(31, "SaveVideo", {"video": ["30", 0], "filename_prefix": ["3", 0], "format": "auto", "format.codec": "auto"}, "Save pose.mp4")
n(32, "CreateVideo", {"images": ["18", 0], "fps": FPS})
n(33, "SaveVideo", {"video": ["32", 0], "filename_prefix": ["4", 0], "format": "auto", "format.codec": "auto"}, "Save original.mp4 (same 124 frames)")
n(40, "VideoFrameSample", {"video": ["30", 0], "num_frames": 4, "strategy": "uniform", "seed": 0})
n(41, "GetVideoComponents", {"video": ["40", 0]})
n(42, "SaveImage", {"images": ["41", 0], "filename_prefix": ["5", 0]}, "Save pose keyframes")
n(43, "VideoFrameSample", {"video": ["32", 0], "num_frames": 4, "strategy": "uniform", "seed": 0})
n(44, "GetVideoComponents", {"video": ["43", 0]})
n(45, "SaveImage", {"images": ["44", 0], "filename_prefix": ["6", 0]}, "Save original keyframes")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"W1_extract-pose_{VERSION}_api.json")
if os.path.exists(out):
    raise SystemExit(f"ALREADY EXISTS: {out} - create a new version (change VERSION), never overwrite.")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nodes")
