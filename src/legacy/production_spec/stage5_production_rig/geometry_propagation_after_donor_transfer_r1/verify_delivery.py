from common import *
status=read(OUT/(PHASE+'_STATUS.json'))
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','STAGE5_CURRENT_LINEAGE_INPUT_RECOVERY_R1.json','STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json','STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json','STAGE5_RIG_PAYLOAD_EQUIVALENCE_R1.json','STAGE5_WEIGHT_PAYLOAD_EQUIVALENCE_R1.json','STAGE5_AUTHORITY_ID_MEMBERSHIP_AUDIT_R1.json','STAGE5_ZERO_EVAL_SMOKE_R1.json','STAGE5_SAVE_REOPEN_AUDIT_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','JOINT_SURFACE_DELTA_DIAGNOSTIC_R1.json']+[p.name for p in ASSETS.values()]
assert all((OUT/n).is_file() for n in required)
jsons=list(OUT.glob('*.json'))
for p in jsons:read(p)
for k,p in inputs().items():assert sha(p)==EXPECTED[k]
for k,p in ASSETS.items():assert sha(p)==read(OUT/'STAGE5_BEFORE_SAVE_PROPAGATION_PAYLOADS_R1.json')[k]['asset']['sha256']
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory()
assert before==after,'FAIL_CLOSED_STAGE5_GEOMETRY_PROPAGATION: final protected history drift'
assert status['STAGE5_GEOMETRY_PROPAGATION_VERDICT']=='PASS_GEOMETRY_PROPAGATED_WITH_RIG_AND_WEIGHTS_FROZEN'
assert status['STOP'] and not status['NEXT_EXECUTED'] and status['PRODUCTION_PROMOTION']=='NO'
rig=read(OUT/'STAGE5_RIG_PAYLOAD_EQUIVALENCE_R1.json');w=read(OUT/'STAGE5_WEIGHT_PAYLOAD_EQUIVALENCE_R1.json')
for k in ASSETS:
 assert rig['paths'][k]['source_rig_payload_sha256']==rig['paths'][k]['derived_rig_payload_sha256']
 assert w['paths'][k]['source_exact_weight_payload_sha256']==w['paths'][k]['derived_exact_weight_payload_sha256']
assert w['paths']['R2']['positive_weight_vector_sha256']==WEIGHT_HASH
dump('FINAL_DELIVERY_VALIDATION_R1.json',{'status':'PASS','required_files_present':required,'valid_json_file_count':len(jsons),'existing_file_count':len(before),'changed_removed_or_added_paths_outside_new_phase':0,'actual_source_and_derived_hashes_verified':True,'STOP_and_NEXT_record_only_verified':True})
manifest={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST.json'}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST.json',{'method':'SHA256 of all delivery files except this manifest','files':manifest})
print(json.dumps({'final_delivery':'PASS','protected_files':len(before),'delivery_files':len(manifest),'R2_weight_hash':WEIGHT_HASH,'asset_hashes':{k:sha(p) for k,p in ASSETS.items()},'STOP':True}))
