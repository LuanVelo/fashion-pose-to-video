# EXP-008 — a new product: FARM Rio "Calça Jeans Giovanna" (third reference product)

**Requested by the user on 2026-11-28 ("vamos tentar uma modelo nova" + the product link).**

## Question
Does the best setup so far (EXP-006: product photo reframed to the pose + neutral video prompt, W5 v20 graph) hold on a new product and a new model?

## Product
`02_library/products/farm-giovanna-jeans/` (front photo 2000×2783 from the store page, internal test use only): light wide-leg jeans with a beaded drawstring, light grey T-shirt with a **colorful print** (the patterned product the plan asked for), white cap, yellow raffia bag, orange sandals. **Hand in the pocket** like the caramel product: a direct test of the frame-0 problem.

## Change in the prep step (found while preparing)
The silhouette-based reframing put the skeleton's eyes on the **cap** (the top of the person is the hat, not the head). `reframe_product.py` got a **keypoint mode**: SDPose keypoints of the product photo (`pose_keypoints.py extract`) and of the pose clip (EXP-004 `src_<pose>.json`), matching the **eye line and the ankles** instead of the silhouette. Overlays: `reviews/reframed_overlays.jpg` (eyes, shoulders and feet on the body for `w-turn-03`; `look-02` legs slightly shorter than hers).

## Runs
farm × `look-02` / `w-turn-03` × video seeds 20261121, 111, 222 = 6 runs (~22 min). Video prompt = EXP-006 `prompt.txt`; image seed fixed (20261121).

## Pass criteria
As before, with zoom on hands, arms and feet of frame 0 and the first second; plus: the T-shirt print kept (colors, layout) through the video and the turn.
