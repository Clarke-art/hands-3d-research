# =====================================================================================
# R1E_THUMB_TRANSITION_GEOMETRIC_FEASIBILITY_AUDIT -- evidence renders (READ ONLY)
# =====================================================================================
import os
import sys
import json
import math
from collections import Counter

import bpy
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.abspath(os.path.join(HERE, ".."))
PROD = os.path.abspath(os.path.join(AUD, "..", ".."))
R1E_DIR = os.path.join(PROD, "stage5_production_rig", "stage5b_r1e")
sys.path.append(os.path.join(R1E_DIR, "scripts"))
sys.path.append(os.path.join(PROD, "stage6_deformation", "stage6b_r1c", "scripts"))
import s5b_r1e_common as C                                          # noqa: E402
import r1c_pen_common as RASP                                       # noqa: E402

REND = os.path.join(AUD, "renders")
os.makedirs(REND, exist_ok=True)
MM = C.MM
CAND_R1E = os.path.join(R1E_DIR, "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend")


def load(n):
    return json.load(open(os.path.join(AUD, n), encoding="utf-8"))


EXACT = load("R1E_EXACT_R3_COLLAR_DYNAMIC_AUDIT.json")
RECL = load("R1E_OLD_COLLAR_SEVERE_RECLASSIFICATION.json")
SP = load("R1E_CAP_TO_COLLAR_SHORTEST_PATH_AUDIT.json")
ENS = load("R1E_CAP_TO_COLLAR_PATH_ENSEMBLE_AUDIT.json")
STRICT = load("R1E_STRICT_GEOMETRIC_BOUND_AUDIT.json")
TOPO = dict((c, load("R1E_%s_SEVERE_EDGE_TOPOLOGY_MAP.json" % c))
            for c in ("FULL_OPP_L3", "CMC_OPP_30", "CMC_MCP_L3"))
E5879 = load("R1E_EDGE5879_FORENSIC_AUDIT.json")

LAB = json.load(open(C.R3_FILES["r3_ownership_labels"], encoding="utf-8"))
CAP = sorted(LAB["CAP"])
BND_IDS = list(LAB["boundary_edges_R3"])

# ---------------------------------------------------------------- geometry
bpy.ops.wm.open_mainfile(filepath=C.R1B_MASTER)
_ob = bpy.data.objects[C.MESH_OBJ]
_mw = _ob.matrix_world.copy()
NV = len(_ob.data.vertices)
V0 = [(_mw @ v.co).copy() for v in _ob.data.vertices]
EDGES = [(e.vertices[0], e.vertices[1]) for e in _ob.data.edges]
POLY = [tuple(p.vertices) for p in _ob.data.polygons]

COLLAR = set()
for k in BND_IDS:
    COLLAR.update(EDGES[k])
ADJ = {}
for a, b in EDGES:
    ADJ.setdefault(a, set()).add(b)
    ADJ.setdefault(b, set()).add(a)
ADJ = dict((k, sorted(v)) for k, v in ADJ.items())
C1 = set()
for v in COLLAR:
    C1.update(ADJ[v])
C1 -= COLLAR
C2 = set()
for v in C1:
    C2.update(ADJ[v])
C2 -= COLLAR | C1

bpy.ops.wm.open_mainfile(filepath=CAND_R1E)
oE = bpy.data.objects[C.MESH_OBJ]
rE = bpy.data.objects[C.RIG_OBJ]
MWE = oE.matrix_world.copy()
W_R1E = C.read_weights(oE, NV)

CM6B = dict((c["case_id"], c) for c in json.load(open(C.CASE_MATRIX, encoding="utf-8"))["cases"])
POSES = [("TH_IP_30", "S6A", ("THUMB_IP_R", 30.0)), ("TH_IP_45", "S6A", ("THUMB_IP_R", 45.0)),
         ("TH_MCP_45", "S6A", ("THUMB_MCP_R", 45.0)),
         ("CMC_OPP_30", "S6B", None), ("CMC_MCP_L3", "S6B", None), ("FULL_OPP_L3", "S6B", None)]


def set_pose(cid, kind, arg):
    C.reset_pose(rE)
    if kind == "S6A":
        C.set_joint_rotation(rE, arg[0], -arg[1])
    else:
        c = CM6B[cid]
        q = c["cmc_quaternion_local"]
        pb = rE.pose.bones["THUMB_CMC_R"]
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
        for bn, dg in (("THUMB_MCP_R", c["mcp_deg"]), ("THUMB_IP_R", c["ip_deg"])):
            if dg:
                p = rE.pose.bones[bn]
                p.rotation_mode = 'QUATERNION'
                p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-dg))
    C.update()


POSED = {}
for cid, kind, arg in POSES:
    set_pose(cid, kind, arg)
    POSED[cid] = C.evaluate(oE, MWE)[0]

RASP.MESH_OBJ = C.MESH_OBJ
LIGHT = Vector((0.42, -0.30, 0.85)).normalized()
W_, H_ = 1500, 1100
TRIS = RASP.tris_of(POLY, V0)
CENTRE = sum(V0, Vector()) / NV


def fit(cen, dirv, up, V, margin=1.06, Wp=None, Hp=None):
    Wp = Wp or W_
    Hp = Hp or H_
    r_, u_ = RASP.ortho_basis(Vector(dirv), Vector(up))
    mx = my = 0.0
    for p in V:
        q = p - cen
        mx = max(mx, abs(q.dot(r_)))
        my = max(my, abs(q.dot(u_)))
    return RASP.View(cen, dirv, up, max(mx, my * float(Wp) / float(Hp)) * margin * MM, Wp, Hp)


def shade(n):
    return 0.30 + 0.70 * abs(n.dot(LIGHT))


def solid(cv, vw, V, tris, fcol=None):
    for fi, t in tris:
        base = fcol(fi) if fcol else (0.30, 0.32, 0.35)
        n = RASP.face_normals(V, [POLY[fi]])[0]
        cv.tri(vw.proj(V[t[0]]), vw.proj(V[t[1]]), vw.proj(V[t[2]]), shade(n), base)


def vdot(cv, vw, V, v, c, r=4):
    x, y, z = vw.proj(V[v])
    cv.px(x, y, c, r, 1.0)          # markers always draw on top of the solid pass


def vlabel(cv, vw, V, v, c):
    x, y, z = vw.proj(V[v])
    RASP.text(cv, int(x) + 8, int(y) - 6, str(v), 2, c)


SEV_ROWS = {}


def severe_rows(cid, V):
    out = []
    for k, (a, b) in enumerate(EDGES):
        bl = (V0[a] - V0[b]).length * MM
        if bl < C.SEVERE_MIN_BIND_MM:
            continue
        r = (V[a] - V[b]).length * MM / bl
        if r > C.SEVERE_STRETCH_X:
            out.append((k, a, b, r))
    return out


for cid, kind, arg in POSES:
    SEV_ROWS[cid] = severe_rows(cid, POSED[cid])

PATH = SP["shortest"]["path"]
PV = PATH["vertex_sequence"]
PE = PATH["edge_id_sequence"]


# =====================================================================================
# 1. shortest path on the bind mesh
# =====================================================================================
def path_panel(fname, cid, title, extra_lines, dirv=(0.92, 0.25, 0.30)):
    V = POSED[cid] if cid else V0
    cen = sum((V0[v] for v in PV), Vector()) / len(PV)
    vw = fit(cen, dirv, (0, 0, 1), [V0[v] for v in PV], 2.6)
    cv = RASP.Canvas(W_, H_)
    solid(cv, vw, V, TRIS, lambda fi: (0.26, 0.28, 0.31))
    for k in BND_IDS:
        a, b = EDGES[k]
        cv.line(vw.proj(V[a]), vw.proj(V[b]), (1.00, 0.90, 0.10), 2, 1.0)
    for v in sorted(COLLAR):
        vdot(cv, vw, V, v, (1.0, 1.0, 1.0), 3)
    for k in PE:
        a, b = EDGES[k]
        cv.line(vw.proj(V[a]), vw.proj(V[b]), (0.10, 1.00, 0.30), 4, 1.0)
    for v in PV:
        vdot(cv, vw, V, v, (1.0, 0.15, 0.15), 7)
        vlabel(cv, vw, V, v, (1.0, 0.55, 0.55))
    RASP.text(cv, 24, 20, title, 3)
    y = 60
    for ln in extra_lines:
        RASP.text(cv, 24, y, ln, 2)
        y += 22
    RASP.text(cv, 24, 1050, "YELLOW = THE 16 EXACT R3 COLLAR EDGES ; WHITE = 32 COLLAR VERTICES", 2)
    RASP.text(cv, 24, 1072, "GREEN = SHORTEST PATH EDGES ; RED DOTS = SHORTEST PATH VERTICES", 2)
    RASP.save(cv, fname, REND)
    print("[REND] " + fname, flush=True)


path_panel("R1E_CAP_TO_COLLAR_SHORTEST_PATH_BIND.png", None,
           "R1E  SHORTEST PATH  APPROVED DISTAL CAP -> R3 COLLAR (BIND MESH)",
           ["PATH: %s   (%d EDGES, %s MM TOTAL BIND LENGTH)"
            % (" -> ".join(str(v) for v in PV), PATH["edge_count"], PATH["total_bind_polyline_mm"]),
            "EDGE IDs %s ; BIND LENGTHS %s MM" % (PE, PATH["edge_bind_lengths_mm"]),
            "R3 OWNERSHIP %s" % PATH["r3_ownership_sequence"],
            "SEMANTIC ROUTE %s" % " -> ".join(PATH["semantic_region_sequence"]),
            "GRAPH DISTANCE TO COLLAR %s ; TO DISTAL CAP %s"
            % (PATH["graph_distance_to_exact_collar"], PATH["graph_distance_to_distal_cap"]),
            "BIND-POSE MEASUREMENT - NO POSE APPLIED"])

for cid, tag in (("TH_IP_45", "TH_IP45"), ("CMC_OPP_30", "CMC_OPP30"), ("FULL_OPP_L3", "FULL_OPP_L3")):
    # the strict-bound list is built from the ensemble in the same order, so index 0 is the
    # shortest cap -> INDEX-collar path
    row = STRICT["per_pose"][cid]["paths"][0]
    extra = ["STRICT LOWER BOUND dt/L = %s  (POSE %s)" % (row["STRICT_LOWER_BOUND_dt_over_L_bind"], cid),
             "dt POSED ENDPOINT SEPARATION = %s MM ; L_bind = %s MM ; SLACK_5X = %s MM"
             % (row["dt_posed_separation_mm"], row["L_bind_path_mm"], row["SLACK_5X_mm"]),
             "|uA| %s MM ; |uB| %s MM ; |delta u| %s MM ; MOVEMENT %s"
             % (row["uA_displacement_mm"], row["uB_displacement_mm"],
                row["delta_u_mm"], row["MOVEMENT_CHARACTER"]),
             "OBSERVED MAX STRETCH ON THIS PATH = %s" % row["OBSERVED_MAX_STRETCH_ON_PATH"]]
    path_panel("R1E_CAP_TO_COLLAR_PATH_%s.png" % tag, cid,
               "R1E  SHORTEST PATH UNDER %s" % cid, extra)


# =====================================================================================
# 2. exact collar edge stretch across all 6 poses
# =====================================================================================
cv = RASP.Canvas(W_, H_)
rows = EXACT["rows"]
n_e, n_p = len(BND_IDS), len(POSES)
top, bot, left, right = 150, 980, 120, 1460
cw = (right - left) / float(n_e)
ch = (bot - top) / float(n_p)
for j, (cid, kind, arg) in enumerate(POSES):
    for i, k in enumerate(BND_IDS):
        r = [x for x in rows if x["pose"] == cid and x["edge_id"] == k][0]["stretch_ratio"]
        t = max(0.0, min(1.0, (r - 0.9) / 2.1))
        col = (0.20 + 0.10 * t, 0.65 - 0.55 * t, 0.35 - 0.25 * t)
        x0 = left + i * cw
        y0 = top + j * ch
        cv.px(x0 + cw * 0.5, y0 + ch * 0.5, col, 18, 1.0)
RASP.text(cv, 24, 20, "R1E  EXACT 16 R3 COLLAR BOUNDARY EDGES  -  STRETCH IN ALL 6 FROZEN POSES", 3)
RASP.text(cv, 24, 60, "ROWS = POSES (TOP TO BOTTOM: TH_IP_30 / TH_IP_45 / TH_MCP_45 / CMC_OPP_30 / CMC_MCP_L3 / FULL_OPP_L3)", 2)
RASP.text(cv, 24, 84, "COLUMNS = THE 16 EXACT R3 BOUNDARY EDGE IDS   EDGE IDS: %s" % BND_IDS, 2)
RASP.text(cv, 24, 1050, "MAX RATIO OVER 16 EDGES x 6 POSES = %s ; MAX |RATIO-1| = %s -> VERDICT %s"
          % (EXACT["max_stretch_ratio_over_all_16_edges_and_6_poses"],
             EXACT["max_abs_deviation_of_ratio_from_1"], EXACT["classification_verdict"]), 2)
RASP.text(cv, 24, 1072, "BOTH ENDPOINTS OF EVERY EXACT COLLAR EDGE ARE WRIST_R = 1.0 -> IDENTICAL RIGID TRANSFORM -> LENGTH INVARIANT.", 2)
RASP.save(cv, "R1E_EXACT_COLLAR_EDGE_STRETCH_6POSE.png", REND)
print("[REND] R1E_EXACT_COLLAR_EDGE_STRETCH_6POSE.png", flush=True)


# =====================================================================================
# 3. severe edges by collar distance
# =====================================================================================
def level_col(lv):
    return {"LEVEL_0_EXACT_R3_BOUNDARY_EDGE": (1.00, 0.10, 0.10),
            "LEVEL_1_COLLAR_VERTEX_INCIDENT": (1.00, 0.55, 0.05),
            "LEVEL_2_COLLAR_ONE_RING": (1.00, 0.90, 0.10),
            "LEVEL_3_COLLAR_TWO_RING": (0.35, 0.85, 0.35),
            "LEVEL_4_PLUS_TRANSITION": (0.35, 0.60, 1.00)}.get(lv, (0.6, 0.6, 0.6))


for cid, tag in (("FULL_OPP_L3", "FULL_OPP_L3"), ("CMC_OPP_30", "CMC_OPP30")):
    cen = sum((V0[v] for v in COLLAR), Vector()) / len(COLLAR)
    ring_pts = [V0[v] for v in list(COLLAR) + list(C1) + list(C2)]
    vw = fit(cen, (0.92, 0.25, 0.30), (0, 0, 1), ring_pts, 1.7)
    cv = RASP.Canvas(W_, H_)
    solid(cv, vw, POSED[cid], TRIS, lambda fi: (0.24, 0.26, 0.29))
    for v in sorted(C2):
        vdot(cv, vw, V0, v, (0.35, 0.85, 0.35), 2)
    for v in sorted(C1):
        vdot(cv, vw, V0, v, (1.00, 0.90, 0.10), 2)
    for v in sorted(COLLAR):
        vdot(cv, vw, V0, v, (1.0, 1.0, 1.0), 3)
    for k in BND_IDS:
        a, b = EDGES[k]
        cv.line(vw.proj(V0[a]), vw.proj(V0[b]), (0.10, 1.00, 0.30), 3, 1.0)
    for r in TOPO[cid]["edges"]:
        a, b = r["v0"], r["v1"]
        cv.line(vw.proj(V0[a]), vw.proj(V0[b]), level_col(r["level"]), 3, 1.0)
        vdot(cv, vw, V0, a, level_col(r["level"]), 4)
        vdot(cv, vw, V0, b, level_col(r["level"]), 4)
    RASP.text(cv, 24, 20, "R1E  %s  SEVERE EDGES BY COLLAR TOPOLOGY DISTANCE" % cid, 3)
    RASP.text(cv, 24, 60, "GREEN LINE = EXACT 16 R3 BOUNDARY EDGES (LEVEL 0) ; WHITE DOTS = 32 COLLAR VERTICES", 2)
    RASP.text(cv, 24, 84, "SEVERE DT > 5X COLOURS   RED L0 / ORANGE L1 / YELLOW L2 / GREEN L3 / BLUE L4+", 2)
    y = 106
    for lv in ("LEVEL_0_EXACT_R3_BOUNDARY_EDGE", "LEVEL_1_COLLAR_VERTEX_INCIDENT",
               "LEVEL_2_COLLAR_ONE_RING", "LEVEL_3_COLLAR_TWO_RING", "LEVEL_4_PLUS_TRANSITION"):
        RASP.text(cv, 24, y, "%s = %d" % (lv, TOPO[cid]["by_level"].get(lv, 0)), 2,
                  level_col(lv))
        y += 20
    RASP.text(cv, 24, 1050, "SEVERE TOTAL = %d ; DOMINANT SEMANTIC PAIR = %s"
              % (TOPO[cid]["severe_edge_count"], TOPO[cid]["dominant_region"]), 2)
    RASP.save(cv, "R1E_%s_SEVERE_BY_COLLAR_DISTANCE.png" % tag, REND)
    print("[REND] R1E_%s_SEVERE_BY_COLLAR_DISTANCE.png" % tag, flush=True)


# =====================================================================================
# 4. edge 5879 neighbourhood
# =====================================================================================
ea, eb = E5879["v0"], E5879["v1"]
nbr = set([ea, eb])
for v in (ea, eb):
    nbr.update(ADJ[v])
cen = (V0[ea] + V0[eb]) * 0.5
vw = fit(cen, (0.92, 0.25, 0.30), (0, 0, 1), [V0[v] for v in nbr], 9.0)
cv = RASP.Canvas(W_, H_)
solid(cv, vw, POSED["FULL_OPP_L3"], TRIS, lambda fi: (0.24, 0.26, 0.29))
for v in sorted(nbr - {ea, eb}):
    vdot(cv, vw, V0, v, (0.70, 0.70, 0.70), 3)
cv.line(vw.proj(V0[ea]), vw.proj(V0[eb]), (1.0, 0.10, 0.10), 4, 1.0)
vdot(cv, vw, V0, ea, (1.0, 0.10, 0.10), 8)
vdot(cv, vw, V0, eb, (1.0, 0.60, 0.10), 8)
vlabel(cv, vw, V0, ea, (1.0, 0.5, 0.5))
vlabel(cv, vw, V0, eb, (1.0, 0.8, 0.5))
RASP.text(cv, 24, 20, "R1E  EDGE 5879  FORENSIC  (v%d <-> v%d)" % (ea, eb), 3)
RASP.text(cv, 24, 60, "BIND %s MM ; WORST POSE %s AT %sX" % (E5879["bind_length_mm"], E5879["worst_pose"], E5879["worst_ratio"]), 2)
RASP.text(cv, 24, 84, "R3 %s / SEMANTIC %s ; G TO COLLAR %s"
          % (E5879["r3_ownership"], E5879["semantic_regions"], E5879["topology_distance_to_exact_collar"]), 2)
RASP.text(cv, 24, 106, "G TO DISTAL CAP %s ; WEIGHTS R1E v%d %s ; v%d %s"
          % (E5879["topology_distance_to_distal_cap"], ea,
             json.dumps(E5879["weights_R1E"]["v0"]), eb,
             json.dumps(E5879["weights_R1E"]["v1"])), 2)
RASP.text(cv, 24, 1050, "THE TWO ENDPOINTS SIT ON OPPOSITE SIDES OF THE THUMB->PALM TRANSITION GRADIENT.", 2)
RASP.text(cv, 24, 1072, "THIS IS A GRADIENT DIFFERENTIAL, NOT A HARD 0/1 FLIP (NO HARD FLIP IS REPORTED ON THIS EDGE).", 2)
RASP.save(cv, "R1E_EDGE5879_NEIGHBORHOOD.png", REND)
print("[REND] R1E_EDGE5879_NEIGHBORHOOD.png", flush=True)


# =====================================================================================
# 5. transition weight field with severe edges overlaid
# =====================================================================================
COL = {"THUMB": (0.90, 0.55, 0.45), "INDEX": (0.42, 0.63, 0.95),
       "MIDDLE": (0.45, 0.80, 0.60), "RING": (0.72, 0.52, 0.90),
       "LITTLE": (0.92, 0.85, 0.42), "wrist": (0.62, 0.62, 0.60)}


def dom_col(fi):
    c = Counter(max(W_R1E[v].items(), key=lambda kv: kv[1])[0] for v in POLY[fi])
    return COL.get(C.GROUP_DIGIT.get(c.most_common(1)[0][0], "wrist"), (0.7, 0.7, 0.7))


cen = sum((V0[v] for v in list(COLLAR) + list(C1) + list(C2)), Vector()) / (len(COLLAR) + len(C1) + len(C2))
vw = fit(cen, (0.92, 0.25, 0.30), (0, 0, 1), [V0[v] for v in list(COLLAR) + list(C1) + list(C2)], 1.8)
cv = RASP.Canvas(W_, H_)
solid(cv, vw, V0, TRIS, dom_col)
for v in sorted(C2):
    vdot(cv, vw, V0, v, (0.30, 0.30, 0.30), 2)
for v in sorted(C1):
    vdot(cv, vw, V0, v, (0.10, 0.10, 0.10), 2)
for k in BND_IDS:
    a, b = EDGES[k]
    cv.line(vw.proj(V0[a]), vw.proj(V0[b]), (0.00, 1.00, 0.40), 3, 1.0)
for v in sorted(COLLAR):
    vdot(cv, vw, V0, v, (1.0, 1.0, 1.0), 3)
for r in TOPO["FULL_OPP_L3"]["edges"] + TOPO["CMC_OPP_30"]["edges"] + TOPO["CMC_MCP_L3"]["edges"]:
    a, b = r["v0"], r["v1"]
    cv.line(vw.proj(V0[a]), vw.proj(V0[b]), level_col(r["level"]), 2, 1.0)
RASP.text(cv, 24, 20, "R1E  TRANSITION WEIGHT FIELD (DOMINANT GROUP) WITH SEVERE EDGES OVERLAID", 3)
RASP.text(cv, 24, 60, "COLOUR = DOMINANT SKIN GROUP ; GREEN LINE = EXACT 16 R3 BOUNDARY EDGES", 2)
RASP.text(cv, 24, 84, "SEVERE EDGES OF CMC_OPP_30 + CMC_MCP_L3 + FULL_OPP_L3 (RED L0 / ORANGE L1 / YELLOW L2 / GREEN L3 / BLUE L4+)", 2)
RASP.text(cv, 24, 1050, "THUMB SALMON / INDEX BLUE / MIDDLE GREEN / RING PURPLE / LITTLE YELLOW / WRIST GREY", 2)
RASP.save(cv, "R1E_TRANSITION_WEIGHT_FIELD_WITH_SEVERE_EDGES.png", REND)
print("[REND] R1E_TRANSITION_WEIGHT_FIELD_WITH_SEVERE_EDGES.png", flush=True)


# =====================================================================================
# 6. strict bound vs observed max stretch
# =====================================================================================
cv = RASP.Canvas(W_, H_)
order = ["TH_IP_30", "TH_IP_45", "TH_MCP_45", "CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]
x0, x1 = 220, 1420
base, topy = 900, 220
scale = (base - topy) / 12.0
for gv in range(0, 13, 2):
    y = base - gv * scale
    cv.line((x0, y), (x1, y), (0.35, 0.35, 0.38), 1, 1.0)
    RASP.text(cv, 150, int(y) - 6, "%dx" % gv, 2)
y5 = base - 5.0 * scale
cv.line((x0, y5), (x1, y5), (1.0, 0.20, 0.20), 2, 1.0)
RASP.text(cv, x1 - 170, int(y5) - 20, "5X HARD GATE", 2, (1.0, 0.35, 0.35))
bw = (x1 - x0) / float(len(order))
for i, cid in enumerate(order):
    s = STRICT["per_pose"][cid]
    vals = [(s["max_OLD_CLAIM"], (0.75, 0.45, 0.25)),
            (s["max_STRICT_LOWER_BOUND"], (0.30, 0.65, 1.00)),
            (s["global_observed_max_stretch"], (1.00, 0.25, 0.25))]
    bx = x0 + i * bw + bw * 0.15
    wbar = bw * 0.70 / 3.0
    for j, (val, col) in enumerate(vals):
        h = max(1.0, val * scale)
        xx = bx + j * wbar
        for yy in range(int(base - h), int(base)):
            for dx in range(int(wbar) - 4):
                cv.px(xx + dx, yy, col, 0, 1.0)
    RASP.text(cv, int(bx) - 6, base + 12, cid[:9], 2)
    RASP.text(cv, int(bx) - 6, base + 34, "%.2f/%.2f/%.2f" % (vals[0][0], vals[1][0], vals[2][0]), 1)
RASP.text(cv, 24, 20, "R1E  OLD CLAIMED BOUND  vs  STRICT BOUND  vs  OBSERVED MAX STRETCH", 3)
RASP.text(cv, 24, 60, "ORANGE = OLD_CLAIM (uA+L)/L   BLUE = STRICT dt/L   RED = OBSERVED GLOBAL MAX", 2)
RASP.text(cv, 24, 84, "OLD CLAIM IS ALWAYS HIGHER THAN THE STRICT BOUND -> OLD_GEOMETRIC_IMPOSSIBILITY_CLAIM = INVALID / UNSUPPORTED", 2)
RASP.text(cv, 24, 1050, "STRICT BOUND > 5X ONLY FOR CMC_MCP_L3 (%s) AND FULL_OPP_L3 (%s); ON 3/10 AND 6/10 OF THE TESTED PATHS"
          % (STRICT["per_pose"]["CMC_MCP_L3"]["max_STRICT_LOWER_BOUND"],
             STRICT["per_pose"]["FULL_OPP_L3"]["max_STRICT_LOWER_BOUND"]), 2)
RASP.save(cv, "R1E_STRICT_BOUND_VS_OBSERVED.png", REND)
print("[REND] R1E_STRICT_BOUND_VS_OBSERVED.png", flush=True)
print("FEAS_RENDER_DONE")
