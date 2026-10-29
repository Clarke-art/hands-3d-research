"""A small role/portal adapter over existing FK and bounded sparse least_squares.

No pitch or frame constants in planning. Full output is allowed only after a
single finite static feasibility batch. Capsules guide; Blender skin judges.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from runtime import *
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
from scipy.interpolate import PchipInterpolator

class Roles:
    def __init__(self,notes,policy): self.notes=notes;self.policy=policy
    def at(self,t,side='R'):
        out=[]
        for j,d in enumerate(c.DIGITS):
            ns=sorted([n for n in self.notes if n['hand']==side and n['finger']==j+1],key=lambda n:n['note_on'])
            active=next((n for n in ns if n['note_on']<=t<n['note_off']),None)
            release=next((n for n in reversed(ns) if n['note_off']<=t<n['note_off']+self.policy['finger_release_follow_sec']),None)
            prep=next((n for n in ns if n['note_on']-self.policy['prepare_sec']<=t<n['note_on']),None)
            role,n=('ACTIVE_HOLD',active) if active else ('RELEASING',release) if release else ('PREPARING',prep) if prep else ('IDLE',None)
            out.append(dict(digit=d,role=role,event_id=n['note_id'] if n else None,next_event_id=prep['note_id'] if prep else None))
        return out

def segment_distance(a,b,c0,d):
    # Segment closest points with endpoint correction (Ericson formulation).
    u=b-a;v=d-c0;w=a-c0;A=u@u;B=u@v;C=v@v;D=u@w;E=v@w;den=A*C-B*B
    s=np.clip((B*E-C*D)/den,0,1) if den>1e-15 else 0.
    t=np.clip((B*s+E)/max(C,1e-15),0,1)
    s=np.clip((B*t-D)/max(A,1e-15),0,1)
    t=np.clip((B*s+E)/max(C,1e-15),0,1)
    return float(np.linalg.norm(a+s*u-c0-t*v))

class Planner:
    def __init__(self,scope):
        self.scope=scope;self.old=scope['old'];self.new=scope['new'];self.next=scope['next_for_releasing']
        self.changed=[self.new['finger']-1,self.old['finger']-1]
        assert len(set(self.changed))==2
        self.roles=Roles(NOTES,POL);self.geom=historical_skin()
        self.actual=dict(np.load(OUT/'ANCHOR_ACTUAL.npz'))
        self.rois=read(ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_SKIN_ROI.json')
        self.times=np.array([self.new['note_on']-.035,self.new['note_on'],self.old['note_off']+POL['finger_release_follow_sec']])
        self.ids=np.unique(np.concatenate([self.rois[d]['vertices'] for d in self.rois]))
        self.roi={d:np.searchsorted(self.ids,self.rois[d]['vertices']) for d in self.rois}
        self.model=self.geom.Skin(self.times,self.ids)
        # Reuse actual exported quaternions/matrices at the three anchors. The
        # frozen LBS model is independently compared against Blender below.
        self.source=self.interp(self.actual['qdeg'],self.times)
        self.world=self.interp(self.actual['rig_world'],self.times)
        self.model.world=self.world
        self.model.angles=self.actual['key_angles'].copy()
        quat=self.actual['quat'];quat=quat/np.linalg.norm(quat,axis=-1,keepdims=True)
        self.model.base=self.geom.Rotation.from_quat(quat[:,:,[1,2,3,0]].reshape(-1,4)).as_matrix().reshape(3,-1,3,3)
        self.original=self.model(self.source)
        self.keys=[]
        sourcebox=np.array([self.original.min((0,1)),self.original.max((0,1))])
        for key in c.KEYS:
            for g in key['geometry']:
                V=np.array(g['vertices'])
                if np.all(V.max(0)>=sourcebox[0]-.02) and np.all(V.min(0)<=sourcebox[1]+.02):self.keys.append((key,g))
        self.base_depth={}
        for key,g in self.keys:
            depth=self.geom.body_depth(self.original,key,g,self.model.angles)
            for d,ix in self.roi.items():self.base_depth[d,key['key_index'],g['name']]=np.maximum(.5,depth[:,ix].max(1))
        self.radii={}
        for j in self.changed:
            d=c.DIGITS[j];segments=[self.skeleton(k,j,self.source[k,j]) for k in range(3)]
            pts=self.original[:,self.roi[d]];r=[]
            for slot in [0,1]:
                maxima=[]
                for k,segs in enumerate(segments):
                    distances=[]
                    for a,b in segs:
                        u=b-a;f=np.clip((pts[k]-a)@u/max(u@u,1e-12),0,1);distances.append(np.linalg.norm(pts[k]-a-f[:,None]*u,axis=1))
                    dist=np.stack(distances,1);assigned=dist[:,slot]<=dist[:,1-slot]
                    maxima.append(dist[assigned,slot].max() if assigned.any() else 0)
                r.append(float(max(maxima)+.0005))
            self.radii[j]=r
        self.target=self.portal_targets()
        self.trace=[];self.calls=0;self.started=time.perf_counter()

    def interp(self,arr,times):
        flat=arr.reshape(len(self.actual['times']),-1)
        return np.column_stack([np.interp(times,self.actual['times'],flat[:,j]) for j in range(flat.shape[1])]).reshape((len(times),)+arr.shape[1:])
    def skeleton(self,k,j,q):
        # canonical performance_core FK is in canonical metres, whereas the
        # exported C1 rig-world includes native rig scale. Use the already
        # verified frozen native REST/REL evaluator, not canonical rels twice.
        d=c.DIGITS[j];names,_,axes,spread,_=c.SETUPS['R',d]
        basis=self.model.base[k].copy()
        for n,r in zip(names,c.joint_mats('R',d,np.radians(q))):basis[self.geom.BN[n]]=r
        poses=[]
        for b,parent in enumerate(self.geom.D['parents']):
            J=np.eye(4);J[:3,:3]=basis[b];mat=self.geom.REL[b]@J
            if parent>=0:mat=poses[parent]@mat
            poses.append(mat)
        points=[(self.world[k]@poses[self.geom.BN[n]])[:3,3] for n in names]
        points.append(self.marker(k,j,q))
        return [(points[1],points[2]),(points[2],points[3])]
    def marker(self,k,j,q):
        state=self.source.copy();state[k,j]=q
        V=self.model(state)
        vid=c.MARKERS['R'][j]['mesh_vertex'];ix=int(np.searchsorted(self.ids,vid));assert self.ids[ix]==vid
        return V[k,ix]
    def portal_targets(self):
        # Front-depth portal is a normalized region of the next playable face,
        # avoiding the occupied distal corridor. The released digit uses a
        # clearance height derived from nearby actual key bodies, never angles.
        targets=[]
        for k,t in enumerate(self.times):
            row=[]
            for j in self.changed:
                original=self.marker(k,j,self.source[k,j]);role=self.roles.at(float(t))[j]['role']
                n=self.new if j==self.new['finger']-1 else self.old
                key=c.KEYS[n['key_index']];pv=np.array(key['press_pivot']);R=c.axisrot(self.model.angles[k,n['key_index']],[1,0,0])
                local=R.T@(original-pv)+pv
                s=key['key_top_playable_surface'][0]
                target=original.copy()
                if j==self.new['finger']-1:
                    local[0]=np.clip(key['key_center'][0],s['xmin']+.003,s['xmax']-.003)
                    local[1]=s['ymin']+.30*(s['ymax']-s['ymin'])
                    local[2]=s['z']+.0005
                    target=R@(local-pv)+pv
                    if role=='PREPARING':target[2]+=.003
                elif role=='RELEASING':
                    tops=[np.array(g['vertices'])[:,2].max() for key0,g in self.keys]
                    target[2]=max(original[2]+.003,max(tops)+max(self.radii[j])+.001)
                row.append(dict(finger=j+1,role=role,target_world_m=target.tolist(),source_world_m=original.tolist()))
            targets.append(row)
        return targets
    def unpack(self,x):
        q=self.source.copy();q[:,self.changed]=np.asarray(x).reshape(3,2,4)
        return q
    def residual(self,x):
        if time.perf_counter()-self.started>110:raise TimeoutError('Finite preflight budget; no retune/restart')
        self.calls+=1;q=self.unpack(x);V=self.model(q);out=[]
        for k,t in enumerate(self.times):
            tasks={r['finger']-1:r for r in self.target[k]}
            for j in self.changed:
                target=np.array(tasks[j]['target_world_m']);out.extend((self.marker(k,j,q[k,j])-target)*1000*2)
                # At the exact OFF/ON boundary continuity requires the releasing
                # finger's old contact left limit too; no shortened MIDI hold.
                active=[n for n in NOTES if n['hand']=='R' and n['finger']==j+1 and n['note_on']<=t<n['note_off']]
                if abs(t-self.old['note_off'])<1e-9 and j==self.old['finger']-1:active.append(self.old)
                for n in active:
                    key=c.KEYS[n['key_index']];pv=np.array(key['press_pivot']);R=c.axisrot(self.model.angles[k,n['key_index']],[1,0,0]);p=R.T@(self.marker(k,j,q[k,j])-pv)+pv
                    s=key['key_top_playable_surface'][0]
                    out.extend([max(0,abs(p[2]-s['z'])*1000-2.05)*12,
                        max(0,s['xmin']-p[0],p[0]-s['xmax'])*1000*12,
                        max(0,s['ymin']-p[1],p[1]-s['ymax'])*1000*12])
            sa=self.skeleton(k,self.changed[0],q[k,self.changed[0]]);sb=self.skeleton(k,self.changed[1],q[k,self.changed[1]])
            for a,(p0,p1) in enumerate(sa):
                for b,(p2,p3) in enumerate(sb):
                    gap=segment_distance(p0,p1,p2,p3)-self.radii[self.changed[0]][a]-self.radii[self.changed[1]][b]
                    out.append(max(0,.0007-gap)*1000*6)
            out.extend(((q[k,self.changed]-self.source[k,self.changed])*np.array([.08,.08,.10,.30])).ravel())
        for key,g in self.keys:
            depth=self.geom.body_depth(V,key,g,self.model.angles)
            for j in self.changed:
                d=c.DIGITS[j];excess=np.maximum(depth[:,self.roi[d]]-self.base_depth[d,key['key_index'],g['name']][:,None],0)
                out.extend((np.sort(excess,axis=1)[:,-3:]*5).ravel())
        return np.array(out)
    def inspect(self,q):
        V=self.model(q);rows=[]
        for k,t in enumerate(self.times):
            sa=self.skeleton(k,self.changed[0],q[k,self.changed[0]]);sb=self.skeleton(k,self.changed[1],q[k,self.changed[1]])
            gaps=[(segment_distance(*a,*b)-self.radii[self.changed[0]][ia]-self.radii[self.changed[1]][ib])*1000 for ia,a in enumerate(sa) for ib,b in enumerate(sb)]
            contacts=[]
            for j in self.changed:
                owned=[n for n in NOTES if n['hand']=='R' and n['finger']==j+1 and n['note_on']<=t<n['note_off']]
                if abs(t-self.old['note_off'])<1e-9 and j==self.old['finger']-1:owned.append(self.old)
                for n in owned:
                    key=c.KEYS[n['key_index']];pv=np.array(key['press_pivot']);p=c.axisrot(-self.model.angles[k,n['key_index']],[1,0,0])@(self.marker(k,j,q[k,j])-pv)+pv
                    s=key['key_top_playable_surface'][0]
                    gap=(p[2]-s['z'])*1000;miss=np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]))*1000
                    contacts.append(dict(event=n['note_id'],gap_mm=gap,horizontal_mm=miss,pass_=abs(gap)<=2.05 and miss<1e-5))
            excess=[]
            for key,g in self.keys:
                depth=self.geom.body_depth(V[k:k+1],key,g,self.model.angles[k:k+1])[0]
                for j in self.changed:
                    d=c.DIGITS[j];e=float(depth[self.roi[d]].max()-self.base_depth[d,key['key_index'],g['name']][k])
                    if e>.02:excess.append(dict(digit=d,key=key['midi_note'],excess_mm=e))
            rows.append(dict(t=float(t),roles=self.roles.at(float(t)),capsule_min_gap_mm=min(gaps),contacts=contacts,new_key_depth_excess=excess,
                qdeg=q[k].tolist(),pass_=min(gaps)>=.5 and all(c0['pass_'] for c0 in contacts) and not excess))
        return rows

if __name__=='__main__':
    S=read(OUT/'EVENT_SCOPE.json')
    assert not (OUT/'STATIC_PREFLIGHT_VERIFIED_RESULT.json').exists()
    if not (OUT/'NUMERICAL_ATTEMPT_STARTED.json').exists():
        save('NUMERICAL_ATTEMPT_STARTED.json',dict(kind='ONE_STATIC_FEASIBILITY_BATCH',candidate_limit=1,total_budget_seconds=300))
    else:
        assert (OUT/'INITIALIZATION_REPAIR.json').exists() and read(OUT/'INITIALIZATION_REPAIR.json')['prior_optimizer_calls']==0
    started=time.perf_counter();p=Planner(S)
    parity=float(np.linalg.norm(p.original-p.interp(p.actual['vertices'],p.times)[:,p.ids],axis=-1).max()*1000)
    save('PLANNER_POLICY_COORDINATE_VERIFIED.json',dict(method='ROLE_FRONT_PORTAL_AND_RELEASE_LIFT',times=p.times,roles=[p.roles.at(t) for t in p.times],
        targets=p.target,changed_digits=[c.DIGITS[j] for j in p.changed],capsule_radii_m=p.radii,
        support_points_per_digit=3,variables=24,preflight_max_nfev=35,trust_deg=[12,18,14,6],
        collision_guidance='Frozen-FK distal capsules + local key bodies; final actual Blender skin required',
        preserves=['root','left','other digits','keys','MIDI','fingering'],model_parity_mm=parity,
        no_pitch_angle_constants=True,no_fixed_frame_corrections=True))
    assert parity<.03, ('Source skin model mismatch',parity)
    lo=np.maximum(p.source[:,p.changed]-[12,18,14,6],[0,0,0,-28]);hi=np.minimum(p.source[:,p.changed]+[12,18,14,6],[75,95,65,28])
    seed=p.source[:,p.changed].ravel();sample=p.residual(seed)
    # Exactly the same bounded least_squares backend and Jacobian sparsity
    # facility as A2, restricted to 3 anchors / 2 digits, not a new engine.
    J=lil_matrix((len(sample),24),dtype=np.int8);J[:,:]=1
    try:
        fit=least_squares(p.residual,seed,bounds=(lo.ravel(),hi.ravel()),jac_sparsity=J.tocsr(),max_nfev=35,
            x_scale='jac',ftol=2e-5,xtol=2e-5,gtol=2e-5,tr_options={'regularize':True})
        q=p.unpack(fit.x);rows=p.inspect(q)
        result=dict(success=bool(fit.success),nfev=fit.nfev,cost=float(fit.cost),message=fit.message,rows=rows,
            numerical_seconds=time.perf_counter()-started,residual_calls=p.calls,preflight_pass=all(r['pass_'] for r in rows),
            new_dynamic_candidate_count=0,scope='Independent static anchors; not a path feasibility certificate',model_parity_mm=parity)
        np.savez_compressed(OUT/'STATIC_PREFLIGHT_VERIFIED.npz',times=p.times,qdeg=q,source_qdeg=p.source)
    except TimeoutError as e:
        result=dict(exception=str(e),numerical_seconds=time.perf_counter()-started,preflight_pass=False,new_dynamic_candidate_count=0,residual_calls=p.calls)
    result['invalid_prior_fk_batch']=dict(file='STATIC_PREFLIGHT_RESULT.json',reason='Canonical metre FK composed with native rig scale; gross metre-scale mismatch, not physical failure evidence',prior_numerical_seconds=read(OUT/'STATIC_PREFLIGHT_RESULT.json')['numerical_seconds'],policy_unchanged=True)
    save('STATIC_PREFLIGHT_VERIFIED_RESULT.json',result)
    print('FINITE_ROLE_PREFLIGHT',json.dumps(result,default=lambda x:x.item() if hasattr(x,'item') else x),flush=True)
