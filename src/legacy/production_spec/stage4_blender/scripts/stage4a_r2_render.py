# STAGE4A_R2 -- human-review evidence renders for the THUMB CMC local deformation cage.
#
# mode=before : the R1 baseline's three 66 mm helical pseudo-collars (red / blue / green)
# mode=after  : the R2 cage -- boundary loop + three concentric rings + radial spokes
#
# Overlays in both modes: CMC rotation centre (orange), first metacarpal axis (black),
# the +-12 mm engineering window (magenta).
#
# usage: blender -b <blend> --python stage4a_r2_render.py -- <outdir> <before|after> <json>
import bpy, sys, json, os, math, heapq
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, MODE, JSON_IN = argv[0], argv[1], argv[2]
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
    return bi


TIP_V, ROOT_V = nearest(canon(TIP_SEED)), nearest(canon(ROOT_SEED))
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


gdt = dij(TIP_V)
L_THUMB = gdt[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gdt[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
CMC = CO[ROOT_V]

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


loops = []
if MODE == "before":
    COL = [(0.85, 0.10, 0.10, 1.0), (0.10, 0.35, 0.90, 1.0), (0.10, 0.65, 0.20, 1.0)]
    for k, ins in enumerate([r for r in data["inserts"]
                             if r.get("accepted") and r.get("joint") == "THUMB_CMC"
                             and r.get("new_idx")]):
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
        vs, fc = tube([CO[i] for i in order], 0.0016, closed=True)
        loops.append(make_obj("legacy_loop%d" % (k + 1), vs, fc, COL[k % 3]))
    print("before mode: %d legacy loops" % len(loops))
else:
    COL = [(0.55, 0.55, 0.60, 1.0), (0.80, 0.05, 0.70, 1.0),
           (0.05, 0.65, 0.80, 1.0), (0.45, 0.75, 0.05, 1.0)]
    for k, rw in enumerate(data["ring_world"]):
        pts = [Vector(p) for p in rw]
        vs, fc = tube(pts, 0.0016 if k == 0 else 0.0020, closed=True)
        loops.append(make_obj("cage_ring%d" % k, vs, fc, COL[k % 4]))
    # radial spokes: every 4th spoke, thin
    b0 = [Vector(p) for p in data["ring_world"][0]]
    b3 = [Vector(p) for p in data["ring_world"][-1]]
    for j in range(0, len(b0), 4):
        vs, fc = tube([b0[j], (b0[j] + b3[j]) / 2, b3[j]], 0.0008, closed=False)
        loops.append(make_obj("spoke%d" % j, vs, fc, (0.20, 0.20, 0.25, 1.0)))
    print("after mode: %d rings + spokes" % len(data["ring_world"]))

_av, _af = tube([CMC + AXIS * (-0.030 + 0.0025 * i) for i in range(41)], 0.0008, closed=False)
make_obj("axis", _av, _af, (0.05, 0.05, 0.05, 1.0))
ref = Vector((0, 0, 1)) if abs(AXIS.z) < 0.9 else Vector((1, 0, 0))
u1 = (ref - AXIS * ref.dot(AXIS)).normalized()
u2 = AXIS.cross(u1)
for off in (12.0, -12.0):
    c = CMC + AXIS * (off / 1000.0)
    pts = [c + (u1 * math.cos(2 * math.pi * t / 64) + u2 * math.sin(2 * math.pi * t / 64)) * 0.058
           for t in range(64)]
    vs, fc = tube(pts, 0.0006, closed=True)
    make_obj("win%+d" % int(off), vs, fc, (0.62, 0.0, 0.62, 1.0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0040, location=tuple(CMC))
bpy.context.active_object.color = (1.0, 0.45, 0.0, 1.0)
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


def render(dirv, out, scale, xray=False):
    scene.render.filepath = out
    cd.ortho_scale = scale
    scene.display.shading.show_xray = xray
    scene.display.shading.xray_alpha = 0.45
    pos = CMC + dirv * 0.8
    cam.location = pos
    cam.rotation_euler = (CMC - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.render.render(write_still=True)
    print("RENDERED", os.path.basename(out), os.path.exists(out))


# a comparable wide framing for the BEFORE / AFTER pair (the whole 66 mm legacy span must
# be visible), plus a zoomed framing that actually resolves the 16 mm cage.
# The CMC surface point sits on the radial-DORSAL aspect of the thumb base, so a strict
# palmar view would occlude the cage -- that one view is rendered with x-ray.
WIDE, ZOOM = 0.16, 0.085
P = "_panel_%s" % MODE
SC = WIDE if MODE == "before" else ZOOM
for nm, dv, xr in (("dorsal", d_perp, False), ("palmar", -d_perp, True), ("side", d_side, True)):
    render(dv, os.path.join(OUTDIR, "%s_%s.png" % (P, nm)), SC, xr)
if MODE == "after":
    import shutil
    for nm, dv, xr in (("dorsal", d_perp, False), ("palmar", -d_perp, True), ("side", d_side, True)):
        render(dv, os.path.join(OUTDIR, "_panel_after_%s.png" % nm), WIDE, xr)
        shutil.copy(os.path.join(OUTDIR, "%s_%s.png" % (P, nm)),
                    os.path.join(OUTDIR, "CMC_RETOPO_%s.png" % nm.upper()))
    print("copied dorsal/palmar/side deliverables (zoomed)")
print("DONE")
