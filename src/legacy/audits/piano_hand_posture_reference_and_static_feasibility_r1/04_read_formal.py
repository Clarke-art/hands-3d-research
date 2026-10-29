import sys,json,hashlib,importlib.util,ast
sys.dont_write_bytecode=True
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';PRE=P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1'
R=json.loads((OLD/'RIG_CANONICAL_PROBE_R1.json').read_text())
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
tree=ast.parse((PRE/'04_hands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'intrinsic','exec'))
out={}
for s,c in R.items():
 source=ROOT/c['baseline'];assert hashlib.sha256(source.read_bytes()).hexdigest()==c['baseline_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);rig=bpy.data.objects[c['rig']];ob=bpy.data.objects[c['mesh']];h.neutral(rig);rig.animation_data_clear()
 V,_=h.coords(ob);C=np.array(c['native_to_canonical']);actual=V@C[:3,:3].T+C[:3,3];delta=float(np.max(np.linalg.norm(actual-np.array(c['rest_verts']),axis=1))*1000)
 identity=hashlib.sha256(json.dumps(intrinsic(ob,rig),sort_keys=True,separators=(',',':')).encode()).hexdigest()
 out[s]={'baseline_sha256':c['baseline_sha256'],'fresh_read_vertex_count':len(V),'fresh_read_bone_count':len(rig.data.bones),'canonical_rest_mesh_max_delta_mm':delta,'intrinsic_static_identity_matches':identity==c['static_identity'],'saved_any_blend':False};assert delta<.001 and identity==c['static_identity']
(P/'FORMAL_ASSET_READBACK_R1.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(out)
