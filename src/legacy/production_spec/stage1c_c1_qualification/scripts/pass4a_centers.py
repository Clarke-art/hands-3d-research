# STAGE1C - Pass 4a: print slice blob centers at key stations (no renders)
import bpy, bmesh, json, math
from mathutils import Vector

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
bm = bmesh.new()
bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
W = [(mw @ v.co).copy() for v in bm.verts]
E = [(e.verts[0].index, e.verts[1].index) for e in bm.edges]

def slice_blobs(c, tol=0.010):
    pts = []
    for (i0, i1) in E:
        z0, z1 = W[i0].z, W[i1].z
        if (z0 - c) * (z1 - c) < 0:
            t = (c - z0) / (z1 - z0)
            p = W[i0] + (W[i1] - W[i0]) * t
            pts.append(Vector((p.x, p.y)))
    blobs = []
    used = [False]*len(pts)
    for i in range(len(pts)):
        if used[i]: continue
        comp=[i]; used[i]=True; q=[i]
        while q:
            j=q.pop()
            for k in range(len(pts)):
                if not used[k] and (pts[j]-pts[k]).length <= tol:
                    used[k]=True; comp.append(k); q.append(k)
        cen = sum((pts[k] for k in comp), Vector((0,0))) / len(comp)
        blobs.append((round(cen.x,4), round(cen.y,4), len(comp)))
    blobs.sort(key=lambda b: -b[0])
    return blobs

for z in [0.155,0.165,0.175,0.185,0.195,0.205,0.215,0.225,0.235,0.245,0.255,0.265,0.275,0.285,0.295,0.305,0.315,0.325,0.335,0.345,0.355,0.365,0.375,0.385,0.395,0.41,0.425]:
    bl = slice_blobs(z)
    print(f"z={z:.3f} nblobs={len(bl)} blobs={bl}")

# vertex z-extremes in x-windows to find tips precisely
import collections
print("--- tips: lowest z vertex per x-bin (bin=0.006) ---")
xb = collections.defaultdict(list)
for p in W:
    xb[round(p.x/0.006)].append(p)
tips = []
for k, ps in sorted(xb.items()):
    lo = min(ps, key=lambda p: p.z)
    tips.append((round(k*0.006,3), round(lo.z,4)))
print(tips)
print("PASS4A_DONE")
