import sys
sys.dont_write_bytecode=True
from reconcile import OUT,FRESH,read,dump,cc
from collections import defaultdict
V=read(FRESH/'R3_FRESH_REVIEW_VIEW_DATA_R1.json');adj=defaultdict(set);cut=set(V['fresh_boundary'])
for e,(a,b) in enumerate(V['edges']):
 if e not in cut:adj[a].add(b);adj[b].add(a)
parts=cc(range(len(V['vertices'])),adj)
dump('R3_FRESH_FULL_VERTEX_CUT_SCOPE_DIAGNOSTIC_R1.json',{'method':'FULL mesh vertex adjacency minus frozen fresh20 cut edges','component_count':len(parts),'component_sizes':[len(p) for p in parts],'INDEX_tip_component_ids':[k for k,p in enumerate(parts) if 233 in p],'THUMB_tip_component_ids':[k for k,p in enumerate(parts) if 284 in p],'applicable_to_partial_vertex_label_identity':False,'reason':'Unknown exterior vertices reconnect the full mesh. V1 must be induced on the exact solved field domain, not on unassigned outside vertices. No global body or physical split is claimed.','fresh_labels_changed':0})
assert len(parts)==1 and len(parts[0])==3416
# Execute synthetic graph construction, not just a counterexample assertion.
F=[[0,1,2,3],[3,2,4,5],[1,6,7,0]];L={0:'INDEX',1:'INDEX',2:'THUMB',3:'THUMB',4:'THUMB',5:'THUMB',6:'INDEX',7:'INDEX'}
ef=defaultdict(list);edges=set()
for f,vs in enumerate(F):
 for a,b in zip(vs,vs[1:]+vs[:1]):e=tuple(sorted((a,b)));edges.add(e);ef[e].append(f)
unlike={e for e in edges if L[e[0]]!=L[e[1]]};dual=defaultdict(set);primal=defaultdict(set)
for e in edges:
 if e not in unlike:
  a,b=e;primal[a].add(b);primal[b].add(a)
  for f in ef[e]:dual[f].update(g for g in ef[e] if g!=f)
vparts=cc(L,primal);fparts=cc(range(len(F)),dual)
assert len(vparts)==2 and len(fparts)==1
pure=[f for f,vs in enumerate(F) if len({L[v] for v in vs})==1];pureparts=cc(pure,dual);assert len(pureparts)==2
controls=read(OUT/'R3_SHEET_VALIDATOR_NEGATIVE_CONTROLS_R1.json');controls['mixed_quad_executed_result']={'vertex_components':vparts,'full_dual_components':fparts,'pure_face_components':pureparts,'actual_unlike_edges':[list(x) for x in sorted(unlike)],'assertions_pass':True};dump('R3_SHEET_VALIDATOR_NEGATIVE_CONTROLS_R1.json',controls)
print('Static full-vertex scope diagnostic and executed mixed-quad counterexample passed; no production solver invoked.')
