import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
import shutil
begin=time.perf_counter();dest=OUT/'C1_B01_ORIGINAL_EDITING_COPY.blend';assert not dest.exists();shutil.copyfile(SOURCE,dest)
sc,rig,mesh,left,lrig=s.open_scene(dest);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
before=s.protected_state();struct={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',mesh,rig),('L',left,lrig)]}
def pair(V):
    trees={d:BVHTree.FromPolygons([Vector(v) for v in V],ROI[d]['faces'],epsilon=0) for d in ['MIDDLE','RING']}
    return len(trees['MIDDLE'].overlap(trees['RING']))
times=[.9,.99,1.027142,1.05,1.10,1.13333333333333,1.207142,1.2414275,1.3,1.38,1.4214275,1.4614275,1.55,1.635713,1.705713,1.75]
rows=[]
for t in times:
    c.settime(sc,t);V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left)
    rows.append(dict(time=t,middle_qdeg=s.degrees('MIDDLE'),ring_qdeg=s.degrees('RING'),middle_ring_full_roi_face_pairs=pair(V),
          active_contacts=[dict(note=n['note_id'],side=n['hand'],finger=n['finger'],contact=s.contact(V if n['hand']=='R' else L,KEYS[n['key_index']],n['hand'],n['finger'])) for n in NOTES if n['note_on']<=t<n['note_off']]))
assert before==s.protected_state()
save('BASELINE_B01_ACTUAL.json',dict(source_sha256=sha(SOURCE),seconds=time.perf_counter()-begin,rows=rows,actions=before,native_structure=struct,
     frozen_domains=read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'],copy_sha256=sha(dest)))
protection('BASELINE_PROTECTION.json');print(json.dumps(rows,default=encode),flush=True)
