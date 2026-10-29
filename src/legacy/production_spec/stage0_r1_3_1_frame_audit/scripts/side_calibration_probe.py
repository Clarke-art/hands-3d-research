# STAGE0 R1.3.1 -- side-calibration probe.  READ-ONLY, no save, no mesh creation.
# Goal: establish the bundle's own world-space handedness using assets that carry
# explicit .L / .R suffixes, plus the eye .L / .R of the realistic body.
import bpy, json, math, sys
from mathutils import Vector

OUT = sys.argv[-1]

def wverts(ob):
    mw = ob.matrix_world
    return [mw @ v.co for v in ob.data.vertices]

def bbox(V):
    return [round(min(v.x for v in V),4), round(max(v.x for v in V),4),
            round(min(v.y for v in V),4), round(max(v.y for v in V),4),
            round(min(v.z for v in V),4), round(max(v.z for v in V),4)]

rep = {}

# ---- A. eye landmarks of the realistic bodies: tells us which world side is body-LEFT
eyes = {}
for name in bpy.data.objects.keys():
    if name.endswith('.eye.L') or name.endswith('.eye.R') or name.endswith('.iris.L') or name.endswith('.iris.R'):
        ob = bpy.data.objects[name]
        if ob.type != 'MESH':
            continue
        V = wverts(ob)
        if not V:
            continue
        c = sum(V, Vector((0,0,0))) / len(V)
        eyes[name] = [round(c.x,4), round(c.y,4), round(c.z,4)]
rep["eye_landmarks_world"] = eyes

# ---- B. realistic body: overall bbox + extreme limbs
bodies = {}
for name in ['GEO-body_male_realistic','GEO-body_female_realistic']:
    if name not in bpy.data.objects:
        continue
    ob = bpy.data.objects[name]
    V = wverts(ob)
    bb = bbox(V)
    xmax_v = max(V, key=lambda p: p.x)
    xmin_v = min(V, key=lambda p: p.x)
    bodies[name] = {"vcount": len(V), "bbox": bb,
                    "xmax_vertex": [round(c,4) for c in xmax_v],
                    "xmin_vertex": [round(c,4) for c in xmin_v]}
rep["realistic_bodies"] = bodies

# ---- C. primitive assembly hands (.L / .R explicit) -> bundle convention
prim = {}
for name in sorted(bpy.data.objects.keys()):
    if name.startswith('GEO-hand_') and (name.endswith('.L') or name.endswith('.R')):
        ob = bpy.data.objects[name]
        V = wverts(ob)
        if not V:
            continue
        bb = bbox(V)
        cen = sum(V, Vector((0,0,0))) / len(V)
        # "distal" = direction from the forearm end (wrist) to the fingertips.
        # For these blocky primitives the long axis of the digit block is a good proxy:
        # take the vertex farthest from the centroid -> a fingertip.
        far = max(V, key=lambda p: (p - cen).length)
        # lateral deviation: distance from the body-symmetry plane (x = const per side);
        # report raw extents so the geometry can be read directly.
        prim[name] = {"vcount": len(V), "bbox": bb,
                      "centroid": [round(c,4) for c in cen],
                      "farthest_vertex_from_centroid": [round(c,4) for c in far]}
rep["primitive_hands"] = prim

rep["PASS"] = "SIDE_CALIBRATION_DONE"
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print("WROTE", OUT)
