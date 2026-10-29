"""Save only the selected design clone, clean reopen, matched static/pose smoke."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

G = read(OUT / 'ITERATION_03_GEOMETRY.json')
assert sha(CURRENT) == EXPECTED
source_raw = LINEAGE / 'RAW_SOURCE_GEOMETRY.json'
lineage_path = LINEAGE / 'HISTORICAL_OPERATION_RAM_REPLAY.json'
registration_path = LINEAGE / 'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json'
human_path = S6 / 'stage6a_human_visible_product_qualification_r1/STAGE6A_HUMAN_VISIBLE_PRODUCT_QUALIFICATION_R1_STATUS.json'
human = read(human_path)
assert human['DEFORMATION_FINAL'] == 'HUMAN_PASS_STAGE6A'
matrix_path = S6 / 'stage6b/STAGE6B_CASE_MATRIX.json'
vector_path = S6 / 'stage6b/STAGE6B_OPPOSITION_VECTOR_AUDIT.json'
inputs = [CURRENT, ROOT / G['donor']['path'], source_raw, lineage_path, registration_path, human_path, matrix_path, vector_path]
inputs += [Path(r['path']) for r in human['receipts'].values()]
for r in human['receipts'].values(): assert sha(r['path']) == r['sha256']
hashes_before = {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}
ob, rig = open_asset(CURRENT); before = snapshot()
assert before['coordinates_local_m'] == G['initial_local_m']
for i in G['vertex_ids']: ob.data.vertices[i].co = G['candidate_local_m'][i]
ob.data.update(); bpy.context.view_layer.update(); pre = snapshot()
assert pre['protected'] == before['protected']
assert pre['coordinates_local_m'] == G['candidate_local_m']
assert state_zero(rig)
# Scene-only candidate labels; no metadata changes to any mesh, bone, or rig.
for k, value in {'DESIGN_ONLY': True, 'HUMAN_APPROVAL': 'PENDING', 'PRODUCTION_PROMOTION': 'NO',
                 'SOURCE_SHA256': EXPECTED, 'GEOMETRY_REPAIR': 'LOCAL_THENAR_VOLUME_RESTORATION'}.items():
    bpy.context.scene['PALMAR_THENAR_' + k] = value
if not CANDIDATE.exists():
    bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE), copy=True, compress=False)
ob, rig = open_asset(CANDIDATE); reopened = snapshot()
assert reopened == pre
changed = [i for i, (a, b) in enumerate(zip(before['coordinates_local_m'], reopened['coordinates_local_m'])) if a != b]
assert changed == G['vertex_ids']
assert all(before['coordinates_local_m'][i] == reopened['coordinates_local_m'][i]
           for i in G['protected_dorsal54'] + G['protected_palmar16'] + G['protected_normal69'])
dump('CANDIDATE_SAVE_REOPEN_PROTECTION_R1.json', {
    'status': 'PASS', 'candidate': ref(CANDIDATE), 'current': ref(CURRENT),
    'only_mesh_vertex_positions_differ': True, 'actual_changed_vertex_ids': changed,
    'RESTORATION_VERTEX_COUNT': len(changed), 'protected_payload_exact': True,
    'protected_payload_sha256_before': digest(before['protected']),
    'protected_payload_sha256_after': digest(reopened['protected']),
    'protected_fields': list(before['protected']), 'topology_vertex_ids_UV_materials_unchanged': True,
    'weights_groups_modifiers_bones_joints_rest_roll_unchanged': True,
    'outside_write_set_position_drift': 0, 'dorsal54_position_drift': 0,
    'palmar16_position_drift': 0, 'normal69_position_drift': 0,
    'native_bone_rest_matrices_exact': True,
    'serialization_drift': 0, 'candidate_save_calls': 1, 'production_save_calls': 0,
    'candidate_final_pose': 'ZERO / RSSF', 'candidate_scene_flags': {
        k: bpy.context.scene[k] for k in bpy.context.scene.keys() if k.startswith('PALMAR_THENAR_')},
})

cameras = G['cameras']; records = []; machine_rows = []; resets = []; display = {}
all_static_views = ['HUMAN_PALMAR', 'FULL_PALM', 'THENAR_CLOSE', 'SIDE_VOLUME', 'SILHOUETTE', 'FIRST_WEB_CLOSE']
smoke_views = ['HUMAN_PALMAR', 'THENAR_CLOSE', 'SIDE_VOLUME', 'FULL_PALM']
cases = [{k: c[k] for k in ['case_id', 'cmc_deg', 'mcp_deg', 'ip_deg', 'cmc_quaternion_local']}
         for c in read(matrix_path)['cases'] if c['case_id'] in ['FULL_OPP_L1', 'FULL_OPP_L2', 'FULL_OPP_L3']]
assert len(cases) == 3
axis = Vector(read(vector_path)['CMC_OPPOSITION_UNIT_ROTATION']['coefficients_local_XYZ']).normalized()
for label, path in [('CURRENT', CURRENT), ('CANDIDATE', CANDIDATE)]:
    ob, rig = open_asset(path); original = snapshot()
    V0, F = evaluate(ob, ob.matrix_world); E = [list(e.vertices) for e in ob.data.edges]
    static_safety, A0 = safety_check(V0, F, E)
    static_safety.update(asset=label, case_id='ZERO')
    assert static_safety['automatic_status'] == 'PASS'
    machine_rows.append(static_safety); display[label] = {'ZERO': [list(v) for v in V0]}
    renderer = Renderer(cameras)
    renderer.draw(label, 'ZERO', V0, F, all_static_views + ['DORSAL54_SENTINEL', 'PALMAR16_SENTINEL'])
    for c in cases:
        reset_pose(rig); bpy.context.view_layer.update(); preV, preF = evaluate(ob, ob.matrix_world)
        assert state_zero(rig) and preF == F
        q, mag = rotation_vector_to_quaternion(axis * math.radians(c['cmc_deg']))
        rig.pose.bones['THUMB_CMC_R'].rotation_quaternion = q
        set_local_axis_rotation(rig, 'THUMB_MCP_R', -c['mcp_deg'])
        set_local_axis_rotation(rig, 'THUMB_IP_R', -c['ip_deg'])
        bpy.context.view_layer.update(); V, FP = evaluate(ob, ob.matrix_world)
        assert FP == F
        row, _ = safety_check(V, F, E, A0)
        row.update(asset=label, case_id=c['case_id'], actual_CMC_quaternion=list(q))
        assert row['automatic_status'] == 'PASS'
        machine_rows.append(row); display[label][c['case_id']] = [list(v) for v in V]
        renderer.draw(label, c['case_id'], V, F, smoke_views)
        reset_pose(rig); bpy.context.view_layer.update(); postV, postF = evaluate(ob, ob.matrix_world)
        err = max((a - b).length * MM for a, b in zip(postV, V0))
        assert state_zero(rig) and postF == F and err <= .0001
        resets.append({'asset': label, 'case_id': c['case_id'], 'all21_zero': True, 'post_zero_error_mm': err, 'status': 'PASS'})
    records.extend(renderer.records)
    renderer.dispose()
    assert snapshot() == original

# Ordinary donor references use the same cameras and its unchanged native faces.
bpy.ops.wm.read_factory_settings(use_empty=True)
renderer = Renderer(cameras)
renderer.draw('OFFICIAL_L1', 'NEUTRAL', [Vector(v) for v in G['donor_visual_world_m']],
              [tuple(f) for f in G['donor_faces']], all_static_views)
records.extend(renderer.records)
hashes_after = {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}
assert hashes_before == hashes_after
dump('MATCHED_RENDER_MANIFEST_R1.json', {'renders': records, 'cameras': cameras,
     'source_visual_reference_only': True, 'source_native_neutral_pose_differs_from_RSSF': True,
     'source_display_registration': 'previously verified rigid registration; no new correspondence',
     'same_current_candidate_camera_scale_light_image_size': True,
     'production_saves': 0, 'candidate_save_calls': 1})
dump('MINIMUM_MACHINE_AUTOMATIC_R1.json', {'status': 'PASS', 'rows': machine_rows,
     'NaN_Inf': 0, 'collapsed_faces': 0, 'degenerate_edges': 0,
     'ZERO_RESTORE': 'PASS', 'resets': resets, 'minimum_visual_components': 'PENDING_ORDINARY_SOLID_SCREEN',
     'hidden_crossing_census': False, 'normal_dot_audit': False, '2127_edge_audit': False,
     'full_stage6b_forensic': False, 'weight_solver': False, 'R3': False, 'true_cap': False})
dump('POSE_DEFINITION_AND_PROTECTION_R1.json', {'status': 'PASS', 'case_matrix': ref(matrix_path),
     'opposition_authority': ref(vector_path), 'cases': cases, 'angles_changed': False,
     'source_native_and_candidate_native_unchanged_by_smoke': True,
     'inputs_before': hashes_before, 'inputs_after': hashes_after,
     'Stage6A_closure_receipts_unchanged': True, 'FINAL_POSE': 'ZERO / RSSF',
     'candidate': ref(CANDIDATE), 'candidate_not_promoted': True,
     'WEIGHTS_CHANGED': 'NO', 'RIG_CHANGED': 'NO', 'PRODUCTION_PROMOTION': 'NO',
     'FULL_STAGE6A_RERUN': False, 'Stage6B_final_PASS': False})
dump('FINAL_DISPLAY_COORDINATES_R1.json', {'assets': display, 'faces': G['faces'], 'vertex_ids': changed})
print('CANDIDATE_SAVED_CLEAN_REOPEN_PASS; FULL_OPP_L1_L2_L3_MATCHED_SMOKE_COMPLETE; ZERO_RESTORE_PASS; renders', len(records), flush=True)
