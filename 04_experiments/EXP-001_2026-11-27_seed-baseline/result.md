# EXP-001 — seed baseline: result

Plan: `plan.md`. Runs and flags: `runs.csv`. Videos: `output/motion/experiments/EXP-001_2026-11-27_seed-baseline/` (each run with `report.mp4` and `review_sheet.jpg`; one `seeds_<product>__<pose>.mp4` per pair: skeleton | seed 20261121 | 111 | 222).

## Verdicts (full review, every 8th frame + report video)
| Pair | seed 20261121 | seed 111 | seed 222 |
|---|---|---|---|
| caramel + `look-02` (control) | PASS | PASS | FAIL (white lines on the jeans) |
| navy polo + `look-02` | FAIL (blue waves on the polo) | PASS | FAIL (white stripes on the jeans) |
| caramel + `w-turn-03` | PARTIAL (garment ok, does not stay turned to the back) | PASS | FAIL (jeans lighter, then striped) |
| navy polo + `w-turn-03` | PARTIAL (garment ok, turns back to the front; neck mark) | PASS (neck mark) | FAIL (white stripes on the jeans) |

## Answer
**H1: the result depends on the seed.** No pair is 3/3 the same. The seed explains more than the product or the pose in this sample: seed 111 passed all 4 pairs, seed 222 failed all 4 with the same "stripe" defect, seed 20261121 was mixed.

- The stripe defect is **not specific to the new poses**: it appears on the production pose `look-02` with the production product (caramel, seed 222).
- A re-run with the same seed gives the same video (EXP-000 vs EXP-001 at seed 20261121: mean difference 1–2 / 255 per pixel). Results are reproducible, so a good seed stays good for the same input.
- `w-turn-03` with seed 20261121 does not hold the turn to the back (the skeleton faces back from frame ~64 to the end).
- The red mark on the neck in every navy `w-turn-03` run comes from **frame 0 (stage 1)**, since it is the same in the 3 seeds: a separate defect of the first frame.

## Review flags
They missed 2 of the 6 failures: thin white lines on denim (caramel `look-02` s222, navy `w-turn-03` s222 with edge p90 1.03). Denim already has many edges, so the edge share hardly moves. The flags help, but **the human review of every video stays mandatory**. Possible improvement: compare against the product colors (white is not in the jeans) instead of frame 0.

## Decision (proposed)
The problem is **robustness**, not pose selection. Next:
1. **EXP-002 (plan phase 4, H-b):** video prompt without the motion words that fight the pose + a short garment description, same 4 pairs × same 3 seeds, so it compares 1:1 with this baseline (12 runs).
2. Production rule until then: generate **2–3 seeds per video** and keep the one that passes the review.
3. Stage 1 neck mark: a separate check on frame 0 (navy + `w-turn-03`).
