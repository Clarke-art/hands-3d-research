"""All computations use frozen cached skin and supplemental actual key meshes."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from depth_math import max_triangle_depth
import numpy as np
EPS_MM=1e-6 # classification of floating-point tangency, not a collision gate
DIGITS=['THUMB','INDEX','MIDDLE','RING','LITTLE']

def axisrot(angle,axis):
    v=np.asarray(axis,dtype=float);v/=np.linalg.norm(v);x,y,z=v;cross=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return np.eye(3)+np.sin(angle)*cross+(1-np.cos(angle))*cross@cross

def contact(V,key,angle):
    p=V[1747];pv=np.array(key['press_pivot']);local=axisrot(-angle,key['press_axis'])@(p-pv)+pv
    s=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(local[:2]-np.clip(local[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
    h=float(np.linalg.norm(local[:2]-np.clip(local[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000);gap=float((local[2]-s['z'])*1000)
    inside=bool(s['xmin']<=local[0]<=s['xmax'] and s['ymin']<=local[1]<=s['ymax'])
    return dict(vertex=1747,horizontal_mm=h,gap_mm=gap,legal_playable_region=inside,world_m=p.tolist(),key_local_m=local.tolist(),pass_=h<=.03 and abs(gap)<=3 and inside)

def analyze(V,T,tri_poly,F,components,regions,owned,which):
    tri_points=V[T];tri_lo=tri_points.min(1);tri_hi=tri_points.max(1)
    region_vertices={r:set(ids.tolist()) for r,ids in regions.items()}
    region_tris={r:np.any(np.isin(T,ids),axis=1) for r,ids in regions.items()}
    region_polys={r:{i for i,f in enumerate(F) if any(v in ids for v in f)} for r,ids in region_vertices.items()}
    component_rows=[];certificates=[]
    active_vertex_peak=0.;active_L=0.;active_U=0.;active_peak=None;active_BVH=[];convex_queries=0
    for comp in components:
        ki=comp['key_index'];P=np.array(comp['planes']);kv=np.array(comp['vertices_world_m']);depth=np.maximum(0,np.min(P[:,3]-V@P[:,:3].T,axis=1))*1000
        # This broad phase includes triangles wholly contained in the component;
        # it does not depend on a BVH surface crossing or a penetrating vertex.
        candidate=np.flatnonzero(np.all(tri_hi>=kv.min(0)-1e-10,axis=1)&np.all(tri_lo<=kv.max(0)+1e-10,axis=1))
        solved={}
        for ti in candidate:
            r=max_triangle_depth(tri_points[ti],P);convex_queries+=1
            solved[int(ti)]=r
            if r['upper_mm']>EPS_MM:
                certificates.append(dict(component=comp['name'],key=comp['note'],key_index=ki,triangle=int(ti),polygon=int(tri_poly[ti]),skin_vertices=T[ti].tolist(),**r))
        pairs=[tuple(p) for p in comp[which+'_skin_key_BVH_pairs']]
        row=dict(key=comp['note'],key_index=ki,component=comp['name'],regions={},candidate_triangles=len(candidate))
        for region,ids in regions.items():
            vp=float(depth[ids].max()) if len(ids) else 0.
            subset=[(ti,r) for ti,r in solved.items() if region_tris[region][ti]]
            L=max((r['lower_mm'] for ti,r in subset),default=0.);U=max((r['upper_mm'] for ti,r in subset),default=0.)
            peak=max(subset,key=lambda x:x[1]['lower_mm']) if subset else None
            rp=[p for p in pairs if p[0] in region_polys[region]]
            row['regions'][region]=dict(vertex_depth_mm=vp,surface_lower_mm=L,surface_upper_mm=U,surface_peak_triangle=peak[0] if peak else None,
                BVH_pairs=len(rp),BVH_face_pairs=rp,allowed_target=region in owned.get(ki,set()),vertices=len(ids))
            if region=='LITTLE_GT_005' and ki!=53:
                active_vertex_peak=max(active_vertex_peak,vp);active_L=max(active_L,L);active_U=max(active_U,U)
                active_BVH.extend((comp['name'],int(a),int(b)) for a,b in rp)
                if peak and (active_peak is None or peak[1]['lower_mm']>active_peak['lower_mm']):
                    active_peak=dict(key=comp['note'],key_index=ki,component=comp['name'],triangle=peak[0],polygon=int(tri_poly[peak[0]]),skin_vertices=T[peak[0]].tolist(),**peak[1])
        component_rows.append(row)
    surface='RESIDUAL' if active_L>EPS_MM else 'CLEAR' if active_U<=EPS_MM else 'UNKNOWN'
    return dict(active_vertex_max_mm=active_vertex_peak,active_surface_bounds_mm=[active_L,active_U],active_surface_state=surface,active_surface_peak=active_peak,
        active_non_target_BVH_pairs=len(active_BVH),active_non_target_BVH_face_pairs=active_BVH,components=component_rows,convex_triangle_queries=convex_queries),certificates

def whole_hand_compare(B,N,supp):
    regressions=[];historical=[]
    for name,sets in supp['digit_pairs'].items():
        b={tuple(x) for x in sets['baseline']};n={tuple(x) for x in sets['corrected']}
        if b:historical.append(dict(kind='DIGIT_CROSSING',pair=name,baseline=len(b),corrected=len(n),new_count=len(n-b)))
        if n-b:regressions.append(dict(kind='NEW_DIGIT_FACE_CROSSING',pair=name,added=sorted(n-b)))
    b={tuple(p) for p in supp['baseline_full_self_pairs']};n={tuple(p) for p in supp['corrected_full_self_pairs']}
    if n-b:regressions.append(dict(kind='NEW_FULL_SKIN_NONINCIDENT_CROSSING',added=sorted(n-b)))
    lb={tuple(p) for p in supp['left_hand_skin_pairs']['baseline']};ln={tuple(p) for p in supp['left_hand_skin_pairs']['corrected']}
    if ln-lb:regressions.append(dict(kind='NEW_RIGHT_LEFT_SKIN_CROSSING',added=sorted(ln-lb)))
    for bc,nc in zip(B['components'],N['components']):
        for region,b in bc['regions'].items():
            if region in ['LITTLE','LITTLE_GT_005']:continue # active correction has its separately reported contract and residual surface risk
            n=nc['regions'][region]
            if n['allowed_target']:continue
            if b['vertex_depth_mm']>.5 or b['surface_lower_mm']>EPS_MM:
                historical.append(dict(kind='NON_TARGET_KEY_EXISTING',region=region,key=bc['key'],component=bc['component'],baseline_vertex_mm=b['vertex_depth_mm'],corrected_vertex_mm=n['vertex_depth_mm'],baseline_surface_mm=[b['surface_lower_mm'],b['surface_upper_mm']],corrected_surface_mm=[n['surface_lower_mm'],n['surface_upper_mm']]))
            if n['vertex_depth_mm']>.5 and n['vertex_depth_mm']>b['vertex_depth_mm']+.02:
                regressions.append(dict(kind='OTHER_REGION_VERTEX_GATE_REGRESSION',region=region,key=bc['key'],baseline_mm=b['vertex_depth_mm'],corrected_mm=n['vertex_depth_mm']))
            if n['surface_lower_mm']>EPS_MM and b['surface_upper_mm']<=EPS_MM:
                regressions.append(dict(kind='NEW_OTHER_REGION_SURFACE_VOLUME_INTRUSION',region=region,key=bc['key'],baseline_upper_mm=b['surface_upper_mm'],corrected_lower_mm=n['surface_lower_mm']))
            elif n['surface_lower_mm']>b['surface_upper_mm']+.02:
                regressions.append(dict(kind='OTHER_REGION_SURFACE_DEPTH_INCREASE',region=region,key=bc['key'],baseline_upper_mm=b['surface_upper_mm'],corrected_lower_mm=n['surface_lower_mm']))
            added=set(map(tuple,n['BVH_face_pairs']))-set(map(tuple,b['BVH_face_pairs']))
            if added:
                regressions.append(dict(kind='OTHER_REGION_NEW_KEY_SURFACE_FACE_PAIRS',region=region,key=bc['key'],added=sorted(added)))
    return dict(result='FAIL' if regressions else 'PASS',regressions=regressions,historical_defects=historical,
        full_self_pairs=dict(baseline=len(b if False else supp['baseline_full_self_pairs']),corrected=len(supp['corrected_full_self_pairs'])),
        left_hand_pairs=dict(baseline=len(lb),corrected=len(ln)))

def run():
    assert read(O/'TOOLCHAIN_PREFLIGHT.json')['pass_']
    C,cm=archive(R2/'ACTUAL_BLENDER_STATIC_SKIN.npz');S,sm=archive(SRC/'SOURCE_LOCAL_STATES.npz');TT,tm=archive(O/'ACTUAL_TRIANGULATION_AND_KEY_CLOCK.npz')
    supp=read(O/'ACTUAL_KEY_AND_BVH_SUPPLEMENT.json');I=read(SRC/'INPUT_BINDINGS.json');P=read(SRC/'POLICY.json');K=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
    assert [P[k] for k in ['contact_horizontal_mm','contact_vertical_abs_mm','wrong_key_depth_mm','nonregression_mm']]==[.03,3.,.5,.02]
    M=read(MODEL/'SOURCE_MODEL_MANIFEST.json');D,dm=archive(MODEL/'SOURCE_MODEL.npz');roi=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json')
    F=M['faces'];W=D['weights'];weight=np.column_stack([W[:,[i for i,n in enumerate(M['bones']) if n.startswith(d+'_')]].sum(1) for d in DIGITS])
    strong={v for r in roi.values() for v in r['vertices']};regions={d:np.array(roi[d]['vertices'],dtype=int) for d in DIGITS}
    regions['PALM_SHARED_WEB']=np.array([i for i in range(3300) if i not in strong]);regions['CROSS_DIGIT_MIXED']=np.flatnonzero((weight>.05).sum(1)>=2);regions['LITTLE_GT_005']=np.flatnonzero(weight[:,4]>.05)
    rows=[];witnesses=[]
    for ix,t in enumerate(TIMES):
        sr=supp['rows'][ix];assert sr['time']==t and np.array_equal(TT['key_angles_'+str(ix)],S['key_angles'][ix])
        owned={}
        for e in I['right_events']:
            if e['note_on']<=t<e['note_off']+.04:owned.setdefault(e['key_index'],set()).add(DIGITS[e['finger']-1])
        owned.setdefault(53,set()).add('LITTLE_GT_005')
        measurements=[];cert=[]
        for which in ['baseline','corrected']:
            V=C[which+'_vertices'][ix];T=TT[which+'_triangles_'+str(ix)];pid=TT[which+'_triangle_polygon_'+str(ix)]
            assert T.shape==(6596,3) and np.all((T>=0)&(T<3300))
            g,proofs=analyze(V,T,pid,F,sr['actual_key_components'],regions,owned,which)
            measurements.append(g);cert.append(proofs)
            print('OFFLINE_DEPTH_DONE',t,which,'queries',g['convex_triangle_queries'],'active',g['active_surface_bounds_mm'],flush=True)
        B,N=measurements;ct=contact(C['corrected_vertices'][ix],K[53],S['key_angles'][ix,53]);bc=contact(C['baseline_vertices'][ix],K[53],S['key_angles'][ix,53]);whole=whole_hand_compare(B,N,sr)
        # Original source_actual contract includes pad, active vertex depth and little/other digit pair counts, not triangle-interior depth.
        little_pairs_nonincrease=all(len(v['corrected'])<=len(v['baseline']) for k,v in sr['digit_pairs'].items() if 'LITTLE' in k)
        original='PASS' if ct['pass_'] and N['active_vertex_max_mm']<=.5 and little_pairs_nonincrease else 'FAIL'
        row=dict(time=t,D5_contact=ct,baseline_D5_contact=bc,ORIGINAL_STATIC_CONTRACT=original,REAL_SURFACE_PENETRATION=N['active_surface_state'],NO_NEW_WHOLE_HAND_REGRESSION=whole['result'],
            baseline=B,corrected=N,whole_hand=whole,original_little_digit_pair_nonincrease=little_pairs_nonincrease)
        rows.append(row)
        dump('POSE_GEOMETRY_'+str(ix)+'.json',row)
        dump('TRIANGLE_DEPTH_CERTIFICATES_'+str(ix)+'.json',dict(time=t,baseline=cert[0],corrected=cert[1],definition='max over triangle points of max(0,min_i(h_i-n_i.p)); meters converted to mm; unit outward planes per convex component',
            proof='Enumerated primal constraint vertices plus nonnegative dual upper certificates; full simplex, no finite sampling claim',roundoff_scope='Cached float vertices and actual convex planes; per-query lower/upper gap recorded',optimizer_calls=0))
    original='FAIL' if any(r['ORIGINAL_STATIC_CONTRACT']=='FAIL' for r in rows) else 'PASS'
    whole='FAIL' if any(r['NO_NEW_WHOLE_HAND_REGRESSION']=='FAIL' for r in rows) else 'PASS'
    surface='UNKNOWN' if any(r['REAL_SURFACE_PENETRATION']=='UNKNOWN' for r in rows) else 'RESIDUAL' if any(r['REAL_SURFACE_PENETRATION']=='RESIDUAL' for r in rows) else 'CLEAR'
    result='STATIC_GEOMETRY_FAIL' if original=='FAIL' or whole=='FAIL' else 'INCONCLUSIVE' if surface=='UNKNOWN' else 'STATIC_GEOMETRY_CLOSED'
    dump('FINAL_GEOMETRY_RESULT.json',dict(RESULT=result,ORIGINAL_STATIC_CONTRACT=original,REAL_SURFACE_PENETRATION=surface,NO_NEW_WHOLE_HAND_REGRESSION=whole,
        rows=[dict(time=r['time'],D5_contact=r['D5_contact'],baseline_vertex_mm=r['baseline']['active_vertex_max_mm'],corrected_vertex_mm=r['corrected']['active_vertex_max_mm'],baseline_surface_bounds_mm=r['baseline']['active_surface_bounds_mm'],corrected_surface_bounds_mm=r['corrected']['active_surface_bounds_mm'],baseline_BVH=r['baseline']['active_non_target_BVH_pairs'],corrected_BVH=r['corrected']['active_non_target_BVH_pairs'],
            ORIGINAL_STATIC_CONTRACT=r['ORIGINAL_STATIC_CONTRACT'],REAL_SURFACE_PENETRATION=r['REAL_SURFACE_PENETRATION'],NO_NEW_WHOLE_HAND_REGRESSION=r['NO_NEW_WHOLE_HAND_REGRESSION'],regressions=r['whole_hand']['regressions']) for r in rows],
        corrected_poses_generated_or_applied=0,optimizer_calls=0,DYNAMIC_RECOMPOSITION='NOT_EXECUTED',HUMAN_NATURALNESS='NOT_TESTED',STOP='HUMAN REVIEW'))
    snapshot('OFFLINE_INPUT_SHA.json')
    print('FINAL_GEOMETRY_RESULT',result,original,surface,whole,flush=True)

if __name__=='__main__':
    try:run()
    except BaseException:
        import traceback
        dump('OFFLINE_DIAGNOSTIC_FAILURE.json',dict(error=traceback.format_exc()))
        raise
