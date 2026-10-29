import bpy,json,sys,hashlib,importlib.util,ast
from pathlib import Path
import numpy as np
from mathutils import Matrix
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PRE=P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
ex=read(PRE/'HAND_EXTRACTION_R1.json');out={}
sp=importlib.util.spec_from_file_location('identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
tree=ast.parse((PRE/'04_hands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intrinsic'],type_ignores=[]),'intrinsic','exec'))
for s,c in ex['cfg'].items():
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/c['baseline']),load_ui=False,use_scripts=False);rig=bpy.data.objects[c['rig']];ob=bpy.data.objects[c['mesh']];h.neutral(rig);rig.animation_data_clear();Q=np.array(ex['frames'][s]['rotation']);w=np.array(ex['frames'][s]['native_wrist']);C=np.eye(4);C[:3,:3]=Q;C[:3,3]=-Q@w
 V,_=h.coords(ob)
 out[s]={'baseline':c['baseline'],'baseline_sha256':c['sha'],'mesh':c['mesh'],'rig':c['rig'],'native_to_canonical':C.tolist(),'static_identity':hashlib.sha256(json.dumps(intrinsic(ob,rig),sort_keys=True,separators=(',',':')).encode()).hexdigest(),'bones':{b.name:{'matrix':(<REDACTED_EMAIL>(b.matrix_local)).tolist(),'parent':b.parent.name if b.parent else None,'length':b.length,'head':((np.array(b.head_local)-w)@Q.T).tolist(),'tail':((np.array(b.tail_local)-w)@Q.T).tolist()} for b in rig.data.bones},'vertices':len(ob.data.vertices),'bone_count':len(rig.data.bones),'rest_verts':((V-w)@Q.T).tolist(),'faces':[list(f.vertices) for f in ob.data.polygons],'smooth':[f.use_smooth for f in ob.data.polygons]}
 print(s,[(b['parent'],n,np.round(b['head'],3).tolist()) for n,b in out[s]['bones'].items()],flush=True)
(P/'RIG_CANONICAL_PROBE_R1.json').write_text(json.dumps(out),encoding='utf-8')
