"""Reuse authority readers, ROI and actual Blender evaluation; no historical experiment execution."""
import sys, importlib.util, shutil
from pathlib import Path
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PREV = ROOT / 'audits/right_hand_first_web_skinning_field_vs_dof_diagnosis_r1'
TOPO = ROOT / 'audits/right_hand_first_web_topology_causal_probe_r1'
spec = importlib.util.spec_from_file_location('inherited_field_readers', PREV / 'common.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
for n in ['bpy','np','Vector','Matrix','m','BASE','SOURCE','ACTION','FROZEN_SHA','APPROVED_ACTION_SHA','PATCH_IDS','action_payload','open_frozen','neutral','motion','coords','values','shape_state','weights','native_no_weights','topology_roi','read','sha','digest']:
    globals()[n] = getattr(h,n)
m.old.lib.OUT = OUT
PHASE = 'RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1'
CANDIDATE = OUT / 'RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_PROBE_R1.blend'
FRAMES = [110,127,130,160,176,205]
VIEWS = ['FIRST_WEB_OBLIQUE','PALMAR_THENAR_CLOSE']
def dump(n,x):
    (OUT/n).write_text(__import__('json').dumps(x,ensure_ascii=False,indent=2,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v.item())+'\n',encoding='utf-8')
def protected_inputs():
    result = h.protected_inputs()
    # Preserve all durable outputs of both authority rounds, including their candidates.
    for folder in [PREV,TOPO]:
        for p in folder.rglob('*'):
            if p.is_file() and not any(part in ['_tmp','__pycache__'] for part in p.relative_to(folder).parts):
                result[p.relative_to(ROOT).as_posix()] = sha(p)
    return result
def verify_inputs(before):
    for p,expected in before.items(): assert sha(ROOT/p)==expected,p
def stats(x):
    return {'mean':float(np.mean(x)),'median':float(np.median(x)),'max':float(np.max(x))}
def render(ob,f):
    cams = read(TOPO/'PROBE_MEASUREMENTS_R1.json')['cameras'][str(f)]
    V,F = m.evaluate(ob,ob.matrix_world)
    rr = m.Renderer(cams,'renders')
    rr.sc.display.shading.shadow_intensity = 0
    rr.draw('FULL_VECTOR_PROBE',f'F{f:03}',V,F,VIEWS)
    rr.dispose()
    return rr.records
