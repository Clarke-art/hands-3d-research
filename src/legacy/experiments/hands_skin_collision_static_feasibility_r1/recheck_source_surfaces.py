import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from geometry_detector import *
A=np.load(O/'ACTUAL_SOURCE_SNAPSHOTS.npz');rows=json.loads((O/'SOURCE_POSES.json').read_text());results=[]
for row in rows:
 target=dict(midi=78,finger=3) if row['label']=='APPROVED_R2' else None
 r=detect(A[row['label']],np.array(row['angles']),target);results.append(dict(label=row['label'],time=row['time'],measurement=r));print('SOURCE_SURFACE_CHECK',row['label'],round(r['wrong_key_or_nonpulp_max_depth_mm'],6),r['nonadjacent_self_triangle_pairs'])
(O/'SOURCE_POSE_COLLISION_DIAGNOSES.json').write_text(json.dumps(results,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
