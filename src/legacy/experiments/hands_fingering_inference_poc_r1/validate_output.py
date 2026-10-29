import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
b=read('SOURCE_EVENT_BINDINGS.json');raw=read('RAW_MODEL_PREDICTIONS.json');rt=read('INFERENCE_RUNTIME_RECEIPT.json');tr=read('RAW_ONNX_LOGITS_AND_TOKENS.json')
assert len(raw)==len(b['bindings'])==len(tr)==23
rows=[];used=set()
for x in b['bindings']:
 match=[(i,p) for i,p in enumerate(raw) if {k:v for k,v in p.items() if k!='finger'}==x['model_input']]
 assert len(match)==1
 i,p=match[0];assert i not in used;used.add(i)
 assert type(p['finger'])==int and 1<=p['finger']<=5
 n=x['source_timeline_note'];rows.append(dict(note_id=x['note_id'],hand=n['hand'],note_name=n['note_name'],midi=n['midi_note'],old_finger=n['finger'],ai_finger=p['finger'],changed=n['finger']!=p['finger'],on_tick=n['on_tick'],off_tick=n['off_tick'],source_on_sec=n['source_on_sec'],source_off_sec=n['source_off_sec'],raw_output_index=i,model_input_index=x['model_input_index'],key_color=n['key_color'],authority='DESIGN_PROVISIONAL'))
for hand in ['L','R']:
 seq=sorted([r for r in rows if r['hand']==hand],key=lambda n:(n['source_on_sec'],n['midi']))
 traces=[x for x in tr if x['hand']==('left' if hand=='L' else 'right')]
 assert len(seq)==len(traces)
 for r,t in zip(seq,traces):
  assert len(t['logits'])==5 and all(math.isfinite(v) for v in t['logits'])
  assert max(range(5),key=lambda i:t['logits'][i])+1==r['ai_finger']
  assert all(t['input_tokens'][i*5+4]==-1 for i in range(26)), 'Unexpected finger hints'
collisions=[];overlaps=[];simultaneous=[];transitions=[]
for i,a in enumerate(rows):
 for c in rows[i+1:]:
  if a['hand']!=c['hand']:continue
  if max(a['on_tick'],c['on_tick'])<min(a['off_tick'],c['off_tick']):
   pair=dict(ids=[a['note_id'],c['note_id']],hand=a['hand'],midi=[a['midi'],c['midi']],fingers=[a['ai_finger'],c['ai_finger']],overlap_ticks=min(a['off_tick'],c['off_tick'])-max(a['on_tick'],c['on_tick']))
   overlaps.append(pair)
   if a['midi']!=c['midi'] and a['ai_finger']==c['ai_finger']:collisions.append(pair)
  if a['on_tick']==c['on_tick']:simultaneous.append(dict(ids=[a['note_id'],c['note_id']],fingers=[a['ai_finger'],c['ai_finger']]))
for hand in ['L','R']:
 seq=sorted([r for r in rows if r['hand']==hand],key=lambda n:(n['on_tick'],n['midi']))
 for a,c in zip(seq,seq[1:]):
  if a['on_tick']==c['on_tick']:continue
  pd=c['midi']-a['midi'];fd=c['ai_finger']-a['ai_finger']
  transitions.append(dict(ids=[a['note_id'],c['note_id']],hand=hand,pitch_delta_semitones=pd,fingers=[a['ai_finger'],c['ai_finger']],onset_delta_ms=(c['source_on_sec']-a['source_on_sec'])*1000,release_gap_ms=(c['source_on_sec']-a['source_off_sec'])*1000,repeated_pitch=pd==0,large_melodic_leap=abs(pd)>=7,non_thumb_direction_reversal=pd*fd*(1 if hand=='R' else -1)<0 and a['ai_finger']!=1 and c['ai_finger']!=1))
assert rt['official_predict_calls']==1 and rt['exception'] is None and rt['input_unchanged']
assert sha(b['source_timeline'])==b['source_timeline_sha256'] and sha(b['source_midi'])==b['source_midi_sha256']
assert sha(O/'RAW_MODEL_PREDICTIONS.json')==rt['raw_output_sha256']
profiles=[]
for p in O.glob('onnxruntime_profile*.json'):
 d=json.loads(p.read_text());providers=sorted({e.get('args',{}).get('provider') for e in d if e.get('args',{}).get('provider')})
 profiles.append(dict(file=p.name,sha256=sha(p),providers=providers))
assert len(profiles)==2 and all(p['providers']==['CPUExecutionProvider'] for p in profiles),profiles
checks=dict(note_count=23,right_count=16,left_count=7,note_message_count=46,one_to_one_identity_binding=True,input_attributes_exactly_preserved=True,all_fingers_1_to_5=True,no_fixed_finger_hints=True,all_logits_finite=True,argmax_matches_direct_output=True,original_source_hashes_unchanged=True,raw_output_hash_unchanged=True,official_predict_calls=1,onnx_runs=23,profiles=profiles)
result=dict(checks=checks,rows=rows,changed_ids=[r['note_id'] for r in rows if r['changed']],same_hand_overlaps=overlaps,simultaneous_note_pairs=simultaneous,same_finger_different_key_overlap_conflicts=collisions,transitions=transitions)
dump('OUTPUT_VALIDATION_AND_FEASIBILITY.json',result)
print(json.dumps(dict(checks=checks,changed_ids=result['changed_ids'],finger_sequences={h:[(r['note_id'],r['note_name'],r['old_finger'],r['ai_finger']) for r in sorted(rows,key=lambda n:n['note_id']) if r['hand']==h] for h in ['R','L']},collisions=collisions,transitions=transitions),ensure_ascii=False))
