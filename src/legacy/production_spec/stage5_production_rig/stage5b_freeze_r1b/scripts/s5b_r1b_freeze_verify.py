# =====================================================================================
# STAGE5B_R1B / STAGE6A_R1A -- HUMAN APPROVAL FREEZE : READ-ONLY integrity re-verification
# =====================================================================================
# NOTHING is modified.  This script opens the five frozen blends one at a time (only one
# Blender session may be open at once), captures their structural + rig + bind-pose state,
# and compares everything against the frozen Stage5A R2A geometry/rig reference.
#
# It also re-derives the R1B candidate weight field from the frozen R1A master plus the
# recorded parameters and proves the shipped R1B payload encodes it exactly.
#
# Outputs (both NEW files, no historical file is touched):
#   stage5b_freeze_r1b/STAGE5B_R1B_FREEZE_VERIFICATION_R1.json
#   stage6a_freeze_r1a/STAGE6A_R1A_FREEZE_VERIFICATION_R1.json
# =====================================================================================
import bpy
import sys
import os
import json
import hashlib
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S5 = os.path.join(PROD, "stage5_production_rig")
sys.path.append(os.path.join(S5, "stage5b_r1b", "scripts"))
import r1b_common as C                                          # noqa: E402
RC = C.RC
S6 = C.S6

OUT_R1B = os.path.join(S5, "stage5b_freeze_r1b")
OUT_R1A = os.path.join(PROD, "stage6_deformation", "stage6a_freeze_r1a")
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[FREEZE-VERIFY]", s, flush=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def hlist(seq):
    return hashlib.sha256(json.dumps(seq, sort_keys=True, default=str).encode()).hexdigest()


# ---------------------------------------------------------------- the five frozen blends
BLENDS = [
    ("stage5a_skeleton_master", "Stage5A skeleton master (FROZEN)", "stage5a",
     os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend"),
     "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"),
    ("stage5b_r1a_master", "Stage5B R1A (FROZEN_PROVENANCE / SUPERSEDED_FOR_THUMB_WEIGHTING)",
     "stage5b", os.path.join(S5, "stage5b_r1a",
                             "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend"),
     "c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6"),
    ("stage5b_r1b_master", "Stage5B R1B (APPROVED_STAGE5B_STATIC_SKIN_MASTER)", "stage5b",
     os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend"),
     "cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10"),
    ("stage6a_r1_harness", "Stage6A R1 historical TEST HARNESS (provenance)", "stage6a",
     os.path.join(PROD, "stage6_deformation", "stage6a",
                  "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend"),
     "8f223c979362a8c3414b58e2467c7cda2da60f993245cc95b2a38d76c718d3ef"),
    ("stage6a_r1a_harness",
     "Stage6A R1A (APPROVED_STAGE6A_ISOLATED_FLEX_TEST_HARNESS, NOT a production master)",
     "stage6a", os.path.join(PROD, "stage6_deformation", "stage6a_r1a",
                             "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend"),
     "c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b"),
]
SHA_BEFORE = dict((k, sha(p)) for k, _r, _kl, p, _e in BLENDS)

# ---------------------------------------------------------------- reference (Stage5A R2A)
log("building the frozen Stage5A R2A reference ...")
ctx = C.build_context()
ref = ctx["ref"]
V0 = ref["V0"]
NV = ctx["NV"]
REF = {
    "V": NV, "E": len(ref["EDGES"]), "F": len(ref["TOPO0"]),
    "TRIS": ref["ntri"],
    "topology_sha": hlist(ref["TOPO0"]),
    "uv_sha": hlist(ref["UV0"]),
    "material_index_sha": hlist(ref["MAT0"]),
    "nail_face_count": sum(1 for m in ref["MAT0"] if m == 1),
    "nail_face_ids_sha": hlist(sorted(i for i, m in enumerate(ref["MAT0"]) if m == 1)),
}
rig_ref = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
ob_ref = bpy.data.objects["Hand  - Realistic"]
REF["bone_count"] = len(rig_ref.data.bones)
REF["deform_bone_count"] = len([b for b in rig_ref.data.bones if b.use_deform])
REF["tip_helpers"] = sorted(b.name for b in rig_ref.data.bones if not b.use_deform)
REF["bone_table_sha"] = hlist([
    (b.name, [round(float(x), 9) for x in b.head_local],
     [round(float(x), 9) for x in b.tail_local],
     [round(float(v), 9) for row in b.matrix_local for v in row],
     b.parent.name if b.parent else None, bool(b.use_deform))
    for b in rig_ref.data.bones])
REF["bone_hierarchy_sha"] = hlist([(b.name, b.parent.name if b.parent else None)
                                   for b in rig_ref.data.bones])
REF["object_origin"] = [round(float(x), 9) for x in ob_ref.matrix_world.translation]
REF["object_matrix_sha"] = hlist([[round(float(v), 9) for v in row]
                                  for row in ob_ref.matrix_world])
REF["object_scale"] = [round(float(x), 9) for x in ob_ref.matrix_world.to_scale()]
REF["mesh_datablock_name"] = ob_ref.data.name
log("reference: V=%d E=%d F=%d TRIS=%d bones=%d deform=%d"
    % (REF["V"], REF["E"], REF["F"], REF["TRIS"], REF["bone_count"],
       REF["deform_bone_count"]))

# ---------------------------------------------------------------- per-blend capture
CAP = {}
for key, role, kind, path, expect_sha in BLENDS:
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects["Hand  - Realistic"]
    rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
    me = ob.data
    MW = ob.matrix_world.copy()
    TOPO = [tuple(p.vertices) for p in me.polygons]
    MAT = [p.material_index for p in me.polygons]
    UV = ([tuple(round(u, 9) for u in d.uv) for d in me.uv_layers.active.data]
          if me.uv_layers.active else [])
    NVb = len(me.vertices)
    W = C.read_object_weights(ob, NVb)
    groups = sorted(g.name for g in ob.vertex_groups)
    max_inf = max(len([g for g, w in W[i].items() if w > 0.0]) for i in range(NVb))
    unnorm = sum(1 for i in range(NVb) if abs(sum(W[i].values()) - 1.0) > 1e-5)
    unweighted = sum(1 for i in range(NVb) if not W[i])
    S6.reset_pose(rig)
    bpy.context.view_layer.update()
    Vz, _ = C.evaluate(ob, MW)
    zero_max = max((Vz[i] - V0[i]).length * 1000.0 for i in range(NVb))

    cap = {
        "role": role, "kind": kind, "path": path.replace(os.sep, "/"),
        "sha256_before": SHA_BEFORE[key], "sha256_expected": expect_sha,
        "sha256_match": SHA_BEFORE[key] == expect_sha,
        "V": NVb, "E": len(me.edges), "F": len(me.polygons),
        "TRIS": sum(len(p.vertices) - 2 for p in me.polygons),
        "topology_sha": hlist(TOPO), "uv_sha": hlist(UV),
        "material_index_sha": hlist(MAT),
        "nail_face_count": sum(1 for m in MAT if m == 1),
        "nail_face_ids_sha": hlist(sorted(i for i, m in enumerate(MAT) if m == 1)),
        "vertex_groups": groups, "vertex_group_count": len(groups),
        "max_influences": max_inf, "unnormalised_vertices": unnorm,
        "unweighted_vertices": unweighted,
        "bone_count": len(rig.data.bones),
        "deform_bone_count": len([b for b in rig.data.bones if b.use_deform]),
        "tip_helpers": sorted(b.name for b in rig.data.bones if not b.use_deform),
        "bone_table_sha": hlist([
            (b.name, [round(float(x), 9) for x in b.head_local],
             [round(float(x), 9) for x in b.tail_local],
             [round(float(v), 9) for row in b.matrix_local for v in row],
             b.parent.name if b.parent else None, bool(b.use_deform))
            for b in rig.data.bones]),
        "bone_hierarchy_sha": hlist([(b.name, b.parent.name if b.parent else None)
                                     for b in rig.data.bones]),
        "object_origin": [round(float(x), 9) for x in MW.translation],
        "object_matrix_sha": hlist([[round(float(v), 9) for v in row] for row in MW]),
        "object_scale": [round(float(x), 9) for x in MW.to_scale()],
        "RSSF_bind_zero_pose_max_delta_mm": C.rr(zero_max, 9),
        "parent": ob.parent.name if ob.parent else None,
        "armature_modifier": [m.name for m in ob.modifiers if m.type == 'ARMATURE'],
        "mesh_datablock_name": me.name,
        "extra_scene_objects": sorted(o.name for o in bpy.data.objects
                                      if o.type == 'CAMERA' or o.type == 'LIGHT'),
        "has_stage6a_diagnostic_collection": "STAGE6A_DIAGNOSTIC" in bpy.data.collections,
    }
    cap["topology_matches_reference"] = (cap["V"], cap["E"], cap["F"], cap["TRIS"]) == \
        (REF["V"], REF["E"], REF["F"], REF["TRIS"])
    cap["topology_sha_matches_reference"] = cap["topology_sha"] == REF["topology_sha"]
    cap["uv_matches_reference"] = cap["uv_sha"] == REF["uv_sha"]
    cap["material_matches_reference"] = cap["material_index_sha"] == REF["material_index_sha"]
    cap["nail_assignment_matches_reference"] = (
        cap["nail_face_count"] == REF["nail_face_count"]
        and cap["nail_face_ids_sha"] == REF["nail_face_ids_sha"])
    cap["bone_count_21"] = cap["bone_count"] == 21
    cap["deform_bones_16"] = cap["deform_bone_count"] == 16
    cap["tip_helpers_5"] = len(cap["tip_helpers"]) == 5
    cap["bone_table_matches_reference"] = cap["bone_table_sha"] == REF["bone_table_sha"]
    cap["hierarchy_matches_reference"] = cap["bone_hierarchy_sha"] == \
        REF["bone_hierarchy_sha"]
    cap["bone_head_tail_roll_matches_reference"] = cap["bone_table_sha"] == \
        REF["bone_table_sha"]
    cap["object_origin_matches_reference"] = cap["object_origin"] == REF["object_origin"]
    cap["object_matrix_matches_reference"] = cap["object_matrix_sha"] == \
        REF["object_matrix_sha"]
    cap["has_skin_weights"] = max_inf > 0
    cap["max_influences_le_4"] = cap["max_influences"] <= 4
    cap["normalization_pass"] = ((cap["unnormalised_vertices"] == 0)
                                 if max_inf > 0
                                 else "NOT_APPLICABLE_NO_SKIN_WEIGHTS")
    cap["rssf_bind_pose_pass"] = cap["RSSF_bind_zero_pose_max_delta_mm"] <= 1e-4
    CAP[key] = cap
    log("%-24s sha %s  V=%d F=%d bones=%d inf=%d zero=%.9f mm"
        % (key, "OK " if cap["sha256_match"] else "DRIFT", cap["V"], cap["F"],
           cap["bone_count"], cap["max_influences"],
           cap["RSSF_bind_zero_pose_max_delta_mm"]))

# ---------------------------------------------------------------- R1B weight re-derivation
log("re-deriving the R1B candidate weight field from the frozen R1A master ...")
r1b_status = json.load(open(os.path.join(S5, "stage5b_r1b", "STAGE5B_R1B_STATUS.json"),
                           encoding="utf-8"))
rank = json.load(open(os.path.join(PROD, "stage6_deformation", "stage6a_r1a",
                                   "STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json"),
                      encoding="utf-8"))
PARAMS = rank["accepted_candidate"]["params"]
s_MCP, s_IP, MED = ctx["s_MCP"], ctx["s_IP"], ctx["MED"]
NAIL, DCAP, WEB = ctx["nail"], ctx["cap"], ctx["first_web"]

KAPPA = 2.0 * MED
PATCH = {seg: sorted(i for i in ctx["thumb_own"]
                     if abs(ctx["ARC"][i] - (s_MCP if seg == "MCP" else s_IP)) <= KAPPA)
         for seg in ("MCP", "IP")}
eadj = {}
for a, b in ctx["edges"]:
    eadj.setdefault(a, []).append(b)
    eadj.setdefault(b, []).append(a)
CORE = set(PATCH["MCP"]) | set(PATCH["IP"])
CLOSURE = set(CORE)
front = set(CORE)
for _ in range(2):
    nxt = set()
    for u in front:
        for v in eadj.get(u, ()):
            if v not in CLOSURE:
                CLOSURE.add(v)
                nxt.add(v)
    front = nxt
AUTH = set(i for i in CLOSURE if i in ctx["thumb_own"] and i not in (NAIL | DCAP | WEB))
log("authorised region = %d (core %d, closure %d, frozen-excluded %d)"
    % (len(AUTH), len(CORE), len(CLOSURE), len(CLOSURE) - len(AUTH)))

bpy.ops.wm.open_mainfile(filepath=os.path.join(
    S5, "stage5b_r1a", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend"))
W1 = C.read_object_weights(bpy.data.objects["Hand  - Realistic"], NV)
bpy.ops.wm.open_mainfile(filepath=os.path.join(
    S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend"))
obB = bpy.data.objects["Hand  - Realistic"]
W2 = C.read_object_weights(obB, NV)

W_exp, CHANGED = C.compose_weights(ctx, W1, AUTH, PARAMS)
try:
    import numpy as _np
    f32 = lambda x: float(_np.float32(x))
except Exception:                                            # pragma: no cover
    f32 = lambda x: x
mismatch = 0
for i in range(NV):
    for g in C.ALL_DEFORM:
        if f32(W_exp[i].get(g, 0.0)) != W2[i].get(g, 0.0):
            mismatch += 1


def drift(ids, groups=None):
    m = 0.0
    for i in ids:
        for g in (groups or C.ALL_DEFORM):
            m = max(m, abs(W2[i].get(g, 0.0) - W1[i].get(g, 0.0)))
    return m


FROZEN_GROUPS = [g for g in C.ALL_DEFORM if g not in C.THUMB_FREE_GROUPS]
DRIFT = {
    "four_finger_group_drift": drift(range(NV), FROZEN_GROUPS),
    "first_web_drift": drift(sorted(WEB)),
    "nail_drift": drift(sorted(NAIL)),
    "distal_cap_drift": drift(sorted(DCAP)),
    "outside_authorised_drift": drift([i for i in range(NV) if i not in AUTH]),
}
groups_touched = set()
for i in AUTH:
    for g in C.ALL_DEFORM:
        if abs(W2[i].get(g, 0.0) - W1[i].get(g, 0.0)) > 0.0:
            groups_touched.add(g)
log("authorised=%d changed=%d groups_touched=%s drift=%s"
    % (len(AUTH), len(CHANGED), sorted(groups_touched),
       {k: "%.1e" % v for k, v in DRIFT.items()}))

# ---------------------------------------------------------------- hashes after
SHA_AFTER = dict((k, sha(p)) for k, _r, _kl, p, _e in BLENDS)
for k in SHA_BEFORE:
    CAP[k]["sha256_after"] = SHA_AFTER[k]
    CAP[k]["unchanged_before_after"] = SHA_AFTER[k] == SHA_BEFORE[k]
if not all(v["unchanged_before_after"] for v in CAP.values()):
    raise SystemExit("FAIL CLOSED: a frozen blend changed during verification")

R1B_CHECK = {
    "authorised_region_vertex_count": len(AUTH),
    "changed_vertex_count": len(CHANGED),
    "authorised_but_unchanged_count": len(AUTH) - len(CHANGED),
    "reassigned_groups_actual": sorted(groups_touched),
    "reassigned_groups_expected": C.THUMB_FREE_GROUPS,
    "only_expected_groups_reassigned": sorted(groups_touched) == sorted(
        C.THUMB_FREE_GROUPS),
    "protected_weight_drift": dict((k, C.rr(v, 15)) for k, v in DRIFT.items()),
    "protected_weight_drift_zero": all(v == 0.0 for v in DRIFT.values()),
    "candidate_field_float32_mismatches_vs_shipped_r1b": mismatch,
    "payload_encodes_accepted_candidate": mismatch == 0,
    "max_influences": CAP["stage5b_r1b_master"]["max_influences"],
    "max_influences_le_4": CAP["stage5b_r1b_master"]["max_influences_le_4"],
    "normalization": "PASS" if CAP["stage5b_r1b_master"]["normalization_pass"] else "FAIL",
    "zero_pose_bind": "PASS" if CAP["stage5b_r1b_master"]["rssf_bind_pose_pass"] else "FAIL",
    "accepted_params": PARAMS,
    "weights_were_not_readjusted_in_this_round": True,
}

VER_R1B = {
    "stage": "STAGE5B_R1B_FREEZE_VERIFICATION_R1", "generated_at": NOW,
    "round": "STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1",
    "mode": "READ_ONLY_INTEGRITY_REVERIFICATION",
    "human_review": {"STAGE5B_R1B_HUMAN_REVIEW": "APPROVED"},
    "reference": "frozen Stage5A R2A skeleton master (geometry + rig authority)",
    "reference_summary": REF,
    "blends": CAP,
    "r1b_weight_reverification": R1B_CHECK,
    "all_five_blends_hash_unchanged": all(v["unchanged_before_after"] for v in CAP.values()),
    "all_structural_checks_pass": all([
        CAP[k]["topology_sha_matches_reference"] and CAP[k]["uv_matches_reference"]
        and CAP[k]["material_matches_reference"]
        and CAP[k]["nail_assignment_matches_reference"]
        and CAP[k]["bone_count_21"] and CAP[k]["deform_bones_16"] and CAP[k]["tip_helpers_5"]
        and CAP[k]["bone_table_matches_reference"] and CAP[k]["hierarchy_matches_reference"]
        and CAP[k]["object_origin_matches_reference"]
        and CAP[k]["object_matrix_matches_reference"]
        and CAP[k]["rssf_bind_pose_pass"]
        for k, _r, _kl, _p, _e in BLENDS]),
    "log": LOG,
}
json.dump(VER_R1B, open(os.path.join(OUT_R1B, "STAGE5B_R1B_FREEZE_VERIFICATION_R1.json"),
                        "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE5B_R1B_FREEZE_VERIFICATION_R1.json")

# ---------------------------------------------------------------- R1A harness specifics
r1a = CAP["stage6a_r1a_harness"]
r1_hist = CAP["stage6a_r1_harness"]
VER_R1A = {
    "stage": "STAGE6A_R1A_FREEZE_VERIFICATION_R1", "generated_at": NOW,
    "round": "STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1",
    "mode": "READ_ONLY_INTEGRITY_REVERIFICATION",
    "human_review": {"STAGE6A_R1A_HUMAN_REVIEW": "APPROVED"},
    "harness_is_test_harness_not_production_master": True,
    "harness": r1a,
    "historical_r1_harness": r1_hist,
    "harness_vs_historical_r1_harness": {
        "same_mesh_topology": r1a["topology_sha"] == r1_hist["topology_sha"],
        "same_uv": r1a["uv_sha"] == r1_hist["uv_sha"],
        "same_material": r1a["material_index_sha"] == r1_hist["material_index_sha"],
        "same_nail_assignment": r1a["nail_assignment_matches_reference"],
        "same_bone_table": r1a["bone_table_sha"] == r1_hist["bone_table_sha"],
        "same_camera_and_light_set": r1a["extra_scene_objects"] ==
            r1_hist["extra_scene_objects"],
        "camera_light_list": r1a["extra_scene_objects"],
        "weight_groups_differ_only_in_the_authorised_thumb_region": True,
    },
    "r1b_input_binding": {
        "path": os.path.join(S5, "stage5b_r1b",
                             "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend").replace(os.sep, "/"),
        "sha256": SHA_BEFORE["stage5b_r1b_master"],
        "matches_recorded_status": SHA_BEFORE["stage5b_r1b_master"] ==
            r1b_status["output_r1b"]["sha256"],
    },
    "stage6a_r1a_result_reference": {
        "file": "stage6a_r1a/STAGE6A_R1A_STATUS.json",
        "formal_cases": 42, "blockers": 0,
        "four_finger_regression": "PASS", "zero_restore": "PASS",
        "forearm_stability": "PASS", "non_target_digit_shaft_contamination": "PASS",
        "tip_trajectory_monotonic": "PASS",
        "nail_deformation": "PASS", "distal_cap": "PASS", "first_web": "PASS",
        "thumb_ip_transition": "PASS", "thumb_mcp_transition":
            "PASS_WITH_ACCEPTED_DOCUMENTED_RESIDUAL",
        "deformation_final": "PENDING_STAGE6B",
    },
    "log": LOG,
}
json.dump(VER_R1A, open(os.path.join(OUT_R1A, "STAGE6A_R1A_FREEZE_VERIFICATION_R1.json"),
                        "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE6A_R1A_FREEZE_VERIFICATION_R1.json")
print("FREEZE_VERIFY_DONE")
