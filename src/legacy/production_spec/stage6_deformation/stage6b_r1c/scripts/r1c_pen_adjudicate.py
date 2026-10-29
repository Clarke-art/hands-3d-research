# =====================================================================================
# STAGE6B_R1C -- PENETRATION VISUAL ADJUDICATION  (evidence only, NO model change)
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
LOG = []


def log(s):
    LOG.append(s)
    print("[R1C-PEN] " + s, flush=True)


# ---------------------------------------------------------------- frozen context
ctx = R.B.build_context()
ref = ctx["ref"]
NV = ref["NV"]
V0 = ref["V0"]
EDGES = ref["EDGES"]
POLY = ctx["poly"]
FO = ctx["FO"]
own_r1a = ctx["own_r1a"]
probe = R.K.load_probe_sets()
PART = R.K.r2_partition(ctx, ref)
CORRECT = R.K.build_corrected_ownership(ctx, ref, PART["partition"], probe)
OWN = CORRECT["corrected"]                 # CORRECTED_DIGIT_OWNERSHIP_R2 (Stage6B R1B)

FACE_OWN = []
for p in POLY:
    c = Counter(OWN[v] for v in p)
    m = c.most_common()
    top = [k for k, v in m if v == m[0][1]]
    FACE_OWN.append(top[0] if len(top) == 1 else sorted(top)[0])

CM = dict((c["case_id"], c) for c in
          json.load(open(R.K.PROVENANCE["stage6b_case_matrix"], encoding="utf-8"))["cases"])
CASES = ["CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"]

# ---------------------------------------------------------------- open the R1B harness
bpy.ops.wm.open_mainfile(filepath=R.K.S6B_R1B_HARNESS)
ob = bpy.data.objects[R.MESH_OBJ]
rig = bpy.data.objects[R.RIG_OBJ]
MW = ob.matrix_world.copy()
log("harness = %s" % R.K.S6B_R1B_HARNESS)
log("harness sha256 = %s" % R.K.sha256(R.K.S6B_R1B_HARNESS))
log("R1C master sha256 = %s" % R.K.sha256(R.K.R1C_MASTER))


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
    V = R.B.evaluate(ob, MW)[0]
    return V


# bind baseline self-intersection (identical predicate to Stage6B)
BASE_PAIRS = R.B.intersect_pairs(V0, POLY)
log("bind baseline intersecting face pairs = %d" % len(BASE_PAIRS))

TRIS = R.tris_of(POLY, V0)
FACE_TRIS = {}
for fi, t in TRIS:
    FACE_TRIS.setdefault(fi, []).append(t)


def centroid(V, p):
    return sum((V[v] for v in p), Vector()) / len(p)


def tri_of(V, t):
    return (V[t[0]], V[t[1]], V[t[2]])


def pair_evidence(V, fa, fb):
    """exact geometric evidence for one face pair"""
    best = {"intersect": False, "depth_mm": 0.0, "seg_mm": 0.0, "pts": []}
    for ta in FACE_TRIS.get(fa, []):
        for tb in FACE_TRIS.get(fb, []):
            A = tri_of(V, ta)
            B3 = tri_of(V, tb)
            pts, ok = R.tri_tri_intersection(A, B3)
            if ok:
                best["intersect"] = True
                best["seg_mm"] = max(best["seg_mm"], R.seg_len(pts) * R.MM)
                if len(pts) > len(best["pts"]):
                    best["pts"] = [list(x) for x in pts]
            best["depth_mm"] = max(best["depth_mm"],
                                   R.poke_depth(A, B3) * R.MM,
                                   R.poke_depth(B3, A) * R.MM)
    return best


def proxy_depth(V, fa, fb):
    """EXACTLY the frozen Stage6B penetration-proxy predicate."""
    return R.stage6b_proxy(V, POLY, fa, fb)


RESULTS = {}
for cid in CASES:
    V = pose_case(cid)
    newp = sorted(R.B.intersect_pairs(V, POLY) - BASE_PAIRS)
    ev = []
    for fa, fb in newp:
        e = pair_evidence(V, fa, fb)
        pd = proxy_depth(V, fa, fb)
        ev.append((pd, fa, fb, e))
    ev.sort(key=lambda x: -x[0])
    real = [e for e in ev if e[3]["intersect"]]
    deep = [e for e in real if e[3]["depth_mm"] >= 0.5]
    # connected components of the real-intersection face graph
    gph = {}
    for pd, fa, fb, e in real:
        gph.setdefault(fa, set()).add(fb)
        gph.setdefault(fb, set()).add(fa)
    seen, comps = set(), []
    for n0 in gph:
        if n0 in seen:
            continue
        q = deque([n0])
        comp = set()
        while q:
            u = q.popleft()
            if u in comp:
                continue
            comp.add(u)
            for w in gph.get(u, ()):
                if w not in comp:
                    q.append(w)
        seen |= comp
        comps.append(comp)
    # classification of the deepest pair (overall) and of the adjudication focus
    if ev:
        pd, fa, fb, e = ev[0]
    else:
        pd, fa, fb, e = 0.0, -1, -1, {"intersect": False, "depth_mm": 0.0, "seg_mm": 0.0}
    ca_ = centroid(V, POLY[fa]) if fa >= 0 else Vector()
    cb_ = centroid(V, POLY[fb]) if fb >= 0 else Vector()
    oa = FACE_OWN[fa] if fa >= 0 else "-"
    ob_ = FACE_OWN[fb] if fb >= 0 else "-"
    pair_class = "-"
    if fa >= 0:
        s = {oa, ob_}
        if s == {"THUMB", "INDEX"}:
            pair_class = "THUMB_INDEX"
        elif "THUMB" in s and "wrist" in s:
            pair_class = "THUMB_PALM"
        elif "THUMB" in s and (s & {"MIDDLE", "RING", "LITTLE"}):
            pair_class = "THUMB_OTHER_DIGIT"
        elif oa == "THUMB" and ob_ == "THUMB":
            pair_class = "INTRA_THUMB"
        else:
            pair_class = "OTHER"
    # normal / direction / nearest points
    na = nb = None
    npa = npb = None
    if fa >= 0:
        na = R.face_normals(V, [POLY[fa]])[0]
        nb = R.face_normals(V, [POLY[fb]])[0]
        ta = tri_of(V, FACE_TRIS[fa][0])
        tb = tri_of(V, FACE_TRIS[fb][0])
        npa = R.closest_point_on_triangle(ca_, *tb)
        npb = R.closest_point_on_triangle(cb_, *ta)
    dvec = (cb_ - ca_)
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

    by_class = {}
    for pd_, x, y, e_ in ev:
        k = cls_of(x, y)
        if k not in by_class or pd_ > by_class[k][0]:
            by_class[k] = (pd_, x, y, e_)

    RESULTS[cid] = {
        "V": V, "newp": newp, "ev": ev, "real": real, "deep": deep, "by_class": by_class,
        "components": [sorted(c) for c in comps],
        "max": {"proxy_depth_mm": R.K.rr(pd, 6), "face_a": fa, "face_b": fb,
                "own_a": oa, "own_b": ob_, "pair_class": pair_class,
                "centroid_a": [R.K.rr(x, 9) for x in ca_] if fa >= 0 else None,
                "centroid_b": [R.K.rr(x, 9) for x in cb_] if fb >= 0 else None,
                "normal_a": [R.K.rr(x, 9) for x in na] if na else None,
                "normal_b": [R.K.rr(x, 9) for x in nb] if nb else None,
                "nearest_point_on_b_from_a": [R.K.rr(x, 9) for x in npa] if npa else None,
                "nearest_point_on_a_from_b": [R.K.rr(x, 9) for x in npb] if npb else None,
                "direction_a_to_b": [R.K.rr(x, 9) for x in dvec] if fa >= 0 else None,
                "verts_a": list(POLY[fa]) if fa >= 0 else None,
                "verts_b": list(POLY[fb]) if fb >= 0 else None,
                "actual": {"intersect": e["intersect"],
                           "vertex_penetration_mm": R.K.rr(e["depth_mm"], 6),
                           "intersection_segment_mm": R.K.rr(e["seg_mm"], 6),
                           "intersection_points": e["pts"][:6]},
                "proxy_depth_mm_rounded": R.K.rr(pd, 6)},
        "counts": {"new_bvh_pairs": len(newp), "real_intersecting_pairs": len(real),
                   "real_depth_ge_0_5mm": len(deep),
                   "connected_components": len(comps),
                   "largest_component_faces": max((len(c) for c in comps), default=0),
                   "total_intersection_segment_mm": R.K.rr(
                       sum(x[3]["seg_mm"] for x in real), 6),
                   "affected_face_count": len(set([f for pd_, x, y, e_ in real
                                                   for f in (x, y)]))},
    }
    focus = None
    for k in ("THUMB_INDEX", "THUMB_PALM", "INTRA_THUMB", "THUMB_OTHER_DIGIT", "OTHER"):
        if k in by_class:
            focus = (k,) + by_class[k]
            break
    RESULTS[cid]["focus"] = {
        "class": focus[0], "proxy_mm": R.K.rr(focus[1], 6), "face_a": focus[2],
        "face_b": focus[3], "own": [FACE_OWN[focus[2]], FACE_OWN[focus[3]]],
        "actual": {"intersect": focus[4]["intersect"],
                   "poke_depth_mm": R.K.rr(focus[4]["depth_mm"], 6),
                   "intersection_segment_mm": R.K.rr(focus[4]["seg_mm"], 6)},
        "centroid": [R.K.rr(x, 9) for x in (centroid(V, POLY[focus[2]]) +
                                            centroid(V, POLY[focus[3]])) * 0.5]}
    log("%-12s new=%d real=%d real>=0.5mm=%d comps=%d | OVERALL maxproxy=%.4f actual=%.4f (%s) | FOCUS %s proxy=%.4f actual=%.4f"
        % (cid, len(newp), len(real), len(deep), len(comps), pd,
           e["depth_mm"], pair_class, focus[0], focus[1], focus[4]["depth_mm"]))
    cls_stats = {}
    for pd_, x, y, ee in ev:
        k = cls_of(x, y)
        st = cls_stats.setdefault(k, {"pairs": 0, "real_pairs": 0,
                                      "max_proxy_mm": 0.0, "max_actual_mm": 0.0,
                                      "max_segment_mm": 0.0, "faces": set()})
        st["pairs"] += 1
        st["max_proxy_mm"] = max(st["max_proxy_mm"], pd_)
        st["max_actual_mm"] = max(st["max_actual_mm"], ee["depth_mm"])
        st["max_segment_mm"] = max(st["max_segment_mm"], ee["seg_mm"])
        if ee["intersect"]:
            st["real_pairs"] += 1
            st["faces"].add(x)
            st["faces"].add(y)
    for k, st in cls_stats.items():
        st["affected_face_count"] = len(st.pop("faces"))
    RESULTS[cid]["class_stats"] = cls_stats
    # class composition of each connected component
    comp_cls = []
    for comp in comps:
        cc = Counter()
        for pd_, x, y, ee in real:
            if x in comp and y in comp:
                cc[cls_of(x, y)] += 1
        comp_cls.append({"faces": len(comp), "pairs_by_class": dict(cc)})
    RESULTS[cid]["component_classes"] = comp_cls
    for k, (pp, x, y, ee) in sorted(by_class.items()):
        log("      %-18s proxy=%.4f mm  actual=%.4f mm  intersect=%s  seg=%.4f mm"
            % (k, pp, ee["depth_mm"], ee["intersect"], ee["seg_mm"]))

# ---------------------------------------------------------------- classification rule
TH_A = 0.5       # mm: visible geometric interpenetration threshold
TH_C = 3.0       # proxy / actual ratio suggesting over-estimation
for cid in CASES:
    r = RESULTS[cid]["max"]
    a = r["actual"]
    if a["intersect"] and a["vertex_penetration_mm"] >= TH_A:
        cls = "CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION"
    elif a["intersect"]:
        cls = "CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT"
    elif r["proxy_depth_mm"] >= TH_A * TH_C:
        cls = "CASE_C_PROXY_OVER_ESTIMATION"
    else:
        cls = "CASE_B_SURFACE_CONTACT_OR_NEAR_CONTACT"
    RESULTS[cid]["max"]["classification"] = cls
    RESULTS[cid]["max"]["ratio_proxy_over_actual"] = (
        R.K.rr(r["proxy_depth_mm"] / max(1e-6, a["vertex_penetration_mm"]), 6)
        if a["vertex_penetration_mm"] > 0 else None)

# =====================================================================================
# RENDER -- solid mesh surface
# =====================================================================================
LIGHT = Vector((0.42, -0.30, 0.85)).normalized()
COL = {"THUMB": (0.90, 0.55, 0.45), "INDEX": (0.42, 0.63, 0.95),
       "MIDDLE": (0.45, 0.80, 0.60), "RING": (0.72, 0.52, 0.90),
       "LITTLE": (0.92, 0.85, 0.42), "wrist": (0.62, 0.62, 0.60)}
HILITE = (1.0, 0.15, 0.75)
WHOLE_C = sum(V0, Vector()) / NV


def shade(n):
    return 0.28 + 0.72 * abs(n.dot(LIGHT))


def draw_mesh(cv, view, V, tri_list, alpha=1.0, blend=False, highlight=None):
    fn_cache = {}
    for fi, t in tri_list:
        base = COL.get(FACE_OWN[fi], (0.7, 0.7, 0.7))
        if highlight and fi in highlight:
            base = HILITE
        n = R.face_normals(V, [POLY[fi]])[0]
        sh = shade(n)
        p0 = view.proj(V[t[0]])
        p1 = view.proj(V[t[1]])
        p2 = view.proj(V[t[2]])
        cv.tri(p0, p1, p2, sh, base, alpha=alpha, blend=blend)


def draw_section(cv, view, V, p0, nsec, half_w):
    """REAL geometric mesh/plane intersection: clip every triangle against the plane."""
    r_, u_ = R.ortho_basis(nsec, Vector((0, 0, 1)))
    segs = []
    for fi, p in enumerate(POLY):
        for t in FACE_TRIS.get(fi, []):
            idx = list(t)
            d = [ (V[i] - p0).dot(nsec) for i in idx ]
            pts = []
            for k in range(3):
                a = idx[k]
                b = idx[(k + 1) % 3]
                da, db = d[k], d[(k + 1) % 3]
                if (da > 0) != (db > 0):
                    tt = da / (da - db)
                    pts.append(V[a] + (V[b] - V[a]) * tt)
            if len(pts) >= 2:
                segs.append((FACE_OWN[fi], pts[0], pts[1]))
    for own, a, b in segs:
        pa = view.proj(a)
        pb = view.proj(b)
        cv.line(pa, pb, COL.get(own, (1, 1, 1)), 1, 1.0)
    return segs


def label(cv, x, y, lines, size=2, c=(0.95, 0.95, 0.95)):
    yy = y
    for s in lines:
        R.text(cv, x, yy, s, size, c)
        yy += 16 * size


for cid in CASES:
    V = RESULTS[cid]["V"]
    m = RESULTS[cid]["max"]
    overall_contact = (Vector(m["centroid_a"]) + Vector(m["centroid_b"])) * 0.5
    # ---- adjudication focus: the deepest THUMB_INDEX / THUMB_PALM pair if it exists
    foc = RESULTS[cid]["focus"]
    fa, fb = foc["face_a"], foc["face_b"]
    ca_ = centroid(V, POLY[fa])
    cb_ = centroid(V, POLY[fb])
    contact = (ca_ + cb_) * 0.5
    nrm = R.face_normal_of(V, POLY[fa]).normalized()
    npa = R.closest_point_on_triangle(ca_, *tri_of(V, FACE_TRIS[fb][0]))
    npb = R.closest_point_on_triangle(cb_, *tri_of(V, FACE_TRIS[fa][0]))
    m = dict(m)
    m.update({"face_a": fa, "face_b": fb, "own_a": FACE_OWN[fa], "own_b": FACE_OWN[fb],
              "centroid_a": [R.K.rr(x, 9) for x in ca_],
              "centroid_b": [R.K.rr(x, 9) for x in cb_],
              "normal_a": [R.K.rr(x, 9) for x in nrm],
              "nearest_point_on_b_from_a": [R.K.rr(x, 9) for x in npa],
              "nearest_point_on_a_from_b": [R.K.rr(x, 9) for x in npb],
              "proxy_depth_mm": foc["proxy_mm"],
              "pair_class": foc["class"],
              "actual": {"intersect": foc["actual"]["intersect"],
                         "vertex_penetration_mm": foc["actual"]["poke_depth_mm"],
                         "intersection_segment_mm": foc["actual"]["intersection_segment_mm"],
                         "intersection_points": []}})
    hi = set()
    for pd_, x, y, e_ in RESULTS[cid]["real"]:
        hi.add(x)
        hi.add(y)
    tag = cid

    # --- A. SOLID SURFACE (oblique, whole hand) ---
    cv = R.Canvas(1500, 1100)
    d_ob = Vector((0.55, 0.42, 0.72)).normalized()
    vw = R.View(WHOLE_C, d_ob, Vector((0, 0, 1)), 115.0, 1500, 1100)
    draw_mesh(cv, vw, V, TRIS)
    cp = vw.proj(contact)
    cv.px(cp[0], cp[1], (1.0, 0.15, 0.75), 6)
    cop = vw.proj(overall_contact)
    cv.px(cop[0], cop[1], (0.15, 1.0, 0.95), 5)
    R.text(cv, 24, 20, "%s SOLID SURFACE (OBLIQUE)" % tag, 3)
    R.text(cv, 24, 1060, "SOLID TRIANGLE MESH WITH Z-BUFFER - NO POINT CLOUD. "
                         "MAGENTA = ADJUDICATION FOCUS (%s) ; CYAN = OVERALL MAX PAIR (%s), %.3f MM PROXY."
                         % (foc["class"], m["pair_class"],
                            RESULTS[cid]["max"]["proxy_depth_mm"]), 2)
    label(cv, 24, 60, ["PROXY %.3f MM / ACTUAL %.3f MM" %
                       (m["proxy_depth_mm"], m["actual"]["vertex_penetration_mm"]),
                       "CLASS %s" % m["classification"],
                       "PAIR %s" % m["pair_class"]], 2)
    R.save(cv, "STAGE6B_R1C_%s_SOLID_SURFACE.png" % tag)
    log("rendered SOLID_SURFACE %s" % tag)

    # --- B. CONTACT CLOSEUP ---
    cv = R.Canvas(1500, 1100)
    aux = Vector((0, 0, 1))
    dv = nrm.cross(aux)
    if dv.length < 0.15:
        dv = nrm.cross(Vector((1, 0, 0)))
    dv = dv.normalized()
    vw2 = R.View(contact, dv, aux, 16.0, 1500, 1100)
    draw_mesh(cv, vw2, V, TRIS)
    R.text(cv, 24, 20, "%s CONTACT CLOSEUP (SOLID SURFACE)" % tag, 3)
    R.text(cv, 24, 1060, "VIEW PERPENDICULAR TO THE CONTACT NORMAL - 32 MM FIELD", 2)
    label(cv, 24, 60, ["FACE A %d (%s) / FACE B %d (%s)" % (fa, m["own_a"], fb, m["own_b"]),
                       "PROXY %.3f MM / ACTUAL %.3f MM" %
                       (m["proxy_depth_mm"], m["actual"]["vertex_penetration_mm"])], 2)
    R.save(cv, "STAGE6B_R1C_%s_CONTACT_CLOSEUP.png" % tag)

    # --- C. FACE HIGHLIGHT ---
    cv = R.Canvas(1500, 1100)
    draw_mesh(cv, vw2, V, TRIS, highlight=hi)
    R.text(cv, 24, 20, "%s CONTACT FACE HIGHLIGHT" % tag, 3)
    label(cv, 24, 60, ["MAGENTA = FACES WITH REAL TRIANGLE/TRIANGLE INTERSECTION: %d FACES"
                       % len(hi),
                       "CONNECTED COMPONENTS: %d ; LARGEST: %d FACES" %
                       (RESULTS[cid]["counts"]["connected_components"],
                        RESULTS[cid]["counts"]["largest_component_faces"]),
                       "TOTAL INTERSECTION SEGMENT PROXY %.3f MM" %
                       RESULTS[cid]["counts"]["total_intersection_segment_mm"]], 2)
    R.save(cv, "STAGE6B_R1C_%s_FACE_HIGHLIGHT.png" % tag)

    # --- E. CROSS SECTION (real mesh/plane intersection) ---
    cv = R.Canvas(1500, 1100)
    nb_ = R.face_normal_of(V, POLY[fb]).normalized()
    nsec = nrm.cross(nb_)
    if nsec.length < 0.25:                       # nearly parallel sheets: no X to show
        nsec = nrm.cross(aux)
        if nsec.length < 0.15:
            nsec = nrm.cross(Vector((1, 0, 0)))
    nsec = nsec.normalized()
    # the section plane is PERPENDICULAR to the surface/surface intersection line, so the
    # two sheets are cut across and appear as two curves crossing in an X
    vw3 = R.View(contact, nsec, aux, 26.0, 1500, 1100)
    segs = draw_section(cv, vw3, V, contact, nsec, 26.0)
    seg_by_class = Counter(o for o, _a, _b in segs if _a is not None)
    R.text(cv, 24, 20, "%s CROSS SECTION (REAL MESH / PLANE INTERSECTION)" % tag, 3)
    label(cv, 24, 60, ["SECTION PLANE THROUGH THE DEEPEST CONTACT, CONTAINING THE "
                       "PENETRATION DIRECTION",
                       "CURVES ARE THE EXACT TRIANGLE / PLANE INTERSECTION POLYLINES",
                       "PLANE NORMAL = THE SURFACE/SURFACE INTERSECTION LINE DIRECTION",
                       "SEGMENTS %d  (%s)" % (len(segs), dict(seg_by_class))], 2)
    yy = 200
    for own in ("THUMB", "INDEX", "wrist"):
        cv.px(1200, yy + 6, COL[own], 6)
        R.text(cv, 1220, yy, "%s SURFACE" % own, 2)
        yy += 26
    R.text(cv, 1200, yy + 10, "DEPTH %.3f MM" % m["actual"]["vertex_penetration_mm"], 2)
    R.text(cv, 1200, yy + 36, "PROXY %.3f MM" % m["proxy_depth_mm"], 2)
    R.save(cv, "STAGE6B_R1C_%s_CROSS_SECTION.png" % tag)

    if cid == "FULL_OPP_L3":
        # --- D. TRANSPARENT OVERLAY ---
        cv = R.Canvas(1500, 1100)
        for grp, al in (("THUMB", 0.45), ("OTHER", 0.45)):
            tl = [(fi, t) for fi, t in TRIS
                  if (FACE_OWN[fi] == "THUMB") == (grp == "THUMB")]
            draw_mesh(cv, vw2, V, tl, alpha=al, blend=True)
        R.text(cv, 24, 20, "%s TRANSPARENT OVERLAY (THUMB / NON-THUMB)" % tag, 3)
        R.text(cv, 24, 1060, "BOTH SURFACES DRAWN WITH ALPHA BLENDING - SPATIAL RELATION "
                             "ONLY, NOT A DEPTH MEASUREMENT", 2)
        R.save(cv, "STAGE6B_R1C_%s_TRANSPARENT_OVERLAY.png" % tag)

        # --- F. DEPTH VECTOR CLOSEUP ---
        cv = R.Canvas(1500, 1100)
        vw4 = R.View(contact, dv, aux, 9.0, 1500, 1100)
        draw_mesh(cv, vw4, V, TRIS, highlight={fa, fb})
        pa = vw4.proj(Vector(m["nearest_point_on_b_from_a"]))
        pb = vw4.proj(Vector(m["nearest_point_on_a_from_b"]))
        cv.line(pa, pb, (1.0, 0.95, 0.10), 3, 1.0)
        cv.px(pa[0], pa[1], (1.0, 0.95, 0.10), 7)
        cv.px(pb[0], pb[1], (0.15, 1.0, 0.95), 7)
        R.text(cv, 24, 20, "%s DEPTH VECTOR CLOSEUP" % tag, 3)
        label(cv, 24, 60, ["YELLOW = POINT ON SURFACE B NEAREST TO SURFACE A CENTROID",
                           "CYAN   = POINT ON SURFACE A NEAREST TO SURFACE B CENTROID",
                           "VECTOR LENGTH IS DRAWN TO SCALE IN THE 18 MM FIELD",
                           "SURFACE-TO-SURFACE GAP / PENETRATION %.3f MM (PROXY)"
                           % m["proxy_depth_mm"],
                           "VERTEX PENETRATION (ACTUAL) %.3f MM"
                           % m["actual"]["vertex_penetration_mm"]], 2)
        cv.px(1200, 300, (1.0, 0.95, 0.10), 6)
        R.text(cv, 1220, 294, "FACE B %d (%s)" % (fb, m["own_b"]), 2)
        cv.px(1200, 330, (0.15, 1.0, 0.95), 6)
        R.text(cv, 1220, 324, "FACE A %d (%s)" % (fa, m["own_a"]), 2)
        cv.px(1200, 360, (1.0, 0.15, 0.75), 6)
        R.text(cv, 1220, 354, "CONTACT NORMAL", 2)
        R.save(cv, "STAGE6B_R1C_%s_DEPTH_VECTOR.png" % tag)
        log("rendered OVERLAY / DEPTH VECTOR for %s" % tag)

# ---------------------------------------------------------------- data outputs
DATA = {"stage": "STAGE6B_R1C_PENETRATION_ADJUDICATION",
        "generated_at": NOW,
        "round_kind": "HUMAN_REVIEW_EVIDENCE_ONLY",
        "model_changes": "NONE (no weight / ownership / geometry / topology / cage / bone / "
                         "joint / opposition-vector / test-angle / pose-path change; no "
                         "collision correction; no production master freeze)",
        "harness": {"path": R.K.S6B_R1B_HARNESS.replace("\\", "/"),
                    "sha256": R.K.sha256(R.K.S6B_R1B_HARNESS)},
        "stage5b_r1c_master": {"path": R.K.R1C_MASTER.replace("\\", "/"),
                               "sha256": R.K.sha256(R.K.R1C_MASTER)},
        "ownership_authority": "DIGIT_OWNERSHIP_AUTHORITY_R2 (Stage6B R1B corrected)",
        "poses_reproduced_verbatim": CASES,
        "re_solved_pose": False,
        "bind_baseline_pairs": len(BASE_PAIRS),
        "threshold": {"CASE_A_visible_interpenetration_mm": 0.5,
                      "CASE_C_over_estimation_ratio": TH_C},
        "cases": {}}
for cid in CASES:
    r = RESULTS[cid]
    DATA["cases"][cid] = {
        "max_pair": r["max"],
        "adjudication_focus": r["focus"],
        "class_stats": r["class_stats"],
        "component_classes": r["component_classes"],
        "counts": r["counts"],
        "connected_components": r["components"][:20],
        "top_real_pairs": [
            {"face_a": x, "face_b": y, "own": [FACE_OWN[x], FACE_OWN[y]],
             "proxy_mm": R.K.rr(pd_, 6), "actual_depth_mm": R.K.rr(e_["depth_mm"], 6),
             "intersection_segment_mm": R.K.rr(e_["seg_mm"], 6)}
            for pd_, x, y, e_ in r["real"][:12]],
    }
json.dump(DATA, open(os.path.join(R.S6B_R1C, "STAGE6B_R1C_PENETRATION_ADJUDICATION.json"),
                     "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump({"log": LOG}, open(os.path.join(R.S6B_R1C, "_tmp", "R1C_PEN_LOG.json"), "w",
                             encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE6B_R1C_PENETRATION_ADJUDICATION.json")
print("PEN_ADJUDICATE_DONE")
