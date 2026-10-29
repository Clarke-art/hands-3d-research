# STAGE4A_T01_FINAL_RECONCILIATION_R1 -- per-MCP local wireframe evidence (READ-ONLY).
#
# For each MCP: a close-up of the joint with
#   * every mesh edge inside the local radius drawn as a thin wire
#   * every edge loop COUNTED by the T-01 true-edge-loop audit drawn as a thick coloured tube
#   * the joint centre marked
#
# The blend is never saved.
# usage: blender -b <blend> --python stage4a_t01_render.py -- <outdir> <T01_FINAL_AUDIT.json>
import bpy, bmesh, sys, os, json, math, heapq
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, JSON_IN = argv[0], argv[1]
os.makedirs(OUTDIR, exist_ok=True)
TARGET = "Hand  - Realistic"
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TIP_SEEDS = {
    "little": Vector((1.3515, 0.0319, 0.1879)), "ring": Vector((1.3933, 0.0320, 0.1599)),
    "middle": Vector((1.4231, 0.0251, 0.1490)), "index": Vector((1.4586, 0.0239, 0.1643)),
    "thumb": Vector((1.4977, 0.0358, 0.2421)),
}
THUMB_ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
FOREARM_SEED = Vector((1.4048, 0.0113, 0.4316)); WRIST_SEED = Vector((1.4048, 0.0113, 0.3430))
FINGER_ORDER = ["little", "ring", "middle", "index"]

ob = bpy.data.objects[TARGET]
MW = ob.matrix_world
LOC0 = MW.translation
canon = lambda p: (M_NORM @ p) + (LOC0 - (M_NORM @ LOC0))
bm = bmesh.new(); bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
W = [(MW @ v.co).copy() for v in bm.verts]
NV = len(W)
ADJ = [[] for _ in range(NV)]
for e in bm.edges:
    a, b = e.verts[0].index, e.verts[1].index
    L = (W[a] - W[b]).length
    ADJ[a].append((b, L)); ADJ[b].append((a, L))
nearest = lambda p: min(range(NV), key=lambda i: (W[i] - p).length_squared)


def dij(src):
    d = [float("inf")] * NV; d[src] = 0.0; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15:
            continue
        for v, w in ADJ[u]:
            if du + w < d[v] - 1e-16:
                d[v] = du + w; heapq.heappush(pq, (d[v], v))
    return d


TIPV = {n: nearest(canon(s)) for n, s in TIP_SEEDS.items()}
G = {n: dij(TIPV[n]) for n in TIPV}
WRIST_V = nearest(canon(WRIST_SEED)); FOREARM = W[nearest(canon(FOREARM_SEED))]
lab = [None] * NV; dd = [float("inf")] * NV
srcs = [("wrist", WRIST_V)] + [(n, TIPV[n]) for n in TIPV]
for nm, s in srcs:
    dd[s] = 0.0; lab[s] = nm
pq = [(0.0, s) for _n, s in srcs]; heapq.heapify(pq)
while pq:
    du, u = heapq.heappop(pq)
    if du > dd[u] + 1e-15:
        continue
    for v, w in ADJ[u]:
        if du + w < dd[v] - 1e-16:
            dd[v] = du + w; lab[v] = lab[u]; heapq.heappush(pq, (dd[v], v))
DIGIT_V = {n: [] for n in TIPV}
for i, l in enumerate(lab):
    if l in DIGIT_V:
        DIGIT_V[l].append(i)
DD = (W[TIPV["middle"]] - FOREARM).normalized()
CLEFTS = [("index", "middle"), ("middle", "ring"), ("ring", "little"), ("index", "thumb")]
FC = {"index": ["index-middle"], "middle": ["index-middle", "middle-ring"],
      "ring": ["middle-ring", "ring-little"], "little": ["ring-little"]}
NOTCH = {}
for a, b in CLEFTS:
    rg = {u for u in range(NV) if lab[u] in (a, b)
          and any(lab[v] in (a, b) and lab[v] != lab[u] for v, _w in ADJ[u])}
    if rg:
        NOTCH["%s-%s" % (a, b)] = max(rg, key=lambda u: (W[u] - FOREARM).dot(DD))
FL = {}
for nm in FINGER_ORDER:
    vals = [G[nm][NOTCH[c]] for c in FC[nm] if c in NOTCH]
    if vals:
        FL[nm] = sum(vals) / len(vals)
FL["thumb"] = G["thumb"][nearest(canon(THUMB_ROOT_SEED))]


def finger_axis(nm):
    tip = W[TIPV[nm]]; L = FL[nm]; ids = DIGIT_V.get(nm, [])
    bd = [i for i in ids if 0.25 * L <= G[nm][i] <= 0.55 * L]
    c = (sum((W[i] for i in bd), Vector()) / len(bd)) if bd else tip
    ax = (tip - c).normalized()
    ref = W[NOTCH[FC[nm][0]]]
    return ax, tip + ax * ((ref - tip).dot(ax))


data = json.load(open(JSON_IN, encoding="utf-8"))


def make_obj(name, verts, faces, color):
    m = bpy.data.meshes.new(name)
    m.from_pydata([tuple(v) for v in verts], [], faces)
    m.update()
    o = bpy.data.objects.new(name, m)
    bpy.context.scene.collection.objects.link(o)
    o.color = color
    return o


def tube(points, radius, closed=True, sides=6):
    n = len(points)
    verts, faces = [], []
    ref = Vector((0.0, 0.0, 1.0))
    for i in range(n):
        t = (points[(i + 1) % n] - points[(i - 1) % n]) if closed else \
            (points[min(n - 1, i + 1)] - points[max(0, i - 1)])
        if t.length < 1e-12:
            t = Vector((0, 0, 1))
        t = t.normalized()
        r = ref if abs(ref.dot(t)) < 0.9 else Vector((1, 0, 0))
        n1 = (r - t * r.dot(t)).normalized(); n2 = t.cross(n1)
        for k in range(sides):
            a = 2 * math.pi * k / sides
            verts.append(points[i] + (n1 * math.cos(a) + n2 * math.sin(a)) * radius)
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        for k in range(sides):
            k2 = (k + 1) % sides
            faces.append((i * sides + k, i * sides + k2, j * sides + k2, j * sides + k))
    return verts, faces


scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'OBJECT'
scene.display.render_aa = '8'
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
w = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
scene.world = w; w.color = (1.0, 1.0, 1.0)
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cd.clip_start = 0.001
cam = bpy.data.objects.new("c", cd)
scene.collection.objects.link(cam); scene.camera = cam
ob.color = (0.90, 0.90, 0.92, 1.0)

DORS = Vector((0, 1, 0))
LOOP_COL = [(0.90, 0.10, 0.10, 1.0), (0.10, 0.55, 0.95, 1.0), (0.15, 0.70, 0.20, 1.0),
            (0.95, 0.55, 0.05, 1.0), (0.65, 0.15, 0.85, 1.0), (0.05, 0.75, 0.75, 1.0)]

for nm in ("index", "middle", "ring", "little"):
    jn = "%s_MCP" % nm.upper()
    r = data["T01_MCP"][jn]
    axis, anchor = finger_axis(nm)
    centre = anchor + axis * (r["joint_axial_center_mm"] / 1000.0)
    # ---- local wireframe
    wire = []
    for e in bm.edges:
        a, b = e.verts[0].index, e.verts[1].index
        mid = (W[a] + W[b]) / 2
        if (mid - centre).length <= 0.030:
            wire.append((W[a], W[b]))
    vv, ff = [], []
    for (p, q) in wire:
        a, b = tube([p, q], 0.00042, closed=False)
        base = len(vv)
        vv += a; ff += [tuple(i + base for i in x) for x in b]
    make_obj("wire_%s" % nm, vv, ff, (0.30, 0.32, 0.38, 1.0))
    # ---- counted loops
    for li, vs in enumerate(r["_verts"]):
        pts = [W[i] for i in vs]
        a, b = tube(pts, 0.0017, closed=True)
        make_obj("loop_%s_%d" % (nm, li), a, b, LOOP_COL[li % len(LOOP_COL)])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0022, location=tuple(centre))
    bpy.context.active_object.color = (1.0, 0.45, 0.0, 1.0)
    dp = (DORS - axis * DORS.dot(axis)).normalized()
    pos = centre + dp * 0.8
    cam.location = pos
    cam.rotation_euler = (centre - pos).to_track_quat('-Z', 'Y').to_euler()
    cd.ortho_scale = 0.075
    out = os.path.join(OUTDIR, "T01_%s.png" % jn)
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("RENDERED", os.path.basename(out), os.path.exists(out),
          "loops=%d" % r["ACTUAL_EDGE_LOOPS"], "wire_edges=%d" % len(wire))
print("DONE")
