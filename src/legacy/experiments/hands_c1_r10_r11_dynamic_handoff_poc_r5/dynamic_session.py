from geometry import *
import geometry as g
R2=ROOT/'experiments/hands_c1_exit_handoff_correction_r2'
R4=ROOT/'experiments/hands_c1_multi_note_safe_pose_feasibility_r4'
STARTCOPY=OUT/'R2_START_ISOLATED_NOT_APPROVED.blend'
assert sha(STARTCOPY)==sha(R2/'EXIT_CORRECTED_NOT_APPROVED.blend')
READS[str(R2/'EXIT_CORRECTED_NOT_APPROVED.blend')]=sha(STARTCOPY)
extract(ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1/validate_full.py',['collision','selfpairs'],globals())
bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
sc,rig,mesh,left,lrig=s.open_scene(STARTCOPY);g.init()
BASE_ACTION=rig.animation_data.action
BASE_NATIVE={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
OTHER_ACTIONS=s.protected_state(True)
R10=next(n for n in NOTES if n['note_id']=='R10');R11=next(n for n in NOTES if n['note_id']=='R11');R12=next(n for n in NOTES if n['note_id']=='R12')
A,H,B=R10['note_on'],R11['note_on'],R12['note_on']
def reset(path=STARTCOPY):
 global sc,rig,mesh,left,lrig,BASE_ACTION
 sc,rig,mesh,left,lrig=s.open_scene(path);g.init();BASE_ACTION=rig.animation_data.action
 return sc
def qset(d,q):
 for name,M in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(q))):rig.pose.bones[name].rotation_quaternion=Matrix(M.tolist()).to_quaternion()
 bpy.context.view_layer.update()
def pose():
 return {b.name:dict(location=list(b.location),quaternion=list(b.rotation_quaternion),scale=list(b.scale)) for b in rig.pose.bones}
def label(i):
 return max([(mesh.vertex_groups[a.group].name.split('_')[0],a.weight) for a in mesh.data.vertices[int(i)].groups],key=lambda x:x[1])[0]
def measure(t):
 V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left)
 active=[n for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
 keys=collision(V);illegal={k:v for k,v in keys.items() if k not in [n['note_name'] for n in active] and (v['pairs'] or v['depth_mm']>1e-6)}
 for it in illegal.values():
  if it['witness']:it['dominant_bones']=[label(i) for i in it['witness']['vertices']]
 sp=selfpairs(V);cats={}
 for a,b in sp:
  labs=[]
  for tri in [T[a],T[b]]:
   ll=[label(i) for i in tri];labs.append(max(set(ll),key=ll.count))
  k='/'.join(sorted(labs));cats[k]=cats.get(k,0)+1
 Q=np.array([s.degrees(d) for d in DIGITS]);contacts=[dict(event=n['note_id'],key=n['note_name'],finger=n['finger'],**s.contact(V,KEYS[n['key_index']],'R',n['finger'])) for n in active]
 pads={d:V[c.MARKERS['R'][i]['mesh_vertex']] for i,d in enumerate(DIGITS)}
 row=dict(time=t,active=[n['note_id'] for n in active],contacts=contacts,keys=keys,illegal=illegal,self_count=len(sp),self_categories=cats,cross_count=len(g.tree(V,T).overlap(g.tree(L,LT))),q=Q,wrist=np.array(<REDACTED_EMAIL>['WRIST_R'].matrix),rig_world=np.array(rig.matrix_world),wrist_basis=np.array(rig.pose.bones['WRIST_R'].matrix_basis),pads=pads,domain_violation_deg=float(max(0,np.max(bounds[:,0]-Q),np.max(Q-bounds[:,1]))))
 return row,V,L
def short(row):return {k:v for k,v in row.items() if k in ['time','active','contacts','illegal','self_count','self_categories','q','pads','wrist']}
def inspect_original():
 rows=[]
 for t in [3.35,A,3.67,3.708333333333333,3.74,H,3.82,3.88,3.95,B,4.08]:
  c.settime(sc,t);r,V,L=measure(t);rows.append(r)
 save('R2_FOCUSED_ORIGINAL_SURVEY.json',dict(rows=rows))
 r4=[]
 for tag in ['R10','R11']:
  snap=read(R4/f'{tag}_ROUND_1_NOT_APPROVED_POSE.json');c.settime(sc,snap['time']);original=np.array(<REDACTED_EMAIL>['WRIST_R'].matrix)
  for name,p in snap['pose'].items():
   b=rig.pose.bones[name];b.location=p['location'];b.rotation_quaternion=p['quaternion'];b.scale=p['scale']
  bpy.context.view_layer.update();r,V,L=measure(snap['time'])
  assert not r['illegal'] and not r['self_count'] and all(a['pass_'] for a in r['contacts'])
  r4.append(dict(tag=tag,time=snap['time'],original_wrist_world=original,static_wrist_world=r['wrist'],wrist_local_basis=r['wrist_basis'],rig_world=r['rig_world'],world_offset_mm=(r['wrist'][:3,3]-original[:3,3])*1000,validation=r))
 a,b=r4;dw=b['static_wrist_world'][:3,3]-a['static_wrist_world'][:3,3]
 save('R4_WORLD_TRANSFORM_RECHECK.json',dict(rows=r4,world_delta_mm=dw*1000,distance_mm=float(np.linalg.norm(dw)*1000),definition='WRIST_R pose matrix maps bone local to armature object space; rig.matrix_world @ pose_bone.matrix gives world matrix. Translation column is wrist head origin. matrix_basis is local pose relative to rest/parent; rig.matrix_world carries original animated hand placement. R4 offsets were WORLD translations. Two different event times: not a required displacement or motion prescription.',not_approved_reference_only=True))
 c.settime(sc,3.67)
 print('R5_ORIGINAL_AND_R4_RECHECK',json.dumps([short(r) for r in rows],default=encode),flush=True)
print('R5_DYNAMIC_SESSION_INITIALIZED',flush=True)
