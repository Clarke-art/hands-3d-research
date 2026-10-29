import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
sc,rig,mesh,left,lrig=s.open_scene(SOURCE);g.init()
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
contexts=[(0.,1.35),(2.1,3.35)]
rn=[n for n in NOTES if n['hand']=='R' and n['finger']==2]
def role(t):
 for r,fn in [('ACTIVE',lambda n:n['note_on']<=t<n['note_off']),('RELEASE',lambda n:n['note_off']<=t<n['note_off']+.04),('PREPARE',lambda n:n['note_on']-.18<=t<n['note_on'])]:
  if any(fn(n) for n in rn):return r
 return 'IDLE'
def smooth(x):
 x=np.clip(x,0,1);return float(x*x*x*(10+x*(-15+6*x)))
def role_gate(t):
 if role(t)!='IDLE':return 0.
 before=max([0.]+[n['note_off']+.04 for n in rn if n['note_off']+.04<=t])
 after=min([5.95]+[n['note_on']-.18 for n in rn if n['note_on']-.18>=t])
 return smooth((t-before)/.18)*smooth((after-.04-t)/.18)
signals=[];episodes=[]
for start,end in contexts:
 hit=[]
 for t in np.unique(np.r_[np.arange(start,end+1e-8,1/60),end]):
  if role(t)!='IDLE':continue
  c.settime(sc,float(t));V,T,F=s.coords_tri(mesh);rows=g.keycheck(V,black_only=True,deep=False)
  # Conservative true-skin triangle AABB proximity; no proxy bones or pads.
  tri=V[g.IT];lo=tri.min(1);hi=tri.max(1);risk=[]
  for comp in g.comps:
   if comp[0]['color']!='BLACK':continue
   kv,P=g.actual(comp);gap=np.linalg.norm(np.maximum(0,np.maximum(kv.min(0)-hi,lo-kv.max(0))),axis=1)
   if gap.min()<=.003:risk.append(comp[0]['note_name'])
  signals.append(dict(time=t,role='IDLE',risk_black_keys=risk,geometry=rows))
  if risk:hit.append(float(t))
 if not hit:continue
 groups=[[hit[0]]]
 for t in hit[1:]:
  if t-groups[-1][-1]<=.12:groups[-1].append(t)
  else:groups.append([t])
 for group in groups:episodes.append(dict(first=group[0],last=group[-1],context=[start,end]))
def envelope(t):
 gain=0.
 for e in episodes:
  a,b=e['first'],e['last'];start,end=e['context']
  w=smooth((t-(a-.18))/.18)*smooth(((b+.18)-t)/.18)
  w*=smooth((t-start)/.18)*smooth((end-t)/.18)
  gain=max(gain,w)
 return gain*role_gate(t)
delta=np.array([-16.,6.,3.,0.]);bounds=np.array(read(ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json')['joint_bounds_deg'])[1]
paths={f'pose.bones["{name}"].rotation_quaternion' for name in c.SETUPS['R','INDEX'][0]}
original=rig.animation_data.action;outside_payload=c.digest(s.payload(original,paths));before=s.protected_state(True);native={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
fc=[f for f in s.curves(original) if f.data_path in paths]
assert set(k.interpolation for f in fc for k in f.keyframe_points)=={'LINEAR'},'Need preserve non-linear source rather than rebake it'
times=np.unique(np.r_[np.arange(0,1.35+1e-8,1/240),np.arange(2.1,3.35+1e-8,1/240),[n['note_on']-.18-.04 for n in rn],26/60,2.6])
times=times[(times>=0)&(times<=3.35)]
records=[];quats=[];last=None
for t in times:
 c.settime(sc,float(t));q=s.degrees('INDEX');w=envelope(float(t));nq=q.copy()
 if w>0:nq=q+w*(np.clip(q+delta,bounds[0],bounds[1])-q)
 if w>0:g.joint_set(nq)
 qs=np.array([list(rig.pose.bones[n].rotation_quaternion) for n in c.SETUPS['R','INDEX'][0]])
 if last is not None:
  for j in range(3):
   if qs[j]@last[j]<0:qs[j]*=-1
 last=qs.copy();quats.append(qs);records.append(dict(time=t,gain=w,base_qdeg=q,qdeg=nq,role=role(float(t))))
action=original.copy();action.name='IDLE_INDEX_BLACK_KEY_CLEARANCE_B_NOT_APPROVED';rig.animation_data.action=action
times=np.array(times);quats=np.array(quats)
for f in s.curves(action):
 if f.data_path not in paths:continue
 j=c.SETUPS['R','INDEX'][0].index(f.data_path.split('"')[1]);ix=f.array_index
 # Source curves are piecewise linear. Keep every original key and insert
 # source-evaluated boundary keys, so values outside edit support stay exact.
 changes={float(1+60*t):float(quats[i,j,ix]) for i,t in enumerate(times)}
 for k in f.keyframe_points:
  t=(k.co.x-1)/60
  if envelope(t)>0:
   changes[float(k.co.x)]=float(np.interp(t,times,quats[:,j,ix]))
 for frame,val in sorted(changes.items()):
  k=f.keyframe_points.insert(frame,val,options={'FAST'});k.interpolation='LINEAR'
 f.update()
assert outside_payload==c.digest(s.payload(action,paths))
assert before==s.protected_state(True)
assert native=={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
save('STRATEGY_AND_ENVELOPE.json',dict(strategy='IDLE_INDEX_BLACK_KEY_CLEARANCE',configuration='B',tested_configurations={'A':[-10,4,2,0],'B':delta},contexts=contexts,episodes=episodes,trigger='Actual evaluated INDEX skin triangles within conservative 3mm AABB distance to actual Action-driven black-key meshes; baseline feed-forward local episodes, no note/key special cases',envelope='quintic smoothstep 180ms entry/exit; 180ms role gate; zero 40ms before PREPARE; 180ms scope boundary fades',bounds_deg=bounds,records=records,signals=signals,source_linear=True,outside_index_action_digest=outside_payload,native=native,protected_actions=before))
c.settime(sc,26/60);sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
dest=OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend';assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
save('CANDIDATE_RECEIPT.json',dict(path=str(dest),sha256=sha(dest),original_sha256=sha(SOURCE),approved=False))
protection('BUILD_INPUT_RECEIPT.json');print('BUILD_DONE',episodes,flush=True)
