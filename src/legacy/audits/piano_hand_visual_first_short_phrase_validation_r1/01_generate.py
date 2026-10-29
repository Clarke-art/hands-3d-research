from phrase_common import *
from scipy.optimize import least_squares
import time
assert not (P/'motion.npz').exists() and not (P/'RIGHT_SEQUENCE_FIT.json').exists(),'One candidate only'
lock=read(P/'GENERATION_LOCK.json');bounds=np.array(o.SP['joint_increment_bounds_deg']['LONG']);model=o.models('R')
prep=o.qanchor('R1');seed=np.tile(prep[:,None,:],(1,2,1));seed[2]=o.qanchor('R2')[2]
lo=[];hi=[]
for j in range(5):
 b=np.radians(o.SP['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG'])
 lo.append(np.tile(np.maximum(b[0],prep[j]-np.radians(12)),(2,1)))
 hi.append(np.tile(np.minimum(b[1],prep[j]+np.radians(12)),(2,1)))
lo=np.array(lo).ravel();hi=np.array(hi).ravel();seed=np.clip(seed.ravel(),lo+1e-9,hi-1e-9)
# All five right-hand gestures participate in one sequence residual. Coefficients reused for repeats.
notes=[n for n in EVENTS['R'] if n['measure']==1]
times=np.unique([n['note_on']+.035*u for n in notes for u in [0,.5,1]]+[n['note_off']+.07*u for n in notes for u in [0,.5]]+[n['note_on']-.06 for n in notes])
targets={}
for n in notes:
 j=n['finger']-1;v=np.array(o.ANCHORS['R2' if j==2 else 'R1']['pad_prediction_xyz_m'][j]);v[0]=c.KEYS[n['key_index']]['key_center'][0];v[2]=c.KEYS[n['key_index']]['key_top_playable_surface'][0]['z']+.0005;targets[j]=v
boxes=[(k['key_index'],np.array(g['vertices']).min(0),np.array(g['vertices']).max(0)) for k in c.KEYS if 65<=k['midi_note']<=88 for g in k['geometry']]
patches={j:np.linalg.norm(model['V']-model['V'][c.MARKERS['R'][j]['mesh_vertex']],axis=1)<.018 for j in range(5)};palm=model['V'][:,1]<.105
grid=np.arange(round(START*120),round(END*120)+1)/120
calls=0;start=time.monotonic();last=start

def residual(x):
 global calls,last
 calls+=1;coef=x.reshape(5,2,4);out=[]
 for t in times:
  q=right(t,coef);V=o.skin('R',q,model);pads=o.worldpads('R',q);ka=c.angles_at(t);active=[]
  for n in notes:
   if n['note_on']-1e-8<=t<=n['note_off']+.07+1e-8:
    j=n['finger']-1;k=n['key_index'];target=o.keytransform(n['midi_note'],targets[j],ka[k]);out.extend((pads[j]-target)*1000*10);out.extend((V[c.MARKERS['R'][j]['mesh_vertex']]-target)*1000*6);active.append((k,patches[j]))
  pen=np.zeros(len(V))
  for k,lower,upper in boxes:
   VV=o.keytransform(k+21,V,ka[k],True) if ka[k] else V;d=np.abs(VV-(lower+upper)/2)-(upper-lower)/2;sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0);margin=np.where(palm,.005,.002)
   for own,patch in active:
    if k==own:margin=margin.copy();margin[patch]=0
   pen=np.maximum(pen,margin-sdf)
  out.extend(np.maximum(pen,0)*1000*2)
 qs=np.degrees([right(t,coef) for t in grid]);v=np.diff(qs,axis=0)*120;a=np.diff(v,axis=0)*120
 out.extend((np.maximum(np.abs(v)-850,0)*.05).ravel());out.extend((np.maximum(np.abs(a)-90000,0)*.0005).ravel());out.extend(((coef-prep[:,None,:])*2).ravel());out.extend((np.diff(coef,axis=1)*2).ravel())
 if time.monotonic()-last>20:print('ONE_SEQUENCE_FIT',calls,'elapsed',round(time.monotonic()-start,1),flush=True);last=time.monotonic()
 return np.array(out)
fit=least_squares(residual,seed,bounds=(lo,hi),max_nfev=lock['max_nfev'],ftol=1e-6,xtol=1e-6,gtol=1e-6)
assert np.isfinite(fit.x).all();coef=fit.x.reshape(5,2,4)
dump('RIGHT_SEQUENCE_FIT.json',{'success':bool(fit.success),'nfev':fit.nfev,'calls':calls,'cost':float(fit.cost),'message':fit.message,'elapsed_sec':time.monotonic()-start,'coefficients_deg':np.degrees(coef),'lower_deg':np.degrees(lo.reshape(5,2,4)),'upper_deg':np.degrees(hi.reshape(5,2,4)),'targets':targets,'candidate_count':1,'restarts':0,'manual_per_note_adjustment':False,'repeated_note_coefficients_shared':True,'left_coefficients_refitted':False})
exact=[v for n in TL['notes'] for v in [n['note_on']-.12,n['note_on'],n['note_on']+.035,n['note_off'],n['note_off']+.07,recovery(n)]];times=np.unique(np.r_[grid,exact]);times=times[(times>=START-1e-8)&(times<=END+1e-8)]
L=[];R=[];keys=[];deltas=[];pitches=[]
for t in times:
 q,ka,d,p=left(float(t));L.append(q);R.append(right(float(t),coef));keys.append(ka);deltas.append(d);pitches.append(p)
np.savez_compressed(P/'motion.npz',times=times,L_q=L,R_q=R,key_angles=keys,L_delta=deltas,L_pitch_deg=pitches)
dump('MOTION_GENERATION.json',{'motion_sha256':sha(P/'motion.npz'),'candidate_count':1,'source_midi_sha256':TL['source_midi_sha256'],'left_29_coefficients_source_sha256':sha(LAST/'ROOT_FINGER_COORDINATION_R1.json'),'right_coefficients_source_sha256':sha(P/'RIGHT_SEQUENCE_FIT.json'),'sample_hz':120,'samples':len(times),'window':[START,END],'no_per_note_manual_adjustment':True,'no_post_smoothing':True,'coefficient_strategy':'reuse left fit; one bounded right whole-sequence fit shared across repeats; derived Bernstein coefficients between contact/full-down endpoints','engineering_bounds_are_not_anatomical':True})
print('ONE_CANDIDATE_ARRAY_SAVED',len(times),flush=True)
