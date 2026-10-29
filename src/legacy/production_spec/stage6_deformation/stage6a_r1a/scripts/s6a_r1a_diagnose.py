# =====================================================================================
# STAGE6A_R1A -- READ-ONLY root-cause diagnosis of the THUMB MCP / IP transition defects
# =====================================================================================
# Nothing is written.  The frozen Stage6A R1 harness is opened read-only, posed and reset.
# Determines, per case, whether the defect comes from
#   A. weight transition   B. topology density   C. pose collision   D. metric artefact
# =====================================================================================
import bpy
import sys
import os
import json
import math
import datetime
from mathutils import Vector, Quaternion

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
S5B_R1B_SCRIPTS = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "stage5_production_rig",
    "stage5b_r1b", "scripts"))
sys.path.append(S5B_R1B_SCRIPTS)
if not os.path.isfile(os.path.join(S5B_R1B_SCRIPTS, "r1b_common.py")):
    raise SystemExit("cannot locate r1b_common.py at %s" % S5B_R1B_SCRIPTS)

import r1b_common as C                                          # noqa: E402
RC = C.RC
S6 = C.S6

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[R1A-DIAG]", s, flush=True)


# ---------------------------------------------------------------- gate the frozen inputs
s_r1a = C.sha256(C.R1A_MASTER)
s_h1 = C.sha256(C.STAGE6A_R1_HARNESS)
log("R1A master sha =", s_r1a)
log("Stage6A R1 harness sha =", s_h1)
if s_r1a != C.R1A_SHA256:
    raise SystemExit("FAIL CLOSED: Stage5B R1A master hash drift")
if s_h1 != C.STAGE6A_R1_HARNESS_SHA256:
    raise SystemExit("FAIL CLOSED: Stage6A R1 harness hash drift")

ctx = C.build_context()
ref = ctx["ref"]
NV = ctx["NV"]
MED = ctx["MED"]
ARC = ctx["ARC"]
V0 = ctx["V0"]
POLY = ctx["poly"]
EDGES = ctx["edges"]
FO = ctx["FO"]
s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]
thumb_own = ctx["thumb_own"]
NAIL, CAP, WEB = ctx["nail"], ctx["cap"], ctx["first_web"]
log("V=%d E=%d F=%d  MED=%.6f mm  s_MCP=%.4f  s_IP=%.4f  s_TIP=%.4f"
    % (NV, len(EDGES), len(POLY), MED, s_MCP, s_IP, ctx["s_TIP"]))
log("nail_thumb_vertices=%d  cap_vertices=%d  first_web=%d  thumb_owned=%d"
    % (len(NAIL), len(CAP), len(WEB), len(thumb_own)))

# ---------------------------------------------------------------- joint ring depths
RD = {j: C.joint_ring_depth(ctx, j) for j in ("MCP", "IP")}
LONG_BIN = [int(math.floor(ARC[i] / MED)) for i in range(NV)]

# ---------------------------------------------------------------- open the R1 harness
bpy.ops.wm.open_mainfile(filepath=C.STAGE6A_R1_HARNESS)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me = ob.data
MW = ob.matrix_world.copy()
W1 = C.read_object_weights(ob, NV)
GROUP_NAMES = sorted(g.name for g in ob.vertex_groups)
log("harness groups (%d): %s" % (len(GROUP_NAMES), GROUP_NAMES))
if sorted(GROUP_NAMES) != sorted(C.ALL_DEFORM):
    raise SystemExit("FAIL CLOSED: harness deform groups differ from the frozen 16")

# ---------------------------------------------------------------- bind baselines
S6.reset_pose(rig)
bpy.context.view_layer.update()
FACE_AREA0 = [C.face_area(V0, p) for p in POLY]
EDGE_LEN0 = [(V0[a] - V0[b]).length for a, b in EDGES]
Vb, Pb = C.evaluate(ob, MW)
log("bind zero-pose max delta = %.9f mm"
    % (max((Vb[i] - V0[i]).length for i in range(NV)) * 1000.0))
BASE_PAIRS = C.intersect_pairs(V0, POLY)
log("bind-pose intersecting face pairs = %d" % len(BASE_PAIRS))

# ---------------------------------------------------------------- patch authority
KAPPA = 2.0 * MED
PATCH = {}
for seg in ("MCP", "IP"):
    a = s_MCP if seg == "MCP" else s_IP
    PATCH[seg] = sorted(i for i in ctx["thumb_own"] if abs(ARC[i] - a) <= KAPPA)
    log("THUMB_%s patch = %d vertices  (arc window %.3f .. %.3f)"
        % (seg, len(PATCH[seg]), a - KAPPA, a + KAPPA))

# ---------------------------------------------------------------- authorised repair region
EXCLUDED = NAIL | CAP | WEB
CORE = set(PATCH["MCP"]) | set(PATCH["IP"])
ADJ2 = set(CORE)
adj = {}
for a, b in EDGES:
    adj.setdefault(a, []).append(b)
    adj.setdefault(b, []).append(a)
front = set(CORE)
for _ in range(2):
    nxt = set()
    for u in front:
        for v in adj.get(u, ()):
            if v not in ADJ2:
                ADJ2.add(v)
                nxt.add(v)
    front = nxt
ADJ2_THUMB_ONLY = set(i for i in ADJ2 if i in thumb_own)
AUTH = set(i for i in ADJ2_THUMB_ONLY if i not in EXCLUDED)
log("authorised region: core=%d  2-ring closure=%d  thumb-only=%d  after exclusion=%d"
    % (len(CORE), len(ADJ2), len(ADJ2_THUMB_ONLY), len(AUTH)))
log("excluded from repair: nail=%d cap=%d first_web=%d"
    % (len(NAIL & ADJ2), len(CAP & ADJ2), len(WEB & ADJ2)))

covered = set(PATCH["MCP"]) | set(PATCH["IP"])
log("core fully covered by AUTH: %s" % (covered <= AUTH))

# which frozen (non-thumb) groups appear on AUTH vertices?
carry = {}
for i in AUTH:
    for g, w in W1[i].items():
        if g not in C.THUMB_FREE_GROUPS and w > 0.0:
            carry.setdefault(g, []).append(i)
log("non-thumb groups carried by AUTH vertices: %s"
    % {g: len(v) for g, v in carry.items()})

PATCH_FACES = {}
for seg in ("MCP", "IP"):
    s = set(PATCH[seg])
    PATCH_FACES[seg] = [fi for fi, p in enumerate(POLY) if any(v in s for v in p)]
PATCH_EDGES = {}
for seg in ("MCP", "IP"):
    s = set(PATCH[seg])
    PATCH_EDGES[seg] = [k for k, (a, b) in enumerate(EDGES) if a in s or b in s]

# ---------------------------------------------------------------- helpers
def dom(w):
    if not w:
        return None
    return max(w.items(), key=lambda kv: kv[1])[0]


def wvec(i, groups=None):
    d = W1[i]
    if groups:
        return dict((g, C.rr(d.get(g, 0.0))) for g in groups)
    return dict((g, C.rr(v)) for g, v in sorted(d.items()) if v > 0.0)


def vert_info(i, seg):
    return {
        "vertex": i,
        "arc_mm": C.rr(ARC[i], 6),
        "arc_offset_from_joint_mm": C.rr(ARC[i] - (s_MCP if seg == "MCP" else s_IP), 6),
        "lateral_radius_mm": C.rr(ctx["dth"][i], 6),
        "longitudinal_ring_bin": LONG_BIN[i],
        "bfs_ring_from_MCP_joint": RD["MCP"].get(i, -1),
        "bfs_ring_from_IP_joint": RD["IP"].get(i, -1),
        "weight_vector": wvec(i),
        "dominant_group": dom(W1[i]),
        "in_nail_semantic": i in NAIL,
        "in_distal_cap": i in CAP,
        "in_first_web_sanctioned": i in WEB,
        "in_authorised_repair_region": i in AUTH,
    }


def edge_info(k, seg):
    a, b = EDGES[k]
    return {"edge_index": k, "vertices": [a, b],
            "arc_mm": [C.rr(ARC[a], 6), C.rr(ARC[b], 6)],
            "longitudinal_ring_bins": [LONG_BIN[a], LONG_BIN[b]],
            "vertex_detail": [vert_info(a, seg), vert_info(b, seg)]}


# ---------------------------------------------------------------- per-case diagnosis
CASES = {}
REPRO = {}
for (d, seg, ang) in C.THUMB_CASES:
    cid = "%s_%s_%d" % ("TH", seg, int(ang))
    bone = "%s_%s_R" % (d, seg)
    joint_arc = s_MCP if seg == "MCP" else s_IP

    S6.reset_pose(rig)
    bpy.context.view_layer.update()
    S6.set_joint_rotation(rig, bone, C.FLEXION_SIGN_THUMB * ang)
    bpy.context.view_layer.update()
    V, P = C.evaluate(ob, MW)

    areas = [C.face_area(V, p) for p in POLY]
    arat = [(areas[i] / FACE_AREA0[i]) if FACE_AREA0[i] > 1e-18 else 0.0
            for i in range(len(POLY))]
    el = [(V[a] - V[b]).length for a, b in EDGES]
    erat = [(el[k] / EDGE_LEN0[k]) if EDGE_LEN0[k] > 1e-18 else 0.0
            for k in range(len(EDGES))]

    pf = PATCH_FACES[seg]
    pe = PATCH_EDGES[seg]
    pr = [arat[i] for i in pf]
    per = [erat[k] for k in pe]

    REPRO[cid] = {"min_face_area_ratio": C.rr(min(pr), 6),
                  "face_area_p05": C.rr(C.stats(pr)["p05"], 6),
                  "min_edge_ratio": C.rr(min(per), 6),
                  "max_edge_stretch": C.rr(max(per), 6),
                  "local_surface_area_ratio": C.rr(
                      sum(areas[i] for i in pf) / max(1e-18, sum(FACE_AREA0[i] for i in pf)), 6)}

    # ---- worst face
    fmin = min(pf, key=lambda i: arat[i])
    # ---- p05 worst region
    thr = C.stats(pr)["p05"]
    worst = sorted([i for i in pf if arat[i] <= thr])
    wc_arc = [C.rr(sum(ARC[v] for v in POLY[i]) / len(POLY[i]), 6) for i in worst]
    wc_dom = {}
    for i in worst:
        for v in POLY[i]:
            g = dom(W1[v])
            wc_dom[g] = wc_dom.get(g, 0) + 1
    # ---- worst edges
    emin = min(pe, key=lambda k: erat[k])
    emax = max(pe, key=lambda k: erat[k])

    # ---- self-intersection (intra-thumb)
    pairs = C.intersect_pairs(V, POLY)
    newp = sorted(pairs - BASE_PAIRS)
    intra = [(a, b) for a, b in newp if FO.get(a) == "THUMB" and FO.get(b) == "THUMB"]
    vs_other = [(a, b) for a, b in newp if (FO.get(a) == "THUMB") != (FO.get(b) == "THUMB")]
    intra_detail = []
    for a, b in intra:
        ca = C.face_centroid(V, POLY[a])
        cb = C.face_centroid(V, POLY[b])
        na = C.face_normal(V, POLY[a])
        nb = C.face_normal(V, POLY[b])
        pen = min(abs((cb - ca).dot(na)), abs((ca - cb).dot(nb))) * 1000.0
        bina = [LONG_BIN[v] for v in POLY[a]]
        binb = [LONG_BIN[v] for v in POLY[b]]
        intra_detail.append({
            "faces": [a, b],
            "face_centroid_arc_mm": [C.rr(RC.arc_of(ctx["AC"]["THUMB"], ca)[0], 6),
                                     C.rr(RC.arc_of(ctx["AC"]["THUMB"], cb)[0], 6)],
            "longitudinal_ring_bins": [bina, binb],
            "longitudinal_ring_bin_gap": min(abs(x - y) for x in bina for y in binb),
            "penetration_depth_mm": C.rr(pen, 6),
            "faces_vertex_detail": [vert_info(v, seg) for v in POLY[a]],
            "faces_vertex_detail_b": [vert_info(v, seg) for v in POLY[b]],
        })

    # ---- transition width analysis (empirical, on AUTH vertices)
    auth_u = [i for i in AUTH if W1[i].get("THUMB_IP_R", 0.0) >= 0.99]
    auth_m = [i for i in AUTH if W1[i].get("THUMB_MCP_R", 0.0) >= 0.99]
    s_full_ip = min((ARC[i] for i in auth_u), default=None)
    s_full_mcp = max((ARC[i] for i in auth_m), default=None)
    span = (s_full_ip - s_full_mcp) if (s_full_ip is not None and s_full_mcp is not None) else None
    bins_in_band = sorted(set(LONG_BIN[i] for i in AUTH
                              if abs(ARC[i] - joint_arc) <= KAPPA))

    # ---- cause classification
    evidence = []
    cause = "A_WEIGHT_TRANSITION"
    fmin_area0 = FACE_AREA0[fmin]
    med_area0 = C.stats([FACE_AREA0[i] for i in pf])["median"]
    fmin_arcs = [C.rr(ARC[v], 4) for v in POLY[fmin]]
    fmin_dom = [dom(W1[v]) for v in POLY[fmin]]
    fmin_lat = [C.rr(ctx["dth"][v], 4) for v in POLY[fmin]]
    distinct_dom = len(set(fmin_dom))
    if span is not None:
        evidence.append({
            "marker": "empirical_transition_arc_span_mm",
            "value": C.rr(span, 4),
            "nominal_R1A": C.rr(2.0 * MED, 4),
            "reads": ("full-IP to full-MCP arc span across the authorised region; the nominal "
                      "R1A blend is 2 x MED, i.e. about two mesh edges"),
        })
    evidence.append({
        "marker": "longitudinal_ring_bins_inside_joint_band",
        "value": len(bins_in_band),
        "reads": "number of distinct MED-wide longitudinal rings the joint band resolves into",
    })
    evidence.append({
        "marker": "worst_face_dominant_weight_groups",
        "value": fmin_dom,
        "reads": "distinct dominant groups across the worst face: >1 means the face straddles "
                 "the weight transition",
    })
    evidence.append({
        "marker": "worst_face_baseline_area_vs_patch_median",
        "value": C.rr(fmin_area0 / max(med_area0, 1e-18), 6),
        "reads": "if << 1 the ratio is amplified by a small denominator (metric artefact risk)",
    })
    evidence.append({
        "marker": "intra_thumb_pair_ring_bin_gap_min",
        "value": (min([x["longitudinal_ring_bin_gap"] for x in intra_detail])
                  if intra_detail else None),
        "reads": "0-1 means adjacent surface, >=3 means genuinely distant surface fold-over",
    })

    # decision
    if distinct_dom >= 2 and span is not None and span <= 3.0 * MED:
        cause = "A_WEIGHT_TRANSITION"
    elif fmin_area0 / max(med_area0, 1e-18) < 0.15 and span is not None and span <= 3.0 * MED:
        cause = "A_WEIGHT_TRANSITION"
    elif intra_detail and min(x["longitudinal_ring_bin_gap"] for x in intra_detail) >= 3:
        cause = "C_POSE_COLLISION"
    elif len(bins_in_band) <= 2:
        cause = "B_TOPOLOGY_DENSITY"
    else:
        cause = "D_METRIC_ARTEFACT"

    CASES[cid] = {
        "case_id": cid, "digit": d, "joint": seg, "angle_deg": ang,
        "bone": bone, "applied_rotation_deg": C.FLEXION_SIGN_THUMB * ang,
        "joint_arc_mm": C.rr(joint_arc, 6), "kappa_mm": C.rr(KAPPA, 6),
        "patch_vertex_count": len(PATCH[seg]),
        "min_face_area_ratio": {
            "face": fmin, "ratio": C.rr(arat[fmin], 6),
            "baseline_face_area_m2": fmin_area0,
            "patch_median_baseline_face_area_m2": med_area0,
            "vertex_arc_mm": fmin_arcs,
            "vertex_lateral_radius_mm": fmin_lat,
            "vertex_dominant_groups": fmin_dom,
            "distinct_dominant_groups": distinct_dom,
            "vertex_detail": [vert_info(v, seg) for v in POLY[fmin]],
        },
        "p05_worst_region": {
            "threshold": C.rr(thr, 6), "face_count": len(worst),
            "faces": worst[:40],
            "arc_range_mm": [C.rr(min(wc_arc), 4), C.rr(max(wc_arc), 4)] if wc_arc else None,
            "mean_arc_mm": C.rr(sum(wc_arc) / len(wc_arc), 6) if wc_arc else None,
            "dominant_group_histogram": wc_dom,
            "nail_faces": sum(1 for i in worst if all(v in NAIL for v in POLY[i])),
            "cap_faces": sum(1 for i in worst if all(v in CAP for v in POLY[i])),
            "first_web_faces": sum(1 for i in worst if any(v in WEB for v in POLY[i])),
        },
        "min_edge_ratio": dict({"ratio": C.rr(erat[emin], 6)}, **edge_info(emin, seg)),
        "max_edge_stretch": dict({"ratio": C.rr(erat[emax], 6)}, **edge_info(emax, seg)),
        "intra_thumb_self_intersection": {
            "pair_count": len(intra),
            "target_vs_other_pair_count": len(vs_other),
            "pairs": intra_detail[:20],
        },
        "transition_field_analysis": {
            "auth_vertex_count": len(AUTH),
            "n_full_ip_ge_0_99": len(auth_u), "n_full_mcp_ge_0_99": len(auth_m),
            "s_full_IP_mm": C.rr(s_full_ip, 6) if s_full_ip is not None else None,
            "s_full_MCP_mm": C.rr(s_full_mcp, 6) if s_full_mcp is not None else None,
            "empirical_transition_arc_span_mm": C.rr(span, 6) if span is not None else None,
            "nominal_R1A_transition_span_mm": C.rr(2.0 * MED, 6),
            "longitudinal_ring_bins_inside_band": bins_in_band,
        },
        "evidence": evidence,
        "cause_classification": {"primary": cause},
    }
    log("%-12s minFaceAR=%.6f p05=%.6f minEdgeR=%.6f maxStretch=%.6f  intra=%d  cause=%s"
        % (cid, min(pr), thr, min(per), max(per), len(intra), cause))

S6.reset_pose(rig)
bpy.context.view_layer.update()

# ---------------------------------------------------------------- R1 baseline reproduction
repro_ok = True
repro_tbl = {}
for cid, base in sorted(C.R1_BASELINE.items()):
    got = REPRO.get(cid)
    row = {}
    for k, v in base.items():
        g = got[k] if got else None
        ok = (g is not None and abs(g - v) <= 5e-6)
        row[k] = {"R1_reported": v, "R1A_reproduced": g, "match": bool(ok)}
        if not ok:
            repro_ok = False
    repro_tbl[cid] = row
log("R1 baseline reproduction: %s" % ("EXACT" if repro_ok else "MISMATCH"))

# ---------------------------------------------------------------- aggregate verdict
cause_hist = {}
for c in CASES.values():
    k = c["cause_classification"]["primary"]
    cause_hist[k] = cause_hist.get(k, 0) + 1

s_auth = sorted(ARC[i] for i in AUTH)
OUT = {
    "stage": "STAGE6A_R1A_THUMB_TRANSITION_ROOT_CAUSE",
    "generated_at": NOW, "mode": "READ_ONLY_DIAGNOSIS",
    "scope": ("root cause of the THUMB_IP / THUMB_MCP transition defects reported by Human "
              "Review on Stage6A R1 (THUMB_IP_TRANSITION = FAIL_REVISE, "
              "THUMB_MCP_TRANSITION = HOLD_FOR_NARROW_REVISION)"),
    "inputs": {
        "stage5b_r1a_master": {"path": C.R1A_MASTER, "sha256": s_r1a,
                               "unchanged_after_diagnosis": C.sha256(C.R1A_MASTER) == s_r1a},
        "stage6a_r1_harness": {"path": C.STAGE6A_R1_HARNESS, "sha256": s_h1,
                               "unchanged_after_diagnosis": C.sha256(C.STAGE6A_R1_HARNESS) == s_h1},
    },
    "authorities": {
        "longitudinal_coordinate": "APPROVED_JOINT_POLYLINE_ARC_LENGTH (mm from the CMC head)",
        "joint_arcs_mm": {"CMC_head": 0.0, "MCP": C.rr(s_MCP, 6), "IP": C.rr(s_IP, 6),
                          "TIP": C.rr(ctx["s_TIP"], 6)},
        "med_edge_mm": C.rr(MED, 6), "kappa_mm": C.rr(KAPPA, 6),
        "R_TT_mm": C.rr(ctx["R_TT"], 6), "R_MAX_mm": C.rr(ctx["R_MAX"], 6),
        "forbidden_coordinate": "GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP",
    },
    "regions": {
        "thumb_owned_vertex_count": len(thumb_own),
        "nail_semantic_vertex_count": len(NAIL), "distal_cap_vertex_count": len(CAP),
        "first_web_sanctioned_vertex_count": len(WEB),
        "THUMB_MCP_local_deformation_patch": {"vertex_count": len(PATCH["MCP"]),
                                              "arc_window_mm": [C.rr(s_MCP - KAPPA, 4),
                                                                C.rr(s_MCP + KAPPA, 4)]},
        "THUMB_IP_local_deformation_patch": {"vertex_count": len(PATCH["IP"]),
                                             "arc_window_mm": [C.rr(s_IP - KAPPA, 4),
                                                               C.rr(s_IP + KAPPA, 4)]},
        "authorised_repair_region": {
            "definition": ("UNION(THUMB_MCP local deformation patch, THUMB_IP local "
                           "deformation patch) + up to 2 topology rings, thumb-owned only, "
                           "MINUS approved distal-cap vertices, nail semantic vertices and "
                           "sanctioned first-web vertices"),
            "core_vertex_count": len(CORE),
            "two_ring_closure_vertex_count": len(ADJ2),
            "thumb_owned_in_closure": len(ADJ2_THUMB_ONLY),
            "final_authorised_vertex_count": len(AUTH),
            "arc_range_mm": [C.rr(s_auth[0], 4), C.rr(s_auth[-1], 4)],
            "core_fully_inside": bool(covered <= AUTH),
            "vertex_ids": sorted(AUTH),
        },
        "excluded_by_freeze": {
            "nail_in_closure": sorted(NAIL & ADJ2),
            "distal_cap_in_closure": sorted(CAP & ADJ2),
            "first_web_in_closure": sorted(WEB & ADJ2),
        },
        "non_thumb_groups_on_authorised_region": dict((g, sorted(v)) for g, v in carry.items()),
    },
    "r1_baseline_reproduction": {"exact": repro_ok, "cases": repro_tbl,
                                 "note": ("the R1 numbers are recomputed here on the frozen R1 "
                                          "harness; an exact match proves the metric path used "
                                          "by the candidate sweep is identical to Stage6A R1")},
    "cases": CASES,
    "cause_histogram": cause_hist,
    "log": LOG,
}
json.dump(OUT, open(os.path.join(OUTDIR, "STAGE6A_R1A_THUMB_TRANSITION_ROOT_CAUSE.json"),
                    "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("cause histogram: %s" % cause_hist)
log("wrote STAGE6A_R1A_THUMB_TRANSITION_ROOT_CAUSE.json")
print("DIAG_DONE")
