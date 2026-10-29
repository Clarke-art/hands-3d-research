"""Continuous event-window constraints over existing frozen FK.

Unknowns are shared wrist translation/rotation, all digits, and playable contact
locations. No fixed root trajectory or piece/note-name conditional pose table.
"""
from stage_common import *
if 'bpy' not in sys.modules:
    from scipy.optimize import least_squares
    from scipy.interpolate import PchipInterpolator
    from scipy.sparse import lil_matrix

HAND='L'
NEUTRAL=np.degrees((o.qanchor('L1')+o.qanchor('L2'))/2);BASE,RBASE=o.root(HAND)
NEUTRAL_PADS=np.array([c.fk(HAND,d,np.radians(NEUTRAL[j]))[0]@RBASE.T+BASE for j,d in enumerate(c.DIGITS)])
B=np.array([o.SP['joint_increment_bounds_deg']['THUMB' if j==0 else 'LONG'] for j in range(5)])
def rotations(a,axis):
    axis=np.array(axis,dtype=float);axis/=np.linalg.norm(axis);x,y,z=axis
    K=np.array([[0,-z,y],[z,0,-x],[-y,x,0.]])
    a=np.asarray(a);return np.eye(3)+np.sin(a)[...,None,None]*K+(1-np.cos(a))[...,None,None]*(K@K)
def extra_rotation(deg):
    a=np.radians(np.asarray(deg))
    return rotations(a[...,2],[0,0,1])@rotations(a[...,1],[0,1,0])@rotations(a[...,0],[1,0,0])
def fk_batch(states):
    st=np.atleast_2d(states);q=np.radians(st[:,6:].reshape(-1,5,4));points=[];jointpoints=[]
    for j,d in enumerate(c.DIGITS):
        names,rels,axes,spread,pad=c.SETUPS[HAND,d];M=np.tile(np.eye(4),(len(st),1,1));js=[]
        for k in range(3):
            M=M@rels[k];js.append(M[:,:3,3].copy());rot=rotations(q[:,j,k],axes[k])
            if k==0:rot=rotations(q[:,j,3],spread)@rot
            J=np.tile(np.eye(4),(len(st),1,1));J[:,:3,:3]=rot;M=M@J
        points.append(np.einsum('kij,j->ki',M,pad)[:,:3]);jointpoints.append(np.stack(js,1))
    pts=np.stack(points,1);jointpoints=np.stack(jointpoints,1)
    RR=extra_rotation(st[:,3:6])@RBASE;root=BASE+st[:,:3]/1000
    return np.einsum('kij,kdj->kdi',RR,pts)+root[:,None,:],np.einsum('kij,kdbj->kdbi',RR,jointpoints)+root[:,None,None,:]

class BaseEventCoordinator:
    def __init__(self,events,policy):
        self.events=sorted(events,key=lambda n:n['note_on']);self.policy=policy
        self.keys={k['midi_note']:k for k in c.KEYS};self.repeats={}
        if not self.events:raise ValueError('empty chord/event set')
        for n in self.events:
            if n['hand']!=HAND or not 1<=n['finger']<=5 or n['midi_note'] not in self.keys or n['note_off']<=n['note_on']:
                raise ValueError('invalid left-hand target, finger, or event')
        for i,a in enumerate(self.events):
            for b in self.events[i+1:]:
                if a['finger']==b['finger'] and max(a['note_on'],b['note_on'])<min(a['note_off'],b['note_off']):
                    raise ValueError('overlapping targets assigned to the same finger')
        self.onset_groups={t:[n['note_id'] for n in self.events if n['note_on']==t] for t in sorted(set(n['note_on'] for n in self.events))}
        self.bounds=B.copy()
        used={n['finger'] for n in self.events}
        for finger,label in [(2,'LEFT_IDLE_INDEX'),(4,'LEFT_IDLE_RING')]:
            if finger not in used:self.bounds[finger-1]=np.array(o.SP['joint_increment_bounds_deg'][label])
        for a,b in zip(self.events,self.events[1:]):
            if a['midi_note']==b['midi_note'] and 0<=b['note_on']-a['note_off']<.07:
                self.repeats[a['note_id']]=b
        self.surfaces=[];self.xy_seed=[];self.xy_low=[];self.xy_high=[]
        for n in self.events:
            k=self.keys[n['midi_note']];s=k['key_top_playable_surface'][0]
            inset=[.003,.007] if k['color']=='WHITE' else [.002,.002]
            lo=np.array([s['xmin'],s['ymin']])+inset;hi=np.array([s['xmax'],s['ymax']])-inset
            y=np.clip(NEUTRAL_PADS[n['finger']-1,1],lo[1],hi[1])
            self.surfaces.append(s);self.xy_low.append(lo*1000);self.xy_high.append(hi*1000)
            self.xy_seed.append(np.array([k['key_center'][0],y])*1000)
        self.xy_seed=np.array(self.xy_seed);self.xy_low=np.array(self.xy_low);self.xy_high=np.array(self.xy_high)
        offsets=[self.keys[n['midi_note']]['key_center'][0]-NEUTRAL_PADS[n['finger']-1,0] for n in self.events]
        yoffsets=[self.xy_seed[i,1]/1000-NEUTRAL_PADS[n['finger']-1,1] for i,n in enumerate(self.events)]
        self.state_low=np.r_[[min(offsets)*1000-45,min(yoffsets)*1000-25,-16],[-8,-8,-12],self.bounds[:,0].ravel()]
        self.state_high=np.r_[[max(offsets)*1000+45,max(yoffsets)*1000+25,12],[8,8,12],self.bounds[:,1].ravel()]
        self.nominal=np.r_[[np.median(offsets)*1000,np.mean(yoffsets)*1000,-6],[0,0,0],NEUTRAL.ravel()]
        self.boxlo=[];self.boxhi=[];self.boxkeys=[]
        for k in c.KEYS:
            if min(n['midi_note'] for n in self.events)-3<=k['midi_note']<=max(n['midi_note'] for n in self.events)+3:
                for g in k['geometry']:
                    self.boxlo.append(np.array(g['vertices']).min(0));self.boxhi.append(np.array(g['vertices']).max(0));self.boxkeys.append(k['midi_note'])
        self.boxlo=np.array(self.boxlo);self.boxhi=np.array(self.boxhi)

    def pressure(self,n,t):
        on,off=n['note_on'],n['note_off'];nxt=self.repeats.get(n['note_id'])
        # Partial release BEFORE the next strike's exact original event time;
        # NOTE_ON/OFF/audio events themselves are not edited.
        if nxt is not None:
            nexton=nxt['note_on'];reset=self.policy['repeat_reset_sec'];floor=self.policy['repeat_reset_pressure']
            if off-reset<=t<nexton:
                return 1-(1-floor)*float(c.smooth((t-(off-reset))/(nexton-(off-reset))))
            if t>=nexton:return 0.
        previous=next((a for a in self.events if self.repeats.get(a['note_id'],{}).get('note_id')==n['note_id']),None)
        if previous is not None and on<=t<on+.035:
            return self.policy['repeat_reset_pressure']+(1-self.policy['repeat_reset_pressure'])*float(c.smooth((t-on)/.035))
        return c.keypress(n,t)

    def key_angles(self,t):
        result=np.zeros(88)
        # Latest note owns that key's mechanical state; no max(old,new) merge.
        for midi in sorted(set(n['midi_note'] for n in self.events)):
            ns=[n for n in self.events if n['midi_note']==midi and n['note_on']<=t+1e-10]
            if ns:result[midi-21]=self.pressure(ns[-1],t)*self.keys[midi]['press_angle_rad']
        return result

    def target(self,idx,xy,t,lift=0):
        n=self.events[idx];k=self.keys[n['midi_note']];surf=self.surfaces[idx]
        point=np.r_[xy[idx]/1000,surf['z']+.0005]
        pivot=np.array(k['press_pivot']);angle=self.key_angles(t)[n['key_index']]
        point=c.axisrot(angle,k['press_axis'])@(point-pivot)+pivot
        point[2]+=lift;return point

    def tasks(self,t):
        tasks=[]
        for j in range(5):
            ns=[(i,n) for i,n in enumerate(self.events) if n['finger']==j+1]
            active=[(i,n) for i,n in ns if n['note_on']<=t+1e-10 and t<n['note_off']-1e-10]
            releasing=[(i,n) for i,n in ns if n['note_off']<=t+1e-10 and t<n['note_off']+self.policy['finger_release_follow_sec']]
            future=[(i,n) for i,n in ns if t<n['note_on'] and n['note_on']-self.policy['prepare_sec']<=t]
            if active:
                i,n=active[-1];tasks.append((j,i,0.,self.policy['contact_weight']))
            elif releasing:
                i,n=releasing[-1];u=(t-n['note_off'])/self.policy['finger_release_follow_sec']
                tasks.append((j,i,.002*c.smooth(u),self.policy['contact_weight']*(1-.3*c.smooth(u))))
            elif any(n['note_off']+self.policy['finger_release_follow_sec']<=t<n['note_off']+self.policy['recovery_sec'] for i,n in ns):
                i,n=next((i,n) for i,n in reversed(ns) if n['note_off']+self.policy['finger_release_follow_sec']<=t<n['note_off']+self.policy['recovery_sec'])
                u=float(c.smooth((t-n['note_off']-self.policy['finger_release_follow_sec'])/(self.policy['recovery_sec']-self.policy['finger_release_follow_sec'])))
                tasks.append((j,i,.002+.008*u,2*(1-u)))
            elif future:
                i,n=future[0];u=float(c.smooth((t-n['note_on']+self.policy['prepare_sec'])/self.policy['prepare_sec']))
                descent=float(c.smooth((t-n['note_on']+.075)/.075))
                tasks.append((j,i,.009*(1-descent),self.policy['prepare_weight']*u))
        return tasks

    def pose_residual(self,state,xy,t,tasks=None):
        pads,joints=fk_batch(state);pads=pads[0];joints=joints[0];out=[]
        tasks=self.tasks(t) if tasks is None else tasks;assigned=set()
        for j,i,lift,weight in tasks:
            assigned.add(j);out.extend((pads[j]-self.target(i,xy,t,lift))*1000*weight)
        # Finite proxy: all pads avoid stationary key volumes; active finger may
        # touch its own moving key. No mesh/rig or per-vertex repair.
        for j in range(5):
            activekeys=[self.events[i]['midi_note'] for jj,i,l,w in tasks if jj==j and w>1]
            lo=self.boxlo;hi=self.boxhi;angles=self.key_angles(t);vv=[]
            for midi in self.boxkeys:
                pivot=np.array(self.keys[midi]['press_pivot']);inv=c.axisrot(-angles[midi-21],[1,0,0]);vv.append(inv@(pads[j]-pivot)+pivot)
            vv=np.array(vv);d=np.abs(vv-(lo+hi)/2)-(hi-lo)/2
            sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0)
            margin=np.array([0 if k in activekeys else .003 for k in self.boxkeys])
            out.extend(np.maximum(margin-sdf,0)*1000*self.policy['clearance_weight'])
            if j not in assigned:
                out.append(max(0,.005-pads[j,2])*1000*2)
            # DIP/proximal joint centres must remain above the highest local key
            # surface; low weight, an engineering proxy, not collision proof.
            for point in joints[j,1:]:
                covers=(point[0]>lo[:,0])&(point[0]<hi[:,0])&(point[1]>lo[:,1])&(point[1]<hi[:,1])
                top=float(np.max(hi[covers,2])) if np.any(covers) else -.010
                out.append(max(0,top+.005-point[2])*1000*.5)
        out.extend((state[6:]-NEUTRAL.ravel())*self.policy['joint_prior_weight'])
        out.extend(state[3:6]*.20)
        out.extend((state[:3]-self.nominal[:3])*np.array([.015,.035,.06]))
        return np.array(out)

    def static_solve(self,t,tasks=None,seed=None):
        tasks=self.tasks(t) if tasks is None else tasks
        if seed is None:
            seed=self.nominal.copy()
            if tasks:
                offsets=[self.keys[self.events[i]['midi_note']]['key_center'][0]-NEUTRAL_PADS[j,0] for j,i,l,w in tasks]
                seed[0]=np.mean(offsets)*1000
        N=len(self.events);initial=np.r_[seed,self.xy_seed.ravel()];lower=np.r_[self.state_low,self.xy_low.ravel()];upper=np.r_[self.state_high,self.xy_high.ravel()]
        def res(x):return np.r_[self.pose_residual(x[:26],x[26:].reshape(N,2),t,tasks),(x[26:]-self.xy_seed.ravel())*.12]
        fit=least_squares(res,np.clip(initial,lower+1e-7,upper-1e-7),bounds=(lower,upper),max_nfev=100,ftol=1e-6,xtol=1e-6,gtol=1e-6)
        return fit

DEFAULT_POLICY=dict(prepare_sec=.18,finger_release_follow_sec=.07,recovery_sec=.32,repeat_reset_sec=.045,
    repeat_reset_pressure=.42,contact_weight=6.,prepare_weight=4.,clearance_weight=2.,
    joint_prior_weight=.055,velocity_weights=[.010,.018,.028,.040],
    acceleration_weights=[.00032,.00048,.00072,.00060],
    max_trajectory_nfev=75,global_time_unchanged=True,candidate_limit=1,
    motion_method='Stage A R2 banded wrist/digit/contact framework adapted to actual left FK and concurrent chord tasks; common C1 bake',
    frozen_joint_bounds_unchanged=True,contact_location_optimized_inside_real_surface=True,
    no_per_pitch_special_rules=True,chord_events_same_finger_conflicts_rejected=True,endpoint_prepared_return_weight=.20)
