import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'));from geometry_detector import *;import blender_utils as u
ai=int(sys.argv[-1]);r=json.loads((O/f'REPAIR_ATTEMPT_{ai+1}.json').read_text());P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];dest=O/'S1_SKIN_SAFE_REPAIR_DIAGNOSTIC_R1.blend'
bpy.ops.wm.open_mainfile(filepath=str(dest) if dest.exists() else M['path'],load_ui=False,use_scripts=False);source=bpy.data.scenes[M['scene']];bpy.context.window.scene=source;u.settime(source,r['source_time'])
for ob in source.objects:ob['BRIDGE_STATIC_COPY_REF']=ob.name
bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene;sc.name=f'S1_REPAIR_{ai+1}_STATIC_ONLY';cp={ob['BRIDGE_STATIC_COPY_REF']:ob for ob in sc.objects if 'BRIDGE_STATIC_COPY_REF' in ob}
for ob in list(source.objects)+list(sc.objects):
 if 'BRIDGE_STATIC_COPY_REF' in ob:del ob['BRIDGE_STATIC_COPY_REF']
for ob in sc.objects:
 if ob.animation_data:ob.animation_data_clear()
rig=cp[M['mapping']['R']['rig']];mesh=cp[M['mapping']['R']['mesh']];rt=cp[M['mapping']['R']['root']];u.apply(np.array(r['state']),rt,rig);V,F=u.coords(mesh);assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
# Measured current cloned key transforms must agree with the original recorded angle; keys are frozen at source time, not raised to rest.
keycheck=[]
for k in KEYS:
 name=P['source_input']['source']['key_objects'][str(k['midi_note'])] if False else None
angles=np.zeros(88)
for ki,kn in u.man['key_pivots'].items():angles[int(ki)]=cp[kn].rotation_euler.x
angle_error=float(np.max(np.abs(angles-np.array(r['key_angles']))));assert angle_error<1e-6
start=time.monotonic();m=detect(V,angles,dict(midi=67,finger=1));ct=m['contact'];prep=contact_metric(V,KEYS[55],angles[55],3)
gates=dict(actual_surface_contact=ct['top_surface_crossing_triangles']>0 and ct['true_pulp_surface_contact_distance_mm']<=.05 and ct['near_contact_projected_area_mm2']>0,pad_inside_playable_top=ct['pad_horizontal_outside_mm']<=1e-5,pad_height_auxiliary=abs(ct['pad_gap_mm'])<=3,target_entity_depth=m['target_key_max_depth_mm']<=.25,non_target_and_nonpulp_depth=m['wrong_key_or_nonpulp_max_depth_mm']<=.25,no_nonadjacent_finger_crossing=m['nonadjacent_self_triangle_pairs']==0,prepared_E5=prep['pad_horizontal_outside_mm']<=2 and 4<=prep['pad_gap_mm']<=20)
status='S1_STATIC_GATE_PASS' if all(gates.values()) else 'STATIC_BLOCKED';np.savez_compressed(O/f'S1_REPAIR_{ai+1}_ACTUAL_SKIN.npz',vertices=V,key_angles=angles)
out=dict(status=status,attempt=ai+1,authority='DESIGN_PROVISIONAL',gates=gates,actual_geometry=m,E5_preparation=prep,state=r['state'],scene=sc.name,mesh=mesh.name,root=rt.name,rig=rig.name,cameras={v:cp[n].name for v,n in M['cameras'].items()},verification_wall_seconds=time.monotonic()-start,solver=r,frozen_native_identity_verified=True,key_angle_max_difference_rad=angle_error,experimental_bound_object_actions=0,new_keyframes=0)
(O/f'S1_REPAIR_{ai+1}_ACTUAL_VALIDATION.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest));print('S1_INDEPENDENT_ACTUAL_GATE',ai+1,status,gates,'depth',m['target_key_max_depth_mm'],'wrong',m['wrong_key_or_nonpulp_max_depth_mm'],'self',m['nonadjacent_self_triangle_pairs'],'prep',prep['pad_gap_mm'],flush=True)

