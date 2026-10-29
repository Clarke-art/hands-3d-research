# STAGE5A_R2A -- dump world-space mesh (read-only) for frame comparison
import bpy, sys, json, hashlib
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
ob = bpy.data.objects["Hand  - Realistic"]
blend = bpy.data.filepath
sha = hashlib.sha256(open(blend, "rb").read()).hexdigest()
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]
L = [tuple(v.co) for v in ob.data.vertices]
json.dump({"blend": blend, "sha256": sha,
           "object_location": list(MW.translation),
           "matrix_world": [[float(x) for x in r] for r in MW],
           "n": len(W),
           "world": [[float(x) for x in p] for p in W],
           "local": [[float(x) for x in p] for p in L],
           "polys": [list(p.vertices) for p in ob.data.polygons]},
          open(OUT, "w"), )
print("[DUMP]", OUT, len(W))
