"""Read saved Lightweight source only; no pose search or asset save."""
import sys,json,hashlib,math
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];SRC=ROOT/'audits/minuet_stage_c_lightweight_animation_poc_r1'
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'))
from blender_local import *
P=Path(__file__).resolve().parent
def output(n,x):(P/n).write_text(json.dumps(x,indent=2,default=lambda x:x.tolist()),encoding='utf8')
man=read(SRC/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']=='18d3c729ff16759a4a7b41a621a1682711d876ad2e109a748d1ea9e675762df3'
timeline=read(C1/'PERFORMANCE_TIMELINE.json');assert sha(MIDI)==timeline['source_sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
assert rig.animation_data.action.name=='DESIGN_ONLY_LIGHTWEIGHT_R1_RIGHT_JOINTS_NOT_APPROVED'
def decompose(d):
 names,_,axes,spread,_=c.SETUPS['R',d];mats=[np.array(rig.pose.bones[n].rotation_quaternion.to_matrix()) for n in names];a=axes[0]/np.linalg.norm(axes[0]);s=spread/np.linalg.norm(spread);v=mats[0]@a;sp=np.arctan2(np.dot(s,np.cross(a,v)),np.dot(a,v));mats[0]=c.axisrot(-sp,s)@mats[0];vals=[]
 for mat,axis in zip(mats,axes):
  axis=axis/np.linalg.norm(axis);vee=np.array([mat[2,1]-mat[1,2],mat[0,2]-mat[2,0],mat[1,0]-mat[0,1]])*.5;vals.append(np.arctan2(np.dot(axis,vee),(np.trace(mat)-1)*.5))
 return np.degrees(vals+[sp])
model=read(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL_MANIFEST.json');legacy=read(C1/'SCENE_MANIFEST.json');ts=np.arange(715)/120;qs=[];quats=[];world=[];angles=[]
for t in ts:
 settime(sc,float(t));qs.append([decompose(d) for d in c.DIGITS]);quats.append([list(rig.pose.bones[n].rotation_quaternion) for n in model['bones']]);world.append(np.array(rig.matrix_world));angles.append([bpy.data.objects[legacy['key_pivots'][str(k)]].rotation_euler.x if str(k) in legacy['key_pivots'] else 0 for k in range(88)])
np.savez_compressed(P/'LIGHTWEIGHT_SOURCE_SAMPLES.npz',times=ts,qdeg=qs,quat=quats,rig_world=world,key_angles=angles)
probes=[]
for t in [1.133333333,3.825,2.6,4.05,4.916666667]:
 settime(sc,t);V,F=mesh_pose(mesh);probes.append(dict(time=t,vertices=V.tolist(),qdeg=[decompose(d).tolist() for d in c.DIGITS],roles={d:('ACTIVE' if any(n['hand']=='R' and n['finger']==j+1 and n['note_on']<=t<=n['note_off'] for n in timeline['notes']) else 'RELEASE_PREPARE_OR_IDLE') for j,d in enumerate(c.DIGITS)}))
output('SOURCE_PROBES.json',probes)
output('PREFLIGHT.json',dict(source=man,source_action=rig.animation_data.action.name,midi_sha256=sha(MIDI),notes=23,roles=[dict(time=p['time'],roles=p['roles']) for p in probes],bounds={d:[np.degrees(x).tolist() for x in c.bounds(d)] for d in c.DIGITS},candidate_count=0,preflight_pose_searches=0,D5_off=3.778568,release_not_hold=True))
print('PREFLIGHT_SOURCE_CONFIRMED',flush=True)

