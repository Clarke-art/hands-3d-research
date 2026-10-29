from pathlib import Path
import json,hashlib,csv,struct,math
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];SRC=ROOT/'references/piano_motion/pianovam_sample_r1';REC='2024-03-04_03-46-36'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=read(P/'KEYBOARD_RUNTIME_GEOMETRY_R1.json');auth=read(P/'KEYBOARD_AUTHORITY_R1.json');scale=auth['approved_unit_scale']['meanMetresPerUnit'];keys=raw['keys'];C4=next(k['manifest'] for k in keys if k['midi']==60)
origin=np.array([C4['pivot']['world'][0],C4['worldBounds']['max'][1],C4['worldBounds']['max'][2]])
B=np.array([[1,0,0],[0,0,-1],[0,1,0]],float)
def convert(p):return ((np.array(p)-origin)@B.T*scale).tolist()
names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
def name(n):return names[n%12]+str(n//12-1)
table=[]
for k in keys:
 m=k['manifest'];lo=np.array(m['worldBounds']['min']);hi=np.array(m['worldBounds']['max']);surfaces=[];geometry=[]
 for mesh in k['meshes']:
  v=np.array(convert(mesh['vertices']));a=v.min(0);b=v.max(0);surfaces.append({'xmin':float(a[0]),'xmax':float(b[0]),'ymin':float(a[1]),'ymax':float(b[1]),'z':float(b[2])});geometry.append(dict(mesh,vertices=v.tolist()))
 front=min(s['ymin'] for s in surfaces);back=max(s['ymax'] for s in surfaces)
 table.append({'key_index':m['midi']-21,'midi_note':m['midi'],'note_name':name(m['midi']),'color':m['color'],'semantic_identity':m['keyId'],'source_object':m['sourceObject'],'render_target':m['renderTarget'],'key_top_playable_surface':surfaces,'key_center':convert((lo+hi)/2),'front_extent':front,'back_extent':back,'width':float((hi[0]-lo[0])*scale),'press_direction':[0,0,-1],'press_pivot':convert(m['pivot']['world']),'press_axis':[1,0,0],'press_angle_rad':m['pressedTransform']['rotationRad'][0],'front_travel_mm':m['motionCalibration']['frontTravelEquivalentMm'],'geometry':geometry})
assert [k['midi_note'] for k in table]==list(range(21,109))
assert sum(k['color']=='WHITE' for k in table)==52
assert all((k['color']=='BLACK')==(k['midi_note']%12 in [1,3,6,8,10]) for k in table)
assert all(a['key_center'][0]<b['key_center'][0] for a,b in zip(table,table[1:]))
checks=[{k:v for k,v in table[n-21].items() if k in ['midi_note','key_index','note_name','color','key_center','semantic_identity']} for n in [21,60,69,108]]
dump('KEYBOARD_COORDINATE_FRAME_R1.json',{'origin_native_Three':origin.tolist(),'origin_definition':'C4 horizontal center, white front edge, white top at rest','canonical_origin_m':[0,0,0],'LOW_TO_HIGH_AXIS_native':[1,0,0],'FRONT_TO_BACK_AXIS_native':[0,0,-1],'KEY_PRESS_AXIS_native':[0,-1,0],'canonical_basis_native':B.tolist(),'handedness':'RIGHT_HANDED x=low-to-high y=front-to-back z=up; requested ordered (low-high,front-back,press) triad is LEFT_HANDED','units':'metres, inherited equivalent-scale interpretation','metres_per_native_unit':scale,'KEY_TOP_REFERENCE':'white top at rest = canonical z0; black top per key table','keyboard_front_edge':{'y':0,'native_z':float(origin[2])},'rear_direction_canonical':[0,1,0],'derivation':'low-high from ordered MIDI key centers; rear from actual pivot.edge=REAR and front endpoints; up from top mesh faces. Sign of press verified by applying approved positive X rotation to front top. No world-axis guess.','sample_mapping_checks':checks})
dump('KEYBOARD_88_KEY_TABLE_R1.json',{'KEY_COUNT':88,'mapping':'key_index is zero based; MIDI = key_index+21','mapping_pass':True,'sample_checks':checks,'keys':table})
# SMF parser: running status, tempo map, merged tracks, CC events. No external dependency.
data=(SRC/f'MIDI/{REC}.mid').read_bytes();assert data[:4]==b'MThd';ln=struct.unpack('>I',data[4:8])[0];fmt,ntr,ppq=struct.unpack('>HHH',data[8:14]);assert not ppq&0x8000
pos=8+ln;raw_events=[]
def vlq(d,i):
 v=0
 while True:
  b=d[i];i+=1;v=(v<<7)|(b&127)
  if not b&128:return v,i
for track in range(ntr):
 assert data[pos:pos+4]==b'MTrk';n=struct.unpack('>I',data[pos+4:pos+8])[0];d=data[pos+8:pos+8+n];pos+=8+n;i=0;tick=0;running=None;order=0
 while i<len(d):
  delta,i=vlq(d,i);tick+=delta;status=d[i]
  if status&128:i+=1
  else:assert running is not None;status=running
  if status==255:
   typ=d[i];i+=1;size,i=vlq(d,i);payload=d[i:i+size];i+=size
   if typ==81:raw_events.append((tick,track,order,'TEMPO',int.from_bytes(payload,'big'),None,None))
  elif status in [240,247]:size,i=vlq(d,i);i+=size;running=None
  else:
   running=status;typ=status>>4;ch=status&15;size=1 if typ in [12,13] else 2;val=list(d[i:i+size]);i+=size
   if typ in [8,9,11]:raw_events.append((tick,track,order,('NOTE_OFF' if typ==8 or typ==9 and val[1]==0 else 'NOTE_ON' if typ==9 else 'CC'),val[0],val[1],ch))
  order+=1
tempo=500000;last=0;t=0;events=[];tempos=[]
for tick,track,order,typ,a,b,ch in sorted(raw_events):
 t+=(tick-last)*tempo/ppq/1e6;last=tick
 if typ=='TEMPO':tempo=a;tempos.append({'tick':tick,'time_sec':t,'microseconds_per_beat':a});continue
 events.append({'source_time_sec':t,'type':typ,'a':a,'b':b,'channel':ch,'tick':tick,'track':track})
rows=list(csv.DictReader((SRC/f'Fingering/{REC}.tsv').open(),delimiter='\t'));pending={};notes=[];pedals=[]
for e in events:
 if e['type']=='NOTE_ON':pending.setdefault((e['channel'],e['a']),[]).append(e)
 elif e['type']=='NOTE_OFF':
  q=pending.get((e['channel'],e['a']),[]);assert q,'Unpaired NOTE_OFF';on=q.pop(0);matches=[(i,r) for i,r in enumerate(rows) if int(r['note'])==on['a'] and abs(float(r['onset'])-on['source_time_sec'])<2e-6 and abs(float(r['key_offset'])-e['source_time_sec'])<2e-6];assert len(matches)==1,('MIDI TSV mismatch',on,e,matches)
  idx,r=matches[0];finger=int(r['finger']) if r['finger'] in ['1','2','3','4','5'] else None
  notes.append({'note_id':f'n{len(notes):04}','source_on_sec':on['source_time_sec'],'source_off_sec':e['source_time_sec'],'midi_note':on['a'],'note_name':name(on['a']),'key_index':on['a']-21,'velocity':on['b'],'release_velocity':e['b'],'channel':on['channel'],'hand':r['hand'] if r['hand'] in ['L','R'] else 'UNKNOWN','finger':finger,'finger_source':'AUTO_PREDICTED' if finger else 'UNKNOWN','finger_confidence':None,'confidence_reason':'No per-event score supplied; dataset aggregate accuracy is not an event confidence.','fingering_row':idx+2})
 elif e['type']=='CC' and e['a'] in [64,66,67]:pedals.append(e)
assert not any(pending.values());assert len(notes)==len(rows)
window=[n for n in notes if n['source_on_sec']<18.5 and n['source_off_sec']>11.5];out=[]
for n in window:
 for typ,s in [('NOTE_ON',n['source_on_sec']),('NOTE_OFF',n['source_off_sec'])]:
  if 11.5<=s<18.5:out.append(dict(n,time_sec=s-11.5,source_time_sec=s,source_observation=(s-11.5)*60,nearest_source_frame=round(s*60),event_type=typ))
initial_pedals={};pe=[]
for e in pedals:
 if e['source_time_sec']<11.5:initial_pedals[str(e['a'])]=e['b']
 if 11.5<=e['source_time_sec']<18.5:pe.append({'time_sec':e['source_time_sec']-11.5,'source_time_sec':e['source_time_sec'],'source_observation':(e['source_time_sec']-11.5)*60,'event_type':'PEDAL','controller':e['a'],'value':e['b'],'channel':e['channel'],'hand':'UNKNOWN','midi_note':None,'note_name':None,'key_index':None,'velocity':None,'finger':None,'finger_source':'UNKNOWN','finger_confidence':None})
out+=pe;out.sort(key=lambda e:(e['time_sec'],e['event_type']!='NOTE_OFF'))
dump('PERFORMANCE_TIMELINE_R1.json',{'schema':'PERFORMANCE_TIMELINE_R1','USAGE_SCOPE':'INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY','license':'CC BY-NC-SA 4.0','source_recording':REC,'source_window_seconds':[11.5,18.5],'duration_seconds':7,'source_hz':60,'observations':421,'single_source_of_truth':True,'audio_event_interface_ready':True,'notes':window,'events':out,'initial_state':{'held_notes':[n for n in window if n['source_on_sec']<11.5],'pedal_controllers':initial_pedals},'end_state':{'held_notes':[n for n in window if n['source_off_sec']>=18.5],'end_policy':'Preview stops at7; consumer disposes voices/keys explicitly, not fabricated source NOTE_OFF'},'motion_binding':{'R':'PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1','L':'PIANOVAM_PHYSICAL_LEFT_MIRRORED_MAPPING_R1','blender_frame_from_time':'1+30*time_sec','no_resampling_or_retiming':True},'source_sha256':{'midi':sha(SRC/f'MIDI/{REC}.mid'),'fingering':sha(SRC/f'Fingering/{REC}.tsv')},'midi_audit':{'format':fmt,'tracks':ntr,'ticks_per_beat':ppq,'tempo_map':tempos,'full_note_count':len(notes),'all_notes_match_TSV_onset_release_pitch':True,'pedal_events_full_recording':len(pedals),'window_event_count':len(out),'window_note_count':len(window),'no_pedal_in_file_means_no_pedal_events_synthesized':True}})
dump('FINGERING_AUTHORITY_R1.json',{'RIGHT_FINGERING_AUTHORITY':'AUTO_PREDICTED','LEFT_FINGERING_AUTHORITY':'AUTO_PREDICTED','EXACT_FINGERING_VALIDATED':False,'use':'PROVISIONAL_CONTACT_HYPOTHESIS','source_folder':'Fingering, not Fingering_GT','source_url':'https://huggingface.co/datasets/PianoVAM/PianoVAM_v1/blob/main/README.md','source_evidence':'Folder description lines209-223: video/MediaPipe automatic majority-key assignment; manual disambiguation not applied.','hand_labels_also_predicted':True,'per_event_confidence':'UNKNOWN / null; no numeric confidence invented','counts':{s:sum(n['hand']==s for n in window) for s in ['R','L','UNKNOWN']}})
policy={'CONTACT_VERTICAL_TOLERANCE_MM':3.0,'CONTACT_HORIZONTAL_TOLERANCE_MM':2.0,'penetration_threshold_mm':3.0,'correct_key_region_requires_actual_polygon_inside':True,'boundary_near_miss_is_not_correct_key':True,'units':'equivalent physical mm from approved keyboard scale','white_width_mm':table[39]['width']*1000,'rationale':'3mm vertical is already visibly small relative to10mm key dip; 2mm horizontal is under10% of a23mm white key. Fixed before contact extraction, fitting, or result viewing.','same_for_both_hands_all_notes':True,'root_model':'fixed wrist-rest anatomical orientation; metre scale1; only XYZ translation','root_temporal_regularization':'sum active assigned-pad target residuals squared + lambda*sum(second-difference translation squared); lambda=(0.080*60)^4; natural endpoints; no per-note tuning','root_y_target':'white front+25mm; black front+15mm within actual playable region; fixed before fitting','root_jump_flag_mm_per_60Hz':10,'contact_success_not_independent_validation':'Fitted on predicted assignments; report fit residuals, not ground-truth evidence.'}
dump('CONTACT_TOLERANCE_POLICY_R1.json',policy)
dump('PRE_RESULT_POLICY_LOCK_R1.json',{'sha256':sha(P/'CONTACT_TOLERANCE_POLICY_R1.json'),'before_contact_solve':True})
print('KEY_TABLE PASS; TIMELINE',len(window),'notes',len(out),'events',len(pe),'pedals; policy locked',policy)
