import sys
sys.dont_write_bytecode=True
import geometry as geo
from geometry import *
D=read(OUT/'R2_GEOMETRY_AMENDMENT_CANDIDATES.json');cs=D['candidates']
if not cs:exit()
ST=read(OUT/'R2_EVALUATED_COORDINATES.json')['states'];S=read(OUT/'R2_BIND_SMOKE_PREVIEW.json')
review=read(OUT/'REVIEW_COORDINATES_R2.json');ba=read(OUT/'R2_BOUNDARY_CONTINUITY_AUDIT.json');pose_audits={}
rawV=V.copy();rawN=baseN.copy();rawAngles=baseA.copy();rawAreas=baseAreas.copy();rawBow=baseBow.copy()
for label,c in cs.items():
 pose_audits[label]={};ids=c['write_vertices'];geo.FULLFS=sorted(face_domain(ids))
 for pose in ['BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
  bv=np.array(ST['CURRENT'][pose]);vv=np.array(ST[label][pose]);geo.V=bv;geo.baseN=normals(bv);geo.baseA=angles(bv);geo.baseAreas=areas(bv);geo.baseBow=set(quad_bowties(bv))
  # Restore all changed globals in reused functions through geometry namespace.
  st=geo.structure(vv,ids);cb,num=geo.contact_check(bv,ids);cc,numc=geo.contact_check(vv,ids);new=sorted(set(cc)-set(cb))
  an=angles(vv);es={ei for fi in face_domain(ids) for ei in FE[fi]}
  internal=[ei for ei in es if (geo.baseA[ei]<90 and an[ei]>=90) or (an[ei]>45 and an[ei]-geo.baseA[ei]>20)]
  fail=[]
  for k in ['new_degenerate_faces','new_quad_bowties','new_reference_reversed_faces','new_previously_outward_normal_reversals','new_boundary_sharp_folds']:
   if st[k]:fail.append(k)
  if new:fail.append('new_exact_contact_or_self_intersection')
  if internal:fail.append('new_sharp_hinge')
  res={'status':'PASS_STRUCTURAL_DIAGNOSTIC_PENDING_VISUAL_REVIEW' if not fail else 'FAIL_DIAGNOSTIC_PREVIEW','failures':fail,'structure':st,'new_contact_pairs':[{'face_ids':list(k),**cc[k]} for k in new],'new_contact_count':len(new),'new_self_intersection_count':len(new),'self_intersection_count_semantics':'Introduced local-to-global native-face intersections only; unchanged historical intersections remain independent.','all_incident_new_sharp_hinge_edges':internal,'removed_contact_pairs_INCIDENTAL_EFFECT':[list(k) for k in sorted(set(cb)-set(cc))],'baseline_triangle_pairs_tested':num,'candidate_triangle_pairs_tested':numc,'visual_dent_crease_shading_gate':'PENDING_IMAGE_INSPECTION','old9_not_optimization_objective':True}
  pose_audits[label][pose]=res;review['states'][label][pose]=ST[label][pose]
  print('POSE_EXACT',label,pose,'fail',fail,'newcontact',len(new),flush=True)
  if label==next(iter(cs)):review['states']['CURRENT'][pose]=ST['CURRENT'][pose]
 geo.V=rawV;geo.baseN=rawN;geo.baseA=rawAngles;geo.baseAreas=rawAreas;geo.baseBow=rawBow
 # Compare actual float32 application with intended design scope; literal zero
 # exterior movement is verified in Blender and repeated from evaluated raw.
 actual=np.array(ST[label]['RSSF_RAW']);d=actual-rawV;mag=np.linalg.norm(d,axis=1)
 c['actual_float32_write_vertex_ids']=[i for i in ids if mag[i]>0]
 c['actual_float32_write_vertex_count']=len(c['actual_float32_write_vertex_ids'])
 c['design_to_float32_max_delta_mm']=float(np.linalg.norm(actual-np.array(c['world_mm']),axis=1).max())
 c['float32_gate_notes']='In-memory mesh copies only; natural face normals recomputed without changing normal flags.'
S['independent_exact_pose_audits']=pose_audits;S['contact_algorithm']='Float64 native fan triangles against entire mesh; shared-topology away-contact and coplanar-overlap included, alongside independent BVH kernel in Blender.'
S['numeric_tolerance_mm']=eps;S['Full42_executed']=False;S['old9_unchanged']=True;S['status']='DIAGNOSTIC_ONLY_PENDING_VISUAL_REVIEW'
dump('R2_BIND_SMOKE_PREVIEW.json',S);dump('REVIEW_COORDINATES_R2.json',review);dump('R2_GEOMETRY_AMENDMENT_CANDIDATES.json',D)
ba['candidate_pose_audits']={label:{pose:z['structure']['boundary_audit'] for pose,z in poses.items()} for label,poses in pose_audits.items()};dump('R2_BOUNDARY_CONTINUITY_AUDIT.json',ba)
