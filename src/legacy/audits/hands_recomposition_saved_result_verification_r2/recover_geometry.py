"""Repair diagnostic predicate only; reuse actual captured skin of all three poses.

No corrected pose is generated, applied, or reevaluated here. Reload original
C1 solely for actual same-time key geometry and baseline snapshot comparison.
"""
from source_actual import *
OUT=O/'software_recovery_1'
def write(n,v):atomic_json('software_recovery_1/'+n,v)

def clip(poly,plane,margin=0.):
    out=[]
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)];dp=float(p@plane[:3]-plane[3]+margin);dq=float(q@plane[:3]-plane[3]+margin)
        if dp<=0:out.append(p)
        if (dp<0<dq) or (dq<0<dp):out.append(p+(q-p)*dp/(dp-dq))
    return out

def surface_gate(V,F,components,pairs):
    """Finite polygon clipping witness against the existing 0.5mm inner key body."""
    bylabel={str(k['key_index'])+':'+g['name']:(k,g,pl) for k,g,kv,kf,pl in components}
    details=[]
    for label,fi in sorted({(label,fi) for label,fi,kf in pairs}):
        k,g,pl=bylabel[label];f=F[fi]
        # Both quad diagonals are checked; a diagnostic proof is not sensitive to tessellation choice.
        variants=[[(0,1,2),(0,2,3)],[(0,1,3),(1,2,3)]] if len(f)==4 else [[tuple([0,j,j+1]) for j in range(1,len(f)-1)]]
        checks=[]
        for variant in variants:
            deep=False;witnesses=[]
            for tri in variant:
                poly=[V[f[i]] for i in tri]
                for plane in pl:
                    if not poly:break
                    poly=clip(poly,plane,.0005)
                if len(poly)>=3:
                    p=np.mean(poly,axis=0);depth=float(-np.max(p@pl[:,:3].T-pl[:,3])*1000)
                    if depth>.5:
                        deep=True;witnesses.append(dict(point_world_m=p,depth_mm=depth,triangle_vertices=[f[i] for i in tri]))
            checks.append(dict(surface_exceeds_half_mm=deep,witnesses=witnesses))
        details.append(dict(key=k['note_name'],component=g['name'],skin_face=fi,diagonal_checks=checks))
    return dict(existing_threshold_mm=.5,deep_surface_proven=any(all(x['surface_exceeds_half_mm'] for x in d['diagonal_checks']) for d in details),
        deep_surface_possible=any(any(x['surface_exceeds_half_mm'] for x in d['diagonal_checks']) for d in details),faces=details,
        interpretation='BVH zero is not a replacement for the original 0.5mm gate; clip existing intersecting skin faces against the half-mm inward offset of real key planes. No numerical optimizer.')

def recovery():
    I,P,man,S,A,results=load_inputs();before=read(O/'INPUT_SHA_BEFORE.json')
    assert read(O/'BLENDER_STATE_RECONSTRUCTION.json')['pass_']
    assert all(sha(p)==s for p,s in before.items())
    with np.load(O/'ACTUAL_BLENDER_STATIC_SKIN.npz',allow_pickle=False) as z:
        base=z['baseline_vertices'].copy();corrected=z['corrected_vertices'].copy();flat=z['face_vertices'];off=z['face_offsets'];F=[flat[off[i]:off[i+1]].tolist() for i in range(len(off)-1)]
    # Automated predicate selftest, with no scene or pose manipulation.
    assert .49<=P['wrong_key_depth_mm'] and not (.51<=P['wrong_key_depth_mm'])
    probe={'LITTLE':{'pairs':{(1,1)},'depth_mm':0.,'allowed_own_key':False},'LITTLE_INFLUENCE_GT_005':{'pairs':{(1,1)},'depth_mm':0.,'allowed_own_key':False}}
    bg=dict(digit_pairs={},self_pairs=set(),keys={'k':dict(key='E5',component='g',regions=probe)})
    ng=dict(digit_pairs={},self_pairs=set(),keys={'k':dict(key='E5',component='g',regions={n:{**r,'pairs':{(2,2)}} for n,r in probe.items()})})
    assert compare(bg,ng)==[]
    write('SOFTWARE_PREDICATE_SELFTEST.json',dict(pass_=True,existing_depth_gate_mm=.5,active_BVH_pairs_are_evidence_not_new_zero_threshold=True,other_digits_nonregression_excludes_active_little=True,original_skin_snapshot_sha256=sha(O/'ACTUAL_BLENDER_STATIC_SKIN.npz'),corrected_poses_reapplied=0))
    bpy.ops.wm.open_mainfile(filepath=str(safe_path(man['path'])),load_ui=False,use_scripts=False);assert not bpy.data.libraries
    sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
    rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];left=bpy.data.objects[man['mapping']['L']['mesh']]
    native_before=h.digest(h.native(mesh,rig));assert native_before==I['native_sha256']
    action_before=actions_digest();rois=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json')
    groups={g.index:g.name for g in mesh.vertex_groups}
    weights=np.array([[sum(g.weight for g in v.groups if groups[g.group].startswith(d+'_')) for d in numeric.DIGITS] for v in mesh.data.vertices]);strong=set(v for r in rois.values() for v in r['vertices'])
    regions={d:np.array(rois[d]['vertices'],dtype=int) for d in numeric.DIGITS}
    regions.update(PALM_SHARED_WEB=np.array([i for i in range(len(weights)) if i not in strong]),CROSS_DIGIT_MIXED_GT_005=np.flatnonzero((weights>.05).sum(1)>=2),LITTLE_INFLUENCE_GT_005=np.flatnonzero(weights[:,4]>.05))
    face_regions={r:{i for i,f in enumerate(F) if any(v in set(ids.tolist()) for v in f)} for r,ids in regions.items()}
    rows=[];kp=0.;ambiguous=False
    for ix,t in enumerate(TIMES):
        t=float(t);h.settime(sc,t);bV,bF=h.coords(mesh);assert bF==F and points_error(bV,base[ix])<.01
        ka=np.zeros(88)
        for ki,n in man['key_pivots'].items():ka[int(ki)]=bpy.data.objects[n].rotation_euler.x
        assert np.array_equal(ka,S['key_angles'][ix])
        components=[]
        for k in numeric.KEYS:
            obs=[ob for ob in sc.objects if ob.type=='MESH' and ob.get('FROZEN_KEY_INDEX')==k['key_index']]
            assert len(obs)==len(k['geometry'])
            for g in k['geometry']:
                ob=next(o for o in obs if g['name'] in o.name);kv,kf=h.coords(ob);pv=np.array(k['press_pivot']);expected=(np.array(g['vertices'])-pv)@h.axisrot(ka[k['key_index']],k['press_axis']).T+pv
                kp=max(kp,float(abs(kv-expected).max()*1000));assert kp<.001
                planes=h.component_planes(dict(vertices=kv,triangles=[v for f in kf for j in range(1,len(f)-1) for v in (f[0],f[j],f[j+1])]))
                components.append((k,g,kv,kf,planes))
        owned={}
        for n in I['right_events']:
            if n['note_on']<=t<n['note_off']+.04:owned.setdefault(n['key_index'],set()).add(numeric.DIGITS[n['finger']-1])
        owned.setdefault(53,set()).add('LITTLE_INFLUENCE_GT_005')
        B=base[ix];V=corrected[ix];bg=geometry(B,F,rois,regions,face_regions,components,owned);ng=geometry(V,F,rois,regions,face_regions,components,owned)
        ct=contact(V,numeric.KEYS[53],ka[53]);regressions=compare(bg,ng);sg=surface_gate(V,F,components,ng['little_pairs'])
        leftV,leftF=h.coords(left);bp=overlap(tree(B,F),tree(leftV,leftF));npairs=overlap(tree(V,F),tree(leftV,leftF))
        if npairs-bp:regressions.append(dict(kind='NEW_RIGHT_LEFT_SKIN_INTERSECTION',added_count=len(npairs-bp)))
        active_pass=ng['little_depth_mm']<=.5 and not sg['deep_surface_proven']
        if sg['deep_surface_possible']!=sg['deep_surface_proven']:ambiguous=True
        row=dict(time=t,contact=ct,baseline_contact=contact(B,numeric.KEYS[53],ka[53]),baseline=serial_summary(bg),corrected=serial_summary(ng),surface_depth_gate=sg,
            active_neighbor_pass=active_pass,nonregression_pass=not regressions,regressions=regressions,E5_surface_intersection_fully_eliminated=not ng['little_pairs'],pass_=ct['pass_'] and active_pass and not regressions)
        rows.append(row);write('GEOMETRY_POSE_'+str(ix)+'.json',row)
        write('GEOMETRY_WITNESS_'+str(ix)+'.json',dict(time=t,actual_skin_archive='../ACTUAL_BLENDER_STATIC_SKIN.npz',baseline_active_wrong_key_face_pairs=sorted(bg['little_pairs']),corrected_active_wrong_key_face_pairs=sorted(ng['little_pairs']),surface_depth_gate=sg,
            E5_actual_geometry=[dict(component=g['name'],world_vertices_m=kv,faces=kf) for k,g,kv,kf,pl in components if k['note_name']=='E5'],new_full_self_face_pairs=sorted(ng['self_pairs']-bg['self_pairs']),regressions=regressions))
        print('RECOVERED_GEOMETRY',t,'contact',ct['pass_'],'neighbor_05mm',active_pass,'BVH',len(ng['little_pairs']),'regressions',len(regressions),'PASS',row['pass_'],flush=True)
        if not row['pass_']:break
    after={p:sha(p) for p in before};assert after==before and actions_digest()==action_before and h.digest(h.native(mesh,rig))==native_before
    write('FROZEN_PROTECTION.json',dict(pass_=True,native_sha256=native_before,action_before=action_before,action_after=actions_digest(),input_sha256_after=after,corrected_poses_reapplied=0))
    result='STATIC_SOURCE_CORRECTION_FAIL' if any(not r['pass_'] for r in rows) else 'INCONCLUSIVE' if ambiguous or len(rows)!=3 else 'STATIC_SOURCE_CORRECTION_VERIFIED'
    write('BLENDER_VERIFICATION_RESULT.json',dict(RESULT=result,rows=[dict(time=r['time'],contact=r['contact'],active_neighbor_pass=r['active_neighbor_pass'],nonregression_pass=r['nonregression_pass'],residual_active_BVH_pairs=r['corrected']['active_little_wrong_key_BVH_pairs'],E5_surface_intersection_fully_eliminated=r['E5_surface_intersection_fully_eliminated']) for r in rows],
        gate_authority='Original 0.03mm horizontal, 3mm vertical, 0.5mm non-target-key depth, 0.02mm depth nonregression; preserve all BVH evidence without adding zero-pair gate',
        geometry_poses_checked=len(rows),reconstruction_pass=True,original_skin_snapshot_reused=True,corrected_poses_reapplied=0,software_repair_round=2,frozen_protection_pass=True,optimizer_calls=0,DYNAMIC_RECOMPOSITION='NOT_EXECUTED',HUMAN_NATURALNESS='NOT_TESTED'))
    print('RECOVERED_RESULT',result,flush=True)

if __name__=='__main__':
    try:recovery()
    except BaseException:
        write('BLENDER_FAILURE.json',dict(RESULT='BLOCKED_TOOLCHAIN',error=traceback.format_exc()))
        raise
