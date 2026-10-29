"""Diagnostic evaluations only: baseline and feasible R2 candidates x bind/IDX15/30/45.
No qualification harness, no historical writes, no blend saves.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math,numpy as np
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
D=read(OUT/'R2_GEOMETRY_AMENDMENT_CANDIDATES.json')
DIAG=ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1'
L=read(DIAG/'LINEAGE_RAW_READONLY_EXTRACTION.json');ROI=read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json')
F=L['topology']['faces'];E=L['topology']['edges'];V=np.array(L['stages']['R2_PRODUCTION']['raw_world_m'])*1000
used=[];ns={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':1000}
used.append(reuse(S6/'stage6a/scripts/s6a_common.py',['reset_pose','set_joint_rotation','evaluate','pose_state'],ns))
ex={'Vector':Vector};used.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_common.py',['ray_triangle','tri_tri_intersection','seg_len'],ex))
pp={'bpy':bpy};used.append(reuse(S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1/blender_extract.py',['mesh_payload','rig_payload','weights'],pp))
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];mw=ob.matrix_world.copy();inv=mw.inverted();original=ob.data
rigbefore=pp['rig_payload'](rig);weightsbefore=pp['weights'](ob);meshbefore=pp['mesh_payload'](ob)
tris=[];owners=[]
for fi,p in enumerate(F):
 for k in range(1,len(p)-1):tris.append((p[0],p[k],p[k+1]));owners.append(fi)
writeunion=set(i for c in D['candidates'].values() for i in c['write_vertices'])
changedfaces={fi for fi,p in enumerate(F) if writeunion.intersection(p)}
def crossing(v):
 # Stable native fan triangulation, translated coordinates avoid large world float loss.
 origin=Vector(v[ROI['center_vertex_id']]);coords=[(Vector(p)-origin)/1000 for p in v]
 bvh=BVHTree.FromPolygons(coords,tris,all_triangles=True,epsilon=0)
 pairs=set()
 for a,b in bvh.overlap(bvh):
  if a>=b:continue
  fa,fb=owners[a],owners[b]
  if fa==fb or not ({fa,fb}&changedfaces):continue
  # Nonadjacent native faces; all sharing any vertex are a separate fold/continuity check.
  if set(F[fa]).intersection(F[fb]):continue
  pts,ok=ex['tri_tri_intersection']([coords[i] for i in tris[a]],[coords[i] for i in tris[b]])
  if ok and ex['seg_len'](pts)*1000>1e-5:pairs.add(tuple(sorted((fa,fb))))
 return pairs
case_matrix=read(S6/'full_stage6a_requalification_r1/FULL_STAGE6A_CASE_MATRIX_R1.json')
cases=case_matrix['cases']
selected={c['case_id']:c for c in cases if c['case_id'] in ['IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']}
assert len(selected)==3
labels={'CURRENT':{'world_mm':V.tolist(),'write_vertices':[]},**D['candidates']}
states={};audits={};basepairs={};sourceflags=[p.use_smooth for p in original.polygons]
for label,c in labels.items():
 me=original.copy();ob.data=me
 if label!='CURRENT':
  for i in c['write_vertices']:me.vertices[i].co=inv@Vector(np.array(c['world_mm'][i])/1000)
 me.update();ns['reset_pose'](rig);bpy.context.view_layer.update()
 wp=pp['weights'](ob);mp=pp['mesh_payload'](ob)
 invariant={k:mp[k]==meshbefore[k] for k in meshbefore if k not in ['vertices','positions','coordinates','vertex_positions','coords','vertex_coordinates']}
 # Explicit properties are the source of truth; payload may contain combined coordinate keys.
 checks={'vertex_count':len(me.vertices)==len(original.vertices),'edge_identity':[(tuple(e.vertices)) for e in me.edges]==[tuple(e.vertices) for e in original.edges],'face_winding_identity':[list(p.vertices) for p in me.polygons]==F,'material_assignment':[p.material_index for p in me.polygons]==[p.material_index for p in original.polygons],'material_slots':[m.as_pointer() for m in me.materials]==[m.as_pointer() for m in original.materials],'smooth_flags':[p.use_smooth for p in me.polygons]==sourceflags,'custom_normal_flag':me.has_custom_normals==original.has_custom_normals,'UV':all([tuple(x.uv) for x in uv.data]==[tuple(x.uv) for x in original.uv_layers[uv.name].data] for uv in me.uv_layers),'weights_exact':wp==weightsbefore,'weight_hash':digest(wp)==EXPECTED_WEIGHTS,'rig_rest_exact':pp['rig_payload'](rig)==rigbefore,'vertex_group_order':[g.name for g in ob.vertex_groups]==[g.name for g in ob.vertex_groups]}
 assert all(checks.values()),checks
 off=np.array([list(<REDACTED_EMAIL>) for v in me.vertices])*1000
 intended=np.array(c['world_mm']);outside=sorted(set(range(len(off)))-set(c['write_vertices']))
 if label!='CURRENT':assert np.array_equal(off[outside],V[outside])
 states[label]={'RSSF_RAW':off.tolist()};audits[label]={'invariant_checks':checks,'actual_write_vertices':[i for i in range(len(off)) if not np.array_equal(off[i],V[i])],'intended_to_float32_actual_max_mm':float(np.max(np.linalg.norm(off-intended,axis=1))),'states':{}}
 for pose in ['BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
  ns['reset_pose'](rig)
  if pose!='BIND':ns['set_joint_rotation'](rig,selected[pose]['bone'],selected[pose]['applied_rotation_deg'])
  bpy.context.view_layer.update();ev,poly=ns['evaluate'](ob,mw);vv=np.array([list(x) for x in ev])*1000;states[label][pose]=vv.tolist()
  assert [list(p) for p in poly]==F
  pairs=crossing(vv)
  if label=='CURRENT':basepairs[pose]=pairs
  newpairs=sorted(pairs-basepairs[pose]);removed=sorted(basepairs[pose]-pairs)
  a={'pose_authority':{'bone':'NONE','angle':0} if pose=='BIND' else selected[pose],'evaluated_topology_same':True,'introduced_nonadjacent_exact_pairs':newpairs,'removed_local_diagnostic_pairs':removed,'crossing_scope':'Only pairs touching the write-set incident faces; baseline contact classification and the prior9 crossings are not rerun or adjudicated. Nonadjacent fan-triangle segment intersections, geometric numerical tolerance1e-5mm, not an anatomy or Stage6 gate.','INCIDENTAL_DIAGNOSTIC_EFFECT':'Any changed contact recorded only; not candidate optimization/ranking objective.','pose_state':ns['pose_state'](rig),'rig_rest_unchanged':pp['rig_payload'](rig)==rigbefore}
  if pose=='BIND':a['raw_to_bind_max_mm']=float(np.max(np.linalg.norm(vv-off,axis=1)))
  audits[label]['states'][pose]=a
  print('DESIGN_SMOKE',label,pose,'introduced',newpairs,'removed',len(removed),flush=True)
 ns['reset_pose'](rig);bpy.context.view_layer.update();ob.data=original;bpy.data.meshes.remove(me)
dump('R2_EVALUATED_COORDINATES.json',{'DESIGN_ONLY_NOT_PRODUCTION':True,'units':'mm','states':states,'production_blend_save_count':0,'Full_Stage6A_executed':False})
dump('R2_BIND_SMOKE_PREVIEW.json',{'status':'DIAGNOSTIC_EVALUATION_ONLY_NOT_STAGE6A_QUALIFICATION','source':ref(CAND),'source_weight_hash':EXPECTED_WEIGHTS,'reused_function_AST_provenance':used,'candidate_evaluations':audits,'max_design_candidates':len(D['candidates']),'case_subset':['BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45'],'Full42_rerun':False,'Stage6B':False,'production_blend_save_count':0,'old9_exact_crossing_evidence_untouched':True,'saved_baseline_coordinate_verification':'Compared in the final independent metrics step; zero/full saved poses should reproduce.'})
print('DESIGN EVALUATION COMPLETE',flush=True)
