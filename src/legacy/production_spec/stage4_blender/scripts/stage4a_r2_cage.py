# STAGE4A_R2 -- THUMB CMC "LOCAL DEFORMATION CAGE" SURGERY.
#
# OPT-A (Human Review, R2) replaces the tubular-collar criterion for THUMB CMC with
# T-04_CMC: LOCAL MULTI-AXIS DEFORMATION SUPPORT TOPOLOGY.  The requirement is now a
# local quad cage around the CMC rotation centre -- concentric geodesic support rings,
# radial spokes, enough local density, smooth divergence toward the first metacarpal /
# thenar / first web -- NOT a closed loop with linking number 1 about the metacarpal.
#
# Construction (guaranteed all-quad by design):
#   1. geodesic field from the CMC surface vertex (Dijkstra on the edge graph)
#   2. the disk of faces whose every vertex lies within R of the CMC -> verified
#      topological disk with ONE simple boundary loop of N edges (N % 4 == 0)
#   3. delete the disk interior, KEEP the boundary loop untouched, so the transition into
#      metacarpal / thenar / first web and all surrounding geometry is unchanged
#   4. rebuild the interior as
#         K concentric rings (N verts each, sampled along the geodesic spokes)
#         + N radial spokes            -> (K+1) x N quads of pure band topology (0 poles)
#         + an all-quad grid core      -> P x Q quads, P and Q both even
#      Every new vertex sits ON the original surface (spoke interpolation) or is
#      projected back onto it with a BVH tree, so thenar volume / first web / palm arch
#      are preserved to within the local chord error.
#
# Pole budget: a count-preserving band introduces no poles at all, and an all-quad grid
# cap of a 2(P+Q) loop has exactly four valence-3 corners.  P and Q even => the centre of
# the grid is a REGULAR valence-4 vertex, so no pole is created at the CMC centre.
#
# usage: blender -b <base.blend> --python stage4a_r2_cage.py -- <R_mm> <out.blend> <out.json>
import bpy, bmesh, sys, os, json, math, heapq, hashlib, datetime
from mathutils import Vector, Matrix, bvhtree

argv = sys.argv[sys.argv.index("--") + 1:]
R_MM, OUT_BLEND, OUT_JSON = float(argv[0]), argv[1], argv[2]
TARGET = "Hand  - Realistic"
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
THUMB_TIP_SEED = Vector((1.4977, 0.0358, 0.2421))
THUMB_ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
RING_SCALES = [0.78, 0.56, 0.34]
SMOOTH_PASSES, SMOOTH_FACTOR = 4, 0.35
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s)


def bail(tag, **kw):
    d = {"fatal": tag, "log": LOG}
    d.update(kw)
    json.dump(d, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("FATAL: %s -- no surgery saved" % tag)
    sys.exit(0)


ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
mi = mw.inverted()
me = ob.data
CO = [mw @ v.co for v in me.vertices]
N = len(CO)
LOC = mw.translation
POLY = [tuple(p.vertices) for p in me.polygons]


def canon(p):
    return (M_NORM @ p) + (LOC - (M_NORM @ LOC))


def nearest(p):
    best, bi = 1e18, 0
    for i, q in enumerate(CO):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i
    return bi


TIP_V = nearest(canon(THUMB_TIP_SEED))
ROOT_V = nearest(canon(THUMB_ROOT_SEED))
CMC = CO[ROOT_V]
log("CMC vertex %d  world=%s" % (ROOT_V, [round(float(x), 6) for x in CMC]))

adj = [[] for _ in range(N)]
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    L = (CO[a] - CO[b]).length
    adj[a].append((b, L)); adj[b].append((a, L))


def dij(src):
    d = [float("inf")] * N
    pr = [-1] * N
    d[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v] - 1e-16:
                d[v] = nd; pr[v] = u; heapq.heappush(pq, (nd, v))
    return d, pr


gd, pred = dij(ROOT_V)
gdt = dij(TIP_V)[0]
L_THUMB = gdt[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gdt[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))

# ================================================================ 1. the disk
R = R_MM / 1000.0
S = set(i for i in range(N) if gd[i] <= R)
disk_faces = [pi for pi, vs in enumerate(POLY) if all(v in S for v in vs)]
efc = {}
for pi in disk_faces:
    vs = POLY[pi]
    for k in range(len(vs)):
        key = tuple(sorted((vs[k], vs[(k + 1) % len(vs)])))
        efc[key] = efc.get(key, 0) + 1
bnd_edges = [k for k, c in efc.items() if c == 1]
cn = {}
for a, b in bnd_edges:
    cn.setdefault(a, []).append(b); cn.setdefault(b, []).append(a)
comps, seen = [], set()
for s in cn:
    if s in seen:
        continue
    comp, st, seen = [], [s], seen | {s}
    while st:
        u = st.pop(); comp.append(u)
        for v in cn[u]:
            if v not in seen:
                seen.add(v); st.append(v)
    comps.append(comp)
vs_in = set()
for pi in disk_faces:
    vs_in.update(POLY[pi])
euler = len(vs_in) - len(efc) + len(disk_faces)
Nb = len(bnd_edges)
disk_ok = (euler == 1 and len(comps) == 1 and Nb == len(cn)
           and all(len(v) == 2 for v in cn.values()))
log("disk R=%.1fmm  faces=%d verts=%d  boundary loop %d edges / %d verts  euler=%d  OK=%s"
    % (R_MM, len(disk_faces), len(vs_in), Nb, len(cn), euler, disk_ok))
if not disk_ok:
    bail("region is not a clean disk", R_mm=R_MM, faces=len(disk_faces), euler=euler,
         components=len(comps), boundary_edges=Nb, boundary_verts=len(cn))
if Nb % 4 != 0:
    bail("boundary loop length %d is not a multiple of 4" % Nb, N=Nb)

start = min(cn)
order, prev, cur = [start], None, start
while True:
    o = [x for x in cn[cur] if x != prev]
    if not o:
        break
    prev, cur = cur, o[0]
    if cur == start:
        break
    order.append(cur)
    if len(order) > Nb:
        break
if len(order) != Nb:
    bail("boundary loop traversal failed", got=len(order), want=Nb)
BVERT = order
eucl = [(CO[i] - CMC).length for i in BVERT]
log("boundary loop: geodesic radius %.2f..%.2f mm | euclidean radius %.2f..%.2f mm (mean %.2f)"
    % (min(gd[i] for i in BVERT) * 1000, max(gd[i] for i in BVERT) * 1000,
       min(eucl) * 1000, max(eucl) * 1000, sum(eucl) / len(eucl) * 1000))
local_edges = [(CO[a] - CO[b]).length for (a, b) in bnd_edges]
log("local mesh edge length on the boundary loop: mean %.2f mm" % (1000 * sum(local_edges) / len(local_edges)))
# d(v) = number of disk faces incident to a boundary vertex.  After the cage each boundary
# vertex keeps its outside edges and gains exactly one spoke, so its valence changes by
# 2 - d(v).  d == 2 therefore leaves the valence untouched; d == 1 / d == 3 create a pole.
dcount = {}
for pi in disk_faces:
    for v in set(POLY[pi]):
        if v in cn:
            dcount[v] = dcount.get(v, 0) + 1
dhist = {}
for b in BVERT:
    dhist[dcount.get(b, 0)] = dhist.get(dcount.get(b, 0), 0) + 1
log("boundary d-histogram (disk faces per boundary vertex): %s  -> valence-neutral(d=2)=%d"
    % (dict(sorted(dhist.items())), dhist.get(2, 0)))

# ================================================================ 2. geodesic spokes
def spoke(b):
    p, chain = b, [b]
    while p != ROOT_V and pred[p] != -1:
        p = pred[p]
        chain.append(p)
    chain.reverse()
    cum = [0.0]
    for k in range(1, len(chain)):
        cum.append(cum[-1] + (CO[chain[k]] - CO[chain[k - 1]]).length)
    return chain, cum


SPOKES = [spoke(b) for b in BVERT]


def along(chain, cum, target):
    if target <= 0:
        return CO[chain[0]].copy()
    for k in range(1, len(chain)):
        if cum[k] >= target:
            t = (target - cum[k - 1]) / max(1e-12, cum[k] - cum[k - 1])
            return CO[chain[k - 1]] + (CO[chain[k]] - CO[chain[k - 1]]) * t
    return CO[chain[-1]].copy()


# ================================================================ 3. BVH of the ORIGINAL surface
bvh = bvhtree.BVHTree.FromPolygons(CO, POLY, all_triangles=False, epsilon=0.0)


def project(p, maxd=0.08):
    r = bvh.find_nearest(p, maxd)
    if r is None or r[0] is None:
        return p, None
    return r[0], r[1]


def deviation(p):
    r = bvh.find_nearest(p, 0.08)
    return 0.0 if r is None or r[0] is None else (p - r[0]).length


# ================================================================ 4. remove the disk interior
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
ring0 = [bm.verts[i] for i in BVERT]
disk_bm_faces = [bm.faces[pi] for pi in disk_faces]
for f in disk_bm_faces:
    bm.faces.remove(f)
bm.edges.ensure_lookup_table(); bm.verts.ensure_lookup_table()
wire = [e for e in bm.edges if len(e.link_faces) == 0]
for e in wire:
    bm.edges.remove(e)
orphan = [v for v in bm.verts if len(v.link_edges) == 0]
for v in orphan:
    bm.verts.remove(v)
log("removed %d disk faces / %d wire edges / %d orphan verts"
    % (len(disk_bm_faces), len(wire), len(orphan)))

# ================================================================ 5. cage vertices
bm.verts.ensure_lookup_table()
K = len(RING_SCALES)
ring_verts = [ring0]
ring_world = [[CO[i].copy() for i in BVERT]]
new_verts = []
# Ring k = the boundary loop shrunk radially toward the CMC surface point by RING_SCALES[k],
# then projected back onto the ORIGINAL surface.  A "fraction along the geodesic spoke"
# placement was tried first and REJECTED: on this coarse mesh the Dijkstra spokes to
# adjacent boundary vertices cross each other, so the ring points came back out of cyclic
# order and the rings folded into zigzags (median turn 180 deg on the innermost ring).
# A radial shrink keeps an exact 1:1 cyclic correspondence with the boundary loop, so every
# ring is a smooth concentric closed curve and every band is a clean quad ring.
for k, sk in enumerate(RING_SCALES):
    row, wp = [], []
    for j in range(Nb):
        p, _n = project(CMC + (ring_world[0][j] - CMC) * sk)
        v = bm.verts.new(mi @ p)
        row.append(v); wp.append(p); new_verts.append(v)
    ring_verts.append(row); ring_world.append(wp)
    rad = [(p - CMC).length for p in wp]
    log("  ring %d  scale %.2f  radius %.2f..%.2f mm (mean %.2f)"
        % (k + 1, sk, min(rad) * 1000, max(rad) * 1000, sum(rad) / len(rad) * 1000))

P = 2 * (Nb // 8)
Q = Nb // 2 - P
if P < 2 or Q < 2 or P % 2 or Q % 2:
    bail("no even P,Q for the core grid", N=Nb, P=P, Q=Q)
log("  core grid %d x %d quads  (loop %d = 2*(%d+%d))" % (P, Q, Nb, P, Q))

INW = ring_world[-1]


ROT = 0


def ring_pt(t):
    t = (t + ROT) % Nb
    i0 = int(math.floor(t)); i1 = (i0 + 1) % Nb
    s = t - i0
    return INW[i0] + (INW[i1] - INW[i0]) * s


# ---- choose the rotation of the core cap: put its four valence-3 corners as far as
# ---- possible from the CMC flexion midline and from the opposition strain path.
RAW_JSON = os.path.join(os.path.dirname(os.path.abspath(OUT_JSON)), "RAW_ENGINEERING.json")
try:
    _raw = json.load(open(RAW_JSON, encoding="utf-8"))["frame_after"]
    DORSAL = Vector(_raw["DORSAL_axis"]).normalized()
    RADIAL = Vector(_raw["RADIAL_axis"]).normalized()
except Exception:
    DORSAL, RADIAL = Vector((0.0, 1.0, 0.0)), Vector((1.0, 0.0, 0.0))
PALMAR = -DORSAL


def corner_penalty(s):
    pen = 0
    for c in (0, P, P + Q, 2 * P + Q):
        p = INW[(c + s) % Nb]
        r = bvh.find_nearest(p, 0.08)
        n = r[1] if (r is not None and r[1] is not None) else None
        if n is None:
            continue
        n = n.normalized()
        a_dor = math.degrees(math.acos(max(-1.0, min(1.0, n.dot(DORSAL)))))
        a_pal = math.degrees(math.acos(max(-1.0, min(1.0, n.dot(PALMAR)))))
        a_rad = math.degrees(math.acos(max(-1.0, min(1.0, n.dot(RADIAL)))))
        if min(a_dor, a_pal) <= 45.0:
            pen += 4                       # on the flexion midline (pinch crease)
        if a_pal <= 62.0 and a_rad <= 75.0:
            pen += 2                       # on the opposition load path
    return pen


ROT = min(range(Nb), key=lambda s: (corner_penalty(s), s))
log("core-cap rotation: offset %d (strain-path penalty %d; worst alternative %d)"
    % (ROT, corner_penalty(ROT), max(corner_penalty(s) for s in range(Nb))))

C00, C10 = INW[ROT % Nb], INW[(P + ROT) % Nb]
C11, C01 = INW[(P + Q + ROT) % Nb], INW[(2 * P + Q + ROT) % Nb]


def gv(t):
    return INN[(t + ROT) % Nb]


def coons(u, v):
    L = ring_pt(u * P)
    Rr = ring_pt(2 * P + Q - u * P)
    B = ring_pt(Nb - v * Q)
    T = ring_pt(P + v * Q)
    bil = ((1 - u) * (1 - v) * C00 + u * (1 - v) * C10 + u * v * C11 + (1 - u) * v * C01)
    return (1 - v) * L + v * Rr + (1 - u) * B + u * T - bil


INN = ring_verts[-1]
grid = [[None] * (Q + 1) for _ in range(P + 1)]
for i in range(P + 1):
    grid[i][0] = gv(i)
for j in range(Q + 1):
    grid[P][j] = gv(P + j)
for i in range(P + 1):
    grid[i][Q] = gv(2 * P + Q - i)
for j in range(Q + 1):
    grid[0][j] = gv(Nb - j)
for i in range(P + 1):
    for j in range(Q + 1):
        if grid[i][j] is not None:
            continue
        p, _n = project(coons(i / P, j / Q))
        v = bm.verts.new(mi @ p)
        grid[i][j] = v
        new_verts.append(v)

# ================================================================ 6. cage faces
cage_faces = []
bad = 0
for k in range(1, K + 1):
    outer, inner = ring_verts[k - 1], ring_verts[k]
    for j in range(Nb):
        try:
            cage_faces.append(bm.faces.new((outer[j], outer[(j + 1) % Nb],
                                            inner[(j + 1) % Nb], inner[j])))
        except ValueError:
            bad += 1
for i in range(P):
    for j in range(Q):
        try:
            cage_faces.append(bm.faces.new((grid[i][j], grid[i + 1][j],
                                            grid[i + 1][j + 1], grid[i][j + 1])))
        except ValueError:
            bad += 1
log("cage faces: %d created (%d concentric bands x %d spokes + %d core), %d collisions"
    % (len(cage_faces), K, Nb, P * Q, bad))

cage_set = set(cage_faces)

# ================================================================ 7. relax + reproject
bm.normal_update()
live = [v for v in new_verts if v.is_valid]
for _p in range(SMOOTH_PASSES):
    bmesh.ops.smooth_vert(bm, verts=live, factor=SMOOTH_FACTOR,
                          use_axis_x=True, use_axis_y=True, use_axis_z=True)
    for v in live:
        p, _n = project(mw @ v.co)
        if p is not None:
            v.co = mi @ p
log("relax: %d passes x %.2f on %d new verts, re-projected onto the original surface"
    % (SMOOTH_PASSES, SMOOTH_FACTOR, len(live)))

# ================================================================ 7b. pole treatment
# T-04_CMC / CON-3 requirement F: no pole may sit on the CMC flexion strain path (the
# dorsal or palmar crest, where flexion pinches) or on the opposition strain path (the
# palmar-radial thenar aspect).  The remedy is the SAME one the Stage-4A pipeline already
# uses for the finger joints: slide the pole CIRCUMFERENTIALLY, i.e. tangentially, away
# from the crest -- a small move on the thenar surface that leaves the silhouette and the
# volume untouched.  Displacement is capped and every moved vertex is re-projected onto
# the original surface.
MID_TGT, OPP_TGT, POLE_MARGIN = 45.0, 62.0, 8.0
POLE_STEP_M, POLE_TOTAL_CAP_M = 0.0009, 0.0040
POLE_MOVES = []
_pole_total = {}


def _ang(n, ax):
    return math.degrees(math.acos(max(-1.0, min(1.0, n.normalized().dot(ax)))))


for _pp in range(1, 6):
    bm.normal_update()
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    movers = []
    for v in bm.verts:
        if len(v.link_edges) == 4:
            continue
        p = mw @ v.co
        # SCOPE GUARD: the surgery is authorised for the CMC neighbourhood only.  A pure
        # axial test is not enough -- the metacarpal axis points across the hand, so a
        # vertex 100 mm away can still have a small axial projection.  Require BOTH.
        if (p - CMC).length > R * 1.05 or abs((p - ANCHOR).dot(AXIS)) > 0.025:
            continue
        ring = [e.other_vert(v) for e in v.link_edges]
        if not ring:
            continue
        c = sum((mw @ w.co for w in ring), Vector()) / len(ring)
        n = p - c
        if n.length < 1e-9:
            continue
        rlen = n.length
        n.normalize()
        a_dor, a_pal, a_rad = _ang(n, DORSAL), _ang(n, PALMAR), _ang(n, RADIAL)
        if min(a_dor, a_pal) <= MID_TGT:
            axis_dir = DORSAL if a_dor <= a_pal else PALMAR
            need = (MID_TGT + POLE_MARGIN) - min(a_dor, a_pal)
            why = "flexion_midline"
        elif a_pal <= OPP_TGT and a_rad <= 75.0:
            axis_dir, need, why = PALMAR, (OPP_TGT + POLE_MARGIN) - a_pal, "opposition_path"
        else:
            continue
        away = axis_dir - n * axis_dir.dot(n)
        if away.length < 1e-6:
            away = n.cross(axis_dir)
        if away.length < 1e-6:
            continue
        away.normalize()
        # The thenar is a LOW-CURVATURE surface, so the tangential distance needed to turn
        # the local normal by `need` degrees is far larger than rlen*need (that estimate
        # assumes a fingertip-sized curvature radius).  Use a fixed step and iterate, with
        # a hard cumulative cap so the cage is never dragged out of shape.
        room = POLE_TOTAL_CAP_M - _pole_total.get(v.index, 0.0)
        if room <= 1e-6:
            continue
        disp = min(max(rlen * math.radians(need), POLE_STEP_M), room)
        movers.append((v, away, disp, why, a_dor, a_pal, a_rad))
    if not movers:
        break
    nbr = set()
    for v, _a, _d, _w, _x, _y, _z in movers:
        for e in v.link_edges:
            nbr.add(e.other_vert(v))
    if nbr:
        bmesh.ops.smooth_vert(bm, verts=[x for x in nbr], factor=0.25,
                              use_axis_x=True, use_axis_y=True, use_axis_z=True)
        bm.normal_update()
    m3 = mi.to_3x3()
    for v, away, disp, why, a_dor, a_pal, a_rad in movers:
        v.co = v.co + m3 @ (-away * disp)
        _pole_total[v.index] = _pole_total.get(v.index, 0.0) + disp
    for v in [m[0] for m in movers] + list(nbr):
        q, _nn = project(mw @ v.co)
        if q is not None:
            v.co = mi @ q
    for v, away, disp, why, a_dor, a_pal, a_rad in movers:
        POLE_MOVES.append({"pass": _pp, "why": why, "displacement_mm": round(disp * 1000, 3),
                           "angle_dorsal_before": round(a_dor, 1),
                           "angle_palmar_before": round(a_pal, 1),
                           "angle_radial_before": round(a_rad, 1)})
    log("pole pass %d: %d pole(s) slid off the CMC strain paths (%s)"
        % (_pp, len(movers), ", ".join(sorted(set(m[3] for m in movers)))))
log("pole treatment: %d moves over %d verts, max cumulative displacement %.3f mm "
    "(step %.1f mm, cap %.1f mm)"
    % (len(POLE_MOVES), len(_pole_total),
       max([v for v in _pole_total.values()] or [0.0]) * 1000,
       POLE_STEP_M * 1000, POLE_TOTAL_CAP_M * 1000))

# ================================================================ 8. orientation
bm.normal_update()
flips = 0
for f in cage_faces:
    if not f.is_valid:
        continue
    c = sum((mw @ v.co for v in f.verts), Vector()) / len(f.verts)
    r = bvh.find_nearest(c, 0.08)
    if r is None or r[1] is None:
        continue
    if f.normal.dot(r[1]) < 0:
        f.normal_flip()
        flips += 1
log("orientation: %d of %d faces flipped to match the original surface" % (flips, len(cage_faces)))

# consistency: every pair of edge-adjacent cage faces must agree on orientation
bm.normal_update()
inconsistent = 0
for f in cage_faces:
    if not f.is_valid:
        continue
    for e in f.edges:
        for g in e.link_faces:
            if g is f or g not in cage_set:
                continue
            if f.normal.dot(g.normal) <= 0:
                inconsistent += 1
log("orientation consistency: %d disagreeing adjacent face pairs inside the cage"
    % inconsistent)

bm.normal_update()
cage_new_world = [mw @ v.co for v in new_verts]
bm.to_mesh(me)
me.update()
bm.free()

# ================================================================ 9. validation
quads = sum(1 for p in me.polygons if len(p.vertices) == 4)
tris = sum(1 for p in me.polygons if len(p.vertices) == 3)
ngons = sum(1 for p in me.polygons if len(p.vertices) > 4)
bm2 = bmesh.new(); bm2.from_mesh(me)
bm2.edges.ensure_lookup_table(); bm2.verts.ensure_lookup_table()
bnd = [e.index for e in bm2.edges if len(e.link_faces) == 1]
over = [e.index for e in bm2.edges if len(e.link_faces) > 2]
loosev = [v.index for v in bm2.verts if len(v.link_edges) == 0]
loosee = [e.index for e in bm2.edges if len(e.link_faces) == 0]
val = {v.index: len(v.link_edges) for v in bm2.verts}
poles = {i: k for i, k in val.items() if k != 4}
bm2.free()
log("AFTER  V=%d E=%d F=%d  quads=%d tris=%d ngons=%d"
    % (len(me.vertices), len(me.edges), len(me.polygons), quads, tris, ngons))
log("VALIDATE  boundary_edges=%d  >2face=%d  loose_verts=%d  loose_edges=%d  poles=%d"
    % (len(bnd), len(over), len(loosev), len(loosee), len(poles)))
clean = (tris == 0 and ngons == 0 and not bnd and not over and not loosev and not loosee)

CO2 = [mw @ v.co for v in me.vertices]
devs = sorted(deviation(p) for p in CO2)
devmax, devp95 = devs[-1], devs[int(0.95 * (len(devs) - 1))]
log("shape deviation vs original surface: max %.4f mm  p95 %.4f mm  mean %.4f mm"
    % (devmax * 1000, devp95 * 1000, sum(devs) / len(devs) * 1000))

# cage locality: the new cage vertices only (plus the untouched boundary loop they hang on)
cage_new = cage_new_world + [CO[i] for i in BVERT]
cage_r = [(p - CMC).length for p in cage_new]
axc = [(p - ANCHOR).dot(AXIS) for p in cage_new]
log("cage locality: %d cage verts, euclidean radius %.2f..%.2f mm from the CMC, "
    "axial span along the metacarpal %.2f mm"
    % (len(cage_r), min(cage_r) * 1000, max(cage_r) * 1000, (max(axc) - min(axc)) * 1000))
NONLOCAL = [p for p in cage_new if (p - CMC).length > R * 1.05]
log("cage verts outside the %.1f mm sphere: %d" % (R_MM, len(NONLOCAL)))

if not clean:
    bail("mesh not clean", tris=tris, ngons=ngons, boundary=len(bnd),
         over=len(over), loose_verts=len(loosev), loose_edges=len(loosee))

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
SHA = hashlib.sha256(open(OUT_BLEND, "rb").read()).hexdigest()
log("SAVED %s (%d bytes, sha256 %s)" % (OUT_BLEND, os.path.getsize(OUT_BLEND), SHA))

out = {
    "stage": "STAGE4A_R2_CMC_LOCAL_DEFORMATION_CAGE",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "runtime": {"blender": bpy.app.version_string, "executable": bpy.app.binary_path},
    "cmc_vertex": ROOT_V, "cmc_world": [float(x) for x in CMC],
    "first_metacarpal_axis": [float(x) for x in AXIS],
    "disk": {"R_mm": R_MM, "faces_before": len(disk_faces), "verts_before": len(vs_in),
             "boundary_loop_edges": Nb, "euler": euler, "is_disk": disk_ok,
             "boundary_geodesic_radius_mm": [round(min(gd[i] for i in BVERT) * 1000, 2),
                                             round(max(gd[i] for i in BVERT) * 1000, 2)],
             "boundary_euclidean_radius_mm": [round(min(eucl) * 1000, 2),
                                              round(max(eucl) * 1000, 2)]},
    "cage": {"concentric_rings_new": K, "concentric_rings_total": K + 1,
             "ring_scales": RING_SCALES, "spokes": Nb,
             "core_grid": [P, Q], "core_cap_rotation": ROT,
             "new_band_quads": K * Nb, "new_core_quads": P * Q,
             "ring_radii_mm": [{"ring": k + 1, "scale": RING_SCALES[k],
                                "radius_min_mm": round(min((p - CMC).length for p in ring_world[k + 1]) * 1000, 2),
                                "radius_max_mm": round(max((p - CMC).length for p in ring_world[k + 1]) * 1000, 2)}
                               for k in range(K)],
             "new_verts": len(new_verts)},
    "relax": {"passes": SMOOTH_PASSES, "factor": SMOOTH_FACTOR},
    "pole_treatment": {"midline_target_deg": MID_TGT, "opposition_target_deg": OPP_TGT,
                       "margin_deg": POLE_MARGIN, "step_mm": POLE_STEP_M * 1000,
                       "cumulative_cap_mm": POLE_TOTAL_CAP_M * 1000,
                       "verts_moved": len(_pole_total),
                       "max_cumulative_mm": round(max([v for v in _pole_total.values()]
                                                      or [0.0]) * 1000, 3),
                       "moves": POLE_MOVES},
    "topology": {"verts": len(me.vertices), "edges": len(me.edges), "faces": len(me.polygons),
                 "quads": quads, "tris": tris, "ngons": ngons,
                 "boundary_edges": len(bnd), "over_2face_edges": len(over),
                 "loose_verts": len(loosev), "loose_edges": len(loosee),
                 "orientation_inconsistent_pairs": inconsistent,
                 "pole_count": len(poles),
                 "valence_histogram": {str(k): sum(1 for v in val.values() if v == k)
                                       for k in sorted(set(val.values()))}},
    "locality": {"cage_verts": len(cage_r),
                 "euclidean_radius_mm": [round(min(cage_r) * 1000, 2),
                                         round(max(cage_r) * 1000, 2)],
                 "axial_span_mm": round((max(axc) - min(axc)) * 1000, 2),
                 "verts_outside_R_sphere": len(NONLOCAL)},
    "shape_deviation_mm": {"max": round(devmax * 1000, 4), "p95": round(devp95 * 1000, 4),
                           "mean": round(sum(devs) / len(devs) * 1000, 4)},
    "out_blend": OUT_BLEND, "out_sha256": SHA, "out_bytes": os.path.getsize(OUT_BLEND),
    "boundary_loop_world": [[round(float(x), 6) for x in CO[i]] for i in BVERT],
    "ring_world": [[[round(float(x), 6) for x in p] for p in rw] for rw in ring_world],
    "new_vertex_world": [[round(float(x), 6) for x in p] for p in cage_new_world],
    "log": LOG,
}
json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("WROTE %s" % OUT_JSON)
