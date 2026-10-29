import sys,json,hashlib,math,time,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix,Vector
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands'
sys.path.insert(0,str(ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion'))
import stage_common as m
import ast
m.NEUTRAL=np.degrees(m.o.qanchor('R1'));m.BASE,m.RBASE=m.o.root('R')
m.B=np.array([m.o.SP['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG'] for j in range(5)])
tree=ast.parse((ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/coordinated_motion.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['rotations','extra_rotation','fk_batch']],type_ignores=[]),'existing_fk_only','exec'),m.__dict__)
c=m.c
I=json.loads((O/'INPUT_BINDINGS.json').read_text());man=I['source_scene'];sm=I['static_scene']
def out(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def native(ob,rig):
 return dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],weights=[[[ob.vertex_groups[g.group].name,g.weight] for g in v.groups] for v in ob.data.vertices],bones=[dict(name=b.name,parent=b.parent.name if b.parent else None,deform=b.use_deform,head=list(b.head_local),tail=list(b.tail_local),matrix=[list(r) for r in b.matrix_local]) for b in rig.data.bones],shapes={b.name:[list(v.co) for v in b.data] for b in ob.data.shape_keys.key_blocks},corrective_drivers=[dict(path=f.data_path,expression=f.driver.expression,variables=[dict(name=v.name,type=v.type,targets=[dict(bone=t.bone_target,transform_type=t.transform_type,transform_space=t.transform_space,data_path=t.data_path) for t in v.targets]) for v in f.driver.variables]) for f in ob.data.shape_keys.animation_data.drivers] if ob.data.shape_keys.animation_data else [])
def settime(sc,t):
 f=1+60*t;sc.frame_set(math.floor(f),subframe=f-math.floor(f));bpy.context.view_layer.update()
def coords(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();V=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);faces=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear();return V,faces
bpy.ops.wm.open_mainfile(filepath=str(ROOT/I['right_pointer']['asset']['path']),load_ui=False,use_scripts=False)
ob=bpy.data.objects['RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];frozen=native(ob,rig);frozen_sha=digest(frozen)
bpy.ops.wm.open_mainfile(filepath=sm['candidate_path'],load_ui=False,use_scripts=False)
statics={}
for pose,info in sm['mapping'].items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;mesh=bpy.data.objects[info['mesh']];rr=bpy.data.objects[info['rig']]
 statics[pose]=dict(native_identity=digest(native(mesh,rr)),mesh=info['mesh'],rig=info['rig'],pose_matrices={b.name:[list(row) for row in b.matrix_basis] for b in rr.pose.bones})
 if pose=='R1':staticbase=np.array(bpy.data.objects[info['root']].matrix_world)
assert statics['R1']['native_identity']==frozen_sha and statics['R2']['native_identity']==frozen_sha
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];rt=bpy.data.objects[man['mapping']['R']['root']]
assert digest(native(mesh,rig))==frozen_sha
keygroups={k['key_index']:[ob for ob in sc.objects if ob.type=='MESH' and ob.get('FROZEN_KEY_INDEX')==k['key_index']] for k in c.KEYS}
settime(sc,0);err=0;keyrows=[]
for k in c.KEYS:
 obs=keygroups[k['key_index']];assert len(obs)==len(k['geometry'])
 for g in k['geometry']:
  ob=next(ob for ob in obs if g['name'] in ob.name);actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);expected=np.array(g['vertices']);err=max(err,float(np.max(np.abs(actual-expected))))
 if 66<=k['midi_note']<=80:keyrows.append({x:k[x] for x in ['midi_note','note_name','color','key_center','key_top_playable_surface','press_pivot','press_angle_rad']})
assert err<1e-6,err
start,end=I['clip_start_sec'],I['clip_end_sec'];times=np.unique(np.r_[np.arange(start,end+1/240,1/120),[v+d for n in I['notes'] for v in [n['note_on'],n['note_off']] for d in [-.15,-.075,-.045,0,.0175,.035,.04,.07]],[start,end]])
times=times[(times>=start)&(times<=end)];angles=[]
for t in times:
 settime(sc,float(t));a=np.zeros(88)
 for ki,pname in man['key_pivots'].items():a[int(ki)]=bpy.data.objects[pname].rotation_euler.x
 angles.append(a)
np.savez_compressed(O/'KEY_ACTION_SAMPLES.npz',times=times,key_angles=angles,static_root_base=staticbase)
# In-memory parity only: no source file is saved.
rig.animation_data_clear();rt.animation_data_clear();rt.matrix_world=Matrix(staticbase.tolist())
for j,d in enumerate(c.DIGITS):
 for n,r in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(m.NEUTRAL[j]))):rig.pose.bones[n].rotation_mode='QUATERNION';rig.pose.bones[n].rotation_quaternion=Matrix(r.tolist()).to_quaternion()
bpy.context.view_layer.update();V,F=coords(mesh)
pads=np.array([list(<REDACTED_EMAIL>[row['distal_frame']].matrix@Vector(row['local_pad_point'])) for row in c.MARKERS['R']]);pred=m.fk_batch(np.r_[np.zeros(6),m.NEUTRAL.ravel()])[0][0]
parity=float(np.max(np.linalg.norm(pads-pred,axis=1))*1000);assert parity<.05,parity
rois={};rest=np.array([list(v.co) for v in mesh.data.vertices]);group={g.index:g.name for g in mesh.vertex_groups}
for digit in c.DIGITS:
 weights=np.array([sum(g.weight for g in v.groups if group[g.group].startswith(digit+'_')) for v in mesh.data.vertices]);ids=np.flatnonzero(weights>.55);members=set(ids);faces=[list(p.vertices) for p in mesh.data.polygons if all(v in members for v in p.vertices)]
 rois[digit]=dict(vertices=ids.tolist(),faces=faces,scope='Strong digit-weight actual skin, includes proximal/middle/distal; excludes shared palm/web')
out('DIGIT_SKIN_ROI.json',rois);out('HAND_NATIVE_IDENTITY.json',dict(sha256=frozen_sha))
out('RIG_PREFLIGHT.json',dict(blender=bpy.app.version_string,source_scene=man['path'],right_frozen_asset=str(ROOT/I['right_pointer']['asset']['path']),right_native_matches_frozen=True,right_native_sha256=frozen_sha,static_four=statics,vertex_count=len(mesh.data.vertices),face_count=len(mesh.data.polygons),bone_count=len(rig.data.bones),deform_bones=sum(b.use_deform for b in rig.data.bones),nondeform_tip_bones=[b.name for b in rig.data.bones if not b.use_deform],mesh_modifiers=[dict(name=x.name,type=x.type) for x in mesh.modifiers],root=dict(name=rt.name,parent=rt.parent.name if rt.parent else None,scale=list(rt.scale),allows_object_translation_rotation=True),wrist=dict(name='WRIST_R',constraints=[x.type for x in rig.pose.bones['WRIST_R'].constraints]),base_xyz_m=m.BASE,base_rotation=m.RBASE,neutral_q_deg=m.NEUTRAL,engineering_joint_bounds_deg=m.B,key_geometry_parity_max_mm=err*1000,key_count=88,key_rows=keyrows,actual_bone_pad_vs_existing_FK_mm=parity,actual_skin_vs_bone_pad_mm=np.linalg.norm(V[[r['mesh_vertex'] for r in c.MARKERS['R']]]-pads,axis=1)*1000,static_root_base_matrix=staticbase,full_root_rig_relation=np.array(rt.matrix_world.inverted()@rig.matrix_world),frozen_scale_unchanged=True,preflight_notes='Only approved source identity and actual geometric extraction; no historical geometry repair or source save.'))
print('REAL_PREFLIGHT_PASS',parity,err*1000,len(times),flush=True)

