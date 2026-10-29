"""Unsaved pose-only diagnostic. Never writes a blend or an Action key."""
import sys, json, math, ast, hashlib
from pathlib import Path
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PREV = ROOT / 'audits/pianovam_retarget_local_axis_mapping_correction_r1'
sys.path.insert(0, str(PREV))
import mapping_core as core
from mapping_core import bpy, Matrix, Vector, Quaternion
m = core.m
m.old.lib.OUT = OUT
SOURCE = PREV / 'RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend'
SOURCE_SHA = 'a5190adc13d39318096490f8fd2c9956d0daff457d25753fa3c216eee2027bbd'
BASE = core.BASE
ACTION = 'PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def dump(n, x): (OUT / n).write_text(json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
ns = {}
node = next(n for n in ast.parse((ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'action_payload')
exec(compile(ast.Module(body=[node], type_ignores=[]), 'readonly_action_payload', 'exec'), ns)
action_payload = ns['action_payload']

assert sha(BASE) == core.BASE_SHA and sha(SOURCE) == SOURCE_SHA
request = Path('<USER_HOME>/.codex/attachments/08be08e7-5510-44e9-b9d3-b6b612b09644/已粘贴的文本.txt')
dump('PRIOR_HUMAN_CONCLUSION_BIND_R1.json', {
    'authority': 'Direct user-authored request', 'request_path': str(request), 'request_sha256': sha(request),
    'previous_phase': 'PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1',
    'Q1_first_web_acceptable': 'NO', 'Q2_fingers_more_natural': 'YES', 'Q3_full_7s': 'REJECT',
    'RETARGET_AXIS_MAPPING_PARTIAL_CAUSE': 'HUMAN_CONFIRMED', 'historical_files_preserved': True})

# Selection made visually from the existing iteration-2 NEW close sheet, before any OFF test.
# Severity refers to residual NEW defects within this selected subset, not old-motion severity.
selection = [(130, 'MOST_SEVERE', '长且尖锐的阶梯状内陷折线，NEW 残余最明显'),
             (76, 'SEVERE', 'NEW 虎口仍有多段内陷边缘与折痕'),
             (205, 'SEVERE', 'NEW 虎口有连续折线，姿态与前两帧不同'),
             (31, 'MODERATE', 'NEW 虎口保留较浅但明确的凹折'),
             (61, 'LOW_DEFECT_CONTROL', '相对平顺；仍有浅折痕，不宣称完全无缺陷')]
prior_rows = {r['frame']: r for r in read(PREV/'DEFECT_FRAME_OLD_VS_CORRECTED_R1.json')['frames']}
rows = []
for f, severity, note in selection:
    r = prior_rows[f]
    rows.append({k: r[k] for k in ['frame', 'frame_domain', 'review_video_frame_zero_based', 'source_frame', 'time_sec', 'review_time_sec']} | {
        'role': 'CONTROL' if f == 61 else 'DEFECT', 'severity': severity, 'visual_note': note,
        'severity_authority': 'Codex preliminary ordinary-solid review of existing corrected NEW frames; Human pending'})
dump('SELECTED_DEFECT_FRAMES_R1.json', {
    'SOURCE_ACTION': ACTION, 'SOURCE_MOTION': 'Same PianoVAM 11.5–18.5 sec / 421 observations',
    'selected_defect_frame_count': 4, 'control_frame_count': 1,
    'selection_evidence': str((PREV/'ITERATION_2_PALMAR_THENAR_CLOSE_SHEET.png').relative_to(ROOT)),
    'new_full_severity_census_run': False, 'frames': rows})

ob, rig = m.open_file(SOURCE)
scene = bpy.context.scene
action = bpy.data.actions[ACTION]
rig.animation_data.action = action
solver = core.Solver(ob, rig, 2)
native = m.product_payload(ob, rig)
shape = core.shape_payload(ob)
materials = [m.material_payload(x) for x in ob.data.materials if x]
actions_before = {a.name: digest(action_payload(a)) for a in bpy.data.actions}
driver_flags = [(f.data_path, f.mute, f.driver.type) for f in ob.data.shape_keys.animation_data.drivers]
protected_files = [BASE, SOURCE, PREV/'mapping_core.py'] + [ROOT/r['path'] for r in read(PREV/'PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_STATUS.json')['source_file_hashes_unchanged']]
files_before = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected_files}
conditions = ['BASELINE', 'INDEX_ABD_OFF', 'INDEX_FLEX_OFF', 'THUMB_CMC_SWING_OFF', 'THUMB_MCP_FLEX_OFF']
if '--combined' in sys.argv:
    gate = read(OUT/'JOINT_COMPONENT_AB_RESULTS_R1.json')
    assert gate['combined_gate']['run_authorized_by_A_C_visual_contribution'], 'E requires inspected A/C contribution'
    conditions = ['COMBINED']

def index_q(flex, abd):
    # Same MCP frame(d, radial) construction as immutable previous Solver.raw.
    d = Vector((math.cos(flex)*math.sin(abd), math.cos(flex)*math.cos(abd), math.sin(flex)))
    S = core.frame(d, (1, 0, 0))
    R = solver.rest['INDEX_MCP_R']
    return (R.transposed() @ solver.anatom['INDEX_MCP_R'] @ S @ solver.calibration['INDEX_MCP_R']).to_quaternion()

def neutral_raw(i, condition):
    raw, comp = solver.raw(i)
    if condition in ['INDEX_ABD_OFF', 'INDEX_FLEX_OFF', 'COMBINED']:
        c = comp['INDEX_MCP_R']
        flex, abd = c['source_flexion_rad'], c['source_abduction_rad']
        q = index_q(flex, abd)
        assert max(abs(a-b) for a,b in zip(q.to_matrix(), raw['INDEX_MCP_R'].to_matrix()) for a,b in zip(a,b)) < 1e-6
        return index_q(0.0 if condition == 'INDEX_FLEX_OFF' else flex,
                       0.0 if condition in ['INDEX_ABD_OFF','COMBINED'] else abd)
    if condition == 'THUMB_MCP_FLEX_OFF':
        return Quaternion(solver.hinges['THUMB_MCP_R'], 0.0)
    if condition == 'THUMB_CMC_SWING_OFF':
        # Full independent CMC stance/swing restored to median calibrated source reference.
        # Same frame anchor and roll calibration; no Euler channel is deleted.
        R = solver.rest['THUMB_CMC_R']
        T = core.frame(solver.thumb_neutral, (0,0,1))
        delta = solver.thumb_src_rest.transposed() @ T
        return (R.transposed() @ solver.thumb_anatom @ delta @ solver.thumb_roll_offset).to_quaternion()
    raise ValueError(condition)

def smooth_override(i, condition):
    seq = [neutral_raw(max(0, i-1), condition), neutral_raw(i, condition), neutral_raw(min(420,i+1), condition)]
    for p in seq:
        if p.dot(seq[1]) < 0: p.negate()
    q = Quaternion([sum(w*p[k] for w,p in zip([.25,.5,.25],seq)) for k in range(4)])
    q.normalize()
    return q

def local_channels():
    return {p.name: {'q': list(p.rotation_quaternion), 'location': list(p.location), 'scale': list(p.scale), 'mode': p.rotation_mode} for p in rig.pose.bones}

def protected():
    assert m.product_payload(ob, rig) == native
    assert core.shape_payload(ob) == shape
    assert [m.material_payload(x) for x in ob.data.materials if x] == materials
    assert [(f.data_path, f.mute, f.driver.type) for f in ob.data.shape_keys.animation_data.drivers] == driver_flags
    assert {a.name: digest(action_payload(a)) for a in bpy.data.actions} == actions_before

values, checks, render_records = [], [], []
for row in rows:
    f, i = row['frame'], row['source_frame']-690
    rig.animation_data.action = action
    scene.frame_set(f)
    bpy.context.view_layer.update()
    before = local_channels()
    baseline_q = {n: rig.pose.bones[n].rotation_quaternion.copy() for n in solver.rest}
    smooth, comp = solver.smoothed(i)
    errors = {n: min(max(abs(a-b) for a,b in zip(smooth[n], baseline_q[n])),max(abs(a+b) for a,b in zip(smooth[n], baseline_q[n]))) for n in smooth}
    assert max(errors.values()) < 1e-6, errors
    Vbase, Fbase = m.evaluate(ob, ob.matrix_world)
    cameras = {v: prior_rows[f]['same_camera'][v] for v in ['PALMAR_THENAR_CLOSE','FIRST_WEB_OBLIQUE']}
    renderer = m.Renderer(cameras, 'renders')
    renderer.sc.display.shading.shadow_intensity = 0
    neighbor_data = []
    for j in [i-1,i,i+1]:
        raw, c = solver.raw(j)
        neighbor_data.append({'source_frame':690+j, 'kernel_weight':[.25,.5,.25][j-i+1],
            'same_source_landmarks_sha256':digest(solver.points[j].tolist()),
            'source_anatomical_components': {n:c[n] for n in ['INDEX_MCP_R','THUMB_CMC_R','THUMB_MCP_R']},
            'raw_bone_local_quaternions': {n:list(raw[n]) for n in ['INDEX_MCP_R','THUMB_CMC_R','THUMB_MCP_R']}})
    for condition in conditions:
        # Detach only runtime Action binding, never edits the Action datablock.
        rig.animation_data.action = None
        for n, q in baseline_q.items(): rig.pose.bones[n].rotation_quaternion = q
        targets = {}
        if condition in ['INDEX_ABD_OFF','INDEX_FLEX_OFF','COMBINED']:
            targets['INDEX_MCP_R'] = smooth_override(i, condition)
        if condition in ['THUMB_CMC_SWING_OFF','COMBINED']:
            targets['THUMB_CMC_R'] = smooth_override(i, 'THUMB_CMC_SWING_OFF')
        if condition == 'THUMB_MCP_FLEX_OFF':
            targets['THUMB_MCP_R'] = smooth_override(i, condition)
        for n, q in targets.items(): rig.pose.bones[n].rotation_quaternion = q
        bpy.context.view_layer.update()
        after = local_channels()
        assert all(after[n] == before[n] for n in before if n not in targets)
        assert all(after[n]['location']==before[n]['location'] and after[n]['scale']==before[n]['scale'] and after[n]['mode']==before[n]['mode'] for n in before)
        assert scene.frame_current == f
        protected()
        V, F = m.evaluate(ob, ob.matrix_world)
        assert F == Fbase
        if condition == 'BASELINE': assert max((a-b).length for a,b in zip(V,Vbase)) == 0
        renderer.draw(condition, f'F{f:03}', V, F, list(cameras))
        neutral = {}
        if 'INDEX_MCP_R' in targets:
            neutral['INDEX_MCP_R'] = {'source_flexion_rad':0.0 if condition=='INDEX_FLEX_OFF' else comp['INDEX_MCP_R']['source_flexion_rad'],
                'source_abduction_rad':0.0 if condition in ['INDEX_ABD_OFF','COMBINED'] else comp['INDEX_MCP_R']['source_abduction_rad']}
        if 'THUMB_CMC_R' in targets:
            neutral['THUMB_CMC_R'] = {'source_CMC_direction':list(solver.thumb_neutral), 'source_swing_quaternion':[1,0,0,0],
                'source_in_palm_swing_rad':0.0,'source_out_of_palm_flexion_rad':math.atan2(solver.thumb_neutral.z,math.hypot(solver.thumb_neutral.x,solver.thumb_neutral.y)),
                'meaning':'Entire independently mapped CMC swing/opposition stance returns to calibrated reference. MCP/IP local bends retained.'}
        if 'THUMB_MCP_R' in targets: neutral['THUMB_MCP_R'] = {'source_signed_hinge_bend_rad':0.0}
        values.append({'frame':f,'source_frame':row['source_frame'],'condition':condition,
            'original_components':{n:comp[n] for n in ['INDEX_MCP_R','THUMB_CMC_R','THUMB_MCP_R']},
            'neutralized_components':neutral,'same_three_source_neighbor_observations':neighbor_data,
            'baseline_smoothed_local_quaternions':{n:list(baseline_q[n]) for n in ['INDEX_MCP_R','THUMB_CMC_R','THUMB_MCP_R']},
            'diagnostic_smoothed_local_quaternions':{n:after[n]['q'] for n in ['INDEX_MCP_R','THUMB_CMC_R','THUMB_MCP_R']},
            'natural_existing_corrective_value':float(ob.data.shape_keys.key_blocks[1].value)})
        checks.append({'frame':f,'source_frame':row['source_frame'],'condition':condition,'same_source_frame_landmarks_mapping_smoothing':True,
            'same_protected_mesh_basis_weights_rest_joint_roll_hierarchy_corrective_driver_materials':True,
            'all_untested_local_channels_exact':True,'changed_local_quaternion_bones':list(targets),'same_camera':cameras,
            'baseline_action_solver_quaternion_max_abs_error':max(errors.values()),
            'existing_driver_runs_naturally':True,'no_actions_edited':True})
        # Reattach source Action and force exact evaluated restore before next test.
        rig.animation_data.action = action
        scene.frame_set(f)
        bpy.context.view_layer.update()
        assert local_channels() == before
        Vr, Fr = m.evaluate(ob,ob.matrix_world)
        assert Fr==Fbase and max((a-b).length for a,b in zip(Vr,Vbase))==0
    render_records.extend(renderer.records)
    renderer.dispose()
    print('FRAME_COMPLETE', f, conditions, flush=True)

protected()
files_after = {p.relative_to(ROOT).as_posix():sha(p) for p in protected_files}
assert files_after == files_before
suffix = '_COMBINED' if '--combined' in sys.argv else ''
dump('JOINT_COMPONENT_VALUES'+suffix+'_R1.json', {'SOURCE_ACTION':ACTION,'frames':values,
    'component_method':'Previous solver raw anatomical components reconstructed with unchanged frame/roll formulas. Neutralization applied at each of the original 3 source-neighbor observations, then EXACT original quaternion kernel. All other local channels copied exactly from saved corrected Action.',
    'neutral_reference':'INDEX source anatomical flexion/abduction=0 maps to calibrated rig rest; THUMB CMC=previous iteration-2 median stance; THUMB MCP hinge=0.',
    'smoothing_note':'The same quaternion smoother is nonlinear: changing one raw anatomical component may change its smoothed bone quaternion in all four coefficients. This is not Euler channel deletion or extra filtering.'})
dump('MACHINE_CHECK'+suffix+'_R1.json', {'status':'PASS','files_before':files_before,'files_after':files_after,
    'actions_before':actions_before,'actions_after':{a.name:digest(action_payload(a)) for a in bpy.data.actions},
    'native_payload_sha256':digest(native),'shape_driver_payload_sha256':digest(shape),'no_blend_saved':True,
    'all_overrides_restored':True,'same_source_observations':421,'same_window_sec':[11.5,18.5],
    'forbidden_stress_audits_run':False,'frames':checks,'render_records':render_records})
print('ISOLATION_COMPLETE',suffix or 'ABCD', 'HASHES_UNCHANGED',flush=True)
