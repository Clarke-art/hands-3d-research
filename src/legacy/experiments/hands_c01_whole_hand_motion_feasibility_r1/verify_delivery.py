import json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
before=read('PROTECTED_FILES_BEFORE.json');after={p:sha(Path(p)) for p in before};assert after==before
(O/'PROTECTED_FILES_AFTER.json').write_text(json.dumps(after,indent=2)+'\n',encoding='utf8')
I=read('INPUT_BINDINGS.json');M=read('SCENE_MANIFEST.json');metric=read('MOTION_FEASIBILITY_METRICS.json');required=['SOURCE_AND_RIG_PREFLIGHT.md','C01_MOTION_PLAN.md','MOTION_FEASIBILITY_METRICS.json','HUMAN_VISUAL_REVIEW.md','FINAL_RECOMMENDATION.md']
assert metric['status']=='MOTION_FEASIBILITY_PARTIAL' and metric['actual_action_generated']
assert metric['source_fingering_unchanged'] and metric['key_actions_payload_unchanged'] and metric['hand_native_identity_unchanged']
assert len(metric['notes'])==9 and [n['note_id'] for n in metric['notes']]==[f'R{i:02}' for i in range(6,15)]
assert [n['finger'] for n in metric['notes']]==[1,1,3,1,2,3,4,5,1]
assert sha(Path(M['path']))==M['sha256']
assert len(read('STILL_MANIFEST.json'))==7 and len(list((O/'stills').glob('*.png')))==7
assert not list(O.glob('*.mp4')) and not (O/'_frames').exists()
for n in required:
 text=(O/n).read_text(encoding='utf8');assert text and '\ufffd' not in text,n
files=[p for p in O.rglob('*') if p.is_file() and p.name!='DELIVERY_MANIFEST.json'];total=sum(p.stat().st_size for p in files)
manifest=dict(task='PIANO_C01_WHOLE_HAND_MOTION_FEASIBILITY_R1',status='MOTION_FEASIBILITY_PARTIAL',protected_file_count=len(before),all_protected_files_unchanged=True,new_continuous_candidates=1,local_repair_iterations=0,video_files=0,stills=7,total_bytes=total,temporary_frame_cache_bytes=0,source_notes=9,source_note_message_bindings=18,required_files=[dict(file=n,sha256=sha(O/n),bytes=(O/n).stat().st_size) for n in required],files=[dict(file=p.relative_to(O).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)])
(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('DELIVERY_PASS',len(before),'protected files unchanged; 1 isolated Action scene; 7 stills; 0 videos; 0 frame cache; total MB',round(total/1024/1024,2))
