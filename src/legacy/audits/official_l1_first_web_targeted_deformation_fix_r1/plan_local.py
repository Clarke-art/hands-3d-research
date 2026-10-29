import json,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
d=json.loads((P/'LOCAL_INPUT.json').read_text()); V=np.array(d['vertices']);W=np.array(d['weights'])
j=d['cameras']['THENAR_CLOSE'];dr=np.array(j['direction']);dr/=np.linalg.norm(dr)
r=np.cross([0,0,1],dr);r/=np.linalg.norm(r);u=np.cross(dr,r);C=np.array(j['center'])
def project(v):
    return np.c_[600+(v-C)@r*1200/j['ortho_scale_m'],550-(v-C)@u*1200/j['ortho_scale_m']]
VP=np.array(json.loads((P/'CMC_OPP_30_INPUT_POINTS.json').read_text()));px=project(VP)
ids=np.argsort(np.linalg.norm(px-[427,339],axis=1))[:20]
for i in ids: print(i, np.round(px[i],1),np.round(V[i],5),[(n,round(w,3)) for n,w in zip(d['groups'],W[i]) if w>.01])
