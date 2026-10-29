import json
from pathlib import Path
import numpy as np
O=Path(__file__).resolve().parent;F=json.loads((O/'STATIC_POSE_FEASIBILITY.json').read_text());A=json.loads((O.parent/'hands/audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json').read_text(encoding='utf-8-sig'))['poses'];base=np.array(json.loads((O/'SKIN_MODEL_META.json').read_text())['root_base_xyz_m'])
for r in F['tests']:
 reference='R2' if r['test'] in ['S2','S4'] else 'R1'
 for a in r['attempts']:
  st=np.array(a['controls']['state']);a['difference_from_approved_static']=dict(reference=reference,root_xyz_m=(base+st[:3]/1000).tolist(),root_position_delta_mm=((base+st[:3]/1000-np.array(A[reference]['root_xyz_m']))*1000).tolist(),extra_rotation_relative_approved_R1_deg=st[3:6].tolist(),joint_increment_delta_deg=(st[6:].reshape(5,4)-np.array(A[reference]['joint_increments_deg'])).tolist(),root_z_unchanged_from_this_initialization=True)
F['metric_definitions']=dict(contact_distance='Minimum true pulp-to-current top-surface distance, zero when the actual clipped skin triangle touches/crosses the playable top surface',signed_vertical_gap='Minimum signed pulp height over playable top polygons; negative does not itself define 3D solid-depth',intrusion_depth='Maximum minimum-normal distance inside each actual convex key piece, considering vertices and exact triangle interior extrema',contact_area='Projected skin surface area in a ±0.05mm slab, not actual soft-tissue/force-bearing area',self_collision='BVH intersection of confident semantic digit triangles after excluding original topology-neighbor/shared-vertex pairs',self_depth='Not inferred from intersection counts; null where not separately computed',minimum_skin_gap='Sampled vertex-to-BVH-triangle gap; not a continuous-motion or exhaustive edge-edge certificate')
F['method_validation_artifact']='COLLISION_METHOD_TESTS.json';F['source_diagnosis_artifact']='SOURCE_POSE_COLLISION_DIAGNOSES.json';F['final_acceptance_tolerances_locked_before_solve']=True;F['no_second_solver_run']=True;F['s5_not_formally_accepted']=True
(O/'STATIC_POSE_FEASIBILITY.json').write_text(json.dumps(F,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Keep the already-rendered failed S1 initialization explicit: no selection/figure identity confusion.
shots=json.loads((O/'STILL_MANIFEST.json').read_text())
for s in shots:
 s['display_label']=s['caption'];s['caption_location']='Report beside exact static frame; red geometric witness markers on failed views where visible';s['rendered_initialization']=next((a['initialization'] for r in F['tests'] for a in r['attempts'] if a['scene']==s['scene']),None)
(O/'STILL_MANIFEST.json').write_text(json.dumps(shots,indent=2)+'\n',encoding='utf8')
print('CONTROLS_AND_METRIC_DEFINITIONS_SAVED')
