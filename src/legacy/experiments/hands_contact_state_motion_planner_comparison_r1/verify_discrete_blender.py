import sys,json,ast,time
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_c01_g4_e5_natural_motion_bridge_r2';sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
from triangle_distance import *
import blender_utils as u
RAW=D
tr=ast.parse((O/'extract_anatomy.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tr.body if isinstance(n,ast.FunctionDef) and n.name in ['unit','angle','matrix','coords','signed_rot','anatomy']],type_ignores=[]),'anatomy','exec'))
tr=ast.parse((PRE/'bake_and_validate.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tr.body if isinstance(n,ast.FunctionDef) and n.name=='strict'],type_ignores=[]),'strict_pulp','exec'))
P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[M['mapping']['R']['rig']];mesh=bpy.data.objects[M['mapping']['R']['mesh']];rt=bpy.data.objects[M['mapping']['R']['root']]
expected=json.loads((O/'ORIGINAL_ACTION_INSPECTION.json').read_text())['action_payloads'];assert {str(i):u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i,n in u.man['key_pivots'].items()}==expected
B=json.loads((O.parent/'hands_c01_anatomy_preparation_audit_r1/B_SOLVE_2.json').read_text());E=json.loads((O/'ENDPOINT_SOLVE_2.json').read_text());Q0=np.array(E['reference_q_R1']);Q1=np.array(E['reference_q_R2']);ACTIVE=np.array(E['active_flex_anchor'])
runs=[dict(phase='P1',method='READ_ONLY_B2',display_time=2.527855,state=B['state'],latent=B['state'][:10]+[B['lambda_reference'],0]),dict(phase='P4',method='READ_ONLY_E5_ENDPOINT',display_time=2.956426,state=E['state'],latent=E['state'][:10]+[E['lambda_reference'],E['active_flex_alpha']])]
for phase in ['P2','P3']:
 for method in ['SLSQP','MINK_DAQP']:runs.append(json.loads((O/f'{phase}_{method}_SOLVE.json').read_text()))
results=[];start=time.monotonic()
for run in runs:
 t=run['display_time'];u.settime(sc,t);angles=u.keyangles();u.apply(np.array(run['state']),rt,rig);V,F=u.coords(mesh);identity=u.digest(u.native(mesh,rig))==u.pf['right_native_sha256'];assert identity
 target=67 if run['phase'] in ['P1','P2'] else 76;finger=1 if target==67 else 3;geo=detect(V,angles,dict(midi=target,finger=finger));ct=geo['contact'];cross=strict(V,KEYS[target-21],angles[target-21],finger);an=anatomy(rig,mesh,run['phase']+'_'+run['method'],state=run['state']);q=np.array(an['recovered_controls']);z=run['latent'];ref=(1-z[10])*Q0[1:]+z[10]*Q1[1:];ref[1,:3]=(1-z[11])*ref[1,:3]+z[11]*ACTIVE;err=float(np.max(abs(q[1:]-ref)));axis=max(j['off_model_rotation_matrix_error'] for d in an['digits'] for j in d['joints']);mr=next(x for x in geo['self_skin'] if x['digits']==['MIDDLE','RING']);gap=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],max(mr['minimum_gap_sampled_mm']/1000+1e-10,1e-7)) if not mr['true_nonadjacent_triangle_pair_count'] else dict(distance_mm=0)
 gates=dict(strict_pulp_contact=cross>0 and ct['top_surface_crossing_triangles']>0 and ct['near_contact_projected_area_mm2']>0,pad_inside=ct['pad_horizontal_outside_mm']<=1e-5,pad_aux_height=abs(ct['pad_gap_mm'])<=3,target_depth=geo['target_key_max_depth_mm']<=.25,non_target_depth=geo['wrong_key_or_nonpulp_max_depth_mm']<=.25,interfinger_surfaces=geo['nonadjacent_self_triangle_pairs']==0,natural_reference_family=err<.001 and -1e-5<=z[10]<=1+1e-5 and -1e-5<=z[11]<=1+1e-5,authorized_axes=axis<1e-5)
 ek=KEYS[55];goal=np.array([ek['key_center'][0],.035,ek['key_top_playable_surface'][0]['z']]);pad=V[int(RAW['pad_indices'][2])];wrist=list(<REDACTED_EMAIL>['WRIST_R'].head)
 out=dict(phase=run['phase'],method=run['method'],display_time=t,solver=run,gates=gates,all_geometry_and_joint_gates=all(gates.values()),strict_crossing_faces=cross,geometry=geo,anatomy=an,middle_ring_exact=gap,native_frozen_identity=identity,wrist_world_m=wrist,middle_pad_world_m=pad.tolist(),middle_pad_distance_to_E5_reference_mm=float(np.linalg.norm(pad-goal)*1000),source_key_angles=angles.tolist(),reference_error_deg=err,off_axis_matrix_error=axis,scope='DISCRETE_STATE_FEASIBILITY_ONLY',Human_naturalness='PENDING',no_new_action=True)
 results.append(out);print('ACTUAL_DISCRETE',run['phase'],run['method'],gates,'depth',geo['target_key_max_depth_mm'],'wrong',geo['wrong_key_or_nonpulp_max_depth_mm'],'gap',gap,flush=True)
(O/'ACTUAL_DISCRETE_VALIDATION.json').write_text(json.dumps(dict(results=results,elapsed_seconds=time.monotonic()-start,source_saved=False,original_key_action_payloads_unchanged=True,Blender_version=bpy.app.version_string),indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()))
