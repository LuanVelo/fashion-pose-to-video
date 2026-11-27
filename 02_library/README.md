# 02_library — the source of truth for inputs

Everything the generation uses, with its status. A file is only used in production when its status says so.

- `poses/` — pose skeletons (`<pose>/pose.mp4` + thumbnails) and `poses/catalog.csv` (one line per pose: origin, status, test results). See `poses/README.md`.
- `products/<product>/` — one folder per product:
  - `front.png` (and `back.png` when the video has a turn) — **not versioned** (may be a third-party photo);
  - `meta.json` — where the image comes from, status, notes;
  - `description.txt` — optional garment description (to be tested, plan phase 3/4).
- `models/` — (future) model identities, when the model is chosen apart from the product.

## Status values
| Status | Meaning |
|---|---|
| `candidate` | extracted / added, not validated yet |
| `validated` | passed the validation protocol (plan phase 5) |
| `rejected` | failed; kept with the reason |
| `untested` | extracted, never generated |

## Link with ComfyUI
ComfyUI only lists files from its `input` folder. The W5 lists read:
- `input/motion/poses/<pose>/pose.mp4` — `look-02` + the pose candidates (paths unchanged, so the production workflows keep working);
- `input/motion/poses_parked/rejected|untested/` — out of the W5 list;
- `input/motion/products/<product>_front.png`.
