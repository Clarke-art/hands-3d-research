import sys
sys.dont_write_bytecode=True
from geometry_gate import *
D=read(OUT/'TEMP_DOWNSTREAM_COORDINATES_R1.json');normal=read(OUT/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');core=read(OUT/'PALMAR_ROOT_DEFECT_CORE_R1.json');results={};ed=np.array(E)
for cid in ['BIND']+D['pose_smoke_cases']:
 baseline=np.array(D['states']['CURRENT'][cid]);candidate=np.array(D['states']['FORMAL_CANDIDATE'][cid]);r=assess(candidate,baseline,IDS);cmp=r['contact_no_regression'];nv=normal['vertex_ids'];outside=sorted(set(range(len(V)))-set(IDS));pd=np.linalg.norm(candidate-baseline,axis=1)
 assert np.array_equal(candidate[nv],baseline[nv]);assert np.array_equal(candidate[outside],baseline[outside])
 # Stretch is measured vs each asset's own BIND; changed source lengths are not mixed with corrected BIND lengths.
 le=lambda a:np.linalg.norm(a[ed[:,1]]-a[ed[:,0]],axis=1)
 oldratio=le(baseline)/le(np.array(D['states']['CURRENT']['BIND']));newratio=le(candidate)/le(np.array(D['states']['FORMAL_CANDIDATE']['BIND']));incident=np.where(np.any(np.isin(ed,IDS),axis=1))[0]
 r.update({'case':cid,'normal_context_candidate_vs_current_coordinate_max_mm':float(pd[nv].max()),'outside16_candidate_vs_current_coordinate_max_mm':float(pd[outside].max()),'neighbor_digit_geometry_contamination_count':int(np.count_nonzero(pd[outside])),'new_true3D_contact_count':len(cmp['new_true_contact_components']),'baseline_contact_worsening_count':len(cmp['worsening_components']),'feature_expansion_count':len(cmp['feature_expansions']),'new_boundary_transition_fold_count':len(r['boundary']['new_boundary_sharp_folds']),'stretch_diagnostics':{'current_incident_edge_ratio_min':float(oldratio[incident].min()),'current_incident_edge_ratio_max':float(oldratio[incident].max()),'candidate_incident_edge_ratio_min':float(newratio[incident].min()),'candidate_incident_edge_ratio_max':float(newratio[incident].max()),'per_edge':[{'edge_id':int(i),'vertex_ids':E[i],'current_ratio_to_own_bind':float(oldratio[i]),'candidate_ratio_to_own_bind':float(newratio[i])} for i in incident],'ratio_not_anatomy_approval_threshold':True},'collapse_exact_zero_area':r['new_degenerate'],'limited_local_smoke_only':True,'full_deformation_qualification':False,'visible_review':'PENDING'})
 results[cid]=r;print('TEMP LOCAL',cid,r['status'],'newcontacts',r['new_true3D_contact_count'],'normalmax',pd[nv].max(),'edge minmax',newratio[incident].min(),newratio[incident].max(),flush=True)
 if r['status']!='PASS':break
status='PASS_STRUCTURAL_PENDING_VISIBLE_REVIEW' if len(results)==1+len(D['pose_smoke_cases']) and all(r['status']=='PASS' for r in results.values()) else 'FAIL_CLOSED_PALMAR_DONOR_RESTORATION_DESIGN'
z=read(OUT/'PALMAR_ROOT_LOCAL_POSE_SMOKE_R1.json');z.update(status=status,states=results,source_AST_provenance=sources);dump('PALMAR_ROOT_LOCAL_POSE_SMOKE_R1.json',z)
