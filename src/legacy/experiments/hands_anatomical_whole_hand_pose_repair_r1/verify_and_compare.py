import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
facts=read(OUT/'BASELINE_FACTS.json');best=read(OUT/'ROUND_2_DATA.json');prior=np.load(OUT/'BASELINE_STATIC.npz');B=prior['V'];BL=prior['L']
extract(ROOT/'experiments/hands_blender_artist_pose_repair_poc_r1/artist_tools.py',['segment_distance','edges','exact_clearance'],globals())
def self_full(V,T):
 pairs=g.tree(V,T).overlap(g.tree(V,T));out=set()
 for i,j in pairs:
  if i<j and not(set(T[i])&set(T[j])):out.add((int(i),int(j)))
 return out
def get_metrics():
 V,T,F=s.coords_tri(s.mesh);L,LT,LF=s.coords_tri(s.left);rows=g.keycheck(V,all_hand=True)
 for row in rows:
  comps=[co for co in g.comps if co[0]['key_index']==row['key_index']]
  row['exact_clearance_mm']=0 if row['depth_mm']>1e-6 else min(exact_clearance(V,T,g.actual(co)[0],co[4]) for co in comps)
 contacts=[]
 for n in NOTES:
  if n['note_on']<=2.6<n['note_off']:contacts.append(dict(hand=n['hand'],finger=n['finger'],key=n['note_name'],contact=s.contact(V if n['hand']=='R' else L,KEYS[n['key_index']],n['hand'],n['finger'])))
 return V,T,L,LT,rows,contacts
sc,rig,mesh,left,lrig=s.open_scene(OUT/'ROUND_2_STATIC_NOT_APPROVED.blend');c.settime(sc,2.6);g.init();V,T,L,LT,rows,contacts=get_metrics()
assert facts['native']=={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',mesh,rig),('L',left,lrig)]}
paths={f'pose.bones["{n}"].rotation_quaternion' for n in c.SETUPS['R','INDEX'][0]};paths.update({f'pose.bones["WRIST_R"].{prop}' for prop in ['location','rotation_quaternion']})
original_rig=next(v for k,v in facts['actions'].items() if k==rig.name)
# Compare all animation paths outside the specifically authorized static edits.
saved_rig_unedited=c.digest(s.payload(rig.animation_data.action,paths));saved_other_actions=s.protected_state(True)
actual_self=self_full(V,T);base_self=set(map(tuple,facts['baseline_self_pairs']))
crossnew=set(g.tree(V,T).overlap(g.tree(L,LT)))-set(g.tree(B,T).overlap(g.tree(BL,LT)))
q=np.array([s.degrees(d) for d in DIGITS]);bd=np.array(facts['bounds_deg']);axis_residual=[]
for i,d in enumerate(DIGITS):
 for name,M in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(q[i]))):
  actual=rig.pose.bones[name].rotation_quaternion.normalized();reconstructed=Matrix(M.tolist()).to_quaternion();axis_residual.append(dict(bone=name,error_deg=math.degrees(actual.rotation_difference(reconstructed).angle)))
loaded=np.load(OUT/'ROUND_2_STATIC.npz');skin_error=float(np.linalg.norm(V-loaded['V'],axis=1).max()*1000);joint_error=float(np.max(abs(q-loaded['q'])))
assert skin_error==0 and joint_error==0
assert all(r['contact']['pass_'] for r in contacts)
illegal=[r for r in rows if r['key']!='G4' and (r['bvh_pairs'] or r['depth_mm']>1e-6)]
assert not illegal and not(actual_self-base_self) and not crossnew
assert np.all(q>=bd[:,0]) and np.all(q<=bd[:,1])
np.savez_compressed(OUT/'REOPENED_BEST_STATIC.npz',V=V,L=L,q=q,T=T)
result=dict(machine_static_geometry_pass=True,keys=rows,active_contacts=contacts,new_self_pairs=sorted(actual_self-base_self),new_cross_hand_pairs=sorted(crossnew),qdeg={d:q[i] for i,d in enumerate(DIGITS)},joint_domain_pass=True,axis_reconstruction_errors=axis_residual,saved_live_skin_error_mm=skin_error,saved_live_joint_error_deg=joint_error,native_unchanged=True,left_skin_error_mm=float(np.linalg.norm(L-BL,axis=1).max()*1000),candidate_sha256=sha(OUT/'ROUND_2_STATIC_NOT_APPROVED.blend'),sample_time=2.6,time_samples=1,animation_not_run=True,human_approval=False)
# Render old rejected and current with EXACT same auxiliary and original cameras.
from bpy_extras.object_utils import world_to_camera_view
projection_rows=[]
for identity,path in [('ORIGINAL',SOURCE),('PREVIOUS_REJECTED',ROOT/'experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_3_STATIC_NOT_APPROVED.blend'),('CURRENT_BEST',OUT/'ROUND_2_STATIC_NOT_APPROVED.blend')]:
 sc,rig,mesh,left,lrig=s.open_scene(path);c.settime(sc,2.6);g.init()
 if identity=='ORIGINAL':
  assert c.digest(s.payload(rig.animation_data.action,paths))==saved_rig_unedited
  assert s.protected_state(True)==saved_other_actions
  result['all_unedited_action_payloads_unchanged']=True
 for view in facts['views']:
  kind=view['view'];name=view['camera']
  if name not in bpy.data.objects:
   cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam)
  cam=bpy.data.objects[name];cam.matrix_world=Matrix(view['matrix']);cam.data.type=view['type'];cam.data.ortho_scale=view['scale'];cam.data.lens=view['lens'];sc.camera=cam
  sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
  dst=OUT/f'{identity}_{kind}_MATCHED.png';assert not dst.exists();sc.render.filepath=str(dst);bpy.ops.render.render(write_still=True)
  projection_rows.append(dict(identity=identity,view=kind,path=str(dst),camera_matrix=np.array(cam.matrix_world),type=cam.data.type,scale=cam.data.ortho_scale))
save('MATCHED_CAMERA_RENDER_MANIFEST.json',projection_rows)
save('SAVED_REOPEN_MACHINE_VALIDATION.json',result);protection('REOPEN_COMPARISON_INPUT_RECEIPT.json')
print('SAVED_VERIFICATION_PASS',dict(skin_error=skin_error,joint_error=joint_error,illegal=0,newself=0,contacts=contacts),flush=True)
