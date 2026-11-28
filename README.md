# Fashion pose-to-video

Generate short fashion catalog videos with motion transfer. The pipeline takes the movement from a reference video and applies it to a model wearing the product from your e-commerce photo. Everything runs locally in [ComfyUI](https://github.com/comfyanonymous/ComfyUI) with **native nodes only**: no custom nodes and no paid APIs.

![Original, skeleton, generated video and super-resolution playing together](docs/media/example_4-stages.gif)

**1 Original** (reference video) · **2 Skeleton** (extracted motion) · **3 Generated** (896×1600) · **4 Super-resolution** (1080×1920). Higher quality video: [`docs/media/example_4-stages.mp4`](docs/media/example_4-stages.mp4).

![Pipeline in 5 steps](docs/media/pipeline.jpg)

---

## Contents

- [How it works](#how-it-works)
- [The 3 production workflows](#the-3-production-workflows)
- [Step by step](#step-by-step)
- [Requirements](#requirements)
- [Models (download)](#models-download)
- [Input and output folders](#input-and-output-folders)
- [Base settings](#base-settings)
- [Results and lessons learned](#results-and-lessons-learned)
- [Repository layout](#repository-layout)
- [What is not in this repository](#what-is-not-in-this-repository)

---

## How it works

Pose extraction runs **once per movement** and goes into a pose catalog. After that, any product can be combined with any pose in the catalog.

```mermaid
flowchart LR
    subgraph P1["1 · Pose extraction (W1) · ~1 min"]
        A["Reference video<br/>one person, full body,<br/>static camera"] --> B["Cut the clip<br/>(start + length in seconds,<br/>converted with the fps)"]
        B --> C["Resample to<br/>124 frames"]
        C --> D["SDPose wholebody<br/>skeleton WITHOUT face,<br/>WITH head"]
    end

    D --> K[("Pose catalog<br/>input/motion/poses/#lt;pose#gt;/<br/>pose.mp4 · original.mp4")]

    subgraph P2["2 · First frame + video (W5) · ~5 min"]
        E["Product photo<br/>(model wearing the garment)"] --> F["Stage 1 · FLUX.2 klein 9B KV<br/>(distilled, 4 steps)<br/>product + skeleton of frame 0<br/>→ first frame 1088×1920"]
        K --> F
        F --> G["Stage 2 · MiniMax H3 ref2va<br/>+ turbo LoRA 8 steps<br/>+ Fun ControlNet (pose)<br/>→ video 896×1600, 124 frames"]
        K --> G
        E --> G
    end

    subgraph P3["3 · Upscale (W6) · ~1 min"]
        H["RelayVSR x2<br/>1792×3200"] --> I["Downscale to<br/>1080×1920"]
    end

    G --> H
    I --> J["Final catalog video<br/>1080×1920 · 24 fps · 5 s"]
    G -.-> L["Side-by-side comparison<br/>original | skeleton | generated"]
```

**Why two stages?** The video starts from a first frame that already has the right garment in the right pose (stage 1, FLUX.2). H3 then animates from that frame, following the skeleton (stage 2), with the product photo as a reference. Making the frame first keeps the garment much more faithful than generating the video directly.

**The bridge between steps.** ComfyUI only lists files from its `input` folder, while the workflows save to `output`. The [`catalog.py`](01_pipeline/scripts/catalog.py) script copies results into `input` with fixed names and never deletes anything; a replaced file is kept as `.previous-<date>`.

---

## The production workflows

| # | Workflow (ComfyUI) | Input | What it does | Output |
|---|---|---|---|---|
| 1 | [`motion_W1_extract-pose_v3`](01_pipeline/workflows/ui/production/motion_W1_extract-pose_v3.json) | reference video, pose name, clip start and length (default 5.2 s) | cuts the clip using the fps (`ComfyMathExpression`), resamples to 124 frames, runs SDPose → skeleton without face and with head, at 24 fps | `output/motion/catalog/<pose>/`: pose, original and 4 thumbnails of each |
| 2a | [`motion_W5_frame0_v21`](01_pipeline/workflows/ui/production/motion_W5_frame0_v21.json) | product photo **reframed to the pose** + `motion/poses/<pose>/pose.mp4` | stage 1 only: first frame (FLUX.2 klein 9B KV, 4 steps), ~5 s; run with several image seeds and **choose one** (hands, arms, sleeves, feet, accessories) | `output/motion/frame0/<product>__<pose>/s<seed>/` |
| 2b | [`motion_W5_video_v21`](01_pipeline/workflows/ui/production/motion_W5_video_v21.json) | the **chosen** first frame + the reframed product + `pose.mp4` | stage 2 only: video (H3 + turbo LoRA + ControlNet 0.6/0.5 + INT8 + sparse attention), ~3.5 min; video prompt without "stripes", pose-neutral motion | `output/motion/video/<product>__<pose>/<run>/` |
| 3 | [`motion_W6_upscale_v3`](01_pipeline/workflows/ui/production/motion_W6_upscale_v3.json) | `motion/production/<name>.mp4` | RelayVSR x2, then downscale to 1080×1920; audio and fps copied from the input | same production folder: `video_2x` and `video_1080x1920` |

Every workflow exists in three forms in this repo:
- **UI** (`01_pipeline/workflows/ui/production/*.json`): the file you open in ComfyUI, with groups and a usage note.
- **API** (`*_api.json`): the same graph in ComfyUI's API format.
- **Generator** (`build_*.py`): the Python script that writes the API JSON. It is the source of truth for each version.

**Speed (W5 v12 → v16, 2026-11-22):** the video went from ~27 min (v9/v11) to **~8.5 min end to end** with the same garment and motion and a slightly softer face. Steps: turbo LoRA 8 steps (v12, 14 min, but it painted the skeleton on the body) → ControlNet strength 0.6 / end 0.5 (v13, lines gone) → ComfyUI's native INT8 attention on the video model (v14, video 7 → 3.4 min) and on the first frame (v15, 4.9 → 3.1 min). v15 was promoted to production as v16. **W5 v17 → v20 (2026-11-23): ~8.4 → ~4.9 min** with native sparse attention on the video (v17) and the distilled FLUX.2 klein 9B KV for the first frame (4 steps in 3 s instead of 28 steps in 3 min; v18 copied the pose of the product photo, fixed in v19). v19 was promoted as v20. Details in [Speed](#speed) and in `CHANGELOG.md` #39–#58.

**Side tool (test): W7 image super-resolution.** [`motion_W7_image-sr_v3`](01_pipeline/workflows/ui/tools/motion_W7_image-sr_v3.json) (x2) and [`motion_W7_image-sr-x4_v2`](01_pipeline/workflows/ui/tools/motion_W7_image-sr-x4_v2.json) (x4) upscale **still images** (first frame, product photos) with [Kandinsky ImageSR 2.0](https://github.com/kandinskylab/kandinsky-image-sr) (MIT, one diffusion step) using only native nodes. The release is a "baked" model without the text path, so [`convert_kandinsky_sr.py`](01_pipeline/scripts/convert_kandinsky_sr.py) rebuilds it in ComfyUI's native Kandinsky 5 Image format for one timestep (t = 0.15 for x2, 0.244 for x4). Frame0 1088×1920 → 2176×3840 in 30 s; much sharper face, knit and denim, same colors. It works frame by frame, so it is **not** for the video (W6 stays). Inputs in `input/image-sr/`, outputs in `output/image-sr/x2|x4/`. Details in `CHANGELOG.md` #60–#64.

**W5 v21 (2026-11-28, `CHANGELOG.md` #79): W5 split in two.** The first frame decides most defects (an extra hand, skeleton lines painted on the clothes, long sleeves instead of 3/4, extra accessories) and costs ~5 s, the video ~3.5 min. So W5 is now two workflows: several first-frame candidates are generated, a person chooses one, and only that one becomes a video. With the product photo reframed to the pose and the corrected video prompt, 10 of 12 test videos were clean (3 products × 2 poses × 2 seeds; the 2 others changed accessories seen from the back: turning poses need a back photo). The whole flow runs with [`run_product.py`](01_pipeline/scripts/run_product.py) `prep | frame0 | video`. Experiments: [`04_experiments/`](04_experiments/README.md) EXP-001…009.

**Pose catalog: 26 skeletons, extracted but not validated.** [`02_library/poses/`](02_library/poses/) holds 26 skeletons (5.2 s, 124 frames, 24 fps, 576×1024: 20 women, 6 men; turns, profiles, hands, weight shift, walk) extracted with W1 v3 from studio product videos of fashion e-commerce stores. Only the skeletons are in the repo, not the original clips. **In W5 v20 most of them made the video change the garment** (the skeleton lines turn into stripes), depending on pose and product; see the catalog [README](02_library/poses/README.md) and the [validation plan](00_docs/plans/plan-2026-11-27-pose-catalog-and-inputs.md). `look-02` is still the only pose proven in production, with the caramel product.

> **W1 v3 ignores the clip start (ComfyUI 0.46.2 bug).** `VideoFrameSample` decodes from the start of the file and drops the trim done by `VideoTemporalCrop`, so W1 v3 always takes the first seconds of the video. Until W1 is fixed, cut the clip beforehand so it starts at 0 s, or leave the start at 0. Details in `CHANGELOG.md` #68.

The test workflows (W1 v1/v2, W2, W3a, W5 v1–v19, W6 v1/v2, W7) are archived in [`01_pipeline/workflows/ui/archive/`](01_pipeline/workflows/ui/archive). Up to W5 v10 / W1 v2 / W6 v2 their labels are in Portuguese.

---

## Step by step

1. **Install the models** from the [table below](#models-download) into the folders shown.
2. **Import the production workflows** from `01_pipeline/workflows/ui/production/` into ComfyUI (drag the `.json` onto the canvas, or copy it to `ComfyUI/user/default/workflows/`).
3. **Extract a pose:** copy the reference video into `ComfyUI/input/`, open `motion_W1_extract-pose_v3`, fill in the pose name and the clip, and run it.
4. **Add the pose to the catalog:**
   ```bash
   python -I -X utf8 "01_pipeline/scripts/catalog.py" pose look-02
   ```
5. **Generate the video** (W5 v21, see [`run_product.py`](01_pipeline/scripts/run_product.py)):
   ```bash
   python -I -X utf8 "01_pipeline/scripts/run_product.py" prep  <product> <photo> <pose>   # reframe the photo to the pose
   python -I -X utf8 "01_pipeline/scripts/run_product.py" frame0 <product> <pose> 6       # 6 first-frame candidates + candidates.html
   python -I -X utf8 "01_pipeline/scripts/run_product.py" video <product> <pose> <seed>   # video from the chosen candidate + report
   ```
   Or by hand in ComfyUI: `motion_W5_frame0_v21` (a few image seeds), then `motion_W5_video_v21` with the chosen first frame. Poses need `motion/poses/<pose>/keypoints.json` for the reframing (`pose_keypoints.py extract` on `original.mp4`).
6. **Optional, comparison video:** builds the original | skeleton | generated video.
   ```bash
   python -I -X utf8 "01_pipeline/scripts/catalog.py" compare caramel-tank-jeans_look-02 look-02
   ```
7. **Upscale:**
   ```bash
   python -I -X utf8 "01_pipeline/scripts/catalog.py" upscale caramel-tank-jeans_look-02
   ```
   Open `motion_W6_upscale_v3`, pick `motion/production/<name>.mp4`, use the same name and run it (~1 min).

> **Paths:** `catalog.py` points to `D:\Comfy-Desktop\ComfyUI-Shared\input|output\motion`. Change the `IN` and `OUT` constants at the top of the file to match your install. Run it with ComfyUI's own Python (it needs `av` and `Pillow`, which ship with ComfyUI).

**Turning stages on and off:** right-click a group title and choose *Set Group Nodes to Never/Always*. This is built into ComfyUI. Use it, for example, to redo only the video without redoing the first frame.

**Good reference video:** one person, full body, static camera, good light, at least 5 s, ideally 24 fps and vertical 9:16.

**Good product photo:** the model from the front, full body. For videos with a turn, a back photo helps.

---

## Requirements

- **GPU:** tested on an NVIDIA RTX 4090 24 GB. Stage 2 at 896×1600 takes ~51 s per step and fits in 24 GB.
- **ComfyUI 0.46.2** (tested on ComfyUI Desktop), **no custom nodes**. Every node is native, including `SDPoseKeypointExtractor`, `MiniMaxH3*`, `RelayVSRConditioning`, `VSRDecode`, `ComfyMathExpression` and `VideoFrameSample`.
- **Disk:** ~69 GB of models.
- **Python** from ComfyUI itself for the scripts (`catalog.py`, `W4_*.py`, `build_*.py`).

---

## Models (download)

No model files are in this repository; download them from the original repositories. These are the same links used by the official ComfyUI templates.

| Folder in `ComfyUI/models/` | File | Size | Used in | Link |
|---|---|---:|---|---|
| `checkpoints/` | `sdpose_wholebody_fp16.safetensors` | 1.8 GB | W1 (skeleton) | [Comfy-Org/SDPose](https://huggingface.co/Comfy-Org/SDPose/resolve/main/checkpoints/sdpose_wholebody_fp16.safetensors) |
| `diffusion_models/` | `flux-2-klein-9b-kv-fp8.safetensors` | 9.8 GB | W5 stage 1 (v18+) | [black-forest-labs/FLUX.2-klein-9b-kv-fp8](https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-kv-fp8/resolve/main/flux-2-klein-9b-kv-fp8.safetensors) ³ |
| `diffusion_models/` | `flux-2-klein-base-9b-fp8.safetensors` | 8.9 GB | W5 stage 1 up to v17 (archived) | [black-forest-labs/FLUX.2-klein-base-9b-fp8](https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9b-fp8) ¹ |
| `text_encoders/` | `qwen_3_8b_fp8mixed.safetensors` | 8.1 GB | W5 stage 1 | [Comfy-Org/flux2-klein-9B](https://huggingface.co/Comfy-Org/flux2-klein-9B/resolve/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors) |
| `vae/` | `flux2-vae.safetensors` | 320 MB | W5 stage 1 | [Comfy-Org/flux2-dev](https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors) ² |
| `diffusion_models/` | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 19.5 GB | W5 stage 2 | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors) |
| `text_encoders/` | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 14.6 GB | W5 stage 2 | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors) |
| `vae/` | `minimax_h3_video_vae_fp16.safetensors` | 4.8 GB | W5 stage 2 | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors) |
| `vae/` | `minimax_h3_audio_vae_fp32.safetensors` | 577 MB | W5 stage 2 | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors) |
| `model_patches/` | `minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors` | 2.1 GB | W5 stage 2 (pose ControlNet) | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/model_patches/minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors) |
| `loras/` | `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 1.8 GB | W5, optional (turbo mode, off by default) | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors) |
| `loras/` | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 2.0 GB | W5 (turbo on by default, 8 steps) | [lightx2v/Minimax-h3-Turbo](https://huggingface.co/lightx2v/Minimax-h3-Turbo/resolve/main/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors) |
| `diffusion_models/` | `relayvsr_x2_lightx2v_int8_convrot.safetensors` | 4.8 GB | W6 | [Comfy-Org/RelayVSR](https://huggingface.co/Comfy-Org/RelayVSR/resolve/main/diffusion_models/relayvsr_x2_lightx2v_int8_convrot.safetensors) |
| `vae/` | `relayvsr_flash_vae_x2_fp32.safetensors` | 121 MB | W6 | [Comfy-Org/RelayVSR](https://huggingface.co/Comfy-Org/RelayVSR/resolve/main/vae/relayvsr_flash_vae_x2_fp32.safetensors) |
| `diffusion_models/` | `kandinsky_imagesr2_t0.15_comfy_bf16.safetensors`, `..._t0.244_...` | 11.7 GB each | W7 (x2 / x4) | made by `convert_kandinsky_sr.py` from [kandinskylab/Kandinsky-ImageSR-2.0](https://huggingface.co/kandinskylab/Kandinsky-ImageSR-2.0) (10.4 GB download) ⁴ |
| `vae/` | `kandinsky_imagesr2_flux1_vae.safetensors` | 168 MB | W7 | the `vae/` of the same release (FLUX.1 VAE), renamed |
| `text_encoders/` | `qwen_2.5_vl_7b_fp8_scaled.safetensors` | 9.4 GB | W7 (required by the native model, output ignored) | [Comfy-Org/HunyuanVideo_1.5_repackaged](https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors) |
| `text_encoders/` | `clip_l.safetensors` | 246 MB | W7 (same) | [comfyanonymous/flux_text_encoders](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors) |

¹ Gated repository: accept the Black Forest Labs license on Hugging Face before downloading.
² Use this full VAE. The `full_encoder_small_decoder` from the klein template makes the first frame blurry.
³ Public repository. Both klein 9B models are under the FLUX non-commercial license.
⁴ Download the release to `models/diffusers/Kandinsky-ImageSR-2.0/`, then run `python -I -X utf8 convert_kandinsky_sr.py --t 0.15` (and `--t 0.244`). MIT license.

```text
ComfyUI/models/
├── checkpoints/
│   └── sdpose_wholebody_fp16.safetensors
├── diffusion_models/
│   ├── flux-2-klein-9b-kv-fp8.safetensors
│   ├── flux-2-klein-base-9b-fp8.safetensors
│   ├── minimax_h3_ref2va_pruned_int8_convrot.safetensors
│   └── relayvsr_x2_lightx2v_int8_convrot.safetensors
├── loras/
│   ├── minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors
│   └── minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors
├── model_patches/
│   └── minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors
├── text_encoders/
│   ├── qwen_3_8b_fp8mixed.safetensors
│   └── qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
└── vae/
    ├── flux2-vae.safetensors
    ├── minimax_h3_audio_vae_fp32.safetensors
    ├── minimax_h3_video_vae_fp16.safetensors
    └── relayvsr_flash_vae_x2_fp32.safetensors
```

---

## Input and output folders

Paths are relative to ComfyUI's `input` and `output` folders.

```text
input/
├── <reference-video>.mp4                   ← W1 input
└── motion/
    ├── products/<product>_front.png        ← product photos
    ├── poses/<pose>/                       ← catalog (catalog.py pose); the W5 pose list
    │   ├── pose.mp4                        ← read by W5
    │   ├── original.mp4
    │   └── keyframes/pose-1..4.png, original-1..4.png
    ├── poses_parked/rejected|untested/     ← poses kept out of the W5 list
    ├── sources/                            ← reference clips for W1 (pre-cut, start 0)
    ├── production/<product>_<pose>.mp4     ← W6 input (catalog.py upscale)
    └── _archive/                           ← old test inputs

output/motion/
├── catalog/<pose>/                         ← W1 output
│   ├── pose_00001_.mp4 · original_00001_.mp4
│   └── keyframes/
├── experiments/EXP-<nnn>_…/<generation>/   ← tests (video, report.mp4, review_sheet.jpg, review.json)
├── reports.html                            ← local page: every generation, product | original | skeleton | generated
├── _archive/                               ← old test outputs (W2…W6 v1, W5_v1…v19, catalogo, producao)
└── production/<product>_<pose>/            ← W5 and W6 outputs
    ├── frame0_00001_.png                   ← first frame (1536×2720)
    ├── video_00001_.mp4                    ← generated video (896×1600)
    ├── compare.mp4                         ← original | skeleton | generated
    ├── video_2x_00001_.mp4                 ← 1792×3200
    └── video_1080x1920_00001_.mp4          ← final video
```

---

## Base settings

| | Stage 1 · first frame | Stage 2 · video |
|---|---|---|
| Model | FLUX.2 klein 9B **KV** (distilled) fp8 + qwen_3_8b, `FluxKVCache` | MiniMax H3 ref2va int8 + qwen3vl 32B |
| References | image 1 = product (**2 MP**) · image 2 = skeleton of frame 0 (**2 MP**), via `ReferenceLatent` | ref 1 = product (`max`) · frame 0 = stage 1 output (`MiniMaxH3AddGuide`) |
| Resolution | 1088×1920 | 896×1600, 124 frames, 24 fps |
| Sampling | **4 steps · CFG 1** · euler | **turbo LoRA `minimax_h3_fl2v_turbo_8step_v1.0`, 8 steps** · guidance 1.0 · res_multistep (turbo OFF = 20 steps) |
| Control | — | Fun ControlNet union, **strength 0.6, end_percent 0.5** |
| Attention | INT8 (`Model Attention Backend` → `comfy kitchen attention`) | INT8 (same) + block-sparse (`Model Sparse Attention`, sol-attn, tau 1.3, from 20%) |
| VAE | `flux2-vae` | video fp16 + audio fp32 |
| Seed | 20261121 (fixed) | 20261121 (fixed) |

The stage 1 prompt tells the model to copy the garment **only from image 1** and the pose, framing and size in the frame **only from the skeleton in image 2** (without that, the distilled model copies the pose of the product photo), and the garment description field is left empty on purpose: when there is text describing the outfit, the text wins over the image.

---

## Results and lessons learned

The full log, with every change and the reason for it, is in [`CHANGELOG.md`](CHANGELOG.md).

### Cross-eyed or misplaced eyes → `end_percent 0.7`

The generated person's head has different proportions from the person in the reference video. The skeleton's eye and nose points land on the generated model's eyebrows, and the ControlNet pulls the eyes there. The fix was to release the ControlNet for the last 30% of the steps, which is when facial detail is drawn. Motion and garment did not change.

![Face in 12 frames: v7 (end 1.0) on top, v9 (end 0.7) below](docs/media/face_v7_vs_v9.jpg)

### Never remove the head from the skeleton

Without the head, the *union* ControlNet starts reading the stick figure as a line map and draws the skeleton lines onto the clothes.

![v8 without head vs v9](docs/media/v8_vs_v9.jpg)

### Upscaling adds sharpness but does not fix defects

RelayVSR x2 makes the face, hair and fabric texture much sharper, with a bit more contrast on the skin. Defects from the generation are still there, only more visible. That is why the face is fixed during generation.

![Zoom before vs after upscale](docs/media/upscale_zoom.jpg)

### Speed

Measured on an RTX 4090, product `caramel-tank-jeans`, pose `look-02`, same seeds.

![All versions side by side, v9 to v16 + upscale](docs/media/speed_v9_to_v16.jpg)

*Frame 60 of each version. Video: [`docs/media/speed_v9_to_v16.mp4`](docs/media/speed_v9_to_v16.mp4). v12 shows the skeleton lines painted by the turbo LoRA with a strong ControlNet; from v13 on the bag stays in the hand.*

| Version | Change | Stage 1 | Video | Total | Image |
|---|---|---|---|---|---|
| v9 / v11 | base (20 steps, first frame 1536×2720) | ~7 min | ~20 min | **27.7 min** | approved base |
| v12 | turbo LoRA 8 steps + first frame 1088×1920 | 4.9 min | 7.6 min | 14.3 min | skeleton lines painted on the body |
| v13 | + ControlNet strength 0.6, end 0.5 | (cache) | 7.0 min | ~14 min | lines gone, bag kept, face slightly softer |
| v14 | + INT8 attention on the video model | (cache) | 3.4 min | ~9.5 min | same as v13 |
| **v15 → v16** | + INT8 attention on the first frame | 3.1 min | 3.6 min | **8.4 min** (cold cache) | same as v14 |
| v16 + W6 v3 | + RelayVSR upscale to 1080×1920 | | +47 s | ~9.2 min | sharper face, curls and knit |
| v17 | + sparse attention on the video (sol-attn) | 3.1 min | 3.2 min | 8.1 min | same as v16 |
| v18 | + first frame with klein 9B **KV distilled**, 4 steps | 15 s | 3.0 min | 5.0 min | garment faithful, but **copied the pose of the product photo** |
| **v19 → v20** | + product 2 MP, skeleton 2 MP, prompt "pose only from image 2" | **3 s** | 2.9 min | **4.9 min** (cold cache) | follows the skeleton from frame 0 |
| v20 + W6 v3 | + RelayVSR upscale to 1080×1920 | | +47 s | **~5.7 min** | |

- The **turbo LoRA** with a strong ControlNet copies the stick figure into the pixels; loosening the ControlNet fixes it and the motion still follows the pose.
- **INT8 attention** (`Model Attention Backend` → `comfy kitchen attention`) is native in ComfyUI 0.46: the same idea as SageAttention, nothing to install, ~2× on the video with no visible change.
- **Sparse attention** (`Model Sparse Attention`, native, sol-attn) makes each sparse video step ~30% faster with no visible change; the gain is small (~20 s) because the turbo video has only 8 steps.
- The **distilled klein 9B KV** (4 steps, CFG 1, reference images cached) makes the first frame ~60× faster. It needs the skeleton at the same size as the product and an explicit prompt, otherwise it copies the pose of the product photo.
- Not used: lower resolution + upscale (704×1248 deforms the face and upscaling does not fix it).
- The **W6 upscale** is still worth it with the fast W5: it delivers the 1080×1920 size the platforms want and gives back the detail the 8-step face loses, for under a minute.

![Fast W5 (v16) vs W6 upscale, frame 60](docs/media/upscale_zoom_v16.jpg)

![Skeleton, v17, v18 and v19 (= v20), frames 0 to 123](docs/media/speed_v17_to_v20_frames.jpg)

*v18 starts with the hand in the pocket (the pose of the product photo); v19/v20 follow the skeleton from frame 0.*

### Other lessons

| Test | Result |
|---|---|
| Video at 704×1248 | faithful garment, deformed face (face ~100 px wide) |
| Video at 1088×1920 | good face, but **the garment changed** and it took 59 min: not viable locally |
| Video at 896×1600 | best balance: faithful garment, good face, ~18–27 min |
| Skeleton without the 68 face points | no effect on the face (kept, since it is cleaner) |
| Bag carried in the hand | disappeared in the 20-step video (v9); **kept for the whole video** with turbo + ControlNet 0.6/0.5 (v13–v16) |
| ComfyUI 0.46.2 bug | occasional `IndexError` in `free_memory` during VAEDecode; running again fixes it |
| ComfyUI 0.46.2 bug (W1) | `VideoFrameSample` after `VideoTemporalCrop` ignores the crop start: W1 v3 always takes the clip from 0 s. Cut the clip beforehand |
| Pose clips from e-commerce product videos | edited videos (full body ~3–4 s → close-up → full body): only ~1 in 4 has 5.2 s without a cut; check the cut frame by frame, and that the model is fully in frame at frame 0 |

---

## Repository layout

One folder per job, numbered in the order of the work (since 2026-11-27, `CHANGELOG.md` #70):

```text
.
├── README.md · CHANGELOG.md · CLAUDE.md
├── 00_docs/                    what we think and decide
│   ├── plans/                  plans (e.g. the pose catalog / inputs plan)
│   ├── research/               research notes (e.g. the face problem, plan A/B/C)
│   └── decisions.md            one line per decision: date, decision, why
├── 01_pipeline/                what runs
│   ├── workflows/
│   │   ├── build_*.py          API JSON generators (one per version; they import each other)
│   │   ├── *_api.json          workflows in API format
│   │   └── ui/production|tools|archive/   UI workflows: the 3 in production, side tools (W7), old/test versions
│   └── scripts/                catalog.py, generation_report.py, generation_review.py, pose_compare_page.py, W4_*.py, convert_kandinsky_sr.py
├── 02_library/                 the source of truth for inputs, with status
│   ├── poses/                  pose skeletons + catalog.csv (candidate / validated / rejected / untested)
│   ├── products/<product>/     meta.json, description (images not versioned)
│   └── models/                 (future) model identities
├── 03_references/pose-videos/  reference videos and e-commerce clips (not versioned, README only)
├── 04_experiments/             every test: EXP-<nnn>_<date>_<slug>/ with plan.md, runs.csv, result.md
├── 05_approvals/approvals.csv  what was approved, by whom, when, with which evidence
└── docs/media/                 video, GIF and images used in this README
```

| To find… | Look in |
|---|---|
| what changed in the project | `CHANGELOG.md` |
| why we decided something | `00_docs/decisions.md` |
| what was tested and the result | `04_experiments/EXP-…/result.md` |
| what is approved | `05_approvals/approvals.csv`, `02_library/poses/catalog.csv` |

**Project rules:**
- A change to a workflow becomes a new version (`_v2`, `_v3`…); nothing is overwritten.
- Every change goes into `CHANGELOG.md`.
- Every test is an experiment folder with its plan written first (`04_experiments/README.md`).
- Every comparison becomes a side-by-side video; every W5 generation gets a report (product | original | skeleton | generated).

---

## What is not in this repository

- **Models:** download them from the links above.
- **Reference videos** (`03_references/`): third-party content, not versioned. That includes the e-commerce clips behind the pose catalog: only their skeletons are published.
- **ComfyUI outputs**, apart from the examples in `docs/media/`.

The project was built with the help of [Claude Code](https://claude.com/claude-code). `CLAUDE.md` holds the briefing the assistant works from.
