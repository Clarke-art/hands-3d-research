"""Continuous left event handoff over Stage B R1's actual left-hand kernel.

Holding targets stay exact. Only released/preparing targets can be blended.
No pitch-specific pose branches or right-hand trajectory mirroring.
"""
from left_chord_base import *
BASE_POLICY=DEFAULT_POLICY.copy()
DEFAULT_POLICY=dict(BASE_POLICY,idle_domain_weight=.30,
    motion_method='Concurrent left contacts + continuous release-to-preparation target handoff, jointly solved with wrist/digits',
    recovery_to_future_blend=True)

class EventCoordinator(BaseEventCoordinator):
    def task_components(self,t):
        result=[]
        for j in range(5):
            ns=[(i,n) for i,n in enumerate(self.events) if n['finger']==j+1]
            active=[(i,n) for i,n in ns if n['note_on']<=t+1e-10 and t<n['note_off']-1e-10]
            old=[(i,n) for i,n in ns if n['note_off']<=t+1e-10]
            future=[(i,n) for i,n in ns if t<n['note_on'] and n['note_on']-self.policy['prepare_sec']<=t]
            if active:
                i,n=active[-1];result.append(dict(finger=j,weight=self.policy['contact_weight'],components=[(i,0.,1.)],phase='HOLD_OR_PRESS'));continue
            previous=old[-1] if old else None;released=None
            if previous:
                i,n=previous;elapsed=t-n['note_off']
                if elapsed<self.policy['finger_release_follow_sec']:
                    u=float(c.smooth(elapsed/self.policy['finger_release_follow_sec']))
                    released=dict(finger=j,weight=self.policy['contact_weight']*(1-.3*u),components=[(i,.002*u,1.)],phase='RELEASE')
                elif elapsed<self.policy['recovery_sec']:
                    u=float(c.smooth((elapsed-self.policy['finger_release_follow_sec'])/(self.policy['recovery_sec']-self.policy['finger_release_follow_sec'])))
                    released=dict(finger=j,weight=2*(1-u),components=[(i,.002+.008*u,1.)],phase='RECOVERY')
            prepared=None
            if future:
                i,n=future[0];u=float(c.smooth((t-n['note_on']+self.policy['prepare_sec'])/self.policy['prepare_sec']))
                descent=float(c.smooth((t-n['note_on']+.075)/.075))
                prepared=dict(finger=j,weight=self.policy['prepare_weight']*u,components=[(i,.009*(1-descent),1.)],phase='PREPARATION')
            if released and prepared:
                pi,pn=previous;ni,nn=future[0]
                start=max(nn['note_on']-self.policy['prepare_sec'],pn['note_off'])
                end=min(pn['note_off']+self.policy['recovery_sec'],nn['note_on'])
                b=float(c.smooth((t-start)/max(end-start,1e-8)))
                components=[(i,lift,factor*(1-b)) for i,lift,factor in released['components']]+[(i,lift,factor*b) for i,lift,factor in prepared['components']]
                result.append(dict(finger=j,weight=released['weight']*(1-b)+prepared['weight']*b,
                    components=components,phase='RELEASE_TO_NEXT_PREPARATION'))
            elif released:result.append(released)
            elif prepared:result.append(prepared)
        return result

    def tasks(self,t):
        # Compatibility summary; the actual solve uses all target components.
        return [(r['finger'],*max(r['components'],key=lambda x:x[2])[:2],r['weight']) for r in self.task_components(t)]

    def pose_residual(self,state,xy,t,tasks=None):
        pads,joints=fk_batch(state);pads=pads[0];joints=joints[0];out=[]
        descriptors=self.task_components(t) if tasks is None else [dict(finger=j,weight=w,components=[(i,lift,1.)]) for j,i,lift,w in tasks]
        assigned=set();weights=np.zeros(5)
        for r in descriptors:
            j=r['finger'];assigned.add(j);weights[j]=r['weight']
            goal=sum(self.target(i,xy,t,lift)*factor for i,lift,factor in r['components'])
            out.extend((pads[j]-goal)*1000*r['weight'])
        lo,hi=self.boxlo,self.boxhi;angles=self.key_angles(t)
        for j in range(5):
            activekeys=[self.events[i]['midi_note'] for r in descriptors if r['finger']==j and r['weight']>1 for i,lift,factor in r['components'] if factor>.1]
            vv=[]
            for midi in self.boxkeys:
                pivot=np.array(self.keys[midi]['press_pivot']);vv.append(c.axisrot(-angles[midi-21],[1,0,0])@(pads[j]-pivot)+pivot)
            vv=np.array(vv);d=np.abs(vv-(lo+hi)/2)-(hi-lo)/2
            sdf=np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0)
            margin=np.array([0 if k in activekeys else .003 for k in self.boxkeys])
            out.extend(np.maximum(margin-sdf,0)*1000*self.policy['clearance_weight'])
            if j not in assigned:out.append(max(0,.005-pads[j,2])*1000*2)
            for point in joints[j,1:]:
                covers=(point[0]>lo[:,0])&(point[0]<hi[:,0])&(point[1]>lo[:,1])&(point[1]<hi[:,1])
                top=float(np.max(hi[covers,2])) if np.any(covers) else -.010
                out.append(max(0,top+.005-point[2])*1000*.5)
        q=state[6:].reshape(5,4)
        for j,label in [(1,'LEFT_IDLE_INDEX'),(3,'LEFT_IDLE_RING')]:
            limits=np.array(o.SP['joint_increment_bounds_deg'][label]);idle=1-float(np.clip(weights[j]/self.policy['prepare_weight'],0,1))
            out.extend((np.maximum(limits[0]-q[j],0)+np.maximum(q[j]-limits[1],0))*idle*self.policy['idle_domain_weight'])
        out.extend((state[6:]-NEUTRAL.ravel())*self.policy['joint_prior_weight']);out.extend(state[3:6]*.20)
        out.extend((state[:3]-self.nominal[:3])*[.015,.035,.06]);return np.array(out)

    def static_solve(self,t,tasks=None,seed=None):
        summary=self.tasks(t) if tasks is None else tasks
        if seed is None:
            seed=self.nominal.copy()
            if summary:seed[0]=np.mean([self.keys[self.events[i]['midi_note']]['key_center'][0]-NEUTRAL_PADS[j,0] for j,i,l,w in summary])*1000
        N=len(self.events);initial=np.r_[seed,self.xy_seed.ravel()];lower=np.r_[self.state_low,self.xy_low.ravel()];upper=np.r_[self.state_high,self.xy_high.ravel()]
        fit=least_squares(lambda x:np.r_[self.pose_residual(x[:26],x[26:].reshape(N,2),t,tasks),(x[26:]-self.xy_seed.ravel())*.12],
            np.clip(initial,lower+1e-7,upper-1e-7),bounds=(lower,upper),max_nfev=100,ftol=1e-6,xtol=1e-6,gtol=1e-6)
        return fit
