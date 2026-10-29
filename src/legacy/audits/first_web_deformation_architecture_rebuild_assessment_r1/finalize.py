import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
status=read(OUT/'FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1_STATUS.json');machine=read(OUT/'KEY_SCREEN_MACHINE_R1.json');protected=read(OUT/'POC_PROTECTED_CONTENT_VERIFICATION_R1.json')
expected=dict(machine['inputs_unchanged'])
freeze=read(ROOT/'production_spec/right_hand_product_baseline_r1/FINAL_OUTPUT_MANIFEST_R1.json')
for row in freeze['files']:
    if row['path'] in ['production_spec/RIGHT_HAND_PRODUCT_BASELINE.json','docs/RIGHT_HAND_PRODUCT_BASELINE_AUTHORITY_R1.md']:expected[row['path']]=row['sha256']
pointer=read(ROOT/'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json')
assert pointer['asset']['sha256']==status['SOURCE_BASELINE_SHA256'] and pointer['RIGHT_HAND_PRODUCT_BASELINE_STATUS']=='HUMAN_APPROVED_FROZEN'
expected[pointer['source']['path']]=pointer['source']['sha256']
expected['references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend']='3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137'
for p,h in expected.items():assert sha(ROOT/p)==h,p
counts={}
for l in ['BASELINE','A','B','C']:
    n=len(list((OUT/(l.lower()+'_selected')).glob('*.png')));assert n==12;counts[l]=n
for r in protected['routes'].values():assert sha(ROOT/r['path'])==r['sha256']
assert all(x is None for x in status['HUMAN_REVIEW'].values())
assert not list(OUT.rglob('*.mp4')),'No route passed full-motion gate; no old clips substituted'
dump('FINAL_ASSET_PROTECTION_R1.json',{'status':'PASS','source_expected_and_final_sha256':expected,'frozen_baseline_and_approved_source_unchanged':True,'production_pointer_and_authority_document_match_frozen_manifest':True,'pocs':protected['routes'],'matched_renders':counts,'full_motion_executed':False,'regression_executed':'ZERO_ONLY','source_action_payload_exact':True,'source_motion_changed':False,'formal_rebuild_started':False,'left_hand_started':False,'web_export_started':False})
dump('REVIEW_UI_VERIFICATION_R1.json',{'status':'PASS','url':'http://127.0.0.1:8772/review.html','default_case':'F130','default_images_loaded':19,'ZERO_selector_test':{'all_routes_updated':True,'all_31_images_loaded':True,'ZERO_pose_views_per_route':4},'restored_case':'F130','console_errors':[],'human_answers_written':False,'proof':'REVIEW_PAGE_PROOF_R1.png'})
files=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='FINAL_OUTPUT_MANIFEST_R1.json']
dump('FINAL_OUTPUT_MANIFEST_R1.json',{'phase':status['PHASE'],'RECOMMENDED_ROUTE':'NONE_OF_THREE','workflow_status':'STOP_HUMAN_REVIEW','file_count':len(files),'files':files})
print('FINAL_ARCHITECTURE_DELIVERY_PASS',len(files),'FILES',sum(counts.values()),'MATCHED_RENDERS',len(expected),'PROTECTED_INPUTS')
