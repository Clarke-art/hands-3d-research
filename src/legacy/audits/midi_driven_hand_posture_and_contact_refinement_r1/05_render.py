import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend'),load_ui=False,use_scripts=False)
sc=bpy.context.scene
sc.render.use_persistent_data=True
# Select an available CUDA/OptiX device when present; fall back to CPU without changing art parameters.
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='OPTIX';prefs.get_devices();gpus=[d for d in prefs.devices if d.type!='CPU']
 for d in prefs.devices:d.use=d in gpus
 if gpus:sc.cycles.device='GPU'
 print('RENDER_DEVICE',[(d.name,d.type,d.use) for d in prefs.devices],flush=True)
except Exception as e:print('CPU_RENDER',str(e),flush=True)
if '--preview' in sys.argv:
 sc.camera=bpy.data.objects['SKIN_REVIEW'];sc.frame_set(52);sc.render.filepath=str(P/'_preview_pose.png');bpy.ops.render.render(write_still=True)
 sc.camera=bpy.data.objects['CONTACT_SIDE'];sc.frame_set(70);sc.render.filepath=str(P/'_preview_side.png');bpy.ops.render.render(write_still=True)
else:
 sc.camera=bpy.data.objects['PRODUCT_DUAL_HAND'];folder=P/'_frames';folder.mkdir(exist_ok=True)
 start=int(sys.argv[sys.argv.index('--start')+1]) if '--start' in sys.argv else 0
 end=int(sys.argv[sys.argv.index('--end')+1]) if '--end' in sys.argv else sc.frame_end
 priority=[j for j in [51,69,111,150] if start<=j<end]
 for j in priority+[j for j in range(start,end) if j not in priority]:
  dest=folder/f'{j:04}.png'
  if dest.is_file():continue
  sc.frame_set(j+1);sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
