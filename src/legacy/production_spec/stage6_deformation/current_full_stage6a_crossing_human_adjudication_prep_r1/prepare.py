from common import *
dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
manifest=read(FRESH/'OUTPUT_ARTIFACT_HASH_MANIFEST.json');files=['FULL_STAGE6A_REQUALIFICATION_AFTER_DONOR_TRANSFER_R1_STATUS.json','FULL_STAGE6A_POST_DONOR_EXACT_CROSSING_AUDIT_R1.json','OLD_9_BLOCKER_FRESH_REMEASUREMENT_R1.json','POSED_COORDINATES_R1.json','FULL_STAGE6A_MACHINE_EVIDENCE_R1.json','EVIDENCE_RENDER_MANIFEST_R1.json']
checks={n:sha(FRESH/n)==manifest[n] for n in files}
status=read(FRESH/files[0]);audit=read(FRESH/files[1]);old9=read(FRESH/files[2]);coords=read(FRESH/files[3])
checks['current_production_asset_hash']=sha(CAND)==EXPECTED_CAND
checks['corrected_rig_hash']=sha(CORRECTED)==EXPECTED_RIG
checks['current_status_active9']=status['MACHINE_HARD_BLOCKER_COUNT']==9 and status['MACHINE_HARD_BLOCKER_CASE_COUNT']==3 and set(status['FAILING_CASES'])=={'IDX_MCP_15','IDX_MCP_30','TH_IP_15'} and status['FULL_STAGE6A_REQUALIFICATION_AFTER_DONOR_TRANSFER_R1']=='FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION'
checks['weight_authority']=status['weight_vector_sha256']==EXPECTED_WEIGHTS
checks['prior_Human_state_not_closed']=status['DORSAL_MCP_HUMAN_VISUAL_STATUS']=='PENDING_HUMAN_REVIEW'
spec=[('A1','IDX_MCP_15',[377,1054],4.291852237657,3.656398753641,.571132346947),('B1','IDX_MCP_30',[1036,2732],3.643731877673,3.499050362724,.622803602530),('B2','IDX_MCP_30',[1226,2742],4.881278495304,4.166144603819,.225100612494),('C1','TH_IP_15',[77,408],5.135486775544,4.234161501363,.160551215443),('C2','TH_IP_15',[376,1050],4.038801154820,3.764636363676,.390457303385),('C3','TH_IP_15',[377,1048],4.875181417447,4.015601435462,.491366744538),('C4','TH_IP_15',[405,1946],3.677946180687,3.526704228757,1.224818773652),('C5','TH_IP_15',[407,1944],3.229683377867,3.078656727932,1.602101430834),('C6','TH_IP_15',[1944,2743],3.229683377867,3.178365369576,.208966459371)]
rows=[]
for key,cid,pair,poke,facet,segment in spec:
 a=next((r for r in audit['rows'] if r['case_id']==cid and r['face_ids']==pair and r['formal_hard_blocker']),None)
 b=next((r for r in old9['rows'] if r['case_id']==cid and r['face_ids']==pair),None)
 ok=a is not None and b is not None and a['class']=='CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION' and a['intersect'] and not a['human_approved'] and b['current_severe_blocker']
 if ok:
  ok=all(a[k]==b['current_fresh_evidence'][k] for k in ['depth_mm','local_edge_mm','seg_mm','pts']) and all(format(a[k],'.12f')==format(v,'.12f') for k,v in [('depth_mm',poke),('local_edge_mm',facet),('seg_mm',segment)])
 checks[key+'_current_identity_values_classification']=ok
 if not ok:continue
 vids=sorted({v for fi in pair for v in coords['faces'][fi]})
 checks[key+'_coordinates_match_saved_current']=all(b['current_face_coordinates_world_m'][str(fi)]==[coords['positions_world_m'][cid][v] for v in coords['faces'][fi]] for fi in pair)
 rows.append({'pair_id':key,'case_id':cid,'face_ids':pair,'vertex_ids':vids,'current_coordinates_world_m':{str(v):coords['positions_world_m'][cid][v] for v in vids},'current_metrics':{k:a[k] for k in ['intersect','depth_mm','local_edge_mm','seg_mm','pts','class']},'classification':a['classification'],'formal_hard_blocker':a['formal_hard_blocker'],'current_human_answer':None,'pre_donor_comparison':{'role':'PRE_DONOR_COMPARATOR_ONLY','old_evidence':b['old_evidence'],'current_identity_status':b['current_identity_status'],'severity_trend':b['severity_trend'],'delta':b['old_to_new_severity_delta']},'cause_candidates':['pose contact','skin','geometry'],'cause_diagnosis_performed':False,'current_authority_row_key':[cid,pair]})
checks['nine_exact_rows']=len(rows)==9
refs={n:ref(FRESH/n) for n in files};refs['production_asset']=ref(CAND);refs['corrected_rig']=ref(CORRECTED)
hashes={'current_full42_status_hash':sha(FRESH/files[0]),'current_crossing_audit_hash':sha(FRESH/files[1]),'old9_fresh_remeasurement_hash':sha(FRESH/files[2]),'production_asset_hash':EXPECTED_CAND,'posed_coordinate_payload_hash':sha(FRESH/files[3])}
dump('CURRENT_FULL_STAGE6A_HUMAN_REVIEW_INPUT_HASHES_R1.json',{'checks':checks,'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED_HUMAN_REVIEW_PACKAGE_INPUT_MISMATCH','input_hashes':hashes,'sources':refs,'current_active_authority_only':True,'historical_report_current_authority':False})
if not all(checks.values()):
 dump(PHASE+'_STATUS.json',{'VERDICT':'FAIL_CLOSED_HUMAN_REVIEW_PACKAGE_INPUT_MISMATCH','failed_inputs':[k for k,v in checks.items() if not v],'STOP':True,'FULL42_RERUN':0,'POSE_APPLICATIONS':0});raise SystemExit('FAIL CLOSED: current authority input mismatch')
dump('LOCKED_CURRENT9_ROWS_R1.json',{'rows':rows,'case_ids':['IDX_MCP_15','IDX_MCP_30','TH_IP_15'],'input_hashes':hashes,'current_metrics_remeasured':False})
print('CURRENT9 AUTHORITY BINDING PASS;3 cases9 pairs; no pose/metric/classifier execution',flush=True)
