from articulation_common import *
from right_motion import *
from scipy.optimize import least_squares
import time
pol=read(P/'GENERATION_POLICY.json');assert not (P/'motion.npz').exists() and not (P/'RIGHT_HAND_FIT.json').exists()
assert all(sha(P/n)==h for n,h in pol['generator_scripts_sha256'].items()),'Locked generator changed'
model=o.models('R');oldfit=read(PRE/'RIGHT_SEQUENCE_FIT.json');old=np.load(PRE/'motion.npz')
# Shared contact/down endpoint pairs. No per-note parameter block.
seed=np.array(oldfit['coefficients_deg']).ravel();lo=[];hi=[]
for j in range(5):
 radius=np.array([16,12,12,12]);lower=np.maximum(np.degrees(B[j,0]),np.degrees(PREP[j])-radius);upper=np.minimum(np.degrees(B[j,1]),np.degrees(PREP[j])+radius);lo.extend(np.tile(lower,2));hi.extend(np.tile(upper,2))
lo=np.r_[lo,[-2,-3,-5,-2],np.maximum(-4,np.degrees(B[:,0,:3]-PREP[:,:3])).ravel()];hi=np.r_[hi,[2,3,0,.5],np.minimum(4,np.degrees(B[:,1,:3]-PREP[:,:3])).ravel()];seed=np.r_[seed,[0,0,-2,-.7],np.zeros(15)];seed=np.clip(seed,lo+1e-8,hi-1e-8)
refs={}
for n in EVENTS:
 j=n['finger']-1;key=c.KEYS[n['key_index']];active=[p for p,a in o.ANCHORS.items() if a['hand']=='R' and a['task'].get('active_finger')==j+1 and a['task'].get('active_midi')==n['midi_note']];anchor=o.ANCHORS[active[0] if active else 'R1'];ref=np.array(anchor['pad_prediction_xyz_m'][j]);choices=[]
 for surf in key['key_top_playable_surface']:
  low=np.array([surf['xmin'],surf['ymin']])+.001;high=np.array([surf['xmax'],surf['ymax']])-.001;xy=np.clip(ref[:2],low,high);choices.append(np.r_[xy,surf['z']+.0005])
 refs[n['note_id']]=min(choices,key=lambda v:np.linalg.norm(v[:2]-ref[:2]))
contacttimes=np.unique([n['note_on']+.035*u for n in EVENTS for u in [0,.5,1]]+[n['note_off']-1/240 for n in EVENTS])
cleartimes=np.unique([n['note_on']-APPROACH/2 for n in EVENTS]+[n['note_on']+.035 for n in EVENTS]+[n['note_off']+.035 for n in EVENTS])
grid=np.arange(round(START*120),round(END*120)+1)/120

def schedule(times):
 rows=[phases(float(t)) for t in times];return tuple(np.array([r[i] for r in rows]) for i in range(4))
def batch(sc,x):
 st,a,p,lift=sc;coef=np.radians(x[:40].reshape(5,2,4));idle=np.radians(x[44:59].reshape(5,3));rest=np.tile(PREP,(len(st),1,1));rest[:,:,:3]+=st[:,None,None]*idle[None,:,:];raised=rest.copy();raised[:,:,0]=np.maximum(B[None,:,0,0],raised[:,:,0]-np.radians(3));q=rest+a[:,:,None]*(coef[None,:,0,:]-rest)+(a*p)[:,:,None]*(coef[None,:,1,:]-coef[None,:,0,:])+lift[:,:,None]*(raised-rest);return q,x[None,40:43]*st[:,None]/1000,x[43]*st
cs=schedule(contacttimes);ns=schedule(cleartimes);gs=schedule(grid)
boxes=[(k['key_index'],np.array(g['vertices']).min(0),np.array(g['vertices']).max(0)) for k in c.KEYS if 65<=k['midi_note']<=88 for g in k['geometry']];patches={j:np.linalg.norm(model['V']-model['V'][c.MARKERS['R'][j]['mesh_vertex']],axis=1)<.018 for j in range(5)};palm=model['V'][:,1]<.105
calls=0;start=time.monotonic();last=start

def residual(x):
 global calls,last
 calls+=1;out=[]
 qs,ds,ps=batch(cs,x)
 for i,t in enumerate(contacttimes):
  pads=transform_right(o.worldpads('R',qs[i]),ds[i],ps[i]);V=transform_right(o.skin('R',qs[i],model),ds[i],ps[i]);ka=c.angles_at(t)
  for n in EVENTS:
   if n['note_on']-1e-8<=t<n['note_off']-1e-8:
    j=n['finger']-1;target=o.keytransform(n['midi_note'],refs[n['note_id']],ka[n['key_index']]);out.extend((pads[j]-target)*1000*pol['weights']['fixed_contact_mm']);out.extend((V[c.MARKERS['R'][j]['mesh_vertex']]-target)*1000*pol['weights']['skin_contact_mm'])
 qs,ds,ps=batch(ns,x)
 for i,t in enumerate(cleartimes):
  V=transform_right(o.skin('R',qs[i],model),ds[i],ps[i]);ka=c.angles_at(t);pen=np.zeros(len(V));active=[]
  for n in EVENTS:
   if n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8:active.append((n['key_index'],patches[n['finger']-1]))
  for k,lower,upper in boxes:
   VV=o.keytransform(k+21,V,ka[k],True) if ka[k] else V;d=np.abs(VV-(lower+upper)/2)-(upper-lower)/2;sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0);margin=np.where(palm,.005,.002)
   for own,patch in active:
    if own==k:margin=margin.copy();margin[patch]=0
   pen=np.maximum(pen,margin-sdf)
  out.extend(np.maximum(pen,0)*1000*pol['weights']['existing_skin_clearance_mm'])
 qs,ds,ps=batch(gs,x);v=np.diff(np.degrees(qs),axis=0)*120;acc=np.diff(v,axis=0)*120
 out.extend((np.maximum(abs(v)-850,0)*.05).ravel());out.extend((np.maximum(abs(acc)-90000,0)*.0005).ravel());rv=np.diff(ds,axis=0)*120*1000;ra=np.diff(rv,axis=0)*120;pv=np.diff(ps)*120;pa=np.diff(pv)*120
 out.extend((np.maximum(np.linalg.norm(rv,axis=1)-450,0)*.05).ravel());out.extend((np.maximum(np.linalg.norm(ra,axis=1)-45000,0)*.0005).ravel());out.extend(np.maximum(abs(pv)-150,0)*.05);out.extend(np.maximum(abs(pa)-15000,0)*.0005)
 out.extend(((np.radians(x[:40].reshape(5,2,4))-PREP[:,None,:])*pol['weights']['joint_anchor_rad']).ravel());out.extend(x[44:]*pol['weights']['idle_deg']);out.extend(x[40:43]*pol['weights']['root_xyz_mm']);out.append(x[43]*pol['weights']['root_pitch_deg'])
 if time.monotonic()-last>20:print('ONE_ARTICULATION_SEQUENCE_FIT',calls,'elapsed',round(time.monotonic()-start,1),flush=True);last=time.monotonic()
 return np.array(out)
fit=least_squares(residual,seed,bounds=(lo,hi),max_nfev=pol['max_nfev'],xtol=1e-6,ftol=1e-6,gtol=1e-6)
assert np.isfinite(fit.x).all();dump('RIGHT_HAND_FIT.json',{'x':fit.x,'success':bool(fit.success),'nfev':fit.nfev,'calls':calls,'message':fit.message,'cost':float(fit.cost),'elapsed_sec':time.monotonic()-start,'parameters':59,'candidate_count':1,'restarts':0,'left_refitted':False,'manual_per_note_adjustment':False,'same_digit_coefficients_reused':True,'contact_targets':refs,'lower':lo,'upper':hi,'generator_sha256':sha(__file__),'policy_sha256':sha(P/'GENERATION_POLICY.json'),'shared_root_amp_xyz_mm_pitch_deg':fit.x[40:44]})
# First evaluate right trajectories on exact original notes before combining unchanged left arrays.
times=old['times'];Q=[];deltas=[];pitches=[]
for t in times:
 q,d,p=sample_right(float(t),fit.x);Q.append(q);deltas.append(d);pitches.append(p)
qbatch,dbatch,pbatch=batch(schedule(times),fit.x);assert np.max(abs(qbatch-np.array(Q)))<1e-12
np.savez_compressed(P/'right_trajectory.npz',times=times,R_q=Q,R_delta=deltas,R_pitch_deg=pitches)
quick=[]
for n in EVENTS:
 j=n['finger']-1;indices=np.flatnonzero((times>=n['note_on']-1e-8)&(times<n['note_off']-1e-8));rows=[]
 for i in indices:
  pads=transform_right(o.worldpads('R',Q[i]),deltas[i],pitches[i]);r=o.measure(pads[j],n['midi_note'],old['key_angles'][i,n['key_index']]);rows.append(r)
 quick.append({'note_id':n['note_id'],'midi':n['midi_note'],'finger':n['finger'],'fixed_gap_min_mm':min(r['gap_mm'] for r in rows),'fixed_gap_max_mm':max(r['gap_mm'] for r in rows),'horizontal_max_mm':max(r['horizontal_mm'] for r in rows),'old_note_identity_unchanged':True})
dump('RIGHT_TRAJECTORY_ON_ORIGINAL_EVENTS.json',{'one_right_trajectory':True,'samples':len(times),'source_event_count':10,'notes':quick,'left_not_generated_or_reoptimized':True,'phase_policy_unchanged':True,'contact_is_soft_residual':'Final actual geometry and visible review remain required'})
np.savez_compressed(P/'motion.npz',times=times,L_q=old['L_q'],L_delta=old['L_delta'],L_pitch_deg=old['L_pitch_deg'],R_q=Q,R_delta=deltas,R_pitch_deg=pitches,key_angles=old['key_angles'])
for key in ['times','L_q','L_delta','L_pitch_deg','key_angles']:assert np.array_equal(np.load(P/'motion.npz')[key],old[key])
dump('MOTION_GENERATION.json',{'candidate_count':1,'motion_sha256':sha(P/'motion.npz'),'previous_motion_sha256':sha(PRE/'motion.npz'),'left_arrays_exact_unchanged':True,'key_time_arrays_exact_unchanged':True,'right_trajectory_validated_on_original_events_before_combining':True,'full_note_count':18,'right_note_count':10,'left_note_count':8,'no_per_note_manual_adjustment':True,'post_smoothing':False,'restarts':0})
print('ONE_NEW_DUAL_HAND_MOTION_ARRAY_SAVED',len(times),fit.x[40:44],flush=True)
