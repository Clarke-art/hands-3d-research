import sys, json, hashlib, ast, math
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PREV=ROOT/'audits/pianovam_retarget_local_axis_mapping_correction_r1'
sys.path.insert(0,str(PREV))
import mapping_core as core
from mapping_core import bpy, Vector, Matrix, Quaternion, np
m=core.m
m.old.lib.OUT=OUT
BASE=core.BASE
SOURCE=PREV/'RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend'
SOURCE_SHA='a5190adc13d39318096490f8fd2c9956d0daff457d25753fa3c216eee2027bbd'
ACTION='PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1'
PHASE='FIRST_WEB_REAL_MOTION_DEFORMATION_FIX_R1'
CANDIDATE=OUT/'RIGHT_HAND_REAL_MOTION_FIRST_WEB_FIX_CANDIDATE_R1.blend'
FIX=ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1'
FRAMES=[130,76,205,31,61]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dump(n,x):
    def cv(v):
        if hasattr(v,'tolist'):return v.tolist()
        if hasattr(v,'item'):return v.item()
        raise TypeError(type(v))
    (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=cv)+'\n',encoding='utf-8')
ns={}
node=next(n for n in ast.parse((ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='action_payload')
exec(compile(ast.Module(body=[node],type_ignores=[]),'readonly_action_payload','exec'),ns)
action_payload=ns['action_payload']
def actions():return {a.name:digest(action_payload(a)) for a in bpy.data.actions}
def load(path):
    ob,rig=m.open_file(path)
    if rig.animation_data:rig.animation_data.action=None
    m.reset_pose(rig);bpy.context.view_layer.update()
    return ob,rig
def neutral(rig):
    if rig.animation_data:rig.animation_data.action=None
    m.reset_pose(rig);bpy.context.view_layer.update()
def motion(rig,f,subframe=0):
    rig.animation_data.action=bpy.data.actions[ACTION]
    bpy.context.scene.frame_set(f,subframe=subframe);bpy.context.view_layer.update()
def Varray(ob):return np.array([list(v) for v in m.evaluate(ob,ob.matrix_world)[0]])
def weights(ob):
    W=np.zeros((len(ob.data.vertices),len(ob.vertex_groups)))
    for v in ob.data.vertices:
        for g in v.groups:W[v.index,g.group]=g.weight
    return W
def skin(rig):return {p.name:<REDACTED_EMAIL>@p.bone.matrix_local.inverted()@rig.matrix_world.inverted() for p in rig.pose.bones}
def transform(T,V):return <REDACTED_EMAIL>([list(r) for r in T.to_3x3()]).T+np.array(list(T.translation))
def regression(rig,case):
    neutral(rig);m.pose(rig,next(c for c in m.CASES if c['case_id']==case))
def design(ob):
    for x in [ob,bpy.context.scene]:
        x['DESIGN_ONLY']=True;x['HUMAN_APPROVAL_PENDING']=True;x['PRODUCTION_PROMOTION']='NO'
        x['PHASE']=PHASE
    ob['PRODUCT_BASELINE_STATUS']='DESIGN_ONLY_NOT_PRODUCTION'
def check_inputs():
    assert sha(BASE)==core.BASE_SHA and sha(SOURCE)==SOURCE_SHA
    status=read(PREV/'PIANOVAM_RETARGET_LOCAL_AXIS_MAPPING_CORRECTION_R1_STATUS.json')
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in status['source_file_hashes_unchanged'])
    return {p.relative_to(ROOT).as_posix():sha(p) for p in [BASE,SOURCE,PREV/'mapping_core.py']+[ROOT/r['path'] for r in status['source_file_hashes_unchanged']]}
