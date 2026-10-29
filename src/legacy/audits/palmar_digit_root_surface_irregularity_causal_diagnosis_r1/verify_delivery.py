import sys
sys.dont_write_bytecode=True
from common import *
from html.parser import HTMLParser
from urllib.parse import unquote
from PIL import Image
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=inventory();changed=[k for k,h in before.items() if after.get(k)!=h];added=[k for k in after if k not in before]
dump('FROZEN_HASHES_AFTER.json',after)
response=read(OUT/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json');assert response['sha256_before']==sha(RESPONSE)
verification={'status':'PASS' if not changed and not added else 'FAIL','preexisting_workspace_file_count':len(before),'changed_or_missing_files':changed,'new_files_outside_diagnostic_directory':added,'PRODUCTION_DRIFT':len(changed),'human_response_external_sha256_before':response['sha256_before'],'human_response_external_sha256_after':sha(RESPONSE),'human_response_byte_preserved':response['sha256_before']==sha(RESPONSE),'current9_hold':'HOLD_NOT_CLOSED','production_write_counts':{'geometry':0,'weights':0,'normals':0,'rig':0,'joint':0,'material':0,'modifier':0},'qualification_status_files_byte_preserved':True,'human_closures_created':0,'approval_receipts_created':0,'active_human_authority_writes':0,'FULL42_RERUN':0,'micro_pose_probe_count':0,'STAGE6B_RUNS':0,'PRODUCTION_PROMOTION':'NO'}
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',verification)
assert not changed and not added and verification['human_response_byte_preserved']
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','HUMAN_PALMAR_IRREGULARITY_VISUAL_TARGET_R1.json','PALMAR_DIGIT_ROOT_IRREGULARITY_ROI_R1.json','PALMAR_IRREGULARITY_LINEAGE_COMPARISON_R1.json','PALMAR_IRREGULARITY_GEOMETRY_VS_SHADING_R1.json','PALMAR_IRREGULARITY_RAW_ZERO_POSED_COMPARISON_R1.json','PALMAR_IRREGULARITY_GEOMETRY_METRICS_R1.json','PALMAR_IRREGULARITY_SKIN_DRIVER_DIAGNOSTIC_R1.json','PALMAR_IRREGULARITY_CURRENT9_OVERLAP_R1.json','PALMAR_IRREGULARITY_SOURCE_DONOR_COMPARISON_R1.json','PALMAR_IRREGULARITY_ROOT_CAUSE_R1.json','CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','PALMAR_DIGIT_ROOT_SURFACE_IRREGULARITY_HUMAN_REVIEW_R1.html']
assert all((OUT/k).is_file() for k in required)
jsons=list(OUT.glob('*.json'))
for p in jsons:read(p)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src']:self.links.append(v)
parser=Links();parser.feed((OUT/required[-1]).read_text(encoding='utf-8'));broken=[p for p in parser.links if not (OUT/unquote(p)).is_file()];assert not broken,broken
pngs=list(OUT.rglob('*.png'));dimensions={}
for p in pngs:
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:dimensions[p.relative_to(OUT).as_posix()]=list(im.size)
manifest=read(OUT/'DIAGNOSTIC_RENDER_MANIFEST_R1.json');assert len(manifest['renders'])==65
assert all(r['native_topology_exact'] and r['all_native_faces_present'] and not r['qualified_asset_loaded'] for r in manifest['renders'])
roi=read(OUT/'PALMAR_DIGIT_ROOT_IRREGULARITY_ROI_R1.json');assert len(roi['vertices'])==92 and len(roi['visible_hit_faces'])==62
donor=read(OUT/'PALMAR_IRREGULARITY_SOURCE_DONOR_COMPARISON_R1.json');assert donor['exact_face_cycle_validation'] and not donor['projection_used']
sec=read(OUT/'PALMAR_IRREGULARITY_NATIVE_CROSS_SECTIONS_R1.json');assert all(len(rows)>0 for st in sec['states'].values() for rows in st.values())
sk=read(OUT/'PALMAR_IRREGULARITY_SKIN_DRIVER_DIAGNOSTIC_R1.json');assert all(v['saved_case_reconstruction_max_ROI_error_mm']<.0001 for v in sk['saved_case_LBS_reconstruction'].values())
source_inputs=[]
for s in read(SOURCE/'RAW_SOURCE_GEOMETRY.json')['stages'].values():
 record=s['input'];p=ROOT/record['path'];source_inputs.append({'path':record['path'],'expected_sha256':record['sha256'],'actual_sha256':sha(p),'PASS':record['sha256']==sha(p)})
assert all(x['PASS'] for x in source_inputs)
dump('INPUT_PROVENANCE_VERIFICATION_R1.json',{'source_lineage_hash_checks':source_inputs,'inputs':[ref(p) for p in [FRESH/'POSED_COORDINATES_R1.json',HIST/'POSED_COORDINATES_R1.json',NATIVE,PREP/'RENDER_ONLY_VISUAL_MANIFEST_R1.json',PREP/'LOCKED_CURRENT9_ROWS_R1.json',SOURCE/'RAW_SOURCE_GEOMETRY.json',SOURCE/'HISTORICAL_OPERATION_RAM_REPLAY.json']], 'source_geometry_snapshot_used':True,'fresh_pose_payload_byte_preserved':True})
dump('INDEPENDENT_DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_artifacts':required,'valid_json_count':len(jsons),'diagnostic_render_count':len(manifest['renders']),'all_png_count':len(pngs),'image_dimensions':dimensions,'broken_review_links':broken,'positive_section_segments_all_required_states':True,'exact_native_oriented_ROI_face_correspondence':True,'LBS_reconstruction_saved_cases_max_error_mm':{k:v['saved_case_reconstruction_max_ROI_error_mm'] for k,v in sk['saved_case_LBS_reconstruction'].items()},'frozen_file_count':len(before),'production_drift':0,'source_inputs_verified':True,'Human_unique_target_match':False,'ROOT_CAUSE_CLASS':'UNRESOLVED','product_PASS':False,'next_not_executed':True,'verification_limit':'Human screenshot identity and product acceptability remain unresolved; candidate diagnostic evidence is complete'})
dump('OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json',{'files':{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST_R1.json'}})
print('PASS',len(before),'frozen files preserved;',len(pngs),'PNG verified;',len(manifest['renders']),'diagnostic renders; current9 HOLD',flush=True)
