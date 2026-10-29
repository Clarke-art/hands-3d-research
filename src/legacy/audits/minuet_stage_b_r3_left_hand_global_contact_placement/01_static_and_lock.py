from contact_region import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
audit=read(P/'R2_ALL_ACTIVE_PLACEMENT.json');regions=build_regions(audit)
fit=read(R2/'COORDINATED_TRAJECTORY_FIT.json');knots=np.array(fit['knots']);reference=np.array(fit['solved_states'])
policy=read(R2/'GENERATION_POLICY.json');tl=read(P/'PERFORMANCE_TIMELINE.json');co=EventCoordinator(tl['notes'],policy)
limits,derivation=correction_budget(reference,regions,co.events)
model=o.models('L');patches=read(P/'PAD_PATCHES.json');indices=sorted(set(i for p in patches for i in p['vertices']))
lookup={v:i for i,v in enumerate(indices)};patchix=[[lookup[v] for v in p['vertices']] for p in patches]
markerix=[lookup[p['marker_vertex']] for p in patches]
tests=[]
testtimes=sorted(set([n['note_on']+.04 for n in co.events]+[(n['note_on']+n['note_off'])/2 for n in co.events]))
curve=PchipInterpolator(knots,reference,axis=0)
for t in testtimes:
    ref=curve(t)[None,:];goal,weights=targets_relative_to_reference(co,np.array([t]),ref,regions)
    env=activity_envelope(np.array([t]),co.events,policy)[0];lo=np.maximum(-limits.ravel(),co.state_low[6:]-ref[0,6:]);hi=np.minimum(limits.ravel(),co.state_high[6:]-ref[0,6:])
    def state(x):
        s=ref.copy();s[0,6:]+=x*np.repeat(env,4);return s
    def residual(x):
        pads=fk_batch(state(x))[0];return np.r_[((pads-goal)*1000*weights[:,:,None]).ravel(),x*.045]
    f=least_squares(residual,np.clip(np.zeros(20),lo+1e-8,hi-1e-8),bounds=(lo,hi),max_nfev=100,ftol=1e-7,xtol=1e-7,gtol=1e-7)
    s=state(f.x);caps=skin_caps_batch(s,model,indices)[0];pads=fk_batch(s)[0][0];active=[]
    for ni,n in enumerate(co.events):
        if n['note_on']<=t<n['note_off']:
            j=n['finger']-1;surf=co.surfaces[ni];local=o.keytransform(n['midi_note'],caps[patchix[j]],co.key_angles(t)[n['key_index']],True)*1000
            a,b=np.quantile(local[:,0],[.05,.95]);active.append(dict(note_id=n['note_id'],pad_min_edge_mm=float(min(a-surf['xmin']*1000,surf['xmax']*1000-b)),pad_target_error_mm=float(np.linalg.norm(pads[j]-goal[0,j])*1000)))
    tests.append(dict(time=t,solver_success=bool(f.success),nfev=f.nfev,joint_delta_deg=f.x.reshape(5,4)*env[:,None],active=active))
dump('STATIC_REACHABILITY.json',dict(static_only=True,dynamic_candidates=0,root_fixed=True,regions=regions,joint_budget_derivation=derivation,tests=tests,all_feasible=all(r['pad_min_edge_mm']>0 and r['pad_target_error_mm']<.1*r['pad_min_edge_mm'] for t in tests for r in t['active']),gate='target error < 10% achieved finite pad edge slack; positive pad edge slack'))
for t in tests:print('STATIC',t['time'],t['solver_success'],t['nfev'],t['active'],'max_joint',np.max(abs(t['joint_delta_deg'])),flush=True)
if not all(r['pad_min_edge_mm']>0 and r['pad_target_error_mm']<.1*r['pad_min_edge_mm'] for t in tests for r in t['active']):raise RuntimeError('Static reachability conflicts with R2/root motion preservation; STOP before candidate')
limits=np.minimum(limits,1.2*np.max(np.abs([t['joint_delta_deg'] for t in tests]),axis=0))
dump('GENERATION_POLICY.json',dict(scope='GLOBAL_CONTACT_PLACEMENT_REFINEMENT_ONLY',candidate_limit=1,root_delta_limit_mm=[0,0,0],root_rotation_delta_limit_deg=[0,0,0],reference='R2 saved trajectory',source_policy=policy,regions=regions,joint_delta_limits_deg=limits,correction_envelope='original prepare/recovery intervals; exact zero outside',joint_correction_prior=.045,correction_velocity_weight=.006,correction_acceleration_weight=.00015,pad_edge_penalty_weight=6.,max_nfev=100,edge_slack_fraction=.12,cap_orientation_guard_fraction=.05,balanced_slack_preference=.25,finite_pad_percentiles=[.05,.95],fixed_y_contact_and_reference_gap=True,static_test_count=len(tests),source_timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),reference_motion_sha256=sha(R2/'motion.npz'),reference_fit_sha256=sha(R2/'COORDINATED_TRAJECTORY_FIT.json')))
print('STRATEGY_AND_GEOMETRIC_ENVELOPE_LOCKED_NO_DYNAMIC_CANDIDATE',flush=True)
