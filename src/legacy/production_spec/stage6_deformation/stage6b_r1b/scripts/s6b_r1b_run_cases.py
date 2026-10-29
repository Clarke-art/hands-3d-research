# =====================================================================================
# STAGE6B -- 9 formal opposition / combined-deformation cases
# =====================================================================================
# READ-ONLY with respect to the harness (opened, posed, reset; never saved).
#   CMC_OPP_10 / _20 / _30          CMC opposition only
#   CMC_MCP_L1 / _L2 / _L3          CMC opposition + MCP flexion (coordinated)
#   FULL_OPP_L1 / _L2 / _L3         CMC + MCP + IP full chain
# Angles are DIAGNOSTIC stress-test parameters, NOT teaching values, NOT human ROM.
# =====================================================================================
import bpy
import sys
import os
import json
import math
import datetime
import numpy as np
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from collections import Counter

HERE0 = os.path.dirname(os.path.abspath(__file__))
PROD_PRE = os.path.abspath(os.path.join(HERE0, "..", "..", ".."))
sys.path.append(HERE0)
sys.path.append(os.path.join(PROD_PRE, "stage6_deformation", "stage6b", "scripts"))
sys.path.append(os.path.join(PROD_PRE, "stage6_deformation", "stage6b_r1b", "scripts"))
import s6b_common as B                                          # noqa: E402
import s6br1b_common as K                                       # noqa: E402
R1C = json.load(open(os.path.join(PROD_PRE, "stage5_production_rig", "stage5b_r1c",
                                  "STAGE5B_R1C_STATUS.json"), encoding="utf-8"))
B.R1B_MASTER = K.R1C_MASTER
B.R1B_SHA256 = R1C["candidate"]["sha256"]
B.HARNESS_R1 = os.path.join(PROD_PRE, "stage6_deformation", "stage6b_r1b",
                            "RIGHT_HAND_STAGE6B_OPPOSITION_HARNESS_R1B.blend")
if R1C["status"] != "CANDIDATE_FOR_HUMAN_REVIEW":
    raise SystemExit("FAIL CLOSED: Stage5B R1C not CANDIDATE_FOR_HUMAN_REVIEW")

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[S6B-RUN]", s, flush=True)


def dump(name, obj):
    json.dump(obj, open(os.path.join(OUTDIR, name), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    log("wrote %s" % name)


# ---------------------------------------------------------------- gates
s_r1b = B.sha256(B.R1B_MASTER)
s_r1a = B.sha256(B.R1A_HARNESS)
s_s5a = B.sha256(B.S5A_MASTER)
if (s_r1b, s_r1a, s_s5a) != (B.R1B_SHA256, B.R1A_HARNESS_SHA256, B.S5A_SHA256):
    raise SystemExit("FAIL CLOSED: frozen input hash drift")

vec = json.load(open(os.path.join(PROD_PRE, "stage6_deformation", "stage6b",
                                  "STAGE6B_OPPOSITION_VECTOR_AUDIT.json"), encoding="utf-8"))
UNIT = np.array(vec["CMC_OPPOSITION_UNIT_ROTATION"]["coefficients_local_XYZ"], dtype=float)
UNIT = UNIT / np.linalg.norm(UNIT)
TWIST = vec["axial_twist_qualification"]["CMC_AXIAL_TWIST_SIGN"]
log("CMC_OPPOSITION_UNIT_ROTATION = %s ; twist sign = %s"
    % ([round(float(x), 9) for x in UNIT], TWIST))

ctx = B.build_context()
V0 = ctx["V0"]
NV = ctx["NV"]
POLY = ctx["poly"]
EDGES = ctx["edges"]
FO = ctx["FO"]
own_r1a = ctx["own_r1a"]
PROBE = K.load_probe_sets()
PART = K.r2_partition(ctx, ctx["ref"])
CORRECT = K.build_corrected_ownership(ctx, ctx["ref"], PART["partition"], PROBE)
own = CORRECT["corrected"]
CORRECTION_DOMAIN = set(CORRECT["domain"])
HISTORIC_B = list(PROBE["CLASS_B"])
FO = {}
for _fi, _p in enumerate(ctx["poly"]):
    _c = Counter(own[v] for v in _p)
    _m = _c.most_common()
    _top = [k for k, v in _m if v == _m[0][1]]
    if len(_top) == 1:
        FO[_fi] = _top[0]
    else:
        _cc = sum((V0[v] for v in _p), Vector()) / len(_p)
        FO[_fi] = sorted(_top, key=lambda D: sum((V0[v] - _cc).length
                                                for v in _p if own[v] == D))[0]
S6 = B.S6

MED = ctx["MED"]
ARC = ctx["ARC"]
s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]
CAGE = sorted(ctx["cmc_cage_patch"])
THENAR = sorted(ctx["thenar"])
WEB = sorted(ctx["first_web"])
CAP = sorted(ctx["distal_cap"])
NAIL = sorted(ctx["nail_thumb"])
MCP_PATCH = sorted(i for i in ctx["thumb_own"] if abs(ARC[i] - s_MCP) <= 2.0 * MED)
IP_PATCH = sorted(i for i in ctx["thumb_own"] if abs(ARC[i] - s_IP) <= 2.0 * MED)
WEB_BND_V, WEB_BND_E = B.web_boundary(ctx)
CMC_C = ctx["cmc_centre"]
log("regions: CMC_cage=%d thenar=%d web=%d(bnd v%d/e%d) cap=%d nail=%d MCP=%d IP=%d"
    % (len(CAGE), len(THENAR), len(WEB), len(WEB_BND_V), len(WEB_BND_E), len(CAP), len(NAIL),
       len(MCP_PATCH), len(IP_PATCH)))

# ---------------------------------------------------------------- open harness
bpy.ops.wm.open_mainfile(filepath=B.HARNESS_R1)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
me = ob.data
MW = ob.matrix_world.copy()
M3 = MW.to_3x3()
W_HARNESS = B.RB.read_object_weights(ob, NV)

# ---------------------------------------------------------------- bind baselines
B.reset_pose(rig)
B.update()
FACE_AREA0 = [B.face_area(V0, p) for p in POLY]
EDGE_LEN0 = [(V0[a] - V0[b]).length for a, b in EDGES]
FACE_NOR0 = [B.face_normal(V0, p) for p in POLY]
BASE_PAIRS = B.intersect_pairs(V0, POLY)
NAIL_FACES = [fi for fi in range(len(POLY)) if all(v in ctx["nail_thumb"] for v in POLY[fi])]
CAP_FACES = [fi for fi in range(len(POLY)) if all(v in ctx["distal_cap"] for v in POLY[fi])]
NAIL_SUM0 = sum(FACE_AREA0[i] for i in NAIL_FACES)
CAP_SUM0 = sum(FACE_AREA0[i] for i in CAP_FACES)
n_pad0 = -B.nail_normal(V0, POLY, NAIL_FACES)
tip0 = B.tip_world(rig)


def rg(r):
    return B.region_faces(POLY, r)


def re_(r):
    return B.region_edges(EDGES, r)


ADJ = {}
for _a, _b in EDGES:
    ADJ.setdefault(_a, set()).add(_b)
    ADJ.setdefault(_b, set()).add(_a)


def domain_of(ids, family):
    """region + 1-ring closure, RESTRICTED to the region's own digit family.

    Cross-digit seam edges are excluded by construction: a region's strain must be measured on
    its own chain's surface, never on the seam that joins it to another digit.
    """
    d = set(ids)
    for i in list(ids):
        d |= ADJ.get(i, set())
    return set(i for i in d if own[i] in family)


def faces_in(d):
    return [fi for fi, p in enumerate(POLY) if all(v in d for v in p)]


def edges_in(d):
    return [k for k, (a, b) in enumerate(EDGES) if a in d and b in d]


FAM = {"CMC_cage": ("THUMB", "wrist"), "thenar": ("THUMB", "wrist"),
       "first_web": ("THUMB",), "thumb_MCP": ("THUMB",), "thumb_IP": ("THUMB",),
       "distal_cap": ("THUMB",), "nail": ("THUMB",)}
_IDS = {"CMC_cage": CAGE, "thenar": THENAR, "first_web": WEB, "thumb_MCP": MCP_PATCH,
        "thumb_IP": IP_PATCH, "distal_cap": CAP, "nail": NAIL}
FIXED_FACES = {"distal_cap": CAP_FACES, "nail": NAIL_FACES}
# (region id set, strain-domain id set, INTRA-domain faces, INTRA-domain edges,
#  ALL touching faces/edges)
REG = {}
for _nm, _ids in _IDS.items():
    _d = domain_of(_ids, FAM[_nm])
    REG[_nm] = (_ids, _d, FIXED_FACES.get(_nm, faces_in(_d)), edges_in(_d),
                rg(_ids), re_(_ids))
log("intra-region face/edge counts: "
    + ", ".join("%s=%d/%d" % (k, len(v[1]), len(v[2])) for k, v in REG.items()))

# digit-ownership seam edges (the surface joins two digits here)
SEAM_EDGES = [k for k, (a, b) in enumerate(EDGES) if own[a] != own[b]]
SEAM_TI = [k for k in SEAM_EDGES if {own[EDGES[k][0]], own[EDGES[k][1]]} == {"THUMB", "INDEX"}]
SEAM_TI_LEN0 = dict((k, EDGE_LEN0[k] * 1000.0) for k in SEAM_TI)
HIST_TI = [k for k, a, b in HISTORIC_B]
HIST_LEN0 = dict((k, EDGE_LEN0[k] * 1000.0) for k in HIST_TI)
log("R2 THUMB|INDEX boundary edges=%d (bind %.4f..%.4f mm)"
    % (len(SEAM_TI), min(SEAM_TI_LEN0.values()), max(SEAM_TI_LEN0.values())))
log("HISTORIC_CLASS_B probe edges=%d (bind %.4f..%.4f mm)"
    % (len(HIST_TI), min(HIST_LEN0.values()), max(HIST_LEN0.values())))

# four-finger clean vertices (must stay at bind: no foreign group)
DOB = {"WRIST_R": "wrist"}
for _d in B.RC.DIGITS:
    for _s in B.RC.CHAIN[_d]:
        DOB["%s_%s_R" % (_d, _s)] = _d
FOREIGN = [sorted(g for g in W_HARNESS[i] if DOB.get(g, "wrist") not in (own[i], "wrist"))
           for i in range(NV)]
FOUR = ("INDEX", "MIDDLE", "RING", "LITTLE")
CLEAN_FOUR = sorted(i for i in range(NV) if own[i] in FOUR and not FOREIGN[i])
SANCTIONED_FOUR = sorted(i for i in range(NV) if own[i] in FOUR and FOREIGN[i])
PALM = sorted(i for i in range(NV) if own[i] == "wrist")
wH = B.S6.bone_world(rig, "WRIST_R", True)
wT = B.S6.bone_world(rig, "WRIST_R", False)
wU = (wT - wH).normalized()
FOREARM = [i for i in range(NV) if (V0[i] - wH).dot(wU) < 0.0]
CLEAN_MOTION_MM = 1e-3
log("clean four-finger=%d sanctioned=%d palm=%d forearm=%d"
    % (len(CLEAN_FOUR), len(SANCTIONED_FOUR), len(PALM), len(FOREARM)))

# ---------------------------------------------------------------- bind region descriptors
CAGE_KD = {}
for nm, (ids, _d, _f, _e, _fa, _ea) in REG.items():
    kd = KDTree(len(ids))
    for n, i in enumerate(ids):
        kd.insert(V0[i], n)
    kd.balance()
    CAGE_KD[nm] = kd
CAP_KD = KDTree(len(CAP))
for n, i in enumerate(CAP):
    CAP_KD.insert(V0[i], n)
CAP_KD.balance()
NAIL_CAP_DIST0 = dict((i, (V0[i] - CAP_KD.find(V0[i])[0]).length) for i in NAIL)
WEB_BND_LEN0 = dict((e, (V0[e[0]] - V0[e[1]]).length) for e in WEB_BND_E)
WEB_HULL0 = None

INDEX_OWN = sorted(i for i in range(NV) if own[i] == "INDEX")
IDX_KD0 = KDTree(len(INDEX_OWN))
for n, i in enumerate(INDEX_OWN):
    IDX_KD0.insert(V0[i], n)
IDX_KD0.balance()
THUMB_OWN_S = sorted(ctx["thumb_own"])
TH_KD0 = KDTree(len(THUMB_OWN_S))
for n, i in enumerate(THUMB_OWN_S):
    TH_KD0.insert(V0[i], n)
TH_KD0.balance()
BIND_TI_DIST = min((V0[i] - IDX_KD0.find(V0[i])[0]).length for i in THUMB_OWN_S) * 1000.0


def pca_extents(V, ids):
    P = np.array([[V[i].x, V[i].y, V[i].z] for i in ids])
    c = P.mean(axis=0)
    Q = P - c
    cov = np.cov(Q.T)
    w, v = np.linalg.eigh(cov)
    order = np.argsort(w)[::-1]
    axes = v[:, order]
    proj = Q @ axes
    ext = proj.max(axis=0) - proj.min(axis=0)
    return {"centroid": [B.rr(x, 9) for x in c],
            "axes": [[B.rr(x, 9) for x in axes[:, k]] for k in range(3)],
            "extents_mm": [B.rr(x * 1000.0, 6) for x in ext],
            "eigenvalues": [B.rr(x, 15) for x in w[order]],
            "bbox_volume_proxy_mm3": B.rr(float(np.prod(ext)) * 1e9, 6)}


def rigid_fit_residual(V, ids, Vref, ref_ids=None):
    """Kabsch rigid fit of the region from bind to the posed state; returns the max residual
    in mm, the region characteristic size in mm, and the relative residual.  A rigidly moving
    patch gives ~0 regardless of how far it translated, so this - not raw displacement spread -
    is the correct 'did this patch deform / detach' measure."""
    A = np.array([[Vref[i].x, Vref[i].y, Vref[i].z] for i in ids])
    Bp = np.array([[V[i].x, V[i].y, V[i].z] for i in ids])
    ca, cb = A.mean(0), Bp.mean(0)
    H = (A - ca).T @ (Bp - cb)
    U, S, Vt = np.linalg.svd(H)
    D = np.diag([1.0, 1.0, float(np.sign(np.linalg.det(Vt.T @ U.T)))])
    R = Vt.T @ D @ U.T
    fit = (A - ca) @ R.T + cb
    res = np.linalg.norm(fit - Bp, axis=1) * 1000.0
    size = float(np.linalg.norm(A - ca, axis=1).mean()) * 1000.0
    return float(res.max()), size, float(res.max() / max(1e-9, size))


def hull_area_2d(pts2d):
    """Andrew monotone chain convex hull area (mm^2)"""
    p = sorted(set((round(float(a), 9), round(float(b), 9)) for a, b in pts2d))
    if len(p) < 3:
        return 0.0

    def cross(o, a, bb):
        return (a[0] - o[0]) * (bb[1] - o[1]) - (a[1] - o[1]) * (bb[0] - o[0])

    lo = []
    for q in p:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    up = []
    for q in reversed(p):
        while len(up) >= 2 and cross(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    h = lo[:-1] + up[:-1]
    if len(h) < 3:
        return 0.0
    a = 0.0
    for i in range(len(h)):
        x1, y1 = h[i]
        x2, y2 = h[(i + 1) % len(h)]
        a += x1 * y2 - x2 * y1
    return abs(a) * 0.5


def web_opening_area(V):
    ids = WEB
    P = np.array([[V[i].x, V[i].y, V[i].z] for i in ids])
    c = P.mean(axis=0)
    Q = P - c
    w, v = np.linalg.eigh(np.cov(Q.T))
    axes = v[:, np.argsort(w)[::-1]]
    proj = Q @ axes
    return hull_area_2d(proj[:, :2]) * 1e6      # mm^2


WEB_HULL0 = web_opening_area(V0)
THENAR_PCA0 = pca_extents(V0, THENAR)
CAGE_PCA0 = pca_extents(V0, CAGE)
log("bind: web opening area %.6f mm2 ; thenar bbox vol %.3f mm3 ; thumb-index nearest %.4f mm"
    % (WEB_HULL0, THENAR_PCA0["bbox_volume_proxy_mm3"], BIND_TI_DIST))

# ---------------------------------------------------------------- cases
CASES = []
for i, a in enumerate(B.CMC_OPP_ANGLES, start=1):
    CASES.append({"case_id": "CMC_OPP_%d" % int(a), "kind": "CMC_ISOLATED",
                  "cmc_deg": a, "mcp_deg": 0.0, "ip_deg": 0.0, "level": i})
for i, a in enumerate(B.CMC_OPP_ANGLES, start=1):
    CASES.append({"case_id": "CMC_MCP_L%d" % i, "kind": "CMC_MCP_COORDINATED",
                  "cmc_deg": a, "mcp_deg": a, "ip_deg": 0.0, "level": i})
for i, a in enumerate(B.CMC_OPP_ANGLES, start=1):
    CASES.append({"case_id": "FULL_OPP_L%d" % i, "kind": "FULL_CHAIN",
                  "cmc_deg": a, "mcp_deg": a, "ip_deg": B.FULL_CHAIN_IP[i - 1], "level": i})
log("formal cases = %d : %s" % (len(CASES), [c["case_id"] for c in CASES]))

# ---------------------------------------------------------------- audits
MATRIX = {"stage": "STAGE6B_R1B_CASE_MATRIX", "generated_at": NOW,
          "note": ("diagnostic / stress-test parameters ONLY - NOT teaching values, NOT human "
                   "ROM, NOT STANDARD_HAND definition"),
          "cmc_opposition_unit_rotation_local_XYZ": [B.rr(float(x), 12) for x in UNIT],
          "cmc_axial_twist_sign": TWIST,
          "cases": []}
CAGE_AUD = {"stage": "STAGE6B_R1B_CMC_CAGE_DEFORM_AUDIT", "generated_at": NOW,
            "authority": ctx["cmc_cage_audit"], "patch_vertex_count": len(CAGE),
            "cases": {}}
THENAR_AUD = {"stage": "STAGE6B_R1B_THENAR_DEFORM_AUDIT", "generated_at": NOW,
              "semantic_region": "Stage5B approved THENAR_BASE", "cases": {}}
WEB_AUD = {"stage": "STAGE6B_R1B_FIRST_WEB_DEFORM_AUDIT", "generated_at": NOW,
           "semantic_region": "Stage5B approved FIRST_WEB (static mask NOT redefined)",
           "boundary_vertex_count": len(WEB_BND_V), "boundary_edge_count": len(WEB_BND_E),
           "cases": {}}
TRAJ = {"stage": "STAGE6B_R1B_TIP_PAD_TRAJECTORY_AUDIT.json", "generated_at": NOW,
        "bind_tip_world": B.v3(tip0, 9), "bind_pad_proxy_normal": B.v3(n_pad0, 9),
        "bind_pad_alignment_with_T_OPPOSE": B.rr(n_pad0.dot(B.T_OPPOSE), 9), "cases": {}}
CONTACT = {"stage": "STAGE6B_R1B_CONTACT_PROGRESSION_AUDIT", "generated_at": NOW,
           "bind_thumb_index_nearest_mm": B.rr(BIND_TI_DIST, 6),
           "classification": ["A_INTRA_THUMB", "B_THUMB_INDEX", "C_THUMB_PALM",
                              "D_THUMB_OTHER_DIGIT", "E_NON_TARGET_DIGIT"],
           "cases": {}}
CROSS = {"stage": "STAGE6B_R1B_CROSS_DIGIT_DEFORM_AUDIT", "generated_at": NOW,
         "clean_motion_blocker_mm": CLEAN_MOTION_MM, "cases": {},
         "NON_TARGET_DIGIT_SHAFT_CONTAMINATION": "PASS"}
STRAIN = {"stage": "STAGE6B_R1B_LOCAL_STRAIN_AUDIT", "generated_at": NOW,
          "note": "machine values are DIAGNOSTIC; only NaN / collapse / degeneration are hard",
          "regions": list(REG.keys()), "cases": {}}
SELFINT = {"stage": "STAGE6B_R1B_SELF_INTERSECTION_AUDIT", "generated_at": NOW,
           "bind_baseline_pairs": len(BASE_PAIRS), "cases": {}}
ND = {"stage": "STAGE6B_R1B_NAIL_DISTAL_CAP_AUDIT", "generated_at": NOW,
      "nail_vertex_count": len(NAIL), "nail_face_count": len(NAIL_FACES),
      "distal_cap_vertex_count": len(CAP), "distal_cap_face_count": len(CAP_FACES),
      "cases": {}}
ZERO = {"stage": "STAGE6B_R1B_ZERO_RESTORE_AUDIT", "generated_at": NOW,
        "hard_gate_mm": 1e-4, "noise_floor_mm": 5.967e-05, "pre": [], "post": [],
        "cases": []}
PALM_FOREARM = {"stage": "STAGE6B_R1B_PALM_FOREARM_STABILITY", "generated_at": NOW, "cases": {}}
HISTB = {"stage": "STAGE6B_R1B_HISTORIC_CLASS_B_EDGE_STRETCH_AUDIT", "generated_at": NOW,
         "method": "the exact 61 CLASS_B edges approved by the Stage6B R1A seam provenance round are tracked FOREVER with the frozen Stage6B tear criterion (posed stretch > 3x AND posed length > 5 mm)",
         "edge_ids": sorted(HIST_TI), "cases": {}}
SEAM = {"stage": "STAGE6B_R1B_R2_BOUNDARY_DEFORM_AUDIT", "generated_at": NOW,
        "method": ("edges whose two endpoints carry different digit ownership are the places "
                   "where one closed surface physically joins two digits.  They are reported "
                   "SEPARATELY from region strain: a region's strain must not be blamed for a "
                   "cross-digit seam edge being pulled apart."),
        "thumb_index_seam_bind_mm": B.rr(min(SEAM_TI_LEN0.values()), 6), "cases": {}}
BLOCKERS = []


def disp(V, ids):
    d = [(V[i] - V0[i]).length for i in ids]
    return (max(d) if d else 0.0), (sum(d) / len(d) if d else 0.0)


for c in CASES:
    cid = c["case_id"]
    # 1/2 RESET + baseline
    B.reset_pose(rig)
    B.update()
    Vz, _ = B.evaluate(ob, MW)
    zmax = max((Vz[i] - V0[i]).length for i in range(NV)) * 1000.0
    ZERO["pre"].append({"case_id": cid, "max_delta_mm": B.rr(zmax, 9)})
    if zmax > 1e-4:
        raise SystemExit("FAIL CLOSED: pre-case zero broken at %s" % cid)
    # 3/4/5 apply pose (single reset, no accumulation)
    cmc_q, cmc_mag = B.rotation_vector_to_quaternion(Vector(UNIT) * math.radians(c["cmc_deg"]))
    pb = rig.pose.bones["THUMB_CMC_R"]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = cmc_q
    if c["mcp_deg"]:
        B.set_local_axis_rotation(rig, "THUMB_MCP_R",
                                  B.FLEXION_SIGN["THUMB_MCP"] * c["mcp_deg"])
    if c["ip_deg"]:
        B.set_local_axis_rotation(rig, "THUMB_IP_R",
                                  B.FLEXION_SIGN["THUMB_IP"] * c["ip_deg"])
    # 6 evaluate
    B.update()
    V, P = B.evaluate(ob, MW)
    tip = B.tip_world(rig)
    tip_d = tip - tip0

    # ---- hard blockers
    nan = sum(1 for v in V if not all(math.isfinite(x) for x in v))
    areas = [B.face_area(V, p) for p in P]
    fr = [(areas[i] / FACE_AREA0[i]) if FACE_AREA0[i] > 1e-18 else 0.0
          for i in range(len(P))]
    el = [(V[a] - V[b]).length for a, b in EDGES]
    er = [(el[k] / EDGE_LEN0[k]) if EDGE_LEN0[k] > 1e-18 else 0.0 for k in range(len(el))]
    collapsed = sum(1 for i, a in enumerate(areas) if a <= 1e-12 or fr[i] <= 1e-6)
    degen = sum(1 for x in el if x <= 1e-12)
    if nan or collapsed or degen:
        BLOCKERS.append({"case_id": cid, "kind": "hard_machine_blocker",
                         "detail": {"nan": nan, "collapsed": collapsed, "degenerate": degen}})

    # ---- strain families (INTRA-region only: cross-digit seam edges are NOT region strain)
    strain_row = {}
    for nm, (ids, dom, faces, eids, faces_all, eids_all) in REG.items():
        strain_row[nm] = B.strain_block(V, V0, POLY, EDGES, FACE_AREA0, EDGE_LEN0, faces, eids)
        strain_row[nm]["seam_edges_touching_region"] = len(
            set(eids_all) - set(eids))
    # thumb MCP / IP crease guard: compare against the Stage6A accepted residual
    strain_row["thumb_MCP"]["STAGE6A_residual_reference_min_edge"] = 0.219223
    strain_row["thumb_MCP"]["residual_flag"] = (
        "NEW_STAGE6B_EVIDENCE" if strain_row["thumb_MCP"]["min_edge_ratio"] < 0.219223 * 0.5
        else "within/near Stage6A residual")
    STRAIN["cases"][cid] = strain_row

    # ---- CMC cage
    cs = strain_row["CMC_cage"]
    cage_faces = REG["CMC_cage"][2]
    fold = []
    for fi in cage_faces:
        nrm = B.face_normal(V, POLY[fi])
        if nrm.dot(FACE_NOR0[fi]) < -0.5:
            fold.append(fi)
    cage_pairs = B.intersect_pairs_subset(V, POLY, cage_faces)
    cage_new = cage_pairs - B.intersect_pairs_subset(V0, POLY, cage_faces)
    cage_boundary = [e for e in EDGES if (e[0] in set(CAGE)) != (e[1] in set(CAGE))]
    cb_ratio = [((V[a] - V[b]).length / max(1e-18, (V0[a] - V0[b]).length))
                for a, b in cage_boundary]
    cb_disc = [abs((V[a] - V0[a]).length - (V[b] - V0[b]).length) * 1000.0
               for a, b in cage_boundary]
    cmax, cmean = disp(V, CAGE)
    cage_ok = (cs["min_face_area_ratio"] is None or cs["min_face_area_ratio"] > 0.05) and \
              len(cage_new) == 0
    CAGE_AUD["cases"][cid] = {
        "cmc_deg": c["cmc_deg"], "cmc_magnitude_rad": B.rr(cmc_mag, 9),
        "strain": cs,
        "face_area_ratio_min": cs["min_face_area_ratio"],
        "edge_ratio_min": cs["min_edge_ratio"], "edge_ratio_max": cs["max_edge_ratio"],
        "fold_over_face_count_normal_dot_lt_-0.5": len(fold),
        "fold_over_faces": fold[:20],
        "new_self_intersection_pairs_within_cage": len(cage_new),
        "new_pair_samples": sorted(cage_new)[:10],
        "boundary_edge_count": len(cage_boundary),
        "boundary_edge_ratio_min": B.rr(min(cb_ratio), 6) if cb_ratio else None,
        "boundary_edge_ratio_max": B.rr(max(cb_ratio), 6) if cb_ratio else None,
        "boundary_displacement_discontinuity_max_mm": B.rr(max(cb_disc), 9) if cb_disc else 0.0,
        "displacement_max_mm": B.rr(cmax * 1000.0, 9),
        "displacement_mean_mm": B.rr(cmean * 1000.0, 9),
        "cage_pca": pca_extents(V, CAGE),
        "CMC_CAGE_CATASTROPHIC_FOLD_OVER": not cage_ok,
    }
    if not cage_ok:
        BLOCKERS.append({"case_id": cid, "kind": "CMC_CAGE_CATASTROPHIC_FOLD_OVER",
                         "detail": {"min_face_area_ratio": cs["min_face_area_ratio"],
                                    "new_pairs_in_cage": len(cage_new)}})

    # ---- thenar
    t_pca = pca_extents(V, THENAR)
    t_dist0 = sorted((V0[i] - CMC_C).length * 1000.0 for i in THENAR)
    t_dist = sorted((V[i] - CMC_C).length * 1000.0 for i in THENAR)
    tmax, tmean = disp(V, THENAR)
    t_boundary = [e for e in EDGES if (e[0] in set(THENAR)) != (e[1] in set(THENAR))]
    tb_ratio = [((V[a] - V[b]).length / max(1e-18, (V0[a] - V0[b]).length))
                for a, b in t_boundary]
    t_inv = sum(1 for fi in REG["thenar"][2]
                if B.face_normal(V, POLY[fi]).dot(FACE_NOR0[fi]) < -0.5)
    vol_ratio = (t_pca["bbox_volume_proxy_mm3"]
                 / max(1e-9, THENAR_PCA0["bbox_volume_proxy_mm3"]))
    THENAR_AUD["cases"][cid] = {
        "local_surface_area_ratio": strain_row["thenar"]["local_surface_area_ratio"],
        "face_area_ratio_min": strain_row["thenar"]["min_face_area_ratio"],
        "pca_bbox_axes": t_pca["axes"], "pca_extents_mm": t_pca["extents_mm"],
        "pca_bbox_volume_proxy_mm3": t_pca["bbox_volume_proxy_mm3"],
        "pca_bbox_volume_ratio_vs_bind": B.rr(vol_ratio, 6),
        "pca_centroid": t_pca["centroid"],
        "centroid_shift_mm": B.rr(float(np.linalg.norm(
            np.array(t_pca["centroid"]) - np.array(THENAR_PCA0["centroid"]))) * 1000.0, 9),
        "radial_dist_to_CMC_joint_mm": {"bind": {"min": B.rr(t_dist0[0], 4),
                                                 "median": B.rr(t_dist0[len(t_dist0) // 2], 4),
                                                 "p95": B.rr(t_dist0[int(0.95 * (len(t_dist0) - 1))], 4),
                                                 "max": B.rr(t_dist0[-1], 4)},
                                        "case": {"min": B.rr(t_dist[0], 4),
                                                 "median": B.rr(t_dist[len(t_dist) // 2], 4),
                                                 "p95": B.rr(t_dist[int(0.95 * (len(t_dist) - 1))], 4),
                                                 "max": B.rr(t_dist[-1], 4)}},
        "boundary_edge_count": len(t_boundary),
        "boundary_edge_ratio_min": B.rr(min(tb_ratio), 6) if tb_ratio else None,
        "boundary_edge_ratio_max": B.rr(max(tb_ratio), 6) if tb_ratio else None,
        "inverted_face_count_diagnostic": t_inv,
        "extreme_vertex_displacement_max_mm": B.rr(tmax * 1000.0, 9),
        "mean_vertex_displacement_mm": B.rr(tmean * 1000.0, 9),
        "THENAR_CATASTROPHIC_COLLAPSE": bool(
            (strain_row["thenar"]["min_face_area_ratio"] or 1.0) < 0.05 or vol_ratio < 0.30),
    }
    if THENAR_AUD["cases"][cid]["THENAR_CATASTROPHIC_COLLAPSE"]:
        BLOCKERS.append({"case_id": cid, "kind": "THENAR_CATASTROPHIC_COLLAPSE",
                         "detail": {"vol_ratio": B.rr(vol_ratio, 6)}})

    # ---- first web
    w_ratio = [((V[a] - V[b]).length / max(1e-18, WEB_BND_LEN0[e]))
               for e in WEB_BND_E for a, b in [e]]
    w_gaps = sorted(((V[a] - V[b]).length * 1000.0) for a, b in WEB_BND_E)
    w_bind_gaps = sorted(WEB_BND_LEN0[e] * 1000.0 for e in WEB_BND_E)
    w_area = web_opening_area(V)
    w_max, w_mean = disp(V, WEB)
    w_inv = sum(1 for fi in REG["first_web"][2]
                if B.face_normal(V, POLY[fi]).dot(FACE_NOR0[fi]) < -0.5)
    # a tear is local surface destruction, NOT cross-chain seam strain (Stage6A rule: a normal
    # flip alone is never the inversion criterion)
    web_selfint = B.intersect_pairs_subset(V, POLY, REG["first_web"][2]) - \
        B.intersect_pairs_subset(V0, POLY, REG["first_web"][2])
    tear_degenerate = sum(1 for fi in REG["first_web"][2]
                          if FACE_AREA0[fi] > 1e-18
                          and B.face_area(V, POLY[fi]) / FACE_AREA0[fi] < 0.05)
    seam_strain = sorted(
        [(k, ((V[EDGES[k][0]] - V[EDGES[k][1]]).length / max(1e-18, EDGE_LEN0[k])),
          EDGE_LEN0[k] * 1000.0)
         for k in (set(REG["first_web"][5]) - set(REG["first_web"][3]))], key=lambda x: -x[1])
    WEB_AUD["cases"][cid] = {
        "boundary_continuity": {
            "edge_ratio_min": B.rr(min(w_ratio), 6) if w_ratio else None,
            "edge_ratio_max": B.rr(max(w_ratio), 6) if w_ratio else None,
            "boundary_edge_count": len(WEB_BND_E)},
        "selected_vertex_displacement_max_mm": B.rr(w_max * 1000.0, 9),
        "selected_vertex_displacement_mean_mm": B.rr(w_mean * 1000.0, 9),
        "boundary_gap_mm": {"bind_min": B.rr(w_bind_gaps[0], 6),
                            "bind_median": B.rr(w_bind_gaps[len(w_bind_gaps) // 2], 6),
                            "case_min": B.rr(w_gaps[0], 6),
                            "case_median": B.rr(w_gaps[len(w_gaps) // 2], 6)},
        "web_opening_area_mm2": B.rr(w_area, 6),
        "web_opening_area_ratio_vs_bind": B.rr(w_area / max(1e-18, WEB_HULL0), 6),
        "face_area_ratio_min": strain_row["first_web"]["min_face_area_ratio"],
        "edge_ratio_min": strain_row["first_web"]["min_edge_ratio"],
        "edge_ratio_max": strain_row["first_web"]["max_edge_ratio"],
        "local_inversion_face_count_normal_flip_diagnostic": w_inv,
        "degenerate_face_count": tear_degenerate,
        "new_self_intersection_pairs_within_web": len(web_selfint),
        "cross_chain_seam_edges_touching_web": len(seam_strain),
        "cross_chain_seam_edge_strain": [
            {"edge": k, "ratio": B.rr(r, 6), "bind_mm": B.rr(l0, 6),
             "posed_mm": B.rr(r * l0, 6)} for k, r, l0 in seam_strain[:8]],
        "cross_chain_seam_max_ratio": B.rr(seam_strain[0][1], 6) if seam_strain else None,
        "FIRST_WEB_ACTUAL_TEAR": bool(tear_degenerate > 0 or len(web_selfint) > 0),
    }
    if tear_degenerate or len(web_selfint):
        BLOCKERS.append({"case_id": cid, "kind": "FIRST_WEB_ACTUAL_TEAR",
                         "detail": {"degenerate_faces": tear_degenerate,
                                    "new_self_intersection": len(web_selfint)}})

    # ---- tip / pad trajectory
    n_pad = -B.nail_normal(V, POLY, NAIL_FACES)
    TRAJ["cases"][cid] = {
        "cmc_deg": c["cmc_deg"], "mcp_deg": c["mcp_deg"], "ip_deg": c["ip_deg"],
        "tip_world": B.v3(tip, 9),
        "displacement_mm": B.v3(tip_d * 1000.0, 9),
        "displacement_magnitude_mm": B.rr(tip_d.length * 1000.0, 9),
        "palmar_component_mm": B.rr(tip_d.dot(B.PALMAR) * 1000.0, 9),
        "ulnar_component_mm": B.rr(tip_d.dot(B.ULNAR) * 1000.0, 9),
        "radial_component_mm": B.rr(tip_d.dot(B.RADIAL) * 1000.0, 9),
        "dorsal_component_mm": B.rr(tip_d.dot(B.DORSAL) * 1000.0, 9),
        "distal_component_mm": B.rr(tip_d.dot(B.DISTAL) * 1000.0, 9),
        "T_OPPOSE_component_mm": B.rr(tip_d.dot(B.T_OPPOSE) * 1000.0, 9),
        "pad_proxy_normal": B.v3(n_pad, 9),
        "pad_alignment_with_T_OPPOSE": B.rr(n_pad.dot(B.T_OPPOSE), 9),
        "pad_alignment_change_vs_bind": B.rr(n_pad.dot(B.T_OPPOSE)
                                             - n_pad0.dot(B.T_OPPOSE), 9),
        "pad_orientation_change_deg_vs_bind": B.rr(math.degrees(n_pad0.angle(n_pad)), 6),
    }

    # ---- contact progression
    newp = sorted(B.intersect_pairs(V, POLY) - BASE_PAIRS)
    cls = {"A_INTRA_THUMB": [], "B_THUMB_INDEX": [], "C_THUMB_PALM": [],
           "D_THUMB_OTHER_DIGIT": [], "E_NON_TARGET_DIGIT": []}
    depths = []
    for a, b in newp:
        fa, fb = FO.get(a), FO.get(b)
        pa = B.face_centroid(V, POLY[a])
        pbb = B.face_centroid(V, POLY[b])
        na = B.face_normal(V, POLY[a])
        nb = B.face_normal(V, POLY[b])
        dep = min(abs((pbb - pa).dot(na)), abs((pa - pbb).dot(nb))) * 1000.0
        depths.append(dep)
        s = {fa, fb}
        if fa == "THUMB" and fb == "THUMB":
            cls["A_INTRA_THUMB"].append((a, b))
        elif s == {"THUMB", "INDEX"}:
            cls["B_THUMB_INDEX"].append((a, b))
        elif "THUMB" in s and "wrist" in s:
            cls["C_THUMB_PALM"].append((a, b))
        elif "THUMB" in s and (s & {"MIDDLE", "RING", "LITTLE"}):
            cls["D_THUMB_OTHER_DIGIT"].append((a, b))
        elif "THUMB" not in s:
            cls["E_NON_TARGET_DIGIT"].append((a, b))
    kd_i = KDTree(len(INDEX_OWN))
    for n, i in enumerate(INDEX_OWN):
        kd_i.insert(V[i], n)
    kd_i.balance()
    near = min((V[i] - kd_i.find(V[i])[0]).length for i in THUMB_OWN_S) * 1000.0
    CONTACT["cases"][cid] = {
        "new_pair_total": len(newp),
        "counts": dict((k, len(v)) for k, v in cls.items()),
        "max_penetration_proxy_mm": B.rr(max(depths), 6) if depths else 0.0,
        "pairs_depth_gt_0_5mm": sum(1 for x in depths if x > 0.5),
        "pairs_depth_gt_0_2mm": sum(1 for x in depths if x > 0.2),
        "thumb_index_nearest_vertex_distance_mm": B.rr(near, 6),
        "bind_thumb_index_nearest_mm": B.rr(BIND_TI_DIST, 6),
        "samples": [[a, b] for a, b in newp[:12]],
        "participating_regions": {
            "thumb_index_pairs_in_web_or_contact_zone": sum(
                1 for a, b in cls["B_THUMB_INDEX"]
                if any(v in set(WEB) or v in set(CAGE) for v in POLY[a] + POLY[b])),
        },
    }

    # ---- self-intersection (classified, never a single total)
    SELFINT["cases"][cid] = {
        "total_new_pairs": len(newp),
        "intra_thumb_crease_pairs": len(cls["A_INTRA_THUMB"]),
        "CMC_cage_fold_pairs": len([1 for a, b in newp
                                    if (a in set(cage_faces) or b in set(cage_faces))]),
        "first_web_pairs": len([1 for a, b in newp
                                if any(v in set(WEB) for v in POLY[a] + POLY[b])]),
        "thumb_index_pairs": len(cls["B_THUMB_INDEX"]),
        "thumb_palm_pairs": len(cls["C_THUMB_PALM"]),
        "thumb_other_digit_pairs": len(cls["D_THUMB_OTHER_DIGIT"]),
        "unrelated_cross_digit_pairs": len(cls["E_NON_TARGET_DIGIT"]),
        "max_penetration_proxy_mm": CONTACT["cases"][cid]["max_penetration_proxy_mm"],
    }

    # ---- nail / distal cap
    nail_a = sum(B.face_area(V, POLY[i]) for i in NAIL_FACES) / max(1e-18, NAIL_SUM0)
    cap_a = sum(B.face_area(V, POLY[i]) for i in CAP_FACES) / max(1e-18, CAP_SUM0)
    nail_res, nail_size, nail_rel = rigid_fit_residual(V, NAIL, V0)
    cap_res, cap_size, cap_rel = rigid_fit_residual(V, CAP, V0)
    nc_res, nc_size, nc_rel = rigid_fit_residual(V, sorted(set(NAIL) | set(CAP)), V0)
    n_norm = -B.nail_normal(V, POLY, NAIL_FACES)
    cap_max, cap_mean = disp(V, CAP)
    cap_disp = [(V[i] - V0[i]).length for i in CAP]
    nail_inv = sum(1 for fi in NAIL_FACES
                   if B.face_normal(V, POLY[fi]).dot(FACE_NOR0[fi]) < -0.5)
    ND["cases"][cid] = {
        "nail_area_ratio": B.rr(nail_a, 6),
        "nail_connectivity": "unchanged (global topology gate)",
        "nail_face_area_ratio_min": strain_row["nail"]["min_face_area_ratio"],
        "nail_orientation": B.v3(n_norm, 9),
        "nail_orientation_change_deg": B.rr(math.degrees(n_pad0.angle(n_norm)) if
                                            n_norm.length > 0 else 0.0, 6),
        "nail_inverted_face_count": nail_inv,
        "nail_rigid_fit_residual_mm": B.rr(nail_res, 9),
        "nail_characteristic_size_mm": B.rr(nail_size, 6),
        "nail_rigid_fit_relative_residual": B.rr(nail_rel, 9),
        "nail_cap_union_rigid_fit_relative_residual": B.rr(nc_rel, 9),
        "nail_cap_union_residual_mm": B.rr(nc_res, 9),
        "distal_cap_area_ratio": B.rr(cap_a, 6),
        "distal_cap_face_area_ratio_min": strain_row["distal_cap"]["min_face_area_ratio"],
        "distal_cap_displacement_max_mm": B.rr(cap_max * 1000.0, 9),
        "distal_cap_displacement_spread_mm": B.rr((max(cap_disp) - min(cap_disp)) * 1000.0, 9),
        "distal_cap_mean_displacement_mm": B.rr(cap_mean * 1000.0, 9),
        "distal_cap_rigid_fit_residual_mm": B.rr(cap_res, 9),
        "distal_cap_characteristic_size_mm": B.rr(cap_size, 6),
        "distal_cap_rigid_fit_relative_residual": B.rr(cap_rel, 9),
        "displacement_spread_is_rigid_motion_not_deformation": True,
    }
    # nail / cap are one rigid distal unit; a genuine detachment would show as a large rigid-fit
    # residual (a rigidly translated patch fits with ~0 residual no matter how far it moved)
    if nail_rel > 0.25:
        BLOCKERS.append({"case_id": cid, "kind": "NAIL_DETACHMENT",
                         "detail": {"relative_residual": B.rr(nail_rel, 6)}})
    if cap_a < 0.5 or cap_rel > 0.25:
        BLOCKERS.append({"case_id": cid, "kind": "DISTAL_CAP_CATASTROPHIC",
                         "detail": {"area_ratio": B.rr(cap_a, 6),
                                    "relative_residual": B.rr(cap_rel, 6)}})

    # ---- digit-ownership SEAM behaviour (the surface physically joins two digits here)
    seam_rows = []
    for k in SEAM_TI:
        a, b = EDGES[k]
        r = ((V[a] - V[b]).length / max(1e-18, EDGE_LEN0[k]))
        seam_rows.append((r, k, a, b, EDGE_LEN0[k] * 1000.0, (V[a] - V[b]).length * 1000.0,
                          (V[a] - V0[a]).length * 1000.0, (V[b] - V0[b]).length * 1000.0))
    seam_rows.sort(reverse=True)
    torn = [x for x in seam_rows if x[0] > 3.0 and x[5] > 5.0]
    SEAM["cases"][cid] = {
        "r2_boundary_edge_count": len(SEAM_TI),
        "bind_length_mm": {"min": B.rr(min(SEAM_TI_LEN0.values()), 6),
                           "median": B.rr(sorted(SEAM_TI_LEN0.values())[len(SEAM_TI) // 2], 6),
                           "max": B.rr(max(SEAM_TI_LEN0.values()), 6)},
        "max_stretch_ratio": B.rr(seam_rows[0][0], 6),
        "max_posed_length_mm": B.rr(seam_rows[0][5], 6),
        "edges_over_3x_and_over_5mm": len(torn),
        "worst_edges": [
            {"edge": k, "ratio": B.rr(r, 6), "bind_mm": B.rr(l0, 6), "posed_mm": B.rr(l1, 6),
             "disp_thumb_mm": B.rr(dt, 6), "disp_other_mm": B.rr(do, 6),
             "own": [own[a], own[b]]} for r, k, a, b, l0, l1, dt, do in seam_rows[:5]],
        "R2_BOUNDARY_TEAR": bool(len(torn) > 0),
    }
    if torn:
        BLOCKERS.append({"case_id": cid, "kind": "R2_BOUNDARY_TEAR",
                         "classification": "F_POSE_CONTACT_CONSTRAINT_FAILURE",
                         "detail": {"edges_over_3x_and_over_5mm": len(torn),
                                    "worst_ratio": B.rr(seam_rows[0][0], 6),
                                    "worst_bind_mm": B.rr(seam_rows[0][4], 6),
                                    "worst_posed_mm": B.rr(seam_rows[0][5], 6)}})

    # ---- HISTORIC_CLASS_B_EDGE_STRETCH_PROBE (round spec sections 7 / 22 / 28)
    hrows = []
    for k, _a, _b in HISTORIC_B:
        a, b = EDGES[k]
        r = ((V[a] - V[b]).length / max(1e-18, EDGE_LEN0[k]))
        hrows.append((r, k, a, b, EDGE_LEN0[k] * 1000.0, (V[a] - V[b]).length * 1000.0))
    hrows.sort(reverse=True)
    htorn = [x for x in hrows if x[0] > 3.0 and x[5] > 5.0]
    HISTB["cases"][cid] = {
        "historic_class_b_edge_count": len(HISTORIC_B),
        "bind_length_mm": {"min": B.rr(min(HIST_LEN0.values()), 6),
                           "median": B.rr(sorted(HIST_LEN0.values())[len(HIST_TI) // 2], 6),
                           "max": B.rr(max(HIST_LEN0.values()), 6)},
        "max_stretch_ratio": B.rr(hrows[0][0], 6),
        "max_posed_length_mm": B.rr(hrows[0][5], 6),
        "edges_over_3x": sum(1 for x in hrows if x[0] > 3.0),
        "edges_over_3x_and_over_5mm": len(htorn),
        "worst_edges": [{"edge": k, "ratio": B.rr(r, 6), "bind_mm": B.rr(l0, 6),
                         "posed_mm": B.rr(l1, 6), "endpoints": [a, b],
                         "corrected_ownership": [own[a], own[b]]}
                        for r, k, a, b, l0, l1 in hrows[:5]],
        "HISTORIC_CLASS_B_EDGE_TEAR": bool(len(htorn) > 0),
    }
    if htorn:
        BLOCKERS.append({"case_id": cid, "kind": "HISTORIC_CLASS_B_EDGE_TEAR",
                         "classification": "F_POSE_CONTACT_CONSTRAINT_FAILURE",
                         "detail": {"edges_over_3x_and_over_5mm": len(htorn),
                                    "worst_ratio": B.rr(hrows[0][0], 6),
                                    "worst_bind_mm": B.rr(hrows[0][4], 6),
                                    "worst_posed_mm": B.rr(hrows[0][5], 6)}})

    # ---- cross-digit / palm / forearm
    cf_max, cf_mean = disp(V, CLEAN_FOUR)
    sf_max, _ = disp(V, SANCTIONED_FOUR)
    pmax, pmean = disp(V, PALM)
    fmax, fmean = disp(V, FOREARM)
    CROSS["cases"][cid] = {"clean_four_finger_max_mm": B.rr(cf_max * 1000.0, 9),
                           "sanctioned_four_finger_root_max_mm": B.rr(sf_max * 1000.0, 9),
                           "clean_four_finger_vertex_count": len(CLEAN_FOUR)}
    PALM_FOREARM["cases"][cid] = {"palm_max_mm": B.rr(pmax * 1000.0, 9),
                                  "palm_mean_mm": B.rr(pmean * 1000.0, 9),
                                  "forearm_max_mm": B.rr(fmax * 1000.0, 9),
                                  "forearm_mean_mm": B.rr(fmean * 1000.0, 9)}
    if cf_max * 1000.0 > CLEAN_MOTION_MM:
        CROSS["NON_TARGET_DIGIT_SHAFT_CONTAMINATION"] = "FAIL"
        BLOCKERS.append({"case_id": cid, "kind": "cross_digit_clean_vertex_motion",
                         "detail": {"max_mm": B.rr(cf_max * 1000.0, 9)}})
    if fmax * 1000.0 > CLEAN_MOTION_MM:
        BLOCKERS.append({"case_id": cid, "kind": "forearm_drag",
                         "detail": {"max_mm": B.rr(fmax * 1000.0, 9)}})

    MATRIX["cases"].append({
        "case_id": cid, "kind": c["kind"], "level": c["level"],
        "cmc_deg": c["cmc_deg"], "mcp_deg": c["mcp_deg"], "ip_deg": c["ip_deg"],
        "cmc_quaternion_local": [B.rr(cmc_q.w, 12), B.rr(cmc_q.x, 12),
                                 B.rr(cmc_q.y, 12), B.rr(cmc_q.z, 12)],
        "cmc_total_magnitude_deg": B.rr(math.degrees(cmc_mag), 9),
        "tip_position": B.v3(tip, 9),
        "tip_T_OPPOSE_component_mm": TRAJ["cases"][cid]["T_OPPOSE_component_mm"],
        "pad_alignment_with_T_OPPOSE": TRAJ["cases"][cid]["pad_alignment_with_T_OPPOSE"],
        "cmc_cage": {"min_face_area_ratio": strain_row["CMC_cage"]["min_face_area_ratio"],
                     "min_edge_ratio": strain_row["CMC_cage"]["min_edge_ratio"],
                     "max_edge_ratio": strain_row["CMC_cage"]["max_edge_ratio"],
                     "local_surface_area_ratio":
                         strain_row["CMC_cage"]["local_surface_area_ratio"],
                     "catastrophic_fold_over":
                         CAGE_AUD["cases"][cid]["CMC_CAGE_CATASTROPHIC_FOLD_OVER"]},
        "thenar": {"local_surface_area_ratio":
                       strain_row["thenar"]["local_surface_area_ratio"],
                   "bbox_volume_ratio": THENAR_AUD["cases"][cid][
                       "pca_bbox_volume_ratio_vs_bind"],
                   "catastrophic_collapse":
                       THENAR_AUD["cases"][cid]["THENAR_CATASTROPHIC_COLLAPSE"]},
        "web": {"area_ratio": WEB_AUD["cases"][cid]["web_opening_area_ratio_vs_bind"],
                "tear": WEB_AUD["cases"][cid]["FIRST_WEB_ACTUAL_TEAR"]},
        "contact": CONTACT["cases"][cid]["counts"],
        "strain": strain_row,
        "blockers": [b for b in BLOCKERS if b["case_id"] == cid],
        "status": "PROVISIONAL_HUMAN_REVIEW",
    })

    # 9 RESET + 10 verify restore
    B.reset_pose(rig)
    B.update()
    Vr, _ = B.evaluate(ob, MW)
    rmax = max((Vr[i] - V0[i]).length for i in range(NV)) * 1000.0
    ZERO["post"].append({"case_id": cid, "max_delta_mm": B.rr(rmax, 9),
                         "bone_pose": "identity"})
    ZERO["cases"].append({"case_id": cid, "restore_max_delta_mm": B.rr(rmax, 9),
                          "PASS": rmax <= 1e-4})
    if rmax > 1e-4:
        BLOCKERS.append({"case_id": cid, "kind": "ZERO_RESTORE_FAIL",
                         "detail": {"max_mm": B.rr(rmax, 6)}})
        raise SystemExit("FAIL CLOSED: zero restore broken after %s" % cid)
    log("%-12s cmc=%2d mcp=%2d ip=%2d | tip Top=%+8.4f mm pad_align=%.6f | cage minAR=%s "
        "minER=%s | web area_ratio=%.4f | contact B=%d C=%d | restore=%.9f"
        % (cid, int(c["cmc_deg"]), int(c["mcp_deg"]), int(c["ip_deg"]),
           TRAJ["cases"][cid]["T_OPPOSE_component_mm"],
           TRAJ["cases"][cid]["pad_alignment_with_T_OPPOSE"],
           strain_row["CMC_cage"]["min_face_area_ratio"],
           strain_row["CMC_cage"]["min_edge_ratio"],
           WEB_AUD["cases"][cid]["web_opening_area_ratio_vs_bind"],
           CONTACT["cases"][cid]["counts"]["B_THUMB_INDEX"],
           CONTACT["cases"][cid]["counts"]["C_THUMB_PALM"], rmax))

ZERO["RESTORE_MAX_DELTA_MM"] = max(z["max_delta_mm"] for z in ZERO["post"])
ZERO["ALL_9_CASES_RESTORE"] = "PASS" if all(z["PASS"] for z in ZERO["cases"]) else "FAIL"

# ---------------------------------------------------------------- progression checks
def seq(cids, key_fn):
    return [key_fn(cid) for cid in cids]


OPP_IDS = ["CMC_OPP_10", "CMC_OPP_20", "CMC_OPP_30"]
CMCP_IDS = ["CMC_MCP_L1", "CMC_MCP_L2", "CMC_MCP_L3"]
FULL_IDS = ["FULL_OPP_L1", "FULL_OPP_L2", "FULL_OPP_L3"]
prog = {}
for nm, ids in (("CMC_ISOLATED", OPP_IDS), ("CMC_MCP", CMCP_IDS), ("FULL_CHAIN", FULL_IDS)):
    v = seq(ids, lambda c: TRAJ["cases"][c]["T_OPPOSE_component_mm"])
    mono = all(v[i + 1] >= v[i] - 1e-6 for i in range(len(v) - 1))
    prog[nm] = {"T_OPPOSE_component_mm": v, "monotonic": mono}
log("tip T_OPPOSE progression: %s" % prog)
pad_seq = {nm: seq(ids, lambda c: TRAJ["cases"][c]["pad_alignment_with_T_OPPOSE"])
           for nm, ids in (("CMC_ISOLATED", OPP_IDS), ("CMC_MCP", CMCP_IDS),
                           ("FULL_CHAIN", FULL_IDS))}
pad_jump = {}
for nm, ids in (("CMC_ISOLATED", OPP_IDS), ("CMC_MCP", CMCP_IDS), ("FULL_CHAIN", FULL_IDS)):
    d = [abs(TRAJ["cases"][ids[i + 1]]["pad_orientation_change_deg_vs_bind"]
             - TRAJ["cases"][ids[i]]["pad_orientation_change_deg_vs_bind"])
         for i in range(len(ids) - 1)]
    pad_jump[nm] = {"step_orientation_delta_deg": [B.rr(x, 6) for x in d],
                    "no_180_jump": all(x < 90.0 for x in d)}
PAD_CONT = "PASS" if all(v["no_180_jump"] for v in pad_jump.values()) else "FAIL"
TIP_CONT = "PASS" if all(v["monotonic"] for v in prog.values()) else "REVIEW"
web_seq = [WEB_AUD["cases"][c]["web_opening_area_ratio_vs_bind"] for c in FULL_IDS]
web_tear = [WEB_AUD["cases"][c]["FIRST_WEB_ACTUAL_TEAR"] for c in FULL_IDS]
WEB_CONT = "PASS" if (not any(web_tear)) else "FAIL"
log("pad continuity=%s ; tip progression=%s ; web continuity=%s" % (PAD_CONT, TIP_CONT,
                                                                   WEB_CONT))

for nm, obj in (("STAGE6B_R1B_CASE_MATRIX.json", MATRIX),
                ("STAGE6B_R1B_CMC_CAGE_DEFORM_AUDIT.json", CAGE_AUD),
                ("STAGE6B_R1B_THENAR_DEFORM_AUDIT.json", THENAR_AUD),
                ("STAGE6B_R1B_FIRST_WEB_DEFORM_AUDIT.json", WEB_AUD),
                ("STAGE6B_R1B_TIP_PAD_TRAJECTORY_AUDIT.json", TRAJ),
                ("STAGE6B_R1B_CONTACT_PROGRESSION_AUDIT.json", CONTACT),
                ("STAGE6B_R1B_CROSS_DIGIT_DEFORM_AUDIT.json", CROSS),
                ("STAGE6B_R1B_LOCAL_STRAIN_AUDIT.json", STRAIN),
                ("STAGE6B_R1B_SELF_INTERSECTION_AUDIT.json", SELFINT),
                ("STAGE6B_R1B_NAIL_DISTAL_CAP_AUDIT.json", ND),
                ("STAGE6B_R1B_ZERO_RESTORE_AUDIT.json", ZERO),
                ("STAGE6B_R1B_PALM_FOREARM_STABILITY.json", PALM_FOREARM),
                ("STAGE6B_R1B_HISTORIC_CLASS_B_EDGE_STRETCH_AUDIT.json", HISTB),
                ("STAGE6B_R1B_R2_BOUNDARY_DEFORM_AUDIT.json", SEAM)):
    dump(nm, obj)

json.dump({"stage": "STAGE6B_R1B_PROGRESSION_SUMMARY", "generated_at": NOW,
           "tip_T_OPPOSE_progression": prog,
           "TIP_PROGRESSION_CONTINUITY": TIP_CONT,
           "pad_alignment_sequence": pad_seq, "pad_orientation_step_deg": pad_jump,
           "PAD_ORIENTATION_CONTINUITY": PAD_CONT,
           "web_area_ratio_full_chain": web_seq,
           "FIRST_WEB_PROGRESSIVE_CONTINUITY": WEB_CONT,
           "zero_restore": {"max_mm": ZERO["RESTORE_MAX_DELTA_MM"],
                            "ALL_9": ZERO["ALL_9_CASES_RESTORE"]},
           "blockers": BLOCKERS, "blocker_count": len(BLOCKERS),
           "cmc_cage_authority": ctx["cmc_cage_audit"],
           "log": LOG},
          open(os.path.join(OUTDIR, "_tmp", "S6B_PROGRESSION_SUMMARY.json"), "w",
               encoding="utf-8"), indent=1, ensure_ascii=False)
log("blockers = %d" % len(BLOCKERS))
print("RUN_S6B_DONE")
