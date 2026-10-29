import sys, json, hashlib
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PREV=ROOT/'audits/pianovam_retarget_local_axis_mapping_correction_r1'
sys.path.insert(0,str(PREV))
import mapping_core as core
m=core.m
source=PREV/'RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend'
machine=json.loads((OUT/'MACHINE_CHECK_R1.json').read_text(encoding='utf-8'))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rest_details(rig):
    return {b.name:{'matrix':[list(r) for r in b.matrix_local],
        'settings':m.rna(b,omit=('color','collections')),
        'constraints':[m.rna(c,depth=2) for c in rig.pose.bones[b.name].constraints]} for b in rig.data.bones}
ob,rig=m.open_file(core.BASE)
native=m.product_payload(ob,rig)
shape=core.shape_payload(ob)
rest=rest_details(rig)
materials=[m.material_payload(x) for x in ob.data.materials if x]
ob,rig=m.open_file(source)
assert m.product_payload(ob,rig)==native and core.shape_payload(ob)==shape
assert rest_details(rig)==rest
assert [m.material_payload(x) for x in ob.data.materials if x]==materials
assert digest(native)==machine['native_payload_sha256']
assert digest(shape)==machine['shape_driver_payload_sha256']
for p,h in machine['files_after'].items():assert core.sha(ROOT/p)==h
result={'status':'PASS','independent_frozen_baseline_vs_source_test_payload_match':True,
    'runtime_diagnostic_payload_matches_frozen_baseline':True,
    'rest_inherit_rotation_scale_and_all_bone_settings_constraints_match':True,
    'same_corrective_and_driver_definitions':True,'materials_match':True,
    'bone_roll_authority':'Exact rest orientation matrices retained; no edit-mode reads/setters needed.',
    'all_input_hashes_unchanged':True,'no_file_saved_or_modified':True}
(OUT/'INDEPENDENT_ASSET_PROTECTION_R1.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('INDEPENDENT_PROTECTION_PASS')
