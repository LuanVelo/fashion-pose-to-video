# EXP-003 — product photo reframed to the skeleton: result

Plan: `plan.md`. Runs, flags and the EXP-001 / EXP-002 verdicts of the same seed: `runs.csv`. Videos: `output/motion/experiments/EXP-003_2026-11-27_product-reframing/` (each run with `report.mp4` showing the reframed product, `review_sheet.jpg`; one `exp001-vs-exp003_<pair>.mp4` per pair: EXP-001 3 seeds | reframed 3 seeds). Overlay of the reframed products with the frame-0 skeleton: `reviews/reframed_product_overlays.jpg` (local).

## Verdicts (full review), EXP-001 → EXP-002 → EXP-003, same seeds
| Pair | s20261121 | s111 | s222 |
|---|---|---|---|
| caramel + `look-02` | PASS → FAIL → **PASS** | PASS → FAIL → **PASS** | FAIL → PASS* → **PASS** |
| navy + `look-02` | FAIL → PASS* → **PASS** (no waves) | PASS → FAIL → **PASS** | FAIL → FAIL → PASS (minor: faint seam line on the jeans) |
| caramel + `w-turn-03` | PARTIAL → PARTIAL → FAIL minor (tan streak on the thigh ~1 s; turn now held) | PASS → FAIL → **PASS** | FAIL → FAIL → FAIL (returns to the front, white bar) |
| navy + `w-turn-03` | PARTIAL (neck face) → PASS* → **PASS** (no neck face, turn held) | PASS (neck face) → FAIL → **PASS** (no neck face) | FAIL → FAIL → FAIL (stripes on the jeans, back) |

Clean passes: **EXP-001 4 · EXP-002 0 · EXP-003 8** (+1 with a minor defect).

## Answer
- **Stage 1 is clean in all 4 pairs:** no face on the neck, no extra shoe, head and feet inside the frame. Reframing the product photo to the skeleton is the stage-1 fix.
- **Stage 2 stripes dropped a lot:** `look-02` passes 6/6 (EXP-001: 3/6). What remains is concentrated in `w-turn-03`, mostly seed 222, in the turn to the back, plus one streak where the skeleton's arm crosses the product's hand-in-pocket (the product pose and the skeleton pose differ at frame 0).
- The results are also **more stable across seeds** (the 3 seeds of a pair look much alike), which fits the idea that the mismatch was amplifying the seed noise.
- **Cost:** the person is smaller in the frame (face ~25–30 % smaller); at 896×1600 the face is still sharp (checked on caramel `look-02` frame 60). The faint seam of the reframed navy photo did not show in the videos (stage 1 redraws the background).
- The review flags marked only 1 run (navy `w-turn-03` s222, correct) and missed 2 defects (the thigh streak and the white bar on caramel `w-turn-03` s222): human review still mandatory.

## Lesson
Match the reference to the skeleton, not the skeleton to the reference: scale and place the person of the product photo where the skeleton is (with its margins). This agrees with the literature advice "frame the reference like the driving pose" (`00_docs/research/research-pose-misalignment.md`).

## Decision (proposed)
1. **Adopt reframing** (`reframe_product.py`) as a standard step of the prep layer, per product × pose.
2. **EXP-004: per-bone retargeting on top of reframing**, to fix the remaining proportion/pose mismatches (arm over the hand-in-pocket, turn to the back), same 4 pairs × 3 seeds, baseline = EXP-003.
3. Production rule meanwhile: reframed product + 2–3 seeds + human review.
