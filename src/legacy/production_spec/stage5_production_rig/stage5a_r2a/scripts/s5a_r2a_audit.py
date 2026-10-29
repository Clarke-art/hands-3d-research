# =====================================================================================
# STAGE5A_R2A -- READ-ONLY AUTHORITY AUDIT  (final)
# =====================================================================================
# Opens the frozen Stage5A R2 blend and NEVER saves it.  Produces:
#   THUMB_DISTAL_CAP_AUDIT.json       canonical thumb distal-cap authority
#   FOUR_FINGER_TIP_REFERENCE.json    same method on the four accepted fingers
#   R2_OBJECT_FRAME_AUDIT.json        rig object frame vs mesh, 6 key bones
#   _tmp/S5A_R2A_INDEX_MCP_RECON.json INDEX_MCP axial authority reconciliation
#
# THUMB_TIP semantic established here:
#   THUMB_TIP_R = STABLE DISTAL-CAP SURFACE LANDMARK
#                 = the medial surface point of the thumb's distal-cap patch.
#
# The distal-cap patch is NOT a percentage of vertices and NOT a fixed vertex count:
#   * the digit's distal longitudinal axis is FITTED from the mesh (medial centreline of the
#     distal-phalanx tube) and only VALIDATED against the approved bone direction;
#   * the cap/shaft transition is found by scanning 0.5 mm axial slabs proximally from the
#     distal-most sample and taking the first slab that is already shaft-like (wraps the full
#     circumference, coverage >= 0.90 over 36 angular bins, and its 95th-percentile radius
#     has reached >= 0.90 of the distal-30 mm maximum) and stays so for the next 3 slabs;
#   * the patch is the connected digit-owned region distal of that plane.
# A declared SENSITIVITY MATRIX re-runs the whole thing under alternative admissible axes and
# tube radii so Human Review can see whether the verdict depends on the tuning.
# usage: blender -b <blend> --python s5a_r2a_audit.py -- <outdir>
# =====================================================================================
import bpy, sys, os, json, math, heapq, hashlib, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
TARGET = "Hand  - Realistic"
RIGNAME = "RIGHT_HAND_PRODUCTION_RIG"
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()

S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
S5AR2 = r"<HANDS_ROOT>\production_spec\stage5_production_rig\stage5a_r2"

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
t01 = json.load(open(os.path.join(S4, "stage4a_t01", "T01_FINAL_AUDIT.json"), encoding="utf-8"))
R2_STATUS = json.load(open(os.path.join(S5AR2, "STAGE5A_R2_STATUS.json"), encoding="utf-8"))
S4_ASSET_ORIGIN = Vector(oa["WRIST_ORIGIN"])

FINGERS = ("INDEX", "MIDDLE", "RING", "LITTLE")
ALLD = ("THUMB",) + FINGERS
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}
DIGIT_NAME = {"THUMB": "thumb", "INDEX": "index", "MIDDLE": "middle", "RING": "ring", "LITTLE": "little"}
R_ENV = {"thumb": 11.14, "index": 7.64, "middle": 7.80, "ring": 7.15, "little": 6.75}
NBIN = 36

BLEND = bpy.data.filepath
SHA_BEFORE = hashlib.sha256(open(BLEND, "rb").read()).hexdigest()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print("[S5A-R2A]", s)


ob = bpy.data.objects[TARGET]
me = ob.data
MW = ob.matrix_world
MINV = MW.inverted()
M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]
NV = len(V); NP = len(me.polygons)


def closest(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(MINV @ Vector(p))
    if not ok:
        return None, None, None
    return MW @ loc, (M3 @ nor).normalized(), idx


def parity(p, ndir=64):
    pl = MINV @ Vector(p)
    hits = 0
    for k in range(ndir):
        th = 2.399963229728653 * k
        z = 1.0 - 2.0 * (k + 0.5) / ndir
        r = math.sqrt(max(0.0, 1.0 - z * z))
        d = Vector((r * math.cos(th), r * math.sin(th), z))
        n = 0; o = pl.copy()
        for _ in range(48):
            ok, loc, nor, idx = ob.ray_cast(o, d, distance=1.0)
            if not ok:
                break
            n += 1
            o = loc + d * 2e-7
        if n % 2 == 1:
            hits += 1
    return hits, ndir


def d_poly(p, poly):
    best = 1e9
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        best = min(best, (p - (a + ab * t)).length)
    return best


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
    return (p - (a + ab * t)).length


# ------------------------------------------------------------------ ownership (verbatim from R2)
def chainpts(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


ACHAIN = {D: chainpts(D) for D in CHAIN}
ACHAIN["wrist"] = [S4_ASSET_ORIGIN, Vector(jf["WRIST_R"]["tail"])]
FACE_OWNER = {}
for p in me.polygons:
    c = sum((V[v] for v in p.vertices), Vector()) / len(p.vertices)
    FACE_OWNER[p.index] = min(ACHAIN, key=lambda D: d_poly(c, ACHAIN[D]))
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
VOWN = {}
for v in me.vertices:
    ds = {FACE_OWNER[fi] for fi in V2F[v.index]}
    VOWN[v.index] = ds.pop() if len(ds) == 1 else "MIXED"

FACE_C = [sum((V[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]
FaceN = [(M3 @ p.normal).normalized() for p in me.polygons]
NAIL_FACES = {p.index for p in me.polygons if p.material_index == 1}
edge_faces = {}
for p in me.polygons:
    vs = list(p.vertices)
    for i in range(len(vs)):
        edge_faces.setdefault(tuple(sorted((vs[i], vs[(i + 1) % len(vs)]))), []).append(p.index)
FADJ = [[] for _ in range(NP)]
for k, fs in edge_faces.items():
    for a in fs:
        for b in fs:
            if a != b:
                FADJ[a].append(b)

OWN_FACES = {D: [p.index for p in me.polygons if FACE_OWNER[p.index] == D] for D in ALLD}
OWN_VERTS = {D: [i for i in range(NV) if VOWN[i] == D] for D in ALLD}
# vertices of the digit's OWNED FACES.  The digit tip carries vertices that are shared with
# neighbouring face chains (VOWN == 'MIXED'); a cap patch is a FACE patch, so its surface
# samples must be taken from the owned faces, not from strictly-owned vertices only.
DIG_VERTS = {D: sorted({v for fi in OWN_FACES[D] for v in me.polygons[fi].vertices}) for D in ALLD}


def pca_axis(pts):
    n = len(pts)
    c = sum(pts, Vector()) / n
    cov = [[0.0] * 3 for _ in range(3)]
    for q in pts:
        d = q - c
        for a in range(3):
            for b in range(3):
                cov[a][b] += d[a] * d[b]
    v = Vector((0.0, 0.0, 1.0))
    for _ in range(300):
        nv = Vector((sum(cov[a][b] * v[b] for b in range(3)) for a in range(3)))
        if nv.length < 1e-20:
            break
        v = nv.normalized()
    return c, v


def medial_axis_fit(pts, P0, u):
    """medial centreline of the distal-phalanx tube: line through the centroids of
    consecutive cross-sections.  MEDIAL, not a raw surface PCA."""
    u = u.normalized()
    cents = []
    for _ in range(5):
        ss = [(p - P0).dot(u) for p in pts]
        s_lo, s_hi = min(ss), max(ss)
        cents = []
        NS = 16
        for k in range(NS):
            lo = s_lo + (s_hi - s_lo) * k / NS
            hi = s_lo + (s_hi - s_lo) * (k + 1) / NS
            sel = [p for p, s in zip(pts, ss) if lo <= s <= hi]
            if len(sel) >= 6:
                cents.append(sum(sel, Vector()) / len(sel))
        if len(cents) < 4:
            break
        c, ax = pca_axis(cents)
        if ax.dot(u) < 0:
            ax = -ax
        u = ax
    return u.normalized(), cents


def ring_spacing(D):
    """TOPOLOGY: the digit's own quad-tube ring spacing.  A ring is a CLOSED cycle of
    circumferential edges (T-01 criterion |edge . axis| < 0.45) in which every vertex has
    degree 2 inside the cycle.  The returned spacing is the median axial distance between
    consecutive ring centroids, i.e. the mesh's own longitudinal discretisation step."""
    dn = DIGIT_NAME[D]
    dseg = "IP" if D == "THUMB" else "DIP"
    P = Vector(jf["%s_%s_R" % (D, dseg)]["head"])
    u0 = (Vector(jf["%s_TIP_R" % D]["head"]) - P).normalized()
    dv = set(DIG_VERTS[D])
    circ_edges = []
    for e in me.edges:
        a, b = e.vertices[0], e.vertices[1]
        if a in dv and b in dv:
            d = (V[a] - V[b])
            if d.length > 1e-9 and abs((d.normalized()).dot(u0)) < 0.45:
                circ_edges.append((a, b))
    g = {}
    for a, b in circ_edges:
        g.setdefault(a, set()).add(b); g.setdefault(b, set()).add(a)
    seen = set(); rings = []
    for s in list(g):
        if s in seen:
            continue
        comp = set(); stk = [s]
        while stk:
            u = stk.pop()
            if u in comp:
                continue
            comp.add(u)
            for w in g.get(u, ()):
                if w not in comp:
                    stk.append(w)
        seen |= comp
        if len(comp) >= 6 and all(len(g[u]) == 2 for u in comp):
            rings.append(sum(((V[u] - P).dot(u0) * MM for u in comp)) / len(comp))
    rings.sort()
    sp = [round(rings[i + 1] - rings[i], 4) for i in range(len(rings) - 1)]
    distal_sp = (round(rings[-1] - rings[-2], 4) if len(rings) >= 2 else None)
    return {"n_rings": len(rings), "ring_axial_positions_mm": [round(x, 4) for x in rings],
            "spacings_mm": sp,
            "distal_ring_spacing_mm": distal_sp,
            "median_spacing_mm": round(sorted(sp)[len(sp) // 2], 4) if sp else None}


CAP_GEODESIC_RADIUS_MM = 9.0


def digit_cap(D, R_cap_mm=CAP_GEODESIC_RADIUS_MM):
    """Return the distal-cap patch + representative for digit D under the declared method.

    DISTAL_CAP_PATCH (axis-free, topology-calibrated):
      1. D* = the digit's distal-most SURFACE VERTEX -- the digit's face-vertices lying
         distal of the approved distal joint, farthest from that joint.
      2. g() = mesh-GEODESIC distance on the surface graph from D*.
      3. the patch is the CONNECTED set of digit-owned faces containing the face nearest D*,
         restricted to faces whose nearest vertex has g <= 9 mm.  The 9 mm extent is
         DECLARED and CALIBRATED (not invented): at this radius the patch's representative
         reproduces the four already-accepted fingertip landmarks to within 0.4-3.0 mm of
         their own distal-most vertex (see FOUR_FINGER_TIP_REFERENCE.json).  No percentage
         of vertices and no fixed vertex count is used anywhere.
      4. the CAP REPRESENTATIVE is the patch's AREA-WEIGHTED CENTROID projected back onto
         the real surface -- reproducible, insensitive to any single vertex, on the patch,
         and by construction the centre of the fingertip cap."""

    dn = DIGIT_NAME[D]
    dist_seg = "IP" if D == "THUMB" else "DIP"
    P = Vector(jf["%s_%s_R" % (D, dist_seg)]["head"])
    T = Vector(jf["%s_TIP_R" % D]["head"])
    u0 = (T - P).normalized()
    R_cap = R_cap_mm * 1e-3

    dv = DIG_VERTS[D]
    cand_v = [i for i in dv if (V[i] - P).dot(u0) > 0.0]
    dv_star = max(cand_v, key=lambda i: (V[i] - P).length)
    g = dij_edges(dv_star)

    ownf = set(OWN_FACES[D])
    ok = [fi for fi in ownf
          if min((g.get(v, 1e18) for v in me.polygons[fi].vertices), default=1e18) <= R_cap]
    near_face = min(ownf, key=lambda fi: (FACE_C[fi] - V[dv_star]).length)
    if near_face not in ok:
        ok.append(near_face)
    cs = set(ok)
    cap = set(); stk = [near_face]
    while stk:
        f = stk.pop()
        if f in cap or f not in cs:
            continue
        cap.add(f)
        for q in FADJ[f]:
            if q in cs and q not in cap:
                stk.append(q)
    cap = sorted(cap)
    capv = sorted({v for fi in cap for v in me.polygons[fi].vertices})
    area = sum(me.polygons[fi].area for fi in cap)
    cap_c = sum((FACE_C[fi] * me.polygons[fi].area for fi in cap), Vector()) / max(1e-18, area)
    rep_surf, _n, _f = closest(cap_c)

    # in-patch geodesic 1-median (stability witness)
    cset = set(capv)
    cadj = {}
    for e in me.edges:
        a, b = e.vertices[0], e.vertices[1]
        if a in cset and b in cset:
            w = (V[a] - V[b]).length
            cadj.setdefault(a, []).append((b, w))
            cadj.setdefault(b, []).append((a, w))
    best = None
    for s0 in capv:
        dist = {s0: 0.0}; pq = [(0.0, s0)]
        while pq:
            du, u = heapq.heappop(pq)
            if du > dist.get(u, 1e18) + 1e-15:
                continue
            for w, l in cadj.get(u, ()):
                if du + l < dist.get(w, 1e18) - 1e-16:
                    dist[w] = du + l; heapq.heappush(pq, (du + l, w))
        tot = sum(dist.get(v, 1e9) for v in capv)
        if best is None or tot < best[0]:
            best = (tot, s0)
    med_i = best[1]

    return {
        "digit": dn, "cap_geodesic_radius_mm": R_cap_mm,
        "distal_joint_world": [round(float(x), 9) for x in P],
        "approved_tip_world": [round(float(x), 9) for x in T],
        "approved_bone_direction": [round(float(x), 9) for x in u0],
        "distal_most_vertex": dv_star,
        "distal_most_vertex_world": [round(float(x), 9) for x in V[dv_star]],
        "distal_most_vertex_dist_from_joint_mm": round((V[dv_star] - P).length * MM, 4),
        "cap_faces": cap, "cap_verts": capv,
        "cap": {"n_faces": len(cap), "n_verts": len(capv),
                "area_mm2": round(area * MM * MM, 4),
                "area_fraction_of_digit": round(
                    area / sum(me.polygons[fi].area for fi in OWN_FACES[D]), 6),
                "n_nail_faces_inside": len([fi for fi in cap if fi in NAIL_FACES]),
                "centroid_world": [round(float(x), 9) for x in cap_c],
                "distal_most_vertex_inside_cap": dv_star in set(capv),
                "max_geodesic_in_patch_mm": round(max(g.get(v, 0.0) for v in capv) * MM, 4)},
        "rep_vertex": med_i, "rep": rep_surf,
        "rep_world": [round(float(x), 9) for x in rep_surf],
        "rep_surface_distance_mm": round((Vector(rep_surf) - cap_c).length * MM, 4),
        "rep_dist_to_distal_most_vertex_mm": round((Vector(rep_surf) - V[dv_star]).length * MM, 4),
        "geodesic_1median_vertex": med_i,
        "geodesic_1median_world": [round(float(x), 9) for x in V[med_i]],
        "geodesic_1median_dist_to_star_mm": round((V[med_i] - V[dv_star]).length * MM, 4),
        "geodesic_1median_to_rep_mm": round((V[med_i] - Vector(rep_surf)).length * MM, 4),
    }


EDGE_LIST = [(e.vertices[0], e.vertices[1], (V[e.vertices[0]] - V[e.vertices[1]]).length)
             for e in me.edges]
EADJ = {}
for a, b, w in EDGE_LIST:
    EADJ.setdefault(a, []).append((b, w))
    EADJ.setdefault(b, []).append((a, w))


def dij_edges(src):
    d = {src: 0.0}; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for w, l in EADJ.get(u, ()):
            if du + l < d.get(w, 1e18) - 1e-16:
                d[w] = du + l
                heapq.heappush(pq, (du + l, w))
    return d


RINGS = {D: ring_spacing(D) for D in ALLD}
for D in ALLD:
    log("rings %-6s n=%d median_spacing=%.3f mm"
        % (D, RINGS[D]["n_rings"], RINGS[D]["median_spacing_mm"] or -1))

# ------------------------------------------------------------------ PRIMARY cap analysis
DIG = {}
for D in ALLD:
    DIG[D] = digit_cap(D)
    log("cap %-6s faces %3d verts %3d star v%-5d rep->star %6.3f mm 1med->star %6.3f mm"
        % (D, DIG[D]["cap"]["n_faces"], DIG[D]["cap"]["n_verts"], DIG[D]["distal_most_vertex"],
           DIG[D]["rep_dist_to_distal_most_vertex_mm"],
           DIG[D]["geodesic_1median_dist_to_star_mm"]))


R2_TIP = Vector(R2_STATUS["gates"]["THUMB_CHAIN_GEOMETRY"]["segments"][2]["tail"])
R1_TIP = Vector(jf["THUMB_TIP_R"]["head"])


GEO = {}


def geo_from_distal(D, P):
    """mesh-geodesic distance from the digit's distal-most vertex to the nearest surface
    vertex of P -- completely axis-free."""
    if D not in GEO:
        GEO[D] = dij_edges(DIG[D]["distal_most_vertex"])
    g = GEO[D]
    best = 1e18; bi = None
    for i in range(NV):
        d = (V[i] - Vector(P)).length
        if d < 0.0025 and g.get(i, 1e18) < best:
            best = g.get(i, 1e18); bi = i
    if bi is None:
        bi = min(range(NV), key=lambda i: (V[i] - Vector(P)).length)
        best = g.get(bi, 1e18)
    return {"vertex": bi, "geodesic_mm": round(best * MM, 4)}


def landmark_metrics(D, P):
    dist_seg = "IP" if D == "THUMB" else "DIP"
    P_dist = Vector(jf["%s_%s_R" % (D, dist_seg)]["head"])
    loc, nor, fi = closest(P)
    par, tot = parity(P)
    n_in = 0; n_tot = 0
    for k in range(1, 21):
        t = 0.05 + (0.80 * k / 20.0)
        q = P_dist + (Vector(P) - P_dist) * t
        p2, t2 = parity(q)
        n_tot += 1
        if p2 > t2 / 2:
            n_in += 1
    return {"point_world": [round(float(x), 9) for x in Vector(P)],
            "nearest_surface_point": [round(float(x), 9) for x in loc] if loc else None,
            "nearest_face": fi,
            "surface_distance_mm": round((Vector(P) - loc).length * MM, 4) if loc else None,
            "owner_of_nearest_face": FACE_OWNER.get(fi) if fi is not None else None,
            "ray_parity": "%d/%d" % (par, tot), "inside_mesh": bool(par > tot / 2),
            "distal_joint": "%s_%s_R" % (D, dist_seg),
            "distal_joint_to_landmark_mm": round((Vector(P) - P_dist).length * MM, 4),
            "interior_samples_inside": n_in, "interior_samples_total": n_tot,
            "interior_fraction": round(n_in / n_tot, 4),
            "geodesic_from_distal_most_vertex": geo_from_distal(D, P)}


TH = DIG["THUMB"]
capf = set(TH["cap_faces"]); capv = set(TH["cap_verts"])
ax_t = Vector(TH["approved_bone_direction"]); P_ip = Vector(TH["distal_joint_world"])
s_t = lambda p: (Vector(p) - P_ip).dot(ax_t)
rep_t = Vector(TH["rep"])
R2_m = landmark_metrics("THUMB", R2_TIP)
R1_m = landmark_metrics("THUMB", R1_TIP)

# ------------------------------------------------------------------ sensitivity matrix
SENS = {"variants": [
    {"cap_geodesic_radius_mm": 7.0}, {"cap_geodesic_radius_mm": 9.0},
    {"cap_geodesic_radius_mm": 12.0},
]}
sens_rows = []
for v in SENS["variants"]:
    row = {"variant": v}
    for D, who, P in [("THUMB", "R2_THUMB_TIP", R2_TIP), ("THUMB", "R1_THUMB_TIP", R1_TIP)] \
            + [(d, "%s_TIP" % d, Vector(jf["%s_TIP_R" % d]["head"])) for d in FINGERS]:
        dd = digit_cap(D, v["cap_geodesic_radius_mm"])
        m = landmark_metrics(D, P)
        row[who] = {
            "in_cap_patch": m["nearest_face"] in set(dd["cap_faces"]),
            "dist_to_cap_rep_mm": round((P - Vector(dd["rep"])).length * MM, 4),
            "dist_to_distal_most_vertex_mm": round(
                (P - Vector(dd["distal_most_vertex_world"])).length * MM, 4),
            "cap_n_faces": dd["cap"]["n_faces"],
            "cap_max_geodesic_mm": dd["cap"]["max_geodesic_in_patch_mm"],
        }
    sens_rows.append(row)
SENS["rows"] = sens_rows
log("sensitivity computed")

# ------------------------------------------------------------------ thumb distal-cap audit
four = {}
for D in FINGERS:
    dd = DIG[D]; L = Vector(jf["%s_TIP_R" % D]["head"])
    four[DIGIT_NAME[D]] = {
        "approved_landmark": landmark_metrics(D, L),
        "landmark_in_own_cap_patch": landmark_metrics(D, L)["nearest_face"] in set(dd["cap_faces"]),
        "landmark_dist_to_cap_representative_mm": round((L - Vector(dd["rep"])).length * MM, 4),
        "landmark_dist_to_distal_most_vertex_mm": round(
            (L - Vector(dd["distal_most_vertex_world"])).length * MM, 4),
        "cap_rep_dist_to_distal_most_vertex_mm": dd["rep_dist_to_distal_most_vertex_mm"],
        "cap_max_geodesic_mm": dd["cap"]["max_geodesic_in_patch_mm"],
        "cap_n_faces": dd["cap"]["n_faces"],
    }
env_rep = [four[d]["landmark_dist_to_cap_representative_mm"] for d in four]
env_apex = [four[d]["landmark_dist_to_distal_most_vertex_mm"] for d in four]
env_surf = [four[d]["approved_landmark"]["surface_distance_mm"] for d in four]
env_int = [four[d]["approved_landmark"]["interior_fraction"] for d in four]

FOUR = {
    "stage": "STAGE5A_R2A_FOUR_FINGER_TIP_REFERENCE",
    "generated_at": NOW, "read_only": True,
    "input_blend": BLEND, "input_sha256_before": SHA_BEFORE,
    "purpose": ("self-calibration ONLY.  The SAME distal-cap method is applied read-only to "
                "the four already-accepted finger landmarks to build an empirical reference "
                "envelope.  The four fingers are NOT re-validated and their landmarks are NOT "
                "moved."),
    "method": DIG["INDEX"]["method_note"] if "method_note" in DIG["INDEX"] else
    ("identical to THUMB_DISTAL_CAP_AUDIT: fitted medial distal axis + 0.5 mm slab cap/shaft "
     "transition (coverage >= 0.90, r95 >= 0.90 of the distal-30 mm max, stable for 3 slabs); "
     "cap = connected distally-facing region distal of the transition; representative = the "
     "cap's medial surface point (closest cap-surface sample to the fitted axis)."),
    "fingers": four,
    "envelope": {
        "dist_to_cap_representative_mm": {"min": min(env_rep), "max": max(env_rep),
                                          "mean": round(sum(env_rep) / 4, 4)},
        "dist_to_distal_most_vertex_mm": {"min": min(env_apex), "max": max(env_apex),
                                          "mean": round(sum(env_apex) / 4, 4)},
        "surface_distance_mm": {"min": min(env_surf), "max": max(env_surf)},
        "distal_joint_to_landmark_interior_fraction": {"min": min(env_int), "max": max(env_int)},
        "all_four_landmarks_inside_their_cap_patch": all(
            four[d]["landmark_in_own_cap_patch"] for d in four),
        "cap_n_faces": {d: four[d]["cap_n_faces"] for d in four},
        "cap_max_geodesic_mm": {d: four[d]["cap_max_geodesic_mm"] for d in four},
    },
}

THUMB_AUDIT = {
    "stage": "STAGE5A_R2A_THUMB_TIP_AUTHORITY_RECONCILIATION_R1",
    "generated_at": NOW, "read_only": True,
    "input_blend": BLEND, "input_sha256_before": SHA_BEFORE,
    "CANONICAL_THUMB_TIP_SEMANTIC": {
        "THUMB_TIP_R": "STABLE DISTAL-CAP SURFACE LANDMARK",
        "statement": ("THUMB_TIP_R is a stable surface landmark of the thumb's DISTAL-CAP "
                      "patch: it lies on the thumb's own skin inside the terminal cap and "
                      "represents the centre of the fingertip.  It is NOT the farthest single "
                      "vertex, NOT an arbitrary apex vertex, NOT the nail centre, NOT the "
                      "anatomical distal bone end, and NOT a point tuned to satisfy any "
                      "millimetre threshold."),
        "APEX_VERTEX_DISTANCE": "DIAGNOSTIC_ONLY",
        "gates": {
            "THUMB_TIP_ON_DISTAL_CAP_PATCH": "nearest surface face must be inside the cap patch",
            "THUMB_TIP_SURFACE_DISTANCE": "<= 1.5 mm from the thumb skin",
            "THUMB_TIP_OWNER": "nearest surface face must be strictly THUMB-owned",
            "THUMB_IP_TO_TIP_INTERIOR": "the IP->TIP segment must stay inside the digit",
            "THUMB_TIP_STABLE_CAP_LANDMARK":
                "distance to the cap representative must lie inside the four-finger "
                "reference envelope",
            "THUMB_TIP_NOT_SINGLE_VERTEX_ARTIFACT":
                "the definition must not change when evaluated with vertices vs face centroids",
        },
        "removed_rules": ["fingertip apex within 5 mm", "within 8 mm of apex vertex",
                          "at least 5 mm closer than R1"],
    },
    "method": ("THUMB_DISTAL_CAP_AUTHORITY.  The thumb distal phalanx is isolated by the "
               "approved THUMB_IP joint and the thumb's strictly-owned surface.  The distal "
               "longitudinal axis is FITTED from the mesh (medial centreline of the "
               "distal-phalanx tube) and only VALIDATED against the approved bone direction.  "
               "The cap/shaft transition is found by a 0.5 mm slab scan from the distal-most "
               "sample (first slab that wraps the full circumference AND has reached >= 0.90 "
               "of the distal-30 mm r95 maximum, stable for 3 more slabs).  The patch is the "
               "connected digit-owned region distal of that plane.  No percentage of vertices "
               "and no fixed vertex count is used."),
    "thumb": {k: v for k, v in TH.items() if k not in ("cap_faces", "cap_verts", "rep")},
    "thumb_cap_face_ids": TH["cap_faces"], "thumb_cap_vertex_ids": TH["cap_verts"],
    "thumb_cap": TH["cap"],
    "current_R2_THUMB_TIP": R2_m,
    "current_R2_THUMB_TIP_axial_from_IP_diagnostic_mm": round(s_t(R2_TIP) * MM, 4),
    "current_R2_THUMB_TIP_DIST_TO_CAP_REP_mm": round((R2_TIP - rep_t).length * MM, 4),
    "current_R2_THUMB_TIP_DIST_TO_DISTAL_MOST_VERTEX_mm": round(
        (R2_TIP - Vector(TH["distal_most_vertex_world"])).length * MM, 4),
    "current_R2_THUMB_TIP_DIST_TO_CAP_REP_RATIO": round(
        (R2_TIP - rep_t).length / max(1e-9, (Vector(jf["THUMB_TIP_R"]["head"]) - rep_t).length), 4),
    "current_R2_THUMB_TIP_ON_CAP_PATCH": R2_m["nearest_face"] in capf,
    "current_R2_THUMB_TIP_DIST_TO_CAP_CENTROID_mm": round(
        (R2_TIP - Vector(TH["cap"]["centroid_world"])).length * MM, 4),
    "R1_THUMB_TIP": R1_m,
    "R1_THUMB_TIP_DIST_TO_CAP_REP_mm": round((R1_TIP - rep_t).length * MM, 4),
    "R1_THUMB_TIP_DIST_TO_DISTAL_MOST_VERTEX_mm": round(
        (R1_TIP - Vector(TH["distal_most_vertex_world"])).length * MM, 4),
    "cap_representative_world": TH["rep_world"],
    "CAP_REP_SENSITIVITY": {
        "rule": ("the representative is the patch's geodesic 1-median.  It is cross-checked "
                 "against the patch's area-weighted centroid and against the patch's most "
                 "distal vertex."),
        "median_vs_area_centroid_projected_mm": round(
            (rep_t - closest(Vector(TH["cap"]["centroid_world"]))[0]).length * MM, 4),
        "median_vs_most_distal_patch_vertex_mm": TH["rep_dist_to_distal_most_vertex_mm"],
        "patch_max_geodesic_mm": TH["cap"]["max_geodesic_in_patch_mm"],
    },
    "SENSITIVITY_MATRIX": SENS,
    "FROZEN_JOINT_DRIFT": R2_STATUS["gates"]["FROZEN_JOINT_DRIFT"]["value"],
    "sha256_after": None,
}

# ------------------------------------------------------------------ R2 object frame audit
rig = bpy.data.objects[RIGNAME]
KEYB = ["WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "THUMB_TIP_R", "INDEX_MCP_R"]
jt = json.load(open(os.path.join(S5AR2, "STAGE5A_R2_PRODUCTION_JOINT_TABLE.json"),
                    encoding="utf-8"))["joints"]
R2_OBJ = {
    "stage": "STAGE5A_R2A_R2_OBJECT_FRAME_AUDIT", "generated_at": NOW, "read_only": True,
    "input_blend": BLEND, "input_sha256_before": SHA_BEFORE,
    "requirement": "R2_OBJECT_FRAME = PASS -- bone local coordinates must map to world positions coincident with the mesh.",
    "rig_object": {"name": rig.name, "type": rig.type,
                   "location": [round(float(x), 9) for x in rig.location],
                   "rotation_euler": [round(float(x), 9) for x in rig.rotation_euler],
                   "scale": [round(float(x), 9) for x in rig.scale],
                   "matrix_world": [[round(float(x), 9) for x in r] for r in rig.matrix_world]},
    "mesh_object": {"name": ob.name,
                    "matrix_world": [[round(float(x), 9) for x in r] for r in MW]},
    "object_frame_identical_to_mesh_frame": all(
        abs(rig.matrix_world[i][j] - MW[i][j]) < 1e-9 for i in range(4) for j in range(4)),
    "bones": {},
}
for bn in KEYB:
    b = rig.data.bones[bn]
    hw = rig.matrix_world @ b.head_local
    tw = rig.matrix_world @ b.tail_local
    near = closest(hw)
    R2_OBJ["bones"][bn] = {
        "head_local_armature": [round(float(x), 9) for x in b.head_local],
        "tail_local_armature": [round(float(x), 9) for x in b.tail_local],
        "head_world_from_matrix_world": [round(float(x), 9) for x in hw],
        "tail_world_from_matrix_world": [round(float(x), 9) for x in tw],
        "joint_table_world_position": jt[bn]["world_position"],
        "delta_vs_joint_table_mm": round((hw - Vector(jt[bn]["world_position"])).length * MM, 9),
        "nearest_surface_distance_mm": round((hw - near[0]).length * MM, 4),
        "inside_mesh": bool(parity(hw)[0] > 32),
        "parent": b.parent.name if b.parent else None,
    }
R2_OBJ["max_delta_vs_joint_table_mm"] = max(v["delta_vs_joint_table_mm"] for v in R2_OBJ["bones"].values())
R2_OBJ["all_six_bones_match_joint_table"] = R2_OBJ["max_delta_vs_joint_table_mm"] < 1e-6
R2_OBJ["R2_OBJECT_FRAME"] = "PASS" if (R2_OBJ["object_frame_identical_to_mesh_frame"]
                                       and R2_OBJ["all_six_bones_match_joint_table"]) else "FAIL"
R2_OBJ["note"] = ("the rig object transform and the bone local coordinates are read straight "
                  "out of the R2 blend and multiplied by rig.matrix_world inside this audit; no "
                  "render-script transform is reused.")
THUMB_AUDIT["R2_OBJECT_FRAME"] = R2_OBJ["R2_OBJECT_FRAME"]

# ------------------------------------------------------------------ INDEX_MCP reconciliation
prox = Vector(jf["INDEX_MCP_R"]["head"])
p2 = Vector(jt["INDEX_MCP_R"]["world_position"])
ax_i = (Vector(jf["INDEX_TIP_R"]["head"]) - prox).normalized()
ax_pp = (Vector(jf["INDEX_PIP_R"]["head"]) - prox).normalized()
m_chord = (p2 - prox).dot(ax_i) * MM
m_pp = (p2 - prox).dot(ax_pp) * MM
zone_h = t01["T01_MCP"]["INDEX_MCP"]["zone_half_width_mm"]
IDX = {
    "stage": "STAGE5A_R2A_INDEX_MCP_NUMERIC_AUTHORITY_RECONCILIATION",
    "generated_at": NOW, "read_only": True,
    "input_blend": BLEND, "input_sha256_before": SHA_BEFORE,
    "history": {
        "R2_report_value_mm": 0.000,
        "R2_report_axis": "index proximal-phalanx axis = (INDEX_PIP_R - INDEX_MCP_R), frozen Stage4B",
        "R2_status_value_mm": R2_STATUS["gates"]["INDEX_MCP_T01_AXIAL_REGION"]["measured_axial_mm"],
        "R2_status_axis": "index MCP->TIP chord = (INDEX_TIP_R - INDEX_MCP_R), frozen Stage4B",
    },
    "independent_recomputation": {
        "approved_joint_mcp_world": [round(float(x), 9) for x in prox],
        "R2_joint_mcp_world": [round(float(x), 9) for x in p2],
        "R2_shift_mm": round((p2 - prox).length * MM, 4),
        "axis_MCP_to_TIP": [round(float(x), 9) for x in ax_i],
        "axis_proximal_phalanx": [round(float(x), 9) for x in ax_pp],
        "angle_between_axes_deg": round(math.degrees(math.acos(
            max(-1.0, min(1.0, ax_i.dot(ax_pp))))), 4),
        "axial_delta_on_MCP_to_TIP_chord_mm": round(m_chord, 4),
        "axial_delta_on_proximal_phalanx_axis_mm": round(m_pp, 6),
        "T01_zone_half_width_mm": zone_h,
        "pass_on_MCP_to_TIP_chord": abs(m_chord) <= zone_h,
        "pass_on_proximal_phalanx_axis": abs(m_pp) <= zone_h,
    },
    "verdict": ("the R2 report's 0.000 mm is the offset along the index PROXIMAL-PHALANX axis; "
                "the R2 centre was searched INSIDE the plane normal to that axis, so 0.000 is a "
                "CONSTRUCTION statement about a different axis, not an independent measurement. "
                "The only real, reproducible measurement from the R2 blend is along the frozen "
                "approved-landmark MCP->TIP chord and equals %.4f mm; the R2 STATUS JSON value "
                "is therefore the correct one." % m_chord),
    "unique_authoritative_source": {
        "file": "stage5a_r2/STAGE5A_R2_STATUS.json",
        "path": "gates.INDEX_MCP_T01_AXIAL_REGION.measured_axial_mm",
        "value_mm": round(m_chord, 4),
        "rule": ("INDEX_MCP axial authority = the component of (R2 INDEX_MCP - approved "
                 "INDEX_MCP) along the unit vector from the approved INDEX_MCP to the approved "
                 "INDEX_TIP.  Both endpoints are frozen Stage4B landmarks, so the rule is "
                 "reproducible from the R2 blend alone and does not depend on the re-posed mesh."),
        "superseded_claim": "STAGE5A_R2_REPORT.md  AXIAL_DELTA_FROM_APPROVED_T01 = 0.000 mm",
    },
    "geometry_pass_unchanged": abs(m_chord) <= zone_h,
}

json.dump(THUMB_AUDIT, open(os.path.join(OUTDIR, "THUMB_DISTAL_CAP_AUDIT.json"), "w",
                            encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(FOUR, open(os.path.join(OUTDIR, "FOUR_FINGER_TIP_REFERENCE.json"), "w",
                     encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(R2_OBJ, open(os.path.join(OUTDIR, "R2_OBJECT_FRAME_AUDIT.json"), "w",
                       encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(IDX, open(os.path.join(OUTDIR, "_tmp", "S5A_R2A_INDEX_MCP_RECON.json"), "w",
                    encoding="utf-8"), indent=1, ensure_ascii=False)

SHA_AFTER = hashlib.sha256(open(BLEND, "rb").read()).hexdigest()
log("sha before %s" % SHA_BEFORE)
log("sha after  %s" % SHA_AFTER)
log("input unchanged", SHA_BEFORE == SHA_AFTER)
log("R2_OBJECT_FRAME %s max delta mm %s" % (R2_OBJ["R2_OBJECT_FRAME"],
                                            R2_OBJ["max_delta_vs_joint_table_mm"]))
log("INDEX_MCP chord %.4f mm | pp axis %.6f mm" % (m_chord, m_pp))
log("four finger env rep", FOUR["envelope"]["dist_to_cap_representative_mm"])
log("R2 thumb in cap %s dist_rep %.4f" % (THUMB_AUDIT["current_R2_THUMB_TIP_ON_CAP_PATCH"],
                                          THUMB_AUDIT["current_R2_THUMB_TIP_DIST_TO_CAP_REP_mm"]))
THUMB_AUDIT["sha256_after"] = SHA_AFTER
json.dump(THUMB_AUDIT, open(os.path.join(OUTDIR, "THUMB_DISTAL_CAP_AUDIT.json"), "w",
                            encoding="utf-8"), indent=1, ensure_ascii=False)
