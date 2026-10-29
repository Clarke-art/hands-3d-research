import sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
import bpy
from common import *
man=read(P/'DYNAMIC_SCENE_MANIFEST_R1.json');previous=read(P/'RENDER_MANIFEST_R1.json') if (P/'RENDER_MANIFEST_R1.json').exists() else {};assert sha(P/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend')==man['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(P/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False)
out={}
for s,info in man['mapping'].items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;folder=P/'_frames'/s;folder.mkdir(parents=True,exist_ok=True);N=sc.frame_end;sc.render.resolution_x=768;sc.render.resolution_y=594;out[s]={'frames':N,'fps':60,'views':list(info['cameras']),'source_candidate_sha256':man['candidate_sha256'],'window_start':WINDOWS[s][0],'render_dimensions':[768,594]}
 for frame in range(1,N+1):
  sc.frame_set(frame)
  for view,name in info['cameras'].items():
   sc.camera=bpy.data.objects[name];path=folder/f'{frame-1:04}_{view}.png'
   if path.exists() and previous.get(s,{}).get('source_candidate_sha256')==man['candidate_sha256']:continue
   sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
  if frame%10==0 or frame==N:print('RENDER_PROGRESS',s,frame,'/',N,flush=True)
dump('RENDER_MANIFEST_R1.json',out)
