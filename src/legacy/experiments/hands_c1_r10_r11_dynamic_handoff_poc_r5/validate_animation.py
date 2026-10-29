import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import dynamic_session as w
from dynamic_session import *
begin=time.perf_counter()
# Existing 240Hz context; 960Hz around historical crossing and exact handoff.
tt=list(np.arange(math.ceil(3.35*240),math.floor(4.08*240)+1)/240)+[3.35,4.08,A,H,B,3.67,3.88]
for low,high in [(3.69,3.73),(H-.025,H+.04)]:
 tt+=list(np.arange(math.ceil(low*960),math.floor(high*960)+1)/960)
for t in [A,H,B]:
 tt += [t+dt for dt in [-1/960,-1/3840,0,1/3840,1/960]]
tt=sorted(tt);times=[]
for t in tt:
 if not times or t-times[-1]>1e-8:times.append(float(t))
for t in [A,H,B]:times=sorted([x for x in times if abs(x-t)>1e-8]+[t])
rn=[n for n in NOTES if n['hand']=='R']
contact_times=[(n,phase,t) for n in rn for phase,t in [('ON',n['note_on']),('HOLD',(n['note_on']+n['note_off'])/2),('PRE_OFF',n['note_off']-.001)]]
def capture48():
 out=[]
 for n,phase,t in contact_times:
  c.settime(w.sc,t);V=s.coords_tri(w.mesh)[0];out.append(dict(event=n['note_id'],phase=phase,time=t,key=n['note_name'],finger=n['finger'],**s.contact(V,KEYS[n['key_index']],'R',n['finger'])))
 return out
base=[];VL=[];VR=[];QS=[];WS=[];base_contacts=[]
w.reset()
for ix,t in enumerate(times):
 c.settime(w.sc,t);r,V,L=w.measure(t);base.append(r);VR.append(V);VL.append(L);QS.append(r['q']);WS.append(r['wrist'])
 if ix%60==0:print('BASE_CONTEXT',ix,len(times),round(time.perf_counter()-begin,1),flush=True)
base_contacts=capture48()
save('BASELINE_CONTEXT_GEOMETRY.json',dict(rows=base,contacts48=base_contacts,samples=len(times)))
np.savez_compressed(OUT/'BASELINE_CONTEXT_ACTUAL.npz',times=times,R=VR,L=VL,Q=QS,W=WS)
VR=np.array(VR);VL=np.array(VL);QS=np.array(QS);WS=np.array(WS)
R2rows=read(R2/'CANDIDATE_2_VALIDATION.json')['rows']
R2dense=np.load(safe(R2/'CANDIDATE_2_DENSE.npz'))
targetinds=[i for i,t in enumerate(R2dense['times']) if 2.45-1e-10<=t<=2.92+1e-10]
source_native=BASE_NATIVE
for number in [1,2]:
 w.reset(OUT/f'CANDIDATE_{number}_NOT_APPROVED.blend')
 native_ok=BASE_NATIVE=={a:c.digest(c.native(o,r)) for a,o,r in [('R',w.mesh,w.rig),('L',w.left,w.lrig)]}
 other_ok=OTHER_ACTIONS==s.protected_state(True)
 contacts=capture48();rows=[];VALL=[];QALL=[];WALL=[]
 for ix,t in enumerate(times):
  c.settime(w.sc,t);r,V,L=w.measure(t);b=base[ix]
  r['left_delta_mm']=float(np.linalg.norm(L-VL[ix],axis=1).max()*1000)
  r['skin_delta_mm']=float(np.linalg.norm(V-VR[ix],axis=1).max()*1000)
  r['regressions']={k:dict(original_mm=b['keys'].get(k,{}).get('depth_mm',0.),candidate_mm=v['depth_mm']) for k,v in r['keys'].items() if v['depth_mm']>b['keys'].get(k,{}).get('depth_mm',0.)+.02}
  r['new_self_count']=max(0,r['self_count']-b['self_count'])
  # Premature pressing: idle finger triangles intersect the upcoming actual key.
  prep=[]
  for n in [w.R11,w.R12]:
   if not n['note_on']-.18<=t<n['note_on']:continue
   digit=DIGITS[n['finger']-1];pairs=[]
   for co in g.comps:
    if co[0]['key_index']!=n['key_index']:continue
    kv,P=g.actual(co)
    hit=g.tree(V,g.ALLT).overlap(g.tree(kv,co[4]))
    pairs += [a for a,b0 in hit if all(w.label(v)==digit for v in g.ALLT[a])]
   pad=s.contact(V,KEYS[n['key_index']],'R',n['finger'])
   prep.append(dict(event=n['note_id'],digit=digit,surface_pairs=len(pairs),pad=pad))
  r['prepare']=prep;rows.append(r);VALL.append(V);QALL.append(r['q']);WALL.append(r['wrist'])
  if ix%60==0:print('CANDIDATE',number,ix,len(times),round(time.perf_counter()-begin,1),flush=True)
 VALL=np.array(VALL);QALL=np.array(QALL);WALL=np.array(WALL);dt=np.diff(times)
 skin_speed=np.max(np.linalg.norm(np.diff(VALL,axis=0),axis=2),axis=1)*1000/dt
 wrist_speed=np.linalg.norm(np.diff(WALL[:,:3,3],axis=0),axis=1)*1000/dt
 qspeed=np.diff(QALL,axis=0)/dt[:,None,None];basespeed=np.diff(QS,axis=0)/dt[:,None,None]
 core=[r for r in rows if A-1e-10<=r['time']<B-1e-10]
 atH=next(r for r in rows if abs(r['time']-H)<1e-9)
 failures=[r for r in core if r['illegal'] or r['self_count'] or any(not a['pass_'] for a in r['contacts']) or r['domain_violation_deg']>1e-6]
 stable=[]
 for ix in targetinds:
  t=float(R2dense['times'][ix]);c.settime(w.sc,t);V=s.coords_tri(w.mesh)[0];stable.append(float(np.linalg.norm(V-R2dense['V'][ix],axis=1).max()*1000))
 # Direct comparisons outside support, including R09 and R12 formal poses.
 outside=[r for r in rows if r['time']<A-1e-6 or r['time']>B+1e-6]
 exactB=next(r for r in rows if abs(r['time']-B)<1e-9)
 # Record local derivatives around boundaries and every authored key, actual
 # FCurve evaluation is already used above; no inferred spline samples.
 ledger=read(OUT/f'CANDIDATE_{number}_EDIT_LEDGER.json')
 continuity=[]
 for t in [A,H,B]+[v['time'] for v in ledger['samples']]:
  vv=[];ww=[]
  for e in [-1e-5,0,1e-5]:
   c.settime(w.sc,t+e);vv.append(s.coords_tri(w.mesh)[0]);ww.append(np.array(<REDACTED_EMAIL>['WRIST_R'].matrix)[:3,3])
  continuity.append(dict(time=t,skin_step_left_mm=float(np.linalg.norm(vv[1]-vv[0],axis=1).max()*1000),skin_step_right_mm=float(np.linalg.norm(vv[2]-vv[1],axis=1).max()*1000),wrist_step_left_mm=float(np.linalg.norm(ww[1]-ww[0])*1000),wrist_step_right_mm=float(np.linalg.norm(ww[2]-ww[1])*1000)))
 p10=next(r for r in rows if abs(r['time']-3.67)<1e-8);p11=next(r for r in rows if abs(r['time']-3.88)<1e-8)
 summary=dict(candidate=number,samples=len(rows),core_samples=len(core),core_illegal_samples=sum(bool(r['illegal']) for r in core),core_self_samples=sum(r['self_count']>0 for r in core),core_self_peak=max(r['self_count'] for r in core),core_contact_failure_samples=sum(any(not a['pass_'] for a in r['contacts']) for r in core),contact48_pass=sum(r['pass_'] for r in contacts),baseline_contact48_pass=sum(r['pass_'] for r in base_contacts),core_domain_peak_deg=max(r['domain_violation_deg'] for r in core),new_self_samples=sum(r['new_self_count']>0 for r in rows),new_cross_samples=sum(r['cross_count']>b['cross_count'] for r,b in zip(rows,base)),left_max_delta_mm=max(r['left_delta_mm'] for r in rows),regression_samples=sum(bool(r['regressions']) for r in rows),outside_support_skin_delta_mm=max(r['skin_delta_mm'] for r in outside),R12_on_skin_delta_mm=exactB['skin_delta_mm'],R12_on_contact=exactB['contacts'],R12_prepare_surface_hit_samples=sum(p['surface_pairs']>0 for r in core for p in r['prepare'] if p['event']=='R12'),max_actual_skin_speed_mm_s=float(skin_speed.max()),max_actual_wrist_speed_mm_s=float(wrist_speed.max()),max_actual_joint_speed_deg_s=float(abs(qspeed).max()),max_added_joint_speed_deg_s=float(abs(qspeed-basespeed).max()),R2_245_292_samples=len(stable),R2_245_292_max_skin_delta_mm=max(stable),native_unchanged=native_ok,other_actions_unchanged=other_ok,handoff=atH,representative_wrist_delta_mm=(np.array(p11['wrist'])[:3,3]-np.array(p10['wrist'])[:3,3])*1000,representative_wrist_distance_mm=float(np.linalg.norm(np.array(p11['wrist'])[:3,3]-np.array(p10['wrist'])[:3,3])*1000),machine_pass=not failures and native_ok and other_ok)
 save(f'CANDIDATE_{number}_VALIDATION.json',dict(summary=summary,rows=rows,contacts48=contacts,continuity=continuity,finite_sampling_only=True,core_range=[A,B],sampling='240Hz 3.35-4.08 plus 960Hz 3.69-3.73 and H-25ms..H+40ms, exact events and +/-1/960,+/-1/3840s; actual evaluated full right mesh with Action-driven actual key meshes, BVH and certified triangle-interior depth; all nonadjacent self triangles.'))
 np.savez_compressed(OUT/f'CANDIDATE_{number}_ACTUAL.npz',times=times,V=VALL,Q=QALL,W=WALL)
 print('SUMMARY',number,json.dumps({k:v for k,v in summary.items() if k not in ['handoff']},default=encode),flush=True)
protection('VALIDATION_INPUT_RECEIPT.json')
print('VALIDATION_COMPLETE',time.perf_counter()-begin,flush=True)
