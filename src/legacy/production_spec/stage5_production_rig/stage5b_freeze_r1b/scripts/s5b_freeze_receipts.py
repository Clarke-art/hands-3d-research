# =====================================================================================
# STAGE5B_R1B / STAGE6A_R1A -- HUMAN APPROVAL FREEZE receipt generator  (documentation only)
# =====================================================================================
# Pure documentation/provenance step.  It reads the round's verification + audit JSONs and
# writes the two Human Approval Freeze receipts.  It does NOT open, write or touch any .blend.
# =====================================================================================
import os
import sys
import json
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S5 = os.path.join(PROD, "stage5_production_rig")
S6D = os.path.join(PROD, "stage6_deformation")
R1B_DIR = os.path.join(S5, "stage5b_r1b")
R1A_DIR = os.path.join(S6D, "stage6a_r1a")
FREEZE_B = os.path.join(S5, "stage5b_freeze_r1b")
FREEZE_A = os.path.join(S6D, "stage6a_freeze_r1a")
NOW = datetime.datetime.now().astimezone().isoformat()


def jload(*p):
    return json.load(open(os.path.join(*p), encoding="utf-8"))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def dump(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s" % path.replace(os.sep, "/"))


V_B = jload(FREEZE_B, "STAGE5B_R1B_FREEZE_VERIFICATION_R1.json")
V_A = jload(FREEZE_A, "STAGE6A_R1A_FREEZE_VERIFICATION_R1.json")
REPRO = jload(R1B_DIR, "_tmp", "R1B_BLEND_REPRODUCIBILITY_CHECK.json")
ST_R1B = jload(R1B_DIR, "STAGE5B_R1B_STATUS.json")
ST_R1A = jload(R1A_DIR, "STAGE6A_R1A_STATUS.json")
SUM = jload(R1A_DIR, "STAGE6A_R1A_CONSOLIDATED_SUMMARY.json")

H = dict((k, v["sha256_before"]) for k, v in V_B["blends"].items())

# ---------------------------------------------------------------- frozen metric baselines
def met(cid):
    return SUM["4_to_6_thumb_case_numbers"][cid]


APPROVED_METRICS = {
    "TH_IP_30": {
        "min_face_area_ratio": [met("TH_IP_30")["min_face_area_ratio"]["R1"],
                                met("TH_IP_30")["min_face_area_ratio"]["R1A"]],
        "face_area_p05": [met("TH_IP_30")["face_area_p05"]["R1"],
                          met("TH_IP_30")["face_area_p05"]["R1A"]],
        "min_edge_ratio": [met("TH_IP_30")["min_edge_ratio"]["R1"],
                           met("TH_IP_30")["min_edge_ratio"]["R1A"]],
        "max_edge_stretch": [met("TH_IP_30")["max_edge_stretch"]["R1"],
                             met("TH_IP_30")["max_edge_stretch"]["R1A"]],
        "intra_thumb_pairs": [met("TH_IP_30")["intra_thumb_pairs"]["R1"],
                              met("TH_IP_30")["intra_thumb_pairs"]["R1A"]],
    },
    "TH_IP_45": {
        "min_face_area_ratio": [met("TH_IP_45")["min_face_area_ratio"]["R1"],
                                met("TH_IP_45")["min_face_area_ratio"]["R1A"]],
        "face_area_p05": [met("TH_IP_45")["face_area_p05"]["R1"],
                          met("TH_IP_45")["face_area_p05"]["R1A"]],
        "min_edge_ratio": [met("TH_IP_45")["min_edge_ratio"]["R1"],
                           met("TH_IP_45")["min_edge_ratio"]["R1A"]],
        "max_edge_stretch": [met("TH_IP_45")["max_edge_stretch"]["R1"],
                             met("TH_IP_45")["max_edge_stretch"]["R1A"]],
        "intra_thumb_pairs": [met("TH_IP_45")["intra_thumb_pairs"]["R1"],
                              met("TH_IP_45")["intra_thumb_pairs"]["R1A"]],
    },
    "TH_MCP_45": {
        "min_face_area_ratio": [met("TH_MCP_45")["min_face_area_ratio"]["R1"],
                                met("TH_MCP_45")["min_face_area_ratio"]["R1A"]],
        "face_area_p05": [met("TH_MCP_45")["face_area_p05"]["R1"],
                          met("TH_MCP_45")["face_area_p05"]["R1A"]],
        "min_edge_ratio": [met("TH_MCP_45")["min_edge_ratio"]["R1"],
                           met("TH_MCP_45")["min_edge_ratio"]["R1A"]],
        "max_edge_stretch": [met("TH_MCP_45")["max_edge_stretch"]["R1"],
                             met("TH_MCP_45")["max_edge_stretch"]["R1A"]],
        "intra_thumb_pairs": [met("TH_MCP_45")["intra_thumb_pairs"]["R1"],
                              met("TH_MCP_45")["intra_thumb_pairs"]["R1A"]],
    },
}
SI = {
    "intra_target_digit_pairs": [279, 259],
    "target_vs_other_digit_pairs": [404, 400],
    "pairs_depth_gt_0_5mm": [454, 450],
    "total_new_pairs": [909, 909 - (279 - 259) - (404 - 400)],
    "thumb_index_classification": "POSE_CONSTRAINT_DIAGNOSTIC",
}

STAGE6B_OBLIGATIONS = [
    "THUMB_CMC isolated opposition",
    "CMC + MCP combined opposition",
    "CMC + MCP + IP combined opposition",
    "first-web opening / closing deformation",
    "thenar volume preservation",
    "thumb distal-cap stability",
    "thumb nail deformation",
    "thumb-index contact progression",
    "pinching",
    "collapse",
    "candy-wrapper",
    "skin inversion",
    "cross-digit contamination",
    "tip trajectory / target reach",
    "restore-to-RSSF",
]

# =====================================================================================
# 1. Stage5B R1B human approval freeze
# =====================================================================================
F_B = {
    "stage": "STAGE5B_R1B_HUMAN_APPROVAL_FREEZE_R1",
    "generated_at": NOW,
    "round": "STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1",
    "mode": "DOCUMENTATION + PROVENANCE + HUMAN APPROVAL FREEZE (no production change)",
    "human_review": {
        "STAGE5B_R1B_HUMAN_REVIEW": "APPROVED",
        "STAGE6A_R1A_HUMAN_REVIEW": "APPROVED",
    },
    "zeroth_final_state": {
        "STAGE5B_R1B": "FINAL_APPROVED",
        "PRODUCTION_BINDING": "FINAL_APPROVED",
        "PRODUCTION_SKIN_WEIGHT_STATIC": "FINAL_APPROVED",
        "STAGE5B_MASTER": "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend",
        "STAGE5B_FREEZE_R1B": "PASS",
        "STAGE5B_R1A": "SUPERSEDED_BY_R1B_FOR_THUMB_WEIGHTING",
        "STAGE6A_R1A": "FINAL_APPROVED",
        "STAGE6A_ISOLATED_FLEX_DEFORMATION": "FINAL_APPROVED",
        "DEFORMATION_FINAL": "PENDING_STAGE6B",
        "STAGE6B": "READY_TO_BEGIN",
        "PRODUCTION_MASTER_GEOMETRY": "UNCHANGED",
        "PRODUCTION_RIG_SKELETON": "UNCHANGED",
    },
    "active_stage5b_master": {
        "path": "production_spec/stage5_production_rig/stage5b_r1b/"
                "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend",
        "sha256": H["stage5b_r1b_master"],
        "role": "APPROVED_STAGE5B_STATIC_SKIN_MASTER / Production Skin Weight master",
    },
    "frozen_provenance": {
        "stage5b_r1a_master": {
            "path": "production_spec/stage5_production_rig/stage5b_r1a/"
                    "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend",
            "sha256": H["stage5b_r1a_master"],
            "role": "FROZEN_PROVENANCE / SUPERSEDED_BY_STAGE5B_R1B_FOR_THUMB_WEIGHTING",
            "files_and_reports_retained_not_overwritten": True,
        },
        "stage5a_skeleton_master": {
            "path": "production_spec/stage5_production_rig/stage5a_r2a/"
                    "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend",
            "sha256": H["stage5a_skeleton_master"], "role": "FROZEN_PROVENANCE",
        },
        "stage6a_r1_harness": {
            "path": "production_spec/stage6_deformation/stage6a/"
                    "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend",
            "sha256": H["stage6a_r1_harness"], "role": "FROZEN_PROVENANCE (historical harness)",
        },
        "stage6a_r1a_harness": {
            "path": "production_spec/stage6_deformation/stage6a_r1a/"
                    "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend",
            "sha256": H["stage6a_r1a_harness"],
            "role": "APPROVED_STAGE6A_ISOLATED_FLEX_TEST_HARNESS (TEST HARNESS, not a "
                    "production master)",
        },
    },
    "read_only_integrity_reverification": {
        "file": "stage5b_freeze_r1b/STAGE5B_R1B_FREEZE_VERIFICATION_R1.json",
        "all_five_blends_hash_unchanged": V_B["all_five_blends_hash_unchanged"],
        "all_structural_checks_pass": V_B["all_structural_checks_pass"],
        "per_blend": dict((k, {
            "sha256_before": v["sha256_before"], "sha256_after": v["sha256_after"],
            "unchanged": v["unchanged_before_after"],
            "V": v["V"], "E": v["E"], "F": v["F"], "TRIS": v["TRIS"],
            "uv_matches_reference": v["uv_matches_reference"],
            "material_matches_reference": v["material_matches_reference"],
            "nail_assignment_matches_reference": v["nail_assignment_matches_reference"],
            "nail_face_count": v["nail_face_count"],
            "bone_count": v["bone_count"], "deform_bone_count": v["deform_bone_count"],
            "tip_helpers": v["tip_helpers"],
            "hierarchy_matches_reference": v["hierarchy_matches_reference"],
            "bone_head_tail_roll_matches_reference":
                v["bone_head_tail_roll_matches_reference"],
            "object_origin_matches_reference": v["object_origin_matches_reference"],
            "RSSF_bind_zero_pose_max_delta_mm": v["RSSF_bind_zero_pose_max_delta_mm"],
        }) for k, v in V_B["blends"].items()),
    },
    "r1b_weight_reverification": V_B["r1b_weight_reverification"],
    "frozen_weighting_method": {
        "authority_file": "stage6a_r1a/STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json",
        "GLOBAL_LONGITUDINAL_COORDINATE": "APPROVED_JOINT_POLYLINE_ARC_LENGTH",
        "FORBIDDEN_COORDINATE":
            "GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP (FORBIDDEN_FOR_LONGITUDINAL_"
            "WEIGHT_COORDINATE)",
        "transition_form": "JOINT_CENTERED",
        "profile": "QUINTIC",
        "W_IP": "5.0 * MED", "W_MCP": "1.0 * MED", "W_BASE": "3.0 * MED",
        "MED_mm": SUM["thumb_transition_field"]["MED_mm"],
        "W_IP_half_width_mm": SUM["thumb_transition_field"]["W_IP_half_width_mm"],
        "W_IP_full_span_mm": SUM["thumb_transition_field"]["W_IP_full_span_mm"],
        "W_BASE_half_width_mm": SUM["thumb_transition_field"]["W_BASE_half_width_mm"],
        "R1A_form": "ONE_SIDED (ramp starts exactly AT the joint arc; the principal gradient "
                    "was compressed into about one mesh edge, which is what R1B repairs)",
        "per_vertex_free_parameters": 0,
        "reassigned_groups": ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R"],
        "not_to_be_re_researched": True,
    },
    "final_th_mcp_45_min_edge_residual": {
        "classification": "ACCEPTED_NON_BLOCKING_FOR_STAGE6A",
        "TH_MCP_45_MIN_EDGE_RESIDUAL": "ACCEPTED_NON_BLOCKING_FOR_STAGE6A",
        "TH_MCP_45_min_edge_ratio": {"Stage6A_R1": 0.421283, "Stage6A_R1A": 0.219223},
        "same_case_other_metrics": {
            "min_face_area_ratio": [0.193672, 0.297893],
            "face_area_p05": [0.523736, 0.580019],
            "max_edge_stretch": [3.016385, 3.016385],
            "intra_thumb_pairs": [79, 74],
        },
        "reasons": [
            "it is the principal single residual among the six thumb cases",
            "max edge stretch is unchanged on the same case and face-area statistics improve",
            "Human Review inspected the same-camera before/after renders and reported no new "
            "unacceptable spike, collapse or teaching-shape break",
            "none of the 375 bounded weight candidates could keep min_edge_ratio "
            "non-regressed on every restricted case",
            "therefore no R1C was opened for a single min-edge number",
        ],
        "is": "ACCEPTED_DOCUMENTED_RESIDUAL",
        "is_not": ["METRIC_INVALID", "GENERAL_EXCEPTION"],
        "must_not_be_propagated_as_a_general_exemption_to_other_joints": True,
    },
    "self_intersection_authority": SI,
    "blend_reproducibility": {
        "errata": "stage5b_r1b/STAGE5B_R1B_BLEND_REPRODUCIBILITY_ERRATA.md",
        "check": "stage5b_r1b/_tmp/R1B_BLEND_REPRODUCIBILITY_CHECK.json",
        "verdict": REPRO["verdict"],
        "byte_differences": REPRO["different_output_path"]["byte_differences"],
        "total_bytes": REPRO["different_output_path"]["total_bytes"],
        "differing_bytes_inside_8byte_pointer_slots":
            REPRO["different_output_path"]["differing_bytes_inside_8byte_pointer_slots"],
    },
    "stop_point": {
        "stage6b_started": False, "stage6b": "READY_TO_BEGIN",
        "note": "STOP after freeze / errata / hash verification / provenance ledger / "
                "Stage6B binding obligations",
    },
}
dump(F_B, os.path.join(FREEZE_B, "STAGE5B_R1B_HUMAN_APPROVAL_FREEZE_R1.json"))

# =====================================================================================
# 2. Stage6A R1A human approval freeze
# =====================================================================================
F_A = {
    "stage": "STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1",
    "generated_at": NOW,
    "round": "STAGE5B_R1B_STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1",
    "mode": "DOCUMENTATION + PROVENANCE + HUMAN APPROVAL FREEZE (no production change)",
    "human_review": {"STAGE6A_R1A_HUMAN_REVIEW": "APPROVED"},
    "zeroth_final_state": {
        "STAGE6A_R1A": "FINAL_APPROVED",
        "STAGE6A_ISOLATED_FLEX_DEFORMATION": "FINAL_APPROVED",
        "THUMB_IP_TRANSITION": "PASS",
        "THUMB_MCP_TRANSITION": "PASS_WITH_ACCEPTED_DOCUMENTED_RESIDUAL",
        "FOUR_FINGER_ISOLATED_FLEX": "FINAL_APPROVED",
        "ZERO_RESTORE": "PASS",
        "FOREARM_STABILITY": "PASS",
        "NON_TARGET_DIGIT_SHAFT_CONTAMINATION": "PASS",
        "TIP_TRAJECTORY_MONOTONIC": "PASS",
        "NAIL_DEFORMATION": "PASS",
        "DISTAL_CAP": "PASS",
        "FIRST_WEB": "PASS",
        "DEFORMATION_FINAL": "PENDING_STAGE6B",
        "CMC_OPPOSITION": "NOT_STARTED",
        "COMBINED_THUMB_OPPOSITION": "NOT_STARTED",
        "STAGE6B": "READY_TO_BEGIN",
    },
    "explicitly_not_approved": {
        "DEFORMATION_FINAL": "PENDING_STAGE6B",
        "reason": "STAGE6B CMC opposition / combined opposition have not been executed; "
                  "STAGE6A_R1A approves STAGE6A_ISOLATED_FLEX_DEFORMATION only",
    },
    "approved_harness": {
        "path": "production_spec/stage6_deformation/stage6a_r1a/"
                "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend",
        "sha256": H["stage6a_r1a_harness"],
        "role": "APPROVED_STAGE6A_ISOLATED_FLEX_TEST_HARNESS",
        "is_test_harness_not_production_master": True,
        "input_master": {"path": "stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend",
                         "sha256": H["stage5b_r1b_master"]},
        "final_pose": "ZERO / RSSF",
    },
    "read_only_integrity_reverification": {
        "file": "stage6a_freeze_r1a/STAGE6A_R1A_FREEZE_VERIFICATION_R1.json",
        "harness_vs_historical_r1_harness": V_A["harness_vs_historical_r1_harness"],
    },
    "approved_numeric_baseline": APPROVED_METRICS,
    "self_intersection_authority": SI,
    "reported_metrics_summary": {
        "formal_cases": 42, "blockers": 0,
        "four_finger_regression_max_displacement_delta_mm": SUM[
            "11_four_finger_drift"]["max_target_displacement_delta_mm"],
        "zero_restore_max_delta_mm": SUM["12_zero_restore"]["max_restore_delta_mm"],
        "nail_area_ratio_delta_vs_R1": SUM["9_nail"]["max_area_ratio_delta_vs_R1"],
        "distal_cap_area_ratio_delta_vs_R1": SUM["8_distal_cap"]["max_area_ratio_delta_vs_R1"],
        "first_web_drift_mm": SUM["10_first_web_drift"][
            "max_sanctioned_displacement_delta_mm"],
    },
    "methodology_errata": {
        "metric_count_wording":
            "stage6a_r1a/STAGE6A_R1A_METRIC_COUNT_WORDING_ERRATA.md",
        "thickness_proxy_authority":
            "stage6a_r1a/STAGE6A_R1_THICKNESS_PROXY_AUTHORITY_ERRATA.md",
        "self_intersection_wording":
            "stage6a_r1a/STAGE6A_R1_SELF_INTERSECTION_WORDING_ERRATA.md",
    },
    "stage6b_binding_obligations": {
        "must_at_least_cover": STAGE6B_OBLIGATIONS,
        "functional_authority": "the real thumb opposition / teaching hand function",
        "must_not_be_substituted_by": "Stage6A isolated flex",
        "thumb_index_retest_required": "Stage6B combined opposition must re-test the real "
                                       "linked pose for thumb-index contact",
        "recorded_not_executed": True,
    },
    "stop_point": {"stage6b_started": False, "stage6b": "READY_TO_BEGIN"},
}
dump(F_A, os.path.join(FREEZE_A, "STAGE6A_R1A_HUMAN_APPROVAL_FREEZE_R1.json"))
print("RECEIPT_JSON_DONE")
