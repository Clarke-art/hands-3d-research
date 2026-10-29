# RUNTIME_PARITY (5.1.2) - TEST 1/2/3: asset discovery + base geometry stats + multires stats
# Faithful re-implementation of the same measurements used by pass1/pass2 (same fields, same definitions).
# Read-only: never saves the .blend, never writes user config.
import bpy, bmesh, json, os
from mathutils import Vector

OUT = os.environ.get("PARITY_OUT", r"<HANDS_ROOT>\production_spec\runtime_parity\blender_5_1_2\evidence")
TARGET = "Hand  - Realistic"

res = {"runtime": {}, "test1_asset_discovery": {}, "test2_base_geometry": {}, "test3_multires": {}}

res["runtime"] = {
    "blender_version_string": bpy.app.version_string,
    "blender_version_tuple": list(bpy.app.version),
    "build_hash": bpy.app.build_hash.decode() if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash),
    "build_date": bpy.app.build_date.decode() if isinstance(bpy.app.build_date, bytes) else str(bpy.app.build_date),
    "build_branch": bpy.app.build_branch.decode() if isinstance(bpy.app.build_branch, bytes) else str(bpy.app.build_branch),
    "binary_path": bpy.app.binary_path,
    "file_path": bpy.data.filepath,
    "factory_startup": bpy.app.use_userpref_skip if hasattr(bpy.app, "use_userpref_skip") else None,
}

# ---------------- TEST 1 : asset discovery ----------------
ob = bpy.data.objects.get(TARGET)
res["test1_asset_discovery"] = {
    "object_found": ob is not None,
    "exact_name": TARGET,
    "name_len": len(TARGET),
    "double_space_present": "Hand  - Realistic" == TARGET,
}

if ob is None:
    # fallback diagnostics: list candidate names so a failure is never ambiguous
    cands = [o.name for o in bpy.data.objects if "Hand" in o.name or "hand" in o.name]
    res["test1_asset_discovery"]["candidates"] = cands
    with open(os.path.join(OUT, "parity_stats.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("TEST1_FAIL")
    raise SystemExit(1)

res["test1_asset_discovery"].update({
    "type": ob.type,
    "is_asset": ob.asset_data is not None,
    "asset_catalog": (ob.asset_data.catalog_id if ob.asset_data else None),
    "mesh_name": ob.data.name,
    "collections": [c.name for c in ob.users_collection],
})

# ---------------- TEST 2 : base geometry stats ----------------
mw = ob.matrix_world
me = ob.data
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()

verts = len(bm.verts); edges = len(bm.edges); faces = len(bm.faces)
tris = sum(1 for f in bm.faces if len(f.verts) == 3)
quads = sum(1 for f in bm.faces if len(f.verts) == 4)
ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
nonmanifold = sum(1 for e in bm.edges if not e.is_manifold)
boundary = sum(1 for e in bm.edges if e.is_boundary)
loose_v = sum(1 for v in bm.verts if not v.link_edges)
loose_e = sum(1 for e in bm.edges if not e.link_faces)
vol = bm.calc_volume(signed=True)
area = sum(f.calc_area() for f in bm.faces)

corners = [mw @ Vector(c) for c in ob.bound_box]
ws_min = [min(c[i] for c in corners) for i in range(3)]
ws_max = [max(c[i] for c in corners) for i in range(3)]

res["test2_base_geometry"] = {
    "objects": 1,
    "vertices": verts, "edges": edges, "faces": faces,
    "triangles": tris, "quads": quads, "ngons": ngons,
    "non_manifold_edges": nonmanifold,
    "boundary_edges": boundary,
    "loose_verts": loose_v, "loose_edges": loose_e,
    "is_closed_manifold": (boundary == 0 and nonmanifold == 0),
    "uv_layers": len(me.uv_layers),
    "uv_layer_names": [u.name for u in me.uv_layers],
    "materials": len(me.materials),
    "armature": ("present" if any(m.type == 'ARMATURE' for m in ob.modifiers) else "none"),
    "vertex_groups": len(ob.vertex_groups),
    "shape_keys": (len(me.shape_keys.key_blocks) if me.shape_keys else 0),
    "modifiers": [[m.type, m.name] for m in ob.modifiers],
    "scale": [round(v, 6) for v in ob.matrix_world.to_scale()],
    "dimensions_local": [round(v, 6) for v in ob.dimensions],
    "world_bbox_min": [round(v, 6) for v in ws_min],
    "world_bbox_max": [round(v, 6) for v in ws_max],
    "world_bbox_size": [round(ws_max[i] - ws_min[i], 6) for i in range(3)],
    "origin_world": [round(v, 6) for v in mw.translation],
    "signed_volume_m3": round(vol, 9),
    "surface_area_m2": round(area, 6),
}
bm.free()

# ---------------- TEST 3 : multires ----------------
mr = next((m for m in ob.modifiers if m.type == 'MULTIRES'), None)
if mr is None:
    res["test3_multires"] = {"multires_modifier_exists": False}
else:
    info = {"multires_modifier_exists": True, "total_levels": mr.total_levels}
    for attr in ("levels", "render_levels", "sculpt_levels"):
        info[attr] = getattr(mr, attr, "ATTR_MISSING")
    per_level = []
    dg = bpy.context.evaluated_depsgraph_get()
    saved = getattr(mr, "levels", None); saved_r = getattr(mr, "render_levels", None)
    for lvl in range(1, mr.total_levels + 1):
        try:
            mr.levels = lvl
        except Exception as e:
            info["levels_set_error"] = str(e); break
        if hasattr(mr, "render_levels"):
            mr.render_levels = lvl
        bpy.context.view_layer.update()
        ob_eval = ob.evaluated_get(dg)
        me2 = ob_eval.to_mesh()
        per_level.append({"level": lvl, "faces": len(me2.polygons), "verts": len(me2.vertices),
                          "corners": sum(len(p.vertices) for p in me2.polygons)})
        ob_eval.to_mesh_clear()
    if saved is not None:
        mr.levels = saved
    if saved_r is not None and hasattr(mr, "render_levels"):
        mr.render_levels = saved_r
    bpy.context.view_layer.update()
    info["per_level"] = per_level
    res["test3_multires"] = info

with open(os.path.join(OUT, "parity_stats.json"), "w") as f:
    json.dump(res, f, indent=1)
print("PARITY_STATS_WRITTEN")
print(json.dumps(res, indent=1)[:2600])
