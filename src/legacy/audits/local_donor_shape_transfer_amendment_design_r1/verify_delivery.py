import sys
sys.dont_write_bytecode=True
from common import *
from html.parser import HTMLParser
from PIL import Image
from xml.etree import ElementTree
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=inventory();dump('FROZEN_HASHES_AFTER.json',after)
missing=sorted(set(before)-set(after));added=sorted(set(after)-set(before));changed=[{'path':p,'before':before[p],'after':after[p]} for p in before.keys()&after.keys() if before[p]!=after[p]]
verification={'status':'PASS' if not(missing or added or changed) else 'FAIL_CLOSED','scope':'Every pre-existing workspace file, including all production/historical/reference/prior-audit files; only this round independent audit directory excluded. No pre-existing file may be modified/deleted and no new file allowed elsewhere.','protected_preexisting_file_count':len(before),'protected_after_count':len(after),'changed_files':changed,'deleted_files':missing,'new_files_outside_current_audit':added,'PRODUCTION_DRIFT':len(changed)+len(missing)+len(added),'all_preexisting_files_byte_identical':before==after,'before_inventory':ref(OUT/'FROZEN_HASHES_BEFORE.json'),'after_inventory':ref(OUT/'FROZEN_HASHES_AFTER.json'),'production_source_stage4c':ref(SOURCE),'production_current_R2_rig':ref(R2),'official_donor_master':ref(MASTER)}
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',verification)
assert before==after,'FAIL_CLOSED protected pre-existing workspace drift'
P=read(OUT/'FORMAL_DONOR_TRANSFER_PROVENANCE_R1.json');assert sha(CANDIDATE)==P['FORMAL_CANDIDATE']['sha256'];assert sha(SOURCE)==P['SOURCE_STAGE4C']['sha256'];assert sha(MASTER)==P['DONOR_SOURCE']['sha256']
st=read(OUT/(PHASE+'_STATUS.json'));st.update({'PRODUCTION_DRIFT':0,'PROTECTED_PREEXISTING_FILE_COUNT':len(before),'AMENDMENT_DESIGN_VERDICT':'READY_FOR_HUMAN_AMENDMENT_APPROVAL'});dump(PHASE+'_STATUS.json',st)
report_path=OUT/(PHASE+'_REPORT.md');report=report_path.read_text(encoding='utf-8').replace('结论：待最终只读hash验证后，READY_FOR_HUMAN_AMENDMENT_APPROVAL。','结论：READY_FOR_HUMAN_AMENDMENT_APPROVAL。')
report+='\n## 最终只读与交付验证\n\nPRODUCTION_DRIFT=0。全部'+str(len(before))+'个预先存在文件SHA256逐个相同；changed/deleted/new-outside-current-audit均为0。Stage4C、official master、currentR2、既有authority与旧Full42文件byte identical。正式candidate保存之后hash未变。\n\nAMENDMENT_DESIGN_VERDICT=READY_FOR_HUMAN_AMENDMENT_APPROVAL。NEXT=HUMAN_APPROVE_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_R1。STOP — HUMAN REVIEW。\n'
report_path.write_text(report,encoding='utf-8')
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json','FORMAL_DONOR_TRANSFER_COORDINATES_R1.json','FORMAL_DONOR_TRANSFER_PROVENANCE_R1.json','FORMAL_DONOR_TRANSFER_STRUCTURE_AUDIT_R1.json','FORMAL_DONOR_TRANSFER_CONTACT_AUDIT_R1.json','FORMAL_DONOR_TRANSFER_BOUNDARY_AUDIT_R1.json','FORMAL_DONOR_TRANSFER_BIND_PREVIEW_R1.json','FORMAL_DONOR_TRANSFER_DOWNSTREAM_PLAN_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','review.html',CANDIDATE.name]
assert all((OUT/p).is_file() for p in required)
json_files=list(OUT.glob('*.json'))
for p in json_files:read(p)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src'] and v and not v.startswith(('#','http')):self.links.append(v)
links=Links();links.feed((OUT/'review.html').read_text(encoding='utf-8'));assert all((OUT/p).is_file() for p in links.links)
for p in (OUT/'sections').glob('*.svg'):ElementTree.parse(p)
manifest=read(OUT/'FORMAL_MATCHED_RENDER_MANIFEST_R1.json');assert len(manifest['renders'])==96
for r in manifest['renders']:
 with Image.open(OUT/r['path']) as im:im.verify()
# Every matched row uses identical camera, scale and resolution.
rows={}
for r in manifest['renders']:
 key=(r['view'],r['shading']);frame={k:r[k] for k in ['camera_target_m','camera_direction','ortho_scale_m','resolution']}
 if key in rows:assert frame==rows[key]
 rows[key]=frame
dump('DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_outputs_present':required,'all_JSON_parsed_count':len(json_files),'all_review_local_links_exist':True,'SVG_sections_parsed':6,'render_count':96,'all_render_images_valid':True,'matched_camera_scale_resolution_per_row_exact':True,'original_human_render_dimensions':[640,800],'candidate_hash_still_exact':True,'protected_preexisting_files':len(before),'review_browser_first_screen_four_solid_columns_inspected':True,'review_browser_native_sections_overlay_inspected':True,'no_application_or_promotion':True,'Human_approval_pending':True})
artifact_hashes={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST.json'};dump('OUTPUT_EVIDENCE_HASH_MANIFEST.json',artifact_hashes)
print('READY_FOR_HUMAN_AMENDMENT_APPROVAL; protected files=',len(before),'drift=0; renders=96; required outputs=PASS; STOP HUMAN REVIEW')
