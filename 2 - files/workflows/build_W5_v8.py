# Gera W5_qualidade_v8_api.json. v8 = v7 com o ESQUELETO DO CONTROLNET SEM CABECA (draw_head=False): os pontos de
# olhos/nariz/orelhas do original nao encaixavam no rosto gerado (cabeca do esqueleto acima do rosto) e puxavam os olhos
# para o lugar errado. Corpo, maos e pes iguais. Produto padrao = regata caramelo + jeans (teste #26).
# (historico v7) # Gera W5_qualidade_v7_api.json. v7 = v6 com o VIDEO em 896x1600 (~1,4 MP): meio-termo entre v5 (704x1248, roupa fiel,
# rosto ruim) e v6 (1088x1920, rosto bom, roupa trocada, 59 min). Unica mudanca vs v6.
# (historico v6) VIDEO em 1088x1920 (era 704x1248) - rosto com ~2,4x mais pixels.
# Unica mudanca vs v5. Fallback se faltar VRAM: 896x1600 (v7).
# (historico v5) ESQUELETO SEM ROSTO (draw_face=False, draw_head=True), extraido do
# video original dentro da Etapa 2 e salvo como registro. Unica mudanca de controle vs v4.
# (historico v4) ETAPA 2 (video) ligada e o VAE de video do H3 em fp16 (completo)
# no lugar do int8_convrot (quantizado). Video continua 704x1248 para comparar com o video da v1.
# (historico v3) v2 trocando SO o VAE do FLUX.2: flux2-vae (decoder completo) no lugar de full_encoder_small_decoder.
# (historico v2) PRIMEIRO QUADRO na melhor qualidade possivel (Etapa 1).
# Mudancas vs v1: quadro 1536x2720 (era 704x1248), produto 4 MP (era 2), esqueleto 1 MP (era 0.9).
# Etapa 2 (video) igual a v1: 704x1248 - o quadro e reduzido pelo H3 no AddGuide.
# Gera W5 (historico v1): teste de QUALIDADE em um workflow so, em 2 etapas.
#   Etapa 1 (W2 em alta): produto + esqueleto da pose do frame 0 -> FLUX.2 klein 9B base -> primeiro quadro 704x1248.
#   Etapa 2 (W3a em alta): H3 ref2va + Fun ControlNet pose, primeiro quadro da etapa 1, 704x1248, 20 passos, ref "max".
# Uso: python -I -X utf8 build_W5.py  -> escreve W5_qualidade_v1_api.json na mesma pasta.
# Versionamento: nunca sobrescrever; nova versao = novo arquivo (_v2, _v3...).
import json, os

VERSAO = "v8"
W, H = 896, 1600          # VIDEO (Etapa 2): 9:16, multiplo de 32 (exigencia do H3); ~1.4 MP (v1-v5: 704x1248; v6: 1088x1920).
IW, IH = 1536, 2720       # QUADRO (Etapa 1): ~4.2 MP, 9:16 (~0.565), multiplo de 16 (exigencia do FLUX.2). Teto pratico do klein (~4 MP).
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

# ---------- Comum ----------
n(1, "PrimitiveString", {"value": "regata-caramelo-jeans_look-02_q8"}, "Nome do teste")
n(2, "StringConcatenate", {"string_a": f"motion/W5_{VERSAO}/", "string_b": ["1", 0], "delimiter": ""}, "Pasta base")
n(3, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/frame0", "delimiter": ""}, "Prefixo primeiro quadro")
n(4, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/video", "delimiter": ""}, "Prefixo video")
n(5, "LoadImage", {"image": "motion/W2/produtos/regata-caramelo-jeans_frente.png"}, "Produto (frente, corpo inteiro) - usado nas 2 etapas")

# ---------- Etapa 1: primeiro quadro (FLUX.2 klein 9B base) ----------
n(100, "UNETLoader", {"unet_name": "flux-2-klein-base-9b-fp8.safetensors", "weight_dtype": "default"})
n(101, "CLIPLoader", {"clip_name": "qwen_3_8b_fp8mixed.safetensors", "type": "flux2", "device": "default"})
n(102, "VAELoader", {"vae_name": "flux2-vae.safetensors"}, "VAE flux2 (decoder completo)")
n(103, "PrimitiveString", {"value": ""}, "Descricao da peca (opcional, ingles, igual ao produto)")
n(104, "StringConcatenate", {"string_a": PROMPT_IMG, "string_b": ["103", 0], "delimiter": "\n\nOutfit details, exactly as in image 1: "}, "Prompt imagem")
n(105, "CLIPTextEncode", {"clip": ["101", 0], "text": ["104", 0]}, "Prompt (positivo)")
n(106, "CLIPTextEncode", {"clip": ["101", 0], "text": ""}, "Negativo (vazio)")
n(107, "ImageScaleToTotalPixels", {"image": ["5", 0], "upscale_method": "lanczos", "megapixels": 4.0, "resolution_steps": 1}, "Produto 4 MP")
n(108, "VAEEncode", {"pixels": ["107", 0], "vae": ["102", 0]})
n(109, "LoadImage", {"image": "motion/W2/look-02/pose-1.png"}, "Esqueleto do frame 0 (keyframe pose 1 do W1)")
n(110, "ImageScaleToTotalPixels", {"image": ["109", 0], "upscale_method": "lanczos", "megapixels": 1.0, "resolution_steps": 1}, "Esqueleto 1 MP")
n(111, "VAEEncode", {"pixels": ["110", 0], "vae": ["102", 0]})
n(112, "ReferenceLatent", {"conditioning": ["105", 0], "latent": ["108", 0]})
n(113, "ReferenceLatent", {"conditioning": ["112", 0], "latent": ["111", 0]})
n(114, "ReferenceLatent", {"conditioning": ["106", 0], "latent": ["108", 0]})
n(115, "ReferenceLatent", {"conditioning": ["114", 0], "latent": ["111", 0]})
n(116, "CFGGuider", {"model": ["100", 0], "positive": ["113", 0], "negative": ["115", 0], "cfg": 3.5})
n(117, "KSamplerSelect", {"sampler_name": "euler"})
n(118, "Flux2Scheduler", {"steps": 28, "width": IW, "height": IH}, "Passos imagem (28)")
n(119, "EmptyFlux2LatentImage", {"width": IW, "height": IH, "batch_size": 1}, "Tamanho do quadro (1536x2720)")
n(120, "RandomNoise", {"noise_seed": SEED}, "Seed imagem")
n(121, "SamplerCustomAdvanced", {"noise": ["120", 0], "guider": ["116", 0], "sampler": ["117", 0], "sigmas": ["118", 0], "latent_image": ["119", 0]})
n(122, "VAEDecode", {"samples": ["121", 0], "vae": ["102", 0]})
n(123, "SaveImage", {"images": ["122", 0], "filename_prefix": ["3", 0]}, "Salva primeiro quadro (ETAPA 1)")

# ---------- Etapa 2: video (MiniMax H3 + Fun ControlNet) ----------
n(200, "UNETLoader", {"unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"})
n(201, "CLIPLoader", {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"})
n(202, "VAELoader", {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}, "VAE video (fp16 completo)")
n(203, "VAELoader", {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}, "VAE audio")
n(204, "LoraLoaderModelOnly", {"model": ["200", 0], "lora_name": "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors", "strength_model": 1.0})
n(205, "PrimitiveBoolean", {"value": False}, "Turbo 4 passos (DESLIGADO = qualidade, 20 passos)")
n(206, "ComfySwitchNode", {"switch": ["205", 0], "on_false": ["200", 0], "on_true": ["204", 0]}, "Switch modelo")
n(207, "PrimitiveInt", {"value": 20}, "Passos (completo)")
n(208, "PrimitiveInt", {"value": 4}, "Passos (turbo)")
n(209, "ComfySwitchNode", {"switch": ["205", 0], "on_false": ["207", 0], "on_true": ["208", 0]}, "Switch passos")
# v5: o esqueleto e extraido aqui do VIDEO ORIGINAL, SEM os pontos de rosto (draw_face=False).
#     draw_head=True mantem nariz/olhos/orelhas -> posicao e rotacao da cabeca continuam controladas.
#     Mesmos parametros do W1 (1024 + grid 32, limiar 0.5, traco 4). Roda 1x e fica em cache.
n(210, "LoadVideo", {"file": "fashion-lookbook-look-02-video.mp4"}, "Video de movimento ORIGINAL (look-02)")
n(211, "VideoFrameSample", {"video": ["210", 0], "num_frames": LENGTH, "strategy": "uniform", "seed": 0}, "Reamostra p/ 124 frames")
n(212, "GetVideoComponents", {"video": ["211", 0]})
n(230, "CheckpointLoaderSimple", {"ckpt_name": "sdpose_wholebody_fp16.safetensors"})
n(231, "ResizeImageMaskNode", {"input": ["212", 0], "resize_type": "scale longer dimension", "resize_type.longer_size": 1024, "scale_method": "lanczos"})
n(232, "ResizeImageMaskNode", {"input": ["231", 0], "resize_type": "scale to multiple", "resize_type.multiple": 32, "scale_method": "area"}, "Grid de 32 px")
n(233, "SDPoseKeypointExtractor", {"model": ["230", 0], "vae": ["230", 2], "image": ["232", 0], "batch_size": 16})
n(234, "SDPoseDrawKeypoints", {"keypoints": ["233", 0], "draw_body": True, "draw_hands": True, "draw_face": False,
                                "draw_feet": True, "stick_width": 4, "face_point_size": 2, "score_threshold": 0.5,
                                "draw_head": False}, "Esqueleto SEM rosto e SEM cabeca (v8)")
n(235, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/pose_sem-cabeca", "delimiter": ""}, "Prefixo pose sem cabeca")
n(236, "CreateVideo", {"images": ["234", 0], "fps": FPS})
n(237, "SaveVideo", {"video": ["236", 0], "filename_prefix": ["235", 0], "format": "auto", "format.codec": "auto"}, "Salva esqueleto sem rosto (registro)")
n(213, "ModelPatchLoader", {"name": "minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors"})
n(214, "MiniMaxH3FunControlNetApply", {"model": ["206", 0], "model_patch": ["213", 0], "vae": ["202", 0],
                                        "strength": 1.0, "start_percent": 0.0, "end_percent": 1.0,
                                        "control_video": ["234", 0]}, "ControlNet pose (sem rosto)")
n(215, "PrimitiveStringMultiline", {"value": PROMPT_VID}, "Prompt video")
n(216, "MiniMaxH3ReferenceToVideo", {"clip": ["201", 0], "vae": ["202", 0], "audio_vae": ["203", 0],
                                      "ref_images.ref_image_0": ["5", 0], "prompt": ["215", 0],
                                      "width": W, "height": H, "length": LENGTH, "ref_image_size": "max"})
n(217, "MiniMaxH3AddGuide", {"positive": ["216", 0], "latent": ["216", 1], "frame_idx": 0,
                             "vae": ["202", 0], "image": ["122", 0]}, "Primeiro quadro = saida da ETAPA 1")
n(218, "BasicGuider", {"model": ["214", 0], "conditioning": ["217", 0]})
n(219, "BasicScheduler", {"model": ["214", 0], "scheduler": "simple", "steps": ["209", 0], "denoise": 1.0})
n(220, "KSamplerSelect", {"sampler_name": "res_multistep"})
n(221, "RandomNoise", {"noise_seed": SEED}, "Seed video")
n(222, "SamplerCustomAdvanced", {"noise": ["221", 0], "guider": ["218", 0], "sampler": ["220", 0],
                                 "sigmas": ["219", 0], "latent_image": ["216", 1]})
n(223, "VAEDecode", {"samples": ["222", 0], "vae": ["202", 0]})
n(224, "VAEDecodeAudio", {"samples": ["222", 0], "vae": ["203", 0]})
n(225, "CreateVideo", {"images": ["223", 0], "audio": ["224", 0], "fps": FPS})
n(226, "SaveVideo", {"video": ["225", 0], "filename_prefix": ["4", 0], "format": "auto", "format.codec": "auto"}, "Salva video (ETAPA 2)")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"W5_qualidade_{VERSAO}_api.json")
if os.path.exists(out):
    raise SystemExit(f"JA EXISTE: {out} - crie nova versao (mude VERSAO), nao sobrescreva.")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nos")
