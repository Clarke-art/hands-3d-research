from stage_common import *
assert not list(P.glob('*.blend'))
scene=(R3/'03_scene_readback.py').read_text(encoding='utf8')
scene=scene.replace("dest=P/'STAGE_B_R3_LEFT_CONTACT_PLACEMENT_DESIGN_ONLY.blend'","dest=P/'STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend'")
scene=scene.replace('STAGE_B_R3_CONTACT_PLACEMENT_ONLY','STAGE_B_R3_DETERMINISTIC_RECOVERY_ONLY')
scene=scene.replace('DESIGN_ONLY_STAGE_B_R3_CONTACT_PLACEMENT_JOINTS','DESIGN_ONLY_STAGE_B_R3_SAVED_TRAJECTORY_RECOVERY_JOINTS')
scene=scene.replace("old=read(R2/'SCENE_MANIFEST.json');", "assert sha(P/'RECOVERY_POLICY.json')==read(P/'POLICY_LOCK.json')['policy_sha256']\nassert read(P/'RECOVERY_POLICY.json')['classification']=='WARN_ACCEPTABLE'\nassert sha(P/'motion.npz')==read(P/'SAVED_MOTION_RECONSTRUCTION.json')['motion_sha256']\nold=read(R2/'SCENE_MANIFEST.json');")
scene+='\ndump("RECOVERY_ATTEMPT.json",dict(attempt=1,status="BLENDER_SAVED_REOPENED_READBACK_VERIFIED",NEW_SOLVER_CALLS=0,candidate_count=1,source_guard_sha256=read(P/"POLICY_LOCK.json")["source_guard_sha256"],Blender_candidate_saved=True))\n'
(P/'03_scene_readback.py').write_text(scene,encoding='utf8')
diagnostics=(R3/'04_diagnostics.py').read_text(encoding='utf8').replace('from contact_region import *','from recovery_kernel import *')
diagnostics=diagnostics.replace("fit=read(P/'COORDINATED_TRAJECTORY_FIT.json')","fit=read(G/'SOLVER_RETURN_CHECKPOINT.json')['solver']")
diagnostics=diagnostics.replace("fit['solver_limit_reached']","fit['limit_reached']")
diagnostics+='\nengineering["NEW_SOLVER_CALLS"]=0\nengineering["solver_origin"]="Prior Guard Fix checkpoint, not new optimization"\nengineering["budget_risk_classification"]=read(P/"RECOVERY_POLICY.json")["classification"]\ndump("ENGINEERING_DIAGNOSTICS.json",engineering)\n'
(P/'04_actual_diagnostics.py').write_text(diagnostics,encoding='utf8')
for name in ['05_render.py','06_media.py']:
    text=(R3/name).read_text(encoding='utf8')
    if name=='05_render.py':text=text.replace("man=read(P/'SCENE_MANIFEST.json');", "assert read(P/'ENGINEERING_GATE.json')['pass_']\nman=read(P/'SCENE_MANIFEST.json');")
    (P/name).write_text(text,encoding='utf8')
import shutil
shutil.copyfile(R3/'R2_ALL_ACTIVE_PLACEMENT.json',P/'R2_ALL_ACTIVE_PLACEMENT.json')
dump('RECOVERY_CODE_REUSE.json',dict(source_scene_sha256=sha(R3/'03_scene_readback.py'),new_scene_sha256=sha(P/'03_scene_readback.py'),source_diagnostics_sha256=sha(R3/'04_diagnostics.py'),new_diagnostics_sha256=sha(P/'04_actual_diagnostics.py'),historical_sources_unchanged=True,new_solver_calls=0,reuse_scope='deterministic Action bake/readback and same cameras/media; no planner execution'))
print('DETERMINISTIC_SCENE_AND_SAME_CAMERA_MEDIA_ADAPTERS_PREPARED',flush=True)
