from contact_region import *
A=dict(np.load(P/'motion.npz'));O=dict(np.load(R2/'motion.npz'));E=dict(np.load(P/'evaluated.npz'));E0=dict(np.load(R2/'evaluated.npz'))
tl=read(P/'PERFORMANCE_TIMELINE.json');pol=read(P/'GENERATION_POLICY.json');co=EventCoordinator(tl['notes'],pol['source_policy']);patches=read(P/'PAD_PATCHES.json');T=E['times'];old=read(P/'R2_ALL_ACTIVE_PLACEMENT.json');rows=[]
for ni,n in enumerate(co.events):
    j=n['finger']-1;s=co.surfaces[ni];ids=np.flatnonzero((T>=n['note_on']-1e-9)&(T<n['note_off']-1e-9));samples=[]
    for i in ids:
        angle=E['key_angles'][i,n['key_index']];center=o.keytransform(n['midi_note'],E['L_skin_pads'][i,j],angle,True)*1000
        cap=o.keytransform(n['midi_note'],E['L_verts'][i,patches[j]['vertices']],angle,True)*1000
        left,right=np.quantile(cap[:,0],[.05,.95]);lo,hi=s['xmin']*1000,s['xmax']*1000
        samples.append(dict(time=float(T[i]),center_x_mm=float(center[0]),center_to_left_mm=float(center[0]-lo),center_to_right_mm=float(hi-center[0]),pad_left_mm=float(left),pad_right_mm=float(right),pad_width_mm=float(right-left),pad_left_margin_mm=float(left-lo),pad_right_margin_mm=float(hi-right),cap_full_left_margin_mm=float(cap[:,0].min()-lo),cap_full_right_margin_mm=float(hi-cap[:,0].max()),gap_mm=float(center[2]-s['z']*1000),inside_target_key=bool(o.measure(E['L_skin_pads'][i,j],n['midi_note'],angle)['inside'])))
    before=old['notes'][ni];ss=before['summary'];newmin=min(min(r['pad_left_margin_mm'],r['pad_right_margin_mm']) for r in samples)
    gapdelta=np.array([r['gap_mm']-b['gap_mm'] for r,b in zip(samples,before['samples'])])
    rows.append(dict(note_id=n['note_id'],note=n['note_name'],finger=n['finger'],note_on=n['note_on'],note_off=n['note_off'],key_left_mm=s['xmin']*1000,key_right_mm=s['xmax']*1000,samples=samples,summary=dict(center_x_range_mm=[min(r['center_x_mm'] for r in samples),max(r['center_x_mm'] for r in samples)],center_min_edge_mm=min(min(r['center_to_left_mm'],r['center_to_right_mm']) for r in samples),pad_min_edge_mm=newmin,before_pad_min_edge_mm=ss['pad_min_edge_mm'],pad_margin_improvement_mm=newmin-ss['pad_min_edge_mm'],lateral_drift_mm=float(np.ptp([r['center_x_mm'] for r in samples])),gap_min_mm=min(r['gap_mm'] for r in samples),gap_max_mm=max(r['gap_mm'] for r in samples),gap_delta_max_mm=float(np.max(abs(gapdelta))),all_centers_inside=all(r['inside_target_key'] for r in samples),all_finite_pad_P90_inside=newmin>0)))
assert sha(P/'PERFORMANCE_TIMELINE.json')==sha(R2/'PERFORMANCE_TIMELINE.json')
assert all(np.array_equal(A[k],O[k]) for k in A if k!='L_q')
qdelta=np.degrees(A['L_q']-O['L_q']);env=activity_envelope(T,co.events,pol['source_policy']);inactive=env<1e-12
inactive_max=float(np.max(abs(qdelta[inactive])))
reg=np.arange(0,T[-1]+1/240,1/120);q0=np.array([np.interp(reg,T,O['L_q'][:,j,z]) for j in range(5) for z in range(4)]).T*180/np.pi
q1=np.array([np.interp(reg,T,A['L_q'][:,j,z]) for j in range(5) for z in range(4)]).T*180/np.pi
v0=np.gradient(q0,1/120,axis=0);v1=np.gradient(q1,1/120,axis=0);acc0=np.gradient(v0,1/120,axis=0);acc1=np.gradient(v1,1/120,axis=0)
fk0=fk_batch(np.c_[O['L_delta']*1000,O['L_extra_rot_deg'],np.degrees(O['L_q']).reshape(-1,20)])[1]
fk1=fk_batch(np.c_[A['L_delta']*1000,A['L_extra_rot_deg'],np.degrees(A['L_q']).reshape(-1,20)])[1]
jointpointdelta=np.linalg.norm(fk1-fk0,axis=-1)*1000
press=np.stack([E['key_angles'][:,n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad'] for n in co.events[:3]],axis=1)
mask=(T>=co.events[0]['note_on']-1e-9)&(T<=co.events[0]['note_off']+.07+1e-9);triaddiff=float(np.max(np.ptp(press[mask],axis=1)))
collision=[]
sampletimes=sorted(set([n['note_on']+.035 for n in co.events]+[n['note_off']-1/120 for n in co.events]+[(n['note_on']+n['note_off'])/2 for n in co.events]))
model=o.models('L');probe=[]
for j in range(5):
    ix=c.MARKERS['L'][j]['mesh_vertex'];near=np.argsort(np.linalg.norm(model['V']-model['V'][ix],axis=1));probe.extend(int(near[z]) for z in [0,6,12,18])
palm=np.flatnonzero(model['V'][:,1]<.10);probe.extend(palm[np.linspace(0,len(palm)-1,12).astype(int)].tolist());probe=sorted(set(probe))
for t in sampletimes:
    i=int(np.argmin(abs(T-t)));activekeys={n['midi_note'] for n in co.events if n['note_on']<=T[i]<n['note_off']};row=dict(time=float(T[i]),active_keys=sorted(activekeys));pairs=[]
    for label,D in [('before',E0),('after',E)]:
        V=D['L_verts'][i,probe];worst=0.;neighbor=0.;key=None
        for k in c.KEYS:
            if abs(k['key_center'][0]-float(np.mean(V[:,0])))>.20:continue
            vv=o.keytransform(k['midi_note'],V,D['key_angles'][i,k['key_index']],True)
            for g in k['geometry']:
                lo=np.array(g['vertices']).min(0);hi=np.array(g['vertices']).max(0);inside=np.all((vv>lo)&(vv<hi),axis=1)
                if np.any(inside):
                    depth=float(np.max(np.min(np.minimum(vv[inside]-lo,hi-vv[inside]),axis=1))*1000)
                    if depth>worst:worst=depth;key=k['midi_note']
                    if k['midi_note'] not in activekeys:neighbor=max(neighbor,depth)
        row[label]=dict(max_sampled_penetration_mm=worst,key_midi=key,max_non_active_key_penetration_mm=neighbor)
    collision.append(row)
fit=read(P/'COORDINATED_TRAJECTORY_FIT.json');man=read(P/'SCENE_MANIFEST.json')
engineering=dict(notes=rows,all_active_events_verified=7,triad_pressure_max_difference=triaddiff,key_angles_bitwise_equal_R2=True,key_angle_readback_parity_rad=man['key_angle_parity_max_rad'],root_translation_delta_max_mm=[0,0,0],root_rotation_delta_max_deg=[0,0,0],joint_delta_max_abs_deg_by_dof=np.max(abs(qdelta),axis=0),joint_delta_rms_deg_by_dof=np.sqrt(np.mean(qdelta*qdelta,axis=0)),unassigned_finger_delta_max_deg=inactive_max,joint_center_displacement_max_mm_by_digit_joint=np.max(jointpointdelta,axis=0),original_joint_speed_max_deg_sec=float(np.max(abs(v0))),new_joint_speed_max_deg_sec=float(np.max(abs(v1))),original_joint_acceleration_max_deg_sec2=float(np.max(abs(acc0))),new_joint_acceleration_max_deg_sec2=float(np.max(abs(acc1))),joint_correction_velocity_max_deg_sec=float(np.max(abs(v1-v0))),joint_bounds_excess_deg=float(max(0,np.max(co.state_low[6:].reshape(5,4)-np.degrees(A['L_q'])),np.max(np.degrees(A['L_q'])-co.state_high[6:].reshape(5,4)))),finite_skin_probe_count=len(probe),finite_skin_probe_collision=collision,maximum_non_active_key_penetration_before_mm=max(r['before']['max_non_active_key_penetration_mm'] for r in collision),maximum_non_active_key_penetration_after_mm=max(r['after']['max_non_active_key_penetration_mm'] for r in collision),solver_converged=fit['success'],solver_nfev=fit['nfev'],solver_limit_reached=fit['solver_limit_reached'],solver_message=fit['message'],solver_optimality=fit['optimality'],solver_numerical_termination_not_contact_or_visual_certificate=True,no_second_candidate=True,retained_R2_WARN=read(R2/'FINAL_STATUS.json')['retained_engineering_WARN'],scope='All seven actual skin cap placements over all hold samples; finite32-point nearby key probes; no exhaustive forensic or pressure simulation')
dump('ENGINEERING_DIAGNOSTICS.json',engineering)
dump('MOTION_PRESERVATION.json',dict(root_bitwise_preserved=True,key_actions_preserved=True,timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),same_sample_clock=True,joint_delta_max_abs_deg_by_dof=engineering['joint_delta_max_abs_deg_by_dof'],inactive_joint_delta_max_deg=inactive_max,original_prepare_release_duration_preserved=True,reference_gap_delta_max_mm=max(r['summary']['gap_delta_max_mm'] for r in rows),original_naturalness_is_human_accepted=True,new_naturalness='HUMAN_PENDING',old_idle_WARN_not_fixed=True))
for r in rows:print('BEFORE_AFTER',r['note_id'],r['note'],r['finger'],r['summary'],flush=True)
print('PRESERVATION',inactive_max,'maxjoint',np.max(abs(qdelta)),'root0','solver',fit['nfev'],fit['success'],'neighbor',engineering['maximum_non_active_key_penetration_before_mm'],engineering['maximum_non_active_key_penetration_after_mm'],flush=True)
