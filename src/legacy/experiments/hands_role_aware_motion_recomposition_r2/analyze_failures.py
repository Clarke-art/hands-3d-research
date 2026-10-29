from bootstrap import *
from representation import Representation
from depth_math import max_triangle_depth,planes_from_mesh
from scipy.interpolate import CubicHermiteSpline
import model as n
r=Representation();G=read(O/'DYNAMIC_BLENDER_GEOMETRY.json');C,_=archive(O/'CANDIDATE_ACTUAL_SKIN.npz');B,_=archive(O/'TARGET_C1_POSTHOC_REFERENCE.npz');K,_=archive(O/'CONTINUOUS_CURVE.npz');M,_=archive(O/'MOTION_CANDIDATE.npz')
times=C['times'];rows=G['rows'];base=G['baseline_rows'];curve=CubicHermiteSpline(K['knots'],K['q_deg'],K['dq_deg_s'],axis=0)
# Exact velocity extrema of each cubic Hermite segment; endpoints included.
vmax=0.;vtime=None;vdigit=None;vjoint=None
for i,dt in enumerate(np.diff(K['knots'])):
    coeff=curve.c[:,i]
    for j in range(5):
        for k in range(4):
            a,b,c0=coeff[0,j,k],coeff[1,j,k],coeff[2,j,k];test=[0.,dt]
            if abs(a)>1e-14:
                root=-b/(3*a)
                if 0<root<dt:test.append(root)
            for u in test:
                v=abs(3*a*u*u+2*b*u+c0)
                if v>vmax:vmax=float(v);vtime=float(K['knots'][i]+u);vdigit=n.DIGITS[j];vjoint=k
Q=M['q_deg'];vel=np.diff(Q,axis=0)/np.diff(times)[:,None,None];bv=np.diff(B['q_deg'],axis=0)/np.diff(times)[:,None,None]
wrist=np.einsum('kij,j->ki',M['rig_world'],np.r_[n.REST[0,:3,3],1])[:,:3];basewrist=np.einsum('kij,j->ki',B['rig_world'],np.r_[n.REST[0,:3,3],1])[:,:3]
wspeed=np.linalg.norm(np.diff(wrist,axis=0),axis=1)/np.diff(times)*1000;bspeed=np.linalg.norm(np.diff(basewrist,axis=0),axis=1)/np.diff(times)*1000
role_rows=[]
for ix,t in enumerate(times):
    for j,eidx,lift,weight in r.roles(t):
        e=r.events[eidx];key=n.KEYS[e['key_index']];pv=np.array(key['press_pivot']);angle=C['key_angles'][ix,e['key_index']]
        p=n.rot(-angle,key['press_axis'])@(C['vertices'][ix,n.PADIDS[j]]-pv)+pv
        surf=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
        miss=float(np.linalg.norm(p[:2]-np.clip(p[:2],[surf['xmin'],surf['ymin']],[surf['xmax'],surf['ymax']]))*1000)
        gap=float((p[2]-surf['z'])*1000);expected=.5+lift*1000*np.cos(angle)
        role='ACTIVE' if e['note_on']<=t<e['note_off'] else 'RELEASING' if t>=e['note_off'] else 'PREPARING'
        role_rows.append(dict(time=float(t),event=e['note_id'],digit=n.DIGITS[j],role=role,horizontal_outside_mm=miss,key_normal_gap_mm=gap,task_height_error_mm=gap-expected))
newreg=[]
for ix,(row,ref) in enumerate(zip(rows,base)):
    if row['non_target_vertex_peak_mm']>ref['non_target_vertex_peak_mm']+.02:
        newreg.append(dict(time=row['time'],kind='NON_TARGET_VERTEX_DEPTH_INCREASE',baseline_mm=ref['non_target_vertex_peak_mm'],candidate_mm=row['non_target_vertex_peak_mm']))
    for pair,num in row['finger_pairs'].items():
        if num>ref['finger_pairs'][pair]:newreg.append(dict(time=row['time'],kind='FINGER_CROSSING_COUNT_INCREASE',pair=pair,baseline=ref['finger_pairs'][pair],candidate=num))
# Deterministic real triangle witnesses: worst depth, first/last/phase boundaries,
# first target contact failure, and largest horizontal miss. The whole 240-frame
# vertex/BVH screen is already failed; these are surface witnesses, not a claim
# of a global continuous maximum.
contacts=[c for row in rows for c in row['contacts']];indices={0,len(times)-1,int(np.argmax([x['non_target_vertex_peak_mm'] for x in rows]))}
bad=[c for c in contacts if not c['pass_']]
for event in ['R11','R12','R13','R14']:
    cs=[c for c in contacts if c['event']==event and not c['pass_']]
    if cs:indices.add(int(np.argmin(abs(times-cs[0]['time']))))
worsth=max(contacts,key=lambda c:c['horizontal_mm']);indices.add(int(np.argmin(abs(times-worsth['time']))))
for e in r.target:
    for t in [e['note_on'],e['note_on']+.035,e['note_off'],e['note_off']+.04]:
        if r.start<=t<=r.end:indices.add(int(np.argmin(abs(times-t))))
surface=[]
for ix in sorted(indices):
    t=float(times[ix]);owned={}
    for e in r.events:
        if e['note_on']<=t<e['note_off']+.04:owned.setdefault(e['key_index'],set()).add(e['finger']-1)
    result=dict(time=t)
    for label,Z in [('baseline',B),('candidate',C)]:
        V=Z['actual_vertices'][ix] if label=='baseline' else Z['vertices'][ix];T=Z['triangles'][ix];tv=V[T];lo=tv.min(1);hi=tv.max(1);angles=Z['key_angles'][ix]
        peakL=0.;peakU=0.;peak=None;count=0;activeL=0.;activeU=0.;certs=[]
        for key,g,_ in n.COMPONENTS:
            ki=key['key_index'];pv=np.array(key['press_pivot']);R=n.rot(angles[ki],key['press_axis']);kv=(np.array(g['vertices'])-pv)@R.T+pv;pl,_=planes_from_mesh(kv,np.array(g['triangles']).reshape(-1,3).tolist())
            ids=np.flatnonzero(np.all(hi>=kv.min(0)-1e-10,axis=1)&np.all(lo<=kv.max(0)+1e-10,axis=1))
            allowed=set()
            for j in owned.get(ki,set()):allowed.update(n.ROIS[n.DIGITS[j]]['vertices'])
            for ti in ids:
                if all(int(v) in allowed for v in T[ti]):continue
                proof=max_triangle_depth(tv[ti],pl);count+=1
                if proof['upper_mm']<=1e-6:continue
                rec=dict(key=key['note_name'],component=g['name'],triangle=int(ti),skin_vertices=T[ti],**proof);certs.append(rec)
                peakL=max(peakL,proof['lower_mm']);peakU=max(peakU,proof['upper_mm'])
                if peak is None or rec['lower_mm']>peak['lower_mm']:peak=rec
                for e in r.events:
                    j=e['finger']-1
                    if e['note_on']<=t<e['note_off'] and ki!=e['key_index'] and any(int(v) in set(n.ROIS[n.DIGITS[j]]['vertices']) for v in T[ti]):
                        activeL=max(activeL,proof['lower_mm']);activeU=max(activeU,proof['upper_mm'])
        result[label]=dict(non_target_surface_bounds_mm=[peakL,peakU],active_surface_bounds_mm=[activeL,activeU],peak=peak,triangle_queries=count)
        atomic_json('SURFACE_WITNESS_'+str(ix)+'_'+label+'.json',dict(time=t,certificates=certs,scope='Selected post-failure phase/worst samples, whole surface versus all 88 moving registered keys verified against actual geometry',global_dynamic_max_claim=False))
    surface.append(result);print('REAL_SURFACE_WITNESS',t,result['candidate']['non_target_surface_bounds_mm'],flush=True)
atomic_json('CONTINUITY_AND_ROLE_DIAGNOSTICS.json',dict(exact_Hermite_joint_speed_peak_deg_s=vmax,speed_peak_time=vtime,speed_peak_digit=vdigit,speed_peak_joint_index=vjoint,
    candidate_sample_joint_speed_peak_deg_s=float(abs(vel).max()),baseline_sample_joint_speed_peak_deg_s=float(abs(bv).max()),candidate_wrist_speed_peak_mm_s=float(wspeed.max()),baseline_wrist_speed_peak_mm_s=float(bspeed.max()),
    endpoint_q_and_velocity_connected=True,wrist_boundary_positions_connected=True,roles=role_rows,prepare_release_follow_errors_reported=True,math_C1_not_safe_motion=True))
atomic_json('FAILURE_AND_SURFACE_SUMMARY.json',dict(surface_witnesses=surface,whole_hand_new_regression_records=newreg,whole_hand_new_regression_count=len(newreg),
    first_contact_failure=bad[0],first_core_target_failure=next((c for c in bad if c['event'] in ['R12','R13']),None),largest_horizontal_miss=worsth,
    surface_depth_lower_bound_for_dynamic_risk_mm=max(s['candidate']['non_target_surface_bounds_mm'][0] for s in surface),
    sampling_limit='Whole vertex and BVH screen at all 240 samples; exact triangle depth at selected failure/phase samples. No continuous interval proof or global face-depth maximum asserted',
    geometry_failure_did_not_trigger_any_motion_rerun=True))
protect();print('FAILURE_ANALYSIS_COMPLETE',len(newreg),'regressions',flush=True)
