import sys
sys.dont_write_bytecode=True
from local_analysis import *
from fractions import Fraction as Fr
reuse(R3DIR/'solve.py',['orientation'],globals())

def shared_geometry(v):
 e=v[955]-v[79];u=v[3025]-v[79];w=v[3340]-v[79];ep=e/np.linalg.norm(e);ur=u-ep*(u@ep);wr=w-ep*(w@ep)
 return {'corner_vertex_ids':[3025,3340],'common_edge_vertex_ids':[79,955],'same_side_ray_cosine':float(ur@wr/np.linalg.norm(ur)/np.linalg.norm(wr)),'corner3025_distance_to_edge_mm':float(np.linalg.norm(ur)),'corner3340_distance_to_edge_mm':float(np.linalg.norm(wr)),'preserved_signed_corner_to_opposite_triangle_plane_height_mm':-signed_volume(v,[79,3025,955,3340])/np.linalg.norm(np.cross(u,e)),'height_is_feature_side_margin_not_whole_pair_clearance':True,'coplanar_limit_of_current_fold':'SAME_SIDE_POSITIVE_AREA_OVERLAP_HARD_FAIL','interpretation':'Current common edge is legal. However, the two corner rays are on nearly the same side: flattening this particular fold through zero signed volume causes genuine off-edge overlap. Its feature-aware barrier must remain active; it is not disproved by natural zero distance on the common edge.'}

def run():
 data=read(OUT/'LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json');validation={};audit=[];shared=read(OUT/'SHARED_EDGE_CONTACT_SEMANTICS_R1.json');shared['finite_shared_edge_fold_limit']={}
 for label,v in [('FROZEN_BASELINE',V),('R3_BEST_FAILED_POINT',P)]:
  shared['finite_shared_edge_fold_limit'][label]=shared_geometry(v);glist,meta=derivatives(v);valid=[]
  for rec in data['points'][label]['directions']:
   df=np.zeros_like(V);df[IDS]=np.array(rec['normalized_direction_vectors_world']);h=1e-5;plus=objective(v+h*df);minus=objective(v-h*df);finite=[(plus[k]-minus[k])/(2*h) for k in ['dent_depth_mm','edge6676_angle_deg','reference_surrounding_continuity_loss_mm2']];analytic=[float(g@df[IDS].ravel()) for g in glist];error=[abs(a-b)/max(abs(a),1e-5) for a,b in zip(analytic,finite)]
   side=(shared_geometry(v+h*df)['preserved_signed_corner_to_opposite_triangle_plane_height_mm']-shared_geometry(v-h*df)['preserved_signed_corner_to_opposite_triangle_plane_height_mm'])/(2*h)
   rec['derivatives']['shared_edge_2182_3330_off_edge_finite_feature_side_height_derivative_mm_per_mm_peak']=side
   rec['derivatives']['shared_edge_2182_3330_side_height_note']='Applicable geometric side margin for the nearly SAME-side shared-edge fold. Zero leads to off-edge positive-area overlap, not legal opposite-side coplanarity. Common-edge distance remains zero and receives no gap floor.'
   if rec['direction_name']=='JOINT_METRIC_GRADIENT':
    tv=np.array(POINT['target_world_mm']);rec['derivatives']['R3_A_S4_V2_actual_soft_target_MSE_derivative_mm2_per_mm_peak']=float(2*np.mean((v[IDS]-tv[IDS])*df[IDS]))
   for step in rec['micro_steps']:
    dv=step['step_max_mm']*df
    ori=[orientation(v+t*dv,IDS) for t in [.25,.5,.75,1.]]
    orientpass=all(not any(z[key] for key in ['new_reversed_faces','new_degenerate_faces','new_bowtie_faces']) for z in ori)
    st=structure(v+dv,IDS);an=angles(v+dv);newobtuse=[int(ei) for ei in {ei for fi in face_domain(IDS) for ei in FE[fi]} if baseA[ei]<90 and an[ei]>=90]
    step['faithful_R3_orientation_checkpoints']=ori;step['R3_final_differential_geometry_flags']={key:st[key] for key in ['new_quad_bowties','new_reference_reversed_faces','new_previously_outward_normal_reversals','new_degenerate_faces','new_boundary_sharp_folds']};step['new_internal_obtuse_edges']=newobtuse
    step['CURRENT_R3_ITERATION_GATE_PASS']=step['CURRENT_R3_ITERATION_GATE_PASS'] and orientpass
    step['R3_final_differential_geometry_gate_pass']=not any(step['R3_final_differential_geometry_flags'].values()) and not newobtuse
   valid.append({'direction_name':rec['direction_name'],'analytic_derivatives':analytic,'central_difference_derivatives':finite,'relative_errors':error,'central_difference_mm':h});audit.append(rec)
  validation[label]={'derivative_checks':valid,'max_relative_error':max(e for z in valid for e in z['relative_errors'])}
 dump('LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json',data);dump('NORMAL_TANGENT_COUPLED_DIRECTION_AUDIT_R1.json',{'directions':audit,'combined_directions_are_mathematical_vectors_only':True,'coordinate_repairs_saved':False,'candidate_count':0});dump('SHARED_EDGE_CONTACT_SEMANTICS_R1.json',shared);dump('OBJECTIVE_JACOBIAN_VALIDATION_R1.json',validation)
 # Exact actual-feature fold controls. Coordinates are only local test
 # features, never a mesh state or repair candidate.
 controls=read(OUT/'GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json');controls['controls']=[z for z in controls['controls'] if not z['name'].startswith('ACTUAL2182_3330_')]
 pts={i:fq(P[i]) for i in [79,955,3025,3340]};e=sub(pts[955],pts[79]);u=sub(pts[3025],pts[79])
 for name,sign,illegal in [('ACTUAL2182_3330_SAME_SIDE_COPLANAR_LIMIT',1,True),('ACTUAL2182_3330_OPPOSITE_SIDE_LEGAL_FLAT_UNFOLD',-1,False)]:
  cache=dict(pts);cache[3340]=add(pts[79],add(mul(e,Fr(1,3)),mul(u,Fr(sign,3))));rr=intersection(P,[3025,955,79],[79,955,3340],[79,955],[[79,955]],cache)
  controls['controls'].append({'name':name,'expected':'HARD_FAIL' if illegal else 'LEGAL','actual':rr,'exact_feature_probe_definition':'3340 = 79 + (955-79)/3 '+('+' if sign>0 else '-')+' (3025-79)/3; exact rational local triangle probe only.','passed':rr['illegal']==illegal})
 controls['TRUE_3D_NEGATIVE_CONTROLS_PASS']=all(z['passed'] for z in controls['controls']);controls['status']='PASS' if controls['TRUE_3D_NEGATIVE_CONTROLS_PASS'] else 'FAIL';assert controls['TRUE_3D_NEGATIVE_CONTROLS_PASS'];dump('GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json',controls)
 print('VALIDATION', {k:z['max_relative_error'] for k,z in validation.items()},'CONTROLS',len(controls['controls']),flush=True)
if __name__=='__main__':run()
