# =====================================================================================
# STAGE6B -- read-only investigation of the nail / cap / first-web blocker candidates
# =====================================================================================
import bpy
import sys
import os
import json
import math
import numpy as np
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6b_common as B                                          # noqa: E402

OUTDIR = sys.argv[sys.argv.index("--") + 1:][0]
ctx = B.build_context()
V0 = ctx["V0"]
NV = ctx["NV"]
POLY = ctx["poly"]
EDGES = ctx["edges"]
own = ctx["own_r1a"]
FACE_AREA0 = [B.face_area(V0, p) for p in POLY]
EDGE_LEN0 = [(V0[a] - V0[b]).length for a, b in EDGES]
NAIL = sorted(ctx["nail_thumb"])
CAP = sorted(ctx["distal_cap"])
WEB = sorted(ctx["first_web"])
NAIL_FACES = [fi for fi in range(len(POLY)) if all(v in ctx["nail_thumb"] for v in POLY[fi])]

bpy.ops.wm.open_mainfile(filepath=B.HARNESS_R1)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
MW = ob.matrix_world.copy()
W = B.RB.read_object_weights(ob, NV)

vec = json.load(open(os.path.join(OUTDIR, "STAGE6B_OPPOSITION_VECTOR_AUDIT.json"),
                     encoding="utf-8"))
UNIT = np.array(vec["CMC_OPPOSITION_UNIT_ROTATION"]["coefficients_local_XYZ"], dtype=float)
UNIT = UNIT / np.linalg.norm(UNIT)

for case, cmc, mcp, ip in (("CMC_OPP_30", 30, 0, 0), ("FULL_OPP_L3", 30, 30, 15)):
    B.reset_pose(rig)
    q, _ = B.rotation_vector_to_quaternion(Vector(UNIT) * math.radians(cmc))
    pb = rig.pose.bones["THUMB_CMC_R"]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = q
    if mcp:
        B.set_local_axis_rotation(rig, "THUMB_MCP_R", -mcp)
    if ip:
        B.set_local_axis_rotation(rig, "THUMB_IP_R", -ip)
    B.update()
    V, _ = B.evaluate(ob, MW)
    print("=" * 90)
    print("CASE %s  cmc=%d mcp=%d ip=%d" % (case, cmc, mcp, ip))

    def top_edges(ids, n=6):
        s = set(ids)
        rows = []
        for k, (a, b) in enumerate(EDGES):
            if a in s or b in s:
                l0 = EDGE_LEN0[k]
                l1 = (V[a] - V[b]).length
                if l0 > 1e-18:
                    rows.append((l1 / l0, k, a, b, l0 * 1000, l1 * 1000))
        rows.sort(reverse=True)
        return rows[:n]

    for nm, ids in (("NAIL", NAIL), ("FIRST_WEB", WEB), ("DISTAL_CAP", CAP)):
        print("  -- %s top stretch edges --" % nm)
        for r in top_edges(ids):
            rat, k, a, b, l0, l1 = r
            print("     ratio %8.3f  e%-5d  v%-5d->v%-5d  bind %.6f mm -> %.4f mm  "
                  "|disp| vA %.3f vB %.3f  own(%s,%s)  wA=%s wB=%s"
                  % (rat, k, a, b, l0, l1, (V[a] - V0[a]).length * 1000,
                     (V[b] - V0[b]).length * 1000, own[a][:3], own[b][:3],
                     {g: round(x, 3) for g, x in W[a].items()},
                     {g: round(x, 3) for g, x in W[b].items()}))

    # rigid-fit residual (Kabsch) for nail, cap, and their union
    def rigid_resid(ids):
        A = np.array([[V0[i].x, V0[i].y, V0[i].z] for i in ids])
        Bp = np.array([[V[i].x, V[i].y, V[i].z] for i in ids])
        ca, cb = A.mean(0), Bp.mean(0)
        H = (A - ca).T @ (Bp - cb)
        U, S, Vt = np.linalg.svd(H)
        d = np.sign(np.linalg.det(Vt.T @ U.T))
        D = np.diag([1.0, 1.0, d])
        R = Vt.T @ D @ U.T
        fit = (A - ca) @ R.T + cb
        res = np.linalg.norm(fit - Bp, axis=1) * 1000.0
        size = float(np.linalg.norm(A - ca, axis=1).mean()) * 1000.0
        return res.max(), size, (res.max() / max(1e-9, size))

    for nm, ids in (("nail", NAIL), ("distal_cap", CAP), ("nail+cap", sorted(set(NAIL) | set(CAP)))):
        mx, size, rel = rigid_resid(ids)
        print("  rigid fit %-10s  max_residual %.6f mm  char_size %.3f mm  rel %.6f"
              % (nm, mx, size, rel))

    # web inverted faces
    inv = []
    for fi in [fi for fi, p in enumerate(POLY) if any(v in set(WEB) for v in p)]:
        nrm = B.face_normal(V, POLY[fi])
        n0 = B.face_normal(V0, POLY[fi])
        if nrm.dot(n0) < -0.5:
            a0 = FACE_AREA0[fi]
            inv.append((fi, round(nrm.dot(n0), 4),
                        round(B.face_area(V, POLY[fi]) / max(1e-18, a0), 4)))
    print("  web faces total=%d inverted(<-0.5)=%d : %s"
          % (len([1 for fi, p in enumerate(POLY) if any(v in set(WEB) for v in p)]),
             len(inv), inv[:10]))
print("INVESTIGATE_DONE")
