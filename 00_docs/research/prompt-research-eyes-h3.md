I need technical research (forums, GitHub issues, Reddit r/StableDiffusion and r/comfyui, the ComfyUI Discord, docs) on a face/eyes problem in video generated with pose transfer. Look for reports from people who have run into this and solutions that worked.

## Context
- ComfyUI 0.46 (native nodes only, no custom nodes), RTX 4090 24 GB.
- Pipeline: product photo (model wearing the garment) → FLUX.2 klein 9B generates the 1st frame in the pose → video with **MiniMax H3 ref2va** (`MiniMaxH3ReferenceToVideo` + `MiniMaxH3AddGuide` on frame 0) + **MiniMax H3 Fun ControlNet union** (`MiniMaxH3FunControlNetApply`, strength 1.0, start 0 / end 1) receiving a skeleton video.
- Skeleton extracted from the reference video with **SDPose wholebody** (`SDPoseDrawKeypoints`): body + hands + feet + head (nose, eyes, ears), without the 68 face points.
- Video 896×1600, 124 frames, 24 fps, 20 steps, res_multistep, guidance 1.0. The face is ~110 px wide; the eye ~20 px.

## Problem
The eyes sometimes end up in the wrong place or cross-eyed over the course of the video. The clothing stays faithful.

## What I've found so far
- Overlaying the skeleton on the ORIGINAL video, the eye/nose points fit perfectly. In the GENERATED video the face is lower and larger: the "eye" points land on the eyebrows and the "nose" between the eyes. In other words, the generated person has different head proportions from the person in the reference video, and the ControlNet pulls the eyes to the wrong position.
- Removing the face points (68 landmarks): changed nothing.
- Removing the whole head from the skeleton (`draw_head=False`): DISASTER — the ControlNet union started reading the figure as a line map and drew the skeleton lines on the clothes (seams, sleeves).
- Raising the resolution to 1088×1920: good face, but the clothing was swapped and it took 59 min.
- Upscaling the video (RelayVSR x2) doesn't fix it: it amplifies the defects.

## Questions
1. Is this misalignment between the skeleton's head and the generated face (difference in proportions between people) a known problem in pose transfer (Wan Animate, UniAnimate, MimicMotion, Animate Anyone, H3, pose ControlNet in video)? How is it usually solved? E.g.: "pose retargeting", normalizing/realigning the skeleton to the generated person's body.
2. Does lowering the ControlNet strength or end_percent (e.g. stopping at 50% of the steps) usually fix the eye/face without losing the motion?
3. Is there a way to adjust/reposition the skeleton's head points (or scale the skeleton) inside ComfyUI with native nodes?
4. Video "face fix" techniques that work with native ComfyUI nodes (e.g.: a second pass on the face only with a mask, temporal inpainting, a close-up face reference).
5. Has anyone reported the ControlNet union mistaking an incomplete skeleton for canny/lineart?

Answer in Portuguese, with source links, separating what is proven by reports from what is assumption. Prioritize solutions that run locally in ComfyUI.
