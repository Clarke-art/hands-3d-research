import sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R3=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance'
exec(compile((R3/'diagnose.py').read_text(encoding='utf8').split('results={};witnesses={}')[0],str(R3/'diagnose.py'),'exec'))
P=OUT
from mathutils import Quaternion
pre=read(P/'STATIC_PREFLIGHT.json');assert pre['complete']
scope=read(P/'PROPOSED_EVENT_SCOPE.json');man,sc,rig,mesh=open_stage(C1);rois=read(R3/'LOCAL_SKIN_ROI.json');original=rig.animation_data.action
rows=[];sampleids=[0,2,5,6,7,9,11,12]
for i,row in enumerate(pre['poses']):
    t=row['video_sec'];rig.animation_data.action=original;settime(sc,t);saved={b.name:b.rotation_quaternion.copy() for b in rig.pose.bones};baseline=mesh_pose(mesh)[0];rig.animation_data.action=None
    delta=np.array(row['delta_deg']);applied=delta.copy()
    for j,d in enumerate(['INDEX','MIDDLE','RING']):
        if not any(a<=t+1e-8<=b+1e-8 for a,b in scope['windows_video_sec'][d]):applied[j]=0
        names,rels,axes,spread,pad=c.SETUPS['R',d]
        for k,name in enumerate(names):
            value=saved[name]@Quaternion(Vector(axes[k]),math.radians(applied[j,k]))
            if k==0:value=Quaternion(Vector(spread),math.radians(applied[j,3]))@value
            rig.pose.bones[name].rotation_quaternion=value
    bpy.context.view_layer.update();V,F=mesh_pose(mesh)
    pair=[]
    for a,b in [('INDEX','MIDDLE'),('MIDDLE','RING'),('RING','LITTLE')]:
        trees=[BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in [a,b]];overlap=trees[0].overlap(trees[1]);before=[BVHTree.FromPolygons([Vector(v) for v in baseline],rois[d]['faces'],epsilon=0) for d in [a,b]]
        pair.append(dict(digits=[a,b],before_face_pairs=len(before[0].overlap(before[1])),after_face_pairs=len(overlap)))
    keys=key_geometry(sc);hits=black_relation(V,rois,keys);beforeblack=black_relation(baseline,rois,keys)
    contacts=[]
    for n in tl['notes']:
        if n['hand']=='R' and n['note_on']<=t<n['note_off']:
            key=c.KEYS[n['key_index']];angle=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x;j=n['finger']-1
            contacts.append(dict(note_id=n['note_id'],finger=n['finger'],note=n['note_name'],skin=contact(V[c.MARKERS['R'][j]['mesh_vertex']],key,angle)))
    rows.append(dict(video_sec=t,music_sec=t-.35,delta_applied_deg=applied,pairs=pair,black_before=beforeblack,black_after=hits,contacts=contacts))
    print('ACTUAL_STATIC',t,'pair',[(p['digits'],p['before_face_pairs'],p['after_face_pairs']) for p in pair],'black',[(h['digit'],h['note'],round(h['depth_mm'],3)) for h in hits],'contacts',contacts,flush=True)
    if i in sampleids:
        for view,name in man['cameras'].items():
            folder=P/'static_check_frames';folder.mkdir(exist_ok=True);sc.camera=bpy.data.objects[name];sc.render.filepath=str(folder/f'{i:02d}_{view}.png');bpy.ops.render.render(write_still=True)
    rig.animation_data.action=original
save('ACTUAL_STATIC_GEOMETRY.json',dict(kind='Static preflight only; no new Action, keyframes or Blend',poses=rows,formal_dynamic_solve_attempts=0,new_dynamic_candidates=0))
print('STATIC_READBACK_COMPLETE_NO_DYNAMIC_CANDIDATE',flush=True)
