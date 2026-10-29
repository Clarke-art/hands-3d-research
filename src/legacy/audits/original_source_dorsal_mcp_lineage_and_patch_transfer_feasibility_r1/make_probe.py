import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np
S=read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages'];T=read(OUT/'HISTORICAL_OPERATION_RAM_REPLAY.json');J=np.array(read(OUT/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json')['per_vertex_linear_part']);R=read(OLD/'DORSAL_MCP_DENT_ROI_R1.json')
donor=np.array(S['OFFICIAL_L1']['canonical_world_m']);rest=np.array(S['STAGE4A_R2']['canonical_world_m']);current=np.array(S['R2_PRODUCTION']['canonical_world_m']);A=T['final_ancestry'];delta=np.zeros_like(rest)
target=np.array([sum((donor[int(k)]*w for k,w in a.items()),np.zeros(3)) for a in A]);delta[:len(A)]=target-rest[:len(A)]
eligible=set(np.where(np.linalg.norm(delta,axis=1)*1000>1e-5)[0].tolist())
adj=[set() for _ in rest]
for a,b in S['R2_PRODUCTION']['edges']:adj[a].add(b);adj[b].add(a)
remaining=set(eligible);components=[]
while remaining:
 todo=[remaining.pop()];comp=set(todo)
 while todo:
  a=todo.pop();new=remaining&adj[a];remaining-=new;comp|=new;todo.extend(new)
 components.append(comp)
chosen=[c for c in components if c&set(R['core_vertices'])]
assert chosen
selected=set.union(*chosen)
# Cut rings on the same donor edges can be separated by unchanged old vertices.
# Close scope over shared actual donor parent-edge ancestry, not only moved-edge adjacency.
while True:
 roots={int(k) for i in selected for k in A[i]}
 extension={i for i in eligible if set(map(int,A[i]))&roots}
 if extension<=selected:break
 selected|=extension
ids=sorted(selected);boundary=sorted({j for i in ids for j in adj[i]}-set(ids))
probe=current.copy()
for i in ids:probe[i]+=J[i]@delta[i]
write=[{'vertex_id':i,'L1_parent_weights':A[i],'rest_current_world_m':rest[i].tolist(),'donor_derived_rest_world_m':target[i].tolist(),'rest_delta_mm':(delta[i]*1000).tolist(),'current_world_m':current[i].tolist(),'probe_world_m':probe[i].tolist(),'reason':'Nonzero donor deviation in historical CON1/CON3 blast-radius component connected to Human core. Exact L1 edge ancestry, propagated by frozen RSSF per-vertex transform.'} for i in ids]
dump('TEMP_DONOR_TRANSFER_DESIGN_ONLY.json',{'NOT_PRODUCTION':True,'NOT_APPROVED':True,'world_mm':(probe*1000).tolist(),'faces':S['R2_PRODUCTION']['faces'],'edges':S['R2_PRODUCTION']['edges'],'moved_vertex_ids':ids,'write_set':write,'DONOR_RESTORE_CORE':ids,'DONOR_TRANSITION_RING':[],'UNCHANGED_BOUNDARY':boundary,'boundary_blending':'Not required: mapped donor deviation is zero at unchanged historical source boundary; no free fairing','scope_method':'Nonzero donor deviation components seeded by frozen Human core, closed over shared actual L1 parent-edge ancestry. Include successive inserted rings sharing donor edges even when an unchanged old vertex separates moved-vertex components. No fixed 15/52/111 support preset.','all_deviation_components':[{'vertex_ids':sorted(c),'selected':bool(c&selected)} for c in components],'unselected_remote_operations':'DIP pole relocation, CMC surgery and unconnected parent-edge components remain unchanged','new_CMC_vertices_outside_L1_mapping_unchanged':True,'RSSF_authority_edited':False,'production_weights_used_as_donor_mapping':False})
print('TEMP PROBE',len(ids),'vertices','max move mm',np.max(np.linalg.norm(probe-current,axis=1))*1000,'components',[len(c) for c in components],flush=True)
# Per historical operation metrics on the exact ancestry-mapped physical patch.
roi_l1={int(k) for i in R['vertices'] for k in A[i]};oprows=[]
def norm(v,p):
 q=v[p];a=sum((np.cross(q[k]-q[0],q[(k+1)%len(q)]-q[0]) for k in range(len(q))),np.zeros(3));return a/max(np.linalg.norm(a),1e-15)
for snap in T['snapshots']:
 v=np.array(snap['local_m'])*1000;F=snap['faces'];affected={i for i,a in enumerate(snap['ancestry']) if set(map(int,a))&roi_l1};fs=[fi for fi,p in enumerate(F) if set(p)&affected];ef={}
 for fi in fs:
  p=F[fi]
  for a,b in zip(p,p[1:]+p[:1]):ef.setdefault(tuple(sorted([a,b])),[]).append(fi)
 ns={fi:norm(v,F[fi]) for fi in fs};di=[{'edge_vertices':list(e),'faces':f,'degrees':float(np.degrees(np.arccos(np.clip(ns[f[0]]@ns[f[1]],-1,1))))} for e,f in ef.items() if len(f)==2]
 worst=max(di,key=lambda z:z['degrees']);oprows.append({'operation':snap['name'],'counts':{'V':len(v),'F':len(F)},'max_mapped_patch_dihedral_deg':worst['degrees'],'worst_edge':worst})
 print(snap['name'],round(worst['degrees'],3),flush=True)
dump('OPERATION_SEQUENCE_METRICS.json',oprows)
