import json,sys,hashlib,math
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O/'evidence/pianoplayer'))
from pianoplayer.hand import Hand
from pianoplayer.models import INote,keypos
b=json.loads((O/'SOURCE_EVENT_BINDINGS.json').read_text());scores=json.loads((O/'CONDITIONAL_MODEL_PATH_SCORES.json').read_text());pp=json.loads((O/'PIANOPLAYER_RAW_OUTPUT.json').read_text())
notes={x['note_id']:x['source_timeline_note'] for x in b['bindings']}
results=[]
for path in scores['paths']:
 fingers=path['fingers']; conflicts=[];chords=[];transitions=[];geometry={};native={}
 for hand,side in [('R','right'),('L','left')]:
  seq=sorted([n for n in notes.values() if n['hand']==hand],key=lambda n:(n['on_tick'],n['midi_note']))
  inotes=[];fseq=[]
  for i,n in enumerate(seq):
   group=[s for s in seq if s['on_tick']==n['on_tick']]
   a=INote(name=n['note_name'][:-1],pitch=n['midi_note'],octave=n['midi_note']//12,time=n['source_on_sec'],duration=n['source_off_sec']-n['source_on_sec'],isBlack=n['key_color']=='BLACK',isChord=len(group)>1,chordID=n['on_tick'],NinChord=len(group),chordnr=group.index(n));a.x=keypos(a)
   geometry[n['note_id']]=a.x;inotes.append(a);fseq.append(fingers[n['note_id']])
  h=Hand(inotes,side=side,size='M');h.depth=len(inotes);h.autodepth=False
  if hand=='L':
   for a in inotes:a.x=-a.x
  native[hand]=h.ave_velocity(fseq,inotes)
  for i,a in enumerate(seq):
   for c in seq[i+1:]:
    if a['midi_note']==c['midi_note']:continue
    if max(a['on_tick'],c['on_tick'])<min(a['off_tick'],c['off_tick']) and fingers[a['note_id']]==fingers[c['note_id']]:conflicts.append(dict(ids=[a['note_id'],c['note_id']],kind='same-finger overlapping distinct keys'))
   if i>0:
    prev=seq[i-1]
    if prev['on_tick']==a['on_tick']:continue
    fa=fingers[prev['note_id']];fc=fingers[a['note_id']];dp=a['midi_note']-prev['midi_note'];dc=geometry[a['note_id']]-geometry[prev['note_id']]
    nonthumb=dp*(fc-fa)*(1 if hand=='R' else -1)<0 and fa>1 and fc>1
    inferred_shift=dc-((h.frest[fc]-h.frest[fa])*(1 if hand=='R' else -1))
    flags=[]
    if nonthumb:flags.append('NON_THUMB_DIRECTION_REVERSAL_REQUIRES_REPOSITION_REVIEW')
    if dp and fa==fc:flags.append('SAME_FINGER_DIFFERENT_KEY_REQUIRES_RELEASE_AND_MOVE')
    if abs(dp)>=7:flags.append('MELODIC_LEAP_HAND_POSITION_CHANGE_EXPECTED')
    if dp==0:flags.append('REPEATED_NOTE_RELEASE_RESTRIKE_REQUIRED')
    if fa==1 and fc>1 and dp*(1 if hand=='R' else -1)<0:flags.append('POTENTIAL_FINGER_OVER_THUMB_TECHNIQUE')
    if fc==1 and fa>1 and dp*(1 if hand=='R' else -1)>0:flags.append('POTENTIAL_THUMB_UNDER_TECHNIQUE')
    transitions.append(dict(ids=[prev['note_id'],a['note_id']],hand=hand,pitch_delta_semitones=dp,fingers=[fa,fc],onset_delta_ms=(a['source_on_sec']-prev['source_on_sec'])*1000,release_gap_ticks=a['on_tick']-prev['off_tick'],relaxed_anchor_shift_cm=inferred_shift,flags=flags))
  for onset in sorted({n['on_tick'] for n in seq}):
   group=[n for n in seq if n['on_tick']==onset]
   if len(group)>1:
    fs=[fingers[n['note_id']] for n in group];span=max(geometry[n['note_id']] for n in group)-min(geometry[n['note_id']] for n in group)
    chords.append(dict(hand=hand,ids=[n['note_id'] for n in group],fingers=fs,all_fingers_unique=len(fs)==len(set(fs)),span_cm=span,configured_hand_max_span_cm=h.max_span_cm,within_approximate_hand_span=span<=h.max_span_cm))
    if span>h.max_span_cm:conflicts.append(dict(ids=[n['note_id'] for n in group],kind='chord exceeds configured approximate span'))
 results.append(dict(path_name=path['path_name'],model_conditional_nll=path['conditional_nll'],model_conditional_nll_by_hand=path['conditional_nll_by_hand'],native_whole_hand_motion_cost=native,native_cost_units='Author ave_velocity approximate weighted cm/s; full right16 and left7; separate units from NLL',nonthumb_reversal_count=sum('NON_THUMB_DIRECTION_REVERSAL_REQUIRES_REPOSITION_REVIEW' in t['flags'] for t in transitions),hard_conflicts=conflicts,chords=chords,transitions=transitions))
costs={p['path_name']:p for p in results};cp=costs['pianoplayer_sequence']
assert not cp['hard_conflicts'] and cp['nonthumb_reversal_count']==0
assert len(pp['hands']['R'])==16 and len(pp['hands']['L'])==7
profiles=[]
for p in O.glob('score_cpu*.json'):
 d=json.loads(p.read_text());providers=sorted({e.get('args',{}).get('provider') for e in d if e.get('args',{}).get('provider')});assert providers==['CPUExecutionProvider'];profiles.append(dict(file=p.name,providers=providers))
assert len(profiles)==2
output_notes=[]
for x in b['bindings']:
 n=x['source_timeline_note'];out=dict(note_id=x['note_id'],hand=n['hand'],note_name=n['note_name'],midi=n['midi_note'],velocity=n['velocity'],channel=n['channel'],source_on_sec=n['source_on_sec'],source_off_sec=n['source_off_sec'],on_tick=n['on_tick'],off_tick=n['off_tick'],finger=scores['paths'][2]['fingers'][x['note_id']],model_input=x['model_input'],authority='DESIGN_PROVISIONAL')
 output_notes.append(out)
assert len(output_notes)==23 and len({n['note_id'] for n in output_notes})==23
candidate=dict(candidate_id='C01_PIANOPLAYER',generation='Unmodified existing PianoPlayer Hand.generate; finite lookahead effort search; no training and no fingering anchors',git_revision=pp['git_revision'],generation_seconds=pp['runtime_seconds'],settings=pp['settings'],model_scoring_role='Path-specific Lumikey conditional evaluation AFTER generation; model NLL not used by PianoPlayer optimizer and no joint model-motion global optimum claimed',scores=cp,authority='DESIGN_PROVISIONAL',status='SEQUENCE_POC_PASS',notes=output_notes,adjacent_phrase_context_role='Real following MIDI notes inspected for preparation; not optimized or scored beyond the original23 test notes',known_limitations=['Finite horizon and tail padding, not exact full-piece DP','Author prunes non-thumb reverse transitions but permits thumb techniques; some valid repositionings may be excluded','No wrist, hand trajectory, key recovery or physical feasibility proof','Held-note conflicts independently validated for this input; not guaranteed on arbitrary polyphony','Model/code commercial weight rights remain unresolved'])
(O/'SEQUENCE_CANDIDATES.json').write_text(json.dumps(dict(task='PIANO_SEQUENCE_FINGERING_PLANNING_R1',availability='AVAILABLE',candidate_count=1,max_candidates=3,test_note_count=23,note_message_count=46,candidates=[candidate]),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(O/'WHOLE_SEQUENCE_COST_AND_RISK.json').write_text(json.dumps(dict(paths=results,cpu_profiles=profiles),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(costs=[dict(path=p['path_name'],nll=p['model_conditional_nll'],motion=p['native_whole_hand_motion_cost'],reversals=p['nonthumb_reversal_count'],hard_conflicts=p['hard_conflicts']) for p in results],candidate_right=[n['finger'] for n in output_notes if n['hand']=='R']),ensure_ascii=False))
