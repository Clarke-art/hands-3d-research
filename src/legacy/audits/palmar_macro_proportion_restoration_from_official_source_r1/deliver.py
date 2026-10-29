import json,hashlib
from pathlib import Path
from PIL import Image,ImageFilter,ImageChops,ImageDraw
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PHASE='PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
G=read('ITERATION_02_GEOMETRY.json');P=read('CANDIDATE_SAVE_REOPEN_PROTECTION_R1.json');M=read('MATCHED_RENDER_MANIFEST_R1.json');A=read('MINIMUM_MACHINE_AUTOMATIC_R1.json')
assert M['count']==22 and A['status']=='PASS'
for row in M['renders']:assert (OUT/row['path']).is_file()
iterations=[
 {'id':'01','strength':1.,'result':'REJECTED_NEW_HARD_FOLD','note':'宏观 signed source contour 场；锁住整个 proximal thumb 的突变边界造成虎口底部明显折面。'},
 {'id':'02','strength':1.4,'result':'SELECTED_FOR_FAILED_DESIGN_REVIEW','note':'完整掌面与连续 thumb-root skirt；只恢复 outward contour / palmar fullness 缺额。比其他版本平稳，但仍非正确比例；thumb-root / lower proximal 交界出现角状轮廓。'},
 {'id':'03','strength':2.,'result':'REJECTED_OVERBULGE','note':'加强上 thenar palmar envelope 恢复；侧视掌缘外鼓，局部过渡不自然。'},
 {'id':'04','strength':1.,'result':'REJECTED_ROOT_CONTOUR_NOT_NATURAL','note':'7 mm signed source field + 连续过渡；thumb-root 仍形成角状收缩，未恢复自然掌形。'},
 {'id':'05','strength':1.,'result':'REJECTED_WEB_FLOOR_HARD_CORNER','note':'5 mm 三维 source field + 全局连续 thumb pose registration skirt；连接体积变大，但 first-web 开口过窄、底部形成尖角。'},
]
visual={'authority':'CODEX_PRELIMINARY_VISUAL_SCREEN; HUMAN_FINAL_AUTHORITY','final_images_screened':22,
 'method':'Ordinary neutral solid renders: six matched triple views, dorsal54/palmar16 pairs, and individual first-web close. Static iterations examined without opposition.',
 'PALM_WIDTH_VISUAL_STATUS':'BETTER_BUT_NATURAL_MACRO_PROPORTION_NOT_ESTABLISHED',
 'THENAR_VOLUME_VISUAL_STATUS':'BETTER_BUT_UPPER_THENAR_FULLNESS_STILL_INSUFFICIENT',
 'THUMB_ROOT_CONNECTION_VISUAL_STATUS':'STILL_INSUFFICIENT_WITH_NEW_ANGULAR_TRANSITION',
 'FIRST_WEB_FLOOR_VISUAL_STATUS':'STILL_TOO_THIN_OR_ANGULAR_FOR_NATURAL_SOURCE_LIKE_CONNECTION',
 'DORSAL54_REGRESSION':'NO','PALMAR16_VISUAL_REGRESSION':'NO',
 'palmar16_note':'Matched close sentinel retains its crease; previous hard shelf not visibly reintroduced. Coordinate lock was not required.',
 'NEW_VISIBLE_DEFECT_COUNT':2,'new_visible_defects':['Angular contour / hard diagonal facet at thumb-root to lower proximal transition, visible in first-web and thenar close.','Unnatural outward bulge at upper ulnar palm in the side view.'],
 'obvious_self_intersection_penetration':0,'obvious_tearing':0,'obvious_new_hard_fold':1,'obvious_new_bulge':1,
 'iterations':iterations,'successful_static_iterations':0,'selected_iteration':'02'}
dump('ORDINARY_SOLID_VISUAL_INSPECTION_R1.json',visual)
machine={'MACHINE_SAFETY':'FAIL_VISIBLE_HARD_CONTOUR','automatic_numeric_floor':'PASS','NaN_Inf':0,'collapsed_face':0,'degenerate':0,
 'obvious_self_intersection_penetration':0,'obvious_tearing':0,'obvious_new_hard_fold':1,'obvious_new_bulge':1,'ZERO_RESTORE':'PASS',
 'scope':'Minimal numeric checks plus ordinary-visible screen; visible hard contour prevents overall minimum gate PASS.',
 'hidden_crossing_census':False,'normal_dot_audit':False,'strain_analysis':False,'dynamic_cases_executed':0}
dump('MINIMUM_MACHINE_SAFETY_R1.json',machine)
status={'PHASE':PHASE,'ACCEPTANCE_POLICY':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST',
 'DONOR_SOURCE':'BLENDER_HUMAN_BASE_MESHES_V1_4_1_HAND_REALISTIC_OFFICIAL_MULTIRES_L1',
 'DONOR_FILE':G['source'],'CURRENT_ASSET':G['current'],'CANDIDATE':P['candidate'],
 'RESTORATION_REGION':'Broad palm / palmar thenar / thumb-root / lower first-web floor; continuous wrist and MCP skirts; lower proximal thumb transition included; unrelated finger bodies and forearm excluded',
 'RESTORATION_VERTEX_COUNT':P['RESTORATION_VERTEX_COUNT'],'STATIC_ITERATION_COUNT':5,'SELECTED_ITERATION':'02',
 **{k:visual[k] for k in ['PALM_WIDTH_VISUAL_STATUS','THENAR_VOLUME_VISUAL_STATUS','THUMB_ROOT_CONNECTION_VISUAL_STATUS','FIRST_WEB_FLOOR_VISUAL_STATUS','DORSAL54_REGRESSION','PALMAR16_VISUAL_REGRESSION','NEW_VISIBLE_DEFECT_COUNT']},
 'WEIGHTS_CHANGED':'NO','RIG_CHANGED':'NO','JOINTS_REST_ROLL_CHANGED':'NO','GROUPS_CHANGED':'NO','MODIFIERS_CHANGED':'NO',
 'TOPOLOGY_VERTEX_IDS_UV_MATERIALS_CHANGED':'NO','SHAPE_KEYS_ADDED':'NO','POSE_CORRECTIVE_ADDED':'NO',
 'MACHINE_SAFETY':machine['MACHINE_SAFETY'],'NUMERIC_MINIMUM':'PASS','ZERO_RESTORE':'PASS',
 'ZERO_VISIBLE_RESULT':'STATIC_PALM_SHAPE_STILL_INSUFFICIENT','PRODUCTION_PROMOTION':'NO','DESIGN_ONLY':True,'NOT_PRODUCTION':True,
 'HUMAN_APPROVAL':'PENDING','VERDICT':'STATIC_PALM_SHAPE_STILL_INSUFFICIENT','READY_FOR_HUMAN_STATIC_SHAPE_APPROVAL':False,
 'STATIC_ITERATION_LIMIT_REACHED':True,'DYNAMIC_CASES_EXECUTED':0,'Stage6B_FINAL_PASS':'NOT_SET','PRODUCTION_SAVE_CALLS':0,
 'CANDIDATE_SAVE_CALLS':1,'PREVIOUS_TUNED_CANDIDATE_USED':False,'STOP':'HUMAN REVIEW'}
dump(PHASE+'_STATUS.json',status)
request=Path('<USER_HOME>/.codex/attachments/c9129a5b-c486-4405-ab90-f7e1a48501e7/已粘贴的文本.txt')
inputs=[ROOT/G['current']['path'],ROOT/G['source']['path'],ROOT/'audits/targeted_thenar_opposition_weight_tuning_r1/RIGHT_HAND_STAGE5B_PALMAR_THENAR_OPPOSITION_TUNED_CANDIDATE_R1.blend']
dump('FINAL_SOURCE_PROTECTION_R1.json',{'current_asset_unchanged':sha(inputs[0])==G['current']['sha256'],
 'official_source_unchanged':sha(inputs[1])==G['source']['sha256'],'historical_tuned_candidate_not_used':True,
 'historical_tuned_candidate_unchanged':sha(inputs[2])=='07403e568b4c193e471e8047a39bbcc30a3c54e7503329246ec1169dc1c449d0',
 'request':{'path':str(request),'sha256':sha(request)},'input_refs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in inputs]})
report=f'''# {PHASE}

结论：**STATIC_PALM_SHAPE_STILL_INSUFFICIENT**。本轮 5 个静态 design iterations 均未达到“正常比例的手掌”。保存第 2 版作为相对平稳的失败设计候选供 Human 审阅；不申请成功验收，不用 BETTER 代替 CORRECT。

从正式 asset `{G['current']['path']}`（SHA256 `{G['current']['sha256']}`）重新建立候选，没有使用上一轮 tuned candidate。最终候选 `{Path(P['candidate']['path']).name}`，SHA256 `{P['candidate']['sha256']}`。DESIGN_ONLY / NOT_PRODUCTION / HUMAN_APPROVAL_PENDING。

Official reference 为 v1.4.1 Hand - Realistic 实际 evaluated Multires L1（3300 vertices / 3298 faces）。读取官方 blend 后验证 L1 原生坐标与历史只读快照一致；未使用工程化 RSSF donor。A 列展示 native source 经 palm rigid registration 后的外形，保持原始 thumb neutral pose。

配准使用 wrist/palm-base、四个 MCP root patches、central metacarpal 六组结构中心，scale=1。独立 thumb-shaft rigid fit 为 thumb-root 的 donor field 处理姿态差；不把 source 张开角直接复制到当前手。配准是本轮设计近似，不宣称已完全分离姿态和外形；各 landmark residual 见 REGISTRATION_AND_SOURCE_REFERENCE_R1.json。宏观比例恢复不足仍是可见结果，不作 root-cause 推断。

完整掌侧范围覆盖 palm width、thenar、thumb-root、lower first-web floor 和 wrist/MCP 过渡，第 2 版实际修改 **{P['RESTORATION_VERTEX_COUNT']}** 个原生顶点，restoration strength=1.4，非最小点集或默认低比例 blend。场从 source 的 ancestry-derived outward contour / palmar fullness 缺额估计，在当前手上连续插值；generated CMC 顶点只用周围场插值，不伪造 source ID 对应。没有复制 donor faces / topology。为连续过渡修改 lower proximal thumb 的根部部分，其主体与 distal segment 在高度裙边以外保持原坐标。

{chr(10).join('- '+v['id']+'：'+v['note'] for v in iterations)}

最终视觉判断：掌宽和 thenar 体积有改善，upper thenar / thumb-root connection 仍没有达到来源模型的自然饱满比例；first-web 底部仍偏薄或角状。新的 thumb-root 至 lower proximal 角状轮廓 / diagonal facet，以及侧视中的 upper ulnar palm 外鼓，共计 2 个可见缺陷。故不能输出 VISUALLY_CORRECT_PALM_PROPORTION_PENDING_HUMAN，也不能输出 READY_FOR_HUMAN_STATIC_SHAPE_APPROVAL。

dorsal54 原生坐标保持，匹配哨兵未见回退。palmar16 按本轮要求作为视觉哨兵，允许坐标改变；匹配近景中旧 hard shelf 未重新出现，crease 仍存在。变化 ID 见 CANDIDATE_SAVE_REOPEN_PROTECTION_R1.json。

自动最低数值检查：NaN/Inf=0、collapsed faces=0、degenerate edges=0、ZERO restore=PASS。普通 solid screen 未见明显穿透或撕裂；**new hard contour=1，所以整体 MACHINE_SAFETY=FAIL_VISIBLE_HARD_CONTOUR**。数值通过不抵消产品外形失败。没有 hidden crossing census、normal-dot、strain 或动态审计。

候选保存一次并干净重开，原生位置与选中版本一致。UV/materials、topology/IDs、weights（含零项）、groups、modifiers、全部 21-bone rig / joints / rest / roll 均保持。仅自动 texspace bound 的派生值随 mesh bounds 改变；use_auto_texspace 原值保留，没有写 texture settings。无 shape keys / corrective。

22 张最终 matched renders：六个视图 × 三个资产，两个 sentinel × current/candidate。统一 camera、scale、material、lighting；source 的中性拇指姿态差明确保留，不能用整个手的 silhouette 差直接判断 pose-free volume。轮廓 overlay 仅供视觉辅助，不是数学 gate。

本轮已达到 5 版上限。最终候选与 review 页面供 Human 判断失败位置和下一步范围。没有运行 FULL_OPP_L1/L2/L3，未调 weights / rig，未跑 Stage6B final、左手镜像、motion retarget 或 production promotion。正式资产哈希保持。

**STOP — HUMAN REVIEW**。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
# A visual outline comparison, explicitly retaining native pose differences.
canvas=Image.new('RGB',(1200,1060),'#15191e');d=ImageDraw.Draw(canvas)
for asset,pose,color in [('OFFICIAL_L1','NEUTRAL','#68c7df'),('CURRENT','ZERO','#b9bcc2'),('CANDIDATE','ZERO','#edb669')]:
    im=Image.open(OUT/'renders'/f'{asset}__{pose}__SILHOUETTE.png').convert('L');mask=im.point(lambda v:255 if v>160 else 0)
    edge=ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(5)),mask.filter(ImageFilter.MinFilter(5)))
    layer=Image.new('RGB',im.size,color);canvas.paste(layer,(0,60),edge)
d.text((20,14),'Source cyan / Current gray / Candidate amber -- native neutral vs RSSF pose differs; visual aid only',fill='white')
canvas.save(OUT/'SILHOUETTE_OVERLAY_VISUAL_AID_R1.png')
views={'HUMAN_PALMAR':'Human 掌侧斜视','FULL_PALM':'Full palm 全掌','THENAR_CLOSE':'Thenar close','FIRST_WEB_CLOSE':'First-web close','SIDE_VOLUME':'Side volume','SILHOUETTE':'Silhouette'}
options=''.join(f'<option value="{k}">{v}</option>' for k,v in views.items())
figs=''.join(f'<figure><figcaption>{title}</figcaption><button class="image" data-asset="{a}" aria-label="放大 {title}"><img src="renders/{a}__{pose}__HUMAN_PALMAR.png" alt="{title} · HUMAN_PALMAR"></button></figure>' for a,pose,title in [('OFFICIAL_L1','NEUTRAL','A · OFFICIAL L1 / Stage2 SOURCE'),('CURRENT','ZERO','B · CURRENT ZERO / RSSF'),('CANDIDATE','ZERO','C · MACRO CANDIDATE ZERO / RSSF')])
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Palmar macro restoration · Static review</title>
<style>:root{color-scheme:dark;font:14px system-ui,"Microsoft YaHei",sans-serif;background:#161a20;color:#ecf0f4}*{box-sizing:border-box}body{margin:0;padding:18px}main{max-width:1800px;margin:auto}h1{font-size:22px;margin:0 0 8px}h2{font-size:18px}p{line-height:1.6;margin:8px 0}.badge{color:#f5ba89}.muted{color:#b8c2ce;font-size:12px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.pair{grid-template-columns:repeat(2,minmax(0,1fr))}figure{margin:0;min-width:0}figcaption{padding:8px 0}.image{width:100%;display:block;padding:0;border:1px solid #586573;cursor:zoom-in;background:#242c35}.image img{width:100%;display:block}button,select,textarea{font:inherit;color:inherit}select,.action,.toolbar button{background:#273342;border:1px solid #758397;border-radius:4px;padding:6px 10px;cursor:pointer}.controls{display:flex;gap:18px;align-items:center;margin:12px 0;flex-wrap:wrap}a{color:#98d1f7}details{margin:18px 0;padding:12px;background:#202834}summary{cursor:pointer}fieldset{border:1px solid #546172;margin:10px 0;padding:14px}label{margin-right:15px}textarea{display:block;width:100%;min-height:80px;background:#202834;border:1px solid #738096;margin:8px 0}dialog{width:min(1450px,96vw);max-height:96vh;padding:12px;background:#121820;border:1px solid #81909e}dialog::backdrop{background:#000d}dialog img{display:block;max-width:100%;max-height:80vh;margin:auto}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px}@media(max-width:650px){.grid{grid-template-columns:1fr}}[hidden]{display:none!important}</style>
<main><h1>掌侧宏观比例恢复 · ZERO 静态审阅</h1><p class="badge">STATIC_PALM_SHAPE_STILL_INSUFFICIENT · DESIGN ONLY · HUMAN APPROVAL PENDING</p><p>5 版均未达到自然掌形。当前展示第 2 版：体积有所改善，拇指根连接仍不足；新的角状过渡与侧视掌缘外鼓，共 2 个可见缺陷。数值最低检查通过；可见外形门未通过。</p>
<div class="controls"><label>比较视图 <select id="view" aria-label="比较视图">OPTIONS</select></label><label>静态版本 <select id="iteration" aria-label="静态版本"><option value="final">最终候选 · 第 2 版</option><option value="01">第 1 版 · 淘汰</option><option value="02">第 2 版 · 选中但不合格</option><option value="03">第 3 版 · 淘汰</option><option value="04">第 4 版 · 淘汰</option><option value="05">第 5 版 · 淘汰</option></select></label></div><div class="grid" id="triple">FIGURES</div>
<p class="muted">三列使用相同相机、尺度、灰色材质与光照。Official L1 保留 native neutral 拇指姿态；Current / Candidate 为 RSSF。来源图中的张开角差不代表当前应该复制该姿态。点击图像可放大并切换 A/B/C。</p>
<details><summary>dorsal54 / palmar16 视觉哨兵</summary><div id="sentinels"></div></details>
<details><summary>轮廓辅助图 · 不是数学 gate</summary><p>Source 青色 / Current 灰色 / Candidate 橙色。来源中性姿态不同，此图仅辅助观察外形。</p><img style="max-width:100%;max-height:850px" src="SILHOUETTE_OVERLAY_VISUAL_AID_R1.png" alt="轮廓视觉辅助"></details>
<p><a href="CANDIDATEFILE">下载 design-only candidate blend</a> · <a href="REPORTFILE">报告</a> · <a href="STATUSFILE">状态 JSON</a></p>
<h2>Human 静态外形反馈</h2><p>尚未提交任何 Human 结论；选项无默认值。此轮之后仍先停止，由 Human 决定下一步。</p><form id="feedback"><fieldset><legend>Q1 · 整体掌形是否已是自然比例？</legend><label><input type="radio" name="q1" value="ACCEPT" required>ACCEPT</label><label><input type="radio" name="q1" value="REJECT">REJECT</label></fieldset><fieldset><legend>Q2 · 虎口下方 / thenar 上缘 / thumb-root 连接是否饱满连续？</legend><label><input type="radio" name="q2" value="ACCEPT" required>ACCEPT</label><label><input type="radio" name="q2" value="REJECT">REJECT</label></fieldset><fieldset><legend>Q3 · 是否有新的鼓包、凹坑、硬折或哨兵回退？</legend><label><input type="radio" name="q3" value="NO" required>NO</label><label><input type="radio" name="q3" value="YES">YES</label></fieldset><label for="notes">具体位置或说明</label><textarea id="notes" name="notes"></textarea><button class="action" type="submit">下载本地反馈 JSON</button><p id="saved" class="muted"></p></form><p class="badge">STOP — HUMAN REVIEW · 未运行 opposition，未推广正式资产</p></main>
<dialog id="lightbox"><div class="toolbar"><span id="caption"></span><div><button id="prev">上一列</button> <button id="next">下一列</button> <button id="close">关闭</button></div></div><img id="large" alt=""></dialog>
<script>const assets=['OFFICIAL_L1','CURRENT','CANDIDATE'],titles=['A · OFFICIAL L1 SOURCE','B · CURRENT ZERO','C · CANDIDATE ZERO'];const view=document.querySelector('#view'),iteration=document.querySelector('#iteration'),box=document.querySelector('#lightbox');let chosen=0,collection=[];
function path(a,v,folder){return `${folder}/${a}__${a==='OFFICIAL_L1'?'NEUTRAL':'ZERO'}__${v}.png`}
function update(){let v=view.value,folder=iteration.value==='final'?'renders':`iteration_${iteration.value}_renders`;document.querySelectorAll('#triple .image').forEach((b,i)=>{let src=path(assets[i],v,folder);b.querySelector('img').src=src;b.querySelector('img').alt=titles[i]+' · '+v;b.setAttribute('aria-label','放大 '+titles[i]+' '+v);b.onclick=()=>openGroup([...document.querySelectorAll('#triple .image img')],i)})}
function openGroup(imgs,i){collection=imgs.map(im=>({src:im.src,alt:im.alt}));chosen=i;show();box.showModal()}
function show(){let item=collection[chosen];document.querySelector('#large').src=item.src;document.querySelector('#large').alt=item.alt;document.querySelector('#caption').textContent=item.alt}
document.querySelector('#prev').onclick=()=>{chosen=(chosen+collection.length-1)%collection.length;show()};document.querySelector('#next').onclick=()=>{chosen=(chosen+1)%collection.length;show()};document.querySelector('#close').onclick=()=>box.close();box.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')document.querySelector('#prev').click();if(e.key==='ArrowRight')document.querySelector('#next').click()});view.onchange=update;iteration.onchange=update;update();
for(let v of ['DORSAL54_SENTINEL','PALMAR16_SENTINEL']){let section=document.createElement('section');section.innerHTML=`<h2>${v}</h2><div class="grid pair">`+['CURRENT','CANDIDATE'].map(a=>`<figure><figcaption>${a}</figcaption><button class="image" aria-label="放大 ${a} ${v}"><img src="${path(a,v,'renders')}" alt="${a} · ${v}"></button></figure>`).join('')+'</div>';document.querySelector('#sentinels').append(section);section.querySelectorAll('button').forEach((b,i)=>b.onclick=()=>openGroup([...section.querySelectorAll('img')],i))}
document.querySelector('#feedback').onsubmit=e=>{e.preventDefault();let data=Object.fromEntries(new FormData(e.target));data.phase='PHASENAME';data.candidate_sha256='CANDIDATESHA';data.timestamp=new Date().toISOString();data.static_only=true;let url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));let a=document.createElement('a');a.href=url;a.download='PALMAR_MACRO_HUMAN_STATIC_REVIEW_R1.json';a.click();URL.revokeObjectURL(url);document.querySelector('#saved').textContent='反馈 JSON 已下载到本地；未自动改变项目状态或启动动态工作。'};
</script></html>'''
for key,val in {'OPTIONS':options,'FIGURES':figs,'CANDIDATEFILE':Path(P['candidate']['path']).name,'REPORTFILE':PHASE+'_REPORT.md','STATUSFILE':PHASE+'_STATUS.json','PHASENAME':PHASE,'CANDIDATESHA':P['candidate']['sha256']}.items():html=html.replace(key,val)
(OUT/'review.html').write_text(html,encoding='utf-8')
dump('DELIVERY_VERIFICATION_R1.json',{'status':'PENDING_BROWSER_VERIFICATION','outputs_present':True,'matched_render_count':22,
 'candidate_saved_and_clean_reopened':True,'Human_answers_preselected':False,'product_verdict':status['VERDICT'],'overall_machine_gate':machine['MACHINE_SAFETY'],'STOP':'HUMAN REVIEW'})
print('STATIC_FAILURE_REVIEW_READY',P['candidate']['sha256'])
