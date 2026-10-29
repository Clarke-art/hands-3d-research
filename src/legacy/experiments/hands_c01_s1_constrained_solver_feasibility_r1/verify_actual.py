import sys,json,time,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
from triangle_distance import *
import blender_utils as u
ai=int(sys.argv[-1]);r=json.loads((O/f'SOLVE_{ai}.json').read_text(encoding='utf-8-sig'));P=json.loads((O/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'));M=P['source_action_scene']
bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False)
source=bpy.data.scenes[M['scene']];bpy.context.window.scene=source;u.settime(source,r['source_time'])
angles=u.keyangles();assert np.max(abs(angles-np.array(r['key_angles'])))<1e-6
expected=json.loads((O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1/ENTRY_CONTEXT_READONLY.json').read_text())['original_key_action_hashes']
actionchecks={str(i):u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i,n in u.man['key_pivots'].items()}
assert expected==actionchecks,'Original key Action changed'
# Verify original 88-key evaluated geometry at this exact action time, before cloning.
keyerrors=[]
for k in KEYS:
 obs=[ob for ob in source.objects if ob.type=='MESH' and ob.get('FROZEN_KEY_INDEX')==k['key_index']]
 assert len(obs)==len(k['geometry'])
 for g in k['geometry']:
  ob=next(ob for ob in obs if g['name'] in ob.name);gv,_=u.coords(ob);want=keyworld(np.array(g['vertices']),k,angles[k['key_index']])
  keyerrors.append(float(np.max(abs(gv-want))))
assert max(keyerrors)<1e-6
for ob in source.objects:ob['CONSTRAINED_STATIC_REF']=ob.name
bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene;sc.name=f'S1_CONSTRAINED_{ai}_STATIC_ONLY'
cp={ob['CONSTRAINED_STATIC_REF']:ob for ob in sc.objects if 'CONSTRAINED_STATIC_REF' in ob}
for ob in list(source.objects)+list(sc.objects):
 if 'CONSTRAINED_STATIC_REF' in ob:del ob['CONSTRAINED_STATIC_REF']
for ob in sc.objects:
 if ob.animation_data:ob.animation_data_clear()
rig=cp[M['mapping']['R']['rig']];mesh=cp[M['mapping']['R']['mesh']];rt=cp[M['mapping']['R']['root']]
u.apply(np.array(r['state']),rt,rig);V,F=u.coords(mesh)
assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
for ki,kn in u.man['key_pivots'].items():assert abs(cp[kn].rotation_euler.x-angles[int(ki)])<1e-6
start=time.monotonic();m=detect(V,angles,dict(midi=67,finger=1));ct=m['contact'];prep=contact_metric(V,KEYS[55],angles[55],3)
gates=dict(actual_surface_contact=ct['top_surface_crossing_triangles']>0 and ct['true_pulp_surface_contact_distance_mm']<=.05 and ct['near_contact_projected_area_mm2']>0,pad_inside_playable_top=ct['pad_horizontal_outside_mm']<=1e-5,pad_height_auxiliary=abs(ct['pad_gap_mm'])<=3,target_entity_depth=m['target_key_max_depth_mm']<=.25,non_target_and_nonpulp_depth=m['wrong_key_or_nonpulp_max_depth_mm']<=.25,no_nonadjacent_finger_crossing=m['nonadjacent_self_triangle_pairs']==0,prepared_E5=prep['pad_horizontal_outside_mm']<=2 and 4<=prep['pad_gap_mm']<=20,authorized_bounds=bool(np.all(np.r_[r['state'][:2],r['state'][3:]]>=np.array(r['bounds_lower'])-1e-7) and np.all(np.r_[r['state'][:2],r['state'][3:]]<=np.array(r['bounds_upper'])+1e-7)))
mr=next(p for p in m['self_skin'] if p['digits']==['MIDDLE','RING'])
exact=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],mr['minimum_gap_sampled_mm']/1000+1e-10) if not mr['true_nonadjacent_triangle_pair_count'] else dict(distance_mm=0.,reason='Actual surface intersection exists')

parity=None # Measured externally from the independently saved Blender snapshot; Blender Python ABI differs.
np.savez_compressed(O/f'ACTUAL_SKIN_{ai}.npz',vertices=V,key_angles=angles)
keys88=[dict(key_index=k['key_index'],midi=k['midi_note'],note=k['note_name'],target=k['midi_note']==67,max_entity_depth_mm=max([h['maximum_triangle_surface_inside_depth_mm'] for h in m['key_hits'] if h['midi']==k['midi_note']]+[0.])) for k in KEYS]
out=dict(attempt=ai,authority='DESIGN_PROVISIONAL',status='S1_STATIC_GATE_PASS' if all(gates.values()) else 'STATIC_BLOCKED',gates=gates,actual_geometry=m,all_88_key_depths=keys88,E5_preparation=prep,middle_ring_exact_clearance=exact,solver=r,state=r['state'],controls=dict(root_translation_mm=r['state'][:3],root_rotation_deg=r['state'][3:6],fingers={d:r['state'][6+4*j:10+4*j] for j,d in enumerate(DIGITS)}),scene=sc.name,mesh=mesh.name,rig=rig.name,root=rt.name,cameras={v:cp[n].name for v,n in M['cameras'].items()},original_key_action_payloads_unchanged=True,original_key_geometry_max_error_m=max(keyerrors),key_angle_error_rad=float(np.max(abs(angles-np.array(r['key_angles'])))),native_frozen_identity_verified=True,proxy_max_vertex_error_mm=parity,verification_seconds=time.monotonic()-start,experimental_bound_actions=0,new_keyframes=0)
(O/f'ACTUAL_VALIDATION_{ai}.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
folder=O/'stills';folder.mkdir(exist_ok=True);manifest=[]
for view in ['OVERHEAD','SIDE_OBLIQUE']:
 sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.display.shading.light='STUDIO';sc.display.shading.color_type='OBJECT';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world.color=(.08,.08,.08)
 cam=cp[M['cameras'][view]];sc.camera=cam;cam.data.ortho_scale=.34;target=Vector(((KEYS[46]['key_center'][0]+KEYS[58]['key_center'][0])/2,-.035,.014));cam.location=target+Vector((0,0,.8) if view=='OVERHEAD' else (.11,-.48,.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 overlays=[];font=bpy.data.curves.new('CONSTRAINED_REVIEW_LABEL','FONT');font.body=f"S1 #{ai}: {out['status']} / DESIGN_PROVISIONAL";font.size=.0055;ob=bpy.data.objects.new('REVIEW_LABEL',font);sc.collection.objects.link(ob);ob.rotation_euler=cam.rotation_euler;ob.location=cam.matrix_world@Vector((-.162,.081,-.42));ob.color=(1,.25,.1,1);overlays.append(ob)
 faces=sorted({t for p in m['self_skin'] for pair in p['triangle_pair_ids'] for t in pair})
 if faces:
  me=bpy.data.meshes.new('COLLISION_OVERLAY');me.from_pydata(V.tolist(),[],TR[faces].tolist());me.update();ob=bpy.data.objects.new('RED_ACTUAL_COLLISION_FACES',me);sc.collection.objects.link(ob);ob.color=(1,.01,.01,1);overlays.append(ob)
 file=folder/f'S1_{ai}_{view}.png';sc.render.filepath=str(file);bpy.ops.render.render(write_still=True)
 manifest.append(dict(file=str(file),attempt=ai,view=view,resolution=[1280,720],actual_mesh=True,caption=font.body))
 for ob in overlays:bpy.data.objects.remove(ob,do_unlink=True)
(O/f'STILLS_{ai}.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
if all(gates.values()):
 bpy.context.preferences.filepaths.save_version=0
 dest=O/'S1_CONSTRAINED_DIAGNOSTIC_R1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
 bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes[out['scene']]
 VR,_=u.coords(bpy.data.objects[out['mesh']]);re=detect(VR,angles,dict(midi=67,finger=1))
 readback=dict(max_vertex_difference_mm=float(np.linalg.norm(VR-V,axis=1).max()*1000),actual_geometry=re,native_identity_verified=u.digest(u.native(bpy.data.objects[out['mesh']],bpy.data.objects[out['rig']]))==u.pf['right_native_sha256'])
 assert readback['max_vertex_difference_mm']<.001
 (O/f'READBACK_{ai}.json').write_text(json.dumps(readback,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
print('BLENDER_ACCEPTANCE',ai,out['status'],gates,'contact',ct['true_pulp_surface_contact_distance_mm'],'depth',m['target_key_max_depth_mm'],'wrong',m['wrong_key_or_nonpulp_max_depth_mm'],'self',m['nonadjacent_self_triangle_pairs'],'MR',exact,flush=True)

