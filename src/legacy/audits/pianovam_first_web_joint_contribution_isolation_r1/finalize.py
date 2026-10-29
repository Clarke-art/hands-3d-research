import json, hashlib
from pathlib import Path
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PHASE='PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selection=read('SELECTED_DEFECT_FRAMES_R1.json')
machine=read('MACHINE_CHECK_R1.json')
assert machine['status']=='PASS'
conditions=['BASELINE','INDEX_ABD_OFF','INDEX_FLEX_OFF','THUMB_CMC_SWING_OFF','THUMB_MCP_FLEX_OFF']
labels={'BASELINE':'BASELINE','INDEX_ABD_OFF':'INDEX ABD OFF','INDEX_FLEX_OFF':'INDEX FLEX OFF','THUMB_CMC_SWING_OFF':'THUMB CMC SWING OFF','THUMB_MCP_FLEX_OFF':'THUMB MCP FLEX OFF'}
notes={
130:{'INDEX_ABD_OFF':('NO_EFFECT','阶梯状长折线仍在；间隙与食指姿态稍变，未见明确减轻。'),
     'INDEX_FLEX_OFF':('NO_EFFECT','尖角和深折线仍在，局部折线略更突出，未改善。'),
     'THUMB_CMC_SWING_OFF':('NO_EFFECT','拇指基部姿态小幅改变，长折线和内陷保留。'),
     'THUMB_MCP_FLEX_OFF':('NO_EFFECT','拇指远段姿态改变，虎口阶梯状凹折保留。')},
76:{'INDEX_ABD_OFF':('SMALL_IMPROVEMENT','掌侧局部折线稍浅，斜视凹角与长折痕仍保留；没有明确消除。'),
    'INDEX_FLEX_OFF':('NO_EFFECT','掌侧和斜视仍有清楚的凹折，未恢复平顺。'),
    'THUMB_CMC_SWING_OFF':('NO_EFFECT','两视角中凹折结构基本保留。'),
    'THUMB_MCP_FLEX_OFF':('NO_EFFECT','拇指远段明显伸开，虎口折痕仍保留。')},
205:{'INDEX_ABD_OFF':('NO_EFFECT','两视角中凹角、折线均保留，缺口未明显减轻。'),
     'INDEX_FLEX_OFF':('NO_EFFECT','尖角及局部折线仍在，未见改善。'),
     'THUMB_CMC_SWING_OFF':('SMALL_IMPROVEMENT','掌侧折线略短、斜视部分凹折减轻；拇指位置变化较大，尖角和凹折仍在。'),
     'THUMB_MCP_FLEX_OFF':('NO_EFFECT','拇指远段改变，根部凹角和折痕仍在。')},
31:{'INDEX_ABD_OFF':('SMALL_IMPROVEMENT','掌侧短折痕稍浅，斜视折线仍在；只属局部小改善。'),
    'INDEX_FLEX_OFF':('NO_EFFECT','原短折痕与凹边仍可见。'),
    'THUMB_CMC_SWING_OFF':('NO_EFFECT','原短折痕与斜视凹边保留。'),
    'THUMB_MCP_FLEX_OFF':('NO_EFFECT','拇指远段姿态改变，局部折线仍在。')},
61:{c:('NO_EFFECT','低缺陷对照仍有浅折线；未观察到明确消除。') for c in conditions[1:]}}
results=[]
for row in selection['frames']:
    f=row['frame']
    for c in conditions:
        effect,note=('BASELINE_REFERENCE',row['visual_note']) if c=='BASELINE' else notes[f][c]
        results.append({'frame':f,'source_frame':row['source_frame'],'role':row['role'],'condition':c,
            'Codex_preliminary_visual_effect':effect,'visual_note':note,
            'authority':'Codex preliminary two-view ordinary-solid visual review; Human pending',
            'views':{v:f'renders/{c}__F{f:03}__{v}.png' for v in ['PALMAR_THENAR_CLOSE','FIRST_WEB_OBLIQUE']}})
gate={'A_clear_contribution':False,'C_clear_contribution':False,
    'run_authorized_by_A_C_visual_contribution':False,
    'reason':'A只有F76/F31局部小改善，C只有F205局部小改善；两者均未达到明显贡献，依用户条件不运行E。'}
dump('JOINT_COMPONENT_AB_RESULTS_R1.json',{'results':results,'combined_gate':gate,
    'effect_categories':['NO_EFFECT','SMALL_IMPROVEMENT','CLEAR_IMPROVEMENT','DEFECT_NEARLY_DISAPPEARS','DEFECT_DISAPPEARS'],
    'single_test_summary':{'INDEX_MCP_ABDUCTION':'SMALL_IMPROVEMENT','INDEX_MCP_FLEXION':'NO_EFFECT','THUMB_CMC_SWING':'SMALL_IMPROVEMENT','THUMB_MCP_FLEXION':'NO_EFFECT'},
    'aggregation_note':'SMALL_IMPROVEMENT 表示部分选帧有小改善，不表示多数帧一致改善或主要触发已定位。',
    'human_review_pending':True,'numerical_defect_score_used':False})
status={'PHASE':PHASE,'SOURCE_ACTION':'PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1','SOURCE_MOTION_CHANGED':'NO',
    'SELECTED_DEFECT_FRAME_COUNT':4,'CONTROL_FRAME_COUNT':1,
    'INDEX_MCP_ABDUCTION_EFFECT':'SMALL_IMPROVEMENT','INDEX_MCP_FLEXION_EFFECT':'NO_EFFECT',
    'THUMB_CMC_SWING_EFFECT':'SMALL_IMPROVEMENT','THUMB_MCP_FLEXION_EFFECT':'NO_EFFECT',
    'COMBINED_TEST_RUN':'NO','COMBINED_EFFECT':'NOT_RUN',
    'PRIMARY_TRIGGER_COMPONENT':'NOT_ISOLATED_TO_TESTED_JOINT_COMPONENTS',
    'COMBINED_MOTION_SKIN_SENSITIVITY':'NOT_ESTABLISHED',
    'RETARGET_COMPONENT_INTERPRETATION_STILL_SUSPECT':'NO_NEW_SEMANTIC_EVIDENCE',
    'FINGERTIP_OBSERVATION':'所选静帧中 INDEX MCP OFF 只改变食指整链姿态、PIP/DIP local bend 保持不变，未重新评估 fast bend，也未开启修复。',
    **{k:'NO' for k in ['BASELINE_MODIFIED','MESH_MODIFIED','WEIGHTS_MODIFIED','RIG_MODIFIED','CORRECTIVE_MODIFIED','DRIVER_MODIFIED','ACTION_MODIFIED','MAPPING_IMPLEMENTATION_MODIFIED','SMOOTHING_MODIFIED']},
    'PRIMARY_CAUSE_CLASSIFICATION':'CAUSE_NOT_ISOLATED',
    'VERDICT':'CAUSE_NOT_ISOLATED_PENDING_HUMAN_REVIEW','STOP':'HUMAN REVIEW',
    'classification_authority':'Codex preliminary; no current Human answers recorded',
    'HUMAN_Q1':None,'HUMAN_Q2':None,'HUMAN_Q3':None,
    'MACHINE_CHECK':'PASS','baseline_sha256':machine['files_after']['production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend'],
    'motion_test_sha256':machine['files_after']['audits/pianovam_retarget_local_axis_mapping_correction_r1/RIGHT_HAND_PIANO_AXIS_CORRECTED_TEST_R1.blend'],
    'same_source_window_seconds':[11.5,18.5],'source_observation_count':421,
    'render_count':50,'no_blend_saved':True,'skin_repair_started':False,'PRODUCTION_PROMOTION':'NO',
    'USAGE_SCOPE':'INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY','LICENSE':'CC BY-NC-SA 4.0'}
dump(PHASE+'_STATUS.json',status)
report='''# PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1

本轮 Codex 初判：**CAUSE_NOT_ISOLATED**；`PRIMARY_TRIGGER_COMPONENT = NOT_ISOLATED_TO_TESTED_JOINT_COMPONENTS`。A–D 均未明显消除缺口，只有少数帧的小改善。不能据此确认 combined-motion skin sensitivity，也没有新的 source anatomical semantics 违规证据。**STOP — HUMAN REVIEW**。

## 绑定与选帧

上一阶段 Human Q1=NO、Q2=YES、Q3=REJECT，`RETARGET_AXIS_MAPPING_PARTIAL_CAUSE=HUMAN_CONFIRMED` 已单独绑定，未改写历史审核记录。冻结右手保持 `HUMAN_APPROVED_FROZEN`。

使用原 axis-corrected test、Action `PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1`、相同 PianoVAM 11.5–18.5 sec / 421 observations。从已有 iteration-2 NEW close sheet 中选 F130（MOST_SEVERE）、F76/F205（SEVERE）、F31（MODERATE），F61 为相对 low-defect control。上述标签是残余 NEW 的相对可见严重度，未照搬旧 retarget 的严重度，也未重做全段 census；F61 仍有浅折痕，未宣称完全正常。

## 临时隔离方法

只在未保存的 Blender 运行时 pose 上测试。前序 mapping_core.py 原样只读导入，iteration=2。A/B 从 Solver.raw 内部已有 source flexion/abduction 读值，重建相同 `frame(direction, palm radial)`，通过原 anatomical rest frame / roll calibration 映射；仅目标 flexion 或 abduction 恢复 0。冻结 RSSF rest 的内建弯曲、张开与 roll 仍保留。没有 Euler X/Z 清零。

C 恢复整个独立映射的 thumb CMC swing/opposition stance 到前序 iteration-2 median CMC→MCP calibrated-neutral。原 CMC 未复制可观测性不足的 axial twist，因此这里将 in-plane swing 和相对 neutral 的 out-of-plane stance 一起恢复；neutral 的绝对 elevation 并非强行设为 0。Thumb MCP/IP local hinge bends 全部保持。D 只把 thumb MCP signed anatomical hinge bend 恢复 0。

每个 OFF 均在原来的 i−1/i/i+1 source observations 上处理目标分量，再使用原 quaternion sign alignment、[.25,.5,.25] 和 normalization。其余骨骼 local quaternion、location、scale、rotation mode 完全复制 saved corrected Action 的实际值。Quaternion 平滑非线性，目标骨的四个 quaternion 系数可同时改变；这不表示额外修改另一解剖分量，也不新增平滑。每帧 saved Action 与原 Solver.smoothed 的 quaternion 数值在 1e−6 内一致。

既有 corrective/driver 始终自然求值，未静音或覆盖；本轮所选 A–D 中自然 corrective 值均为 0。正式 Action 数据不变，运行时只临时分离 Action binding 后写目标 pose；每次测试立即重新绑定并校验 evaluated mesh 精确恢复。未保存任何 .blend。

## 两视角结果

每帧 BASELINE + A/B/C/D，固定同一 Palmar/Thenar Close 和 First-Web Oblique 相机、960×880、光照、clay 材质和显示平滑，共 50 张 matched renders。显示副本只用于未保存的诊断 scene，没有改动资产 mesh。

| Frame | Role | INDEX ABD OFF | INDEX FLEX OFF | THUMB CMC SWING OFF | THUMB MCP FLEX OFF |
| --- | --- | --- | --- | --- | --- |
| 130 | MOST_SEVERE | NO_EFFECT | NO_EFFECT | NO_EFFECT | NO_EFFECT |
| 76 | SEVERE | SMALL_IMPROVEMENT | NO_EFFECT | NO_EFFECT | NO_EFFECT |
| 205 | SEVERE | NO_EFFECT | NO_EFFECT | SMALL_IMPROVEMENT | NO_EFFECT |
| 31 | MODERATE | SMALL_IMPROVEMENT | NO_EFFECT | NO_EFFECT | NO_EFFECT |
| 61 | CONTROL | NO_EFFECT | NO_EFFECT | NO_EFFECT | NO_EFFECT |

F130 的阶梯状深折线在所有 OFF 中保留。A 在 F76/F31 掌側只有稍浅的局部折线，斜视凹角仍在。C 在 F205 缩短部分折线，但尖角和凹折保留；thumb 改变位置不能直接等同缺陷消除。D 主要改变 thumb 远段姿态，first-web 根部缺口仍在。没有 CLEAR_IMPROVEMENT 或接近消失的单项。

**COMBINED_TEST_RUN=NO**：A 与 C 均未表现明显贡献，未满足用户规定的组合测试前提。E 的因果效应未知，不能把 NOT_RUN 当成 NO_EFFECT，不能声称已证实或排除 combined-motion skin sensitivity。不继续拆其他关节、PIP/DIP 或几十种组合。

## 辅助记录与保护检查

JOINT_COMPONENT_VALUES_R1.json 记录每帧每条件原分量、neutralized 分量、实际 baseline/diagnostic local quaternion、三个原邻近观测的 landmark digest 和原 anatomical components。数值只供重现，不做 ROM/医学角度判断。MACHINE_CHECK_R1.json 记录所有未测试 local channels 精确一致、同相机、同 source/frame/mapping/smoothing、同 mesh/Basis/weights/rest/joint layout/roll/hierarchy/corrective/driver、全部 Action payload hash 一致和每次精确 restore。

冻结 baseline SHA256 仍为 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`；motion test SHA256 仍为 `a5190adc13d39318096490f8fd2c9956d0daff457d25753fa3c216eee2027bbd`。原 mapping_core.py 与四个 sample 文件 hash 均前后相同。未运行 R3、true-cap、hidden crossing、normal-dot、Stage6 或 2127 edges。

FINGERTIP_OBSERVATION = 所选静帧中 INDEX MCP OFF 只改变食指整链姿态、PIP/DIP local bend 保持不变，未重新评估 fast bend，也未开启修复。

## Human review（本轮尚未回答）

Q1. 哪一个单独 component OFF 对虎口缺口改善最明显？ INDEX_MCP_ABDUCTION / INDEX_MCP_FLEXION / THUMB_CMC_SWING / THUMB_MCP_FLEXION / NONE

Q2. 是否只有 INDEX_MCP + THUMB_CMC 组合隔离后才明显恢复？ YES / NO / NOT_RUN

Q3. 是否已经足以定位为 combined-motion skin deformation 问题？ YES / NO

review.html 提供 frame/condition 下拉，以及每个条件两个视角与相同帧 BASELINE 对照、Codex preliminary effect。所有本轮 Human 字段保持 null。OFF 仅用于 causal isolation，不表示真实钢琴动作应为零；不推断 index 不应外展或 thumb opposition 错误。

本轮没有进行 weights/mesh/Basis/rig/mapping/source/Action/corrective/driver 修复，没有换 sample、左手或 Web export。停在本轮 Human 审核；下一阶段也未自动启动。
'''
report+='\n## 最终字段\n\n```json\n'+json.dumps(status,ensure_ascii=False,indent=2)+'\n```\n'
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
data={'frames':selection['frames'],'conditions':conditions,'labels':labels,'results':results}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>First-web joint contribution isolation R1</title><style>
*{box-sizing:border-box}body{margin:0;background:#11171d;color:#e5ebf0;font:15px/1.6 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:20px}h1{font-size:23px;margin:0 0 5px}p{margin:6px 0}label{display:inline-block;margin:15px 20px 10px 0}select{font:inherit;background:#26313c;color:white;padding:8px;border:1px solid #536373;border-radius:4px;max-width:100%}.note{padding:12px;background:#1d2933;border-left:3px solid #96adbd;margin:8px 0 18px}.view{margin:12px 0}h2{font-size:17px;margin:8px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0;background:#1b242d}figcaption{padding:6px 10px;font-size:13px}img{display:block;width:100%;height:auto}small{color:#adbbc8}ol{padding-left:22px}a{color:#aed9fb}@media(max-width:700px){main{padding:12px}.pair{gap:5px}h1{font-size:19px}}
</style><main><h1>First-web · Joint contribution isolation R1</h1>
<p>同一 axis-corrected motion · 11.5–18.5 sec · 421 observations · 只定位，不修复</p>
<small>Codex 初判：CAUSE_NOT_ISOLATED。Human 待审核；组合 E 因 A/C 未显示明显贡献而未运行。OFF 仅用于因果隔离，不是正确钢琴动作。</small>
<div><label>Frame <select id="frame" aria-label="Frame"></select></label><label>Condition <select id="condition" aria-label="Condition"></select></label></div>
<p id="meta"></p><div class="note"><strong id="effect"></strong><p id="note"></p></div>
<section class="view"><h2>Palmar / Thenar Close</h2><div class="pair"><figure><figcaption>BASELINE</figcaption><a id="bpLink"><img id="bp" alt="Baseline palmar close"></a></figure><figure><figcaption class="selected"></figcaption><a id="tpLink"><img id="tp" alt="Selected condition palmar close"></a></figure></div></section>
<section class="view"><h2>First-Web Oblique</h2><div class="pair"><figure><figcaption>BASELINE</figcaption><a id="boLink"><img id="bo" alt="Baseline first-web oblique"></a></figure><figure><figcaption class="selected"></figcaption><a id="toLink"><img id="to" alt="Selected condition first-web oblique"></a></figure></div></section>
<p><small>同帧左右相机、光照、材质完全匹配；点击图片可查看原尺寸。保护检查 PASS；baseline、motion test、mesh、weights、rig、corrective、driver、Action 均未修改。</small></p>
<h2>Human review</h2><ol><li>哪一个单独 component OFF 对虎口缺口改善最明显？<br>INDEX_MCP_ABDUCTION / INDEX_MCP_FLEXION / THUMB_CMC_SWING / THUMB_MCP_FLEXION / NONE</li><li>是否只有 INDEX_MCP + THUMB_CMC 组合隔离后才明显恢复？<br>YES / NO / NOT_RUN</li><li>是否已经足以定位为 combined-motion skin deformation 问题？<br>YES / NO</li></ol><p><strong>STOP — HUMAN REVIEW</strong></p>
<p><a href="PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_REPORT.md">Report</a> · <a href="PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1_STATUS.json">Status</a> · <a href="JOINT_COMPONENT_AB_RESULTS_R1.json">逐帧结果</a></p></main>
<script>const data=__DATA__;const frame=document.getElementById('frame'),condition=document.getElementById('condition');
for(const r of data.frames){const o=document.createElement('option');o.value=r.frame;o.textContent=`F${r.frame} · ${r.severity}`;frame.append(o)}
for(const c of data.conditions){const o=document.createElement('option');o.value=c;o.textContent=data.labels[c];condition.append(o)}
function update(){const f=Number(frame.value),c=condition.value,r=data.frames.find(x=>x.frame===f),result=data.results.find(x=>x.frame===f&&x.condition===c);document.getElementById('meta').textContent=`Source frame ${r.source_frame} · ${r.time_sec.toFixed(3)} sec · Clip ${(r.review_time_sec).toFixed(3)} sec · ${r.severity}`;document.getElementById('effect').textContent=`Codex preliminary effect: ${result.Codex_preliminary_visual_effect}`;document.getElementById('note').textContent=result.visual_note;document.querySelectorAll('.selected').forEach(e=>e.textContent=data.labels[c]);
for(const [id,test,view] of [['bp',false,'PALMAR_THENAR_CLOSE'],['tp',true,'PALMAR_THENAR_CLOSE'],['bo',false,'FIRST_WEB_OBLIQUE'],['to',true,'FIRST_WEB_OBLIQUE']]){const path=`renders/${test?c:'BASELINE'}__F${String(f).padStart(3,'0')}__${view}.png`;document.getElementById(id).src=path;document.getElementById(id+'Link').href=path}}
frame.addEventListener('change',update);condition.addEventListener('change',update);update();</script></html>'''
(OUT/'review.html').write_text(html.replace('__DATA__',json.dumps(data,ensure_ascii=False)),encoding='utf-8')
verified=[]
for rec in machine['render_records']:
    p=OUT/rec['path']
    with Image.open(p) as im:assert list(im.size)==rec['camera']['resolution'];im.verify()
    verified.append({'path':rec['path'],'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert len(verified)==50
dump('RENDER_FILE_VERIFICATION_R1.json',{'status':'PASS','render_count':50,'files':verified})
print('FINALIZED',PHASE,'50_RENDERS','CAUSE_NOT_ISOLATED','COMBINED_NOT_RUN')
