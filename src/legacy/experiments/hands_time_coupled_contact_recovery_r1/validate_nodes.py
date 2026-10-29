import sys,time,json,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent;start=time.monotonic();r=json.loads((O/'CORRECTION_SOLVE_RESULTS.json').read_text());assert r['numeric_gate'] and r['motion_numeric_pass'];(O/'NODE_REQUESTS.json').write_text(json.dumps(r['nodes'],indent=2))
subprocess.run([sys.executable,'-B',str(O/'make_batch_verifier.py')],check=True)
with (O/'logs/blender_nodes.log').open('w') as log:subprocess.run([r'D:\blender\blender.exe','-b','-t','4','--python',str(O/'batch_verify.py'),'--',str(O/'NODE_REQUESTS.json'),str(O/'NODE_ACTUAL_RAW.json')],stdout=log,stderr=subprocess.STDOUT,timeout=55,check=True)
rows=json.loads((O/'NODE_ACTUAL_RAW.json').read_text());assert len(rows)==3
import sys;sys.path.insert(0,str(O));from rig_model import np
segments=[]
for a,b in zip(rows,rows[1:]):
 dt=b['display_time']-a['display_time'];v=float(np.linalg.norm(np.array(b['wrist_world_m'])-a['wrist_world_m'])*1000/dt);segments.append(dict(dt=dt,wrist_speed_mm_s=v,wrist_pass=v<=500,latent_rates=((np.array(b['latent'])-a['latent'])/dt).tolist()))
max_key_error=max(float(np.max(abs(np.array(a['key_angles'])-b['key_angles']))) for a,b in zip(rows,r['nodes']))
out=dict(authority='DESIGN_PROVISIONAL',scope='Three time-coupled nodes only',nodes=rows,all_geometry_gates=all(x['all_gates'] for x in rows),segments=segments,motion_pass=all(x['wrist_pass'] for x in segments) and r['motion_numeric_pass'],key_state_match_max_rad=max_key_error,all_source_identities=all(x['native_identity'] and x['original_key_actions_match'] for x in rows),wall_seconds=time.monotonic()-start)
(O/'ACTUAL_BLENDER_VALIDATION.json').write_text(json.dumps(out,indent=2));print('NODES_ACTUAL',out['all_geometry_gates'],out['motion_pass'],segments,flush=True)
