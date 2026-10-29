import sys, importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PREV=ROOT/'audits/official_l1_product_rebase_feasibility_r1'
spec=importlib.util.spec_from_file_location('previous_rebase',PREV/'common.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
old.lib.OUT=OUT
for name in dir(old):
    if not name.startswith('_'): globals()[name]=getattr(old,name)
OUT=Path(__file__).resolve().parent
INPUT=PREV/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend'
INPUT_SHA='9e8b29875fc6c215ef1e0fce4f582774f10b21596835d03763edb771443b11ec'
CANDIDATE=OUT/'RIGHT_HAND_OFFICIAL_L1_FIRST_WEB_TUNED_DESIGN_ONLY_R1.blend'
CASE_IDS=['ZERO','INDEX_MCP_45','CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3']
CASES=[{'case_id':'ZERO'}]+[c for c in old.cases() if c['case_id'] in CASE_IDS]
CASES.sort(key=lambda c:CASE_IDS.index(c['case_id']))
def open_file(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    ob=bpy.data.objects[MESH_NAME];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
    reset_pose(rig);bpy.context.view_layer.update()
    return ob,rig
def pose(rig,c):
    if c['case_id']=='ZERO': reset_pose(rig);bpy.context.view_layer.update()
    else: old.apply_case(rig,c)
def cameras(): return read(PREV/'STATIC_BIND_AND_REBASE_R1.json')['cameras']
