import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
begin=time.perf_counter();policy=read(OUT/'STRATEGY_AND_ENVELOPE.json');bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
times=list(np.arange(0,1.35+1e-8,1/240))+list(np.arange(2.1,3.35+1e-8,1/240))
boundary=[0.,.18,.812856-.04,.812856,.992856,1.207142,1.247142,1.35,2.1,2.28,3.2,3.35,26/60,2.6]
for n in NOTES:
 for t in [n['note_on']-.18,n['note_on'],n['note_off'],n['note_off']+.04]:
  if 0<=t<=1.35 or 2.1<=t<=3.35:boundary.append(t)
for t in boundary:
 times.extend(x for x in np.arange(t-.0125,t+.01251,1/960) if 0<=x<=1.35 or 2.1<=x<=3.35)
times=np.unique(np.round(np.r_[times,boundary],12));times=times[((times>=0)&(times<=1.35))|((times>=2.1)&(times<=3.35))]
rn=[n for n in NOTES if n['hand']=='R'];contact_times=[(n,phase,t) for n in rn for phase,t in [('ON',n['note_on']),('HOLD',(n['note_on']+n['note_off'])/2),('PRE_OFF',n['note_off']-.001)]]
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);g.init();baseV=[];baseQ=[];baseW=[];base_contacts=[]
for t in times:
 c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);baseV.append(V);baseQ.append([s.degrees(d) for d in DIGITS]);baseW.append(np.array(rig.matrix_world))
for n,phase,t in contact_times:
 c.settime(sc,t);V,T,F=s.coords_tri(mesh);base_contacts.append(dict(time=t,event=n['note_id'],phase=phase,contact=s.contact(V,KEYS[n['key_index']],'R',n['finger']),V=V))
baseV=np.array(baseV);baseQ=np.array(baseQ);print('BASELINE_CAPTURE',len(times),flush=True)
np.savez_compressed(OUT/'BASELINE_LOCAL_SAMPLES.npz',times=times,vertices=baseV,qdeg=baseQ,palm=baseW)
sc,rig,mesh,left,lrig=s.open_scene(OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend');g.init()
paths={f'pose.bones["{name}"].rotation_quaternion' for name in c.SETUPS['R','INDEX'][0]}
assert c.digest(s.payload(rig.animation_data.action,paths))==policy['outside_index_action_digest']
assert s.protected_state(True)==policy['protected_actions']
assert policy['native']=={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
def collision(V,T):
 if len(T)==0:return {}
 tr=V[T];lo=tr.min(1);hi=tr.max(1);skin=g.tree(V,T);out={}
 for comp in g.comps:
  kv,P=g.actual(comp);mask=np.all(hi>=kv.min(0),axis=1)&np.all(lo<=kv.max(0),axis=1)
  if not mask.any():continue
  kt=g.tree(kv,comp[4]);pairs=skin.overlap(kt);peak=0.;cert=None
  for j in np.flatnonzero(mask):
   rr=g.dm.max_triangle_depth(tr[j],P)
   if rr['upper_mm']>peak:peak=float(rr['upper_mm']);cert=dict(triangle=T[j],**rr)
  name=comp[0]['note_name'];prev=out.get(name,dict(depth_mm=0.,bvh_pairs=0,certificate=None,color=comp[0]['color']))
  if peak>prev['depth_mm']:prev.update(depth_mm=peak,certificate=cert)
  prev['bvh_pairs']+=len(pairs);out[name]=prev
 return out
def selfpairs(V,changed):
 ids=np.flatnonzero(np.any(np.isin(g.ALLT,changed),axis=1));T=g.ALLT[ids]
 if not len(T):return set()
 pairs=g.tree(V,T).overlap(g.tree(V,g.ALLT));out=set()
 for i,j in pairs:
  a=int(ids[i]);b=int(j)
  if a==b or np.intersect1d(g.ALLT[a],g.ALLT[b]).size:continue
  out.add(tuple(sorted((a,b))))
 return out
rows=[];candQ=[];changed_max=np.zeros(baseV.shape[1]);newkey=[];newself=[];limits=[];candV=[]
for i,t in enumerate(times):
 c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);B=baseV[i];change=np.linalg.norm(V-B,axis=1);changed=np.flatnonzero(change>1e-10);changed_max=np.maximum(changed_max,change);candV.append(V)
 # Full INDEX ROI plus every triangle with any actually changed vertex, including blended seams.
 tri=g.ALLT[np.any(np.isin(g.ALLT,np.union1d(g.IDS,changed)),axis=1)]
 bc=collision(B,tri);cc=collision(V,tri);bp=selfpairs(B,changed);cp=selfpairs(V,changed)
 nk=[dict(key=k,baseline_mm=bc.get(k,{}).get('depth_mm',0),candidate_mm=v['depth_mm']) for k,v in cc.items() if v['depth_mm']>1e-5 and v['depth_mm']>bc.get(k,{}).get('depth_mm',0)+1e-4]
 ns=sorted(cp-bp)
 q=np.array([s.degrees(d) for d in DIGITS]);candQ.append(q)
 bv=np.maximum(bounds[:,0]-baseQ[i],baseQ[i]-bounds[:,1]);cv=np.maximum(bounds[:,0]-q,q-bounds[:,1]);worse=np.argwhere(cv>np.maximum(1e-4,bv+1e-4))
 if len(worse):limits.append(dict(time=t,indices=worse,baseline=baseQ[i],candidate=q))
 row=dict(time=t,baseline_keys=bc,candidate_keys=cc,new_or_worse_key_collisions=nk,baseline_self_pairs=len(bp),candidate_self_pairs=len(cp),new_self_pair_count=len(ns),new_self_examples=ns[:10],changed_vertex_count=len(changed),palm_delta=float(np.max(abs(np.array(rig.matrix_world)-baseW[i]))))
 rows.append(row)
 if nk:newkey.append(dict(time=t,collisions=nk))
 if ns:newself.append(dict(time=t,count=len(ns),examples=ns[:10]))
 if i%100==0:print('VALIDATE',i,'/',len(times),'seconds',round(time.perf_counter()-begin,1),flush=True)
contacts=[]
for (n,phase,t),b in zip(contact_times,base_contacts):
 c.settime(sc,t);V,T,F=s.coords_tri(mesh);cc=s.contact(V,KEYS[n['key_index']],'R',n['finger'])
 contacts.append(dict(time=t,event=n['note_id'],note=n['note_name'],finger=n['finger'],phase=phase,baseline=b['contact'],candidate=cc,pad_shift_mm=float(np.linalg.norm(V[cc['vertex']]-b['V'][cc['vertex']])*1000),other_digit_max_mm={d:float(np.max(np.linalg.norm(V[ROI[d]['vertices']]-b['V'][ROI[d]['vertices']],axis=1))*1000) for d in DIGITS if d!='INDEX'}))
candQ=np.array(candQ);np.savez_compressed(OUT/'CANDIDATE_LOCAL_SAMPLES.npz',times=times,vertices=np.array(candV),qdeg=candQ)
def window(a,b):
 rr=[r for r in rows if a-1e-9<=r['time']<=b+1e-9]
 def peak(which,color=None):
  items=[dict(time=r['time'],key=k,**{x:v[x] for x in ['depth_mm','bvh_pairs']}) for r in rr for k,v in r[which].items() if color is None or v['color']==color]
  return max(items,key=lambda x:x['depth_mm']) if items else None
 return dict(range=[a,b],samples=len(rr),maximum_step_sec=float(max(np.diff([r['time'] for r in rr]))),baseline_peak=peak('baseline_keys'),candidate_peak=peak('candidate_keys'),baseline_black_peak=peak('baseline_keys','BLACK'),candidate_black_peak=peak('candidate_keys','BLACK'),new_or_worse_key_samples=sum(bool(r['new_or_worse_key_collisions']) for r in rr),new_self_pair_samples=sum(r['new_self_pair_count']>0 for r in rr))
deltaq=candQ-baseQ;dt=np.diff(times);valid=(dt>1e-7)&(dt<.01);vel=np.diff(deltaq[:,1,:3],axis=0)[valid]/dt[valid,None]
save('DENSE_GEOMETRY_AND_REGRESSION.json',dict(times=times,sampling='240Hz plus exact event/role boundaries and 960Hz +/-12.5ms near listed high-risk times; actual evaluated skin and Action-driven actual key meshes',rows=rows,new_key_samples=newkey,new_self_samples=newself,new_limit_violations=limits,windows=[window(.35,.8),window(2.45,2.9),window(0,1.35),window(2.1,3.35)],contacts=contacts,joint_summary=dict(baseline_min=baseQ.min(0),baseline_max=baseQ.max(0),candidate_min=candQ.min(0),candidate_max=candQ.max(0),max_added_joint_speed_deg_s=np.max(abs(vel),axis=0)),actual_changed_vertex_ids=np.flatnonzero(changed_max>1e-10),other_vertex_unchanged=True,all_palm_unchanged=all(r['palm_delta']==0 for r in rows),protected_actions_unchanged=True,rest_skinning_correctives_unchanged=True,notes_clock_unchanged=len(NOTES)==23,elapsed_sec=time.perf_counter()-begin))
protection('VALIDATION_INPUT_RECEIPT.json')
print('VALIDATION_DONE',json.dumps(dict(windows=[window(.35,.8),window(2.45,2.9)],contacts_pass=sum(r['candidate']['pass_'] for r in contacts),newkey_samples=len(newkey),newself_samples=len(newself),new_limit_violations=len(limits)),ensure_ascii=False),flush=True)
