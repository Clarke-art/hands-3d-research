"""Recover already-baked RSSF coordinate correspondence, not a new pose run."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np
from mathutils import Vector
src=ROOT/'production_spec/stage4_blender/scripts/stage4b_rssf_r2.py'
txt=src.read_text(encoding='utf-8-sig').split('# =============================================================== 6. LBS deform')[0]
assert 'save_as_mainfile' not in txt
path=ROOT/'production_spec/stage4_blender/stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend'
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
sys.argv=['audit','--',str(OUT/'NEVER_SAVED_RSSF.blend'),str(OUT)]
ns={};exec(compile(txt,str(src),'exec'),ns)
W=ns['W'];raw=ns['raww'];names=ns['BNAME'];QW=ns['QW'];PH=ns['PH'];BH=ns['BH'];pred=[];jac=[]
for i,p in enumerate(W):
 J=np.zeros((3,3));q=np.zeros(3)
 for name in names:
  w=raw[name][i]
  if w<=1e-6:continue
  rot=np.array(QW[name]);J+=w*rot;q+=w*(np.array(PH[name])+rot@(np.array(p)-np.array(BH[name])))
 pred.append(q.tolist());jac.append(J.tolist())
S=read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages'];B=np.array(S['STAGE4B_RSSF']['canonical_world_m']);err=np.linalg.norm(np.array(pred)-B,axis=1)*1000
native=[]
for i,p in enumerate(W):
 acc=Vector((0,0,0))
 for name in names:
  w=raw[name][i]
  if w>1e-6:acc+=w*(PH[name]+QW[name]@(p-BH[name]))
 native.append(list(ns['MW'].inverted()@acc))
assert native==S['STAGE4B_RSSF']['local_m'],'Actual historical mathutils float32 reconstruction must be exact'
dump('HISTORICAL_RSSF_COORDINATE_CORRESPONDENCE.json',{'script':str(src.relative_to(ROOT)),'script_sha256':sha(src),'per_vertex_linear_part':jac,'binary64_linear_reconstruction_vs_stored_float32_max_mm':float(err.max()),'actual_native_mathutils_forward_reconstruction_exact':True,'existing_RSSF_state_recovered':True,'new_RSSF_solution':False,'blend_saves':0,'semantics':'Push donor-derived rest-shape delta through the same frozen per-vertex linear transform used to bake Stage4B. Retain current positions as anchor; no RSSF re-solve or downstream pose qualification.'})
print('RSSF historical correspondence reconstructed',err.max(),flush=True)
