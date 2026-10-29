from phrase_common import *
import mido
midi=c.P/'source/anna-magdalena-22.mid';m=mido.MidiFile(midi)
meta=[];raw=[]
for i,tr in enumerate(m.tracks):
 tick=0;held={}
 for msg in tr:
  tick+=msg.time
  if msg.is_meta:meta.append({'track':i,'tick':tick,**msg.dict()})
  elif msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note]=(tick,msg.velocity)
  elif msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0):
   on,v=held.pop((msg.channel,msg.note));raw.append(dict(track=i,channel=msg.channel,midi_note=msg.note,on_tick=on,off_tick=tick,velocity=v))
 assert not held
assert m.ticks_per_beat==384
assert [(a['tick'],a['tempo']) for a in meta if a['type']=='set_tempo']==[(0,500000)]
assert [(a['tick'],a['numerator'],a['denominator']) for a in meta if a['type']=='time_signature']==[(0,2,4)]
selected=sorted([n for n in raw if n['on_tick']<1536],key=lambda n:(n['on_tick'],n['track']))
assert selected==[{k:n[k] for k in ['track','channel','midi_note','on_tick','off_tick','velocity']} for n in c.TL['notes']]
assert sha(midi)==c.TL['source_midi_sha256']
dump('PERFORMANCE_TIMELINE.json',{**c.TL,'presentation_duration_sec':END-START,'render_source_clock_window':[START,END]})
dump('SOURCE_MIDI_VERIFICATION.json',{'path':str(midi),'sha256':sha(midi),'ppq':m.ticks_per_beat,'metadata':meta,'selected':selected,'selected_count':len(selected),'original_timeline_exact_match':True,'music_source_seconds':[0,2],'presentation_source_seconds':[.7,2.7],'render_source_seconds':[START,END],'source_same_hand_overlaps':0,'source_dual_hand_peak_polyphony':2,'key_return_overlap_seconds':.07,'fingering_authority':'Existing designed provisional fingering; NOT MIDI encoded or performer ground truth'})
before=read(LAST/'PROTECTED_INPUTS_BEFORE_R1.json');assert all(sha(f)==h for f,h in before.items())
for folder in [o.STATIC,LAST,OLD]:
 for f in folder.iterdir():
  if f.is_file():before[str(f)]=sha(f)
for s in ['R','L']:
 base=read(o.ROOT/'production_spec'/('RIGHT_HAND_PRODUCT_BASELINE.json' if s=='R' else 'LEFT_HAND_PRODUCT_BASELINE.json'))
 f=o.ROOT/base['asset']['path'];assert sha(f)==base['asset']['sha256'];before[str(f)]=sha(f)
dump('PROTECTED_INPUTS_BEFORE.json',before)
names={38:'D2',50:'D3',81:'A5',79:'G5',78:'F#5',76:'E5',74:'D5'}
lines=['# SHORT_PHRASE_EVENT_AND_FINGERING','', '原 Musette MIDI：`'+str(midi)+'`；SHA256 `'+sha(midi)+'`。直接重新解析：384 PPQ、120 BPM、2/4，tempo 不变。','', '连续第 1–2 小节，源 tick 0–1536 / 0–2s；保留全部 18 个双手事件。审核窗口源展示时钟 0.4–3.1s，音乐起点 0.7s，成片时长 2.7s。','', '右手 Track 1：A5→G5→F#5→E5→D5，指法5→4→3→2→1；左手 Track 2：D2→D3→D2→D3，指法5→1→5→1，两小节均相同。指法沿用设计候选，非 MIDI 自带指法。','', '|ID|小节|手|音符|指|源 on/off tick|源 on/off 秒|审核视频 on/off 秒|','|---|---|---|---|---|---|---|---|']
for n in c.TL['notes']:lines.append(f"|{n['note_id']}|{n['measure']}|{n['hand']}|{names[n['midi_note']]}|{n['finger']}|{n['on_tick']}/{n['off_tick']}|{n['on_tick']/768:.3f}/{n['off_tick']/768:.3f}|{n['note_on']-START:.3f}/{n['note_off']-START:.3f}|")
lines+=['','同手 MIDI 音符不重叠；双手最大两音同时发声。旧琴键规则保留 35ms 下沉、70ms 回弹，因此交接存在70ms回弹重叠。NOTE_OFF 先于同刻 NOTE_ON；不改变原时值、速度、键身份。']
(P/'SHORT_PHRASE_EVENT_AND_FINGERING.md').write_text('\n'.join(lines),encoding='utf8')
dump('GENERATION_LOCK.json',{'candidate_count':1,'restarts':0,'left':'Unchanged 29-parameter fitted coefficients, event scheduler extended to all 8 bass events','right':'One bounded whole-sequence fit of reusable contact/pressure coefficient pairs for five fingers, shared across both measures; 40 parameters; inherited FK/skin/quintic/Bernstein/least_squares','root_right':'Approved R1 fixed','root_left':'Inherited unchanged D2 envelope and 29 fitted coefficients','right_contact_targets':'Frozen key center x, y from approved R1 prepared pad (R2 for middle); transported with actual key; 0.5mm design gap','bounds':'Inherited static engineering joint domain; ±12deg from approved preparation; no post-failure adjustment','manual_per_note_adjustment':False,'per_frame_IK':False,'max_nfev':60,'post_smoothing':False,'metric_3mm':'Diagnostic only; no automatic product rejection','freeze_hash_count':len(before),'scripts':{f.name:sha(f) for f in P.glob('*.py')}})
print('ORIGINAL_MIDI_VERIFIED',len(selected),'notes; protected',len(before),flush=True)
