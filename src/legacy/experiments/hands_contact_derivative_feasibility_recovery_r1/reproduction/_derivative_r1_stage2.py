import sys,os,time,json,subprocess
from pathlib import Path
os.environ['PYTHONUTF8']='1';sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));start=time.monotonic()
import contact_solver as cs
inp=json.loads((O/'RECOVERY_INPUT.json').read_text());s=inp['sample'];a=inp['actual'];r=cs.run_solve('recovery_dynamic',s['latent'],s['contacts'],s['display_time'],cs.np.array(a['key_angles']),70)
with (O/'logs/recovery_dynamic_actual.log').open('w') as f:subprocess.run([r'D:\blender\blender.exe','-b','-t','4','--python',str(O/'blender_verify.py'),'--',str(O/'runs/recovery_dynamic.json')],stdout=f,stderr=subprocess.STDOUT,timeout=35,check=True)
ac=json.loads((O/'runs/recovery_dynamic_actual.json').read_text());result=json.loads((O/'CONTACT_FEASIBILITY_RECOVERY.json').read_text());result['dynamic_detector_stage']=dict(result=r,actual=ac);result['status']='CONTACT_FEASIBILITY_RECOVERED' if ac['all_gates'] else 'FEASIBILITY_RECOVERY_BLOCKED';(O/'CONTACT_FEASIBILITY_RECOVERY.json').write_text(json.dumps(result,indent=2));(O/'STAGE2_BUDGET.json').write_text(json.dumps(dict(charged_seconds=time.monotonic()-start,limit=110),indent=2))
