# EXP-002 — skeleton aligned to the person: result

Plan: `plan.md`. Runs, flags and the EXP-001 verdict of the same seed: `runs.csv`. Videos: `output/motion/experiments/EXP-002_2026-11-27_skeleton-alignment/` (each run with `report.mp4` showing the aligned skeleton, `review_sheet.jpg`; one `exp001-vs-exp002_<product>__<pose>.mp4` per pair: EXP-001 3 seeds | aligned 3 seeds). Overlay of the aligned frame-0 skeletons on the products: `reviews/aligned_frame0_overlays.jpg` (local).

## Verdicts, EXP-001 → EXP-002 (same seeds)
| Pair | s20261121 | s111 | s222 |
|---|---|---|---|
| caramel + `look-02` | PASS → **FAIL** (garment swap) | PASS → **FAIL** (striped sweater) | FAIL → PASS* (hair cut by the frame) |
| navy + `look-02` | FAIL → PASS* (no waves; hair cut) | PASS → **FAIL** (faint lines) | FAIL → FAIL |
| caramel + `w-turn-03` | PARTIAL → PARTIAL | PASS → **FAIL** (lines painted on the body) | FAIL → FAIL |
| navy + `w-turn-03` | PARTIAL (neck face) → PASS* (**no neck face**, turn held; third shoe frames 0–40; hair cut) | PASS (neck face) → **FAIL** (striped cardigan) | FAIL → FAIL |

Clean passes: EXP-001 4 (+2 partial) → EXP-002 0 clean, 3 with a defect (+1 partial).

## Answer
- **Stage 1 face on the neck: fixed.** With the skeleton's face points on the eyes, klein no longer paints a second face.
- **Stage 2 stripes: not reduced.** The result per seed changed a lot (some fails became passes and the reverse), but overall it got worse: 4 seeds that passed now fail. Alignment is not the fix for the stripes.
- **New stage-1 defects caused by enlarging the skeleton:**
  - the person gets bigger, so the top of the hair is cut by the frame (3 runs);
  - a **third shoe** between the feet (navy + `w-turn-03`, all seeds): a foot point of the scaled skeleton lands between the two feet and klein draws a shoe there. Same mechanism as the neck face: **any skeleton point that does not sit on the body becomes an extra object.**
- `look-02` (only head and shoulders aligned, legs short) did not do better than the full fit.

## Lesson
The model draws whatever the skeleton marks where there is no body (face on the neck, third shoe, and probably the stripes in stage 2). The skeleton and the person must match **exactly**, and enlarging the skeleton to the product photo's framing pushes the body to the frame edges. Better direction: **leave the skeleton at its catalog size and bring the product photo to the skeleton's framing** (pad the photo so the person has the same size and margins as the skeleton) = plan H-c (standardized product framing), which also creates the margin the cut-by-frame rule needs.

## Decision (proposed)
1. `align_skeleton.py` stays as a tool (it fixes the neck face), but is **not** adopted as is.
2. **EXP-003 (H-c):** product photo reframed to the skeleton's size/position (padding on a plain background, done in the prep step), catalog skeleton unchanged; same 4 pairs × same 3 seeds; checks: neck face, extra objects, hair cut, stripes.
3. Stripes: still open. After H-c, test H-b (prompt) and the ControlNet settings again, now on top of a correct framing.
4. New automatic stage-1 check for the prep step / triage: count faces and shoes/feet in frame 0 (extra object = reject before stage 2).
