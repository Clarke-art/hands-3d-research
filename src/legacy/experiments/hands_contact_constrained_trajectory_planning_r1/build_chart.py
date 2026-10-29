import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from symbolic_skin import *
from scipy.optimize import linprog
from triangle_distance import distances
I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());B=json.loads((O/'TRAJECTORY_BENCHMARK_INPUT.json').read_text());z0=np.array(B['Start']['local']['latent']);V=skin(state(z0));data=np.load(O/'COLLOCATION_KEY_STATES.npz');J=I['junction_time'];aa=data['angles'][np.argmin(abs(data['times']-J))]
start=time.perf_counter();chart=[];lpcount=0
for midi,N,d,lo,hi in prepkey(aa,I['contacts'][0]['midi'],I['contacts'][0]['finger']):
 tris=V[TR];ids=np.flatnonzero(np.all(tris.max(1)>=lo-.002,1)&np.all(tris.min(1)<=hi+.002,1));k=c.KEYS[midi-21];ang=aa[midi-21];R=c.axisrot(-ang,[1,0,0]);pv=np.array(k['press_pivot']);NL=N@R.T;dl=d-N@pv+NL@pv
 for tid in ids:
  T=tris[tid];slack=d[:,None]-N@T.T;ix=np.argmin(slack.max(1));lam=np.eye(len(N))[ix]
  if slack[ix].max()>0.00015:
   # Exact LP dual: min_lambda max_vertex weighted key-plane slack.
   A=np.c_[slack.T,-np.ones(3)];fit=linprog(np.r_[np.zeros(len(N)),1.],A_ub=A,b_ub=np.zeros(3),A_eq=[np.r_[np.ones(len(N)),0.]],b_eq=[1.],bounds=[(0,None)]*len(N)+[(None,None)],method='highs');assert fit.success;lam=fit.x[:-1];lpcount+=1
  if float((lam@slack).max()) < -.001:continue
  chart.append(dict(midi=int(midi),triangle=int(tid),vertices=TR[tid].tolist(),normal_key_local=(lam@NL).tolist(),offset_key_local=float(lam@dl),reference_dual_depth_mm=float((lam@slack).max()*1000)))
pairs=[]
for j in range(5):
 for k in range(j+1,5):
  ia=np.flatnonzero(LABEL==j);ib=np.flatnonzero(LABEL==k);A=V[TR[ia]];BB=V[TR[ib]];bl=BB.min(1);bh=BB.max(1)
  for ai,ta in enumerate(ia):
   delta=np.maximum(np.maximum(bl-A[ai].max(0),A[ai].min(0)-bh),0)
   for bi in np.flatnonzero(np.sum(delta**2,1)<=.004**2):
    tb=int(ib[bi])
    if tb not in META['topological_vertex_neighbors'][int(ta)] and not set(TR[ta])&set(TR[tb]):pairs.append((int(ta),tb))
pairs=np.array(pairs,int).reshape(-1,2);dd,wa,wb=distances(V[TR[pairs[:,0]]],V[TR[pairs[:,1]]]) if len(pairs) else ([],[],[]);out=dict(key_chart=chart,self_chart=[dict(a=int(a),b=int(b),axis=((wa[n]-wb[n])/dd[n]).tolist()) for n,(a,b) in enumerate(pairs)],setup_numerical_seconds=time.perf_counter()-start,dual_LP_count=lpcount,scope='Fixed local certificate planes with candidate filtering; all triangle vertices constrained against a convex-combination key plane; exact whole-mesh validation independent');(O/'ACTIVE_GEOMETRY_CHART.json').write_text(json.dumps(out,indent=2));print('chart',len(chart),'self',len(pairs),'LP',lpcount,'seconds',out['setup_numerical_seconds'])
