# EXP-007 — frame-0 candidates: result

Frames: `output/motion/experiments/EXP-007_2026-11-28_frame0-selection/<pair>/<P0|P1>/s<seed>/` (stage 1 only, 6 image seeds × 2 stage-1 prompts × 4 pairs = 48). Prompt P1: `prompt_P1.txt`.

## Human review (zoom on hands, arms, feet, garment)
**caramel + `w-turn-03`** (the pair with the extra hand):
| Prompt | s1 | s20261121 | s2 | s3 | s4 | s5 | good |
|---|---|---|---|---|---|---|---|
| P0 (current) | ok | extra hand | ok | extra hand | extra hand | extra hand | 2/6 |
| P1 (+ arms/hands sentence) | ok | ok | skeleton lines painted | ok | ok | unclear (hand at the pocket) | 4/6 |

Other pairs (contact sheets): image seed **2** paints the skeleton lines on the clothes in several pairs (caramel `w-turn-03`, navy `w-turn-03`, both prompts); some seeds change details of the garment (navy polo: long sleeves or a mesh / black cuff on one sleeve; caramel `look-02` P0 s5: sleeves on a tank top). Defects of frame 0 are **seed-dependent** and varied (extra hand, painted lines, sleeves).

## Automatic score (keypoints vs skeleton)
**Does not detect the extra hand.** On caramel `w-turn-03` the 12 frames score 0.025–0.031 with good and bad mixed: the detector follows one arm per side (the hanging one, which matches the skeleton) and ignores the hand in the pocket. A skin-colour test at the product's wrist position overlapped too (good 0.34–0.49, bad 0.47–0.55). Neither is reliable enough to choose alone.

## Answer
- **P1 helps** (extra hand 4/6 → 1/6 unclear on the problem pair) → it goes into the stage-1 prompt of W5 v21.
- Frame-0 defects are many and seed-dependent; the cheapest reliable fix is **several candidates (~3–10 s each) + a choice**, before spending ~3.5 min on the video.
- The choice is **human for now** (the user's rule: "por enquanto somos nós que checamos"), on a contact page of the candidates; the keypoint score stays only as a pre-filter for gross pose errors.

## Decision
W5 v21 split into `W5_frame0_v21` (candidates) and `W5_video_v21` (video from the chosen frame 0) + `run_product.py` (prep → frame0 candidates page → video + review). Validation: EXP-009.
