"""Read-only visual differential: official L1, current ZERO, historical FULL_OPP_L1.

Only unsaved display meshes receive shading/material settings. No blend saves.
"""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion, Vector

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
S6 = ROOT / 'production_spec/stage6_deformation'
DONOR = ROOT / 'audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1'
STATIC = ROOT / 'audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1'
CURRENT = ROOT / 'production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'
EXPECTED = '90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa'
MM = 1000.

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def dump(n, x):
    (OUT / n).write_text(json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def ref(p):
    return {'path': Path(p).relative_to(ROOT).as_posix(), 'sha256': sha(p)}

def reuse(path, names):
    nodes = [n for n in ast.parse(path.read_text(encoding='utf-8-sig')).body
             if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), globals())
    return {'source': ref(path), 'functions': names, 'top_level_executed': False}

helpers = [reuse(S6 / 'stage6a/scripts/s6a_common.py', ['reset_pose', 'evaluate', 'face_area']),
           reuse(S6 / 'stage6b/scripts/s6b_common.py', ['set_local_axis_rotation', 'rotation_vector_to_quaternion']),
           reuse(S6 / 'palmar_root_targeted_visual_deformation_r1/run_and_render.py', ['native_payload', 'state_zero'])]
raw_path = DONOR / 'RAW_SOURCE_GEOMETRY.json'
registration_path = DONOR / 'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json'
display_path = STATIC / 'MATCHED_REVIEW_GEOMETRY_R1.json'
matrix_path = S6 / 'stage6b/STAGE6B_CASE_MATRIX.json'
vector_path = S6 / 'stage6b/STAGE6B_OPPOSITION_VECTOR_AUDIT.json'
camera_path = S6 / 'stage6b_opposition_requalification_r1/RENDER_MANIFEST_R1.json'
floor_path = S6 / 'whole_hand_surface_integrity_baseline_r1/MINIMUM_MACHINE_SAFETY_R1.json'
inputs = [CURRENT, raw_path, registration_path, display_path, matrix_path, vector_path, camera_path, floor_path]
raw = read(raw_path)['stages']['OFFICIAL_L1']
OFFICIAL = ROOT / raw['input']['path']
inputs.append(OFFICIAL)
before_hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}
assert sha(CURRENT) == EXPECTED and sha(OFFICIAL) == raw['input']['sha256']
frozen = read(display_path)
reg = read(registration_path)['rigid_display_registration']
assert reg['scale'] == 1
case = next(c for c in read(matrix_path)['cases'] if c['case_id'] == 'FULL_OPP_L1')
case = {k: case[k] for k in ['case_id', 'cmc_deg', 'mcp_deg', 'ip_deg', 'cmc_quaternion_local']}
assert [case[k] for k in ['cmc_deg', 'mcp_deg', 'ip_deg']] == [10., 10., 5.]
axis = Vector(read(vector_path)['CMC_OPPOSITION_UNIT_ROTATION']['coefficients_local_XYZ']).normalized()
floor = read(floor_path)['thresholds']

# Fresh read-back of the actual official stored L1; no source modifier setter.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(OFFICIAL), load_ui=False, use_scripts=False)
source_ob = bpy.data.objects['Hand  - Realistic']
multires = next(m for m in source_ob.modifiers if m.type == 'MULTIRES')
assert multires.levels == 1 and multires.show_viewport
eo = source_ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
em = eo.to_mesh()
source_local = [list(v.co) for v in em.vertices]
source_faces = [list(p.vertices) for p in em.polygons]
assert source_local == raw['local_m'] and source_faces == raw['faces']
source_edges = [list(e.vertices) for e in em.edges]
canonical = [source_ob.matrix_world @ (Matrix.Diagonal((1., -1., -1.)) @ v.co) for v in em.vertices]
# The previously verified row-vector rigid transform is transposed for mathutils.
rotation = Matrix(reg['rotation_row']).transposed()
translation = Vector(reg['translation_mm']) / MM
source_V = [rotation @ v + translation for v in canonical]
saved_source = frozen['states']['SOURCE_PRE_ENGINEERING_L1']['vertices']
source_display_error = max((v - Vector(p) / MM).length for v, p in zip(source_V, saved_source))
assert len(source_V) == len(saved_source) == 3300 and source_display_error < 1e-6
eo.to_mesh_clear()
mapped = frozen['states']['OFFICIAL_L1_RSSF_DISPLAY']
assert mapped['faces'] == source_faces
mapped_V = [Vector(p) / MM for p in mapped['vertices']]
source_records = {
    'SOURCE': {'V': source_V, 'F': [tuple(f) for f in source_faces], 'E': source_edges,
               'label': 'OFFICIAL L1 / Stage2 — native neutral; frozen rigid registration'},
    'SOURCE_RSSF_DISPLAY': {'V': mapped_V, 'F': [tuple(f) for f in mapped['faces']], 'E': source_edges,
                          'label': 'OFFICIAL L1 — inherited frozen RSSF display mapping; visual control only'},
}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(CURRENT), load_ui=False, use_scripts=False)
ob = next(o for o in bpy.data.objects if o.type == 'MESH' and len(o.data.vertices) == 3416)
rig = bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
MW = ob.matrix_world.copy()
original = native_payload(ob, rig)
reset_pose(rig)
bpy.context.view_layer.update()
VB, F = evaluate(ob, MW)
assert state_zero(rig)
E = [list(e.vertices) for e in ob.data.edges]
raw_zero_error = max((v - MW @ p.co).length * MM for v, p in zip(VB, ob.data.vertices))
assert raw_zero_error <= floor['zero_mm']

# Recover the exact historical FULL_OPP_L1 thumb/palmar camera, including center.
historical = next(r for r in read(camera_path)['renders']
                  if r['case_id'] == 'FULL_OPP_L1' and r['view'] == 'THUMB_PALMAR_OBLIQUE_SOLID')
human_camera = historical['camera']
D = Vector((.631289124, .775318801, -.0188387)).normalized()
Z = Vector((0, 0, 1))
radial = Z.cross(D).normalized()
thumb = rig.matrix_world @ rig.data.bones['THUMB_MCP_R'].head_local
little = rig.matrix_world @ rig.data.bones['LITTLE_MCP_R'].head_local
if (thumb - little).dot(radial) < 0:
    radial = -radial

def union_frame(points, direction, resolution, padding):
    d = Vector(direction).normalized()
    r = Z.cross(d).normalized()
    u = d.cross(r).normalized()
    xs, ys, zs = [[v.dot(a) for v in points] for a in (r, u, d)]
    center = r * ((min(xs) + max(xs)) / 2) + u * ((min(ys) + max(ys)) / 2) + d * ((min(zs) + max(zs)) / 2)
    aspect = resolution[0] / resolution[1]
    scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * aspect) / min(1., aspect) * padding
    return {'center': list(center), 'direction': list(d), 'ortho_scale_m': scale, 'resolution': resolution}

cameras = {
    'HUMAN_MATCHED_PALMAR_OBLIQUE': human_camera,
    'PALMAR_VOLUME_SILHOUETTE': human_camera,
    'FULL_PALM': union_frame(source_V + VB + mapped_V, -D, [1200, 1400], 1.12),
    'VOLUME_SIDE_OBLIQUE': {'center': human_camera['center'],
                          'direction': list((-D * .63 + radial * .68 + Z * .12).normalized()),
                          'ortho_scale_m': human_camera['ortho_scale_m'], 'resolution': [1200, 1000]},
}
sc = bpy.data.scenes.new('UNSAVED_VISUAL_COMPARISON_ONLY')
sc.render.engine = 'BLENDER_WORKBENCH'
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.world = bpy.data.worlds.new('UNSAVED_NEUTRAL_WORLD')
sc.world.color = (.15, .17, .20)
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
sh = sc.display.shading
sh.color_type = 'MATERIAL'
sh.background_type = 'WORLD'
sh.show_cavity = False
sh.studiolight_rotate_z = .25
cd = bpy.data.cameras.new('UNSAVED_MATCHED_CAMERA')
cd.type = 'ORTHO'
cd.clip_start, cd.clip_end = .001, 5
cam = bpy.data.objects.new('UNSAVED_MATCHED_CAMERA', cd)
sc.collection.objects.link(cam)
sc.camera = cam
clay = bpy.data.materials.new('UNSAVED_NEUTRAL_CLAY')
clay.diffuse_color = (.66, .68, .71, 1)
silhouette = bpy.data.materials.new('UNSAVED_WHITE_SILHOUETTE')
silhouette.diffuse_color = (.96, .96, .96, 1)
(OUT / 'renders').mkdir(exist_ok=True)
manifest, checks = [], []
active = None

def minimum_check(label, V, P, edges, baseline=None):
    areas = [face_area(V, p) for p in P]
    finite = sum(not math.isfinite(float(x)) for v in V for x in v)
    collapse = sum(a <= floor['collapse_area_m2_le'] or
                   (baseline is not None and a / baseline[i] <= floor['collapse_ratio_le'])
                   for i, a in enumerate(areas))
    degenerate = sum((V[a] - V[b]).length <= floor['degenerate_edge_m_le'] for a, b in edges)
    row = {'state': label, 'NaN_Inf': finite, 'collapsed_faces': collapse,
           'degenerate_edges': degenerate, 'status': 'PASS' if finite == collapse == degenerate == 0 else 'FAIL'}
    checks.append(row)
    assert row['status'] == 'PASS'
    return areas

def draw(label, V, P):
    global active
    if active:
        data = active.data
        bpy.data.objects.remove(active, do_unlink=True)
        bpy.data.meshes.remove(data)
    me = bpy.data.meshes.new('UNSAVED_EVALUATED_DISPLAY_ONLY')
    me.from_pydata(V, [], P)
    me.materials.append(clay)
    me.materials.append(silhouette)
    for p in me.polygons:
        p.use_smooth = True
    me.update()
    assert [tuple(p.vertices) for p in me.polygons] == P
    active = bpy.data.objects.new('UNSAVED_EVALUATED_DISPLAY_ONLY', me)
    sc.collection.objects.link(active)
    for view, job in cameras.items():
        sil = view == 'PALMAR_VOLUME_SILHOUETTE'
        sh.light = 'FLAT' if sil else 'STUDIO'
        sh.show_shadows = not sil
        sh.show_specular_highlight = not sil
        sc.world.color = (.025, .030, .040) if sil else (.15, .17, .20)
        for p in me.polygons:
            p.material_index = 1 if sil else 0
        center, direction = Vector(job['center']), Vector(job['direction'])
        cam.location = center + direction * .7
        cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cd.ortho_scale = job['ortho_scale_m']
        sc.render.resolution_x, sc.render.resolution_y = job['resolution']
        name = f'{label}__{view}.png'
        sc.render.filepath = str(OUT / 'renders' / name)
        bpy.ops.render.render(write_still=True, scene=sc.name)
        manifest.append({'state': label, 'view': view, 'path': 'renders/' + name,
                         'camera': job, 'same_camera_all_columns': True,
                         'all_native_faces_present': True, 'smooth_display_copy_only': True,
                         'neutral_material': True, 'cavity': False,
                         'style': 'WHITE_FLAT_SILHOUETTE' if sil else 'NEUTRAL_STUDIO_SOLID',
                         'source_reference_only': label.startswith('SOURCE')})
        dump('RENDER_MANIFEST_R1.json', {'renders': manifest, 'cameras': cameras,
                                       'historical_human_camera': ref(camera_path),
                                       'exact_historical_FULL_OPP_L1_palmar_camera_recovered': True,
                                       'human_target_camera_identification': 'Most recent formal FULL_OPP_L1 palmar oblique; no separate Human camera transform supplied',
                                       'source_registration': 'SOURCE_VISUAL_REFERENCE_ONLY / VISUALLY_MATCHED_REGISTRATION',
                                       'production_saves': 0})
        print('RENDER', label, view, flush=True)

for label, record in source_records.items():
    minimum_check(label, record['V'], record['F'], record['E'])
    draw(label, record['V'], record['F'])
A0 = minimum_check('ZERO', VB, F, E)
draw('ZERO', VB, F)

# Only historical FULL_OPP_L1, applied once; all renders precede final RESET ZERO.
reset_pose(rig)
bpy.context.view_layer.update()
pre, pre_faces = evaluate(ob, MW)
pre_error = max((a - b).length * MM for a, b in zip(pre, VB))
assert state_zero(rig) and pre_faces == F and pre_error <= floor['zero_mm']
q, magnitude = rotation_vector_to_quaternion(axis * math.radians(case['cmc_deg']))
rig.pose.bones['THUMB_CMC_R'].rotation_quaternion = q
set_local_axis_rotation(rig, 'THUMB_MCP_R', -case['mcp_deg'])
set_local_axis_rotation(rig, 'THUMB_IP_R', -case['ip_deg'])
bpy.context.view_layer.update()
VP, FP = evaluate(ob, MW)
assert FP == F
active_bones = [b.name for b in rig.pose.bones if abs(b.rotation_quaternion.angle) > 1e-7]
assert set(active_bones) == {'THUMB_CMC_R', 'THUMB_MCP_R', 'THUMB_IP_R'}
minimum_check('FULL_OPP_L1', VP, FP, E, A0)
draw('FULL_OPP_L1', VP, FP)
reset_pose(rig)
bpy.context.view_layer.update()
restored, restored_faces = evaluate(ob, MW)
post_error = max((a - b).length * MM for a, b in zip(restored, VB))
assert state_zero(rig) and restored_faces == F and post_error <= floor['zero_mm']
assert native_payload(ob, rig) == original
after_hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}
assert before_hashes == after_hashes

dump('MINIMUM_MACHINE_SAFETY_R1.json', {'status': 'PASS', 'rows': checks,
     'threshold_source': ref(floor_path),
     'thresholds_used': {k: floor[k] for k in ['collapse_area_m2_le', 'collapse_ratio_le', 'degenerate_edge_m_le', 'zero_mm']},
     'ZERO_RESTORE': 'PASS', 'zero_raw_error_mm': raw_zero_error,
     'pre_zero_error_mm': pre_error, 'post_zero_error_mm': post_error,
     'all_21_channels_zero_at_end': state_zero(rig),
     'hidden_crossing_census': False, 'weight_diagnosis': False,
     'full_stage6b_forensic': False, 'volume_numeric_audit': False})
dump('INPUT_AND_PROTECTION_R1.json', {
    'status': 'PASS', 'inputs_before': before_hashes, 'inputs_after': after_hashes,
    'official_fresh_L1_matches_verified_snapshot': True,
    'source_native_vertex_count': len(source_V), 'source_native_face_count': len(source_faces),
    'source_display_registration_reused': ref(registration_path),
    'source_display_registration_scale': 1,
    'source_registration_reproduction_max_m': source_display_error,
    'source_RSSF_display_mapping_reused': ref(display_path),
    'SOURCE_VISUAL_REFERENCE_ONLY': True, 'exact_source_current_geometric_overlay_claimed': False,
    'source_main_is_native_neutral_rigid_only': True,
    'source_RSSF_display_control_is_not_native_neutral_pose': True,
    'pose_definition': ref(matrix_path), 'opposition_authority': ref(vector_path),
    'historical_case': case, 'actual_CMC_quaternion_local': list(q),
    'historical_vector_normalized_as_prior_execution': list(axis),
    'active_pose_bones': active_bones, 'FULL_OPP_L1_applications': 1,
    'helper_reuse': helpers, 'final_pose': 'ZERO / RSSF',
    'native_payload_unchanged': True, 'GEOMETRY_WRITES': 0, 'WEIGHT_WRITES': 0,
    'RIG_WRITES': 0, 'JOINT_WRITES': 0, 'PRODUCTION_SAVES': 0,
    'PRODUCTION_PROMOTION': 'NO', 'new_correspondence': False,
    'axis_or_vector_search': False, 'R3': False, 'true_cap': False,
})
print('VISUAL_COMPARISON_COMPLETE; 16 renders; ZERO_RESTORE PASS; production unchanged', flush=True)
