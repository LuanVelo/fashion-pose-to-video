# Gera W3a_api.json: animacao via MiniMax H3 + Fun ControlNet Union (pose).
# Base: template oficial video_minimax_h3_fun_controlnet_union (sem o extrator SDPose, que ja e o W1).
# Uso: python -I -X utf8 build_W3a.py  -> escreve W3a_api.json na mesma pasta.
import json, os

PROMPT = (
    "A fashion e-commerce video. The model from <Picture 1> stands full body on a plain light grey studio background, "
    "wearing exactly the outfit from <Picture 1>: keep every garment and accessory identical to <Picture 1>, "
    "same colors, fabric texture, stripes, length and fit, nothing added or removed. "
    "She moves naturally following the pose guide: subtle weight shifts, relaxed arms, calm confident expression. "
    "Static camera, whole body in frame from head to feet for the entire video, soft even studio light. "
    "Photorealistic, natural motion, no text.\n\n"
    "Audio: quiet studio room tone, no music, no speech."
)

W, H, LENGTH, FPS = 480, 864, 124, 24      # teste barato: 480p 9:16, 124 frames = ~5 s (17n+5)
SEED = 20261121

g = {}
def n(i, cls, inputs, title=None):
    g[str(i)] = {"class_type": cls, "inputs": inputs}
    if title:
        g[str(i)]["_meta"] = {"title": title}

# Nome / saida
n(1, "PrimitiveString", {"value": "regata-rosa_look-02"}, "Nome do teste")
n(2, "StringConcatenate", {"string_a": "motion/W3a/", "string_b": ["1", 0], "delimiter": ""}, "Pasta base")
n(3, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/video", "delimiter": ""}, "Prefixo video")

# Modelos H3
n(10, "UNETLoader", {"unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"})
n(11, "CLIPLoader", {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"})
n(12, "VAELoader", {"vae_name": "minimax_h3_video_vae_int8_convrot.safetensors"}, "VAE video")
n(13, "VAELoader", {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}, "VAE audio")

# Turbo (LoRA 4 passos) liga/desliga
n(14, "LoraLoaderModelOnly", {"model": ["10", 0], "lora_name": "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors", "strength_model": 1.0})
n(15, "PrimitiveBoolean", {"value": True}, "Turbo 4 passos (desligar = qualidade, 20 passos)")
n(16, "ComfySwitchNode", {"switch": ["15", 0], "on_false": ["10", 0], "on_true": ["14", 0]}, "Switch modelo")
n(17, "PrimitiveInt", {"value": 20}, "Passos (completo)")
n(18, "PrimitiveInt", {"value": 4}, "Passos (turbo)")
n(19, "ComfySwitchNode", {"switch": ["15", 0], "on_false": ["17", 0], "on_true": ["18", 0]}, "Switch passos")

# Controle de pose: pose.mp4 do W1 -> 124 frames uniformes (5 s @30fps -> ~24fps)
n(20, "LoadVideo", {"file": "motion/W3a/look-02_pose.mp4"}, "Pose video (W1 pose.mp4)")
n(21, "VideoFrameSample", {"video": ["20", 0], "num_frames": LENGTH, "strategy": "uniform", "seed": 0}, "Reamostra p/ 124 frames")
n(22, "GetVideoComponents", {"video": ["21", 0]})
n(23, "ModelPatchLoader", {"name": "minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors"})
n(24, "MiniMaxH3FunControlNetApply", {"model": ["16", 0], "model_patch": ["23", 0], "vae": ["12", 0],
                                       "strength": 1.0, "start_percent": 0.0, "end_percent": 1.0,
                                       "control_video": ["22", 0]}, "ControlNet pose")

# Referencias
n(30, "LoadImage", {"image": "motion/W2/produtos/regata-rosa_frente.png"}, "Ref 1 - Produto (<Picture 1>)")
n(31, "LoadImage", {"image": "motion/W3a/regata-rosa_look-02_frame0.png"}, "Primeiro quadro - W2 pose-1 (mesma pose do frame 0)")
n(32, "PrimitiveStringMultiline", {"value": PROMPT}, "Prompt")

n(33, "MiniMaxH3ReferenceToVideo", {"clip": ["11", 0], "vae": ["12", 0], "audio_vae": ["13", 0],
                                     "ref_images.ref_image_0": ["30", 0], "prompt": ["32", 0],
                                     "width": W, "height": H, "length": LENGTH, "ref_image_size": "match"})
n(34, "MiniMaxH3AddGuide", {"positive": ["33", 0], "latent": ["33", 1], "frame_idx": 0,
                            "vae": ["12", 0], "image": ["31", 0]}, "Primeiro quadro (frame 0)")

# Amostragem (guidance 1.0 = BasicGuider, como no template)
n(40, "BasicGuider", {"model": ["24", 0], "conditioning": ["34", 0]})
n(41, "BasicScheduler", {"model": ["24", 0], "scheduler": "simple", "steps": ["19", 0], "denoise": 1.0})
n(42, "KSamplerSelect", {"sampler_name": "res_multistep"})
n(43, "RandomNoise", {"noise_seed": SEED}, "Seed (fixa p/ comparar)")
n(44, "SamplerCustomAdvanced", {"noise": ["43", 0], "guider": ["40", 0], "sampler": ["42", 0],
                                "sigmas": ["41", 0], "latent_image": ["33", 1]})

# Saida
n(50, "VAEDecode", {"samples": ["44", 0], "vae": ["12", 0]})
n(51, "VAEDecodeAudio", {"samples": ["44", 0], "vae": ["13", 0]})
n(52, "CreateVideo", {"images": ["50", 0], "audio": ["51", 0], "fps": FPS})
n(53, "SaveVideo", {"video": ["52", 0], "filename_prefix": ["3", 0], "format": "auto", "format.codec": "auto"}, "Salva video")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "W3a_api.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nos")
