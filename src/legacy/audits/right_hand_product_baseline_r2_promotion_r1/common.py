"""Exact promotion identity readers. No harmonic solver or weight writer."""
import sys,importlib.util,copy,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
QUAL=ROOT/'audits/right_hand_first_web_production_weight_qualification_r1'
CAUSAL=ROOT/'audits/right_hand_first_web_full_static_weight_field_causal_probe_r1'
spec=importlib.util.spec_from_file_location('qualification_readers_only',QUAL/'common.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
for n in ['bpy','np','m','BASE','ACTION','APPROVED_ACTION_SHA','FROZEN_SHA','action_payload','neutral','motion','coords','values','shape_state','weights','read','sha','digest','CASES','CASE_IDS']:
    globals()[n]=getattr(h,n)
m.old.lib.OUT=OUT
CANDIDATE=CAUSAL/'RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_PROBE_R1.blend'
APPROVED_SHA='0f6b24fc8d74a0fe37fb4a142169633d525db3c2ea58a440005060c137cc374d'
PHASE='RIGHT_HAND_PRODUCT_BASELINE_R2_PROMOTION_R1'
R2_DIR=ROOT/'production_spec/right_hand_product_baseline_r2'
R2=R2_DIR/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend'
POINTER=ROOT/'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json'
def dump(n,x):
    (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v.item())+'\n',encoding='utf-8')
def protected():
    result=read(QUAL/'FINAL_ASSET_PROTECTION_R1.json')['protected_inputs_expected_and_final'].copy()
    for folder in [CAUSAL,QUAL]:
        for p in folder.rglob('*'):
            if p.is_file() and not any(v in ['__pycache__','_tmp'] for v in p.relative_to(folder).parts):result[p.relative_to(ROOT).as_posix()]=sha(p)
    result[CANDIDATE.relative_to(ROOT).as_posix()]=APPROVED_SHA
    result[BASE.relative_to(ROOT).as_posix()]=FROZEN_SHA
    return result
def verify(inputs,allow_pointer=False):
    for path,expected in inputs.items():
        if allow_pointer and path==POINTER.relative_to(ROOT).as_posix():continue
        assert sha(ROOT/path)==expected,path
def open_asset(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    ob=bpy.data.objects[m.MESH_NAME];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];return ob,rig

PRODUCT_METADATA_KEYS={'DESIGN_ONLY','NOT_PRODUCTION','HUMAN_APPROVAL_PENDING','PRODUCTION_PROMOTION','PHASE','PRODUCT_BASELINE_STATUS','PRODUCT_BASELINE_SOURCE_SHA256'}
def core_payload(ob,rig):
    """Whole product identity, excluding only enumerated mesh-object approval labels."""
    object_state=m.object_payload(ob)
    object_state['custom_properties']={k:v for k,v in object_state['custom_properties'].items() if k not in PRODUCT_METADATA_KEYS}
    me=ob.data
    return {
        'mesh_topology_UV_weights_rest_modifiers':m.product_payload(ob,rig),
        'mesh_object_state':object_state,
        'armature_complete':m.rig_payload(rig),
        'Basis_corrective_and_driver':shape_state(ob),
        'materials_native':[m.material_payload(mat) for mat in me.materials],
        'native_shading':{'smooth_faces':[p.use_smooth for p in me.polygons],'sharp_edges':[e.use_edge_sharp for e in me.edges],'face_material_indices':[p.material_index for p in me.polygons],'custom_normals':me.has_custom_normals,'normal_vectors':[list(n.vector) for n in me.corner_normals] if me.has_custom_normals else []},
        'mesh_edges_loops':{'edges':[list(e.vertices) for e in me.edges],'loops':[[l.vertex_index,l.edge_index] for l in me.loops],'face_ranges':[[p.loop_start,p.loop_total] for p in me.polygons]},
        'UV_layer_flags':[{'name':u.name,'active':u.active,'active_render':u.active_render,'active_clone':u.active_clone} for u in me.uv_layers],
        'vertex_group_settings':[[g.index,g.name,g.lock_weight] for g in ob.vertex_groups],
        'mesh_attributes':[{'name':a.name,'type':a.data_type,'domain':a.domain,'values':[m.rna(v) for v in a.data]} for a in me.attributes if a.name!='position'],
        'mesh_native_settings':m.rna(me,omit=('vertices','edges','loops','polygons','attributes','uv_layers','vertex_colors','materials','shape_keys','animation_data'),depth=0),
        'mesh_custom_properties':m.props(me),
    }
