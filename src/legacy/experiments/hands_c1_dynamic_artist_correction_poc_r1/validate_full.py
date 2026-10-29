import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
begin=time.perf_counter()
ledger=read(OUT/'CANDIDATE_2_FIXED_EDIT_LEDGER.json')
critical=ledger['times']+[2.45,2.6,2.92]+[n[x] for n in NOTES for x in ['note_on','note_off'] if 2.1<=n[x]<=3.35]
times=list(np.arange(504,805)/240)+[2.1,3.35]
times+=[v for t in critical for v in np.arange(t-.00625,t+.006251,1/960) if 2.1<=v<=3.35]
times+=list(np.arange(2.875,2.926,1/960))+critical
times=sorted(times);times=[t for i,t in enumerate(times) if i==0 or t-times[i-1]>1e-9]
# Insert exact event/pose values, rather than rounded neighbors.
for t in critical:
 times=[x for x in times if abs(x-t)>1e-9]+[t]
times=np.array(sorted(times))
rn=[n for n in NOTES if n['hand']=='R']
contact_times=[(n,phase,t) for n in rn for phase,t in [('ON',n['note_on']),('HOLD',(n['note_on']+n['note_off'])/2),('PRE_OFF',n['note_off']-.001)]]
bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
def selfpairs(V):
 return {(int(i),int(j)) for i,j in g.tree(V,g.ALLT).overlap(g.tree(V,g.ALLT)) if i<j and not set(g.ALLT[i])&set(g.ALLT[j])}
def collision(V):
 tr=V[g.ALLT];lo=tr.min(1);hi=tr.max(1);skin=g.tree(V,g.ALLT);out={}
 for co in g.comps:
  kv,P=g.actual(co);mask=np.all(hi>=kv.min(0),axis=1)&np.all(lo<=kv.max(0),axis=1)
  if not mask.any():continue
  pairs=skin.overlap(g.tree(kv,co[4]));peak=0.;witness=None
  for j in np.flatnonzero(mask):
   r=g.dm.max_triangle_depth(tr[j],P)
   if r['upper_mm']>peak:peak=float(r['upper_mm']);witness=dict(vertices=g.ALLT[j],point=r['witness_world_m'])
  key=co[0]['note_name'];old=out.setdefault(key,dict(depth_mm=0.,pairs=0,witness=None))
  old['pairs']+=len(pairs)
  if peak>old['depth_mm']:old.update(depth_mm=peak,witness=witness)
 return out
def capture_contacts():
 out=[]
 for n,phase,t in contact_times:
  c.settime(sc,t);V,T,F=s.coords_tri(mesh)
  out.append(dict(event=n['note_id'],key=n['note_name'],finger=n['finger'],phase=phase,time=t,**s.contact(V,KEYS[n['key_index']],'R',n['finger'])))
 return out
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);g.init()
native={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
actions=s.protected_state(True);outside_rig=c.digest(s.payload(rig.animation_data.action,set(ledger['edited_paths'])))
baseV=[];baseL=[];baseQ=[];baseW=[];baseCols=[];baseSelf=[];baseCross=[];baseContacts=capture_contacts()
original_curves={(f.data_path,f.array_index):f for f in s.curves(rig.animation_data.action)}
outside_times=[0.,.35,1.,2.099,2.1999,3.1201,3.35,4.,5.5]
outside_vals={t:{p:[f.evaluate(1+60*t) for (path,i),f in sorted(original_curves.items()) if path==p] for p in ledger['edited_paths'] if 'WRIST_R' not in p} for t in outside_times}
for ix,t in enumerate(times):
 c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left)
 baseV.append(V);baseL.append(L);baseQ.append([s.degrees(d) for d in DIGITS]);baseW.append(np.array(<REDACTED_EMAIL>['WRIST_R'].matrix))
 baseCols.append(collision(V));baseSelf.append(selfpairs(V));baseCross.append(set(g.tree(V,T).overlap(g.tree(L,LT))))
 if ix%50==0:print('BASELINE',ix,len(times),'sec',round(time.perf_counter()-begin,1),flush=True)
baseV=np.array(baseV);baseL=np.array(baseL);baseQ=np.array(baseQ);baseW=np.array(baseW)
np.savez_compressed(OUT/'BASELINE_DENSE.npz',times=times,V=baseV,L=baseL,Q=baseQ,W=baseW)
save('BASELINE_DENSE_GEOMETRY.json',dict(times=times,collisions=baseCols,self_counts=[len(x) for x in baseSelf],cross_counts=[len(x) for x in baseCross],contacts48=baseContacts))
for number in [1,2]:
 tag=f'CANDIDATE_{number}_FIXED';path=OUT/f'CANDIDATE_{number}_IMPLEMENTATION_FIXED_NOT_APPROVED.blend'
 sc,rig,mesh,left,lrig=s.open_scene(path);g.init()
 assert native=={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
 assert actions==s.protected_state(True)
 assert outside_rig==c.digest(s.payload(rig.animation_data.action,set(ledger['edited_paths'])))
 candidate_curves={(f.data_path,f.array_index):f for f in s.curves(rig.animation_data.action)}
 outside_error=max(abs(candidate_curves[p,i].evaluate(1+60*t)-v) for t,ps in outside_vals.items() for p,vs in ps.items() for i,v in enumerate(vs))
 contacts=capture_contacts();rows=[];cv=[];cq=[];cw=[]
 for ix,t in enumerate(times):
  c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left);Q=np.array([s.degrees(d) for d in DIGITS]);W=np.array(<REDACTED_EMAIL>['WRIST_R'].matrix)
  cc=collision(V);active={n['note_name'] for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']}
  illegal={k:v for k,v in cc.items() if k not in active and (v['depth_mm']>1e-6 or v['pairs'])}
  regress={k:dict(baseline_mm=baseCols[ix].get(k,{}).get('depth_mm',0),candidate_mm=v['depth_mm'],active=k in active) for k,v in cc.items() if v['depth_mm']>baseCols[ix].get(k,{}).get('depth_mm',0)+.02}
  cp=selfpairs(V);cross=set(g.tree(V,T).overlap(g.tree(L,LT)))
  activecontacts=[dict(event=n['note_id'],key=n['note_name'],**s.contact(V,KEYS[n['key_index']],'R',n['finger'])) for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
  rows.append(dict(time=t,active_keys=sorted(active),keys=cc,illegal=illegal,regressions=regress,new_self=sorted(cp-baseSelf[ix]),self_count=len(cp),new_cross=sorted(cross-baseCross[ix]),left_delta_mm=float(np.max(np.linalg.norm(L-baseL[ix],axis=1)))*1000,contacts=activecontacts,domain_violation_deg=float(max(0,np.max(bounds[:,0]-Q),np.max(Q-bounds[:,1]))),baseline_domain_violation_deg=float(max(0,np.max(bounds[:,0]-baseQ[ix]),np.max(baseQ[ix]-bounds[:,1])))))
  cv.append(V);cq.append(Q);cw.append(W)
  if ix%50==0:print(tag,ix,len(times),'sec',round(time.perf_counter()-begin,1),flush=True)
 cv=np.array(cv);cq=np.array(cq);cw=np.array(cw)
 np.savez_compressed(OUT/(tag+'_DENSE.npz'),times=times,V=cv,Q=cq,W=cw)
 dt=np.diff(times);ok=dt>1e-7
 speed=np.diff(cq,axis=0)[ok]/dt[ok,None,None];base_speed=np.diff(baseQ,axis=0)[ok]/dt[ok,None,None]
 wrist_speed=np.linalg.norm(np.diff(cw[:,:3,3],axis=0)[ok],axis=1)/dt[ok]*1000
 skin_speed=np.max(np.linalg.norm(np.diff(cv,axis=0)[ok],axis=2),axis=1)/dt[ok]*1000
 target=[r for r in rows if 2.45-1e-10<=r['time']<=2.92+1e-10]
 target_hit=[r for r in target if r['illegal']]
 exact=rows[int(np.argmin(abs(times-2.6)))];c.settime(sc,2.6)
 V=cv[int(np.argmin(abs(times-2.6)))];keys=g.keycheck(V,all_hand=True)
 extract(ROOT/'experiments/hands_blender_artist_pose_repair_poc_r1/artist_tools.py',['segment_distance','edges','exact_clearance'],globals())
 for r in keys:
  if r['key'] in ['A#4','A4','C#5']:
   r['exact_clearance_mm']=0. if r['bvh_pairs'] or r['depth_mm']>1e-6 else min(exact_clearance(V,g.ALLT,g.actual(co)[0],co[4]) for co in g.comps if co[0]['key_index']==r['key_index'])
 summary=dict(candidate=str(path),samples=len(times),target_samples=len(target),target_illegal_samples=len(target_hit),target_first_illegal=target_hit[0]['time'] if target_hit else None,target_last_illegal=target_hit[-1]['time'] if target_hit else None,target_illegal_peak=max([dict(time=r['time'],key=k,depth_mm=v['depth_mm'],pairs=v['pairs']) for r in target for k,v in r['illegal'].items()],key=lambda v:v['depth_mm'],default=None),all_regression_samples=sum(bool(r['regressions']) for r in rows),target_regression_samples=sum(bool(r['regressions']) for r in target),new_self_samples=sum(bool(r['new_self']) for r in rows),new_cross_samples=sum(bool(r['new_cross']) for r in rows),left_max_delta_mm=max(r['left_delta_mm'] for r in rows),contact48_pass=sum(r['pass_'] for r in contacts),baseline_contact48_pass=sum(r['pass_'] for r in baseContacts),dense_active_contact_failures=[dict(time=r['time'],contacts=[a for a in r['contacts'] if not a['pass_']]) for r in rows if any(not a['pass_'] for a in r['contacts'])],max_domain_violation_deg=max(r['domain_violation_deg'] for r in rows),max_baseline_domain_violation_deg=max(r['baseline_domain_violation_deg'] for r in rows),outside_curve_value_max_error=outside_error,max_joint_speed_deg_s=np.max(abs(speed),axis=0),baseline_max_joint_speed_deg_s=np.max(abs(base_speed),axis=0),max_added_joint_speed_deg_s=np.max(abs(speed-base_speed),axis=0),max_wrist_speed_mm_s=float(wrist_speed.max()),max_skin_speed_mm_s=float(skin_speed.max()),exact_2_6=exact,exact_2_6_clearances=keys,native_unchanged=True,other_actions_unchanged=True,unedited_rig_paths_unchanged=True,event_count=len(NOTES),sampling='240Hz context 2.10-3.35 plus exact events/10 authored poses and 960Hz +/-6.25ms; 960Hz exit danger strip 2.875-2.925. Full evaluated right skin, actual 88-key components broadphase + BVH + triangle-convex certified depth; full skin self/cross. Finite samples, no continuous-time proof.',elapsed_seconds=time.perf_counter()-begin)
 save(tag+'_VALIDATION.json',dict(summary=summary,contacts48=contacts,rows=rows))
 print('SUMMARY',tag,json.dumps({k:summary[k] for k in ['target_illegal_samples','target_illegal_peak','contact48_pass','max_domain_violation_deg','new_self_samples','new_cross_samples','all_regression_samples']}),flush=True)
protection('DENSE_VALIDATION_INPUT_RECEIPT.json')
print('FULL_VALIDATION_COMPLETE',time.perf_counter()-begin,flush=True)
