import sys
sys.dont_write_bytecode = True
from common import *
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree
from PIL import Image

required = [PHASE+'_REPORT.md', PHASE+'_STATUS.json',
 'CURRENT_JOINT_QUALIFICATION_SEMANTICS_R1.json',
 'JOINT_SURFACE_REQUALIFICATION_R1.json', 'JOINT_SURFACE_DELTA_RANKING_R1.json',
 'REST_RIG_PAYLOAD_REVALIDATION_R1.json', 'ZERO_POSE_REVALIDATION_R1.json',
 'BIND_ZERO_GEOMETRY_REVALIDATION_R1.json', 'MODIFIER_BIND_CONTRACT_REVALIDATION_R1.json',
 'WEIGHT_HASH_READONLY_REVERIFICATION_R1.json', 'DORSAL_MCP_BIND_ZERO_CONTOUR_EVIDENCE_R1.json',
 'PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json', 'review.html']
assert all((OUT/n).is_file() for n in required)
status = read(OUT/(PHASE+'_STATUS.json'))
for k,v in {'FORMAL_JOINT_COUNT':21,'FORMAL_JOINTS_PASS':21,
 'DEFORM_JOINT_INSIDE_FAILURE_COUNT':0,'TIP_HELPER_FAILURE_COUNT':0,'JOINT_REGION_FAILURE_COUNT':0,
 'BONE_PAYLOAD_DELTA':0,'JOINT_PAYLOAD_DELTA':0,'ROLL_DELTA':0,'REST_MATRIX_DELTA':0,
 'REST_RIG_PAYLOAD_MATCH':'PASS','ZERO_POSE':'PASS','BIND_ZERO':'PASS','MODIFIER_BINDING':'PASS',
 'R2_WEIGHT_HASH':WEIGHT_HASH,'R2_WEIGHT_HASH_MATCH':'PASS',
 'DORSAL_MCP_DENT_REAPPEARED_AT_BIND_ZERO':'NO','JOINT_RELOCATION_REQUIRED':'NO',
 'RIG_REBUILD_REQUIRED':'NO','WEIGHT_CHANGE_REQUIRED':'NO','STATIC_SKIN_REQUALIFICATION':'NOT_RUN',
 'PROTECTED_HISTORY_DRIFT':0,'MACHINE_HARD_BLOCKER_COUNT_RETAINED':9,
 'FULL_STAGE6A_STATUS_RETAINED':'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION',
 'RAW_TO_BIND_POINT_COUNT':3416,'OUTSIDE_EXPECTED_NUMERICAL_RESIDUE_COUNT':0,
 'BLEND_FILES_SAVED_THIS_PHASE':0,'STAGE6_POSE_COUNT':0,'PRODUCTION_PROMOTION':'NO',
 'VERDICT':'PASS_JOINT_REST_ZERO_BIND_REQUALIFIED','STOP':True,'NEXT_EXECUTED':False}.items():
 assert status[k] == v, (k,status[k])
assert status['RAW_TO_BIND_MAX_DELTA_MM'] < status['EXISTING_ZERO_BIND_GATE_MM'] == 0.0001
assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
assert not list(OUT.rglob('*.blend'))

class Links(HTMLParser):
 def __init__(self):
  super().__init__(); self.links=[]; self.rows=0
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('src','href') and v:self.links.append(v)
  if tag=='tr':self.rows+=1
html=(OUT/'review.html').read_text(encoding='utf-8')
parser=Links(); parser.feed(html)
local=[]
for link in parser.links:
 parts=urlsplit(link)
 if not parts.scheme and parts.path:
  p=(OUT/unquote(parts.path)).resolve()
  assert p.is_relative_to(OUT) and p.is_file(),link
  local.append(link)
assert parser.rows==22 and 'height:84px' in html and 'overflow-wrap:anywhere' in html
renders=read(OUT/'MATCHED_RENDER_MANIFEST_R1.json')['renders']
assert len(renders)==18
for r in renders:
 with Image.open(OUT/r['path']) as im:
  assert list(im.size)==r['resolution'],r['path']
  im.verify()
annotations=read(OUT/'JOINT_ANNOTATION_EVIDENCE_MANIFEST_R1.json')['annotations']
assert len(annotations)==6
for r in annotations:
 with Image.open(OUT/r['source']) as a, Image.open(OUT/r['output']) as b:
  assert a.size==b.size
  b.verify()
svgs=list((OUT/'sections').glob('*.svg')); assert len(svgs)==6
for p in svgs:ElementTree.parse(p)
with Image.open(OUT/'MATCHED_RAW_BIND_CONTOUR_INSPECTION_R1.png') as im:
 assert im.size==(1920,2728); im.verify()

dump('BROWSER_REVIEW_VALIDATION_R1.json',{
 'initial_browser_review':'COMPLETED_BEFORE_FINAL_LAYOUT_FIX',
 'url':'http://127.0.0.1:8877/review.html','initial_loaded_images':24,
 'initial_table_joint_rows':21,'initial_viewport_width':630,
 'initial_caption_overflow_observed':True,
 'local_final_caption_height_px':84,'local_long_link_wrapping_added':True,
 'final_browser_refresh':'NOT_EXECUTED_AUTOMATIC_APPROVAL_REVIEW_UNAVAILABLE',
 'review_failure_reason':'Selected approval model is at capacity; not a determination that action is unsafe',
 'blocked_action_retried_or_bypassed':False,
 'scope':'Browser delivery layout only; numerical/native requalification complete independently'})
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json'); after=inventory()
assert before==after
jsons=list(OUT.rglob('*.json'))
for p in jsons:
 json.loads(p.read_text(encoding='utf-8-sig'),parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
dump('FINAL_DELIVERY_VALIDATION_R1.json',{
 'status':'PASS','required_files_present':len(required),'strict_JSON_files_validated':len(jsons),
 'native_render_files_validated':len(renders),'annotation_files_validated':len(annotations),
 'native_section_SVGs_validated':len(svgs),'review_local_references_validated':len(local),
 'input_asset_SHA256_checks':'PASS','no_blend_saved':True,
 'protected_preexisting_file_count':len(before),'changed_removed_added_outside_phase_directory':0,
 'final_browser_refresh':'UNVERIFIED_REVIEW_SERVICE_CAPACITY',
 'VERDICT':status['VERDICT'],'NEXT_EXECUTED':False,'STOP':True})
manifest={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*'))
 if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST.json'}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST.json',{'algorithm':'SHA256','files':manifest,
 'exclusion':'Only this self-referential manifest','phase':PHASE})
print(json.dumps({'status':'PASS','required_files':len(required),'evidence_file_count':len(manifest),
 'protected_files':len(before),'drift':0,'verdict':status['VERDICT'],'STOP':True}))
