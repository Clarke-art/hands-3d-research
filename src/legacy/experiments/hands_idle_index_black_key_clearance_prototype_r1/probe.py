import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);g.init()
configs={'A':[-10,4,2,0],'B':[-16,6,3,0]}
bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])[1]
rows=[]
for t in [26/60,2.6]:
 c.settime(sc,t);q=s.degrees('INDEX');V,T,F=s.coords_tri(mesh);base=g.keycheck(V)
 rows.append(dict(time=t,config='BASELINE',qdeg=q,keys=base))
 for name,d in configs.items():
  c.settime(sc,t);nq=np.clip(q+np.array(d),bounds[0],bounds[1]);g.joint_set(nq);V,T,F=s.coords_tri(mesh)
  rows.append(dict(time=t,config=name,qdeg=nq,keys=g.keycheck(V)))
save('TWO_STATIC_PROBES.json',dict(configs=configs,rows=rows))
protection('PROBE_INPUT_RECEIPT.json')
for r in rows:print(r['time'],r['config'],r['qdeg'],[(k['key'],round(k['depth_mm'],5),k['bvh_pairs'],round(k['clearance_vertex_surface_mm'],3)) for k in r['keys']],flush=True)
