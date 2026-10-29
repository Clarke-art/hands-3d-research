from common import *
import re,math
names=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','CURRENT_JOINT_QUALIFICATION_SEMANTICS_AFTER_PALMAR_R1.json','FORMAL_JOINT_HELPER_INVENTORY_R1.json','JOINT_SURFACE_REQUALIFICATION_AFTER_PALMAR_R1.json','MIDDLE_MCP_R_SURFACE_RELATION_REVALIDATION_R1.json','JOINT_SURFACE_DELTA_RANKING_AFTER_PALMAR_R1.json','REST_RIG_PAYLOAD_AFTER_PALMAR_R1.json','ZERO_POSE_REVALIDATION_AFTER_PALMAR_R1.json','BIND_ZERO_GEOMETRY_REVALIDATION_AFTER_PALMAR_R1.json','PALMAR_ROOT_BIND_ZERO_VISUAL_R1.json','DORSAL54_BIND_ZERO_REGRESSION_R1.json','MODIFIER_BIND_CONTRACT_AFTER_PALMAR_R1.json','WEIGHT_HASH_READONLY_AFTER_PALMAR_R1.json','CURRENT9_HOLD_AND_OVERLAP_RECHECK_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','review.html']
assert all((OUT/n).is_file() for n in names)
status=read(OUT/(PHASE+'_STATUS.json'));assert status['VERDICT']=='PASS_JOINT_REST_ZERO_BIND_REQUALIFIED' and status['STOP'] and not status['NEXT_EXECUTED']
J=read(OUT/'JOINT_SURFACE_REQUALIFICATION_AFTER_PALMAR_R1.json');I=read(OUT/'FORMAL_JOINT_HELPER_INVENTORY_R1.json');B=read(OUT/'BIND_ZERO_GEOMETRY_REVALIDATION_AFTER_PALMAR_R1.json');D=read(OUT/'CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json');sem=read(OUT/'CURRENT_JOINT_QUALIFICATION_SEMANTICS_AFTER_PALMAR_R1.json')
assert len(J['all21_current_rows'])==len(I['rows'])==sem['formal_joint_count']==21
assert all(r['final_status']=='PASS' for r in J['all21_current_rows'].values())
assert len(B['all3416_delta_mm'])==3416 and max(B['all3416_delta_mm'])<=sem['zero_bind']['bind_gate_mm'] and B['RAW_TO_BIND_OUT_OF_TOLERANCE_COUNT']==0
assert D['CORRECTED']['coordinates_local_m']==D['R2']['coordinates_local_m']==D['STAGE4']['coordinates_local_m']
assert D['CORRECTED']['coordinates_world_m']==D['R2']['coordinates_world_m']==D['STAGE4']['coordinates_world_m']
assert next(iter(D['CORRECTED']['protected']['rigs'].values()))['bones']==next(iter(D['R2']['protected']['rigs'].values()))['bones']
assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
canonical=S5/'human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend'
assert sha(canonical)=='5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe'
dump('CURRENT_CORRECTED_RIG_AUTHORITY_HASH_VERIFICATION_R1.json',{'status':'PASS','canonical_corrected_rig_authority':ref(canonical),'both_new_derivatives_full_rest_payload_matches_each_propagation_source':True,'existing_prior_lineage_preflight':ref(PROP/'PALMAR_STAGE5_INPUT_PAYLOAD_PREFLIGHT_R1.json'),'rebuild_or_refit':False})
for key,r in sem['sources'].items():assert sha(r['path'])==r['sha256'],key
for r in read(OUT/'READONLY_FUNCTION_REUSE_AUDIT_R1.json')['reuse']:assert sha(r['source']['path'])==r['source']['sha256']
for manifest,field,count in [('PALMAR_BIND_ZERO_MATCHED_RENDER_MANIFEST_R1.json','records',18),('DORSAL_BIND_ZERO_MATCHED_RENDER_MANIFEST_R1.json','renders',9)]:
 rows=read(OUT/manifest)[field];assert len(rows)==count
 groups={}
 for r in rows:
  assert (OUT/r['path']).is_file()
  key=(r['view'],r['style'] if field=='records' else r['shade']);groups.setdefault(key,[]).append(r)
 for key,rr in groups.items():
  assert len(rr)==3
  keys=['camera_matrix','orthographic_width_m','resolution','studio_rotation_z'] if field=='records' else ['target_world_m','direction','orthographic_scale_m','resolution','engine']
  assert all(all(r[k]==rr[0][k] for k in keys) for r in rr),key
 assert read(OUT/manifest).get('native_asset_saves',read(OUT/manifest).get('production_blend_saves',0))==0
assert not list(OUT.glob('*.blend*'))
for attribute,target in re.findall(r'(href|src)="([^"]+)"',(OUT/'review.html').read_text(encoding='utf-8')):
 if not target.startswith(('http','data:','#')):assert (OUT/target).is_file(),target
protected=read(OUT/'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json');assert protected['PROTECTED_HISTORY_DRIFT']==0 and not protected['changed_paths'] and not protected['added_paths_outside_phase'] and not protected['removed_paths']
report=(OUT/(PHASE+'_REPORT.md')).read_text(encoding='utf-8');assert all(k in report for k in status)
assert status['CURRENT9_HUMAN_RESPONSE']=='HOLD_NOT_CLOSED' and all(status[k]==0 for k in ('CURRENT9_DIRECT_OVERLAP','CURRENT9_1RING_OVERLAP','CURRENT9_2RING_OVERLAP'))
assert status['MID_MCP_45_MANDATORY_REVALIDATION']==status['WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED']=='YES'
dump('DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_artifact_count':len(names),'required_artifacts':{n:ref(OUT/n) for n in names},'all21_records_complete':True,'full3416_gate_rechecked':True,'matched_render_camera_lighting_scale_rows':9,'fresh_render_count':27,'all_local_review_links_resolve':True,'zero_blend_outputs':True,'formal_authority_source_hashes_reverified':True,'NEXT_EXECUTED':False,'STOP':True})
dump('OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json'})
print('DELIVERY PASS required17 artifacts /27 renders /21 joints /3416 bind vertices /STOP')
