# EXP-004 — per-bone retargeting on top of reframing: result

Plan (with the method fixes made before running): `plan.md`. Runs, flags and the EXP-003 verdict of the same seed: `runs.csv`. Videos: `output/motion/experiments/EXP-004_2026-11-28_bone-retargeting/` (each run with `report.mp4` showing the retargeted skeleton; one `exp003-vs-exp004_<pair>.mp4` per pair). Frame-0 overlays: `reviews/retarget_frame0_overlays.jpg` (local).

## Verdicts, EXP-003 → EXP-004 (same seeds, same reframed product)
| Pair | s20261121 | s111 | s222 |
|---|---|---|---|
| caramel + `look-02` | PASS → PASS | PASS → PASS | PASS → PASS |
| navy + `look-02` | PASS → **FAIL** (stripes on the sleeves) | PASS → PASS | PASS (minor) → **FAIL** (seam lines) |
| caramel + `w-turn-03` | FAIL minor (thigh streak) → **PASS** | PASS → PASS | FAIL → PARTIAL (garment clean, returns to the front) |
| navy + `w-turn-03` | PASS → **FAIL** (shirt swap) | PASS → PARTIAL (returns to the front) | FAIL → FAIL |

Clean passes: **EXP-003 8 → EXP-004 6** (+1 partial).

## Answer
**Per-bone retargeting is not adopted.** The total got worse, and the effect depends on how well the product photo shows the body:
- **Caramel (better):** the thigh streak is gone and seed 222 lost its white bar. Her photo shows arms and legs; the measured ratios were plausible (shoulders 0.80: she is narrower than the source model).
- **Navy (worse):** 3 runs that passed now fail, and a **third shoe** came back in frame 0 of `w-turn-03`. In her photo the hands are behind the back, so arm lengths are guessed (forearm measured 0.72, then raised to 0.82 by the limb rule), and the head ratio went up to 1.10. Wrong measurements produce a skeleton that sits off her body, which is exactly the failure we are trying to avoid.
- This matches the caveat of the Wan-Animate authors: with 2D skeletons the posture of the person distorts the measured bone lengths, which is why they measure on edited **T-pose** images.

## Lesson
Retargeting only helps when the target's proportions are measured reliably. From an ordinary product photo (hands in pockets / behind the back, wide trousers) the measurement is the weak link; a bad measurement is worse than none. The reframing of EXP-003 (one uniform scale + position) is robust because it needs only the head, feet and center.

## Decision (proposed)
1. Keep **reframing (EXP-003) as the standard**; retargeting stays as a tool (`retarget_skeleton.py`, `pose_keypoints.py`), off by default.
2. Retargeting could come back only with a reliable target measurement (e.g. the product person regenerated in a neutral / T-pose by stage 1 and measured there), and only for products with visible limbs. Not a priority.
3. Keypoints as numbers are still useful: they enable the **pose curation** step (smoothing, left/right swaps, hands) and the frame-0 checks.
4. What remains (EXP-003): stripes in the `w-turn-03` back turn with some seeds. Next candidates, one at a time: skeleton without hands; ControlNet strength/end on the reframed setup; prompt without the conflicting motion words + garment description (H-b).
