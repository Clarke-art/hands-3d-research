from pathlib import Path
import sys,json,hashlib,collections,csv
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/_deps'));import mido

def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
midi=P/'source/anna-magdalena-04.mid';m=mido.MidiFile(midi);meta=[];controls=[];notes=[];names={};endtick={}
for ti,tr in enumerate(m.tracks):
 tick=0;held=collections.defaultdict(collections.deque)
 for msg in tr:
  tick+=msg.time
  if msg.is_meta:
   meta.append({'track':ti,'tick':tick,**msg.dict()})
   if msg.type=='track_name':names[ti]=msg.name
  elif msg.type=='control_change':controls.append({'track':ti,'tick':tick,**msg.dict()})
  elif msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note].append((tick,msg.velocity))
  elif msg.type=='note_off' or (msg.type=='note_on' and not msg.velocity):
   on,vel=held[msg.channel,msg.note].popleft();notes.append({'track':ti,'channel':msg.channel,'midi':msg.note,'on_tick':on,'off_tick':tick,'velocity':vel})
 endtick[ti]=tick;assert all(not queue for queue in held.values())
assert m.type==1 and m.ticks_per_beat==384 and names[1]=='one:' and names[2]=='two:'
time_sigs=[(x['tick'],x['numerator'],x['denominator']) for x in meta if x['type']=='time_signature'];assert time_sigs==[(0,3,4)]
tempo_map=sorted([(x['tick'],x['tempo']) for x in meta if x['type']=='set_tempo']);assert tempo_map==[(0,428571)]
ppq=m.ticks_per_beat;bar_ticks=ppq*3;start=0;end=bar_ticks*16

def sec(tick):
 seconds=0.;last=0;tempo=500000
 for tt,tv in tempo_map:
  if tt>tick:break
  seconds+=mido.tick2second(tt-last,ppq,tempo);last=tt;tempo=tv
 return seconds+mido.tick2second(tick-last,ppq,tempo)
def pitch(n):return ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][n%12]+str(n//12-1)
selected=sorted([n for n in notes if start<=n['on_tick']<end],key=lambda n:(n['on_tick'],n['track'],n['midi']))
assert all(n['off_tick']<=end for n in selected) and endtick[1]==endtick[2]==bar_ticks*32
for i,n in enumerate(selected):n.update(note_id=f'n{i:03d}',hand='R' if n['track']==1 else 'L',measure=1+n['on_tick']//bar_ticks,note_name=pitch(n['midi']),on_sec=sec(n['on_tick']),off_sec=sec(n['off_tick']),duration_ticks=n['off_tick']-n['on_tick'],key_index=n['midi']-21)
assert sorted(n['midi'] for n in selected if n['hand']=='L' and n['on_tick']==0)==[55,59,62]
assert [(n['midi'],n['on_tick'],n['off_tick']) for n in selected if n['hand']=='R' and n['on_tick']<bar_ticks]==[(74,0,384),(67,384,576),(69,576,768),(71,768,960),(72,960,1152)]
byhand={};chords=[];overlaps=[]
for s in ['L','R']:
 ns=[n for n in selected if n['hand']==s];onsets=sorted(set(n['on_tick'] for n in ns));events=sorted([(n['off_tick'],0,n) for n in ns]+[(n['on_tick'],1,n) for n in ns],key=lambda x:(x[0],x[1]));active={};peak=0
 for t,typ,n in events:
  if typ:
   if active:overlaps.append({'hand':s,'new_note':n['note_id'],'on_tick':t,'active_before_new_note':list(active),'simultaneous_same_onset':all(v['on_tick']==t for v in active.values())})
   active[n['note_id']]=n;peak=max(peak,len(active))
  else:active.pop(n['note_id'],None)
 for t in onsets:
  group=[n for n in ns if n['on_tick']==t]
  if len(group)>1:chords.append({'hand':s,'measure':1+t//bar_ticks,'on_tick':t,'on_sec':sec(t),'midi':[n['midi'] for n in group],'note_names':[n['note_name'] for n in group],'off_ticks':[n['off_tick'] for n in group],'note_ids':[n['note_id'] for n in group],'span_semitones':max(n['midi'] for n in group)-min(n['midi'] for n in group)})
 unique=sorted(set(n['midi'] for n in ns));byhand[s]={'notes':len(ns),'onset_groups':len(onsets),'unique_midis':unique,'unique_pitch_names':[pitch(x) for x in unique],'unique_pitch_count':len(unique),'range_midis':[min(unique),max(unique)],'range_names':[pitch(min(unique)),pitch(max(unique))],'range_semitones':max(unique)-min(unique),'peak_polyphony':peak,'simultaneous_onset_groups':sum(g['hand']==s for g in chords),'onset_step_min_ticks':min(b-a for a,b in zip(onsets,onsets[1:])),'onset_step_min_sec':min(sec(b)-sec(a) for a,b in zip(onsets,onsets[1:])),'duration_histogram_ticks':dict(sorted(collections.Counter(n['duration_ticks'] for n in ns).items())),'sustained_half_note_or_more_count':sum(n['duration_ticks']>=ppq*2 for n in ns),'different_onset_held_overlap_instances':sum(o['hand']==s and not o['simultaneous_same_onset'] for o in overlaps)}
all_events=sorted([(n['off_tick'],0,n) for n in selected]+[(n['on_tick'],1,n) for n in selected],key=lambda x:(x[0],x[1]));active={};peak=0
for t,typ,n in all_events:
 if typ:active[n['note_id']]=n;peak=max(peak,len(active))
 else:active.pop(n['note_id'],None)
barrows=[]
for bar in range(1,17):
 ns=[n for n in selected if n['measure']==bar];barrows.append({'measure':bar,'tick_range':[(bar-1)*bar_ticks,bar*bar_ticks],'sec_range':[sec((bar-1)*bar_ticks),sec(bar*bar_ticks)],'R_notes':sum(n['hand']=='R' for n in ns),'L_notes':sum(n['hand']=='L' for n in ns),'R_sequence':[{k:n[k] for k in ['note_id','note_name','on_tick','off_tick','duration_ticks']} for n in ns if n['hand']=='R'],'L_sequence':[{k:n[k] for k in ['note_id','note_name','on_tick','off_tick','duration_ticks']} for n in ns if n['hand']=='L']})
summary={'source_file':str(midi),'source_sha256':sha(midi),'format':m.type,'ppq':ppq,'metadata':meta,'controls':controls,'track_name_to_hand':{'1 one:':'R = LilyPond Staff one / voiceone','2 two:':'L = LilyPond Staff two / voicetwo including nested chord voice ii'},'hand_assignment_by_source_staff_not_pitch_split':True,'time_signature':[3,4],'tempo_us_per_quarter':428571,'display_score_bpm':140,'exact_MIDI_bpm':60000000/428571,'bar_ticks':bar_ticks,'source_notated_measures':[1,16],'source_tick_range_half_open':[start,end],'source_sec_range':[sec(start),sec(end)],'excerpt_duration_sec':sec(end)-sec(start),'note_on_count':len(selected),'note_off_count':len(selected),'event_count':len(selected)*2,'all_notes_original_velocity':sorted(set(n['velocity'] for n in selected)),'no_boundary_notes_clipped':True,'all_source_note_count':len(notes),'source_track_end_ticks':endtick,'source_full_duration_sec':m.length,'notated_first_section_repeat':'Score has volta2 first16 bars; source MIDI encodes first and second16-bar sections once, NOT repeats unfolded. Use first16 notated bars once; do not add replay.','no_anacrusis':True,'written_grace_note':'LilyPond bar8 graceB4 retained exactly as MIDI events; notation ornaments not expanded manually','by_hand':byhand,'simultaneous_chords':chords,'same_hand_overlap_instances':overlaps,'dual_hand_peak_polyphony':peak,'measure_rows':barrows,'notes':selected,'candidate_generated':False,'motion_solver_executed':False}
dump('MIDI_SCOPE_STATISTICS.json',summary)
with (P/'ORIGINAL_EVENTS_FIRST16.csv').open('w',newline='',encoding='utf-8-sig') as f:
 keys=list(selected[0]);w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(selected)
print(json.dumps({k:summary[k] for k in ['ppq','source_tick_range_half_open','source_sec_range','excerpt_duration_sec','note_on_count','by_hand','simultaneous_chords','dual_hand_peak_polyphony']},ensure_ascii=False,indent=2))
print('BAR_COUNTS',[(r['measure'],r['R_notes'],r['L_notes']) for r in barrows])
