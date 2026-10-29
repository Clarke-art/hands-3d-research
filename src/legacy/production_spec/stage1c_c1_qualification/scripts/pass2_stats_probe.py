# STAGE1C - Pass 2: full geometry stats + orientation probe renders (read-only, in-memory only)
import bpy, bmesh, json, math, sys
from mathutils import Vector

OUT_JSON = r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\stats\asset_geometry_stats_raw.json"
OUT_DIR = r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\renders"

TARGET = "Hand  - Realistic"
ob = bpy.data.objects[TARGET]

report = {"target_object": TARGET}

# ---------- world transform / bbox ----------
mw = ob.matrix_world
report["matrix_world_translation"] = [round(v, 6) for v in mw.translation]
report["matrix_world_scale"] = [round(v, 6) for v in mw.to_scale()]
report["dimensions_local"] = [round(v, 6) for v in ob.dimensions]
corners = [mw @ Vector(c) for c in ob.bound_box]
ws_min = [min(c[i] for c in corners) for i in range(3)]
ws_max = [max(c[i] for c in corners) for i in range(3)]
report["world_bbox_min"] = [round(v, 6) for v in ws_min]
report["world_bbox_max"] = [round(v, 6) for v in ws_max]
report["world_bbox_size"] = [round(ws_max[i] - ws_min[i], 6) for i in range(3)]

# ---------- base mesh stats via bmesh ----------
me = ob.data
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()

verts = len(bm.verts)
edges = len(bm.edges)
faces = len(bm.faces)
tris = sum(1 for f in bm.faces if len(f.verts) == 3)
quads = sum(1 for f in bm.faces if len(f.verts) == 4)
ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
nonmanifold = [e for e in bm.edges if not e.is_manifold]
boundary = [e for e in bm.edges if e.is_boundary]
loose_verts = [v for v in bm.verts if not v.link_edges]
loose_edges = [e for e in bm.edges if not e.link_faces]
# wire edges (manifold-ish but no faces) covered by loose_edges; also interior/face-pole counts
poles5 = sum(1 for v in bm.verts if v.is_manifold and len(v.link_edges) == 5)
poles3 = sum(1 for v in bm.verts if v.is_manifold and len(v.link_edges) == 3)

# volume & area (closed mesh check)
try:
    vol = bm.calc_volume(signed=True)
except Exception:
    vol = None
area = sum(f.calc_area() for f in bm.faces)

# symmetry checks across X / Y / Z planes (world space)
def sym_axis(axis):
    # build KD-ish dict by rounding mirrored coords
    ai = "XYZ".index(axis)
    ok = 0
    bad = 0
    tol = 1e-4
    allv = [mw @ v.co for v in bm.verts]
    from mathutils import kdtree
    kd = kdtree.KDTree(len(allv))
    for i, p in enumerate(allv):
        kd.insert(p, i)
    kd.balance()
    for p in allv:
        q = Vector(p)
        q[ai] = -q[ai]
        hit = kd.find(q)
        if hit is not None and hit[2] <= tol:
            ok += 1
        else:
            bad += 1
    return {"matched": ok, "unmatched": bad, "ratio": round(ok / max(1, verts), 4)}

report["base_mesh"] = {
    "verts": verts, "edges": edges, "faces": faces,
    "triangles": tris, "quads": quads, "ngons": ngons,
    "non_manifold_edges": len(nonmanifold),
    "boundary_edges": len(boundary),
    "loose_verts": len(loose_verts), "loose_edges": len(loose_edges),
    "valence3_poles": poles3, "valence5_poles": poles5,
    "signed_volume_m3": round(vol, 9) if vol is not None else None,
    "surface_area_m2": round(area, 6),
    "uv_layers": len(me.uv_layers),
    "uv_layer_names": [u.name for u in me.uv_layers],
    "materials": len(me.materials),
    "shape_keys": (len(me.shape_keys.key_blocks) if me.shape_keys else 0),
    "modifiers": [(m.type, m.name) for m in ob.modifiers],
    "has_armature_modifier": any(m.type == "ARMATURE" for m in ob.modifiers),
    "face_maps": len(me.face_maps) if hasattr(me, "face_maps") else None,
    "vertex_groups": len(ob.vertex_groups),
    "is_closed_manifold": (len(boundary) == 0 and len(nonmanifold) == 0),
}
report["symmetry"] = {a: sym_axis(a) for a in "XYZ"}

# ---------- multires ----------
for m in ob.modifiers:
    if m.type == "MULTIRES":
        report["multires"] = {
            "total_levels": m.total_levels,
            "render_levels": m.render_levels,
            "viewport_levels": m.levels,
            "sculpt_levels": m.sculpt_levels,
            "use_subsurf_uv": getattr(m, "use_subsurf_uv", None),
        }

# per-level stats by temporarily setting viewport levels (in memory only)
if any(m.type == "MULTIRES" for m in ob.modifiers):
    mr = next(m for m in ob.modifiers if m.type == "MULTIRES")
    per_level = []
    dg = bpy.context.evaluated_depsgraph_get()
    for lvl in range(1, mr.total_levels + 1):
        mr.levels = lvl
        mr.render_levels = lvl
        bpy.context.view_layer.update()
        ob_eval = ob.evaluated_get(dg)
        me2 = ob_eval.to_mesh()
        t = sum(1 for p in me2.polygons)  # faces after multires (all quads->4)
        tr = sum(len(p.vertices) for p in me2.polygons)
        per_level.append({"level": lvl, "faces": t, "verts": len(me2.vertices), "corners": tr})
        ob_eval.to_mesh_clear()
    mr.levels = report["multires"]["viewport_levels"]
    mr.render_levels = report["multires"]["render_levels"]
    bpy.context.view_layer.update()
    report["multires_per_level"] = per_level

# ---------- axial profile for orientation / forearm ----------
allv = [mw @ v.co for v in bm.verts]
zs = [p.z for p in allv]
xs = [p.x for p in allv]
ys = [p.y for p in allv]
report["coord_ranges"] = {
    "x": [round(min(xs), 4), round(max(xs), 4)],
    "y": [round(min(ys), 4), round(max(ys), 4)],
    "z": [round(min(zs), 4), round(max(zs), 4)],
}

# slice profile along Z: count vertices in slabs (proxy for cross-section complexity)
import collections
slabs = {}
n_slabs = 40
zmin, zmax = min(zs), max(zs)
for p in allv:
    idx = min(n_slabs - 1, int((p.z - zmin) / (zmax - zmin) * n_slabs))
    slabs[idx] = slabs.get(idx, 0) + 1
report["vert_count_per_z_slab"] = {str(k): v for k, v in sorted(slabs.items())}

bm.free()

# ---------- render orientation probe (6 orthographic views) ----------
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (0.65, 0.45, 0.85)
scene.display.shading.show_cavity = True
scene.display.shading.background_type = 'WORLD'
scene.display.render_aa = '8'

world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)
    bg.inputs[1].default_value = 1.0

scene.render.resolution_x = 900
scene.render.resolution_y = 1200
scene.render.film_transparent = False

# isolate target for renders: hide all other objects in view layer (in memory only)
for o in bpy.context.view_layer.objects:
    o.hide_render = (o.name != TARGET)

cam_data = bpy.data.cameras.new("probe_cam")
cam_data.type = 'ORTHO'
cam = bpy.data.objects.new("probe_cam", cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam

cx = (ws_min[0] + ws_max[0]) / 2
cy = (ws_min[1] + ws_max[1]) / 2
cz = (ws_min[2] + ws_max[2]) / 2
span = max(ws_max[i] - ws_min[i] for i in range(3)) * 1.35
cam_data.ortho_scale = span

views = {
    "probe_front_negY": (cx, cy - 10, cz, 90, 0, 0),
    "probe_back_posY": (cx, cy + 10, cz, 90, 0, 180),
    "probe_left_negX": (cx - 10, cy, cz, 90, 0, 90),
    "probe_right_posX": (cx + 10, cy, cz, 90, 0, -90),
    "probe_top_posZ": (cx, cy, cz + 10, 0, 0, 0),
    "probe_bot_negZ": (cx, cy, cz - 10, 180, 0, 0),
}
from mathutils import Euler
for name, (px, py, pz, rx, ry, rz) in views.items():
    cam.location = (px, py, pz)
    cam.rotation_euler = Euler((math.radians(rx), math.radians(ry), math.radians(rz)), 'XYZ')
    scene.render.filepath = OUT_DIR + "\\" + name + ".png"
    bpy.ops.render.render(write_still=True)

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("PASS2_DONE")
