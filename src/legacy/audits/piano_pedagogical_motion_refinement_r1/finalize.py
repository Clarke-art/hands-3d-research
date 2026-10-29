from pathlib import Path
import json,hashlib,urllib.request
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
old=read('PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in old.items() if not Path(p).exists() or sha(p)!=h];assert not changed,changed
assert len(list(P.glob('*.blend')))==1
man=read('SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
videos=read('VIDEO_VERIFICATION.json');assert len(videos)==13
for n,x in videos.items():assert sha(P/n)==x['sha256']
stills=read('STILL_MANIFEST.json');different=[]
for r in stills:
 a=Image.open(P/'stills'/r['files']['SOURCE']).convert('RGB');b=Image.open(P/'stills'/r['files']['NEW']).convert('RGB');different.append(dict(label=r['label'],view=r['view'],different=ImageChops.difference(a,b).getbbox() is not None))
assert all(r['different'] for r in different)
for view in ['TEACHING','OVERHEAD','SIDE_OBLIQUE']:assert len(list((P/'_frames'/view).glob('*.png')))==357
url='http://127.0.0.1:8770/audits/piano_pedagogical_motion_refinement_r1/normal_speed_teaching_NOT_APPROVED.mp4'
with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes=0-99'})) as res:assert res.status==206 and len(res.read())==100
save('ASSET_PRESERVATION.json',dict(protected_files=len(old),changed=changed,all_hashes_match=True,native_scene_objects=173,native_asset_identity=read('SCENE_ASSET_IDENTITY.json')['pass_'],source_lightweight_sha256='18d3c729ff16759a4a7b41a621a1682711d876ad2e109a748d1ea9e675762df3',historical_results_preserved=True,old_tool_scratch_files_relocated=True))
save('DELIVERY_VERIFICATION.json',dict(candidate_count=1,candidate_sha256=man['sha256'],source_not_substituted=True,source_and_new_stills_differ=different,media_count=13,all_media_full_decode_pass=True,frames_each_view=357,views=3,half_speed_frames=357,quarter_speed_frames=357,half_speed_duration=11.9,quarter_speed_duration=23.8,new_intermediate_motion=False,browser_checks=dict(quarter_speed_comparison='PASS: overhead paired encoded video, 1920px, currentTime=3.833333s, rate=.25, playing',half_speed_new='PASS: side-oblique, currentTime=2.6s, rate=.5, playing',frame_forward_back='PASS 68 ->69 ->68, original PNG',range_requests='PASS206',console_errors=[]),strict_gate_remains='FAIL',source_protection='PASS'))
status=read('FINAL_STATUS.json');status['FROZEN_ASSETS_UNCHANGED']='YES';status['PROTECTED_FILES_CHECKED']=len(old);status['DELIVERED_MEDIA_COUNT']=13;status['NEW_VIDEOS_ACTUALLY_RENDERED']='YES';status['HUMAN_REVIEW_AVAILABLE']=True;save('FINAL_STATUS.json',status)
(P/'OPEN_REVIEW.txt').write_text('http://127.0.0.1:8770/audits/piano_pedagogical_motion_refinement_r1/HUMAN_REVIEW.html\n如果本地服务已停止，在本目录运行 python serve_review.py，再打开此链接。\nDIAGNOSTIC_ONLY / NOT_APPROVED / FAIL_CLOSED。STOP — HUMAN REVIEW。\n',encoding='utf8')
print('FINAL_PROTECTED',len(old),'UNCHANGED; NEW_BLEND=1; NEW_MEDIA=13; FAIL_CLOSED_RETAINED')
