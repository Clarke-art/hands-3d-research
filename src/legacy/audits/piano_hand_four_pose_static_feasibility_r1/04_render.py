from pathlib import Path
import json,hashlib
import bpy
P=Path(__file__).resolve().parent
man=json.loads((P/'STATIC_SCENE_MANIFEST_R1.json').read_text(encoding='utf-8'));assert hashlib.sha256((P/'STATIC_POSTURE_CANDIDATE_R1.blend').read_bytes()).hexdigest()==man['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(P/'STATIC_POSTURE_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False);(P/'renders').mkdir(exist_ok=True);out=[]
for pose,info in man['mapping'].items():
 sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc
 for view,name in info['cameras'].items():
  sc.camera=bpy.data.objects[name];dest=P/'renders'/f'{pose}__{view}.png';sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True);out.append({'pose':pose,'view':view,'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()});print('RENDERED',pose,view,flush=True)
(P/'RENDER_MANIFEST_R1.json').write_text(json.dumps({'candidate_sha256':man['candidate_sha256'],'unique_views':12,'renders':out,'candidate_modified_after_render':False},indent=2),encoding='utf-8')
