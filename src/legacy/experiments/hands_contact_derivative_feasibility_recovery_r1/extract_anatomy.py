import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands';sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
import blender_utils as u
I=u.I;PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1'
META=json.loads((O/'SKIN_MODEL_META.json').read_text());RAW=np.load(O/'SKIN_MODEL.npz')
def unit(v):return np.array(v)/np.linalg.norm(v)
def angle(u,v,n):
 u=unit(u-n*np.dot(u,n));v=unit(v-n*np.dot(v,n))
 return float(np.degrees(np.arctan2(np.dot(n,np.cross(u,v)),np.dot(u,v))))
def matrix(x):return np.array([list(r) for r in x])
def coords(x):return np.array(list(x))
def signed_rot(R,n):
 q=Matrix(R.tolist()).to_quaternion();a=2*math.atan2(np.linalg.norm([q.x,q.y,q.z]),q.w);v=np.array([q.x,q.y,q.z])
 return float(np.degrees(a)*np.dot(unit(v),n)) if np.linalg.norm(v)>1e-10 else 0.
def anatomy(rig,mesh,label,hand='R',state=None):
 assert hand in ['R','L']
 rest=rig.data.bones;pose=rig.pose.bones
 hn=lambda d,j:f'{d}_{j}_{hand}'
 wh=coords(rest[f'WRIST_{hand}'].head_local);mid=coords(rest[hn('MIDDLE','MCP')].head_local)
 across=coords(rest[hn('LITTLE','MCP')].head_local)-coords(rest[hn('INDEX','MCP')].head_local)
 y=unit(mid-wh);z=unit(np.cross(across,y))
 if np.dot(z,[0,0,1])<0:z=-z
 x=unit(np.cross(y,z));y=unit(np.cross(z,x));frame=np.column_stack([x,y,z])
 wristR=matrix(pose[f'WRIST_{hand}'].matrix)[:3,:3]@np.linalg.inv(matrix(rest[f'WRIST_{hand}'].matrix_local)[:3,:3]);frame=wristR@frame
 digitrows=[];allq=[]
 for d in u.c.DIGITS:
  names,rels,axes,spread,pad=u.c.SETUPS[hand,d];jointrows=[];recovered=[]
  for ji,name in enumerate(names):
   b=rest[name];pb=pose[name];R=matrix(pb.matrix_basis)[:3,:3];U,sv,Vt=np.linalg.svd(R);R=U@Vt
   ax=np.array(axes[ji]);sp=np.array(spread)
   if ji==0:
    ss=angle(ax,R@ax,sp);RF=u.c.axisrot(-np.radians(ss),sp)@R;ff=signed_rot(RF,ax);reconstruct=u.c.axisrot(np.radians(ss),sp)@u.c.axisrot(np.radians(ff),ax)
   else:ss=0.;ff=signed_rot(R,ax);reconstruct=u.c.axisrot(np.radians(ff),ax)
   recovered.append(ff)
   direction=unit(matrix(pb.matrix)[:3,1]);parentdir=unit(matrix(pose[names[ji-1]].matrix)[:3,1]) if ji>0 else frame[:,1]
   pre=matrix(pose[b.parent.name].matrix)@np.linalg.inv(matrix(rest[b.parent.name].matrix_local))@matrix(b.matrix_local) if b.parent else matrix(b.matrix_local)
   aw=unit(pre[:3,:3]@ax)
   lateral=float(np.degrees(np.arcsin(np.clip(np.dot(direction,aw),-1,1))-np.arcsin(np.clip(np.dot(parentdir,aw),-1,1))))
   pp=frame.T@direction
   row=dict(bone=name,parent=b.parent.name if b.parent else None,deform=b.use_deform,length_mm=b.length*1000,rest_local_matrix=matrix(b.matrix_local).tolist(),basis_rotation=R.tolist(),axis_flex_local=ax.tolist(),axis_spread_local=sp.tolist() if ji==0 else None,positive_flex_direction='Rodrigues about cross(rest longitudinal Y, canonical palmar -Z); positive is palmar bending in rest reference',recovered_flex_increment_deg=ff,recovered_spread_increment_deg=ss if ji==0 else None,off_model_rotation_matrix_error=float(np.linalg.norm(R-reconstruct)),parent_to_child_projected_bend_deg=angle(parentdir,direction,aw),parent_to_child_out_of_hinge_plane_deg=lateral,palm_heading_deg=float(np.degrees(np.arctan2(pp[0],pp[1]))),palm_elevation_deg=float(np.degrees(np.arctan2(pp[2],np.linalg.norm(pp[:2])))),head_rig_m=coords(pb.head).tolist(),tail_rig_m=coords(pb.tail).tolist(),head_world_m=list(<REDACTED_EMAIL>),tail_world_m=list(<REDACTED_EMAIL>),rest_head_rig_m=coords(b.head_local).tolist(),rest_tail_rig_m=coords(b.tail_local).tolist(),Blender_constraints=[dict(type=c.type,name=c.name) for c in pb.constraints])
   jointrows.append(row)
  recovered.append(jointrows[0]['recovered_spread_increment_deg']);allq.append(recovered)
  dnames=set(n for n in rest.keys() if n.startswith(d+'_'));groupmap={g.index:g.name for g in mesh.vertex_groups}
  ws=np.array([sum(g.weight for g in v.groups if groupmap[g.group] in dnames) for v in mesh.data.vertices]);vids=np.flatnonzero(ws>.55);marker=int(RAW['pad_indices'][u.c.DIGITS.index(d)])
  digitrows.append(dict(digit=d,bone_chain=names+[f'{d}_TIP_{hand}'],joints=jointrows,skin_identity=dict(strong_digit_vertices=len(vids),strong_vertex_ids=vids.tolist(),mesh_vertex_groups=sorted(dnames),frozen_pad_vertex=marker,pad_vertex_digit_weight=float(ws[marker]),pad_vertex_weights={groupmap[g.group]:g.weight for g in mesh.data.vertices[marker].groups}),controls_recovered_deg=recovered))
 V,F=u.coords(mesh);np.savez_compressed(O/f'AUDIT_{label}_ACTUAL_SKIN.npz',vertices=V)
 native=u.digest(u.native(mesh,rig))
 if hand=='R':assert native==u.pf['right_native_sha256']
 return dict(label=label,hand=hand,native_sha256=native,mesh=mesh.name,rig=rig.name,vertex_count=len(V),face_count=len(F),root_world_matrix=matrix(rig.matrix_world).tolist(),palm_frame_in_rig=frame.tolist(),wrist_head_rig_m=coords(pose[f'WRIST_{hand}'].head).tolist(),wrist_head_world_m=list(rig.matrix_world@pose[f'WRIST_{hand}'].head),wrist_basis=matrix(pose[f'WRIST_{hand}'].matrix_basis).tolist(),digits=digitrows,recovered_controls=allq,source_state=state,shape_key_values={b.name:b.value for b in mesh.data.shape_keys.key_blocks},frozen_native_verified=hand=='R')
rows=[]
# Formal R2, zero basis rest. Rest already contains curvature.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/I['right_pointer']['asset']['path']),load_ui=False,use_scripts=False)
rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];mesh=bpy.data.objects['RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH']
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update();rows.append(anatomy(rig,mesh,'FROZEN_R2_REST'))
# Approved four static poses: read-only actual Blender bone matrices.
sm=I['static_scene'];bpy.ops.wm.open_mainfile(filepath=sm['candidate_path'],load_ui=False,use_scripts=False)
for label,info in sm['mapping'].items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc
 rows.append(anatomy(bpy.data.objects[info['rig']],bpy.data.objects[info['mesh']],'APPROVED_'+label,info['hand']))
# S1 actual saved #2 and reconstruct #1 from exact recorded controls in copied scene.
P=json.loads((PRE/'POLICY_LOCK.json').read_text());M=P['source_action_scene']
bpy.ops.wm.open_mainfile(filepath=str(PRE/'S1_CONSTRAINED_DIAGNOSTIC_R1.blend'),load_ui=False,use_scripts=False)
info=json.loads((PRE/'ACTUAL_VALIDATION_2.json').read_text());sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']];rt=bpy.data.objects[info['root']]
rows.append(anatomy(rig,mesh,'S1_2_HUMAN_FAIL',state=info['state']))
r1=json.loads((PRE/'SOLVE_1.json').read_text());u.apply(np.array(r1['state']),rt,rig);rows.append(anatomy(rig,mesh,'S1_1_HUMAN_FAIL',state=r1['state']))
# Original S2 qualified static posture, no state changes.
static=O.parent/'hands_skin_collision_static_feasibility_r1';F=json.loads((static/'STATIC_POSE_FEASIBILITY.json').read_text());test=F['tests'][1];info=next(a for a in test['attempts'] if a['scene']==test['selected_scene'])
bpy.ops.wm.open_mainfile(filepath=F['diagnostic_blend'],load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes[info['scene']]
rows.append(anatomy(bpy.data.objects[info['rig']],bpy.data.objects[info['mesh']],'S2_STATIC_QUALIFIED',state=info['controls']['state']))
out=dict(task='PIANO_C01_ANATOMY_AND_PREPARATION_AUDIT_R1',authority='DESIGN_PROVISIONAL',human_baseline='S1_HUMAN_ANATOMICAL_VISUAL_FAIL',rows=rows,angles_not_Blender_Euler=True,angle_meaning='Recovered ordered rest-relative control rotations; projected bone tangent bends/palm heading are geometric reference angles, not clinically calibrated absolute anatomical joint angles',source_files_readonly=True,no_blend_saved=True)
(O/'ACTUAL_RIG_ANATOMY.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
for r in rows:
 mid=next(d for d in r['digits'] if d['digit']=='MIDDLE')
 print(r['label'],mid['controls_recovered_deg'],'heading',mid['joints'][0]['palm_heading_deg'],'PIPbend',mid['joints'][1]['parent_to_child_projected_bend_deg'],'DIPbend',mid['joints'][2]['parent_to_child_projected_bend_deg'],'offmodel',max(j['off_model_rotation_matrix_error'] for j in mid['joints']),flush=True)
