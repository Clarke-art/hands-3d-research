"""Historical solid z-buffer renderer; actual measured coordinates only.
No production mesh, material, modifier, bone or group writes.
"""
from common import *
import bpy,math,os,numpy as np
from types import SimpleNamespace
from mathutils import Vector
MM=1000.;W_,H_=1200,900;SEV_MIN=3.;C=SimpleNamespace(MM=MM)
path=S6/'stage6b_r1c/scripts/r1c_pen_common.py'
rns={'bpy':bpy,'math':math,'np':np,'Vector':Vector,'MM':MM,'os':os}
names=['ortho_basis','View','Canvas','face_normals','save']
nodes=[n for n in ast.parse(path.read_text(encoding='utf-8-sig')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),rns)
RASP=SimpleNamespace(**{n:rns[n] for n in names});LIGHT=Vector((.42,-.30,.85)).normalized()
renderer_sources=[{'source':ref(path),'function_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes}}]
renderer_sources.append(reuse(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['shade','draw_solid','strain_fn'],globals()))
OLD=read(HIST/'POSED_COORDINATES_R1.json');oldpositions=OLD['positions_world_m'];POLY=OLD['faces']
TRIS=[]
for fi,p in enumerate(POLY):
 for k in range(1,len(p)-1):TRIS.append((fi,(p[0],p[k],p[k+1])))
frame=read(ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_RENDER_GEOMETRY_R1.json')['frame']
M=read(TARGETED/'MEASUREMENT_DOMAIN_MANIFEST_R1.json');ROIIDS=sorted(set(APPROVED54)|set(M['first_fixed_outer_ring']))
DORS=Vector((.631289124,.775318801,-.0188387)).normalized()
manifest=[];REND=OUT/'renders';REND.mkdir(exist_ok=True)
def fit_matched(A,B,ids,direction,up=Vector((0,0,1)),margin=1.12):
 d=Vector(direction).normalized();r,u=RASP.ortho_basis(d,Vector(up));ps=[arr[i] for arr in [A,B] for i in ids]
 x=[p.dot(r) for p in ps];y=[p.dot(u) for p in ps];z=[p.dot(d) for p in ps]
 cen=r*((min(x)+max(x))/2)+u*((min(y)+max(y))/2)+d*((min(z)+max(z))/2)
 hw=max((max(x)-min(x))/2,(max(y)-min(y))/2*W_/H_,.003)*margin
 return RASP.View(cen,d,u,hw*MM,W_,H_)
def render_case(cid,V,rawbind,localids,nailids,capids,webids,crossings):
 global V0
 V0=rawbind
 old=[Vector(p) for p in oldpositions[cid]];jobs=[('FULL_SOLID',list(range(len(V))),-DORS,None,None)]
 ang=int(cid.rsplit('_',1)[1]);important=ang==45 or cid in ['IDX_MCP_15','IDX_MCP_30','TH_IP_15','RNG_MCP_15','RNG_MCP_30'] or any(z['hard_blocker'] for z in crossings)
 if important:
  jobs.extend([('LOCAL_SOLID',sorted(localids),-DORS,None,None),('LOCAL_PALMAR_SOLID',sorted(localids),DORS,None,None),('LOCAL_STRAIN',sorted(localids),-DORS,None,'STRAIN')])
 if ang==45:jobs.append(('NAIL_SOLID',sorted(nailids),-DORS,None,None))
 if cid.startswith('TH_') or cid.startswith('IDX_MCP'):
  jobs.append(('CAP37_SOLID',sorted(capids),Vector((-.62,-.35,-.70)),None,None))
 if cid.startswith('IDX_MCP') or cid in ['TH_MCP_45','TH_IP_45']:jobs.append(('FIRST_WEB_SOLID',sorted(webids),Vector((-.92,-.25,-.30)),None,None))
 if cid in ['RNG_MCP_15','RNG_MCP_30','RNG_MCP_45']:
  dor=-Vector(frame['outward']);up=Vector(frame['y'])
  jobs.extend([('DORSAL_MCP_CLOSE_SOLID',ROIIDS,dor,None,None),('DORSAL_MCP_GRAZING_SOLID',ROIIDS,(dor*.22+Vector(frame['x'])*.98).normalized(),None,None),('DORSAL_MCP_WIRE_STRAIN',ROIIDS,dor,None,'STRAIN')])
 for cr in crossings:
  if cr['hard_blocker'] or cr['acceptance'].startswith('KNOWN_'):
   a,b=cr['face_ids'];ids=sorted(set(POLY[a])|set(POLY[b]));name=f'PAIR_{a}_{b}'
   norm=(V[POLY[a][1]]-V[POLY[a][0]]).cross(V[POLY[a][2]]-V[POLY[a][0]]).normalized()
   direction=-(norm+DORS*.55).normalized()
   jobs.extend([(name+'_CONTEXT',ids,direction,{a:(.93,.31,.14),b:(.19,.57,.94)},None),(name+'_ISOLATED',ids,direction,{a:(.93,.31,.14),b:(.19,.57,.94)},'ISOLATED')])
 for style,ids,direction,highlight,mode in jobs:
  up=Vector(frame['y']) if style.startswith('DORSAL_MCP') else Vector((0,0,1))
  margin=1.4 if 'ISOLATED' in style or 'CONTEXT' in style else 1.18
  vw=fit_matched(old,V,ids,direction,up,margin)
  for asset,P in [('PRE_DONOR_HISTORICAL',old),('CURRENT_FRESH',V)]:
   cv=RASP.Canvas(W_,H_);tris=[t for t in TRIS if t[0] in highlight] if mode=='ISOLATED' else TRIS
   fcol=(lambda fi:highlight.get(fi,(.72,.72,.72))) if highlight else strain_fn(P) if mode=='STRAIN' else None
   draw_solid(cv,vw,P,tris,fcol)
   if style=='DORSAL_MCP_WIRE_STRAIN':
    for ei in M['outer_support_edge_ids']:
     a,b=OLD['edges'][ei];cv.line(vw.proj(P[a]),vw.proj(P[b]),(.10,.10,.12),0,.7)
   if mode=='ISOLATED':
    cr=next(z for z in crossings if z['face_ids']==list(highlight))
    points=cr.get('pts',[]) if asset=='CURRENT_FRESH' else next((z['pts'] for z in read(HIST/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')['cases'][cid]['crossings'] if z['face_ids']==cr['face_ids']),[])
    for p in points:
     x,y,z=vw.proj(Vector(p));cv.px(x,y,(.18,.95,.45),4,1)
   name=f'{cid}__{style}__{asset}.png';RASP.save(cv,name,str(REND))
   manifest.append({'path':'renders/'+name,'case_id':cid,'asset':asset,'style':style,'view_key':cid+'__'+style,'camera_centre_m':list(vw.c),'camera_direction':list(vw.d),'camera_up':list(vw.u),'half_width_mm':vw.hw*MM,'resolution':[W_,H_],'focus_vertex_ids':ids,'solid_native_surface':True,'isolated_pair_supplementary':mode=='ISOLATED','current_coordinates_fresh_depsgraph':True,'old_coordinates_source':ref(HIST/'POSED_COORDINATES_R1.json'),'shading':'Historical R1E flat native solid z buffer; same fixed light and facet topology.','diagnostic_color_is_gate':False})
 dump('EVIDENCE_RENDER_MANIFEST_R1.json',{'renders':manifest,'render_count':len(manifest),'renderer_functions':renderer_sources,'matched_current_vs_pre_donor':True,'production_geometry_edits':0,'production_save_calls':0,'rendered_before_pose_reset':True})
