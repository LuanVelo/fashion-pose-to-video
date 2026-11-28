# EXP-011 — `w-side-04` re-cut before the turn

**Requested by the user on 2026-11-28** after EXP-010 ("ao girar não acompanha… cortar a parte do vídeo original que gira e deixar a pose só até onde funcionaria" → "Yes, re-cut it").

## Hypothesis (one at a time)
The 3 `w-side-04` videos failed only because the last second of the pose turns toward the back (source `asos_210859472.mp4`: front 0–4.2 s, the turn starts at ~4.25 s, profile at 4.8 s, back at 5.6–7.2 s). Without the turn the pose works.

## Change
- Pose trimmed to its first **100 frames** (0–4.17 s at 24 fps): `pose.mp4`, `original.mp4`, `keypoints.json` (new `trim_pose.py`; old files kept as `.previous-<date>`). No W1 re-run: the skeleton is the same extraction, only shorter.
- `run_product.py video`: the H3 video length (node 216) and the frame sampler (node 211) follow the pose's frame count instead of a fixed 124 (queue-time override, the workflow file is unchanged). Real speed is kept: the video is 4.2 s instead of 5.2 s.
- Everything else as EXP-010: same prep images and the **same chosen first frames** (caramel s2, navy s4, FARM s1; frame 0 of the pose does not change), video seed 20261121.

## Runs
3 videos (~10 min).

## Pass criteria
Two checks (Claude, then the user): the generated motion follows the skeleton over the whole clip (hands to the hips and back), garment, hands (count), feet, face across frames, accessories. Compared side by side with the EXP-010 videos.
