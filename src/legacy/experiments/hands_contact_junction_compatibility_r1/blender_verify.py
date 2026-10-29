import sys,json,ast,time,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
from triangle_distance import *
import blender_utils as u
RAW=D;P=json.loads((O/'POLICY_LOCK.json').read_text());I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());PRE=O.parent/'hands_contact_state_motion_planner_comparison_r1'
tree=ast.parse((O/'extract_anatomy.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['unit','angle','matrix','coords','signed_rot','anatomy']],type_ignores=[]),'anatomy','exec'))
tree=ast.parse((O.parent/'hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='strict'],type_ignores=[]),'strict','exec'))
M=P['source_action_scene'];bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[M['mapping']['R']['rig']];mesh=bpy.data.objects[M['mapping']['R']['mesh']];rt=bpy.data.objects[M['mapping']['R']['root']]
expected=json.loads((PRE/'ORIGINAL_ACTION_INSPECTION.json').read_text())['action_payloads'];actual={str(i):u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i,n in u.man['key_pivots'].items()};assert expected==actual
E=json.loads((O/'ENDPOINT_SOLVE_2.json').read_text());Q0=np.array(E['reference_q_R1']);Q1=np.array(E['reference_q_R2']);ACTIVE=np.array(E['active_flex_anchor'])
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:
 rows=[]
 for t in [2.527855,2.72,I['junction_time']-.0001,I['junction_time'],I['junction_time']+.0001,2.956426]:
  u.settime(sc,t);a=u.keyangles();rows.append(dict(time=t,angles=a.tolist()))
 assert abs(rows[3]['angles'][I['hold']['midi']-21]-.08712320774793625)<1e-7
 assert abs(rows[3]['angles'][I['next']['midi']-21])<1e-7
 np.savez_compressed(O/'BOUNDARY_KEY_STATES.npz',times=[r['time'] for r in rows],angles=[r['angles'] for r in rows])
 out=dict(status='BOUNDARY_CONTRACT_PASS',source_contract=str(PRE/'CONTACT_STATE_SEQUENCE.json'),joint_time=I['junction_time'],left_limit_requires='old HOLD true surface contact',right_limit_requires='new PRESS contact from ON at initial key position',position_continuity_requires_intersection_of_closed_contact_sets=True,does_not_require_two_fully_depressed_keys=True,force_and_acoustic_attack='NOT_MODELLED',rows=rows,action_payloads=actual,native_identity=u.digest(u.native(mesh,rig))==u.pf['right_native_sha256'],source_saved=False)
 (O/'BOUNDARY_SOURCE_VERIFICATION.json').write_text(json.dumps(out,indent=2));print('BOUNDARY_CONTRACT_PASS',flush=True)
else:
 runpath=Path(args[0]);r=json.loads(runpath.read_text());u.settime(sc,r['display_time']);a=u.keyangles();u.apply(np.array(r['state']),rt,rig);V,F=u.coords(mesh);identity=u.digest(u.native(mesh,rig))==u.pf['right_native_sha256'];assert identity
 results=[];active={ct['midi'] for ct in r['contacts']}
 for ct in r['contacts']:
  note=ct['midi'];finger=ct['finger'];g=detect(V,a,dict(midi=note,finger=finger));contact=g['contact'];cross=strict(V,KEYS[note-21],a[note-21],finger);gate=bool(cross>0 and contact['top_surface_crossing_triangles']>0 and contact['near_contact_projected_area_mm2']>0 and contact['pad_horizontal_outside_mm']<=1e-5 and abs(contact['pad_gap_mm'])<=3);results.append(dict(midi=note,finger=finger,strict_crossing_faces=cross,contact_gate=gate,geometry=g))
 wrong=max([h['maximum_triangle_surface_inside_depth_mm'] for h in results[0]['geometry']['key_hits'] if h['midi'] not in active]+[h['wrong_region_depth_mm'] for ct in results for h in ct['geometry']['key_hits'] if h['midi']==ct['midi']]+[0.]);dep=max(ct['geometry']['target_key_max_depth_mm'] for ct in results)
 an=anatomy(rig,mesh,r['id'],state=r['state']);q=np.array(an['recovered_controls']);z=np.array(r['latent']);ref=(1-z[10])*Q0[1:]+z[10]*Q1[1:];ref[1,:3]=(1-z[11])*ref[1,:3]+z[11]*ACTIVE;err=float(np.max(abs(q[1:]-ref)));axis=max(j['off_model_rotation_matrix_error'] for d in an['digits'] for j in d['joints']);domain=bool(np.all(z[:3]>=np.array([-150,-30,-12.217247311392744])-.001) and np.all(z[:3]<=np.array([60,35,12])+.001) and np.all(abs(z[3:6])<=np.array([8,8,12])+.001) and np.all(q[0]>=np.array([0,0,0,-35])-.001) and np.all(q[0]<=np.array([25,25,18,35])+.001) and np.all(z[10:]>=-1e-6) and np.all(z[10:]<=1+1e-6))
 g=results[0]['geometry'];mr=next(x for x in g['self_skin'] if x['digits']==['MIDDLE','RING']);gap=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],max(mr['minimum_gap_sampled_mm']/1000+1e-10,1e-7)) if not mr['true_nonadjacent_triangle_pair_count'] else dict(distance_mm=0)
 finger=I['next']['finger'];ek=KEYS[I['next']['midi']-21];pad=V[int(RAW['pad_indices'][finger-1])];pl=keylocal(np.array([pad]),ek,a[ek['key_index']])[0];dist=min(np.linalg.norm(pl-np.array([np.clip(pl[0],s['xmin'],s['xmax']),np.clip(pl[1],s['ymin'],s['ymax']),s['z']]))*1000 for s in ek['key_top_playable_surface']);refpt=np.array([ek['key_center'][0],.035,ek['key_top_playable_surface'][0]['z']])
 gates=dict(all_required_contacts=all(ct['contact_gate'] for ct in results),target_depth=dep<=.25,non_target_or_wrong_region_depth=wrong<=.25,self_surfaces=g['nonadjacent_self_triangle_pairs']==0,natural_family=err<.001,authorized_axes=axis<1e-5,authorized_domain=domain)
 out=dict(id=r['id'],display_time=r['display_time'],all_gates=all(gates.values()),gates=gates,contact_results=results,target_max_depth_mm=dep,non_target_or_wrong_region_max_mm=wrong,self_crossings=g['nonadjacent_self_triangle_pairs'],middle_ring_exact=gap,anatomy=an,wrist_world_m=list(<REDACTED_EMAIL>['WRIST_R'].head),next_pad_world_m=pad.tolist(),next_pad_distance_to_playable_surface_mm=float(dist),next_pad_distance_to_previous_reference_point_mm=float(np.linalg.norm(pad-refpt)*1000),key_angles=a.tolist(),root_control=z[:6].tolist(),latent=z.tolist(),state=r['state'],native_identity=identity,original_key_actions_match=True,Human_naturalness='PENDING',scope='ACTUAL_STATIC_ONLY',source_saved=False)
 (runpath.with_name(runpath.stem+'_actual.json')).write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()));print('ACTUAL',r['id'],gates,'target',dep,'wrong',wrong,'nextgap',dist,flush=True)
