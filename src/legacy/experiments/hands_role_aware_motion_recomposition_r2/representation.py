from bootstrap import *
import model as n,types
from scipy.interpolate import PchipInterpolator
from scipy.spatial.transform import Rotation,RotationSpline,Slerp
functions_from(OLD/'performance_core.py',['smooth'],globals())
c=types.SimpleNamespace(smooth=smooth)
_tree=ast.parse((A2/'coordinated_motion.py').read_text(encoding='utf-8-sig'))
_cls=next(x for x in _tree.body if isinstance(x,ast.ClassDef) and x.name=='EventCoordinator')
_tasks=next(x for x in _cls.body if isinstance(x,ast.FunctionDef) and x.name=='tasks')
exec(compile(ast.Module(body=[_tasks],type_ignores=[]),'A2_original_role_tasks','exec'))

def ease(x):
    x=np.clip(x,0,1);return x*x*x*(10+x*(-15+6*x))
def blend_world(a,b,u):
    out=np.eye(4);out[:3,3]=(1-u)*a[:3,3]+u*b[:3,3]
    out[:3,:3]=Slerp([0,1],Rotation.from_matrix(np.array([a[:3,:3],b[:3,:3]])))([float(u)]).as_matrix()[0]
    return out

class Representation:
    def __init__(self):
        self.I=read(O/'INPUT_BINDINGS.json');self.features,_=archive(SRC/'SOURCE_FEATURES.npz');self.source=self.I['source_context'];self.target=self.I['target_context']
        self.start,self.end=self.I['target_window_sec'];self.shift=self.I['phase_clock_shift_sec'];self.neutral=np.array(self.I['neutral_q_deg']);self.bounds=np.array(read(SRC/'POLICY.json')['joint_bounds_deg'])
        self.t=self.features['times'];self.q=PchipInterpolator(self.t,self.features['q_prior']-self.neutral,axis=0)
        self.fractions=np.array(self.features['preferred_xy_fraction']);self.anchor_times=np.array([e['note_on']+.035 for e in self.source])
        self.source_angle=PchipInterpolator(self.t,self.features['key_angles'],axis=0)
        self.clock,_=archive(O/'TARGET_KEY_ACTION_CLOCK.npz');self.target_angle=PchipInterpolator(self.clock['times'],self.clock['key_angles'],axis=0)
        self.boundary,_=archive(O/'TARGET_BOUNDARY_CONDITIONS.npz');self.events=self.I['right_events'];self.policy=read(A2/'GENERATION_POLICY.json')
        self.co=types.SimpleNamespace(events=self.events,policy=self.policy)
        self.map={e['note_id']:i for i,e in enumerate(self.target)}
        self.boundary_q=[self.boundary['q'][1],self.boundary['q'][4]];self.boundary_qdot=[(self.boundary['q'][2]-self.boundary['q'][0])/(1/120),(self.boundary['q'][5]-self.boundary['q'][3])/(1/120)]
        self.boundary_w=[self.boundary['world'][1],self.boundary['world'][4]];self.boundary_v=[(self.boundary['world'][2,:3,3]-self.boundary['world'][0,:3,3])/(1/120),(self.boundary['world'][5,:3,3]-self.boundary['world'][3,:3,3])/(1/120)]
        self.boundary_omega=[Rotation.from_matrix(self.boundary['world'][0,:3,:3]<REDACTED_EMAIL>['world'][2,:3,:3]).as_rotvec()/(1/120),Rotation.from_matrix(self.boundary['world'][3,:3,:3]<REDACTED_EMAIL>['world'][5,:3,:3]).as_rotvec()/(1/120)]
        self.relative=np.array([np.linalg.inv(self.frame(float(t),False))@w for t,w in zip(self.t,self.features['wrist_relative_world'])])
        self.rel_translation=PchipInterpolator(self.t,self.relative[:,:3,3],axis=0)
        self.rel_rotation=RotationSpline(self.t,Rotation.from_matrix(self.relative[:,:3,:3]))
    def roles(self,t):return tasks(self.co,float(t))
    def fraction(self,event):
        return self.fractions[self.map[event['note_id']]] if event['note_id'] in self.map else np.array([.5,.5])
    def preferred_xy(self,event):
        lo,hi=n.inset(n.KEYS[event['key_index']]);return lo+self.fraction(event)*(hi-lo)
    def frame(self,t,target):
        events=self.target if target else self.source;st=t-self.shift if target else t
        angles=self.target_angle(np.clip(t,self.start,self.end)) if target else self.source_angle(np.clip(t,self.t[0],self.t[-1]))
        i=int(np.clip(np.searchsorted(self.anchor_times,st)-1,0,2))
        u=float(ease((st-self.anchor_times[i])/(self.anchor_times[i+1]-self.anchor_times[i])))
        if st<=self.anchor_times[0]:i=0;u=0.
        if st>=self.anchor_times[-1]:i=2;u=1.
        mats=[]
        for j in [i,i+1]:
            k=n.KEYS[events[j]['key_index']];lo,hi=n.inset(k);xy=lo+self.fractions[j]*(hi-lo);R=n.rot(angles[k['key_index']],k['press_axis'])
            p=n.point_on_key(k,xy,angles[k['key_index']]);m=np.eye(4);m[:3,:3]=R;m[:3,3]=p;mats.append(m)
        return blend_world(mats[0],mats[1],u)
    def envelope(self,t):return float(ease((t-self.start)/.09)*ease((self.end-t)/.07))
    def relative_at(self,st):
        st=np.clip(st,self.t[0],self.t[-1]);m=np.eye(4);m[:3,3]=self.rel_translation(st);m[:3,:3]=self.rel_rotation(st).as_matrix();return m
    def world(self,t,x):
        m=self.frame(t,True)@self.relative_at(t-self.shift);a=self.envelope(t);m[1,3]+=x[0]/1000*a;m[2,3]+=x[1]/1000*a
        if t<self.start+.09:
            b=self.boundary_w[0].copy();b[:3,3]+=self.boundary_v[0]*(t-self.start);b[:3,:3]=b[:3,:3]@Rotation.from_rotvec(self.boundary_omega[0]*(t-self.start)).as_matrix();m=blend_world(b,m,float(ease((t-self.start)/.09)))
        if t>self.end-.07:
            b=self.boundary_w[1].copy();b[:3,3]+=self.boundary_v[1]*(t-self.end);b[:3,:3]=b[:3,:3]@Rotation.from_rotvec(self.boundary_omega[1]*(t-self.end)).as_matrix();m=blend_world(m,b,float(1-ease((self.end-t)/.07)))
        return m
    def prior(self,t,x):
        q=self.neutral.copy();idle=np.ones(5);rolemap={j:self.events[idx] for j,idx,lift,w in self.roles(t)}
        for j in range(5):
            e=rolemap.get(j)
            if e is None:
                recent=[ev for ev in self.target if ev['finger']==j+1 and ev['note_off']<=t<ev['note_off']+.15]
                e=recent[-1] if recent else None
            if e is None:continue
            si=self.map.get(e['note_id']);roleweight=0.
            if t<e['note_on']:
                u=float(ease((t-e['note_on']+.18)/.18));idle[j]=1-u;roleweight=u
                if si is not None:
                    value=self.neutral+self.q(np.clip(self.source[si]['note_on'],self.t[0],self.t[-1]));q[j]=(1-u)*self.neutral[j]+u*value[j]
            elif t<e['note_off']:
                idle[j]=0.;roleweight=1.
                if si is not None:q[j]=(self.neutral+self.q(np.clip(t-self.shift,self.t[0],self.t[-1])))[j]
            else:
                u=float(ease((t-e['note_off'])/.15));idle[j]=float(ease((t-e['note_off']-.04)/.11));roleweight=1-u
                if si is not None:
                    value=(self.neutral+self.q(np.clip(self.source[si]['note_off'],self.t[0],self.t[-1])))[j];q[j]=(1-u)*value+u*self.neutral[j]
            if e['note_id']==self.target[1]['note_id']:q[j,1]+=x[2]*self.envelope(t)*roleweight
            if e['note_id']==self.target[2]['note_id']:q[j,1]+=x[3]*self.envelope(t)*roleweight
            if e['note_id']==self.target[1]['note_id'] and t>=e['note_off']:
                q[j,0]+=x[7]*self.envelope(t)*ease((t-e['note_off'])/.04)*(1-ease((t-e['note_off'])/.15))
        a=self.envelope(t)
        for j,var in [(2,4),(1,5),(0,6)]:
            q[j,0]+=x[var]*a*idle[j]
        if t<self.start+.09:
            b=self.boundary_q[0]+self.boundary_qdot[0]*(t-self.start);q=(1-ease((t-self.start)/.09))*b+ease((t-self.start)/.09)*q
        if t>self.end-.07:
            b=self.boundary_q[1]+self.boundary_qdot[1]*(t-self.end);q=ease((self.end-t)/.07)*q+(1-ease((self.end-t)/.07))*b
        return np.clip(q,self.bounds[:,0],self.bounds[:,1])

