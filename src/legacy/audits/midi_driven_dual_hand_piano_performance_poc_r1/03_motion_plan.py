from performance_core import *
from scipy.optimize import least_squares
policy={'candidate_count':1,'source_actions_used':False,'scale':1,'root':'one bounded shared neutral palm placement per hand optimized over all home fingers; constant across excerpt, never per-note teleport','root_height_m':[.055,.085],'root_yaw_deg':[-12,12],'finger_DOF':'3 bounded palmar flexions plus base spread; no axial twist; no negative flexion','long_finger_flex_bounds_deg':[[0,75],[0,95],[0,65]],'thumb_flex_bounds_deg':[[0,40],[0,55],[0,55]],'base_spread_deg':{'thumb':[-35,35],'other':[-28,28]},'target_hover_m':.012,'phases_seconds':{'PREPARATION_before_on':.18,'APPROACH_before_on':.10,'CONTACT':0,'KEY_PRESS_after_on':.035,'RELEASE_after_off':.07,'NEXT_NOTE_TRANSITION':'return to home hover through same release curve'},'key_audio_clock':'same absolute timeline; NOTE_ON is first contact and key-down start; key reaches full travel 35ms later','optimizer':'one global home placement solve per hand (max200 evaluations), then one deterministic sequential local joint solve per finger and120Hz observation (max35 evaluations); no random restarts or tuning sweeps','contact_tolerance_mm':{'vertical':3,'horizontal':2},'skin_variant_count':1}
dump('GENERATION_POLICY_R1.json',policy)
dump('PRE_GENERATION_LOCK_R1.json',{'policy_sha256':sha(P/'GENERATION_POLICY_R1.json'),'timeline_sha256':sha(P/'PERFORMANCE_TIMELINE_R1.json'),'fingering_sha256':sha(P/'PROVISIONAL_FINGERING_PLAN_R1.json')})
design=read(P/'SONG_DATA_R1.json')['execution_layout'];homes={s:design[s]['home_midi_by_finger'] for s in ['R','L']};ys={s:design[s]['home_depth_m_by_finger'] for s in ['R','L']}
solution={};data={};times=np.arange(round(DURATION*HZ)+1)/HZ
for s in ['R','L']:
 targets=np.array([keypoint(m,y)+[0,0,.012] for m,y in zip(homes[s],ys[s])]);center=design[s]['root_seed_x_m']
 x0=np.r_[center,-.077,.066,0,np.concatenate([prior(d) for d in DIGITS])]
 low=np.r_[center-.035,-.11,.055,np.radians(-12),np.concatenate([bounds(d)[0] for d in DIGITS])];high=np.r_[center+.035,-.045,.085,np.radians(12),np.concatenate([bounds(d)[1] for d in DIGITS])]
 def residual(x):
  root=x[:3];R=rz(x[3]);q=x[4:].reshape(5,4);err=[]
  for j,d in enumerate(DIGITS):
   pt,_=fk(s,d,q[j]);err.extend((root+R@pt-targets[j])*1000);err.extend((q[j]-prior(d))*.12)
  err.extend((x[:3]-x0[:3])*5);err.append(x[3]*.4);return err
 fit=least_squares(residual,x0,bounds=(low,high),max_nfev=200,ftol=1e-10,xtol=1e-10,gtol=1e-8);root=fit.x[:3];R=rz(fit.x[3]);q=fit.x[4:].reshape(5,4);homeq=q.copy();angles=[];pads=[];targetrows=[];errors=[]
 for t in times:
  row=[];points=[];tars=[]
  for j,d in enumerate(DIGITS):
   midi=homes[s][j];y=ys[s][j];target=keypoint(midi,y)+[0,0,.012]
   ns=[n for n in TL['notes'] if n['hand']==s and n['finger']==j+1]
   phase='PREPARATION';active_note=None
   for n in ns:
    a,b=n['note_on'],n['note_off']
    if a-.1<=t<a:
     target=keypoint(n['midi_note'],y)+np.array([0,0,.012*(1-smooth((t-(a-.1))/.1))]);phase='APPROACH';active_note=n;break
    if a<=t<b:
     target=keypoint(n['midi_note'],y,KEYS[n['key_index']]['press_angle_rad']*keypress(n,t));phase='CONTACT' if abs(t-a)<1e-8 else 'KEY_PRESS';active_note=n;break
    if b<=t<b+.07:
     target=keypoint(n['midi_note'],y,KEYS[n['key_index']]['press_angle_rad']*keypress(n,t))+[0,0,.012*smooth((t-b)/.07)];phase='RELEASE';active_note=n;break
   def localres(v):
    pt,_=fk(s,d,v);return np.r_[(root+R@pt-target)*1000,(v-homeq[j])*.07,(v-q[j])*.04]
   fitq=least_squares(localres,q[j],bounds=bounds(d),max_nfev=35,ftol=1e-8,xtol=1e-8,gtol=1e-7);q[j]=fitq.x;pt,_=fk(s,d,q[j]);world=root+R@pt;row.append(q[j].copy());points.append(world);tars.append(target)
   if active_note is not None and active_note['note_on']<=t<=active_note['note_off']:errors.append(float(np.linalg.norm(world-target)*1000))
  angles.append(row);pads.append(points);targetrows.append(tars)
 data[s+'_q']=np.array(angles);data[s+'_pads']=np.array(pads);data[s+'_targets']=np.array(targetrows);data[s+'_root']=root;data[s+'_yaw']=np.array(fit.x[3]);solution[s]={'home_midis_by_finger':homes[s],'home_depth_m_by_finger':ys[s],'root_xyz_m':root.tolist(),'root_yaw_deg':float(np.degrees(fit.x[3])),'home_joint_angles_deg':np.degrees(homeq).tolist(),'home_fit_max_error_mm':float(max(np.linalg.norm(root+R@fk(s,d,homeq[j])[0]-targets[j])*1000 for j,d in enumerate(DIGITS))),'active_target_max_error_mm':max(errors),'home_solver_evaluations':fit.nfev,'joint_step_max_deg_at120Hz':float(np.degrees(np.max(np.abs(np.diff(data[s+'_q'],axis=0))))) }
 print(s,solution[s],flush=True)
data['times']=times;data['key_angles']=np.array([angles_at(t) for t in times]);np.savez_compressed(P/'procedural_motion.npz',**data)
dump('HAND_MOTION_PLAN_R1.json',{'authority':'NEW_PROCEDURAL_CANDIDATE_FROM_PUBLIC_DOMAIN_MIDI_AND_DESIGNED_FINGERING','no_pianovam_action_or_landmarks':True,'shared_timebase':'PERFORMANCE_TIMELINE_R1.json','sample_rate':HZ,'duration':DURATION,'joint_order':['base_flex','middle_flex','distal_flex','base_spread'],'phase_policy':policy,'hands':solution,'stop_loss':'This is the only candidate. Do not tune again after visual failure; fix only implementation bugs.'})
