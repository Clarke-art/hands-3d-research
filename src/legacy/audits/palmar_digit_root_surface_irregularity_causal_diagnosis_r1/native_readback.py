import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
roi=read(OUT/'PALMAR_DIGIT_ROOT_IRREGULARITY_ROI_R1.json');fs=roi['visible_hit_faces'];vs=roi['vertices'];results={}
paths={'CURRENT_R2':S5/'geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend','PRE_DONOR_R2':S5/'targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend','NEW_STAGE4C':ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_R1.blend'}
for label,p in paths.items():
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 o=next(o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)==3416);me=o.data
 results[label]={'input':ref(p),'source_native_coordinates_world_m':[list(<REDACTED_EMAIL>[i].co) for i in vs],'smooth_flags':[me.polygons[i].use_smooth for i in fs],'sharp_edges':[i for i in roi['edges'] if me.edges[i].use_edge_sharp],'has_custom_normals':me.has_custom_normals,'auto_smooth_property_present':hasattr(me,'use_auto_smooth'),'attributes':[{'name':a.name,'domain':a.domain,'data_type':a.data_type} for a in me.attributes],'modifiers':[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render} for m in o.modifiers],'vertex_normals':{str(i):list(me.vertices[i].normal) for i in vs},'face_normals':{str(i):list(me.polygons[i].normal) for i in fs},'corner_normals':{str(i):[list(me.corner_normals[l].vector) for l in me.polygons[i].loop_indices] for i in fs},'armature_pose_basis':{r.name:{b.name:[list(row) for row in b.matrix_basis] for b in r.pose.bones} for r in bpy.data.objects if r.type=='ARMATURE'},'read_only':True}
dump('NATIVE_SHADING_READBACK_R1.json',{'runtime':bpy.app.version_string,'runtime_binary':bpy.app.binary_path,'states':results,'native_setters':0,'blend_saves':0,'pose_applications':0,'qualified_coordinate_evaluations':0})
print('Read-only native shading captured',flush=True)
