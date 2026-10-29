"""Independent donor re-evaluation and position-only formal Stage4C derivation."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from payload import protected,PAYLOAD_SOURCE
import bpy,numpy as np
from mathutils import Vector,Matrix
prior_manifest=read(PRIOR/'OUTPUT_EVIDENCE_HASH_MANIFEST.json')
inputs=['DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json','DONOR_PATCH_TRANSFER_FEASIBILITY_R1.json','TEMP_DONOR_TRANSFER_DESIGN_ONLY.json','HISTORICAL_OPERATION_RAM_REPLAY.json','HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json','RAW_SOURCE_GEOMETRY.json']
for name in inputs:assert sha(PRIOR/name)==prior_manifest[name],('Prior frozen evidence drift',name)
S=read(PRIOR/'RAW_SOURCE_GEOMETRY.json')['stages'];T=read(PRIOR/'HISTORICAL_OPERATION_RAM_REPLAY.json');C=read(PRIOR/'DONOR_TO_CURRENT_TOPOLOGY_CORRESPONDENCE_R1.json');P=read(PRIOR/'TEMP_DONOR_TRANSFER_DESIGN_ONLY.json');J=read(PRIOR/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json')
assert read(PRIOR/'DONOR_PATCH_TRANSFER_FEASIBILITY_R1.json')['transfer_structural_gate']=='PASS'
for path,label in [(MASTER,'OFFICIAL_L1'),(SOURCE,'STAGE4C_R2'),(REST,'STAGE4A_R2'),(R2,'R2_PRODUCTION')]:assert sha(path)==S[label]['input']['sha256']
bpy.ops.wm.open_mainfile(filepath=str(MASTER),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];m=next(m for m in ob.modifiers if m.type=='MULTIRES');assert m.total_levels==1;m.levels=1
bpy.context.view_layer.update();eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());em=eo.to_mesh();norm=Matrix.Diagonal((1.,-1.,-1.));donor=np.array([list(ob.matrix_world@(<REDACTED_EMAIL>)) for v in em.vertices]);donorlocal=[list(v.co) for v in em.vertices];donorfaces=[list(f.vertices) for f in em.polygons];eo.to_mesh_clear()
assert donorlocal==S['OFFICIAL_L1']['local_m'] and donorfaces==S['OFFICIAL_L1']['faces'],'Actual official stored L1 changed'
bpy.ops.wm.open_mainfile(filepath=str(REST),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];rest=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);assert rest.tolist()==S['STAGE4A_R2']['canonical_world_m']
A=T['final_ancestry'];target=np.empty((len(A),3));ancestry_checks=[]
for i,a in enumerate(A):
 assert abs(sum(a.values())-1)<1e-6 and all(0<=int(k)<len(donor) and w>=0 for k,w in a.items())
 target[i]=sum((donor[int(k)]*w for k,w in a.items()),np.zeros(3))
# Validate recorded actual edge fractions against native parent-edge state for every split.
edge_validation=[]
for step,event in enumerate(T['events']):
 inputstate=T['snapshots'][step];verts=np.array(inputstate['local_m']);weights=inputstate['ancestry'];edges={tuple(sorted([a,b])) for p in inputstate['faces'] for a,b in zip(p,p[1:]+p[:1])}
 for row in event['new_vertices']:
  p=np.array(row['pre_projection_local_m']);hits=[]
  for a,b in edges:
   d=verts[b]-verts[a];t=float((p-verts[a])@d/(d@d))
   if 0<t<1 and np.linalg.norm(p-(verts[a]+t*d))<1e-7:
    w={}
    for idx,f in [(a,1-t),(b,t)]:
     for k,z in weights[idx].items():w[k]=w.get(k,0)+z*f
    if set(w)==set(row['L1_ancestry']) and max(abs(w[k]-row['L1_ancestry'][k]) for k in w)<1e-6:hits.append([a,b,t])
  assert len(hits)==1,('Parent edge is not uniquely reproduced',row['vertex_id'],hits)
  edge_validation.append({'vertex_id':row['vertex_id'],'operation':event['label'],'actual_parent_edge':hits[0][:2],'fraction_recomputed':hits[0][2],'frozen_fraction':row['parent_edge_fraction']})
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];before=protected(ob);locals0=[list(v.co) for v in ob.data.vertices];current=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);assert current.tolist()==S['STAGE4C_R2']['canonical_world_m'];assert current.tolist()==S['R2_PRODUCTION']['canonical_world_m']
delta=np.zeros_like(rest);delta[:len(A)]=target-rest[:len(A)];eligible=set(np.where(np.linalg.norm(delta,axis=1)*1000>1e-5)[0].tolist());adj=[set() for _ in rest]
for e in ob.data.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
core=set(read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json')['core_vertices']);remaining=set(eligible);selected=set()
while remaining:
 todo=[remaining.pop()];component=set(todo)
 while todo:
  a=todo.pop();new=remaining&adj[a];remaining-=new;component|=new;todo.extend(new)
 if component&core:selected|=component
while True:
 roots={k for i in selected for k in A[i]};extension={i for i in eligible if set(A[i])&roots}
 if extension<=selected:break
 selected|=extension
ids=sorted(selected);assert len(ids)==54 and ids==P['moved_vertex_ids'],'FAIL_CLOSED_FORMAL_TRANSFER_REPRODUCTION: write set'
worldtarget=current.copy();jac=np.array(J['per_vertex_linear_part']);writes=[]
for i in ids:
 worldtarget[i]=current[i]+jac[i]@delta[i]
 assert dict(P['write_set'][ids.index(i)]['L1_parent_weights'])==A[i]
 if str(i) in C['current_ROI_to_source']:assert C['current_ROI_to_source'][str(i)]['L1_parent_weights']==A[i]
 writes.append({'vertex_id':i,'official_L1_parent_weights':A[i],'donor_rest_target_world_m':target[i].tolist(),'historical_rest_world_m':rest[i].tolist(),'frozen_RSSF_linear_transform':jac[i].tolist(),'source_world_m':current[i].tolist(),'computed_target_world_m':worldtarget[i].tolist(),'restoration_reason':'Nonzero donor deviation in frozen ancestry-closed Human defect blast radius. Exact recorded edge-parent interpolation (original L1 vertex for existing vertices) plus frozen RSSF linear transform; no fitting or tuning.'})
inv=ob.matrix_world.inverted()
for i in ids:
 # Match the specified historical storage conversion exactly; no source/probe target copying.
 ob.data.vertices[i].co=inv@(Vector(worldtarget[i]*1000)/1000)
ob.data.update()
for key,val in {'DESIGN_ONLY':True,'NOT_PRODUCTION':True,'NOT_HUMAN_APPROVED':True,'DO_NOT_PROMOTE':True,'PHASE':PHASE}.items():ob['AMENDMENT_'+key]=val
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),copy=True,compress=False)
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE),load_ui=False,use_scripts=False);ob=bpy.data.objects['Hand  - Realistic'];after=protected(ob);assert before==after,('Protected payload drift',[k for k in before if before[k]!=after[k]])
saved=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);local=[list(v.co) for v in ob.data.vertices];changed=[i for i in range(len(local)) if local[i]!=locals0[i]];assert changed==ids
probe=np.array(P['world_mm'])/1000;probeerr=np.linalg.norm(saved-probe,axis=1)*1000;assert saved.tolist()==probe.tolist(),'FAIL_CLOSED_DONOR_TRANSFER_FORMALIZATION: stored coordinates mismatch'
fidelity=np.linalg.norm(saved[ids]-worldtarget[ids],axis=1)*1000
for row in writes:
 i=row['vertex_id'];row['target_local_m']=local[i];row['saved_target_world_m']=saved[i].tolist();row['delta_world_mm']=((saved[i]-current[i])*1000).tolist()
dump('FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json',{'RECOMPUTED_WRITE_SET_COUNT':len(ids),'PROBE_WRITE_SET_COUNT':len(P['moved_vertex_ids']),'WRITE_SET_IDENTITY_MATCH':True,'vertex_ids':ids,'write_set':writes,'all54_explicit_ancestry_and_reason':True,'scope_expansion':0,'optimization_or_fairing_steps':0})
dump('FORMAL_DONOR_TRANSFER_COORDINATES_R1.json',{'source_world_mm':(current*1000).tolist(),'candidate_world_mm':(saved*1000).tolist(),'candidate_local_m':local,'source_local_m':locals0,'unrounded_ancestry_target_world_mm':(worldtarget*1000).tolist(),'faces':[list(f.vertices) for f in ob.data.polygons],'edges':[list(e.vertices) for e in ob.data.edges],'smooth_flags':[f.use_smooth for f in ob.data.polygons],'MAX_COORD_DELTA_VS_PROBE_MM':float(probeerr.max()),'DONOR_FIDELITY':{'max_mm':float(fidelity.max()),'mean_mm':float(fidelity.mean()),'RMS_mm':float(np.sqrt(np.mean(fidelity**2))),'p95_mm':float(np.percentile(fidelity,95)),'semantics':'Exact54 ancestry targets after frozen RSSF, before versus after native float32 storage; no nearest-surface distance. Outside write set retains engineered current surface by design.'},'TOTAL_VERTEX_POSITION_CHANGED':len(changed),'OUTSIDE54_POSITION_DRIFT_COUNT':sum(i not in selected for i in changed),'TOPOLOGY_DRIFT':0,'UV_DRIFT':0,'MATERIAL_DRIFT':0,'WEIGHT_DRIFT':0,'BONE_JOINT_DRIFT':0})
dump('FORMAL_PAYLOAD_PRESERVATION_R1.json',{'status':'PASS','all_protected_fields_exact':True,'protected_fields':list(before),'before_payload_digest':digest(before),'after_payload_digest':digest(after),'payload_AST_provenance':PAYLOAD_SOURCE,'manifold_incidence_identical':True,'outside54_local_positions_exact_zero':True,'custom_normal_state':before['custom_normal_state'],'vertex_group_count':len(before['groups']),'armature_count':len(before['armatures']),'required_design_metadata_only_exception':'AMENDMENT_DESIGN_ONLY / NOT_PRODUCTION / NOT_HUMAN_APPROVED / DO_NOT_PROMOTE / PHASE object custom properties. Existing custom properties and all mesh data unchanged except54 positions.'})
dump('FORMAL_DONOR_TRANSFER_PROVENANCE_R1.json',{'DONOR_SOURCE':ref(MASTER),'donor_object':'Hand  - Realistic','donor_layer':'Official stored Multires L1','SOURCE_STAGE4C':ref(SOURCE),'historical_rest_ancestor':ref(REST),'FORMAL_CANDIDATE':ref(CANDIDATE),'verified_prior_inputs':[ref(PRIOR/n) for n in inputs],'official_L1_re_evaluated_from_master':True,'official_L1_coordinates_and_native_cycles_exact_vs_frozen_evidence':True,'Stage2_evaluated_L1_equality_authority':ref(PRIOR/'SOURCE_GEOMETRY_LINEAGE_R1.json'),'actual_split_parent_edge_independent_validation':edge_validation,'frozen_RSSF_native_reconstruction_authority':ref(PRIOR/'HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json'),'WRITE_SET_REPRODUCED':'54/54','MAX_COORD_DELTA_VS_PROBE_MM':float(probeerr.max()),'copied_final_probe_coordinates':False,'deterministic_formula':'source_stage4c[i] + frozen_RSSF_J[i] * (sum(parent_weight * actual_official_L1[parent]) - historical_stage4a_rest[i]); same native float32 storage conversion','metadata':['DESIGN_ONLY','NOT_PRODUCTION','NOT_HUMAN_APPROVED','DO_NOT_PROMOTE'],'downstream_execution':False})
print('FORMAL CANDIDATE REPRODUCED',len(ids),'probe max delta mm',probeerr.max(),'fidelity max mm',fidelity.max(),flush=True)
