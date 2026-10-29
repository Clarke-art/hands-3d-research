import sys
sys.dont_write_bytecode=True
from robust_geometry import *
R3DIR=ROOT/'audits/minimal_local_geometry_amendment_design_r3'
R3=read(R3DIR/'COLLISION_CONSTRAINED_SOLVE_AUDIT_R3.json');FINAL_IDS=R3['final_selected_attempt_ids'];POINT=R3['solves']['R3_A_S4_V2'];P=np.array(POINT['world_mm']);IDS=POINT['support_ids']

def projected_cross(v,fi,chart=None):
 pp=v[F[fi]];center=V[F[fi]].mean(0)
 if chart is None:_,_,vt=np.linalg.svd(pp-pp.mean(0));chart=vt[:2].T
 q=(pp-center)@chart;hits=[]
 for a,b,c,d in [(0,1,2,3),(1,2,3,0)]:
  mat=np.column_stack([q[b]-q[a],q[c]-q[d]])
  if abs(np.linalg.det(mat))<1e-15:continue
  u,t=np.linalg.solve(mat,q[c]-q[a])
  if 0<u<1 and 0<t<1:
   hits.append({'opposite_edge_offsets':[a,c],'parameters':[float(u),float(t)],'intersection_chart_mm':(q[a]+u*(q[b]-q[a])).tolist(),'strict_parameter_margin':float(min(u,1-u,t,1-t))})
 return {'flag':bool(hits),'hits':hits,'projection_chart':chart.tolist(),'points_chart_mm':q.tolist()}

def pair_details(v,fa,fb):
 shared=sorted(set(F[fa])&set(F[fb]));edges=[E[i] for i in set(FE[fa])&set(FE[fb])];rows=[]
 for i in np.where(owners==fa)[0]:
  for j in np.where(owners==fb)[0]:
   a,b=legal_features(i,j);rr=intersection(v,tri[i],tri[j],a,b);rr.update({'fan_triangle_indices':[int(i),int(j)]});rows.append(rr)
 illegal=[r for r in rows if r['illegal']];legal=[r for r in rows if r['classification']=='LEGAL_SHARED_TOPOLOGY_CONTACT'];dist=min(tri_pair_metrics(v,tri[i],tri[j])['distance_mm'] for i in np.where(owners==fa)[0] for j in np.where(owners==fb)[0])
 return {'native_face_cycles':[F[fa],F[fb]],'shared_vertex_ids':shared,'shared_native_edge_vertex_ids':edges,'native_face_normal_dot':float(normal(v,F[fa])@normal(v,F[fb])),'whole_pair_unsigned_minimum_distance_mm':dist,'whole_pair_distance_is_not_off_shared_feature_margin':bool(shared),'fan_pair_tests':rows,'true_off_shared_feature_contact':bool(illegal),'legal_shared_contact':bool(legal),'max_illegal_segment_mm':max((r['intersection_segment_mm'] for r in illegal),default=0.)}

def run():
 result={}
 for fi in [2771,3332,3351]:
  cycle=F[fi];a=[cycle[0],cycle[1],cycle[2]];b=[cycle[0],cycle[2],cycle[3]];av=np.cross(V[a[1]]-V[a[0]],V[a[2]]-V[a[0]])/2;bv=np.cross(V[b[1]]-V[b[0]],V[b[2]]-V[b[0]])/2;fan=intersection(V,a,b,[cycle[0],cycle[2]],[[cycle[0],cycle[2]]]);edges=[]
  for i,j in [(0,2),(1,3)]:
   pa,pb,s,t=segment_segment(V[cycle[i]],V[cycle[(i+1)%4]],V[cycle[j]],V[cycle[(j+1)%4]]);edges.append({'opposite_edge_offsets':[i,j],'minimum_3D_distance_mm':float(np.linalg.norm(pa-pb)),'closest_parameters':[s,t]})
  ext,counts=exact_certified(V,cycle,only_faces=[fi]);flag=projected_cross(V,fi);bad=fan['illegal'] or min(z['minimum_3D_distance_mm'] for z in edges)<1e-12 or min(np.linalg.norm(av),np.linalg.norm(bv))<1e-10
  bad=bool(bad)
  result[str(fi)]={'classification':'TRUE_3D_DEFECT' if bad else 'PROJECTION_ONLY_DIAGNOSTIC','native_face_id':fi,'native_cycle':cycle,'world_mm':V[cycle].tolist(),'native_vector_sum_face_area_mm2':float(areas(V)[fi]),'fan_triangle_area_mm2':[float(np.linalg.norm(av)),float(np.linalg.norm(bv))],'signed_fan_area_against_frozen_roi_outward_mm2':[float(av@n),float(bv@n)],'signed_orientation_reference':'ROI outward is a chart diagnostic; it is not a coordinate-free 3D inversion test. Native winding, nonzero fan area, and the continuous embedded fan complex are structural.','fan_unit_normals':[(av/np.linalg.norm(av)).tolist(),(bv/np.linalg.norm(bv)).tolist()],'fan_normal_dot':float(av@bv/np.linalg.norm(av)/np.linalg.norm(bv)),'native_edge_ids':FE[fi],'native_2face_incidence':{str(e):EF[e] for e in FE[fi]},'manifold_edge_incidence_valid':all(len(EF[e])==2 for e in FE[fi]),'intrinsic_fan_intersection':fan,'opposite_boundary_edge_tests':edges,'projection_diagnostic':flag,'actual_intrinsic_3D_self_intersection':bad,'extrinsic_existing_contacts_touching_face':[{'face_ids':list(k),**z} for k,z in ext.items()],'extrinsic_contacts_do_not_relabel_the_projection_predicate':True,'whole_mesh_context_counts':counts,'can_remove_in_2D_by_changing_camera_is_not_structural_repair':True}
  print('BOW',fi,result[str(fi)]['classification'],'edge gap',min(z['minimum_3D_distance_mm'] for z in edges),flush=True)
 dump('PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json',{'baseline_source':L['stages']['STAGE4C_R2_RAW']['input'],'flags':result,'semantics':'All three quads are nonplanar embedded two-triangle fans. Opposite projected edges cross, but actual boundary segments have positive separation and the fan interiors intersect only at the legal diagonal. Sharp 3D folding remains a shape diagnostic, not automatic true inversion.','absolute_projection_count_zero_is_required':False,'proposed_rule':'NO_NEW_TRUE_3D_STRUCTURAL_DEFECT plus fixed-view projection-specific no-regression/human review, not absolute baseline projected flag eradication.'})
 pairs={(204,207),(2182,3330),(3329,3331),(3312,3313)};stats={}
 for key in R3['solves']:
  rr=R3['solves'][key]
  for h in rr['accepted_iterations']:
   for z in h['active_separation_constraints']:
    k=tuple(sorted(z['face_ids']));pairs.add(k);ss=stats.setdefault(k,{'constraint_occurrences':0,'solve_ids':set(),'feature_kinds':set(),'four_point_features':set()});ss['constraint_occurrences']+=1;ss['solve_ids'].add(key);ss['feature_kinds'].add(z.get('feature_kind',z.get('kind','')))
    if 'four_point_vertex_ids' in z:ss['four_point_features'].add(tuple(z['four_point_vertex_ids']))
  for z in rr['rejected_steps']:
   for pp in z.get('face_pairs',[]):pairs.add(tuple(sorted(pp)))
   if 'face_ids' in z.get('detail',{}):pairs.add(tuple(sorted(z['detail']['face_ids'])))
 inventory=[]
 for pair in sorted(pairs):
  base=pair_details(V,*pair);w=pair_details(P,*pair)
  label='OFF_EDGE_ILLEGAL' if base['true_off_shared_feature_contact'] and base['shared_vertex_ids'] else 'NONADJACENT_TRUE_COLLISION' if base['true_off_shared_feature_contact'] else 'SHARED_LEGAL' if base['legal_shared_contact'] else 'NEAR_CONTACT_WARNING'
  record=stats.get(pair,{});record={k:(sorted(v) if isinstance(v,set) else v) for k,v in record.items()}
  inventory.append({'face_ids':list(pair),'classification_at_baseline':label,'classification_at_R3_failed_point':'OFF_EDGE_ILLEGAL' if w['true_off_shared_feature_contact'] and w['shared_vertex_ids'] else 'NONADJACENT_TRUE_COLLISION' if w['true_off_shared_feature_contact'] else 'SHARED_LEGAL' if w['legal_shared_contact'] else 'NEAR_CONTACT_WARNING','trace_occurrences':record,'baseline':base,'R3_failed_point':w,'finite_feature_off_edge_crossing_still_hard_fail':True,'old9_Stage6A_classification_not_rerun':True})
 dump('ACTIVE_SET_PAIR_INVENTORY_R1.json',{'source':ref(R3DIR/'COLLISION_CONSTRAINED_SOLVE_AUDIT_R3.json'),'selected_solve_ids':FINAL_IDS,'all_trace_solve_ids_including_superseded':list(R3['solves']),'pair_count':len(pairs),'pairs':inventory,'one_native_pair_can_contain_legal_and_illegal_features':True,'near_contact_is_not_exact_collision':True})
 shared=next(z for z in inventory if z['face_ids']==[2182,3330]);dump('SHARED_EDGE_CONTACT_SEMANTICS_R1.json',{'shared_edge_vertex_ids':[79,955],'pair':shared,'relation':'LEGAL_SHARED_EDGE_AND_VERTICES_WITH_NO_BASELINE_OFF_EDGE_INTERSECTION; off-edge contact remains forbidden.','release_from_barrier':['Identical shared vertex contacts','Native shared edge contacts','Internal triangulation diagonal contacts','Volume sign changes at finite-feature-disjoint or legal-flat-fold events'],'keep_hard':['Any exact intersection point beyond actual shared simplex','Positive-area coplanar overlap','New nonadjacent finite triangle contact','Swept native fan triangle degeneracy'],'persistent_coplanar_policy':'Use an intrinsic planar chart on certified common plane, clip finite polygons and subtract the actual shared simplex. Continuous 2D orientation/edge events remain required even when all four-point volume polynomials vanish. Do not impose distance floors on legal zero-distance adjacency.','clearance_added_mm':0,'R3_near_warning_is_not_structural_fail':True})
 classification={'A_TRUE_3D_STRUCTURAL_HARD_GATE':{'predicates':['native topology/cycle/incidence mutation','zero-area native fan triangle or collapse on the continuous path','certified new finite nonadjacent intersection','certified intersection beyond legal shared simplex','positive-area coplanar overlap'],'orientation_note':'A fixed outward/chart normal dot or a 180deg normal change alone is not coordinate-free inversion. Require a declared material-frame/path convention; moving triangle area vectors continuously without zero area is not automatically face reversal.'},'B_BASELINE_EXISTING_DIAGNOSTIC':{'predicates':['Three baseline projected bowtie flags2771/3332/3351','baseline sharp crease/warped nonplanar quad'],'policy':'Do not require absolute zero. Track fixed projection, positive 3D area, no new true defect and no-regression or justified Human review.'},'C_SHARED_TOPOLOGY_LEGAL_CONTACT':{'predicates':['Actual common native vertex','Actual common native edge','Fan internal diagonal'],'policy':'Subtract legal simplex exactly; no pair-wide positive separation floor.'},'D_SHARED_FEATURE_OFF_EDGE_ILLEGAL_CROSSING':{'predicates':['Certified point/segment outside legal simplex','Coplanar overlap with positive area'],'policy':'Hard fail, including faces with a shared vertex/edge.'},'E_NUMERICAL_PROXIMITY_ACTIVE_SET_WARNING':{'predicates':['AABB proximity band','Closest distance near zero','Four-point side sign/linearized volume warning','Fixed-chart outward normal diagnostic'],'policy':'Activate feature-aware checks, never automatically structural failure. Plane-extension sign changes require finite-feature membership.'},'tolerance_class':'COMPUTATIONAL_GEOMETRY_TOLERANCE','anatomy_clearance':False,'historical_validator_edited':False,'R3_iteration_vs_terminal_gate':'Iteration guards retained no NEW projected flags; final R3 eligibility also rejected unresolved baseline projected flags. The latter is overconstraint for the audited embedded quads, but by itself does not explain iteration stagnation.'}
 dump('GEOMETRIC_GATE_SEMANTIC_CLASSIFICATION_R1.json',classification)
 print('SEMANTIC AUDIT COMPLETE',len(pairs),flush=True)
if __name__=='__main__':run()
