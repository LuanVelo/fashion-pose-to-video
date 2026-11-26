# Changelog — Fashion pose-to-video

Detailed record of what was created or changed, where, and why. The newest entry is at the top.
Path abbreviations:
- `WF/` = `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\user\default\workflows\` (workflows that show up in ComfyUI)
- `IN/` = `D:\Comfy-Desktop\ComfyUI-Shared\input\`
- `OUT/` = `D:\Comfy-Desktop\ComfyUI-Shared\output\`
- `PROJ/` = `E:\dev\Fashion-pose-to-video\`

**Versioning rule (from 2026-11-21 on):** an existing workflow is no longer modified. A configuration change = a new file with a version suffix (`_v1`, `_v2`…), both in ComfyUI (`WF/`) and in the API copy and the generator (`PROJ/2 - files/workflows/`). The `build_*.py` generators refuse to overwrite an existing version file.

---

## 2026-11-25 — #62 W7 image SR v2 (x2, any size) + W7 image SR x4 v1
**Bug (W7 v1, user's run on `fernanda_ref.png`, 406×483):** `RuntimeError: size of tensor a (101) must match ... (102)` in SamplerCustomAdvanced. The ×2 image (812×966) gives an odd latent width; the native Kandinsky 5 pads the latent to the 2×2 patch and does not crop its output back. v1 only worked because 1088×1920 ×2 is a multiple of 16.
**Fix (v2 and x4):** after the bicubic upscale, `PadImageNode` (pad to multiple of 16, mirror, like the official pipeline's replicate padding) → VAE … decode → `ImageCrop` back to exactly factor × input (offsets from `GetImageSize` + `ComfyMathExpression` `((-a) % 16) // 2`). Output prefixes now generic: `OUT/motion/sr/x2/` and `OUT/motion/sr/x4/` (`kandinsky_*`, `bicubic_*`).
**Created:** `build_W7_v2.py` (shared `build()`), `W7_image-sr_v2_api.json`, `WF/motion_W7_image-sr_v2.json` (default input `fernanda_ref.png`); `build_W7x4_v1.py`, `W7_image-sr-x4_v1_api.json`, `WF/motion_W7_image-sr-x4_v1.json`; x4 model `models/diffusion_models/kandinsky_imagesr2_t0.244_comfy_bf16.safetensors` (`convert_kandinsky_sr.py --t 0.244`, x4 default, creativity 4); x4 test input `IN/motion/sr/caramel-tank-jeans_front_480x680.png` (the product photo reduced to 1/4 with lanczos, so the 1920×2720 x4 result can be compared with the real photo). Copies in `ui_tests/`, plus the user's re-saved v1 (subgraph "Setup") as `ui_tests/motion_W7_image-sr_v1_resaved-2026-11-25.json`.
**Check:** `graphToPrompt()` equals both API JSONs. Not run (the user runs them). x4 is for small inputs (whole image in one pass): keep the input ≤ ~600 px.

## 2026-11-25 — #61 W7 image SR v1 run: 30 s, clearly sharper, no color shift
**Run** (the user, default values, frame0 1088×1920 → 2176×3840): success, **30 s** end to end (cold start, includes loading the 11.7 GB model and the encoders). Whole image in one pass, no memory problem.
**Image:** much sharper than the original enlarged with lanczos: eyes, brows, lashes, lips and skin texture defined, curls separated, knit rows visible on the tank, denim twill visible, nails and fingers clean. Identity, garment, color and composition unchanged (global mean RGB within ~1 level, mean abs difference 2.6/255 after reducing back to 1088×1920). A little more local contrast on the face (looks retouched rather than wrong).
**Comparison** in `OUT/motion/sr/`: `compare_original_vs_kandinsky-x2.jpg` (whole image), `compare_original_vs_kandinsky-x2_zoom.jpg` (face, knit, hand/jeans/bag), `compare_original_vs_kandinsky-x2_full.png` (full resolution). Stills, so an image comparison instead of a video.

## 2026-11-25 — #60 W7 image SR v1 (TEST): Kandinsky ImageSR 2.0 x2 for stills, native nodes
**User's request:** test https://github.com/kandinskylab/kandinsky-image-sr (one-step diffusion SR, x2/x4, MIT) in a separate workflow, native nodes only. Image only (no temporal consistency), so it is for stills (frame0, product photos), not for the video (W6 RelayVSR stays).
**Downloaded (authorized):** `kandinskylab/Kandinsky-ImageSR-2.0@7d5b5ed7` (transformer 10.3 GB + FLUX.1 VAE) into `models/diffusers/Kandinsky-ImageSR-2.0/`; text encoders of the official `image_kandinsky5_t2i` template, `qwen_2.5_vl_7b_fp8_scaled` (9.4 GB) and `clip_l` (0.25 GB), in `models/text_encoders/`.
**Created:** `PROJ/2 - files/workflows/convert_kandinsky_sr.py` → `models/diffusion_models/kandinsky_imagesr2_t0.15_comfy_bf16.safetensors` (11.7 GB); `models/vae/kandinsky_imagesr2_flux1_vae.safetensors` (copy of the release VAE); `build_W7_v1.py`, `W7_image-sr_v1_api.json`, `WF/motion_W7_image-sr_v1.json` (copy in `ui_tests/`); test input `IN/motion/sr/caramel-tank-jeans_look-02_frame0.png` (W5 v19 frame0, 1088×1920).
**Why a conversion:** the release is a "baked" Kandinsky 5 DiT without the text tower and cross-attention (their zero-text outputs are per-timestep tables). ComfyUI natively loads Kandinsky 5 Image, so the converter rebuilds those modules as constants for one t (time embedding = table, cross-attention = table bias with gate 1, text weights 0) and folds two native-vs-pipeline differences into the weights: the Flux latent shift (ComfyUI subtracts 0.1159, the pipeline does not) and the flow start (1−t)·latent with zero noise (the workflow multiplies the latent by 1/(1−t)). Checked offline: ComfyUI detects it as `Kandinsky5Image` / Flux latent; time embedding and cross-attention bias equal the release tables (bf16 error only).
**Graph:** LoadImage → bicubic ×2 → VAE encode → latent ×1/(1−0.15) → SamplerCustomAdvanced (DisableNoise, euler, ManualSigmas `0.15, 0`, empty prompt zeroed) → decode → save `OUT/motion/sr/<name>_kandinsky-x2_*` + bicubic ×2 baseline. t=0.15 = x2 default (creativity 4). Difference from the official pipeline: no 1024 px tiling (whole image in one pass, 2176×3840 for frame0). `graphToPrompt()` equals the generator's API JSON. Not run (the user runs it).

## 2026-11-23 — #59 Remove the re-saved W5 v16 from ComfyUI
**User's decision:** remove it. `WF/motion_W5_quality_v16.json` (the user's subgraph re-organization, #58) was identical to the archived `ui_tests/motion_W5_quality_v16_resaved-2026-11-23.json` and was removed from `WF/` (backup also in the session scratchpad). `WF/` now has only production: `motion_W1_extract-pose_v3`, `motion_W5_quality_v20`, `motion_W6_upscale_v3`.

## 2026-11-23 — #58 W5 v20 = PRODUCTION 2/3 (v19 promoted), ~4.9 min
**User's decision:** promote v19 (#57) to production.
**Created:** `WF/motion_W5_quality_v20.json` (copy in `PROJ/2 - files/workflows/ui_production/`), `build_W5_v20.py`, `W5_quality_v20_api.json`.
**v19 → v20:** same graph and values; base folder `motion/W5_v19/` → **`motion/production/`**, sparse attention `verbose` ON → OFF (log only), titles without "(v18: …)" notes, usage note rewritten (PRODUCTION 2/3, ~5 min, what makes it fast, license). **Check:** API diff v19 → v20 = only those; UI widgets and links equal to v19 except nodes 2, 231 and the note.
**ComfyUI (`WF/`):** added v20; removed the tests v17, v18, v19 (repo copies in `ui_tests/`; v17/v19 identical in content, v18 re-saved by ComfyUI with only an empty `widgets_values` on node 131). `ui_production/motion_W5_quality_v16.json` moved to `ui_tests/`. **`WF/motion_W5_quality_v16.json` left in place:** the user re-organized it in ComfyUI into subgraphs ("stage 1 - First frame setup" and three "New Subgraph") at 14:42; a copy is archived as `ui_tests/motion_W5_quality_v16_resaved-2026-11-23.json`. Backup of the removed files in the session scratchpad (`wf_removed_2026-11-23/`).
**Docs:** README (production table, step 5, flowchart ~5 min + klein KV, base settings: klein 9B KV / 2 MP + 2 MP / 4 steps CFG 1 / sparse attention, prompt note, Speed table v17–v20 + W6 row, notes, new image `docs/media/speed_v17_to_v20_frames.jpg`, models table + tree with `flux-2-klein-9b-kv-fp8` and the license note), CLAUDE.md (production flow, current state).

## 2026-11-23 — #57 W5 v19 run: 4.9 min and the first frame follows the skeleton
**Run** (the user, cold cache, default values): success, **291.8 s = 4.9 min** end to end (v17: 8.1, v16: 8.4, v9: 27.7). Outputs in `OUT/motion/W5_v19/caramel-tank-jeans_look-02/`.
**Log:** stage 1 klein 9B KV, 4 steps in **3 s** (v18: 15 s with the 4 MP product; v17: 3:05). The rest of the run is model loading/encoding (~1.3 min), video 8 steps 2:55 (sparse from step 3) and decode.
**Image:** the first frame now follows the skeleton (both arms down, no hand in the pocket), so the video follows the pose from frame 0 like v17. Garment faithful (knit, color, neckline, jeans, bag kept in the hand the whole video, sandals). The model is a bit larger in frame than in v17 (head and feet closer to the edges), whole body still visible. Face and curls at frame 60 comparable to v17.
**Comparison** (same folder): `side-by-side_skeleton_v17_v18_v19.mp4`, `frames_skeleton_v17_v18_v19.png`, `frame0_skeleton_product_v17_v18_v19.png`, `zoom_v17_vs_v19_f60.png`.
**Reading:** the 2 MP product + 2 MP skeleton + "do not copy the pose of image 1" fixed v18. v19 is a production candidate (~5 min, or ~5.7 min with the W6 upscale). License note: klein 9B (base and KV) is FLUX non-commercial.

## 2026-11-23 — #56 W5 v19 speed test: make the distilled first frame follow the skeleton
**Problem (#55):** the klein 9B KV first frame (v18) copied the pose and framing of the product photo instead of the skeleton.
**Created:** `WF/motion_W5_quality_v19.json` (copy in `ui_tests/`), `build_W5_v19.py`, `W5_quality_v19_api.json`.
**v18 → v19 (stage 1 inputs only):** product reference (node 107) **4 MP → 2 MP**; skeleton reference (node 110) **1 MP → 2 MP**; image prompt (node 104): added "Do not copy the pose of image 1: the arms, hands, legs, head position, body framing and size in the frame come only from the skeleton in image 2." and removed "camera" from "Keep the same face, hair, background, lighting and camera as image 1". Titles cleaned. Unchanged: klein 9B KV + FluxKVCache, 4 steps, CFG 1, seed, 1088×1920, stage 2. Base folder → `motion/W5_v19/`.
**Check:** UI JSON vs API JSON by script (values of nodes 2/104/107/110 equal; every other node and every link identical to the frontend-verified v18). The browser pane was in use by the user, so no `graphToPrompt()` this time. Not run (the user runs it).
**Expected:** first frame in the skeleton pose (arms down, no hand in the pocket), garment as faithful as v18, ~5 min end to end.

## 2026-11-23 — #55 W5 v18 run: 5.0 min, garment faithful, but the first frame ignores the skeleton
**Run** (the user, cold cache, default values): success, **299.4 s = 5.0 min** end to end (v17: 8.1 min). Outputs in `OUT/motion/W5_v18/caramel-tank-jeans_look-02/`.
**Log:** stage 1 klein 9B KV, 4 steps in **15 s** (v17: 28 steps in 3:05); model loads unchanged. Video 8 steps 2:57 (sparse from step 3, same as v17).
**Image:** the KV-distilled first frame copies the garment very well (knit texture, color, neckline, bag, sandals; arguably closer to the product photo than v17) **but ignores the skeleton (image 2): it reproduces the pose of the product photo** (right hand in the pocket, model larger in frame, like the product shot). Because frame 0 does not match pose frame 0, the video starts with the hand in the pocket and the ControlNet pulls the body into the skeleton pose only after ~1.5 s (frame 40 on it follows the skeleton like v17).
**Comparison** (same folder): `side-by-side_skeleton_v17_v18.mp4`, `frames_skeleton_v17_v18.png` (frames 0/12/40/80/123), `frame0_product_v17_v18.png`, `frame0_top_v17_v18.png`.
**Reading:** big speed win (stage 1 −2:50) but not usable as is: the first frame must follow pose frame 0. Next options: (a) skeleton reference stronger in the distilled model (e.g. skeleton first, higher resolution, prompt wording) or without the KV cache; (b) klein base with fewer steps (e.g. 12–16, smaller gain, keeps pose following).

## 2026-11-23 — #54 W5 v18 speed test: distilled first-frame model (FLUX.2 klein 9B KV, 4 steps)
**Goal:** stage 1 (klein 9B base, 28 steps, CFG 3.5 = 56 model passes, ~3.1 min) is now the largest block of the run. The user chose to test a distilled model.
**Model downloaded (user's go-ahead "Testar klein destilado"):** `flux-2-klein-9b-kv-fp8.safetensors` (9,818,935,984 bytes) → `models/diffusion_models/`, from https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-kv-fp8 (public; the plain distilled `FLUX.2-klein-9b-fp8` is gated and returned 401). It is the model of the official template `image_flux2_klein_9b_kv_image_edit`: distilled (4 steps, CFG 1) and trained for the **KV cache** of reference images. License: FLUX non-commercial, same as the klein 9B base already in use.
**Created:** `WF/motion_W5_quality_v18.json` (copy in `ui_tests/`), `build_W5_v18.py`, `W5_quality_v18_api.json`.
**v17 → v18 (stage 1 only):** node 100 `flux-2-klein-base-9b-fp8` → `flux-2-klein-9b-kv-fp8`; new node 131 `FluxKVCache` between the INT8 attention node 130 and the CFGGuider 116 (link 22 now 131→116, new link 89 130→131); CFGGuider cfg 3.5 → **1.0** (negative branch skipped); Flux2Scheduler 28 → **4** steps. Unchanged: prompts, seed, euler, flux2-vae, product 4 MP + skeleton 1 MP references, 1088×1920, all of stage 2 (= v17, incl. sparse attention). Base folder → `motion/W5_v18/`.
**Check:** the UI JSON loaded in the frontend; `graphToPrompt()` = the generator's API JSON (60 nodes). Not run (the user runs it).
**Expected:** stage 1 ~3.1 min → well under 1 min (~5.5 min end to end). Risk: the distilled model may copy the garment less faithfully than the base → compare frame0 v17 vs v18 closely (print, knit, bag, face).

## 2026-11-23 — #53 W5 v17 run: sparse attention works, small gain (~20 s)
**Run** (the user, cold cache, default values): success, **485.8 s = 8.1 min** end to end (v15/v16: 8.4 min). Outputs in `OUT/motion/W5_v17/caramel-tank-jeans_look-02/` (`frame0_00001_.png`, `video_00001_.mp4`).
**Log:** stage 1 FLUX 28 steps 3:05 (6.6 s/step, unchanged). Video 8 steps 3:10 (incl. ~28 s model init): steps 1–2 dense ("sigma outside the start/end window", start 0.2), steps 3–8 **sparse** ("sparse producer path: 63949 tokens, sinks (0, 190)/(183, 190)"). Sparse steps ≈ 21.5 s vs ≈ 30.6 s dense (**~30% faster per step**); the video stage gained ~25 s.
**Image:** `frame0` identical to v15/v16 pixel for pixel (sparse is only on the video model). Video frame 60 mean difference 5/255; face, curls, knit and bag unchanged to the eye. Comparison in the same folder: `side-by-side_v16_vs_v17.mp4`, `side-by-side_v16_vs_v17_zoom.mp4` (fixed crops: face, top), `zoom_v16_vs_v17_f60.png`.
**Reading:** no quality cost, but the gain is small because the video stage is now short (8 steps); the biggest remaining block is stage 1 (FLUX klein base 28 steps + CFG ≈ 3.1 min) and model loading (~1.5 min). Possible extra on the sparse side: start 0.0 (2 more sparse steps, ~15–20 s) or a higher tau.

## 2026-11-23 — #52 W5 v17 speed test: native block-sparse attention on the video model
**Goal:** cut the video stage (~3.6 min in v16) further with no visible change. Production stays W5 v16.
**Created:** `WF/motion_W5_quality_v17.json` (copy in `PROJ/2 - files/workflows/ui_tests/`), `build_W5_v17.py`, `W5_quality_v17_api.json`.
**v16 → v17 (one change):** new node 231 `BlockSparseAttention` ("Model Sparse Attention", native, `comfy_extras/nodes_sparse_attention.py`) between the INT8 attention node 230 and the ControlNet 214 (214 model: 230 → 231). Settings = node defaults: method **sol-attn** (training-free adaptive threshold), **tau 1.3**, start 0.2, end 1.0, min_tokens 12288, extra_tokens 256, sink_conditioning `exact_kv_and_rows` (text/audio/reference rows stay exact; H3-aware block patches); **verbose ON** so the server log shows which attention calls went sparse. Dense calls (first 20% of the schedule, short sequences) fall back to the INT8 backend of node 230. `sol_attn_is_available` = True on the RTX 4090 (checked). Base folder `motion/production/` → `motion/W5_v17/` (test). Usage note rewritten for the test.
**Check:** the UI JSON loaded in the frontend; `graphToPrompt()` = the generator's API JSON (59 nodes, same values and links). Not run (the user runs it).
**Expected:** video ~3.6 → ~2.5–3 min; compare v16 vs v17 side by side after the run.

## 2026-11-22 — #51 W6 v3 run on the fast W5 video + comparison of all versions
**W6 v3** (first run, default values): input `IN/motion/production/caramel-tank-jeans_look-02.mp4` (= v15 video, #50). No error, **47 s**. Outputs in `OUT/motion/production/caramel-tank-jeans_look-02/`: `video_2x_00001_.mp4` (1792×3200), `video_1080x1920_00001_.mp4`.
**Comparison** (same folder): `side-by-side_v15_vs_upscale.mp4`, `side-by-side_v15_vs_upscale_zoom.mp4` and `zoom_v15_vs_upscale_f60.png` (face + top, fixed crop). The upscale is clearly sharper (eyes, eyebrows, curls, knit texture) with no new artifacts → **the upscale still makes sense** with the fast W5 (fast flow ≈ 8.4 + 0.8 ≈ 9.2 min, output 1080×1920).
**All versions** (the user's request): `versions_v9_to_v16.mp4` (v9 | v12 | v13 | v14 | v15=v16 | v16 + upscale, labels with times).
**Repo media (`docs/media/`):** `speed_v9_to_v16.mp4` (2180 px wide, 1.0 MB), `speed_v9_to_v16.jpg` (frame 60), `upscale_zoom_v16.jpg`. README "Speed" section: image + video link, W6 row in the table, upscale note and zoom image.

## 2026-11-22 — #50 Upscale test input for the fast W5 (v15 video)
**User's request:** check whether the W6 upscale still makes sense with the fast W5. Created `IN/motion/production/caramel-tank-jeans_look-02.mp4` = copy of `OUT/motion/W5_v15/caramel-tank-jeans_look-02/video_00001_.mp4` (v15 = same graph as production W5 v16), which is exactly the default input of `motion_W6_upscale_v3` (name `caramel-tank-jeans_look-02`). W6 v3 will save to `OUT/motion/production/caramel-tank-jeans_look-02/` (video_2x 1792x3200, video_1080x1920). **Status:** ready, not run (first W6 v3 run).

## 2026-11-22 — #49 W6 v2 removed from ComfyUI again
**User's decision:** remove it. `WF/motion_W6_upscale_v2.json` (re-saved by the user at 12:39) had the same nodes, values and links as the archived copy; only node positions, groups and canvas view differed. Archived as `PROJ/2 - files/workflows/ui_tests/motion_W6_upscale_v2_resaved-2026-11-22.json` (the earlier archive `motion_W6_upscale_v2.json` is kept), then removed from `WF/` (backup in the session scratchpad). `WF/` now has only the 3 production workflows: `motion_W1_extract-pose_v3`, `motion_W5_quality_v16`, `motion_W6_upscale_v3`.

## 2026-11-22 — #48 W5 v16 = PRODUCTION 2/3 (v15 promoted)
**User's decision:** promote v15 (8.4 min end to end, #47) to production.
**Created:** `WF/motion_W5_quality_v16.json` (copy in `PROJ/2 - files/workflows/ui_production/`), `build_W5_v16.py`, `W5_quality_v16_api.json`.
**v15 → v16:** same graph and values; only the base folder `motion/W5_v15/` → **`motion/production/`** (node 2, title "Base folder (production)"), the ControlNet title without the "(v12: …)" note, a rewritten usage note (PRODUCTION 2/3, ~8.5 min, what makes it fast and how to turn each part off) and a clean generator header. **Check:** API diff v15 → v16 = only those; every API value, link and title matches the UI.
**ComfyUI (`WF/`):** removed `motion_W5_quality_v11` and the tests v12–v15 (only production stays). Archived copies: `ui_tests/` (v11 moved there from `ui_production/`; v12–v15 already there). v11 and v15 were byte-identical; v12–v14 in `WF/` had been re-saved by ComfyUI (same nodes, values and links; only formatting/canvas view). A backup of the removed `WF/` files is in the session scratchpad (`wf_removed_2026-11-22/`). `WF/` now has `motion_W1_extract-pose_v3`, `motion_W5_quality_v16`, `motion_W6_upscale_v3` — plus `motion_W6_upscale_v2`, saved again by the user at 12:39 and different from the archived copy (left untouched).
**Docs:** README (production table, step 5, flowchart ~8.5 min, base settings, new "Speed" section with the v9 → v16 table, bag lesson), CLAUDE.md (production flow, current state).

## 2026-11-22 — #47 W5 v15 run — 8.4 min end to end from a cold cache (v9: 27.7 min)
The user cleared ComfyUI's cache completely before running, so this is the real end-to-end time including model loads: **8 min 24 s** (504 s). Stage 1: 28 steps in **3 min 04 s** (6.6 s/step; v14: 4 min 53 s, 10.4 s/step → 1.6× faster). Video: 8 steps in **3 min 33 s** (~26 s/step, same as v14). The rest (~1.8 min) = model loads + decodes.
Outputs in `OUT/motion/W5_v15/caramel-tank-jeans_look-02/`: `video_00001_.mp4`, `frame0_00001_.png`, `side-by-side_v9_v14_v15.mp4`, `frame0_v14_vs_v15.png`, `frame0_zoom_v14_vs_v15.png` (face/top and torso crops), `body_v14-top_v15-bottom.png` (frames 10/40/70/110).
**Quality:** first frame practically identical to v14 (mean pixel difference 1.6/255): same face, curls, knit texture, V neck, jeans. Video differs a bit more (3.9/255 on average, because it starts from a slightly different first frame) but the face, garment, bag, motion and framing match frame by frame; no skeleton lines.
**Summary of the speed work (#39–#47):** 27.7 min (v9) → 14.3 (v12 turbo, lines) → ~14 (v13, lines fixed) → ~9.5 (v14, INT8 video) → **8.4 min (v15, INT8 image too)**, 3.3× faster, with the face slightly softer than v9 (8 vs 20 steps) and the bag now kept.
**Pending (user):** promote v15 to the production W5.

## 2026-11-22 — #46 W5 v15 — INT8 attention on the first frame (FLUX) too
**User's request:** optimize the first frame (now the slowest stage, ~5 min of v14's ~9.5 min).
**Created:** `WF/motion_W5_quality_v15.json` (copy in `PROJ/2 - files/workflows/ui_tests/`), `build_W5_v15.py`, `W5_quality_v15_api.json`.
| Node | v14 | v15 |
|---|---|---|
| **new** `ModelAttentionBackend` (130) "Attention (image): INT8 comfy kitchen" | — | between the FLUX `UNETLoader` (100) and the `CFGGuider` (116), `comfy kitchen attention` |
| Base folder (2) | `motion/W5_v14/` | **`motion/W5_v15/`** |
Everything else = v14 (INT8 attention on the video model too). One change only, so its effect on the first frame is measurable; the product reference stays at 4 MP (2 MP is the next lever if needed). The first frame changes slightly, so the video re-runs too: this run measures the **full time end to end**.
**Check:** API diff v14 → v15 = only the new node, the re-wired CFGGuider model input and the folder; UI from the v14 UI (+1 node, +1 link, link 22 now 130 → 116); every API value, link and title matches the UI.
**Expected:** first frame ~2.5–3.5 min (v14: 4 min 53 s); total ~7–8 min. **Status:** built, not run.

## 2026-11-22 — #45 W5 v14 run — INT8 attention: video 2.1× faster, same image
Ran without error: **4 min 36 s** (stage 1 from cache, same first frame as v12/v13; video 8 steps in **3 min 23 s**, ~25 s/step — v13: 7 min 02 s, ~53 s/step). Full run without cache ≈ 5 min (stage 1) + 3.4 min (video) + ~1 min (loads/decode) ≈ **~9.5 min** (v9: 27.7 min).
Outputs in `OUT/motion/W5_v14/caramel-tank-jeans_look-02/`: `video_00001_.mp4`, `frame0_00001_.png`, `side-by-side_v9_v13_v14.mp4`, `faces_v13-top_v14-bottom.png`, `body_v13-top_v14-bottom.png` (frames 10/40/70/110).
**Quality:** v14 is practically identical to v13 (same seed): mean absolute pixel difference 1.7/255 (max 2.8 mid-video); face, eyes, hair, garment, bag and motion match frame by frame; no skeleton lines.
**Conclusion:** INT8 attention is a free ~2× on the video stage. Now the first frame (FLUX, ~5 min) is the biggest stage. Next levers: INT8 attention on the FLUX model too (stage 1), native `BlockSparseAttention` on H3, product reference at 2 MP.

## 2026-11-22 — #44 W5 v14 — native INT8 attention (SageAttention-like, no install)
**User's request:** test SageAttention. **Finding:** no install needed. ComfyUI 0.46 ships `ModelAttentionBackend` ("Model Attention Backend", experimental, `comfy_extras/nodes_model_advanced.py`) with the option **`comfy kitchen attention`** = quantized INT8 attention from `comfy_kitchen` (same idea as SageAttention). Checked: `comfy_kitchen.int8_attention_is_available()` is true on the 4090 and the option is listed by `/object_info`. SageAttention itself (pip `triton-windows` + `sageattention`, flag `--use-sage-attention`) was NOT installed. Also found, not used yet: native `BlockSparseAttention` ("Model Sparse Attention", method `sol-attn`, training-free, H3-aware) — a possible next test.
**Created:** `WF/motion_W5_quality_v14.json` (copy in `PROJ/2 - files/workflows/ui_tests/`), `build_W5_v14.py`, `W5_quality_v14_api.json`.
| Node | v13 | v14 |
|---|---|---|
| **new** `ModelAttentionBackend` (230) "Attention: INT8 comfy kitchen (like SageAttention)" | — | between the model switch (206) and the ControlNet (214), `attention` = `comfy kitchen attention` |
| Base folder (2) | `motion/W5_v13/` | **`motion/W5_v14/`** |
Only the H3 video model is patched; FLUX stage 1 is untouched, so the first frame is the same as v12/v13 (comes from cache) and the comparison isolates the attention change. Setting the node to `pytorch attention` = exactly v13.
**Check:** API diff v13 → v14 = only the new node, the re-wired ControlNet model input and the folder. UI built from the v13 UI (+1 node, +1 link, link 43 now 230 → 214); every API value, link and title matches the UI. Also confirmed through `/history` that the v12 and v13 runs used exactly the generator values (the stale `widgets_values_named` copy in the UI JSON is ignored by the frontend; fixed in v14 anyway).
**Expected:** video 8 steps faster than v13's 7 min (typical INT8-attention gain 20–40%). **Status:** built, not run.

## 2026-11-22 — #43 W5 v13 run — skeleton lines gone; candidate for the fast production version
Ran without error: **8 min 05 s** (stage 1 came from cache — same first frame as v12; video 8 steps in **7 min 02 s**, ~53 s/step). Full run without cache ≈ v12's 14.3 min (stage 1 ~5 min + video ~7 min + loads).
Outputs in `OUT/motion/W5_v13/caramel-tank-jeans_look-02/`: `video_00001_.mp4`, `frame0_00001_.png`, `side-by-side_v9_v12_v13.mp4` (SKELETON | v9 | v12 | v13), `faces_v13-top_v9-bottom.png` (frames 10/40/70/110), `pose_check_skeleton_v9_v13.png` (frames 10/40/70/100/123). `side-by-side_v9_v12_v13_zoom.mp4` / `zoom_v9_v12_v13.png` are also there, but the crop follows the skeleton head, and v13 frames the model larger than the skeleton, so its face panel is off-center — use the faces PNG instead.
**Result:**
- **No skeleton lines** on body or clothes (v12's defect is gone with ControlNet strength 0.6 / end 0.5).
- **Motion follows the pose** (step, crossed leg at frame 70, arm positions); slightly freer than v9.
- **Face:** natural eyes, consistent identity, a little softer than v9 (8 vs 20 steps).
- **Garment:** faithful (color, knit texture, V neck, jeans seams).
- **The bag stays in the hand** for the whole video (v9 lost it — an old lesson).
- Framing: the model is a bit larger in frame than in v9 (follows the first frame more than the skeleton's scale).
**Pending (user):** approve v13 as the fast production W5 (then: promote to `motion_W5_quality_v14` with output `motion/production/`), or try another tweak.

## 2026-11-22 — #42 W5 v13 — v12 with a weaker ControlNet
**User's decision** (between "official ref2v LoRA" and "weaker ControlNet"): weaker ControlNet, keeping the 8-step fl2v LoRA.
**Created:** `WF/motion_W5_quality_v13.json` (copy in `PROJ/2 - files/workflows/ui_tests/`), `build_W5_v13.py`, `W5_quality_v13_api.json`.
| Node | v12 | v13 | Why |
|---|---|---|---|
| MiniMaxH3FunControlNetApply (214) strength | 1.0 | **0.6** | v12 painted the skeleton lines on the body/clothes (#41) |
| MiniMaxH3FunControlNetApply (214) end_percent | 0.7 | **0.5** | with 8 steps, control stops after step 4 instead of ~6 |
| Base folder (2) | `motion/W5_v12/` | **`motion/W5_v13/`** | separate test output |
Everything else = v12 (turbo 8 steps ON, first frame 1088×1920). **Check:** API diff v12 → v13 = only these values; UI built from the v12 UI (same links), every API value/title matches the UI widgets.
**Risk:** motion may follow the reference pose less closely. **Expected time:** ~14 min. **Status:** built, not run. Pose `look-02` (v9 skeleton) already in the catalog.

## 2026-11-22 — #41 W5 v12 run — 2× faster, but skeleton lines painted on the body; NOT approved
Ran without error (default values, product `caramel-tank-jeans`, pose `look-02` = v9 skeleton): **14 min 19 s** in total (v9: 27 min 40 s). Stage 1: 28 steps in 4 min 53 s (10.4 s/step at 1088×1920; v9: 15.7 s/step at 1536×2720 — only ~1.5× faster, the 4 MP product reference keeps the token count high). Stage 2: 8 steps in 7 min 38 s (~57 s/step, same cost per step as v9; LoRA loaded, 208 patches). Remaining ~1.5 min = model loads + decode.
Outputs in `OUT/motion/W5_v12/caramel-tank-jeans_look-02/`: `frame0_00001_.png`, `video_00001_.mp4`, `side-by-side_v9_vs_v12.mp4` (SKELETON | v9 | v12, `W4_compare_versions.py`), `side-by-side_v9_vs_v12_zoom.mp4` and `zoom_v9_vs_v12.png` (face + torso, crop following the skeleton head; script `zoom_cmp.py` in the session scratchpad).
**Result:**
- First frame: clean, faithful garment and face (the 1088×1920 frame is fine).
- Video: **pale skeleton lines drawn over the body and clothes** from the first frames on (shoulder line, a "V" on the chest, lines down the arms and the jeans) — the same kind of defect as v8. Face and garment otherwise comparable to v9; motion follows the pose.
**Diagnosis (hypothesis):** the `fl2v` 8-step LoRA was trained for first/last-frame video without ControlNet; with only 8 steps and ControlNet strength 1.0 until 70%, the distilled model copies the control video almost literally into the pixels. The official `video_minimax_h3_fun_controlnet_union` template pairs the ControlNet with the `ref2v` 4-step LoRA instead.
**Decision pending (user):** next test candidates — (a) ControlNet strength 0.5–0.7 and/or end 0.5 with the same LoRA; (b) the ref2v 4-step LoRA (official pairing) at 6–8 steps; (c) LoRA strength ~0.6 with 12 steps.

## 2026-11-22 — #40 Catalog pose `look-02` created (fix for W5 v12 "Invalid input")
**Error:** first run of W5 v12 failed on validation: `Catalog POSE (motion/poses/<pose>/pose.mp4) - file` — invalid input. Cause: `IN/motion/poses/look-02/pose.mp4` did not exist (W1 v3 has never run, so the English catalog was empty). `LoadVideo` accepts subfolder paths (its `validate_inputs` only checks that the file exists), so no workflow change is needed.
**Created:** `IN/motion/poses/look-02/pose.mp4` = copy of `OUT/motion/W5_v9/regata-caramelo-jeans_look-02_q9/pose_sem-rosto_00001_.mp4` (576×1024, 124 frames, 24 fps) — the exact skeleton the approved v9 video used, so v9 × v12 is a fair comparison. No `original.mp4` yet (`catalog.py compare` needs it; W1 v3 will create the full catalog entry later).

## 2026-11-22 — #39 W5 v12 — speed test (turbo 8 steps + smaller first frame)
**User's request:** cut the ~27 min per video a lot while losing little quality. Research (web): the standard levers are step-distilled LoRAs (turbo/lightning), attention kernels (SageAttention, torch.compile), step caching (TeaCache/EasyCache) and low-res + upscale. For H3, a public benchmark measured the official 8-step turbo at 2.1× faster with near-identical quality, and 4 steps clearly worse; the ComfyUI docs call the 4-step ref2v LoRA (the one in v11) weaker on references. Low-res + upscale was ruled out: our own tests showed 704×1248 deforms the face and upscaling does not fix it.
**Created:**
- `WF/motion_W5_quality_v12.json` (copy in `PROJ/2 - files/workflows/ui_tests/`), `PROJ/2 - files/workflows/build_W5_v12.py`, `W5_quality_v12_api.json`.
**Changes vs v11 (everything else identical):**
| Node | v11 | v12 | Why |
|---|---|---|---|
| Turbo LoRA (204) | `minimax_h3_ref2v_turbo_4step_v0.1` | **`minimax_h3_fl2v_turbo_8step_v1.0`** (already on disk, lightx2v) | official 8-step LoRA; 8 steps keep quality, the 4-step one is weak on references |
| Turbo switch (205) | OFF | **ON** | fast by default; OFF = exactly v11 (20 steps, no LoRA) |
| Steps (turbo) (208) | 4 | **8** | LoRA is trained for 8 |
| Stage 1 frame (118/119) | 1536×2720 (~4.2 MP) | **1088×1920 (~2.1 MP)** | the video is 896×1600; ~2× fewer image tokens |
| Base folder (2) | `motion/production/` | **`motion/W5_v12/`** | test output kept apart from production |
Sampler/scheduler kept at `res_multistep` + `simple` (same as the official `video_minimax_h3_i2v` template that ships this LoRA). Product reference stays at 4 MP (garment fidelity).
**Risk:** the 8-step LoRA was trained on fl2va; on ref2va it is untested here (third parties report it works). If the garment or face degrade: try the LoRA at strength 0.8 or 10 steps, or fall back to turbo OFF.
**Check:** API diff v11 → v12 = only the values above; UI built from the v11 UI (same links), every API value/title matches the UI widgets. ComfyUI was not running, so `graphToPrompt()` was not checked in the frontend.
**Expected time:** ~10 min (stage 1 ~2–3 min, video 8 × ~52 s ≈ 7 min). **Status:** built, not run. Next: run with `caramel-tank-jeans` + `look-02` and compare side by side with the approved v9 video.
**Later options (not done):** SageAttention (`--use-sage-attention`; needs `triton-windows` + `sageattention` pip packages — awaiting authorization; H3 head_dim 128 is compatible), native `EasyCache` on the 20-step path, distilled FLUX.2 klein 9B for stage 1 (download).

## 2026-11-22 — #38 Everything in English (to share the project publicly, e.g. on Reddit)
**User's request:** translate the whole project to English.
**Docs:** `README.md` rewritten in English. `HISTORICO.md` → **`CHANGELOG.md`** (full translation of #1–#37, done by a sub-agent; identifiers, paths and node titles kept as they were at the time). `1 - AI instructions/pesquisa-olhos-pose-h3.md` → `research-eyes-pose-h3.md`, `prompt_pesquisa_olhos_H3.md` → `prompt-research-eyes-h3.md`, `3 - Assets/referencias de pose/LEIA-ME.md` → `README.md`. `CLAUDE.md` rewritten in English (adds: talk to the user in Portuguese, keep the repo in English). The Portuguese originals were removed from the repo (still in git history).
**New production versions (English labels and folders; same graph and values — checked: API values differ only in the folder/name defaults below, and each UI's `graphToPrompt()` matches its generator after reloading from disk):**
| Before (Portuguese) | After (English) | What changed |
|---|---|---|
| `motion_W1_extrai-pose_v2` / `build_W1_v2.py` | **`motion_W1_extract-pose_v3`** / `build_W1_v3.py` / `W1_extract-pose_v3_api.json` | titles, groups, note; output `motion/catalogo/` → `motion/catalog/` |
| `motion_W5_qualidade_v10` / `build_W5_v10.py` | **`motion_W5_quality_v11`** / `build_W5_v11.py` / `W5_quality_v11_api.json` | titles, groups, note; output `motion/producao/` → `motion/production/`; default name `regata-caramelo-jeans_look-02` → `caramel-tank-jeans_look-02`; product `motion/W2/produtos/regata-caramelo-jeans_frente.png` → `motion/products/caramel-tank-jeans_front.png` (copy of the same file, created in `IN/`) |
| `motion_W6_upscale_v2` / `build_W6_v2.py` | **`motion_W6_upscale_v3`** / `build_W6_v3.py` / `W6_upscale_v3_api.json` | titles, groups, note; input/output `motion/producao/` → `motion/production/`; KSampler seed kept at 42 "fixed" |
**ComfyUI:** only the 3 English workflows remain in `WF/`. The Portuguese W1 v2 / W5 v10 / W6 v2 were archived in `2 - files/workflows/ui_tests/` (byte-compared, then removed from `WF/`). W6 v2 in `WF/` had been re-saved by the user when they ran the upscale (input `video_00001_.mp4`, moved nodes); that saved version is the one archived. Folders renamed in the repo: `ui_testes/` → `ui_tests/`, `ui_producao/` → `ui_production/` (now holds the English v3/v11/v3).
**Scripts:** `catalogo.py` → **`catalog.py`** (commands `pose`, `upscale`, `compare`, `list`; folders `catalog/`, `production/`; replaced files kept as `.previous-<date>`; comparison file `compare.mp4`). `W4_lado_a_lado.py` → **`W4_side_by_side.py`** (labels ORIGINAL | SKELETON | GENERATED). `W4_compara_versoes.py` → **`W4_compare_versions.py`** (`--height`, `--altura` still accepted). `.gitignore` comments translated, `*.previous-*` added.
**Media (`docs/media/`):** re-rendered with English labels: `example_4-stages.gif` / `.mp4` (was `exemplo_4-etapas`), `pipeline.jpg`, `v8_vs_v9.jpg` (was `v8_x_v9.jpg`), `upscale_zoom.jpg` (was `zoom_upscale.jpg`); renamed `face_v7_vs_v9.jpg`, `body_v7_vs_v9.jpg`.
**Kept in Portuguese:** archived test workflows and old generators (`ui_tests/`, `build_W*` up to v10/v2), and the folder `3 - Assets/referencias de pose/` (it is the working folder of the Claude session; can be renamed later). Existing outputs in `OUT/motion/catalogo/` and `OUT/motion/producao/` were not moved.
**Status:** the English workflows have not run yet.

## 2026-11-22 — #37 Repository made public
At the user's request (they will share it with other people): https://github.com/LuanVelo/fashion-pose-to-video went from private to **public**. Same content as #36 (no models, no reference videos).

## 2026-11-22 — #36 Project on GitHub (private) + README
**Created:** git repository in `PROJ/` (branch `main`) and the repository https://github.com/LuanVelo/fashion-pose-to-video (the user's request; private by default, can be made public in Settings).
- `README.md`: what it is, Mermaid flowchart, the 3 production workflows, step by step, requirements, **table of the 12 models with original links** (the same ones as the official ComfyUI templates) and the `models/` tree, input/output folders, base configuration, results and lessons learned with images.
- `docs/media/`: `exemplo_4-etapas.gif` (960 px, 12 fps, shown directly in the README), `exemplo_4-etapas.mp4` (2400 px, 2.3 MB), `pipeline.jpg`, `rosto_v7_x_v9.jpg`, `corpo_v7_x_v9.jpg`, `v8_x_v9.jpg`, `zoom_upscale.jpg`.
- `.gitignore`: models (`*.safetensors` etc.), videos in `3 - Assets/` (third-party content), `*.anterior-*`.
- `3 - Assets/referencias de pose/LEIA-ME.md`: explains that the videos are not uploaded.
**Not uploaded:** models, reference videos, ComfyUI outputs (only the examples in `docs/media`).
**From here on:** every change logged here becomes a commit + push.

## 2026-11-22 — #35 4-stage comparison + options in W4_compara_versoes.py
**Changed:** `PROJ/2 - files/workflows/W4_compara_versoes.py` — before: height = tallest video and number of frames = from the 1st video → after: options `--altura=N` and `--frames=N` (without them, same as before). Reason: 4 panels at 1920 px would exceed 4,300 px in width (many players can't play it); and the original has 150 frames, the others 124.
**Created:** `OUT/motion/producao/regata-caramelo-jeans_look-02/lado-a-lado_4-etapas.mp4` (3634×1644, 124 frames, 24 fps, no audio): 1 ORIGINAL (`catalogo/_teste_B4-P13/original_00001_.mp4`) | 2 ESQUELETO (skeleton; v9 `pose_sem-rosto_00001_`) | 3 GERADO (generated) 896x1600 (v9 `video_00001_`) | 4 SUPER-RESOLUÇÃO (super-resolution) 1080x1920 (W6 v2). Panels at 1600 px (native height of the generated video).
**No workflow changed.**

## 2026-11-22 — #34 W6 v2 run with the v9 video — good upscale
Run by the user with input `IN/video_00001_.mp4` (uploaded through the UI; identical to `OUT/motion/W5_v9/regata-caramelo-jeans_look-02_q9/video_00001_.mp4`). **0.8 min**, no error. Outputs in `OUT/motion/producao/regata-caramelo-jeans_look-02/`: `video_2x_00001_.mp4` (1792×3200) and `video_1080x1920_00001_.mp4`.
**Check:** `zoom_upscale.png` in the same folder (frame 60, face and tank top, original × 2x).
- Face: much sharper (eyelashes, eyebrows, lips, hair); eyes are still correct (the v7 defect doesn't exist in v9, so the upscale has nothing to amplify).
- Fabric: knit texture of the tank top well defined (the product is knitwear, so it is consistent), denim and seams more defined.
- Side effect: slightly more contrast and saturation on the skin and darker eyebrows. If it bothers: `detail` 0.7 in VSR Decode (that would be W6 v3).
**Side by side (the user's request: every comparison becomes a simultaneous video):** `lado-a-lado_upscale.mp4` (full frame, 896x1600 x 1080x1920, via W4_compara_versoes.py) and `lado-a-lado_upscale_zoom.mp4` (face and tank top zoomed in, crop following the skeleton's nose with a 9-frame moving average), in the same folder.
**Conclusion (my assessment; waiting for the user):** v9 + W6 v2 works as a complete pipeline. No workflow changed.

## 2026-11-22 — #33 Production pipeline in 3 workflows + ComfyUI cleanup
**The user's request:** catalog with ~4 poses → separate pose extraction from generation. 3 production workflows in ComfyUI; tests archived in the project and removed from ComfyUI.
**Created (generators and API in `PROJ/2 - files/workflows/`; UI in `WF/` with a copy in `ui_producao/`; all three checked: UI's API = generator, reloaded from disk):**
- `motion_W1_extrai-pose_v2` (`build_W1_v2.py`, `W1_extrai-pose_v2_api.json`). Before (v1) → after: skeleton with face, native fps, clip range in frames, SDPose on every frame → **no face and with head (same as W5 v9), clip range in seconds converted using the video's fps (`ComfyMathExpression` round(a*b)), resamples to 124 frames before SDPose, saves at 24 fps**; original saved with the same 124 frames (no audio). Default duration 5.2 s (the UI rounds to 0.1). Same output: `OUT/motion/catalogo/<pose>/`.
- `motion_W5_qualidade_v10` (`build_W5_v10.py`, `W5_qualidade_v10_api.json`). Before (v9) → after: LoadVideo of the original video + SDPose (nodes 210, 230–237) and LoadImage `pose-1.png` (109) → **LoadVideo `motion/poses/<pose>/pose.mp4` (210) + `ImageFromBatch` index 0 (240) as the first-frame pose**; output `motion/W5_v9/` → **`motion/producao/<nome>/`**. Everything else identical (end 0.7, 896×1600, seeds). Expected difference vs v9: the first-frame pose now comes without face points (the W1 v1 pose-1.png had them) and pose.mp4 goes through video compression.
- `motion_W6_upscale_v2` (`build_W6_v2.py`, `W6_upscale_v2_api.json`). Before (v1) → after: input `motion/W6/...` and output `motion/W6_v1/` → **input `motion/producao/<nome>.mp4`, output `motion/producao/<nome>/`**; KSampler seed fixed at 42 ("fixed"; the front end randomized it on open). Same quality.
- `catalogo.py`: `pose <pose>` (OUT/catalogo → IN/motion/poses/<pose>/pose.mp4, original.mp4, keyframes), `upscale <nome>` (OUT/producao/<nome>/video_* → IN/motion/producao/<nome>.mp4), `comparativo <nome> <pose>` (W4 → OUT/producao/<nome>/comparativo.mp4), `lista`. Doesn't delete; a replaced file becomes `.anterior-<data>`.
**Moved (copied, checked byte by byte with `cmp` and removed from `WF/`):** `motion_W1_extrai-pose`, `motion_W2_pose-em-imagem`, `motion_W3a_anima-h3`, `motion_W5_qualidade_v1`…`v9`, `motion_W6_upscale_v1` → `PROJ/2 - files/workflows/ui_testes/`. Also removed the helper folders `user/default/motion_api/` and `tmp_api/` (identical to the project's API copies). Workflows from other projects (vovo, h3, rioopen) were not touched.
**Status:** none of the 3 has run yet.

## 2026-11-22 — #32 v9 comparison + project presentation page
**Created:** `OUT/motion/W4/regata-caramelo-jeans_look-02_q9_lado-a-lado.mp4` (1480×904, 124 frames, 24 fps, with audio), via `W4_lado_a_lado.py` with original = `OUT/motion/catalogo/_teste_B4-P13/original_00001_.mp4`, skeleton and video from W5 v9.
**Created:** a page (private artifact) explaining the project, with the comparison, the pipeline, the workflows, the v9 configuration, the v1→v9 history, the face problem, the lessons learned and next steps: https://claude.ai/artifact/MSZTy9bCannn73yKp5SSrC . Source and images in the session scratchpad.
**No workflow changed.**

## 2026-11-22 — #31 W5 v9 approved as the production base
**The user's decision:** v9 (`WF/motion_W5_qualidade_v9.json`, `PROJ/2 - files/workflows/build_W5_v9.py`) replaces v7 as the base. Before → after: base v7 (ControlNet end 1.0) → **v9 (end 0.7)**. Reason: better eyes during head turns without losing clothing, motion or time (#30). No workflow file changed; v7 and v8 stay as history. Next versions start from v9.

## 2026-11-22 — #30 W5 v9 run — better eyes, clothing and motion same as v7
Ran without error: **27 min 40 s** (frame0 in ~7 min; video ~20 min). Outputs in `OUT/motion/W5_v9/regata-caramelo-jeans_look-02_q9/`: `video_00001_.mp4`, `frame0_00001_.png`, `pose_sem-rosto_00001_.mp4`.
**Check** (script `confere_v9.py` in the scratchpad; run only after the render finished): `corpo.png` (frames 0/30/60/90/123) and `rosto.png` (12 frames, crop following the skeleton's nose), v7 `_00002_` (end 1.0) × v9 (end 0.7), same seed and product. Both in the output folder.
**Result:**
- Motion: poses identical to v7 in all 5 frames → releasing the last 30% did not lose the motion.
- Clothing: caramel tank top and jeans faithful, same as v7.
- Face: in v7, frames 44–77 (head turning) have one eye more closed/asymmetric; in v9 the eyes stay open, symmetric and in place in all 12 sampled frames. Eyebrows and features closer to frame0.
- Limitation: 12 of 124 frames evaluated; the full video still needs to be watched.
**Conclusion:** `end_percent 0.7` improves the eye at no cost in clothing, motion or time. Candidate for the new base in place of v7. If a wrong eye still shows up in the full video: test end 0.6.

## 2026-11-22 — #29 W5 quality v9 (head back + ControlNet end_percent 0.7)
**Reason:** step A of the research `PROJ/1 - AI instructions/pesquisa-olhos-pose-h3.md`. The skeleton's head (from the original video) doesn't fit the generated face and the ControlNet pulls the eyes; removing the head (v8) broke everything. Hypothesis: the early steps lock layout/motion and the late ones do the face detail → releasing the ControlNet in the last 30% lets the face follow the first frame. Checked in the code (`comfy_extras/nodes_minimax_h3.py`): `start_percent`/`end_percent` exist in `MiniMaxH3FunControlNetApply` ("advanced" fields in the UI). Installed patch = Union v1.
**Created (v7 and v8 untouched):** `WF/motion_W5_qualidade_v9.json` (started from v8 in the UI, groups kept, note rewritten), `PROJ/2 - files/workflows/build_W5_v9.py` and `W5_qualidade_v9_api.json` (checked: UI's API = generator).

**Differences v7 → v9** (same product as test #26):
| Node | v7 (_00002_, test #26) | v9 |
|---|---|---|
| Test name (1) / Folder (2) | regata-rosa_look-02_q7 / motion/W5_v7/ | regata-caramelo-jeans_look-02_q9 / motion/W5_v9/ |
| ControlNet (214) `end_percent` | 1.0 | **0.7** (strength 1.0, start 0) |
| SDPoseDrawKeypoints (234) | draw_face=False, draw_head=True | same (v8 had draw_head=False) |

Kept 124 frames (not a short clip) to compare directly with `OUT/motion/W5_v7/regata-rosa_look-02_q7/video_00002_.mp4` (same product, same seed) without having to run a new baseline.
**Evaluate:** eyes (position/cross-eyed), clothing fidelity, motion fidelity. Next in the matrix if needed: end 0.6; strength 0.8/end 1.0; strength 0.8/end 0.7.
**Output:** `OUT/motion/W5_v9/regata-caramelo-jeans_look-02_q9/`. **Estimated time:** ~27 min. **Status:** built, not run.

## 2026-11-22 — #28 W5 v8 run — FAILED: headless skeleton became a "drawing" on the clothes
Ran without technical error: **26 min 23 s** (Stage 1 7 min 19 s at 15.7 s/step; video 17 min 29 s at 52.4 s/step). Outputs in `OUT/motion/W5_v8/regata-caramelo-jeans_look-02_q8/`: `video_00001_.mp4`, `pose_sem-cabeca_00001_.mp4`, `frame0_00001_.png`.
**Result:** the skeleton lines were drawn ON THE CLOTHES throughout the video — a bar across the shoulders, lines from the neck to the hip on the tank top, vertical seams on the jeans and translucent "sleeves" following the arms. Face ok, but the video is unusable.
**Likely cause:** the Fun ControlNet *union* infers the control type from the image. Without a head, the figure no longer looks like a pose skeleton and is read as an edge/line map (canny/lineart), so the model copies the lines as contours.
**Lesson:** the head has to stay in the skeleton (`draw_head=True`). For the eye, adjust ControlNet strength/duration, not the drawing.
Comparison: scratchpad `v8_check.png` (sent in the chat).

## 2026-11-21 — #27 W5 quality v8 (ControlNet skeleton WITHOUT head)
**Reason (analysis of the cross-eyed/misplaced eye):** overlaying the skeleton on the video, in the ORIGINAL the eye/nose points fit exactly; in the GENERATED video the face sits lower and is larger — the "eye" points land on the eyebrows and the "nose" between the eyes. H3 receives conflicting signals (first frame/ref say one eye height, ControlNet at strength 1.0 forces another) and in some frames the eye slips or misaligns. The mismatch originates in Stage 1 (Klein doesn't place the head exactly on the points) and in the difference in proportions between people. Analysis image: scratchpad `esq_original_vs_gerado.png` (sent in the chat).
**Created (v7 untouched):** `WF/motion_W5_qualidade_v8.json` (started from v7 in the UI, groups and note kept), `PROJ/2 - files/workflows/build_W5_v8.py` and `W5_qualidade_v8_api.json` (checked: UI's API = generator).

**Differences v7 → v8:**
| Node | v7 | v8 |
|---|---|---|
| Test name (1) / Folder (2) | regata-rosa_look-02_q7 / motion/W5_v7/ | regata-caramelo-jeans_look-02_q8 / motion/W5_v8/ |
| Product (5) | motion/W2/produtos/regata-rosa_frente.png | motion/W2/produtos/regata-caramelo-jeans_frente.png |
| SDPoseDrawKeypoints (234) `draw_head` | True | **False** (no eyes/nose/ears; body, hands and feet the same) |
| Pose prefix (235) | /pose_sem-rosto | /pose_sem-cabeca |

**Risk:** the head turn from the original video is no longer enforced (only neck/shoulders guide). If head motion is lost → alternative: head on + ControlNet `end_percent` 0.5.
**Compare with:** `OUT/motion/W5_v7/regata-rosa_look-02_q7/video_00002_.mp4` (same product, same seed). **Status:** built, not run.

## 2026-11-21 — #26 W5 v7 with a new product (caramel tank top + jeans) — replicability
**No workflow change:** only the product photo was swapped (`IN/image (2).png`, 1920×2720; organized copy in `IN/motion/W2/produtos/regata-caramelo-jeans_frente.png`). The test name was NOT changed → outputs `_00002_` in `OUT/motion/W5_v7/regata-rosa_look-02_q7/` (`frame0_00002_.png`, `video_00002_.mp4`, `pose_sem-rosto_00002_.mp4`).
**Time:** 27 min 13 s in total (video 17 min 22 s, ~52 s/step; stage 1 redone with the new product).
**Created:** `check_caramelo_corpo.png` (product | frame0 | frames 0/30/60/90/123) and `zoom_rosto_caramelo.png`, in the same folder.
**Assessment:**
- Caramel knit tank top, blue wide-leg jeans and black flip-flops: **faithful** throughout the video. The neckline came out more U-shaped than V. Jeans with some odd dark stains in a few frames.
- **Suede tote bag: appears in frame0, but DISAPPEARS in the video from frame 0** (the skeleton has no bag and the hand motion doesn't hold it). The video background also came out grayer than frame0.
- Face: natural and stable, without the artifacts of the previous model; curly hair well preserved. Identity changes a bit relative to the product (already in frame0).
- **Conclusion:** the pipeline is replicable for clothing; hand-carried accessories (bag) are not kept.

## 2026-11-21 — #25 W6 v1 run — upscale ok, but keeps the face artifacts
Ran and saved `OUT/motion/W6_v1/regata-rosa_look-02_q7/video_2x_00001_.mp4` (1792×3200) and `video_1080x1920_00001_.mp4`. Comparison zoom (v7 × upscale): sharper, but the v7 eye/eyelid defects remain — upscaling doesn't fix the face; the problem is in the generation (H3 at 896×1600).
Ideas noted (not done): a 2nd H3 pass at 1088×1920 with partial denoise over v7 (need to confirm support in the native nodes); a close-up face reference as a 2nd ref.

## 2026-11-21 — #24 W6 video upscale v1 (RelayVSR x2, local)
**Reason:** take the v7 video (896×1600) to 1080p/2K without regenerating, running locally.
**Downloaded (authorized by the user):** `models/diffusion_models/relayvsr_x2_lightx2v_int8_convrot.safetensors` (4.81 GB) and `models/vae/relayvsr_flash_vae_x2_fp32.safetensors` (122 MB), from Comfy-Org/RelayVSR. x2 pair retrained by LightX2V to come after H3.
**Created:** `WF/motion_W6_upscale_v1.json`, `PROJ/2 - files/workflows/build_W6.py` and `W6_upscale_v1_api.json`. Base: official template `utility_relayvsr_video_x2_upscale` (subgraph expanded into native nodes).
**Input:** `IN/motion/W6/regata-rosa_look-02_q7.mp4` (copy of `OUT/motion/W5_v7/regata-rosa_look-02_q7/video_00001_.mp4`).
**Flow:** LoadVideo → GetVideoComponents → RelayVSRConditioning → KSampler (1 step, cfg 1, euler/simple, seed 42) → VSRDecode (detail 1.0) → CreateVideo (audio and fps from the input) → saves `video_2x` (1792×3200) + ImageScale lanczos crop center → saves `video_1080x1920`.
**Output:** `OUT/motion/W6_v1/<nome>/`. **Adjustment if it invents detail:** lower the VSR Decode `detail` (e.g. 0.7) → that would be v2.
**Status:** built, not run.

## 2026-11-21 — #23 W5 v7 run — faithful clothing, better face; 18.6 min
Ran without error: **18 min 38 s** in total (video 20 steps in 17 min 10 s, **~51.5 s/step**, fit in VRAM, without the v6 offload). Outputs in `OUT/motion/W5_v7/regata-rosa_look-02_q7/`: `video_00001_.mp4` (896×1600, 124 frames), `pose_sem-rosto_00001_.mp4`, `frame0_00001_.png`.
**Created:** `comparativo_v5_v6_v7.mp4` (3 videos side by side, via `W4_compara_versoes.py`) and `zoom_rosto_v5_v6_v7.png` (face at frames 0/40/82/123 + input), in the same folder.
**Assessment:**
- Clothing: **faithful** in every frame (pink V-neck tank top, white pants, red striped shirt tied at the waist, sandal) — unlike v6.
- Face: more natural and stable than in v5 (704×1248); still a bit less detailed than in v6 (1088×1920). The head turn (frame ~82) comes out coherent.
- **Conclusion:** 896×1600 is the best local balance so far (quality × fidelity × time).

## 2026-11-21 — #22 W5 quality v7 (video at 896×1600)
**Reason:** find the middle ground between v5 (704×1248: faithful clothing, deformed face) and v6 (1088×1920: good face, swapped clothing, 59 min).
**Created (v1–v6 untouched):** `WF/motion_W5_qualidade_v7.json` (started from v6), `PROJ/2 - files/workflows/build_W5_v7.py` and `W5_qualidade_v7_api.json`.

**Differences v6 → v7:**
| Node | v6 | v7 |
|---|---|---|
| Test name (1) / Folder (2) | …_q6 / motion/W5_v6/ | …_q7 / motion/W5_v7/ |
| MiniMaxH3ReferenceToVideo (216) width × height | 1088 × 1920 | **896 × 1600** (~1.4 MP) |

Everything else identical (frame 1536×2720 flux2-vae, skeleton without face, 20 steps, ref max, fp16 video VAE, seed 20261121).
**Estimated time:** 20–30 min (not measured). **Status:** built, not run.

## 2026-11-21 — #21 W5 v6 run — natural face, but the CLOTHING changed; 59 min
No memory error, but **59 min 24 s** (20 steps at ~180 s/step, versus ~25 s at 704×1248 — a sign of VRAM-to-RAM offload). Outputs in `OUT/motion/W5_v6/regata-rosa_look-02_q6/`: `video_00001_.mp4` (1088×1920, 124 frames), `pose_sem-rosto_00001_.mp4`, `frame0_00001_.png`.
**Created:** `comparativo_v5_x_v6.mp4`, `zoom_rosto_v5_x_v6.png` in the same folder.
**Assessment:**
- **Face: much better** — natural, real expressions, without the deformation of v1–v5. Confirms the face problem was a lack of pixels.
- **Clothing: serious regression** — from frame 0 the tank top turned into a **long-sleeve crew-neck sweater**, and the tied striped shirt turned into a **striped skirt** over the pants. H3 ignored the first frame (AddGuide) and the product reference at this resolution.
- Hypothesis: 1088×1920 is outside the local H3's training range (~0.9 MP); above it, adherence to the references drops.
**Conclusion:** native 1080p on local H3 is not viable (wrong clothing + 1 h per video). The ideal resolution lies between 704×1248 (faithful clothing, bad face) and 1088×1920 (good face, wrong clothing).
**No workflow changed.**

## 2026-11-21 — #20 W5 quality v6 (video at 1088×1920)
**Reason:** the face deforms as early as frame 0 (anchored on the high-res frame) → lack of pixels: at 704×1248 the face is ~100 px wide. A close-up face reference is left for later (it doesn't add pixels).
**Created (v1–v5 untouched):** `WF/motion_W5_qualidade_v6.json` (started from v5), `PROJ/2 - files/workflows/build_W5_v6.py` and `W5_qualidade_v6_api.json`.

**Differences v5 → v6:**
| Node | v5 | v6 |
|---|---|---|
| Test name (1) / Folder (2) | …_q5 / motion/W5_v5/ | …_q6 / motion/W5_v6/ |
| MiniMaxH3ReferenceToVideo (216) width × height | 704 × 1248 | **1088 × 1920** (~2.1 MP; face ~2.4× more pixels) |

Everything else identical to v5 (frame 1536×2720 flux2-vae, skeleton without face, 20 steps, ref max, fp16 video VAE, seed 20261121).
**Risk:** estimated time 25–40 min (not measured) and possible VRAM shortage → fallback v7 at 896×1600.
**Status:** built, not run.

## 2026-11-21 — #19 W5 v5 run — skeleton without face didn't fix the face
No error; **584 s** (Stage 1 from cache; skeleton extraction + 20 steps in 8 min 28 s). Outputs in `OUT/motion/W5_v5/regata-rosa_look-02_q5/`: `frame0_00001_.png`, `pose_sem-rosto_00001_.mp4` (124 frames, 576×1024), `video_00001_.mp4`.
**Created:** `comparativo_v1_v4_v5.mp4` and `zoom_rosto_v1_v4_v5.png` in the same folder.
**Assessment (face zoom, frames 0/40/82/123):** v1, v4 and v5 practically the same — face thinner/more angular than the input and changing over the video. **Face landmark hypothesis ruled out** (small or no effect). Also already ruled out: image VAE (v3 only fixed the frame) and video VAE (v4).
**Remaining hypotheses:** (1) face too small in the video frame (~100 px wide at 704×1248); (2) H3 without a close-up face reference (only the full-body photo).
**No workflow changed.**

## 2026-11-21 — #18 W5 quality v5 (skeleton without face)
**Request:** start from v4 and change only the skeleton, removing the face. The user's question: would the head be left without control? **No:** in the ComfyUI code (`comfy_extras/pose/keypoint_draw.py`) `draw_head` (nose, eyes, ears = head position/rotation) is independent of `draw_face` (68 points for contour, mouth, eyebrows). v5 uses `draw_face=False` and `draw_head=True`.
**Created (v1–v4 untouched):**
- `WF/motion_W5_qualidade_v5.json` (positions and groups copied from v4 + new group "ETAPA 2a")
- `PROJ/2 - files/workflows/build_W5_v5.py` and `W5_qualidade_v5_api.json` (+ copy in `...\user\default\motion_api\`)

**Differences v4 → v5:**
| Node | v4 | v5 |
|---|---|---|
| Test name (1) / Folder (2) | …_q4 / motion/W5_v4/ | …_q5 / motion/W5_v5/ |
| LoadVideo (210) | `motion/W3a/look-02_pose.mp4` (ready-made skeleton from W1, with face) | `fashion-lookbook-look-02-video.mp4` (**original video**) |
| New 230–234 | — | SDPose inside Stage 2: sdpose checkpoint → resize 1024 → grid 32 → extractor (batch 16) → **draw: body, hands, feet, head ON; face OFF**; stroke 4, threshold 0.5 (= W1) |
| New 235–237 | — | saves the skeleton without face: `OUT/motion/W5_v5/<nome>/pose_sem-rosto_*.mp4` (24 fps) — replicable record |
| ControlNet (214) `control_video` | frames of the W1 pose.mp4 | output of the draw without face (234) |

Everything else identical to v4 (frame 1536×2720 with flux2-vae; video 704×1248, 20 steps, ref max, fp16 video VAE, seed 20261121).
**Status:** built, not run.

## 2026-11-21 — #17 W5 v4 run — bad face in the video
Stage 1 came from cache (frame same as v3); Stage 2 without error, **581 s** (20 steps in 8 min 25 s). Outputs in `OUT/motion/W5_v4/regata-rosa_look-02_q4/`: `frame0_00001_.png`, `video_00001_.mp4`.
**Created:** `PROJ/2 - files/workflows/W4_compara_versoes.py` (N videos side by side with labels); `comparativo_v1_x_v4.mp4` and `zoom_rosto_v1_x_v4.png` in the v4 output folder.
**Assessment (the user: "rosto ficou péssimo" — "the face came out terrible"; confirmed in the zoom):**
- v1 and v4 have practically the same bad face → **the fp16 VAE didn't fix the face**; the problem is before the decode.
- Already at frame 0 the face differs from the input frame (asymmetric eyes, thinner/more angular face) and changes over the video (loses identity).
- Hypotheses: (1) **skeleton face landmarks** (SDPose `draw_face=true`) come from the ORIGINAL model's face and force that shape onto a different face; (2) **small face**: ~100 px wide in a 704×1248 video; (3) H3 only has the full-body photo as an identity reference.
**No workflow changed.**

## 2026-11-21 — #16 Download of the fp16 video VAE + W5 quality v4
**Downloaded (authorized by the user):** `D:\Comfy-Desktop\ComfyUI-Shared\models\vae\minimax_h3_video_vae_fp16.safetensors` — 5,207,808,496 bytes (~5.21 GB), from `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors`.
**Check:** 562 tensors, all F16. The old `int8_convrot` has 850 tensors with 144 I8 + 144 U8 (quantized weights).
**Created (v1–v3 untouched):**
- `WF/motion_W5_qualidade_v4.json` (started from the v3 layout; **Stage 2 enabled**)
- `PROJ/2 - files/workflows/build_W5_v4.py` and `W5_qualidade_v4_api.json`

**Differences v3 → v4:**
| Node | v3 | v4 |
|---|---|---|
| Test name (1) | regata-rosa_look-02_q3 | regata-rosa_look-02_q4 |
| Base folder (2) | motion/W5_v3/ | motion/W5_v4/ |
| Video VAELoader (202) | minimax_h3_video_vae_int8_convrot.safetensors | **minimax_h3_video_vae_fp16.safetensors** |
| Stage 2 group | Never | **Always** |

Stage 1 identical to v3 (frame 1536×2720, flux2-vae). Stage 2 same as v1 except the VAE and the input frame: 704×1248, 124 frames, 20 steps, ref max, ControlNet 1.0, seed 20261121.
**Compare with:** the v1 video (`OUT/motion/W5_v1/regata-rosa_look-02_q1/video_00001_.mp4`). Differences: high-res frame (v3) + full video VAE.
**Output:** `OUT/motion/W5_v4/regata-rosa_look-02_q4/`. **Status:** built, not run.

## 2026-11-21 — #15 W5 v3, Stage 1 run — full VAE approved
The user: "melhorou muito" ("much better"). Output `OUT/motion/W5_v3/regata-rosa_look-02_q3/frame0_00001_.png` (1536×2720).
1:1 face comparison v2 × v3: v3 with defined hair strands, eyes and skin texture; v2 had blotches/artifacts from the reduced decoder. (The Laplacian variance didn't change — 35 → 34 — because the v2 artifacts also counted as "high frequency"; the metric doesn't work for this case, the visual assessment is what counts.)
**Lesson:** the VAE decoder is a sharpness bottleneck. The video uses `minimax_h3_video_vae_int8_convrot` (quantized, 2.62 GB); there is a `minimax_h3_video_vae_fp16` (5.21 GB, Comfy-Org/MiniMax-H3), not downloaded.
**No workflow changed.**

## 2026-11-21 — #14 Download of the full VAE + W5 quality v3
**Downloaded (authorized by the user):** `D:\Comfy-Desktop\ComfyUI-Shared\models\vae\flux2-vae.safetensors` — 336,213,556 bytes (~320.6 MB), from `https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors` (link used in 20 official templates).
**Check:** encoder identical to `full_encoder_small_decoder` (137.7 MB); **decoder 198.5 MB vs 111.8 MB** in the reduced one → confirms the old VAE has a lightweight decoder.
**Created (v1 and v2 untouched):**
- `WF/motion_W5_qualidade_v3.json` (started from the v2 layout; Stage 2 on Never)
- `PROJ/2 - files/workflows/build_W5_v3.py` and `W5_qualidade_v3_api.json`

**Differences v2 → v3:**
| Node | v2 | v3 |
|---|---|---|
| Test name (1) | regata-rosa_look-02_q2 | regata-rosa_look-02_q3 |
| Base folder (2) | motion/W5_v2/ | motion/W5_v3/ |
| Stage 1 VAELoader (102) | full_encoder_small_decoder.safetensors | **flux2-vae.safetensors** |

Everything else identical (1536×2720, 28 steps, CFG 3.5, seed, product 4 MP). Isolates the effect of the VAE.
**Output:** `OUT/motion/W5_v3/regata-rosa_look-02_q3/frame0_*.png`. **Status:** built, not run.
**Note:** the other klein workflows (W2, vovo_*, rioopen_*) still use the reduced VAE; switch only if the test confirms a gain.

## 2026-11-21 — #13 W5 v2, Stage 1 run — frame still "blurry"
No error; **459 s** (~7 min 40 s) for the 1536×2720 frame. Output `OUT/motion/W5_v2/regata-rosa_look-02_q2/frame0_00001_.png`.
**Sharpness measurement (Laplacian variance):** downscaled to 768 px wide → product 113 · v2 98 · v1 70 (v2 much better than v1). At native resolution → product 110 · **v2 35** → at 1:1, v2 has little detail per pixel: smooth skin, soft edges (the "blur" the user saw).
**Likely cause:** the VAE `full_encoder_small_decoder.safetensors` used in all klein workflows has a **reduced decoder** (lightweight version). The official templates also use `flux2-vae.safetensors` (full decoder, 320.6 MB, Comfy-Org on Hugging Face), **not downloaded**. Secondary factor: 4 MP is at klein's limit.
**Created:** `OUT/motion/W5_v2/regata-rosa_look-02_q2/zoom_v1_vs_v2.png` (crops of face and knit texture).
**No workflow changed.** Next proposed test: v3 = v2 swapping only the VAE to `flux2-vae` (depends on download authorization).

## 2026-11-21 — #12 W5 quality v2 (first frame at the best quality)
**Reason:** the local video came out at low quality; the first frame (which anchors the video) was at 704×1248. Focus now: the frame at the best possible quality; the video comes later.
**Created (v1 untouched):**
- `WF/motion_W5_qualidade_v2.json` (started from the v1 layout; Stage 2 already saved as **Never**)
- `PROJ/2 - files/workflows/build_W5_v2.py` and `W5_qualidade_v2_api.json`
- copy in `...\user\default\motion_api\W5_qualidade_v2_api.json`

**Differences v1 → v2 (Stage 1 and name only):**
| Node | v1 | v2 |
|---|---|---|
| Test name (1) | regata-rosa_look-02_q1 | regata-rosa_look-02_q2 |
| Base folder (2) | motion/W5_v1/ | motion/W5_v2/ |
| Product (107, ImageScaleToTotalPixels) | 2 MP | **4 MP** |
| Skeleton (110) | 0.9 MP | 1 MP |
| Flux2Scheduler (118) / EmptyFlux2LatentImage (119) | 704×1248 | **1536×2720** (~4.2 MP, klein's practical ceiling) |
| Stage 2 group | Always | Never (turn on when testing video) |

Kept: 28 steps, CFG 3.5, euler, seed 20261121, prompt, empty description. Stage 2 identical to v1 (704×1248; H3 downscales the frame in AddGuide).
**Output:** `OUT/motion/W5_v2/regata-rosa_look-02_q2/frame0_*.png`. **Status:** built, not run.

## 2026-11-21 — #11 W5 v1, Stage 2 (quality video) run
Stage 2 re-enabled with "Set Group Nodes to Always"; Stage 1 came from cache. No error (the VAEDecode bug didn't show up).
**Time:** 560 s in total (~9 min 20 s): 32B text encoder load ~20 s; sampling **20 steps in 8 min 18 s (~24.9 s/step)**; decode ~12 s. Reference for future 704×1248, 124-frame, ref max videos.
**Output:** `OUT/motion/W5_v1/regata-rosa_look-02_q1/video_00001_.mp4` (704×1248, 24 fps, 124 frames, 5.17 s, with audio).
**Created:** `OUT/motion/W5_v1/regata-rosa_look-02_q1/comparativo_lado-a-lado.mp4` (via `W4_lado_a_lado.py`; panels downscaled to 864 px high — for sharpness, watch the video on its own).
**Initial assessment (4 frames):** clothing and identity stable, pose follows the skeleton. The framing "zoom-in" I flagged as a problem **is in the original video** (correction raised by the user and confirmed by measuring pose.mp4): the figure takes up 65% of the frame height at frame 0, 72% at 37, 81% at frames 75–112 and 78% at 149 (+25%; the model walks toward the camera). H3 reproduced it faithfully — **not a defect**. "Lock camera" adjustments dropped.
**No workflow changed.**

## 2026-11-21 — #10 W5 v1, Stage 1 run
Run by the user with Stage 2 set to "Set Group Nodes to Never" (native group mute, right-click on the title). No error; 128 s in total (28 steps in 1 min 49 s, ~3.9 s/step).
**Output:** `OUT/motion/W5_v1/regata-rosa_look-02_q1/frame0_00001_.png` (704×1248).
**Created:** `OUT/motion/W5_v1/regata-rosa_look-02_q1/comparativo_frame0.png` (product | skeleton | generated, made with PIL, outside ComfyUI).
**Assessment:** faithful clothing (knit texture, stripes, sandals), same model, pose matches the frame 0 skeleton.
**No workflow changed.**

## 2026-11-21 — #9 W5 quality v1 (high-res frame + video, in a single workflow)
**Created (new, nothing existing was changed):**
- `WF/motion_W5_qualidade_v1.json`
- `PROJ/2 - files/workflows/build_W5.py` (generator) and `W5_qualidade_v1_api.json` (API copy)
- `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\user\default\motion_api\W5_qualidade_v1_api.json` (API copy used only for loading into the front end)

**Structure:**
| Group | What it does | Quality settings (vs. test) |
|---|---|---|
| Common | name `regata-rosa_look-02_q1`, folders, product `IN/motion/W2/produtos/regata-rosa_frente.png` | — |
| Stage 1 (= W2 at high res) | product + skeleton `IN/motion/W2/look-02/pose-1.png` → FLUX.2 klein 9B base → first frame | **704×1248** (was 480×848) · **28 steps** (was 20) · product **2 MP** (was 1) · skeleton 0.9 MP (was 0.5) · only 1 branch (frame 0 pose) · empty description |
| Stage 2 (= W3a at high res) | H3 ref2va + Fun ControlNet pose (`IN/motion/W3a/look-02_pose.mp4`) → video | **704×1248** (was 480×864) · **turbo OFF = 20 steps** (was 4) · `ref_image_size` **max** (was match) · first frame wired directly to the Stage 1 output (previously came from a file) |

Kept the same: prompts (corrected W2 and W3a), ControlNet strength 1.0, 124 frames, 24 fps, fixed seed 20261121, res_multistep, BasicGuider (guidance 1.0).

**Why 704×1248 and not 720×1280:** the `MiniMaxH3ReferenceToVideo` node requires width/height to be multiples of 32; 720 isn't.
**Output:** `OUT/motion/W5_v1/<nome>/frame0_*.png` and `video_*.mp4`.
**How to run:** Ctrl+B on "Salva video (ETAPA 2)" → Run (frame only) → approve → re-enable → Run (frame comes from cache, only generates the video).
**Status:** built, not run.

## 2026-11-21 — #8 W4 side-by-side comparison (script, not a workflow)
**Created:** `PROJ/2 - files/workflows/W4_lado_a_lado.py`
- Usage: `python -I -X utf8 W4_lado_a_lado.py <original.mp4> <pose.mp4> <gerado.mp4> <saida.mp4>`
- Common height 864 px, labels ORIGINAL | ESQUELETO | GERADO, alignment by uniform sampling (same logic as the W3a `VideoFrameSample`), audio from the generated video.
- **Generated:** `OUT/motion/W4/regata-rosa_look-02_lado-a-lado.mp4` (1476×904, 124 frames, 24 fps, with audio).

## 2026-11-21 — #7 W3a animation via H3 (test)
**Created:**
- `WF/motion_W3a_anima-h3.json`
- `PROJ/2 - files/workflows/build_W3a.py` and `W3a_api.json`
- `IN/motion/W3a/look-02_pose.mp4` (copy of `OUT/motion/catalogo/_teste_B4-P13/pose_00001_.mp4`)
- `IN/motion/W3a/regata-rosa_look-02_frame0.png` (copy of `OUT/motion/W2/look-02/pose-1_00004_.png`)

**Config.:** based on the template `video_minimax_h3_fun_controlnet_union` without the internal SDPose extractor (W1 already does it). H3 ref2va + ControlNet strength 1.0; ref 1 = product; first frame (`MiniMaxH3AddGuide` frame 0) = W2 output; control = pose.mp4 resampled 150→124 frames (`VideoFrameSample` uniform); 480×864; turbo LoRA 4 steps via switch; `ref_image_size` match; fixed seed.
**Execution:** 1st attempt failed in `VAEDecode` (IndexError in `comfy/model_management.py` `free_memory` — a memory-management bug in ComfyUI 0.46.2, not in the workflow). 2nd attempt OK → `OUT/motion/W3a/regata-rosa_look-02/video_00001_.mp4`. Plan B if it happens again: switch to VAE Decode (Tiled).

## 2026-11-21 — #6 Reference video downloaded
**Created:** `PROJ/3 - Assets/referencias de pose/pozze_black-friday_DfEy39VA9dX.mp4` (Instagram @pozze.com.br, post DfEy39VA9dX; 720×1280, 30 fps, 11.1 s, with audio, 2.25 MB).
Notes: has a turn to the back (good motion test); framing cuts at mid-thigh.
Already went through W1 (by the user), but with the old name → `OUT/motion/catalogo/_teste_B4-P13/pose_00002_.mp4` and `original_00002_.mp4` (330 frames).

## 2026-11-21 — #5 W2 fixed (garment description)
**Problem:** with a new product (pink tank top), the generated clothing came from the old text in the "Descricao da peca" (garment description) field (look-02: cream polo/rust skirt). **The description text wins over image 1.**
**Changed (before the versioning rule — file overwritten):**
- `WF/motion_W2_pose-em-imagem.json`:
  - node *Descricao da peca* → empty value; title "Descricao da peca (opcional, ingles, igual a imagem 1)"
  - node *Prompt completo* `string_a` → + "The clothing must be copied only from image 1 … Do not invent or replace any clothing." ; `delimiter` → "\n\nOutfit details, exactly as in image 1: "
  - node *Image 1 - Produto* → `motion/W2/produtos/regata-rosa_frente.png`
  - node *Nome do teste* → `regata-rosa_look-02`
  - "Como usar" (how to use) note updated
- `PROJ/2 - files/workflows/build_W2.py` and `W2_api.json` regenerated with the same.
**Created:** `IN/motion/W2/produtos/regata-rosa_frente.png` (copy of `IN/image (1).png`, sent by the user).
**Result:** with an empty description it worked — clothing from image 1 in the skeleton's pose (`OUT/motion/W2/look-02/pose-*_00004_.png`).
**Previous version (v0, lost in ComfyUI):** description = "cream short-sleeve knit polo with black-tipped collar and sleeve cuffs, rust satin midi slip skirt with ivory lace hem, brown leather slide sandals, woven straw tote bag"; delimiter "\n\nOutfit: "; prompt without the phrase "copied only from image 1"; product `motion/W2/look-02/produto_provisorio_look-02.png`; name `look-02`.

## 2026-11-21 — #4 W2 pose in image (test)
**Created:**
- `WF/motion_W2_pose-em-imagem.json`
- `PROJ/2 - files/workflows/build_W2.py` and `W2_api.json`
- `IN/motion/W2/look-02/pose-1..4.png` (W1 pose keyframes) and `produto_provisorio_look-02.png` (frame 1 of the original)

**Config.:** structure of the user's `*_klein9b-base` workflows: FLUX.2 klein 9B base fp8 + qwen_3_8b + full_encoder_small_decoder; image 1 = product (1 MP), image 2 = skeleton (0.5 MP) via ReferenceLatent; 4 branches (one per keyframe); 480×848; 20 steps; CFG 3.5; fixed seed 20261121 (control "fixed").
**Run 1:** OK, faithful clothing, but the poses were too similar to the product to evaluate adherence.

## 2026-11-21 — #3 W1 first test
Run by the user with `fashion-lookbook-look-02-video.mp4` (724×1268, 30 fps, 150 frames). No error, ~38 s. Pose 576×1024, complete skeletons (body, hands, face, feet). Output went to `OUT/motion/catalogo/_teste_B4-P13/` because the "Nome do movimento" (motion name) field wasn't changed.

## 2026-11-21 — #2 Project migrated to this folder
- The official folder changed from `E:\dev\Image Studio\motion` to `PROJ/` (the old one was left intact).
- **Created:** `PROJ/CLAUDE.md` (full briefing, loaded automatically) and `PROJ/2 - files/workflows/W1_api.json` (copy of the old one).

## Before 2026-11-21 — #1 W1 pose extraction (another project)
`WF/motion_W1_extrai-pose.json`: LoadVideo → VideoTemporalCrop → SDPose (1024 + grid 32 px) → `OUT/motion/catalogo/<nome>/` pose/original mp4 + 4 keyframes of each.
