# STAGE5A_R2A -- terminal-ring topology diagnostic (READ-ONLY)
import bpy, sys, os, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
def pca_axis(pts):
    n = len(pts); c = sum(pts, Vector()) / n
    cov = [[0.0]*3 for _ in range(3)]
    for q in pts:
        d = q - c
        for a in range(3):
            for b in range(3):
                cov[a][b] += d[a]*d[b]
    v = Vector((0.0, 0.0, 1.0))
    for _ in range(300):
        nv = Vector((sum(cov[a][b]*v[b] for b in range(3)) for a in range(3)))
        if nv.length < 1e-20: break
        v = nv.normalized()
    return c, v


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
    return (p - (a + ab * t)).length


def medial_axis_fit(pts, P0, u):
    u = u.normalized(); cents = []
    for _ in range(5):
        ss = [(p - P0).dot(u) for p in pts]
        s_lo, s_hi = min(ss), max(ss); cents = []
        NS = 16
        for k in range(NS):
            lo = s_lo + (s_hi - s_lo) * k / NS; hi = s_lo + (s_hi - s_lo) * (k + 1) / NS
            sel = [p for p, q in zip(pts, ss) if lo <= q <= hi]
            if len(sel) >= 6:
                cents.append(sum(sel, Vector()) / len(sel))
        if len(cents) < 4: break
        c, ax = pca_axis(cents)
        if ax.dot(u) < 0: ax = -ax
        u = ax
    return u.normalized(), cents

ob = bpy.data.objects["Hand  - Realistic"]; me = ob.data
MW = ob.matrix_world
V = [(MW @ v.co).copy() for v in me.vertices]; NV = len(V)
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


AC = {D: chp(D) for D in CHAIN}
AC["wrist"] = [AO, Vector(jf["WRIST_R"]["tail"])]
FO = {}
for p in me.polygons:
    c = sum((V[v] for v in p.vertices), Vector()) / len(p.vertices)
    FO[p.index] = min(AC, key=lambda D: d_poly(c, AC[D]))
V2F = [[] for _ in range(NV)]
for p in me.polygons:
    for v in p.vertices:
        V2F[v].append(p.index)
VO = {}
for v in me.vertices:
    ds = {FO[fi] for fi in V2F[v.index]}
    VO[v.index] = ds.pop() if len(ds) == 1 else "MIXED"

EDGES = {tuple(sorted((e.vertices[0], e.vertices[1]))): (V[e.vertices[0]] - V[e.vertices[1]]).normalized()
         for e in me.edges}

R = {}
for D in ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]:
    dseg = "IP" if D == "THUMB" else "DIP"
    P = Vector(jf["%s_%s_R" % (D, dseg)]["head"])
    T = Vector(jf["%s_TIP_R" % D]["head"])
    u0 = (T - P).normalized()
    own_f = set(fi for fi in FO if FO[fi] == D)
    own_v = set(v for fi in own_f for v in me.polygons[fi].vertices)
    R_env = {"thumb":11.14,"index":7.64,"middle":7.80,"ring":7.15,"little":6.75}[D.lower()]
    seed = [V[i] for i in own_v if seg_dist(V[i], P, T) <= R_env*1e-3 and (V[i]-P).dot(u0) > -0.003]
    u0, _c = medial_axis_fit(seed, P, u0)
    # circumferential edges fully inside the digit
    circ = [k for k, dr in EDGES.items()
            if k[0] in own_v and k[1] in own_v and abs(dr.dot(u0)) < 0.45]
    # graph
    g = {}
    for a, b in circ:
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
        deg_ok = all(len(g[u]) == 2 for u in comp)
        if len(comp) >= 6 and deg_ok:
            ax = sorted(((V[u] - P).dot(u0) * 1000, u) for u in comp)
            rings.append({"n_verts": len(comp), "axial_min_mm": round(ax[0][0], 3),
                          "axial_max_mm": round(ax[-1][0], 3),
                          "axial_mean_mm": round(sum(a for a, _ in ax) / len(ax), 3),
                          "verts": [u for _a, u in ax]})
    rings.sort(key=lambda r: -r["axial_mean_mm"])
    R[D] = {"u0": [round(float(x), 9) for x in u0], "n_circ_edges": len(circ),
            "n_own_faces": len(own_f), "n_own_verts": len(own_v),
            "n_rings": len(rings), "rings": rings[:14]}

json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[RINGDIAG] written", OUT)
