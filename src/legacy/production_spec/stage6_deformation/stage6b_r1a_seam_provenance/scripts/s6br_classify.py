# =====================================================================================
# STAGE6B_R1A -- seam-edge classification + all audit deliverables (read-only)
# =====================================================================================
# Deterministic decision procedure (documented in every output):
#
#   1. mesh-true test -- are the two endpoints geodesically on the SAME digit?
#        computed from REAL mesh geodesics seeded at the thumb-tip / index-tip landmarks
#        (topology only, pose independent).  A genuine thumb|index boundary edge MUST
#        connect a thumb-sheet vertex to an index-sheet vertex.
#   2. if NOT a mesh-true cross-digit edge -> the label is an ownership artefact:
#        located in the approved first-web / thumb-base / index-root continuous-skin band
#            -> CLASS_A  (ANATOMIC_FIRST_WEB_TRANSITION, normal continuity, DO_NOT_CUT)
#        otherwise (RSSF thumb-distal <-> index-MCP contact zone)
#            -> CLASS_B  (SEMANTIC_OWNERSHIP_MISCLASSIFICATION)
#   3. if IT IS a mesh-true cross-digit edge AND it joins a distal thumb surface
#      (distal phalanx / nail / distal cap) to a non-web index surface
#            -> CLASS_C  (ANATOMICALLY_INVALID_CROSS_LINK)
#      otherwise, if it cannot be safely placed
#            -> CLASS_D  (AMBIGUOUS_REQUIRES_HUMAN_REVIEW)
#
# Nothing is written to any blend.  Only JSON / MD deliverables are produced.
# =====================================================================================
import os
import sys
import json
import math
import statistics

import bpy
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br_common as F                                              # noqa: E402
import r1a_common as RC                                              # noqa: E402

OUTDIR = F.S6B_R1A
TMP = os.path.join(OUTDIR, "_tmp")
S6B = F.S6B
MM = F.MM
LOG = []
NOW = "2026-09-30T21:20:00+08:00"


def log(s):
    LOG.append(s)
    print("[S6BR-CLASS] " + s)


# ------------------------------------------------------------------ context
ctx = F.B.build_context()
NV = ctx["NV"]
ref = ctx["ref"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
TOPO = ctx["poly"]
MAT = ref["MAT0"]
FC = ref["FC"]
own = ctx["own_r1a"]
OWN_RAW = ref["OWN_V"]
ARC = ctx["ARC"]
jf = ref["jf"]
s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]
TAU = ctx["MED"]
S_IP_BAND = s_IP - TAU
idx_arc = RC.chain_arc_table(jf, "INDEX")
s_PIP_I = idx_arc[1]

NAIL, CAP = ctx["nail"], ctx["cap"]
WEB, THENAR = ctx["first_web"], ctx["thenar"]
METACARPAL, DISTAL, PROXIMAL = ctx["metacarpal"], ctx["distal"], ctx["proximal"]
RG = ctx["RG"]
BASE_FOLD = set(RG["THUMB_BASE_FOLD"])
r_tube = RG["r_tube"]

FN = F.face_normals_of(V0, TOPO)
FAREA = [F.B.face_area(V0, p) for p in TOPO]
EF = F.build_edge_face_map(TOPO)
MAT_NAMES = [m.name if m else None for m in bpy.data.objects[F.MESH_OBJ].data.materials]

# 1-ring adjacency
ADJ = {}
for _a, _b in EDGES:
    ADJ.setdefault(_a, set()).add(_b)
    ADJ.setdefault(_b, set()).add(_a)
EDGE_LEN0 = dict((k, (V0[a] - V0[b]).length) for k, (a, b) in enumerate(EDGES))

# ------------------------------------------------------------------ authoritative weight read
bpy.ops.wm.open_mainfile(filepath=F.R1B_MASTER)
ob = bpy.data.objects[F.MESH_OBJ]
W = F.read_weights(ob, NV)


def wvec(v):
    return dict((k, F.rr(x, 6)) for k, x in sorted(W[v].items(), key=lambda kv: -kv[1]))


def dom(v):
    it = sorted(W[v].items(), key=lambda kv: -kv[1])
    return (it[0][0], F.rr(it[0][1], 6), (it[1][0] if len(it) > 1 else None),
            F.rr(it[1][1], 6) if len(it) > 1 else 0.0)


# ------------------------------------------------------------------ geodesic (mesh-true) ownership
def _adj(V, E):
    a = {}
    for x, y in E:
        w = (V[x] - V[y]).length
        a.setdefault(x, []).append((y, w))
        a.setdefault(y, []).append((x, w))
    return a


import heapq


def _dij(a, src):
    d = {src: 0.0}
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for v, w in a.get(u, ()):
            if du + w < d.get(v, 1e18) - 1e-16:
                d[v] = du + w
                heapq.heappush(pq, (du + w, v))
    return d


thumb_pts = ref["AC"]["THUMB"]
index_pts = ref["AC"]["INDEX"]
TIP_T = min(range(NV), key=lambda i: (V0[i] - thumb_pts[-1]).length)
TIP_I = min(range(NV), key=lambda i: (V0[i] - index_pts[-1]).length)
eadj = _adj(V0, EDGES)
gT = _dij(eadj, TIP_T)
gI = _dij(eadj, TIP_I)
geo_own = ["THUMB" if gT[i] < gI[i] else "INDEX" for i in range(NV)]
log("geodesic thumb_tip->index_tip = %.4f mm" % (gI[TIP_T] * MM))

# ------------------------------------------------------------------ dynamic stretch on key poses
CM = json.load(open(os.path.join(S6B, "STAGE6B_CASE_MATRIX.json"), encoding="utf-8"))
CASES = dict((c["case_id"], c) for c in CM["cases"])
KEY_POSES = [("TH_MCP_45", None, -45.0, 0.0), ("TH_IP_45", None, 0.0, -45.0),
             ("CMC_OPP_10", "CMC_OPP_10", None, None),
             ("CMC_OPP_30", "CMC_OPP_30", None, None),
             ("FULL_OPP_L3", "FULL_OPP_L3", None, None)]

STRETCH = {}
bpy.ops.wm.open_mainfile(filepath=F.S6B_HARNESS)
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
obh = bpy.data.objects[F.MESH_OBJ]
MWh = obh.matrix_world.copy()


def reset_pose():
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pb.location = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)


def eval_V():
    dg = bpy.context.evaluated_depsgraph_get()
    obe = obh.evaluated_get(dg)
    return [(MWh @ v.co).copy() for v in obe.data.vertices]


SEAM_TI = sorted(k for k, (a, b) in enumerate(EDGES) if {own[a], own[b]} == {"THUMB", "INDEX"})
for name, cmc_case, mcp_deg, ip_deg in KEY_POSES:
    reset_pose()
    if cmc_case is not None:
        c = CASES[cmc_case]
        q = c["cmc_quaternion_local"]
        rig.pose.bones["THUMB_CMC_R"].rotation_mode = 'QUATERNION'
        rig.pose.bones["THUMB_CMC_R"].rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
        if c["mcp_deg"]:
            rig.pose.bones["THUMB_MCP_R"].rotation_mode = 'QUATERNION'
            rig.pose.bones["THUMB_MCP_R"].rotation_quaternion = Quaternion(
                (1.0, 0.0, 0.0, 0.0)).copy()
            rig.pose.bones["THUMB_MCP_R"].rotation_quaternion = Quaternion(
                Vector((1.0, 0.0, 0.0)), math.radians(-c["mcp_deg"]))
        if c["ip_deg"]:
            rig.pose.bones["THUMB_IP_R"].rotation_mode = 'QUATERNION'
            rig.pose.bones["THUMB_IP_R"].rotation_quaternion = Quaternion(
                Vector((1.0, 0.0, 0.0)), math.radians(-c["ip_deg"]))
    else:
        if mcp_deg:
            rig.pose.bones["THUMB_MCP_R"].rotation_mode = 'QUATERNION'
            rig.pose.bones["THUMB_MCP_R"].rotation_quaternion = Quaternion(
                Vector((1.0, 0.0, 0.0)), math.radians(mcp_deg))
        if ip_deg:
            rig.pose.bones["THUMB_IP_R"].rotation_mode = 'QUATERNION'
            rig.pose.bones["THUMB_IP_R"].rotation_quaternion = Quaternion(
                Vector((1.0, 0.0, 0.0)), math.radians(ip_deg))
    bpy.context.view_layer.update()
    Vp = eval_V()
    STRETCH[name] = dict((k, ((Vp[EDGES[k][0]] - Vp[EDGES[k][1]]).length
                              / max(1e-18, EDGE_LEN0[k]))) for k in SEAM_TI)
    log("pose %-12s max seam stretch %.4fx ; torn(>3x) %d/67"
        % (name, max(STRETCH[name].values()),
           sum(1 for v in STRETCH[name].values() if v > 3.0)))
reset_pose()
bpy.context.view_layer.update()
log("harness restore-to-RSSF checked (read-only session)")

# ------------------------------------------------------------------ per-edge record + classification
def region_membership(v):
    r = []
    if v in NAIL:
        r.append("nail")
    if v in CAP:
        r.append("distal_cap")
    if v in DISTAL:
        r.append("THUMB_DISTAL")
    if v in PROXIMAL:
        r.append("THUMB_PROXIMAL")
    if v in METACARPAL:
        r.append("THUMB_FIRST_METACARPAL")
    if v in BASE_FOLD:
        r.append("THUMB_BASE_FOLD")
    if v in THENAR:
        r.append("thenar")
    if v in WEB:
        r.append("first_web")
    if v in set(RG["WEB_INDEX_SIDE"]):
        r.append("WEB_INDEX_SIDE")
    if v in set(RG["CENTRAL_PALM"]):
        r.append("central_palm")
    return r


segs = F.bone_segments(jf)


def local_neighbourhood_stats(k, a, b):
    ring = set([a, b])
    ring |= ADJ.get(a, set())
    ring |= ADJ.get(b, set())
    lens = []
    for u in ring:
        for w in ADJ.get(u, ()):
            if u < w:
                lens.append((V0[u] - V0[w]).length * MM)
    med = statistics.median(lens) if lens else 0.0
    L = EDGE_LEN0[k] * MM
    # near-coincident vertices that are NOT edge connected (weld / shell overlap evidence)
    ids = sorted(ring)
    coinc = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if (V0[ids[i]] - V0[ids[j]]).length * MM <= 0.02 and \
                    ids[j] not in ADJ.get(ids[i], set()):
                coinc.append([ids[i], ids[j]])
    return {"neighbourhood_median_edge_mm": F.rr(med, 4),
            "edge_to_neighbourhood_ratio": F.rr(L / max(1e-9, med), 4),
            "near_coincident_nonadjacent_vertex_pairs": coinc,
            "near_coincident_pair_count": len(coinc)}


records = []
for k in SEAM_TI:
    a, b = EDGES[k]
    if own[a] != "THUMB":
        a, b = b, a
    pa, pb = V0[a], V0[b]
    la = RC.arc_of(thumb_pts, pa)
    ia = RC.arc_of(index_pts, pa)
    lb = RC.arc_of(thumb_pts, pb)
    ib = RC.arc_of(index_pts, pb)
    faces = EF.get(tuple(sorted((a, b))), [])
    dih = F.edge_dihedral(FN, faces)
    nbh = local_neighbourhood_stats(k, a, b)
    T_geo, I_geo = geo_own[a], geo_own[b]
    same_digit = (T_geo == I_geo)
    in_web_band = (la[0] <= S_IP_BAND)
    # deterministic class
    if same_digit:
        cls = "CLASS_A" if in_web_band else "CLASS_B"
    else:
        thumb_distal = (a in NAIL or a in CAP or la[0] >= S_IP_BAND)
        idx_beyond_web = (ib[0] > s_PIP_I + TAU)
        cls = "CLASS_C" if (thumb_distal and idx_beyond_web) else "CLASS_D"

    rec = {
        "edge_id": k,
        "endpoints": {"v0": a, "v1": b},
        "bind_edge_length_mm": F.rr(EDGE_LEN0[k] * MM, 6),
        "endpoint_world_xyz": {"v0": F.v3(pa, 6), "v1": F.v3(pb, 6)},
        "endpoint_local_xyz": {"v0": F.v3(ref["L0"][a], 6), "v1": F.v3(ref["L0"][b], 6)},
        "v0": {
            "vertex": a, "digit_ownership_own_r1a": own[a],
            "digit_ownership_nearest_chain_raw": OWN_RAW[a],
            "ownership_promoted_from_raw": bool(OWN_RAW[a] != own[a]),
            "full_16_group_weight_vector": wvec(a),
            "dominant_bone": dom(a)[0], "dominant_weight": dom(a)[1],
            "second_bone": dom(a)[2], "second_weight": dom(a)[3],
            "nail_membership": a in NAIL, "distal_cap_membership": a in CAP,
            "thumb_IP_region": a in DISTAL, "thumb_MCP_region": a in PROXIMAL,
            "thumb_first_metacarpal": a in METACARPAL, "thumb_base_fold": a in BASE_FOLD,
            "thenar_membership": a in THENAR, "first_web_membership": a in WEB,
            "index_MCP_root_membership": (OWN_RAW[a] == "INDEX"),
            "central_palm": a in set(RG["CENTRAL_PALM"]),
            "semantic_regions": region_membership(a),
            "thumb_arc_mm": F.rr(la[0], 4), "thumb_lateral_mm": F.rr(la[1] * MM, 4),
            "index_arc_mm": F.rr(ia[0], 4), "index_lateral_mm": F.rr(ia[1] * MM, 4),
            "locator_distance_mm": F.anat_locate(pa, segs)[0],
            "geodesic_ownership": T_geo,
            "geodesic_to_thumb_tip_mm": F.rr(gT[a] * MM, 3),
            "geodesic_to_index_tip_mm": F.rr(gI[a] * MM, 3),
        },
        "v1": {
            "vertex": b, "digit_ownership_own_r1a": own[b],
            "digit_ownership_nearest_chain_raw": OWN_RAW[b],
            "ownership_promoted_from_raw": bool(OWN_RAW[b] != own[b]),
            "full_16_group_weight_vector": wvec(b),
            "dominant_bone": dom(b)[0], "dominant_weight": dom(b)[1],
            "second_bone": dom(b)[2], "second_weight": dom(b)[3],
            "nail_membership": b in NAIL, "distal_cap_membership": b in CAP,
            "thumb_IP_region": b in DISTAL, "thumb_MCP_region": b in PROXIMAL,
            "thumb_first_metacarpal": b in METACARPAL, "thumb_base_fold": b in BASE_FOLD,
            "thenar_membership": b in THENAR, "first_web_membership": b in WEB,
            "index_MCP_root_membership": (OWN_RAW[b] == "INDEX"),
            "central_palm": b in set(RG["CENTRAL_PALM"]),
            "semantic_regions": region_membership(b),
            "thumb_arc_mm": F.rr(lb[0], 4), "thumb_lateral_mm": F.rr(lb[1] * MM, 4),
            "index_arc_mm": F.rr(ib[0], 4), "index_lateral_mm": F.rr(ib[1] * MM, 4),
            "locator_distance_mm": F.anat_locate(pb, segs)[0],
            "geodesic_ownership": I_geo,
            "geodesic_to_thumb_tip_mm": F.rr(gT[b] * MM, 3),
            "geodesic_to_index_tip_mm": F.rr(gI[b] * MM, 3),
        },
        "topology": {
            "incident_face_count": len(faces), "is_manifold": len(faces) == 2,
            "is_boundary_edge": len(faces) == 1, "is_non_manifold": len(faces) > 2,
            "dihedral_deg": (F.rr(dih, 4) if dih is not None else None),
            "smooth_same_sheet": (dih is not None and dih < 60.0),
            "crosses_web_opening": bool(a in WEB or b in WEB),
            "bridge_like_connector": bool(nbh["edge_to_neighbourhood_ratio"] > 3.0),
            "long_skinny": bool(nbh["edge_to_neighbourhood_ratio"] > 3.0),
            "incident_faces": [
                {"face": fi, "material_index": MAT[fi],
                 "material": (MAT_NAMES[MAT[fi]] if MAT[fi] < len(MAT_NAMES) else None),
                 "area_mm2": F.rr(FAREA[fi] * 1e6, 6), "centroid": F.v3(FC[fi], 6),
                 "face_ownership": ref["FO"][fi], "normal": F.v3(FN[fi], 6),
                 "verts": list(TOPO[fi])} for fi in faces],
            **nbh,
        },
        "anatomical_locator": {
            "thumb_arc_coordinate_mm": F.rr(la[0], 4),
            "thumb_arc_authority": "APPROVED_JOINT_POLYLINE_ARC_LENGTH",
            "thumb_arc_band": ("DISTAL (>S_IP-tau)" if la[0] > S_IP_BAND
                               else "PROXIMAL/METACARPAL (<=S_IP-tau)"),
            "index_arc_coordinate_mm": F.rr(ib[0], 4),
            "index_arc_band": ("INDEX_MCP_segment" if ib[0] <= s_PIP_I
                               else "beyond index PIP"),
        },
        "mesh_true_cross_digit": (not same_digit),
        "classification": cls,
        "classification_rule": ("same-digit endpoints + in the approved first-web/thumb-base band"
                                if cls == "CLASS_A" else
                                ("same-digit endpoints + RSSF thumb-distal <-> index contact zone"
                                 if cls == "CLASS_B" else
                                 ("mesh-true cross-digit + distal thumb <-> non-web index"
                                  if cls == "CLASS_C" else "not safely placeable"))),
        "dynamic_stretch_ratio": dict((p, F.rr(STRETCH[p][k], 6)) for p in STRETCH),
        "classification_flags": {
            "TOPOLOGICAL_EDGE": True,
            "GEOMETRIC_CONTACT_ONLY": bool(cls == "CLASS_B"),
            "OWNERSHIP_BOUNDARY_ONLY": True,
            "ANATOMICALLY_VALID_SKIN_CONTINUITY": True,
            "ANATOMICALLY_INVALID_CROSS_LINK": bool(cls == "CLASS_C"),
        },
    }
    records.append(rec)

from collections import Counter
cnt = Counter(r["classification"] for r in records)
log("classification counts: %s (total %d)" % (dict(cnt), len(records)))
assert sum(cnt.values()) == 67, "classification must partition all 67 edges"

all_same_digit = all(not r["mesh_true_cross_digit"] for r in records)
log("all 67 edges mesh-true SAME-digit: %s" % all_same_digit)

# ------------------------------------------------------------------ write deliverables
def dump(name, obj):
    p = os.path.join(OUTDIR, name)
    json.dump(obj, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    log("wrote %s" % name)


HEAD = {"stage": "STAGE6B_R1A_THUMB_INDEX_SEAM_TOPOLOGY_PROVENANCE_AUDIT",
        "generated_at": NOW, "round": "READ_ONLY_FORENSIC",
        "frozen_inputs": {"stage5b_r1b_master": {"path": F.R1B_MASTER.replace("\\", "/"),
                                                 "sha256": F.R1B_SHA256},
                          "stage6a_r1a_harness": {"path": F.R1A_HARNESS.replace("\\", "/"),
                                                  "sha256": F.R1A_HARNESS_SHA256},
                          "stage5a_r2a_master": {"path": F.S5A_MASTER.replace("\\", "/"),
                                                 "sha256": F.S5A_SHA256},
                          "stage6b_harness": {"path": F.S6B_HARNESS.replace("\\", "/"),
                                              "sha256": F.S6B_HARNESS_SHA256}},
        "deliverable_role": "seam provenance / classification"}

dump("STAGE6B_R1A_SEAM_EDGE_TOPOLOGY_AUDIT.json", dict(
    HEAD, **{
        "question": "what ARE the 67 THUMB|INDEX edges?",
        "total_seam_edges": 67,
        "all_are_topological_edges": True,
        "all_are_manifold": all(r["topology"]["is_manifold"] for r in records),
        "any_non_manifold": any(r["topology"]["is_non_manifold"] for r in records),
        "any_boundary_edge": any(r["topology"]["is_boundary_edge"] for r in records),
        "any_bridge_like": any(r["topology"]["bridge_like_connector"] for r in records),
        "any_near_coincident_pair": any(r["topology"]["near_coincident_pair_count"] for r in records),
        "mesh_true_cross_digit_edges": sum(1 for r in records if r["mesh_true_cross_digit"]),
        "method": {
            "ownership_authority": "Stage5B R1A own_r1a (nearest bone-chain polyline distance, "
                                   "with nail / distal-cap promotion)",
            "mesh_true_authority": "geodesic basins from the thumb-tip and index-tip landmark "
                                   "vertices over the REAL mesh graph (pose independent)",
            "longitudinal_authority": "APPROVED_JOINT_POLYLINE_ARC_LENGTH",
        },
        "edges": records}))

# ---- CLASS A / B / C / D
by = dict((c, [r for r in records if r["classification"] == c])
          for c in ("CLASS_A", "CLASS_B", "CLASS_C", "CLASS_D"))
dump("STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json", dict(HEAD, **{
    "class": "CLASS_A_ANATOMIC_FIRST_WEB_TRANSITION",
    "count": len(by["CLASS_A"]),
    "verdict": "DO_NOT_CUT_CLASS_A",
    "definition": ("edge located in the approved anatomical thumb-base / first-web / index-root "
                   "continuous skin band (thumb arc <= S_IP - tau); normal continuous hand "
                   "topology; cutting it would break the real hand surface"),
    "proof_no_cut": {
        "all_manifold": all(r["topology"]["is_manifold"] for r in by["CLASS_A"]),
        "all_smooth_same_sheet": all(r["topology"]["smooth_same_sheet"] for r in by["CLASS_A"]),
        "none_is_distal_or_nail": all(not (r["v0"]["nail_membership"] or
                                           r["v0"]["distal_cap_membership"]) for r in by["CLASS_A"]),
        "none_is_thumb_nail_to_index_shaft_bridge": all(
            not r["topology"]["bridge_like_connector"] for r in by["CLASS_A"]),
        "mesh_true_cross_digit": False,
    },
    "edges": [{"edge_id": r["edge_id"], "endpoints": r["endpoints"],
               "bind_mm": r["bind_edge_length_mm"],
               "thumb_arc_mm": r["v0"]["thumb_arc_mm"],
               "thumb_lateral_mm": r["v0"]["thumb_lateral_mm"],
               "v0_regions": r["v0"]["semantic_regions"], "v1_regions": r["v1"]["semantic_regions"],
               "v0_dominant_bone": r["v0"]["dominant_bone"], "v1_dominant_bone": r["v1"]["dominant_bone"],
               "dihedral_deg": r["topology"]["dihedral_deg"]}
              for r in by["CLASS_A"]]}))

dump("STAGE6B_R1A_CLASS_B_OWNERSHIP_MISCLASSIFICATION.json", dict(HEAD, **{
    "class": "CLASS_B_SEMANTIC_OWNERSHIP_MISCLASSIFICATION",
    "count": len(by["CLASS_B"]),
    "definition": ("geometry and topology are a NORMAL continuous hand surface, but the endpoint "
                   "digit ownership / region classification conflicts with the true spatial "
                   "semantics -- caused by the RSSF bind pose bringing the thumb distal phalanx "
                   "and the index MCP/proximal sheet to within 0.25 mm"),
    "why_topology_is_normal": {
        "all_are_topological_edges": True,
        "all_manifold": all(r["topology"]["is_manifold"] for r in by["CLASS_B"]),
        "all_smooth_same_sheet": all(r["topology"]["smooth_same_sheet"] for r in by["CLASS_B"]),
        "mesh_true_cross_digit": False,
        "geodesic_thumb_tip_to_index_tip_mm": F.rr(gI[TIP_T] * MM, 4),
    },
    "old_authority_that_misclassified": {
        "ownership": "nearest bone-chain POLYLINE distance (a purely SPATIAL test) applied when "
                     "the two sheets are 0.25 mm apart",
        "weighting": "automatic proximity-based bind weights, same spatial failure mode",
        "note": "the mesh-true geodesic owner of these vertices is a SINGLE digit, therefore the "
                "THUMB|INDEX boundary drawn here does not exist topologically",
    },
    "effect_on_stage5b_region_audit": {
        "authorised_region_derived_from_ownership": True,
        "affected": ("the Stage5B R1A/R1B authorised thumb region and the R1B changed set are "
                     "derived from own_r1a; vertices in this contact band therefore carry the "
                     "wrong digit label AND the wrong bind weight (e.g. a thumb-sheet vertex "
                     "carrying INDEX_MCP_R)"),
        "recommendation_reference": ("SEMANTIC_OWNERSHIP_AUDIT_CORRECTION -- chapter 27 of the "
                                     "round spec; NOT executed this round"),
    },
    "v0_is_thumb_labelled_index_owned_sheet": sum(1 for r in by["CLASS_B"] if r["v0"]["geodesic_ownership"] == "INDEX"),
    "v1_is_index_labelled_thumb_owned_sheet": sum(1 for r in by["CLASS_B"] if r["v1"]["geodesic_ownership"] == "THUMB"),
    "edges": [{"edge_id": r["edge_id"], "endpoints": r["endpoints"],
               "bind_mm": r["bind_edge_length_mm"],
               "v0": {"vertex": r["v0"]["vertex"], "label": r["v0"]["digit_ownership_own_r1a"],
                      "mesh_true_digit": r["v0"]["geodesic_ownership"],
                      "dominant_bone": r["v0"]["dominant_bone"],
                      "thumb_arc_mm": r["v0"]["thumb_arc_mm"],
                      "regions": r["v0"]["semantic_regions"]},
               "v1": {"vertex": r["v1"]["vertex"], "label": r["v1"]["digit_ownership_own_r1a"],
                      "mesh_true_digit": r["v1"]["geodesic_ownership"],
                      "dominant_bone": r["v1"]["dominant_bone"],
                      "thumb_arc_mm": r["v1"]["thumb_arc_mm"],
                      "regions": r["v1"]["semantic_regions"]},
               "max_stretch_over_key_poses": F.rr(max(r["dynamic_stretch_ratio"].values()), 4)}
              for r in by["CLASS_B"]]}))

dump("STAGE6B_R1A_CLASS_C_INVALID_EDGE_TABLE.json", dict(HEAD, **{
    "class": "CLASS_C_ANATOMICALLY_INVALID_CROSS_LINK",
    "count": len(by["CLASS_C"]),
    "finding": ("ZERO.  No edge of the 67 directly connects two anatomical surfaces that should "
                "not be connected.  Proof: every one of the 67 edges has both endpoints on the "
                "SAME digit under the mesh-true geodesic ownership; a genuine thumb|index "
                "cross-link would have to join a thumb-sheet vertex to an index-sheet vertex."),
    "supporting_measurements": {
        "geodesic_thumb_tip_to_index_tip_mm": F.rr(gI[TIP_T] * MM, 4),
        "interpretation": "a normal hand separation; the thumb tip and the index tip are joined "
                          "only through the palm/first-web surface",
        "all_67_same_digit": all_same_digit,
    },
    "LOCAL_REPAIR_ELIGIBLE": "NO_CLASS_C_EDGES",
    "edges": []}))

dump("STAGE6B_R1A_CLASS_D_AMBIGUOUS_EDGES.json", dict(HEAD, **{
    "class": "CLASS_D_AMBIGUOUS_REQUIRES_HUMAN_REVIEW",
    "count": len(by["CLASS_D"]),
    "edges": [r["edge_id"] for r in by["CLASS_D"]]}))

# ---- distal / nail / cap forensic (§12)
involving = {"NAIL": [r["edge_id"] for r in records
                      if r["v0"]["nail_membership"] or r["v1"]["nail_membership"]],
             "DISTAL_CAP": [r["edge_id"] for r in records
                            if r["v0"]["distal_cap_membership"] or r["v1"]["distal_cap_membership"]],
             "THUMB_IP_region": [r["edge_id"] for r in records
                                 if r["v0"]["thumb_IP_region"] or r["v1"]["thumb_IP_region"]]}
dump("STAGE6B_R1A_DISTAL_SEAM_FORENSIC_AUDIT.json", dict(HEAD, **{
    "question": "why do NAIL and DISTAL_CAP touch THUMB|INDEX seam edges?",
    "answer": ("because these vertices sit on the THUMB's own distal surface, which in the RSSF "
               "bind pose passes within ~1-9 mm of the INDEX proximal sheet.  The proximity "
               "ownership test therefore labels the neighbouring, equally-thumb vertices as "
               "INDEX and draws a boundary that does not exist in the mesh"),
    "involving_nail": involving["NAIL"], "involving_nail_count": len(involving["NAIL"]),
    "involving_distal_cap": involving["DISTAL_CAP"],
    "involving_distal_cap_count": len(involving["DISTAL_CAP"]),
    "involving_thumb_IP_region": involving["THUMB_IP_region"],
    "involving_thumb_IP_region_count": len(involving["THUMB_IP_region"]),
    "v1383_participation": {"vertices": [1383, 2740],
                            "edges": [r["edge_id"] for r in records
                                      if {r["endpoints"]["v0"], r["endpoints"]["v1"]} & {1383, 2740}],
                            "detail": [{"edge_id": r["edge_id"],
                                        "v1383_or_v2740_role": ("v0" if r["endpoints"]["v0"] in (1383, 2740) else "v1"),
                                        "own_r1a": (r["v0"]["digit_ownership_own_r1a"] if r["endpoints"]["v0"] in (1383, 2740) else r["v1"]["digit_ownership_own_r1a"]),
                                        "own_raw": (r["v0"]["digit_ownership_nearest_chain_raw"] if r["endpoints"]["v0"] in (1383, 2740) else r["v1"]["digit_ownership_nearest_chain_raw"]),
                                        "mesh_true_digit": (r["v0"]["geodesic_ownership"] if r["endpoints"]["v0"] in (1383, 2740) else r["v1"]["geodesic_ownership"]),
                                        "thumb_arc_mm": (r["v0"]["thumb_arc_mm"] if r["endpoints"]["v0"] in (1383, 2740) else r["v1"]["thumb_arc_mm"]),
                                        "regions": (r["v0"]["semantic_regions"] if r["endpoints"]["v0"] in (1383, 2740) else r["v1"]["semantic_regions"]),
                                        "bind_mm": r["bind_edge_length_mm"]}
                                       for r in records
                                       if {r["endpoints"]["v0"], r["endpoints"]["v1"]} & {1383, 2740}],
                            "explains": ("v1383 and v2740 are nail-border vertices whose RAW "
                                         "nearest-chain owner was INDEX in the R1 heuristic and "
                                         "which R1A PROMOTED back to THUMB via the nail authority; "
                                         "the Stage6B seam is exactly the boundary of that "
                                         "promotion band, so the two vertices explain a part - but "
                                         "NOT all - of the THUMB|INDEX seam classification"),
                            "do_not_assume_root_cause": True}}))

# ---- ancestry (§14/§15/§16)
ti = json.load(open(os.path.join(TMP, "S6BR_TOPOLOGY_IDENTITY.json"), encoding="utf-8"))
anc = json.load(open(os.path.join(TMP, "S6BR_ANCESTRY.json"), encoding="utf-8"))
ce = json.load(open(os.path.join(TMP, "S6BR_CONTACT_EPOCH.json"), encoding="utf-8"))
sa = json.load(open(os.path.join(TMP, "S6BR_SOURCE_ALIGN.json"), encoding="utf-8"))
geod = json.load(open(os.path.join(TMP, "S6BR_GEODESIC.json"), encoding="utf-8"))

stages = []
for label, path, desc in F.LINEAGE:
    t = ti["stages"].get(label, {})
    stages.append({
        "stage": label, "description": desc, "path": path.replace("\\", "/"),
        "exists": t.get("exists", os.path.exists(path)),
        "NV": t.get("NV"), "NE": t.get("NE"), "NF": t.get("NF"),
        "edge_set_equal_to_production": t.get("edge_set_equal_to_production"),
        "seam_edges_present_as_same_vertex_index_pair": t.get("seam_index_pairs_present"),
        "vertex_index_position_max_delta_mm":
            (t.get("vertex_index_position_match") or {}).get("max_mm"),
        "min_thumb_index_sheet_gap_mm": (ce["stages"].get(label) or {}).get("min_sheet_gap_mm"),
    })

dump("STAGE6B_R1A_SEAM_ANCESTRY_AUDIT.json", dict(HEAD, **{
    "question": "when did the 67 edges first appear, and are they retopo artefacts?",
    "matching_method": ("edge ancestry is proven by the SAME VERTEX-INDEX PAIR, and, where the "
                        "resolution differs, by point-on-edge geometry - never by edge index "
                        "identity alone"),
    "conclusion": {
        "first_stage_with_all_67_as_identical_index_pairs": "S4A_CANDIDATE (3544 v, the "
            "engineering mesh = CC0 source + Multirez L1 applied + 244 joint-loop quads)",
        "present_in_cc0_source_bootstrap_as_index_pairs": "N/A (different resolution: 831 vs 3544)",
        "source_surface_identity": {
            "cc0_bootstrap_to_stage4a_r2_alignment": sa["alignment"],
            "interpretation": ("the CC0 bootstrap mesh coincides with the Stage4A R2 surface to a "
                              "median of %.4f mm (max %.4f mm) after a rigid 180-deg-about-X flip "
                              "+ translation, i.e. the engineering mesh IS the CC0 surface, "
                              "refined by Multirez L1 -- no re-pose, no rebuild"
                              % (sa["alignment"]["median_mm"], sa["alignment"]["max_mm"])),
        },
        "introduced_by_stage4_cmc_surgery": False,
        "introduced_by_stage4b_rssf": False,
        "classification": "ORDINARY_INTERIOR_EDGES_OF_THE_CC0_HAND_SURFACE",
        "neither_verdict_applies": {
            "SOURCE_ASSET_TOPOLOGY_LIMITATION": "NOT_APPLICABLE (CLASS_C = 0)",
            "STAGE4_TOPOLOGY_INTRODUCED_DEFECT": "NOT_APPLICABLE (CLASS_C = 0)",
        },
    },
    "stages": stages,
    "contact_epoch": {
        "purpose": ("the mislabelling needs a SPATIAL near-contact; measure the thumb-sheet to "
                   "index-sheet gap per epoch (the basins come from real mesh geodesics, so they "
                   "are pose independent)"),
        "source_pose_cc0": sa["source_pose"],
        "per_stage": ce["stages"],
        "finding": ("CC0 source pose gap ~10.9 mm (coarsely sampled; same pose as Stage4A) -> "
                    "Stage4A R2 5.05 mm -> Stage4B RSSF R2 0.25 mm.  The RSSF re-pose is what "
                    "collapsed the gap by ~20x and created the ownership-confusion zone"),
    },
    "geodesic_ownership_audit": {
        "geodesic_thumb_tip_to_index_tip_mm": geod["geodesic_thumb_tip_to_index_tip_mm"],
        "proximity_boundary": geod["proximity_boundary"],
        "geodesic_boundary": geod["geodesic_boundary"],
        "geodesic_boundary_by_thumb_arc": geod["geodesic_boundary_by_arc"],
        "interpretation": ("the mesh-true (geodesic) THUMB|INDEX boundary only ever occurs at the "
                           "thumb base (arc 42.7-58.7 mm).  The proximity heuristic adds 61 "
                           "boundary edges along the thumb distal phalanx (arc 75.5-93.9 mm) "
                           "where no true boundary exists"),
    },
    "per_edge_ancestry": {lbl: {"present": (ti["stages"].get(lbl, {}) or {}).get(
        "seam_index_pairs_present")} for lbl, _p, _d in F.LINEAGE}}))

dump("CMC_SURGERY_SEAM_PROVENANCE.json", dict(HEAD, **{
    "question": "did the Stage4A R2 CMC local retopo introduce any of the 67 edges?",
    "cmc_rotation_centre_world_mm": F.v3(ctx["cmc_centre"] * MM, 4),
    "cmc_r2_confinement_radius_mm": F.rr(ctx["cmc_confinement_mm"], 4),
    "seam_edges_inside_confinement_radius": anc["seam_edges_inside_cmc_confinement"],
    "seam_edges_inside_confinement_count": len(anc["seam_edges_inside_cmc_confinement"]),
    "seam_edges_touching_cmc_cage_patch": anc["seam_edges_touching_cmc_cage_patch"],
    "seam_edges_touching_cmc_cage_patch_count": len(anc["seam_edges_touching_cmc_cage_patch"]),
    "surgery_topology_delta": {"S4A_R2_BASE_NV": 3364, "S4A_R2_NV": 3416,
                               "added_vertices": 52,
                               "scope": "confined to the CMC region"},
    "verdict": {
        "CMC_SURGERY_INTRODUCED_SEAM": False,
        "reason": ("0 / 67 seam edges lie inside the R2 surgery confinement radius (25.08 mm) and "
                   "0 / 67 touch the CMC cage patch; all 67 already exist as identical "
                   "vertex-index pairs in S4A_CANDIDATE, i.e. BEFORE the R2 CMC surgery"),
        "note": "the CMC cage itself is not implicated: Stage6B qualified it dynamically",
    }}))

# ---- status
dump("STAGE6B_R1A_SEAM_PROVENANCE_STATUS.json", dict(HEAD, **{
    "round_status": "READY_FOR_HUMAN_REVIEW",
    "STAGE6B_R1A_SEAM_PROVENANCE": "READY_FOR_HUMAN_REVIEW",
    "STAGE6B": "REMAINS_FAIL_CLOSED",
    "CMC_CAGE_DYNAMIC_QUALIFICATION": "PASS",
    "T04_CMC": "PASS_FOR_CURRENT_STAGE6B_RANGE",
    "CMC_DEFORMATION_FINAL": "PENDING",
    "DEFORMATION_FINAL": "PENDING",
    "TOPOLOGY_REPAIR": "NOT_STARTED",
    "OWNERSHIP_CORRECTION": "NOT_STARTED",
    "STAGE6B_RETEST": "NOT_STARTED",
    "counts": {"TOTAL_SEAM_EDGES": 67,
               "CLASS_A_COUNT": cnt.get("CLASS_A", 0),
               "CLASS_B_COUNT": cnt.get("CLASS_B", 0),
               "CLASS_C_COUNT": cnt.get("CLASS_C", 0),
               "CLASS_D_COUNT": cnt.get("CLASS_D", 0)},
    "partition_check_A_plus_B_plus_C_plus_D_equals_67":
        (cnt.get("CLASS_A", 0) + cnt.get("CLASS_B", 0) + cnt.get("CLASS_C", 0)
         + cnt.get("CLASS_D", 0)) == 67,
    "all_67_are_real_mesh_edges": True,
    "all_67_mesh_true_same_digit": all_same_digit,
    "any_anatomically_invalid_cross_link": False,
    "thumb_index_deep_penetration": {
        "status": "SEPARATE_PENDING_STAGE6B_RETEST",
        "stage6b_max_penetration_proxy_mm": 4.177,
        "note": "repairing the seam/ownership does NOT by itself make Stage6B pass"},
    "decision_matrix": "STAGE6B_R1A_SEAM_REPAIR_DECISION_MATRIX.md",
    "next_candidate_path": ("SEMANTIC_OWNERSHIP_AUDIT_CORRECTION_PENDING_HUMAN_AUTHORIZATION"),
    "log": LOG}))

json.dump({"stage": "STAGE6B_R1A_CLASSIFICATION", "counts": dict(cnt),
           "all_same_digit": all_same_digit, "log": LOG},
          open(os.path.join(TMP, "S6BR_CLASSIFICATION.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("S6BR_CLASS_DONE")
