# Reference videos

The motion videos live in this folder, but **they are not versioned**: they are third-party content and are listed in `.gitignore`.

Used in the tests:
- `fashion-lookbook-look-02-video.mp4`: 724×1268, 30 fps, 5 s, model walking toward the camera. It's the `look-02` pose in the examples.
- `pozze_black-friday_DfEy39VA9dX.mp4`: 720×1280, 30 fps, 11 s, with a turn to the back and cut at the thigh. Not yet tested in production.

New catalog candidates (2026-11-25, approved by the user, not yet run in W1). Source: [Pexels](https://www.pexels.com/license/), free for commercial use, no attribution required (credited here anyway). Downloaded in HD, not 4K.

| File | Size | fps | Length | Content | Author / page |
|---|---|---|---|---|---|
| `pexels_3888256_…photo-shoot.mp4` | 1080×2048 | 25 | 15 s | Beige suit, plain studio backdrop, several poses | cottonbro studio · [3888256](https://www.pexels.com/video/a-woman-model-in-black-top-and-white-suit-posing-in-a-photo-shoot-3888256/) |
| `pexels_7507265_fashionable-woman-posing.mp4` | 1080×1920 | 25 | 7 s | Trousers + cardigan, beige backdrop, weight shifts | SHVETS production · [7507265](https://www.pexels.com/video/fashionable-woman-posing-7507265/) |
| `pexels_7760060_woman-standing-and-posing-at-the-camera.mp4` | 1080×2048 | 25 | 17 s | Jeans + coat opening, white backdrop | cottonbro studio · [7760060](https://www.pexels.com/video/woman-standing-and-posing-at-the-camera-7760060/) |
| `pexels_8798401_a-female-model-in-a-green-dress.mp4` | 720×1366 | 25 | 16 s | Short dress, dark backdrop | MART PRODUCTION · [8798401](https://www.pexels.com/video/a-female-model-in-a-green-dress-8798401/) |
| `pexels_8992290_woman-wearing-dress-spinning-around.mp4` | 1080×1920 | 25 | 17 s | Dress + turn (back view), clothing store background | Alena Darmel · [8992290](https://www.pexels.com/video/woman-wearing-dress-spinning-around-8992290/) |
| `pexels_9558748_a-man-standing-in-front-of-a-white-background.mp4` | 1080×2048 | 25 | 18 s | Man, white backdrop | MART PRODUCTION · [9558748](https://www.pexels.com/video/a-man-standing-in-front-of-a-white-background-9558748/) |

The 1080×2048 / 720×1366 files are slightly taller than 9:16 (~1:1.9). W1 v3 keeps the aspect ratio (longer side → 1024, multiple of 32 → 544×1024 instead of 576×1024), so check how W5 fits that skeleton on the first run.

A good reference video: one person, full body, static camera, good lighting, at least 5 s, ideally 24 fps and vertical 9:16.
To use it in ComfyUI, copy it to the `input/` folder and run `motion_W1_extract-pose_v3`, then `catalog.py pose <pose>`.
