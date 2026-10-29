from bridge_model import *
import hashlib
results=[json.loads((O/(pid+'_RESULT.json')).read_text(encoding='utf8')) for pid in ['candidate_front','candidate_right']];plan=json.loads((O/'candidate_front_PLAN_EXECUTED.json').read_text(encoding='utf8'));T=np.array(results[0]['times']);Z=np.array(results[0]['latents']);event=CTX['time_span']['junction'];end=CTX['time_span']['first_full_press'];seq=json.loads((O/'CONTACT_STATE_SEQUENCE.json').read_text(encoding='utf8'))['all_source_sequence']
assert np.array_equal(Z,np.array(results[1]['latents']));assert results[1]['solver_called']==False
if len(sys.argv)>1:
 times=json.loads((O/'R2_ADAPTIVE_TIMES.json').read_text(encoding='utf8'));label='ADAPTIVE'
else:
 times=sorted(set([T[0]+i/120 for i in range(int((end-T[0])*120)+1)]+T.tolist()+[((a+b)/2) for a,b in zip(T,T[1:])]+[event+d for d in [-.002,-.001,-.00025,-1e-6,0,1e-6,.00025,.001,.002]]+[end,end+1e-6]));label='BASE'
requests=[];motion=[]
for i,t in enumerate(times):
 inside=t<=end;z,zd,zdd=numeric_curve(Z,T,min(t,end))
 if not inside:zd=np.zeros(12);zdd=np.zeros(12)
 cts=[]
 for m in seq:
  if m['hand']==CTX['hand'] and m['required_contact'] and m['display_interval'][0]<=t<m['display_interval'][1]:
   ct=next(ct for ct in CTX['contact_descriptors'] if ct['note_id']==m['note_id']);cts.append(ct)
 if abs(t-event)<1e-10:cts=[plan['held_contact'],plan['target_contact']]
 assert cts
 r=dict(id='r2_'+label.lower()+'_'+str(i),candidate_id='candidate_front',display_time=t,contacts=cts,latent=z.tolist(),state=state(z).tolist(),planned_phases=[p['name'] for p in plan['phase_schedule'] if p['window'][0]-1e-12<=t<=p['window'][1]+1e-12],trajectory_status='UNOPTIMIZED_INITIALIZER_PREVIEW_NOT_AN_IK_SOLUTION',scope='C01_R2_C1_CURVE_DEBUG_VALIDATION',post_scope_static_probe=not inside);requests.append(r)
 v,a,qr=MD(z,zd,zdd);motion.append(dict(time=t,latent=z.tolist(),latent_rate=zd.tolist(),wrist_position_m=np.array(KIN(z)[0]).ravel().tolist(),wrist_speed_mm_s=float(np.linalg.norm(np.array(v))),mapped_joint_rate_max_deg_s=float(np.max(abs(np.array(qr)))),acceleration_mm_s2=float(np.linalg.norm(np.array(a))),control_domain=bool(np.all(z>=LOW-1e-9)&np.all(z<=HIGH+1e-9)),speed_pass=bool(np.linalg.norm(np.array(v))<=500+1e-5),joint_speed_pass=bool(np.max(abs(np.array(qr)))<=240+1e-5),latent_rate_pass=bool(np.all(abs(zd)<=np.array(CTX['motion_bounds']['latent_velocity'])+1e-5)),post_scope_static_probe=not inside))
save('R2_'+label+'_REQUESTS.json',requests);save('R2_'+label+'_MOTION.json',motion)
if label=='BASE':
 dense=[];jumps=[];vlist=tangents([z for z in Z],T)
 for i in range(len(T)-1):
  ms=0.;mq=0.;ma=0.;domains=[]
  for u in np.linspace(0,1,501):
   z,zd,zdd=hermite(Z[i],Z[i+1],vlist[i],vlist[i+1],T[i+1]-T[i],u);v,a,qr=MD(z,zd,zdd);ms=max(ms,float(np.linalg.norm(np.array(v))));mq=max(mq,float(np.max(abs(np.array(qr)))));ma=max(ma,float(np.linalg.norm(np.array(a))))
   if np.any(z<LOW-1e-9) or np.any(z>HIGH+1e-9):domains.append(float(u))
  dense.append(dict(segment=i,time_interval=[float(T[i]),float(T[i+1])],checks=501,max_wrist_speed_mm_s=ms,max_joint_rate_deg_s=mq,max_acceleration_mm_s2=ma,domain_failed_fractions=domains))
  if i:
   a=numeric_curve(Z,T,float(T[i])-1e-10);b=numeric_curve(Z,T,float(T[i])+1e-10);jumps.append(dict(time=float(T[i]),control_position_one_sided_difference=float(np.max(abs(a[0]-b[0]))),control_velocity_one_sided_difference=float(np.max(abs(a[1]-b[1]))),C1_by_analytic_Hermite_definition=True,C2_not_claimed=True))
 save('R2_DENSE_MOTION_AUDIT.json',dict(segments=dense,knot_one_sided_checks=jumps,curve_C1_in_scope=True,no_geometric_continuity_proof=True,outside_scope_velocity_stopped_for_static_probe_only=True))
 save('R2_TRAJECTORY_DATA.json',dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',status='NO_FEASIBLE_IK_TRAJECTORY_FOUND',candidate_front=dict(solver_status=results[0]['status'],accepted_iterations=len(results[0]['history']),knots=[dict(time=float(t),latent=z.tolist(),state=state(z).tolist()) for t,z in zip(T,Z)],curve='C1 Hermite initialized from existing reference bank; optimizer returned initial curve after strict derivative rejection'),candidate_right=dict(status=results[1]['status'],solver_called=False,physical_curve_identical_to_front=True,geometry_evidence_reuse='Same full control states/time/contact set/original Action; no repeat of duplicate Blender sweeps'),full_bridge_PASS=False,HUMAN_NATURALNESS_REVIEW_PENDING=True))
 print('R2_SAMPLE_COUNT',len(requests),'densepeaks',max(x['max_wrist_speed_mm_s'] for x in dense),max(x['max_joint_rate_deg_s'] for x in dense),flush=True)
