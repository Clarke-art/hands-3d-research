import sys
sys.dont_write_bytecode=True
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
spec=importlib.util.spec_from_file_location('rebase_readonly_helpers',ROOT/'audits/palmar_thenar_source_shape_restoration_r1/common.py')
lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
lib.OUT=OUT
for name in dir(lib):
    if not name.startswith('_'):globals()[name]=getattr(lib,name)
PHASE='OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1'
SOURCE=ROOT/'references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
SOURCE_SHA='3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137'
RIG_SOURCE=ROOT/'production_spec/stage5_production_rig/human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend'
RIG_SHA='5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe'
WEIGHT_SHA='1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
CANDIDATE=OUT/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend'
MESH_NAME='RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH'

def open_candidate():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE),load_ui=False,use_scripts=False)
    ob=bpy.data.objects[MESH_NAME];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
    reset_pose(rig);bpy.context.view_layer.update();return ob,rig

def product_payload(ob,rig):
    return {'positions_local_m':[list(v.co) for v in ob.data.vertices],
        'faces':[list(f.vertices) for f in ob.data.polygons],
        'UV':[{'name':u.name,'coords':[list(v.uv) for v in u.data]} for u in ob.data.uv_layers],
        'groups':[g.name for g in ob.vertex_groups],
        'weights':[[[g.group,float(g.weight)] for g in v.groups] for v in ob.data.vertices],
        'rest':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(r) for r in b.matrix_local],
            'parent':b.parent.name if b.parent else None,'connected':b.use_connect,'deform':b.use_deform} for b in rig.data.bones},
        'mesh_world':[list(r) for r in ob.matrix_world], 'rig_world':[list(r) for r in rig.matrix_world],
        'modifiers':[{'name':m.name,'type':m.type,'object':m.object.name if getattr(m,'object',None) else None,
                      'preserve_volume':getattr(m,'use_deform_preserve_volume',None)} for m in ob.modifiers]}

def cases():
    matrix=S6/'full_stage6a_requalification_r1/FULL_STAGE6A_CASE_MATRIX_R1.json'
    rows=[r for r in read(matrix)['cases'] if r['angle_deg']==45 and (r['joint']=='MCP' or (r['digit']=='THUMB' and r['joint']=='IP'))]
    assert len(rows)==6 and all(r['applied_rotation_deg']==-45 and r['axis']=='bone_local_X' for r in rows)
    result=[{'case_id':r['digit']+'_'+r['joint']+'_45','bone':r['bone'],'applied_rotation_deg':r['applied_rotation_deg'],
        'axis':'bone_local_X','source_case_id':r['case_id']} for r in rows]
    oppmatrix=S6/'stage6b/STAGE6B_CASE_MATRIX.json'
    for r in read(oppmatrix)['cases']:
        if r['case_id'] in ['CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3']:
            result.append({k:r[k] for k in ['case_id','cmc_deg','mcp_deg','ip_deg']})
    assert len(result)==10
    return result

def apply_case(rig,c):
    reset_pose(rig)
    if 'bone' in c:set_local_axis_rotation(rig,c['bone'],c['applied_rotation_deg'])
    else:
        axis=Vector(read(S6/'stage6b/STAGE6B_OPPOSITION_VECTOR_AUDIT.json')['CMC_OPPOSITION_UNIT_ROTATION']['coefficients_local_XYZ']).normalized()
        q,angle=rotation_vector_to_quaternion(axis*math.radians(c['cmc_deg']))
        rig.pose.bones['THUMB_CMC_R'].rotation_quaternion=q
        if c['mcp_deg']:set_local_axis_rotation(rig,'THUMB_MCP_R',-c['mcp_deg'])
        if c['ip_deg']:set_local_axis_rotation(rig,'THUMB_IP_R',-c['ip_deg'])
    bpy.context.view_layer.update()
