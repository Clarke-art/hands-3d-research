# =====================================================================================
# STAGE5B R1E -- READ-ONLY PROBE 8 : residual severe families of the current candidate
# =====================================================================================
import os
import sys
import json
import math
import bpy
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s5b_r1e_common as C                                          # noqa: E402

R1E = C.R1E
CAND = os.path.join(R1E, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend")
LAB = json.load(open(C.R3_FILES["r3_ownership_labels"], encoding="utf-8"))
R3 = list(LAB["R3"])
CB = json.load(open(C.PROBE_FILES["stage6b_r1a_class_b"], encoding="utf-8"))
HIST_B = set(e["edge_id"] for e in CB["edges"])
REGION = set(json.load(open(os.path.join(R1E, "STAGE5B_R1E_AUTHORISED_WEIGHT_REGION.json"),
                            encoding="utf-8"))["authorised_vertices"])
CM = dict((c["case_id"], c) for c in json.load(open(C.CASE_MATRIX, encoding="utf-8"))["cases"])

bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
ob0 = bpy.data.objects[C.MESH_OBJ]
mw0 = ob0.matrix_world.copy()
NV = len(ob0.data.vertices)
V0 = [(mw0 @ v.co).copy() for v in ob0.data.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in ob0.data.edges]
BIND = [(V0[a] - V0[b]).length * C.MM for a, b in EDGES]
BND = list(LAB["boundary_edges_R3"])
COLLAR = set()
for k in BND:
    COLLAR.update(EDGES[k])
adj = {}
for a, b in EDGES:
    adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
adj = dict((k, sorted(v)) for k, v in adj.items())
GD = C.rings_from(adj, COLLAR, 64)

bpy.ops.wm.open_mainfile(filepath=C.R2A)
o2, r2 = bpy.data.objects[C.MESH_OBJ], bpy.data.objects[C.RIG_OBJ]
mw2 = o2.matrix_world.copy()
LIVE = {}
for d, ch in C.BONE_CHAIN.items():
    p = [mw2 @ Vector(r2.data.bones[ch[0]].head_local)]
    for nm in ch:
        p.append(mw2 @ Vector(r2.data.bones[nm].tail_local))
    LIVE[d] = p
sT = [C.arc_of(LIVE["THUMB"], V0[i])[0] for i in range(NV)]
dT = [C.arc_of(LIVE["THUMB"], V0[i])[1] for i in range(NV)]
sI = [C.arc_of(LIVE["INDEX"], V0[i])[0] for i in range(NV)]
dI = [C.arc_of(LIVE["INDEX"], V0[i])[1] for i in range(NV)]

bpy.ops.wm.open_mainfile(filepath=CAND)
ob = bpy.data.objects[C.MESH_OBJ]
rig = bpy.data.objects[C.RIG_OBJ]
MW = ob.matrix_world.copy()
W = C.read_weights(ob, NV)

SEV_X, SEV_MIN = 5.0, 3.0
OUT = {}
for cid in ["TH_MCP_45", "CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]:
    C.reset_pose(rig)
    if cid == "TH_MCP_45":
        C.set_joint_rotation(rig, "THUMB_MCP_R", -45.0)
    else:
        c = CM[cid]
        q = c["cmc_quaternion_local"]
        pb = rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
        for bn, dg in (("THUMB_MCP_R", c["mcp_deg"]), ("THUMB_IP_R", c["ip_deg"])):
            if dg:
                p = rig.pose.bones[bn]; p.rotation_mode = 'QUATERNION'
                p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-dg))
    C.update()
    V = C.evaluate(ob, MW)[0]
    rows = []
    for k, (a, b) in enumerate(EDGES):
        if BIND[k] < SEV_MIN:
            continue
        r = (V[a] - V[b]).length * C.MM / BIND[k]
        if r <= SEV_X:
            continue
        rows.append({"edge": k, "ratio": round(r, 2), "bind": round(BIND[k], 2),
                     "a": a, "b": b, "aR3": R3[a], "bR3": R3[b],
                     "cB": k in HIST_B, "col": (a in COLLAR or b in COLLAR),
                     "areg": a in REGION, "breg": b in REGION,
                     "a_sT": round(sT[a], 1), "b_sT": round(sT[b], 1),
                     "a_dT": round(dT[a], 1), "b_dT": round(dT[b], 1),
                     "a_g": GD.get(a, -1), "b_g": GD.get(b, -1),
                     "aW": dict((g, round(v, 3)) for g, v in sorted(W[a].items())),
                     "bW": dict((g, round(v, 3)) for g, v in sorted(W[b].items()))})
    rows.sort(key=lambda t: -t["ratio"])
    OUT[cid] = {"n": len(rows), "rows": rows}
    print("== %s severe=%d" % (cid, len(rows)))
    fam = {}
    for t in rows:
        key = "|".join(sorted([t["aR3"], t["bR3"]])) + ("/cB" if t["cB"] else "") \
            + ("/col" if t["col"] else "") + ("/reg" if (t["areg"] and t["breg"]) else "")
        fam[key] = fam.get(key, 0) + 1
    print("   families:", json.dumps(fam, ensure_ascii=False))
    for t in rows[:12]:
        print("   e%-5d r=%-7.2f bind=%-5.2f %-6s/%-6s cB=%-5s col=%-5s reg=%s/%s g=%s/%s dT=%s/%s"
              % (t["edge"], t["ratio"], t["bind"], t["aR3"], t["bR3"], t["cB"], t["col"],
                 t["areg"], t["breg"], t["a_g"], t["b_g"], t["a_dT"], t["b_dT"]))
        print("        A", t["aW"])
        print("        B", t["bW"])

json.dump(OUT, open(os.path.join(R1E, "_tmp", "r1e_probe8.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("PROBE8_DONE")
