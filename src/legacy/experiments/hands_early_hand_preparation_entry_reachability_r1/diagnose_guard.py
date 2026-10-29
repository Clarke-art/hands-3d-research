from guarded_node import *
cfg=json.loads((O/'EXPERIMENT_CONFIG.json').read_text(encoding='utf8'));rows=json.loads((O/'HOLD_PROBE_REQUESTS.json').read_text(encoding='utf8'));aa=np.load(O/'PREPARATION_KEY_STATES.npz')['angles'][0];report=[]
for r in rows[:2]:
 node=DynamicNode(r['latent'],r['contacts'],aa,r['display_time'],(LOW,HIGH));z=np.array(r['latent']);mats=[];details=[]
 for h in [1e-4,1e-5,1e-6]:
  M=node.jac(z,h);mats.append(M)
  if len(mats)>1:
   delta=abs(mats[-1]-mats[-2]);ri,ci=np.unravel_index(delta.argmax(),delta.shape);detail=dict(h=h,row=int(ri),column=int(ci),max_difference=float(delta[ri,ci]),classification='contact_equality' if ri==0 else ('contact_inequality_'+str(ri) if ri<=10 else 'key_or_self_geometry'))
   step=h*(.1 if ci>=10 else 1);dd=np.eye(12)[ci]*step;v0=node.value(z);sig0=node.last_signature;vp=node.value(z+dd);sigp=node.last_signature;vm=node.value(z-dd);sigm=node.last_signature;detail.update(base=float(v0[ri]),plus=float(vp[ri]),minus=float(vm[ri]),base_contact_branch=sig0[0],plus_contact_branch=sigp[0],minus_contact_branch=sigm[0]);details.append(detail)
 report.append(dict(id=r['id'],details=details))
save('DERIVATIVE_DISCONTINUITY_DIAGNOSIS.json',report);print(report,flush=True)
