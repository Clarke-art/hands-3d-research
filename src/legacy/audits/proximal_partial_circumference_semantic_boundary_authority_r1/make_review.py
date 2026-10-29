import sys
sys.dont_write_bytecode=True
import json,base64,html
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
NAME='PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def datauri(p,mime):return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
d=read(OUT/'REVIEW_VIEW_DATA.json');d['flow']=read(OUT/'LOCAL_SURFACE_FLOW_R1.json')['states']
logic=(OUT/'review_logic.js').read_text(encoding='utf8')
images={p.stem:datauri(p,'image/png') for p in (OUT/'renders').glob('*.png')}
cards=[]
for q in d['boundaries']:
    opt=q['option']; es=q['boundary_edges'];row1,row2=q['row_pair']
    cards.append(f'''<label class="answer-card"><input type="radio" name="selected_option" value="{opt}" required><span class="option-tag">OPTION {opt}</span><strong>{q['stop']}</strong><span>{row1} / {row2}</span><small>e{es[0]['edge_id']} / e{es[1]['edge_id']}</small></label>''')
cards.append('''<label class="answer-card"><input type="radio" name="selected_option" value="D" required><span class="option-tag">OPTION D</span><strong>KEEP_UNRESOLVED</strong><span>保留未决</span><small>不建立边界 authority</small></label>''')
comparisons=[]
for q in d['boundaries']:
    es=q['boundary_edges']; opt=q['option']; rows=' / '.join(q['row_pair']);trans='；'.join(str(e['before_face_id'])+' → '+str(e['after_face_id']) for e in es)
    comparisons.append(f'''<details class="evidence-card"><summary>Option {opt} · {rows} · closeup</summary><p>left e{es[0]['edge_id']} = {es[0]['vertex_ids']}；right e{es[1]['edge_id']} = {es[1]['vertex_ids']}。面转换：{trans}。两侧 exact anatomical role 均未被机器唯一证明。</p><img src="{images['OPTION_'+opt+'_CLOSEUP']}" alt="Option {opt} native/RSSF boundary closeup"></details>''')
question=lambda ident,title: f'''<label class="question" for="{ident}"><span>{title}</span><select id="{ident}" name="{ident}" required><option value="">请选择 / 尚未判断</option><option value="YES">YES · 可接受</option><option value="NO">NO · 不可接受</option><option value="UNRESOLVED">UNRESOLVED · 仍无法判断</option></select></label>'''
refs=ROOT/'production_spec/stage5_production_rig/stage5b_r1e_manual_anatomical_reference_review_r1/references'
dorsal=datauri(refs/'male_both_sides.jpg','image/jpeg');palmar=datauri(refs/'Hand female 5.jpg','image/jpeg')
document=r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Proximal boundary · Human anatomical adjudication</title><style>
:root{color-scheme:light;--ink:#203447;--muted:#5c7082;--line:#d8e1e7;--bg:#f3f6f8;--accent:#305f7b}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1420px;margin:auto;padding:36px 30px 80px}h1{font-size:clamp(27px,3.2vw,43px);line-height:1.25;margin:12px 0 16px}h2{font-size:23px;margin:0 0 13px}h3{font-size:18px;margin:0 0 10px}.eyebrow{color:var(--muted);font-size:12px;letter-spacing:.09em}p{margin:10px 0}.notice{border-left:4px solid #66758a;background:#e9eef3;padding:15px 20px;border-radius:4px;max-width:1100px}.muted{color:var(--muted)}.section{margin-top:28px;padding:24px;background:#fff;border:1px solid var(--line);border-radius:12px}.toolbar{display:flex;flex-wrap:wrap;gap:15px;align-items:center;margin:16px 0}.toolbar label{display:flex;gap:7px;align-items:center}button,select,textarea{font:inherit}button{background:#fff;color:var(--ink);border:1px solid #b7c9d4;padding:8px 15px;border-radius:6px;cursor:pointer}button:hover{background:#edf3f6}button:focus-visible,select:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid #6599c0;outline-offset:3px}button.primary{background:#244f69;color:white;border-color:#244f69;padding:12px 20px;font-weight:650}.view-buttons{display:flex;gap:7px;flex-wrap:wrap}.view-buttons button[aria-pressed=true]{background:#dceaf2;border-color:#517e9a}select{padding:7px 10px;border:1px solid #b7c9d4;border-radius:6px;background:#fff;max-width:100%}.viewgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.viewport{border:1px solid var(--line);border-radius:9px;overflow:hidden;background:#f9fbfd}.viewport h3{margin:0;padding:9px 15px;background:#edf2f6}canvas{display:block;width:100%;height:480px;touch-action:none;cursor:grab}.viewport small{display:block;padding:9px 13px;min-height:60px;background:white}.legend{display:flex;flex-wrap:wrap;gap:16px;font-size:13px}.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px}.line{display:inline-block;width:20px;border-top:3px solid;margin-right:5px}img{display:block;width:100%;height:auto;border-radius:6px}details{margin-top:15px;border:1px solid var(--line);border-radius:8px;padding:14px}summary{font-weight:650;cursor:pointer}details p{font-size:14px}.answer-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin:18px 0}.answer-card{position:relative;display:flex;flex-direction:column;gap:6px;min-height:180px;padding:17px;border:1px solid #c5d2dc;border-radius:9px;cursor:pointer}.answer-card input{position:absolute;right:14px;top:15px;width:20px;height:20px}.answer-card:has(input:checked){outline:3px solid #4d7c97;background:#f0f7fa}.option-tag{font-size:12px;letter-spacing:.08em;color:var(--muted)}.answer-card strong{font-size:15px;overflow-wrap:anywhere}.answer-card small{color:var(--muted)}.question{display:grid;grid-template-columns:minmax(300px,1fr) minmax(230px,330px);gap:20px;padding:15px 0;border-top:1px solid var(--line);align-items:center}.question span{font-weight:600}.boundary-readout{padding:12px 16px;background:#f0f4f7;border-radius:6px;margin:15px 0}textarea{width:100%;min-height:105px;padding:12px;border:1px solid #b7c9d4;border-radius:6px;resize:vertical}#response-preview{min-height:280px;font:12px/1.55 Consolas,monospace}#form-status{min-height:28px;white-space:pre-wrap;margin-top:12px;color:#8d3647}.refgrid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.refgrid svg{display:block;width:100%;height:480px;background:#edf1f4}.refgrid a{color:#335d7a}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;text-align:left;border-bottom:1px solid var(--line)}code{overflow-wrap:anywhere}.validation{background:#fff0d3;border:2px solid #a77415;padding:14px;display:none}.validation.visible{display:block}footer{font-size:13px;color:var(--muted);margin-top:24px}@media(max-width:900px){main{padding:22px 14px 50px}.section{padding:17px}.viewgrid,.refgrid{grid-template-columns:1fr}.answer-grid{grid-template-columns:1fr 1fr}.question{grid-template-columns:1fr;gap:8px}canvas{height:410px}.refgrid svg{height:350px}}@media(max-width:520px){.answer-grid{grid-template-columns:1fr}.answer-card{min-height:130px}canvas{height:350px}}
</style></head><body><main>
<div class="eyebrow">EXACT-FACE REVIEW · P02–P06 · 2026-10-03</div><h1>拇指局部扇区 → 更宽共享界面<br>Human anatomical adjudication</h1>
<p class="muted">PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW_R1</p>
<div class="notice">机器未取得唯一 anatomical role boundary。三条真实边对均保持未决；页面没有预选答案。请判断表面组织的角色变化，允许选择 D 保留未决。批准范围仅限 thumb shared-strip proximal semantic stop。</div>
<p id="validation-notice" class="validation">AUTOMATED UI VALIDATION — 测试模式，不下载文件，不记录 Human decision；所有测试答复禁止作为 authority。</p>
<section class="section"><h2>1 · 并排查看同 ID 表面</h2><p class="muted">拖动旋转，滚轮缩放。视图、显示边界和 zoom 的操作不填写审阅答案。浅色面用于定位行，颜色不表示 ownership；局部显示可见背面诊断叠加。</p>
<div class="view-buttons" id="view-buttons"><button type="button" data-view="DORSAL" aria-pressed="true">Dorsal / nail侧</button><button type="button" data-view="PALMAR" aria-pressed="false">Palmar / opposite侧</button><button type="button" data-view="RADIAL" aria-pressed="false">Radial / away-web侧</button><button type="button" data-view="ULNAR" aria-pressed="false">Ulnar / web侧</button></div>
<div class="toolbar"><label for="display-boundary">显示边界<select id="display-boundary"><option value="ALL">A + B + C 总览</option><option value="A">A · P03 / P04</option><option value="B">B · P04 / P05</option><option value="C">C · P05 / P06</option></select></label><label for="zoom-scope">范围<select id="zoom-scope"><option value="LOCAL">P02–P06 局部</option><option value="CONTEXT">冻结 landmarks 位置上下文</option></select></label><label><input id="show-labels" type="checkbox" checked>显示 IDs</label><label><input id="show-flow" type="checkbox">surface-flow arrows</label><button type="button" id="reset-camera">重置视角</button></div>
<div class="legend"><span><i class="line" style="color:#2470b5"></i>A e1375 / e1374</span><span><i class="line" style="color:#b76a16"></i>B e4666 / e4668</span><span><i class="line" style="color:#8c4ab4"></i>C e1376 / e1377</span><span><i class="dot" style="background:#086f65"></i>FIRST_WEB frozen seeds</span><span><i class="dot" style="background:#67b7c6"></i>thumb nail</span><span><i class="dot" style="background:#b9a4d5"></i>cap37</span></div>
<div class="viewgrid"><div class="viewport"><h3>NATIVE · original topology</h3><canvas id="native-canvas" aria-label="Native exact-face anatomical reference viewer"></canvas><small>Approved corrected distal-axis orientation 通过相同 frozen nail IDs 搬运，仅作方向 reference。native corrected MCP/CMC 位置没有批准的注册；精确关节 marker 见 RSSF 伴随视图。</small></div><div class="viewport"><h3>RSSF · approved corrected structure</h3><canvas id="rssf-canvas" aria-label="RSSF exact-face anatomical reference viewer"></canvas><small>MCP、CMC、thumb distal direction 使用批准的 corrected structure。切换「位置上下文」可同时看到 nail、cap37 和 frozen web seeds。方向轴不等于 palm normal。</small></div></div>
<p class="muted">侧名由拇指局部 nail／frozen-web reference 定义，不声称是全掌表面法向。全部上下文表面只用于观看，不建立新的 palm role domain。</p>
</section>
<section class="section"><h2>2 · 三条边界与两端 controls</h2><details open><summary>三候选叠加总览 · native / RSSF</summary><img src="@@OVERVIEW@@" alt="Three candidate edge-pair overlay overview"></details>@@COMPARISONS@@
<details><summary>P02 early-side control</summary><p>只需判断主导组织仍是 thumb-local digit/web sector；不要求完全没有 broader influence。机器未能认证其主导角色。</p><img src="@@P02@@" alt="P02 early side control native and RSSF"></details>
<details><summary>P06 late-side control</summary><p>需要正向 broader-interface 证据，不能以 post-reversal 或“不像 digit”替代。</p><img src="@@P06@@" alt="P06 late side control native and RSSF"></details>
<details><summary>Native · palmar / dorsal / radial / ulnar</summary><img src="@@NATIVE@@" alt="Native four anatomical reference views"></details>
<details><summary>RSSF · palmar / dorsal / radial / ulnar</summary><img src="@@RSSF@@" alt="RSSF four anatomical reference views"></details>
<details><summary>FIRST_WEB seeds · nail · cap37 · MCP / CMC context</summary><img src="@@CONTEXT@@" alt="Frozen anatomical landmark context"></details>
<details><summary>Exact-face evidence table</summary><table><thead><tr><th>Row</th><th>Face IDs</th><th>Exact anatomical role</th><th>Local organization</th></tr></thead><tbody><tr><td>P02</td><td>1372 / 1375</td><td>AMBIGUOUS</td><td>digit-web compatible；dominant role not certified</td></tr><tr><td>P03</td><td>1373 / 1374</td><td>AMBIGUOUS</td><td>digit-web support + morphology transition</td></tr><tr><td>P04</td><td>1368 / 1371</td><td>AMBIGUOUS</td><td>paired two-lane surface continuation</td></tr><tr><td>P05</td><td>1369 / 1370</td><td>AMBIGUOUS</td><td>per-face mixed descriptive field</td></tr><tr><td>P06</td><td>1378 / 1377</td><td>AMBIGUOUS</td><td>positive broader role not proven</td></tr></tbody></table><p>已有几何转向、法向和 widening 数据只作描述；本页面不以它们排名或推荐任何答案。</p></details>
</section>
<section class="section"><h2>3 · 有出处的外观与 anatomical reference</h2><p>照片来自其他真实手，既有 landmarks 尚待 Human registration。请用它们理解 surface organization，不能将照片位置直接转成 mesh ID。</p><details><summary>背侧 / 掌侧真实外观参考 · CC BY-SA 4.0</summary><div class="refgrid"><figure><svg viewBox="0 0 2505 3296" role="img" aria-label="Right-hand dorsal photograph reference"><image width="5313" height="3296" href="@@DORSALPHOTO@@"></image></svg><figcaption>Sciencia58 · <a href="https://commons.wikimedia.org/wiki/File:Hand_male_both_sides.jpg" target="_blank" rel="noopener">Hand male both sides</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>。原图保留；仅 viewport 显示右手背侧部分。</figcaption></figure><figure><svg viewBox="0 0 3472 4424" role="img" aria-label="Right-hand palmar photograph reference"><image width="3472" height="4424" href="@@PALMARPHOTO@@"></image></svg><figcaption>Sciencia58 · <a href="https://commons.wikimedia.org/wiki/File:Hand_female_5.jpg" target="_blank" rel="noopener">Hand female 5</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>。没有将照片注册到本模型。</figcaption></figure></div></details>
<p><a href="https://pubmed.ncbi.nlm.nih.gov/3767503/" target="_blank" rel="noopener">Kapandji (1986), Functional anatomy of the first web space</a> 的 indexed abstract 支持 first-web 功能涉及关节、肌筋膜、web integument 和 thenar aponeurotic system；不提供本模型边界 ID。</p>
<p><a href="https://pubmed.ncbi.nlm.nih.gov/39084025/" target="_blank" rel="noopener">Measurement and observation of the first web space (2024)</a> 的 indexed abstract excerpt 提示皮肤形态可不对称，并受 palmar-abduction 参考姿态影响；不支持把 chain 视为完美圆柱。查阅日：2026-10-03；直接页面遇 CAPTCHA，未检查 full text。</p></section>
<section class="section" id="human-response"><h2>4 · 填写 Human adjudication</h2><p>没有预选答案。选定边界后，Q3 自动记录对应的原始 edge IDs，避免填写不一致。导出只保存答复，不自动应用任何 authority 或 production 修改。</p>
<form id="review-form"><fieldset style="border:0;margin:0;padding:0"><legend>选择 A / B / C / D</legend><div class="answer-grid">@@CARDS@@</div></fieldset>
@@Q1@@@@Q2@@<div class="boundary-readout" id="boundary-readout" aria-live="polite">Q3 · 尚未选择 boundary</div>@@Q4@@
<label class="question" for="Q5_approve_for_boundary_authority"><span>Q5 · 是否批准所选 boundary authority？</span><select id="Q5_approve_for_boundary_authority" name="Q5_approve_for_boundary_authority" required><option value="">请选择 / 尚未判断</option><option value="APPROVE_BOUNDARY_ONLY">APPROVE · 仅 proximal semantic stop</option><option value="REJECT">REJECT · 拒绝</option><option value="KEEP_UNRESOLVED">KEEP_UNRESOLVED · 保留未决</option></select></label>
<p class="muted">批准 A/B/C 需 Q1、Q2、Q4 均为 YES。D 可导出未决答复，不能同时批准边界。FIRST_WEB21、cap37、nail、rig、CMC cage、distal stop、lateral、weights、R3 等不在批准范围。</p>
<label for="notes"><strong>Notes · exact-face role 判断依据 / 不确定点</strong></label><textarea id="notes" name="notes" placeholder="可记录某张 face 的 digit wrapping、web flank 或 broader sheet 组织依据；允许说明无法判断。"></textarea>
<div class="toolbar"><button class="primary" type="button" id="export-response">EXPORT RESPONSE JSON</button><button type="button" id="clear-response">清空本页答复</button></div><div id="form-status" role="status" aria-live="polite"></div>
<label for="response-preview">导出预览（只读）</label><textarea id="response-preview" readonly placeholder="完成选择并点击 EXPORT RESPONSE JSON 后显示。"></textarea></form>
</section><footer>Review ID: PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW_R1 · Human response count at generation = 0 · READ-ONLY PRODUCTION · NEXT = HUMAN_PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_ADJUDICATION</footer>
</main><script id="view-data" type="application/json">@@DATA@@</script><script>@@LOGIC@@</script><script>
'use strict';
const data=JSON.parse(document.getElementById('view-data').textContent);
const validationMode=new URLSearchParams(location.search).get('validation')==='1';
const validationDownload=validationMode&&new URLSearchParams(location.search).get('validation_download')==='1';
if(validationMode)document.getElementById('validation-notice').classList.add('visible');
if(validationDownload)document.getElementById('validation-notice').textContent='AUTOMATED UI VALIDATION — 仅下载明确标记的 QA 测试文件；不是 Human response，禁止作为 authority。';
const scene={view:'DORSAL',boundary:'ALL',scope:'LOCAL',yaw:0,pitch:0,zoom:1};
const rowColors={P02:'#c9e6df',P03:'#d9e8f4',P04:'#eee4cb',P05:'#e7dcef',P06:'#d7dce5'};
const boundaryColors={A:'#2470b5',B:'#b76a16',C:'#8c4ab4'};
const add=(a,b)=>a.map((v,i)=>v+b[i]), sub=(a,b)=>a.map((v,i)=>v-b[i]), mul=(a,s)=>a.map(v=>v*s), dot=(a,b)=>a.reduce((v,x,i)=>v+x*b[i],0), cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]], unit=a=>mul(a,1/Math.hypot(...a));
const mean=arr=>mul(arr.reduce((a,b)=>add(a,b),[0,0,0]),1/arr.length);
function rotate(v,axis,angle){const c=Math.cos(angle),s=Math.sin(angle);return add(add(mul(v,c),mul(cross(axis,v),s)),mul(axis,dot(axis,v)*(1-c)));}
const focusFaces=Object.values(data.row_faces).flat(), focusIds=[...new Set(focusFaces.flatMap(f=>data.faces[f]))];
const cached={};
for(const state of ['NATIVE','RSSF']){
  const verts=data.vertices[state], norm=data.faces.map(vs=>unit(vs.reduce((a,v,i)=>add(a,cross(verts[v],verts[vs[(i+1)%vs.length]])),[0,0,0])));
  cached[state]={verts,norm,centre:mean(focusIds.map(v=>verts[v]))};
}
function draw(state){
  const canvas=document.getElementById(state==='NATIVE'?'native-canvas':'rssf-canvas'),ctx=canvas.getContext('2d'), w=canvas.clientWidth,h=canvas.clientHeight,dpr=devicePixelRatio||1;
  if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);ctx.fillStyle='#f9fbfd';ctx.fillRect(0,0,w,h);
  const fr=data.frames[state],up=fr.distal_axis;let look={DORSAL:fr.dorsal_axis_from_approved_nail,PALMAR:mul(fr.dorsal_axis_from_approved_nail,-1),RADIAL:fr.radial_axis_away_from_frozen_web,ULNAR:mul(fr.radial_axis_away_from_frozen_web,-1)}[scene.view];look=rotate(look,up,scene.yaw);let right=unit(cross(up,look));look=rotate(look,right,scene.pitch);const cameraUp=unit(cross(look,right));
  const {verts,norm,centre}=cached[state],projectRaw=p=>{const v=sub(p,centre);return [dot(v,right)*1000,dot(v,cameraUp)*1000,dot(v,look)*1000];};
  const proj=verts.map(projectRaw);let fitIds=focusIds;
  if(scene.scope==='CONTEXT')fitIds=[...new Set([...focusIds,...data.cap37_vertex_ids,...data.frozen_first_web_seeds,...data.thumb_nail_faces.flatMap(f=>data.faces[f])])];
  let fitPoints=fitIds.map(v=>proj[v]);if(scene.scope==='CONTEXT'&&state==='RSSF')fitPoints=fitPoints.concat(fr.corrected_chain_world_m.slice(0,2).map(projectRaw));
  const xs=fitPoints.map(p=>p[0]),ys=fitPoints.map(p=>p[1]),lo=[Math.min(...xs),Math.min(...ys)],hi=[Math.max(...xs),Math.max(...ys)],cx=(lo[0]+hi[0])/2,cy=(lo[1]+hi[1])/2;
  const scale=Math.min((w-110)/Math.max(hi[0]-lo[0],1),(h-90)/Math.max(hi[1]-lo[1],1))*.78*scene.zoom;
  const screen=p=>[w/2+(p[0]-cx)*scale,h/2-(p[1]-cy)*scale];
  const faceColors={};for(const [row,fs]of Object.entries(data.row_faces))for(const f of fs)faceColors[f]=rowColors[row];
  if(scene.scope==='CONTEXT'){for(const f of data.frozen_surface_strip_faces)faceColors[f]='#b8ddd1';for(const f of data.cap37_faces)faceColors[f]='#b9a4d5';for(const f of data.thumb_nail_faces)faceColors[f]='#67b7c6';}
  const faces=scene.scope==='LOCAL'?data.local_context_faces:data.faces.map((_,i)=>i);
  const sorted=faces.slice().sort((a,b)=>dot(mean(data.faces[a].map(v=>sub(verts[v],centre))),look)-dot(mean(data.faces[b].map(v=>sub(verts[v],centre))),look));
  const polygon=(fi,fill,alpha)=>{const pts=data.faces[fi].map(v=>screen(proj[v]));if(pts.every(p=>p[0]<-15)||pts.every(p=>p[0]>w+15)||pts.every(p=>p[1]<-15)||pts.every(p=>p[1]>h+15))return;ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.globalAlpha=alpha;ctx.fillStyle=fill;ctx.fill();ctx.strokeStyle='#a2aebb';ctx.lineWidth=.55;ctx.stroke();ctx.globalAlpha=1;};
  ctx.save();ctx.beginPath();ctx.rect(0,0,w,h);ctx.clip();for(const fi of sorted)polygon(fi,faceColors[fi]||'#e5eaf0',scene.scope==='LOCAL'?.55:.82);for(const fi of faces.filter(f=>focusFaces.includes(f)))polygon(fi,faceColors[fi],.86);
  const choices=data.boundaries.filter(q=>scene.boundary==='ALL'||q.option===scene.boundary);
  for(const q of choices)for(const e of q.boundary_edges){const a=screen(proj[data.edges[e.edge_id][0]]),b=screen(proj[data.edges[e.edge_id][1]]);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.strokeStyle=boundaryColors[q.option];ctx.lineWidth=3;ctx.stroke();}
  const labels=document.getElementById('show-labels').checked;
  const markerLabels=[];
  function marker(p,label,color){const xy=screen(projectRaw(p));if(xy[0]<0||xy[0]>w||xy[1]<0||xy[1]>h)return;ctx.beginPath();ctx.arc(...xy,4,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();ctx.strokeStyle='white';ctx.lineWidth=1.4;ctx.stroke();if(labels&&label)markerLabels.push({xy,label,color});}
  if(scene.scope==='CONTEXT'){
    for(const v of data.frozen_first_web_vertices)marker(verts[v],'','#94bdb4');
    for(const v of data.frozen_first_web_seeds)marker(verts[v],'v'+v+' frozen seed','#086f65');
    marker(mean([...new Set(data.thumb_nail_faces.flatMap(f=>data.faces[f]))].map(v=>verts[v])),'thumb nail frozen','#3c93a7');
    marker(mean(data.cap37_vertex_ids.map(v=>verts[v])),'cap37 frozen','#8a62b5');
    if(state==='RSSF'){
      const chain=fr.corrected_chain_world_m;ctx.setLineDash([5,4]);ctx.strokeStyle='#46596b';ctx.lineWidth=1.2;ctx.beginPath();chain.forEach((p,i)=>i?ctx.lineTo(...screen(projectRaw(p))):ctx.moveTo(...screen(projectRaw(p))));ctx.stroke();ctx.setLineDash([]);marker(chain[0],'CMC approved','#364858');marker(chain[1],'MCP approved','#364858');
    }
  }
  if(document.getElementById('show-flow').checked){
    for(const row of data.flow[state])for(const lane of row.lane_flows){const ctr=mean(data.faces[lane.face_id].map(v=>verts[v])),start=screen(projectRaw(ctr)),end=screen(projectRaw(add(ctr,mul(lane.longitudinal_surface_tangent,.003))));ctx.beginPath();ctx.moveTo(...start);ctx.lineTo(...end);ctx.strokeStyle='#3e6379';ctx.lineWidth=1.7;ctx.stroke();const ang=Math.atan2(end[1]-start[1],end[0]-start[0]);ctx.beginPath();ctx.moveTo(...end);ctx.lineTo(end[0]-6*Math.cos(ang-.5),end[1]-6*Math.sin(ang-.5));ctx.lineTo(end[0]-6*Math.cos(ang+.5),end[1]-6*Math.sin(ang+.5));ctx.closePath();ctx.fillStyle='#3e6379';ctx.fill();}
  }
  ctx.restore();
  if(labels){
    markerLabels.forEach((m,i)=>{const tx=14,ty=24+i*22;ctx.beginPath();ctx.moveTo(...m.xy);ctx.lineTo(tx+145,ty-3);ctx.strokeStyle=m.color;ctx.lineWidth=.6;ctx.stroke();ctx.fillStyle='rgba(249,251,253,.95)';ctx.fillRect(tx-3,ty-12,155,18);ctx.fillStyle=m.color;ctx.font='11px system-ui';ctx.fillText(m.label,tx,ty);});
    ctx.font='11px system-ui';Object.entries(data.row_faces).forEach(([row,fs],i)=>{const ctr=mean([...new Set(fs.flatMap(f=>data.faces[f]))].map(v=>verts[v])),xy=screen(projectRaw(ctr)),tx=w-150,ty=25+i*22;ctx.beginPath();ctx.moveTo(...xy);ctx.lineTo(tx-6,ty-3);ctx.strokeStyle='#647b8e';ctx.lineWidth=.6;ctx.stroke();ctx.fillStyle='rgba(249,251,253,.94)';ctx.fillRect(tx-3,ty-12,148,18);ctx.fillStyle='#203447';ctx.fillText(row+' '+fs.join('/'),tx,ty);});
    choices.forEach((q,i)=>{ctx.fillStyle=boundaryColors[q.option];ctx.fillText(q.option+' '+q.boundary_edges.map(e=>'e'+e.edge_id).join(' / '),14,h-16-i*19);});
  }
}
function redraw(){draw('NATIVE');draw('RSSF');}
function resetCamera(){scene.yaw=0;scene.pitch=0;scene.zoom=1;redraw();}
document.querySelectorAll('[data-view]').forEach(btn=>btn.addEventListener('click',()=>{scene.view=btn.dataset.view;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));resetCamera();}));
for(const [id,key] of [['display-boundary','boundary'],['zoom-scope','scope']])document.getElementById(id).addEventListener('change',e=>{scene[key]=e.target.value;resetCamera();});
for(const id of ['show-labels','show-flow'])document.getElementById(id).addEventListener('change',redraw);
document.getElementById('reset-camera').addEventListener('click',resetCamera);
for(const canvas of document.querySelectorAll('canvas')){let last=null;canvas.addEventListener('pointerdown',e=>{last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});canvas.addEventListener('pointermove',e=>{if(!last)return;scene.yaw+=(e.clientX-last[0])*.008;scene.pitch=Math.max(-1.3,Math.min(1.3,scene.pitch+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];redraw();});canvas.addEventListener('pointerup',()=>{last=null;});canvas.addEventListener('pointercancel',()=>{last=null;});canvas.addEventListener('wheel',e=>{e.preventDefault();scene.zoom=Math.max(.3,Math.min(6,scene.zoom*Math.exp(-e.deltaY*.001)));redraw();},{passive:false});}
window.addEventListener('resize',redraw);redraw();
const form=document.getElementById('review-form');
function readAnswers(){const selected=form.querySelector('input[name="selected_option"]:checked');return {selected_option:selected?selected.value:'',Q1_P02_digit_web_acceptable:form.elements.Q1_P02_digit_web_acceptable.value,Q2_P06_broader_interface_acceptable:form.elements.Q2_P06_broader_interface_acceptable.value,Q4_native_RSSF_context_acceptable:form.elements.Q4_native_RSSF_context_acceptable.value,Q5_approve_for_boundary_authority:form.elements.Q5_approve_for_boundary_authority.value,notes:form.elements.notes.value};}
form.addEventListener('change',()=>{const a=readAnswers(),q=BoundaryReview.boundaries[a.selected_option];document.getElementById('boundary-readout').textContent=q?'Q3 · '+q.stop+' · '+q.rows.join(' / ')+' · e'+q.edges.join(' / e'):a.selected_option==='D'?'Q3 · KEEP_UNRESOLVED · 无 boundary authority':'Q3 · 尚未选择 boundary';document.getElementById('response-preview').value='';document.getElementById('form-status').textContent='';});
form.addEventListener('submit',e=>e.preventDefault());
document.getElementById('clear-response').addEventListener('click',()=>{form.reset();document.getElementById('boundary-readout').textContent='Q3 · 尚未选择 boundary';document.getElementById('response-preview').value='';document.getElementById('form-status').textContent='本页答复已清空；没有保存 Human decision。';});
document.getElementById('export-response').addEventListener('click',()=>{
  const a=readAnswers(),errors=BoundaryReview.validateAnswers(a),status=document.getElementById('form-status');if(errors.length){status.textContent=errors.join('\n');return;}
  const result=BoundaryReview.buildResponse(a,new Date().toISOString(),validationMode);result.reviewer_timezone_offset_minutes=new Date().getTimezoneOffset();const text=JSON.stringify(result,null,2);document.getElementById('response-preview').value=text;
  if(validationMode&&!validationDownload){status.textContent='VALIDATION ONLY：JSON 预览已生成；没有下载，也不是 Human response。';return;}
  const blob=new Blob([text+'\n'],{type:'application/json;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=(validationMode?'AUTOMATED_UI_VALIDATION_NOT_HUMAN':BoundaryReview.REVIEW_ID+'_RESPONSE')+'_'+new Date().toISOString().replace(/[:.]/g,'-')+'.json';document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent=(validationMode?'QA 测试文件已下载；不是 Human response。':'')+'JSON 下载已发起。也可复制下方预览保存。答复尚未应用到 authority 或 production。';
});
</script></body></html>'''
replacements={'@@OVERVIEW@@':images['THREE_CANDIDATE_BOUNDARIES_OVERVIEW'],'@@COMPARISONS@@':''.join(comparisons),'@@P02@@':images['P02_EARLY_SIDE_CONTROL'],'@@P06@@':images['P06_LATE_SIDE_CONTROL'],'@@NATIVE@@':images['NATIVE_FOUR_REFERENCE_VIEWS'],'@@RSSF@@':images['RSSF_FOUR_REFERENCE_VIEWS'],'@@CONTEXT@@':images['FROZEN_LANDMARK_CONTEXT'],'@@DORSALPHOTO@@':dorsal,'@@PALMARPHOTO@@':palmar,'@@CARDS@@':''.join(cards),'@@Q1@@':question('Q1_P02_digit_web_acceptable','Q1 · P02 主导组织仍是 digit-web / partial-circumference side，是否可接受？'),'@@Q2@@':question('Q2_P06_broader_interface_acceptable','Q2 · P06 已属于 broader-interface context，是否可接受？'),'@@Q4@@':question('Q4_native_RSSF_context_acceptable','Q4 · 所选边界两侧角色变化，在 native/RSSF 中均可接受？'),'@@DATA@@':json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/'),'@@LOGIC@@':logic}
for key,value in replacements.items():document=document.replace(key,value)
assert '@@' not in document
(OUT/'PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW.html').write_text(document,encoding='utf8')
status=read(OUT/(NAME+'_STATUS.json'));status.update(Human_Review_HTML_generated=True,Human_Review_has_selectable_controls=True,response_JSON_export_implemented=True)
(OUT/(NAME+'_STATUS.json')).write_text(json.dumps(status,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('Self-contained editable Human Review HTML created:',len(document),'characters; no preselection or answer persistence.')
