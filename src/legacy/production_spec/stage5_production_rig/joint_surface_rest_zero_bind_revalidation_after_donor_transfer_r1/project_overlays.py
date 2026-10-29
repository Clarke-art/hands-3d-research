import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
G=read(OUT/'MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json');joints=read(OUT/'JOINT_SURFACE_REQUALIFICATION_R1.json')['all21_current_rows'];M=read(OUT/'MATCHED_RENDER_MANIFEST_R1.json')
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
cd=bpy.data.cameras.new('READ_ONLY_MATCHED_CAMERA');cd.type='ORTHO';cam=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(cam);sc.camera=cam
result={}
for r in M['renders']:
 if r['view'] in ('CLOSE','SIDE','GRAZING'):continue
 target=Vector(r['target_world_m']);direction=Vector(r['direction']);cam.location=target+direction*.55;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=r['orthographic_scale_m'];sc.render.resolution_x,sc.render.resolution_y=r['resolution'];sc.render.resolution_percentage=100;sc.camera=cam;bpy.context.view_layer.update()
 def project(v):
  q=world_to_camera_view(sc,cam,Vector(v));return [q.x*r['resolution'][0],(1-q.y)*r['resolution'][1]]
 result[r['path']]={'bones':{n:{e:project(b[e+'_world_m']) for e in ('head','tail')} for n,b in G['bones'].items()},'approved54':{str(i):project(G['stages']['R2_RAW']['world_m'][i]) for i in G['changed_ids']},'terminal284':project(G['stages']['R2_RAW']['world_m'][284]),'RING_nearest_new':project(joints['RING_MCP_R']['surface']['nearest_native_feature']['nearest_point_world_m']),'RING_nearest_old':project(joints['RING_MCP_R']['old_geometry']['nearest_native_feature']['nearest_point_world_m'])}
dump('MATCHED_NATIVE_POINT_PROJECTIONS_R1.json',{'method':'bpy_extras world_to_camera_view under actual matched camera/frame/resolution; exact 3D source points projected for audit overlay, no joint relocation','views':result})
