from coordination import *
import time
LIMIT=np.array([3.,5.,3.,2.,2.]) # mm world X/Y/Z; degrees world X pitch and Z yaw
TIMES=[3.75,3.825,3.85]
R4=ROOT/'audits/minuet_stage_c_r4_multi_finger_coordinated_clearance'
class Bounded(Context):
 def __init__(self,t):
  self.root_delta=np.zeros(5);self.pivot=None
  super().__init__([t])
  _,poses,_=super().skin(np.zeros(12),True)
  self.pivot=(self.world[0]@poses[0,BN['WRIST_R']])[:3,3]
 def skin(self,delta,return_pose=False):
  V=super().skin(delta,return_pose)
  if self.pivot is None:return V
  assert not return_pose
  R=Rotation.from_rotvec(np.radians([self.root_delta[3],0,self.root_delta[4]])).as_matrix()
  return (V-self.pivot)@R.T+self.pivot+self.root_delta[:3]/1000
 def objective(self,x):
  self.root_delta=x[12:]
  return np.r_[super().residual(x[:12]).ravel(),x[12:]/LIMIT*2.]
def lock():
 assert not (P/'STRATEGY_LOCK.json').exists()
 parity=[]
 for k,t in enumerate(D['times']):
  ctx=Bounded(t);parity.append(dict(t=t,max_mm=np.linalg.norm(ctx.original[0]-D['actual_skin'][k],axis=-1).max()*1000))
 assert max(r['max_mm'] for r in parity)<.03
 roots=[]
 for i,t in enumerate(D['times']):
  roots.append((D['rig_world'][i]@D['pose_matrices'][i,BN['WRIST_R']])[:3,3])
 roots=np.array(roots)
 key=next(k for k in c.KEYS if k['midi_note']==75);v=np.array(key['geometry'][0]['vertices'])
 evidence=dict(source_times=D['times'],wrist_world_m=roots,wrist_envelope_mm=np.ptp(roots,axis=0)*1000,key_Dsharp5_size_mm=np.ptp(v,axis=0)*1000,skin_parity=parity)
 dump('ROOT_RANGE_EVIDENCE.json',evidence)
 dump('STRATEGY_LOCK.json',dict(baseline=M['baseline']['sha256'],purpose='FINITE_STATIC_A_B_COMPARISON_ONLY',times_video_sec=TIMES,times_music_sec=np.array(TIMES)-.35,fixed_A='Reuse R4 valid 3.825s 12-DOF result without any fixed-root reoptimization; neighboring original R1 states are references only, not optimized A solutions.',joint_degrees=['MCP flex','PIP flex','DIP flex','MCP spread'],joint_delta_limits=DELTA_LIMIT,joint_absolute_bounds=[[0,75],[0,95],[0,65],[-28,28]],root_dofs=['world X mm','world Y mm','world Z mm','world X pitch deg','world Z yaw deg'],root_bounds_symmetric=LIMIT,root_pivot='Original WRIST_R world position; world rotation vector [pitch,0,yaw], no roll parameter',range_rationale='X <=3 mm: <27% of 11.274 mm black-key width; Y <=5 mm: <8% of 64.866 mm black-key length; Z <=3 mm: <20% of 15.444 mm black-key height. Original wrist local envelope saved separately; these conservative research caps are not a proven naturalness threshold. Rotations capped at 2 degrees, same order as original late local orientation excursion; original total route untouched.',objective='Identical R4 skin, active/release moving surface, 7 local black keys, adjacent pairs, source joint prior; add root normalized L2 weight2. No new release target or joint-domain relaxation.',seed='Original C1 zero joint/root increments independently for each of three static states; no multistart, no choosing among outcomes.',per_pose_max_nfev=160,ftol=1e-7,xtol=1e-7,gtol=1e-7,diff_step=1e-4,termination_policy='Save every result and validate exact Blender skin; no parameter retuning, range expansion or rerun. Independent static samples do not establish temporal continuity.',actual_validation='E5/D5 actual pad gap <=2 mm and horizontal <=0.5 mm; local actual skin intersection witnesses and black key depth, three unchanged source cameras; no numerical success alone establishes feasibility.',script_sha256={n:sha(P/n) for n in ['bounded_static.py','coordination.py']},new_dynamic_solves=0,new_dynamic_candidates=0))
 print('LOCKED',json.dumps(evidence,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),flush=True)
def solve():
 policy=read(P/'STRATEGY_LOCK.json')
 for n,h in policy['script_sha256'].items():assert sha(P/n)==h
 assert not (P/'STATIC_ATTEMPT_STARTED.json').exists(),'Do not rerun static optimization'
 dump('STATIC_ATTEMPT_STARTED.json',dict(time=time.time(),static_batch=1,states=3,dynamic_solves=0))
 rows=[]
 for t in TIMES:
  ctx=Bounded(t);lo,hi=bounds([t]);fit=least_squares(ctx.objective,np.zeros(17),bounds=(np.r_[lo.ravel()+1e-6,-LIMIT],np.r_[hi.ravel()-1e-6,LIMIT]),max_nfev=160,ftol=1e-7,xtol=1e-7,gtol=1e-7,diff_step=1e-4)
  ctx.root_delta=fit.x[12:];V=ctx.skin(fit.x[:12]);black,sdf=ctx.black_clearance(V)
  rows.append(dict(video_sec=t,music_sec=t-.35,delta_deg=fit.x[:12].reshape(3,4),actual_degrees=original_degrees([t])[0]+fit.x[:12].reshape(3,4),root_delta=fit.x[12:],root_pivot_world_m=ctx.pivot,nfev=fit.nfev,status=fit.status,success=bool(fit.success),message=fit.message,cost=fit.cost,optimality=fit.optimality,active_mask=fit.active_mask,contacts=ctx.contacts(V)[1],pair_field_max_mm=ctx.pair_clearance(V).max(),black_field_max_mm=black.max()))
  dump('BOUNDED_STATIC_RESULTS.json',dict(complete=len(rows)==3,poses=rows,static_batch_count=1,new_dynamic_solves=0,new_dynamic_candidates=0))
  print('BOUNDED_STATIC',t,json.dumps(rows[-1],default=lambda v:v.tolist() if hasattr(v,'tolist') else v),flush=True)
if __name__=='__main__':
 if '--lock' in sys.argv:lock()
 elif '--solve' in sys.argv:solve()
