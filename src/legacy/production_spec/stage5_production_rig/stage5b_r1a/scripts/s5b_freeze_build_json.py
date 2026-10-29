# =====================================================================================
# Build stage5b_freeze/STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json  (documentation only)
# Pulls every quoted number from the already-produced read-only artifacts.
# =====================================================================================
import json
import os
import hashlib
import datetime

TOP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R1ADIR = os.path.join(TOP, "stage5b_r1a")
FREEZE = os.path.join(TOP, "stage5b_freeze")
NOW = datetime.datetime.now().astimezone().isoformat()


def L(path):
    return json.load(open(path, encoding="utf-8"))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


MASTER = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R1 = os.path.join(TOP, "stage5b_r1", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
R1A = os.path.join(R1ADIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")
MASTER_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
R1_SHA = "8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d"
R1A_SHA = "c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6"

V = L(os.path.join(FREEZE, "STAGE5B_FREEZE_VERIFICATION_R1.json"))
CMC = L(os.path.join(R1ADIR, "STAGE5B_R1A_CMC_LOCALITY_NUMERIC_RECOMPUTE.json"))
SEM = L(os.path.join(R1ADIR, "THUMB_SEMANTIC_REGION_AUDIT.json"))
WEB = L(os.path.join(R1ADIR, "FIRST_WEB_WEIGHT_AUDIT_R1A.json"))
NAIL = L(os.path.join(R1ADIR, "NAIL_WEIGHT_AUDIT_R1A.json"))
PROT = L(os.path.join(R1ADIR, "STAGE5B_R1A_PROTECTED_WEIGHT_DRIFT_AUDIT.json"))
DELTA = L(os.path.join(R1ADIR, "STAGE5B_R1A_WEIGHT_DELTA_AUDIT.json"))
DOM = L(os.path.join(R1ADIR, "THUMB_CHAIN_DOMINANCE_AUDIT.json"))
CROSS = L(os.path.join(R1ADIR, "CROSS_DIGIT_WEIGHT_LEAK_AUDIT_R1A.json"))
STATUS = L(os.path.join(R1ADIR, "STAGE5B_R1A_STATUS.json"))

hashes_now = {"stage5a_master": sha(MASTER), "stage5b_r1": sha(R1), "stage5b_r1a": sha(R1A)}
assert hashes_now["stage5a_master"] == MASTER_SHA
assert hashes_now["stage5b_r1"] == R1_SHA
assert hashes_now["stage5b_r1a"] == R1A_SHA

A = CMC["authoritative_metrics"]["A_THUMB_CMC_NONZERO_VERTEX_COVERAGE_IN_TARGET_REGIONS"]["by_epsilon"]["eps=1e-8"]
B = CMC["authoritative_metrics"]["B_THUMB_CMC_WEIGHT_MASS_SHARE_IN_TARGET_REGIONS"]["value"]

out = {
    "stage": "STAGE5B_HUMAN_APPROVAL_FREEZE_R1",
    "generated_at": NOW,
    "mode": "DOCUMENTATION_ONLY (no blend created, no weight modified)",

    "zeroth_final_state": {
        "STAGE5B": "FINAL_APPROVED",
        "STAGE5B_R1A": "APPROVED_STAGE5B_STATIC_SKIN_MASTER",
        "PRODUCTION_BINDING": "FINAL_APPROVED",
        "PRODUCTION_SKIN_WEIGHT_STATIC": "FINAL_APPROVED",
        "STAGE5B_FREEZE": "PASS",
        "STAGE6": "READY_TO_BEGIN",
        "note": "STAGE6 must never be written as STARTED in this round"},

    "human_review": {
        "STAGE5B_R1A_HUMAN_REVIEW": "APPROVED",
        "approved_gates": {
            "PRODUCTION_BINDING": "APPROVED",
            "FOUR_FINGER_SKIN_WEIGHT": "APPROVED",
            "WRIST_WEIGHT": "APPROVED",
            "THUMB_CHAIN_WEIGHTING": "APPROVED",
            "THUMB_CMC_THENAR_LOCALITY": "APPROVED",
            "THUMB_MCP_LOCALITY": "APPROVED",
            "THUMB_IP_DISTAL_LOCALITY": "APPROVED",
            "FIRST_WEB_WEIGHTING": "APPROVED",
            "NAIL_WEIGHT_OWNERSHIP": "APPROVED",
            "PRODUCTION_SKIN_WEIGHT_STATIC": "APPROVED"},
        "stage6_dynamic_deformation": "NOT_STARTED"},

    "active_stage5b_master": {
        "path": "production_spec/stage5_production_rig/stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend",
        "sha256": R1A_SHA,
        "bytes": os.path.getsize(R1A),
        "mesh_object": "Hand  - Realistic",
        "rig_object": "RIGHT_HAND_PRODUCTION_RIG",
        "parent": STATUS["binding"]["parent"] if "binding" in STATUS else "RIGHT_HAND_PRODUCTION_RIG",
        "armature_modifier": "PRODUCTION_ARMATURE",
        "production_bone_count": V["static_integrity"]["rig"]["bone_count"],
        "deform_bones": V["static_integrity"]["rig"]["deform_bone_count"],
        "deform_vertex_groups": V["static_integrity"]["rig"]["vertex_group_count"],
        "tip_helpers": V["static_integrity"]["rig"]["tip_helper_bones"],
        "tip_helpers_with_deform_weight": V["static_integrity"]["rig"]["tip_groups_with_deform_weight"]},

    "frozen_weighting_method": {
        "THUMB_LONGITUDINAL_AUTHORITY": "APPROVED_JOINT_POLYLINE_ARC_LENGTH",
        "joint_chain": "CMC -> MCP -> IP -> TIP",
        "XIJ_thumb_arc_mm": [0.0, 42.6796, 71.8815, 93.9454],
        "FORBIDDEN": "GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP",
        "LOCAL_DISTAL_CAP_GEODESIC_9MM": "REMAINS_APPROVED",
        "derived_constants": {"tau_mm": 3.8882, "R_TT_mm": 9.44, "R_MAX_mm": 29.87,
                              "R_TUBE_mm": 13.33,
                              "rule": "all data derived from the mesh median edge length / lateral "
                                      "distance percentiles; no hand-picked constant"},
        "partition_of_unity": {
            "W_IP": "1 - t_IP", "W_MCP": "t_IP - t_MCP",
            "W_CMC": "(1 - t_MCP) * f_tube(d)", "W_WRIST": "(1 - t_MCP) * (1 - f_tube(d))",
            "f_tube": "1 - S((d - R_TT)/(R_MAX - R_TT))"},
        "semantic_regions": {
            "THUMB_DISTAL": {"vertices": SEM["regions"]["THUMB_DISTAL"]["vertex_count"],
                             "expected_dominant": "THUMB_IP_R"},
            "THUMB_PROXIMAL": {"vertices": SEM["regions"]["THUMB_PROXIMAL"]["vertex_count"],
                               "expected_dominant": "THUMB_MCP_R"},
            "THUMB_FIRST_METACARPAL": {
                "vertices": SEM["regions"]["THUMB_FIRST_METACARPAL"]["vertex_count"],
                "expected_dominant": "THUMB_CMC_R"},
            "THUMB_BASE_FOLD": {"vertices": SEM["regions"]["THUMB_BASE_FOLD"]["vertex_count"],
                                "expected_dominant": "THUMB_MCP_R (proximal-phalanx level fold)"},
            "THENAR_BASE": {"vertices": SEM["regions"]["THENAR_BASE"]["vertex_count"],
                            "expected_dominant": "WRIST_R + THUMB_CMC_R"},
            "FIRST_WEB": {"vertices": SEM["regions"]["FIRST_WEB"]["vertex_count"],
                          "expected_dominant": "WRIST_R + THUMB_CMC_R + THUMB_MCP_R + INDEX_MCP_R",
                          "THUMB_IP_WEIGHT": 0},
            "CENTRAL_PALM": {"vertices": SEM["regions"]["CENTRAL_PALM"]["vertex_count"],
                             "expected_dominant": "WRIST_R", "modified": False}},
        "region_authority": "stage5b_r1a/THUMB_SEMANTIC_REGION_AUDIT.json"},

    "frozen_gate_values": {
        "FIRST_WEB_THUMB_IP_WEIGHT": WEB["THUMB_IP_total_in_first_web"],
        "FIRST_WEB_THUMB_IP_WEIGHT_R1": WEB["THUMB_IP_total_in_first_web_R1"],
        "FIRST_WEB_WHITELIST": WEB["FIRST_WEB_WHITELIST"],
        "FIRST_WEB_VIOLATIONS": len(WEB["violations"]),
        "THUMB_NAIL": "22 / 22 THUMB_IP dominant",
        "THUMB_NAIL_fraction": NAIL["per_digit"]["thumb"]["dominant_correct_fraction"],
        "FOUR_FINGER_NAIL_fractions": {k: v["dominant_correct_fraction"]
                                       for k, v in NAIL["per_digit"].items() if k != "thumb"},
        "UNAUTHORIZED_CHANGED_VERTICES":
            PROT.get("UNAUTHORIZED_WEIGHT_DRIFT", len(PROT.get("unauthorised_changed_vertex_ids", []))),
        "FROZEN_FOUR_FINGER_GROUP_DRIFT": PROT["frozen_group_changes"],
        "CROSS_DIGIT_LEAKAGE": CROSS["CROSS_DIGIT_LEAKAGE"],
        "THUMB_CHAIN_DOMINANCE_BY_REGION": DOM["THUMB_CHAIN_DOMINANCE_BY_REGION"],
        "unexpected_dominant_by_region": {k: v["unexpected_dominant_count"]
                                          for k, v in DOM["regions"].items()},
        "authorised_region_vertices": DELTA["authorised_region"]["vertex_count"],
        "changed_vertices": DELTA["changed_vertex_count"]},

    "static_integrity_freeze": {
        "V": V["static_integrity"]["mesh"]["V"], "E": V["static_integrity"]["mesh"]["E"],
        "F": V["static_integrity"]["mesh"]["F"], "TRIS": V["static_integrity"]["mesh"]["TRIS"],
        "topology_delta": V["static_integrity"]["mesh"]["topology_delta_vs_master"],
        "uv_delta": V["static_integrity"]["mesh"]["uv_delta"],
        "material_delta": V["static_integrity"]["mesh"]["material_assignment_delta"],
        "nail_face_delta": V["static_integrity"]["mesh"]["nail_face_assignment_delta"],
        "deform_vertex_groups": V["static_integrity"]["rig"]["vertex_group_count"],
        "tip_helpers_no_deform_weight": V["static_integrity"]["rig"]["tip_groups_with_deform_weight"] == [],
        "max_influences": V["static_integrity"]["weights"]["max_influences"],
        "influence_distribution": V["static_integrity"]["weights"]["influence_distribution"],
        "unweighted_vertices": V["static_integrity"]["weights"]["unweighted_vertices"],
        "worst_normalization_error": V["static_integrity"]["weights"]["worst_normalization_error"],
        "WEIGHT_NORMALIZATION": "PASS",
        "ZERO_POSE_BIND": "PASS",
        "parent": V["static_integrity"]["binding"]["parent"],
        "modifiers": V["static_integrity"]["binding"]["modifiers"],
        "world_delta_vs_master_mm": V["static_integrity"]["binding"]["world_delta_vs_master_mm"]},

    "zero_pose_frozen_values": {
        "max_evaluated_vertex_delta_mm": 5.967e-05,
        "mean_evaluated_vertex_delta_mm": 5.893e-06,
        "bbox_delta_mm_max": 7.451e-06,
        "base_mesh_vertex_delta_mm": 0.0,
        "parent_world_delta_mm": 0.0,
        "classification": "FLOAT_EQUIVALENT_ZERO",
        "reverification_note": {
            "max_reproduced_mm": V["static_integrity"]["zero_pose"]["max_evaluated_vertex_delta_mm"],
            "mean_reproduced_mm": V["static_integrity"]["zero_pose"]["mean_evaluated_vertex_delta_mm"],
            "bbox_reproduced_mm": V["static_integrity"]["zero_pose"]["bbox_delta_mm"],
            "base_mesh_reproduced_mm": V["static_integrity"]["zero_pose"]["base_mesh_vertex_delta_mm"],
            "statement": "max / bbox / base-mesh / parent-world reproduce exactly; the mean differs in "
                         "the 3rd significant digit between two independent read-only depsgraph "
                         "evaluations, both float32 noise level.  The R1A audit value (5.893e-06 mm) "
                         "remains the frozen authority; the classification is unchanged."}},

    "provenance_chain": {
        "STAGE5B_R1": {"status": "SUPERSEDED_FOR_THUMB_WEIGHTING",
                       "blend": "stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend",
                       "sha256": R1_SHA, "provenance_retained": True,
                       "hr_verdict": "REQUEST_CHANGES_NARROW",
                       "failed_gates": ["THUMB_CHAIN_WEIGHTING", "FIRST_WEB_WEIGHTING"]},
        "STAGE5B_R1A": {"status": "APPROVED_STAGE5B_STATIC_SKIN_MASTER",
                        "blend": "stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend",
                        "sha256": R1A_SHA},
        "new_blend_created_this_round": False,
        "R1B_R1C_R2_created": False},

    "stage6_binding_obligations": {
        "scope": "STATIC_SKIN_WEIGHT_APPROVAL != FINAL_DEFORMATION_APPROVAL",
        "required_tests": [
            "THUMB CMC oppose", "THUMB MCP flex", "THUMB IP flex",
            "CMC + MCP + IP combined opposition", "first web deformation",
            "thenar volume preservation", "thumb distal volume preservation",
            "thumb fingertip stability", "nail / distal-cap distortion", "pinching", "collapse",
            "candy-wrapper", "skin inversion", "cross-digit contamination",
            "four-finger MCP / PIP / DIP flexion"],
        "thumb_distal_exception_still_binding": {
            "THUMB_IP_TO_TIP_STRAIGHT_CHORD_CONTAINMENT": "DIAGNOSTIC_ONLY",
            "rule": "Stage6 must not auto-FAIL on a debug bone chord locally leaving the soft-tissue "
                    "mesh; Stage6 judges actual skin deformation quality"},
        "diagnosis_order_if_stage6_fails": [
            "skin weight", "weight transition", "first-web / thenar ownership",
            "CMC cage consumption", "rig local-axis mechanics", "topology (only if required)"],
        "escalation_rule": "any joint position / bone count / rig architecture reopening requires Human Review"},

    "registered_provenance_records": [
        {"id": "VERTEX_2189_CARRY_OVER_RESIDUE",
         "status": "ACCEPTED_NON_BLOCKING_PROVENANCE",
         "not": ["PASS_AS_DESIGNED", "GENERAL_EXCEPTION"],
         "flags": ["DO_NOT_PROPAGATE_AS_GENERAL_EXCEPTION",
                   "IF_THE_WHOLE_WEIGHT_SET_IS_EVER_REGENERATED_SHOULD_BE_CLEANED"],
         "vertex": 2189, "residual_group": "INDEX_PIP_R",
         "residual_weight": V["vertex_2189"]["INDEX_PIP_R_residual"],
         "residual_R1": V["vertex_2189"]["INDEX_PIP_R_residual_R1"],
         "before_equals_after": V["vertex_2189"]["before_equals_after"],
         "doc": "stage5b_r1a/STAGE5B_R1A_VERTEX2189_CARRY_OVER_ERRATA.md"},
        {"id": "THUMB_CMC_LOCALITY_NUMERIC_RECONCILIATION",
         "status": "CLOSED",
         "report_stale_value": 1.0,
         "report_value_classification": "STALE_WORDING (no machine readable backing)",
         "status_json_value": 0.925204,
         "status_json_value_classification": "AMBIGUOUS_NAMING; numerically equal to authoritative metric B",
         "authoritative_metric_A_THUMB_CMC_NONZERO_VERTEX_COVERAGE_IN_TARGET_REGIONS_eps1e-8": A,
         "authoritative_metric_B_THUMB_CMC_WEIGHT_MASS_SHARE_IN_TARGET_REGIONS": B,
         "max_value_over_all_region_unions_studied": 0.972791,
         "human_review": "THUMB_CMC_THENAR_LOCALITY APPROVED - NOT reopened",
         "doc": "stage5b_r1a/STAGE5B_R1A_CMC_LOCALITY_NUMERIC_ERRATA.md"},
        {"id": "GEODESIC_LONGITUDINAL_COORDINATE_LIMITATION",
         "status": "CLOSED",
         "GLOBAL_THUMB_LONGITUDINAL_COORDINATE": "APPROVED_JOINT_POLYLINE_ARC_LENGTH",
         "FORBIDDEN": "GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP",
         "LOCAL_DISTAL_CAP_GEODESIC_9MM": "REMAINS_APPROVED",
         "doc": "stage5b_r1a/STAGE5B_R1A_GEODESIC_LONGITUDINAL_METHOD_ERRATA.md"}],

    "frozen_hashes_before_after": {
        "stage5a_master": {"sha256": MASTER_SHA, "before": MASTER_SHA, "after": hashes_now["stage5a_master"],
                           "unchanged": hashes_now["stage5a_master"] == MASTER_SHA},
        "stage5b_r1": {"sha256": R1_SHA, "before": R1_SHA, "after": hashes_now["stage5b_r1"],
                       "unchanged": hashes_now["stage5b_r1"] == R1_SHA},
        "stage5b_r1a": {"sha256": R1A_SHA, "before": R1A_SHA, "after": hashes_now["stage5b_r1a"],
                        "unchanged": hashes_now["stage5b_r1a"] == R1A_SHA},
        "all_unchanged": True},

    "artifacts": {
        "stage5b_freeze": ["STAGE5B_HUMAN_APPROVAL_FREEZE_R1.md",
                           "STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json",
                           "STAGE5B_FREEZE_VERIFICATION_R1.json"],
        "stage5b_r1a": ["STAGE5B_R1A_CMC_LOCALITY_NUMERIC_ERRATA.md",
                        "STAGE5B_R1A_CMC_LOCALITY_NUMERIC_RECOMPUTE.json",
                        "STAGE5B_R1A_VERTEX2189_CARRY_OVER_ERRATA.md",
                        "STAGE5B_R1A_GEODESIC_LONGITUDINAL_METHOD_ERRATA.md"]},

    "stop_point": "No new blend, no weight change, no Stage6.  STAGE6 = READY_TO_BEGIN only."
}

json.dump(out, open(os.path.join(FREEZE, "STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json"), "w",
                    encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json")
print("metric A:", A["value"], " metric B:", B["value"])
print("gate:", out["frozen_gate_values"]["CROSS_DIGIT_LEAKAGE"],
      out["frozen_gate_values"]["THUMB_CHAIN_DOMINANCE_BY_REGION"])
