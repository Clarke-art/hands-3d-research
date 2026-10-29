import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;OLD=O.parent/'hands_fingering_inference_poc_r1';ROOT=O.parent/'hands'
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import mido
b=json.loads((OLD/'SOURCE_EVENT_BINDINGS.json').read_text());tl=json.loads(Path(b['source_timeline']).read_text());mf=mido.MidiFile(b['source_midi'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,d):(O/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(Path(b['source_midi']))==b['source_midi_sha256'] and sha(Path(b['source_timeline']))==b['source_timeline_sha256']
assert len(tl['notes'])==23 and len(b['bindings'])==23
messages={};paired=[];tempo=[]
for track,seq in enumerate(mf.tracks):
 t=0;active={}
 for index,msg in enumerate(seq):
  t+=msg.time
  if msg.type=='set_tempo':tempo.append([t,msg.tempo])
  if msg.type not in ['note_on','note_off']:continue
  event=dict(track=track,sequence=index,tick=t,**msg.dict());messages[(track,index)]=event
  key=(msg.channel,msg.note)
  if msg.type=='note_on' and msg.velocity:active[key]=event
  else:
   start=active.pop(key);paired.append((start,event))
assert tempo==b['tempo_events'] and mf.ticks_per_beat==b['ppq']
for x in b['bindings']:
 assert messages[(x['midi_note_on']['track'],x['midi_note_on']['sequence'])]==x['midi_note_on']
 assert messages[(x['midi_note_off']['track'],x['midi_note_off']['sequence'])]==x['midi_note_off']
 assert x['source_timeline_note']==next(n for n in tl['notes'] if n['note_id']==x['note_id'])
context=[]
for hand,track in [('R',1),('L',2)]:
 nextnotes=sorted([(on,off) for on,off in paired if on['track']==track and on['tick']>=4608],key=lambda q:(q[0]['tick'],q[0]['note']))[:9]
 for i,(on,off) in enumerate(nextnotes):
  context.append(dict(context_id=f'CTX_{hand}{i:02}',hand=hand,pitch=on['note'],note_name=mido.get_note_name(on['note']) if hasattr(mido,'get_note_name') else ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][on['note']%12]+str(on['note']//12-1),note_on=on,note_off=off,source_on_sec=on['tick']*428571/384/1e6,source_off_sec=off['tick']*428571/384/1e6,role='Adjacent MIDI context for analysis only; not a new scored/test note'))
protected=list(p for p in OLD.iterdir() if p.is_file())+[p for p in (OLD/'evidence').glob('*') if p.is_file()]+[Path(b['source_midi']),Path(b['source_timeline'])]
for rel in ['node_modules/@lumikey/piano-fingering-model/models/fingering_transformer_left.onnx','node_modules/@lumikey/piano-fingering-model/models/fingering_transformer_right.onnx','node_modules/@lumikey/piano-fingering-model/dist/inference.js','node_modules/@lumikey/piano-fingering-model/dist/node.js']:
 protected.append(OLD/rel)
dump('PROTECTED_INPUTS_BEFORE.json',{str(p):sha(p) for p in protected})
dump('SOURCE_EVENT_BINDINGS.json',dict(b,task='PIANO_SEQUENCE_FINGERING_PLANNING_R1',identity_revalidated_from_original_midi=True,context=context))
print('SOURCE_PASS',23,46,'ADJACENT_CONTEXT',[(x['context_id'],x['note_name'],x['note_on']['tick']) for x in context])
