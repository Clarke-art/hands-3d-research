from common import *
from collections import Counter
from datetime import datetime,timezone
qc=read(OUT/'MACHINE_VALIDATION.json');edit=read(OUT/'EDIT_RECEIPT.json');base=read(OUT/'BASELINE_LOCAL_PROBE.json');handoff=read(OUT/'HUMAN_HANDOFF_RECEIPT.json')
core=[r for r in qc['records'] if 4.85-1e-9<=r['time']<=5.25+1e-9]
witness=min(qc['records'],key=lambda r:abs(r['time']-4.916666666666667))
counts=Counter(r['kind'] for r in qc['regressions'])
groups={k:dict(records=v,distinct_times=len({r['time'] for r in qc['regressions'] if r['kind']==k}),first=min(r['time'] for r in qc['regressions'] if r['kind']==k),last=max(r['time'] for r in qc['regressions'] if r['kind']==k)) for k,v in counts.items()}
dsharp=[r for r in qc['regressions'] if r.get('key')=='D#5']
target=[r for r in qc['regressions'] if r['kind']=='TARGET_REGRESSION']
processes=[read(p) for p in sorted(OUT.glob('*_PROCESS.json'))]
session=read(OUT/'SESSION_START.json');now=datetime.now(timezone.utc)
ledger=dict(recorded_session_start_utc=session['started_utc'],summary_utc=now.isoformat(),recorded_session_elapsed_seconds=(now-datetime.fromisoformat(session['started_utc'].replace('Z','+00:00'))).total_seconds(),
    first_read_clock_utc='2026-10-15T00:05:54+00:00',first_read_clock_to_summary_seconds=(now-datetime.fromisoformat('2026-10-15T00:05:54+00:00')).total_seconds(),
    baseline_probe_file_created_utc=datetime.fromtimestamp((OUT/'BASELINE_LOCAL_PROBE.json').stat().st_ctime,timezone.utc).isoformat(),
    source_copy_seconds=base['copy_seconds'],baseline_setup_probe_seconds=base['total_seconds'],edit_process_seconds=edit['seconds'],
    edit_lock_to_receipt_wall_seconds=(OUT/'EDIT_RECEIPT.json').stat().st_mtime-(OUT/'STRATEGY_LOCK.json').stat().st_mtime,
    real_geometry_check_seconds=qc['seconds'],actual_validation_including_archive_and_protection_seconds=next(p['seconds'] for p in processes if p['stage']=='validate_once'),
    baseline_video_seconds=read(OUT/'BASELINE_PREVIEW_RECEIPT.json')['seconds'],after_video_seconds=None,after_video_reason='Machine gate FAIL; no candidate render/preview generated',
    handoff_preparation_seconds=handoff['seconds'],human_edit_seconds=None,human_edit_performed=False,human_instructions_steps=8,actual_human_clicks=None,
    failed_software_process_seconds=sum(p['seconds'] for p in processes if p['returncode']!=0),processes=processes,
    cost_caveat='Wall intervals include scripting, inspection and ordinary bug fixes; process seconds are measured. Failed-process runtime does not include all reasoning/debugging wall time. Initial reading before first clock was not separately timed.',
    bug_records=[dict(issue='Blender script directory absent from sys.path',effect='Initial baseline script stopped before source copy',resolution='Explicit script directory insertion'),
                 dict(issue='LINEAR F-Curve unused AUTO handles recalculate',effect='Outside-value assertion overincluded non-evaluated handles; no candidate saved at failure',resolution='Preserve exact outside key values/interpolation, restore handle coordinates, validate outside actual skin unchanged; same locked edit'),
                 dict(issue='Blender5 selection API moved to PoseBone.select; select_pattern operator absent',effect='Handoff UI selection only; no motion change or saved handoff at failures',resolution='Inspect local RNA and use PoseBone.select')])
summary=dict(task='HANDS_PROCEDURAL_ANIMATION_PRODUCTION_FEASIBILITY_R1',RESULT='HUMAN_EDIT_REQUIRED',MACHINE_VALIDATION='FAIL',HUMAN_NATURALNESS='NOT_TESTED',GENERAL_MIDI_AUTOMATION='NOT_VALIDATED',
    witness=witness,core_baseline_vertex_peak_mm=max(r['target_vertex_mm'][0] for r in core),core_candidate_vertex_peak_mm=qc['target_core_peak_vertex_mm'],
    core_baseline_surface_peak_upper_mm=max(r['target_surface_upper_mm'][0] for r in core),core_candidate_surface_peak_upper_mm=qc['target_core_peak_surface_upper_mm'],
    regression_groups=groups,dsharp_vertex_max_mm=max([r.get('candidate_mm',0) for r in dsharp if r['kind']=='OTHER_REGION_VERTEX_REGRESSION']+[0]),
    dsharp_surface_max_mm=max([r.get('candidate_mm',0) for r in dsharp if r['kind']=='OTHER_REGION_SURFACE_REGRESSION']+[0]),
    target_exit_vertex_worsening_max_mm=max([r['candidate_mm']-r['baseline_mm'] for r in target]+[0]),
    no_new_digit_self_crosshand_faces=not any(r['new'] for rec in qc['records'] for r in rec['pairs'].values()),
    candidate_count=1,complete_geometry_passes=1,optimizer_calls=0,new_candidate_video=False,human_edit_handoff=handoff['file'],
    contact_counts=dict(Counter(r['event'] for r in qc['contacts'])),historical_defects_retained=True)
save('PRODUCTION_RESULT.json',summary);save('COST_LEDGER.json',ledger)
# Merge actual input-read hashes from this experiment's explicit protection receipts.
expected={}
for p in OUT.glob('*PROTECTION.json'):
    for row in read(p)['files']:
        assert row['unchanged']
        if row['path'] in expected:assert expected[row['path']]==row['before']
        expected[row['path']]=row['before']
for p in [ROOT/'AGENTS.md',ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid',
          ROOT/'audits/piano_pedagogical_demonstration_audit_r1/TEACHING_DEFECT_REGISTER.md',
          ROOT/'audits/piano_hands_product_route_reassessment_r1/PRODUCT_BASELINE_REVIEW.md']:
    expected.setdefault(str(safe(p)),sha(p))
rows=[dict(path=p,before=h,after=sha(p),unchanged=h==sha(p)) for p,h in expected.items()]
assert all(r['unchanged'] for r in rows)
assert sha(OUT/'C_RING_SINGLE_CANDIDATE_NOT_APPROVED.blend')==edit['candidate_sha256']
assert sha(OUT/handoff['file'])==handoff['sha256']
save('FINAL_INPUT_PROTECTION.json',dict(all_unchanged=True,files=rows,scope='Explicit input union only; additional prose/AGENTS/MIDI hashed at delivery, not falsely described as new pre-run snapshots',piano_access=False))
print(json.dumps(dict(summary={k:summary[k] for k in ['core_baseline_vertex_peak_mm','core_baseline_surface_peak_upper_mm','dsharp_vertex_max_mm','dsharp_surface_max_mm','target_exit_vertex_worsening_max_mm']},
                      cost={k:ledger[k] for k in ['recorded_session_elapsed_seconds','source_copy_seconds','baseline_setup_probe_seconds','edit_process_seconds','edit_lock_to_receipt_wall_seconds','real_geometry_check_seconds','baseline_video_seconds','failed_software_process_seconds']},input_hashes=len(rows)),indent=2))
