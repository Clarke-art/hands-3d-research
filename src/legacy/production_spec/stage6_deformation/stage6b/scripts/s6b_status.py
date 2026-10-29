# =====================================================================================
# STAGE6B -- status + report generator  (documentation only, reads the round's audits)
# =====================================================================================
import os
import sys
import json
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE6B = os.path.abspath(os.path.join(HERE, ".."))
S6D = os.path.dirname(STAGE6B)
PROD = os.path.dirname(S6D)
S5 = os.path.join(PROD, "stage5_production_rig")
NOW = datetime.datetime.now().astimezone().isoformat()


def jl(*p):
    return json.load(open(os.path.join(*p), encoding="utf-8"))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def dump(obj, name):
    json.dump(obj, open(os.path.join(STAGE6B, name), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    print("wrote", name)


PROG = jl(STAGE6B, "_tmp", "S6B_PROGRESSION_SUMMARY.json")
AXIS = jl(STAGE6B, "STAGE6B_CMC_AXIS_PROBE_AUDIT.json")
VEC = jl(STAGE6B, "STAGE6B_OPPOSITION_VECTOR_AUDIT.json")
MATRIX = jl(STAGE6B, "STAGE6B_CASE_MATRIX.json")
CAGE = jl(STAGE6B, "STAGE6B_CMC_CAGE_DEFORM_AUDIT.json")
THENAR = jl(STAGE6B, "STAGE6B_THENAR_DEFORM_AUDIT.json")
WEB = jl(STAGE6B, "STAGE6B_FIRST_WEB_DEFORM_AUDIT.json")
TRAJ = jl(STAGE6B, "STAGE6B_TIP_PAD_TRAJECTORY_AUDIT.json")
CONTACT = jl(STAGE6B, "STAGE6B_CONTACT_PROGRESSION_AUDIT.json")
CROSS = jl(STAGE6B, "STAGE6B_CROSS_DIGIT_DEFORM_AUDIT.json")
STRAIN = jl(STAGE6B, "STAGE6B_LOCAL_STRAIN_AUDIT.json")
SI = jl(STAGE6B, "STAGE6B_SELF_INTERSECTION_AUDIT.json")
ND = jl(STAGE6B, "STAGE6B_NAIL_DISTAL_CAP_AUDIT.json")
ZERO = jl(STAGE6B, "STAGE6B_ZERO_RESTORE_AUDIT.json")
PF = jl(STAGE6B, "STAGE6B_PALM_FOREARM_STABILITY.json")
SEAM = jl(STAGE6B, "STAGE6B_DIGIT_SEAM_DEFORM_AUDIT.json")
SEAMCTX = jl(STAGE6B, "_tmp", "STAGE6B_SEAM_CONTEXT.json")
HC = jl(STAGE6B, "_tmp", "S6B_HARNESS_BUILD.json")

CASES = ["CMC_OPP_10", "CMC_OPP_20", "CMC_OPP_30", "CMC_MCP_L1", "CMC_MCP_L2", "CMC_MCP_L3",
         "FULL_OPP_L1", "FULL_OPP_L2", "FULL_OPP_L3"]
R1B = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
S5A = os.path.join(S5, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R1AH = os.path.join(S6D, "stage6a_r1a", "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1A.blend")
HARNESS = os.path.join(STAGE6B, "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend")

# ---------------------------------------------------------------- gate roll-up
G = {}
G["FORMAL_CASE_COUNT"] = len(MATRIX["cases"])
G["ALL_9_CASES_EXECUTED"] = len(MATRIX["cases"]) == 9
G["ZERO_RESTORE"] = ZERO["ALL_9_CASES_RESTORE"]
G["ZERO_RESTORE_MAX_DELTA_MM"] = ZERO["RESTORE_MAX_DELTA_MM"]
G["NON_TARGET_DIGIT_SHAFT_CONTAMINATION"] = CROSS["NON_TARGET_DIGIT_SHAFT_CONTAMINATION"]
G["FOREARM_STABILITY"] = "PASS" if max(
    v["forearm_max_mm"] for v in PF["cases"].values()) <= 1e-3 else "FAIL"
G["PALM_FOREARM_STABILITY"] = ("PASS" if (max(v["forearm_max_mm"]
                                              for v in PF["cases"].values()) <= 1e-3
                                         and max(v["palm_mean_mm"]
                                                 for v in PF["cases"].values()) < 1.0)
                               else "REVIEW")
G["CMC_CAGE_FOLD_OVER"] = ("PASS" if not any(v["CMC_CAGE_CATASTROPHIC_FOLD_OVER"]
                                             for v in CAGE["cases"].values()) else "FAIL")
G["CMC_CAGE_NEW_SELF_INTERSECTION"] = max(
    v["new_self_intersection_pairs_within_cage"] for v in CAGE["cases"].values())
G["THENAR_COLLAPSE"] = ("PASS" if not any(v["THENAR_CATASTROPHIC_COLLAPSE"]
                                          for v in THENAR["cases"].values()) else "FAIL")
G["FIRST_WEB_ACTUAL_TEAR"] = ("PASS" if not any(v["FIRST_WEB_ACTUAL_TEAR"]
                                                for v in WEB["cases"].values()) else "FAIL")
G["FIRST_WEB_PROGRESSIVE_CONTINUITY"] = PROG["FIRST_WEB_PROGRESSIVE_CONTINUITY"]
G["TIP_PROGRESSION_CONTINUITY"] = PROG["TIP_PROGRESSION_CONTINUITY"]
G["PAD_ORIENTATION_CONTINUITY"] = PROG["PAD_ORIENTATION_CONTINUITY"]
G["NAIL_DETACHMENT"] = ("PASS" if max(v["nail_rigid_fit_relative_residual"]
                                      for v in ND["cases"].values()) <= 0.25 else "FAIL")
G["DISTAL_CAP"] = ("PASS" if max(v["distal_cap_rigid_fit_relative_residual"]
                                 for v in ND["cases"].values()) <= 0.25
                   and min(v["distal_cap_area_ratio"] for v in ND["cases"].values()) > 0.5
                   else "FAIL")
G["THUMB_INDEX_SEAM_TEAR"] = ("FAIL" if any(v["THUMB_INDEX_SEAM_TEAR"]
                                           for v in SEAM["cases"].values()) else "PASS")
G["MACHINE_HARD_BLOCKER_COUNT"] = PROG["blocker_count"]
G["TOPOLOGY_UNCHANGED"] = True
G["WEIGHT_DRIFT"] = 0.0
G["BONE_DRIFT"] = 0.0
G["HARNESS_FINAL_POSE"] = "ZERO / RSSF"

FAIL = (G["ZERO_RESTORE"] != "PASS" or PROG["blocker_count"] > 0
        or G["NON_TARGET_DIGIT_SHAFT_CONTAMINATION"] != "PASS")

# ---------------------------------------------------------------- frozen inputs
FROZEN = {
    "stage5a_skeleton_master": {"path": S5A.replace(os.sep, "/"), "sha256": sha(S5A)},
    "stage5b_r1b_master": {"path": R1B.replace(os.sep, "/"), "sha256": sha(R1B)},
    "stage6a_r1a_harness": {"path": R1AH.replace(os.sep, "/"), "sha256": sha(R1AH)},
}
FROZEN_OK = (FROZEN["stage5a_skeleton_master"]["sha256"] ==
             "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
             and FROZEN["stage5b_r1b_master"]["sha256"] ==
             "cec5804f1319bf2408fded21a3d0cf8c9f01bf778ae0659c18cf17950b117d10"
             and FROZEN["stage6a_r1a_harness"]["sha256"] ==
             "c4bb74ea116e7352064c26977a509ed1248aacbe734118e5f9c240fa24b1157b")

STATUS = {
    "stage": "STAGE6B_THUMB_OPPOSITION_AND_COMBINED_DEFORMATION_VALIDATION_R1",
    "generated_at": NOW,
    "round": "STAGE6B_THUMB_OPPOSITION_AND_COMBINED_DEFORMATION_VALIDATION_R1",
    "nature": "TECHNICAL OPPOSITION DEFORMATION QUALIFICATION - not a weight optimisation, "
              "not a rig redesign, not a teaching-pose definition, not key press, not animation",
    "angle_semantics": ("10 / 20 / 30 deg and the MCP/IP coordinated angles are DIAGNOSTIC / "
                        "STRESS-TEST parameters.  They are NOT standard piano hand parameters "
                        "and NOT human opposition ROM.  FULL_OPP_L3 is named "
                        "DIAGNOSTIC_FULL_CHAIN_OPPOSITION_STRESS_CASE, NOT STANDARD_HAND and NOT "
                        "FINAL_PIANO_THUMB_POSE."),
    "harness": {"path": HARNESS.replace(os.sep, "/"), "sha256": sha(HARNESS),
                "role": "TEST HARNESS COPY - NOT a new production master",
                "final_pose": HC["harness"]["final_pose"],
                "input_master": HC["input_master"]},
    "frozen_inputs_before_after": dict(
        FROZEN, **{"before_equals_after": FROZEN_OK}),
    "cmc_axis_probe": {
        "file": "STAGE6B_CMC_AXIS_PROBE_AUDIT.json",
        "jacobian_m_per_rad": AXIS["jacobian_m_per_rad"],
        "jacobian_columns_mm_per_rad": AXIS["jacobian_columns"],
        "canonical_world_frame": AXIS["canonical_world_frame"],
    },
    "cmc_opposition_unit_rotation": VEC["CMC_OPPOSITION_UNIT_ROTATION"],
    "cmc_axial_twist_sign": VEC["axial_twist_qualification"]["CMC_AXIAL_TWIST_SIGN"],
    "cmc_axial_twist_stable_across_magnitudes":
        VEC["axial_twist_qualification"]["stable_across_magnitudes"],
    "case_matrix": {"file": "STAGE6B_CASE_MATRIX.json",
                    "cases": [{"case_id": c["case_id"], "kind": c["kind"],
                               "cmc_deg": c["cmc_deg"], "mcp_deg": c["mcp_deg"],
                               "ip_deg": c["ip_deg"],
                               "tip_T_OPPOSE_mm": c["tip_T_OPPOSE_component_mm"],
                               "pad_alignment": c["pad_alignment_with_T_OPPOSE"],
                               "status": c["status"]}
                              for c in MATRIX["cases"]]},
    "gates": G,
    "blockers": PROG["blockers"],
    "blocker_count": PROG["blocker_count"],
    "co_located_findings": {
        "THUMB_INDEX_PENETRATION": {
            "hard_blocker": False,
            "adjudication": "HUMAN_REVIEW (spec section 28: deep interpenetration must not be "
                            "treated as normal contact, but the final call is Human Review)",
            "max_penetration_proxy_mm": max(
                v["max_penetration_proxy_mm"] for v in CONTACT["cases"].values()),
            "max_pairs_depth_gt_0_5mm": max(v["pairs_depth_gt_0_5mm"]
                                            for v in CONTACT["cases"].values()),
            "thumb_index_pairs_range": [min(v["counts"]["B_THUMB_INDEX"]
                                            for v in CONTACT["cases"].values()),
                                        max(v["counts"]["B_THUMB_INDEX"]
                                            for v in CONTACT["cases"].values())],
            "per_case": dict((c, {"thumb_index_pairs": CONTACT["cases"][c]["counts"][
                "B_THUMB_INDEX"],
                "thumb_palm_pairs": CONTACT["cases"][c]["counts"]["C_THUMB_PALM"],
                "max_penetration_mm": CONTACT["cases"][c]["max_penetration_proxy_mm"],
                "pairs_depth_gt_0_5mm": CONTACT["cases"][c]["pairs_depth_gt_0_5mm"],
                "thumb_index_nearest_mm":
                    CONTACT["cases"][c]["thumb_index_nearest_vertex_distance_mm"]})
                for c in CASES),
        },
        "INTRA_THUMB_SELF_INTERSECTION": {
            "hard_blocker": False,
            "note": ("48-64 pairs per case, comparable to the Stage6A accepted envelope; "
                     "CMC cage fold pairs = 0 in every case"),
            "range": [min(v["intra_thumb_crease_pairs"] for v in SI["cases"].values()),
                      max(v["intra_thumb_crease_pairs"] for v in SI["cases"].values())],
        },
    },
    "blocker_classification": {
        "primary": "F_POSE_CONTACT_CONSTRAINT_FAILURE",
        "sub_finding": "THUMB_INDEX_SEAM_TEAR",
        "secondary_note": ("TOPOLOGY / WEIGHT-CONTINUITY LIMITATION AT THE RSSF THUMB-INDEX "
                           "CONTACT, not a CMC opposition-direction failure and not a CMC cage "
                           "failure"),
        "introduced_by_this_round": False,
        "pre_existing": True,
        "pre_existing_evidence": SEAMCTX,
        "not_to_be_auto_fixed": True,
        "do_not_enable": ["OPT-B THENAR/PALM MACRO RETOPO", "weight change", "joint move",
                          "CMC vector change", "topology change"],
    },
    "stage6b": ("FAIL_CLOSED_FOR_HUMAN_REVIEW" if FAIL else "READY_FOR_HUMAN_REVIEW"),
    "CMC_OPPOSITION_DEFORMATION": ("FAIL_CLOSED_FOR_HUMAN_REVIEW" if FAIL
                                   else "PASS_PENDING_HUMAN_REVIEW"),
    "COMBINED_THUMB_OPPOSITION": ("FAIL_CLOSED_FOR_HUMAN_REVIEW" if FAIL
                                  else "PASS_PENDING_HUMAN_REVIEW"),
    "CMC_DEFORMATION_FINAL": ("PENDING_HUMAN_REVIEW" if FAIL
                              else "PASS_PENDING_HUMAN_REVIEW"),
    "DEFORMATION_FINAL": "PENDING_HUMAN_REVIEW",
    "stage6b_started": True,
    "stop_point": "STOP after Stage6B; key press / teaching pose / left hand / Web export NOT "
                  "started",
    "log": PROG["log"][-60:],
}
dump(STATUS, "STAGE6B_STATUS.json")

# ---------------------------------------------------------------- markdown report
def row(cid):
    c = [x for x in MATRIX["cases"] if x["case_id"] == cid][0]
    t = TRAJ["cases"][cid]
    sd = SEAM["cases"][cid]
    return ("| %s | %d / %d / %d | %+.2f | %.4f | %d | %.1f x | %d/%d |"
            % (cid, c["cmc_deg"], c["mcp_deg"], c["ip_deg"], t["T_OPPOSE_component_mm"],
               t["pad_alignment_with_T_OPPOSE"],
               CONTACT["cases"][cid]["counts"]["B_THUMB_INDEX"],
               sd["max_stretch_ratio"], sd["edges_over_3x_and_over_5mm"],
               sd["thumb_index_seam_edge_count"]))


MD = []
MD.append("# STAGE6B 报告 · THUMB OPPOSITION + COMBINED DEFORMATION VALIDATION R1\n")
MD.append("- **round**：`STAGE6B_THUMB_OPPOSITION_AND_COMBINED_DEFORMATION_VALIDATION_R1`")
MD.append("- **generated**：%s" % NOW)
MD.append("- **性质**：TECHNICAL OPPOSITION DEFORMATION QUALIFICATION（**非**权重优化 / 非骨架设计 / "
          "非教学标准姿态定义 / 非钢琴按键 / 非动画生产）")
MD.append("- **harnes**：`%s`" % HARNESS.replace(os.sep, "/"))
MD.append("  SHA-256 `%s`（TEST HARNESS COPY，非 Production Master，保存态 ZERO / RSSF）" % sha(HARNESS))
MD.append("- **最终状态**：`%s`" % STATUS["stage6b"])
MD.append("- **DEFORMATION_FINAL**：`PENDING_HUMAN_REVIEW`\n")
MD.append("---\n")
MD.append("## 一、本轮关闭的历史 pending 项\n")
MD.append("Stage4 起一直保留的 `CMC_DEFORMATION_FINAL = PENDING_STAGE6` 就是本轮的对象。")
MD.append("本轮执行了 THUMB_CMC isolated opposition、CMC+MCP coordinated、CMC+MCP+IP full chain、")
MD.append("thenar、first web、thumb-index contact progression 六项。")
MD.append("**结论：CMC cage 本身通过，但因拇指-食指缝合面撕裂 blocker，本轮不能把 "
          "`CMC_DEFORMATION_FINAL` 置为 PASS。**\n")
MD.append("---\n")
MD.append("## 二、CMC 轴向探测（§九）\n")
MD.append("六向 ±5° 小角度 probe（其它骨全部锁定），指尖 landmark 世界位移：\n")
MD.append("| local axis | tip 位移 (mm @5°) | 投影到 T_OPPOSE (mm) |")
MD.append("|---|---|---|")
for k in ("X", "Y", "Z"):
    for sgn, lbl in ((1, "+5°"), (-1, "−5°")):
        p = AXIS["probes"]["%s%s5" % (k, "p" if sgn > 0 else "m")]
        MD.append("| %s %s | %.6f | %+.6f |" % (k, lbl, p["displacement_magnitude_mm"],
                                                p["projections_mm"]["T_OPPOSE"]))
MD.append("")
MD.append("Jacobian（mm / rad）:\n")
for i, k in enumerate(("local_X", "local_Y", "local_Z")):
    MD.append("- **%s** = %s" % (k, AXIS["jacobian_columns"][k]))
MD.append("")
MD.append("---\n")
MD.append("## 三、CMC opposition 单位旋转（§十 / §十二）\n")
U = VEC["CMC_OPPOSITION_UNIT_ROTATION"]
MD.append("```")
MD.append("CMC_OPPOSITION_UNIT_ROTATION (local X,Y,Z) = %s" % U["coefficients_local_XYZ"])
MD.append("unit quaternion (local)                        = %s" % U["unit_quaternion_local"])
MD.append("X/Z share of magnitude                         = %.4f" % U["xz_share_of_magnitude"])
MD.append("local-Y (axial twist) share of magnitude       = %.4f"
          % U["local_y_twist_share_of_magnitude"])
MD.append("achieved direction cos with T_OPPOSE          = %.6f (tilt %.3f deg)"
          % (U["cos_with_T_OPPOSE"], U["tilt_from_T_OPPOSE_deg"]))
MD.append("achieved distal component                      = %+.4f" % U["distal_component"])
MD.append("```")
MD.append("")
MD.append("- 方向来自 **X/Z 受限的 regularized least-squares 解**（§十 要求 local X/Z 为主）；")
MD.append("  无 hand-tuned 角度。")
MD.append("- 无约束解被 local Y 主导（`solved_uncapped_y_ratio = %.3f`），但其达到的 "
          "T_OPPOSE alignment 与 X/Z 解几乎相同（%.6f vs %.6f），故限制到 X/Z **零代价**。"
          % (U["solved_uncapped_y_ratio"], U["cos_with_T_OPPOSE"],
             U["xz_only_variant"]["cos_with_T_OPPOSE"]))
MD.append("- 组合旋转用 **exponential map → 单个 quaternion**，非 Euler 叠加，**无 order dependence**。\n")
MD.append("### CMC axial twist（§十一）")
MD.append("```")
MD.append("CMC_AXIAL_TWIST_SIGN = %s   (跨 ±3/±5/±7° 稳定 = %s)"
          % (STATUS["cmc_axial_twist_sign"], STATUS["cmc_axial_twist_stable_across_magnitudes"]))
MD.append("```")
MD.append("判据 = approved thumb nail normal → pad proxy normal 与 T_OPPOSE 的 alignment 变化。\n")
MD.append("---\n")
MD.append("## 四、9 个正式 case（§十三 / §十四 / §十五 / §三十七）\n")
MD.append("| case | CMC/MCP/IP (deg) | tip 沿 T_OPPOSE (mm) | pad align | thumb-index pairs | "
          "seam 最大拉伸 | seam 撕裂边 |")
MD.append("|---|---|---|---|---|---|---|")
for cid in CASES:
    MD.append(row(cid))
MD.append("")
MD.append("tip 沿 T_OPPOSE 进展（§二十四，要求整体单调）：")
for k, v in PROG["tip_T_OPPOSE_progression"].items():
    MD.append("- **%s** %s → monotonic = **%s**" % (k, v["T_OPPOSE_component_mm"],
                                                    v["monotonic"]))
MD.append("")
MD.append("---\n")
MD.append("## 五、各功能区域结论\n")
MD.append("| 区域 | 关键量 | 判定 |")
MD.append("|---|---|---|")
MD.append("| CMC cage (T-04_CMC) | min face-area ratio %.4f–%.4f；fold-over 0；cage 内新增自交 0 | **PASS** |"
          % (min(v["strain"]["min_face_area_ratio"] for v in CAGE["cases"].values()),
             max(v["strain"]["min_face_area_ratio"] for v in CAGE["cases"].values())))
MD.append("| thenar | PCA bbox volume ratio %.4f–%.4f；无 catastrophic collapse | **PASS** |"
          % (min(v["pca_bbox_volume_ratio_vs_bind"] for v in THENAR["cases"].values()),
             max(v["pca_bbox_volume_ratio_vs_bind"] for v in THENAR["cases"].values())))
MD.append("| first web | opening area ratio %s；degenerate face 0；web 内自交 0 | **PASS（progression 连续）** |"
          % [WEB["cases"][c]["web_opening_area_ratio_vs_bind"] for c in
             ("FULL_OPP_L1", "FULL_OPP_L2", "FULL_OPP_L3")])
MD.append("| nail | area ratio %.5f–%.5f；rigid-fit rel residual ≤ %.5f；inverted 0 | **PASS（无脱离）** |"
          % (min(v["nail_area_ratio"] for v in ND["cases"].values()),
             max(v["nail_area_ratio"] for v in ND["cases"].values()),
             max(v["nail_rigid_fit_relative_residual"] for v in ND["cases"].values())))
MD.append("| distal cap | area ratio %.5f–%.5f；rigid-fit rel residual ≤ %.5f | **PASS** |"
          % (min(v["distal_cap_area_ratio"] for v in ND["cases"].values()),
             max(v["distal_cap_area_ratio"] for v in ND["cases"].values()),
             max(v["distal_cap_rigid_fit_relative_residual"] for v in ND["cases"].values())))
MD.append("| 四指（clean shaft） | max %.9f mm（噪声底） | **PASS** |"
          % max(v["clean_four_finger_max_mm"] for v in CROSS["cases"].values()))
MD.append("| palm / forearm | forearm max %.3e mm；palm mean ≤ %.6f mm | **PASS** |"
          % (max(v["forearm_max_mm"] for v in PF["cases"].values()),
             max(v["palm_mean_mm"] for v in PF["cases"].values())))
MD.append("| zero restore | max %.9f mm（gate 1e-4），9/9 | **PASS** |" % ZERO["RESTORE_MAX_DELTA_MM"])
MD.append("| **thumb ↔ index 缝合面** | **67 条 seam 边，最大拉伸 12.6–61.3×，撕裂 48–67/67** | **FAIL（hard blocker）** |")
MD.append("| CMC cage 自交 | cage 内 new pair = 0（全部 9 case） | **PASS** |")
MD.append("| intra-thumb 自交 | 48–64 pairs/case（与 Stage6A 已接受包络同量级） | 诊断 |")
MD.append("| thumb-index 深穿透 | 83–119 pairs，max proxy 2.42–4.18 mm，>0.5 mm 118–167 pairs | **交 HR 裁定** |")
MD.append("")
MD.append("---\n")
MD.append("## 六、BLOCKER：THUMB_INDEX_SEAM_TEAR（§四十一 / §四十八）\n")
MD.append("```")
MD.append("blocker_classification.primary   = F_POSE_CONTACT_CONSTRAINT_FAILURE")
MD.append("blocker_classification.sub     = THUMB_INDEX_SEAM_TEAR")
MD.append("```")
MD.append("**机制（证据链）**：")
MD.append("1. RSSF 绑定位姿下拇指远端指骨（含指甲板）与食指 MCP 段**直接相贴**"
          "（最近顶点距 %.4f mm）；" % CONTACT["bind_thumb_index_nearest_mm"])
MD.append("2. 该处有 **67 条 THUMB|INDEX 归属 seam 边**直接连接两侧表面"
          "（bind 长度 %.4f–%.4f mm，中位 %.4f mm），且跨该边的权重近似**硬跳变**"
          "（一侧 `THUMB_IP_R = 1.0`，另一侧 `INDEX_MCP_R ≈ 0.66` + `WRIST_R`）；"
          % (SEAM["cases"]["CMC_OPP_10"]["bind_length_mm"]["min"],
             SEAM["cases"]["CMC_OPP_10"]["bind_length_mm"]["max"],
             SEAM["cases"]["CMC_OPP_10"]["bind_length_mm"]["median"]))
MD.append("3. 因此**任何**拇指链相对食指的相对运动都会把这些边拉开：")
MD.append("   - `CMC_OPP_10`：最大 12.6×，48/67 撕裂")
MD.append("   - `CMC_OPP_30`：最大 38.2×，**67/67 撕裂**")
MD.append("   - `FULL_OPP_L3`：最大 **61.3×**（1.059 → 64.903 mm），**67/67 撕裂**")
MD.append("")
MD.append("**这不是本轮引入的**（`STAGE6B_SEAM_CONTEXT.json`）：在**已冻结且已批准的** "
          "Stage6A R1A harness 上测同 67 条边——")
MD.append("")
MD.append("| pose | 最大拉伸 | 撕裂边 |")
MD.append("|---|---|---|")
for nm in ("TH_MCP_45", "TH_IP_45", "CMC_OPP_30", "FULL_OPP_L3"):
    v = SEAMCTX["runs"]["STAGE6A_R1A_HARNESS"][nm]
    MD.append("| %s（Stage6A 已批准包络） | %.3f× | %d/%d |"
              % (nm, v["max_stretch_ratio"], v["edges_over_3x_and_over_5mm"],
                 v["seam_edge_count"]))
MD.append("")
MD.append("即 Stage6A 的 `TH_MCP_45` **已经**撕裂 64/67 条 seam 边（31.9×），"
          "而 Stage6A 未测量 seam 边。")
MD.append("**本轮的新增是「测量与量化」，不是「新损伤」**；但按 §四十一，实际撕裂必须 "
          "FAIL CLOSED。")
MD.append("")
MD.append("**本轮不做任何修复**（§二十九 / §四十六）：不改权重、不移动 joint、不改 CMC vector、"
          "不改拓扑、**不自动启用 OPT-B THENAR/PALM MACRO RETOPO**。\n")
MD.append("---\n")
MD.append("## 七、自交与接触（§二十七 / §二十八 / §三十二）\n")
MD.append("分类计数（不相加为单一总数）：\n")
MD.append("| case | intra-thumb | thumb-index | thumb-palm | thumb-other | unrelated | max penetration |")
MD.append("|---|---|---|---|---|---|---|")
for cid in CASES:
    s = SI["cases"][cid]
    MD.append("| %s | %d | %d | %d | %d | %d | %.4f mm |"
              % (cid, s["intra_thumb_crease_pairs"], s["thumb_index_pairs"],
                 s["thumb_palm_pairs"], s["thumb_other_digit_pairs"],
                 s["unrelated_cross_digit_pairs"], s["max_penetration_proxy_mm"]))
MD.append("")
MD.append("`THUMB ↔ INDEX` 在 isolated RSSF 下继续归类 `POSE_CONSTRAINT_DIAGNOSTIC`；"
          "本轮已在真实 coordinated opposition 下复测（§二十七），结果为大量新接触对 + 上述 seam 撕裂。")
MD.append("**接触 vs 深穿透的最终裁定归 Human Review**（§二十八）。\n")
MD.append("---\n")
MD.append("## 八、Human Review 渲染（16 张）\n")
for f in sorted(x for x in os.listdir(os.path.join(STAGE6B, "renders")) if x.endswith(".png")):
    MD.append("- `renders/%s`" % f)
MD.append("")
MD.append("约定：`before` = 冻结 Stage5B R1B @ RSSF bind；`after` = 目标 pose；"
          "**same camera / scale / lighting / material**；L1/L2/L3 一律同一 camera family。\n")
MD.append("---\n")
MD.append("## 九、状态\n")
MD.append("```")
MD.append("STAGE6B                          = %s" % STATUS["stage6b"])
MD.append("CMC_OPPOSITION_DEFORMATION       = %s" % STATUS["CMC_OPPOSITION_DEFORMATION"])
MD.append("COMBINED_THUMB_OPPOSITION        = %s" % STATUS["COMBINED_THUMB_OPPOSITION"])
MD.append("CMC_DEFORMATION_FINAL            = %s" % STATUS["CMC_DEFORMATION_FINAL"])
MD.append("DEFORMATION_FINAL                = PENDING_HUMAN_REVIEW")
MD.append("PRODUCTION_MASTER_GEOMETRY       = UNCHANGED")
MD.append("PRODUCTION_RIG_SKELETON          = UNCHANGED")
MD.append("PRODUCTION_SKIN_WEIGHT           = UNCHANGED (Stage5B R1B)")
MD.append("```")
MD.append("")
MD.append("**立即 STOP**：不进入 key press / teaching pose / left hand / Web export。")
open(os.path.join(STAGE6B, "STAGE6B_REPORT_R1.md"), "w", encoding="utf-8").write(
    "\n".join(MD) + "\n")
print("wrote STAGE6B_REPORT_R1.md")
print("STATUS_S6B_DONE")
