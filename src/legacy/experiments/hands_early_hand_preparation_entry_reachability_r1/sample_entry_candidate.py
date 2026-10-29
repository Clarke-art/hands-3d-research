from coupled_model import *
from kinematic_derivative_api import motion_derivatives
cfg=json.loads((O/'EXPERIMENT_CONFIG.json').read_text(encoding='utf8'));data=json.loads((O/'ENTRY_SOLVE_INPUT.json').read_text(encoding='utf8'));result=json.loads((O/'ENTRY_CORRECTION_RESULT.json').read_text(encoding='utf8'));times=np.array(result['times']);Z=np.array(result['latents']);MD=motion_derivatives(F)
assert np.max(abs(Z[0]-np.array(cfg['initial_latent'])))<1e-12
sequence=json.loads((O/'CONTACT_STATE_SEQUENCE.json').read_text(encoding='utf8'))['all_source_sequence'];desc={ct['note_id']:ct for ct in cfg['contacts']}
def pose(t):
 i=min(max(np.searchsorted(times,t,side='right')-1,0),len(times)-2);f=(t-times[i])/(times[i+1]-times[i]);z=Z[i]*(1-f)+Z[i+1]*f;zd=(Z[i+1]-Z[i])/(times[i+1]-times[i]);return z,zd,i
grid=sorted(set([times[0]+i/120 for i in range(int((times[-1]-times[0])*120)+1)]+times.tolist()+[times[-1],cfg['junction']-1e-6,cfg['junction']+1e-6]+[cfg['junction']+f*(times[-1]-cfg['junction']) for f in np.arange(.0625,1,.0625)]+json.loads((O/'HOLD_ADAPTIVE_TIMES.json').read_text(encoding='utf8'))))
requests=[];motion=[]
for i,t in enumerate(grid):
 z,zd,seg=pose(t);cts=[desc[m['note_id']] for m in sequence if m['hand']=='R' and m['required_contact'] and m['display_interval'][0]<=t<m['display_interval'][1] and m['note_id'] in desc]
 if abs(t-cfg['junction'])<1e-12:cts=cfg['contacts']
 assert cts
 w,q=KIN(z);v,a,qr=MD(z,zd,np.zeros(12));speed=float(np.linalg.norm(np.array(v)));joint=float(np.max(abs(np.array(qr))));requests.append(dict(id='entry_sample_'+str(i),display_time=t,contacts=cts,latent=z.tolist(),state=state(z).tolist()))
 motion.append(dict(time=t,segment=int(seg),wrist_world_m=np.array(w).ravel().tolist(),wrist_speed_mm_s=speed,mapped_joint_rate_max_deg_s=joint,latent_rates=zd.tolist(),within_segment_acceleration_mm_s2=float(np.linalg.norm(np.array(a))),domain_pass=bool(np.all(z>=LOW-1e-8)&np.all(z<=HIGH+1e-8)),wrist_pass=bool(speed<=500+1e-5),joint_pass=bool(joint<=240+1e-5),latent_pass=bool(np.all(abs(zd)<=np.array(data['motion_bounds']['latent_velocity'])+1e-5))))
dense=[];derivative_errors=[];jumps=[]
for seg in range(len(times)-1):
 zd=(Z[seg+1]-Z[seg])/(times[seg+1]-times[seg]);peak=0.;jointpeak=0.;accpeak=0.
 for f in np.linspace(0,1,101):
  z=(1-f)*Z[seg]+f*Z[seg+1];v,a,qr=MD(z,zd,np.zeros(12));peak=max(peak,float(np.linalg.norm(np.array(v))));jointpeak=max(jointpeak,float(np.max(abs(np.array(qr)))));accpeak=max(accpeak,float(np.linalg.norm(np.array(a))))
  if f in [0.,.5,1.]:
   h=1e-6;vm=(np.array(KIN(z+h*zd)[0])-np.array(KIN(z-h*zd)[0]))*1000/(2*h);qm=(state(z+h*zd)[6:]-state(z-h*zd)[6:])/(2*h);derivative_errors.append(dict(segment=seg,fraction=float(f),wrist_error_mm_s=float(np.max(abs(vm.ravel()-np.array(v).ravel()))),joint_error_deg_s=float(np.max(abs(qm-np.array(qr).ravel())))))
 dense.append(dict(segment=seg,start=float(times[seg]),end=float(times[seg+1]),dense_count=101,maximum_wrist_speed_mm_s=peak,maximum_joint_rate_deg_s=jointpeak,maximum_within_segment_acceleration_mm_s2=accpeak))
 if seg:
  za=(Z[seg]-Z[seg-1])/(times[seg]-times[seg-1]);vl=MD(Z[seg],za,np.zeros(12))[0];vr=MD(Z[seg],zd,np.zeros(12))[0];jumps.append(dict(time=float(times[seg]),wrist_velocity_jump_mm_s=float(np.linalg.norm(np.array(vr-vl))),acceleration_at_knot='UNDEFINED_WHEN_VELOCITY_JUMP_NONZERO; no finite comfort claim'))
save('ENTRY_SAMPLE_REQUESTS.json',requests);save('ENTRY_CANDIDATE_MOTION.json',dict(samples=motion,dense_segment_checks=dense,analytic_vs_fd=derivative_errors,knot_velocity_jumps=jumps,interpolation='Piecewise linear latent states; exact frozen FK and reference-family mapping',C0_position_continuity=True,C1_velocity_continuity=all(r['wrist_velocity_jump_mm_s']<1e-5 for r in jumps),finite_sampling_not_continuous_collision_proof=True))
save('EARLY_PREPARATION_TRAJECTORY.json',dict(task=cfg['task'],authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',status='EXECUTED_UNVALIDATED_CANDIDATE',solver_status=result['status'],numeric_violation=result['violation'],fixed_B2_start=True,start=float(times[0]),end=float(times[-1]),knots=[dict(time=float(t),latent=z.tolist(),state=state(z).tolist()) for t,z in zip(times,Z)],sample_count=len(requests),actual_samples_file='ENTRY_ACTUAL_SAMPLES.json',motion_file='ENTRY_CANDIDATE_MOTION.json',interpolation='Piecewise linear in existing 12 latent controls; all states generated from unchanged natural reference family',complete_entry_pass=False,formal_Action_created=False))
print('ENTRY_SAMPLES',len(requests),[(r['maximum_wrist_speed_mm_s'],r['maximum_joint_rate_deg_s']) for r in dense],flush=True)
