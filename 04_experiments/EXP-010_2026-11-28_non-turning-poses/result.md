# EXP-010 — non-turning poses with the W5 v21 flow: result

Videos: `output/motion/video/<product>__<pose>/s<frame0 seed>-v20261121/` (video, `report.mp4`, `detail_sheet.jpg`). Review page (local): `output/motion/video/EXP-010_review.html`. Per-run verdicts: `runs.csv`.

## Verdicts (two checks: Claude first, then the user; the user's verdict is final)
| Pose | caramel | navy polo | FARM | Decision |
|---|---|---|---|---|
| `w-side-05` | PASS | PASS | PASS | **validated** (3/3) |
| `w-side-04` | FAIL | FAIL | FAIL | does not follow the turn at the end → **re-cut the clip before the turn** and test again |
| `m-side-05` | partial (bag disappears) | FAIL (face defect) | partial (bag disappears) | partial; keep as a candidate |
| `m-side-04` | FAIL | FAIL | FAIL | **three hands at frame 0** in all three (crossed arms) → **isolated**, to be solved later as its own case |
| `w-walk-01` | FAIL | FAIL | FAIL | does not follow the motion at all (FARM: the bag floats alone at the start) → **rejected** |

**1 pose validated out of 5.** No painted lines and no garment swaps in the 15 videos.

## What Claude's check missed (the user caught it)
- `m-side-04`: three hands at frame 0 in all three chosen first frames. The crossed arms hide where each hand belongs; the zoom review of the candidates did not count hands.
- `w-side-04`: the generated video does not follow the turn at the end of the skeleton. Claude's sheets look at single frames (defects), not at whether the motion follows the skeleton.
- `w-walk-01`: the motion is not followed at all (Claude only saw the exit from the frame).
- `m-side-05` navy: the face changes during the video.
→ Next reviews compare the generated video with the skeleton (motion followed?) and count hands on frame 0 whenever arms cross or touch the body.

## Lessons
1. Poses whose frame 0 has crossed arms (or arms far from a neutral product pose) break stage 1 (extra hand). Candidate rule: flag them in the catalog and keep them out of the normal flow until a fix exists.
2. A partial turn (side pose ending in a turn) is not followed; cut the clip where the pose still works.
3. Walking poses (walk-in, leaving the frame) are not followed by stage 2 in this setup.
4. A bag carried in the hand disappears or changes when the pose uses both hands (known since v9).

## Next
- Re-cut `w-side-04` before the turn (W1 v3 with a pre-cut clip, start 0) and re-test.
- Decide the crossed-arms case (`m-side-04`) as its own experiment.
- Remaining candidate poses: `m-side-03`, `w-hands-02`, `w-side-01` (non-turning).
