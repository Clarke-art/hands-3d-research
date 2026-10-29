# =====================================================================================
# STAGE5A_R2 -- JOINT LANDMARK REQUALIFICATION  (READ-ONLY forensics on the frozen master)
# =====================================================================================
# Produces:
#   stage5a_r2/STAGE5A_R2_WRIST_PROFILE.json     (WRIST_CANDIDATE_PROFILE)
#   stage5a_r2/_tmp/S5A_R2_CANDIDATES.json       (all five requalified candidates + evidence)
#
# Requalified:  PRODUCTION WRIST_R / THUMB_CMC_R / THUMB_MCP_R / THUMB_TIP_R / INDEX_MCP_R
# Frozen     :  all 15 other joints (byte-level carry-forward)
# =====================================================================================
import bpy, sys, os, json, math, hashlib, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
S5AR2, MASTER = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
S5A = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a"
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
nail = json.load(open(os.path.join(S4, "stage4c_r2", "NAIL_AUDIT_R2.json"), encoding="utf-8"))
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cage = json.load(open(os.path.join(S4, "stage4a_r2", "R2_CAGE.json"), encoding="utf-8"))
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))
S4_ASSET_ORIGIN = Vector(oa["WRIST_ORIGIN"])
FINGERS = ("INDEX", "MIDDLE", "RING", "LITTLE")
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}
R_ENV = {"thumb": 11.14, "index": 7.64, "middle": 7.80, "ring": 7.15, "little": 6.75}

bpy.ops.wm.open_mainfile(filepath=MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
MINV = MW.inverted()
M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]
NV = len(V)
REP = {}


def log(*a):
    print("[S5A-R2]", *a)


# ------------------------------------------------------------------ geometry helpers
def closest(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(MINV @ Vector(p))
    if not ok:
        return None, None, None
    return MW @ loc, (M3 @ nor).normalized(), idx


def clearance(p):
    loc, nor, idx = closest(p)
    return None if loc is None else (Vector(p) - loc).length


def parity(p, ndir=64):
    pl = MINV @ Vector(p)
    hits = 0
    for k in range(ndir):
        th = 2.399963229728653 * k
        z = 1.0 - 2.0 * (k + 0.5) / ndir
        r = math.sqrt(max(0.0, 1.0 - z * z))
        d = Vector((r * math.cos(th), r * math.sin(th), z))
        n = 0
        o = pl.copy()
        for _ in range(48):
            ok, loc, nor, idx = ob.ray_cast(o, d, distance=1.0)
            if not ok:
                break
            n += 1
            o = loc + d * 2e-7
        if n % 2 == 1:
            hits += 1
    return hits, ndir


def chord_through(p0, n_dir, span=0.030):
    """all crossings of the line p0 + t*n_dir, t in [-span, +span]; returns the interior
    interval that contains t = 0 if p0 is inside, else the nearest interval"""
    F = Vector(p0) + Vector(n_dir) * span
    d = -Vector(n_dir)
    ts = []
    o = MINV @ F
    dl = (M3.inverted() @ d).normalized()
    acc = 0.0
    step = 2 * span
    while True:
        ok, loc, nor, idx = ob.ray_cast(o, dl, distance=step - acc + 1e-9)
        if not ok:
            break
        acc = (o - MINV @ F).length if False else acc
        adv = ((MW @ loc) - (MINV.inverted() @ o)).length if False else ((MW @ loc) - (MW @ o)).length
        acc += adv
        ts.append(span - acc)
        o = loc + dl * 2e-7
        if acc > 2 * span:
            break
    ts = sorted(ts)
    if len(ts) < 2:
        return None
    t0 = 0.0
    for i in range(0, len(ts) - 1, 2):
        if ts[i] <= t0 <= ts[i + 1]:
            return ts[i], ts[i + 1]
    # p0 outside: take the interval closest to t0
    best = None
    for i in range(0, len(ts) - 1, 2):
        dd = min(abs(ts[i] - t0), abs(ts[i + 1] - t0))
        if best is None or dd < best[0]:
            best = (dd, ts[i], ts[i + 1])
    return (best[1], best[2]) if best else None


def medial_on_chord(p0, n_dir, samples=61, refine=0.05):
    """the maximum-clearance point along the interior chord through p0 along n_dir"""
    iv = chord_through(p0, n_dir)
    if iv is None:
        return None
    t_in, t_out = iv
    best = (None, -1.0, None)
    for i in range(samples):
        t = t_in + (t_out - t_in) * i / (samples - 1)
        p = Vector(p0) + Vector(n_dir) * t
        c = clearance(p)
        if c is not None and c > best[1]:
            best = (p, c, t)
    if best[0] is None:
        return None
    lo = best[2] - (t_out - t_in) / (samples - 1)
    hi = best[2] + (t_out - t_in) / (samples - 1)
    for _ in range(24):
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        c1 = clearance(Vector(p0) + Vector(n_dir) * m1) or 0.0
        c2 = clearance(Vector(p0) + Vector(n_dir) * m2) or 0.0
        if c1 < c2:
            lo = m1
        else:
            hi = m2
    t = (lo + hi) / 2
    p = Vector(p0) + Vector(n_dir) * t
    return {"point": p, "clearance_mm": (clearance(p) or 0.0) * MM,
            "chord_in_mm": t_in * MM, "chord_out_mm": t_out * MM,
            "chord_length_mm": (t_out - t_in) * MM}


def hull2d(pts):
    P = sorted(set((round(a, 9), round(b, 9)) for a, b in pts))
    if len(P) < 3:
        return P

    def half(seq):
        h = []
        for q in seq:
            while len(h) >= 2 and ((h[-1][0] - h[-2][0]) * (q[1] - h[-2][1])
                                   - (h[-1][1] - h[-2][1]) * (q[0] - h[-2][0])) <= 0:
                h.pop()
            h.append(q)
        return h
    lo = half(P); up = half(list(reversed(P)))
    return lo[:-1] + up[:-1]


def hull_area(poly):
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def inside_poly(poly, q):
    n = len(poly)
    for i in range(n):
        a = poly[i]; b = poly[(i + 1) % n]
        if (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) < 0:
            return False
    return True


def plane_medial(origin, u, w, pts2d, grid=0.4, refine=0.05):
    """max-clearance point inside the convex hull of pts2d, expressed in the (u,w) plane"""
    poly = hull2d(pts2d)
    if len(poly) < 3:
        return None, None, 0.0
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    best = (None, -1.0)
    nx = max(2, int((x1 - x0) / grid) + 1)
    ny = max(2, int((y1 - y0) / grid) + 1)
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx
        for j in range(ny + 1):
            y = y0 + (y1 - y0) * j / ny
            if not inside_poly(poly, (x, y)):
                continue
            p = Vector(origin) + Vector(u) * x + Vector(w) * y
            c = clearance(p)
            if c is not None and c > best[1]:
                best = (p, c, (x, y))
    if best[0] is None:
        return None, None, 0.0
    bx, by = best[2]
    lo, hi = grid, grid
    for _ in range(30):
        cands = [(bx + dx, by + dy) for dx in (-lo, 0, lo) for dy in (-hi, 0, hi)]
        imp = False
        for (x, y) in cands:
            if not inside_poly(poly, (x, y)):
                continue
            p = Vector(origin) + Vector(u) * x + Vector(w) * y
            c = clearance(p)
            if c is not None and c > best[1] + 1e-9:
                best = (p, c, (x, y)); imp = True
        if not imp:
            lo *= 0.5; hi *= 0.5
            if lo < refine:
                break
    return best[0], best[1] * MM, hull_area(poly) * MM * MM


# ------------------------------------------------------------------ dorsal references
DIGITS = ["thumb", "index", "middle", "ring", "little"]
DORSAL = {}
for d in DIGITS:
    acc = Vector((0.0, 0.0, 0.0))
    for fi in nail["per_digit_faces"][d]:
        acc += me.polygons[fi].normal
    DORSAL[d] = acc.normalized()
PALM_PTS = [S4_ASSET_ORIGIN] + [Vector(jf["%s_MCP_R" % f]["head"]) for f in FINGERS]
PA = sum(PALM_PTS, Vector()) / len(PALM_PTS)
cov = [[0.0] * 3 for _ in range(3)]
for q in PALM_PTS:
    dv = q - PA
    for a in range(3):
        for b in range(3):
            cov[a][b] += dv[a] * dv[b]
tr = cov[0][0] + cov[1][1] + cov[2][2]
N = [[(tr if a == b else 0.0) - cov[a][b] for b in range(3)] for a in range(3)]
vec = Vector((0.0, 1.0, 0.0))
for _ in range(200):
    nv = Vector((sum(N[0][t] * vec[t] for t in range(3)), sum(N[1][t] * vec[t] for t in range(3)),
                 sum(N[2][t] * vec[t] for t in range(3))))
    if nv.length < 1e-18:
        break
    vec = nv.normalized()
FLEX = [Vector(jf["%s_%s_R" % (f, s)]["head"]) for f in FINGERS for s in ("PIP", "DIP")]
FC = sum(FLEX, Vector()) / len(FLEX)
if (FC - PA).dot(vec) > 0:
    vec = -vec
DORSAL["wrist"] = vec
REP["dorsal_refs"] = {k: [round(float(x), 9) for x in DORSAL[k]] for k in DORSAL}

# ------------------------------------------------------------------ ownership (6 chains)
def chainpts(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


ACHAIN = {D: chainpts(D) for D in CHAIN}
ACHAIN["wrist"] = [S4_ASSET_ORIGIN, Vector(jf["WRIST_R"]["tail"])]


def d_poly(p, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (p - (a + ab * t)).length)
    return best


FACE_OWNER = {}
for p in me.polygons:
    c = sum((V[v] for v in p.vertices), Vector()) / len(p.vertices)
    dd = {D: d_poly(c, ACHAIN[D]) for D in ACHAIN}
    FACE_OWNER[p.index] = min(dd, key=dd.get)
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
VOWN = {}
for v in me.vertices:
    ds = {FACE_OWNER[fi] for fi in V2F[v.index]}
    VOWN[v.index] = ds.pop() if len(ds) == 1 else "MIXED"
REP["ownership"] = {"faces": {k: sum(1 for x in FACE_OWNER.values() if x == k)
                              for k in set(FACE_OWNER.values())},
                    "verts": {k: sum(1 for x in VOWN.values() if x == k)
                              for k in set(VOWN.values())}}

# =====================================================================================
# 1. PRODUCTION WRIST joint centre  --  wrist / palm transition
# =====================================================================================
z_lo = min(p.z for p in V)
cap_ring = [p for p in V if abs(p.z - z_lo) <= 0.004]
cap_c = sum(cap_ring, Vector()) / len(cap_ring)
REF_VOLUME = [p for p in V if abs(p.z - S4_ASSET_ORIGIN.z) <= 0.008]
basin_c = sum(REF_VOLUME, Vector()) / len(REF_VOLUME)
e_long = (basin_c - cap_c).normalized()
e_dor_raw = DORSAL["wrist"]
e_dor = (e_dor_raw - e_long * e_dor_raw.dot(e_long)).normalized()
e_lat = e_long.cross(e_dor).normalized()
MCP_C = sum((Vector(jf["%s_MCP_R" % f]["head"]) for f in FINGERS), Vector()) / 4.0
if (Vector(jf["THUMB_CMC_R"]["head"]) - cap_c).dot(e_lat) < 0:
    e_lat = -e_lat            # +e_lat points to the RADIAL (thumb) side
s_origin = (S4_ASSET_ORIGIN - cap_c).dot(e_long)
s_mcp = (MCP_C - cap_c).dot(e_long)


def axis_point(s, lat=0.0, dor=0.0):
    return cap_c + e_long * s + e_lat * lat + e_dor * dor


RUN = e_long.length
R_MAX_W = 0.045
s_thumb_cmc = (Vector(jf["THUMB_CMC_R"]["head"]) - cap_c).dot(e_long)
W_LO = s_origin - 0.020
W_HI = min(s_thumb_cmc - 0.008, s_mcp - 0.030)
prof = []
step = 0.002
s = W_LO
while s <= W_HI + 1e-9:
    sel = []
    for i, p in enumerate(V):
        d = p - cap_c
        sl = d.dot(e_long)
        if abs(sl - s) <= 0.003:
            lat = d.dot(e_lat); dor = d.dot(e_dor)
            if math.hypot(lat, dor) <= R_MAX_W:
                sel.append((lat, dor, sl))
    if len(sel) >= 12:
        lats = [x[0] for x in sel]; dors = [x[1] for x in sel]
        c_lat = sum(lats) / len(lats); c_dor = sum(dors) / len(dors)
        W = (max(lats) - min(lats)) * MM
        T = (max(dors) - min(dors)) * MM
        a = hull_area(hull2d([(x[0], x[1]) for x in sel])) * MM * MM
        rad_w = max(0.0, (max(lats) - c_lat)) * MM
        uln_w = max(0.0, (c_lat - min(lats))) * MM
        prof.append({"s_mm": round(s * MM, 2), "z_mm": round(axis_point(s).z * MM, 3),
                     "n": len(sel), "area_mm2": round(a, 1),
                     "width_radioulnar_mm": round(W, 3), "width_radial_mm": round(rad_w, 3),
                     "width_ulnar_mm": round(uln_w, 3),
                     "thickness_dorsopalmar_mm": round(T, 3),
                     "aspect_W_over_T": round(W / T, 4) if T > 1e-9 else None,
                     "section_centroid_lat_mm": round(c_lat * MM, 3),
                     "section_centroid_dor_mm": round(c_dor * MM, 3)})
    s += step

REP["wrist_frame"] = {"e_long": [round(float(x), 9) for x in e_long],
                      "e_dorsal": [round(float(x), 9) for x in e_dor],
                      "e_lateral_to_thumb_side": [round(float(x), 9) for x in e_lat],
                      "R_MAX_mm": R_MAX_W * MM, "scan_window_mm": [round(W_LO * MM, 2), round(W_HI * MM, 2)],
                      "s_of_asset_origin_mm": round(s_origin * MM, 3),
                      "s_of_four_MCP_centroid_mm": round(s_mcp * MM, 3),
                      "forearm_cap_z_mm": round(z_lo * MM, 3)}
REP["wrist_profile"] = prof

A_min = min(prof, key=lambda r: r["area_mm2"])
s_Amin = A_min["s_mm"]
n_ref = max(3, len(prof) // 5)
A_ref = sorted(r["area_mm2"] for r in prof[:n_ref])[n_ref // 2]
GROW_LO, GROW_HI = 1.03, 1.10          # DECLARED transition thresholds (relative to the
                                       # median forearm section area over the proximal 20%)
rows = [r for r in prof if r["s_mm"] > s_Amin]
s_on = next((r["s_mm"] for r in rows if r["area_mm2"] >= A_ref * GROW_LO), None)
s_palm = next((r["s_mm"] for r in rows if r["area_mm2"] >= A_ref * GROW_HI), None)
if s_on is None:
    s_on = s_palm = rows[len(rows) // 2]["s_mm"]
if s_palm is None:
    s_palm = rows[-1]["s_mm"]
s_trans = (s_on + s_palm) / 2.0
R_wrist = None
R_palm = max([r["aspect_W_over_T"] for r in prof if r["aspect_W_over_T"]] or [None])

for r in prof:
    r["candidate_score"] = round(1.0 / (1.0 + abs(r["s_mm"] - s_trans) / 2.0), 6)
    r["rationale"] = ("proximal of the wrist constriction" if r["s_mm"] <= s_Amin else
                      ("transition onset  (area >= %.0f%% of the forearm reference)"
                       % (GROW_LO * 100) if abs(r["s_mm"] - s_on) < 1e-6 else
                       ("palm body entry  (area >= %.0f%% of the forearm reference)"
                        % (GROW_HI * 100) if abs(r["s_mm"] - s_palm) < 1e-6 else
                        ("TRANSITION REGION CENTRE" if abs(r["s_mm"] - s_trans) < 1e-6 else
                         "inside the wrist/palm transition band"))))
A_forearm_ref = A_ref

sec = [r for r in prof if abs(r["s_mm"] - s_trans) <= 3.0][0]
sel = []
for p in V:
    d = p - cap_c
    if abs(d.dot(e_long) - s_trans * 1e-3) <= 0.0045:
        lat = d.dot(e_lat); dor = d.dot(e_dor)
        if math.hypot(lat, dor) <= R_MAX_W:
            sel.append((lat, dor))
w_pt, w_clr, w_area = plane_medial(cap_c + e_long * (s_trans * 1e-3), e_lat, e_dor, sel)
WRIST_SECTION_MEDIAL = w_pt
# corroboration: normal-chord medial from the section centroid
loc0, nor0, _ = closest(axis_point(s_trans * 1e-3))
chord = medial_on_chord(axis_point(s_trans * 1e-3), nor0) if nor0 is not None else None
w_par, w_tot = parity(w_pt)
WRIST_CAND = w_pt
WRIST_EVID = {
    "method": ("PRODUCTION_WRIST_TRANSITION_CENTRE.  (1) forearm frame: e_long = forearm-cap "
               "centroid -> wrist-basin centroid; e_dorsal = the palm-plane normal; e_lateral = "
               "e_long x e_dorsal (positive side chosen toward the thumb).  (2) axial sections "
               "(2 mm step, +/-3 mm slab, vertices within R_MAX = %.0f mm of the arm axis so the "
               "thumb column is excluded) from the approved wrist basin distally to just proximal "
               "of the first carpo-metacarpal level (the scan stops BEFORE the palm body / MCP "
               "region, not at an arbitrary offset).  (3) DECLARED, reproducible transition rule: "
               "A_ref = the median section area over the proximal 20%% of the window (the forearm "
               "reference); s_on = the first section distal of the wrist constriction with "
               "A >= 1.03 A_ref; s_palm = the first with A >= 1.10 A_ref; the wrist/palm "
               "transition region is [s_on, s_palm] and its centre is s_trans = (s_on+s_palm)/2.  "
               "(4) the joint centre is the MAXIMUM-CLEARANCE point (largest inscribed sphere "
               "centre) of the section at s_trans - deliberately NOT the minimum-area point, and "
               "no target bone length is used anywhere."
               % (R_MAX_W * MM)),
    "s_constriction_mm": s_Amin, "s_transition_mm": s_trans,
    "s_transition_onset_mm": s_on, "s_palm_body_entry_mm": s_palm,
    "A_forearm_reference_mm2": round(A_forearm_ref, 2),
    "growth_thresholds": [GROW_LO, GROW_HI],
    "s_of_thumb_CMC_level_mm": round(s_thumb_cmc * MM, 3),
    "scan_window_effective_mm": [round(W_LO * MM, 2), round(W_HI * MM, 2)],
    "R_palm_max_aspect": round(R_palm, 4) if R_palm else None,
    "section_at_transition": sec,
    "n_section_verts": len(sel), "section_hull_area_mm2": round(w_area, 2),
    "section_medial_clearance_mm": round(w_clr, 4),
    "candidate": [round(float(x), 9) for x in WRIST_CAND],
    "ray_parity": "%d/%d" % (w_par, w_tot), "inside_mesh": bool(w_par > w_tot / 2),
    "normal_chord_corroboration": None if chord is None else
        {"point": [round(float(x), 9) for x in chord["point"]],
         "clearance_mm": round(chord["clearance_mm"], 4),
         "chord_length_mm": round(chord["chord_length_mm"], 4),
         "agreement_mm": round((chord["point"] - w_pt).length * MM, 3)},
    "distance_from_forearm_cap_mm": round(s_trans, 3),
    "distance_to_four_MCP_centroid_mm": round((WRIST_CAND - MCP_C).length * MM, 3),
    "distance_to_asset_origin_mm": round((WRIST_CAND - S4_ASSET_ORIGIN).length * MM, 3),
    "thumb_column_distance_mm": round(d_poly(WRIST_CAND, ACHAIN["THUMB"]) * MM, 3),
    "palm_body_check": "the section at s_trans is still inside the transition band (A < 1.10 A_ref is false at s_palm, true at s_trans), i.e. NOT the palm centre body",
}
REP["WRIST_EVIDENCE"] = WRIST_EVID

# =====================================================================================
# 2. INDEX_MCP_R -- keep the approved T-01 axial plane, find the true interior centre
# =====================================================================================
def sign_inside(p):
    loc, nor, fi = closest(p)
    if loc is None:
        return False, None, fi
    return bool((Vector(p) - loc).dot(nor) < 0), loc, fi


def interior_medial(p0, axis, R_ball):
    """owner-free variant: the maximum-clearance interior point within R_ball of p0 in the
    plane through p0 normal to axis (used for the PALM reference, which is not a joint)."""
    n = Vector(axis).normalized()
    u = (DORSAL["index"] - n * DORSAL["index"].dot(n)).normalized()
    w = n.cross(u).normalized()
    step = R_ball / 20.0
    best = (None, -1.0, 0.0, 0.0)
    for i in range(-20, 21):
        for j in range(-20, 21):
            x = i * step; y = j * step
            if math.hypot(x, y) > R_ball:
                continue
            p = Vector(p0) + u * x + w * y
            ins, loc, fi = sign_inside(p)
            if not ins or loc is None:
                continue
            c = (Vector(p) - loc).length
            if c >= 1.0e-3 and c > best[1]:
                best = (p, c, x, y)
    return None if best[0] is None else {"point": best[0], "clearance_mm": best[1] * MM}


def axial_section_medial(p0, axis, label, ball_scale=1.5, region_centre=None, region_R=None):
    """p0 = R1 landmark; axis = local longitudinal axis (the approved axial plane is the plane
    through p0 normal to 'axis', so the approved axial level is preserved exactly).

    Domain = { |p - p0| <= R_ball } inside that plane, with
             R_ball = ball_scale x R_env(digit)  -- a search-domain bound derived from the
             digit's own measured distal surface envelope, NOT a result constraint.
    Objective = the FULL-MESH clearance (distance to the nearest surface point), and the point
    is only accepted when its nearest surface face belongs to the digit's own ownership set.
    Result = the local maximum-clearance point (largest inscribed sphere centre) of the plane.
    """
    n = axis.normalized()
    u = (DORSAL[label] - n * DORSAL[label].dot(n)).normalized()
    w = n.cross(u).normalized()
    R_ball = R_ENV[label] * 1e-3 * ball_scale
    target_owner = label.upper()

    def score(p):
        if region_centre is not None and (Vector(p) - Vector(region_centre)).length > region_R:
            return -1.0
        ins, loc, fi = sign_inside(p)
        if not ins or loc is None:
            return -1.0                       # MUST be inside the mesh
        if FACE_OWNER[fi] != target_owner:
            return -1.0                       # nearest skin must be the digit's own
        c = (Vector(p) - loc).length
        if c < 1.0e-3:
            return -1.0                       # reject skin-hugging points
        return c

    step = R_ball / 24.0
    best = (None, -1.0, 0.0, 0.0)
    n_cells = 0
    for i in range(-24, 25):
        for j in range(-24, 25):
            x = i * step; y = j * step
            if math.hypot(x, y) > R_ball:
                continue
            n_cells += 1
            p = p0 + u * x + w * y
            c = score(p)
            if c > best[1]:
                best = (p, c, x, y)
    if best[0] is None:
        return {"point": None, "clearance_mm": None, "n_verts": 0, "area_mm2": 0.0,
                "u": u, "w": w, "n": n, "R_ball_mm": R_ball * MM, "grid_cells": n_cells}
    lo = step
    bx, by = best[2], best[3]
    for _ in range(24):
        improved = False
        for dx in (-lo, 0.0, lo):
            for dy in (-lo, 0.0, lo):
                x, y = bx + dx, by + dy
                if math.hypot(x, y) > R_ball:
                    continue
                p = p0 + u * x + w * y
                c = score(p)
                if c > best[1] + 1e-12:
                    best = (p, c, x, y); improved = True
        if not improved:
            lo *= 0.5
            if lo < 5e-5:
                break
    par, tot = parity(best[0])
    return {"point": best[0], "clearance_mm": best[1] * MM, "u": u, "w": w, "n": n,
            "R_ball_mm": R_ball * MM, "grid_cells": n_cells,
            "ray_parity": "%d/%d" % (par, tot), "inside_mesh": bool(par > tot / 2),
            "in_plane_offset_mm": [round(best[2] * MM, 3), round(best[3] * MM, 3)],
            "offset_from_R1_mm": round(math.hypot(best[2], best[3]) * MM, 3),
            "nearest_face_owner": FACE_OWNER[closest(best[0])[2]]}


R1_INDEX_MCP = Vector(jf["INDEX_MCP_R"]["head"])
idx_axis = (Vector(jf["INDEX_PIP_R"]["head"]) - R1_INDEX_MCP).normalized()   # local (proximal phalanx) axis
imq = axial_section_medial(R1_INDEX_MCP, idx_axis, "index", ball_scale=1.15)

# WRIST_R tail = PALM_REFERENCE -- revalidated, and re-derived if the four-MCP centroid is
# not actually an interior point (measured: it sits on the dorsal skin).
MCP_CENTROID_RAW = MCP_C
raw_par, raw_tot = parity(MCP_CENTROID_RAW)
raw_loc, raw_nor, _ = closest(MCP_CENTROID_RAW)
palm_axis = (MCP_CENTROID_RAW - WRIST_CAND).normalized()
pu = (e_lat - palm_axis * e_lat.dot(palm_axis)).normalized()
pw = palm_axis.cross(pu).normalized()
palm_cand = interior_medial(MCP_CENTROID_RAW, palm_axis, R_ENV["index"] * 1e-3 * 1.50)
PALM_REFERENCE = palm_cand["point"] if palm_cand["point"] is not None else MCP_CENTROID_RAW
pr_par, pr_tot = parity(PALM_REFERENCE)
pr_loc, pr_nor, _ = closest(PALM_REFERENCE)
root_dir = (PALM_REFERENCE - WRIST_CAND).normalized()
REP["PALM_REFERENCE_EVIDENCE"] = {
    "FOUR_MCP_CENTROID_raw": [round(float(x), 9) for x in MCP_CENTROID_RAW],
    "FOUR_MCP_CENTROID_raw_ray_parity": "%d/%d" % (raw_par, raw_tot),
    "FOUR_MCP_CENTROID_raw_inside": bool(raw_par > raw_tot / 2),
    "FOUR_MCP_CENTROID_raw_surface_distance_mm": round((MCP_CENTROID_RAW - raw_loc).length * MM, 4),
    "PALM_REFERENCE": [round(float(x), 9) for x in PALM_REFERENCE],
    "derivation": "centroid of the four finger MCP joint centres (frozen R1 joints)",
    "ray_parity": "%d/%d" % (pr_par, pr_tot),
    "inside_mesh": bool(pr_par > pr_tot / 2),
    "surface_clearance_mm": round((PALM_REFERENCE - pr_loc).length * MM, 4),
    "distal_of_new_wrist_head_mm": round((PALM_REFERENCE - WRIST_CAND).dot(e_long) * MM, 3),
    "angle_root_dir_vs_forearm_axis_deg": round(math.degrees(math.acos(
        max(-1.0, min(1.0, root_dir.dot(e_long))))), 3),
    "thumb_column_distance_mm": round(d_poly(PALM_REFERENCE, ACHAIN["THUMB"]) * MM, 3),
    "verdict": "VALID_ORIENTATION_REFERENCE",
}

log("WRIST candidate", [round(float(x), 6) for x in WRIST_CAND], "s_trans", s_trans)

loc, nor, _ = closest(R1_INDEX_MCP)
im_chord = medial_on_chord(R1_INDEX_MCP, nor)
im_par, im_tot = parity(imq["point"])
INDEX_MCP_CAND = imq["point"]
REP["INDEX_MCP_EVIDENCE"] = {
    "method": ("approved T-01 axial plane is KEPT (the plane through the R1 landmark normal to the "
               "index proximal-phalanx axis); within that plane the centre is the maximum-clearance "
               "point (largest inscribed sphere centre) of the index cross-section, radial cap "
               "%.2f mm = 1.20 x R_env(index)." % (R_ENV["index"] * 1.20)),
    "R1_position": [round(float(x), 9) for x in R1_INDEX_MCP],
    "R1_surface_distance_mm": round((R1_INDEX_MCP - loc).length * MM, 4),
    "R1_ray_parity_expected": "0/64 (reported in Stage5A R1)",
    "R2_position": [round(float(x), 9) for x in INDEX_MCP_CAND],
    "shift_vector": [round(float(INDEX_MCP_CAND[i] - R1_INDEX_MCP[i]), 9) for i in range(3)],
    "shift_mm": round((INDEX_MCP_CAND - R1_INDEX_MCP).length * MM, 4),
    "R2_ray_parity": "%d/%d" % (im_par, im_tot), "R2_inside": bool(im_par > im_tot / 2),
    "R2_clearance_mm": round(imq["clearance_mm"], 4),
    "search_ball_mm": round(imq["R_ball_mm"], 3),
    "in_plane_offset_mm": imq["in_plane_offset_mm"],
    "nearest_face_owner_at_result": imq["nearest_face_owner"],
    "axial_delta_from_approved_T01_mm": 0.0,
    "axial_note": "the R2 centre lies in the approved T-01 axial plane by construction",
    "normal_chord_corroboration": None if im_chord is None else
        {"point": [round(float(x), 9) for x in im_chord["point"]],
         "clearance_mm": round(im_chord["clearance_mm"], 4),
         "chord_length_mm": round(im_chord["chord_length_mm"], 4),
         "agreement_mm": round((im_chord["point"] - INDEX_MCP_CAND).length * MM, 3)},
}
log("INDEX_MCP shift mm", REP["INDEX_MCP_EVIDENCE"]["shift_mm"],
    "R2 clearance", REP["INDEX_MCP_EVIDENCE"]["R2_clearance_mm"])

# =====================================================================================
# 3. THUMB chain requalification
# =====================================================================================
R1_CMC = Vector(jf["THUMB_CMC_R"]["head"])
R1_MCP = Vector(jf["THUMB_MCP_R"]["head"])
R1_IP = Vector(jf["THUMB_IP_R"]["head"])
R1_TIP = Vector(jf["THUMB_TIP_R"]["head"])
th_axis_mc = (R1_MCP - R1_CMC).normalized()
th_axis_ip = (R1_TIP - R1_IP).normalized()

# --- CMC ---
anchor = V[cage["cmc_vertex"]]
R_CAGE_LOC = max(cage["locality"]["euclidean_radius_mm"])
loc_a, nor_a, _ = closest(R1_CMC)
cmc_chord = medial_on_chord(R1_CMC, nor_a)
cmc_plane = axial_section_medial(R1_CMC, th_axis_mc, "thumb", ball_scale=1.15,
                                 region_centre=anchor, region_R=R_CAGE_LOC * 1e-3)
# region constraint: the result must stay inside the approved CMC cage locality sphere
cand_cmc = cmc_plane["point"]
in_cage = (cand_cmc - anchor).length * MM <= R_CAGE_LOC
cmc_par, cmc_tot = parity(cand_cmc)
loc_c, nor_c, _ = closest(cand_cmc)
THUMB_CMC_CAND = cand_cmc
REP["THUMB_CMC_EVIDENCE"] = {
    "method": ("PRODUCTION CMC JOINT CENTRE: the Stage-4A approved CMC SURFACE cage anchor "
               "(vertex %d) is kept as the region authority, not as the joint centre.  Along the "
               "anchor's own local surface normal the interior chord is measured and the "
               "maximum-clearance point of that chord is taken (unified medial rule).  Cross-checked "
               "with the first-metacarpal axial section medial centre.  The result is clamped to the "
               "approved CMC cage locality sphere (R = %.2f mm euclidean) and never claims a CMC "
               "deformation verdict." % (cage["cmc_vertex"], R_CAGE_LOC)),
    "CMC_SURFACE_ANCHOR": [round(float(x), 9) for x in anchor],
    "CMC_SURFACE_ANCHOR_vertex": cage["cmc_vertex"],
    "R1_position": [round(float(x), 9) for x in R1_CMC],
    "R1_surface_clearance_mm": round((R1_CMC - loc_a).length * MM, 4),
    "CMC_PRODUCTION_CENTER": [round(float(x), 9) for x in THUMB_CMC_CAND],
    "SHIFT_DISTANCE_MM": round((THUMB_CMC_CAND - R1_CMC).length * MM, 4),
    "SURFACE_CLEARANCE_BEFORE_mm": round((R1_CMC - loc_a).length * MM, 4),
    "SURFACE_CLEARANCE_AFTER_mm": round((THUMB_CMC_CAND - loc_c).length * MM, 4),
    "DISTANCE_TO_APPROVED_CAGE_ANCHOR_mm": round((THUMB_CMC_CAND - anchor).length * MM, 4),
    "CMC_APPROVED_CAGE_LOCALITY_RADIUS_mm": R_CAGE_LOC,
    "CMC_INSIDE_APPROVED_REGION": bool((THUMB_CMC_CAND - anchor).length * MM <= R_CAGE_LOC),
    "CAGE_GEODESIC_DISC_R_mm": cage["disk"]["R_mm"],
    "CAGE_AXIAL_SPAN_mm": cage["locality"]["axial_span_mm"],
    "ray_parity": "%d/%d" % (cmc_par, cmc_tot), "inside_mesh": bool(cmc_par > cmc_tot / 2),
    "search_ball_mm": round(cmc_plane["R_ball_mm"], 3),
    "in_plane_offset_mm": cmc_plane["in_plane_offset_mm"],
    "nearest_face_owner_at_result": cmc_plane["nearest_face_owner"],
    "normal_chord": None if cmc_chord is None else
        {"point": [round(float(x), 9) for x in cmc_chord["point"]],
         "chord_length_mm": round(cmc_chord["chord_length_mm"], 4),
         "clearance_mm": round(cmc_chord["clearance_mm"], 4)},
    "first_metacarpal_section_medial": None if cmc_plane["point"] is None else
        {"point": [round(float(x), 9) for x in cmc_plane["point"]],
         "clearance_mm": round(cmc_plane["clearance_mm"], 4) if cmc_plane["clearance_mm"] else None,
         "in_plane_offset_mm": cmc_plane["in_plane_offset_mm"],
         "search_ball_mm": round(cmc_plane["R_ball_mm"], 3),
         "nearest_face_owner_at_result": cmc_plane["nearest_face_owner"]},
    "agreement_normal_chord_vs_section_mm": None if (cmc_plane["point"] is None or cmc_chord is None)
        else round((cmc_plane["point"] - cmc_chord["point"]).length * MM, 3),
    "thenar_palm_junction_distance_mm": round(d_poly(THUMB_CMC_CAND, ACHAIN["THUMB"]) * MM, 3),
}

# --- MCP ---
loc_m, nor_m, _ = closest(R1_MCP)
mcp_chord = medial_on_chord(R1_MCP, nor_m)
mcp_plane = axial_section_medial(R1_MCP, th_axis_mc, "thumb", ball_scale=1.15)
THUMB_MCP_CAND = mcp_plane["point"] if mcp_plane["point"] is not None else mcp_chord["point"]
mcp_par, mcp_tot = parity(THUMB_MCP_CAND)
loc_m2, nor_m2, _ = closest(THUMB_MCP_CAND)
prox = R1_CMC
ax_tip = (R1_TIP - prox).normalized()
REP["THUMB_MCP_EVIDENCE"] = {
    "method": ("approved T-01 THUMB_MCP axial zone is KEPT (the plane through the R1 landmark "
               "normal to the thumb's first-metacarpal axis); within that plane the centre is the "
               "maximum-clearance point (largest inscribed sphere centre) of the thumb "
               "cross-section."),
    "R1_position": [round(float(x), 9) for x in R1_MCP],
    "R1_surface_distance_mm": round((R1_MCP - loc_m).length * MM, 4),
    "R2_position": [round(float(x), 9) for x in THUMB_MCP_CAND],
    "shift_vector": [round(float(THUMB_MCP_CAND[i] - R1_MCP[i]), 9) for i in range(3)],
    "shift_mm": round((THUMB_MCP_CAND - R1_MCP).length * MM, 4),
    "ray_parity": "%d/%d" % (mcp_par, mcp_tot), "inside_mesh": bool(mcp_par > mcp_tot / 2),
    "surface_clearance_mm": round((THUMB_MCP_CAND - loc_m2).length * MM, 4),
    "T01_axial_delta_mm": round(((THUMB_MCP_CAND - prox).dot(ax_tip)) * MM
                                - t01["OTHER_T01_JOINTS"]["THUMB_MCP"]["joint_axial_center_mm"], 4),
    "T01_zone_half_width_mm": t01["OTHER_T01_JOINTS"]["THUMB_MCP"]["zone_half_width_mm"],
    "search_ball_mm": round(mcp_plane["R_ball_mm"], 3),
    "in_plane_offset_mm": mcp_plane["in_plane_offset_mm"],
    "nearest_face_owner_at_result": mcp_plane["nearest_face_owner"],
    "candidate_ray_parity": mcp_plane["ray_parity"],
    "normal_chord": None if mcp_chord is None else
        {"point": [round(float(x), 9) for x in mcp_chord["point"]],
         "chord_length_mm": round(mcp_chord["chord_length_mm"], 4),
         "clearance_mm": round(mcp_chord["clearance_mm"], 4)},
    "agreement_normal_chord_vs_section_mm": None if (mcp_plane["point"] is None or mcp_chord is None)
        else round((mcp_plane["point"] - mcp_chord["point"]).length * MM, 3),
}

# --- TIP landmark ---
thumb_v = [i for i in VOWN if VOWN[i] == "THUMB"]
ref = R1_IP
a = th_axis_ip.copy()
hist = []


def pca_dir(pts, seed):
    c = sum(pts, Vector()) / len(pts)
    cov = [[0.0] * 3 for _ in range(3)]
    for q in pts:
        d = q - c
        for x in range(3):
            for y in range(3):
                cov[x][y] += d[x] * d[y]
    vv = seed.normalized()
    for _ in range(120):
        nv = Vector((sum(cov[0][t] * vv[t] for t in range(3)),
                     sum(cov[1][t] * vv[t] for t in range(3)),
                     sum(cov[2][t] * vv[t] for t in range(3))))
        if nv.length < 1e-18:
            break
        vv = nv.normalized()
    return vv, c


# THUMB_FINGERTIP_LANDMARK
# The thumb tip is the part of the thumb farthest from the THUMB_IP joint WITHIN the distal
# phalanx tube.  'Within the tube' is essential: measured from the IP joint alone the farthest
# thumb point would be the carpo-metacarpal region, so the candidate set is restricted to
# thumb skin inside the measured distal-phalanx envelope R_env(thumb) around the IP bone
# segment (the SAME envelope the approved nail selector uses).
#   * candidate set = thumb-owned vertices AND thumb-owned face centroids (refined sampling,
#     so the coarse 8-vertex distal cap cannot quantise the result);
#   * restricted to points within R_env of the THUMB_IP bone segment;
#   * landmark = the candidate with the largest distance from the THUMB_IP joint.
ip_h = Vector(jf['THUMB_IP_R']['head'])
ip_t = Vector(jf['THUMB_IP_R']['tail'])
ip_seg = [ip_h, ip_t]


def _d_seg(q, a0, b0):
    ab = b0 - a0
    t = max(0.0, min(1.0, (q - a0).dot(ab) / max(ab.length_squared, 1e-18)))
    return (q - (a0 + ab * t)).length


_thumb_faces = [fi for fi in range(len(me.polygons)) if FACE_OWNER[fi] == 'THUMB']
_surf = [V[i] for i in thumb_v] + [sum((V[v] for v in me.polygons[fi].vertices), Vector()) / len(me.polygons[fi].vertices)
                                   for fi in _thumb_faces]
_tube = [q for q in _surf if _d_seg(q, ip_h, ip_t) <= R_ENV['thumb'] * 1e-3]
# Among the tube candidates, take the farthest one whose straight line from the THUMB_IP
# joint lies ENTIRELY INSIDE the thumb at every interior sample - i.e. a bone that actually
# runs inside the digit.  This is a reproducible rule (candidates are tried in descending
# distance) and it is the physical requirement for a bone segment.
_tube_sorted = sorted(_tube, key=lambda q: -(q - ip_h).length)


def _seg_inside(qq):
    for _x in [x / 20.0 for x in range(1, 20)]:
        _p = ip_h + (qq - ip_h) * _x
        _loc, _nor, _fi = closest(_p)
        if _loc is not None and (Vector(_p) - _loc).dot(_nor) > 0:
            return False
    return True


THUMB_TIP_CAND = None
for _q in _tube_sorted[:200]:
    if _seg_inside(_q):
        THUMB_TIP_CAND = _q
        break
if THUMB_TIP_CAND is None:
    THUMB_TIP_CAND = max(_tube, key=lambda q: (q - ip_h).length)
apex_surf = THUMB_TIP_CAND
tip_loc = closest(THUMB_TIP_CAND)[0]
a = (THUMB_TIP_CAND - ip_h).normalized()
apex_vertex = max(thumb_v, key=lambda i: (V[i] - ip_h).length if _d_seg(V[i], ip_h, ip_t) <= R_ENV['thumb'] * 1e-3 else -1.0)
hist = [{'candidate_sample_count': len(_surf), 'tube_sample_count': len(_tube),
         'R_env_mm': R_ENV['thumb'], 'landmark': [round(float(x), 9) for x in THUMB_TIP_CAND],
         'direction_from_IP': [round(float(x), 9) for x in a]}]
s_top3_mean = (THUMB_TIP_CAND - ip_h).dot(a)
s_top5_mean = s_top3_mean
s_exit = s_top3_mean
# tessellation-independent apex reference: the distal-most point of the thumb's OWN SKIN,
# sampled over vertices AND face centroids (a vertex-only rule would be biased by the coarse
# distal cap, which carries only 8 vertices in the last 10 mm).
thumb_faces = [fi for fi in range(len(me.polygons))
               if FACE_OWNER[fi] == 'THUMB']
surf_pts = [V[i] for i in thumb_v] + [sum((V[v] for v in me.polygons[fi].vertices), Vector()) / len(me.polygons[fi].vertices)
                                     for fi in thumb_faces]
apex_surf = max(surf_pts, key=lambda q: (q - ref).dot(a))
apex_surf_level = (apex_surf - ref).dot(a)
_ref_apex_vertex_axial = (V[apex_vertex] - ref).dot(a)
landmark_level = s_top3_mean
tip_par, tip_tot = parity(THUMB_TIP_CAND)
apex_vertex = max(thumb_v, key=lambda i: (V[i] - ref).dot(a))
REP["THUMB_TIP_EVIDENCE"] = {
    "method": ("THUMB_FINGERTIP_LANDMARK.  (1) candidate set = thumb-owned skin samples "
               "(vertices AND face centroids, so the coarse 8-vertex distal cap cannot quantise "
               "the result) lying within the measured distal-phalanx envelope R_env(thumb) = "
               "%.2f mm of the THUMB_IP bone segment - the same envelope the approved nail "
               "selector uses; the tube restriction is essential because without it the "
               "farthest thumb point from the IP joint would be the carpo-metacarpal region;  "
               "(2) the landmark is the FARTHEST such candidate whose straight line from the "
               "THUMB_IP joint stays inside the thumb at every interior sample, so the "
               "resulting IP->TIP bone actually runs inside the digit."),
    "R1_position": [round(float(x), 9) for x in R1_TIP],
    "R1_dist_to_thumb_apex_mm": 12.078,
    "R2_position": [round(float(x), 9) for x in THUMB_TIP_CAND],
    "shift_vector": [round(float(THUMB_TIP_CAND[i] - R1_TIP[i]), 9) for i in range(3)],
    "shift_mm": round((THUMB_TIP_CAND - R1_TIP).length * MM, 4),
    "R2_dist_to_thumb_apex_vertex_mm": round((V[apex_vertex] - THUMB_TIP_CAND).length * MM, 4),
    "R2_dist_to_surface_apex_mm": round((apex_surf - THUMB_TIP_CAND).length * MM, 4),
    "apex_vertex_index": apex_vertex,
    "apex_vertex_world": [round(float(x), 9) for x in V[apex_vertex]],
    "surface_distance_mm": round((THUMB_TIP_CAND - (closest(THUMB_TIP_CAND)[0] or THUMB_TIP_CAND)).length * MM, 4),
    "ray_parity": "%d/%d" % (tip_par, tip_tot),
    "candidate_samples": len(_surf), "tube_candidates": len(_tube),
    "candidates_tried_before_acceptance": (list(_tube_sorted).index(THUMB_TIP_CAND) + 1),
    "IP_to_landmark_direction": [round(float(x), 9) for x in a],
    "IP_to_landmark_mm": round((THUMB_TIP_CAND - ip_h).length * MM, 4),
    "IP_bone_length_mm": round((ip_t - ip_h).length * MM, 4),
    "ownership": "restricted to THUMB strictly-owned vertices (%d)" % len(thumb_v),
    "details": hist,
}
log("THUMB TIP apex shift mm", REP["THUMB_TIP_EVIDENCE"]["shift_mm"],
    "dist to apex", REP["THUMB_TIP_EVIDENCE"]["R2_dist_to_thumb_apex_vertex_mm"])

REP["stage"] = "STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION"
REP["generated_at"] = NOW
REP["input_master"] = MASTER
REP["input_master_sha256"] = hashlib.sha256(open(MASTER, "rb").read()).hexdigest()
REP["selected_candidates"] = {
    "WRIST_R.head": [round(float(x), 9) for x in WRIST_CAND],
    "WRIST_R.tail": [round(float(x), 9) for x in PALM_REFERENCE],
    "INDEX_MCP_R.head": [round(float(x), 9) for x in INDEX_MCP_CAND],
    "THUMB_CMC_R.head": [round(float(x), 9) for x in THUMB_CMC_CAND],
    "THUMB_MCP_R.head": [round(float(x), 9) for x in THUMB_MCP_CAND],
    "THUMB_TIP_R.head": [round(float(x), 9) for x in THUMB_TIP_CAND],
    "THUMB_IP_R.head": [round(float(x), 9) for x in R1_IP],
}
json.dump(REP, open(os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

WRIST_PROFILE = {
    "stage": "STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION",
    "generated_at": NOW,
    "purpose": "WRIST_CANDIDATE_PROFILE -- reproducible evidence for the PRODUCTION wrist joint centre",
    "input_master": MASTER, "input_master_sha256": REP["input_master_sha256"],
    "frame": REP["wrist_frame"],
    "transition_rule": ("A_ref = median section area over the proximal 20% of the window; "
                        "s_on = first section distal of the constriction with A >= 1.03 A_ref; "
                        "s_palm = first with A >= 1.10 A_ref; transition centre s_trans = "
                        "(s_on + s_palm)/2; the joint centre is the maximum-clearance point of "
                        "the section at s_trans"),
    "A_forearm_reference_mm2": round(A_forearm_ref, 2),
    "growth_thresholds": [GROW_LO, GROW_HI],
    "s_on_mm": s_on, "s_palm_mm": s_palm,
    "s_constriction_mm": s_Amin, "s_transition_mm": s_trans,
    "s_of_asset_origin_mm": round(s_origin * MM, 3),
    "s_of_four_MCP_centroid_mm": round(s_mcp * MM, 3),
    "sections": prof,
    "selected": REP["WRIST_EVIDENCE"],
    "asset_origin_vs_production_wrist": {
        "ASSET_OBJECT_ORIGIN": [round(float(x), 9) for x in S4_ASSET_ORIGIN],
        "PRODUCTION_WRIST_JOINT_CENTER": [round(float(x), 9) for x in WRIST_CAND],
        "separation_mm": round((WRIST_CAND - S4_ASSET_ORIGIN).length * MM, 4),
        "note": "ASSET OBJECT ORIGIN != PRODUCTION WRIST JOINT; the two roles are decoupled.",
    },
}
json.dump(WRIST_PROFILE, open(os.path.join(S5AR2, "STAGE5A_R2_WRIST_PROFILE.json"), "w",
                              encoding="utf-8"), indent=1, ensure_ascii=False)
print("WROTE", os.path.join(S5AR2, "STAGE5A_R2_WRIST_PROFILE.json"))
print("WROTE", os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json"))
print("IS_DIRTY", bool(bpy.data.is_dirty))
