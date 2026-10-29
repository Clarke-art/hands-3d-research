from pathlib import Path
exec(compile(Path(__file__).with_name('diagnose.py').read_text(encoding='utf8').split('results={};witnesses={}')[0],str(Path(__file__).with_name('diagnose.py')),'exec'))
man,sc,rig,mesh=open_stage(C2)
contacts=[];geom_errors=[]
times=sorted(set([i/60 for i in range(357)]+[float(t) for n in tl['notes'] for t in np.linspace(n['note_on'],n['note_off']-1e-6,9)]))
for t in times:
    settime(sc,t)
    for side in ['R','L']:
        ns=[n for n in tl['notes'] if n['hand']==side and n['note_on']<=t<n['note_off']]
        if not ns:continue
        info=man['mapping'][side];r=bpy.data.objects[info['rig']];m=bpy.data.objects[info['mesh']];V,F=mesh_pose(m)
        for n in ns:
            k=c.KEYS[n['key_index']];angle=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x;mark=c.MARKERS[side][n['finger']-1];point=V[mark['mesh_vertex']]
            marker=<REDACTED_EMAIL>[mark['distal_frame']].matrix@Vector(mark['local_pad_point'])
            obs=[o for o in sc.objects if o.type=='MESH' and not o.hide_render and f"KEY_RENDER_{n['midi_note']:03d}" in o.name]
            near=[]
            for ob in obs:
                v,f=mesh_pose(ob);tree=BVHTree.FromPolygons([Vector(p) for p in v],f,epsilon=0);h=tree.find_nearest(Vector(point));near.append(float(h[3]*1000))
                geom=next(g for g in k['geometry'] if g['name'] in ob.name)
                pv=np.array(k['press_pivot']);gv=(np.array(geom['vertices'])-pv)@c.axisrot(angle,[1,0,0]).T+pv
                geom_errors.append(float(np.max(np.linalg.norm(v-gv,axis=1))*1000))
            contacts.append(dict(video_sec=t,note_id=n['note_id'],hand=side,finger=n['finger'],note=n['note_name'],skin=contact(point,k,angle),marker=contact(np.array(marker),k,angle),actual_key_mesh_nearest_mm=min(near)))
summary=dict(samples=len(contacts),note_ids=sorted(set(r['note_id'] for r in contacts)),max_skin_gap_mm=max(abs(r['skin']['gap_mm']) for r in contacts),max_marker_gap_mm=max(abs(r['marker']['gap_mm']) for r in contacts),max_horizontal_miss_mm=max(r['skin']['horizontal_mm'] for r in contacts),max_actual_key_mesh_nearest_mm=max(r['actual_key_mesh_nearest_mm'] for r in contacts),max_moving_key_mesh_vs_authoritative_table_mm=max(geom_errors),original_timeline_sha256=sha(C1/'PERFORMANCE_TIMELINE.json'),source_audio_sha256=sha(C1/'piano_performance.wav'))
save('ORIGINAL_ACTIVE_CONTACT_RECHECK.json',dict(summary=summary,rows=contacts,scope='Finite all 23 active pad samples, evaluated moving key meshes; no new trajectory'))
print('CONTACT',summary,flush=True)
# No new correction or generated Action. This locks the reference baseline for the gate only.
base=read(C1/'SCENE_MANIFEST.json')
save('BASELINE_LOCK.json',dict(baseline='Stage C R1',path=base['path'],sha256=base['sha256'],reason='Exact inherited Stage A R2 motion. R2 is a diagnostic comparator; its isolated ring spread advances C#5 interference.',new_candidate_count=0,formal_motion_solve_attempts=0))
rs=read(OUT/'R2_BLACK_SUMMARY.json')
index_frames={r['video_sec'] for r in read(OUT/'R2_LOCAL_GEOMETRY.json')['black_hits'] if any(h['digit']=='INDEX' and h['midi']!=78 for h in r['hits'])}
outside={t for t in index_frames if not .8<=t<=2.08}
save('PREGENERATION_FEASIBILITY_GATE.json',dict(status='FAIL_CLOSED',candidate_count=0,formal_local_solve_attempts=0,static_correction_trials=0,baseline_sha256=base['sha256'],source_reference_locked=True,strategies_generated=False,reason='Confirmed visible non-target black-key penetration affects INDEX, MIDDLE and RING across most of the phrase, including immutable outside-window INDEX states. A correction restricted to the middle/ring handoff cannot satisfy the joint product constraints. Longer right-hand coordination needs separate authorization; do not run even one knowingly incomplete candidate.',index_collision_frame_count=len(index_frames),index_collision_sample_duration_sec=len(index_frames)/60,index_collision_frames_outside_existing_local_window=len(outside),full_video_sec=5.95,black_key_pairs=rs,does_not_claim_frozen_rig_intrinsically_infeasible=True,allowed_next_design='Event-based local joint coordination with active pad anchors and actual black-key skin constraints, only after explicit wider temporal/finger scope authorization. No root, frozen asset or music change is proposed.'))
print('PREGENERATION_GATE_FAIL_CLOSED_NO_SOLVE_NO_CANDIDATE',flush=True)
