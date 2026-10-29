import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mapping_core import *
ob,rig=m.open_file(BASE);native=m.product_payload(ob,rig);shape=shape_payload(ob);materials=[m.material_payload(x) for x in ob.data.materials if x]
a=read(OUT/'PIANOVAM_AXIS_CORRECTED_ACTION_R1.json');test=ROOT/a['new_test_blend'];ob,rig=m.open_file(test)
assert m.product_payload(ob,rig)==native and shape_payload(ob)==shape and [m.material_payload(x) for x in ob.data.materials if x]==materials
action=bpy.data.actions[a['new_action']];curves=[f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
assert len(curves)==64 and all(len(fc.keyframe_points)==421 and 'rotation_quaternion' in fc.data_path and '_TIP_' not in fc.data_path for fc in curves)
assert sha(BASE)==BASE_SHA and sha(OLD)==OLD_SHA and sha(test)==a['new_test_sha256']
dump('SAVED_ASSET_PROTECTION_VERIFICATION_R1.json',{'baseline_source_sha_unchanged':True,'old_asset_sha_unchanged':True,'new_saved_test_sha_matches':True,'mesh_basis_weights_uv_materials_modifiers_object_transforms_rest_bones_hierarchy_shape_corrective_driver_exact':'PASS','new_action_quaternion_channels':len(curves),'keys_per_channel':421,'TIP_channels':0,'materials_exact_after_independent_reopen':True,'no_asset_written_during_verification':True})
print('SAVED_PAYLOAD_VERIFIED_ALL_PROTECTED_EXACT',flush=True)
