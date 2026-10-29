import sys,json,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;OLD=O.parent/'hands_fingering_inference_poc_r1'
sys.path.insert(0,str(O/'evidence/pianoplayer'))
from pianoplayer.hand import Hand
from pianoplayer.models import INote,keypos
b=json.loads((OLD/'SOURCE_EVENT_BINDINGS.json').read_text())
start=time.perf_counter();result={};settings={}
for side,label in [('R','right'),('L','left')]:
 source=sorted([x for x in b['bindings'] if x['source_timeline_note']['hand']==side],key=lambda x:(x['source_timeline_note']['on_tick'],x['model_input']['note']))
 notes=[]
 for i,x in enumerate(source):
  n=x['source_timeline_note'];group=[q for q in source if q['source_timeline_note']['on_tick']==n['on_tick']]
  a=INote(name=n['note_name'][:-1],pitch=n['midi_note'],octave=n['midi_note']//12,time=n['source_on_sec'],duration=n['source_off_sec']-n['source_on_sec'],noteID=i,measure=n['measure'],isBlack=n['key_color']=='BLACK',isChord=len(group)>1,NinChord=len(group),chordnr=group.index(x),chordID=n['on_tick'],fingering=0)
  # Use the author's note-name geometry function; MIDI helper treats semitones as white-key widths.
  a.x=keypos(a);notes.append(a)
 original=[(n.pitch,n.time,n.duration,n.x) for n in notes]
 hand=Hand(notes,side=label,size='M');hand.verbose=False;hand.generate(start_measure=1,nmeasures=4)
 assert original==[(n.pitch,n.time,n.duration,n.x) for n in notes]
 assert all(type(n.fingering)==int and 1<=n.fingering<=5 for n in notes)
 result[side]=[dict(note_id=x['note_id'],finger=a.fingering,reported_window_cost=a.cost) for x,a in zip(source,notes)]
 settings[side]=dict(size='M',depth=9,autodepth=True,preserve_posture_memory=False,chord_stagger_seconds=0,key_geometry='Unmodified author keypos(note-name); not keypos_midi')
out=dict(route='Unmodified PianoPlayer Hand.generate',git_revision=json.loads((O/'evidence/pianoplayer_tree.json').read_text())['sha'],runtime_seconds=time.perf_counter()-start,settings=settings,hands=result,input_attrs_unchanged=True,trained_weights_required=False)
(O/'PIANOPLAYER_RAW_OUTPUT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(out))
