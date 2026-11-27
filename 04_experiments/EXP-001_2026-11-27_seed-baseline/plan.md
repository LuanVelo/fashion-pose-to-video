# EXP-001 — seed baseline (plan phase 2)

**Written before running. Approved by the user on 2026-11-27.**

## Question
Are the W5 v20 failures seen in EXP-000 **systematic** (the same product + pose always fails or always passes) or **seed luck**?

## Hypothesis
H0: the result of a product + pose pair does not depend on the video seed (3 of 3 the same).
H1: the result changes with the video seed.

## Conditions
W5 v20 (`01_pipeline/workflows/W5_quality_v20_api.json`) with **no setting changed**. Only the product, the pose, the output folder and the **video seed** (node 221) change. The image seed (node 120) stays at 20261121, so frame 0 is the same for the 3 seeds of a pair.

| Product | Pose | Video seeds |
|---|---|---|
| caramel-tank-jeans | `look-02` | 20261121, 111, 222 |
| navy-polo-jeans | `look-02` | 20261121, 111, 222 |
| caramel-tank-jeans | `w-turn-03` | 20261121, 111, 222 |
| navy-polo-jeans | `w-turn-03` | 20261121, 111, 222 |

Seed 20261121 repeats EXP-000, so it also checks that a re-run gives the same video.

**Control:** `caramel-tank-jeans` + `look-02` + seed 20261121 = the known good production result.

## Outputs
`output/motion/experiments/EXP-001_2026-11-27_seed-baseline/<product>__<pose>__s<seed>/`, each with the video, `report.mp4`, `review_sheet.jpg` and `review.json`. Plus one side-by-side video per pair with the 3 seeds.

## Review and pass criteria
Whole video (review sheet every 8th frame + report video + `generation_review.py` flags). A run passes only if all hold:
- same garment as the product in every frame (color, cut, texture, no new pattern or stripes);
- same model (face, hair);
- no extra body parts, faces or objects;
- follows the skeleton's movement;
- no skeleton lines visible.

## Reading the result
- **3/3 same verdict for every pair** → failures are systematic → plan phase 4 tests causes on the failing pairs.
- **Mixed verdicts within a pair** → seed matters → the problem is robustness: next experiments aim at anchoring the garment (prompt, description, skeleton alignment), and production needs several seeds + review.
- If the control fails → stop: the environment changed.

## Cost
12 runs × ~4.5 min ≈ 55 min of GPU.
