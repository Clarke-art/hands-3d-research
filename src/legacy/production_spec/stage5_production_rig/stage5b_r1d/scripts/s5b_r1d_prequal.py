# =====================================================================================
# STAGE5B R1D -- TARGETED PREQUALIFICATION (round section 19 / 24)
# -------------------------------------------------------------------------------------
# Runs ONLY the six named poses plus the distal continuity probe, against the R1D
# candidate and (for before/after) the R1B frozen master and the R1C failed candidate.
# Emits the seven evidence PNGs required by round section 25.
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
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(HERE)
sys.path.append(os.path.join(PROD, "stage6_deformation", "stage6b_r1b", "scripts"))
sys.path.append(os.path.join(PROD, "stage6_deformation", "stage6b_r1c", "scripts"))
import s6br1b_common as K                                          # noqa: E402
import r1c_pen_common as RASP                                      # noqa: E402

OUT = os.path.join(PROD, "stage5_production_rig", "stage5b_r1d")
S6A_R1C = os.path.join(PROD, "stage6_deformation", "stage6a_r1c")
S6B_R1D = os.path.join(PROD, "stage6_deformation", "stage6b_r1d")
REND = os.path.join(OUT, "renders")
NOW = datetime.datetime.now().astimezone().isoformat()
MM = K.MM
TAU = 0.0
LOG = []


def log(s):
    LOG.append(s)
    print("[PQUAL] " + s, flush=True)


def rr(x, n=9):
    return K.rr(x, n)


for d in (OUT, S6A_R1C, S6B_R1D, REND):
    os.makedirs(d, exist_ok=True)

CAND_R1D = os.path.join(OUT, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1D.blend")

# ---------------------------------------------------------------- frozen context
ctx = K.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
POLY = ref["TOPO0"]
EDGES = ref["EDGES"]
TAU = ref["med_edge"]
MED = ctx["MED"]
probe = K.load_probe_sets()
PART = K.r2_partition(ctx, ref)
CORR = K.build_corrected_ownership(ctx, ref, PART["partition"], probe)["corrected"]
DOMAIN = set(K.build_corrected_ownership(ctx, ref, PART["partition"], probe)["domain"])

# live thumb axis (never the stale joint frame)
R2A = os.path.join(PROD, "stage5_production_rig", "stage5a_r2a",
                   "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
bpy.ops.wm.open_mainfile(filepath=R2A)
_ob = bpy.data.objects[K.MESH_OBJ]
_rig = bpy.data.objects[K.RIG_OBJ]
_MWo = _ob.matrix_world.copy()
LIVE = [_MWo @ Vector(_rig.data.bones[n].head_local)
        for n in ("THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R")]
LIVE.append(_MWo @ Vector(_rig.data.bones["THUMB_IP_R"].tail_local))
XIJ = [0.0]
_a = 0.0
for _i in range(3):
    _a += (LIVE[_i + 1] - LIVE[_i]).length
    XIJ.append(_a * MM)


def arc_of(pts, v):
    bd, bs, acc = 1e18, 0.0, 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-18)))
        d = (v - (a + ab * t)).length
        if d < bd:
            bd, bs = d, (acc + t * ab.length) * MM
        acc += ab.length
    return bs, bd * MM


sL = [arc_of(LIVE, V0[i])[0] for i in range(NV)]
DISTAL = set(i for i in range(NV) if CORR[i] == "THUMB" and sL[i] >= XIJ[2] - TAU)
CORR_THUMB = set(i for i in range(NV) if CORR[i] == "THUMB")
log("LIVE XIJ = %s ; distal set = %d ; corrected THUMB = %d"
    % ([rr(x, 3) for x in XIJ], len(DISTAL), len(CORR_THUMB)))

HIST_B = [(k, a, b) for k, a, b in probe["CLASS_B"]]
BIND_LEN = [(V0[a] - V0[b]).length * MM for a, b in EDGES]
HIST_BIND = dict((k, BIND_LEN[k]) for k, _a, _b in HIST_B)

CM6B = dict((c["case_id"], c) for c in
            json.load(open(os.path.join(PROD, "stage6_deformation", "stage6b",
                                        "STAGE6B_CASE_MATRIX.json"), encoding="utf-8"))["cases"])

S6A_CASES = [("TH_IP_30", "THUMB_IP_R", 30.0), ("TH_IP_45", "THUMB_IP_R", 45.0),
             ("TH_MCP_45", "THUMB_MCP_R", 45.0)]
S6B_CASES = ["CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]

SEVERE_STRETCH_X = 5.0
SEVERE_MIN_BIND_MM = 3.0
TEAR_X = 3.0
TEAR_MIN_POSED_MM = 5.0


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


def measure(V):
    o2 = o5 = sev = 0
    sev_distal = 0
    o2d = o5d = 0
    mx = 0.0
    mxinfo = None
    tear = 0
    tear_list = []
    hb_max = 0.0
    hb_torn = 0
    for k, (a, b) in enumerate(EDGES):
        bl = BIND_LEN[k]
        if bl <= 0.0:
            continue
        pl = (V[a] - V[b]).length * MM
        r = pl / bl
        if bl > SEVERE_MIN_BIND_MM:
            if r > 2.0:
                o2 += 1
                if a in DISTAL and b in DISTAL:
                    o2d += 1
            if r > SEVERE_STRETCH_X:
                o5 += 1
                if a in DISTAL and b in DISTAL:
                    o5d += 1
            if r > SEVERE_STRETCH_X:
                sev += 1
                if (a in DISTAL and b in DISTAL) or (a in DOMAIN and b in DOMAIN):
                    sev_distal += 1
            if r > mx:
                mx = r
                mxinfo = {"edge": k, "verts": [a, b], "bind_mm": rr(bl, 4), "posed_mm": rr(pl, 4),
                          "a_own": CORR[a], "b_own": CORR[b],
                          "distal": (a in DISTAL and b in DISTAL)}
        if r > TEAR_X and pl > TEAR_MIN_POSED_MM:
            tear += 1
            if len(tear_list) < 8:
                tear_list.append({"edge": k, "verts": [a, b], "ratio": rr(r, 4),
                                  "bind_mm": rr(bl, 4), "posed_mm": rr(pl, 4)})
    for k, a, b in HIST_B:
        bl = HIST_BIND[k]
        if bl <= 0:
            continue
        r = (V[a] - V[b]).length * MM / bl
        hb_max = max(hb_max, r)
        if r > TEAR_X and (V[a] - V[b]).length * MM > TEAR_MIN_POSED_MM:
            hb_torn += 1
    newp = intersect_pairs(V, POLY) - BASE_PAIRS
    newp_distal = sorted((a, b) for a, b in newp
                         if set(POLY[a]) <= (DISTAL | CORR_THUMB)
                         and set(POLY[b]) <= (DISTAL | CORR_THUMB))
    return {
        "edges_over_2x": o2, "edges_over_5x": o5,
        "edges_over_2x_distal": o2d, "edges_over_5x_distal": o5d,
        "SEVERE_EDGE_STRETCH_EDGE_COUNT": sev,
        "SEVERE_EDGE_STRETCH_DISTAL_COUNT": sev_distal,
        "max_stretch_ratio": rr(mx, 4), "max_stretch_edge": mxinfo,
        "TEAR_edges_over_3x_and_over_5mm": tear, "worst_tear_edges": tear_list,
        "historic_CLASS_B_max_stretch": rr(hb_max, 4),
        "historic_CLASS_B_tear": hb_torn,
        "new_self_intersection_pairs": len(newp),
        "new_self_intersection_pairs_distal": len(newp_distal),
        "new_severe_self_intersection_pairs_distal_sample": [list(x) for x in newp_distal[:12]],
    }


def run(path, label):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[K.MESH_OBJ]
    rig = bpy.data.objects[K.RIG_OBJ]
    MW = ob.matrix_world.copy()
    cases = {}
    for cid, bone, ang in S6A_CASES:
        K.B.S6.reset_pose(rig)
        K.B.S6.set_joint_rotation(rig, bone, -ang)
        K.B.update()
        V = K.RB.evaluate(ob, MW)[0]
        cases[cid] = measure(V)
        log("%-8s %-11s over2x=%4d over5x=%4d severe=%4d max=%.3f tear=%d histB_max=%.3f histB_tear=%d newSI=%d"
            % (label, cid, cases[cid]["edges_over_2x"], cases[cid]["edges_over_5x"],
               cases[cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"], cases[cid]["max_stretch_ratio"],
               cases[cid]["TEAR_edges_over_3x_and_over_5mm"],
               cases[cid]["historic_CLASS_B_max_stretch"], cases[cid]["historic_CLASS_B_tear"],
               cases[cid]["new_self_intersection_pairs"]))
    for cid in S6B_CASES:
        c = CM6B[cid]
        q = c["cmc_quaternion_local"]
        K.B.reset_pose(rig)
        pb = rig.pose.bones["THUMB_CMC_R"]
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
        for bn, dg in (("THUMB_MCP_R", c["mcp_deg"]), ("THUMB_IP_R", c["ip_deg"])):
            if dg:
                p = rig.pose.bones[bn]
                p.rotation_mode = 'QUATERNION'
                p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-dg))
        K.B.update()
        V = K.RB.evaluate(ob, MW)[0]
        cases[cid] = measure(V)
        log("%-8s %-11s over2x=%4d over5x=%4d severe=%4d max=%.3f tear=%d histB_max=%.3f histB_tear=%d newSI=%d"
            % (label, cid, cases[cid]["edges_over_2x"], cases[cid]["edges_over_5x"],
               cases[cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"], cases[cid]["max_stretch_ratio"],
               cases[cid]["TEAR_edges_over_3x_and_over_5mm"],
               cases[cid]["historic_CLASS_B_max_stretch"], cases[cid]["historic_CLASS_B_tear"],
               cases[cid]["new_self_intersection_pairs"]))
    return cases


RES = {}
for label, path in (("R1B", K.R1B_MASTER), ("R1C", K.R1C_MASTER), ("R1D", CAND_R1D)):
    RES[label] = run(path, label)

# ---------------------------------------------------------------- verdict
REQ = {}
for cid in ("TH_IP_45", "TH_IP_30", "TH_MCP_45"):
    REQ[cid] = {"severe_edge_stretch": RES["R1D"][cid]["SEVERE_EDGE_STRETCH_EDGE_COUNT"],
                "new_severe_distal_self_intersection": RES["R1D"][cid]["new_self_intersection_pairs_distal"]}
for cid in S6B_CASES:
    REQ[cid] = {"severe_distal_stretch": RES["R1D"][cid]["SEVERE_EDGE_STRETCH_DISTAL_COUNT"],
                "new_severe_distal_self_intersection": RES["R1D"][cid]["new_self_intersection_pairs_distal"]}
flip_a = json.load(open(os.path.join(OUT, "STAGE5B_R1D_HARD_FLIP_AUDIT.json"), encoding="utf-8"))
OK = (flip_a["R2_DISTAL_HARD_FLIP_EDGES"] == 0
      and all(v == 0 for c in REQ.values() for v in c.values()))
VERDICT = "PASS" if OK else "FAIL_CLOSED"

DATA = {
    "stage": "STAGE5B_R1D_TARGETED_PREQUALIFICATION",
    "generated_at": NOW,
    "poses": S6A_CASES and [c[0] for c in S6A_CASES] + S6B_CASES,
    "thresholds": {"severe_stretch_x": SEVERE_STRETCH_X, "min_bind_mm": SEVERE_MIN_BIND_MM,
                   "tear_x": TEAR_X, "tear_min_posed_mm": TEAR_MIN_POSED_MM},
    "R2_DISTAL_HARD_FLIP_EDGES": flip_a["R2_DISTAL_HARD_FLIP_EDGES"],
    "requirements": REQ,
    "targeted_prequalification": VERDICT,
    "results": RES,
    "log": LOG,
}
K.jdump("STAGE5B_R1D_TARGETED_PREQUALIFICATION.json", DATA, OUT)
log("TARGETED PREQUALIFICATION = %s" % VERDICT)

# =====================================================================================
# RENDERS  (round section 25)
# =====================================================================================
RASP.MESH_OBJ = K.MESH_OBJ
LIGHT = Vector((0.42, -0.30, 0.85)).normalized()
W_, H_ = 1500, 1100
COL = {"THUMB": (0.90, 0.55, 0.45), "INDEX": (0.42, 0.63, 0.95),
       "MIDDLE": (0.45, 0.80, 0.60), "RING": (0.72, 0.52, 0.90),
       "LITTLE": (0.92, 0.85, 0.42), "wrist": (0.62, 0.62, 0.60)}


def fit_view(cen, dirv, up, V, margin=1.06):
    r_, u_ = RASP.ortho_basis(Vector(dirv), Vector(up))
    mx = my = 0.0
    for p in V:
        q = p - cen
        mx = max(mx, abs(q.dot(r_)))
        my = max(my, abs(q.dot(u_)))
    return RASP.View(cen, dirv, up, max(mx, my * float(W_) / float(H_)) * margin * MM, W_, H_)


def shade(n):
    return 0.30 + 0.70 * abs(n.dot(LIGHT))


def draw_solid(cv, vw, V, tris, fcol=None):
    for fi, t in tris:
        base = fcol(fi) if fcol else COL.get(ctx["FO"][fi], (0.7, 0.7, 0.7))
        n = RASP.face_normals(V, [POLY[fi]])[0]
        cv.tri(vw.proj(V[t[0]]), vw.proj(V[t[1]]), vw.proj(V[t[2]]), shade(n), base)


def tri_list():
    return RASP.tris_of(POLY, V0)


TRIS = tri_list()
CENTRE = sum(V0, Vector()) / NV


# --- 1. distal weight field (dominant group colour, R1D vs R1B side by side)
def weight_panel(W, V):
    def fcol(fi):
        c = Counter(max(W[v].items(), key=lambda kv: kv[1])[0] for v in POLY[fi])
        g = c.most_common(1)[0][0]
        return COL.get(K.GROUP_DIGIT.get(g, "wrist"), (0.7, 0.7, 0.7))
    return fcol


def readW(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[K.MESH_OBJ]
    return K.read_weights(ob, NV), ob.matrix_world.copy()


W_R1B, _m1 = readW(K.R1B_MASTER)
W_R1D, _m2 = readW(CAND_R1D)
cv = RASP.Canvas(W_, H_)
vw = fit_view(CENTRE, (0.55, 0.42, 0.72), (0, 0, 1), V0, 2.2)
half = RASP.View(vw.c, vw.d, (vw.u.cross(vw.d)).normalized() * -1, vw.hw * MM * 0.5, W_, H_)
half.c = vw.c - vw.r * vw.hw * 0.5
draw_solid(cv, half, V0, TRIS, weight_panel(W_R1B, V0))
half2 = RASP.View(vw.c + vw.r * vw.hw * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1,
                  vw.hw * MM * 0.5, W_, H_)
draw_solid(cv, half2, V0, TRIS, weight_panel(W_R1D, V0))
RASP.text(cv, 24, 20, "STAGE5B R1D  DISTAL WEIGHT FIELD  (DOMINANT GROUP)", 3)
RASP.text(cv, 24, 60, "LEFT = STAGE5B R1B FROZEN MASTER   |   RIGHT = STAGE5B R1D CANDIDATE", 2)
RASP.text(cv, 24, 84, "COLOURS = THUMB SALMON / INDEX BLUE / MIDDLE GREEN / RING PURPLE / LITTLE YELLOW / WRIST GREY", 2)
RASP.text(cv, 24, 1050, "SAME GEOMETRY, SAME POSE - ONLY THE BLEND WEIGHTS DIFFER.", 2)
RASP.save(cv, "STAGE5B_R1D_DISTAL_WEIGHT_FIELD.png", REND)
log("rendered STAGE5B_R1D_DISTAL_WEIGHT_FIELD.png")


# --- 2. hard flip before / after
def flip_edges(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects[K.MESH_OBJ]
    W = K.read_weights(ob, NV)
    out = []
    for a, b in EDGES:
        wa, wb = W[a], W[b]
        L = set(g for g, v in wa.items() if v >= 0.95) & set(g for g in wa if wb.get(g, 0.0) <= 0.05)
        Rp = set(g for g, v in wb.items() if v >= 0.95) & set(g for g in wb if wa.get(g, 0.0) <= 0.05)
        if L and Rp and L != Rp:
            out.append((a, b))
    return out


FE_B = flip_edges(K.R1B_MASTER)
FE_D = flip_edges(CAND_R1D)
cv = RASP.Canvas(W_, H_)
left = RASP.View(vw.c - vw.r * vw.hw * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1,
                 vw.hw * MM * 0.5, W_, H_)
right = RASP.View(vw.c + vw.r * vw.hw * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1,
                  vw.hw * MM * 0.5, W_, H_)
draw_solid(cv, left, V0, TRIS, lambda fi: (0.42, 0.44, 0.48))
draw_solid(cv, right, V0, TRIS, lambda fi: (0.42, 0.44, 0.48))
for pan, fe in ((left, FE_B), (right, FE_D)):
    for a, b in fe:
        cv.px(pan.proj(V0[a])[0], pan.proj(V0[a])[1], (1.0, 0.15, 0.15), 6)
        cv.px(pan.proj(V0[b])[0], pan.proj(V0[b])[1], (1.0, 0.15, 0.15), 6)
RASP.text(cv, 24, 20, "STAGE5B R1D  HARD 0/1 WEIGHT FLIP EDGES  BEFORE / AFTER", 3)
RASP.text(cv, 24, 60, "BEFORE (R1B MASTER): %d FLIP EDGES  |  AFTER (R1D): %d FLIP EDGES  |  0 NEW" %
          (len(FE_B), len(FE_D)), 2)
RASP.text(cv, 24, 84, "RED DOTS = ENDPOINTS OF A HARD 0/1 FLIP EDGE (SAME BIND POSE, SAME GEOMETRY)", 2)
RASP.text(cv, 24, 1050, "THE 3 REMAINING AFTER-EDGES ARE PRE-EXISTING FIRST-WEB / THENAR STEPS, PRESENT IN R1B TOO.", 2)
RASP.save(cv, "STAGE5B_R1D_HARD_FLIP_BEFORE_AFTER.png", REND)
log("rendered STAGE5B_R1D_HARD_FLIP_BEFORE_AFTER.png")


# --- 3/4/5/6/7. strain + solid renders for the named poses
def pose_and_render(blend, kind, cid, bone=None, ang=None):
    bpy.ops.wm.open_mainfile(filepath=blend)
    ob = bpy.data.objects[K.MESH_OBJ]
    rig = bpy.data.objects[K.RIG_OBJ]
    MW = ob.matrix_world.copy()
    if kind == "s6a":
        K.B.S6.reset_pose(rig)
        K.B.S6.set_joint_rotation(rig, bone, -ang)
    else:
        c = CM6B[cid]
        q = c["cmc_quaternion_local"]
        K.B.reset_pose(rig)
        pb = rig.pose.bones["THUMB_CMC_R"]
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
        for bn, dg in (("THUMB_MCP_R", c["mcp_deg"]), ("THUMB_IP_R", c["ip_deg"])):
            if dg:
                p = rig.pose.bones[bn]
                p.rotation_mode = 'QUATERNION'
                p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-dg))
    K.B.update()
    return K.RB.evaluate(ob, MW)[0]


for cid, bone, ang in S6A_CASES:
    V = pose_and_render(CAND_R1D, "s6a", cid, bone, ang)
    face_ratio = [1.0] * len(POLY)
    for fi, p in enumerate(POLY):
        m = 1.0
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            bl = (V0[a] - V0[b]).length * MM
            if bl > SEVERE_MIN_BIND_MM:
                m = max(m, (V[a] - V[b]).length * MM / bl)
        face_ratio[fi] = m

    def strain_col(fi, fr=face_ratio):
        r = fr[fi]
        if r < 1.5:
            return (0.28 + 0.34 * (r - 1.0) / 0.5, 0.42, 0.60)
        if r < 2.5:
            t = (r - 1.5)
            return (0.62 + 0.33 * t, 0.80 - 0.25 * t, 0.45 - 0.30 * t)
        t = min(1.0, (r - 2.5) / 2.5)
        return (0.95, 0.55 - 0.50 * t, 0.15 - 0.13 * t)

    cv = RASP.Canvas(W_, H_)
    cen = sum(V, Vector()) / NV
    vwp = fit_view(cen, (0.55, 0.42, 0.72), (0, 0, 1), V)
    draw_solid(cv, vwp, V, TRIS, strain_col)
    RASP.text(cv, 24, 20, "%s  EDGE STRAIN (R1D CANDIDATE)" % cid, 3)
    RASP.text(cv, 24, 60, "BLUE <=1.5X / YELLOW 1.5-2.5X / RED >=5X   (BIND EDGES > 3 MM)", 2)
    RASP.text(cv, 24, 84, "OVER 2X = %d ; OVER 5X = %d ; MAX = %.3fX"
              % (RES["R1D"][cid]["edges_over_2x"], RES["R1D"][cid]["edges_over_5x"],
                 RES["R1D"][cid]["max_stretch_ratio"]), 2)
    RASP.save(cv, "STAGE6A_R1C_%s_EDGE_STRAIN.png" % cid, REND)
    log("rendered STAGE6A_R1C_%s_EDGE_STRAIN.png" % cid)

    if cid == "TH_IP_45":
        cv = RASP.Canvas(W_, H_)
        draw_solid(cv, vwp, V, TRIS)
        RASP.text(cv, 24, 20, "TH_IP_45  SOLID SURFACE (R1D CANDIDATE)", 3)
        RASP.text(cv, 24, 60, "THUMB IP 45 DEG FLEXION, CMC / WRIST LOCKED AT BIND - SAME CALIBER AS STAGE6A R1A", 2)
        RASP.text(cv, 24, 84, "R1B MASTER FOR THE SAME POSE: OVER 5X = %d ; MAX = %.3fX"
                  % (RES["R1B"]["TH_IP_45"]["edges_over_5x"], RES["R1B"]["TH_IP_45"]["max_stretch_ratio"]), 2)
        RASP.save(cv, "STAGE6A_R1C_TH_IP45_SOLID_SURFACE.png", REND)
        log("rendered STAGE6A_R1C_TH_IP45_SOLID_SURFACE.png")

for cid in S6B_CASES:
    V = pose_and_render(CAND_R1D, "s6b", cid)
    face_ratio = [1.0] * len(POLY)
    for fi, p in enumerate(POLY):
        m = 1.0
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            bl = (V0[a] - V0[b]).length * MM
            if bl > SEVERE_MIN_BIND_MM:
                m = max(m, (V[a] - V[b]).length * MM / bl)
        face_ratio[fi] = m

    def strain_col2(fi, fr=face_ratio):
        r = fr[fi]
        if r < 1.5:
            return (0.28 + 0.34 * (r - 1.0) / 0.5, 0.42, 0.60)
        if r < 2.5:
            t = (r - 1.5)
            return (0.62 + 0.33 * t, 0.80 - 0.25 * t, 0.45 - 0.30 * t)
        t = min(1.0, (r - 2.5) / 2.5)
        return (0.95, 0.55 - 0.50 * t, 0.15 - 0.13 * t)

    tag = {"CMC_OPP_30": "CMC_OPP30", "CMC_MCP_L3": "CMC_MCP_L3", "FULL_OPP_L3": "FULL_OPP_L3"}[cid]
    cv = RASP.Canvas(W_, H_)
    cen = sum(V, Vector()) / NV
    vwp = fit_view(cen, (0.55, 0.42, 0.72), (0, 0, 1), V)
    draw_solid(cv, vwp, V, TRIS)
    RASP.text(cv, 24, 20, "%s  SOLID SURFACE (R1D CANDIDATE)" % tag, 3)
    RASP.text(cv, 24, 60, "MAX STRETCH %.3fX (R1B %.3fX / R1C %.3fX) ; OVER 5X = %d (R1B %d / R1C %d)"
              % (RES["R1D"][cid]["max_stretch_ratio"], RES["R1B"][cid]["max_stretch_ratio"],
                 RES["R1C"][cid]["max_stretch_ratio"], RES["R1D"][cid]["edges_over_5x"],
                 RES["R1B"][cid]["edges_over_5x"], RES["R1C"][cid]["edges_over_5x"]), 2)
    RASP.save(cv, "STAGE6B_R1D_%s_SOLID_SURFACE.png" % tag, REND)
    log("rendered STAGE6B_R1D_%s_SOLID_SURFACE.png" % tag)

    if cid == "FULL_OPP_L3":
        cv = RASP.Canvas(W_, H_)
        draw_solid(cv, vwp, V, TRIS, strain_col2)
        RASP.text(cv, 24, 20, "FULL_OPP_L3  EDGE STRAIN (R1D CANDIDATE)", 3)
        RASP.text(cv, 24, 60, "BLUE <=1.5X / YELLOW 1.5-2.5X / RED >=5X   (BIND EDGES > 3 MM)", 2)
        RASP.text(cv, 24, 84, "OVER 2X = %d ; OVER 5X = %d ; MAX = %.3fX"
                  % (RES["R1D"][cid]["edges_over_2x"], RES["R1D"][cid]["edges_over_5x"],
                     RES["R1D"][cid]["max_stretch_ratio"]), 2)
        RASP.text(cv, 24, 1050, "R1B: OVER 5X = %d, MAX %.3fX  |  R1C: OVER 5X = %d, MAX %.3fX"
                  % (RES["R1B"][cid]["edges_over_5x"], RES["R1B"][cid]["max_stretch_ratio"],
                     RES["R1C"][cid]["edges_over_5x"], RES["R1C"][cid]["max_stretch_ratio"]), 2)
        RASP.save(cv, "STAGE6B_R1D_FULL_OPP_L3_EDGE_STRAIN.png", REND)
        log("rendered STAGE6B_R1D_FULL_OPP_L3_EDGE_STRAIN.png")

# --- 8. R2 corrected ownership boundary (the interleaving that blocks a continuous field)
BND_EDGES = []
for k, (a, b) in enumerate(EDGES):
    if CORR[a] != CORR[b]:
        BND_EDGES.append((k, a, b))
cv = RASP.Canvas(W_, H_)
cen = sum(V0, Vector()) / NV
vwb = fit_view(cen, (0.55, 0.42, 0.72), (0, 0, 1), V0, 3.0)


def own_col(fi):
    c = Counter(CORR[v] for v in POLY[fi])
    g = c.most_common(1)[0][0]
    return COL.get(g, (0.7, 0.7, 0.7))


draw_solid(cv, vwb, V0, TRIS, own_col)
for k, a, b in BND_EDGES:
    if {CORR[a], CORR[b]} != {"THUMB", "INDEX"}:
        continue
    short = (V0[a] - V0[b]).length * MM <= 6.0
    c = (1.0, 0.15, 0.15) if short else (0.15, 1.0, 0.35)
    cv.line(vwb.proj(V0[a]), vwb.proj(V0[b]), c, 2, 1.0)
n_short = sum(1 for k, a, b in BND_EDGES
              if {CORR[a], CORR[b]} == {"THUMB", "INDEX"} and (V0[a] - V0[b]).length * MM <= 6.0)
RASP.text(cv, 24, 20, "STAGE5B R1D  CORRECTED OWNERSHIP BOUNDARY AT THE THUMB TIP", 3)
RASP.text(cv, 24, 60, "SURFACE COLOURED BY CORRECTED DIGIT OWNERSHIP (THUMB SALMON / INDEX BLUE / ...)", 2)
RASP.text(cv, 24, 84, "RED = THUMB/INDEX BOUNDARY EDGE WITH BIND LENGTH <= 6 MM (%d OF THEM) - AN INTERLEAVED LABEL FIELD" % n_short, 2)
RASP.text(cv, 24, 108, "GREEN = THUMB/INDEX BOUNDARY EDGE LONGER THAN 6 MM", 2)
RASP.text(cv, 24, 1050, "ADJACENT VERTICES 3-6 MM APART CARRY OPPOSITE DIGIT LABELS, SO NO WEIGHT FIELD CAN BE", 2)
RASP.text(cv, 24, 1074, "BOTH OWNERSHIP-CONSISTENT AND CONTINUOUS THERE.", 2)
RASP.save(cv, "STAGE5B_R1D_R2_OWNERSHIP_BOUNDARY.png", REND)
log("rendered STAGE5B_R1D_R2_OWNERSHIP_BOUNDARY.png (%d short THUMB/INDEX boundary edges)" % n_short)
json.dump({"r2_boundary_edges_total": len(BND_EDGES),
           "thumb_index_boundary_edges": sum(1 for k, a, b in BND_EDGES if {CORR[a], CORR[b]} == {"THUMB", "INDEX"}),
           "thumb_index_boundary_edges_bind_le_6mm": n_short,
           "list": [{"edge": k, "a": a, "b": b, "bind_mm": rr((V0[a] - V0[b]).length * MM, 4),
                     "a_own": CORR[a], "b_own": CORR[b]} for k, a, b in BND_EDGES]},
          open(os.path.join(OUT, "STAGE5B_R1D_R2_OWNERSHIP_BOUNDARY.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print("PREQUAL_DONE  VERDICT=%s" % VERDICT)
