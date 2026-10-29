from coupled_model import *
cfg=json.loads((O/'EXPERIMENT_CONFIG.json').read_text(encoding='utf8'));z0=np.array(cfg['initial_latent']);zj=np.array(cfg['boundary_reference']);a=np.load(O/'PREPARATION_KEY_STATES.npz')['angles'][0];out=[]
assert not (O/'DELAYED_FLEX_REQUESTS.json').exists()
for f in cfg['hold_probe_fractions']:
 z=(1-f)*z0+f*zj;z[11]=zj[11]*f**3;nd=DynamicNode(z,[cfg['contacts'][0]],a,cfg['start']+(cfg['junction']-cfg['start'])*f,(LOW,HIGH));trace=[]
 for it in range(3):
  v=nd.value(z);ct=cfg['contacts'][0];k=c.KEYS[ct['midi']-21];nz=c.axisrot(-a[ct['midi']-21],k['press_axis'])[2,2];trace.append(float(v[0]));z[2]-=v[0]/nz
 v=nd.value(z);out.append(dict(id='delayed_flex_'+str(len(out)),display_time=cfg['start']+(cfg['junction']-cfg['start'])*f,contacts=[cfg['contacts'][0]],latent=z.tolist(),state=state(z).tolist(),fraction=f,trace=trace,numeric_violation=float(max(abs(v[0]),max(0,-v[1:].min())))))
save('DELAYED_FLEX_REQUESTS.json',out);print([(r['id'],r['numeric_violation']) for r in out],flush=True)
save('DELAYED_FLEX_RATIONALE.json',dict(evidence='Actual collisions attributed to MIDDLE on intervening black keys C#5/D#5 during simultaneous flex/lateral travel',change='Keep same boundary and root/other controls; delay preparing finger flex with cubic fraction**3',maximum_alpha_rate=3*zj[11]/(cfg['junction']-cfg['start']),limit=8,optimization=False,derivative_failure_handling='First optimizer batch aborted unverified adaptive contact branches; this analytic preparation is not an optimizer derivative bypass and remains subject to all actual gates'))
