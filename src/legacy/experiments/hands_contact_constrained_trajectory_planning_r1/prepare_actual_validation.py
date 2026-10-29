import sys,json,math,ast
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from rig_model import *
r=json.loads((O/'CASADI_LOCAL_SOLVE.json').read_text());I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());old=O.parent/'hands_contact_junction_compatibility_r1';oldtraj=json.loads((old/'LOCAL_CONTROL_TRAJECTORY.json').read_text());C=np.array(r['coefficients']);start=r['source_start'];J=r['junction'];end=r['end'];dur=[J-start,end-J]
def curve(ph,t,order=0):
 cc=C[ph].copy();d=5;fac=1;s=(t-[start,J][ph])/dur[ph]
 for _ in range(order):cc=np.diff(cc,axis=1);fac*=d/dur[ph];d-=1
 return fac*sum(math.comb(d,k)*s**k*(1-s)**(d-k)*cc[:,k] for k in range(d+1))
ts=[x['display_time'] for x in oldtraj['samples']]+list(np.linspace(start,J,9))+list(np.linspace(J,end,17))+[J-1e-6,J+1e-6];ts=sorted(set(round(float(t),12) for t in ts));rows=[]
for n,t in enumerate(ts):
 ph=0 if t<J-1e-9 else 1;z=curve(ph,t);cts=I['contacts'] if abs(t-J)<1e-9 else [I['contacts'][0 if t<J else 1]];rows.append(dict(id='candidate_'+str(n).zfill(3),display_time=t,latent=z.tolist(),state=state(z).tolist(),contacts=cts,latent_velocity=curve(ph,t,1).tolist(),latent_acceleration=curve(ph,t,2).tolist()))
boundary=dict(position_jump_latent=(curve(1,J)-curve(0,J)).tolist(),velocity_jump_latent_per_s=(curve(1,J,1)-curve(0,J,1)).tolist(),acceleration_jump_latent_per_s2=(curve(1,J,2)-curve(0,J,2)).tolist(),position_max_mixed_units=float(abs(curve(1,J)-curve(0,J)).max()))
# Explicit one-sided configuration at same event time, no fictitious dt for speed.
left=curve(0,J);rows.append(dict(id='junction_left_limit',display_time=J,latent=left.tolist(),state=state(left).tolist(),contacts=I['contacts'],side='left_limit'))
trajectory=dict(status='FAILED_NLP_LAST_ITERATE_NOT_ACCEPTED_PATH',candidate_count=1,coefficients=r['coefficients'],interval=[start,end],junction=J,samples=rows,phase_jumps=boundary,sampling='120Hz original grid and exact boundary; old failure times preserved; each phase subdivided at~960Hz for collision/high-curvature risk plus event +/-1microsecond; extra exact left limit',not_safe_initial_path=True,not_pass=True)
(O/'LOCAL_CONTROL_TRAJECTORY.json').write_text(json.dumps(trajectory,indent=2));print('samples',len(rows),'jump',boundary['position_max_mixed_units'],'wall',r['numerical_wall_seconds'],'solverconstruction',r['solver_construction_seconds'])
# Reuse existing verifier source with new output label; source assets remain readonly.
s=(O/'verify_local_path.py').read_text(encoding='utf8');s=s.replace("row=measure(r);out.append(row)","row=measure(r);row['scope']='FAILED_NLP_TRAJECTORY_SAMPLE';out.append(row)");(O/'verify_local_path.py').write_text(s,encoding='utf8')
err=json.loads((O/'ADAPTATION_SX_BUILD_INTERRUPTED.json').read_text(encoding='utf-8-sig'));err.update(record_status='SUPERSEDED_BY_COMPLETED_SOLVER_OUTPUT',stop_command_did_not_find_process=True,actual_termination=r['stats']['return_status'],actual_IPOPT_iterations=r['stats']['iter_count'],note='Redirected stdout buffered. Prior interpretation of no iterations was wrong; process completed before attempted stop. CASADI_LOCAL_SOLVE.json is authoritative.');(O/'ADAPTATION_SX_BUILD_INTERRUPTED.json').write_text(json.dumps(err,indent=2))
