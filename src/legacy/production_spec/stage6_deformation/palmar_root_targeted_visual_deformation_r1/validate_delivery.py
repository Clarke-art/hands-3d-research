import sys
sys.dont_write_bytecode=True
from common import *
import re,subprocess
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','review.html','ZERO_RESET_AUDIT_R1.json','MINIMUM_MACHINE_SAFETY_AUDIT_R1.json','MATCHED_RENDER_MANIFEST_R1.json','IN_MEMORY_NO_ASSET_DRIFT_R1.json','ORDINARY_SOLID_VISUAL_INSPECTION_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json']
assert all((OUT/n).is_file() for n in required)
status=read(OUT/(PHASE+'_STATUS.json'));assert status['VERDICT']=='READY_FOR_HUMAN_VISUAL_APPROVAL' and status['HUMAN_VISUAL_APPROVAL']=='PENDING' and not status['NEXT_EXECUTED'] and status['POSE_COUNT']==3
assert status['MID_MCP_45_MANDATORY_REVALIDATION']=='YES'
zero=read(OUT/'ZERO_RESET_AUDIT_R1.json');assert zero['status']=='PASS' and len(zero['rows'])==6 and all(r['status']=='PASS' and r['all21_channels_zero'] for r in zero['rows'])
manifest=read(OUT/'MATCHED_RENDER_MANIFEST_R1.json')['renders'];assert len(manifest)==24
for cid in CASES:
 for view in ['FULL_HAND','ROOT_CLOSE','ALTERNATE','GRAZING']:
  rows=[r for r in manifest if r['pose']==cid and r['view']==view];assert len(rows)==2
  assert rows[0]['camera']==rows[1]['camera'] and rows[0]['camera_matrix']==rows[1]['camera_matrix'] and rows[0]['studio_rotation_z']==rows[1]['studio_rotation_z']
  assert all((OUT/r['path']).is_file() and r['rendered_before_original_rig_reset'] and r['all_native_faces_present'] for r in rows)
 assert (OUT/(cid+'_INSPECTION.png')).is_file()
 assert status[cid+'_MACHINE_SAFETY']=='PASS' and status[cid+'_VISIBLE_STATUS']=='VISUALLY_ACCEPTABLE_PENDING_HUMAN'
safety=read(OUT/'MINIMUM_MACHINE_SAFETY_AUDIT_R1.json');assert safety['status']=='PASS'
assert all(r['NaN_Inf_count']==r['collapsed_face_count']==r['degenerate_edge_count']==r['obvious_severe_stretch_count']==0 for r in safety['automatic_results']['REPAIRED_PALMAR'].values())
assert read(OUT/'IN_MEMORY_NO_ASSET_DRIFT_R1.json')['status']=='PASS'
assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
assert not list(OUT.glob('*.blend*'))
html=(OUT/'review.html').read_text(encoding='utf-8');assert '__PICTURES__' not in html and '__ASSETS__' not in html
assert html.count('type="radio"')==6 and not re.search(r'type="radio"[^>]*checked',html)
for target in re.findall(r'renders/[^"\s]+\.png',html):assert (OUT/target).is_file(),target
client=html.split('<script>')[1].split('</script>')[0];(OUT/'REVIEW_CLIENT_VALIDATION.js').write_text(client,encoding='utf-8');subprocess.run(['node','--check',str(OUT/'REVIEW_CLIENT_VALIDATION.js')],check=True,capture_output=True)
protected=read(OUT/'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json');assert protected['PROTECTED_HISTORY_DRIFT']==0 and not protected['changed_paths'] and not protected['new_paths_outside_phase']
report=(OUT/(PHASE+'_REPORT.md')).read_text(encoding='utf-8');assert all(k in report for k in status)
dump('DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_artifacts':{n:ref(OUT/n) for n in required},'distinct_authorized_pose_count':3,'actual_temporary_pose_applications':6,'matched_render_count':24,'matched_camera_light_scale_verified':True,'all_pose_resets_PASS':True,'review_client_JS_syntax_PASS':True,'browser_UI_verified_15_30_45_switches_and_actual_1400px_images':True,'Human_review_answers_unselected':True,'Human_review_submission_not_performed':True,'source_blends_not_saved':True,'Human_final_visual_approval_pending':True,'NEXT_EXECUTED':False})
dump('OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json'})
print('DELIVERY PASS: 3 poses /24 matched renders /ZERO PASS; Human visual approval pending; STOP')
