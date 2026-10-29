"""Bounded read-only evidence extraction. No import/execution of motion or Blender code."""
import sys,json,hashlib,ast
from pathlib import Path
sys.dont_write_bytecode=True
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];A=ROOT/'audits'
S=A/'piano_hand_static_to_dynamic_transition_r1';R=A/'left_little_finger_moving_key_reachability_r1';D=A/'left_octave_neighbor_key_clearance_conflict_isolation_r1';C=A/'left_octave_root_finger_coordinated_clearance_r1';CORE=A/'midi_driven_dual_hand_piano_performance_poc_r1';STATIC=A/'piano_hand_static_posture_clearance_refinement_r2'
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
files=[CORE/n for n in ['performance_core.py','01_source_timeline.py','05_audio.py','PERFORMANCE_TIMELINE_R1.json','KEYBOARD_88_KEY_TABLE_R1.json','RIG_CANONICAL_PROBE_R1.json','FINGERTIP_CONTACT_MARKERS_R1.json','source/anna-magdalena-22.mid','source/PIANO_SAMPLE_MANIFEST.json','KEY_AUDIO_SYNC_R1.json']]
files += [S/n for n in ['common.py','01_plan.py','02_scene_verify.py','03_measure.py','TEMPORAL_MOTION_POLICY_R1.json','CONTACT_AWARE_MOTION_PLAN_R1.json','DYNAMIC_CONTACT_R1.json','NEIGHBOR_CLEARANCE_R1.json','MOTION_CONTINUITY_R1.json','PIANO_HAND_STATIC_TO_DYNAMIC_TRANSITION_R1_REPORT.md','DYNAMIC_SCENE_MANIFEST_R1.json']]
files += [R/n for n in ['03_probe.py','ROOT_FOLLOW_THROUGH_POLICY_R1.json','PROBE_RESULT_R1.json','PROBE_DYNAMIC_CONTACT_R1.json','PROBE_CLEARANCE_R1.json','PROBE_CONTINUITY_R1.json','LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md']]
files += [D/n for n in ['01_counterfactual.py','ROOT_COUNTERFACTUAL_R1.json','CONTACT_CLEARANCE_CONFLICT_R1.json','FINAL_STATUS_R1.json','LEFT_OCTAVE_NEIGHBOR_KEY_CLEARANCE_CONFLICT_ISOLATION_R1_REPORT.md']]
files += [C/n for n in ['01_coordinate.py','03_measure.py','02_verify_render.py','05_finish.py','COORDINATED_CLEARANCE_POLICY_R1.json','ROOT_FINGER_COORDINATION_R1.json','DYNAMIC_CONTACT_R1.json','NEIGHBOR_KEY_CLEARANCE_R1.json','MOTION_CONTINUITY_R1.json','SAVE_REOPEN_VERIFICATION_R1.json','STATIC_ANCHOR_PROTECTION_R1.json','FINAL_ASSET_PROTECTION_R1.json','FINAL_STATUS_R1.json','IMPLEMENTATION_REPAIR_R1.json','LEFT_OCTAVE_ROOT_FINGER_COORDINATED_CLEARANCE_R1_REPORT.md','HUMAN_VISIBLE_PRECHECK_R1.json','coordinated_motion.npz']]
files += [STATIC/n for n in ['SOLVED_STATIC_POSES_R2.json','STATIC_REFINEMENT_POLICY_R2.json','STATIC_SCENE_MANIFEST_R2.json']]
authority=read(C/'FINAL_ASSET_PROTECTION_R1.json');formals={**authority['hand_baselines'],**authority['piano_authority']}
files += [Path(v['path']) for v in formals.values()]
files += [S/'STATIC_TO_DYNAMIC_TRANSITION_CANDIDATE_R1.blend',R/'LEFT_LITTLE_MOVING_KEY_PROBE_R1.blend',C/'LEFT_OCTAVE_COORDINATED_CLEARANCE_CANDIDATE_R1.blend',STATIC/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend']
files=list(dict.fromkeys(files));protected={str(f):sha(f) for f in files};dump('PROTECTED_EVIDENCE_BEFORE.json',protected)
functions={}
for f in files:
 if f.suffix=='.py':
  tree=ast.parse(f.read_text(encoding='utf8'));functions[str(f.relative_to(ROOT))]=[{'name':n.name,'line':n.lineno,'end_line':n.end_lineno} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
def phases(n,old=False):
 rows=n['samples'] if old else n['rows'];out={}
 for ph in sorted(set(r['phase'] for r in rows)):
  rr=[r for r in rows if r['phase']==ph];gg=[r['skin_pad' if old else 'skin']['gap_mm'] for r in rr]
  out[ph]={'max_abs_skin_gap_mm':max(map(abs,gg)),'first_time':min(r['time'] for r in rr),'last_time':max(r['time'] for r in rr),'inside_all':all(r['skin_pad' if old else 'skin']['inside'] for r in rr)}
 return out
old=read(S/'DYNAMIC_CONTACT_R1.json')['L']['note_rows'];reach=read(R/'PROBE_DYNAMIC_CONTACT_R1.json')['notes'];coord=read(C/'DYNAMIC_CONTACT_R1.json')['notes'];series=[]
for previous,rootfollow,current in zip(old,reach,coord):
 series.append({'note_id':current['note_id'],'midi':current['midi'],'static_transition_max_skin_gap_mm':previous['max_absolute_skin_gap_mm'],'reachability_max_skin_gap_mm':rootfollow['max_skin_gap_mm'],'coordinated_required_max_skin_gap_mm':current['max_skin_gap_mm'],'coordinated_required_pass':current['pass'],'coordinated_phase_summary':phases(current),'static_transition_phase_summary':phases(previous,True),'reachability_phase_summary':phases(rootfollow),'comparison_caveat':'Old summaries include key rebound adhesion; current required interval excludes NOTE_OFF and natural release. Phase summaries support like-for-like required-contact comparison.'})
q=np.load(C/'coordinated_motion.npz');pol=read(C/'COORDINATED_CLEARANCE_POLICY_R1.json');rootstates=[]
for t in [.7,.735,.95,.985,1.02,1.1,1.2,1.235,1.27,1.45,1.52]:
 i=int(np.argmin(abs(q['times']-t)));assert abs(float(q['times'][i])-t)<1e-8
 rootstates.append({'time':t,'D2_depression':float(q['key_angles'][i,17]/read(CORE/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'][17]['press_angle_rad']),'D3_depression':float(q['key_angles'][i,29]/read(CORE/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'][29]['press_angle_rad']),'little_DIP_increment_deg':float(np.degrees(q['q'][i,4,2]))})
fit=read(C/'ROOT_FINGER_COORDINATION_R1.json');rig=read(CORE/'RIG_CANONICAL_PROBE_R1.json');formalcheck={k:{'path':v['path'],'expected_sha256':v['expected_sha256'],'current_sha256':sha(Path(v['path'])),'matches':sha(Path(v['path']))==v['expected_sha256']} for k,v in formals.items()}
dump('READ_ONLY_EVIDENCE_SUMMARY.json',{'scope':'ARCHITECTURE_REASSESSMENT_ONLY','source_file_count':len(files),'formal_assets':formalcheck,'left_bone_count':len(rig['L']['bones']),'left_bone_names':list(rig['L']['bones']),'source_function_locations':functions,'events':pol['events'],'contact_series':series,'saved_motion_phase_samples':rootstates,'final_fit':{k:fit[k] for k in ['nfev','calls','elapsed_sec','success','cost','policy_sha256','script_sha256','candidate_count']},'solver_code_matches_saved_fit':sha(C/'01_coordinate.py')==fit['script_sha256'],'policy_matches_saved_fit':sha(C/'COORDINATED_CLEARANCE_POLICY_R1.json')==fit['policy_sha256'],'computed_new_trajectories':False,'computed_new_skin_or_collisions':False,'invoked_Blender_or_solver':False})
print(json.dumps({'files':len(files),'formal_matches':all(v['matches'] for v in formalcheck.values()),'bone_count':len(rig['L']['bones']),'contact_series':[{k:v for k,v in n.items() if 'phase_summary' not in k} for n in series],'saved_phase_samples':rootstates,'code_matches_fit':sha(C/'01_coordinate.py')==fit['script_sha256']},ensure_ascii=False))
