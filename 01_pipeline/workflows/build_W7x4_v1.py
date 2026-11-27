# Builds W7_image-sr-x4_v1_api.json. TEST - Kandinsky ImageSR 2.0 x4 still-image upscale, NATIVE nodes only.
# Same graph as W7 v2 (build_W7_v2.build) with factor 4 and the x4 default timestep t = 0.244 (creativity 4):
# model kandinsky_imagesr2_t0.244_comfy_bf16.safetensors (convert_kandinsky_sr.py --t 0.244), latent gain 1/(1-0.244),
# ManualSigmas "0.244, 0". x4 is for SMALL inputs (whole image in one pass, no tiling): keep the input <= ~600 px.
# Default input: the product photo reduced to 1/4 (480x680), so the x4 result can be compared with the real 1920x2720.
# Usage: python -I -X utf8 build_W7x4_v1.py  -> writes W7_image-sr-x4_v1_api.json in this folder.
from build_W7_v2 import build, write

write(build(4, 0.244, "kandinsky_imagesr2_t0.244_comfy_bf16.safetensors",
            "motion/sr/caramel-tank-jeans_front_480x680.png", "x4"), "W7_image-sr-x4_v1_api.json")
