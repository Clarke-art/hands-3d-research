import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import *
from persistence import atomic_record,atomic_json
import bpy,numpy as np,math
from mathutils import Matrix,Vector
sys.path.insert(0,str(OLD));import performance_core as c
I=read(O/'INPUT_BINDINGS.json');P=read(O/'POLICY.json');man=I['source_scene']
helpers=ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1'
functions_from(helpers/'blender_preflight.py',['digest','native','settime','coords'],globals())
functions_from(ROOT/'experiments/hands_role_aware_collision_avoidance_r1/baseline_blender.py',['degrees'],globals())
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);assert not bpy.data.libraries
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
assert digest(native(mesh,rig))==I['native_sha256']
relation=np.array(I['full_root_rig_relation']);base=np.array(I['base_xyz_m']);static=np.array(I['static_root_base_matrix'])
times=np.unique(np.r_[P['control_times_sec'],P['evaluation_times_sec'],P['blender_check_times_sec']]);states=[];verts=[];basis=[];worlds=[];keyangles=[]
for t in times:
 settime(sc,float(t));V,F=coords(mesh);world=np.array(rig.matrix_world);C=<REDACTED_EMAIL>(relation)@np.linalg.inv(static)
 xyz=(C[:3,:3]@base+C[:3,3]-base)*1000;rot=np.degrees(list(Matrix(C[:3,:3].tolist()).to_euler('XYZ')))
 states.append(np.r_[xyz,rot,np.array([degrees(d) for d in c.DIGITS]).ravel()]);verts.append(V);basis.append([np.array(b.matrix_basis)[:3,:3] for b in rig.pose.bones]);worlds.append(world)
 ka=np.zeros(88)
 for ki,name in man['key_pivots'].items():ka[int(ki)]=bpy.data.objects[name].rotation_euler.x
 keyangles.append(ka)
atomic_record('SOURCE_PROBE.npz',dict(times=times,states=states,vertices=verts,joint_basis=basis,rig_world=worlds,key_angles=keyangles),dict(record_type='FROZEN_C1_ACTUAL_REFERENCE',bone_names=[b.name for b in rig.pose.bones],native_sha256=I['native_sha256'],source_sha256=sha(man['path']),libraries=0,no_source_save=True))
atomic_json('SOURCE_PROBE_RECEIPT.json',dict(samples=len(times),actual_skin=True,exact_time_sampling=True,source_unchanged=True,native_matches=True,new_actions=0,new_blends=0))
protect();print('FROZEN_C1_SOURCE_PROBE',len(times),'exact times; no source edits/saves')
