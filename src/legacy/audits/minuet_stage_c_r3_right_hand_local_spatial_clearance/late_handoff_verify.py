from pathlib import Path
exec(compile(Path(__file__).with_name('diagnose.py').read_text(encoding='utf8').split('results={};witnesses={}')[0],str(Path(__file__).with_name('diagnose.py')),'exec'))
rois=read(OUT/'LOCAL_SKIN_ROI.json');output={};reference={}
for label,folder in [('R1',C1),('R2',C2),('A2',A)]:
    man=read(folder/'SCENE_MANIFEST.json');bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
    info=man['mapping'] if label=='A2' else man['mapping']['R'];rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']];rows=[]
    for i in range(888,939):
        t=i/240;settime(sc,t-(.05 if label=='A2' else 0));V,F=mesh_pose(mesh)
        if label=='R1':reference[i]=V.copy()
        trees=[BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in ['MIDDLE','RING']];pairs=trees[0].overlap(trees[1])
        rows.append(dict(video_sec=t,music_sec=t-.35,triangle_pairs=len(pairs),skin_vs_R1_max_mm=float(np.linalg.norm(V-reference[i],axis=1).max()*1000),phases=[dict(note_id=n['note_id'],finger=n['finger'],note=n['note_name']) for n in tl['notes'] if n['hand']=='R' and n['note_on']<=t<n['note_off']],black_hits=black_relation(V,rois,key_geometry(sc)),face_examples={d:[rois[d]['faces'][p[j]] for p in pairs[:3]] for j,d in enumerate(['MIDDLE','RING'])}))
    output[label]=rows
save('LATE_HANDOFF_240HZ.json',output)
for label,rows in output.items():
    hit=[r for r in rows if r['triangle_pairs']];print(label,'late interval',hit[0]['video_sec'],hit[-1]['video_sec'],'max pairs',max(r['triangle_pairs'] for r in hit),'max skin delta',max(r['skin_vs_R1_max_mm'] for r in rows),flush=True)
