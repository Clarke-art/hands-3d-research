# STAGE4A CMC LOCALITY REFINEMENT -- CMC-specific pole audit.
#
# Re-audits the poles in the thumb CMC / MCP neighbourhood and splits them into the three
# categories the reviewer asked for:
#   CMC_CORE_POLES             poles inside the CMC bending core window
#   CMC_FLEXION_MIDLINE_POLES  poles on the dorsal/palmar crest (where flexion pinches)
#   CMC_OPPOSITION_PATH_POLES  poles on the palmar-radial thenar path loaded in opposition
#
# usage: blender -b RIGHT_HAND_ENGINEERING_STAGE4A.blend --python stage4a_cmc_pole_audit.py -- <raw.json> <out.json>
import bpy, sys, json, math, heapq
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
RAW_JSON, OUT_JSON = argv[0], argv[1]
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
N = len(me.vertices)
CO = [mw @ v.co for v in me.vertices]

raw = json.load(open(RAW_JSON, encoding="utf-8"))
DORSAL = Vector(raw["frame_after"]["DORSAL_axis"]).normalized()
PALMAR = -DORSAL
RADIAL = Vector(raw["frame_after"]["RADIAL_axis"]).normalized()

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


def canon(p):
    loc = mw.translation
    return (Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1))) @ p) + \
           (loc - (Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1))) @ loc))


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
L = gd[ROOT_V]
band = [i for i in range(N) if 0.25 * L <= gd[i] <= 0.55 * L]
c_mid = sum((CO[i] for i in band), Vector()) / len(band)
AXIS = (CO[TIP_V] - c_mid).normalized()
ANCHOR = CO[TIP_V] + AXIS * ((CO[ROOT_V] - CO[TIP_V]).dot(AXIS))
CMC = CO[ROOT_V]

val = [0] * N
for e in me.edges:
    val[e.vertices[0]] += 1
    val[e.vertices[1]] += 1

CORE_HALF = 0.012 * 0.5        # half of the +-12 mm CMC window
rows = []
for i, k in enumerate(val):
    if k == 4:
        continue
    p = CO[i]
    ax = (p - ANCHOR).dot(AXIS)
    g = gd[i]
    in_cmc_band = abs(ax) <= 0.012
    # "near the CMC" = within 25 mm of the CMC centre along the metacarpal axis
    if abs(ax) > 0.025:
        continue
    ring = [CO[j] for j, _w in adj[i]]
    if not ring:
        continue
    c = sum(ring, Vector()) / len(ring)
    nrm = (p - c)
    if nrm.length < 1e-9:
        continue
    nrm.normalize()
    a_dor = math.degrees(math.acos(max(-1.0, min(1.0, nrm.dot(DORSAL)))))
    a_pal = math.degrees(math.acos(max(-1.0, min(1.0, nrm.dot(PALMAR)))))
    a_rad = math.degrees(math.acos(max(-1.0, min(1.0, nrm.dot(RADIAL)))))
    rows.append({
        "vertex": i, "valence": k,
        "axial_from_cmc_mm": round(ax * 1000, 2),
        "geod_from_tip_mm": round(g * 1000, 2),
        "in_cmc_deformation_window": bool(in_cmc_band),
        "in_cmc_core": bool(abs(ax) <= CORE_HALF),
        "angle_from_dorsal_deg": round(a_dor, 1),
        "angle_from_palmar_deg": round(a_pal, 1),
        "angle_from_radial_deg": round(a_rad, 1),
        "on_flexion_midline": bool(min(a_dor, a_pal) <= 45.0),
        "on_opposition_path": bool(a_pal <= 62.0 and a_rad <= 75.0),
        "world": [round(float(x), 6) for x in p],
    })

out = {
    "stage": "STAGE4A_CMC_LOCALITY_REFINEMENT_R1",
    "cmc_rotation_center": [round(float(x), 6) for x in CMC],
    "first_metacarpal_axis": [round(float(x), 6) for x in AXIS],
    "criteria": {
        "CMC_CORE": "|axial offset from the CMC centre| <= 6 mm (half of the +-12 mm window)",
        "CMC_FLEXION_MIDLINE": "outward normal within 45 deg of the dorsal or palmar crest",
        "CMC_OPPOSITION_PATH": "outward normal within 62 deg of palmar AND 75 deg of radial "
                              "(the thenar surface loaded during opposition)",
    },
    "region": "thumb poles within 25 mm of the CMC centre along the metacarpal axis",
    "poles_near_cmc": len(rows),
    "CMC_CORE_POLES": [r for r in rows if r["in_cmc_core"]],
    "CMC_FLEXION_MIDLINE_POLES": [r for r in rows if r["on_flexion_midline"]],
    "CMC_OPPOSITION_PATH_POLES": [r for r in rows if r["on_opposition_path"]],
    "rows": rows,
}
json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("=" * 74)
print("poles near the CMC: %d" % len(rows))
print("CMC_CORE_POLES            : %d" % len(out["CMC_CORE_POLES"]))
print("CMC_FLEXION_MIDLINE_POLES : %d" % len(out["CMC_FLEXION_MIDLINE_POLES"]))
print("CMC_OPPOSITION_PATH_POLES : %d" % len(out["CMC_OPPOSITION_PATH_POLES"]))
for r in rows:
    print("  v%-5d val=%d axial=%7.2f  a_dor=%5.1f a_pal=%5.1f a_rad=%5.1f  core=%s midline=%s opposition=%s"
          % (r["vertex"], r["valence"], r["axial_from_cmc_mm"], r["angle_from_dorsal_deg"],
             r["angle_from_palmar_deg"], r["angle_from_radial_deg"], r["in_cmc_core"],
             r["on_flexion_midline"], r["on_opposition_path"]))
print("WROTE", OUT_JSON)
