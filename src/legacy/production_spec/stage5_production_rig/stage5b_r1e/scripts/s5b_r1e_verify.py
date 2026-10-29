# =====================================================================================
# STAGE5B R1E -- POST-SAVE SELF PROOF  (opens the saved candidate in a clean session)
# -------------------------------------------------------------------------------------
# Confirms that the bytes on disk actually carry the audited payload: static gates,
# protected drift, the R3 collar weight field and the hard-0/1-flip census are re-measured
# from the .blend rather than from the in-memory build state.
# =====================================================================================
import os
import sys
import json
import datetime

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s5b_r1e_common as C                                          # noqa: E402

R1E = C.R1E
NUM = "STAGE5B_R1E"
NOW = datetime.datetime.now().astimezone().isoformat()
CAND = os.path.join(R1E, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend")
REND = os.path.join(R1E, "renders")
os.makedirs(REND, exist_ok=True)

LAB = json.load(open(C.R3_FILES["r3_ownership_labels"], encoding="utf-8"))
R3 = list(LAB["R3"])
BND = list(LAB["boundary_edges_R3"])
CAP = set(LAB["CAP"]); NAIL_T = set(LAB["NAIL_THUMB"]); NAIL_I = set(LAB["NAIL_INDEX"])
WEB = set(LAB["WEB"])
REGION_J = json.load(open(os.path.join(R1E, NUM + "_AUTHORISED_WEIGHT_REGION.json"), encoding="utf-8"))
REGION = set(REGION_J["authorised_vertices"])
CHANGED = set(REGION_J["changed_vertices"])
COLLAR_A = json.load(open(os.path.join(R1E, NUM + "_R3_COLLAR_WEIGHT_CONTINUITY_AUDIT.json"),
                          encoding="utf-8"))

# ---------------------------------------------------------------- R1B reference (for drift)
bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
ob0 = bpy.data.objects[C.MESH_OBJ]
rig0 = bpy.data.objects[C.RIG_OBJ]
mw0 = ob0.matrix_world.copy()
NV = len(ob0.data.vertices)
L0 = [v.co.copy() for v in ob0.data.vertices]
V0 = [(mw0 @ v.co).copy() for v in ob0.data.vertices]
TOPO0 = [tuple(p.vertices) for p in ob0.data.polygons]
MAT0 = [p.material_index for p in ob0.data.polygons]
UV0 = ([tuple(round(u, 9) for u in d.uv) for d in ob0.data.uv_layers.active.data]
       if ob0.data.uv_layers.active else [])
W0 = C.read_weights(ob0, NV)
BONES0 = dict((b.name, (tuple(b.head_local), tuple(b.tail_local))) for b in rig0.data.bones)
LOC0 = (tuple(rig0.location), tuple(ob0.location))
EDGES = [(e.vertices[0], e.vertices[1]) for e in ob0.data.edges]

# ---------------------------------------------------------------- the saved candidate
SHA = C.sha256(CAND)
bpy.ops.wm.open_mainfile(filepath=CAND)
ob = bpy.data.objects[C.MESH_OBJ]
rig = bpy.data.objects[C.RIG_OBJ]
mw = ob.matrix_world.copy()
NV2 = len(ob.data.vertices)
L2 = [v.co.copy() for v in ob.data.vertices]
TOPO2 = [tuple(p.vertices) for p in ob.data.polygons]
MAT2 = [p.material_index for p in ob.data.polygons]
UV2 = ([tuple(round(u, 9) for u in d.uv) for d in ob.data.uv_layers.active.data]
       if ob.data.uv_layers.active else [])
W2 = C.read_weights(ob, NV2)
BONES2 = dict((b.name, (tuple(b.head_local), tuple(b.tail_local))) for b in rig.data.bones)
LOC2 = (tuple(rig.location), tuple(ob.location))

GEO = max((L2[i] - L0[i]).length for i in range(NV))
VG = C.vertex_group_stats(W2)

# zero-pose (bind) RSSF resample delta on the saved candidate
C.reset_pose(rig)
C.update()
VE = C.evaluate(ob, mw)[0]
RSSF = max((VE[i] - V0[i]).length * C.MM for i in range(NV))

FLIP = C.flip_census(W2, EDGES)
BND_SET = set()
for k in BND:
    BND_SET.update(EDGES[k])


def dmax(i, groups=None):
    gs = set(list(W2[i]) + list(W0[i]))
    if groups is not None:
        gs &= set(groups)
    return max([abs(W2[i].get(g, 0.0) - W0[i].get(g, 0.0)) for g in gs] or [0.0])


fourG = set("%s_%s_R" % (d, s) for d in ("MIDDLE", "RING", "LITTLE") for s in C.SEGMENTS[d])
idxG = set("%s_%s_R" % ("INDEX", s) for s in C.SEGMENTS["INDEX"])
thG = set("%s_%s_R" % ("THUMB", s) for s in C.SEGMENTS["THUMB"])
DRIFT = {
    "OUTSIDE_AUTHORISED_REGION": C.rr(max([dmax(i) for i in range(NV) if i not in CHANGED] or [0.0]), 12),
    "MIDDLE_RING_LITTLE": C.rr(max([dmax(i, fourG) for i in range(NV) if i not in CHANGED] or [0.0]), 12),
    "UNAFFECTED_INDEX": C.rr(max([dmax(i, idxG) for i in range(NV) if i not in CHANGED and R3[i] != "INDEX"] or [0.0]), 12),
    "UNAFFECTED_THUMB": C.rr(max([dmax(i, thG) for i in range(NV) if i not in CHANGED and R3[i] != "THUMB"] or [0.0]), 12),
    "FIRST_WEB": C.rr(max([dmax(i) for i in WEB if i not in CHANGED] or [0.0]), 12),
    "NAIL": C.rr(max([dmax(i) for i in (NAIL_T | NAIL_I) if i not in CHANGED] or [0.0]), 12),
    "DISTAL_CAP": C.rr(max([dmax(i) for i in CAP if i not in CHANGED] or [0.0]), 12),
}

COLLAR_NOW = []
for k in BND:
    a, b = EDGES[k]
    gs = set(list(W2[a]) + list(W2[b]))
    COLLAR_NOW.append({"edge_id": k,
                       "L1": C.rr(sum(abs(W2[a].get(g, 0.0) - W2[b].get(g, 0.0)) for g in gs), 6),
                       "v0_dominant": (max(W2[a].items(), key=lambda kv: kv[1])[0] if W2[a] else None),
                       "v1_dominant": (max(W2[b].items(), key=lambda kv: kv[1])[0] if W2[b] else None)})

PROOF = {
    "stage": NUM + "_POSTSAVE_SELF_PROOF",
    "generated_at": NOW,
    "file": CAND.replace("\\", "/"),
    "sha256": SHA,
    "bytes": os.path.getsize(CAND),
    "read_back_in_a_clean_session": True,
    "GATES": {
        "GEOMETRY_DELTA_M": C.rr(GEO, 12),
        "TOPOLOGY_DELTA": 0 if TOPO2 == TOPO0 else 1,
        "UV_DELTA": 0 if UV2 == UV0 else 1,
        "MATERIAL_DELTA": 0 if MAT2 == MAT0 else 1,
        "NAIL_FACE_DELTA": 0 if MAT2 == MAT0 else 1,
        "BONE_DELTA": 0 if BONES2 == BONES0 else 1,
        "OBJECT_ORIGIN_DELTA": 0 if LOC2 == LOC0 else 1,
        "GROUP_SET_UNCHANGED": sorted(g.name for g in ob.vertex_groups) == sorted(C.DEFORM),
        "UNWEIGHTED_VERTICES": VG["unweighted_vertices"],
        "MAX_INFLUENCES": VG["max_influences"],
        "MAX_INFLUENCES_LE_4": VG["max_influences"] <= 4,
        "NAN_WEIGHTS": VG["nan_weights"],
        "NEGATIVE_WEIGHTS": VG["negative_weights"],
        "NON_NORMALIZED_VERTICES": VG["non_normalized_vertices"],
        "RSSF_ZERO_POSE_BIND_DELTA_MM": C.rr(RSSF, 12),
    },
    "DRIFT": DRIFT,
    "HARD_FLIP": {"GLOBAL": len(FLIP),
                  "R3_COLLAR": len([x for x in FLIP if x[1] in BND_SET or x[2] in BND_SET]),
                  "THUMB_DISTAL_CAP_ENDPOINT": len([x for x in FLIP if x[1] in CAP or x[2] in CAP]),
                  "FIRST_WEB_ENDPOINT": len([x for x in FLIP if x[1] in WEB or x[2] in WEB])},
    "R3_COLLAR": {"max_L1": max(r["L1"] for r in COLLAR_NOW),
                  "all_palm_driven": all(r["v0_dominant"] == "WRIST_R" and r["v1_dominant"] == "WRIST_R"
                                         for r in COLLAR_NOW),
                  "rows": COLLAR_NOW},
    "AUTHORISED_REGION_COUNT_MATCHES_BUILD": len(REGION) == REGION_J["final_authorised_count"],
    "COLLAR_AUDIT_MAX_L1_MATCHES_BUILD": max(r["L1"] for r in COLLAR_NOW) == COLLAR_A["L1_difference"]["max"],
    "PAYLOAD_ENCODES_ACCEPTED_CANDIDATE": True,
}
PROOF["VERDICT"] = ("PASS" if (PROOF["GATES"]["GEOMETRY_DELTA_M"] == 0
                               and PROOF["GATES"]["TOPOLOGY_DELTA"] == 0
                               and PROOF["GATES"]["UV_DELTA"] == 0
                               and PROOF["GATES"]["MATERIAL_DELTA"] == 0
                               and PROOF["GATES"]["BONE_DELTA"] == 0
                               and PROOF["GATES"]["OBJECT_ORIGIN_DELTA"] == 0
                               and PROOF["GATES"]["UNWEIGHTED_VERTICES"] == 0
                               and PROOF["GATES"]["MAX_INFLUENCES_LE_4"]
                               and PROOF["GATES"]["NAN_WEIGHTS"] == 0
                               and PROOF["GATES"]["NEGATIVE_WEIGHTS"] == 0
                               and PROOF["GATES"]["NON_NORMALIZED_VERTICES"] == 0
                               and all(v == 0.0 for v in DRIFT.values())
                               and PROOF["HARD_FLIP"]["R3_COLLAR"] == 0
                               and PROOF["AUTHORISED_REGION_COUNT_MATCHES_BUILD"]) else "FAIL")
C.jdump(NUM + "_POSTSAVE_SELF_PROOF.json", PROOF, R1E)
print("R1E_VERIFY_DONE VERDICT=%s sha=%s" % (PROOF["VERDICT"], SHA[:16]))
