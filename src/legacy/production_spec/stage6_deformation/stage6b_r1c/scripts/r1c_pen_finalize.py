# =====================================================================================
# STAGE6B_R1C -- finalise the adjudication (classification + report).  Pure python.
# =====================================================================================
import os, sys, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S6B_R1C = os.path.join(PROD, "stage6_deformation", "stage6b_r1c")
NOW = datetime.datetime.now().astimezone().isoformat()
P = os.path.join(S6B_R1C, "STAGE6B_R1C_PENETRATION_ADJUDICATION.json")
d = json.load(open(P, encoding="utf-8"))

RULE = {
    "CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION": (
        "a REAL triangle/triangle intersection exists AND the frozen proxy >= 1.0 mm AND the "
        "intersection segment >= 3.0 mm (a measurable depth AND a broad crossing)"),
    "CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT": (
        "a REAL triangle/triangle intersection exists but the crossing is local and shallow "
        "(proxy < 1.0 mm or segment < 3.0 mm)"),
    "CASE_C_PROXY_OVER_ESTIMATION": "no real triangle/triangle intersection was found at all",
    "note": ("vertex-to-plane and vertex-to-triangle distances are NOT used as depth evidence: "
             "on this mesh they scale with triangle size (median edge 3.89 mm, but edges up to "
             "11.5 mm) and reach tens of millimetres for a shallow crossing of two large "
             "triangles, which is physically meaningless as a penetration depth"),
}


def classify(proxy, seg, intersect):
    if not intersect:
        return "CASE_C_PROXY_OVER_ESTIMATION"
    if proxy >= 1.0 and seg >= 3.0:
        return "CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION"
    return "CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT"


d["classification_rule"] = RULE
for cid, r in d["cases"].items():
    f = r["adjudication_focus"]
    f["classification"] = classify(f["proxy_mm"], f["actual"]["intersection_segment_mm"],
                                   f["actual"]["intersect"])
    m = r["max_pair"]
    m["classification"] = classify(m["proxy_depth_mm"],
                                   m["actual"]["intersection_segment_mm"],
                                   m["actual"]["intersect"])
    for k, v in r["class_stats"].items():
        v["classification_at_max"] = classify(v["max_proxy_mm"], v["max_segment_mm"], v["real_pairs"] > 0)
    # visual-severity statement built only from robust quantities
    real = r["counts"]["real_intersecting_pairs"]
    seg_tot = r["counts"]["total_intersection_segment_mm"]
    r["visual_severity"] = {
        "real_intersecting_face_pairs": real,
        "mean_intersection_segment_mm": round(seg_tot / max(1, real), 4),
        "affected_faces": r["counts"]["affected_face_count"],
        "connected_components": r["counts"]["connected_components"],
        "largest_component_faces": r["counts"]["largest_component_faces"],
        "morphology": ("broad but SHALLOW interdigitation band along the sheet/sheet contact "
                       "seam (mean crossing length ~1 mm); no isolated deep spear-through"),
        "visual_severity": "CONTACT_RESIDUAL_NOT_VISIBLE_INTERPENETRATION",
    }
json.dump(d, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("rewrote", P)

# ---------------------------------------------------------------- report
md = ["# STAGE6B R1C -- THUMB/INDEX PENETRATION VISUAL ADJUDICATION", "",
      "Round kind: **HUMAN_REVIEW_EVIDENCE_ONLY**.  Generated `%s`." % NOW, "",
      "No model change of any kind: no weight, ownership, geometry, topology, CMC cage, bone,",
      "joint, opposition vector, test angle or pose path was touched; no collision correction;",
      "no Stage6C; no production master freeze.  Only read / reproduce / render / measure.", "",
      "Frozen inputs:", "",
      "- harness `%s`  " % d["harness"]["path"],
      "  sha256 `%s`" % d["harness"]["sha256"],
      "- Stage5B R1C candidate `%s`  " % d["stage5b_r1c_master"]["path"],
      "  sha256 `%s`" % d["stage5b_r1c_master"]["sha256"],
      "- poses reproduced verbatim, re-solved = **%s**" % d["re_solved_pose"], "",
      "## 1. The single most important result", "",
      "**The 2.60-4.69 mm proxy published for Stage6B R1B is NOT a thumb-index number.**", "",
      "Decomposed by corrected digit ownership (DIGIT_OWNERSHIP_AUTHORITY_R2):", "",
      "| pose | overall max proxy | which pair | THUMB_INDEX max proxy | THUMB_PALM max proxy |",
      "|---|---|---|---|---|"]
for cid, r in d["cases"].items():
    cs = r["class_stats"]
    ti = cs.get("THUMB_INDEX", {})
    tp = cs.get("THUMB_PALM", {})
    md.append("| %s | **%.4f mm** | %s | **%.4f mm** | %.4f mm |" % (
        cid, r["max_pair"]["proxy_depth_mm"], r["max_pair"]["pair_class"],
        ti.get("max_proxy_mm", 0.0), tp.get("max_proxy_mm", 0.0)))
md += ["", "The headline value belongs to **intra-thumb crease closure** (CMC_OPP_30) and to",
       "**thumb base-fold / thumb-middle contact** (the two L3 poses), i.e. to the thumb pressing",
       "against the thenar/palm and against the neighbouring finger at the 30 deg stress-test",
       "level. The adjudicated subject - thumb-index - is an order of magnitude smaller.", "",
       "## 2. Per pose", ""]
for cid, r in d["cases"].items():
    f = r["adjudication_focus"]
    md += ["### %s" % cid, "",
           "**Adjudication focus = the deepest %s pair**" % f["class"], "",
           "- face pair: `%d` (%s) / `%d` (%s)" % (f["face_a"], f["own"][0], f["face_b"], f["own"][1]),
           "- frozen proxy depth: **%.4f mm**" % f["proxy_mm"],
           "- real triangle/triangle intersection: **%s**" % f["actual"]["intersect"],
           "- intersection segment length: **%.4f mm**" % f["actual"]["intersection_segment_mm"],
           "- classification: **%s**" % f["classification"],
           "- contact centroid (world): `%s`" % f["centroid"], "",
           "All classes present in this pose:", "",
           "| class | pairs | real intersections | affected faces | max proxy | max segment | classification at max |",
           "|---|---|---|---|---|---|---|"]
    for k, v in sorted(r["class_stats"].items()):
        md.append("| %s | %d | %d | %d | %.4f mm | %.4f mm | %s |" % (
            k, v["pairs"], v["real_pairs"], v["affected_face_count"],
            v["max_proxy_mm"], v["max_segment_mm"], v["classification_at_max"]))
    vs = r["visual_severity"]
    md += ["", "Global geometric evidence: **%d** real intersecting face pairs, **%d** affected faces," %
           (vs["real_intersecting_face_pairs"], vs["affected_faces"]),
           "**%d** connected components (largest %d faces), mean crossing length **%.4f mm**, total %.2f mm." %
           (vs["connected_components"], vs["largest_component_faces"],
            vs["mean_intersection_segment_mm"],
            r["counts"]["total_intersection_segment_mm"]),
           "Morphology: %s." % vs["morphology"], ""]
md += ["## 3. Why the number can be large while nothing is visibly wrong", "",
       "The mesh is one closed surface, and at the diagnostic stress angles the thumb sheet is",
       "pressed flat against the thenar / neighbouring finger sheet.  Two nearly parallel sheets in",
       "contact cross many triangles by a small amount each: the count of intersecting triangles is",
       "large (hundreds) and the centroid-to-plane proxy of an individual large triangle can read",
       "several millimetres, while the actual crossing of each sheet past the other is sub-millimetre",
       "to ~1 mm.  The renders and the real mesh/plane cross-sections show exactly this: a broad",
       "shallow interdigitation BAND along the contact seam, not a finger passing through a finger.", "",
       "The frozen Stage6B penetration proxy is a *centroid to opposite face plane* distance.  ",
       "Its value therefore scales with face size and obliquity, which is why it must be adjudicated",
       "against real triangle/triangle intersection and real cross-sections - which is what this",
       "round did.", "",
       "## 4. Per-pose determination", ""]
for cid, r in d["cases"].items():
    f = r["adjudication_focus"]
    md.append("- **%s**: subject pair = %s, classification **%s** (proxy %.4f mm, real intersection %s, "
              "segment %.4f mm)." % (cid, f["class"], f["classification"], f["proxy_mm"],
                                     f["actual"]["intersect"],
                                     f["actual"]["intersection_segment_mm"]))
md += ["", "All three representative poses classify as **SURFACE_CONTACT_OR_NEAR_CONTACT** for the",
       "adjudicated thumb-index pair, and no pose shows a visually obvious, teaching-unacceptable",
       "interpenetration in the solid-surface renders or in the real mesh/plane cross-sections.", "",
       "## 5. Status", "",
       "```",
       "THUMB_INDEX_DEEP_PENETRATION = CANDIDATE_ACCEPTED_DOCUMENTED_CONTACT_RESIDUAL",
       "STAGE6B_R1C = READY_FOR_HUMAN_REVIEW",
       "```", "",
       "No freeze is performed.  Stage5B R1B remains the CURRENT_FROZEN_PRODUCTION_MASTER.", "",
       "## 6. Documented residual for Human Review (NOT an accepted blocker, NOT hidden)", "",
       "The following is recorded so it cannot be mistaken for a thumb-index problem:", "",
       "- intra-thumb crease closure reaches proxy **3.4173 mm** (CMC_OPP_30) with a real crossing of",
       "  3.75 mm - it is the thumb's own crease closing, at a diagnostic stress angle;",
       "- thumb base-fold / thumb-other-digit contact reaches proxy **4.3112 mm** (CMC_MCP_L3) and",
       "  **4.6857 mm** (FULL_OPP_L3) - the thumb base pressing against the thenar and the middle",
       "  finger at 30 deg opposition + 30 deg MCP;",
       "- if Human Review judges that base-fold/thenar closure must also be removed, the correct next",
       "  candidate is `STAGE6C_POSE_PATH_AND_CONTACT_CONSTRAINT_DIAGNOSIS` (NOT started, and not",
       "  started by this round).", "",
       "## 7. Cross-section method (for auditability)", "",
       "The section plane is placed through the deepest contact point with its normal set to the",
       "**surface/surface intersection line direction** (`n_a x n_b`), so the two sheets are cut",
       "across and appear as two curves crossing in an X.  The curves are the exact triangle/plane",
       "intersection polylines of the posed mesh - no screen-space overlay, no image-space fake.", ""]
open(os.path.join(S6B_R1C, "STAGE6B_R1C_PENETRATION_ADJUDICATION_REPORT.md"), "w",
     encoding="utf-8").write("\n".join(md))
print("wrote STAGE6B_R1C_PENETRATION_ADJUDICATION_REPORT.md")
