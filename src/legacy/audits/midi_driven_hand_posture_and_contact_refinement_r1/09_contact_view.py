import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend'),load_ui=False,use_scripts=False)
sc=bpy.context.scene;sc.camera=bpy.data.objects['CONTACT_SIDE']
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.cycles.device='GPU'
for name,t in [('left',137/120),('right',308/120)]:
 f=1+t*60;sc.frame_set(int(f),subframe=f-int(f));sc.render.filepath=str(P/('_contact_'+name+'.png'));bpy.ops.render.render(write_still=True)
