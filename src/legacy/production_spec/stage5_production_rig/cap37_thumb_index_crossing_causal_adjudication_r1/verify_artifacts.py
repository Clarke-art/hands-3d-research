import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from causal_common import *
from PIL import Image
v=read(OUT/'VISUAL_EVIDENCE_MANIFEST.json');s=read(OUT/(PHASE+'_STATUS.json'));sw=read(OUT/'CROSSING_ONSET_SWEEP.json')
assert len(v['outputs'])==66
required=['full_hand','thumb_index_close','surface_solid','wire_overlay','isolated_pair','section']
for p in PAIRS:
 for a in ASSETS:
  for style in required:
   assert len([r for r in v['outputs'] if r['pair']==p['id'] and r['asset']==a and r['style']==style])==1
for r in v['outputs']:
 with Image.open(OUT/r['file']) as im:assert im.size==(1500,1100);im.load()
for a,poses in sw['results'].items():
 assert set(poses)=={'TH_IP_30','IDX_MCP_45'}
 for pose,d in poses.items():
  assert d['local_X_sign']==-1 and d['fixed_step_deg']==.5
  expected={p['id'] for p in PAIRS if p['pose']==pose};assert set(d['onsets'])==expected
  assert all(set(row['pairs'])==expected and 0<=row['angle_deg']<=d['max_angle_deg'] for row in d['fixed_grid']+d['additional_refinement_samples'])
assert s['counts']['R2_INCREMENTAL_INTRODUCED_PAIR_COUNT']==0 and s['counts']['VALIDATOR_SEMANTIC_ADJUDICATION_COUNT']==3
assert s['counts']['VISIBLE_TEACHING_DEFECT_COUNT'] is None and s['NEXT']=='READY_FOR_HUMAN_CAUSAL_ADJUDICATION'
assert read(OUT/'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json')['status']=='PASS'
assert read(OUT/'REVIEW_UI_VERIFICATION.json')['status']=='PASS'
before=read(OUT/'FROZEN_HASHES_BEFORE.json');assert inventory()==before
hashes={p.name:sha(p) for p in OUT.glob('*.json') if p.name not in ['FINAL_ARTIFACT_VERIFICATION.json','OUTPUT_FILE_HASHES.json']}
hashes.update({p.name:sha(p) for p in OUT.glob('*.md')});hashes['review.html']=sha(OUT/'review.html');hashes.update({r['file']:sha(OUT/r['file']) for r in v['outputs']})
dump('OUTPUT_FILE_HASHES.json',hashes)
dump('FINAL_ARTIFACT_VERIFICATION.json',{'status':'PASS','PNG_count':66,'all_PNG_decoded':True,'required_matched_view_coverage':True,'pair_and_pose_scope_exact':True,'historical_hashes_exact':True,'R2_clean_reopen_and_hash_verification':True,'review_selector_and_zoom_JS_verified':True,'visibility_human_adjudication_not_fabricated':True,'NEXT':s['NEXT'],'STOP':'HUMAN_REVIEW','new_production_artifacts':[]})
print('Final artifact verification PASS; 66 PNG, exact three-pair scope, frozen history.')
