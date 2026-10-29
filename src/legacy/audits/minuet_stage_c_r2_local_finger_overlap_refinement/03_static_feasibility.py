import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_local import *
assert not DEST.exists() and not (P/'LOCAL_CORRECTION_POLICY_LOCK.json').exists()
man=read(C1/'SCENE_MANIFEST.json');tl=read(C1/'PERFORMANCE_TIMELINE.json');roi=read(P/'LOCAL_SKIN_ROI.json');numeric=dict(np.load(P/'source_numeric.npz'))
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
info=man['mapping']['R'];rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']];cam=bpy.data.objects[man['cameras']['OVERHEAD']]
settime(sc,1.05);roi['LITTLE']=finger_roi(mesh,rig,'LITTLE');dump('LOCAL_SKIN_ROI_WITH_NEIGHBOR.json',roi)
times=[.966666667,1.05,1.2,1.383333333,1.4214275,1.45,1.55,1.635713,1.70,1.80,1.85]
curves_save={name:rig.pose.bones[name].rotation_quaternion.copy() for name in c.SETUPS['R','RING'][0]}
# Limited static pose tests, not animated candidates and not a motion solve.
rig.animation_data.action=None
def q_at(t):return np.array([[np.interp(t,numeric['times'],numeric['qdeg'][:,j,k]) for k in range(4)] for j in range(5)])
def apply_q(q):
    for j,d in enumerate(c.DIGITS):
        for name,mat in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,np.radians(q[j]))):
            bone=rig.pose.bones[name];bone.rotation_quaternion=Matrix(mat).to_quaternion()
    bpy.context.view_layer.update()
rows=[]
for delta in [0,-1,-2,-3,-4,-5,-6]:
    samples=[]
    for t in times:
        settime(sc,t);q=q_at(t);q[3,3]+=delta;apply_q(q);V,_=mesh_pose(mesh);rel=local_relation(V,roi,cam);neighbor=local_relation(V,{'MIDDLE':roi['RING'],'RING':roi['LITTLE']},cam)
        pp=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['R']])
        active=[]
        for n in tl['notes']:
            if n['hand']=='R' and n['note_on']<=t<n['note_off']:
                angle=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x;k=c.KEYS[n['key_index']];marker=contact(pp[n['finger']-1],k,angle);skin=contact(V[c.MARKERS['R'][n['finger']-1]['mesh_vertex']],k,angle)
                active.append(dict(note_id=n['note_id'],finger=n['finger'],marker=marker,skin=skin))
        samples.append(dict(presentation_sec=t,music_sec=t-.35,**rel,ring_little_patch_triangle_pairs=neighbor['intersecting_patch_triangle_pairs'],active_contacts=active))
    rows.append(dict(ring_MCP_spread_delta_deg=delta,samples=samples,target_patch_pair_sum=sum(s['intersecting_patch_triangle_pairs'] for s in samples),neighbor_patch_pair_sum=sum(s['ring_little_patch_triangle_pairs'] for s in samples),maximum_active_skin_gap_mm=max(abs(a['skin']['gap_mm']) for s in samples for a in s['active_contacts']),maximum_active_skin_horizontal_mm=max(a['skin']['horizontal_mm'] for s in samples for a in s['active_contacts'])))
    print('FINITE_STATIC_DELTA',delta,'PAIRS',rows[-1]['target_patch_pair_sum'],'GAP',rows[-1]['maximum_active_skin_gap_mm'],'MISS',rows[-1]['maximum_active_skin_horizontal_mm'],'NEIGHBOR',rows[-1]['neighbor_patch_pair_sum'],flush=True)
dump('STATIC_FEASIBILITY.json',dict(rows=rows,finite_pose_tests=7*len(times),motion_solver_calls=0,animated_candidates=0,only_one_target_DOF='RING_MCP_R spread axis, inherited approved FK definition',root_changed=False,mesh_rig_rest_weights_corrective_changed=False))
