# Fashion pose-to-video

Short fashion catalog videos with motion transfer in ComfyUI.
Project folder: `E:\dev\Fashion-pose-to-video` (replaces the old `E:\dev\Image Studio\motion`).
The user speaks Portuguese: talk to them in Portuguese. Everything in the repository (docs, code, workflow labels, CHANGELOG) is in English.

## Folder layout
- `1 - AI instructions\` — briefings and research for the AI.
- `2 - files\workflows\` — generators (`build_*.py`), API JSON copies, UI workflows (`ui_production\`, `ui_tests\`) and scripts.
- `3 - Assets\referencias de pose\` — original reference motion videos (not versioned).
  To use them in ComfyUI, copy them to `D:\Comfy-Desktop\ComfyUI-Shared\input\`.
- `docs\media\` — example video, GIF and images used in the README.

## Goal
Extract the motion (pose) from reference videos and apply it to a photo of a model wearing an e-commerce garment, producing short videos. Phase 1 is 100% local (no paid credits). Seedream/API only in a future phase.

## Working rules
- NEVER run workflows (no POST /prompt, no "Run"). Claude builds and saves; the user runs them manually and reports back.
- Use NATIVE ComfyUI nodes (do not install custom nodes) and start from the installed official templates.
- Cheap resolution (480p) for tests; high quality only after approval.
- Model downloads only with authorization.
- **Version, never overwrite:** a change to an existing workflow = new file `_v2`, `_v3`… (in ComfyUI, in the API copy and in `build_*.py`).
- **Log every change in `CHANGELOG.md`** (what, where, before → after, why), newest entry on top, in English.
- Videos/images the user asks for also go in the chat (SendUserFile).
- **Every comparison (version A vs B, before vs after) becomes a SIDE-BY-SIDE VIDEO playing simultaneously, with labels** (`W4_compare_versions.py` / `W4_side_by_side.py`), plus a zoomed side by side when detail matters. Only after ComfyUI is idle (nothing heavy while it renders).

## Repository
- Public GitHub: https://github.com/LuanVelo/fashion-pose-to-video (branch `main`). `README.md` is the public documentation: keep it up to date (workflows, models, examples in `docs/media/`).
- Never commit models or the videos in `3 - Assets/` (see `.gitignore`). After each CHANGELOG entry: commit + push.

## Environment
- GPU RTX 4090 24 GB, Windows.
- ComfyUI Desktop, instance **cfui01**: `D:\Comfy-Desktop\ComfyUI-Installs\cfui01` — version 0.46.2, at http://127.0.0.1:8188. Zero custom nodes.
- venv Python: `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\.venv\Scripts\python.exe` (use with `-I -X utf8`).
- Shared models: `D:\Comfy-Desktop\ComfyUI-Shared\models` (also used by the portable install in `E:\dev\ComfyUI_windows_portable`).
- Input/Output: `D:\Comfy-Desktop\ComfyUI-Shared\input` and `\output`, subfolders `input\motion\` and `output\motion\`.
- UI workflows saved in: `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\user\default\workflows\` (prefix `motion_`).
  **Only the production workflows stay in ComfyUI.** Test/old versions go to `2 - files\workflows\ui_tests\` (and leave ComfyUI); a copy of the production ones lives in `2 - files\workflows\ui_production\`.
- Official templates: `...\cfui01\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates\`
- Building a UI JSON without running: load the API JSON in the frontend (browser at 127.0.0.1:8188, `app.loadApiJson`, or load an existing UI and edit it), arrange, and save with `api.storeUserData('workflows/<name>.json')`. Then check that `graphToPrompt()` matches the generator's API JSON.

## Available models
- Full MiniMax H3 (ref2va, fl2va, turbo LoRAs 4/8 steps, qwen3vl_32b text encoder, video/audio VAEs) — also used by the h3_* and vovo_* workflows.
- Flux 2 Klein 9B base + qwen_3_8b (image editing/variation). Klein 9B **KV distilled** fp8 (4 steps, CFG 1, `FluxKVCache`) downloaded 2026-11-23 for the W5 v18 speed test (#54).
- Downloaded for this project: sdpose_wholebody_fp16 (checkpoints), rt_detr_v4-x-hgnet_fp16 (diffusion_models), minimax_h3_fun_controlnet_union_pruned_int8_convrot (model_patches), minimax_h3_video_vae_fp16 (vae), flux2-vae (vae), RelayVSR x2 + flash VAE.
- Plan B NOT downloaded: Wan Animate 2 (~26 GB, template video_wan_animate2) and Qwen Image Edit 2511 (~31 GB).
- The README has the full table with original links.

## Production flow (3 workflows in ComfyUI, English since 2026-11-22, CHANGELOG #38)
1. **`motion_W1_extract-pose_v3`** (PRODUCTION 1/3, `build_W1_v3.py`): reference video + pose name + clip in seconds (start, length 5.2 s) → cut by fps (ComfyMathExpression) → 124 frames → SDPose without face, with head → `output/motion/catalog/<pose>/` (pose_*.mp4, original_*.mp4, keyframes). Then `catalog.py pose <pose>` copies to `input/motion/poses/<pose>/pose.mp4` + `original.mp4`.
2. **`motion_W5_quality_v20`** (PRODUCTION 2/3, `build_W5_v20.py`, CHANGELOG #58): ~4.9 min — stage 1 FLUX.2 klein 9B **KV distilled** (4 steps, CFG 1, `FluxKVCache`, product 2 MP + skeleton 2 MP, prompt: pose only from image 2), first frame 1088×1920; stage 2 turbo LoRA `fl2v_turbo_8step` 8 steps, ControlNet 0.6 / end 0.5, INT8 attention on both models + block-sparse attention (sol-attn) on H3; reads `motion/poses/<pose>/pose.mp4`; pose for the first frame = frame 0 of pose.mp4. Replaces v16 (8.4 min, archived in `ui_tests/`). Product default `input/motion/products/caramel-tank-jeans_front.png`. Output `output/motion/production/<product>_<pose>/` (frame0, video). Then `catalog.py compare <name> <pose>` and `catalog.py upscale <name>`.
3. **`motion_W6_upscale_v3`** (PRODUCTION 3/3, `build_W6_v3.py`): RelayVSR x2 from `input/motion/production/<name>.mp4` → same production folder (video_2x 1792×3200, video_1080x1920). ~1 min.
- Side tool (TEST, not part of the motion flow): **`motion_W7_image-sr_v3`** (x2) and **`motion_W7_image-sr-x4_v2`** (x4) — Kandinsky ImageSR 2.0 still-image upscale, native nodes, model converted by `convert_kandinsky_sr.py` (one file per timestep: t0.15 x2, t0.244 x4). Inputs `input/image-sr/`, outputs `output/image-sr/x2|x4/`. Not for video (no temporal consistency). CHANGELOG #60–#64.
- `2 - files\workflows\catalog.py` = output→input bridge (ComfyUI only lists files in `input`): `pose`, `upscale`, `compare`, `list`. Never deletes; the previous file becomes `.previous-<date>`.
- The Portuguese production versions (W1 v2, W5 v10, W6 v2, `catalogo.py`) are superseded; their outputs went to `output/motion/catalogo/` and `output/motion/producao/`.

## Inputs to prepare
- Videos: 1 person, full body, static camera, good light, ≥5 s, ideally 24 fps, 9:16.
- Product: front full-body photo, back (if the video has a turn), close-up of print/logo.

## Current state (2026-11-22)
- **Production W5 = v20** (v19 approved by the user, CHANGELOG #57/#58), ~4.9 min (+47 s W6). Example: `output/motion/W5_v19/caramel-tank-jeans_look-02/video_00001_.mp4`. Previous: v16 (#48, 8.4 min, klein base 28 steps), `output/motion/W5_v15/caramel-tank-jeans_look-02/video_00001_.mp4`. Previous quality base: W5 v9 (#31), `output/motion/W5_v9/regata-caramelo-jeans_look-02_q9/video_00001_.mp4` (20 steps, ~27 min, slightly sharper face).
- W6 v2 upscale of the v9 video ran fine (#34): `output/motion/producao/regata-caramelo-jeans_look-02/` (video_2x, video_1080x1920, side-by-side videos).
- W6 v3 ran (#51, 47 s) on the v15 video: clearly sharper face/curls/knit at 1080×1920 → keep the upscale in the fast flow. W1 v3 has not run yet; W5 v20 = the v19 graph (ran). Suggested next: W1 v3 for new poses → `catalog.py pose <pose>` → W5 v20 → W6 v3; confirm v20 with another product (print/logo: the product reference is now 2 MP).
- Test history (W1 v1, W2, W3a, W5 v1–v10, W6 v1/v2): see CHANGELOG.md. Key lessons: description text beats image 1 (leave it empty); `flux2-vae` full decoder; 896×1600 is the local sweet spot (1088×1920 changes the garment, 59 min); never remove the head from the skeleton (v8: lines drawn on clothes); upscale does not fix face defects; a bag carried in the hand disappears in the video; ComfyUI 0.46.2 occasionally throws IndexError in free_memory on VAEDecode (re-run).
- Face research: `1 - AI instructions\research-eyes-pose-h3.md` (plan A loosen the ControlNet = done in v9 → B head retargeting, translation only → C second face pass with H3's native inpaint).
- Reference video not yet used in production: `3 - Assets\referencias de pose\pozze_black-friday_DfEy39VA9dX.mp4` (720×1280, 30 fps, 11 s; back turn; cut at the thigh).
- **Speed work (CHANGELOG #39–#48):** W5 v12–v15 (tests, in `ui_tests/`, outputs `output/motion/W5_v12..v15/`) → v15 approved and promoted as **W5 v16**: ~27 min → **8.4 min** end to end. Lessons: turbo LoRA + ControlNet 1.0 paints the skeleton on the body (fix: strength 0.6, end 0.5); native INT8 attention (`ModelAttentionBackend` → `comfy kitchen attention`) ≈ SageAttention, ~2× on H3, ~1.6× on FLUX, no visible change, nothing to install. W5 v17–v19 (#52–#57): sparse attention on H3 (~20 s), klein 9B KV distilled first frame (3 min → 3 s; needs skeleton 2 MP + prompt "pose only from image 2", else it copies the product pose) → v20. Next speed candidates: split W5 into a first-frame batch + a video batch for catalogs (no model swaps, approve frame0 before the video); sparse start 0.0.
- Pose `look-02` in the catalog (`input/motion/poses/look-02/pose.mp4`) = the v9 skeleton (no `original.mp4` yet; W1 v3 has not run).
- Next: run the English production flow end to end; build the catalog with ~4 poses (incl. Pozze); confirm replicability with another product; if the eye problem returns, try end 0.6 or plan B.
