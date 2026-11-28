# Changelog — Fashion pose-to-video

Detailed record of what was created or changed, where, and why. The newest entry is at the top.
Path abbreviations:
- `WF/` = `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\user\default\workflows\` (workflows that show up in ComfyUI)
- `IN/` = `D:\Comfy-Desktop\ComfyUI-Shared\input\`
- `OUT/` = `D:\Comfy-Desktop\ComfyUI-Shared\output\`
- `PROJ/` = `E:\dev\Fashion-pose-to-video\`

**Versioning rule (from 2026-11-21 on):** an existing workflow is no longer modified. A configuration change = a new file with a version suffix (`_v1`, `_v2`…), both in ComfyUI (`WF/`) and in the API copy and the generator (`PROJ/2 - files/workflows/`). The `build_*.py` generators refuse to overwrite an existing version file.

---

## 2026-11-28 — #83 Approved pose list: 3 poses
User: turning poses are not used; `w-turn-03` works but does not enter the approved list. Approved = `look-02`, `w-side-05`, `w-side-04` (cut to 4.2 s, products with free hands). `02_library/poses/catalog.csv` (`w-turn-03` → `works-not-approved`), `00_docs/decisions.md`.

## 2026-11-28 — #82 Three candidate poses set aside (they turn)
Before EXP-012, a frame check (original + skeleton every 12 frames) showed that `m-side-03`, `w-hands-02` and `w-side-01` turn to profile and to the back in the second half (the earlier limb-color facing check missed it); frontal only for 2-2.5 s. User: not used ("então fica sem"). `02_library/poses/catalog.csv`: `local_group` = `turning`, with the frame ranges; `00_docs/decisions.md`. No video generated.

## 2026-11-28 — #81 EXP-011: `w-side-04` cut before the turn → validated
**Requested by the user** after EXP-010 (the end turn was not followed). The source turns at ~4.25 s → pose cut to its first 100 frames (0–4.17 s) with the new `01_pipeline/scripts/trim_pose.py` (`IN/motion/poses/w-side-04/`: pose.mp4, original.mp4, keypoints.json; old files `.previous-<date>`). No W1 re-run.
**`run_product.py video`:** the H3 video length (node 216) and the frame sampler (node 211) now follow the pose frame count (was fixed 124); `RUN_TAG` env var appends a suffix to the run folder. Queue-time override only; `W5_video_v21_api.json` unchanged.
**Result:** same first frames and seed as EXP-010; all 3 videos follow the skeleton to the end (navy PASS; caramel bag floats, FARM bag reshaped while both hands are on the hips). **User decision:** a hand on the hips cannot hold a bag → request mismatch, not a generation defect; `w-side-04` validated for products with free hands. Recorded in `00_docs/decisions.md`, `02_library/poses/catalog.csv` (new column `exp011_v21`, frames 100), experiments index.

## 2026-11-28 — #80 EXP-010: non-turning poses with the W5 v21 flow
**Requested by the user:** validate the poses that do not turn to the back. 3 products × 5 poses (`w-side-05`, `w-side-04`, `m-side-05`, `m-side-04`, `w-walk-01`), 6 first-frame candidates per pair, 1 video seed = 15 videos.
**Preparation:** `m-side-05` re-cut from 1.5 s of the source and re-extracted with W1 v3 (the model entered the frame at frame 0). New `01_pipeline/scripts/normalize_pose.py`: scales a pose that fills the frame (skeleton, original, keypoints) uniformly, anchored on the floor, to the framing of the working poses (eye line 0.145, ankles 0.875), so reframed product photos keep the cap and the feet; old files kept as `.previous-<date>` (scales 0.85–0.94).
**Result (two checks, the user's is final):** `w-side-05` **validated** 3/3; `w-side-04` 0/3 (the end turn is not followed → re-cut before the turn); `m-side-05` partial (bag disappears; navy face defect); `m-side-04` 0/3 (crossed arms → three hands at frame 0) → **isolated** (`IN/motion/poses_parked/isolated/`); `w-walk-01` 0/3 (motion not followed) → `poses_parked/rejected/`. No painted lines, no garment swaps.
**Claude's review missed** the three hands, the turn and the walk not followed and the navy face → reviews now also compare motion vs skeleton and count hands when arms cross.
**Files:** `04_experiments/EXP-010_…/` (`plan.md`, `runs.csv`, `result.md`), index, `02_library/poses/catalog.csv` (new column `exp010_v21`, `local_group` updated). Local review page `OUT/motion/video/EXP-010_review.html`.

## 2026-11-28 — #79 W5 v21 split promoted to production
**Approval:** the user reviewed the 12 EXP-009 videos (`output/motion/video/EXP-009_review.html`, report per video) and approved ("Approved"). Recorded in `05_approvals/approvals.csv` and EXP-009 `result.md`.
**ComfyUI (`WF/`):** new `motion_W5_frame0_v21.json` and `motion_W5_video_v21.json`, built by loading `W5_frame0_v21_api.json` / `W5_video_v21_api.json` in the frontend (`app.loadApiJson`) with a usage note each; `graphToPrompt()` matches both API JSONs (33 and 34 nodes, no differences). `motion_W5_quality_v20.json` removed from `WF/` (moved aside to `IN/_ui_build/`).
**Repo:** `01_pipeline/workflows/ui/production/` = W1 v3, **W5 frame0 v21, W5 video v21**, W6 v3; `motion_W5_quality_v20.json` → `ui/archive/`.
**Docs:** README (production table with 2a/2b, v21 paragraph, step 5 with `run_product.py`), CLAUDE.md (production flow and current state).

## 2026-11-28 — #78 Overnight work: FARM product, frame-0 candidates, W5 v21 split (TEST) and the replicable flow
**Requested by the user before sleeping:** keep running until results are good; goal = a replicable workflow for any e-commerce photo (FARM Rio as the reference); visual checks stay human ("por enquanto somos nós que checamos"; a VLM checker was started and removed on the user's word).
**New product:** `02_library/products/farm-giovanna-jeans/` (FARM "Calça Jeans Giovanna", front photo from the store page, internal test use only).
**Prep fix:** `reframe_product.py --kp-product --kp-pose` matches the eye line and ankles from SDPose keypoints (the FARM cap made the silhouette mode put the skeleton's eyes on the cap). Pose keypoints stored as `IN/motion/poses/<pose>/keypoints.json` (`look-02`, `w-turn-03`).
**EXP-008 (FARM, EXP-006 setup):** `look-02` 3/3 clean; `w-turn-03` garment fine but the cap and the raffia bag are reinvented from the back → turning poses need a back photo.
**EXP-007 (frame-0 candidates, stage 1 only, 48 frames):** frame-0 defects are seed-dependent (extra hand, painted lines, wrong sleeves, extra accessories); the arms/hands sentence (P1) cuts the extra hand on caramel `w-turn-03` from 4/6 to ~1/6; the keypoint score does not see the extra hand → generate candidates, choose by eye.
**W5 v21 (TEST, production stays v20):** `build_W5_v21.py` → `W5_frame0_v21_api.json` (stage 1 + P1 sentence, output `motion/frame0/`) and `W5_video_v21_api.json` (stage 2 from a chosen first frame via LoadImage, EXP-006 video prompt, output `motion/video/`). UI versions not built yet.
**Flow script:** `01_pipeline/scripts/run_product.py prep | frame0 | video` (+ `frame0_select.py`, `detail_sheet.py`). EXP-009 runs it end to end.

## 2026-11-28 — #77 Correction: extra hand in caramel + w-turn-03 (EXP-003, EXP-005, EXP-006)
**The user's catch:** every caramel + `w-turn-03` video since EXP-003 has an **extra hand**: frame 0 (stage 1, klein) keeps the product's hand in the pocket **and** draws the skeleton's hanging hand on the same side. Same frame 0 for every seed (image seed fixed), so all seeds have it; the video prompt cannot fix it. My review missed it (1/8-frame sheets, no zoom on hands).
**Corrected counts:** EXP-003 **7/12** (was 8), EXP-005 A **1/4** and B **1/4** (were 3/4), EXP-006 **9/12** (was 12/12). The other 9 confirmed perfect by the user (the line on the navy `look-02` s222 jeans is the trousers' crease and light, not a defect). EXP-004 (retargeted skeleton) had no extra hand on this pair's frame 0.
**Consequence:** the prompt fix stands; the remaining defect is the stage-1 pose mismatch (product hand in pocket vs skeleton arm hanging). W5 v21 waits for a frame-0 fix/check. Review rule tightened: zoom on hands and arms of frame 0 and the first second of every run.

## 2026-11-28 — #76 EXP-006 neutral video prompt + reframing: 12/12 clean
**Experiment** `04_experiments/EXP-006_2026-11-28_neutral-prompt/` (plan approved; order set by the user: the 4 EXP-003 failures first, then the 8 passes). EXP-003 setup (reframed product, catalog skeleton, W5 v20) with only the video prompt (node 215) changed (`prompt.txt`): "stands" → "is shown"; "stripes" removed; motion sentence → "She follows the pose guide exactly, with a calm confident expression." (no movement named).
**Result:** step 1 4/4, step 2 8/8 → **12/12 clean** (EXP-003 8/12). Stripes, thigh streak, lost turn and unwanted turn all gone; no regression. Comparisons `exp003-vs-exp006_<pair>.mp4`.
**Side finding (the user's question):** the thigh streak of EXP-003 came from frame 0: with the reframed photo, stage 1 copied the product's hand-in-pocket instead of the skeleton's hanging arm (EXP-001 frame 0 followed the skeleton). Recorded in EXP-003 `result.md`; rule: check frame 0 against the skeleton before stage 2; prefer product photos with arms down.
**Next (proposed):** W5 v21 = v20 + this prompt (production stays v20 until approved); then validate the 7 candidate poses and a patterned product.

## 2026-11-28 — #75 EXP-005 video prompt: the word "stripes" and the motion sentence caused most remaining defects
**Experiment** `04_experiments/EXP-005_2026-11-28_video-prompt/` (plan approved; scope set by the user: the 4 runs that failed in EXP-003 first). EXP-003 setup (reframed product, catalog skeleton, W5 v20), only the video prompt (node 215) changed, two variants (exact text in `prompts.json`): **A** motion words ("stands" → "is shown"; "moves naturally …: subtle weight shifts, relaxed arms" → "follows the pose guide exactly, including turning around … when the guide turns"); **B** "stripes" removed from "same colors, fabric texture, stripes, length and fit". 8 runs. Comparisons `compare_<pair>__s<seed>.mp4` (skeleton | EXP-003 | A | B).
**Result:** EXP-003 0/4 clean on these runs → A 3/4, B 3/4 (+1 partial). B removes every stripe and the thigh streak; A also keeps the turn to the back, but its wording made the model turn around on `look-02`, a pose that never turns.
**Lesson:** the prompt itself was asking for stripes on every product, and the motion sentence ("stands", "subtle weight shifts") fought turning poses; the motion text must stay pose-neutral.
**Next (proposed):** EXP-006 = B + a pose-neutral motion sentence, on these 4 runs then on the 8 passing ones; if it holds on all 12, build W5 v21.

## 2026-11-28 — #74 EXP-004 per-bone retargeting: not adopted (6/12 vs 8/12)
**New scripts (native ComfyUI code, no custom nodes):**
- `01_pipeline/scripts/pose_keypoints.py extract|draw`: runs ComfyUI's own SDPose (`sdpose_wholebody_fp16`, in-process, in inference mode) to save OpenPose keypoints as JSON (no native node saves them), and redraws them with `SDPoseDrawKeypoints` and the W1 v3 settings. Checked: redrawing the source keypoints reproduces the catalog skeletons (`w-turn-03` 2–5 px differences; `look-02` identical extent, extracted from the reference video since it has no `original.mp4`). Free ComfyUI's VRAM first (`POST /free`).
- `01_pipeline/scripts/retarget_skeleton.py`: per-bone retargeting (Wan-Animate style, 2D): ratios target/source per bone (source frame 0; target = reframed product photo; the two segments of a limb share the larger ratio; one head ratio; clip 0.7–1.4; median for hidden bones), tree walk from the mid-hip keeping angles and foreshortening, hands/feet/face carried rigidly, floor anchor smoothed over 15 frames.
- `generation_report.py` already accepts the retargeted skeleton.
**Experiment** `04_experiments/EXP-004_2026-11-28_bone-retargeting/` (plan approved; three method fixes made before running and recorded in the plan: reference frame 0, shared limb ratio, smoothed floor anchor): EXP-003 setup + retargeted skeleton, same 4 pairs × 3 seeds. Side-by-side `exp003-vs-exp004_<pair>.mp4`.
**Result:** clean passes 6/12 (EXP-003 8). Better for caramel (thigh streak gone, white bar gone); worse for navy (3 passes became fails, third shoe back in frame 0 of `w-turn-03`). Cause: the navy photo hides the hands (behind the back), so bone lengths are guessed wrong (forearm 0.72 → 0.82, head 1.10); a wrong skeleton sits off the body. Matches the Wan-Animate caveat (2D posture distorts bone lengths; they measure on T-pose images).
**Decision (proposed):** keep reframing as the standard; retargeting stays as a tool, off by default; keypoints JSON kept for pose curation and frame-0 checks. Next candidates: skeleton without hands, ControlNet settings, prompt (H-b).

## 2026-11-27 — #73 EXP-003 product reframing: best result so far (8/12 clean) + research note
**New script:** `01_pipeline/scripts/reframe_product.py <product> <pose.mp4> <out.png> [overlay.jpg]`: scales and places the person of the product photo where the skeleton is (eye line on the skeleton head, feet on the skeleton feet, same center) on a 9:16 1088×1920 canvas filled with the photo's own background color (soft 24 px seam). `generation_report.py` accepts the reframed product as its product argument.
**Experiment** `04_experiments/EXP-003_2026-11-27_product-reframing/` (plan written first, approved): same 4 pairs × same 3 seeds; only the product image changed (reframed per pair, `IN/motion/experiments/EXP-003/<pair>/product.png`); catalog skeleton unchanged. 12 runs. Side-by-side `exp001-vs-exp003_<pair>.mp4`.
**Result:** clean passes 8/12 (EXP-001 4, EXP-002 0). Stage 1 clean in all pairs (no neck face, no extra shoe, nothing cut). `look-02` 6/6. Remaining: `w-turn-03` seed 222 (stripes in the back turn, return to the front) and one thigh streak where the skeleton arm crosses the product's hand-in-pocket. Results more consistent across seeds. Person ~25–30 % smaller, face still sharp. Flags missed 2 defects → human review stays.
**Research:** `00_docs/research/research-pose-misalignment.md` — other people's experience (Animate-X, StableAnimator++, Wan-Animate retargeting, MimicMotion, community guides): skeleton/reference mismatch is a known main cause of extra anatomy; the standard fixes are framing the reference like the pose and per-bone retargeting. Sources from other models (we use MiniMax H3 + Fun ControlNet): the method transfers, the result must be tested on H3.
**Next (proposed):** adopt reframing in the prep layer; EXP-004 = per-bone retargeting on top of reframing (baseline EXP-003).

## 2026-11-27 — #72 EXP-002 skeleton alignment: fixes the neck face, not the stripes
**New script:** `01_pipeline/scripts/align_skeleton.py <pose.mp4> <product> <out.mp4> [overlay.jpg]`: one uniform scale + shift for the whole skeleton video, computed on frame 0 (head on the product person's eye line, feet on the feet, same center), scale capped so no frame leaves the frame; writes an overlay of the aligned frame 0 on the product. `generation_report.py` takes an optional 4th argument (the skeleton actually used) and labels it "SKELETON (aligned)".
**Experiment** `04_experiments/EXP-002_2026-11-27_skeleton-alignment/` (plan written first, approved): same 4 pairs × same 3 seeds as EXP-001, only the pose video replaced by the aligned copy (`IN/motion/experiments/EXP-002/<product>__<pose>/pose.mp4`; scale 1.22–1.25; `look-02` capped: head and shoulders aligned, legs ~13 % short). 12 runs, ~48 min. Side-by-side `exp001-vs-exp002_<pair>.mp4`.
**Result:** the stage-1 **face on the neck is gone**. The stripes are **not** reduced: 4 seeds that passed in EXP-001 now fail (0 clean passes vs 4). New stage-1 defects from the bigger skeleton: top of the hair cut by the frame, and a **third shoe** between the feet (a skeleton foot point off the body). Lesson: every skeleton point that does not sit on the body becomes an extra object; enlarging the skeleton pushes the body to the frame edges.
**Next (proposed):** EXP-003 = bring the product photo to the skeleton's framing (padding, prep step; plan H-c), skeleton unchanged; then the stripes (prompt / ControlNet) on top of the right framing. Add a frame-0 check for extra faces/feet.

## 2026-11-27 — #71 EXP-001 seed baseline: the failures are seed luck, not the pose
**Experiment** `04_experiments/EXP-001_2026-11-27_seed-baseline/` (plan written first, approved by the user; plan phase 2): W5 v20 unchanged, 2 products (caramel, navy polo) × 2 poses (`look-02`, `w-turn-03`) × 3 video seeds (20261121, 111, 222; node 221), image seed fixed. 12 runs (~47 min), outputs in `OUT/motion/experiments/EXP-001_2026-11-27_seed-baseline/` (W5 node 2 prefix overridden at queue time), each with `report.mp4` + `review_sheet.jpg`, plus `seeds_<product>__<pose>.mp4` (skeleton | 3 seeds).
**Result (full review):** no pair is 3/3 the same. Seed 111 passed all 4 pairs; seed 222 failed all 4 with stripes (including the production pair caramel + `look-02`); seed 20261121 mixed (navy `look-02` waves; `w-turn-03` does not hold the turn to the back). Same-seed re-runs are reproducible (mean difference 1–2/255 vs EXP-000). The navy `w-turn-03` "neck mark" is in fact **a second face painted on the neck** (the user's catch, also the "extra face" of #69): frame 0 (stage 1) makes the person larger than the skeleton, so the skeleton's face points fall on the neck and klein draws a face there → skeleton/person alignment (plan H-a) is needed for stage 1.
**Review flags:** missed 2 of 6 failures (thin white lines on denim) → human review stays mandatory; next flag version should compare with the product colors.
**Proposed next:** EXP-002 = video prompt without the conflicting motion words + garment description, same 4 pairs × same 3 seeds (1:1 with the baseline); until a fix, production uses 2–3 seeds per video + review.

## 2026-11-27 — #70 New folder structure (repo + ComfyUI motion folders)
**Why:** the user found the project hard to follow: tests, library, references and production were mixed, with Portuguese and English names. Approved structure: one folder per job, numbered in the order of the work. Nothing was deleted; repo files moved with `git mv` (history kept). Paths in older CHANGELOG entries are the old ones.
**Repo, before → after:**
- `1 - AI instructions/` → `00_docs/plans/` (the plan) and `00_docs/research/` (face research); new `00_docs/decisions.md` (one line per decision, seeded with the main ones).
- `2 - files/workflows/` → `01_pipeline/workflows/` (all `build_*.py` + `*_api.json` stay together because builds import earlier versions) with UI files in `ui/production/` (was `ui_production/`), `ui/tools/` (W7 v3 and x4 v2) and `ui/archive/` (was `ui_tests/`); scripts → `01_pipeline/scripts/` (`catalog.py`, `generation_report.py`, `generation_review.py`, `pose_compare_page.py`, `W4_*.py`, `convert_kandinsky_sr.py`).
- `2 - files/pose-catalog/` → `02_library/poses/`; new `02_library/products/<product>/meta.json` (caramel-tank-jeans, navy-polo-jeans; images copied but not versioned), `02_library/models/` (future), `02_library/README.md` (status values).
- `3 - Assets/referencias de pose/` → `03_references/pose-videos/` (contents moved; the old folder is empty but could not be removed while a session used it as its working folder).
- New `04_experiments/` (README with the experiment rules and an index) with `EXP-000_2026-11-27_trial-chain/` (`result.md` + `runs.csv`: the 21 runs of #69 with flags and verdicts; `reviews/` not versioned).
- New `05_approvals/approvals.csv`, seeded with the approvals so far (production W5 v16/v20, W6 v3, Pexels and e-commerce references, the plan, this structure; the "26 ready poses" claim marked withdrawn).
- `.gitignore`: `3 - Assets/**` rules → `03_references/**`; product images and `04_experiments/**/reviews/` ignored.
**ComfyUI folders (`IN/motion`, `OUT/motion`):** production paths unchanged (`input/motion/poses`, `products`, `sources`, `production`), so the production workflows keep working (checked: the W5 v20 default product and pose exist). Moved: `OUT/motion/{W2, W3a, W4, W5_v1…v19, W6_v1, catalogo, producao}` → `OUT/motion/_archive/`; the #69 test outputs (`production/test_*`, `pose-qa*`, the two `*_w-side-04`) → `OUT/motion/experiments/EXP-000_2026-11-27_trial-chain/`; `IN/motion/{W2, W3a, W6, _teste_B4-P13.mp4}` → `IN/motion/_archive/`; `IN/motion/poses_rejected|poses_untested` → `IN/motion/poses_parked/rejected|untested`.
**Scripts:** `generation_report.py` / `generation_review.py` now take names relative to `OUT/motion/` (`production/…` or `experiments/EXP-…/…`); the report finds parked poses; the index moved to `OUT/motion/reports.html` (21 generations). Checked: `catalog.py list`, `pose_compare_page.py`, both report scripts and all builds (parse).
**Docs:** README (layout, folders, links), CLAUDE.md (folder layout, example paths → `_archive/`), plan and pose catalog README links.

## 2026-11-27 — #69 W5 v20 with the new poses: the garment drifts; tests stopped, plan approved
**Runs** (by Claude, on the user's request; W5 v20 API with only name, product, pose and the tested value changed; 1 video seed each; outputs in `OUT/motion/production/`):
1. `caramel-tank-jeans_w-side-04` (skeleton 4:5): frame 0 right, then the outfit turns into a beige knit set with the skeleton lines painted on it as stripes; the bag disappears; the turn to profile is not followed.
2. Same with the skeletons **cropped to 9:16** (all 26 cropped around the body to 576×1024, originals and keyframes too; 4:5 files kept as `.previous-<date>`): same defect.
3. `navy-polo-jeans_w-side-04` (the user's image `IN/image (3).png`, copied to `IN/motion/products/navy-polo-jeans_front.png`): much better, faint lines on the polo, no turn to profile.
4. `test_caramel_w-side-04_cn045` (ControlNet 0.45) and `_s080` (skeleton scaled to 80%): the jeans become a striped skirt / dress.
5. Control `test_control_caramel_look-02` (W5 v20 defaults): good, as before → the environment is fine.
6. `test_caramel_w-turn-03`: good (turns to profile and back, garment and bag kept). `test_caramel_w-side-04_end025` (ControlNet end 0.25): fails.
7. **Pose QA batch** `pose-qa/caramel-tank-jeans_<pose>`, stopped by the user after 10: pass `m-side-03`, `m-side-04`, `m-turn-02`, `m-turn-03` (arm artifact), `w-hands-02`, `w-side-01`; fail `m-side-02`, `w-shift-01` (stripes), `m-side-05` (model cut by the frame at frame 0), `w-hands-01` (extra arms at frame 0, stripes).
8. **Turbo off** (20 steps) on the 4 stripe failures, `pose-qa-turbo-off/`: fixes `w-hands-01` only; the other 3 get worse (garment already wrong at frame 0). Side-by-side `compare_turbo-on-vs-off_<pose>.mp4`.
9. **Second product on the 8 "approved" poses** `pose-qa/navy-polo-jeans_<pose>`: `look-02` fails (blue waves on the polo), `w-turn-03` has a red mark on the neck (the user also saw an extra face), `m-side-03` ran; the rest was cancelled when the user stopped everything.
**Analysis:** facing (front/back, from the limb colors) and skeleton jitter do not separate passes from fails; turning to the back is not by itself the cause (5 back turns passed). A model cut by the frame does break frame 0. The defect depends on pose **and** product.
**Process problem (the user's call):** ~20 single-seed runs in a trial-and-error chain, videos judged on 5–6 frames (missed an extra face and drift), results shown without comparison. The user stopped all runs and asked for a plan.
**Plan (approved):** `PROJ/1 - AI instructions/plan-2026-11-27-pose-catalog-and-inputs.md` (Portuguese reading copy `.pt.md`, not versioned): rules (hypothesis + control written first, 3 video seeds, full review, comparisons), phase 0 record fix, phase 1 review tools, phase 2 seed baseline, phase 3 input standardization outside ComfyUI, phase 4 causes one at a time, phase 5 pose validation on 3 reference products.
**New:** `generation_report.py` (per generation `report.mp4`: product | original pose video | skeleton | generated, + local index `OUT/motion/production/reports.html`); rule added to CLAUDE.md. Local W5 pose list cleaned: `IN/motion/poses/` keeps the 7 candidates + `look-02`; `poses_rejected/` (5) and `poses_untested/` (14), nothing deleted.
**Phase 1 (review tools):** `generation_review.py <name>` writes `review_sheet.jpg` (every 8th frame, each tile with its values) and `review.json` next to the video, with 3 flags on the garment region (person against the plain background, head excluded): *drift* (color histogram vs frame 0), *new colors* (colors absent from frame 0) and *edge* (strong-edge share vs frame 0, catches stripes and painted lines). Calibrated on 12 existing runs: the 7 good ones stay at drift ≤ 0.45 / new ≤ 0.05 / edge p90 ≤ 0.86; all 4 known bad ones are flagged (drift 0.75–0.90, or edge p90 1.5–2.0, which is what catches the navy `look-02` waves). Limits 0.50 / 0.10 / 1.25, flag at ≥ 5 frames. Faces and extra limbs are not detected: the human review stays.
**Repo (phase 0):** `2 - files/pose-catalog/` now holds the 9:16 skeletons, says "extracted, NOT validated", and `catalog.csv` gets the local group and the W5 results per product. README and CLAUDE.md corrected.

## 2026-11-27 — #68 Pose catalog: 26 skeletons from the 5.2 s clips (W1 v3 batch) + W1 start bug
**Run:** on the user's explicit request, Claude queued W1 v3 (`W1_extract-pose_v3_api.json`, values unchanged except pose name, video and start) once per 5.2 s clip of #67. This is an exception to the "never run workflows" rule, for this batch only. Sources were copied to `IN/motion/sources/`. ~45 s per pose.
**Names:** `<gender>-<type>-<nn>` (`w`/`m`; `turn`, `side`, `hands`, `shift`, `walk`), e.g. `w-turn-01`, `m-side-02`. Local map pose ↔ source clip: `3 - Assets/referencias de pose/ecommerce/review_pose_plan.json` (gitignored).
**Dropped (4 of 30):** `m-side-01`, `m-turn-01`, `w-side-02`, `w-turn-02`. A frame-exact check showed the cut to a close-up comes at 5.0–5.14 s (the 0.2 s cut scan of #67 was too coarse). `m-side-01` had already run (its last frames were the close-up); the other three were removed from the queue.
**Bug found (ComfyUI 0.46.2):** **W1 v3 ignores the clip start.** `VideoTemporalCrop` returns a lazily trimmed video, but `VideoFrameSample` (`_decode_selected_frames` in `comfy_extras/nodes_dataset.py`) decodes from the start of the file and drops the trim. So W1 always took the first 5.2 s of the video. It was found because `m-side-05`, `w-turn-10`, `w-turn-11` and `w-walk-01` started with an empty frame (the model walking into frame), and a re-run with a later start gave byte-identical files. `look-02` (start 0) was not affected.
**Fix used (no workflow change):** the 7 clips with start > 0 (`m-side-05`, `w-hands-01`, `w-side-03`, `w-side-06`, `w-turn-10`, `w-turn-11`, `w-walk-01`) were cut beforehand with PyAV (libx264, CRF 12, start → start + 5.4 s) into `IN/motion/sources/<pose>_clip.mp4`, and W1 v3 ran again on them with start 0. The 4 walk-in clips also got a start 0.8 s later, so frame 0 has the model fully in frame (W5 takes the first-frame pose from frame 0). The other 19 poses had start 0 and were right the first time. A proper fix is a future W1 v4.
**Result (26 poses, 20 women / 6 men):** turn 12, side 10, hands 2, shift 1, walk 1, all 124 frames at 24 fps. Sizes 800×1024 (ASOS 4:5), 704×1024 or 576×1024 (Zalando). Filed with `catalog.py pose` into `IN/motion/poses/<pose>/` (pose.mp4, original.mp4, keyframes; the superseded runs are kept as `.previous-<date>`). All keyframes checked against the current `pose.mp4`. Weak spots: `w-hands-01` (skeleton lost ~0.9 s while bending forward, frames 65–85), `w-walk-01` (walks out of frame in the last ~0.3 s), `w-turn-10` / `w-turn-11` (3 weak frames each).
**Repo (skeletons only, user's decision):** new `2 - files/pose-catalog/` with `<pose>/pose.mp4` + `pose-1..4.png`, `catalog.csv` (no product ids or links), `contact_sheet.jpg` and a README (~19 MB). The original clips stay local.
**New script:** `2 - files/workflows/pose_compare_page.py` writes the local page `IN/motion/poses/compare.html`: original clip and skeleton side by side, played in sync, with filters (gender, type, speed). Not in the repo, because it shows the original clips.
**Docs:** README (pose catalog paragraph, W1 start bug warning, lessons table, layout), CLAUDE.md (W1 bug, catalog state, next steps), pose catalog README.
**Next:** W5 v20 with the new poses (check framing: the skeletons are 4:5 and W5 renders 9:16); W1 v4 without the start bug.

## 2026-11-27 — #67 E-commerce pose catalog: 30 clips of 5.2 s + 94 of 3 s (ASOS, Zalando)
**Why:** batch 1 (Pexels, #66) had non-catalog poses and framing problems. Goal: 100+ pose clips from fashion e-commerce product videos (studio, professional models). Internal use only (skeleton reference); originals never published.
**Source pilot:** ASOS best (direct mp4, 1080×1350, 50 fps); Zalando good but mixed (HLS, ads, close-ups, street shots). Zara hard; COS, H&M, Net-a-Porter, Boohoo, Farm, Animale, Dafiti without product video; Mango and Revolve blocked (403); Renner in a queue.
**Download** (user approved): 177 ASOS + 57 Zalando = 234 videos, ~900 MB, 0 failures, in `PROJ/3 - Assets/referencias de pose/ecommerce/<store>/` + `manifest.csv` (not versioned).
**Review:** local review page (OK / reject, clips with type and start, women/men filter, separate 5.2 s / 3 s counters). The user reviewed the first 59 videos (48 OK); then clips were proposed by shot-cut detection (first and last shot of each video) and every proposal was checked on 4-frame strips (start → end): head cropped, close-ups, street shots and cuts inside the clip were dropped. The user approved the result.
**Finding:** these videos are edited (~3–4 s full body → close-up → full body), so only ~1 in 4 kept videos has 5.2 s of continuous full body; ~1 in 5 ASOS videos crops the head. User's decision: allow 3 s clips, but **keep them apart and use only the 5.2 s clips for now** so the W1 v3 → W5 v20 flow does not change.
**Result:** `review_clips_5.2s.json` = 30 clips (22 women, 8 men; turn-360 14, side 12, hands 2, walk-in 1, stand-shift 1; ASOS 24, Zalando 6). `review_clips_3s.json` = 94 clips (80 women, 14 men). `review.json` = all verdicts, notes and clips. 131 videos kept; the 103 rejected sent to the Windows Recycle Bin.
**Repo:** `.gitignore` now also ignores `3 - Assets/**/manifest*.csv` and `review*.json` (videos were already ignored). README of the folder: new e-commerce catalog section.
**Next:** W1 v3 on the 30 clips of 5.2 s → skeleton catalog. 100 clips of 5.2 s would need another harvest from sources with longer takes, or a 3 s flow (W1 v4 / W5 v21).

## 2026-11-25 — #66 Six new reference videos for the pose catalog (Pexels)
**Search:** ~285 vertical Pexels videos (12 queries: model posing, lookbook, catwalk, turning around…) filtered by metadata (≥5 s, one person, no close-ups), then checked at the start, middle and end of each clip (full body in frame all the time, static camera). 13 candidates (10 main + 3 reserves) downloaded in HD to a temporary `candidatos/` folder and reviewed by the user in a local OK / reject page.
**Kept (6)** in `PROJ/3 - Assets/referencias de pose/` (not versioned): `pexels_3888256` (beige suit), `pexels_7507265` (cardigan), `pexels_7760060` (jeans + coat), `pexels_8798401` (green dress, 720×1366), `pexels_8992290` (dress + turn, back view), `pexels_9558748` (man, white backdrop). **Rejected (7)**, sent to the Windows Recycle Bin: 4831678, 7760072, 9034585, 9558954, 40035918, 40738019, 6323266. The review page, its temporary server config and the `candidatos/` folder were removed.
**Docs:** `3 - Assets/referencias de pose/README.md` lists the six with size, fps, length, author and Pexels link (license: free for commercial use), and now points to `motion_W1_extract-pose_v3` (was the old v2 name).
**Note:** five of them are ~1:1.9 (1080×2048), a bit taller than 9:16; W1 v3 keeps the ratio (544×1024 skeleton), so check the W5 framing on the first run. Next: W1 v3 on each → `catalog.py pose <pose>`.

## 2026-11-25 — #65 W7 runs: x4 on a 1200 px image is too big; x2 v3 on the same image is good
**x4 v2 run** (the user) on `IN/Office Discussion Scene.png` (1200×840 → 4800×3360, 16 MP): the SR step itself took 25 s, but the VAE decode at that size filled the 24 GB and crawled; the user interrupted it after ~4 min (only `OUT/image-sr/x4/bicubic_00002_.png` saved). Confirms the x4 rule: input ≤ ~600 px. For bigger outputs a tiled VAE encode/decode version would be needed.
**x2 v3 run** (the user) on the same image → `OUT/image-sr/x2/kandinsky_00001_.png` (2400×1680) in **17 s** (models cached). First run of v3 (new `image-sr/` prefixes OK).
**Image:** faces clearly sharper (hair strands, brows, eyes, skin, glasses frames and earring), hands and sweater knit cleaner, binders in the background crisper while staying soft. The out-of-focus foreground and the blurred man on the left **stay out of focus** (the model respects the depth of field; only small highlights on the glasses get a bit crisper). Colors kept (mean abs difference 1.6/255 at the input size).
**Comparison** in `OUT/image-sr/x2/`: `compare_office_original_vs_kandinsky-x2.jpg` (whole image, stacked) and `compare_office_original_vs_kandinsky-x2_zoom.jpg` (man's face, woman's face, hands, binders, out-of-focus man).

## 2026-11-25 — #64 W7 image SR gets its own folders (v3 / x4 v2), out of motion/
**User's decision:** image SR is not part of the motion flow, so its files leave `motion/`.
**Moved (nothing deleted):** `IN/motion/sr/*` → `IN/image-sr/` (frame0 and the 480×680 product test); `OUT/motion/sr/*` → `OUT/image-sr/` (x2 frame0 results and comparisons in `x2/`, the x4 run in `x4/`). The empty `motion/sr/` folders were removed.
**Created:** `build_W7_v3.py` → `W7_image-sr_v3_api.json` (x2, prefixes `image-sr/x2/kandinsky|bicubic`, default input `fernanda_ref.png`); `build_W7x4_v2.py` → `W7_image-sr-x4_v2_api.json` (x4, `image-sr/x4/…`, default input `image-sr/caramel-tank-jeans_front_480x680.png`). Same graph and values as v2 / x4 v1. `WF/motion_W7_image-sr_v3.json` and `WF/motion_W7_image-sr-x4_v2.json` (copies in `ui_tests/`) were made from the user's 21:56 saves of v2 / x4 v1 by changing only the two save prefixes, the x4 input and the note (ComfyUI was closed, so no `graphToPrompt()` this time; the widget values match the API JSONs).
**ComfyUI (`WF/`):** removed the superseded `motion_W7_image-sr_v1`, `_v2` and `-x4_v1` (the user's 21:56 saves are archived as `ui_tests/*_resaved-2026-11-25-2156.json`; identical copies checked before removal). `WF/` now has the 3 production workflows + W7 v3 + W7 x4 v2.
**Docs:** README (W7 side tool paragraph, models table + note ⁴), CLAUDE.md (W7 line).

## 2026-11-25 — #63 W7 image SR x4 v1 run: small photo ×4, strong result
**Run** (the user): `motion_W7_image-sr-x4_v1` on `IN/fernanda_ref.png` (406×483, not a multiple of 16 → the pad/crop fix of #62 worked) → `OUT/motion/sr/x4/kandinsky_00001_.png` + `bicubic_00001_.png`, 1624×1932, saved 21:53. W7 v2 (x2) has not run yet.
**Image:** from a very soft 406 px photo to a sharp portrait: eyes, lashes, teeth, lips, skin, the rib knit of the top and the book spines are rebuilt; colors kept (mean RGB within ~1 level, mean abs difference 4/255 at the input size). At x4 the model invents plausible detail (e.g. stronger lines around the eyes, exact tooth shapes, the knit ribs): good for a small reference, but it is reconstruction, not recovery.
**Comparison** in `OUT/motion/sr/x4/`: `compare_original_vs_kandinsky-x4.jpg` (whole image), `compare_original_vs_kandinsky-x4_zoom.jpg` (eyes/smile, top fabric, books).

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
