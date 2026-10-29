from io_core import *
import numpy as np
cost=read(O/'COST_PREFLIGHT_CLOCK_FIXED.json');bl=read(O/'STAGE0_BLENDER.json');bd=read(O/'BOUNDARY_CONTRACT_WITNESS.json');env=read(O/'C1_REFERENCE_ENVELOPES_CLOCK_FIXED.json')
assert bd['no_feasible_candidate_within_locked_boundary'] and not cost['pass_']
receipts=[read(p) for p in sorted(O.glob('*_PROCESS.json'))]
ledger=dict(stage0_external_python_process_wall_seconds=sum(r['seconds'] for r in receipts if not r['blender']),blender_process_wall_seconds=sum(r['seconds'] for r in receipts if r['blender']),formal_solver_starts=0,formal_iterations=0,formal_candidate_count=0,formal_numerical_generation_seconds=0.,native_preflight_calls=106,preflight_call_meaning='Two full seed/Jacobian tests, 53 calls each; first derivative reference rejected and retained',numeric_budget_seconds=180,unlogged_initial_failures='Two initial Python import/assertion failures are retained in SOFTWARE_REPAIR_0/1; tool wall times 1.30/1.75s, no optimization',all_logged_processes=receipts)
ledger['stage0_python_wall_seconds_including_initial_failures']=ledger['stage0_external_python_process_wall_seconds']+1.30+1.75
atomic_json('COMPUTE_LEDGER_FINAL.json',ledger)
# Test original actual skin contacts, not candidate contacts.
data=archive(O/'BASELINE_ACTUAL.npz');bindings=read(R2/'INPUT_BINDINGS.json');keys=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];markers=read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers']['R']
stats={};contacts=[]
for it,t in enumerate(data['times']):
    for e in bindings['right_events']:
        if not e['note_on']<=t<e['note_off']:continue
        key=keys[e['key_index']];pv=np.asarray(key['press_pivot']);axis=np.asarray(key['press_axis'],dtype=float);axis/=np.linalg.norm(axis)
        x,y,z=axis;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);angle=data['key_angles'][it,e['key_index']]
        R=np.eye(3)+np.sin(angle)*K+(1-np.cos(angle))*(K@K)
        vertex=markers[e['finger']-1]['mesh_vertex'];p=(data['vertices'][it,vertex]-pv)@R+pv
        s=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
        miss=np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000;gap=(p[2]-s['z'])*1000
        inside=s['xmin']<=p[0]<=s['xmax'] and s['ymin']<=p[1]<=s['ymax']
        row=dict(time=float(t),event=e['note_id'],vertex=vertex,horizontal_mm=float(miss),gap_mm=float(gap),inside=bool(inside),pass_=bool(inside and miss<=.03 and abs(gap)<=3))
        contacts.append(row)
for e in ['R03','R04','R05','R06']:
    a=[r for r in contacts if r['event']==e];stats[e]=dict(samples=len(a),failures=sum(not r['pass_'] for r in a),horizontal_max_mm=max(r['horizontal_mm'] for r in a),gap_abs_max_mm=max(abs(r['gap_mm']) for r in a))
atomic_json('ORIGINAL_C1_CONTACT_REFERENCE.json',dict(rows=contacts,stats=stats,original_only=True,candidate=False,raw_readback_samples=len(data['times'])))
atomic_json('EXECUTION_POLICY_AND_STOP.json',dict(window=[1.2414275,2.134284],method='C1 + six cubic B-spline coefficient slots per26 channels; native skin hard constraint functions; intended trust-constr/NonlinearConstraint',coefficient_slots=156,free_variables=52,contact_xy_variables=0,coefficient_domains={'translation_mm':[-8,8],'rotation_vector_deg':[-4,4],'joint_correction_deg':[-8,8]},init='one all-zero C1 correction',solver_budget={'seconds':180,'iterations':60,'native_calls':6000},formal_started=False,stop_stage=0,primary_stop='Frozen endpoint actual non-target vertex depth already exceeds0.5mm; endpoint basis correction identically zero',secondary_stop='Full numerical Jacobian45.078s; continuous root/skin bounds not certified',no_new_solver_or_seed=True,velocity_reference_status='Reconstructed fixed C1 readback adapter, provisional; not original Action derivative certificate',key_screen_status='32 nearby registered components; full continuous conservative coverage not certified; boundary proof independently checks all139',no_new_trajectory=True))
atomic_json('FINAL_RESULT.json',dict(task='HANDS_SPARSE_WINDOW_CONSTRAINED_TRAJECTORY_FEASIBILITY_R1',RESULT='NO_FEASIBLE_CANDIDATE_WITHIN_SCOPE',SPARSE_WINDOW_HYPOTHESIS='UNKNOWN',HUMAN_NATURALNESS='NOT_TESTED',stop_stage='Stage0 deterministic boundary/geometry contract conflict and cost preflight',formal_solver_starts=0,formal_dynamic_candidates=0,actual_C1_reference_samples=241,candidate_Blender_samples=0,free_variables=52,geometric_impossibility_scope='Only current frozen endpoint boundary contract plus all-region non-target vertex0.5mm acceptance, not global motion/Rig infeasibility',Actions_created=0,Blends_saved=0,videos=0,piano_access=False))
merged={}
for p in O.glob('PROTECTION_*.json'):
    for r in read(p)['files']:
        assert r['unchanged']
        if r['path'] in merged:assert merged[r['path']]==r['before']
        merged[r['path']]=r['before']
merged.update(READS)
rows=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in merged.items()]
assert all(r['unchanged'] for r in rows)
atomic_json('PROTECTION_FINAL.json',dict(all_unchanged=True,files=rows,piano_access=False,original_Rig_Action_in_memory_unchanged=bl['original_unchanged'],scope='Actual input read union; no whole-project scan'))
print('FINAL_STAGE0_STOP',len(rows),ledger['stage0_python_wall_seconds_including_initial_failures'],stats,flush=True)
