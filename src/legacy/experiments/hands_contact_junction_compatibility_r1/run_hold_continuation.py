import sys,json,time,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from contact_solver import *
assert json.loads((O/'runs/junction_2_actual.json').read_text())['all_gates']
prev=O.parent/'hands_contact_state_motion_planner_comparison_r1';p2=json.loads((prev/'P2_SLSQP_SOLVE.json').read_text());z=np.array(p2['latent']);contacts=[I['contacts'][0]];data=np.load(O/'BOUNDARY_KEY_STATES.npz');angles=data['angles'][1];times=np.linspace(I['continuation_start_time'],I['junction_time']-1/120,7)[1:];trust=np.r_[[4,4,2],[2,2,2],[5,5,5,5],.12,.18];records=[];total=sum(json.loads(f.read_text())['elapsed_seconds'] for f in (O/'runs').glob('junction_?.json'))
for i,t in enumerate(times,1):
 if total+35>500:break
 r=run_solve('hold_'+str(i),z,contacts,float(t),angles,35,goal=I['next'],trust=trust);total+=r['elapsed_seconds'];file=O/'runs'/('hold_'+str(i)+'.json')
 with (O/'logs'/('hold_'+str(i)+'_actual.log')).open('w') as log:process=subprocess.run([r'D:\blender\blender.exe','-b','-t','4','--python',str(O/'blender_verify.py'),'--',str(file)],stdout=log,stderr=subprocess.STDOUT,timeout=60)
 af=file.with_name(file.stem+'_actual.json');assert af.exists();a=json.loads(af.read_text());records.append(dict(solve_file=str(file.relative_to(O)),actual_file=str(af.relative_to(O)),actual_gates=a['all_gates'],solve_seconds=r['elapsed_seconds'],next_surface_distance_mm=a['next_pad_distance_to_playable_surface_mm']));print('HOLD_ACTUAL',i,a['all_gates'],a['next_pad_distance_to_playable_surface_mm'],flush=True)
 if not a['all_gates']:break
 z=np.array(r['latent'])
(O/'HOLD_RUN_INDEX.json').write_text(json.dumps(dict(records=records,total_numerical_including_junction_seconds=total,max_new_nodes=6,previous_good_as_next_initialization=True,stop_on_actual_failure=True,inter_node_continuity='NOT_YET_PROVEN',no_path_generated=True),indent=2))
