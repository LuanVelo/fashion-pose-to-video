# Builds W7_image-sr-x4_v2_api.json. TEST - Kandinsky ImageSR 2.0 x4, NATIVE nodes only.
# v1 -> v2: own folders instead of motion/: output OUT/motion/sr/x4/ -> OUT/image-sr/x4/; default input
# IN/motion/sr/caramel-tank-jeans_front_480x680.png -> IN/image-sr/caramel-tank-jeans_front_480x680.png (moved).
# Same graph and values as x4 v1 (t=0.244). Keep the input <= ~600 px (whole image in one pass).
# Usage: python -X utf8 build_W7x4_v2.py  -> writes W7_image-sr-x4_v2_api.json in this folder.
from build_W7_v2 import write
from build_W7_v3 import build_v3

write(build_v3(4, 0.244, "kandinsky_imagesr2_t0.244_comfy_bf16.safetensors",
               "image-sr/caramel-tank-jeans_front_480x680.png"), "W7_image-sr-x4_v2_api.json")
