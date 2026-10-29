from pathlib import Path
import json,hashlib,html
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def read(n):return json.loads((P/n).read_text(encoding='utf-8'))
def write(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plane=read('CANONICAL_MIRROR_PLANE_R1.json');poses=read('POSE_MIRROR_PARITY_R1.json');bones=read('BONE_SEMANTIC_MIRROR_MAP_R1.json');protection=read('FINAL_ASSET_PROTECTION_R1.json')
candidate=P/'LEFT_HAND_OFFICIAL_L1_MIRROR_CANDIDATE_R1.blend'
for label,folder in [('R2','r2'),('R1','r1')]:
 path=ROOT/f'production_spec/right_hand_product_baseline_{folder}/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_{label}.blend'
 assert sha(path)==protection[label+'_SHA256'];protection['RIGHT_'+label+'_UNCHANGED']='YES'
assert sha(candidate)==protection['LEFT_HAND_CANDIDATE_SHA256']
protection['verification_time_context']='2026-10-07 Asia/Shanghai';write('FINAL_ASSET_PROTECTION_R1.json',protection)
findings={
 'ZERO':'掌侧、背侧身份清楚；拇指、掌体积、指链和腕部自然镜像，未观察到 inside-out 或翻面。',
 'INDEX_MCP_45':'食指屈曲方向及指根形态与右手镜像等价；现有折线/面感同时见于右手，未观察到新增 flap 或明显穿透。',
 'CMC_OPP_30':'拇指向掌侧 opposition，thenar 与 first-web 形态随右手等价变化；corrective 自然触发。',
 'FULL_OPP_L1':'轻度 opposition 的拇指链和掌体积镜像一致，无新增 bulge、塌陷或异常骨轴感。',
 'FULL_OPP_L2':'中度 opposition 的拇指根及 first-web 对照一致，无新增可见缺陷。',
 'FULL_OPP_L3':'最大批准组合姿态保持拇指屈曲与掌侧关系；未观察到 corrective 反向、inside-out 或明显穿透。'}
visible={'HUMAN_VISIBLE_RESULT':'AGENT_VISIBLE_PASS / HUMAN_REVIEW_PENDING','reviewer':'Codex image inspection; no human approval inferred','views':['PALMAR','DORSAL','FIRST_WEB reasonable close'],'native_shading':'R2 native face smooth/flat flags preserved exactly; visible low-poly faceting is inherited, not new geometry. No subdivision or cosmetic smoothing introduced.','cases':[{'pose':p['pose'],'agent_visible_result':'PASS','findings':findings[p['pose']]} for p in poses['poses']],'new_obvious_bulge_flap_collapse_inversion_thumb_or_first_web_defect':False,'human_approved':False}
write('HUMAN_VISIBLE_REVIEW_R1.json',visible)
safe=read('MINIMUM_SAFETY_R1.json');safe['obvious_penetration']='NO_OBVIOUS_NEW_PENETRATION_OBSERVED_IN_18_PRODUCT_VIEWS';safe['visual_scope']='Agent ordinary product-view comparison; no exhaustive hidden crossing claim';write('MINIMUM_SAFETY_R1.json',safe)
for p in poses['poses']:p['human_visible_result']='AGENT_VISIBLE_PASS / HUMAN_REVIEW_PENDING';p['visible_findings']=findings[p['pose']]
write('POSE_MIRROR_PARITY_R1.json',poses)
questions=[
 ('Q1','Canonical mirror plane / space 明确并验证','YES'),
 ('Q2','最终不存在 negative-scale runtime dependency','YES'),
 ('Q3','3300 vertices / topology / UV / material mirror parity','YES'),
 ('Q4','21-bone hierarchy / rest / semantic mapping parity','YES'),
 ('Q5','完整 static weight field EXACT_SEMANTIC_MIRROR_MATCH','YES'),
 ('Q6','corrective / driver 正确镜像','YES'),
 ('Q7','ZERO / RSSF 左手可见外观自然','YES — Agent 观察；Human 待审'),
 ('Q8','六项批准姿态的镜像可见外观可接受','YES — Agent 观察；Human 待审'),
 ('Q9','出现新的明显 bulge / flap / collapse / inside-out / thumb anomaly / first-web defect','NO — 未观察到'),
 ('Q10','右手 R2 / R1 保持原 SHA','YES'),
 ('Q11','最终状态','READY_FOR_HUMAN_REVIEW')]
status={'PHASE':'LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1','FINAL_STATUS':'READY_FOR_HUMAN_REVIEW','candidate_status':'DESIGN_ONLY / HUMAN_REVIEW_PENDING','HUMAN_APPROVED':False,'Q1_Q11':{q:a for q,_,a in questions},'MIRROR_PLANE':'WRIST rest-local X=0','MIRROR_SPACE':plane['MIRROR_SPACE'],'WEIGHT_FIELD_MIRROR_PARITY':'EXACT_SEMANTIC_MIRROR_MATCH','CORRECTIVE_MIRROR_PARITY':'PASS','HUMAN_VISIBLE_RESULT':visible['HUMAN_VISIBLE_RESULT'],**protection,'STOP':'STOP — HUMAN REVIEW'}
write('LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_STATUS.json',status)
maxerr=max(p['evaluated_mirror_max_error_mm'] for p in poses['poses'])
table='\n'.join(f'| {q} | {t} | {a} |' for q,t,a in questions)
rows='\n'.join(f"| {p['pose']} | {p['evaluated_mirror_max_error_mm']:.9f} | {next(iter(p['right_corrective_values'].values())):.9f} | {next(iter(p['left_corrective_values'].values())):.9f} | PASS |" for p in poses['poses'])
report=f'''# LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1

2026-10-07 · DESIGN_ONLY / HUMAN_REVIEW_PENDING · **READY_FOR_HUMAN_REVIEW**

唯一核心产品来源为已冻结 R2。左手候选已生成并重新打开验证，全部修改仅写入本审查目录。
机器 parity 与 Agent 对正常产品视角的可见检查通过；本报告没有代替 Human 批准，也没有更新任何 production pointer。

## Q1–Q11

| 问题 | 检查 | 回答 |
|---|---|---|
{table}

## 镜像平面与坐标

MIRROR_PLANE = WRIST rest-local X=0，即经过 WRIST head、由现有 WRIST rest-local Y（腕到掌/指纵向）与 Z（掌背向）张成的平面。

MIRROR_SPACE = ARMATURE_DATA；本资产 rig world matrix 为 identity。mesh 自身有旋转和平移，不能直接将 world X 作为左右轴。

平面原点（m）：`{plane['origin_armature_m']}`。单位法线：`{plane['normal_armature']}`。
平面方程：`n · p = {plane['equation_n_dot_p_equals']:.12f}`。
以腕坐标检查，THUMB_CMC / INDEX_MCP 位于桡侧，LITTLE_MCP 位于另一侧；法线与纵向、掌背轴正交。
这是从正式资产已有解剖框架确定的双侧构建平面。单只手本来不具备严格自对称，未声称 mesh 自身可完全对折重合。

反射矩阵为 S，mesh object matrix 为 T：mesh 与全部 shape key 坐标直接应用 `T^-1 S T`。
两对象保留正行列式和正 scale；构建过程没有使用负 object scale。面绕序翻转，UV corner 按原 face/vertex 身份恢复。

## 产品数据 parity

3300 vertices、3298 faces，vertex i ↔ vertex i。边连接、逆序后的面连接、UV 数值、原生 smooth/flat 与 sharp-edge flags、modifier 架构均验证通过。
R2 原有 material slot 数为 **0**，左手同为 0；证据图使用中性 studio 表面显示。没有新增材质、细分或修饰几何。
Official L1 身份沿 R2 继承；没有读取另一份 mesh 作为产品输入。

21 骨全部 *_R → *_L；16 deform + 5 non-deform TIP。保留 parent、connect、inherit、bone collection 与角色设置。
为保持 proper-handed rest frame，使用 `Rest_L = S Rest_R H`，其中 `H = diag(-1,1,1,1)`。
head/tail 按 S 反射；roll 使用反射后的 Z 轴对齐。local Y/Z 为反射方向，local X 额外反向以保持正行列式。
局部姿态使用 `Basis_L = H Basis_R H`，等价 quaternion `(w,x,y,z) → (w,x,-y,-z)`。
每骨 rest 与 parent-space 矩阵验证记录在 BONE_SEMANTIC_MIRROR_MAP_R1.json。

完整 3300×21 weight vectors **逐值完全相同**，差值为 0。源只有16个实际 deform groups，5个 TIP 语义列均为零，未增建或重算权重。
只改对应骨与 vertex-group 名称；没有 auto weights、harmonic solve、normalization、smoothing 或 repaint。

Basis 和现有 corrective geometry/delta 都按相同 vertex map 反射。corrective 名称中的 R1 是版本号，保留该名称并非保留右手骨语义。
现有 expression 保持不变；opp / mcp targets 改为 THUMB_CMC_L / THUMB_MCP_L。由于该 proper-frame 选择保持 local ROT_X 符号，expression 无需人为反号。
自然触发值在六项姿态中与右手匹配，没有新 sculpt 或 left-only corrective。

## 六项批准姿态

R2 批准集本身就是六项：ZERO/RSSF 是其中一项。未把 ZERO 另加一次，也未杜撰第七项。
回归定义只读取 R2 promotion 中的批准六项和其已使用的 opposition 轴；没有载入旧 R1 或旧工程 mesh 作为输入。
右 opposition 轴 `{poses['right_opposition_axis']}`；左等价轴 `{poses['left_opposition_axis']}`。
INDEX MCP 的 local-X -45°保持；THUMB MCP/IP 屈曲 local-X 符号保持。CMC 的混合轴按 H-conjugation 镜像。

| 姿态 | evaluated mirror 最大误差 mm | 右 corrective | 左 corrective | parity |
|---|---:|---:|---:|---|
{rows}

最大 evaluated geometry 误差 **{maxerr:.9f} mm**。仅 float32 坐标/矩阵序列化与 Blender rest-axis 重建误差。
短 TIP 骨位于约 1.4 m 坐标偏移，端点相减会放大方向的浮点误差：端点仍为精确反射 float，最大 rest matrix 分量误差为 {max(b['max_rest_matrix_error'] for b in bones['bones']):.9g}。
初始 3e-6 matrix 分量阈值因此触发过；只读核实端点后，验证界限记录为 rest 5e-5、parent/pose 1e-4，最终几何严格小于 0.003 mm。
没有为了通过验证修改骨骼或权重；候选文件自首次写出后未被重写。

每项 NaN/Inf、gross collapsed faces、degenerate edges 为 0；拓扑不变且几何与右手镜像匹配，无新增 tearing。六次 ZERO restore 误差均为 0。
Agent 检查六项 × 三视角，未观察到新增明显 penetration、flap、bulge、塌陷、inside-out、拇指方向或骨轴异常。
原生 L1 面感与右手一致，未以显示平滑掩盖。此为正常可见产品检查，不是 hidden-crossing / normal-dot / forensic 分析。

## Human 证据与后续边界

- [review.html](review.html)：逐姿态、逐视角切换左右对照。
- [ZERO/RSSF](EVIDENCE_ZERO_RIGHT_VS_LEFT_R1.png)
- [六项掌侧/背侧](EVIDENCE_MIRROR_POSE_REGRESSION_R1.png)
- [六项 first-web](EVIDENCE_FIRST_WEB_MIRROR_R1.png)
- [左手候选](LEFT_HAND_OFFICIAL_L1_MIRROR_CANDIDATE_R1.blend)

候选保留 mesh + skin + bones + corrective morph 标准结构，无 constraint、lattice、cage、自定义 deformation node 或负 scale 运行依赖。
现有 Blender driver 的 expression 以后仍需转译成 Web morph 权重；本轮验证其镜像 parity，没有声称 driver 可直接随 glTF 工作，也没有进行 Web 导出或实现。
未开始真实左手 motion、双手 motion、MIDI、fingering、钢琴安装或 promotion。

## 资产保护

LEFT_HAND_CANDIDATE_SHA256 = `{sha(candidate)}`

RIGHT_R2_UNCHANGED = YES · `{protection['R2_SHA256']}`

RIGHT_R1_UNCHANGED = YES · `{protection['R1_SHA256']}`

WEIGHT_FIELD_MIRROR_PARITY = EXACT_SEMANTIC_MIRROR_MATCH

CORRECTIVE_MIRROR_PARITY = PASS

HUMAN_VISIBLE_RESULT = AGENT_VISIBLE_PASS / HUMAN_REVIEW_PENDING

FINAL_STATUS = READY_FOR_HUMAN_REVIEW

**STOP — HUMAN REVIEW。等待 Human 决策。**
'''
(P/'LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md').write_text(report,encoding='utf-8')
options=''.join(f'<option value="{p["pose"]}">{p["pose"]}</option>' for p in poses['poses'])
qhtml=''.join(f'<tr><td>{q}</td><td>{html.escape(t)}</td><td>{html.escape(a)}</td></tr>' for q,t,a in questions)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Left Hand · Canonical Mirror R1</title>
<style>:root{color-scheme:dark;font:16px/1.6 system-ui,sans-serif;background:#111c28;color:#e4edf5}body{max-width:1360px;margin:auto;padding:32px}h1{font-size:32px;margin:0}p{color:#b9cad9}a{color:#83d9de}header{border-bottom:1px solid #344455;padding-bottom:22px}.badge{display:inline-block;background:#174a43;color:#aff0cf;padding:4px 12px;border-radius:20px;margin-bottom:12px}select,button{font:inherit;background:#233547;color:#e4edf5;border:1px solid #526677;border-radius:6px;padding:8px}nav{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:24px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0;background:#1a2938;border-radius:9px;overflow:hidden}figcaption{padding:12px;font-weight:650}img{width:100%;height:auto;display:block}table{border-collapse:collapse;width:100%;font-size:14px}td{border-bottom:1px solid #344455;padding:9px}code{overflow-wrap:anywhere}.note{background:#1b2d3b;border-left:3px solid #64c1b9;padding:16px;margin:20px 0}details{margin:24px 0}footer{margin:36px 0;color:#9baebf}@media(max-width:700px){body{padding:16px}.pair{gap:8px}h1{font-size:25px}}</style>
<header><div class="badge">READY_FOR_HUMAN_REVIEW</div><h1>LEFT HAND · Canonical Mirror R1</h1><p>R2 唯一 canonical master · 3300 vertices · 21 bones · 完整权重逐值相同</p><b>DESIGN_ONLY / HUMAN_REVIEW_PENDING — 尚未获得 Human 批准</b></header>
<nav><label>批准姿态 <select id="pose">OPTIONS</select></label><label>视角 <select id="view"><option value="PALMAR">PALMAR / teaching</option><option value="DORSAL">DORSAL / general</option><option value="FIRST_WEB">FIRST_WEB / reasonable close</option></select></label><button id="next">下一姿态 →</button></nav>
<div class="pair"><figure><figcaption>RIGHT · 已批准 R2</figcaption><a id="ar"><img id="right" alt="R2 右手产品视角"></a></figure><figure><figcaption>LEFT · 待审候选</figcaption><a id="al"><img id="left" alt="左手候选镜像产品视角"></a></figure></div>
<div class="note"><b id="caption"></b><p id="finding"></p><span id="error"></span></div>
<p>左右摄像机按同一平面镜像，保留掌侧/背侧身份。证据来自实际候选重新打开后的 evaluated geometry；显示保留 R2 原生面着色，未添加平滑、细分或修饰几何。点击图片查看原尺寸。</p>
<details><summary>Q1–Q11 / 审查结论</summary><table>QTABLE</table></details>
<details><summary>镜像规则与精度</summary><p>WRIST rest-local X=0，平面由现有腕骨 Y/Z 轴构成；在 ARMATURE_DATA 中定义并共轭至 mesh data。不是 world-X 假设。Rest_L = S Rest_R H；Basis_L = H Basis_R H；H = diag(-1,1,1,1)。最终对象正 scale / 正行列式。</p><p>权重差值为 0。短 TIP 骨存在 float32 rest-axis 重建误差；全部六项 evaluated mirror 误差小于 0.003 mm。详见报告。现有 driver 未来需 Web 转译，本轮未导出。</p></details>
<p><a href="LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1_REPORT.md">完整报告</a> · <a href="LEFT_HAND_OFFICIAL_L1_MIRROR_CANDIDATE_R1.blend">左手 .blend 候选</a> · <a href="EVIDENCE_ZERO_RIGHT_VS_LEFT_R1.png">ZERO 证据</a> · <a href="EVIDENCE_MIRROR_POSE_REGRESSION_R1.png">六项回归</a> · <a href="EVIDENCE_FIRST_WEB_MIRROR_R1.png">First-web 证据</a></p>
<p>Candidate SHA256<br><code>HASH</code></p><footer>RIGHT_R2_UNCHANGED = YES · RIGHT_R1_UNCHANGED = YES<br>STOP — HUMAN REVIEW。等待 Human 决策。</footer>
<script>const poses=POSEDATA;const selector=document.querySelector('#pose'),view=document.querySelector('#view');function update(){const p=poses.find(p=>p.pose===selector.value);for(const [side,id,a] of [['R','right','ar'],['L','left','al']]){const path='_render_tiles/'+p.pose+'__'+view.value+'__'+side+'.png';document.getElementById(id).src=path;document.getElementById(a).href=path;}document.querySelector('#caption').textContent=p.pose+' · '+view.value;document.querySelector('#finding').textContent=p.visible_findings;document.querySelector('#error').textContent='Evaluated mirror 最大误差 '+p.evaluated_mirror_max_error_mm.toFixed(9)+' mm · Agent visible PASS / Human pending';}selector.onchange=view.onchange=update;document.querySelector('#next').onclick=()=>{selector.selectedIndex=(selector.selectedIndex+1)%selector.options.length;update()};update();</script></html>'''
page=page.replace('OPTIONS',options).replace('QTABLE',qhtml).replace('HASH',sha(candidate)).replace('POSEDATA',json.dumps(poses['poses'],ensure_ascii=False))
(P/'review.html').write_text(page,encoding='utf-8')
write('FINAL_OUTPUT_MANIFEST_R1.json',{'files':[{'path':f.relative_to(P).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(P.rglob('*')) if f.is_file() and f.name!='FINAL_OUTPUT_MANIFEST_R1.json'],'human_approval_pending':True})
assert all((P/'_render_tiles'/f'{p["pose"]}__{v}__{s}.png').exists() for p in poses['poses'] for v in ['PALMAR','DORSAL','FIRST_WEB'] for s in ['R','L'])
print('READY_FOR_HUMAN_REVIEW',sha(candidate),'max_evaluated_error_mm',maxerr)
