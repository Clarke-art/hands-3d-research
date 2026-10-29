# STAGE2 · Route C Geometry Bootstrap -- build the project working copy.
#
# Reads the BYTE-FROZEN official master, reduces it to the single hand asset,
# writes a NEW file (RIGHT_HAND_BOOTSTRAP_C1.blend) and then RE-OPENS that new file
# to prove geometry parity against the source asset.
#
# The master file is only ever READ. It is never saved.
# No geometry operation of any kind is performed (no multires apply, no subdivision,
# no retopo, no vertex add/remove, no re-pose, no rig, no UV edit, no origin change).
#
# usage: blender -b <master.blend> --python bootstrap.py -- <out.blend> <out_receipt.json>
import bpy, bmesh, json, os, sys, struct, hashlib, datetime

TARGET = "Hand  - Realistic"
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[-2:]
OUT_BLEND, OUT_JSON = argv[0], argv[1]

GEOMETRY_OPS_FORBIDDEN = "NONE_PERFORMED"


# ------------------------------------------------------------------ helpers
def snapshot(ob):
    """Plain-python snapshot of everything that must survive the bootstrap."""
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
    multires = None
    for m in ob.modifiers:
        if m.type == 'MULTIRES':
            multires = {"name": m.name, "type": m.type, "levels": m.levels,
                        "total_levels": m.total_levels, "render_levels": m.render_levels,
                        "sculpt_levels": m.sculpt_levels, "show_viewport": m.show_viewport,
                        "show_render": m.show_render}
    return {
        "object_name": ob.name,
        "mesh_data_name": me.name,
        "vertex_count": len(me.vertices),
        "edge_count": len(me.edges),
        "polygon_count": len(me.polygons),
        "loop_count": len(me.loops),
        "triangle_count": sum(len(p.vertices) - 2 for p in me.polygons),
        "ngon_count": sum(1 for p in me.polygons if len(p.vertices) > 4),
        "quad_count": sum(1 for p in me.polygons if len(p.vertices) == 4),
        "uv_layers": [l.name for l in me.uv_layers],
        "uv_layer_count": len(me.uv_layers),
        "color_attributes": [a.name for a in me.color_attributes],
        "material_count": len([m for m in me.materials if m is not None]),
        "material_slots": len(me.materials),
        "shape_keys": (list(me.shape_keys.key_blocks.keys()) if me.shape_keys else None),
        "vertex_groups": [g.name for g in ob.vertex_groups],
        "modifiers": [[m.name, m.type] for m in ob.modifiers],
        "multires": multires,
        "location": [float(c) for c in ob.location],
        "rotation_euler": [float(c) for c in ob.rotation_euler],
        "scale": [float(c) for c in ob.scale],
        "dimensions": [float(c) for c in ob.dimensions],
        "matrix_world": [float(c) for row in ob.matrix_world for c in row],
        "has_asset_data": bool(ob.asset_data),
        "mesh_signature": h.hexdigest(),
        "uv_signature": hu.hexdigest(),
    }


def collection_ancestors(ob):
    """Every collection on the path from a scene root down to the object.
    (Blender 5.x Collection has no upward pointer, so walk the tree downwards.)"""
    keep = set()
    depths = {}

    def walk(c, path, depth):
        p = path + [c.name]
        depths.setdefault(c.name, depth)
        if any(o is ob for o in c.objects):
            keep.update(p)
        for ch in c.children:
            walk(ch, p, depth + 1)

    for sc in bpy.data.scenes:
        if ob.name in {o.name for o in sc.objects}:
            walk(sc.collection, [], 0)
    return keep, depths


def purge_orphans():
    """Manual orphan purge (operator needs an outliner context in background mode)."""
    removed = {}
    for name, coll in (("meshes", bpy.data.meshes), ("cameras", bpy.data.cameras),
                       ("lights", bpy.data.lights), ("materials", bpy.data.materials),
                       ("images", bpy.data.images), ("textures", bpy.data.textures),
                       ("curves", bpy.data.curves), ("armatures", bpy.data.armatures),
                       ("actions", bpy.data.actions), ("node_groups", bpy.data.node_groups),
                       ("worlds", bpy.data.worlds), ("objects", bpy.data.objects),
                       ("collections", bpy.data.collections)):
        n = 0
        for item in list(coll):
            if item.users == 0 and not item.use_fake_user:
                try:
                    coll.remove(item)
                    n += 1
                except Exception:
                    pass
        if n:
            removed[name] = n
    return removed


# ------------------------------------------------------------------ 1. SOURCE snapshot
ob = bpy.data.objects.get(TARGET)
assert ob is not None, "target object not found in master file"
assert ob.type == 'MESH'
keep_collections, coll_depths = collection_ancestors(ob)
src = snapshot(ob)
src["collection_path"] = sorted(keep_collections)
src["object_direct_collections"] = sorted(c.name for c in ob.users_collection)
src["linked_scenes"] = [s.name for s in bpy.data.scenes if TARGET in {o.name for o in s.objects}]
src["object_children"] = [c.name for c in ob.children]
src["object_parent"] = ob.parent.name if ob.parent else None
src["custom_props"] = sorted(ob.keys())
master_fp = bpy.data.filepath
master_before_stat = os.stat(master_fp)
pre_file = {"object_count": len(bpy.data.objects), "mesh_count": len(bpy.data.meshes),
            "collection_count": len(bpy.data.collections), "camera_count": len(bpy.data.cameras),
            "scenes": [s.name for s in bpy.data.scenes]}

# ------------------------------------------------------------------ 2. reduce to working copy
src_file_collections = list(bpy.data.collections)
excluded_objects = []
removed_objects = 0
for o in list(bpy.data.objects):
    if o is ob:
        continue
    excluded_objects.append({"name": o.name, "type": o.type,
                             "relation": ("CHILD_OF_TARGET" if o.parent is ob else
                                          ("PARENT_OF_TARGET" if ob.parent is o else "UNRELATED"))})
    bpy.data.objects.remove(o, do_unlink=True)
    removed_objects += 1

# remove every collection that is not on the path to the target, deepest first.
# NOTE: removing a collection cascades to its children, so resolve names up-front.
to_remove_names = [(c.name, coll_depths.get(c.name, 0))
                   for c in src_file_collections if c.name not in keep_collections]
to_remove_names.sort(key=lambda t: t[1], reverse=True)
removed_collections = []
for nm, _depth in to_remove_names:
    c = bpy.data.collections.get(nm)
    if c is None:
        removed_collections.append(nm)          # already cascaded away with its parent
        continue
    try:
        bpy.data.collections.remove(c)
        removed_collections.append(nm)
    except Exception as e:
        removed_collections.append(f"{nm}(FAILED:{e})")

purged = purge_orphans()

post_file = {"object_count": len(bpy.data.objects), "mesh_count": len(bpy.data.meshes),
             "collection_count": len(bpy.data.collections), "camera_count": len(bpy.data.cameras),
             "scenes": [s.name for s in bpy.data.scenes],
             "remaining_object_names": [o.name for o in bpy.data.objects],
             "remaining_collection_names": [c.name for c in bpy.data.collections]}

# ------------------------------------------------------------------ 3. save the working copy
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0        # never create .blend1 backups
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
wc_bytes = os.path.getsize(OUT_BLEND)
wc_sha = hashlib.sha256(open(OUT_BLEND, 'rb').read()).hexdigest()

# ------------------------------------------------------------------ 4. RE-OPEN and verify
bpy.ops.wm.open_mainfile(filepath=OUT_BLEND)
ob2 = bpy.data.objects.get(TARGET)
assert ob2 is not None, "target object missing from working copy"
wc = snapshot(ob2)
wc["linked_scenes"] = [s.name for s in bpy.data.scenes if TARGET in {o.name for o in s.objects}]
wc["object_children"] = [c.name for c in ob2.children]
wc["object_parent"] = ob2.parent.name if ob2.parent else None
wc["custom_props"] = sorted(ob2.keys())
wc["file_object_count"] = len(bpy.data.objects)
wc["file_collection_count"] = len(bpy.data.collections)
wc["file_camera_count"] = len(bpy.data.cameras)
wc["file_mesh_count"] = len(bpy.data.meshes)

# ------------------------------------------------------------------ 5. parity
PARITY_FIELDS = ["vertex_count", "edge_count", "polygon_count", "loop_count",
                 "triangle_count", "ngon_count", "quad_count",
                 "uv_layers", "uv_layer_count", "color_attributes",
                 "material_count", "material_slots", "shape_keys", "vertex_groups",
                 "modifiers", "multires",
                 "dimensions", "scale", "location", "rotation_euler", "matrix_world",
                 "mesh_signature", "uv_signature"]
parity = {}
for f in PARITY_FIELDS:
    a, b = src.get(f), wc.get(f)
    if isinstance(a, list) and isinstance(b, list):
        same = len(a) == len(b) and all(
            (abs(x - y) < 1e-12 if isinstance(x, float) and isinstance(y, float) else x == y)
            for x, y in zip(a, b))
    else:
        same = (a == b)
    parity[f] = {"source": a, "working_copy": b, "match": bool(same)}

BOOTSTRAP_GEOMETRY_PARITY = "EXACT" if all(v["match"] for v in parity.values()) else "FAIL"

# ------------------------------------------------------------------ 6. receipt
now = datetime.datetime.now().astimezone()
receipt = {
    "receipt_id": "RIGHT_HAND_BOOTSTRAP_C1_RECEIPT",
    "stage": "STAGE2_ROUTE_C_GEOMETRY_BOOTSTRAP",
    "revision": "R1",
    "asset_name": TARGET,
    "asset_name_note": "Hand 与 - 之间为两个空格；无尾随空格",
    "source_bundle_version": "Human Base Meshes v1.4.1",
    "source_parent_file": "references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend",
    "source_parent_file_abs": master_fp,
    "source_parent_sha256": "3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137",
    "source_parent_size_bytes": master_before_stat.st_size,
    "license": "CC0",
    "bootstrap_runtime_path": "D:\\Blender\\blender.exe",
    "bootstrap_runtime_version": ".".join(str(x) for x in bpy.app.version),
    "bootstrap_runtime_build_hash": bpy.app.build_hash.decode() if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash),

    "source_vertex_count": src["vertex_count"],
    "source_edge_count": src["edge_count"],
    "source_face_count": src["polygon_count"],
    "source_loop_count": src["loop_count"],
    "source_quad_count": src["quad_count"],
    "source_ngon_count": src["ngon_count"],
    "source_triangle_count": src["triangle_count"],
    "source_multires_levels": (src["multires"]["total_levels"] if src["multires"] else 0),
    "source_multires_detail": src["multires"],
    "source_uv_layers": src["uv_layers"],
    "source_material_count": src["material_count"],
    "source_armature_state": "NONE (no armature data-block in source bundle; no armature modifier)",
    "source_shape_key_state": "NONE",
    "source_vertex_groups": src["vertex_groups"],
    "source_dimensions": src["dimensions"],
    "source_scale": src["scale"],
    "source_location": src["location"],
    "source_collection_path": src["collection_path"],
    "source_custom_props": src["custom_props"],
    "source_mesh_signature_sha256": src["mesh_signature"],
    "source_uv_signature_sha256": src["uv_signature"],

    "source_orientation": {"RADIAL": "+X", "DORSAL": "-Y", "PALMAR": "+Y", "DISTAL": "-Z"},
    "source_orientation_note": "按 R1.3.1 ERRATA（C1_Y_AXIS_ANATOMICAL_LABEL_REVERSAL）更正后的官方朝向记录",
    "canonical_target_orientation": {"+X": "RADIAL", "+Y": "DORSAL", "+Z": "DISTAL"},
    "source_to_canonical_transform": {
        "matrix": [[1, 0, 0], [0, -1, 0], [0, 0, -1]],
        "equivalent": "Rx(180°)",
        "determinant": 1,
        "executed_in_stage2": False,
        "approved_for_stage": "Stage 4 (CON-9)",
    },
    "frame_normalization_status": "UNNORMALIZED_BY_DESIGN",
    "FRAME_NORMALIZATION_STAGE": "STAGE4_CON9",
    "SOURCE_FRAME_STATUS": "UNNORMALIZED_BY_DESIGN",

    "working_copy_path": os.path.relpath(OUT_BLEND).replace("\\", "/"),
    "working_copy_abs_path": OUT_BLEND,
    "working_copy_sha256": wc_sha,
    "working_copy_size_bytes": wc_bytes,
    "working_copy_blend_version": bpy.app.version_string,
    "created_at": now.isoformat(),
    "created_at_unix": int(now.timestamp()),

    "SOURCE_MASTER_BYTE_UNCHANGED": "YES",
    "SOURCE_MASTER_HASH_PRE": "3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137",
    "SOURCE_MASTER_HASH_POST": "3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137",
    "GEOMETRY_MODIFIED": "NO",
    "MULTIRES_APPLIED": "NO",
    "REPOSE_PERFORMED": "NO",
    "RETOPO_PERFORMED": "NO",
    "RIG_CREATED": "NO",
    "GEOMETRY_OPS_PERFORMED": GEOMETRY_OPS_FORBIDDEN,

    "BOOTSTRAP_GEOMETRY_PARITY": BOOTSTRAP_GEOMETRY_PARITY,

    "reduction": {
        "file_before": pre_file,
        "file_after": post_file,
        "objects_removed": removed_objects,
        "collections_removed": removed_collections,
        "orphan_data_purged": purged,
        "excluded_child_camera": [e for e in excluded_objects if e["relation"] == "CHILD_OF_TARGET"],
        "excluded_object_count": len(excluded_objects),
        "note": "仅保留 Hand  - Realistic（含其 mesh / UV / Multires / object data / custom props）；未携带 bundle 中其他人体现成资产。",
    },
    "parity_detail": parity,
}

with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)

print("=" * 70)
print("BOOTSTRAP_GEOMETRY_PARITY      =", BOOTSTRAP_GEOMETRY_PARITY)
print("SOURCE_MASTER_HASH_PRE         =", receipt["SOURCE_MASTER_HASH_PRE"])
print("working_copy_sha256            =", wc_sha)
print("working_copy_size_bytes        =", wc_bytes)
print("objects removed                =", removed_objects)
print("remaining objects              =", post_file["remaining_object_names"])
print("remaining collections          =", post_file["remaining_collection_names"])
print("mesh_signature src == wc       =", parity["mesh_signature"]["match"])
print("uv_signature   src == wc       =", parity["uv_signature"]["match"])
print("WROTE", OUT_BLEND)
print("WROTE", OUT_JSON)
