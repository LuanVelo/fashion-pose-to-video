# EXP-000 — trial-and-error chain on the new poses (2026-11-27)

**Recorded after the fact.** This was not a planned experiment: it is the chain of single-seed runs that led to the plan. Details: CHANGELOG #69. Videos: `output/motion/experiments/EXP-000_2026-11-27_trial-chain/`.

## What ran
W5 v20, one video seed each, only the name, product, pose and the tested value changed. See `runs.csv`.

## What we learned
- With most new skeletons, stage 2 changes the garment and paints the skeleton lines on it as stripes. Frame 0 (stage 1) is always right.
- The defect depends on the pose **and** the product (`look-02`: pass with caramel, fail with navy polo).
- Not the cause, alone (1 seed each): skeleton aspect ratio, ControlNet 0.45, skeleton at 80%, ControlNet end 0.25, turbo off.
- A model cut by the frame breaks frame 0 (`m-side-05`, `w-hands-01`).
- Turning to the back is not by itself the cause.

## Review flags on these runs
`runs.csv` has the `generation_review.py` flags of every run. They agree with the human review, with two limits found here:
- the flags compare each frame with **frame 0 of the video**: when the garment is already wrong at frame 0 (turbo off on `w-side-04`), they miss it → next version should also compare with the product image / stage 1 frame 0;
- they do not see faces or limbs (extra arms, extra face): human review only.

## Why it is not conclusive
One seed per condition, videos judged on 5–6 frames, no control per test. Every "pass" here must be re-checked.

## Decision
Stop trial and error. Plan approved: `00_docs/plans/plan-2026-11-27-pose-catalog-and-inputs.md`. Next experiment: EXP-001, seed baseline (plan phase 2).
