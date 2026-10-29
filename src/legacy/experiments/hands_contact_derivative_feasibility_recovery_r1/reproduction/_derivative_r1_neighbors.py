import sys,os,time,json,subprocess
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));start=time.monotonic()
import contact_solver as cs
P=O.parent/'hands_contact_constrained_trajectory_planning_r1';actual=json.loads((P/'LOCAL_PATH_ACTUAL_SAMPLES.json').read_text());traj=json.loads((P/'LOCAL_CONTROL_TRAJECTORY.json').read_text())
end=json.loads((O/'runs/recovery_dynamic_actual.json').read_text());assert end['all_gates'];rows=[]
for s in [r for r in traj['samples'] if r['id'] in ['candidate_027','candidate_028']]:
 a=next(x for x in actual if x['id']==s['id']);name='adjacent_'+s['id'];r=cs.run_solve(name,s['latent'],s['contacts'],s['display_time'],cs.np.array(a['key_angles']),30)
 with (O/'logs'/f'{name}.log').open('w') as f:subprocess.run([r'D:\blender\blender.exe','-b','-t','4','--python',str(O/'blender_verify.py'),'--',str(O/'runs'/f'{name}.json')],stdout=f,stderr=subprocess.STDOUT,timeout=25,check=True)
 rows.append(json.loads((O/'runs'/f'{name}_actual.json').read_text()))
rows.append(end);speeds=[]
for a,b in zip(rows,rows[1:]):
 dt=b['display_time']-a['display_time'];vel=(cs.np.array(b['latent'])-a['latent'])/dt;w=cs.np.linalg.norm(cs.np.array(b['wrist_world_m'])-a['wrist_world_m'])*1000/dt;speeds.append(dict(dt=dt,wrist_speed_mm_s=float(w),latent_velocity=vel.tolist(),component_limits_pass=bool(cs.np.all(abs(vel)<=cs.np.r_[[500]*3,[120]*3,[240]*4,5,8])),wrist_limit_pass=bool(w<=500)))
r=dict(states=rows,adjacent_secants=speeds,all_static_gates=all(x['all_gates'] for x in rows),motion_compatible=all(x['component_limits_pass'] and x['wrist_limit_pass'] for x in speeds),continuous_path_verified=False)
(O/'ADJACENT_RECOVERY.json').write_text(json.dumps(r,indent=2));(O/'NEIGHBOR_BUDGET.json').write_text(json.dumps(dict(charged_seconds=time.monotonic()-start),indent=2))
