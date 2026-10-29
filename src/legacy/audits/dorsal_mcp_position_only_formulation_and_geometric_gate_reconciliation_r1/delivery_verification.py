import sys
sys.dont_write_bytecode=True
from semantic_audit import *
import ast

REQUIRED=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','GEOMETRIC_GATE_SEMANTIC_CLASSIFICATION_R1.json','PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json','SHARED_EDGE_CONTACT_SEMANTICS_R1.json','ACTIVE_SET_PAIR_INVENTORY_R1.json','LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json','NORMAL_TANGENT_COUPLED_DIRECTION_AUDIT_R1.json','GEOMETRIC_GATE_NEGATIVE_CONTROLS_R1.json','PROPOSED_POSITION_ONLY_GEOMETRY_GATE_CONTRACT_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json']

def fixed_projection():
 d=read(OUT/'LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json');bow=read(OUT/'PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json');results={}
 for label,v in [('FROZEN_BASELINE',V),('R3_BEST_FAILED_POINT',P)]:
  r=d['points'][label]['directions'][0];df=np.zeros_like(V);df[IDS]=np.array(r['normalized_direction_vectors_world']);rows=[]
  for fid,z in bow['flags'].items():
   fi=int(fid);chart=np.array(z['projection_diagnostic']['projection_chart']);a=projected_cross(v,fi,chart);b=projected_cross(v+1e-5*df,fi,chart)
   def params(t):return [{'parameters':q['parameters'],'strict_parameter_margin':q['strict_parameter_margin']} for q in t['hits']]
   gaps=[]
   for vv in [v,v+1e-5*df]:
    cycle=F[fi];ds=[]
    for i,j in [(0,2),(1,3)]:
     p,q,ss,tt=segment_segment(vv[cycle[i]],vv[cycle[(i+1)%4]],vv[cycle[j]],vv[cycle[(j+1)%4]]);ds.append(float(np.linalg.norm(p-q)))
    gaps.append(min(ds))
   rows.append({'native_face_id':fi,'fixed_chart_source':'Frozen source SVD chart stored in PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json','before_flag':a['flag'],'after_flag':b['flag'],'before_crossing_count':len(a['hits']),'after_crossing_count':len(b['hits']),'before_intersection_parameters':params(a),'after_intersection_parameters':params(b),'before_minimum_actual_opposite_edge_gap_mm':gaps[0],'after_minimum_actual_opposite_edge_gap_mm':gaps[1],'boolean_count_no_regression':len(b['hits'])<=len(a['hits']),'continuous_no_new_true3D_defect_certificate':'CONTINUOUS_MICRO_WITNESS_CERTIFICATE_R1.json','severity_note':'Crossing parameter location is disclosed, not assumed to be an anatomical severity score. Shape/projection appearance remains Human review.'})
  assert all(z['boolean_count_no_regression'] and z['after_minimum_actual_opposite_edge_gap_mm']>0 for z in rows);results[label]=rows
 dump('FIXED_SOURCE_PROJECTION_MICRO_NO_REGRESSION_R1.json',{'operational_rule':'No new flag and no increased crossing count in the SAME frozen-source chart, plus unchanged legal intrinsic fan intersection combinatorics. Aesthetic severity is separately disclosed for Human review, not inferred from camera-dependent crossing position.','step_max_mm':1e-5,'points':results,'new_geometry_coordinates_saved':False})

def verify():
 assert all((OUT/f).is_file() for f in REQUIRED)
 files=list(OUT.glob('*.json'))
 def finite(z):
  if isinstance(z,float):assert math.isfinite(z)
  elif isinstance(z,dict):
   for v in z.values():finite(v)
  elif isinstance(z,list):
   for v in z:finite(v)
 for p in files:finite(read(p))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
 assert not list(OUT.rglob('*.blend'))
 figs=list((OUT/'figures').glob('*.png'));assert len(figs)==4 and all(p.stat().st_size>10000 for p in figs)
 s=read(OUT/(PHASE+'_STATUS.json'));assert s['status']=='PASS_POSITION_ONLY_FEASIBILITY_REOPENED' and s['NEXT_EXECUTED'] is False and s['geometry_candidate_count']==0
 m=read(OUT/'ARTIFACT_MANIFEST_R1.json');errors=[z['path'] for z in m['artifacts'] if sha(ROOT/z['path'])!=z['sha256']]
 assert not errors,errors
 print('DELIVERY VERIFIED required=',len(REQUIRED),'finite_JSON=',len(files),'figures=',len(figs),'manifest_drift=',len(errors),'no_candidate_blend=True',flush=True)

if __name__=='__main__':
 if '--fixed-projection' in sys.argv:fixed_projection()
 else:verify()
