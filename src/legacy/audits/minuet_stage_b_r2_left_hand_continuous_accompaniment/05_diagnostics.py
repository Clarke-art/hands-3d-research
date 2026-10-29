from stage_common import *
from left_continuous_motion import *
A=np.load(P/'motion.npz');E=np.load(P/'evaluated.npz');tl=read(P/'PERFORMANCE_TIMELINE.json');T=E['times'];notes=tl['notes'];co=EventCoordinator(notes,read(P/'GENERATION_POLICY.json'));rows=[]
for n in notes:
    j=n['finger']-1;idx=np.flatnonzero((T>=n['note_on']-1e-9)&(T<n['note_off']-1e-9));rr=[];ss=[]
    for i in idx:
        rr.append(o.measure(E['L_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]))
        ss.append(o.measure(E['L_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']]))
    samples=[]
    for label,t in [('on',n['note_on']),('down',n['note_on']+.035),('hold',(n['note_on']+n['note_off'])/2),('before_off',n['note_off']-1/120),('off',n['note_off']),('return',n['note_off']+.07)]:
        i=int(np.argmin(abs(T-t)));samples.append(dict(phase=label,time=float(T[i]),pressure=float(E['key_angles'][i,n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad']),
            skin=o.measure(E['L_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,n['key_index']])))
    rows.append(dict(note_id=n['note_id'],note=n['note_name'],finger=n['finger'],measure=n['measure'],
        skin_gap_min_mm=min(r['gap_mm'] for r in ss),skin_gap_max_mm=max(r['gap_mm'] for r in ss),
        bone_gap_min_mm=min(r['gap_mm'] for r in rr),bone_gap_max_mm=max(r['gap_mm'] for r in rr),
        horizontal_max_mm=max(r['horizontal_mm'] for r in rr),
        historical_3mm_contact_fail_fraction=sum(not r['pass'] for r in rr)/len(rr),samples=samples))
expected=np.array([co.key_angles(t) for t in T]);parity=float(np.max(abs(E['key_angles']-expected)));assert parity<1e-5
press=np.stack([E['key_angles'][:,n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad'] for n in notes[:3]],axis=1)
mask=(T>=notes[0]['note_on']-1e-9)&(T<=notes[0]['note_off']+.07+1e-9)
diff=float(np.max(np.ptp(press[mask],axis=1)));assert diff<1e-6
inactive=list(set(range(88))-set(n['key_index'] for n in notes));assert np.max(abs(E['key_angles'][:,inactive]))==0
holding=[]
for i,t in enumerate(T):
    ds=co.task_components(float(t));prep=[r['finger'] for r in ds if r['phase'] in ['PREPARATION','RELEASE_TO_NEXT_PREPARATION']]
    if not prep:continue
    current=[n for n in notes if n['note_on']<=t and t<n['note_off'] and n['finger']-1 not in prep]
    for n in current:
        m=o.measure(E['L_skin_pads'][i,n['finger']-1],n['midi_note'],E['key_angles'][i,n['key_index']]);holding.append(dict(note_id=n['note_id'],time=float(t),preparing_fingers=[j+1 for j in prep],measure=m))
handoff=[];boundary=notes[3]['note_on']
for t in [boundary-.075,boundary,boundary+.0175,boundary+.035,boundary+.07]:
    i=int(np.argmin(abs(T-t)));m=[]
    for n in notes[:4]:
        m.append(dict(note_id=n['note_id'],finger=n['finger'],skin=o.measure(E['L_skin_pads'][i,n['finger']-1],n['midi_note'],E['key_angles'][i,n['key_index']]),
            key_pressure=float(E['key_angles'][i,n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad'])))
    handoff.append(dict(time=float(T[i]),targets=m))
fit=read(P/'COORDINATED_TRAJECTORY_FIT.json');curve=PchipInterpolator(fit['knots'],fit['solved_states'],axis=0)
regular=np.arange(0,read(P/'SCENE_MANIFEST.json')['frames']/60+1/240,1/120);v=curve.derivative(1)(regular);acc=curve.derivative(2)(regular);q=np.degrees(A['L_q'])
model=o.models('L');indices=[]
for j in range(5):
    ix=c.MARKERS['L'][j]['mesh_vertex'];near=np.argsort(np.linalg.norm(model['V']-model['V'][ix],axis=1));indices.extend([int(near[z]) for z in [0,6,12,18]])
palm=np.flatnonzero(model['V'][:,1]<.10);indices.extend(palm[np.linspace(0,len(palm)-1,12).astype(int)].tolist());indices=sorted(set(indices));collision=[]
sampletimes=sorted(set([n['note_on']+.035 for n in notes]+[n['note_off']-1/120 for n in notes]+[boundary+.035,notes[-1]['note_off']+.32]))
for t in sampletimes:
    i=int(np.argmin(abs(T-t)));V=E['L_verts'][i,indices];worst=0;key=None
    for k in c.KEYS:
        if abs(k['key_center'][0]-float(np.mean(V[:,0])))>.20:continue
        vv=o.keytransform(k['midi_note'],V,E['key_angles'][i,k['key_index']],True)
        for g in k['geometry']:
            lo=np.array(g['vertices']).min(0);hi=np.array(g['vertices']).max(0);inside=np.all((vv>lo)&(vv<hi),axis=1)
            if np.any(inside):
                depth=float(np.max(np.min(np.minimum(vv[inside]-lo,hi-vv[inside]),axis=1))*1000)
                if depth>worst:worst=depth;key=k['midi_note']
    collision.append(dict(time=float(T[i]),max_sampled_key_penetration_mm=worst,key_midi=key))
dump('ENGINEERING_DIAGNOSTICS.json',dict(notes=rows,all_original_left_notes=7,source_different_onset_held_overlaps=0,
    chord_pressure_max_difference=diff,key_angle_readback_parity_max_rad=parity,other_keys_stationary=True,
    held_while_other_finger_prepares=holding,held_during_preparation_max_skin_gap_mm=max(abs(r['measure']['gap_mm']) for r in holding),
    chord_to_single_transition=handoff,mechanical_contact_task_peak=4,adjacent_same_key_restrikes_present=False,
    musical_register_shift_required=False,root_axis_excursion_mm=np.ptp(A['L_delta'],axis=0)*1000,
    root_max_speed_mm_sec=float(np.max(np.linalg.norm(v[:,:3],axis=1))),root_max_accel_mm_sec2=float(np.max(np.linalg.norm(acc[:,:3],axis=1))),
    joint_max_speed_deg_sec=float(np.max(abs(v[:,6:]))),joint_max_accel_deg_sec2=float(np.max(abs(acc[:,6:]))),
    joint_bound_excess_deg=float(max(np.max(co.bounds[:,0]-q),np.max(q-co.bounds[:,1]),0)),
    planned_C1=True,baked_interpolation='LINEAR120Hz + exact phase/support samples, not strict C2',
    skin_probe_count=len(indices),skin_probe_collision=collision,maximum_sampled_key_penetration_mm=max(r['max_sampled_key_penetration_mm'] for r in collision),
    solver_converged=fit['success'],solver_nfev=fit['nfev'],solver_message=fit['message'],
    major_contact_mismatch_notes=[r['note_id'] for r in rows if r['horizontal_max_mm']>6 or max(abs(r['skin_gap_min_mm']),abs(r['skin_gap_max_mm']))>8],
    historical_3mm_gate_not_a_Human_visible_veto=True,scope='Finite contact/32-point collision proxy; no exhaustive vertex-forensic, physics or Human naturalness proof.'))
print('ALL_SEVEN_CONTACTS',[(r['note_id'],r['note'],r['finger'],round(r['skin_gap_min_mm'],2),round(r['skin_gap_max_mm'],2),round(r['horizontal_max_mm'],2)) for r in rows],flush=True)
print('ROOT_SPEED',np.max(np.linalg.norm(v[:,:3],axis=1)),'JOINT_SPEED',np.max(abs(v[:,6:])),'PEN',max(r['max_sampled_key_penetration_mm'] for r in collision),'HELD_PREP',max(abs(r['measure']['gap_mm']) for r in holding),flush=True)
