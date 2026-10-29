# =====================================================================================
# STAGE6B_R1B -- EXPLORATORY 5 (read-only): geodesic field map + path v284 -> v2189
# =====================================================================================
import os
import sys
import json
import heapq

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
import r1a_common as RC                                             # noqa: E402

MM = 1000.0
OUT = os.path.join(S6D, "stage6b_r1b", "_tmp")
LOG = []


def log(s):
    LOG.append(s)
    print("[EX5] " + s)


ctx = B.build_context()
ref = ctx["ref"]
NV = ctx["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
own = ctx["own_r1a"]
jf = ref["jf"]
AC = ref["AC"]

eadj = {}
for a, b in EDGES:
    w = (V0[a] - V0[b]).length
    eadj.setdefault(a, []).append((b, w))
    eadj.setdefault(b, []).append((a, w))


def dij(src):
    d = {src: 0.0}
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in eadj.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                heapq.heappush(pq, (du + w, v))
    return d


def dij_prev(src):
    d = {src: 0.0}
    prev = {src: None}
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in eadj.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                prev[v] = u
                heapq.heappush(pq, (du + w, v))
    return d, prev


ptsT = AC["THUMB"]
ptsI = AC["INDEX"]

g284 = dij(284)
gB = dij(1076)
d, prev = dij_prev(284)
p = [2189]
while p[-1] != 284:
    p.append(prev[p[-1]])
log("geodesic path v284 -> v2189 : %d steps, %.3f mm" % (len(p), d[2189] * MM))
step = max(1, len(p) // 30)
for k in range(0, len(p), step):
    v = p[k]
    aT = RC.arc_of(ptsT, V0[v])
    aI = RC.arc_of(ptsI, V0[v])
    log("  v%-5d g=%7.2f  dT=%7.2f dI=%7.2f aT=%7.2f aI=%7.2f own=%s  xyz=%s"
        % (v, d[v] * MM, ref["dchain"][v]["THUMB"], ref["dchain"][v]["INDEX"],
           aT[0], aI[0], own[v], [round(x, 5) for x in V0[v]]))

capids = sorted(json.load(open(os.path.join(PROD, "stage5_production_rig", "stage5a_r2a",
                                            "THUMB_DISTAL_CAP_AUDIT.json"),
                               encoding="utf-8"))["thumb_cap_vertex_ids"])
mind = 1e9
argmin = None
for a in capids:
    for b in [284, 1752, 1338, 1343, 2741, 1450, 1449, 1451, 1379, 1384, 1397, 2788, 2789,
              1339, 1340, 1341, 1378, 1452, 1455, 1456, 2783, 2785, 2787, 282, 2963, 2964,
              297, 299, 339, 340, 342, 505, 37, 1383, 2740, 283, 281, 289]:
        dd = (V0[a] - V0[b]).length * MM
        if dd < mind:
            mind = dd
            argmin = (a, b)
log("min spatial distance blobB-cap <-> blobA-cluster = %.3f mm  (%s)" % (mind, argmin))

# ---------------- heat maps
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


def draw(axis, name, field, zoom=None, W=1400, H=1100, vmax=180.0):
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
    s = min((W - 40) / max(1e-12, x1 - x0), (H - 40) / max(1e-12, y1 - y0))
    a = np.zeros((H, W, 4), dtype=np.float32)
    a[:, :, :3] = 0.06
    a[:, :, 3] = 1.0
    # base cloud
    for i in range(NV):
        u, v = pts[i]
        xi, yi = int(20 + (u - x0) * s), int(20 + (v - y0) * s)
        if 0 <= xi < W and 0 <= yi < H:
            a[yi, xi, :3] = (0.22, 0.23, 0.26)
    for i in range(NV):
        t = min(1.0, max(0.0, field[i] * MM / vmax))
        c = (min(1.0, 2 * t), 1.0 - abs(2 * t - 1.0), min(1.0, 2 * (1 - t)))
        u, v = pts[i]
        xi, yi = int(20 + (u - x0) * s), int(20 + (v - y0) * s)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                X, Y = xi + dx, yi + dy
                if 0 <= X < W and 0 <= Y < H:
                    a[Y, X, :3] = c
    for i in capids:
        u, v = pts[i]
        xi, yi = int(20 + (u - x0) * s), int(20 + (v - y0) * s)
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                if dx * dx + dy * dy > 17:
                    continue
                X, Y = xi + dx, yi + dy
                if 0 <= X < W and 0 <= Y < H:
                    a[Y, X, :3] = (1.0, 1.0, 1.0)
    img = bpy.data.images.new(name, width=W, height=H, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(a[::-1]).reshape(-1))
    img.filepath_raw = os.path.join(OUT, name)
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    log("wrote %s" % name)


mid = (V0[284] + V0[2189]) * 0.5
draw("D", "EX5_GEO_v284_DORSAL.png", g284)
draw("R", "EX5_GEO_v284_RADIAL.png", g284)
draw("D", "EX5_GEO_v1076_DORSAL.png", gB)
draw("R", "EX5_GEO_v1076_RADIAL.png", gB)
draw("D", "EX5_GEO_v284_DORSAL_ZOOM.png", g284, zoom=(mid.x, mid.z, 0.05), vmax=200.0)
draw("R", "EX5_GEO_v284_RADIAL_ZOOM.png", g284, zoom=(mid.y, mid.z, 0.05), vmax=200.0)

json.dump({"log": LOG, "g284_v2189_mm": d[2189] * MM,
           "min_spatial_cap_to_blobA_mm": mind},
          open(os.path.join(OUT, "EXPLORE_GEO.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("EXPLORE5_DONE")
