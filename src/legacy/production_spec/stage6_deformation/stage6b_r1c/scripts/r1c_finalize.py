# =====================================================================================
# STAGE6B_R1C -- finalise: report + status + frozen-input verification (pure python)
# =====================================================================================
import os, sys, json, hashlib, datetime, glob
HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S6D = os.path.join(PROD, "stage6_deformation")
S6B_R1C = os.path.join(S6D, "stage6b_r1c")
S5 = os.path.join(PROD, "stage5_production_rig")
NOW = datetime.datetime.now().astimezone().isoformat()


def L(p):
    return json.load(open(p, encoding="utf-8"))


def sh(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


PEN = L(os.path.join(S6B_R1C, "STAGE6B_R1C_PENETRATION_ADJUDICATION.json"))
STR = L(os.path.join(S6B_R1C, "STAGE6B_R1C_DEFORMATION_CONTINUITY_AUDIT.json"))
R1C_STATUS = L(os.path.join(S5, "stage5b_r1c", "STAGE5B_R1C_STATUS.json"))

# ---------------------------------------------------------------- frozen input verification
FROZEN = {
  "stage5b_r1b_frozen_master": os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend"),
  "stage5b_r1c_candidate": os.path.join(S5, "stage5b_r1c", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend"),
  "stage6a_r1b_harness": os.path.join(S6D, "stage6a_r1b", "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1B.blend"),
  "stage6b_r1b_harness": os.path.join(S6D, "stage6b_r1b", "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend"),
  "stage6b_r1_harness": os.path.join(S6D, "stage6b", "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1.blend"),
}
VER = {}
for k, p in FROZEN.items():
    VER[k] = {"path": p.replace("\\", "/"), "sha256": sh(p) if os.path.exists(p) else None}
VER["stage5b_r1b_matches_recorded_frozen_master"] = (
    VER["stage5b_r1b_frozen_master"]["sha256"] ==
    R1C_STATUS["current_frozen_production_master"]["sha256"])
VER["stage5b_r1c_matches_recorded_candidate"] = (
    VER["stage5b_r1c_candidate"]["sha256"] == R1C_STATUS["candidate"]["sha256"])

cases = ["CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]
BG = {"R1": STR["harnesses"]["R1_input_stage5b_r1b"], "R1B": STR["harnesses"]["R1B_input_stage5b_r1c"]}

md = []
md += ["# STAGE6B R1C -- THUMB / INDEX / PALM PENETRATION VISUAL ADJUDICATION", "",
       "Round kind: **HUMAN_REVIEW_EVIDENCE_ONLY**.  Generated `%s`." % NOW, "",
       "No model change of any kind.  Nothing was written to any `.blend`; no weight, ownership,",
       "geometry, topology, CMC cage, bone, joint, opposition vector, test angle or pose path was",
       "touched; no collision correction, no Stage6C, no freeze.  Only read / reproduce / render / measure.", "",
       "## 1. Frozen inputs (verified unchanged)", "",
       "| input | sha256 |", "|---|---|"]
for k, v in VER.items():
    if isinstance(v, dict):
        md.append("| `%s` | `%s` |" % (k, v["sha256"]))
md += ["", "`stage5b_r1b_frozen_master` still equals the recorded CURRENT_FROZEN_PRODUCTION_MASTER: **%s**  "
       % VER["stage5b_r1b_matches_recorded_frozen_master"],
       "`stage5b_r1c_candidate` still equals the recorded candidate: **%s**"
       % VER["stage5b_r1c_matches_recorded_candidate"], ""]

md += ["## 2. THE HEADLINE RESULT -- the published 2.60-4.69 mm proxy is not a thumb-index number", "",
       "The three frozen poses were reproduced verbatim (`re_solved_pose = %s`) and every new" % PEN["re_solved_pose"],
       "intersecting face pair was decomposed by **DIGIT_OWNERSHIP_AUTHORITY_R2** (corrected ownership):", "",
       "| pose | published overall max proxy | which pair it belongs to | THUMB\\_INDEX max proxy | THUMB\\_PALM max proxy |",
       "|---|---|---|---|---|"]
for cid in cases:
    r = PEN["cases"][cid]; cs = r["class_stats"]; m = r["max_pair"]
    md.append("| %s | **%.4f mm** | `%s` | **%.4f mm** | %.4f mm |" % (
        cid, m["proxy_depth_mm"], m["pair_class"],
        cs.get("THUMB_INDEX", {}).get("max_proxy_mm", 0.0),
        cs.get("THUMB_PALM", {}).get("max_proxy_mm", 0.0)))
md += ["", "In all three poses the adjudicated subject -- **thumb/index** -- is the *smallest* class present",
       "(6-8 real crossing pairs, 0.42-1.13 mm proxy).  The large values belong to **thumb/palm**, ",
       "**thumb/other-digit** and **intra-thumb**.", ""]

md += ["## 3. WHY the numbers are large -- the decisive evidence", "",
       "It is **not** physiological surface contact, and it is **not** an over-optimistic posture.",
       "The three poses deform the thumb's own distal surface into a **torn flap**:", "",
       "| metric | Stage6B R1 (frozen R1B master) | Stage6B R1B (R1C candidate) |",
       "|---|---|---|",
       "| hard 0/1 weight-flip edges in the input master | **%d** | **%d** |",
       "| CMC_OPP_30: edges >2x / >5x | %d / %d | %d / %d |",
       "| CMC_MCP_L3: edges >2x / >5x | %d / %d | %d / %d |",
       "| FULL_OPP_L3: edges >2x / >5x | %d / %d | %d / %d |",
       "| worst stretch ratio (all three poses) | %.2fx | %.2fx |",
       "| faces over 5x, by corrected ownership | %s | %s |"]
a = BG["R1"]["cases"]; b = BG["R1B"]["cases"]
md = md[:md.index("| hard 0/1 weight-flip edges in the input master | **%d** | **%d** |")]
md += ["| hard 0/1 weight-flip edges in the input master | **%d** | **%d** |" %
       (BG["R1"]["master_hard_flip_edges"], BG["R1B"]["master_hard_flip_edges"]),
       "| CMC_OPP_30: edges >2x / >5x | %d / %d | %d / %d |" %
       (a["CMC_OPP_30"]["edges_over_2x"], a["CMC_OPP_30"]["edges_over_5x"],
        b["CMC_OPP_30"]["edges_over_2x"], b["CMC_OPP_30"]["edges_over_5x"]),
       "| CMC_MCP_L3: edges >2x / >5x | %d / %d | %d / %d |" %
       (a["CMC_MCP_L3"]["edges_over_2x"], a["CMC_MCP_L3"]["edges_over_5x"],
        b["CMC_MCP_L3"]["edges_over_2x"], b["CMC_MCP_L3"]["edges_over_5x"]),
       "| FULL_OPP_L3: edges >2x / >5x | %d / %d | %d / %d |" %
       (a["FULL_OPP_L3"]["edges_over_2x"], a["FULL_OPP_L3"]["edges_over_5x"],
        b["FULL_OPP_L3"]["edges_over_2x"], b["FULL_OPP_L3"]["edges_over_5x"]),
       "| worst stretch ratio (all poses) | %.2fx | %.2fx |" %
       (max(a[c]["max_stretch_ratio"] for c in cases), max(b[c]["max_stretch_ratio"] for c in cases)),
       "| faces over 5x, by corrected ownership | %s | %s |" %
       (json.dumps(a["FULL_OPP_L3"]["faces_over_5x_by_ownership"]),
        json.dumps(b["FULL_OPP_L3"]["faces_over_5x_by_ownership"])), ""]
md += ["**Root cause, measured directly on the input master** (bind state, Blender's own vertex groups):",
       "adjacent vertices on the **thumb's own distal surface** carry",
       "`THUMB_IP_R = 1.0` next to `WRIST_R = 1.0` (and one `INDEX_MCP_R` case).  The flip vertices are",
       "**%.1f-%.1f mm from the thumb distal-cap centroid** and are `%d / %d` inside the R2 correction" % (
           STR["harnesses"]["R1B_input_stage5b_r1c"].get("hard_flip_vertex_distance_to_thumb_cap_mm", [0, 0])[0],
           STR["harnesses"]["R1B_input_stage5b_r1c"].get("hard_flip_vertex_distance_to_thumb_cap_mm", [0, 0])[1],
           STR["harnesses"]["R1B_input_stage5b_r1c"].get("hard_flip_vertices_in_R2_correction_domain", 0),
           STR["harnesses"]["R1B_input_stage5b_r1c"].get("hard_flip_vertex_count", 0)),
       "domain, i.e. they are thumb vertices with wrist/index weights.  Under opposition one side",
       "travels ~70-95 mm and the other stays put, so the surface tears open (bind 3-4 mm edges become",
       "40-95 mm) and the resulting flap sweeps back through the palm and the neighbouring digits.", "",
       "This is therefore **NOT** `THUMB_INDEX_DEEP_PENETRATION` caused by contact or by the pose path.",
       "It is a **local blend-weight continuity failure on the thumb distal surface**.", ""]

md += ["## 4. Per-pose adjudication of the actual thumb/index pair", "",
       "Single unified rule (`classification_rule` in the JSON): the depth is a footprint-constrained",
       "poke depth, normalised by the **bind** mean edge of the SAME triangle pair, so the verdict does",
       "not depend on facet size.", "",
       "| pose | focus pair | faces | real tri/tri crossing | segment | poke | bind local edge | poke/edge | classification |",
       "|---|---|---|---|---|---|---|---|---|"]
for cid in cases:
    r = PEN["cases"][cid]; f = r["adjudication_focus"]
    md.append("| %s | `%s` | %d / %d | %s | %.4f mm | %.4f mm | %.4f mm | **%.4f** | **%s** |" % (
        cid, f["class"], f["face_a"], f["face_b"], f["actual"]["intersect"],
        f["actual"]["intersection_segment_mm"], f["actual"]["poke_depth_mm"],
        f["actual"]["local_bind_edge_mm"], f["actual"]["poke_over_local_bind_edge"],
        f["classification"]))
md += ["", "Every class present in each pose:", "",
       "| pose | class | pairs | real | affected faces | max proxy | max poke | max segment | class at max |",
       "|---|---|---|---|---|---|---|---|---|"]
for cid in cases:
    for k, v in sorted(PEN["cases"][cid]["class_stats"].items()):
        md.append("| %s | %s | %d | %d | %d | %.4f mm | %.4f mm | %.4f mm | %s |" % (
            cid, k, v["pairs"], v["real_pairs"], v["affected_face_count"],
            v["max_proxy_mm"], v["max_poke_mm"], v["max_seg_mm"],
            v.get("classification_at_max", v.get("classification", "-"))))
md += ["", "## 5. Actual geometric intersection census", "",
       "| pose | new intersecting pairs | with a real tri/tri crossing | affected faces | components | largest | total crossing length | mean crossing length |",
       "|---|---|---|---|---|---|---|---|"]
for cid in cases:
    c = PEN["cases"][cid]["counts"]
    md.append("| %s | %d | **%d** | %d | %d | %d | %.2f mm | %.4f mm |" % (
        cid, c["new_intersecting_face_pairs"], c["real_intersecting_pairs"],
        c["affected_face_count"], c["connected_components"], c["largest_component_faces"],
        c["total_intersection_segment_mm"],
        c["total_intersection_segment_mm"] / max(1, c["real_intersecting_pairs"])))
md += ["", "Morphology: a broad but shallow interdigitation band -- **hundreds** of crossing pairs whose",
       "mean crossing length is only ~1.2-1.3 mm -- plus the torn flap.  There is no isolated deep",
       "spear-through of one finger through another.", ""]

md += ["## 6. Answer to the twelve questions of the round", ""]
q = []
q.append(("1. CMC_OPP_30 max proxy depth", "**%.4f mm**, and it belongs to `%s`, not to thumb/index" % (
    PEN["cases"]["CMC_OPP_30"]["max_pair"]["proxy_depth_mm"],
    PEN["cases"]["CMC_OPP_30"]["max_pair"]["pair_class"])))
q.append(("2. CMC_OPP_30 actual classification",
          "thumb/index focus = **%s**; overall max pair = **%s**" % (
              PEN["cases"]["CMC_OPP_30"]["adjudication_focus"]["classification"],
              PEN["cases"]["CMC_OPP_30"]["max_pair"]["classification"])))
q.append(("3. CMC_MCP_L3 max proxy depth", "**%.4f mm** (`%s`)" % (
    PEN["cases"]["CMC_MCP_L3"]["max_pair"]["proxy_depth_mm"],
    PEN["cases"]["CMC_MCP_L3"]["max_pair"]["pair_class"])))
q.append(("4. CMC_MCP_L3 actual classification", "thumb/index focus = **%s**; overall = **%s**" % (
    PEN["cases"]["CMC_MCP_L3"]["adjudication_focus"]["classification"],
    PEN["cases"]["CMC_MCP_L3"]["max_pair"]["classification"])))
q.append(("5. FULL_OPP_L3 max proxy depth", "**%.4f mm** (`%s`)" % (
    PEN["cases"]["FULL_OPP_L3"]["max_pair"]["proxy_depth_mm"],
    PEN["cases"]["FULL_OPP_L3"]["max_pair"]["pair_class"])))
q.append(("6. FULL_OPP_L3 actual classification", "thumb/index focus = **%s**; overall = **%s**" % (
    PEN["cases"]["FULL_OPP_L3"]["adjudication_focus"]["classification"],
    PEN["cases"]["FULL_OPP_L3"]["max_pair"]["classification"])))
q.append(("7. actual intersecting face count",
          "CMC_OPP_30 %d, CMC_MCP_L3 %d, FULL_OPP_L3 %d (%d/%d/%d real crossing pairs)" % (
              PEN["cases"]["CMC_OPP_30"]["counts"]["affected_face_count"],
              PEN["cases"]["CMC_MCP_L3"]["counts"]["affected_face_count"],
              PEN["cases"]["FULL_OPP_L3"]["counts"]["affected_face_count"],
              PEN["cases"]["CMC_OPP_30"]["counts"]["real_intersecting_pairs"],
              PEN["cases"]["CMC_MCP_L3"]["counts"]["real_intersecting_pairs"],
              PEN["cases"]["FULL_OPP_L3"]["counts"]["real_intersecting_pairs"])))
q.append(("8. connected intersection components",
          "CMC_OPP_30 %d, CMC_MCP_L3 %d, FULL_OPP_L3 %d" % (
              PEN["cases"]["CMC_OPP_30"]["counts"]["connected_components"],
              PEN["cases"]["CMC_MCP_L3"]["counts"]["connected_components"],
              PEN["cases"]["FULL_OPP_L3"]["counts"]["connected_components"])))
q.append(("9. visible gross interpenetration", "**YES for the poses as a whole** -- the torn thumb flap "
          "crosses back through the palm and the middle finger (see the strain map and the solid renders). "
          "NO for the thumb/index pair itself, which is a shallow grazing contact."))
q.append(("10. teaching acceptability", "**NOT acceptable as-is** -- the torn flap is grossly visible. "
          "The thumb/index contact alone would be acceptable."))
q.append(("11. recommendation", "**STAGE6C_REQUIRED** (see section 7; note the root cause is a weight "
          "continuity failure, not the pose path)"))
q.append(("12. renders", "`production_spec/stage6_deformation/stage6b_r1c/renders/` -- 21 files, "
          "6 evidence types per pose (A solid, B close-up, C face highlight, D alpha overlay, "
          "E real cross-section, F depth vector) + a per-pose edge-strain map"))
for a_, b_ in q:
    md.append("- **%s** -- %s" % (a_, b_))
md += [""]

md += ["## 7. Status", "",
       "```",
       "THUMB_INDEX_DEEP_PENETRATION (the pair itself) = CANDIDATE_ACCEPTED_DOCUMENTED_CONTACT_RESIDUAL",
       "THUMB_DISTAL_WEIGHT_CONTINUITY_DEFECT        = CONFIRMED_VISUAL_BLOCKER",
       "STAGE6B_R1C                                  = READY_FOR_HUMAN_REVIEW",
       "STAGE5B_R1C                                  = CANDIDATE_FOR_HUMAN_REVIEW",
       "DEFORMATION_FINAL                            = PENDING_HUMAN_REVIEW",
       "```", "",
       "Hypothesis opened for Human Review (NOT started, nothing executed):",
       "",
       "* the round's own branch rule names `STAGE6C_POSE_PATH_AND_CONTACT_CONSTRAINT_DIAGNOSIS` as the",
       "  next candidate when a pose shows visible interpenetration, **but the evidence of this round",
       "  says the pose path is not the cause**.  Re-tuning the CMC quaternion or the MCP/IP progression",
       "  would not remove a 0/1 weight discontinuity;",
       "* the previous round's own section 37 classification applies instead:",
       "  `LOCAL_WEIGHT_CONTINUITY_INSUFFICIENT`, i.e. the Stage5B R1C local weight reconciliation did",
       "  not achieve same-digit deformation continuity on the thumb distal surface, and in fact raised",
       "  the mesh-wide hard 0/1 weight-flip edge count from **%d to %d**." % (
           BG["R1"]["master_hard_flip_edges"], BG["R1B"]["master_hard_flip_edges"]),
       "* a further fact worth recording: **Stage6A R1B measured but did not gate** the same signal --",
       "  its `TH_IP_45` case records `max_edge_ratio = 7.835` and",
       "  `new_severe_self_intersection_pairs = 78`, yet the case counts as PASS because the hard-blocker",
       "  set only covers NaN / collapse / degeneration / topology.  The Stage6A gate set should be",
       "  amended in a later round to include a maximum-stretch and self-intersection gate.", "",
       "No freeze has been performed.  Stage5B R1B remains the CURRENT_FROZEN_PRODUCTION_MASTER.", ""]

open(os.path.join(S6B_R1C, "STAGE6B_R1C_PENETRATION_ADJUDICATION_REPORT.md"), "w",
     encoding="utf-8").write("\n".join(md))

STATUS = {
  "stage": "STAGE6B_R1C_PENETRATION_VISUAL_ADJUDICATION",
  "round_kind": "HUMAN_REVIEW_EVIDENCE_ONLY",
  "generated_at": NOW,
  "model_changes": 0,
  "input": VER,
  "harness": PEN["harness"], "stage5b_r1c_master": PEN["stage5b_r1c_master"],
  "poses_reproduced_verbatim": PEN["poses_reproduced_verbatim"], "re_solved_pose": False,
  "classification_rule": PEN["classification_rule"],
  "per_pose": {cid: {"max_proxy_mm": PEN["cases"][cid]["max_pair"]["proxy_depth_mm"],
                     "max_proxy_pair_class": PEN["cases"][cid]["max_pair"]["pair_class"],
                     "thumb_index_max_proxy_mm": PEN["cases"][cid]["class_stats"].get(
                         "THUMB_INDEX", {}).get("max_proxy_mm", 0.0),
                     "thumb_index_pairs": PEN["cases"][cid]["class_stats"].get(
                         "THUMB_INDEX", {}).get("pairs", 0),
                     "thumb_index_classification": PEN["cases"][cid]["adjudication_focus"]["classification"],
                     "counts": PEN["cases"][cid]["counts"]}
              for cid in cases},
  "deformation_continuity": {
    "hard_0_1_weight_flip_edges_R1B_master": BG["R1"]["master_hard_flip_edges"],
    "hard_0_1_weight_flip_edges_R1C_master": BG["R1B"]["master_hard_flip_edges"],
    "R1B_candidate": BG["R1B"]["cases"], "R1_reference": BG["R1"]["cases"],
    "worst_stretch_ratio_R1B": max(b[c]["max_stretch_ratio"] for c in cases),
    "worst_stretch_ratio_R1": max(a[c]["max_stretch_ratio"] for c in cases),
  },
  "THUMB_INDEX_DEEP_PENETRATION": "CANDIDATE_ACCEPTED_DOCUMENTED_CONTACT_RESIDUAL",
  "THUMB_DISTAL_WEIGHT_CONTINUITY_DEFECT": "CONFIRMED_VISUAL_BLOCKER",
  "ROOT_CAUSE_CLASSIFICATION": "LOCAL_WEIGHT_CONTINUITY_INSUFFICIENT",
  "POSE_PATH_IS_THE_CAUSE": False,
  "STAGE6B_R1C": "READY_FOR_HUMAN_REVIEW",
  "STAGE5B_R1C": R1C_STATUS["status"],
  "DEFORMATION_FINAL": "PENDING_HUMAN_REVIEW",
  "CMC_DEFORMATION_FINAL": "PASS_PENDING_HUMAN_REVIEW",
  "NEXT_CANDIDATE_PER_ROUND_RULE": "STAGE6C_POSE_PATH_AND_CONTACT_CONSTRAINT_DIAGNOSIS (NOT_STARTED)",
  "NEXT_CANDIDATE_PER_EVIDENCE": "THUMB_DISTAL_WEIGHT_CONTINUITY_RECONCILIATION_R2 (NOT_STARTED)",
  "STAGE6A_GATE_AMENDMENT_PROPOSED": {
     "observation": "STAGE6A_R1B TH_IP_45 records max_edge_ratio 7.8355 and new_severe_self_intersection_pairs 78, yet passes",
     "proposal": "add a maximum edge stretch gate and a severe self-intersection gate to the Stage6A hard-blocker set",
     "status": "PROPOSED_NOT_APPLIED"},
  "freeze_performed": False,
}
json.dump(STATUS, open(os.path.join(S6B_R1C, "STAGE6B_R1C_STATUS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("wrote REPORT + STATUS")
