# Builds W7_image-sr_v3_api.json. TEST - Kandinsky ImageSR 2.0 x2 still-image upscale, NATIVE nodes only.
# v2 -> v3: own folders instead of motion/ (image SR is not part of the motion flow):
#   output OUT/motion/sr/x2/ -> OUT/image-sr/x2/ (kandinsky_*, bicubic_*); test inputs live in IN/image-sr/.
# Same graph and values as v2 (build_W7_v2.build: bicubic x2, mirror pad to 16, t=0.15, crop back).
# Usage: python -X utf8 build_W7_v3.py  -> writes W7_image-sr_v3_api.json in this folder.
from build_W7_v2 import build, write


def build_v3(factor, t, model, image):
    g = build(factor, t, model, image, f"x{factor}")
    g["18"]["inputs"]["filename_prefix"] = f"image-sr/x{factor}/kandinsky"
    g["19"]["inputs"]["filename_prefix"] = f"image-sr/x{factor}/bicubic"
    return g


if __name__ == "__main__":
    write(build_v3(2, 0.15, "kandinsky_imagesr2_t0.15_comfy_bf16.safetensors", "fernanda_ref.png"),
          "W7_image-sr_v3_api.json")
