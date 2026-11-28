# EXP-007 — automatic frame-0 selection (stage 1 only)

**Approved by the user on 2026-11-28 ("rodar até resultado bom", overnight). Adjusted by the user: the visual approval stays human ("por enquanto somos nós que checamos, igual estamos fazendo"); no VLM checker.**

## Goal (the user's requirement)
A **non-manual** fix for the frame-0 pose mismatch, that works the same for 100+ products: the system generates frame-0 candidates, scores them against the skeleton, keeps the best one or rejects the product with a reason. People only calibrate the rule once (this experiment) and approve final videos by sampling.

## Problem
With the reframed product photo, stage 1 (FLUX.2 klein KV, W5 nodes 104–123) sometimes copies the product's pose instead of the skeleton's: caramel + `w-turn-03` frame 0 has the hand in the pocket **and** the skeleton's hanging hand (extra hand) for the fixed image seed 20261121 (EXP-003/005/006). Every video made from that frame 0 inherits the defect.

## Questions
1. Does a different **image seed** give a correct frame 0, and how often (per pair)?
2. Does a **stronger stage-1 prompt** reduce wrong frames 0?
3. Do the **automatic checks** separate good from bad frames 0 the same way a careful human review does (zoom on hands, arms, feet, face)?

## Conditions (stage 1 only, ~3 s per image)
The W5 v20 API graph is sent **without the stage-2 nodes** (only what `SaveImage` node 123 needs), so ComfyUI renders only frame 0. Inputs as in EXP-006: reframed product (`input/motion/experiments/EXP-003/<pair>/product.png`), catalog skeleton, 4 pairs.

| Factor | Values |
|---|---|
| Image seed (node 120) | 6: 20261121 (current) + 5 new |
| Stage-1 prompt (node 104) | **P0** current; **P1** = current + "Arms, hands and legs must be exactly as in image 2: if image 2 shows the arms hanging, no hand is in a pocket, behind the back or on the hip. The person has exactly two arms and two hands." |
| Pairs | caramel / navy × `look-02` / `w-turn-03` |

4 pairs × 6 seeds × 2 prompts = **48 frames 0, ~3–5 min of GPU**.

## Automatic checks (all scripted, no human in the loop)
- **A. Pose score:** `pose_keypoints.py extract` on each frame 0 → distance between the generated keypoints and the skeleton's frame-0 keypoints (wrists, elbows, shoulders, hips, knees, ankles, nose), normalized by the body height; plus "hand on the body side": wrist position relative to the hip (catches hand in a pocket vs hanging).
- **B. (dropped by the user)** VLM body-part count — the approval stays a human review; extra hands are checked by eye with zoom.
- **C. Frame edges:** head and feet inside the frame (reuse the reframing numbers).

## Human calibration (once, this experiment only)
I review all 48 frames 0 with zoom on hands, arms, feet and face and mark good / bad (the reference). Then: how many bad ones A catches (target: all of them), how many good ones they wrongly reject (target: few).

## Reading the result → the production rule
- A agrees with the review → rule = "generate N frames 0 (N from question 1), keep the best one that passes A+C, otherwise reject the product with the reason". N chosen so that every pair gets at least one good frame 0.
- P1 reduces bad frames 0 → it goes into the stage-1 prompt of W5 v21.
- Only after this: generate the videos of the selected frames 0 (needs a W5 variant that takes a given frame 0 — split stage 1 / stage 2, the speed idea already in CLAUDE.md).

## Tools
`01_pipeline/scripts/frame0_select.py stage1 …` (stage 1 only, per image seed) and `… score <skeleton.json> <frames>` (keypoint distance to the skeleton frame 0).
