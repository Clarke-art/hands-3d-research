"""Read-only qualification harness. No field solver, weight setter or .blend save."""
import sys,importlib.util,copy
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'audits/right_hand_first_web_full_static_weight_field_causal_probe_r1'
PRODUCT=ROOT/'audits/right_hand_first_web_product_impact_go_no_go_r1'
spec=importlib.util.spec_from_file_location('approved_full_field_readers',PREV/'common.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
for n in ['bpy','np','m','BASE','ACTION','APPROVED_ACTION_SHA','FROZEN_SHA','action_payload','open_frozen','neutral','motion','coords','values','shape_state','weights','native_no_weights','read','sha','digest','PATCH_IDS']:
    globals()[n]=getattr(h,n)
m.old.lib.OUT=OUT
PHASE='RIGHT_HAND_FIRST_WEB_PRODUCTION_WEIGHT_QUALIFICATION_R1'
CANDIDATE=PREV/'RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_PROBE_R1.blend'
VIEWS=['DEFAULT_TEACHING_VIEW','NORMAL_ORBIT_VIEW','REASONABLE_CLOSE_VIEW']
PREVIOUS=read(PREV/'PROBE_MEASUREMENTS_R1.json')
PRODUCT_DATA=read(PRODUCT/'PRODUCT_VIEW_OBSERVATION_R1.json')
MOTION_CAMERAS={r['frame']:r['cameras'] for r in PRODUCT_DATA['frames'] if 'observation' not in r}
assert len(MOTION_CAMERAS)==210
CASE_IDS=['ZERO','INDEX_MCP_45','CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3']
CASES=[next(c for c in m.CASES if c['case_id']==n) for n in CASE_IDS]
def dump(n,x):
    (OUT/n).write_text(__import__('json').dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v.item())+'\n',encoding='utf-8')
def protected():
    result=read(PREV/'FULL_VECTOR_FIELD_DEFINITION_R1.json')['protected_inputs_before'].copy()
    for p in PREV.rglob('*'):
        if p.is_file() and not any(v in ['__pycache__','_tmp'] for v in p.relative_to(PREV).parts):result[p.relative_to(ROOT).as_posix()]=sha(p)
    for p in [PRODUCT/'PRODUCT_VIEW_OBSERVATION_R1.json',PRODUCT/'FRAMING_PROBE_R1.json',PRODUCT/'VIDEO_VERIFICATION_R1.json',ROOT/'production_spec/right_hand_product_baseline_r1/SOURCE_HUMAN_APPROVAL_BIND_R1.json']:
        result[p.relative_to(ROOT).as_posix()]=sha(p)
    for view in VIEWS:
        p=PRODUCT/f'product_7s_{view.lower()}.mp4';result[p.relative_to(ROOT).as_posix()]=sha(p)
    return result
def verify(before):
    for path,expected in before.items():assert sha(ROOT/path)==expected,path
def open_candidate():
    assert sha(CANDIDATE)==PREVIOUS['candidate']['sha256']
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE),load_ui=False,use_scripts=False)
    ob=bpy.data.objects[m.MESH_NAME];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];neutral(rig)
    return ob,rig
def camera_from_baseline_pose(V):
    # Reuse prior product framing rule and the SAME mature directions/normal scales.
    hand=(V.min(0)+V.max(0))*.5
    web=(V[PATCH_IDS].min(0)+V[PATCH_IDS].max(0))*.5
    mid=hand*.45+web*.55
    cams=copy.deepcopy(MOTION_CAMERAS[1])
    for view in VIEWS:cams[view]['center']=(hand if view=='DEFAULT_TEACHING_VIEW' else mid).tolist()
    return cams
def constraint_payload(ob,rig):
    return {'rig':m.rig_payload(rig),'mesh_constraints':[m.rna(c,depth=2) for c in ob.constraints]}
