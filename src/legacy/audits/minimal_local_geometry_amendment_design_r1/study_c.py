import sys
sys.dont_write_bytecode=True
from design import *
ns={'np':np,'F':F}
reuse(OUT/'geometry_metrics.py',['quad_bowties'],ns)
scopes=[R['core_vertices']+[962,2609,3300,3308,3315,3347],R['core_vertices']+[962,2609,3300,3308,3315,3347,3306,3338],R['core_vertices']+R['1_ring']+[3315,3306,3338]]
for ids in scopes:
 ids=sorted(ids);ns['FULLFS']=[fi for fi,p in enumerate(F) if set(ids).intersection(p)]
 for m in ['harmonic','biharmonic']:
  v=fair(ids,m);q=(v-origin)@B;bh=(fair(ids,'biharmonic')-origin)@B
  cf=np.linalg.lstsq(feat(Q[R['2_ring']]),Q[R['2_ring'],2],rcond=None)[0];target=feat(q)@cf-.65*np.exp(-np.sum((q[:,:2]-Q[[3332,3340],:2].mean(0))**2,axis=1)/72)
  q[ids,2]=.25*bh[ids,2]+.75*target[ids];v[ids]=q[ids]@B.T+origin
  a=analyze(v,ids);basebow=ns['quad_bowties'](V);bow=ns['quad_bowties'](v)
  print('C_STUDY',m,len(ids),'newbow',sorted(set(bow)-set(basebow)),'max',a['max_angle'],'crease',a['edge6676_angle_deg'],'maxmove',np.linalg.norm(v-V,axis=1).max(),'extra',sorted(set(ids)-set(R['core_vertices'])))
