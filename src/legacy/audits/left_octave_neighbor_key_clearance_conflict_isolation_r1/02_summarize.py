import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;OLD=P.parent/'piano_hand_static_to_dynamic_transition_r1';LATEST=P.parent/'left_little_finger_moving_key_reachability_r1';sys.path.insert(0,str(OLD));import common as o
def dump(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v),encoding='utf8')
raw=o.read(P/'COUNTERFACTUAL_RAW_R1.json');rows=raw['rows'];times=[r['time'] for r in rows]
def phases(t):return [{'note_id':n['note_id'],'midi':n['midi_note'],'phase':'NOTE_ON' if abs(t-n['note_on'])<1e-8 else 'NOTE_OFF/RELEASE' if abs(t-n['note_off'])<1e-8 else o.phase(n,t)} for n in o.EVENTS['L'] if n['note_on']-.12-1e-8<=t<=o.recovery_end(n)+1e-8]
def spans(mask):
 out=[];i=0
 while i<len(mask):
  if not mask[i]:i+=1;continue
  start=i
  while i+1<len(mask) and mask[i+1]:i+=1
  end=i;prev=times[max(0,start-1)];next=times[min(len(times)-1,end+1)];begin=(prev+times[start])/2;finish=(times[end]+next)/2
  out.append({'first_hit':times[start],'last_hit':times[end],'onset_bracket':[prev,times[start]],'offset_bracket':[times[end],next],'duration_lower_sec':times[end]-times[start],'duration_upper_sec':next-prev,'midpoint_duration_estimate_sec':finish-begin,'sample_count':end-start+1,'observed_phase_combinations':list(dict.fromkeys(' + '.join(x['note_id']+':'+x['phase'] for x in phases(t)) for t in times[start:end+1]))});i+=1
 return out
summary={};events=[]
for state in ['A','B']:
 summary[state]={}
 for key in ['40','42']:
  rr=[r[state]['keys'][key]['penetrations'] for r in rows];allhits=[v for r in rr for v in r];ids=sorted(set(v['vertex'] for v in allhits));deepids=sorted(set(v['vertex'] for v in allhits if v['vertical_below_top_mm']>3));anyruns=spans([bool(r) for r in rr]);deepruns=spans([any(v['vertical_below_top_mm']>3 for v in r) for r in rr]);sources=sorted(set(raw['affected_vertex_regions_only'][str(v)]['dominant_digit'] for v in ids))
  summary[state][key]={'midi':int(key),'key_name':o.c.KEYS[int(key)-21]['note_name'],'unpressed_all_samples':all(r[state]['keys'][key]['key_unchanged_unpressed'] for r in rows),'source_digits':sources,'unique_affected_vertices':ids,'legacy_deep_unique_vertices':deepids,'max_simultaneous_hit_vertices':max(len(set(v['vertex'] for v in r)) for r in rr),'max_simultaneous_deep_vertices':max(len(set(v['vertex'] for v in r if v['vertical_below_top_mm']>3)) for r in rr),'max_vertical_below_top_mm':max([v['vertical_below_top_mm'] for v in allhits],default=0),'max_minimum_exit_distance_mm':max([v['minimum_exit_distance_mm'] for v in allhits],default=0),'any_penetration_intervals':anyruns,'legacy_depth_gt3_intervals':deepruns,'total_midpoint_penetration_duration_sec':sum(r['midpoint_duration_estimate_sec'] for r in anyruns),'total_duration_bounds_sec':[sum(r['duration_lower_sec'] for r in anyruns),sum(r['duration_upper_sec'] for r in anyruns)]}
  summary[state][key]['by_digit']={}
  for digit in sources:
   digitrows=[[v for v in r if raw['affected_vertex_regions_only'][str(v['vertex'])]['dominant_digit']==digit] for r in rr];flat=[v for r in digitrows for v in r]
   summary[state][key]['by_digit'][digit]={'unique_vertices':sorted(set(v['vertex'] for v in flat)),'max_simultaneous_vertices':max(len(r) for r in digitrows),'max_vertical_below_top_mm':max(v['vertical_below_top_mm'] for v in flat),'max_minimum_exit_distance_mm':max(v['minimum_exit_distance_mm'] for v in flat),'intervals':spans([bool(r) for r in digitrows])}
  for r in rows:
   if not r[state]['keys'][key]['penetrations']:continue
   events.append({'state':state,'time':r['time'],'midi':int(key),'phases':phases(r['time']),'mesh_object':raw['mesh_object'],'penetrations':[dict(v,region=raw['affected_vertex_regions_only'][str(v['vertex'])]) for v in r[state]['keys'][key]['penetrations']],'simultaneous_active_contact':{str(x['midi']):r[state]['contact'][str(x['midi'])] for x in r[state]['active_contact_tasks']},'key_depression_fraction':0})
contacts={}
for state in ['A','B']:
 contacts[state]=[]
 for n in o.EVENTS['L']:
  selected=[r for r in rows if n['note_on']-1e-8<=r['time']<=n['note_off']+.07+1e-8];mm=[r[state]['contact'][str(n['midi_note'])] for r in selected];contacts[state].append({'note_id':n['note_id'],'midi':n['midi_note'],'contact_pass':all(v['fixed']['pass'] and v['skin']['pass'] for v in mm),'max_fixed_gap_mm':max(abs(v['fixed']['gap_mm']) for v in mm),'max_skin_gap_mm':max(abs(v['skin']['gap_mm']) for v in mm),'inside_both_all_samples':all(v['fixed']['inside'] and v['skin']['inside'] for v in mm),'phase_results':{ph:{'pass':all(r[state]['contact'][str(n['midi_note'])]['fixed']['pass'] and r[state]['contact'][str(n['midi_note'])]['skin']['pass'] for r in selected if ('NOTE_ON' if abs(r['time']-n['note_on'])<1e-8 else o.phase(n,r['time']))==ph),'samples':sum(('NOTE_ON' if abs(r['time']-n['note_on'])<1e-8 else o.phase(n,r['time']))==ph for r in selected)} for ph in ['NOTE_ON','KEY_PRESS','HOLD','RELEASE']}})
stage_rows=[]
for t,label in [(.4,'PREPARATION'),(.7,'D2_FIRST_NOTE_ON'),(.7166666667,'D2_FIRST_KEY_PRESS'),(.735,'D2_FIRST_FULL_DOWN'),(.85,'D2_FIRST_HOLD / D3_APPROACH'),(.95,'D2_RELEASE / D3_NOTE_ON'),(.985,'D2_REBOUND / D3_FULL_DOWN'),(1.1,'D3_HOLD'),(1.2,'D2_SECOND_NOTE_ON / D3_RELEASE'),(1.235,'D2_SECOND_FULL_DOWN / D3_REBOUND'),(1.4,'D2_SECOND_HOLD'),(1.45,'D2_SECOND_RELEASE'),(1.55,'RECOVERY')]:
 r=min(rows,key=lambda x:abs(x['time']-t));stage_rows.append({'stage':label,'actual_sample_time':r['time'],'states':{s:{'E2_hit_vertices':len(r[s]['keys']['40']['penetrations']),'Fsharp2_hit_vertices':len(r[s]['keys']['42']['penetrations']),'D2_skin_gap_mm':r[s]['contact']['38']['skin']['gap_mm'],'D3_skin_gap_mm':r[s]['contact']['50']['skin']['gap_mm'],'active_tasks':r[s]['active_contact_tasks']} for s in ['A','B']}})
oldA=o.np.load(LATEST/'evaluated_probe.npz');parity=0
for i,t in enumerate(oldA['times']):
 r=min(rows,key=lambda x:abs(x['time']-t));assert abs(r['time']-t)<1e-8
 for j,midi in [(4,38),(0,50)]:parity=max(parity,float(o.np.max(abs(o.np.array(r['A']['contact'][str(midi)]['skin_xyz_mm'])-oldA['skin_pads'][i,j]*1000))))
assert parity<.03
removed=all(not summary['B'][k]['unique_affected_vertices'] for k in ['40','42']);d2fail=all(not v['contact_pass'] for v in contacts['B'] if v['midi']==38)
classification='ROOT_PATH_CONFLICT' if removed and d2fail else 'CAUSE_NOT_ISOLATED'
dump('NEIGHBOR_KEY_PENETRATION_EVENTS_R1.json',{'scope':'Only E2/F#2 and their finite affected skin regions, no full-hand anatomy forensic','geometry_definition':'True key-solid containment; >3mm below top separately retained as legacy screen','time_resolution_sec':1/240,'duration_method':'Bracket transitions by last clear/first hit and last hit/first clear samples; duration is not exact crossing time','summaries':summary,'events':events,'region_evidence':raw['affected_vertex_regions_only'],'stage_comparison':stage_rows})
dump('ROOT_COUNTERFACTUAL_R1.json',{'state_A':'Current saved dynamic root + current finger Action','state_B':'Same current finger Action, approved common static root only; unsaved diagnostic','source_sha256':raw['source_sha256'],'joint_action_and_pose_unchanged':raw['same_joint_action_max_matrix_difference']==0,'joint_pose_max_matrix_delta':raw['same_joint_action_max_matrix_difference'],'key_angles_unchanged':raw['same_key_angle_max_difference_rad']==0,'action_data_hashes_unchanged':raw['actions_sha256_before']==raw['actions_sha256_after'],'current_A_skin_parity_max_mm':parity,'contacts':contacts,'neighbor_comparison':summary,'penetration_removed_both_keys':removed,'D2_contact_fails_again':d2fail,'result':'ROOT_CONTACT_CLEARANCE_TRADEOFF' if removed and d2fail else 'CAUSE_NOT_ISOLATED','static_root_is_approved':True,'counterfactual_is_approved_dynamic_motion':False,'not_saved':True,'new_action_candidates':0})
dump('CONTACT_CLEARANCE_CONFLICT_R1.json',{'primary_cause_classification':classification,'causal_evidence':'Controlled external-root intervention with byte-identical Action curves, exact same local joint matrices and key angles at each time.','conclusion':'Removing dynamic root removes both-key observed skin-solid penetrations but loses D2 contact.' if removed and d2fail else 'See counterfactual details','scope_limit':'Specific saved trajectory and observed contact regions. Does not prove root is the sole possible global cause or that no fixed-root finger solution exists.','idle_finger_dynamic_avoidance_direct_evidence':'Current unchanged MIDDLE and RING postures do not clear F#2 under A root; same postures clear under B. This demonstrates insufficient avoidance under A, not articulation-alone causation. E2 belongs to LITTLE, not idle three.','other_regions':'No INDEX, THUMB or PALM affected-vertex evidence for these two keys in sampled A/B states.','recommend_only_one_route':classification,'no_repair_authorized_or_executed':True,'new_action_candidates':0,'static_approval_remains_valid':True})
print(json.dumps({'summary':summary,'contacts':contacts,'cause':classification,'A_parity_mm':parity},ensure_ascii=True,indent=2),flush=True)
