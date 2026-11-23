# Builds W5_quality_v18_api.json. SPEED TEST (not production) - W5 v17 with a DISTILLED first-frame model.
# v18 = W5 v17 (v16 + sparse attention on the video model, CHANGELOG #52/#53) with ONE change, in stage 1 only:
#   FLUX.2 klein 9B base (28 steps, CFG 3.5)  ->  FLUX.2 klein 9B KV distilled (flux-2-klein-9b-kv-fp8, 4 steps, CFG 1),
#   following the official template image_flux2_klein_9b_kv_image_edit: node 131 FluxKVCache (reference tokens
#   are computed once and cached, instead of on every step), CFGGuider cfg 1.0 (the negative branch is skipped),
#   Flux2Scheduler 4 steps, euler. INT8 attention (node 130) kept before the KV cache. VAE flux2-vae (full decoder), product
#   reference 4 MP and skeleton 1 MP unchanged. Same prompts, same seed.
#   Goal: stage 1 ~3.1 min -> well under 1 min. Risk: the distilled model may copy the garment less faithfully.
#   Output: OUT/motion/W5_v18/<name>/ (test folder, not production).
#   Stage 2 unchanged from v17: MiniMax H3 ref2va + turbo 8 steps + Fun ControlNet 0.6/0.5 + INT8 + sparse -> 896x1600, 124 frames.
# Usage: python -I -X utf8 build_W5_v18.py  -> writes W5_quality_v18_api.json in this folder.
# Versioning: never overwrite; a new version is a new file (_v19...).
import json, os

VERSION = "v18"
W, H = 896, 1600          # VIDEO (stage 2): 9:16, multiple of 32 (H3 requirement); ~1.4 MP.
IW, IH = 1088, 1920       # FIRST FRAME (stage 1): ~2.1 MP, 9:16, multiple of 16 (FLUX.2 requirement). v11 was 1536x2720 (~4.2 MP).
LENGTH, FPS = 124, 24
SEED = 20261121

PROMPT_IMG = (
    "Image 1 shows a fashion model wearing the product outfit. "
    "Image 2 is a pose skeleton (a colored stick figure on a black background): use it only as the target body pose. "
    "Create a new full-body fashion photograph of the same model from image 1, wearing exactly the same outfit from image 1, "
    "standing in exactly the pose shown by the skeleton in image 2: same position of head, shoulders, arms, hands, legs and feet, "
    "whole body visible from head to feet. "
    "The clothing must be copied only from image 1: keep every garment and accessory identical to image 1, "
    "with the same colors, fabric, texture, print, stripes, logos, trims, length and fit. Do not invent or replace any clothing. "
    "Keep the same face, hair, background, lighting and camera as image 1. "
    "Photorealistic photo. Do not draw any skeleton lines or colored dots."
)
PROMPT_VID = (
    "A fashion e-commerce video. The model from <Picture 1> stands full body on a plain light grey studio background, "
    "wearing exactly the outfit from <Picture 1>: keep every garment and accessory identical to <Picture 1>, "
    "same colors, fabric texture, stripes, length and fit, nothing added or removed. "
    "She moves naturally following the pose guide: subtle weight shifts, relaxed arms, calm confident expression. "
    "Static camera, whole body in frame from head to feet for the entire video, soft even studio light. "
    "Photorealistic, natural motion, no text.\n\n"
    "Audio: quiet studio room tone, no music, no speech."
)

g = {}
def n(i, cls, inputs, title=None):
    g[str(i)] = {"class_type": cls, "inputs": inputs}
    if title:
        g[str(i)]["_meta"] = {"title": title}

# ---------- Common ----------
n(1, "PrimitiveString", {"value": "caramel-tank-jeans_look-02"}, "Video name (<product>_<pose>)")
n(2, "StringConcatenate", {"string_a": "motion/W5_v18/", "string_b": ["1", 0], "delimiter": ""}, "Base folder (test v18)")
n(3, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/frame0", "delimiter": ""}, "First frame prefix")
n(4, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/video", "delimiter": ""}, "Video prefix")
n(5, "LoadImage", {"image": "motion/products/caramel-tank-jeans_front.png"}, "Product (front, full body) - used in both stages")

# ---------- Stage 1: first frame (FLUX.2 klein 9B base) ----------
n(100, "UNETLoader", {"unet_name": "flux-2-klein-9b-kv-fp8.safetensors", "weight_dtype": "default"}, "Image model: klein 9B KV distilled (v17: base)")
n(101, "CLIPLoader", {"clip_name": "qwen_3_8b_fp8mixed.safetensors", "type": "flux2", "device": "default"})
n(102, "VAELoader", {"vae_name": "flux2-vae.safetensors"}, "VAE flux2 (full decoder)")
n(103, "PrimitiveString", {"value": ""}, "Garment description (optional, English; leave empty)")
n(104, "StringConcatenate", {"string_a": PROMPT_IMG, "string_b": ["103", 0], "delimiter": "\n\nOutfit details, exactly as in image 1: "}, "Image prompt")
n(105, "CLIPTextEncode", {"clip": ["101", 0], "text": ["104", 0]}, "Prompt (positive)")
n(106, "CLIPTextEncode", {"clip": ["101", 0], "text": ""}, "Negative (empty)")
n(107, "ImageScaleToTotalPixels", {"image": ["5", 0], "upscale_method": "lanczos", "megapixels": 4.0, "resolution_steps": 1}, "Product 4 MP")
n(108, "VAEEncode", {"pixels": ["107", 0], "vae": ["102", 0]})
n(110, "ImageScaleToTotalPixels", {"image": ["240", 0], "upscale_method": "lanczos", "megapixels": 1.0, "resolution_steps": 1}, "Skeleton of frame 0, 1 MP")
n(111, "VAEEncode", {"pixels": ["110", 0], "vae": ["102", 0]})
n(112, "ReferenceLatent", {"conditioning": ["105", 0], "latent": ["108", 0]})
n(113, "ReferenceLatent", {"conditioning": ["112", 0], "latent": ["111", 0]})
n(114, "ReferenceLatent", {"conditioning": ["106", 0], "latent": ["108", 0]})
n(115, "ReferenceLatent", {"conditioning": ["114", 0], "latent": ["111", 0]})
n(130, "ModelAttentionBackend", {"model": ["100", 0], "attention": "comfy kitchen attention"}, "Attention (image): INT8 comfy kitchen")
n(131, "FluxKVCache", {"model": ["130", 0]}, "KV cache for the reference images")
n(116, "CFGGuider", {"model": ["131", 0], "positive": ["113", 0], "negative": ["115", 0], "cfg": 1.0}, "CFG 1 (distilled; v17: 3.5)")
n(117, "KSamplerSelect", {"sampler_name": "euler"})
n(118, "Flux2Scheduler", {"steps": 4, "width": IW, "height": IH}, "Image steps (4, distilled; v17: 28)")
n(119, "EmptyFlux2LatentImage", {"width": IW, "height": IH, "batch_size": 1}, "Frame size (1088x1920)")
n(120, "RandomNoise", {"noise_seed": SEED}, "Image seed")
n(121, "SamplerCustomAdvanced", {"noise": ["120", 0], "guider": ["116", 0], "sampler": ["117", 0], "sigmas": ["118", 0], "latent_image": ["119", 0]})
n(122, "VAEDecode", {"samples": ["121", 0], "vae": ["102", 0]})
n(123, "SaveImage", {"images": ["122", 0], "filename_prefix": ["3", 0]}, "Save first frame (STAGE 1)")

# ---------- Stage 2: video (MiniMax H3 + Fun ControlNet) ----------
n(200, "UNETLoader", {"unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"})
n(201, "CLIPLoader", {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"})
n(202, "VAELoader", {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}, "Video VAE (full fp16)")
n(203, "VAELoader", {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}, "VAE audio")
n(204, "LoraLoaderModelOnly", {"model": ["200", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}, "Turbo LoRA (8-step, official)")
n(205, "PrimitiveBoolean", {"value": True}, "Turbo 8 steps (ON = fast; OFF = v11 quality, 20 steps)")
n(206, "ComfySwitchNode", {"switch": ["205", 0], "on_false": ["200", 0], "on_true": ["204", 0]}, "Model switch")
n(207, "PrimitiveInt", {"value": 20}, "Steps (full)")
n(208, "PrimitiveInt", {"value": 8}, "Steps (turbo)")
n(209, "ComfySwitchNode", {"switch": ["205", 0], "on_false": ["207", 0], "on_true": ["208", 0]}, "Steps switch")
# Pose comes ready from the catalog (W1). It already has 124 frames; VideoFrameSample only enforces 124 if it does not.
n(210, "LoadVideo", {"file": "motion/poses/look-02/pose.mp4"}, "Catalog POSE (motion/poses/<pose>/pose.mp4)")
n(211, "VideoFrameSample", {"video": ["210", 0], "num_frames": LENGTH, "strategy": "uniform", "seed": 0}, "Ensure 124 frames")
n(212, "GetVideoComponents", {"video": ["211", 0]})
n(240, "ImageFromBatch", {"image": ["212", 0], "batch_index": 0, "length": 1}, "Skeleton frame 0 (pose for the first frame)")
n(213, "ModelPatchLoader", {"name": "minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors"})
n(230, "ModelAttentionBackend", {"model": ["206", 0], "attention": "comfy kitchen attention"}, "Attention: INT8 comfy kitchen (like SageAttention)")
n(231, "BlockSparseAttention", {"model": ["230", 0], "selection": "sol-attn", "selection.tau": 1.3,
                                "start_percent": 0.2, "end_percent": 1.0, "dense_blocks": "", "min_tokens": 12288,
                                "extra_tokens": 256, "sink_conditioning": "exact_kv_and_rows", "verbose": True},
  "Sparse attention: sol-attn tau 1.3")
n(214, "MiniMaxH3FunControlNetApply", {"model": ["231", 0], "model_patch": ["213", 0], "vae": ["202", 0],
                                        "strength": 0.6, "start_percent": 0.0, "end_percent": 0.5,
                                        "control_video": ["212", 0]}, "ControlNet pose - strength 0.6, end 0.5")
n(215, "PrimitiveStringMultiline", {"value": PROMPT_VID}, "Video prompt")
n(216, "MiniMaxH3ReferenceToVideo", {"clip": ["201", 0], "vae": ["202", 0], "audio_vae": ["203", 0],
                                      "ref_images.ref_image_0": ["5", 0], "prompt": ["215", 0],
                                      "width": W, "height": H, "length": LENGTH, "ref_image_size": "max"})
n(217, "MiniMaxH3AddGuide", {"positive": ["216", 0], "latent": ["216", 1], "frame_idx": 0,
                             "vae": ["202", 0], "image": ["122", 0]}, "First frame = STAGE 1 output")
n(218, "BasicGuider", {"model": ["214", 0], "conditioning": ["217", 0]})
n(219, "BasicScheduler", {"model": ["214", 0], "scheduler": "simple", "steps": ["209", 0], "denoise": 1.0})
n(220, "KSamplerSelect", {"sampler_name": "res_multistep"})
n(221, "RandomNoise", {"noise_seed": SEED}, "Video seed")
n(222, "SamplerCustomAdvanced", {"noise": ["221", 0], "guider": ["218", 0], "sampler": ["220", 0],
                                 "sigmas": ["219", 0], "latent_image": ["216", 1]})
n(223, "VAEDecode", {"samples": ["222", 0], "vae": ["202", 0]})
n(224, "VAEDecodeAudio", {"samples": ["222", 0], "vae": ["203", 0]})
n(225, "CreateVideo", {"images": ["223", 0], "audio": ["224", 0], "fps": FPS})
n(226, "SaveVideo", {"video": ["225", 0], "filename_prefix": ["4", 0], "format": "auto", "format.codec": "auto"}, "Save video (STAGE 2)")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"W5_quality_{VERSION}_api.json")
if os.path.exists(out):
    raise SystemExit(f"ALREADY EXISTS: {out} - create a new version (change VERSION), never overwrite.")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nodes")
