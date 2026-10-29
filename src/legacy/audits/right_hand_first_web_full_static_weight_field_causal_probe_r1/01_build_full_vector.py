"""Exactly ONE full-vector Dirichlet harmonic intervention; validation before renders."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
assert not CANDIDATE.exists(),'ONE candidate only; refusing overwrite'
before = protected_inputs()
authority = {}
for folder,name in [(TOPO,'RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend'),(PREV,'RIGHT_HAND_FIRST_WEB_WEIGHT_FIELD_PROBE_R1.blend')]:
    p=folder/name
    bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
    authority[folder.name]={'sha256':sha(p),'objects':[{'name':o.name,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in bpy.data.objects], 'action_payload_sha256':digest(action_payload(bpy.data.actions[ACTION])),'experiment_repeated':False}
    assert authority[folder.name]['action_payload_sha256']==APPROVED_ACTION_SHA
ob,rig=open_frozen()
native=native_no_weights(ob,rig);shape=shape_state(ob);W=weights(ob);ZERO=coords(ob)
roi,boundary=topology_roi(ob)
old=read(PREV/'READ_ONLY_WEIGHT_FIELD_R1.json')
assert roi==old['ROI_ids'] and set(boundary)==set(old['boundary_ids'])
free=sorted(set(roi)-set(boundary));slot={v:i for i,v in enumerate(free)}
names=[g.name for g in ob.vertex_groups]
bones=[b.name for b in rig.data.bones];deform=[b.name for b in rig.data.bones if b.use_deform]
assert len(bones)==21 and len(deform)==16 and set(names)==set(deform)
active=[i for i in range(len(names)) if np.any(W[roi,i]>0)]
inactive=[n for n in bones if n not in [names[i] for i in active]]
assert np.max(abs(W.sum(1)-1))<2e-7
edges=np.array([list(e.vertices) for e in ob.data.edges if all(i in roi for i in e.vertices)])
# The operator uses original mesh Basis positions in world space, never a posed frame.
REST=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices])
ell=np.linalg.norm(REST[edges[:,1]]-REST[edges[:,0]],axis=1)
assert np.all(ell>1e-12)
L=np.zeros((len(free),len(free)));rhs=np.zeros((len(free),len(active)))
for (a,b),length in zip(edges,ell):
    c=1./length
    for i,j in [(a,b),(b,a)]:
        if i not in slot: continue
        k=slot[i];L[k,k]+=c
        if j in slot: L[k,slot[j]]-=c
        else: rhs[k]+=c*W[j,active]
solution=np.linalg.solve(L,rhs)
residual=float(np.max(abs(L@solution-rhs)))
sum_before=solution.sum(1)
assert solution.min()>=0 and np.max(abs(sum_before-1))<2e-7
# Only remove floating-point partition-of-unity error; no artistic redistribution.
solution/=sum_before[:,None]
target=W.copy();target[np.ix_(free,active)]=solution
for i in free:
    for j in active: ob.vertex_groups[j].add([i],float(target[i,j]),'REPLACE')
bpy.context.view_layer.update()
WW=weights(ob);outside=sorted(set(range(len(W)))-set(roi))
assert np.array_equal(WW[outside],W[outside]) and np.array_equal(WW[boundary],W[boundary])
assert WW.min()>=0 and np.max(abs(WW.sum(1)-1))<2e-7
assert native_no_weights(ob,rig)==native and shape_state(ob)==shape
assert digest(action_payload(bpy.data.actions[ACTION]))==APPROVED_ACTION_SHA
zero_delta=float(np.max(np.linalg.norm(coords(ob)-ZERO,axis=1))*1000)
assert zero_delta<.001
E=np.array([r['edge'] for r in old['representative_edges']]);bandell=np.linalg.norm(REST[E[:,1]]-REST[E[:,0]],axis=1)*1000
def grad(ww,ee,length): return abs(ww[ee[:,1]]-ww[ee[:,0]])/length[:,None]
g0=grad(W,edges,ell*1000);g1=grad(WW,edges,ell*1000)
b0=grad(W,E,bandell);b1=grad(WW,E,bandell)
def comparison(x,y):
    return {'before':stats(x),'after':stats(y),'mean_reduction_percent':float((1-y.mean()/x.mean())*100) if x.mean()>0 else None,'max_reduction_percent':float((1-y.max()/x.max())*100) if x.max()>0 else None}
perbone={names[j]:{'ROI':comparison(g0[:,j],g1[:,j]),'high_strain_band':comparison(b0[:,j],b1[:,j]),'changed_free_vertices':int(np.count_nonzero(WW[free,j]!=W[free,j])),'max_abs_weight_change':float(np.max(abs(WW[free,j]-W[free,j])))} for j in active}
full_roi=comparison(g0.sum(1),g1.sum(1));full_band=comparison(b0.sum(1),b1.sum(1))
wi=names.index('WRIST_R');ti=names.index('THUMB_CMC_R');diff=abs(W[E[:,1]]-W[E[:,0]])
pair_fraction=(diff[:,wi]+diff[:,ti])/diff.sum(1)
energy0=float(np.sum((1./ell)*np.sum((W[edges[:,1]]-W[edges[:,0]])**2,axis=1)))
energy1=float(np.sum((1./ell)*np.sum((WW[edges[:,1]]-WW[edges[:,0]])**2,axis=1)))
modified=all(perbone[names[j]]['changed_free_vertices']>0 for j in active if np.ptp(W[roi,j])>0)
# Fixed manipulation-validity criterion, not fitted to surface quality: both means reduce >=20%.
reduced=full_roi['mean_reduction_percent']>=20 and full_band['mean_reduction_percent']>=20
dump('FULL_VECTOR_GRADIENT_R1.json',{'PHASE':PHASE,'gradient_definition':'sum_b abs(w_b(v)-w_b(u))/Basis_rest_edge_length_mm','units':'weight_L1_per_mm','ROI_overall':full_roi,'human_visible_high_strain_band':full_band,'per_active_bone':perbone,'band_definition':'Inherited F130 worst 8 edges; fixed BEFORE this intervention; no reselection','band_edges':[{'edge':list(map(int,e)),'before':float(x),'after':float(y),'pair_fraction_of_baseline_full_vector_L1':float(p)} for e,x,y,p in zip(E,b0.sum(1),b1.sum(1),pair_fraction)],'all_ROI_edges':edges.tolist(),'FULL_VECTOR_FIELD_MODIFIED':'YES' if modified else 'NO','FULL_VECTOR_GRADIENT_MEANINGFULLY_REDUCED':'YES' if reduced else 'NO','meaningful_reduction_rule':'At least 20% reduction in full-vector mean gradient, both original ROI and inherited high-strain band; max/median separately reported, not hidden. This validates the manipulation only, never visual PASS.','weighted_Dirichlet_energy_before_after':[energy0,energy1],'ROI_edge_count':len(edges),'high_strain_band_edge_count':len(E)})
definition={'PHASE':PHASE,'candidate_status':'DESIGN_ONLY','candidate_count':1,'method':'DIRICHLET_HARMONIC_FULL_VECTOR_FIELD','equation':'L_II W_I = -L_IB W_B, simultaneously all active columns','operator':'Undirected mesh-edge graph; positive conductance c_uv=1/Basis_rest_edge_length_m. Same fixed operator for every bone. No cotangent negative coefficients.','ROI_source':'Approved 149-point patch + existing two-ring ROI; exactly inherited 234 nodes / 70 boundary / 164 free. No enlargement.','ROI':roi,'boundary':boundary,'free':free,'all_21_bones':bones,'deform_bones':deform,'ACTIVE_WEIGHT_BONES_IN_ROI':[names[j] for j in active],'zero_contribution_bones_not_added':inactive,'active_selection':'Exactly nonzero baseline ROI contribution; no support threshold, pruning or painting','active_bone_statistics':{names[j]:{'ROI_nonzero_vertices':int(np.count_nonzero(W[roi,j])),'ROI_mean_weight':float(W[roi,j].mean()),'ROI_max_weight':float(W[roi,j].max()),'boundary_nonzero_vertices':int(np.count_nonzero(W[boundary,j]))} for j in active},'baseline_full_21_vector':{str(i):{n:float(W[i,names.index(n)]) if n in names else 0. for n in bones} for i in roi},'candidate_full_21_vector':{str(i):{n:float(WW[i,names.index(n)]) if n in names else 0. for n in bones} for i in roi},'previous_pair_fraction_range':pair_fraction[[np.argmin(pair_fraction),np.argmax(pair_fraction)]].tolist(),'previous_pair_coverage_definition':'WRIST+THUMB absolute component differences / complete endpoint-vector L1, on inherited 8-edge band','constraints':{'minimum_weight':float(WW.min()),'sum_range_all_vertices':[float(WW.sum(1).min()),float(WW.sum(1).max())],'boundary_numerically_exact':True,'outside_ROI_numerically_exact':True,'mesh_topology_basis_rest_bones_modifiers_exact':True,'corrective_and_driver_exact':True,'Action_exact':True,'ZERO_difference_max_mm':zero_delta},'numerics':{'solve_max_absolute_residual':residual,'interior_pre_normalization_sum_range':[float(sum_before.min()),float(sum_before.max())],'normalization':'Interior only division by sum solely for <=2e-7 floating point partition error','normalization_max_weight_delta':float(np.max(abs(solution-solution*sum_before[:,None]))),'clipping':False,'support_thresholding':False,'pruning':False},'baseline_native_no_weights_sha256':digest(native),'baseline_shape_sha256':digest(shape),'action_payload_sha256':APPROVED_ACTION_SHA,'previous_candidates_read_only':authority,'protected_inputs_before':before,'forbidden_layers_used':False}
dump('FULL_VECTOR_FIELD_DEFINITION_R1.json',definition)
for x in [ob,bpy.context.scene]:
    x['DESIGN_ONLY']=True;x['NOT_PRODUCTION']=True;x['HUMAN_APPROVAL_PENDING']=True;x['PHASE']=PHASE;x['PRODUCTION_PROMOTION']='NO'
ob['PRODUCT_BASELINE_STATUS']='DESIGN_ONLY_FULL_VECTOR_STATIC_WEIGHT_CAUSAL_PROBE'
bpy.context.scene['HUMAN_APPROVED']=False;bpy.context.scene['RIGHT_HAND_PRODUCT_BASELINE']='DESIGN_ONLY_NOT_PRODUCTION'
bpy.context.preferences.filepaths.save_version=0
motion(rig,130)
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),compress=False)
verify_inputs(before)
print('FULL_VECTOR_FIELD_BUILT_BEFORE_RENDER',{'active_bones':definition['ACTIVE_WEIGHT_BONES_IN_ROI'],'ROI_mean_reduction_percent':full_roi['mean_reduction_percent'],'band_mean_reduction_percent':full_band['mean_reduction_percent'],'valid_manipulation':reduced,'changed_columns':modified},flush=True)
