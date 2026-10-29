# =====================================================================================
# STAGE6B_R1B -- EXPLORATORY 4: is the frozen joint-frame JSON consistent with the LIVE
#                R2A armature?  (read-only) + visual blob map
# =====================================================================================
import os
import sys
import json
import math

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
LOG = []


def log(s):
    LOG.append(s)
    print("[EX4] " + s)


jf = json.load(open(os.path.join(PROD, "stage4_blender", "stage4c_r2",
                                 "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
log("opening the ACTIVE Stage5B R1B master to read the LIVE armature")
bpy.ops.wm.open_mainfile(filepath=B.R1B_MASTER)
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
ob = bpy.data.objects["Hand  - Realistic"]
MWo = ob.matrix_world.copy()
NV = len(ob.data.vertices)
V0 = [(MWo @ v.co).copy() for v in ob.data.vertices]
MWr = rig.matrix_world.copy()

log("%-16s %-46s %-46s %10s" % ("bone", "jf head (world)", "LIVE head (world)", "delta_mm"))
live = {}
_ALL = [b.name for b in rig.pose.bones]
for n in _ALL:
    pb = rig.pose.bones[n]
    h = (MWr @ pb.head).copy()
    t = (MWr @ pb.tail).copy()
    live[n] = {"head": [round(x, 9) for x in h], "tail": [round(x, 9) for x in t]}
    jh = Vector(jf[n]["head"])
    jt = Vector(jf[n]["tail"])
    log("%-16s %-46s %-46s %10.4f" % (n, str([round(x, 5) for x in jh]),
                                      str([round(x, 5) for x in h]),
                                      (h - jh).length * MM))
    log("%-16s %-46s %-46s %10.4f" % ("  .tail", str([round(x, 5) for x in jt]),
                                      str([round(x, 5) for x in t]),
                                      (t - jt).length * MM))

# ---- blob map render (orthographic projections, numpy canvas)
capids = sorted(json.load(open(os.path.join(PROD, "stage5_production_rig", "stage5a_r2a",
                                            "THUMB_DISTAL_CAP_AUDIT.json"),
                               encoding="utf-8"))["thumb_cap_vertex_ids"])
BLOB_B = set(capids)
BLOB_A = set([284, 1752, 1343, 2741, 1450, 1449, 1451, 1379, 1384, 1397, 2788, 2789,
              1338, 1339, 1340, 1341, 1378, 1452, 1455, 1456, 2783, 2785, 2787, 282,
              2963, 2964, 297, 299, 339, 340, 342, 505, 37, 1383, 2740, 283, 281, 289])


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


def draw(axis, name, zoom=None, W=1400, H=1100):
    f = proj(axis)
    pts = [f(v) for v in V0]
    us = [q[0] for q in pts]
    vs = [q[1] for q in pts]
    if zoom:
        cx, cy, hw = zoom
        box = (cx - hw, cx + hw, cy - hw * H / W, cy + hw * H / W)
    else:
        box = (min(us), max(us), min(vs), max(vs))
    x0, x1, y0, y1 = box
    sx = (W - 40) / max(1e-12, x1 - x0)
    sy = (H - 40) / max(1e-12, y1 - y0)
    s = min(sx, sy)
    a = np.zeros((H, W, 4), dtype=np.float32)
    a[:, :, :3] = 0.06
    a[:, :, 3] = 1.0

    def P(p):
        u, v = f(p)
        return (20 + (u - x0) * s, 20 + (v - y0) * s)

    def dot(p, c, r):
        x, y = P(p)
        xi, yi = int(x), int(y)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy > r * r + 1:
                    continue
                X, Y = xi + dx, yi + dy
                if 0 <= X < W and 0 <= Y < H:
                    a[Y, X, :3] = c
    # base mesh
    for i in range(NV):
        dot(V0[i], (0.30, 0.32, 0.36), 1)
    for i in sorted(BLOB_A):
        dot(V0[i], (0.95, 0.20, 0.20), 3)
    for i in sorted(BLOB_B):
        dot(V0[i], (0.20, 0.55, 1.00), 4)
    # bone chain (live)
    for n, c in (("THUMB_CMC_R", (1.0, 0.9, 0.2)), ("THUMB_MCP_R", (1.0, 0.7, 0.1)),
                 ("THUMB_IP_R", (1.0, 0.4, 0.0)), ("THUMB_TIP_R", (1.0, 0.95, 0.85)),
                 ("INDEX_MCP_R", (0.3, 1.0, 0.4)), ("INDEX_PIP_R", (0.2, 0.9, 0.5)),
                 ("INDEX_DIP_R", (0.2, 0.8, 0.6)),
                 ("MIDDLE_MCP_R", (0.2, 0.7, 1.0)), ("MIDDLE_PIP_R", (0.2, 0.6, 1.0)),
                 ("MIDDLE_DIP_R", (0.2, 0.5, 1.0)),
                 ("RING_MCP_R", (0.9, 0.3, 0.9)), ("RING_PIP_R", (0.8, 0.2, 0.9)),
                 ("RING_DIP_R", (0.7, 0.2, 0.9)),
                 ("LITTLE_MCP_R", (1.0, 1.0, 1.0)), ("LITTLE_PIP_R", (0.8, 0.8, 0.8)),
                 ("LITTLE_DIP_R", (0.6, 0.6, 0.6))):
        h = Vector(live[n]["head"])
        t = Vector(live[n]["tail"])
        N = 400
        for k in range(N + 1):
            dot(h + (t - h) * (k / N), c, 2)
    img = bpy.data.images.new(name, width=W, height=H, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(a[::-1]).reshape(-1))
    img.filepath_raw = os.path.join(OUT, name)
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    log("wrote %s" % name)


draw("D", "EX4B_MAP_DORSAL.png")
draw("R", "EX4B_MAP_RADIAL.png")
zc = [sum(v.x for v in V0) / NV, sum(v.z for v in V0) / NV]
# zoom on the thumb distal region: centre on the midpoint of v284 / v2189
mid = (V0[284] + V0[2189]) * 0.5
draw("D", "EX4B_MAP_DORSAL_ZOOM.png", zoom=(mid.x, mid.z, 0.055))
draw("R", "EX4B_MAP_RADIAL_ZOOM.png", zoom=(mid.y, mid.z, 0.055))

json.dump({"log": LOG, "live": live, "blob_A": sorted(BLOB_A), "blob_B": sorted(BLOB_B)},
          open(os.path.join(OUT, "EXPLORE_LIVE.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("EXPLORE4_DONE")
