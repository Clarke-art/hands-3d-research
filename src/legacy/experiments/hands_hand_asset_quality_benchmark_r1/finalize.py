from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(r'<HANDS_ROOT>');OUT=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
before=json.loads((OUT/'PROTECTED_SHA256_BEFORE.json').read_text(encoding='utf8'));rows=[]
for r in before:
 p=Path(r['path']);assert p.is_relative_to(ROOT) and p.resolve().is_relative_to(ROOT)
 h=sha(p);rows.append(dict(path=str(p),before=r['sha256'],after=h,unchanged=h==r['sha256']))
assert all(r['unchanged'] for r in rows)
download=json.loads((OUT/'ASSET_DOWNLOAD_RECEIPT.json').read_text());h=sha(OUT/'sources/hand-posable.glb');assert h==download['sha256']
save('PROTECTED_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,count=len(rows),write_scope=str(OUT),independent_piano_access=False,formal_asset_replaced=False,rebind_performed=False,source_files=rows,download_original=dict(path='sources/hand-posable.glb',before=download['sha256'],after=h,unchanged=True)))
save('CANDIDATE_SOURCE_AND_LICENSE.json',dict(accessed_date='2026-10-16',actual_candidates=[dict(id='MAKEHUMAN',name='Posable anatomical right hand',publisher_and_derivative_author='Innerscene',upstream_authors='MakeHuman Team / MakeHuman Community / MPFB contributors',source_page='https://www.innerscene.com/tools/library/3d-parts/posable-anatomical-right-hand-f6098b4f',download_original=download,license='CC0-1.0',commercial_use=True,modification=True,redistribution_of_original_or_derived_mesh=True,attribution_required=False,endorsement_granted=False,warranty=False,source_page_evidence='sources/innerscene.html',library_terms='sources/library_terms.html',upstream_license_evidence=['sources/makehuman_license.html','sources/mpfb_license.md','sources/mpfb_assets_license.md'],legalcode='sources/cc0.html',upstream_license_url='https://static.makehumancommunity.org/about/license.html',material_images_in_glb=0,source_metadata_skin_name='jartur69_middleage_slavic_male_with_genitals_and_beard',skin_license_primary_url='https://static.makehumancommunity.org/assets/assetpacks/skins02.html',raw_glb_sha256=h,native_reflection_unresolved=True)],not_counted_as_candidates=[dict(name='Blender official Hand - Realistic',author='Dan Ulrich / Blender Studio',license='CC0-1.0',source='https://www.blender.org/download/demo-files/',reason='Same source ancestry as current C1, not an independent upgrade',local_primary_evidence='sources/blender_official.html',ancestry_evidence=str(ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_feasibility_r1/PALMAR_ROOT_SOURCE_ANCESTRY_R1.json')),dict(name='Hands Rigged',author='SparrowHawk',license_shown='CC0',source='https://blendswap.com/blend/22269',download_page='https://blendswap.com/blend/22269/download',reason='Sign-in required; file not acquired. Actual mesh/rig quality NOT_TESTED',local_evidence=['sources/blendswap.html','sources/blendswap_download.html'])]))
result=dict(task='HANDS_HAND_ASSET_QUALITY_BENCHMARK_R1',candidate_evaluations=[dict(candidate='MAKEHUMAN',classification='NO_MEANINGFUL_QUALITY_ADVANTAGE',index_proximal='Some overhead contour improvement; no reliable cross-view clear superiority',first_web='No clear multi-view improvement; faceting remains',native_three_static_poses='TESTED_WITH_COMPARABILITY_LIMITS',native_right_handedness='UNRESOLVED_REFLECTED_SOURCE_TRANSFORM',rig_actions_contact_compatibility='NOT_TESTED',human_approved=False)],overall_classification='NO_MEANINGFUL_QUALITY_ADVANTAGE',recommend_asset_adaptation_trial=False,recommend_formal_replacement=False,protected_inputs_unchanged=len(rows),independent_piano_access=False,status='STOP — HUMAN REVIEW',test_scope={'static_neutral_index_flex_thumb_spread':'EXECUTED','same_group_camera_scale_lighting':'VERIFIED','textures_or_AI_hands_used':False,'contact_and_collision':'NOT_TESTED','self_intersection':'NOT_TESTED','full_range_and_opposition':'NOT_TESTED','midi_and_23_note_motion_compatibility':'NOT_TESTED'})
result['pose_comparability']={'nominal_index_targets_deg':[20,35,15],'nominal_thumb_target_deg':15,'actual_local_C1_index_deg':[20,35,15],'actual_local_candidate_index_deg':[19.25003,35.82194,15.26586],'actual_local_C1_thumb_deg':15,'actual_local_candidate_thumb_deg':16.85756,'exact_angle_or_final_joint_pose_match':False}
settings=json.loads((OUT/'RENDER_SETTINGS.json').read_text(encoding='utf8'));settings['pose_comparability']='Independent native binds and transforms; same nominal target increments, different realized local angles. NOT anatomically identical poses; see RESULT.pose_comparability. No transferred animation.';save('RENDER_SETTINGS.json',settings)
save('RESULT.json',result)
panels=['HAND_ASSET_OVERALL_COMPARISON.png','INDEX_PROXIMAL_COMPARISON.png','FIRST_WEB_COMPARISON.png','POSE_DEFORMATION_COMPARISON.png']
qa=[]
for name in panels:
 p=OUT/name
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:qa.append(dict(file=name,resolution=list(im.size),bytes=p.stat().st_size,sha256=sha(p),visual_review='Viewed actual final panel; labels and footnotes checked',source='Blender actual evaluated meshes; PIL layout/labels only'))
save('DELIVERY_VISUAL_QA.json',qa)
artifacts=panels+['HAND_ASSET_BENCHMARK_REVIEW.blend','HAND_ASSET_BENCHMARK_STATIC.blend','CANDIDATE_IMPORTED_UNALTERED.blend','TECHNICAL_REPORT.md','HUMAN_REVIEW.md','CANDIDATE_SOURCE_AND_LICENSE.json','PROTECTED_SHA256_BEFORE_AFTER.json','RESULT.json','DELIVERY_VISUAL_QA.json','ALIGNMENT_AND_POSE_RECEIPT.json','RENDER_MANIFEST.json','CANDIDATE_RIG_AND_SKIN_RECEIPT.json','GEOMETRY_AND_TEST_SCOPE.json','sources/hand-posable.glb']
save('DELIVERY_SHA256.json',[dict(path=str(OUT/n),bytes=(OUT/n).stat().st_size,sha256=sha(OUT/n)) for n in artifacts])
print('FINAL',len(rows),'PROTECTED_UNCHANGED;',len(artifacts),'DELIVERABLES_VERIFIED; STOP — HUMAN REVIEW')
