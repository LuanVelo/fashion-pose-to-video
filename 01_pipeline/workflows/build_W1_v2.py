# Gera W1_extrai-pose_v2_api.json. PRODUCAO 1/3 - extracao de pose para o CATALOGO.
# v2 = esqueleto no formato que a geracao usa (igual a W5 v9): sem os 68 pontos de rosto (draw_face=False),
# COM cabeca (draw_head=True; sem cabeca o ControlNet union desenha linhas na roupa - HISTORICO #28),
# 124 quadros a 24 fps. Trecho escolhido em SEGUNDOS (inicio + duracao) e convertido em frames pelo fps do video,
# entao funciona com qualquer fps de origem. Se o video acabar antes, o trecho e cortado no fim (sem erro).
#   Saida em OUT/motion/catalogo/<nome-da-pose>/: pose_*.mp4, original_*.mp4 (mesmos 124 quadros, 24 fps, sem audio),
#   keyframes/pose_* e keyframes/original_* (4 cada, miniaturas do catalogo).
#   Depois de rodar: `catalogo.py pose <nome-da-pose>` copia para IN/motion/poses/<nome-da-pose>/ (o W5 le de la).
# (historico v1) LoadVideo -> VideoTemporalCrop (frames) -> SDPose com rosto, fps nativo, sem reamostrar.
# Uso: python -I -X utf8 build_W1_v2.py  -> escreve W1_extrai-pose_v2_api.json na mesma pasta.
# Versionamento: nunca sobrescrever; nova versao = novo arquivo (_v3...).
import json, os

VERSAO = "v2"
LENGTH, FPS = 124, 24          # mesmo formato do video gerado no W5 (124 = 17n+5 -> 5,17 s)

g = {}
def n(i, cls, inputs, title=None):
    g[str(i)] = {"class_type": cls, "inputs": inputs}
    if title:
        g[str(i)]["_meta"] = {"title": title}

# ---------- Comum ----------
n(1, "PrimitiveString", {"value": "look-02"}, "Nome da pose (vira a pasta do catalogo)")
n(2, "StringConcatenate", {"string_a": "motion/catalogo/", "string_b": ["1", 0], "delimiter": ""}, "Pasta base")
n(3, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/pose", "delimiter": ""}, "Prefixo pose")
n(4, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/original", "delimiter": ""}, "Prefixo original")
n(5, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/keyframes/pose", "delimiter": ""}, "Prefixo keyframes pose")
n(6, "StringConcatenate", {"string_a": ["2", 0], "string_b": "/keyframes/original", "delimiter": ""}, "Prefixo keyframes original")

# ---------- Trecho ----------
n(10, "LoadVideo", {"file": "fashion-lookbook-look-02-video.mp4"}, "Video de referencia")
n(11, "GetVideoComponents", {"video": ["10", 0]}, "Le o fps do video")
n(12, "PrimitiveFloat", {"value": 0.0}, "Inicio do trecho (segundos)")
n(13, "PrimitiveFloat", {"value": 5.2}, "Duracao do trecho (segundos; 5.2 ~ 124 quadros a 24 fps)")  # a UI arredonda a 0,1
n(14, "ComfyMathExpression", {"expression": "round(a * b)", "values.a": ["12", 0], "values.b": ["11", 2]}, "Inicio em frames")
n(15, "ComfyMathExpression", {"expression": "max(1, round(a * b))", "values.a": ["13", 0], "values.b": ["11", 2]}, "Duracao em frames")
n(16, "VideoTemporalCrop", {"video": ["10", 0], "start_frame": ["14", 1], "length": ["15", 1]}, "Recorta o trecho")
n(17, "VideoFrameSample", {"video": ["16", 0], "num_frames": LENGTH, "strategy": "uniform", "seed": 0}, "Reamostra p/ 124 quadros")
n(18, "GetVideoComponents", {"video": ["17", 0]})

# ---------- Esqueleto (mesmos parametros da W5 v9) ----------
n(20, "CheckpointLoaderSimple", {"ckpt_name": "sdpose_wholebody_fp16.safetensors"})
n(21, "ResizeImageMaskNode", {"input": ["18", 0], "resize_type": "scale longer dimension", "resize_type.longer_size": 1024, "scale_method": "lanczos"})
n(22, "ResizeImageMaskNode", {"input": ["21", 0], "resize_type": "scale to multiple", "resize_type.multiple": 32, "scale_method": "area"}, "Grid de 32 px")
n(23, "SDPoseKeypointExtractor", {"model": ["20", 0], "vae": ["20", 2], "image": ["22", 0], "batch_size": 16})
n(24, "SDPoseDrawKeypoints", {"keypoints": ["23", 0], "draw_body": True, "draw_hands": True, "draw_face": False,
                               "draw_feet": True, "stick_width": 4, "face_point_size": 2, "score_threshold": 0.5,
                               "draw_head": True}, "Esqueleto sem rosto, COM cabeca (nao desligar a cabeca)")

# ---------- Saidas ----------
n(30, "CreateVideo", {"images": ["24", 0], "fps": FPS})
n(31, "SaveVideo", {"video": ["30", 0], "filename_prefix": ["3", 0], "format": "auto", "format.codec": "auto"}, "Salva pose.mp4")
n(32, "CreateVideo", {"images": ["18", 0], "fps": FPS})
n(33, "SaveVideo", {"video": ["32", 0], "filename_prefix": ["4", 0], "format": "auto", "format.codec": "auto"}, "Salva original.mp4 (mesmos 124 quadros)")
n(40, "VideoFrameSample", {"video": ["30", 0], "num_frames": 4, "strategy": "uniform", "seed": 0})
n(41, "GetVideoComponents", {"video": ["40", 0]})
n(42, "SaveImage", {"images": ["41", 0], "filename_prefix": ["5", 0]}, "Keyframes pose")
n(43, "VideoFrameSample", {"video": ["32", 0], "num_frames": 4, "strategy": "uniform", "seed": 0})
n(44, "GetVideoComponents", {"video": ["43", 0]})
n(45, "SaveImage", {"images": ["44", 0], "filename_prefix": ["6", 0]}, "Keyframes original")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"W1_extrai-pose_{VERSAO}_api.json")
if os.path.exists(out):
    raise SystemExit(f"JA EXISTE: {out} - crie nova versao (mude VERSAO), nao sobrescreva.")
with open(out, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
print("ok", out, len(g), "nos")
