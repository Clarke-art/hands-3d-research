# =====================================================================================
# STAGE6A_R1A -- consolidation, cross-check and freeze verification
# =====================================================================================
# Reads the round's JSON outputs (no Blender needed) and
#   * verifies every frozen input hash BEFORE / AFTER the round,
#   * cross-checks that the candidate-sweep PREDICTION equals the measured R1A requalification,
#   * emits the consolidated Human Review summary.
# =====================================================================================
import os
import sys
import json
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE6A_R1A = os.path.abspath(os.path.join(HERE, ".."))
STAGE6D = os.path.dirname(STAGE6A_R1A)
PROD = os.path.dirname(STAGE6D)
S5 = os.path.join(PROD, "stage5_production_rig")
R1A_MASTER = os.path.join(S5, "stage5b_r1a", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")
R1B_MASTER = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
R1_HARNESS = os.path.join(STAGE6D, "stage6a",
                          "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend")
R1A_HARNESS = os.path.join(STAGE6A_R1A, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend")
S5A_MASTER = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
S5A_FREEZE = os.path.join(S5, "stage5a_freeze")

EXPECT = {
    "stage5b_r1a_master": (R1A_MASTER,
                           "c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6"),
    "stage6a_r1_harness": (R1_HARNESS,
                           "8f223c979362a8c3414b58e2467c7cda2da60f993245cc95b2a38d76c718d3ef"),
}
S5A_EXPECT = ("stage5a_r2a",
              "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845")
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[S6A-R1A-CONS]", s, flush=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def jload(*parts):
    return json.load(open(os.path.join(*parts), encoding="utf-8"))


# ---------------------------------------------------------------- 1. freeze verification
verify = {}
for name, (path, want) in EXPECT.items():
    got = sha(path)
    verify[name] = {"path": path.replace(os.sep, "/"), "expected": want, "actual": got,
                    "unchanged": got == want}
s5a = sha(S5A_MASTER)
verify["stage5a_skeleton_master"] = {"path": S5A_MASTER.replace(os.sep, "/"),
                                     "expected": S5A_EXPECT[1], "actual": s5a,
                                     "unchanged": s5a == S5A_EXPECT[1]}
freeze_files = sorted(os.listdir(S5A_FREEZE)) if os.path.isdir(S5A_FREEZE) else []
verify["stage5a_freeze_dir_contents"] = {"files": freeze_files,
                                         "file_count": len(freeze_files)}
for k, v in verify.items():
    if "unchanged" in v:
        log("FREEZE %-26s %s" % (k, "UNCHANGED" if v["unchanged"] else "DRIFT"))
if not all(v.get("unchanged", True) for v in verify.values()):
    raise SystemExit("FAIL CLOSED: a frozen input drifted during this round")

r1b_status = jload(S5, "stage5b_r1b", "STAGE5B_R1B_STATUS.json")
r1b_sha = r1b_status["output_r1b"]["sha256"]
r1b_now = sha(R1B_MASTER)
r1a_h_sha = sha(R1A_HARNESS)
log("R1B candidate     = %s (%s)" % (r1b_sha, "OK" if r1b_now == r1b_sha else "DRIFT"))
log("Stage6A R1A harness = %s" % r1a_h_sha)
if r1b_now != r1b_sha:
    raise SystemExit("FAIL CLOSED: R1B candidate hash drifted")

# ---------------------------------------------------------------- 2. cross-check
rank = jload(STAGE6A_R1A, "STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json")
pred = rank["accepted_candidate"]["cases"]
strain_a = jload(STAGE6A_R1A, "STAGE6A_R1A_LOCAL_STRAIN_AUDIT.json")["cases"]
si_a = jload(STAGE6A_R1A, "STAGE6A_R1A_SELF_INTERSECTION_AUDIT.json")["cases"]
strain_1 = jload(STAGE6D, "stage6a", "STAGE6A_LOCAL_STRAIN_AUDIT.json")["cases"]
si_1 = jload(STAGE6D, "stage6a", "STAGE6A_SELF_INTERSECTION_AUDIT.json")["cases"]
nail_1 = jload(STAGE6D, "stage6a", "STAGE6A_NAIL_DEFORM_AUDIT.json")["cases"]
nail_a = jload(STAGE6A_R1A, "STAGE6A_R1A_NAIL_DEFORM_AUDIT.json")["cases"]
dist_1 = jload(STAGE6D, "stage6a", "STAGE6A_THUMB_DISTAL_AUDIT.json")["cases"]
dist_a = jload(STAGE6A_R1A, "STAGE6A_R1A_THUMB_DISTAL_AUDIT.json")["cases"]
versus = jload(STAGE6A_R1A, "STAGE6A_R1A_VERSUS_STAGE6A_R1.json")
status_a = jload(STAGE6A_R1A, "STAGE6A_R1A_STATUS.json")

xcheck = {}
mismatch = 0
for cid in sorted(pred):
    for key, src in (("min_face_area_ratio", "face_area_ratio"),
                     ("face_area_p05", "face_area_p05"),
                     ("max_edge_stretch", "edge_length_ratio")):
        if key == "min_face_area_ratio":
            meas = strain_a[cid]["face_area_ratio"]["min"]
        elif key == "face_area_p05":
            meas = strain_a[cid]["face_area_ratio"]["dist"]["p05"]
        else:
            meas = strain_a[cid]["edge_length_ratio"]["max"]
        pred_v = pred[cid][key]
        ok = abs(pred_v - meas) <= 2e-6
        if not ok:
            mismatch += 1
        xcheck.setdefault(cid, {})[key] = {"sweep_prediction": pred_v,
                                           "r1a_measured": meas, "match": bool(ok)}
    pm = pred[cid]["intra_thumb_self_intersection_count"]
    mm = si_a[cid]["intra_target_digit_pairs"]
    ok = pm == mm
    if not ok:
        mismatch += 1
    xcheck[cid]["intra_thumb_pairs"] = {"sweep_prediction": pm, "r1a_measured": mm,
                                       "match": bool(ok)}
log("sweep-prediction vs measured R1A requalification: %s"
    % ("EXACT" if mismatch == 0 else "%d MISMATCHES" % mismatch))
if mismatch:
    raise SystemExit("FAIL CLOSED: the promoted candidate does not reproduce under the "
                     "independent Stage6A R1A requalification")

# ---------------------------------------------------------------- 3. consolidated table
CASES = ["TH_IP_30", "TH_IP_45", "TH_MCP_45", "TH_MCP_30", "TH_MCP_15", "TH_IP_15"]
table = {}
for cid in CASES:
    b, a = strain_1[cid], strain_a[cid]
    table[cid] = {
        "min_face_area_ratio": {"R1": b["face_area_ratio"]["min"],
                                "R1A": a["face_area_ratio"]["min"]},
        "face_area_p05": {"R1": b["face_area_ratio"]["dist"]["p05"],
                          "R1A": a["face_area_ratio"]["dist"]["p05"]},
        "face_area_median": {"R1": b["face_area_ratio"]["dist"]["median"],
                             "R1A": a["face_area_ratio"]["dist"]["median"]},
        "min_edge_ratio": {"R1": b["edge_length_ratio"]["min"],
                           "R1A": a["edge_length_ratio"]["min"]},
        "max_edge_stretch": {"R1": b["edge_length_ratio"]["max"],
                             "R1A": a["edge_length_ratio"]["max"]},
        "local_surface_area_ratio": {"R1": b["local_surface_area_ratio"],
                                     "R1A": a["local_surface_area_ratio"]},
        "intra_thumb_pairs": {"R1": si_1[cid]["intra_target_digit_pairs"],
                              "R1A": si_a[cid]["intra_target_digit_pairs"]},
        "new_self_intersection_pairs_total": {"R1": si_1[cid]["new_pairs"],
                                              "R1A": si_a[cid]["new_pairs"]},
        "nail_area_ratio": {"R1": nail_1[cid]["nail_area_ratio"],
                            "R1A": nail_a[cid]["nail_area_ratio"]},
        "distal_cap_area_ratio": {"R1": dist_1[cid]["cap_area_ratio"],
                                  "R1A": dist_a[cid]["cap_area_ratio"]},
    }

nail_max_delta = max(abs(table[c]["nail_area_ratio"]["R1A"] - table[c]["nail_area_ratio"]["R1"])
                     for c in CASES)
cap_max_delta = max(abs(table[c]["distal_cap_area_ratio"]["R1A"]
                        - table[c]["distal_cap_area_ratio"]["R1"]) for c in CASES)
ff = versus["four_finger_regression"]

# ---------------------------------------------------------------- thumb transition profile
# closed-form replication of the promoted field (no Blender needed): the numbers below are the
# exact longitudinal profile that R1B now encodes.
auth = jload(STAGE6A_R1A, "STAGE6A_R1A_THUMB_TRANSITION_ROOT_CAUSE.json")["authorities"]
MED = auth["med_edge_mm"]
S_MCP = auth["joint_arcs_mm"]["MCP"]
S_IP = auth["joint_arcs_mm"]["IP"]
S_TIP = auth["joint_arcs_mm"]["TIP"]
P = rank["accepted_candidate"]["params"]
W_IP = P["W_IP"] * MED
W_BASE = P["W_BASE"] * MED


def quintic(z):
    z = max(0.0, min(1.0, z))
    return z * z * z * (z * (z * 6.0 - 15.0) + 10.0)


def smoothstep(z):
    z = max(0.0, min(1.0, z))
    return z * z * (3.0 - 2.0 * z)


def profile(s):
    u = quintic(0.5 + (s - S_IP) / (2.0 * W_IP))          # IP share
    vb = 1.0 - smoothstep(0.5 + (s - S_MCP) / (2.0 * W_BASE))   # base (CMC+WRIST) share
    if u + vb > 1.0:
        k = 1.0 / (u + vb)
        u *= k
        vb *= k
    return {"IP": round(u, 4), "MCP": round(max(0.0, 1.0 - u - vb), 4), "BASE": round(vb, 4)}


def profile_R1A(s):
    t_ip = smoothstep((s - S_IP) / MED)
    t_mcp = smoothstep((s - S_MCP) / MED)
    return {"IP": round(t_ip, 4), "MCP": round(t_mcp - t_ip, 4), "BASE": round(1.0 - t_mcp, 4)}


PROFILE_ARC = [S_MCP - 15, S_MCP - 7, S_MCP, S_MCP + 7, S_MCP + 15,
               (S_MCP + S_IP) / 2.0, S_IP - 7, S_IP, S_IP + 7, S_IP + 15, S_TIP]
TRANSITION = {
    "form": "joint-centred (straddles the joint: half the blend proximal, half distal)",
    "R1A_form": "one-sided (ramp starts exactly AT the joint arc)",
    "params": P, "MED_mm": MED,
    "W_IP_half_width_mm": round(W_IP, 4), "W_IP_full_span_mm": round(2 * W_IP, 4),
    "W_BASE_half_width_mm": round(W_BASE, 4), "W_BASE_full_span_mm": round(2 * W_BASE, 4),
    "R1A_full_span_mm": round(2 * MED, 4),
    "R1A_empirical_span_mm": 3.886146,
    "IP_band_arc_window_mm": [round(S_IP - W_IP, 3), round(S_IP + W_IP, 3)],
    "MCP_band_arc_window_mm": [round(S_MCP - W_BASE, 3), round(S_MCP + W_BASE, 3)],
    "profile_R1A": {str(round(s, 1)): profile_R1A(s) for s in PROFILE_ARC},
    "profile_R1B": {str(round(s, 1)): profile(s) for s in PROFILE_ARC},
    "trade_off_note": ("the wider joint-centred band is exactly what removes the one-edge weight "
                       "gradient; its visible cost is a softer (longer) bend at the IP, which is "
                       "the trade-off Human Review must judge on the renders"),
}

SUMMARY = {
    "stage": "STAGE6A_R1A_CONSOLIDATED_SUMMARY",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "round": "STAGE5B_R1B_THUMB_MCP_IP_NARROW_WEIGHT_REPAIR + "
             "STAGE6A_R1A_ISOLATED_FLEX_REQUALIFICATION",
    "1_root_cause": {
        "classification": "A_WEIGHT_TRANSITION",
        "axis": ("the R1A thumb weight field used a ONE-SIDED ramp that is exactly zero AT the "
                 "joint arc: A_IP = S((s - s_IP)/1*MED), so 100% of the IP/MCP blend had to be "
                 "resolved inside a single mesh edge"),
        "empirical_transition_span_R1": 3.886146,
        "nominal_span_R1": 7.77641,
        "med_edge_mm": 3.888205,
        "evidence_file": "STAGE6A_R1A_THUMB_TRANSITION_ROOT_CAUSE.json",
        "rejected_causes": {
            "B_topology_density": "topology is a uniform 100% quad mesh; the joint band "
                                  "resolves into 5 longitudinal rings - sufficient if the "
                                  "blend is spread over them",
            "C_pose_collision": "the intra-thumb worst faces sit 0-1 rings apart, i.e. the same "
                                "crease, not distant surface self-contact",
            "D_metric_artefact": "the worst face baseline area equals the patch median "
                                 "(1.616e-05 vs 1.544e-05 m2), so the ratio is not amplified by "
                                 "a tiny denominator",
        },
    },
    "2_modified_vertex_count": r1b_status["changed_vertex_count"],
    "3_authorised_region": {
        "definition": ("UNION(THUMB_MCP local deformation patch, THUMB_IP local deformation "
                       "patch) + up to 2 topology rings, thumb-owned only, MINUS approved "
                       "distal-cap vertices, nail semantic vertices and sanctioned first-web "
                       "vertices"),
        "vertex_count": r1b_status["authorised_region_vertex_count"],
        "core_patch_union": 202, "two_ring_closure": 411, "frozen_excluded": 88,
        "arc_range_mm": [24.5128, 87.3134],
        "reassigned_groups": r1b_status["reassigned_groups"],
        "rings_extension_used": 2,
        "authorised_but_unchanged": 4,
    },
    "4_to_6_thumb_case_numbers": table,
    "thumb_transition_field": TRANSITION,
    "7_intra_thumb_intersection": {c: table[c]["intra_thumb_pairs"] for c in CASES},
    "8_distal_cap": {"max_area_ratio_delta_vs_R1": cap_max_delta,
                     "DISTAL_CAP": versus["DISTAL_CAP_NO_REGRESSION"],
                     "per_case": {c: table[c]["distal_cap_area_ratio"] for c in CASES}},
    "9_nail": {"max_area_ratio_delta_vs_R1": nail_max_delta,
               "NAIL_DEFORMATION": versus["NAIL_DEFORMATION_NO_REGRESSION"],
               "per_case": {c: table[c]["nail_area_ratio"] for c in CASES}},
    "10_first_web_drift": {"max_sanctioned_displacement_delta_mm":
                           versus["first_web_max_sanctioned_displacement_delta_mm"],
                           "FIRST_WEB": versus["FIRST_WEB_NO_REGRESSION"]},
    "11_four_finger_drift": {"cases_compared": ff["cases_compared"],
                             "max_target_displacement_delta_mm":
                                 ff["max_target_displacement_delta_mm"],
                             "max_non_target_clean_delta_mm":
                                 ff["max_non_target_clean_delta_mm"],
                             "hard_blocker_mismatches": ff["hard_blocker_mismatches"],
                             "FOUR_FINGER_REGRESSION": ff["FOUR_FINGER_REGRESSION"]},
    "12_zero_restore": {"ZERO_RESTORE": status_a["gates"]["ZERO_RESTORE"],
                        "max_restore_delta_mm":
                            status_a["versus_stage6a_r1"] and
                            jload(STAGE6A_R1A, "STAGE6A_R1A_ZERO_RESTORE_AUDIT.json")
                            ["max_restore_delta_mm"],
                        "hard_gate_mm": 1e-4, "noise_floor_mm": 5.967e-05},
    "13_stage5b_r1a_hash_before_after": {
        "sha256": verify["stage5b_r1a_master"]["actual"],
        "unchanged": verify["stage5b_r1a_master"]["unchanged"],
        "role": "FROZEN_PROVENANCE (still the Stage5B FINAL_APPROVED master)"},
    "14_stage5b_r1b_candidate": {"path": R1B_MASTER.replace(os.sep, "/"),
                                 "sha256": r1b_now,
                                 "status": r1b_status["status"],
                                 "post_save_self_proof":
                                     r1b_status.get("post_save_self_proof")},
    "15_stage6a_r1a_harness": {"path": R1A_HARNESS.replace(os.sep, "/"),
                               "sha256": r1a_h_sha,
                               "final_pose": "ZERO / RSSF",
                               "input_master": "Stage5B R1B candidate"},
    "16_human_review_renders": sorted(
        f for f in os.listdir(os.path.join(STAGE6A_R1A, "renders")) if f.endswith(".png")),
    "17_STAGE5B_R1B": r1b_status["status"],
    "18_STAGE6A_R1A": "READY_FOR_HUMAN_REVIEW",
    "19_STAGE6B": "NOT_STARTED",
    "gates": status_a["gates"],
    "all_gates_pass": status_a["all_gates_pass"],
    "blockers": status_a["blockers"],
    "DEFORMATION_FINAL": "NOT_SET_PENDING_HUMAN_REVIEW",
    "frozen_input_verification": verify,
    "sweep_prediction_vs_requalification": {"mismatch_count": mismatch,
                                            "verdict": "EXACT" if mismatch == 0 else "MISMATCH",
                                            "per_case": xcheck},
    "residual_open_items": [{
        "item": "TH_MCP_45 min_edge_ratio",
        "R1": table["TH_MCP_45"]["min_edge_ratio"]["R1"],
        "R1A": table["TH_MCP_45"]["min_edge_ratio"]["R1A"],
        "note": ("the ONLY metric anywhere in the six thumb cases that is worse than Stage6A R1. "
                 "No candidate in the swept family avoided it (0 / 375 kept min_edge_ratio "
                 "non-regressed on every restricted case).  It is a palmar-side inner-surface "
                 "compression at 45 deg isolated MCP flex; secondary to the repaired face-area "
                 "collapse, and explicitly handed to Human Review."),
    }],
    "log": LOG,
}
json.dump(SUMMARY, open(os.path.join(STAGE6A_R1A, "STAGE6A_R1A_CONSOLIDATED_SUMMARY.json"),
                        "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE6A_R1A_CONSOLIDATED_SUMMARY.json")

print("=" * 100)
print("%-10s %-22s %-12s %-12s" % ("case", "metric", "Stage6A R1", "R1A"))
for cid in CASES:
    for k in ("min_face_area_ratio", "face_area_p05", "max_edge_stretch", "min_edge_ratio",
              "intra_thumb_pairs"):
        v = table[cid][k]
        print("%-10s %-22s %-12s %-12s" % (cid, k, v["R1"], v["R1A"]))
print("=" * 100)
print("CONSOLIDATE_DONE")
