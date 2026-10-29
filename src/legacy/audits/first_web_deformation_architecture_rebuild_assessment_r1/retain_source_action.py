import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
# Serialization repair only: detached ZERO Action must be retained in saved POCs.
for r,n in [('A','LOCAL_RETOPOLOGY'),('B','HELPER_BONE'),('C','LOCAL_CAGE')]:
    path=OUT/f'ROUTE_{r}_{n}_POC_R1.blend';ob,rig=load(path)
    if ACTION not in bpy.data.actions:
        with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):dst.actions=[ACTION]
        bpy.data.actions[ACTION].use_fake_user=True
        assert digest(action_payload(bpy.data.actions[ACTION]))==read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['actions_before'][ACTION]
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=False)
        row=read(OUT/f'ROUTE_{r}_BUILD_R1.json');row['sha256']=sha(path);row['serialization_repair']='Detached ZERO original Action explicitly retained, no geometry/rig/design changes';dump(f'ROUTE_{r}_BUILD_R1.json',row)
inputs();print('SOURCE_ACTION_RETAINED_ALL_POCS')
