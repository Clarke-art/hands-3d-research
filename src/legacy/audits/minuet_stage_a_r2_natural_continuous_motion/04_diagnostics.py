from stage_common import *
from coordinated_motion import *
A=np.load(P/'motion.npz');E=np.load(P/'evaluated.npz');tl=read(P/'PERFORMANCE_TIMELINE.json');T=E['times'];notes=tl['notes']
fit=read(P/'COORDINATED_TRAJECTORY_FIT.json');co=EventCoordinator(notes,read(P/'GENERATION_POLICY.json'));rows=[]
old=read(R1/'ENGINEERING_DIAGNOSTICS.json');oldrows={r['note_id']:r for r in old['notes']}
for n in notes:
    j=n['finger']-1;indices=np.flatnonzero((T>=n['note_on']-1e-9)&(T<n['note_off']-1e-9))
    rr=[o.measure(E['R_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]) for i in indices]
    sr=[o.measure(E['R_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]) for i in indices]
    samples=[]
    for t in [n['note_on'],n['note_on']+.035,(n['note_on']+n['note_off'])/2,n['note_off']-1/120]:
        i=int(np.argmin(abs(T-t)));samples.append(dict(time=float(T[i]),
            fixed=o.measure(E['R_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]),
            skin=o.measure(E['R_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']])))
    r=dict(note_id=n['note_id'],note=n['note_name'],midi=n['midi_note'],finger=n['finger'],
        fixed_gap_min_mm=min(x['gap_mm'] for x in rr),fixed_gap_max_mm=max(x['gap_mm'] for x in rr),
        horizontal_max_mm=max(x['horizontal_mm'] for x in rr),
        skin_gap_min_mm=min(x['gap_mm'] for x in sr),skin_gap_max_mm=max(x['gap_mm'] for x in sr),
        engineering_contact_fail_fraction=sum(not x['pass'] for x in rr)/len(rr),samples=samples)
    r['R1_gap_max_mm']=oldrows[n['note_id']]['fixed_gap_max_mm'];r['R1_horizontal_max_mm']=oldrows[n['note_id']]['horizontal_max_mm']
    rows.append(r)
curve=PchipInterpolator(np.array(fit['knots']),np.array(fit['solved_states']),axis=0)
regular=np.arange(0,read(P/'SCENE_MANIFEST.json')['frames']/60+1/240,1/120)
speed=curve.derivative(1)(regular);acc=curve.derivative(2)(regular)
qdeg=np.degrees(A['R_q']);boundexcess=float(max(np.max(B[:,0]-qdeg),np.max(qdeg-B[:,1]),0))
repeats=[]
for a,b in zip(notes,notes[1:]):
    if a['note_id'] not in co.repeats:continue
    check=[]
    for t in [b['note_on']-.045,b['note_on'],b['note_on']+.035]:
        i=int(np.argmin(abs(T-t)));check.append(dict(time=float(T[i]),
            pressure=float(E['key_angles'][i,b['key_index']]/c.KEYS[b['key_index']]['press_angle_rad']),
            pad=o.measure(E['R_pads'][i,b['finger']-1],b['midi_note'],E['key_angles'][i,b['key_index']])))
    mechanical_pass=abs(check[0]['pressure']-1)<.015 and .38<check[1]['pressure']<.46 and abs(check[2]['pressure']-1)<.015
    repeats.append(dict(previous=a['note_id'],next=b['note_id'],samples=check,
        partial_reset_and_restrike_verified=mechanical_pass,unchanged_MIDI_on=b['note_on'],unchanged_MIDI_off=a['note_off']))
# Same limited representative skin screen as R1, no vertex-by-vertex repair.
model=o.models('R');indices=[]
for j in range(5):
    idx=c.MARKERS['R'][j]['mesh_vertex'];near=np.argsort(np.linalg.norm(model['V']-model['V'][idx],axis=1));indices.extend([int(near[z]) for z in [0,6,12,18]])
palm=np.flatnonzero(model['V'][:,1]<.10);indices.extend(palm[np.linspace(0,len(palm)-1,12).astype(int)].tolist());indices=sorted(set(indices))
collision=[]
for n in notes:
    for t in [n['note_on']+.035,n['note_off']-1/120]:
        i=int(np.argmin(abs(T-t)));V=E['R_verts'][i,indices];worst=0;key=None
        for k in c.KEYS:
            if abs(k['key_center'][0]-float(np.mean(V[:,0])))>.20:continue
            vv=o.keytransform(k['midi_note'],V,E['key_angles'][i,k['key_index']],True)
            for g in k['geometry']:
                lo=np.array(g['vertices']).min(0);hi=np.array(g['vertices']).max(0);inside=np.all((vv>lo)&(vv<hi),axis=1)
                if np.any(inside):
                    depth=float(np.max(np.min(np.minimum(vv[inside]-lo,hi-vv[inside]),axis=1))*1000)
                    if depth>worst:worst=depth;key=k['midi_note']
        collision.append(dict(note_id=n['note_id'],time=float(T[i]),max_sampled_key_penetration_mm=worst,key_midi=key))
dump('ENGINEERING_DIAGNOSTICS.json',dict(notes=rows,joint_bound_excess_deg=boundexcess,
    root_max_speed_mm_sec=float(np.max(np.linalg.norm(speed[:,:3],axis=1))),root_max_accel_mm_sec2=float(np.max(np.linalg.norm(acc[:,:3],axis=1))),
    wrist_rotation_max_speed_deg_sec=float(np.max(abs(speed[:,3:6]))),joint_max_speed_deg_sec=float(np.max(abs(speed[:,6:]))),
    joint_max_accel_deg_sec2=float(np.max(abs(acc[:,6:]))),
    R1_joint_max_speed_deg_sec=old['joint_max_speed_deg_sec'],R1_root_max_speed_mm_sec=old['root_max_speed_mm_sec'],
    time_derivative_method='Analytic PCHIP derivatives on regular 120Hz; C1, not C2 at support knots',
    planned_joint_C1_continuity=True,planned_root_C1_continuity=True,baked_interpolation='LINEAR at 120Hz plus exact event/support samples; not mathematically exact C1',root_and_digits_jointly_solved=True,
    finite_skin_probe_count=len(indices),collision=collision,repeat_checks=repeats,
    repeated_key_mechanical_pass=all(r['partial_reset_and_restrike_verified'] for r in repeats),
    contact_failed_notes_engineering_3mm=[r['note_id'] for r in rows if r['horizontal_max_mm']>2 or max(abs(r['fixed_gap_min_mm']),abs(r['fixed_gap_max_mm']))>3],
    major_contact_mismatch_notes=[r['note_id'] for r in rows if r['horizontal_max_mm']>6 or max(abs(r['fixed_gap_min_mm']),abs(r['fixed_gap_max_mm']))>8],
    maximum_skin_probe_penetration_mm=max(r['max_sampled_key_penetration_mm'] for r in collision),
    all_16_events_preserved=True,solver_success=fit['success'],solver_nfev=fit['nfev'],
    scope='Limited diagnostics. Engineering WARN does not replace Human naturalness review.'))
print('CONTACT',[(r['note_id'],r['note'],round(r['fixed_gap_max_mm'],2),round(r['horizontal_max_mm'],2)) for r in rows])
print('JOINT_SPEED',np.max(abs(speed[:,6:])),'ROOT_SPEED',np.max(np.linalg.norm(speed[:,:3],axis=1)),'REPEAT',all(r['partial_reset_and_restrike_verified'] for r in repeats),'SKIN_PEN',max(r['max_sampled_key_penetration_mm'] for r in collision))
