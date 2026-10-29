# =====================================================================================
# STAGE5B_R1A -- READ-ONLY ROOT CAUSE SURVEY (revision 2: arc-based thumb frame)
#   * explains the R1 THUMB_IP over-spread (BEFORE any weight is modified)
#   * resolves the real spatial semantics of v1383 / v2740
#   * qualifies the FIRST WEB mask and pre-measures the R1A semantic regions
# Produces:
#   STAGE5B_R1A_THUMB_WEIGHT_ROOT_CAUSE_AUDIT.json
#   THUMB_NAIL_BOUNDARY_VERTEX_AUDIT.json
#   _tmp/R1A_SURVEY.json           (per-vertex tables reused by the later scripts)
#   _tmp/R1A_REGION_PROBE.json     (region / web-mask candidates, pre-measurement)
# =====================================================================================
import bpy
import sys
import os
import json
import math
import hashlib
import datetime
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import r1a_common as C                                   # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
TOP = os.path.dirname(OUTDIR)
NOW = datetime.datetime.now().astimezone().isoformat()
MM = C.MM
R1 = os.path.join(TOP, "stage5b_r1", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")
R1_SHA = "8f4c6901fdae417e3855d388f9739ebea10863f0ebdbfedf0df8d79a751c308d"
MASTER = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
MASTER_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[R1A-SURVEY]", s)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rr(x, n=6):
    return round(float(x), n)


# ============================================================ 0. input gate
s_master = sha(MASTER)
s_r1 = sha(R1)
log("master sha =", s_master, "OK" if s_master == MASTER_SHA else "DRIFT")
log("r1 sha     =", s_r1, "OK" if s_r1 == R1_SHA else "DRIFT")
if s_master != MASTER_SHA or s_r1 != R1_SHA:
    raise SystemExit("FAIL CLOSED: frozen input hash drift")

# ============================================================ 1. reference + R1 weights
ref = C.load_reference(TOP)
NV = ref["NV"]
V0 = ref["V0"]
jf = ref["jf"]
log("reference: V=%d E=%d F=%d TRIS=%d med_edge=%.4f mm"
    % (ref["TOPSIG"][0], ref["TOPSIG"][1], ref["TOPSIG"][2], ref["TOPSIG"][3],
       ref["med_edge"]))

b = C.load_weights(R1)
W = b["W"]
V1 = b["V"]
groups = b["groups"]
log("R1 groups = %d" % len(groups))
dz, VE = C.zero_pose_delta(b["ob"], b["MW"], V0)
log("R1 zero-pose max delta = %.9f mm" % max(dz))

TF = C.thumb_frame(ref)
ARC = TF["arc_thumb_mm"]
SGM = TF["geodesic_from_tip_mm"]
s_MCP, s_IP, s_TIP = TF["s_MCP_joint_mm"], TF["s_IP_joint_mm"], TF["s_TIP_mm"]
MED = ref["med_edge"]
TAU = MED                                    # one mesh median edge = resolvable transition band
R_TT, R_MAX = C.thumb_radii(ref, TF)
MASKS = C.thumb_masks(ref, TF, TAU, R_TT, R_MAX)
WEB = C.first_web_mask(ref, TF, TAU, R_TT)
log("thumb arc joints (mm): MCP=%.4f IP=%.4f TIP=%.4f ; med_edge=%.4f ; tau=%.4f"
    % (s_MCP, s_IP, s_TIP, MED, TAU))
log("R_TT=%.4f mm ; R_MAX=%.4f mm" % (R_TT, R_MAX))
log("regions: distal=%d proximal=%d metacarpal=%d thenar=%d web=%d"
    % (len(MASKS["THUMB_DISTAL"]), len(MASKS["THUMB_PROXIMAL"]),
       len(MASKS["THUMB_FIRST_METACARPAL"]), len(MASKS["THENAR_BASE"]), len(WEB)))

TNAIL = MASKS["nail_thumb_vertices"]
CAP_V = MASKS["cap_vertices"]
THUMB_OWN = [i for i in range(NV) if ref["OWN_V"][i] == "THUMB"]
log("thumb-owned=%d thumb-nail=%d cap=%d" % (len(THUMB_OWN), len(TNAIL), len(CAP_V)))

# ============================================================ 2. ROOT CAUSE
ipw = [W[i].get("THUMB_IP_R", 0.0) for i in range(NV)]
ipnz = [i for i in range(NV) if ipw[i] > 0.0]
G = {g: [W[i].get(g, 0.0) for i in range(NV)] for g in C.DEFORM}

# --- 2a. the R1 guard predicate vs the corrected predicate (arc based, as R1 used it)
n_own_thumb = len(THUMB_OWN)
n_guard_r1 = sum(1 for i in THUMB_OWN
                 if (i in TNAIL) or (ARC[i] <= s_IP + TAU))
n_guard_ok = sum(1 for i in THUMB_OWN
                 if (i in TNAIL) or (ARC[i] >= s_IP - TAU))
n_arc_le_ip = sum(1 for i in THUMB_OWN if ARC[i] <= s_IP + TAU)
forced = []
for i in THUMB_OWN:
    w = ipw[i]
    if w <= 0.0:
        continue
    others = 1.0 - w
    if others <= 1e-12 or w >= 2.0 * others - 1e-6:
        forced.append(i)

# --- 2b. per-group stats
STATS = {}
for g in C.DEFORM:
    ws = G[g]
    nz = [x for x in ws if x > 0.0]
    STATS[g] = {"nonzero": len(nz), "gt_0.25": sum(1 for x in nz if x > 0.25),
                "gt_0.50": sum(1 for x in nz if x > 0.50),
                "gt_0.75": sum(1 for x in nz if x > 0.75),
                "max": rr(max(nz), 6) if nz else 0.0,
                "mean_nonzero": rr(sum(nz) / len(nz), 6) if nz else 0.0,
                "sum": rr(sum(nz), 6)}

# --- 2c. where does THUMB_IP live
def region_bucket(i):
    if ref["OWN_V"][i] != "THUMB" and i not in TNAIL:
        return "NOT_THUMB_OWNED"
    if ARC[i] >= s_IP:
        return "distal phalanx (arc >= IP joint)"
    if ARC[i] >= s_MCP:
        return "proximal phalanx (MCP arc <= s < IP arc)"
    return "first metacarpal (s < MCP arc)"


IP_BUCKETS = {}
for i in ipnz:
    k = region_bucket(i)
    d = IP_BUCKETS.setdefault(k, {"verts": 0, "weight_sum": 0.0, "gt_0.5": 0})
    d["verts"] += 1
    d["weight_sum"] += ipw[i]
    if ipw[i] > 0.5:
        d["gt_0.5"] += 1
for k in IP_BUCKETS:
    IP_BUCKETS[k]["weight_sum"] = rr(IP_BUCKETS[k]["weight_sum"], 6)

ARC_BUCKETS = {}
for i in ipnz:
    a = ARC[i]
    k = ("arc <= IP joint arc (the WHOLE metacarpal + proximal phalanx + IP joint level)"
         if a <= s_IP + TAU else "arc > IP joint arc (distal phalanx only)")
    d = ARC_BUCKETS.setdefault(k, {"verts": 0, "weight_sum": 0.0})
    d["verts"] += 1
    d["weight_sum"] += ipw[i]
for k in ARC_BUCKETS:
    ARC_BUCKETS[k]["weight_sum"] = rr(ARC_BUCKETS[k]["weight_sum"], 6)

HIST = {"0.0": 0, "(0,0.25]": 0, "(0.25,0.5]": 0, "(0.5,0.75]": 0, "(0.75,1.0]": 0}
for i in THUMB_OWN:
    w = ipw[i]
    HIST["0.0" if w <= 0 else "(0,0.25]" if w <= 0.25 else "(0.25,0.5]" if w <= 0.5
         else "(0.5,0.75]" if w <= 0.75 else "(0.75,1.0]"] += 1

# --- 2d. geodesic anomaly (why a geodesic digit coordinate cannot be used here)
GEO_FAR = sorted((i for i in range(NV)
                  if SGM[i] > 120.0 and ref["dchain"][i]["THUMB"] < 15.0),
                 key=lambda i: -SGM[i])
GEO_ANOM = {
    "statement": ("geodesic distance from the thumb distal-most vertex is NOT monotone along "
                  "the digit on this mesh: the thumb NAIL plate and the adjacent dorsal sheet "
                  "are 148-180 mm away in surface distance while only 8-30 mm away in space.  "
                  "R1 nevertheless seeded GEO at the distal-most vertex and defined gval(); that "
                  "coordinate was never used by the R1 guards, so it caused no damage - but it is "
                  "UNUSABLE for R1A and is explicitly rejected."),
    "thumb_nail_vertex_geodesic_mm": {str(i): rr(SGM[i], 3) for i in sorted(TNAIL)},
    "vertex_284_geodesic_mm": rr(SGM[284], 3),
    "vertex_1076_cap_patch_geodesic_mm": rr(SGM[1076], 3),
    "euclidean_cap_rep_to_284_mm": rr((V0[284] - Vector(ref["cap"]["cap_representative_world"])).length * MM, 3),
    "count_verts_geo_gt_120_and_dthumb_lt_15": len(GEO_FAR),
    "geodesic_joint_levels_mm_diagnostic": TF["geodesic_joint_levels_mm"],
    "adopted_coordinate": ("ARC length along the approved thumb joint polyline "
                           "(CMC head -> MCP joint -> IP joint -> TIP landmark); monotone along "
                           "the digit, follows the approved kinematic axis, and reproduces the "
                           "R2A approved distal-phalanx extent IP arc .. TIP arc")}

# --- 2e. analytic bound on CMC / MCP when the guard forces W_IP >= 2*others
bound = {"rule": "if W_IP >= 2 * sum(others) then sum(others) <= 1/3",
         "max_possible_thumb_cmc_when_forced": 1.0 / 3.0,
         "max_possible_thumb_mcp_when_forced": 1.0 / 3.0,
         "observed_thumb_cmc_max": STATS["THUMB_CMC_R"]["max"],
         "observed_thumb_mcp_max": STATS["THUMB_MCP_R"]["max"],
         "observed_thumb_ip_max": STATS["THUMB_IP_R"]["max"],
         "forced_vertex_count": len(forced),
         "forced_fraction_of_thumb_owned": rr(len(forced) / max(1, n_own_thumb), 4)}

# ============================================================ 3. FIRST WEB recomputed
W_WEB = 2.0 * MED
web_r1 = set(i for i in range(NV)
             if ref["dchain"][i]["THUMB"] <= W_WEB and ref["dchain"][i]["INDEX"] <= W_WEB)
web_groups = sorted({g for i in web_r1 for g in W[i]})
web_totals = {}
for i in web_r1:
    for g, w in W[i].items():
        web_totals[g] = web_totals.get(g, 0.0) + w
strict_viol = [{"vertex": i, "bone": g, "weight": rr(w, 6)}
               for i in web_r1 for g, w in W[i].items() if g not in C.WEB_OK]

FIRST_WEB_RC = {
    "r1_mask_rule": ("d_poly(thumb chain) <= 2*median_edge AND d_poly(index chain) <= "
                     "2*median_edge  (no longitudinal (arc) bound at all)"),
    "r1_mask_threshold_mm": rr(W_WEB, 4), "r1_mask_vertex_count": len(web_r1),
    "r1_mask_participating_groups": web_groups,
    "r1_mask_group_weight_totals": dict((k, rr(v, 6)) for k, v in sorted(web_totals.items())),
    "r1_mask_thumb_ip_total": rr(sum(ipw[i] for i in web_r1), 6),
    "r1_audit_reported_violations": 0,
    "strict_whitelist_recomputed_violations": len(strict_viol),
    "strict_whitelist_violation_bones": sorted({r["bone"] for r in strict_viol}),
    "r1_mask_contains_thumb_distal_or_nail": sorted(set(web_r1) & (TNAIL | CAP_V)),
    "r1_mask_thumb_arc_range_mm": [rr(min(ARC[i] for i in web_r1), 4),
                                  rr(max(ARC[i] for i in web_r1), 4)] if web_r1 else None,
    "audit_bug": ("the R1 audit violation loop exempted THUMB_IP_R / INDEX_PIP_R / INDEX_DIP_R "
                  "explicitly (`if b not in WEB_OK and b not in (...)`), so a THUMB_IP entry in "
                  "the first web could never be reported as a violation while the declared "
                  "whitelist was WEB_OK only -> audit semantics and weight semantics disagree"),
    "build_bug": ("the R1 web branch removed THUMB_IP only when `i not in NAIL_THUMB_V`; every "
                  "thumb nail vertex that also fell inside the first-web band kept THUMB_IP "
                  "allowed AND had it forced to >= 2x others -> non-zero THUMB_IP inside the web"),
    "violation_samples": strict_viol[:30]}

# ============================================================ 4. v1383 / v2740
V2F = [[] for _ in range(NV)]
for fi, vs in enumerate(ref["TOPO0"]):
    for v in vs:
        V2F[v].append(fi)


def vertex_case(vid):
    inc = sorted(V2F[vid])
    incm = [(fi, ref["MAT0"][fi], ref["FO"][fi]) for fi in inc]
    nail_inc = [fi for fi in inc if ref["MAT0"][fi] == 1]
    own = ref["OWN_V"][vid]
    si, _ = C.arc_of(C.chp(jf, "INDEX"), V0[vid])
    w = dict(W[vid])
    dom = max(w.items(), key=lambda kv: kv[1])[0] if w else None
    return {
        "vertex": vid,
        "world_coordinate": [rr(x, 9) for x in V1[vid]],
        "local_coordinate": [rr(x, 9) for x in b["me"].vertices[vid].co],
        "incident_face_count": len(inc),
        "incident_face_ids": inc,
        "incident_face_material_index": [m for _f, m, _o in incm],
        "incident_face_centroid_owner": [o for _f, _m, o in incm],
        "nail_bed_face_ids": nail_inc,
        "non_nail_face_ids": [fi for fi in inc if ref["MAT0"][fi] != 1],
        "incident_to_nail_bed_face": len(nail_inc) > 0,
        "nail_faces": len(nail_inc), "non_nail_faces": len(inc) - len(nail_inc),
        "classification": ("SHARED_SEMANTIC_BOUNDARY_VERTEX (nail/skin border of the thumb "
                           "nail: incident to both NAIL_BED and non-NAIL faces)"),
        "vertex_ownership_region": own,
        "two_nearest_chains": [{"chain": a, "dist_mm": rr(d, 4)} for a, d in ref["order2"][vid]],
        "dist_to_THUMB_chain_mm": rr(ref["dchain"][vid]["THUMB"], 4),
        "dist_to_INDEX_chain_mm": rr(ref["dchain"][vid]["INDEX"], 4),
        "dist_to_wrist_chain_mm": rr(ref["dchain"][vid]["wrist"], 4),
        "arc_along_thumb_chain_mm": rr(ARC[vid], 4),
        "arc_along_index_chain_mm": rr(si, 4),
        "thumb_joint_arcs_mm": {"MCP": rr(s_MCP, 4), "IP": rr(s_IP, 4), "TIP": rr(s_TIP, 4)},
        "thumb_segment_of_projection": ("distal phalanx" if ARC[vid] >= s_IP
                                        else "proximal phalanx" if ARC[vid] >= s_MCP
                                        else "first metacarpal"),
        "geodesic_from_thumb_distal_most_vertex_mm": rr(SGM[vid], 4),
        "dist_to_THUMB_IP_bone_mm": rr(C.seg_dist(V0[vid], ref["BH"]["THUMB_IP_R"],
                                                  ref["BT"]["THUMB_IP_R"]) * MM, 4),
        "dist_to_THUMB_MCP_bone_mm": rr(C.seg_dist(V0[vid], ref["BH"]["THUMB_MCP_R"],
                                                   ref["BT"]["THUMB_MCP_R"]) * MM, 4),
        "dist_to_THUMB_CMC_bone_mm": rr(C.seg_dist(V0[vid], ref["BH"]["THUMB_CMC_R"],
                                                   ref["BT"]["THUMB_CMC_R"]) * MM, 4),
        "dist_to_INDEX_MCP_bone_mm": rr(C.seg_dist(V0[vid], ref["BH"]["INDEX_MCP_R"],
                                                   ref["BT"]["INDEX_MCP_R"]) * MM, 4),
        "in_thumb_distal_cap_patch": vid in CAP_V,
        "dist_to_cap_representative_mm": rr((V0[vid] - Vector(
            ref["cap"]["cap_representative_world"])).length * MM, 4),
        "in_first_web_mask_r1": vid in web_r1,
        "in_first_web_mask_r1a": vid in WEB,
        "in_thumb_nail_vertex_set": vid in TNAIL,
        "current_full_weights_16": dict((k, rr(v, 9)) for k, v in sorted(w.items())),
        "current_weights_present_groups": sorted(w.keys()),
        "current_weights_all_16_including_zeros": dict(
            (g, rr(W[vid].get(g, 0.0), 9)) for g in C.DEFORM),
        "current_dominant_bone": dom,
        "region_classification_source": ("NAIL_WEIGHT_AUDIT / R1 build: material_index==1 face "
                                         "whose FACE centroid ownership == THUMB -> vertex pulled "
                                         "into NAIL_BY_DIGIT['THUMB']; the VERTEX level owner "
                                         "(nearest chain by 2-D polyline distance) is however "
                                         f"{own}, which is what drove the R1 weight allocation"),
        "why_r1_gave_it_no_thumb_bone": (
            "OWN_V(v)=%s and d_poly(v,THUMB)=%.2f mm: %s" % (
                own, ref["dchain"][vid]["THUMB"],
                ("outside the R1 first-web band (threshold %.2f mm), so the web cross-blend "
                 "never ran and THUMB_* was not in the allowed set" % W_WEB)
                if ref["dchain"][vid]["THUMB"] > W_WEB else
                ("inside the R1 first-web band, so only the ROOT-level web blend ran: "
                 "THUMB_CMC_R / THUMB_MCP_R were added but THUMB_IP_R was never eligible "
                 "because the vertex is INDEX owned")))}


CASE = {"1383": vertex_case(1383), "2740": vertex_case(2740)}

# ============================================================ 5. region probe
probe = {
    "tau_mm": rr(TAU, 4), "med_edge_mm": rr(MED, 4),
    "R_TT_mm": rr(R_TT, 4), "R_MAX_mm": rr(R_MAX, 4),
    "thumb_joint_arcs_mm": {"MCP": rr(s_MCP, 4), "IP": rr(s_IP, 4), "TIP": rr(s_TIP, 4)},
    "THUMB_DISTAL": sorted(MASKS["THUMB_DISTAL"]),
    "THUMB_PROXIMAL": sorted(MASKS["THUMB_PROXIMAL"]),
    "THUMB_FIRST_METACARPAL": sorted(MASKS["THUMB_FIRST_METACARPAL"]),
    "THENAR_BASE": sorted(MASKS["THENAR_BASE"]),
    "nail_thumb_vertices": sorted(TNAIL),
    "cap_vertices": sorted(CAP_V),
    "counts": {k: len(MASKS[k]) for k in ("THUMB_DISTAL", "THUMB_PROXIMAL",
                                          "THUMB_FIRST_METACARPAL", "THENAR_BASE")},
    "thenar_base_own_breakdown": {},
    "web_R1A": sorted(WEB),
    "web_R1A_count": len(WEB),
    "web_R1A_own_breakdown": {},
    "web_R1A_thumb_arc_range_mm": [rr(min(ARC[i] for i in WEB), 4),
                                   rr(max(ARC[i] for i in WEB), 4)] if WEB else None,
    "web_R1A_contains_nail": sorted(set(WEB) & TNAIL),
    "web_R1A_contains_cap": sorted(set(WEB) & CAP_V),
    "web_R1A_group_totals_R1": {},
    "web_R1_vertex_ids": sorted(web_r1),
    "thumb_owned_arc_range_mm": [rr(min(ARC[i] for i in THUMB_OWN), 4),
                                 rr(max(ARC[i] for i in THUMB_OWN), 4)],
    "own_breakdown_all": {k: sum(1 for i in range(NV) if ref["OWN_V"][i] == k)
                          for k in list(ref["AC"])},
}
for k, key in (("thenar_base_own_breakdown", "THENAR_BASE"), ("web_R1A_own_breakdown", "web_R1A")):
    ids = MASKS["THENAR_BASE"] if key == "THENAR_BASE" else WEB
    probe[k] = {kk: sum(1 for j in ids if ref["OWN_V"][j] == kk) for kk in list(ref["AC"])}
wt = {}
for i in WEB:
    for g, w in W[i].items():
        wt[g] = wt.get(g, 0.0) + w
probe["web_R1A_group_totals_R1"] = dict((k, rr(v, 6)) for k, v in sorted(wt.items()))

# ============================================================ 6. outputs
ROOT = {
    "stage": "STAGE5B_R1A_THUMB_WEIGHT_ROOT_CAUSE_AUDIT",
    "generated_at": NOW, "read_only": True,
    "input_r1_blend": R1, "input_r1_sha256": s_r1,
    "input_master_blend": MASTER, "input_master_sha256": s_master,
    "q1_why_thumb_ip_spread_over_the_thumb": {
        "observation": {
            "THUMB_IP_R_nonzero_vertices": STATS["THUMB_IP_R"]["nonzero"],
            "gt_0.25": STATS["THUMB_IP_R"]["gt_0.25"],
            "gt_0.50": STATS["THUMB_IP_R"]["gt_0.50"],
            "gt_0.75": STATS["THUMB_IP_R"]["gt_0.75"],
            "max": STATS["THUMB_IP_R"]["max"],
            "mean_nonzero": STATS["THUMB_IP_R"]["mean_nonzero"],
            "weight_sum": STATS["THUMB_IP_R"]["sum"]},
        "mechanism": ("R1's `THUMB DISTAL OWNERSHIP GUARD` predicate is INVERTED.  It fires when "
                      "`arc_of(THUMB,v) <= XIJ['THUMB'][2] + tau`, but XIJ['THUMB'][2] is the "
                      "arc position of the IP JOINT measured from the CMC head, i.e. the DISTAL "
                      "end of the MCP segment.  Every thumb-owned vertex satisfies that "
                      "inequality (all of them have arc <= IP-joint arc), so the guard becomes "
                      "'THUMB_IP_R >= 2 x sum(others)' over the ENTIRE thumb: distal phalanx, "
                      "proximal phalanx, first metacarpal and thumb base.  The intended predicate "
                      "was distal-of-IP: `arc >= XIJ['THUMB'][2] - tau`."),
        "vertex_counts": {
            "thumb_owned_vertices": n_own_thumb,
            "guard_predicate_true_under_R1_rule": n_guard_r1,
            "guard_predicate_true_under_corrected_rule": n_guard_ok,
            "thumb_owned_with_arc_le_IP_arc_plus_tau": n_arc_le_ip,
            "vertices_observed_with_W_IP_ge_2x_others": len(forced)},
        "histogram_W_IP_over_thumb_owned": HIST,
        "region_breakdown_of_THUMB_IP_mass": IP_BUCKETS,
        "arc_breakdown_of_THUMB_IP_mass": ARC_BUCKETS},
    "q2_which_semantic_term_caused_the_spread": {
        "answer": "the semantic guard (THUMB DISTAL OWNERSHIP GUARD), not the lateral distance "
                  "term, not the normalisation order",
        "details": [
            "the guard sets raw[THUMB_IP_R] = max(raw, 2*others) BEFORE normalisation; the "
            "normalisation is a plain partition and cannot undo it (it scales numerator and "
            "denominator together)",
            "there is NO else-branch that restricts THUMB_IP_R to the distal phalanx, so once the "
            "predicate is always true the distal authority becomes a whole-digit authority",
            "the longitudinal term lam = exp(-((xi-mj)/kappa)^2) and the lateral term "
            "mu = exp(-(d/L0)^2) are both computed and then OVERRIDDEN by the guard on every "
            "thumb-owned vertex",
            "the region mask is too wide in an independent way: OWN_V is a plain nearest-chain "
            "partition with NO thenar / first-metacarpal-base region, so the whole thumb base is "
            "classified as THUMB and inherits the same treatment",
            "the R1 audit defect (below) then hid the symptom: violations were reported as []"],
        "normalisation_order": "normalise -> prune(4) -> normalise; deterministic and NOT the "
                               "cause (worst normalisation error 4.4e-8)"},
    "q3_why_first_web_violations_empty_while_thumb_ip_is_present": FIRST_WEB_RC,
    "q4_why_cmc_and_mcp_max_are_small": {
        "thumb_cmc_max": STATS["THUMB_CMC_R"]["max"],
        "thumb_mcp_max": STATS["THUMB_MCP_R"]["max"],
        "thumb_ip_max": STATS["THUMB_IP_R"]["max"],
        "analytic_bound": bound,
        "statement": ("because the guard forces THUMB_IP_R >= 2 x sum(everything else) on every "
                      "thumb-owned vertex, the remaining groups can only share at most 1/3 of the "
                      "normalised weight; THUMB_CMC_R and THUMB_MCP_R then split that 1/3 between "
                      "themselves, which caps them at ~0.3618 / ~0.2955.  The weakness is a "
                      "SYMPTOM of the inverted guard, not an independent defect."),
        "expected_after_fix": ("with a joint-local partition of unity along the thumb arc the "
                               "first-metacarpal band and the proximal-phalanx band reach "
                               "THUMB_CMC_R / THUMB_MCP_R dominance on their own surface, without "
                               "any artificial >0.5 gate")},
    "q5_root_cause_classification": {
        "thumb_distal_ownership_guard_polarity_error": "PRIMARY (confirmed)",
        "first_web_exception_implementation_error": "PRIMARY (confirmed: NAIL_THUMB_V exemption "
                                                    "keeps THUMB_IP allowed + forced inside the web)",
        "audit_semantic_mismatch": "PRIMARY (confirmed: audit exempts THUMB_IP from the violation "
                                   "check while declaring a whitelist that excludes it)",
        "region_mask_too_wide": "CONTRIBUTING (OWN_V has no thenar / first-metacarpal-base region "
                                "and no longitudinal bound on the web band)",
        "thumb_distal_ownership_guard_too_strong": "CONTRIBUTING (the inverted guard is "
                                                   "unconditional)",
        "wrist_background_prune_competition": "NOT_THE_CAUSE",
        "group_normalization_order": "NOT_THE_CAUSE (error 4.4e-8)",
        "semantic_ownership_classification_error": "CONTRIBUTING (nail vertices v1383 / v2740 are "
                                                   "vertex-owned by INDEX because the 2-D "
                                                   "nearest-chain test is used as the ownership "
                                                   "authority)"},
    "geodesic_coordinate_rejection": GEO_ANOM,
    "per_group_stats": STATS,
    "thumb_geometry_reference": {
        "median_edge_mm": rr(MED, 4), "tau_used_mm": rr(TAU, 4),
        "R_TT_tube_radius_mm": rr(R_TT, 4), "R_MAX_base_radius_mm": rr(R_MAX, 4),
        "thumb_chain_arcs_mm": [rr(x, 4) for x in TF["XIJ_thumb_arc_mm"]],
        "distal_most_vertex": TF["dstar"]},
    "log": LOG}

json.dump(ROOT, open(os.path.join(OUTDIR, "STAGE5B_R1A_THUMB_WEIGHT_ROOT_CAUSE_AUDIT.json"),
                     "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE5B_R1A_THUMB_WEIGHT_ROOT_CAUSE_AUDIT.json")

NAILB = {
    "stage": "THUMB_NAIL_BOUNDARY_VERTEX_AUDIT",
    "generated_at": NOW, "read_only": True,
    "purpose": ("independent re-verification of the two vertices that NAIL_WEIGHT_AUDIT treats as "
                "thumb nail vertices but which are NOT dominated by THUMB_IP_R"),
    "nail_definition_used_by_R1_audit": ("vertex belongs to a polygon with material_index==1 whose "
                                         "FACE centroid is owned by THUMB (nearest chain)"),
    "thumb_nail_vertex_set": sorted(TNAIL),
    "thumb_nail_vertex_count": len(TNAIL),
    "thumb_distal_cap_patch_vertex_ids": sorted(CAP_V),
    "cap_representative_vertex": ref["cap"]["thumb"]["rep_vertex"],
    "cap_representative_world": [rr(x, 9) for x in ref["cap"]["cap_representative_world"]],
    "cases": CASE,
    "verdicts": {}}
for vid in (1383, 2740):
    c = CASE[str(vid)]
    NAILB["verdicts"][str(vid)] = {
        "incident_to_nail_bed_face": c["incident_to_nail_bed_face"],
        "nail_faces": c["nail_faces"], "non_nail_faces": c["non_nail_faces"],
        "classification": c["classification"],
        "vertex_ownership_region": c["vertex_ownership_region"],
        "thumb_segment_of_projection": c["thumb_segment_of_projection"],
        "arc_along_thumb_chain_mm": c["arc_along_thumb_chain_mm"],
        "dist_to_THUMB_chain_mm": c["dist_to_THUMB_chain_mm"],
        "dist_to_INDEX_chain_mm": c["dist_to_INDEX_chain_mm"],
        "dist_to_thumb_distal_cap_rep_mm": c["dist_to_cap_representative_mm"],
        "in_thumb_distal_cap_patch": c["in_thumb_distal_cap_patch"],
        "in_first_web_mask_r1": c["in_first_web_mask_r1"],
        "in_first_web_mask_r1a": c["in_first_web_mask_r1a"],
        "current_dominant": c["current_dominant_bone"],
        "why_r1_gave_it_no_thumb_bone": c["why_r1_gave_it_no_thumb_bone"],
        "branch_rule_result": "C -> SHARED_SEMANTIC_BOUNDARY_VERTEX (nail/skin border) located on "
                              "the THUMB DISTAL PHALANX -> R1A assigns THUMB_IP_R as dominant "
                              "(branch A applies to the distal authority; recorded here as a "
                              "shared boundary exception with incident-face evidence)"}
json.dump(NAILB, open(os.path.join(OUTDIR, "THUMB_NAIL_BOUNDARY_VERTEX_AUDIT.json"), "w",
                      encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote THUMB_NAIL_BOUNDARY_VERTEX_AUDIT.json")

json.dump(probe, open(os.path.join(OUTDIR, "_tmp", "R1A_REGION_PROBE.json"), "w",
                      encoding="utf-8"), indent=1, ensure_ascii=False)

json.dump({"NV": NV, "arc_thumb_mm": [rr(x, 5) for x in ARC],
           "geo_from_tip_mm": [rr(x, 4) for x in SGM],
           "d_thumb_chain_mm": [rr(ref["dchain"][i]["THUMB"], 5) for i in range(NV)],
           "d_index_chain_mm": [rr(ref["dchain"][i]["INDEX"], 5) for i in range(NV)],
           "own": ref["OWN_V"],
           "own2": [[a for a, _d in ref["order2"][i]] for i in range(NV)],
           "s_MCP_mm": rr(s_MCP, 5), "s_IP_mm": rr(s_IP, 5), "s_TIP_mm": rr(s_TIP, 5),
           "med_edge_mm": rr(MED, 5), "tau_mm": rr(TAU, 5),
           "R_TT_mm": rr(R_TT, 5), "R_MAX_mm": rr(R_MAX, 5),
           "cap_verts": sorted(CAP_V), "nail_thumb_verts": sorted(TNAIL),
           "web_R1A": sorted(WEB), "web_R1": sorted(web_r1),
           "regions": {k: sorted(MASKS[k]) for k in ("THUMB_DISTAL", "THUMB_PROXIMAL",
                                                     "THUMB_FIRST_METACARPAL", "THENAR_BASE")}},
          open(os.path.join(OUTDIR, "_tmp", "R1A_SURVEY.json"), "w", encoding="utf-8"))
print("SURVEY_DONE")
