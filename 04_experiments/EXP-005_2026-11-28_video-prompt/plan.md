# EXP-005 — video prompt (plan phase 4, H-b), on the runs that failed in EXP-003

**Draft for the user's approval. Scope set by the user: test the failing runs first; the passing ones only after we see the result.**

## Question
Do the remaining stage-2 defects of EXP-003 (stripes on the garment, the model turning back to the front instead of following the turn) come from the **video prompt**?

## Why
The W5 v20 video prompt (node 215) has two suspicious parts:
1. **Motion words that fight the pose:** "The model … **stands** full body …", "She moves naturally following the pose guide: **subtle weight shifts, relaxed arms**". Nothing about turning; for a pose that turns to the back the text pulls toward "stay in front, move little". In EXP-003 the `w-turn-03` failures turn back to the front.
2. **The word "stripes":** "keep every garment … identical …, same colors, fabric texture, **stripes**, length and fit". It is in every video, also for plain garments, and stripes are the main defect we see. It probably comes from an early striped product.

One change per variant, so each cause is measured alone.

## Prompts (only node 215 changes; everything else = EXP-003)
**Current (EXP-003, baseline):**
> A fashion e-commerce video. The model from <Picture 1> stands full body on a plain light grey studio background, wearing exactly the outfit from <Picture 1>: keep every garment and accessory identical to <Picture 1>, same colors, fabric texture, stripes, length and fit, nothing added or removed. She moves naturally following the pose guide: subtle weight shifts, relaxed arms, calm confident expression. Static camera, whole body in frame from head to feet for the entire video, soft even studio light. Photorealistic, natural motion, no text.
>
> Audio: quiet studio room tone, no music, no speech.

**Variant A — motion words only:**
- "stands full body" → "is shown full body"
- "She moves naturally following the pose guide: subtle weight shifts, relaxed arms, calm confident expression." → "**She follows the pose guide exactly, including turning around and showing her back when the guide turns, with a calm confident expression.**"

**Variant B — the word "stripes" only:**
- "same colors, fabric texture, stripes, length and fit" → "**same colors, fabric texture, length and fit**"

## Runs (the 4 non-clean runs of EXP-003)
| Pair | Video seed | EXP-003 defect |
|---|---|---|
| caramel + `w-turn-03` | 20261121 | tan streak on the thigh (~1 s) |
| caramel + `w-turn-03` | 222 | turns back to the front; white bar on the jeans |
| navy + `w-turn-03` | 222 | white stripes on the jeans (back view) |
| navy + `look-02` | 222 | faint seam line on the jeans (minor) |

× 2 variants = **8 runs (~30 min)**. Same reframed product photos (`input/motion/experiments/EXP-003/<pair>/product.png`), catalog skeletons, W5 v20, image seed fixed.

## Pass criteria
As before (whole video; same garment, same model, no extra parts / faces / objects, follows the skeleton including the turn, no lines).

## Reading the result
- A fixes the turn and/or the stripes → the motion words were a cause.
- B removes the stripes → the word "stripes" was a cause.
- Both help → next run A+B together.
- If a variant fixes these runs, **then** run it on the 8 runs that passed in EXP-003 (to check it breaks nothing) before any new W5 version is built (prompt change = new workflow version, W5 v21).
