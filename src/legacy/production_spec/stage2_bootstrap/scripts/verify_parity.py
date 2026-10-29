# STAGE2 -- INDEPENDENT parity verification.
# Runs in a FRESH Blender process, opens ONLY the working copy from disk, recomputes the
# signatures and compares them against the values recorded in BOOTSTRAP_RECEIPT.json.
# usage: blender -b <working_copy.blend> --python verify_parity.py -- <receipt.json>
import bpy, json, sys, struct, hashlib

TARGET = "Hand  - Realistic"
receipt_path = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else sys.argv[-1]
rec = json.load(open(receipt_path, encoding='utf-8'))

ob = bpy.data.objects.get(TARGET)
res = {"target_found": ob is not None}
if ob:
    me = ob.data
    h = hashlib.sha256()
    for v in me.vertices:
        h.update(struct.pack('<3d', v.co[0], v.co[1], v.co[2]))
    for e in me.edges:
        h.update(struct.pack('<2i', e.vertices[0], e.vertices[1]))
    for p in me.polygons:
        h.update(struct.pack('<i', len(p.vertices)))
        for vi in p.vertices:
            h.update(struct.pack('<i', vi))
    for l in me.loops:
        h.update(struct.pack('<2i', l.vertex_index, l.edge_index))
    hu = hashlib.sha256()
    for layer in me.uv_layers:
        hu.update(layer.name.encode())
        for d in layer.data:
            hu.update(struct.pack('<2d', d.uv[0], d.uv[1]))
    mr = next((m for m in ob.modifiers if m.type == 'MULTIRES'), None)
    res.update({
        "vertex_count": len(me.vertices), "edge_count": len(me.edges),
        "polygon_count": len(me.polygons), "loop_count": len(me.loops),
        "ngon_count": sum(1 for p in me.polygons if len(p.vertices) > 4),
        "quad_count": sum(1 for p in me.polygons if len(p.vertices) == 4),
        "uv_layers": [l.name for l in me.uv_layers],
        "material_count": len([m for m in me.materials if m is not None]),
        "shape_keys": (list(me.shape_keys.key_blocks.keys()) if me.shape_keys else None),
        "modifiers": [[m.name, m.type] for m in ob.modifiers],
        "multires_levels": (mr.total_levels if mr else 0),
        "scale": [float(c) for c in ob.scale],
        "dimensions": [float(c) for c in ob.dimensions],
        "mesh_signature": h.hexdigest(),
        "uv_signature": hu.hexdigest(),
        "file_object_count": len(bpy.data.objects),
        "file_collection_count": len(bpy.data.collections),
        "file_mesh_count": len(bpy.data.meshes),
        "file_camera_count": len(bpy.data.cameras),
        "object_names": [o.name for o in bpy.data.objects],
    })

CHECKS = [
    ("vertex_count", rec["source_vertex_count"]),
    ("edge_count", rec["source_edge_count"]),
    ("polygon_count", rec["source_face_count"]),
    ("loop_count", rec["source_loop_count"]),
    ("ngon_count", rec["source_ngon_count"]),
    ("quad_count", rec["source_quad_count"]),
    ("uv_layers", rec["source_uv_layers"]),
    ("material_count", rec["source_material_count"]),
    ("shape_keys", None),
    ("multires_levels", rec["source_multires_levels"]),
    ("mesh_signature", rec["source_mesh_signature_sha256"]),
    ("uv_signature", rec["source_uv_signature_sha256"]),
]
print("=" * 70)
allok = True
for field, expected in CHECKS:
    got = res.get(field)
    ok = (got == expected)
    allok = allok and ok
    print(f"  {field:<16} expected={expected!s:<66} got={got!s:<66} {'OK' if ok else 'MISMATCH'}")
print("-" * 70)
print("  file_object_count   =", res["file_object_count"], "->", res["object_names"])
print("  file_mesh_count     =", res["file_mesh_count"])
print("  file_camera_count   =", res["file_camera_count"])
print("  file_collection_count =", res["file_collection_count"])
print("=" * 70)
print("INDEPENDENT_BOOTSTRAP_VERIFICATION =", "PASS" if allok else "FAIL")
res["INDEPENDENT_BOOTSTRAP_VERIFICATION"] = "PASS" if allok else "FAIL"
out = receipt_path.replace("BOOTSTRAP_RECEIPT.json", "BOOTSTRAP_VERIFICATION_INDEPENDENT.json")
json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("WROTE", out)
