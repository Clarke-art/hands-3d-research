"""One compact continuous correction field, using the existing frozen evaluator."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from runtime import *
from scipy.interpolate import BSpline,PchipInterpolator,PPoly
from scipy.spatial.transform import Rotation

def partition_cells(g):
    rest=(np.c_[g.D['rest_vertices'],np.ones(len(g.W))]@g.D['mesh_to_rig'].T)[:,:3]
    cells={}
    for d in ['MIDDLE','RING']:
        names=c.SETUPS['R',d][0]
        pip=g.REST[g.BN[names[1]],:3,3];dip=g.REST[g.BN[names[2]],:3,3]
        pad=rest[c.MARKERS['R'][c.DIGITS.index(d)]['mesh_vertex']]
        direction=(pad-pip)/np.linalg.norm(pad-pip)
        limits=[np.dot((pip+dip)/2-pip,direction),np.dot(dip-pip,direction),np.dot((dip+pad)/2-pip,direction)]
        faces=[[] for _ in range(4)]
        for f in ROIS[d]['faces']:
            cell=int(np.searchsorted(limits,np.dot(rest[f].mean(0)-pip,direction)));faces[cell].append(f)
        assert all(faces), (d,[len(fs) for fs in faces])
        cells[d]=[dict(vertices=sorted({v for face in fs for v in face}),faces=fs,
            segment='PIP_DIP' if i<2 else 'DIP_PAD',slice=i%2) for i,fs in enumerate(faces)]
        assert {tuple(f) for cell in cells[d] for f in cell['faces']}=={tuple(f) for f in ROIS[d]['faces']}
    return cells

def fit_axes(points):
    # Reference PCA axes are frozen for a given time; bounds contain ALL face
    # vertices, not a percentile, radius shrink or a sampled subset.
    mean=points.mean(1);centered=points-mean[:,None]
    cov=np.einsum('kvi,kvj->kij',centered,centered)
    _,axes=np.linalg.eigh(cov)
    return axes
def boxes(points,axes,padding=.0005):
    local=np.einsum('kvi,kij->kvj',points,axes)
    lo=local.min(1)-padding;hi=local.max(1)+padding
    center=np.einsum('kj,kij->ki',(lo+hi)/2,axes)
    return center,(hi-lo)/2
def sat_axes(a,b):
    axes=np.concatenate([a.transpose(0,2,1),b.transpose(0,2,1),
        np.cross(a.transpose(0,2,1)[:,:,None],b.transpose(0,2,1)[:,None]).reshape(len(a),9,3)],axis=1)
    lengths=np.linalg.norm(axes,axis=2,keepdims=True)
    return axes/np.maximum(lengths,1e-12),lengths[:,:,0]>1e-8
def sat_gap(a,b,ea,eb,aa,ab,axes,valid):
    projection=np.abs(np.einsum('kni,ki->kn',axes,b-a))
    ra=np.sum(np.abs(np.einsum('kni,kij->knj',axes,aa))*ea[:,None],2)
    rb=np.sum(np.abs(np.einsum('kni,kij->knj',axes,ab))*eb[:,None],2)
    gaps=np.where(valid,projection-ra-rb,-1.e3)
    return gaps.max(1),gaps

class Context:
    def __init__(self,times,manifest):
        self.t=np.asarray(times);self.K=len(self.t);self.g=skin_module();self.cells=manifest['cells']
        ids=set(v for d in ROIS for v in ROIS[d]['vertices'])|{m['mesh_vertex'] for m in c.MARKERS['R']}
        self.ids=np.array(sorted(ids));self.ix={d:np.searchsorted(self.ids,ROIS[d]['vertices']) for d in ROIS}
        self.marker=np.array([np.searchsorted(self.ids,m['mesh_vertex']) for m in c.MARKERS['R']])
        self.model=self.g.Skin(self.t,self.ids)
        self.model.world=interp(BASE['rig_world'],self.t);self.model.angles=interp(BASE['key_angles'],self.t)
        quat=interp(BASE['quat'],self.t);quat/=np.linalg.norm(quat,axis=-1,keepdims=True)
        self.model.base=Rotation.from_quat(quat[:,:,[1,2,3,0]].reshape(-1,4)).as_matrix().reshape(self.K,-1,3,3)
        self.source=interp(BASE['qdeg'],self.t);self.original=self.model(self.source)
        self.cell_ix={d:[np.searchsorted(self.ids,cell['vertices']) for cell in self.cells[d]] for d in self.cells}
        self.axes={d:[fit_axes(self.original[:,ix]) for ix in self.cell_ix[d]] for d in self.cells}
        self.pairs=[]
        for a in range(4):
            for b in range(4):
                axes,valid=sat_axes(self.axes['MIDDLE'][a],self.axes['RING'][b]);self.pairs.append((a,b,axes,valid))
        self.keys=[];sourcebox=np.array([self.original.min((0,1)),self.original.max((0,1))])
        for key in c.KEYS:
            for body in key['geometry']:
                v=np.array(body['vertices'])
                if np.all(v.max(0)>=sourcebox[0]-.025) and np.all(v.min(0)<=sourcebox[1]+.025):self.keys.append((key,body))
        self.source_depth=[]
        self.source_depth_points=[]
        for key,body in self.keys:
            dep=self.g.body_depth(self.original,key,body,self.model.angles)
            self.source_depth.append({d:dep[:,ix].max(1) for d,ix in self.ix.items()})
            self.source_depth_points.append(dep)
        self.rows={}
    def envelope(self,V):
        allboxes={d:[boxes(V[:,ix],ax) for ix,ax in zip(self.cell_ix[d],self.axes[d])] for d in self.cells}
        gaps=[];detail=[]
        for a,b,axes,valid in self.pairs:
            ca,ea=allboxes['MIDDLE'][a];cb,eb=allboxes['RING'][b]
            gap,axisgaps=sat_gap(ca,cb,ea,eb,self.axes['MIDDLE'][a],self.axes['RING'][b],axes,valid)
            gaps.append(gap);detail.append((ca,cb,axes,axisgaps))
        return np.stack(gaps,1),detail
    def contacts(self,V):
        rows=[]
        for k,t in enumerate(self.t):
            ns=[n for n in NOTES if n['hand']=='R' and n['note_on']<=t<n['note_off']]
            # Keep old-key contact left limit at coincident OFF/next ON too.
            ns += [n for n in NOTES if n['hand']=='R' and n['finger']-1 in CHANGED and abs(t-n['note_off'])<1e-9]
            for n in ns:
                key=c.KEYS[n['key_index']];pv=np.array(key['press_pivot']);R=c.axisrot(-self.model.angles[k,n['key_index']],[1,0,0])
                p=R@(V[k,self.marker[n['finger']-1]]-pv)+pv
                s=min(key['key_top_playable_surface'],key=lambda s:np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])))
                gap=(p[2]-s['z'])*1000;miss=np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000
                rows.append(dict(k=k,t=float(t),event=n['note_id'],finger=n['finger'],gap_mm=float(gap),horizontal_mm=float(miss),pass_=abs(gap)<=3 and miss<.03))
        return rows
    def key_regression(self,V):
        values=[];details=[]
        for i,(key,body) in enumerate(self.keys):
            dep=self.g.body_depth(V,key,body,self.model.angles)
            for d,ix in self.ix.items():
                maximum=dep[:,ix].max(1);allowed=np.maximum(.5,self.source_depth_points[i][:,ix])
                excess=np.maximum(dep[:,ix]-allowed,0).max(1)
                values.append(excess)
                for k in np.flatnonzero(excess>.02):
                    j=int(ix[np.argmax(dep[k,ix]-allowed[k])]);details.append(dict(t=float(self.t[k]),digit=d,midi=key['midi_note'],component=body['name'],
                        depth_mm=float(dep[k,j]),source_depth_mm=float(self.source_depth_points[i][k,j]),world_m=V[k,j].tolist()))
        return np.stack(values,1),details

class Curve:
    def __init__(self):
        old,new,nxt=[SCOPE[k] for k in ['old','new','next_for_releasing']]
        # Two event-defined interior knots, two free coefficients per DOF.
        # First/last two control coefficients are zero: delta and its velocity
        # vanish at both window boundaries without clipping output angles.
        self.knots=np.r_[[START]*4,[old['note_off'],nxt['note_on']],[END]*4]
        self.free=np.array([2,3]);self.coefficients=6;self.variables=16
        self.source=PchipInterpolator(BASE['times'],BASE['qdeg'],axis=0)
        ns=[n for n in NOTES if n['hand']=='R' and n['finger']==new['finger'] and n['note_off']<=new['note_on']-POL['prepare_sec']]
        self.middle_begin=max(n['note_off'] for n in ns)
    def coefficient_array(self,x):
        arr=np.zeros((6,2,4));arr[self.free]=np.asarray(x).reshape(2,2,4);return arr
    def delta(self,x,t):
        t=np.asarray(t);d=BSpline(self.knots,self.coefficient_array(x),3,extrapolate=False)(t)
        d[:,0]*=smooth((t-self.middle_begin)/POL['finger_release_follow_sec'])[:,None]
        return d
    def state(self,x,t):
        q=self.source(t).copy();q[:,CHANGED]+=self.delta(x,np.asarray(t));return q
    def targets(self,ctx,manifest):
        target=ctx.original[:,ctx.marker].copy();normal=np.array(manifest['witness_displacement_m'])
        old,new,nxt=[SCOPE[k] for k in ['old','new','next_for_releasing']]
        gate=release_gate(ctx.t,old['note_off'],POL['finger_release_follow_sec'],nxt['note_on']-.075)
        target[:,old['finger']-1]+=gate[:,None]*normal
        # The new contact site moves only in its legal key plane. It blends
        # continuously during prepare/hold/release rather than resetting at ON.
        key=c.KEYS[new['key_index']];pv=np.array(key['press_pivot']);s=key['key_top_playable_surface'][0]
        prep=smooth((ctx.t-(new['note_on']-POL['prepare_sec']))/POL['prepare_sec'])
        recovery=1-smooth((ctx.t-new['note_off'])/(END-new['note_off']))
        for k,t in enumerate(ctx.t):
            R=c.axisrot(ctx.model.angles[k,new['key_index']],[1,0,0]);local=R.T@(target[k,new['finger']-1]-pv)+pv
            tangent=R.T@(-normal*.5);tangent[2]=0
            tangent[:2]=np.clip(local[:2]+tangent[:2],[s['xmin']+.003,s['ymin']+.001],[s['xmax']-.003,s['ymax']-.001])-local[:2]
            target[k,new['finger']-1]+=prep[k]*recovery[k]*(R@tangent)
        return target

def curve_certificate(curve,x):
    # Exact polynomial extrema of source PCHIP + cubic correction times the
    # quintic middle gate. Domain and delta-velocity certificates concern the
    # numerical representation; actual baked quaternion checks remain needed.
    from numpy.polynomial import Polynomial as P
    delta=[PPoly.from_spline(BSpline(curve.knots,curve.coefficient_array(x)[:,j,k],3)) for j in range(2) for k in range(4)]
    breaks=np.unique(np.r_[BASE['times'],curve.knots,curve.middle_begin,curve.middle_begin+POL['finger_release_follow_sec']])
    breaks=breaks[(breaks>=START)&(breaks<=END)];mins=np.full((2,4),np.inf);maxs=-mins.copy();vmax=0.;worst=[]
    for a,b in zip(breaks[:-1],breaks[1:]):
        if b-a<1e-12:continue
        m=(a+b)/2;i=min(len(BASE['times'])-2,max(0,np.searchsorted(BASE['times'],m)-1))
        for j in range(2):
            for k in range(4):
                pp=delta[j*4+k];ii=min(len(pp.x)-2,max(0,np.searchsorted(pp.x,m)-1))
                d=P(pp.c[:,ii][::-1])(P([a-pp.x[ii],1]))
                if j==0:
                    if m<=curve.middle_begin:gate=P([0])
                    elif m>=curve.middle_begin+POL['finger_release_follow_sec']:gate=P([1])
                    else:
                        u=P([(a-curve.middle_begin)/POL['finger_release_follow_sec'],1/POL['finger_release_follow_sec']]);gate=10*u**3-15*u**4+6*u**5
                    d=d*gate
                base=P(curve.source.c[:,i,CHANGED[j],k][::-1])(P([a-BASE['times'][i],1]));q=base+d
                roots=q.deriv().roots();probes=[0,b-a]+[r.real for r in roots if abs(r.imag)<1e-9 and 0<r.real<b-a]
                vals=q(probes);mins[j,k]=min(mins[j,k],min(vals));maxs[j,k]=max(maxs[j,k],max(vals))
                dv=d.deriv();r=dv.deriv().roots();vv=[0,b-a]+[z.real for z in r if abs(z.imag)<1e-9 and 0<z.real<b-a];vmax=max(vmax,float(max(abs(dv(vv)))))
    low=np.array([0,0,0,-28]);high=np.array([75,95,65,28]);violation=max(float((low-mins).max()),float((maxs-high).max()),0)
    return dict(domain_min_deg=mins,domain_max_deg=maxs,max_domain_violation_deg=violation,
        correction_velocity_max_deg_sec=vmax,domain_pass=violation<=.002,correction_velocity_pass=vmax<=180,
        boundary_delta_max_deg=float(abs(curve.delta(x,np.array([START,END]))).max()),
        boundary_delta_velocity_exact_zero=True,scope='Exact polynomial numerical-domain and added-velocity extrema, not a continuous geometric collision certificate')
