from pathlib import Path
import json,hashlib,ast
P=Path(__file__).resolve().parent;ROOT=P.parents[1];CURRENT=ROOT/'audits/right_hand_articulation_contact_short_phrase_r1';PREVIOUS=ROOT/'audits/piano_hand_visual_first_short_phrase_validation_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
stats=read(P/'MIDI_SCOPE_STATISTICS.json');evidence=[]
for file,function,reason in [(CURRENT/'right_motion.py','sample_right','Only one contact/down endpoint per digit, no pitch-conditioned pose; one shared stance transform'),(CURRENT/'right_motion.py','phases','MIDI phase weights exist, but simultaneous or repeated assignments to same digit overwrite arrays; no allocation/regrasp layer'),(PREVIOUS/'phrase_common.py','left','Only inherited L1/L2 pressure curves; fixed key17/29 D2/D3 drive coordinated root and idle motion'),(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/03_motion_plan.py',None,'Legacy independent per-finger/per-time IK has constant root and requires external home/fingering layout; not a qualified long hand-position/chord planner'),(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1/01_source_timeline.py',None,'Musette-specific pitch/finger dictionary and first-two-bar scope assertions; not a universal fingering planner')]:
 text=file.read_text(encoding='utf-8-sig');tree=ast.parse(text)
 functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function] if function else []
 row={'file':str(file),'sha256':sha(file),'function':function,'reason':reason}
 if functions:row['line_start']=functions[0].lineno;row['line_end']=functions[0].end_lineno
 evidence.append(row)
# A source-level capability check, not a pose solve, IK test, or new action.
decision={'preflight_mode':'READ_ONLY_SOURCE_AND_CODE_CAPABILITY_CHECK','can_reasonably_execute_with_current_qualified_generator':False,'decision':'FAIL_CLOSED_BEFORE_GENERATION','candidate_count':0,'optimization_runs':0,'new_actions':0,'renders':0,'source_notes':stats['note_on_count'],'first_blocking_structure':stats['simultaneous_chords'][0],'current_required_generic_capabilities':{'target_key_conditioned_finger_poses':'MISSING_IN_CURRENT_QUALIFIED_ENDPOINT_GENERATOR','left_three_active_finger_contact_task':'NOT_ESTABLISHED','automatic_or_explicit_validated_full_phrase_fingering':'NOT_ESTABLISHED','long_two_hand_changing_position_root_paths':'MISSING_IN_CURRENT_SHARED_STANCE_GENERATOR','multi_note_MIDI_key_audio_data_representation':'SUPPORTED_AT_INTERFACE_LEVEL','basic_FK_skin_existing_key_contact_evaluation_and_baking':'REUSABLE','multiple_independent_digit_phase_weights':'PARTIALLY_SUPPORTED: representable, but not actual chord contact/hand-position proof'},'chord_actual_performance_support':'NOT_ESTABLISHED','right_single_endpoint_per_digit_incompatibility':{'distinct_source_R_keys':stats['by_hand']['R']['unique_pitch_count'],'fixed_endpoint_pairs':5,'source_level_reason':'At each NOTE_ON, stance=1 and that digit uses the same q_contact regardless of pitch; a5-digit fixed contact map cannot supply9 distinct inner-key contact targets over the phrase. A new key/hand-position-conditioned posture mechanism is required.'},'left_pitch_context':{'source_range':stats['by_hand']['L']['range_names'],'source_unique_keys':stats['by_hand']['L']['unique_pitch_count'],'current_qualified_active_tasks':['D2/LITTLE','D3/THUMB'],'source_level_reason':'Changing event IDs or input pitches leaves the inherited target poses/root tied to D2/D3; there is no qualified three-contact left task or moving-register control.'},'adaptation_assessment':'Requires a new target-key/hand-position-conditioned pose mechanism, coordinated left chord generation, and long-phrase hand-position/fingering organization; not just widening the event loop or copying the existing coefficients. Implementing and qualifying that unestablished core in this product-validation round would exceed a limited reuse adapter.','what_is_NOT_claimed':['Frozen rig is physically incapable of aG-major triad','A rendered chord visibly failed','Minuet MIDI is malformed','Lack of previous testing alone proves mathematical infeasibility','Musette Human acceptance is revoked'],'Musette_Human_acceptance_carried_forward':True,'no_score_simplification':True,'no_manual_per_note_animation':True,'no_millimeter_veto':True,'source_code_evidence':evidence}
dump('FEASIBILITY_DECISION.json',decision)
# Snapshot current protected bytes; Human may have updated non-frozen acceptance reports
# since older audits, so do not overwrite/re-adjudicate their historical statuses.
old=read(CURRENT/'PROTECTED_INPUTS_BEFORE.json');protect={f:sha(f) for f in old if Path(f).is_file()}
for folder in [CURRENT,ROOT/'production_spec/right_hand_product_baseline_r2',ROOT/'production_spec/left_hand_product_baseline_r1']:
 for f in folder.rglob('*'):
  if f.is_file():protect[str(f)]=sha(f)
for name in ['RIGHT_HAND_PRODUCT_BASELINE.json','LEFT_HAND_PRODUCT_BASELINE.json']:
 ptr=ROOT/'production_spec'/name;v=read(ptr);asset=ROOT/v['asset']['path'];assert sha(asset)==v['asset']['sha256'];protect[str(ptr)]=sha(ptr);protect[str(asset)]=sha(asset)
static=ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2';sm=read(static/'STATIC_SCENE_MANIFEST_R2.json');assert sha(static/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend')==sm['candidate_sha256']
for f in static.iterdir():
 if f.is_file():protect[str(f)]=sha(f)
for f in (P/'source').iterdir():protect[str(f)]=sha(f)
dump('PROTECTED_INPUTS_BEFORE.json',protect)
dump('FINGERING_PREFLIGHT.json',{'status':'NOT_COMMITTED_NOT_EXECUTABLE_PREFLIGHT_STOP','source_has_printed_finger_numbers':False,'full_phrase_fingers_validated':False,'initial_R_reference_only':{'notes':['D5','G4','A4','B4','C5'],'provisional_fingers':[5,1,2,3,4],'home_reference_midis_by_fingers1to5':[67,69,71,72,74]},'initial_L_chord_reference_only':{'notes':['G3','B3','D4'],'provisional_fingers':[5,3,1],'simultaneous_on_tick':0,'simultaneous_off_tick':768},'authority':'Designed provisional music-level reference, NOT derived MIDI fingering or approved new hand pose','remaining_full_phrase_assignments':'UNASSIGNED: requires hand-position transitions and simultaneously unique chord fingers; do not blindly apply Musette dictionary','no_per_note_manual_pose_or_animation':True,'no_candidate_generated':True})
print('FINITE_PREFLIGHT_FAIL_CLOSED_NO_MOTION',len(protect),flush=True)
