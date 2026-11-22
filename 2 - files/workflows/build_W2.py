# Gera W2_api.json (pose em imagem, FLUX.2 klein 9B base, multi-referencia).
# Uso: python -I -X utf8 build_W2.py   -> escreve W2_api.json na mesma pasta.
import json, os

PROMPT = (
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
# Opcional. Vazio = a roupa vem so da imagem 1. Se preencher, descreva EXATAMENTE a roupa da imagem 1
# (texto errado vence a imagem: foi o que aconteceu no teste regata-rosa com a descricao do look-02).
DESCRICAO = ""

W, H = 480, 848          # teste barato (480p, ~9:16, multiplo de 16)
STEPS, CFG, SEED = 20, 3.5, 20261121

g = {}
def n(i, cls, inputs, title=None):
    g[str(i)] = {"class_type": cls, "inputs": inputs}
    if title:
        g[str(i)]["_meta"] = {"title": title}

# Nome / pasta de saida
n(1, "PrimitiveString", {"value": "regata-rosa_look-02"}, "Nome do teste")
n(2, "StringConcatenate", {"string_a": "motion/W2/", "string_b": ["1", 0], "delimiter": ""}, "Pasta base")

# Prompt = base + descricao da peca
n(3, "PrimitiveString", {"value": DESCRICAO}, "Descricao da peca (opcional, ingles, igual a imagem 1)")
n(4, "StringConcatenate", {"string_a": PROMPT, "string_b": ["3", 0], "delimiter": "\n\nOutfit details, exactly as in image 1: "}, "Prompt completo")

# Modelos (mesmos dos workflows klein9b-base existentes)
n(10, "UNETLoader", {"unet_name": "flux-2-klein-base-9b-fp8.safetensors", "weight_dtype": "default"})
n(11, "CLIPLoader", {"clip_name": "qwen_3_8b_fp8mixed.safetensors", "type": "flux2", "device": "default"})
n(12, "VAELoader", {"vae_name": "full_encoder_small_decoder.safetensors"})

n(13, "CLIPTextEncode", {"clip": ["11", 0], "text": ["4", 0]}, "Prompt (positivo)")
n(14, "CLIPTextEncode", {"clip": ["11", 0], "text": ""}, "Negativo (vazio)")

# Produto (image 1) - 1 MP para preservar detalhe da peca
n(20, "LoadImage", {"image": "motion/W2/produtos/regata-rosa_frente.png"}, "Image 1 - Produto (frente, corpo inteiro)")
n(21, "ImageScaleToTotalPixels", {"image": ["20", 0], "upscale_method": "lanczos", "megapixels": 1.0, "resolution_steps": 1})
n(22, "VAEEncode", {"pixels": ["21", 0], "vae": ["12", 0]})
n(23, "ReferenceLatent", {"conditioning": ["13", 0], "latent": ["22", 0]})
n(24, "ReferenceLatent", {"conditioning": ["14", 0], "latent": ["22", 0]})

# Compartilhados pelos 4 ramos
n(30, "RandomNoise", {"noise_seed": SEED}, "Seed (fixa p/ comparar)")
n(31, "KSamplerSelect", {"sampler_name": "euler"})
n(32, "Flux2Scheduler", {"steps": STEPS, "width": W, "height": H})
n(33, "EmptyFlux2LatentImage", {"width": W, "height": H, "batch_size": 1}, "Tamanho de saida")

# 4 ramos, um por keyframe de pose (image 2)
for k in range(1, 5):
    b = 100 * k
    n(b + 0, "LoadImage", {"image": f"motion/W2/look-02/pose-{k}.png"}, f"Image 2 - Pose {k}")
    n(b + 1, "ImageScaleToTotalPixels", {"image": [str(b), 0], "upscale_method": "lanczos", "megapixels": 0.5, "resolution_steps": 1})
    n(b + 2, "VAEEncode", {"pixels": [str(b + 1), 0], "vae": ["12", 0]})
    n(b + 3, "ReferenceLatent", {"conditioning": ["23", 0], "latent": [str(b + 2), 0]})
    n(b + 4, "ReferenceLatent", {"conditioning": ["24", 0], "latent": [str(b + 2), 0]})
    n(b + 5, "CFGGuider", {"model": ["10", 0], "positive": [str(b + 3), 0], "negative": [str(b + 4), 0], "cfg": CFG})
    n(b + 6, "SamplerCustomAdvanced", {"noise": ["30", 0], "guider": [str(b + 5), 0], "sampler": ["31", 0],
                                       "sigmas": ["32", 0], "latent_image": ["33", 0]})
    n(b + 7, "VAEDecode", {"samples": [str(b + 6), 0], "vae": ["12", 0]})
    n(b + 8, "StringConcatenate", {"string_a": ["2", 0], "string_b": f"/pose-{k}", "delimiter": ""}, f"Prefixo pose {k}")
    n(b + 9, "SaveImage", {"images": [str(b + 7), 0], "filename_prefix": [str(b + 8), 0]}, f"Salva pose {k}")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "W2_api.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nos")
