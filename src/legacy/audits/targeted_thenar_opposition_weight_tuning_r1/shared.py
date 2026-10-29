import sys
sys.dont_write_bytecode = True
import importlib.util
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PRIOR = ROOT / 'audits/palmar_thenar_source_shape_restoration_r1'
spec = importlib.util.spec_from_file_location('thenar_readonly_shared', PRIOR / 'common.py')
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)
lib.OUT = OUT
lib.CURRENT = PRIOR / 'RIGHT_HAND_STAGE5B_PALMAR_THENAR_RESTORATION_CANDIDATE_R1.blend'
lib.EXPECTED = '950d47f422f5c4b5eb604edefce0d6f4c542a90a395f522c3e9917ad362d12e8'
lib.CANDIDATE = OUT / 'RIGHT_HAND_STAGE5B_PALMAR_THENAR_OPPOSITION_TUNED_CANDIDATE_R1.blend'
lib.PHASE = 'TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1'
for name in ['read', 'sha', 'dump', 'ref', 'digest', 'open_asset', 'smoothstep', 'safety_check', 'Renderer',
             'snapshot', 'reset_pose', 'evaluate', 'state_zero', 'set_local_axis_rotation', 'rotation_vector_to_quaternion',
             'bpy', 'Vector', 'Matrix', 'Quaternion', 'math', 'S6', 'MM', 'CURRENT', 'EXPECTED', 'CANDIDATE', 'PHASE']:
    globals()[name] = getattr(lib, name)

def protected_without_weights(snap):
    return {k: v for k, v in snap['protected'].items() if k != 'weights_exact_including_zero'}

def bind_human_receipt():
    request = Path('<USER_HOME>/.codex/attachments/7db53719-c7b5-4f1e-b22e-8dec554a60d5/已粘贴的文本.txt')
    assert sha(CURRENT) == EXPECTED
    dump('PRIOR_HUMAN_REVIEW_BINDING_R1.json', {
        'authority': 'EXPLICIT_CURRENT_USER_INSTRUCTION', 'request_path': str(request), 'request_sha256': sha(request),
        'reviewed_candidate': ref(CURRENT), 'Q1': 'ACCEPT', 'Q2': 'REJECT', 'Q3': 'YES',
        'Human_note': 'FULL_OPP_L2 / FULL_OPP_L3 在虎口下方 / 大鱼际连接区出现明显硬折角，动态外观不可接受；ZERO 与 FULL_OPP_L1 可接受。',
        'ZERO_SHAPE_PASS': 'YES', 'OPPOSITION_VOLUME_OR_SURFACE_FAIL': 'YES',
        'accepted_scope': ['ZERO_STATIC_GEOMETRY', 'PRIOR_FULL_OPP_L1_VISIBLE_APPEARANCE'],
        'rejected_scope': ['PRIOR_FULL_OPP_L2', 'PRIOR_FULL_OPP_L3'],
        'current_tuned_candidate_Human_approval': 'PENDING',
        'isolation': 'Independent audit directory / design asset branch; workspace has no .git repository',
        'production_overwrite': False,
    })

def formal_cases():
    path = S6 / 'stage6b/STAGE6B_CASE_MATRIX.json'
    vector = S6 / 'stage6b/STAGE6B_OPPOSITION_VECTOR_AUDIT.json'
    cases = [{k: c[k] for k in ['case_id', 'cmc_deg', 'mcp_deg', 'ip_deg']} for c in read(path)['cases']
             if c['case_id'] in ['FULL_OPP_L1', 'FULL_OPP_L2', 'FULL_OPP_L3']]
    axis = Vector(read(vector)['CMC_OPPOSITION_UNIT_ROTATION']['coefficients_local_XYZ']).normalized()
    return cases, axis

def apply_weights(ob, ids, names, values):
    for i, row in zip(ids, values):
        for name, weight in zip(names, row):
            group = ob.vertex_groups[name]
            if weight > 0:
                group.add([i], float(weight), 'REPLACE')
            elif any(g.group == group.index for g in ob.data.vertices[i].groups):
                group.remove([i])
    bpy.context.view_layer.update()

def sample(ob, rig, label, renderer, views):
    reset_pose(rig); bpy.context.view_layer.update(); V0, F = evaluate(ob, ob.matrix_world)
    E = [list(e.vertices) for e in ob.data.edges]
    safe, A0 = safety_check(V0, F, E); assert safe['automatic_status'] == 'PASS'
    rows = [dict(safe, asset=label, case_id='ZERO')]; coords = {'ZERO': [list(v) for v in V0]}; resets = []
    renderer.draw(label, 'ZERO', V0, F, views)
    cases, axis = formal_cases()
    for c in cases:
        reset_pose(rig); bpy.context.view_layer.update(); assert state_zero(rig)
        q, mag = rotation_vector_to_quaternion(axis * math.radians(c['cmc_deg']))
        rig.pose.bones['THUMB_CMC_R'].rotation_quaternion = q
        set_local_axis_rotation(rig, 'THUMB_MCP_R', -c['mcp_deg'])
        set_local_axis_rotation(rig, 'THUMB_IP_R', -c['ip_deg'])
        bpy.context.view_layer.update(); V, FP = evaluate(ob, ob.matrix_world); assert FP == F
        row, _ = safety_check(V, F, E, A0); assert row['automatic_status'] == 'PASS'
        rows.append(dict(row, asset=label, case_id=c['case_id'])); coords[c['case_id']] = [list(v) for v in V]
        renderer.draw(label, c['case_id'], V, F, views)
        reset_pose(rig); bpy.context.view_layer.update(); Vr, Fr = evaluate(ob, ob.matrix_world)
        error = max((a - b).length * MM for a, b in zip(Vr, V0))
        assert error <= .0001 and Fr == F and state_zero(rig)
        resets.append({'asset': label, 'case_id': c['case_id'], 'post_zero_error_mm': error, 'all21_zero': True, 'status': 'PASS'})
    return rows, coords, resets
