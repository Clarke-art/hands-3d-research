"""Read-only causal inputs. No pose cases applied and no blend saves.
Stage6A coordinates are reused from the frozen completed run.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
FULL=S6/'full_stage6a_requalification_r1'
assert read(FULL/'FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json')['FULL_STAGE6A_REQUALIFICATION_R1']=='FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION'
assert read(FULL/'FULL_STAGE6A_SELF_INTERSECTION_AUDIT_R1.json')['new_unapproved_severe_count']==9
paths={
 'STAGE4A_R2_FROZEN':ROOT/'production_spec/stage4_blender/stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend',
 'STAGE4B_RSSF_R2':ROOT/'production_spec/stage4_blender/stage4b_rssf/RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend',
 'STAGE4C_R2_RAW':ROOT/'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend',
 'CORRECTED_STAGE5A_RIG':CORRECTED,
 'R2_PRODUCTION':CAND}
rows={};schema=None
for label,path in paths.items():
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 ob=bpy.data.objects['Hand  - Realistic'];me=ob.data;MW=ob.matrix_world.copy()
 raw=[list(<REDACTED_EMAIL>) for v in me.vertices];faces=[list(f.vertices) for f in me.polygons];edges=[list(e.vertices) for e in me.edges]
 topo={'vertex_count':len(raw),'faces':faces,'edges':edges}
 if schema is None:schema=topo
 assert topo==schema,(label,'topology identity mismatch')
 rig=bpy.data.objects.get('RIGHT_HAND_PRODUCTION_RIG')
 if rig:
  assert all(abs(pb.rotation_quaternion.angle)<1e-7 and tuple(pb.location)==(0,0,0) and tuple(pb.scale)==(1,1,1) for pb in rig.pose.bones),'Not zero/RSSF saved'
 N=(MW.to_3x3().inverted().transposed())
 weights=[{ob.vertex_groups[g.group].name:float(g.weight) for g in v.groups if g.weight>0} for v in me.vertices]
 mods=[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render,**({'object':m.object.name if m.object else None,'preserve_volume':m.use_deform_preserve_volume,'bone_envelopes':m.use_bone_envelopes,'vertex_groups':m.use_vertex_groups} if m.type=='ARMATURE' else {})} for m in ob.modifiers]
 def evaluate():
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);em=eo.to_mesh()
  result={'world_m':[list(<REDACTED_EMAIL>) for v in em.vertices],'faces':[list(p.vertices) for p in em.polygons],'edges':[list(e.vertices) for e in em.edges],'face_normals_world':[list((<REDACTED_EMAIL>).normalized()) for p in em.polygons],'corner_normals_world':[list((<REDACTED_EMAIL>).normalized()) for n in em.corner_normals]}
  eo.to_mesh_clear();return result
 on=evaluate();arm=[m for m in ob.modifiers if m.type=='ARMATURE'];flags=[m.show_viewport for m in arm]
 for m in arm:m.show_viewport=False
 off=evaluate()
 for m,flag in zip(arm,flags):m.show_viewport=flag
 bpy.context.view_layer.update()
 assert on['faces']==off['faces']==faces and on['edges']==off['edges']==edges
 rows[label]={'input':ref(path),'raw_world_m':raw,'raw_local_m':[list(v.co) for v in me.vertices],'evaluated_on':on,'evaluated_armature_off':off,'weights':weights,'armature_count':len(arm),'modifiers':mods,'source_face_use_smooth':[f.use_smooth for f in me.polygons],'source_edge_sharp':[e.use_edge_sharp for e in me.edges],'has_custom_normals':me.has_custom_normals,'corner_normals_world':[list((<REDACTED_EMAIL>).normalized()) for n in me.corner_normals],'face_material_indices':[f.material_index for f in me.polygons],'material_slots':[None if m is None else {'name':m.name,'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes} for m in me.materials],'UV_payload_hash':digest({u.name:[list(x.uv) for x in u.data] for u in me.uv_layers}),'object_world_matrix':[list(r) for r in MW],'parent_inverse':[list(r) for r in ob.matrix_parent_inverse],'armature_world_matrix':[list(r) for r in rig.matrix_world] if rig else None,'pose_position':rig.data.pose_position if rig else None,'pose_zero_verified':True if rig else 'NO_ARMATURE'}
 if label=='R2_PRODUCTION':assert sha(path)==EXPECTED_CAND and digest(weights)==EXPECTED_WEIGHTS
 print(label,len(raw),'armatures',len(arm),'raw/on max mm',max((Vector(a)-Vector(b)).length*1000 for a,b in zip(raw,on['world_m'])),'customNormals',me.has_custom_normals,flush=True)
G=read(FULL/'POSED_COORDINATES_R1.json')
assert G['faces']==schema['faces'] and G['edges']==schema['edges']
for cid in ['BIND','IDX_MCP_15','IDX_MCP_30','IDX_MCP_45']:
 rows['STAGE6A_'+cid]={'input':ref(FULL/'POSED_COORDINATES_R1.json'),'world_m':G['positions_world_m'][cid],'source':'Existing completed coordinate evidence; no pose execution','source_case':cid}
dump('LINEAGE_RAW_READONLY_EXTRACTION.json',{'stages':rows,'topology':schema,'pose_applications':0,'blend_saves':0,'geometry_weight_normal_material_edits':0,'earlier_stage4A_BASE_not_used_for_vertex_identity_comparison':{'reason':'3364 vertices, differs from the current frozen3416 topology; no index identity is assumed across that boundary. Only Stage4A_R2 frozen is added to the requested lineage.'}})
print('READONLY LINEAGE EXTRACTION COMPLETE')
