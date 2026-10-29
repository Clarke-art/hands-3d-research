# STAGE1C - Pass 12: knuckle-bump test to fix palmar/dorsal side (pose-independent landmark)
import bpy, bmesh
from mathutils import Vector
TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]
mw = ob.matrix_world
bm = bmesh.new(); bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table()
W = [(mw @ v.co).copy() for v in bm.verts]

def profile(x0, x1, z0, z1, n=40, label=""):
    print(f"--- {label} x[{x0},{x1}] ---")
    print("  z      y_min   y_max")
    rows = []
    for i in range(n):
        z = z0 + (z1 - z0) * (i + 0.5) / n
        band = [p for p in W if x0 <= p.x <= x1 and abs(p.z - z) <= (z1 - z0) / n * 0.6]
        if len(band) < 3:
            continue
        ys = [p.y for p in band]
        rows.append((round(z, 4), round(min(ys), 5), round(max(ys), 5)))
        print(f"  {rows[-1][0]:<7} {rows[-1][1]:<8} {rows[-1][2]}")
    return rows

# MIDDLE finger: tip z=0.149 -> MCP z~0.235
profile(1.408, 1.438, 0.150, 0.244, 34, "MIDDLE finger (tip->MCP)")
# RING finger
profile(1.380, 1.406, 0.161, 0.240, 30, "RING finger")
# INDEX finger
profile(1.444, 1.470, 0.165, 0.248, 30, "INDEX finger")
print("PASS12_DONE")
