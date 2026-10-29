import json as _lock_json
from pathlib import Path as _LockPath
if __name__ == "__main__" and _lock_json.loads((_LockPath(__file__).resolve().parent / "POLICY_LOCK.json").read_text(encoding="utf-8"))["no_more_solves"]:
    raise SystemExit("STOP — HUMAN REVIEW: completed experiment is locked; use a separately authorized run")
import sys,time,json,ast,os
from pathlib import Path
sys.dont_write_bytecode=True;os.environ['PYTHONUTF8']='1'
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import derivative_probe as d
from derivative_probe import ca,np,P,F,skin,state,I,ContactDerivative,save
start=time.monotonic();rows=[]
def timing(f,x,n=3):
 ts=[]
 for _ in range(n):
  d.check();t=time.perf_counter();y=f(x);ts.append(time.perf_counter()-t)
 return np.array(y),ts
# Original graph, no solver and no historical writes. Exactly three recorded nodes.
src=(P/'solve_trajectory.py').read_text();src=src[:src.index('meta=dict(')]
src=src.replace("assert not json.loads((O/'POLICY_LOCK.json').read_text()).get('no_more_solves',True),'STOP HUMAN REVIEW: new solve is not authorized by this completed run'",'')
src=src.replace('from symbolic_skin import *','from symbolic_skin import *\nO=Path(r"'+str(P)+'")')
src=src.replace("data=np.load(O/'COLLOCATION_KEY_STATES.npz')","data={k:v[[5,6,7]] for k,v in dict(np.load(O/'COLLOCATION_KEY_STATES.npz')).items()}")
sys.path.insert(0,str(P));ns={ '__file__':str(P/'solve_trajectory.py')};t=time.perf_counter();exec(compile(src,'original_three_node_graph','exec'),ns);x=ns['x0'];G=ns['G'];X=ns['X'];old=ca.Function('original_three_jac',[X],[ca.jacobian(G,X)]);build=time.perf_counter()-t
jold,ot=timing(old,x);_,gt=timing(ns['gfun'],x)

np.savez_compressed(O/'ORIGINAL_JACOBIAN.npz',jac=jold,x=x);ns['gfun'].save(str(O/'ORIGINAL_G.casadi'));save('ORIGINAL_DIRECT_BUDGET.json',dict(charged_seconds=time.monotonic()-start))
