from stage_common import *
from left_chord_motion import *
A=np.load(P/'motion.npz');E=np.load(P/'evaluated.npz');tl=read(P/'PERFORMANCE_TIMELINE.json');T=E['times'];notes=tl['notes'];rows=[]
co=EventCoordinator(notes,read(P/'GENERATION_POLICY.json'));fit=read(P/'COORDINATED_TRAJECTORY_FIT.json')
for n in notes:
    j=n['finger']-1;idx=np.flatnonzero((T>=n['note_on']-1e-9)&(T<n['note_off']-1e-9));rr=[];ss=[]
    for i in idx:
        rr.append(o.measure(E['L_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]))
        ss.append(o.measure(E['L_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]))
    samples=[]
    for label,t in [('NOTE_ON',n['note_on']),('FULL_DOWN',n['note_on']+.035),('HOLD_MIDDLE',(n['note_on']+n['note_off'])/2),('BEFORE_OFF',n['note_off']-1/120),('NOTE_OFF',n['note_off']),('KEY_RETURN',n['note_off']+.07),('RECOVERY',n['note_off']+.25)]:
        i=int(np.argmin(abs(T-t)));samples.append(dict(phase=label,time=float(T[i]),pressure=float(E['key_angles'][i,n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad']),
            bone_pad=o.measure(E['L_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]),
            skin_pad=o.measure(E['L_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']])))
    rows.append(dict(note=n['note_name'],note_id=n['note_id'],finger=n['finger'],midi=n['midi_note'],key_index=n['key_index'],
        fixed_gap_min_mm=min(r['gap_mm'] for r in rr),fixed_gap_max_mm=max(r['gap_mm'] for r in rr),
        horizontal_max_mm=max(r['horizontal_mm'] for r in rr),skin_gap_min_mm=min(r['gap_mm'] for r in ss),skin_gap_max_mm=max(r['gap_mm'] for r in ss),
        strict_3mm_contact_fail_fraction=sum(not r['pass'] for r in rr)/len(rr),samples=samples))
curve=PchipInterpolator(fit['knots'],fit['solved_states'],axis=0);regular=np.arange(0,read(P/'SCENE_MANIFEST.json')['frames']/60+1/240,1/120)
speed=curve.derivative(1)(regular);acc=curve.derivative(2)(regular);qdeg=np.degrees(A['L_q'])
press=np.stack([E['key_angles'][:,n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad'] for n in notes],axis=1)
samepress=float(np.max(np.max(press,axis=1)-np.min(press,axis=1)));assert samepress<1e-6
phasepress={}
for label,t in [('on',notes[0]['note_on']),('fully_down',notes[0]['note_on']+.035),('off',notes[0]['note_off']),('fully_returned',notes[0]['note_off']+.07)]:
    i=int(np.argmin(abs(T-t)));phasepress[label]=press[i].tolist()
assert max(abs(np.array(phasepress['on'])))<1e-6 and max(abs(np.array(phasepress['fully_down'])-1))<1e-6 and max(abs(np.array(phasepress['fully_returned'])))<1e-6
inactive=list(set(range(88))-set(n['key_index'] for n in notes));assert np.max(abs(E['key_angles'][:,inactive]))==0
model=o.models('L');indices=[]
for j in range(5):
    idx=c.MARKERS['L'][j]['mesh_vertex'];near=np.argsort(np.linalg.norm(model['V']-model['V'][idx],axis=1));indices.extend([int(near[z]) for z in [0,6,12,18]])
palm=np.flatnonzero(model['V'][:,1]<.10);indices.extend(palm[np.linspace(0,len(palm)-1,12).astype(int)].tolist());indices=sorted(set(indices));collision=[]
for label,t in [('on',notes[0]['note_on']),('down',notes[0]['note_on']+.035),('held',notes[0]['note_on']+.4),('off',notes[0]['note_off']),('release',notes[0]['note_off']+.035),('recovered',notes[0]['note_off']+.32)]:
    i=int(np.argmin(abs(T-t)));V=E['L_verts'][i,indices];worst=0;key=None
    for k in c.KEYS:
        if abs(k['key_center'][0]-float(np.mean(V[:,0])))>.20:continue
        vv=o.keytransform(k['midi_note'],V,E['key_angles'][i,k['key_index']],True)
        for g in k['geometry']:
            lo=np.array(g['vertices']).min(0);hi=np.array(g['vertices']).max(0);inside=np.all((vv>lo)&(vv<hi),axis=1)
            if np.any(inside):
                depth=float(np.max(np.min(np.minimum(vv[inside]-lo,hi-vv[inside]),axis=1))*1000)
                if depth>worst:worst=depth;key=k['midi_note']
    collision.append(dict(phase=label,time=float(T[i]),max_sampled_key_penetration_mm=worst,key_midi=key))
# Confirm that EACH active digit really changes during the press, not just an
# audio/key-only chord driven by one finger. Shared wrist contributes as well.
changes=[]
i0=int(np.argmin(abs(T-notes[0]['note_on'])));i1=int(np.argmin(abs(T-(notes[0]['note_on']+.035))))
for n in notes:
    j=n['finger']-1;changes.append(dict(note=n['note_name'],finger=n['finger'],joint_press_change_deg=np.degrees(A['L_q'][i1,j]-A['L_q'][i0,j]),
        pad_press_displacement_mm=(E['L_pads'][i1,j]-E['L_pads'][i0,j])*1000))
dump('ENGINEERING_DIAGNOSTICS.json',dict(triad_contacts=rows,three_distinct_active_fingers=True,shared_root_and_all_joints_jointly_solved=True,
    same_key_pressure_max_difference=samepress,key_phase_pressures=phasepress,other_keys_stationary=True,active_finger_press_changes=changes,
    joint_bound_excess_deg=float(max(np.max(co.bounds[:,0]-qdeg),np.max(qdeg-co.bounds[:,1]),0)),
    root_max_speed_mm_sec=float(np.max(np.linalg.norm(speed[:,:3],axis=1))),root_max_accel_mm_sec2=float(np.max(np.linalg.norm(acc[:,:3],axis=1))),
    root_axis_excursion_mm=np.ptp(A['L_delta'],axis=0)*1000,wrist_rotation_max_speed_deg_sec=float(np.max(abs(speed[:,3:6]))),
    joint_max_speed_deg_sec=float(np.max(abs(speed[:,6:]))),joint_max_accel_deg_sec2=float(np.max(abs(acc[:,6:]))),
    planned_curves_C1=True,baked_interpolation='LINEAR 120Hz plus exact phase times; not exact mathematical C1',
    solver_converged=fit['success'],solver_nfev=fit['nfev'],solver_message=fit['message'],
    finite_skin_probe_count=len(indices),skin_probe_collision=collision,maximum_sampled_key_penetration_mm=max(r['max_sampled_key_penetration_mm'] for r in collision),
    strict_3mm_failing_notes=[r['note'] for r in rows if r['horizontal_max_mm']>2 or max(abs(r['fixed_gap_min_mm']),abs(r['fixed_gap_max_mm']))>3],
    major_contact_mismatch_notes=[r['note'] for r in rows if r['horizontal_max_mm']>6 or max(abs(r['skin_gap_min_mm']),abs(r['skin_gap_max_mm']))>8],
    historical_3mm_gate_not_a_Human_visible_veto=True,scope='Finite contact/32-point collision proxy, not exhaustive surface certification or Human naturalness approval.'))
print('TRIAD_DYNAMIC_CONTACT',[(r['note'],r['skin_gap_min_mm'],r['skin_gap_max_mm'],r['horizontal_max_mm']) for r in rows],flush=True)
print('TIMING_DIFF',samepress,'JOINT_SPEED',np.max(abs(speed[:,6:])),'ROOT_SPEED',np.max(np.linalg.norm(speed[:,:3],axis=1)),'SKIN_PROBE_PEN',max(r['max_sampled_key_penetration_mm'] for r in collision),flush=True)
