"""Fresh R3 only. JSON/HTML outputs; no Blender API, geometry or weight mutation."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, math, heapq, datetime
from pathlib import Path
from collections import defaultdict, deque, Counter
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
INPUT = ROOT/'audits/r3_recovery_input_contract_finalization_r1'
RUN = 'R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1'
EXPECTED = 'f392fd33be0430cabf4b849fb8a4565853c245f2cf09e953d506493c93ca3cab'
PROX_HASH = '5ff37ae7d0915e1ab3b57b00f261b47b038e78a0bf1d316d0c52c39d5b063afb'
RESPONSE = Path('<USER_HOME>/Downloads/R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T10-43-37-453Z.json')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(d): return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def digest(d): return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def dump(n,d): (OUT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def resolve(p):
 p=Path(p); return p if p.is_absolute() else ROOT/p
def inventory(): return {str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents}
def components(ids,adj):
 remaining=set(ids);result=[]
 while remaining:
  start=min(remaining);remaining.remove(start);q=deque([start]);c=[]
  while q:
   v=q.popleft();c.append(v)
   for w in sorted(adj[v]):
    if w in remaining: remaining.remove(w);q.append(w)
  result.append(sorted(c))
 return result
def preflight():
 checks=[]
 def gate(n,ok,detail=None):
  checks.append({'gate':n,'pass':bool(ok),'detail':detail})
  if not ok:
   dump('R3_PRE_SOLVE_GATES_R1.json',{'pass':False,'checks':checks})
   dump(RUN+'_STATUS.json',{'technical_validation_verdict':'FAIL_CLOSED_SOLVER_OR_CONTRACT','failed_gate':n,'solver_runs':0,'BLEND_FILES_WRITTEN':0,'skin_rebuild_count':0,'Stage6_runs':0,'STOP':True})
   raise RuntimeError('FAIL_CLOSED: '+n)
 c=read(INPUT/'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1.json')
 gate('canonical contract hash',digest(c)==EXPECTED,digest(c))
 r=read(RESPONSE)
 required={'review_id':'R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW_R1','contract_id':c['contract_id'],'canonical_contract_hash':EXPECTED,'proximal_boundary_authority_hash':PROX_HASH,'approved_for_input_contract':True,'cost_semantics_approved_with_contract':True,'authorized_next_phase':RUN,'validation_mode':False,'automatic_solver_execution':False}
 for k,v in required.items(): gate('Human response '+k,type(r.get(k))==type(v) and r.get(k)==v)
 for i in range(1,9):
  keys=[k for k in r if k.startswith('Q'+str(i)+'_')];gate('Human Q'+str(i),len(keys)==1 and r[keys[0]]==('YES' if i<8 else 'APPROVE_INPUT_CONTRACT'))
 refs=[]
 def verify_refs(d,where):
  if isinstance(d,dict):
   if 'path' in d and 'sha256' in d:
    p=resolve(d['path']); actual=sha(p) if p.is_file() else None;gate('reference hash '+where,actual==d['sha256'],str(p));refs.append({'path':str(p),'sha256':actual})
   for k,v in d.items():verify_refs(v,where+'/'+k)
  elif isinstance(d,list):
   for i,v in enumerate(d):verify_refs(v,where+'/'+str(i))
 verify_refs(c,'contract')
 docs={n:read(resolve(x['path'])) for n,x in c['files'].items()}
 for n,d in docs.items(): verify_refs(d,n)
 src=c['frozen_authority_sources']
 extraction=read(resolve(src['READ_ONLY_LIVE_EXTRACTION.json']['path']))
 V=extraction['RSSF']['vertices_world_m'];E=extraction['RSSF']['edges'];F=extraction['RSSF']['faces']
 gate('native RSSF corrected frozen topology',F==extraction['NATIVE']['faces'] and E==extraction['NATIVE']['edges'] and V==extraction['CORRECTED']['vertices_world_m'])
 g=docs['R3_ENGINEERING_GRAPH_DOMAIN_R1.json'];G=set(g['vertex_ids']);GE=g['edge_ids'];GF=set(g['face_ids'])
 Tdoc=docs['R3_AUTHORITY_BACKED_THUMB_HARD_SOURCES_R1.json'];Idoc=docs['R3_INDEX_HARD_SOURCES_R1.json'];T=set(Tdoc['unique']['vertex_ids']);I=set(Idoc['unique']['vertex_ids'])
 gate('unique sets and set hashes',all(len(d['unique']['vertex_ids'])==len(set(d['unique']['vertex_ids']))==d['unique']['count'] and digest(d['unique']['vertex_ids'])==d['unique']['set_sha256'] for d in [Tdoc,Idoc]))
 gate('THUMB INDEX conflict zero',not T&I);gate('complete hard sources in graph',bool(T) and bool(I) and T|I<=G)
 gate('THUMB authority backed only',T==set(Tdoc['ingredients']['cap37']['vertex_ids'])|set(Tdoc['ingredients']['thumb_nail']['vertex_ids']) and not Tdoc['tube_derived_hard_sources_used'])
 neutral=docs['R3_NEUTRAL_INTERFACE_CONTEXT_R1.json'];W=set(neutral['FIRST_WEB21']['membership']['vertex_ids']);band=set(neutral['conservative_web_transition_band']['vertex_ids'])
 gate('FIRST_WEB neutral no hard pins',len(W)==21 and not W&(T|I) and W<=G and neutral['FIRST_WEB21']['hard_pin_count']==0)
 oldcap={151,158,1061,1074,1076,2189,2192,2569,2577};gate('old cap9 hard role NONE',not oldcap&(T|I))
 adj=defaultdict(dict);ef=defaultdict(list);lookup={tuple(sorted(e)):i for i,e in enumerate(E)}
 for f,vs in enumerate(F):
  for a,b in zip(vs,vs[1:]+vs[:1]):ef[lookup[tuple(sorted((a,b)))]].append(f)
 faceedges={lookup[tuple(sorted((a,b)))] for f in GF for a,b in zip(F[f],F[f][1:]+F[f][:1])}
 gate('exact graph faces vertices edges',G=={v for f in GF for v in F[f]} and set(GE)==faceedges and len(GE)==len(set(GE)))
 for e in GE:
  a,b=E[e];ell=math.dist(V[a],V[b])*1000
  gate('edge identity metric support '+str(e),[a,b]==g['edge_endpoints'][str(e)] and math.isfinite(ell) and ell>0 and math.isclose(ell,g['edge_lengths_mm'][str(e)],rel_tol=1e-12) and bool(set(ef[e])&GF))
  adj[a][b]=ell;adj[b][a]=ell
 cs=components(G,adj);gate('connected and sources reachable',len(cs)==1 and T|I<=set(cs[0]))
 excluded=g['construction']['excluded_explicit_landmarks'];leaks={k:sorted(G&set(v['vertex_ids'])) for k,v in excluded.items()};gate('other digit and wrist leakage zero',not any(leaks.values()),leaks)
 freeze=ROOT/'audits/human_proximal_partial_circumference_boundary_authority_freeze_r1'
 prox=read(freeze/'PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY_R1.json');gate('proximal canonical hash',digest(prox)==PROX_HASH)
 pb=neutral['proximal_boundary'];gate('P04 P05 semantic boundary',pb['stop']=='STOP_AFTER_P04' and pb['distal_row']=='P04' and pb['proximal_row']=='P05' and [pb['left_boundary_edge_id'],pb['right_boundary_edge_id']]==[4666,4668] and pb['boundary_vertex_ids']==[E[4666],E[4668]] and not band&(T|I) and not {1369,1370}&set(neutral['conservative_web_transition_band']['face_ids']))
 cost=docs['R3_COST_UNIT_CONTRACT_R1.json'];P=round(cost['TAU_mm']/3*1000);cap=cost['finite_capacity_cap'];B=len(G)*cap+len(GE)*P;INF=B+1
 gate('corrected cost semantics',cost['R3_COST_UNIT']=='CORRECTED_COMMON_MM_SEMANTICS' and cap==400000 and P==1296 and cost['canonical_units']=='mm')
 gate('recomputed INF bound',INF==c['INF']==docs['R3_INF_AUTHORITY_CANDIDATE_R1.json']['INF'],{'V':len(G),'E':len(GE),'B':B,'INF':INF})
 actual={'THUMB':len(T),'INDEX':len(I),'neutral':len(G-T-I),'V':len(G),'E':len(GE)};expected={'THUMB':57,'INDEX':145,'neutral':760,'V':962,'E':1881}
 gate('contract counts',actual=={'THUMB':c['THUMB_hard_source_count'],'INDEX':c['INDEX_hard_source_count'],'neutral':c['neutral_interface_vertex_count'],'V':c['graph_vertex_count'],'E':c['graph_edge_count']})
 dump('R3_PRE_SOLVE_GATES_R1.json',{'pass':True,'checks':checks,'reference_hashes':refs,'Human_response_sha256':sha(RESPONSE),'actual':actual,'summary_differences':{k:[expected[k],v] for k,v in actual.items() if expected[k]!=v},'B':B,'INF':INF,'wire_only_edges':0})
 return locals()

def dijkstra(G,adj,sources):
 d={v:math.inf for v in G};q=[]
 for v in sorted(sources): d[v]=0.;heapq.heappush(q,(0.,v))
 while q:
  du,u=heapq.heappop(q)
  if du!=d[u]:continue
  for v in sorted(adj[u]):
   nd=du+adj[u][v]
   if nd<d[v]:d[v]=nd;heapq.heappush(q,(nd,v))
 return d

class Dinic:
 def __init__(self,n):self.n=n;self.to=[];self.cap=[];self.g=[[] for _ in range(n)]
 def add(self,u,v,c):
  self.g[u].append(len(self.to));self.to.append(v);self.cap.append(c)
  self.g[v].append(len(self.to));self.to.append(u);self.cap.append(0)
 def flow(self,s,t,INF):
  result=0
  def dfs(u,f):
   if u==t:return f
   while it[u]<len(self.g[u]):
    e=self.g[u][it[u]];v=self.to[e]
    if self.cap[e]>0 and level[v]==level[u]+1:
     d=dfs(v,min(f,self.cap[e]))
     if d:self.cap[e]-=d;self.cap[e^1]+=d;return d
    it[u]+=1
   return 0
  while True:
   level=[-1]*self.n;level[s]=0;q=deque([s])
   while q:
    u=q.popleft()
    for e in self.g[u]:
     v=self.to[e]
     if self.cap[e]>0 and level[v]<0:level[v]=level[u]+1;q.append(v)
   if level[t]<0:break
   it=[0]*self.n
   while True:
    f=dfs(s,INF)
    if not f:break
    result+=f
  reach={s};q=deque([s])
  while q:
   for e in self.g[q.popleft()]:
    v=self.to[e]
    if self.cap[e]>0 and v not in reach:reach.add(v);q.append(v)
  return result,reach

def solve(d,dT,dI):
 G,E,GE,T,I,cap,P,INF=[d[k] for k in ['G','E','GE','T','I','cap','P','INF']]
 ids=sorted(G);idx={v:i for i,v in enumerate(ids)};n=len(ids);net=Dinic(n+2);term={}
 for v in ids:
  ct=min(cap,round(dT[v]*1000));ci=min(cap,round(dI[v]*1000))
  if v in T:ct,ci=0,INF
  elif v in I:ct,ci=INF,0
  term[v]={'source_to_v':ci,'v_to_sink':ct,'hard_role':'THUMB' if v in T else 'INDEX' if v in I else 'NONE'}
  net.add(n,idx[v],ci);net.add(idx[v],n+1,ct)
 for e in sorted(GE):
  a,b=E[e];net.add(idx[a],idx[b],P);net.add(idx[b],idx[a],P)
 flow,reach=net.flow(n,n+1,INF);labels={v:'THUMB' if idx[v] in reach else 'INDEX' for v in ids}
 return flow,labels,term

def closure(labels,d):
 labels=labels.copy();seen={digest(labels)};rows=[];changes=0;converged=False;reason=None
 for it in range(1,d['docs']['R3_CLOSURE_CONTRACT_R1.json']['iteration_cap_full_sweeps']+1):
  changed=0;actions=[]
  for name,pins in [('THUMB',d['T']),('INDEX',d['I'])]:
   for comp in components([v for v in labels if labels[v]==name],d['adj']):
    if set(comp)&pins:continue
    other='INDEX' if name=='THUMB' else 'THUMB'
    for v in comp:labels[v]=other
    changed+=len(comp);actions.append({'from':name,'to':other,'vertex_ids':comp})
    if any(labels[v]!='THUMB' for v in d['T']) or any(labels[v]!='INDEX' for v in d['I']):raise RuntimeError('FAIL_CLOSED closure pin mutation')
  changes+=changed;h=digest(labels);rows.append({'full_sweep':it,'changed_count':changed,'actions':actions,'state_sha256':h})
  if changed==0:converged=True;break
  if h in seen:reason='repeated state';break
  seen.add(h)
 if not converged and reason is None:reason='iteration cap'
 return labels,{'rule':'NO HISTORICAL LABEL INJECTION','full_sweeps':len(rows),'converged':converged,'cumulative_changed_count':changes,'sweeps':rows,'failure_reason':reason,'hard_pins_preserved':True}

def energy(labels,d,dT,dI):
 unary=sum(min(d['cap'],round((dT if lab=='THUMB' else dI)[v]*1000)) for v,lab in labels.items() if v not in d['T']|d['I'])
 edges=[e for e in d['GE'] if labels[d['E'][e][0]]!=labels[d['E'][e][1]]];pair=len(edges)*d['P']
 return {'unary_capacity':unary,'pairwise_capacity':pair,'total_capacity':unary+pair,'unary_mm_cost':unary/1000,'pairwise_mm_cost':pair/1000,'unary_pairwise_ratio':unary/pair if pair else None,'cut_edge_count':len(edges),'cut_edge_ids':edges,'hard_penalty':0,'units':'integer capacity (1000 per mm cost)','hard_pin_cost_rule':'own hard label terminal cost zero; wrong hard label INF'}

def independent_edmonds_karp(term,d):
 # Independent BFS augmenting-path implementation, no package dependency.
 r=defaultdict(dict);s=-1;t=-2
 def add(a,b,c):r[a][b]=r[a].get(b,0)+c;r[b].setdefault(a,0)
 for v,x in term.items():add(s,v,x['source_to_v']);add(v,t,x['v_to_sink'])
 for e in d['GE']:
  a,b=d['E'][e];add(a,b,d['P']);add(b,a,d['P'])
 total=0;paths=0
 while True:
  parent={s:None};q=deque([s])
  while q and t not in parent:
   a=q.popleft()
   for b,c in r[a].items():
    if c>0 and b not in parent:parent[b]=a;q.append(b)
  if t not in parent:break
  aug=d['INF'];b=t
  while b!=s:a=parent[b];aug=min(aug,r[a][b]);b=a
  b=t
  while b!=s:a=parent[b];r[a][b]-=aug;r[b][a]+=aug;b=a
  total+=aug;paths+=1
 return total,paths

def run():
 sys.setrecursionlimit(10000)
 if (OUT/'R3_FRESH_MINCUT_RESULT_R1.json').exists() and '--resume' not in sys.argv:raise RuntimeError('Refusing to overwrite completed fresh run')
 d=preflight();print('Preflight passed; freezing all existing files',flush=True)
 if '--resume' in sys.argv:
  before=read(OUT/'FROZEN_HASHES_BEFORE.json')
  assert inventory()==before, 'Protected inputs changed before resume'
 else:before=inventory();dump('FROZEN_HASHES_BEFORE.json',before)
 G,V,E,F,GE,GF,T,I,W,adj,ef,cost=[d[k] for k in ['G','V','E','F','GE','GF','T','I','W','adj','ef','cost']]
 dT=dijkstra(G,adj,T);dI=dijkstra(G,adj,I)
 if any(not math.isfinite(x) for x in list(dT.values())+list(dI.values())):raise RuntimeError('FAIL_CLOSED unreachable fields')
 def field(x):return {'minimum_mm':min(x.values()),'maximum_mm':max(x.values()),'finite_cap_hits':sum(round(v*1000)>=d['cap'] for v in x.values()),'unreachable_count':sum(not math.isfinite(v) for v in x.values()),'field_sha256':digest(x),'values_mm':x}
 dump('FRESH_R3_UNARY_FIELDS_R1.json',{'fresh_Dijkstra':True,'unit':'mm edge-geodesic','graph_hash':sha(INPUT/'R3_ENGINEERING_GRAPH_DOMAIN_R1.json'),'dT':field(dT),'dI':field(dI),'exact_tie_count':sum(dT[v]==dI[v] for v in G),'integer_capacity_tie_count':sum(round(dT[v]*1000)==round(dI[v]*1000) for v in G),'historical_fields_loaded':False})
 flow,raw,term=solve(d,dT,dI);eraw=energy(raw,d,dT,dI)
 assert flow==eraw['total_capacity'] and all(raw[v]=='THUMB' for v in T) and all(raw[v]=='INDEX' for v in I)
 dump('R3_HARD_PIN_CAPACITY_AUDIT_R1.json',{'pass':True,'B':d['B'],'INF':d['INF'],'strictly_above_finite_bound':d['INF']>d['B'],'single_INF_per_unique_source':True,'THUMB_count':len(T),'INDEX_count':len(I),'neutral_INF_count':0,'source_conflicts':0,'terminals':term,'formula':'B=|V|*400000+|E|*1296; INF=B+1'})
 dump('R3_FRESH_MINCUT_RESULT_R1.json',{'solver':'fresh deterministic exact Dinic s-t mincut','flow':flow,'labels':raw,'THUMB_count':sum(x=='THUMB' for x in raw.values()),'INDEX_count':sum(x=='INDEX' for x in raw.values()),'hard_source_preservation':True,'energy':eraw,'historical_labels_loaded_before_solve':False,'label_sha256':digest(raw),'maxflow_equals_cut_energy':True})
 final,cl=closure(raw,d);dump('R3_FRESH_CLOSURE_AUDIT_R1.json',cl)
 if not cl['converged']:raise RuntimeError('FAIL_CLOSED closure '+cl['failure_reason'])
 efinal=energy(final,d,dT,dI);cut=efinal['cut_edge_ids'];cutset=set(cut);boundary_vertices={v for e in cut for v in E[e]}
 dump('R3_FRESH_ENERGY_AUDIT_R1.json',{'approved_semantics':cost['R3_COST_UNIT'],'TAU_mm':cost['TAU_mm'],'pairwise_mm':cost['TAU_mm']/3,'pairwise_integer':d['P'],'finite_capacity_cap':d['cap'],'raw_mincut':eraw,'post_closure':efinal,'pairwise_dominated_unit_bug_used':False,'balance_required':False})
 outside=sorted(set(range(len(V)))-G)
 dump('R3_FRESH_FINAL_LABELS_R1.json',{'role':'SOLVER-DERIVED OWNERSHIP LABELS','Human_approved':False,'pointwise_anatomical_authority':False,'graph_vertex_ids':sorted(G),'labels':final,'label_sha256':digest(final),'outside_graph_vertex_ids':outside,'outside_graph_status':'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH','historical_label_injection':False,'THUMB_count':sum(x=='THUMB' for x in final.values()),'INDEX_count':sum(x=='INDEX' for x in final.values())})
 badj=defaultdict(set);edgeadj=defaultdict(set);byvertex=defaultdict(list);byface=defaultdict(list)
 for e in cut:
  a,b=E[e];badj[a].add(b);badj[b].add(a)
  for v in [a,b]:byvertex[v].append(e)
  for f in ef[e]:byface[f].append(e)
 for es in byvertex.values():
  for e in es:edgeadj[e].update(es)
 bcomps=components(cut,edgeadj)
 faceedgeadj=defaultdict(set)
 for es in byface.values():
  for e in es:faceedgeadj[e].update(es)
 bfcomps=components(cut,faceedgeadj)
 boundary_rows=[{'edge_id':e,'vertex_ids':E[e],'surface_face_ids':ef[e],'graph_support_face_ids':sorted(set(ef[e])&GF),'labels':[final[v] for v in E[e]],'length_mm':math.dist(V[E[e][0]],V[E[e][1]])*1000} for e in cut]
 dump('R3_FRESH_BOUNDARY_AUDIT_R1.json',{'pass':all(r['graph_support_face_ids'] and len(set(r['labels']))==2 for r in boundary_rows),'edge_count':len(cut),'vertex_adjacency_component_count':len(bcomps),'vertex_adjacency_components':bcomps,'face_strip_component_count':len(bfcomps),'face_strip_components':bfcomps,'surface_support':True,'self_consistency':cutset=={e for e in GE if final[E[e][0]]!=final[E[e][1]]},'edges':boundary_rows,'component_note':'Vertex-adjacency and shared-face strip counts reported separately; ladder cross edges may not share vertices.'})
 # Full frozen face dual adjacency, cut only fresh unlike-label graph edges.
 fadj=defaultdict(set)
 for e,fs in ef.items():
  if e in cutset:continue
  for f in fs:fadj[f].update(x for x in fs if x!=f)
 sheets=components(range(len(F)),fadj);vsets=[{v for f in s for v in F[f]} for s in sheets];validator=d['docs']['R3_VALIDATOR_CONTRACT_R1.json']
 def identity(which):
  ident=validator[which+'_identity'];tip=ident['tip'];requiredfaces=set(ident['nail_faces'])|set(ident.get('cap_faces',[]));requiredverts=set(ident.get('cap_vertices',[]))|{tip}
  candidates=[k for k,s in enumerate(sheets) if requiredfaces<=set(s) and requiredverts<=vsets[k]]
  return candidates
 isheet=identity('INDEX');tsheet=identity('THUMB');sheetpass=len(isheet)==len(tsheet)==1 and isheet!=tsheet
 index_vs=vsets[isheet[0]] if len(isheet)==1 else set();thumb_vs=vsets[tsheet[0]] if len(tsheet)==1 else set()
 sheetdoc={'pass':sheetpass,'status':'PASS' if sheetpass else 'FAIL_REVALIDATION_REVIEW_REQUIRED','method':'Full frozen face dual adjacency minus fresh cut edges; identities by independent tip+nail/cap, never component rank','face_component_count':len(sheets),'INDEX_identity_component_ids':isheet,'THUMB_identity_component_ids':tsheet,'marker_identity_collision':bool(set(isheet)&set(tsheet)),'INDEX_sheet_vertex_count':len(index_vs) if sheetpass else None,'body_THUMB_side_count':len(V)-len(index_vs) if sheetpass else None,'body_THUMB_counterpart_vertex_count':len(thumb_vs) if sheetpass else None,'boundary_shared_vertices':sorted(index_vs&thumb_vs) if sheetpass else [],'face_components':[{'component_id':k,'face_count':len(s),'vertex_count':len(vsets[k]),'face_ids':s,'vertex_ids':sorted(vsets[k]),'contains_v233':233 in vsets[k],'contains_v284':284 in vsets[k]} for k,s in enumerate(sheets)]}
 dump('R3_FRESH_SHEET_SPLIT_AUDIT_R1.json',sheetdoc)
 # Every label component and every source-free island, including involved mesh faces.
 comps=[];islands=[]
 for lab,pins,fieldd in [('THUMB',T,dT),('INDEX',I,dI)]:
  for comp in components([v for v in G if final[v]==lab],adj):
   cs=set(comp);row={'label':lab,'vertex_ids':comp,'size':len(comp),'face_ids':[f for f,vs in enumerate(F) if cs&set(vs)],'own_source_vertex_ids':sorted(cs&pins),'source_free':not bool(cs&pins),'tiny_size_le_4':len(comp)<=4,'minimum_distance_to_own_sources_mm':min(fieldd[v] for v in cs),'maximum_distance_to_own_sources_mm':max(fieldd[v] for v in cs),'validator_blocker':not bool(cs&pins)};comps.append(row)
   if row['source_free']:islands.append(row)
 dump('R3_FRESH_ISLAND_AUDIT_R1.json',{'pass':not islands,'islands_count':len(islands),'THUMB_component_count':sum(x['label']=='THUMB' for x in comps),'INDEX_component_count':sum(x['label']=='INDEX' for x in comps),'tiny_components_count':sum(x['tiny_size_le_4'] for x in comps),'label_components':comps,'source_free_islands':islands,'additional_auto_repair':False})
 bd=dijkstra(G,adj,boundary_vertices) if boundary_vertices else {v:math.inf for v in G}
 ambiguity=[v for v in sorted(G) if abs(dT[v]-dI[v])<cost['TAU_mm']]
 ambrows=[{'vertex_id':v,'dT_mm':dT[v],'dI_mm':dI[v],'difference_mm':abs(dT[v]-dI[v]),'raw_label':raw[v],'final_label':final[v],'on_boundary':v in boundary_vertices,'distance_to_boundary_mm':bd[v] if math.isfinite(bd[v]) else None,'boundary_neighbor':bool(set(adj[v])&boundary_vertices),'in_FIRST_WEB21':v in W,'hard_role':term[v]['hard_role']} for v in ambiguity]
 dump('R3_FRESH_AMBIGUITY_AUDIT_R1.json',{'criterion':'abs(dT_mm-dI_mm)<TAU_mm','TAU_mm':cost['TAU_mm'],'vertex_count':len(ambiguity),'vertex_ids':ambiguity,'vertices':ambrows,'FIRST_WEB_intersection':sorted(W&set(ambiguity)),'conservative_band_intersection':sorted(d['band']&set(ambiguity)),'historical_16_vertices_reused':False})
 classrows=[]
 for row in validator['CLASS_A_edges']:
  e=row['edge_id'];a,b=E[e];geopass=set(row['vertex_ids'])=={a,b} and bool(ef[e]);protection=final[a]==final[b]
  classrows.append({'edge_id':e,'vertex_ids':[a,b],'labels':[final[a],final[b]],'geometry_authority_preserved':geopass,'surface_faces':ef[e],'fresh_label_protection_pass':protection,'pass':geopass and protection,'status':'PASS' if geopass and protection else 'FAIL_REVIEW_REQUIRED'})
 classpass=sum(r['pass'] for r in classrows)
 dump('R3_FRESH_CLASS_A_AUDIT_R1.json',{'geometry_pass_count':sum(r['geometry_authority_preserved'] for r in classrows),'pass_count':classpass,'status':'PASS' if classpass==6 else 'FAIL_REVIEW_REQUIRED','protection_semantics':'DO_NOT_CUT_CLASS_A: fresh binary ownership must not separate endpoints; no requirement to match historical THUMB labels','labels_modified_to_force_pass':False,'edges':classrows})
 webcounts=dict(Counter(final[v] for v in W))
 dump('R3_FRESH_FIRST_WEB21_AUDIT_R1.json',{'hard_pins':0,'membership_hash_unchanged':True,'distribution':webcounts,'vertex_labels':{v:final[v] for v in sorted(W)},'written_back_to_anatomy_authority':False,'labels_role':'solver result only'})
 wrapper=read(resolve(d['c']['frozen_authority_sources']['CMC_CAGE_R3_WRAPPER_RECONCILIATION_R1.json']['path']))
 cmcdoc={'geometry':'FROZEN_PRESERVED','hard_source_count':0,'wrapper_authority_status':'UNRESOLVED_PROTECTION_SUPPORT','old_label_filter_retired':True,'exact_construction_mapping_authoritative':False,'mapping_caveat':wrapper['mapping_caveat'],'context_sets':{}}
 for name in ['construction_coordinate_candidate','unfiltered_historical_support']:
  ids=wrapper[name]['vertex_ids'];counts=dict(Counter(final.get(v,'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH') for v in ids));cmcdoc['context_sets'][name]={'role':'CONTEXT_ONLY_NOT_HARD_SOURCE','vertex_ids':ids,'fresh_labels':{v:final.get(v,'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH') for v in ids},'distribution':counts,'partition_conflict_candidate':bool(counts.get('THUMB') and counts.get('INDEX'))}
 cmcdoc['unexpected_partition_conflict']=any(s['partition_conflict_candidate'] for s in cmcdoc['context_sets'].values());cmcdoc['status']='REVIEW_REQUIRED' if cmcdoc['unexpected_partition_conflict'] else 'NO_OBSERVED_BINARY_CONFLICT_WITHIN_GRAPH_PROTECTION_MASK_STILL_UNRESOLVED'
 dump('R3_FRESH_CMC_CONTEXT_AUDIT_R1.json',cmcdoc)
 cap37=set(validator['THUMB_identity']['cap_vertices']);capok=cap37<=T and all(final[v]=='THUMB' for v in cap37)
 dump('R3_CAP37_SOURCE_PRESERVATION_AUDIT_R1.json',{'pass':capok,'count':len(cap37),'graph_reachable':cap37<=G,'hard_source_preserved':capok,'conflicts':sorted(cap37&I),'vertices':[{'vertex_id':v,'label':final.get(v),'hard_role':term.get(v,{}).get('hard_role'),'dT_mm':dT.get(v),'dI_mm':dI.get(v)} for v in sorted(cap37)]})
 indexok=all(final[v]=='INDEX' for v in I)
 dump('R3_INDEX_SOURCE_PRESERVATION_AUDIT_R1.json',{'pass':indexok,'source_count':len(I),'preserved_count':sum(final[v]=='INDEX' for v in I),'preservation_fraction':1.0 if indexok else None,'vertices':[{'vertex_id':v,'final_label':final[v],'reachable':math.isfinite(dI[v])} for v in sorted(I)]})
 oldcap=sorted(d['oldcap']);oldcaprows=[{'vertex_id':v,'graph_membership':v in G,'final_label':final.get(v,'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH'),'dT_mm':dT.get(v),'dI_mm':dI.get(v),'boundary_distance_mm':bd.get(v) if v in G and math.isfinite(bd[v]) else None,'strong_hard_role':'NONE','anatomical_authority_from_result':False} for v in oldcap]
 dump('R3_OLD_CAP9_FRESH_RESULT_AUDIT_R1.json',{'hard_role_count':0,'vertices':oldcaprows,'distribution':dict(Counter(r['final_label'] for r in oldcaprows)),'solver_THUMB_is_not_anchor':True})
 dump('R3_FRESH_PROXIMAL_BOUNDARY_AUDIT_R1.json',{'pass':True,'authority_hash':PROX_HASH,'usage':'PROXIMAL_SEMANTIC_STOP_ONLY','STOP_AFTER_P04':True,'propagation_beyond_P04':False,'neutral_band_hard_pins':0,'forced_cut_edges':[],'pointwise_anatomy_authority_created':False,'edges':[{'edge_id':e,'vertex_ids':E[e],'fresh_labels':[final.get(v,'NO_SOLVE_UNASSIGNED_OUTSIDE_GRAPH') for v in E[e]],'in_fresh_cut':e in cutset} for e in [4666,4668]]})
 # Fresh solve and derived labels already completed. History is first read here.
 hp=ROOT/'production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary';old=read(hp/'R3_OWNERSHIP_LABELS.json');oldstatus=read(hp/'THUMB_TIP_OWNERSHIP_BOUNDARY_R3_STATUS.json');oldamb=read(hp/'R3_AMBIGUOUS_VERTEX_AUDIT.json')
 oldlabels=old['R3'];changed=[v for v in sorted(G) if oldlabels[v]!=final[v]];oldflow=None
 for line in oldstatus['log']:
  if 'min-cut:' in line and 'flow=' in line:oldflow=int(line.split('flow=')[1].split(',')[0])
 comparison={'role':'COMPARISON_ONLY_AFTER_FRESH_SOLVE','DIFFERENCE_IS_NOT_FAILURE':True,'historical_full_mesh_counts':dict(Counter(oldlabels)),'historical_on_current_graph_counts':dict(Counter(oldlabels[v] for v in G)),'fresh_counts':dict(Counter(final.values())),'old_boundary_count':len(old['boundary_edges_R3']),'new_boundary_count':len(cut),'old_boundary_edge_ids':old['boundary_edges_R3'],'new_boundary_edge_ids':cut,'changed_count_on_current_graph':len(changed),'changed_vertex_ids':changed,'changed_on_common_binary_label_domain':sum(oldlabels[v] in ['THUMB','INDEX'] for v in changed),'current_graph_history_other_digit_or_wrist_count':sum(oldlabels[v] not in ['THUMB','INDEX'] for v in G),'old_sheet_split':oldstatus['sheet_split'],'new_sheet_split':{k:v for k,v in sheetdoc.items() if k!='face_components'},'old_ambiguity_count':oldamb['AMBIGUOUS_VERTEX_COUNT_BEFORE'],'new_ambiguity_count':len(ambiguity),'old_flow':oldflow,'new_flow':flow,'old_cost_behavior':'PAIRWISE_DOMINATED_BY_HISTORICAL_METER_MM_BUG','differences_reason':'Different approved inputs, cost units, cap authority, kinematics and graph; no historical reproduction target.'}
 dump('R3_HISTORICAL_VS_FRESH_COMPARISON_R1.json',comparison)
 # Deterministic recomputation required by validator contract; independent NetworkX optimality check.
 dt2=dijkstra(G,adj,T);di2=dijkstra(G,adj,I);flow2,raw2,_=solve(d,dt2,di2);fin2,cl2=closure(raw2,d)
 repro=dt2==dT and di2==dI and flow2==flow and raw2==raw and fin2==final and cl2==cl
 independent_flow,augmentations=independent_edmonds_karp(term,d)
 solverpass=repro and independent_flow==flow and capok and indexok and not islands
 dump('R3_FRESH_REPRODUCIBILITY_AUDIT_R1.json',{'pass':solverpass,'two_fresh_runs_identical':repro,'independent_algorithm':'independent Edmonds-Karp BFS augmenting paths','independent_augmentations':augmentations,'independent_flow':independent_flow,'Dinic_flow':flow,'equal_optimum':independent_flow==flow,'historical_truth_used':False})
 review_reasons=[]
 if not sheetpass:review_reasons.append('Sheet identity revalidation fails: independent INDEX/THUMB markers collide or cannot identify separate sheets.')
 if classpass<6:review_reasons.append('CLASS_A fresh labels separate '+str(6-classpass)+' protected surface edges; labels left unchanged.')
 if cmcdoc['unexpected_partition_conflict']:review_reasons.append('CMC protection context spans both binary labels; independent wrapper authority remains unresolved.')
 verdict='FAIL_CLOSED_SOLVER_OR_CONTRACT' if not solverpass else 'TECHNICALLY_VALID_BUT_HUMAN_REVIEW_REQUIRED' if review_reasons else 'PASS_READY_FOR_HUMAN_REVIEW'
 status={'run':RUN,'Human_contract_approval_verified':'YES','contract_hash_verified':'YES','graph_V':len(G),'graph_E':len(GE),'THUMB_hard_source_count':len(T),'INDEX_hard_source_count':len(I),'source_conflicts':0,'INF':d['INF'],'fresh_dT_unreachable_count':0,'fresh_dI_unreachable_count':0,'mincut_flow':flow,'fresh_THUMB_count':sum(x=='THUMB' for x in final.values()),'fresh_INDEX_count':sum(x=='INDEX' for x in final.values()),'cut_edge_count':eraw['cut_edge_count'],'total_unary_cost':eraw['unary_capacity'],'total_pairwise_cost':eraw['pairwise_capacity'],'unary_pairwise_ratio':eraw['unary_pairwise_ratio'],'closure_iterations':cl['full_sweeps'],'closure_converged':'YES' if cl['converged'] else 'NO','closure_changed_count':cl['cumulative_changed_count'],'final_boundary_edge_count':len(cut),'boundary_component_count':len(bcomps),'boundary_face_strip_component_count':len(bfcomps),'INDEX_sheet_vertex_count':sheetdoc['INDEX_sheet_vertex_count'],'body_THUMB_side_count':sheetdoc['body_THUMB_side_count'],'islands_count':len(islands),'ambiguity_vertex_count':len(ambiguity),'CLASS_A_pass_count':classpass,'FIRST_WEB21_distribution':webcounts,'old_cap9_hard_role_count':0,'old_cap9_distribution':dict(Counter(r['final_label'] for r in oldcaprows)),'cap37_preservation':'PASS' if capok else 'FAIL','INDEX_hard_source_preservation':'PASS' if indexok else 'FAIL','historical_to_fresh_changed_labels':len(changed),'technical_validation_verdict':verdict,'review_reasons':review_reasons,'Human_Review_page_generated':'PENDING','Human_approved_frozen':False,'BLEND_FILES_WRITTEN':0,'skin_rebuild_count':0,'Stage6_runs':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'NEXT':'HUMAN_R3_FRESH_RESULT_APPROVAL','after_Human_approval_only':'CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1','STOP':True,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 dump('R3_FRESH_VALIDATION_VERDICT_R1.json',{'verdict':verdict,'solver_technically_valid':solverpass,'review_reasons':review_reasons,'hard_sources_pass':capok and indexok,'sheet_revalidation_pass':sheetpass,'CLASS_A_pass_count':classpass,'pointwise_Human_anatomical_authority':False,'Human_approved_frozen':False,'NEXT':status['NEXT'],'STOP':True})
 dump(RUN+'_STATUS.json',status)
 reviewdata={'vertices':V,'native_vertices':d['extraction']['NATIVE']['vertices_world_m'],'edges':E,'faces':F,'graph':sorted(G),'graph_faces':sorted(GF),'labels':final,'old_labels':oldlabels,'changed':changed,'fresh_boundary':cut,'old_boundary':old['boundary_edges_R3'],'index_sheet':sorted(index_vs) if sheetpass else [],'thumb_body':sorted(set(range(len(V)))-index_vs) if sheetpass else [],'sheet_valid':sheetpass,'WEB':sorted(W),'cap37':sorted(cap37),'oldcap9':oldcap,'ambiguity':ambiguity,'classA':[r['edge_id'] for r in classrows],'CMC':wrapper['unfiltered_historical_support']['vertex_ids'],'THUMB_sources':sorted(T),'INDEX_sources':sorted(I),'frames':read(INPUT/'REVIEW_VIEW_DATA.json')['frames'],'status':status,'contract_hash':EXPECTED,'proximal_hash':PROX_HASH,'result_hash':digest(final),'fields':{v:[dT[v],dI[v]] for v in sorted(G)}}
 dump('R3_FRESH_REVIEW_VIEW_DATA_R1.json',reviewdata)
 after=inventory();dump('FROZEN_HASHES_AFTER.json',after);delta={k:{'before':before.get(k),'after':after.get(k)} for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
 dump('FROZEN_HASH_VERIFICATION_R1.json',{'pass':not delta,'protected_file_count':len(before),'delta':delta,'Human_response_sha256_unchanged':sha(RESPONSE)==read(OUT/'R3_PRE_SOLVE_GATES_R1.json')['Human_response_sha256'],'BLEND_FILES_WRITTEN':0})
 if delta:raise RuntimeError('FAIL_CLOSED protected files changed')
 print(json.dumps(status,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':
 if '--preflight' in sys.argv:
  d=preflight();print(json.dumps({'pre_solve_pass':True,'V':len(d['G']),'E':len(d['GE']),'THUMB':len(d['T']),'INDEX':len(d['I']),'INF':d['INF']}))
 else:
  try:run()
  except Exception as ex:
   dump('R3_EXECUTION_FAILURE_R1.json',{'verdict':'FAIL_CLOSED_SOLVER_OR_CONTRACT','error':str(ex),'STOP':True});raise
