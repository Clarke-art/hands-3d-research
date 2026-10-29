from pathlib import Path
import json,re,urllib.request
P=Path(__file__).resolve().parent
required=['RIGHT_HAND_OVERLAP_AND_BLACK_KEY_DIAGNOSIS.md','LOCAL_JOINT_COORDINATION_DESIGN.md','IMPLEMENTATION_REPORT.md','BEFORE_AFTER_SPATIAL_REVIEW.md','APPROVED_MOTION_PRESERVATION.md','ENGINEERING_DIAGNOSTICS.json','FINAL_STATUS.json','FINAL_ANSWERS.md','DIAGNOSTIC_REVIEW.html']
assert all((P/f).is_file() for f in required)
page=(P/'DIAGNOSTIC_REVIEW.html').read_text(encoding='utf8')
links=re.findall(r'(?:href|src)="([^"]+)"',page)
missing=[a for a in links if not (P/a).is_file()];assert not missing,missing
assert not list(P.glob('*.blend'))
status=json.loads((P/'FINAL_STATUS.json').read_text(encoding='utf8'))
e=json.loads((P/'ENGINEERING_DIAGNOSTICS.json').read_text(encoding='utf8'))
assert status['NEW_DYNAMIC_CANDIDATES']==0 and status['FORMAL_LOCAL_MOTION_SOLVE_ATTEMPTS']==0
assert len(e['residual']['complete_episode_intervals_video_sec'])==2
url=json.loads((P/'review_server_state.json').read_text())['url']
response=urllib.request.urlopen(url);assert response.status==200
out=dict(required_files=len(required),relative_links_checked=len(links),missing_links=missing,blends=0,html_http=response.status,status='PASS_DELIVERY_FAIL_CLOSED_PRODUCT',residual_episodes=e['residual']['complete_episode_intervals_video_sec'])
(P/'FINAL_DELIVERY_VERIFICATION.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(out))
