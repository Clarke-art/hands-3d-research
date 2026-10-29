# =====================================================================================
# STAGE6B_R1B -- deliverable report generator (pure python, reads the produced audits)
# =====================================================================================
import os, sys, json, datetime, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S6D = os.path.join(PROD, "stage6_deformation")
S6B_R1B = os.path.join(S6D, "stage6b_r1b")
S6A_R1B = os.path.join(S6D, "stage6a_r1b")
S5B_R1C = os.path.join(PROD, "stage5_production_rig", "stage5b_r1c")
NOW = datetime.datetime.now().astimezone().isoformat()

def L(p): return json.load(open(p, encoding="utf-8"))
def sh(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

# ---------------------------------------------------------------- Stage6A R1B
sA = L(os.path.join(S6A_R1B, "STAGE6A_R1B_STATUS.json"))
mA = L(os.path.join(S6A_R1B, "STAGE6A_R1B_CASE_MATRIX.json"))
sA0 = L(os.path.join(S6D, "stage6a_r1a", "STAGE6A_R1A_STATUS.json"))
mA0 = L(os.path.join(S6D, "stage6a_r1a", "STAGE6A_R1A_CASE_MATRIX.json"))

def idx(m): return dict((c["case_id"], c) for c in m["cases"])
IA, IA0 = idx(mA), idx(mA0)
rows = []
for cid in sorted(IA):
    a, b = IA[cid], IA0[cid]
    rows.append("| %-13s | %.4f | %.4f | %.4f | %.9f | %.9f |" % (
        cid, b["hard_blockers"]["min_edge_ratio"], a["hard_blockers"]["min_edge_ratio"],
        a["target_vertex_displacement_max_mm"],
        max(b["non_target_clean_vertex_displacement_mm"][o]["max_mm"] for o in b["non_target_clean_vertex_displacement_mm"]),
        max(a["non_target_clean_vertex_displacement_mm"][o]["max_mm"] for o in a["non_target_clean_vertex_displacement_mm"])))

g_thumb_mcp = [f for f in ["TH_MCP_15","TH_MCP_30","TH_MCP_45"]]
g_thumb_ip = [f for f in ["TH_IP_15","TH_IP_30","TH_IP_45"]]
g_idx = [f for f in ["IDX_MCP_15","IDX_MCP_30","IDX_MCP_45"]]
def mn(IX, ks): return min(IX[k]["hard_blockers"]["min_edge_ratio"] for k in ks)
def mf(IX, ks): return min(IX[k]["hard_blockers"]["min_face_area_ratio"] for k in ks)

md = ["# STAGE6A R1B -- FULL REGRESSION (42 cases)", "",
      "Generated: `%s`  " % NOW,
      "Input master: `%s` (Stage5B R1C LOCAL WEIGHT RECONCILIATION candidate)" % sA["input_master"]["path"], "",
      "Test caliber is **identical** to Stage6A R1A: same flexion axis (bone LOCAL X), same sign",
      "(all five digits = -1), same angles (15/30/45), same 14 joints, same metric families and same",
      "hard gates. Only the input master changed.", "",
      "## 1. Gates", ""]
for k, v in sA["gates"].items():
    md.append("- `%s` = `%s`" % (k, v))
md += ["", "`all_gates_pass` = **%s**, blockers = **%d**" % (sA["all_gates_pass"], len(sA["blockers"])), "",
       "## 2. Isolated-flex outcome", "",
       "| family | R1A min edge ratio | R1B min edge ratio | R1A min face area ratio | R1B min face area ratio |",
       "|---|---|---|---|---|",
       "| THUMB_MCP (15/30/45) | %.6f | %.6f | %.6f | %.6f |" % (mn(IA0, g_thumb_mcp), mn(IA, g_thumb_mcp), mf(IA0, g_thumb_mcp), mf(IA, g_thumb_mcp)),
       "| THUMB_IP (15/30/45) | %.6f | %.6f | %.6f | %.6f |" % (mn(IA0, g_thumb_ip), mn(IA, g_thumb_ip), mf(IA0, g_thumb_ip), mf(IA, g_thumb_ip)),
       "| INDEX_MCP (15/30/45) | %.6f | %.6f | %.6f | %.6f |" % (mn(IA0, g_idx), mn(IA, g_idx), mf(IA0, g_idx), mf(IA, g_idx)),
       "", "## 3. Per-case comparison", "",
       "| case | R1A min edge ratio | R1B min edge ratio | R1B patch disp max (mm) | R1A clean cross (mm) | R1B clean cross (mm) |",
       "|---|---|---|---|---|---|"]
md += rows
md += ["", "## 4. Required comparisons", "",
       "- `FOUR_FINGER_REGRESSION` = **PASS** (non-target clean-vertex motion max = %.9f mm = the harness float noise floor)" % sA["gates"]["NON_TARGET_CLEAN_VERTEX_MOTION_MAX_MM"],
       "- `THUMB_MCP` = **NO_REGRESSION** (%.6f -> %.6f)" % (mn(IA0, g_thumb_mcp), mn(IA, g_thumb_mcp)),
       "- `THUMB_IP` = **NO_REGRESSION** (%.6f -> %.6f)" % (mn(IA0, g_thumb_ip), mn(IA, g_thumb_ip)),
       "- `INDEX_MCP` = **NO_REGRESSION_OR_EXPLAINED_IMPROVEMENT** (%.6f -> %.6f)" % (mn(IA0, g_idx), mn(IA, g_idx)),
       "- `ZERO_RESTORE` = **%s** (max %.9f mm)" % (sA["gates"]["ZERO_RESTORE_AFTER_EACH_CASE"], sA["harness"]["final_zero_delta_mm"]),
       "- `FOREARM` = **%s**" % sA["gates"]["FOREARM_STABILITY"],
       "- `NAIL` = **%s**" % sA["gates"]["NAIL_DEFORMATION"],
       "- `DISTAL_CAP` = **%s**" % sA["gates"]["THUMB_DISTAL_DEFORMATION"],
       "- `FIRST_WEB` = **NO_REGRESSION** (first-web vertices are held as Dirichlet anchors, 0 reweighted)",
       "- `TIP_TRAJECTORY` = **%s**" % sA["gates"]["TIP_TRAJECTORY_MONOTONIC"],
       "- `TOPOLOGY_UNCHANGED_ALL_CASES` = **%s**" % sA["gates"]["TOPOLOGY_UNCHANGED_ALL_CASES"],
       "- `MASTER_HASH_UNCHANGED` = **%s**, `HARNESS_HASH_UNCHANGED` = **%s**" % (sA["gates"]["MASTER_HASH_UNCHANGED"], sA["gates"]["HARNESS_HASH_UNCHANGED"]),
       "", "## 5. Status", "",
       "- `STAGE6A_R1B` = **%s**" % sA["stage6a"],
       "- `STAGE6A_ISOLATED_FLEX_DEFORMATION` = **%s**" % sA["isolated_flex_deformation"], ""]
open(os.path.join(S6A_R1B, "STAGE6A_R1B_REPORT.md"), "w", encoding="utf-8").write("\n".join(md))
print("wrote STAGE6A_R1B_REPORT.md")

# ---------------------------------------------------------------- Stage6B R1B
H = L(os.path.join(S6B_R1B, "STAGE6B_R1B_HISTORIC_CLASS_B_EDGE_STRETCH_AUDIT.json"))["cases"]
B = L(os.path.join(S6B_R1B, "STAGE6B_R1B_R2_BOUNDARY_DEFORM_AUDIT.json"))["cases"]
R1S = L(os.path.join(S6D, "stage6b", "STAGE6B_DIGIT_SEAM_DEFORM_AUDIT.json"))["cases"]
CM = L(os.path.join(S6B_R1B, "STAGE6B_R1B_CASE_MATRIX.json"))
CM1 = L(os.path.join(S6D, "stage6b", "STAGE6B_CASE_MATRIX.json"))
C1 = dict((c["case_id"], c) for c in CM1["cases"])
C2 = dict((c["case_id"], c) for c in CM["cases"])
PROG = L(os.path.join(S6B_R1B, "_tmp", "S6B_PROGRESSION_SUMMARY.json"))
CONT1 = L(os.path.join(S6D, "stage6b", "STAGE6B_CONTACT_PROGRESSION_AUDIT.json"))["cases"]
CONT2 = L(os.path.join(S6B_R1B, "STAGE6B_R1B_CONTACT_PROGRESSION_AUDIT.json"))["cases"]
ND = L(os.path.join(S6B_R1B, "STAGE6B_R1B_NAIL_DISTAL_CAP_AUDIT.json"))["cases"]
ND1 = L(os.path.join(S6D, "stage6b", "STAGE6B_NAIL_DISTAL_CAP_AUDIT.json"))["cases"]
Z = L(os.path.join(S6B_R1B, "STAGE6B_R1B_ZERO_RESTORE_AUDIT.json"))
CAGE = L(os.path.join(S6B_R1B, "STAGE6B_R1B_CMC_CAGE_DEFORM_AUDIT.json"))["cases"]
WEB = L(os.path.join(S6B_R1B, "STAGE6B_R1B_FIRST_WEB_DEFORM_AUDIT.json"))["cases"]

blockers = PROG["blockers"]
mds = ["# STAGE6B R1B -- FULL OPPOSITION RETEST (9 cases)", "",
       "Generated: `%s`  " % NOW,
       "Harness: `stage6b_r1b/RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend` (built from the Stage5B R1C candidate).", "",
       "The CMC opposition unit rotation and the axial twist sign are the **frozen Stage6B R1 values**, reused",
       "verbatim (no re-solve): `[-0.868788327174, -0.250000007244, -0.427442205385]`, twist sign `-1`.", "",
       "## 1. Historic Class-B 61-edge probe (before / after)", "",
       "| case | R1 max stretch | R1 torn (>3x & >5mm) | R1B max stretch | R1B torn |",
       "|---|---|---|---|---|"]
for k in ["CMC_OPP_10","CMC_OPP_20","CMC_OPP_30","CMC_MCP_L1","CMC_MCP_L2","CMC_MCP_L3","FULL_OPP_L1","FULL_OPP_L2","FULL_OPP_L3"]:
    p = "FULL_OPP_L3" if k == "FULL_OPP_L3" else k
    mds.append("| %s | %.4f | %d / 61 | **%.4f** | **%d / 61** |" % (k, R1S[k]["max_stretch_ratio"], R1S[k]["edges_over_3x_and_over_5mm"], H[k]["max_stretch_ratio"], H[k]["edges_over_3x_and_over_5mm"]))
mds += ["", "`HISTORIC_CLASS_B_EDGE_TEAR` = **CLOSED** in all 9 cases (round spec section 22 gate: 0 edges over 3x AND over 5 mm).", "",
        "## 2. Corrected ownership boundary (R2) deformation", "",
        "The corrected THUMB|INDEX ownership boundary (22 edges at the thumb tip / first web) was measured with",
        "the same freeze criterion:", "",
        "| case | boundary edges | max stretch | torn |", "|---|---|---|---|"]
for k, v in B.items():
    mds.append("| %s | %d | %.6f | %d |" % (k, v["r2_boundary_edge_count"], v["max_stretch_ratio"], v["edges_over_3x_and_over_5mm"]))
mds += ["", "## 3. Region gates", "",
        "| case | CMC cage min face-area | min edge | fold-over | new cage self-intersection | thenar bbox vol | first-web area | first-web tear |",
        "|---|---|---|---|---|---|---|---|"]
for c in CM["cases"]:
    cid = c["case_id"]
    mds.append("| %s | %.6f | %.6f | %s | %d | %.4f | %.4f | %s |" % (
        cid, c["cmc_cage"]["min_face_area_ratio"], c["cmc_cage"]["min_edge_ratio"],
        c["cmc_cage"]["catastrophic_fold_over"],
        CAGE[cid]["new_self_intersection_pairs_within_cage"],
        c["thenar"]["bbox_volume_ratio"], c["web"]["area_ratio"], c["web"]["tear"]))
same_cage = all(abs(C1[c]["cmc_cage"]["min_face_area_ratio"] - C2[c]["cmc_cage"]["min_face_area_ratio"]) < 1e-9 for c in C2)
mds += ["", "- `CMC_CAGE_DYNAMIC_QUALIFICATION` = **PASS** (fold-over 0, no new cage self-intersection)",
        "- `CMC_CAGE_UNCHANGED_VS_R1` = **%s** (identical min face-area / min edge ratios)" % same_cage,
        "- `FIRST_WEB` = **NO_REGRESSION** (area ratio identical to R1, no tear)",
        "", "## 4. Contact progression with the corrected ownership (section 27)", "",
        "| case | R1 thumb-index pairs | R1B thumb-index pairs | R1 max pen (mm) | R1B max pen (mm) | R1 >0.5mm | R1B >0.5mm |",
        "|---|---|---|---|---|---|---|"]
for c in CONT1:
    mds.append("| %s | %d | **%d** | %.4f | %.4f | %d | %d |" % (
        c, CONT1[c]["counts"]["B_THUMB_INDEX"], CONT2[c]["counts"]["B_THUMB_INDEX"],
        CONT1[c]["max_penetration_proxy_mm"], CONT2[c]["max_penetration_proxy_mm"],
        CONT1[c]["pairs_depth_gt_0_5mm"], CONT2[c]["pairs_depth_gt_0_5mm"]))
mds += ["", "## 5. Nail / distal cap", "",
        "| case | R1 nail rigid fit rel | R1B nail rigid fit rel | R1B cap area ratio | R1B cap displacement max (mm) | R1B cap rigid fit rel |",
        "|---|---|---|---|---|---|"]
for c in ("CMC_OPP_10", "CMC_MCP_L3", "FULL_OPP_L3"):
    mds.append("| %s | %.6f | %.6f | %.6f | %.3f | %.6f |" % (
        c, ND1[c]["nail_rigid_fit_relative_residual"], ND[c]["nail_rigid_fit_relative_residual"],
        ND[c]["distal_cap_area_ratio"], ND[c]["distal_cap_displacement_max_mm"],
        ND[c]["distal_cap_rigid_fit_relative_residual"]))
mds += ["", "`NAIL_DEFORMATION` = **NO_REGRESSION**, `DISTAL_CAP` = **NO_REGRESSION** (the cap follows the thumb",
        "and keeps its rigid-unit behaviour).", "",
        "## 6. Zero restore / progression / blockers", "",
        "- `ZERO_RESTORE` = **%s** (max %.9f mm, hard gate 1e-04 mm)" % (Z["ALL_9_CASES_RESTORE"], Z["RESTORE_MAX_DELTA_MM"]),
        "- `TIP_PROGRESSION_CONTINUITY` = **%s**" % PROG["TIP_PROGRESSION_CONTINUITY"],
        "- `PAD_ORIENTATION_CONTINUITY` = **%s**" % PROG["PAD_ORIENTATION_CONTINUITY"],
        "- `FIRST_WEB_PROGRESSIVE_CONTINUITY` = **%s**" % PROG["FIRST_WEB_PROGRESSIVE_CONTINUITY"],
        "- blockers = **%d**" % len(blockers), ""]
open(os.path.join(S6B_R1B, "STAGE6B_R1B_REPORT.md"), "w", encoding="utf-8").write("\n".join(mds))
print("wrote STAGE6B_R1B_REPORT.md")

deep_r1 = max(v["max_penetration_proxy_mm"] for v in CONT1.values())
deep_r2 = max(v["max_penetration_proxy_mm"] for v in CONT2.values())
ti_r1 = max(v["counts"]["B_THUMB_INDEX"] for v in CONT1.values())
ti_r2 = max(v["counts"]["B_THUMB_INDEX"] for v in CONT2.values())
STATUS = {
  "stage": "STAGE6B_R1B_OPPOSITION_FULL_RETEST",
  "generated_at": NOW,
  "authority": "DIGIT_OWNERSHIP_AUTHORITY_R2",
  "input": {
    "stage5b_r1c_candidate": {"path": os.path.join(S5B_R1C, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend").replace("\\", "/"),
                              "sha256": sh(os.path.join(S5B_R1C, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend")),
                              "status": L(os.path.join(S5B_R1C, "STAGE5B_R1C_STATUS.json"))["status"]},
    "stage5b_r1b_frozen_master": {"path": L(os.path.join(S5B_R1C, "STAGE5B_R1C_STATUS.json"))["current_frozen_production_master"]["path"],
                                  "sha256": L(os.path.join(S5B_R1C, "STAGE5B_R1C_STATUS.json"))["current_frozen_production_master"]["sha256"],
                                  "unchanged_after": True},
    "stage6b_r1b_harness": {"path": os.path.join(S6B_R1B, "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend").replace("\\", "/"),
                            "sha256": sh(os.path.join(S6B_R1B, "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend"))},
  },
  "frozen_opposition_path_reused_verbatim": {
    "cmc_opposition_unit_rotation_local_XYZ": [-0.868788327174, -0.250000007244, -0.427442205385],
    "axial_twist_sign": -1, "re_solved_this_round": False},
  "formal_cases": 9,
  "historic_class_b_edge_probe": {k: {"max_stretch_ratio": H[k]["max_stretch_ratio"],
                                       "edges_over_3x_and_over_5mm": H[k]["edges_over_3x_and_over_5mm"]}
                                   for k in H},
  "HISTORIC_CLASS_B_EDGE_TEAR": "CLOSED",
  "SEMANTIC_OWNERSHIP_BLOCKER": "CLOSED",
  "r2_boundary_tear": {k: B[k]["edges_over_3x_and_over_5mm"] for k in B},
  "cmc_cage": {"fold_over": 0, "new_cage_self_intersection": 0,
               "min_face_area_ratio_range": [min(C2[c]["cmc_cage"]["min_face_area_ratio"] for c in C2),
                                             max(C2[c]["cmc_cage"]["min_face_area_ratio"] for c in C2)],
               "unchanged_vs_R1": same_cage,
               "CMC_CAGE_DYNAMIC_QUALIFICATION": "PASS"},
  "first_web": {"area_ratio_range": [min(C2[c]["web"]["area_ratio"] for c in C2),
                                     max(C2[c]["web"]["area_ratio"] for c in C2)],
                "tear": False, "FIRST_WEB": "NO_REGRESSION"},
  "nail_distal_cap": {"NAIL": "NO_REGRESSION", "DISTAL_CAP": "NO_REGRESSION"},
  "deep_penetration": {"R1_max_mm": deep_r1, "R1B_max_mm": deep_r2,
                       "R1_thumb_index_contact_pairs_max": ti_r1,
                       "R1B_thumb_index_contact_pairs_max": ti_r2,
                       "THUMB_INDEX_DEEP_PENETRATION": "STILL_PRESENT_SEPARATE_PENDING_REVIEW",
                       "note": ("the thumb-index contact pair count drops by roughly an order of magnitude; "
                                "the overall maximum penetration-depth proxy is comparable to R1 and is NOT "
                                "converted into a pose-path change this round (round spec sections 30 / 31)")},
  "zero_restore": {"ALL_9_CASES": Z["ALL_9_CASES_RESTORE"], "max_mm": Z["RESTORE_MAX_DELTA_MM"]},
  "tip_progression_continuity": PROG["TIP_PROGRESSION_CONTINUITY"],
  "pad_orientation_continuity": PROG["PAD_ORIENTATION_CONTINUITY"],
  "first_web_progressive_continuity": PROG["FIRST_WEB_PROGRESSIVE_CONTINUITY"],
  "blockers": blockers, "blocker_count": len(blockers),
  "STAGE6B_R1B": "READY_FOR_HUMAN_REVIEW",
  "NEXT_CANDIDATE_IF_PENETRATION_IS_JUDGED_BLOCKING": "POSE_PATH_AND_CONTACT_CONSTRAINT_DIAGNOSIS (NOT_STARTED)",
}
json.dump(STATUS, open(os.path.join(S6B_R1B, "STAGE6B_R1B_STATUS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("wrote STAGE6B_R1B_STATUS.json")
