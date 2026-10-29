"""Report and minimal Human review for the selected position-only design clone."""
import sys
sys.dont_write_bytecode = True
import hashlib, json
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PHASE = 'PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1'
def read(n): return json.loads((OUT / n).read_text(encoding='utf-8'))
def dump(n, d): (OUT / n).write_text(json.dumps(d, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
G = read('ITERATION_03_GEOMETRY.json')
P = read('CANDIDATE_SAVE_REOPEN_PROTECTION_R1.json')
M = read('MATCHED_RENDER_MANIFEST_R1.json')
A = read('MINIMUM_MACHINE_AUTOMATIC_R1.json')
assert P['status'] == A['status'] == 'PASS' and len(M['renders']) == 46
for r in M['renders']: assert (OUT / r['path']).is_file()
visual = {
    'ZERO': {'result': 'CLEARLY_IMPROVED', 'note': '虎口下方连接斜面与大鱼际上缘更饱满，first-web 开口保留；未见前两版的静态硬折面。'},
    'FULL_OPP_L1': {'result': 'CLEARLY_IMPROVED', 'note': '连接区改善仍可见，大鱼际主鼓起保留；局部基底 crease 更清楚，最终自然度由 Human 决定。'},
    'FULL_OPP_L2': {'result': 'NEW_VISIBLE_PROBLEM', 'note': '增加的静态体积在虎口基底形成更突出的硬折角 / 压挤凹槽，position-only 尚未达到自然形变目标。'},
    'FULL_OPP_L3': {'result': 'NEW_VISIBLE_PROBLEM', 'note': '虎口 floor 的角状折面与凹槽更明显；下部 thenar mass 仍在，但局部上缘的体积保持外观不合格。'},
}
dump('ORDINARY_SOLID_VISUAL_INSPECTION_R1.json', {
    'reviewer': 'CODEX_PRELIMINARY_VISUAL_SCREEN', 'Human_final_authority': True,
    'final_render_images_screened': 46, 'method': 'All final ordinary render contact sheets plus individual main and thenar close images; no hidden crossing analysis',
    'cases': visual, 'dorsal54_regression': 'NO', 'palmar16_regression': 'NO',
    'new_visible_defect_family_count': 1, 'new_visible_defect_pose_instance_count': 2,
    'new_visible_defect_family': 'MORE_PRONOUNCED_WEB_FLOOR_ANGULAR_COMPRESSION_L2_L3',
    'obvious_self_intersection_or_gross_penetration': 0, 'obvious_tearing': 0,
    'gross_neighbor_contamination': 0, 'gross_thenar_disappearance': 0,
    'product_shape_issue_is_not_catastrophic_collapsed_face': True,
    'ZERO_SHAPE_PASS': 'YES_CODEX_PRELIMINARY_ONLY', 'OPPOSITION_VOLUME_PRESERVATION_FAIL': 'YES',
    'iterations': [
        {'id': '01', 'result': 'NEW_VISIBLE_PROBLEM', 'reason': 'Direct neutral donor-position blend introduced web-floor hard facets; not saved as candidate'},
        {'id': '02', 'result': 'NEW_VISIBLE_PROBLEM', 'reason': 'Raw transverse donor displacements retained a thumb-wall ledge; not saved as candidate'},
        {'id': '03', 'result': 'CLEARLY_IMPROVED_ZERO_SELECTED', 'reason': 'Smooth interpolation of donor contour field and distal taper retained RSSF shaft/web opening; saved as the sole design clone'},
    ],
})
machine = {'MACHINE_SAFETY': 'PASS', 'automatic_status': 'PASS', 'NaN_Inf': 0,
           'collapsed_face': 0, 'degenerate': 0, 'obvious_self_intersection_penetration': 0,
           'obvious_tearing': 0, 'ZERO_restore': 'PASS', 'gross_neighbor_contamination': 0,
           'product_opposition_hard_fold_issue_present': True,
           'scope': 'minimum catastrophic checks + ordinary-solid gross screen, not exhaustive intersections',
           'hidden_crossing_census': False}
dump('MINIMUM_MACHINE_SAFETY_R1.json', machine)
status = {
    'PHASE': PHASE, 'ACCEPTANCE_POLICY': 'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST',
    'DONOR_SOURCE': 'BLENDER_HUMAN_BASE_MESHES_V1_4_1_HAND_REALISTIC_OFFICIAL_MULTIRES_L1',
    'DONOR_FILE': G['donor'], 'CANDIDATE': P['candidate'], 'DESIGN_ONLY': True,
    'RESTORATION_VERTEX_COUNT': len(G['vertex_ids']),
    'RESTORATION_CORE_VERTEX_COUNT': len(G['core_ids']), 'TRANSITION_VERTEX_COUNT': len(G['transition_ids']),
    'RESTORATION_REGION': 'PALMAR_THENAR_VOLUME_REGION; lower first-web floor, upper thenar, palmar thumb-root connection and compact transition',
    'GEOMETRY_REPAIR': 'LOCAL_THENAR_VOLUME_RESTORATION',
    **{pose + '_VISIBLE_RESULT': row['result'] for pose, row in visual.items()},
    'DORSAL54_REGRESSION': 'NO', 'PALMAR16_REGRESSION': 'NO',
    'NEW_VISIBLE_DEFECT_COUNT': 2, 'NEW_VISIBLE_DEFECT_COUNT_SEMANTICS': 'one angular-compression family observed in two pose cases L2/L3',
    'MACHINE_SAFETY': 'PASS', 'ZERO_RESTORE': 'PASS',
    'ZERO_SHAPE_PASS': 'YES', 'ZERO_SHAPE_PASS_AUTHORITY': 'CODEX_PRELIMINARY; HUMAN_PENDING',
    'OPPOSITION_VOLUME_PRESERVATION_FAIL': 'YES',
    'OPPOSITION_FAIL_DESCRIPTION': 'local web-floor angular compression at L2/L3; not a claim of whole-thenar disappearance or proven weight root cause',
    'WEIGHTS_CHANGED': 'NO', 'RIG_CHANGED': 'NO', 'JOINTS_CHANGED': 'NO',
    'MODIFIERS_CHANGED': 'NO', 'GROUPS_CHANGED': 'NO',
    'TOPOLOGY_VERTEX_IDS_UV_MATERIALS_CHANGED': 'NO',
    'WEIGHT_CHANGE_REQUIRED': 'NOT_DETERMINED; NEXT_RECORDED_ONLY',
    'RIG_CHANGE_REQUIRED': 'NO', 'RET0PO_REQUIRED': 'NO',
    'PRODUCTION_PROMOTION': 'NO', 'PRODUCTION_SAVE_CALLS': 0, 'CANDIDATE_SAVE_CALLS': 1,
    'Stage6A_HUMAN_PASS_ANCESTOR_RECEIPTS': 'RETAINED_UNCHANGED; NOT_REISSUED_FOR_CANDIDATE',
    'Stage6B_FINAL_PASS': 'NOT_SET', 'HUMAN_APPROVAL': 'PENDING',
    'VERDICT': 'ZERO_SHAPE_PASS_OPPOSITION_VOLUME_PRESERVATION_FAIL_STOP_HUMAN_REVIEW',
    'NEXT': 'TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1', 'NEXT_EXECUTED': False,
    'STOP': 'HUMAN REVIEW',
}
dump(PHASE + '_STATUS.json', status)

candidate_name = Path(P['candidate']['path']).name
views = {'HUMAN_PALMAR': '掌侧斜视 · Human 历史机位', 'FULL_PALM': 'Full palm · 全掌',
         'THENAR_CLOSE': 'Thenar close · 连接区', 'SIDE_VOLUME': 'Side volume · 稍侧视图',
         'SILHOUETTE': 'Silhouette · 轮廓', 'FIRST_WEB_CLOSE': 'First-web close · 虎口'}
def options(names): return ''.join(f'<option value="{v}">{views[v]}</option>' for v in names)
def figure(asset, pose, view, title, group):
    return f'<figure><figcaption>{title}</figcaption><button class="image" data-group="{group}" data-asset="{asset}" data-pose="{pose}" data-view="{view}" aria-label="放大 {title} {pose}"><img src="renders/{asset}__{pose}__{view}.png" alt="{title} · {pose} · {view}"></button></figure>'
static_group = '<div class="grid three">' + ''.join(figure(a, p, 'HUMAN_PALMAR', t, 'static') for a, p, t in [
    ('OFFICIAL_L1', 'NEUTRAL', 'A · OFFICIAL L1 / Stage2 donor'), ('CURRENT', 'ZERO', 'B · CURRENT ZERO / RSSF'),
    ('CANDIDATE', 'ZERO', 'C · CANDIDATE ZERO / RSSF')]) + '</div>'
def pair(pose, view='HUMAN_PALMAR'):
    return '<div class="grid two">' + ''.join(figure(a, pose, view, t, pose) for a, t in [
        ('CURRENT', 'Current'), ('CANDIDATE', 'Restoration candidate')]) + '</div>'
sentinels = ''.join(f'<h3>{v}</h3>' + pair('ZERO', v).replace('data-group="ZERO"', f'data-group="{v}"')
                   for v in ['DORSAL54_SENTINEL', 'PALMAR16_SENTINEL'])
html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Palmar thenar restoration R1 · DESIGN ONLY</title>
<style>
:root{font-family:system-ui,"Microsoft YaHei",sans-serif;color-scheme:dark;background:#15191e;color:#edf1f5}*{box-sizing:border-box}
body{margin:0;padding:22px}main{max-width:1750px;margin:auto}h1{font-size:23px;margin:0 0 8px}h2{font-size:18px}h3{font-size:14px}
p{line-height:1.65;margin:8px 0}.muted{color:#bdc7d2;font-size:12px}.badge{color:#f3cd91;font-size:13px}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}button,select,textarea{font:inherit;color:inherit}
nav button,select,.action,.toolbar button{border:1px solid #657183;background:#28313d;border-radius:4px;padding:7px 11px;cursor:pointer}
nav button[aria-selected="true"]{background:#3a5067;border-color:#a9c8e8}.grid{display:grid;gap:12px}.three{grid-template-columns:repeat(3,minmax(0,1fr))}.two{grid-template-columns:repeat(2,minmax(0,1fr))}
figure{margin:0;min-width:0}figcaption{padding:10px 0;font-size:14px}.image{padding:0;width:100%;display:block;border:1px solid #465361;border-radius:5px;overflow:hidden;background:#27303a;cursor:zoom-in}.image img{display:block;width:100%;height:auto}
[hidden]{display:none!important}.controls{margin:10px 0 14px}.note{border-left:3px solid #d3ae73;padding:8px 13px;margin:15px 0;background:#1e2530}
.review{margin-top:26px;padding:18px;border:1px solid #516070;border-radius:6px;max-width:1200px}fieldset{border:0;padding:10px 0;margin:0}legend{font-size:14px}label.answer{display:inline-block;margin:8px 24px 0 0;font-size:14px}textarea{width:100%;background:#202833;border:1px solid #647083;padding:8px;resize:vertical}a{color:#b7d8fb}
dialog{width:1450px;max-width:98vw;max-height:97vh;background:#15191e;color:#edf1f5;border:1px solid #627086;padding:12px}dialog::backdrop{background:#000c}.toolbar{display:flex;gap:9px;align-items:center;margin-bottom:9px}.toolbar span{flex:1;font-size:13px}dialog img{display:block;max-height:83vh;max-width:100%;width:auto;height:auto;margin:auto}
@media(max-width:750px){body{padding:10px}.grid{gap:5px}figcaption{font-size:10px}h1{font-size:18px}nav button{font-size:12px}}
</style><main><h1>虎口下方 / 大鱼际连接 · Source shape restoration R1</h1>
<p class="badge">DESIGN ONLY · 323 个局部顶点 · 保持 rig / weights · 未推广</p>
<nav aria-label="审阅屏幕"><button data-panel="zero" aria-selected="true">1 · ZERO 三列</button><button data-panel="l1" aria-selected="false">2 · FULL_OPP_L1</button><button data-panel="l23" aria-selected="false">3 · FULL_OPP_L2 / L3</button><button data-panel="sentinel" aria-selected="false">4 · dorsal54 / palmar16</button></nav>
<section id="zero" class="panel"><div class="controls"><label>静态视图 <select id="static-view">''' + options(views) + '''</select></label></div>
<p class="muted">SOURCE_VISUAL_REFERENCE_ONLY · Official L1 保持原始中性姿态；当前与 candidate 都是 ZERO / RSSF。三列统一相机、比例、材质与光照，source 姿态不构成精确几何叠加。</p>
''' + static_group + '''<p class="muted">Codex 初步：CLEARLY_IMPROVED。请重点看虎口下方斜面、大鱼际上缘和连接连续性；点击图可放大，并左右切换。</p></section>
<section id="l1" class="panel" hidden><h2>FULL_OPP_L1 · CMC 10° / MCP 10° / IP 5°</h2><div class="controls"><label>视图 <select id="l1-view">''' + options(['HUMAN_PALMAR', 'THENAR_CLOSE', 'SIDE_VOLUME', 'FULL_PALM']) + '''</select></label></div>
''' + pair('FULL_OPP_L1') + '''<p class="muted">Codex 初步：CLEARLY_IMPROVED。连接区改善保留；虎口基底 crease 的自然程度仍待 Human 判断。</p></section>
<section id="l23" class="panel" hidden><div class="controls"><label>L2 / L3 视图 <select id="l23-view">''' + options(['HUMAN_PALMAR', 'THENAR_CLOSE', 'SIDE_VOLUME', 'FULL_PALM']) + '''</select></label></div>
<h2>FULL_OPP_L2 · CMC 20° / MCP 20° / IP 10°</h2>''' + pair('FULL_OPP_L2') + '''<h2>FULL_OPP_L3 · CMC 30° / MCP 30° / IP 15°</h2>''' + pair('FULL_OPP_L3') + '''
<div class="note">Codex 初步：L2 / L3 = NEW_VISIBLE_PROBLEM。虎口基底硬折角比 Current 更突出；下部大鱼际仍在，但 position-only 未达到局部体积保持的产品目标。请切换 Thenar close 核对。</div></section>
<section id="sentinel" class="panel" hidden><h2>回归 sentinel · Current / Candidate ZERO</h2>''' + sentinels + '''<p class="muted">原 dorsal54 / palmar16 顶点和邻接边界锁定；Codex 未见回退。旧 Human PASS 记录保持原样。</p></section>
<div class="review"><p><strong>STOP — HUMAN REVIEW</strong></p><p>ZERO 静态改善；L2/L3 仍有更突出的局部压挤折角。当前 candidate 保留给 Human 审阅，不继续修改静态 geometry，不调整权重。</p>
<p class="muted">最低机器安全 PASS · ZERO restore PASS · 未见明显穿模 / tearing / 邻指污染。局部硬折角是单独的产品外观问题。</p>
<form id="human-form"><fieldset><legend>Q1. Candidate ZERO 手掌形状是否正常？</legend><label class="answer"><input type="radio" name="Q1" value="ACCEPT"> ACCEPT</label><label class="answer"><input type="radio" name="Q1" value="REJECT"> REJECT</label></fieldset>
<fieldset><legend>Q2. FULL_OPP L1/L2/L3 是否正常？</legend><label class="answer"><input type="radio" name="Q2" value="ACCEPT"> ACCEPT</label><label class="answer"><input type="radio" name="Q2" value="REJECT"> REJECT</label></fieldset>
<fieldset><legend>Q3. 是否发现新的明显问题？</legend><label class="answer"><input type="radio" name="Q3" value="NO"> NO</label><label class="answer"><input type="radio" name="Q3" value="YES"> YES</label></fieldset>
<label class="muted" for="human-notes">补充（可选：case ID + 可见问题）</label><textarea id="human-notes" rows="2"></textarea>
<p><button class="action" type="button" id="export-response">下载审阅答案</button> <span id="response-message" class="muted"></span></p></form>
<p class="muted">答案仅在此页面选择，点击下载才生成本地文件；不自动认定批准或推广。</p>
<p class="muted">NEXT = TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1 · 仅记录，未执行。</p>
<p>''' + f'<a href="{PHASE}_REPORT.md">报告</a> · <a href="{PHASE}_STATUS.json">状态</a> · <a href="{candidate_name}" download>DESIGN_ONLY candidate blend</a>' + '''</p></div></main>
<dialog id="lightbox"><div class="toolbar"><button id="previous" aria-label="上一列">←</button><span id="image-title"></span><button id="next" aria-label="下一列">→</button><button id="close-box">关闭</button></div><img id="large" alt=""></dialog>
<script>
const box=document.getElementById('lightbox'),large=document.getElementById('large'),title=document.getElementById('image-title');let group=[],index=0;
function redraw(b,view){b.dataset.view=view;const img=b.querySelector('img');img.src=`renders/${b.dataset.asset}__${b.dataset.pose}__${view}.png`;img.alt=`${b.dataset.asset} · ${b.dataset.pose} · ${view}`}
function update(selector,view){document.querySelectorAll(selector).forEach(b=>redraw(b,view))}
document.getElementById('static-view').onchange=e=>update('#zero .image',e.target.value);
document.getElementById('l1-view').onchange=e=>update('#l1 .image',e.target.value);
document.getElementById('l23-view').onchange=e=>update('#l23 .image',e.target.value);
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.panel').forEach(p=>p.hidden=p.id!==b.dataset.panel);document.querySelectorAll('nav button').forEach(n=>n.setAttribute('aria-selected',String(n===b)))});
function display(){const img=group[index].querySelector('img');large.src=img.src;large.alt=img.alt;title.textContent=img.alt}
document.querySelectorAll('.image').forEach(b=>b.onclick=()=>{group=[...document.querySelectorAll('.image')].filter(n=>n.dataset.group===b.dataset.group);index=group.indexOf(b);display();box.showModal()});
function move(n){index=(index+n+group.length)%group.length;display()}
document.getElementById('previous').onclick=()=>move(-1);document.getElementById('next').onclick=()=>move(1);document.getElementById('close-box').onclick=()=>box.close();document.addEventListener('keydown',e=>{if(box.open&&e.key==='ArrowLeft')move(-1);if(box.open&&e.key==='ArrowRight')move(1)});
document.getElementById('export-response').onclick=()=>{const f=new FormData(document.getElementById('human-form')),msg=document.getElementById('response-message');if(!['Q1','Q2','Q3'].every(q=>f.get(q))){msg.textContent='请先完成三题。';return}const result={phase:'PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1',Q1:f.get('Q1'),Q2:f.get('Q2'),Q3:f.get('Q3'),notes:document.getElementById('human-notes').value,recorded_at:new Date().toISOString(),production_promotion:false};const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='PALMAR_THENAR_RESTORATION_HUMAN_RESPONSE_R1.json';a.click();URL.revokeObjectURL(url);msg.textContent='审阅答案已下载；未自动推广。'};
</script></html>'''
(OUT / 'review.html').write_text(html, encoding='utf-8')

report = f'''# {PHASE}

2026-10-06（Asia/Shanghai）。PRODUCT SHAPE REPAIR；HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST。

## 结果与停止点

已创建并 clean-reopen 核对 **DESIGN_ONLY position-only candidate**，修改 **{len(G['vertex_ids'])} 个局部顶点 = {len(G['core_ids'])} 个 core + {len(G['transition_ids'])} 个 transition**。原正式资产未覆盖。

**ZERO 与 FULL_OPP_L1：CLEARLY_IMPROVED。FULL_OPP_L2 / L3：NEW_VISIBLE_PROBLEM。**

ZERO 的虎口下方斜面、大鱼际上缘和拇指根掌侧连接更饱满，保持原 first-web 开口和 crease。L1 的静态改善仍可见。L2/L3 在同一冻结权重下，虎口 floor 出现更突出的硬折角 / 局部压挤凹槽。因此本轮**不判 READY_FOR_HUMAN_APPROVAL，也不判 Stage6B final PASS**。最低 catastrophic 机器门通过不代表局部形变产品外观通过。

`ZERO_SHAPE_PASS = YES` 是 Codex 初步静态判断，最终 Human 尚未批准。`OPPOSITION_VOLUME_PRESERVATION_FAIL = YES` 指 L2/L3 的局部上缘 / floor 压挤外观；下部 thenar mass 仍在，不等于全块大鱼际消失，也未证明权重是唯一根因。

按用户第十三条停止逻辑，保留当前静态 candidate，不继续通过改静态 geometry 掩盖 pose 问题。`NEXT = TARGETED_THENAR_OPPOSITION_WEIGHT_TUNING_R1`，**仅记录，未执行**。**STOP — HUMAN REVIEW。**

## 输入与 candidate

- 正式输入：`{P['current']['path']}`。
- 正式输入 SHA256：`{P['current']['sha256']}`，前后仍是用户指定的 `90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa`。
- 官方 donor：`{G['donor']['path']}`，SHA256 `{G['donor']['sha256']}`。
- Candidate：[RIGHT_HAND_STAGE5B_PALMAR_THENAR_RESTORATION_CANDIDATE_R1.blend]({candidate_name})，SHA256 `{P['candidate']['sha256']}`。

Official Hand - Realistic 的 actual stored Multires L1 本轮只读求值，原生坐标与 faces 和既有已验证 snapshot 精确一致。采用已验证、与 Stage2 等价的 official L1；不替换整手、不转入 source topology。

## 局部 source-profile restoration

复用已验证 rigid display registration、historical current-to-base native identity 与 split-parent ancestry。以当前保留的 lower-thenar surface anchors 对 donor 作平移放置；donor 本身不改形状。提取 donor 相对当前的横向轮廓与掌侧饱满度分量，以同一局部 source profile field 连续转移到现有 engineering topology；保留当前 RSSF 轴向安排和上方 thumb shaft。

source profile field 的插值 support 为 9 mm；这只插值 donor-derived displacement 值，**没有平均 / fair 当前 mesh coordinates**，不是自由 smoothing 或 generic fairing。Generated CMC transition vertices 接受该同一场的连续延拓，未为它们编造 exact donor vertex-ID pairing。

选定 blend strength = 0.38，局部 compact footprint 与 smooth transition 仅覆盖 thenar / palmar thumb-root / lower first-web floor。它不扩展到整个 palm、wrist、四指掌侧或整手。更远区域原坐标保持精确不变。顶点 ID 及 donor parentage / field extension 记录于 [选定形状记录](ITERATION_03_GEOMETRY.json)。

这是一种由 source 轮廓和体积引导、适配 RSSF 的产品恢复，不是逐毫米复制原始中性 donor。没有进行 anatomy、根因、CMC-axis、retopo 或 topology-correspondence 研究。

## 少量视觉迭代

共三版内存静态预览。前两版在虎口基底引入硬折面，未保存成 blend，未进入 opposition smoke。第三版通过 donor profile field 插值、轴向保留与 distal transition 解决静态新折面，选为唯一正式 design candidate。Candidate blend 只保存一次，且在 ZERO；后续 pose 全部在内存，最后 RESET ZERO，未保存 posed blend。

达到静态明显改善后，才运行三个 FULL_OPP 当前 / candidate matched visual smoke。发现 L2/L3 局部产品问题后，按用户要求停止静态迭代。未添加 CMC_MCP_L3，因为三个正式 FULL_OPP 已足以展示剩余问题。

## Human-visible 分类

| Case | Codex 初步分类 | 人眼观察 |
| --- | --- | --- |
''' + '\n'.join(f'| {pose} | {row["result"]} | {row["note"]} |' for pose, row in visual.items()) + f'''

`NEW_VISIBLE_DEFECT_COUNT = 2` 按 pose occurrence 计数：同一类“更突出的 web-floor angular compression”分别见于 L2、L3；不是两个独立拓扑破洞。既有 Current 的高等级 compression crease 也存在，candidate 在该处更硬 / 更角状，因此未把它自动归为通过。

## 普通实体证据与保护

46 张 final matched renders：18 张静态三列（6 camera families）、24 张 opposition current/candidate（3 cases × 4 families × 2 assets）、4 张 dorsal54 / palmar16 回归 sentinel。全部通过六张普通实体 inspection sheets 筛查，并单独看过主要静态、pose 主图与 thenar close。没有 forensic wire、normal-dot、hidden crossing census 或细微数值优化。

当前 / candidate 每组同一相机 center、direction、scale、image size、灰色材质与 studio lighting；cavity OFF。相机沿用上一轮正式 FULL_OPP_L1 掌侧斜视 family。Source default 是未改形状的原始中性 L1，采用已有刚体显示配准，标记 SOURCE_VISUAL_REFERENCE_ONLY，不能当作 RSSF exact overlay。

实际 candidate save/reopen 确认：只有 mesh vertex positions 不同。Topology、vertex order、faces、edges、loops、UV、materials、groups、weights、modifier、bones、joints、parents、rest matrices 与 pose reset 状态完整一致。Roll 所决定的 native rest orientation / matrices 精确保持；没有 edit-mode 或 bone setter。

dorsal54、palmar16、此前 normal69，以及 prior approved patch 的直接邻接边界锁定。原 approved vertices 的 position drift 均 0；matched sentinel 未见回退。其他手掌和四指普通实体图未见 gross contamination。Stage6A Human PASS closure 与 receipt 文件前后 hash 保留，**没有将旧 Human PASS 自动移授给新 candidate**，也未重新宣布 Stage6A / Stage6B Human PASS。

## 最低安全门

NaN / Inf = 0；collapsed face = 0；degenerate = 0；明显 gross self-intersection / penetration = 0；明显 tearing = 0；gross neighbor contamination = 0；ZERO restore = PASS。后三项是普通实体可见筛查，未声称没有所有数学 self-intersections。

Current 与 candidate 均对 L1、L2、L3 执行 RESET ZERO → 原定义 apply → evaluate → render → RESET ZERO，6 次 reset 全 PASS，最终 21 pose channels ZERO。静态 + pose 的最低检查均通过。局部角状折痕作为产品外观问题单独记录，不与 catastrophic face collapse 混为一谈。

## 最终字段

| 字段 | 值 |
| --- | --- |
''' + '\n'.join(f'| {k} | {v} |' for k, v in status.items() if k in [
    'DONOR_SOURCE', 'RESTORATION_VERTEX_COUNT', 'RESTORATION_REGION', 'ZERO_VISIBLE_RESULT',
    'FULL_OPP_L1_VISIBLE_RESULT', 'FULL_OPP_L2_VISIBLE_RESULT', 'FULL_OPP_L3_VISIBLE_RESULT',
    'DORSAL54_REGRESSION', 'PALMAR16_REGRESSION', 'NEW_VISIBLE_DEFECT_COUNT', 'MACHINE_SAFETY',
    'ZERO_RESTORE', 'WEIGHTS_CHANGED', 'RIG_CHANGED', 'PRODUCTION_PROMOTION', 'VERDICT',
    'ZERO_SHAPE_PASS', 'OPPOSITION_VOLUME_PRESERVATION_FAIL', 'NEXT', 'NEXT_EXECUTED']) + f'''

## 审阅

[review.html](review.html)：第一屏 Official L1 / Current ZERO / Candidate ZERO；第二屏 L1；第三屏 L2/L3；第四屏 dorsal54 / palmar16 sentinel。静态可切换 full palm、thenar close、side、silhouette、first-web close；pose 可切换 main、thenar close、side、full palm。点击图片放大，左右切换同组。Human 的 Q1/Q2/Q3 均未预选；页面可下载本地审阅答案，不自动批准或 promotion。

候选文件内部 scene flag 为 DESIGN_ONLY / HUMAN_APPROVAL PENDING / PRODUCTION_PROMOTION NO。没有 weight / joint / rig edit、左手镜像、motion retarget、Web export 或 production promotion。正式当前资产继续保持原样。

证据：[状态]({PHASE}_STATUS.json)、[save/reopen 与只读保护](CANDIDATE_SAVE_REOPEN_PROTECTION_R1.json)、[最低安全](MINIMUM_MACHINE_SAFETY_R1.json)、[姿态与历史保护](POSE_DEFINITION_AND_PROTECTION_R1.json)、[普通实体视觉记录](ORDINARY_SOLID_VISUAL_INSPECTION_R1.json)、[matched manifest](MATCHED_RENDER_MANIFEST_R1.json)。
'''
(OUT / (PHASE + '_REPORT.md')).write_text(report, encoding='utf-8')
dump('DELIVERY_VERIFICATION_R1.json', {'status': 'FILES_READY_BROWSER_PENDING', 'render_count': 46,
     'candidate_clean_reopen': 'PASS', 'required_report_status_review_candidate_present': True,
     'required_final_fields_present': True, 'Human_choices_preselected': False,
     'NEXT_EXECUTED': False, 'production_promotion': 'NO'})
print('REPORT_STATUS_REVIEW_READY; ZERO improved; L2/L3 product issue; NEXT recorded only; STOP HUMAN REVIEW')
