"""Read existing masters; export measured evidence only. Never save a blend or write weights."""
import sys
sys.dont_write_bytecode = True
import json, math, hashlib, datetime
from pathlib import Path
from collections import deque
import bpy
from mathutils import Vector, Quaternion

AUD = Path(__file__).resolve().parents[1]
ROOT = AUD.parents[2]
PROD = ROOT / 'production_spec'
S5 = PROD / 'stage5_production_rig'
S6 = PROD / 'stage6_deformation'
sys.path.append(str(S5 / 'stage5b_r1e/scripts'))
import s5b_r1e_common as C
TMP = AUD / '_tmp'
TMP.mkdir(exist_ok=True)
def dump(p, x):
    p.write_text(json.dumps(x, indent=1, ensure_ascii=False), encoding='utf-8')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
dirs = [S5/'stage5a_r2a', S5/'stage5b_r1b', S5/'stage5b_r1e', Path(C.R3D), S5/'stage5b_r1e_feasibility_audit']
frozen = set(p for d in dirs for p in d.rglob('*') if p.is_file())
frozen.update(ROOT.rglob('*.blend'))
frozen.update([Path(C.CASE_MATRIX), Path(C.CMC_AUDIT), S5/'stage5b_r1a/FIRST_WEB_WEIGHT_AUDIT_R1A.json', S5/'stage5b_r1a/FIRST_WEB_REGION_AUDIT_R1A.json'])
before = {str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(frozen)}
dump(AUD/'R1E_ENDPOINT_FROZEN_HASHES_BEFORE.json', before)
print('FROZEN BEFORE',len(before),flush=True)
lab = json.loads(Path(C.R3_FILES['r3_ownership_labels']).read_text(encoding='utf-8'))

def read_master(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    ob, rig = bpy.data.objects[C.MESH_OBJ], bpy.data.objects[C.RIG_OBJ]
    v = [list(ob.matrix_world @ x.co) for x in ob.data.vertices]
    w = [{ob.vertex_groups[g.group].name:float(g.weight) for g in x.groups if g.weight>0} for x in ob.data.vertices]
    edges = [list(e.vertices) for e in ob.data.edges]
    faces = [list(p.vertices) for p in ob.data.polygons]
    bones = {b.name:{'matrix_local':[list(row) for row in b.matrix_local], 'head_local':list(b.head_local), 'tail_local':list(b.tail_local), 'parent':b.parent.name if b.parent else None} for b in rig.data.bones}
    return {'v':v,'w':w,'edges':edges,'faces':faces,'bones':bones,'rig_world':[list(row) for row in rig.matrix_world], 'mesh_world':[list(row) for row in ob.matrix_world]},ob,rig

B,_,_ = read_master(C.R1B_MASTER)
A,_,rA = read_master(C.R2A)
joints = {n:list(rA.matrix_world @ rA.data.bones[n].head_local) for n in C.DEFORM}
chains = {d:[list(rA.matrix_world @ rA.data.bones[ch[0]].head_local)]+[list(rA.matrix_world @ rA.data.bones[n].tail_local) for n in ch] for d,ch in C.BONE_CHAIN.items()}
arcs = {d:[C.arc_of([Vector(p) for p in pts],Vector(v)) for v in B['v']] for d,pts in chains.items()}
FW,_,_ = read_master(S5/'stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend')
E,ob,rig = read_master(S5/'stage5b_r1e/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend')
assert B['v']==E['v'] and B['edges']==E['edges'] and B['faces']==E['faces'] and B['bones']==E['bones']
assert len(lab['CAP'])==9 and all(E['w'][v]=={'THUMB_IP_R':1.0} for v in lab['CAP'])
assert all(B['w'][v]==E['w'][v]==FW['w'][v] for v in lab['WEB'])
cases = {c['case_id']:c for c in json.loads(Path(C.CASE_MATRIX).read_text(encoding='utf-8'))['cases']}
poses = {}
for cid in ['TH_IP_30','TH_IP_45','TH_MCP_45','CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3']:
    C.reset_pose(rig)
    if cid.startswith('TH_'):
        group = 'THUMB_IP_R' if cid.startswith('TH_IP') else 'THUMB_MCP_R'
        C.set_joint_rotation(rig,group,-float(cid.rsplit('_',1)[1]))
        spec = {'bone':group,'angle_deg':-float(cid.rsplit('_',1)[1])}
    else:
        spec = cases[cid]
        rig.pose.bones['THUMB_CMC_R'].rotation_quaternion=Quaternion(spec['cmc_quaternion_local'])
        for group, angle in [('THUMB_MCP_R',spec['mcp_deg']),('THUMB_IP_R',spec['ip_deg'])]:
            C.set_joint_rotation(rig,group,-angle)
    C.update()
    transforms = {g:rig.matrix_world @ rig.pose.bones[g].matrix @ rig.data.bones[g].matrix_local.inverted() @ rig.matrix_world.inverted() for g in C.DEFORM}
    identity_errors = {g:max(abs(t[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4)) for g,t in transforms.items() if g in ['WRIST_R','INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R']}
    assert max(identity_errors.values())<2e-6
    posed = C.evaluate(ob,ob.matrix_world.copy())[0]
    # Validate analytical LBS against Blender's modifier without changing any weights.
    max_err=0.0
    for v in set(lab['CAP'])|{1551,3125}:
        total=sum(E['w'][v].values())
        pred=sum(((transforms[g] @ Vector(B['v'][v]))*(w/total) for g,w in E['w'][v].items()),Vector())
        max_err=max(max_err,(pred-posed[v]).length*1000)
    assert max_err<0.001
    poses[cid]={'spec':spec,'transforms':{g:[list(row) for row in t] for g,t in transforms.items()},'posed': [list(v) for v in posed], 'stationary_group_identity_errors':identity_errors,'LBS_validation_max_error_mm':max_err}
    print('READ ONLY POSE',cid,'LBS error mm',max_err,flush=True)
C.reset_pose(rig)
C.update()
raw={'runtime':{'blender':bpy.app.version_string,'binary':bpy.app.binary_path},'generated_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(), 'R1B':B,'R1E':E,'R2A_joints':joints,'R2A_chains':chains,'arcs_mm':arcs,'R3':lab,'first_web_approved_weights':{str(v):FW['w'][v] for v in lab['WEB']},'poses':poses}
dump(TMP/'review_raw.json',raw)
after={p:sha(ROOT/p) for p in before}
assert before==after
dump(TMP/'extract_hash_check.json',{'equal':True,'files':len(before)})
print('EXTRACTION COMPLETE; NO BLENDS SAVED',flush=True)
