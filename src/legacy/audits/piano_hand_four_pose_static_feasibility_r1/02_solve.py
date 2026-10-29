import sys,json,hashlib,time
sys.dont_write_bytecode=True
from pathlib import Path
P=Path(__file__).resolve().parent;OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(OLD))
import numpy as np
from scipy.optimize import least_squares
import performance_core as c
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
policy=read(P/'STATIC_POSTURE_POLICY_R1.json');lock=read(P/'PRE_SOLVE_LOCK_R1.json');assert sha(P/'STATIC_POSTURE_POLICY_R1.json')==lock['policy_sha256'] and sha(Path(__file__))==lock['solver_script_sha256']
assert not (P/'SOLVED_STATIC_POSES_R1.json').exists(),'Single-run result already exists; do not restart or tune.'
data=read(P/'FORMAL_INPUT_EXTRACTION_R1.json');KEYS=c.KEYS;DIGITS=c.DIGITS;w=policy['solver']['residual_weights']
surfs=np.array([[v[k] for k in ['xmin','xmax','ymin','ymax','z']] for key in KEYS for v in key['key_top_playable_surface']])
def height(pts):
 mask=(pts[:,None,0]>=surfs[:,0])&(pts[:,None,0]<=surfs[:,1])&(pts[:,None,1]>=surfs[:,2])&(pts[:,None,1]<=surfs[:,3])
 return np.max(np.where(mask,surfs[:,4],-.1),axis=1)
def rootrot(v):return c.rz(v[3])@c.axisrot(v[4],[1,0,0])@c.axisrot(v[5],[0,1,0])
models={}
for s in ['L','R']:
 d=data[s];V=np.array(d['rest_vertices_canonical']);W=np.array(d['weights']);names=d['bone_names'];bones=c.RIG[s]['bones'];rest={n:np.array(bones[n]['matrix']) for n in names};inv={n:np.linalg.inv(rest[n]) for n in names}
 wrist=np.flatnonzero(V[:,1]<.045);palm=np.flatnonzero((V[:,1]>=.045)&(V[:,1]<.105))
 palm=palm[np.argsort(V[palm,2],kind='stable')[:24]];wrist=wrist[np.argsort(V[wrist,2],kind='stable')[:12]]
 samples=[]
 for digit in DIGITS:
  cols=[i for i,n in enumerate(names) if n.startswith(digit+'_')];inds=np.flatnonzero(W[:,cols].sum(1)>.65);samples.append(inds[np.argsort(V[inds,2],kind='stable')[:8]])
 ids=np.r_[[r['mesh_vertex'] for r in c.MARKERS[s]],palm,wrist,*samples].astype(int)
 weighted=np.c_[V[ids],np.ones(len(ids))][:,None,:]*W[ids,:,None]
 models[s]={'names':names,'bones':bones,'rest':rest,'inv':inv,'weighted':weighted,'sample_indices':ids.tolist(),'sample_digit_counts':[len(x) for x in samples]}
def local(s,q):
 m=models[s];basis={}
 for j,digit in enumerate(DIGITS):
  for n,r in zip(c.SETUPS[s,digit][0],c.joint_mats(s,digit,q[j])):
   B=np.eye(4);B[:3,:3]=r;basis[n]=B
 pose={}
 def get(n):
  if n in pose:return pose[n]
  parent=m['bones'][n]['parent'];pose[n]=(get(parent)@m['inv'][parent]@m['rest'][n] if parent else m['rest'][n])@basis.get(n,np.eye(4));return pose[n]
 matrices=np.array([get(n)@m['inv'][n] for n in m['names']]);skin=np.einsum('bij,nbj->nbi',matrices,m['weighted']).sum(1)[:,:3]
 pads=np.array([(get(row['distal_frame'])@np.r_[row['local_pad_point'],1])[:3] for row in c.MARKERS[s]])
 return pads,skin
def regions(midi,active):
 k=KEYS[midi-21];ss=k['key_top_playable_surface'];loy=min(t['ymin'] for t in ss);hiy=max(t['ymax'] for t in ss);out=[]
 for j,t in enumerate(ss):
  if active and k['color']=='WHITE' and j>0:continue
  ix=.003 if k['color']=='WHITE' else .002;iy=.007 if k['color']=='WHITE' else .002
  # The front/rear seam is not a physical outer edge.
  out.append((np.array([t['xmin']+ix,t['ymin']+(iy if t['ymin']<=loy+1e-7 else 0)]),np.array([t['xmax']-ix,t['ymax']-(iy if t['ymax']>=hiy-1e-7 or active else 0)]),t['z']))
 return out
def region_delta(pt,boxes):
 vals=[pt[:2]-np.clip(pt[:2],lo,hi) for lo,hi,z in boxes];j=int(np.argmin([v@v for v in vals]));return vals[j],boxes[j][2]
poses={};diagnostics={};starttime=time.monotonic()
for s,ps in [('L',['L1','L2']),('R',['R1','R2'])]:
 rb=policy['root_bounds'][s];roots=np.array(rb['xyz_mm'])/1000;rots=np.radians(policy['root_bounds']['yaw_pitch_roll_deg']);lo=np.r_[roots[0],rots[0]];hi=np.r_[roots[1],rots[1]]
 qlo=[];qhi=[];priors=[]
 for pose in ps:
  priors.append(np.radians(policy['priors_deg'][pose]))
  for j,digit in enumerate(DIGITS):
   typ='THUMB' if j==0 else 'LEFT_IDLE_INDEX_MIDDLE_RING' if s=='L' and j in [1,2,3] else 'LONG';b=np.radians(policy['joint_increment_bounds_deg'][typ]);qlo.extend(b[0]);qhi.extend(b[1])
 lo=np.r_[lo,qlo];hi=np.r_[hi,qhi];seedroot=np.r_[np.array(rb['seed_xyz_mm'])/1000,[0,0,0]];x0=np.r_[seedroot,np.array(priors).flatten()]
 def residual(x):
  root=x[:3];R=rootrot(x);out=[];qs=x[6:].reshape(2,5,4)
  for i,pose in enumerate(ps):
   task=policy['tasks'][pose];q=qs[i];lp,ls=local(s,q);pads=lp@R.T+root;skin=ls@R.T+root;active=task['active_finger'];prep={int(k)-1:m for k,m in task['prepared'].items()};jointweights=np.full(5,w['other_joint_rad'])
   if s=='L':jointweights[1:4]=w['left_idle_joint_rad']
   tasks=dict(prep)
   if active is not None:tasks[active-1]=task['active_midi'];jointweights[active-1]=w['active_joint_rad']
   for j,midi in tasks.items():
    isactive=active==j+1;boxes=regions(midi,isactive);delta,z=region_delta(pads[j],boxes);k=KEYS[midi-21];digit=DIGITS[j];prefx=k['key_center'][0]+(policy['contact_regions']['left_preferred_x_offset_from_center_mm'].get(digit,0)/1000 if s=='L' else 0);prefy=(policy['contact_regions']['black_preferred_y_mm'] if k['color']=='BLACK' else policy['contact_regions']['white_preferred_y_mm'].get(digit,43))/1000
    if isactive:
     out.extend(delta*1000*w['active_contact_mm']);out.append((pads[j,2]-z-.0005)*1000*w['active_contact_mm']);sd,sz=region_delta(skin[j],boxes);out.extend(sd*1000*w['active_skin_contact_mm']);out.append((skin[j,2]-sz-.0005)*1000*w['active_skin_contact_mm'])
    else:
     out.extend(delta*1000*w['prepared_region_mm']);gap=pads[j,2]-z;out.append((gap-np.clip(gap,.004,.018))*1000*w['prepared_gap_interval_mm']);out.append((gap-.008)*1000*w['prepared_preferred_height_mm'])
    out.extend((pads[j,:2]-[prefx,prefy])*1000*w['preferred_xy_mm'])
   out.extend(((q-priors[i])*jointweights[:,None]).flatten())
   # Exactly the preregistered planning samples. No per-vertex deformation occurs.
   palmwrist=skin[5:41];out.extend(np.maximum(height(palmwrist)+.006-palmwrist[:,2],0)*1000*w['palm_wrist_clearance_mm'])
   idle=np.ones(5);idle[active-1 if active is not None else []]=0
   out.extend(np.maximum(height(pads)+.004-pads[:,2],0)*idle*1000*w['idle_proxy_clearance_mm'])
   cursor=41
   for j,count in enumerate(models[s]['sample_digit_counts']):
    proxy=skin[cursor:cursor+count];cursor+=count;out.extend(np.maximum(height(proxy)+.004-proxy[:,2],0)*idle[j]*1000*w['idle_proxy_clearance_mm'])
  out.extend(((qs[1]-qs[0])*w['paired_joint_difference_rad']).flatten());out.extend((x[:3]-seedroot[:3])*1000*w['root_prior_mm']);out.extend(x[3:6]*w['root_rotation_rad'])
  return np.array(out)
 fit=least_squares(residual,x0,bounds=(lo,hi),max_nfev=policy['solver']['max_nfev_per_pair'],xtol=policy['solver']['xtol'],ftol=policy['solver']['ftol'],gtol=policy['solver']['gtol'])
 assert np.all(np.isfinite(fit.x))
 R=rootrot(fit.x);qs=fit.x[6:].reshape(2,5,4)
 for i,pose in enumerate(ps):
  pads,skin=local(s,qs[i]);poses[pose]={'hand':s,'root_xyz_m':fit.x[:3].tolist(),'root_yaw_pitch_roll_deg':np.degrees(fit.x[3:6]).tolist(),'root_rotation_matrix':R.tolist(),'joint_increments_deg':np.degrees(qs[i]).tolist(),'pad_prediction_xyz_m':(pads@R.T+fit.x[:3]).tolist(),'skin_pad_prediction_xyz_m':(skin[:5]@R.T+fit.x[:3]).tolist(),'task':policy['tasks'][pose],'bounded':bool(np.all(fit.x>=lo-1e-10) and np.all(fit.x<=hi+1e-10))}
 diagnostics[s]={'success':bool(fit.success),'status':int(fit.status),'message':fit.message,'nfev':fit.nfev,'njev':fit.njev,'cost':float(fit.cost),'optimality':float(fit.optimality),'one_initialization':True,'restart_count':0,'elapsed_sec_since_start':time.monotonic()-starttime,'active_bound_variables':np.flatnonzero(fit.active_mask).tolist()}
 print(s,json.dumps(diagnostics[s]),flush=True)
 for p in ps:print(p,'root',poses[p]['root_xyz_m'],'angles',poses[p]['joint_increments_deg'],'pads_mm',(np.array(poses[p]['pad_prediction_xyz_m'])*1000).round(2).tolist(),flush=True)
dump('SOLVED_STATIC_POSES_R1.json',{'policy_sha256':sha(P/'STATIC_POSTURE_POLICY_R1.json'),'script_sha256':sha(Path(__file__)),'candidate_count':1,'poses':poses,'solver_diagnostics':diagnostics,'proxy_indices':{s:models[s]['sample_indices'] for s in models},'continuous_action_count':0,'dynamic_transition_proven':False})
