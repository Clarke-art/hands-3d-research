import sys
sys.dont_write_bytecode=True
from pathlib import Path
OUT=Path(__file__).resolve().parent
S5=OUT.parent
PRE=S5/'static_skin_compatibility_revalidation_after_donor_transfer_r1'
s=(PRE/'common.py').read_text(encoding='utf-8').split("if __name__=='__main__':")[0]
s=s.replace("PROP = S5 / 'geometry_propagation_after_donor_transfer_r1'", "PROP = S5 / 'geometry_propagation_after_palmar_donor_restoration_r1'\nPRE = S5 / 'static_skin_compatibility_revalidation_after_donor_transfer_r1'\nAPPDIR = ROOT / 'production_spec/stage4_blender/stage4c_donor_transfer_palmar_root_r1'\nJOINTDIR = S5 / 'joint_surface_rest_zero_bind_revalidation_after_palmar_donor_restoration_r1'\nIDS16 = set(range(3348,3364))")
s=s.replace('STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_DONOR_TRANSFER_R1','STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1')
a=s.index('FILES =');b=s.index('def read')
s=s[:a]+'''FILES = {
 'CURRENT': PROP/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend',
 'OLD_R2': S5/'geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend',
 'CORRECTED_RIG': S5/'human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend',
 'STAGE4': APPDIR/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_PALMAR_ROOT_R1.blend',
 'STAGE5A': PROP/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_PALMAR_ROOT_R1.blend'}
EXPECTED = {'CURRENT':'90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa','OLD_R2':'d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d','CORRECTED_RIG':'5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe','STAGE4':'0c1831042151a40f87f3779b97ece94cfc29a7831babfa1dda64c9ac0f4ae9c6','STAGE5A':'b7a4fe408ba979ee41f72b1a62e25b7ce292da42da561dc47bbc65b9475d6b8e'}
REQUEST = Path('<USER_HOME>/.codex/attachments/68e7aeec-a20d-45fc-b39f-cbfa68fdbf27/已粘贴的文本.txt')
'''+s[b:]
(OUT/'common.py').write_text(s,encoding='utf-8')
sys.path.insert(0,str(OUT))
from common import *
dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
actual={k:ref(p) for k,p in FILES.items()};assert all(v['sha256']==EXPECTED[k] for k,v in actual.items())
prerequisites={
 'application':APPDIR/'PALMAR_DIGIT_ROOT_DONOR_RESTORATION_APPLICATION_R1_STATUS.json',
 'propagation':PROP/'STAGE5_GEOMETRY_PROPAGATION_AFTER_PALMAR_DONOR_RESTORATION_R1_STATUS.json',
 'joint':JOINTDIR/'JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1_STATUS.json',
 'pre_palmar_static':PRE/'STATIC_SKIN_COMPATIBILITY_REVALIDATION_AFTER_DONOR_TRANSFER_R1_STATUS.json'}
assert 'PASS_APPLIED_TO_NEW_STAGE4C_DERIVED_REVISION' in read(prerequisites['application']).values()
assert 'PASS_GEOMETRY_PROPAGATED_WITH_RIG_AND_WEIGHTS_FROZEN' in read(prerequisites['propagation']).values()
assert read(prerequisites['joint'])['VERDICT']=='PASS_JOINT_REST_ZERO_BIND_REQUALIFIED'
assert read(prerequisites['pre_palmar_static'])['VERDICT']=='PASS_STATIC_SKIN_COMPATIBILITY_REQUALIFIED'
(OUT/'USER_PHASE_SCOPE_ORIGINAL.txt').write_bytes(REQUEST.read_bytes())
dump('PALMAR_STATIC_SKIN_INPUT_HASH_AUDIT_R1.json',{'status':'PASS','inputs':actual,'prerequisites':{k:ref(p) for k,p in prerequisites.items()},'weight_authority':WEIGHT_HASH,'user_request':ref(REQUEST),'read_only':True})
ex=(PRE/'extract_readonly.py').read_text(encoding='utf-8')
ex=ex.replace("source=S5/'joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1/payload.py'", "source=S5/'geometry_propagation_after_donor_transfer_r1/payload.py'")
ex=ex.replace('data=snapshot()',"data=snapshot()\n data['protected']['object']['custom_properties']=props(bpy.data.objects[data['object_name']])")
(OUT/'extract_readonly.py').write_text(ex,encoding='utf-8')
# Reuse only the approved acceptance code up to edge5879; geometry-specific code is supplied locally.
r=(PRE/'revalidate.py').read_text(encoding='utf-8').split('# Diagnose distances only')[0]
r=r.replace("PROP/'STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json'", "PROP/'PALMAR_STAGE5B_R2_GEOMETRY_PROPAGATION_AUDIT_R1.json'")
r=r.replace("PRIOR=read(R2DIR/'R2_CONTINUITY_STATIC_AUDIT.json')", "ORIGIN=read(R2DIR/'R2_CONTINUITY_STATIC_AUDIT.json')\nPRE_FORMAL=read(PRE/'STATIC_SKIN_CONTINUITY_EDGE_REVALIDATION_R1.json')\nPRIOR={**ORIGIN,'all_checked_edges':PRE_FORMAL['all_checked_edges']}")
r=r.replace(" if not ok: minimal_blockers.append({'gate':name,'detail':detail})", " if not ok:\n  minimal_blockers.append({'gate':name,'detail':detail})\n  dump(PHASE+'_STATUS.json',{'VERDICT':'FAIL_CLOSED_STATIC_SKIN_COMPATIBILITY_AFTER_PALMAR','minimal_blocker':minimal_blockers[0],'STOP':True})\n  (OUT/(PHASE+'_REPORT.md')).write_text('FAIL_CLOSED_STATIC_SKIN_COMPATIBILITY_AFTER_PALMAR\\n\\n'+json.dumps(minimal_blockers[0],ensure_ascii=False,indent=2)+'\\nNo repair. STOP.\\n',encoding='utf-8')\n  raise SystemExit('FAIL CLOSED: '+name)")
r=r.replace("edge_identity=topology_exact and checked==set(prior_by_edge) and len(checked)==2127", "edge_identity=topology_exact and checked==set(prior_by_edge)=={r['edge_id'] for r in ORIGIN['all_checked_edges']} and len(checked)==PRE_FORMAL['checked_edge_count']==2127")
r=r.replace("'metric_exact_old_R2':actual==old_metric and saved is not None and actual==saved['R2_metrics']", "'metric_exact_old_R2':actual==old_metric and saved is not None and actual==saved['R2_metrics'] and actual==next(z for z in ORIGIN['all_checked_edges'] if z['edge_id']==eid)['R2_metrics']")
r+='\nexec(compile((OUT/\'diagnostics.py\').read_text(encoding=\'utf-8\'),str(OUT/\'diagnostics.py\'),\'exec\'),globals())\n'
(OUT/'revalidate.py').write_text(r,encoding='utf-8')
dump('ACCEPTANCE_CODE_REUSE_PROVENANCE_R1.json',{'source':ref(PRE/'revalidate.py'),'strategy':'Reuse existing acceptance blocks only, with pre-palmar formal comparator and fail-closed STOP; geometry diagnostics kept local','solver_imports_or_top_level_execution':False,'original_metric_validator_sources':[ref(R2DIR/'common.py'),ref(R2DIR/'audit_and_report.py')],'normalization_threshold_source':ref(AUTH/'SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json')})
print('All five input hashes and four prerequisite verdicts PASS; protected baseline frozen.')
