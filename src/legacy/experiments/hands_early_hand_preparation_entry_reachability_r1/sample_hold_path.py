from coupled_model import *
from kinematic_derivative_api import motion_derivatives
cfg=json.loads((O/'EXPERIMENT_CONFIG.json').read_text(encoding='utf8'));z0=np.array(cfg['initial_latent']);zj=np.array(cfg['boundary_reference']);aa=np.load(O/'PREPARATION_KEY_STATES.npz')['angles'][0]
span=cfg['junction']-cfg['start'];ct=cfg['contacts'][0];normal_z=c.axisrot(-aa[ct['midi']-21],c.KEYS[ct['midi']-21]['press_axis'])[2,2]
template=DynamicNode(z0,[ct],aa,cfg['start'],(LOW,HIGH))
def path(t):
 fraction=(t-cfg['start'])/span;z=(1-fraction)*z0+fraction*zj;z[11]=zj[11]*fraction**3
 if abs(t-cfg['start'])<1e-12:return z0.copy()
 for it in range(3):z[2]-=template.value(z)[0]/normal_z
 return z
if len(sys.argv)>1:
 times=json.loads((O/'HOLD_ADAPTIVE_TIMES.json').read_text(encoding='utf8'));label='ADAPTIVE'
else:
 times=sorted(set([cfg['start']+i/120 for i in range(int(span*120)+1)]+[2.72,cfg['junction']-1e-6,cfg['junction']]+[cfg['start']+span*f for f in np.arange(.525,.901,.025)]));label='BASE'
requests=[];motion=[];h=1e-5
for idx,t in enumerate(times):
 z=path(t);zm=path(max(cfg['start'],t-h));zp=path(min(cfg['junction'],t+h));dt=min(cfg['junction'],t+h)-max(cfg['start'],t-h);zd=(zp-zm)/dt
 w,st=KIN(z);wm=KIN(zm)[0];wp=KIN(zp)[0];speed=np.linalg.norm(np.array(wp-wm))*1000/dt;rates=(state(zp)[6:]-state(zm)[6:])/dt
 acc=None
 if t>cfg['start']+h and t<cfg['junction']-h:acc=float(np.linalg.norm(np.array(wp-2*w+wm))*1000/h**2)
 requests.append(dict(id='hold_path_'+label.lower()+'_'+str(idx),display_time=t,contacts=[ct],latent=z.tolist(),state=state(z).tolist()))
 motion.append(dict(time=t,wrist_world_m=np.array(w).ravel().tolist(),wrist_local_fd_speed_mm_s=float(speed),latent_rates=zd.tolist(),mapped_joint_rates_deg_s=rates.tolist(),acceleration_local_fd_mm_s2=acc,domain_pass=bool(np.all(z>=LOW-1e-9)&np.all(z<=HIGH+1e-9)),wrist_pass=bool(speed<=500),mapped_joint_pass=bool(np.max(abs(rates))<=240),latent_rate_pass=bool(np.all(abs(zd)<=np.r_[[500]*3,[120]*3,[240]*4,5,8]+1e-6))))
save('HOLD_PATH_'+label+'_REQUESTS.json',requests);save('HOLD_PATH_'+label+'_MOTION.json',motion)
save('HOLD_PATH_DEFINITION.json',dict(status='DIAGNOSTIC_HOLD_CONTINUATION_ONLY',start=cfg['start'],end=cfg['junction'],frozen_start=z0,reference=zj,interpolation='root/other controls linear; preparing middle flex alpha=fraction**3; root-Z follows actual G4 minimum clipped pulp-face gap',contact_residual_target_mm=-.005,actual_early_preparation_trajectory='NOT_EXECUTED; no RELEASE/PRESS entry path is constructed',geometric_projection='3 deterministic normal transports per evaluation, not nonlinear optimization',sweep_not_global_search=True,position_continuity='analytic controls plus contact projection; only sampled local branch continuity verified, no universal proof',source_key_angle_in_hold_constant=float(aa[ct['midi']-21])))
print('SAMPLES',label,len(requests),'motionmax',max(r['wrist_local_fd_speed_mm_s'] for r in motion),max(max(abs(x) for x in r['mapped_joint_rates_deg_s']) for r in motion),flush=True)
