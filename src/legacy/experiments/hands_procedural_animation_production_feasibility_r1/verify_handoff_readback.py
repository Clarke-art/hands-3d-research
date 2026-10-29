import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();h=read(OUT/'HUMAN_HANDOFF_RECEIPT.json');base=read(OUT/'BASELINE_LOCAL_PROBE.json')
sc,rig,mesh,left,lrig=s.open_scene(OUT/h['file']);assert sha(OUT/h['file'])==h['sha256']
assert s.protected_state()==base['actions']
assert all(c.digest(c.native(ob,rg))==base['structure'][side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
assert sc.frame_current==296 and sc.frame_start==265 and sc.frame_end==336 and sc.render.fps==60
assert rig.data.bones.active.name=='RING_MCP_R' and rig.pose.bones['RING_MCP_R'].select
assert bpy.data.texts['HUMAN_RING_EDIT_INSTRUCTIONS'].as_string().startswith('HUMAN EDIT REQUIRED')
assert all(Path(scene.render.filepath).is_relative_to(OUT) for scene in bpy.data.scenes)
save('HANDOFF_READBACK.json',dict(pass_=True,seconds=time.perf_counter()-begin,all_source_actions_exact=True,native_structure_exact=True,frame=296,active_bone=rig.data.bones.active.name,human_edit_performed=False))
protection('HANDOFF_READBACK_PROTECTION.json');print('HANDOFF_REOPEN_PASS',flush=True)
