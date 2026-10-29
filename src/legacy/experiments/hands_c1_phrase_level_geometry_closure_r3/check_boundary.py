import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1';R2=ROOT/'experiments/hands_c1_exit_handoff_correction_r2'
extract(R1/'validate_full.py',['collision','selfpairs'],globals())
sc,rig,mesh,left,lrig=s.open_scene(OUT/'R2_START_ISOLATED_NOT_APPROVED.blend');g.init()
bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
# Reuse already verified R2 context; extend only the handoff search.
prior=read(R2/'CANDIDATE_2_VALIDATION.json');old=[r for r in prior['rows'] if r['time']>=3.02]
times=list(np.arange(804,913)/240)+[3.349997,3.5642825,3.778568,3.8]
for t in [3.349997,3.5642825,3.778568]:times.extend(x for x in np.arange(t-.00625,t+.006251,1/960) if 3.35<=x<=3.8)
times=sorted(set(float(t) for t in times if 3.349997<=t<=3.8))
def label(vi):
 groups=mesh.data.vertices[int(vi)].groups
 return max([(mesh.vertex_groups[a.group].name.split('_')[0],a.weight) for a in groups],key=lambda x:x[1])[0]
def tri_label(ids):
 labs=[label(i) for i in ids];return max(set(labs),key=labs.count)
rows=[];begin=time.perf_counter()
for ix,t in enumerate(times):
 c.settime(sc,t);V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left);keys=collision(V)
 active=[n for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
 illegal={k:v for k,v in keys.items() if k not in [n['note_name'] for n in active] and (v['depth_mm']>1e-6 or v['pairs'])}
 sp=selfpairs(V);pair_labels={}
 for a,b in sp:
  key='/'.join(sorted([tri_label(T[a]),tri_label(T[b])]))
  pair_labels[key]=pair_labels.get(key,0)+1
 q=np.array([s.degrees(d) for d in DIGITS]);contacts=[dict(event=n['note_id'],key=n['note_name'],**s.contact(V,KEYS[n['key_index']],'R',n['finger'])) for n in active]
 rows.append(dict(time=t,illegal=illegal,self_count=len(sp),self_categories=pair_labels,self_examples=[dict(triangles=[a,b],vertices=[T[a],T[b]]) for a,b in sorted(sp)[:5]],active_contacts=contacts,joint_violation_deg=float(max(0,np.max(bounds[:,0]-q),np.max(q-bounds[:,1]))),safe_existing_handoff=not illegal and not sp and all(r['pass_'] for r in contacts)))
 if ix%40==0:print('BOUNDARY_EXTENSION',ix,len(times),round(time.perf_counter()-begin,1),flush=True)
contacts=[]
for n in [n for n in NOTES if n['hand']=='R']:
 for phase,t in [('ON',n['note_on']),('HOLD',(n['note_on']+n['note_off'])/2),('PRE_OFF',n['note_off']-.001)]:
  c.settime(sc,t);V,T,F=s.coords_tri(mesh);contacts.append(dict(event=n['note_id'],phase=phase,time=t,**s.contact(V,KEYS[n['key_index']],'R',n['finger'])))
roles=[]
for t in [2.1,2.92,3.02,3.30,3.349997,3.50,3.5642825,3.70,3.778568,3.8]:
 row={'time':t,'digits':{}}
 for di,d in enumerate(DIGITS):
  events=[n for n in NOTES if n['hand']=='R' and n['finger']==di+1]
  a=next((n for n in events if n['note_on']<=t<n['note_off']),None)
  release=next((n for n in events if n['note_off']<=t<n['note_off']+.04),None)
  prep=next((n for n in events if n['note_on']-.18<=t<n['note_on']),None)
  row['digits'][d]=dict(role='ACTIVE' if a else 'RELEASE' if release else 'PREPARE' if prep else 'IDLE',event=(a or release or prep or {}).get('note_id'))
 roles.append(row)
save('DENSE_HANDOFF_BOUNDARY_CHECK.json',dict(existing_R2_context_reused=dict(samples=len(old),start=old[0]['time'],end=old[-1]['time'],safe_key_samples=sum(not r['illegal'] for r in old)),extension_rows=rows,extension_samples=len(rows),extension_safe_handoff_samples=sum(r['safe_existing_handoff'] for r in rows),extension_illegal_samples=sum(bool(r['illegal']) for r in rows),self_intersection_samples=sum(r['self_count']>0 for r in rows),max_self_pairs=max(r['self_count'] for r in rows),contacts48=contacts,contacts48_pass=sum(r['pass_'] for r in contacts),roles=roles,role_convention='ACTIVE exact formal ON/OFF; existing40ms RELEASE and180ms PREPARE conventions; overlaps reported with ACTIVE priority. No note time edits.',limit=3.8,finite_sampling_only=True))
# Diagnostic images only; no new animation/video has been designed or rendered.
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for t,tag in [(3.349997,'C5_ON'),(3.5642825,'D5_ON'),(3.778568,'E5_ON'),(3.8,'LIMIT')]:
 c.settime(sc,t)
 for kind in ['OVERHEAD','SIDE_OBLIQUE']:
  sc.camera=bpy.data.objects[MAN['cameras'][kind]];sc.render.filepath=str(OUT/f'BOUNDARY_{tag}_{kind}.png');bpy.ops.render.render(write_still=True)
protection('BOUNDARY_CHECK_INPUT_RECEIPT.json');print('BOUNDARY_CHECK_COMPLETE',len(rows),sum(r['safe_existing_handoff'] for r in rows),flush=True)
