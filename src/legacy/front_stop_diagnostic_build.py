from pathlib import Path
import json, gzip, math, hashlib

W=Path(r'D:\codex one\3D interactive components\piano')
O=Path(__file__).resolve().parent/'canonical_upright_action_key043_front_stop_compatibility_r1'
O.mkdir(exist_ok=True)
E=W/'canonical_upright_action_educational_motion_validation_r1'
C=E/'catcher_attachment'
hashes={}
def source(p):
    p=Path(p); hashes[str(p.relative_to(W))]=hashlib.sha256(p.read_bytes()).hexdigest(); return p
def read(p): return json.loads(source(p).read_text(encoding='utf-8-sig'))
def dump(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def doc(n,s): (O/n).write_text(s.strip()+'\n',encoding='utf-8')

stim=read(W/'canonical_upright_action_b02_representative_installed_pilot_r2/KEY_REPLAY_STIMULUS.json')
manifest=read(W/'v1_2d_cp1/data/key_stick_manifest.json')
key=next(q for q in manifest if q['semanticId']=='KEY_043')
a=stim['key_actions'][0]['full_angle_rad']
design=read(W/'canonical_upright_action_b02_representative_keyboard_interface_r8/REPRESENTATIVE_DESIGN_V1.json')
pad=next(q for q in design['parts'] if q['name']=='R8_KEY_043_FRONT_STOP')
f=read(C/'FIRST_SUBSTANTIVE_NATIVE_FAILURE.json')
identity=read(C/'FIRST_FAILURE_PHYSICAL_IDENTITY_AND_NATIVE_WITNESSES.json')[0]
qa=read(C/'SAVED_REOPEN_QA.json')
source(C/'FIRST_NATIVE_FAILURE_EDU_R1.blend')
assert hashes[str((C/'FIRST_NATIVE_FAILURE_EDU_R1.blend').relative_to(W))]==qa['sha256']
world={}
names={'CP2K1_KEY_043_STICK','R8_KEY_043_FRONT_STOP','R8_FRONT_RAIL'}
for label,p in [('REST',E/'INITIAL_R11_OPERATIVE_WORLD.jsonl.gz'),('FAILURE',C/'FIRST_FAILURE_ALL_OPERATIVE_WORLD.jsonl.gz')]:
    world[label]={}
    with gzip.open(source(p),'rt',encoding='utf-8') as stream:
        for line in stream:
            q=json.loads(line)
            if q['object'] in names:world[label][q['object']]=q
assert world['REST']['R8_KEY_043_FRONT_STOP']==world['FAILURE']['R8_KEY_043_FRONT_STOP']
assert world['REST']['R8_FRONT_RAIL']==world['FAILURE']['R8_FRONT_RAIL']
rows=[json.loads(s) for s in source(C/'NATIVE_SAMPLES.jsonl').read_text().splitlines()]
samples=[{'frame':q['frame'],'input':q['native_key_inputs'][0],'front_gaps':q['support']['front_stop_actual_vertical_gaps']} for q in rows if .57<q['native_key_inputs'][0]['actual_fraction']<.61]
def gap(u,y):return (math.tan(a*u)-math.tan(a))*(y+150)-2
def dip(u):return 85.0723147392273*math.sin(a*u)+7.5*(1-math.cos(a*u))
res=max(abs(q['gap_mm']-gap(f['native_key_inputs'][0]['actual_fraction'],q['XY_mm'][1])) for q in f['support']['front_stop_actual_vertical_gaps'])
calc={'method':'Closed-form evaluation of archived dimensions only; no bpy, solver, scene, frame or new native state',
 'full_angle_rad':a,'nominal_dip_mm':6,'front_reference_full_dip_mm':dip(1),
 'remaining_front_reference_dip_from_saved_failure_mm':dip(1)-f['native_key_inputs'][0]['actual_front_dip_mm'],
 'ideal_first_edge_contact_fraction':math.atan(math.tan(a)-2/69)/a,
 'exact_native_continuous_onset':'NOT_LOCALIZED', 'native_sample_bracket':[.575,.6],
 'assumed_analytical_gap_reporting_envelope_mm':.001,'envelope_is_not_manufacturing_or_material_tolerance':True,
 'max_formula_vs_saved_60pct_gap_residual_mm':res,
 'required_vertical_compression_at_full_angle_mm':2,'required_normal_separation_mm':2*math.cos(a),
 'required_full_compression_strain_at_pad_y_ends':[2/(710+math.tan(a)*(y+150)+2-702) for y in [-227,-219]],
 'rows':[{'fraction':u,'front_dip_mm':dip(u),'gaps_mm':{str(y):gap(u,y) for y in [-227,-226,-223,-220,-219]}} for u in [0,.575,.6,1]],
 'rigid_geometry_full_travel':'INCOMPATIBLE','physical_felt_capacity':'UNKNOWN'}
assert res<.001
dump('READ_ONLY_GEOMETRY_AND_CALCULATION.json',{'source_design_pad':pad,'key_manifest':key,'saved_world':world,'saved_samples':samples,'calculation':calc,'saved_failure_reopen_historical_QA':qa,'saved_identity':{n:{k:v[k] for k in ['parent','properties','constraints','modifiers']} for n,v in identity['identity'].items()}})
for rel in ['canonical_upright_action_b02_representative_keyboard_interface_r8/declare_design.py','canonical_upright_action_b02_keyboard_interface_correction_r9/seal_v2.py','canonical_upright_action_b02_keyboard_interface_gate_closure_r10/prebuild.py','canonical_upright_action_b02_cp2b_rear_key_role_closure_r11/common.py','canonical_upright_action_educational_motion_validation_r1/STATUS.json','canonical_upright_action_educational_motion_validation_r1/FIRST_PHYSICAL_FAILURE_RECONCILIATION.json','canonical_upright_action_educational_motion_validation_r1/catcher_attachment/run_native.py','v1_2e_cp1r20/evidence/authority/kawai_p010.png','research/representative_upright_scientific_r2/extracted/B01_masoudi_thesis/p118.txt','research/representative_upright_scientific_r2/extracted/B01_masoudi_thesis/p126.txt']:
    source(W/rel)

doc('FRONT_STOP_MECHANICAL_ROLE.md',r'''
# KEY043 前止挡机械职责

2026-10-11 · FRONT_STOP_COMPATIBILITY_DIAGNOSTIC_ONLY · STOP — HUMAN REVIEW

基线：SCIENTIFICALLY_CONSTRAINED_REPRESENTATIVE_INSTALLED_INTERFACE。仅读取历史记录和解析计算；未启动 Blender，未执行历史脚本，未创建新姿态。

## 结论

FRONT_STOP_ROLE = CONFIRMED。R8_KEY_043_FRONT_STOP 是前端按下行程的有限柔性下止挡，承担终程缓冲和限位的预期职责。它不是 REST 后支承、平衡支点、Capstan 传动件，也不是把键杆往上推回 REST 的已验证回弹机构。

预期接触是 CP2K1_KEY_043_STICK 底面与止挡斜顶面，传力路径为键杆→毛毡垫→R8_FRONT_RAIL→保留 keybed。REST 时顶面与键杆分离；按下时从靠支点的后缘开始接近并接触。当前失败是后缘区域实际实体相交。

## 模型与原始意图

R8/declare_design.py 第65–66行把顶面直接定义为完整转角下键杆底面再向上加2 mm；function=FINITE_FRONT_COMPLIANT_DOWNSTOP，material=REPRESENTATIVE_FELT，unloaded_reserve_mm=2。P01.stop_limit 明确声明仅解析容积余量，完整原生键程、恢复力及 felt law 未合格。

这是明确的 Representative Design 意图，不是已验证的2 mm材料压缩能力。R9派生保留KEY043止挡；保存的R11 REST与教育失败现场中，其顶点、拓扑和矩阵逐项一致。安装没有在这次按键中漂移。

失败身份记录显示该止挡无父级、无约束、无modifier；保存的实际几何保持不变。材料名称并没有提供形变、力—位移、迟滞、压实上限或回弹模型。现有碰撞检查实际把它作为未变形的有限实体处理。

## 科学来源与适用边界

1. [Kawai Vertical Piano Regulation Manual](https://portal.kawaius.com/api/media/file/Kawai_Upright_Piano_Regulation_Manual_EN.pdf)，项目已有原件 v1_2c1a_candidate/references/S06_regulation.pdf；直接检查已有渲染 v1_2e_cp1r20/evidence/authority/kawai_p010.png，印刷页10：通过纸垫片调整白键下沉，并强调一致按压力。支持“止挡堆叠高度和受力条件决定有效键程”。本轮在线PDF截图获取失败，证据采用本地已有页图。其10.3 mm白键数值不适用于KEY043黑键，不引入项目参数。
2. [Baldwin US4127051A](https://patents.google.com/patent/US4127051A/en)，背景说明：前轨是按键下止挡，键底与轨间的毛毡垫用于缓冲消声，纸垫调整键程。仅使用传统键框原理；专利主体是三角琴改进结构，不把其结构尺寸或新结构移植成立式琴权威。
3. [Howard Piano Industries：Front Rail Felt Punchings](https://www.howardpianoindustries.com/piano-front-rail-felt-punchings/)，供应商第一手材料资料：firm felt、纸/卡垫调键程，多种厚度，并提示旧毛毡压实。仅支持材料与维修形式；不提供本垫的载荷—压缩曲线或可逆2 mm能力，产品厚度不作为本项目尺寸标准。
4. [Masoudi 立式琴机械研究论文](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/8b1f5033-3619-46b4-8083-833cbd07e4f5/content)，项目已有 extracted/B01_masoudi_thesis/p118.txt（印刷94页）Table4.2：front rail punching为key-ground接触2，rest rail与balance rail为不同接触；同页说明毛毡压缩非线性及迟滞。p126.txt（印刷102页）说明调节前垫可改变key dip。只用于接触拓扑和建模要求；不能把论文锤毡试验或其原型尺寸直接用于本前垫。

矩形8×8 mm、斜顶、2 mm余量、当前坐标均是工程假设。真实前轨常见的是带孔毛毡垫配合导向销和纸垫，不意味着本代表性方垫必须复制OEM形状；也不能据名称授予任意网格重叠豁免。
''')

doc('KEY043_CONTACT_TIMING_AND_GEOMETRY.md',r'''
# KEY043 接触时机与完整键程兼容性

## 数据来源与坐标

数值来源：R8 REPRESENTATIVE_DESIGN_V1.json与declare_design.py；R2 KEY_REPLAY_STIMULUS.json；v1_2d_cp1/data/key_stick_manifest.json；教育验证根目录INITIAL_R11_OPERATIVE_WORLD.jsonl.gz；最终catcher_attachment目录的失败world、NATIVE_SAMPLES、FIRST_SUBSTANTIVE_NATIVE_FAILURE及身份记录。根目录早期失败不能替代最终catcher_attachment物理失败。最终Blend历史重开QA为frame25、6216网格、world误差0；本轮核对该Blend SHA256与QA一致，未重新打开Blend。

以下为Blender世界坐标毫米：X横向，+Y向键后/action，+Z向上，前方为负Y；旋转绕世界X轴。REST角为0。支点名义坐标(-19.822327,-150,710)，键杆底面保存值709.999979，顶面725.000024；截面约9×15 mm，平面内有斜向布局。frontCenter=(-23.600001,-235.072315,717.5)不是底面点。

| 构件/参数 | 保存值，mm |
|---|---|
| 止挡X | -27.063923 … -19.063924 |
| 止挡Y | -226.999998 … -218.999997 |
| 止挡底面 | 702.000022 |
| 止挡前缘顶面Y=-227 | 706.555784 |
| 止挡后缘顶面Y=-219 | 707.121432 |
| 垫厚，前缘/后缘 | 4.555762 / 5.121410 |
| 前轨 | X=-40.149964…30.500000；Y=-229.000002…-216.999993；Z=700.000048…702.000022 |

止挡矩阵为单位阵，无旋转对象变换；斜度编码于网格。顶面向后升高，名义斜率tan(0.0705868344763)，约4.04433°。顶面比完整键程的键底平面高2 mm，底面稳坐前轨；不是已发现的轨底脱座或整件误移。

## 冻结键程定义

KEY043 nominal dip=6.0 mm，arm=85.072314739 mm，full angle α=0.07058683447626896 rad，输入u指角度比例θ=uα，不能把实际下沉严格写成6u。

前端追踪点相对支点高7.5 mm，因此既有观测定义下：

`D(u)=85.072314739 sin(uα)+7.5[1−cos(uα)] mm`。

100%角度的解析前端追踪下沉为6.018677 mm，6 mm是冻结名义dip；差异来自追踪点与角度构造基准，不改变law，不把差异当成本轮新错误。60%保存值3.608644 mm；至100%角度尚余约2.410033 mm（若只减名义6 mm，余2.391356 mm，后者不等于冻结角度的真实追踪余程）。

刚体轨迹：`y'=py+(y0−py)cosθ−(z0−pz)sinθ`，`z'=pz+(y0−py)sinθ+(z0−pz)cosθ`。平底z0=pz在固定世界Y处成为`z_key=710+tanθ(y+150)`。

## 接触记录与解析预测

止挡顶面`z_stop=710+tanα(y+150)+2`。因此名义垂直间隙：

`g(u,y)=[tan(uα)−tanα](y+150)−2 mm`。

| 输入 | 前端下沉（解析mm） | 前缘y=-227间隙 | 后缘y=-219间隙 |
|---|---:|---:|---:|
| REST | 0 | 3.444231 | 2.878597 |
| 57.5% | 3.458095 | 0.317282 | 0.076525 |
| 60% | 3.608640 | 0.181168 | -0.045447 |
| 100%，只读公式外推 | 6.018677 | -2.000000 | -2.000000 |

57.5%是最后通过采样，保存前端下沉3.458142 mm；60%是首个确认失败，frame25，actual fraction=0.60000002849，Wippen=3.707842588°。独立内侧检查y=-220得到-0.017157/-0.017173 mm；y=-226仍有约0.1528 mm间隙。后缘先接触的趋势与原斜面设计一致。

当前原生证据只给出57.5%到60%的采样夹区；碰撞阈值不是精确零接触判定。对名义有限平底/斜顶和覆盖后缘的键杆，解后缘g=0得到解析接触估计u≈59.06855%。这不是新原生测量，不替代“精确连续起始位置未定位”。没有在该位置驱动Blender、加密采样或测试完整键程。

误差：名义公式对60%四个保存间隙的最大差约0.000053 mm，当前前端追踪值差约0.0000044 mm，57.5%追踪值差约0.000047 mm。报告采用±0.001 mm作为保守解析数值包络假设，对接触输入估计约±0.021个百分点（可报告±0.03个百分点）。这不是实际制造公差或获批门禁，不改变原检测阈值。完整键程仍是理想刚体平面外推，未由新原生状态验证。

## 剩余行程要求与判定

保留几何需各接触点垂直变形`c=max(0,-g)`，到完整角度约2.000±0.001 mm；两平行终面间法向距离约1.99502 mm。不能混用方向。前后初厚4.556–5.121 mm对应约43.9%–39.1%垂直压缩，应剩2.556–3.121 mm厚度。60%后缘已需求约0.04545 mm，至终程还需约1.95455 mm；前缘尚未接触，最终也需约2 mm。并非整个垫一开始统一下降2 mm。

有正的剩余厚度，只证明未在理想解析模型中碰到硬轨，不能证明材料力学可行。前端剩余2.410 mm、局部最大所需压缩2 mm、BVH内部采样0.04546 mm是三种量。

当前未变形网格与完整冻结角度不兼容已经成立，FULL_KEY_TRAVEL_COMPATIBILITY=INCOMPATIBLE仅指这个实现。60%接触可由原设计的2 mm余量解释，不能认定它已科学合理，也不能断言实际钢琴会卡死。CONTACT_TIMING_COMPATIBILITY=UNKNOWN（物理合理性）；INSTALLATION_GEOMETRY_CAUSE=UNKNOWN（未证明错误安装或尺寸必须改）。是否能在合理按压力下达到终程并恢复REST，没有本垫材料证据。
''')

doc('FELT_VS_INSTALLATION_ROUTE.md',r'''
# 有限毛毡接触与安装几何路线比较

唯一当前推荐：RECOMMENDED_ROUTE=NEED_MORE_AUTHORITY。

已确定直接原因：一个按完整键程再加2 mm未压缩余量设计的柔性下止挡，被现有执行链作为未变形实体检测；继续规定角度会发生真实网格相交。尚未确定的是这2 mm是否有合理材料依据，或应由重新调节有效工作面消除大部分需求。这不是可以用改碰撞阈值解决的问题。

| 比较项 | A：BOUNDED_REPRESENTATIVE_FELT_CONTACT | B：FRONT_STOP_INSTALLATION_GEOMETRY_CORRECTION |
|---|---|---|
| 已有依据 | 最符合R8原始柔性意图；真实毛毡接触及非线性有依据 | 真实维修通过前垫堆叠调节有效键程，有科学依据 |
| 关键缺口 | 当前厚度/面积/边界下2 mm可逆压缩、合理力、迟滞、极限、残余变形未知 | 无证据证明安装偏移；新工作面需对应哪一受力状态/接触时机尚无权威参数 |
| 条件性最小修改 | 独立实验中仅KEY043垫的有限接触表示与其审查指标；接触以g=0开始，向支承方向压缩，基座固定 | 独立实验中仅KEY043垫顶面/有效厚度；维持底座接头、X/Y覆盖和前轨；优先不移动共用轨 |
| 不可接受做法 | 任意相交豁免；用BVH深度当压缩；凭空认定2 mm上限；把锤毡参数移植为本垫数据 | 把整垫向下平移2 mm导致底座插入轨；只为PASS削掉接触功能；未经依据设零压缩终止 |
| 对其它机构风险 | 引入接触表达/释放路径，验证范围较大；可能错误宣称动态力学 | 局部网格范围较小，但改变接触时间、载荷和终止条件；移动共用轨会波及五站，禁止 |
| 可否立即选择实施 | 否 | 否 |

几何上可写一个设计族：`z_new_top=z_key_full+c_authorized(y)`，而`c_authorized`必须先有材料或明确受力状态的工程依据。现状是c=2 mm。令c=0并减掉2 mm顶层会获得理想刚性终面，但这只是几何条件式，不能据此宣布真实毛毡接触合格，也不是本轮推荐执行尺寸。

A需要规定压缩方向（建议研究沿固定基座+Z厚度方向；按压位移为−Z，不能未经依据等同纯法向压缩）、局部接触范围、压缩上限和下方硬轨边界；最终停止必须与冻结终角和获批受力条件一致，不能由无限规定角度压穿。释放应在接触解除后恢复原顶面，并检查永久压实/迟滞假设。仅接触运动示意不能升级回弹动力学资格。

B的直接运动学影响：若支点、键杆、law、Capstan/P39及Wippen求解链完全不变，同一角度下它们几何上应不变；但更晚/更早止挡接触会改变实际可达行程和保持/释放的接触状态，仍须独立验证。垫X/Y有限接触覆盖须保留；底面必须贴合固定前轨。KEY042/044/045/046布局不得改动，不能凭KEY043结果外推相邻音符。B02正式安装和冻结资产均不得覆盖。

## 分类保留

- 真正机械实体干涉：本轮确认的是当前未变形键杆/止挡有限体积交叠，历史FAIL_STOP有效。
- 合理柔性接触但表达缺失：具备原始设计意图与一般原理；“合理的2 mm压缩”未成立。
- 安装位置不兼容：对完全不变形实体与完整角度而言成立；物理安装错误作为根因未确认。
- 数值残差：0.045460 mm内部采样与两项负垂直间隙构成独立证据，不能归为纯浮点误差。BVH采样深度也不是精确最大穿入或材料压缩测量。
- 静态支承工程WARN：保留原分类，不重审。
- 未确定：材料可逆容量、合理接触时机、受力终点、真实回弹。

科学证据足以确认接触角色，不能在A/B间建立唯一充分的尺寸或材料实施依据。因此不强行选A，也不凭39%–44%数字断言所有毛毡都不可能压缩。停止扩大研究，提交Human选择补充材料权威或受力状态设计基准。
''')

doc('MINIMAL_NEXT_AUTHORIZATION.md',r'''
# 最小下一阶段授权与验证设计（未执行）

本轮推荐NEED_MORE_AUTHORITY。当前可批准的唯一下一步是KEY043前垫“接触工作条件权威补全”；不是批准完整运动恢复，也不是把A/B都授权尝试。

## 前置Human决定

需Human批准一个与本安装相关的材料/结构依据：选定前轨毛毡的厚度、有效接触面积、支承方式、按压力或可接受的准静态受力状态、可逆压缩曲线/允许包络、最大压缩及回弹/永久压实边界。可用可信材料技术资料、专业测量或经明确论证的Representative工程参数；不能仅填一个2 mm数值。

据此形成单一方案供Human再次审查：若当前2 mm需求被支持，才申请A；若允许压缩较小并有终程受力基准，才申请B的具体工作面修订。若两者仍未知，继续BLOCKED。需单独授权非冻结KEY043实验副本的具体对象/参数，以及通过旧失败位置后的键程测试。此文不构成授权。

## 唯一最小验证流程

1. 冻结引用：将R11来源、R12历史FAIL_STOP、教育catcher_attachment失败Blend/world/STATUS及193 drivers、18条已批transfer修复的现有manifest作为只读输入；新目录、新派生实验版本、新hash清单，绝不覆盖历史文件。
2. 变更白名单：仅该独立副本中的KEY043前垫工作面或获批有限接触表示；两者只按获批单一方案执行。正式B02不改。共同前轨、键杆、支点、Capstan、P39、Wippen、运动law、driver、solver、其它音符网格和Actions保持冻结。若需要改solver等超范围内容，STOP另行审批。
3. 静态门禁先行：REST无新干涉，底面与前轨接头保持，有限覆盖/正剩余厚度/最小承载面满足获批参数，几何哈希差异仅在白名单；键杆与止挡关系不得用全对豁免。所有既有碰撞guard保留；若A需新的合规接触观察器，仅允许获批有限区域、方向和压缩包络，与全局干涉检测并存。
4. 首次接触：在已保存57.5%–60%夹区附近按预先封存的只读几何预测建立实际表面零间隙事件，观察整个有限工作面而不只四个采样点。后续原生取样/括区精化必须获得授权，并以独立有限面距离/体积方法复核；首次未解释干涉即STOP，不边试边调。新方案若改变时机，以其预先封存预测为准，不强迫沿用59.06855%。
5. 剩余完整键程：只有接触门禁通过、且Human明确授权越过旧60%边界，才按预封存的单键序列至100%冻结角度；同步记录实际前端下沉、各接触点压缩/间隙、剩余垫厚、底座接头以及Capstan→P39→Wippen→Jack/Butt→Hammer。不得改角度来绕开失败；必须区分6 mm名义dip和约6.018677 mm追踪点下沉。
6. 保持、释放、REST：在完整角度保持检查无继续穿入或越界压缩；按同一冻结law释放，检查接触解除、获批准静态回弹表示、键杆/Capstan/P39关系及最终REST几何恢复。几何恢复不授予自由飞行、锤击时序、锤弦接触、完整Hammer dynamics或Half-blow19资格。
7. 音符隔离：仅KEY043输入；KEY044/045/其它键及Shared保持0，逐状态比较其输入、关键变换和网格哈希；若出现未授权变化即STOP。验证邻件作为静态真实实体，不删除/隐藏它们以通过。
8. 停止线：新硬实体交叠；未获批区域接触；压缩超过封存上限或出现拉伸“吸附”；底座脱座/硬轨触底；传动方向错误、Capstan/P39失去预期接触；保持/释放无法恢复REST；任何非白名单变化或保护hash变化；任一不能解释的残差。保留第一个失败状态，禁止后续输入、加密和自动重调。只记录并回到HUMAN REVIEW。

通过上述KEY043实验仍不得自动执行KEY044/045、三音交错、B03–B06或88音部署。KEY044/045继续NOT_EXECUTED/BLOCKED_FOR_CONTINUATION，B03–B06继续BLOCKED。

## 本轮Q1–Q13

| 问题 | 答复 |
|---|---|
| Q1真实职责 | 有毛毡缓冲意图的前端下止挡，预期限定最终按键行程 |
| Q2时机合理吗 | 与2 mm余量设计吻合；真实材料/手感合理性UNKNOWN；60%不是精确起点 |
| Q3安装已证实不兼容吗 | 当前不变形网格与完整角度不兼容；安装偏移或物理尺寸错误未证实 |
| Q4正常压缩依据 | 一般毛毡接触有依据；本垫2 mm可逆压缩NOT_ESTABLISHED |
| Q5剩余键程条件 | 保持现状需局部约2 mm总压缩及终止/释放条件；否则需有依据地重设有效工作面 |
| Q6 0.04546 mm分类 | 已确认原生几何相交、柔性意图未实现/未合格；不是纯数值误差，也非实测压缩或金属硬碰撞结论 |
| Q7是否改止挡几何 | 未确定，不能据当前证据授权改 |
| Q8是否加有限柔性表示 | 若保留现有未加载几何则必须有合格有限接触表示；材料参数不足，当前不能实施 |
| Q9哪条科学依据更充分 | A更贴原设计，B有调节原理；两者实施参数均不足，唯一推荐NEED_MORE_AUTHORITY |
| Q10是否改冻结/law/driver | 不需要，也不授权 |
| Q11最小实验 | 先补全KEY043前垫工作条件；独立授权后单键验证首次接触、有限余程、保持、释放与REST |
| Q12阻塞是否保持 | 是，KEY044/045继续不执行，B03–B06 BLOCKED |
| Q13历史资产是否不变 | 是，本轮只有新诊断文档/数据，无机械资产写入；没有全库重复审计 |

STOP — HUMAN REVIEW。要求Human审核源自本轮用户明确的诊断授权边界与资料缺口，而非额外引入的审批流程。
''')

status={'task':'CANONICAL_UPRIGHT_ACTION_KEY043_FRONT_STOP_COMPATIBILITY_R1','date':'2026-10-11','authority':'SCIENTIFICALLY_CONSTRAINED_REPRESENTATIVE_INSTALLED_INTERFACE','scope':'FRONT_STOP_COMPATIBILITY_DIAGNOSTIC_ONLY',
 'FRONT_STOP_ROLE':'CONFIRMED','CONTACT_TIMING_COMPATIBILITY':'UNKNOWN','INSTALLATION_GEOMETRY_CAUSE':'UNKNOWN','FELT_COMPRESSION_REQUIREMENT':'NOT_ESTABLISHED','FULL_KEY_TRAVEL_COMPATIBILITY':'INCOMPATIBLE',
 'FULL_KEY_TRAVEL_COMPATIBILITY_SCOPE':'Existing undeformed mesh against frozen full-angle law only; physical compressible felt feasibility UNKNOWN',
 'FELT_COMPRESSION_REQUIREMENT_SCOPE':'Required displacement analytically established near 2 mm; mechanically justified reversible capacity NOT_ESTABLISHED',
 'RECOMMENDED_ROUTE':'NEED_MORE_AUTHORITY','NEW_NATIVE_MOTION_TESTS':0,'NEW_BLENDER_STATES':0,'GEOMETRY_MODIFIED':'NO','MATERIAL_MODEL_MODIFIED':'NO','LAW_DRIVER_SOLVER_RIG_MODIFIED':'NO','COLLISION_GUARDS_MODIFIED':'NO','FROZEN_ASSETS_UNCHANGED':'YES',
 'PRESERVATION_SCOPE':'Read-only source access; selected evidence SHA256 rechecked. No repeated whole-library driver or mesh audit; historical 3382-file protection remains historical.',
 'KEY044_KEY045':'NOT_EXECUTED_BLOCKED_FOR_CONTINUATION','B03_TO_B06':'BLOCKED','88_NOTE_DEPLOYMENT':'NOT_AUTHORIZED',
 'R12_AND_EDUCATIONAL_HISTORY':'FAIL_STOP_UNCHANGED','KM1_GEOMETRY_RIG_MOTION':'UNCHANGED','DRIVERS_193_AND_APPROVED_TRANSFERS_18':'UNCHANGED','B02_RESEARCH_ASSETS':'UNCHANGED',
 'DYNAMICS':{n:'NOT_QUALIFIED' for n in ['Free-flight','Hammer timing','Hammer-string contact','Full Hammer dynamics','Half-blow19']},
 'FINAL_STATUS':'DIAGNOSTIC_COMPLETE_READY_FOR_HUMAN_REVIEW','repair_selection_authority':'BLOCKED_PENDING_MATERIAL_OR_REGULATED_STOP_DATUM','diagnostic_limit':'Cause narrowed to undeformed representation of explicit 2 mm reserve; unique A/B implementation not established; allowed NEED_MORE_AUTHORITY outcome. No physical design fault certification.',
 'STOP':'HUMAN REVIEW'}
dump('FINAL_STATUS.json',status)
changed=[rel for rel,h in hashes.items() if hashlib.sha256((W/rel).read_bytes()).hexdigest()!=h]
assert not changed,changed
dump('EVIDENCE_HASH_VERIFICATION.json',{'selected_sources_sha256':hashes,'all_selected_sources_unchanged':True,'whole_library_reaudit':False,'new_native_motion_tests':0,'source_writes':0})
print(json.dumps({'output':str(O),'files':[p.name for p in O.iterdir()],'source_hashes_verified':len(hashes),'calculation':calc},ensure_ascii=False,indent=2))
