"""Render previously measured coordinates only, using the historical solid rasterizer."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualification_common import *
import bpy,math
from mathutils import Vector
sys.path.append(str(S6/'stage6b_r1c/scripts'))
sys.path.append(str(S5/'stage5b_r1e/scripts'))
import r1c_pen_common as RASP
import s5b_r1e_common as C
saved=read(OUT/'STATIC_LIVE_REOPEN_PAYLOAD.json');matrix=read(OUT/'TARGETED_FIXTURE_MATRIX.json')
coords=read(OUT/'POSED_COORDINATE_EVIDENCE.json')['positions_world_m'];data=read(OUT/'TARGETED_DEFORMATION_MACHINE_EVIDENCE.json')['results']
V0=[Vector(p)/1000 for p in saved['mesh']['positions_world_mm']];POLY=saved['mesh']['faces'];EDGES=saved['mesh']['edges']
TRIS=RASP.tris_of(POLY,V0);LIGHT=Vector((.42,-.30,.85)).normalized();W_,H_=1500,1100;SEV_MIN=C.SEVERE_MIN_BIND_MM
reuse=reuse_functions(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['fit_view','shade','draw_solid','strain_fn'],globals())
REND=OUT/'renders';REND.mkdir(exist_ok=True)
assets=list(coords);views=[];outputs=[]
cases=[('CAP37','TH_IP_30'),('CAP37','TH_IP_45'),('CAP37','IDX_MCP_45'),('OLD_CAP9','TH_IP_45'),('OLD_CAP9','IDX_MCP_45'),('FIRST_WEB','FULL_OPP_L3'),('FRESH_R3_TRANSITION_COLLAR','CMC_OPP_30'),('FRESH_R3_TRANSITION_COLLAR','CMC_MCP_L3'),('EDGE5879','CMC_MCP_L3')]
dirs={'CAP37':(.62,.35,.70),'OLD_CAP9':(.62,.35,.70),'FIRST_WEB':(.92,.25,.30),'FRESH_R3_TRANSITION_COLLAR':(.30,.72,.62),'EDGE5879':(.92,.25,.30)}
def record_view(key,vw,ids,cid):
    clipped={a:sum(not(12<=vw.proj(Vector(coords[a][cid][v]))[0]<=1488 and 140<=vw.proj(Vector(coords[a][cid][v]))[1]<=1010) for v in ids) for a in assets}
    row={'key':key,'centre_world_m':list(vw.c),'direction':list(vw.d),'up':list(vw.u),'half_width_mm':vw.hw*1000,'W':1500,'H':1100,'shared_across_all_candidates':True,'core_clipped_vertex_counts':clipped,'lighting':list(LIGHT),'shading':'R1E 0.30+0.70*abs(normal dot LIGHT)'}
    views.append(row)
def marker(cv,vw,V,v,col=(.95,.95,.3)):
    x,y,z=vw.proj(V[v]);cv.px(x,y,col,3,1.0)
for name,cid in cases:
    f=matrix['fixtures'][name];ids=f['region'];core=f['core'];cen=sum((V0[v] for v in core),Vector())/len(core)
    margin=9.0 if name=='EDGE5879' else 3.4 if name=='FRESH_R3_TRANSITION_COLLAR' else 3.0
    vw=fit_view(cen,dirs[name],(0,0,1),[V0[i] for i in ids],margin)
    # A single shared wider frame only if the legacy bind fit clips a posed core.
    allpts=[Vector(coords[a][cid][i]) for a in assets for i in ids]+[V0[i] for i in ids]
    r,u=RASP.ortho_basis(Vector(dirs[name]),Vector((0,0,1)))
    need=max(max(abs((p-cen).dot(r)),abs((p-cen).dot(u))*1500/780) for p in allpts)*1.06
    if need>vw.hw: vw=RASP.View(cen,dirs[name],(0,0,1),need*1000,1500,1100)
    key=f'{name}__{cid}';record_view(key,vw,core,cid)
    for asset in assets:
        V=[Vector(p) for p in coords[asset][cid]];m=data[asset][cid]['fixtures'][name]
        for style in ['solid','strain']:
            cv=RASP.Canvas(1500,1100)
            draw_solid(cv,vw,V,TRIS,strain_fn(V) if style=='strain' else None)
            for v in core: marker(cv,vw,V,v)
            if name=='EDGE5879':
                a,b=EDGES[5879];cv.line(vw.proj(V[a]),vw.proj(V[b]),(1,.15,.1),3,1.0)
            if name=='FRESH_R3_TRANSITION_COLLAR':
                for k in f['boundary_edge_ids']:
                    a,b=EDGES[k];cv.line(vw.proj(V[a]),vw.proj(V[b]),(.1,.95,.35),2,1.0)
            RASP.text(cv,24,20,f'{name}  {cid}  {asset}  {style.upper()}',3)
            RASP.text(cv,24,60,'TARGETED EVIDENCE ONLY - MATCHED CAMERA, LIGHT, SCALE, POSE',2)
            RASP.text(cv,24,84,'CORE DOTS YELLOW - POSED SURFACE; NO PRODUCTION EDIT',2)
            RASP.text(cv,24,1050,f'SEVERE {m["severe_edge_count"]} - MIN AREA RATIO {m["min_face_area_ratio"]:.3f} - V2 CLASS A {m["visible_geometric_crossings_count"]}',2)
            fn=f'{key}__{asset}__{style}.png';RASP.save(cv,fn,str(REND));outputs.append({'fixture':name,'pose':cid,'asset':asset,'style':style,'file':'renders/'+fn,'view_key':key})
    print('Rendered matched fixture',key,flush=True)
# Exact failure face-pair isolation: supplementary to full solid surface views, never replaces them.
for cid,pair in [('TH_IP_30',[1225,2740]),('IDX_MCP_45',[1041,2735]),('IDX_MCP_45',[1226,2742])]:
    ids=sorted({v for fi in pair for v in POLY[fi]});cen=sum((V0[i] for i in ids),Vector())/len(ids)
    points=[Vector(coords[a][cid][i]) for a in assets for i in ids]+[V0[i] for i in ids]
    vw=fit_view(cen,(.62,.35,.70),(0,0,1),points,1.8)
    key=f'PAIR_{pair[0]}_{pair[1]}__{cid}';record_view(key,vw,ids,cid)
    for a in assets:
        V=[Vector(p) for p in coords[a][cid]];cv=RASP.Canvas(1500,1100)
        for fi,t in TRIS:
            if fi not in pair: continue
            n=RASP.face_normals(V,[POLY[fi]])[0];col=(.95,.45,.25) if fi==pair[0] else (.3,.65,.95)
            cv.tri(vw.proj(V[t[0]]),vw.proj(V[t[1]]),vw.proj(V[t[2]]),shade(n),col)
        for fi in pair:
            p=POLY[fi]
            for j in range(len(p)):cv.line(vw.proj(V[p[j]]),vw.proj(V[p[(j+1)%len(p)]]),(.95,.95,.95),1,1.0)
        pts=[]
        for fa,ta in TRIS:
            if fa!=pair[0]:continue
            for fb,tb in TRIS:
                if fb!=pair[1]:continue
                pp,ok=RASP.tri_tri_intersection([V[v] for v in ta],[V[v] for v in tb])
                if ok:
                    for p in pp: x,y,z=vw.proj(p);cv.px(x,y,(.1,1,.2),5,1)
                    pts+=pp
        RASP.text(cv,24,20,f'{cid}  {a}  FACE PAIR {pair[0]} / {pair[1]}',3)
        RASP.text(cv,24,60,'ISOLATED GEOMETRIC EVIDENCE - ORANGE THUMB / BLUE INDEX',2)
        RASP.text(cv,24,84,'GREEN = EXACT TRIANGLE CROSSING POINTS; WHITE = POSED POLYGON EDGES',2)
        RASP.text(cv,24,1050,'SUPPLEMENT TO FULL SURFACE VIEW - SAME CAMERA FOR ALL ASSETS',2)
        fn=f'{key}__{a}.png';RASP.save(cv,fn,str(REND));outputs.append({'fixture':'CAP37','pose':cid,'asset':a,'style':'pair_isolation','file':'renders/'+fn,'view_key':key,'face_pair':pair})
    print('Rendered isolated crossing',key,flush=True)
dump('VISUAL_EVIDENCE_MANIFEST.json',{'renderer_function_AST_hashes':reuse,'historical_renderer':str((S6/'stage6b_r1c/scripts/r1c_pen_common.py').relative_to(ROOT)),'views':views,'outputs':outputs,'historical_directions_and_lighting_preserved':True,'camera_fit_note':'Frozen corrected selector replaces obsolete cap/collar; bind centre fixed and scale shared across four candidates, widened once to contain every posed region. No per-candidate auto-fit. Pair isolation supplements full solid views.','production_writes':0,'new_pose_evaluations':0})
print('Render evidence complete; no pose evaluation or production save.')
