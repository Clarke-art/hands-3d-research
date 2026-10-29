import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
import support as s
out={}
for tag,path in [('base',SOURCE),('candidate',OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend')]:
 sc,rig,mesh,left,lrig=s.open_scene(path);ac=rig.animation_data.action;rows=[]
 for t in [1.247142,3.345,3.35,3.355,3.36,3.3666667,3.38,3.4]:
  c.settime(sc,t);rows.append(dict(t=t,q=s.degrees('INDEX'),quat=[list(rig.pose.bones[n].rotation_quaternion) for n in c.SETUPS['R','INDEX'][0]]))
 fs=[dict(path=f.data_path,i=f.array_index,keys=[list(k.co) for k in f.keyframe_points if 199<k.co.x<206]) for f in s.curves(ac) if 'INDEX_' in f.data_path]
 out[tag]=dict(rows=rows,curves=fs)
save('BAKE_BOUNDARY_DIAGNOSIS.json',out)
print(json.dumps(out,default=encode),flush=True)
