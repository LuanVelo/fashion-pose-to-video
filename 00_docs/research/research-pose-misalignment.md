# Research — pose / body mismatch in pose-driven video (2026-11-27)

Why: in EXP-000…002 the model drew objects where the skeleton did not sit on the body (a face on the neck, a third shoe, skeleton lines turning into stripes). Before guessing more fixes, we looked for other people's experience. Sources at the end.

**Scope note:** our pipeline is **MiniMax H3 + the Fun ControlNet Union** (VideoX-Fun family), not Wan-Animate. The sources below come from other models (Wan-Animate, Animate-X, UniAnimate, MimicMotion, StableAnimator). What transfers is the **preprocessing method** (fixing the skeleton before any model sees it), which is model-independent; the closest relative of our setup is Wan "Fun Control" (same VideoX-Fun family, same kind of control video). No H3-specific report was found, so every fix here is a hypothesis to test on H3.

## What the literature and community report
1. **Skeleton vs reference mismatch (scale, position, proportions) is a known main cause of distortions and extra anatomy.**
   - Animate-X adds a pose rescale + realignment step; in its ablation, *pose realignment contributes the most*.
   - StableAnimator++ builds a whole benchmark of misaligned poses (random scale / shift / rotation) and shows that "alignment-free" methods (e.g. Animate-X) still distort under large misalignment.
   - A 2026 training-free method reports that large pose discrepancies make baselines *hallucinate extra limbs*; MimicMotion and StableAnimator show extra hands and wrong wrists in comparisons.
   - Practical guides: pick a reference whose body scale and position are close to the driving video; frame the reference like the pose (full body to full body).
2. **The standard fix is per-bone retargeting, not a single global scale.**
   - Wan-Animate (official): retargeting is *highly recommended in Animation Mode when body proportions differ*; it computes **the length ratio of each limb** between the two characters and rescales the driving skeleton's bones. Because 2D posture distorts bone lengths, they optionally measure on edited **T-pose** images. Not recommended in Replacement Mode.
   - UniAnimate-DiT scales the driver's bone lengths to the reference (reported unstable in edge cases).
   - One-to-All Animation criticizes whole-skeleton rescaling: it breaks the correspondence of body parts (consistent with our EXP-002).
   - Tools: kijai's ComfyUI-WanAnimatePreprocess (`retarget_image`, basic and FLUX-Kontext-based retargeting), ComfyUI-ProportionChanger — both are custom nodes (not allowed here), but the method can be reproduced in a script.
3. **Skeleton quality matters.** Filter low-confidence keypoints before drawing (lines to guessed joints create stray structure; our W1 already uses `score_threshold 0.5`). Hand keypoints are often wrong in fast moves / wide shots; some pipelines drop hands (`draw_hands: false`) because a clean body skeleton drives better. Check the pose video for swapped legs, missing hands, jumps.
4. **Control strength:** "prompt ignored = control too strong" (community guide). A stick figure carries no depth or contact, so clothing detail is filled in inconsistently.
5. **Turns / 3D:** 2D skeletons lose depth; papers use parametric 3D bodies (EMOSH) or 3D pose + view control. ComfyUI 0.46.2 has native SAM 3D Body nodes (model download needed).

**Not found:** a direct report of "skeleton lines turning into stripes on the garment". Our closest explanation is the same mechanism as extra limbs: the model renders the skeleton where it does not match the body.

## What it means for our plan
- EXP-003 (reference framed like the skeleton) = the "choose / frame the reference like the driving pose" advice. Running.
- **Next: EXP-004 per-bone retargeting (Wan-Animate method)** — the best-supported fix: limb-length ratios measured on a frontal frame of the source and on the product photo, angles kept, feet on the floor.
- Cheap side tests: skeleton without hands; check keypoint confidence/jumps in our catalog.
- Larger options later: SAM 3D Body (native, needs a model) for turns; Wan Animate (plan B, not downloaded, ~26 GB) which has retargeting built in.

## Sources
- StableAnimator++ (pose misalignment): https://arxiv.org/html/2507.15064v1
- Animate-X: https://arxiv.org/html/2410.10306
- One-to-All Animation: https://arxiv.org/html/2511.22940
- EMOSH: https://arxiv.org/pdf/2606.28026
- Screen, Cache, and Match (extra limbs under pose discrepancy): https://arxiv.org/html/2601.22160
- MimicMotion (confidence-aware pose guidance): https://arxiv.org/html/2406.19680v1
- Human video generation with 3D pose and view control: https://arxiv.org/html/2602.21188
- Wan-Animate paper: https://arxiv.org/html/2509.14055 ; official preprocess guide: https://github.com/Wan-Video/Wan2.2/blob/main/wan/modules/animate/preprocess/UserGuider.md
- kijai ComfyUI-WanAnimatePreprocess (retargeting): https://deepwiki.com/kijai/ComfyUI-WanAnimatePreprocess/4.5-pose-retargeting-system
- ComfyUI-ProportionChanger: https://github.com/grmchn/ComfyUI-ProportionChanger
- ComfyUI Wan Fun Control docs: https://docs.comfy.org/tutorials/video/wan/fun-control
- Wan 2.2 Fun Control guide (control too strong): https://www.3dart.it/en/wan-tutorial-05-fun-control-en/
- WanVideo UniAnimate DWPose node (draw_hands): https://comfy.icu/node/WanVideoUniAnimateDWPoseDetector
