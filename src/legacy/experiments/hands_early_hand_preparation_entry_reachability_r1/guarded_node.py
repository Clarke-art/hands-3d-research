from coupled_model import *
class GuardedNode(DynamicNode):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.guard_calls=[]
 def checked_jac(self,z):
  z=np.asarray(z).ravel();base=self.value(z);baseline=self.last_signature;history=[];switches=[]
  def sample(h):
   cols=[];changes=[]
   for i in range(12):
    step=h*(.1 if i>=10 else 1);dd=np.eye(12)[i]*step
    plus=self.value(z+dd);sp=self.last_signature;minus=self.value(z-dd);sm=self.last_signature
    cols.append((plus-minus)/(2*step))
    changes.append([i,[j for j in range(3) if sp[j]!=baseline[j] or sm[j]!=baseline[j]]])
   self.stats['jacobians']+=1
   return np.array(cols).T,[r for r in changes if r[1]]
  tick=time.monotonic();previous,ch=sample(1e-4);switches.append(dict(h=1e-4,changed_columns=ch))
  try:
   for h in [1e-5,1e-6]:
    current,ch=sample(h);switches.append(dict(h=h,changed_columns=ch));error=float(np.max(abs(current-previous)));history.append(dict(h=h,max_abs_difference=error))
    if error<1e-3:
     rec=dict(status='VERIFIED_LOCAL_STRICT_FD',steps=history,branch_checks=switches,in_solver=True,recomputed_features=True,universal_smoothness=False,seconds=time.monotonic()-tick);self.guard_calls.append(rec);return current
    previous=current
   rec=dict(status='FAIL_CLOSED_NONSMOOTH_OR_UNVERIFIED',steps=history,branch_checks=switches,in_solver=True,seconds=time.monotonic()-tick);self.guard_calls.append(rec)
   raise ValueError('Guard rejects unverified local derivative; no frozen-branch substitution')
  finally:self.stats['jac_seconds']+=time.monotonic()-tick
