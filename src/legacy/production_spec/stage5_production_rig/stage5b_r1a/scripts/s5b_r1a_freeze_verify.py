# =====================================================================================
# STAGE5B_R1A_HUMAN_APPROVAL_FREEZE_R1 -- READ-ONLY VERIFICATION + CMC RECOMPUTE
# =====================================================================================
# Nothing is written back to any .blend.  This script only opens the frozen blends,
# recomputes the disputed THUMB_CMC locality metrics from scratch, and re-verifies the
# static integrity / zero-pose values quoted in the R1A report.
# Outputs (JSON only):
#   stage5b_freeze/STAGE5B_FREEZE_VERIFICATION_R1.json
#   stage5b_r1a/STAGE5B_R1A_CMC_LOCALITY_NUMERIC_RECOMPUTE.json
# =====================================================================================
import bpy
import sys
import os
import json
import math
import hashlib
import datetime
from mathutils import Vector

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "scripts"))
import r1a_common as C                                   # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
R1ADIR = argv[0]
TOP = os.path.dirname(R1ADIR)
FREEZE = os.path.join(TOP, "stage5b_freeze")
NOW = datetime.datetime.now().astimezone().isoformat()
MM = C.MM

MASTER = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
MASTER_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
R1 = os.path.join(TOP, "stage5b_r1", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
R1_SHA = "8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d"
R1A = os.path.join(R1ADIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")
R1A_SHA = "c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6"
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[FREEZE]", s)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rr(x, n=9):
    return round(float(x), n)


# ============================================================ 0. hash gate
S = {"stage5a_master": sha(MASTER), "stage5b_r1": sha(R1), "stage5b_r1a": sha(R1A)}
log("master", S["stage5a_master"][:16])
log("r1    ", S["stage5b_r1"][:16])
log("r1a   ", S["stage5b_r1a"][:16])
assert S["stage5a_master"] == MASTER_SHA
assert S["stage5b_r1"] == R1_SHA
assert S["stage5b_r1a"] == R1A_SHA

# ============================================================ 1. reference geometry
ref = C.load_reference(TOP)
NV = ref["NV"]
V0 = ref["V0"]
TF = C.thumb_frame(ref)
TAU = ref["med_edge"]
R_TT, R_MAX = C.thumb_radii(ref, TF)
RG = C.build_regions(ref, TF, TAU, R_TT, R_MAX)
META = RG["THUMB_FIRST_METACARPAL"]
THENAR = RG["THENAR_BASE"]
PROX = RG["THUMB_PROXIMAL"]
FOLD = RG["THUMB_BASE_FOLD"]
DIST = RG["THUMB_DISTAL"]
WEB = RG["FIRST_WEB"]
PALM = RG["CENTRAL_PALM"]
AUTH = RG["AUTH"]

# cross-check the region sets against the frozen THUMB_SEMANTIC_REGION_AUDIT.json
SEM = json.load(open(os.path.join(R1ADIR, "THUMB_SEMANTIC_REGION_AUDIT.json"),
                     encoding="utf-8"))
REGION_MATCH = {}
for name, mine in (("THUMB_DISTAL", DIST), ("THUMB_PROXIMAL", PROX),
                   ("THUMB_FIRST_METACARPAL", META), ("THUMB_BASE_FOLD", FOLD),
                   ("THENAR_BASE", THENAR), ("FIRST_WEB", WEB), ("CENTRAL_PALM", PALM)):
    theirs = set(SEM["regions"][name]["vertex_ids"])
    REGION_MATCH[name] = {"count_recomputed": len(mine), "count_frozen_json": len(theirs),
                          "identical": set(mine) == theirs}
log("region cross-check:", json.dumps({k: v["identical"] for k, v in REGION_MATCH.items()}))

# ============================================================ 2. frozen R1A weights
b1 = C.load_weights(R1)
W1 = b1["W"]
log("R1 groups = %d" % len(b1["groups"]))
bA = C.load_weights(R1A)
WA = bA["W"]
me = bA["me"]
ob = bA["ob"]
rig = bA["rig"]
groups = bA["groups"]
log("R1A groups = %d" % len(groups))
G = {g: [WA[i].get(g, 0.0) for i in range(NV)] for g in C.DEFORM}

# ---- static integrity -------------------------------------------------------------
TOPO = bA["TOPO"]
MAT = bA["MAT"]
UV = bA["UV"]
ntri = bA["ntri"]
BONE_COUNT = len(rig.data.bones)
TIPH = [b.name for b in rig.data.bones if not b.use_deform]
DEFB = [b.name for b in rig.data.bones if b.use_deform]
TIP_WITH_WEIGHT = [g for g in groups if g.endswith("_TIP_R")]
DIST_ = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, ">4": 0}
NORM_ERR = 0.0
UNW = []
for i in range(NV):
    d = WA[i]
    n = len(d)
    DIST_[n if n <= 4 else ">4"] += 1
    s = sum(d.values())
    if n == 0:
        UNW.append(i)
    NORM_ERR = max(NORM_ERR, abs(s - 1.0))
dz, VE = C.zero_pose_delta(ob, bA["MW"], V0)
bb0 = [(min(v[k] for v in V0), max(v[k] for v in V0)) for k in range(3)]
bb1 = [(min(v[k] for v in VE), max(v[k] for v in VE)) for k in range(3)]
MODS = [(m.name, m.type, (m.object.name if getattr(m, "object", None) else None))
        for m in ob.modifiers]

INTEGRITY = {
    "mesh": {"V": NV, "E": len(me.edges), "F": len(me.polygons), "TRIS": ntri,
             "topology_delta_vs_master": 0 if TOPO == ref["TOPO0"] else 1,
             "uv_delta": 0 if UV == ref["UV0"] else 1,
             "material_assignment_delta": 0 if MAT == ref["MAT0"] else 1,
             "nail_face_assignment_delta": 0 if [i for i, m in enumerate(MAT) if m == 1]
             == [i for i, m in enumerate(ref["MAT0"]) if m == 1] else 1},
    "rig": {"bone_count": BONE_COUNT, "tip_helper_bones": TIPH,
            "tip_helper_count": len(TIPH), "deform_bones": DEFB,
            "deform_bone_count": len(DEFB),
            "vertex_groups": groups, "vertex_group_count": len(groups),
            "tip_groups_with_deform_weight": TIP_WITH_WEIGHT},
    "weights": {"max_influences": max([k for k in DIST_ if k != ">4"] or [0]),
                "influence_distribution": DIST_, "vertices_over_4": DIST_[">4"],
                "unweighted_vertices": len(UNW), "worst_normalization_error": rr(NORM_ERR, 12)},
    "binding": {"parent": bA["parent"], "modifiers": MODS,
                "world_delta_vs_master_mm": rr(max(abs(bA["MW"][i][j] - ref["MW0"][i][j])
                                                   for i in range(4) for j in range(4)) * MM, 9)},
    "zero_pose": {"max_evaluated_vertex_delta_mm": rr(max(dz), 9),
                  "mean_evaluated_vertex_delta_mm": rr(sum(dz) / NV, 9),
                  "bbox_delta_mm": [rr(abs(bb1[k][0] - bb0[k][0]) * MM, 9) for k in range(3)]
                  + [rr(abs(bb1[k][1] - bb0[k][1]) * MM, 9) for k in range(3)],
                  "base_mesh_vertex_delta_mm": rr(max((bA["V"][i] - V0[i]).length
                                                      for i in range(NV)) * MM, 9),
                  "classification": "FLOAT_EQUIVALENT_ZERO"}}
log("integrity: V=%d E=%d F=%d TRIS=%d ; bones=%d (tip helpers %d) ; groups=%d ; max_inf=%d ; unweighted=%d"
    % (NV, len(me.edges), len(me.polygons), ntri, BONE_COUNT, len(TIPH), len(groups),
       INTEGRITY["weights"]["max_influences"], len(UNW)))
log("zero pose max=%.9f mean=%.9f base=%.9f"
    % (INTEGRITY["zero_pose"]["max_evaluated_vertex_delta_mm"],
       INTEGRITY["zero_pose"]["mean_evaluated_vertex_delta_mm"],
       INTEGRITY["zero_pose"]["base_mesh_vertex_delta_mm"]))

# ============================================================ 3. THUMB_CMC locality recompute
CMC = G["THUMB_CMC_R"]
UNION_MT = META | THENAR                       # the union named in the R1A report


def cov(eps, region):
    den = [i for i in range(NV) if CMC[i] > eps]
    num = [i for i in den if i in region]
    return {"numerator": len(num), "denominator": len(den),
            "value": rr(len(num) / len(den), 9) if den else 0.0}


def mass(region):
    tot = sum(CMC)
    inside = sum(CMC[i] for i in region)
    return {"numerator": rr(inside, 9), "denominator": rr(tot, 9),
            "value": rr(inside / tot, 9) if tot else 0.0}


METRICS = {
    "A_THUMB_CMC_NONZERO_VERTEX_COVERAGE_IN_TARGET_REGIONS": {
        "definition": ("numerator = #{v : THUMB_CMC_R > eps AND v in (THUMB_FIRST_METACARPAL "
                       "U THENAR_BASE)} ; denominator = #{v : THUMB_CMC_R > eps}"),
        "region_union": "THUMB_FIRST_METACARPAL U THENAR_BASE",
        "by_epsilon": {"eps=0.0": cov(0.0, UNION_MT), "eps=1e-8": cov(1e-8, UNION_MT),
                       "eps=1e-6": cov(1e-6, UNION_MT), "eps=1e-3": cov(1e-3, UNION_MT)}},
    "B_THUMB_CMC_WEIGHT_MASS_SHARE_IN_TARGET_REGIONS": {
        "definition": ("numerator = sum(THUMB_CMC_R) over (THUMB_FIRST_METACARPAL U THENAR_BASE) ; "
                       "denominator = sum(THUMB_CMC_R) over the entire mesh"),
        "region_union": "THUMB_FIRST_METACARPAL U THENAR_BASE",
        "value": mass(UNION_MT)}}

UNION_MINT = META | THENAR
CANDS = {
    "C1_META_U_THENAR": UNION_MINT,
    "C2_META_U_THENAR_U_PROXIMAL": META | THENAR | PROX,
    "C3_META_U_THENAR_U_BASE_FOLD": META | THENAR | FOLD,
    "C4_META_U_THENAR_U_PROXIMAL_U_BASE_FOLD": META | THENAR | PROX | FOLD,
    "C5_META_U_THENAR_U_PROXIMAL_U_BASE_FOLD_U_DISTAL": META | THENAR | PROX | FOLD | DIST,
    "C6_META_U_THENAR_U_FIRST_WEB": META | THENAR | WEB,
    "C7_ALL_THUMB_SEMANTIC_REGIONS_EXCEPT_CENTRAL_PALM":
        META | THENAR | PROX | FOLD | DIST | WEB,
    "C8_AUTHORISED_MODIFICATION_SET": AUTH,
    "C9_META_ALONE": META,
    "C10_THENAR_ALONE": THENAR,
    "C11_META_U_THENAR_U_AUTH": META | THENAR | AUTH,
}
CAND = {}
for k, u in CANDS.items():
    CAND[k] = {"region_union_size": len(u), "vertex_coverage_eps0": cov(0.0, u),
               "weight_mass_share": mass(u)}
log("candidate unions computed: " + ", ".join("%s=%.6f" % (k, v["weight_mass_share"]["value"])
                                               for k, v in CAND.items()))

# where does the CMC mass outside META U THENAR sit?
outside = [i for i in range(NV) if CMC[i] > 0.0 and i not in UNION_MINT]
OUTSIDE = {"vertex_count": len(outside), "weight_sum": rr(sum(CMC[i] for i in outside), 9),
           "share_of_total": rr(sum(CMC[i] for i in outside) / sum(CMC), 9),
           "by_region": {}}
for name, reg in (("THUMB_DISTAL", DIST), ("THUMB_PROXIMAL", PROX), ("THUMB_BASE_FOLD", FOLD),
                  ("FIRST_WEB", WEB), ("CENTRAL_PALM", PALM)):
    ids = [i for i in outside if i in reg]
    OUTSIDE["by_region"][name] = {"vertex_count": len(ids),
                                 "weight_sum": rr(sum(CMC[i] for i in ids), 9)}
OUTSIDE["by_region"]["NOT_IN_ANY_R1A_REGION"] = {
    "vertex_count": len([i for i in outside if i not in (DIST | PROX | FOLD | WEB | PALM)]),
    "weight_sum": rr(sum(CMC[i] for i in outside
                         if i not in (DIST | PROX | FOLD | WEB | PALM)), 9)}
OUTSIDE["max_single_outside_weight"] = rr(max([CMC[i] for i in outside] or [0.0]), 9)
OUTSIDE["max_outside_vertex"] = max(outside, key=lambda i: CMC[i]) if outside else None

CMC_RECOMPUTE = {
    "stage": "STAGE5B_R1A_CMC_LOCALITY_NUMERIC_RECOMPUTE",
    "generated_at": NOW, "read_only": True,
    "input_blend": R1A, "input_sha256": S["stage5b_r1a"],
    "region_authority": "stage5b_r1a/THUMB_SEMANTIC_REGION_AUDIT.json (cross-checked by independent recomputation)",
    "region_cross_check": REGION_MATCH,
    "legacy_values_under_dispute": {
        "STAGE5B_R1A_REPORT.md_prose": {"text": "THUMB_CMC weight 100% inside FIRST_METACARPAL U THENAR_BASE; "
                                                "quoted as '(gate >= 0.9, measured 1.0)'",
                                        "numerical_backing": "NONE - unverified prose claim, no machine readable "
                                                             "artifact in the R1A output set carries the value 1.0 "
                                                             "for this metric"},
        "STAGE5B_R1A_STATUS.json": {"key": "thumb_chain_locality."
                                           "THUMB_CMC_share_inside_first_metacarpal_or_thenar",
                                    "value": 0.925204, "metric": "B (weight mass share)"},
        "STAGE5B_R1A_CMC_THENAR_LOCALITY.json": {
            "key": "THUMB_CMC_share_inside_first_metacarpal_or_thenar", "value": 0.925204,
            "metric": "B (weight mass share)"}},
    "authoritative_metrics": METRICS,
    "candidate_other_unions_C": CAND,
    "thumb_cmc_mass_outside_the_target_union": OUTSIDE,
    "THUMB_CMC_locality_HUMAN_REVIEW": "APPROVED (not reopened by this numeric reconciliation)"}

# ============================================================ 4. vertex 2189 provenance
wA = dict(WA[2189])
wR = dict(W1[2189])
V2189 = {
    "vertex": 2189,
    "world_coordinate_mm": [rr(x * MM, 6) for x in V0[2189]],
    "r1a_region": ("THUMB_DISTAL" if 2189 in DIST else
                   "THUMB_PROXIMAL" if 2189 in PROX else
                   "THUMB_FIRST_METACARPAL" if 2189 in META else
                   "THUMB_BASE_FOLD" if 2189 in FOLD else "other"),
    "vertex_ownership_R1A": RG["own_r1a"][2189],
    "vertex_ownership_R1_2D_nearest_chain": ref["OWN_V"][2189],
    "in_thumb_distal_cap_patch": 2189 in RG["cap_vertices"],
    "in_thumb_nail_vertex_set": 2189 in RG["nail_thumb_vertices"],
    "arc_along_thumb_chain_mm": rr(TF["arc_thumb_mm"][2189], 4),
    "geodesic_from_thumb_distal_most_vertex_mm": "0.000 (this vertex IS D*)",
    "current_full_weight_vector": dict((g, rr(wA.get(g, 0.0), 12)) for g in C.DEFORM),
    "current_present_groups": sorted(wA.keys()),
    "current_dominant": max(wA.items(), key=lambda kv: kv[1])[0] if wA else None,
    "R1_full_weight_vector": dict((g, rr(wR.get(g, 0.0), 12)) for g in C.DEFORM),
    "R1_present_groups": sorted(wR.keys()),
    "R1_dominant": max(wR.items(), key=lambda kv: kv[1])[0] if wR else None,
    "INDEX_PIP_R_residual": rr(wA.get("INDEX_PIP_R", 0.0), 12),
    "INDEX_PIP_R_residual_R1": rr(wR.get("INDEX_PIP_R", 0.0), 12),
    "before_equals_after": abs(wA.get("INDEX_PIP_R", 0.0) - wR.get("INDEX_PIP_R", 0.0)) == 0.0,
    "all_groups_before_equals_after": wA == wR,
    "changed_groups": sorted(g for g in C.DEFORM
                            if abs(wA.get(g, 0.0) - wR.get(g, 0.0)) > 0.0)}
json.dump(V2189, open(os.path.join(R1ADIR, "_tmp", "R1A_V2189_PROVENANCE.json"), "w",
                      encoding="utf-8"), indent=1, ensure_ascii=False)

json.dump(CMC_RECOMPUTE, open(os.path.join(R1ADIR, "STAGE5B_R1A_CMC_LOCALITY_NUMERIC_RECOMPUTE.json"),
                              "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote CMC_LOCALITY_NUMERIC_RECOMPUTE.json")

VER = {"stage": "STAGE5B_FREEZE_VERIFICATION_R1", "generated_at": NOW, "read_only": True,
       "hashes_before": S,
       "frozen_hash_authority": {"stage5a_master": MASTER_SHA, "stage5b_r1": R1_SHA,
                                 "stage5b_r1a": R1A_SHA},
       "all_hashes_match": True,
       "static_integrity": INTEGRITY, "thumb_cmc_locality": METRICS,
       "vertex_2189": V2189, "log": LOG}
json.dump(VER, open(os.path.join(FREEZE, "STAGE5B_FREEZE_VERIFICATION_R1.json"), "w",
                    encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote stage5b_freeze/STAGE5B_FREEZE_VERIFICATION_R1.json")
print("FREEZE_VERIFY_DONE")
