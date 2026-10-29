from path_model import *
assert read(OUT/'PHASE_FUNCTION_GATE.json')['pass_']
g=skin_module();cells=partition_cells(g)
manifest=dict(cells=cells,box_padding_m=.0005,coverage='Every distal ROI face is assigned; every vertex of every assigned face is contained. Bounds are maxima/minima, no percentile shrink.',
    stage_mechanisms=1,envelope_mechanisms=1,curve_schemes=1)
# Select the relative clearance direction using an actual C1 intersection
# witness, then the least translation separating its two local boxes.
original=read(R1/'BASELINE_GEOMETRY.json');peak=max(original['rows'],key=lambda r:r['triangle_pairs']);t=peak['t']
ctx=Context(np.array([t]),manifest);gaps,detail=ctx.envelope(ctx.original)
facea,faceb=peak['face_examples'][0]
ca=next(i for i,c0 in enumerate(cells['MIDDLE']) if facea in c0['faces']);cb=next(i for i,c0 in enumerate(cells['RING']) if faceb in c0['faces'])
pair=ca*4+cb;a,b,axes,axisgaps=detail[pair];ix=int(np.argmax(axisgaps[0]));normal=axes[0,ix]
normal*=1 if (b[0]-a[0])@normal>=0 else -1
distance=max(0,.0007-gaps[0,pair]);manifest.update(witness_time=t,witness_face_pair=[facea,faceb],witness_cells=[ca,cb],
    witness_proxy_gap_mm=float(gaps[0,pair]*1000),witness_normal=normal,witness_displacement_m=normal*distance,
    displacement_length_mm=float(distance*1000),direction='Least separating axis of the local boxes containing the actual intersecting faces, not global upward clearance')
save('ENVELOPE_MANIFEST.json',manifest)
# Same R1 failed static postures; geometry is neither edited nor rescaled.
trial=dict(np.load(R1/'STATIC_ACTUAL_SKIN.npz'));old=read(R1/'STATIC_PREFLIGHT_VERIFIED_RESULT.json')
compare=Context(trial['times'],manifest);rows=[]
for state in ['source','new']:
    V=trial[state][:,compare.ids];gap,_=compare.envelope(V)
    for k,t in enumerate(trial['times']):
        actual=read(R1/'STATIC_ACTUAL_VALIDATION.json')['rows'][k]
        count=actual['source_middle_ring' if state=='source' else 'new_middle_ring']['triangle_pairs']
        rows.append(dict(t=float(t),state=state,actual_skin_pairs=count,new_proxy_gap_mm=float(gap[k].min()*1000),new_proxy_collision=bool(gap[k].min()<0),
            old_proxy_gap_mm=old['rows'][k]['capsule_min_gap_mm'] if state=='new' else None,
            old_proxy_collision=True if state=='new' else None))
save('ENVELOPE_COMPARISON.json',dict(rows=rows,old_radius_m=read(R1/'PLANNER_POLICY_COORDINATE_VERIFIED.json')['capsule_radii_m'],
    new_parts_per_digit=4,contains_entire_faces=True,skin_geometry_changed=False,planning_padding_same_m=.0005,
    limitations='Local convex boxes can still classify separated concave patches as overlapping; samples do not prove all-poses reliability'))
curve=Curve();test=Context(BASE['times'],manifest);targets=curve.targets(test,manifest)
parity=float(np.linalg.norm(test.original-BASE['vertices'][:,test.ids],axis=2).max()*1000)
off=SCOPE['old']['note_off'];follow=POL['finger_release_follow_sec'];gate=release_gate(np.array([off-1e-7,off,off+1e-7]),off,follow,SCOPE['next_for_releasing']['note_on']-.075)
assert np.linalg.norm(gate[1]*manifest['witness_displacement_m'])==0 and parity<.03
zero=curve_certificate(curve,np.zeros(curve.variables));assert zero['domain_pass'] and zero['correction_velocity_pass']
save('CONTINUOUS_TARGET_GATE.json',dict(pass_=True,source_model_max_error_mm=parity,off_extra_jump_mm=float(np.linalg.norm((gate[2]-gate[0])*manifest['witness_displacement_m'])*1000),
    off_extra_offset_mm=0.,off_extra_velocity_mm_sec=0.,window_delta_value_and_derivative_zero=True,
    coefficients=16,internal_event_knots=2,knots=curve.knots,source_certificate=zero,
    displacement_length_mm=manifest['displacement_length_mm'],no_instant_full_clearance_at_off=True))
np.savez_compressed(OUT/'CONTINUOUS_TARGETS.npz',times=BASE['times'],source=test.original[:,test.marker],targets=targets)
save('SOLVER_POLICY.json',dict(candidate_limit=1,path_attempt_limit=1,max_nfev=35,solver_wall_seconds=190,variables=16,
    trust_degrees=[12,18,14,6],contact_vertical_abs_mm=3,contact_horizontal_mm=.03,new_key_depth_threshold_mm=.5,nonregression_tolerance_mm=.02,
    added_joint_velocity_deg_sec=180,decomposition_tolerance_deg=.002,root_freedoms=0,
    method='A2 bounded least_squares / sparse storage, two event-defined free cubic coefficient slices; continuous quintic middle activation',
    parameter_retuning=False,source_model_parity_gate_mm=.03))
print('CONTINUOUS_TARGET_AND_SEGMENT_ENVELOPE_READY',manifest['displacement_length_mm'],'mm',normal.tolist(),'parity',parity,flush=True)
