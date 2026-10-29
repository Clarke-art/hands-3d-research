import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
gate=read(OUT/'SENSITIVITY_GATE_R1.json');assert gate['weight_field_probe_allowed'] and gate['clear_visible_static_conflict'] is False
assert not CANDIDATE.exists(),'ONE candidate only: refuse overwrite'
before=protected_inputs();ob,rig=open_frozen();native=native_no_weights(ob,rig);shape=shape_state(ob);W=weights(ob);ZERO=coords(ob)
roi,boundary=topology_roi(ob);wi=ob.vertex_groups['WRIST_R'].index;ti=ob.vertex_groups['THUMB_CMC_R'].index;S=W[:,wi]+W[:,ti];R=np.divide(W[:,ti],S,out=np.zeros(len(S)),where=S>1e-9)
edges=np.array([list(e.vertices) for e in ob.data.edges if all(i in roi for i in e.vertices)]);length=np.linalg.norm(ZERO[edges[:,1]]-ZERO[edges[:,0]],axis=1)
assert np.all(length>1e-9)
fixed=set(boundary)|{i for i in roi if S[i]<=1e-9};free=sorted(set(roi)-fixed);slot={v:i for i,v in enumerate(free)}
# ONE fixed definition: rest-edge inverse-length graph harmonic Dirichlet interpolation.
# No smoothing strength, regularization parameter, frame fitting, or optimization search.
L=np.zeros((len(free),len(free)));b=np.zeros(len(free))
for (a,c),ell in zip(edges,length):
    weight=1./ell
    for i,j in [(a,c),(c,a)]:
        if i not in slot:continue
        k=slot[i];L[k,k]+=weight
        if j in slot:L[k,slot[j]]-=weight
        else:b[k]+=weight*R[j]
newR=R.copy();newR[free]=np.linalg.solve(L,b)
assert np.min(newR[roi])>=-1e-9 and np.max(newR[roi])<=1+1e-9
newR=np.clip(newR,0,1)
for i in free:
    ob.vertex_groups[wi].add([i],float(S[i]*(1-newR[i])),'REPLACE');ob.vertex_groups[ti].add([i],float(S[i]*newR[i]),'REPLACE')
bpy.context.view_layer.update();WW=weights(ob);other=[i for i in range(len(ob.vertex_groups)) if i not in [wi,ti]];outside=sorted(set(range(len(W)))-set(free))
assert np.array_equal(WW[:,other],W[:,other]) and np.array_equal(WW[outside],W[outside])
Serror=float(np.max(abs(WW[:,wi]+WW[:,ti]-S)));assert Serror<1e-7 and WW.min()>=0
assert native_no_weights(ob,rig)==native and shape_state(ob)==shape
Znew=coords(ob);zeroerror=float(np.linalg.norm(Znew-ZERO,axis=1).max()*1000);assert zeroerror<.001
for x in [ob,bpy.context.scene]:x['DESIGN_ONLY']=True;x['NOT_PRODUCTION']=True;x['HUMAN_APPROVAL_PENDING']=True;x['PHASE']=PHASE;x['PRODUCTION_PROMOTION']='NO'
ob['PRODUCT_BASELINE_STATUS']='DESIGN_ONLY_STATIC_WEIGHT_FIELD_CAUSAL_PROBE'
bpy.context.scene['HUMAN_APPROVED']=False;bpy.context.scene['RIGHT_HAND_PRODUCT_BASELINE']='DESIGN_ONLY_NOT_PRODUCTION'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),compress=False)
# Clean reopen ensures a valid saved field; renders use Blender's actual evaluated skin.
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE),load_ui=False,use_scripts=False);ob=bpy.data.objects[m.MESH_NAME];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];neutral(rig)
assert native_no_weights(ob,rig)==native and shape_state(ob)==shape and np.array_equal(weights(ob),WW)
assert digest(action_payload(bpy.data.actions[ACTION]))==APPROVED_ACTION_SHA
zero_candidate=coords(ob);records=[];rows=[]
baseline=read(OUT/'BASELINE_SIX_FRAME_COORDINATES_R1.json')['frames']
for f in FRAMES:
    motion(rig,f);V=coords(ob);assert np.isfinite(V).all()
    rows.append({'frame':f,'corrective_natural_values':values(ob),'surface_difference_max_mm':float(max(np.linalg.norm(V[i]-np.array(baseline[str(f)][str(i)])) for i in roi)*1000),'surface_difference_representative_points_mm':{str(i):((V[i]-np.array(baseline[str(f)][str(i)]))*1000).tolist() for i in read(OUT/'READ_ONLY_WEIGHT_FIELD_R1.json')['representative_vertices']},'surface_difference_scope':'Local ROI only'})
    records+=render(ob,'WEIGHT_FIELD_PROBE',f)
neutral(rig);restore=float(np.linalg.norm(coords(ob)-zero_candidate,axis=1).max()*1000);assert restore==0
actualR=np.divide(WW[:,ti],WW[:,wi]+WW[:,ti],out=np.zeros(len(W)),where=S>1e-9)
oldgrad=abs(R[edges[:,1]]-R[edges[:,0]])/(length*1000);newgrad=abs(actualR[edges[:,1]]-actualR[edges[:,0]])/(length*1000)
E=np.array([r['edge'] for r in read(OUT/'READ_ONLY_WEIGHT_FIELD_R1.json')['representative_edges']]);el=np.linalg.norm(ZERO[E[:,1]]-ZERO[E[:,0]],axis=1)*1000
dump('WEIGHT_FIELD_PROBE_VERIFICATION_R1.json',{'candidate':{'path':CANDIDATE.relative_to(ROOT).as_posix(),'sha256':sha(CANDIDATE)},'candidate_count':1,'method':'Unique harmonic R field on SAME 234-node ROI, inverse rest-edge-length graph conductance, original 70 boundary values pinned. No strength parameter/sweep, no painting, no frame fitting.','ROI':roi,'pinned_boundary':boundary,'free_nodes':free,'negative_weights':0,'S_preservation_max_abs_error':Serror,'all_other_influences_exact':True,'outside_and_boundary_weights_exact':True,'normalized_sum_range':[float(WW.sum(1).min()),float(WW.sum(1).max())],'mesh_topology_basis_rest_rig_corrective_driver_exact':True,'source_action_payload_exact':True,'ZERO_existing_positions_max_difference_mm':zeroerror,'ZERO_restore':'PASS','ZERO_restore_max_mm':restore,'ROI_ratio_gradient_before':{'mean_per_mm':float(oldgrad.mean()),'max_per_mm':float(oldgrad.max())},'ROI_ratio_gradient_after':{'mean_per_mm':float(newgrad.mean()),'max_per_mm':float(newgrad.max())},'representative_band_gradient':[{'edge':[int(a),int(c)],'before_per_mm':float(abs(R[a]-R[c])/ll),'after_per_mm':float(abs(actualR[a]-actualR[c])/ll)} for (a,c),ll in zip(E,el)],'full_weight_vector_L1_band_before_after':[{'edge':[int(a),int(c)],'before':float(abs(W[a]-W[c]).sum()),'after':float(abs(WW[a]-WW[c]).sum())} for a,c in E],'ROI_ratios_before_after':[{'vertex':i,'before':float(R[i]),'after':float(actualR[i])} for i in roi],'rows':rows,'render_records':records,'inputs_unchanged':before,'forbidden_deformation_layers_used':False})
verify_inputs(before);print('ONE_HARMONIC_FIELD_PROBE_COMPLETE',len(free),'FREE',Serror,flush=True)
