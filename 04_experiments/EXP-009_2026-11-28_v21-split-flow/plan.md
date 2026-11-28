# EXP-009 — W5 v21 split flow (replicable: photo → prep → frame-0 candidates → choice → video)

**Run overnight on 2026-11-28 under the user's request ("rodar até resultado bom"; goal: a replicable workflow for any e-commerce photo, FARM as reference; checks stay human).**

## Flow under test (`01_pipeline/scripts/run_product.py`)
1. `prep` — photo keypoints, photo reframed to each pose (keypoint mode: eyes + ankles).
2. `frame0` — 6 first-frame candidates (`W5_frame0_v21`: v20 stage 1 + the arms/hands sentence) and a `candidates.html` page.
3. Choice of one candidate per pair (human review, zoom on hands, arms, feet, sleeves, accessories, painted lines).
4. `video` — `W5_video_v21` (v20 stage 2 + EXP-006 prompt, first frame from LoadImage), 2 video seeds each, plus `report.mp4`, review sheet and detail sheet.

## Pairs and chosen first frames
| Pair | Chosen seed | Rejected (reason) |
|---|---|---|
| caramel + `w-turn-03` | 1 | 5 (hand at the pocket) |
| navy + `w-turn-03` | 5 | 1, 3, 20261121 (long sleeves: product has 3/4), 2 (painted lines), 4 (third shoe) |
| farm + `w-turn-03` | 1 | — (all 6 good) |
| caramel + `look-02` | 3 | 1 (hand at the pocket) |
| navy + `look-02` | 3 | 1 (long sleeves), 4 (black cuffs), 5 (extra bracelets) |
| farm + `look-02` | 3 | — (all 6 good) |

Video seeds 20261121 and 111 → 12 videos.

## Pass criteria
Whole video with detail sheets (native-resolution crops of hands and feet every 12 frames): same garment and accessories as the product, same model, no extra parts / faces / objects, no painted lines, follows the skeleton.
