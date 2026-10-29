# STAGE4C_R2 -- build NAIL_AUDIT_R2 / ORIGIN_AUDIT_R2 / STAGE4C_R2_STATUS from the run log.
# R1 files are READ ONLY (and hash-recorded so the provenance claim is checkable).
import json, os, hashlib, datetime

B = "stage4c_r2"
R1D = "stage4c"
RUN = json.load(open(os.path.join(B, "STAGE4C_R2_RUN.json"), encoding="utf-8"))
R1_NAIL = json.load(open(os.path.join(R1D, "NAIL_AUDIT.json"), encoding="utf-8"))
R1_ORG = json.load(open(os.path.join(R1D, "ORIGIN_AUDIT.json"), encoding="utf-8"))
DIAG = json.load(open(os.path.join(B, "_tmp", "R1_SELECTOR_DIAGNOSIS.json"), encoding="utf-8"))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- NAIL_AUDIT_R2
g = RUN["gates"]
nail = {
    "stage": "STAGE4C_R2_CON_4_NAILS",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "revision_of": "STAGE4C_R1 (provenance, unmodified: sha256 %s)"
                  % sha(os.path.join(R1D, "RIGHT_HAND_ENGINEERING_STAGE4C_R1.blend")),
    "approach_unchanged": "per-face MATERIAL semantic (slot 1 = NAIL_BED); zero added geometry, "
                          "zero added tris.  R1's overall approach is retained -- the failure "
                          "was in the SELECTOR, not in material-only vs a nail mesh.",
    "why_material_only_still_stands": "the R1 hypothesis was re-tested rather than abandoned: "
                                      "once the selector gates on digit ownership, the distal "
                                      "phalanx domain and the dorsal facing, material-only "
                                      "produces a clean per-digit plate on every digit with 0 "
                                      "overlap and 0 leakage.  There is therefore no evidence "
                                      "that material-only cannot form a reasonable teaching "
                                      "semantic on this topology, which is the condition the "
                                      "brief sets for switching to a separate nail mesh.",
    "r1_defect": {
        "summary": "R1 had no digit-ownership gate and no distal-phalanx spatial domain gate; "
                   "it relied on a face-normal cone plus the axial position along the distal "
                   "bone.  Both are insufficient on this asset.",
        "measured_causes": [
            "adjacent finger nail normals are nearly parallel (index-middle %.2f deg, "
            "middle-ring %.2f deg, ring-little %.2f deg, index-ring %.2f deg), so R1's "
            "63.3 deg cone puts %d faces inside more than one digit's cone"
            % (DIAG["nail_normal_pair_angles_deg"]["index_vs_middle"],
               DIAG["nail_normal_pair_angles_deg"]["middle_vs_ring"],
               DIAG["nail_normal_pair_angles_deg"]["ring_vs_little"],
               DIAG["nail_normal_pair_angles_deg"]["index_vs_ring"],
               DIAG["faces_inside_more_than_one_cone"]),
            "with no ownership gate the sets overlap: 204 instances over only 155 unique "
            "faces = 49 duplicate assignments across 6 of the 10 digit pairs",
            "the axial test constrains only ONE coordinate, so faces at the finger ROOT still "
            "qualify: R1's union reaches %.2f mm from the nearest distal bone, with %d faces "
            "beyond 12 mm (p90 = %.2f mm) -- that is the pale band at the finger roots"
            % (DIAG["r1_union_distance_to_nearest_distal_bone_mm"]["max"],
               DIAG["r1_union_far_from_any_distal_bone"]["count"],
               DIAG["r1_union_distance_to_nearest_distal_bone_mm"]["p90"]),
            "%d of R1's union faces are in fact owned by a different digit"
            % DIAG["r1_union_owned_by_a_different_digit"]["count"],
        ],
        "diagnosis_file": "stage4c_r2/_tmp/R1_SELECTOR_DIAGNOSIS.json",
        "r1_selector_reproduced_exactly": DIAG["reconstruction_matches_r1"],
    },
    "r2_selector": {
        "gates": {
            "A_digit_ownership": "the face must belong to the owning digit.  Ownership is "
                                 "decided on the digit's FULL bone chain (meta+prox+distal), "
                                 "which is strictly stronger than the distal-segment-only test "
                                 "the brief names.  It has to be stronger: in this opposed RSSF "
                                 "pose the thumb's distal phalanx sits only ~9 mm from the "
                                 "INDEX knuckle, so a distal-segment rule alone would hand "
                                 "index-knuckle faces to the thumb.  The brief's literal "
                                 "distal-segment comparison is ALSO enforced as a gate.",
            "B_distal_domain": "axial inside [%.2f, %.2f] of the owning distal bone AND radial "
                               "offset inside the digit's own measured surface envelope AND on "
                               "the dorsal side AND in the outer %.0f%% of that envelope"
                               % (RUN["selector_parameters"]["AX_LO"],
                                  RUN["selector_parameters"]["AX_HI"],
                                  100 * (1 - RUN["selector_parameters"]["RADIAL_FRAC_MIN"])),
            "C_dorsal_facing": "face normal inside a %.2f cone (%.1f deg) of the owning digit's "
                               "nail normal -- tightened from R1's 0.45 because the neighbours' "
                               "nail normals are only ~13 deg apart"
                               % (RUN["selector_parameters"]["CONE_MIN"],
                                  __import__("math").degrees(
                                      __import__("math").acos(RUN["selector_parameters"]["CONE_MIN"]))),
            "web_guard": ">= %.0f mm from every other digit's distal bone"
                         % (RUN["selector_parameters"]["COMP_MIN_M"] * 1000),
        },
        "disjointness_is_structural": "every face has exactly one owner, so the five sets cannot "
                                      "intersect; the 10 pairwise intersections are still "
                                      "computed and reported as evidence",
        "envelope_radii_mm": RUN["envelopes_mm"],
        "specks": RUN["speck_removal"],
    },
    "gates_result": {
        "NAIL_FACE_SET_DISJOINT": g["NAIL_FACE_SET_DISJOINT"],
        "NAIL_FACE_OVERLAP_COUNT_TOTAL": g["NAIL_FACE_OVERLAP_COUNT_TOTAL"],
        "NAIL_FACE_OWNER_DISTANCE_TEST": g["NAIL_FACE_OWNER_DISTANCE_TEST"],
        "NAIL_FACE_OWNER_DISTANCE_VIOLATIONS": len(g["NAIL_FACE_OWNER_DISTANCE_VIOLATIONS"]),
        "NAIL_DISTAL_DOMAIN_TEST": g["NAIL_DISTAL_DOMAIN_TEST"],
        "NAIL_DISTAL_DOMAIN_VIOLATIONS": len(g["NAIL_DISTAL_DOMAIN_VIOLATIONS"]),
        "NAIL_PALMAR_LEAKAGE": g["NAIL_PALMAR_LEAKAGE"],
        "NAIL_WEBSPACE_LEAKAGE": g["NAIL_WEBSPACE_LEAKAGE"],
        "NAIL_FACES_FURTHER_THAN_12MM_FROM_ANY_DISTAL_BONE":
            g["NAIL_FACES_FURTHER_THAN_12MM_FROM_ANY_DISTAL_BONE"],
        "NAIL_CONNECTED_COMPONENTS_PER_DIGIT": g["NAIL_CONNECTED_COMPONENTS_PER_DIGIT"],
        "one_connected_component_per_digit": all(len(v) == 1
                                                 for v in g["NAIL_CONNECTED_COMPONENTS_PER_DIGIT"].values()),
    },
    "pairwise_intersections": g["pairwise_intersections"],
    "per_digit_faces": RUN["per_digit_faces"],
    "per_digit_stats": RUN["per_digit_stats"],
    "r1_vs_r2": {k: v for k, v in RUN["r1_vs_r2"].items()
                 if k in ("r1_instances", "r1_union", "r1_per_digit", "r2_per_digit",
                          "r2_instances", "r2_union")},
    "r1_vs_r2_face_delta": {k: {"count": len(v) if isinstance(v, list) else v, "faces": v[:40]}
                            for k, v in RUN["r1_vs_r2"].items()
                            if k.endswith("not_in_r1") or k.endswith("not_in_r2")
                            or k == "faces_retained"},
    "materials": RUN["materials"],
    "freeze": RUN["freeze_verification"],
    "r1_authority_correction": {
        "stale_field": "stage4c/NAIL_AUDIT.json -> nail_side_identifiable_on_all_five_digits",
        "why_invalid": "R1's per-digit face sets overlap (204 instances / 155 unique), so a face "
                       "could be counted as the nail of more than one digit.  A boolean that "
                       "ignores overlap cannot be a Human Review authority.",
        "replacement": "NAIL_AUDIT_R2.json -> gates_result (disjointness, overlap count, "
                       "ownership test, distal-domain test, leakage, components)",
        "r1_file_untouched": True,
    },
    "VERDICT": "PASS_PENDING_HUMAN_REVIEW"
             if g["NAIL_FACE_SET_DISJOINT"] and g["NAIL_FACE_OVERLAP_COUNT_TOTAL"] == 0
             and g["NAIL_PALMAR_LEAKAGE"] == 0 and g["NAIL_WEBSPACE_LEAKAGE"] == 0
             and g["NAIL_FACE_OWNER_DISTANCE_TEST"] and g["NAIL_DISTAL_DOMAIN_TEST"] else "FAIL",
}

# ---------------------------------------------------------------- ORIGIN_AUDIT_R2
rr = {}
for k in ("ORIGIN_BEFORE", "ORIGIN_AFTER", "WRIST_ORIGIN", "WORLD_GEOMETRY_DELTA_AFTER_ORIGIN",
          "float32_storage_epsilon_m", "world_geometry_delta_is_zero", "locator",
          "interior_minimum_at_z_mm", "interior_local_minima", "cut_plane_band_excluded_mm",
          "cut_plane_cap_hull_area_mm2", "stage4b_WRIST_R_head",
          "stage4b_WRIST_R_is_the_forearm_cut_plane",
          "stage4b_WRIST_R_z_equals_mesh_bbox_zmin", "mesh_bbox_zmin",
          "cross_file_verification", "P0_STYLE_FINDING", "ORIGIN_AFTER_minus_WRIST_ORIGIN_m"):
    rr[k] = R1_ORG[k]

org = dict(rr)
org.update({
    "stage": "STAGE4C_R2_CON_6_ORIGIN",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "revision_of": "STAGE4C_R1 (provenance, unmodified)",
    "origin_recomputed": False,
    "origin_unchanged_reason": "R2 did not re-search the origin.  The R1 value is neither "
                               "challenged by new evidence nor touched by this revision, and "
                               "stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend was saved "
                               "with an origin delta of exactly 0.0 m against R1.",
    "origin_verified_in_r2_master": {
        "origin": [1.408704638, 0.022395039, 0.335847497],
        "origin_delta_vs_r1_m": RUN["freeze_verification"]["origin_delta_m"],
        "matches_R1_WRIST_ORIGIN": RUN["freeze_verification"]["origin_delta_m"] == 0.0,
    },
    "ERRATA": {
        "errata_id": "STAGE4C_R1_ORIGIN_STAGE3_DELTA_WORDING",
        "status": "CORRECTED IN R2 (R1 files left untouched as provenance)",
        "correct_numeric_relationship":
            "the R2/R1 wrist locator lands at z = %.2f mm; the Stage-3 accepted wrist level is "
            "z = 343.00 mm; the DIFFERENCE is %.2f mm (same basin, not a reproduction)."
            % (R1_ORG["interior_minimum_at_z_mm"], R1_ORG["delta_to_stage3_mm"]),
        "stale_strings_in_r1": [
            {"file": "stage4c/ORIGIN_AUDIT.json", "field": "note",
             "text": "...The locator used here independently reproduces the already-accepted "
                     "Stage-3 wrist level to <1 mm.",
             "problem": "contradicts delta_to_stage3_mm = 7.23 in the SAME file"},
            {"file": "stage4c/ORIGIN_AUDIT.json",
             "field": "reproduces_stage3_wrist_narrowest_z",
             "text": "field NAME implies agreement; its value 0.343 is the Stage-3 LEVEL, not "
                     "the achieved agreement",
             "problem": "misleading field name next to delta_to_stage3_mm = 7.23"},
            {"file": "stage4c/STAGE4C_RUN.json", "field": "CON_6_origin.note",
             "text": "same '<1 mm' sentence", "problem": "same contradiction"},
        ],
        "corrected_statement": "difference to the Stage-3 accepted wrist level = %.2f mm "
                               "(the same anatomical basin; the two locators are independent "
                               "methods and do NOT agree to sub-millimetre)"
                               % R1_ORG["delta_to_stage3_mm"],
        "r1_files_modified": False,
        "r1_file_hashes": {p: sha(os.path.join(R1D, p)) for p in
                           ("ORIGIN_AUDIT.json", "NAIL_AUDIT.json", "STAGE4C_STATUS.json",
                            "STAGE4C_RUN.json", "RIGHT_HAND_ENGINEERING_STAGE4C_R1.blend")},
    },
    "stage4b_finding_carried_forward": {
        "id": "STAGE4B_WRIST_R_LOCATOR_DEFECT",
        "status": "OPEN -- FOR STAGE 5",
        "statement": "the Stage-4B skeleton's WRIST_R sits on the forearm cut plane (z = "
                     "0.277349 m = mesh bbox z-min 0.276016 m; the Stage-4B log itself reports "
                     "'narrowest cross-section at -1.9 mm from the forearm cap'), which makes "
                     "its wrist->palm bone 201 mm instead of an anatomical ~65-90 mm.",
        "binding_on_stage5": "STAGE 5 MUST NOT INHERIT THE STAGE-4B WRIST_R POSITION.  Use the "
                             "R2 origin [1.408704638, 0.022395039, 0.335847497] or re-derive "
                             "the wrist with the documented radius-limited interior-minimum "
                             "locator.",
        "does_not_affect": "the Stage-4B RSSF joint-angle validation, which is measured entirely "
                           "on the fingers.",
    },
    "evidence_renders": ["stage4c_r2/renders/STAGE4C_R2_ORIGIN_SIDE.png",
                         "stage4c_r2/renders/STAGE4C_R2_ORIGIN_DORSAL_OBLIQUE.png"],
    "VERDICT": "PASS_PENDING_HUMAN_REVIEW",
})

# ---------------------------------------------------------------- STATUS
status = {
    "stage": "STAGE4C_R2_NAIL_SELECTOR_AND_ORIGIN_EVIDENCE_CORRECTION",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "output_blend": RUN["output"],
    "r1_provenance": RUN["r1_input"],
    "joint_frame": RUN["joint_frame"],
    "tris": {"HAND_BASE_TRIS": RUN["freeze_verification"]["TOTAL_RIGHT_HAND_TRIS"],
             "NAIL_ADDED_TRIS": 0,
             "TOTAL_RIGHT_HAND_TRIS": RUN["freeze_verification"]["TOTAL_RIGHT_HAND_TRIS"],
             "target": "8k-20k", "hard_ceiling": 30000},
    "freeze_verification": RUN["freeze_verification"],
    "VERDICT": {
        "STAGE4C_R2": "READY_FOR_HUMAN_REVIEW",
        "CON_4_NAILS": nail["VERDICT"],
        "CON_5_RSSF_REPOSE": "CARRY_FORWARD_UNCHANGED_PASS",
        "CON_6_ORIGIN": "PASS_PENDING_HUMAN_REVIEW",
        "CON_7_UV": "CARRY_FORWARD_PASS",
        "CANONICAL_HAND_POSE": "RSSF",
        "HAND_BASE_TOPOLOGY": "UNCHANGED",
        "CMC_DEFORMATION_FINAL": "PENDING_STAGE6",
        "PRODUCTION_RIG": "NOT_STARTED",
        "STAGE5": "NOT_STARTED",
        "STAGE4C_R1": "SUPERSEDED_FOR_CON_4 (retained as provenance)",
    },
    "open_findings_for_human_review": [
        "STAGE4B_WRIST_R_LOCATOR_DEFECT (OPEN, binding on Stage 5) -- see ORIGIN_AUDIT_R2.json",
        "STAGE4C_R1_ORIGIN_STAGE3_DELTA_WORDING (CLOSED by errata) -- R1 files left untouched",
    ],
}
json.dump(nail, open(os.path.join(B, "NAIL_AUDIT_R2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(org, open(os.path.join(B, "ORIGIN_AUDIT_R2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(status, open(os.path.join(B, "STAGE4C_R2_STATUS.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("WROTE NAIL_AUDIT_R2.json ORIGIN_AUDIT_R2.json STAGE4C_R2_STATUS.json")
print("CON_4:", nail["VERDICT"], "| CON_6:", org["VERDICT"])
print(json.dumps(status["VERDICT"], ensure_ascii=False, indent=1))
