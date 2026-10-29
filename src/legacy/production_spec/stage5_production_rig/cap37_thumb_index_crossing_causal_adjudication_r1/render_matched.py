import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from causal_common import *
import bpy,math
from mathutils import Vector
sys.path.append(str(S6/'stage6b_r1c/scripts'))
import r1c_pen_common as RASP
from types import SimpleNamespace
C=SimpleNamespace(MM=1000.)
d=read(OUT/'CAUSAL_COORDINATE_EVIDENCE.json');on=read(OUT/'SELECTED_ONSET_VISUAL_COORDINATES.json');POLY=d['faces'];V0=[Vector(p) for p in d['native_bind_world_m']]
TRIS=RASP.tris_of(POLY,V0);LIGHT=Vector((.42,-.30,.85)).normalized();W_=1500;H_=1100
fn=reuse(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['fit_view','shade','draw_solid'],globals())
labels=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')['membership']['vertex_labels'];digitids=sorted(int(v) for v in labels)
REND=OUT/'renders';REND.mkdir(exist_ok=True);views={};outputs=[]
assets=list(ASSETS)
def view(key,ids,positions,dir,minhw=0):
 cen=sum((V0[v] for v in ids),Vector())/len(ids);pts=[p[v] for p in positions for v in ids]+[V0[v] for v in ids]
 vw=fit_view(cen,dir,(0,0,1),pts,1.35)
 vw=RASP.View(cen,dir,(0,0,1),max(vw.hw*1000,minhw),1500,1100)
 views[key]={'centre_world_m':list(vw.c),'direction':list(vw.d),'up':list(vw.u),'half_width_mm':vw.hw*1000,'W':1500,'H':1100,'same_for_all_assets_and_selected_angles':True,'lighting':list(LIGHT),'shading':'Frozen R1E 0.30+0.70*abs(normal dot LIGHT)'}
 return vw
def paint_pair(cv,vw,V,pair,solid=False):
 for fi in pair['faces']:
  p=POLY[fi];col=(1,.45,.24) if fi==pair['faces'][0] else (.3,.7,1)
  if solid:
   for fj,t in TRIS:
    if fj==fi:cv.tri(vw.proj(V[t[0]]),vw.proj(V[t[1]]),vw.proj(V[t[2]]),shade(RASP.face_normals(V,[p])[0]),col)
  for j in range(len(p)):cv.line(vw.proj(V[p[j]]),vw.proj(V[p[(j+1)%len(p)]]),col,2,1)
 for fa,ta in TRIS:
  if fa!=pair['faces'][0]:continue
  for fb,tb in TRIS:
   if fb!=pair['faces'][1]:continue
   pts,ok=RASP.tri_tri_intersection([V[v] for v in ta],[V[v] for v in tb])
   if ok:
    for p in pts:cv.px(*vw.proj(p)[:2],(.1,1,.2),5,1)
    if len(pts)>1:cv.line(vw.proj(pts[0]),vw.proj(pts[1]),(.1,1,.2),2)
def section(cv,vw,V,centre):
 # Actual triangle/plane clipping, fixed world-Z plane across the three assets.
 z=centre.z
 for fi,t in TRIS:
  pts=[]
  for j in range(3):
   a=V[t[j]];b=V[t[(j+1)%3]];da=a.z-z;db=b.z-z
   if da*db<0:pts.append(a+(b-a)*(da/(da-db)))
  if len(pts)==2:
   lab={labels.get(str(v)) for v in POLY[fi]};col=(1,.45,.24) if lab=={'THUMB'} else (.3,.7,1) if lab=={'INDEX'} else (.55,.55,.55)
   cv.line(vw.proj(pts[0]),vw.proj(pts[1]),col,2)
def save(cv,key,a,style,pair,angle):
 RASP.text(cv,24,20,f'{pair["id"]}  {a}  {style.upper()}',3)
 RASP.text(cv,24,60,f'{pair["bone"]} LOCAL X -{angle} DEG - MATCHED CAMERA / LIGHT / SCALE',2)
 RASP.text(cv,24,86,'EVIDENCE ONLY - NO PRODUCTION EDIT - CONTACT ACCEPTABILITY PENDING HUMAN',2)
 RASP.text(cv,24,1050,'ORANGE THUMB / BLUE INDEX / GREEN CROSSING (FORENSIC OVERLAYS ONLY)',2)
 file=f'{key}__{a}__{style}.png';RASP.save(cv,file,str(REND));outputs.append({'pair':pair['id'],'pose':pair['pose'],'angle_deg':angle,'asset':a,'style':style,'file':'renders/'+file,'view_key':key})
for pair in PAIRS:
 pid=pair['id'];pose=pair['pose'];terminal=pose+'__'+str(pair['max_angle']);actual={a:[Vector(p) for p in d['actual_endpoints_world_m'][a][terminal]] for a in assets}
 selected=on['selected_angles_by_pair'][pid];samples={a:{ang:[Vector(p) for p in on['full_mesh_positions_world_m'][a][pose+'__'+str(ang)]] for ang in selected} for a in assets}
 pts=list(actual.values())+[v for s in samples.values() for v in s.values()];ids=sorted({v for part in d['patches'][pid] for v in part['one_ring_same_frozen_label_vertex_ids']});core=sorted({v for f in pair['faces'] for v in POLY[f]})
 cameras={'full_hand':view(pid+'__full_hand',list(range(len(V0))),pts,(.55,.42,.72)), 'thumb_index_close':view(pid+'__thumb_index_close',digitids,pts,(.62,.35,.70)), 'surface_solid':view(pid+'__surface_solid',ids,pts,(.92,.25,.30),18),'wire_overlay':view(pid+'__wire_overlay',ids,pts,(.62,.35,.70),18),'isolated_pair':view(pid+'__isolated_pair',core,pts,(.62,.35,.70),10),'section':view(pid+'__section',ids,pts,(0,0,1),18)}
 sec_centre=sum((actual['R2'][v] for v in core),Vector())/len(core);views[pid+'__section']['plane_world_z_m']=sec_centre.z
 for a,V in actual.items():
  for style,vw in cameras.items():
   cv=RASP.Canvas(1500,1100);key=pid+'__'+style
   if style=='isolated_pair':paint_pair(cv,vw,V,pair,True)
   elif style=='section':section(cv,vw,V,sec_centre)
   else:
    draw_solid(cv,vw,V,TRIS)
    if style=='wire_overlay':
     for part in d['patches'][pid]:
      for k in part['one_ring_edge_ids']:
       u,v=d['edges'][k];cv.line(vw.proj(V[u]),vw.proj(V[v]),(.8,.8,.8),1,.7)
     paint_pair(cv,vw,V,pair)
   save(cv,key,a,style,pair,pair['max_angle'])
  for ang,V in samples[a].items():
   cv=RASP.Canvas(1500,1100);vw=cameras['wire_overlay'];draw_solid(cv,vw,V,TRIS);paint_pair(cv,vw,V,pair)
   key=pid+'__onset_'+str(ang);views[key]=dict(views[pid+'__wire_overlay']);save(cv,key,a,'onset_surface_overlay',pair,ang)
 print('Matched evidence rendered',pid,flush=True)
dump('VISUAL_EVIDENCE_MANIFEST.json',{'outputs':outputs,'views':views,'renderer_function_AST_hashes':fn,'same_pose_camera_light_scale_for_each_comparison':True,'camera_fit':'Bind-centred fit to union of all three candidates / selected sweep samples; single shared scale per view. Full hand includes all vertices; close includes frozen bounded THUMB/INDEX domain.','plain_surface_views':['full_hand','thumb_index_close','surface_solid'],'forensic_views':['wire_overlay','isolated_pair','section','onset_surface_overlay'],'section':'Actual triangle/plane intersection, shared world-Z plane through R2 terminal pair centroid; no inferred tissue thickness.','production_saves':0,'new_pose_evaluations':0})
