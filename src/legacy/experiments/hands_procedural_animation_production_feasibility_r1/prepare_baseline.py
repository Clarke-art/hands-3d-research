import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
import shutil
begin=time.perf_counter()
copy=OUT/'C1_LOCAL_EDIT_WORKING_COPY.blend';assert not copy.exists()
tic=time.perf_counter();shutil.copyfile(SOURCE,copy);copy_sec=time.perf_counter()-tic
sc,rig,mesh,left,lrig=s.open_scene(copy)
# degrees() was extracted with blender_support globals, which open_scene populated.
struct={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',mesh,rig),('L',left,lrig)]}
acts=s.protected_state();rows=[]
model=read(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL_MANIFEST.json')
with np.load(safe(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL.npz')) as z:weights=z['weights'].copy()
ring=np.flatnonzero(weights[:,[i for i,n in enumerate(model['bones']) if n.startswith('RING_')]].sum(1)>.05)
for t in [START,4.63571,4.75,4.916666666666667,5.064281,5.1,END]:
    c.settime(sc,t);V,T,F=s.coords_tri(mesh)
    rows.append(dict(time=t,ring_qdeg=s.degrees('RING'),ring_Csharp5_depth_mm=s.target_depth(V,ring),
                     active=[dict(id=n['note_id'],side=n['hand'],finger=n['finger'],key=n['note_name']) for n in NOTES if n['note_on']<=t<n['note_off']]))
assert s.protected_state()==acts
assert all(c.digest(c.native(ob,rg))==struct[side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
save('BASELINE_LOCAL_PROBE.json',dict(rows=rows,ring_influence_vertices=ring,structure=struct,actions=acts,copy_sha256=sha(copy),source_sha256=sha(SOURCE),copy_seconds=copy_sec,total_seconds=time.perf_counter()-begin,source='ORIGINAL_C1',new_motion=False))
protection('PREPARATION_PROTECTION.json')
print('BASELINE_PROBE',json.dumps(rows,default=encode),flush=True)
