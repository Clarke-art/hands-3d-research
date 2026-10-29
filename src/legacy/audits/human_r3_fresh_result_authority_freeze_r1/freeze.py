"""Consume the designated Human response and freeze existing R3 outputs only.
No solver/validator imports, graph traversal, geometry API or production write.
"""
import sys
sys.dont_write_bytecode=True
import json,hashlib,datetime
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
FRESH=ROOT/'audits/r3_full_recompute_and_authority_revalidation_r1'
REVAL=ROOT/'audits/r3_sheet_identity_validator_reconciliation_r1'
INPUT=ROOT/'audits/r3_recovery_input_contract_finalization_r1'
RUN='HUMAN_R3_FRESH_RESULT_AUTHORITY_FREEZE_R1'
AUTH='FRESH_R3_OWNERSHIP_AUTHORITY_R1'
SCOPE='BOUNDED_SOLVER_DOMAIN_VERTEX_OWNERSHIP_AUTHORITY'
METHOD='BOUNDED_VERTEX_LABEL_REGION_IDENTITY_WITH_PURE_FACE_AND_MIXED_BAND_VALIDATION_R2'
CONTRACT_HASH='f392fd33be0430cabf4b849fb8a4565853c245f2cf09e953d506493c93ca3cab'
PROX_HASH='5ff37ae7d0915e1ab3b57b00f261b47b038e78a0bf1d316d0c52c39d5b063afb'
LABEL_HASH='c401b8bdfaad33a554ee87a94bd1fcc991684658bf05301ef5a0df7f6a7b2631'
VALIDATOR_HASH='f0a8312df970d3972c424add5b4677fbe34630f20f8a3b487fb432b306b77dc2'
NEXT='CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1'
RESPONSE=Path('<USER_HOME>/Downloads/R3_FRESH_RESULT_HUMAN_REVIEW_R2_RESPONSE_2026-10-03T12-22-24-961Z.json')
INPUT_RESPONSE=Path('<USER_HOME>/Downloads/R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T10-43-37-453Z.json')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def rel(p):
 try:return str(Path(p).relative_to(ROOT))
 except ValueError:return str(p)
def ref(p,role=None):
 d={'path':rel(p),'sha256':sha(p)}
 if role:d['role']=role
 return d
def resolve(p):p=Path(p);return p if p.is_absolute() else ROOT/p
def inventory():return {rel(p):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents}

def main():
 if (OUT/(AUTH+'.json')).exists():raise RuntimeError('Authority already exists; refuse overwrite')
 checks=[]
 def gate(name,ok,detail=None):
  checks.append({'check':name,'pass':bool(ok),'detail':detail})
  if not ok:
   dump('FREEZE_INPUT_VERIFICATION_R1.json',{'pass':False,'checks':checks,'freeze_performed':False})
   dump(RUN+'_STATUS.json',{'status':'FAIL_CLOSED','failed_check':name,'authority_frozen':False,'R3_reruns':0,'skin_rebuilds':0,'Stage6_runs':0,'BLEND_FILES_WRITTEN':0,'STOP':True})
   raise RuntimeError('FAIL_CLOSED: '+name)
 before=inventory();dump('FROZEN_HASHES_BEFORE.json',before)
 response=read(RESPONSE);response_hash=sha(RESPONSE);input_response_hash=sha(INPUT_RESPONSE)
 required={'review_id':'R3_FRESH_RESULT_HUMAN_REVIEW_R2','phase':'HUMAN_R3_FRESH_RESULT_APPROVAL','canonical_contract_hash':CONTRACT_HASH,'proximal_boundary_authority_hash':PROX_HASH,'fresh_result_label_hash':LABEL_HASH,'validator_revalidation_hash':VALIDATOR_HASH,'canonical_sheet_validator_method':METHOD,'technical_verdict':'PASS_READY_FOR_HUMAN_REVIEW','revalidation_blockers':[],'accepted_as_ownership_authority_candidate':True,'sheet_revalidation_pass':True,'validation_mode':False,'automatic_apply':False,'automatic_solver_execution':False,'skin_rebuild_approved':False,'Stage6_approved':False}
 for k,v in required.items():gate('Human response '+k,type(response.get(k))==type(v) and response.get(k)==v)
 qkeys=['Q1_overall_ownership','Q2_first_web','Q3_index_sheet','Q4_thumb_base_palm','Q5_hard_source_preservation','Q6_boundary_ambiguity','Q7_accept_ownership_authority_candidate']
 for k in qkeys:gate('Human response '+k,response.get(k)=='YES')
 gate('Formal Human response kind',response.get('response_kind')=='HUMAN_R3_FRESH_RESULT_REVIEW_RESPONSE')
 gate('Human notes preserved',isinstance(response.get('notes'),str) and bool(response['notes']))
 # All bound frozen files are checked by hashes; prior validators are not executed.
 for folder in [FRESH,REVAL]:
  manifest=read(folder/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')
  for name,h in manifest.items():gate('Frozen output hash '+rel(folder/name),sha(folder/name)==h)
 contract=read(INPUT/'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1.json');gate('Canonical input contract hash',digest(contract)==CONTRACT_HASH)
 for name,r in list(contract['files'].items())+list(contract['frozen_authority_sources'].items()):gate('Referenced frozen authority hash '+name,sha(resolve(r['path']))==r['sha256'])
 prior_input=read(INPUT_RESPONSE)
 for k,v in {'review_id':'R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW_R1','contract_id':'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1','canonical_contract_hash':CONTRACT_HASH,'proximal_boundary_authority_hash':PROX_HASH,'approved_for_input_contract':True,'cost_semantics_approved_with_contract':True,'validation_mode':False}.items():gate('Input approval chain '+k,type(prior_input.get(k))==type(v) and prior_input.get(k)==v)
 labeldoc=read(FRESH/'R3_FRESH_FINAL_LABELS_R1.json');labels={int(k):v for k,v in labeldoc['labels'].items()};ids=sorted(labels)
 gate('Fresh label hash (original integer-ID ordering)',digest(labels)==LABEL_HASH==labeldoc['label_sha256'])
 gate('Binary labels only',set(labels.values())=={'THUMB','INDEX'})
 members={lab:sorted(v for v,l in labels.items() if l==lab) for lab in ['THUMB','INDEX']}
 gate('Unique 962 membership, 498 THUMB / 464 INDEX',len(labels)==962 and len(members['THUMB'])==498 and len(members['INDEX'])==464 and not set(members['THUMB'])&set(members['INDEX']))
 graphpath=INPUT/'R3_ENGINEERING_GRAPH_DOMAIN_R1.json';graph=read(graphpath)
 gate('Frozen graph V/E and exact IDs',graph['vertex_count']==962 and graph['edge_count']==1881 and graph['vertex_ids']==ids and len(graph['edge_ids'])==1881 and len(set(graph['edge_ids']))==1881)
 sourcepaths={'THUMB':INPUT/'R3_AUTHORITY_BACKED_THUMB_HARD_SOURCES_R1.json','INDEX':INPUT/'R3_INDEX_HARD_SOURCES_R1.json'};sourcedocs={lab:read(p) for lab,p in sourcepaths.items()};sources={lab:d['unique']['vertex_ids'] for lab,d in sourcedocs.items()}
 for lab,expected in [('THUMB',57),('INDEX',145)]:
  gate('Unique '+lab+' sources/hash',len(sources[lab])==len(set(sources[lab]))==expected and digest(sources[lab])==sourcedocs[lab]['unique']['set_sha256'])
  gate('Frozen '+lab+' source labels preserved',all(labels.get(v)==lab for v in sources[lab]))
 gate('Source conflicts zero',not set(sources['THUMB'])&set(sources['INDEX']))
 boundarypath=FRESH/'R3_FRESH_BOUNDARY_AUDIT_R1.json';boundary=read(boundarypath);cutids=[r['edge_id'] for r in boundary['edges']]
 gate('Frozen 20 boundary edges',boundary['pass'] and boundary['self_consistency'] and boundary['edge_count']==len(cutids)==len(set(cutids))==20)
 closure=read(FRESH/'R3_FRESH_CLOSURE_AUDIT_R1.json');gate('Frozen closure 1 sweep converged 0 changes',closure['full_sweeps']==1 and closure['converged'] is True and closure['cumulative_changed_count']==0)
 islands=read(FRESH/'R3_FRESH_ISLAND_AUDIT_R1.json');gate('Frozen islands zero',islands['pass'] and islands['islands_count']==0)
 ambpath=FRESH/'R3_FRESH_AMBIGUITY_AUDIT_R1.json';amb=read(ambpath);gate('Frozen ambiguity21 complete',amb['vertex_count']==len(amb['vertex_ids'])==len(amb['vertices'])==21 and set(amb['vertex_ids'])<=set(labels))
 classa=read(FRESH/'R3_FRESH_CLASS_A_AUDIT_R1.json');gate('Frozen CLASS_A6/6',classa['status']=='PASS' and classa['pass_count']==classa['geometry_pass_count']==len(classa['edges'])==6)
 webpath=FRESH/'R3_FRESH_FIRST_WEB21_AUDIT_R1.json';web=read(webpath);webids=sorted(int(k) for k in web['vertex_labels'])
 gate('Frozen FIRST_WEB21 7/14 no pins',web['distribution']=={'THUMB':7,'INDEX':14} and len(webids)==21 and web['hard_pins']==0 and not set(webids)&(set(sources['THUMB'])|set(sources['INDEX'])) and web['written_back_to_anatomy_authority'] is False)
 gate('FIRST_WEB labels equal frozen field',all(labels[v]==web['vertex_labels'][str(v)] for v in webids))
 oldcap=read(FRESH/'R3_OLD_CAP9_FRESH_RESULT_AUDIT_R1.json');oldids=[r['vertex_id'] for r in oldcap['vertices']]
 gate('Frozen old cap9 9 INDEX hard role NONE',len(oldids)==9 and oldcap['hard_role_count']==0 and oldcap['distribution']=={'INDEX':9} and all(r['strong_hard_role']=='NONE' and r['final_label']=='INDEX' and labels[r['vertex_id']]=='INDEX' for r in oldcap['vertices']) and not set(oldids)&(set(sources['THUMB'])|set(sources['INDEX'])))
 cap_authority_ref=contract['frozen_authority_sources']['cap_authority'];capauthority=read(resolve(cap_authority_ref['path']));cap=read(FRESH/'R3_CAP37_SOURCE_PRESERVATION_AUDIT_R1.json');capids=sorted(capauthority['vertex_ids'])
 gate('Canonical cap37 unchanged and preserved',capauthority['status']=='HUMAN_APPROVED_FROZEN' and len(capids)==37 and cap['pass'] is True and cap['count']==37 and cap['hard_source_preserved'] and not cap['conflicts'] and set(capids)<=set(sources['THUMB']) and all(labels[v]=='THUMB' for v in capids))
 index=read(FRESH/'R3_INDEX_SOURCE_PRESERVATION_AUDIT_R1.json');gate('Frozen 145/145 INDEX source preservation',index['pass'] is True and index['source_count']==index['preserved_count']==len(index['vertices'])==145 and {r['vertex_id'] for r in index['vertices']}==set(sources['INDEX']) and all(r['final_label']=='INDEX' for r in index['vertices']))
 validatorpath=REVAL/'R3_SHEET_IDENTITY_REVALIDATION_R2.json';validator=read(validatorpath)
 gate('Exact sheet validator revalidation hash',sha(validatorpath)==VALIDATOR_HASH)
 gate('Frozen canonical sheet validator PASS',validator['verdict']=='FRESH_R3_SHEET_IDENTITY_PASS' and validator['canonical_validator_method']==METHOD and validator['frozen_result_hash']==LABEL_HASH and all(validator[k] is True for k in ['V1_pass','V2_pass','mixed_band_pass','domain_respecting_V3_pass','INDEX_identity_resolved','THUMB_identity_resolved']))
 derived=read(REVAL/'R3_FRESH_DERIVED_VALIDATION_STATUS_R2.json');gate('Derived result ready for Human review',derived['derived_verdict']=='PASS_READY_FOR_HUMAN_REVIEW' and derived['fresh_labels_hash']==LABEL_HASH and derived['canonical_contract_hash']==CONTRACT_HASH)
 proximalref=contract['frozen_authority_sources']['proximal_boundary'];gate('Proximal boundary authority hash',digest(read(resolve(proximalref['path'])))==PROX_HASH)
 costpath=INPUT/'R3_COST_UNIT_CONTRACT_R1.json';cost=read(costpath);gate('Bind already-approved cost contract',cost['R3_COST_UNIT']=='CORRECTED_COMMON_MM_SEMANTICS')
 statusR1=read(FRESH/'R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1_STATUS.json')
 gate('Frozen R1 summary consistency',all(statusR1[k]==v for k,v in {'graph_V':962,'graph_E':1881,'fresh_THUMB_count':498,'fresh_INDEX_count':464,'THUMB_hard_source_count':57,'INDEX_hard_source_count':145,'source_conflicts':0,'final_boundary_edge_count':20,'ambiguity_vertex_count':21,'CLASS_A_pass_count':6}.items()))
 gate('All existing files unchanged before freeze',before==inventory())
 gate('Formal responses unchanged before freeze',sha(RESPONSE)==response_hash and sha(INPUT_RESPONSE)==input_response_hash)
 dump('FREEZE_INPUT_VERIFICATION_R1.json',{'pass':True,'checks':checks,'Human_response_sha256':response_hash,'prior_input_response_sha256':input_response_hash,'solver_or_sheet_validator_executed':False,'unit_semantics_reaudited':False,'freeze_authorized_by_current_user_request':True})
 print('All approval/hash/frozen-output checks passed; constructing new freeze artifacts.',flush=True)
 # This is the first publication of an authority, only after every gate has passed.
 sourcecopy=OUT/'HUMAN_R3_FRESH_RESULT_RESPONSE_SOURCE_COPY.json';sourcecopy.write_bytes(RESPONSE.read_bytes());gate('Byte-identical Human response source copy',sha(sourcecopy)==response_hash)
 membership={'schema':'R3_VERTEX_MEMBERSHIP_SORTED_PAIRS_R1','authority_scope':SCOPE,'graph_vertex_ids':ids,'vertex_label_pairs':[[v,labels[v]] for v in ids],'THUMB_vertex_ids':members['THUMB'],'INDEX_vertex_ids':members['INDEX']}
 membership_hash=digest(membership);(OUT/'R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json').write_bytes(canon(membership))
 dump('R3_OWNERSHIP_MEMBERSHIP_HASH.json',{'algorithm':'SHA-256','canonicalization':'UTF-8, sorted string object keys, compact comma/colon separators, no trailing newline; vertex-ID pairs and per-label lists sorted numerically','membership_hash':membership_hash,'canonical_file':ref(OUT/'R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json'),'vertex_count':962,'THUMB_count':498,'INDEX_count':464,'original_fresh_label_hash':LABEL_HASH,'original_label_hash_convention':'Fresh R1 digest of integer-keyed mapping in numeric-ID order; distinct from new explicit-pair membership hash.'})
 boundaryauthority={'authority_id':'DERIVED_OWNERSHIP_BOUNDARY_R1','status':'DERIVED_FROM_HUMAN_FROZEN_OWNERSHIP_FIELD','edge_ids':sorted(cutids),'edge_count':20,'edge_records':boundary['edges'],'membership_sha256':digest(sorted(cutids)),'audit_reference':ref(boundarypath),'independent_anatomical_surface_authority':False}
 ambiguityauthority={'authority_id':'DERIVED_AMBIGUITY_BAND_R1','status':'DERIVED_FROM_FROZEN_COST_FIELDS','vertex_ids':amb['vertex_ids'],'vertex_count':21,'vertex_records':amb['vertices'],'membership_sha256':digest(amb['vertex_ids']),'audit_reference':ref(ambpath),'vertices_retain_binary_ownership':True,'third_ownership_label':False}
 bounds={'full_physical_mesh_anatomical_ownership_map_approved':False,'physical_mesh_separation_approved':False,'global_body_wrist_ownership_approved':False,'skin_weights_approved':False,'Stage5B_rebuild_approved':False,'Stage6_approved':False,'final_production_qualification_approved':False,'automatic_apply':False,'automatic_solver_execution':False,'pointwise_anatomical_landmark_authority_created':False}
 authority={'authority_id':AUTH,'status':'HUMAN_APPROVED_FROZEN','authority_type':SCOPE,'authority_scope':SCOPE,'domain_definition':'Exactly the hash-bound 962-vertex engineering solver domain; frozen THUMB/INDEX vertex ownership only. Outside this domain remains unassigned.','approval_scope_limits':bounds,'graph':{'vertex_ids':graph['vertex_ids'],'edge_ids':graph['edge_ids'],'vertex_count':962,'edge_count':1881,'graph_sha256':sha(graphpath),'vertex_set_sha256':digest(graph['vertex_ids']),'edge_set_sha256':digest(graph['edge_ids']),'reference':ref(graphpath)},'membership':{'vertex_labels':{str(v):labels[v] for v in ids},'THUMB_vertex_ids':members['THUMB'],'INDEX_vertex_ids':members['INDEX'],'vertex_count':962,'THUMB_count':498,'INDEX_count':464,'membership_hash':membership_hash,'fresh_result_label_hash':LABEL_HASH,'original_output_reference':ref(FRESH/'R3_FRESH_FINAL_LABELS_R1.json'),'membership_canonical_reference':ref(OUT/'R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json')},'hard_sources':{lab:{'vertex_ids':sources[lab],'count':len(sources[lab]),'set_sha256':sourcedocs[lab]['unique']['set_sha256'],'reference':ref(sourcepaths[lab]),'all_frozen_labels_preserved':True} for lab in ['THUMB','INDEX']},'hard_source_conflicts':0,'boundary':boundaryauthority,'ambiguity':ambiguityauthority,'sheet_validator':{'method':METHOD,'validator_revalidation_hash':VALIDATOR_HASH,'reference':ref(validatorpath),'status':'HUMAN_ACCEPTED_CANONICAL_BOUND_VERTEX_IDENTITY','V1':'vertex-label region identity / coverage','V2':'pure-face coherence','mixed_boundary_band':'validation carrier, no third ownership label','domain_respecting_V3':'barrier cross-check','full_face_dual_physical_split_as_ownership_gate':'RETIRED_VALIDATOR_METHOD_MISMATCH','original_R1_failure_reference':ref(FRESH/'R3_FRESH_SHEET_SPLIT_AUDIT_R1.json'),'physical_mesh_split_claim':False},'FIRST_WEB21':{'membership_vertex_ids':webids,'original_anatomical_membership_reference':contract['frozen_authority_sources']['first_web_membership'],'anatomical_authority_unchanged':True,'hard_pin_count':0,'fresh_distribution':{'THUMB':7,'INDEX':14},'fresh_vertex_labels':web['vertex_labels'],'fresh_label_role':'SOLVER_DERIVED_BOUNDED_OWNERSHIP_ONLY_NOT_ANATOMICAL_WRITEBACK'},'old_cap9':{'vertex_ids':sorted(oldids),'historical_anatomical_status':'SUPERSEDED_CONTAMINATED','hard_role_count':0,'fresh_distribution':{'THUMB':0,'INDEX':9},'fresh_labels':{str(v):labels[v] for v in sorted(oldids)},'fresh_label_role':'SOLVER_RESULT_ONLY','upgraded_to_anatomical_landmark':False},'cap37_preservation':{'pass':True,'count':37,'vertex_ids':capids,'all_THUMB':True,'all_hard_source_preserved':True,'authority_reference':cap_authority_ref,'audit_reference':ref(FRESH/'R3_CAP37_SOURCE_PRESERVATION_AUDIT_R1.json')},'INDEX_source_preservation':{'pass':True,'preserved_count':145,'source_count':145,'all_INDEX':True,'audit_reference':ref(FRESH/'R3_INDEX_SOURCE_PRESERVATION_AUDIT_R1.json')},'closure':{'full_sweeps':1,'converged':True,'changed_count':0,'reference':ref(FRESH/'R3_FRESH_CLOSURE_AUDIT_R1.json')},'islands':{'count':0,'reference':ref(FRESH/'R3_FRESH_ISLAND_AUDIT_R1.json')},'CLASS_A':{'pass_count':6,'total_count':6,'geometry_authority_unchanged':True,'reference':ref(FRESH/'R3_FRESH_CLASS_A_AUDIT_R1.json')},'input_contract':{'contract_id':contract['contract_id'],'canonical_contract_hash':CONTRACT_HASH,'reference':ref(INPUT/'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1.json'),'Human_approval_reference':ref(INPUT_RESPONSE)},'proximal_boundary_authority':{'canonical_hash':PROX_HASH,'reference':proximalref,'scope':'PROXIMAL_SEMANTIC_STOP_AUTHORITY_UNCHANGED'},'approved_cost_contract':{'semantics':'CORRECTED_COMMON_MM_SEMANTICS','cost_contract_reference':ref(costpath),'input_contract_hash':CONTRACT_HASH,'previous_Human_approval_reference':ref(INPUT_RESPONSE),'unit_reaudit_performed':False},'Human_approval':{'review_id':response['review_id'],'phase':response['phase'],'response_sha256':response_hash,'response_reference':ref(RESPONSE),'source_copy_reference':ref(sourcecopy),'notes_verbatim':response['notes'],'responses':{k:response[k] for k in qkeys},'response_export_Human_approved_frozen':response['Human_approved_frozen'],'scope':'BOUNDED_SOLVER_DOMAIN_OWNERSHIP_ONLY','freeze_action_authorization':'Current explicit HUMAN_R3_FRESH_RESULT_AUTHORITY_FREEZE_R1 user request consumes the accepted Human candidate; original exported response remains unchanged.'},'downstream_state':{'SKIN_WEIGHT_AUTHORITY':'NOT_YET_RECONCILED','SKIN_REBUILD':'NOT_STARTED','Stage6':'NOT_RUN','NEXT':NEXT,'automatic_start':False,'skin_rebuild_authorized_by_this_freeze':False},'execution_limits':{'fresh_labels_changed':0,'R3_reruns':0,'Dijkstra_runs':0,'mincut_runs':0,'closure_runs':0,'sheet_validator_runs':0,'skin_rebuilds':0,'Stage6_runs':0,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0}}
 combined=digest(authority);dump(AUTH+'.json',authority);(OUT/(AUTH+'_CANONICAL.json')).write_bytes(canon(authority))
 dump('R3_OWNERSHIP_AUTHORITY_HASH.json',{'algorithm':'SHA-256','canonicalization':'UTF-8 sorted string keys; compact comma/colon separators; array order retained; no newline; complete authority payload, no excluded authority fields','authority_id':AUTH,'status':'HUMAN_APPROVED_FROZEN','combined_authority_hash':combined,'canonical_file':ref(OUT/(AUTH+'_CANONICAL.json')),'pretty_authority_file':ref(OUT/(AUTH+'.json')),'membership_hash':membership_hash,'deterministic_payload_has_no_run_timestamp':True})
 chain=[{'step':1,'phase':'R3_RECOVERY_INPUT_CONTRACT_HUMAN_APPROVAL','path':str(INPUT_RESPONSE),'hash':input_response_hash,'status':'HUMAN_APPROVED_INPUT_CONTRACT','effect':'Approves bounded inputs and CORRECTED_COMMON_MM_SEMANTICS, not fresh results or production changes.','contract_reference':ref(INPUT/'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1.json'),'canonical_contract_hash':CONTRACT_HASH},{'step':2,'phase':'R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1',**ref(FRESH/'R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1_STATUS.json'),'hash':sha(FRESH/'R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1_STATUS.json'),'status':'TECHNICALLY_VALID_BUT_HUMAN_REVIEW_REQUIRED','effect':'Creates fresh frozen solver labels, boundary and fields; original face-dual failure retained.','fresh_result_label_hash':LABEL_HASH},{'step':3,'phase':'R3_SHEET_IDENTITY_VALIDATOR_RECONCILIATION_R1',**ref(REVAL/'R3_SHEET_IDENTITY_VALIDATOR_RECONCILIATION_R1_STATUS.json'),'hash':sha(REVAL/'R3_SHEET_IDENTITY_VALIDATOR_RECONCILIATION_R1_STATUS.json'),'status':'FRESH_R3_SHEET_IDENTITY_PASS','effect':'Static derived-method correction; labels unchanged; binds canonical bounded sheet validator.','validator_reference':ref(validatorpath),'validator_revalidation_hash':VALIDATOR_HASH},{'step':4,'phase':'R3_FRESH_RESULT_HUMAN_REVIEW_R2','path':str(RESPONSE),'hash':response_hash,'status':'HUMAN_ACCEPTED_OWNERSHIP_AUTHORITY_CANDIDATE','effect':'Q1–Q7 YES approve bounded ownership candidate and R2 method; notes exclude skin, full mesh and Stage6 approval.','review_page_reference':ref(REVAL/'R3_FRESH_RESULT_HUMAN_REVIEW_R2.html'),'source_copy_reference':ref(sourcecopy)},{'step':5,'phase':RUN,**ref(OUT/(AUTH+'.json')),'hash':sha(OUT/(AUTH+'.json')),'status':'HUMAN_APPROVED_FROZEN','effect':'Publishes a new bounded-domain ownership authority only; no historical or production files changed.','combined_authority_hash':combined}]
 dump('R3_OWNERSHIP_AUTHORITY_PROVENANCE_CHAIN.json',{'authority_id':AUTH,'combined_authority_hash':combined,'chain':chain,'Human_notes_verbatim':response['notes'],'old_full_face_dual_failure_preserved':True,'no_historical_rewrite':True,'new_authority_does_not_approve_skin_or_Stage6':True})
 dump('R3_DOWNSTREAM_SKIN_RECONCILIATION_TRIGGER.json',{'status':'NEXT_PHASE_DECLARED_NOT_STARTED','NEXT':NEXT,'prerequisite_authority':AUTH,'prerequisite_authority_status':'HUMAN_APPROVED_FROZEN','combined_authority_hash':combined,'membership_hash':membership_hash,'authority_reference':ref(OUT/(AUTH+'.json')),'automatic_start':False,'automatic_apply':False,'skin_rebuild_authorized':False,'skin_rebuild_count':0,'Stage6_authorized':False,'Stage6_runs':0,'skin_weight_authority':'NOT_YET_RECONCILED','skin_rebuild_status':'NOT_STARTED','next_round_topics':['cap37 driver authority','old cap9 native INDEX correction','R3 ownership to skin role','first-web weight wrapper','independent R1B entries','edge5879','new skin rebuild scope'],'execution_of_next_phase_this_run':False,'STOP':True})
 # Verify the new freeze is internally coherent, without re-running any original gate algorithm.
 gate('Authority canonical bytes/hash',sha(OUT/(AUTH+'_CANONICAL.json'))==combined and digest(read(OUT/(AUTH+'.json')))==combined)
 gate('Membership canonical bytes/hash',sha(OUT/'R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json')==membership_hash)
 gate('Full authority mapping matches frozen solver membership',read(OUT/(AUTH+'.json'))['membership']['vertex_labels']==labeldoc['labels'])
 gate('Verbatim Human notes preserved',read(OUT/(AUTH+'.json'))['Human_approval']['notes_verbatim']==response['notes'])
 after=inventory();gate('All pre-existing files before/after equal',before==after)
 gate('Both formal Human response files unchanged',sha(RESPONSE)==response_hash and sha(INPUT_RESPONSE)==input_response_hash)
 dump('FREEZE_INPUT_VERIFICATION_R1.json',{'pass':True,'checks':checks,'Human_response_sha256':response_hash,'prior_input_response_sha256':input_response_hash,'solver_or_sheet_validator_executed':False,'unit_semantics_reaudited':False,'freeze_authorized_by_current_user_request':True})
 dump('FROZEN_HASHES_AFTER.json',after);dump('FROZEN_HASH_VERIFICATION_R1.json',{'pass':True,'protected_file_count':len(before),'modified_files':[],'external_Human_responses_unchanged':True,'fresh_labels_changed':0,'historical_files_modified':False,'fresh_solver_files_modified':False,'blend_files_modified':False,'skin_weights_modified':False,'BLEND_FILES_WRITTEN':0})
 result={'phase':RUN,'authority_id':AUTH,'Human_response_verified':'YES','Fresh_label_hash_verified':'YES','Sheet_validator_hash_verified':'YES','graph_V':962,'graph_E':1881,'THUMB_count':498,'INDEX_count':464,'Boundary_count':20,'Ambiguity_count':21,'CLASS_A':'6/6 PASS','FIRST_WEB21_distribution':{'THUMB':7,'INDEX':14},'FIRST_WEB21_hard_pins':0,'old_cap9_distribution':{'THUMB':0,'INDEX':9},'old_cap9_hard_role':0,'old_cap9_status':'SUPERSEDED_CONTAMINATED','cap37_preservation':'37/37 THUMB HARD_SOURCE_PRESERVED','INDEX_hard_source_preservation':'145/145 INDEX HARD_SOURCE_PRESERVED','authority_scope':SCOPE,'membership_hash':membership_hash,'combined_authority_hash':combined,'historical_files_modified':False,'fresh_solver_files_modified':False,'blend_files_modified':False,'skin_weights_modified':False,'authority_status':'HUMAN_APPROVED_FROZEN','SKIN_WEIGHT_AUTHORITY':'NOT_YET_RECONCILED','SKIN_REBUILD':'NOT_STARTED','Stage6':'NOT_RUN','R3_reruns':0,'skin_rebuilds':0,'Stage6_runs':0,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'NEXT':NEXT,'STOP':True}
 dump(RUN+'_STATUS.json',result)
 report=f'''# {RUN}

**{AUTH} = HUMAN_APPROVED_FROZEN.** Scope: **{SCOPE}**. This freezes THUMB/INDEX ownership within the exact962-vertex engineering solver domain. Outside-domain vertices remain unassigned; this authority creates no full physical mesh anatomical map or global body/wrist authority.

## Approval consumption and identity

Sole new formal Human response: `{RESPONSE.name}`; source SHA-256 `{response_hash}`. Review ID R3_FRESH_RESULT_HUMAN_REVIEW_R2; phase HUMAN_R3_FRESH_RESULT_APPROVAL; all Q1–Q7 YES; accepted candidate=true; sheet_revalidation_pass=true; validation_mode=false. Every specified contract, proximal, label, validator and method binding matches exactly. Empty revalidation blockers and PASS_READY_FOR_HUMAN_REVIEW are verified. All automatic/apply/solver/skin/Stage6 flags are false. A byte-identical source copy and the complete original notes are saved. The export's Human_approved_frozen=false is preserved: export accepted the candidate; this explicitly requested phase performs the authority freeze without changing that response.

Original fresh labels hash: `{LABEL_HASH}` (original integer-ID ordering). Frozen graph962 vertices/1881 edges, THUMB498/INDEX464, hard sources57/145, conflicts0, boundary20, ambiguity21, closure1 sweep/converged/0 changes, islands0, CLASS_A6/6 PASS. Cap37 remains37/37 THUMB hard sources with the original cap-authority hash unchanged. All145 INDEX hard sources remain INDEX. Both prior output evidence manifests and all referenced input/authority hashes match. No Dijkstra, mincut, closure, sheet validator, R3 solve or unit re-audit was performed; stored outputs were checked only.

## Membership and combined authority hash

Membership hash: `{membership_hash}`. The canonical membership payload uses numerically sorted [vertex_id,label] pairs, complete graph IDs and separate sorted THUMB/INDEX membership lists. Its schema/scope are included. This explicit-pair hash differs from the original R1 label mapping hash by serialization definition, not by membership. The authority also contains the complete vertex_id→THUMB/INDEX mapping, and equality with frozen solver labels was verified.

Combined authority hash: `{combined}`. Canonical bytes are UTF-8, sorted string object keys, compact comma/colon separators, preserved array order and no trailing newline. They cover the complete authority payload: ID/status/scope, graph IDs/edges/hash, memberships, hard source sets/hashes, full boundary/ambiguity membership and records/hashes, FIRST_WEB/cap9 distributions, cap37/INDEX preservation, validator method/hash, contract/proximal/label hashes, Human response/hash/notes and approval limits. The payload contains no run timestamp or mutable self-hash. The pretty JSON and canonical JSON encode the same authority; R3_OWNERSHIP_AUTHORITY_HASH.json records both file hashes and the combined canonical hash.

## Authority semantics and limits

Canonical validator `{METHOD}` is formally bound: V1 vertex-label identity/coverage; V2 pure-face coherence; mixed band validation carrier; domain-respecting V3 barrier cross-check. The old full face-dual physical split remains retired as an ownership identity gate. Original R1 failure and approved input contract remain unchanged as provenance evidence.

FIRST_WEB21 retains its original anatomical membership file/hash, hard pins0 and ownership distribution7 THUMB/14 INDEX. These are solver-derived bounded ownership labels; no FIRST_WEB anatomical writeback occurred. Old cap9 retain SUPERSEDED_CONTAMINATED status and hard role0; their9 INDEX labels are solver results, not anatomical landmark authority.

The20 cut edges are frozen as DERIVED_OWNERSHIP_BOUNDARY_R1, with complete IDs/endpoints/labels and audit hashes. They are derived from the ownership field and do not become independently approved anatomical surface authority. All21 ambiguity vertices and frozen dT/dI comparison records are retained as DERIVED_AMBIGUITY_BAND_R1; they keep binary ownership labels and do not become a third class.

CORRECTED_COMMON_MM_SEMANTICS is bound through its unchanged cost-contract hash and prior Human-approved input contract. Units were not re-audited. The five-step provenance chain records input approval → fresh recompute → validator reconciliation → R2 Human result response → current freeze, each with path/hash/status/effect.

## Human notes — verbatim

```text
{response['notes']}
```

## Protection and downstream state

All {len(before)} pre-existing workspace files have identical before/after SHA-256 hashes. Both external formal Human response hashes remain unchanged. Historical R3, fresh solver results, R1/R2 Human pages, R1B/C/D/E, Stage6, cap authorities, corrected rig and every blend are immutable. R3 reruns=0; skin rebuilds=0; Stage6 runs=0; BLEND_FILES_WRITTEN=0. WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0.

SKIN_WEIGHT_AUTHORITY=NOT_YET_RECONCILED; SKIN_REBUILD=NOT_STARTED; Stage6=NOT_RUN. The new trigger declares NEXT={NEXT} and automatic_start=false. That phase is not executed or authorized as a skin rebuild by this freeze. Its future topics are cap37 driver authority, old cap9 native INDEX correction, ownership→skin roles, first-web weight wrapper, independent R1B entries, edge5879 and a new rebuild scope.

**NEXT: {NEXT}. STOP.**
'''
 (OUT/(RUN+'_REPORT.md')).write_text(report,encoding='utf8')
 requiredfiles=[AUTH+'.json',RUN+'_REPORT.md',RUN+'_STATUS.json','R3_OWNERSHIP_AUTHORITY_PROVENANCE_CHAIN.json','R3_OWNERSHIP_AUTHORITY_HASH.json','R3_OWNERSHIP_MEMBERSHIP_HASH.json','R3_DOWNSTREAM_SKIN_RECONCILIATION_TRIGGER.json']
 gate('All requested artifacts present',all((OUT/n).is_file() for n in requiredfiles))
 dump('FREEZE_OUTPUT_VERIFICATION_R1.json',{'pass':True,'required_files':requiredfiles,'authority_status':'HUMAN_APPROVED_FROZEN','mapping_equal_frozen_solver':True,'canonical_membership_hash':membership_hash,'combined_authority_hash':combined,'before_after_file_hashes_equal':True,'Human_notes_verbatim':True,'production_approved_or_started':False,'NEXT':NEXT,'STOP':True})
 dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'})
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
