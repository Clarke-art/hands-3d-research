import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix,Vector
O=Path(__file__).resolve().parent;PREV=O.parent/'hands_c01_whole_hand_motion_feasibility_r1';sys.path.insert(0,str(O));sys.path.insert(0,str(PREV));from geometry_detector import *;import blender_utils as u
P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];results=json.loads((O/'SOLVER_RESULTS.json').read_text());bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);source=bpy.data.scenes[M['scene']];bpy.context.window.scene=source
frozen=u.pf['right_native_sha256'];actual=[];scenes=[]
for test in results['tests']:
 evaluated=[]
 for ai,attempt in enumerate(test.get('attempts',[])):
  bpy.context.window.scene=source;u.settime(source,test['time']);rig=bpy.data.objects[M['mapping']['R']['rig']];mesh=bpy.data.objects[M['mapping']['R']['mesh']];rt=bpy.data.objects[M['mapping']['R']['root']]
  # One full isolated scene copy, then freeze inherited current key/left state. No keyframes inserted.
  for ob in source.objects:ob['STATIC_COPY_REFERENCE']=ob.name
  bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene;sc.name=f"{test['test']}_INIT_{ai+1}_STATIC_ONLY";copied={ob['STATIC_COPY_REFERENCE']:ob for ob in sc.objects if 'STATIC_COPY_REFERENCE' in ob}
  for ob in list(source.objects)+list(sc.objects):
   if 'STATIC_COPY_REFERENCE' in ob:del ob['STATIC_COPY_REFERENCE']
  rig=copied[M['mapping']['R']['rig']];mesh=copied[M['mapping']['R']['mesh']];rt=copied[M['mapping']['R']['root']]
  for ob in sc.objects:
   if ob.animation_data:ob.animation_data_clear()
  u.apply(np.array(attempt['state']),rt,rig);V,F=u.coords(mesh);assert u.digest(u.native(mesh,rig))==frozen
  detection=detect(V,np.array(attempt['key_angles']),dict(midi=test['midi'],finger=test['finger']))
  ct=detection['contact'];touch=ct['top_surface_crossing_triangles']>0 and ct['true_pulp_min_signed_gap_mm'] is not None and ct['true_pulp_surface_contact_distance_mm']<=.05 and ct['near_contact_projected_area_mm2']>0 and ct['pad_horizontal_outside_mm']<=1e-5 and abs(ct['pad_gap_mm'])<=3
  targetDepth=detection['target_key_max_depth_mm']<=.25;clear=detection['wrong_key_or_nonpulp_max_depth_mm']<=.25;selfclear=detection['nonadjacent_self_triangle_pairs']==0
  prep=None;prepok=True
  if test['prepare']:
   prep=contact_metric(V,KEYS[test['prepare']['midi']-21],attempt['key_angles'][test['prepare']['midi']-21],test['prepare']['finger']);prepok=prep['pad_horizontal_outside_mm']<=2 and 4<=prep['pad_gap_mm']<=20
  status='PASS_STATIC_SCREEN_HUMAN_PENDING' if touch and targetDepth and clear and selfclear and prepok else 'NOT_FOUND_IN_THIS_ATTEMPT'
  snap=O/f"{test['test']}_ATTEMPT_{ai+1}_ACTUAL_SKIN.npz";np.savez_compressed(snap,vertices=V)
  evaluated.append(dict(initialization=attempt['initialization'],scene=sc.name,mesh=mesh.name,rig=rig.name,root=rt.name,status=status,contact_gate=touch,target_depth_gate=targetDepth,non_target_gate=clear,self_collision_gate=selfclear,prepare_gate=prepok,preparation_measurement=prep,actual_geometry=detection,controls=dict(state=attempt['state'],root_z_fixed_per_initialization=True,root_translation_delta_mm=attempt['state'][:3],root_extra_rotation_deg=attempt['state'][3:6],joint_increment_deg=np.array(attempt['state'][6:]).reshape(5,4).tolist()),solver=attempt,actual_skin_snapshot=str(snap),frozen_hand_identity_unchanged=True,cameras={v:copied[n].name for v,n in M['cameras'].items()}))
  print('ACTUAL_STATIC_GATE',test['test'],ai+1,status,'skin_gap',round(ct['true_pulp_min_signed_gap_mm'] or 0,6),'own',round(detection['target_key_max_depth_mm'],5),'wrong',round(detection['wrong_key_or_nonpulp_max_depth_mm'],5),'self',detection['nonadjacent_self_triangle_pairs'],'prep',prepok,flush=True)
  bpy.context.window.scene=source
 # Deterministic selection uses actual pass first, then real collision/contact measures, no new solve.
 best=min(evaluated,key=lambda r:(r['status']!='PASS_STATIC_SCREEN_HUMAN_PENDING',r['actual_geometry']['nonadjacent_self_triangle_pairs']>0,r['actual_geometry']['wrong_key_or_nonpulp_max_depth_mm'],abs(r['actual_geometry']['contact']['true_pulp_min_signed_gap_mm'] or 999))) if evaluated else None
 actual.append(dict(test=test['test'],note_id=test['note_id'],midi=test['midi'],finger=test['finger'],source_time=test['time'],status=best['status'] if best else test['status'],selected_initialization=best['initialization'] if best else None,selected_scene=best['scene'] if best else None,attempts=evaluated))
 if best:scenes.append(best)
firstfourpass=all(r['status']=='PASS_STATIC_SCREEN_HUMAN_PENDING' for r in actual if r['test'] in ['S1','S2','S3','S4'])
for r in actual:
 if r['test']=='S5' and not firstfourpass:r['exploratory_actual_status']=r['status'];r['status']='NOT_QUALIFIED_PRECONDITION_NOT_MET';r['reason']='Provisional proxy checks allowed calculation, but stricter actual triangle interior verification later rejected S1. Retain S5 controls as exploratory evidence only; not formal acceptance.'
passed=[r['test'] for r in actual if r['status']=='PASS_STATIC_SCREEN_HUMAN_PENDING'];state='STATIC_FEASIBILITY_PASS' if len(passed)==len(actual) and len(passed)>=4 else 'STATIC_FEASIBILITY_PARTIAL' if passed else 'NOT_FOUND_WITHIN_BUDGET'
if scenes:bpy.context.window.scene=bpy.data.scenes[scenes[0]['scene']]
bpy.context.preferences.filepaths.save_version=0;dest=O/'SKIN_COLLISION_STATIC_DIAGNOSTIC_R1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
output=dict(task='PIANO_HAND_SKIN_COLLISION_STATIC_FEASIBILITY_R1',status=state,authority='DESIGN_PROVISIONAL',collision_method='VALIDATED_FOR_STATIC_SCREEN',total_numerical_wall_seconds=results['total_numerical_wall_seconds'],budget_seconds=600,tests=actual,passed_tests=passed,diagnostic_blend=str(dest),continuous_motion_generated=False,new_keyframes_inserted=0,weights_changed=False,source_shapes_rig_identity_unchanged=True,limitations=['Static only, no force/soft tissue simulation','Near contact area is geometric tolerance area','Source animation datablocks may remain as inherited references; experimental scenes have no bound object animations','S5 was started only after all S1-S4 met provisional proxy checks; final actual checks reported explicitly'])
(O/'STATIC_POSE_FEASIBILITY.json').write_text(json.dumps(output,ensure_ascii=False,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8');(O/'SELECTED_STATIC_SCENES.json').write_text(json.dumps(scenes,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8');print('STATIC_ACTUAL_RESULT',state,passed,flush=True)
