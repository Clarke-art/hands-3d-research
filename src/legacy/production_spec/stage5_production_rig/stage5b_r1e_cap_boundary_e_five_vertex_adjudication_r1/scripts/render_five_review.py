"""Only Human-selected E, one E_FINAL, and five disputed native vertices."""
import sys
sys.dont_write_bytecode=True
import io,base64,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from e_geometry import *
R=load(OUT/'_FIVE_RENDER_DATA.json'); ROWS=R['five_vertex_rows']; DEC=R['disputed_vertex_decisions']
BLUE='#1769cc';GREEN='#08794a';RED='#c6333e';NAIL='#a75bc1';INK='#183247';ORANGE='#ed9418';TEAL='#007483'
VIEWS={'DORSAL':np.array([0.,-1.,0.]),'PALMAR':np.array([0.,1.,0.]),'RADIAL':np.array([1.,0.,0.]),
 'ULNAR':np.array([-1.,0.,0.]),'THUMB_SIDE':unit(np.cross(AXIS,[0.,-1.,0.])),'TIP':AXIS}
FOCUS=sorted(BASEV|FIVE|NV|{min(range(len(V)),key=lambda i:np.linalg.norm(V[i]-IP))})
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf',n)
def txt(d,xy,text,size=22,color=INK,bold=False):d.text(xy,text,font=font(size,bold),fill=color)
def project(normal,w,h):
 view=unit(normal);right=unit(np.cross([0.,0.,1.],view));up=unit(np.cross(view,right));xy=np.stack([V@right,V@up],axis=1);z=V@view
 limits=xy[FOCUS];mid=(limits.min(0)+limits.max(0))/2;scale=min((w-240)/max(np.ptp(limits[:,0]),1e-5),(h-150)/max(np.ptp(limits[:,1]),1e-5))
 def p3(p):return np.array([(w-140)/2+(p@right-mid[0])*scale,h/2-(p@up-mid[1])*scale])
 pts=np.array([p3(p) for p in V]);pix=np.full((h,w,3),249,dtype=np.uint8);zb=np.full((h,w),-np.inf)
 for fi,vs in enumerate(F):
  gray=int(175+58*abs(FN[fi]@view));col=np.array([gray,min(gray+4,255),min(gray+8,255)])
  for j in range(1,len(vs)-1):
   ids=[vs[0],vs[j],vs[j+1]];p=pts[ids];x0=max(0,int(np.floor(p[:,0].min())));x1=min(w-1,int(np.ceil(p[:,0].max())));y0=max(0,int(np.floor(p[:,1].min())));y1=min(h-1,int(np.ceil(p[:,1].max())))
   if x1<x0 or y1<y0:continue
   den=(p[1,1]-p[2,1])*(p[0,0]-p[2,0])+(p[2,0]-p[1,0])*(p[0,1]-p[2,1])
   if abs(den)<1e-8:continue
   yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5
   a=((p[1,1]-p[2,1])*(xx-p[2,0])+(p[2,0]-p[1,0])*(yy-p[2,1]))/den;b=((p[2,1]-p[0,1])*(xx-p[2,0])+(p[0,0]-p[2,0])*(yy-p[2,1]))/den;c=1-a-b
   depth=a*z[ids[0]]+b*z[ids[1]]+c*z[ids[2]];region=zb[y0:y1+1,x0:x1+1];mask=(a>=0)&(b>=0)&(c>=0)&(depth>region)
   region[mask]=depth[mask];pix[y0:y1+1,x0:x1+1][mask]=col
 im=Image.fromarray(pix);d=ImageDraw.Draw(im)
 for a,b in ED:
  p=(pts[a]+pts[b])/2;x,y=map(int,p)
  if 0<=x<w and 0<=y<h and (z[a]+z[b])/2>=zb[y,x]-.7:d.line([tuple(pts[a]),tuple(pts[b])],fill='#b1bbc4',width=1)
 return im,pts,p3,{'toward_viewer_unit':view.tolist(),'right_unit':right.tolist(),'up_unit':up.tolist(),'pixels_per_mm':scale}
def segmented(d,a,b,color,offset,width=4):
 a=np.array(a);b=np.array(b);dist=np.linalg.norm(b-a)
 for t in np.arange(-24+offset,dist,24):
  lo=max(0,t);hi=min(dist,t+12)
  if hi>lo:d.line([tuple(a+(b-a)*lo/max(dist,1)),tuple(a+(b-a)*hi/max(dist,1))],fill=color,width=width)
def overlay(im,p,p3):
 layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer)
 for fi in BASEF:ld.polygon([tuple(p[v]) for v in F[fi]],fill=(10,135,83,28))
 for fi in NF:ld.polygon([tuple(p[v]) for v in F[fi]],fill=(166,76,190,94))
 im=Image.alpha_composite(im.convert('RGBA'),layer);d=ImageDraw.Draw(im)
 for fi in NF:
  points=[tuple(p[v]) for v in F[fi]];d.line(points+[points[0]],fill=NAIL,width=2)
 for a,b in R['baseline_boundary_edges']:segmented(d,p[a],p[b],BLUE,0,4)
 for a,b in R['final_boundary_edges']:segmented(d,p[a],p[b],GREEN,12,4)
 ip=p3(IP);tip=p[SEED];d.line([tuple(ip),tuple(tip)],fill=TEAL,width=3)
 x,y=ip;d.line([(x-8,y),(x+8,y)],fill=TEAL,width=3);d.line([(x,y-8),(x,y+8)],fill=TEAL,width=3)
 tx,ty=tip;d.ellipse((tx-7,ty-7,tx+7,ty+7),fill=ORANGE,outline='white',width=2)
 txt(d,(15,15),'Native IP / IP-to-tip axis (inherited)',18,TEAL,True);d.line([(20,45),tuple(ip)],fill=TEAL,width=1)
 txt(d,(15,im.height-45),'seed v284 / tip axis toward viewer' if np.linalg.norm(ip-tip)<4 else 'seed v284 = orange | IP-to-tip line = teal',18,ORANGE,True)
 for i,r in enumerate(ROWS):
  v=r['vertex_id'];col=GREEN if DEC[str(v)]=='KEEP' else RED;x,y=p[v];rad=7
  d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=col,outline='white',width=2)
  labelx=im.width-260;labely=85+i*100
  d.line([(x,y),(labelx-8,labely+12)],fill=col,width=2)
  txt(d,(labelx,labely),f'v{v} {DEC[str(v)]}',22,col,True)
 return im.convert('RGB')
SVGS=[];METADATA=[];pngs=[]
for name,normal in VIEWS.items():
 base,p,p3,meta=project(normal,1360,900);annotated=overlay(base,p,p3)
 im=Image.new('RGB',(2100,1220),'#f1f5f8');d=ImageDraw.Draw(im)
 txt(d,(30,20),'E BASELINE / E_FINAL / FIVE VERTICES / '+name,34,bold=True)
 txt(d,(32,74),'Native / pre-RSSF | Human E baseline selected | Only five disputed membership decisions | Production unchanged',22)
 txt(d,(32,116),'Blue dashed = E baseline | Green phased = E_FINAL (same boundary) | Red = REMOVE from cap | Green dots = KEEP',22)
 txt(d,(32,156),'All colored overlays are X-ray, including hidden surface. Grey native surface is depth-tested. Purple = approved nail.',21)
 im.paste(annotated,(30,220));d=ImageDraw.Draw(im)
 txt(d,(1430,225),'ENGINEERING ADJUDICATION',25,bold=True)
 for i,r in enumerate(ROWS):
  v=r['vertex_id'];col=GREEN if DEC[str(v)]=='KEEP' else RED; y=282+i*122
  txt(d,(1430,y),f'v{v}: {DEC[str(v)]}',25,col,True)
  txt(d,(1430,y+35),f'g {r["geodesic_from_v284_mm"]:.6f} mm',20)
  txt(d,(1430,y+65),f'axis depth {r["axial_depth_from_tip_mm"]:.6f} mm',20)
 txt(d,(1430,938),'E_FINAL = 37 vertices / 25 faces',22,bold=True)
 txt(d,(1430,976),'Single disk / one loop / nail edge preserved',20)
 txt(d,(32,1140),'No vertex is deleted from the mesh. KEEP/REMOVE refers only to proposed cap membership. No authority applied.',22,bold=True)
 txt(d,(32,1180),'READY FOR HUMAN FREEZE REVIEW ONLY | STOP | No R3 / weights / Stage6 / strict-bound / retopo changes',21)
 filename='E_FIVE_VERTEX_'+name+'_CLOSEUP.png';im.save(OUT/'renders'/filename);pngs.append(filename)
 bio=io.BytesIO();base.save(bio,format='PNG');embedded=base64.b64encode(bio.getvalue()).decode()
 parts=[f'<svg class="native-view" id="view-{name}" data-view="{name}" viewBox="0 0 1360 900" xmlns="http://www.w3.org/2000/svg"><image width="1360" height="900" href="data:image/png;base64,{embedded}"/>']
 def poly(fi):return ' '.join(f'{p[v,0]:.2f},{p[v,1]:.2f}' for v in F[fi])
 parts.append('<g class="nail">')
 for fi in NF:parts.append(f'<polygon points="{poly(fi)}" fill="{NAIL}" fill-opacity=".3" stroke="{NAIL}" stroke-width="2"/>')
 parts.append('</g>')
 for family,edges,color,offset in [('baseline',R['baseline_boundary_edges'],BLUE,0),('final',R['final_boundary_edges'],GREEN,-12)]:
  parts.append(f'<g class="{family}">')
  if family=='final':
   for fi in BASEF:parts.append(f'<polygon points="{poly(fi)}" fill="{GREEN}" fill-opacity=".07"/>')
  for a,b in edges:parts.append(f'<path d="M{p[a,0]:.2f} {p[a,1]:.2f} L{p[b,0]:.2f} {p[b,1]:.2f}" fill="none" stroke="{color}" stroke-width="4" stroke-dasharray="12 12" stroke-dashoffset="{offset}"/>')
  parts.append('</g>')
 parts.append('<g class="disputed">')
 for i,r in enumerate(ROWS):
  v=r['vertex_id'];col=GREEN if DEC[str(v)]=='KEEP' else RED;x,y=p[v];lx=1100;ly=85+i*100
  parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="7" fill="{col}" stroke="white" stroke-width="2"><title>v{v} recommendation {DEC[str(v)]}</title></circle><path d="M{x:.2f} {y:.2f} L{lx-8} {ly+12}" stroke="{col}" stroke-width="2"/><text x="{lx}" y="{ly+20}" font-size="24" fill="{col}" stroke="white" stroke-width="3" paint-order="stroke">v{v} {DEC[str(v)]}</text>')
 parts.append('</g><g class="landmarks">');ip=p3(IP);tip=p[SEED];x,y=ip;tx,ty=tip
 parts.append(f'<path d="M{x:.2f} {y:.2f} L{tx:.2f} {ty:.2f} M{x-8:.2f} {y:.2f} h16 M{x:.2f} {y-8:.2f} v16" stroke="{TEAL}" stroke-width="3"/><circle cx="{tx:.2f}" cy="{ty:.2f}" r="7" fill="{ORANGE}" stroke="white" stroke-width="2"/>')
 parts.append(f'<text x="16" y="28" font-size="20" fill="{TEAL}">Native IP engineering estimate / IP→tip axis</text><path d="M20 40 L{x:.2f} {y:.2f}" stroke="{TEAL}"/>')
 parts.append(f'<text x="16" y="875" font-size="20" fill="{ORANGE}">'+('v284 orange / IP→tip axis toward viewer (axial projection)' if np.linalg.norm(ip-tip)<4 else 'v284 orange / teal line from IP cross to tip')+'</text></g></svg>')
 SVGS.append(''.join(parts));METADATA.append({'view':name,'camera_basis':meta,'png':'renders/'+filename})
 print('Rendered five-vertex',name,flush=True)
sheet=Image.new('RGB',(2100,2000),'white');dd=ImageDraw.Draw(sheet)
txt(dd,(25,12),'E FIVE-VERTEX / SIX NATIVE CLOSEUPS (zoom individual PNGs for IDs)',26,bold=True)
for i,name in enumerate(pngs):
 a=Image.open(OUT/'renders'/name);a.thumbnail((1050,610));sheet.paste(a,((i%2)*1050,80+(i//2)*635))
sheet.save(OUT/'renders/E_FIVE_VERTEX_NATIVE_MULTIVIEW_CONTACT_SHEET.png')
tabs=''.join(f'<button class="view-button" type="button" data-view="{name}">{name}</button>' for name in VIEWS)
table=''.join(f'<tr><td>v{r["vertex_id"]}</td><td><b>{r["decision"]}</b></td><td>{r["geodesic_from_v284_mm"]:.6f}</td><td>{r["euclidean_tip_distance_mm"]:.6f}</td><td>{r["axial_depth_from_tip_mm"]:.6f}</td><td>{r["circumferential_angle_deg"]:.2f}°</td><td>{r["nail_relation"]}</td></tr>' for r in ROWS)
form=''
for i,v in enumerate([1453,2785,2790,297,298],1):form+=f'<fieldset><legend>Q{i}. v{v} KEEP / REMOVE</legend><select name="Q{i}"><option value="">尚未回答</option><option>KEEP</option><option>REMOVE</option></select></fieldset>'
form+='<fieldset><legend>Q6. E_FINAL boundary 是否视觉合理？</legend><select name="Q6"><option value="">尚未回答</option><option>YES</option><option>NO</option><option>UNRESOLVED</option></select></fieldset><fieldset><legend>Q7. 是否批准进入 HUMAN_CAP_AUTHORITY_FREEZE？</legend><select name="Q7"><option value="">尚未回答</option><option>APPROVE_FOR_FREEZE</option><option>REJECT</option><option>UNRESOLVED</option></select></fieldset>'
links=' · '.join(f'<a href="renders/{name}">{view} PNG</a>' for view,name in zip(VIEWS,pngs))
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>CAP BOUNDARY E FIVE VERTEX REVIEW</title><style>body{margin:0;background:#edf3f7;color:#183247;font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1480px;margin:auto;padding:24px}header,section{padding:24px;background:white;border:1px solid #d0dce6;border-radius:12px;margin-bottom:24px}h1{font-size:29px;margin:0 0 14px}h2{margin:0 0 14px}.notice{background:#edf8f3;border-left:4px solid #08794a;padding:14px}.controls{display:flex;flex-wrap:wrap;gap:12px;padding:12px 0}button,select,textarea{font:inherit;padding:10px;border:1px solid #99afbd;border-radius:6px}button{cursor:pointer;background:white;color:#183247}button.active{background:#183247;color:white}.native-view{display:none;width:100%;height:auto}.native-view.active{display:block}#viewer{border:1px solid #d3dfe8;background:#f9f9f9}a{color:#08697e}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #cbd9e3;padding:8px;text-align:left}th{background:#edf3f7}fieldset{margin:16px 0;border:1px solid #cbd9e3;border-radius:8px;padding:16px}legend{font-weight:650}textarea{width:100%;box-sizing:border-box;height:80px}pre{white-space:pre-wrap;background:#edf3f7;padding:16px}#result{display:none}</style><main>
<header><h1>CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1</h1><p><b>Candidate E = SELECTED_HUMAN_BASELINE · Region identity = ACCEPTED_UNCHANGED · Production authority = NOT APPLIED</b></p><p>原始 Human boundary response：Q1=YES / Q2=YES / Q3=NO / Q4=NO / Q5=YES / Q6=E / Q7=APPROVE_WITH_MINOR_BOUNDARY_FIX。仅审 v1453、v2785、v2790、v297、v298，其它 E membership 保持。</p>
<p class="notice"><b>工程建议：REMOVE v1453/v2785/v2790；KEEP v297/v298。</b>裁决后的 E_FINAL 与 E baseline membership 相同，仍37点/25面。REMOVE 是不纳入 cap，绝非删除 native mesh 顶点。READY_FOR_HUMAN_CAP_AUTHORITY_FREEZE 只表示可交 Human 审阅，本页不执行 freeze。</p><p>保留 rounded-bulb 形状证据，不将 &gt;9mm 当删除标准。v1453/v2785 的唯一合法补面是耦合 face1220，产生两个凹口代理；v2790 没有不引入其它顶点的合法支持面。删除 v297/v298 虽仍闭环，但产生向内凹口。</p></header>
<section id="views"><h2>只比较 E baseline / E_FINAL / 五个 disputed vertices</h2><div class="controls">'''+tabs+'''</div><div class="controls"><label><input id="toggle-baseline" type="checkbox" checked> E baseline 蓝色虚线</label><label><input id="toggle-final" type="checkbox" checked> E_FINAL 绿色分相线/浅色面</label><label><input id="toggle-disputed" type="checkbox" checked> 五个 disputed IDs</label><label><input id="toggle-nail" type="checkbox" checked> Approved nail 紫色</label></div><p>彩色点/边/面为 X-ray 投影，包括隐藏表面；灰色 native mesh 深度显示。蓝/绿边界完全重合，用虚线相位区分。橙点=v284，青色=继承的 native IP 与 IP→tip 轴；TIP 视角中 IP 与 tip 的投影重合、轴指向观察者。</p><div id="viewer">'''+''.join(SVGS)+'''</div><p>'''+links+''' · <a href="renders/E_FIVE_VERTEX_NATIVE_MULTIVIEW_CONTACT_SHEET.png">六方向 contact sheet</a></p></section>
<section><h2>五点事实与裁决依据</h2><div style="overflow:auto"><table><thead><tr><th>Vertex</th><th>建议</th><th>Geodesic mm</th><th>Tip Euclidean mm</th><th>Axis depth mm</th><th>Circumferential angle</th><th>Nail relation</th></tr></thead><tbody>'''+table+'''</tbody></table></div>
<p><b>v1453：</b>baseline v1382–v341 接续转角22.887°/12.272°，没有明显 missing-corner notch。加 face1220 需同时 KEEP v2785，形成两个新凹口端点，perimeter增加8.693155mm；它有 rounded skin 证据，但并非本 cap edge 必须包含。</p><p><b>v2785：</b>有 tip-facing bulb-side 证据。耦合补面后自身转角115.272°，端点 v1382/v341 intrinsic角和281.477°/260.463°，属局部 tab，不宜为恢复 curved skin 而强行纳入。</p><p><b>v2790：</b>仍是 frozen native THUMB bulb-side 点；四个 incident faces 均需要五点之外的未批准 corner（例如 face1243 需要 v1342）。在本轮限制下不能构建合法 KEEP。未改其它 membership。</p><p><b>v297：</b>保留 face1942 的 rounded ring completion；删除会在 v2965 产生279.457° intrinsic notch。<b>v298：</b>保留 face1944；删除会在 v2966 产生266.588° notch。删除两者均仍单连通/单闭环，因此 KEEP 的依据是自然边界形状，而不是虚称拓扑闭合必需。</p>
<p>Five-point vicinity 中 final boundary 无局部 spike/notch proxy，全部 boundary degree=2；seed 与 approved distal nail-margin edge v37–v879 保持。E_FINAL max g=13.367420mm、axial spread=3.767492mm、surface area=182.066159mm²、perimeter=48.760464mm。</p><p><a href="FIVE_VERTEX_INDIVIDUAL_FORENSIC.json">逐点 forensic JSON</a> · <a href="E_FIVE_VERTEX_VARIANT_ANALYSIS.json">add-one / leave-one / necessary paired consistency</a> · <a href="NATIVE_THUMB_DISTAL_CAP_CANDIDATE_E_FINAL.json">E_FINAL JSON</a> · <a href="E_FINAL_BOUNDARY_TOPOLOGY_AUDIT.json">Topology / smoothness audit</a> · <a href="CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1_REPORT.md">报告</a></p></section>
<section id="human"><h2>Human 五点裁决与 Freeze 前确认</h2><p>全部答案初始为空，模型建议不是已记录的 Human 答案。只能在本地生成记录，不上传、不修改 production。</p><form id="human-form">'''+form+'''<label>可选说明<textarea name="notes"></textarea></label><button type="submit">生成 Human 五点答案记录</button></form><pre id="result"></pre><button id="download-response" type="button" hidden>下载 Human five-vertex response JSON</button></section><section><b>STOP — WAITING FOR HUMAN FIVE-VERTEX REVIEW</b><p>旧 cap9 保持 INVALID；R3、first web、CMC cage、RSSF、其它区域不重开。BLEND_FILES_WRITTEN=0；全部 DELTA=0；R1F_CREATED=false；Stage6_runs=0；未重算 strict bound 或 retopo；没有 production cap authority 写入。</p></section></main>
<script>let current='DORSAL';function show(){document.querySelectorAll('.native-view').forEach(s=>s.classList.toggle('active',s.dataset.view===current));document.querySelectorAll('.view-button').forEach(b=>b.classList.toggle('active',b.dataset.view===current))}document.querySelectorAll('.view-button').forEach(b=>b.onclick=()=>{current=b.dataset.view;show()});show();for(const name of ['baseline','final','disputed','nail']){const c=document.getElementById('toggle-'+name);c.onchange=()=>document.querySelectorAll('.'+name).forEach(g=>g.style.display=c.checked?'':'none')}let response=null;document.getElementById('human-form').onsubmit=e=>{e.preventDefault();const data=new FormData(e.target);for(let i=1;i<=7;i++){if(!data.get('Q'+i)){alert('请回答 Q'+i);return}}const answers=Object.fromEntries(data);const agree=answers.Q1==='REMOVE'&&answers.Q2==='REMOVE'&&answers.Q3==='REMOVE'&&answers.Q4==='KEEP'&&answers.Q5==='KEEP';response={review:'CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1',answers,recorded_at:new Date().toISOString(),matches_presented_E_FINAL:agree,selected_E_FINAL_membership_changed:false,production_authority_applied:false,authority_freeze_performed:false};if(!agree)response.followup='Human answers differ from presented E_FINAL. Require a face-consistent narrow review before freeze; this page does not change the shown patch.';document.getElementById('result').textContent=JSON.stringify(response,null,2);document.getElementById('result').style.display='block';document.getElementById('download-response').hidden=false};document.getElementById('download-response').onclick=()=>{if(!response)return;const url=URL.createObjectURL(new Blob([JSON.stringify(response,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='HUMAN_CAP_BOUNDARY_E_FIVE_VERTEX_RESPONSE_R1.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};</script></html>'''
(OUT/'CAP_BOUNDARY_E_FIVE_VERTEX_REVIEW.html').write_text(page,encoding='utf8')
(OUT/'NATIVE_FIVE_VERTEX_VIEW_METADATA.json').write_text(json.dumps({'views':METADATA,'overlay_policy':'X-ray colored layers on depth-tested native surface','displayed_candidates':['E_BASELINE','E_FINAL']},indent=2),encoding='utf8')
print('Saved six native closeups, contact sheet and five-vertex Human page',flush=True)
