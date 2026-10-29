from common import *
import re
from PIL import Image
before=read(OUT/'PROTECTED_BEFORE.json');protected={x['path']:x['sha256'] for x in before['files']}
actual_reads={}
for p in OUT.glob('*RECEIPT*.json'):
 data=read(p)
 for row in data.get('files',[]):
  key=row['path'];value=row.get('before',row.get('sha256'))
  assert key not in actual_reads or actual_reads[key]==value
  actual_reads[key]=value
for key,value in READS.items():actual_reads.setdefault(key,value)
for key,value in actual_reads.items():
 if key in protected:assert protected[key]==value
 else:protected[key]=value
files=[dict(path=k,before=v,after=sha(k),unchanged=v==sha(k),protection_set='initial_45' if k in {x['path'] for x in before['files']} else 'additional_actual_read') for k,v in protected.items()]
assert all(r['unchanged'] for r in files)
save('PROTECTED_SHA256_BEFORE_AFTER.json',dict(all_unchanged=True,initial_protected_count=len(before['files']),checked_count=len(files),files=files,piano_access=False,source_sha256=sha(SOURCE),limitations='File SHA receipts plus native data and saved diagnostic verification; no claim of a repair candidate. Actual supplementary input hashes were captured by the read audit hook, not guessed from history.'))
quality={};images=[]
for p in OUT.glob('*.png'):
 with Image.open(p) as im:im.verify()
 images.append(str(p))
quality['images_verified']=len(images)
for p in OUT.glob('*.py'):compile(p.read_text(encoding='utf8'),str(p),'exec')
quality['python_sources_compile']=True
broken=[]
for p in OUT.glob('*.md'):
 for dest in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
  if re.match(r'^[A-Za-z]:/',dest) and not Path(dest).exists():broken.append(dict(markdown=str(p),target=dest))
assert not broken;quality['local_markdown_links_exist']=True
assert not (OUT/'STATIC_NOT_APPROVED.blend').exists();quality['no_repair_candidate_mislabel']=True
assert read(OUT/'REOPEN_DIAGNOSTIC_VERIFICATION.json')['all_pass'];quality['three_diagnostic_blends_reopened_exactly']=True
quality.update(result='UNRESOLVED',final_state='STOP — HUMAN REVIEW',pose_rounds=0,animation_authorized=False,protected_all_unchanged=True,protected_checked=len(files),targeted_extra_readonly_checks=1,static_candidate_geometry='NOT_RUN',new_illegal_collision_count=None)
save('FINAL_VERIFICATION.json',quality)
save('RESULT.json',dict(result='UNRESOLVED',status='STOP — HUMAN REVIEW',candidate=None,pose_rounds=0,geometry_pass=False,naturality_pass=False,continuous_animation='NO',asset_issue_confirmed=False,reason='Partial deformation-source evidence; no unique anatomical defect cause or pose repair feasibility established. No frozen-asset change authorized or performed.',human_rejected_previous_status='GEOMETRY_PASS_NATURALITY_FAIL'))
artifacts=[]
for p in OUT.iterdir():
 if p.is_file() and p.name not in ['ARTIFACT_SHA256.json']:
  artifacts.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
save('ARTIFACT_SHA256.json',dict(files=artifacts,excluded=['self','matplotlib_cache'],result='UNRESOLVED'))
print(json.dumps(quality,ensure_ascii=False),flush=True)
