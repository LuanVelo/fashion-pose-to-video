# EXP-007 — automatic frame-0 selection (stage 1 only)

**Draft for the user's approval. Nothing runs before it.**

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
- **B. Body-part count:** the pose detector looks for one person, so an extra hand may not show in A. Second check with a **local vision-language model through ComfyUI's native `TextGenerate` node** (image input) using the model already on disk `qwen_2.5_vl_7b_fp8_scaled` (no download): fixed question "How many hands does the person have? Is any hand inside a pocket? Answer as JSON." Parsed automatically.
- **C. Frame edges:** head and feet inside the frame (reuse the reframing numbers).

## Human calibration (once, this experiment only)
I review all 48 frames 0 with zoom on hands, arms, feet and face and mark good / bad (the reference). Then: how many bad ones A, B, A+B catch (target: all of them), how many good ones they wrongly reject (target: few).

## Reading the result → the production rule
- A+B agree with the review → rule = "generate N frames 0 (N from question 1), keep the best one that passes A+B+C, otherwise reject the product with the reason". N chosen so that every pair gets at least one good frame 0.
- P1 reduces bad frames 0 → it goes into the stage-1 prompt of W5 v21.
- If B (VLM) is unreliable → test the larger local VLM (`qwen3vl_32b`, already on disk) before anything else.
- Only after this: generate the videos of the selected frames 0 (needs a W5 variant that takes a given frame 0 — split stage 1 / stage 2, the speed idea already in CLAUDE.md).
