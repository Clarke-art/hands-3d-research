from support import *
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(A2))
import coordinated_motion as cm
import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
P=read(O/'POLICY.json');assert sha(O/'POLICY.json')==read(O/'POLICY_LOCK.json')['policy_sha256']
assert not (O/'BATCH_STARTED.json').exists()
dump('BATCH_STARTED.json',dict(attempt=1,restarts=0,script_sha256=sha(__file__),time=time.time()))
I=read(O/'INPUT_BINDINGS.json');events=I['p3_events'];co=cm.EventCoordinator(events,cm.DEFAULT_POLICY)
shift=.35
# Reuse only frozen-model initialization and FK/LBS definitions, no historical solver/search.
code=(PREV/'evaluate.py').read_text(encoding='utf-8-sig')
exec(compile(code[code.index('M=read(MODEL/'):code.index('ref_t=REF')],str(PREV/'evaluate.py')+':frozen_fk_lbs_only','exec'))
times=np.array(P['phase_times_sec']);K=len(times)
ref_t=REF['music_times']+shift
NUM=dict(np.load(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/source_numeric.npz'))
qsource=np.column_stack([np.interp(times,NUM['times'],NUM['qdeg'].reshape(-1,20)[:,j]) for j in range(20)]).reshape(K,5,4)
pf=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/RIG_PREFLIGHT.json')
BASE=np.array(cm.BASE);BASEMAT=np.array(I['static_root_base_matrix']);RELROOT=np.array(pf['full_root_rig_relation'])
def world(root):
 T=np.eye(4);T[:3,3]=BASE+root[:3]/1000
 RR=np.eye(4);RR[:3,:3]=cm.extra_rotation(root[3:6]);N=np.eye(4);N[:3,3]=-BASE
 return T@RR@N@BASEMAT@RELROOT
def evaluate(root,q,ids):
 basis=np.tile(np.eye(3),(K,len(REST),1,1))
 for j,d in enumerate(DIGITS):
  for k,name in enumerate(NAMES[j]):
   basis[:,BN[name]]=rot(np.radians(q[:,j,k]),AXES[j][k])
   if k==0:basis[:,BN[name]]=rot(np.radians(q[:,j,3]),SPREAD[j])@basis[:,BN[name]]
 return skin(basis,np.broadcast_to(world(root),(K,4,4)),ids)[0]
# Full native model parity against actual C1 evidence, no optimizer.
ix=np.array([np.argmin(abs(ref_t-t)) for t in times])
vv,_=skin(REF['joint_basis'][ix,:,:3,:3],REF['rig_world'][ix],np.arange(len(W)))
error=float(np.max(np.linalg.norm(vv-REF['verts'][ix],axis=-1))*1000);assert error<.01,error
dump('FK_LBS_SELF_CHECK.json',dict(samples=K,vertices=len(W),max_native_rebuild_error_mm=error))
angles=np.array([[np.interp(t,ref_t,REF['key_angles'][:,j]) for j in range(88)] for t in times])
tasks=[co.tasks(t) for t in times]
low=np.r_[P['root_low'],np.tile(cm.B[:,0].ravel(),K),co.xy_low[8:14].ravel()]
high=np.r_[P['root_high'],np.tile(cm.B[:,1].ravel(),K),co.xy_high[8:14].ravel()]
# Decode C1 root in A2 coordinates; only used as deterministic starting seed/reference.
from scipy.spatial.transform import Rotation
source_roots=[]
for idx in ix:
 C=REF['rig_world'][idx]@np.linalg.inv(RELROOT)@np.linalg.inv(BASEMAT)
 extra=Rotation.from_matrix(C[:3,:3]).as_euler('xyz',degrees=True)
 pos=C[:3,:3]@BASE+C[:3,3]
 source_roots.append(np.r_[(pos-BASE)*1000,extra])
source_roots=np.array(source_roots)
x0=np.r_[np.median(source_roots,axis=0),qsource.ravel(),co.xy_seed[8:14].ravel()];x0=np.clip(x0,low+1e-7,high-1e-7)
def unpack(x):
 root=x[:6];q=x[6:6+20*K].reshape(K,5,4);xy=co.xy_seed.copy();xy[8:14]=x[6+20*K:].reshape(6,2)
 return root,q,xy
padids=[m['mesh_vertex'] for m in MARK]
boxp=np.array([co.keys[m]['press_pivot'] for m in co.boxkeys]);boxlo,boxhi=co.boxlo,co.boxhi
boxrot=cm.rotations(-angles[:,np.array(co.boxkeys)-21],[1,0,0])
calls=0;started=time.perf_counter();last=x0.copy();sizes=[]
def residual(x,timed=True):
 global calls,last,sizes
 if timed and time.perf_counter()-started>54:raise TimeoutError('FIXED_SINGLE_BATCH_WALL_CAP')
 calls+=1;last=x.copy();root,q,xy=unpack(x);pads=evaluate(root,q,padids);out=[];sizes=[]
 states=np.c_[np.tile(root,(K,1)),q.reshape(K,20)];_,jp=cm.fk_batch(states)
 for k,t in enumerate(times):
  rr=[];assigned=set();allowed=[]
  for j,i,lift,w in tasks[k]:
   assigned.add(j);key=co.keys[events[i]['midi_note']];s=co.surfaces[i];pv=np.array(key['press_pivot'])
   target=cm.rotations(angles[k,events[i]['key_index']],key['press_axis'])@(np.r_[xy[i]/1000,s['z']+.0005]-pv)+pv;target[2]+=lift
   rr.extend((pads[k,j]-target)*1000*w)
   if w>1:allowed.append((j,events[i]['midi_note']))
  pv=np.einsum('bij,dbj->dbi',boxrot[k],pads[k,:,None,:]-boxp[None,:,:])+boxp[None,:,:]
  dd=np.abs(pv-(boxlo+boxhi)/2)-(boxhi-boxlo)/2
  sdf=np.linalg.norm(np.maximum(dd,0),axis=-1)+np.minimum(np.max(dd,axis=-1),0)
  margin=np.full(sdf.shape,.003)
  for j,midi in allowed:margin[j,np.array(co.boxkeys)==midi]=-.004
  rr.extend((np.maximum(margin-sdf,0)*1000*cm.DEFAULT_POLICY['clearance_weight']).ravel())
  for j in range(5):
   if j not in assigned:rr.append(max(0,.005-pads[k,j,2])*1000*2)
   for point in jp[k,j,1:]:
    covers=(point[0]>boxlo[:,0])&(point[0]<boxhi[:,0])&(point[1]>boxlo[:,1])&(point[1]<boxhi[:,1]);top=float(np.max(boxhi[covers,2])) if covers.any() else -.010
    rr.append(max(0,top+.005-point[2])*1000*.5)
  rr.extend((q[k]-cm.NEUTRAL).ravel()*.055)
  rr.extend((q[k]-qsource[k]).ravel()*.055)
  rr.extend(root[3:6]*.20);rr.extend((root[:3]-np.median(source_roots[:,:3],axis=0))*[.015,.035,.06])
  sizes.append(len(rr));out.extend(rr)
 out.extend((np.diff(q.reshape(K,20),axis=0)/np.diff(times)[:,None]*.020).ravel())
 out.extend(((xy[8:14]-co.xy_seed[8:14])*.12).ravel())
 return np.array(out)
r0=residual(x0,False);J=lil_matrix((len(r0),len(x0)),dtype=np.int8);row=0
for k,size in enumerate(sizes):
 cols=list(range(6))+list(range(6+20*k,6+20*(k+1)))
 for j,i,l,w in tasks[k]:
  if 8<=i<14:cols.extend([6+20*K+2*(i-8),6+20*K+2*(i-8)+1])
 J[row:row+size,cols]=1;row+=size
for k in range(K-1):J[row:row+20,6+20*k:6+20*(k+2)]=1;row+=20
J[row:,6+20*K:]=1
protect()
try:
 fit=least_squares(residual,x0,bounds=(low,high),jac_sparsity=J.tocsr(),max_nfev=45,ftol=1e-6,xtol=1e-6,gtol=1e-6)
 x=fit.x;meta=dict(success=bool(fit.success),nfev=fit.nfev,message=fit.message,optimality=float(fit.optimality),cost=float(fit.cost))
except TimeoutError as e:x=last;meta=dict(success=False,nfev=None,message=str(e),last_residual_evaluation_only=True)
root,q,xy=unpack(x);pads=evaluate(root,q,padids)
rows=[]
for k,t in enumerate(times):
 contacts=[]
 for j,i,l,w in tasks[k]:
  s,h,g,near=surface_metrics(pads[k,j][None],co.keys[events[i]['midi_note']],angles[k,events[i]['key_index']])
  contacts.append(dict(finger=j+1,event=events[i]['note_id'],lift_mm=l*1000,weight=w,horizontal_mm=float(h[0]*1000),gap_mm=float(g[0]*1000),active_or_release=l==0 and w>=4,contact_pass=bool(h[0]*1000<=.03 and abs(g[0]*1000)<=3)))
 rows.append(dict(label=P['phase_labels'][k],time=t,contacts=contacts,root_xyz_mm=(BASE+root[:3]/1000)*1000,root_rotation_deg=root[3:6],q_deg=q[k],min_joint_bound_margin_deg=float(np.minimum(q[k]-cm.B[:,0],cm.B[:,1]-q[k]).min())))
delta=q-qsource;lower=[]
for k in range(K-1):
 dm=float(np.max(abs(delta[k+1]-delta[k])));dt=times[k+1]-times[k]
 lower.append(dict(start=P['phase_labels'][k],end=P['phase_labels'][k+1],available_sec=dt,max_added_joint_delta_deg=dm,conditional_min_sec_under_180_deg_s=dm/180,necessary_mean_added_deg_s=dm/dt,necessary_condition_pass=dm<=180*dt))
np.savez_compressed(O/'STATIC_LAYOUTS.npz',times=times,states=np.c_[np.tile(root,(K,1)),q.reshape(K,20)],contact_xy=xy,world=world(root),qsource=qsource,source_roots=source_roots,key_angles=angles)
dump('NUMERIC_RESULT.json',dict(solver=meta,elapsed_solver_and_diagnostics_seconds=time.perf_counter()-started,residual_calls=calls,variables=len(x),shared_root=True,root_delta_A2_mm=root[:3],root_extra_rotation_deg=root[3:6],root_xyz_mm=(BASE+root[:3]/1000)*1000,rows=rows,conditional_temporal_endpoint_checks=lower,no_trajectory=True))
protect();print('SINGLE_BATCH_DONE',meta,'seconds',round(time.perf_counter()-started,3))
for row in rows:print(row['label'],[(c['event'],round(c['horizontal_mm'],3),round(c['gap_mm'],3),c['contact_pass']) for c in row['contacts'] if c['active_or_release']])
