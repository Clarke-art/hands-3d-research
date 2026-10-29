from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R3=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
files=set(read(R3/'PROTECTED_INPUTS_BEFORE.json'))
files.update(str(f) for f in R3.rglob('*') if f.is_file() and not f.name.startswith('review_server') and '__pycache__' not in f.parts)
before={p:sha(p) for p in sorted(files)};dump('PROTECTED_INPUTS_BEFORE.json',before)
tl=read(ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/PERFORMANCE_TIMELINE.json');notes={n['note_id']:n for n in tl['notes']}
on=lambda n:notes[n]['note_on'];off=lambda n:notes[n]['note_off'];end=356/60
windows={
 'INDEX':[[0,on('R02')],[off('R02'),on('R09')],[on('R10'),end]],
 'MIDDLE':[[on('R01'),off('R05')],[on('R08')-.18,off('R13')]],
 'RING':[[on('R00'),on('R09')],[on('R10')-.18,end]]}
dump('PROPOSED_EVENT_SCOPE.json',dict(baseline='Stage C R1',baseline_sha256='d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7',video_to_music_offset_sec=-.35,windows_video_sec=windows,windows_music_sec={d:[[a-.35,b-.35] for a,b in ws] for d,ws in windows.items()},digits=['INDEX','MIDDLE','RING'],dofs=['MCP flexion','PIP flexion','DIP flexion','MCP spread'],fixed=['right root','thumb','little','entire left hand','keyboard','music'],window_reason='Music-event anchored supports for confirmed pair/black-key conflicts. INDEX A4 active and the clean R09 phase are retained; middle early/late windows separated by a clean interval; ring windows separated around middle C5.',outer_clip_boundaries='Source already penetrates at video start and end. These are presentation-domain edges, not artificial zero-offset seams inside the phrase. Interior support boundaries require zero correction and velocity.',status='PROPOSED_PENDING_STATIC_GEOMETRY_GATE',formal_dynamic_attempts=0))
print('SCOPE_AND_PROTECTION',len(files))
