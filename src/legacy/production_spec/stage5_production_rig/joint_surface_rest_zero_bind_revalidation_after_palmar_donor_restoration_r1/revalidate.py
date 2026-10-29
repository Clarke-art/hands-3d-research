import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from payload import *
from mathutils import Vector,Quaternion,Matrix
sem=read(OUT/'CURRENT_JOINT_QUALIFICATION_SEMANTICS_R1.json')
ns={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':1000.0}
reused=[reuse(S5/'stage5a_r2/scripts/stage5a_r2_audit.py',['closest','parity'],ns),reuse(ROOT/'production_spec/stage6_deformation/stage6a/scripts/s6a_common.py',['reset_pose','evaluate'],ns)]
data={};rolls={}
for k,p in FILES.items():
 assert sha(p)==EXPECTED[k]
 load(p);data[k]=snapshot();rolls[k]=read_rolls_last()
 print('CLEAN READ',k,flush=True)
dump('CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json',data)
prop4=read(PROP/'FROZEN_INPUT_NATIVE_PAYLOADS_R1.json')
prior={k:read(PROP/(k+'_REOPENED_NATIVE_PAYLOAD_R1.json')) for k in ('CORRECTED','R2')}
checks={k:data[k]==prior[k] for k in prior}
checks['STAGE4']=all(data[k]['coordinates_local_m']==data['STAGE4']['coordinates_local_m'] for k in prior)
checks['old_inputs_actual']=all(data[k]['coordinates_local_m']==prop4['CORRECTED' if k=='OLD_CORRECTED' else 'R2']['coordinates_local_m'] for k in ('OLD_CORRECTED','OLD_R2'))
assert all(checks.values()),checks
rest={}
for k,old in [('CORRECTED','OLD_CORRECTED'),('R2','OLD_R2')]:
 a=data[k]['protected']['rigs'];b=data[old]['protected']['rigs']
 assert a==b and rolls[k]==rolls[old]
 rest[k]={'REST_RIG_PAYLOAD_MATCH':'PASS','source':ref(FILES[old]),'current':ref(FILES[k]),'bone_count':21,'BONE_PAYLOAD_DELTA':0,'JOINT_HEAD_DELTA_MM':0.0,'JOINT_TAIL_DELTA_MM':0.0,'ROLL_DELTA':0.0,'REST_MATRIX_DELTA':0,
 'source_rig_payload_sha256':digest(b),'current_rig_payload_sha256':digest(a),'native_explicit_rolls_source':rolls[old],'native_explicit_rolls_current':rolls[k],
 'all_names_order_hierarchy_connect_deform_inherit_local_frames_transforms_constraints_and_original_metadata_exact':True}
assert next(iter(data['CORRECTED']['protected']['rigs'].values()))['bones']==next(iter(data['R2']['protected']['rigs'].values()))['bones']
dump('REST_RIG_PAYLOAD_REVALIDATION_R1.json',{'status':'PASS','paths':rest,'corrected_thumb_chain_preserved':True,'clean_reopen_matches_prior_saved_native_snapshots':checks,'serialization_drift':0,'blend_saves_this_phase':0,'native_roll_read':'last step in unsaved read session; no EditBone setter / recalculation / mode exit / save'})
weights={k:digest(data[k]['positive_weight_vectors']) for k in ('OLD_R2','R2')}
assert all(h==WEIGHT_HASH for h in weights.values())
assert data['OLD_R2']['protected']['weights_exact_including_zero']==data['R2']['protected']['weights_exact_including_zero']
dump('WEIGHT_HASH_READONLY_REVERIFICATION_R1.json',{'status':'PASS','vector_count':3416,'actual_hashes':weights,'authority':WEIGHT_HASH,'all_weight_scalars_including_zero_entries_exact':True,'weight_scalar_delta':0,'static_skin_continuity_qualification_run':False})
bindkeys=('groups','weights_exact_including_zero')
binding={k:data['R2']['protected'][k]==data['OLD_R2']['protected'][k] for k in bindkeys}
for f in ('modifiers','settings','matrices'):
 binding['mesh_object_'+f]=data['R2']['protected']['object'][f]==data['OLD_R2']['protected']['object'][f]
binding['full_rig_object_rest_and_bind_space']=data['R2']['protected']['rigs']==data['OLD_R2']['protected']['rigs']
assert all(binding.values())
dump('MODIFIER_BIND_CONTRACT_REVALIDATION_R1.json',{'status':'PASS','checks':binding,'modifier_stack_settings':data['R2']['protected']['object']['modifiers'],'mesh_object_matrices':data['R2']['protected']['object']['matrices'],'group_order':data['R2']['protected']['groups'],'bone_group_mapping':[g[1] for g in data['R2']['protected']['groups']],
 'actual_asset_independent_bind_matrix':'None stored by Blender Armature modifier; object-to-armature spaces and each bone rest inverse are evaluated by Blender. Actual matrix_parent_inverse is recorded separately as object data. No invented inverse bind property.','modifier_ON_zero_only':True,'reparent_rebind_transform_apply_inverse_bind_recalculation':False})

def query_setup(key):
 load(FILES[key]);source=bpy.data.objects[data[key]['object_name']]
 # Geometry-only query copy isolates raw surface from Armature evaluation.
 # Native mesh data copied without coordinate/topology setters; no authoritative edit/save.
 query=bpy.data.objects.new('READ_ONLY_RAW_SURFACE_QUERY',source.data.copy());query.matrix_world=source.matrix_world.copy();bpy.context.scene.collection.objects.link(query)
 ns.update(MOB=query,MW=query.matrix_world.copy(),MINV=query.matrix_world.inverted(),M3=query.matrix_world.to_3x3())
 return query
def surface(q,ob,need_parity):
 p=Vector(q);loc,norm,fi=ns['closest'](p)
 assert loc is not None
 dist=(p-loc).length*1000;signed=(p-loc).dot(norm)*1000
 f=ob.data.polygons[fi]
 features={'native_polygon':fi,'native_vertices':list(f.vertices),'native_edges':[ob.data.loops[i].edge_index for i in range(f.loop_start,f.loop_start+f.loop_total)],'feature_kind':'closest point on native polygon surface','nearest_point_world_m':list(loc),'normal_world':list(norm)}
 votes,total=ns['parity'](p) if need_parity else (None,None)
 return {'surface_distance_mm':dist,'normal_signed_distance_mm':signed,'inside_ray_parity':None if not need_parity else votes>total/2,'ray_parity_votes':votes,'ray_parity_direction_count':total,'parity_signed_distance_mm':(-dist if votes>total/2 else dist) if need_parity else None,'nearest_native_feature':features}
def region(rule,p,s,ob):
 r=rule['region'];kind=r['type'];p=Vector(p)
 if kind=='FROZEN_T01_AXIAL_ZONE':
  a=Vector(r['anchor_world_m']);ax=(Vector(r['tip_frame_world_m'])-a).normalized();measured=(p-a).dot(ax)*1000;delta=measured-r['center_mm'];passed=abs(delta)<=r['half_width_mm']
  return {'status':'PASS' if passed else 'FAIL','type':kind,'measured_axial_mm':measured,'approved_axial_mm':r['center_mm'],'delta_from_approved_mm':delta,'half_width_mm':r['half_width_mm'],'qualification_margin_mm':r['half_width_mm']-abs(delta),'frozen_axis_world':list(ax),'joint_locator_run':False}
 if kind=='FROZEN_CMC_LOCALITY_SPHERE':
  anchor=<REDACTED_EMAIL>[r['anchor_native_vertex']].co;dist=(p-anchor).length*1000
  return {'status':'PASS' if dist<=r['radius_mm'] else 'FAIL','type':kind,'anchor_native_vertex':r['anchor_native_vertex'],'distance_to_frozen_cage_anchor_mm':dist,'approved_radius_mm':r['radius_mm'],'qualification_margin_mm':r['radius_mm']-dist,'current_surface_clearance_mm':s['surface_distance_mm'],'new_deep_clearance_gate':False}
 if kind=='FROZEN_WRIST_PALM_TRANSITION':
  measured=r['approved_s_mm']+(p-Vector(r['approved_world_m'])).dot(Vector(r['e_long']))*1000;lo,hi=r['s_band_mm'];passed=lo<=measured<=hi
  return {'status':'PASS' if passed else 'FAIL','type':kind,'fixed_region_axial_mm':measured,'frozen_transition_band_mm':[lo,hi],'qualification_margin_mm':min(measured-lo,hi-measured),'transition_locator_run':False}
 if kind=='CORRECTED_NATIVE_TERMINAL_SURFACE_LANDMARK':
  terminal=<REDACTED_EMAIL>[r['terminal_native_vertex']].co;delta=(p-terminal).length*1000
  domain=read(S5/'cap_derived_thumb_kinematic_authority_revalidation_r1/GEOMETRIC_EVIDENCE_COMPUTATION.json')['native_domain_vertex_ids']
  cap=read(S5/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json')['vertex_ids']
  owner=r['terminal_native_vertex'] in domain and r['terminal_native_vertex'] in cap
  passed=delta==0 and s['surface_distance_mm']<=r['surface_max_mm'] and owner
  return {'status':'PASS' if passed else 'FAIL','type':kind,'terminal_native_vertex':r['terminal_native_vertex'],'terminal_landmark_delta_mm':delta,'own_digit_identity':'THUMB' if owner else 'UNRESOLVED','surface_max_mm':r['surface_max_mm'],'surface_margin_mm':r['surface_max_mm']-s['surface_distance_mm'],'apex_rule':'Corrected native terminal; superseded cap REP/apex hard thresholds not used','cap37_membership_only':True}
 apex=<REDACTED_EMAIL>[r['frozen_apex_native_vertex']].co;da=(p-apex).length*1000
 owner=s['nearest_native_feature']['native_polygon']==r['frozen_accepted_native_surface_face']
 passed=s['surface_distance_mm']<=r['surface_max_mm'] and da<=r['apex_max_mm'] and owner
 return {'status':'PASS' if passed else 'FAIL','type':kind,'frozen_apex_native_vertex':r['frozen_apex_native_vertex'],'apex_distance_mm':da,'surface_max_mm':r['surface_max_mm'],'apex_max_mm':r['apex_max_mm'],'surface_margin_mm':r['surface_max_mm']-s['surface_distance_mm'],'apex_margin_mm':r['apex_max_mm']-da,'digit_identity':r['frozen_digit_identity'] if owner else 'MISMATCH','nearest_face_matches_frozen_accepted_own_digit_face':owner,'new_cap_geodesic_apex_or_ownership_selection_run':False}
measurements={};endpoints={}
for key in ('OLD_CORRECTED','CORRECTED','R2'):
 ob=query_setup(key);bones=next(iter(data[key]['protected']['rigs'].values()))['bones'];rows={};ep=[]
 for name,rule in sem['rules'].items():
  p=bones[name]['head_world_m'];s=surface(p,ob,rule['inside_required']);r=region(rule,p,s,ob)
  passed=r['status']=='PASS' and (not rule['inside_required'] or s['inside_ray_parity'])
  rows[name]={'name':name,'fixed_world_position_m':p,'authority':rule,'surface':s,'region':r,'final_status':'PASS' if passed else 'FAIL'}
  for endpoint in ('head','tail'):
   sp=surface(bones[name][endpoint+'_world_m'],ob,False)
   ep.append({'bone':name,'endpoint':endpoint,'fixed_world_m':bones[name][endpoint+'_world_m'],**sp})
 measurements[key]=rows;endpoints[key]=ep
 print('ALL JOINTS MEASURED',key,'PASS',sum(r['final_status']=='PASS' for r in rows.values()),flush=True)
current=measurements['CORRECTED'];old=measurements['OLD_CORRECTED']
for name,row in current.items():
 row['old_geometry']=old[name]['surface'];row['old_region']=old[name]['region'];row['new_geometry']=row['surface']
 row['distance_delta_mm']=row['surface']['surface_distance_mm']-old[name]['surface']['surface_distance_mm']
 row['R2_geometry_rig_same_joint_crosscheck']=measurements['R2'][name]['fixed_world_position_m']==row['fixed_world_position_m'] and measurements['R2'][name]['surface']==row['surface'] and measurements['R2'][name]['region']==row['region']
 assert row['R2_geometry_rig_same_joint_crosscheck']
deformfail=[n for n,r in current.items() if r['authority']['inside_required'] and not r['surface']['inside_ray_parity']]
tipfail=[n for n,r in current.items() if not r['authority']['inside_required'] and r['final_status']!='PASS']
regionfail=[n for n,r in current.items() if r['region']['status']!='PASS']
summary={'FORMAL_JOINT_COUNT':21,'FORMAL_JOINTS_PASS':sum(r['final_status']=='PASS' for r in current.values()),'DEFORM_JOINT_INSIDE_FAILURE_COUNT':len(deformfail),'TIP_HELPER_FAILURE_COUNT':len(tipfail),'JOINT_REGION_FAILURE_COUNT':len(regionfail),'deform_inside_failures':deformfail,'TIP_failures':tipfail,'region_failures':regionfail}
jointpass=not deformfail and not tipfail and not regionfail
dump('JOINT_SURFACE_REQUALIFICATION_R1.json',{'status':'PASS' if jointpass else 'FAIL_CLOSED_JOINT_SURFACE_REVALIDATION','summary':summary,'all21_current_rows':current,'independently_remeasured_R2_crosscheck':measurements['R2'],'old21_measured_against_actual_corrected_source_geometry':old,'R2_parity_closest_functions_reuse':reused[0],'bone_tail_inside_not_a_joint_gate':True})
rank=[]
for a,b in zip(endpoints['OLD_CORRECTED'],endpoints['CORRECTED']):
 assert a['bone']==b['bone'] and a['endpoint']==b['endpoint'] and a['fixed_world_m']==b['fixed_world_m']
 rank.append({'bone':b['bone'],'endpoint':b['endpoint'],'old_geometry_distance_mm':a['surface_distance_mm'],'new_geometry_distance_mm':b['surface_distance_mm'],'delta_mm':b['surface_distance_mm']-a['surface_distance_mm'],'old_nearest_native_feature':a['nearest_native_feature'],'new_nearest_native_feature':b['nearest_native_feature']})
rank.sort(key=lambda r:abs(r['delta_mm']),reverse=True)
heads=sorted([{'name':n,'old_distance_mm':r['old_geometry']['surface_distance_mm'],'new_distance_mm':r['surface']['surface_distance_mm'],'delta_mm':r['distance_delta_mm']} for n,r in current.items()],key=lambda r:abs(r['delta_mm']),reverse=True)
prior_diag=[]
prior_diag.sort(key=lambda r:abs(r['delta_mm']),reverse=True)
dump('JOINT_SURFACE_DELTA_RANKING_R1.json',{'all21_joint_head_ranking':heads,'all42_fixed_head_tail_ranking':rank,'MAX_JOINT_SURFACE_DISTANCE_DELTA_MM':abs(heads[0]['delta_mm']),'MAX_JOINT_SURFACE_DISTANCE_DELTA_JOINT':heads[0]['name'],'RING_MCP_SURFACE_DELTA_MM':current['RING_MCP_R']['distance_delta_mm'],'prior_phase_diagnostic_top_head_tail':prior_diag[:5],'prior_phase_method':'native-index fan surface; current formal measurement uses actual Blender polygon closest/tessellation. Each method old/new paired without mixing','ROI_nearby_required_focus':{n:current[n] for n in ['RING_MCP_R','MIDDLE_MCP_R','LITTLE_MCP_R','INDEX_MCP_R','WRIST_R']}})
if not jointpass:
 dump('PHASE_MACHINE_RESULT_R1.json',{'VERDICT':'FAIL_CLOSED_JOINT_SURFACE_REVALIDATION','STOP':True,'zero_bind_not_run_due_joint_failure':True});raise SystemExit('FAIL CLOSED: joint qualification; no repair')

# Fresh actual R2 clean reopen; only the formally recovered zero reset runs in memory.
load(FILES['R2']);assert snapshot()==data['R2']
ob=bpy.data.objects[data['R2']['object_name']];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];MW=ob.matrix_world.copy()
assert len(ob.modifiers)==1 and ob.modifiers[0].type=='ARMATURE' and ob.modifiers[0].object==rig and ob.modifiers[0].show_viewport
ns['reset_pose'](rig);bpy.context.view_layer.update()
nan=sum(not math.isfinite(float(v)) for b in rig.pose.bones for row in b.matrix for v in row)
pose_residue=[];states={}
for b in rig.pose.bones:
 st={'mode':b.rotation_mode,'location':list(b.location),'quaternion':list(b.rotation_quaternion),'scale':list(b.scale),'matrix_basis':[list(r) for r in b.matrix_basis],'pose_matrix':[list(r) for r in b.matrix],'rest_matrix':[list(r) for r in b.bone.matrix_local]}
 st['pose_rest_matrix_max_entry_delta']=max(abs(b.matrix[i][j]-b.bone.matrix_local[i][j]) for i in range(4) for j in range(4))
 st['matrix_basis_identity_exact']=b.matrix_basis==Matrix.Identity(4)
 okay=b.rotation_mode=='QUATERNION' and tuple(b.location)==(0,0,0) and tuple(b.scale)==(1,1,1) and abs(b.rotation_quaternion.angle)<1e-7 and st['matrix_basis_identity_exact']
 if not okay:pose_residue.append(b.name)
 states[b.name]=st
groups={g.index:g.name for g in ob.vertex_groups};deform={b.name for b in rig.data.bones if b.use_deform}
missing_bones=sorted(set(sem['rules'])-set(rig.pose.bones.keys()));missing_groups=sorted(deform-set(groups.values()));missing_refs=[m.name for m in ob.modifiers if m.type=='ARMATURE' and m.object is None]
bad_weights=[v.index for v in ob.data.vertices for g in v.groups if g.group not in groups or not math.isfinite(g.weight)]
passedzero=not(nan or pose_residue or missing_bones or missing_groups or missing_refs or bad_weights)
dump('ZERO_POSE_REVALIDATION_R1.json',{'ZERO_POSE':'PASS' if passedzero else 'FAIL','recovered_reset_procedure':reused[1],'all21_channel_states':states,'NaN_Inf_count':nan,'bone_missing_count':len(missing_bones),'group_missing_count':len(missing_groups),'modifier_reference_missing_count':len(missing_refs),'pose_residue_count':len(pose_residue),'matrix_basis_identity_exact':all(s['matrix_basis_identity_exact'] for s in states.values()),'pose_rest_matrix_residue_max_entry':max(s['pose_rest_matrix_max_entry_delta'] for s in states.values()),'matrix_residue_role':'Blender recomposes zero hierarchy in float32; no new entry-wise matrix threshold; formal channel zero plus existing raw-bind geometry tolerance governs','temporary_only_no_save':True,'poses_run':['ZERO_ONLY']})
vb,faces=ns['evaluate'](ob,MW);vraw=[(<REDACTED_EMAIL>).copy() for v in ob.data.vertices]
assert len(vb)==len(vraw)==3416 and [list(f) for f in faces]==[f[1] for f in data['R2']['protected']['mesh']['faces']]
d=[(a-b).length*1000 for a,b in zip(vb,vraw)];finite=all(math.isfinite(float(z)) for v in vb for z in v)
tol=sem['zero_bind']['bind_gate_mm'];outside=[i for i,v in enumerate(d) if v>tol]
bindpass=passedzero and finite and not outside
bind={'BIND_ZERO':'PASS' if bindpass else 'FAIL','compared_native_point_count':3416,'RAW_TO_BIND_MAX_DELTA_MM':max(d),'RAW_TO_BIND_MEAN_DELTA_MM':sum(d)/len(d),'RAW_TO_BIND_RMS_DELTA_MM':math.sqrt(sum(z*z for z in d)/len(d)),'OUTSIDE_EXPECTED_NUMERICAL_RESIDUE_COUNT':len(outside),'outside_native_vertex_ids':outside,'recovered_existing_tolerance_mm':tol,'comparator':'<=','semantics_source':sem['sources']['current_R2_zero_consumer'],'all3416_delta_mm':d,'evaluated_coordinates_finite':finite,'native_face_cycles_unchanged':True,'armature_modifier_ON':True,'pose':'ZERO','new_tolerance_count':0,'no_saved_bind_copy_created':True}
dump('BIND_ZERO_GEOMETRY_REVALIDATION_R1.json',bind)
visual={'frame':read(APP/'PALMAR_APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json')['frame'],'camera':read(APP/'PALMAR_APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json')['camera'],
 'stages':{'STAGE4_RAW':{'world_m':data['STAGE4']['coordinates_world_m']},'R2_RAW':{'world_m':data['R2']['coordinates_world_m']},'R2_BIND_ZERO':{'world_m':[list(v) for v in vb]}},
 'faces':[f[1] for f in data['R2']['protected']['mesh']['faces']],'smooth':data['R2']['protected']['mesh']['smooth_flags'],
 'bones':next(iter(data['R2']['protected']['rigs'].values()))['bones'],'changed_ids':read(PROP/'PALMAR_STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json')['actual_changed_ids'],'rank_heads':heads,'rank_endpoints':rank}
dump('MATCHED_ZERO_BIND_REVIEW_GEOMETRY_R1.json',visual)
dump('PHASE_MACHINE_RESULT_R1.json',{'VERDICT':'MACHINE_JOINT_REST_ZERO_BIND_PASS_PENDING_VISUAL_EVIDENCE' if bindpass else 'FAIL_CLOSED_ZERO_BIND_REVALIDATION','summary':summary,'REST_RIG_PAYLOAD_MATCH':'PASS','ZERO_POSE':'PASS' if passedzero else 'FAIL','BIND_ZERO':bind['BIND_ZERO'],'STOP':not bindpass,'Stage6_poses_run':[],'authority_edits':0,'blend_files_saved':0})
dump('READONLY_FUNCTION_REUSE_AUDIT_R1.json',{'reuse':reused,'audit_build_solver_top_level_code_executed':False,'functions_loaded_only':['closest','parity','reset_pose','evaluate'],'poses_run':['ZERO_ONLY']})
assert bindpass,'FAIL_CLOSED_ZERO_BIND_REVALIDATION'
print('MACHINE PASS joint21 / rest0 / zero / bind max mm',max(d),flush=True)
