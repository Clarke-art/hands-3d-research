# STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1 -- geodesic-ring evidence render.
#
# Draws the geodesic ball boundaries around the CMC rotation centre (a family of
# closed loops concentric about the CMC surface point) together with the CMC marker,
# the first metacarpal axis and the +-12 mm engineering window.
#
# The purpose is to decide, visually, whether "rings centred on the CMC" form a
# sensible local collar around the thumb base -- something the fixed axial plane
# cannot do, because the axial level sets around the CMC wrap the whole hand.
#
# usage: blender -b <blend> --python stage4a_r1_georing_render.py -- <outdir> <radii_csv>
import bpy, sys, json, os, math, heapq
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
RADII = [float(x) for x in argv[1].split(",")]
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


TIP_V = nearest(canon(TIP_SEED))
ROOT_V = nearest(canon(ROOT_SEED))

adj = [[] for _ in range(N)]
for e in me.edges:
    a, b = e.vertices[0], e.vertices[1]
    L = (CO[a] - CO[b]).length
    adj[a].append((b, L))
    adj[b].append((a, L))


def dijkstra(src):
    d = [float("inf")] * N
    d[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u] + 1e-15:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v] - 1e-16:
                d[v] = nd
                heapq.heappush(pq, (nd, v))
    return d


gd_tip = dijkstra(TIP_V)
L_THUMB = gd_tip[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gd_tip[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC = CO[ROOT_V]
gd = dijkstra(ROOT_V)


def axial(p):
    return (p - ANCHOR).dot(AXIS)


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
        if closed:
            t = (points[(i + 1) % n] - points[(i - 1) % n])
        else:
            t = (points[min(n - 1, i + 1)] - points[max(0, i - 1)])
        if t.length < 1e-12:
            t = Vector((0, 0, 1))
        t = t.normalized()
        r = ref if abs(ref.dot(t)) < 0.9 else Vector((1, 0, 0))
        n1 = (r - t * r.dot(t)).normalized()
        n2 = t.cross(n1)
        for k in range(sides):
            ang = 2 * math.pi * k / sides
            verts.append(points[i] + (n1 * math.cos(ang) + n2 * math.sin(ang)) * radius)
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        for k in range(sides):
            k2 = (k + 1) % sides
            faces.append((i * sides + k, i * sides + k2, j * sides + k2, j * sides + k))
    return verts, faces


# ---- collect the face-region boundary loops of the geodesic balls
COLOURS = [(0.85, 0.10, 0.10, 1.0), (0.95, 0.55, 0.05, 1.0), (0.10, 0.65, 0.20, 1.0),
           (0.10, 0.35, 0.90, 1.0), (0.60, 0.10, 0.75, 1.0)]
report = []
for k, R in enumerate(RADII):
    S = set(i for i in range(N) if gd[i] <= R)
    uf = {}
    for p in me.polygons:
        vs = list(p.vertices)
        if not all(v in S for v in vs):
            continue
        for j in range(len(vs)):
            key = tuple(sorted((vs[j], vs[(j + 1) % len(vs)])))
            uf.setdefault(key, []).append(p.index)
    fb = [key for key, v in uf.items() if len(v) == 1]
    cn = {}
    for a, b in fb:
        cn.setdefault(a, []).append(b)
        cn.setdefault(b, []).append(a)
    seen = set()
    comps = []
    for s in cn:
        if s in seen:
            continue
        comp, stack = [], [s]
        seen.add(s)
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in cn[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    for ci, comp in enumerate(comps[:1]):
        cs = set(comp)
        # order the cycle
        start = sorted(cs)[0]
        order, prev, cur = [start], None, start
        while True:
            opts = [x for x in cn[cur] if x != prev]
            if not opts:
                break
            prev, cur = cur, opts[0]
            if cur == start:
                break
            order.append(cur)
            if len(order) > len(cs) + 2:
                break
        pts = [CO[i] for i in order]
        vs, fc = tube(pts, 0.0009, closed=True)
        make_obj("ring_%d" % k, vs, fc, COLOURS[k % len(COLOURS)])
        ax = [axial(CO[i]) * 1000 for i in comp]
        rr = []
        for i in comp:
            v = CO[i] - ANCHOR
            rr.append((v - AXIS * v.dot(AXIS)).length * 1000)
        report.append({"R_mm": R * 1000, "verts": len(cs), "edges": len(fb) and len(comp),
                       "closed": all(len(cn[u]) == 2 for u in comp),
                       "axial_min_mm": round(min(ax), 2), "axial_max_mm": round(max(ax), 2),
                       "axial_span_mm": round(max(ax) - min(ax), 2),
                       "r_min_mm": round(min(rr), 2), "r_max_mm": round(max(rr), 2)})
        print("RING R=%5.1f mm  verts=%3d closed=%s  axial=[%7.2f,%7.2f] span=%6.2f  r=[%5.1f,%5.1f]"
              % (R * 1000, len(cs), all(len(cn[u]) == 2 for u in comp),
                 min(ax), max(ax), max(ax) - min(ax), min(rr), max(rr)))

# ---- axis, window, marker
axis_pts = [CMC + AXIS * (-0.035 + 0.0025 * i) for i in range(41)]
_av, _af = tube(axis_pts, 0.0006, closed=False)
make_obj("axis", _av, _af, (0.05, 0.05, 0.05, 1.0))

ref = Vector((0, 0, 1)) if abs(AXIS.z) < 0.9 else Vector((1, 0, 0))
u1 = (ref - AXIS * ref.dot(AXIS)).normalized()
u2 = AXIS.cross(u1)
for off_mm in (12.0, -12.0):
    c = CMC + AXIS * (off_mm / 1000.0)
    pts = [c + (u1 * math.cos(2 * math.pi * t / 64) + u2 * math.sin(2 * math.pi * t / 64)) * 0.055
           for t in range(64)]
    _wv, _wf = tube(pts, 0.0005, closed=True)
    make_obj("win_%+d" % int(off_mm), _wv, _wf, (0.55, 0.0, 0.55, 1.0))

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0035, location=tuple(CMC))
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


def render(dirv, scale, out, hide_hand=False):
    ob.hide_render = hide_hand
    scene.render.filepath = out
    cd.ortho_scale = scale
    pos = CMC + dirv * 0.8
    cam.location = pos
    cam.rotation_euler = (CMC - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.render.render(write_still=True)
    print("RENDERED", out, os.path.exists(out))


render(d_perp, 0.115, os.path.join(OUTDIR, "R1_GEORING_DORSAL.png"))
render(d_side, 0.115, os.path.join(OUTDIR, "R1_GEORING_SIDE.png"))
render(d_perp, 0.115, os.path.join(OUTDIR, "R1_GEORING_LOOPS_ONLY.png"), hide_hand=True)
json.dump(report, open(os.path.join(OUTDIR, "R1_GEORING.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("DONE")
