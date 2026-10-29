# STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1 -- human-review evidence renders (local CMC views).
#
# Deliberately LOCAL: the hand is drawn as a pale surface (no dense full-hand wireframe).
# Overlays:
#   * the three baseline THUMB_CMC support loops (red / blue / green)
#   * the CMC rotation centre (orange sphere)
#   * the first metacarpal axis (black line)
#   * the +-12 mm engineering window (two magenta rings)
#   * the candidate CMC-concentric ring family (magenta / cyan / lime)
#
# usage: blender -b <blend> --python stage4a_r1_render.py -- <outdir> <raw.json> <audit.json>
import bpy, sys, json, os, math, heapq
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, RAW_JSON, AUDIT_JSON = argv[0], argv[1], argv[2]
os.makedirs(OUTDIR, exist_ok=True)

TIP_SEED = Vector((1.4977, 0.0358, 0.2421))
ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TARGET = "Hand  - Realistic"

ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
CO = [mw @ v.co for v in me.vertices]
N = len(CO)
loc = mw.translation


def canon(p):
    return (M_NORM @ p) + (loc - (M_NORM @ loc))


def nearest(p):
    best, bi = 1e18, 0
    for i, q in enumerate(CO):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i
    return best, bi


_, TIP_V = nearest(canon(TIP_SEED))
_, ROOT_V = nearest(canon(ROOT_SEED))
adj = [[] for _ in range(N)]
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    L = (CO[a] - CO[b]).length
    adj[a].append((b, L)); adj[b].append((a, L))


def dij(src):
    d = [float("inf")] * N; d[src] = 0.0; pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v] - 1e-16:
                d[v] = nd; heapq.heappush(pq, (nd, v))
    return d


gd_tip = dij(TIP_V)
L_THUMB = gd_tip[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gd_tip[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC = CO[ROOT_V]
gd = dij(ROOT_V)

audit = json.load(open(AUDIT_JSON, encoding="utf-8"))
raw = json.load(open(RAW_JSON, encoding="utf-8"))


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
        n1 = (r - t * r.dot(t)).normalized()
        n2 = t.cross(n1)
        for k in range(sides):
            a = 2 * math.pi * k / sides
            verts.append(points[i] + (n1 * math.cos(a) + n2 * math.sin(a)) * radius)
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        for k in range(sides):
            k2 = (k + 1) % sides
            faces.append((i * sides + k, i * sides + k2, j * sides + k2, j * sides + k))
    return verts, faces


def ring_set(R):
    S = set(i for i in range(N) if gd[i] <= R)
    uf = {}
    for p in me.polygons:
        vs = list(p.vertices)
        if not all(v in S for v in vs):
            continue
        for j in range(len(vs)):
            k = tuple(sorted((vs[j], vs[(j + 1) % len(vs)])))
            uf.setdefault(k, []).append(p.index)
    fb = [k for k, v in uf.items() if len(v) == 1]
    cn = {}
    for a, b in fb:
        cn.setdefault(a, []).append(b); cn.setdefault(b, []).append(a)
    seen, comps = set(), []
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
    comps.sort(key=len, reverse=True)
    comp = comps[0]
    start = sorted(comp)[0]
    order, prev, cur = [start], None, start
    while True:
        o = [x for x in cn[cur] if x != prev]
        if not o:
            break
        prev, cur = cur, o[0]
        if cur == start:
            break
        order.append(cur)
        if len(order) > len(comp) + 2:
            break
    return [CO[i] for i in order]


# ---- baseline loops
BASE_COL = [(0.85, 0.10, 0.10, 1.0), (0.10, 0.35, 0.90, 1.0), (0.10, 0.65, 0.20, 1.0)]
cmc_ins = [r for r in raw["inserts"]
           if r.get("accepted") and r.get("joint") == "THUMB_CMC" and r.get("new_idx")]
base_objs = []
for k, ins in enumerate(cmc_ins):
    S = set(ins["new_idx"])
    nb = {}
    for e in me.edges:
        a, b = e.vertices[0], e.vertices[1]
        if a in S and b in S:
            nb.setdefault(a, []).append(b); nb.setdefault(b, []).append(a)
    start = sorted(S)[0]
    order, prev, cur = [start], None, start
    while True:
        o = [x for x in nb.get(cur, []) if x != prev]
        if not o:
            break
        prev, cur = cur, o[0]
        if cur == start:
            break
        order.append(cur)
        if len(order) > len(S) + 2:
            break
    vs, fc = tube([CO[i] for i in order], 0.0013, closed=True)
    base_objs.append(make_obj("base_loop%d" % (k + 1), vs, fc, BASE_COL[k % 3]))

# ---- candidate CMC-concentric rings
CAND_COL = [(0.80, 0.05, 0.70, 1.0), (0.05, 0.65, 0.80, 1.0), (0.45, 0.75, 0.05, 1.0)]
cand_objs = []
for k, R in enumerate((0.008, 0.012, 0.016)):
    vs, fc = tube(ring_set(R), 0.0011, closed=True)
    cand_objs.append(make_obj("cand_ring%d" % k, vs, fc, CAND_COL[k % 3]))

# ---- axis / window / marker
_av, _af = tube([CMC + AXIS * (-0.030 + 0.0025 * i) for i in range(41)], 0.0008, closed=False)
axis_obj = make_obj("axis", _av, _af, (0.05, 0.05, 0.05, 1.0))

ref = Vector((0, 0, 1)) if abs(AXIS.z) < 0.9 else Vector((1, 0, 0))
u1 = (ref - AXIS * ref.dot(AXIS)).normalized()
u2 = AXIS.cross(u1)
win_obj = []
for off in (12.0, -12.0):
    c = CMC + AXIS * (off / 1000.0)
    pts = [c + (u1 * math.cos(2 * math.pi * t / 64) + u2 * math.sin(2 * math.pi * t / 64)) * 0.058
           for t in range(64)]
    vs, fc = tube(pts, 0.0006, closed=True)
    win_obj.append(make_obj("win%+d" % int(off), vs, fc, (0.62, 0.0, 0.62, 1.0)))

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0040, location=tuple(CMC))
mk = bpy.context.active_object
mk.color = (1.0, 0.45, 0.0, 1.0)
ob.color = (0.90, 0.90, 0.92, 1.0)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'OBJECT'
scene.display.render_aa = '8'
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
w = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
scene.world = w
w.color = (1.0, 1.0, 1.0)
cd = bpy.data.cameras.new("c")
cd.type = 'ORTHO'
cd.clip_start = 0.001
cam = bpy.data.objects.new("c", cd)
scene.collection.objects.link(cam)
scene.camera = cam

DORS = Vector((0, 1, 0))
d_perp = (DORS - AXIS * DORS.dot(AXIS)).normalized()
d_side = AXIS.cross(d_perp).normalized()


def render(dirv, scale, out, hide=()):
    for o in base_objs + cand_objs:
        o.hide_render = o in hide
    scene.render.filepath = out
    cd.ortho_scale = scale
    pos = CMC + dirv * 0.8
    cam.location = pos
    cam.rotation_euler = (CMC - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.render.render(write_still=True)
    print("RENDERED", os.path.basename(out), os.path.exists(out))


ALLB, ALLC = base_objs, cand_objs
render(d_perp, 0.30, os.path.join(OUTDIR, "CMC_RETOPO_DORSAL.png"), hide=cand_objs)
render(d_perp * -1, 0.30, os.path.join(OUTDIR, "CMC_RETOPO_PALMAR.png"), hide=cand_objs)
render(d_side, 0.30, os.path.join(OUTDIR, "CMC_RETOPO_SIDE.png"), hide=cand_objs)

render(d_perp, 0.30, os.path.join(OUTDIR, "_panel_before.png"), hide=cand_objs)
render(d_perp, 0.30, os.path.join(OUTDIR, "_panel_after.png"), hide=base_objs)

# ---- side-by-side BEFORE / AFTER (same camera)
import numpy as np
a = bpy.data.images.load(os.path.abspath(os.path.join(OUTDIR, "_panel_before.png")))
b = bpy.data.images.load(os.path.abspath(os.path.join(OUTDIR, "_panel_after.png")))
W, H = a.size
buf_a = np.empty(W * H * 4, dtype=np.float32)
buf_b = np.empty(W * H * 4, dtype=np.float32)
a.pixels.foreach_get(buf_a)
b.pixels.foreach_get(buf_b)
buf_a = buf_a.reshape(H, W, 4)
buf_b = buf_b.reshape(H, W, 4)
gap = np.ones((H, 12, 4), dtype=np.float32)
gap[:, :, :3] = 0.15
strip = np.concatenate([buf_a, gap, buf_b], axis=1)
out_img = bpy.data.images.new("ba", width=strip.shape[1], height=H, alpha=True)
out_img.pixels.foreach_set(strip.ravel())
out_img.filepath_raw = os.path.abspath(os.path.join(OUTDIR, "CMC_RETOPO_BEFORE_AFTER.png"))
out_img.file_format = 'PNG'
out_img.save()
for f in ("_panel_before.png", "_panel_after.png"):
    p = os.path.join(OUTDIR, f)
    if os.path.exists(p):
        os.remove(p)
print("WROTE", os.path.join(OUTDIR, "CMC_RETOPO_BEFORE_AFTER.png"))
print("DONE")
