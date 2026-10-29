import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
facts=read(OUT/'BASELINE_FACTS.json');prior=np.load(OUT/'BASELINE_STATIC.npz');B=prior['V'];BL=prior['left']
sc,rig,mesh,left,lrig=s.open_scene(OUT/'ROUND_3_STATIC_NOT_APPROVED.blend');c.settime(sc,2.6);g.init()
V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left);diff=np.linalg.norm(V-B,axis=1);changed=np.flatnonzero(diff>1e-10)
CT=g.ALLT[np.any(np.isin(g.ALLT,np.union1d(g.IDS,changed)),axis=1)];g.IT=CT
extract(OUT/'artist_tools.py',['segment_distance','edges','exact_clearance','selfpairs'],globals())
keys=g.keycheck(V);base=g.keycheck(B)
for row in keys:
 cs=[co for co in g.comps if co[0]['key_index']==row['key_index']]
 row['exact_surface_clearance_mm']=0. if row['depth_mm']>1e-6 else min(exact_clearance(V,CT,g.actual(co)[0],co[4]) for co in cs)
bp=selfpairs(B,CT);cp=selfpairs(V,CT)
assert facts['native']=={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',mesh,rig),('L',left,lrig)]}
assert np.array_equal(np.array(rig.matrix_world),np.array(facts['root_world']))
paths={f'pose.bones["{n}"].rotation_quaternion' for n in c.SETUPS['R','INDEX'][0]}
assert c.digest(s.payload(rig.animation_data.action,paths))==facts['unedited_rig_digest']
others=s.protected_state(True);before={k:v for k,v in facts['protected_actions'].items() if k!=rig.name};assert others==before
allcontacts=[]
for n in NOTES:
 if n['note_on']<=2.6<n['note_off']:
  coords=V if n['hand']=='R' else L;orig=B if n['hand']=='R' else BL
  allcontacts.append(dict(note=n['note_id'],hand=n['hand'],finger=n['finger'],key=n['note_name'],baseline=s.contact(orig,KEYS[n['key_index']],n['hand'],n['finger']),candidate=s.contact(coords,KEYS[n['key_index']],n['hand'],n['finger'])))
P=V[np.unique(CT)];crossgap=float(np.linalg.norm(np.maximum(0,np.maximum(P.min(0)-L.max(0),L.min(0)-P.max(0))))*1000)
if crossgap==0:
 bpL=set(g.tree(B,CT).overlap(g.tree(L,LT)));cpL=set(g.tree(V,CT).overlap(g.tree(L,LT)));newcross=len(cpL-bpL)
else:newcross=0
from bpy_extras.object_utils import world_to_camera_view
projections=[]
for kind in ['OVERHEAD','SIDE_OBLIQUE','ARTIST_AUX_INDEX_SIDE']:
 cam=bpy.data.objects[MAN['cameras'][kind]] if kind in MAN['cameras'] else bpy.data.objects[kind]
 def project(point):
  p=world_to_camera_view(sc,cam,Vector(point));return [p.x*1280,(1-p.y)*720]
 witnesses=[]
 for identity,rows in [('ORIGINAL',base),('ROUND_3',keys)]:
  for row in rows:
   if row['depth_mm']>1e-6 and row['certificate']:
    p=row['certificate']['witness_world_m'];witnesses.append(dict(identity=identity,key=row['key'],depth_mm=float(row['depth_mm']),pixel=project(p),world_m=p,triangle=row['certificate']['triangle']))
 projections.append(dict(view=kind,camera=cam.name,matrix=np.array(cam.matrix_world),scale=cam.data.ortho_scale,witnesses=witnesses))
q=s.degrees('INDEX');bd=np.array(facts['bounds_deg']);originalkeydict={r['key']:r for r in base};newkeys=[r for r in keys if r['depth_mm']>1e-6 and originalkeydict.get(r['key'],{}).get('depth_mm',0)<=1e-6]
out=dict(time=2.6,candidate=str(OUT/'ROUND_3_STATIC_NOT_APPROVED.blend'),qdeg=q,keys=keys,baseline_keys=base,new_key_identities=[r['key'] for r in newkeys],new_self_pairs=sorted(cp-bp),new_cross_hand_pairs=newcross,cross_hand_changed_region_aabb_separation_mm=crossgap,all_active_contacts_at_2_6=allcontacts,thumb_pad_shift_mm=float(np.linalg.norm(V[2963]-B[2963])*1000),other_digit_skin_max_mm={d:float((diff[ROI[d]['vertices']]*1000).max()) for d in DIGITS},q_bounds_deg=bd,strict_q_in_bounds=bool(np.all(q>=bd[0]) and np.all(q<=bd[1])),native_unchanged=True,protected_actions_unchanged=True,other_finger_action_payload_unchanged=True,left_skin_max_delta_mm=float(np.linalg.norm(L-BL,axis=1).max()*1000),projections=projections,saved_vs_live_q_error_deg=float(np.max(abs(q-read(OUT/'ROUND_3_STATIC_CHECK.json')['qdeg']))),saved_vs_live_skin_error_mm=float(np.linalg.norm(V-np.load(OUT/'ROUND_3_STATIC.npz')['V'],axis=1).max()*1000),phase2_executed=False,temporal_sampling='NOT_RUN: static gate failed; exactly one time t=2.600000s. No continuous-time safety claim.')
save('SAVED_REOPEN_STATIC_VALIDATION.json',out);protection('REOPEN_INPUT_RECEIPT.json')
print('REOPEN_RESULT',json.dumps(dict(depth_mm=max(r['depth_mm'] for r in keys),new_keys=out['new_key_identities'],new_self=len(cp-bp),legal=out['strict_q_in_bounds'],saved_pose_error=out['saved_vs_live_q_error_deg'],saved_skin_error=out['saved_vs_live_skin_error_mm'],thumb_shift=out['thumb_pad_shift_mm']),ensure_ascii=False),flush=True)
