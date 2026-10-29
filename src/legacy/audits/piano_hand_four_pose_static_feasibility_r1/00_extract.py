import sys,json,hashlib,ast,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';R2=P.parent/'real_piano_reference_gap_closure_and_static_posture_probe_r2'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
before=read(R2/'PROTECTED_INPUTS_BEFORE_R2.json')
for p in R2.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:before[str(p.resolve())]=sha(p)
assert all(Path(p).is_file() and sha(Path(p))==v for p,v in before.items())
dump('PROTECTED_INPUTS_BEFORE_R1.json',before)
R=read(OLD/'RIG_CANONICAL_PROBE_R1.json')
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
tree=ast.parse((P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1/04_hands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'intrinsic','exec'))
out={}
for s,c in R.items():
 source=ROOT/c['baseline'];assert sha(source)==c['baseline_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);rig=bpy.data.objects[c['rig']];ob=bpy.data.objects[c['mesh']];rig.animation_data_clear();h.neutral(rig)
 identity=hashlib.sha256(json.dumps(intrinsic(ob,rig),sort_keys=True,separators=(',',':')).encode()).hexdigest();assert identity==c['static_identity']
 V,_=h.coords(ob);C=np.array(c['native_to_canonical']);v=V@C[:3,:3].T+C[:3,3];assert np.max(np.linalg.norm(v-np.array(c['rest_verts']),axis=1))<1e-6
 names=list(c['bones']);W=h.weights(ob,rig);wcols=[b.name for b in rig.data.bones];W=W[:,[wcols.index(n) for n in names]]
 mods=[{'type':m.type,'preserve_volume':bool(getattr(m,'use_deform_preserve_volume',False))} for m in ob.modifiers]
 out[s]={'baseline':str(source),'sha256':sha(source),'static_identity':identity,'bone_names':names,'rest_vertices_canonical':v.tolist(),'weights':W.tolist(),'modifiers':mods,'canonical_mesh_delta_mm':float(np.max(np.linalg.norm(v-np.array(c['rest_verts']),axis=1))*1000),'vertices':len(v),'bones':len(rig.data.bones),'saved_blend':False}
dump('FORMAL_INPUT_EXTRACTION_R1.json',out)
dump('INHERITED_INPUTS_R1.json',{'sources':{n:{'path':str(p),'sha256':sha(p)} for n,p in {'reference_manifest':R2/'REAL_PIANO_REFERENCE_MANIFEST_R2.md','posture_contract':R2/'NATURAL_PIANO_HAND_POSTURE_CONTRACT_R2.md','geometry':R2/'HAND_KEYBOARD_STATIC_FEASIBILITY_R2.json','keyboard':OLD/'KEYBOARD_88_KEY_TABLE_R1.json','keyboard_authority':OLD/'KEYBOARD_AUTHORITY_R1.json','canonical_rig':OLD/'RIG_CANONICAL_PROBE_R1.json','markers':OLD/'FINGERTIP_CONTACT_MARKERS_R1.json'}.items()},'reference_search_stop_loss':'REACHED','human_authorization':'BOUNDED_STATIC_POSTURE_EXPERIMENT_AUTHORIZED_CURRENT_USER_ATTACHMENT','not_biomechanical_proof':True})
print('EXTRACTED',len(before),'protected; hands',[(s,o['vertices'],o['bones'],o['modifiers']) for s,o in out.items()])
