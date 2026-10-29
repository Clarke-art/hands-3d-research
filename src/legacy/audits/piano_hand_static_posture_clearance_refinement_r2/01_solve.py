import sys,json,hashlib,time
sys.dont_write_bytecode=True
from pathlib import Path
P=Path(__file__).resolve().parent;R1=P.parent/'piano_hand_four_pose_static_feasibility_r1';OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1'
sys.path.insert(0,str(OLD/'_deps'));sys.path.insert(0,str(OLD))
import numpy as np
from scipy.optimize import least_squares
import performance_core as c
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
policy=read(P/'STATIC_REFINEMENT_POLICY_R2.json');lock=read(P/'PRE_SOLVE_LOCK_R2.json');assert sha(P/'STATIC_REFINEMENT_POLICY_R2.json')==lock['policy_sha256'] and sha(Path(__file__))==lock['solver_script_sha256']
assert not (P/'SOLVED_STATIC_POSES_R2.json').exists(),'No restart or result overwrite.'
data=read(R1/'FORMAL_INPUT_EXTRACTION_R1.json');DIGITS=c.DIGITS;KEYS=c.KEYS;w=policy['solver']['residual_weights'];models={};timer=time.monotonic()
surfs=np.array([[v[n] for n in ['xmin','xmax','ymin','ymax','z']] for key in KEYS for v in key['key_top_playable_surface']])
def height(pts):
 mask=(pts[:,None,0]>=surfs[:,0])&(pts[:,None,0]<=surfs[:,1])&(pts[:,None,1]>=surfs[:,2])&(pts[:,None,1]<=surfs[:,3]);return np.max(np.where(mask,surfs[:,4],-.1),axis=1)
def rootrot(x):return c.rz(x[3])@c.axisrot(x[4],[1,0,0])@c.axisrot(x[5],[0,1,0])
for s in ['L','R']:
 d=data[s];V=np.array(d['rest_vertices_canonical']);W=np.array(d['weights']);names=d['bone_names'];bones=c.RIG[s]['bones'];rest={n:np.array(bones[n]['matrix']) for n in names};inv={n:np.linalg.inv(rest[n]) for n in names};weighted=np.c_[V,np.ones(len(V))][:,None,:]*W[:,:,None]
 band=policy['solver']['planned_key_bands'][s];boxes=[];midis=[]
 for k in KEYS:
  if band[0]<=k['midi_note']<=band[1]:
   for g in k['geometry']:
    verts=np.array(g['vertices']);boxes.append([verts.min(0),verts.max(0)]);midis.append(k['midi_note'])
 boxes=np.array(boxes);palmwrist=V[:,1]<.105;patches={j:np.linalg.norm(V-V[c.MARKERS[s][j]['mesh_vertex']],axis=1)<.018 for j in range(5)}
 models[s]={'names':names,'bones':bones,'rest':rest,'inv':inv,'weighted':weighted,'boxes':boxes,'box_midis':np.array(midis),'palmwrist':palmwrist,'patches':patches}
def local(s,q):
 m=models[s];basis={}
 for j,d in enumerate(DIGITS):
  for n,r in zip(c.SETUPS[s,d][0],c.joint_mats(s,d,q[j])):
   B=np.eye(4);B[:3,:3]=r;basis[n]=B
 pose={}
 def get(n):
  if n not in pose:
   par=m['bones'][n]['parent'];pose[n]=(get(par)@m['inv'][par]@m['rest'][n] if par else m['rest'][n])@basis.get(n,np.eye(4))
  return pose[n]
 matrices=np.array([get(n)@m['inv'][n] for n in m['names']]);skin=np.einsum('bij,nbj->nbi',matrices,m['weighted']).sum(1)[:,:3];pads=np.array([(get(r['distal_frame'])@np.r_[r['local_pad_point'],1])[:3] for r in c.MARKERS[s]])
 return pads,skin
def boxes_penalty(s,V,task):
 m=models[s];b=m['boxes'];center=(b[:,0]+b[:,1])/2;half=(b[:,1]-b[:,0])/2
 signed_components=np.abs(V[:,None,:]-center[None,:,:])-half[None,:,:]
 sdf=np.linalg.norm(np.maximum(signed_components,0),axis=2)+np.minimum(np.max(signed_components,axis=2),0)
 margin=np.full(sdf.shape,.002);margin[m['palmwrist']]=.005
 if task['active_finger'] is not None:
  patch=m['patches'][task['active_finger']-1];own=m['box_midis']==task['active_midi'];margin[np.ix_(patch,own)]=0
 return np.maximum(np.max(margin-sdf,axis=1),0)
def regions(midi,active,s,j):
 k=KEYS[midi-21];ss=k['key_top_playable_surface'];loy=min(t['ymin'] for t in ss);hiy=max(t['ymax'] for t in ss);out=[]
 for a,t in enumerate(ss):
  frontonly=k['color']=='WHITE' and (active or (s=='R' and j in [1,3]))
  if frontonly and a>0:continue
  ix=.003 if k['color']=='WHITE' else .002;iy=.007 if k['color']=='WHITE' else .002
  lower=np.array([t['xmin']+ix,t['ymin']+(iy if t['ymin']<=loy+1e-7 else 0)]);upper=np.array([t['xmax']-ix,t['ymax']-(iy if t['ymax']>=hiy-1e-7 or active else 0)])
  if s=='R' and j in [1,3] and k['color']=='WHITE':upper[1]=min(upper[1],.045)
  out.append((lower,upper,t['z']))
 return out
def region_delta(pt,boxes):
 vals=[pt[:2]-np.clip(pt[:2],lo,hi) for lo,hi,z in boxes];j=int(np.argmin([v@v for v in vals]));return vals[j],boxes[j][2]
poses={};diag={}
for s,ps in [('L',['L1','L2']),('R',['R1','R2'])]:
 rb=policy['root_bounds'][s];roots=np.array(rb['xyz_mm'])/1000;rots=np.radians(policy['root_bounds']['yaw_pitch_roll_deg']);lo=np.r_[roots[0],rots[0]];hi=np.r_[roots[1],rots[1]];priors=[];qlo=[];qhi=[]
 for pose in ps:
  priors.append(np.radians(policy['priors_deg'][pose]))
  for j,d in enumerate(DIGITS):
   typ='THUMB' if j==0 else 'LEFT_IDLE_'+d if s=='L' and j in [1,2,3] else 'LONG';b=np.radians(policy['joint_increment_bounds_deg'][typ]);qlo.extend(b[0]);qhi.extend(b[1])
 lo=np.r_[lo,qlo];hi=np.r_[hi,qhi];qlo=np.array(qlo).reshape(2,5,4);qhi=np.array(qhi).reshape(2,5,4);seed=np.r_[np.array(rb['seed_xyz_mm'])/1000,np.radians(policy['root_bounds']['seed_yaw_pitch_roll_deg'][s])];x0=np.r_[seed,np.array(priors).flatten()];evalcalls=0;lastnote=time.monotonic()
 def residual(x):
  global evalcalls,lastnote
  evalcalls+=1;R=rootrot(x);root=x[:3];qs=x[6:].reshape(2,5,4);out=[]
  for i,pose in enumerate(ps):
   task=policy['tasks'][pose];q=qs[i];lp,ls=local(s,q);pads=lp@R.T+root;skin=ls@R.T+root;active=task['active_finger'];prep={int(k)-1:v for k,v in task['prepared'].items()};tasks=dict(prep);jw=np.full(5,w['other_joint_rad'])
   if s=='L':jw[1:4]=w['left_idle_joint_rad']
   if active is not None:tasks[active-1]=task['active_midi'];jw[active-1]=w['active_joint_rad']
   for j,midi in tasks.items():
    isactive=active==j+1;reg=regions(midi,isactive,s,j);d,z=region_delta(pads[j],reg);key=KEYS[midi-21];digit=DIGITS[j];prefx=key['key_center'][0]+(policy['contact_regions']['left_preferred_x_offset_from_center_mm'].get(digit,0)/1000 if s=='L' else 0);prefy=(policy['contact_regions']['black_preferred_y_mm'] if key['color']=='BLACK' else policy['contact_regions']['white_preferred_y_mm'].get(digit,35))/1000
    if isactive:
     out.extend(d*1000*w['active_contact_mm']);out.append((pads[j,2]-z-.0005)*1000*w['active_contact_mm']);sk=skin[c.MARKERS[s][j]['mesh_vertex']];sd,sz=region_delta(sk,reg);out.extend(sd*1000*w['active_skin_contact_mm']);out.append((sk[2]-sz-.0005)*1000*w['active_skin_contact_mm'])
    else:
     out.extend(d*1000*w['prepared_region_mm']);gap=pads[j,2]-z;out.append((gap-np.clip(gap,.004,.018))*1000*w['prepared_gap_interval_mm']);out.append((gap-.008)*1000*w['prepared_preferred_height_mm'])
    out.extend((pads[j,:2]-[prefx,prefy])*1000*w['preferred_xy_mm'])
   out.extend(((q-priors[i])*jw[:,None]).flatten());out.extend(boxes_penalty(s,skin,task)*1000*w['full_skin_clearance_mm'])
   # Penalize saturated flexion without changing the declared hard bounds.
   relax=np.maximum(q[:,:3]-(qhi[i,:,:3]-.10*(qhi[i,:,:3]-qlo[i,:,:3])),0);out.extend((relax*w['joint_limit_relief_rad']).flatten())
   idle=np.ones(5)
   if active is not None:idle[active-1]=0
   out.extend(np.maximum(height(pads)+.004-pads[:,2],0)*idle*1000*w['idle_pad_clearance_mm'])
  out.extend(((qs[1]-qs[0])*w['paired_joint_difference_rad']).flatten());out.extend((x[:3]-seed[:3])*1000*w['root_prior_mm']);out.extend((x[3:6]-seed[3:6])*w['root_rotation_rad'])
  if time.monotonic()-lastnote>20:print('SOLVING',s,'residual_calls',evalcalls,'elapsed',round(time.monotonic()-timer,1),flush=True);lastnote=time.monotonic()
  return np.array(out)
 fit=least_squares(residual,x0,bounds=(lo,hi),max_nfev=policy['solver']['max_nfev_per_pair'],xtol=policy['solver']['xtol'],ftol=policy['solver']['ftol'],gtol=policy['solver']['gtol'])
 assert np.isfinite(fit.x).all();R=rootrot(fit.x);qs=fit.x[6:].reshape(2,5,4)
 for i,pose in enumerate(ps):
  pads,skin=local(s,qs[i]);poses[pose]={'hand':s,'root_xyz_m':fit.x[:3].tolist(),'root_yaw_pitch_roll_deg':np.degrees(fit.x[3:6]).tolist(),'root_rotation_matrix':R.tolist(),'joint_increments_deg':np.degrees(qs[i]).tolist(),'pad_prediction_xyz_m':(pads@R.T+fit.x[:3]).tolist(),'skin_pad_prediction_xyz_m':(skin[[r['mesh_vertex'] for r in c.MARKERS[s]]]@R.T+fit.x[:3]).tolist(),'task':policy['tasks'][pose],'bounded':bool(np.all(fit.x>=lo-1e-10) and np.all(fit.x<=hi+1e-10))}
 diag[s]={'success':bool(fit.success),'status':int(fit.status),'message':fit.message,'nfev':fit.nfev,'njev':fit.njev,'residual_calls':evalcalls,'cost':float(fit.cost),'optimality':float(fit.optimality),'one_initialization':True,'restart_count':0,'active_bound_variables':np.flatnonzero(fit.active_mask).tolist(),'elapsed_sec':time.monotonic()-timer}
 print('SOLVED',s,json.dumps(diag[s]),flush=True)
 for pose in ps:print(pose,'root_mm',(np.array(poses[pose]['root_xyz_m'])*1000).round(2).tolist(),'root_deg',np.round(poses[pose]['root_yaw_pitch_roll_deg'],2).tolist(),'q_deg',np.round(poses[pose]['joint_increments_deg'],2).tolist(),'pads_mm',(np.array(poses[pose]['pad_prediction_xyz_m'])*1000).round(2).tolist(),flush=True)
dump('SOLVED_STATIC_POSES_R2.json',{'policy_sha256':sha(P/'STATIC_REFINEMENT_POLICY_R2.json'),'script_sha256':sha(Path(__file__)),'candidate_count':1,'poses':poses,'solver_diagnostics':diag,'full_skin_proxy_vertex_count':3300,'dynamic_transition_proven':False,'continuous_action_count':0})
