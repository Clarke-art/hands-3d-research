import sys,json,ast,time,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands';sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
from triangle_distance import *
import blender_utils as u
RAW=D
tree=ast.parse((O/'extract_anatomy.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['unit','angle','matrix','coords','signed_rot','anatomy']],type_ignores=[]),'actual_bone_mapper','exec'))
ai=int(sys.argv[-1]);r=json.loads((O/f'ENDPOINT_SOLVE_{ai}.json').read_text());P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene']
bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);source=bpy.data.scenes[M['scene']];bpy.context.window.scene=source;u.settime(source,r['source_time']);angles=u.keyangles()
assert np.max(abs(angles-np.array(r['key_angles'])))<1e-6
expected=json.loads((O/'PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json').read_text())['original_action_payloads']
current={str(i):u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i,n in u.man['key_pivots'].items()};assert current==expected
keyerrs=[]
for k in KEYS:
 obs=[ob for ob in source.objects if ob.type=='MESH' and ob.get('FROZEN_KEY_INDEX')==k['key_index']]
 assert len(obs)==len(k['geometry'])
 for g in k['geometry']:
  ob=next(ob for ob in obs if g['name'] in ob.name);vv,_=u.coords(ob);keyerrs.append(float(np.max(abs(vv-keyworld(np.array(g['vertices']),k,angles[k['key_index']])))))
assert max(keyerrs)<1e-6
for ob in source.objects:ob['ENDPOINT_REF']=ob.name
bpy.ops.scene.new(type='FULL_COPY');sc=bpy.context.scene;sc.name=f'E5_NATURAL_ENDPOINT_{ai}_DESIGN_PROVISIONAL';cp={ob['ENDPOINT_REF']:ob for ob in sc.objects if 'ENDPOINT_REF' in ob}
for ob in list(source.objects)+list(sc.objects):
 if 'ENDPOINT_REF' in ob:del ob['ENDPOINT_REF']
for ob in sc.objects:
 if ob.animation_data:ob.animation_data_clear()
rig=cp[M['mapping']['R']['rig']];mesh=cp[M['mapping']['R']['mesh']];rt=cp[M['mapping']['R']['root']]
u.apply(np.array(r['state']),rt,rig);V,F=u.coords(mesh);assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
start=time.monotonic();m=detect(V,angles,dict(midi=76,finger=3));ct=m['contact'];an=anatomy(rig,mesh,f'E5_ENDPOINT_{ai}',state=r['state'])
aq=np.array(an['recovered_controls']);qref=(1-r['lambda_reference'])*np.array(r['reference_q_R1'])[1:]+r['lambda_reference']*np.array(r['reference_q_R2'])[1:]
if ai==2:qref[1,:3]=(1-r['active_flex_alpha'])*qref[1,:3]+r['active_flex_alpha']*np.array(r['active_flex_anchor'])
familyerror=float(np.max(abs(aq[1:]-qref)));axiserror=max(j['off_model_rotation_matrix_error'] for d in an['digits'] for j in d['joints'])
bounds=bool(np.all(np.array(r['x'])>=np.array(r['bounds_lower'])-1e-7) and np.all(np.array(r['x'])<=np.array(r['bounds_upper'])+1e-7))
gates=dict(actual_E5_pulp_contact=ct['top_surface_crossing_triangles']>0 and ct['true_pulp_surface_contact_distance_mm']<=.05 and ct['near_contact_projected_area_mm2']>0,pad_inside_E5=ct['pad_horizontal_outside_mm']<=1e-5,pad_height_aux=abs(ct['pad_gap_mm'])<=3,target_key_depth=m['target_key_max_depth_mm']<=.25,non_target_and_nonpulp_depth=m['wrong_key_or_nonpulp_max_depth_mm']<=.25,five_finger_surface_crossings_zero=m['nonadjacent_self_triangle_pairs']==0,approved_spread_and_mapped_coordinated_family=familyerror<=1e-4,authorized_axes_only=axiserror<=1e-5,authorized_control_domain=bounds)
mr=next(p for p in m['self_skin'] if p['digits']==['MIDDLE','RING']);exact=exact_clearance(V,TR,np.flatnonzero(LABEL==2),np.flatnonzero(LABEL==3),META['topological_vertex_neighbors'],mr['minimum_gap_sampled_mm']/1000+1e-10) if not mr['true_nonadjacent_triangle_pair_count'] else dict(distance_mm=0.,reason='actual crossing')
out=dict(attempt=ai,status='ENDPOINT_GATES_PASS' if all(gates.values()) else 'ENDPOINT_BLOCKED',authority='DESIGN_PROVISIONAL',gates=gates,actual_geometry=m,actual_anatomy=an,middle_ring_exact_clearance=exact,reference_family_error_deg=familyerror,off_axis_rotation_error=axiserror,original_key_action_identity=True,key_geometry_error_m=max(keyerrs),key_angle_error_rad=float(np.max(abs(angles-np.array(r['key_angles'])))),source_time=r['source_time'],state=r['state'],solver=r,scene=sc.name,rig=rig.name,mesh=mesh.name,root=rt.name,cameras={v:cp[n].name for v,n in M['cameras'].items()},Human_naturalness='PENDING',active_phase_reference='Provisional old-S2 hinge flexion with Human-reviewed spread correction' if ai==2 else 'Conservative approved whole passive family',actual_snapshot=str(O/f'ENDPOINT_{ai}_ACTUAL_SKIN.npz'),verification_seconds=time.monotonic()-start)
np.savez_compressed(O/f'ENDPOINT_{ai}_ACTUAL_SKIN.npz',vertices=V,key_angles=angles)
(O/f'ENDPOINT_ACTUAL_{ai}.json').write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')
# Isolated diagnostics may retain a failed endpoint for evidence, no source save.
for a in list(bpy.data.actions):bpy.data.actions.remove(a,do_unlink=True)
for other in list(bpy.data.scenes):
 if other!=sc:bpy.data.scenes.remove(other)
sc.frame_start=sc.frame_current;sc.frame_end=sc.frame_current;bpy.context.preferences.filepaths.save_version=0
dest=O/f'E5_ENDPOINT_{ai}_DIAGNOSTIC.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print('ENDPOINT_ACTUAL',ai,out['status'],gates,'gap',ct['true_pulp_surface_contact_distance_mm'],'signed',ct['true_pulp_min_signed_gap_mm'],'depth',m['target_key_max_depth_mm'],'wrong',m['wrong_key_or_nonpulp_max_depth_mm'],'self',m['nonadjacent_self_triangle_pairs'],'MR',exact,flush=True)

