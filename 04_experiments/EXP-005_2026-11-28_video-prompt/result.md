# EXP-005 — video prompt, on the 4 runs that failed in EXP-003: result

Plan: `plan.md`. Exact prompts: `prompts.json`. Videos: `output/motion/experiments/EXP-005_2026-11-28_video-prompt/` (`A_*` and `B_*` runs with `report.mp4` and `review_sheet.jpg`; `compare_<pair>__s<seed>.mp4` = skeleton | EXP-003 | A | B).

## Verdicts (full review)
| Run | EXP-003 (current prompt) | A: motion words | B: no "stripes" |
|---|---|---|---|
| caramel + `w-turn-03` s20261121 | FAIL minor (tan streak on the thigh) | **PASS** (no streak, turn held) | **PASS** (no streak, turn held) |
| caramel + `w-turn-03` s222 | FAIL (returns to the front, white bar) | **PASS** (stays turned to the back, no bar) | PARTIAL (no bar, but returns to the front) |
| navy + `w-turn-03` s222 | FAIL (white stripes on the jeans) | **PASS** | **PASS** |
| navy + `look-02` s222 | PASS minor (faint seam line) | **FAIL: she turns around to the back, but the skeleton never turns** | **PASS** (no seam line) |

A: 3/4 · B: 3/4 clean (+1 partial) · EXP-003 on the same runs: 0/4 clean.

## Answer
**The prompt was a major cause of the remaining defects.** Both changes fixed most of the failing runs on their own:
- **B (remove the word "stripes"):** the stripes and the thigh streak are gone in every run. It does not help the model keep the turn (caramel s222 still returns to the front).
- **A (motion words):** fixes the turn and the stripes, but the new wording ("turning around … when the guide turns") made the model **turn on a pose that does not turn** (navy `look-02`). The text must not describe a specific movement: it must only say "follow the guide".

## Decision (proposed)
1. Remove "stripes" from the video prompt (B). Clear win, no side effect seen.
2. Replace the motion sentence with a **pose-neutral** one: drop "stands" and "subtle weight shifts, relaxed arms", and say only that she follows the pose guide exactly, with no movement named. Draft: "She follows the pose guide exactly, with a calm confident expression."
3. **EXP-006:** B + neutral motion sentence together, first on these 4 runs, then on the 8 runs that passed in EXP-003 (as the user asked: failures first, then the rest). If it holds on all 12 → build **W5 v21** (prompt change = new workflow version).

## Correction (2026-11-28, the user's catch)
The caramel `w-turn-03` runs (A and B, both seeds) have the **extra hand** from frame 0 (same frame 0 as EXP-003; the prompt does not touch stage 1). Corrected: A **1/4**, B **1/4** (+1 partial). The prompt findings (stripes, unwanted turn) still hold.
