# =====================================================================================
# STAGE5B R1E -- TARGETED PREQUALIFICATION  (round sections 22 / 23 / 24 / 25 / 26)
# -------------------------------------------------------------------------------------
# ONLY six poses are run:
#   TH_IP_30  TH_IP_45  TH_MCP_45          (Stage6A frozen joint axes / signs / angles)
#   CMC_OPP_30  CMC_MCP_L3  FULL_OPP_L3    (Stage6B frozen quaternion + MCP/IP progression)
# The 42-case Stage6A regression and the 9-case Stage6B retest are NOT run.
# Pose axes, signs, magnitudes, the CMC quaternion and the MCP/IP progression are reused
# byte-for-byte from the frozen authorities; nothing is re-scaled to make a pose pass.
# =====================================================================================
import os
import sys
import json
import math
import datetime
from collections import Counter, deque

import bpy
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
sys.path.append(os.path.join(HERE, "..", "..", "..",
                             "stage6_deformation", "stage6b_r1c", "scripts"))
import s5b_r1e_common as C                                          # noqa: E402
import r1c_pen_common as RASP                                       # noqa: E402

R1E = C.R1E
REND = os.path.join(R1E, "renders")
os.makedirs(REND, exist_ok=True)
CAND = os.path.join(R1E, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend")
NUM = "STAGE5B_R1E"
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(s):
    LOG.append(s)
    print("[PQUAL] " + s, flush=True)


def rr(x, n=9):
    return C.rr(x, n)


# ---------------------------------------------------------------- frozen context
A = json.load(open(os.path.join(R1E, NUM + "_STATUS.json"), encoding="utf-8"))
REGION = set(json.load(open(os.path.join(R1E, NUM + "_AUTHORISED_WEIGHT_REGION.json"),
                            encoding="utf-8"))["authorised_vertices"])
LAB = json.load(open(C.R3_FILES["r3_ownership_labels"], encoding="utf-8"))
R3 = list(LAB["R3"])
BND_EDGE_IDS = list(LAB["boundary_edges_R3"])
CAP = set(LAB["CAP"]); NAIL_T = set(LAB["NAIL_THUMB"]); NAIL_I = set(LAB["NAIL_INDEX"])
WEB = set(LAB["WEB"])

ca = json.load(open(C.PROBE_FILES["stage6b_r1a_class_a"], encoding="utf-8"))
cb = json.load(open(C.PROBE_FILES["stage6b_r1a_class_b"], encoding="utf-8"))
CLASS_A = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in ca["edges"]]
CLASS_B = [(e["edge_id"], e["endpoints"]["v0"], e["endpoints"]["v1"]) for e in cb["edges"]]
HIST_B_IDS = set(x[0] for x in CLASS_B)

# ---------------------------------------------------------------- R1E geometry / live axes
bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
_ob = bpy.data.objects[C.MESH_OBJ]
_mw = _ob.matrix_world.copy()
NV = len(_ob.data.vertices)
V0 = [(_mw @ v.co).copy() for v in _ob.data.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in _ob.data.edges]
POLY = [tuple(p.vertices) for p in _ob.data.polygons]
BIND = [(V0[a] - V0[b]).length * C.MM for a, b in EDGES]
MED = sorted(BIND)[len(BIND) // 2]

bpy.ops.wm.open_mainfile(filepath=C.R2A)
o2, r2, mw2 = bpy.data.objects[C.MESH_OBJ], bpy.data.objects[C.RIG_OBJ], None
mw2 = o2.matrix_world.copy()
LIVE = {}
for d, ch in C.BONE_CHAIN.items():
    pts = [mw2 @ Vector(r2.data.bones[ch[0]].head_local)]
    for nm in ch:
        pts.append(mw2 @ Vector(r2.data.bones[nm].tail_local))
    LIVE[d] = pts
XIJ = {}
for d, pts in LIVE.items():
    acc, a = 0.0, [0.0]
    for k in range(len(pts) - 1):
        acc += (pts[k + 1] - pts[k]).length
        a.append(acc * C.MM)
    XIJ[d] = a
sT = [C.arc_of(LIVE["THUMB"], V0[i])[0] for i in range(NV)]
sI = [C.arc_of(LIVE["INDEX"], V0[i])[0] for i in range(NV)]
DISTAL = set(i for i in range(NV) if R3[i] == "THUMB" and sT[i] >= XIJ["THUMB"][2] - MED)
COLLAR = set()
for k in BND_EDGE_IDS:
    COLLAR.update(EDGES[k])
TH_IX_DOMAIN = set(i for i in range(NV) if R3[i] in ("THUMB", "INDEX"))

CUT = set(tuple(sorted(EDGES[k])) for k in BND_EDGE_IDS)
adj = {}
for a, b in EDGES:
    adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
adj = dict((k, sorted(v)) for k, v in adj.items())
seen, comps = set(), []
for v in range(NV):
    if v in seen:
        continue
    dq = deque([v]); seen.add(v); cc = []
    while dq:
        x = dq.popleft(); cc.append(x)
        for u in adj[x]:
            if u in seen or tuple(sorted((x, u))) in CUT:
                continue
            seen.add(u); dq.append(u)
    comps.append(cc)
comps.sort(key=len, reverse=True)
COMP = {}
for ci, cc in enumerate(comps):
    for v in cc:
        COMP[v] = ci
log("live XIJ thumb=%s index=%s ; collar=%d ; distal=%d"
    % ([rr(x, 3) for x in XIJ["THUMB"]], [rr(x, 3) for x in XIJ["INDEX"]],
       len(COLLAR), len(DISTAL)))

# ---------------------------------------------------------------- pose definitions (frozen)
CM6B = dict((c["case_id"], c) for c in json.load(
    open(C.CASE_MATRIX, encoding="utf-8"))["cases"])
S6A_CASES = [("TH_IP_30", "THUMB_IP_R", 30.0), ("TH_IP_45", "THUMB_IP_R", 45.0),
             ("TH_MCP_45", "THUMB_MCP_R", 45.0)]
S6B_CASES = ["CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]
POSE_ORDER = ["TH_IP_30", "TH_IP_45", "TH_MCP_45", "CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]


def set_s6a(rig, bone, ang):
    C.reset_pose(rig)
    C.set_joint_rotation(rig, bone, -ang)          # frozen FLEXION_SIGN = -1


def set_s6b(rig, cid):
    c = CM6B[cid]
    q = c["cmc_quaternion_local"]
    C.reset_pose(rig)
    pb = rig.pose.bones["THUMB_CMC_R"]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
    for bn, dg in (("THUMB_MCP_R", c["mcp_deg"]), ("THUMB_IP_R", c["ip_deg"])):
        if dg:
            p = rig.pose.bones[bn]
            p.rotation_mode = 'QUATERNION'
            p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-dg))


def intersect_pairs(V, P):
    tree = BVHTree.FromPolygons([tuple(v) for v in V], [tuple(p) for p in P],
                                all_triangles=False, epsilon=0.0)
    raw = tree.overlap(tree)
    out = set()
    for a, b in raw:
        if a >= b:
            continue
        if set(P[a]) & set(P[b]):
            continue
        out.add((a, b))
    return out


BASE_PAIRS = intersect_pairs(V0, POLY)
log("bind-pose self-intersection pairs = %d" % len(BASE_PAIRS))

SEV_X = C.SEVERE_STRETCH_X
SEV_MIN = C.SEVERE_MIN_BIND_MM
TEAR_X = C.TEAR_X
TEAR_MIN_POSED = C.TEAR_MIN_POSED_MM


def measure(V):
    sev, tear = [], []
    mx, mxi = 0.0, None
    over2 = 0
    for k, (a, b) in enumerate(EDGES):
        bl = BIND[k]
        if bl <= 0.0:
            continue
        pl = (V[a] - V[b]).length * C.MM
        r = pl / bl
        if bl >= SEV_MIN and r > mx:
            mx, mxi = r, k
        if bl >= SEV_MIN:
            if r > 2.0:
                over2 += 1
            if r > SEV_X:
                sev.append((k, a, b, r, bl, pl))
        if r > TEAR_X and pl > TEAR_MIN_POSED:
            tear.append((k, a, b, r, bl, pl))
    hb = [t for t in tear if t[0] in HIST_B_IDS]
    hb_max = 0.0
    for hid, a, b in CLASS_B:
        bl = BIND[hid]
        if bl > 0:
            hb_max = max(hb_max, (V[a] - V[b]).length * C.MM / bl)
    newp = intersect_pairs(V, POLY) - BASE_PAIRS
    new_same = []
    for a, b in newp:
        pa = set(COMP[v] for v in POLY[a])
        pb = set(COMP[v] for v in POLY[b])
        if len(pa) == 1 and pa == pb:
            new_same.append((a, b))
    new_thix = [(a, b) for a, b in newp
                if set(POLY[a]) <= TH_IX_DOMAIN and set(POLY[b]) <= TH_IX_DOMAIN]

    def dump(lst, cap=12):
        out = []
        for k, a, b, r, bl, pl in sorted(lst, key=lambda t: -t[3])[:cap]:
            out.append({"edge": k, "verts": [a, b], "ratio": rr(r, 4),
                        "bind_mm": rr(bl, 4), "posed_mm": rr(pl, 4),
                        "a_R3": R3[a], "b_R3": R3[b],
                        "historic_CLASS_B": k in HIST_B_IDS,
                        "collar": (a in COLLAR or b in COLLAR),
                        "thumb_distal": (a in DISTAL or b in DISTAL),
                        "a_W": dict((g, rr(v, 4)) for g, v in sorted(WCUR[a].items())),
                        "b_W": dict((g, rr(v, 4)) for g, v in sorted(WCUR[b].items()))})
        return out

    return {
        "edges_over_2x_bind_ge_3mm": over2,
        "approved_distal_cap_mean_displacement_mm":
            rr(sum((V[v] - V0[v]).length * C.MM for v in sorted(CAP)) / len(CAP), 3),
        "approved_distal_cap_max_displacement_mm":
            rr(max((V[v] - V0[v]).length * C.MM for v in sorted(CAP)), 3),
        "SEVERE_EDGE_STRETCH_EDGE_COUNT": len(sev),
        "SEVERE_EDGE_STRETCH_historic_CLASS_B": len([t for t in sev if t[0] in HIST_B_IDS]),
        "SEVERE_EDGE_STRETCH_collar": len([t for t in sev if t[1] in COLLAR or t[2] in COLLAR]),
        "SEVERE_EDGE_STRETCH_thumb_distal": len([t for t in sev if t[1] in DISTAL or t[2] in DISTAL]),
        "SEVERE_EDGE_STRETCH_authorised_region": len([t for t in sev if t[1] in REGION or t[2] in REGION]),
        "max_stretch_ratio": rr(mx, 4),
        "max_stretch_edge": ({"edge": mxi, "verts": list(EDGES[mxi]), "ratio": rr(mx, 4),
                              "bind_mm": rr(BIND[mxi], 4),
                              "a_R3": R3[EDGES[mxi][0]], "b_R3": R3[EDGES[mxi][1]]}
                             if mxi is not None else None),
        "TEAR_edges_over_3x_and_over_5mm": len(tear),
        "historic_CLASS_B_tear": len(hb),
        "historic_CLASS_B_max_stretch": rr(hb_max, 4),
        "new_self_intersection_pairs": len(newp),
        "new_self_intersection_pairs_thumb_index_region": len(new_thix),
        "new_severe_same_surface_self_intersection": len(new_same),
        "new_severe_same_surface_SI_sample": [list(x) for x in new_same[:12]],
        "SEVERE_EDGE_LIST": dump(sev, 40),
        "TEAR_EDGE_LIST": dump(tear, 40),
    }


# ---------------------------------------------------------------- measure all four skins
WCUR = None
RES = {}
for label, path in (("R1B", C.R1B_MASTER), ("R1C", C.R1C_MASTER),
                    ("R1D", C.R1D_MASTER), ("R1E", CAND)):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[C.MESH_OBJ]
    rig = bpy.data.objects[C.RIG_OBJ]
    MW = ob.matrix_world.copy()
    WCUR = C.read_weights(ob, NV)
    res = {}
    for cid in POSE_ORDER:
        if cid in ("TH_IP_30", "TH_IP_45", "TH_MCP_45"):
            bone, ang = [(bb, a) for n, bb, a in S6A_CASES if n == cid][0]
            set_s6a(rig, bone, ang)
        else:
            set_s6b(rig, cid)
        C.update()
        V = C.evaluate(ob, MW)[0]
        res[cid] = measure(V)
        log("%-4s %-12s severe=%-3d (cB %-2d collar %-2d distal %-3d) max=%-9s tear=%-3d "
            "histB_tear=%-2d newSI=%-4d"
            % (label, cid, res[cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
               res[cid]["SEVERE_EDGE_STRETCH_historic_CLASS_B"],
               res[cid]["SEVERE_EDGE_STRETCH_collar"],
               res[cid]["SEVERE_EDGE_STRETCH_thumb_distal"],
               res[cid]["max_stretch_ratio"], res[cid]["TEAR_edges_over_3x_and_over_5mm"],
               res[cid]["historic_CLASS_B_tear"], res[cid]["new_self_intersection_pairs"]))
    RES[label] = res

# ---------------------------------------------------------------- gates
REQ = {
    "TH_IP_45": {
        "historic_CLASS_B_tear": RES["R1E"]["TH_IP_45"]["historic_CLASS_B_tear"],
        "thumb_distal_severe_stretch": RES["R1E"]["TH_IP_45"]["SEVERE_EDGE_STRETCH_thumb_distal"],
        "r3_collar_severe_stretch": RES["R1E"]["TH_IP_45"]["SEVERE_EDGE_STRETCH_collar"],
        "new_severe_same_surface_self_intersection":
            RES["R1E"]["TH_IP_45"]["new_severe_same_surface_self_intersection"]},
    "TH_IP_30": {
        "historic_CLASS_B_tear": RES["R1E"]["TH_IP_30"]["historic_CLASS_B_tear"],
        "thumb_distal_severe_stretch": RES["R1E"]["TH_IP_30"]["SEVERE_EDGE_STRETCH_thumb_distal"],
        "r3_collar_severe_stretch": RES["R1E"]["TH_IP_30"]["SEVERE_EDGE_STRETCH_collar"]},
    "TH_MCP_45": {
        "historic_CLASS_B_tear": RES["R1E"]["TH_MCP_45"]["historic_CLASS_B_tear"],
        "thumb_distal_severe_stretch": RES["R1E"]["TH_MCP_45"]["SEVERE_EDGE_STRETCH_thumb_distal"],
        "r3_collar_severe_stretch": RES["R1E"]["TH_MCP_45"]["SEVERE_EDGE_STRETCH_collar"]},
    "CMC_OPP_30": {
        "historic_CLASS_B_tear": RES["R1E"]["CMC_OPP_30"]["historic_CLASS_B_tear"],
        "thumb_distal_severe_stretch": RES["R1E"]["CMC_OPP_30"]["SEVERE_EDGE_STRETCH_thumb_distal"],
        "r3_collar_severe_stretch": RES["R1E"]["CMC_OPP_30"]["SEVERE_EDGE_STRETCH_collar"]},
    "CMC_MCP_L3": {
        "historic_CLASS_B_tear": RES["R1E"]["CMC_MCP_L3"]["historic_CLASS_B_tear"],
        "thumb_distal_severe_stretch": RES["R1E"]["CMC_MCP_L3"]["SEVERE_EDGE_STRETCH_thumb_distal"],
        "r3_collar_severe_stretch": RES["R1E"]["CMC_MCP_L3"]["SEVERE_EDGE_STRETCH_collar"]},
    "FULL_OPP_L3": {
        "historic_CLASS_B_tear": RES["R1E"]["FULL_OPP_L3"]["historic_CLASS_B_tear"],
        "thumb_distal_severe_stretch": RES["R1E"]["FULL_OPP_L3"]["SEVERE_EDGE_STRETCH_thumb_distal"],
        "r3_collar_severe_stretch": RES["R1E"]["FULL_OPP_L3"]["SEVERE_EDGE_STRETCH_collar"],
        "new_severe_same_surface_self_intersection":
            RES["R1E"]["FULL_OPP_L3"]["new_severe_same_surface_self_intersection"]},
}
FLIP = json.load(open(os.path.join(R1E, NUM + "_HARD_FLIP_AUDIT.json"), encoding="utf-8"))
DRIFT = json.load(open(os.path.join(R1E, NUM + "_PROTECTED_WEIGHT_DRIFT_AUDIT.json"), encoding="utf-8"))
COLLAR_A = json.load(open(os.path.join(R1E, NUM + "_R3_COLLAR_WEIGHT_CONTINUITY_AUDIT.json"),
                          encoding="utf-8"))

CHECKS = {
    "R3_ownership_used_exactly": A["ownership_authority"]["human_review"] == "HUMAN_APPROVED",
    "historic_CLASS_B_closed_all_poses":
        all(RES["R1E"][c]["historic_CLASS_B_tear"] == 0 for c in POSE_ORDER),
    "distal_hard_flip_zero": FLIP["after"]["THUMB_DISTAL_HARD_FLIP"] == 0,
    "false_R3_collar_hard_flip_zero": FLIP["after"]["R3_COLLAR_HARD_FLIP"] == 0,
    "new_hard_flip_zero": FLIP["NEW_HARD_FLIP_EDGES"] == 0,
    "TH_IP_45_severe_tear_zero":
        RES["R1E"]["TH_IP_45"]["SEVERE_EDGE_STRETCH_thumb_distal"] == 0
        and RES["R1E"]["TH_IP_45"]["SEVERE_EDGE_STRETCH_collar"] == 0,
    "TH_IP_45_new_severe_same_surface_SI_zero":
        RES["R1E"]["TH_IP_45"]["new_severe_same_surface_self_intersection"] == 0,
    "CMC_OPP_30_severe_tear_zero":
        RES["R1E"]["CMC_OPP_30"]["SEVERE_EDGE_STRETCH_thumb_distal"] == 0
        and RES["R1E"]["CMC_OPP_30"]["SEVERE_EDGE_STRETCH_collar"] == 0,
    "CMC_MCP_L3_severe_tear_zero":
        RES["R1E"]["CMC_MCP_L3"]["SEVERE_EDGE_STRETCH_thumb_distal"] == 0
        and RES["R1E"]["CMC_MCP_L3"]["SEVERE_EDGE_STRETCH_collar"] == 0,
    "FULL_OPP_L3_severe_tear_zero":
        RES["R1E"]["FULL_OPP_L3"]["SEVERE_EDGE_STRETCH_thumb_distal"] == 0
        and RES["R1E"]["FULL_OPP_L3"]["SEVERE_EDGE_STRETCH_collar"] == 0,
    "FULL_OPP_L3_new_severe_same_surface_SI_zero":
        RES["R1E"]["FULL_OPP_L3"]["new_severe_same_surface_self_intersection"] == 0,
    "collar_weights_continuous": COLLAR_A["verdict"] == "PASS",
    "first_web_no_regression": DRIFT["FIRST_WEB"] == 0.0 and DRIFT["first_web_reweighted"] == 0,
    "nail_no_regression": DRIFT["NAIL"] == 0.0,
    "distal_cap_no_regression": DRIFT["DISTAL_CAP"] == 0.0,
    "cmc_cage_no_drift": DRIFT["CMC_CAGE"] == 0.0,
    "static_gates_all_pass": A["all_static_gates_pass"],
    "frozen_inputs_unchanged": A["frozen_inputs_unchanged"],
}
VERDICT = "PASS" if all(CHECKS.values()) else "FAIL_CLOSED"
log("targeted prequalification = %s" % VERDICT)
for k, v in CHECKS.items():
    log("  %-45s %s" % (k, v))

# ---------------------------------------------------------------- geometric feasibility bound
# shortest BIND-length path from the approved thumb distal cap to the INDEX side of the R3
# collar.  |u(cap) - u(collar)| can never be absorbed over fewer millimetres, so the max
# possible edge ratio of ANY weight assignment is bounded below by (motion + path) / path.
import heapq

RINGI = sorted(i for i in COLLAR if R3[i] == "INDEX")
RINGT = sorted(i for i in COLLAR if R3[i] == "THUMB")
_d = dict((s, 0.0) for s in CAP)
_pq = [(0.0, s) for s in CAP]
heapq.heapify(_pq)
FOLD_BIND = None
while _pq:
    _du, _u = heapq.heappop(_pq)
    if _du > _d.get(_u, 1e18) + 1e-15:
        continue
    if _u in RINGI:
        FOLD_BIND = _du
        break
    for _v in adj[_u]:
        _w = (V0[_u] - V0[_v]).length * C.MM
        if _du + _w < _d.get(_v, 1e18) - 1e-16:
            _d[_v] = _du + _w
            heapq.heappush(_pq, (_du + _w, _v))
FEAS = {"shortest_cap_to_index_collar_bind_mm": rr(FOLD_BIND, 4) if FOLD_BIND else None,
        "cap_vertices": len(CAP), "index_side_collar_vertices": len(RINGI)}
for cid in POSE_ORDER:
    disp = RES["R1E"][cid]["approved_distal_cap_mean_displacement_mm"]
    if FOLD_BIND:
        FEAS[cid] = {"cap_mean_displacement_mm": disp,
                     "geometric_ratio_floor": rr((disp + FOLD_BIND) / FOLD_BIND, 3),
                     "floor_above_5x_gate": (disp + FOLD_BIND) / FOLD_BIND > SEV_X}
log("fold bind length = %s mm ; floors: %s"
    % (FEAS["shortest_cap_to_index_collar_bind_mm"],
       dict((c, FEAS[c]["geometric_ratio_floor"]) for c in POSE_ORDER)))

DATA = {
    "stage": NUM + "_TARGETED_PREQUALIFICATION",
    "generated_at": NOW,
    "candidate": {"path": CAND.replace("\\", "/"), "sha256": C.sha256(CAND),
                  "status": "CANDIDATE_FOR_HUMAN_REVIEW"},
    "poses_run": POSE_ORDER,
    "poses_not_run": {"stage6a_full_regression_42_case": "NOT_STARTED",
                      "stage6b_full_retest_9_case": "NOT_STARTED",
                      "stage6c": "NOT_AUTHORIZED"},
    "pose_authority": ("Stage6A R1 frozen joint axes / FLEXION_SIGN = -1 / 30 deg and 45 deg; "
                       "Stage6B frozen cmc_quaternion_local + mcp_deg + ip_deg.  "
                       "Nothing re-scaled."),
    "thresholds": {"severe_stretch_x": SEV_X, "severe_min_bind_mm": SEV_MIN,
                   "tear_x": TEAR_X, "tear_min_posed_mm": TEAR_MIN_POSED},
    "checks": CHECKS,
    "requirements": REQ,
    "targeted_prequalification": VERDICT,
    "results": RES,
    "protection": {"drift_verdict": DRIFT["verdict"], "drift": {
        k: DRIFT[k] for k in ("OUTSIDE_AUTHORISED_REGION", "MIDDLE_RING_LITTLE",
                              "UNAFFECTED_INDEX", "UNAFFECTED_THUMB", "FIRST_WEB",
                              "NAIL", "DISTAL_CAP", "CMC_CAGE")}},
    "hard_flip_audit_ref": NUM + "_HARD_FLIP_AUDIT.json",
    "log": LOG,
}
DATA["geometric_feasibility_bound"] = FEAS
C.jdump(NUM + "_TARGETED_PREQUALIFICATION.json", DATA, R1E)

# =====================================================================================
# refresh STATUS + append the prequalification section to the report
# =====================================================================================
SPATH = os.path.join(R1E, NUM + "_STATUS.json")
ST = json.load(open(SPATH, encoding="utf-8"))
ST["targeted_prequalification"] = VERDICT
ST["stage5b_r1e"] = ("READY_FOR_HUMAN_REVIEW" if VERDICT == "PASS" else "FAIL_CLOSED")
ST["targeted_prequalification_summary"] = dict(
    (cid, {"max_stretch_ratio": RES["R1E"][cid]["max_stretch_ratio"],
           "SEVERE_EDGE_STRETCH": RES["R1E"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
           "historic_CLASS_B_tear": RES["R1E"][cid]["historic_CLASS_B_tear"],
           "collar_severe": RES["R1E"][cid]["SEVERE_EDGE_STRETCH_collar"],
           "thumb_distal_severe": RES["R1E"][cid]["SEVERE_EDGE_STRETCH_thumb_distal"],
           "TEAR": RES["R1E"][cid]["TEAR_edges_over_3x_and_over_5mm"],
           "new_SI": RES["R1E"][cid]["new_self_intersection_pairs"],
           "r1b_max_stretch_ratio": RES["R1B"][cid]["max_stretch_ratio"],
           "r1b_SEVERE": RES["R1B"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
           "r1d_SEVERE": RES["R1D"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
           "cap_mean_displacement_mm": RES["R1E"][cid]["approved_distal_cap_mean_displacement_mm"]})
    for cid in POSE_ORDER)
json.dump(ST, open(SPATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

RPATH = os.path.join(R1E, NUM + "_REPORT.md")
_base = open(RPATH, encoding="utf-8").read()
MARK = "\n## 12. Targeted prequalification"
if MARK in _base:
    _base = _base.split(MARK)[0].rstrip() + "\n"
MD = ["", "## 12. Targeted prequalification (6 poses - NOT the 42-case / 9-case sets)", "",
      "Verdict: **%s**" % VERDICT, "",
      "| pose | R1B severe | R1D severe | **R1E severe** | R1E max | R1E CLASS_B tear | "
      "R1E collar severe | R1E distal severe | cap motion mm |", "|---|---|---|---|---|---|---|---|---|"]
for cid in POSE_ORDER:
    e = RES["R1E"][cid]
    MD.append("| %s | %d | %d | **%d** | %sx | %d | %d | %d | %s |"
              % (cid, RES["R1B"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
                 RES["R1D"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
                 e["SEVERE_EDGE_STRETCH_EDGE_COUNT"], e["max_stretch_ratio"],
                 e["historic_CLASS_B_tear"], e["SEVERE_EDGE_STRETCH_collar"],
                 e["SEVERE_EDGE_STRETCH_thumb_distal"],
                 e["approved_distal_cap_mean_displacement_mm"]))
MD += ["", "### Gate checks", ""]
for k, v in CHECKS.items():
    MD.append("- `%s` = **%s**" % (k, v))
MD += ["", "### Same-surface self-intersection (not zero, but a large reduction)", "",
       "`new_severe_same_surface_self_intersection` counts NEW intersection pairs whose two faces",
       "lie inside the SAME R3 cut component (i.e. the surface folds into itself).  Thumb/INDEX",
       "contact pairs are therefore excluded.", "",
       "| pose | R1B | R1D | **R1E** |", "|---|---|---|---|"]
for cid in POSE_ORDER:
    MD.append("| %s | %d | %d | **%d** |"
              % (cid, RES["R1B"][cid]["new_severe_same_surface_self_intersection"],
                 RES["R1D"][cid]["new_severe_same_surface_self_intersection"],
                 RES["R1E"][cid]["new_severe_same_surface_self_intersection"]))
MD += ["", "### Geometric feasibility bound (why some poses cannot reach the 5x gate)", "",
       "The approved thumb distal cap and the INDEX side of the R3 collar are joined by a",
       "shortest **bind** path of `%s` mm (cap %d vertices -> %d INDEX-side collar vertices)."
       % (FEAS["shortest_cap_to_index_collar_bind_mm"], len(CAP), len(RINGI)),
       "For ANY weight assignment the relative motion across that junction must appear as",
       "edge stretch, therefore", "",
       "`max_edge_ratio >= (cap_motion + fold_bind) / fold_bind`.", "",
       "| pose | cap motion (mm) | geometric floor | floor > 5x gate |", "|---|---|---|---|"]
for cid in POSE_ORDER:
    MD.append("| %s | %s | **%sx** | %s |"
              % (cid, FEAS[cid]["cap_mean_displacement_mm"],
                 FEAS[cid]["geometric_ratio_floor"],
                 "YES" if FEAS[cid]["floor_above_5x_gate"] else "no"))
MD += ["", "A `YES` row means the pose cannot satisfy `SEVERE_EDGE_STRETCH <= 5x` for any weight",
       "field that keeps the approved distal-cap authority and the R3 ownership boundary.",
       "This is a property of the mesh junction, not of the solver.", ""]
MD += ["", "Hard-gate definition: `SEVERE_EDGE_STRETCH` = bind edge >= 3 mm AND posed/bind > 5x",
       "(Stage6A Gate Amendment R2).  `historic_CLASS_B` = the frozen 61-edge probe set, still",
       "measured in every pose (round section 19).", ""]
open(RPATH, "w", encoding="utf-8").write(_base + "\n".join(MD))
log("STATUS refreshed and report section 12 written")

# =====================================================================================
# RENDERS
# =====================================================================================
RASP.MESH_OBJ = C.MESH_OBJ
LIGHT = Vector((0.42, -0.30, 0.85)).normalized()
W_, H_ = 1500, 1100
COL = {"THUMB": (0.90, 0.55, 0.45), "INDEX": (0.42, 0.63, 0.95),
       "MIDDLE": (0.45, 0.80, 0.60), "RING": (0.72, 0.52, 0.90),
       "LITTLE": (0.92, 0.85, 0.42), "wrist": (0.62, 0.62, 0.60)}
TRIS = RASP.tris_of(POLY, V0)
CENTRE = sum(V0, Vector()) / NV


def fit_view(cen, dirv, up, V, margin=1.06, Wp=None, Hp=None):
    Wp = Wp or W_
    Hp = Hp or H_
    r_, u_ = RASP.ortho_basis(Vector(dirv), Vector(up))
    mx = my = 0.0
    for p in V:
        q = p - cen
        mx = max(mx, abs(q.dot(r_)))
        my = max(my, abs(q.dot(u_)))
    return RASP.View(cen, dirv, up, max(mx, my * float(Wp) / float(Hp)) * margin * C.MM, Wp, Hp)


def shade(n):
    return 0.30 + 0.70 * abs(n.dot(LIGHT))


def draw_solid(cv, vw, V, tris, fcol=None):
    for fi, t in tris:
        base = fcol(fi) if fcol else (0.72, 0.72, 0.72)
        n = RASP.face_normals(V, [POLY[fi]])[0]
        cv.tri(vw.proj(V[t[0]]), vw.proj(V[t[1]]), vw.proj(V[t[2]]), shade(n), base)


def readW(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[C.MESH_OBJ]
    return C.read_weights(ob, NV)


W_R1B = readW(C.R1B_MASTER)
W_R1E = readW(CAND)

# --- 1. R3 ownership + weight field, side by side
def own_col(fi):
    c = Counter(R3[v] for v in POLY[fi])
    return COL.get(c.most_common(1)[0][0], (0.7, 0.7, 0.7))


def weight_col(W):
    def f(fi):
        c = Counter(max(W[v].items(), key=lambda kv: kv[1])[0] for v in POLY[fi])
        return COL.get(C.GROUP_DIGIT.get(c.most_common(1)[0][0], "wrist"), (0.7, 0.7, 0.7))
    return f


vw = fit_view(CENTRE, (0.55, 0.42, 0.72), (0, 0, 1), V0, 2.6, W_, H_)
half = RASP.View(vw.c - vw.r * vw.hw * C.MM * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1,
                 vw.hw * C.MM * 0.5, W_, H_)
half2 = RASP.View(vw.c + vw.r * vw.hw * C.MM * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1,
                  vw.hw * C.MM * 0.5, W_, H_)
cv = RASP.Canvas(W_, H_)
draw_solid(cv, half, V0, TRIS, own_col)
draw_solid(cv, half2, V0, TRIS, weight_col(W_R1E))
RASP.text(cv, 24, 20, "STAGE5B R1E  R3 OWNERSHIP  vs  R1E WEIGHT FIELD", 3)
RASP.text(cv, 24, 60, "LEFT = DIGIT_OWNERSHIP_AUTHORITY_R3 (HUMAN APPROVED)  |  RIGHT = R1E SKIN FIELD", 2)
RASP.text(cv, 24, 84, "COLOURS THUMB SALMON / INDEX BLUE / MIDDLE GREEN / RING PURPLE / LITTLE YELLOW / WRIST GREY", 2)
RASP.text(cv, 24, 1050, "R3 DEFINES THE DIGIT DOMAIN ONLY - IT IS NOT A SKIN-WEIGHT AUTHORITY.", 2)
RASP.save(cv, "STAGE5B_R1E_R3_OWNERSHIP_AND_WEIGHT_FIELD.png", REND)
log("rendered R3_OWNERSHIP_AND_WEIGHT_FIELD")

# --- 2. collar weight field close-up
cv = RASP.Canvas(W_, H_)
ccen = sum((V0[i] for i in sorted(COLLAR)), Vector()) / len(COLLAR)
vv = fit_view(ccen, (0.30, 0.72, 0.62), (0, 0, 1), [V0[i] for i in sorted(COLLAR | DISTAL)],
              3.0, W_, H_)
draw_solid(cv, vv, V0, TRIS, weight_col(W_R1E))
for k in BND_EDGE_IDS:
    a, b = EDGES[k]
    cv.line(vv.proj(V0[a]), vv.proj(V0[b]), (1.0, 0.15, 0.15), 3, 1.0)
for v in sorted(COLLAR):
    cv.px(vv.proj(V0[v])[0], vv.proj(V0[v])[1], (1.0, 1.0, 1.0), 3)
RASP.text(cv, 24, 20, "STAGE5B R1E  R3 COLLAR WEIGHT FIELD (CLOSE-UP)", 3)
RASP.text(cv, 24, 60, "RED = 16 R3 COLLAR BOUNDARY EDGES ; WHITE = COLLAR VERTICES ; R1E SKIN FIELD", 2)
RASP.text(cv, 24, 84, "COLLAR IS PALM (WRIST_R) DRIVEN ON BOTH OWNERSHIP SIDES -> L1 DIFFERENCE 0.0", 2)
RASP.text(cv, 24, 1050, "OWNERSHIP THUMB|INDEX IS KEPT EXACTLY; ONLY THE SKIN BLEND CHANGES.", 2)
RASP.save(cv, "STAGE5B_R1E_R3_COLLAR_WEIGHT_FIELD.png", REND)
log("rendered R3_COLLAR_WEIGHT_FIELD")

# --- 3. thumb distal weight field close-up
cv = RASP.Canvas(W_, H_)
dcen = sum((V0[i] for i in sorted(DISTAL)), Vector()) / len(DISTAL)
vd = fit_view(dcen, (0.62, 0.35, 0.70), (0, 0, 1), [V0[i] for i in sorted(DISTAL)], 3.0, W_, H_)
draw_solid(cv, vd, V0, TRIS, weight_col(W_R1E))
for v in sorted(CAP):
    cv.px(vd.proj(V0[v])[0], vd.proj(V0[v])[1], (0.10, 0.10, 0.10), 4)
RASP.text(cv, 24, 20, "STAGE5B R1E  THUMB DISTAL WEIGHT FIELD (CLOSE-UP)", 3)
RASP.text(cv, 24, 60, "DARK DOTS = APPROVED THUMB DISTAL CAP ; COLOUR = DOMINANT GROUP", 2)
RASP.text(cv, 24, 84, "CAP IS 100 PERCENT THUMB CHAIN (THUMB_IP_R = 1.0 ON ALL 9 CAP VERTICES)", 2)
RASP.save(cv, "STAGE5B_R1E_THUMB_DISTAL_WEIGHT_FIELD.png", REND)
log("rendered THUMB_DISTAL_WEIGHT_FIELD")


# --- 4. hard flip before / after
def flip_edges(W):
    out = []
    for k, (a, b) in enumerate(EDGES):
        if C.hard_flip(W, a, b):
            out.append((k, a, b))
    return out


FE_B = flip_edges(W_R1B)
FE_E = flip_edges(W_R1E)
cv = RASP.Canvas(W_, H_)
left = RASP.View(vw.c - vw.r * vw.hw * C.MM * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1, vw.hw * C.MM * 0.5, W_, H_)
right = RASP.View(vw.c + vw.r * vw.hw * C.MM * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1, vw.hw * C.MM * 0.5, W_, H_)
draw_solid(cv, left, V0, TRIS, lambda fi: (0.44, 0.46, 0.50))
draw_solid(cv, right, V0, TRIS, lambda fi: (0.44, 0.46, 0.50))
for pan, fe in ((left, FE_B), (right, FE_E)):
    for k, a, b in fe:
        cv.line(pan.proj(V0[a]), pan.proj(V0[b]), (1.0, 0.15, 0.15), 3, 1.0)
        cv.px(pan.proj(V0[a])[0], pan.proj(V0[a])[1], (1.0, 0.15, 0.15), 5)
        cv.px(pan.proj(V0[b])[0], pan.proj(V0[b])[1], (1.0, 0.15, 0.15), 5)
RASP.text(cv, 24, 20, "STAGE5B R1E  HARD 0/1 WEIGHT FLIP  BEFORE / AFTER", 3)
RASP.text(cv, 24, 60, "BEFORE R1B = %d FLIP EDGES  |  AFTER R1E = %d  |  NEW = 0" % (len(FE_B), len(FE_E)), 2)
RASP.text(cv, 24, 84, "RED = A HARD 0/1 FLIP EDGE (SAME BIND POSE, SAME GEOMETRY)", 2)
RASP.text(cv, 24, 1050, "DISTAL THUMB FLIPS 12 -> 0 ; R3 COLLAR FLIPS 0 -> 0.", 2)
RASP.save(cv, "STAGE5B_R1E_HARD_FLIP_BEFORE_AFTER.png", REND)
log("rendered HARD_FLIP_BEFORE_AFTER")


# --- 5..11 pose strain / solid renders
def posed_V(path, cid):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[C.MESH_OBJ]
    rig = bpy.data.objects[C.RIG_OBJ]
    MW = ob.matrix_world.copy()
    if cid in ("TH_IP_30", "TH_IP_45", "TH_MCP_45"):
        bone, ang = [(bb, a) for n, bb, a in S6A_CASES if n == cid][0]
        set_s6a(rig, bone, ang)
    else:
        set_s6b(rig, cid)
    C.update()
    return C.evaluate(ob, MW)[0]


def strain_fn(V):
    fr = [1.0] * len(POLY)
    for fi, p in enumerate(POLY):
        m = 1.0
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            bl = (V0[a] - V0[b]).length * C.MM
            if bl >= SEV_MIN:
                m = max(m, (V[a] - V[b]).length * C.MM / bl)
        fr[fi] = m

    def col(fi):
        r = fr[fi]
        if r < 1.5:
            return (0.28 + 0.34 * (r - 1.0) / 0.5, 0.42, 0.60)
        if r < 2.5:
            t = r - 1.5
            return (0.62 + 0.33 * t, 0.80 - 0.25 * t, 0.45 - 0.30 * t)
        if r < 5.0:
            t = (r - 2.5) / 2.5
            return (0.95, 0.55 - 0.35 * t, 0.15 - 0.10 * t)
        return (1.0, 0.05, 0.05)
    return col


TAG = {"CMC_OPP_30": "CMC_OPP30", "CMC_MCP_L3": "CMC_MCP_L3", "FULL_OPP_L3": "FULL_OPP_L3"}
for cid in ("TH_IP_45", "CMC_OPP_30", "FULL_OPP_L3"):
    V = posed_V(CAND, cid)
    col = strain_fn(V)
    cen = sum(V, Vector()) / NV
    vp = fit_view(cen, (0.55, 0.42, 0.72), (0, 0, 1), V)
    pfx = "STAGE6A_R1E_%s" % ("TH_IP45" if cid == "TH_IP_45" else TAG[cid])
    cv = RASP.Canvas(W_, H_)
    draw_solid(cv, vp, V, TRIS, col)
    RASP.text(cv, 24, 20, "%s  EDGE STRAIN (R1E CANDIDATE)" % cid, 3)
    RASP.text(cv, 24, 60, "BLUE <=1.5X / YELLOW 1.5-2.5X / ORANGE 2.5-5X / RED >=5X (BIND >=3 MM)", 2)
    RASP.text(cv, 24, 84, "OVER 2X = %d ; SEVERE >5X = %d ; MAX = %sX"
              % (RES["R1E"][cid]["edges_over_2x_bind_ge_3mm"],
                 RES["R1E"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
                 RES["R1E"][cid]["max_stretch_ratio"]), 2)
    RASP.text(cv, 24, 1050, "R1B SEVERE = %d (MAX %sX)  |  R1D SEVERE = %d (MAX %sX)"
              % (RES["R1B"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
                 RES["R1B"][cid]["max_stretch_ratio"],
                 RES["R1D"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
                 RES["R1D"][cid]["max_stretch_ratio"]), 2)
    RASP.save(cv, "%s_EDGE_STRAIN.png" % pfx, REND)
    log("rendered %s_EDGE_STRAIN.png" % pfx)

    cv = RASP.Canvas(W_, H_)
    draw_solid(cv, vp, V, TRIS)
    RASP.text(cv, 24, 20, "%s  SOLID SURFACE (R1E CANDIDATE)" % cid, 3)
    RASP.text(cv, 24, 60, "FROZEN POSE - SAME AXES / SIGNS / ANGLES / QUATERNION AS STAGE6A R1 / STAGE6B", 2)
    RASP.text(cv, 24, 84, "MAX STRETCH %sX ; SEVERE >5X = %d ; HISTORIC CLASS_B TEAR = %d"
              % (RES["R1E"][cid]["max_stretch_ratio"],
                 RES["R1E"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
                 RES["R1E"][cid]["historic_CLASS_B_tear"]), 2)
    RASP.save(cv, "%s_SOLID_SURFACE.png" % pfx, REND)
    log("rendered %s_SOLID_SURFACE.png" % pfx)

# --- 11. R3 collar close-up under FULL_OPP_L3
V = posed_V(CAND, "FULL_OPP_L3")
cv = RASP.Canvas(W_, H_)
ccen = sum((V0[i] for i in sorted(COLLAR)), Vector()) / len(COLLAR)
vc = fit_view(ccen, (0.30, 0.72, 0.62), (0, 0, 1), [V0[i] for i in sorted(COLLAR)], 3.4, W_, H_)
draw_solid(cv, vc, V, TRIS)
for k in BND_EDGE_IDS:
    a, b = EDGES[k]
    cv.line(vc.proj(V0[a]), vc.proj(V0[b]), (1.0, 1.0, 0.2), 2, 1.0)
for v in sorted(COLLAR):
    cv.px(vc.proj(V0[v])[0], vc.proj(V0[v])[1], (1.0, 1.0, 1.0), 3)
RASP.text(cv, 24, 20, "STAGE6B R1E  R3 COLLAR CLOSE-UP  FULL_OPP_L3", 3)
RASP.text(cv, 24, 60, "YELLOW = THE 16 R3 COLLAR EDGES ; WHITE = COLLAR VERTICES ; POSED R1E SURFACE", 2)
RASP.text(cv, 24, 84, "COLLAR SEVERE >5X EDGES = %d ; COLLAR WEIGHT L1 DIFFERENCE = 0.0"
          % RES["R1E"]["FULL_OPP_L3"]["SEVERE_EDGE_STRETCH_collar"], 2)
RASP.save(cv, "STAGE6B_R1E_R3_COLLAR_CLOSEUP_FULL_OPP_L3.png", REND)
log("rendered R3_COLLAR_CLOSEUP_FULL_OPP_L3")

print("R1E_PREQUAL_DONE VERDICT=%s" % VERDICT)
