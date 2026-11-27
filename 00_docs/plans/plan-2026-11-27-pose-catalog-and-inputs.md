# Plan — make W5 reliable with new poses and new products (2026-11-27)

Status: **draft for the user's review. Nothing in it runs before approval.**

## 1. Why we stopped
On 2026-11-27 we ran ~20 W5 v20 generations in a trial-and-error chain (crop to 9:16, ControlNet 0.45, skeleton at 80%, ControlNet end 0.25, turbo off, 10-pose batch, second product). Three things went wrong:
- **No plan per test:** each run answered a new question, with no control and no repeat. Conclusions changed from run to run.
- **Weak review:** videos were judged on 5–6 frames, so defects were missed (a floating extra face, garment drift). Some poses were called "approved" when they were not.
- **Results shown alone,** not next to the product, the original and the skeleton.

## 2. What we know for sure (evidence, not guesses)
| Fact | Evidence |
|---|---|
| The pipeline itself still runs as before | control run `test_control_caramel_look-02` (W5 v20 defaults) = the known good result |
| W1 v3 ignores the clip start (ComfyUI 0.46.2 bug) | byte-identical outputs with different starts; workaround = pre-cut clip (#68) |
| With most new skeletons, stage 2 changes the garment and paints the skeleton lines as stripes | caramel: 4 of 10 poses fail clearly; frame 0 (stage 1) is always right |
| The defect also depends on the product | `look-02` passes with caramel, fails with navy polo (blue "waves" on the polo) |
| Not caused by: skeleton aspect ratio, ControlNet strength 0.45, skeleton scale, ControlNet end 0.25, turbo | one run each, all still failing (turbo off fixed 1 of 4, worsened 3) |
| A model cut by the frame breaks frame 0 | `m-side-05` (enters the frame), `w-hands-01` (arms leave the top edge) |
| Turning to the back is **not** by itself the cause | 5 poses with a back turn passed with caramel; `w-side-04` never turns and fails |

**What we do not know:** how much of each result is **seed luck**. Every test so far is one run.

## 3. Rules for every test from now on
1. **Written before running:** the question, the hypothesis, the control, and what result confirms or refutes it.
2. **Repeat:** each condition runs with **3 seeds**. One run proves nothing. Only the **video seed** changes (W5 node 221, "Video seed"); the image seed (node 120) stays at 20261121, so frame 0 is the same and only stage 2 varies.
3. **Full review:** a dense sheet of every 8th frame (16 frames) + the report video, not a few samples.
4. **Pass criteria (all must hold):** same garment as the product (color, cut, texture, no new pattern or stripes) in every frame; same model (face, hair); no extra body parts, faces or objects; follows the skeleton's movement; no skeleton lines visible.
5. **Always shown as a comparison:** `generation_report.py` (product | original | skeleton | generated) + a side-by-side video when comparing versions.
6. **Only after ComfyUI is idle,** and only after the user approves the test batch.

## 4. Phases

### Phase 0 — Fix the record (no GPU, ~30 min)
- The public catalog (`02_library/poses/`, commit `266ded8`) says the 26 poses work. Change it to **"extracted, not validated"**, with the W5 results so far (pass/fail per product) and the defects found.
- CHANGELOG #69: all tests of 2026-11-27 (what, settings, result), including the stop and this plan.
- Local state stays as it is: approved / rejected / untested folders in `input/motion/poses*`, 9:16 crop with the 4:5 originals kept as `.previous-…`.

### Phase 1 — Measurement tools (no GPU, ~1 h)
- **Dense review sheet** per generation (every 8th frame), saved next to `report.mp4`.
- **Two automatic flags** to help the human review (not to replace it):
  - *garment drift*: color/texture distance of the body region between frame 0 and each frame;
  - *skeleton leak*: saturated pixels with the skeleton palette hues that are not in frame 0.
- Calibrate both on runs we already have: known good (`test_control_caramel_look-02`) vs known bad (`caramel-tank-jeans_w-side-04`).

### Phase 2 — Baseline and seed variance (GPU ~55 min, 12 runs)
Question: *are the failures systematic or seed luck?*
| Product | Pose | Seeds |
|---|---|---|
| caramel | `look-02` | 3 |
| navy polo | `look-02` | 3 |
| caramel | `w-turn-03` | 3 |
| navy polo | `w-turn-03` | 3 |
Decision: if the good and bad results flip with the seed, the next work is robustness (more control on the garment), not pose selection. If they hold, the failure is systematic and Phase 4 tests the causes.

### Phase 3 — Input standardization (answers the user's 4 questions)
**Where:** a **preparation step outside ComfyUI** (Python, run before W5), with ComfyUI only doing the generation. Reasons: the checks are deterministic and testable, they fail early with a clear message (before 5 min of GPU), and they work the same for 1 or 20 products. ComfyUI stays a fixed, versioned generator.

1. **Product image format and resolution.** One standard: front, full body head to feet, one person, plain light background, ≥1024 px on the long side; normalized by the prep step to a fixed 9:16 canvas with the same head/feet margins as the skeletons (the size of the person in the frame must match the skeleton). Rejected automatically: cropped body, more than one person, too small, busy background.
2. **Garment description.** Test it, do not assume it: earlier lesson (v7) was that a description beat image 1 for the **first frame** (so it stays empty there). For the **video** prompt it may anchor the garment against the stripe drift. Phase 4 tests: no description vs a short factual description (type, color, material, pattern), written per product (by hand or generated by Claude from the product image, then checked).
3. **20 client products that work.** Not guaranteed by luck: (a) the prep step rejects bad inputs; (b) each product runs on a small fixed set of validated poses; (c) every output goes through the review sheet + flags; failures are re-run with another seed or another pose, never delivered unchecked. We also measure the pass rate per product type (light/dark, plain/pattern, dress/trousers).
4. **Different models.** Today the model comes from the product photo (image 1 has the model wearing the garment). For a model chosen independently of the product we need a separate identity input (new workflow version); this goes after the garment drift is solved.

### Phase 4 — Find the cause of the garment drift (only after Phase 2; one hypothesis at a time, 3 seeds each)
Ranked by evidence and cost:
- **H-a Skeleton vs person mismatch:** retarget the skeleton to the person in frame 0 (same height, position, shoulder width). Cheap, no download.
- **H-b Video prompt:** remove the motion words that fight the pose ("subtle weight shifts, relaxed arms") and add the garment description.
- **H-c Product framing:** standardized product image (Phase 3) vs raw.
- **H-d Skeleton style:** thinner lines, hands and feet off, or face points on (front/back cue).
- **H-e Other control signal** (depth via native Depth Anything 3): last, needs a 542 MB download and the user's go-ahead, and may copy the silhouette of the original garment.

### Phase 5 — Pose catalog validation (after a fix exists)
A pose is "validated" only if it passes on a fixed panel of **3 reference products** (light plain, dark plain, patterned) × 2 seeds, reviewed with the rules of section 3. Only validated poses go to the W5 list and to the public catalog as "validated".

## 5. Decisions needed from the user
1. Approve Phase 0 and 1 (no GPU).
2. Approve the Phase 2 batch (12 runs, ~55 min) and the 4 product/pose pairs.
3. The 3 reference products for Phase 5 (we have caramel and navy polo; a patterned one is missing).
4. Garment descriptions: written by you, or drafted by Claude and checked by you.
