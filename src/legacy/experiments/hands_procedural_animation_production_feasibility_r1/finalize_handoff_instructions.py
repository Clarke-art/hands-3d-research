import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();sc,rig,mesh,left,lrig=s.open_scene(OUT/'HUMAN_RING_EDIT_HANDOFF.blend')
before=s.protected_state();native={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',mesh,rig),('L',left,lrig)]}
warning='''MANDATORY DENSE-KEY EDIT NOTE (final handoff instructions)

C1 is already baked at about 120Hz. Do NOT rotate frame 296 and insert only one
new key while leaving its immediate old half-frame neighbors: that creates a spike.
In the COPIED right-rig Action, filter to RING_MCP_R and its FOUR quaternion curves.
Preserve exact original boundary keys at 277 and 331 and all keys outside them.
For a conventional sparse manual pose edit, remove ONLY the interior keys of these
four curves between 277 and 331, then author a small set of visual ring poses at
292, 296 and 316. Keep the PIP/DIP curves unchanged initially. This is a proposed
Human editing workflow, not a tested motion. If using Bezier interpolation, clamp
and inspect handles to avoid overshoot, ease the boundary slopes, and check at 1x.
Do not modify unrelated channels, root, wrist, fingers, MIDI, keyboard or cameras.
The complete geometry, contact, domain and velocity validation MUST be rerun in a
separately authorized follow-up after Human editing. No manual result is approved.

The following eight-step overview remains context; this dense-key note qualifies
steps 5-7. FINAL_PRODUCTION_FEASIBILITY.md contains the full Chinese instructions.

'''
block=bpy.data.texts['HUMAN_RING_EDIT_INSTRUCTIONS'];prior=block.as_string();block.clear();block.write(warning+prior)
assert s.protected_state()==before
dest=OUT/'HUMAN_RING_EDIT_HANDOFF_READY.blend';assert not dest.exists()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=False)
sc,rig,mesh,left,lrig=s.open_scene(dest)
assert s.protected_state()==before
assert all(c.digest(c.native(ob,rg))==native[side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
assert bpy.data.texts['HUMAN_RING_EDIT_INSTRUCTIONS'].as_string().startswith('MANDATORY DENSE-KEY EDIT NOTE')
with (OUT/'HUMAN_EDIT_INSTRUCTIONS_FINAL.txt').open('x',encoding='utf8') as f:f.write(warning+prior)
save('FINAL_HANDOFF_RECEIPT.json',dict(file=dest.name,sha256=sha(dest),seconds=time.perf_counter()-begin,readback_pass=True,
     source='ORIGINAL_C1',action_motion_unchanged=True,native_structure_unchanged=True,instructions_include_dense_key_hazard=True,human_edit_performed=False,
     note='UI/instruction delivery copies are not additional motion candidates'))
protection('FINAL_HANDOFF_PROTECTION.json');print('FINAL_HANDOFF_READY',sha(dest),flush=True)
