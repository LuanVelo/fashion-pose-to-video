# EXP-002 — skeleton aligned to the person (plan phase 4, H-a)

**Written before running. Approved by the user on 2026-11-27 ("alignment first").**

## Question
Does aligning the skeleton to the person of the product photo (size and position) remove the stage 1 face on the neck and reduce the stage 2 stripes?

## Why
EXP-001: W5 stage 1 keeps the product framing (person ~2–97 % of the height), the catalog skeletons are smaller and lower (head/eye line at 17–19 %, feet at 84–91 %). On navy + `w-turn-03` the skeleton's face points fall on the neck and klein paints a second face there. The stripes look like the same mechanism (the model draws what the skeleton marks where it is not on the body).

## Change (the only one)
The pose video is replaced by an **aligned copy** made by `01_pipeline/scripts/align_skeleton.py` (one uniform scale + shift for the whole video, from frame 0: head on the person's eye line, feet on the person's feet, same center; the scale is capped so no frame leaves the frame). Files: `input/motion/experiments/EXP-002/<product>__<pose>/pose.mp4`.

| Pair | Scale | Frame 0 skeleton (head–feet, share of height) | Note |
|---|---|---|---|
| caramel + `look-02` | 1.22 (capped) | 0.07–0.86 (person 0.02–0.98) | head and shoulders aligned, legs ~13 % short: she walks toward the camera, a full fit would push the end of the clip out of frame |
| navy + `look-02` | 1.22 (capped) | 0.07–0.86 (person 0.01–1.00) | same |
| caramel + `w-turn-03` | 1.22 | 0.07–0.97 (person 0.02–0.98) | full fit |
| navy + `w-turn-03` | 1.25 (capped) | 0.05–0.97 (person 0.01–1.00) | full fit (head 2 % higher) |

Everything else as EXP-001: W5 v20 unchanged, same 4 pairs, same video seeds (20261121, 111, 222), image seed fixed. **Baseline = EXP-001** (1:1 comparison per run).

## Pass criteria
As EXP-001 (whole video, review sheet + report + flags; same garment, same model, no extra parts or faces, follows the skeleton, no lines), plus: **no face on the neck in frame 0.**

## Reading the result
- Neck face gone on navy + `w-turn-03` → alignment fixes stage 1; the prep step must align every pose to every product.
- Stripes clearly fewer than EXP-001 (EXP-001: seed 222 failed 4/4, seed 20261121 2 partial + 1 fail) → alignment also helps stage 2.
- `look-02` (only head aligned) vs `w-turn-03` (full fit) tells whether a partial fit is enough.
- No change in stripes → stage 2 needs another fix (next: H-b prompt).

## Cost
12 runs × ~4 min ≈ 50 min of GPU.
