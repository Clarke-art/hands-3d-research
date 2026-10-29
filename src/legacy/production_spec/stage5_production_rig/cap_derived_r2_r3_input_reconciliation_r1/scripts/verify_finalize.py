"""Verify all numerical audit products and frozen files; never runs production code."""
import json,hashlib,sys,ast
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def canon(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
required=['CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1_REPORT.md','CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1_STATUS.json','CORRECTED_LIVE_THUMB_CHAIN_R1.json','R2_SEED_AUTHORITY_RECONCILIATION.json','R2_DOMAIN_INPUT_RULE_R1.json','CORRECTED_THUMB_TUBE_ANCHOR_CANDIDATE_AUDIT.json','R3_STRONG_ANCHOR_INPUT_RECONCILIATION.json','FIRST_WEB_WRAPPER_RECONCILIATION_R1.json','NAIL_CAP_WRAPPER_RECONCILIATION_R1.json','CMC_CAGE_R3_WRAPPER_RECONCILIATION_R1.json','R3_UNARY_FIELD_INPUT_CONTRACT_R1.json','R3_GRAPH_DOMAIN_INPUT_RECONCILIATION.json','R3_VALIDATOR_REUSE_RECONCILIATION.json','R2_R3_INPUT_DIFF_PREVIEW.json']
assert all((OUT/n).is_file() for n in required)
assert not (OUT/'CANONICAL_R2_R3_RECONCILED_INPUT_CONTRACT_R1.json').exists()
assert not (OUT/'R2_R3_INPUT_RECONCILIATION_HUMAN_REVIEW.html').exists()
assert not list(OUT.rglob('*.blend*'))
A=read(OUT/'AUTHORITY_INPUT_VERIFICATION.json');J=read(OUT/'READ_ONLY_LIVE_EXTRACTION.json')
for key,s in A['sources'].items():assert sha(ROOT/s['path'])==s['sha256'],key
cap=read(ROOT/A['sources']['cap_authority']['path']);assert canon({k:v for k,v in cap.items() if k!='combined_authority_hash'})==A['cap_combined_authority_hash']
assert len(cap['vertex_ids'])==37 and len(cap['face_ids'])==25
native=read(ROOT/A['sources']['native_partition_evidence']['path']);labels=native['labels'];oldcap={151,158,1061,1074,1076,2189,2192,2569,2577}
assert all(labels[v]=='index' for v in oldcap)
assert all(labels[v]=='thumb' for v in cap['vertex_ids'])
for key in ['CORRECTED','NATIVE']:
 assert J[key]['faces']==J['RSSF']['faces'] and J[key]['edges']==J['RSSF']['edges']
assert J['CORRECTED']['vertices_world_m']==J['RSSF']['vertices_world_m']
assert J['CORRECTED']['material_indices']==J['RSSF']['material_indices']
assert J['CORRECTED']['bones']['THUMB_IP_R']['tail_world_m']==J['CORRECTED']['bones']['THUMB_TIP_R']['head_world_m']
assert J['CORRECTED']['bones']['THUMB_IP_R']['tail_world_m']==J['RSSF']['vertices_world_m'][284]
t=read(OUT/'CORRECTED_THUMB_TUBE_ANCHOR_CANDIDATE_AUDIT.json')
for key in ['native_guarded_tube','native_guarded_corridor','two_ring_stable_tube','two_ring_stable_corridor']:
 ids=t['sets'][key]['vertex_ids'];assert not (oldcap&set(ids));assert all(labels[i]=='thumb' for i in ids)
assert all(labels[i]=='index' for i in t['sets']['index_native_guarded_tube']['vertex_ids'])
assert t['radius_sampling_sensitivity']['tube_delta']['before_count']==164 and t['radius_sampling_sensitivity']['tube_delta']['after_candidate_count']==155
assert len(t['ingredient_overlap']['rawtube_vs_native_index'])==41
n=read(OUT/'NAIL_CAP_WRAPPER_RECONCILIATION_R1.json')
for d,faces in n['per_digit_face_ids'].items():
 assert all(J['RSSF']['material_indices'][f]==1 for f in faces)
 assert set(n['per_digit_vertex_sets'][d]['vertex_ids'])=={v for f in faces for v in J['RSSF']['faces'][f]}
assert not n['cross_digit_conflicts']
sourceCode=read(OUT/'SOURCE_CODE_PROVENANCE_R1.json')
for s in sourceCode:assert sha(ROOT/s['path'])==s['sha256']
checkedSets=[]
def visit(x,path):
 if isinstance(x,dict):
  if 'set_sha256' in x:
   assert x['vertex_ids']==sorted(set(x['vertex_ids']));assert len(x['vertex_ids'])==x['count'];assert canon(x['vertex_ids'])==x['set_sha256'],path;checkedSets.append({'record':path,'count':x['count'],'set_sha256':x['set_sha256']})
  for k,v in x.items():visit(v,path+'/'+k)
 elif isinstance(x,list):
  for k,v in enumerate(x):visit(v,path+'/'+str(k))
for p in sorted(OUT.glob('*.json')):
 if p.name not in ['FROZEN_HASHES_BEFORE.json','READ_ONLY_LIVE_EXTRACTION.json','RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json']:visit(read(p),p.name)
# All pre-existing files are immutable; this also detects outside-output writes/new files.
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after={'workspace':{},'external':{}};changes=[]
for k,h in before['workspace'].items():
 p=ROOT/k;after['workspace'][k]=sha(p) if p.is_file() else None
 if after['workspace'][k]!=h:changes.append({'path':k,'before':h,'after':after['workspace'][k]})
for k,h in before['external'].items():
 p=Path(k);after['external'][k]=sha(p) if p.is_file() else None
 if after['external'][k]!=h:changes.append({'path':k,'before':h,'after':after['external'][k]})
outside_new=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts and str(p.relative_to(ROOT)) not in before['workspace']]
assert not changes and not outside_new,(changes,outside_new)
dump('FROZEN_HASHES_AFTER.json',after)
frozen={'status':'PASS','before_manifest':'FROZEN_HASHES_BEFORE.json','after_manifest':'FROZEN_HASHES_AFTER.json','workspace_files_checked':len(before['workspace']),'external_files_checked':len(before['external']),'mismatch_count':len(changes),'changed_files':changes,'new_files_outside_output':outside_new,'all_before_equal_after':True,'scope':'All pre-existing workspace files excluding .git plus six external protected Human/authority inputs. Includes every historical blend, Stage4/5, R2/R3, Stage6, corrected rig, cap37 and Human responses.'}
dump('FROZEN_HASH_VERIFICATION_R1.json',frozen)
statusPath=OUT/'CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1_STATUS.json';s=read(statusPath);assert s['status']=='FAIL_CLOSED_UNRESOLVED_INPUT_AUTHORITY';assert s['combined_input_contract_hash'] is None and not s['new_input_contract_generated'] and not s['R3_RECOMPUTE_ALLOWED'];s['frozen_hash_verification']=frozen;s['output_verification']='PASS';dump(statusPath.name,s)
v={'status':'PASS','required_files_present':required,'conditional_canonical_contract_absent_as_required':True,'ready_for_R3_approval_page_absent_as_required':True,'corrected_chain_live_read_verified':True,'native_RSSF_topology_identity_verified':True,'cap37_membership_verified_unchanged':True,'nail_face_material_and_membership_verified':True,'candidate_set_hashes_checked':len(checkedSets),'geometry_hash':canon(J['RSSF']['vertices_world_m']),'topology_hash':canon({'edges':J['RSSF']['edges'],'faces':J['RSSF']['faces']}),'scripts_parseable':True,'forbidden_runs':'No production modules imported or executed. Blender only opened files and read bones/geometry; extract_live.py has no save call. Static candidate scripts use numpy geometry and a cap37-only medoid shortest-path comparison; no R2 partition, R3 dT/dI full fields/mincut/closure/boundary or skin code.','all_frozen_hashes_equal':True}
for p in (OUT/'scripts').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
dump('OUTPUT_VERIFICATION_R1.json',v)
sourcefiles={k:val for k,val in A['sources'].items()}
sourcefiles['historical_R3_labels']={'path':'production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary/R3_OWNERSHIP_LABELS.json','role':'DIFF_ONLY','sha256':sha(ROOT/'production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary/R3_OWNERSHIP_LABELS.json')}
manifest={'type':'READ_ONLY_RECONCILIATION_EVIDENCE_MANIFEST_NOT_CANONICAL_CONTRACT','status':'FAIL_CLOSED','hash_method':'SHA256; JSON set hash over sorted unique integer IDs using UTF-8 compact sort_keys JSON; file hashes over exact bytes. Combined evidence hash excludes its own field.','authority_sources':sourcefiles,'cap_combined_authority_hash':A['cap_combined_authority_hash'],'reconciled_candidate_set_hashes':checkedSets,'output_file_hashes':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json'},'combined_input_contract_hash':None,'future_contract_requirement':'Only after all critical authorities resolved may a canonical contract be emitted. Its source+set hashes must be verified before any separately Human-approved R3 run.'}
manifest['combined_evidence_package_hash']=canon(manifest);dump('RECONCILIATION_EVIDENCE_HASH_MANIFEST_R1.json',manifest)
print(json.dumps({'verification':'PASS','frozen_files':len(before['workspace']),'external_files':len(before['external']),'candidate_set_hashes_checked':len(checkedSets),'contract_generated':False,'combined_contract_hash':None,'evidence_hash':manifest['combined_evidence_package_hash'],'NEXT':s['NEXT'],'STOP':True},indent=2))
