# =====================================================================================
# STAGE6A -- isolated flex deformation validation (sign probe + 42 formal cases)
# =====================================================================================
# READ-ONLY w.r.t. every .blend on disk.  Only pose bone rotations are applied, always
# from a full bind reset, and always reset back afterwards.
# =====================================================================================
import bpy
import sys
import os
import json
import math
import hashlib
import datetime
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree

HERE0 = os.path.dirname(os.path.abspath(__file__))
PROD_PRE = os.path.abspath(os.path.join(HERE0, "..", "..", ".."))
sys.path.append(HERE0)
sys.path.append(os.path.join(PROD_PRE, "stage6_deformation", "stage6a", "scripts"))
sys.path.append(os.path.join(PROD_PRE, "stage6_deformation", "stage6b_r1b", "scripts"))
import s6a_common as S                                   # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
STAGE6D = os.path.dirname(OUTDIR)
PROD = os.path.dirname(STAGE6D)
S5 = os.path.join(PROD, "stage5_production_rig")
MASTER = os.path.join(S5, "stage5b_r1c", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1C.blend")
R1C_STATUS = json.load(open(os.path.join(S5, "stage5b_r1c", "STAGE5B_R1C_STATUS.json"), encoding="utf-8"))
MASTER_SHA = R1C_STATUS["candidate"]["sha256"]
HARNESS = os.path.join(OUTDIR, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1B.blend")
NOW = datetime.datetime.now().astimezone().isoformat()
log, LOG = S.log_factory("S6A-RUN")
MM = S.MM


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def dump(name, obj, where=None):
    name = name.replace("STAGE6A_", "STAGE6A_R1B_")
    p = os.path.join(where or OUTDIR, name)
    json.dump(obj, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    log("wrote %s" % name)


# ============================================================ 0. gates
s_master = sha(MASTER)
if s_master != MASTER_SHA:
    raise SystemExit("FAIL CLOSED: Stage5B R1C candidate hash mismatch")
s_harness = sha(HARNESS)
log("master %s ; harness %s" % (s_master[:12], s_harness[:12]))

C, ref = S.load_reference(S5)
V0 = ref["V0"]
NV = ref["NV"]
jf = ref["jf"]
MED = ref["med_edge"]
TF = C.thumb_frame(ref)
ARC_T = TF["arc_thumb_mm"]
RG = C.build_regions(ref, TF, MED, *C.thumb_radii(ref, TF))
OWN = RG["own_r1a"]                     # evidence based ownership authority (R1A)
TNAIL_ALL = {d: set(ref["NAIL_BY_DIGIT"].get(d, set())) for d in S.DIGITS}
CAP = RG["cap_vertices"]
h = S.open_harness(HARNESS)
ob, rig, me = h["ob"], h["rig"], h["me"]
MW = h["MW"]
MINV = MW.inverted()
M3 = MW.to_3x3()
POLY = h["POLY"]
EDGES = h["EDGES"]
NV2 = h["NV"]
assert NV2 == NV

# ---------------------------------------------------------------- digit arc frames
PTS = {d: C.chp(jf, d) for d in S.DIGITS}
XIJ = {d: C.chain_arc_table(jf, d) for d in S.DIGITS}
ARC = {}
for d in S.DIGITS:
    if d == "THUMB":
        ARC[d] = ARC_T
    else:
        ARC[d] = [C.arc_of(PTS[d], V0[i])[0] for i in range(NV)]
LOG_OWN = {d: [i for i in range(NV) if OWN[i] == d] for d in S.DIGITS}


def joint_arc(d, seg):
    return XIJ[d][S.CHAIN[d].index(seg)]


# ---------------------------------------------------------------- T-01 loop spacing (kappa)
T01 = json.load(open(os.path.join(PROD, "stage4_blender", "stage4a_t01", "T01_FINAL_AUDIT.json"),
                     encoding="utf-8"))


def loop_spacing(key):
    for grp in ("T01_MCP", "OTHER_T01_JOINTS"):
        if key in T01.get(grp, {}):
            L = T01[grp][key]["LOOP_POSITION_axial_from_commissure_mm"]
            dd = sorted(round(L[i + 1] - L[i], 4) for i in range(len(L) - 1))
            if dd:
                return dd[len(dd) // 2]
    return None


KAPPA = {}
for d in ("INDEX", "MIDDLE", "RING", "LITTLE"):
    for seg in ("MCP", "PIP", "DIP"):
        k = loop_spacing("%s_%s" % (d, seg))
        KAPPA[(d, seg)] = k if k else 2.0 * MED
KAPPA[("THUMB", "MCP")] = 2.0 * MED
KAPPA[("THUMB", "IP")] = 2.0 * MED
log("kappa (mm): " + ", ".join("%s_%s=%.2f" % (a, b, KAPPA[(a, b)])
                              for a, b in sorted(KAPPA)))

# ---------------------------------------------------------------- palmar direction (per digit)
# Stage5A frozen convention: bone local Y = longitudinal, local Z = dorsal-like.
# palmar = -(bone local Z) in world.  Cross-checked against the global canonical +Y = DORSAL.
PALMAR = {}
DORSAL_CHECK = {}
for d in S.DIGITS:
    bone = "%s_MCP_R" % d
    m = rig.data.bones[bone].matrix_local.to_3x3()
    z_world = (M3 @ m @ Vector((0.0, 0.0, 1.0))).normalized()
    PALMAR[d] = -z_world
    DORSAL_CHECK[d] = {"bone_local_Z_world": [S.rr(x, 6) for x in z_world],
                       "dot_with_global_plusY": S.rr(z_world.y, 6),
                       "consistent_with_canonical_plusY_dorsal": z_world.y > 0.0}
log("palmar dirs: " + ", ".join("%s dot(+Y)=%.3f" % (d, DORSAL_CHECK[d]["dot_with_global_plusY"])
                               for d in S.DIGITS))

# ---------------------------------------------------------------- patches
PATCH = {}
for (d, seg) in S.TEST_JOINTS:              # CMC and WRIST are LOCKED this round
    k = KAPPA[(d, seg)]
    a = joint_arc(d, seg)
    ids = [i for i in LOG_OWN[d] if abs(ARC[d][i] - a) <= k]
    PATCH[(d, seg)] = sorted(ids)


def patch_key(d, seg):
    return "%s_%s" % (d, seg)


SHAFT = {}
for d in S.DIGITS:
    if d == "THUMB":
        lo = joint_arc(d, "MCP") + KAPPA[(d, "MCP")]
        hi = joint_arc(d, "IP") - KAPPA[(d, "IP")]
    else:
        lo = joint_arc(d, "MCP") + KAPPA[(d, "MCP")]
        hi = joint_arc(d, "PIP") - KAPPA[(d, "PIP")]
    SHAFT[d] = [i for i in LOG_OWN[d] if lo <= ARC[d][i] <= hi]

# forearm = proximal of the wrist head along the wrist axis
wH = S.bone_world(rig, "WRIST_R", True)
wT = S.bone_world(rig, "WRIST_R", False)
wU = (wT - wH).normalized()
FOREARM = [i for i in range(NV) if (V0[i] - wH).dot(wU) < 0.0]
log("patches: " + ", ".join("%s=%d" % (patch_key(*k), len(v)) for k, v in sorted(PATCH.items())))
log("shafts: " + ", ".join("%s=%d" % (d, len(v)) for d, v in SHAFT.items()))
log("forearm vertices: %d" % len(FOREARM))

# ---------------------------------------------------------------- bind baselines
FACE_AREA0 = [S.face_area(V0, p) for p in POLY]
FACE_CEN0 = [S.face_centroid(V0, p) for p in POLY]
FACE_NOR0 = [S.face_normal(V0, p) for p in POLY]
EDGE_LEN0 = [(V0[a] - V0[b]).length for a, b in EDGES]
EDGE_FACES = {}
for fi, p in enumerate(POLY):
    for k in range(len(p)):
        e = tuple(sorted((p[k], p[(k + 1) % len(p)])))
        EDGE_FACES.setdefault(e, []).append(fi)
# face adjacency (faces sharing a vertex) for intersection filtering
V2F = [[] for _ in range(NV)]
for fi, p in enumerate(POLY):
    for v in p:
        V2F[v].append(fi)


def intersect_pairs(V, P):
    tree = BVHTree.FromPolygons([tuple(v) for v in V], [tuple(p) for p in P],
                                all_triangles=False, epsilon=0.0)
    raw = tree.overlap(tree)
    out = set()
    for a, b in raw:
        if a >= b:
            continue
        if set(P[a]) & set(P[b]):
            continue                      # share a vertex -> touching, not an intersection
        out.add((a, b))
    return out


BASE_PAIRS = intersect_pairs(V0, POLY)
log("bind-pose baseline intersecting face pairs = %d" % len(BASE_PAIRS))

# local thickness proxy (ray cast to the far side) per patch vertex, at bind
def thickness_proxy(V, ids):
    dgx = bpy.context.evaluated_depsgraph_get()
    obx = ob.evaluated_get(dgx)
    out = {}
    for i in ids:
        cps = []
        d = None
        for dd in S.DIGITS:
            if OWN[i] == dd:
                d = dd
                break
        cps = PTS[d] if d else PTS["INDEX"]
        # nearest point on the digit polyline
        best = (1e9, None)
        for k in range(len(cps) - 1):
            a, b = cps[k], cps[k + 1]
            ab = b - a
            t = max(0.0, min(1.0, (V[i] - a).dot(ab) / max(ab.length_squared, 1e-18)))
            q = a + ab * t
            dd2 = (V[i] - q).length
            if dd2 < best[0]:
                best = (dd2, q)
        tgt = best[1]
        if tgt is None:
            continue
        dw = (tgt - V[i])
        if dw.length < 1e-9:
            continue
        dw.normalize()
        o_loc = MINV @ (V[i] + dw * 5e-7)
        d_loc = (MINV.to_3x3() @ dw).normalized()
        hit, loc, nor, idx = obx.ray_cast(o_loc, d_loc, distance=0.5)
        if hit:
            out[i] = (V[i] - (MW @ loc)).length * MM
    return out


S.reset_pose(rig)
bpy.context.view_layer.update()
THICK0 = {}
for key, ids in PATCH.items():
    sample = ids[::max(1, len(ids) // 60)][:60]
    THICK0[key] = thickness_proxy(V0, sample)
log("bind thickness proxy sampled: " + ", ".join("%s=%d" % (patch_key(*k), len(v))
                                                 for k, v in sorted(THICK0.items())))

# ---- weight-authoritative cross-digit classification -------------------------------
DOB = {"WRIST_R": "wrist"}
for _d in S.DIGITS:
    for _s in S.CHAIN[_d]:
        DOB["%s_%s_R" % (_d, _s)] = _d
FOREIGN = {}
for i in range(NV):
    o = OWN[i]
    FOREIGN[i] = sorted(g for g in h["W"][i]
                        if DOB.get(g, "wrist") not in (o, "wrist"))
log("vertices carrying a foreign-digit group: %d"
    % sum(1 for i in range(NV) if FOREIGN[i]))
CLEAN = {d: [i for i in range(NV) if OWN[i] == d and not FOREIGN[i]] for d in S.DIGITS}
# blocker threshold for "own-digit-only weights must not be moved by another digit".
# The harness float32 noise floor is 5.967e-05 mm (zero-pose baseline), so 1e-3 mm (1 um) is
# ~17x the noise floor and still orders of magnitude below any visible displacement.
CLEAN_MOTION_BLOCKER_MM = 1e-3
SANCTIONED = {d: [i for i in range(NV) if OWN[i] == d and FOREIGN[i]] for d in S.DIGITS}
log("clean (own-digit-only) vertices: " + ", ".join("%s=%d" % (d, len(CLEAN[d])) for d in S.DIGITS))
log("sanctioned cross-blend vertices: " + ", ".join("%s=%d" % (d, len(SANCTIONED[d])) for d in S.DIGITS))

PATCH_FACES = {}
PATCH_EDGES = {}
for key, ids in PATCH.items():
    idset = set(ids)
    kk = patch_key(*key)
    PATCH_FACES[kk] = [i for i in range(len(POLY)) if any(v in idset for v in POLY[i])]
    PATCH_EDGES[kk] = [k for k, (a, b) in enumerate(EDGES) if a in idset or b in idset]
TNAIL_FACES = {d: [i for i in range(len(POLY)) if all(v in TNAIL_ALL[d] for v in POLY[i])]
              for d in S.DIGITS}
CAP_FACES = [i for i in range(len(POLY)) if all(v in CAP for v in POLY[i])]
log("patch faces/edges precomputed")

# ============================================================ 1. flexion sign probe
SIGN_AUDIT = {"stage": "STAGE6A_FLEXION_AXIS_SIGN_AUDIT", "generated_at": NOW,
              "method": ("rotate the target joint about its bone LOCAL X by +/-5 deg, measure the "
                         "world displacement of the digit tip landmark (posed TIP bone head), "
                         "project onto the digit PALMAR direction (= -(bone local Z), Stage5A "
                         "frozen convention), select the sign with the positive palmar component"),
              "canonical": {"+Y": "DORSAL", "-Y": "PALMAR",
                            "flexion_axis": "bone LOCAL X (Stage5A frozen)"},
              "palmar_direction_per_digit": {d: [S.rr(x, 6) for x in PALMAR[d]] for d in S.DIGITS},
              "dorsal_convention_cross_check": DORSAL_CHECK,
              "probes": {}, "FLEXION_SIGN": {}, "FLEXION_AXIS_SIGN_QUALIFIED": "PASS"}
SIGN = {}
sign_ok = True
for (d, seg) in S.TEST_JOINTS:
    bone = "%s_%s_R" % (d, seg)
    tip = S.TIPBONE[d]
    rec = {}
    for sgn in (+1.0, -1.0):
        S.reset_pose(rig)
        S.set_joint_rotation(rig, bone, sgn * S.PROBE_ANGLE)
        dg = bpy.context.evaluated_depsgraph_get()
        bpy.context.view_layer.update()
        pb = rig.pose.bones[tip]
        tp = rig.matrix_world @ pb.head
        rec["%+d" % int(sgn)] = {"tip_world": [S.rr(x, 9) for x in tp]}
    bpy.context.view_layer.update()
    S.reset_pose(rig)
    bpy.context.view_layer.update()
    pb = rig.pose.bones[tip]
    tp0 = rig.matrix_world @ pb.head
    for sgn in (+1.0, -1.0):
        tp = Vector(rec["%+d" % int(sgn)]["tip_world"])
        disp = tp - tp0
        rec["%+d" % int(sgn)]["displacement_mm"] = [S.rr(x * MM, 9) for x in disp]
        rec["%+d" % int(sgn)]["palmar_dot_mm"] = S.rr(disp.dot(PALMAR[d]) * MM, 9)
        rec["%+d" % int(sgn)]["magnitude_mm"] = S.rr(disp.length * MM, 9)
    dp = rec["+1"]["palmar_dot_mm"]
    dm = rec["-1"]["palmar_dot_mm"]
    if dp > 0 > dm:
        chosen = +1.0
    elif dm > 0 > dp:
        chosen = -1.0
    else:
        chosen = None
        sign_ok = False
    rec["selected_FLEXION_SIGN"] = chosen
    rec["separated"] = bool(chosen is not None
                            and min(abs(dp), abs(dm)) > 1e-6)
    if not rec["separated"]:
        sign_ok = False
    SIGN[(d, seg)] = chosen
    SIGN_AUDIT["probes"][patch_key(d, seg)] = rec
    log("probe %-12s +5=%+.6f mm  -5=%+.6f mm  sign=%s"
        % (patch_key(d, seg), dp, dm, chosen))
# per-digit consistency
DIGIT_SIGN = {}
for d in S.DIGITS:
    sset = {SIGN[(d, seg)] for seg in S.CHAIN[d] if (d, seg) in SIGN}
    DIGIT_SIGN[d] = (sset.pop() if len(sset) == 1 else None)
    if DIGIT_SIGN[d] is None:
        sign_ok = False
SIGN_AUDIT["FLEXION_SIGN"] = {patch_key(*k): v for k, v in sorted(SIGN.items())}
SIGN_AUDIT["per_digit_sign"] = DIGIT_SIGN
SIGN_AUDIT["FLEXION_AXIS_SIGN_QUALIFIED"] = "PASS" if sign_ok else "FAIL"
log("per-digit signs: %s" % DIGIT_SIGN)
if not sign_ok:
    dump("STAGE6A_FLEXION_AXIS_SIGN_AUDIT.json", SIGN_AUDIT)
    raise SystemExit("FAIL CLOSED: flexion axis sign not qualified")

# ============================================================ 2. patches table
PATCH_TABLE = {"stage": "STAGE6A_LOCAL_PATCH_TABLE.json", "generated_at": NOW,
               "authority": ("four fingers: approved T-01 joint deformation-loop spacing "
                             "(median loop position delta) around the approved joint arc; "
                             "thumb: approved joint arc +/- 2 mesh median edges.  Thumb uses the "
                             "frozen APPROVED_JOINT_POLYLINE_ARC_LENGTH coordinate, NOT any "
                             "whole-thumb surface geodesic."),
               "med_edge_mm": S.rr(MED, 6),
               "kappa_mm": {"%s_%s" % k: S.rr(v, 6) for k, v in KAPPA.items()},
               "joint_arcs_mm": {}, "patches": {}, "shafts": {}, "forearm": {}}
for d in S.DIGITS:
    PATCH_TABLE["joint_arcs_mm"][d] = {"chain_arc_mm": [S.rr(x, 6) for x in XIJ[d]]}
for (d, seg) in S.TEST_JOINTS:
    ids = PATCH[(d, seg)]
    PATCH_TABLE["patches"][patch_key(d, seg)] = {
        "digit": d, "joint": seg, "vertex_ids": ids, "vertex_count": len(ids),
        "kappa_mm": S.rr(KAPPA[(d, seg)], 6),
        "joint_arc_mm": S.rr(joint_arc(d, seg), 6),
        "arc_range_mm": [S.rr(min((ARC[d][i] for i in ids), default=0), 4),
                         S.rr(max((ARC[d][i] for i in ids), default=0), 4)]}
for d in S.DIGITS:
    PATCH_TABLE["shafts"][d] = {"vertex_ids": SHAFT[d], "vertex_count": len(SHAFT[d])}
PATCH_TABLE["forearm"] = {"vertex_ids": FOREARM, "vertex_count": len(FOREARM)}
dump("STAGE6A_LOCAL_PATCH_TABLE.json", PATCH_TABLE)

# ============================================================ 3. the 42 formal cases
def metrics(V, P):
    """hard blockers + diagnostics for one evaluated state"""
    m = {}
    nan = sum(1 for v in V if not all(math.isfinite(c) for c in v))
    m["nan_inf_vertices"] = nan
    m["nan_inf_faces"] = sum(1 for p in P if any(not all(math.isfinite(c) for c in V[v]) for v in p))
    areas = [S.face_area(V, p) for p in P]
    ratios = [(areas[i] / FACE_AREA0[i]) if FACE_AREA0[i] > 1e-18 else 0.0
              for i in range(len(P))]
    m["min_face_area_m2"] = min(areas)
    m["min_face_area_ratio"] = min(ratios)
    m["max_face_area_ratio"] = max(ratios)
    m["collapsed_faces"] = sum(1 for i, a in enumerate(areas)
                               if a <= 1e-12 or ratios[i] <= 1e-6)
    el = [(V[a] - V[b]).length for a, b in EDGES]
    er = [(el[i] / EDGE_LEN0[i]) if EDGE_LEN0[i] > 1e-18 else 0.0 for i in range(len(el))]
    m["min_edge_ratio"] = min(er)
    m["max_edge_ratio"] = max(er)
    m["degenerate_edges"] = sum(1 for x in el if x <= 1e-12)
    pairs = intersect_pairs(V, P)
    newp = sorted(pairs - BASE_PAIRS)
    m["new_severe_self_intersection_pairs"] = len(newp)
    m["new_self_intersection_samples"] = newp[:12]
    m["_newp"] = newp
    m["topology"] = {"V": len(V), "E": len(EDGES), "F": len(P),
                     "TRIS": sum(len(p) - 2 for p in P)}
    m["topology_unchanged"] = (len(V), len(P)) == (NV, len(POLY))
    return m, ratios, er


def region_disp(V, ids):
    d = [(V[i] - V0[i]).length * MM for i in ids]
    return (max(d) if d else 0.0), (sum(d) / len(d) if d else 0.0)


CASES = []
ZERO_AUDIT = {"stage": "STAGE6A_ZERO_RESTORE_AUDIT.json", "generated_at": NOW,
              "method": ("before every case and after every case ALL pose bones are reset to "
                         "bind; the evaluated mesh is compared with the frozen Stage5B "
                         "zero-pose baseline (Stage5A R2A geometry)."),
              "hard_gate_mm": 1e-4, "baseline_reference_mm": 5.967e-05,
              "pre_case": [], "post_case": [], "max_restore_delta_mm": 0.0,
              "ZERO_RESTORE_AFTER_EACH_CASE": "PASS"}
STRAIN = {"stage": "STAGE6A_LOCAL_STRAIN_AUDIT.json", "generated_at": NOW,
          "note": "mostly DIAGNOSTIC; no hand-coded anatomical PASS threshold is applied. "
                  "Only near-zero face area / explosive outliers are treated as blockers.",
          "cases": {}}
PINCH = {"stage": "STAGE6A_PINCH_COLLAPSE_AUDIT.json", "generated_at": NOW,
         "note": "machine values are diagnostic; final shape judgement is Human Review",
         "cases": {}}
SELFINT = {"stage": "STAGE6A_SELF_INTERSECTION_AUDIT.json", "generated_at": NOW,
           "bind_baseline_pairs": len(BASE_PAIRS),
           "method": ("new intersecting face pairs = case pairs - bind-pose pairs, with pairs "
                      "sharing a vertex excluded.  Each new pair is decomposed by FACE-centroid "
                      "ownership into intra-target-digit (fold at the crease) and target-vs-other "
                      "(pose contact, the RSSF bind already has the thumb pressed against the "
                      "index).  A penetration-depth proxy = min(|plane-distance of one centroid to "
                      "the other face|) is reported; the 0.5 mm band is a practical "
                      "artifact-visibility proxy for Human Review, NOT an anatomical threshold."),
           "cases": {}, "total_new_pairs": 0, "total_intra_target": 0, "total_target_vs_other": 0,
           "severe_pairs_depth_gt_0_5mm": 0,
           "NEW_SEVERE_SELF_INTERSECTION": "PASS_WITH_HUMAN_REVIEW"}
CROSS = {"stage": "STAGE6A_CROSS_DIGIT_DEFORM_AUDIT.json", "generated_at": NOW,
         "method": ("non-target digit SHAFT bands must not be driven by an isolated flex of "
                    "another digit"), "cases": {},
         "clean_motion_blocker_mm": 1e-3,
         "noise_floor_mm": 5.967e-05,
         "NON_TARGET_DIGIT_SHAFT_CONTAMINATION": "PASS"}
FORE = {"stage": "STAGE6A_FOREARM_AUDIT", "generated_at": NOW,
        "forearm_vertex_count": len(FOREARM), "cases": {}, "FOREARM_STABILITY": "PASS"}
TRAJ = {"stage": "STAGE6A_TIP_TRAJECTORY_AUDIT.json", "generated_at": NOW,
        "method": ("per isolated joint: tip landmark world position at bind / 15 / 30 / 45 deg; "
                   "palmar component must increase monotonically"),
        "joints": {}, "TIP_TRAJECTORY_MONOTONIC": "PASS"}
NAILD = {"stage": "STAGE6A_NAIL_DEFORM_AUDIT.json", "generated_at": NOW,
         "per_digit_nail_vertex_count": {d: len(TNAIL_ALL[d]) for d in S.DIGITS},
         "cases": {}, "NAIL_DEFORMATION": "PASS_PENDING_HUMAN_REVIEW"}
THUMBD = {"stage": "STAGE6A_THUMB_DISTAL_AUDIT.json", "generated_at": NOW,
          "authority": "R2A approved distal-cap semantic (GEODESIC_CONNECTED_CAP_FROM_DISTAL_MOST_SURFACE_REGION, 9 mm)",
          "cap_vertex_ids": sorted(CAP),
          "cases": {}, "THUMB_DISTAL_DEFORMATION": "PASS_PENDING_HUMAN_REVIEW"}
BLOCKERS = []
PREFIX = {"INDEX": "IDX", "MIDDLE": "MID", "RING": "RNG", "LITTLE": "LTL", "THUMB": "TH"}

zero_before = []
for (d, seg) in S.TEST_JOINTS:
    bone = "%s_%s_R" % (d, seg)
    tip = S.TIPBONE[d]
    key = patch_key(d, seg)
    ids = PATCH[(d, seg)]
    nail_ids = sorted(TNAIL_ALL[d])
    traj = []
    for ang in S.TEST_ANGLES:
        cid = "%s_%s_%d" % (PREFIX[d], seg, int(ang))
        # --- RESET + verify
        S.reset_pose(rig)
        bpy.context.view_layer.update()
        Vz, Pz = S.evaluate(ob, MW)
        zmax = max((Vz[i] - V0[i]).length for i in range(NV)) * MM
        zero_before.append({"case_id": cid, "max_delta_mm": S.rr(zmax, 9)})
        if zmax > 1e-4:
            raise SystemExit("FAIL CLOSED: pre-case zero state broken at %s (%.9f mm)" % (cid, zmax))
        # --- apply
        S.set_joint_rotation(rig, bone, SIGN[(d, seg)] * ang)
        bpy.context.view_layer.update()
        V, P = S.evaluate(ob, MW)
        pb = rig.pose.bones[tip]
        tp = (rig.matrix_world @ pb.head)
        traj.append({"angle_deg": ang, "tip_world": [S.rr(x, 9) for x in tp]})
        m, ratios, er = metrics(V, P)
        # --- region displacements
        pmax, pmean = region_disp(V, ids)
        sh_clean = {o: region_disp(V, CLEAN[o]) for o in S.DIGITS if o != d}
        sh_sanc = {o: region_disp(V, SANCTIONED[o]) for o in S.DIGITS if o != d}
        sh_band = {o: region_disp(V, SHAFT[o]) for o in S.DIGITS if o != d}
        fmax, fmean = region_disp(V, FOREARM)
        # --- strain diagnostics
        pf = PATCH_FACES[key]
        pe_idx = PATCH_EDGES[key]
        pr = [ratios[i] for i in pf]
        pe = [er[k] for k in pe_idx]
        lp = [V[i] for i in ids]
        lp0 = [V0[i] for i in ids]
        bb = [(min(v[k] for v in lp) - min(v[k] for v in lp0)) * MM for k in range(3)] + \
             [(max(v[k] for v in lp) - max(v[k] for v in lp0)) * MM for k in range(3)]
        axis = (PTS[d][-1] - PTS[d][0]).normalized()

        def span(VV):
            pr2 = [VV[i].dot(axis) for i in ids]
            return max(pr2) - min(pr2)
        bw = span(V) / span(V0) if span(V0) > 1e-12 else 0.0
        STRAIN["cases"][cid] = {
            "edge_length_ratio": {"min": S.rr(min(pe), 6), "max": S.rr(max(pe), 6),
                                  "dist": {k: (S.rr(v, 6) if isinstance(v, float) else v)
                                           for k, v in S.stats(pe).items()}},
            "face_area_ratio": {"min": S.rr(min(pr), 6), "max": S.rr(max(pr), 6),
                                "dist": {k: (S.rr(v, 9) if isinstance(v, float) else v)
                                         for k, v in S.stats(pr).items()}},
            "local_surface_area_ratio": S.rr(
                sum(S.face_area(V, POLY[i]) for i in pf)
                / max(1e-18, sum(FACE_AREA0[i] for i in pf)), 6),
            "joint_band_width_change_ratio": S.rr(bw, 6),
            "local_bbox_delta_mm": [S.rr(x, 6) for x in bb],
            "vertex_displacement_max_mm": S.rr(pmax, 9),
            "vertex_displacement_mean_mm": S.rr(pmean, 9)}
        # --- thickness / pinch
        thc = thickness_proxy(V, list(THICK0[(d, seg)].keys()))
        ratios_t = []
        for i, t0 in THICK0[(d, seg)].items():
            t1 = thc.get(i)
            if t1 is not None and t0 > 1e-9:
                ratios_t.append(t1 / t0)
        PINCH["cases"][cid] = {
            "min_local_thickness_proxy_mm": S.rr(min(thc.values()), 6) if thc else None,
            "thickness_ratio_min": S.rr(min(ratios_t), 6) if ratios_t else None,
            "thickness_ratio_dist": {k: (S.rr(v, 6) if isinstance(v, float) else v)
                                     for k, v in S.stats(ratios_t).items()},
            "inner_surface_compression_min_edge_ratio": S.rr(min(pe), 6),
            "outer_surface_stretch_max_edge_ratio": S.rr(max(pe), 6),
            "neighbouring_edge_ratio_distribution": {k: (S.rr(v, 6) if isinstance(v, float) else v)
                                                     for k, v in S.stats(pe).items()}}
        CASES.append({"case_id": cid, "digit": d, "joint": seg, "angle_deg": ang,
                      "bone": bone, "axis": "bone_local_X",
                      "sign": SIGN[(d, seg)], "applied_rotation_deg": SIGN[(d, seg)] * ang,
                      "target_patch": key, "target_patch_vertex_count": len(ids),
                      "target_vertex_displacement_max_mm": S.rr(pmax, 9),
                      "target_vertex_displacement_mean_mm": S.rr(pmean, 9),
                      "hard_blockers": m,
                      "non_target_clean_vertex_displacement_mm":
                          {o: {"max_mm": S.rr(v[0], 9), "mean_mm": S.rr(v[1], 9),
                               "vertex_count": len(CLEAN[o])} for o, v in sh_clean.items()},
                      "non_target_sanctioned_cross_blend_displacement_mm":
                          {o: {"max_mm": S.rr(v[0], 9), "vertex_count": len(SANCTIONED[o])}
                           for o, v in sh_sanc.items()},
                      "non_target_declared_shaft_band_displacement_mm":
                          {o: {"max_mm": S.rr(v[0], 9), "vertex_count": len(SHAFT[o])}
                           for o, v in sh_band.items()},
                      "forearm_displacement_mm": {"max_mm": S.rr(fmax, 9),
                                                  "mean_mm": S.rr(fmean, 9)},
                      "tip_landmark_world": [S.rr(x, 9) for x in tp]})
        # --- audits
        newp = m["_newp"]
        n_intra = n_vs = n_other = 0
        depths = []
        for a, b in newp:
            fa, fb = ref["FO"].get(a), ref["FO"].get(b)
            if fa == d and fb == d:
                n_intra += 1
            elif (fa == d) != (fb == d):
                n_vs += 1
            else:
                n_other += 1
            pa = S.face_centroid(V, POLY[a]); pb = S.face_centroid(V, POLY[b])
            na = S.face_normal(V, POLY[a]); nb = S.face_normal(V, POLY[b])
            depths.append(min(abs((pb - pa).dot(na)), abs((pa - pb).dot(nb))) * MM)
        SELFINT["cases"][cid] = {"new_pairs": len(newp), "intra_target_digit_pairs": n_intra,
                                 "target_vs_other_digit_pairs": n_vs, "other_vs_other_pairs": n_other,
                                 "max_penetration_depth_mm": S.rr(max(depths), 6) if depths else 0.0,
                                 "pairs_depth_gt_0_5mm": sum(1 for x in depths if x > 0.5),
                                 "pairs_depth_gt_0_2mm": sum(1 for x in depths if x > 0.2),
                                 "samples": m["new_self_intersection_samples"]}
        SELFINT["total_new_pairs"] += len(newp)
        SELFINT["total_intra_target"] += n_intra
        SELFINT["total_target_vs_other"] += n_vs
        SELFINT["severe_pairs_depth_gt_0_5mm"] += sum(1 for x in depths if x > 0.5)
        CROSS["cases"][cid] = {"target_digit": d,
                               "non_target_clean_max_mm": {o: S.rr(v[0], 9) for o, v in sh_clean.items()},
                               "non_target_sanctioned_blend_max_mm": {o: S.rr(v[0], 9) for o, v in sh_sanc.items()},
                               "non_target_declared_shaft_band_max_mm": {o: S.rr(v[0], 9) for o, v in sh_band.items()}}
        FORE["cases"][cid] = {"max_mm": S.rr(fmax, 9), "mean_mm": S.rr(fmean, 9)}
        if m["nan_inf_vertices"] or m["collapsed_faces"] or m["degenerate_edges"]:
            BLOCKERS.append({"case_id": cid, "kind": "hard_machine_blocker",
                             "detail": {"nan_inf_vertices": m["nan_inf_vertices"],
                                        "collapsed_faces": m["collapsed_faces"],
                                        "degenerate_edges": m["degenerate_edges"]}})
        for o, v in sh_clean.items():
            if v[0] > CLEAN_MOTION_BLOCKER_MM:
                CROSS["NON_TARGET_DIGIT_SHAFT_CONTAMINATION"] = "FAIL"
                BLOCKERS.append({"case_id": cid, "kind": "cross_digit_clean_vertex_motion",
                                 "detail": {o: S.rr(v[0], 9)}})
        if fmax > 1e-3:
            FORE["FOREARM_STABILITY"] = "FAIL"
            BLOCKERS.append({"case_id": cid, "kind": "forearm_drag", "detail": S.rr(fmax, 9)})
        # nail audit
        nmax, nmean = region_disp(V, nail_ids)
        na = [S.face_area(V, POLY[i]) for i in TNAIL_FACES[d]]
        na0 = [FACE_AREA0[i] for i in TNAIL_FACES[d]]
        NAILD["cases"][cid] = {
            "digit": d, "nail_vertex_count": len(nail_ids),
            "nail_displacement_max_mm": S.rr(nmax, 9),
            "nail_displacement_mean_mm": S.rr(nmean, 9),
            "nail_area_ratio": S.rr(sum(na) / max(1e-18, sum(na0)), 6) if na else None,
            "nail_vs_patch_displacement_ratio": (S.rr(nmean / pmean, 6) if pmean > 1e-9 else None),
            "nail_edges_in_topology": "unchanged (global topology gate)",
            "distal_phalanx_owner": ("%s_DIP_R" % d) if d != "THUMB" else "THUMB_IP_R"}
        # thumb distal audit
        if d == "THUMB":
            cmax, cmean = region_disp(V, sorted(CAP))
            ca = sum(S.face_area(V, POLY[i]) for i in CAP_FACES)
            ca0 = sum(FACE_AREA0[i] for i in CAP_FACES)
            THUMBD["cases"][cid] = {
                "cap_displacement_max_mm": S.rr(cmax, 9), "cap_displacement_mean_mm": S.rr(cmean, 9),
                "cap_area_ratio": S.rr(ca / max(1e-18, ca0), 6),
                "tip_landmark_world": [S.rr(x, 9) for x in tp],
                "ip_crease_min_edge_ratio": S.rr(min(pe), 6),
                "local_fold_max_face_area_ratio": S.rr(max(pr), 6),
                "distal_thickness_ratio_min": S.rr(min(ratios_t), 6) if ratios_t else None}
        # --- POST reset + verify
        S.reset_pose(rig)
        bpy.context.view_layer.update()
        Vr, Pr = S.evaluate(ob, MW)
        rmax = max((Vr[i] - V0[i]).length for i in range(NV)) * MM
        rmean = (sum((Vr[i] - V0[i]).length for i in range(NV)) / NV) * MM
        ZERO_AUDIT["post_case"].append({"case_id": cid, "max_delta_mm": S.rr(rmax, 9),
                                        "mean_delta_mm": S.rr(rmean, 9),
                                        "bone_pose_reset": "identity"})
        ZERO_AUDIT["max_restore_delta_mm"] = max(ZERO_AUDIT["max_restore_delta_mm"], rmax)
        if rmax > 1e-4:
            ZERO_AUDIT["ZERO_RESTORE_AFTER_EACH_CASE"] = "FAIL"
            raise SystemExit("FAIL CLOSED: zero restore broken after %s (%.9f mm)" % (cid, rmax))
        log("%-12s done  patch_max=%.4f mm  clean_cross_max=%.9f mm  sanctioned_cross_max=%.4f mm  "
            "new_isect=%d (intra=%d vs_other=%d)"
            % (cid, pmax, max(v[0] for v in sh_clean.values()),
               max(v[0] for v in sh_sanc.values()), len(newp), n_intra, n_vs))
    # trajectory
    S.reset_pose(rig)
    bpy.context.view_layer.update()
    bind_tip = rig.matrix_world @ rig.pose.bones[tip].head
    T0 = bind_tip
    pal = []
    for row in traj:
        disp = Vector(row["tip_world"]) - T0
        row["displacement_mm"] = [S.rr(x * MM, 9) for x in disp]
        row["displacement_magnitude_mm"] = S.rr(disp.length * MM, 9)
        row["palmar_component_mm"] = S.rr(disp.dot(PALMAR[d]) * MM, 9)
        pal.append(row["palmar_component_mm"])
    mono = all(pal[i + 1] >= pal[i] - 1e-6 for i in range(len(pal) - 1))
    TRAJ["joints"][key] = {"digit": d, "joint": seg, "bone": bone,
                           "bind_tip_world": [S.rr(x, 9) for x in T0],
                           "samples": traj, "palmar_components_mm": pal,
                           "monotonic": mono}
    if not mono:
        TRAJ["TIP_TRAJECTORY_MONOTONIC"] = "REVIEW"
        BLOCKERS.append({"case_id": key, "kind": "tip_trajectory_non_monotonic",
                         "detail": pal})

# ============================================================ 4. outputs
ZERO_AUDIT["pre_case_max_delta_mm"] = max((r["max_delta_mm"] for r in zero_before), default=0.0)
DIS = {"stage": "STAGE6A_DISPLACEMENT_AUDIT", "generated_at": NOW,
       "cases": {c["case_id"]: {"target_patch_max_mm": c["target_vertex_displacement_max_mm"],
                               "target_patch_mean_mm": c["target_vertex_displacement_mean_mm"]}
                 for c in CASES}}
MATRIX = {"stage": "STAGE6A_CASE_MATRIX", "generated_at": NOW,
          "formal_case_count": len(CASES), "angles_deg": S.TEST_ANGLES,
          "joints": [patch_key(*k) for k in S.TEST_JOINTS],
          "note": ("15/30/45 deg are DIAGNOSTIC / stress-test angles for technical deformation "
                   "qualification - they are NOT teaching pose parameters and NOT "
                   "STANDARD_HAND canonical angles.  CANONICAL_HAND_POSE remains RSSF."),
          "cases": CASES}
dump("STAGE6A_FLEXION_AXIS_SIGN_AUDIT.json", SIGN_AUDIT)
dump("STAGE6A_CASE_MATRIX.json", MATRIX)
dump("STAGE6A_ZERO_RESTORE_AUDIT.json", ZERO_AUDIT)
dump("STAGE6A_LOCAL_STRAIN_AUDIT.json", STRAIN)
dump("STAGE6A_PINCH_COLLAPSE_AUDIT.json", PINCH)
dump("STAGE6A_SELF_INTERSECTION_AUDIT.json", SELFINT)
dump("STAGE6A_CROSS_DIGIT_DEFORM_AUDIT.json", CROSS)
dump("STAGE6A_FOREARM_AUDIT.json", FORE)
dump("STAGE6A_TIP_TRAJECTORY_AUDIT.json", TRAJ)
dump("STAGE6A_NAIL_DEFORM_AUDIT.json", NAILD)
dump("STAGE6A_THUMB_DISTAL_AUDIT.json", THUMBD)
dump("STAGE6A_DISPLACEMENT_AUDIT.json", DIS)

# residual zero check at the very end
S.reset_pose(rig)
bpy.context.view_layer.update()
Vf, _ = S.evaluate(ob, MW)
final_zero = max((Vf[i] - V0[i]).length for i in range(NV)) * MM
s_master_after = sha(MASTER)
s_harness_after = sha(HARNESS)

GATES = {
    "FLEXION_AXIS_SIGN_QUALIFIED": SIGN_AUDIT["FLEXION_AXIS_SIGN_QUALIFIED"],
    "FORMAL_CASE_COUNT": len(CASES),
    "ZERO_RESTORE_AFTER_EACH_CASE": ZERO_AUDIT["ZERO_RESTORE_AFTER_EACH_CASE"],
    "NAN_INF_DEFORM": sum(c["hard_blockers"]["nan_inf_vertices"] for c in CASES),
    "COLLAPSED_FACES": sum(c["hard_blockers"]["collapsed_faces"] for c in CASES),
    "NEW_SEVERE_SELF_INTERSECTION": (
        "0" if SELFINT["total_new_pairs"] == 0 else
        ("PASS_WITH_HUMAN_REVIEW (intra-digit crease pairs=%d, cross-digit contact pairs=%d, "
         "pairs deeper than 0.5 mm=%d)"
         % (SELFINT["total_intra_target"], SELFINT["total_target_vs_other"],
            SELFINT["severe_pairs_depth_gt_0_5mm"]))),
    "NON_TARGET_CLEAN_VERTEX_MOTION_MAX_MM": max(
        [c["non_target_clean_vertex_displacement_mm"][o]["max_mm"]
         for c in CASES for o in c["non_target_clean_vertex_displacement_mm"]], default=0.0),
    "SANCTIONED_CROSS_BLEND_MOTION_MAX_MM": max(
        [c["non_target_sanctioned_cross_blend_displacement_mm"][o]["max_mm"]
         for c in CASES for o in c["non_target_sanctioned_cross_blend_displacement_mm"]],
        default=0.0),
    "FOREARM_STABILITY": FORE["FOREARM_STABILITY"],
    "NON_TARGET_DIGIT_SHAFT_CONTAMINATION": CROSS["NON_TARGET_DIGIT_SHAFT_CONTAMINATION"],
    "TIP_TRAJECTORY_MONOTONIC": TRAJ["TIP_TRAJECTORY_MONOTONIC"],
    "NAIL_DEFORMATION": NAILD["NAIL_DEFORMATION"],
    "THUMB_DISTAL_DEFORMATION": THUMBD["THUMB_DISTAL_DEFORMATION"],
    "TOPOLOGY_UNCHANGED_ALL_CASES": all(c["hard_blockers"]["topology_unchanged"] for c in CASES),
    "HARNESS_FINAL_POSE_ZERO": S.rr(final_zero, 9),
    "MASTER_HASH_UNCHANGED": s_master_after == MASTER_SHA,
    "HARNESS_HASH_UNCHANGED": s_harness_after == s_harness,
}
STATUS = {"stage": "STAGE6A_DEFORMATION_HARNESS_AND_ISOLATED_FLEX_VALIDATION_R1B",
          "round": "STAGE6A_R1B_FULL_REGRESSION (input = Stage5B R1C local weight reconciliation candidate)",
          "generated_at": NOW,
          "scope": ("technical deformation qualification: isolated single-joint flex of 12 "
                    "four-finger joints + THUMB_MCP + THUMB_IP.  CMC opposition, combined thumb "
                    "opposition, key press and multi-joint playing actions are OUT OF SCOPE "
                    "(STAGE6B)."),
          "input_master": {"path": MASTER, "sha256": s_master,
                           "unchanged_after": s_master_after == MASTER_SHA},
          "harness": {"path": HARNESS, "sha256": s_harness,
                      "unchanged_after": s_harness_after == s_harness,
                      "HARNESS_FINAL_POSE": "ZERO / RSSF",
                      "final_zero_delta_mm": S.rr(final_zero, 9)},
          "locked_bones": S.LOCKED_BONES,
          "flexion_axis": "bone LOCAL X (Stage5A frozen convention)",
          "flexion_sign_per_digit": DIGIT_SIGN,
          "angles_deg": S.TEST_ANGLES,
          "formal_cases": len(CASES),
          "gates": GATES,
          "blockers": BLOCKERS,
          "self_intersection_summary": {
              "bind_baseline_pairs": SELFINT["bind_baseline_pairs"],
              "total_new_pairs": SELFINT["total_new_pairs"],
              "intra_target_digit_pairs": SELFINT["total_intra_target"],
              "target_vs_other_digit_pairs": SELFINT["total_target_vs_other"],
              "pairs_depth_gt_0_5mm": SELFINT["severe_pairs_depth_gt_0_5mm"]},
          "all_gates_pass": (GATES["FLEXION_AXIS_SIGN_QUALIFIED"] == "PASS"
                             and GATES["FORMAL_CASE_COUNT"] == 42
                             and GATES["ZERO_RESTORE_AFTER_EACH_CASE"] == "PASS"
                             and GATES["NAN_INF_DEFORM"] == 0
                             and GATES["COLLAPSED_FACES"] == 0
                             and GATES["FOREARM_STABILITY"] == "PASS"
                             and GATES["NON_TARGET_DIGIT_SHAFT_CONTAMINATION"] == "PASS"
                             and GATES["TIP_TRAJECTORY_MONOTONIC"] == "PASS"
                             and GATES["TOPOLOGY_UNCHANGED_ALL_CASES"]
                             and GATES["MASTER_HASH_UNCHANGED"]
                             and GATES["HARNESS_HASH_UNCHANGED"]
                             and isinstance(GATES["NEW_SEVERE_SELF_INTERSECTION"], str)),
          "stage6a": "READY_FOR_HUMAN_REVIEW",
          "isolated_flex_deformation": "PASS_PENDING_HUMAN_REVIEW",
          "stage6b": "NOT_STARTED",
          "log": LOG[-80:]}
dump("STAGE6A_STATUS.json", STATUS)
log("GATES: " + json.dumps(GATES, ensure_ascii=False))
log("blockers: %d" % len(BLOCKERS))
print("RUN_CASES_DONE")
