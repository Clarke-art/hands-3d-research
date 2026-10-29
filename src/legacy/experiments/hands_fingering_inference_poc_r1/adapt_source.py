import sys,json,hashlib,math
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(r'<HANDS_ROOT>')
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'))
import mido
TL=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/PERFORMANCE_TIMELINE.json'
MID=ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
tl=json.loads(TL.read_text(encoding='utf-8-sig')); mf=mido.MidiFile(MID)
assert sha(MID)==tl['source_sha256']=='fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75'
raw=[];tempo=[];sigs=[];messages={}
for tr,track in enumerate(mf.tracks):
 tick=0;held={}
 for seq,msg in enumerate(track):
  tick+=msg.time
  if msg.type=='set_tempo':tempo.append([tick,msg.tempo])
  if msg.type=='time_signature':sigs.append([tick,msg.numerator,msg.denominator])
  if msg.type not in ('note_on','note_off'):continue
  event=dict(track=tr,sequence=seq,tick=tick,**msg.dict()); messages[(tr,seq)]=event
  key=(msg.channel,msg.note)
  if msg.type=='note_on' and msg.velocity:
   assert key not in held
   held[key]=event
  else:
   on=held.pop(key)
   if on['tick']<4608:
    assert tick<=4608
    raw.append((on,event))
assert mf.ticks_per_beat==384 and tempo==[[0,428571]] and sigs==[[0,3,4]]
assert len(raw)==23 and len(tl['notes'])==23
bindings=[];inputs=[]
# Preserve the existing validated timeline order, including ascending chord pitch.
for i,n in enumerate(tl['notes']):
 matches=[(on,off) for on,off in raw if on['track']==n['track'] and on['sequence']==n['on_sequence'] and off['sequence']==n['off_sequence']]
 assert len(matches)==1
 on,off=matches[0]
 for k,v in [('midi_note',on['note']),('channel',on['channel']),('velocity',on['velocity']),('on_tick',on['tick']),('off_tick',off['tick']),('off_type',off['type']),('off_velocity',off['velocity'])]:assert n[k]==v,(n['note_id'],k)
 for t,field,pfield in [(on['tick'],'source_on_sec','note_on'),(off['tick'],'source_off_sec','note_off')]:
  assert abs(n[field]-t*428571/384/1e6)<1e-12
  assert abs(n[pfield]-n[field]-.35)<1e-12
 model=dict(left=n['hand']=='L',note=n['midi_note'],time=n['source_on_sec']*1000,duration=(n['source_off_sec']-n['source_on_sec'])*1000,velocity=n['velocity'])
 assert 'finger' not in model and model['duration']>0
 inputs.append(model)
 bindings.append(dict(model_input_index=i,note_id=n['note_id'],hand_assignment_authority='Existing validated timeline; not predicted',source_timeline_note=n,midi_note_on=on,midi_note_off=off,model_input=model,conversion=dict(time='source_on_sec * 1000',duration='(source_off_sec - source_on_sec) * 1000',presentation_lead_included=False)))
assert sorted(n['note_id'] for n in tl['notes'])==[f'L{i:02}' for i in range(7)]+[f'R{i:02}' for i in range(16)]
assert sum(n['hand']=='R' for n in tl['notes'])==16
assert len({(x['midi_note_on']['track'],x['midi_note_on']['sequence']) for x in bindings})==23
assert len({(x['midi_note_off']['track'],x['midi_note_off']['sequence']) for x in bindings})==23
result=dict(task='PIANO_AUTOMATIC_FINGERING_INFERENCE_POC_R1',source_timeline=str(TL),source_timeline_sha256=sha(TL),source_midi=str(MID),source_midi_sha256=sha(MID),ppq=384,tempo_events=tempo,time_signatures=sigs,source_tick_range=[0,4608],source_duration_sec=5.142852,note_count=23,right_count=16,left_count=7,note_message_count=46,boundary_policy='Include notes starting before tick 4608 and their corresponding releases at or before 4608; exclude next measure NOTE_ON at 4608',finger_constraints_provided=False,bindings=bindings)
dump('SOURCE_EVENT_BINDINGS.json',result);dump('MODEL_INPUT_UNCONSTRAINED.json',inputs)
print(json.dumps(dict(input_identity='PASS',notes=23,note_messages=46,midi_sha256=sha(MID),timeline_sha256=sha(TL),mido_version=str(mido.version_info))))

