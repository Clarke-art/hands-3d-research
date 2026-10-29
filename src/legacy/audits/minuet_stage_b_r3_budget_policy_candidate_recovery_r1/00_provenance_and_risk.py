from stage_common import *
import shutil,importlib.util
assert not (P/'RECOVERY_ATTEMPT.json').exists()
paths=set(read(G/'PROTECTED_INPUTS_BEFORE.json'));paths.update(str(p) for p in G.rglob('*') if p.is_file())
dump('PROTECTED_INPUTS_BEFORE.json',{path:sha(path) for path in sorted(paths)})
manifest=read(G/'DELIVERY_MANIFEST.json');mismatch=[name for name,h in manifest['files'].items() if sha(G/name)!=h];assert not mismatch
lock=read(G/'GENERATION_LOCK.json');assert all(sha(G/name)==h for name,h in lock['scripts'].items());assert sha(G/'GENERATION_POLICY.json')==lock['policy_sha256']
for name in ['GENERATION_POLICY.json','PERFORMANCE_TIMELINE.json','PAD_PATCHES.json']:
    shutil.copyfile(G/name,P/name)
spec=importlib.util.spec_from_file_location('saved_pipeline',G/'total_angle_pipeline.py');kernel=importlib.util.module_from_spec(spec);spec.loader.exec_module(kernel)
p=kernel.TotalAnglePipeline();returned=read(G/'SOLVER_RETURN_CHECKPOINT.json');guard=read(G/'SOLVER_AND_GUARD_DIAGNOSTICS.json');raw=np.array(returned['raw_unknown_actual_delta_deg']);curve=p.curve(raw)
q=np.array(guard['final_total_q_deg']);delta=np.array(guard['final_actual_delta_deg']);T=p.times
assert np.array_equal(curve(T),q);assert np.array_equal(curve(T)-p.refcurve(T),delta)
assert np.array_equal(np.array(returned['support_total_q_deg']),kernel.total_angles(p.reference_q,p.expand(raw)))
assert sha(R2/'motion.npz')==returned['source_hashes']['R2_motion_sha256']
cert=p.certify(raw);assert cert['domain']['pass_'] and cert['boundary_position_and_velocity_preserved'] and cert['outside_window_max_change_deg']==0
stage=next(s for s in guard['stages'] if s['stage']=='ACTUAL_OUTPUT_CORRECTION_BUDGET');violations=stage['violations'];extrema=cert['actual_delta_budget']['violations'];assert len(violations)==62 and len(extrema)==14
ids=kernel.rec.joint_identities();fullref=kernel.PchipInterpolator(p.knots,p.reference_states,axis=0)

def measure(t,excess):
    st=fullref(float(t))[None,:];st[0,6:]=curve(t);pads,joints=kernel.fk_batch(st);ref=fullref(float(t))[None,:];oldpads=kernel.fk_batch(ref)[0]
    # Conservative angular-arc sensitivity bound. No clipped/corrected counter-
    # trajectory is constructed. Radii are actual pad-to-joint distances.
    bound=np.zeros(5)
    for j,e in excess.items():
        finger=j//4;local=j%4;point=joints[0,finger,0 if local==3 else local]
        radius=float(np.linalg.norm(pads[0,finger]-point)*1000)
        bound[finger]+=radius*abs(e)*np.pi/180
    return dict(time=float(t),simultaneous_excess_angular_arc_bound_mm_by_finger=bound,actual_pad_displacement_from_R2_mm_by_finger=np.linalg.norm(pads[0]-oldpads[0],axis=1)*1000)
bytime={}
for r in violations:bytime.setdefault(r['time_sec'],{})[r['flat_index']]=r['excess_deg']
spatial=[measure(t,e) for t,e in sorted(bytime.items())]
extspatial=[]
for r in extrema:
    t=r['time_sec'];dd=curve(t)-p.refcurve(t);es=np.maximum(abs(dd)-p.budget,0);extspatial.append(measure(t,{j:float(es[j]) for j in np.flatnonzero(es>1e-7)}))
dc=curve.c-p.refcurve.c;intervals=[]
# Exact finite cubic threshold-crossing intervals for all affected scalars.
affected=sorted(set(r['flat_index'] for r in violations)|set(r['flat_index'] for r in extrema))
for j in affected:
    for k,h in enumerate(np.diff(p.knots)):
        cc=dc[:,k,j];points=[0.,float(h)]
        for sign in [-1,1]:
            shifted=cc.copy();shifted[-1]-=sign*(p.budget[j]+1e-7)
            for root in np.roots(shifted):
                if abs(root.imag)<1e-9 and 0<root.real<h:points.append(float(root.real))
        points=sorted(set(points))
        for a,b in zip(points,points[1:]):
            if abs(np.polyval(cc,(a+b)/2))>p.budget[j]+1e-7:
                intervals.append(dict(flat_index=j,**{k:v for k,v in ids[j].items() if k!='flat_index'},start=float(p.knots[k]+a),end=float(p.knots[k]+b),duration_sec=float(b-a)))
merged=[]
for j in affected:
    for r in [x for x in intervals if x['flat_index']==j]:
        if merged and merged[-1]['flat_index']==j and r['start']-merged[-1]['end']<1e-9:
            merged[-1]['end']=r['end'];merged[-1]['duration_sec']=merged[-1]['end']-merged[-1]['start']
        else:merged.append(r.copy())
groups=[]
for j in affected:
    vr=[r for r in violations if r['flat_index']==j];er=[r for r in extrema if r['flat_index']==j]
    peak=max(er,key=lambda r:r['excess_deg']);iv=[r for r in merged if r['flat_index']==j]
    groups.append(dict(**ids[j],sample_violations=len(vr),continuous_extrema_violations=len(er),max_excess_deg=peak['excess_deg'],budget_deg=float(p.budget[j]),max_actual_correction_abs_deg=abs(peak['actual_deg']),max_correction_budget_ratio=abs(peak['actual_deg'])/p.budget[j],total_excess_duration_sec=sum(r['duration_sec'] for r in iv),episodes=iv))
st=np.c_[p.A['L_delta']*1000,p.A['L_extra_rot_deg'],q];refst=np.c_[p.A['L_delta']*1000,p.A['L_extra_rot_deg'],np.degrees(p.A['L_q']).reshape(-1,20)]
pads,joints=kernel.fk_batch(st);oldpads=kernel.fk_batch(refst)[0]
model=o.models('L');patches=read(P/'PAD_PATCHES.json');indices=sorted(set(i for pa in patches for i in pa['vertices']));lookup={v:i for i,v in enumerate(indices)}
caps=kernel.skin_caps_batch(st,model,indices);oldcaps=kernel.skin_caps_batch(refst,model,indices)
skin=np.stack([caps[:,lookup[pa['marker_vertex']]] for pa in patches],axis=1);oldskin=np.stack([oldcaps[:,lookup[pa['marker_vertex']]] for pa in patches],axis=1)
reg=np.arange(0,p.knots[-1]+1/240,1/120);full=fullref(reg);new=full.copy();new[:,6:]=curve(reg);npad=kernel.fk_batch(new)[0];opad=kernel.fk_batch(full)[0]
frames=np.arange(357)/60;fr=fullref(frames);nr=fr.copy();nr[:,6:]=curve(frames);pf=kernel.fk_batch(nr)[0];of=kernel.fk_batch(fr)[0]
qframe=curve(frames);oldframe=p.refcurve(frames);v=curve.derivative()(reg);v0=p.refcurve.derivative()(reg);acc=curve.derivative(2)(reg);acc0=p.refcurve.derivative(2)(reg)
vz=np.unravel_index(np.argmax(abs(v)),v.shape);az=np.unravel_index(np.argmax(abs(acc)),acc.shape)
notes=[]
for i,n in enumerate(p.co.events):
    finger=n['finger']-1;s=p.co.surfaces[i];ix=np.flatnonzero((T>=n['note_on'])&(T<n['note_off']));mins=[];gaps=[]
    for k in ix:
        angle=p.A['key_angles'][k,n['key_index']];cap=o.keytransform(n['midi_note'],caps[k,[lookup[v] for v in patches[finger]['vertices']]],angle,True)*1000;a,b=np.quantile(cap[:,0],[.05,.95]);mins.append(min(a-s['xmin']*1000,s['xmax']*1000-b));gaps.append(o.measure(skin[k,finger],n['midi_note'],angle)['gap_mm'])
    notes.append(dict(note_id=n['note_id'],note=n['note_name'],finger=n['finger'],predicted_finite_pad_min_edge_mm=float(min(mins)),predicted_gap_min_mm=float(min(gaps)),predicted_gap_max_mm=float(max(gaps)),scope='finite frozen LBS prediction; actual Blender readback still required'))
data=dict(saved_source_manifest_verified=True,source_solver_checkpoint_sha256=sha(G/'SOLVER_RETURN_CHECKPOINT.json'),source_guard_checkpoint_sha256=sha(G/'SOLVER_AND_GUARD_DIAGNOSTICS.json'),source_pipeline_sha256=sha(G/'total_angle_pipeline.py'),raw_solver_result_and_output_bitwise_parity=True,source_solver=returned['solver'],original_output_samples=len(T),dofs=20,sample_violation_records=violations,continuous_extrema_records=extrema,groups=groups,unique_violating_times=len(bytime),spatial_bounds_at_all_sample_violations=spatial,spatial_bounds_at_all_continuous_extrema=extspatial,max_simultaneous_excess_arc_bound_mm=float(max(np.max(r['simultaneous_excess_angular_arc_bound_mm_by_finger']) for r in spatial+extspatial)),max_correction_budget_ratio=max(g['max_correction_budget_ratio'] for g in groups),total_q_engineering_domain=cert['domain'],outside_window_change_deg=cert['outside_window_max_change_deg'],C1_position_jump_deg=cert['C1_position_jump_max_deg'],C1_velocity_jump_deg_sec=cert['C1_velocity_jump_max_deg_sec'],window_boundary_parity=cert['boundary_position_and_velocity_preserved'],actual_pad_displacement_from_R2_max_mm_by_finger=np.max(np.linalg.norm(pads-oldpads,axis=-1)*1000,axis=0),predicted_skin_marker_displacement_from_R2_max_mm_by_finger=np.max(np.linalg.norm(skin-oldskin,axis=-1)*1000,axis=0),new_max_60fps_pad_step_mm_by_finger=np.max(np.linalg.norm(np.diff(pf,axis=0),axis=-1)*1000,axis=0),R2_max_60fps_pad_step_mm_by_finger=np.max(np.linalg.norm(np.diff(of,axis=0),axis=-1)*1000,axis=0),max_60fps_added_pad_step_mm_by_finger=np.max(np.linalg.norm(np.diff(pf-of,axis=0),axis=-1)*1000,axis=0),new_max_60fps_joint_step_deg_by_dof=np.max(abs(np.diff(qframe,axis=0)),axis=0),R2_max_60fps_joint_step_deg_by_dof=np.max(abs(np.diff(oldframe,axis=0)),axis=0),new_peak_speed=dict(time=float(reg[vz[0]]),flat_index=int(vz[1]),value_deg_sec=float(v[vz])),new_peak_acceleration=dict(time=float(reg[az[0]]),flat_index=int(az[1]),value_deg_sec2=float(acc[az])),R2_max_speed_deg_sec=float(np.max(abs(v0))),new_max_speed_deg_sec=float(np.max(abs(v))),R2_max_accel_deg_sec2=float(np.max(abs(acc0))),new_max_accel_deg_sec2=float(np.max(abs(acc))),predicted_active_notes=notes,pad_bound_method='sum(current pad-to-joint radius * abs(budget excess) radians), per finger; no angle clipping or changed candidate',NEW_SOLVER_CALLS=0,Blender_candidate_created=False)
dump('PROVENANCE_AND_RISK_DATA.json',data)
print('PROVENANCE_PASS',len(T),'samples',len(raw),'original unknowns',flush=True)
print('BUDGET_GROUPS',[(g['digit'],g['joint'],g['sample_violations'],g['max_excess_deg'],g['total_excess_duration_sec']) for g in groups],flush=True)
print('MAX_EXCESS_ARC_MM',data['max_simultaneous_excess_arc_bound_mm'],'RATIO',data['max_correction_budget_ratio'],flush=True)
print('FRAME_PAD_STEPS',data['R2_max_60fps_pad_step_mm_by_finger'],data['new_max_60fps_pad_step_mm_by_finger'],'ADDED',data['max_60fps_added_pad_step_mm_by_finger'],flush=True)
print('PEAKS',data['new_peak_speed'],data['new_peak_acceleration'],flush=True)
print('PREDICTED_CONTACTS',notes,flush=True)
