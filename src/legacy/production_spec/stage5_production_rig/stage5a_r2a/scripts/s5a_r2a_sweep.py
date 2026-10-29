# STAGE5A_R2A -- geodesic cap radius sweep (READ-ONLY)
import bpy, sys, os, json, math, heapq
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
ob = bpy.data.objects["Hand  - Realistic"]; me = ob.data
MW = ob.matrix_world
V = [(MW @ v.co).copy() for v in me.vertices]; NV = len(V)
MM = 1000.0
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}


def d_poly(p, poly):
    b = 1e9
    for i in range(len(poly) - 1):
        a, q = poly[i], poly[i + 1]; ab = q - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
        b = min(b, (p - (a + ab * t)).length)
    return b


def chp(D):
    p = [Vector(jf["%s_%s_R" % (D, CHAIN[D][0])]["head"])]
    for s in CHAIN[D]:
        p.append(Vector(jf["%s_%s_R" % (D, s)]["tail"]))
    return p


AC = {D: chp(D) for D in CHAIN}; AC["wrist"] = [AO, Vector(jf["WRIST_R"]["tail"])]
FO = {}
for p in me.polygons:
    c = sum((V[v] for v in p.vertices), Vector()) / len(p.vertices)
    FO[p.index] = min(AC, key=lambda D: d_poly(c, AC[D]))
OF = {D: [p.index for p in me.polygons if FO[p.index] == D] for D in CHAIN}
DV = {D: sorted({v for p in me.polygons if FO[p.index] == D for v in p.vertices}) for D in CHAIN}
EADJ = {}
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    w = (V[a] - V[b]).length
    EADJ.setdefault(a, []).append((b, w)); EADJ.setdefault(b, []).append((a, w))
FADJ = [[] for _ in range(len(me.polygons))]
ef = {}
for p in me.polygons:
    vs = list(p.vertices)
    for i in range(len(vs)):
        ef.setdefault(tuple(sorted((vs[i], vs[(i + 1) % len(vs)]))), []).append(p.index)
for k, fs in ef.items():
    for a in fs:
        for b in fs:
            if a != b:
                FADJ[a].append(b)


def dij(src):
    d = {src: 0.0}; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d.get(u, 1e18) + 1e-15:
            continue
        for w, l in EADJ.get(u, ()):
            if du + l < d.get(w, 1e18) - 1e-16:
                d[w] = du + l; heapq.heappush(pq, (du + l, w))
    return d


R = {}
for D in ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]:
    dseg = "IP" if D == "THUMB" else "DIP"
    P = Vector(jf["%s_%s_R" % (D, dseg)]["head"]); T = Vector(jf["%s_TIP_R" % D]["head"])
    u0 = (T - P).normalized()
    cand = [i for i in DV[D] if (V[i] - P).dot(u0) > 0]
    star = max(cand, key=lambda i: (V[i] - P).length)
    g = dij(star)
    ownf = set(OF[D])
    near_face = min(ownf, key=lambda fi: (sum((V[v] for v in me.polygons[fi].vertices), Vector())
                                          / len(me.polygons[fi].vertices) - V[star]).length)
    rows = []
    for rc in [3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20]:
        # a face belongs if its NEAREST vertex is within R_cap (robust for the coarse
        # terminal quads, whose far corners can be several mm away)
        ok = [fi for fi in ownf
              if min((g.get(v, 1e18) for v in me.polygons[fi].vertices), default=1e18) <= rc * 1e-3]
        if near_face not in ok:
            ok.append(near_face)
        cs = set(ok); comp = set(); stk = [near_face]
        while stk:
            f = stk.pop()
            if f in comp or f not in cs:
                continue
            comp.add(f)
            for q in FADJ[f]:
                if q in cs and q not in comp:
                    stk.append(q)
        cv = {v for fi in comp for v in me.polygons[fi].vertices}
        # in-patch 1-median
        cadj = {}
        for e in me.edges:
            a, b = e.vertices[0], e.vertices[1]
            if a in cv and b in cv:
                w = (V[a] - V[b]).length
                cadj.setdefault(a, []).append((b, w)); cadj.setdefault(b, []).append((a, w))
        best = None
        for s0 in cv:
            dd = {s0: 0.0}; pq = [(0.0, s0)]
            while pq:
                du, u = heapq.heappop(pq)
                if du > dd.get(u, 1e18) + 1e-15:
                    continue
                for w, l in cadj.get(u, ()):
                    if du + l < dd.get(w, 1e18) - 1e-16:
                        dd[w] = du + l; heapq.heappush(pq, (du + l, w))
            tot = sum(dd.get(v, 1e9) for v in cv)
            if best is None or tot < best[0]:
                best = (tot, s0)
        rows.append({"R_mm": rc, "n_faces": len(comp), "n_verts": len(cv),
                     "median_vertex": best[1],
                     "median_to_star_mm": round((V[best[1]] - V[star]).length * MM, 3)})
    # landmark distances
    LM = {"R1_TIP": Vector(jf["%s_TIP_R" % D]["head"])}
    if D == "THUMB":
        LM["R2_TIP"] = Vector((1.456466794, 0.018134484, 0.48759535))
    lmd = {}
    for k, q in LM.items():
        bi = min(range(NV), key=lambda i: (V[i] - q).length)
        lmd[k] = {"nearest_vertex": bi, "geodesic_from_star_mm": round(g.get(bi, -1) * MM, 3),
                  "euclid_from_star_mm": round((V[bi] - V[star]).length * MM, 3),
                  "euclid_point_to_star_mm": round((q - V[star]).length * MM, 3)}
    R[D] = {"distal_most_vertex": star,
            "distal_most_vertex_world": [round(float(x), 9) for x in V[star]],
            "sweep": rows, "landmarks": lmd}
json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[SWEEP]", OUT)
