from pathlib import Path
import json,numpy as np
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False,default=lambda v:v.item()),encoding='utf-8')
M=read('CONTACT_MEASUREMENTS_R1.json');keys=read('KEYBOARD_88_KEY_TABLE_R1.json')['keys'];A=np.load(P/'hand_motion_canonical.npz');policy=read('CONTACT_TOLERANCE_POLICY_R1.json');tol=policy['CONTACT_HORIZONTAL_TOLERANCE_MM']/1000
for c in M['chord_observations']:
 intervals=[]
 for n in c['active_assigned_notes']:
  k=keys[n['midi_note']-21];p=A[c['hand']+'_pads'][c['observation'],n['finger']-1,0];surfaces=k['key_top_playable_surface'];intervals.append([min(s['xmin'] for s in surfaces)-p-tol,max(s['xmax'] for s in surfaces)-p+tol])
 lo=max(a for a,b in intervals);hi=min(b for a,b in intervals)
 c['translation_feasibility_x']={'intervals_m':intervals,'intersection_m':[lo,hi],'impossible_even_with_any_XYZ_translation':bool(lo>hi),'disjoint_gap_mm':max(0,lo-hi)*1000,'bound':'Conservative: allows whole key bounding width at any depth and ±2mm outside. Empty intersection proves translation-only impossibility at fixed static orientation; nonempty does not prove contact.'}
for s in ['R','L']:
 rows=[c for c in M['chord_observations'] if c['hand']==s];M['summary'][s]['translation_only_x_infeasible_chord_observations']=sum(c['translation_feasibility_x']['impossible_even_with_any_XYZ_translation'] for c in rows)
dump('CONTACT_MEASUREMENTS_R1.json',M)
tl=read('PERFORMANCE_TIMELINE_R1.json');ts=np.arange(421)/60+11.5;short=[n['note_id'] for n in tl['notes'] if not np.any((ts>=n['source_on_sec'])&(ts<n['source_off_sec']))]
key=read('KEY_EVENT_ANIMATION_R1.json');key['sub_60Hz_note_visibility_audit']={'unsampled_note_ids':short,'count':len(short),'meaning':'Original exact events preserved in timeline; these short notes have no held sample at fixed60Hz preview and therefore may not visibly depress. Preview is not subframe key-response validation.'};dump('KEY_EVENT_ANIMATION_R1.json',key)
print(json.dumps(M['summary'],indent=2));print('SHORT_NOTES_WITH_NO_60HZ_HELD_SAMPLE',short)
