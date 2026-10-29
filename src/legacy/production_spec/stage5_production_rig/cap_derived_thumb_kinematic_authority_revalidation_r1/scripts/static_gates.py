import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
D=read(OUT/'RAW_READ_ONLY_GEOMETRY_AND_BONES.json');G=read(OUT/'GEOMETRIC_EVIDENCE_COMPUTATION.json')
V=[Vector(v) for v in D['RSSF']['vertices_world_m']];F=D['RSSF']['faces'];ids=set(G['native_domain_vertex_ids']);ff=[i for i,vs in enumerate(F) if all(v in ids for v in vs)]
bvh=BVHTree.FromPolygons(V,[F[i] for i in ff],all_triangles=False)
def vec(v):return Vector(v)
def measure(p):
 loc,norm,idx,dist=bvh.find_nearest(p)
 return {'nearest_native_thumb_surface_mm':dist*1000,'nearest_face_id':ff[idx],'signed_distance_mm':(p-loc).dot(norm)*1000,'inside_native_thumb_local_surface':(p-loc).dot(norm)<1e-7}
def angle(a,b):return math.degrees(vec(a).angle(vec(b)))
out={'method':'Nearest oriented native-thumb surface on RSSF; excludes contact-adjacent INDEX surface. Sign gate is local static plausibility, not a new deformation qualification.','bones':{},'cross_sections':{}}
for key,origin in [('current',G['IP_current_head_world_m']),('independent',G['RSSF_locator']['IP']['center_world_m'])]:
 p=vec(origin);axis=vec(G['RSSF_locator']['axis']);z=vec(G['dorsal_cue']);z=(z-axis*z.dot(axis)).normalized();x=axis.cross(z).normalized();rays=[]
 for i in range(16):
  a=2*math.pi*i/16;dr=x*math.cos(a)+z*math.sin(a);loc,n,idx,dist=bvh.ray_cast(p,dr,0.04)
  rays.append({'direction':list(dr),'hit_world_m':list(loc) if loc else None,'radius_mm':dist*1000 if loc else None})
 out['cross_sections'][key]={'center_world_m':origin,'surface_gate':measure(p),'rays':rays,'all_directions_contained':all(r['hit_world_m'] is not None for r in rays),'opposite_radius_asymmetry_mm':[abs(rays[i]['radius_mm']-rays[i+8]['radius_mm']) if rays[i]['radius_mm'] and rays[i+8]['radius_mm'] else None for i in range(8)]}
parent=Matrix(D['R2A']['bones']['THUMB_MCP_R']['matrix_local']).to_3x3()
for name in ['THUMB_IP_R','THUMB_TIP_R']:
 c=D['R2A']['bones'][name];cand=G['candidate'][name];m=Matrix(cand['frame_XYZ']);ax,roll=bpy.types.Bone.AxisRollFromMatrix(m)
 current_m=Matrix(c['matrix_local']).to_3x3();delta=math.degrees((roll-c['edit_roll_rad']+math.pi)%(2*math.pi)-math.pi)
 transported=vec(current_m.col[1]).rotation_difference(vec(m.col[1]))@current_m.col[2]
 twist=math.degrees(math.atan2(m.col[1].dot(transported.cross(m.col[2])),transported.dot(m.col[2])))
 pr=parent.col[1].rotation_difference(m.col[1])@parent.col[2]
 parent_twist=math.degrees(math.atan2(m.col[1].dot(pr.cross(m.col[2])),pr.dot(m.col[2]))) if name=='THUMB_IP_R' else 0.
 row={'candidate_roll_rad':roll,'candidate_roll_deg':math.degrees(roll),'current_roll_deg':math.degrees(c['edit_roll_rad']),'roll_coordinate_delta_deg':delta,
 'parallel_transport_twist_delta_deg':twist,'axis_delta_deg':angle(m.col[1],current_m.col[1]),'frame_rotation_delta_deg':math.degrees(current_m.to_quaternion().rotation_difference(m.to_quaternion()).angle),
 'candidate_parent_transport_twist_deg':parent_twist,'candidate_frame_XYZ':cand['frame_XYZ'],'current_frame_XYZ':[list(r) for r in current_m],
 'head_delta_mm':(vec(cand['head_world_m'])-vec(c['head_world_m'])).length*1000,'tail_delta_mm':(vec(cand['tail_world_m'])-vec(c['tail_world_m'])).length*1000}
 for label,b in [('current',c),('candidate',cand)]:
  h=vec(b['head_world_m']);t=vec(b['tail_world_m']);ys=(t-h).normalized();samples=[]
  for i in range(1,21):
   f=.05+.8*i/20;q=h+(t-h)*f;r=measure(q);r.update(t=f,world_m=list(q));samples.append(r)
  row[label]={'head':measure(h),'tail':measure(t),'segment_samples':samples,'inside_count':sum(r['inside_native_thumb_local_surface'] for r in samples),'total':20,'axis_to_independent_longitudinal_deg':angle(ys,G['geometric_axis_independent_locator_to_tip']),
  'points_toward_terminal_tip':ys.dot(vec(G['mapping']['rssf_v284_world_m'])-vec(G['IP_current_head_world_m']))>0}
 out['bones'][name]=row
(OUT/'STATIC_GEOMETRY_GATES_AND_FRAME_METRICS.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('GATES', {n:{k:r[k] for k in ['head_delta_mm','tail_delta_mm','axis_delta_deg','roll_coordinate_delta_deg','parallel_transport_twist_delta_deg']} for n,r in out['bones'].items()})
print('INSIDE',{n:{k:r[k]['inside_count'] for k in ['current','candidate']} for n,r in out['bones'].items()})
print('SECTION',{k:(v['all_directions_contained'],v['surface_gate'],max(x for x in v['opposite_radius_asymmetry_mm'] if x is not None)) for k,v in out['cross_sections'].items()})
