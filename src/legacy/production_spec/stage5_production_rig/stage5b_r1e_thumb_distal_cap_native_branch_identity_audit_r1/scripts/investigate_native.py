import sys
sys.dont_write_bytecode=True
import json, heapq
from pathlib import Path
import numpy as np
out=Path(__file__).resolve().parents[1];root=out.parents[2]
d=json.loads((out/'_tmp/static_mesh_states.json').read_text());v=np.array(d['NATIVE']['vertices_world_m']);faces=d['NATIVE']['faces'];edges=d['NATIVE']['edges']
adj=[[] for _ in v]
for a,b in edges:
    length=float(np.linalg.norm(v[a]-v[b]));adj[a].append((b,length));adj[b].append((a,length))
def dij(seeds):
    dist=np.full(len(v),np.inf);pred={};q=[]
    for s in seeds:dist[s]=0.;heapq.heappush(q,(0.,s))
    while q:
        cost,a=heapq.heappop(q)
        if cost>dist[a]+1e-15:continue
        for b,l in adj[a]:
            nc=cost+l
            if nc<dist[b]-1e-15:dist[b]=nc;pred[b]=a;heapq.heappush(q,(nc,b))
    return dist,pred
loc=np.array(d['NATIVE']['matrix_world'])[:3,3];norm=np.diag([1,-1,-1])
canon=lambda p:<REDACTED_EMAIL>(p)+loc-norm@loc
nearest=lambda p:int(np.argmin(np.linalg.norm(v-p,axis=1)))
seeds={'little':[1.3515,.0319,.1879],'ring':[1.3933,.0320,.1599],'middle':[1.4231,.0251,.1490],'index':[1.4586,.0239,.1643],'thumb':[1.4977,.0358,.2421],'wrist':[1.4048,.0113,.3430]}
tip={n:nearest(canon(p)) for n,p in seeds.items()};names=list(tip);ds={n:dij([a])[0] for n,a in tip.items()};lab=np.argmin(np.array([ds[n] for n in names]),axis=0);labels=[names[i] for i in lab]
fore=v[nearest(canon([1.4048,.0113,.4316]))];distal=(v[tip['middle']]-fore);distal/=np.linalg.norm(distal)
notch={}
for a,b in [('index','middle'),('middle','ring'),('ring','little'),('index','thumb')]:
    candidates=[i for i in range(len(v)) if labels[i] in [a,b] and any(labels[j] in [a,b] and labels[j]!=labels[i] for j,l in adj[i])]
    notch[a+'-'+b]=max(candidates,key=lambda i:float((v[i]-fore)@distal))
rootthumb=nearest(canon([1.4489,.0115,.3134]));length=ds['thumb'][rootthumb]
region=[i for i in range(len(v)) if labels[i]=='thumb' and .25*length<=ds['thumb'][i]<=.55*length]
c=v[region].mean(0);axis=v[tip['thumb']]-c;axis/=np.linalg.norm(axis);anchor=v[tip['thumb']]+axis*((v[rootthumb]-v[tip['thumb']])@axis);L=(v[tip['thumb']]-anchor)@axis
joints={}
for name,frac in [('MCP',.44),('IP',.75)]:
    sel=[i for i in range(len(v)) if labels[i]=='thumb' and abs((v[i]-anchor)@axis-L*frac)<=.003]
    joints[name]=v[sel].mean(0).tolist()
print('tip seeds',tip);print('notch',notch,{k:v[i].tolist() for k,i in notch.items()});print('thumb native joints',joints,'axis',axis.tolist())
cap=[151,158,1061,1074,1076,2189,2192,2569,2577]
for i in cap:
    two={j for a,l in adj[i] for j,lj in adj[a]}
    print(i,labels[i],{n:round(ds[n][i]*1000,2) for n in ['thumb','index']},'2ring',sorted({labels[j] for j in two}))
(out/'_tmp/native_independent_partition.json').write_text(json.dumps({'tip_seeds':tip,'transformed_seed_world_m':{n:canon(p).tolist() for n,p in seeds.items()},'labels':labels,'notches':notch,'thumb_native_joints':joints,'thumb_axis':axis.tolist(),'thumb_root_vertex':rootthumb,'thumb_axis_anchor':anchor.tolist(),'thumb_length_m':float(L)}),encoding='utf8')
