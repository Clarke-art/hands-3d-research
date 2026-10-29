import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from blender_utils import *
M=json.loads((O/'SCENE_MANIFEST.json').read_text());metrics=json.loads((O/'MOTION_FEASIBILITY_METRICS.json').read_text());bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world.color=(.08,.08,.08)
rig=bpy.data.objects[M['mapping']['R']['rig']];rt=bpy.data.objects[M['mapping']['R']['root']];newrig=rig.animation_data.action;newroot=rt.animation_data.action;newslot=rig.animation_data.action_slot;newrootslot=rt.animation_data.action_slot
oldrig=bpy.data.actions[man['actions']['R_rig']['action']];oldroot=bpy.data.actions[man['actions']['R_root']['action']]
folder=O/'stills';folder.mkdir(exist_ok=True);result=[]
notes={n['note_id']:n for n in I['notes']}
probes=[('R07_R08_PREPARE',notes['R08']['note_on']-.025,'OVERHEAD','C01'),('R08_E5_MIDDLE',notes['R08']['note_on']+.035,'OVERHEAD','C01'),('B02_E5_HANDOVER',3.825,'OVERHEAD','C01'),('R12_FSHARP_RING',notes['R12']['note_on']+.035,'OVERHEAD','C01'),('R12_FSHARP_RING',notes['R12']['note_on']+.035,'SIDE_OBLIQUE','C01'),('R13_R14_OCTAVE',notes['R14']['note_on']+.035,'OVERHEAD','C01'),('B02_E5_HANDOVER',3.825,'OVERHEAD','OLD')]
for label,t,view,version in probes:
 if version=='OLD':rig.animation_data.action=oldrig;rig.animation_data.action_slot=oldrig.slots[newslot.identifier];rt.animation_data.action=oldroot;rt.animation_data.action_slot=oldroot.slots[newrootslot.identifier]
 else:rig.animation_data.action=newrig;rig.animation_data.action_slot=newslot;rt.animation_data.action=newroot;rt.animation_data.action_slot=newrootslot
 settime(sc,t);sc.camera=bpy.data.objects[M['cameras'][view]];sc.camera.data.ortho_scale=.34
 target=Vector(((c.KEYS[67-21]['key_center'][0]+c.KEYS[79-21]['key_center'][0])/2,-.035,.015));sc.camera.location=target+Vector((0,0,.8) if view=='OVERHEAD' else (.11,-.48,.22));sc.camera.rotation_euler=(target-sc.camera.location).to_track_quat('-Z','Y').to_euler()
 file=folder/f'{version}_{label}_{view}.png';sc.render.filepath=str(file);start=time.perf_counter();bpy.ops.render.render(write_still=True);duration=time.perf_counter()-start;result.append(dict(file=str(file),label=label,time=t,view=view,version=version,actual_action_evaluated=True,render_seconds=duration));print('ONE_DIAGNOSTIC_STILL',file.name,round(duration,2),flush=True)
out('STILL_MANIFEST.json',result)
# Video is allowed only if actual geometry passed. Render budget estimated from real still runtime.
if metrics['can_render_video']:
 predicted=max(x['render_seconds'] for x in result)*(sc.frame_end-sc.frame_start+1)
 out('VIDEO_RENDER_BUDGET.json',dict(predicted_seconds=predicted,limit_seconds=120,actual_still_timing_used=True))
 if predicted<=120:
  rig.animation_data.action=newrig;rig.animation_data.action_slot=newslot;rt.animation_data.action=newroot;rt.animation_data.action_slot=newrootslot;sc.camera=bpy.data.objects[M['cameras']['OVERHEAD']]
  sc.render.image_settings.file_format='FFMPEG';sc.render.ffmpeg.format='MPEG4';sc.render.ffmpeg.codec='H264';sc.render.ffmpeg.constant_rate_factor='MEDIUM';sc.render.filepath=str(O/'C01_overhead_720p_1x.mp4');bpy.ops.render.render(animation=True)
  out('VIDEO_MANIFEST.json',dict(file=sc.render.filepath,frames=sc.frame_end-sc.frame_start+1,fps=60,dimensions=[1280,720],one_camera_one_render=True,temp_png_frames=0))
 else:out('VIDEO_STOP.json',dict(reason='Estimated video render exceeds the fixed small budget; no animation render started',predicted_seconds=predicted))
else:out('VIDEO_STOP.json',dict(reason='Actual contact/collision gate did not pass; no video or slow-motion encode',status=metrics['status'],render_frames=0))

