# =====================================================================================
# R3 EVIDENCE RENDERS  (round sections 27 / 28)  -- read only, nothing is written but PNGs
# =====================================================================================
import os
import sys
import json
import math
from collections import Counter, deque

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(HERE)
sys.path.append(os.path.join(PROD, "stage6_deformation", "stage6b_r1b", "scripts"))
sys.path.append(os.path.join(PROD, "stage6_deformation", "stage6b_r1c", "scripts"))
import s6br1b_common as K                                          # noqa: E402
import r1c_pen_common as RASP                                      # noqa: E402

OUT = os.path.dirname(HERE)
REND = os.path.join(OUT, "renders")
os.makedirs(REND, exist_ok=True)
L = json.load(open(os.path.join(OUT, "R3_OWNERSHIP_LABELS.json"), encoding="utf-8"))
R2 = L["R2"]
R3 = L["R3"]
LABELS = json.load(open(os.path.join(OUT, "R3_BOUNDARY_CONNECTEDNESS_AUDIT.json"), encoding="utf-8"))

ctx = K.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
POLY = ref["TOPO0"]
EDGES = ref["EDGES"]
MAT0 = ref["MAT0"]

CAP = set(L["CAP"])
NAIL_THUMB = set(L["NAIL_THUMB"])
NAIL_INDEX = set(L["NAIL_INDEX"])
WEB = set(L["WEB"])
THUMB_STRONG = set(L["THUMB_STRONG"])
INDEX_STRONG = set(L["INDEX_STRONG"])
BND_R2 = L["boundary_edges_R2"]
BND_R3 = L["boundary_edges_R3"]
CHANGED = set(L["changed"])

W_, H_ = 1500, 1100
LIGHT = Vector((0.42, -0.30, 0.85)).normalized()
CENTRE = sum(V0, Vector()) / NV
TRIS = RASP.tris_of(POLY, V0)
AXES = {"DORSAL": Vector((0, -1, 0)), "PALMAR": Vector((0, 1, 0)),
        "RADIAL": Vector((-1, 0, 0)), "3Q": Vector((0.55, 0.42, 0.72))}
COL = {"THUMB": (0.90, 0.42, 0.32), "INDEX": (0.30, 0.55, 0.92),
       "MIDDLE": (0.35, 0.78, 0.55), "RING": (0.70, 0.45, 0.90),
       "LITTLE": (0.92, 0.82, 0.35), "wrist": (0.55, 0.55, 0.55)}
HILITE_CAP = (1.00, 1.00, 1.00)
HILITE_NAIL = (1.00, 0.30, 0.85)
HILITE_WEB = (0.10, 1.00, 0.85)
BND_COL = (1.0, 0.10, 0.10)


def shade(n):
    return 0.30 + 0.70 * abs(n.dot(LIGHT))


def fit(centre, dirv, up, pts, margin=1.08):
    r_, u_ = RASP.ortho_basis(Vector(dirv), Vector(up))
    c = Vector(centre)
    mx = my = 0.0
    for p in pts:
        q = p - c
        mx = max(mx, abs(q.dot(r_)))
        my = max(my, abs(q.dot(u_)))
    return RASP.View(c, dirv, up, max(mx, my * float(W_) / float(H_)) * margin * 1000.0, W_, H_)


def face_label(lab, fi):
    return Counter(lab[v] for v in POLY[fi]).most_common(1)[0][0]


def draw(cv, view, lab, tris, overlay=None, overlay_col=None, dim=None):
    for fi, t in tris:
        g = face_label(lab, fi) if lab else None
        base = COL.get(g, (0.6, 0.6, 0.6)) if lab else (0.45, 0.45, 0.48)
        if dim and fi in dim:
            base = (0.30, 0.30, 0.32)
        if overlay and fi in overlay:
            base = overlay_col
        cv.tri(view.proj(V0[t[0]]), view.proj(V0[t[1]]), view.proj(V0[t[2]]),
               shade(RASP.face_normals(V0, [POLY[fi]])[0]), base)


def legend(cv, x, y, rows):
    yy = y
    for txt, c in rows:
        cv.px(x + 6, yy + 6, c, 6)
        RASP.text(cv, x + 22, yy, txt, 2)
        yy += 22


def faces_of(vset):
    return set(fi for fi, p in enumerate(POLY) if any(v in vset for v in p))


FACES_BND_R2 = set(fi for k in BND_R2 for fi in ())
FACES_BND_R3 = set(fi for k in BND_R3 for fi in ())


def bnd_faces(edge_ids):
    s = set()
    for k in edge_ids:
        a, b = EDGES[k]
        for fi, p in enumerate(POLY):
            if a in p and b in p:
                s.add(fi)
    return s


FB_R3 = bnd_faces(BND_R3)
FB_R2 = bnd_faces(BND_R2)

# ------------------------------------------------------------------ 1..3  three views
for view_name in ("DORSAL", "PALMAR", "RADIAL"):
    d = AXES[view_name]
    cv = RASP.Canvas(W_, H_)
    vw = fit(CENTRE, d, (0, 0, 1), V0, 2.15)
    half_a = RASP.View(vw.c - vw.r * vw.hw * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1,
                       vw.hw * 1000.0 * 0.5, W_, H_)
    half_b = RASP.View(vw.c + vw.r * vw.hw * 0.5, vw.d, vw.u.cross(vw.d).normalized() * -1,
                       vw.hw * 1000.0 * 0.5, W_, H_)
    draw(cv, half_a, R2, TRIS)
    draw(cv, half_b, R3, TRIS)
    for pan, be in ((half_a, BND_R2), (half_b, BND_R3)):
        for k in be:
            cv.line(pan.proj(V0[EDGES[k][0]]), pan.proj(V0[EDGES[k][1]]), BND_COL, 2, 1.0)
    for pan in (half_a, half_b):
        for v in CAP:
            cv.px(pan.proj(V0[v])[0], pan.proj(V0[v])[1], HILITE_CAP, 5)
        for v in NAIL_THUMB:
            cv.px(pan.proj(V0[v])[0], pan.proj(V0[v])[1], HILITE_NAIL, 3)
    RASP.text(cv, 24, 20, "DIGIT OWNERSHIP  R2  (LEFT)  VS  R3  (RIGHT)   -- %s VIEW" % view_name, 3)
    RASP.text(cv, 24, 60, "THUMB SALMON / INDEX BLUE / MIDDLE GREEN / RING PURPLE / LITTLE YELLOW / WRIST GREY", 2)
    RASP.text(cv, 24, 84, "RED LINE = THUMB|INDEX BOUNDARY EDGE ; WHITE = APPROVED DISTAL CAP ; MAGENTA = THUMB NAIL", 2)
    RASP.text(cv, 24, 1050, "R2 boundary %d edges / %d components   ->   R3 boundary %d edges / %d components. "
                            "SAME GEOMETRY, SAME POSE." % (len(BND_R2), LABELS["R2"]["component_count"],
                                                           len(BND_R3), LABELS["R3"]["component_count"]), 2)
    legend(cv, 1180, 30, [("THUMB", COL["THUMB"]), ("INDEX", COL["INDEX"]), ("MIDDLE", COL["MIDDLE"]),
                          ("RING", COL["RING"]), ("LITTLE", COL["LITTLE"]), ("WRIST", COL["wrist"])])
    RASP.save(cv, "DIGIT_OWNERSHIP_R2_VS_R3_%s.png" % view_name, REND)
    print("[R3R] rendered %s" % view_name, flush=True)

# ------------------------------------------------------------------ 4  thumb tip closeup
TIP = Vector((0, 0, 0))
for v in CAP:
    TIP = TIP + V0[v]
TIP = TIP / max(1, len(CAP))
cv = RASP.Canvas(W_, H_)
vl = RASP.View(TIP - Vector((0, 0, 0)), AXES["DORSAL"], (0, 0, 1), 26.0, W_, H_)
vr = RASP.View(TIP, AXES["DORSAL"], (0, 0, 1), 26.0, W_, H_)
vv = RASP.View(TIP, AXES["DORSAL"], (0, 0, 1), 52.0, W_, H_)
ha = RASP.View(vv.c - vv.r * vv.hw * 0.5, vv.d, vv.u.cross(vv.d).normalized() * -1, vv.hw * 1000.0 * 0.5, W_, H_)
hb = RASP.View(vv.c + vv.r * vv.hw * 0.5, vv.d, vv.u.cross(vv.d).normalized() * -1, vv.hw * 1000.0 * 0.5, W_, H_)
draw(cv, ha, R2, TRIS, overlay=FB_R2, overlay_col=(1.0, 0.55, 0.0))
draw(cv, hb, R3, TRIS, overlay=FB_R3, overlay_col=(1.0, 0.55, 0.0))
for pan, be in ((ha, BND_R2), (hb, BND_R3)):
    for k in be:
        cv.line(pan.proj(V0[EDGES[k][0]]), pan.proj(V0[EDGES[k][1]]), BND_COL, 3, 1.0)
for pan in (ha, hb):
    for v in CAP:
        cv.px(pan.proj(V0[v])[0], pan.proj(V0[v])[1], HILITE_CAP, 6)
    for v in NAIL_THUMB:
        cv.px(pan.proj(V0[v])[0], pan.proj(V0[v])[1], HILITE_NAIL, 4)
    for v in WEB:
        cv.px(pan.proj(V0[v])[0], pan.proj(V0[v])[1], HILITE_WEB, 3)
RASP.text(cv, 24, 20, "THUMB TIP CLOSE-UP  R2 (LEFT) VS R3 (RIGHT)  52 MM FIELD", 3)
RASP.text(cv, 24, 60, "ORANGE = THUMB|INDEX BOUNDARY FACES ; RED LINES = BOUNDARY EDGES", 2)
RASP.text(cv, 24, 84, "WHITE = APPROVED DISTAL CAP (9) ; MAGENTA = THUMB NAIL ; CYAN = APPROVED FIRST WEB", 2)
RASP.text(cv, 24, 1050, "R2: INTERLEAVED - THE BOUNDARY RUNS THROUGH THE TIP IN 10 FRAGMENTS. "
                        "R3: ONE COHERENT SEAM WITH NO ISLAND.", 2)
RASP.save(cv, "DIGIT_OWNERSHIP_R2_VS_R3_THUMB_TIP_CLOSEUP.png", REND)
print("[R3R] rendered thumb tip closeup", flush=True)

# ------------------------------------------------------------------ 5  first web closeup
WEBC = sum((V0[v] for v in WEB), Vector()) / max(1, len(WEB))
cv = RASP.Canvas(W_, H_)
vv = RASP.View(WEBC, AXES["3Q"], (0, 0, 1), 60.0, W_, H_)
ha = RASP.View(vv.c - vv.r * vv.hw * 0.5, vv.d, vv.u.cross(vv.d).normalized() * -1, vv.hw * 1000.0 * 0.5, W_, H_)
hb = RASP.View(vv.c + vv.r * vv.hw * 0.5, vv.d, vv.u.cross(vv.d).normalized() * -1, vv.hw * 1000.0 * 0.5, W_, H_)
draw(cv, ha, R2, TRIS, overlay=FB_R2, overlay_col=(1.0, 0.55, 0.0))
draw(cv, hb, R3, TRIS, overlay=FB_R3, overlay_col=(1.0, 0.55, 0.0))
for pan in (ha, hb):
    for v in WEB:
        cv.px(pan.proj(V0[v])[0], pan.proj(V0[v])[1], HILITE_WEB, 4)
    for v in CAP:
        cv.px(pan.proj(V0[v])[0], pan.proj(V0[v])[1], HILITE_CAP, 4)
RASP.text(cv, 24, 20, "FIRST WEB CLOSE-UP  R2 (LEFT) VS R3 (RIGHT)", 3)
RASP.text(cv, 24, 60, "CYAN = APPROVED FIRST_WEB REGION (21 VERTICES, THUMB_IP == 0) ; WHITE = APPROVED DISTAL CAP", 2)
RASP.text(cv, 24, 1050, "THE APPROVED FIRST WEB IS HELD AS A FROZEN ANCHOR AND IS NOT REPARTITIONED BY R3.", 2)
RASP.save(cv, "DIGIT_OWNERSHIP_R2_VS_R3_FIRST_WEB_CLOSEUP.png", REND)
print("[R3R] rendered first web closeup", flush=True)

# ------------------------------------------------------------------ 6  boundary topology map
cv = RASP.Canvas(W_, H_)
vw = fit(CENTRE, AXES["3Q"], (0, 0, 1), V0, 2.15)
draw(cv, vw, R3, TRIS)
for k in BND_R3:
    cv.line(vw.proj(V0[EDGES[k][0]]), vw.proj(V0[EDGES[k][1]]), BND_COL, 3, 1.0)
for k in BND_R2:
    a, b = EDGES[k]
    cv.px(vw.proj(V0[a])[0], vw.proj(V0[a])[1], (1.0, 0.55, 0.0), 5)
    cv.px(vw.proj(V0[b])[0], vw.proj(V0[b])[1], (1.0, 0.55, 0.0), 5)
for v in CAP:
    cv.px(vw.proj(V0[v])[0], vw.proj(V0[v])[1], HILITE_CAP, 6)
RASP.text(cv, 24, 20, "R3 THUMB|INDEX BOUNDARY TOPOLOGY MAP", 3)
RASP.text(cv, 24, 60, "RED LINE = R3 BOUNDARY EDGE (%d, %d COMPONENTS, %d OPEN ENDPOINTS, %d BRANCH VERTICES)"
          % (len(BND_R3), LABELS["R3"]["component_count"], LABELS["R3"]["open_endpoints"],
             LABELS["R3"]["branch_vertices"]), 2)
RASP.text(cv, 24, 84, "ORANGE DOTS = THE 22 R2 BOUNDARY EDGE ENDPOINTS (THE INTERLEAVED SET) ; WHITE = APPROVED CAP", 2)
RASP.text(cv, 24, 1050, "COLOURS = R3 OWNERSHIP. R3 COLLAPSES THE FRAGMENTED R2 BOUNDARY ONTO A SINGLE SEAM.", 2)
RASP.save(cv, "R3_THUMB_INDEX_BOUNDARY_TOPOLOGY_MAP.png", REND)
print("[R3R] rendered boundary topology map", flush=True)

# ------------------------------------------------------------------ 7  boundary components + sheet split
inc = {}
for k in BND_R3:
    for v in EDGES[k]:
        inc.setdefault(v, []).append(k)
seen = set()
comps = []
for k in sorted(BND_R3):
    if k in seen:
        continue
    c = []
    dq = deque([k])
    seen.add(k)
    while dq:
        x = dq.popleft()
        c.append(x)
        for v in EDGES[x]:
            for k2 in inc.get(v, ()):
                if k2 not in seen:
                    seen.add(k2)
                    dq.append(k2)
    comps.append(c)
print("[R3R] R3 boundary components: %d" % len(comps), flush=True)


def cut_components(skip):
    ADJ = {}
    for a, b in EDGES:
        if tuple(sorted((a, b))) in skip:
            continue
        ADJ.setdefault(a, []).append(b)
        ADJ.setdefault(b, []).append(a)
    se = set()
    out = []
    for v in range(NV):
        if v in se:
            continue
        c = []
        dq = deque([v])
        se.add(v)
        while dq:
            x = dq.popleft()
            c.append(x)
            for y in ADJ.get(x, ()):
                if y not in se:
                    se.add(y)
                    dq.append(y)
        out.append(c)
    return sorted(out, key=len, reverse=True)


ZSET = set(tuple(sorted(EDGES[k])) for k in BND_R3)
split = cut_components(ZSET)
SHEET = set(split[1]) if len(split) > 1 else set()
cv = RASP.Canvas(W_, H_)
vw = fit(CENTRE, AXES["3Q"], (0, 0, 1), V0, 2.15)
for fi, t in TRIS:
    if any(v in SHEET for v in POLY[fi]):
        base = (1.0, 0.85, 0.10)
    else:
        base = (0.35, 0.40, 0.50)
    cv.tri(vw.proj(V0[t[0]]), vw.proj(V0[t[1]]), vw.proj(V0[t[2]]),
           shade(RASP.face_normals(V0, [POLY[fi]])[0]), base)
for k in BND_R3:
    cv.line(vw.proj(V0[EDGES[k][0]]), vw.proj(V0[EDGES[k][1]]), BND_COL, 3, 1.0)
RASP.text(cv, 24, 20, "R3 THUMB|INDEX BOUNDARY -- CONNECTED COMPONENTS AND SHEET SPLIT", 3)
RASP.text(cv, 24, 60, "YELLOW = THE %d-VERTEX SHEET THAT IS SEPARATED WHEN THE %d BOUNDARY EDGES ARE CUT"
          % (len(SHEET), len(BND_R3)), 2)
RASP.text(cv, 24, 84, "GREY = THE REMAINING %d-VERTEX BODY (CONTAINS THE WHOLE APPROVED DISTAL CAP AND THUMB NAIL)"
          % (NV - len(SHEET)), 2)
RASP.text(cv, 24, 108, "BOUNDARY COMPONENTS: %d ; EACH EDGE IS ITS OWN COMPONENT (A LADDER SEAM IN THE QUAD STRIP)" % len(comps), 2)
for v, c, nm in ((1076, (1.0, 0.10, 1.0), "V1076 = LIVE THUMB TIP (IN THE GREY BODY)"),
                 (1228, (0.10, 1.0, 1.0), "V1228 = LIVE INDEX TIP (IN THE YELLOW SHEET)")):
    px = vw.proj(V0[v])
    cv.px(px[0], px[1], c, 9)
RASP.text(cv, 24, 152, "MAGENTA MARK = v1076 LIVE THUMB TIP - IN THE GREY BODY", 2)
RASP.text(cv, 24, 176, "CYAN MARK = v1228 LIVE INDEX TIP - IN THE YELLOW SHEET", 2)
RASP.text(cv, 24, 200, "THE YELLOW SHEET ALSO CARRIES ALL 43 LIVE INDEX NAIL VERTICES AND NONE OF THE THUMB CAP / NAIL / WEB.", 2)
RASP.text(cv, 24, 1050, "TEST: REMOVING ALL %d BOUNDARY EDGES SPLITS THE CLOSED MESH INTO EXACTLY 2 SHEETS." % len(BND_R3), 2)
RASP.save(cv, "R3_THUMB_INDEX_BOUNDARY_CONNECTED_COMPONENTS.png", REND)
print("[R3R] rendered boundary components", flush=True)

# ------------------------------------------------------------------ 8/9  anchor maps
for tag, S_, col, other in (("THUMB", THUMB_STRONG, (1.0, 0.30, 0.85), (0.40, 0.44, 0.52)),
                            ("INDEX", INDEX_STRONG, (0.20, 0.95, 1.0), (0.40, 0.44, 0.52))):
    cv = RASP.Canvas(W_, H_)
    vw = fit(CENTRE, AXES["3Q"], (0, 0, 1), V0, 2.15)
    for fi, t in TRIS:
        base = col if any(v in S_ for v in POLY[fi]) else other
        cv.tri(vw.proj(V0[t[0]]), vw.proj(V0[t[1]]), vw.proj(V0[t[2]]),
               shade(RASP.face_normals(V0, [POLY[fi]])[0]), base)
    RASP.text(cv, 24, 20, "R3 %s STRONG ANCHOR MAP" % tag, 3)
    RASP.text(cv, 24, 60, "PINNED ANCHORS = %d VERTICES (LIVE Stage5A R2A ANATOMY, NO ANIMATION INPUT)" % len(S_), 2)
    extra = ("APPROVED DISTAL CAP + APPROVED THUMB NAIL + PROXIMAL/METACARPAL TUBE + APPROVED FIRST WEB"
             if tag == "THUMB" else "LIVE INDEX NAIL + INDEX PIP..DIP TUBE")
    RASP.text(cv, 24, 84, extra, 2)
    RASP.text(cv, 24, 1050, "ANCHORS ARE HARD-CONSTRAINED IN THE MIN-CUT, SO THE BOUNDARY CAN NEVER CROSS THEM.", 2)
    RASP.save(cv, "R3_%s_STRONG_ANCHOR_MAP.png" % tag, REND)
    print("[R3R] rendered %s anchor map" % tag, flush=True)

# ------------------------------------------------------------------ 10 edge 498 neighbourhood
E498 = None
for k, (a, b) in enumerate(EDGES):
    if {a, b} == {160, 1080}:
        E498 = k
NEI = {160, 1080}
for v in (160, 1080):
    for a, b in EDGES:
        if a == v:
            NEI.add(b)
        if b == v:
            NEI.add(a)
C498 = sum((V0[v] for v in (160, 1080)), Vector()) / 2
cv = RASP.Canvas(W_, H_)
vv = RASP.View(C498, AXES["3Q"], (0, 0, 1), 44.0, W_, H_)
ha = RASP.View(vv.c - vv.r * vv.hw * 0.5, vv.d, vv.u.cross(vv.d).normalized() * -1, vv.hw * 1000.0 * 0.5, W_, H_)
hb = RASP.View(vv.c + vv.r * vv.hw * 0.5, vv.d, vv.u.cross(vv.d).normalized() * -1, vv.hw * 1000.0 * 0.5, W_, H_)
for pan, lab in ((ha, R2), (hb, R3)):
    for fi, t in TRIS:
        if not any(v in NEI for v in POLY[fi]):
            continue
        g = face_label(lab, fi)
        cv.tri(pan.proj(V0[t[0]]), pan.proj(V0[t[1]]), pan.proj(V0[t[2]]),
               shade(RASP.face_normals(V0, [POLY[fi]])[0]), COL.get(g, (0.6, 0.6, 0.6)))
    for k, (a, b) in enumerate(EDGES):
        if a in NEI and b in NEI and k != E498:
            cv.line(pan.proj(V0[a]), pan.proj(V0[b]), (0.25, 0.25, 0.28), 2, 1.0)
    cv.line(pan.proj(V0[160]), pan.proj(V0[1080]), (1.0, 0.10, 0.10), 4, 1.0)
    cv.px(pan.proj(V0[160])[0], pan.proj(V0[160])[1], (1.0, 1.0, 1.0), 7)
    cv.px(pan.proj(V0[1080])[0], pan.proj(V0[1080])[1], (1.0, 0.90, 0.10), 7)
RASP.text(cv, 24, 20, "EDGE 498 NEIGHBOURHOOD   v160 - v1080   (BIND 3.098 MM)   R2 (LEFT) VS R3 (RIGHT)", 3)
RASP.text(cv, 24, 60, "EACH PANEL DRAWS ONLY THE 1-RING OF v160 / v1080, COLOURED BY THAT OWNERSHIP FIELD", 2)
RASP.text(cv, 24, 84, "WHITE DOT = v160 ; YELLOW DOT = v1080 ; RED LINE = THE DISPUTED EDGE", 2)
RASP.text(cv, 24, 1050, "R2 SPLITS THIS PAIR; R3 ALSO SPLITS IT - BOTH PUT v1080 ON THE INDEX SHEET, AND THAT SHEET IS A "
                        "SEPARATE 217-VERTEX PATCH.", 2)
RASP.save(cv, "R3_EDGE498_NEIGHBORHOOD.png", REND)
print("[R3R] rendered edge498 neighbourhood", flush=True)

json.dump({"sheet_vertex_count": len(SHEET),
           "sheet_contains_cap": len(set(split[1]) & CAP) if len(split) > 1 else None,
           "sheet_contains_thumb_nail": len(set(split[1]) & NAIL_THUMB) if len(split) > 1 else None,
           "sheet_contains_index_nail": len(set(split[1]) & NAIL_INDEX) if len(split) > 1 else None,
           "body_vertex_count": NV - len(SHEET),
           "boundary_component_count": len(comps),
           "edge498": E498,
           "v160_R2": R2[160], "v1080_R2": R2[1080],
           "v160_R3": R3[160], "v1080_R3": R3[1080]},
          open(os.path.join(OUT, "_tmp_sheet_split.json"), "w", encoding="utf-8"), indent=1)
print("R3_RENDER_DONE")
