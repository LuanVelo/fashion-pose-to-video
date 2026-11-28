# EXP-003 — product photo reframed to the skeleton (plan phase 4, H-c)

**Written before running. Approved by the user on 2026-11-27 ("Run EXP-003").**

## Question
If the product photo is brought to the skeleton's framing (person scaled down and placed where the skeleton is, with margins), do the stage 1 defects go away (face on the neck, extra shoe, hair cut) **and** do the stage 2 stripes drop?

## Why
EXP-002: aligning the skeleton to the photo fixed the neck face but enlarged the body to the frame edges (hair cut, third shoe) and did not reduce the stripes. Lesson: every skeleton point off the body becomes an extra object. Here the skeleton stays as in the catalog and the photo moves.

## Change (the only one)
Product image (W5 node 5) replaced by a reframed copy made by `01_pipeline/scripts/reframe_product.py` (person's eye line at the skeleton head, feet at the skeleton feet, same center; 9:16 canvas 1088×1920 filled with the photo's own background color, soft 24 px seam): `input/motion/experiments/EXP-003/<product>__<pose>/product.png`. The pose video is the **catalog skeleton, unchanged**.

| Pair | Photo scale | Person in the canvas (top–bottom) | Skeleton frame 0 (head–feet) |
|---|---|---|---|
| caramel + `look-02` | 0.51 | 0.16–0.84 | 0.19–0.84 |
| caramel + `w-turn-03` | 0.58 | 0.13–0.91 | 0.17–0.91 |
| navy + `look-02` | 0.62 | 0.16–0.84 | 0.19–0.84 |
| navy + `w-turn-03` | 0.71 | 0.13–0.91 | 0.17–0.91 |

Known side effects to watch: the person is smaller (face ~25–30 % smaller than in EXP-001); the navy photo has a background gradient, so a faint rectangle seam is visible in the reframed photo. `look-02` frame 0 is a walking step while the product person stands: stage 1 redraws the pose anyway.

Everything else as EXP-001 / EXP-002: W5 v20 unchanged, same 4 pairs, same 3 video seeds (20261121, 111, 222), image seed fixed. **Baselines: EXP-001 (original) and EXP-002 (aligned skeleton).**

## Pass criteria
As before (whole video; same garment, same model, no extra parts, faces or objects, follows the skeleton, no lines), plus in frame 0: no face on the neck, no extra shoe or foot, head and feet fully inside the frame.

## Reading the result
- Stage 1 clean in all 4 pairs → reframing is the stage-1 fix; it becomes the prep step's standard.
- Stripes clearly fewer than EXP-001 → the stripes also come from the skeleton/person mismatch.
- Stripes unchanged → stage 2 needs its own fix (prompt H-b, ControlNet settings), now on a correct framing.
- Face quality drop (smaller person) → note the cost; a later check can try a bigger canvas or a higher stage-2 resolution.

## Cost
12 runs × ~4 min ≈ 50 min of GPU.
