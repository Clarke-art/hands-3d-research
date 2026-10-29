# STAGE2 · Route C Geometry Bootstrap -- READ-ONLY structural probe of the master file.
# Determines scene / collection layout and asset metadata so the working copy can be
# reduced to the hand asset without collateral damage.
import bpy, json, sys

TARGET = "Hand  - Realistic"
rep = {"target": TARGET}

ob = bpy.data.objects.get(TARGET)
rep["target_found"] = ob is not None
if ob:
    rep["object"] = {
        "name": ob.name,
        "type": ob.type,
        "parent": ob.parent.name if ob.parent else None,
        "children": [c.name for c in ob.children],
        "location": [round(c, 6) for c in ob.location],
        "rotation_euler": [round(c, 8) for c in ob.rotation_euler],
        "rotation_mode": ob.rotation_mode,
        "scale": [round(c, 8) for c in ob.scale],
        "dimensions": [round(c, 6) for c in ob.dimensions],
        "matrix_world_translation": [round(c, 6) for c in ob.matrix_world.translation],
        "data_name": ob.data.name,
        "data_users": ob.data.users,
        "vertex_count": len(ob.data.vertices),
        "edge_count": len(ob.data.edges),
        "polygon_count": len(ob.data.polygons),
        "loop_count": len(ob.data.loops),
        "uv_layers": [l.name for l in ob.data.uv_layers],
        "color_attributes": [a.name for a in ob.data.color_attributes],
        "materials": [m.name if m else None for m in ob.data.materials],
        "shape_keys": (list(ob.data.shape_keys.key_blocks.keys()) if ob.data.shape_keys else None),
        "modifiers": [(m.name, m.type, getattr(m, 'levels', None), getattr(m, 'total_levels', None),
                       getattr(m, 'render_levels', None)) for m in ob.modifiers],
        "has_asset_data": bool(ob.asset_data),
        "collections_direct": [c.name for c in ob.users_collection],
        "vertex_groups": [g.name for g in ob.vertex_groups],
        "custom_props": {k: str(v)[:60] for k, v in ob.items()} if ob.keys() else {},
    }
    rep["mesh_custom_props"] = {k: str(v)[:60] for k, v in ob.data.items()} if ob.data.keys() else {}
    # is the object linked into more than one scene?
    rep["linked_scenes"] = [s.name for s in bpy.data.scenes if TARGET in {o.name for o in s.objects}]

rep["file"] = {
    "filepath": bpy.data.filepath,
    "scenes": [s.name for s in bpy.data.scenes],
    "object_count": len(bpy.data.objects),
    "mesh_count": len(bpy.data.meshes),
    "collection_count": len(bpy.data.collections),
    "armatures": [a.name for a in bpy.data.armatures],
    "actions": len(bpy.data.actions),
    "worlds": [w.name for w in bpy.data.worlds],
    "images": [i.name for i in bpy.data.images],
    "node_groups": len(bpy.data.node_groups),
    "cameras": [c.name for c in bpy.data.cameras],
    "lights": [l.name for l in bpy.data.lights],
    "movieclips": len(bpy.data.movieclips),
    "sounds": len(bpy.data.sounds),
    "books/volumes": len(bpy.data.volumes) if hasattr(bpy.data, 'volumes') else 'n/a',
}

# collection tree of the scene containing the hand
if ob:
    sc = [s for s in bpy.data.scenes if TARGET in {o.name for o in s.objects}]
    trees = {}
    for s in sc:
        def walk(c, depth=0, out=None):
            out = out if out is not None else []
            out.append({"depth": depth, "name": c.name, "objects": [o.name for o in c.objects],
                        "children": [ch.name for ch in c.children]})
            for ch in c.children:
                walk(ch, depth+1, out)
            return out
        trees[s.name] = walk(s.collection)
    rep["collection_trees"] = trees
    # how many collections are empty of objects (directly)
    rep["empty_collections"] = [c.name for c in bpy.data.collections if not c.objects and not c.children]

rep["PASS"] = "STAGE2_STRUCTURE_PROBE_DONE"
out = sys.argv[-1]
with open(out, 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print("WROTE", out)
