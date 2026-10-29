import sys
sys.dont_write_bytecode=True
from search_anchored import *
matrix=read(OUT/'SUPPORT_DEPTH_FEASIBILITY_MATRIX_R2.json');sols=read(OUT/'FEASIBLE_SOLVES_R2.json');first=sols['first']
cs={}
for dep,c in sorted(sols['solutions'].items(),key=lambda item:int(item[0])):
 if first is not None and int(dep) in [first,first+1]:cs['R2_'+chr(65+len(cs))]=c
def disp(v,ids):
 ids=sorted(ids);d=v-V;ds=np.linalg.norm(d,axis=1);moved=[i for i in ids if ds[i]>1e-7];ba=boundary_audit(v,moved)
 return {'DESIGN_ONLY_NOT_APPLICATION_AUTHORITY':True,'support_pool_vertex_count':len(ids),'actual_moved_vertex_ids':moved,'actual_write_vertex_count':len(moved),'approx_zero_omitted_vertex_ids':sorted(set(ids)-set(moved)),'approx_zero_numeric_tolerance_mm':1e-7,'max_displacement_mm':float(ds.max()),'mean_displacement_mm':float(ds[moved].mean()) if moved else 0.,'RMS_displacement_mm':float(np.sqrt(np.mean(ds[moved]**2))) if moved else 0.,'percentile95_displacement_mm':float(np.percentile(ds[moved],95)) if moved else 0.,'max_boundary_displacement_mm':ba['boundary_displacement_max_mm'],'max_boundary_displacement_gradient':ba['max_boundary_displacement_gradient'],'outside_support_displacement_mm':float(max(ds[i] for i in range(len(V)) if i not in ids)),'vertices':{str(i):{'baseline_world_mm':V[i].tolist(),'candidate_world_mm':v[i].tolist(),'delta_world_mm':d[i].tolist(),'delta_magnitude_mm':float(ds[i])} for i in ids}}
cmp={};bound={};states={'CURRENT':{'RSSF_RAW':V.tolist()},'R1C_FAILED_REFERENCE':{'RSSF_RAW':prior.tolist()}}
for label,c in cs.items():
 c['DESIGN_ONLY_NOT_PRODUCTION']=True;c['Human_selected']=False;c['write_vertices']=[i for i in c['support_pool_vertex_ids'] if np.linalg.norm(np.array(c['world_mm'][i])-V[i])>1e-7]
 cmp[label]=disp(np.array(c['world_mm']),c['support_pool_vertex_ids']);bound[label]=boundary_audit(np.array(c['world_mm']),c['write_vertices']);states[label]={'RSSF_RAW':c['world_mm']}
failed=read(OUT/'FAILED_SOLVE_WITNESSES_R2.json')['best_failed_or_feasible_per_depth'];failed_evidence={}
if not cs and (OUT/'CORE_HINGE_CONSTRAINT_TRACE_R2.json').exists():
 trace=read(OUT/'CORE_HINGE_CONSTRAINT_TRACE_R2.json')
 for dep in range(1,6):
  trials=[a for a in matrix['attempts'] if a['support_depth']==dep and a['attempt_id'].startswith('CORE_HINGE')]
  if trials:
   a=min(trials,key=lambda z:(len(z['failures']),len((z.get('contact') or {}).get('introduced_pairs',[])),len(z['new_quad_bowtie_face_ids'])+len(z['new_reversal_face_ids'])+len(z['new_boundary_sharp_fold_edge_ids']),z['max_displacement_mm']))
   z=trace[a['attempt_id']];failed[str(dep)]={'attempt':a,'world_mm':z['world_mm'],'full_structural_audit':z['full_audit']}
for dep,z in failed.items():
 v=np.array(z['world_mm']);pool=sorted(sets[int(dep)]);ba=boundary_audit(v,pool)
 es=sorted({ei for fi in face_domain(pool) for ei in FE[fi]});a=angles(v);rows=[{'edge_id':ei,'face_ids':EF[ei],'baseline_dihedral_deg':float(baseA[ei]),'trial_dihedral_deg':float(a[ei]),'delta_deg':float(a[ei]-baseA[ei])} for ei in es if a[ei]-baseA[ei]>20]
 failed_evidence[dep]={'attempt':z['attempt'],'full_structure':z['full_structural_audit'],'boundary_audit':ba,'all_incident_high_change_edges':rows,'displacements':disp(v,pool),'contact_gate':'NOT_RUN_AFTER_EARLIER_STRUCTURAL_REJECTION' if z['attempt']['contact'] is None else z['attempt']['contact'],'not_a_Human_candidate':True}
if not cs:
 dep=max(map(int,failed));states[f'FAILED_SOLVE_S{dep}']={'RSSF_RAW':failed[str(dep)]['world_mm']}
failure_edge=next((ei for z in reversed(list(failed.values())) for ei in z['attempt']['new_internal_obtuse_edge_ids']),6675)
comparison_pool=sets[min(5,first+1 if first else 5)]
dump('R2_GEOMETRY_AMENDMENT_CANDIDATES.json',{'status':'DESIGN_ONLY_NOT_PRODUCTION','source_layer':'FROZEN_STAGE4C_R2_NEW_POSITION_ONLY_DERIVED_COORDINATE_COPIES','source':L['stages']['STAGE4C_R2_RAW']['input'],'candidate_count':len(cs),'candidates':cs,'Human_selection_pending':bool(cs),'production_blend_save_count':0,'topology_change':False})
dump('R2_CANDIDATE_WRITE_SET_COMPARISON.json',{'status':'DESIGN_COMPARISON_NOT_WRITE_AUTHORITY','candidates':cmp,'recommended_candidate':'PENDING_FINAL_GATES' if cs else 'NONE','actual_write_authority_established':False,'failed_solve_evidence_file':'R2_FAILED_SOLVE_WRITE_SET_EVIDENCE.json'})
dump('R2_FAILED_SOLVE_WRITE_SET_EVIDENCE.json',{'not_selectable_candidates':True,'support_depth_witnesses':failed_evidence})
dump('R2_BOUNDARY_CONTINUITY_AUDIT.json',{'candidate_audits':bound,'failed_support_depth_audits':{k:{'attempt_id':z['attempt']['attempt_id'],'boundary_audit':z['boundary_audit'],'all_incident_high_change_edges':z['all_incident_high_change_edges']} for k,z in failed_evidence.items()},'R1C_comparison':boundary_audit(prior,read(R1/'GEOMETRY_AMENDMENT_CANDIDATES_R1.json')['candidates']['C']['write_vertices']),'native_boundary_and_fixed_fixed_ring_complete':True,'metric_screen_is_anatomical_authority':False,'new_internal_hinge_is_also_rejection':True})
dump('REVIEW_COORDINATES_R2.json',{'states':states,'comparison_edge_ids':sorted({ei for fi in face_domain(comparison_pool) for ei in FE[fi]}),'failure_edge_id':failure_edge,'failed_trial_is_not_candidate':not bool(cs),'bind_poses_not_qualified':'Only structurally feasible candidates receive diagnostic downstream evaluations.'})
if not cs:dump('R2_BIND_SMOKE_PREVIEW.json',{'status':'NOT_RUN_NO_STRUCTURALLY_FEASIBLE_CANDIDATE','candidates':{},'BIND':'NOT_RUN','IDX_MCP_15':'NOT_RUN','IDX_MCP_30':'NOT_RUN','IDX_MCP_45':'NOT_RUN','Full42_executed':False,'production_saves':0,'reason':'All support depths rejected before downstream preview; failed position solves are diagnostic evidence only.'})
# Preserve all additional full-guide experiments as rejected diagnostic evidence.
extra=[]
for dep in range(1,6):
 for strength in ([3.] if dep==1 else [3.,30.,300.,3000.]):
  v,method=anchored(dep,.001,.03,strength,full_guide=True);st,fail=initial_gate(v,sorted(sets[dep]));assert fail
  extra.append({'support_depth':dep,'method':method,'failures':fail,'edge6675_deg':st['edge6675_deg'],'edge6602_deg':st['edge6602_deg'],'edge6676_deg':st['edge6676_deg'],'new_quad_bowtie_face_ids':st['new_quad_bowties'],'new_internal_hinge_edge_ids':st['all_incident_new_obtuse_edges'],'new_boundary_sharp_fold_edge_ids':[r['edge_id'] for r in st['new_boundary_sharp_folds']]})
dump('R1_GUIDE_PROPAGATION_DIAGNOSTIC_R2.json',{'status':'ALL_REJECTED_DESIGN_PROBES','attempts':extra,'not_Human_candidates':True,'guide_is_not_anatomy_authority':True})
print('PREPARED',len(cs),'candidates','first',first,'reviewlabels',list(states))
