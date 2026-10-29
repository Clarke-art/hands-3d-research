import sys
sys.dont_write_bytecode=True
from common import *
from html.parser import HTMLParser
from urllib.parse import unquote
status=read(OUT/(PHASE+'_STATUS.json'));frozen=read(OUT/'FROZEN_INPUT_NATIVE_PAYLOADS_R1.json');saved=read(OUT/'PALMAR_STAGE5_BEFORE_SAVE_PAYLOADS_R1.json');weight=read(OUT/'PALMAR_STAGE5_WEIGHT_PAYLOAD_EQUIVALENCE_R1.json');rig=read(OUT/'PALMAR_STAGE5_RIG_PAYLOAD_EQUIVALENCE_R1.json');members=read(OUT/'PALMAR_STAGE5_AUTHORITY_MEMBERSHIP_R1.json');gates=read(OUT/'PALMAR_STAGE5_DOWNSTREAM_REQUIRED_GATES_R1.json');recovery=read(OUT/'PALMAR_STAGE5_INPUT_LINEAGE_RECOVERY_R1.json')
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','PALMAR_STAGE5_INPUT_LINEAGE_RECOVERY_R1.json','PALMAR_STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json','PALMAR_STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json','PALMAR_STAGE5_RIG_PAYLOAD_EQUIVALENCE_R1.json','PALMAR_STAGE5_WEIGHT_PAYLOAD_EQUIVALENCE_R1.json','PALMAR_STAGE5_NORMAL69_PROTECTION_R1.json','PALMAR_STAGE5_AUTHORITY_MEMBERSHIP_R1.json','PALMAR_STAGE5_CURRENT9_INDEPENDENCE_R1.json','PALMAR_STAGE5_JOINT_SURFACE_DIAGNOSTIC_R1.json','PALMAR_STAGE5_ZERO_EVAL_SMOKE_R1.json','PALMAR_STAGE5_SAVE_REOPEN_AUDIT_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json']+[p.name for p in ASSETS.values()]
assert all((OUT/n).is_file() for n in required)
for p in OUT.glob('*.json'):read(p)
for k,z in recovery['inputs'].items():assert sha(Path(z['path']))==EXPECTED[k]
normal=read(DESIGN/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json')['vertex_ids'];assert len(normal)==69
for k,p in ASSETS.items():
 s=read(OUT/(k+'_REOPENED_NATIVE_PAYLOAD_R1.json'));old=frozen[k];target=frozen['STAGE4'];assert sha(p)==saved[k]['asset']['sha256'];assert s==saved[k]['after']
 assert s['coordinates_local_m']==target['coordinates_local_m'] and s['coordinates_world_m']==target['coordinates_world_m'] and len(s['coordinates_local_m'])==3416
 changed=[i for i,(a,b) in enumerate(zip(old['coordinates_local_m'],s['coordinates_local_m'])) if a!=b];assert changed==IDS
 assert all(old['coordinates_local_m'][i]==s['coordinates_local_m'][i]==target['coordinates_local_m'][i] for i in normal)
 assert all(old['coordinates_local_m'][i]==s['coordinates_local_m'][i] for i in members['sets']['dorsal54']['frozen_native_vertex_ids'])
 assert s['protected']==old['protected'];assert rig['paths'][k]['source_rig_payload_sha256']==rig['paths'][k]['derived_rig_payload_sha256']
 assert weight['paths'][k]['source_exact_including_zero_payload_sha256']==weight['paths'][k]['derived_exact_including_zero_payload_sha256']
 rolls=read(OUT/(k+'_NATIVE_ROLL_EQUIVALENCE_R1.json'));assert rolls['source_native_rolls']==rolls['reopened_native_rolls']==old['native_editbone_rolls']
 smoke=read(OUT/(k+'_ZERO_EVAL_SMOKE_RESULT_R1.json'));assert smoke['ZERO_EVAL_SMOKE']=='PASS' and smoke['evaluated_vertex_count']==3416 and smoke['missing_bones_count']==smoke['missing_groups_count']==smoke['NaN_Inf_count']==smoke['evaluation_failure_count']==0 and not smoke['Stage6_poses_run'] and smoke['artifact_hash_unchanged']
 assert saved[k]['assigned_coordinate_count']==3416 and saved[k]['new_scene_provenance_metadata']['MID_MCP_45_MANDATORY_REVALIDATION']==saved[k]['new_scene_provenance_metadata']['WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED']=='YES'
 assert saved[k]['new_scene_provenance_metadata']['NEXT_RECORDED_ONLY']==NEXT
assert digest(read(OUT/'R2_REOPENED_NATIVE_PAYLOAD_R1.json')['positive_weight_vectors'])==WEIGHT_HASH==status['R2_WEIGHT_HASH_AFTER_PROPAGATION']
assert {k:v['membership_count'] for k,v in members['sets'].items()}=={'cap37':37,'old_cap9':9,'FIRST_WEB21':21,'fresh_R3_protected_domain':962,'historical317_weight_universe':317,'thumb_nail':22,'CMC_frozen_cage_context':73,'dorsal54':54,'palmar16':16}
for s in members['sets'].values():assert sha(Path(s['authority']['path']))==s['authority']['sha256'] and digest(s['frozen_native_vertex_ids'])==s['membership_sha256']
assert gates['MID_MCP_45_MANDATORY_REVALIDATION']==gates['WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_REQUIRED']=='YES' and gates['NEXT']==NEXT and not gates['NEXT_EXECUTED']
diag=read(OUT/'PALMAR_STAGE5_JOINT_SURFACE_DIAGNOSTIC_R1.json');assert diag['classification']=='DIAGNOSTIC_ONLY' and not diag['joints_moved'] and not diag['thresholds_or_anatomy_qualification']
for d in diag['paths'].values():assert len(d['measurements'])==42 and len(d['palmar16_nearest_fixed_joint_heads'])==16 and {r['bone'] for r in d['highlight_fixed_joint_measurements']}=={'WRIST_R','MIDDLE_MCP_R','RING_MCP_R'}
assert status['VERDICT']=='PASS_GEOMETRY_PROPAGATED_WITH_RIG_AND_WEIGHTS_FROZEN' and status['STOP'] and not status['NEXT_EXECUTED'] and status['PRODUCTION_PROMOTION']=='NO'
assert status['CURRENT9_DIRECT_OVERLAP']==status['CURRENT9_1RING_OVERLAP']==status['CURRENT9_2RING_OVERLAP']==0 and status['CURRENT9_HUMAN_RESPONSE']=='HOLD_NOT_CLOSED'
assert status['MID_MCP_pose_evaluation_runs']==status['Full42_runs']==status['Stage6B_runs']==0 and not status['whole_hand_integrity_baseline_executed'] and not status['current9_closure_generated']
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory();assert before==after,'FAIL_CLOSED: protected history drift'
initial=read(OUT/'CURRENT9_RESPONSE_STATE_BEFORE.json');response=ref(RESPONSE) if RESPONSE.is_file() else None;assert response==initial['external_source'];assert sha(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json')==initial['prior_hold_receipt']['sha256']
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src'] and not v.startswith('#'):self.paths.append(v)
links=Links();links.feed((OUT/'review.html').read_text(encoding='utf-8'));broken=[p for p in links.paths if not (OUT/unquote(p)).is_file()];assert not broken
dump('PALMAR_STAGE5_FINAL_DELIVERY_VALIDATION_R1.json',{'status':'PASS','required_artifacts':required,'broken_review_links':broken,'frozen_preexisting_file_count':len(before),'PROTECTED_HISTORY_DRIFT':0,'full3416_geometry_local_world_exact_each':True,'actual_changed16_each':True,'normal69_dorsal54_outside16_exact':True,'complete_original_rig_weight_group_modifier_material_UV_metadata_exact':True,'native_rolls_reopen_exact':True,'fresh_R2_weight_hash':WEIGHT_HASH,'minimal_ZERO_smoke_only_PASS':True,'membership_IDs_counts_unchanged':True,'diagnostic_only_joint_surface':True,'mandatory_future_flags_saved_and_retained':True,'current9_HOLD_preserved':True,'new_assets':{k:ref(p) for k,p in ASSETS.items()},'NEXT_not_executed':True})
dump('OUTPUT_EVIDENCE_HASH_MANIFEST.json',{'files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST.json'}})
print('FINAL DELIVERY PASS:',len(before),'history files unchanged; complete3416 each /changed16 each /rig+weights frozen /STOP',flush=True)
