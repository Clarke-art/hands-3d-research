import sys
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];C2=ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'
sys.path.insert(0,str(C2))
from blender_local import *
P=OUT
def save(n,v):
    (OUT/n).write_text(json.dumps(v,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()),encoding='utf8')
tl=read(C1/'PERFORMANCE_TIMELINE.json')
def open_stage(folder):
    man=read(folder/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
    bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
    info=man['mapping']['R'];rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']]
    return man,sc,rig,mesh
def key_geometry(sc):
    keys={}
    for k in c.KEYS:
        if k['color']!='BLACK' or not 66<=k['midi_note']<=80:continue
        obs=[ob for ob in sc.objects if ob.type=='MESH' and not ob.hide_render and f"KEY_RENDER_{k['midi_note']:03d}" in ob.name]
        assert len(obs)==1,(k['midi_note'],[o.name for o in obs])
        ob=obs[0];V,F=mesh_pose(ob);center=V.mean(axis=0);planes=[]
        for f in F:
            p=V[f];n=np.cross(p[1]-p[0],p[2]-p[0]);norm=np.linalg.norm(n)
            if norm<1e-12:continue
            n/=norm
            if np.dot(n,center-p[0])>0:n=-n
            planes.append([*n,np.dot(n,p[0])])
        keys[k['midi_note']]=dict(name=k['note_name'],object=ob.name,V=V,F=F,planes=np.array(planes),tree=BVHTree.FromPolygons([Vector(v) for v in V],F,epsilon=0),lo=V.min(axis=0),hi=V.max(axis=0),matrix=np.array(ob.matrix_world))
    return keys
def black_relation(V,rois,keys):
    rows=[]
    for d,roi in rois.items():
        ids=np.array(roi['vertices']);pts=V[ids];lo=pts.min(axis=0);hi=pts.max(axis=0);tree=None
        for midi,k in keys.items():
            if np.any(hi<k['lo']) or np.any(lo>k['hi']):continue
            if tree is None:tree=BVHTree.FromPolygons([Vector(v) for v in V],roi['faces'],epsilon=0)
            pairs=tree.overlap(k['tree'])
            signed=pts@k['planes'][:,:3].T-k['planes'][:,3];depth=-signed.max(axis=1)*1000
            inside=np.flatnonzero(depth>.02)
            if not pairs and not len(inside):continue
            j=int(np.argmax(depth));vid=int(ids[j]);near=k['tree'].find_nearest(Vector(pts[j]))
            rows.append(dict(digit=d,midi=midi,note=k['name'],triangle_pairs=len(pairs),inside_vertices=len(inside),deepest_vertex=vid,depth_mm=max(0,float(depth[j])),nearest_actual_surface_mm=float(near[3]*1000),point_world_m=pts[j].tolist(),key_object=k['object'],key_surface_point_world_m=list(near[0]),patch_face_examples=[roi['faces'][pair[0]] for pair in pairs[:3]]))
    return rows
results={};witnesses={}
for label,folder in [('R1',C1),('R2',C2)]:
    man,sc,rig,mesh=open_stage(folder);settime(sc,0)
    # Four visibly adjacent distal fingers only. Thumb has no black-key adjacency in full-sequence video sheets.
    rois={d:finger_roi(mesh,rig,d) for d in ['INDEX','MIDDLE','RING','LITTLE']};keys=key_geometry(sc)
    rows=[];overlap=[]
    for frame in range(357):
        t=frame/60;settime(sc,t);V,F=mesh_pose(mesh)
        # Black F#5 actually moves. Re-evaluate these few key surfaces at the current shared clock.
        dynamic=key_geometry(sc)
        hits=black_relation(V,rois,dynamic)
        if hits:rows.append(dict(video_sec=t,music_sec=t-.35,active=[dict(id=n['note_id'],finger=n['finger'],note=n['note_name']) for n in tl['notes'] if n['hand']=='R' and n['note_on']<=t<n['note_off']],hits=hits))
        r=local_relation(V,rois,bpy.data.objects[man['cameras']['OVERHEAD']]);overlap.append(dict(video_sec=t,**r))
        for hit in hits:
            key=(hit['digit'],hit['midi'])
            if key not in witnesses or hit['depth_mm']>witnesses[key]['depth_mm']:
                witnesses[key]=dict(stage=label,video_sec=t,**hit)
        if frame%90==0:print('FINITE_DISTAL_BLACK_CHECK',label,frame,flush=True)
    results[label]=dict(black_hits=rows,middle_ring=overlap,source_sha256=man['sha256'])
    save(f'{label}_LOCAL_GEOMETRY.json',results[label])
save('LOCAL_SKIN_ROI.json',rois)
save('BLACK_KEY_WITNESSES.json',list(witnesses.values()))
for label,res in results.items():
    summary=[]
    combos=sorted({(h['digit'],h['midi']) for r in res['black_hits'] for h in r['hits']})
    for d,midi in combos:
        hit=[(r['video_sec'],h) for r in res['black_hits'] for h in r['hits'] if h['digit']==d and h['midi']==midi]
        intervals=[]
        for t,h in hit:
            if intervals and t-intervals[-1][1]<.017:intervals[-1][1]=t
            else:intervals.append([t,t])
        summary.append(dict(digit=d,midi=midi,note=hit[0][1]['note'],intervals=intervals,max_depth_mm=max(h['depth_mm'] for t,h in hit),frames=len(hit)))
    print('SUMMARY',label,json.dumps(summary),flush=True)
    save(label+'_BLACK_SUMMARY.json',summary)
print('DIAGNOSIS_FINISHED_NO_CANDIDATE',flush=True)
