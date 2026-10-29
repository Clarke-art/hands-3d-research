from local_common import *
from html.parser import HTMLParser
from urllib.request import urlopen
manifest=read(P/'DELIVERY_MANIFEST.json');state=read(P/'FINAL_STATUS.json')
assert len(list(P.glob('*.blend')))==1 and read(P/'CANDIDATE_COMMIT.json')['count']==1
for n,v in manifest['files'].items():assert (P/n).is_file() and sha(P/n)==v['sha256'] and (P/n).stat().st_size==v['bytes']
assert state['LOCAL_REFINEMENT']=='PARTIAL' and state['strict_zero_geometric_intersection']=='FAIL_RETAINED' and state['HUMAN_VISIBLE_QUALITY']=='HUMAN_PENDING'
assert state['parameter_changes_after_lock']==0 and state['motion_solver_calls']==0 and state['FINAL_STATUS']=='READY_FOR_HUMAN_REVIEW'
lock=read(P/'LOCAL_CORRECTION_POLICY_LOCK.json');assert sha(P/'LOCAL_CORRECTION_POLICY.json')==lock['policy_sha256'] and all(sha(P/n)==s for n,s in lock['scripts'].items())
assert read(P/'APPROVED_SOURCE_PROTECTION.json')['pass_'] and read(P/'ACTIVE_RING_C5_CAP_READBACK.json')['pass_']
class Links(HTMLParser):
    def __init__(self):super().__init__();self.refs=[]
    def handle_starttag(self,tag,attrs):self.refs.extend(v for k,v in attrs if k in ['src','href','poster'])
links=Links();links.feed((P/'HUMAN_REVIEW.html').read_text(encoding='utf8'));assert all((P/n).is_file() for n in links.refs)
server=read(P/'review_server_state.json')
with urlopen(server['url'],timeout=5) as response:assert response.status==200 and response.read().decode('utf8')==(P/'HUMAN_REVIEW.html').read_text(encoding='utf8')
before=read(P/'OVERLAP_TIMES_AND_GEOMETRY.json')['rows'];after=read(P/'IN_MEMORY_VALIDATION.json')['local_bad_samples'];bframes=[r['frame'] for r in before if r['intersecting_patch_triangle_pairs']];aframes=sorted({1+round(r['presentation_sec']*60) for r in after if abs(r['presentation_sec']*60-round(r['presentation_sec']*60))<1e-7})
dump('MAIN_FRAME_LOCAL_OVERLAP_COMPARISON.json',dict(source_actual_distal_patch_intersected_video_frames=bframes,candidate_actual_distal_patch_intersected_video_frames=aframes,source_count=len(bframes),candidate_count=len(aframes),same60Hz_clock=True,geometry_zero_clearance_pass=False,Human_quality='HUMAN_PENDING',scope='Same distal patches in original and candidate; fewer intersected frames is a finite diagnostic, not Human visual PASS.'))
dump('FINAL_DELIVERY_VERIFICATION.json',dict(pass_=True,all_delivery_SHA_verified=True,all_review_links_resolve=True,review_URL=server['url'],one_candidate=True,one_unchanged_locked_policy=True,parameter_changes_after_lock=0,strict_geometric_zero_failure_retained=True,source_assets_unchanged=True,local_refinement='PARTIAL',Human_approval=False,final_status=state['FINAL_STATUS']))
print('FINAL_ONE_CANDIDATE_PARTIAL_WARN_SOURCE_PROTECTION_AND_LINKS_VERIFIED',flush=True)
