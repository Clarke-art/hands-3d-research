"""Independent plan consistency / output hash / frozen-state checks."""
import json,hashlib,math,re,subprocess
from collections import Counter,deque
from pathlib import Path
from snapshot import OUT,ROOT,sha,inventory
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
S=read('CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_STATUS.json')
E=read('SKIN_REBUILD_ENVELOPE_R1.json');R=read('R1B_SAFE_WEIGHT_REUSE_SET_R1.json');C=read('CAP37_SKIN_DRIVER_AUTHORITY_R1.json')
W=read('FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json');O=read('OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json');I=read('CORRECTED_RIG_SKIN_FIELD_IMPACT_AUDIT_R1.json')
D=read('SAVED_RIG_AND_SKIN_EVIDENCE_R1.json')['sources'];A=json.loads((ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json').read_text(encoding='utf-8'))
assert A['graph']['vertex_count']==len(A['graph']['vertex_ids'])==962
assert A['graph']['edge_count']==len(A['graph']['edge_ids'])==1881
assert digest(A)=='361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0'
for f in ['CAP_SKIN_DRIVER_AUTHORITY_R1.json','CAP37_SKIN_DRIVER_AUTHORITY_R1.json','OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json',
          'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json','SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json','R1B_SAFE_WEIGHT_REUSE_SET_R1.json',
          'SKIN_REBUILD_ENVELOPE_R1.json','EDGE5879_REBUILD_SCOPE_R1.json']:
    assert read(f)['status']=='RESOLVED'
sets={k:set(R[k]) for k in ['SAFE_REUSE','TARGETED_REVALIDATION','REBUILD_REQUIRED','UNRESOLVED']}
assert sum(len(v) for v in sets.values())==3416 and set.union(*sets.values())==set(range(3416))
for a in sets:
    for b in sets:
        if a!=b:assert sets[a].isdisjoint(sets[b])
assert not sets['UNRESOLVED']
assert set(E['vertex_ids'])==sets['TARGETED_REVALIDATION']|sets['REBUILD_REQUIRED']
assert S['R1B_safe_reuse_count']==len(sets['SAFE_REUSE'])==2401
assert S['targeted_revalidation_count']==len(sets['TARGETED_REVALIDATION'])==771
assert S['rebuild_required_count']==len(sets['REBUILD_REQUIRED'])==244
assert len(E['vertex_ids'])==E['total_count']==S['rebuild_envelope_total_count']==1015
adj={i:set() for i in range(3416)}
for i,j in D['R1B']['edges']:adj[i].add(j);adj[j].add(i)
def bounded(seed,depth):
    # Independent bounded hop check for engineering skin neighborhoods only.
    result={i:0 for i in seed};q=deque(sorted(seed))
    while q:
        i=q.popleft()
        if result[i]==depth:continue
        for j in sorted(adj[i]):
            if j not in result:result[j]=result[i]+1;q.append(j)
    return set(result)
check_components={
 'CAP37_CONTINUITY_2RING':bounded(A['cap37_preservation']['vertex_ids'],2),
 'OLD_CAP9_INDEX_CONTINUITY_2RING':bounded(A['old_cap9']['vertex_ids'],2),
 'FIRST_WEB_CONTINUITY_2RING':bounded(A['FIRST_WEB21']['membership_vertex_ids'],2),
 'EDGE5879_CONTINUITY_2RING':bounded([1551,3125],2),
 'FRESH_R3_BOUNDARY_TRANSITION_2RING':bounded({v for row in A['boundary']['edge_records'] for v in row['vertex_ids']},2)}
for k,v in check_components.items():assert set(E['overlapping_components'][k]['vertex_ids'])==v and v<=set(E['vertex_ids'])
assert len(check_components['FRESH_R3_BOUNDARY_TRANSITION_2RING'])==S['fresh_R3_boundary_transition_count']==126
assert set(A['cap37_preservation']['vertex_ids'])<=sets['REBUILD_REQUIRED']
assert set(A['old_cap9']['vertex_ids'])<=sets['REBUILD_REQUIRED']
assert {1551,3125}<=sets['REBUILD_REQUIRED']
assert set(W['membership']['vertex_ids'])==set(A['FIRST_WEB21']['membership_vertex_ids']) and not W['THUMB_IP_allowed']
assert not set(W['allowed_deform_groups'])&{'THUMB_IP_R','THUMB_TIP_R'}
assert len(C['per_vertex_surface_evidence'])==37 and C['geometry_evidence']['IP_segment_projection_count']==37
assert all(x['corrected_thumb_projection']['nearest_segment']==2 for x in C['per_vertex_surface_evidence'])
assert C['rule']['h_mm']==5*3.888205 and not C['rule']['weights_evaluated_or_generated_this_round']
assert len(O['per_vertex_evidence'])==9
for x in O['per_vertex_evidence']:
    assert x['witness_count']>0 and not x['one_hot_MCP_independently_supported']
    for w in x['clean_INDEX_witnesses']:
        j=w['vertex_id'];assert j in bounded([x['vertex_id']],2)
        assert w['vector']==D['R1B']['weights'][j] and w['vector_sha256']==digest(w['vector'])
        assert A['membership']['vertex_labels'][str(j)]=='INDEX'
safeproof={p['vertex_id']:p for p in R['safe_reuse_proof']}
for i in sets['SAFE_REUSE']:
    assert safeproof[i]['vector_sha256']==digest(D['R1B']['weights'][i])
    assert D['R1B']['weights'][i].get('THUMB_IP_R',0)==0
    for g,w in D['R1B']['weights'][i].items():
        assert g in D['CORRECTED']['bones'] and D['CORRECTED']['bones'][g]['use_deform']
        assert D['CORRECTED']['bones'][g]==D['R2A']['bones'][g]
assert I['material_skin_field_affected_vertex_count']==S['corrected_rig_affected_vertex_count']==163
assert len(I['per_vertex'])==3416
assert {r['vertex_id'] for r in I['per_vertex'] if r['material_skin_field_change']}==set(I['material_skin_field_affected_vertex_ids'])
assert all(r['consumed_field_change_reasons'] for r in I['per_vertex'] if r['material_skin_field_change'])
assert all(not r['material_skin_field_change'] for r in I['per_vertex'] if r['normalized_denominator_only_change'])
B=read('SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1.json');BH=digest(B)
assert sha(OUT/'SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1_CANONICAL.json')==BH==read('SKIN_AUTHORITY_PROPOSAL_HASH_R1.json')['proposal_bundle_hash']
for f,h in B['proposal_files'].items():assert sha(OUT/f)==h
assert B['R3_authority_hash']=='361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0'
for p,h in read('INPUT_AUTHORITY_VERIFICATION_R1.json')['input_file_sha256'].items():assert sha(ROOT/p)==h
HTML=(OUT/'SKIN_AUTHORITY_RECONCILIATION_HUMAN_REVIEW.html').read_text(encoding='utf-8')
vis=json.loads(re.search(r'<script id="evidence" type="application/json">(.*?)</script>',HTML,re.S).group(1))
assert vis['bundle_hash']==BH and vis['packet']==B
assert Counter(vis['classifications'])=={k:len(v) for k,v in sets.items() if v}
assert ' checked' not in re.search(r'const questions=.*?const validationMode',HTML,re.S).group(0)
# Update pure-response test binding to final bundle, never export a formal response.
p=OUT/'verify_response_logic.cjs';js=p.read_text(encoding='utf-8')
js=re.sub(r'const D=.*?;\nconst questions=',lambda _: 'const D='+json.dumps({'packet':B,'bundle_hash':BH})+';\nconst questions=',js,count=1,flags=re.S)
p.write_text(js,encoding='utf-8');subprocess.run(['node',str(p)],check=True)
assert read('RESPONSE_LOGIC_VERIFICATION_R1.json')['proposal_bundle_hash']==BH
QA=read('BROWSER_QA_VERIFICATION_R1.json');assert QA['status']=='PASS' and QA['proposal_bundle_hash']==BH
assert QA['all_yes_QA_export_disabled'] and not QA['formal_Human_response_created']
assert len(QA['views_verified'])==8
for k in ['BLEND_FILES_WRITTEN','weights_generated','weights_written','R3_reruns','Stage6_runs','WEIGHT_DELTA','GEOMETRY_DELTA','TOPOLOGY_DELTA','BONE_DELTA','JOINT_DELTA']:assert S[k]==0
assert S['Human_Review_generated'] and S['STOP'] and S['NEXT']=='HUMAN_SKIN_AUTHORITY_RECONCILIATION_APPROVAL'
before=read('FROZEN_HASHES_BEFORE.json');after=inventory()
assert before==after,{'missing':list(set(before)-set(after)),'added':list(set(after)-set(before)),'changed':[p for p in before if p in after and before[p]!=after[p]]}
dump('FROZEN_HASHES_AFTER.json',after)
fv={'status':'PASS','protected_file_count':len(before),'before_equals_after':True,'changed_files':[],
    'all_preexisting_workspace_files_protected':True,'external_formal_Human_responses_protected':True,
    'Stage4_corrected_rig_cap37_R3_R1B_C_D_E_Stage6_Human_response_unchanged':True,
    'new_blend_files':[],'new_weight_vectors':0}
dump('FROZEN_HASH_VERIFICATION_R1.json',fv)
dump('OUTPUT_VERIFICATION_R1.json',{'status':'PASS','authority_proposals':'ALL_RESOLVED_PENDING_HUMAN_APPROVAL',
 'all_3416_vertices_disjointly_classified':True,'safe_reuse_exact_vectors_and_unchanged_driver_slots':True,
 'independent_bounded_neighborhood_checks':True,'old_cap9_clean_INDEX_witnesses_verified':True,
 'cap37_saved_surface_and_driver_geometry_verified':True,'no_candidate_vectors_or_deformation_pass_claimed':True,
 'proposal_bundle_hash':BH,'response_logic_cases':24,'browser_QA_pass':True,'frozen_before_equals_after':True,
 'BLEND_FILES_WRITTEN':0,'weights_written':0,'R3_reruns':0,'Stage6_runs':0,'NEXT':S['NEXT'],'STOP':True})
report=OUT/'CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md'
report.write_text(report.read_text(encoding='utf-8')+f'\n## 输出核验\n\n3416点分类覆盖与互斥、safe vector hashes/实际driver slots、5类bounded skin neighbourhood、old9 INDEX witnesses、cap37 projection、proposal bundle及24个response logic guard cases通过。8个浏览器静态视图通过，QA全YES无法导出或成为Human审批，正式页面恢复空白。{len(before)}个preexisting workspace/external formal response files before==after。BLEND_FILES_WRITTEN=0；weights written=0；R3 reruns=0；Stage6 runs=0。\n',encoding='utf-8')
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{'status':'PASS','files':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'}})
print(json.dumps({'verification':'PASS','protected_files':len(before),'safe':len(sets['SAFE_REUSE']),'targeted':len(sets['TARGETED_REVALIDATION']),'rebuild':len(sets['REBUILD_REQUIRED']),'envelope':len(E['vertex_ids']),'proposal_bundle_hash':BH,'STOP':True},indent=2))
