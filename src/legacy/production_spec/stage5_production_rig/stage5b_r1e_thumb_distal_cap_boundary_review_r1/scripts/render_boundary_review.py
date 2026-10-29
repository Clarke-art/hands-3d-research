"""Static scientific native projections and self-contained SVG-layer Human review."""
import sys
sys.dont_write_bytecode=True
import base64, io, json, html, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from boundary_geometry import *
R=load(OUT/'_RENDER_DATA.json'); COMP=load(OUT/'CAP_BOUNDARY_CANDIDATE_COMPARISON.json')
COL={'A':'#d63b3b','B':'#7c36b0','C':'#078b65','D':'#db9413','E':'#0966d0'}
CLASSCOL={'A':'#148342','B':'#677484','C':'#d33138','D':'#9852b3','E':'#c78b07'}
INK='#183247'; NAIL='#ac55c1'; SEEDCOL='#f29013'; AXCOL='#006e7a'
CFAMS={k:set(v) for k,v in R['candidate_faces'].items()}; BOUNDS=R['candidate_boundary_edges']
ALL=[i for i in range(N) if V[i,2]>390]
LOCALFOCUS=sorted({v for vs in R['candidate_vertices'].values() for v in vs}|NV)
LOCALFOCUS+= [int(np.argmin(np.linalg.norm(V-IP,axis=1)))]
VIEWS={'DORSAL':np.array([0.,-1.,0.]),'PALMAR':np.array([0.,1.,0.]),'RADIAL':np.array([1.,0.,0.]),
    'ULNAR':np.array([-1.,0.,0.]),'SIDE':unit(np.cross(AXIS,[0.,-1.,0.])),'TIP':AXIS}
def font(n,b=False): return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf',n)
def txt(d,xy,s,n=22,c=INK,b=False): d.text(xy,s,font=font(n,b),fill=c,stroke_width=0)
def patterned(d,a,b,color,width,k):
    a=np.array(a); b=np.array(b); dist=np.linalg.norm(b-a)
    # Different repeating phase enables overlapping exact native edges to remain distinguishable.
    period=32; phase='ABCDE'.index(k)*6; length=11
    for t in np.arange(-period+phase,dist,period):
        t0=max(0,t); t1=min(dist,t+length)
        if t1>t0: d.line([tuple(a+(b-a)*t0/max(dist,1)),tuple(a+(b-a)*t1/max(dist,1))],fill=color,width=width)
def arrow(d,a,b,color=AXCOL):
    a=np.array(a); b=np.array(b); vec=b-a
    if np.linalg.norm(vec)<3:return
    u=unit(vec); side=np.array([-u[1],u[0]])
    d.line([tuple(a),tuple(b)],fill=color,width=3); d.polygon([tuple(b),tuple(b-u*15+side*6),tuple(b-u*15-side*6)],fill=color)
def projection(normal,w,h,focus):
    view=unit(normal); right=unit(np.cross([0.,0.,1.],view)); up=unit(np.cross(view,right))
    xy=np.stack([V@right,V@up],axis=1); depth=V@view
    q=xy[focus]; mid=(q.min(0)+q.max(0))/2
    scale=min((w-110)/max(np.ptp(q[:,0]),1e-5),(h-170)/max(np.ptp(q[:,1]),1e-5))
    def p3(v):return np.array([w/2+(v@right-mid[0])*scale,(h+40)/2-(v@up-mid[1])*scale])
    pts=np.array([p3(v) for v in V]); pix=np.full((h,w,3),249,dtype=np.uint8); zb=np.full((h,w),-np.inf)
    for fi,vs in enumerate(F):
        gray=int(172+61*abs(FN[fi]@view)); color=np.array([gray,min(gray+4,255),min(gray+8,255)],np.uint8)
        for j in range(1,len(vs)-1):
            inds=[vs[0],vs[j],vs[j+1]]; p=pts[inds]
            x0=max(0,int(np.floor(p[:,0].min()))); x1=min(w-1,int(np.ceil(p[:,0].max())))
            y0=max(0,int(np.floor(p[:,1].min()))); y1=min(h-1,int(np.ceil(p[:,1].max())))
            if x1<x0 or y1<y0:continue
            den=(p[1,1]-p[2,1])*(p[0,0]-p[2,0])+(p[2,0]-p[1,0])*(p[0,1]-p[2,1])
            if abs(den)<1e-8:continue
            yy,xx=np.mgrid[y0:y1+1,x0:x1+1]; xx=xx+.5; yy=yy+.5
            aa=((p[1,1]-p[2,1])*(xx-p[2,0])+(p[2,0]-p[1,0])*(yy-p[2,1]))/den
            bb=((p[2,1]-p[0,1])*(xx-p[2,0])+(p[0,0]-p[2,0])*(yy-p[2,1]))/den; cc=1-aa-bb
            z=aa*depth[inds[0]]+bb*depth[inds[1]]+cc*depth[inds[2]]; zone=zb[y0:y1+1,x0:x1+1]
            mask=(aa>=0)&(bb>=0)&(cc>=0)&(z>zone); zone[mask]=z[mask]; pix[y0:y1+1,x0:x1+1][mask]=color
    im=Image.fromarray(pix); d=ImageDraw.Draw(im)
    for a,b in ED:
        p=(pts[a]+pts[b])/2; x,y=map(int,p)
        if 0<=x<w and 0<=y<h and (depth[a]+depth[b])/2>=zb[y,x]-.7:
            d.line([tuple(pts[a]),tuple(pts[b])],fill='#b0bac4',width=1)
    return im,pts,p3,{'toward_viewer_unit':view.tolist(),'right_unit':right.tolist(),'up_unit':up.tolist(),'pixels_per_mm':scale}
def overlay(im,pts,p3,forensic=False,ids=False):
    im=im.convert('RGBA'); layer=Image.new('RGBA',im.size); ld=ImageDraw.Draw(layer)
    for fi in NF: ld.polygon([tuple(pts[v]) for v in F[fi]],fill=(167,65,190,100))
    if not forensic:
        for fi in CFAMS['E']:ld.polygon([tuple(pts[v]) for v in F[fi]],fill=(29,103,210,28))
    im=Image.alpha_composite(im,layer); d=ImageDraw.Draw(im)
    for fi in NF:
        p=[tuple(pts[v]) for v in F[fi]];d.line(p+[p[0]],fill=NAIL,width=2)
    if forensic:
        for v in sorted(CORE):
            x,y=pts[v];d.ellipse((x-4,y-4,x+4,y+4),fill='#063e25',outline='white',width=1)
        for v in sorted(EXP):
            x,y=pts[v];cls=R['classifications'][str(v)];color=CLASSCOL[cls]; r=6
            d.rectangle((x-r,y-r,x+r,y+r),fill=color,outline='#ffedab',width=2)
            if v==882:d.ellipse((x-13,y-13,x+13,y+13),outline='#d33138',width=3)
            if ids:d.text((x+7,y-18),str(v),font=font(18,True),fill=color,stroke_width=2,stroke_fill='white')
    else:
        for k in 'ABCDE':
            for a,b in BOUNDS[k]:patterned(d,pts[a],pts[b],COL[k],5,k)
    x,y=p3(IP);d.line([(x-10,y),(x+10,y)],fill=AXCOL,width=3);d.line([(x,y-10),(x,y+10)],fill=AXCOL,width=3)
    tx,ty=pts[SEED];arrow(d,p3(IP),pts[SEED]);d.ellipse((tx-8,ty-8,tx+8,ty+8),fill=SEEDCOL,outline='white',width=2)
    txt(d,(18,24),'thumb IP (native estimate)',20,AXCOL,True);d.line([(20,50),tuple(p3(IP))],fill=AXCOL,width=2)
    txt(d,(im.width-270,65),'native terminal tip v284',20,SEEDCOL,True);d.line([(im.width-265,93),(tx,ty)],fill=SEEDCOL,width=2)
    if np.linalg.norm(p3(IP)-pts[SEED])<4:txt(d,(20,im.height-42),'IP -> tip axis: toward viewer (axial view)',19,AXCOL,True)
    else:txt(d,(20,im.height-42),'Arrow: IP -> tip axis',19,AXCOL,True)
    return im.convert('RGB')

SVGS=[]; VM=[]
for name,normal in VIEWS.items():
    full,pf,p3f,_=projection(normal,610,1020,ALL); full=overlay(full,pf,p3f)
    close,pc,p3c,meta=projection(normal,1680,1020,LOCALFOCUS); close=overlay(close,pc,p3c)
    im=Image.new('RGB',(2400,1470),'#f0f4f7');d=ImageDraw.Draw(im)
    txt(d,(30,20),'THUMB DISTAL CAP / BOUNDARY CANDIDATES / '+name,34,b=True)
    txt(d,(32,72),'Native / pre-RSSF | Region identity ACCEPTED | Final boundary UNRESOLVED | Read-only candidate comparison',23)
    for i,k in enumerate('ABCDE'):
        m=COMP['candidates'][k]['metrics']; txt(d,(35+i*465,125),f'{k}: {m["vertex_count"]}v / {m["face_count"]}f / max g {m["max_geodesic_mm"]:.3f}',22,COL[k],True)
    txt(d,(32,173),'Purple = approved nail | Orange = seed v284 | Teal = native IP / tip axis | Boundaries use phased colors on shared edges.',22)
    txt(d,(32,209),'All color layers are X-ray including hidden surface. Neutral native mesh is depth-tested. D is a diagnostic patch, not stable curvature authority.',21)
    im.paste(full,(30,280));im.paste(close,(680,280));d=ImageDraw.Draw(im)
    txt(d,(32,247),'Native context',20,b=True);txt(d,(682,247),'Local native thumb / five exact existing-edge boundary overlays',20,b=True)
    txt(d,(32,1320),'A min-corner | B strict face | C minimum topology closure | D curvature/normal knee | E axial circumferential cut',24,b=True)
    txt(d,(32,1364),'E = engineering recommendation for Human review only. Old cap9 remains contaminated native INDEX. No production cap authority is applied.',22)
    txt(d,(32,1406),'STOP after review materials | No blend / weights / R3 / Stage6 / strict bound / retopo changes',22,b=True)
    im.save(OUT/'renders'/('CAP_BOUNDARY_CANDIDATES_'+name+'.png'))
    # Interactive SVG uses a clean native base with separate exact-coordinate overlays.
    base,points,p3,meta2=projection(normal,1500,1050,LOCALFOCUS);bio=io.BytesIO();base.save(bio,format='PNG')
    b64=base64.b64encode(bio.getvalue()).decode(); parts=[f'<svg class="native-view" id="view-{name}" data-view="{name}" viewBox="0 0 1500 1050" xmlns="http://www.w3.org/2000/svg"><image width="1500" height="1050" href="data:image/png;base64,{b64}"/>']
    def poly(fi):return ' '.join(f'{points[v,0]:.2f},{points[v,1]:.2f}' for v in F[fi])
    for k in 'ABCDE':
        parts.append(f'<g class="candidate candidate-{k}">')
        parts.append('<g class="face-fill">')
        for fi in sorted(CFAMS[k]):parts.append(f'<polygon points="{poly(fi)}" fill="{COL[k]}" fill-opacity="0.075"><title>Candidate {k} face {fi}</title></polygon>')
        parts.append('</g><g class="boundary">')
        for a,b in BOUNDS[k]:
            parts.append(f'<path d="M {points[a,0]:.2f} {points[a,1]:.2f} L {points[b,0]:.2f} {points[b,1]:.2f}" fill="none" stroke="{COL[k]}" stroke-width="4" stroke-dasharray="11 21" stroke-dashoffset="{-6*"ABCDE".index(k)}"><title>{k} boundary v{a}–v{b}</title></path>')
        parts.append('</g></g>')
    parts.append('<g class="nail">')
    for fi in NF:parts.append(f'<polygon points="{poly(fi)}" fill="{NAIL}" fill-opacity="0.30" stroke="{NAIL}" stroke-width="2"><title>Approved nail face {fi}</title></polygon>')
    parts.append('</g><g class="core vertices">')
    for v in sorted(CORE):parts.append(f'<circle cx="{points[v,0]:.2f}" cy="{points[v,1]:.2f}" r="4" fill="#064529" stroke="white"><title>v{v} core g={G[v]:.6f}mm</title></circle>')
    parts.append('</g><g class="expansion vertices">')
    for v in sorted(EXP):
        color=CLASSCOL[R['classifications'][str(v)]]
        parts.append(f'<rect x="{points[v,0]-5:.2f}" y="{points[v,1]-5:.2f}" width="10" height="10" fill="{color}" stroke="#ffe6a1" stroke-width="2"><title>v{v} g={G[v]:.6f}mm classification {R["classifications"][str(v)]}</title></rect>')
    parts.append('</g><g class="vertex-ids">')
    for v in sorted(set(LOCALFOCUS)):
        parts.append(f'<text x="{points[v,0]+7:.2f}" y="{points[v,1]-8:.2f}" font-size="16" fill="#183247" stroke="white" stroke-width="3" paint-order="stroke">v{v}</text>')
    parts.append('</g><g class="face-ids">')
    for fi in sorted(set().union(*CFAMS.values())):
        q=p3(CENT[fi]);parts.append(f'<text x="{q[0]:.2f}" y="{q[1]:.2f}" font-size="13" fill="#735343" stroke="white" stroke-width="3" paint-order="stroke">f{fi}</text>')
    parts.append('</g><g class="landmarks">')
    x,y=p3(IP); tx,ty=points[SEED]
    parts.append(f'<path d="M {x-10:.2f} {y:.2f} h20 M {x:.2f} {y-10:.2f} v20" stroke="{AXCOL}" stroke-width="3"/>')
    parts.append(f'<text x="20" y="35" font-size="22" fill="{AXCOL}">thumb IP (native engineering estimate)</text><path d="M20 46 L{x:.2f} {y:.2f}" stroke="{AXCOL}" stroke-width="2"/>')
    parts.append(f'<circle cx="{tx:.2f}" cy="{ty:.2f}" r="8" fill="{SEEDCOL}" stroke="white" stroke-width="2"/><text x="1160" y="74" fill="{SEEDCOL}" font-size="24">seed / tip v284</text><path d="M1160 82 L{tx:.2f} {ty:.2f}" stroke="{SEEDCOL}"/>')
    if np.linalg.norm(np.array([x,y])-np.array([tx,ty]))>4:
        parts.append(f'<path d="M{x:.2f} {y:.2f} L{tx:.2f} {ty:.2f}" stroke="{AXCOL}" stroke-width="3"/><text x="20" y="1020" fill="{AXCOL}" font-size="22">IP→tip axis (line from cross to orange seed)</text>')
    else:parts.append(f'<text x="20" y="1020" fill="{AXCOL}" font-size="22">IP→tip axis: toward viewer · IP and tip projections overlap</text>')
    parts.append('</g></svg>');SVGS.append(''.join(parts))
    zoomids=set(CV)|{v for vs in R['candidate_vertices'].values() for v in vs}; z=points[sorted(zoomids)];lo=z.min(0)-40;hi=z.max(0)+40
    VM.append({'view':name,'camera_basis':meta2,'full_viewbox':[0,0,1500,1050],
        'tip_closeup_viewbox':[float(lo[0]),float(lo[1]),float(hi[0]-lo[0]),float(hi[1]-lo[1])]})
    print('Rendered',name,flush=True)

im=Image.new('RGB',(2800,1950),'#f0f4f7');d=ImageDraw.Draw(im)
txt(d,(28,20),'28 EXPANSION VERTICES / NATIVE MULTI-SIGNAL FORENSIC',36,b=True)
txt(d,(30,75),'Small dark-green circles: <=9mm core | Gold-outlined squares: >9mm expansion | Classification letters below are categories, not candidate IDs.',23)
for i,(k,label) in enumerate([('A','rounded-bulb corner'),('B','face-completion only'),('C','local shaft overreach'),('D','distal nail edge'),('E','unresolved')]):
    txt(d,(30+i*550,119),k+' = '+label,22,CLASSCOL[k],True)
for index,name in enumerate(['DORSAL','PALMAR','RADIAL','TIP']):
    focus=sorted(CV|NV); base,pts,p3,_=projection(VIEWS[name],1000,770,focus); panel=overlay(base,pts,p3,True,True)
    x=30+(index%2)*1020;y=210+(index//2)*825;im.paste(panel,(x,y));d=ImageDraw.Draw(im);txt(d,(x,y-33),name,23,b=True)
txt(d,(2110,210),'Vertex  class   g(mm)  depth(mm)',22,b=True)
for j,v in enumerate(sorted(EXP)):
    cls=R['classifications'][str(v)];txt(d,(2110,260+j*45),f'{v:4}       {cls}     {G[v]:6.3f}    {DEPTH[v]:6.3f}',20,CLASSCOL[cls],True)
txt(d,(2110,1560),'Classification is provisional.',21,b=True)
txt(d,(2110,1600),'v882: C / local distal-shaft tail',20,CLASSCOL['C'],True)
txt(d,(2110,1640),'g=15.894139; depth=11.154648',19)
txt(d,(2110,1680),'Nail member does not imply cap.',19)
txt(d,(30,1890),'Region identity remains Human-accepted. All classifications are for boundary review only. No vertex delete / blend edit / new authority.',24,b=True)
im.save(OUT/'renders/CAP_28_EXPANSION_VERTICES_FORENSIC.png')

QS=[('Q1','Current A（33-face min-corner）是否明显过度向 proximal 扩张？'),('Q2','Strict B 是否明显过小或破坏完整 distal bulb？'),
    ('Q3','Candidate C 的 topology closure 是否视觉合理？'),('Q4','Candidate D 的 curvature boundary 是否最符合 distal bulb→shaft transition？'),
    ('Q5','Candidate E 的 circumferential cut 是否形成最自然稳定的 cap edge？'),('Q6','你认为哪一个 candidate 最适合作为 production cap boundary？'),
    ('Q7','是否允许选中 candidate 进入最终 cap-authority freeze？')]
form=''
for q,t in QS:
    options=['YES','NO','UNRESOLVED'] if int(q[1:])<=5 else (list('ABCDE')+['UNRESOLVED'] if q=='Q6' else ['APPROVE_FOR_FREEZE','APPROVE_WITH_MINOR_BOUNDARY_FIX','REJECT','UNRESOLVED'])
    form+=f'<fieldset><legend>{q}. {t}</legend><select name="{q}"><option value="">尚未回答</option>'+''.join(f'<option>{s}</option>' for s in options)+'</select></fieldset>'
row=''.join(f'<tr><td style="color:{COL[k]}"><b>{k}</b></td><td>{COMP["candidates"][k]["metrics"]["vertex_count"]}</td><td>{COMP["candidates"][k]["metrics"]["face_count"]}</td><td>{COMP["candidates"][k]["metrics"]["max_geodesic_mm"]:.6f}</td><td>{COMP["candidates"][k]["metrics"]["boundary_edge_count"]}</td><td>{COMP["candidates"][k]["metrics"]["boundary_axial_spread_mm"]:.3f}</td><td>{COMP["candidates"][k]["metrics"]["bulb_coverage"]["rounded_tip_proxy_area_coverage_fraction"]*100:.2f}%</td><td>{COMP["candidates"][k]["metrics"]["thumb_nail_coverage"]["nail_compatibility"]}</td></tr>' for k in 'ABCDE')
tabs=''.join(f'<button type="button" class="view-button" data-view="{k}">{k}</button>' for k in VIEWS)
checks=''.join(f'<label style="color:{COL[k]}"><input id="toggle-{k}" type="checkbox" checked data-candidate="{k}"> {k}: {COMP["candidates"][k]["name"]}</label>' for k in 'ABCDE')
pnglinks=' · '.join(f'<a href="renders/CAP_BOUNDARY_CANDIDATES_{k}.png">{k} PNG</a>' for k in VIEWS)
forensicb64=base64.b64encode((OUT/'renders/CAP_28_EXPANSION_VERTICES_FORENSIC.png').read_bytes()).decode()
jsonlinks=' · '.join(f'<a href="{name}">{name}</a>' for name in ['CURRENT_CAP_BOUNDARY_FORENSIC.json','CAP_EXPANSION_VERTEX_CLASSIFICATION.json','CAP_BOUNDARY_CANDIDATE_COMPARISON.json','V882_BOUNDARY_FORENSIC.json'])
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>THUMB DISTAL CAP BOUNDARY REVIEW R1</title>
<style>body{margin:0;background:#eef3f6;color:#183247;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1560px;margin:auto;padding:24px}header,section{background:white;border:1px solid #d4dfe7;border-radius:12px;padding:24px;margin:0 0 22px}h1{font-size:30px;margin:0 0 16px}h2{margin:0 0 14px}.notice{padding:14px;background:#fff2df;border-left:4px solid #d79119}.controls{display:flex;flex-wrap:wrap;gap:12px;padding:12px 0}.candidates{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}label{cursor:pointer}button,select,textarea{font:inherit;border:1px solid #96aebd;border-radius:6px;padding:9px}button{cursor:pointer;background:white;color:#183247}button.active{background:#183247;color:white}.sticky{position:sticky;top:0;background:white;z-index:3;padding:14px;border-bottom:1px solid #dbe3e8}#viewer{width:100%;overflow:hidden;background:#f9f9f9;border:1px solid #d7e0e6}.native-view{display:none;width:100%;height:auto}.native-view.active{display:block}.face-fill{transition:opacity .15s}.vertex-ids,.face-ids{display:none}#viewer.boundary-only .face-fill,#viewer.boundary-only .vertices,#viewer.boundary-only .vertex-ids,#viewer.boundary-only .face-ids{display:none!important}a{color:#096579}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:8px;border:1px solid #ccd9e2;text-align:left}th{background:#edf3f7}fieldset{border:1px solid #cbd9e2;border-radius:8px;margin:15px 0;padding:16px}legend{font-weight:650}textarea{width:100%;box-sizing:border-box;height:90px}img{width:100%;height:auto}pre{white-space:pre-wrap;background:#edf3f6;padding:16px}#result{display:none}.legend{display:flex;flex-wrap:wrap;gap:16px}</style>
<main><header><h1>THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1</h1><p><b>Region identity = ACCEPTED（保持） · Boundary = UNRESOLVED · READ ONLY PRODUCTION</b></p>
<p>已读取原始 Human response：Q1=YES、Q2=YES、Q3=NO、Q4=NO、Q5=UNRESOLVED、Q6=APPROVE_WITH_BOUNDARY_REVIEW。只审最终 membership boundary，不重新询问“是不是 thumb distal cap”。</p>
<p class="notice">旧 cap9 全部 native INDEX_SURFACE，保持 CONFIRMED_CONTAMINATED。A–E 均为审阅候选，未写 production authority。E 只获得工程推荐；D 曲率/法线转折随周向/尺度变化7.5–14.0 mm，标为不能成立为唯一稳定 curvature authority，保留诊断 patch 供对照。</p>
<p>每层使用同一 native/pre-RSSF mesh。灰色 mesh 按深度显示；彩色面、边、顶点均为 X-ray 证据层，包含背面。共享 native edges 以分相虚线区分；单独开启某候选可看完整边界。IP 为继承的工程估计，未创建新 joint 权威。</p></header>
<section id="views"><h2>六方向 · 图层比较</h2><div class="sticky"><div class="controls">'''+tabs+'''</div><div class="candidates">'''+checks+'''</div><div class="controls"><label><input id="toggle-nail" type="checkbox" checked> Approved nail</label><label><input id="toggle-core" type="checkbox" checked> ≤9mm core vertices（深绿圆点）</label><label><input id="toggle-expansion" type="checkbox" checked> &gt;9mm expansion（分类方点）</label><label><input id="toggle-id" type="checkbox"> Vertex IDs</label><label><input id="toggle-face-id" type="checkbox"> Face IDs</label><label><input id="toggle-boundary" type="checkbox"> Boundary-only（隐藏面填充和顶点）</label><label><input id="toggle-closeup" type="checkbox"> Local tip closeup</label></div></div>
<div class="legend"><span style="color:#148342">扩展分类 A：rounded bulb corner</span><span style="color:#677484">B：face completion only</span><span style="color:#d33138">C：local shaft overreach</span><span style="color:#9852b3">D：distal nail edge</span><span style="color:#c78b07">E：unresolved</span></div><p>这里的 expansion 分类 A–E 与 boundary candidate A–E 是两套不同含义；所有分类均为 provisional engineering interpretation，等待 Human boundary 判断。</p>
<div id="viewer">'''+''.join(SVGS)+'''</div><p>'''+pnglinks+'''</p></section>
<section><h2>候选指标与 nail / shaft 关系</h2><div style="overflow:auto"><table><thead><tr><th>Candidate</th><th>Vertices</th><th>Faces</th><th>Max g mm</th><th>Boundary edges</th><th>Axial spread mm</th><th>Rounded-bulb proxy area coverage</th><th>Nail relationship</th></tr></thead><tbody>'''+row+'''</tbody></table></div>
<p>A/B/C/D/E 都形成单 edge-connected manifold disk、单闭环，无 edge/vertex-link 非流形。B 缺3个核心点；C 补回核心，但 rounded-bulb proxy 覆盖仅38.52%；E 保留全部核心，覆盖80.95%，与 A 的81.25%相近，避开 v39/v882/v886 三个 shaft-extension proxy 点。D 诊断 patch 更大，含7个 shaft-extension proxy 点，其唯一解剖 transition 未建立。</p>
<p>Nail 不要求全部落入 terminal cap：approved nail 沿轴向跨越3.74–19.63 mm。E boundary 与 distal nail margin edge v37–v879 相接，未改 nail；B/C 只覆盖其中 v879，完整 distal-margin 关系需 Human 特别检查。A/D 与 distal nail 面有交叠，但 nail membership 本身不能证明 cap extent。</p>
<p><b>ENGINEERING_RECOMMENDATION = E，RECOMMENDED_FOR_HUMAN_REVIEW_ONLY。</b>几何：更均匀的轴向边界、保留核心与大部分 rounded envelope；解剖：terminal tip 与 distal nail margin 相接，减少远端 shaft 尾角；拓扑：单连通 disk / 单闭环，原 mesh edges 自动决定。限制：轴估计、face-centroid staircase、curvature/normal 与 bulb coverage 均为代理，不能替代 Human freeze。</p>
<p>'''+jsonlinks+'''</p><p>'''+ ' · '.join(f'<a href="CAP_BOUNDARY_CANDIDATE_{k}.json">Candidate {k} JSON</a>' for k in 'ABCDE')+'''</p></section>
<section><h2>28 expansion vertices forensic</h2><p>20点自身≤9mm，28点因 min-corner face completion 纳入，最大15.894139mm；既不按距离直接删除，也不因连通而合理化保留。分类统计 A=15 / B=5 / C=3 / D=1 / E=4。v882 provisional=C，处于 distal nail margin / near-transverse distal-shaft continuation，仍在 IP 的 distal 侧；这不推翻已接受的 thumb cap region identity。</p><img src="data:image/png;base64,'''+forensicb64+'''" alt="28 expansion vertex forensic native multiview"><p><a href="renders/CAP_28_EXPANSION_VERTICES_FORENSIC.png">独立 forensic PNG</a></p></section>
<section id="human"><h2>Human boundary review（只问 Q1–Q7）</h2><p>答案初始为空。在浏览器本地生成记录；无网络提交，不自动冻结。Q7 的选择只是一份待提交的 Human 答案。</p><form id="human-form">'''+form+'''<label>可选说明 / narrow boundary fix vertex or face IDs<textarea name="notes"></textarea></label><button type="submit">生成 Human boundary 答案</button></form><pre id="result"></pre><button id="download-response" type="button" hidden>下载 Human boundary response JSON</button></section>
<section><b>BOUNDARY = UNRESOLVED · NEXT = MANUAL_CAP_BOUNDARY_REVIEW · STOP</b><p>既有 production / Human 原始输入 hash before==after。BLEND_FILES_WRITTEN=0；WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA=0；R1F_CREATED=false；Stage6_runs=0。旧 bound 保持 INVALIDATED AS ANATOMICAL CAP-ENDPOINT EVIDENCE；没有 replacement bound。</p><a href="THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1_REPORT.md">Review report</a></section></main>
<script>const meta='''+json.dumps(VM)+''';let current='DORSAL';const viewer=document.getElementById('viewer');function updateView(){document.querySelectorAll('.native-view').forEach(s=>s.classList.toggle('active',s.dataset.view===current));document.querySelectorAll('.view-button').forEach(b=>b.classList.toggle('active',b.dataset.view===current));const m=meta.find(x=>x.view===current);document.getElementById('view-'+current).setAttribute('viewBox',(document.getElementById('toggle-closeup').checked?m.tip_closeup_viewbox:m.full_viewbox).join(' '));}document.querySelectorAll('.view-button').forEach(b=>b.onclick=()=>{current=b.dataset.view;updateView()});document.querySelectorAll('[data-candidate]').forEach(c=>c.onchange=()=>document.querySelectorAll('.candidate-'+c.dataset.candidate).forEach(g=>g.style.display=c.checked?'':'none'));[['nail','.nail'],['core','.core'],['expansion','.expansion'],['id','.vertex-ids'],['face-id','.face-ids']].forEach(([id,cls])=>{const c=document.getElementById('toggle-'+id);c.onchange=()=>document.querySelectorAll(cls).forEach(g=>g.style.display=c.checked?'inline':'none')});document.getElementById('toggle-boundary').onchange=e=>viewer.classList.toggle('boundary-only',e.target.checked);document.getElementById('toggle-closeup').onchange=updateView;updateView();let response=null;document.getElementById('human-form').onsubmit=e=>{e.preventDefault();const f=new FormData(e.target);for(let i=1;i<=7;i++){if(!f.get('Q'+i)){alert('请填写 Q'+i+'（不确定可选 UNRESOLVED）');return}}response={review:'THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1',answers:Object.fromEntries(f),recorded_at:new Date().toISOString(),region_identity:'ACCEPTED_UNCHANGED',production_authority_applied:false};const box=document.getElementById('result');box.textContent=JSON.stringify(response,null,2);box.style.display='block';document.getElementById('download-response').hidden=false};document.getElementById('download-response').onclick=()=>{if(!response)return;const u=URL.createObjectURL(new Blob([JSON.stringify(response,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='HUMAN_THUMB_DISTAL_CAP_BOUNDARY_RESPONSE_R1.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};</script></html>'''
page=page.replace('<div id="viewer">','<p id="view-caption"></p><div id="viewer">')
page=page.replace('</style>','.closeup .landmarks text,.closeup .landmarks path:nth-of-type(2),.closeup .landmarks path:nth-of-type(3){display:none}</style>')
page=page.replace('function updateView(){','function updateView(){viewer.classList.toggle("closeup",document.getElementById("toggle-closeup").checked);document.getElementById("view-caption").textContent=current==="TIP"?"TIP 轴向视图：橙点=v284；thumb IP 与 tip 投影重合，IP→tip 轴指向观察者。":"橙点=v284；青色十字=thumb IP 工程估计；青色轴线从 IP 指向 tip。";')
page=page.replace('<p><b>ENGINEERING_RECOMMENDATION','<p class="notice">E 新增 v297/v298（faces1942/1944），未包含暂列 rounded-bulb-corner 类的 v1453/v2785/v2790。接近的 bulb proxy 面积百分比不代表相同逐点覆盖；这些差异必须由 Human 判断。</p><p><b>ENGINEERING_RECOMMENDATION')
(OUT/'THUMB_DISTAL_CAP_BOUNDARY_REVIEW.html').write_text(page,encoding='utf8')
(OUT/'NATIVE_VIEW_METADATA.json').write_text(json.dumps({'views':VM,'overlay_policy':'Depth-tested native base; X-ray SVG evidence layers including hidden surface'},indent=2),encoding='utf8')
print('Saved six overlays, expansion forensic, and self-contained interactive review HTML',flush=True)
