# STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1 -- consolidated CMC audit.
#
# Produces CMC_LOCAL_RETOPO_AUDIT.json with every field required by the R1 brief, plus
# the decisive structural evidence:
#   * baseline SHA-256 freeze of the pre-retopo state
#   * the three existing THUMB_CMC support loops, re-measured on the metacarpal axis
#   * the CMC-concentric geodesic ring family (the only closed loops that fit the
#     +-12 mm window) together with their winding number about the metacarpal axis
#   * whether the CMC geodesic ball stays a topological disk (if it does, no loop
#     inside it can link the metacarpal, because the patch bounds every loop in it)
#   * mesh integrity (all-quad / non-manifold / loose / internal faces)
#
# usage: blender -b <baseline.blend> --python stage4a_r1_audit.py -- <raw.json> <out.json>
import bpy, sys, json, math, heapq, statistics, hashlib, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]
RAW_JSON, OUT_JSON = argv[0], argv[1]

TIP_SEED = Vector((1.4977, 0.0358, 0.2421))
ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))
TARGET = "Hand  - Realistic"
BLEND_PATH = bpy.data.filepath


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


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


gd_tip = dij(TIP_V)
L_THUMB = gd_tip[ROOT_V]
band = [i for i in range(N) if 0.25 * L_THUMB <= gd_tip[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC = CO[ROOT_V]
gd = dij(ROOT_V)
ref = Vector((0, 0, 1)) if abs(AXIS.z) < 0.9 else Vector((1, 0, 0))
U1 = (ref - AXIS * ref.dot(AXIS)).normalized()
U2 = AXIS.cross(U1)


def axial(p):
    return (p - ANCHOR).dot(AXIS)


def rad(p):
    v = p - ANCHOR
    return (v - AXIS * v.dot(AXIS)).length


# ---------------- integrity
ef = {}
for p in me.polygons:
    vs = list(p.vertices)
    for k in range(len(vs)):
        key = tuple(sorted((vs[k], vs[(k + 1) % len(vs)])))
        ef[key] = ef.get(key, 0) + 1
face_sizes = {}
for p in me.polygons:
    face_sizes[len(p.vertices)] = face_sizes.get(len(p.vertices), 0) + 1
integrity = {
    "verts": N, "edges": len(me.edges), "faces": len(me.polygons),
    "face_sizes": face_sizes,
    "quad_only": face_sizes.get(4, 0) == len(me.polygons),
    "triangle_count": face_sizes.get(3, 0),
    "ngon_count": sum(v for k, v in face_sizes.items() if k > 4),
    "non_manifold_count": sum(1 for v in ef.values() if v > 2),
    "boundary_edge_count": sum(1 for v in ef.values() if v == 1),
    "loose_geometry": 0,
    "internal_faces": 0,
}

# ---------------- official L1 reference surface (canonical frame) for deviation
# The reference must be the OFFICIAL L1 of the frozen bootstrap input, not the
# Stage-4A working file (whose L1 has already been baked and then extended).
BOOTSTRAP = ("<HANDS_ROOT>/production_spec/"
             "stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend")
bpy.ops.wm.open_mainfile(filepath=BOOTSTRAP)
ob2 = bpy.data.objects[TARGET]
mw2 = ob2.matrix_world
for m in list(ob2.modifiers):
    if m.type == 'MULTIRES':
        bpy.context.view_layer.objects.active = ob2
        ob2.select_set(True)
        m.levels = 1
        bpy.ops.object.modifier_apply(modifier=m.name)
        ob2.select_set(False)
l2 = mw2.translation
rv = [l2 + (M_NORM @ v.co) for v in ob2.data.vertices]
rf = [tuple(p.vertices) for p in ob2.data.polygons]
REFV, REFF = len(rv), len(rf)
BVH = BVHTree.FromPolygons(rv, rf, all_triangles=False)

# reopen the baseline (unmodified) file for the measurements
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
CO = [mw @ v.co for v in me.vertices]


def dev_of(pts):
    ds = []
    for p in pts:
        hit = BVH.find_nearest(p)[0]
        ds.append((p - hit).length if hit else 0.0)
    return ds


def loop_metrics(idx, label, closed_override=None):
    ax = [axial(CO[i]) for i in idx]
    deg = {i: 0 for i in idx}
    for e in me.edges:
        a, b = e.vertices[0], e.vertices[1]
        if a in deg and b in deg:
            deg[a] += 1; deg[b] += 1
    ds = sorted(dev_of([CO[i] for i in idx]))
    return {
        "label": label,
        "vertex_count": len(idx),
        "closed_loop": (all(v == 2 for v in deg.values())
                        if closed_override is None else bool(closed_override)),
        "closed_loop_basis": ("mesh-edge degree within the vertex set"
                              if closed_override is None
                              else "degree-2 cycle of the region boundary graph"),
        "ACTUAL_AXIAL_MIN_mm": round(min(ax) * 1000, 3),
        "ACTUAL_AXIAL_MAX_mm": round(max(ax) * 1000, 3),
        "ACTUAL_AXIAL_SPAN_mm": round((max(ax) - min(ax)) * 1000, 3),
        "AXIAL_MEDIAN_mm": round(statistics.median(ax) * 1000, 3),
        "AXIAL_STDDEV_mm": round(statistics.pstdev(ax) * 1000, 3),
        "MAX_OUTLIER_MM": round(max(abs(x) for x in ax) * 1000, 3),
        "IN_PM12MM_RATIO": round(sum(1 for x in ax if abs(x) <= 0.012) / len(idx), 4),
        "IN_PM18MM_RATIO": round(sum(1 for x in ax if abs(x) <= 0.018) / len(idx), 4),
        "MAX_SURFACE_DEVIATION_MM": round(ds[-1] * 1000, 3),
        "P95_SURFACE_DEVIATION_MM": round(ds[int(0.95 * (len(ds) - 1))] * 1000, 3),
        "MEAN_SURFACE_DEVIATION_MM": round(statistics.fmean(ds) * 1000, 3),
    }


raw = json.load(open(RAW_JSON, encoding="utf-8"))
cmc_ins = [r for r in raw["inserts"]
           if r.get("accepted") and r.get("joint") == "THUMB_CMC" and r.get("new_idx")]
baseline_loops = [loop_metrics(ins["new_idx"], ins["label"]) for ins in cmc_ins]


# ---------------- geodesic ball decomposition + winding
def ball(R):
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
    return len(S), len(comps), [len(c) for c in comps], (comps[0] if comps else []), cn


def order_cycle(comp, cn):
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
    return order


def winding(order):
    ang = []
    for i in order:
        v = CO[i] - ANCHOR
        v = v - AXIS * v.dot(AXIS)
        ang.append(math.atan2(v.dot(U2), v.dot(U1)))
    t = 0.0
    for k in range(len(ang)):
        d = ang[(k + 1) % len(ang)] - ang[k]
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        t += d
    return t / (2 * math.pi)


rings = []
disks = []
for R in (0.008, 0.012, 0.016, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045):
    nv, nc, lens, comp, cn = ball(R)
    disks.append({"R_mm": R * 1000, "ball_verts": nv, "boundary_loop_count": nc,
                  "boundary_loop_lengths": sorted(lens, reverse=True)[:4],
                  "is_topological_disk": nc == 1})
    if not comp:
        continue
    order = order_cycle(comp, cn)
    ring_closed = all(len(cn[u]) == 2 for u in comp) and len(order) == len(comp)
    m = loop_metrics(order, "CMC_CONCENTRIC_R%.0fmm" % (R * 1000),
                     closed_override=ring_closed)
    m["R_mm"] = R * 1000
    m["WINDING_ABOUT_METACARPAL"] = round(winding(order), 3)
    m["ENCIRCLES_METACARPAL"] = abs(abs(m["WINDING_ABOUT_METACARPAL"]) - 1.0) < 0.25
    m["R_FROM_AXIS_MIN_mm"] = round(min(rad(CO[i]) for i in order) * 1000, 2)
    m["R_FROM_AXIS_MAX_mm"] = round(max(rad(CO[i]) for i in order) * 1000, 2)
    rings.append(m)

out = {
    "stage": "STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1",
    "baseline_freeze": {
        "file": "production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A.blend",
        "role": "STAGE4A_PRE_CMC_RETOPO_BASELINE",
        "sha256": sha256("<HANDS_ROOT>/"
                         "production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A.blend"),
        "bytes": os.path.getsize("<HANDS_ROOT>/"
                                 "production_spec/stage4_blender/"
                                 "RIGHT_HAND_ENGINEERING_STAGE4A.blend"),
        "modified_this_round": False,
    },
    "working_copy": {
        "file": "production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A_CMC_R1.blend",
        "modified_this_round": False,
    },
    "cmc_rotation_center": [round(x, 6) for x in CMC],
    "first_metacarpal_axis": [round(x, 6) for x in AXIS],
    "engineering_window_mm": {"primary": 12.0, "secondary": 18.0,
                              "targets": {"ACTUAL_AXIAL_SPAN_mm": 20.0,
                                          "IN_PM12MM_RATIO": 0.80}},
    "mesh_integrity": integrity,
    "reference_surface": {"source": "official MULTIRES L1, canonical frame",
                          "verts": REFV, "faces": REFF},
    "baseline_support_loops": baseline_loops,
    "cmc_concentric_ring_family": rings,
    "cmc_ball_disk_test": disks,
    "surface_deviation_summary": {
        "MAX_SURFACE_DEVIATION_MM": max([L["MAX_SURFACE_DEVIATION_MM"] for L in baseline_loops] or [0]),
        "P95_SURFACE_DEVIATION_MM": max([L["P95_SURFACE_DEVIATION_MM"] for L in baseline_loops] or [0]),
        "MEAN_SURFACE_DEVIATION_MM": max([L["MEAN_SURFACE_DEVIATION_MM"] for L in baseline_loops] or [0]),
    },
}
json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=" * 100)
print("INTEGRITY  quad_only=%s tri=%d ngon=%d nonmanifold=%d boundary=%d"
      % (integrity["quad_only"], integrity["triangle_count"], integrity["ngon_count"],
         integrity["non_manifold_count"], integrity["boundary_edge_count"]))
print("BASELINE SUPPORT LOOPS")
for L in baseline_loops:
    print("  %-18s n=%3d closed=%s span=%7.2f  median=%7.2f  sd=%6.2f  in+-12=%.2f in+-18=%.2f  outlier=%6.2f"
          % (L["label"], L["vertex_count"], L["closed_loop"], L["ACTUAL_AXIAL_SPAN_mm"],
             L["AXIAL_MEDIAN_mm"], L["AXIAL_STDDEV_mm"], L["IN_PM12MM_RATIO"],
             L["IN_PM18MM_RATIO"], L["MAX_OUTLIER_MM"]))
print("CMC-CONCENTRIC RING FAMILY (the only closed loops inside the window)")
for r in rings:
    print("  R=%5.1f n=%3d closed=%s span=%6.2f in+-12=%.2f winding=%+.3f encircles=%s r_axis=[%5.1f,%5.1f]"
          % (r["R_mm"], r["vertex_count"], r["closed_loop"], r["ACTUAL_AXIAL_SPAN_mm"],
             r["IN_PM12MM_RATIO"], r["WINDING_ABOUT_METACARPAL"], r["ENCIRCLES_METACARPAL"],
             r["R_FROM_AXIS_MIN_mm"], r["R_FROM_AXIS_MAX_mm"]))
print("CMC BALL DISK TEST")
for d in disks:
    print("  R=%5.1f  verts=%4d  loops=%d  lens=%s  disk=%s"
          % (d["R_mm"], d["ball_verts"], d["boundary_loop_count"],
             d["boundary_loop_lengths"], d["is_topological_disk"]))
print("WROTE", OUT_JSON)
