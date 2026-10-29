import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
prefix=Path(__file__).with_name('baseline_blender.py').read_text(encoding='utf8').split('uniform=')[0]
exec(compile(prefix,str(Path(__file__).with_name('baseline_blender.py')),'exec'))
times=np.array([SCOPE['new']['note_on']-.035,SCOPE['new']['note_on'],SCOPE['old']['note_off']+POL['finger_release_follow_sec']])
VALL=[];Q=[];RW=[];QUAT=[];K=[]
for t in times:
    settime(float(t));V,F=vertices();VALL.append(V);Q.append([degrees(d) for d in c.DIGITS]);RW.append(np.array(rig.matrix_world))
    QUAT.append([list(b.rotation_quaternion) for b in rig.pose.bones]);K.append([bpy.data.objects[MAN['key_pivots'][str(k['key_index'])]].rotation_euler.x if str(k['key_index']) in MAN['key_pivots'] else 0 for k in c.KEYS])
np.savez_compressed(OUT/'ANCHOR_ACTUAL.npz',times=times,vertices=VALL,qdeg=Q,rig_world=RW,quat=QUAT,key_angles=K)
save('INITIALIZATION_REPAIR.json',dict(reason='Historical 60Hz numeric model interpolates root/basis; replace with exact C1 exported anchor world/basis/key matrices',
    prior_parity_mm=.07516299955282862,prior_optimizer_calls=0,parameter_policy_changed=False,new_candidates=0,exact_times=times))
print('EXACT_ANCHORS_EXPORTED_NO_ACTION',flush=True)
