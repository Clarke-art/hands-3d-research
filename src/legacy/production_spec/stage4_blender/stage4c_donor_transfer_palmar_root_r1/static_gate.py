import sys
sys.dont_write_bytecode=True
from geometry_gate import *
assert read(OUT/'PALMAR_APPLICATION_SAVE_REOPEN_AUDIT_R1.json')['SAVE_REOPEN']=='PASS'
r=assess(P,V,IDS);cmp=r['contact_no_regression']
r.update({'source_AST_provenance':sources,'actual_reopened_application':ref(ASSET),'actual_geometry_payload':ref(OUT/'PALMAR_APPLICATION_NATIVE_GEOMETRY_R1.json'),'native_V_E_F':[len(V),len(E),len(F)],'new_true_contact_component_count':len(cmp['new_true_contact_components']),'existing_contact_worsening_count':len(cmp['worsening_components']),'feature_expansion_count':len(cmp['feature_expansions']),'new_boundary_transition_fold_count':len(r['boundary']['new_boundary_sharp_folds']),'manifold_incidence_unchanged':all(len(ff)==2 for ff in EF),'face_reversal_semantics':'Native oriented cycles unchanged; exact endpoint contacts and source-application linear fan-area sanity. No absolute projected normal/bowtie zero. Not full continuous deformation qualification.','fresh_application_gate_run':True,'candidate_PASS_not_used_as_substitute':True,'bind_pose_qualification_runs':0,'promoted':False})
dump('PALMAR_APPLICATION_STRUCTURE_AUDIT_R1.json',r)
dump('PALMAR_APPLICATION_CONTACT_AUDIT_R1.json',{'status':'PASS' if cmp['PASS'] else 'FAIL_CLOSED','baseline_counts':r['baseline_counts'],'application_counts':r['candidate_counts'],'baseline_components':r['baseline_components'],'application_components':r['candidate_components'],'contact_no_regression':cmp,'new_true3D_contact_count':len(cmp['new_true_contact_components']),'baseline_contact_worsening_count':len(cmp['worsening_components']),'feature_expansion_count':len(cmp['feature_expansions']),'scope':'Every16-write incident native fan vs entire current source mesh; exact rational illegal features minus legal shared-simplex; existing contact feature/extent no-regression. Outside incidence exact unchanged.','source_AST_provenance':sources,'fresh_actual_reopened_geometry':True})
adj=[set() for _ in V]
for a,b in E:adj[a].add(b);adj[b].add(a)
w=set(IDS);r1=w|{j for i in w for j in adj[i]};r2=r1|{j for i in r1 for j in adj[i]};wf=face_domain(IDS);rows=[]
for p in read(ROOT/'production_spec/stage6_deformation/current_full_stage6a_crossing_human_adjudication_prep_r1/LOCKED_CURRENT9_ROWS_R1.json')['rows']:
 pv=set(p['vertex_ids']);pf=set(p['face_ids']);rows.append({'pair_id':p['pair_id'],'case_id':p['case_id'],'direct_vertex_overlap':sorted(w&pv),'changed_face_overlap':sorted(wf&pf),'1ring_overlap':sorted(r1&pv),'2ring_overlap':sorted(r2&pv)})
d=sum(bool(x['direct_vertex_overlap'] or x['changed_face_overlap']) for x in rows);one=sum(bool(x['1ring_overlap']) for x in rows);two=sum(bool(x['2ring_overlap']) for x in rows)
expected=read(DESIGN/'PALMAR_ROOT_CURRENT9_INDEPENDENCE_R1.json');assert d==expected['CURRENT9_DIRECT_OVERLAP']==one==expected['CURRENT9_1RING_OVERLAP']==two==expected['CURRENT9_2RING_OVERLAP']==0
dump('PALMAR_APPLICATION_CURRENT9_ID_CONSISTENCY_R1.json',{'status':'PASS','CURRENT9_DIRECT_OVERLAP':d,'CURRENT9_1RING_OVERLAP':one,'CURRENT9_2RING_OVERLAP':two,'rows':rows,'ID_consistency_recheck_only':True,'CURRENT9_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','answers_modified':False,'closure_created':False,'acceptance_expanded':False,'posed_reclassification_runs':0})
print('Fresh application TRUE3D',r['status'],'newcontact',len(cmp['new_true_contact_components']),'boundaryfold',r['new_boundary_transition_fold_count'],'current9 IDs',d,one,two,flush=True)
assert r['status']=='PASS','FAIL_CLOSED_PALMAR_DONOR_RESTORATION_APPLICATION'
