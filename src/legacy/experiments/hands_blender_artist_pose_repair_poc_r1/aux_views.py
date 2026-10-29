import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
import support as s
for tag,path in [('ORIGINAL',SOURCE),('ROUND_1_APPLIED',OUT/'ROUND_1_APPLIED_STATIC_NOT_APPROVED.blend')]:
 sc,rig,mesh,left,lrig=s.open_scene(path);c.settime(sc,2.6)
 camdata=bpy.data.cameras.new('ARTIST_AUX_INDEX_SIDE');cam=bpy.data.objects.new('ARTIST_AUX_INDEX_SIDE',camdata);sc.collection.objects.link(cam)
 cam.location=(.015,-.035,.085);target=Vector((.13,.045,.017));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.145
 sc.camera=cam;sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(OUT/f'{tag}_AUX_INDEX_SIDE.png');bpy.ops.render.render(write_still=True)
 V,T,F=s.coords_tri(mesh)
 print(tag,'q',s.degrees('INDEX').tolist(),'pads',[(DIGITS[i],V[m['mesh_vertex']].tolist()) for i,m in enumerate(c.MARKERS['R'])],flush=True)
protection('AUX_VIEW_INPUT_RECEIPT.json')
