import sys
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
import geometry as g
from geometry import *
sc,rig,mesh,left,lrig=s.open_scene(SOURCE,reuse_loaded=True)
for r in read(ROOT/'experiments/hands_idle_index_black_key_clearance_prototype_r1/PROTECTED_AFTER_AND_SHA256_RECEIPT.json')['files']:
 READS[r['path']]=sha(r['path'])
READS[str(SOURCE)]=sha(SOURCE)
save('PROTECTED_BEFORE.json',dict(files=[dict(path=p,sha256=h) for p,h in READS.items()]))
c.settime(sc,2.6);g.init()
V0,T0,F0=s.coords_tri(mesh);Q0=s.degrees('INDEX').copy()
protected=s.protected_state();native={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
rootmat=np.array(rig.matrix_world);left0=s.coords_tri(left)[0]
bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])[1]
paths={f'pose.bones["{n}"].rotation_quaternion' for n in c.SETUPS['R','INDEX'][0]}
other_rig=c.digest(s.payload(rig.animation_data.action,paths))
save('BASELINE_FACTS.json',dict(time=2.6,index_qdeg=Q0,bounds_deg=bounds,index_axes=c.SETUPS['R','INDEX'][2],spread_axis=c.SETUPS['R','INDEX'][3],active=[n for n in NOTES if n['note_on']<=2.6<n['note_off']],index_roles=[n for n in NOTES if n['hand']=='R' and n['finger']==2],root_world=rootmat,wrist=np.array(rig.pose.bones['WRIST_R'].matrix),all_digit_qdeg={d:s.degrees(d) for d in DIGITS},baseline_geometry=g.keycheck(V0),thumb_contact=s.contact(V0,KEYS[46],'R',1),native=native,protected_actions=protected,unedited_rig_digest=other_rig))
dest=OUT/'C1_ARTIST_WORKING_COPY_NOT_APPROVED.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
def render_views(tag):
 result=[]
 for kind in ['OVERHEAD','SIDE_OBLIQUE']:
  sc.camera=bpy.data.objects[MAN['cameras'][kind]];path=OUT/f'{tag}_{kind}.png';assert not path.exists();sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);result.append(dict(view=kind,path=str(path),camera=sc.camera.name,matrix=np.array(sc.camera.matrix_world),ortho_scale=sc.camera.data.ortho_scale))
 return result
views=render_views('ORIGINAL_2_600')
save('BASELINE_VIEWS.json',views)
np.savez_compressed(OUT/'BASELINE_STATIC.npz',V=V0,T=T0,q=Q0,left=left0)
protection('BASELINE_INPUT_RECEIPT.json')
print('ARTIST_SESSION_READY',Q0.tolist(),[(r['key'],r['depth_mm']) for r in g.keycheck(V0) if r['depth_mm']>1e-6],flush=True)
