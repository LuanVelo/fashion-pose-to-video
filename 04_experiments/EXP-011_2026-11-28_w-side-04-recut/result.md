# EXP-011 — `w-side-04` re-cut before the turn: result

Videos: `output/motion/video/<product>__w-side-04/s<frame0 seed>-v20261121-recut/`. Side by side with EXP-010 (both skeletons, 3 products): `output/motion/video/EXP-011_w-side-04_cut_vs_EXP-010.mp4` (local).

## Result
**The hypothesis holds: the turn was the only pose problem.** With the pose cut to 100 frames (0–4.17 s, before the turn at ~4.25 s), all 3 videos follow the skeleton to the end (hands to the hips, hands down, front). Up to frame ~92 the new videos are almost identical to EXP-010 (same first frame and seed); EXP-010 failed only where the old skeleton turned to profile and the video stayed frontal.

| Product | Claude | User |
|---|---|---|
| navy polo | PASS | PASS |
| caramel (tote in the hand) | partial: the bag floats in the air ~60–72 when both hands go to the hips | accepted |
| FARM (raffia bag in the hand) | partial: the bag changes shape ~48–84 | accepted |

## Decision (user, 2026-11-28)
"A mão ir ao corpo e segurar a bolsa é impossível de fato… vamos assumir que esse problema não é da geração mas do pedido em si." A pose that puts both hands on the body cannot also hold a bag: this is a mismatch between the product photo and the skeleton, not a generation defect. **`w-side-04` is validated** (with the cut) for products whose hands are free; poses with both hands on the body are not matched with products that carry an object in the hand.

## Change kept
- `trim_pose.py` (cut a pose to its first N frames) and `run_product.py video` (H3 length and frame sampler follow the pose frame count; `RUN_TAG` keeps runs apart). Videos of trimmed poses are shorter (here 4.2 s) at real speed.
