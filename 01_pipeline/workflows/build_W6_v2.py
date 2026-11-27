# Gera W6_upscale_v2_api.json. PRODUCAO 3/3 - upscale do video gerado.
# v2 = v1 (RelayVSR x2, sem mudanca de qualidade) ajustada ao fluxo de producao: entrada IN/motion/producao/<nome>.mp4
# (copiada de OUT/motion/producao/<nome>/ por `catalogo.py upscale <nome>`) e saida na MESMA pasta do video gerado,
# OUT/motion/producao/<nome>/ (video_2x e video_1080x1920).
# (historico v1) Gera W6_upscale_v1_api.json: UPSCALE de video local com RelayVSR x2 (nos nativos, base no template
# utility_relayvsr_video_x2_upscale). Pensado para vir depois do H3 (o par x2 foi retreinado pela LightX2V para isso).
#   Entrada: video gerado (ex. W5 v7 896x1600) -> RelayVSR 2x (1792x3200) -> salva 2x e uma copia 1080x1920.
#   Audio e fps vem do video de entrada.
# Uso: python -I -X utf8 build_W6.py  -> escreve W6_upscale_v1_api.json na mesma pasta.
# Versionamento: nunca sobrescrever; nova versao = novo arquivo (_v2, _v3...).
import json, os

VERSAO = "v2"
ENTRADA = "motion/producao/regata-caramelo-jeans_look-02.mp4"   # copia do OUT/motion/producao/<nome>/video_*.mp4
NOME = "regata-caramelo-jeans_look-02"
FINAL_W, FINAL_H = 1080, 1920

g = {}
def n(i, cls, inputs, title=None):
    g[str(i)] = {"class_type": cls, "inputs": inputs}
    if title:
        g[str(i)]["_meta"] = {"title": title}

n(1, "PrimitiveString", {"value": NOME}, "Nome do video (igual ao do W5, <produto>_<pose>)")
n(2, "StringConcatenate", {"string_a": "motion/producao/", "string_b": ["1", 0], "delimiter": ""}, "Pasta base (producao)")
n(3, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/video_2x", "delimiter": ""}, "Prefixo 2x")
n(4, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/video_1080x1920", "delimiter": ""}, "Prefixo 1080p")

n(10, "LoadVideo", {"file": ENTRADA}, "Video a ampliar (motion/producao/<nome>.mp4)")
n(11, "GetVideoComponents", {"video": ["10", 0]})
n(12, "UNETLoader", {"unet_name": "relayvsr_x2_lightx2v_int8_convrot.safetensors", "weight_dtype": "default"}, "RelayVSR x2")
n(13, "VAELoader", {"vae_name": "relayvsr_flash_vae_x2_fp32.safetensors"}, "RelayVSR Flash VAE x2")
n(14, "RelayVSRConditioning", {"model": ["12", 0], "images": ["11", 0]})
n(15, "KSampler", {"model": ["12", 0], "positive": ["14", 0], "negative": ["14", 0], "latent_image": ["14", 1],
                   "seed": 42, "steps": 1, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0},
  "KSampler (1 passo, cfg 1 - nao mudar)")
n(16, "VSRDecode", {"vae": ["13", 0], "samples": ["15", 0], "images": ["11", 0], "detail": 1.0},
  "VSR Decode (detail 1.0 = todo detalhe do modelo; menor = mais conservador)")
n(17, "CreateVideo", {"images": ["16", 0], "audio": ["11", 1], "fps": ["11", 2]})
n(18, "SaveVideo", {"video": ["17", 0], "filename_prefix": ["3", 0], "format": "auto", "format.codec": "auto"}, "Salva 2x (1792x3200)")
n(19, "ImageScale", {"image": ["16", 0], "upscale_method": "lanczos", "width": FINAL_W, "height": FINAL_H, "crop": "center"},
  "Reduz p/ 1080x1920")
n(20, "CreateVideo", {"images": ["19", 0], "audio": ["11", 1], "fps": ["11", 2]})
n(21, "SaveVideo", {"video": ["20", 0], "filename_prefix": ["4", 0], "format": "auto", "format.codec": "auto"}, "Salva 1080x1920")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"W6_upscale_{VERSAO}_api.json")
if os.path.exists(out):
    raise SystemExit(f"JA EXISTE: {out} - crie nova versao (mude VERSAO), nao sobrescreva.")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nos")
