import sys
sys.dont_write_bytecode = True
import json, hashlib
from pathlib import Path
OUT = Path(__file__).resolve().parent; ROOT = OUT.parents[1]
PHASE = 'TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1'
def read(n): return json.loads((OUT / n).read_text(encoding='utf-8'))
def dump(n, d): (OUT / n).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
P = read('TUNED_SAVE_REOPEN_PROTECTION_R1.json'); M = read('MINIMUM_MACHINE_AUTOMATIC_R1.json')
assert P['status'] == M['status'] == 'PASS'
renders = read('FINAL_MATCHED_RENDER_MANIFEST_R1.json')['renders']
assert len(renders) == 36 and all((OUT / r['path']).is_file() for r in renders)
cases = {
    'ZERO': {'status': 'PRESERVED_ACCEPTED_STATIC_BASIS', 'note': '已接受的 ZERO 静态形状保持，native positions 和 Basis 坐标逐点不变，corrective 值均为 0。'},
    'FULL_OPP_L1': {'status': 'NO_VISIBLE_REGRESSION', 'note': '局部权重变化后未见明显回退；两项 corrective 在 L1 精确为 0。'},
    'FULL_OPP_L2': {'status': 'IMPROVED_BUT_VISIBLE_ISSUE_REMAINS', 'note': '虎口 floor 的过渡比基线柔和，但仍有角状边缘，尚不判自然度通过。'},
    'FULL_OPP_L3': {'status': 'VISIBLE_ISSUE_STILL_PRESENT', 'note': '硬折角减弱但仍清楚可见，未达到 Human 要求，停止本轮微调。'},
}
status = {
    'PHASE': PHASE, 'ACCEPTANCE_POLICY': 'PRODUCT_VISIBLE_QUALITY_FIRST',
    'PRIOR_HUMAN_REVIEW': {'Q1': 'ACCEPT', 'Q2': 'REJECT', 'Q3': 'YES'},
    'STATIC_GEOMETRY_BASE_FOR_TUNING': P['source'], 'TUNED_ASSET': P['tuned_asset'],
    'ZERO_STATIC_STATUS': cases['ZERO']['status'],
    'FULL_OPP_L1_STATUS': cases['FULL_OPP_L1']['status'],
    'FULL_OPP_L2_STATUS': cases['FULL_OPP_L2']['status'],
    'FULL_OPP_L3_STATUS': cases['FULL_OPP_L3']['status'],
    'NEW_VISIBLE_DEFECT_COUNT': 0, 'RESIDUAL_KNOWN_VISIBLE_ISSUE_CASE_COUNT': 2,
    'DORSAL54_REGRESSION': 'NO', 'PALMAR16_REGRESSION': 'NO',
    'WEIGHT_TUNING_SCOPE': 'PALMAR_THENAR_OPPOSITION_REGION; 372 vertices; only existing WRIST / THUMB_CMC / THUMB_MCP / THUMB_IP influences',
    'WEIGHT_VERTEX_COUNT': P['weight_vertex_count'],
    'GEOMETRY_REWRITE_SCOPE': 'ZERO native/Basis positions: NONE; dynamic local support keys on 257 vertices only',
    'STATIC_GEOMETRY_WRITES': 0, 'POSE_CORRECTIVE_SUPPORT_VERTEX_COUNT': P['corrective_vertex_count'],
    'POSE_CORRECTIVE_KEY_COUNT': 2, 'RIG_BONE_JOINT_REST_CHANGE': 'NO',
    'TOPOLOGY_UV_MATERIALS_GROUPS_MODIFIERS_CHANGE': 'NO',
    'ZERO_CORRECTIVE_VALUES': [0, 0], 'L1_CORRECTIVE_VALUES': [0, 0],
    'MACHINE_SAFETY': 'PASS', 'MACHINE_SAFETY_SCOPE': 'minimum catastrophic checks and ordinary gross visual screen only',
    'ZERO_RESTORE': 'PASS', 'PRODUCTION_PROMOTION': 'NO',
    'PRODUCTION_SAVE_CALLS': 0, 'TUNED_CANDIDATE_SAVE_CALLS': 1,
    'VERDICT': 'VISIBLE_ISSUE_STILL_PRESENT',
    'REMAINING_REPAIR_ROUTE': 'MORE_TARGETED_POSE_CORRECTIVE_SUPPORT_REQUIRED; WEIGHT_ONLY_ATTEMPT_INSUFFICIENT',
    'further_repair_executed': False, 'HUMAN_APPROVAL': 'PENDING', 'Stage6B_FINAL_PASS': 'NOT_SET',
    'STOP': 'HUMAN REVIEW',
}
dump(PHASE + '_STATUS.json', status)
dump('ORDINARY_SOLID_VISUAL_INSPECTION_R1.json', {
    'authority': 'CODEX_PRELIMINARY; FINAL_HUMAN_REQUIRED', 'screened_final_render_count': 36,
    'screen_method': 'All five ordinary-render sheets plus individual target close images', 'cases': cases,
    'new_visible_defects': 0, 'residual_known_issue_case_count': 2,
    'obvious_self_intersection_penetration': 0, 'gross_tearing': 0, 'gross_contamination': 0,
    'obvious_flap': 0, 'dorsal54_regression': 'NO', 'palmar16_regression': 'NO',
    'VERDICT': 'VISIBLE_ISSUE_STILL_PRESENT',
    'remaining_route': status['REMAINING_REPAIR_ROUTE'], 'research_branch_opened': False,
})
dump('MINIMUM_MACHINE_SAFETY_R1.json', {'status': 'PASS', 'NaN_Inf': 0, 'collapsed_face': 0, 'degenerate': 0,
    'obvious_self_intersection_penetration': 0, 'gross_tearing': 0, 'gross_contamination': 0,
    'ZERO_RESTORE': 'PASS', 'visual_fold_issue_is_separate_product_failure': True,
    'hidden_crossing_census': False, 'normal_dot_audit': False, 'true_cap': False, '2127_edge_audit': False})

asset_name = Path(P['tuned_asset']['path']).name
view_options = ''.join(f'<option value="{v}">{t}</option>' for v, t in [('HUMAN_PALMAR','掌侧斜视'),('THENAR_CLOSE','Thenar close'),('SIDE_VOLUME','稍侧体积'),('FULL_PALM','Full palm')])
def pair(pose, view, group):
    return '<div class="pair">' + ''.join(f'<figure><figcaption>{t}</figcaption><button class="image" data-group="{group}" data-asset="{a}" data-pose="{pose}" data-view="{view}" aria-label="放大 {a} {pose} {view}"><img src="renders/{a}__{pose}__{view}.png" alt="{a} · {pose} · {view}"></button></figure>'
        for a, t in [('BASELINE','Current candidate · 已接受静态基线'),('TUNED','Tuned result · 局部权重 + pose support')]) + '</div>'
panels = ''.join(f'<section class="panel" id="{c}" {"" if c=="ZERO" else "hidden"}><h2>{c}</h2>{pair(c,"HUMAN_PALMAR",c)}<p class="muted">{cases[c]["note"]}</p></section>' for c in cases)
panels += '<section class="panel" id="SENTINELS" hidden><h2>dorsal54 / palmar16 sentinel</h2>' + ''.join(f'<h3>{v}</h3>'+pair('ZERO',v,v) for v in ['DORSAL54_SENTINEL','PALMAR16_SENTINEL']) + '</section>'
html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Targeted thenar opposition tuning R1</title>
<style>
:root{font-family:system-ui,"Microsoft YaHei",sans-serif;color-scheme:dark;background:#15191e;color:#edf1f5}*{box-sizing:border-box}body{margin:0;padding:22px}main{max-width:1550px;margin:auto}h1{font-size:23px;margin:0 0 9px}h2{font-size:18px}h3{font-size:14px}p{line-height:1.65}.muted{color:#bdc7d2;font-size:12px}.verdict{color:#f1bf86;font-size:14px}nav{display:flex;gap:8px;margin:15px 0;flex-wrap:wrap}button,select,textarea{font:inherit;color:inherit}nav button,select,.action,.toolbar button{background:#28323e;border:1px solid #677487;border-radius:4px;padding:7px 11px;cursor:pointer}nav button[aria-selected="true"]{background:#405670;border-color:#bdd8f3}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}figure{margin:0;min-width:0}figcaption{font-size:14px;padding:9px 0}.image{padding:0;border:1px solid #49596b;border-radius:5px;width:100%;display:block;overflow:hidden;background:#252d38;cursor:zoom-in}.image img{width:100%;height:auto;display:block}[hidden]{display:none!important}.controls{margin:10px 0}.review{border:1px solid #586b7c;border-radius:5px;padding:17px;margin-top:25px;max-width:1150px}fieldset{padding:10px 0;border:0;margin:0}legend{font-size:14px}label.answer{display:inline-block;margin:8px 25px 0 0}textarea{width:100%;background:#202935;border:1px solid #647487;padding:8px}a{color:#b8dafc}dialog{max-width:98vw;width:1450px;max-height:97vh;border:1px solid #647486;padding:12px;background:#15191e;color:#edf1f5}dialog::backdrop{background:#000c}.toolbar{display:flex;gap:9px;align-items:center;padding-bottom:9px}.toolbar span{flex:1;font-size:13px}dialog img{display:block;max-width:100%;max-height:83vh;width:auto;height:auto;margin:auto}@media(max-width:700px){body{padding:10px}.pair{gap:5px}figcaption{font-size:10px}h1{font-size:18px}}
</style><main><h1>虎口 / 大鱼际连接 · 局部 opposition tuning R1</h1>
<p class="verdict">VISIBLE_ISSUE_STILL_PRESENT · L2 有改善，L3 硬折角仍可见 · DESIGN ONLY / 未推广</p>
<p class="muted">上一轮 Human：ZERO / L1 ACCEPT，L2 / L3 REJECT。已绑定正式记录；本轮答案仍待 Human。静态顶点位置保持不变。</p>
<nav aria-label="比较组"><button data-panel="ZERO" aria-selected="true">ZERO</button><button data-panel="FULL_OPP_L1" aria-selected="false">FULL_OPP_L1</button><button data-panel="FULL_OPP_L2" aria-selected="false">FULL_OPP_L2</button><button data-panel="FULL_OPP_L3" aria-selected="false">FULL_OPP_L3</button><button data-panel="SENTINELS" aria-selected="false">dorsal54 / palmar16</button></nav>
<div class="controls"><select id="view" aria-label="比较视图">''' + view_options + '</select></div>' + panels + '''
<div class="review"><strong>STOP — HUMAN REVIEW</strong><p>局部权重调节让过渡更柔和；本轮小范围 pose support 仍未消除 L3 折角。需要更有针对性的 pose-corrective support，本轮不继续微调。</p>
<p class="muted">最低机器安全 PASS · ZERO restore PASS · 未见新的明显穿模 / flap / tearing / 邻域污染。dorsal54 / palmar16 未见回退。机器门不代表产品折角问题通过。</p>
<form id="human-form"><fieldset><legend>Q1. ZERO 静态是否保持正常？</legend><label class="answer"><input type="radio" name="Q1" value="ACCEPT"> ACCEPT</label><label class="answer"><input type="radio" name="Q1" value="REJECT"> REJECT</label></fieldset><fieldset><legend>Q2. FULL_OPP_L1 / L2 / L3 是否可接受？</legend><label class="answer"><input type="radio" name="Q2" value="ACCEPT"> ACCEPT</label><label class="answer"><input type="radio" name="Q2" value="REJECT"> REJECT</label></fieldset><fieldset><legend>Q3. 是否出现新的明显问题？</legend><label class="answer"><input type="radio" name="Q3" value="NO"> NO</label><label class="answer"><input type="radio" name="Q3" value="YES"> YES</label></fieldset><label class="muted" for="notes">如 YES：case ID + 一句话现象</label><textarea id="notes" rows="2"></textarea><p><button class="action" type="button" id="save-answers">下载审阅答案</button> <span id="answer-state" class="muted"></span></p></form><p class="muted">只下载本地答案，不自动批准或 production promotion。</p><p>''' + f'<a href="{PHASE}_REPORT.md">报告</a> · <a href="{PHASE}_STATUS.json">状态</a> · <a href="{asset_name}" download>DESIGN_ONLY tuned blend</a>' + '''</p></div></main>
<dialog id="lightbox"><div class="toolbar"><button id="prev" aria-label="上一列">←</button><span id="large-title"></span><button id="next" aria-label="下一列">→</button><button id="close">关闭</button></div><img id="large" alt=""></dialog>
<script>
const view=document.getElementById('view'),box=document.getElementById('lightbox'),large=document.getElementById('large');let group=[],index=0;
function redraw(){document.querySelectorAll('.panel:not([hidden]) .image').forEach(b=>{b.dataset.view=view.value;const i=b.querySelector('img');i.src=`renders/${b.dataset.asset}__${b.dataset.pose}__${view.value}.png`;i.alt=`${b.dataset.asset} · ${b.dataset.pose} · ${view.value}`})}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.panel').forEach(p=>p.hidden=p.id!==b.dataset.panel);document.querySelectorAll('nav button').forEach(n=>n.setAttribute('aria-selected',String(n===b)));document.querySelector('.controls').hidden=b.dataset.panel==='SENTINELS';if(b.dataset.panel!=='SENTINELS')redraw()});view.onchange=redraw;
function show(){const i=group[index].querySelector('img');large.src=i.src;large.alt=i.alt;document.getElementById('large-title').textContent=i.alt}
document.querySelectorAll('.image').forEach(b=>b.onclick=()=>{group=[...document.querySelectorAll('.image')].filter(n=>n.dataset.group===b.dataset.group);index=group.indexOf(b);show();box.showModal()});function move(n){index=(index+n+group.length)%group.length;show()}document.getElementById('prev').onclick=()=>move(-1);document.getElementById('next').onclick=()=>move(1);document.getElementById('close').onclick=()=>box.close();document.addEventListener('keydown',e=>{if(box.open&&e.key==='ArrowLeft')move(-1);if(box.open&&e.key==='ArrowRight')move(1)});
document.getElementById('save-answers').onclick=()=>{const f=new FormData(document.getElementById('human-form')),msg=document.getElementById('answer-state');if(!['Q1','Q2','Q3'].every(q=>f.get(q))){msg.textContent='请先完成三题。';return}const d={phase:'TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1',Q1:f.get('Q1'),Q2:f.get('Q2'),Q3:f.get('Q3'),notes:document.getElementById('notes').value,recorded_at:new Date().toISOString(),production_promotion:false},url=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='TARGETED_THENAR_OPPOSITION_HUMAN_RESPONSE_R1.json';a.click();URL.revokeObjectURL(url);msg.textContent='答案已下载，未推广。'};
</script></html>'''
(OUT / 'review.html').write_text(html, encoding='utf-8')
report = f'''# {PHASE}

2026-10-06（Asia/Shanghai）。PRODUCT_VISIBLE_QUALITY_FIRST。

## 结论

**VERDICT = VISIBLE_ISSUE_STILL_PRESENT。** ZERO 保持已接受的静态形状；L1 未见明显回退；L2 的硬折面减弱，但尚留角状边缘；L3 的虎口基底硬折角仍清楚可见。**没有宣布修好或 READY_FOR_HUMAN_VISUAL_APPROVAL。**

本轮先做局部 weight tuning，再做一次局部 pose-corrective support，均未改 ZERO 静态 vertex positions。纯局部权重调节不足以完成这一产品修复，剩余路线应是**更有针对性的 pose-corrective support**；本轮小范围平滑型支持也不足以消除 L3，故停止微调，不新开研究线。该路线判断来自可见效果，不是对唯一数学根因的证明。

## 正式 Human 绑定与隔离基线

用户本轮明示 `Q1 = ACCEPT / Q2 = REJECT / Q3 = YES`；Human note：ZERO 与 FULL_OPP_L1 可接受，FULL_OPP_L2 / L3 在虎口下方 / 大鱼际连接区硬折角不可接受。[正式绑定记录](PRIOR_HUMAN_REVIEW_BINDING_R1.json)保留用户请求路径与 SHA256，并绑定实际 candidate SHA256。

输入：[已接受静态 candidate](../palmar_thenar_source_shape_restoration_r1/RIGHT_HAND_STAGE5B_PALMAR_THENAR_RESTORATION_CANDIDATE_R1.blend)，SHA256 `{P['source']['sha256']}`。本工作区没有 Git repository，使用独立 `audits/targeted_thenar_opposition_weight_tuning_r1` 目录和独立 tuned blend 作为 design asset 分支，未覆盖旧 candidate 或 production。

输出：[{asset_name}]({asset_name})，SHA256 `{P['tuned_asset']['sha256']}`。仍为 DESIGN_ONLY / HUMAN_APPROVAL PENDING / PRODUCTION_PROMOTION NO。

## 实际修复范围

1. **局部权重调节：{P['weight_vertex_count']} vertices。** 仅修改已有 WRIST_R / THUMB_CMC_R / THUMB_MCP_R / THUMB_IP_R 权重。使用 native one-ring 局部 smooth 与紧凑 transition；没有整手 weight solver。其他 influence columns 和区域外权重精确保持。
2. **局部动态支持：{P['corrective_vertex_count']} vertices，2 relative shape keys。** 从 L2 / L3 的 posed local surface 生成一个固定边界、紧凑 falloff 的有限 corrective，存为 native key delta。只软化局部动态 surface，不 fair / rewrite 静态 Basis。简单 drivers 依据既有 CMC opposition 与 MCP flexion 通道作门控，无新骨骼、joint、rest、modifier 或控制器。
3. **ZERO / L1 关闭支持。** 实际 clean-reopen 后求值：ZERO key values `[0,0]`；L1 `[0,0]`；L2 `[1,0]`；L3 `[0,1]`。组合 flexion 门控阻止仅 CMC 通道激活支持。其他未测试姿态不获资格声明。

区域限制在 PALMAR_THENAR_OPPOSITION_REGION：虎口下方、上部 thenar connection、palmar thumb-root、lower first-web floor 与局部 transition。dorsal54 / palmar16 / 原 normal69 及直接边界锁定；不改变无关四指主体。

## 产品结果

| Case | 状态 | 可见结果 |
| --- | --- | --- |
''' + '\n'.join(f'| {c} | {r["status"]} | {r["note"]} |' for c, r in cases.items()) + f'''

`NEW_VISIBLE_DEFECT_COUNT = 0` 指未观察到新的独立明显缺陷。原已知的硬折角问题仍有 L2 / L3 两个 residual case，尤其 L3；这不是“缺陷为零”或产品通过。

掌面主鼓起、first-web 开口与四指关系没有明显被带坏；未见新的 gross flap / penetration / tearing / contamination。dorsal54 / palmar16 matched sentinel 未见回退。

## 最低机器安全与保存核验

36 张 final matched ordinary renders：ZERO 与三种 FULL_OPP，每组 current candidate / tuned result，4 views；另有4张 sentinel。全部通过五张实体 inspection sheets 筛查，重点 close 另逐图检查。同相机、light、material、scale、image size；cavity OFF。

NaN / Inf = 0；collapsed face = 0；degenerate = 0；明显 self-intersection / penetration = 0；gross tearing = 0；gross contamination = 0；ZERO restore PASS。可见 gross 门不声称所有隐蔽数学 crossing 为零。局部硬折角是仍未通过的产品条件。

Clean reopen 确认原 native vertex positions 与新增 Basis 坐标逐点保持；topology、vertex IDs、UV、materials、groups、骨骼 / joints / rest matrices / modifiers 精确一致。变化只包含明确局部权重、两个局部 shape keys 及其简单驱动。Source candidate 和正式 production 不变。每个正式 case 都先 RESET ZERO，再 apply 原 Stage6B 定义、evaluate、render、RESET ZERO；最终所有21 pose channels ZERO，keys ZERO。未保存 nonzero pose。

机器安全 PASS 与产品 verdict VISIBLE_ISSUE_STILL_PRESENT 分开记录。没有 normal-dot、2127 edge、true-cap、隐藏 crossing census、大范围 Stage6A/Stage6B 资格流程或新 root-cause 研究。

## 最终字段

| 字段 | 值 |
| --- | --- |
''' + '\n'.join(f'| {k} | {status[k]} |' for k in ['ZERO_STATIC_STATUS','FULL_OPP_L1_STATUS','FULL_OPP_L2_STATUS','FULL_OPP_L3_STATUS','NEW_VISIBLE_DEFECT_COUNT','DORSAL54_REGRESSION','PALMAR16_REGRESSION','WEIGHT_TUNING_SCOPE','GEOMETRY_REWRITE_SCOPE','MACHINE_SAFETY','PRODUCTION_PROMOTION','VERDICT']) + f'''

## Human review 与停止

[review.html](review.html) 提供 ZERO、L1、L2、L3 current/tuned 同机位比较，以及 dorsal54 / palmar16 sentinel；main、thenar close、side、full palm 可切换。Human 只回答 Q1 static、Q2 L1/L2/L3、Q3 新问题；本轮答案未预选，上一轮 Human 结论不会被填进新表单。

**STOP — HUMAN REVIEW。** 不继续 weight/geometry/corrective 微调，不自动进入后续路线，不做 production promotion 或 Stage6B final PASS。

证据：[状态]({PHASE}_STATUS.json)、[save/reopen](TUNED_SAVE_REOPEN_PROTECTION_R1.json)、[最低自动检查](MINIMUM_MACHINE_AUTOMATIC_R1.json)、[最低安全](MINIMUM_MACHINE_SAFETY_R1.json)、[普通视觉记录](ORDINARY_SOLID_VISUAL_INSPECTION_R1.json)。
'''
(OUT / (PHASE + '_REPORT.md')).write_text(report, encoding='utf-8')
dump('DELIVERY_VERIFICATION_R1.json', {'status': 'FILES_READY_BROWSER_PENDING', 'required_files_present': True,
    'tuned_asset_clean_reopen': 'PASS', 'final_render_count': 36, 'Human_choices_preselected': False,
    'VERDICT': 'VISIBLE_ISSUE_STILL_PRESENT', 'PRODUCTION_PROMOTION': 'NO'})
print('REPORT_STATUS_REVIEW_READY; VISIBLE_ISSUE_STILL_PRESENT; STOP HUMAN REVIEW')
