import bpy
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime import *
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import math
SCOPE=read(OUT/'EVENT_SCOPE.json');start,end=SCOPE['start'],SCOPE['end']
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
sc=bpy.data.scenes[MAN['scene']];bpy.context.window.scene=sc
assert not bpy.data.libraries, 'External linked libraries would require separate access review'
rig=bpy.data.objects[MAN['mapping']['R']['rig']];mesh=bpy.data.objects[MAN['mapping']['R']['mesh']]
ROIS=read(ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_SKIN_ROI.json')
def settime(t):
    f=1+60*t;i=math.floor(f);sc.frame_set(i,subframe=f-i);bpy.context.view_layer.update()
def vertices():
    ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    V=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);F=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear()
    return V,F
def degrees(d):
    names,_,axes,spread,_=c.SETUPS['R',d];mats=[np.array(rig.pose.bones[n].rotation_quaternion.to_matrix()) for n in names]
    a=axes[0]/np.linalg.norm(axes[0]);s=spread/np.linalg.norm(spread);v=mats[0]@a
    sp=np.arctan2(np.dot(s,np.cross(a,v)),np.dot(a,v));mats[0]=c.axisrot(-sp,s)@mats[0]
    q=[]
    for mat,axis in zip(mats,axes):
        axis=axis/np.linalg.norm(axis);vee=np.array([mat[2,1]-mat[1,2],mat[0,2]-mat[2,0],mat[1,0]-mat[0,1]])*.5
        q.append(np.arctan2(np.dot(axis,vee),(np.trace(mat)-1)*.5))
    return np.degrees(q+[sp])
def pair(V):
    trees=[BVHTree.FromPolygons([Vector(v) for v in V],ROIS[d]['faces'],epsilon=0) for d in ['MIDDLE','RING']]
    pairs=trees[0].overlap(trees[1])
    return dict(triangle_pairs=len(pairs),face_examples=[[ROIS['MIDDLE']['faces'][a],ROIS['RING']['faces'][b]] for a,b in pairs[:2]])
uniform=np.arange(math.ceil(start*240),math.floor(end*240)+1)/240
events=[n[x] for n in NOTES for x in ['note_on','note_off'] if start<=n[x]<=end]
times=np.unique(np.r_[start,end,uniform,events,[r['t'] for r in SCOPE['reference_tasks'] if start<=r['t']<=end]])
rows=[];VALL=[];Q=[];RW=[];K=[];QUAT=[]
for t in times:
    settime(float(t));V,F=vertices();r=pair(V)
    rows.append(dict(t=float(t),**r));VALL.append(V);Q.append([degrees(d) for d in c.DIGITS]);RW.append(np.array(rig.matrix_world))
    QUAT.append([list(b.rotation_quaternion) for b in rig.pose.bones]);K.append([bpy.data.objects[MAN['key_pivots'][str(k['key_index'])]].rotation_euler.x if str(k['key_index']) in MAN['key_pivots'] else 0 for k in c.KEYS])
np.savez_compressed(OUT/'BASELINE_ACTUAL.npz',times=times,vertices=VALL,qdeg=Q,rig_world=RW,quat=QUAT,key_angles=K)
hit=[r for r in rows if r['triangle_pairs']]
save('BASELINE_GEOMETRY.json',dict(rows=rows,samples=len(times),first_hit=hit[0]['t'] if hit else None,last_hit=hit[-1]['t'] if hit else None,
    max_pairs=max(r['triangle_pairs'] for r in rows),boundaries=[rows[0],rows[-1]],faces=F,
    bone_names=[b.name for b in rig.pose.bones],source_sha256=sha(SOURCE),sampling='240 Hz plus exact events and phase boundaries',
    saved_source=False,library_count=len(bpy.data.libraries)))
print('BASELINE_LOCAL_ACTUAL',len(times),'crossing',hit[0]['t'],hit[-1]['t'],'peak',max(r['triangle_pairs'] for r in rows),flush=True)
