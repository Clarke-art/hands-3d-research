import sys, importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O))
import geometry as g
from geometry import *
sc,rig,mesh,left,lrig=s.open_scene(SOURCE)
g.init();c.settime(sc,2.6)
for r in read(ROOT/'experiments/hands_anatomical_whole_hand_pose_repair_r1/PROTECTED_BEFORE.json')['files']:
 safe(r['path']);READS[r['path']]=sha(r['path'])
V0,T0,F0=s.coords_tri(mesh);L0,LT,LF=s.coords_tri(left)
Q0={d:s.degrees(d).copy() for d in DIGITS}
W0=rig.pose.bones['WRIST_R'].matrix.copy()
P0=Vector(V0[c.MARKERS['R'][0]['mesh_vertex']])
NATIVE={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
PROTECTED=s.protected_state()
BASE_ACTION=rig.animation_data.action
BASE_PATHS=s.payload(BASE_ACTION)
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
def render(tag):
 for kind in ['OVERHEAD','SIDE_OBLIQUE']:
  sc.camera=bpy.data.objects[MAN['cameras'][kind]]
  sc.render.filepath=str(OUT/f'{tag}_{kind}.png')
  if Path(sc.render.filepath).exists():continue
  bpy.ops.render.render(write_still=True)
def fullself(V):
 pairs=g.tree(V,g.ALLT).overlap(g.tree(V,g.ALLT))
 return {(i,j) for i,j in pairs if i<j and not set(g.ALLT[i])&set(g.ALLT[j])}
SELF0=fullself(V0)
extract(ROOT/'experiments/hands_blender_artist_pose_repair_poc_r1/artist_tools.py',['segment_distance','edges','exact_clearance'],globals())
if not (OUT/'PROTECTED_BEFORE.json').exists():save('PROTECTED_BEFORE.json',dict(files=[dict(path=p,sha256=h) for p,h in READS.items()]))
if not (OUT/'BASELINE_FACTS.json').exists():save('BASELINE_FACTS.json',dict(qdeg=Q0,keys=g.keycheck(V0,all_hand=True),native=NATIVE,actions=PROTECTED,events=[n for n in NOTES if 2.0<n['note_on']<3.5 or 2.0<n['note_off']<3.5],index_events=[n for n in NOTES if n['hand']=='R' and n['finger']==2],external_libraries=len(bpy.data.libraries),images=[dict(name=i.name,path=i.filepath,packed=bool(i.packed_file)) for i in bpy.data.images],sounds=[dict(name=i.name,path=i.filepath,packed=bool(i.packed_file)) for i in bpy.data.sounds]))
render('ORIGINAL_2_600')
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
if not (OUT/'C1_ISOLATED_WORKING_COPY.blend').exists():bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'C1_ISOLATED_WORKING_COPY.blend'),check_existing=True)
if not (OUT/'SESSION_INPUT_RECEIPT.json').exists():protection('SESSION_INPUT_RECEIPT.json')
spec=importlib.util.spec_from_file_location('hands_blender_mcp',r'<USER_HOME>/AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons/addon.py')
addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon)
addon.register()
print('HANDS_DYNAMIC_SESSION_READY',flush=True)
