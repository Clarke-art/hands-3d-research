import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
src=(O/'batch_verify.py').read_text(encoding='utf8'); exec(compile(src[:src.index('args=sys.argv')],str(O/'batch_verify.py'),'exec'))
def js(name,d): (O/name).write_text(json.dumps(d,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()),encoding='utf8')
B=json.loads((O.parent/'hands_c01_anatomy_preparation_audit_r1/B_SOLVE_2.json').read_text(encoding='utf8'))
J=json.loads((O.parent/'hands_contact_junction_compatibility_r1/JUNCTION_STATIC_FEASIBILITY.json').read_text(encoding='utf8'))['attempts'][1]['numerical']
L=json.loads((O.parent/'hands_time_coupled_contact_recovery_r1/CORRECTION_SOLVE_RESULTS.json').read_text(encoding='utf8'))['nodes'][0]
start=2.527855; junction=I['junction_time']; end=L['display_time']; hold=I['contacts'][0]
z0=np.r_[B['state'][:10],B['lambda_reference'],0.]; zj=np.array(J['latent']); zl=np.array(L['latent'])
times=sorted(set([start,2.72,junction-1e-6,junction,junction+1e-6,end,2.956426]+[start+(junction-start)*x for x in [.25,.5,.75]]))
keyrows=[]
for t in times:
 u.settime(sc,t); keyrows.append(dict(time=t,angles=u.keyangles().tolist()))
js('REAL_ACTION_EVENT_STATES.json',dict(rows=keyrows,action_payloads=actual,native_identity=True,source_saved=False))
np.savez_compressed(O/'PREPARATION_KEY_STATES.npz',times=times,angles=[r['angles'] for r in keyrows])
anchors=[dict(id='B2_REPRODUCED',display_time=start,latent=z0.tolist(),state=B['state'],contacts=[hold]),dict(id='OLD_COMMON_REPRODUCED',display_time=junction,latent=zj.tolist(),state=J['state'],contacts=I['contacts']),dict(id='OLD_LOCAL_REPRODUCED',display_time=end,latent=zl.tolist(),state=L['state'],contacts=[I['contacts'][1]])]
rows=[]
for r in anchors:
 row=measure(r); rows.append(row); print('ANCHOR',r['id'],row['all_gates'],row['wrist_world_m'],flush=True)
js('ANCHOR_ACTUAL.json',rows);js('ANCHOR_REQUESTS.json',anchors)
js('EXPERIMENT_CONFIG.json',dict(task='PIANO_EARLY_HAND_PREPARATION_AND_ENTRY_REACHABILITY_R1',authority='DESIGN_PROVISIONAL',start=start,junction=junction,end=end,contacts=I['contacts'],initial_latent=z0.tolist(),boundary_reference=zj.tolist(),old_local_latent=zl.tolist(),hold_probe_fractions=[.25,.5,.75,1.],source_saved=False))
assert rows[0]['all_gates'] and rows[1]['all_gates'] and rows[2]['all_gates']
