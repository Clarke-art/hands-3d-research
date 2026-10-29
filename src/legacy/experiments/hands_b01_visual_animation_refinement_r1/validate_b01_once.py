import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();lock=read(OUT/'STRATEGY_LOCK.json');edit=read(OUT/'EDIT_RECEIPT.json');visual=read(OUT/'VISUAL_REVIEW_BEFORE_QC.json')
assert visual['reviewed_before_machine_qc']
if (OUT/'FULL_VALIDATION_STARTED.json').exists():assert read(OUT/'FULL_VALIDATION_STARTED.json')['candidate_sha256']==edit['candidate_sha256']
else:save('FULL_VALIDATION_STARTED.json',dict(candidate_sha256=edit['candidate_sha256'],full_pass_number=1,visual_review_completed=True))
sc,rig,mesh,left,lrig=s.open_scene(edit['candidate_path']);assert sha(edit['candidate_path'])==edit['candidate_sha256']
candidate=rig.animation_data.action;source=bpy.data.actions[edit['source_action']];slot=rig.animation_data.action_slot.identifier
assert s.protected_state(exclude_rig=True)==edit['protected_actions']
assert all(c.digest(c.native(ob,rg))==edit['native_structure'][side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
def bind(action):rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[slot]
dm=types.ModuleType('existing_depth_math');p=ROOT/'audits/hands_saved_pose_geometry_closure_r1/depth_math.py';exec(compile(safe(p).read_text(encoding='utf8'),str(p),'exec'),dm.__dict__);assert len(dm.selftest())==4
components=[]
for key,g,pl in s.registered_components():
    ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==key['key_index'] and g['name'] in o.name)
    me=ob.data;me.calc_loop_triangles();kv=np.array([list(v.co) for v in me.vertices]);kt=np.array([list(t.vertices) for t in me.loop_triangles],int);lp,_=dm.planes_from_mesh(kv,kt)
    components.append(dict(key=key,obj=ob,vertices=kv,triangles=kt,localplanes=lp,name=g['name'],registered=g))
assert len(components)==139
model=read(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL_MANIFEST.json')
with np.load(safe(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL.npz')) as z:W=z['weights'].copy()
DW=np.column_stack([W[:,[i for i,n in enumerate(model['bones']) if n.startswith(d+'_')]].sum(1) for d in DIGITS]);union={v for r in ROI.values() for v in r['vertices']}
regions={d:np.array(ROI[d]['vertices'],int) for d in DIGITS};regions['PALM_SHARED_WEB']=np.array([i for i in range(len(W)) if i not in union]);regions['CROSS_DIGIT_MIXED']=np.flatnonzero((DW>.05).sum(1)>=2)
regions['MIDDLE_GT005']=np.flatnonzero(DW[:,2]>.05);regions['RING_GT005']=np.flatnonzero(DW[:,3]>.05)
names=list(regions);nr=len(names);EPS=1e-6
raw=[START,END,*np.arange(round(START*240),round(END*240)+1)/240,*[a[0] for a in lock['anchors']]]
for n in NOTES:
    for field in ['note_on','note_off']:raw.extend(n[field]+d for d in [-.18,-.075,0,.0175,.035,.04,.07] if START<=n[field]+d<=END)
times=[]
for t in sorted(raw):
    if not times or t-times[-1]>1e-8:times.append(float(t))
times=np.array(times);records=[];contacts=[];regressions=[];snapshots=[[],[]];qstates=[[],[]];tristates=[[],[]];queries=0;members=None;region_polys=None;region_tri=None;triangulation_changed_samples=0
maxkeyerr=0.;outside_delta=0.;max_unedited_q=0.;max_root_delta=0.;corefail=0
def tree(V,F):return BVHTree.FromPolygons([Vector(v) for v in V],F,epsilon=0)
def geometry_trees(V,F,L,LF):
    whole=tree(V,F);digits={d:tree(V,ROI[d]['faces']) for d in DIGITS}
    pairs={a+'_'+b:set(map(tuple,digits[a].overlap(digits[b]))) for a,b in itertools.combinations(DIGITS,2)}
    pairs['FULL_SELF']={(a,b) for a,b in whole.overlap(whole) if a<b and members[a].isdisjoint(members[b])};pairs['RIGHT_LEFT']=set(map(tuple,whole.overlap(tree(L,LF))))
    return whole,pairs
def key_world(comp):
    M=np.array(comp['obj'].matrix_world);kv=(np.c_[comp['vertices'],np.ones(len(comp['vertices']))]@M.T)[:,:3]
    lp=np.c_[comp['localplanes'][:,:3],-comp['localplanes'][:,3]];wp=<REDACTED_EMAIL>(M);norm=np.linalg.norm(wp[:,:3],axis=1)
    return kv,np.c_[wp[:,:3]/norm[:,None],-wp[:,3]/norm]
for ix,t in enumerate(times):
    states=[]
    for action in [source,candidate]:
        bind(action);c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left);q=np.array([s.degrees(d) for d in DIGITS]);root=np.array(rig.matrix_world)
        states.append((V,T,F,L,LF,q,root))
    B,T,F,L,LF,qb,rb=states[0];N,NT,NF,NL,NLF,qn,rn=states[1]
    assert F==NF and np.array_equal(L,NL),('POLYGON_OR_LEFT_SKIN_CHANGED',t,F==NF,float(np.max(abs(L-NL))))
    # Blender may choose a different diagonal for a deformed quad. Preserve and
    # evaluate each state's actual triangulation, not the other pose's diagonal.
    tristates[0].append(T);tristates[1].append(NT)
    same_tri=np.all(T==NT,axis=1);triangulation_changed_samples+=int(not np.all(same_tri))
    snapshots[0].append(B);snapshots[1].append(N);qstates[0].append(qb);qstates[1].append(qn)
    max_root_delta=max(max_root_delta,float(np.max(abs(rn-rb))));max_unedited_q=max(max_unedited_q,float(np.max(abs(qn[[0,1,4]]-qb[[0,1,4]]))))
    if t<=lock['support'][0]+1e-9 or t>=lock['support'][1]-1e-9:outside_delta=max(outside_delta,float(np.max(np.linalg.norm(N-B,axis=1))*1000))
    if members is None:
        members=[set(f) for f in F];region_polys={name:{i for i,f in enumerate(F) if any(v in set(ids) for v in f)} for name,ids in regions.items()}
    region_tri=[np.array([np.any(np.isin(tris,ids),axis=1) for ids in regions.values()]) for tris in [T,NT]]
    changed_tri=(~same_tri)|np.any(np.any(B!=N,axis=1)[T],axis=1)
    trees=[];pairs=[]
    for V in [B,N]:tr,pa=geometry_trees(V,F,L,LF);trees.append(tr);pairs.append(pa)
    pairrow={}
    for label in pairs[0]:
        added=pairs[1][label]-pairs[0][label];pairrow[label]=dict(baseline=len(pairs[0][label]),candidate=len(pairs[1][label]),new=len(added))
        if added:regressions.append(dict(time=t,kind='NEW_'+label+'_FACE_PAIRS',count=len(added),examples=sorted(added)[:10]))
    if lock['core'][0]-1e-9<=t<=lock['core'][1]+1e-9 and pairs[1]['MIDDLE_RING']:corefail+=1
    for n in NOTES:
        if n['note_on']<=t<n['note_off']:
            va,vb=(B,N) if n['hand']=='R' else (L,NL);bc=s.contact(va,KEYS[n['key_index']],n['hand'],n['finger']);nc=s.contact(vb,KEYS[n['key_index']],n['hand'],n['finger']);vid=nc['vertex']
            contacts.append(dict(time=t,event=n['note_id'],baseline=bc,candidate=nc,pad_change_mm=float(np.linalg.norm(vb[vid]-va[vid])*1000)))
    triV=[B[T],N[NT]];triLo=[v.min(1) for v in triV];triHi=[v.max(1) for v in triV];depths=np.zeros((2,139,nr));surfaces=np.zeros((2,139,nr));framekeynew=0
    for ci,comp in enumerate(components):
        key=comp['key'];kv,P=key_world(comp);lo=kv.min(0);hi=kv.max(0);pv=np.asarray(key['press_pivot']);exp=(np.asarray(comp['registered']['vertices'])-pv)@c.axisrot(s.keyangle(key),key['press_axis']).T+pv
        maxkeyerr=max(maxkeyerr,float(np.max(abs(kv-exp))*1000));crosses=[];certs=[];ktree=None
        for si,V in enumerate([B,N]):
            if np.any(V.max(0)<lo-1e-10) or np.any(V.min(0)>hi+1e-10):crosses.append(set());certs.append({});continue
            if ktree is None:ktree=tree(kv,comp['triangles'])
            crosses.append(set(map(tuple,trees[si].overlap(ktree))))
            depth=np.maximum(0,np.min(P[:,3]-V@P[:,:3].T,axis=1))*1000
            for ri,ids in enumerate(regions.values()):depths[si,ci,ri]=float(depth[ids].max())
            candidate_tris=np.flatnonzero(np.all(triHi[si]>=lo-1e-10,axis=1)&np.all(triLo[si]<=hi+1e-10,axis=1));solved={}
            for ti in candidate_tris:
                ti=int(ti)
                if si==1 and not changed_tri[ti] and ti in certs[0]:r=certs[0][ti]
                else:r=dm.max_triangle_depth(triV[si][ti],P);queries+=1
                solved[ti]=r
                if r['upper_mm']>EPS:
                    for ri in np.flatnonzero(region_tri[si][:,ti]):surfaces[si,ci,ri]=max(surfaces[si,ci,ri],r['upper_mm'])
            certs.append(solved)
        added=crosses[1]-crosses[0]
        owned={DIGITS[n['finger']-1] for n in NOTES if n['hand']=='R' and n['key_index']==key['key_index'] and n['note_on']<=t<n['note_off']+.04}
        added=[(a,b) for a,b in added if not any(a in region_polys[d] for d in owned)]
        if added:framekeynew+=len(added);regressions.append(dict(time=t,kind='NEW_NONOWNED_SKIN_KEY_FACES',key=key['note_name'],component=comp['name'],count=len(added),examples=added[:8]))
        for ri,region in enumerate(names):
            digit=region.split('_GT')[0]
            if digit in owned:continue
            bd,nd=depths[:,ci,ri];bs,ns=surfaces[:,ci,ri]
            if nd>.5 and nd>bd+.02:regressions.append(dict(time=t,kind='NONOWNED_VERTEX_REGRESSION',region=region,key=key['note_name'],baseline_mm=bd,candidate_mm=nd))
            if (ns>EPS and bs<=EPS) or ns>bs+.02:regressions.append(dict(time=t,kind='NONOWNED_SURFACE_REGRESSION',region=region,key=key['note_name'],baseline_mm=bs,candidate_mm=ns))
    records.append(dict(time=t,pairs=pairrow,new_nonowned_key_faces=framekeynew,all_region_vertex_peak_mm=depths.max(axis=(1,2)),all_region_surface_peak_mm=surfaces.max(axis=(1,2))))
    if ix%12==0:
        print('B01_REAL_QC',ix,len(times),'sec',round(time.perf_counter()-begin,2),'MR',pairrow['MIDDLE_RING'],'regressions',len(regressions),flush=True)
        (OUT/'QC_PROGRESS.json').write_text(json.dumps(dict(completed=ix,total=len(times),seconds=time.perf_counter()-begin,regressions=len(regressions))),encoding='utf8')
    if time.perf_counter()-begin>1100:raise TimeoutError('QC_TIME_STOP_NO_SECOND_CANDIDATE')
Q=np.array(qstates);bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])
domain_B=float(max(0,np.max(bounds[:,0][None]-Q[0]),np.max(Q[0]-bounds[:,1][None])));domain_N=float(max(0,np.max(bounds[:,0][None]-Q[1]),np.max(Q[1]-bounds[:,1][None])))
vel=np.diff(Q,axis=1)/np.diff(times)[None,:,None,None];added_velocity=float(np.max(abs(vel[1]-vel[0])))
fail=sum(not r['candidate']['pass_'] for r in contacts);basefail=sum(not r['baseline']['pass_'] for r in contacts)
passed=not regressions and corefail==0 and fail==0 and domain_N<=.002 and added_velocity<=180 and outside_delta<.001 and maxkeyerr<.001 and max_root_delta==0 and max_unedited_q<1e-6
with (OUT/'ACTUAL_B01_SKIN_QC.npz').open('xb') as f:np.savez_compressed(f,times=times,baseline_vertices=snapshots[0],candidate_vertices=snapshots[1],baseline_qdeg=qstates[0],candidate_qdeg=qstates[1],baseline_triangles=tristates[0],candidate_triangles=tristates[1])
save('B01_MACHINE_VALIDATION.json',dict(pass_=bool(passed),seconds=time.perf_counter()-begin,samples=len(times),records=records,regressions=regressions,contacts=contacts,
 baseline_contact_failures=basefail,candidate_contact_failures=fail,baseline_domain_violation_deg=domain_B,candidate_domain_violation_deg=domain_N,
 added_velocity_peak_deg_s=added_velocity,baseline_joint_velocity_peak_deg_s=float(np.max(abs(vel[0]))),candidate_joint_velocity_peak_deg_s=float(np.max(abs(vel[1]))),
 core_samples_with_middle_ring_intersections=corefail,outside_edit_skin_delta_mm=outside_delta,unedited_digits_qdeg_difference=max_unedited_q,root_world_difference=max_root_delta,
 key_registration_max_mm=maxkeyerr,surface_queries=queries,actual_triangulation_changed_samples=triangulation_changed_samples,coverage=dict(right_vertices=len(W),triangles=len(T),keys=88,components=139,regions={k:len(v) for k,v in regions.items()},digit_pairs=10,full_nonincident_self=True,right_left=True),
 original_actions_preserved=s.protected_state(exclude_rig=True)==edit['protected_actions'],source_sha256=sha(SOURCE),candidate_sha256=sha(edit['candidate_path']),
 sample_policy='240Hz full .9-1.75s + exact MIDI roles, anchors, support boundaries; finite geometry, no unsampled continuous safety proof',human_visual_acceptance='PENDING',optimizer_calls=0))
protection('VALIDATION_PROTECTION.json');print('B01_QC_FINAL',passed,corefail,fail,domain_N,added_velocity,len(regressions),time.perf_counter()-begin,flush=True)
