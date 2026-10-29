from pathlib import Path
O=Path(r'<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1')
s=(O/'extra_probe.py').read_text()
line="src=src.replace('vv,ww,ss=f(zz);wv=',\"kin_input=ca.SX.sym('kin_input',12);_,kin_w,kin_s=f(kin_input);kin_only=ca.Function('kin_only',[kin_input],[kin_w,kin_s]);ww,ss=kin_only(zz);wv=\")\n"
s=s.replace("sys.path.insert(0,str(P));ns=",line+"sys.path.insert(0,str(P));ns=")
s=s.replace("save('MULTINODE_PERFORMANCE.json'","save('MULTINODE_PRUNED_PERFORMANCE.json'").replace("save('NONSMOOTH_DIAGNOSIS.json'","save('NONSMOOTH_PRUNED_DIAGNOSIS.json'").replace("save('WORKLOAD_PROFILE.json'","save('WORKLOAD_PRUNED_PROFILE.json'").replace("save('EXTRA_BUDGET.json'","save('PRUNED_BUDGET.json'")
s=s.replace("jold,ot=timing(old,x);_,gt=timing(ns['gfun'],x)","jold,ot=timing(old,x);_,gt=timing(ns['gfun'],x);np.savez_compressed(O/'PRUNED_JACOBIAN.npz',jac=jold,x=x);ns['gfun'].save(str(O/'PRUNED_G.casadi'));old.save(str(O/'PRUNED_J.casadi'))")
(O/'pruned_probe.py').write_text(s)
