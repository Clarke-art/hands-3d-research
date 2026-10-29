import json,hashlib
from pathlib import Path
import numpy as np
O=Path(__file__).resolve().parent;F=json.loads((O/'STATIC_POSE_FEASIBILITY.json').read_text());D=json.loads((O/'SOURCE_POSE_COLLISION_DIAGNOSES.json').read_text());SRC=json.loads((O/'SOURCE_POSES.json').read_text());META=json.loads((O/'SKIN_MODEL_META.json').read_text());RAW=np.load(O/'SKIN_MODEL.npz');P=json.loads((O/'POLICY_LOCK.json').read_text());SHOTS=json.loads((O/'STILL_MANIFEST.json').read_text());method=json.loads((O/'COLLISION_METHOD_TESTS.json').read_text());PAR=json.loads((O/'SKIN_PROXY_PARITY.json').read_text())
def doc(n,s):(O/n).write_text(s.rstrip()+'\n',encoding='utf8')
def chosen(r):return next(a for a in r['attempts'] if a['scene']==r['selected_scene'])
initial=next(r for r in D if r['label']=='C01_INITIAL')['measurement'];approved1=next(r for r in D if r['label']=='APPROVED_R1')['measurement'];approved2=next(r for r in D if r['label']=='APPROVED_R2')['measurement'];w=RAW['rest_matrices'][META['names'].index('WRIST_R'),:3,3];wrist={r['label']:(np.array(r['rig_world'])@np.r_[w,1])[:3]*1000 for r in SRC};ROOT=O.parent/'hands';TL=json.loads(Path(P['source_input']['timeline']).read_text());held=[n['note_id'] for n in TL['notes'] if n['hand']=='R' and n['note_on']<=1.914284<n['note_off']]
doc('COLLISION_METHOD_VALIDATION.md',f'''# 真实皮肤碰撞方法验证 — R1

任务PIANO_HAND_SKIN_COLLISION_STATIC_FEASIBILITY_R1，2026-10-12 Asia/Shanghai。方法状态：**VALIDATED_FOR_STATIC_SCREEN**。最终实验状态STATIC_FEASIBILITY_PARTIAL；可信检测不等于所有姿态可行。

## 几何与共同坐标系

读取正式冻结RIGHT HAND R2、实际权重与修正形状，3300顶点、3298原面，Blender原网格实际三角化为6596三角面。始终使用依赖图求值后的deformed mesh，转为世界坐标；骨端/pad仅作为辅助指标。

当前琴键状态来自原Action采样，不将按下键假设为静止。每个实际凸键几何件按真实hinge/press axis/pivot与当前角度变换到同一世界系；88键全部参与验收。此前几何核对误差约0.000022mm，未改键宽、键高或尺寸。PRESS和未PRESS的校准均做了坐标往返验证。

## 键面接触与键体侵入分开

真实指腹为固定rest语义指区内、距离原pad16mm的皮肤足迹。将其三角面裁剪到实际playable top polygon，以面/边与当前键面相交确定触点。最低顶点离键并不等于整个皮肤面离键。本轮记录三种独立数值：pad距离、真正表面接触距离、最低有符号面高度。

若指腹三角面与键面有合法触点，最小表面距离是0；最低有符号高度可能为负，它描述相对top的下探，不能拿它冒充接触距离或直接代替实体侵入深度。接触面积是±0.05mm几何薄层内投影面积，**不是软组织受力/压缩面积**。

键体侵入同时检查全部顶点和BVH检测到的相交三角面。对相交手部三角面，在实际凸键体内部精确求三角面上的最大最小支持面距离：将三角面重心坐标和深度变量构成3变量线性多面体，枚举顶点。由此能抓到“所有顶点都在键外，面内部却切入”的漏报。实际见证点、三角面ID和深度都保留。

每个命中都标明目标键/非目标键。目标键允许数值接触容差；目标键过深侵入独立FAIL。非目标键没有排除列表，掌根/指蹼也不能从键体检测中删除。

## 手指互穿与自然连接

原始语义权重按三角面取平均；某指总权重>0.55的面归属该指，混合掌根/指蹼面保留为不确定连接区。它们只不参与跨指归属统计，仍完整参与琴键碰撞。五指两两BVH比较真实三角面。

排除仅依据**原始网格拓扑**：共享顶点/直接拓扑相邻的连续面不能被误认作两指互穿。没有按世界距离随意去掉交叉，也没有为了PASS剔除问题琴键。原始及排除后的相交计数分别保留。

相交三角面对数表示表面交叉，不能换算成毫米或体积；本轮self_penetration_depth_mm留null。最小间隙采用顶点到对侧BVH三角面的采样，交叉时为0；它不是穷尽edge-edge距离，也不是连续动作安全余量。S2中/无名指采样间隙约0.138mm，需Human特别复核；没有把该数值伪称为充足动态余量。

## 可信性校准

COLLISION_METHOD_TESTS.json保留原始结果：

- 无遮挡真实皮肤fixture：只为检测校准平移，88键无碰撞；不是求解候选，也不是把手掌抬高获得PASS。
- 同一真实拇指皮肤在实际白键上的3mm悬空、切触、1mm侵入，分别在未按压和按压状态验证：悬空无接触，切触有面上触点/近接触面积，侵入正确报约1mm。
- 独立三角面：分离为0交叉，已知交叉检出；连续共享边拓扑正确排除。
- 关键漏报fixture：三角面三个顶点都在5mm半边长盒体外，顶点法报0mm；面内部法检出 **5.000mm**，safe/tangent分别0mm。
- 实际C01及批准R1/R2姿态复核：批准姿态没有非目标键侵入或非相邻指面交叉；C01初始的A♯4/C♯5侵入可由顶点及三角面双重确认。

## 求解前固定的验收合同

POLICY_LOCK.json在求解前保存；没有看到结果后放宽。pad水平必须在目标playable region，pad竖向仍使用旧3mm辅助范围，但**不能单独获得PASS**。真实面上接触必须存在、几何接触距离≤0.05mm、近接触面积>0；目标键和非目标区域的最大实体深度各≤0.25mm；排除自然连接后真实指面相交必须0。

数值求解目标采用−0.005mm的微量数值settling offset，事先写入SOLVER_WEIGHT_LOCK；最终仍按实际Blender接触和0.25mm原容差验收，不拿代理得分替代。旧静态合同允许pad+0.5mm/竖向3mm近似，此轮不再将它当作物理贴键证明。

## 数值代理的边界

复用已有冻结Skin实现（线性混合蒙皮＋原first-web driver），实际权重、原mesh与修正形状不变。8组源姿态逐顶点对Blender校准，最大误差{max(x['maximum_vertex_error_mm'] for x in PAR['parity_tests']):.6f}mm。求解器使用全部3300皮肤顶点对键体的约束，以及采样的有向近邻表面互避代理；最终回到真实网格/BVH和面内部验收。

实验证明：代理中pad/顶点看似正确，仍可漏掉三角面内部侵入，因此S1被最终检测否决。该限制已明示，没有继续用不可靠代理指标宣布最终PASS。方法用于本轮静态屏幕门禁；近切触、混合连接区和有限间隙仍保留Human审查，不能证明任意姿态/连续动作零碰撞。
''')
rows=[]
for h in initial['key_hits']:
 bone={}
 for v in h['vertex_ids']:
  n=META['names'][int(np.argmax(RAW['weights'][v]))];bone[n]=bone.get(n,0)+1
 rows.append((h,bone))
ht='| 键 | 主要手指/皮肤 | 顶点侵入mm | 面内部最大侵入mm | 侵入顶点 | 手/键相交三角面对 |\n|---|---|---|---|---|---|\n'+'\n'.join(f"| {h['key'].replace('#','♯')} | {'食指远节/DIP皮肤' if h['midi']==70 else '无名指远节/DIP皮肤'} | {h['maximum_vertex_inside_depth_mm']:.6f} | {h['maximum_triangle_surface_inside_depth_mm']:.6f} | {len(h['vertex_ids'])} | {h['triangle_surface_intersection_pairs']} |" for h,bones in rows)
doc('INITIAL_POSE_COLLISION_DIAGNOSIS.md',f'''# C01初始姿态碰撞诊断 — R1

只读复核C01原失败Action展示时间1.914284秒，音乐时间1.564284秒。此时R06尚未开始；原时间轴中的右手持音为{','.join(held)}。本轮未重编事件或修复连续动作。

## 实际侵入确认

{ht}

两处都有实际求值顶点进入凸键体，并有非相邻手/键三角面交叉和内部见证点。因此不是pad误读、坐标系不一致、琴键静止高度假设或手指根连接导致的伪碰撞。最大面侵入比旧顶点结果略大，是更完整检测带来的差异，不能把两指标混称同一个深度。

侵入顶点主要权重分别属于INDEX_DIP_R（5点）和RING_DIP_R（2点），即食指/无名指远节指腹/侧面附近；具体顶点与三角面ID、世界见证点在SOURCE_POSE_COLLISION_DIAGNOSES.json。按最强骨权重定位是工程皮肤分区，不是组织学边界。

## 与批准静态姿态对照

批准R1/R2：当前方法下非目标键侵入0、非相邻指面相交0。C01初始却已碰撞，说明“起点安全”未由上一轮规划建立；没有修改或撤销批准静态姿态。

实际腕点（毫米）：

| 状态 | X | Y | Z |
|---|---|---|---|
| C01初始 | {wrist['C01_INITIAL'][0]:.3f} | {wrist['C01_INITIAL'][1]:.3f} | {wrist['C01_INITIAL'][2]:.3f} |
| 批准R1/R2 | {wrist['APPROVED_R1'][0]:.3f} | {wrist['APPROVED_R1'][1]:.3f} | {wrist['APPROVED_R1'][2]:.3f} |

C01初始比批准姿态向低键侧约87.840mm，腕点低约4.166mm，手指控制也不同。这些差异与侵入相关，但本轮没有靠抬腕的反事实试验去宣称唯一因果。新S2在记录的更低腕高、原自由度内仍能找到安全触键，说明单一腕高不足以解释全部问题。

## 触键目标的另一项区别

批准R2原目标F♯5中指的真实指腹距键约{approved2['contact']['true_pulp_min_signed_gap_mm']:.6f}mm，面上接触0、几何近接触面积0。它符合历史+0.5mm近似目标/3mm工程范围，但在本轮更严格的真实接触合同中属于hover。此结论只区分两轮验证范围，不改其原Human批准身份。

新S2真实接触时pad仍可高于键面约0.880mm，S3真实接触时pad约1.575mm；可见pad位置并不唯一代表整个指腹触点。不能统一给pad下降0.5mm就保证接触/不穿键。

## 原因判断

- **初始姿态不安全：确认。** 两个真实皮肤侵入，批准基准没有同类侵入。
- **现有运动目标缺完整皮肤约束：有直接支持。** 上轮只用pad/关节代理；本轮增加完整皮肤键体及指面互避后，S2/S3/S4可以找到合格静态姿态。
- **触键目标与皮肤足迹不匹配：确认存在。** 历史pad+0.5mm可以悬空；仅最小顶点靠近键面也可漏掉三角面切入。
- **掌腕/五指协调或范围不足：S1仍有条件性问题。** 两组初始化均未满足全部门禁，但不能证明所有允许控制均无解。
- **冻结Rig必须改结构：无证据。** 已有三个实际通过例，未新增任何骨骼或自由度。
- **误报：本初始两处不支持误报解释。** 自然连接排除与已知接触/侵入校准通过。

本轮不生成连续动画。R05持音未纳入上一轮R06—R14求解任务，是入口上下文不完整的一个已识别限制，仍需在未来单独的连续规划任务中处理。
''')
table='| 测试 | 实际指/键 | 状态 | pad距键mm | 真表面接触距mm | 目标实体侵入mm | 非目标/非指腹最大侵入mm | 指面相交 | 近接触面积mm² |\n|---|---|---|---|---|---|---|---|---|\n'
for r in F['tests']:
 a=chosen(r);g=a['actual_geometry'];ct=g['contact'];status='PASS静态门禁/待Human' if r['status']=='PASS_STATIC_SCREEN_HUMAN_PENDING' else 'FAIL两组初始化' if r['test']=='S1' else '仅探索，前置条件不成立'
 table+=f"| {r['test']} | {r['finger']}指/{META['key_table'][r['midi']-21]['note_name'].replace('#','♯')} | {status} | {ct['pad_gap_mm']:.6f} | {ct['true_pulp_surface_contact_distance_mm']:.6f} | {g['target_key_max_depth_mm']:.6f} | {g['wrong_key_or_nonpulp_max_depth_mm']:.6f} | {g['nonadjacent_self_triangle_pairs']} | {ct['near_contact_projected_area_mm2']:.6f} |\n"
visual='\n\n'.join(f"### {s['test']} · {s['view']}\n\n{s['caption']}。{'红色引线起点是真实侵入见证点；标记抬高15mm仅为可见，不代表移动手部。' if s['test'] in ['INITIAL','S1'] else '真实静态求值网格。'}\n\n![{s['test']} {s['view']}]({Path(s['file']).as_posix()})" for s in SHOTS)
doc('HUMAN_VISUAL_REVIEW.md',f'''# Human静态视觉复核 — R1

状态STATIC_FEASIBILITY_PARTIAL，全部DESIGN_PROVISIONAL。仅8张1280×720静帧，未制作视频或PNG序列。已有左手若在画面边缘，仅为原场景参考，不是本轮新求解。

{table}

## 审查要点

- INITIAL红色位置：食指远节/A♯4、无名指远节/C♯5真实侵入。顶点深度约1.590/0.666mm，面内部深度约1.740/0.842mm。
- S1图采用第一次C01初始化，目标G4面侵入0.549mm，最小顶点看似尚有+0.006mm间隙，却不是合法整体接触。第二批准R1初始化也未过，目标侵入0.278mm；两组都保留在Blend和JSON。拇指白键前缘/侧缘及三角面3869见证点为重点。
- S2 E5中指：实际触点在键面，非目标侵入0、指面交叉0；但中/无名指采样间隙约0.138mm，是微小安全余量，须侧斜/Blend复核，不据此推断动态安全。
- S3 C5拇指：目标内数值侵入约0.071mm，在事前0.25mm合同内；真实面上接触存在，不能误用pad高约1.575mm判它悬空。此解达到迭代上限未宣称收敛，最终依据真实几何门禁。
- S4 F♯5无名指：侧斜观察黑键高差，实际触点存在，非目标侵入/指面交叉0。近接触面积不是力学承载面积。
- S5未列图：在代理检查通过后先算过，但更严格面检测使S1失败，故只保留探索数据，不算正式前置通过后的八度验证。

诊断Blend：[SKIN_COLLISION_STATIC_DIAGNOSTIC_R1.blend]({Path(F['diagnostic_blend']).as_posix()})。场景S1_INIT_1/2、S2_INIT_1/2、S3_INIT_1/2、S4_INIT_1/2、S5_INIT_1/2均是STATIC_ONLY：当前按压键状态取自原Action，各实验场景对象动画已解绑、无新关键帧。原动画datablock可能作为继承参考存在，不代表本轮生成了连续动画。不要通过播放这些静态场景推断动作可行。

{visual}

**STOP — HUMAN REVIEW。** 不自动进入连续动作求解。
''')
doc('FINAL_RECOMMENDATION.md',f'''# 最终建议 — PIANO_HAND_SKIN_COLLISION_STATIC_FEASIBILITY_R1

**STATIC_FEASIBILITY_PARTIAL。** 碰撞方法已校准；冻结Rig的现有自由度能找到真实触键且无超限完整皮肤键体碰撞/非相邻指面互穿的静态例子，但G4拇指＋中指准备E5的联合要求仍未全部通过。本轮没有连续动画或视频。

{table}

## 必答结论

1. **碰撞方法可信吗？** 对本轮静态门禁可信。真实deformed mesh、当前88键状态、共同世界系、拓扑连接排除、真实三角面接触及内部侵入均验证。已知safe/contact/penetration和顶点全外的三角面穿透样例通过。微小间隙、连接分区和静态/动态区别保留Human审查。
2. **C01初始为什么侵入？** 已确认食指/无名指远节实际进入A♯4/C♯5，不是误报。批准R1/R2无同类侵入；C01入口掌根/指部状态不同且约束遗漏完整皮肤。腕点低4.166mm及左移87.840mm是相关差异，不能未经消融就称唯一根因。旧pad近似目标和入口上下文不完整也有证据支持。
3. **至少一组正确接触且无明显皮肤碰撞？** 有，S2/S3/S4真实面上接触距0，非目标最大侵入0、非相邻指面交叉0。S3约0.071mm目标数值侵入仍在事前0.25mm范围，微接触由Human最终审阅。
4. **G4拇指、E5中指、F♯5无名指分别可行吗？** E5中指和F♯5无名指已得到合格静态候选；C5拇指也得到候选。G4＋准备E5的S1两组初始化未过，目标面侵入分别0.549、0.278mm。单独G4的S5探索例显示存在潜力，但因S1未满足前置条件，不能正式宣布S5通过或八度回位可行。
5. **需要新自由度吗？** 对三个通过例不需要：保持原Rig/rest/绑定/权重/厚度，仅用既有整体XY/旋转与20个手指控制。Z在各初始化记录值固定，没有整体抬高逃避。S1没找到合格姿态不能证明需要新骨骼或证明数学无解。
6. **主要障碍是哪一层？** 同时有目标定义与几何约束缺口：pad+0.5mm可悬空，頂点接近/顶点无侵入也可漏掉三角面内部穿透；真正指腹接触、完整皮肤键体和指面互避必须一起判断。当前S1的准备跨度/足迹配合还没建立；连续时序规划不在本轮验证范围。
7. **值得扩展现有联合求解器吗？** 值得先把面级/凸键体内部约束和接触足迹并入现有接口，继续短段静态验证；已有蒙皮代理逐顶点误差不足0.001mm，且现有控制能解出真实静态例，不必先重做Rig或训练模型。不能直接扩展为完整双手动画。
8. **应转向成熟IK/碰撞约束方案吗？** 本轮没有比较外部IK，不能凭名称判断更好。优先保留已验证FK/蒙皮与控制接口，加强真正表面约束；若这一有限改造在后续受控试验仍失败，再评估带碰撞约束的IK。没有证据要求现在替换整套系统。

## 预算及可信边界

新增数值求解总墙钟 **{F['total_numerical_wall_seconds']:.3f}秒**，限600秒；每项恰两组有依据的记录/批准初始化，固定权重、最多28次评估，无随机搜索、不扩大迭代、不重新训练。S1因两组均用完且最终面门禁失败而停止；没有用剩余时间反复改权重或补第三组。不能将此称作冻结Rig绝对不可行。

S5曾在前4项代理初检通过后计算；真实三角面验收发现S1失败，已明确降为探索证据，不计正式通过，未删除或修改计算结果来制造结论。

数值代理只加速求解，最终全部回到Blender实际网格。检测补全抓到了代理漏报并否决S1，没有看到结果后放宽0.25mm容差。接触距离与有符号高度/实体侵入独立记录，没有把−0.074mm高度当作“距键0.074mm”，也没有用pad悬空距离冒充真实接触。

S2中/无名指采样间隙约0.138mm需要Human检查，三个通过例仍为静态技术候选，不能推论连续释放、穿指、自然度或教学通过。新结果全部DESIGN_PROVISIONAL。

源冻结资产、四批准姿态、Stage A/B/C、C01指法、MIDI/音频和上一轮失败Action/证据保持只读。交付一份诊断Blend、8张720p静帧和五项要求文件，无视频或帧序列缓存。

**STOP — HUMAN REVIEW。** 不进入下一轮连续求解、动画或视频。
''')
status=dict(task='PIANO_HAND_SKIN_COLLISION_STATIC_FEASIBILITY_R1',status='STATIC_FEASIBILITY_PARTIAL',collision_method='VALIDATED_FOR_STATIC_SCREEN',passed_formal_tests=['S2','S3','S4'],failed_formal_tests=['S1'],s5='EXPLORATORY_ONLY_PRECONDITION_NOT_MET',numerical_wall_seconds=F['total_numerical_wall_seconds'],max_initializations=2,continuous_motion_generated=False,videos=0,stills=8,authority='DESIGN_PROVISIONAL',stop='STOP — HUMAN REVIEW')
(O/'FINAL_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('STATIC_REPORTS_COMPLETE',status['status'])
