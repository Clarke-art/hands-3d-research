from stage_common import *
import ast
assert not (P/'GENERATION_LOCK.json').exists()
pre=read(P/'CONTINUOUS_PREFLIGHT.json');actual=read(P/'ACTUAL_LEFT_STATIC_READBACK.json')
assert pre['point_contact_supported'] and actual['actual_left_pad_vs_FK_max_mm']<.03
files=['stage_common.py','left_chord_base.py','left_continuous_motion.py','03_generate.py','04_scene.py']
for n in files:ast.parse((P/n).read_text(encoding='utf8'))
dump('GENERATION_LOCK.json',dict(candidate_limit=1,source_sha256=sha(SOURCE),timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),
    policy_sha256=sha(P/'GENERATION_POLICY.json'),input_lock_sha256=sha(P/'INPUT_LOCK.json'),scripts={n:sha(P/n) for n in files},
    complete_four_bar_input=True,no_dynamic_candidate_generated=True,fingering=[5,3,1,4,3,2,3]))
print('ONE_COMPLETE_LEFT_FOUR_BAR_CANDIDATE_LOCKED')
