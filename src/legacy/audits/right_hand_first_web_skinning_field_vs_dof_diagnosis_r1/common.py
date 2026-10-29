import sys,importlib.util,ast,json,hashlib,math,copy
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'audits/right_hand_first_web_topology_causal_probe_r1'
spec=importlib.util.spec_from_file_location('latest_authority_harness',PREV/'common.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
for n in ['bpy','np','Vector','Matrix','Quaternion','m','core','BASE','SOURCE','ACTION','FROZEN_SHA','APPROVED_ACTION_SHA','PATCH_IDS','action_payload','open_frozen','neutral','motion','coords','values','shape_state']:globals()[n]=getattr(h,n)
m.old.lib.OUT=OUT
PHASE='RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1'
FRAMES=[110,127,130,160,176,205]
FOLDED=[127,130,160,205];SMOOTH=[110,176]
CANDIDATE=OUT/'RIGHT_HAND_FIRST_WEB_WEIGHT_FIELD_PROBE_R1.blend'
DELTA=.02
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v.item())+'\n',encoding='utf-8')
def weights(ob):
    W=np.zeros((len(ob.data.vertices),len(ob.vertex_groups)))
    for v in ob.data.vertices:
        for g in v.groups:W[v.index,g.group]=g.weight
    return W
def protected_inputs():
    j=read(PREV/'FINAL_ASSET_PROTECTION_R1.json');out={r['path']:r['actual_sha256'] for r in j['protected_inputs']}
    out[j['production_pointer']['path']]=j['production_pointer']['sha256']
    for n in ['RIGHT_HAND_FIRST_WEB_TOPOLOGY_CAUSAL_PROBE_R1_REPORT.md','ATTRIBUTION_AND_RECONCILIATION_R1.json','CANDIDATE_DESIGN_R1.json','PROBE_MEASUREMENTS_R1.json','CANDIDATE_VERIFICATION_R1.json','FINAL_ASSET_PROTECTION_R1.json','common.py']:
        out[(PREV/n).relative_to(ROOT).as_posix()]=sha(PREV/n)
    out[(PREV/'RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend').relative_to(ROOT).as_posix()]=read(PREV/'CANDIDATE_VERIFICATION_R1.json')['candidate_sha256']
    for p,v in out.items():assert sha(ROOT/p)==v,p
    return out
def verify_inputs(x):
    for p,v in x.items():assert sha(ROOT/p)==v,p
def topology_roi(ob):
    # Reuse only the previous ROI-selection functions, not the topology experiment.
    ns={}
    nodes=[n for n in ast.parse((PREV/'02_probe.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['build_roi','boundary_loop']]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'read_only_same_ROI_selection','exec'),ns)
    faces=[list(p.vertices) for p in ob.data.polygons];roi,fi=ns['build_roi'](faces,PATCH_IDS,2);loop=ns['boundary_loop'](faces,fi)
    boundary=loop[0] if len(loop)==1 and isinstance(loop[0],list) else loop
    assert len(roi)==234 and len(boundary)==70
    return sorted(roi),list(boundary)
def render(ob,label,f):
    cams=read(PREV/'PROBE_MEASUREMENTS_R1.json')['cameras'][str(f)]
    V,F=m.evaluate(ob,ob.matrix_world);rr=m.Renderer(cams,'renders');rr.sc.display.shading.shadow_intensity=0
    rr.draw(label,f'F{f:03}',V,F,list(cams));rr.dispose();return rr.records
def native_no_weights(ob,rig):
    p=m.product_payload(ob,rig);p.pop('weights');return p
