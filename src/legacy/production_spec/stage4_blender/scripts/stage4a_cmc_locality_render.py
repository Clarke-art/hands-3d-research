# STAGE4A CMC LOCALITY REFINEMENT -- dedicated CMC/thenar evidence renders.
#
# Produces a human-reviewable view of the three CMC support loops:
#   * each loop drawn as its own coloured tube (red / blue / green)
#   * CMC rotation centre marked
#   * first metacarpal axis drawn
#   * the +-12 mm deformation window drawn as two cylinders
#   * the rest of the hand shown as a pale underlay (optional)
#
# usage: blender -b <final.blend> --python stage4a_cmc_locality_render.py -- <raw.json> <outdir> <dorsal> <axis-free>
import bpy, sys, json, os, math
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
RAW_JSON, OUTDIR, DORSAL_ARG = argv[0], argv[1], argv[2]
os.makedirs(OUTDIR, exist_ok=True)
DORSAL_OVERRIDE = Vector([float(x) for x in DORSAL_ARG.split(",")]).normalized() if DORSAL_ARG else None

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
CO = [mw @ v.co for v in me.vertices]

raw = json.load(open(RAW_JSON, encoding="utf-8"))
CM = Vector(raw["thumb_cmc_axial_audit"] and raw["insights"]["cmc_center"]) if False else None

# --- CMC frame (mirrors stage4a_cmc_locality.py)
import heapq
N = len(CO)
adj = [[] for _ in range(N)]
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    L = (CO[a] - CO[b]).length
    adj[a].append((b, L))
    adj[b].append((a, L))


def nearest(p):
    best, bi = 1e18, 0
    for i, q in enumerate(CO):
        d = (q - p).length_squared
        if d < best:
            best, bi = d, i
    return bi


M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
loc = mw.translation


def canon(p):
    return (M_NORM @ p) + (loc - (M_NORM @ loc))


TIP_V = nearest(canon(Vector((1.4977, 0.0358, 0.2421))))
ROOT_V = nearest(canon(Vector((1.4489, 0.0115, 0.3134))))
gd = [float("inf")] * N
gd[TIP_V] = 0.0
pq = [(0.0, TIP_V)]
while pq:
    d, u = heapq.heappop(pq)
    if d > gd[u] + 1e-15:
        continue
    for v, w in adj[u]:
        nd = d + w
        if nd < gd[v] - 1e-16:
            gd[v] = nd
            heapq.heappush(pq, (nd, v))
L_THUMB = gd[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gd[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC = CO[ROOT_V]
print("CMC", [round(x, 6) for x in CMC], "AXIS", [round(x, 4) for x in AXIS])


def make_obj(name, verts, faces, color):
    m = bpy.data.meshes.new(name)
    m.from_pydata([tuple(v) for v in verts], [], faces)
    m.update()
    o = bpy.data.objects.new(name, m)
    bpy.context.scene.collection.objects.link(o)
    o.color = color
    return o


def tube(points, radius, closed=True, sides=6):
    """Build a clean tube mesh along a polyline (the Wireframe modifier cannot handle
    edge-only meshes, so the loops are drawn as real geometry)."""
    n = len(points)
    verts, faces = [], []
    ref = Vector((0.0, 0.0, 1.0))
    for i in range(n):
        if closed:
            t = (points[(i + 1) % n] - points[(i - 1) % n])
        else:
            a = points[max(0, i - 1)]
            b = points[min(n - 1, i + 1)]
            t = (b - a)
        if t.length < 1e-12:
            t = Vector((0, 0, 1))
        t = t.normalized()
        r = ref if abs(ref.dot(t)) < 0.9 else Vector((1, 0, 0))
        n1 = (r - t * r.dot(t)).normalized()
        n2 = t.cross(n1)
        for k in range(sides):
            ang = 2 * math.pi * k / sides
            verts.append(points[i] + (n1 * math.cos(ang) + n2 * math.sin(ang)) * radius)
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        for k in range(sides):
            k2 = (k + 1) % sides
            faces.append((i * sides + k, i * sides + k2, j * sides + k2, j * sides + k))
    return verts, faces


# --- loop tubes
COLORS = [(0.85, 0.10, 0.10, 1.0), (0.10, 0.35, 0.90, 1.0), (0.10, 0.65, 0.20, 1.0)]
cmc_ins = [r for r in raw["inserts"]
           if r.get("accepted") and r.get("joint") == "THUMB_CMC" and r.get("new_idx")]
loop_objs = []
for k, ins in enumerate(cmc_ins):
    S = set(ins["new_idx"])
    verts = {i: CO[i] for i in S}
    idx = {i: n for n, i in enumerate(sorted(S))}
    # order the loop into a polyline by walking its ring edges
    ring = [(e.vertices[0], e.vertices[1]) for e in me.edges
            if e.vertices[0] in S and e.vertices[1] in S]
    nb = {}
    for a, b in ring:
        nb.setdefault(a, []).append(b)
        nb.setdefault(b, []).append(a)
    start = sorted(S)[0]
    order, prev, cur = [start], None, start
    while True:
        nxts = [x for x in nb.get(cur, []) if x != prev]
        if not nxts:
            break
        nxt = nxts[0]
        if nxt == start:
            break
        order.append(nxt)
        prev, cur = cur, nxt
        if len(order) > len(S) + 2:
            break
    pts = [CO[i] for i in order]
    vs, fc = tube(pts, 0.0011, closed=True)
    ans = [o for o in loop_objs]
    o = make_obj("loop%d" % (k + 1), vs, fc, COLORS[k % 3])
    loop_objs.append(o)
    print("loop%d: %d verts %d ring edges -> tube %d verts %d faces closed=%s"
          % (k + 1, len(S), len(ring), len(vs), len(fc), len(order) == len(S)))

# --- metacarpal axis: a thin line + tick rings at 0 and +-12 mm
axis_pts = [CMC + AXIS * (-0.030 + 0.0025 * i) for i in range(35)]
_av, _af = tube(axis_pts, 0.0007, closed=False)
make_obj("axis", _av, _af, (0.05, 0.05, 0.05, 1.0))

ref = Vector((0, 0, 1)) if abs(AXIS.z) < 0.9 else Vector((1, 0, 0))
u1 = (ref - AXIS * ref.dot(AXIS)).normalized()
u2 = AXIS.cross(u1)
for off_mm, col in ((12.0, (0.55, 0.0, 0.55, 1.0)), (-12.0, (0.55, 0.0, 0.55, 1.0))):
    c = CMC + AXIS * (off_mm / 1000.0)
    pts = [c + (u1 * math.cos(2 * math.pi * t / 64) + u2 * math.sin(2 * math.pi * t / 64)) * 0.052
           for t in range(64)]
    _wv, _wf = tube(pts, 0.00055, closed=True)
    make_obj("win_%+d" % off_mm, _wv, _wf, col)

# --- CMC centre marker
_sph = []
for _i in range(12):
    pass
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0045, location=tuple(CMC))
_marker = bpy.context.active_object
_marker.name = "cmc_center"
_marker.color = (1.0, 0.45, 0.0, 1.0)

# --- pale hand underlay
hand = ob
hand.color = (0.88, 0.88, 0.90, 1.0)

# --- camera
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'OBJECT'
scene.display.shading.background_type = 'WORLD'
_w = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W")
scene.world = _w
_w.color = (1.0, 1.0, 1.0)
scene.display.render_aa = '8'
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000

cam_data = bpy.data.cameras.new("c")
cam_data.type = 'ORTHO'
cam_data.clip_start = 0.001
cam = bpy.data.objects.new("c", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
hand.hide_render = False


def render(dirv, scale, out, hide_hand=False):
    hand.hide_render = hide_hand
    scene.render.filepath = out
    cam_data.ortho_scale = scale
    pos = CMC + dirv * 0.8
    cam.location = pos
    cam.rotation_euler = (CMC - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.render.render(write_still=True)
    print("RENDERED", out, "exists=", os.path.exists(out))


DORS = DORSAL_OVERRIDE if DORSAL_OVERRIDE is not None else Vector((0, 1, 0))
d_perp = (DORS - AXIS * DORS.dot(AXIS)).normalized()
d_side = AXIS.cross(d_perp).normalized()

render(d_perp, 0.17, os.path.join(OUTDIR, "THUMB_CMC_LOCALITY_REVIEW.png"))
render(d_side, 0.17, os.path.join(OUTDIR, "THUMB_CMC_LOCALITY_SIDE.png"))
render(d_perp, 0.17, os.path.join(OUTDIR, "THUMB_CMC_LOCALITY_REVIEW_loops_only.png"), hide_hand=True)
print("DONE")
