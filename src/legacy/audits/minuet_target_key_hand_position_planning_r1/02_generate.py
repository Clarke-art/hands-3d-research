from stage_common import *
from target_key_planner import TargetKeyPlanner
from scipy.optimize import least_squares
import time
assert not (P/'CANDIDATE_ATTEMPT.json').exists(), 'ONE NEW CANDIDATE ONLY'
lock=read(P/'PLANNING_LOCK.json')
assert all(sha(P/n)==h for n,h in lock['scripts'].items())
assert sha(P/'GENERATION_POLICY.json')==lock['policy_sha256']
assert sha(P/'TARGET_KEY_AND_ROOT_PLAN.json')==lock['plan_sha256']
dump('CANDIDATE_ATTEMPT.json',dict(attempt=1,restarts=0,status='STARTED',input_lock=lock['input_sha256']))
tl=read(P/'PERFORMANCE_TIMELINE.json');pol=read(P/'GENERATION_POLICY.json');plan=read(P/'TARGET_KEY_AND_ROOT_PLAN.json')
planner=TargetKeyPlanner(c.KEYS,o.ANCHORS,'R');neutral=o.qanchor('R1');base,R=o.root('R')
B=np.array([np.radians(pol['joint_bounds_deg']['THUMB' if j==0 else 'LONG']) for j in range(5)])
events=tl['notes'];byfinger={j:[n for n in events if n['finger']==j+1] for j in range(5)}
end=tl['presentation_duration_sec'];grid=np.arange(0,np.ceil(end*120)+1)/120
# Include source NOTE_ON/OFF and full travel instants exactly in the bake.
times=np.unique(np.r_[grid,[n[p]+dt for n in events for p in ['note_on','note_off'] for dt in [0,.035,.07]]])
times=times[times<=grid[-1]+1e-9]
Q=[];D=[];KA=[];previous=neutral.copy();calls=0;start=time.monotonic();residuals=[]
def worldpad(j,q,delta): return c.fk('R',c.DIGITS[j],q)[0]@R.T+base+delta
for i,t in enumerate(times):
    delta=planner.root_at(plan,float(t));q=previous.copy();angles=np.zeros(88)
    for n in events:
        angles[n['key_index']]=max(angles[n['key_index']],c.keypress(n,t)*c.KEYS[n['key_index']]['press_angle_rad'])
    for j in range(5):
        ns=byfinger[j];active=[n for n in ns if n['note_on']<=t+1e-10 and t<n['note_off']-1e-10]
        release=[n for n in ns if n['note_off']<=t+1e-10 and t<n['note_off']+.07]
        upcoming=[n for n in ns if t<n['note_on'] and n['note_on']-.10<=t]
        if active: n=active[-1];goal=planner.moving_target(plan['key_targets'][n['note_id']],angles[n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad']);phase='CONTACT_HOLD'
        elif release:
            n=release[-1];goal=planner.moving_target(plan['key_targets'][n['note_id']],angles[n['key_index']]/c.KEYS[n['key_index']]['press_angle_rad']);phase='RELEASE'
        elif upcoming:
            n=upcoming[0];u=c.smooth((t-n['note_on']+.10)/.10)
            target=np.array(plan['key_targets'][n['note_id']]['unpressed_pad_xyz'])
            ready=worldpad(j,neutral[j],delta)
            goal=ready*(1-u)+target*u;goal[2]+=.003*np.sin(np.pi*u);phase='APPROACH'
        else:
            dt=times[i]-times[i-1] if i else 1/120
            q[j]=previous[j]+np.clip(neutral[j]-previous[j],-np.radians(180)*dt,np.radians(180)*dt)
            continue
        def residual(x):
            return np.r_[(worldpad(j,x,delta)-goal)*1000*pol['contact_weight_mm'],
                (x-neutral[j])*pol['joint_prior_weight_rad'],
                (x-previous[j])*pol['joint_temporal_weight_rad']]
        fit=least_squares(residual,np.clip(previous[j],B[j,0]+1e-9,B[j,1]-1e-9),
            bounds=(B[j,0],B[j,1]),max_nfev=pol['joint_solver_max_nfev'],ftol=1e-7,xtol=1e-7,gtol=1e-7)
        q[j]=fit.x;calls+=1
        if active: residuals.append(dict(note_id=n['note_id'],t=float(t),gap_to_goal_mm=float(np.linalg.norm(worldpad(j,q[j],delta)-goal)*1000)))
    assert np.isfinite(q).all();Q.append(q);D.append(delta);KA.append(angles);previous=q
    if i%120==0:print('SINGLE_CANDIDATE_BAKE_SAMPLE',i,'/',len(times),flush=True)
np.savez_compressed(P/'motion.npz',times=times,R_q=Q,R_delta=D,key_angles=KA)
dump('MOTION_GENERATION.json',dict(candidate_count=1,restarts=0,samples=len(times),
    independent_target_solves=calls,elapsed_sec=time.monotonic()-start,
    motion_sha256=sha(P/'motion.npz'),events=16,actions_baked=False,left_generated=False,
    no_manual_per_note_pose=True,no_post_smoothing=True,exact_event_instants_in_bake=True,
    solver_contact_error_max_mm=max(r['gap_to_goal_mm'] for r in residuals),
    root_segment_count=len(plan['segments']),per_sample_contact_residuals=residuals))
print('ONE_MOTION_COMPLETE',len(times),max(r['gap_to_goal_mm'] for r in residuals),flush=True)
