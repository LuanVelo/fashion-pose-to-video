# EXP-006 — "stripes" removed + pose-neutral motion sentence: result

Plan: `plan.md`. Prompt: `prompt.txt`. Runs: `runs.csv`. Videos: `output/motion/experiments/EXP-006_2026-11-28_neutral-prompt/` (each run with `report.mp4` and `review_sheet.jpg`; `exp003-vs-exp006_<pair>.mp4` = old prompt 3 seeds | new prompt 3 seeds).

## Verdicts (full review), EXP-003 → EXP-006
| Pair | s20261121 | s111 | s222 |
|---|---|---|---|
| caramel + `look-02` | PASS → PASS | PASS → PASS | PASS → PASS |
| navy + `look-02` | PASS → PASS | PASS → PASS | PASS minor → **PASS** (no seam, no unwanted turn) |
| caramel + `w-turn-03` | FAIL minor → **PASS** (no streak) | PASS → PASS | FAIL → **PASS** (turn to the back held) |
| navy + `w-turn-03` | PASS → PASS | PASS → PASS | FAIL → **PASS** (no stripes) |

**Clean passes: 12/12** (EXP-001 4, EXP-002 0, EXP-003 8, EXP-004 6). Step 1 (the 4 failures) 4/4, step 2 (the 8 passes) 8/8, no regression. The review flags marked none of the 12 (consistent with the human review).

## Answer
Reframing (EXP-003) + the corrected video prompt solve all the defects seen on these 4 pairs × 3 seeds: stripes, streaks, the lost turn and the unwanted turn. The prompt was asking for "stripes" on every product and its motion sentence fought turning poses.

## Remaining caveat
Caramel `w-turn-03`: frame 0 (stage 1) still keeps the product's hand in the pocket while the skeleton's arm hangs (see EXP-003 side note). No artifact appeared in the videos, but the mismatch is still there → keep the frame-0 check rule (compare frame-0 keypoints with the skeleton before stage 2).

## Decision (proposed)
1. **Build W5 v21** = W5 v20 graph with the new video prompt (node 215) — `build_W5_v21.py`, API JSON, UI workflow. Production stays v20 until the user approves v21.
2. The prep step (reframing the product to the pose) becomes part of the production flow (script now, later inside the orchestrator).
3. Scope of the evidence: 2 products × 2 poses × 3 seeds. Next validation: the 7 candidate poses and a third (patterned) product, per the plan phase 5.

## Correction (2026-11-28, the user's catch)
The 3 caramel `w-turn-03` runs have an **extra hand** from frame 0 (stage 1 copies the hand in the pocket and also draws the skeleton's hanging hand). Corrected count: **9/12 clean**, not 12/12. The other 9 were re-checked by the user: perfect. The prompt fix stands (stripes and turns); the remaining defect is a **stage-1 / frame-0** problem: product pose (hand in pocket) ≠ skeleton pose. In EXP-004 (retargeted skeleton) the same pair's frame 0 had no extra hand. The frame-0 check is now required, not optional.
Second catch (same day): navy + `look-02` s222 still has the **light line down the front of each jeans leg** (the same defect EXP-003 had as "minor seam"). It runs along the skeleton's leg lines and is stronger than the real front seam of the product jeans. Corrected count: **8/12 clean**. The product jeans do have a faint seam there, which makes this defect easy to miss and hard for the flags; the rule: compare the jeans against the product photo at full resolution, any line stronger than in the product = fail.
