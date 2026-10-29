import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();lock=read(OUT/'STRATEGY_LOCK.json');edit=read(OUT/'EDIT_RECEIPT.json')
save('FULL_VALIDATION_STARTED.json',dict(candidate_sha256=edit['candidate_sha256'],complete_pass_number=1,sample_hz=240))
sc,rig,mesh,left,lrig=s.open_scene(edit['candidate_path']);assert sha(edit['candidate_path'])==edit['candidate_sha256']
candidate=rig.animation_data.action;slot=rig.animation_data.action_slot.identifier;source=bpy.data.actions[edit['source_action']]
assert s.payload(source,{'pose.bones["RING_MCP_R"].rotation_quaternion'})==s.payload(candidate,{'pose.bones["RING_MCP_R"].rotation_quaternion'})
assert s.protected_state(exclude_rig=True)==edit['protected_actions']
assert all(c.digest(c.native(ob,rg))==edit['native_structure'][side] for side,ob,rg in [('R',mesh,rig),('L',left,lrig)])
def bind(action):rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[slot]
dm=types.ModuleType('existing_depth_math');p=ROOT/'audits/hands_saved_pose_geometry_closure_r1/depth_math.py'
exec(compile(safe(p).read_text(encoding='utf8'),str(p),'exec'),dm.__dict__)
assert len(dm.selftest())==4
components=[]
for key,g,pl in s.registered_components():
    ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==key['key_index'] and g['name'] in o.name)
    me=ob.data;me.calc_loop_triangles();kv=np.array([list(v.co) for v in me.vertices]);kt=np.array([list(t.vertices) for t in me.loop_triangles],int)
    planes,_=dm.planes_from_mesh(kv,kt)
    components.append(dict(key=key,obj=ob,vertices=kv,triangles=kt,localplanes=planes,name=g['name']))
assert len(components)==139
model=read(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL_MANIFEST.json')
with np.load(safe(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL.npz')) as z:W=z['weights'].copy()
DW=np.column_stack([W[:,[i for i,n in enumerate(model['bones']) if n.startswith(d+'_')]].sum(1) for d in DIGITS])
union=set(v for d in ROI.values() for v in d['vertices'])
regions={d:np.array(ROI[d]['vertices'],int) for d in DIGITS};regions['PALM_SHARED_WEB']=np.array([v for v in range(len(W)) if v not in union]);regions['CROSS_DIGIT_MIXED']=np.flatnonzero((DW>.05).sum(1)>=2);regions['RING_GT005']=np.flatnonzero(DW[:,3]>.05)
RINGI=list(regions).index('RING_GT005');nr=len(regions)
raw=[START,END,4.6,4.85,5.25,5.5,4.916666666666667,*np.arange(round(START*240),round(END*240)+1)/240]
for n in NOTES:
    for x in ['note_on','note_off']:
        raw.extend(n[x]+d for d in [-.18,-.075,0,.0175,.035,.04,.07] if START<=n[x]+d<=END)
times=[]
for t in sorted(raw):
    if not times or t-times[-1]>1e-8:times.append(float(t))
times=np.array(times)
records=[];regressions=[];contactrows=[];allV=[[],[]];allQ=[[],[]];allquat=[[],[]];allleft=[]
queries=0;key_parity=0.;native_contact_drift=0.;max_other_vertex_move=0.;outside_motion_delta=0.
target_poly=None;members=None;region_polys=None;region_tri=None
def world_component(comp):
    ob=comp['obj'];M=np.array(ob.matrix_world);kv=(np.c_[comp['vertices'],np.ones(len(comp['vertices']))]@M.T)[:,:3]
    lp=np.c_[comp['localplanes'][:,:3],-comp['localplanes'][:,3]]
    wp=<REDACTED_EMAIL>(M);length=np.linalg.norm(wp[:,:3],axis=1)
    P=np.c_[wp[:,:3]/length[:,None],-wp[:,3]/length]
    return kv,P
def tree(V,F):return BVHTree.FromPolygons([Vector(v) for v in V],F,epsilon=0)
def overlaps(V,F,L,LF):
    whole=tree(V,F);digits={d:tree(V,ROI[d]['faces']) for d in DIGITS}
    pairs={a+'_'+b:set(map(tuple,digits[a].overlap(digits[b]))) for a,b in itertools.combinations(DIGITS,2)}
    pairs['FULL_SELF']={(a,b) for a,b in whole.overlap(whole) if a<b and members[a].isdisjoint(members[b])}
    pairs['RIGHT_LEFT']=set(map(tuple,whole.overlap(tree(L,LF))))
    return whole,pairs
for ix,t in enumerate(times):
    states=[]
    for action in [source,candidate]:
        bind(action);c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);L,LT,LF=s.coords_tri(left)
        q=np.array([s.degrees(d) for d in DIGITS]);quat=np.array([list(rig.pose.bones[n].rotation_quaternion.normalized()) for n in c.SETUPS['R','RING'][0]])
        states.append((V,T,F,L,LF,q,quat))
    B,T,F,L,LF,qb,rb=states[0];N,NT,NF,NL,NLF,qn,rn=states[1]
    assert np.array_equal(T,NT) and F==NF and np.array_equal(L,NL)
    allV[0].append(B);allV[1].append(N);allQ[0].append(qb);allQ[1].append(qn);allquat[0].append(rb);allquat[1].append(rn);allleft.append(L)
    if members is None:
        members=[set(f) for f in F]
        region_polys={name:{i for i,f in enumerate(F) if any(v in set(ids) for v in f)} for name,ids in regions.items()}
        region_tri=np.array([np.any(np.isin(T,ids),axis=1) for ids in regions.values()])
    moved=np.any(B!=N,axis=1);changed_tri=np.any(moved[T],axis=1)
    max_other_vertex_move=max(max_other_vertex_move,float(np.linalg.norm(N[DW[:,3]==0]-B[DW[:,3]==0],axis=1).max()*1000))
    if t<=4.6+1e-9 or t>=5.5-1e-9:outside_motion_delta=max(outside_motion_delta,float(np.linalg.norm(N-B,axis=1).max()*1000))
    trees=[];pairs=[]
    for V in [B,N]:
        tr,pa=overlaps(V,F,L,LF);trees.append(tr);pairs.append(pa)
    pair_stats={}
    for label in pairs[0]:
        added=pairs[1][label]-pairs[0][label]
        pair_stats[label]=dict(baseline=len(pairs[0][label]),candidate=len(pairs[1][label]),new=len(added))
        if added:regressions.append(dict(time=t,kind='NEW_'+label+'_FACE_PAIRS',count=len(added),examples=sorted(added)[:12]))
    # Contact uses actual evaluated skin of both hands and actual key angles.
    for n in NOTES:
        if n['note_on']<=t<n['note_off']:
            va,vb=(B,N) if n['hand']=='R' else (L,NL)
            cb=s.contact(va,KEYS[n['key_index']],n['hand'],n['finger']);cn=s.contact(vb,KEYS[n['key_index']],n['hand'],n['finger'])
            vid=cn['vertex'];drift=float(np.linalg.norm(vb[vid]-va[vid])*1000);native_contact_drift=max(native_contact_drift,drift)
            contactrows.append(dict(time=t,event=n['note_id'],baseline=cb,candidate=cn,drift_mm=drift))
    depths=np.zeros((2,139,nr));surfaces=np.zeros((2,139,nr));target_pairs=[0,0];key_added=0;surface_peak=[None,None]
    triV=[B[T],N[T]];triLo=[v.min(1) for v in triV];triHi=[v.max(1) for v in triV]
    for ci,comp in enumerate(components):
        key=comp['key'];kv,P=world_component(comp);lo=kv.min(0);hi=kv.max(0)
        # Actual Blender key body against the frozen registration, not a new proxy.
        pv=np.asarray(key['press_pivot']);g=key['geometry'][next(j for j,g in enumerate(key['geometry']) if g['name']==comp['name'])]
        exp=(np.asarray(g['vertices'])-pv)@c.axisrot(s.keyangle(key),key['press_axis']).T+pv
        key_parity=max(key_parity,float(np.max(abs(kv-exp))*1000))
        sets=[];certs=[];ktree=None
        for state,V in enumerate([B,N]):
            if np.any(V.max(0)<lo-1e-10) or np.any(V.min(0)>hi+1e-10):sets.append(set());certs.append({});continue
            if ktree is None:ktree=tree(kv,comp['triangles'])
            cross=set(map(tuple,trees[state].overlap(ktree)));sets.append(cross)
            depth=np.maximum(0,np.min(P[:,3]-V@P[:,:3].T,axis=1))*1000
            for ri,ids in enumerate(regions.values()):depths[state,ci,ri]=float(depth[ids].max())
            candidates=np.flatnonzero(np.all(triHi[state]>=lo-1e-10,axis=1)&np.all(triLo[state]<=hi+1e-10,axis=1))
            solved={}
            for ti in candidates:
                ti=int(ti)
                if state==1 and not changed_tri[ti] and ti in certs[0]:r=certs[0][ti]
                else:r=dm.max_triangle_depth(triV[state][ti],P);queries+=1
                solved[ti]=r
                if r['upper_mm']>1e-6:
                    for ri in np.flatnonzero(region_tri[:,ti]):surfaces[state,ci,ri]=max(surfaces[state,ci,ri],r['upper_mm'])
                    if key['key_index']==52 and region_tri[RINGI,ti] and (surface_peak[state] is None or r['upper_mm']>surface_peak[state]['upper_mm']):surface_peak[state]=dict(triangle=ti,component=comp['name'],**r)
            certs.append(solved)
            if key['key_index']==52:target_pairs[state]+=sum(a in region_polys['RING_GT005'] for a,b in cross)
        added=sets[1]-sets[0]
        if added:
            # No absolute zero-BVH gate: the comparison asks whether this edit
            # created new nonowned skin/key intersections outside the repair target.
            allowed_regions={DIGITS[n['finger']-1] for n in NOTES if n['hand']=='R' and n['key_index']==key['key_index'] and n['note_on']<=t<n['note_off']+.04}
            new_nonowned=[(a,b) for a,b in added if not any(a in region_polys[d] for d in allowed_regions)]
            if key['key_index']==52:new_nonowned=[(a,b) for a,b in new_nonowned if a not in region_polys['RING_GT005']]
            if new_nonowned:key_added+=len(new_nonowned);regressions.append(dict(time=t,kind='NEW_OTHER_SKIN_KEY_FACE_PAIRS',key=key['note_name'],component=comp['name'],count=len(new_nonowned),examples=new_nonowned[:8]))
        for ri,region in enumerate(regions):
            owned=any(n['hand']=='R' and DIGITS[n['finger']-1]==region and n['key_index']==key['key_index'] and n['note_on']<=t<n['note_off']+.04 for n in NOTES)
            if owned:continue
            target=region in ['RING','RING_GT005'] and key['key_index']==52
            if not target:
                if depths[1,ci,ri]>.5 and depths[1,ci,ri]>depths[0,ci,ri]+.02:regressions.append(dict(time=t,kind='OTHER_REGION_VERTEX_REGRESSION',region=region,key=key['note_name'],baseline_mm=depths[0,ci,ri],candidate_mm=depths[1,ci,ri]))
                if surfaces[1,ci,ri]>max(.0001,surfaces[0,ci,ri]+.02):regressions.append(dict(time=t,kind='OTHER_REGION_SURFACE_REGRESSION',region=region,key=key['note_name'],baseline_mm=surfaces[0,ci,ri],candidate_mm=surfaces[1,ci,ri]))
    target_idx=[j for j,c0 in enumerate(components) if c0['key']['key_index']==52]
    td=depths[:,target_idx,RINGI].max(1);tsurf=surfaces[:,target_idx,RINGI].max(1)
    if td[1]>td[0]+.02 or tsurf[1]>tsurf[0]+.02:regressions.append(dict(time=t,kind='TARGET_REGRESSION',baseline_mm=td[0],candidate_mm=td[1],surface_baseline_mm=tsurf[0],surface_candidate_mm=tsurf[1]))
    records.append(dict(time=t,target_vertex_mm=td,target_surface_upper_mm=tsurf,target_key_face_pairs=target_pairs,target_surface_witness=surface_peak,pairs=pair_stats,
                        other_vertex_peak_mm=depths[:,:,:RINGI].max(axis=(1,2)),new_other_key_face_pairs=key_added))
    if ix%10==0:
        print('FULL_REAL_QC',ix,len(times),'seconds',round(time.perf_counter()-begin,2),'queries',queries,'target',td.tolist(),'regressions',len(regressions),flush=True)
        (OUT/'QC_PROGRESS.json').write_text(json.dumps(dict(completed=ix,total=len(times),seconds=time.perf_counter()-begin,regressions=len(regressions))),encoding='utf8')
    if time.perf_counter()-begin>1100:raise TimeoutError('QC_SCOPE_TIME_STOP_NO_SECOND_VALIDATION')
Q=np.array(allQ);dt=np.diff(times);vel=np.diff(Q,axis=1)/dt[None,:,None,None]
domain=np.array(lock['engineering_domain_deg']);domain_violation=float(max(0,np.max(domain[0]-Q[1,:,3]),np.max(Q[1,:,3]-domain[1])))
added=float(np.max(abs(vel[1]-vel[0])));targetcore=[r for r in records if 4.85-1e-9<=r['time']<=5.25+1e-9]
corepeak=max(r['target_vertex_mm'][1] for r in targetcore);coresurface=max(r['target_surface_upper_mm'][1] for r in targetcore)
contactfail=sum(not r['candidate']['pass_'] for r in contactrows);baselinecontactfail=sum(not r['baseline']['pass_'] for r in contactrows)
passed=not regressions and contactfail==0 and native_contact_drift<=.01 and domain_violation<=.002 and added<=180 and corepeak<=.5 and coresurface<=.5 and key_parity<.001 and outside_motion_delta<.001
with (OUT/'ACTUAL_LOCAL_SKIN_QC.npz').open('xb') as f:np.savez_compressed(f,times=times,baseline_vertices=allV[0],candidate_vertices=allV[1],left_vertices=allleft,baseline_qdeg=allQ[0],candidate_qdeg=allQ[1],triangles=T)
save('MACHINE_VALIDATION.json',dict(pass_=bool(passed),seconds=time.perf_counter()-begin,samples=len(times),sampling='240Hz + exact MIDI role stages + edit boundaries + witness; not an unsampled continuous collision proof',
    candidate_sha256=sha(edit['candidate_path']),records=records,regressions=regressions,contacts=contactrows,baseline_contact_failures=baselinecontactfail,candidate_contact_failures=contactfail,
    active_pad_drift_max_mm=native_contact_drift,target_core_peak_vertex_mm=corepeak,target_core_peak_surface_upper_mm=coresurface,
    domain_violation_deg=domain_violation,added_joint_velocity_peak_deg_s=added,original_joint_velocity_peak_deg_s=float(np.max(abs(vel[0]))),candidate_joint_velocity_peak_deg_s=float(np.max(abs(vel[1]))),
    outside_edit_skin_delta_mm=outside_motion_delta,unweighted_ring_region_other_skin_delta_mm=max_other_vertex_move,key_geometry_registration_max_mm=key_parity,surface_queries=queries,
    coverage=dict(keys=88,components=139,right_vertices=len(W),skin_triangles=len(T),regions={k:len(v) for k,v in regions.items()},digit_pairs=10,nonincident_full_self=True,right_left=True,real_skin=True,real_key_mesh=True),
    actions_preserved=s.protected_state(exclude_rig=True)==edit['protected_actions'],original_asset_files_readonly=True,naturalness='PENDING' if passed else 'NOT_TESTED',
    limitation='Finite real geometry samples; no blanket continuous, collision-free or whole-C1 product claim'))
protection('VALIDATION_PROTECTION.json');print('QC_FINAL',passed,corepeak,coresurface,contactfail,len(regressions),time.perf_counter()-begin,flush=True)
