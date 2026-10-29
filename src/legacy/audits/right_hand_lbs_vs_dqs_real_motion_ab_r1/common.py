import sys, json, hashlib, ast, math, copy
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PREV=ROOT/'audits/pianovam_retarget_local_axis_mapping_correction_r1'
sys.path.insert(0,str(PREV))
import mapping_core as core
from mapping_core import bpy, np, Vector
m=core.m
m.old.lib.OUT=OUT
BASE=core.BASE
SOURCE=PREV/'RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend'
ACTION='PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1'
PHASE='RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1'
TEST=OUT/(PHASE+'.blend')
FRAMES=[130,76,205,31,61]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dump(n,x):
    (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v.item())+'\n',encoding='utf-8')
ns={}
node=next(n for n in ast.parse((ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='action_payload')
exec(compile(ast.Module(body=[node],type_ignores=[]),'readonly_action_payload','exec'),ns)
action_payload=ns['action_payload']
def inputs():
    rows=read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['files_before']
    for p,h in rows.items():assert sha(ROOT/p)==h,p
    return rows
def rigs():return [bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'],bpy.data.objects['B_DQS_RIG']]
def neutral():
    for r in rigs():
        r.animation_data.action=None;m.reset_pose(r)
    bpy.context.view_layer.update()
def motion(f,sub=0):
    for r in rigs():r.animation_data.action=bpy.data.actions[ACTION]
    bpy.context.scene.frame_set(f,subframe=sub);bpy.context.view_layer.update()
def regression(c):
    neutral()
    for r in rigs():m.pose(r,next(x for x in m.CASES if x['case_id']==c))
    bpy.context.view_layer.update()
def coords(o):return np.array([list(v) for v in m.evaluate(o,o.matrix_world)[0]])
def values(o):return {k.name:float(k.value) for k in o.data.shape_keys.key_blocks[1:]}
def modifier_payload(ob):
    result=[]
    for mod in ob.modifiers:
        row={}
        for p in mod.bl_rna.properties:
            n=p.identifier
            if n in ['rna_type','persistent_uid','execution_time','is_active']:continue
            if p.type in ['BOOLEAN','INT','FLOAT','STRING','ENUM']:
                v=getattr(mod,n)
                row[n]=list(v) if getattr(p,'is_array',False) else v
            elif p.type=='POINTER':
                v=getattr(mod,n);row[n]=('MATCHED_RIG' if v in rigs() else v.name if v and hasattr(v,'name') else None)
        result.append(row)
    return result
