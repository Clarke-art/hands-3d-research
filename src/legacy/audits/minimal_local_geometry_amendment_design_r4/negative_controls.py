import sys
sys.dont_write_bytecode=True
from semantic_audit import *
from persistent_coplanar import *

def run():
 controls=[];pos=[]
 def add_control(name,v,aa,bb,lv=(),le=(),should_block=True):
  rr=intersection(np.array(v,dtype=float),aa,bb,lv,le);controls.append({'name':name,'expected':'HARD_FAIL' if should_block else 'LEGAL','actual':rr,'passed':rr['illegal']==should_block,'synthetic_feature_coordinates_mm':v})
 add_control('TRUE_3D_COPLANAR_BOWTIE_QUAD',[[0,0,0],[1,1,0],[0,1,0],[1,0,0]],[0,1,2],[0,2,3],[0,2],[[0,2]])
 add_control('SHARED_EDGE_OFF_EDGE_OVERLAP',[[0,0,0],[1,0,0],[.5,1,0],[.5,.5,0]],[0,1,2],[1,0,3],[0,1],[[0,1]])
 add_control('TRUE_3D_NONADJACENT_SEGMENT_CROSSING',[[0,0,0],[1,0,0],[0,1,0],[.2,.2,-1],[.2,.2,1],[.8,.2,0]],[0,1,2],[3,4,5])
 add_control('LEGAL_SHARED_EDGE_FLAT',[[0,0,0],[1,0,0],[.5,1,0],[.5,-1,0]],[0,1,2],[1,0,3],[0,1],[[0,1]],False)
 add_control('LEGAL_SHARED_VERTEX',[[0,0,0],[1,0,0],[0,1,0],[-1,0,0],[0,-1,0]],[0,1,2],[0,3,4],[0],[],False)
 add_control('LEGAL_NONCOPLANAR_ADJACENT_FOLD',[[0,0,0],[1,0,0],[.5,1,0],[.5,-.5,.8]],[0,1,2],[1,0,3],[0,1],[[0,1]],False)
 initial=np.array([[0.,0,0],[1,0,0],[0,1,0]]);reverse=initial.copy();reverse[2,1]=-1;end_sign=float(np.cross(reverse[1]-reverse[0],reverse[2]-reverse[0])@np.array([0,0,1]));mid=(initial+reverse)/2;midarea=float(np.linalg.norm(np.cross(mid[1]-mid[0],mid[2]-mid[0]))/2)
 controls.append({'name':'FACE_REVERSAL_BY_MATERIAL_TRIANGLE_COLLAPSE','expected':'HARD_FAIL','endpoint_signed_area_double':end_sign,'certified_collapse_fraction':'1/2','triangle_area_at_collapse_mm2':midarea,'passed':end_sign<0 and midarea==0,'note':'This is a real reversal along a specified linear material path, not a legitimate rigid normal rotation.'})
 deg=np.array([[0.,0,0],[1,0,0],[2,0,0]]);area=float(np.linalg.norm(np.cross(deg[1]-deg[0],deg[2]-deg[0]))/2);controls.append({'name':'DEGENERATE_NATIVE_TRIANGLE','expected':'HARD_FAIL','area_mm2':area,'passed':area==0})
 r2=ROOT/'audits/minimal_local_geometry_amendment_design_r2/REVIEW_COORDINATES_R2.json';vv=np.array(read(r2)['states']['FAILED_SOLVE_S5']['RSSF_RAW']);rr=pair_details(vv,204,207);controls.append({'name':'HISTORICAL_R2_S5_TRUE204_207_CROSSING','expected':'HARD_FAIL','source':ref(r2),'exact_fan_audit':rr,'passed':rr['true_off_shared_feature_contact']})
 v0=np.array([[0.,0,0],[1,0,0],[0,1,0],[2,0,0],[3,0,0],[2,1,0]]);v1=v0.copy();v1[3:,0]-=4;path=persistent_planar_path(v0,v1,[0,1,2],[3,4,5]);controls.append({'name':'PERSISTENT_COPLANAR_TUNNEL_WITH_BOTH_ENDPOINTS_DISJOINT','expected':'HARD_FAIL','endpoint0':intersection(v0,[0,1,2],[3,4,5]),'endpoint1':intersection(v1,[0,1,2],[3,4,5]),'all_3D_four_point_volume_polynomials_identically_zero':True,'continuous_2D_event_audit':path,'passed':path['collision_detected']})
 legal=np.array([[0.,0,0],[1,0,0],[.5,1,0],[.5,-1,0]]);legalend=legal.copy();legalend[2,1]+=.2;legalend[3,1]-=.2;pathlegal=persistent_planar_path(legal,legalend,[0,1,2],[1,0,3],[0,1],[[0,1]]);controls.append({'name':'PERSISTENT_COPLANAR_LEGAL_SHARED_EDGE_CONTINUATION','expected':'LEGAL','continuous_2D_event_audit':pathlegal,'passed':pathlegal['safe']})
 for fi in [2771,3332,3351]:
  p=F[fi];r=intersection(V,[p[0],p[1],p[2]],[p[0],p[2],p[3]],[p[0],p[2]],[[p[0],p[2]]]);controls.append({'name':f'BASELINE_PROJECTION_ONLY_QUAD{fi}','expected':'LEGAL_INTRINSIC_3D_DIAGNOSTIC_RETAINED','actual':r,'passed':not r['illegal']})
 allpass=all(z['passed'] for z in controls);dump('GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json',{'status':'PASS' if allpass else 'FAIL_CLOSED_CONTROL_FAILURE','TRUE_3D_NEGATIVE_CONTROLS_PASS':allpass,'controls':controls,'surface_clearance_added_mm':0,'tolerance_class':'COMPUTATIONAL_GEOMETRY_TOLERANCE','exact_rational_feature_predicates':True,'historical_validator_modified':False,'production_geometry_generated':False});assert allpass
 dump('PERSISTENT_COPLANAR_FEATURE_POLICY_R1.json',{'native_shared_vertex':'Exclude only identical shared point; any off-point contact remains hard.','native_shared_edge':'Exclude only actual segment, with exact on-segment predicate; exclude no surrounding strip or expanded triangle.','internal_fan_diagonal':'Legal only within its native face; coplanar area overlap still illegal.','persistent_coplanar':'Certify common plane, choose nonsingular dominant-axis chart, enumerate continuous2D orientation/edge events. Test finite clipped polygons after subtracting shared simplex. A pair-wide gap floor is never meaningful for adjacency.','moving_common_plane':'Use an adaptive chart atlas with explicit plane projection singularity events; fixed-plane proof above is not automatically a proof for arbitrary rotating common planes.','nonrational_event_roots':'Require certified algebraic-root intervals and finite-feature sign tests. If unresolved, fail closed rather than endpoint-only PASS.','negative_persistent_tunnel_control':path,'positive_persistent_shared_edge_control':pathlegal,'no_legal_shared_contact_in_collision_active_set':True})
 print('CONTROLS',len(controls),'PASS',allpass,flush=True)
if __name__=='__main__':run()
