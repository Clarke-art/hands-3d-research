from common import *
from datetime import datetime,timezone
import subprocess,re
qc=read(OUT/'B01_MACHINE_VALIDATION.json');edit=read(OUT/'EDIT_RECEIPT.json');rb=read(OUT/'CANDIDATE_READBACK.json');media=read(OUT/'FINAL_LOCAL_VIDEO_RECEIPT.json')
assert not qc['pass_'] and rb['pass_'] and edit['candidates']==1 and edit['optimizer_calls']==0
assert sha(edit['candidate_path'])==edit['candidate_sha256']==qc['candidate_sha256']==rb['candidate_sha256']
source_records={}
for p in OUT.glob('*PROTECTION.json'):
    for row in read(p)['files']:
        assert row['unchanged']
        if row['path'] in source_records:assert source_records[row['path']]==row['before']
        source_records[row['path']]=row['before']
for p in [ROOT/'AGENTS.md',ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid',
          ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/OVERLAP_IDENTITY_AND_CAUSE.md',
          ROOT/'experiments/hands_c1_full_overhead_teaching_review_r1/CAMERA_FRAMING_CHECK.json']:
    source_records.setdefault(str(p),sha(p))
rows=[dict(path=p,before=h,delivery=sha(p),unchanged=h==sha(p)) for p,h in source_records.items()];assert all(r['unchanged'] for r in rows)
for file in media['files']:
    assert sha(OUT/file['file'])==file['sha256']
    meta=json.loads(subprocess.check_output(['D:/ffmpeg/bin/ffprobe.exe','-v','error','-count_frames','-show_streams','-of','json',str(OUT/file['file'])]))
    v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert int(v['nb_read_frames'])==51 and v['r_frame_rate']=='60/1' and float(v['start_time'])==float(a['start_time'])==0
    assert abs(float(a['duration'])-.85)<.025
report=OUT/'FINAL_B01_VISUAL_REVIEW.md';text=report.read_text(encoding='utf8')
for link in re.findall(r'\]\(<(D:/[^>]+)>\)',text):assert safe(link).is_file(),link
assert all(s in text for s in ['RESULT = GENERATED_WITH_DEFECTS','B01_MACHINE_VALIDATION = FAIL','HUMAN_VISUAL_ACCEPTANCE = PENDING','ORIGINAL_C1 = UNCHANGED','B02_B03 = NOT_MODIFIED','STOP — HUMAN REVIEW'])
assert len(list(OUT.glob('B01_MULTIJOIN_SINGLE_CANDIDATE*.blend')))==1
assert not list(OUT.glob('*FULL*OVERHEAD*.mp4'))
files=[report,Path(edit['candidate_path']),OUT/'B01_BEFORE_AFTER_OVERHEAD_1X_NOT_APPROVED.mp4']
start=datetime.fromisoformat(read(OUT/'SESSION_START.json')['started_utc'].replace('Z','+00:00'));now=datetime.now(timezone.utc)
save('DELIVERY_RECEIPT.json',dict(task='HANDS_B01_VISUAL_ANIMATION_REFINEMENT_R1',RESULT='GENERATED_WITH_DEFECTS',B01_MACHINE_VALIDATION='FAIL',HUMAN_VISUAL_ACCEPTANCE='PENDING',ORIGINAL_C1='UNCHANGED',B02_B03='NOT_MODIFIED',
 completed_at=now.isoformat(),wall_seconds=(now-start).total_seconds(),files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in files],source_checks=rows,
 final_media_receipt='FINAL_LOCAL_VIDEO_RECEIPT.json',audio_mux_repair_seconds=media['seconds'],
 actual_edit_strategies=1,formal_motion_candidates=1,full_completed_geometry_passes=1,full_video_produced=False,diagnostic_video_marked_NOT_APPROVED=True,
 input_scope='Explicit referenced-file union only; additional prose/MIDI/AGENTS snapshots taken at delivery, not falsely claimed to be pre-run records',piano_access=False,optimizer_calls=0))
print(json.dumps(dict(delivery_pass=True,machine_validation='FAIL',wall_seconds=(now-start).total_seconds(),unchanged_inputs=len(rows),candidate_sha256=sha(edit['candidate_path']),comparison_video=media['files'][1]),indent=2))
