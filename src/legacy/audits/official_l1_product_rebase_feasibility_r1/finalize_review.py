import json,hashlib,ast
from pathlib import Path
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PHASE='OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
G=read('STATIC_BIND_AND_REBASE_R1.json');M=read('REPRESENTATIVE_MOTION_EVIDENCE_R1.json');RM=read('MOTION_RENDER_MANIFEST_R1.json')
for key in ['source','rig_source','weight_donor','candidate']:
    assert sha(ROOT/G[key]['path'])==G[key]['sha256'],key
assert M['candidate_sha256']==G['candidate']['sha256'] and M['count']==10
assert M['automatic_status']=='PASS' and M['ZERO_RESTORE']=='PASS'
bad=['INDEX_MCP_45','CMC_OPP_30','FULL_OPP_L2','FULL_OPP_L3']
case_status={c['case_id']:('FAIL_VISIBLE_UPPER_FIRST_WEB_HARD_FOLD' if c['case_id'] in bad else 'PASS_CODEX_PRELIMINARY') for c in M['cases']}
animations=[]
for row in RM['animations']:
    frames=[]
    for f in row['frames']:
        im=Image.open(OUT/f['path']).convert('RGB');im.thumbnail((720,660));frames.append(im)
    sequence=frames+frames[-2:0:-1]
    target=f"motion_previews/{row['case_id']}.gif";(OUT/'motion_previews').mkdir(exist_ok=True)
    sequence[0].save(OUT/target,save_all=True,append_images=sequence[1:],duration=[400,150,150,150,150,700,150,150,150,150],loop=0,optimize=False)
    animations.append({'case_id':row['case_id'],'path':target,'view':row['view'],'source_frames':row['frames'],'display_only_compilation':True})
dump('VISIBLE_MOTION_PREVIEW_MANIFEST_R1.json',{'animations':animations,'new_test_cases':0,'new_axis_vector_search':False})
status={
 'PHASE':PHASE,'ASSET_CLASS':'DESIGN_ONLY / NOT_PRODUCTION','HUMAN_APPROVAL':'PENDING','DO_NOT_PROMOTE':True,
 'SOURCE_MESH':'Blender Human Base Meshes v1.4.1 / Hand  - Realistic / Official Multires L1',
 'SOURCE_VERTEX_FACE_COUNT':{'vertices':3300,'edges':6596,'faces':3298},
 'RIG_SOURCE':G['rig_source'],'BONE_COUNT':21,
 'ARMATURE_FIT_STATUS':'COMPLETED_SOURCE_SHAPE_PRESERVED_DYNAMIC_FIRST_WEB_BLOCKER',
 'WEIGHT_TRANSFER_METHOD':G['weight_transfer_method'],'WEIGHT_DONOR_POSITIVE_HASH':G['weight_donor_positive_payload_hash'],
 'LOCAL_WEIGHT_TUNING_VERTEX_COUNT':173,'LOCAL_WEIGHT_TUNING_ATTEMPTS':1,
 'ZERO_VISUAL_STATUS':'PASS_CODEX_PRELIMINARY',
 'FOUR_FINGER_FLEX_STATUS':'FAIL_INDEX_FIRST_WEB_HARD_FOLD; MIDDLE_RING_LITTLE_PASS_CODEX_PRELIMINARY',
 'THUMB_FLEX_STATUS':'PASS_CODEX_PRELIMINARY',
 'CMC_OPP_30_STATUS':case_status['CMC_OPP_30'],'FULL_OPP_L1_STATUS':case_status['FULL_OPP_L1'],
 'FULL_OPP_L2_STATUS':case_status['FULL_OPP_L2'],'FULL_OPP_L3_STATUS':case_status['FULL_OPP_L3'],
 'VISIBLE_PRODUCT_BLOCKER_COUNT':1,'VISIBLE_BLOCKER_COUNT_SEMANTICS':'One defect family repeated in four authorized cases',
 'VISIBLE_AFFECTED_CASE_COUNT':4,'VISIBLE_AFFECTED_CASES':bad,
 'MINIMUM_VISIBLE_BLOCKER':'Upper first-web at index-root attachment pinches into a pointed shelf / flap-like hard fold. Clear at CMC_OPP_30; repeated at FULL_OPP_L2/L3 and INDEX_MCP_45.',
 'MACHINE_SAFETY':'PASS_MINIMUM_NUMERICAL_AND_GROSS_VISIBLE_SCREEN',
 'MACHINE_SAFETY_DETAILS':{'NaN_Inf':0,'collapsed_faces':0,'degenerate_edges':0,'gross_severe_stretch_edges':0,
   'gross_visible_tearing':0,'obvious_gross_visible_penetration':0,'visible_screen_scope':'Ordinary neutral renders only; no hidden intersection census',
   'ZERO_restore':'PASS','ZERO_restore_max_mm':max(r['post_zero_error_mm'] for r in M['restores'])},
 'SOURCE_SHAPE_PRESERVED':'YES','SOURCE_NATIVE_POSITIONS_FACES_UV_MATERIALS':'PRESERVED',
 'SOURCE_VS_BOUND_ZERO_FLOAT_ERROR_MM':G['zero_evaluated_source_error_mm'],
 'RECOMMENDED_PRODUCT_MESH':'NOT_CONFIRMED_BY_THIS_TRIAL',
 'CURRENT_ENGINEERING_MESH_ROLE_FOR_NEW_ROUTE':'LEGACY_REFERENCE_ONLY',
 'PRODUCTION_MASTER_REPLACED':False,'PRODUCTION_PROMOTION':'NO','VERDICT':'FAIL_PRODUCT_REBASE_FEASIBILITY',
 'VERDICT_SCOPE':'This fitted rig + surface weight transfer + one bounded local smooth trial; does not prove Official L1 cannot work.',
 'CASE_VISIBLE_STATUS':case_status,'source':G['source'],'weight_donor':G['weight_donor'],'candidate':G['candidate'],
 'SAVED_CANDIDATE_POSE':'ZERO','TIP_HELPERS_NON_DEFORM':True,'STATIC_MATCHED_VIEW_COUNT':6,'REPRESENTATIVE_CASE_COUNT':10,
 'STOP':'STOP — HUMAN REVIEW','AUTOMATIC_FOLLOWUP':False}
dump(PHASE+'_STATUS.json',status)
dump('FINAL_VISIBLE_PRODUCT_SCREEN_R1.json',{'reviewer':'Codex preliminary ordinary visible screen','human_approval':'PENDING',
 'static_views':['PALMAR_FULL','DORSAL_FULL','RADIAL_SIDE','ULNAR_SIDE','THUMB_WEB_OBLIQUE','THENAR_CLOSE'],
 'static_status':'PASS_CODEX_PRELIMINARY','case_status':case_status,'blocker_count':1,'affected_cases':bad,
 'minimum_blocker':status['MINIMUM_VISIBLE_BLOCKER'],'gross_visible_tearing':0,'obvious_gross_visible_penetration':0,
 'accepted_features':'Ordinary creases, soft compression, and minor low-poly faceting in passing cases',
 'excluded_inference':'Root cause between spatial fit and transferred weights is not isolated; no anatomy/axis/topology research follows.'})
fields=['SOURCE_MESH','SOURCE_VERTEX_FACE_COUNT','RIG_SOURCE','BONE_COUNT','ARMATURE_FIT_STATUS','WEIGHT_TRANSFER_METHOD',
 'LOCAL_WEIGHT_TUNING_VERTEX_COUNT','ZERO_VISUAL_STATUS','FOUR_FINGER_FLEX_STATUS','THUMB_FLEX_STATUS','CMC_OPP_30_STATUS',
 'FULL_OPP_L1_STATUS','FULL_OPP_L2_STATUS','FULL_OPP_L3_STATUS','VISIBLE_PRODUCT_BLOCKER_COUNT','MACHINE_SAFETY',
 'SOURCE_SHAPE_PRESERVED','PRODUCTION_PROMOTION','VERDICT']
table='\n'.join('| '+k+' | '+json.dumps(status[k],ensure_ascii=False).replace('|','/')+' |' for k in fields)
report=f'''# {PHASE}

**FAIL_PRODUCT_REBASE_FEASIBILITY — STOP — HUMAN REVIEW**

Official L1 的正常静态手型保留，但本次拟合与权重转移没有得到全部自然的代表动作。最小肉眼 blocker 是虎口上缘、连接食指根处的尖折 / 片状硬台阶，同一问题出现在 INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L2 和 FULL_OPP_L3。一次局部平滑后仍存在，故停止本轮调整。此结论限定于本次 candidate，不能推断 Official L1 路线本身不可行。

| 最终字段 | 结果 |
| --- | --- |
{table}

## 候选与边界

候选：[RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend](./RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend)，SHA256 `{G['candidate']['sha256']}`。保存姿态为 ZERO。NOT_PRODUCTION / HUMAN_APPROVAL_PENDING / DO_NOT_PROMOTE。

产品 mesh 直接来自 Official donor 实际 Multires L1 求值，V3300 / E6596 / F3298，原始局部坐标和面序列精确保留，UV 与材质来自同一 source 求值。只做整体刚性显示配准；没有将 engineering palm、旧 patch 或 topology 复制回 source，也没有重拓扑。source 的 thenar 主体、虎口开口、掌宽和背侧表面在六组静态同机位对比中保持原样。

21 骨骼的名字、父子层级、连接关系、16 deform / 5 non-deform TIP 结构来自 corrected rig lineage。允许的空间适配使用已有表面对应关系的局部仿射拟合映射 head / tail，并映射 roll 方向；局部 X 屈曲和 corrected thumb chain 的动作语义继续复用。连接骨骼共用端点。空间拟合完成不等于全部动作验收通过。

R2 donor 正权重 hash `{G['weight_donor_positive_payload_hash']}` 经 nearest surface + face barycentric interpolation 转移，在临时配准 donor proxy 上查找，归一化到 16 组。该 proxy 不进入产品 mesh。历史对应关系覆盖 3341 个工程顶点，其余 75 个只在临时 proxy 中作邻域空间插值。新 topology 使用新权重 payload，未强求旧 hash。

仅进行一次局部权重平滑，173 个 Official L1 顶点参与，只改 WRIST / THUMB_CMC / MCP / IP 四列，其他权重列、源几何、UV、骨架 rest 和 modifier 不变。保留初始转移候选及初始动作证据。没有继续扩大修复范围。

## 可见结果与最低检查

六个静态对比通过 Codex 初步观察，Human 仍待评审。MIDDLE/RING/LITTLE MCP45、THUMB MCP/IP45、FULL_OPP_L1 的正常 crease、软压缩和轻微分面可接受。INDEX MCP45 的根部附近存在同类虎口尖折；CMC30 最明显，L2 与 L3 重复，thenar 主体仍保留，没有整块缺失或粗大撕裂。

严格只跑授权的 10 个代表 case，复用 Stage6A -45° local X 与 Stage6B 原 opposition vector 和 L1/L2/L3 定义。每个 case 有四个静态视角和六帧 ZERO→该 case 的 quaternion slerp 循环预览；预览中间帧用于人眼观看，不扩展资格矩阵。最终展示统一采用普通灰色 studio shading、相同冻结相机和无 cast shadow 投影，避免投影斑块被误认作表面凹陷，没有删面或藏面。

10/10 的 NaN/Inf、collapsed face、degenerate edge、gross severe stretch 检查为零；每次动作后 21 骨骼恢复 ZERO，最大恢复误差 0 mm。普通图像观察未见粗大 tearing / penetration。这些最低检查 PASS 不能消除尖折产品 blocker，也不表示完成了隐藏交叉检查。

原始 source 与绑定后的 ZERO 世界求值最大浮点差为 {G['zero_evaluated_source_error_mm']:.12f} mm（约 0.482 微米），原生局部几何精确相同。ZERO restore 以当前绑定 ZERO 为基准，误差为零，两者不是同一比较。

未进行 hidden crossing、normal-dot、R3、true-cap、逐点 anatomy proof 或新动作轴/vector 搜索；没有替换 master、镜像左手、retarget 或 Web export。正式 Stage5B、Official donor、corrected rig 均经 SHA256 复核保持原样。

## Human review

[打开 review.html](./review.html)。四部分：source vs ZERO 六视图、四指 MCP45、thumb flexion、opposition。Q1/Q2/Q3 = ACCEPT/REJECT，Q4 = NO/YES；不预填，人类结果可下载本地 JSON。此页面只是独立设计候选的评审材料，没有生产推广操作。

原始证据：[静态绑定](./STATIC_BIND_AND_REBASE_R1.json)、[10 个动作与恢复](./REPRESENTATIVE_MOTION_EVIDENCE_R1.json)、[局部权重调整](./LOCAL_VISIBLE_WEIGHT_TUNING_R1.json)、[可见结论](./FINAL_VISIBLE_PRODUCT_SCREEN_R1.json)、[状态](./{PHASE}_STATUS.json)。

**PRODUCTION_PROMOTION = NO. STOP — HUMAN REVIEW.**
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
config={'static':['PALMAR_FULL','DORSAL_FULL','RADIAL_SIDE','ULNAR_SIDE','THUMB_WEB_OBLIQUE','THENAR_CLOSE'],
 'groups':[['INDEX_MCP_45','MIDDLE_MCP_45','RING_MCP_45','LITTLE_MCP_45'],['THUMB_MCP_45','THUMB_IP_45'],['CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3']],
 'cases':{c['case_id']:{'views':c['views'],'status':case_status[c['case_id']],'motion_view':next(a['view'] for a in animations if a['case_id']==c['case_id'])} for c in M['cases']},
 'candidate_sha256':G['candidate']['sha256']}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Official L1 产品 rebase · Human review</title>
<style>*{box-sizing:border-box}body{margin:0;background:#12181e;color:#e9eff4;font:15px/1.5 system-ui,"Microsoft YaHei",sans-serif}header,main{max-width:1440px;margin:auto;padding:20px 28px}header{padding-bottom:12px}h1{font-size:24px;margin:0 0 8px}.tag{color:#ffbd91}p{margin:6px 0}.muted{color:#acbac6;font-size:13px}nav{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 0}button,select{font:inherit;padding:9px 13px;background:#24313d;color:#e9eff4;border:1px solid #526374;border-radius:7px;cursor:pointer}button[aria-pressed=true]{background:#367897;border-color:#87c7df}.tools{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0;background:#1d2731;border-radius:8px;overflow:hidden}figcaption{padding:9px 14px}img{display:block;width:100%;object-fit:contain;background:#737c87}.pair img{max-height:66vh}.case-note{margin:10px 0 15px}.fail{color:#ffbd91}a{color:#9ed9ef}details{margin-top:20px;padding:15px;background:#1d2731;border-radius:8px}summary{cursor:pointer}fieldset{border:1px solid #526374;margin:14px 0;padding:13px}label{margin-right:18px}input{margin-right:7px}.foot{padding-top:16px}.error{color:#ff9999}@media(max-width:760px){header,main{padding:16px}.pair{grid-template-columns:1fr}.pair img{max-height:60vh}h1{font-size:20px}}</style>
<header><h1>Official L1 产品 rebase · Human review</h1><p class="tag">FAIL_PRODUCT_REBASE_FEASIBILITY · NOT_PRODUCTION · HUMAN_APPROVAL_PENDING</p><p>静态源手型保留。当前 blocker：虎口上缘在食指根连接处出现尖折 / 片状硬折，重复于 4 个动作；一次局部权重平滑后仍存在。</p><p class="muted">3300 顶点 / 3298 面 · 21 骨骼 · 173 个顶点局部权重调整 · 最低机器检查与 ZERO 恢复 PASS · PRODUCTION_PROMOTION = NO</p>
<nav><button data-part="0" aria-pressed="true">1 · 静态源手型</button><button data-part="1" aria-pressed="false">2 · 四指 MCP45</button><button data-part="2" aria-pressed="false">3 · Thumb flexion</button><button data-part="3" aria-pressed="false">4 · Opposition</button></nav></header>
<main><div class="tools"><label id="case-label">动作 <select aria-label="动作" id="case"></select></label><label>视图 <select aria-label="视图" id="view"></select></label><button id="animate" aria-pressed="false">动作循环</button></div><p id="case-note" class="case-note"></p><div class="pair"><figure><figcaption id="left-title"></figcaption><img id="left" alt=""></figure><figure><figcaption id="right-title"></figcaption><img id="right" alt=""></figure></div><p id="load-error" class="error" role="status"></p>
<details><summary>填写 Human review · 四个问题</summary><form id="human">
<fieldset><legend>Q1 · ZERO 静态手型是否保持原模型正常外形？</legend><label><input type="radio" name="Q1" value="ACCEPT">ACCEPT</label><label><input type="radio" name="Q1" value="REJECT">REJECT</label></fieldset>
<fieldset><legend>Q2 · 四指与 thumb flexion 是否正常？</legend><label><input type="radio" name="Q2" value="ACCEPT">ACCEPT</label><label><input type="radio" name="Q2" value="REJECT">REJECT</label></fieldset>
<fieldset><legend>Q3 · Opposition 是否正常？</legend><label><input type="radio" name="Q3" value="ACCEPT">ACCEPT</label><label><input type="radio" name="Q3" value="REJECT">REJECT</label></fieldset>
<fieldset><legend>Q4 · 是否发现新的明显产品问题？</legend><label><input type="radio" name="Q4" value="NO">NO</label><label><input type="radio" name="Q4" value="YES">YES</label></fieldset>
<button type="button" id="download">下载评审结果 JSON</button><p id="human-note" role="status">尚未填写；结果仅下载到本地。</p></form></details>
<p class="foot"><a href="OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_REPORT.md">报告</a> · <a href="OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1_STATUS.json">完整状态</a> · <a href="RIGHT_HAND_OFFICIAL_L1_PRODUCT_REBASE_CANDIDATE_R1.blend">候选 Blender 文件</a></p><p class="muted">普通灰色、冻结同机位；关闭 cast shadow 投影，无藏面。循环预览是同一授权动作路径的真实蒙皮渲染帧。STOP — HUMAN REVIEW。</p></main>
<script>const cfg=__CONFIG__;let part=0,loop=false;const by=id=>document.getElementById(id),cs=by('case'),vs=by('view');
const names={PALMAR_FULL:'掌侧全景',DORSAL_FULL:'背侧全景',RADIAL_SIDE:'桡侧',ULNAR_SIDE:'尺侧',THUMB_WEB_OBLIQUE:'虎口斜视',THENAR_CLOSE:'Thenar 近景',FINGER_ROOTS_CLOSE:'指根近景'};
function options(el,arr){el.replaceChildren(...arr.map(x=>{const o=document.createElement('option');o.value=x;o.textContent=names[x]||x;return o}));}
function views(){options(vs,part===0?cfg.static:cfg.cases[cs.value].views);loop=false;draw()}
function draw(){const c=cs.value,v=vs.value;by('case-label').hidden=part===0;by('animate').hidden=part===0;by('animate').setAttribute('aria-pressed',String(loop));by('animate').textContent=loop?'返回静态动作':'动作循环';by('load-error').textContent='';
 const lp=part===0?'OFFICIAL_L1__REST':'REBASED__ZERO';by('left').src=`final_renders/${lp}__${v}.png`;by('left-title').textContent=part===0?'OFFICIAL L1 SOURCE · '+names[v]:'REBASED ZERO · '+names[v];by('left').alt=by('left-title').textContent;
 by('right').src=part===0?`final_renders/REBASED__ZERO__${v}.png`:loop?`motion_previews/${c}.gif`:`final_renders/REBASED__${c}__${v}.png`;
 by('right-title').textContent=part===0?'REBASED ZERO · '+names[v]:c+' · '+(loop?'ZERO → 动作 → ZERO':names[v]);by('right').alt=by('right-title').textContent;
 by('case-note').textContent=part===0?'六个同机位静态对比：源手型保持，Codex 初步观察通过；Human 待评审。':cfg.cases[c].status.startsWith('FAIL')?'Codex 初步观察：虎口上缘尖折 / 硬折，产品 gate 未通过。':'Codex 初步观察：可接受的 crease / 软压缩 / 轻微分面；Human 待评审。';by('case-note').className='case-note '+(part&&cfg.cases[c].status.startsWith('FAIL')?'fail':'');}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{part=Number(b.dataset.part);document.querySelectorAll('nav button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));options(cs,part?cfg.groups[part-1]:['ZERO']);views()});cs.onchange=views;vs.onchange=()=>{loop=false;draw()};by('animate').onclick=()=>{loop=!loop;if(loop)vs.value=cfg.cases[cs.value].motion_view;draw()};
for(const id of ['left','right'])by(id).onerror=()=>by('load-error').textContent='图片载入失败，请检查本地 renders 文件。';
by('download').onclick=()=>{const answers=Object.fromEntries(new FormData(by('human')));if(Object.keys(answers).length!==4){by('human-note').textContent='请填写全部四个问题。';return}const data={phase:'OFFICIAL_L1_PRODUCT_REBASE_FEASIBILITY_R1',candidate_sha256:cfg.candidate_sha256,human_answers:answers,production_promotion:'NO',timestamp:new Date().toISOString()};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='OFFICIAL_L1_PRODUCT_REBASE_HUMAN_REVIEW.json';a.click();URL.revokeObjectURL(a.href);by('human-note').textContent='评审结果已下载；没有修改候选或推广 production。'};
options(cs,['ZERO']);views();</script></html>'''
(OUT/'review.html').write_text(html.replace('__CONFIG__',json.dumps(config,ensure_ascii=False)),encoding='utf-8')
for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
for r in RM['renders']:assert (OUT/r['path']).is_file()
dump('FINAL_OUTPUT_INTEGRITY_R1.json',{'input_hashes_unchanged':True,'candidate':G['candidate'],
 'required_fields_present':all(k in status for k in fields),'representative_case_count':10,'final_motion_render_count':len(RM['renders']),
 'motion_preview_count':10,'python_parse':'PASS','production_promotion':'NO','human_review':'PENDING','automatic_followup':False})
print('FINAL_OUTPUTS_READY',status['VERDICT'],flush=True)
