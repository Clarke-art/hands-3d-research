from stage_common import *
import ast
assert not (P/'GENERATION_LOCK.json').exists()
feas=read(P/'STATIC_FEASIBILITY.json');actual=read(P/'ACTUAL_LEFT_STATIC_READBACK.json')
assert feas['point_contact_static_supported'] and actual['actual_left_pad_vs_FK_max_mm']<.03
for r in actual['tests']:
    if r['test']=='all_three_fully_down':
        assert len(r['measures'])==3
        assert all(v['skin_pad']['horizontal_mm']<2 and abs(v['skin_pad']['gap_mm'])<8 for v in r['measures'])
files=['stage_common.py','left_chord_motion.py','03_generate.py','04_scene.py']
for n in files:ast.parse((P/n).read_text(encoding='utf8'))
dump('GENERATION_LOCK.json',dict(candidate_limit=1,input_lock_sha256=sha(P/'INPUT_LOCK.json'),
    source_sha256=sha(SOURCE),timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),policy_sha256=sha(P/'GENERATION_POLICY.json'),
    scripts={n:sha(P/n) for n in files},preflight_actual_skin_supported=True,
    fingering_unchanged=[5,3,1],no_dynamic_candidate_generated=True,render_result_available=False))
print('ONE_LEFT_CHORD_CANDIDATE_LOCKED_AFTER_ACTUAL_STATIC_READBACK')
