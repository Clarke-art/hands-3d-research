"""Generate pending Human evidence from frozen native static extraction only."""
import sys
sys.dont_write_bytecode = True
import base64, collections, hashlib, heapq, html, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[2]
SRC = OUT.parent / 'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p):
    s = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): s.update(b)
    return s.hexdigest()
def dump(name, obj): (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf8')
BEFORE = read(OUT/'FROZEN_HASHES_BEFORE.json')
C = read(SRC/'NATIVE_THUMB_DISTAL_CAP_CANDIDATE_SET.json')
D = read(SRC/'_tmp/render_data.json')
N = D['native']; V = np.array(N['vertices_world_m']); F = N['faces']; E = N['edges']; L = D['labels']
CV = set(C['vertex_ids']); CF = set(C['face_ids']); OLD = D['current_cap9']; NF = set(D['thumb_nail_faces'])
NV = {v for fi in NF for v in F[fi]}; SEED = C['seed_vertex_id']; DOMAIN = set(C['graph_vertex_ids'])
IP = np.array(D['native_thumb']['joint_world_m']['IP']); TIP = V[SEED]
def unit(a): return a / np.linalg.norm(a)
TIPDIR = unit(TIP-IP)
assert len(CV)==48 and len(CF)==33 and SEED==284
assert CV == {v for fi in CF for v in F[fi]} and CV.isdisjoint(OLD)
assert DOMAIN == {i for i,x in enumerate(L) if x=='thumb'}
assert sha(ROOT/N['path']) == C['mesh_sha256'] == N['sha256']
assert C['vertex_ids']==D['native_cap'] and C['face_ids']==D['native_cap_faces']
adj = [[] for _ in V]
for a,b in E:
    if a in DOMAIN and b in DOMAIN:
        w = float(np.linalg.norm(V[a]-V[b])*1000)
        adj[a].append((b,w)); adj[b].append((a,w))
G = np.full(len(V), np.inf); G[SEED] = 0.; q = [(0.,SEED)]; pred = {}
while q:
    cost,a = heapq.heappop(q)
    if cost>G[a]: continue
    for b,w in adj[a]:
        if cost+w < G[b]: G[b]=cost+w; pred[b]=a; heapq.heappush(q,(G[b],b))
def path(v):
    p=[v]
    while p[-1]!=SEED: p.append(pred[p[-1]])
    return p[::-1]
edge_faces=collections.defaultdict(list); selected_edges=collections.defaultdict(list)
for fi,vs in enumerate(F):
    for a,b in zip(vs,vs[1:]+vs[:1]):
        e=tuple(sorted((a,b))); edge_faces[e].append(fi)
        if fi in CF: selected_edges[e].append(fi)
BE = sorted(e for e,fs in selected_edges.items() if len(fs)==1)
BV = {v for e in BE for v in e}
BF = {selected_edges[e][0] for e in BE}
bad_edges = [e for e,fs in selected_edges.items() if len(fs)>2]
ba=collections.defaultdict(list)
for a,b in BE: ba[a].append(b); ba[b].append(a)
loops=[]; unused=set(BE)
while unused:
    a,b=min(unused); seq=[a,b]; unused.remove((a,b))
    while seq[-1]!=seq[0]:
        opts=[v for v in ba[seq[-1]] if tuple(sorted((v,seq[-1]))) in unused]
        if not opts: break
        nxt=min(opts); unused.remove(tuple(sorted((seq[-1],nxt)))); seq.append(nxt)
    loops.append(seq)
inside=sorted(v for v in CV if G[v]<=9.0)
expanded=sorted(CV-set(inside))
assert abs(max(G[v] for v in CV)-C['max_selected_vertex_geodesic_mm'])<1e-8
assert all(L[v]=='thumb' for v in CV)
assert all(min(G[v] for v in F[fi])<=9 and set(F[fi])<=DOMAIN for fi in CF)
vrows=[]
for v in sorted(CV):
    fs=sorted(fi for fi in CF if v in F[fi])
    vrows.append({'vertex_id':v,'face_ids':fs,'world_m':V[v].tolist(), 'geodesic_distance_mm':float(G[v]),
        'native_branch':'THUMB','native_branch_provenance':'Independent native partition; no R3 labels',
        'nail_membership':v in NV,'tip_distance_mm':float(np.linalg.norm(V[v]-TIP)*1000),
        'tip_distance_metric':'Native Euclidean distance to seed v284; geodesic is separately recorded',
        'boundary_membership':v in BV,'boundary_edges':[list(e) for e in BE if v in e],
        'selection_class':'VERTEX_GEODESIC_LE_9MM' if v in inside else 'MIN_CORNER_FACE_EXPANSION_GT_9MM',
        'geodesic_seed_to_vertex_path':path(v),
        'qualifying_face_corners':[{ 'face_id':fi,'vertices_le_9mm':[a for a in F[fi] if G[a]<=9]} for fi in fs]})
frows=[]
for fi in sorted(CF):
    vs=F[fi]; center=V[vs].mean(0)
    frows.append({'face_id':fi,'vertex_ids':vs,'corner_geodesic_distances_mm':[{ 'vertex_id':v,'geodesic_distance_mm':float(G[v])} for v in vs],
        'geodesic_distance_mm_min_corner':float(min(G[vs])),'geodesic_distance_mm_max_corner':float(max(G[vs])),
        'geodesic_distance_semantics':'Face selection uses min corner; no centroid surface geodesic claimed',
        'native_branch':'THUMB','corner_native_branches':[L[v].upper() for v in vs],
        'nail_membership':fi in NF,'nail_corner_vertex_ids':sorted(set(vs)&NV),
        'tip_distance_mm':float(np.linalg.norm(center-TIP)*1000),'tip_distance_metric':'Native face-centroid Euclidean distance to v284',
        'boundary_membership':fi in BF,'boundary_edges':[list(e) for e in BE if fi in selected_edges[e]],
        'vertices_gt_9mm':[v for v in vs if G[v]>9]})
COMMON={'execution':'HUMAN_CAP_AUTHORITY_CORRECTION_R1','candidate_name':'NATIVE_THUMB_DISTAL_CAP_CANDIDATE_R1',
    'human_approval':'PENDING_HUMAN_REVIEW','production_cap_replaced':False,'mesh_state':C['mesh_state'],
    'native_mesh_path':N['path'],'native_mesh_sha256':N['sha256'],'vertex_count':48,'face_count':33,
    'seed_vertex_id':284,'geodesic_radius_convention_mm':9.0,'source_candidate_sha256':sha(SRC/'NATIVE_THUMB_DISTAL_CAP_CANDIDATE_SET.json')}
dump('NATIVE_THUMB_CAP_CANDIDATE_R1.json',{**C,**COMMON,'vertex_geodesic_le_9mm_ids':inside,
    'face_expansion_geodesic_gt_9mm_ids':expanded,'boundary_vertex_ids':sorted(BV),'boundary_face_ids':sorted(BF),
    'thumb_IP_world_m':IP.tolist(),'thumb_IP_status':'Inherited native engineering estimate; no new joint authority',
    'thumb_tip_direction_unit_world':TIPDIR.tolist(),'nail_face_ids':sorted(NF),'nail_provenance':'Approved Stage4C_R2 nail mask mapped by unchanged face IDs to native geometry',
    'human_decision':None,'membership_authority_applied':False})
dump('NATIVE_THUMB_CAP_BOUNDARY_AUDIT.json',{**COMMON,'vertices':vrows,'faces':frows,
    'boundary_definition':'Edges incident to exactly one selected candidate face; boundary vertices are their endpoints',
    'boundary_edges':[{'vertex_ids':list(e),'candidate_face_ids':selected_edges[e], 'native_incident_face_ids':edge_faces[e],
        'native_outside_candidate_face_ids':[fi for fi in edge_faces[e] if fi not in CF], 'length_mm':float(np.linalg.norm(V[e[0]]-V[e[1]])*1000)} for e in BE],
    'boundary_vertex_count':len(BV),'boundary_edge_count':len(BE),'boundary_face_count':len(BF),
    'boundary_paths_vertex_ids':loops,'boundary_closed_loops':all(s[0]==s[-1] for s in loops),
    'boundary_vertex_degrees':{str(v):len(ba[v]) for v in sorted(BV)},'candidate_nonmanifold_edge_ids':[list(e) for e in bad_edges],
    'geodesic_gt_9mm_expansion_vertices':[r for r in vrows if r['vertex_id'] in expanded],
    'anatomical_boundary_reasonableness':'PENDING_HUMAN_Q5; topological checks are not anatomical approval'})
dump('CAP_CANDIDATE_GEODESIC_EXPANSION_AUDIT.json',{**COMMON,
    'graph_domain':'Native THUMB-only induced edge graph; edge length in native world mm',
    'face_predicate':C['face_predicate'],'vertex_geodesic_le_9mm_count':len(inside),'vertex_geodesic_le_9mm_ids':inside,
    'face_expansion_geodesic_gt_9mm_count':len(expanded),'face_expansion_geodesic_gt_9mm_ids':expanded,
    'max_candidate_geodesic_mm':float(max(G[list(CV)])),
    'all_candidate_vertices_within_9mm':False,'expansion_vertices':[r for r in vrows if r['vertex_id'] in expanded],
    'faces_with_gt_9mm_corners':[r for r in frows if r['vertices_gt_9mm']],
    'statement':'9 mm is the min-corner face admission convention, not an all-vertices hard radius.'})

# Native orthographic views with a depth-tested neutral surface and explicitly X-ray evidence overlays.
GREEN='#087a39'; RED='#c62c37'; ORANGE='#f19b17'; PURPLE='#9a49ba'; INK='#183147'; CYAN='#007884'
def font(n,b=False): return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf',n)
def txt(d,xy,s,n=22,c=INK,b=False): d.text(xy,s,font=font(n,b),fill=c)
def arrow(d,a,b,c=CYAN,width=4):
    a=np.array(a); b=np.array(b); vec=b-a
    if np.linalg.norm(vec)<3: return
    u=unit(vec); side=np.array([-u[1],u[0]])
    d.line([tuple(a),tuple(b)],fill=c,width=width)
    d.polygon([tuple(b),tuple(b-u*16+side*7),tuple(b-u*16-side*7)],fill=c)
def dashed(d,a,b,c,width=3):
    a=np.array(a); b=np.array(b); dist=np.linalg.norm(b-a)
    for t in np.arange(0,dist,13):
        d.line([tuple(a+(b-a)*t/max(dist,1)),tuple(a+(b-a)*min(t+7,dist)/max(dist,1))],fill=c,width=width)
ALL=[i for i in range(len(V)) if V[i,2]>.39]
THUMB=[i for i in DOMAIN if np.linalg.norm(V[i]-TIP)<.039]
OLDFOCUS=sorted(set(OLD)|{b for a,b in E if a in OLD}|{a for a,b in E if b in OLD})
VIEW={ 'DORSAL':np.array([0.,-1.,0.]),'PALMAR':np.array([0.,1.,0.]),
    'RADIAL':np.array([1.,0.,0.]),'ULNAR':np.array([-1.,0.,0.]),
    'THUMB_SIDE':unit(np.cross(TIPDIR,np.array([0.,-1.,0.]))),'THUMB_TIP_CLOSEUP':TIPDIR}
renders=OUT/'renders'; renders.mkdir(exist_ok=True)
views_meta=[]
def panel(normal,size,focus,caption,mark_boundary=False):
    w,h=size; view=unit(normal); right=unit(np.cross([0.,0.,1.],view)); up=unit(np.cross(view,right))
    xy=np.stack([V@right,V@up],axis=1); depth=V@view
    limits=xy[focus]; lo=limits.min(0); hi=limits.max(0); mid=(lo+hi)/2
    scale=min((w-100)/max(hi[0]-lo[0],1e-6),(h-155)/max(hi[1]-lo[1],1e-6))
    def p3(v): return np.array([w/2+(v@right-mid[0])*scale,(h+70)/2-(v@up-mid[1])*scale])
    pts=np.array([p3(v) for v in V]); zbuf=np.full((h,w),-np.inf); pix=np.full((h,w,3),250,dtype=np.uint8)
    for fi,vs in enumerate(F):
        vv=V[vs]; fn=np.cross(vv[1]-vv[0],vv[2]-vv[0]); norm=np.linalg.norm(fn)
        lighting=abs(float(fn@view/norm)) if norm>0 else .5
        gray=int(177+53*lighting); color=np.array([gray, min(gray+4,255),min(gray+7,255)])
        for j in range(1,len(vs)-1):
            inds=[vs[0],vs[j],vs[j+1]]; p=pts[inds]
            x0=max(0,int(np.floor(p[:,0].min()))); x1=min(w-1,int(np.ceil(p[:,0].max())))
            y0=max(65,int(np.floor(p[:,1].min()))); y1=min(h-1,int(np.ceil(p[:,1].max())))
            if x1<x0 or y1<y0: continue
            den=(p[1,1]-p[2,1])*(p[0,0]-p[2,0])+(p[2,0]-p[1,0])*(p[0,1]-p[2,1])
            if abs(den)<1e-8: continue
            yy,xx=np.mgrid[y0:y1+1,x0:x1+1]; xx=xx+.5; yy=yy+.5
            aa=((p[1,1]-p[2,1])*(xx-p[2,0])+(p[2,0]-p[1,0])*(yy-p[2,1]))/den
            bb=((p[2,1]-p[0,1])*(xx-p[2,0])+(p[0,0]-p[2,0])*(yy-p[2,1]))/den; cc=1-aa-bb
            zz=aa*depth[inds[0]]+bb*depth[inds[1]]+cc*depth[inds[2]]
            zzview=zbuf[y0:y1+1,x0:x1+1]; mask=(aa>=0)&(bb>=0)&(cc>=0)&(zz>zzview)
            zzview[mask]=zz[mask]; pix[y0:y1+1,x0:x1+1][mask]=color
    im=Image.fromarray(pix); d=ImageDraw.Draw(im)
    # Surface topology is depth-filtered; overlays below are X-ray by explicit review design.
    for a,b in E:
        pa,pb=pts[a],pts[b]; p=(pa+pb)/2
        x,y=map(int,p)
        if 0<=x<w and 65<=y<h and (depth[a]+depth[b])/2>=zbuf[y,x]-.001:
            d.line([tuple(pa),tuple(pb)],fill='#abb5bf',width=1)
    layer=Image.new('RGBA',(w,h)); ld=ImageDraw.Draw(layer)
    for fi in sorted(NF): ld.polygon([tuple(pts[v]) for v in F[fi]],fill=(155,62,187,115))
    for fi in sorted(CF): ld.polygon([tuple(pts[v]) for v in F[fi]],fill=(0,181,83,85))
    im=Image.alpha_composite(im.convert('RGBA'),layer); d=ImageDraw.Draw(im)
    for fi in NF:
        p=[tuple(pts[v]) for v in F[fi]]; d.line(p+[p[0]],fill=PURPLE,width=2)
    for a,b in BE: dashed(d,pts[a],pts[b],GREEN,3)
    def dot(v,c,r,expand=False):
        x,y=pts[v]
        if expand: d.rectangle((x-r,y-r,x+r,y+r),fill=c,outline='#ffd66e',width=2)
        else: d.ellipse((x-r,y-r,x+r,y+r),fill=c,outline='white',width=1)
    for v in sorted(CV): dot(v,GREEN,5 if mark_boundary else 3,v in expanded)
    for v in OLD: dot(v,RED,7 if caption.startswith('Old') else 4)
    dot(SEED,ORANGE,8 if mark_boundary else 6)
    a=p3(IP); x,y=a
    d.line([(x-9,y),(x+9,y)],fill=CYAN,width=3); d.line([(x,y-9),(x,y+9)],fill=CYAN,width=3)
    if mark_boundary:
        txt(d,(18,80),'thumb IP (native engineering estimate)',19,CYAN,True); d.line([(22,111),tuple(a)],fill=CYAN,width=2)
        tx,ty=pts[SEED]; label=(w-245,135)
        txt(d,label,'seed / tip v284',21,ORANGE,True); d.line([(label[0],label[1]+25),(tx,ty)],fill=ORANGE,width=2)
        boundary_anchor=pts[max(BV,key=lambda v:pts[v,0])]
        txt(d,(w-270,h-70),'candidate boundary',20,GREEN,True); d.line([(w-268,h-43),tuple(boundary_anchor)],fill=GREEN,width=2)
        projected=np.array([TIPDIR@right,-TIPDIR@up])
        if np.linalg.norm(projected)<1e-6:
            txt(d,(18,h-104),'Tip direction: toward viewer (+IP -> v284)',19,CYAN,True)
            d.ellipse((tx-17,ty-17,tx+17,ty+17),outline=CYAN,width=2)
        else:
            start=np.array([75.,h-155.]); arrow(d,start,start+unit(projected)*80)
            txt(d,(18,h-105),'thumb tip direction (IP -> v284)',19,CYAN,True)
    d.rectangle((0,0,w,62),fill='#e8eef3'); txt(d,(14,18),caption,22,b=True)
    d.rectangle((0,0,w-1,h-1),outline='#c0cdd7',width=2)
    return im.convert('RGB'), {'right_unit':right.tolist(),'up_unit':up.tolist(),'toward_viewer_unit':view.tolist()}
for name,normal in VIEW.items():
    im=Image.new('RGB',(2200,1450),'#f2f5f8'); d=ImageDraw.Draw(im)
    txt(d,(30,20),'HUMAN CAP AUTHORITY REVIEW / '+name,35,b=True)
    txt(d,(32,75),'NATIVE / PRE-RSSF Stage4A_R2 | 48 vertices / 33 faces | Pending Human approval',25)
    txt(d,(32,122),f'Green dots: g <= 9 mm ({len(inside)})     Green squares + gold outline: face expansion, g > 9 mm ({len(expanded)})',23,GREEN,True)
    txt(d,(32,160),'Green translucent faces: candidate 33     Red: contaminated cap9     Orange: seed v284     Purple: approved nail mask',22)
    txt(d,(32,198),'Dashed green: exact candidate boundary. Evidence overlays are X-ray (include hidden surfaces); grey surface is depth-tested.',21)
    a,_=panel(normal,(640,960),ALL,'Native hand context (all overlays)')
    focus=THUMB if name!='THUMB_TIP_CLOSEUP' else sorted(CV|NV)
    b,meta=panel(normal,(1020,960),focus,'Native thumb / distal cap closeup',True)
    c,_=panel(normal,(440,960),OLDFOCUS,'Old cap9 / INDEX inset')
    im.paste(a,(30,255)); im.paste(b,(690,255)); im.paste(c,(1730,255)); d=ImageDraw.Draw(im)
    txt(d,(32,1240),f'Min-corner 9 mm rule is NOT an all-vertex hard radius. Max candidate g = {max(G[list(CV)]):.6f} mm.',24,b=True)
    txt(d,(32,1280),f'Boundary: {len(BE)} edges / {len(BV)} vertices / {len(loops)} closed loop(s). Native engineering IP label does not create joint authority.',22)
    txt(d,(32,1320),'Old cap9 IDs: '+', '.join(map(str,OLD))+' | all 9 = INDEX_SURFACE; none are thumb anatomical evidence.',22,RED)
    txt(d,(32,1364),'READ ONLY PRODUCTION | No cap / weight / geometry / topology / bone / joint edit | STOP after Human review package',22,b=True)
    file='HUMAN_CAP_'+name+'.png'; im.save(renders/file)
    views_meta.append({'view':name,'png':'renders/'+file,'camera_basis_native_world':meta,'native_mesh_state':C['mesh_state'],
        'overlay_policy':'X-ray including hidden surfaces; depth-tested neutral base. Same candidate/nail/cap9/seed in every view.',
        'panels':['native hand context','native thumb closeup','old erroneous cap9 INDEX inset']})
    print('Rendered',name,flush=True)
dump('NATIVE_VIEW_METADATA.json',{'views':views_meta,'THUMB_SIDE_definition':'Side orthogonal to native IP-to-tip direction and dorsal normal',
    'THUMB_TIP_CLOSEUP_definition':'Camera toward-viewer axis = native IP-to-v284 unit direction; axial terminal view'})

questions=[('Q1','v284 是否视觉上位于真实 native thumb terminal tip？'),('Q2','48-vertex candidate 是否整体位于 thumb distal cap？'),
    ('Q3','candidate 是否明显侵入 thumb middle/proximal surface？'),('Q4','candidate 是否遗漏明显 distal-cap surface？'),
    ('Q5','当前 33-face boundary 是否视觉合理？'),('Q6','是否批准 NATIVE_THUMB_DISTAL_CAP_CANDIDATE_R1 作为新的 cap membership authority？')]
cards=''.join(f'<article id="{m["view"]}"><h2>{m["view"]}</h2><a href="{m["png"]}" target="_blank"><img src="data:image/png;base64,{base64.b64encode((OUT/m["png"]).read_bytes()).decode()}" alt="{m["view"]} native pre-RSSF cap review"></a><p>点击图片打开独立 PNG，可放大查看。全手、拇指局部、错误 cap9 食指局部使用同一视角。所有彩色层为 X-ray 审阅标记，包括被表面遮挡的点和面。</p></article>' for m in views_meta)
form=''
for q,text in questions:
    options=['YES','NO','UNRESOLVED'] if q!='Q6' else ['APPROVE','APPROVE_WITH_BOUNDARY_REVIEW','REJECT','UNRESOLVED']
    form+=f'<fieldset><legend>{q}. {text}</legend><label><select name="{q}"><option value="">请选择（尚未回答）</option>'+''.join(f'<option>{o}</option>' for o in options)+'</select></label></fieldset>'
table=''.join(f'<tr><td>v{r["vertex_id"]}</td><td>{r["geodesic_distance_mm"]:.6f}</td><td>{r["tip_distance_mm"]:.6f}</td><td>{"YES" if r["nail_membership"] else "NO"}</td><td>{"YES" if r["boundary_membership"] else "NO"}</td><td>{", ".join(map(str,r["face_ids"]))}</td></tr>' for r in vrows if r['vertex_id'] in expanded)
nav=''.join(f'<a href="#{k}">{k}</a>' for k in VIEW)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>HUMAN CAP AUTHORITY REVIEW</title>
<style>body{margin:0;background:#eef2f6;color:#183147;font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1440px;margin:auto;padding:28px}header,article,section{background:white;border:1px solid #d6e0e7;border-radius:12px;padding:24px;margin-bottom:24px}h1{font-size:32px;margin:0 0 16px}h2{margin:0 0 12px}nav{display:flex;flex-wrap:wrap;gap:10px;position:sticky;top:0;background:#eef2f6;padding:12px;z-index:2}a{color:#086579}nav a{background:white;border-radius:6px;padding:8px}img{width:100%;height:auto;border:1px solid #cbd5df}strong{font-weight:700}.notice{border-left:4px solid #bf3240;padding:12px;background:#fff3f2}.legend{display:flex;flex-wrap:wrap;gap:16px}.green{color:#087a39}.red{color:#c62c37}.purple{color:#9a49ba}.orange{color:#a66805}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:8px;border:1px solid #d4dfe7}th{background:#eef4f7}fieldset{border:1px solid #cbd6df;border-radius:8px;margin:16px 0;padding:16px}legend{font-weight:650}select,button,textarea{font:inherit;padding:10px;border:1px solid #9eafbd;border-radius:6px}select{max-width:100%}button{cursor:pointer;background:#183147;color:white}textarea{box-sizing:border-box;width:100%;height:80px}pre{white-space:pre-wrap;background:#edf3f6;padding:16px}#result{display:none}article{scroll-margin-top:90px}</style><main><header><h1>HUMAN CAP AUTHORITY REVIEW</h1>
<p>HUMAN_CAP_AUTHORITY_CORRECTION_R1 · native / pre-RSSF · <strong>48 个候选顶点 / 33 个候选面</strong> · seed <strong>v284</strong></p>
<p class="notice"><strong>CURRENT_APPROVED_CAP_9 = CONTAMINATED，9 / 9 = native INDEX_SURFACE。</strong>旧 cap9 不得作为真实 thumb distal-cap anatomical evidence。此页只征求 Human 判断；新候选未获批准，production membership authority 未应用。</p>
<div class="legend"><strong class="green">● 绿色圆点：自身 g ≤9 mm</strong><strong class="green">▣ 绿色方点 + 金边：自身 g &gt;9 mm，因 face expansion 纳入</strong><strong class="red">● 红色：旧错误 cap9</strong><strong class="orange">● 橙色：seed v284</strong><strong class="purple">紫色：approved thumb nail region</strong></div>
<p>绿色半透明面 = 33 个候选面；绿色虚线 = selected-face boundary。彩色标记为 X-ray 叠加（包括隐藏表面），灰色 native 网格按深度显示。每幅 PNG 同时含全手、thumb 局部与错误 cap9 的 INDEX 局部，不把不同部位拼成一个解剖表面。</p>
<p>thumb IP 为先前只读重建的 native 工程估计；tip direction 指向 IP→v284。指甲使用 approved Stage4C_R2 的原 face IDs 映回 native 网格。图中不使用 posed/RSSF 或 R3 身份作为解剖证明。</p></header><nav>'''+nav+'''<a href="#expansion">GEODESIC AUDIT</a><a href="#human">HUMAN Q1–Q6</a></nav>'''+cards+f'''<section id="expansion"><h2>9 mm 与 min-corner face expansion</h2><p>在 native THUMB-only induced edge graph 上从 v284 求 geodesic，候选 face 通过 <code>min(corner geodesic) ≤9 mm</code> 纳入，再取 33 个面的角点并集。<strong>{len(inside)} 点自身 g ≤9 mm；{len(expanded)} 点自身 g &gt;9 mm。</strong>最大候选顶点距离 <strong>{max(G[list(CV)]):.6f} mm</strong>。不能把全部 48 点描述成“都在 9 mm 内”。</p><div style="overflow:auto"><table><thead><tr><th>Vertex ID</th><th>Geodesic mm</th><th>Tip Euclidean mm</th><th>Nail member</th><th>Boundary member</th><th>Candidate faces admitting corner</th></tr></thead><tbody>{table}</tbody></table></div>
<p>全部 48 点 / 33 面的 geodesic、native branch、nail membership、tip distance、boundary membership：<a href="NATIVE_THUMB_CAP_BOUNDARY_AUDIT.json">Boundary audit JSON</a>。<a href="CAP_CANDIDATE_GEODESIC_EXPANSION_AUDIT.json">Expansion audit JSON</a> · <a href="NATIVE_THUMB_CAP_CANDIDATE_R1.json">Candidate JSON</a> · <a href="HUMAN_CAP_AUTHORITY_REVIEW_REPORT.md">Report</a></p>
<p>拓扑 boundary 有 {len(BE)} 条边 / {len(BV)} 个顶点 / {len(loops)} 个闭环。拓扑闭合不代替 Q5 的视觉判断。</p></section><section id="human"><h2>Human 判断（仅 Q1–Q6）</h2><p>所有选项初始为空。答案在浏览器本地生成；没有网络提交或自动应用。Q6 的任何选择都不会修改 production。生成记录后需由 Human 将结果交回项目，等待另轮明确授权。</p><form id="review">{form}<p><label>可选说明 / 边界需复核处<textarea name="notes" placeholder="可填写 vertex / face ID 或视图位置"></textarea></label></p><button type="submit">生成 Human 答案记录</button></form><pre id="result"></pre><button id="download" type="button" hidden>下载 Human 答案 JSON</button></section><section><strong>STOP — WAITING FOR HUMAN CAP AUTHORITY REVIEW</strong><p>BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0。production before == after。未修改 cap、R3、权重，未重跑 R3、创建 R1F、运行 Stage6、重算 strict bound 或 retopo。</p></section></main>
<script>
let response=null;document.getElementById('review').addEventListener('submit',e=>{{e.preventDefault();const f=new FormData(e.target);for(let i=1;i<=6;i++){{if(!f.get('Q'+i)){{alert('请回答 Q'+i+'（不确定可选 UNRESOLVED）');return}}}}response={{review:'HUMAN_CAP_AUTHORITY_CORRECTION_R1',candidate:'NATIVE_THUMB_DISTAL_CAP_CANDIDATE_R1',answers:Object.fromEntries(f),recorded_at:new Date().toISOString(),production_authority_applied:false}};const r=document.getElementById('result');r.textContent=JSON.stringify(response,null,2);r.style.display='block';document.getElementById('download').hidden=false;}});document.getElementById('download').onclick=()=>{{if(!response)return;const u=URL.createObjectURL(new Blob([JSON.stringify(response,null,2)],{{type:'application/json'}}));const a=document.createElement('a');a.href=u;a.download='HUMAN_CAP_AUTHORITY_RESPONSE_R1.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)}};
</script></html>'''
(OUT/'HUMAN_CAP_AUTHORITY_REVIEW.html').write_text(page,encoding='utf8')

# Complete freeze verification after evidence generation; no production file is opened for writing.
AFTER={p:sha(ROOT/p) for p in BEFORE}
added=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts and p.relative_to(ROOT).as_posix() not in BEFORE]
changed=[p for p,h in BEFORE.items() if AFTER[p]!=h]
assert not changed and not added
ZERO={k:0 for k in ['BLEND_FILES_WRITTEN','WEIGHT_DELTA','GEOMETRY_DELTA','TOPOLOGY_DELTA','BONE_DELTA','JOINT_DELTA']}
dump('FROZEN_HASH_VERIFICATION.json',{'all_before_equals_after':True,'protected_existing_file_count':len(BEFORE),
    'before':BEFORE,'after':AFTER,'changed_files':changed,'new_files_outside_review_directory':added,
    'new_production_blends':[],'verification_scope':'All pre-existing workspace files except .git, including production_spec, docs, references and previous review/audit files',
    **ZERO,'evidence_writes_only_in':str(OUT),'pose_evaluations':0,'R3_runs':0,'Stage6_runs':0,'strict_bound_recomputations':0,'R1F_CREATED':False,'cap_authority_applied':False})
exp_table='\n'.join(f'| {r["vertex_id"]} | {r["geodesic_distance_mm"]:.6f} | {r["tip_distance_mm"]:.6f} | {r["nail_membership"]} | {r["boundary_membership"]} |' for r in vrows if r['vertex_id'] in expanded)
report=f'''# HUMAN_CAP_AUTHORITY_REVIEW_REPORT

执行：HUMAN_CAP_AUTHORITY_CORRECTION_R1。状态：**STOP — WAITING_FOR_HUMAN_CAP_AUTHORITY_REVIEW**。

只生成 Human 审阅材料。候选 **NATIVE_THUMB_DISTAL_CAP_CANDIDATE_R1** 仍为 PENDING_HUMAN_REVIEW，human_decision=null，未登记新的 membership authority。

## 输入与显示

独立候选原清单逐 ID 保持：48 vertices / 33 faces，seed v284；native THUMB-only induced graph；继承的 9 mm min-corner convention。与旧 cap9 无交集。旧 cap9：{', '.join(map(str,OLD))}，已证明全部 INDEX_SURFACE，CURRENT_APPROVED_CAP_9=CONTAMINATED；本轮只作红色错误对照。

源候选 SHA256：`{COMMON['source_candidate_sha256']}`。
native blend：`{N['path']}`；SHA256：`{N['sha256']}`。复用独立 audit 保存的 native world coordinates/topology，直接核对源 blend 哈希；没有重新保存 blend、求姿态或运行 Blender。nail mask 使用 Stage4C_R2 approved 12-face region：{sorted(NF)}，映回不变 face IDs。IP `{IP.tolist()}` 是继承的 native 工程估计；tip direction `{TIPDIR.tolist()}` 为 IP→v284，不创建 joint/bone authority。

六个 PNG：DORSAL、PALMAR、RADIAL、ULNAR、THUMB_SIDE、THUMB_TIP_CLOSEUP，均只画 native/pre-RSSF；每图同时提供完整手上下文、thumb distal closeup、旧错误 cap9 食指局部，并显示候选绿色点/半透明面、红 cap9、橙 seed、紫 nail、IP、tip direction、candidate boundary。灰色表面作深度测试；全部彩色证据使用明确标注的 X-ray 投影，包括隐藏面，不能将隐藏投影当可见表面贴合。DORSAL=-Y、PALMAR=+Y、RADIAL=+X、ULNAR=-X；thumb side 和 tip axial basis 见 NATIVE_VIEW_METADATA.json。

## Geodesic expansion

**{len(inside)} 个候选点自身 geodesic ≤9 mm；{len(expanded)} 个自身 >9 mm，由 min-corner face expansion 纳入。最大 {max(G[list(CV)]):.6f} mm。48 点并非全部在 9 mm 内。**

计算仅用于这份候选的审阅 audit，不改变已存在 membership。测地距离使用 native world edge length mm 和独立 THUMB-only graph。tip distance 为 native 到 seed v284 的 Euclidean distance；vertex 和 face-corner geodesic 单独列出，未把 face centroid Euclidean distance 写成 surface geodesic。

| vertex ID | geodesic mm | tip Euclidean mm | nail | boundary |
| --- | ---: | ---: | --- | --- |
{exp_table}

## Boundary audit

全部 48 vertex rows / 33 face rows 含原始 ID、geodesic、native branch、nail membership、tip distance、boundary membership。记录 selected-face boundary edges、外侧 native faces、geodesic shortest paths 和每个扩展点的 admitting face / ≤9 mm corner。边界：{len(BE)} edges / {len(BV)} vertices / {len(BF)} boundary faces / {len(loops)} closed loop(s)；selected-edge incidence >2：{len(bad_edges)}。闭环检查只说明候选拓扑，解剖边界是否合理留给 Human Q5。

## Human questions

{chr(10).join(q+'. '+t for q,t in questions)}

Q1–Q5：YES / NO / UNRESOLVED；Q6：APPROVE / APPROVE_WITH_BOUNDARY_REVIEW / REJECT / UNRESOLVED。页面不预选答案，不自动判定。浏览器只在 Human 操作后生成可下载答案；不会提交网络或更新 production authority。

## 冻结

{len(BEFORE)} 个既有 workspace 文件逐文件 SHA256 before==after（全部既有 production/docs/reference/旧审阅和审计文件，另含全部 BLEND）。新增材料只在本审阅目录。完整 before/after 见 FROZEN_HASH_VERIFICATION.json。

BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0。cap/R3 未修改；R3_runs=0；R1F_CREATED=false；Stage6_runs=0；strict_bound_recomputations=0；retopo=false。

**STOP。未自动应用新的 cap membership authority。**
'''
(OUT/'HUMAN_CAP_AUTHORITY_REVIEW_REPORT.md').write_text(report,encoding='utf8')
print(json.dumps({'inside_9mm':len(inside),'expanded_gt_9mm':len(expanded),'expanded_ids':expanded,
    'boundary_edges':len(BE),'boundary_vertices':len(BV),'boundary_loops':loops,'frozen_files':len(BEFORE),'STOP':True}),flush=True)
