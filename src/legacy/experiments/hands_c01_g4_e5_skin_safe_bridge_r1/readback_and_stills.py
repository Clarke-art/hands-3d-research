import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'));from geometry_detector import *;from triangle_distance import *;import blender_utils as u
P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];rows=[];manifest=[];folder=O/'stills';folder.mkdir(exist_ok=True)
def closest_footprint(V):
 k=KEYS[46];ang=angles[46];p=keylocal(V,k,ang);patch=set(META['pad_patches'][0]);best=None
 for ti in np.flatnonzero(LABEL==0):
  if not all(int(v) in patch for v in TR[ti]):continue
  for s in k['key_top_playable_surface']:
   poly=list(p[TR[ti]])
   for ax,lim,sgn in [(0,s['xmin'],-1),(0,s['xmax'],1),(1,s['ymin'],-1),(1,s['ymax'],1)]:poly=clip(poly,ax,lim,sgn) if poly else []
   for q in poly:
    gap=(q[2]-s['z'])*1000
    if best is None or gap<best['signed_vertical_gap_mm']:
     best=dict(hand_triangle_id=int(ti),signed_vertical_gap_mm=float(gap),skin_clipped_point_world_m=keyworld(np.array([q]),k,ang)[0].tolist(),playable_top_point_world_m=keyworld(np.array([[q[0],q[1],s['z']]]),k,ang)[0].tolist())
 return best

def render(sc,info,label,view,V,faces=None):
 bpy.context.window.scene=sc;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world.color=(.08,.08,.08)
 cam=bpy.data.objects[info['cameras'][view]];sc.camera=cam;cam.data.ortho_scale=.34;target=Vector(((u.c.KEYS[46]['key_center'][0]+u.c.KEYS[58]['key_center'][0])/2,-.035,.014));cam.location=target+Vector((0,0,.8) if view=='OVERHEAD' else (.11,-.48,.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();overlays=[]
 caption='S1 #1: CONTACT; FAIL MIDDLE/RING CROSSING (9 PAIRS)' if label=='S1_1' else 'S1 #2: NO CROSSING; FAIL REAL CONTACT (4.842 um HOVER)' if label=='S1_2' else 'S2: STATIC ONLY; MIDDLE/RING EXACT GAP 0.11775 mm'
 font=bpy.data.curves.new('REVIEW_LABEL','FONT');font.body=caption;font.size=.0055;ob=bpy.data.objects.new('REVIEW_LABEL',font);sc.collection.objects.link(ob);ob.rotation_euler=cam.rotation_euler;ob.location=cam.matrix_world@Vector((-.162,.081,-.42));ob.color=(1,.25,.1,1);overlays.append(ob)
 if faces:
  # Actual intersecting triangles are colored in an overlay; source skin is unchanged.
  ids=sorted(set(faces));me=bpy.data.meshes.new('ACTUAL_COLLISION_FACE_OVERLAY');me.from_pydata(V.tolist(),[],TR[ids].tolist());me.update();ob=bpy.data.objects.new('RED_ACTUAL_COLLISION_FACES',me);sc.collection.objects.link(ob);ob.color=(1,.015,.015,1);overlays.append(ob)
  point=Vector(V[TR[ids]].mean((0,1)));bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.0012,location=point+Vector((0,0,.015)));ob=bpy.context.object;ob.color=(1,.02,.02,1);overlays.append(ob)
  cr=bpy.data.curves.new('LOCATION_CONNECTOR','CURVE');cr.dimensions='3D';cr.bevel_depth=.0002;ln=cr.splines.new('POLY');ln.points.add(1);ln.points[0].co=(*point,1);ln.points[1].co=(*(point+Vector((0,0,.015))),1);ob=bpy.data.objects.new('LOCATION_CONNECTOR',cr);sc.collection.objects.link(ob);ob.color=(1,.02,.02,1);overlays.append(ob)
 file=folder/f'{label}_{view}.png';sc.render.filepath=str(file);bpy.ops.render.render(write_still=True);manifest.append(dict(file=str(file),test=label,view=view,caption=caption,resolution=[1280,720],actual_mesh=True,overlay_is_diagnostic_only=True))
 for ob in overlays:bpy.data.objects.remove(ob,do_unlink=True)

bpy.ops.wm.open_mainfile(filepath=str(O/'S1_SKIN_SAFE_REPAIR_DIAGNOSTIC_R1.blend'),load_ui=False,use_scripts=False)
for ai in [1,2]:
 info=json.loads((O/f'S1_REPAIR_{ai}_ACTUAL_VALIDATION.json').read_text());sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;mesh=bpy.data.objects[info['mesh']];rig=bpy.data.objects[info['rig']];V,F=u.coords(mesh);assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256'];snap=np.load(O/f'S1_REPAIR_{ai}_ACTUAL_SKIN.npz')['vertices'];diff=float(np.linalg.norm(V-snap,axis=1).max()*1000);assert diff<.001
 # Object copy names can differ; find each original key pivot via matching positions/name family.
 angles=np.zeros(88)
 for ki,kn in u.man['key_pivots'].items():
  candidates=[ob for ob in sc.objects if ob.name==kn or ob.name.startswith(kn+'.')];assert len(candidates)==1;angles[int(ki)]=candidates[0].rotation_euler.x
 assert np.max(np.abs(angles-np.array(info['solver']['key_angles'])))<1e-6
 m=detect(V,angles,dict(midi=67,finger=1));foot=closest_footprint(V);mr=next(p for p in m['self_skin'] if p['digits']==['MIDDLE','RING']);exact=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],mr['minimum_gap_sampled_mm']/1000+1e-10) if not mr['true_nonadjacent_triangle_pair_count'] else dict(distance_mm=0.,reason='Actual BVH surface intersections exist')
 rows.append(dict(attempt=ai,readback_vertex_error_mm=diff,key_angle_max_error_rad=float(np.max(np.abs(angles-np.array(info['solver']['key_angles'])))),actual_geometry=m,closest_clipped_thumb_footprint=foot,middle_ring_exact_clearance=exact))
 faces=[i for p in m['self_skin'] for pair in p['triangle_pair_ids'] for i in pair];render(sc,info,f'S1_{ai}','OVERHEAD',V,faces);render(sc,info,f'S1_{ai}','SIDE_OBLIQUE',V,faces)
# Read-only load S2 diagnostic and render one representative view; never save this prior file.
old=O.parent/'hands_skin_collision_static_feasibility_r1';oldres=json.loads((old/'STATIC_POSE_FEASIBILITY.json').read_text());s2=oldres['tests'][1];info=next(a for a in s2['attempts'] if a['scene']==s2['selected_scene']);bpy.ops.wm.open_mainfile(filepath=oldres['diagnostic_blend'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[info['scene']];bpy.context.window.scene=sc;V,F=u.coords(bpy.data.objects[info['mesh']]);assert np.max(np.abs(V-np.load(old/'S2_ATTEMPT_1_ACTUAL_SKIN.npz')['vertices']))<1e-8;render(sc,info,'S2','SIDE_OBLIQUE',V)
(O/'INDEPENDENT_READBACK_CHECKS.json').write_text(json.dumps(rows,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8');(O/'STILL_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8');print('READBACK_AND_STILLS_COMPLETE',len(manifest),flush=True)
