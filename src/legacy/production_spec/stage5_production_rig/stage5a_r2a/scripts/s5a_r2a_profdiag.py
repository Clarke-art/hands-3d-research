# STAGE5A_R2A -- 1 mm radial profile (READ-ONLY)
import bpy, sys, os, json, math
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
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}
RENV = {"THUMB": 11.14, "INDEX": 7.64, "MIDDLE": 7.80, "RING": 7.15, "LITTLE": 6.75}


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
DV = {D: sorted({v for p in me.polygons if FO[p.index] == D for v in p.vertices})
      for D in CHAIN}


def pca_axis(pts):
    n = len(pts); c = sum(pts, Vector()) / n
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


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-18)))
    return (p - (a + ab * t)).length


def medial_fit(pts, P0, u):
    u = u.normalized()
    for _ in range(5):
        ss = [(p - P0).dot(u) for p in pts]
        s_lo, s_hi = min(ss), max(ss)
        cents = []
        for k in range(16):
            lo = s_lo + (s_hi - s_lo) * k / 16; hi = s_lo + (s_hi - s_lo) * (k + 1) / 16
            sel = [p for p, q in zip(pts, ss) if lo <= q <= hi]
            if len(sel) >= 6:
                cents.append(sum(sel, Vector()) / len(sel))
        if len(cents) < 4:
            break
        c, ax = pca_axis(cents)
        if ax.dot(u) < 0:
            ax = -ax
        u = ax
    return u.normalized()


R = {}
for D in ["THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"]:
    dseg = "IP" if D == "THUMB" else "DIP"
    P = Vector(jf["%s_%s_R" % (D, dseg)]["head"]); T = Vector(jf["%s_TIP_R" % D]["head"])
    u0 = (T - P).normalized(); Rr = RENV[D] * 1e-3
    seed = [V[i] for i in DV[D] if seg_dist(V[i], P, T) <= Rr and (V[i] - P).dot(u0) > -0.003]
    ax = medial_fit(seed, P, u0)
    s_of = lambda p: (Vector(p) - P).dot(ax)
    pts = [V[i] for i in DV[D] if ((V[i] - P) - ax * ((V[i] - P).dot(ax))).length <= 1.3 * Rr]
    smax = max(s_of(p) for p in pts)
    prof = []
    off = 0.0
    while off <= 34.0:
        lo = smax - (off + 0.5) * 1e-3
        hi = smax - (off - 0.5) * 1e-3
        sel = [p for p in pts if lo <= s_of(p) <= hi]
        if sel:
            rs = sorted((((p - P) - ax * ((p - P).dot(ax))).length) for p in sel)
            prof.append({"s_mm": round((smax - off) * 1000, 3), "n": len(sel),
                         "r95": round(rs[int(0.95 * (len(rs) - 1))] * 1000, 3),
                         "rmax": round(rs[-1] * 1000, 3), "rmin": round(rs[0] * 1000, 3)})
        off += 1.0
    R[D] = {"axis": [round(float(x), 9) for x in ax],
            "axis_vs_bone_deg": round(math.degrees(math.acos(max(-1, min(1, ax.dot(u0))))), 3),
            "n_pts": len(pts), "prof": prof}
json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[PROF]", OUT)
