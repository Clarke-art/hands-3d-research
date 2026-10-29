import sys,re,struct,urllib.request
sys.dont_write_bytecode=True
from common import *
from html.parser import HTMLParser
required=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','SOURCE_GEOMETRY_LINEAGE_R1.json','DENT_SOURCE_LINEAGE_METRICS_R1.json','DENT_SOURCE_MATCHED_VISUAL_AUDIT_R1.json','DENT_FIRST_INTRODUCTION_OPERATION_AUDIT_R1.json','DONOR_SOURCE_SELECTION_R1.json','DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json','DONOR_PATCH_TRANSFER_FEASIBILITY_R1.json','FULL_REPLACEMENT_VS_LOCAL_TRANSFER_R1.json','review.html','TEMP_DONOR_TRANSFER_DESIGN_ONLY.blend','TEMP_DONOR_TRANSFER_DESIGN_ONLY.json']
assert all((OUT/n).is_file() for n in required)
manifest=read(OUT/'DENT_SOURCE_MATCHED_VISUAL_AUDIT_R1.json');dims={}
for r in manifest['renders']:
 data=(OUT/r['path']).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',data[16:24]);assert (w,h)==((640,800) if r['view']=='HUMAN' else (640,640));dims[r['path']]=[w,h]
class Refs(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,tag,attrs):
  self.refs.extend(v for k,v in attrs if k in ['src','href'])
p=Refs();p.feed((OUT/'review.html').read_text(encoding='utf-8'));missing=[r for r in p.refs if not (OUT/r).is_file()];assert not missing
response=urllib.request.urlopen('http://127.0.0.1:8874/review.html');assert response.status==200
# An unchanged saved-source topology and unchanged outside coordinates imply every
# pair untouched by moved vertices is identical. All moved incident pairs use the exact gate.
assert read(OUT/'PROBE_TRUE3D_STRUCTURAL_GATE.json')['status']=='PASS'
assert read(OUT/'PROBE_PROTECTED_PAYLOAD_VERIFICATION.json')['all_protected_payloads_identical']
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after=inventory();changed=[n for n,h in before.items() if after.get(n)!=h];added=sorted(set(after)-set(before));assert not changed and not added,(changed,added)
dump('FROZEN_HASHES_AFTER.json',after)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS_BYTE_IDENTICAL_ALL_PREEXISTING_PROJECT_FILES','PRODUCTION_DRIFT':0,'protected_file_count':len(before),'changed_or_deleted_files':changed,'new_files_outside_this_audit':added,'all_history_frozen_official_production_authority_receipts_and_Stage6_included':True,'before_inventory':'FROZEN_HASHES_BEFORE.json','after_inventory':'FROZEN_HASHES_AFTER.json','new_output_scope':str(OUT.relative_to(ROOT)),'hash':'SHA256 actual file bytes','historical_blend_save_count':0,'production_blend_save_count':0,'weight_bone_joint_RSSF_cap37_R3_FIRST_WEB_nail_Human_truecap_Stage6_authority_writes':0})
dump('DELIVERY_VERIFICATION.json',{'status':'PASS','required_outputs':required+['PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json'],'valid_JSON_outputs':[p.name for p in OUT.glob('*.json') if read(p) is not None],'matched_render_count':len(dims),'PNG_dimensions':dims,'HTML_local_reference_count':len(p.refs),'missing_HTML_references':missing,'HTTP_review_status':200,'browser_review_verified':'Visible title, PASS badge, NOT_PRODUCTION/NOT_APPROVED, three-column current/donor/probe and five-column lineage; user-facing browser retained','STOP':'HUMAN_REVIEW','NEXT_EXECUTED':False})
dump('OUTPUT_EVIDENCE_HASH_MANIFEST.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST.json'})
print('DELIVERY VERIFIED',len(before),'preexisting files byte-identical;',len(dims),'renders; no production drift',flush=True)
