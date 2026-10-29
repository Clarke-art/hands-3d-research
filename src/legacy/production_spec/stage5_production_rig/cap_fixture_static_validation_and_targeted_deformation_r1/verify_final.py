from qualification_common import *
from PIL import Image
import math,re
status=read(OUT/(PHASE+'_STATUS.json'));matrix=read(OUT/'TARGETED_FIXTURE_MATRIX.json');machine=read(OUT/'TARGETED_DEFORMATION_MACHINE_EVIDENCE.json');debt=read(OUT/'INHERITED_DEBT_DEFORMATION_MAPPING.json');failure=read(OUT/'TARGETED_BLOCKING_FAILURE_CLASSIFICATION.json');visual=read(OUT/'VISUAL_EVIDENCE_MANIFEST.json');coords=read(OUT/'POSED_COORDINATE_EVIDENCE.json');live=read(OUT/'STATIC_LIVE_REOPEN_PAYLOAD.json')
assert status['TARGETED_DEFORMATION_VERDICT']=='FAIL_CLOSED_TARGETED_DEFORMATION'
assert status['CAP37_TARGETED_DEFORMATION']=='FAIL_CLOSED' and status['R2_INCREMENTAL_INTRODUCED_FAILURE_COUNT']==0 and status['CANDIDATE_INTRODUCED_FAILURE_COUNT']==3
assert sha(CAND)==EXPECTED and digest(live['weights'])==VECTOR
assert len(debt['rows'])==16 and len({r['debt_id'] for r in debt['rows']})==16
assert all(r['disposition']=='STATIC_QUALIFICATION_DEBT_WITHOUT_TRUE_DEFORMATION_FAILURE' and r['true_failure_count']==0 and not r['scope_expansion'] for r in debt['rows'])
assert len(failure['failures'])==3 and len({r['pose'] for r in failure['failures']})==2
for r in failure['failures']:
    assert r['classification']=='CANDIDATE_INTRODUCED_DEFORMATION_FAILURE' and not r['R2_incrementally_introduced']
    assert r['historical_comparison']['R1B_DONOR'] is None and r['historical_comparison']['R1E'] is None
    assert r['historical_comparison']['R1_CORRECTED_RIG']['class']==r['evidence']['class']=='CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION'
    assert r['evidence']['intersect'] and r['evidence']['depth_mm']>r['evidence']['local_edge_mm'] and r['evidence']['seg_mm']>0
assert len(matrix['poses'])==7 and [r['case_id'] for r in matrix['poses']][-1]=='IDX_MCP_45'
assert all(r['run_label']=='TARGETED_DIAGNOSTIC_PROBE' for r in matrix['poses'] if 'cmc_quaternion_local' in r)
allframes=0
for a,states in coords['positions_world_m'].items():
    assert len(states)==8
    for n,p in states.items():
        assert len(p)==3416 and all(len(v)==3 and all(math.isfinite(x) for x in v) for v in p)
        allframes+=1
assert len(visual['outputs'])==84
for r in visual['outputs']:
    with Image.open(OUT/r['file']) as im:
        assert im.size==(1500,1100);im.verify()
assert all(not any(r['core_clipped_vertex_counts'].values()) for r in visual['views'])
assert read(OUT/'REVIEW_UI_LOGIC_VERIFICATION.json')['status']=='PASS'
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=read(OUT/'FROZEN_HASHES_AFTER.json')
assert before==after==inventory()
for p,h in matrix['sources'].items():assert sha(ROOT/p)==h
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','TARGETED_FIXTURE_MATRIX.json','INHERITED_DEBT_DEFORMATION_MAPPING.json','TARGETED_DEFORMATION_MACHINE_EVIDENCE.json','CAP_FIXTURE_STATIC_CONFIRMATION.json','TARGETED_BLOCKING_FAILURE_CLASSIFICATION.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','HISTORICAL_HARNESS_REUSE_AND_SEMANTICS_AUDIT.json','VISUAL_EVIDENCE_MANIFEST.json','review.html']
assert all((OUT/n).is_file() for n in required)
page=(OUT/'review.html').read_text(encoding='utf-8')
for url in re.findall(r'href="([^"]+)"',page):assert (OUT/url).is_file(),url
record={'status':'PASS','qualification_result':'FAIL_CLOSED_TARGETED_DEFORMATION','verification_is_not_deformation_pass':True,'required_artifacts_present':True,'candidate_hash_and_vector_hash_verified':True,'whole_workspace_historical_files_unchanged':len(before),'all32_coordinate_frames_finite_and_3416_vertices':allframes,'PNG_decodes_verified':84,'all_comparison_core_vertices_in_frame':True,'debt_disposition_complete':16,'geometric_failure_observations_verified':3,'no_R2_incremental_introduced':True,'seven_original_pose_definitions_only':True,'all_new_files_only_in_qualification_directory':True,'production_save_calls':0,'Stage6_full_suite_runs':0,'R3_reruns':0,'true_cap_bounds_computed':0}
dump('INDEPENDENT_FINAL_ARTIFACT_VERIFICATION.json',record)
files={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST.json'}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST.json',{'files':files,'canonical_files_hash':digest(files)})
print(json.dumps(record,indent=2))
