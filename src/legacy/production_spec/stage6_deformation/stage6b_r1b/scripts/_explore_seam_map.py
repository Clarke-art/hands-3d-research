# =====================================================================================
# STAGE6B_R1B -- EXPLORATORY 6 (read-only): draw the 67 edges + chains + landmarks
# =====================================================================================
import os
import sys
import json

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S6D = os.path.join(PROD, "stage6_deformation")
for _p in (os.path.join(S6D, "stage6b", "scripts"),
           os.path.join(PROD, "stage5_production_rig", "stage5b_r1b", "scripts"),
           os.path.join(PROD, "stage5_production_rig", "stage5b_r1a", "scripts")):
    if _p not in sys.path:
        sys.path.append(_p)
import s6b_common as B                                              # noqa: E402

MM = 1000.0
OUT = os.path.join(S6D, "stage6b_r1b", "_tmp")
P = os.path.join(S6D, "stage6b_r1a_seam_provenance")
CA = json.load(open(os.path.join(P, "STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json"), encoding="utf-8"))
CB = json.load(open(os.path.join(P, "STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json"),
                    encoding="utf-8"))
LOG = []


def log(s):
    LOG.append(s)
    print("[EX6] " + s)


ctx = B.build_context()
ref = ctx["ref"]
NV = ctx["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
jf = ref["jf"]
AC = ref["AC"]
capids = sorted(set(ref["cap"]["thumb_cap_vertex_ids"]))

EA = [tuple(e["endpoints"].values()) for e in CA["edges"]]
EB = [tuple(e["endpoints"].values()) for e in CB["edges"]]


def proj(axis):
    def f(p):
        if axis == "D":
            return p.x, p.z
        if axis == "P":
            return -p.x, p.z
        if axis == "R":
            return -p.y, p.z
        return p.y, p.z
    return f


def draw(axis, name, box, W=1500, H=1100, chain="jf"):
    f = proj(axis)
    x0, x1, y0, y1 = box
    s = min((W - 40) / max(1e-12, x1 - x0), (H - 40) / max(1e-12, y1 - y0))
    a = np.zeros((H, W, 4), dtype=np.float32)
    a[:, :, :3] = 0.05
    a[:, :, 3] = 1.0

    def pos(p):
        u, v = f(p)
        return (20 + (u - x0) * s, 20 + (v - y0) * s)

    for i in range(NV):
        x, y = pos(V0[i])
        xi, yi = int(x), int(y)
        if 0 <= xi < W and 0 <= yi < H:
            a[yi, xi, :3] = (0.32, 0.34, 0.38)
    for i in ctx["nail"]:
        x, y = pos(V0[i])
        xi, yi = int(x), int(y)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 10 and 0 <= xi + dx < W and 0 <= yi + dy < H:
                    a[yi + dy, xi + dx, :3] = (0.95, 0.90, 0.25)          # nail = yellow
    for i in capids:
        x, y = pos(V0[i])
        xi, yi = int(x), int(y)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 10 and 0 <= xi + dx < W and 0 <= yi + dy < H:
                    a[yi + dy, xi + dx, :3] = (0.85, 0.20, 0.95)          # cap = magenta
    for i in ctx["first_web"]:
        x, y = pos(V0[i])
        xi, yi = int(x), int(y)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 10 and 0 <= xi + dx < W and 0 <= yi + dy < H:
                    a[yi + dy, xi + dx, :3] = (0.15, 0.95, 0.85)          # first web = cyan

    def seg(p, q, c, rad=1):
        x1_, y1_ = pos(p)
        x2_, y2_ = pos(q)
        n = max(2, int(np.hypot(x2_ - x1_, y2_ - y1_) * 1.5) + 1)
        for k in range(n + 1):
            t = k / n
            xi, yi = int(x1_ + (x2_ - x1_) * t), int(y1_ + (y2_ - y1_) * t)
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    if 0 <= xi + dx < W and 0 <= yi + dy < H:
                        a[yi + dy, xi + dx, :3] = c

    for (i, j) in EB:
        seg(V0[i], V0[j], (1.0, 0.35, 0.05), 1)                            # CLASS_B orange
    for (i, j) in EA:
        seg(V0[i], V0[j], (0.10, 0.95, 0.25), 1)                            # CLASS_A green
    # chains
    live = {}
    bl = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"].data.bones
    MWr = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"].matrix_world
    for b in bl:
        live[b.name] = (MWr @ b.head_local, MWr @ b.tail_local)

    src = jf if chain == "jf" else live
    for nm, c in (("THUMB_CMC_R", (1.0, 0.85, 0.15)), ("THUMB_MCP_R", (1.0, 0.65, 0.05)),
                  ("THUMB_IP_R", (1.0, 0.35, 0.0)), ("THUMB_TIP_R", (1.0, 1.0, 1.0)),
                  ("INDEX_MCP_R", (0.2, 1.0, 0.3)), ("INDEX_PIP_R", (0.1, 0.85, 0.35)),
                  ("INDEX_DIP_R", (0.1, 0.7, 0.4))):
        h = Vector(src[nm]["head"]) if chain == "jf" else src[nm][0]
        t = Vector(src[nm]["tail"]) if chain == "jf" else src[nm][1]
        seg(h, t, c, 2)
    img = bpy.data.images.new(name, width=W, height=H, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(a[::-1]).reshape(-1))
    img.filepath_raw = os.path.join(OUT, name)
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    log("wrote %s" % name)


mid = (V0[284] + V0[2189]) * 0.5
hw = 0.045
boxD = (mid.x - hw, mid.x + hw, mid.z - hw * 1100 / 1500, mid.z + hw * 1100 / 1500)
boxR = (mid.y - hw, mid.y + hw, mid.z - hw * 1100 / 1500, mid.z + hw * 1100 / 1500)
draw("D", "EX6_SEAM_DORSAL_ZOOM.png", boxD)
draw("R", "EX6_SEAM_RADIAL_ZOOM.png", boxR)
draw("P", "EX6_SEAM_PALMAR_ZOOM.png", (-(mid.x + hw), -(mid.x - hw),
                                       mid.z - hw * 1100 / 1500, mid.z + hw * 1100 / 1500))
json.dump({"log": LOG}, open(os.path.join(OUT, "EXPLORE_SEAM.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("EXPLORE6_DONE")
