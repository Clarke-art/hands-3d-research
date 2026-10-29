from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent; ROOT=P.parents[1]; R6=ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(n,v): (P/n).write_text(json.dumps(v,indent=2),encoding='utf8')
old=json.loads((R6/'PROTECTED_INPUTS_BEFORE.json').read_text(encoding='utf8'))
changed=[p for p,h in old.items() if not Path(p).exists() or sha(p)!=h]
assert not changed,changed
for p in R6.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:old[str(p)]=sha(p)
save('PROTECTED_INPUTS_BEFORE.json',old)
source=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend'
assert sha(source)=='d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7'
save('STRATEGY_LOCK.json',dict(method='CONTACT_GUIDED_LIGHTWEIGHT_ANIMATION',source=str(source),source_sha256=sha(source),candidate_limit=1,budget_sec=600,heavy_solver_calls=0,nonlinear_optimizer=False,local_search='Deterministic bounded coordinate probes; three sweeps; three non-active fingers only',frame_hz=30,render_hz=60,trust_degrees=[5,7,5,5],steps_degrees=[2,1,.5],source_contact_guard_sec=.025,blend_ramp_sec=.16,temporal_gaussian_sigma_frames=2,geometry='Actual frozen skin samples; convex local digit envelopes; actual nearby black key boxes',preserve=['root','left','thumb','little','keys','MIDI','audio','cameras'],special_note_pose_patches=False))
sys.path.insert(0,str(R6))
import whole_phrase_model as m
q=m.source_angles(m.np.arange(715)/120)
print('PROTECTED',len(old),'SOURCE_VERIFIED',flush=True)
print('SOURCE_Q_MIN',q.min(0).tolist(),'MAX',q.max(0).tolist(),flush=True)
