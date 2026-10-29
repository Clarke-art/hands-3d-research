import sys,json,hashlib,ast,math,copy
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'audits/pianovam_retarget_local_axis_mapping_correction_r1'
sys.path.insert(0,str(PREV))
import mapping_core as core
from mapping_core import bpy,np,Vector,Matrix,Quaternion
m=core.m;m.old.lib.OUT=OUT
BASE=core.BASE;SOURCE=PREV/'RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend'
ACTION='PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1'
PHASE='FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1'
FRAMES=[130,76,205,61]
PATCH_IDS=json.loads((ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1/WEIGHT_ITERATION_2.json').read_text())['allowed_vertex_ids']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v.item())+'\n',encoding='utf-8')
ns={};node=next(n for n in ast.parse((ROOT/'audits/pianovam_first_web_corrective_ab_isolation_r1/isolate.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='action_payload');exec(compile(ast.Module(body=[node],type_ignores=[]),'readonly_action_payload','exec'),ns);action_payload=ns['action_payload']
def inputs():
    rows=read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['files_before']
    for p,h in rows.items():assert sha(ROOT/p)==h,p
    return rows
def fresh():
    inputs();ob,rig=m.open_file(BASE)
    with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):dst.actions=[ACTION]
    rig.animation_data_create();rig.animation_data.action=bpy.data.actions[ACTION]
    bpy.data.actions[ACTION].use_fake_user=True
    assert digest(action_payload(rig.animation_data.action))==read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['actions_before'][ACTION]
    neutral(rig);return ob,rig
def load(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    return bpy.data.objects[m.MESH_NAME],bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
def neutral(rig):
    if rig.animation_data:
        rig.animation_data.action=None
        for t in rig.animation_data.nla_tracks:t.mute=True
    m.reset_pose(rig);bpy.context.view_layer.update()
def motion(rig,f,sub=0):
    rig.animation_data.action=bpy.data.actions[ACTION]
    for t in rig.animation_data.nla_tracks:t.mute=False
    bpy.context.scene.frame_set(f,subframe=sub);bpy.context.view_layer.update()
def coords(ob):return np.array([list(v) for v in m.evaluate(ob,ob.matrix_world)[0]])
def values(ob):return {k.name:float(k.value) for k in ob.data.shape_keys.key_blocks[1:]}
def weights(ob):
    w=np.zeros((len(ob.data.vertices),len(ob.vertex_groups)))
    for v in ob.data.vertices:
        for g in v.groups:w[v.index,g.group]=g.weight
    return w
def support(ob):
    v=np.array([list(<REDACTED_EMAIL>) for x in ob.data.vertices]);c=np.array([1.443,.022,.45]);r=np.array([.022,.022,.025]);t=np.maximum(0,1-np.linalg.norm((v-c)/r,axis=1));t=t*t*(3-2*t)
    mask=np.zeros(len(v));mask[PATCH_IDS]=t[PATCH_IDS];return mask
def save(ob,path):
    assert not path.exists(),'Refuse overwrite POC'
    for x in [ob,bpy.context.scene]:
        x['DESIGN_ONLY']=True;x['HUMAN_APPROVAL_PENDING']=True;x['PRODUCTION_PROMOTION']='NO';x['PHASE']=PHASE
    ob['PRODUCT_BASELINE_STATUS']='DESIGN_ONLY_NOT_PRODUCTION'
    bpy.context.scene['HUMAN_APPROVED']=False;bpy.context.scene['RIGHT_HAND_PRODUCT_BASELINE']='DESIGN_ONLY_NOT_PRODUCTION';bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=210
    bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=False)
def cameras():
    rows=read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['frames']
    return {str(r['frame']):r['same_camera'] for r in rows if r['condition']=='BASELINE'}
