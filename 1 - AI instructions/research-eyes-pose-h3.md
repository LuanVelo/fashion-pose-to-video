# Research: wrong eyes/face in pose-transfer video (MiniMax H3 + Fun ControlNet)

Research date: 2026-11-22
Scope: ComfyUI 0.46, **native nodes only**, RTX 4090 24 GB, local execution.

---

## 1. Pipeline context

- Product photo (model wearing the garment) → **FLUX.2 klein 9B** generates frame 0 already in the pose.
- Video: **MiniMaxH3ReferenceToVideo** (ref2va) + **MiniMaxH3AddGuide** on frame 0 + **MiniMaxH3FunControlNetApply** (strength 1.0, start 0, end 1) receiving the skeleton video.
- Skeleton: SDPose wholebody → **SDPoseDrawKeypoints** with body, hands, feet and head (nose, eyes, ears), without the 68 face points.
- 896×1600, 124 frames, 24 fps, 20 steps, `res_multistep`, guidance 1.0.
- Face ~110 px wide and eye ~20 px.

## 2. Symptom and diagnosis

**Symptom:** the eyes sometimes end up in the wrong place or cross-eyed over the course of the video. The clothing stays faithful.

**Tests already done:**

| Test | Result |
|---|---|
| Skeleton overlaid on the ORIGINAL video | Eye and nose points fit perfectly |
| Skeleton overlaid on the GENERATED video | Face lower and larger: the "eyes" land on the eyebrows and the "nose" between the eyes |
| Remove the 68 face landmarks | No change |
| `draw_head=False` | **Disaster**: the ControlNet read the figure as a line map and drew the lines on the clothes (seams, sleeves) |
| Generate at 1088×1920 | Good face, but the clothing was swapped and it took 59 min |
| RelayVSR x2 upscale | Amplifies the defects |

**Diagnosis:** the generated person (coming from FLUX) has different head proportions from the person in the reference video. The ControlNet pulls the eyes toward the skeleton point positions, and ref2va/AddGuide pulls toward the actual face in frame 0. This conflict probably causes the intermittent wrong or cross-eyed look. The misalignment already exists in frame 0.

---

## 3. Research findings

Legend: **[PROVEN]** = documentation or public report. **[ASSUMPTION]** = inference not yet validated.

### 3.1 Proportion misalignment is a known problem **[PROVEN]**

- Wan-Animate paper: because the character and the reference video have different bone proportions and sizes, they do **pose retargeting** on the skeletons extracted from the reference video.
  https://arxiv.org/pdf/2509.14055
- One-to-All Animation paper: current methods (UniAnimate-DiT, Wan-Animate, MimicMotion, StableAnimator) require aligned reference–pose pairs. When retargeting fails, identity drifts. Their fix randomly replaces the facial structures of the poses during training, to **decouple identity and skeleton**. In other words, the face points carry the facial geometry of the source person.
  https://arxiv.org/html/2511.22940v2
- Issue on Kijai's GitHub (Wan Animate): "the system ends up trying to stretch the character to fit the skeleton". Suggested workaround: turn off parts of the skeleton, at the cost of motion fidelity.
  https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/1262
- Kijai's retargeting (custom) scales the head by the body's global factor. It has no dedicated head/face correction.
  https://deepwiki.com/kijai/ComfyUI-WanAnimatePreprocess/4.5-pose-retargeting-system
- The custom node "Pose Detection OneToAll Animation" refits the skeleton to the reference's proportions, limb by limb (use only as a method reference).
  https://comfy.icu/node/PoseDetectionOneToAllAnimation

### 3.2 ControlNet strength / end_percent

- **[PROVEN]** The official H3 Fun ControlNet docs only say to keep guidance at 1.0 and to raise strength above 1 only if the output drifts away from the control. They don't mention start/end.
  https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fun-controlnet
- **[PROVEN]** In VideoX-Fun, `control_context_scale` scales each control skip: 1.0 is the strongest, 0.0 turns it off.
  https://comfyui-wiki.com/en/news/2026-08-24-minimax-h3-fun-controlnet-union
- **[PROVEN]** For Z-Image Fun Union (same team), the recommended optimal range is 0.65–0.80.
  https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union
- **[PROVEN]** In images, pose ControlNet with strength 1.0 and end_percent 0.5 is a common setup.
  https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/discussions/50
- **[ASSUMPTION]** There is no report on H3 video that this fixes the eyes. Hypothesis: the early steps lock layout and motion, and the late ones do the face detail. So end 0.6–0.7 may release the face without losing the motion. Risk: the clothing or silhouette drifting slightly.

### 3.3 Editing the skeleton with native nodes

- **[PROVEN]** In `SDPoseDrawKeypoints`, `draw_body` and `draw_head` are independent. With `draw_head=False` + `draw_body=True`, you get the body without a head. With `draw_body=False` + `draw_head=True`, you get **only the head and the neck point**. Inputs: draw_body, draw_hands, draw_face, draw_feet, stick_width, face_point_size, score_threshold, draw_head.
  https://docs.comfy.org/built-in-nodes/SDPoseDrawKeypoints
- **[PROVEN]** There is no native node for editing `POSE_KEYPOINT`.
- **[ASSUMPTION]** Retargeting can be done with image layers (see plan, step B).

### 3.4 Face fix in video

- **[PROVEN]** The Fun ControlNet Union has **native inpainting**: with a mask on the `mask` input, the regions marked with 1 are regenerated under control of the optional `source_video`, and the rest of the frame stays fixed.
  https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fun-controlnet
- **[PROVEN]** HF discussion: H3 distorts small faces (the smaller the face in the frame, the worse). Close-ups and medium shots look good. ~1.0 MP is cited as the sweet spot with the turbo LoRA. Suggestions given: crop the region, re-render and blend with a feathered mask; denoise ~0.15 v2v for light cases; regenerate at a higher resolution instead of using a latent upscaler.
  https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/30
- **[PROVEN]** ComfyUI-H3-FaceRefine (custom) implements exactly a face detailer for H3. Useful parameters to copy:
  - crop = 2.5× the face height (face at ~40% of the crop), canvas from 512 to 768;
  - crop center smoothed over a 21-frame Gaussian window and size over 51 frames (prevents the crop from "breathing");
  - per-frame denoise: 1.0 for faces ≤30 px, 0.35 for ≥120 px;
  - paste with a feather 4–8 mask.
  https://github.com/Carasibana/ComfyUI-H3-FaceRefine

### 3.5 ControlNet union mistaking an incomplete skeleton for lineart

- **[PROVEN]** Union uses a single checkpoint for Canny/Depth/HED/MLSD/Pose (and more types in v2.0), with no type selector.
- **[PROVEN]** v2.0 (2026-09-22) adds Scribble, Layout and Gray and doubles the injection blocks. To use it, just swap the patch in ModelPatchLoader.
  https://comfyui-wiki.com/en/news/2026-09-22-minimax-h3-fun-controlnet-union-2
- **[ASSUMPTION]** No direct report was found. Inference: the model infers the type from the appearance; without a head, the figure looks like MLSD/Canny (thin lines on a black background), which explains the seams drawn on the clothes. **Never remove the head from the skeleton.**

---

## 4. Action plan (test order)

Rules for all tests: fixed seed and a short clip (~8–10 s or less) for comparison. Vary one thing at a time.

### A. Loosen the ControlNet (cheap)

Suggested matrix in `MiniMaxH3FunControlNetApply`:

| strength | end_percent |
|---|---|
| 1.0 | 0.7 |
| 1.0 | 0.6 |
| 0.8 | 1.0 |
| 0.8 | 0.7 |

Evaluate three things: eyes (position/cross-eyed), clothing fidelity and motion fidelity.
Also check whether the patch is Union v1 or v2.0.

### B. Manual head retargeting with layers (native nodes only)

1. Run SDPose on the **FLUX frame 0** and on **frame 0 of the reference video**.
2. Measure in both: neck→nose, distance between the eyes and nose position. Compute `escala = d_flux / d_ref` and the offset (dx, dy).
   - Note: the native nodes don't read keypoints numerically. Measure once by hand (overlay and measure in pixels) or in an external script. The transform is constant for the whole video.
3. Layer A: `SDPoseDrawKeypoints` with `draw_head=False` (body, hands and feet).
4. Layer B: `SDPoseDrawKeypoints` with `draw_body=False, draw_head=True` (head + neck).
5. Transform B: `ImageScaleBy` (scale) + `ImageCrop`/padding to pivot at the neck + offset (dx, dy).
6. Mask of B: `ImageToMask` → `ThresholdMask`.
7. `ImageCompositeMasked` of B over A (x, y = offset). This is the new `control_video`.
8. Validate by overlaying the new skeleton on the FLUX frame 0: the eye points should land on the eyes.

Limitation: the correction is fixed and doesn't follow strong head turns. The neck line may end up slightly broken, which should be acceptable.

### C. Second pass on the face only (native H3 inpaint)

1. Define a **fixed crop** (`ImageCrop`) that covers the head's trajectory in all frames (~330×330 px, about 3× the face width).
2. Enlarge the crop to ~768×768 (`ImageScale`, lanczos). This takes the face from ~110 px to ~250 px.
3. Run H3 + Fun ControlNet in inpaint mode:
   - `source_video` = the enlarged crop;
   - `mask` = feathered face oval (without covering the hair/neck so the rest isn't touched);
   - reference = face close-up cropped from the FLUX frame 0;
   - pose control cropped and enlarged with the same transform, or none. Test both.
4. Scale back to the original size and paste with `ImageCompositeMasked` + a feathered mask.
5. If the head moves a lot, the fixed crop won't work. In that case a tracking crop would be needed, as in H3-FaceRefine (custom node), or splitting the video into segments.

### D. Fallback

- Generate at 1088×1920 only if A to C fail (59 min and clothing swap).
- Don't use upscaling (VSR or latent) as a face fix.

---

## 5. Success criteria

- Stable eyes, not cross-eyed, across all 124 frames.
- Clothing faithful to the product photo (color, seams and cut).
- Motion faithful to the reference video.
- Render time close to the current one (896×1600).
