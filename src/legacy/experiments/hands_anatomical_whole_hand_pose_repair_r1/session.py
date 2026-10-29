import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
sc,rig,mesh,left,lrig=s.open_scene(SOURCE,reuse_loaded=True)
for r in read(ROOT/'experiments/hands_blender_artist_pose_repair_poc_r1/PROTECTED_SHA256_BEFORE_AFTER.json')['files']:READS[r['path']]=sha(r['path'])
PREVIOUS=ROOT/'experiments/hands_blender_artist_pose_repair_poc_r1/ROUND_3_STATIC_NOT_APPROVED.blend'
ref_paths=[PREVIOUS,ROOT/'audits/piano_hand_posture_reference_and_static_feasibility_r1/REAL_PIANO_REFERENCE_MANIFEST_R1.md',ROOT/'audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/REAL_PIANO_REFERENCE_MANIFEST_R2.md',ROOT/'audits/real_piano_reference_gap_closure_and_static_posture_probe_r2/NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2.md',ROOT/'audits/piano_hand_posture_reference_and_static_feasibility_r1/_research/right_source_view.png',ROOT/'audits/piano_hand_posture_reference_and_static_feasibility_r1/_research/left_source_view.png',ROOT/'references/piano_motion/pianovam_sample_r1/Video/2024-03-04_03-46-36.mp4',ROOT/'references/piano_motion/pianovam_sample_r1/ATTRIBUTION_AND_USAGE_R1.md',ROOT/'references/piano_motion/pianovam_sample_r1/selected_metadata_entry.json',ROOT/'AGENTS.md']
for p in ref_paths:READS[str(p)]=sha(p)
save('PROTECTED_BEFORE.json',dict(files=[dict(path=p,sha256=h) for p,h in READS.items()]))
c.settime(sc,2.6);g.init();B,T,F=s.coords_tri(mesh);BL,LT,LF=s.coords_tri(left)
BASE_Q={d:s.degrees(d).copy() for d in DIGITS};BASE_BONES={b.name:dict(quaternion=list(b.rotation_quaternion),location=list(b.location),scale=list(b.scale),matrix=np.array(b.matrix)) for b in rig.pose.bones}
NATIVE={side:c.digest(c.native(ob,rg)) for side,ob,rg in [('R',mesh,rig),('L',left,lrig)]};ACTIONS=s.protected_state();RIG_M=np.array(rig.matrix_world).copy();ROOT_M=np.array(bpy.data.objects[MAN['mapping']['R']['root']].matrix_world).copy()
extract(ROOT/'experiments/hands_blender_artist_pose_repair_poc_r1/artist_tools.py',['segment_distance','edges','exact_clearance','selfpairs'],globals())
BOUNDS=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
baseline_keys=g.keycheck(B,all_hand=True);palm=rig.pose.bones['WRIST_R'];BASE_WRIST=palm.matrix.copy();THUMB_PAD=B[c.MARKERS['R'][0]['mesh_vertex']].copy()
def self_full(V):
 pairs=g.tree(V,g.ALLT).overlap(g.tree(V,g.ALLT));out=set()
 for i,j in pairs:
  if i>=j or set(g.ALLT[i])&set(g.ALLT[j]):continue
  out.add((int(i),int(j)))
 return out
BASE_SELF=self_full(B)
def active_contacts(V,L):
 rows=[]
 for n in NOTES:
  if n['note_on']<=2.6<n['note_off']:
   rows.append(dict(hand=n['hand'],finger=n['finger'],key=n['note_name'],event=n['note_id'],contact=s.contact(V if n['hand']=='R' else L,KEYS[n['key_index']],n['hand'],n['finger'])))
 return rows
def render_views(tag):
 sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';rows=[]
 for kind in ['OVERHEAD','SIDE_OBLIQUE','AUX_INDEX_SIDE','AUX_PALM_PERSP']:
  name=MAN['cameras'].get(kind,'ANATOMICAL_'+kind);cam=bpy.data.objects[name];sc.camera=cam;path=OUT/f'{tag}_{kind}.png';assert not path.exists();sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);rows.append(dict(view=kind,path=str(path),camera=cam.name,matrix=np.array(cam.matrix_world),type=cam.data.type,scale=cam.data.ortho_scale,lens=cam.data.lens))
 return rows
for name,location,target,typ,scale in [('AUX_INDEX_SIDE',(.015,-.035,.085),(.13,.045,.017),'ORTHO',.145),('AUX_PALM_PERSP',(.33,-.30,.22),(.145,-.025,.02),'PERSP',.21)]:
 cd=bpy.data.cameras.new('ANATOMICAL_'+name);cam=bpy.data.objects.new('ANATOMICAL_'+name,cd);sc.collection.objects.link(cam);cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type=typ;cd.ortho_scale=scale;cd.lens=55
dest=OUT/'ORIGINAL_C1_ISOLATED_NOT_APPROVED.blend';assert not dest.exists();sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
views=render_views('ORIGINAL')
facts=dict(time=2.6,qdeg=BASE_Q,bounds_deg=BOUNDS,rig_matrix=RIG_M,root_matrix=ROOT_M,wrist_bone=BASE_BONES['WRIST_R'],palm_points_world={n:list(<REDACTED_EMAIL>[n].head) for n in ['WRIST_R','INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R','MIDDLE_MCP_R','RING_MCP_R','LITTLE_MCP_R']},index_axes_local=c.SETUPS['R','INDEX'][2],index_spread_axis_local=c.SETUPS['R','INDEX'][3],key_black_front_y=KEYS[49]['key_top_playable_surface'][0]['ymin'],baseline_keys=baseline_keys,baseline_self_pairs=sorted(BASE_SELF),active_contacts=active_contacts(B,BL),native=NATIVE,actions=ACTIONS,bones=BASE_BONES,views=views)
save('BASELINE_FACTS.json',facts);np.savez_compressed(OUT/'BASELINE_STATIC.npz',V=B,L=BL,T=T,LT=LT)
protection('BASELINE_INPUT_RECEIPT.json')
print('BASELINE_READY',json.dumps(dict(collision_keys=[(r['key'],r['depth_mm'],r['bvh_pairs']) for r in baseline_keys if r['depth_mm']>1e-6],palm_points=facts['palm_points_world'],self_pairs=len(BASE_SELF),contacts=facts['active_contacts']),ensure_ascii=False),flush=True)
