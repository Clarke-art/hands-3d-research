from repair_model import *
import hashlib
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
old=json.loads((ROOT/'audits/piano_pedagogical_demonstration_audit_r1/PROTECTED_INPUTS_BEFORE.json').read_text(encoding='utf8'))
assert all(Path(p).exists() and sha(p)==h for p,h in old.items())
for p in (ROOT/'audits/piano_pedagogical_demonstration_audit_r1').rglob('*'):
 if p.is_file():old[str(p)]=sha(p)
(P/'PROTECTED_INPUTS_BEFORE.json').write_text(json.dumps(old,indent=2),encoding='utf8')
probes=json.loads((P/'SOURCE_PROBES.json').read_text());errors=[]
for p in probes:
 predicted=m.Skin([p['time']])(np.array(p['qdeg'])[None])[0];actual=np.array(p['vertices']);errors.append(float(np.linalg.norm(predicted-actual,axis=1).max()*1000))
assert max(errors)<.25,errors
lock=dict(method='CONTACT_GUIDED_LIGHTWEIGHT_ANIMATION',source_sha256='18d3c729ff16759a4a7b41a621a1682711d876ad2e109a748d1ea9e675762df3',formal_attempts=1,candidate_limit=1,budget_sec=300,heavy_solver_calls=0,windows=[[.90,1.78],[2.25,2.95],[3.50,4.35],[4.55,5.40]],window_fade_sec=.12,active_protection='Exact note_on through note_off; 15ms pre-on guard. Release is free immediately after actual note_off.',prepare_ramp_sec=.09,release_ramp_sec=.055,trust_degrees=[14,20,16,14],steps_degrees=[4,2,1],coordinate_sweeps_per_step=3,frame_hz=60,smoothing_sigma_frames=1.0,correction_velocity_limit_deg_sec=210,geometry='Frozen weighted skin, five local digit envelopes; actual nearby moving key bodies. No full hand nonlinear optimizer.',source_model_max_error_mm=errors,style_penalty=.003,temporal_penalty=.004,black_clearance_mm=.8,neighbor_clearance_mm=.7,per_note_pose_patches=False)
with (P/'STRATEGY_LOCK.json').open('x',encoding='utf8') as f:json.dump(lock,f,indent=2)
print('LOCKED',len(old),'files; source-model errors mm',errors,flush=True)
