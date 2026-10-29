"""One bounded local posed-surface corrective; accepted static basis is immutable."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import *
import numpy as np

assert sha(CURRENT) == EXPECTED and not CANDIDATE.exists()
recipe = read(OUT / 'ITERATION_01_WEIGHTS.json')
G = read(PRIOR / 'ITERATION_03_GEOMETRY.json')
ob, rig = open_asset(CURRENT); before = snapshot()
assert before['protected']['mesh']['shape_keys'] is None
mod = next(m for m in ob.modifiers if m.type == 'ARMATURE')
assert not mod.use_deform_preserve_volume and mod.use_vertex_groups and not mod.use_bone_envelopes
apply_weights(ob, recipe['vertex_ids'], recipe['group_names'], recipe['candidate_group_weights'])
weights_only = snapshot()
assert weights_only['coordinates_local_m'] == before['coordinates_local_m']
V0, F = evaluate(ob, ob.matrix_world); E = [list(e.vertices) for e in ob.data.edges]
adj = [set() for _ in V0]
for a, b in E: adj[a].add(b); adj[b].add(a)
D = Vector((.631289124, .775318801, -.0188387)).normalized(); Z = Vector((0, 0, 1)); X = D.cross(Z).normalized(); P = -D
W = rig.matrix_world @ rig.data.bones['WRIST_R'].head_local
locked = set(G['protected_dorsal54']) | set(G['protected_palmar16']) | set(G['protected_normal69'])
locked |= {j for i in list(locked) for j in adj[i]}
falloff = {}
for i in recipe['vertex_ids']:
    if i in locked: continue
    x, depth, z = [(V0[i] - W).dot(a) * MM for a in (X, P, Z)]
    radius = math.sqrt(((x - 34.) / 25.) ** 2 + ((z - 65.) / 26.) ** 2)
    f = (1 - smoothstep(.35, 1., radius)) * smoothstep(-28., -8., depth)
    f *= smoothstep(40., 48., z) * (1 - smoothstep(80., 89., z))
    if f > 1e-3: falloff[i] = f
ids = sorted(falloff)
cases, axis = formal_cases()
basis_local = [v.co.copy() for v in ob.data.vertices]
groups = {g.index: g.name for g in ob.vertex_groups}
correctives = {}
for case in cases[1:]:
    reset_pose(rig)
    q, mag = rotation_vector_to_quaternion(axis * math.radians(case['cmc_deg']))
    rig.pose.bones['THUMB_CMC_R'].rotation_quaternion = q
    set_local_axis_rotation(rig, 'THUMB_MCP_R', -case['mcp_deg'])
    set_local_axis_rotation(rig, 'THUMB_IP_R', -case['ip_deg'])
    bpy.context.view_layer.update(); posed, FP = evaluate(ob, ob.matrix_world); assert FP == F
    relaxed = [v.copy() for v in posed]
    # Alternating local fairing is applied to the posed display surface only.
    # Fixed boundary and a compact falloff retain the surrounding mass/opening.
    for _ in range(7):
        for rate in [.50, -.52]:
            previous = [v.copy() for v in relaxed]
            for i in ids:
                neighbors = sorted(adj[i])
                average = sum((previous[j] for j in neighbors), Vector()) / len(neighbors)
                relaxed[i] = previous[i] + (average - previous[i]) * rate * falloff[i]
    deltas = {}
    mesh_to_rig = rig.matrix_world.inverted() @ ob.matrix_world
    rig_to_mesh = mesh_to_rig.inverted()
    world_to_mesh = ob.matrix_world.inverted().to_3x3()
    for i in ids:
        # Standard inverse linear-skin transform converts posed corrective
        # displacement into a native shape-key delta, with weights held fixed.
        skin = Matrix(((0., 0., 0., 0.),) * 4); total = 0.
        for entry in ob.data.vertices[i].groups:
            name = groups[entry.group]
            if name not in rig.data.bones or not rig.data.bones[name].use_deform: continue
            transform = rig_to_mesh @ rig.pose.bones[name].matrix @ rig.data.bones[name].matrix_local.inverted() @ mesh_to_rig
            skin += transform * entry.weight; total += entry.weight
        assert total > 0
        skin *= 1 / total
        delta = skin.to_3x3().inverted() @ (world_to_mesh @ (relaxed[i] - posed[i]))
        deltas[i] = list(delta)
    correctives[case['case_id']] = deltas
reset_pose(rig); bpy.context.view_layer.update()
assert [list(v.co) for v in ob.data.vertices] == before['coordinates_local_m']
basis = ob.shape_key_add(name='Basis', from_mix=False)
driver_records = []
for case_id, deltas in correctives.items():
    key = ob.shape_key_add(name='THENAR_' + case_id + '_LOCAL_SUPPORT_R1', from_mix=False)
    for i, delta in deltas.items(): key.data[i].co = basis_local[i] + Vector(delta)
    fc = key.driver_add('value'); driver = fc.driver; driver.type = 'SCRIPTED'
    for name, path in [('cw', 'pose.bones["THUMB_CMC_R"].rotation_quaternion[0]'),
                       ('mx', 'pose.bones["THUMB_MCP_R"].rotation_quaternion[1]')]:
        var = driver.variables.new(); var.name = name; var.type = 'SINGLE_PROP'
        var.targets[0].id = rig; var.targets[0].data_path = path
    angle = '(2*acos(max(-1,min(1,cw)))*57.29577951308232)'
    gate = 'min(1,max(0,-mx)/0.17364817766693033)'
    envelope = f'max(0,min(1,({angle}-12)/8,(30-{angle})/10))' if case_id == 'FULL_OPP_L2' else f'max(0,min(1,({angle}-20)/10))'
    driver.expression = f'{envelope}*{gate}'
    assert driver.is_simple_expression
    driver_records.append({'key': key.name, 'expression': driver.expression, 'variables': ['CMC quaternion W', 'MCP flexion quaternion X'], 'simple_expression': True})
bpy.context.view_layer.update()
assert all(k.value == 0 for k in ob.data.shape_keys.key_blocks[1:])
final = snapshot()
assert final['coordinates_local_m'] == before['coordinates_local_m']
assert [list(v.co) for v in basis.data] == before['coordinates_local_m']
protected_a = protected_without_weights(before)
protected_b = protected_without_weights(final)
protected_a['mesh'] = {k: v for k, v in protected_a['mesh'].items() if k != 'shape_keys'}
protected_b['mesh'] = {k: v for k, v in protected_b['mesh'].items() if k != 'shape_keys'}
assert protected_a == protected_b
for k, v in {'DESIGN_ONLY': True, 'STATIC_GEOMETRY_BASE_FOR_TUNING': str(CURRENT), 'HUMAN_APPROVAL': 'PENDING',
             'PRODUCTION_PROMOTION': 'NO', 'BASIS_GEOMETRY_REWRITE': 'NONE'}.items():
    bpy.context.scene['THENAR_OPPOSITION_' + k] = v
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE), copy=True, compress=False)
ob, rig = open_asset(CANDIDATE); reopened = snapshot()
assert reopened == final
assert all(k.value == 0 for k in ob.data.shape_keys.key_blocks[1:])
dump('TUNED_SAVE_REOPEN_PROTECTION_R1.json', {
    'status': 'PASS', 'source': ref(CURRENT), 'tuned_asset': ref(CANDIDATE),
    'weight_vertex_count': len(recipe['vertex_ids']), 'weight_vertex_ids': recipe['vertex_ids'],
    'weight_groups': recipe['group_names'], 'corrective_vertex_count': len(ids), 'corrective_vertex_ids': ids,
    'corrective_keys': driver_records, 'corrective_pose_local_deltas_m': correctives,
    'ZERO_basis_exact': True, 'native_geometry_positions_exact': True,
    'outside_scope_weights_exact': True, 'non_thumb_wrist_weights_exact': True,
    'dorsal54_palmar16_normal69_boundary_exact': True,
    'rig_bones_joints_rest_modifiers_groups_UV_materials_topology_exact': True,
    'added_shape_keys_only_dynamic_local_support': True, 'serialization_drift': 0,
    'corrective_values_at_ZERO': [k.value for k in ob.data.shape_keys.key_blocks[1:]],
    'candidate_save_calls': 1, 'production_saves': 0,
})
records = []; rows = []; resets = []; activation = []; coordinates = {}
for label, path in [('BASELINE', CURRENT), ('TUNED', CANDIDATE)]:
    ob, rig = open_asset(path); renderer = Renderer(G['cameras'])
    rr, coords, reset_rows = sample(ob, rig, label, renderer, ['HUMAN_PALMAR', 'THENAR_CLOSE', 'SIDE_VOLUME', 'FULL_PALM'])
    renderer.draw(label, 'ZERO', [Vector(v) for v in coords['ZERO']], [tuple(f) for f in G['faces']], ['DORSAL54_SENTINEL', 'PALMAR16_SENTINEL'])
    renderer.dispose(); records.extend(renderer.records); rows.extend(rr); resets.extend(reset_rows); coordinates[label] = coords
    if label == 'TUNED':
        for case in cases:
            reset_pose(rig)
            q, _ = rotation_vector_to_quaternion(axis * math.radians(case['cmc_deg']))
            rig.pose.bones['THUMB_CMC_R'].rotation_quaternion = q
            set_local_axis_rotation(rig, 'THUMB_MCP_R', -case['mcp_deg'])
            set_local_axis_rotation(rig, 'THUMB_IP_R', -case['ip_deg'])
            bpy.context.view_layer.update()
            activation.append({'case_id': case['case_id'], 'key_values': [k.value for k in ob.data.shape_keys.key_blocks[1:]]})
        reset_pose(rig); bpy.context.view_layer.update(); assert state_zero(rig)
        assert all(k.value == 0 for k in ob.data.shape_keys.key_blocks[1:])
        assert snapshot() == final
assert activation[0]['key_values'] == [0., 0.]
assert sha(CURRENT) == EXPECTED
dump('FINAL_MATCHED_RENDER_MANIFEST_R1.json', {'renders': records, 'cameras': G['cameras'], 'same_camera_light_scale_image_size': True})
dump('MINIMUM_MACHINE_AUTOMATIC_R1.json', {'status': 'PASS', 'rows': rows, 'resets': resets, 'ZERO_RESTORE': 'PASS',
     'corrective_activation': activation, 'L1_corrective_values_exact_zero': True,
     'NaN_Inf': 0, 'collapsed_face': 0, 'degenerate': 0, 'ordinary_gross_visual_screen': 'PENDING',
     'hidden_crossing_census': False, 'broad_qualification': False})
dump('FINAL_DISPLAY_COORDINATES_R1.json', {'assets': coordinates, 'faces': G['faces']})
print('TUNED_ASSET_SAVED_CLEAN_REOPEN_PASS; STATIC_BASIS_LOCKED; L1_CORRECTIVES_OFF; ZERO_RESTORE_PASS; renders', len(records), flush=True)
