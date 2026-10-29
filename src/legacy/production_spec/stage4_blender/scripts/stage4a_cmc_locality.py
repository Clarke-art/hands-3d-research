# STAGE4A CMC LOCALITY REFINEMENT -- axis-based audit of the thumb CMC support loops.
#
# Required measurements (reviewer, STAGE4A_CMC_LOCALITY_REFINEMENT_R1 section 4/5):
#   ACTUAL_AXIAL_MIN / MAX / SPAN, AXIAL_MEDIAN, AXIAL_STDDEV per loop,
#   fraction of vertices inside +-12 mm and +-18 mm, largest axial outlier,
#   loop closure, and surface deviation vs the official L1 reference surface.
#
# Axis: first metacarpal axis, derived exactly as the engineering pipeline does
#       (through the thumb tip and the mid-phalanx centreline; anchored on the
#        projection of the measured thumb root = CMC rotation centre).
#
# usage: blender -b RIGHT_HAND_BOOTSTRAP_C1.blend --python stage4a_cmc_locality.py -- <final.blend> <raw.json> <out.json>
import bpy, sys, json, math, heapq, statistics, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]
FINAL_BLEND, RAW_JSON, OUT_JSON = argv[0], argv[1], argv[2]

TIP_SEED = Vector((1.4977, 0.0358, 0.2421))            # thumb tip, SOURCE frame
ROOT_SEED = Vector((1.4489, 0.0115, 0.3134))           # thumb root = CMC centre, SOURCE frame
M_NORM = Matrix(((1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0)))

TARGET = "Hand  - Realistic"


def build_reference():
    """Official L1 surface, frame-normalised -> BVH (the shape the CMC work must not alter)."""
    ob = bpy.data.objects[TARGET]
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    for m in list(ob.modifiers):
        if m.type == 'MULTIRES':
            m.levels = 1
            bpy.ops.object.modifier_apply(modifier=m.name)
    ob.select_set(False)
    loc = ob.matrix_world.translation.copy()
    me = ob.data
    # the pipeline transforms the mesh DATA (v.co -> M @ v.co) and leaves the object
    # location untouched, so the resulting world position is  loc + (M @ local).
    verts = [loc + (M_NORM @ v.co) for v in me.vertices]
    faces = [tuple(p.vertices) for p in me.polygons]
    return BVHTree.FromPolygons(verts, faces, all_triangles=False), len(verts), len(faces)


BVH, REF_V, REF_F = build_reference()
print("REFERENCE (official L1, canonical frame): V=%d F=%d" % (REF_V, REF_F))

bpy.ops.wm.open_mainfile(filepath=FINAL_BLEND)
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
CO = [mw @ v.co for v in me.vertices]
N = len(CO)

# ---------------- adjacency + geodesic from the thumb tip
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


def canon(p):                       # SOURCE-frame world -> canonical-frame world
    loc = mw.translation
    return (M_NORM @ p) + (loc - (M_NORM @ loc))


TIP_V = nearest(canon(TIP_SEED))
ROOT_V = nearest(canon(ROOT_SEED))
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
band_ids = [i for i in range(N) if 0.25 * L_THUMB <= gd[i] <= 0.55 * L_THUMB]
c_mid = sum((CO[i] for i in band_ids), Vector()) / len(band_ids)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC_CENTER = CO[ROOT_V]

print("CMC centre   = [%.6f, %.6f, %.6f]" % tuple(CMC_CENTER))
print("metacarpal axis = [%.4f, %.4f, %.4f]   thumb geodesic length = %.2f mm"
      % (AXIS.x, AXIS.y, AXIS.z, L_THUMB * 1000))


def axial(p):
    return (p - ANCHOR).dot(AXIS)


raw = json.load(open(RAW_JSON, encoding="utf-8"))
cmc_ins = [r for r in raw["inserts"]
           if r.get("accepted") and r.get("joint") == "THUMB_CMC" and r.get("new_idx")]

LOOPS = []
for k, ins in enumerate(cmc_ins, 1):
    idx = ins["new_idx"]
    idxset = set(idx)
    ax = [axial(CO[i]) for i in idx]
    # closure: every vertex must have exactly 2 neighbours inside the same loop
    deg = {i: 0 for i in idx}
    for e in me.edges:
        a, b = e.vertices[0], e.vertices[1]
        if a in deg and b in deg:
            deg[a] += 1
            deg[b] += 1
    closed = all(v == 2 for v in deg.values())
    in12 = sum(1 for x in ax if abs(x) <= 0.012)
    in18 = sum(1 for x in ax if abs(x) <= 0.018)
    dev = [(CO[i] - BVH.find_nearest(CO[i])[0]).length if BVH.find_nearest(CO[i])[0] else 0.0
           for i in idx]
    dev.sort()
    LOOPS.append({
        "loop": k, "label": ins["label"], "target_offset_mm": ins["offset_mm"],
        "vertex_count": len(idx),
        "closed_topological_loop": bool(closed),
        "ACTUAL_AXIAL_MIN_mm": round(min(ax) * 1000, 2),
        "ACTUAL_AXIAL_MAX_mm": round(max(ax) * 1000, 2),
        "ACTUAL_AXIAL_SPAN_mm": round((max(ax) - min(ax)) * 1000, 2),
        "AXIAL_MEDIAN_mm": round(statistics.median(ax) * 1000, 2),
        "AXIAL_MEAN_mm": round(statistics.fmean(ax) * 1000, 2),
        "AXIAL_STDDEV_mm": round(statistics.pstdev(ax) * 1000, 2),
        "largest_axial_outlier_mm": round(max(abs(x) for x in ax) * 1000, 2),
        "frac_within_pm12mm": round(in12 / len(idx), 4),
        "frac_within_pm18mm": round(in18 / len(idx), 4),
        "surface_dev_vs_L1_max_mm": round(dev[-1] * 1000, 3),
        "surface_dev_vs_L1_p95_mm": round(dev[int(0.95 * (len(dev) - 1))] * 1000, 3),
        "locality": "HELICAL_NON_LOCAL" if (max(ax) - min(ax)) * 1000 > 40 else "LOCAL",
    })

spans = [L["ACTUAL_AXIAL_SPAN_mm"] for L in LOOPS]
out = {
    "stage": "STAGE4A_CMC_LOCALITY_REFINEMENT_R1",
    "cmc_rotation_center": [round(x, 6) for x in CMC_CENTER],
    "first_metacarpal_axis": [round(x, 6) for x in AXIS],
    "thumb_geodesic_length_mm": round(L_THUMB * 1000, 2),
    "deformation_window_mm": {"primary": 12.0, "secondary": 18.0},
    "thresholds": {"local_pass_axial_span_mm": 40.0,
                   "note": "reviewer: a 40-60+ mm axial span may not be judged PASS"},
    "loops": LOOPS,
    "worst_axial_span_mm": max(spans) if spans else None,
    "mean_axial_span_mm": round(sum(spans) / len(spans), 2) if spans else None,
    "all_closed": bool(all(L["closed_topological_loop"] for L in LOOPS)),
    "max_surface_deviation_mm": max([L["surface_dev_vs_L1_max_mm"] for L in LOOPS] or [0]),
    "p95_surface_deviation_mm": max([L["surface_dev_vs_L1_p95_mm"] for L in LOOPS] or [0]),
    "verdict": ("LOCAL" if spans and max(spans) <= 40.0 else "NEEDS_REVISION"),
    "reference_surface": {"source": "official MULTIRES L1, canonical frame",
                          "verts": REF_V, "faces": REF_F},
}
json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=" * 78)
for L in LOOPS:
    print("  loop %d %-18s span=%7.2f mm  [%7.2f,%7.2f]  median=%7.2f std=%6.2f  "
          "in+-12=%.2f in+-18=%.2f  outlier=%6.2f  closed=%s"
          % (L["loop"], L["label"], L["ACTUAL_AXIAL_SPAN_mm"], L["ACTUAL_AXIAL_MIN_mm"],
             L["ACTUAL_AXIAL_MAX_mm"], L["AXIAL_MEDIAN_mm"], L["AXIAL_STDDEV_mm"],
             L["frac_within_pm12mm"], L["frac_within_pm18mm"], L["largest_axial_outlier_mm"],
             L["closed_topological_loop"]))
print("  worst span = %.2f mm   mean span = %.2f mm   verdict = %s"
      % (out["worst_axial_span_mm"], out["mean_axial_span_mm"], out["verdict"]))
print("  surface deviation vs L1: max = %.3f mm  p95 = %.3f mm"
      % (out["max_surface_deviation_mm"], out["p95_surface_deviation_mm"]))
print("WROTE", OUT_JSON)
