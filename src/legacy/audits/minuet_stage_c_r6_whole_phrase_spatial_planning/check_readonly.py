from whole_phrase_model import *
policy=read(P/'PREFLIGHT_POLICY.json')
t=D['times'];ix=np.unique(np.r_[np.arange(0,len(t),37),0,len(t)-1,np.argmin(abs(t-3.825)),np.flatnonzero(D['shape_values'][:,1]>.01)])
model=Skin(t[ix]);original=model(original=True);recomposed=model(source_angles(t[ix]))
actual=D['actual_skin'][ix]
err=np.linalg.norm(original-actual,axis=-1)*1000
qerr=np.linalg.norm(recomposed-actual,axis=-1)*1000
digit_bones=set()
for digit in c.DIGITS:
    roots={BN[n] for n in c.SETUPS['R',digit][0]}
    for i in range(len(REST)):
        j=i
        while j>=0:
            if j in roots:digit_bones.add(i);break
            j=D['parents'][j]
fixed=np.flatnonzero(W[:,sorted(digit_bones)].sum(1)<1e-12)
components=key_components();hits=[]
for key,g in components:
    depth=body_depth(D['actual_skin'][:,fixed],key,g,D['key_angles'])
    if depth.max()>.5:
        ti,vi=np.unravel_index(depth.argmax(),depth.shape)
        hits.append(dict(time=float(t[ti]),vertex=int(fixed[vi]),key=key['note_name'],component=g['name'],depth_mm=float(depth[ti,vi])))
vel=np.diff(S['qdeg'],axis=0)/np.diff(S['times'])[:,None,None]
acc=np.diff(vel,axis=0)/((np.diff(S['times'])[1:]+np.diff(S['times'])[:-1])/2)[:,None,None]
dump('READONLY_MODEL_CHECK.json',dict(quaternion_skin_max_mm=float(err.max()),
    absolute_engineering_angle_skin_max_mm=float(qerr.max()),
    samples=t[ix],max_by_digit={d:float(err[:,M['rois'][d]['vertices']].max()) for d in c.DIGITS},
    source_joint_min_deg=S['qdeg'].min(0),source_joint_max_deg=S['qdeg'].max(0),
    source_peak_velocity_deg_sec=np.max(abs(vel),axis=0),source_peak_acceleration_deg_sec2=np.max(abs(acc),axis=0),
    shape_max_abs=np.max(abs(D['shape_values']),axis=0),fixed_skin_vertices=len(fixed),
    invariant_key_conflicts=hits,convex_components_verified=len(components),
    static_solves=0,dynamic_solves=0,pose_edits=0,
    gate='CONTINUE' if not hits and err.max()<.03 and qerr.max()<.03 else 'STOP_FOR_EVIDENCE_REVIEW'))
print('READONLY_PARITY',float(err.max()),float(qerr.max()),'INVARIANT_HITS',hits,flush=True)
