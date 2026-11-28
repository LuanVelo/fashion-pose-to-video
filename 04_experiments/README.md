# 04_experiments — every test, one folder each

A test is anything that is not a production delivery: a new setting, a new pose, a new product, a fix. Each one gets a folder `EXP-<nnn>_<yyyy-mm-dd>_<slug>/`, numbered in order, and follows the rules of the plan (`00_docs/plans/plan-2026-11-27-pose-catalog-and-inputs.md`, section 3).

## Folder content
| File | Written | Content |
|---|---|---|
| `plan.md` | **before** running | question, hypothesis, control, conditions, seeds, what confirms / refutes it, pass criteria |
| `runs.csv` | while running | one line per generation: name, product, pose, video seed, workflow + changed values, time, flags, verdict |
| `result.md` | after the review | what happened (with the review sheets), the answer to the question, the decision, the next step |
| `reviews/` | after each run | `review_sheet.jpg` copies — **local only, not versioned** (they show generated people from product photos) |

The videos stay in ComfyUI: `output/motion/experiments/EXP-<nnn>_…/<product>__<pose>__s<seed>/` (video, `report.mp4`, `review_sheet.jpg`, `review.json`). The local page `output/motion/reports.html` lists every generation (product | original | skeleton | generated).

## Rules (short)
1. `plan.md` first. One question per experiment.
2. 3 video seeds per condition (W5 node 221); the image seed stays fixed.
3. Review the whole video: `generation_review.py` sheet + flags, and the report video.
4. Every result is shown as a comparison.
5. Each experiment ends with a line in `CHANGELOG.md`; an approval also goes to `05_approvals/approvals.csv`.

## Index
| ID | Date | Question | Result |
|---|---|---|---|
| [EXP-000](EXP-000_2026-11-27_trial-chain/result.md) | 2026-11-27 | (no plan) trial-and-error chain on the new poses | garment drift with most new skeletons; process stopped, plan written |
| [EXP-001](EXP-001_2026-11-27_seed-baseline/result.md) | 2026-11-27 | are the failures systematic or seed luck? (2 products × 2 poses × 3 seeds) | **seed luck**: no pair 3/3; seed 111 passed all 4, seed 222 failed all 4 (stripes), also on `look-02` + caramel |
| [EXP-002](EXP-002_2026-11-27_skeleton-alignment/result.md) | 2026-11-27 | does aligning the skeleton to the product person fix the neck face and the stripes? | neck face **fixed**; stripes **not** (4 passes → 0 clean); new defects: hair cut by the frame, a third shoe → next: reframe the product to the skeleton (H-c) |
