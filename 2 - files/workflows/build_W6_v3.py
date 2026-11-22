# Builds W6_upscale_v3_api.json. PRODUCTION 3/3 - upscale of the generated video.
# v3 = W6 v2 with English labels and English folders. Same graph and values: local RelayVSR x2 (native nodes, based on
# the official template utility_relayvsr_video_x2_upscale), made to run after H3.
#   Input: IN/motion/production/<name>.mp4 (copied by `catalog.py upscale <name>`)
#   -> RelayVSR 2x (1792x3200) -> saves the 2x video and a 1080x1920 copy in OUT/motion/production/<name>/.
#   Audio and fps come from the input video.
# Usage: python -I -X utf8 build_W6_v3.py  -> writes W6_upscale_v3_api.json in this folder.
# Versioning: never overwrite; a new version is a new file (_v4...).
import json, os

VERSION = "v3"
INPUT = "motion/production/caramel-tank-jeans_look-02.mp4"   # copy of OUT/motion/production/<name>/video_*.mp4 (catalog.py upscale)
NAME = "caramel-tank-jeans_look-02"
FINAL_W, FINAL_H = 1080, 1920

g = {}
def n(i, cls, inputs, title=None):
    g[str(i)] = {"class_type": cls, "inputs": inputs}
    if title:
        g[str(i)]["_meta"] = {"title": title}

n(1, "PrimitiveString", {"value": NAME}, "Video name (same as in W5, <product>_<pose>)")
n(2, "StringConcatenate", {"string_a": "motion/production/", "string_b": ["1", 0], "delimiter": ""}, "Base folder (production)")
n(3, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/video_2x", "delimiter": ""}, "2x prefix")
n(4, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/video_1080x1920", "delimiter": ""}, "1080p prefix")

n(10, "LoadVideo", {"file": INPUT}, "Video to upscale (motion/production/<name>.mp4)")
n(11, "GetVideoComponents", {"video": ["10", 0]})
n(12, "UNETLoader", {"unet_name": "relayvsr_x2_lightx2v_int8_convrot.safetensors", "weight_dtype": "default"}, "RelayVSR x2")
n(13, "VAELoader", {"vae_name": "relayvsr_flash_vae_x2_fp32.safetensors"}, "RelayVSR Flash VAE x2")
n(14, "RelayVSRConditioning", {"model": ["12", 0], "images": ["11", 0]})
n(15, "KSampler", {"model": ["12", 0], "positive": ["14", 0], "negative": ["14", 0], "latent_image": ["14", 1],
                   "seed": 42, "steps": 1, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0},
  "KSampler (1 step, cfg 1 - do not change)")
n(16, "VSRDecode", {"vae": ["13", 0], "samples": ["15", 0], "images": ["11", 0], "detail": 1.0},
  "VSR Decode (detail 1.0 = all model detail; lower = more conservative)")
n(17, "CreateVideo", {"images": ["16", 0], "audio": ["11", 1], "fps": ["11", 2]})
n(18, "SaveVideo", {"video": ["17", 0], "filename_prefix": ["3", 0], "format": "auto", "format.codec": "auto"}, "Save 2x (1792x3200)")
n(19, "ImageScale", {"image": ["16", 0], "upscale_method": "lanczos", "width": FINAL_W, "height": FINAL_H, "crop": "center"},
  "Downscale to 1080x1920")
n(20, "CreateVideo", {"images": ["19", 0], "audio": ["11", 1], "fps": ["11", 2]})
n(21, "SaveVideo", {"video": ["20", 0], "filename_prefix": ["4", 0], "format": "auto", "format.codec": "auto"}, "Save 1080x1920")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"W6_upscale_{VERSION}_api.json")
if os.path.exists(out):
    raise SystemExit(f"ALREADY EXISTS: {out} - create a new version (change VERSION), never overwrite.")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nodes")
