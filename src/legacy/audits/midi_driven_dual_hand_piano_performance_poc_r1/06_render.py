import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'MIDI_DRIVEN_DUAL_HAND_PIANO_PERFORMANCE_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False)
sc=bpy.context.scene
sc.render.use_persistent_data=True
# Select an available CUDA/OptiX device when present; fall back to CPU without changing art parameters.
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='CUDA';prefs.get_devices();gpus=[d for d in prefs.devices if d.type!='CPU']
 for d in prefs.devices:d.use=d in gpus
 if gpus:sc.cycles.device='GPU'
 print('RENDER_DEVICE',[(d.name,d.type,d.use) for d in prefs.devices],flush=True)
except Exception as e:print('CPU_RENDER',str(e),flush=True)
if '--preview' in sys.argv:
 sc.camera=bpy.data.objects['SKIN_REVIEW'];sc.frame_set(67);sc.render.filepath=str(P/'SKIN_MATERIAL_REVIEW_R1.png');bpy.ops.render.render(write_still=True)
 sc.camera=bpy.data.objects['CONTACT_SIDE'];sc.frame_set(90);sc.render.filepath=str(P/'_contact_review.png');bpy.ops.render.render(write_still=True)
else:
 sc.camera=bpy.data.objects['PRODUCT_DUAL_HAND'];folder=P/'_frames';folder.mkdir(exist_ok=True)
 for j in range(sc.frame_end):
  dest=folder/f'{j:04}.png'
  if dest.is_file():continue
  sc.frame_set(j+1);sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
