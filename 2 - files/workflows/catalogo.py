# Ponte entre os 3 workflows de producao (o ComfyUI so le arquivos da pasta input; os workflows salvam em output).
# Uso (python do venv do ComfyUI):  python -I -X utf8 catalogo.py <comando> ...
#   pose <pose>             W1 v2 -> catalogo: copia o pose/original/keyframes MAIS RECENTES de OUT/motion/catalogo/<pose>/
#                           para IN/motion/poses/<pose>/ com nomes fixos (pose.mp4, original.mp4, keyframes/...).
#   upscale <nome>          W5 v10 -> W6 v2: copia o video_*.mp4 mais recente de OUT/motion/producao/<nome>/
#                           para IN/motion/producao/<nome>.mp4.
#   comparativo <nome> <pose>  original | esqueleto | gerado (W4_lado_a_lado.py) -> OUT/motion/producao/<nome>/comparativo.mp4
#   lista                   mostra as poses do catalogo e os videos de producao.
# Nunca apaga nada. Se o destino ja existe, o anterior vira <arquivo>.anterior-<data>.
import sys, os, glob, shutil, subprocess, datetime

IN = r"D:\Comfy-Desktop\ComfyUI-Shared\input\motion"
OUT = r"D:\Comfy-Desktop\ComfyUI-Shared\output\motion"
AQUI = os.path.dirname(os.path.abspath(__file__))

def recente(padrao):
    fs = sorted(glob.glob(padrao), key=os.path.getmtime)
    if not fs:
        raise SystemExit(f"nada encontrado: {padrao}")
    return fs[-1]

def copia(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        guarda = f"{dst}.anterior-{datetime.datetime.now():%Y%m%d-%H%M%S}"
        os.replace(dst, guarda)
        print("  anterior guardado em", guarda)
    shutil.copy2(src, dst)
    print(" ", src, "->", dst)

def cmd_pose(pose):
    o, d = os.path.join(OUT, "catalogo", pose), os.path.join(IN, "poses", pose)
    copia(recente(os.path.join(o, "pose_*.mp4")), os.path.join(d, "pose.mp4"))
    copia(recente(os.path.join(o, "original_*.mp4")), os.path.join(d, "original.mp4"))
    for tipo in ("pose", "original"):
        fs = sorted(glob.glob(os.path.join(o, "keyframes", f"{tipo}_*.png")), key=os.path.getmtime)[-4:]
        for k, f in enumerate(sorted(fs), 1):
            copia(f, os.path.join(d, "keyframes", f"{tipo}-{k}.png"))
    print(f"ok - no W5 escolha motion/poses/{pose}/pose.mp4")

def cmd_upscale(nome):
    copia(recente(os.path.join(OUT, "producao", nome, "video_0*.mp4")), os.path.join(IN, "producao", f"{nome}.mp4"))
    print(f"ok - no W6 escolha motion/producao/{nome}.mp4 e use o nome {nome}")

def cmd_comparativo(nome, pose):
    d = os.path.join(IN, "poses", pose)
    gerado = recente(os.path.join(OUT, "producao", nome, "video_0*.mp4"))
    saida = os.path.join(OUT, "producao", nome, "comparativo.mp4")
    if os.path.exists(saida):
        os.replace(saida, f"{saida}.anterior-{datetime.datetime.now():%Y%m%d-%H%M%S}")
    subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(AQUI, "W4_lado_a_lado.py"),
                    os.path.join(d, "original.mp4"), os.path.join(d, "pose.mp4"), gerado, saida], check=True)

def cmd_lista():
    print("Poses no catalogo (IN/motion/poses):")
    for p in sorted(glob.glob(os.path.join(IN, "poses", "*", "pose.mp4"))):
        print("  ", os.path.basename(os.path.dirname(p)))
    print("Videos de producao (OUT/motion/producao):")
    for p in sorted(glob.glob(os.path.join(OUT, "producao", "*"))):
        print("  ", os.path.basename(p), "-", ", ".join(sorted(os.path.basename(f) for f in glob.glob(os.path.join(p, "*.mp4")))))

if __name__ == "__main__":
    a = sys.argv[1:]
    cmds = {"pose": (cmd_pose, 1), "upscale": (cmd_upscale, 1), "comparativo": (cmd_comparativo, 2), "lista": (cmd_lista, 0)}
    if not a or a[0] not in cmds or len(a) - 1 != cmds[a[0]][1]:
        raise SystemExit(__doc__ or open(__file__, encoding="utf-8").read().split("import")[0])
    cmds[a[0]][0](*a[1:])
