from common import *
from collections import Counter
from datetime import datetime,timezone
sys.path.insert(0,str(OLD/'_deps'))
import numpy as np
r=read(OUT/'B01_MACHINE_VALIDATION.json');lock=read(OUT/'STRATEGY_LOCK.json');edit=read(OUT/'EDIT_RECEIPT.json')
with np.load(OUT/'ACTUAL_B01_SKIN_QC.npz',allow_pickle=False) as z:
    q=z['candidate_qdeg'];qb=z['baseline_qdeg'];times=z['times']
bd=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
violation=np.maximum(bd[:,0][None]-q,q-bd[:,1][None]);index=np.unravel_index(violation.argmax(),violation.shape)
it,j,k=index
domain=dict(time=float(times[it]),digit=['THUMB','INDEX','MIDDLE','RING','LITTLE'][j],channel=['MCP_flexion','PIP_flexion','DIP_flexion','MCP_spread'][k],
            source_deg=float(qb[index]),candidate_deg=float(q[index]),lower_deg=float(bd[j,0,k]),upper_deg=float(bd[j,1,k]),violation_deg=float(violation[index]))
core=[rec for rec in r['records'] if lock['core'][0]-1e-9<=rec['time']<=lock['core'][1]+1e-9]
group={kind:dict(records=sum(row['kind']==kind for row in r['regressions']),first=min(row['time'] for row in r['regressions'] if row['kind']==kind),last=max(row['time'] for row in r['regressions'] if row['kind']==kind)) for kind in {row['kind'] for row in r['regressions']}}
keygroups=dict(Counter(row.get('key') for row in r['regressions'] if 'key' in row))
summary=dict(result='GENERATED_WITH_DEFECTS',machine_validation='FAIL' if not r['pass_'] else 'PASS',human_visual_acceptance='PENDING',original_C1='UNCHANGED',B02_B03='NOT_MODIFIED',
 core_samples=len(core),core_source_intersection_samples=sum(rec['pairs']['MIDDLE_RING']['baseline']>0 for rec in core),core_candidate_intersection_samples=sum(rec['pairs']['MIDDLE_RING']['candidate']>0 for rec in core),
 core_source_peak_face_pairs=max(rec['pairs']['MIDDLE_RING']['baseline'] for rec in core),core_candidate_peak_face_pairs=max(rec['pairs']['MIDDLE_RING']['candidate'] for rec in core),
 witness_1_133333=min(r['records'],key=lambda rec:abs(rec['time']-1.1333333333333333)),handoff_1_4214275=min(r['records'],key=lambda rec:abs(rec['time']-1.4214275)),
 domain_witness=domain,regression_groups=group,key_regression_record_counts=keygroups,contact_counts=dict(Counter(row['event'] for row in r['contacts'])),
 contact_pad_change_max_mm=max(row['pad_change_mm'] for row in r['contacts']),
 new_other_digit_pair_records=[row for row in r['regressions'] if row['kind'].startswith('NEW_') and row['kind'].endswith('_FACE_PAIRS') and row['kind'] not in ['NEW_MIDDLE_RING_FACE_PAIRS','NEW_FULL_SELF_FACE_PAIRS']],
 candidate_sha256=edit['candidate_sha256'],full_candidate_video_produced=False)
save('B01_RESULT_SUMMARY.json',summary)
processes=[read(p) for p in sorted(OUT.glob('*_PROCESS.json'))]
start=datetime.fromisoformat(read(OUT/'SESSION_START.json')['started_utc'].replace('Z','+00:00'));now=datetime.now(timezone.utc)
save('COST_LEDGER.json',dict(started=start.isoformat(),recorded_summary=now.isoformat(),wall_seconds_to_summary=(now-start).total_seconds(),
 baseline_probe_seconds=read(OUT/'BASELINE_B01_ACTUAL.json')['seconds'],actual_edit_seconds=edit['seconds'],local_render_seconds=read(OUT/'LOCAL_RENDER_RECEIPT.json')['seconds'],
 local_encoding_and_media_check_seconds=read(OUT/'LOCAL_VIDEO_RECEIPT.json')['seconds'],real_complete_QC_seconds=r['seconds'],
 successful_complete_QC_process_seconds=next(p['seconds'] for p in processes if p['stage']=='validate_b01_once' and p['returncode']==0),
 failed_incomplete_QC_process_seconds=sum(p['seconds'] for p in processes if p['stage']=='validate_b01_once' and p['returncode']!=0),
 ordinary_media_bug_failed_process_seconds=2.1510941,processes=processes,
 bug_notes=['FFmpeg duration arguments required leading zero (0.9,0.85); no output produced at failure',
            'Diagnostic assumed identical evaluated quad triangulation; one sample changed diagonals. Fixed to use each real pose triangulation and disabled cache across changed triangle vertices. Same motion SHA, one completed full QC.'],
 curve_retries=0,parameter_retries=0,formal_candidates=1,completed_geometry_passes=1,optimizer_calls=0,
 time_note='Wall time includes reading, source verification, scripting, visual sequence inspection and bug handling; stage seconds are measured runtimes. No Human editing performed.'))
print(json.dumps(dict(core_samples=summary['core_samples'],core_source_intersections=summary['core_source_intersection_samples'],core_candidate_intersections=summary['core_candidate_intersection_samples'],
 source_peak=summary['core_source_peak_face_pairs'],candidate_peak=summary['core_candidate_peak_face_pairs'],domain_witness=domain,key_regression_record_counts=keygroups,contact_pad_change_max_mm=summary['contact_pad_change_max_mm']),indent=2))
