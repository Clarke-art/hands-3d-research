"""Publish only this audit's report/status and review page; no production edits."""
from pathlib import Path
import json,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
D=read('FULL_VECTOR_FIELD_DEFINITION_R1.json');G=read('FULL_VECTOR_GRADIENT_R1.json');M=read('PROBE_MEASUREMENTS_R1.json');P=read('FINAL_ASSET_PROTECTION_R1.json')
assert P['status']=='PASS'
PHASE=D['PHASE'];RESULT='STATIC_WEIGHT_FIELD_PROBLEM_SUPPORTED'
visual={
 '110':'两视角保持自然平滑。原斜向凹线趋于平顺，未见新增明显 bulge/flap/shelf 或掌面塌陷。',
 '127':'两视角原 first-web 阶梯状折口明显消失，连续过渡更自然；改善方向与 F130 一致。',
 '130':'两视角原深阶梯缺口与尖锐折带明显消失，first-web 成为连续平滑过渡；达到自然很多的门槛。',
 '160':'原斜向深凹折带明显消失；两视角均呈平滑过渡。',
 '176':'恢复帧两视角保持平滑，无新增明显 flap/硬台阶或体积塌陷。',
 '205':'原对角折口与锯齿深折明显消失；两视角一致改善，拇指根部仍自然连接。'}
questions=[
 ['Q1','完整 active-bone static weight-vector field 已重构？','YES','8 个 active 分量在全部 164 个内部点均改变；70 边界点完整向量固定。'],
 ['Q2','ACTIVE_WEIGHT_BONES_IN_ROI？',', '.join(D['ACTIVE_WEIGHT_BONES_IN_ROI']),'21 骨中 16 个 use_deform=true；ROI 仅 8 个实际非零，包含很小但真实的 MIDDLE/RING contribution。'],
 ['Q3','完整向量梯度实质降低？','YES','ROI mean −17.04% / max −24.32%；主带 mean −73.77% / max −73.25%。'],
 ['Q4','F130 主 blocker 明显改善？','YES',visual['130']],
 ['Q5','F127/F160/F205 一致明显改善？','YES','三帧原折口/凹折均明显消失，方向一致。'],
 ['Q6','F110/F176 保持自然平滑？','YES','两保护帧继续平滑；没有用破坏它们来换取 folded frames 的改善。'],
 ['Q7','新增明显 bulge/flap/shelf/collapse？','NO','六帧×两视角未见新增上述明显缺陷或明显 palm distortion。'],
 ['Q8','结果可归因于完整 static weight field？','YES','唯一变量为 ROI 内部完整权重向量；mesh/rest/21 bones/Action/constraints/corrective/driver/LBS 均通过一致性复核。'],
 ['Q9','最终结论？',RESULT,'现有 deformation basis 在固定 sample 与六决策帧上具备解决主 blocker 的能力；等待 Human review，不 promotion。']]
status={'PHASE':PHASE,**{q[0]:q[2] for q in questions},'FINAL_CAUSAL_RESULT':RESULT,'FULL_VECTOR_FIELD_MODIFIED':'YES','FULL_VECTOR_GRADIENT_MEANINGFULLY_REDUCED':'YES','FULL_VECTOR_GRADIENT_REDUCTION':{'ROI_mean_percent':G['ROI_overall']['mean_reduction_percent'],'ROI_max_percent':G['ROI_overall']['max_reduction_percent'],'band_mean_percent':G['human_visible_high_strain_band']['mean_reduction_percent'],'band_max_percent':G['human_visible_high_strain_band']['max_reduction_percent']},'F130_HUMAN_VISIBLE_RESULT':'CLEAR_IMPROVEMENT_MAIN_BLOCKER_REMOVED_IN_MATCHED_VIEWS','STATIC_WEIGHT_ROUTE':'OPEN','FROZEN_FALLBACK_UNCHANGED':'YES','candidate':M['candidate'],'candidate_count':1,'candidate_status':'DESIGN_ONLY','FIRST_WEB_HUMAN_VISIBLE_BLOCKER':'OPEN_PENDING_HUMAN_REVIEW','RIGHT_HAND_DEFORMATION_CLOSED':'NO','LEFT_HAND_START':'NO','WEB_PRODUCT_PROMOTION':'NO','human_final_decision':'PENDING','NEXT_STAGE':'HUMAN_DECISION_ON_PRODUCTION_QUALITY_STATIC_WEIGHT_SOLUTION','WORKFLOW_STATUS':'STOP_HUMAN_REVIEW','assessment_basis':'Agent visual inspection of matched six-frame ordinary solid renders; Human acceptance not assumed.'}
dump(PHASE+'_STATUS.json',status)
dump('VISIBLE_RESULT_R1.json',{'FINAL_CAUSAL_RESULT':RESULT,'decision_basis':'Matched FIRST_WEB_OBLIQUE and PALMAR_THENAR_CLOSE, baseline left/candidate right; ordinary solid views are primary. Numbers are secondary.','per_frame':visual,'Q4':'YES','Q5':'YES','Q6':'YES','Q7':'NO','observer':'Agent image review','human_final_decision':'PENDING','not_a_production_approval':True})
qtable='\n'.join('|'+ ' | '.join(q)+'|' for q in questions)
bone_rows='\n'.join(f"| {n} | {v['ROI_nonzero_vertices']} | {v['ROI_mean_weight']:.8f} | {v['ROI_max_weight']:.8f} |" for n,v in D['active_bone_statistics'].items())
grad_rows='\n'.join(f"| {title} | {v['before']['mean']:.8f} | {v['after']['mean']:.8f} | {v['before']['median']:.8f} | {v['after']['median']:.8f} | {v['before']['max']:.8f} | {v['after']['max']:.8f} | {v['mean_reduction_percent']:.2f}% |" for title,v in [('ROI overall',G['ROI_overall']),('Human-visible 8-edge band',G['human_visible_high_strain_band'])])
bone_grad='\n'.join(f"| {n} | {v['ROI']['before']['mean']:.8f} → {v['ROI']['after']['mean']:.8f} | {v['ROI']['before']['max']:.8f} → {v['ROI']['after']['max']:.8f} | {v['high_strain_band']['before']['mean']:.8f} → {v['high_strain_band']['after']['mean']:.8f} | {v['high_strain_band']['before']['max']:.8f} → {v['high_strain_band']['after']['max']:.8f} |" for n,v in G['per_active_bone'].items())
frame_rows='\n'.join(f"| F{f} | {visual[str(f)]} |" for f in [110,127,130,160,176,205])
report=f'''# {PHASE}

**FINAL_CAUSAL_RESULT = {RESULT}**  
**STATIC_WEIGHT_ROUTE = OPEN**  
**FROZEN_FALLBACK_UNCHANGED = YES**  
**STOP — HUMAN REVIEW**

唯一 DESIGN_ONLY full-vector harmonic candidate 在两指定视角中明显去除了 F130 的主阶梯深缺口；F127/F160/F205 一致改善，F110/F176 保持自然平滑。六帧未见新增明显 bulge / flap / hard shelf / volume collapse / palm distortion。因此本轮证据支持完整 static weight field 仍可解决该 blocker，不能将其归因于已证明不足的 deformation DOF。

可见判断来自 agent 对同相机截图的逐帧评估，**Human final decision = PENDING**。正式 blocker 尚未获得 Human closure，RIGHT_HAND_DEFORMATION_CLOSED=NO。候选不是生产权重解，未 promotion；本轮之后不自动继续权重设计。

## Q1–Q9

| # | 问题 | 回答 | 证据 / 边界 |
|---|---|---|---|
{qtable}

## 继承的权威与实验控制

读取最近两轮 report / JSON / audit 及两个 DESIGN_ONLY candidate（只读对象与 Action 元数据，未复做其试验）。继承 LEVEL_1_TOPOLOGY_ROUTE=CLOSED 和上一轮 Human 接受的 INSUFFICIENT_EVIDENCE，不重开 retopo/subdivide/edge-flow。旧 pair probe 仅覆盖完整梯度约 9–35%，其失败不代表全向量失败。

本轮直接从 frozen fallback 构建 ONE candidate：`{M['candidate']['path']}`，SHA256 `{M['candidate']['sha256']}`。沿用 PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1，11.5–18.5 sec，7 sec，421 observations，同六帧。固定帧相机逐字继承 topology causal probe 的 camera JSON；baseline 图直接复用上一轮已批准图，SHA 一致，未重新渲染历史 baseline。

## Q2：完整 21 骨向量组成

rig 总数 21；16 个骨骼 use_deform=true；5 个 TIP 为 non-deform，其向量分量严格零。读取所有现有 group，不预设 bone 名称。ROI 内实际非零 influence 共 8 个：

`ACTIVE_WEIGHT_BONES_IN_ROI = {D['ACTIVE_WEIGHT_BONES_IN_ROI']}`

| Bone | ROI 非零顶点数 | ROI mean weight | ROI max weight |
|---|---:|---:|---:|
{bone_rows}

MIDDLE_MCP_R 与 RING_MCP_R 贡献很小但实际存在，因此保留参与，未做 support thresholding；ROI 完全无贡献的其余骨骼未加入。完整 baseline/candidate 21 分量逐点存于 FULL_VECTOR_FIELD_DEFINITION_R1.json。

上一轮 WRIST/THUMB pair 在继承 F130 主带 8 边上占完整 endpoint-vector L1 差的 **{100*D['previous_pair_fraction_range'][0]:.2f}%–{100*D['previous_pair_fraction_range'][1]:.2f}%**。其余主要 INDEX 项本轮参与同一求解，未再固定。pair 逐边占比仍附在梯度 JSON，未重复 sensitivity sweep。

## 唯一 candidate 的数学定义

沿用既有 ROI：234 节点 / 431 原网格边 / 70 原外边界 / 164 内部点，未扩大到整手。对全部 8 active 分量共同求解：

`L_II W_I = -L_IB W_B`；`c_uv = 1 / 原 Basis 世界系 rest-edge-length`。

正 conductance 的同一 mesh-edge graph Laplacian 对每个 bone 完全一致。boundary 每分量固定 baseline 值；没有 strength、iteration 参数、目标帧拟合、优化器、painting、support pruning 或第二 candidate。固定边界使每列唯一；非负边界配合离散 maximum principle 保持非负；所有列共用算子使常数 partition-of-unity 被保持。只对内部约 10⁻⁸ 的浮点 sum 误差做 numerical normalization。

- solve 最大 absolute residual = {D['numerics']['solve_max_absolute_residual']:.3g}；normalization 最大单分量改变量 = {D['numerics']['normalization_max_weight_delta']:.3g}。
- 最小 weight = 0；全网格 weight sum 范围 = [{D['constraints']['sum_range_all_vertices'][0]:.10f}, {D['constraints']['sum_range_all_vertices'][1]:.10f}]。
- ROI 外与 boundary 全部数值逐分量完全一致；inactive 分量也完全一致，保存后重新打开复核通过。
- 8 个 active 分量每个均在 164/164 free 点改变，不是名义 full-vector、实际 pair。
- mesh coordinates / edges / faces / Basis / UV / native shading flags / 21 bones / rest matrices / constraints / drivers / original corrective / modifiers / Action 均一致；保持 LBS。
- 新 bone / helper / cage / corrective / DQS 均为零。既有 corrective 六帧自然值都为 0.0，未强制切换。

## Q3：干预验证（在渲染前完成；SECONDARY EVIDENCE）

完整 gradient = `Σ_b |w_b(v) − w_b(u)| / 原 rest-edge-length_mm`，单位 L1/mm。

| 区域 | mean before | mean after | median before | median after | max before | max after | mean 降幅 |
|---|---:|---:|---:|---:|---:|---:|---:|
{grad_rows}

主带 max 下降 73.25%；ROI max 下降 24.32%。weighted Dirichlet energy `{G['weighted_Dirichlet_energy_before_after'][0]:.6f} → {G['weighted_Dirichlet_energy_before_after'][1]:.6f}`，下降 30.48%。全部原边与预选主带沿用，未按结果重新挑选。

| Bone | ROI mean before → after | ROI max before → after | Band mean before → after | Band max before → after |
|---|---:|---:|---:|---:|
{bone_grad}

不声称每个指标或每个 bone 均下降：ROI median 略升，THUMB_CMC mean 上升 3.96%，微小 MIDDLE/RING 项因谐波传播会增加支持，但没有人为添加全无贡献骨骼。固定 boundary 仍保留原陡变；高应变主带的主要 INDEX 梯度已明显减少。这与上一轮只改 pair 的因果隔离缺口不同。

过程透明说明：构建脚本曾加入 Human 未要求的“ROI 与 band mean 都 ≥20%”软件 gate，输出 NO。**首次渲染前**检查真实数据后撤销这个额外 gate：ROI 17.04% / max 24.32%、主带 73.77%、所有 8 列实改与 energy 下降已经构成有效干预，并非 gradient 基本不变。原 log 和修正理由保留在 PRE_RENDER_MANIPULATION_ASSESSMENT_R1.json；没有改候选、边界、算子、weights 或参数。这一判断完全先于可见结果。

![完整向量梯度](EVIDENCE_FULL_VECTOR_GRADIENT_R1.png)

## Q4–Q7：Human-visible 主结果

同 camera / pose / frame / neutral Workbench lighting / material / smooth display shading。baseline LEFT，candidate RIGHT；未经 pixel difference、strain 或 distance 分数代替视觉判据。

| 帧 | 匹配两视角的可见结果 |
|---|---|
{frame_rows}

![F130 对照](EVIDENCE_F130_FULL_WEIGHT_FIELD_PROBE.png)

![六帧对照](EVIDENCE_SIX_FRAMES_FULL_WEIGHT_FIELD_PROBE.png)

候选可以看到 first-web 原来被拉开的阶梯深折被连续曲面替代，既不只是锯齿减少，也不只是浅一点。静态 rest shape 完全不变；运动中表面变化源于完整 weights。无新明显 palm distortion。此处只评估六帧×两视角可见表面，不宣称完整 motion 的所有角度已获得生产质量认可。

## 次级位移与最低保护

F130 对应 ROI 点最大位移 24.515 mm，候选局部 max edge-length ratio=1.765；仅作干预确实影响曲面的佐证，不作为 PASS 条件。六帧完整数值位于 PROBE_MEASUREMENTS_R1.json。421 observations 检查包含最后端点 F211：`i=0..420 → source 690+i → frame 1+i//2, subframe=(i%2)/2`。没有改 sample 或 retarget。

NaN/Inf=0、gross collapsed faces=0、degenerate edges=0，ZERO restore=0.000000 mm。candidate 与 baseline 的 ZERO 求值浮点差最大 {D['constraints']['ZERO_difference_max_mm']:.9f} mm；原生坐标逐项一致。连接拓扑不变，六决策帧未见明显新增 tearing/penetration。未运行 hidden crossing census、normal-dot、R3、true-cap、2127-edge 或逐顶点 anatomy forensic；不将普通视图判断冒充 exhaustive collision proof。

## 资产保护与停止

Frozen fallback SHA256 轮前轮后均为 `{P['fallback_actual_sha256']}`，**FROZEN_FALLBACK_UNCHANGED=YES**。所有前两轮 durable audit / report / JSON / candidate / raster 和 protected source/sample/pointer 哈希结束一致。仅本轮 audit 内一份 .blend；未移动 production pointer、未 promotion、未正式 weight rebuild、未开始左手或 Web export。

**STATIC_WEIGHT_ROUTE = OPEN**。本轮证明 existing static field 具有解决当前六帧主 blocker 的能力；production-quality weight solution 的设计需下一轮 Human 决策。`DEFORMATION_DOF_LIMIT_SUPPORTED` 本轮不成立，不自动进入新 bone / helper / cage / PSD / RBF / muscle / new rig。

交付：本报告、review.html、唯一 DESIGN_ONLY .blend、三张指定 EVIDENCE PNG、FULL_VECTOR_FIELD_DEFINITION_R1.json、FULL_VECTOR_GRADIENT_R1.json、PROBE_MEASUREMENTS_R1.json、FINAL_ASSET_PROTECTION_R1.json，以及小量可复现脚本和判读记录。

**STOP — HUMAN REVIEW。等待 Human 决策。**
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
data={'frames':[110,127,130,160,176,205],'visual':visual,'questions':questions}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Full static weight field · R1</title>
<style>:root{color-scheme:dark;font-family:Segoe UI,Microsoft YaHei,sans-serif;background:#101923;color:#e3ecf5}*{box-sizing:border-box}body{margin:0 auto;padding:30px;max-width:1600px}h1{font-size:clamp(21px,3vw,34px);overflow-wrap:anywhere;margin:10px 0 18px}h2{font-size:23px}p{line-height:1.8;color:#bbcad9}.tag{display:inline-block;border:1px solid #3b5c55;border-radius:20px;padding:7px 14px;color:#74e8ba;font-size:13px}.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.fact{padding:18px;border:1px solid #2b3b4c;border-radius:10px}.fact strong{display:block;font-size:28px;color:#71deb2}.fact span{font-size:14px;color:#b1c1d0}nav{display:flex;gap:10px;flex-wrap:wrap}button,select{padding:10px 16px;font:inherit;background:#1b2c3b;border:1px solid #405266;border-radius:6px;color:#e4edf6;cursor:pointer}button.active{background:#265244;border-color:#6cd4a6}.sticky{position:sticky;top:0;background:#101923f5;padding:14px 0;z-index:2;border-bottom:1px solid #304457}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:16px 0 28px}figure{margin:0;background:#172532;border:1px solid #304457;border-radius:8px;overflow:hidden}figcaption{padding:12px;color:#cad8e5;font-size:14px}img{display:block;width:100%;height:auto}a{color:#83dcb9}table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #314457;overflow-wrap:anywhere}td:nth-child(3){color:#79deb6;max-width:320px}tr:nth-child(2) td:nth-child(3){font-size:12px}th{color:#aebfd0}.tablewrap{overflow:auto}.links{display:flex;gap:20px;flex-wrap:wrap;margin:24px 0}.foot{border-top:1px solid #304457;padding-top:16px;margin-top:35px}@media(max-width:720px){body{padding:16px}.facts{grid-template-columns:1fr 1fr}.pair{gap:6px}figcaption{padding:8px;font-size:11px}.tablewrap{font-size:12px}}</style>
<span class="tag">DESIGN_ONLY · 1 candidate · STOP — HUMAN REVIEW</span><h1>RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1</h1>
<p><b style="color:#75e3b5">FINAL_CAUSAL_RESULT = STATIC_WEIGHT_FIELD_PROBLEM_SUPPORTED</b><br>F130 主阶梯深缺口明显消失，其余三个 folded frames 一致改善；F110/F176 保持平滑。可见判断待 Human review，候选尚未 promotion。</p>
<div class="facts"><div class="fact"><strong>73.77% ↓</strong><span>主高应变带 full-vector mean</span></div><div class="fact"><strong>17.04% ↓</strong><span>ROI overall full-vector mean</span></div><div class="fact"><strong>8 / 8</strong><span>全部 active bone 分量参与</span></div><div class="fact"><strong>OPEN</strong><span>STATIC_WEIGHT_ROUTE</span></div></div>
<div class="sticky"><nav id="frames" aria-label="选择决策帧"></nav><p id="result" aria-live="polite"></p></div>
<p>同 camera / pose / frame / lighting / shading，baseline LEFT，candidate RIGHT。点击图像可查看原图。</p>
<section id="matched"></section>
<h2>Q1–Q9</h2><div class="tablewrap"><table><thead><tr><th>#</th><th>问题</th><th>回答</th><th>证据与边界</th></tr></thead><tbody id="questions"></tbody></table></div>
<h2>完整 weight-vector 干预验证</h2><p>21 骨中 16 个为 deform，ROI 中 8 个实际非零：WRIST_R、THUMB_CMC_R、THUMB_MCP_R、INDEX_MCP_R、INDEX_PIP_R、INDEX_DIP_R、MIDDLE_MCP_R、RING_MCP_R。164 内部点重构，70 外边界完整向量固定。各项均值不要求统一下降；完整主带是主要干预验证域，数值仅作 secondary evidence。</p>
<a href="EVIDENCE_FULL_VECTOR_GRADIENT_R1.png" target="_blank"><img src="EVIDENCE_FULL_VECTOR_GRADIENT_R1.png" alt="全向量与逐骨梯度 before/after"></a>
<div class="links"><a href="EVIDENCE_F130_FULL_WEIGHT_FIELD_PROBE.png">F130 两视角证据</a><a href="EVIDENCE_SIX_FRAMES_FULL_WEIGHT_FIELD_PROBE.png">六帧总览</a><a href="RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_FIELD_CAUSAL_PROBE_R1_REPORT.md">完整报告</a><a href="RIGHT_HAND_FIRST_WEB_FULL_STATIC_WEIGHT_PROBE_R1.blend">DESIGN_ONLY candidate</a></div>
<div class="links"><a href="FULL_VECTOR_FIELD_DEFINITION_R1.json">Field definition</a><a href="FULL_VECTOR_GRADIENT_R1.json">Full-vector gradients</a><a href="PROBE_MEASUREMENTS_R1.json">Measurements</a><a href="FINAL_ASSET_PROTECTION_R1.json">Asset protection</a></div>
<p class="foot">FROZEN_FALLBACK_UNCHANGED = YES · PROTECTED_FROZEN_FALLBACK<br>未移动 production pointer、未 promotion、未开始左手或 Web export。421 observations 最低故障保护通过。下一轮等待 Human 决定 production-quality static weight solution。Human final decision = PENDING。</p>
<script>const DATA=__DATA__;const views=['FIRST_WEB_OBLIQUE','PALMAR_THENAR_CLOSE'];let current=130;const frames=document.querySelector('#frames');for(const f of DATA.frames){const b=document.createElement('button');b.textContent='F'+f+(f===130?' · PEAK':f===110||f===176?' · SMOOTH':' · FOLDED');b.dataset.frame=f;b.addEventListener('click',()=>show(f));frames.append(b)}function show(f){current=f;for(const b of frames.children){const active=Number(b.dataset.frame)===f;b.classList.toggle('active',active);b.setAttribute('aria-pressed',active)}document.querySelector('#result').textContent='F'+f+'：'+DATA.visual[f];const target=document.querySelector('#matched');target.replaceChildren();for(const v of views){const h=document.createElement('h2');h.textContent=v;target.append(h);const pair=document.createElement('div');pair.className='pair';for(const label of ['BASELINE','FULL_VECTOR_PROBE']){const fig=document.createElement('figure');const cap=document.createElement('figcaption');cap.textContent=(label==='BASELINE'?'LEFT · frozen baseline':'RIGHT · full-vector candidate')+' · F'+f;const a=document.createElement('a');a.href='renders/'+label+'__F'+String(f).padStart(3,'0')+'__'+v+'.png';a.target='_blank';const im=document.createElement('img');im.src=a.href;im.alt=cap.textContent+' · '+v;a.append(im);fig.append(cap,a);pair.append(fig)}target.append(pair)}}for(const q of DATA.questions){const tr=document.createElement('tr');for(const cell of q){const td=document.createElement('td');td.textContent=cell;tr.append(td)}document.querySelector('#questions').append(tr)}show(130);</script></html>'''
(OUT/'review.html').write_text(html.replace('__DATA__',json.dumps(data,ensure_ascii=False)),encoding='utf-8')
print('REPORT_STATUS_REVIEW_DELIVERED',RESULT)
