from common import *
from datetime import datetime,timezone
report=OUT/'FINAL_PRODUCTION_FEASIBILITY.md';text=report.read_text(encoding='utf8')
assert all(x in text for x in ['RESULT = HUMAN_EDIT_REQUIRED','MACHINE_VALIDATION = FAIL','HUMAN_NATURALNESS = NOT_TESTED','GENERAL_MIDI_AUTOMATION = NOT_VALIDATED','STOP — HUMAN REVIEW'])
check=read(OUT/'FINAL_INPUT_PROTECTION.json');rows=[]
for row in check['files']:
    actual=sha(row['path']);assert actual==row['after'];rows.append(dict(path=row['path'],expected=row['after'],delivery=actual,unchanged=True))
handoff=read(OUT/'FINAL_HANDOFF_RECEIPT.json');assert handoff['readback_pass'] and handoff['action_motion_unchanged']
assert sha(OUT/handoff['file'])==handoff['sha256']
edit=read(OUT/'EDIT_RECEIPT.json');assert sha(edit['candidate_path'])==edit['candidate_sha256']
preview=read(OUT/'BASELINE_PREVIEW_RECEIPT.json')
for video in preview['files']:assert sha(OUT/video['file'])==video['sha256']
assert not list(OUT.glob('after*.mp4'))
assert len(list(OUT.glob('C_RING_SINGLE_CANDIDATE*.blend')))==1
assert len(list(OUT.glob('FULL_VALIDATION_STARTED.json')))==1
import re
links=re.findall(r'\]\(<(D:/[^>]+)>\)',text)
for link in links:assert safe(link).is_file(),link
files=[OUT/handoff['file'],OUT/'HUMAN_EDIT_INSTRUCTIONS_FINAL.txt',OUT/'C_RING_SINGLE_CANDIDATE_NOT_APPROVED.blend',
       OUT/'before_C1_teaching_1x.mp4',OUT/'before_C1_side_oblique_1x.mp4',report]
now=datetime.now(timezone.utc);start=datetime.fromisoformat(read(OUT/'SESSION_START.json')['started_utc'].replace('Z','+00:00'))
receipt=dict(task='HANDS_PROCEDURAL_ANIMATION_PRODUCTION_FEASIBILITY_R1',RESULT='HUMAN_EDIT_REQUIRED',MACHINE_VALIDATION='FAIL',HUMAN_NATURALNESS='NOT_TESTED',GENERAL_MIDI_AUTOMATION='NOT_VALIDATED',
    completed_at=now.isoformat(),session_wall_seconds=(now-start).total_seconds(),first_recorded_clock_to_delivery_seconds=(now-datetime.fromisoformat('2026-10-15T00:05:54+00:00')).total_seconds(),
    final_human_handoff=handoff,deliverables=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files],source_checks=rows,
    candidate_count=1,complete_geometry_passes=1,solver_calls=0,after_candidate_video=False,human_edit_performed=False,piano_access=False,report_links_verified=len(links),
    final_handoff_instruction_process=read(OUT/'finalize_handoff_instructions_PROCESS.json'))
save('DELIVERY_RECEIPT.json',receipt)
print(json.dumps(dict(pass_=True,session_wall_seconds=receipt['session_wall_seconds'],first_clock_to_delivery_seconds=receipt['first_recorded_clock_to_delivery_seconds'],verified_inputs=len(rows),links=len(links),final_handoff=handoff['file']),indent=2))
