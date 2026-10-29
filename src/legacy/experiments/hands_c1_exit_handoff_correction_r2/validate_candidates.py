import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
R1=ROOT/'experiments/hands_c1_dynamic_artist_correction_poc_r1'
base=read(R1/'BASELINE_DENSE_GEOMETRY.json');prior=read(R1/'CANDIDATE_2_FIXED_VALIDATION.json')
bdfile=np.load(safe(R1/'BASELINE_DENSE.npz'));rdfile=np.load(safe(R1/'CANDIDATE_2_FIXED_DENSE.npz'))
# Materialize each frozen array once; npz indexing otherwise decompresses the
# whole trajectory again for every sample. This changes no sampled values.
bd={k:bdfile[k] for k in bdfile.files};rd={k:rdfile[k] for k in rdfile.files}
times=bd['times'];assert np.array_equal(times,rd['times']);assert np.max(abs(times-np.array(base['times'])))==0
bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
contract=read(R1/'CANDIDATE_2_FIXED_EDIT_LEDGER.json');paths=set(contract['edited_paths'])
extract(R1/'validate_full.py',['collision','selfpairs'],globals())
begin=time.perf_counter()
for number in [1,2]:
 path=OUT/f'EXIT_CANDIDATE_{number}_NOT_APPROVED.blend';sc,rig,mesh,left,lrig=s.open_scene(path);g.init()
 assert contract['native']=={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
 other=s.protected_state(True);assert other=={k:v for k,v in contract['protected_actions'].items() if k!=rig.name}
 act=rig.animation_data.action
 # Check all unedited rig paths against the R1 payload, without opening C1 scene.
 r1payload=read(R1/'BASELINE_FACTS.json')['actions']
 contacts=[]
 for n in [n for n in NOTES if n['hand']=='R']:
  for phase,t in [('ON',n['note_on']),('HOLD',(n['note_on']+n['note_off'])/2),('PRE_OFF',n['note_off']-.001)]:
   c.settime(sc,t);V,T,F=s.coords_tri(mesh);contacts.append(dict(event=n['note_id'],key=n['note_name'],time=t,phase=phase,**s.contact(V,KEYS[n['key_index']],'R',n['finger'])))
 rows=[];Vs=[];Qs=[];Ws=[]
 for i,t in enumerate(times):
  c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left);Q=np.array([s.degrees(d) for d in DIGITS]);cols=collision(V)
  active={n['note_name'] for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']}
  illegal={k:v for k,v in cols.items() if k not in active and (v['depth_mm']>1e-6 or v['pairs'])}
  def regress(ref,eps):
   return {k:dict(baseline_mm=ref.get(k,{}).get('depth_mm',0),candidate_mm=v['depth_mm'],increase_mm=v['depth_mm']-ref.get(k,{}).get('depth_mm',0)) for k,v in cols.items() if k not in active and v['depth_mm']>ref.get(k,{}).get('depth_mm',0)+eps}
  strict=regress(base['collisions'][i],.0001);canonical=regress(base['collisions'][i],.02)
  vsprior=regress(prior['rows'][i]['keys'],.0001)
  bp=selfpairs(bd['V'][i]);cp=selfpairs(V);cross=set(g.tree(V,T).overlap(g.tree(L,LT)))
  assert base['cross_counts'][i]==0
  current=[dict(event=n['note_id'],key=n['note_name'],**s.contact(V,KEYS[n['key_index']],'R',n['finger'])) for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
  rows.append(dict(time=float(t),keys=cols,illegal=illegal,strict_regressions_C1=strict,canonical_regressions_C1=canonical,strict_regressions_R1=vsprior,new_self=sorted(cp-bp),self_count=len(cp),cross_pairs=len(cross),left_delta_mm=float(np.max(np.linalg.norm(L-bd['L'][i],axis=1)))*1000,contacts=current,joint_domain_violation_deg=float(max(0,np.max(bounds[:,0]-Q),np.max(Q-bounds[:,1]))),skin_delta_R1_mm=float(np.max(np.linalg.norm(V-rd['V'][i],axis=1)))*1000))
  Vs.append(V);Qs.append(Q);Ws.append(np.array(<REDACTED_EMAIL>['WRIST_R'].matrix))
  if i%75==0:print('R2_VALIDATE',number,i,len(times),'sec',round(time.perf_counter()-begin,1),flush=True)
 Vs=np.array(Vs);Qs=np.array(Qs);Ws=np.array(Ws)
 np.savez_compressed(OUT/f'CANDIDATE_{number}_DENSE.npz',times=times,V=Vs,Q=Qs,W=Ws)
 target=[r for r in rows if 2.45-1e-10<=r['time']<=2.92+1e-10];hits=[r for r in target if r['illegal']]
 dt=np.diff(times);valid=dt>1e-7
 speeds=np.diff(Qs,axis=0)[valid]/dt[valid,None,None];prior_speed=np.diff(rd['Q'],axis=0)[valid]/dt[valid,None,None]
 delta=Qs-rd['Q'];newdomain=[r for r in rows if r['joint_domain_violation_deg']>1e-5]
 outside=[r for r in rows if r['time']<=2.68+1e-10 or r['time']>=3.12-1e-10]
 preserved=[r for r in rows if r['time']<=2.68+1e-10]
 summary=dict(candidate=str(path),sha256=sha(path),samples=len(times),target_samples=len(target),target_illegal_samples=len(hits),target_peak=max([dict(time=r['time'],key=k,depth_mm=v['depth_mm']) for r in target for k,v in r['illegal'].items()],key=lambda x:x['depth_mm'],default=None),target_key_peaks={k:max(r['keys'].get(k,{}).get('depth_mm',0) for r in target) for k in ['A#4','A4','C#5']},context_canonical_regression_samples=sum(bool(r['canonical_regressions_C1']) for r in rows),context_strict_regression_samples=sum(bool(r['strict_regressions_C1']) for r in rows),context_R1_strict_regression_samples=sum(bool(r['strict_regressions_R1']) for r in rows),max_domain_violation_deg=max(r['joint_domain_violation_deg'] for r in rows),domain_violation_samples=len(newdomain),contacts48_pass=sum(r['pass_'] for r in contacts),dense_contact_failures=[dict(time=r['time'],contact=ct) for r in rows for ct in r['contacts'] if not ct['pass_']],G4_dense_count=sum(ct['key']=='G4' for r in rows for ct in r['contacts']),G4_dense_failures=sum(ct['key']=='G4' and not ct['pass_'] for r in rows for ct in r['contacts']),new_self_samples=sum(bool(r['new_self']) for r in rows),new_cross_samples=sum(r['cross_pairs']>0 for r in rows),left_max_delta_mm=max(r['left_delta_mm'] for r in rows),preserved_entry_hold_skin_delta_mm=max(r['skin_delta_R1_mm'] for r in preserved),outside_skin_delta_R1_mm=max(r['skin_delta_R1_mm'] for r in outside),joint_speed_peak_deg_s=float(np.max(abs(speeds))),added_joint_speed_vs_R1_peak_deg_s=float(np.max(abs(speeds-prior_speed))),wrist_speed_peak_mm_s=float(np.max(np.linalg.norm(np.diff(Ws[:,:3,3],axis=0)[valid],axis=1)/dt[valid])*1000),skin_speed_peak_mm_s=float(np.max(np.linalg.norm(np.diff(Vs,axis=0)[valid],axis=2)/dt[valid,None])*1000),native_unchanged=True,other_actions_unchanged=True,baseline_cache_sha256=sha(R1/'BASELINE_DENSE.npz'),baseline_geometry_sha256=sha(R1/'BASELINE_DENSE_GEOMETRY.json'),R1_cache_sha256=sha(R1/'CANDIDATE_2_FIXED_DENSE.npz'),sampling='Same501 source times as frozen R1:240Hz 2.10-3.35, exact events and authored boundaries, 960Hz near boundaries and2.875-2.925; C1/R1 exact evaluated caches reused with protected hashes. Corrected full skin and actual Action-driven key meshes recomputed after reopening each blend. No continuous-time proof.')
 save(f'CANDIDATE_{number}_VALIDATION.json',dict(summary=summary,contacts48=contacts,rows=rows))
 print('R2_SUMMARY',number,json.dumps({k:summary[k] for k in ['target_illegal_samples','target_key_peaks','context_canonical_regression_samples','context_strict_regression_samples','max_domain_violation_deg','contacts48_pass','new_self_samples','new_cross_samples']}),flush=True)
protection('VALIDATION_INPUT_RECEIPT.json')
print('R2_VALIDATION_COMPLETE',flush=True)
