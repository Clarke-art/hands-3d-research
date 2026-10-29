import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
before=protected_inputs()
dump('HUMAN_DECISION_BIND_R1.json',{'authority':'Direct Human request in current chat','LEVEL_1_TOPOLOGY_ROUTE':'CLOSED','FIRST_WEB_HUMAN_VISIBLE_BLOCKER':'OPEN','FALLBACK_STATUS':'PROTECTED_FROZEN_FALLBACK','RIGHT_HAND_DEFORMATION_CLOSED':'NO','LEFT_HAND_START':'NO','WEB_PRODUCT_PROMOTION':'NO','closed_routes':['topology','subdivide','retopo_A2','source_mesh_replacement','DQS','cage','helper','new_corrective','axis_mapping','joint_isolation'],'previous_results_reused_not_rerun':True})
# Read the previous DESIGN_ONLY file as authority, without redoing its experiment.
path=PREV/'RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend'
h.bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
authority_read={'candidate_sha256':sha(path),'objects':[{'name':o.name,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in bpy.data.objects],'action_hash':digest(action_payload(bpy.data.actions[ACTION])),'experiment_rerun':False}
assert authority_read['action_hash']==APPROVED_ACTION_SHA
ob,rig=open_frozen();native=native_no_weights(ob,rig);shape=shape_state(ob);W=weights(ob);names=[g.name for g in ob.vertex_groups];wi=names.index('WRIST_R');ti=names.index('THUMB_CMC_R')
roi,boundary=topology_roi(ob);R0=coords(ob);S=W[:,wi]+W[:,ti];ratio=np.divide(W[:,ti],S,out=np.zeros(len(S)),where=S>1e-9)
attr=read(PREV/'ATTRIBUTION_AND_RECONCILIATION_R1.json');band=next(r for r in attr['frames'] if r['frame']==130)['top_edges'];E=np.array([[r['v_a'],r['v_b']] for r in band]);rep=sorted(set(E.flatten().tolist()));assert all(W[i,wi]>DELTA and W[i,ti]>DELTA for i in rep)
edges=np.array([list(e.vertices) for e in ob.data.edges if all(i in roi for i in e.vertices)]);length0=np.linalg.norm(R0[edges[:,1]]-R0[edges[:,0]],axis=1)
grad=abs(ratio[edges[:,1]]-ratio[edges[:,0]])/(length0*1000)
full_diff=abs(W[E[:,1]]-W[E[:,0]]);band_rows=[]
for k,(a,b) in enumerate(E):
    d=full_diff[k];order=np.argsort(-d)
    band_rows.append({'edge':[int(a),int(b)],'prior_authority':band[k],'ratio_endpoints':[float(ratio[a]),float(ratio[b])],'S_endpoints':[float(S[a]),float(S[b])],'ratio_gradient_per_mm':float(abs(ratio[a]-ratio[b])/(np.linalg.norm(R0[a]-R0[b])*1000)),'full_weight_vector_a':{n:float(w) for n,w in zip(names,W[a])},'full_weight_vector_b':{n:float(w) for n,w in zip(names,W[b])},'L1_component_contributions':{names[j]:float(d[j]) for j in order if d[j]>1e-7},'WRIST_THUMB_pair_fraction_of_full_L1':float((d[wi]+d[ti])/d.sum())})
dump('READ_ONLY_WEIGHT_FIELD_R1.json',{'previous_candidate_read':authority_read,'frozen_sha256':sha(BASE),'group_names':names,'ROI_ids':roi,'boundary_ids':boundary,'original_patch_ids':PATCH_IDS,'representative_vertices':rep,'representative_edges':band_rows,'ROI_full_weight_vectors':[{ 'vertex':i,'weights':W[i].tolist(),'S':float(S[i]),'R':float(ratio[i])} for i in roi],'ratio_gradient_definition':'abs(R_b-R_a)/rest_edge_length_mm; only rest ROI edges, no new strain census','ROI_ratio_gradient_summary':{'mean_per_mm':float(grad.mean()),'max_per_mm':float(grad.max())},'ROI_edges':edges.tolist(),'rest_ROI_coordinates_world':{str(i):R0[i].tolist() for i in roi},'scope':'Full vector read only. Pair perturbations only; secondary influences recorded when directly present in the inherited band.'})
baseline={};perturbed={};response=[];records=[];restoration=[]
def set_pair(ids,sign):
    for i in ids:
        ob.vertex_groups[wi].add([i],float(W[i,wi]-sign*DELTA),'REPLACE');ob.vertex_groups[ti].add([i],float(W[i,ti]+sign*DELTA),'REPLACE')
    bpy.context.view_layer.update()
def restore(ids):
    for i in ids:
        ob.vertex_groups[wi].add([i],float(W[i,wi]),'REPLACE');ob.vertex_groups[ti].add([i],float(W[i,ti]),'REPLACE')
    bpy.context.view_layer.update()
for f in FRAMES:
    motion(rig,f);V=coords(ob);baseline[str(f)]={str(i):V[i].tolist() for i in roi};assert np.isfinite(V).all();records+=render(ob,'BASELINE',f)
    row={'frame':f,'corrective_natural_values':values(ob),'per_vertex':[],'per_edge':[]}
    aggregate={}
    for label,sign in [('WRIST_TO_THUMB',1),('THUMB_TO_WRIST',-1)]:
        set_pair(rep,sign);A=coords(ob);aggregate[label]=A
        ww=weights(ob);other=[i for i in range(len(names)) if i not in [wi,ti]]
        assert np.array_equal(ww[:,other],W[:,other]) and np.max(abs(ww[:,wi]+ww[:,ti]-S))<1e-7
        records+=render(ob,label,f);restore(rep);assert np.array_equal(weights(ob),W)
        assert np.linalg.norm(coords(ob)-V,axis=1).max()<1e-8
    for i in rep:
        set_pair([i],1);plus=coords(ob)[i];restore([i]);set_pair([i],-1);minus=coords(ob)[i];restore([i])
        adj=[int(b if a==i else a) for a,b in E if i in [a,b]]
        axes=np.array([(V[j]-V[i])/np.linalg.norm(V[j]-V[i]) for j in adj]);axis=axes.mean(0);axis/=np.linalg.norm(axis)
        D=(plus-minus)*.5
        closing=float(D@axis)*1000
        row['per_vertex'].append({'vertex':i,'neighbor_endpoints':adj,'plus_displacement_mm':((plus-V[i])*1000).tolist(),'minus_displacement_mm':((minus-V[i])*1000).tolist(),'local_jacobian_world_m_per_unit_weight':((plus-minus)/(2*DELTA)).tolist(),'toward_partner_axis_world':axis.tolist(),'plus_transfer_closing_projection_mm':closing,'preferred_edge_closure_sign':('WRIST_TO_THUMB' if closing>.01 else 'THUMB_TO_WRIST' if closing<-.01 else 'INSENSITIVE'),'note':'Towards endpoint is a response direction proxy, not a verified natural surface target.'})
    for a,b in E:
        d=np.linalg.norm(V[b]-V[a]);row['per_edge'].append({'edge':[int(a),int(b)],'baseline_length_mm':float(d*1000),'WRIST_TO_THUMB_simultaneous_endpoints_length_delta_mm':float((np.linalg.norm(aggregate['WRIST_TO_THUMB'][b]-aggregate['WRIST_TO_THUMB'][a])-d)*1000),'THUMB_TO_WRIST_simultaneous_endpoints_length_delta_mm':float((np.linalg.norm(aggregate['THUMB_TO_WRIST'][b]-aggregate['THUMB_TO_WRIST'][a])-d)*1000)})
    row['max_aggregate_response_mm']={k:float(np.linalg.norm(v-V,axis=1).max()*1000) for k,v in aggregate.items()}
    response.append(row);restoration.append({'frame':f,'positions_restored_mm':float(np.linalg.norm(coords(ob)-V,axis=1).max()*1000)})
neutral(rig);zeroerror=float(np.linalg.norm(coords(ob)-R0,axis=1).max()*1000);assert zeroerror==0
assert native_no_weights(ob,rig)==native and shape_state(ob)==shape and np.array_equal(weights(ob),W)
assert digest(action_payload(bpy.data.actions[ACTION]))==APPROVED_ACTION_SHA
verify_inputs(before)
dump('SENSITIVITY_RESPONSE_R1.json',{'fixed_delta_weight':DELTA,'parameter_sweep':False,'optimization':False,'perturbation_scope':rep,'all_other_weights_exact':True,'pair_S_preserved_max_error_bound':1e-7,'evaluation':'Blender depsgraph evaluated mesh only; no manual LBS reconstruction','frames':response,'restoration':restoration,'ZERO_restore_mm':zeroerror,'ZERO_restore':'PASS','source_action_hash_exact':True,'blend_files_written':0,'input_hashes_unchanged':before,'render_records':records})
dump('BASELINE_SIX_FRAME_COORDINATES_R1.json',{'frames':baseline,'ROI_ids':roi,'ZERO_ROI':{str(i):R0[i].tolist() for i in roi},'native_no_weights_sha256':digest(native),'shape_sha256':digest(shape),'scope':'Only local ROI positions retained; no whole-hand per-vertex audit.'})
print('SENSITIVITY_COMPLETE_ALL_RESTORED',len(rep),'POINTS',len(E),'EDGES',flush=True)
