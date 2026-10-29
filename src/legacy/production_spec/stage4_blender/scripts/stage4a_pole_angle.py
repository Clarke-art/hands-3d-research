# STAGE4A -- angular position of the poles that fall inside a joint bending CORE.
#
# A pole only pinches a bending joint if it lies on the FLEXION MIDLINE (dorsal or
# palmar crest).  Lateral poles are bent around, not through.  Fingers in this relaxed
# hand are only mildly curled, so the global anatomical DORSAL axis is a usable proxy
# for the local dorsal direction (stated as a limitation in the report).
#
# usage: blender -b RIGHT_HAND_ENGINEERING_STAGE4A.blend --python stage4a_pole_angle.py -- <raw.json> <out.json>
import bpy, sys, json, math, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
RAW, OUT = argv[0], argv[1]
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
me = ob.data
me.calc_loop_triangles()
nbr = [[] for _ in range(len(me.vertices))]
for e in me.edges:
    nbr[e.vertices[0]].append(e.vertices[1])
    nbr[e.vertices[1]].append(e.vertices[0])

raw = json.load(open(RAW, encoding="utf-8"))
DORSAL = Vector(raw["frame_after"]["DORSAL_axis"]).normalized()
PALMAR = -DORSAL

rows = []
for p in raw["pole_audit_after_relocation"]["poles_in_deformation_core"]:
    i = p["vertex"]
    wp = mw @ me.vertices[i].co
    ring = [mw @ me.vertices[j].co for j in nbr[i]]
    if not ring:
        continue
    c = sum(ring, Vector()) / len(ring)
    outward = (wp - c)
    if outward.length < 1e-9:
        continue
    outward.normalize()
    a_dor = math.degrees(math.acos(max(-1.0, min(1.0, outward.dot(DORSAL)))))
    a_pal = math.degrees(math.acos(max(-1.0, min(1.0, outward.dot(PALMAR)))))
    on_midline = min(a_dor, a_pal) <= 45.0
    rows.append({"vertex": i, "digit": p["digit"], "joint": p["in_deformation_zone"],
                 "valence": p["valence"],
                 "angle_from_dorsal_deg": round(a_dor, 2),
                 "angle_from_palmar_deg": round(a_pal, 2),
                 "on_flexion_midline": bool(on_midline),
                 "world": [round(float(x), 6) for x in wp]})

out = {
    "core_pole_count": len(rows),
    "on_flexion_midline_count": sum(1 for r in rows if r["on_flexion_midline"]),
    "midline_criterion_deg": 45.0,
    "proxy_note": "angle measured between the pole's outward 1-ring normal and the global "
                  "anatomical DORSAL/PALMAR axis; fingers are only mildly curled in this "
                  "asset so the global axis is a usable proxy for the local one",
    "rows": rows,
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("=" * 70)
print("core poles:", len(rows), " on flexion midline:", out["on_flexion_midline_count"])
for r in rows:
    print("  v%-5d %-7s %-11s val=%d  a_dor=%6.1f  a_pal=%6.1f  midline=%s"
          % (r["vertex"], r["digit"], r["joint"], r["valence"],
             r["angle_from_dorsal_deg"], r["angle_from_palmar_deg"], r["on_flexion_midline"]))
print("WROTE", OUT)
