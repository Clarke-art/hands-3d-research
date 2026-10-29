from common import *
from html.parser import HTMLParser
from urllib.request import urlopen
required=['APPROVED_SOURCE_BINDINGS.md','SHARED_MIDI_TIMELINE.md','DUAL_HAND_SCENE_INTEGRATION.md','APPROVED_MOTION_PRESERVATION.md','DUAL_HAND_FUNCTIONAL_VALIDATION.md','HUMAN_VISIBLE_REVIEW.md','ENGINEERING_DIAGNOSTICS.json','FINAL_STATUS.json','HUMAN_REVIEW.html',DEST.name,'normal_speed_teaching.mp4','normal_speed_overhead.mp4','normal_speed_side_oblique.mp4']
assert all((P/n).is_file() and (P/n).stat().st_size>0 for n in required)
assert list(P.glob('*.blend'))==[DEST]
manifest=read(P/'DELIVERY_MANIFEST.json')
for n,v in manifest['files'].items():assert sha(P/n)==v['sha256'] and (P/n).stat().st_size==v['bytes']
state=read(P/'FINAL_STATUS.json')
assert state['candidate_count']==1 and state['NEW_MOTION_SOLVER_CALLS']==0 and state['manual_per_note_motion_fixes']==0
assert state['HUMAN_VISIBLE_QUALITY']=='HUMAN_PENDING' and state['ENGINEERING_DIAGNOSTICS']=='WARN' and state['FINAL_STATUS']=='READY_FOR_HUMAN_REVIEW'
assert read(P/'FROZEN_ASSET_PROTECTION.json')['pass_']
assert read(P/'MUX_AUDIO_CLOCK_VERIFICATION.json')['pass_']
class References(HTMLParser):
    def __init__(self):super().__init__();self.refs=[]
    def handle_starttag(self,tag,attrs):
        self.refs.extend(v for k,v in attrs if k in ['src','href','poster'])
page=References();page.feed((P/'HUMAN_REVIEW.html').read_text(encoding='utf8'))
assert all((P/x).is_file() for x in page.refs)
server=read(P/'review_server_state.json')
with urlopen(server['url'],timeout=5) as response:
    assert response.status==200 and response.read().decode('utf8')==(P/'HUMAN_REVIEW.html').read_text(encoding='utf8')
dump('FINAL_DELIVERY_VERIFICATION.json',dict(pass_=True,required_files=len(required),all_delivery_SHA_verified=True,sole_Blend_candidate=True,all_review_page_references_resolve=True,local_review_HTTP_status=200,review_url=server['url'],Human_visual_approval=False,final_status=state['FINAL_STATUS'],notes='No candidate re-save, no second candidate, no source modification; full realtime playback helper limitation remains explicit.'))
print('FINAL_DELIVERY_SHA_LINKS_ONE_CANDIDATE_HUMAN_PENDING_PASS',flush=True)
