from pathlib import Path
# Load only read-only helper definitions, never execute the full scan twice.
exec(compile(Path(__file__).with_name('diagnose.py').read_text(encoding='utf8').split('results={};witnesses={}')[0],str(Path(__file__).with_name('diagnose.py')),'exec'))
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Quaternion
witness=read(OUT/'BLACK_KEY_WITNESSES.json')
times=sorted(set([w['video_sec'] for w in witness]+[1.133333333333,1.75,1.8,3.4,3.883333333333]))
refs={};report={};screen=[]
for label,folder in [('R1',C1),('R2',C2),('A2',A)]:
    man=read(folder/'SCENE_MANIFEST.json')
    bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
    info=man['mapping'] if label=='A2' else man['mapping']['R'];rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']]
    rois=read(OUT/'LOCAL_SKIN_ROI.json');rows=[]
    for t in times:
        settime(sc,t-(.05 if label=='A2' else 0));V,F=mesh_pose(mesh);keys=key_geometry(sc);hits=black_relation(V,rois,keys)
        basis=np.array([np.array(b.matrix_basis) for b in rig.pose.bones]);root=np.array(bpy.data.objects[info['root']].matrix_world)
        if label=='R1':refs[t]=dict(V=V,basis=basis,root=root)
        parity=dict(skin_max_mm=float(np.linalg.norm(V-refs[t]['V'],axis=1).max()*1000),basis_max=float(abs(basis-refs[t]['basis']).max()),root_max=float(abs(root-refs[t]['root']).max()))
        active=[]
        for n in tl['notes']:
            if n['hand']=='R' and n['note_on']<=t<n['note_off']:
                k=c.KEYS[n['key_index']];angle=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x
                active.append(dict(note_id=n['note_id'],finger=n['finger'],note=n['note_name'],skin=contact(V[c.MARKERS['R'][n['finger']-1]['mesh_vertex']],k,angle)))
        for hit in hits:
            vid=hit['deepest_vertex'];hit['vertex_weights']={mesh.vertex_groups[g.group].name:g.weight for g in mesh.data.vertices[vid].groups if g.weight>.01}
            k=keys[hit['midi']];v=Vector(V[vid]);ray=[]
            for direction in [Vector((1,.17,.13)),Vector((-.13,1,.21)),Vector((.21,.13,1))]:
                direction.normalize();near=k['tree'].ray_cast(v,direction)
                ray.append(dict(hit=near[0] is not None,distance_mm=float(near[3]*1000) if near[0] is not None else None,outward_exit=bool(near[1].dot(direction)>0) if near[1] is not None else None))
            hit['independent_ray_exit_checks']=ray
            hit['black_mesh_convexity_max_error_m']=float((k['V']@k['planes'][:,:3].T-k['planes'][:,3]).max())
            if label in ['R1','R2']:
                for view,name in man['cameras'].items():
                    v=world_to_camera_view(sc,bpy.data.objects[name],Vector(hit['point_world_m']))
                    screen.append(dict(stage=label,video_sec=t,view=view,digit=hit['digit'],note=hit['note'],depth_mm=hit['depth_mm'],pixel=[float(v.x*1280),float((1-v.y)*720)]))
        rows.append(dict(video_sec=t,scene_time_sec=t-(.05 if label=='A2' else 0),source_parity=parity,active=active,black_hits=hits))
    report[label]=rows
save('WITNESS_SOURCE_PARITY_AND_CONTACT.json',report);save('WITNESS_SCREEN_COORDINATES.json',screen)
# Confirm residual using the saved R2 Action at quarter-frame resolution.
man,sc,rig,mesh=open_stage(C2);rois=read(OUT/'LOCAL_SKIN_ROI.json');rows=[]
for t in np.arange(.8,2.10001,1/240):
    settime(sc,float(t));V,F=mesh_pose(mesh)
    trees=[BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in ['MIDDLE','RING']];pairs=trees[0].overlap(trees[1])
    if pairs:
        weights={};faceids={d:sorted({v for pair in pairs for v in rois[d]['faces'][pair[i]]}) for i,d in enumerate(['MIDDLE','RING'])}
        for d,ids in faceids.items():
            weights[d]={name:sum(g.weight for vid in ids for g in mesh.data.vertices[vid].groups if mesh.vertex_groups[g.group].name==name)/len(ids) for name in [d+'_MCP_R',d+'_PIP_R',d+'_DIP_R']}
        rows.append(dict(video_sec=float(t),music_sec=float(t-.35),triangle_pairs=len(pairs),skin_vertices=faceids,mean_skin_weights=weights,skin_world_bounds={d:[V[ids].min(axis=0).tolist(),V[ids].max(axis=0).tolist()] for d,ids in faceids.items()}))
save('R2_RESIDUAL_240HZ.json',dict(samples=rows,step_sec=1/240,search_interval=[.8,2.1]))
print('RESIDUAL',len(rows),rows[0]['video_sec'],rows[-1]['video_sec'],'MAX',max(r['triangle_pairs'] for r in rows),flush=True)
print('A2_PARITY_MAX',max(r['source_parity']['skin_max_mm'] for r in report['A2']),flush=True)
print('WITNESS_VERIFICATION_DONE',flush=True)
