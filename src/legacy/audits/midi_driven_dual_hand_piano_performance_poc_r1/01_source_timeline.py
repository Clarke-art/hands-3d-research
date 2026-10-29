from pathlib import Path
import sys,json,hashlib,shutil,collections
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PRE=P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1';PIANO=ROOT.parent/'piano/release/grand-piano-v1.1-rc-candidate'
sys.path.insert(0,str(P/'_deps'));import mido
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=read(P.parent/'piano_keyboard_low_dof_root_pose_validation_r1/PROTECTED_INPUTS_BEFORE_R1.json')
for f,v in before.items():assert sha(f)==v
for f in (P.parent/'piano_keyboard_low_dof_root_pose_validation_r1').iterdir():
 if f.is_file():before[str(f)]=sha(f)
dump('PROTECTED_INPUTS_BEFORE_R1.json',before)
for n in ['KEYBOARD_AUTHORITY_R1.json','KEYBOARD_COORDINATE_FRAME_R1.json','KEYBOARD_88_KEY_TABLE_R1.json','CONTACT_TOLERANCE_POLICY_R1.json','FINGERTIP_CONTACT_MARKERS_R1.json']:
 shutil.copyfile(PRE/n,P/n)
shutil.copyfile(PIANO/'data/V1_1D_PIANO_SAMPLE_MANIFEST.json',P/'source/PIANO_SAMPLE_MANIFEST.json')
shutil.copyfile(PIANO/'assets/audio/vcsl-kawai-grand/SOURCE_AND_LICENSE.md',P/'source/PIANO_SAMPLE_LICENSE.md')
m=mido.MidiFile(P/'source/anna-magdalena-22.mid');assert m.ticks_per_beat==384
allnotes=[];meta=[];controls=[]
for track,tr in enumerate(m.tracks):
 tick=0;held={}
 for msg in tr:
  tick+=msg.time
  if msg.is_meta:meta.append({'track':track,'tick':tick,**msg.dict()})
  elif msg.type=='control_change':controls.append({'track':track,'tick':tick,**msg.dict()})
  elif msg.type=='note_on' and msg.velocity:
   assert (msg.channel,msg.note) not in held;held[msg.channel,msg.note]=(tick,msg.velocity)
  elif msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0):
   on,vel=held.pop((msg.channel,msg.note));allnotes.append({'track':track,'channel':msg.channel,'midi_note':msg.note,'on_tick':on,'off_tick':tick,'velocity':vel})
 assert not held
assert [(x['tick'],x['tempo']) for x in meta if x['type']=='set_tempo']==[(0,500000)]
excerpt=sorted([x for x in allnotes if x['on_tick']<1536],key=lambda x:(x['on_tick'],x['track']))
expected={1:[(81,0,384),(79,384,480),(78,480,576),(76,576,672),(74,672,768)],2:[(38,0,192),(50,192,384),(38,384,576),(50,576,768)]}
for tr in [1,2]:
 actual=[(x['midi_note'],x['on_tick'],x['off_tick']) for x in excerpt if x['track']==tr]
 assert actual==[ (n,a+bar*768,b+bar*768) for bar in range(2) for n,a,b in expected[tr]],(tr,actual)
offset=.7;notes=[];events=[]
for i,x in enumerate(excerpt):
 hand='R' if x['track']==1 else 'L';finger={81:5,79:4,78:3,76:2,74:1}[x['midi_note']] if hand=='R' else {38:5,50:1}[x['midi_note']]
 n={**x,'note_id':f'n{i:02}','measure':1+x['on_tick']//768,'time':offset+x['on_tick']/768,'note_on':offset+x['on_tick']/768,'note_off':offset+x['off_tick']/768,'hand':hand,'finger':finger,'key_index':x['midi_note']-21,'fingering_authority':'DESIGNED_PROVISIONAL_NOT_GROUND_TRUTH'};notes.append(n)
 for typ,t in [('NOTE_ON',n['note_on']),('NOTE_OFF',n['note_off'])]:events.append({'time':t,'type':typ,'note_id':n['note_id'],'midi_note':n['midi_note'],'velocity':n['velocity'] if typ=='NOTE_ON' else 0,'source_note_on_velocity':n['velocity'],'hand':hand,'finger':finger,'key_index':n['key_index']})
timeline={'schema':'MIDI_PERFORMANCE_TIMELINE_1.0','song':'Musette, BWV Anh.126','source_midi_sha256':sha(P/'source/anna-magdalena-22.mid'),'measures':[1,2],'ppq':384,'tempo_us_per_quarter':500000,'bpm':120,'time_signature':[2,4],'source_excerpt_ticks':[0,1536],'source_music_duration_sec':2,'presentation_lead_in_sec':offset,'presentation_duration_sec':3.4,'timebase':'seconds from a single shared presentation clock; original MIDI times + constant 0.7s lead-in','notes':notes,'events':sorted(events,key=lambda e:(e['time'],e['type']=='NOTE_ON')),'pedal':[],'hand_authority':'Official LilyPond Staff one/voiceone = right, Staff two/voicetwo = left; checked PDF and exact MIDI tracks, not pitch split','original_timing_velocity_preserved':True}
dump('PERFORMANCE_TIMELINE_R1.json',timeline)
dump('PROVISIONAL_FINGERING_PLAN_R1.json',{'status':'DESIGNED_PROVISIONAL_REQUIRES_HUMAN_REVIEW','official_fingering_present':False,'source_notes_modified':False,'automatic_fingering_search':False,'selection_reason':'Measures3–4 add a rapid register shift after 16ths; choose permitted continuous opening2 bars for first bounded POC, retaining all original notes and both complete staves.','R':'D5–A5 five-finger position; A5=5 G5=4 F#5=3 E5=2 D5=1; thumb on D5, middle on black F#5.','L':'D2=5, D3=1 alternating octave; plan shared palm and modest forearm movement instead of simultaneous forced octave stretch.','rows':[{k:n[k] for k in ['note_id','measure','note_on','note_off','hand','midi_note','finger']} for n in notes]})
dump('SOURCE_MIDI_AUDIT_R1.json',{'format':m.type,'ppq':m.ticks_per_beat,'tracks':len(m.tracks),'metadata':meta,'controls':controls,'all_source_notes':len(allnotes),'excerpt_notes':len(notes),'exact_lilypond_measure_1_2_comparison':'PASS','PDF_visual_check':'PASS by agent; no printed finger numbers','ranges':{s:[min(n['midi_note'] for n in notes if n['hand']==s),max(n['midi_note'] for n in notes if n['hand']==s)] for s in ['R','L']},'same_hand_max_polyphony':1,'dual_hand_max_polyphony':2,'fingering_midi_field':False,'files':{f.name:sha(f) for f in (P/'source').iterdir() if f.is_file()}})
print('TIMELINE',len(notes),'notes',len(events),'events; exact score comparison PASS')
