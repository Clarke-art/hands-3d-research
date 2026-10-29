"""Independently verify delivery completeness and recompute metrics from native entries."""
import sys
sys.dont_write_bytecode=True
from common import *
import math
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json',
 'STATIC_SKIN_WEIGHT_PAYLOAD_AUDIT_R1.json','STATIC_SKIN_FULL_MESH_MATH_AUDIT_R1.json',
 'STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json','STATIC_SKIN_OLD_R2_METRIC_EQUIVALENCE_R1.json',
 'STATIC_SKIN_CAP37_REVALIDATION_R1.json','STATIC_SKIN_OLD_CAP9_REVALIDATION_R1.json',
 'STATIC_SKIN_FIRST_WEB_REVALIDATION_R1.json','STATIC_SKIN_R3_GUARD_REVALIDATION_R1.json',
 'STATIC_SKIN_EDGE5879_REVALIDATION_R1.json','STATIC_SKIN_INHERITED_DEBT_REVALIDATION_R1.json',
 'DONOR_TRANSFER54_SKIN_COMPATIBILITY_DIAGNOSTIC_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json']
checks={'all14_required_outputs_exist':all((OUT/n).is_file() for n in required)}
s=read(OUT/(PHASE+'_STATUS.json'))
n=read(OUT/'CURRENT_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json')
o=read(OUT/'OLD_R2_CLEAN_REOPEN_NATIVE_PAYLOAD_R1.json')
cont=read(OUT/'STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json')
names=n['group_order']
vectors=[{names[g]:value for g,value in entries} for entries in n['protected']['weights_exact_including_zero']]
checks['3416_raw_vectors_independent_math']=len(vectors)==3416 and all(abs(sum(v.values())-1)<=1e-5 and all(math.isfinite(x) and x>=0 for x in v.values()) and sum(x>0 for x in v.values())<=4 for v in vectors)
checks['authority_hash_from_native_entries']=digest([{g:v for g,v in row.items() if v>0} for row in vectors])==WEIGHT_HASH
edges=[e[1] for e in n['protected']['mesh']['edges']]
matched=0;blocked=[]
for row in cont['all_checked_edges']:
 eid=row['edge_id'];i,j=edges[eid]
 delta={g:abs(vectors[i].get(g,0)-vectors[j].get(g,0)) for g in sorted(set(vectors[i])|set(vectors[j]))}
 m={'L_inf':max(delta.values(),default=0),'L1':sum(delta.values()),'per_group':delta}
 if m==row['R2_metrics'] and row['vertex_ids']==[i,j]:matched+=1
 if m['L_inf']>.5 or m['L1']>1:blocked.append(eid)
checks['2127_independent_metrics_exact']=matched==s['EDGE_METRIC_EXACT_MATCH_COUNT']==2127
checks['all16_debts_exact']=blocked==read(OUT/'STATIC_SKIN_INHERITED_DEBT_REVALIDATION_R1.json')['edge_ids'] and len(blocked)==16
checks['old_R2_full_native_entries_exact']=n['protected']['weights_exact_including_zero']==o['protected']['weights_exact_including_zero']
binary=b''.join(struct.pack('<16f',*v) for v in n['dense_float32_rows'])
checks['dense_float32_binary_export_exact']=binary==(OUT/'STATIC_SKIN_DENSE_FLOAT32_PAYLOAD_READONLY_R1.bin').read_bytes()
checks['required_audits_PASS']=all(read(OUT/f).get('status','').startswith('PASS') for f in required if f.endswith('.json') and f!=PHASE+'_STATUS.json')
checks['PASS_verdict_and_STOP']=s['VERDICT']=='PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED' and s['STOP'] and not s['NEXT_EXECUTED']
checks['execution_limits_zero']=all(s[k]==0 for k in ['POSE_RUNS','STAGE6_RUNS','WEIGHT_WRITES','BLEND_SAVES','R3_RUNS','SOLVER_RUNS'])
checks['all_blend_input_hashes_retained']=all(sha(p)==EXPECTED[k] for k,p in FILES.items())
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory()
checks['all4020_preexisting_files_exact']=before==after and len(before)==4020
manifest=read(OUT/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json')
checks['manifest_all_files_exact']=all(sha(OUT/f)==h for f,h in manifest['files'].items()) and digest(manifest['files'])==manifest['canonical_files_hash']
checks['manifest_complete']=set(manifest['files'])=={p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file() and p.name not in manifest['excludes']}
output={'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED_DELIVERY_VALIDATION','checks':checks,'required_outputs':required,
 'independently_recomputed_edge_count':matched,'independently_recomputed_absolute_debt_ids':blocked,'history_drift':0 if before==after else 1,
 'manifest_reference':ref(OUT/'OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'),'STOP':True}
dump('FINAL_DELIVERY_VALIDATION_R1.json',output)
print(json.dumps(output,ensure_ascii=False,indent=2))
assert all(checks.values()),output
