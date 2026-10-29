from geometry import *
import geometry as g
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1'
sc,rig,mesh,left,lrig=s.open_scene(OUT/'R1_START_ISOLATED_NOT_APPROVED.blend');g.init()
assert sha(R1/'DYNAMIC_CANDIDATE_NOT_APPROVED.blend')==sha(OUT/'R1_START_ISOLATED_NOT_APPROVED.blend')=='0afd1b6a0997b62dd0311f61ce44add5a8e0147d441a29556f51dc6bd7993cad'
protected={r['path']:r['before'] for r in read(R1/'PROTECTED_INPUTS_SHA256_BEFORE_AFTER.json')['files']}
for p in sorted(R1.rglob('*')):
 safe(p)
 if p.is_file():protected[str(p)]=sha(p)
for p,h in protected.items():assert sha(p)==h
if not (OUT/'PROTECTED_BEFORE.json').exists():save('PROTECTED_BEFORE.json',dict(files=[dict(path=p,sha256=h) for p,h in protected.items()],R1_all_files_frozen=True))
OLD_ACTION=rig.animation_data.action
OLD_PAYLOAD=s.payload(OLD_ACTION)
NATIVE={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
OTHER_ACTIONS=s.protected_state(True)
extract(R1/'validate_full.py',['collision'],globals())
rows=[]
for t in [2.78,2.8875,2.90,2.92,2.921426,2.95,3.0416666666666665,3.066666666666667,3.10,3.11375,3.12]:
 c.settime(sc,t);V,T,F=s.coords_tri(mesh);cols=collision(V)
 facts=[]
 for key in ['A4','A#4','C#5']:
  r=cols.get(key)
  if r and r['witness']:
   ids=r['witness']['vertices'];facts.append(dict(key=key,depth_mm=r['depth_mm'],pairs=r['pairs'],witness=r['witness'],weights={str(int(i)):[dict(bone=mesh.vertex_groups[a.group].name,weight=a.weight) for a in mesh.data.vertices[int(i)].groups if a.weight>.001] for i in ids}))
 rows.append(dict(time=t,keys=facts,qdeg={d:s.degrees(d) for d in ['INDEX','MIDDLE']},wrist_location=list(rig.pose.bones['WRIST_R'].location),wrist_quaternion=list(rig.pose.bones['WRIST_R'].rotation_quaternion),active=[dict(id=n['note_id'],key=n['note_name'],finger=n['finger'],contact=s.contact(V,KEYS[n['key_index']],'R',n['finger'])) for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]))
data=np.load(R1/'CANDIDATE_2_FIXED_DENSE.npz');q=data['Q'];times=data['times'];bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
viol=[]
for i,t in enumerate(times):
 for di,d in enumerate(DIGITS):
  for j in range(4):
   v=q[i,di,j]
   if v<bounds[di,0,j]-1e-5 or v>bounds[di,1,j]+1e-5:viol.append(dict(time=float(t),digit=d,joint=['MCP' if d!='THUMB' else 'CMC','PIP' if d!='THUMB' else 'MCP','DIP' if d!='THUMB' else 'IP','SPREAD'][j],value_deg=v,low=bounds[di,0,j],high=bounds[di,1,j]))
handles=[dict(path=f.data_path,index=f.array_index,points=[dict(time=(float(k.co.x)-1)/60,co=list(k.co),left=list(k.handle_left),right=list(k.handle_right),interpolation=k.interpolation,lt=k.handle_left_type,rt=k.handle_right_type) for k in f.keyframe_points if 1+60*2.68-.001<=k.co.x<=1+60*3.12+.001]) for f in s.curves(OLD_ACTION) if any(n in f.data_path for n in ['MIDDLE_MCP_R','INDEX','WRIST_R'])]
if not (OUT/'EXIT_DIAGNOSIS.json').exists():save('EXIT_DIAGNOSIS.json',dict(samples=rows,joint_violations=viol,curves=handles,events=[n for n in NOTES if 2.1<n['note_on']<3.35 or 2.1<n['note_off']<3.35],native=NATIVE,other_actions=OTHER_ACTIONS))
if not (OUT/'DIAGNOSIS_INPUT_RECEIPT.json').exists():protection('DIAGNOSIS_INPUT_RECEIPT.json')
print('DIAGNOSIS_READY',json.dumps(dict(collisions=[dict(time=r['time'],keys=[(k['key'],k['depth_mm'],k['witness']['vertices'].tolist()) for k in r['keys']]) for r in rows],violations=len(viol),violation_peak=min(viol,key=lambda x:x['value_deg']) if viol else None),ensure_ascii=False,default=encode),flush=True)
