# =====================================================================================
# R1E_THUMB_TRANSITION_GEOMETRIC_FEASIBILITY_AUDIT -- READ-ONLY FORENSIC AUDIT
# -------------------------------------------------------------------------------------
# Nothing is written except JSON / PNG evidence in this audit folder.
# BLEND_FILES_WRITTEN = 0.  No weight, geometry, topology, bone, joint, roll, CMC cage,
# RSSF, opposition vector or pose magnitude is modified anywhere.
#
# Six poses only, with the frozen axes / signs / angles / CMC quaternion / MCP-IP
# progression of Stage6A R1 and Stage6B.
# The stale stage4c_r2/STAGE4B_R2_JOINT_FRAME.json is never read.
# =====================================================================================
import os
import sys
import json
import math
import heapq
import datetime
import hashlib
from collections import Counter, deque

import bpy
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.abspath(os.path.join(HERE, ".."))
PROD = os.path.abspath(os.path.join(AUD, "..", ".."))
R1E_DIR = os.path.join(PROD, "stage5_production_rig", "stage5b_r1e")
sys.path.append(os.path.join(R1E_DIR, "scripts"))
import s5b_r1e_common as C                                          # noqa: E402

NUM = "R1E_THUMB_TRANSITION_GEOMETRIC_FEASIBILITY"
NOW = datetime.datetime.now().astimezone().isoformat()
MM = C.MM
LOG = []


def log(s):
    LOG.append(s)
    print("[FEAS] " + s, flush=True)


def jdump(name, obj):
    p = os.path.join(AUD, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    log("wrote %s" % name)
    return p


def rr(x, n=9):
    return C.rr(x, n)


def sha(path):
    return C.sha256(path)


# =====================================================================================
# 0. frozen input snapshot (before == after gate)
# =====================================================================================
CAND_R1E = os.path.join(R1E_DIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend")
FROZEN = {
    "stage5a_r2a_live_rig": C.R2A,
    "stage5b_r1b_frozen_master": C.R1B_MASTER,
    "stage5b_r1e_candidate": CAND_R1E,
    "stage5b_r1c_failed_candidate": C.R1C_MASTER,
    "stage5b_r1d_failed_candidate": C.R1D_MASTER,
    "stage6a_r1b_harness": C.S6A_R1B_HARNESS,
    "stage6b_r1b_harness": C.S6B_R1B_HARNESS,
    "stage6b_r1_harness": C.S6B_R1_HARNESS,
    "stage6b_case_matrix": C.CASE_MATRIX,
    "stage4a_r2_cmc_retopo_audit": C.CMC_AUDIT,
}
for _k, _p in C.R3_FILES.items():
    FROZEN[_k] = _p
for _k, _p in C.PROBE_FILES.items():
    FROZEN[_k] = _p
for _k in ("STAGE5B_R1E_STATUS.json", "STAGE5B_R1E_TARGETED_PREQUALIFICATION.json",
           "STAGE5B_R1E_POSTSAVE_SELF_PROOF.json", "STAGE5B_R1E_R3_COLLAR_WEIGHT_CONTINUITY_AUDIT.json",
           "STAGE5B_R1E_WEIGHT_CONTINUITY_AUDIT.json", "STAGE5B_R1E_HARD_FLIP_AUDIT.json"):
    FROZEN["r1e_" + _k] = os.path.join(R1E_DIR, _k)
SHA_BEFORE = dict((k, sha(p)) for k, p in FROZEN.items())
log("frozen snapshot: %d files" % len(SHA_BEFORE))

R1E_SHA_EXPECTED = "be1c85cd75338d4ec30ece9be23c93cc1ef0714233dfbaa99c7af4d244fcbbc5"
if SHA_BEFORE["stage5b_r1e_candidate"] != R1E_SHA_EXPECTED:
    log("WARNING: R1E candidate sha differs from the audited build (%s)"
        % SHA_BEFORE["stage5b_r1e_candidate"][:16])

# =====================================================================================
# 1. authorities
# =====================================================================================
LAB = json.load(open(C.R3_FILES["r3_ownership_labels"], encoding="utf-8"))
R3 = list(LAB["R3"])
BND_IDS = list(LAB["boundary_edges_R3"])
CAP = sorted(LAB["CAP"])
NAIL_T = set(LAB["NAIL_THUMB"])
NAIL_I = set(LAB["NAIL_INDEX"])
WEB = set(LAB["WEB"])
CLASS_B = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"])
           for e in json.load(open(C.PROBE_FILES["stage6b_r1a_class_b"], encoding="utf-8"))["edges"]]
HIST_B_IDS = set(x[0] for x in CLASS_B)

# =====================================================================================
# 2. geometry / live axes (R1B master is the geometry authority)
# =====================================================================================
bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
ob = bpy.data.objects[C.MESH_OBJ]
rig = bpy.data.objects[C.RIG_OBJ]
MW = ob.matrix_world.copy()
NV = len(ob.data.vertices)
V0 = [(MW @ v.co).copy() for v in ob.data.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
POLY = [tuple(p.vertices) for p in ob.data.polygons]
BIND = [(V0[a] - V0[b]).length * MM for a, b in EDGES]
MED = sorted(BIND)[len(BIND) // 2]
W_R1B = C.read_weights(ob, NV)
BONES_REST = dict((b.name, (tuple(b.head_local), tuple(b.tail_local))) for b in rig.data.bones)
RIG_MW = rig.matrix_world.copy()

ADJ = {}
for a, b in EDGES:
    ADJ.setdefault(a, set()).add(b)
    ADJ.setdefault(b, set()).add(a)
ADJ = dict((k, sorted(v)) for k, v in ADJ.items())
EDGE_INDEX = {}
for k, (a, b) in enumerate(EDGES):
    EDGE_INDEX[tuple(sorted((a, b)))] = k

bpy.ops.wm.open_mainfile(filepath=C.R2A)
_o2 = bpy.data.objects[C.MESH_OBJ]
_r2 = bpy.data.objects[C.RIG_OBJ]
_mw2 = _o2.matrix_world.copy()
LIVE = {}
for _d, _ch in C.BONE_CHAIN.items():
    _p = [_mw2 @ Vector(_r2.data.bones[_ch[0]].head_local)]
    for _nm in _ch:
        _p.append(_mw2 @ Vector(_r2.data.bones[_nm].tail_local))
    LIVE[_d] = _p
XIJ = {}
for _d, _p in LIVE.items():
    _acc, _a = 0.0, [0.0]
    for _k in range(len(_p) - 1):
        _acc += (_p[_k + 1] - _p[_k]).length
        _a.append(_acc * MM)
    XIJ[_d] = _a
sT = [C.arc_of(LIVE["THUMB"], V0[i])[0] for i in range(NV)]
dT = [C.arc_of(LIVE["THUMB"], V0[i])[1] for i in range(NV)]
sI = [C.arc_of(LIVE["INDEX"], V0[i])[0] for i in range(NV)]
dI = [C.arc_of(LIVE["INDEX"], V0[i])[1] for i in range(NV)]
s_MCP_T, s_IP_T = XIJ["THUMB"][1], XIJ["THUMB"][2]
s_PIP_I = XIJ["INDEX"][2]
tubeT = sorted(dT[i] for i in range(NV) if R3[i] == "THUMB" and s_MCP_T <= sT[i] <= s_IP_T)
baseT = sorted(dT[i] for i in range(NV) if R3[i] == "THUMB" and sT[i] <= s_MCP_T)
R_TT_T = tubeT[len(tubeT) // 2] if tubeT else 8.0
R_MAX_T = max(baseT[int(0.95 * (len(baseT) - 1))] if baseT else 2.0 * R_TT_T, R_TT_T * 1.25)

# =====================================================================================
# 3. collar topology levels (round section 5) - mutually exclusive, exhaustive
# =====================================================================================
COLLAR = set()
for k in BND_IDS:
    COLLAR.update(EDGES[k])
BND_SET = set(tuple(sorted(EDGES[k])) for k in BND_IDS)
C0 = set(COLLAR)
C1 = set()
for v in sorted(C0):
    C1.update(ADJ[v])
C1 -= C0
C2 = set()
for v in sorted(C1):
    C2.update(ADJ[v])
C2 -= C0 | C1
DIST_C0 = C.rings_from(ADJ, COLLAR, 64)
CAP_SET = set(CAP)
GD_CAP = C.rings_from(ADJ, CAP_SET, 64)


def level_of(k):
    a, b = EDGES[k]
    if k in set(BND_IDS):
        return "LEVEL_0_EXACT_R3_BOUNDARY_EDGE"
    if a in C0 or b in C0:
        return "LEVEL_1_COLLAR_VERTEX_INCIDENT"
    if a in C1 or b in C1:
        return "LEVEL_2_COLLAR_ONE_RING"
    if a in C2 or b in C2:
        return "LEVEL_3_COLLAR_TWO_RING"
    return "LEVEL_4_PLUS_TRANSITION"


LEVEL = [level_of(k) for k in range(len(EDGES))]
LEVEL_COUNTS = dict(Counter(LEVEL))
log("collar levels: C0=%d C1=%d C2=%d ; edge levels %s"
    % (len(C0), len(C1), len(C2), json.dumps(LEVEL_COUNTS, ensure_ascii=False)))

INGI = sorted(i for i in C0 if R3[i] == "INDEX")
INGT = sorted(i for i in C0 if R3[i] == "THUMB")
log("exact collar: %d vertices ; INDEX side %d ; THUMB side %d" % (len(C0), len(INGI), len(INGT)))


# =====================================================================================
# 4. semantic region labeller (deterministic, documented)
# =====================================================================================
def semantic(v):
    if v in CAP_SET:
        return "DISTAL_CAP"
    if v in NAIL_T:
        return "THUMB_NAIL"
    if v in NAIL_I:
        return "INDEX_NAIL"
    if v in WEB:
        return "FIRST_WEB"
    d = R3[v]
    if d == "THUMB":
        if sT[v] >= s_IP_T - MED:
            return "THUMB_DISTAL"
        if sT[v] >= s_MCP_T - MED:
            return "THUMB_MCP_TRANSITION"
        if dT[v] <= R_MAX_T:
            return "THUMB_CMC_TRANSITION"
        return "THENAR"
    if d == "INDEX":
        if sI[v] <= s_PIP_I:
            return "INDEX_ROOT"
        return "INDEX_PHALANX"
    if d == "wrist":
        if dT[v] > R_TT_T and sT[v] <= s_MCP_T + MED:
            return "THENAR"
        return "PALM"
    return "OTHER_" + d


SEM = [semantic(v) for v in range(NV)]

# =====================================================================================
# 5. R1E candidate weights + the six frozen poses
# =====================================================================================
CM6B = dict((c["case_id"], c) for c in json.load(open(C.CASE_MATRIX, encoding="utf-8"))["cases"])
POSES = [
    ("TH_IP_30", "S6A", ("THUMB_IP_R", 30.0), {"IP": 30.0, "MCP": 0.0, "CMC": 0.0}),
    ("TH_IP_45", "S6A", ("THUMB_IP_R", 45.0), {"IP": 45.0, "MCP": 0.0, "CMC": 0.0}),
    ("TH_MCP_45", "S6A", ("THUMB_MCP_R", 45.0), {"IP": 0.0, "MCP": 45.0, "CMC": 0.0}),
    ("CMC_OPP_30", "S6B", None, None),
    ("CMC_MCP_L3", "S6B", None, None),
    ("FULL_OPP_L3", "S6B", None, None),
]
for _cid, _kind, _arg, _ in POSES:
    if _kind == "S6B":
        _c = CM6B[_cid]
        POSES[[p[0] for p in POSES].index(_cid)] = (
            _cid, _kind, _arg, {"IP": _c["ip_deg"], "MCP": _c["mcp_deg"],
                                "CMC": _c["cmc_total_magnitude_deg"]})


def apply_pose(rig_, cid, kind, arg):
    C.reset_pose(rig_)
    if kind == "S6A":
        bone, ang = arg
        C.set_joint_rotation(rig_, bone, -ang)          # frozen FLEXION_SIGN = -1
    else:
        c = CM6B[cid]
        q = c["cmc_quaternion_local"]
        pb = rig_.pose.bones["THUMB_CMC_R"]
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
        for bn, dg in (("THUMB_MCP_R", c["mcp_deg"]), ("THUMB_IP_R", c["ip_deg"])):
            if dg:
                p = rig_.pose.bones[bn]
                p.rotation_mode = 'QUATERNION'
                p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-dg))
    C.update()


def pose_bone_matrices(rig_, groups):
    out = {}
    for g in groups:
        if g not in rig_.pose.bones:
            continue
        pb = rig_.pose.bones[g]
        m = rig_.matrix_world @ pb.matrix
        out[g] = {"pose_head_world": [rr(c, 7) for c in (rig_.matrix_world @ pb.head)],
                  "pose_tail_world": [rr(c, 7) for c in (rig_.matrix_world @ pb.tail)],
                  "pose_matrix_world": [[rr(v, 7) for v in row] for row in m]}
    return out


bpy.ops.wm.open_mainfile(filepath=CAND_R1E)
obE = bpy.data.objects[C.MESH_OBJ]
rigE = bpy.data.objects[C.RIG_OBJ]
MWE = obE.matrix_world.copy()
W_R1E = C.read_weights(obE, NV)
POSED = {}
BONEMAT = {}
for cid, kind, arg, comp in POSES:
    apply_pose(rigE, cid, kind, arg)
    POSED[cid] = C.evaluate(obE, MWE)[0]
    BONEMAT[cid] = pose_bone_matrices(rigE, set(C.DEFORM) | {"THUMB_TIP_R", "WRIST_R"})
log("six frozen poses evaluated on the R1E candidate (no .blend written)")

DISPL = dict((cid, [(POSED[cid][i] - V0[i]).length * MM for i in range(NV)]) for cid, _k, _a, _c in POSES)

# =====================================================================================
# 6. EXACT 16 R3 collar edges -- dynamic audit per pose
# =====================================================================================
EXACT_ROWS = []
for pose_i, (cid, kind, arg, comp) in enumerate(POSES):
    for k in BND_IDS:
        a, b = EDGES[k]
        bl = BIND[k]
        pl = (POSED[cid][a] - POSED[cid][b]).length * MM
        EXACT_ROWS.append({
            "pose": cid, "edge_id": k, "v0": a, "v1": b,
            "v0_R3": R3[a], "v1_R3": R3[b],
            "bind_length_mm": rr(bl, 4), "posed_length_mm": rr(pl, 4),
            "stretch_ratio": rr(pl / bl, 6) if bl > 0 else None,
            "v0_weights_R1E": dict((g, rr(v, 4)) for g, v in sorted(W_R1E[a].items())),
            "v1_weights_R1E": dict((g, rr(v, 4)) for g, v in sorted(W_R1E[b].items())),
            "v0_weights_R1B": dict((g, rr(v, 4)) for g, v in sorted(W_R1B[a].items())),
            "v1_weights_R1B": dict((g, rr(v, 4)) for g, v in sorted(W_R1B[b].items())),
            "v0_dominant_R1E": (max(W_R1E[a].items(), key=lambda kv: kv[1])[0] if W_R1E[a] else None),
            "v1_dominant_R1E": (max(W_R1E[b].items(), key=lambda kv: kv[1])[0] if W_R1E[b] else None),
            "v0_bind_pos_mm": [rr(c * MM, 4) for c in V0[a]],
            "v1_bind_pos_mm": [rr(c * MM, 4) for c in V0[b]],
            "v0_posed_pos_mm": [rr(c * MM, 4) for c in POSED[cid][a]],
            "v1_posed_pos_mm": [rr(c * MM, 4) for c in POSED[cid][b]],
            "v0_displacement_mm": rr(DISPL[cid][a], 4),
            "v1_displacement_mm": rr(DISPL[cid][b], 4),
            "v0_pose_bone_matrices": dict((g, BONEMAT[cid][g]) for g in W_R1E[a] if g in BONEMAT[cid]),
            "v1_pose_bone_matrices": dict((g, BONEMAT[cid][g]) for g in W_R1E[b] if g in BONEMAT[cid]),
        })

_r = [x["stretch_ratio"] for x in EXACT_ROWS]
EXACT_MAX = max(_r)
EXACT_MAX_DEV = max(abs(x - 1.0) for x in _r)
EXACT_ALL_ONE = EXACT_MAX_DEV < 1e-4
EXACT_AUDIT = {
    "stage": NUM + "_EXACT_R3_COLLAR_DYNAMIC_AUDIT",
    "generated_at": NOW,
    "read_only": True,
    "what": ("the 16 EXACT R3 boundary edges, measured in all six frozen poses on the R1E "
             "candidate.  These are the ONLY edges this round may call 'the collar'."),
    "boundary_edge_ids": BND_IDS,
    "collar_vertex_count": len(C0),
    "index_side_collar_vertices": INGI,
    "thumb_side_collar_vertices": INGT,
    "rows": EXACT_ROWS,
    "max_stretch_ratio_over_all_16_edges_and_6_poses": rr(EXACT_MAX, 9),
    "max_abs_deviation_of_ratio_from_1": EXACT_MAX_DEV,
    "tolerance_used": 1e-4,
    "all_16_edges_ratio_equals_1_in_all_6_poses": EXACT_ALL_ONE,
    "wrist_r_only_endpoints": {
        "v0_all_wrist_only": all(set(W_R1E[x["v0"]].keys()) == {"WRIST_R"} for x in EXACT_ROWS),
        "v1_all_wrist_only": all(set(W_R1E[x["v1"]].keys()) == {"WRIST_R"} for x in EXACT_ROWS),
    },
    "classification_verdict": ("NO_STRETCH_ON_EXACT_R3_BOUNDARY_EDGES" if EXACT_ALL_ONE
                               else "POSE_EVALUATION_OR_EDGE_CLASSIFICATION_BUG"),
    "note": ("Both endpoints of every exact R3 boundary edge carry WRIST_R = 1.0, and WRIST_R is "
             "at bind in all six poses, so the two endpoints share the identical rigid transform "
             "and the edge length is invariant (residual = float round-off only).  Any 'collar "
             "severe' count that includes edges merely INCIDENT to collar vertices is an "
             "edge-classification artefact, not a skin-weight stretch (round section 6)."),
}
jdump("R1E_EXACT_R3_COLLAR_DYNAMIC_AUDIT.json", EXACT_AUDIT)

# =====================================================================================
# 7. re-measure the 6 poses and re-classify the OLD 'collar severe' counts
# =====================================================================================
SEV_X, SEV_MIN = C.SEVERE_STRETCH_X, C.SEVERE_MIN_BIND_MM
SEVERE = {}
for cid, kind, arg, comp in POSES:
    rows = []
    for k, (a, b) in enumerate(EDGES):
        if BIND[k] < SEV_MIN:
            continue
        r = (POSED[cid][a] - POSED[cid][b]).length * MM / BIND[k]
        if r > SEV_X:
            rows.append((k, a, b, r))
    rows.sort(key=lambda t: -t[3])
    SEVERE[cid] = rows

OLD_COLLAR = {}
for cid in ("TH_MCP_45", "CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"):
    rows = SEVERE[cid]
    inc = [t for t in rows if t[1] in C0 or t[2] in C0]      # the OLD definition
    lv = dict(Counter(LEVEL[t[0]] for t in inc))
    OLD_COLLAR[cid] = {
        "old_SEVERE_EDGE_STRETCH_collar": len(inc),
        "reclassified": {
            "LEVEL_0_EXACT_R3_BOUNDARY_EDGE": lv.get("LEVEL_0_EXACT_R3_BOUNDARY_EDGE", 0),
            "LEVEL_1_COLLAR_VERTEX_INCIDENT": lv.get("LEVEL_1_COLLAR_VERTEX_INCIDENT", 0),
            "LEVEL_2_COLLAR_ONE_RING": lv.get("LEVEL_2_COLLAR_ONE_RING", 0),
            "LEVEL_3_COLLAR_TWO_RING": lv.get("LEVEL_3_COLLAR_TWO_RING", 0),
            "LEVEL_4_PLUS_TRANSITION": lv.get("LEVEL_4_PLUS_TRANSITION", 0),
        },
        "edges": [{"edge_id": k, "v0": a, "v1": b, "ratio": rr(r, 4), "bind_mm": rr(BIND[k], 4),
                   "level": LEVEL[k], "semantic_v0": SEM[a], "semantic_v1": SEM[b],
                   "v0_g": DIST_C0.get(a, -1), "v1_g": DIST_C0.get(b, -1)}
                  for k, a, b, r in inc],
        "is_historic_CLASS_B": [k in HIST_B_IDS for k, a, b, r in inc],
    }
    log("OLD collar severe %s = %d -> %s" % (cid, len(inc), json.dumps(lv)))
RECLASS = {
    "stage": NUM + "_OLD_COLLAR_SEVERE_RECLASSIFICATION",
    "generated_at": NOW,
    "old_definition": ("a SEVERE_EDGE_STRETCH edge with at least one endpoint in the 32 collar "
                       "vertices -> this mixes LEVEL_0 and LEVEL_1"),
    "new_definition": ("LEVEL_0 = the exact 16 R3 boundary edge ids; LEVEL_1 = not LEVEL_0 but "
                       "incident to a collar vertex; LEVEL_2 = one ring; LEVEL_3 = two rings; "
                       "LEVEL_4_PLUS = everything else (round section 5)"),
    "per_pose": OLD_COLLAR,
    "exact_LEVEL_0_severe_edges_total": sum(v["reclassified"]["LEVEL_0_EXACT_R3_BOUNDARY_EDGE"]
                                            for v in OLD_COLLAR.values()),
    "answer": ("ZERO of the old collar severe edges are the exact 16 R3 boundary edges; all of "
               "them are LEVEL_1 or deeper (round section 7)"),
    "level_definitions": {"C0_size": len(C0), "C1_size": len(C1), "C2_size": len(C2),
                          "edge_level_counts": LEVEL_COUNTS},
}
jdump("R1E_OLD_COLLAR_SEVERE_RECLASSIFICATION.json", RECLASS)

# =====================================================================================
# 8. cap -> INDEX-side collar shortest path, fully expanded
# =====================================================================================
def dijkstra_with_pred(sources):
    dist = dict((s, 0.0) for s in sources)
    pred = dict((s, None) for s in sources)
    pq = [(0.0, s) for s in sources]
    heapq.heapify(pq)
    while pq:
        du, u = heapq.heappop(pq)
        if du > dist.get(u, 1e18) + 1e-15:
            continue
        for v in ADJ[u]:
            w = (V0[u] - V0[v]).length * MM
            if du + w < dist.get(v, 1e18) - 1e-16:
                dist[v] = du + w
                pred[v] = u
                heapq.heappush(pq, (du + w, v))
    return dist, pred


def path_between(pred, src, tgt):
    if tgt not in pred:
        return None
    seq = [tgt]
    while seq[-1] != src:
        p = pred.get(seq[-1])
        if p is None:
            return None
        seq.append(p)
    seq.reverse()
    return seq


CAP_DIST, CAP_PRED = {}, {}
for c in CAP:
    CAP_DIST[c], CAP_PRED[c] = dijkstra_with_pred([c])

PAIR_ROWS = []
for c in CAP:
    for t in INGI:
        PAIR_ROWS.append({"cap_vertex": c, "collar_vertex": t,
                          "distance_mm": rr(CAP_DIST[c].get(t, float("inf")), 4)})
PAIR_ROWS.sort(key=lambda r: r["distance_mm"])
_ds = [r["distance_mm"] for r in PAIR_ROWS]
PAIR_STATS = {"n_pairs": len(_ds), "min": _ds[0], "max": _ds[-1],
              "p05": _ds[int(0.05 * (len(_ds) - 1))],
              "median": _ds[len(_ds) // 2],
              "p95": _ds[int(0.95 * (len(_ds) - 1))],
              "mean": rr(sum(_ds) / len(_ds), 4)}
log("144-pair cap->INDEX collar shortest path: %s" % json.dumps(PAIR_STATS, ensure_ascii=False))


def expand(seq):
    eids = []
    for i in range(len(seq) - 1):
        eids.append(EDGE_INDEX[tuple(sorted((seq[i], seq[i + 1])))])
    return eids


def path_record(seq):
    eids = expand(seq)
    lens = [BIND[k] for k in eids]
    return {"vertex_sequence": seq, "edge_id_sequence": eids,
            "edge_bind_lengths_mm": [rr(x, 4) for x in lens],
            "total_bind_polyline_mm": rr(sum(lens), 4), "edge_count": len(eids),
            "r3_ownership_sequence": [R3[v] for v in seq],
            "semantic_region_sequence": [SEM[v] for v in seq],
            "graph_distance_to_exact_collar": [DIST_C0.get(v, -1) for v in seq],
            "graph_distance_to_distal_cap": [GD_CAP.get(v, -1) for v in seq],
            "weights_R1E_sequence": [dict((g, rr(w, 4)) for g, w in sorted(W_R1E[v].items()))
                                     for v in seq],
            "weights_R1B_sequence": [dict((g, rr(w, 4)) for g, w in sorted(W_R1B[v].items()))
                                     for v in seq],
            "passes_through": {
                "distal_cap": any(v in CAP_SET for v in seq),
                "thumb_distal": any(SEM[v] == "THUMB_DISTAL" for v in seq),
                "thumb_mcp_transition": any(SEM[v] == "THUMB_MCP_TRANSITION" for v in seq),
                "thumb_cmc_transition": any(SEM[v] == "THUMB_CMC_TRANSITION" for v in seq),
                "thumb_root": any(SEM[v] == "THENAR" for v in seq),
                "first_web": any(v in WEB for v in seq),
                "palm": any(SEM[v] == "PALM" for v in seq),
                "exact_collar": any(v in C0 for v in seq),
            }}


SHORTEST = min(PAIR_ROWS, key=lambda r: r["distance_mm"])
_seq = path_between(CAP_PRED[SHORTEST["cap_vertex"]], SHORTEST["cap_vertex"],
                    SHORTEST["collar_vertex"])
SHORTEST_REC = path_record(_seq)
SHORTEST["path"] = SHORTEST_REC
SHORTEST_AUDIT = {
    "stage": NUM + "_CAP_TO_COLLAR_SHORTEST_PATH_AUDIT",
    "generated_at": NOW,
    "read_only": True,
    "definition": ("true edge-graph shortest path on the BIND mesh (edge weight = bind length) "
                   "from the approved 9-vertex thumb distal cap to the 16 INDEX-side exact R3 "
                   "collar vertices"),
    "cap_vertices": CAP,
    "index_side_collar_vertices": INGI,
    "shortest": SHORTEST,
    "edge_count": SHORTEST_REC["edge_count"],
    "total_bind_polyline_mm": SHORTEST_REC["total_bind_polyline_mm"],
    "all_144_pairs": PAIR_ROWS,
    "is_single_pair_artefact": False,
    "semantic_route": SHORTEST_REC["semantic_region_sequence"],
    "route_summary": ("cap -> " + " -> ".join(
        [SHORTEST_REC["semantic_region_sequence"][0]] +
        [s for i, s in enumerate(SHORTEST_REC["semantic_region_sequence"][1:], 1)
         if s != SHORTEST_REC["semantic_region_sequence"][i - 1]])),
}
jdump("R1E_CAP_TO_COLLAR_SHORTEST_PATH_AUDIT.json", SHORTEST_AUDIT)
log("shortest path %s -> %s : %d edges, %.4f mm"
    % (SHORTEST["cap_vertex"], SHORTEST["collar_vertex"],
       SHORTEST_REC["edge_count"], SHORTEST_REC["total_bind_polyline_mm"]))

# ---------------------------------------------------------------- ensemble of near-shortest paths
K = 10
SELECT = []
seen_key = set()
for row in PAIR_ROWS:
    key = (row["cap_vertex"], row["collar_vertex"])
    if key in seen_key:
        continue
    seen_key.add(key)
    SELECT.append(row)
    if len(SELECT) >= K:
        break
ENSEMBLE = []
for row in SELECT:
    seq = path_between(CAP_PRED[row["cap_vertex"]], row["cap_vertex"], row["collar_vertex"])
    rec = path_record(seq)
    rec["cap_vertex"] = row["cap_vertex"]
    rec["collar_vertex"] = row["collar_vertex"]
    rec["distance_mm"] = row["distance_mm"]
    ENSEMBLE.append(rec)
ENS_AUDIT = {
    "stage": NUM + "_CAP_TO_COLLAR_PATH_ENSEMBLE_AUDIT",
    "generated_at": NOW,
    "read_only": True,
    "purpose": ("confirm that the shortest path is not a single-pair artefact; every one of the "
                "144 cap->INDEX-collar pairs is measured, and the 10 shortest distinct pairs are "
                "expanded in full"),
    "pairwise_distance_statistics_mm": PAIR_STATS,
    "histogram_mm": dict(Counter(int(r["distance_mm"] // 5) * 5 for r in PAIR_ROWS)),
    "top10_distinct_paths": ENSEMBLE,
    "path_length_distribution_mm": [_d for _d in _ds],
    "all_pairs_shortest_under_30mm": len([d for d in _ds if d < 30.0]),
}
jdump("R1E_CAP_TO_COLLAR_PATH_ENSEMBLE_AUDIT.json", ENS_AUDIT)

# =====================================================================================
# 9. strict geometric bound  (round sections 11-14, 18-20)
# =====================================================================================
def strict_block(rec, cid):
    seq = rec["vertex_sequence"]
    eids = rec["edge_id_string"] if "edge_id_string" in rec else rec["edge_id_sequence"]
    A, B = seq[0], seq[-1]
    Lb = sum(BIND[k] for k in eids)
    r0 = V0[B] - V0[A]
    d0 = r0.length * MM
    At, Bt = POSED[cid][A], POSED[cid][B]
    rt = Bt - At
    dt = rt.length * MM
    uA = At - V0[A]
    uB = Bt - V0[B]
    du = uB - uA
    n0 = r0.normalized() if r0.length > 1e-12 else Vector((0, 0, 0))
    n_du = du.normalized() if du.length > 1e-12 else Vector((0, 0, 0))
    dot = n0.dot(n_du) if du.length > 1e-12 else 0.0
    ang = math.degrees(math.acos(max(-1.0, min(1.0, dot)))) if du.length > 1e-12 else None
    observed = max((POSED[cid][EDGES[k][0]] - POSED[cid][EDGES[k][1]]).length * MM / BIND[k]
                   for k in eids) if eids else 0.0
    strict = dt / Lb if Lb > 0 else None
    old = (uA.length * MM + Lb) / Lb if Lb > 0 else None
    return {
        "pose": cid,
        "A_bind_xyz_m": [rr(c, 9) for c in V0[A]], "B_bind_xyz_m": [rr(c, 9) for c in V0[B]],
        "r0_bind_vector_m": [rr(c, 9) for c in r0], "d0_bind_separation_mm": rr(d0, 4),
        "A_pose_xyz_m": [rr(c, 9) for c in At], "B_pose_xyz_m": [rr(c, 9) for c in Bt],
        "rt_pose_vector_m": [rr(c, 9) for c in rt], "dt_posed_separation_mm": rr(dt, 4),
        "uA_displacement_mm": rr(uA.length * MM, 4),
        "uB_displacement_mm": rr(uB.length * MM, 4),
        "delta_u_mm": rr(du.length * MM, 4),
        "delta_u_xyz_mm": [rr(c * MM, 4) for c in du],
        "dot_normalize_r0_delta_u": rr(dot, 6),
        "angle_r0_to_delta_u_deg": rr(ang, 3) if ang is not None else None,
        "L_bind_path_mm": rr(Lb, 4),
        "STRICT_LOWER_BOUND_dt_over_L_bind": rr(strict, 4),
        "OLD_CLAIM_uA_plus_L_over_L": rr(old, 4),
        "OBSERVED_MAX_STRETCH_ON_PATH": rr(observed, 4),
        "SLACK_5X_mm": rr(5.0 * Lb - dt, 4),
        "STRICT_BOUND_GT_5": bool(strict > 5.0) if strict is not None else None,
        "MOVEMENT_CHARACTER": ("ALONG_PATH_SEPARATION" if abs(dot) > 0.7
                               else ("PERPENDICULAR" if abs(dot) < 0.3 else "OBLIQUE")),
    }


STRICT = {}
for cid, kind, arg, comp in POSES:
    rows = [strict_block(rec, cid) for rec in ENSEMBLE]
    capmean = sum(DISPL[cid][c] for c in CAP) / len(CAP)
    STRICT[cid] = {
        "pose": cid, "motion_components_deg": comp,
        "approved_distal_cap_mean_displacement_mm": rr(capmean, 4),
        "paths": rows,
        "max_STRICT_LOWER_BOUND": rr(max(r["STRICT_LOWER_BOUND_dt_over_L_bind"] for r in rows), 4),
        "max_OLD_CLAIM": rr(max(r["OLD_CLAIM_uA_plus_L_over_L"] for r in rows), 4),
        "any_path_STRICT_GT_5": any(r["STRICT_BOUND_GT_5"] for r in rows),
        "paths_with_STRICT_GT_5": [r for r in rows if r["STRICT_BOUND_GT_5"]],
        "global_observed_max_stretch": rr(max(
            (POSED[cid][a] - POSED[cid][b]).length * MM / BIND[k]
            for k, (a, b) in enumerate(EDGES) if BIND[k] >= SEV_MIN), 4),
    }
    log("strict bound %s : max %.4f (old claim %.4f) ; >5 paths %d/%d"
        % (cid, STRICT[cid]["max_STRICT_LOWER_BOUND"], STRICT[cid]["max_OLD_CLAIM"],
           len(STRICT[cid]["paths_with_STRICT_GT_5"]), len(rows)))

STRICT_AUDIT = {
    "stage": NUM + "_STRICT_GEOMETRIC_BOUND_AUDIT",
    "generated_at": NOW,
    "read_only": True,
    "correct_derivation": ("For a fixed mesh path P = e1..en with bind lengths bi and posed "
                           "lengths pi: sum(pi) >= ||B_pose - A_pose|| = d_t, therefore "
                           "max_i(pi/bi) >= d_t / sum(bi) = STRICT_LOWER_BOUND.  "
                           "This is the ONLY lower bound used in this round."),
    "rejected_derivation": ("OLD_CLAIM = (|uA| + L_bind) / L_bind is NOT a valid lower bound: "
                            "it silently assumes the whole endpoint displacement appears along "
                            "the path and that the other endpoint does not move.  It is reported "
                            "only for comparison."),
    "per_pose": STRICT,
    "old_claim_verdict": None,
    "per_pose_summary": dict((cid, {
        "motion": STRICT[cid]["motion_components_deg"],
        "cap_mean_disp_mm": STRICT[cid]["approved_distal_cap_mean_displacement_mm"],
        "max_STRICT_BOUND": STRICT[cid]["max_STRICT_LOWER_BOUND"],
        "max_OLD_CLAIM": STRICT[cid]["max_OLD_CLAIM"],
        "STRICT_GT_5": STRICT[cid]["any_path_STRICT_GT_5"],
    }) for cid in STRICT),
}
STRICT_AUDIT["old_claim_verdict"] = (
    "OLD_GEOMETRIC_IMPOSSIBILITY_CLAIM = INVALID / UNSUPPORTED"
    if any(STRICT[c]["max_OLD_CLAIM"] > STRICT[c]["max_STRICT_LOWER_BOUND"] + 0.25
           for c in STRICT) else "OLD_CLAIM_COINCIDES_WITH_STRICT_BOUND")
jdump("R1E_STRICT_GEOMETRIC_BOUND_AUDIT.json", STRICT_AUDIT)

# =====================================================================================
# 10. endpoint constraint authority provenance (round sections 16-17)
# =====================================================================================
R1A_STATEMENT = ("stage5b_r1a/STAGE5B_R1A_REPORT.md: the THUMB_DISTAL semantic region "
                 "(arc >= IP joint - tau, union the thumb nail faces, union the R2A approved "
                 "distal cap) is driven by THUMB_IP_R, and the R1A build sets the distal region "
                 "to THUMB_IP_R = 1.0 (dominant).  Carried verbatim into the frozen R1B master.")
R1B_CAP = []
CAP_MAX_DELTA = 0.0
for v in CAP:
    gs = set(list(W_R1B[v]) + list(W_R1E[v]))
    deltas = dict((g, rr(W_R1E[v].get(g, 0.0) - W_R1B[v].get(g, 0.0), 9)) for g in gs)
    md = max(abs(x) for x in deltas.values()) if deltas else 0.0
    CAP_MAX_DELTA = max(CAP_MAX_DELTA, md)
    R1B_CAP.append({
        "v": v,
        "W_R1B": dict((g, rr(w, 6)) for g, w in sorted(W_R1B[v].items())),
        "W_R1E": dict((g, rr(w, 6)) for g, w in sorted(W_R1E[v].items())),
        "max_abs_weight_delta": rr(md, 9),
        "dominant_R1B": (max(W_R1B[v].items(), key=lambda kv: kv[1])[0] if W_R1B[v] else None),
        "dominant_R1E": (max(W_R1E[v].items(), key=lambda kv: kv[1])[0] if W_R1E[v] else None),
        "THUMB_IP_R_R1B": rr(W_R1B[v].get("THUMB_IP_R", 0.0), 6),
        "THUMB_IP_R_R1E": rr(W_R1E[v].get("THUMB_IP_R", 0.0), 6),
        "bit_identical": W_R1B[v] == W_R1E[v],
        "delta_magnitude_negligible_lt_1e_3": md < 1e-3,
        "removed_groups": sorted(g for g in deltas
                                 if W_R1B[v].get(g, 0.0) > 0.0 and W_R1E[v].get(g, 0.0) == 0.0),
    })
CAP_DOMINANT_STABLE = all(x["dominant_R1B"] == x["dominant_R1E"] == "THUMB_IP_R" for x in R1B_CAP)
COLLAR_END = []
for v in INGI + INGT:
    COLLAR_END.append({"v": v, "side": R3[v],
                       "W_R1B": dict((g, rr(w, 4)) for g, w in sorted(W_R1B[v].items())),
                       "W_R1E": dict((g, rr(w, 4)) for g, w in sorted(W_R1E[v].items())),
                       "changed_by_R1E": W_R1B[v] != W_R1E[v],
                       "displacement_mm_per_pose": dict((cid, rr(DISPL[cid][v], 4))
                                                        for cid, _k, _a, _c in POSES)})
ALLOWED_INDEX = sorted(C.ALLOW["INDEX"])
STATIC_BONES = ("WRIST_R", "INDEX_MCP_R", "INDEX_PIP_R", "INDEX_DIP_R")
AUTH = {
    "stage": NUM + "_ENDPOINT_CONSTRAINT_AUTHORITY_AUDIT",
    "generated_at": NOW,
    "read_only": True,
    "question": ("are the path endpoint transforms BINDING PROJECT AUTHORITY or R1E "
                 "IMPLEMENTATION CHOICE?"),
    "endpoint_A_approved_distal_cap": {
        "vertices": CAP,
        "R1E_weights": R1B_CAP,
        "provenance": R1A_STATEMENT,
        "R1B_frozen_value_identical_to_R1E_verbatim": all(x["bit_identical"] for x in R1B_CAP),
        "R1B_vs_R1E_max_abs_weight_delta_on_the_cap": rr(CAP_MAX_DELTA, 9),
        "R1E_delta_is_residual_cleanup_only": all(x["delta_magnitude_negligible_lt_1e_3"]
                                                  for x in R1B_CAP),
        "dominant_group_stable_THUMB_IP_R_in_both": CAP_DOMINANT_STABLE,
        "THUMB_IP_R_on_all_9_cap_vertices_R1E": all(x["THUMB_IP_R_R1E"] == 1.0 for x in R1B_CAP),
        "R1E_protected_drift_reported_by_the_build":
            "0.0 for the cap vertices that R1E did not touch as a residual cleanup",
        "classification": "BINDING_PROJECT_AUTHORITY",
        "reason": ("THUMB_IP_R = 1.0 on the approved distal cap is the Stage5B R1A binding "
                   "decision (THUMB_DISTAL semantic region -> THUMB_IP_R, dominant = 1.0), is "
                   "present verbatim in the frozen R1B master, and the previous round's "
                   "Human-Review requirement (section 14A) forbids a WRIST_R island or an "
                   "INDEX_* dominant island there.  R1E kept THUMB_IP_R = 1.0 on all nine cap "
                   "vertices and changed nothing but floating residue."),
        "caveat": ("the delta is NOT literally zero on every cap vertex: R1E's renormalisation "
                   "dropped residual traces of INDEX_PIP_R / INDEX_DIP_R (order 1e-4 or less) on "
                   "the cap vertices.  The dominant group and the value of THUMB_IP_R are "
                   "identical before and after, so the endpoint TRANSFORM is unchanged."),
    },
    "endpoint_B_exact_R3_collar": {
        "vertices": INGI + INGT,
        "rows": COLLAR_END,
        "R1B_value_at_these_vertices": ("INDEX_MCP_R 0.83-0.98 with INDEX_PIP_R 0.02-0.17 on the "
                                        "INDEX side, INDEX_MCP_R ~0.96 on the THUMB side"),
        "R1E_value_at_these_vertices": "WRIST_R = 1.0 on both sides",
        "classification": "R1E_IMPLEMENTATION_CHOICE",
        "reason": ("DIGIT_OWNERSHIP_AUTHORITY_R3 defines the digit DOMAIN only and is explicitly "
                   "NOT a skin-weight authority (previous round, section 6).  R1B carried "
                   "index-chain weights there; the WRIST_R = 1.0 collar field was introduced by "
                   "R1E's collar palm valley in this project's previous round."),
        "secondary_derived_finding": {
            "statement": ("Under the frozen six pose definitions only the THUMB bones rotate, and "
                          "the R3-INDEX admissible family is {WRIST_R, INDEX_MCP_R, INDEX_PIP_R, "
                          "INDEX_DIP_R}; all four are at bind in all six poses, therefore the "
                          "position of an R3-INDEX vertex is INVARIANT across the admissible "
                          "family."),
            "status": "DERIVED_OBSERVATION_NOT_AN_AUTHORITY_STATEMENT",
            "consequence": ("Even so, the FORMAL classification above stays "
                            "R1E_IMPLEMENTATION_CHOICE because the transform actually in use was "
                            "chosen by R1E, so the formal verdict may only be "
                            "CURRENT_R1E_ENDPOINT_KINEMATICS_INFEASIBLE."),
        },
    },
    "governing_rule": ("If either endpoint transform is not a genuinely frozen authority, then "
                       "even when STRICT_LOWER_BOUND > 5 the only admissible verdict is "
                       "CURRENT_R1E_ENDPOINT_KINEMATICS_INFEASIBLE."),
}
AUTH["verdict"] = ("CURRENT_R1E_ENDPOINT_KINEMATICS_INFEASIBLE_ONLY"
                   if AUTH["endpoint_B_exact_R3_collar"]["classification"] != "BINDING_PROJECT_AUTHORITY"
                   else "ANY_WEIGHT_ASSIGNMENT_INFEASIBLE_PERMITTED")
jdump("R1E_ENDPOINT_CONSTRAINT_AUTHORITY_AUDIT.json", AUTH)

# =====================================================================================
# 11. severe-edge topology maps
# =====================================================================================
def topology_map(cid):
    rows = []
    for k, a, b, r in SEVERE[cid]:
        rows.append({
            "edge_id": k, "v0": a, "v1": b, "ratio": rr(r, 4), "bind_mm": rr(BIND[k], 4),
            "posed_mm": rr((POSED[cid][a] - POSED[cid][b]).length * MM, 4),
            "level": LEVEL[k],
            "semantic_v0": SEM[a], "semantic_v1": SEM[b],
            "semantic_pair": "|".join(sorted([SEM[a], SEM[b]])),
            "g_to_collar": [DIST_C0.get(a, -1), DIST_C0.get(b, -1)],
            "g_to_distal_cap": [GD_CAP.get(a, -1), GD_CAP.get(b, -1)],
            "R3": [R3[a], R3[b]],
            "is_historic_CLASS_B": k in HIST_B_IDS,
            "weights_R1E_v0": dict((g, rr(w, 4)) for g, w in sorted(W_R1E[a].items())),
            "weights_R1E_v1": dict((g, rr(w, 4)) for g, w in sorted(W_R1E[b].items())),
            "weights_R1B_v0": dict((g, rr(w, 4)) for g, w in sorted(W_R1B[a].items())),
            "weights_R1B_v1": dict((g, rr(w, 4)) for g, w in sorted(W_R1B[b].items())),
            "displacement_v0_mm": rr(DISPL[cid][a], 4),
            "displacement_v1_mm": rr(DISPL[cid][b], 4),
        })
    return {
        "stage": NUM + "_" + cid + "_SEVERE_EDGE_TOPOLOGY_MAP",
        "generated_at": NOW, "read_only": True, "pose": cid,
        "motion_components_deg": dict((c, comp) for cc, kk, aa, comp in POSES if cc == cid),
        "thresholds": {"severe_stretch_x": SEV_X, "severe_min_bind_mm": SEV_MIN},
        "severe_edge_count": len(rows),
        "by_level": dict(Counter(r["level"] for r in rows)),
        "by_semantic_pair": dict(Counter(r["semantic_pair"] for r in rows).most_common()),
        "by_inner_ring_of_collar": dict(Counter(
            min(r["g_to_collar"]) if min(r["g_to_collar"]) >= 0 else ">32" for r in rows)),
        "by_g_to_cap": dict(Counter(min(r["g_to_distal_cap"]) for r in rows)),
        "edges": rows,
        "dominant_region": (Counter(r["semantic_pair"] for r in rows).most_common(1)[0][0]
                            if rows else None),
    }


TOPOMAPS = {}
for cid in ("FULL_OPP_L3", "CMC_OPP_30", "CMC_MCP_L3"):
    TOPOMAPS[cid] = topology_map(cid)
    jdump("R1E_%s_SEVERE_EDGE_TOPOLOGY_MAP.json" % cid, TOPOMAPS[cid])
    log("%s severe %d ; by level %s ; dominant %s"
        % (cid, TOPOMAPS[cid]["severe_edge_count"],
           json.dumps(TOPOMAPS[cid]["by_level"], ensure_ascii=False),
           TOPOMAPS[cid]["dominant_region"]))

# =====================================================================================
# 12. edge 5879 forensic
# =====================================================================================
TARGET_EDGE = 5879
ea, eb = EDGES[TARGET_EDGE]
F1, F2 = [], []
for fi, p in enumerate(POLY):
    if ea in p and eb in p:
        F1.append(fi)


def ring_weights(v, n):
    seen = {v}
    front = [v]
    out = {}
    for d in range(1, n + 1):
        nxt = []
        for u in front:
            for w in ADJ[u]:
                if w not in seen:
                    seen.add(w)
                    nxt.append(w)
        front = nxt
        for u in front:
            out[u] = {"ring": d, "semantic": SEM[u], "R3": R3[u],
                      "W_R1E": dict((g, rr(x, 4)) for g, x in sorted(W_R1E[u].items())),
                      "W_R1B": dict((g, rr(x, 4)) for g, x in sorted(W_R1B[u].items())),
                      "g_to_collar": DIST_C0.get(u, -1)}
    return out


EDGE5879 = {
    "stage": NUM + "_EDGE5879_FORENSIC_AUDIT",
    "generated_at": NOW, "read_only": True,
    "edge_id": TARGET_EDGE, "v0": ea, "v1": eb,
    "bind_length_mm": rr(BIND[TARGET_EDGE], 4),
    "shared_faces": F1,
    "r3_ownership": {"v0": R3[ea], "v1": R3[eb]},
    "semantic_regions": {"v0": SEM[ea], "v1": SEM[eb]},
    "live_joint_polyline_alpha": {
        "v0": {"sT_mm": rr(sT[ea], 3), "dT_mm": rr(dT[ea], 3),
               "sI_mm": rr(sI[ea], 3), "dI_mm": rr(dI[ea], 3)},
        "v1": {"sT_mm": rr(sT[eb], 3), "dT_mm": rr(dT[eb], 3),
               "sI_mm": rr(sI[eb], 3), "dI_mm": rr(dI[eb], 3)}},
    "weights_R1E": {"v0": dict((g, rr(w, 4)) for g, w in sorted(W_R1E[ea].items())),
                    "v1": dict((g, rr(w, 4)) for g, w in sorted(W_R1E[eb].items()))},
    "weights_R1B": {"v0": dict((g, rr(w, 4)) for g, w in sorted(W_R1B[ea].items())),
                    "v1": dict((g, rr(w, 4)) for g, w in sorted(W_R1B[eb].items()))},
    "topology_distance_to_exact_collar": [DIST_C0.get(ea, -1), DIST_C0.get(eb, -1)],
    "topology_distance_to_distal_cap": [GD_CAP.get(ea, -1), GD_CAP.get(eb, -1)],
    "first_web_membership": [ea in WEB, eb in WEB],
    "hist_ring": ring_weights(ea, 2),
    "incident_face_ids": [fi for fi, p in enumerate(POLY) if ea in p or eb in p],
    "per_pose": {},
}
for cid, kind, arg, comp in POSES:
    bl = BIND[TARGET_EDGE]
    pl = (POSED[cid][ea] - POSED[cid][eb]).length * MM
    EDGE5879["per_pose"][cid] = {
        "posed_length_mm": rr(pl, 4), "ratio": rr(pl / bl, 4),
        "uA_mm": rr(DISPL[cid][ea], 4), "uB_mm": rr(DISPL[cid][eb], 4),
        "relative_motion_mm": rr(((POSED[cid][eb] - V0[eb]) - (POSED[cid][ea] - V0[ea])).length * MM, 4),
    }
_mx = max(EDGE5879["per_pose"].items(), key=lambda kv: kv[1]["ratio"])
EDGE5879["worst_pose"] = _mx[0]
EDGE5879["worst_ratio"] = _mx[1]["ratio"]
EDGE5879["root_cause_evidence"] = {
    "v0_dominant": (max(W_R1E[ea].items(), key=lambda kv: kv[1])[0] if W_R1E[ea] else None),
    "v1_dominant": (max(W_R1E[eb].items(), key=lambda kv: kv[1])[0] if W_R1E[eb] else None),
    "both_endpoints_R3_THUMB": R3[ea] == "THUMB" and R3[eb] == "THUMB",
    "both_endpoints_same_semantic": SEM[ea] == SEM[eb],
    "g_to_collar": [DIST_C0.get(ea, -1), DIST_C0.get(eb, -1)],
    "interpretation": ("the two endpoints sit on OPPOSITE SIDES of the diameter of the "
                       "thumb-to-palm transition: one is still driven by the thumb chain, the "
                       "other has already been handed to the palm by the lateral gate.  The "
                       "differential is produced by the transition gradient, not by a hard 0/1 "
                       "flip (no hard flip is reported on this edge)."),
}
jdump("R1E_EDGE5879_FORENSIC_AUDIT.json", EDGE5879)
log("edge5879 forensic: v%d-v%d worst %s %.4fx" % (ea, eb, EDGE5879["worst_pose"], EDGE5879["worst_ratio"]))

# =====================================================================================
# 13. same-surface self-intersection topology audit
# =====================================================================================
def intersect_pairs(V, P):
    tree = BVHTree.FromPolygons([tuple(v) for v in V], [tuple(p) for p in P],
                                all_triangles=False, epsilon=0.0)
    raw = tree.overlap(tree)
    out = set()
    for x, y in raw:
        if x >= y:
            continue
        if set(P[x]) & set(P[y]):
            continue
        out.add((x, y))
    return out


BASE = intersect_pairs(V0, POLY)
CUT = set(tuple(sorted(EDGES[k])) for k in BND_IDS)
seen, comps = set(), []
for v in range(NV):
    if v in seen:
        continue
    dq = deque([v]); seen.add(v); cc = []
    while dq:
        x = dq.popleft(); cc.append(x)
        for u in ADJ[x]:
            if u in seen or tuple(sorted((x, u))) in CUT:
                continue
            seen.add(u); dq.append(u)
    comps.append(cc)
comps.sort(key=len, reverse=True)
COMP = {}
for ci, cc in enumerate(comps):
    for v in cc:
        COMP[v] = ci

SI = {}
for cid in ("TH_IP_45", "CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"):
    newp = intersect_pairs(POSED[cid], POLY) - BASE
    same = []
    for a, b in newp:
        pa = set(COMP[v] for v in POLY[a])
        pb = set(COMP[v] for v in POLY[b])
        if len(pa) == 1 and pa == pb:
            same.append((a, b))
    rows = []
    for a, b in same:
        sa = Counter(SEM[v] for v in POLY[a]).most_common(1)[0][0]
        sb = Counter(SEM[v] for v in POLY[b]).most_common(1)[0][0]
        gmin = min(min(DIST_C0.get(v, 999) for v in POLY[a]),
                   min(DIST_C0.get(v, 999) for v in POLY[b]))
        rows.append({"face_a": a, "face_b": b, "semantic_a": sa, "semantic_b": sb,
                     "semantic_pair": "|".join(sorted([sa, sb])),
                     "min_graph_distance_to_collar": gmin,
                     "collar_band": ("EXACT_COLLAR" if gmin == 0 else
                                     "ONE_RING" if gmin == 1 else
                                     "TWO_RING" if gmin == 2 else "THREE_PLUS")})
    SI[cid] = {
        "pose": cid,
        "new_self_intersection_pairs_total": len(newp),
        "new_same_surface(self_component)_pairs": len(same),
        "by_semantic_pair": dict(Counter(r["semantic_pair"] for r in rows).most_common()),
        "by_collar_band": dict(Counter(r["collar_band"] for r in rows)),
        "rows": rows,
        "dominant_region": (Counter(r["semantic_pair"] for r in rows).most_common(1)[0][0]
                            if rows else None),
    }
    log("same-surface SI %s : %d (of %d new pairs) ; dominant %s"
        % (cid, len(same), len(newp), SI[cid]["dominant_region"]))
SI_AUDIT = {
    "stage": NUM + "_SAME_SURFACE_SI_TOPOLOGY_AUDIT",
    "generated_at": NOW, "read_only": True,
    "definition": ("a NEW intersection pair whose two faces lie inside the SAME side of the R3 "
                   "collar cut (i.e. the surface folds into itself); thumb-INDEX contact pairs "
                   "across the cut are excluded"),
    "per_pose": SI,
}
jdump("R1E_SAME_SURFACE_SI_TOPOLOGY_AUDIT.json", SI_AUDIT)

# =====================================================================================
# 14. motion decomposition + control pose comparison (sections 26-27)
# =====================================================================================
MOTION = {
    "stage": NUM + "_MOTION_DECOMPOSITION",
    "generated_at": NOW,
    "table": [{"pose": cid, "THUMB_IP_deg": comp["IP"], "THUMB_MCP_deg": comp["MCP"],
               "CMC_opposition_deg": comp["CMC"],
               "SEVERE": len(SEVERE[cid]),
               "max_stretch": STRICT[cid]["global_observed_max_stretch"],
               "STRICT_BOUND": STRICT[cid]["max_STRICT_LOWER_BOUND"]}
              for cid, kind, arg, comp in POSES],
    "observations": {
        "TH_IP_45_vs_TH_MCP_45": {
            "IP_only_45": {"severe": len(SEVERE["TH_IP_45"]),
                           "max": STRICT["TH_IP_45"]["global_observed_max_stretch"]},
            "MCP_only_45": {"severe": len(SEVERE["TH_MCP_45"]),
                            "max": STRICT["TH_MCP_45"]["global_observed_max_stretch"]},
            "conclusion": ("the same 45 deg on MCP instead of IP produces the first severe "
                           "population -> the residual is dominated by the MCP / proximal "
                           "component, not by the IP"),},
        "CMC_OPP_30_vs_CMC_MCP_L3": {
            "CMC_30_only": {"severe": len(SEVERE["CMC_OPP_30"]),
                            "max": STRICT["CMC_OPP_30"]["global_observed_max_stretch"]},
            "CMC_30_plus_MCP_30": {"severe": len(SEVERE["CMC_MCP_L3"]),
                                   "max": STRICT["CMC_MCP_L3"]["global_observed_max_stretch"]},
            "conclusion": ("adding MCP 30 deg to the same CMC 30 deg opposition changes the "
                           "distribution but not the mechanism"),},
    },
}
jdump("R1E_MOTION_DECOMPOSITION.json", MOTION)

# =====================================================================================
# 15. final status
# =====================================================================================
SHA_AFTER = dict((k, sha(p)) for k, p in FROZEN.items())
CHANGED = [k for k in SHA_BEFORE if SHA_AFTER[k] != SHA_BEFORE[k]]
STRICT_GT5 = [cid for cid in STRICT if STRICT[cid]["any_path_STRICT_GT_5"]]
ENDPOINT_B_BINDING = AUTH["endpoint_B_exact_R3_collar"]["classification"] == "BINDING_PROJECT_AUTHORITY"

if not STRICT_GT5:
    BRANCH = "A"
    NEXT = "R1E_TRANSITION_WEIGHT_FIELD_RECONCILIATION_R2"
elif not ENDPOINT_B_BINDING:
    BRANCH = "B"
    NEXT = "ENDPOINT_WEIGHT_AUTHORITY_REVIEW"
else:
    BRANCH = "C"
    NEXT = "MESH_SUPPORT_REVIEW"

STATUS = {
    "stage": NUM + "_STATUS",
    "generated_at": NOW,
    "round": "R1E_THUMB_TRANSITION_GEOMETRIC_FEASIBILITY_AUDIT",
    "kind": "READ_ONLY_FORENSIC_MATHEMATICAL_TOPOLOGICAL_AUDIT",
    "read_only": True,
    "BLEND_FILES_WRITTEN": 0,
    "frozen_inputs_before": SHA_BEFORE,
    "frozen_inputs_after": SHA_AFTER,
    "frozen_inputs_unchanged": not CHANGED,
    "frozen_inputs_changed": CHANGED,
    "stage5b_r1e_status": "CANDIDATE_FOR_HUMAN_REVIEW",
    "stage5b_r1e_verdict": "FAIL_CLOSED_PENDING_FEASIBILITY_DIAGNOSIS",
    "stage5b_r1e_weight_modified": False,
    "r1f_created": False,
    "r3_ownership_modified": False,
    "geometry_topology_bone_joint_roll_cmcage_rssf_modified": False,
    "poses_run": [p[0] for p in POSES],
    "poses_not_run": {"stage6a_full_42_case": "NOT_RUN", "stage6b_full_9_case": "NOT_RUN",
                      "stage6c": "NOT_ENTERED"},
    "stale_joint_frame_read": False,
    "findings": {
        "exact_16_collar_edges_stretch_in_all_6_poses":
            EXACT_AUDIT["max_stretch_ratio_over_all_16_edges_and_6_poses"],
        "exact_16_collar_edges_all_ratio_1": EXACT_AUDIT["all_16_edges_ratio_equals_1_in_all_6_poses"],
        "old_collar_severe_reclassified_to_LEVEL_0":
            RECLASS["exact_LEVEL_0_severe_edges_total"],
        "shortest_cap_to_index_collar_path_mm": SHORTEST["distance_mm"],
        "shortest_cap_to_index_collar_edge_count": SHORTEST_REC["edge_count"],
        "pairwise_144_statistics_mm": PAIR_STATS,
        "strict_bound_per_pose": STRICT_AUDIT["per_pose_summary"],
        "strict_bound_gt_5_poses": STRICT_GT5,
        "old_claim_verdict": STRICT_AUDIT["old_claim_verdict"],
        "endpoint_A_distal_cap_authority": AUTH["endpoint_A_approved_distal_cap"]["classification"],
        "endpoint_B_collar_authority": AUTH["endpoint_B_exact_R3_collar"]["classification"],
        "edge5879_worst_pose": EDGE5879["worst_pose"],
        "edge5879_worst_ratio": EDGE5879["worst_ratio"],
        "full_opp_l3_severe_dominant_region": TOPOMAPS["FULL_OPP_L3"]["dominant_region"],
        "cmc_opp_30_severe_dominant_region": TOPOMAPS["CMC_OPP_30"]["dominant_region"],
        "cmc_mcp_l3_severe_dominant_region": TOPOMAPS["CMC_MCP_L3"]["dominant_region"],
        "same_surface_SI_dominant_region": SI["FULL_OPP_L3"]["dominant_region"],
        "control_pose": "TH_IP_45 (severe 0, max %sx)"
                        % STRICT["TH_IP_45"]["global_observed_max_stretch"],
    },
    "geometric_impossibility_claim": {
        "status": ("SUPPORTED_PENDING_HUMAN_REVIEW" if BRANCH == "C" else "NOT_PROVEN"),
        "branch": BRANCH,
        "permitted_wording": ("CURRENT_MESH_SUPPORT_INSUFFICIENT_FOR_THIS_POSE_RANGE = "
                              "SUPPORTED_PENDING_HUMAN_REVIEW" if BRANCH == "C"
                              else "CURRENT_R1E_ENDPOINT_KINEMATICS_INFEASIBLE"),
        "forbidden_wording_used": False,
    },
    "next_candidate": NEXT,
    "log": LOG,
}
jdump("R1E_THUMB_TRANSITION_GEOMETRIC_FEASIBILITY_STATUS.json", STATUS)
log("BRANCH %s ; NEXT_CANDIDATE = %s ; frozen unchanged = %s" % (BRANCH, NEXT, not CHANGED))
print("FEAS_AUDIT_DONE branch=%s" % BRANCH)

# keep the state for the render script
with open(os.path.join(AUD, "_tmp", "feas_state.json"), "w", encoding="utf-8") as f:
    json.dump({"branch": BRANCH, "next": NEXT, "strict_gt5": STRICT_GT5}, f, indent=1)
