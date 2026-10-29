# STAGE5A_R2A -- pick the canonical cap landmark subject to the interior constraint
import bpy, sys, os, json, math, heapq
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
AO = Vector(oa["WRIST_ORIGIN"])
ob = bpy.data.objects["Hand  - Realistic"]; me = ob.data
MW = ob.matrix_world; MINV = MW.inverted(); M3 = MW.to_3x3()
V = [(MW @ v.co).copy() for v in me.vertices]; NV = len(V); NP = len(me.polygons)
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
FC = [sum((V[v] for v in p.vertices), Vector()) / len(p.vertices) for p in me.polygons]
FO = {}
for p in me.polygons:
    FO[p.index] = min(AC, key=lambda D: d_poly(FC[p.index], AC[D]))
OF = {D: [p.index for p in me.polygons if FO[p.index] == D] for D in CHAIN}
DV = {D: sorted({v for p in me.polygons if FO[p.index] == D for v in p.vertices}) for D in CHAIN}
EADJ = {}
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    w = (V[a] - V[b]).length
    EADJ.setdefault(a, []).append((b, w)); EADJ.setdefault(b, []).append((a, w))
FADJ = [[] for _ in range(NP)]
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


def frac(a, b):
    n_in = 0; n_tot = 0
    for k in range(1, 21):
        t = 0.05 + (0.80 * k / 20.0)
        q = a + (b - a) * t
        p2, t2 = parity(q)
        n_tot += 1
        if p2 > t2 / 2:
            n_in += 1
    return n_in, n_tot


R = {}
# --- reference: interior fraction of the four accepted DIP->TIP segments
for D in ["INDEX", "MIDDLE", "RING", "LITTLE"]:
    a = Vector(jf["%s_DIP_R" % D]["head"]); b = Vector(jf["%s_TIP_R" % D]["head"])
    ni, nt = frac(a, b)
    R[D] = {"DIP_to_TIP_interior": "%d/%d" % (ni, nt), "fraction": round(ni / nt, 4),
            "length_mm": round((b - a).length * MM, 4)}

# --- thumb cap
D = "THUMB"
P = Vector(jf["THUMB_IP_R"]["head"]); T = Vector(jf["THUMB_TIP_R"]["head"])
u0 = (T - P).normalized()
cand = [i for i in DV[D] if (V[i] - P).dot(u0) > 0]
star = max(cand, key=lambda i: (V[i] - P).length)
g = dij(star)
ownf = set(OF[D])
ok = [fi for fi in ownf if min((g.get(v, 1e18) for v in me.polygons[fi].vertices), default=1e18) <= 9e-3]
nf = min(ownf, key=lambda fi: (FC[fi] - V[star]).length)
if nf not in ok:
    ok.append(nf)
cs = set(ok); cp = set(); stk = [nf]
while stk:
    f = stk.pop()
    if f in cp or f not in cs:
        continue
    cp.add(f)
    for q in FADJ[f]:
        if q in cs and q not in cp:
            stk.append(q)
cp = sorted(cp)
area = sum(me.polygons[fi].area for fi in cp)
capc = sum((FC[fi] * me.polygons[fi].area for fi in cp), Vector()) / max(1e-18, area)
sok, loc, nor, fidx = ob.closest_point_on_mesh(MINV @ capc)
REP = MW @ loc

# cap surface samples sorted by distance from IP
samples = []
for fi in cp:
    samples.append(("f%d" % fi, FC[fi]))
for i in sorted({v for fi in cp for v in me.polygons[fi].vertices}):
    samples.append(("v%d" % i, V[i]))
samples.append(("REP", Vector(REP)))
samples.sort(key=lambda s: -(s[1] - P).length)
rows = []
for nm, p in samples:
    ni, nt = frac(P, p)
    rows.append({"name": nm, "dist_from_IP_mm": round((p - P).length * MM, 4),
                 "interior": "%d/%d" % (ni, nt), "fraction": round(ni / nt, 4),
                 "p": [round(float(x), 9) for x in p],
                 "geodesic_from_star_mm": round(min((g.get(i, 1e18) for i in range(NV)
                                                     if (V[i] - p).length < 0.0025), default=-1) * MM, 4)})
R["THUMB"] = {"cap_faces": cp, "cap_centroid": [round(float(x), 9) for x in capc],
              "REP": [round(float(x), 9) for x in Vector(REP)],
              "distal_most_vertex": star,
              "distal_most_vertex_world": [round(float(x), 9) for x in V[star]],
              "samples_by_distance": rows}
json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[PICK]", OUT)
