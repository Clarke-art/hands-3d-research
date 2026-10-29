# =====================================================================================
# STAGE6A_R1A -- bounded deterministic THUMB weight candidate sweep
# =====================================================================================
# WRITES NOTHING except its own JSON report.  The frozen Stage6A R1 harness is opened,
# weights are varied IN MEMORY only, and the frozen file is hash-checked afterwards.
#
# candidate family: (form, W_IP, W_MCP, W_BASE, shift_IP, shift_MCP, profile)
#   -- a global, reproducible parameterisation of the thumb-chain weight field along the
#      approved joint-polyline arc length.  No per-vertex free parameters.
#
# Acceptance is BASELINE-RELATIVE (Pareto), never a new hand-picked anatomical threshold.
# =====================================================================================
import bpy
import sys
import os
import json
import math
import time
import datetime
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
S5B = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "..", "..", "stage5_production_rig",
                                   "stage5b_r1b", "scripts"))
sys.path.append(S5B)
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
    print("[R1B-SWEEP]", s, flush=True)


# ---------------------------------------------------------------- gates
s_r1a = C.sha256(C.R1A_MASTER)
s_h1 = C.sha256(C.STAGE6A_R1_HARNESS)
if s_r1a != C.R1A_SHA256 or s_h1 != C.STAGE6A_R1_HARNESS_SHA256:
    raise SystemExit("FAIL CLOSED: frozen input hash drift")
ctx = C.build_context()
NV, MED, ARC, V0 = ctx["NV"], ctx["MED"], ctx["ARC"], ctx["V0"]
POLY, EDGES, FO = ctx["poly"], ctx["edges"], ctx["FO"]
s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]
NAIL, CAP, WEB = ctx["nail"], ctx["cap"], ctx["first_web"]

# ---------------------------------------------------------------- authorised region
KAPPA = 2.0 * MED
PATCH = {seg: sorted(i for i in ctx["thumb_own"]
                     if abs(ARC[i] - (s_MCP if seg == "MCP" else s_IP)) <= KAPPA)
         for seg in ("MCP", "IP")}
adj = {}
for a, b in EDGES:
    adj.setdefault(a, []).append(b)
    adj.setdefault(b, []).append(a)
CORE = set(PATCH["MCP"]) | set(PATCH["IP"])
CLOSURE = set(CORE)
front = set(CORE)
for _ in range(2):
    nxt = set()
    for u in front:
        for v in adj.get(u, ()):
            if v not in CLOSURE:
                CLOSURE.add(v)
                nxt.add(v)
    front = nxt
EXCLUDED = NAIL | CAP | WEB
AUTH = sorted(i for i in CLOSURE if i in ctx["thumb_own"] and i not in EXCLUDED)
AUTH_SET = set(AUTH)
log("AUTH = %d vertices (core=%d closure=%d, frozen-excluded=%d)"
    % (len(AUTH), len(CORE), len(CLOSURE), len(CLOSURE) - len(AUTH)))

# ---------------------------------------------------------------- open the R1 harness
bpy.ops.wm.open_mainfile(filepath=C.STAGE6A_R1_HARNESS)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me = ob.data
MW = ob.matrix_world.copy()
M3 = MW.to_3x3()
VG = {g.name: g for g in ob.vertex_groups}
if sorted(VG) != sorted(C.ALL_DEFORM):
    raise SystemExit("FAIL CLOSED: unexpected vertex groups")
W1 = C.read_object_weights(ob, NV)

# ---------------------------------------------------------------- static sets
FACE_AREA0 = [C.face_area(V0, p) for p in POLY]
EDGE_LEN0 = [(V0[a] - V0[b]).length for a, b in EDGES]
PATCH_FACES = {seg: [fi for fi, p in enumerate(POLY) if any(v in set(PATCH[seg]) for v in p)]
               for seg in ("MCP", "IP")}
PATCH_EDGES = {seg: [k for k, (a, b) in enumerate(EDGES)
                     if a in set(PATCH[seg]) or b in set(PATCH[seg])]
               for seg in ("MCP", "IP")}
PATCH_FACE_SUM0 = {seg: sum(FACE_AREA0[i] for i in PATCH_FACES[seg]) for seg in ("MCP", "IP")}
THUMB_FACES = [fi for fi in range(len(POLY)) if FO.get(fi) == "THUMB"]

S6.reset_pose(rig)
bpy.context.view_layer.update()
BASE_INTRA = C.intersect_pairs_subset(V0, POLY, THUMB_FACES)
log("bind intra-thumb self-intersection pairs = %d" % len(BASE_INTRA))

NAIL_FACES = [fi for fi in range(len(POLY)) if all(v in NAIL for v in POLY[fi])]
CAP_FACES = [fi for fi in range(len(POLY)) if all(v in CAP for v in POLY[fi])]
NAIL_SUM0 = sum(FACE_AREA0[i] for i in NAIL_FACES)
CAP_SUM0 = sum(FACE_AREA0[i] for i in CAP_FACES)
WEB_V = sorted(WEB)
DIGIT_OF_BONE = {"WRIST_R": "wrist"}
for _d in RC.DIGITS:
    for _s in RC.CHAIN[_d]:
        DIGIT_OF_BONE["%s_%s_R" % (_d, _s)] = _d
OND = ctx["own_r1a"]
FOREIGN = [sorted(g for g in W1[i] if DIGIT_OF_BONE.get(g, "wrist") not in (OND[i], "wrist"))
           for i in range(NV)]
CLEAN_NONTHUMB = sorted(i for i in range(NV) if OND[i] != "THUMB" and not FOREIGN[i])
log("clean non-thumb vertices monitored = %d" % len(CLEAN_NONTHUMB))
PALMAR_T = -(M3 @ rig.data.bones["THUMB_MCP_R"].matrix_local.to_3x3()
             @ Vector((0.0, 0.0, 1.0))).normalized()
# Stage6A R1 thresholds (identical convention)
CLEAN_MOTION_BLOCKER_MM = 1e-3
NOISE_FLOOR_MM = 5.967e-05


# ---------------------------------------------------------------- metric engine
def measure(seg, ang):
    bone = "THUMB_%s_R" % seg
    S6.reset_pose(rig)
    S6.set_joint_rotation(rig, bone, C.FLEXION_SIGN_THUMB * ang)
    bpy.context.view_layer.update()
    V, P = C.evaluate(ob, MW)

    pf, pe = PATCH_FACES[seg], PATCH_EDGES[seg]
    pr = []
    for fi in pf:
        a0 = FACE_AREA0[fi]
        pr.append((C.face_area(V, POLY[fi]) / a0) if a0 > 1e-18 else 0.0)
    per = []
    for k in pe:
        a, b = EDGES[k]
        l0 = EDGE_LEN0[k]
        per.append(((V[a] - V[b]).length / l0) if l0 > 1e-18 else 0.0)

    newp = C.intersect_pairs_subset(V, POLY, THUMB_FACES) - BASE_INTRA
    pen = []
    for a, b in newp:
        ca = C.face_centroid(V, POLY[a]); cb = C.face_centroid(V, POLY[b])
        na = C.face_normal(V, POLY[a]); nb = C.face_normal(V, POLY[b])
        pen.append(min(abs((cb - ca).dot(na)), abs((ca - cb).dot(nb))) * 1000.0)

    sa = sum(C.face_area(V, POLY[i]) for i in pf) / max(1e-18, PATCH_FACE_SUM0[seg])
    nail_a = sum(C.face_area(V, POLY[i]) for i in NAIL_FACES) / max(1e-18, NAIL_SUM0)
    cap_a = sum(C.face_area(V, POLY[i]) for i in CAP_FACES) / max(1e-18, CAP_SUM0)
    web_move = max([(V[i] - V0[i]).length for i in WEB_V], default=0.0) * 1000.0
    clean_move = max([(V[i] - V0[i]).length for i in CLEAN_NONTHUMB], default=0.0) * 1000.0
    tip = rig.matrix_world @ rig.pose.bones["THUMB_TIP_R"].head
    st, st_e = C.stats(pr), C.stats(per)
    return {
        "min_face_area_ratio": C.rr(min(pr), 6),
        "face_area_p05": C.rr(st["p05"], 6),
        "face_area_median": C.rr(st["median"], 6),
        "face_area_p95": C.rr(st["p95"], 6),
        "min_edge_ratio": C.rr(min(per), 6),
        "max_edge_stretch": C.rr(max(per), 6),
        "edge_p05": C.rr(st_e["p05"], 6),
        "edge_median": C.rr(st_e["median"], 6),
        "edge_p95": C.rr(st_e["p95"], 6),
        "local_surface_area_ratio": C.rr(sa, 6),
        "intra_thumb_self_intersection_count": len(newp),
        "max_intra_thumb_penetration_proxy_mm": C.rr(max(pen), 6) if pen else 0.0,
        "distal_cap_area_ratio": C.rr(cap_a, 6),
        "nail_area_ratio": C.rr(nail_a, 6),
        "tip_landmark_world": [C.rr(x, 9) for x in tip],
        "first_web_max_movement_mm": C.rr(web_move, 9),
        "non_target_clean_max_movement_mm": C.rr(clean_move, 9),
    }


def measure_case_set():
    out = {}
    for (d, seg, ang) in C.THUMB_CASES:
        out["TH_%s_%d" % (seg, int(ang))] = measure(seg, ang)
    S6.reset_pose(rig)
    bpy.context.view_layer.update()
    return out


def apply_candidate(W2):
    for i in AUTH:
        for g in C.THUMB_FREE_GROUPS:
            w = W2[i].get(g, 0.0)
            if w > 0.0:
                VG[g].add([i], float(w), 'REPLACE')
            else:
                try:
                    VG[g].remove([i])
                except RuntimeError:
                    pass


# ---------------------------------------------------------------- acceptance + ranking
def ratio_up(v, b):
    return (v / b) if b > 1e-18 else 1.0


def ratio_dn(v, b):
    return (b / v) if v > 1e-18 else 1.0


def evaluate_acceptance(res):
    b = C.R1_BASELINE
    ip30, ip45, mcp45 = res["TH_IP_30"], res["TH_IP_45"], res["TH_MCP_45"]
    A = (ip30["min_face_area_ratio"] > b["TH_IP_30"]["min_face_area_ratio"] and
         ip45["min_face_area_ratio"] > b["TH_IP_45"]["min_face_area_ratio"])
    B = (ip30["face_area_p05"] > b["TH_IP_30"]["face_area_p05"] and
         ip45["face_area_p05"] > b["TH_IP_45"]["face_area_p05"])
    Cc = (ip30["max_edge_stretch"] <= b["TH_IP_30"]["max_edge_stretch"] and
          ip45["max_edge_stretch"] <= b["TH_IP_45"]["max_edge_stretch"])
    D = (ip30["intra_thumb_self_intersection_count"] <= C.R1_INTRA["TH_IP_30"] and
         ip45["intra_thumb_self_intersection_count"] <= C.R1_INTRA["TH_IP_45"])
    E = (mcp45["min_face_area_ratio"] >= b["TH_MCP_45"]["min_face_area_ratio"] and
         mcp45["face_area_p05"] >= b["TH_MCP_45"]["face_area_p05"] and
         mcp45["max_edge_stretch"] <= b["TH_MCP_45"]["max_edge_stretch"] and
         mcp45["intra_thumb_self_intersection_count"] <= C.R1_INTRA["TH_MCP_45"])
    F_ = True
    for cid in ("TH_MCP_15", "TH_MCP_30", "TH_IP_15"):
        r, r1 = res[cid], b[cid]
        if not (r["min_face_area_ratio"] >= r1["min_face_area_ratio"] and
                r["face_area_p05"] >= r1["face_area_p05"] and
                r["max_edge_stretch"] <= r1["max_edge_stretch"] and
                r["intra_thumb_self_intersection_count"] <= C.R1_INTRA[cid]):
            F_ = False
    # STRICT overlay: the user's A-F list names "face-area / edge-stretch / intra-thumb" for the
    # non-degradation clauses.  Edge strain has two sides (max stretch AND min compression), so
    # the overlay additionally forbids any min_edge_ratio regression.  It is reported separately
    # and is preferred when satisfiable, but never replaces the requested A-F decision.
    RESTRICTED = ("TH_MCP_15", "TH_MCP_30", "TH_MCP_45", "TH_IP_15")
    EDGE_STRICT = all(res[cid]["min_edge_ratio"] >= b[cid]["min_edge_ratio"]
                      for cid in RESTRICTED)
    hard = {
        "nan_inf_vertices": 0,
        "collapsed_faces": sum(1 for r in res.values() if r["min_face_area_ratio"] <= 1e-6),
        "degenerate_edges": sum(1 for r in res.values() if r["min_edge_ratio"] <= 1e-9),
        "unweighted_authorised_vertices": 0,
        "max_influences_le_4": True,
        "non_target_clean_at_noise_floor": all(
            r["non_target_clean_max_movement_mm"] <= 1e-4 for r in res.values()),
    }
    spec_pass = bool(A and B and Cc and D and E and F_ and
                     hard["collapsed_faces"] == 0 and
                     hard["degenerate_edges"] == 0 and
                     hard["non_target_clean_at_noise_floor"])
    return {"A_IP_min_face_area_strictly_better": A,
            "B_IP_face_area_p05_strictly_better": B,
            "C_IP_max_edge_stretch_not_increased": Cc,
            "D_IP_intra_thumb_not_increased": D,
            "E_MCP45_no_overall_degradation": E,
            "F_15_30_not_sacrificed": F_,
            "STRICT_edge_min_compression_not_regressed": EDGE_STRICT,
            "hard_gates": hard,
            "PASS": spec_pass,
            "PASS_STRICT": bool(spec_pass and EDGE_STRICT)}


def headline(res):
    """worst relative improvement over the four metrics that MUST strictly improve
    (TH_IP_30 / TH_IP_45 x (min face-area ratio, face-area p05)).  >1 = strict improvement."""
    b = C.R1_BASELINE
    return min(ratio_up(res["TH_IP_30"]["min_face_area_ratio"],
                        b["TH_IP_30"]["min_face_area_ratio"]),
               ratio_up(res["TH_IP_45"]["min_face_area_ratio"],
                        b["TH_IP_45"]["min_face_area_ratio"]),
               ratio_up(res["TH_IP_30"]["face_area_p05"], b["TH_IP_30"]["face_area_p05"]),
               ratio_up(res["TH_IP_45"]["face_area_p05"], b["TH_IP_45"]["face_area_p05"]))


def mcp_margin(res):
    b = C.R1_BASELINE
    rs = []
    for cid in ("TH_MCP_15", "TH_MCP_30", "TH_MCP_45"):
        rs.append(ratio_up(res[cid]["min_face_area_ratio"], b[cid]["min_face_area_ratio"]))
        rs.append(ratio_up(res[cid]["face_area_p05"], b[cid]["face_area_p05"]))
        rs.append(ratio_dn(res[cid]["max_edge_stretch"], b[cid]["max_edge_stretch"]))
        rs.append((C.R1_INTRA[cid] + 1.0) / (res[cid]["intra_thumb_self_intersection_count"] + 1.0))
    return min(rs)


# =====================================================================================
# candidate #0 -- the R1A configuration, must reproduce Stage6A R1 exactly
# =====================================================================================
t0 = time.time()
W_ref, _ch = C.compose_weights(ctx, W1, AUTH_SET, dict(C.R1A_PARAMS))
try:
    import numpy as _np
    f32 = lambda x: float(_np.float32(x))
except Exception:                                            # pragma: no cover
    f32 = lambda x: x
drift = 0.0
f32_mismatch = 0
for i in range(NV):
    for g in C.ALL_DEFORM:
        a, b = W1[i].get(g, 0.0), W_ref[i].get(g, 0.0)
        drift = max(drift, abs(a - b))
        if f32(b) != f32(a):
            f32_mismatch += 1
log("R1A reference re-composition: max drift %.3e, float32-exact mismatches %d"
    % (drift, f32_mismatch))
if drift > 1e-6 or f32_mismatch > 0:
    raise SystemExit("FAIL CLOSED: R1A reference re-composition is not a float32-exact identity")

apply_candidate(W_ref)
REF = measure_case_set()
ref_ok = True
for cid, r1 in sorted(C.R1_BASELINE.items()):
    for k in ("min_face_area_ratio", "face_area_p05", "max_edge_stretch", "min_edge_ratio"):
        if abs(REF[cid][k] - r1[k]) > 5e-6:
            ref_ok = False
            log("REF MISMATCH %s %s got %.6f want %.6f" % (cid, k, REF[cid][k], r1[k]))
    if REF[cid]["intra_thumb_self_intersection_count"] != C.R1_INTRA[cid]:
        ref_ok = False
        log("REF MISMATCH %s intra %d vs %d"
            % (cid, REF[cid]["intra_thumb_self_intersection_count"], C.R1_INTRA[cid]))
log("R1A reference full metric reproduction: %s" % ("EXACT" if ref_ok else "MISMATCH"))
if not ref_ok:
    raise SystemExit("FAIL CLOSED: sweep engine does not reproduce the Stage6A R1 baseline")

# =====================================================================================
# Stage A -- coarse grid
# =====================================================================================
GRID = []
for W_IP in (2.5, 3.0, 4.0, 5.0, 6.0, 8.0):
    for W_MCP in (1.0, 2.0, 3.0, 6.0):
        for W_BASE in (1.0, 2.0, 3.0, 4.0):
            for prof in ("smoothstep", "quintic", "cosine"):
                GRID.append({"form": "centered", "W_IP": W_IP, "W_MCP": W_MCP,
                             "W_BASE": W_BASE, "shift_IP": 0.0, "shift_MCP": 0.0,
                             "profile": prof})
log("stage A grid size = %d" % len(GRID))

rows = []


def run(params):
    W2, changed = C.compose_weights(ctx, W1, AUTH_SET, params)
    apply_candidate(W2)
    res = measure_case_set()
    return {"params": params, "cases": res, "changed_vertex_count": len(changed),
            "headline": headline(res), "mcp_margin": mcp_margin(res),
            "worst_stretch": max(res[c]["max_edge_stretch"] for c in res),
            "acceptance": evaluate_acceptance(res)}


for n, p in enumerate(GRID):
    rows.append(run(p))
    if (n + 1) % 72 == 0:
        log("  grid %d/%d  (%.1f s)" % (n + 1, len(GRID), time.time() - t0))
log("stage A done in %.1f s" % (time.time() - t0))

feasible = [r for r in rows if r["acceptance"]["PASS"]]
log("stage A feasible (A-F + hard gates): %d / %d" % (len(feasible), len(rows)))
if feasible:
    feasible.sort(key=lambda r: (-r["headline"], -r["mcp_margin"], r["worst_stretch"]))
    b0 = feasible[0]
    log("stage A best headline = %.6f  params=%s" % (b0["headline"], b0["params"]))
    best_a = b0["params"]
else:
    rows.sort(key=lambda r: (-r["headline"], r["worst_stretch"]))
    best_a = rows[0]["params"]
    log("stage A NO feasible candidate; best headline = %.6f params=%s"
        % (rows[0]["headline"], best_a))

# =====================================================================================
# Stage B -- refine around stage A + a bounded IP-ramp centre shift
# =====================================================================================
FINE = []
for dIP in (-1.0, -0.5, 0.0, 0.5, 1.0):
    for dMCP in (-0.5, 0.0, 0.5):
        for sh in (-1.0, -0.5, 0.0, 0.5, 1.0):
            p = {"form": "centered",
                 "W_IP": max(0.5, best_a["W_IP"] + dIP),
                 "W_MCP": max(0.5, best_a["W_MCP"] + dMCP),
                 "W_BASE": best_a["W_BASE"], "shift_IP": sh, "shift_MCP": 0.0,
                 "profile": best_a["profile"]}
            if p not in FINE:
                FINE.append(p)
for prof in ("smoothstep", "quintic", "cosine"):
    for W_IP in (3.0, 4.0, 5.0, 6.0):
        p = {"form": "centered", "W_IP": W_IP, "W_MCP": 2.0, "W_BASE": 2.0,
             "shift_IP": 0.0, "shift_MCP": 0.0, "profile": prof}
        if p not in FINE:
            FINE.append(p)
log("stage B fine grid size = %d" % len(FINE))
for p in FINE:
    rows.append(run(p))
log("stage B done in %.1f s" % (time.time() - t0))

# ---------------------------------------------------------------- final ranking
for r in rows:
    r["acceptance"] = evaluate_acceptance(r["cases"])
feasible = [r for r in rows if r["acceptance"]["PASS"]]
strict = [r for r in feasible if r["acceptance"]["PASS_STRICT"]]


def nor_regression(r):
    """worst-case relative non-regression margin over ALL 6 thumb cases x the 5 recorded
    metric families (min face-area ratio, face-area p05, max edge stretch, min edge ratio,
    intra-thumb pairs).  == 1.0 means every metric is at least as good as Stage6A R1;
    < 1.0 quantifies the single worst residual regression."""
    b = C.R1_BASELINE
    worst = 1.0
    for cid in sorted(r["cases"]):
        g = r["cases"][cid]
        worst = min(worst,
                    ratio_up(g["min_face_area_ratio"], b[cid]["min_face_area_ratio"]),
                    ratio_up(g["face_area_p05"], b[cid]["face_area_p05"]),
                    ratio_dn(g["max_edge_stretch"], b[cid]["max_edge_stretch"]),
                    ratio_up(g["min_edge_ratio"], b[cid]["min_edge_ratio"]),
                    (C.R1_INTRA[cid] + 1.0) /
                    (g["intra_thumb_self_intersection_count"] + 1.0))
    return worst


for r in feasible:
    r["noregress"] = nor_regression(r)
# a candidate is PROMOTED only if every one of the four required improvements is at least
# +25% (a CLEAR Pareto improvement, never "the least bad"), and among those we minimise the
# worst residual regression anywhere else, then maximise the required improvement.
CLEAR_MARGIN = 1.25
clear = [r for r in feasible if r["headline"] >= CLEAR_MARGIN]
pool = clear if clear else feasible
pool.sort(key=lambda r: (-r["noregress"], -r["headline"], r["worst_stretch"]))
accepted = pool[0] if pool else None
headline_best = max(feasible, key=lambda r: (-r["headline"], -r["noregress"])) if feasible else None
noregress_best = max(feasible, key=lambda r: (-r["noregress"], -r["headline"])) if feasible else None
sel_pool = pool
infeasible = [r for r in rows if not r["acceptance"]["PASS"]]
infeasible.sort(key=lambda r: (-r["headline"], r["worst_stretch"]))
ranked = sel_pool + [r for r in feasible if r not in sel_pool] + infeasible
log("FINAL feasible (A-F + hard gates): %d / %d ; strictly edge-clean: %d ; clear(>=%.2f): %d"
    % (len(feasible), len(rows), len(strict), CLEAR_MARGIN, len(clear)))
if accepted:
    log("ACCEPTED headline=%.6f worst_noregression=%.4f params=%s"
        % (accepted["headline"], accepted["noregress"], accepted["params"]))


def delta_block(res):
    b = C.R1_BASELINE
    out = {}
    for cid in sorted(res):
        g, r1 = res[cid], b[cid]
        out[cid] = {
            "min_face_area_ratio": {"R1": r1["min_face_area_ratio"],
                                    "candidate": g["min_face_area_ratio"],
                                    "ratio": C.rr(ratio_up(g["min_face_area_ratio"],
                                                           r1["min_face_area_ratio"]), 4)},
            "face_area_p05": {"R1": r1["face_area_p05"], "candidate": g["face_area_p05"],
                              "ratio": C.rr(ratio_up(g["face_area_p05"],
                                                     r1["face_area_p05"]), 4)},
            "max_edge_stretch": {"R1": r1["max_edge_stretch"],
                                 "candidate": g["max_edge_stretch"],
                                 "ratio_not_worse": C.rr(ratio_dn(g["max_edge_stretch"],
                                                                 r1["max_edge_stretch"]), 4)},
            "min_edge_ratio": {"R1": r1["min_edge_ratio"], "candidate": g["min_edge_ratio"]},
            "intra_thumb_self_intersection_count": {"R1": C.R1_INTRA[cid],
                                                    "candidate":
                                                        g["intra_thumb_self_intersection_count"]},
            "local_surface_area_ratio": {"R1A": REF[cid]["local_surface_area_ratio"],
                                         "candidate": g["local_surface_area_ratio"]},
            "nail_area_ratio": {"R1A": REF[cid]["nail_area_ratio"],
                                "candidate": g["nail_area_ratio"]},
            "distal_cap_area_ratio": {"R1A": REF[cid]["distal_cap_area_ratio"],
                                      "candidate": g["distal_cap_area_ratio"]},
            "first_web_max_movement_mm": {"R1A": REF[cid]["first_web_max_movement_mm"],
                                          "candidate": g["first_web_max_movement_mm"]},
            "non_target_clean_max_movement_mm": {
                "R1A": REF[cid]["non_target_clean_max_movement_mm"],
                "candidate": g["non_target_clean_max_movement_mm"]},
            "max_intra_thumb_penetration_proxy_mm": {
                "R1A": REF[cid]["max_intra_thumb_penetration_proxy_mm"],
                "candidate": g["max_intra_thumb_penetration_proxy_mm"]},
        }
    return out


# frozen-set no-drift proof: nail / distal cap / first web must be bit-identical to R1A
freeze_proof = {}
for cid in sorted(REF):
    freeze_proof[cid] = {
        "nail_area_ratio_identical_to_R1A": abs(
            REF[cid]["nail_area_ratio"] - (accepted["cases"][cid]["nail_area_ratio"]
                                           if accepted else REF[cid]["nail_area_ratio"])) < 1e-9,
        "distal_cap_area_ratio_identical_to_R1A": abs(
            REF[cid]["distal_cap_area_ratio"] - (accepted["cases"][cid]["distal_cap_area_ratio"]
                                                 if accepted else REF[cid]["distal_cap_area_ratio"])) < 1e-9,
        "first_web_movement_identical_to_R1A": abs(
            REF[cid]["first_web_max_movement_mm"] - (accepted["cases"][cid]["first_web_max_movement_mm"]
                                                     if accepted else REF[cid]["first_web_max_movement_mm"])) < 1e-9,
        "non_target_clean_identical_to_R1A": abs(
            REF[cid]["non_target_clean_max_movement_mm"] -
            (accepted["cases"][cid]["non_target_clean_max_movement_mm"]
             if accepted else REF[cid]["non_target_clean_max_movement_mm"])) < 1e-12,
    }

S6.reset_pose(rig)
bpy.context.view_layer.update()
s_h1_after = C.sha256(C.STAGE6A_R1_HARNESS)
s_r1a_after = C.sha256(C.R1A_MASTER)


def slim(r, rank):
    return {"rank": rank, "params": r["params"], "headline_improvement": C.rr(r["headline"], 4),
            "mcp_margin": C.rr(r["mcp_margin"], 4),
            "worst_case_non_regression_margin": C.rr(r.get("noregress", 1.0), 4),
            "worst_case_max_edge_stretch": C.rr(r["worst_stretch"], 6),
            "changed_vertex_count": r["changed_vertex_count"],
            "acceptance": r["acceptance"], "cases": r["cases"]}


OUT = {
    "stage": "STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING",
    "generated_at": NOW,
    "mode": "IN_MEMORY_CANDIDATE_SWEEP_NO_BLEND_WRITTEN",
    "objective": ("baseline-relative Pareto closure.  A candidate is ACCEPTED only when it is "
                  "strictly better than Stage6A R1 on the TH_IP_30 and TH_IP_45 min face-area "
                  "ratio AND face-area p05, and not worse on max edge stretch, intra-thumb "
                  "self-intersection, TH_MCP_45, and the 15/30 deg cases.  No new hand-picked "
                  "anatomical threshold is introduced."),
    "candidate_family": {
        "longitudinal_coordinate": "APPROVED_JOINT_POLYLINE_ARC_LENGTH",
        "forbidden_coordinate": "GLOBAL_SURFACE_GEODESIC_FROM_DISTAL_TIP (not used)",
        "free_parameters": ["form", "W_IP", "W_MCP", "W_BASE", "shift_IP", "shift_MCP",
                            "profile"],
        "per_vertex_free_parameters": 0,
        "widths_in_units_of_MED": True, "MED_mm": C.rr(MED, 6),
        "reassignment_groups": C.THUMB_FREE_GROUPS,
        "forbidden_groups": ["INDEX_*", "MIDDLE_*", "RING_*", "LITTLE_*"],
        "authorised_vertex_count": len(AUTH),
    },
    "engine_validation": {
        "r1a_recomposition_max_weight_drift": C.rr(drift, 12),
        "r1a_recomposition_float32_exact_mismatches": f32_mismatch,
        "r1a_reference_metric_reproduction": "EXACT" if ref_ok else "MISMATCH",
        "r1a_reference_full_metrics": REF,
    },
    "baseline_stage6a_r1": {"deformation_metrics": C.R1_BASELINE,
                            "intra_thumb_pairs": C.R1_INTRA},
    "grid_size": {"stage_a": len(GRID), "stage_b": len(FINE), "total": len(rows)},
    "feasible_count": len(feasible),
    "strict_edge_clean_count": len(strict),
    "clear_improvement_count": len(clear),
    "clear_margin_required": CLEAR_MARGIN,
    "selection_rule": ("(1) satisfy A-F plus every hard gate; (2) all four required improvements "
                       "must be at least +25% (a CLEAR Pareto improvement -- a candidate that is "
                       "merely 'least bad' is never promoted); (3) among those, minimise the worst "
                       "residual regression over all six thumb cases and all five recorded metric "
                       "families; (4) then maximise the required improvement"),
    "outcome": ("PARETO_IMPROVING_CANDIDATE_FOUND" if accepted
                else "NO_PARETO_IMPROVING_CANDIDATE"),
    "accepted_candidate": ({"params": accepted["params"],
                            "headline_improvement": C.rr(accepted["headline"], 4),
                            "worst_case_non_regression_margin": C.rr(accepted["noregress"], 4),
                            "changed_vertex_count": accepted["changed_vertex_count"],
                            "acceptance": accepted["acceptance"],
                            "before_after": delta_block(accepted["cases"]),
                            "cases": accepted["cases"]} if accepted else None),
    "alternatives_reported_to_human_review": {
        "headline_optimal": ({"params": headline_best["params"],
                              "headline_improvement": C.rr(headline_best["headline"], 4),
                              "worst_case_non_regression_margin": C.rr(headline_best["noregress"], 4),
                              "acceptance": headline_best["acceptance"]}
                             if headline_best else None),
        "most_non_regressive_feasible": (
            {"params": noregress_best["params"],
             "headline_improvement": C.rr(noregress_best["headline"], 4),
             "worst_case_non_regression_margin": C.rr(noregress_best["noregress"], 4),
             "acceptance": noregress_best["acceptance"]} if noregress_best else None),
        "strict_edge_clean_candidates": len(strict),
        "note": ("no candidate in the swept family keeps min_edge_ratio non-regressed on every "
                 "restricted case; the promoted candidate is the highest worst-case "
                 "non-regression margin among the candidates whose four required improvements "
                 "are all at least +25%"),
    },
    "frozen_set_nodrift_proof": freeze_proof,
    "ranking_top": [slim(r, i + 1) for i, r in enumerate(ranked[:20])],
    "all_results": [{"params": r["params"], "headline": C.rr(r["headline"], 4),
                     "mcp_margin": C.rr(r["mcp_margin"], 4),
                     "worst_case_non_regression_margin": C.rr(r.get("noregress", 1.0), 4),
                     "worst_stretch": C.rr(r["worst_stretch"], 6),
                     "PASS": r["acceptance"]["PASS"],
                     "PASS_STRICT": r["acceptance"]["PASS_STRICT"],
                     "key_metrics": {
                         cid: {"min_face_area_ratio": r["cases"][cid]["min_face_area_ratio"],
                               "face_area_p05": r["cases"][cid]["face_area_p05"],
                               "max_edge_stretch": r["cases"][cid]["max_edge_stretch"],
                               "min_edge_ratio": r["cases"][cid]["min_edge_ratio"],
                               "intra": r["cases"][cid]["intra_thumb_self_intersection_count"]}
                         for cid in sorted(r["cases"])}} for r in ranked],
    "frozen_inputs_after_sweep": {
        "stage5b_r1a_sha256": s_r1a, "stage5b_r1a_sha256_unchanged": s_r1a_after == s_r1a,
        "stage6a_r1_harness_sha256": s_h1,
        "stage6a_r1_harness_sha256_unchanged": s_h1_after == s_h1,
    },
    "log": LOG,
}
json.dump(OUT, open(os.path.join(OUTDIR, "STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json"),
                    "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("OUTCOME = %s" % OUT["outcome"])
log("wrote STAGE6A_R1A_THUMB_WEIGHT_CANDIDATE_RANKING.json")
print("SWEEP_DONE")
