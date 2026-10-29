import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
from rig_model import *
P=O.parent/'hands_contact_derivative_feasibility_recovery_r1';H=O.parent/'hands_contact_constrained_trajectory_planning_r1'
def read(p):return json.loads(p.read_text())
a=read(P/'ADJACENT_RECOVERY.json')['states'];old=read(H/'LOCAL_PATH_ACTUAL_SAMPLES.json');samples=read(H/'LOCAL_CONTROL_TRAJECTORY.json')['samples'];seq=read(O/'CONTACT_STATE_SEQUENCE.json');nodes=[]
for recovered in a:
 original=next(r for r in old if abs(r['display_time']-recovered['display_time'])<1e-12 and r['id'].startswith('candidate'))
 sample=next(r for r in samples if r['id']==original['id']);modes=[r for r in seq['all_source_sequence'] if r['hand']=='R' and r['display_interval'][0]<=sample['display_time']<r['display_interval'][1]]
 required=[r for r in modes if r['required_contact']];assert {(r['midi'],r['finger']) for r in required}=={(r['midi'],r['finger']) for r in sample['contacts']}
 assert np.max(abs(np.array(original['key_angles'])-recovered['key_angles']))<1e-12
 nodes.append(dict(id=original['id'],time=sample['display_time'],contacts=sample['contacts'],modes=modes,key_angles=original['key_angles'],original_failed=original,recovered=recovered,original_latent=sample['latent'],initial_latent=recovered['latent'],fixed=False))
segments=[];vl=np.r_[[500]*3,[120]*3,[240]*4,5,8]
for aa,bb in zip(nodes,nodes[1:]):
 dt=bb['time']-aa['time'];wdelta=(np.array(bb['recovered']['wrist_world_m'])-aa['recovered']['wrist_world_m'])*1000;dz=np.array(bb['initial_latent'])-aa['initial_latent'];dq=np.array(bb['recovered']['state'][6:])-aa['recovered']['state'][6:]
 segments.append(dict(dt=dt,allowed_wrist_displacement_mm=500*dt,wrist_displacement_vector_mm=wdelta.tolist(),wrist_displacement_mm=float(np.linalg.norm(wdelta)),wrist_speed_mm_s=float(np.linalg.norm(wdelta)/dt),latent_delta=dz.tolist(),latent_rate=(dz/dt).tolist(),mapped_joint_delta_deg=dq.tolist(),mapped_joint_rate_deg_s=(dq/dt).tolist(),violating_latent_indices=np.flatnonzero(abs(dz/dt)>vl).tolist(),contact_mode_switch=False,if_both_states_fixed='PROVEN_AVERAGE_SPEED_CONFLICT',actual_fixed=False))
valid=[r for r in old if r['all_gates'] and r['display_time']<nodes[0]['time'] and r['id'].startswith('candidate')];reference=max(valid,key=lambda r:r['display_time'])
out=dict(task='PIANO_TIME_COUPLED_CONTACT_RECOVERY_R1',authority='DESIGN_PROVISIONAL',nodes=nodes,segments=segments,preceding_valid_reference=reference,reference_use='Read-only external diagnostic, not fixed boundary; no approach compatibility claimed',following_reference=None,anchors=[],joint_domain=dict(lower=LOW.tolist(),upper=HIGH.tolist()),motion_bounds=dict(wrist_speed_mm_s=500,latent_velocity=vl.tolist(),mapped_joint_rate_deg_s=240,source=str(H/'TRAJECTORY_BENCHMARK_INPUT.json'),acceleration_and_jerk='diagnostic only in this discrete problem'),branch_conclusion='No mode switch. Independent optimizations lacked neighbor coupling and selected separated solutions. Distinct connected components of contact feasible set not proven. No proof that C01 or fixed MIDI timing is impossible.')
(O/'RECOVERY_TIMELINE_INPUT.json').write_text(json.dumps(out,indent=2));print([(n['id'],n['time']) for n in nodes]);print(segments)
