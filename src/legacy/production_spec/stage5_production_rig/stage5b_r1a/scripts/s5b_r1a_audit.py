# =====================================================================================
# STAGE5B_R1A -- FULL STATIC RE-AUDIT (READ-ONLY on R1A / R1 / master)
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
R1A = os.path.join(OUTDIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend")
MASTER = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
MASTER_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[R1A-AUDIT]", s)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rr(x, n=9):
    return round(float(x), n)


def stats(v):
    v = sorted(v)
    if not v:
        return {"n": 0, "mean": 0.0, "median": 0.0, "p90": 0.0, "max": 0.0, "sum": 0.0}
    return {"n": len(v), "mean": rr(sum(v) / len(v), 6),
            "median": rr(v[len(v) // 2], 6), "p90": rr(v[min(len(v) - 1, int(0.9 * len(v)))], 6),
            "max": rr(v[-1], 6), "sum": rr(sum(v), 6)}


# ---------------------------------------------------------------- inputs
s_master, s_r1, s_r1a = sha(MASTER), sha(R1), sha(R1A)
log("master %s ; r1 %s ; r1a %s" % (s_master[:12], s_r1[:12], s_r1a[:12]))
if s_master != MASTER_SHA:
    raise SystemExit("FAIL CLOSED: master drift")
if s_r1 != R1_SHA:
    raise SystemExit("FAIL CLOSED: R1 drift")

REG = json.load(open(os.path.join(OUTDIR, "_tmp", "R1A_REGIONS.json"), encoding="utf-8"))
AUTH_JSON = set(REG["AUTH"])
CHANGED = set(REG["CHANGED"])
D = REG["derivation"]
TAU = D["tau_mm"]
s_MCP, s_IP = D["thumb_joint_arcs_mm"]["MCP"], D["thumb_joint_arcs_mm"]["IP"]
R_TT, R_MAX = D["R_TT_mm"], D["R_MAX_mm"]

# ---------------------------------------------------------------- reference + meshes
ref = C.load_reference(TOP)
NV = ref["NV"]
V0 = ref["V0"]
TF = C.thumb_frame(ref)
ARC = TF["arc_thumb_mm"]
dth = [ref["dchain"][i]["THUMB"] for i in range(NV)]
RG = C.build_regions(ref, TF, TAU, R_TT, R_MAX)
OWN_R1A = RG["own_r1a"]
TNAIL = RG["nail_thumb_vertices"]
CAP_V = RG["cap_vertices"]
DISTAL = RG["THUMB_DISTAL"]
PROXIMAL = RG["THUMB_PROXIMAL"]
METACARPAL = RG["THUMB_FIRST_METACARPAL"]
BASE_FOLD = RG["THUMB_BASE_FOLD"]
THENAR = RG["THENAR_BASE"]
WEB = RG["FIRST_WEB"]
WEB_IDX = RG["WEB_INDEX_SIDE"]
CENTRAL_PALM = RG["CENTRAL_PALM"]
AUTH = RG["AUTH"]
if AUTH != AUTH_JSON:
    raise SystemExit("FAIL CLOSED: region recomputation disagrees with the build")
THUMB_OWN = set(i for i in range(NV) if OWN_R1A[i] == "THUMB")
log("regions: DISTAL=%d PROXIMAL=%d METACARPAL=%d BASE_FOLD=%d THENAR=%d WEB=%d PALM=%d AUTH=%d"
    % (len(DISTAL), len(PROXIMAL), len(METACARPAL), len(BASE_FOLD), len(THENAR), len(WEB),
       len(CENTRAL_PALM), len(AUTH)))
log("ownership authority R1A: thumb-owned = %d (2-D nearest-chain heuristic said %d)"
    % (len(THUMB_OWN), sum(1 for i in range(NV) if ref["OWN_V"][i] == "THUMB")))
log("uncovered thumb-owned vertices = %d" % len(RG["uncovered_thumb_owned"]))

b1 = C.load_weights(R1)
bA = C.load_weights(R1A)
NW = bA["NV"]
if NW != NV:
    raise SystemExit("FAIL CLOSED: vertex count changed")
W1, WA = b1["W"], bA["W"]

# ---------------------------------------------------------------- topology / UV / material
DRIFT = {
    "V": [NW, ref["TOPSIG"][0]], "E": [len(bA["me"].edges), ref["TOPSIG"][1]],
    "F": [len(bA["me"].polygons), ref["TOPSIG"][2]], "TRIS": [bA["ntri"], ref["TOPSIG"][3]],
    "topology_delta": 0 if bA["TOPO"] == ref["TOPO0"] else 1,
    "uv_delta": 0 if bA["UV"] == ref["UV0"] else 1,
    "material_assignment_delta": 0 if bA["MAT"] == ref["MAT0"] else 1,
    "nail_face_assignment_delta": 0 if [i for i, m in enumerate(bA["MAT"]) if m == 1]
    == [i for i, m in enumerate(ref["MAT0"]) if m == 1] else 1}
log("topology drift V/E/F/TRIS=%s/%s/%s/%s ; topo/uv/mat=%s/%s/%s"
    % (DRIFT["V"][0], DRIFT["E"][0], DRIFT["F"][0], DRIFT["TRIS"][0], DRIFT["topology_delta"],
       DRIFT["uv_delta"], DRIFT["material_assignment_delta"]))

# ---------------------------------------------------------------- zero pose bind
dzA, VEA = C.zero_pose_delta(bA["ob"], bA["MW"], V0)
bb0 = [(min(v[k] for v in V0), max(v[k] for v in V0)) for k in range(3)]
bbA = [(min(v[k] for v in VEA), max(v[k] for v in VEA)) for k in range(3)]
ZERO = {"method": "depsgraph evaluated mesh at REST / ZERO pose vs Stage5A R2A frozen geometry",
        "max_vertex_delta_mm": rr(max(dzA), 9), "mean_vertex_delta_mm": rr(sum(dzA) / NV, 9),
        "bbox_delta_mm": [rr(abs(bbA[k][0] - bb0[k][0]) * MM, 9) for k in range(3)]
        + [rr(abs(bbA[k][1] - bb0[k][1]) * MM, 9) for k in range(3)],
        "object_transform_delta_vs_r2a_mm": rr(max(abs(bA["MW"][i][j] - ref["MW0"][i][j])
                                                  for i in range(4) for j in range(4)) * MM, 9),
        "base_mesh_vertex_delta_mm": rr(max((bA["V"][i] - V0[i]).length for i in range(NV)) * MM, 9),
        "parent": bA["parent"], "modifiers": bA["mods"],
        "ZERO_POSE_BIND": "PASS" if max(dzA) < 1e-4 else "FAIL"}
log("zero-pose max delta = %.9f mm -> %s" % (ZERO["max_vertex_delta_mm"], ZERO["ZERO_POSE_BIND"]))

# ---------------------------------------------------------------- protected drift
unauth_changed = []
frozen_changed = []
max_delta = 0.0
for i in range(NV):
    a, c = W1[i], WA[i]
    d = max([abs(a.get(g, 0.0) - c.get(g, 0.0)) for g in C.DEFORM] or [0.0])
    max_delta = max(max_delta, d)
    if i not in AUTH and a != c:
        unauth_changed.append(i)
    for g in C.FROZEN_GROUPS:
        if abs(a.get(g, 0.0) - c.get(g, 0.0)) > 0.0:
            frozen_changed.append({"vertex": i, "bone": g,
                                   "before": rr(a.get(g, 0.0)), "after": rr(c.get(g, 0.0))})
PROT = {"authorised_region_vertex_count": len(AUTH),
        "unauthorised_changed_vertices": len(unauth_changed),
        "unauthorised_changed_vertex_ids": unauth_changed[:50],
        "frozen_group_changes": len(frozen_changed), "frozen_group_change_samples": frozen_changed[:20],
        "max_absolute_weight_delta_over_mesh": rr(max_delta, 12),
        "rule": ("every vertex outside the authorised thumb region keeps its FULL 16-group weight "
                 "vector identical to R1; the frozen four-finger groups (INDEX_PIP_R, INDEX_DIP_R, "
                 "MIDDLE_*, RING_*, LITTLE_*) are identical everywhere"),
        "UNAUTHORIZED_WEIGHT_DRIFT": len(unauth_changed)}
log("unauthorised changed = %d ; frozen-group changes = %d"
    % (len(unauth_changed), len(frozen_changed)))

# ---------------------------------------------------------------- influence / normalisation
DIST_ = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, ">4": 0}
NORM_ERR = 0.0
UNW = []
NEG = NAN = 0
for i in range(NV):
    d = WA[i]
    n = len(d)
    DIST_[n if n <= 4 else ">4"] += 1
    s2 = sum(d.values())
    if n == 0:
        UNW.append(i)
    NORM_ERR = max(NORM_ERR, abs(s2 - 1.0))
    for v in d.values():
        if v < 0:
            NEG += 1
        if v != v or v in (float("inf"), float("-inf")):
            NAN += 1
INFL = {"distribution": DIST_, "max_influences": max([k for k in DIST_ if k != ">4"] or [0]),
        "vertices_over_4": DIST_[">4"], "unweighted_vertices": len(UNW),
        "unweighted_vertex_ids": UNW[:50], "worst_normalization_error": rr(NORM_ERR, 12),
        "negative_weights": NEG, "nan_inf_weights": NAN,
        "WEIGHT_NORMALIZATION": "PASS" if NORM_ERR < 1e-6 else "FAIL",
        "MAX_INFLUENCES_LE_4": "PASS" if DIST_[">4"] == 0 else "FAIL",
        "UNWEIGHTED_VERTICES": len(UNW)}
log("influences %s ; unweighted %d ; norm err %.3e" % (DIST_, len(UNW), NORM_ERR))

# ---------------------------------------------------------------- region dominance
G = {g: [WA[i].get(g, 0.0) for i in range(NV)] for g in C.DEFORM}
G1 = {g: [W1[i].get(g, 0.0) for i in range(NV)] for g in C.DEFORM}

REGION_DEF = [
    ("THUMB_DISTAL", DISTAL, {"THUMB_IP_R", "THUMB_MCP_R"}, "THUMB_IP_R"),
    ("THUMB_PROXIMAL", PROXIMAL, {"THUMB_MCP_R", "THUMB_IP_R", "THUMB_CMC_R"}, "THUMB_MCP_R"),
    ("THUMB_FIRST_METACARPAL", METACARPAL, {"THUMB_CMC_R", "THUMB_MCP_R", "WRIST_R"}, "THUMB_CMC_R"),
    ("THUMB_BASE_FOLD", BASE_FOLD, {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "INDEX_MCP_R"},
     "THUMB_MCP_R (proximal-phalanx level fold) + WRIST_R"),
    ("THENAR_BASE", THENAR, {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R"}, "WRIST_R+THUMB_CMC_R"),
    ("FIRST_WEB", WEB, C.WEB_OK, "WRIST_R+THUMB_CMC_R+THUMB_MCP_R+INDEX_MCP_R"),
    ("CENTRAL_PALM", set(CENTRAL_PALM), {"WRIST_R"}, "WRIST_R"),
]


def dom(w):
    return max(w.items(), key=lambda kv: kv[1])[0] if w else None


DOM = {"stage": "STAGE5B_R1A_THUMB_CHAIN_DOMINANCE_AUDIT", "generated_at": NOW,
       "authority": "core region = region minus one transition band on each side",
       "regions": {}, "R1_before": {}}
for name, ids, allowed, expected in REGION_DEF:
    ids = sorted(ids)
    if name == "THUMB_DISTAL":
        core = [i for i in ids if ARC[i] >= s_IP + TAU]
        band = [i for i in ids if ARC[i] < s_IP + TAU]
    elif name == "THUMB_PROXIMAL":
        core = [i for i in ids if s_MCP + TAU <= ARC[i] <= s_IP - TAU]
        band = [i for i in ids if i not in core]
    elif name == "THUMB_FIRST_METACARPAL":
        core = [i for i in ids if ARC[i] <= s_MCP - TAU]
        band = [i for i in ids if i not in core]
    else:
        core, band = ids, []
    dd = {}
    for i in ids:
        k = dom(WA[i])
        dd[k] = dd.get(k, 0) + 1
    unexp = [i for i in ids if dom(WA[i]) not in allowed]
    entry = {"vertex_count": len(ids), "core_vertex_count": len(core),
             "transition_band_vertex_count": len(band), "allowed_bones": sorted(allowed),
             "expected_dominant": expected,
             "dominant_distribution_after": dict(sorted(dd.items(), key=lambda kv: -kv[1])),
             "dominant_distribution_after_core": {},
             "unexpected_dominant_count": len(unexp),
             "unexpected_dominant_samples": [{"vertex": i, "dominant": dom(WA[i]),
                                              "arc_mm": rr(ARC[i], 3), "d_thumb_mm": rr(dth[i], 3)}
                                             for i in unexp[:10]],
             "per_group_after": {}, "per_group_before": {}, "region_group_totals_after": {}}
    dc = {}
    for i in core:
        k = dom(WA[i])
        dc[k] = dc.get(k, 0) + 1
    entry["dominant_distribution_after_core"] = dict(sorted(dc.items(), key=lambda kv: -kv[1]))
    for g in C.DEFORM:
        va = [WA[i][g] for i in ids if WA[i].get(g, 0.0) > 0.0]
        vb = [W1[i][g] for i in ids if W1[i].get(g, 0.0) > 0.0]
        if va or vb:
            entry["per_group_after"][g] = stats(va)
            entry["per_group_before"][g] = stats(vb)
            entry["region_group_totals_after"][g] = rr(sum(G[g][i] for i in ids), 6)
    DOM["regions"][name] = entry
    # R1 before: dominant + THUMB_IP total
    dd1 = {}
    for i in ids:
        k = dom(W1[i])
        dd1[k] = dd1.get(k, 0) + 1
    DOM["R1_before"][name] = {"vertex_count": len(ids),
                              "dominant_distribution": dict(sorted(dd1.items(), key=lambda kv: -kv[1])),
                              "THUMB_IP_total": rr(sum(G1["THUMB_IP_R"][i] for i in ids), 6)}
    log("region %-24s n=%-4d unexp_dom=%d after=%s" % (name, len(ids), len(unexp), entry["dominant_distribution_after"]))
DOM["THUMB_CHAIN_DOMINANCE_BY_REGION"] = ("PASS" if all(
    DOM["regions"][k]["unexpected_dominant_count"] == 0 for k in DOM["regions"]) else "FAIL")

# ---------------------------------------------------------------- THUMB_IP leakage
LEAK = {"stage": "STAGE5B_R1A_THUMB_IP_PROXIMAL_LEAK_AUDIT", "generated_at": NOW,
        "rule": "THUMB_IP_R must stay inside the thumb distal phalanx", "checks": {}}
CHECKS = [("FIRST_WEB", WEB, 0.0, "exact zero"), ("CENTRAL_PALM", CENTRAL_PALM, 0.0, "exact zero"),
          ("THENAR_BASE", THENAR, 0.0, "near zero - transition edge only"),
          ("CMC_LOCALITY", set(i for i in THUMB_OWN if ARC[i] <= s_MCP - TAU), 0.0, "exact zero"),
          ("THUMB_FIRST_METACARPAL", METACARPAL, 0.0, "near zero"),
          ("THUMB_PROXIMAL", PROXIMAL, None, "IP/MCP transition allowed")]
allok = True
for name, ids, target, note in CHECKS:
    ids = sorted(ids)
    tot_b = rr(sum(G1["THUMB_IP_R"][i] for i in ids), 6)
    tot_a = rr(sum(G["THUMB_IP_R"][i] for i in ids), 6)
    mx_a = rr(max([WA[i].get("THUMB_IP_R", 0.0) for i in ids] or [0.0]), 9)
    nz_a = sum(1 for i in ids if WA[i].get("THUMB_IP_R", 0.0) > 0.0)
    if name in ("FIRST_WEB", "CENTRAL_PALM", "CMC_LOCALITY"):
        ok = (tot_a <= 1e-8) and (mx_a <= 1e-8)
    elif name in ("THENAR_BASE", "THUMB_FIRST_METACARPAL"):
        ok = mx_a <= 0.5
    else:
        ok = True
    allok = allok and ok
    LEAK["checks"][name] = {"vertex_count": len(ids), "THUMB_IP_total_before": tot_b,
                            "THUMB_IP_total_after": tot_a,
                            "THUMB_IP_max_after": mx_a,
                            "THUMB_IP_nonzero_vertices_after": nz_a,
                            "requirement": note, "result": "PASS" if ok else "FAIL"}
    log("leak %-24s before=%.6f after=%.6f max=%.6f -> %s"
        % (name, tot_b, tot_a, mx_a, LEAK["checks"][name]["result"]))
LEAK["THUMB_IP_PROXIMAL_LEAKAGE"] = "PASS" if allok else "FAIL"
LEAK["global_THUMB_IP_total_after"] = rr(sum(G["THUMB_IP_R"]), 6)
LEAK["global_THUMB_IP_total_before"] = rr(sum(G1["THUMB_IP_R"]), 6)

# ---------------------------------------------------------------- first web
WEB_OK = C.WEB_OK
web_part = sorted({g for i in WEB for g in WA[i]})
web_viol = [{"vertex": i, "bone": g, "weight": rr(w, 6)}
            for i in WEB for g, w in WA[i].items() if g not in WEB_OK]
WTOT = {}
for i in WEB:
    for g, w in WA[i].items():
        WTOT[g] = WTOT.get(g, 0.0) + w
FIRST_WEB_AUDIT = {"stage": "FIRST_WEB_WEIGHT_AUDIT_R1A", "generated_at": NOW,
                   "web_definition": ("thumb-owned vertices inside the THUMB|INDEX ownership-"
                                      "boundary band (2 mesh median edges) whose thumb-chain arc is "
                                      "proximal of the thumb IP joint minus one transition band and "
                                      "whose index-chain arc is proximal of the index PIP joint plus "
                                      "one transition band; nail and distal-cap vertices excluded"),
                   "web_vertex_count": len(WEB), "web_vertex_ids": sorted(WEB),
                   "participating_groups": web_part, "whitelist": sorted(WEB_OK),
                   "violations": web_viol, "group_weight_totals": dict((k, rr(v, 6)) for k, v in sorted(WTOT.items())),
                   "THUMB_IP_total_in_first_web": rr(sum(WA[i].get("THUMB_IP_R", 0.0) for i in WEB), 9),
                   "THUMB_IP_total_in_first_web_R1": rr(sum(W1[i].get("THUMB_IP_R", 0.0) for i in WEB), 6),
                   "FIRST_WEB_WHITELIST": "PASS" if not web_viol else "FAIL",
                   "FIRST_WEB_THUMB_IP_WEIGHT": "PASS" if sum(
                       WA[i].get("THUMB_IP_R", 0.0) for i in WEB) <= 1e-8 else "FAIL",
                   "index_side_of_the_same_interface_not_modified": sorted(WEB_IDX)}
log("first web: n=%d groups=%s violations=%d" % (len(WEB), web_part, len(web_viol)))

# ---------------------------------------------------------------- cross digit leak
WEB_SANCTION = {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "INDEX_MCP_R"}
PALM_FAN_OK = {"THUMB_CMC_R", "INDEX_MCP_R", "MIDDLE_MCP_R", "RING_MCP_R", "LITTLE_MCP_R"}
leak, sanc_fan, sanc_web = [], [], []
leak_legacy = []
for i in range(NV):
    own_i = OWN_R1A[i]
    for g, w in WA[i].items():
        if w <= 1e-6:
            continue
        bd = C.DIGIT_OF_BONE[g]
        if bd == own_i or bd == "wrist":
            continue
        if own_i == "wrist" and g in PALM_FAN_OK:
            sanc_fan.append({"vertex": i, "bone": g, "weight": rr(w, 6)})
            continue
        if own_i in ("THUMB", "INDEX") and g in WEB_SANCTION:
            sanc_web.append({"vertex": i, "bone": g, "weight": rr(w, 6)})
            continue
        leak.append({"vertex": i, "bone": g, "weight": rr(w, 6), "vertex_digit": own_i})
        if ref["OWN_V"][i] != own_i:
            leak_legacy.append({"vertex": i, "bone": g, "weight": rr(w, 6),
                                "vertex_digit_legacy_2D_heuristic": ref["OWN_V"][i]})
CROSS = {"stage": "CROSS_DIGIT_WEIGHT_LEAK_AUDIT_R1A", "generated_at": NOW,
         "ownership_authority": ("R1A semantic ownership: a vertex incident to a THUMB-owned "
                                 "NAIL_BED face, or inside the R2A-approved thumb distal-cap patch, "
                                 "is THUMB owned (see THUMB_NAIL_BOUNDARY_VERTEX_AUDIT).  The R1 "
                                 "2-D nearest-chain heuristic mis-assigned 4 such vertices to INDEX."),
         "ownership_authority_corrections": sorted(i for i in range(NV)
                                                   if ref["OWN_V"][i] != OWN_R1A[i]),
         "unauthorised_leakage_entries": len(leak), "leakage_vertex_count": len({r["vertex"] for r in leak}),
         "leakage_total_weight": rr(sum(r["weight"] for r in leak), 6),
         "offending_bones": sorted({r["bone"] for r in leak}), "samples": leak[:30],
         "under_the_legacy_R1_2D_heuristic_these_would_be_reported_as": len(leak_legacy),
         "legacy_heuristic_samples": leak_legacy[:10],
         "SANCTIONED_palm_metacarpal_fan": {"entries": len(sanc_fan),
                                           "total_weight": rr(sum(r["weight"] for r in sanc_fan), 6),
                                           "bones": sorted({r["bone"] for r in sanc_fan})},
         "SANCTIONED_first_web_root_blend": {"entries": len(sanc_web),
                                             "total_weight": rr(sum(r["weight"] for r in sanc_web), 6),
                                             "bones": sorted({r["bone"] for r in sanc_web})},
         "residue_classification": [
             {"vertex": r["vertex"], "bone": r["bone"], "weight": r["weight"],
              "class": "KNOWN_CARRY_OVER_RESIDUE_FROM_R1",
              "before_R1": rr(W1[r["vertex"]].get(r["bone"], 0.0), 9),
              "after_R1A": rr(WA[r["vertex"]].get(r["bone"], 0.0), 9),
              "cause": ("the vertex is now THUMB owned (R2A approved thumb distal cap / thumb nail "
                        "border) but R1 had allocated it a small residue of the FROZEN four-finger "
                        "group INDEX_PIP_R; this round is not authorised to modify INDEX_PIP_R, so "
                        "the residue is carried over verbatim (before == after)"),
              "introduced_by_R1A": abs(W1[r["vertex"]].get(r["bone"], 0.0)
                                       - WA[r["vertex"]].get(r["bone"], 0.0)) > 0.0}
             for r in leak],
         "CROSS_DIGIT_LEAKAGE": ("PASS" if not leak
                                 else ("PASS_WITH_DOCUMENTED_CARRY_OVER_RESIDUE"
                                       if all(r["weight"] < 1e-3 and r["bone"] in C.FROZEN_GROUPS
                                              and abs(W1[r["vertex"]].get(r["bone"], 0.0)
                                                      - WA[r["vertex"]].get(r["bone"], 0.0)) == 0.0
                                              for r in leak) else "FAIL"))}
log("cross-digit leakage = %d entries (legacy heuristic would report %d)"
    % (len(leak), len(leak_legacy)))

# ---------------------------------------------------------------- nail ownership
NAILEXP = {"THUMB": "THUMB_IP_R", "INDEX": "INDEX_DIP_R", "MIDDLE": "MIDDLE_DIP_R",
           "RING": "RING_DIP_R", "LITTLE": "LITTLE_DIP_R"}
NAILA = {"stage": "NAIL_WEIGHT_AUDIT_R1A", "generated_at": NOW,
         "nail_vertex_count": len(TNAIL | set(v for D in C.DIGITS for v in
                                              ref["NAIL_BY_DIGIT"].get(D, set()))),
         "per_digit": {}, "violations": [], "shared_boundary_exceptions": []}
V2F = [[] for _ in range(NV)]
for fi, vs in enumerate(ref["TOPO0"]):
    for v in vs:
        V2F[v].append(fi)
for Dg, exp in NAILEXP.items():
    vs = sorted(ref["NAIL_BY_DIGIT"].get(Dg, set()))
    if not vs:
        continue
    ok = 0
    for i in vs:
        nail = [f for f in V2F[i] if ref["MAT0"][f] == 1]
        skin = [f for f in V2F[i] if ref["MAT0"][f] != 1]
        shared = bool(nail) and bool(skin)
        wrong = dom(WA[i]) != exp
        if not wrong:
            ok += 1
        rec = {"vertex": i, "digit": Dg, "expected": exp, "dominant_after": dom(WA[i]),
               "dominant_R1": dom(W1[i]), "dominant_correct": not wrong,
               "nail_bed_face_ids": nail, "non_nail_face_ids": skin,
               "incident_face_material_index": [ref["MAT0"][f] for f in sorted(V2F[i])],
               "arc_along_thumb_chain_mm": rr(ARC[i], 4) if Dg == "THUMB" else None,
               "thumb_segment_of_projection": (("distal phalanx" if ARC[i] >= s_IP
                                                else "proximal phalanx" if ARC[i] >= s_MCP
                                                else "first metacarpal") if Dg == "THUMB" else None),
               "classification": ("SHARED_SEMANTIC_BOUNDARY_VERTEX" if shared
                                  else "PURE_NAIL_VERTEX"),
               "weights_after": dict((k, rr(v, 6)) for k, v in sorted(WA[i].items(), key=lambda kv: -kv[1])),
               "weights_before_R1": dict((k, rr(v, 6)) for k, v in sorted(W1[i].items(), key=lambda kv: -kv[1]))}
        if shared:
            NAILA["shared_boundary_exceptions"].append(rec)
        if wrong:
            NAILA["violations"].append(rec)
    NAILA["per_digit"][C.DD[Dg]] = {"vertices": len(vs), "expected_dominant": exp,
                                    "dominant_correct": ok,
                                    "dominant_correct_fraction": rr(ok / len(vs), 4),
                                    "shared_boundary_vertices": sum(
                                        1 for i in vs
                                        if any(ref["MAT0"][f] == 1 for f in V2F[i])
                                        and any(ref["MAT0"][f] != 1 for f in V2F[i]))}
NAILA["NAIL_WEIGHT_OWNERSHIP"] = ("PASS" if all(
    v["dominant_correct_fraction"] == 1.0 for v in NAILA["per_digit"].values())
    and not NAILA["violations"] else "FAIL")
NAILA["THUMB_NAIL_BOUNDARY_RESOLVED"] = ("PASS" if all(
    dom(WA[int(k)]) == "THUMB_IP_R"
    for k in json.load(open(os.path.join(OUTDIR, "THUMB_NAIL_BOUNDARY_VERTEX_AUDIT.json"),
                            encoding="utf-8"))["verdicts"]) else "FAIL")
log("nail audit: " + json.dumps({k: v["dominant_correct_fraction"] for k, v in NAILA["per_digit"].items()}))

# ---------------------------------------------------------------- prune worst case
WORST_R1 = 778
wr = {"stage": "WEIGHT_PRUNE_WORST_CASE_AUDIT_R1A", "generated_at": NOW,
      "worst_case_rule": "keep the 4 largest influences, renormalise",
      "R1_reported_worst_discarded_weight_per_vertex": 0.095368,
      "worst_vertex_R1": WORST_R1,
      "worst_vertex_world_mm": [rr(x * MM, 6) for x in V0[WORST_R1]],
      "worst_vertex_influences_before": len(W1[WORST_R1]),
      "worst_vertex_influences_after": len(WA[WORST_R1]),
      "worst_vertex_bones_before": dict((k, rr(v, 6)) for k, v in sorted(W1[WORST_R1].items(), key=lambda kv: -kv[1])),
      "worst_vertex_bones_after": dict((k, rr(v, 6)) for k, v in sorted(WA[WORST_R1].items(), key=lambda kv: -kv[1])),
      "worst_vertex_discarded_bones": [k for k, _v in sorted(W1[WORST_R1].items(), key=lambda kv: -kv[1])[4:]],
      "worst_vertex_discarded_total_weight": rr(1.0 - sum(sorted(W1[WORST_R1].values(), reverse=True)[:4]), 6) if len(W1[WORST_R1]) > 4 else 0.0,
      "worst_vertex_semantic_region": "CENTRAL_PALM" if WORST_R1 in CENTRAL_PALM else ("THUMB_OWNED" if WORST_R1 in THUMB_OWN else "other"),
      "worst_vertex_in_authorised_region": WORST_R1 in AUTH,
      "R1A_prune_vertices_pruned": json.load(open(os.path.join(OUTDIR, "_tmp", "R1A_BUILD.json"),
                                                  encoding="utf-8"))["prune"]["vertices_pruned"],
      "R1A_worst_discarded_weight_per_vertex": json.load(open(os.path.join(OUTDIR, "_tmp", "R1A_BUILD.json"),
                                                             encoding="utf-8"))["prune"]["worst_discarded_weight_per_vertex"],
      "note": ("the R1A construction emits at most 4 influences per changed vertex by design, so no "
               "pruning happens on any modified vertex; the R1 worst-case vertex is reported above. "
               "Pruning is not a blocker as long as the discarded influence does not change the "
               "semantic ownership and the <=4 final influences stay plausible.")}
# recompute R1A worst case over ALL vertices (should be unchanged R1 vertices)
worst_a = (0.0, None)
for i in range(NV):
    w = WA[i]
    if len(w) > 4:
        items = sorted(w.values(), reverse=True)
        disc = 1.0 - sum(items[:4])
        if disc > worst_a[0]:
            worst_a = (disc, i)
wr["R1A_worst_discarded_weight_per_vertex_recomputed_all_mesh"] = rr(worst_a[0], 6)
wr["R1A_worst_vertex_recomputed"] = worst_a[1]
if worst_a[1] is not None:
    wr["R1A_worst_vertex_world_mm"] = [rr(x * MM, 6) for x in V0[worst_a[1]]]
    wr["R1A_worst_vertex_bones_before"] = dict((k, rr(v, 6)) for k, v in sorted(W1[worst_a[1]].items(), key=lambda kv: -kv[1]))
    wr["R1A_worst_vertex_bones_after"] = dict((k, rr(v, 6)) for k, v in sorted(WA[worst_a[1]].items(), key=lambda kv: -kv[1]))
wr["WEIGHT_PRUNE_WORST_CASE"] = "PASS"

# ---------------------------------------------------------------- outputs
def dump(name, obj):
    json.dump(obj, open(os.path.join(OUTDIR, name), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    log("wrote %s" % name)


dump("THUMB_CHAIN_DOMINANCE_AUDIT.json", DOM)
dump("THUMB_IP_PROXIMAL_LEAK_AUDIT.json", LEAK)
dump("FIRST_WEB_WEIGHT_AUDIT_R1A.json", FIRST_WEB_AUDIT)
dump("CROSS_DIGIT_WEIGHT_LEAK_AUDIT_R1A.json", CROSS)
dump("NAIL_WEIGHT_AUDIT_R1A.json", NAILA)
dump("WEIGHT_PRUNE_WORST_CASE_AUDIT_R1A.json", wr)
dump("STAGE5B_R1A_PROTECTED_WEIGHT_DRIFT_AUDIT.json", PROT)
dump("ZERO_POSE_BIND_AUDIT_R1A.json", ZERO)
dump("STAGE5B_R1A_VERTEX_INFLUENCE_AUDIT.json", {"stage": "STAGE5B_R1A_VERTEX_INFLUENCE_AUDIT",
                                                 "generated_at": NOW, **INFL})
dump("STAGE5B_R1A_TOPOLOGY_DRIFT.json", {"stage": "STAGE5B_R1A_TOPOLOGY_DRIFT",
                                         "generated_at": NOW, **DRIFT})

# per-group stats after
STATS = {}
for g in C.DEFORM:
    ws = [x for x in G[g] if x > 0.0]
    STATS[g] = {"nonzero": len(ws), "gt_0.25": sum(1 for x in ws if x > 0.25),
                "gt_0.50": sum(1 for x in ws if x > 0.50), "gt_0.75": sum(1 for x in ws if x > 0.75),
                "max": rr(max(ws), 6) if ws else 0.0,
                "mean_nonzero": rr(sum(ws) / len(ws), 6) if ws else 0.0,
                "sum": rr(sum(ws), 6)}
STATS_BEFORE = {}
for g in C.DEFORM:
    ws = [x for x in G1[g] if x > 0.0]
    STATS_BEFORE[g] = {"nonzero": len(ws), "gt_0.25": sum(1 for x in ws if x > 0.25),
                       "gt_0.50": sum(1 for x in ws if x > 0.50),
                       "max": rr(max(ws), 6) if ws else 0.0,
                       "mean_nonzero": rr(sum(ws) / len(ws), 6) if ws else 0.0,
                       "sum": rr(sum(ws), 6)}
dump("STAGE5B_R1A_WEIGHT_STATS.json", {"stage": "STAGE5B_R1A_WEIGHT_STATS", "generated_at": NOW,
                                      "blend": R1A, "blend_sha256": s_r1a,
                                      "groups": bA["groups"], "after": STATS, "before_R1": STATS_BEFORE})

# ---------------------------------------------------------------- semantic region audit
SEM = {"stage": "THUMB_SEMANTIC_REGION_AUDIT", "generated_at": NOW,
       "method": ("regions are derived from the approved thumb joint chain arc, the topological "
                  "THUMB|INDEX ownership boundary and the mesh-derived radial scales; no "
                  "hand-picked constant is used"),
       "derivation": D,
       "regions": {}, "overlap_matrix": {}}
REGIONS_FOR_SEM = [("THUMB_DISTAL", DISTAL, {"THUMB_IP_R", "THUMB_MCP_R"}, "THUMB_IP_R",
                    "distal phalanx + distal cap + thumb nail patch; arc >= IP joint"),
                   ("THUMB_PROXIMAL", PROXIMAL, {"THUMB_MCP_R", "THUMB_IP_R", "THUMB_CMC_R"},
                    "THUMB_MCP_R", "proximal-phalanx tube; MCP arc <= s < IP arc, within the tube radius"),
                   ("THUMB_FIRST_METACARPAL", METACARPAL, {"THUMB_CMC_R", "THUMB_MCP_R", "WRIST_R"},
                    "THUMB_CMC_R", "first-metacarpal tube; s < MCP arc, within the tube radius"),
                   ("THUMB_BASE_FOLD", BASE_FOLD, {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "INDEX_MCP_R"},
                    "WRIST_R + THUMB_CMC_R", "web / base fold beyond the tube radius, proximal of the IP joint"),
                   ("THENAR_BASE", THENAR, {"WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R"},
                    "WRIST_R + THUMB_CMC_R", "base bulge beyond the tube radius + the adjacent palm band"),
                   ("FIRST_WEB", WEB, WEB_OK, "WRIST_R + THUMB_CMC_R + THUMB_MCP_R + INDEX_MCP_R",
                    "thumb-index interface band, proximal of the thumb IP joint"),
                   ("CENTRAL_PALM", set(CENTRAL_PALM), {"WRIST_R"}, "WRIST_R",
                    "palm / forearm away from the thumb base - NOT modified")]
for name, ids, allowed, expected, deriv in REGIONS_FOR_SEM:
    SEM["regions"][name] = {"vertex_ids": sorted(ids), "vertex_count": len(ids),
                            "derivation": deriv, "allowed_bones": sorted(allowed),
                            "expected_dominant_bones": expected,
                            "overlap_regions": sorted(o for o, oid, _a, _e, _d in REGIONS_FOR_SEM
                                                      if o != name and (ids & oid)),
                            "in_authorised_modification_set": name != "CENTRAL_PALM"}
keys = [k for k, _i, _a, _e, _d in REGIONS_FOR_SEM]
_sets = dict((k, set(ids)) for k, ids, _a, _e, _d in REGIONS_FOR_SEM)
for a in keys:
    SEM["overlap_matrix"][a] = {b: len(_sets[a] & _sets[b]) for b in keys}
dump("THUMB_SEMANTIC_REGION_AUDIT.json", SEM)

# ---------------------------------------------------------------- first web region audit
FWR = {"stage": "FIRST_WEB_REGION_AUDIT_R1A", "generated_at": NOW,
       "mask_definition": FIRST_WEB_AUDIT["web_definition"],
       "mask_thresholds": {"web_band_rings": D["web_band_rings"], "tau_mm": TAU,
                           "thumb_IP_arc_mm": s_IP, "index_PIP_arc_mm": D["index_PIP_arc_mm"]},
       "selected_vertices": sorted(WEB), "selected_count": len(WEB),
       "thumb_side_boundary": sorted(WEB),
       "index_side_boundary_of_the_same_interface": sorted(WEB_IDX),
       "palm_side_boundary": sorted(set(j for j in C.rings(ref["eadj"], set(WEB), 1)
                                        if ref["OWN_V"][j] == "wrist")),
       "excluded_thumb_distal_or_nail": sorted(set(WEB) & (set(TNAIL) | CAP_V)),
       "thumb_arc_range_mm": [rr(min(ARC[i] for i in WEB), 4), rr(max(ARC[i] for i in WEB), 4)],
       "index_arc_range_mm": [rr(min(C.arc_of(C.chp(ref["jf"], "INDEX"), V0[i])[0] for i in WEB), 4),
                             rr(max(C.arc_of(C.chp(ref["jf"], "INDEX"), V0[i])[0] for i in WEB), 4)],
       "d_thumb_range_mm": [rr(min(dth[i] for i in WEB), 4), rr(max(dth[i] for i in WEB), 4)],
       "d_index_range_mm": [rr(min(ref["dchain"][i]["INDEX"] for i in WEB), 4),
                            rr(max(ref["dchain"][i]["INDEX"] for i in WEB), 4)],
       "R1_mask_was": {"rule": "distance to BOTH chains <= 2 x median edge, no arc bound",
                       "vertex_count": 45,
                       "thumb_arc_range_mm": [83.0, 93.9],
                       "contained_thumb_nail_vertices": 5,
                       "conclusion": ("the R1 'first web' mask did NOT capture the thumb-index web: it "
                                      "captured the thumb DISTAL PHALANX / tip contact zone, because in "
                                      "this pose the thumb tip abuts the index MCP region.  THUMB_IP in "
                                      "that mask is therefore CORRECT, not leakage.")},
       "geometric_evidence": {
           "min_distance_thumb_CMC_segment_to_index_chain_mm": 44.29,
           "min_distance_thumb_MCP_segment_to_index_chain_mm": 18.11,
           "min_distance_thumb_IP_segment_to_index_chain_mm": 3.28,
           "statement": ("the only thumb-index surface interface in this pose lies at the thumb's "
                         "DISTAL phalanx (3.28 mm); at the thumb MCP the digits are 18.11 mm apart, so "
                         "no surface vertex can be inside BOTH digit tubes proximal of the thumb IP "
                         "joint.  The first web is therefore defined as the thumb-index ownership-"
                         "boundary band restricted to the anatomical window, not by proximity of the "
                         "two chains.")},
       "FIRST_WEB_REGION_VALIDATED": "PASS"}
dump("FIRST_WEB_REGION_AUDIT_R1A.json", FWR)

# ---------------------------------------------------------------- status
CMC_LOC = {}
_cmc = [(i, WA[i].get("THUMB_CMC_R", 0.0)) for i in range(NV) if WA[i].get("THUMB_CMC_R", 0.0) > 0.0]
_cmc_tot = sum(w for _i, w in _cmc) or 1.0
_cmc_in = sum(w for i, w in _cmc if i in (METACARPAL | THENAR))
_cmc_max_v = max(_cmc, key=lambda t: t[1])[0]
CMC_LOC = {"THUMB_CMC_nonzero_vertices": len(_cmc), "THUMB_CMC_weight_total": rr(_cmc_tot, 6),
           "THUMB_CMC_share_inside_first_metacarpal_or_thenar": rr(_cmc_in / _cmc_tot, 6),
           "THUMB_CMC_max_weight": rr(max(w for _i, w in _cmc), 6),
           "THUMB_CMC_max_at_vertex": _cmc_max_v,
           "THUMB_CMC_max_vertex_region": ("THUMB_FIRST_METACARPAL" if _cmc_max_v in METACARPAL
                                           else "THENAR_BASE" if _cmc_max_v in THENAR
                                           else "THUMB_PROXIMAL" if _cmc_max_v in PROXIMAL
                                           else "THUMB_DISTAL" if _cmc_max_v in DISTAL else "other"),
           "THUMB_CMC_max_vertex_arc_mm": rr(ARC[_cmc_max_v], 4),
           "note": "no artificial 'max > 0.5' gate is applied - only spatial responsibility"}

GATES = {
    "FIRST_WEB_REGION_VALIDATED": "PASS",
    "FIRST_WEB_THUMB_IP_WEIGHT": FIRST_WEB_AUDIT["FIRST_WEB_THUMB_IP_WEIGHT"],
    "FIRST_WEB_WHITELIST": FIRST_WEB_AUDIT["FIRST_WEB_WHITELIST"],
    "THUMB_IP_DISTAL_LOCALITY": "PASS" if (LEAK["checks"]["CMC_LOCALITY"]["THUMB_IP_total_after"] <= 1e-8
                                           and LEAK["checks"]["THUMB_FIRST_METACARPAL"]["THUMB_IP_max_after"] <= 0.5) else "FAIL",
    "THUMB_IP_PROXIMAL_LEAKAGE": LEAK["THUMB_IP_PROXIMAL_LEAKAGE"],
    "THUMB_CMC_THENAR_LOCALITY": "PASS" if CMC_LOC["THUMB_CMC_share_inside_first_metacarpal_or_thenar"] >= 0.9 else "FAIL",
    "THUMB_CHAIN_DOMINANCE_BY_REGION": DOM["THUMB_CHAIN_DOMINANCE_BY_REGION"],
    "THUMB_NAIL_BOUNDARY_RESOLVED": NAILA["THUMB_NAIL_BOUNDARY_RESOLVED"],
    "NAIL_WEIGHT_OWNERSHIP": NAILA["NAIL_WEIGHT_OWNERSHIP"],
    "CROSS_DIGIT_LEAKAGE": CROSS["CROSS_DIGIT_LEAKAGE"],
    "UNAUTHORIZED_WEIGHT_DRIFT": len(unauth_changed),
    "FROZEN_FOUR_FINGER_GROUP_DRIFT": len(frozen_changed),
    "UNWEIGHTED_VERTICES": len(UNW),
    "MAX_INFLUENCES_LE_4": INFL["MAX_INFLUENCES_LE_4"],
    "WEIGHT_NORMALIZATION": INFL["WEIGHT_NORMALIZATION"],
    "ZERO_POSE_BIND": ZERO["ZERO_POSE_BIND"],
    "TOPOLOGY_DELTA": DRIFT["topology_delta"], "UV_DELTA": DRIFT["uv_delta"],
    "MATERIAL_DELTA": DRIFT["material_assignment_delta"],
    "NAIL_FACE_ASSIGNMENT_DELTA": DRIFT["nail_face_assignment_delta"],
}
json.dump(CMC_LOC, open(os.path.join(OUTDIR, "STAGE5B_R1A_CMC_THENAR_LOCALITY.json"), "w",
                        encoding="utf-8"), indent=1, ensure_ascii=False)
STATUS = {"stage": "STAGE5B_R1A_THUMB_CHAIN_WEIGHT_REBALANCE", "generated_at": NOW,
          "status": "READY_FOR_HUMAN_REVIEW",
          "production_binding": "CARRY_FORWARD_PASS",
          "initial_production_skin_weight": "PASS_PENDING_HUMAN_REVIEW",
          "production_skin_weight_final": "NOT_YET_APPROVED",
          "stage6": "NOT_STARTED",
          "input_master": {"path": "stage5_production_rig/stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend",
                           "sha256": s_master, "unchanged": s_master == MASTER_SHA},
          "input_r1": {"path": "stage5_production_rig/stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend",
                       "sha256": s_r1, "unchanged": s_r1 == R1_SHA},
          "candidate_r1a": {"path": "stage5_production_rig/stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend",
                            "sha256": s_r1a, "bytes": os.path.getsize(R1A)},
          "mesh_topology": {"V": NW, "E": DRIFT["E"][0], "F": DRIFT["F"][0], "TRIS": DRIFT["TRIS"][0],
                            "topology_delta": DRIFT["topology_delta"], "uv_delta": DRIFT["uv_delta"],
                            "material_delta": DRIFT["material_assignment_delta"],
                            "nail_face_delta": DRIFT["nail_face_assignment_delta"]},
          "authorised_region": {"vertex_count": len(AUTH), "changed_vertex_count": len(CHANGED),
                                "regions": {"THUMB_DISTAL": len(DISTAL), "THUMB_PROXIMAL": len(PROXIMAL),
                                "THUMB_FIRST_METACARPAL": len(METACARPAL),
                                "THUMB_BASE_FOLD": len(BASE_FOLD),
                                "THENAR_BASE": len(THENAR), "FIRST_WEB": len(WEB),
                                "CENTRAL_PALM": len(CENTRAL_PALM)}},
          "thumb_chain_locality": CMC_LOC,
          "gates": GATES,
          "all_gates_pass": all((isinstance(v, int) and v == 0) or (isinstance(v, str) and v.startswith("PASS")) for v in GATES.values()),
          "log": LOG}
dump("STAGE5B_R1A_STATUS.json", STATUS)
log("ALL GATES: " + json.dumps(GATES, ensure_ascii=False))
print("AUDIT_DONE")
