from stage_common import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
text=(B1/'left_chord_motion.py').read_text(encoding='utf8').replace('class EventCoordinator:','class BaseEventCoordinator:')
(P/'left_chord_base.py').write_text(text,encoding='utf8')
dump('BASELINE_CODE_REUSE_BIND.json',dict(source=str(B1/'left_chord_motion.py'),source_sha256=sha(B1/'left_chord_motion.py'),
    copy_sha256=sha(P/'left_chord_base.py'),only_base_class_name_changed=True,original_unmodified=True,
    Stage_A_R2_framework_retained=True,actual_left_FK_retained=True,right_trajectory_mirrored=False))
print('UNCHANGED_B1_KERNEL_COPIED_AS_BASE')
