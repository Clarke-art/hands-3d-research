"""Geometry-driven finite pad region and R2-relative correction kernel.

No pitch branches, manually specified contact coordinates, or root changes.
"""
from stage_common import *
from left_continuous_motion import *

def skin_caps_batch(states, model, indices):
    st=np.atleast_2d(states);K=len(st);q=np.radians(st[:,6:].reshape(K,5,4));basis={}
    for j,d in enumerate(c.DIGITS):
        names,rels,axes,spread,pad=c.SETUPS['L',d]
        for z,name in enumerate(names):
            M=np.tile(np.eye(4),(K,1,1));R=rotations(q[:,j,z],axes[z])
            if z==0:R=rotations(q[:,j,3],spread)@R
            M[:,:3,:3]=R;basis[name]=M
    pose={}
    def get(name):
        if name not in pose:
            parent=model['bones'][name]['parent']
            M=(get(parent)@model['inv'][parent]@model['rest'][name]) if parent else np.tile(model['rest'][name],(K,1,1))
            pose[name]=<REDACTED_EMAIL>(name,np.eye(4))
        return pose[name]
    mats=np.stack([get(n)@model['inv'][n] for n in model['names']],axis=1)
    local=np.einsum('kbij,nbj->kni',mats,model['weighted'][indices])[...,:3]
    RR=extra_rotation(st[:,3:6])@RBASE;root=BASE+st[:,:3]/1000
    return np.einsum('kij,knj->kni',RR,local)+root[:,None,:]

def activity_envelope(times,events,policy):
    out=np.zeros((len(times),5))
    for n in events:
        rise=c.smooth((times-n['note_on']+policy['prepare_sec'])/policy['prepare_sec'])
        fall=1-c.smooth((times-n['note_off'])/policy['recovery_sec'])
        out[:,n['finger']-1]=np.maximum(out[:,n['finger']-1],rise*fall)
    return out

def build_regions(audit):
    rows=[]
    for r in audit['notes']:
        s=r['summary'];w=r['key_width_mm'];pad=s['pad_max_width_mm']
        # Edge slack scales with the available key width; guard covers finite
        # cap orientation changes. Asymmetric extents are retained.
        slack=.12*w;guard=.05*pad
        lo=r['key_left_mm']+s['left_extent_max_mm']+slack+guard
        hi=r['key_right_mm']-s['right_extent_max_mm']-slack-guard
        if lo>=hi:raise ValueError('Pad/key safe region is empty')
        original=r['planned_xy_mm'][0];nearest=float(np.clip(original,lo,hi))
        target=.75*nearest+.25*(lo+hi)/2
        rows.append(dict(note_id=r['note_id'],finger=r['finger'],left_mm=lo,right_mm=hi,
            target_x_mm=target,delta_x_mm=target-original,edge_slack_mm=slack,orientation_guard_mm=guard,
            original_x_mm=original,pad_width_mm=pad,key_width_mm=w))
    return rows

def correction_budget(states,regions,events):
    # Derive joint envelope from required geometric displacement and current
    # local fingertip leverage. Caps use available joint domain, never enlarge it.
    pads=fk_batch(states)[0];J=[]
    for d in range(20):
        ss=states.copy();ss[:,6+d]+=.01
        J.append((fk_batch(ss)[0]-pads)*1000/.01)
    J=np.stack(J,axis=-1);limits=np.zeros((5,4));derivation=[]
    for j in range(5):
        rows=[r for r in regions if r['finger']==j+1];needed=max(abs(r['delta_x_mm']) for r in rows)
        jac=J[:,j,:,j*4:(j+1)*4];leverage=np.linalg.norm(jac,axis=1)
        med=np.median(leverage,axis=0)
        # Correction budget is two times needed displacement shared over a
        # digit's four DOFs, normalized by each DOF's actual mm/degree leverage.
        limits[j]=2*needed/np.maximum(med,.1)
        derivation.append(dict(finger=j+1,needed_x_shift_mm=needed,median_leverage_mm_per_deg=med,joint_delta_limit_deg=limits[j]))
    return limits,derivation

def targets_relative_to_reference(co,times,ref,regions):
    baseline=fk_batch(ref)[0];goal=baseline.copy();weights=np.zeros((len(times),5))
    for k,t in enumerate(times):
        for r in co.task_components(float(t)):
            weights[k,r['finger']]=r['weight']
            goal[k,r['finger'],0]+=sum(regions[i]['delta_x_mm']*factor for i,lift,factor in r['components'])/1000
    return goal,weights
