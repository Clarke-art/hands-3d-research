import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np
assert sha(INPUT)==INPUT_SHA
ob,rig=open_file(INPUT)
V,F=evaluate(ob,ob.matrix_world)
groups=[g.name for g in ob.vertex_groups]
W=np.zeros((len(V),len(groups)))
for v in ob.data.vertices:
    for g in v.groups: W[v.index,g.group]=g.weight
dump('LOCAL_INPUT.json',{'vertices':[list(v) for v in V],'local':[list(v.co) for v in ob.data.vertices], 'faces':F,'edges':[list(e.vertices) for e in ob.data.edges],'weights':W,'groups':groups,'bones':{b.name:{'head':list(<REDACTED_EMAIL>_local),'tail':list(<REDACTED_EMAIL>_local)} for b in rig.data.bones},'cameras':cameras(),'cases':CASES})
for c in CASES:
    pose(rig,c);VP,FP=evaluate(ob,ob.matrix_world)
    dump(c['case_id']+'_INPUT_POINTS.json',[list(v) for v in VP])
print('LOCAL_INPUT_READY',flush=True)
