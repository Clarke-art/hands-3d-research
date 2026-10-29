from performance_core import *
from scipy.optimize import least_squares
OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
old=np.load(OLD/'procedural_motion.npz')
layout=read(P/'SONG_DATA_R1.json')['execution_layout']
times=old['times'];DT=1/HZ
policy={'candidate_count':1,'authority':'DESIGN_ONLY / fingering DESIGN_PROVISIONAL','reference':'Frozen L1 ZERO / RSSF rest geometry, mirrored from R2; angles below are modest audit increments from that curved geometry, not human anatomical standards','idle_target':'NO key/home IK for relaxed fingers. Curved RSSF + small deterministic phase-driven flexion; shared palm transport.','states':['ACTIVE_PRESS','PREPARING','RELEASING','RELAXED_IDLE'],'prepare_sec':.16,'release_sec':.14,'joint_increment_limits_deg':{'long':[50,48,32,28],'thumb':[30,35,25,35]},'palm_global_bounds':{'x':'seed +/-45mm','y_m':[-.14,-.065],'z_m':[.045,.085],'yaw_deg':[-16,16],'pitch_deg':[0,9],'roll_deg':[-5,5]},'temporal_constraints':{'joint_velocity_deg_s':360,'joint_acceleration_deg_s2':14400,'root_velocity_m_s':.32,'root_acceleration_m_s2':14,'root_rotation_velocity_deg_s':70,'root_rotation_acceleration_deg_s2':2400,'method':'previous legal state plus velocity prediction; intersect per-step velocity/acceleration bounds and braking envelope with joint limits INSIDE IK. No post-smoothing.'},'whole_hand':'single root XYZ/yaw/pitch/roll jointly solved with playing/preparing/releasing fingers; idle fingers transported in that common palm frame; clearance proxies are RSSF palm samples and idle pads','objective_units':'contact in mm; natural posture and temporal penalties in rad; root regularization in mm. No effectively-zero prior.','fixed_inputs':'copied byte-identical timeline, fingering, keyboard, markers, tolerances and WAV; key angle array copied exactly','skin':'inherit exactly; realism unresolved independently','stop_loss':'one deterministic initialization and one forward constrained trajectory; no restarts, sweeps or alternate versions'}
dump('GENERATION_POLICY_R1.json',policy)
dump('PRE_GENERATION_LOCK_R1.json',{'policy_sha256':sha(P/'GENERATION_POLICY_R1.json'),'script_sha256':sha(__file__),'inherited':read(P/'INHERITED_INPUTS_R1.json')})

def rotbatch(a,axes):
 v=axes/np.linalg.norm(axes,axis=-1,keepdims=True);K=np.zeros(v.shape[:-1]+(3,3));K[...,0,1]=-v[...,2];K[...,0,2]=v[...,1];K[...,1,0]=v[...,2];K[...,1,2]=-v[...,0];K[...,2,0]=-v[...,1];K[...,2,1]=v[...,0]
 return np.eye(3)+np.sin(a)[...,None,None]*K+(1-np.cos(a))[...,None,None]*(K@K)
def fast_setup(s):
 sets=[SETUPS[s,d] for d in DIGITS]
 return np.array([v[1] for v in sets]),np.array([v[2] for v in sets]),np.array([v[3] for v in sets]),np.array([v[4] for v in sets])
fast={s:fast_setup(s) for s in ['R','L']}
def allpads(s,q):
 rel,axes,spread,pad=fast[s];rots=rotbatch(q[:,:3],axes);rots[:,0]=rotbatch(q[:,3],spread)@rots[:,0];M=np.tile(np.eye(4),(5,1,1))
 for j in range(3):
  J=np.tile(np.eye(4),(5,1,1));J[:,:3,:3]=rots[:,j];M=M@rel[:,j]@J
 return np.einsum('ijk,ik->ij',M,pad)[:,:3]
def palmrot(x):return rz(x[3])@axisrot(x[4],[1,0,0])@axisrot(x[5],[0,1,0])
def safeheight(pts):
 # Frozen unpressed top provides conservative clearance, never moves contact targets.
 z=np.full(len(pts),-.1)
 for k in KEYS:
  for surf in k['key_top_playable_surface']:
   mask=(pts[:,0]>=surf['xmin'])&(pts[:,0]<=surf['xmax'])&(pts[:,1]>=surf['ymin'])&(pts[:,1]<=surf['ymax'])
   z=np.where(mask,np.maximum(z,surf['z']),z)
 return z
# Array form avoids Python key loops in every numerical-Jacobian evaluation.
surfs=np.array([[v[k] for k in ['xmin','xmax','ymin','ymax','z']] for key in KEYS for v in key['key_top_playable_surface']])
def safeheight(pts):
 mask=(pts[:,None,0]>=surfs[:,0])&(pts[:,None,0]<=surfs[:,1])&(pts[:,None,1]>=surfs[:,2])&(pts[:,None,1]<=surfs[:,3])
 return np.max(np.where(mask,surfs[:,4],-.1),axis=1)
out={'times':times,'key_angles':old['key_angles']};plans={};state_rows={}
for s in ['R','L']:
 homes=layout[s]['home_midi_by_finger'];ys=layout[s]['home_depth_m_by_finger'];seed=layout[s]['root_seed_x_m']
 ns=[n for n in TL['notes'] if n['hand']==s]
 qrest=np.radians([[3,5,3,0],[5,8,5,0],[5,8,5,0],[5,8,5,0],[8,10,6,0]])
 natural=np.radians([[5,8,4,0],[18,20,12,0],[18,20,12,0],[18,20,12,0],[28,18,10,0]])
 lo=np.r_[seed-.045,-.14,.045,np.radians([-16,0,-5]),np.tile(np.radians([0,0,0,-28]),5)]
 hi=np.r_[seed+.045,-.065,.085,np.radians([16,9,5]),np.tile(np.radians([50,48,32,28]),5)]
 lo[6:10]=np.radians([0,0,0,-35]);hi[6:10]=np.radians([30,35,25,35])
 x0=np.r_[seed,-.10,.060,np.radians([0,4,0]),natural.flatten()]
 targets=np.array([keypoint(m,y)+[0,0,.009] for m,y in zip(homes,ys)])
 use=np.array([1,1,1,1,1] if s=='R' else [1,0,0,0,1])
 rest=np.array(RIG[s]['rest_verts']);region=rest[(rest[:,1]>.045)&(rest[:,1]<.095)]
 # 12 representative low palmar points; this is only planning clearance, final screen uses evaluated mesh.
 palm=region[np.argsort(region[:,2])[:12]]
 def initres(x):
  q=x[6:].reshape(5,4);R=palmrot(x);pads=allpads(s,q)@R.T+x[:3];pv=palm@R.T+x[:3]
  return np.r_[((pads-targets)*use[:,None]*1000).flatten(),((q-natural)*8).flatten(),(x[:3]-x0[:3])*80,(x[3:6]-x0[3:6])*8,np.maximum(safeheight(pv)+.006-pv[:,2],0)*1000]
 fit=least_squares(initres,x0,bounds=(lo,hi),max_nfev=160,ftol=1e-8,xtol=1e-9,gtol=1e-7)
 base=fit.x.copy();homeq=base[6:].reshape(5,4).copy()
 if s=='R':qrest[:,3]=homeq[:,3]*.65
 else:qrest[[0,4],3]=homeq[[0,4],3]*.7
 # Start in coordinated idle, not the contact-fit pose.
 x=base.copy();x[6:]=qrest.flatten();lastdelta=np.zeros_like(x)
 vmax=np.r_[np.full(3,.32),np.full(3,np.radians(70)),np.full(20,np.radians(360))]
 amax=np.r_[np.full(3,14.),np.full(3,np.radians(2400)),np.full(20,np.radians(14400))]
 rows=[];roots=[];Rrows=[];padsrows=[];targetrows=[];states=[];diagnostics=[]
 for i,t in enumerate(times):
  weights=np.zeros(5);targets=np.zeros((5,3));ref=qrest.copy();st=['RELAXED_IDLE']*5;activation=np.zeros(5)
  for n in ns:
   j=n['finger']-1;a=n['note_on'];b=n['note_off'];w=0
   if a-.16<=t<a:
    u=float(smooth((t-(a-.16))/.16));st[j]='PREPARING';w=u;target=keypoint(n['midi_note'],ys[j])+[0,0,.022*(1-u)]
   elif a<=t<b:
    st[j]='ACTIVE_PRESS';w=1.;target=keypoint(n['midi_note'],ys[j],out['key_angles'][i,n['key_index']])
   elif b<=t<b+.14:
    u=float(smooth((t-b)/.14));st[j]='RELEASING';w=1-u;target=keypoint(n['midi_note'],ys[j],out['key_angles'][i,n['key_index']])+[0,0,.027*u]
   if w>0:
    weights[j]=w;activation[j]=w;targets[j]=target
  # Correlated, small passive excursion with active thumb/little loading, never random.
  drive=activation[4]-.6*activation[0] if s=='L' else float(np.dot(activation,[.3,.6,.8,.7,1]))
  for j in range(5):
   coupled=qrest[j]+np.radians([2.5,1.8,1.0,.5])*drive*(.8 if j in [0,4] else 1)
   ref[j]=(1-activation[j])*coupled+activation[j]*homeq[j]
  # Braking envelope prevents the temporal box becoming infeasible at a physical bound.
  astep=amax*DT*DT
  # Exact discrete stopping sum: D(v)=sum(max(v-k*a_step,0)), k=0..n-1.
  # Include the final partial step; continuous or trapezoidal approximations
  # underestimate this distance when the last displacement is below a_step.
  def stopping_step(distance):
   distance=np.maximum(distance,0);n=np.maximum(1,np.ceil((np.sqrt(1+8*distance/astep)-1)/2))
   return (distance+astep*n*(n-1)/2)/n
  allowed=np.minimum(vmax*DT,stopping_step(hi-x))
  lowerallowed=np.minimum(vmax*DT,stopping_step(x-lo))
  low=np.maximum(lo,x-lowerallowed);high=np.minimum(hi,x+allowed)
  low=np.maximum(low,x+lastdelta-amax*DT*DT);high=np.minimum(high,x+lastdelta+amax*DT*DT)
  assert np.all(high>=low-1e-9),('TEMPORAL_BOUND_INFEASIBLE',s,i,[(int(k),float(x[k]),float(lastdelta[k]),float(low[k]),float(high[k])) for k in np.flatnonzero(high<low-1e-9)])
  if np.any(high-low<1e-12):
   # A zero-width temporal box prescribes a UNIQUE next pose, which is generally
   # not the current pose during braking. Keep that prescribed point.
   tight=high-low<1e-12;center=np.clip((low[tight]+high[tight])/2,lo[tight],hi[tight]);low[tight]=np.maximum(lo[tight],center-1e-12);high[tight]=np.minimum(hi[tight],center+1e-12)
  pred=x+lastdelta
  def residual(v):
   q=v[6:].reshape(5,4);R=palmrot(v);pads=allpads(s,q)@R.T+v[:3];pv=palm@R.T+v[:3]
   # Relaxed idle fingers track their RSSF-derived curve; active fingers share root support.
   poseweight=3*weights+70*(1-weights)
   idleclear=np.maximum(safeheight(pads)+.006-pads[:,2],0)*(1-weights)
   return np.r_[((pads-targets)*weights[:,None]*1000).flatten(),((q-ref)*poseweight[:,None]).flatten(),(v[:3]-base[:3])*90,(v[3:6]-base[3:6])*12,(v[:3]-pred[:3])*250,(v[3:6]-pred[3:6])*5,(v[6:]-pred[6:])*5,np.maximum(safeheight(pv)+.006-pv[:,2],0)*1000,idleclear*1500]
  start=np.clip(pred,low+1e-12,high-1e-12)
  fitstep=least_squares(residual,start,bounds=(low,high),max_nfev=24,ftol=1e-6,xtol=1e-7,gtol=1e-6)
  prev=x.copy();x=fitstep.x;delta=x-prev
  assert np.all(np.abs(delta-lastdelta)<=astep+1e-8),('ACCELERATION_CONSTRAINT_BROKEN',s,i)
  assert np.all(np.abs(delta)<=vmax*DT+1e-8),('VELOCITY_CONSTRAINT_BROKEN',s,i)
  lastdelta=delta;q=x[6:].reshape(5,4);R=palmrot(x)
  rows.append(q.copy());roots.append(x[:3].copy());Rrows.append(R);padsrows.append(allpads(s,q)@R.T+x[:3]);targetrows.append(targets.copy());states.append(st);diagnostics.append(fitstep.nfev)
  if i%60==0:print(s,'sample',i,'root',np.round(x[:3],4).tolist(),flush=True)
 out[s+'_q']=np.array(rows);out[s+'_root']=np.array(roots);out[s+'_rotation']=np.array(Rrows);out[s+'_pads']=np.array(padsrows);out[s+'_targets']=np.array(targetrows)
 state_rows[s]=states
 plans[s]={'reference_root_xyz_m':base[:3].tolist(),'reference_root_yaw_pitch_roll_deg':np.degrees(base[3:6]).tolist(),'reference_contact_joint_increments_deg':np.degrees(homeq).tolist(),'idle_RSSF_increments_deg':np.degrees(qrest).tolist(),'root_travel_axis_mm':np.ptp(out[s+'_root'],axis=0).tolist(),'solver_max_evaluations':max(diagnostics),'max_step_deg':float(np.max(np.abs(np.degrees(np.diff(out[s+'_q'],axis=0)))))}
 plans[s]['root_travel_axis_mm']=(np.ptp(out[s+'_root'],axis=0)*1000).tolist()
np.savez_compressed(P/'procedural_motion.npz',**out)
dump('HAND_POSTURE_COORDINATION_R1.json',{'policy':policy,'hands':plans,'times':times.tolist(),'states_by_finger_THUMB_INDEX_MIDDLE_RING_LITTLE':state_rows,'same_key_angles':bool(np.array_equal(out['key_angles'],old['key_angles']))})
print(json.dumps(plans,indent=2),flush=True)
