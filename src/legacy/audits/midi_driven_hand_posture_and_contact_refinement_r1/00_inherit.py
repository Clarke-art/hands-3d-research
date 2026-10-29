from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent
OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
protected=json.loads((OLD/'PROTECTED_INPUTS_BEFORE_R1.json').read_text(encoding='utf-8-sig'))
for f in OLD.iterdir():
 if f.is_file():protected[str(f)]=sha(f)
for f in (OLD/'source').rglob('*'):
 if f.is_file():protected[str(f)]=sha(f)
assert all(sha(f)==v for f,v in protected.items())
(P/'PROTECTED_INPUTS_BEFORE_R1.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
names=['PERFORMANCE_TIMELINE_R1.json','PROVISIONAL_FINGERING_PLAN_R1.json','SONG_DATA_R1.json','KEYBOARD_88_KEY_TABLE_R1.json','KEYBOARD_AUTHORITY_R1.json','KEYBOARD_COORDINATE_FRAME_R1.json','FINGERTIP_CONTACT_MARKERS_R1.json','CONTACT_TOLERANCE_POLICY_R1.json','RIG_CANONICAL_PROBE_R1.json','KEY_AUDIO_SYNC_R1.json','piano_performance.wav']
for n in names:shutil.copyfile(OLD/n,P/n)
core=(OLD/'performance_core.py').read_text().replace("str(P/'_deps')","str(P.parent/'midi_driven_dual_hand_piano_performance_poc_r1/_deps')")
(P/'performance_core.py').write_text(core,encoding='utf-8')
(P/'INHERITED_INPUTS_R1.json').write_text(json.dumps({n:sha(P/n) for n in names},indent=2),encoding='utf-8')
print('Protected',len(protected),'files; inherited',len(names),'byte-identical inputs')
