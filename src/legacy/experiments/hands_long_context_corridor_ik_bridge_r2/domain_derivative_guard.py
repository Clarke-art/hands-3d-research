from bridge_model import *
def domain_checked_jac(self,z):
 z=np.asarray(z).ravel();self.value(z);base_sig=self.last_signature;steps=[];branches=[];previous=None;beg=time.monotonic();outside=bool(np.any(z<LOW-1e-12) or np.any(z>HIGH+1e-12))
 for h in [1e-4,1e-5,1e-6]:
  cols=[];mode=[];changes=[]
  for i in range(12):
   hh=h*(.1 if i>=10 else 1);dd=np.eye(12)[i]*hh
   if not outside and z[i]-2*hh<LOW[i] and z[i]+2*hh<=HIGH[i]:
    v0=self.value(z);a=self.value(z+dd);sa=self.last_signature;b=self.value(z+2*dd);sb=self.last_signature;col=(-3*v0+4*a-b)/(2*hh);kind='VERIFIED_FORWARD_SECOND_ORDER'
   elif not outside and z[i]+2*hh>HIGH[i] and z[i]-2*hh>=LOW[i]:
    v0=self.value(z);a=self.value(z-dd);sa=self.last_signature;b=self.value(z-2*dd);sb=self.last_signature;col=(3*v0-4*a+b)/(2*hh);kind='VERIFIED_BACKWARD_SECOND_ORDER'
   else:
    a=self.value(z+dd);sa=self.last_signature;b=self.value(z-dd);sb=self.last_signature;col=(a-b)/(2*hh);kind='CENTRAL_NUMERICAL_EXTENSION_ONLY' if outside else 'CENTRAL_INSIDE_DOMAIN'
   cols.append(col);mode.append(kind);changed=[j for j in range(len(base_sig)) if sa[j]!=base_sig[j] or sb[j]!=base_sig[j]]
   if changed:changes.append([i,changed])
  current=np.array(cols).T;self.stats['jacobians']+=1;branches.append(dict(h=h,column_modes=mode,changed_columns=changes))
  if previous is not None:
   err=float(np.max(abs(current-previous)));steps.append(dict(h=h,max_abs_difference=err))
   if err<1e-3:
    self.guard_calls.append(dict(status='DOMAIN_AWARE_LOCAL_DIFFERENCE_VERIFIED',steps=steps,branch_checks=branches,center=z.tolist(),center_outside_domain=outside,physical_domain_gate_not_relaxed=True,in_solver=True,seconds=time.monotonic()-beg));return current
  previous=current
 self.guard_calls.append(dict(status='FAIL_CLOSED_DOMAIN_AWARE_DIFFERENCE_UNVERIFIED',steps=steps,branch_checks=branches,center=z.tolist(),center_outside_domain=outside,physical_domain_gate_not_relaxed=True,in_solver=True,seconds=time.monotonic()-beg))
 raise ValueError('DOMAIN_AWARE_STRICT_DERIVATIVE_REJECTION')
if __name__=='__main__':
 d=json.loads((O/'R2_DERIVATIVE_SHARED_BLOCKER.json').read_text(encoding='utf8'))['diagnostics'][0];p=json.loads((O/'candidate_right_PLAN_COMPILED.json').read_text(encoding='utf8'));n=CorridorNode(d['initial_node_before_IPOPT_push'],[p['held_contact']],keyangles(d['time']),d['time'],p)
 try:
  jac=domain_checked_jac(n,d['tested_trial']);status='DOMAIN_AWARE_SCOPED_DERIVATIVE_VERIFIED'
 except Exception as e:status='REJECTED';jac=None
 save('R2_DOMAIN_DERIVATIVE_CHECK.json',dict(status=status,raw_shared_failure=d,guard_records=n.guard_calls,jacobian_shape=list(jac.shape) if jac is not None else None,method='Same multi-scale1e-3 consistency gate; only legitimate one-sided stencils close to authorized boundaries; no collision/contact/rate limits changed',meaning='A local derivative repair, not a path feasibility or global derivative PASS'))
 print('DOMAIN_DERIVATIVE_CHECK',status,n.guard_calls,flush=True)
