"""Bridge between the 3 production workflows.

ComfyUI only lists files from its `input` folder, while the workflows save to `output`.
This script copies results into `input` with fixed names, and builds comparison videos.

Usage (with ComfyUI's Python):  python -I -X utf8 catalog.py <command> ...
  pose <pose>               W1 -> catalog: copies the NEWEST pose/original/keyframes from OUT/motion/catalog/<pose>/
                            to IN/motion/poses/<pose>/ with fixed names (pose.mp4, original.mp4, keyframes/...).
  upscale <name>            W5 -> W6: copies the newest video_*.mp4 from OUT/motion/production/<name>/
                            to IN/motion/production/<name>.mp4.
  compare <name> <pose>     original | skeleton | generated (W4_side_by_side.py)
                            -> OUT/motion/production/<name>/compare.mp4
  list                      shows the poses in the catalog and the production videos.

Never deletes anything. If a destination already exists, the old file is kept as <file>.previous-<date>.
Edit IN and OUT below to match your ComfyUI input/output folders.
"""
import sys, os, glob, shutil, subprocess, datetime

IN = r"D:\Comfy-Desktop\ComfyUI-Shared\input\motion"
OUT = r"D:\Comfy-Desktop\ComfyUI-Shared\output\motion"
HERE = os.path.dirname(os.path.abspath(__file__))


def newest(pattern):
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    if not files:
        raise SystemExit(f"nothing found: {pattern}")
    return files[-1]


def keep_previous(path):
    if os.path.exists(path):
        kept = f"{path}.previous-{datetime.datetime.now():%Y%m%d-%H%M%S}"
        os.replace(path, kept)
        print("  previous file kept as", kept)


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    keep_previous(dst)
    shutil.copy2(src, dst)
    print(" ", src, "->", dst)


def cmd_pose(pose):
    o, d = os.path.join(OUT, "catalog", pose), os.path.join(IN, "poses", pose)
    copy(newest(os.path.join(o, "pose_*.mp4")), os.path.join(d, "pose.mp4"))
    copy(newest(os.path.join(o, "original_*.mp4")), os.path.join(d, "original.mp4"))
    for kind in ("pose", "original"):
        files = sorted(glob.glob(os.path.join(o, "keyframes", f"{kind}_*.png")), key=os.path.getmtime)[-4:]
        for k, f in enumerate(sorted(files), 1):
            copy(f, os.path.join(d, "keyframes", f"{kind}-{k}.png"))
    print(f"ok - in W5 pick motion/poses/{pose}/pose.mp4")


def cmd_upscale(name):
    copy(newest(os.path.join(OUT, "production", name, "video_0*.mp4")), os.path.join(IN, "production", f"{name}.mp4"))
    print(f"ok - in W6 pick motion/production/{name}.mp4 and use the name {name}")


def cmd_compare(name, pose):
    d = os.path.join(IN, "poses", pose)
    generated = newest(os.path.join(OUT, "production", name, "video_0*.mp4"))
    output = os.path.join(OUT, "production", name, "compare.mp4")
    keep_previous(output)
    subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(HERE, "W4_side_by_side.py"),
                    os.path.join(d, "original.mp4"), os.path.join(d, "pose.mp4"), generated, output], check=True)


def cmd_list():
    print("Poses in the catalog (IN/motion/poses):")
    for p in sorted(glob.glob(os.path.join(IN, "poses", "*", "pose.mp4"))):
        print("  ", os.path.basename(os.path.dirname(p)))
    print("Production videos (OUT/motion/production):")
    for p in sorted(glob.glob(os.path.join(OUT, "production", "*"))):
        vids = sorted(os.path.basename(f) for f in glob.glob(os.path.join(p, "*.mp4")))
        print("  ", os.path.basename(p), "-", ", ".join(vids))


if __name__ == "__main__":
    a = sys.argv[1:]
    commands = {"pose": (cmd_pose, 1), "upscale": (cmd_upscale, 1), "compare": (cmd_compare, 2), "list": (cmd_list, 0)}
    if not a or a[0] not in commands or len(a) - 1 != commands[a[0]][1]:
        raise SystemExit(__doc__)
    commands[a[0]][0](*a[1:])
