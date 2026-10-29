import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent
p=O/'coupled_model.py';s=p.read_text(encoding='utf8');before=hashlib.sha256(s.encode()).hexdigest()
assert "cross_margins=[]" not in s
s=s.replace('candidates=[]','candidates=[];cross_margins=[]')
s=s.replace('for vi,point in enumerate(poly):candidates.append',"if poly:cross_margins.append(min(-min(a[2]-s['z'] for a in poly),max(a[2]-s['z'] for a in poly))*1000)\n   for vi,point in enumerate(poly):candidates.append")
# Preserve original indentation for the inserted loop: the original was 5 spaces, not 3.
s=s.replace('\n   for vi,point in enumerate(poly):candidates.append','\n     for vi,point in enumerate(poly):candidates.append')
for term in ["(pt[0]-s['xmin'])*1000-.001","(s['xmax']-pt[0])*1000-.001","(pt[1]-s['ymin'])*1000-.001","(s['ymax']-pt[1])*1000-.001"]:s=s.replace(term,term.replace('-.001',''))
s=s.replace('maxgap*1000-.001','max(cross_margins)-.001')
compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
(O/'CONTACT_PROXY_REPAIR.json').write_text(json.dumps(dict(reason='Measured selected-polygon max-gap inequality jumps 1.735mm for a 1e-6 control perturbation despite unchanged true contact requirement',before_sha256=before,after_sha256=hashlib.sha256(s.encode()).hexdigest(),changes=['Crossing margin is max over all projected pulp triangles of min(-min_gap,max_gap): true existence of a crossing face, no selected-face polygon height jump','Clipped witness may lie on playable boundary; artificial 0.001mm witness inset removed. Original pad inset remains, actual pad-inside/area/crossing contract unchanged.'],physical_acceptance_gates_unchanged=True,historical_module_unchanged=True,derivative_guard_not_disabled=True),indent=2),encoding='utf8')
from guarded_node import *
cfg=json.loads((O/'EXPERIMENT_CONFIG.json').read_text(encoding='utf8'));probe=json.loads((O/'DELAYED_FLEX_REQUESTS.json').read_text(encoding='utf8'));actions=json.loads((O/'REAL_ACTION_EVENT_STATES.json').read_text(encoding='utf8'))['rows']
def angles(t):
 src=json.loads((O.parent/'hands_contact_state_motion_planner_comparison_r1/ORIGINAL_ACTION_INSPECTION.json').read_text(encoding='utf8'));out=np.zeros(88)
 for idx,curves in src['fcurves'].items():
  for curve in curves:
   if curve['path']=='rotation_euler' and curve['index']==0:
    points=curve['points'];out[int(idx)]=np.interp(t,[r['display_time'] for r in points],[r['angle'] for r in points])
 return out
times=[cfg['start']]+[r['display_time'] for r in probe[:3]]+[cfg['junction'],(cfg['junction']+cfg['end'])/2,cfg['end']]
zs=[cfg['initial_latent']]+[r['latent'] for r in probe[:3]]+[cfg['boundary_reference']]
keys=[angles(t) for t in times];cts=[[cfg['contacts'][0]] for t in times[:4]]+[cfg['contacts'],[cfg['contacts'][1]],[cfg['contacts'][1]]]
for t,aa in zip(times[5:],keys[5:]):
 z=np.array(cfg['boundary_reference']);dt=t-cfg['junction'];z[6]=max(0,z[6]-240*dt);z[9]-=240*dt
 nd=DynamicNode(z,[cfg['contacts'][1]],aa,t,(LOW,HIGH))
 for it in range(3):
  v=nd.value(z);ct=cfg['contacts'][1];nz=c.axisrot(-aa[ct['midi']-21],c.KEYS[ct['midi']-21]['press_axis'])[2,2];z[2]-=v[0]/nz
 zs.append(z.tolist())
motion=dict(wrist_speed_mm_s=500,latent_velocity=np.r_[[500]*3,[120]*3,[240]*4,5,8].tolist(),mapped_joint_rate_deg_s=240)
save('ENTRY_SOLVE_INPUT.json',dict(time_grid=times,initial_latent=zs,contact_sets=cts,moving_keys=[a.tolist() for a in keys],joint_domain=dict(lower=LOW,upper=HIGH),motion_bounds=motion,fixed_start=True,endpoint_is_adjustable=True,endpoint_target='Any original-contract E5 feasible state; old local vector not imposed',initialization='Early delayed preparing-finger flex; genuine common boundary; normal transport to source E5 Action with bounded thumb release controls',source_key_angle_reconstruction='Original LINEAR Action point reconstruction; final Blender reads real Action independently'))
print('ENTRY_INPUT',times,flush=True)
