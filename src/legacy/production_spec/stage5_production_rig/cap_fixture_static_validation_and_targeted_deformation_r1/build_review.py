from qualification_common import *
import html
status=read(OUT/(PHASE+'_STATUS.json'));visual=read(OUT/'VISUAL_EVIDENCE_MANIFEST.json');failure=read(OUT/'TARGETED_BLOCKING_FAILURE_CLASSIFICATION.json');debt=read(OUT/'INHERITED_DEBT_DEFORMATION_MAPPING.json');matrix=read(OUT/'TARGETED_FIXTURE_MATRIX.json');machine=read(OUT/'TARGETED_DEFORMATION_MACHINE_EVIDENCE.json')
payload={'status':status,'outputs':visual['outputs'],'failure':failure,'debt':debt,'fixtures':matrix['fixture_results']}
table=''.join(f'<tr><td>{html.escape(k)}</td><td>{html.escape(str(v))}</td></tr>' for k,v in status.items() if k.isupper())
failtable=''.join(f'<tr><td>{r["pose"]}</td><td>{r["face_pair"]}</td><td>{r["evidence"]["depth_mm"]:.4f}</td><td>{r["evidence"]["local_edge_mm"]:.4f}</td><td>{r["evidence"]["seg_mm"]:.4f}</td></tr>' for r in failure['failures'])
debttable=''.join(f'<tr><td>{r["debt_id"]}</td><td>{r["vertex_ids"]}</td><td>{r["max_ratio"]:.4f}x</td><td>{", ".join(r["strain_only_pose_ids"]) or "—"}</td><td>0 / 保留静态债务</td></tr>' for r in debt['rows'])
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CAP Fixture R1 · Failure Review</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101519;color:#e6edf0;font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1440px;margin:auto;padding:32px 28px 90px}h1{font-size:32px;line-height:1.35;margin:12px 0}h2{font-size:22px;margin-top:42px}p{max-width:1040px}a{color:#83cbd9}code{overflow-wrap:anywhere;font-size:13px}.tag{font-size:13px;letter-spacing:2px;color:#88a3ae}.fail{border-left:5px solid #ff806e;background:#332324;padding:16px 20px;border-radius:5px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.stat,.card{background:#1b242b;border:1px solid #34424b;border-radius:8px;padding:14px}.stat strong{font-size:24px;display:block}.subtle{color:#aebec6;font-size:14px}.controls{display:flex;flex-wrap:wrap;gap:12px;margin:22px 0;position:sticky;top:0;background:#101519ed;padding:12px 0;z-index:2}label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:#bdd0d8}select{background:#202e37;color:#fff;border:1px solid #536975;border-radius:5px;padding:10px;font-size:15px;min-width:155px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}.panel{margin:0;min-width:0;background:#1b242b;border:1px solid #34424b;border-radius:8px;overflow:hidden}.panel img{width:100%;height:auto;display:block}.panel figcaption{padding:12px 16px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px 12px;border-bottom:1px solid #33424b;text-align:left;vertical-align:top}th{color:#9fbcc7;background:#1b242b}tr:hover{background:#1d2b33}.scroll{overflow:auto}details{margin:18px 0;background:#1b242b;border:1px solid #34424b;padding:14px;border-radius:8px}summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}#pairFacts{padding:16px;background:#1b242b;border:1px solid #34424b;border-radius:8px;margin-top:14px}.footer{margin-top:40px;color:#adc0c9}.legend{display:flex;flex-wrap:wrap;gap:20px;font-size:14px}.orange{color:#ffaf7b}.blue{color:#83c1ff}.green{color:#85edab}@media(max-width:900px){.grid{grid-template-columns:1fr 1fr}.pair{grid-template-columns:1fr}main{padding:24px 16px}.controls{position:static}h1{font-size:25px}}
</style></head><body><main>
<div class="tag">TARGETED QUALIFICATION · R2 READ-ONLY INPUT</div><h1>Cap fixture / deformation 审阅</h1>
<div class="fail"><strong>FAIL_CLOSED_TARGETED_DEFORMATION</strong><br>cap37 two-ring 邻域确认 3 条 THUMB–INDEX 几何穿插观测；本轮停止，保留原 production candidate。</div>
<p>同一批历史姿态下，edge5879 严重伸长已闭合，16 条 inherited static debt 未检出真实 deformation failure。另有两种姿态出现 cap 邻域穿插：TH_IP_30 一对、IDX_MCP_45 两对。三对在 corrected R1 中已存在，R2 没有增量新增；对应面对在 R1B/R1E 同姿态中没有相交。</p>
<div class="grid"><div class="stat"><strong>PASS</strong>静态 fixture / corrected chain</div><div class="stat"><strong>16 / 16</strong>债务映射、处置完成</div><div class="stat"><strong>3 对 / 2 姿态</strong>recovery 相对 R1B 的局部穿插</div><div class="stat"><strong>0</strong>权重、几何、拓扑、骨/关节漂移</div></div>
<p class="subtle">本页是失败证据入口。它不执行修改、批准、freeze、promotion 或下一阶段。CMC 姿态仅为 TARGETED_DIAGNOSTIC_PROBE；本轮不作 CMC / Stage6B pass 声明。</p>
<h2>五个 fixture · 相同视角对照</h2><p>两侧共享 camera、lighting、scale、pose 和 framing。黄色点为实际 posed core；绿色线为 frozen fresh20 ownership boundary。切换历史候选查看变化；strain 图采用原 R1E 色阶。</p>
<div class="controls"><label>Fixture<select id="fixture"></select></label><label>历史姿态<select id="pose"></select></label><label>历史参照<select id="baseline"><option value="R1B_DONOR">R1B donor</option><option value="R1E">R1E failed candidate</option><option value="R1_CORRECTED_RIG">Corrected R1</option></select></label><label>显示<select id="style"><option value="solid">Solid surface</option><option value="strain">Edge strain</option></select></label></div>
<div class="pair"><figure class="panel"><a id="leftLink"><img id="left" alt="历史候选匹配视角"></a><figcaption id="leftCaption"></figcaption></figure><figure class="panel"><a id="rightLink"><img id="right" alt="R2 匹配视角"></a><figcaption id="rightCaption"></figcaption></figure></div><div id="fixtureFacts"></div>
<h2>阻塞证据 · 精确面对隔离图</h2><p>隔离图补充完整表面图，只显示测得的两张真实 polygon。橙色为 THUMB、蓝色为 INDEX、绿色点为实际 triangle crossing；白色为 posed polygon 边。既有 R1C V2 判据要求真实交叉且 footprint-constrained poke 至少达到同一面对的 bind facet mean edge。</p>
<div class="legend"><span class="orange">● THUMB surface</span><span class="blue">● INDEX surface</span><span class="green">● crossing points</span></div>
<div class="scroll"><table><thead><tr><th>历史姿态</th><th>Face pair</th><th>Poke mm</th><th>Bind facet mean mm</th><th>Crossing segment mm</th></tr></thead><tbody>__FAILTABLE__</tbody></table></div>
<div class="controls"><label>观测<select id="failureSelect"></select></label></div><div class="pair"><figure class="panel"><a id="pairLeftLink"><img id="pairLeft" alt="历史参照面对"></a><figcaption id="pairLeftCaption"></figcaption></figure><figure class="panel"><a id="pairRightLink"><img id="pairRight" alt="R2 交叉面对"></a><figcaption>R2 · actual measured face pair</figcaption></figure></div><div id="pairFacts"></div>
<h2>Inherited static debt · 16 条</h2><p>这些结果只覆盖已选历史姿态及 endpoint incident patch。四组 proximal seam 有 &gt;3x strain diagnostic，既有 Stage6B R1B 规则明确不将 strain/normal flip 单独判为 surface destruction。无 severe &gt;5x、collapse、局部面积毁损或 V2 visible crossing。自然轮廓、pinching、crease、volume 与教学可读性仍需人工审阅，静态债务保持记录。</p>
<div class="scroll"><table><thead><tr><th>Debt edge</th><th>Endpoint IDs</th><th>Max posed/bind</th><th>&gt;3x strain poses</th><th>True failure</th></tr></thead><tbody>__DEBTTABLE__</tbody></table></div>
<details><summary>完整 required status fields / 停止状态</summary><div class="scroll"><table>__TABLE__</table></div></details>
<details><summary>R2 哈希与复用边界</summary><p>Candidate SHA256</p><code>__HASH__</code><p>Weight vector SHA256</p><code>__VECTOR__</code><p>已独立 clean-reopen，比对所有3416 vectors、mesh/rig snapshots 和全工作区历史文件。复用六个 R1D/R1E 姿态并追加一个既有 IDX_MCP_45；没有新角度/Action 或 full-suite harness。旧 cap9 one-hot 和旧全图 R3 cut-component 判法已废止；仅使用 frozen corrected selector、fresh authority 与既有几何判据。</p></details>
<p><a href="__REPORT__">完整报告</a> · <a href="TARGETED_FIXTURE_MATRIX.json">Fixture matrix</a> · <a href="TARGETED_BLOCKING_FAILURE_CLASSIFICATION.json">失败分类与 vertices / weights / bones</a> · <a href="INHERITED_DEBT_DEFORMATION_MAPPING.json">Debt mapping</a> · <a href="TARGETED_DEFORMATION_MACHINE_EVIDENCE.json">Machine evidence</a> · <a href="PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json">只读保护验证</a> · <a href="VISUAL_EVIDENCE_MANIFEST.json">84 图与共享视角参数</a></p>
<noscript><p>浏览器关闭 JavaScript 时，请打开 <a href="renders/CAP37__TH_IP_30__R2__solid.png">cap37</a>、<a href="renders/OLD_CAP9__IDX_MCP_45__R2__solid.png">old9</a>、<a href="renders/FIRST_WEB__FULL_OPP_L3__R2__solid.png">FIRST_WEB</a>、<a href="renders/FRESH_R3_TRANSITION_COLLAR__CMC_MCP_L3__R2__solid.png">collar</a>、<a href="renders/EDGE5879__CMC_MCP_L3__R2__solid.png">edge5879</a>。</p></noscript>
<div class="footer">STOP — HUMAN REVIEW OF BLOCKING FAILURE。后续 bound / full Stage6A / full Stage6B 均未启动。未来修复范围与方法尚未裁定；如涉及 outside317 vertices 或 pinned quintic 权威变更，须另行明确 scope/authority。</div>
</main><script type="application/json" id="evidence">__DATA__</script><script>
const D=JSON.parse(document.getElementById('evidence').textContent), O=D.outputs;
const el=id=>document.getElementById(id), names=Object.keys(D.fixtures);
function options(id,values){el(id).innerHTML=values.map(v=>`<option value="${v}">${v}</option>`).join('');}
function image(id,link,filename){el(id).src=filename;el(link).href=filename;}
function availablePoses(f){return [...new Set(O.filter(r=>r.fixture===f&&r.style==='solid').map(r=>r.pose))];}
function fileFor(f,p,a,s){const r=O.find(r=>r.fixture===f&&r.pose===p&&r.asset===a&&r.style===s);if(!r)throw Error('Missing evidence '+[f,p,a,s]);return r.file;}
function drawFixture(){const f=el('fixture').value,p=el('pose').value,a=el('baseline').value,s=el('style').value;
 image('left','leftLink',fileFor(f,p,a,s));image('right','rightLink',fileFor(f,p,'R2',s));
 el('leftCaption').textContent=a+' · '+p;el('rightCaption').textContent='R2 · '+p;
 const r=D.fixtures[f];el('fixtureFacts').textContent='Fixture: '+r.verdict+' · severe 0 · min area ratio '+r.min_area_ratio.toFixed(4)+' · contour / readability 仍需 Human Review';
}
function drawFailure(){const r=D.failure.failures[Number(el('failureSelect').value)],a=el('baseline').value,stem=`renders/PAIR_${r.face_pair[0]}_${r.face_pair[1]}__${r.pose}__`;
 image('pairLeft','pairLeftLink',stem+a+'.png');image('pairRight','pairRightLink',stem+'R2.png');el('pairLeftCaption').textContent=a+' · '+r.pose;
 el('pairFacts').textContent='分类: '+r.classification+' (基准 R1B → corrected recovery; corrected R1 已存在, R2 增量新增 0)。Vertices: '+r.vertex_ids.join(', ')+'。Outside317: '+r.vertices_outside317.join(', ')+'. 无自动 scope 扩大。';
}
options('fixture',names);options('pose',availablePoses(names[0]));
el('failureSelect').innerHTML=D.failure.failures.map((r,i)=>`<option value="${i}">${r.pose} · faces ${r.face_pair.join(' / ')}</option>`).join('');
el('fixture').addEventListener('change',()=>{options('pose',availablePoses(el('fixture').value));drawFixture();});
el('pose').addEventListener('change',drawFixture);el('style').addEventListener('change',drawFixture);
el('baseline').addEventListener('change',()=>{drawFixture();drawFailure();});el('failureSelect').addEventListener('change',drawFailure);
drawFixture();drawFailure();
</script></body></html>'''
for a,b in {'__FAILTABLE__':failtable,'__DEBTTABLE__':debttable,'__TABLE__':table,'__HASH__':EXPECTED,'__VECTOR__':VECTOR,'__REPORT__':PHASE+'_REPORT.md','__DATA__':json.dumps(payload,ensure_ascii=False).replace('</','<\\/')}.items():page=page.replace(a,b)
(OUT/'review.html').write_text(page,encoding='utf-8')
print('Built offline Human Review: five fixtures, shared-camera comparisons, three crossing pairs, debt16 table')
