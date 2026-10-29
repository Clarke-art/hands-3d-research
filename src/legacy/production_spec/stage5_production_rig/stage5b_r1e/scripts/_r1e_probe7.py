# =====================================================================================
# STAGE5B R1E -- READ-ONLY PROBE 7 : identity of the residual severe families
# =====================================================================================
import os
import sys
import json
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s5b_r1e_common as C                                          # noqa: E402

R1E = C.R1E
LAB = json.load(open(C.R3_FILES["r3_ownership_labels"], encoding="utf-8"))
R3 = list(LAB["R3"])
BND = list(LAB["boundary_edges_R3"])
CAP = set(LAB["CAP"]); NAIL_T = set(LAB["NAIL_THUMB"]); WEB = set(LAB["WEB"])
COLLAR = set()
bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
ob = bpy.data.objects[C.MESH_OBJ]
me = ob.data
MW = ob.matrix_world.copy()
NV = len(me.vertices)
V0 = [(MW @ v.co).copy() for v in me.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in me.edges]
for k in BND:
    COLLAR.update(EDGES[k])
W_B = C.read_weights(ob, NV)

bpy.ops.wm.open_mainfile(filepath=os.path.join(R1E, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend"))
obE = bpy.data.objects[C.MESH_OBJ]
W_E = C.read_weights(obE, NV)

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
sI = [C.arc_of(LIVE["INDEX"], V0[i])[0] for i in range(NV)]
dT = [C.arc_of(LIVE["THUMB"], V0[i])[1] for i in range(NV)]
dI = [C.arc_of(LIVE["INDEX"], V0[i])[1] for i in range(NV)]

REGION = set(json.load(open(os.path.join(R1E, "STAGE5B_R1E_AUTHORISED_WEIGHT_REGION.json"),
                            encoding="utf-8"))["authorised_vertices"])

adj = {}
for a, b in EDGES:
    adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
adj = dict((k, sorted(v)) for k, v in adj.items())
GD = C.rings_from(adj, COLLAR, 64)

FOCUS = [565, 1861, 1886, 1891, 1866, 3049, 3027, 2064, 2261, 2293, 2300, 2313,
         151, 1076, 2189, 2153, 694, 693, 1228]
O = {}
for v in FOCUS:
    O[str(v)] = {"R3": R3[v], "in_collar": v in COLLAR, "in_region": v in REGION,
                 "g_dist": GD.get(v), "sT": round(sT[v], 2), "dT": round(dT[v], 2),
                 "sI": round(sI[v], 2), "dI": round(dI[v], 2),
                 "pos": [round(c * C.MM, 1) for c in V0[v]],
                 "W_R1B": dict((g, round(x, 4)) for g, x in sorted(W_B[v].items())),
                 "W_R1E": dict((g, round(x, 4)) for g, x in sorted(W_E[v].items()))}

# the THUMB-MIDDLE severe family: gather all edges with one THUMB and one MIDDLE endpoint
tm = []
for k, (a, b) in enumerate(EDGES):
    if {R3[a], R3[b]} == {"THUMB", "MIDDLE"}:
        tm.append({"edge": k, "a": a, "b": b, "a_region": a in REGION, "b_region": b in REGION,
                   "a_g": GD.get(a, -1), "b_g": GD.get(b, -1),
                   "a_sT": round(sT[a], 2), "b_sT": round(sT[b], 2),
                   "a_dT": round(dT[a], 2), "b_dT": round(dT[b], 2),
                   "a_R1B": dict((g, round(x, 4)) for g, x in sorted(W_B[a].items())),
                   "b_R1B": dict((g, round(x, 4)) for g, x in sorted(W_B[b].items())),
                   "a_R1E": dict((g, round(x, 4)) for g, x in sorted(W_E[a].items())),
                   "b_R1E": dict((g, round(x, 4)) for g, x in sorted(W_E[b].items())),
                   "changed": (W_B[a] != W_E[a]) or (W_B[b] != W_E[b])})
O["thumb_middle_edges"] = tm
O["thumb_middle_changed"] = len([e for e in tm if e["changed"]])
O["thumb_middle_in_region_endpoints"] = len(set([e["a"] for e in tm if e["a_region"]]
                                                 + [e["b"] for e in tm if e["b_region"]]))
json.dump(O, open(os.path.join(R1E, "_tmp", "r1e_probe7.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("PROBE7_DONE  thumb_middle_edges=%d changed=%d" % (len(tm), O["thumb_middle_changed"]))
for e in tm[:20]:
    print(" e%-5d %-5d(%-5s g%-3s reg%-5s sT%6.1f dT%5.1f) %-6s %-5d(%-5s g%-3s reg%-5s sT%6.1f dT%5.1f)"
          % (e["edge"], e["a"], e["a_R1B"], e["a_g"], e["a_region"], e["a_sT"], e["a_dT"],
             e["b_R3"] if "b_R3" in e else R3[e["b"]], e["b"], e["b_R1B"], e["b_g"], e["b_region"],
             e["b_sT"], e["b_dT"]))
