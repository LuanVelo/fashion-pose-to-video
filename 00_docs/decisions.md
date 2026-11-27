# Decisions

One line per decision: date, decision, why, where it is detailed. Newest on top. (What changed in files goes to `CHANGELOG.md`; approvals of deliverables go to `05_approvals/approvals.csv`.)

| Date | Decision | Why | Details |
|---|---|---|---|
| 2026-11-27 | New folder structure: `00_docs`, `01_pipeline`, `02_library`, `03_references`, `04_experiments`, `05_approvals` | the project was hard to follow; tests, library and production were mixed | CHANGELOG #70 |
| 2026-11-27 | Every test is an experiment folder with a plan written first, 3 video seeds, full review, comparisons | ~20 single-seed runs gave contradictory conclusions | plan, CHANGELOG #69 |
| 2026-11-27 | Input standardization is a Python prep step **before** ComfyUI; ComfyUI only generates | deterministic checks, fail before spending GPU, same for 1 or 20 products | plan phase 3 |
| 2026-11-27 | Every W5 generation gets a report: product, original pose video, skeleton, generated | to see in practice what each generation does | CHANGELOG #69 |
| 2026-11-27 | Depth control (Depth Anything 3) postponed | may copy the original garment's silhouette; needs a 542 MB download | plan phase 4 (H-e) |
| 2026-11-27 | Pose skeletons are 9:16 (576×1024) like `look-02` | W5 renders 9:16; 4:5 skeletons were stretched | CHANGELOG #69 |
| 2026-11-27 | Use only the 5.2 s clips for now; 3 s clips kept apart | do not change the W1 → W5 flow while testing | CHANGELOG #67 |
| 2026-11-27 | Pose skeletons may be public; e-commerce originals never | originals are third-party | CHANGELOG #67, #68 |
| 2026-11-27 | Pose sources: fashion e-commerce (ASOS, Zalando) instead of stock video | stock video poses were not catalog-like | CHANGELOG #67 |
| 2026-11-22 | Production stays 100% local, native ComfyUI nodes only, no custom nodes | project goal phase 1 | CLAUDE.md |
| 2026-11-21 | A workflow change = a new version file; nothing overwritten | traceability | CHANGELOG (versioning rule) |
