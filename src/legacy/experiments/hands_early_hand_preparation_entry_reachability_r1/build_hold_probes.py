from coupled_model import *
cfg=json.loads((O/'EXPERIMENT_CONFIG.json').read_text(encoding='utf8'))
z0=np.array(cfg['initial_latent']);zj=np.array(cfg['boundary_reference']);a=np.load(O/'PREPARATION_KEY_STATES.npz')['angles'][0]
requests=[];traces=[]
for fraction in cfg['hold_probe_fractions']:
 z=(1-fraction)*z0+fraction*zj; node=DynamicNode(z,[cfg['contacts'][0]],a,cfg['start']+(cfg['junction']-cfg['start'])*fraction,(LOW,HIGH));trace=[]
 for step in range(3):
  v=node.value(z);ct=cfg['contacts'][0];k=c.KEYS[ct['midi']-21];nz=c.axisrot(-a[ct['midi']-21],k['press_axis'])[2,2];trace.append(dict(residual_mm=float(v[0]),signature=node.last_signature[0]));z[2]-=v[0]/nz
 v=node.value(z);rid='hold_probe_'+str(len(requests));req=dict(id=rid,display_time=cfg['start']+(cfg['junction']-cfg['start'])*fraction,contacts=[cfg['contacts'][0]],latent=z.tolist(),state=state(z).tolist(),fraction=fraction);requests.append(req)
 traces.append(dict(id=rid,trace=trace,domain_pass=bool(np.all(z>=LOW)&np.all(z<=HIGH)),constraint_violation=float(max(abs(v[0]),max(0,-v[1:].min()))),middle_pad_world_m=skin(state(z))[int(RAW['pad_indices'][cfg['contacts'][1]['finger']-1])].tolist(),numerical_optimization=False))
save('HOLD_PROBE_REQUESTS.json',requests);save('HOLD_PROBE_NUMERIC.json',traces)
print([(r['id'],r['constraint_violation'],r['domain_pass']) for r in traces],flush=True)
