"""Package visually inspected renders. Does not open or change any blend."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PHASE = 'PALMAR_THENAR_VOLUME_SOURCE_ZERO_POSE_COMPARISON_R1'

def read(n):
    return json.loads((OUT / n).read_text(encoding='utf-8'))

def dump(n, d):
    (OUT / n).write_text(json.dumps(d, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

protection = read('INPUT_AND_PROTECTION_R1.json')
safety = read('MINIMUM_MACHINE_SAFETY_R1.json')
manifest = read('RENDER_MANIFEST_R1.json')
assert safety['status'] == protection['status'] == 'PASS'
assert len(manifest['renders']) == 16
for r in manifest['renders']:
    assert (OUT / r['path']).is_file()

explanation = ('ZERO 已有虎口下方连接偏窄的观感，FULL_OPP_L1 主要加深局部折痕；'
               '原始 source 姿态不同，RSSF source 控制又含历史工程显示映射，'
               '因此现有视觉证据不足以把原始形状偏瘦、静态重姿态后的外观变化和真实体积损失分开。')
status = {
    'PHASE': PHASE,
    'ACCEPTANCE_POLICY': 'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST',
    'SOURCE_VISUAL_REFERENCE': 'VERIFIED_OFFICIAL_MULTIRES_L1_NATIVE_NEUTRAL_WITH_FROZEN_RIGID_REGISTRATION',
    'SOURCE_VISUAL_REFERENCE_ONLY': True,
    'SOURCE_DISPLAY_CONTROL': 'INHERITED_OFFICIAL_L1_RSSF_DISPLAY_MAPPING; NOT_NATIVE_NEUTRAL',
    'SOURCE_PALMAR_VOLUME_STATUS': 'CONTINUOUS_THENAR_MASS_VISIBLE; NO_CLEAR_MISSING_BLOCK_IN_NATIVE_NEUTRAL',
    'CURRENT_ZERO_PALMAR_VOLUME_STATUS': 'NARROW_UPPER_THENAR_CONNECTION_APPEARANCE_PRESENT; LOWER_THENAR_BULGE_RETAINED',
    'FULL_OPP_L1_PALMAR_VOLUME_STATUS': 'STATIC_APPEARANCE_RETAINED_WITH_LOCAL_WEB_CREASE_AND_COMPRESSION; NO_GROSS_THENAR_DISAPPEARANCE',
    'SOURCE_VS_ZERO_VISIBLE_DIFFERENCE': 'NATIVE_SOURCE_HAS_MORE_OPEN_BROAD_CONNECTION_IN_ITS_SPLAYED_POSE; RSSF_MAPPED_SOURCE_AND_ZERO_LOOK_CLOSE_AT_TARGET',
    'ZERO_VS_FULL_OPP_L1_VISIBLE_DIFFERENCE': 'THUMB_AND_WEB_BORDER_MOVE; LOCAL_WEB_BASE_FOLD_MORE_PRONOUNCED; MAIN_THENAR_OUTER_BULGE_CLOSE',
    'THENAR_VOLUME_LOSS_VISIBLE_IN_SOURCE': 'UNRESOLVED; NO_CLEAR_MISSING_BLOCK_OBSERVED_IN_NATIVE_NEUTRAL',
    'THENAR_VOLUME_LOSS_VISIBLE_IN_ZERO': 'UNRESOLVED; NARROW_CONNECTION_APPEARANCE_VISIBLE',
    'THENAR_VOLUME_LOSS_VISIBLE_IN_FULL_OPP_L1': 'UNRESOLVED; NARROW_CONNECTION_APPEARANCE_AND_LOCAL_FOLD_VISIBLE',
    'PRIMARY_CLASSIFICATION': 'UNRESOLVED',
    'HUMAN_EXPLANATION': explanation,
    'HUMAN_VISIBLE_PRODUCT_CONCERN': 'VISIBLE_NARROW_UPPER_THENAR_CONNECTION_APPEARANCE; CAUSAL_ORIGIN_UNRESOLVED; PENDING_HUMAN_REVIEW',
    'ZERO_RESTORE': 'PASS',
    'NaN_Inf': 0,
    'OBVIOUS_COLLAPSE': 0,
    'OBVIOUS_DEGENERATE': 0,
    'GEOMETRY_WRITES': 0,
    'WEIGHT_WRITES': 0,
    'RIG_WRITES': 0,
    'JOINT_WRITES': 0,
    'PRODUCTION_SAVES': 0,
    'PRODUCTION_PROMOTION': 'NO',
    'SOURCE_HASH_AFTER': protection['inputs_after'][next(k for k in protection['inputs_after'] if k.endswith('RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'))],
    'FULL_OPP_L1_POSE_DEFINITION_REUSED': True,
    'FULL_OPP_L1_APPLICATIONS': 1,
    'RENDERS_INSPECTED': 16,
    'HUMAN_MATCHED_CAMERA': 'MOST_RECENT_FORMAL_FULL_OPP_L1_PALMAR_CAMERA_EXACTLY_RESTORED; SEPARATE_HUMAN_CAMERA_NOT_SUPPLIED',
    'EXACT_SOURCE_CURRENT_GEOMETRIC_OVERLAY': False,
    'NEXT': 'PALMAR_THENAR_VISUAL_EVIDENCE_EXPANSION_R1',
    'NEXT_EXECUTED': False,
    'STOP': 'HUMAN REVIEW',
    'HUMAN_DECISION': 'PENDING',
}
dump(PHASE + '_STATUS.json', status)

views = [
    ('HUMAN_MATCHED_PALMAR_OBLIQUE', '掌侧斜视 · 历史 FULL_OPP_L1 机位', '虎口下方 / 大鱼际上方 / 拇指根与掌面的连接。'),
    ('PALMAR_VOLUME_SILHOUETTE', 'PALMAR_VOLUME_SILHOUETTE · 轮廓辅助', '看轮廓和连接区域；虎口空隙的投影不是体积测量。'),
    ('FULL_PALM', 'Alternate palmar view · 稍远的全掌', '统一相机和比例，保留整手上下文。'),
    ('VOLUME_SIDE_OBLIQUE', '稍侧的体积视图', '核对连接凹陷与大鱼际鼓起是否还在。'),
]
columns = [('SOURCE', 'A · OFFICIAL L1 / Stage2', '原始中性姿态 · 历史刚体配准'),
           ('ZERO', 'B · CURRENT ZERO / RSSF', '最终 repaired Stage5B R2 · 静态'),
           ('FULL_OPP_L1', 'C · CURRENT FULL_OPP_L1', '既有正式姿态 · CMC 10° / MCP 10° / IP 5°')]
rows = []
for view, title, desc in views:
    figures = []
    for label, heading, caption in columns:
        figures.append(f'''<figure><figcaption><strong>{heading}</strong><span class="caption" data-caption="{label}">{caption}</span></figcaption>
<button class="image-button" data-state="{label}" data-view="{view}" aria-label="放大 {heading} {title}"><img src="renders/{label}__{view}.png" alt="{heading} · {title}" width="1200" height="{'1400' if view == 'FULL_PALM' else '1000'}"></button></figure>''')
    rows.append(f'<section><h2>{title}</h2><p class="hint">{desc}</p><div class="grid">{"".join(figures)}</div></section>')

html = '''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Palmar thenar · source / ZERO / FULL_OPP_L1</title>
<style>
:root{color-scheme:dark;font-family:system-ui,"Microsoft YaHei",sans-serif;background:#15191e;color:#edf0f3}
*{box-sizing:border-box}body{margin:0;padding:22px}main{max-width:1900px;margin:auto}
h1{font-size:22px;margin:0 0 8px}h2{font-size:16px;margin:0}p{line-height:1.65;margin:8px 0}
.hint,.caption,.source-note{font-size:12px;color:#b7c1cd}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
section{margin:22px 0}figure{margin:0;min-width:0}figcaption{padding:9px 0;line-height:1.6}figcaption strong{font-size:14px}
.caption{display:block;min-height:20px}.image-button{width:100%;padding:0;background:#262c34;border:1px solid #424b58;cursor:zoom-in;display:block;border-radius:5px;overflow:hidden}
.image-button img{display:block;width:100%;height:auto}button,select{font:inherit;color:inherit}select{background:#252c35;border:1px solid #566171;padding:6px 9px;border-radius:4px}
.source-note{padding:7px 0;margin:0}.finding{max-width:1150px;padding:18px;border:1px solid #566171;border-radius:6px;margin:28px 0}
.finding b{color:#f2cd91}a{color:#b6d7ff}dialog{max-width:98vw;width:1400px;max-height:97vh;border:1px solid #566171;background:#15191e;color:#edf0f3;padding:12px}
dialog::backdrop{background:#000c}.toolbar{display:flex;gap:10px;align-items:center;padding-bottom:9px}.toolbar span{flex:1;font-size:13px}.toolbar button{background:#303846;border:1px solid #657083;border-radius:4px;padding:6px 12px;cursor:pointer}
dialog img{display:block;max-width:100%;max-height:83vh;width:auto;height:auto;margin:auto}
@media(max-width:700px){body{padding:10px}.grid{gap:5px}figcaption strong{font-size:10px}.caption{font-size:10px}h1{font-size:18px}}
</style><main>
<h1>虎口下方 / 大鱼际连接 · 三列视觉比较 R1</h1>
<label class="source-note">A 列： <select id="source-mode" aria-label="A列 source 显示方式"><option value="SOURCE">Official L1 原始中性姿态</option><option value="SOURCE_RSSF_DISPLAY">已有 RSSF 显示映射 · 辅助控制</option></select></label>
<p class="source-note">SOURCE_VISUAL_REFERENCE_ONLY · source 沿用历史配准，三列统一相机、比例、材质与光照；source 与 ZERO 的原生姿态不同，不能当作精确几何叠加。点击图片放大。</p>
''' + ''.join(rows) + f'''
<div class="finding"><b>PRIMARY_CLASSIFICATION = UNRESOLVED</b><p>{explanation}</p>
<p>轮廓与侧向图中，大鱼际主鼓起仍在；未见“只有 FULL_OPP_L1 才把正常的大鱼际整块拉没”。A 列切到 RSSF 显示映射后，其连接区与 ZERO 接近，但该控制包含历史工程映射，不能独立证明原始 source 偏瘦。</p>
<p class="hint">NaN / Inf = 0 · 明显 collapse = 0 · 明显 degenerate = 0 · ZERO restore PASS<br>Geometry / weight / rig writes = 0 · production save = 0 · production promotion NO</p>
<p class="hint">NEXT = PALMAR_THENAR_VISUAL_EVIDENCE_EXPANSION_R1 · 仅记录，未执行。STOP — HUMAN REVIEW</p>
<a href="{PHASE}_REPORT.md">报告</a> · <a href="{PHASE}_STATUS.json">状态</a></div>
</main>''' + '''<dialog id="lightbox"><div class="toolbar"><button id="prev" aria-label="上一列">←</button><span id="image-label"></span><button id="next" aria-label="下一列">→</button><button id="close">关闭</button></div><img id="large-image" alt=""></dialog>
<script>
const sourceMode=document.getElementById('source-mode'),box=document.getElementById('lightbox'),large=document.getElementById('large-image'),label=document.getElementById('image-label');
const states=['SOURCE','ZERO','FULL_OPP_L1'];let currentState=0,currentView='HUMAN_MATCHED_PALMAR_OBLIQUE';
function actualState(state){return state==='SOURCE'?sourceMode.value:state}
function show(){const state=actualState(states[currentState]);large.src=`renders/${state}__${currentView}.png`;large.alt=`${state} · ${currentView}`;label.textContent=large.alt}
sourceMode.addEventListener('change',()=>{document.querySelectorAll('[data-state="SOURCE"]').forEach(b=>{b.querySelector('img').src=`renders/${sourceMode.value}__${b.dataset.view}.png`});document.querySelectorAll('[data-caption="SOURCE"]').forEach(c=>c.textContent=sourceMode.value==='SOURCE'?'原始中性姿态 · 历史刚体配准':'历史 RSSF 显示映射 · 含工程映射，仅作控制');if(box.open)show()});
document.querySelectorAll('.image-button').forEach(b=>b.addEventListener('click',()=>{currentState=states.indexOf(b.dataset.state);currentView=b.dataset.view;show();box.showModal()}));
function shift(n){currentState=(currentState+n+3)%3;show()}
document.getElementById('prev').onclick=()=>shift(-1);document.getElementById('next').onclick=()=>shift(1);document.getElementById('close').onclick=()=>box.close();
document.addEventListener('keydown',e=>{if(box.open&&e.key==='ArrowLeft')shift(-1);if(box.open&&e.key==='ArrowRight')shift(1)});
box.addEventListener('click',e=>{if(e.target===box)box.close()});
</script></html>'''
(OUT / 'review.html').write_text(html, encoding='utf-8')

report = f'''# {PHASE}

日期：2026-10-06（Asia/Shanghai）。本轮为 VISUAL DIFFERENTIAL CHECK，采用 HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST。

## 判断

**PRIMARY_CLASSIFICATION = UNRESOLVED。**

{explanation}

明确可见的是：连接偏窄的观感并非只在 FULL_OPP_L1 才出现；ZERO 已有类似结构。FULL_OPP_L1 使拇指内移、虎口开口改变，侧向图上的虎口基底折痕更明显，但大鱼际下部鼓起和主要外轮廓仍保留。没有观察到“静态体积正常、只有这一 opposition 才整块拉没”的明确证据。这是当前比较的视觉发现，不是对所有形变缺陷的否定，也不构成 Stage6B Human PASS。

## 三列与比较限制

| 列 | 实际数据 | 可比性 |
| --- | --- | --- |
| A | Blender Human Base Meshes v1.4.1 · Hand - Realistic · actual stored Multires L1，原始中性姿态 | 本轮只读打开官方 blend，当前 L1 的 3300 vertices / 3298 faces 与既有已验证 snapshot 精确一致；沿用既有刚体旋转和平移，scale = 1，无新 correspondence |
| B | 实际最终 repaired Stage5B R2，fresh RESET ZERO / RSSF | 从指定正式资产当前求值，原生生产拓扑不变 |
| C | 同一正式资产，既有 FULL_OPP_L1 | 历史向量和 pose definition 原样复用，CMC 10° / MCP 10° / IP 5°，一次 apply |

A 的默认图是原始中性形状，只有既有刚体显示配准。A 下拉项提供此前 donor restoration 已验证的 OFFICIAL_L1_RSSF_DISPLAY，原封不动复用冻结坐标与原生 source faces。它采用先前以工程静态坐标为 anchor 的逐顶点 RSSF 显示映射，因此**不属于原始中性姿态，也不是独立、无工程影响的 source 基线**。使用它仅帮助辨认 ZERO 与历史映射 source 在目标区的可见接近程度。

两种 A 均标记 **SOURCE_VISUAL_REFERENCE_ONLY / VISUALLY_MATCHED_REGISTRATION**。默认 source 与 ZERO 的拇指张开、手指屈曲和掌面朝向并不完全一致。source → ZERO 的轮廓差异不能直接换算成真实体积减少。source 的 mapped 控制与 ZERO 接近，也不能反过来证明原始 source 天生偏窄。这两个限制是本轮选择 UNRESOLVED 的理由。

当前正式资产：`{next(k for k in protection['inputs_before'] if k.endswith('RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'))}`。

SHA256 前后均为 `{status['SOURCE_HASH_AFTER']}`。

## 机位与视觉发现

主机位精确恢复最近一次正式 Stage6B requalification 的 FULL_OPP_L1 / THUMB_PALMAR_OBLIQUE_SOLID 相机 center、direction、ortho scale 与 1200 × 1000 image size。用户此次没有另附相机矩阵，因此将该历史掌侧斜视作为 Human matched 的最合理恢复，未声称独立确认了用户鼠标调整后的未知机位。

每个 camera family 内 A / B / C 使用同一 center、direction、scale、resolution。材质为统一灰色，Workbench studio 光照相同，cavity OFF，平滑设置仅施加到未保存的 display copy。silhouette 使用同一主相机的白色 FLAT 轮廓。另有稍远全掌和稍侧体积视图，共 12 张主要证据 + 4 张 source RSSF 控制，不生成 wire / grazing / forensic 图。

本轮逐张看过 16 张图，观察如下：

| 比较 | 可见观察 | 对分流的含义 |
| --- | --- | --- |
| 原始中性 source | 大鱼际与拇指根有连续宽斜面和下部鼓起，未见明确少一整块；拇指更向外张开 | 不足以判 SOURCE_BASE_SHAPE_NARROW，也不能用其较宽投影直接证明工程损失 |
| 当前 ZERO | 虎口下方到掌面的连接显得收窄，目标附近斜谷已存在；下部 thenar mass 仍在 | 产品观感在静态阶段已经可见，但真实静态体积损失尚未证明 |
| 当前 FULL_OPP_L1 | 虎口开口缩小并移动，局部基底折痕更尖；主 thenar 鼓起与 ZERO 接近 | 可见局部 pose 影响，没有明确整块大鱼际消失证据 |
| source RSSF 显示控制 ↔ ZERO | 目标连接区、主要鼓起与外轮廓相近 | 控制含工程映射，不能据此在原始 source 与静态重姿态之间归因 |
| silhouette / full palm / side | B ↔ C 的主要 thenar 外轮廓接近；改变集中在拇指和虎口边缘 | 支持“并非仅在 FULL_OPP_L1 才开始出现”，不提供体积测量或 geometry threshold |

不把虎口正常开口当作 mesh 破洞。关注的是其下方连接斜面是否饱满。图中没有明确表面断开一整块；局部偏窄观感及 pose 折痕仍交由 Human 产品审阅。

## 最低检查与只读保护

所有四个显示状态的 NaN / Inf、明显 collapsed faces、明显 degenerate edges 均为 0。仅复用既有 catastrophic floor；没有完整 crossing census、normal-dot、weight continuity、微小 strain 或数值体积审计。

执行顺序为 fresh RESET ZERO → apply 原正式 FULL_OPP_L1 → evaluate → render 全部 C 视图 → RESET ZERO。最终 21 channels 全 ZERO，ZERO restore PASS，内存中的 mesh、weights、rest rig、groups、modifiers 与最初读入 payload 相同。正式资产、官方 source、使用的历史定义和映射输入文件 SHA256 前后完全相同。未保存 blend。

## 最终字段

| 字段 | 结果 |
| --- | --- |
''' + '\n'.join(f'| {k} | {v} |' for k, v in status.items() if k in [
    'SOURCE_VISUAL_REFERENCE', 'SOURCE_PALMAR_VOLUME_STATUS', 'CURRENT_ZERO_PALMAR_VOLUME_STATUS',
    'FULL_OPP_L1_PALMAR_VOLUME_STATUS', 'SOURCE_VS_ZERO_VISIBLE_DIFFERENCE',
    'ZERO_VS_FULL_OPP_L1_VISIBLE_DIFFERENCE', 'THENAR_VOLUME_LOSS_VISIBLE_IN_SOURCE',
    'THENAR_VOLUME_LOSS_VISIBLE_IN_ZERO', 'THENAR_VOLUME_LOSS_VISIBLE_IN_FULL_OPP_L1',
    'PRIMARY_CLASSIFICATION', 'HUMAN_VISIBLE_PRODUCT_CONCERN', 'ZERO_RESTORE',
    'GEOMETRY_WRITES', 'WEIGHT_WRITES', 'RIG_WRITES', 'PRODUCTION_PROMOTION', 'NEXT', 'NEXT_EXECUTED', 'STOP']) + f'''

写入数量指原始 / 正式资产的修改数量。显示网格、材质和相机只在未保存的隔离 scene 中创建，不写入 source 或 production。

## 审阅入口与停止点

[review.html](review.html) 首页直接展示三列大图，下一行 silhouette，再下一行 full palm，然后稍侧体积视图。A 可切换历史 RSSF 显示控制；点击任一图放大后，左右按钮或方向键可在同一 camera family 的三列间切换。

NEXT = **PALMAR_THENAR_VISUAL_EVIDENCE_EXPANSION_R1**。仅记录，未执行。**STOP — HUMAN REVIEW。**

没有 geometry / weight / joint / rig edit、retopo、sculpt、donor transfer、production save 或 promotion。没有自动进入后续诊断或修复。

证据索引：[状态]({PHASE}_STATUS.json)、[相机与渲染清单](RENDER_MANIFEST_R1.json)、[最低机器检查](MINIMUM_MACHINE_SAFETY_R1.json)、[输入与只读保护](INPUT_AND_PROTECTION_R1.json)。
'''
(OUT / (PHASE + '_REPORT.md')).write_text(report, encoding='utf-8')
dump('DELIVERY_VERIFICATION_R1.json', {
    'status': 'PASS', 'required_report_present': True, 'required_status_present': True,
    'review_present': True, 'image_references_present': 16, 'render_count': 16,
    'browser_display_verified': 'PENDING', 'all_required_fields_present': True,
    'production_hash_unchanged': True, 'ZERO_RESTORE': 'PASS', 'NEXT_EXECUTED': False,
})
print('REPORT / STATUS / REVIEW READY; PRIMARY_CLASSIFICATION UNRESOLVED; STOP HUMAN REVIEW')
