import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();qc=read(OUT/'MACHINE_VALIDATION.json');assert not qc['pass_'],'Use preview workflow for passing candidate'
edit=read(OUT/'EDIT_RECEIPT.json');sc,rig,mesh,left,lrig=s.open_scene(edit['candidate_path'])
candidate=rig.animation_data.action;source=bpy.data.actions[edit['source_action']]
def angular_bound(action):
    fs=sorted([f for f in s.curves(action) if f.data_path=='pose.bones["RING_MCP_R"].rotation_quaternion'],key=lambda f:f.array_index)
    ts=sorted({float(k.co.x) for f in fs for k in f.keyframe_points if 1+60*START<=k.co.x<=1+60*END}|{1+60*START,1+60*END})
    peak=0.;witness=None
    for a,b in zip(ts[:-1],ts[1:]):
        q0=np.array([f.evaluate(a) for f in fs]);q1=np.array([f.evaluate(b) for f in fs]);d=q1-q0;dd=d@d
        u=float(np.clip(-(q0@d)/dd,0,1)) if dd>0 else 0.;z=q0+u*d
        crossnorm=np.sqrt(max(0,float((q0@q0)*dd-(q0@d)**2)))
        value=float(np.degrees(2*crossnorm/max(z@z,1e-14)/((b-a)/60)))
        if value>peak:peak=value;witness=[(a-1)/60,(b-1)/60]
    return dict(peak_deg_s=peak,segment_sec=witness,meaning='Maximum physical angular rate of normalized linear quaternion segments; not an added engineering-angle rate or a naturalness score')
rates=dict(baseline=angular_bound(source),candidate=angular_bound(candidate))
if (OUT/'CURVE_CONTINUITY_CHECK.json').exists():assert read(OUT/'CURVE_CONTINUITY_CHECK.json')==rates
else:save('CURVE_CONTINUITY_CHECK.json',rates)
sc,rig,mesh,left,lrig=s.open_scene(OUT/'C1_LOCAL_EDIT_WORKING_COPY.blend')
before=s.protected_state();native={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',mesh,rig),('L',left,lrig)]}
text='''HUMAN EDIT REQUIRED — ONE RING / C#5 PROBLEM ONLY

This file starts from ORIGINAL C1, not the rejected automatic edit.
The single automatic MCP (-7.5 deg flexion, -2 deg spread) candidate failed real QC.
Do not apply that offset again, do not overwrite C1 or the rejected candidate.

Display window 4.4-5.6 sec = frames 265-336 at 60 fps, frame=1+60*t.
Main original witness: 4.916666667 sec, frame 296, RIGHT RING / C#5 (MIDI73).
Editable object: RIGHT_HAND_PRODUCTION_RIG.002, bone RING_MCP_R.
Potential manual refinement, only if necessary: RING_PIP_R and RING_DIP_R.
Keep shared root/wrist, every other finger, left hand, MIDI and all key Actions fixed.
Protect R13 little/G5 until 4.63571 sec; R14/R15 thumb/G4; L06 middle/B3.

1. Save As a NEW file HUMAN_RING_EDIT_<version>.blend INSIDE this experiment directory.
2. Animation workspace: set active scene shown here, preview frames 265-336; Auto Key OFF.
3. Action Editor: make a single-user COPY of the right-rig Action before editing.
4. Pose Mode, RING_MCP_R selected; inspect frame 296 in teaching and side/overhead views.
5. Mark unchanged boundary rotations at frames 277 (4.6s) and 331 (5.5s).
6. Make a smaller visual MCP/curvature adjustment at frame 296. The frozen engineering
   flexion axis is not necessarily local Euler X: use the rotation gizmo and actual skin.
   Preserve the finger arc; do not translate the bone, raise the wrist or change the rig.
   If MCP alone causes crossings, consider small PIP/DIP distribution MANUALLY; this is
   not prevalidated. Insert Rotation keys only for intentionally edited ring bones.
7. Inspect entry/exit and core frames 292-316, interpolate smoothly, play at 60fps/1x.
   Check the neighboring middle/little boundaries and black-key sides, not just the tip.
8. Save the NEW edit and return its exact path. Stop: a separate real geometry/contact
   validation is REQUIRED after the Human edit. No Human edit or PASS exists yet.

Machine numbers and regressions are in FINAL_PRODUCTION_FEASIBILITY.md and
MACHINE_VALIDATION.json. This copy is an editing handoff, not an approved production asset.
'''
block=bpy.data.texts.new('HUMAN_RING_EDIT_INSTRUCTIONS');block.write(text)
sc.frame_start=265;sc.frame_end=336;sc.frame_preview_start=265;sc.frame_preview_end=336;sc.use_preview_range=True
sc['STATUS']='HUMAN_EDIT_REQUIRED / ORIGINAL_C1_ACTIONS';sc['TARGET']='RING C#5, frame296';sc['HUMAN_EDIT_PERFORMED']=False
for scene in bpy.data.scenes:scene.render.filepath=str(OUT/'human_render_output'/scene.name/'frame_')
sc.camera=bpy.data.objects[MAN['cameras']['TEACHING']]
for name,t in [('B03_RING_WITNESS',4.916666666666667),('EDIT_ENTRY',4.6),('EDIT_EXIT',5.5)]:
    sc.timeline_markers.new(name,frame=round(1+60*t))
c.settime(sc,4.916666666666667)
for ob in bpy.context.view_layer.objects:ob.select_set(False)
rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='DESELECT')
rig.pose.bones['RING_MCP_R'].select=True
rig.data.bones.active=rig.data.bones['RING_MCP_R']
assert s.protected_state()==before
assert all(c.digest(c.native(ob,rg))==native[side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
dest=OUT/'HUMAN_RING_EDIT_HANDOFF.blend';assert not dest.exists()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=False)
save('HUMAN_HANDOFF_RECEIPT.json',dict(seconds=time.perf_counter()-begin,file=dest.name,sha256=sha(dest),base='ORIGINAL_C1',all_actions_unchanged=True,native_structure_unchanged=True,
    human_edit_performed=False,human_edit_seconds=None,instruction_steps=8,actual_clicks_unknown=True,selected_bone='RING_MCP_R',frame=296,output_paths_inside_experiment=True))
with (OUT/'HUMAN_EDIT_INSTRUCTIONS.txt').open('x',encoding='utf8') as f:f.write(text)
protection('HANDOFF_PROTECTION.json')
print('HUMAN_HANDOFF_READY',time.perf_counter()-begin,flush=True)
