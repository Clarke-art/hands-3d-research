import sys,json,ast,time
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands';sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
from triangle_distance import *
import blender_utils as u
RAW=D
tree=ast.parse((O/'extract_anatomy.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['unit','angle','matrix','coords','signed_rot','anatomy']],type_ignores=[]),'independent_actual_anatomy','exec'))
import math
ai=int(sys.argv[-1]);r=json.loads((O/f'B_SOLVE_{ai}.json').read_text(encoding='utf-8-sig'));P=json.loads((O/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'));M=P['source_action_scene']
bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);source=bpy.data.scenes[M['scene']];bpy.context.window.scene=source;u.settime(source,r['source_time'])
angles=u.keyangles();assert np.max(abs(angles-np.array(r['key_angles'])))<1e-6
oldhash=json.loads((O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1/ENTRY_CONTEXT_READONLY.json').read_text())['original_key_action_hashes']
current={str(i):u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i,n in u.man['key_pivots'].items()};assert oldhash==current
keyerrs=[]
for k in KEYS:
 obs=[ob for ob in source.objects if ob.type=='MESH' and ob.get('FROZEN_KEY_INDEX')==k['key_index']]
 assert len(obs)==len(k['geometry'])
 for g in k['geometry']:
  ob=next(ob for ob in obs if g['name'] in ob.name);vv,_=u.coords(ob);keyerrs.append(float(np.max(abs(vv-keyworld(np.array(g['vertices']),k,angles[k['key_index']])))))
assert max(keyerrs)<1e-6
for ob in source.objects:ob['ANATOMY_EXPERIMENT_REF']=ob.name
bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene;sc.name=f'S1_NATURAL_B_{ai}_STATIC_ONLY';cp={ob['ANATOMY_EXPERIMENT_REF']:ob for ob in sc.objects if 'ANATOMY_EXPERIMENT_REF' in ob}
for ob in list(source.objects)+list(sc.objects):
 if 'ANATOMY_EXPERIMENT_REF' in ob:del ob['ANATOMY_EXPERIMENT_REF']
for ob in sc.objects:
 if ob.animation_data:ob.animation_data_clear()
rig=cp[M['mapping']['R']['rig']];mesh=cp[M['mapping']['R']['mesh']];rt=cp[M['mapping']['R']['root']]
u.apply(np.array(r['state']),rt,rig);V,F=u.coords(mesh);assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
start=time.monotonic();m=detect(V,angles,dict(midi=67,finger=1));ct=m['contact'];prep=contact_metric(V,KEYS[55],angles[55],3);an=anatomy(rig,mesh,f'B_{ai}',state=r['state'])
aq=np.array(an['recovered_controls']);expect=(1-r['lambda_reference'])*np.array(r['reference_q_R1'])[1:]+r['lambda_reference']*np.array(r['reference_q_R2'])[1:]
err=float(np.max(abs(aq[1:]-expect)));axiserr=max(j['off_model_rotation_matrix_error'] for d in an['digits'] for j in d['joints']);parametererr=float(np.max(abs(aq-np.array(r['state'][6:]).reshape(5,4))))
gates=dict(actual_G4_pulp_contact=ct['top_surface_crossing_triangles']>0 and ct['true_pulp_surface_contact_distance_mm']<=.05 and ct['near_contact_projected_area_mm2']>0,pad_inside_G4=ct['pad_horizontal_outside_mm']<=1e-5,pad_height_aux=abs(ct['pad_gap_mm'])<=3,target_entity_depth=m['target_key_max_depth_mm']<=.25,non_target_and_nonpulp_depth=m['wrong_key_or_nonpulp_max_depth_mm']<=.25,all_five_finger_skin_no_crossing=m['nonadjacent_self_triangle_pairs']==0,passive_approved_family=err<=1e-4,no_off_model_joint_rotations=axiserr<=1e-5,actual_controls_match=parametererr<=1e-4,stage_early_middle_pad_clearance=prep['pad_gap_mm']>=4,original_root_Z_fixed=abs(r['state'][2]-r['original_A_state'][2])<1e-12)
mr=next(p for p in m['self_skin'] if p['digits']==['MIDDLE','RING'])
exact=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],mr['minimum_gap_sampled_mm']/1000+1e-10) if not mr['true_nonadjacent_triangle_pair_count'] else dict(distance_mm=0.,reason='True surface crossing')
keys88=[dict(midi=k['midi_note'],note=k['note_name'],max_entity_depth_mm=max([h['maximum_triangle_surface_inside_depth_mm'] for h in m['key_hits'] if h['midi']==k['midi_note']]+[0.])) for k in KEYS]
out=dict(attempt=ai,status='REFERENCE_STATIC_GATES_PASS' if all(gates.values()) else 'STATIC_BLOCKED',authority='DESIGN_PROVISIONAL',Human_visual_naturalness='PENDING',A_baseline_Human_fail_unchanged=True,gates=gates,actual_geometry=m,all_88_key_depths=keys88,actual_anatomy=an,E5_old_exact_target_metric=prep,old_E5_target_gate=prep['pad_horizontal_outside_mm']<=2 and 4<=prep['pad_gap_mm']<=20,stage_strategy='natural early hand ready; precise E5 hovering is not required at S1',middle_ring_exact_clearance=exact,passive_family_max_control_error_deg=err,off_model_rotation_error=axiserr,all_controls_max_error_deg=parametererr,original_key_action_payloads_unchanged=True,key_geometry_error_m=max(keyerrs),key_angle_error_rad=float(np.max(abs(angles-np.array(r['key_angles'])))),solver=r,state=r['state'],scene=sc.name,mesh=mesh.name,rig=rig.name,root=rt.name,cameras={v:cp[n].name for v,n in M['cameras'].items()},experimental_bound_actions=0,new_keyframes=0,verification_seconds=time.monotonic()-start)
np.savez_compressed(O/f'B_ACTUAL_SKIN_{ai}.npz',vertices=V,key_angles=angles)
(O/f'B_ACTUAL_{ai}.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
if all(gates.values()):
 bpy.context.preferences.filepaths.save_version=0;dest=O/'S1_ANATOMY_PREPARATION_DIAGNOSTIC_R1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
 bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes[out['scene']]
 vr,_=u.coords(bpy.data.objects[out['mesh']]);mm=detect(vr,angles,dict(midi=67,finger=1));ar=anatomy(bpy.data.objects[out['rig']],bpy.data.objects[out['mesh']],f'B_{ai}_READBACK')
 rb=dict(vertex_difference_mm=float(np.linalg.norm(vr-V,axis=1).max()*1000),actual_geometry=mm,anatomy=ar,native_identity_verified=u.digest(u.native(bpy.data.objects[out['mesh']],bpy.data.objects[out['rig']]))==u.pf['right_native_sha256'])
 assert rb['vertex_difference_mm']<.001
 (O/f'B_READBACK_{ai}.json').write_text(json.dumps(rb,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
print('B_ACTUAL',ai,out['status'],gates,'contact',ct['true_pulp_surface_contact_distance_mm'],'depth',m['target_key_max_depth_mm'],'wrong',m['wrong_key_or_nonpulp_max_depth_mm'],'self',m['nonadjacent_self_triangle_pairs'],'middle ring',exact,'E5 outside',prep['pad_horizontal_outside_mm'],flush=True)
