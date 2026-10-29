import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'hands/audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import mido
B=json.loads((O.parent/'hands_sequence_fingering_planning_r1/SOURCE_EVENT_BINDINGS.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(B['source_midi'])==B['source_midi_sha256'];assert sha(B['source_timeline'])==B['source_timeline_sha256']
mf=mido.MidiFile(B['source_midi']);msgs={};tempo=[];pairs=[]
for ti,tr in enumerate(mf.tracks):
 tick=0;active={}
 for si,msg in enumerate(tr):
  tick+=msg.time
  if msg.type=='set_tempo':tempo.append([tick,msg.tempo])
  if msg.type not in ['note_on','note_off']:continue
  ev=dict(track=ti,sequence=si,tick=tick,**msg.dict());msgs[ti,si]=ev;k=(msg.channel,msg.note)
  if msg.type=='note_on' and msg.velocity:active[k]=ev
  else:pairs.append(dict(on=active.pop(k),off=ev))
assert tempo==B['tempo_events'] and mf.ticks_per_beat==B['ppq']
for x in B['bindings']:
 for k in ['midi_note_on','midi_note_off']:e=x[k];assert msgs[e['track'],e['sequence']]==e
# Original tempo is constant; verify before exact tick->seconds conversion.
assert len(tempo)==1 and tempo[0][0]==0
notes=[]
for x in B['bindings']:
 n=x['source_timeline_note'];notes.append(dict(note_id=x['note_id'],hand=n['hand'],midi=n['midi_note'],on_tick=x['midi_note_on']['tick'],off_tick=x['midi_note_off']['tick'],music_on=x['midi_note_on']['tick']*tempo[0][1]/B['ppq']/1e6,music_off=x['midi_note_off']['tick']*tempo[0][1]/B['ppq']/1e6,display_on=x['midi_note_on']['tick']*tempo[0][1]/B['ppq']/1e6+.35,display_off=x['midi_note_off']['tick']*tempo[0][1]/B['ppq']/1e6+.35,key_color=n['key_color']))
c=json.loads((O.parent/'hands_sequence_fingering_planning_r1/SEQUENCE_CANDIDATES.json').read_text())
(O/'SOURCE_MIDI_REVALIDATION.json').write_text(json.dumps(dict(midi=B['source_midi'],midi_sha256=sha(B['source_midi']),timeline=B['source_timeline'],timeline_sha256=sha(B['source_timeline']),ppq=B['ppq'],tempo=tempo,notes=notes,all_bindings_match_original=True,source_pairs=pairs,candidate_file=str(O.parent/'hands_sequence_fingering_planning_r1/SEQUENCE_CANDIDATES.json'),candidate_sha256=sha(O.parent/'hands_sequence_fingering_planning_r1/SEQUENCE_CANDIDATES.json')),indent=2))
print('MIDI_VALIDATED',len(notes));print('CANDIDATE_KEYS',list(c));print('CANDIDATE_HEAD',str(c)[:1500])
