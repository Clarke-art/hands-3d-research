"""Read-only historical operation replay in RAM. Historical save section excluded.
No alternate engineering operation, candidate, or source-shape rebuild is executed.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,bmesh,numpy as np
src=ROOT/'production_spec/stage4_blender/scripts/stage4a_r2_base.py'
text=src.read_text(encoding='utf-8-sig').split('# ==================================================================== 9. SAVE')[0]
assert 'save_as_mainfile' not in text
ns={};ancestry=[];events=[];snapshots=[]
def state(bm,name):
 vs=list(bm.verts);ix={v:i for i,v in enumerate(vs)}
 return {'name':name,'local_m':[list(v.co) for v in vs],'faces':[[ix[v] for v in f.verts] for f in bm.faces],'ancestry':[{str(k):float(w) for k,w in ancestry[i].items()} for i,v in enumerate(vs)]}
def tracked_subdivide(bm,**kw):
 if not ancestry:
  ancestry.extend({i:1.} for i,v in enumerate(bm.verts))
  snapshots.append(state(bm,'L1_NORMALIZED_BEFORE_CON1'))
 edges=[(e.verts[0].index,e.verts[1].index,e.verts[0].co.copy(),e.verts[1].co.copy()) for e in kw['edges']]
 before=list(bm.verts);r=bmesh.ops.subdivide_edges(bm,**kw)
 records=[]
 for idx,v in enumerate(bm.verts):
  if idx<len(before):continue
  matches=[]
  for a,b,p,q in edges:
   d=q-p;t=(v.co-p).dot(d)/d.length_squared if d.length_squared else 0.
   if -1e-6<=t<=1+1e-6 and (v.co-(p+d*t)).length<1e-7:matches.append((a,b,t))
  assert len(matches)==1,('nonunique split parent',list(v.co),len(matches))
  a,b,t=matches[0];weights={}
  for parent,s in [(a,1-t),(b,t)]:
   for i,w in ancestry[parent].items():weights[i]=weights.get(i,0)+w*s
  ancestry.append(weights);records.append({'vertex_id':idx,'pre_projection_local_m':list(v.co),'L1_ancestry':{str(k):w for k,w in weights.items()},'parent_edge_fraction':t})
 events.append({'label':ns.get('label','see snapshots'),'new_vertices':records})
 return r
text=text.replace('bmesh.ops.subdivide_edges(bm,','tracked_subdivide(bm,')
ns['tracked_subdivide']=tracked_subdivide
def trace(frame,event,arg):
 if frame.f_code.co_filename==str(src) and event=='return' and frame.f_code.co_name=='insert_loop' and arg and arg.get('accepted'):
  events[-1]['label']=arg['label'];events[-1]['receipt']=arg
  snapshots.append(state(ns['bm'],arg['label']))
 return trace
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'production_spec/stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend'),load_ui=False,use_scripts=False)
sys.argv=['audit','--',str(OUT/'NEVER_SAVED.blend'),str(OUT)]
sys.settrace(trace)
exec(compile(text,str(src),'exec'),ns)
sys.settrace(None)
# Pole relocation creates replacement BMeshes. Preserve ancestry by the unchanged vertex order.
final=ns['me'];last=snapshots[-1]
hist=read(OUT/'RAW_SOURCE_GEOMETRY.json')['stages']['STAGE4A_R2_BASE']
coords=[list(v.co) for v in final.vertices];faces=[list(f.vertices) for f in final.polygons]
assert coords==hist['local_m'] and faces==hist['faces'],'Replay must equal historical frozen base exactly'
dump('HISTORICAL_OPERATION_RAM_REPLAY.json',{'historical_script':str(src.relative_to(ROOT)),'script_sha256':sha(src),'exact_final_coordinates_and_native_face_cycles_match':True,'snapshots':snapshots,'events':events,'final_local_m':coords,'final_faces':faces,'final_ancestry':last['ancestry'],'core_moves':ns['CORE_MOVES'],'midline_moves':ns['MIDLINE_MOVES'],'blend_saves':0,'alternate_operation_execution':0})
print('EXACT HISTORICAL RAM REPLAY VERIFIED',len(snapshots),flush=True)
