import json,hashlib,numpy as np
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];PHASE='RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
S=read('SENSITIVITY_RESPONSE_R1.json');P=read('WEIGHT_FIELD_PROBE_VERIFICATION_R1.json');W=read('READ_ONLY_WEIGHT_FIELD_R1.json')
band=P['representative_band_gradient'];old=np.array([r['before_per_mm'] for r in band]);new=np.array([r['after_per_mm'] for r in band]);reduction=float(1-new.mean()/old.mean())
Q={'Q1':'YES','Q2':'MIXED','Q3':'NO','Q4':'YES','Q5':'YES','Q6':'NO','Q7':'NO','Q8':'YES','Q9':'INSUFFICIENT_EVIDENCE'}
questions={'Q1':'F130 fold 与 WRIST/THUMB 高 ratio-gradient 区域空间一致？','Q2':'多个 folded frame 是否要求大体一致的局部 transfer 方向？','Q3':'改善方向是否明显破坏 F110/F176？','Q4':'是否执行 ONE deterministic weight-field candidate？','Q5':'weight-gradient 是否实质性降低？','Q6':'F130 blocker 是否明显改善？','Q7':'F127/F160/F205 是否一致改善？','Q8':'F110/F176 是否保持自然平滑？','Q9':'最终诊断'}
explain={'Q1':'7/8 inherited band edges have pair-ratio gradients above the ROI mean. Spatial association only; the pair is not the largest full-vector contribution.','Q2':'F127/F160/F205 corresponding-point closure projections broadly agree, but several F130 signs reverse. These tiny edge-closure proxies do not establish a visible static-weight conflict.','Q3':'Both 0.02 micro-transfer directions preserve the two smooth-frame appearances; no visibly destructive direction has been demonstrated.','Q4':'One unique Dirichlet harmonic R field, 234-node inherited ROI / 70 pinned boundary nodes / 164 free nodes.','Q5':f'YES for the preselected F130 8-edge pair-ratio band: mean gradient decreases {reduction*100:.2f}% (7/8 edges decrease). Whole ROI mean/max do not decrease; full-vector band L1 decreases only 11.62%. Do not generalize this answer to the whole weight field.','Q6':'Deep stepped fold remains in both prescribed views; the pair field has not made F130 natural.','Q7':'No consistent visible blocker improvement across the three other folded frames.','Q8':'The two control frames stay smooth; no obvious new bulge/flap/hard shelf/palm-volume distortion in the matched views.','Q9':'Causal isolation for the requested whole-field-versus-21-bone-DOF question fails: the allowed manipulated pair accounts for only 9–35% of the inherited endpoint-vector L1. Most of the actual gradient is held constant in directly observed INDEX influences. Asset and pair-intervention controls pass, but an unsuccessful pair-field probe cannot distinguish an untested static full-vector field problem from a DOF limit.'}
notes={110:'SMOOTH：两方向微扰及 harmonic probe 仍保持平滑。',127:'FOLDED：harmonic probe 未显著消除主折口。',130:'PEAK：主阶梯深折保留；局部 ratio-gradient 降低未带来明显自然外观。',160:'FOLDED：主凹沟/角折保留。',176:'SMOOTH / RECOVERY：仍平滑。',205:'FOLDED：外形有小幅变化，主要折口与尖折仍在。'}
controls={'asset_and_saved_candidate_controls':'PASS','actual_evaluated_deformation':'BLENDER_ONLY','pair_S_and_all_other_weights':'PASS','manipulation_target_pair_band_gradient':'PASS_LOCAL_BAND_ONLY','whole_ROI_gradient_reduction':'NOT_ACHIEVED','whole_static_weight_field_vs_DOF_causal_isolation':'FAIL','CONTROL_FAILURE_CODE':'ALLOWED_PAIR_INTERVENTION_DOES_NOT_ISOLATE_DOMINANT_FULL_VECTOR_GRADIENT','reason':explain['Q9'],'not_a_missing_file_or_incomplete_execution':True,'not_a_claim_all_21_bone_static_fields_are_impossible':True}
dump('CAUSAL_DISCRIMINATION_CONTROL_R1.json',controls)
dump('VISIBLE_RESULT_R1.json',{'authority':'Agent preliminary ordinary solid-view review; Human pending','frame_notes':notes,'micro_transfer_clear_visible_static_conflict':False,'F130_HUMAN_VISIBLE_RESULT':'NO_CLEAR_IMPROVEMENT_BLOCKER_OPEN','folded_frames_consistent_improvement':False,'smooth_controls_preserved':True,'new_visible_defect_types':0,'views':['FIRST_WEB_OBLIQUE','PALMAR_THENAR_CLOSE'],'reviewed_conditions':['BASELINE','WRIST_TO_THUMB','THUMB_TO_WRIST','WEIGHT_FIELD_PROBE'],'reviewed_frames':[110,127,130,160,176,205],'excluded_hidden_checks':True})
status={'PHASE':PHASE,**Q,'FINAL_DIAGNOSIS':'INSUFFICIENT_EVIDENCE','FINAL_DIAGNOSIS_REASON':explain['Q9'],'CONTROL_STATUS':controls,'WEIGHT_FIELD_PROBE':'RUN','F130_HUMAN_VISIBLE_RESULT':'NO_CLEAR_IMPROVEMENT_BLOCKER_OPEN','FROZEN_FALLBACK_UNCHANGED':'YES','FROZEN_FALLBACK_STATUS':'PROTECTED_FROZEN_FALLBACK','SOURCE_BASELINE_SHA256':W['frozen_sha256'],'SOURCE_ACTION':'PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1','SOURCE_MOTION_CHANGED':'NO','SOURCE_WINDOW_SECONDS':[11.5,18.5],'SOURCE_OBSERVATIONS':421,'LEVEL_1_TOPOLOGY_ROUTE':'CLOSED','STATIC_WEIGHT_FIELD_PROBLEM_SUPPORTED':False,'DEFORMATION_DOF_LIMIT_SUPPORTED':False,'FIRST_WEB_HUMAN_VISIBLE_BLOCKER':'OPEN','RIGHT_HAND_DEFORMATION_CLOSED':'NO','LEFT_HAND_START':'NO','WEB_PRODUCT_PROMOTION':'NO','PRODUCTION_POINTER_MOVED':'NO','candidate':P['candidate'],'candidate_count':1,'candidate_status':'DESIGN_ONLY_NOT_PRODUCTION_HUMAN_APPROVAL_PENDING','new_corrective_count':0,'new_helper_bone_count':0,'cage_or_DQS_used':False,'WORKFLOW_STATUS':'STOP_HUMAN_REVIEW','Q5_SCOPE':'YES for selected F130 pair-ratio band; NO for whole ROI mean/max; not all-vector causal isolation','human_final_decision':'PENDING'}
dump(PHASE+'_STATUS.json',status)
report=f'''# {PHASE}

**FINAL_DIAGNOSIS = INSUFFICIENT_EVIDENCE**

WEIGHT_FIELD_PROBE = RUN（恰好一份）；F130_HUMAN_VISIBLE_RESULT = NO_CLEAR_IMPROVEMENT_BLOCKER_OPEN；FROZEN_FALLBACK_UNCHANGED = YES。STOP — HUMAN REVIEW。

本次出现的是**因果隔离控制失效**，而不是资产污染或执行缺失：只允许改变的 WRIST/THUMB 两项实际仅覆盖继承最坏8边完整权重向量 L1 差的9.45%–35.18%。直接读取的 INDEX MCP/PIP/DIP 项贡献更大，且按本轮要求逐点固定保留。失败的两项 probe 不能排除这些未改变的静态场仍不合理，因此不能推出整个21-bone deformation basis不足。此处使用 INSUFFICIENT_EVIDENCE 的原因是 A/B 所需隔离对照没有成立；并非因为还想多做候选或不愿作选择。

|题|回答|口径|
|---|---|---|
'''+''.join(f'|{k} {questions[k]}|**{Q[k]}**|{explain[k]}|\n' for k in Q)+f'''

继承权威：已经读取上一阶段 report、attribution、design、measurements、verification、protection及 DESIGN_ONLY candidate，candidate SHA256 `373b8516fe45d8f9f83e752eeb3607e7bfd7e3135ed8467ad22272a99ac355bb`。只读打开其对象/Action元数据；未重建 topology、未复做其实验。Human 已关闭 LEVEL_1 topology route。正式 fallback SHA256 `{W['frozen_sha256']}` 保持，状态继承 PROTECTED_FROZEN_FALLBACK，blocker仍OPEN。

输入来自原 frozen mesh + 原 axis-corrected Action，未用 topology candidate 作新权重资产起点。继续同一11.5–18.5秒/421 observations，使用六决策帧110/127/130/160/176/205及上一阶段相机。禁止路线均未开启；也没有扩大到对INDEX做扰动或优化。完整 weight vector 的读取是本轮明确要求，记录 INDEX 项是因为8条指定边上存在直接数据，不是猜测。

只读完整向量的重要新事实：

|原F130代表边|WRIST+THUMB占全部向量L1差|保留的INDEX MCP/PIP/DIP L1贡献合计|
|---|---|---|
'''+''.join(f"|{r['edge'][0]}–{r['edge'][1]}|{r['WRIST_THUMB_pair_fraction_of_full_L1']*100:.2f}%|{sum(r['L1_component_contributions'].get(n,0) for n in ['INDEX_MCP_R','INDEX_PIP_R','INDEX_DIP_R']):.4f}|\n" for r in W['representative_edges'])+f'''
所以“空间重合”是YES，但不能把“最大两项的bone名称是WRIST/THUMB”当成“完整向量梯度主要由这两项产生”。例如2035–3143，完整L1差0.4900，WRIST/THUMB两项只贡献0.0463，其余大部分是INDEX链项；其pair ratio gradient本来只有0.00218/mm。所有端点完整16项向量见 READ_ONLY_WEIGHT_FIELD_R1.json，未重做strain census或相关系数研究。

微扰严格一次固定幅度 δw=0.02，复用原最坏8条边的14个唯一端点。先分别对14点同时执行 WRIST→THUMB / THUMB→WRIST 两方向，渲染六帧×两视角；再每点独立执行同幅度±扰动，测实际 evaluated vertex displacement。每次恢复原值，其他bones逐点完全一致，每点S不变（float32误差界1e−7）；ZERO恢复误差0mm。局部Jacobian用实际求值的中心差分 `(X_plus-X_minus)/(2δw)`，**没有重建LBS矩阵链**。

方向证据定义为该点位移在“朝向同一代表边另一端”的投影，这是关闭局部边间距的响应代理，不是已有自然软组织目标面。F127/F160/F205多数对应点偏好同号；F130某些点反号。例如点338投影依次+0.0107/−0.0104/+0.0381/+0.0835mm；点1525为+0.0207/−0.0112/+0.0503/+0.0802mm；点2825为−0.0188/+0.0112/−0.0470/−0.0779mm。F130整个微扰的最大位移仅0.0647mm，普通实体视图没有明显改善或破坏。这样微小的代理符号反转不足以宣告有Human-visible STATIC_WEIGHT_CONFLICT；F110/F176两方向均保持平滑。故本次仍未排除静态pair field可能性，执行唯一允许的确定性probe。门槛理由见 SENSITIVITY_GATE_R1.json。

静态 probe：沿用上一轮234节点ROI/70节点外边界，在164个内部点求一次Dirichlet harmonic解。图conductance固定为1/rest_edge_length，没有smoothing strength、参数sweep、目标姿态拟合、人工刷权重或自动搜索。固定boundary原R，每点S保留，其他所有骨骼项原值不变，R限定[0,1]。mesh/topology/Basis/rest/21 bones/Action/corrective/driver均保持。唯一文件 `{P['candidate']['path']}`，SHA256 `{P['candidate']['sha256']}`，重新打开验证通过。

梯度结果必须区分三个口径：

|口径|Before|Probe|解释|
|---|---|---|---|
|F130原8边 pair ratio-gradient均值|{old.mean():.8f}/mm|{new.mean():.8f}/mm|下降{reduction*100:.2f}%；7/8下降，1/8上升|
|全部ROI边 pair ratio-gradient均值|{P['ROI_ratio_gradient_before']['mean_per_mm']:.8f}/mm|{P['ROI_ratio_gradient_after']['mean_per_mm']:.8f}/mm|没有下降；固定边界可保留/重分配陡变|
|全部ROI边最大 pair ratio-gradient|{P['ROI_ratio_gradient_before']['max_per_mm']:.8f}/mm|{P['ROI_ratio_gradient_after']['max_per_mm']:.8f}/mm|没有下降|
|原8边完整向量L1差均值|0.48431547|0.42803863|仅下降11.62%，被固定项的主要差仍在|

Q5的YES只指本轮预先选定主带的pair ratio-gradient，不能被解读为整个ROI/完整weight-vector transition已被有效重建。单一harmonic候选未能形成“实际主导的完整梯度已经被消除”的对照，因此也不能将没有视觉收益解释为所有静态weights都不可能。

普通可见结果：F130两指定视角仍保留主阶梯深折，没有自然很多；F127/F160/F205也没有一致明显改善。F110/F176保持平滑，未见新bulge/flap/hard shelf或明显palm-volume distortion。这里只判六帧，不虚构完整7秒验证。旧approved corrective在六帧都自然求值0.0，未强制ON/OFF。候选原Basis/rest完全不变，ZERO求值最大float差{P['ZERO_existing_positions_max_difference_mm']:.9f}mm，恢复自身ZERO误差0mm；S误差{P['S_preservation_max_abs_error']:.9g}，权重和范围{P['normalized_sum_range']}。

局部表面差只用于确认干预发生，不作为改善分数。六帧ROI最大差依次为'''+', '.join(f"F{r['frame']} {r['surface_difference_max_mm']:.4f}mm" for r in P['rows'])+'''. 三张证据PNG为 sensitivity、F130 pair-field对比、六帧对比；review页面可以查看同帧同相机原图。没有第二套候选，没有开启其它influence实验。

结论边界：本轮支持“仅重构WRIST/THUMB比例的唯一probe未解决blocker”。本轮既未证明完整静态weight field可解决，也未证明21-bone deformation DOF不足。由于直接观察到主要固定influence梯度，A/B因果隔离条件不成立，最终选INSUFFICIENT_EVIDENCE。资产/求值/干预控制PASS与因果隔离FAIL分别记录在 CAUSAL_DISCRIMINATION_CONTROL_R1.json，避免混淆。等待Human决定；不自动扩展研究或启动helper。

冻结fallback、上一阶段candidate/audit、生产pointer与sample输入哈希均在结束复核。未move pointer、未promotion、未正式weight rebuild、未新增helper/cage/corrective、未开始左手或Web。未执行hidden crossing、normal-dot、R3、true-cap、2127-edge或逐顶点大型audit。完整手部位置快照已缩减为234节点ROI记录。

STOP — HUMAN REVIEW。
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Skinning field vs DOF · R1</title><style>body{margin:0;background:#101820;color:#e5edf5;font:16px/1.6 system-ui}main{max-width:1280px;margin:auto;padding:24px}h1{font-size:26px}h2{font-size:22px}.banner{padding:16px;background:#33271e;border:1px solid #c79162;border-radius:9px}.controls{position:sticky;top:0;z-index:2;background:#182b39;padding:12px;margin:22px 0}select{font-size:16px;padding:8px;background:#294353;color:white;border:1px solid #65849a;border-radius:5px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}.triple{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}figure{margin:0}img{display:block;width:100%}figcaption{background:#223747;padding:6px}.hint{color:#b7c8d6}a{color:#93cdff}section{margin-top:26px;border-top:1px solid #3c5160;padding-top:12px}table{width:100%;border-collapse:collapse}td,th{padding:7px;border:1px solid #465d6c;vertical-align:top}details{margin-top:15px;padding:10px;background:#1b2c38}</style><main><h1>RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1</h1><div class="banner"><b>FINAL_DIAGNOSIS = INSUFFICIENT_EVIDENCE · STOP — HUMAN REVIEW</b><p>唯一静态pair-field probe未明显改善F130。主带ratio-gradient下降34.8%，但WRIST/THUMB只覆盖完整向量差9%–35%，主要固定INDEX项仍在。资产与干预控制通过；用于“全部静态weight field vs 21-bone DOF”的因果隔离未成立。</p></div><p>冻结 fallback 保持原SHA256；LEVEL_1_TOPOLOGY_ROUTE=CLOSED。没有第二份候选或新增 deformation layer。</p>
<div class="controls"><label for="frameSelect">帧 </label><select id="frameSelect"><option value="130">F130 · PEAK</option><option value="110">F110 · SMOOTH</option><option value="127">F127 · FOLDED</option><option value="160">F160 · FOLDED</option><option value="176">F176 · RECOVERY</option><option value="205">F205 · FOLDED</option></select> <label for="modeSelect">对比 </label><select id="modeSelect"><option value="FIELD">ONE harmonic weight-field probe</option><option value="SENSITIVITY">固定 ±0.02 sensitivity</option></select></div><p id="frameNote"></p><div id="matchedImages"></div>
<section><h2>Q1–Q9</h2><table><thead><tr><th>题</th><th>回答</th><th>范围</th></tr></thead><tbody>QA</tbody></table></section>
<section><h2>少量证据</h2><details><summary>Weight sensitivity · 两方向与六帧response</summary><a href="EVIDENCE_WEIGHT_SENSITIVITY_R1.png" target="_blank"><img src="EVIDENCE_WEIGHT_SENSITIVITY_R1.png" alt="Weight sensitivity evidence"></a></details><details><summary>F130 weight-field probe</summary><a href="EVIDENCE_F130_WEIGHT_FIELD_PROBE.png" target="_blank"><img src="EVIDENCE_F130_WEIGHT_FIELD_PROBE.png" alt="F130 weight-field probe"></a></details><details><summary>六帧 weight-field probe</summary><a href="EVIDENCE_SIX_FRAMES_WEIGHT_FIELD_PROBE.png" target="_blank"><img src="EVIDENCE_SIX_FRAMES_WEIGHT_FIELD_PROBE.png" alt="Six frames weight-field probe"></a></details></section>
<section><p><a href="RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_REPORT.md">完整报告</a> · <a href="RIGHT_HAND_FIRST_WEB_SKINNING_FIELD_VS_DOF_DIAGNOSIS_R1_STATUS.json">状态</a> · <a href="RIGHT_HAND_FIRST_WEB_WEIGHT_FIELD_PROBE_R1.blend">ONE DESIGN_ONLY candidate</a></p><p class="hint">现有blocker仍OPEN。没有将“单一pair field失败”当成“所有静态weights失败”；等待Human决策。</p></section>
<script>const notes=NOTES;function update(){const f=document.querySelector('#frameSelect').value,m=document.querySelector('#modeSelect').value;document.querySelector('#frameNote').textContent=notes[f];const labels=m==='FIELD'?['BASELINE','WEIGHT_FIELD_PROBE']:['BASELINE','WRIST_TO_THUMB','THUMB_TO_WRIST'];document.querySelector('#matchedImages').innerHTML=['FIRST_WEB_OBLIQUE','PALMAR_THENAR_CLOSE'].map(v=>`<div><h2>${v}</h2><div class="${labels.length===2?'pair':'triple'}">${labels.map(l=>{const path=`renders/${l}__F${f.padStart(3,'0')}__${v}.png`;return `<figure><figcaption>${l}</figcaption><a href="${path}" target="_blank"><img src="${path}" alt="${l} F${f} ${v}"></a></figure>`}).join('')}</div></div>`).join('')}document.querySelector('#frameSelect').addEventListener('change',update);document.querySelector('#modeSelect').addEventListener('change',update);update();</script></main></html>'''
scope={'Q1':'空间关联，未证明主要贡献','Q2':'response proxy混合；不等于明显可见冲突','Q3':'没有证明明显破坏','Q4':'仅一份，固定harmonic定义','Q5':'YES仅主带R均值−34.8%；ROI整体均值/最大值未降','Q6':'阶梯深折保留','Q7':'无一致明显改善','Q8':'两个control仍平滑','Q9':'实际完整gradient隔离控制未成立'}
html=html.replace('NOTES',json.dumps(notes,ensure_ascii=False)).replace('QA',''.join(f'<tr><td>{k} · {questions[k]}</td><td><b>{Q[k]}</b></td><td>{scope[k]}</td></tr>' for k in Q))
(OUT/'review.html').write_text(html,encoding='utf-8')
html=html.replace('h1{font-size:26px}','h1{font-size:26px;overflow-wrap:anywhere}')
(OUT/'review.html').write_text(html,encoding='utf-8')
print('CAUSAL_REPORT_REVIEW_READY',status['FINAL_DIAGNOSIS'])
