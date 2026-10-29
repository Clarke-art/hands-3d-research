from coupled_model import *
cfg=json.loads((O/'EXPERIMENT_CONFIG.json').read_text(encoding='utf8'));r=json.loads((O/'ENTRY_CORRECTION_RESULT.json').read_text(encoding='utf8'));times=np.array(r['times']);Z=np.array(r['latents']);actual=json.loads((O/'ENTRY_ACTUAL_SAMPLES.json').read_text(encoding='utf8'));i=next(i for i,a in enumerate(actual) if not a['all_gates']);lo=actual[i-1]['display_time'];hi=actual[i]['display_time'];rows=[]
for j in range(1,8):
 t=lo+(hi-lo)*j/8;seg=min(max(np.searchsorted(times,t,side='right')-1,0),len(times)-2);f=(t-times[seg])/(times[seg+1]-times[seg]);z=(1-f)*Z[seg]+f*Z[seg+1];rows.append(dict(id='entry_adaptive_'+str(j),display_time=t,contacts=[cfg['contacts'][0]],latent=z.tolist(),state=state(z).tolist()))
save('ENTRY_ADAPTIVE_REQUESTS.json',rows);print('ENTRY_ADAPTIVE_BRACKET',lo,hi,flush=True)
