# EXP-004 — per-bone retargeting on top of reframing (plan phase 4)

**Draft for the user's approval. Nothing runs before it.**

## Question
On top of the EXP-003 setup (product photo reframed to the skeleton), does retargeting the skeleton **bone by bone** to the product person's proportions remove the remaining defects (streak where the skeleton arm crosses the body, stripes in the `w-turn-03` back turn) without breaking what already passes?

## Why
- EXP-003 fixed size and position (8/12 clean). What is left looks like **proportion / limb mismatch**: e.g. caramel `w-turn-03` s20261121, a streak on the thigh where the skeleton's forearm lies over the body.
- Literature (`00_docs/research/research-pose-misalignment.md`): Wan-Animate recommends per-limb retargeting when body proportions differ (length ratio of each limb); whole-skeleton rescaling breaks part correspondence (One-to-All); Animate-X: realignment is the biggest single gain. Sources are other models; this tests it on MiniMax H3 + Fun ControlNet.

## Method (new script `01_pipeline/scripts/retarget_skeleton.py`, native code only)
1. **Keypoints as numbers.** No native node saves them, so a script imports ComfyUI's own SDPose nodes (same model `sdpose_wholebody_fp16`, same settings as W1 v3) and writes OpenPose JSON for:
   - the **source clip** (`input/motion/poses/<pose>/original.mp4`, 124 frames, the frames W1 used);
   - the **target person**: the reframed product photo of EXP-003 (`input/motion/experiments/EXP-003/<pair>/product.png`).
   Check: redrawing the source JSON must reproduce the catalog `pose.mp4` (pixel difference ≈ 0), so we know the numbers are the same skeleton.
2. **Bone lengths.** Bones of the OpenPose body tree (neck–shoulders, shoulder–elbow, elbow–wrist, neck–hips, hip–knee, knee–ankle, ankle–foot points, neck–nose–eyes–ears), measured:
   - target: on the product photo, using for each bone the **longer of left/right** (foreshortening only shortens) and only keypoints with confidence ≥ 0.5;
   - source: on the source frame where the person is most frontal and upright (widest shoulders among the first frames).
   Ratio per bone = target / source. Bones not visible on the target (e.g. a hand in a pocket) use the **median ratio** of the reliable bones. Ratios outside 0.7–1.4 are clipped and reported.
3. **Retarget every frame.** Walk the tree from the root (mid-hip): each child joint = parent + (source bone vector × ratio). Angle and foreshortening of the source are kept (a bone that shortens in profile shortens the same way). Hands and face points move rigidly with their wrist / head and are scaled by the forearm / head ratio.
4. **Placement.** Per frame, translate so that the retargeted mid-hip follows the source mid-hip horizontally and the lowest foot stays on the source's floor line (no floating, no sinking). Frame 0 is then checked against the product person (overlay).
5. **Draw** with ComfyUI's own `KeypointDraw` and the W1 v3 settings (body + hands + feet + head, no face, stick width 4, score threshold 0.5) → `input/motion/experiments/EXP-004/<pair>/pose.mp4`, 576×1024, 124 frames, 24 fps.

## Checks before any GPU run (shown to the user)
- Overlay of the retargeted frame 0 on the reframed product for each pair: face points on the eyes, shoulders, elbows, hips, knees, feet on the body.
- Per-bone ratio table per pair.
- No frame touching the frame edge; no joint jumps (> 5 % of the height between two frames).

## Conditions
| | |
|---|---|
| Change (the only one vs EXP-003) | pose video = retargeted skeleton |
| Same as EXP-003 | W5 v20 unchanged; reframed product photo; 4 pairs (caramel / navy × `look-02` / `w-turn-03`); video seeds 20261121, 111, 222; image seed fixed |
| Baseline | **EXP-003** (1:1 per run); EXP-001 for reference |

## Pass criteria
As before (whole video; same garment, same model, no extra parts / faces / objects, follows the skeleton, no lines), plus: the movement still reads as the original pose (the retargeting must not change the motion itself).

## Reading the result
- More clean passes than EXP-003 (8/12), no new defect → adopt retargeting in the prep layer (reframe + retarget per product × pose).
- Same count → proportions were not the remaining cause; the back-turn stripes need a different fix (3D body for turns, ControlNet settings, prompt).
- New defects → note what the retargeting broke (e.g. wrong hidden-bone estimate) before any next step.

## Cost
- Keypoint extraction: a few minutes of GPU (only when ComfyUI is idle).
- 12 W5 runs ≈ 50 min.

## Side tests kept for later (one change at a time)
Skeleton without hands; ControlNet strength on the reframed setup; prompt without motion words + garment description (H-b).

## Approved, then adjusted before running (2026-11-28)
Approved by the user ("Approve EXP-004"). While building the skeletons, the checks showed three problems in the method; fixed **before** any W5 run:
1. **Source reference frame = frame 0**, not "the most frontal frame": in `look-02` the most frontal frame was 48, when she has walked closer, so the ratios mixed camera distance with proportions (everything ~15 % smaller). Frame 0 is the frame the product photo was reframed to.
2. **Foreshortened limbs on the target photo** (navy: hands behind the back, forearm ratio 0.72): the two segments of a limb share the larger ratio (foreshortening only shortens); the small head bones share one ratio.
3. **Floor anchor jumps:** the lowest foot changes during the turn (frames 64, 75–77) and the whole skeleton jumped up to 30 px → the vertical shift is smoothed (running median, 15 frames).

Checks after the fixes: keypoints redraw = catalog skeleton (w-turn-03: 2–5 px differences; look-02: identical extent); no frame touches the edge; new joint jumps: 0, except 1 frame in caramel `w-turn-03`. Ratios used (target/source): caramel `look-02` 0.92–1.06, caramel `w-turn-03` 0.80–1.08 (shoulders 0.80), navy `look-02` 0.89–1.10, navy `w-turn-03` 0.82–1.06. Overlays: `reviews/retarget_frame0_overlays.jpg` (local).
