import sys,itertools,collections
from common import *
locked();model=sys.argv[1] if len(sys.argv)>1 else 'A';A=np.load(P/f'model_{model.lower()}_evaluations.npz');old=read(PRE/'CONTACT_MEASUREMENTS_R1.json');ep=read(P/'EVALUATION_AND_MODEL_B_GATE_POLICY_R1.json');temp=read(P/'ROOT_POSE_TEMPORAL_POLICY_R1.json');place=ep['placement_not_contact'];hlim=place['per_key_injective_pad_coverage_horizontal_margin_mm'];vlim=place['per_key_injective_pad_coverage_vertical_margin_mm'];angles=A['angles'];summary={};clusters=[];onsets=[];collisions={};attrs={}
def cover(table,criterion):
 n=len(table)
 if n>5:return False,None
 for perm in itertools.permutations(range(5),n):
  if all(criterion(table[j][f]) for j,f in enumerate(perm)):return True,[f+1 for f in perm]
 return False,None
def cluster(side,i,notes,pads,ang):
 table=[[measurement(p,keys[n['key_index']],ang[n['key_index']]) for p in pads] for n in notes]
 strict,match=cover(table,lambda m:m['contact_within_fixed_tolerances']);coarse,cm=cover(table,lambda m:m['horizontal_in_key_error_mm']<=hlim and abs(m['vertical_gap_mm'])<=vlim);horizontal,hm=cover(table,lambda m:m['horizontal_in_key_error_mm']<=hlim)
 labeled=[table[j][n['finger']-1] for j,n in enumerate(notes)];lpass=all(m['contact_within_fixed_tolerances'] for m in labeled);duplicate=len({n['finger'] for n in notes})<len(notes)
 if lpass:category='NO_FAILURE'
 elif strict:category='LIKELY_FINGERING_LABEL_CONFLICT'
 elif coarse:category='SOURCE_2_5D_OR_CONTACT_PRECISION_LIMIT'
 elif horizontal and not duplicate:category='DEPTH_OR_APPROACH_ORIENTATION_LIMIT'
 else:category='ROOT_POSE_GEOMETRIC_FAILURE'
 xs=[keys[n['key_index']]['key_center'][0] for n in notes];tars=np.array([target_for(keys[n['key_index']],ang[n['key_index']]) for n in notes]);n=len(notes)
 return {'hand':side,'observation':int(i),'time_sec':float(i/60),'cluster_type':'SINGLE_NOTE' if n==1 else '2_NOTE_CLUSTER' if n==2 else '3_PLUS_NOTE_CLUSTER','note_ids':[n['note_id'] for n in notes],'midi_notes':[n['midi_note'] for n in notes],'predicted_fingers':[n['finger'] for n in notes],'PREDICTED_FINGER_CONTACT':labeled,'labeled_all_pass':lpass,'unlabeled_strict_contact_feasible':strict,'unlabeled_coarse_placement_feasible':coarse,'unlabeled_horizontal_depth_feasible':horizontal,'strict_witness_fingers_DIAGNOSTIC_ONLY':match,'coarse_witness_fingers_DIAGNOSTIC_ONLY':cm,'duplicate_predicted_finger':duplicate,'attribution':category,'attribution_scope':'AT_CURRENT_FITTED_POSE_AND_PREDICTED_HAND; no architecture impossibility or true fingering claim','finger_label_independent_span':{'pad_x_span_mm':float(np.ptp(pads[:,0])*1000),'target_center_x_span_mm':float(np.ptp(xs)*1000),'target_center_outside_pad_envelope_mm':float(max(max(0,min(pads[:,0])-x,x-max(pads[:,0])) for x in xs)*1000),'pad_centroid_minus_target_centroid_mm':((pads.mean(0)-tars.mean(0))*1000).tolist()},'pair_matrix':table}
for side in ['R','L']:
 PP=A[side+'_pads'];V=A[side+'_verts'];regions=ex['body_regions'][side];rows=[]
 for i,t in enumerate(times):
  notes=[n for n in active(t) if n['hand']==side and n['finger'] is not None]
  if notes:rows.append(cluster(side,i,notes,PP[i],angles[i]))
 clusters+=rows
 for e in tl['events']:
  if e['event_type']!='NOTE_ON' or e['hand']!=side or e['finger'] is None:continue
  u=e['time_sec']*60;i=min(int(u),419);f=u-i;p=(1-f)*PP[i]+f*PP[i+1];ang=(1-f)*angles[i]+f*angles[i+1];m=measurement(p[e['finger']-1],keys[e['key_index']],ang[e['key_index']]);onsets.append({'note_id':e['note_id'],'hand':side,'time_sec':e['time_sec'],'midi_note':e['midi_note'],'finger':e['finger'],'finger_source':'AUTO_PREDICTED','finger_confidence':None,'contact_kind':'PREDICTED_FINGER_CONTACT','pad_world_m':p[e['finger']-1].tolist(),**m})
 hits=[]
 # Same visible-key volume screen as previous, not a new anatomy audit.
 for i in range(N):
  v=V[i];hit=np.zeros(len(v),bool)
  for k in keys:
   pv=np.array(k['press_pivot']);q=rot(v,pv,-angles[i,k['key_index']])
   for g in k['geometry']:
    gv=np.array(g['vertices']);lo=gv.min(0);hi=gv.max(0);hit|=np.all(q>=lo,axis=1)&np.all(q<=hi,axis=1)&(q[:,2]<hi[2]-.003)
  if hit.any():hits.append({'observation':i,'key_volume_vertices':int(hit.sum()),'palm_vertices':int(hit[regions['palm_vertices']].sum()),'wrist_vertices':int(hit[regions['wrist_vertices']].sum())})
 collisions[side]=hits;rr=[r for r in onsets if r['hand']==side];group={}
 for kind in ['SINGLE_NOTE','2_NOTE_CLUSTER','3_PLUS_NOTE_CLUSTER']:
  cc=[r for r in rows if r['cluster_type']==kind];group[kind]={'observations':len(cc),'labeled_all_pass':sum(r['labeled_all_pass'] for r in cc),'unlabeled_strict_feasible':sum(r['unlabeled_strict_contact_feasible'] for r in cc),'unlabeled_coarse_feasible':sum(r['unlabeled_coarse_placement_feasible'] for r in cc),'horizontal_depth_feasible':sum(r['unlabeled_horizontal_depth_feasible'] for r in cc),'attribution_counts':dict(collections.Counter(r['attribution'] for r in cc))}
 multi=[r for r in rows if r['cluster_type']!='SINGLE_NOTE'];fails=[r for r in multi if not r['labeled_all_pass']];counts=collections.Counter(r['attribution'] for r in fails);old_s=old['summary'][side];translation_steps=np.linalg.norm(np.diff(A[side+'_roots'],axis=0),axis=1)*1000;orientation_steps=np.max(np.abs(np.degrees(np.diff(A[side+'_orientation'],axis=0))),axis=1)
 summary[side]={'note_on_measured':len(rr),'note_on_contacts_within_policy':sum(r['contact_within_fixed_tolerances'] for r in rr),'prior_note_on_pass':old_s['note_on_contacts_within_policy'],'onset_improvement_percentage_points':100*(sum(r['contact_within_fixed_tolerances'] for r in rr)-old_s['note_on_contacts_within_policy'])/len(rr),'max_vertical_gap_mm':max(abs(r['vertical_gap_mm']) for r in rr),'median_vertical_gap_mm':float(np.median([abs(r['vertical_gap_mm']) for r in rr])),'penetrating_note_ons':sum(r['penetration'] for r in rr),'floating_note_ons':sum(r['vertical_gap_mm']>3 for r in rr),'groups':group,'multinote_observations':len(multi),'multinote_coarse_feasible_fraction':sum(r['unlabeled_coarse_placement_feasible'] for r in multi)/max(1,len(multi)),'multinote_horizontal_feasible_fraction':sum(r['unlabeled_horizontal_depth_feasible'] for r in multi)/max(1,len(multi)),'multinote_failed_observations':len(fails),'failure_counts':dict(counts),'likely_fingering_conflict_failure_fraction':counts['LIKELY_FINGERING_LABEL_CONFLICT']/max(1,len(fails)),'depth_approach_failure_fraction':counts['DEPTH_OR_APPROACH_ORIENTATION_LIMIT']/max(1,len(fails)),'root_geometric_failure_fraction':counts['ROOT_POSE_GEOMETRIC_FAILURE']/max(1,len(fails)),'palm_collision_observations':sum(r['palm_vertices']>0 for r in hits),'wrist_collision_observations':sum(r['wrist_vertices']>0 for r in hits),'mesh_collision_observations':len(hits),'max_translation_step_mm':float(translation_steps.max()),'max_orientation_step_deg':float(orientation_steps.max()),'continuity_locked_limits_pass':bool(translation_steps.max()<=10 and orientation_steps.max()<=temp['orientation_step_limit_deg_per_60Hz']),'numeric_finite':bool(np.isfinite(V).all())}
 attrs[side]={'denominator':'same-hand MULTI_NOTE observations whose original predicted labels fail strict contact; repeated held observations are temporally correlated','count':len(fails),'counts':dict(counts),'likely_finger_label_conflict':counts['LIKELY_FINGERING_LABEL_CONFLICT'],'likely_conflict_fraction':counts['LIKELY_FINGERING_LABEL_CONFLICT']/max(1,len(fails))}
dump(f'MODEL_{model}_CONTACT_MEASUREMENTS_R1.json',{'model':model,'summary':summary,'note_on_measurements':onsets,'contact_kind':'PREDICTED_FINGER_CONTACT','not_ground_truth':True})
dump(f'MODEL_{model}_KEY_CLUSTER_PLACEMENT_METRIC_R1.json',{'model':model,'summary':{s:summary[s]['groups'] for s in summary},'finger_label_independent_but_hand_assignment_still_predicted':True,'unknown_hand_notes_excluded':25,'matching_is_analysis_only_not_solver_input_or_fingering_update':True,'thresholds':place,'rows':clusters})
dump(f'MODEL_{model}_CONTACT_FAILURE_ATTRIBUTION_R1.json',{'model':model,'summary':attrs,'classification_policy':ep['failure_attribution_precedence'],'critical_caveat':ep['attribution_caution'],'evidence_counts_do_not_certify_causality':True})
dump(f'MODEL_{model}_COLLISION_R1.json',{'model':model,'method':'Inherited actual key-piece vertex volume screen >3mm under top; no hidden crossing/normal-dot audit','hands':collisions})
oldcoll=sum(old['summary'][s]['palm_collision_observations']+old['summary'][s]['wrist_collision_observations'] for s in summary);newcoll=sum(summary[s]['palm_collision_observations']+summary[s]['wrist_collision_observations'] for s in summary);reduction=1-newcoll/oldcoll
g=ep['A_PASS_requires_both_hands'];gates={'multi_note_placement':all(v['multinote_coarse_feasible_fraction']>=g['multi_note_coarse_coverage_fraction_min'] for v in summary.values()),'predicted_contact_substantially_improved':all(v['onset_improvement_percentage_points']>=g['labeled_onset_contact_improvement_absolute_percentage_points_min'] for v in summary.values()),'collision_reduction':reduction>=g['combined_palm_wrist_collision_observation_reduction_min'],'continuity':all(v['continuity_locked_limits_pass'] for v in summary.values()),'geometric_failures_not_many':all(v['root_geometric_failure_fraction']<=g['geometric_failure_fraction_max'] for v in summary.values()),'Human_visible_precheck':'PENDING'}
dump(f'MODEL_{model}_RESULT_R1.json',{'model':model,'executed':True,'machine_gates':gates,'summary':summary,'collision_reduction_fraction':reduction,'status':'FAIL_MACHINE_GATES' if not all(v for k,v in gates.items() if k!='Human_visible_precheck') else 'PENDING_VISIBLE_REVIEW','independent_contact_validation':False,'Action_and_source_labels_mutated':False})
if model=='A':
 gate=ep['MODEL_B_gate'];cnt=sum(v['multinote_failed_observations'] for v in summary.values());depth=sum(v['failure_counts'].get('DEPTH_OR_APPROACH_ORIENTATION_LIMIT',0) for v in summary.values());support=all(v['depth_approach_failure_fraction']>.5 and v['multinote_horizontal_feasible_fraction']>=.7 for v in summary.values()) and depth/max(1,cnt)>.5
 dump('MODEL_B_GATE_R1.json',{'MODEL_B_AUTHORIZED_BY_EVIDENCE':False,'numerical_depth_gate_support':support,'depth_approach_count':depth,'failed_multinote_count':cnt,'depth_share':depth/max(1,cnt),'both_hands_depth_majority_required':True,'visual_orientation_evidence':'PENDING','reason':'Numerical gate alone is not authorization; visible residual attribution required.' if support else 'Depth/approach is not the clear dominant residual for both hands at locked criteria. Do not add pitch/roll.','model_B_executed':False})
print(json.dumps({'model':model,'summary':summary,'gates':gates,'collision_reduction':reduction},indent=2))
