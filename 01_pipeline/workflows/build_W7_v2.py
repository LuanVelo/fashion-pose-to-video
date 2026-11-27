# Builds W7_image-sr_v2_api.json. TEST - Kandinsky ImageSR 2.0 x2 still-image upscale, NATIVE nodes only.
# v1 -> v2: fixes "size of tensor a (101) must match ... (102)" on images whose upscaled size is not a multiple of 16
# (the native Kandinsky 5 pads the latent to the 2x2 patch and does not crop it back). The upscaled image is now
# mirror-padded to a multiple of 16 before the VAE (like the official pipeline's replicate padding) and the result is
# cropped back to exactly factor x the input size. Also: generic output prefixes (motion/sr/x2/...).
# Same model math as v1: see build_W7_v1.py / convert_kandinsky_sr.py. build() is shared with build_W7x4_v1.py.
# Usage: python -I -X utf8 build_W7_v2.py  -> writes W7_image-sr_v2_api.json in this folder.
# Versioning: never overwrite; a new version is a new file.
import json, os


def build(factor, t, model, image, tag):
    g = {}
    def n(i, cls, inputs, title=None):
        g[str(i)] = {"class_type": cls, "inputs": inputs}
        if title:
            g[str(i)]["_meta"] = {"title": title}

    n(1, "LoadImage", {"image": image}, "Image to upscale")
    n(2, "ImageScaleBy", {"image": ["1", 0], "upscale_method": "bicubic", "scale_by": float(factor)},
      f"Bicubic x{factor} (model input - keep bicubic and {factor}.0)")
    n(20, "PadImageNode", {"image": ["2", 0], "padding_type": "pad to multiple", "padding_type.multiple": 16,
                           "padding_style": "mirror image"}, "Mirror pad to a multiple of 16 (cropped back at the end)")
    n(21, "GetImageSize", {"image": ["2", 0]}, "Upscaled size (before padding)")
    n(22, "ComfyMathExpression", {"expression": "((-a) % 16) // 2", "values.a": ["21", 0]}, "Left padding")
    n(23, "ComfyMathExpression", {"expression": "((-a) % 16) // 2", "values.a": ["21", 1]}, "Top padding")
    n(3, "UNETLoader", {"unet_name": model, "weight_dtype": "default"}, f"Kandinsky ImageSR 2.0 (converted, t={t})")
    n(4, "DualCLIPLoader", {"clip_name1": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "clip_name2": "clip_l.safetensors",
                            "type": "kandinsky5_image", "device": "default"}, "Text encoders (required by the native model; ignored)")
    n(5, "CLIPTextEncode", {"text": "", "clip": ["4", 0]}, "Empty prompt (the model has no text)")
    n(6, "ConditioningZeroOut", {"conditioning": ["5", 0]})
    n(7, "VAELoader", {"vae_name": "kandinsky_imagesr2_flux1_vae.safetensors"}, "FLUX.1 VAE (from the SR release)")
    n(8, "VAEEncode", {"pixels": ["20", 0], "vae": ["7", 0]})
    n(10, "ComfyMathExpression", {"expression": f"1 / (1 - {t}) + 0 * a", "values.a": ["21", 0]},
      f"Latent gain 1/(1-t), t={t} (a is unused)")
    n(11, "LatentMultiply", {"samples": ["8", 0], "multiplier": ["10", 0]})
    n(12, "DisableNoise", {}, "No noise (the bicubic latent is the start)")
    n(13, "BasicGuider", {"model": ["3", 0], "conditioning": ["6", 0]})
    n(14, "KSamplerSelect", {"sampler_name": "euler"})
    n(15, "ManualSigmas", {"sigmas": f"{t}, 0"}, f"One step: sigma {t} -> 0 (must match the model t)")
    n(16, "SamplerCustomAdvanced", {"noise": ["12", 0], "guider": ["13", 0], "sampler": ["14", 0], "sigmas": ["15", 0],
                                    "latent_image": ["11", 0]}, "One-step SR")
    n(17, "VAEDecode", {"samples": ["16", 0], "vae": ["7", 0]})
    n(24, "ImageCrop", {"image": ["17", 0], "width": ["21", 0], "height": ["21", 1], "x": ["22", 1], "y": ["23", 1]},
      f"Crop back to x{factor} of the input")
    n(18, "SaveImage", {"images": ["24", 0], "filename_prefix": f"motion/sr/{tag}/kandinsky"}, f"Save Kandinsky x{factor}")
    n(19, "SaveImage", {"images": ["2", 0], "filename_prefix": f"motion/sr/{tag}/bicubic"}, f"Save bicubic x{factor} (baseline)")
    return g


def write(g, name):
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    if os.path.exists(out):
        raise SystemExit(f"ALREADY EXISTS: {out} - create a new version, never overwrite.")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(g, f, indent=1, ensure_ascii=False)
    print("ok", out, len(g), "nodes")


if __name__ == "__main__":
    write(build(2, 0.15, "kandinsky_imagesr2_t0.15_comfy_bf16.safetensors", "fernanda_ref.png", "x2"),
          "W7_image-sr_v2_api.json")
