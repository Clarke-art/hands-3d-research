"""Product-level Go/No-Go observation harness for RIGHT_HAND_FIRST_WEB_PRODUCT_IMPACT_GO_NO_GO_R1.

Observation only. This harness never writes any .blend and never modifies mesh,
topology, weights, bones, rest pose, corrective, driver, Action or retarget mapping.
It loads the frozen production baseline read-only, appends the already-approved
PianoVAM Action as a library datablock, and renders ordinary solid views.
"""
import sys, json, hashlib, ast, copy
from pathlib import Path
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PREV = ROOT / 'audits/pianovam_retarget_local_axis_mapping_correction_r1'
sys.path.insert(0, str(PREV))
import mapping_core as core
from mapping_core import bpy, np, Vector, Matrix, Quaternion

m = core.m
m.old.lib.OUT = OUT

BASE = ROOT / 'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'
SOURCE = PREV / 'RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend'
ACTION = 'PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1'
PHASE = 'RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1'
FROZEN_SHA = '4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2'
assert core.BASE_SHA == FROZEN_SHA
TOTAL_FRAMES = 210
PATCH_IDS = json.loads((ROOT / 'audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json').read_text())['allowed_vertex_ids']


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def dump(n, x):
    (OUT / n).write_text(json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False, default=lambda v: v.tolist() if hasattr(v, 'tolist') else v.item()) + '\n', encoding='utf-8')


_ns = {}
_node = next(n for n in ast.parse((ROOT / 'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py').read_text()).body
             if isinstance(n, ast.FunctionDef) and n.name == 'action_payload')
exec(compile(ast.Module(body=[_node], type_ignores=[]), 'readonly_action_payload', 'exec'), _ns)
action_payload = _ns['action_payload']

APPROVED_ACTION_SHA = read(ROOT / 'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['actions_before'][ACTION]


def protected_inputs():
    rows = read(ROOT / 'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['files_before']
    out = {}
    for p, h in rows.items():
        out[p] = h
    out['audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json'] = sha(
        ROOT / 'audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json')
    out['audits/first_web_real_motion_deformation_fix_r1/REAL_MOTION_MATCHED_CAMERAS_R1.json'] = sha(
        ROOT / 'audits/first_web_real_motion_deformation_fix_r1/REAL_MOTION_MATCHED_CAMERAS_R1.json')
    return out


def verify_inputs(before):
    for p, h in before.items():
        assert sha(ROOT / p) == h, p


def open_frozen():
    assert sha(BASE) == FROZEN_SHA, 'FROZEN BASELINE SHA CHANGED'
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=str(BASE), load_ui=False, use_scripts=False)
    ob = bpy.data.objects[m.MESH_NAME]
    rig = bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
    with bpy.data.libraries.load(str(SOURCE), link=False) as (src, dst):
        dst.actions = [ACTION]
    rig.animation_data_create()
    rig.animation_data.action = bpy.data.actions[ACTION]
    bpy.data.actions[ACTION].use_fake_user = True
    got = digest(action_payload(bpy.data.actions[ACTION]))
    assert got == APPROVED_ACTION_SHA, 'APPROVED ACTION PAYLOAD CHANGED'
    neutral(rig)
    return ob, rig


def neutral(rig):
    if rig.animation_data:
        rig.animation_data.action = None
        for t in rig.animation_data.nla_tracks:
            t.mute = True
    m.reset_pose(rig)
    bpy.context.view_layer.update()


def motion(rig, f, sub=0):
    rig.animation_data.action = bpy.data.actions[ACTION]
    for t in rig.animation_data.nla_tracks:
        t.mute = False
    bpy.context.scene.frame_set(f, subframe=sub)
    bpy.context.view_layer.update()


def coords(ob):
    return np.array([list(v) for v in m.evaluate(ob, ob.matrix_world)[0]])


def values(ob):
    return {k.name: float(k.value) for k in ob.data.shape_keys.key_blocks[1:]}


def shape_state(ob):
    return core.shape_payload(ob)