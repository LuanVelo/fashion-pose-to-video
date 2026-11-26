# Builds W7_image-sr_v1_api.json. TEST - Kandinsky ImageSR 2.0 x2 still-image upscale, NATIVE nodes only.
# Model: kandinskylab/Kandinsky-ImageSR-2.0 (MIT), converted to the native ComfyUI Kandinsky 5 Image format by
# convert_kandinsky_sr.py for ONE baked timestep (t = 0.15 = x2 default, creativity 4). The text path is zeroed in the
# conversion, so the prompt is ignored (the encoders are loaded only because the native model needs a 3584-dim
# conditioning).
# One-step flow, same math as the official pipeline: bicubic x2 -> FLUX.1 VAE encode -> latent * 1/(1-t)
# (the sampler starts from (1-t)*latent with zero noise) -> 1 Euler step from sigma t to 0 -> decode.
# Difference from the official pipeline: no 1024 px tiling (whole image in one pass; native ComfyUI has no blended
# tiling), so very large images are out of the training size (1024 px tiles).
#   Input: IN/motion/sr/<name>.png      Output: OUT/motion/sr/<name>_kandinsky-x2_*.png + <name>_bicubic-x2_*.png
# Usage: python -I -X utf8 build_W7_v1.py  -> writes W7_image-sr_v1_api.json in this folder.
# Versioning: never overwrite; a new version is a new file (_v2...).
import json, os

VERSION = "v1"
T = 0.15                                   # must match the converted model file and ManualSigmas
MODEL = "kandinsky_imagesr2_t0.15_comfy_bf16.safetensors"
VAE = "kandinsky_imagesr2_flux1_vae.safetensors"      # FLUX.1-schnell AE shipped with the release (diffusers format)
NAME = "caramel-tank-jeans_look-02_frame0"
INPUT = f"motion/sr/{NAME}.png"

g = {}
def n(i, cls, inputs, title=None):
    g[str(i)] = {"class_type": cls, "inputs": inputs}
    if title:
        g[str(i)]["_meta"] = {"title": title}

n(1, "LoadImage", {"image": INPUT}, "Image to upscale (input/motion/sr/)")
n(2, "ImageScaleBy", {"image": ["1", 0], "upscale_method": "bicubic", "scale_by": 2.0},
  "Bicubic x2 (model input - keep bicubic and 2.0)")
n(3, "UNETLoader", {"unet_name": MODEL, "weight_dtype": "default"}, f"Kandinsky ImageSR 2.0 (converted, t={T})")
n(4, "DualCLIPLoader", {"clip_name1": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "clip_name2": "clip_l.safetensors",
                        "type": "kandinsky5_image", "device": "default"}, "Text encoders (required by the native model; ignored)")
n(5, "CLIPTextEncode", {"text": "", "clip": ["4", 0]}, "Empty prompt (the model has no text)")
n(6, "ConditioningZeroOut", {"conditioning": ["5", 0]})
n(7, "VAELoader", {"vae_name": VAE}, "FLUX.1 VAE (from the SR release)")
n(8, "VAEEncode", {"pixels": ["2", 0], "vae": ["7", 0]})
n(9, "GetImageSize", {"image": ["1", 0]})
n(10, "ComfyMathExpression", {"expression": f"1 / (1 - {T}) + 0 * a", "values.a": ["9", 0]},
  f"Latent gain 1/(1-t), t={T} (a is unused)")
n(11, "LatentMultiply", {"samples": ["8", 0], "multiplier": ["10", 0]})
n(12, "DisableNoise", {}, "No noise (the bicubic latent is the start)")
n(13, "BasicGuider", {"model": ["3", 0], "conditioning": ["6", 0]})
n(14, "KSamplerSelect", {"sampler_name": "euler"})
n(15, "ManualSigmas", {"sigmas": f"{T}, 0"}, f"One step: sigma {T} -> 0 (must match the model t)")
n(16, "SamplerCustomAdvanced", {"noise": ["12", 0], "guider": ["13", 0], "sampler": ["14", 0], "sigmas": ["15", 0],
                                "latent_image": ["11", 0]}, "One-step SR")
n(17, "VAEDecode", {"samples": ["16", 0], "vae": ["7", 0]})
n(18, "SaveImage", {"images": ["17", 0], "filename_prefix": f"motion/sr/{NAME}_kandinsky-x2"}, "Save Kandinsky x2")
n(19, "SaveImage", {"images": ["2", 0], "filename_prefix": f"motion/sr/{NAME}_bicubic-x2"}, "Save bicubic x2 (baseline)")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"W7_image-sr_{VERSION}_api.json")
if os.path.exists(out):
    raise SystemExit(f"ALREADY EXISTS: {out} - create a new version (change VERSION), never overwrite.")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nodes")
