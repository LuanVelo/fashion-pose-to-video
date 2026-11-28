# EXP-012 — pose pre-screen: rank candidate poses before generating

**Requested by the user on 2026-11-28:** get at least 2 more approved poses; use what EXP-000…011 taught us to analyze candidates before testing and to test only the ones with a high chance of working.

## Why
3 approved out of 27 poses; most of the waste came from poses that fail for reasons visible in the skeleton alone (turns, crossed arms, walking out, far-from-neutral start). These can be measured from keypoints, without generation.

## Source
The 131 local e-commerce source videos (`03_references/pose-videos/ecommerce/`, local only), not only the 30 clips already cut: **any 5.2 s window** of a video can be a pose. Videos already marked unusable in `review.json` (head cropped, close-ups) are skipped.

## Step 1 — keypoints for every source (no generation)
SDPose (same model as W1 v3, in-process via `pose_keypoints.py`) at 8 fps sampling over each whole video → one keypoints file per video. Runs only with ComfyUI idle. ~10–20 min of GPU.

## Step 2 — hard rules (a window is excluded if any fails); each rule comes from a past failure
| Rule | Measured as | Lesson |
|---|---|---|
| Frontal the whole window | both eyes + both shoulders detected; shoulder width ≥ 70 % of its frontal value in every frame | turns / profile are not followed (EXP-010/011, w-turn-03, the 3 set aside in #82) |
| Full body, inside the frame | head and ankles detected and ≥ 3 % from the edges in every frame | walking out (`w-walk-01`), cut head/feet |
| No crossed arms at frame 0 | wrists not on the opposite side of the body midline | three hands at frame 0 (`m-side-04`) |
| Stays in place | hip-center drift ≤ 15 % of the frame width | walk-in not followed (`w-walk-01`) |
| Skeleton complete | ≥ 95 % of frames with all body keypoints | missing skeleton (`w-hands-01`) |

## Step 3 — ranking of the windows that pass
- Frame 0 close to a neutral product pose (arms down, hands near the thighs) → higher.
- Some motion (arms/weight shift), not frozen → higher; very large limb motion → lower.
- Tag "hands on the body" (both wrists at the hips / pockets during the window) → valid only for products with free hands (user rule, EXP-011).
- At most 1 window per source video; prefer poses not similar to the 3 approved ones.

## Step 4 — human check before any generation
Contact sheet (original + skeleton every 12 frames) of the **top ~8**; Claude checks, then the user picks.

## Step 5 — test only the chosen ones
W1 v3 on the pre-cut clip → `catalog.py pose` → 9:16 crop → keypoints → `normalize_pose.py` → `run_product.py` (3 products, 6 first-frame candidates, 1 video seed), two-pass review. Goal: ≥ 2 new approved poses.

## Cost
Steps 1–4: ~30 min GPU + script work, no video. Step 5: ~12 min GPU per pose.
