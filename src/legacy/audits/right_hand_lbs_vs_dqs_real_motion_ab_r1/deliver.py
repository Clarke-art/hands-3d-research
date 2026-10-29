import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PHASE='RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v=read('DEFORMATION_MODE_VERIFICATION_R1.json');minimum=read('MINIMUM_MACHINE_SAFETY_R1.json');video=read('VIDEO_VERIFICATION_R1.json')
assert v['status']==minimum['status']==video['status']=='PASS'
notes={130:'DQS 减少小阶梯，但残留较大的角状折口，桥面鼓起并形成更宽、突出的片状折边；仍为明显 blocker。',76:'阶梯凹口减轻，桥面更饱满；仍有深沟及 upper-web 尖薄折边。',205:'部分凹折变平，斜视仍有角状峰和折沟；未达到自然可接受。',31:'桥面稍平顺；斜视深沟与尖折仍在。',61:'低缺陷对照基本保持，只有轻微形状和 shading 差异。'}
frame_status={130:'WORSE_PROMINENT_PLATE_LIKE_FOLD_BLOCKER',76:'PARTIAL_NOTCH_REDUCTION_RESIDUAL_FOLD',205:'PARTIAL_REDUCTION_RESIDUAL_ANGULAR_FOLD',31:'SMALL_IMPROVEMENT_RESIDUAL_CREASE',61:'LOW_DEFECT_CONTROL_PRESERVED'}
regstatus={c:('PRELIM_ACCEPTABLE_MINOR_CREASE_CHANGE' if c in ['CMC_OPP_30','FULL_OPP_L3'] else 'PRELIM_ACCEPTABLE') for c in ['ZERO','INDEX_MCP_45','CMC_OPP_30','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3']}
visible={'authority':'Agent ordinary solid-view preliminary review; Human decision pending','PRIMARY_CLASSIFICATION':'DQS_WORSE','keyframe_notes':notes,'regression':regstatus,'DQS_NEW_VISIBLE_DEFECT_COUNT':1,'count_unit':'One issue type: more prominent broad plate-like first-web fold/protrusion. Not a frame census.','gross_visible_tearing':{'LBS':0,'DQS':0},'full_motion_review':{'frames':[1,210],'views':['PALMAR_MOTION','OBLIQUE_MOTION'],'reviewed_all_210_paired_frames':True,'method':'Seven complete 30-frame comparison sheets, five selected full-resolution matched close comparisons and six regression poses. No severity census or new ranking.','limitation':'Video playback supplied for Human temporal acceptability review; visual minimum is ordinary inspection, not an intersection audit.'},'thenar_ballooning':'No obvious separate gross ballooning in these views','thumb_root_twist':'No obvious separate gross twist','regression_note':'CMC_OPP_30/FULL_OPP_L3 retain comparable thumb silhouette, with a slightly sharper crease/ridge under DQS. Final acceptability remains Human pending.'}
dump('VISIBLE_AB_REVIEW_R1.json',visible)
minimum['gross_visible_tearing']={'LBS':0,'DQS':0};minimum['gross_visible_tearing_authority']='Ordinary solid-view agent review; no hidden tearing/intersection census';dump('MINIMUM_MACHINE_SAFETY_R1.json',minimum)
key=read('KEYFRAME_LBS_VS_DQS_R1.json')
for row in key['frames']:row.update({'DQS_preliminary_status':frame_status[row['frame']],'visible_note':notes[row['frame']],'human_status':'PENDING'})
dump('KEYFRAME_LBS_VS_DQS_R1.json',key)
reg=read('REGRESSION_LBS_VS_DQS_R1.json')
for row in reg['poses']:row.update({'DQS_preliminary_status':regstatus[row['case']],'human_status':'PENDING'})
dump('REGRESSION_LBS_VS_DQS_R1.json',reg)
status={'PHASE':PHASE,'TASK_TYPE':'DEFORMATION_ARCHITECTURE_AB_TEST','SOURCE_BASELINE_SHA256':v['SOURCE_BASELINE_SHA256'],'SOURCE_ACTION':'PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1','SOURCE_MOTION_CHANGED':'NO','SOURCE_WINDOW_SECONDS':[11.5,18.5],'SOURCE_OBSERVATIONS':421,'BASELINE_DEFORMATION_MODE':'LBS','LBS_PRESERVE_VOLUME':False,'DQS_PRESERVE_VOLUME':True}
for k in ['MESH_IDENTICAL','WEIGHTS_IDENTICAL','RIG_IDENTICAL','CORRECTIVES_IDENTICAL','DRIVERS_IDENTICAL','MODIFIER_STACK_IDENTICAL_EXCEPT_DQS']:status[k]='YES' if v[k] else 'NO'
status.update({'F130_LBS_STATUS':'DEEP_STEPPED_NOTCH_VISIBLE_BLOCKER','FULL_7S_LBS_STATUS':'VISIBLE_FIRST_WEB_BLOCKERS','FULL_7S_DQS_STATUS':'RESIDUAL_FOLD_AND_MORE_PROMINENT_PLATE_LIKE_WEB_DISTORTION','DQS_NEW_VISIBLE_DEFECT_COUNT':1,'NEW_CORRECTIVE_COUNT':0,'FINGERTIP_ISSUE_STATUS':'DEFERRED','PRIMARY_CLASSIFICATION':'DQS_WORSE','CLASSIFICATION_AUTHORITY':'AGENT_PRELIMINARY_HUMAN_PENDING','VERDICT':'DQS_WORSE','WORKFLOW_STATUS':'STOP_HUMAN_REVIEW','HUMAN_REVIEW':{'Q1':None,'Q2':None,'Q3':None,'Q4':None},'PRODUCTION_PROMOTION':'NO','MINIMUM_MACHINE_SAFETY':'PASS','ZERO_RESTORE':'PASS','FAILED_PREVIOUS_CANDIDATE_USED':'NO','test_asset':v['test_asset']})
for f,s in frame_status.items():status[f'F{f}_DQS_STATUS']=s
for c,s in regstatus.items():status[c+'_DQS_REGRESSION']=s
for k in ['BASELINE','WEIGHTS','MESH','RIG','CORRECTIVE','DRIVER','ACTION']:status[k+'_MODIFIED']='NO'
dump(PHASE+'_STATUS.json',status)
for view,name in [('PALMAR_MOTION','palmar'),('OBLIQUE_MOTION','first_web')]:
    cv=Image.new('RGB',(1280,640));d=ImageDraw.Draw(cv)
    for x,l in enumerate(['LBS','DQS']):
        cv.paste(Image.open(OUT/(l.lower()+'_motion')/f'{l}__F130__{view}.png').convert('RGB'),(x*640,0));d.rectangle((x*640,0,x*640+190,28),fill='#15202b');d.text((x*640+8,8),l+' F130',fill='white')
    cv.save(OUT/f'poster_{name}.jpg',quality=92)
report=f'''# {PHASE}

预分类：**DQS_WORSE**。当前步骤结束于 **STOP — HUMAN REVIEW**。此结论为代理的普通实体视图判断，四项 Human 答案未填写，PRODUCTION_PROMOTION = NO。

DQS 在部分动作帧明显减轻 LBS 的小阶梯凹折，但 F130 仍有大的角状折口，虎口桥面更鼓起，形成更宽且突出的片状折边。按本轮“明显 first-web distortion / 更差”的分类规则，优先归 DQS_WORSE。局部变平的收益已保留在下面的逐帧说明中；不能据此认定 DQS 完全无效，也不能认定 LBS 体积损失是唯一或主要根因。纯 Preserve Volume 开关没有使这段动作达到自然可接受程度。

冻结基线实际读取：LBS，ArmatureModifier.use_deform_preserve_volume = False；SHA256 `{v['SOURCE_BASELINE_SHA256']}`。仅从该基线创建独立测试，再从 axis-corrected test 追加原 Action，未重新 retarget。上一轮失败候选未加载。新增 corrective = 0。

A_LBS / B_DQS 的对象变换完全一致，mesh / UV / 顶点索引 / weights / materials / Key datablock / approved driver 均共享或逐项一致。Rest armature datablock 共享，两份 pose rig 使用同一个 Action。B 的 Armature target 绑定到其等价 rig；归一化 target 身份后，全部 modifier RNA 设置和顺序只差 Preserve Volume。驱动目标保留原 A rig，未改 driver：所有 421 个观察点和六个姿态均逐骨确认 A/B pose matrices 完全一致，因此共享 corrective 的自然求值对 A/B 相同。测试中不应独立改变其中一份 pose rig。Blender 中两份测试对象位于同一位置，单独查看时可用 Outliner 隐藏另一份 mesh；审核渲染从各自 evaluated mesh 生成。

Shape keys 在原 modifier stack 前求值，modifier 未新增、未应用、未重排。原批准 corrective `FIRST_WEB_OPPOSITION_CREASE_R1` 自然求值；关键帧数值见 KEYFRAME_LBS_VS_DQS_R1.json，全部观测点见 APPROVED_CORRECTIVE_NATURAL_VALUES_R1.json。

|关键帧|DQS 普通可见检查|
|---|---|
'''+''.join(f'|F{f}|{notes[f]}|\n' for f in [130,76,205,31,61])+f'''
帧时序：Ff 对应 observation index 2×(f−1)，源 frame 690+2×(f−1)，源时间 11.5+(f−1)/30 秒。Action 端点 F211 与半帧保留不变。视频 F1–F210 / 30fps，时长精确 7.000 秒，两组左右并排 LEFT=LBS、RIGHT=DQS。421 观测点全部用于最低安全检查，未删 key、改 smoothing 或时间。

六个旧姿态 ZERO、INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L1/L2/L3，代理初判保留可接受外形。CMC_OPP_30 / FULL_OPP_L3 的 crease 稍尖，留待 Human 判断。ZERO A/B 最大位置差 {minimum['ZERO_A_B_max_mm']:.9f} mm，为浮点求值量级，四个 ZERO 视图无明显外形变化；两组恢复到各自 ZERO 的误差均为 0 mm。

最低机器安全：两组 421 个观测点 + 六姿态 NaN/Inf = 0、collapsed face = 0、degenerate edge = 0、ZERO restore = PASS。普通实体视图 gross visible tearing = 0（代理检查，非 hidden forensic 证明）。未执行 volume integral、strain/crossing/normal-dot census、R3、true-cap、2127 edges 或 Stage6 重验。DQS_NEW_VISIBLE_DEFECT_COUNT = 1 表示一个问题类型：更加突出的片状虎口折边，不表示异常帧计数。指尖问题仍 DEFERRED。

渲染相机使用之前从 unchanged BEFORE motion 得到的相机记录；没有加载失败候选。A/B 每帧使用相同相机与 framing。使用统一 Workbench 中性实体材质、display-only smooth shading、无 cavity、shadow intensity 0；材质与网格资产本身未更改。关键帧有 frontal first-web close、palmar/thenar close、oblique、palmar context；每姿态有 palmar full、thenar close、dorsal full、first-web close。

交付：review.html；两视角同步对照视频；40 张关键帧、48 张旧姿态、840 张完整动作 matched renders；独立 test blend 与脚本、数据验证。基线与源数据 SHA256 前后保持不变。

Human review：

1. DQS / Preserve Volume 是否明显改善真实 motion 的虎口深折？YES / NO
2. DQS 下完整 7 秒虎口是否已自然可接受？YES / NO
3. DQS 是否引入新的明显鼓包、扭曲或旧姿态回退？NO / YES
4. 是否值得把右手产品 deformation 从 LBS 改为 DQS 继续验证？YES / NO

按照请求在此停止。不推广、修改正式基线或尝试 hybrid。若 Human 确认此路线无价值，后续 architecture rebuild assessment 需要新的独立任务；本轮不执行。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LBS vs DQS · 真实动作 A/B R1</title><style>
body{background:#101820;color:#e6edf4;font:16px/1.6 system-ui;margin:0}main{max-width:1280px;margin:auto;padding:24px}h1{font-size:28px}h2{font-size:22px;margin-top:36px}.banner{padding:18px;border:1px solid #d39460;background:#33251d;border-radius:10px}video{width:100%;background:#202933;border-radius:8px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px}.pair img{width:100%;display:block}figure{margin:0}figcaption{padding:7px;background:#202c37}select,button{padding:8px;font-size:16px;background:#263744;color:white;border:1px solid #607080;border-radius:5px}a{color:#91caff}.hint{color:#b6c4d1}section{border-top:1px solid #35424e;margin-top:28px;padding-top:12px}#frameNote{background:#202c37;padding:10px}.grid{display:grid;gap:18px}.links{display:flex;gap:20px;flex-wrap:wrap}</style><main>
<h1>LBS vs DQS / Preserve Volume</h1><p>同一冻结基线 · 同一真实动作 11.5–18.5 秒 · LEFT = LBS / RIGHT = DQS</p><div class="banner"><b>预分类：DQS_WORSE · STOP — HUMAN REVIEW</b><br>部分阶梯凹折减轻；F130 仍有折口，并出现更突出的片状虎口折边。正式基线保持冻结，未推广。</div>
<section><h2>1 · 完整 7 秒同步比较</h2><p class="hint">每个视频内部两组已同步。可暂停、拖动和全屏查看；默认未播放。</p><h3>Palmar / pianist-side</h3><video id="palmarVideo" controls loop muted preload="metadata" poster="poster_palmar.jpg" src="review_lbs_vs_dqs_palmar.mp4"></video><h3>First-web oblique</h3><video id="obliqueVideo" controls loop muted preload="metadata" poster="poster_first_web.jpg" src="review_lbs_vs_dqs_first_web.mp4"></video></section>
<section><h2>2 · 关键帧</h2><label for="frameSelect">帧 </label><select id="frameSelect"><option value="130">F130 · MOST_SEVERE</option><option value="76">F76 · SEVERE</option><option value="205">F205 · SEVERE</option><option value="31">F31 · MODERATE</option><option value="61">F61 · LOW-DEFECT CONTROL</option></select><p id="frameNote"></p><div id="frameImages" class="grid"></div></section>
<section><h2>3 · 六个批准旧姿态 regression</h2><label for="poseSelect">姿态 </label><select id="poseSelect"><option>ZERO</option><option>INDEX_MCP_45</option><option>CMC_OPP_30</option><option>FULL_OPP_L1</option><option>FULL_OPP_L2</option><option>FULL_OPP_L3</option></select><p class="hint">代理初判旧姿态外形保留可接受；CMC_OPP_30 / FULL_OPP_L3 crease 稍尖，请重点确认。</p><div id="poseImages" class="grid"></div></section>
<section><h2>Human review · 只需回复四题</h2><ol><li>DQS 是否明显改善真实 motion 的虎口深折？YES / NO</li><li>DQS 下完整 7 秒虎口是否已自然可接受？YES / NO</li><li>DQS 是否引入新的明显鼓包、扭曲或旧姿态回退？NO / YES</li><li>是否值得把右手产品 deformation 从 LBS 改为 DQS 继续验证？YES / NO</li></ol><p>四项 Human 答案均待回复。新 corrective = 0；指尖问题 DEFERRED。</p><div class="links"><a href="RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_REPORT.md">完整报告</a><a href="RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1_STATUS.json">状态数据</a><a href="RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1.blend">独立 A/B blend</a></div></section>
<script>const notes=NOTES;function pair(folder,pose,view,title){return `<div><h3>${title}</h3><div class="pair">${['LBS','DQS'].map(l=>`<figure><figcaption>${l}</figcaption><a href="${l.toLowerCase()}_${folder}/${l}__${pose}__${view}.png" target="_blank"><img src="${l.toLowerCase()}_${folder}/${l}__${pose}__${view}.png" alt="${l} ${pose} ${title}"></a></figure>`).join('')}</div></div>`}function frames(){let f=document.querySelector('#frameSelect').value;document.querySelector('#frameNote').textContent=notes[f];document.querySelector('#frameImages').innerHTML=[['FIRST_WEB_CLOSE','First-web close'],['PALMAR_THENAR_CLOSE','Palmar / thenar close'],['FIRST_WEB_OBLIQUE','First-web oblique'],['PALMAR_CONTEXT','Full-hand context']].map(([v,t])=>pair('selected','F'+f.padStart(3,'0'),v,t)).join('')}function poses(){let p=document.querySelector('#poseSelect').value;document.querySelector('#poseImages').innerHTML=[['PALMAR_FULL','Palmar full'],['THENAR_CLOSE','Thenar close'],['DORSAL_FULL','Dorsal full'],['FIRST_WEB_CLOSE','First-web close']].map(([v,t])=>pair('regression',p,v,t)).join('')}document.querySelector('#frameSelect').addEventListener('change',frames);document.querySelector('#poseSelect').addEventListener('change',poses);frames();poses();</script></main></html>'''.replace('NOTES',json.dumps(notes,ensure_ascii=False))
(OUT/'review.html').write_text(html,encoding='utf-8')
for p,h in v['input_hashes_unchanged'].items():assert sha(ROOT/p)==h
assert sha(ROOT/v['test_asset']['path'])==v['test_asset']['sha256']
print('AB_REPORT_REVIEW_READY_DQS_WORSE_HUMAN_PENDING')
