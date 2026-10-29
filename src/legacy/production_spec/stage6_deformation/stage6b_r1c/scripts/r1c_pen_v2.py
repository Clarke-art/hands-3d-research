# =====================================================================================
# STAGE6B_R1C -- PENETRATION VISUAL ADJUDICATION  (EVIDENCE ONLY, NO MODEL CHANGE)
# -------------------------------------------------------------------------------------
# v2: single unified classification rule, labels always describe the pair actually drawn,
#     solid z-buffered surface renders, real mesh/plane cross-sections, 6 evidence types
#     per pose (A..F of the round spec).
# =====================================================================================
import os
import sys
import json
import math
import datetime
from collections import Counter, deque

import bpy
import numpy as np
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import r1c_pen_common as R                                          # noqa: E402

NOW = datetime.datetime.now().astimezone().isoformat()
MM = R.MM
LOG = []


def log(s):
    LOG.append(s)
    print("[R1C-PEN] " + s, flush=True)


TAG = {"CMC_OPP_30": "CMC_OPP30", "CMC_MCP_L3": "CMC_MCP_L3", "FULL_OPP_L3": "FULL_OPP_L3"}
CASES = ["CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]

# ---------------------------------------------------------------- frozen context
ctx = R.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
POLY = ctx["poly"]
probe = R.K.load_probe_sets()
PART = R.K.r2_partition(ctx, ref)
CORRECT = R.K.build_corrected_ownership(ctx, ref, PART["partition"], probe)
OWN = CORRECT["corrected"]                    # DIGIT_OWNERSHIP_AUTHORITY_R2

FACE_OWN = []
for p in POLY:
    c = Counter(OWN[v] for v in p)
    m = c.most_common()
    top = [k for k, v in m if v == m[0][1]]
    FACE_OWN.append(top[0] if len(top) == 1 else sorted(top)[0])

CM = dict((c["case_id"], c) for c in
          json.load(open(R.K.PROVENANCE["stage6b_case_matrix"], encoding="utf-8"))["cases"])

bpy.ops.wm.open_mainfile(filepath=R.K.S6B_R1B_HARNESS)
ob = bpy.data.objects[R.MESH_OBJ]
rig = bpy.data.objects[R.RIG_OBJ]
MW = ob.matrix_world.copy()
HARNESS_SHA = R.K.sha256(R.K.S6B_R1B_HARNESS)
MASTER_SHA = R.K.sha256(R.K.R1C_MASTER)
log("harness = %s" % R.K.S6B_R1B_HARNESS)
log("harness sha256 = %s" % HARNESS_SHA)
log("R1C master = %s" % R.K.R1C_MASTER)
log("R1C master sha256 = %s" % MASTER_SHA)


def pose_case(cid):
    c = CM[cid]
    q = c["cmc_quaternion_local"]
    R.B.reset_pose(rig)
    pb = rig.pose.bones["THUMB_CMC_R"]
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion((q[0], q[1], q[2], q[3]))
    if c["mcp_deg"]:
        p = rig.pose.bones["THUMB_MCP_R"]
        p.rotation_mode = 'QUATERNION'
        p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-c["mcp_deg"]))
    if c["ip_deg"]:
        p = rig.pose.bones["THUMB_IP_R"]
        p.rotation_mode = 'QUATERNION'
        p.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-c["ip_deg"]))
    R.B.update()
    return R.B.evaluate(ob, MW)[0]


def centroid(V, p):
    return sum((V[v] for v in p), Vector()) / len(p)


def tri_of(V, t):
    return (V[t[0]], V[t[1]], V[t[2]])


BASE_PAIRS = R.B.intersect_pairs(V0, POLY)
TRIS = R.tris_of(POLY, V0)
FACE_TRIS = {}
for fi, t in TRIS:
    FACE_TRIS.setdefault(fi, []).append(t)
FACE_VERTS = [set(p) for p in POLY]

# mesh characteristic edge length (scale reference)
_el = sorted((V0[a] - V0[b]).length * MM for a, b in EDGES)
CHARACTERISTIC_EDGE_MM = _el[len(_el) // 2]
log("bind baseline intersecting face pairs = %d ; characteristic edge = %.4f mm"
    % (len(BASE_PAIRS), CHARACTERISTIC_EDGE_MM))


def tri_mean_edge(t, V):
    a, b, c = V[t[0]], V[t[1]], V[t[2]]
    return ((a - b).length + (b - c).length + (c - a).length) / 3.0 * MM


def face_area(V, p):
    a = Vector((0.0, 0.0, 0.0))
    for i in range(len(p)):
        a = a + V[p[i]].cross(V[p[(i + 1) % len(p)]])
    return 0.5 * a.length


def seg2_seg2(p1, p2, q1, q2):
    """2D segment/segment intersection (screen space), returns point or None"""
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x3, y3 = q1[0], q1[1]
    x4, y4 = q2[0], q2[1]
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if abs(d) < 1e-12:
        return None
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    if -1e-9 <= t <= 1 + 1e-9 and -1e-9 <= u <= 1 + 1e-9:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def pair_evidence(V, fa, fb):
    """exact geometric evidence for one face pair.

    `local_edge_mm` is taken from the BIND (undeformed) mesh, so the depth / resolution
    ratio answers the physically meaningful question: does the crossing exceed the mesh's
    own facet resolution at this location?  Using the deformed triangles would let a
    stretched region mask a real penetration."""
    best = {"intersect": False, "depth_mm": 0.0, "seg_mm": 0.0, "pts": [],
            "local_edge_mm": 0.0, "tri_pairs": 0}
    lens = []
    dmax = 0.0
    for ta in FACE_TRIS.get(fa, []):
        for tb in FACE_TRIS.get(fb, []):
            A = tri_of(V, ta)
            B3 = tri_of(V, tb)
            lens.append(0.5 * (tri_mean_edge(ta, V0) + tri_mean_edge(tb, V0)))
            pts, ok = R.tri_tri_intersection(A, B3)
            if ok:
                best["intersect"] = True
                best["seg_mm"] = max(best["seg_mm"], R.seg_len(pts) * MM)
                if len(pts) > len(best["pts"]):
                    best["pts"] = [list(x) for x in pts]
                # the poke is only meaningful for a triangle pair that REALLY crosses
                dmax = max(dmax, R.poke_depth(A, B3) * MM, R.poke_depth(B3, A) * MM)
    best["depth_mm"] = dmax
    best["tri_pairs"] = len(lens)
    best["local_edge_mm"] = (sum(lens) / len(lens)) if lens else CHARACTERISTIC_EDGE_MM
    return best


def proxy_depth(V, fa, fb):
    """EXACTLY the frozen Stage6B penetration-proxy predicate"""
    return R.stage6b_proxy(V, POLY, fa, fb)


def cls_of(x, y):
    s = {FACE_OWN[x], FACE_OWN[y]}
    if s == {"THUMB", "INDEX"}:
        return "THUMB_INDEX"
    if "THUMB" in s and "wrist" in s:
        return "THUMB_PALM"
    if "THUMB" in s and (s & {"MIDDLE", "RING", "LITTLE"}):
        return "THUMB_OTHER_DIGIT"
    if s == {"THUMB"}:
        return "INTRA_THUMB"
    return "OTHER"


def components(faces):
    """connected components of a face set through shared mesh edges"""
    faces = sorted(faces)
    idx = dict((f, i) for i, f in enumerate(faces))
    parent = list(range(len(faces)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    edge_map = {}
    for f in faces:
        p = POLY[f]
        for i in range(len(p)):
            k = tuple(sorted((p[i], p[(i + 1) % len(p)])))
            edge_map.setdefault(k, []).append(f)
    for k, fs in edge_map.items():
        for j in range(1, len(fs)):
            a, b = find(idx[fs[0]]), find(idx[fs[j]])
            if a != b:
                parent[a] = b
    groups = {}
    for f in faces:
        groups.setdefault(find(idx[f]), set()).add(f)
    return sorted(groups.values(), key=len, reverse=True)


# =====================================================================================
# MEASURE
# =====================================================================================
RESULTS = {}
for cid in CASES:
    V = pose_case(cid)
    newp = sorted(R.B.intersect_pairs(V, POLY) - BASE_PAIRS)
    ev = []
    for fa, fb in newp:
        e = pair_evidence(V, fa, fb)
        pd = proxy_depth(V, fa, fb)
        ev.append((pd, fa, fb, e))
    ev.sort(key=lambda t: (-t[0], t[1], t[2]))
    real = [x for x in ev if x[3]["intersect"]]
    realf = set()
    for _pd, fa, fb, _e in real:
        realf.add(fa)
        realf.add(fb)
    comps = components(realf)
    RESULTS[cid] = {
        "V": V, "newp": newp, "ev": ev, "real": real,
        "real_faces": realf, "comps": comps,
        "counts": {
            "new_intersecting_face_pairs": len(newp),
            "real_intersecting_pairs": len(real),
            "real_intersecting_face_pairs_frac": R.K.rr(len(real) / max(1, len(newp)), 6),
            "affected_face_count": len(realf),
            "connected_components": len(comps),
            "largest_component_faces": (len(comps[0]) if comps else 0),
            "total_intersection_segment_mm": R.K.rr(sum(x[3]["seg_mm"] for x in real), 6),
        },
    }

# per class statistics + per class worst pair
for cid in CASES:
    V = RESULTS[cid]["V"]
    ev = RESULTS[cid]["ev"]
    stats = {}
    worst = {}
    for pd_, x, y, e_ in ev:
        k = cls_of(x, y)
        st = stats.setdefault(k, {"pairs": 0, "real_pairs": 0, "faces": set(),
                                  "max_proxy_mm": 0.0, "max_poke_mm": 0.0,
                                  "max_seg_mm": 0.0, "max_poke_over_edge": 0.0})
        st["pairs"] += 1
        st["max_proxy_mm"] = max(st["max_proxy_mm"], pd_)
        if e_["intersect"]:
            st["real_pairs"] += 1
            st["faces"].add(x)
            st["faces"].add(y)
            st["max_poke_mm"] = max(st["max_poke_mm"], e_["depth_mm"])
            st["max_seg_mm"] = max(st["max_seg_mm"], e_["seg_mm"])
            st["max_poke_over_edge"] = max(st["max_poke_over_edge"],
                                           e_["depth_mm"] / max(1e-9, e_["local_edge_mm"]))
        if k not in worst or pd_ > worst[k][0]:
            worst[k] = (pd_, x, y, e_)
    for k, st in stats.items():
        st["affected_face_count"] = len(st.pop("faces"))
    RESULTS[cid]["class_stats"] = stats
    RESULTS[cid]["class_worst"] = worst
    comp_cls = []
    for comp in RESULTS[cid]["comps"]:
        cc = Counter()
        for pd_, x, y, e_ in RESULTS[cid]["real"]:
            if x in comp and y in comp:
                cc[cls_of(x, y)] += 1
        comp_cls.append({"faces": len(comp), "pairs_by_class": dict(cc)})
    RESULTS[cid]["component_classes"] = comp_cls

# =====================================================================================
# CLASSIFICATION (single unified rule, applied to every reported pair)
# =====================================================================================
RULE = {
    "depth_measure": ("footprint-constrained poke depth: the largest perpendicular distance of a "
                      "vertex of one triangle from the other triangle's plane, counted only when "
                      "that vertex projects INSIDE the other triangle"),
    "scale_reference": "the BIND (undeformed) mesh mean edge length of the SAME triangle pair; mesh median edge = %.4f mm"
                       % CHARACTERISTIC_EDGE_MM,
    "CASE_C_PROXY_OVER_ESTIMATION":
        "no real triangle/triangle crossing is found for the pair",
    "CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION":
        "real crossing AND depth >= 1.0 x the pair's own mean edge length "
        "(the sheets pass through each other by more than one facet of the mesh's own resolution)",
    "CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT":
        "real crossing AND depth < 1.0 x the pair's own mean edge length "
        "(the sheets touch / graze; the crossing is within the mesh's own facet resolution)",
}


def classify(e):
    if not e["intersect"]:
        return "CASE_C_PROXY_OVER_ESTIMATION"
    ratio = e["depth_mm"] / max(1e-9, e["local_edge_mm"])
    if ratio >= 1.0:
        return "CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION"
    return "CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT"


def ratio_of(e):
    return R.K.rr(e["depth_mm"] / max(1e-9, e["local_edge_mm"]), 6)


FOCUS_ORDER = ("THUMB_INDEX", "THUMB_PALM", "THUMB_OTHER_DIGIT", "INTRA_THUMB", "OTHER")
for cid in CASES:
    V = RESULTS[cid]["V"]
    # overall max pair (by the frozen proxy) and adjudication focus pair
    mx = RESULTS[cid]["ev"][0] if RESULTS[cid]["ev"] else None
    RESULTS[cid]["max"] = None
    if mx is not None:
        _pd, fa, fb, e = mx
        ca_, cb_ = centroid(V, POLY[fa]), centroid(V, POLY[fb])
        RESULTS[cid]["max"] = {
            "face_a": fa, "face_b": fb, "verts_a": sorted(POLY[fa]), "verts_b": sorted(POLY[fb]),
            "own_a": FACE_OWN[fa], "own_b": FACE_OWN[fb], "pair_class": cls_of(fa, fb),
            "proxy_depth_mm": R.K.rr(_pd, 6),
            "centroid_a": [R.K.rr(x, 9) for x in ca_],
            "centroid_b": [R.K.rr(x, 9) for x in cb_],
            "face_area_a_mm2": R.K.rr(face_area(V, POLY[fa]) * MM * MM, 6),
            "face_area_b_mm2": R.K.rr(face_area(V, POLY[fb]) * MM * MM, 6),
            "actual": {"intersect": e["intersect"],
                       "poke_depth_mm": R.K.rr(e["depth_mm"], 6),
                       "intersection_segment_mm": R.K.rr(e["seg_mm"], 6),
                       "local_bind_edge_mm": R.K.rr(e["local_edge_mm"], 6),
                       "poke_over_local_bind_edge": ratio_of(e)},
            "classification": classify(e),
        }
    foc = None
    for k in FOCUS_ORDER:
        if k in RESULTS[cid]["class_worst"]:
            pd_, fa, fb, e = RESULTS[cid]["class_worst"][k]
            ca_, cb_ = centroid(V, POLY[fa]), centroid(V, POLY[fb])
            foc = {
                "class": k, "face_a": fa, "face_b": fb,
                "verts_a": sorted(POLY[fa]), "verts_b": sorted(POLY[fb]),
                "own": [FACE_OWN[fa], FACE_OWN[fb]],
                "proxy_mm": R.K.rr(pd_, 6),
                "centroid": [R.K.rr(x, 9) for x in (ca_ + cb_) * 0.5],
                "centroid_a": [R.K.rr(x, 9) for x in ca_],
                "centroid_b": [R.K.rr(x, 9) for x in cb_],
                "actual": {"intersect": e["intersect"],
                           "poke_depth_mm": R.K.rr(e["depth_mm"], 6),
                           "intersection_segment_mm": R.K.rr(e["seg_mm"], 6),
                           "local_bind_edge_mm": R.K.rr(e["local_edge_mm"], 6),
                           "poke_over_local_bind_edge": ratio_of(e)},
                "classification": classify(e),
            }
            break
    RESULTS[cid]["focus"] = foc

for cid in CASES:
    c = RESULTS[cid]["counts"]
    f = RESULTS[cid]["focus"]
    m = RESULTS[cid]["max"]
    log("%-12s pairs=%d real=%d faces=%d comps=%d largest=%d total_seg=%.2f mm"
        % (cid, c["new_intersecting_face_pairs"], c["real_intersecting_pairs"],
           c["affected_face_count"], c["connected_components"],
           c["largest_component_faces"], c["total_intersection_segment_mm"]))
    log("   OVERALL MAX  %-17s proxy=%.4f poke=%.4f edge=%.4f ratio=%.4f -> %s"
        % (m["pair_class"], m["proxy_depth_mm"], m["actual"]["poke_depth_mm"],
           m["actual"]["local_bind_edge_mm"], m["actual"]["poke_over_local_bind_edge"],
           m["classification"]))
    log("   FOCUS        %-17s proxy=%.4f poke=%.4f edge=%.4f ratio=%.4f -> %s"
        % (f["class"], f["proxy_mm"], f["actual"]["poke_depth_mm"],
           f["actual"]["local_bind_edge_mm"], f["actual"]["poke_over_local_bind_edge"],
           f["classification"]))
    for k, st in sorted(RESULTS[cid]["class_stats"].items()):
        log("     %-18s pairs=%3d real=%3d faces=%3d maxproxy=%.4f maxpoke=%.4f maxseg=%.4f ratio=%.4f"
            % (k, st["pairs"], st["real_pairs"], st["affected_face_count"],
               st["max_proxy_mm"], st["max_poke_mm"], st["max_seg_mm"], st["max_poke_over_edge"]))


# =====================================================================================
# RENDER
# =====================================================================================
LIGHT = Vector((0.42, -0.30, 0.85)).normalized()
COL = {"THUMB": (0.90, 0.55, 0.45), "INDEX": (0.42, 0.63, 0.95),
       "MIDDLE": (0.45, 0.80, 0.60), "RING": (0.72, 0.52, 0.90),
       "LITTLE": (0.92, 0.85, 0.42), "wrist": (0.62, 0.62, 0.60)}
HILITE = (1.0, 0.15, 0.75)
W_, H_ = 1500, 1100


def shade(n):
    return 0.30 + 0.70 * abs(n.dot(LIGHT))


def fit_view(centre, dirv, up, V, margin=1.06):
    r_, u_ = R.ortho_basis(Vector(dirv), Vector(up))
    c = Vector(centre)
    mx = my = 0.0
    for p in V:
        q = p - c
        mx = max(mx, abs(q.dot(r_)))
        my = max(my, abs(q.dot(u_)))
    hw = max(mx, my * float(W_) / float(H_)) * margin
    return R.View(c, dirv, up, hw * MM, W_, H_)


def draw_mesh(cv, view, V, tri_list, highlight=None, alpha=1.0, blend=False):
    for fi, t in tri_list:
        base = HILITE if (highlight and fi in highlight) else COL.get(FACE_OWN[fi], (0.7, 0.7, 0.7))
        n = R.face_normals(V, [POLY[fi]])[0]
        sh = shade(n)
        cv.tri(view.proj(V[t[0]]), view.proj(V[t[1]]), view.proj(V[t[2]]),
               sh, base, alpha=alpha, blend=blend)


def draw_section(cv, view, V, p0, nsec, thick=1):
    segs = []
    for fi, p in enumerate(POLY):
        for t in FACE_TRIS.get(fi, []):
            idx = list(t)
            d = [(V[i] - p0).dot(nsec) for i in idx]
            pts = []
            for k in range(3):
                a, b = idx[k], idx[(k + 1) % 3]
                da, db = d[k], d[(k + 1) % 3]
                if (da > 0) != (db > 0):
                    tt = da / (da - db)
                    pts.append(V[a] + (V[b] - V[a]) * tt)
            if len(pts) >= 2:
                segs.append((FACE_OWN[fi], pts[0], pts[1]))
    for own, a, b in segs:
        cv.line(view.proj(a), view.proj(b), COL.get(own, (1, 1, 1)), thick, 1.0)
    return segs


def legend(cv, x, y, extra=()):
    yy = y
    for k in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE", "wrist"):
        cv.px(x + 6, yy + 6, COL[k], 6)
        R.text(cv, x + 22, yy, k, 2)
        yy += 22
    yy += 6
    for s, c in extra:
        R.text(cv, x, yy, s, 2, c)
        yy += 20


def label(cv, x, y, lines, size=2, c=(0.95, 0.95, 0.95)):
    yy = y
    for s in lines:
        R.text(cv, x, yy, s, size, c)
        yy += 16 * size


def pair_label(cid, pref, r):
    """label block that ALWAYS describes the pair it is drawn for"""
    return ["PROXY %.4f MM" % r["proxy_mm"],
            "REAL CROSSING %s / SEG %.4f MM" % (r["actual"]["intersect"],
                                                r["actual"]["intersection_segment_mm"]),
            "POKE %.4f MM / BIND LOCAL EDGE %.4f MM = %.4f"
            % (r["actual"]["poke_depth_mm"], r["actual"]["local_bind_edge_mm"],
               r["actual"]["poke_over_local_bind_edge"]),
            "CLASS %s" % r["classification"],
            "PAIR %s" % r["class"]]


for cid in CASES:
    V = RESULTS[cid]["V"]
    foc = RESULTS[cid]["focus"]
    mx = RESULTS[cid]["max"]
    fa, fb = foc["face_a"], foc["face_b"]
    ca_ = Vector(foc["centroid_a"])
    cb_ = Vector(foc["centroid_b"])
    contact = (ca_ + cb_) * 0.5
    nra = R.face_normal_of(V, POLY[fa]).normalized()
    nrb = R.face_normal_of(V, POLY[fb]).normalized()
    tag = TAG[cid]
    hi = set(RESULTS[cid]["real_faces"])
    cen = sum(V, Vector()) / NV

    # ---------------------------------------------------------------- A. SOLID SURFACE (whole hand)
    cv = R.Canvas(W_, H_)
    vw = fit_view(cen, (0.55, 0.42, 0.72), (0, 0, 1), V)
    draw_mesh(cv, vw, V, TRIS)
    cv.px(*vw.proj(contact)[:2], (1.0, 0.15, 0.75), 7)
    cv.px(*vw.proj((Vector(mx["centroid_a"]) + Vector(mx["centroid_b"])) * 0.5)[:2],
          (0.15, 1.0, 0.95), 5)
    R.text(cv, 24, 20, "%s  SOLID SURFACE (OBLIQUE) -- EVIDENCE A" % tag, 3)
    label(cv, 24, 60, ["OVERALL MAX PAIR: %s PROXY %.4f MM / %s"
                       % (mx["pair_class"], mx["proxy_depth_mm"], mx["classification"]),
                       "ADJUDICATION FOCUS: %s PROXY %.4f MM / %s"
                       % (foc["class"], foc["proxy_mm"], foc["classification"])], 2)
    R.text(cv, 24, 1050, "SOLID TRIANGLE MESH, Z-BUFFER, NO POINT CLOUD. "
                         "MAGENTA = DEEPEST FOCUS PAIR ; CYAN = OVERALL MAX PAIR.", 2)
    legend(cv, 1180, 30)
    R.save(cv, "STAGE6B_R1C_%s_SOLID_SURFACE.png" % tag)
    log("rendered A SOLID_SURFACE %s" % tag)

    # ---------------------------------------------------------------- B. CONTACT CLOSEUP
    cv = R.Canvas(W_, H_)
    vw2 = R.View(contact, nra, (0, 0, 1), 18.0, W_, H_)
    draw_mesh(cv, vw2, V, TRIS)
    cv.px(*vw2.proj(contact)[:2], (1.0, 0.15, 0.75), 7)
    R.text(cv, 24, 20, "%s  CONTACT CLOSEUP (SOLID SURFACE) -- EVIDENCE B" % tag, 3)
    label(cv, 24, 56, ["VIEW ALONG THE FOCUS FACE NORMAL, 36 MM FIELD"] + pair_label(cid, "f", foc), 2)
    R.save(cv, "STAGE6B_R1C_%s_CONTACT_CLOSEUP.png" % tag)
    log("rendered B CONTACT_CLOSEUP %s" % tag)

    # ---------------------------------------------------------------- C. FACE HIGHLIGHT
    cv = R.Canvas(W_, H_)
    draw_mesh(cv, vw, V, TRIS, highlight=hi)
    R.text(cv, 24, 20, "%s  CONTACT FACE HIGHLIGHT -- EVIDENCE C" % tag, 3)
    label(cv, 24, 56, ["MAGENTA = EVERY FACE WITH A REAL TRIANGLE/TRIANGLE CROSSING",
                       "%d FACES / %d COMPONENT(S), LARGEST %d FACES / TOTAL SEAM %.2f MM"
                       % (RESULTS[cid]["counts"]["affected_face_count"],
                          RESULTS[cid]["counts"]["connected_components"],
                          RESULTS[cid]["counts"]["largest_component_faces"],
                          RESULTS[cid]["counts"]["total_intersection_segment_mm"])], 2)
    legend(cv, 1180, 30, extra=[("CLOSEUP FIELD 36 MM", (1, 1, 1))])
    R.save(cv, "STAGE6B_R1C_%s_FACE_HIGHLIGHT.png" % tag)
    log("rendered C FACE_HIGHLIGHT %s" % tag)

    # ---------------------------------------------------------------- D. TRANSPARENT OVERLAY
    cv = R.Canvas(W_, H_)
    vwo = R.View(contact, nra, (0, 0, 1), 26.0, W_, H_)
    partner = foc["own"][1] if foc["own"][0] == "THUMB" else foc["own"][0]
    sub_a = [(fi, t) for fi, t in TRIS if FACE_OWN[fi] == "THUMB"]
    sub_b = [(fi, t) for fi, t in TRIS if FACE_OWN[fi] == partner]
    draw_mesh(cv, vwo, V, sub_a, alpha=0.40, blend=True)
    draw_mesh(cv, vwo, V, sub_b, alpha=0.40, blend=True)
    R.text(cv, 24, 20, "%s  TRANSPARENT OVERLAY (ALPHA) -- EVIDENCE D" % tag, 3)
    label(cv, 24, 56, ["ONLY THE TWO ADJUDICATED SHEETS ARE DRAWN, ALPHA-BLENDED",
                       "RELATION ONLY - NOT A DEPTH MEASUREMENT",
                       "SHEET 1 = THUMB (SALMON) ; SHEET 2 = %s" % partner], 2)
    R.save(cv, "STAGE6B_R1C_%s_TRANSPARENT_OVERLAY.png" % tag)
    log("rendered D TRANSPARENT_OVERLAY %s" % tag)

    # ---------------------------------------------------------------- E. CROSS SECTION
    nsec = nra.cross(nrb)
    if nsec.length < 0.25:
        nsec = nra.cross(Vector((0, 0, 1)))
        if nsec.length < 0.15:
            nsec = nra.cross(Vector((1, 0, 0)))
    nsec = nsec.normalized()
    cv = R.Canvas(W_, H_)
    vws = R.View(contact, nsec, (0, 0, 1), 24.0, W_, H_)
    segs = draw_section(cv, vws, V, contact, nsec, 2)
    # mark the screen-space crossings of the focus sheet against the other sheet
    A_segs = [s for s in segs if s[0] == FACE_OWN[fa]]
    B_segs = [s for s in segs if s[0] == FACE_OWN[fb]]
    xcross = 0
    for _o1, a1, b1 in A_segs:
        p1, p2 = vws.proj(a1), vws.proj(b1)
        for _o2, a2, b2 in B_segs:
            q1, q2 = vws.proj(a2), vws.proj(b2)
            pt = seg2_seg2(p1, p2, q1, q2)
            if pt is not None:
                cv.px(pt[0], pt[1], (1.0, 1.0, 1.0), 5)
                xcross += 1
    R.text(cv, 24, 20, "%s  CROSS SECTION (REAL MESH / PLANE INTERSECTION) -- EVIDENCE E" % tag, 3)
    label(cv, 24, 56, ["PLANE THROUGH THE DEEPEST FOCUS CONTACT, NORMAL = nA x nB (THE SHEET/SHEET CROSSING LINE)",
                       "CURVES ARE THE EXACT TRIANGLE/PLANE INTERSECTION POLYLINES - NOT A SCREEN OVERLAY",
                       "FOCUS SHEETS CROSS %d TIME(S) IN THIS SECTION (WHITE DOTS)" % xcross,
                       "FOCUS: %s  POKE %.4f MM / BIND LOCAL EDGE %.4f MM = %.4f  -> %s"
                       % (foc["class"], foc["actual"]["poke_depth_mm"],
                          foc["actual"]["local_bind_edge_mm"],
                          foc["actual"]["poke_over_local_bind_edge"], foc["classification"])], 2)
    legend(cv, 1180, 30, extra=[("FOCUS FACE A = %d" % fa, COL[FACE_OWN[fa]]),
                                ("FOCUS FACE B = %d" % fb, COL[FACE_OWN[fb]])])
    R.save(cv, "STAGE6B_R1C_%s_CROSS_SECTION.png" % tag)
    log("rendered E CROSS_SECTION %s (%d crossing marks)" % (tag, xcross))

    # ---------------------------------------------------------------- F. DEPTH VECTOR
    cv = R.Canvas(W_, H_)
    vwd = R.View(contact, nra.cross(Vector((0, 0, 1))).normalized(), (0, 0, 1), 16.0, W_, H_)
    draw_mesh(cv, vwd, V, TRIS)
    # the two focus faces outlined
    for f, cc in ((fa, (1.0, 1.0, 1.0)), (fb, (0.15, 1.0, 0.95))):
        p = POLY[f]
        for i in range(len(p)):
            cv.line(vwd.proj(V[p[i]]), vwd.proj(V[p[(i + 1) % len(p)]]), cc, 2, 1.0)
    # deepest poking vertex -> its projection on the other plane
    best_v = None
    best_d = 0.0
    nplane = (V[POLY[fb][1]] - V[POLY[fb][0]]).cross(V[POLY[fb][2]] - V[POLY[fb][0]])
    nplane = nplane.normalized() if nplane.length > 1e-18 else Vector((0, 0, 1))
    for v in POLY[fa]:
        d = (V[v] - V[POLY[fb][0]]).dot(nplane)
        if abs(d) > best_d:
            best_d = abs(d)
            best_v = v
    if best_v is not None:
        p = V[best_v]
        proj = p - nplane * ((p - V[POLY[fb][0]]).dot(nplane))
        cv.line(vwd.proj(p), vwd.proj(proj), (1.0, 0.15, 0.75), 2, 1.0)
        cv.px(*vwd.proj(p)[:2], (1.0, 0.15, 0.75), 5)
        cv.px(*vwd.proj(proj)[:2], (0.15, 1.0, 0.95), 5)
    R.text(cv, 24, 20, "%s  DEPTH VECTOR CLOSEUP -- EVIDENCE F" % tag, 3)
    label(cv, 24, 56, ["WHITE = FOCUS FACE A (%s) OUTLINE ; CYAN = FOCUS FACE B (%s) OUTLINE"
                       % (FACE_OWN[fa], FACE_OWN[fb]),
                       "MAGENTA = DEEPEST POKING VERTEX OF A ; CYAN DOT = ITS FOOT ON B's PLANE",
                       "POKE %.4f MM  (PROXY %.4f MM, SEGMENT %.4f MM)"
                       % (foc["actual"]["poke_depth_mm"], foc["proxy_mm"],
                          foc["actual"]["intersection_segment_mm"])], 2)
    R.save(cv, "STAGE6B_R1C_%s_DEPTH_VECTOR.png" % tag)
    log("rendered F DEPTH_VECTOR %s" % tag)


# =====================================================================================
# JSON
# =====================================================================================
DATA = {
    "stage": "STAGE6B_R1C_PENETRATION_ADJUDICATION",
    "round_kind": "HUMAN_REVIEW_EVIDENCE_ONLY",
    "generated_at": NOW,
    "model_changes": {"weights": 0, "ownership": 0, "geometry": 0, "topology": 0,
                      "cmc_cage": 0, "bone": 0, "joint": 0, "opposition_vector": 0,
                      "test_angle": 0, "pose_path": 0, "collision_correction": 0,
                      "stage6c": 0, "freeze": 0},
    "harness": {"path": R.K.S6B_R1B_HARNESS.replace("\\", "/"), "sha256": HARNESS_SHA},
    "stage5b_r1c_master": {"path": R.K.R1C_MASTER.replace("\\", "/"), "sha256": MASTER_SHA},
    "ownership_authority": "DIGIT_OWNERSHIP_AUTHORITY_R2 (corrected digit ownership)",
    "poses_reproduced_verbatim": CASES,
    "re_solved_pose": False,
    "bind_baseline_pairs": len(BASE_PAIRS),
    "characteristic_edge_mm": R.K.rr(CHARACTERISTIC_EDGE_MM, 6),
    "classification_rule": RULE,
    "cases": {},
}
for cid in CASES:
    V = RESULTS[cid]["V"]
    DATA["cases"][cid] = {
        "tag": TAG[cid],
        "pose": {"cmc_quaternion_local": CM[cid]["cmc_quaternion_local"],
                 "mcp_deg": CM[cid]["mcp_deg"], "ip_deg": CM[cid]["ip_deg"]},
        "counts": RESULTS[cid]["counts"],
        "component_classes": RESULTS[cid]["component_classes"],
        "class_stats": RESULTS[cid]["class_stats"],
        "adjudication_focus": RESULTS[cid]["focus"],
        "max_pair": RESULTS[cid]["max"],
        "top_real_pairs": [
            {"face_a": x, "face_b": y, "own": [FACE_OWN[x], FACE_OWN[y]],
             "pair_class": cls_of(x, y), "proxy_mm": R.K.rr(pd, 6),
             "poke_depth_mm": R.K.rr(e["depth_mm"], 6),
             "local_bind_edge_mm": R.K.rr(e["local_edge_mm"], 6),
             "poke_over_local_bind_edge": ratio_of(e),
             "intersection_segment_mm": R.K.rr(e["seg_mm"], 6),
             "classification": classify(e)}
            for pd, x, y, e in RESULTS[cid]["ev"][:12]],
        "renders": {
            "A_SOLID_SURFACE": "STAGE6B_R1C_%s_SOLID_SURFACE.png" % TAG[cid],
            "B_CONTACT_CLOSEUP": "STAGE6B_R1C_%s_CONTACT_CLOSEUP.png" % TAG[cid],
            "C_FACE_HIGHLIGHT": "STAGE6B_R1C_%s_FACE_HIGHLIGHT.png" % TAG[cid],
            "D_TRANSPARENT_OVERLAY": "STAGE6B_R1C_%s_TRANSPARENT_OVERLAY.png" % TAG[cid],
            "E_CROSS_SECTION": "STAGE6B_R1C_%s_CROSS_SECTION.png" % TAG[cid],
            "F_DEPTH_VECTOR": "STAGE6B_R1C_%s_DEPTH_VECTOR.png" % TAG[cid],
        },
    }
P = os.path.join(R.S6B_R1C, "STAGE6B_R1C_PENETRATION_ADJUDICATION.json")
BACKUP = os.path.join(R.S6B_R1C, "_tmp", "STAGE6B_R1C_PENETRATION_ADJUDICATION_v1.json")
if os.path.exists(P) and not os.path.exists(BACKUP):
    os.replace(P, BACKUP)
    log("previous adjudication JSON moved to _tmp/")
json.dump(DATA, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote %s" % P)
open(os.path.join(R.S6B_R1C, "_tmp", "R1C_PEN_LOG.txt"), "w", encoding="utf-8").write("\n".join(LOG))
print("PEN_ADJUDICATE_V2_DONE", flush=True)
