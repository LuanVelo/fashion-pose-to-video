# EXP-010 — validate the non-turning poses with the W5 v21 flow

**Requested by the user on 2026-11-28 ("vamos focar nas que não giram de costas" → "vamos começar a fazer isso").**

## Poses (no turn to the back; facing measured from the limb colors, CHANGELOG #69)
`m-side-04` (candidate), `w-side-05`, `w-walk-01` (untested), `w-side-04`, `m-side-05` (rejected in W5 v20, before the reframing and prompt fixes). `look-02` is already validated (EXP-009).

## Preparation (done before any video)
- `m-side-05`: the model entered the frame at frame 0 → clip re-cut from 1.5 s of the source (`input/motion/sources/m-side-05_clip_v2.mp4`), W1 v3 run again, cropped to 9:16; no frame touches the edge.
- Keypoints extracted for the 5 poses (`input/motion/poses/<pose>/keypoints.json`).
- **New step `normalize_pose.py`:** these 5 skeletons fill the frame (eye line at 0.07–0.11 of the height, ankles at 0.87–0.94), so the reframed product photos were cut (cap, feet). The pose (skeleton video, original video, keypoints) is scaled uniformly, anchored on the floor, to the framing of the poses that work (`look-02`, `w-turn-03`: eye line 0.145, ankles 0.875). Scales 0.85–0.94. Old files kept as `.previous-<date>`.
- Prep: 3 products × 5 poses reframed (keypoint mode); overlays checked.

## Runs
3 products (caramel, navy polo, FARM) × 5 poses × 6 first-frame candidates → one chosen per pair (zoom review) → 1 video seed (20261121) = 15 videos (~55 min). Second seed later, only for the poses that pass.

## Pass criteria
As in EXP-009 (detail sheets at native resolution: hands, feet, sleeves, accessories, print, painted lines, extra parts; follows the skeleton). A pose is **validated** when its 3 videos pass; the user confirms.

## Chosen first frames (Claude's zoom review of the 6 candidates per pair)
| Pose | caramel | navy polo | FARM | Rejected (examples) |
|---|---|---|---|---|
| `m-side-04` (crossed arms) | s4 | s3 | s3 | long-sleeve on caramel (s2), a pen / raffia in the second hand (s20261121), finger pointing (navy s4); the crossed-arm pose conflicts with the bag hand of caramel and FARM |
| `w-side-05` | s3 | s4 | s4 | black cuff / cut-out sleeve / extra shoe / long sleeves (navy s1, s3, s20261121) |
| `w-walk-01` | s3 | s2 | s1 | bag on the shoulder + pocket (caramel s1), beige sleeve (caramel s5), duplicated arm (FARM s2, s4) |
| `w-side-04` | s2 | s4 | s1 | extra shoe (navy s2, s3, s5, s20261121), long sleeves (navy s20261121), extra watch (FARM s5) |
| `m-side-05` | s2 | s4 | s4 | extra crossed shoe (caramel s1, s20261121), long sleeves (navy s20261121) |

## User observation during the run (2026-11-28)
`m-side-04`: the first pose (arms crossed) is very far from the product photos (a bag in one hand), so the generation "got lost". Candidate rule, **not applied now** (the user: keep the run as it is): exclude or flag poses whose frame 0 differs strongly from a neutral product pose (crossed arms, hands on the body, hands behind), or match each product to poses whose frame 0 is close to its photo. To be decided after EXP-010.
