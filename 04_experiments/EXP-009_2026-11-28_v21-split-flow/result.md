# EXP-009 — W5 v21 split flow: result

Videos: `output/motion/video/<product>__<pose>/s<frame0 seed>-v<video seed>/` (video, `report.mp4`, `review_sheet.jpg`, `detail_sheet.jpg`). Summaries: `output/motion/video/EXP-009_summary_look.mp4`, `EXP-009_summary_turn.mp4`. First-frame candidates: `output/motion/frame0/<pair>/candidates.html`.

## Verdicts (Claude's review of the detail sheets: native-resolution hands and feet every 12 frames; to be confirmed by the user)
| Pair | v20261121 | v111 |
|---|---|---|
| caramel + `look-02` | PASS | PASS |
| navy + `look-02` | PASS | PASS |
| farm + `look-02` | PASS | PASS |
| caramel + `w-turn-03` | PASS (no extra hand; turn to the back held; bag ok) | PASS |
| navy + `w-turn-03` | PASS (3/4 sleeves kept; turn held) | PASS |
| farm + `w-turn-03` | PARTIAL: garment and print ok, cap → headscarf with a bow and raffia bag reshaped from the back | PARTIAL (same) |

**10/12 clean, 2 partial** — the partials are the known "no back photo" limit of turning poses (EXP-008), not a pipeline defect. No extra hands, no painted lines, no garment swaps in any of the 12.

## What made the difference
1. Product photo reframed to the pose with keypoints (eyes + ankles).
2. Video prompt without "stripes" and with a pose-neutral motion sentence (EXP-006).
3. Stage-1 arms/hands sentence (EXP-007 P1).
4. **First frame chosen among 6 candidates** (~5 s each): the rejected candidates had long sleeves instead of 3/4, painted lines, an extra shoe, extra bracelets or a hand at the pocket. Choosing the first frame removes the main source of defects before the 3.5-min video.

## Review flags
The 4 FARM videos were flagged (drift 0.70–0.78) although 2 are clean: the light jeans and grey T-shirt are close to the white background, so the person mask is unreliable. The flags are not usable for light garments on white; the human review with detail sheets stays the gate.

## Next
- User review of the 12 videos (summaries first).
- Back photo for turning poses (FARM has more images on the product page; image 3 or 4 may be the back).
- More poses: validate the 7 candidate poses with this flow.
- UI workflows for W5 v21 (frame0 / video) so it can also be run from ComfyUI by hand.

## Approval
Approved by the user on 2026-11-28 ("Approved") after reviewing the 12 videos on `output/motion/video/EXP-009_review.html` → W5 v21 promoted to production (CHANGELOG #79).
