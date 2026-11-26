# Converts the Kandinsky ImageSR 2.0 "baked" Diffusers transformer into a checkpoint that the NATIVE ComfyUI
# Kandinsky 5 Image loader (UNETLoader) understands, for ONE fixed one-step timestep t. No custom nodes.
#
# Why a conversion is needed: the release removes the text tower and the 50 cross-attention layers and stores their
# zero-text outputs as per-timestep tables (time_embed_table, xattn_bias_table). ComfyUI's native Kandinsky5 model
# still has those modules, so we rebuild them as constant functions of t:
#   - time_embeddings: weights 0, out bias = time_embed_table[t]       -> time_embed is the baked value
#   - pooled_text_embeddings: weights 0, norm 0                         -> adds 0
#   - text_embeddings / cross-attention q,k,v: weights 0                -> text is ignored (any prompt, zeroed)
#   - cross-attention out_layer: weight 0, bias = xattn_bias_table[t]; cross gate rows of visual_modulation = 1
#     -> each block adds exactly the baked bias
#   - no text transformer blocks
# Two ComfyUI-vs-pipeline differences are folded into the weights (so the workflow only needs native nodes):
#   1) latent format: ComfyUI Flux latent = (raw - s) * k, the pipeline uses raw * k (k=0.3611, s=0.1159, c=s*k)
#   2) the flow sampler starts from (1 - t) * latent (zero noise); the workflow multiplies the raw latent by 1/(1-t)
#      first (LatentMultiply), so the model sees x_pipe - (1-t)*c.
#   -> visual_embeddings.in_layer.bias += (1-t)*c * W.sum(input)      (model sees x_pipe again)
#   -> out_layer.out_layer.bias += c                                   (denoised decodes to the pipeline result)
# Usage: python -I -X utf8 convert_kandinsky_sr.py --t 0.15  (x2 default) | --t 0.244 (x4 default)
# Never overwrites: refuses if the output file exists.
import argparse, json, os
import torch
from safetensors.torch import load_file, save_file

SRC = r"D:\Comfy-Desktop\ComfyUI-Shared\models\diffusers\Kandinsky-ImageSR-2.0\transformer"
DST_DIR = r"D:\Comfy-Desktop\ComfyUI-Shared\models\diffusion_models"
K, S = 0.3611, 0.1159          # FLUX.1 VAE scaling / shift (ComfyUI latent_formats.Flux, vae/config.json)

ap = argparse.ArgumentParser()
ap.add_argument("--t", type=float, required=True)
args = ap.parse_args()
t = args.t

cfg = json.load(open(os.path.join(SRC, "config.json"), encoding="utf-8"))
baked = [float(v) for v in cfg["baked_timesteps"]]
idx = min(range(len(baked)), key=lambda i: abs(baked[i] - t))
if abs(baked[idx] - t) > 1e-6:
    raise SystemExit(f"t={t} is not baked; available: {baked}")
t_txt = ("%.4f" % t).rstrip("0").rstrip(".")
out_path = os.path.join(DST_DIR, f"kandinsky_imagesr2_t{t_txt}_comfy_bf16.safetensors")
if os.path.exists(out_path):
    raise SystemExit(f"ALREADY EXISTS: {out_path}")

sd = {}
for f in sorted(os.listdir(SRC)):
    if f.endswith(".safetensors"):
        sd.update(load_file(os.path.join(SRC, f)))
print("loaded", len(sd), "tensors")

md, td, nb = cfg["model_dim"], cfg["time_dim"], cfg["num_visual_blocks"]
DT = torch.bfloat16
f32 = lambda x: x.to(torch.float32)
out = {}
c = S * K

for k, v in sd.items():
    if k == "time_embed_table" or k.endswith("xattn_bias_table"):
        continue
    out[k] = v

# time path
out["time_embeddings.in_layer.weight"] = torch.zeros(dtype=DT, size=(td, md,))
out["time_embeddings.in_layer.bias"] = torch.zeros(dtype=DT, size=(td,))
out["time_embeddings.out_layer.weight"] = torch.zeros(dtype=DT, size=(td, td,))
out["time_embeddings.out_layer.bias"] = f32(sd["time_embed_table"][idx])
out["pooled_text_embeddings.in_layer.weight"] = torch.zeros(dtype=DT, size=(td, 768,))
out["pooled_text_embeddings.in_layer.bias"] = torch.zeros(dtype=DT, size=(td,))
out["pooled_text_embeddings.norm.weight"] = torch.zeros(dtype=DT, size=(td,))
out["pooled_text_embeddings.norm.bias"] = torch.zeros(dtype=DT, size=(td,))
# text path (ignored)
out["text_embeddings.in_layer.weight"] = torch.zeros(dtype=DT, size=(md, 3584,))
out["text_embeddings.in_layer.bias"] = torch.zeros(dtype=DT, size=(md,))
out["text_embeddings.norm.weight"] = torch.ones(dtype=DT, size=(md,))
out["text_embeddings.norm.bias"] = torch.zeros(dtype=DT, size=(md,))

for b in range(nb):
    p = f"visual_transformer_blocks.{b}."
    for name in ("to_query", "to_key", "to_value"):
        out[p + f"cross_attention.{name}.weight"] = torch.zeros(dtype=DT, size=(md, md,))
        out[p + f"cross_attention.{name}.bias"] = torch.zeros(dtype=DT, size=(md,))
    head_dim = sum(cfg["axes_dims"])
    out[p + "cross_attention.query_norm.weight"] = torch.ones(dtype=DT, size=(head_dim,))
    out[p + "cross_attention.key_norm.weight"] = torch.ones(dtype=DT, size=(head_dim,))
    out[p + "cross_attention.out_layer.weight"] = torch.zeros(dtype=DT, size=(md, md,))
    out[p + "cross_attention.out_layer.bias"] = f32(sd[p + "xattn_bias_table"][idx])
    # visual_modulation rows: [sa shift, sa scale, sa gate, ca shift, ca scale, ca gate, ff shift, ff scale, ff gate]
    w = f32(sd[p + "visual_modulation.out_layer.weight"]).clone()
    bias = f32(sd[p + "visual_modulation.out_layer.bias"]).clone()
    w[5 * md:6 * md] = 0.0
    bias[5 * md:6 * md] = 1.0
    out[p + "visual_modulation.out_layer.weight"] = w
    out[p + "visual_modulation.out_layer.bias"] = bias

W = f32(sd["visual_embeddings.in_layer.weight"])
out["visual_embeddings.in_layer.bias"] = f32(sd["visual_embeddings.in_layer.bias"]) + (1.0 - t) * c * W.sum(dim=1)
out["out_layer.out_layer.bias"] = f32(sd["out_layer.out_layer.bias"]) + c

out = {k: v.to(DT).contiguous() for k, v in out.items()}
need = ["visual_transformer_blocks.0.cross_attention.key_norm.weight", "visual_embeddings.in_layer.bias",
        "time_embeddings.in_layer.bias", "visual_transformer_blocks.0.feed_forward.in_layer.weight"]
missing = [k for k in need if k not in out]
if missing:
    raise SystemExit(f"missing keys for ComfyUI detection: {missing}")
print("visual_embeddings.in_layer.weight", tuple(out["visual_embeddings.in_layer.weight"].shape))
save_file(out, out_path, metadata={"source": "kandinskylab/Kandinsky-ImageSR-2.0@7d5b5ed7", "one_step_t": str(t),
                                    "note": "native ComfyUI conversion, see convert_kandinsky_sr.py"})
print("ok", out_path, f"{os.path.getsize(out_path) / 1e9:.2f} GB", len(out), "tensors")
