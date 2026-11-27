"""Local comparison page for the pose catalog: original 5.2 s clip next to its skeleton, played in sync.

Scans IN/motion/poses/<pose>/ (pose.mp4 + original.mp4, made by W1 + `catalog.py pose`) and writes
IN/motion/poses/compare.html with relative links. The page stays local: the original clips are
third-party (e-commerce) videos and never go to the repository.

Usage (with ComfyUI's Python):  python -I -X utf8 pose_compare_page.py [plan.json]
  plan.json (optional): list of {pose, gender, type, clip, source_file, start} to show the source of each pose.
"""
import sys, os, json, html

POSES = r"D:\Comfy-Desktop\ComfyUI-Shared\input\motion\poses"

info = {}
if len(sys.argv) > 1:
    info = {p["pose"]: p for p in json.load(open(sys.argv[1], encoding="utf-8"))}

rows = []
for pose in sorted(os.listdir(POSES)):
    d = os.path.join(POSES, pose)
    if not (os.path.isdir(d) and os.path.exists(os.path.join(d, "pose.mp4"))):
        continue
    p = info.get(pose, {})
    rows.append({"pose": pose, "gender": p.get("gender", ""), "type": p.get("type", ""),
                 "source": f'{p.get("source_file", "")} @ {p.get("clip_start_in_source", p.get("start", ""))} s' if p else "",
                 "original": os.path.exists(os.path.join(d, "original.mp4"))})

page = """<!doctype html><meta charset="utf-8"><title>Pose catalog: original vs skeleton</title>
<style>
body{font:14px system-ui,sans-serif;margin:0;background:#111;color:#eee}
header{position:sticky;top:0;background:#1b1b1b;padding:10px 16px;display:flex;gap:12px;align-items:center;z-index:2;flex-wrap:wrap}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:14px;padding:14px}
.card{background:#1e1e1e;border-radius:8px;padding:8px}
.pair{display:flex;gap:6px}.pair div{flex:1;text-align:center;font-size:11px;color:#aaa}
video{width:100%;background:#000;border-radius:4px;display:block}
.t{font-weight:600;font-size:15px}.s{color:#999;font-size:12px}
button,select{background:#333;color:#eee;border:1px solid #555;border-radius:4px;padding:4px 10px;cursor:pointer}
</style>
<header><b>Pose catalog</b> <span id="n"></span>
<select id="fg"><option value="">all</option><option value="women">women</option><option value="men">men</option></select>
<select id="ft"><option value="">all types</option></select>
<button id="all">play all</button><button id="stop">pause all</button>
<label>speed <select id="sp"><option>1</option><option>0.5</option><option>0.25</option></select></label>
<span class="s">click a card to play it alone · both videos stay in sync</span></header>
<main id="grid"></main>
<script>
const R = __ROWS__;
const grid = document.getElementById("grid");
[...new Set(R.map(r => r.type).filter(Boolean))].sort().forEach(t => ft.insertAdjacentHTML("beforeend", `<option>${t}</option>`));
function pairs() { return [...grid.querySelectorAll(".card")].map(c => c._v); }
function render() {
  grid.innerHTML = "";
  const list = R.filter(r => (!fg.value || r.gender === fg.value) && (!ft.value || r.type === ft.value));
  n.textContent = `${list.length} poses`;
  for (const r of list) {
    const c = document.createElement("div"); c.className = "card";
    c.innerHTML = `<div class="t">${r.pose}</div><div class="s">${r.gender} · ${r.type} · ${r.source}</div>
      <div class="pair"><div>${r.original ? `<video src="${r.pose}/original.mp4" muted loop playsinline preload="metadata"></video>original` : "no original.mp4"}</div>
      <div><video src="${r.pose}/pose.mp4" muted loop playsinline preload="metadata"></video>skeleton</div></div>`;
    const v = [...c.querySelectorAll("video")]; c._v = v;
    if (v.length === 2) v[0].addEventListener("timeupdate", () => { if (Math.abs(v[1].currentTime - v[0].currentTime) > 0.08) v[1].currentTime = v[0].currentTime; });
    c.onclick = () => { const on = v[0].paused; pairs().flat().forEach(x => x.pause()); if (on) play(v); };
    grid.appendChild(c);
  }
}
function play(v) { v.forEach(x => { x.playbackRate = +sp.value; x.currentTime = 0; x.play(); }); }
all.onclick = () => pairs().forEach(play);
stop.onclick = () => pairs().flat().forEach(x => x.pause());
sp.onchange = () => pairs().flat().forEach(x => x.playbackRate = +sp.value);
fg.onchange = ft.onchange = render;
render();
</script>
"""
out = os.path.join(POSES, "compare.html")
open(out, "w", encoding="utf-8").write(page.replace("__ROWS__", json.dumps(rows)))
print(len(rows), "poses ->", out)
