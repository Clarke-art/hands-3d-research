"""Commit the same one locked partial result; retain strict clearance FAIL.

The source module and its policy hashes remain unchanged. There is no second
fit, changed amplitude/window, altered contact guard or new motion trajectory.
The user explicitly permits natural finger adjacency and PARTIAL classification,
and requires Human-visible quality over a blanket zero-intersection criterion.
"""
import sys,shutil
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from local_common import *
review=read(P/'ANIMATED_PRECOMMIT_VISUAL_REVIEW.json');assert review['pass_'] and not review['confirmed_new_visible_defect']
first=read(P/'IN_MEMORY_VALIDATION.json');assert first['local_bad_samples']
shutil.copyfile(P/'IN_MEMORY_VALIDATION.json',P/'FIRST_LOCKED_EVALUATION.json')
assert read(P/'LOCAL_DOMAIN_AND_CONTINUITY.json')['pass_']
module=P/'06_apply_validate.py';text=module.read_text(encoding='utf8');prefix=text[:text.index('\nvalidation=validate()')]
# Execute the original hash-locked deterministic construction, byte-for-byte.
# This reconstructs exactly the same retained curve; no original code is edited.
exec(compile(prefix,str(module),'exec'))
def evaluate_same_partial():
    try:validate()
    except AssertionError as error:
        assert error.args and error.args[0][0]=='LOCAL_PATCH_INTERSECTION_REMAINS',('UNEXPECTED_GUARD_FAILURE',str(error))
    else:raise AssertionError('Expected preserved residual must not silently become a geometric PASS')
    got=read(P/'IN_MEMORY_VALIDATION.json')
    assert got['metrics']==first['metrics'] and got['local_bad_samples']==first['local_bad_samples'],('SAME_LOCKED_RESULT_NOT_IDENTICAL',got['metrics'])
    return dict(functional_and_non_target_guards='PASS',refinement='PARTIAL',exact_zero_geometric_intersection='FAIL_RETAINED',same_locked_result_identical=True,metrics=got['metrics'],samples=got['samples'],local_bad_samples=len(got['local_bad_samples']),motion_solver_calls=0,parameter_changes=0)
before=evaluate_same_partial()
sc.name='STAGE_C_R2_LOCAL_FINGER_OVERLAP_DESIGN_ONLY';sc['DESIGN_ONLY']=True;sc['HUMAN_APPROVAL_PENDING']=True;sc['LOCAL_REFINEMENT_POLICY_SHA256']=lock['policy_sha256'];sc['SOURCE_C1_SHA256']=man['sha256'];sc['LOCAL_REFINEMENT']='PARTIAL';sc['STRICT_ZERO_GEOMETRIC_INTERSECTION']='FAIL_RETAINED_AS_WARN';sc['NEW_MOTION_SOLVER_CALLS']=0
sc.camera=bpy.data.objects[man['cameras']['TEACHING']];settime(sc,0)
dump('CANDIDATE_COMMIT.json',dict(count=1,state='SOLE_SAME_LOCKED_PARTIAL_CANDIDATE_SAVE_STARTED',policy_sha256=lock['policy_sha256'],parameter_changes=0))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
newman=dict(man,path=str(DEST),sha256=sha(DEST),scene=sc.name,source_C1_sha256=man['sha256'],actual_camera_parameters=actual_cameras,local_action=new.name,local_policy_sha256=lock['policy_sha256'],candidate_count=1,refinement='PARTIAL',strict_zero_geometric_intersection='FAIL_RETAINED')
dump('SCENE_MANIFEST.json',newman)
bpy.ops.wm.open_mainfile(filepath=str(DEST),load_ui=False,use_scripts=False);sc=bpy.data.scenes[newman['scene']];bpy.context.window.scene=sc;camera=bpy.data.objects[newman['cameras']['OVERHEAD']]
after=evaluate_same_partial()
dump('SAVED_CANDIDATE_VALIDATION.json',dict(functional_and_non_target_guards='PASS',before_save=before,after_reopen=after,strict_zero_geometric_intersection='FAIL_RETAINED',refinement='PARTIAL',Human_visible_quality='HUMAN_PENDING'))
dump('CANDIDATE_COMMIT.json',dict(count=1,state='SOLE_SAME_LOCKED_PARTIAL_CANDIDATE_SAVED_REOPENED_VERIFIED',sha256=newman['sha256'],policy_sha256=lock['policy_sha256'],motion_solver_calls=0,parameter_changes=0))
doc('STRICT_CLEARANCE_GATE_AND_USER_SCOPE.md','# Retained partial result and original strict clearance failure\n\nThe original06_apply_validate.py enforces a blanket zero-target-patch-intersection assertion. The one locked−6degree trajectory passed every active-contact and non-target preservation guard, but failed that stronger geometric assertion at24 finite samples near video1.108333–1.191667s, max16 intersecting patch triangle pairs. Its first log, first numeric result and unchanged policy/module hashes are retained. Geometric clearance is explicitly FAIL, not relabeled PASS.\n\nThe user requires Human-visible quality first, explicitly allows PARTIAL classification, recognizes natural adjacent-finger closeness, and prohibits endless optimization of tiny hidden geometric error. Normal unchanged-camera frames show substantially reduced extended fingertip fusion, preserved curvature and no newly confirmed visible defect. Therefore the SAME locked trajectory is committed once as a PARTIAL/WARN candidate for Human review. No amplitude, time window, contact guard, fingering, solver setting or frozen asset was changed after the strict assertion failure; no second trajectory or saved candidate exists. Original policy/model implementation remains byte-identical.\n\nThis is not a new geometry tolerance or automatic Human acceptance. Human must inspect the remaining brief fingertip adjacency and may reject it. The round stops after this one partial result.\n')
print('ONE_SAME_LOCKED_PARTIAL_CANDIDATE_SAVED_NO_RETUNING',flush=True)
