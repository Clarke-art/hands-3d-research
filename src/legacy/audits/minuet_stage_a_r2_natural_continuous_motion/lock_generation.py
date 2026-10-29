from stage_common import *
import ast
assert not (P/'GENERATION_LOCK.json').exists()
files=['stage_common.py','coordinated_motion.py','02_generate.py','03_scene.py']
for n in files:ast.parse((P/n).read_text(encoding='utf8'))
dump('GENERATION_LOCK.json',dict(candidate_limit=1,source_sha256=sha(SOURCE),
    timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),policy_sha256=sha(P/'GENERATION_POLICY.json'),
    input_lock_sha256=sha(P/'INPUT_LOCK.json'),R1_camera_bind_sha256=sha(P/'R1_REVIEW_CAMERA_BIND.json'),
    scripts={n:sha(P/n) for n in files},no_render_result_available=True))
print('ONE_NEW_DYNAMIC_CANDIDATE_GENERATION_LOCKED')
