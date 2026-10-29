from window_problem import *
rows=[]
for ix in [0,len(T)-1]:
    t=float(T[ix]);V=BASE['vertices'][ix];a=BASE['key_angles'][ix];owned={}
    for e in EVENTS:
        if e['note_on']<=t<e['note_off']+.04:owned.setdefault(e['key_index'],set()).add(DIGITS[e['finger']-1])
    violations=[]
    for key,g,pl in COMPONENTS:
        pv=np.asarray(key['press_pivot']);local=(V-pv)@rot(a[key['key_index']],key['press_axis'])+pv
        depth=np.maximum(0,-np.max(local@pl[:,:3].T-pl[:,3],axis=1)*1000)
        for region,ids in REGIONS.items():
            if region in owned.get(key['key_index'],set()):continue
            if depth[ids].max()>.5:
                vid=int(ids[np.argmax(depth[ids])]);violations.append(dict(region=region,key=key['note_name'],key_index=key['key_index'],component=g['name'],vertex=vid,depth_mm=float(depth[vid]),world_m=V[vid],body_local_m=local[vid],all_plane_slacks_mm=(pl[:,3]-local[vid]@pl[:,:3].T)*1000))
    violations.sort(key=lambda r:-r['depth_mm'])
    rows.append(dict(time=t,phase='ENTRY' if ix==0 else 'EXIT',active=[e['note_id'] for e in EVENTS if e['note_on']<=t<e['note_off']],original_actual_vertex_violations=violations))
test=np.linspace(-1,1,SIZE)
assert np.max(abs(correction(test,[START,END])))==0
assert np.max(abs(correction(test,[START,END],1)))<1e-12
q,w=state(test,[START,END]);assert np.max(abs(q-BASE['q_deg'][[0,-1]]))<1e-10
assert np.max(abs(w-BASE['rig_world'][[0,-1]]))<1e-5
atomic_json('BOUNDARY_CONTRACT_WITNESS.json',dict(rows=rows,original_vertex_gate_mm=.5,all_non_target_regions_gate=True,fixed_endpoint_correction_zero_for_all_parameters=True,basis_endpoint_rows=IDENT([START,END])[:,FREE],basis_endpoint_derivative_rows=IDENT([START,END],nu=1)[:,FREE],free_variables=SIZE,proof='B-spline free basis rows at both endpoints identically zero; joint/root corrections and their first derivatives vanish for every feasible coefficient. Existing non-target actual-skin vertex depth >0.5mm is invariant under this boundary contract.',no_feasible_candidate_within_locked_boundary=any(r['original_actual_vertex_violations'] for r in rows),not_global_rig_infeasibility=True))
atomic_record('BOUNDARY_ACTUAL_WITNESS.npz',dict(times=T[[0,-1]],vertices=BASE['vertices'][[0,-1]],key_angles=BASE['key_angles'][[0,-1]],q_deg=BASE['q_deg'][[0,-1]],rig_world=BASE['rig_world'][[0,-1]],triangles=BASE['triangles']))
protect('PROTECTION_BOUNDARY_AUDIT.json')
for r in rows:print(r['phase'],r['time'],len(r['original_actual_vertex_violations']),r['original_actual_vertex_violations'][:2],flush=True)
