from geometry import *
import geometry as g
R2=ROOT/'experiments/hands_c1_exit_handoff_correction_r2'
STARTCOPY=OUT/'R2_START_ISOLATED_NOT_APPROVED.blend'
assert sha(STARTCOPY)==sha(R2/'EXIT_CORRECTED_NOT_APPROVED.blend')
extract(ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1/validate_full.py',['collision','selfpairs'],globals())
sc,rig,mesh,left,lrig=s.open_scene(STARTCOPY);g.init()
bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
BASE_NATIVE={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
BASE_ACTIONS=s.protected_state()
BASE_ACTION_COUNT=len(bpy.data.actions)
BASE_CAMERA={kind:dict(matrix=np.array(bpy.data.objects[name].matrix_world),type=bpy.data.objects[name].data.type,scale=bpy.data.objects[name].data.ortho_scale) for kind,name in MAN['cameras'].items()}
targets=[('R08',3.12),('R09',3.45),('R10',3.67),('R11',3.88)]
baselines={};attempts={tag:0 for tag,t in targets}
def label(i):
 return max([(mesh.vertex_groups[a.group].name.split('_')[0],a.weight) for a in mesh.data.vertices[int(i)].groups],key=lambda x:x[1])[0]
def tri_label(ids):
 labs=[label(i) for i in ids];return max(set(labs),key=labs.count)
def qset(d,q):
 for name,M in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(q))):rig.pose.bones[name].rotation_quaternion=Matrix(M.tolist()).to_quaternion()
 bpy.context.view_layer.update()
def measure(tag,t):
 V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left)
 active=[n for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
 assert len(active)==1
 n=active[0];keys=collision(V);illegal={k:v for k,v in keys.items() if k!=n['note_name'] and (v['depth_mm']>1e-6 or v['pairs'])}
 for item in illegal.values():
  if item['witness']:item['dominant_bones']=[label(i) for i in item['witness']['vertices']]
 sp=selfpairs(V);categories={}
 for a,b in sp:
  k='/'.join(sorted([tri_label(T[a]),tri_label(T[b])]))
  categories[k]=categories.get(k,0)+1
 Q=np.array([s.degrees(d) for d in DIGITS]);contact=s.contact(V,KEYS[n['key_index']],'R',n['finger'])
 cross=set(g.tree(V,T).overlap(g.tree(L,LT)))
 pads={d:dict(world=V[c.MARKERS['R'][i]['mesh_vertex']],range_min=V[np.array(ROI[d]['vertices'],int)].min(0),range_max=V[np.array(ROI[d]['vertices'],int)].max(0)) for i,d in enumerate(DIGITS)}
 row=dict(tag=tag,time=t,event=n,key=n['note_name'],finger=n['finger'],contact=contact,keys=keys,illegal=illegal,self_count=len(sp),self_categories=categories,self_examples=[dict(triangles=[a,b],vertices=[T[a],T[b]]) for a,b in sorted(sp)[:10]],q=Q,pads=pads,wrist=np.array(<REDACTED_EMAIL>['WRIST_R'].matrix),domain_violation_deg=float(max(0,np.max(bounds[:,0]-Q),np.max(Q-bounds[:,1]))),cross_count=len(cross),mesh_digest=c.digest(V.tolist()))
 if tag in baselines:
  base=baselines[tag];row['left_delta_mm']=float(np.linalg.norm(L-base['L'],axis=1).max()*1000);row['new_cross_count']=len(cross-base['cross'])
 row['native_unchanged']=BASE_NATIVE=={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
 row['actions_unchanged']=BASE_ACTIONS==s.protected_state() and len(bpy.data.actions)==BASE_ACTION_COUNT
 row['machine_pass']=bool(not illegal and not sp and contact['pass_'] and row['domain_violation_deg']<=1e-6 and row.get('new_cross_count',0)==0 and row.get('left_delta_mm',0)==0 and row['native_unchanged'] and row['actions_unchanged'])
 return row,V,L,cross
def concise(row):
 return {k:row[k] for k in ['tag','time','key','finger','contact','illegal','self_count','self_categories','q','pads','wrist','domain_violation_deg','machine_pass','actions_unchanged']}
def render(tag,kind,row):
 sc.camera=bpy.data.objects[MAN['cameras'][kind]]
 sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
 sc.render.filepath=str(OUT/f'{tag}_{kind}.png')
 assert not Path(sc.render.filepath).exists()
 # Blender reevaluates the original Action at render start. Restore the static
 # pose AFTER that evaluation; never mute, unlink, replace or edit the Action.
 pose={b.name:(b.location.copy(),b.rotation_quaternion.copy(),b.scale.copy()) for b in rig.pose.bones}
 def restore_static(*args):
  for name,(loc,rot,scale) in pose.items():
   b=rig.pose.bones[name];b.location=loc;b.rotation_quaternion=rot;b.scale=scale
  bpy.context.view_layer.update()
 checks=[]
 def verify_static(*args):checks.append(c.digest(s.coords_tri(mesh)[0].tolist()))
 bpy.app.handlers.frame_change_post.append(restore_static)
 bpy.app.handlers.render_pre.append(restore_static)
 bpy.app.handlers.render_post.append(verify_static)
 try:
  bpy.ops.render.render(write_still=True)
 finally:
  bpy.app.handlers.frame_change_post.remove(restore_static)
  bpy.app.handlers.render_pre.remove(restore_static)
  bpy.app.handlers.render_post.remove(verify_static)
 assert checks==[row['mesh_digest']],'RENDER_POSE_CHANGED'
 save(tag+'_'+kind+'_RENDER_VERIFICATION.json',dict(mesh_digest=row['mesh_digest'],render_post_digests=checks,original_actions_unchanged=BASE_ACTIONS==s.protected_state(),temporary_static_restore_handlers_removed=True))
def baseline(tag,t,images=True):
 c.settime(sc,t)
 row,V,L,cross=measure(tag,t)
 baselines[tag]=dict(row=row,L=L,cross=cross,pose={b.name:dict(location=list(b.location),rotation_mode=b.rotation_mode,quaternion=list(b.rotation_quaternion),scale=list(b.scale)) for b in rig.pose.bones})
 save(tag+'_BASELINE.json',row)
 if images:
  for kind in ['OVERHEAD','SIDE_OBLIQUE']:render(tag+'_BASE',kind,row)
 return concise(row)
def candidate(tag,changes,reason,wrist_delta_mm=None):
 assert attempts[tag]<2,'TWO_ROUND_CAP'
 base=baselines[tag];t=base['row']['time'];c.settime(sc,t)
 for name,p in base['pose'].items():
  b=rig.pose.bones[name];b.location=p['location'];b.rotation_mode=p['rotation_mode'];b.rotation_quaternion=p['quaternion'];b.scale=p['scale']
 for d,q in changes.items():qset(d,q)
 if wrist_delta_mm is not None:
  b=rig.pose.bones['WRIST_R'];M=<REDACTED_EMAIL>;M.translation+=Vector(wrist_delta_mm)*.001;b.matrix=rig.matrix_world.inverted()@M
 bpy.context.view_layer.update();attempts[tag]+=1
 name=f'{tag}_ROUND_{attempts[tag]}_NOT_APPROVED'
 row,V,L,cross=measure(tag,t)
 snapshot=dict(status='NOT_APPROVED',source=str(STARTCOPY),source_sha256=sha(STARTCOPY),time=t,frame=1+60*t,changes=changes,wrist_delta_mm=wrist_delta_mm,reason=reason,pose={b.name:dict(location=list(b.location),rotation_mode=b.rotation_mode,quaternion=list(b.rotation_quaternion),scale=list(b.scale)) for b in rig.pose.bones},action_policy='Original Action retained and unmodified. Apply snapshot AFTER exact frame_set. Static overrides only; changing frame restores animation.',validation=row)
 save(name+'_POSE.json',snapshot)
 np.savez_compressed(OUT/(name+'_EVALUATED.npz'),V=V,T=g.ALLT)
 for kind in ['OVERHEAD','SIDE_OBLIQUE']:render(name,kind,row)
 return concise(row)
print('R4_STATIC_SESSION_INITIALIZED',flush=True)
