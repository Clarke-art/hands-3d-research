"""Re-run the approved static validator on cleanly reopened, unchanged weights.

No constructor, solver, setter, save, pose evaluation, or authority selector is run.
Geometry measurements below are diagnostic context, never weight acceptance priors.
"""
import sys
sys.dont_write_bytecode=True
from common import *
import math, collections

N=read(OUT/'CURRENT_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json')
O=read(OUT/'OLD_R2_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json')
C=read(OUT/'CORRECTED_RIG_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json')
ARCHIVE=read(R2DIR/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
R1DIR=S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1'
W=N['positive_weight_vectors']; OLDW=O['positive_weight_vectors']
B=read(R1DIR/'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json')['weights']
D=read(R1DIR/'LIVE_SOURCE_DATA_R1.json')['R1B']['weights']
EDGES=[e[1] for e in N['protected']['mesh']['edges']]
SCOPE=read(R2DIR/'AUTHORIZED_WEIGHT_WRITE_SET_R2.json')
WRITE,ORIGINAL,NEW18,CLEAN55=[set(SCOPE[k]) for k in ['approved_write_universe_317','original_244','additional_continuity_18','cleanup_only_55']]
CONT=read(AUTH/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')
CAP=read(AUTH/'CAP37_SKIN_DRIVER_AUTHORITY_R1.json')
OLD=read(AUTH/'OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json')
WEB=read(AUTH/'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
EDGE_AUTH=read(AUTH/'EDGE5879_REBUILD_SCOPE_R1.json')
R3=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')
LABEL={int(k):v for k,v in R3['membership']['vertex_labels'].items()}
WEBIDS=set(WEB['membership']['vertex_ids'])
CAPIDS={r['vertex_id'] for r in CAP['per_vertex_surface_evidence']}
OLDIDS=set(OLD['vertex_ids'])
TOL=CONT['normalization']['absolute_tolerance']
CANONCAP=read(ROOT/CAP['membership_reference']['path'])
ORIGIN=read(R2DIR/'R2_CONTINUITY_STATIC_AUDIT.json')
PRE_FORMAL=read(PRE/'STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json')
PRIOR={**ORIGIN,'all_checked_edges':PRE_FORMAL['all_checked_edges']}
CLASS=read(R2DIR/'R2_STATIC_BLOCKER_CLASSIFICATION.json')
APP=read(ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_AUTHORITY_INTERSECTION_AUDIT_R1.json')
PROP_AUDIT=read(PROP/'PALMAR_STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json')
IDS=set(PROP_AUDIT['actual_changed_ids'])
DEBT_EXPECTED=[1130,1137,1171,1172,1174,1176,1555,4417,4421,4425,4427,4428,4431,4474,4881,5474]
minimal_blockers=[]
def gate(name,ok,detail=None):
 if not ok:
  minimal_blockers.append({'gate':name,'detail':detail})
  dump(PHASE+'_STATUS.json',{'VERDICT':'FAIL_CLOSED_STATIC_SKIN_COMPATIBILITY_AFTER_PALMAR','minimal_blocker':minimal_blockers[0],'STOP':True})
  (OUT/(PHASE+'_REPORT.md')).write_text('FAIL_CLOSED_STATIC_SKIN_COMPATIBILITY_AFTER_PALMAR\n\n'+json.dumps(minimal_blockers[0],ensure_ascii=False,indent=2)+'\nNo repair. STOP.\n',encoding='utf-8')
  raise SystemExit('FAIL CLOSED: '+name)
 return bool(ok)
def audit(n,obj): dump(n,obj); return obj
def raw(i,data=N):
 return {data['group_order'][j]:v for j,v in data['protected']['weights_exact_including_zero'][i]}
def binary_dense(data): return b''.join(struct.pack('<16f',*row) for row in data['dense_float32_rows'])
def subset_rows(ids):
 return [{'vertex_id':i,'old_R2_vector':OLDW[i],'current_vector':W[i],
          'dense_float32_exact':N['dense_float32_rows'][i]==O['dense_float32_rows'][i],
          'stored_entries_including_zero_exact':N['protected']['weights_exact_including_zero'][i]==O['protected']['weights_exact_including_zero'][i]} for i in sorted(ids)]

# Only the existing validator's pure functions are loaded; its top-level solver/report code is never executed.
reuse_log=[reuse(R2DIR/'common.py',['metric'],globals()),reuse(R2DIR/'audit_and_report.py',['support','fails','edge_record'],globals())]
audit('STATIC_VALIDATOR_FUNCTION_REUSE_R1.json',{'status':'PASS','records':reuse_log,'historical_solver_execution':False})

# Bind recovered contracts to the recorded Human response, proposal, and existing authority receipts.
approval=read(R2DIR/'HUMAN_AMENDMENT_APPROVAL_SOURCE_COPY.json')
proposal=ROOT/'audits/skin_static_gate_semantics_and_scope_reconciliation_r1/SKIN_WRITE_SCOPE_AMENDMENT_R2_PROPOSAL.json'
manifest=read(R2DIR/'OUTPUT_EVIDENCE_HASH_MANIFEST_R2.json')
baseline_files=['R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json','R2_CONTINUITY_STATIC_AUDIT.json','R2_STATIC_BLOCKER_CLASSIFICATION.json','R2_ZERO_CLEANUP_EXPECTED.json','AUTHORIZED_WEIGHT_WRITE_SET_R2.json','HUMAN_AMENDMENT_APPROVAL_SOURCE_COPY.json','HUMAN_AMENDMENT_AND_INPUT_VERIFICATION_R2.json']
baseline_hash_checks={f:sha(R2DIR/f)==manifest['files'][f] for f in baseline_files}
historical_inputs=read(R2DIR/'HUMAN_AMENDMENT_AND_INPUT_VERIFICATION_R2.json')
component_checks={f:sha(AUTH/f)==h for f,h in historical_inputs['authority_component_hashes'].items()}
authority_refs=[CAP['membership_reference'],R3['graph']['reference']]+[x['source'] for x in APP['sets'].values()]
authority_hash_checks=[{'reference':r,'match':sha(ROOT/r['path'])==r['sha256']} for r in authority_refs]
contract_checks={
 'baseline_evidence_manifest_hashes':all(baseline_hash_checks.values()),
 'all12_original_skin_authority_components':all(component_checks.values()),
 'Human_Q1_to_Q5_accepted':approval['all_accepted'] and all(approval[f'Q{i}']=='YES' for i in range(1,6)),
 'proposal_hash_bound':sha(proposal)==approval['proposal_sha256']==SCOPE['proposal_sha256'],
 'Human_response_hash_bound':sha(R2DIR/'HUMAN_AMENDMENT_APPROVAL_SOURCE_COPY.json')==SCOPE['approval_sha256'],
 'continuity_semantics':CLASS['canonical_semantics']=='SCOPED_ABSOLUTE_SCREEN_PLUS_NO_REGRESSION_WITH_EXPLICIT_QUALIFICATION',
 'normalization_contract':TOL==1e-5,
 'static_limits_retained':PRIOR['canonical_absolute_limits']=={'L_inf':.5,'L1':1},
 'frozen_authority_reference_hashes':all(x['match'] for x in authority_hash_checks),
 'cap37_membership_exact':CAPIDS==set(CANONCAP['vertex_ids'])==set(R3['cap37_preservation']['vertex_ids']),
 'old_cap9_membership_exact':OLDIDS==set(R3['old_cap9']['vertex_ids'])==set(CANONCAP['old_cap9_ids']),
 'FIRST_WEB21_membership_exact':WEBIDS==set(R3['FIRST_WEB21']['membership_vertex_ids']),
 'historical317_membership_exact':len(WRITE)==317 and WRITE==set(APP['sets']['historical317_weight_universe']['frozen_vertex_ids']),
}
gate('RESTORED_STATIC_CONTRACT_AUTHORITY',all(contract_checks.values()),contract_checks)
audit('STATIC_SKIN_CONTRACT_RECOVERY_R1.json',{'status':'PASS' if all(contract_checks.values()) else 'FAIL_CLOSED','checks':contract_checks,'baseline_manifest_checks':baseline_hash_checks,'skin_authority_component_checks':component_checks,'authority_reference_checks':authority_hash_checks,
 'semantics':CLASS['canonical_semantics'],'normalization_tolerance':TOL,'canonical_zero_epsilon':0,
 'historical_construction_methods_are_not_acceptance_gates':True,'sources':[ref(proposal),ref(R2DIR/'HUMAN_AMENDMENT_APPROVAL_SOURCE_COPY.json'),ref(AUTH/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json'),ref(R2DIR/'audit_and_report.py')]})

full_binary=binary_dense(N);old_binary=binary_dense(O)
(OUT/'STATIC_SKIN_DENSE_FLOAT32_PAYLOAD_READONLY_R1.bin').write_bytes(full_binary)
payload_checks={'vertex_count_3416':len(W)==3416,'group_count_16':len(N['group_order'])==16,
 'group_order_exact':N['group_order']==O['group_order']==ARCHIVE['group_order']==CONT['deform_bones'],
 'weight_authority_hash':digest(W)==WEIGHT_HASH,
 'old_R2_archive_hash':digest(ARCHIVE['weights'])==WEIGHT_HASH,
 'all_positive_vectors_exact':W==OLDW==ARCHIVE['weights'],
 'dense_float32_bytes_exact':full_binary==old_binary,
 'sparse_entries_order_and_explicit_zeros_exact':N['protected']['weights_exact_including_zero']==O['protected']['weights_exact_including_zero'],
 'all_values_exactly_float32':all(f32(x)==x for row in N['dense_float32_rows'] for x in row)}
gate('STATIC_SKIN_PAYLOAD',all(payload_checks.values()),payload_checks)
audit('STATIC_SKIN_WEIGHT_PAYLOAD_AUDIT_R1.json',{'status':'PASS' if all(payload_checks.values()) else 'FAIL_CLOSED_STATIC_SKIN_PAYLOAD_DRIFT',
 'checks':payload_checks,'R2_WEIGHT_VECTOR_HASH':digest(W),'authority_hash_serialization':'Canonical sorted-key compact UTF-8 JSON of positive group-name vectors, using directly read IEEE float32 values; identical to historical R2 digest',
 'dense_float32_le_SHA256':hashlib.sha256(full_binary).hexdigest(),'dense_byte_count':len(full_binary),'group_order':N['group_order'],
 'stored_entry_count':sum(len(x) for x in N['protected']['weights_exact_including_zero']),
 'explicit_stored_zero_count':sum(v==0 for row in N['protected']['weights_exact_including_zero'] for _,v in row),
 'implicit_dense_zero_count':sum(v==0 for row in N['dense_float32_rows'] for v in row),
 'full_float32_payload_reference':ref(OUT/'CURRENT_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json'),
 'weight_writes':0,'normalization_calls':0,'runtime_prune_calls':0})
if not all(payload_checks.values()):
 dump(PHASE+'_STATUS.json',{'VERDICT':'FAIL_CLOSED_STATIC_SKIN_PAYLOAD_DRIFT','minimal_blocker':minimal_blockers[0],'STOP':True})
 raise RuntimeError('FAIL_CLOSED_STATIC_SKIN_PAYLOAD_DRIFT')

# Every stored entry is tested, not just the positive hash representation.
violations={k:[] for k in ['weight_sum','negative','NaN','Inf','max_influences','non_deform_groups','TIP_helpers','FIRST_WEB_THUMB_IP','illegal_cross_digit','forbidden_residue']}
math_rows=[]
deform=set(CONT['deform_bones']);helpers=set(CONT['helpers']['names'])
for i in range(3416):
 v=raw(i); values=list(v.values()); s=sum(values)
 error=abs(s-1); influences=sum(x>0 for x in values)
 if not math.isfinite(s) or error>TOL:violations['weight_sum'].append(i)
 for key,predicate in [('negative',lambda x:x<0),('NaN',math.isnan),('Inf',math.isinf)]:
  violations[key].extend({'vertex_id':i,'group':g,'value':x if math.isfinite(x) else str(x)} for g,x in v.items() if predicate(x))
 if influences>CONT['max_influences']:violations['max_influences'].append(i)
 violations['non_deform_groups'].extend({'vertex_id':i,'group':g,'value':x} for g,x in v.items() if g not in deform and x!=0)
 violations['TIP_helpers'].extend({'vertex_id':i,'group':g,'value':x} for g,x in v.items() if g in helpers and x!=0)
 if i in WEBIDS and v.get('THUMB_IP_R',0)!=0:violations['FIRST_WEB_THUMB_IP'].append(i)
 foreign=[{'vertex_id':i,'group':g,'value':x} for g,x in v.items() if g not in support(i) and x!=0]
 violations['forbidden_residue'].extend(foreign)
 if i in LABEL and foreign:violations['illegal_cross_digit'].append({'vertex_id':i,'foreign_entries':foreign})
 math_rows.append({'vertex_id':i,'sum':s,'absolute_sum_error':error,'positive_influences':influences,'allowed_groups':sorted(support(i)),'forbidden_entry_count':len(foreign)})
cleanup=[]
for r in read(R2DIR/'R2_ZERO_CLEANUP_EXPECTED.json')['per_vertex']:
 i=r['vertex_id']; entries={g:raw(i).get(g,0) for g in r['forbidden_entries_removed']}
 cleanup.append({'vertex_id':i,'forbidden_entries':entries,'all_exact_zero':all(x==0 for x in entries.values()),'payload_exact_old_R2':W[i]==OLDW[i]==r['expected_float32_after']})
math_pass=not any(violations.values()) and len(cleanup)==55 and all(r['all_exact_zero'] and r['payload_exact_old_R2'] for r in cleanup)
gate('FULL_MESH_MATH_AND_CLEANUP55',math_pass, {k:len(v) for k,v in violations.items()})
audit('STATIC_SKIN_FULL_MESH_MATH_AUDIT_R1.json',{'status':'PASS' if math_pass else 'FAIL_CLOSED','checked_vertex_count':3416,
 'normalization_tolerance':TOL,'max_sum_error':max(r['absolute_sum_error'] for r in math_rows),'max_positive_influences':max(r['positive_influences'] for r in math_rows),
 'canonical_zero_epsilon':0,'violations':violations,'violation_counts':{k:len(v) for k,v in violations.items()},'cleanup55':cleanup,'per_vertex':math_rows,
 'ownership_scope':'Frozen962 plus cap37/oldcap9/FIRST_WEB wrappers; remaining mesh uses the official deform-group contract. No invented whole-mesh anatomy labels.'})

# Reconstruct the same static closure; fresh R3 is read solely as a side/leakage guard.
prior_R1=read(R1DIR/'SKIN_CONTINUITY_STATIC_CHECK_R1.json')
previous_checked={r['edge_id'] for r in prior_R1['all_checked_edges']}
seed=WRITE|set(WEB['continuity_scope'])|set(OLD['continuity_gate']['patch_vertex_ids'])|set(CAP['continuity_gate']['cap_2ring_vertex_ids'])|set(EDGE_AUTH['neighborhood_ids'])
checked=previous_checked|{eid for eid,(i,j) in enumerate(EDGES) if i in seed or j in seed or (i in LABEL and j in LABEL and LABEL[i]!=LABEL[j])}
records=[edge_record(eid) for eid in sorted(checked)]
by_edge={r['edge_id']:r for r in records};prior_by_edge={r['edge_id']:r for r in PRIOR['all_checked_edges']}
topology_exact=N['protected']['mesh']['edges']==O['protected']['mesh']['edges'] and EDGES==ARCHIVE['mesh']['edges']
edge_identity=topology_exact and checked==set(prior_by_edge)=={r['edge_id'] for r in ORIGIN['all_checked_edges']} and len(checked)==PRE_FORMAL['checked_edge_count']==2127
gate('STATIC_EDGE_SET_IDENTITY',edge_identity)
eq=[]
for r in records:
 eid=r['edge_id']; i,j=r['vertex_ids']; saved=prior_by_edge.get(eid)
 old_metric=metric(OLDW[i],OLDW[j]);actual=r['R2_metrics']
 eq.append({'edge_id':eid,'vertex_ids':[i,j],'endpoints_exact_old_R2':W[i]==OLDW[i] and W[j]==OLDW[j],
 'current_metric':actual,'old_R2_freshly_recomputed_metric':old_metric,'old_R2_saved_metric':saved['R2_metrics'] if saved else None,
 'metric_exact_old_R2':actual==old_metric and saved is not None and actual==saved['R2_metrics'] and actual==next(z for z in ORIGIN['all_checked_edges'] if z['edge_id']==eid)['R2_metrics'],
 'L_inf_delta_vs_old_R2':actual['L_inf']-old_metric['L_inf'],'L1_delta_vs_old_R2':actual['L1']-old_metric['L1'],
 'endpoint_ID_exact_saved_edge':saved is not None and r['vertex_ids']==saved['vertex_ids']})
exact_count=sum(r['metric_exact_old_R2'] and r['endpoint_ID_exact_saved_edge'] for r in eq)
gate('OLD_R2_EDGE_METRIC_EQUIVALENCE',exact_count==2127,{'exact_count':exact_count})
audit('STATIC_SKIN_OLD_R2_METRIC_EQUIVALENCE_R1.json',{'status':'PASS' if exact_count==2127 else 'FAIL_CLOSED',
 'STATIC_EDGE_SET_IDENTITY':edge_identity,'current_checked_edge_set_SHA256':digest(sorted(checked)),
 'old_checked_edge_set_SHA256':digest(sorted(prior_by_edge)),'EDGE_METRIC_EXACT_MATCH_COUNT':exact_count,'total':len(checked),
 'MAX_LINF_DELTA_VS_OLD_R2':max(abs(r['L_inf_delta_vs_old_R2']) for r in eq),
 'MAX_L1_DELTA_VS_OLD_R2':max(abs(r['L1_delta_vs_old_R2']) for r in eq),'per_edge':eq})

# Recompute existing R2 causal classification, with the same normalization comparison tolerance.
blockers=[]
for row in records:
 if not row['absolute_exceedance']:continue
 i,j=row['vertex_ids']; exact=all(W[v]==B[v]==D[v] for v in [i,j]);witnesses=[]
 for u,v in [(i,j),(j,i)]:
  if u in WRITE and v not in WRITE:
   foreign={g:value for g,value in W[v].items() if g not in support(u)}
   f=sum(foreign.values());a=sum(value for g,value in W[v].items() if g in support(u))
   inf=max(foreign.values(),default=0);l1=f+max(0,1-TOL-a)
   if inf>.5 or l1>1:witnesses.append({'write_vertex':u,'immutable_vertex':v,'minimum_possible_L_inf':inf,'minimum_possible_L1':l1,'foreign_components':foreign})
 if exact and i not in WRITE and j not in WRITE:temporal=primary='INHERITED_COPY_ONLY'
 elif not fails(row['R1_metrics']):temporal='R2_INTRODUCED';primary='TRUE_SCOPE_CONFLICT' if witnesses else temporal
 elif row['L_inf_delta_vs_R1']>TOL or row['L1_delta_vs_R1']>TOL:temporal='R2_WORSENED';primary='TRUE_SCOPE_CONFLICT' if witnesses else temporal
 elif row['L_inf_delta_vs_R1']<0 or row['L1_delta_vs_R1']<0:temporal='R2_IMPROVED_BUT_STILL_FAIL';primary='TRUE_SCOPE_CONFLICT' if witnesses else temporal
 else:temporal='UNCHANGED_AFFECTED_SEAM';primary='TRUE_SCOPE_CONFLICT' if witnesses else 'SEMANTIC_TRANSITION_REQUIRES_QUALIFICATION'
 blockers.append({**row,'primary_classification':primary,'temporal_classification':temporal,'true_scope_conflict_witnesses':witnesses,
 'classification':'INHERITED_COPY_ONLY_STATIC_QUALIFICATION_DEBT' if primary=='INHERITED_COPY_ONLY' else primary,'resolved':False})
debts=[r for r in blockers if r['primary_classification']=='INHERITED_COPY_ONLY']
debt_ids=[r['edge_id'] for r in debts]
introduced=sum(r['temporal_classification']=='R2_INTRODUCED' for r in blockers)
worsened=sum(r['temporal_classification']=='R2_WORSENED' for r in blockers)
conflicts=sum(bool(r['true_scope_conflict_witnesses']) for r in blockers)
debt_exact=debt_ids==DEBT_EXPECTED==CLASS['inherited_qualification_debt_ids'] and all(by_edge[eid]['R2_metrics']==prior_by_edge[eid]['R2_metrics'] and all(W[v]==OLDW[v]==B[v]==D[v] and v not in WRITE for v in EDGES[eid]) for eid in debt_ids)
gate('INHERITED_DEBT_IDENTITY',debt_exact)
gate('CANDIDATE_INTRODUCED_WORSENED_SCOPE_CONFLICT',introduced==worsened==conflicts==0 and len(blockers)==16)
audit('STATIC_SKIN_INHERITED_DEBT_REVALIDATION_R1.json',{'status':'PASS_DEBT_PRESERVED' if debt_exact else 'FAIL_CLOSED','identity_match':debt_exact,'count':len(debts),'edge_ids':debt_ids,'classification':'INHERITED_COPY_ONLY_STATIC_QUALIFICATION_DEBT','resolved_count':0,'edges':debts})
coverage={name:all(eid in checked for eid,(i,j) in enumerate(EDGES) if i in verts or j in verts) for name,verts in {'historical317':WRITE,'FIRST_WEB_full_2ring':set(WEB['continuity_scope']),'cap37_2ring':set(CAP['continuity_gate']['cap_2ring_vertex_ids']),'old_cap9_patch':set(OLD['continuity_gate']['patch_vertex_ids']),'edge5879_neighborhood':set(EDGE_AUTH['neighborhood_ids'])}.items()}
coverage['fresh_R3_boundary']=all(eid in checked for eid,(i,j) in enumerate(EDGES) if i in LABEL and j in LABEL and LABEL[i]!=LABEL[j])
gate('CONTINUITY_SCOPE_COVERAGE',all(coverage.values()))
audit('STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json',{'status':'PASS_STATIC_SCREEN_WITH_16_INHERITED_DEBTS' if edge_identity and exact_count==2127 and debt_exact and introduced==worsened==conflicts==0 and all(coverage.values()) else 'FAIL_CLOSED','semantics':CLASS['canonical_semantics'],
 'limits':PRIOR['canonical_absolute_limits'],'checked_edge_count':len(checked),'coverage':coverage,'absolute_blocker_count':len(blockers),
 'R2_introduced_count':introduced,'R2_worsened_count':worsened,'true_scope_conflict_count':conflicts,'all_checked_edges':records,'all_exceedances':blockers,
 'subthreshold_historical_increases_preserved':PRIOR['subthreshold_no_regression_diagnostics'],'weight_construction_rerun':False,'deformation_qualified':False})

cap_rows=[]
for r in CAP['per_vertex_surface_evidence']:
 i=r['vertex_id'];s=r['corrected_thumb_projection']['arc_mm'];t=max(0.,min(1.,.5+(s-CAP['rule']['s_IP_mm'])/(2*CAP['rule']['h_mm'])));q=t*t*t*(t*(6*t-15)+10)
 expected={g:f32(v) for g,v in [('THUMB_IP_R',q),('THUMB_MCP_R',1-q)] if v>0}
 cap_rows.append({'vertex_id':i,'frozen_historical_arc_mm':s,'historical_quintic_float32':expected,'saved_vector':W[i],
 'quintic_historical_payload_exact':expected==W[i]==OLDW[i],'IP_dominant':W[i].get('THUMB_IP_R',0)>=W[i].get('THUMB_MCP_R',0),
 'geometry_unchanged':N['coordinates_local_m'][i]==O['coordinates_local_m'][i]})
cap_pass=len(cap_rows)==37 and all(r['quintic_historical_payload_exact'] and r['IP_dominant'] and r['geometry_unchanged'] for r in cap_rows)
gate('CAP37_FROZEN_PROFILE',cap_pass)
audit('STATIC_SKIN_CAP37_REVALIDATION_R1.json',{'status':'PASS' if cap_pass else 'FAIL_CLOSED','membership_count':37,'canonical_authority':ref(ROOT/CAP['membership_reference']['path']),
 'membership_exact':CAPIDS==set(CANONCAP['vertex_ids']),'vectors_exact_old_R2':all(W[i]==OLDW[i] for i in CAPIDS),'historical_corrected_arc_quintic_preserved_count':sum(r['quintic_historical_payload_exact'] for r in cap_rows),
 'IP_dominant_count':sum(r['IP_dominant'] for r in cap_rows),'allowed_groups':CAP['allowed_cap_deform_groups'],'new_geometry_projection_runs':0,'new_weights_generated':0,'per_vertex':cap_rows})
old_pass=len(OLDIDS)==9 and all(W[i]==OLDW[i] and LABEL[i]=='INDEX' and all(g in OLD['allowed_deform_groups'] or x==0 for g,x in raw(i).items()) for i in OLDIDS)
gate('OLD_CAP9_INDEX_PAYLOAD',old_pass)
audit('STATIC_SKIN_OLD_CAP9_REVALIDATION_R1.json',{'status':'PASS' if old_pass else 'FAIL_CLOSED','count':9,'native_INDEX_SURFACE_count':sum(LABEL[i]=='INDEX' for i in OLDIDS),
 'THUMB_distal_override_count':sum(any(x!=0 for g,x in raw(i).items() if g.startswith('THUMB_')) for i in OLDIDS),'vectors_exact_old_R2':old_pass,'allowed_groups':OLD['allowed_deform_groups'],'per_vertex':subset_rows(OLDIDS)})
web_pass=len(WEBIDS)==21 and all(W[i]==OLDW[i] and all(g in WEB['allowed_deform_groups'] or x==0 for g,x in raw(i).items()) for i in WEBIDS)
gate('FIRST_WEB_SHARED_WRAPPER',web_pass)
audit('STATIC_SKIN_FIRST_WEB_REVALIDATION_R1.json',{'status':'PASS' if web_pass else 'FAIL_CLOSED','count':21,'membership_exact':WEBIDS==set(R3['FIRST_WEB21']['membership_vertex_ids']),
 'vectors_exact_old_R2':all(W[i]==OLDW[i] for i in WEBIDS),'allowed_groups':WEB['allowed_deform_groups'],'THUMB_IP_exact_zero':all(raw(i).get('THUMB_IP_R',0)==0 for i in WEBIDS),
 'TIP_exact_zero':all(all(raw(i).get(g,0)==0 for g in helpers) for i in WEBIDS),'per_vertex':subset_rows(WEBIDS)})
r3canonical=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/R3_OWNERSHIP_MEMBERSHIP_CANONICAL.json')
frozen_graph=read(ROOT/R3['graph']['reference']['path'])
r3checks={'membership_canonical_hash':digest(r3canonical)==R3['membership']['membership_hash'],
 'labels_exact':LABEL=={int(i):label for i,label in r3canonical['vertex_label_pairs']},
 'domain962_exact':set(LABEL)==set(R3['graph']['vertex_ids']) and len(LABEL)==962,
 'domain_vertex_set_hash':digest(sorted(LABEL))==R3['graph']['vertex_set_sha256'],
 'graph_edge_set_hash':digest(R3['graph']['edge_ids'])==R3['graph']['edge_set_sha256'],
 'actual_graph_endpoint_IDs_exact':all(EDGES[int(eid)]==pair for eid,pair in frozen_graph['edge_endpoints'].items()),
 'graph_frozen_edge_IDs_exact':R3['graph']['edge_ids']==frozen_graph['edge_ids'],
 'no_leakage':not violations['illegal_cross_digit'],'all_domain_vectors_exact':all(W[i]==OLDW[i] for i in LABEL),
 'boundary_IDs_exact':{eid for eid,(i,j) in enumerate(EDGES) if i in LABEL and j in LABEL and LABEL[i]!=LABEL[j]}==set(R3['boundary']['edge_ids'])}
gate('FROZEN_R3_GUARD',all(r3checks.values()),r3checks)
audit('STATIC_SKIN_R3_GUARD_REVALIDATION_R1.json',{'status':'PASS' if all(r3checks.values()) else 'FAIL_CLOSED','authority':ref(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json'),
 'checks':r3checks,'guard_scope':'SIDE_AND_LEAKAGE_ONLY_WITH_APPROVED_FIRST_WEB21_EXCEPTION','Dijkstra_runs':0,'mincut_runs':0,'closure_runs':0,'sheet_runs':0,'label_to_one_hot_conversion':False,
 'per_vertex':[{'vertex_id':i,'frozen_label':LABEL[i],'allowed_groups':sorted(support(i)),'weights_exact_old_R2':W[i]==OLDW[i],'nonzero_groups':sorted(W[i])} for i in sorted(LABEL)]})
e5879=by_edge[5879];edge_pass=set(e5879['vertex_ids'])=={1551,3125} and all(W[i]==OLDW[i] for i in [1551,3125]) and e5879['R2_metrics']==prior_by_edge[5879]['R2_metrics'] and not fails(e5879['R2_metrics'])
gate('EDGE5879_EXACT_STATIC_MATCH',edge_pass)
audit('STATIC_SKIN_EDGE5879_REVALIDATION_R1.json',{'status':'PASS' if edge_pass else 'FAIL_CLOSED','edge':e5879,'exact_old_R2_metric':e5879['R2_metrics']==prior_by_edge[5879]['R2_metrics'],'endpoint_vectors':subset_rows([1551,3125]),'deformation_runs':0})


exec(compile((OUT/'diagnostics.py').read_text(encoding='utf-8'),str(OUT/'diagnostics.py'),'exec'),globals())
