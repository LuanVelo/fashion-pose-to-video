# EXP-006 — "stripes" removed + pose-neutral motion sentence (plan phase 4, H-b)

**Written before running. Approved by the user on 2026-11-28 ("Run EXP-006").**

## Question
Does the combined prompt fix the 4 EXP-003 failures (like EXP-005 A/B did) **without** making a non-turning pose turn, and does it keep the 8 runs that already passed?

## Change (only node 215, video prompt; everything else = EXP-003)
- "stands full body" → "is shown full body"
- "same colors, fabric texture, stripes, length and fit" → "same colors, fabric texture, length and fit"
- "She moves naturally following the pose guide: subtle weight shifts, relaxed arms, calm confident expression." → "**She follows the pose guide exactly, with a calm confident expression.**" (no movement named)

Exact text saved in `prompt.txt`.

## Runs (order set by the user: failures first)
1. **Step 1:** the 4 non-clean EXP-003 runs (caramel `w-turn-03` s20261121, s222; navy `w-turn-03` s222; navy `look-02` s222).
2. **Step 2, only if step 1 is good (≥ 3/4 clean, no unwanted turn):** the 8 runs that passed in EXP-003.

Same reframed product photos, catalog skeletons, W5 v20 graph, image seed fixed, video seeds as in EXP-003.

## Pass criteria
As before (whole video; same garment, same model, no extra parts / faces / objects, follows the skeleton — including **not** turning when the skeleton does not turn — no lines).

## Reading the result
- 12/12 or close, no regression on the 8 → build **W5 v21** with this prompt (new workflow version; production stays v20 until the user approves).
- Turns lost again (as with B alone) → the neutral sentence is too weak for turns; next: per-pose motion hint written in the pose catalog (e.g. "turns to show the back") added only for poses that turn.
- Regressions on the 8 → compare with EXP-003 run by run before deciding.
