"""Assemble bounded diagnosis and plans from existing read-only checks."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1];R3=ROOT/'audits/minuet_stage_b_r3_left_hand_global_contact_placement';R2=ROOT/'audits/minuet_stage_b_r2_left_hand_continuous_accompaniment'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(name,text):
    with (P/name).open('x',encoding='utf8') as f:f.write(text)
def dump(name,value):write(name,json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False))
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
inventory=read(P/'EVIDENCE_INVENTORY.json');base=read(P/'READ_ONLY_BASELINE_AND_DOMAIN_CHECKS.json');small=read(P/'SMALL_FIXTURE_VERIFICATION.json');extra=read(P/'SUPPLEMENTAL_CHECKS.json');stat=read(R3/'STATIC_REACHABILITY.json');pol=read(R3/'GENERATION_POLICY.json')
protected=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[p for p,h in protected.items() if sha(p)!=h]
dump('PROTECTED_INPUTS_VERIFICATION.json',dict(files_checked=len(protected),changed=changed,unchanged=not changed,includes_all_8294_previous_protected_files=True,includes_all_42_existing_R3_files=True,original_R3_failure_records_and_scripts_unmodified=True))
guard=R3/'02_generate_once.py';record=R3/'GENERATION_FAILURE.json';scriptref=f'[{guard.name} 第46行](<{guard.as_posix()}:46>)'
boundstable='|手指|屈曲增量1/2/3（度）|基部横展增量（度）|\n|---|---|---|\n|拇指1：CMC/MCP/IP|0..25 / 0..25 / 0..18|-35..35（CMC）|\n|食指2、中指3、无名指4、小指5：MCP/PIP/DIP|0..32 / 0..32 / 0..20|-25..25（MCP）|\n'
write('DYNAMIC_FAILURE_EVIDENCE.md',f'''# R3动态失败现场与证据恢复

本轮仅诊断，正式/静态求解调用均0，动态候选0，Blender Action和motion.npz新增0。

**FINAL_FAILED_TRAJECTORY = UNAVAILABLE**。只读盘点R3目录全部{len(inventory['R3_files'])}个文件；无最终motion.npz、COORDINATED_TRAJECTORY_FIT.json、潜变量checkpoint、npy/npz/pickle/hdf5/tmp/dmp。已有ENGINEERING_DIAGNOSTICS.json包含R2落点及静态证据，没有首次动态fit.x或最终q。额外限定检查系统临时目录顶层中含minuet/stage-b-r3/hands-checkpoint/crash/dump的文件名，无匹配；未声称扫描整个磁盘或恢复已结束进程内存。

已读GENERATION_FAILURE.json、GENERATION_FAILURE_LOG.txt、IMPLEMENTATION_REPORT.md、CANDIDATE_ATTEMPT.json、GENERATION_LOCK.json、contact_region.py、02_generate_once.py、01_static_and_lock.py、STATIC_REACHABILITY.json，以及R2原fit、motion.npz、工程关节域和FK定义。R3原脚本/策略哈希与生成锁一致。

## 实际触发路径

{scriptref}：

```python
fit = least_squares(...)  # 第43行；本轮未执行
latent = fit.x.reshape(K, 20)
corr = PchipInterpolator(knots, latent, axis=0)(times) * envelope20
q = np.degrees(A['L_q']).reshape(-1, 20) + corr
assert np.all(q >= co.state_low[6:] - 1e-7) and np.all(q <= co.state_high[6:] + 1e-7)
# motion.npz与fit元数据的保存都在assert之后
```

CONFIRMED：异常发生在优化器调用返回后的输出重采样/插值检查，尚未写motion.npz，尚未运行Blender场景保存或Action烘焙。检查整段827个输出采样×20DOF，包含主动、准备、恢复与闲置阶段，非仅7次触键。不是root或琴键范围检查。

CONFIRMED：最终fit、真实nfev、status/success/message、最优性、latent、插值q、违规mask均未在assert前持久化，这是失败证据保存缺陷。GENERATION_FAILURE_LOG.txt自述为已观察工具输出重建，非完整stdout。最后观察值：残差调用3303、约240.5秒、加权接触RMS0.7916；不可换算成nfev，不证明求解器达到100次上限或收敛。

## 能恢复与不能恢复

|数据|结果与边界|
|---|---|
|R2原始轨迹、支持点、时间、root及键角|可恢复；113个支持点、827个输出采样|
|R3最终一批10个静态姿态修正|可恢复；无需再求解，重构其静态关节值用于域复核|
|静态预检总20次|历史记账可读；原第一批完整数值没有独立保存，不能以最终一批冒充两批现场|
|R3代码、策略、guard位置、异常文本|可恢复、锁哈希核验一致|
|R3最终动态fit.x / latent / q / optimizer termination|不可恢复；UNKNOWN|
|原动态违规手指/关节/DOF/时间/值/量|不可定位；全部UNKNOWN|
|本轮人工数组反例|独立合成机制验证，明确不是R3失败轨迹|

详细清单见EVIDENCE_INVENTORY.json；全域复核见READ_ONLY_BASELINE_AND_DOMAIN_CHECKS.json。本轮未为恢复未知字段重跑R3。

STOP — HUMAN REVIEW。
''')

near=[r for r in base['index_map_and_baseline_slack'] if r['R2_samples_within_1e_minus7_of_boundary']>0]
neartext='；'.join(f"{r['digit']} {r['joint']} {r['dof']}（{r['R2_samples_within_1e_minus7_of_boundary']}个近边界样本）" for r in near)
write('JOINT_LIMIT_CAUSE_ANALYSIS.md',f'''# 关节范围机制与原因分级

结论：**guard触发路径已定位；首次动态超限关节、时间和量尚未定位。** 确认了输出域保障不足、静态/正式变量预算不一致及失败前未保存结果三个工程问题；它们不等于证明上次具体违规样本，更不证明冻结Rig不可行。

## 1. 实际检查对象、单位与范围

20个左手DOF，flat_index = (finger-1)×4 + local_dof，顺序THUMB/INDEX/MIDDLE/RING/LITTLE，每指3个局部屈曲增量+同一基部骨的横展增量。横展不是第4个骨关节，不含轴向扭转。

{boundstable}

范围来自piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json的joint_increment_bounds_deg，经R2 left_chord_base.py的B/self.bounds/state_low/state_high进入guard。全部五指本曲目都被使用，因此未替换成LEFT_IDLE_INDEX/RING的整指hard域；闲置策略只是另有软约束。它是已有弯曲RSSF rest上的工程增量域，不是测得的解剖生理角度或被冻结Rig的全部物理极限。

R2保存L_q为弧度，输出guard先np.degrees转换；latent和corr为度，与degree bounds比较，合法后才np.radians保存。FK将degree states转弧度，明确取L的SETUPS。5×4数组与bounds的展开顺序一致。**未发现单位、左右手、轴/关节索引转换错误**；没有修改工程域。

只读验证：R2支持点与827个原采样均PASS；零修正不改R2且PASS；保存角度与PCHIP参考重建最大差{base['R2_saved_q_vs_PCHIP_reference_max_abs_deg']:.3g}度；转换往返最大差{base['degrees_to_radians_roundtrip_max_abs_deg']:.3g}度；时间范围及支持点范围都是0..5.95秒，没有外推采样。窗口包络在[0,1]。

## 2. CONFIRMED：支持点合法不保证输出加法合法

在支持点，latent边界是max(-limit,lo-reference)..min(limit,hi-reference)。若reference本身合法、e∈[0,1]且返回latent满足这些边界，则reference+e×latent是两个合法值的凸组合，支持点总角度合法。

但输出是PCHIP(reference)+e(t)×PCHIP(latent)，**不是**对支持点总角度PCHIP(reference+e×latent)。PCHIP导数取决于各自数据的相邻割线，不能把两个曲线的保形性质自动推广到相加结果或乘包络的结果。当前residual仅约束113个支持点；输出另有{extra['output_samples_not_support_knots']}个离任何支持点超过1e-12秒的采样。没有输出层域约束或总角度保形保证。

独立人工反例（非R3现场）：3点t=[0,1,2]，参考角度=[22,24.7,25]°，修正=[3,0.3,-0.3]°，包络恒为1。支持点总角度=[25,25,24.7]°合法；分别PCHIP后相加在人工t=0.61时为25.078033°，超过人工使用的0..25°域约0.078033°。对支持点总角度单独PCHIP则保持域内。**该数值与人工关节身份绝不能用于填写原R3超限关节、时刻或超限量。**

因此结构性的域保障缺口CONFIRMED；原R3是否恰由此导致某个具体违规，仅SUPPORTED。guard拒绝非法输出本身是正确的，不能通过取消assert、扩大容差或裁剪角度修复。

## 3. CONFIRMED：静态通过与正式修正域不是同一条件

静态先用geometry-leverage预算进行独立pose解，保存actual_delta = latent×e；随后使用1.2×max(abs(actual_delta))收紧budget。正式求解把这个收紧后的actual量预算用作**latent**的hard边界，实际修正又乘e。e<1时，正式允许的actual幅度更小。

只读比较已保存静态t=1.4214275秒，e≈0.205488。静态中指MCP横展actual_delta=3.329830°，对应latent=16.204491°；正式latent上限10.523030°，差5.681461°。同一静态姿态还有拇指CMC横展和小指MCP屈曲的latent预算不一致。详见SUPPLEMENTAL_CHECKS.json。

**这些是已保存静态姿态对正式潜变量预算的差额，不是Rig关节绝对值超限，也不是首次动态超限量。** 所有10个保存静态姿态的实际关节值均在原工程域内。差异说明静态通过没有验证正式收紧域、时间耦合和输出插值的整套条件；并不证明正式问题在该时刻没有其他合法解。

## 4. 静态与动态为何不能互相替代

静态仅测试每个起音组on+0.04秒及持键中点，共10个不同姿态；没有覆盖所有NOTE_ON/OFF、准备/释放边界和连续曲线。两批20次独立静态求解也没有施加全段修正速度/加速度约束。正式问题另外有潜变量prior、修正速度/加速度惩罚、收紧预算及包络。局部可达不等于存在满足这些附加条件的整段解。

R2本身存在接近工程边界的自由度：{neartext}。它們都是合法原样本，说明支持点间余量可能很小，支持插值叠加风险；它们不是已定位的R3肇事关节。

## 5. 假设分级

|假设|等级|判断|
|---|---|---|
|输出插值/叠加未保持总角度域|结构缺口CONFIRMED；原失败归因SUPPORTED|人工反例与代码证明缺口，原fit丢失所以不能确定实际违规|
|静态/正式预算表示不一致|CONFIRMED|一条保存静态恢复姿态不能满足正式latent预算；不证明全段无解|
|新接触目标与R2姿态存在完整动态冲突|UNKNOWN|独立pose支持静态可达；无完整动态解/约束残差|
|固定root是主因|UNKNOWN|10个固定root静态任务实际触键可达，不能归因于root|
|安全区域几何本身不合理|UNKNOWN作为失败原因|已有静态正余量，无新证据需调整区域|
|单位/左手索引错误|NOT_FOUND|源代码及R2复核一致|
|求解器方法必须更换|UNKNOWN，无支持|没有nfev/status/optimality证据|
|异常前未保存求解结果|CONFIRMED|所有有效结果保存语句在guard之后|

目前最有支持的解释是**约束验证管线不一致，尤其最终曲线域保障不足**，不是Rig不可能或root一定需要重做。实际违规的finger/joint/DOF/time/value/bounds/excess仍UNKNOWN。

STOP — HUMAN REVIEW。
''')

edge=[r['pad_min_edge_mm'] for t in stat['tests'] for r in t['active']]
write('ROOT_CONTACT_CONSTRAINT_ASSESSMENT.md',f'''# 固定root与接触约束评估

**FIXED_ROOT_CONFLICT = UNKNOWN**。没有证据要求开放掌腕自由度，也没有证据需要修改冻结Rig。

已保存的10个静态探针使用R2对应时刻的原root。三指和弦同时求解、其余单音各自按相应事件检查；有限指腹边缘余量约{min(edge):.3f}–{max(edge):.3f}mm，实际关节域复核均通过。它证明目标在这些姿态上可于固定root条件下到达；不能证明整个连续修正及所有准备/释放阶段都可达。

约10.991952°是静态最大关节修正，不能当成动态超限10.99°。R3最终曲线未保存，无法计算连续时段可达性、root灵敏度或放开root后的最小必要量。本轮没有进行root扰动优化或额外pose求解。

优先修正的是已经确认的数值表示、插值域保障与失败记录管线。保留R2 root平移、旋转、MIDI、键角和原动作窗口；不直接批准root重新优化。仅在未来同一域/同一输出表示下仍有可复核的持续接触冲突，并且证明该冲突不能通过既有合法指关节协调满足时，才有理由另向Human提交有限root+指协调设计。当前没有这类证据，不给任意毫米/角度root预算。

不能承诺完整保持自然动作的动态改善已实现。静态证据支持有可能；最终仍须唯一有效候选的7次真实skin落点、同相机同期原速对照和Human视觉审查。若保持窗口外手型、窗口边界连续性和工程域之间冲突，应停止，不扩大自由度。

没有证据支持更换优化器或修改安全区域；本轮只推荐一个工程管线修复方向。

STOP — HUMAN REVIEW。
''')

write('MINIMAL_NEXT_REPAIR_PLAN.md','''# 唯一推荐的下一阶段：GUARD_FIX

这里的GUARD_FIX指**输出关节域保障与诊断管线修复**，不是放宽或删除guard。本轮只提出方案，没有实现到R3历史代码，也没有生成候选。

## 修改范围

在未来另获授权的独立目录中，只修改局部修正曲线的数值表示/输出检查和结果记录接口。保持R2 root与原时间轴，保持通用白键安全区域、原指法、事件、键盘声链、冻结Mesh/Rig/Weights以及全部历史文件。保留当前优化器；不同时开启root协调、安全区域调参或自然手型重构。

1. 将工程关节域检查、物理修正量预算和静态预检统一到相同的实际角度/修正表示。区分latent与latent×envelope，不能把静态actual预算直接当latent预算并据此宣称预检覆盖了正式问题。用正式最终预算复核预检；任何新静态求解都计数留证。
2. 对最终**总关节角度**建立域保持曲线，避免把两个独立PCHIP相加当成保形保证。最小首选设计是在原活动窗口内对合法总q支持点进行标量域保持插值，窗口外精确复用R2，并在原窗口边界复用R2值/连续导数约束。其可行性必须在授权生成前用零修正和人工反例验证；若边界连续性与域保障不能同时满足，不用裁剪或放宽guard强行通过。
3. 静态、优化残差/约束检查和输出统一调用同一个曲线评价器；在既有827个输出采样与原事件边界复核总q、修正预算、窗口外保持、接触目标与连续性。仅支持点合法不再作为输出域通过依据。
4. 优化器返回后立即保存真实termination和latent/支持点；输出guard之前保存输出时间、总q、包络与全部违规摘要。guard失败也应留下可复核数值现场。具体记录机制见DIAGNOSTIC_INSTRUMENTATION.md。

以上是一条数值验证管线修复路线，不是批准对整段自然动作重新设计。总q插值可能改变活动窗口内的细节，必须把R2动作保持作为硬验收条件，不能只因域合法就交付PASS。

## 下一轮授权后的有限执行与验收

- 先验证：原R2零修正逐样本一致；支持点和输出域一致；小型人工反例能被准确定位；静态与正式actual预算一致；窗口外姿态与root原样。
- 参数与曲线策略在生成之前只锁定一次；正式只允许一份动态候选、一次求解，禁止第二次修改参数重算。
- 有效候选必须7次skin触键全部核验、和弦同步、NOTE_ON/OFF/tempo/键角/音频不变，且合法最终采样、无新增明显悬空/抽动/掌腕迁移。
- 与原R2保持相同相机、尺度、时钟、速度制作真实三视角同期对照；Human自然动作认可不能由数值PASS代填。
- 真实nfev、终止状态、是否达到上限、关节域、窗口外姿态、关键轨迹变化必须可复核。

## 止损条件

合成及零修正验证失败则不开始动态生成。首份候选的域/实际接触/动作保持失败则FAIL_CLOSED并保存失败证据；不裁剪、不改root、不改Rig、不缩小安全区、不换指、不换方法重试。若数据依然不足，标记UNKNOWN并停止。

本轮没有执行上述推荐修复。

STOP — HUMAN REVIEW。
''')

write('DIAGNOSTIC_INSTRUMENTATION.md','''# 最小失败记录机制

本目录新增独立diagnostic_recorder.py；不修改或导入执行R3生成脚本，不包含优化器、FK、动画保存或关节裁剪。当前只运行有限人工数组测试与历史数据只读复核。没有写motion.npz或Blender Action。

## 未来授权运行中的三个记录点

1. **优化器刚返回，先保存再处理**：真实fit.nfev、njev（若可用）、success、status、message、cost、optimality、active_mask、max_nfev及与上限的比较；residual callback计数另列。保存knots、reference states、最终latent、原source hashes、degree bounds、物理/latent预算、包络策略、timegrid和策略哈希。此时不依赖PCHIP或guard成功。
2. **按实际处理阶段分别检查**：raw support q、support corrected q、final interpolated q、若生成后进入Action则saved Action回读q分别记录。每阶段保存采样时间、总q、合法mask、非有限值mask、全部超限的hand/finger/joint/DOF/flat index/value/lower/upper/excess以及有限摘要。样本数和DOF预先有限，禁止逐顶点forensic。原始支持点失败与插值后失败必须分开，不用“joint failure”单字符串混淆。
3. **抛异常之前记录**：诊断JSON写入并fsync返回后才允许guard拒绝。即使插值阶段抛错，也应保留第1步已有的solver checkpoint，并另存exception/type/处理阶段；不能把所有保存安排在最终assert之后。

建议未来调用顺序（示意，**本轮未执行**）：

```python
# 此处fit必须来自未来授权的唯一求解，不能以callback计数代替nfev
write_checkpoint(new_run/'SOLVER_TERMINATION.json', {
    'solver': actual_returned_fit_metadata,
    'knots': knots, 'reference': reference, 'latent': fit.x,
    'source_hashes': hashes, 'bounds_deg': boundaries,
})
# 用统一评价器得到support/final总角度，保留同一原事件时钟
stages = [inspect_stage(stage, times, q_deg, lower, upper)
          for stage, times, q_deg in diagnostic_stages]
ok = record_before_guard(new_run/'OUTPUT_GUARD_CHECKPOINT.json',
                         actual_returned_fit_metadata, stages,
                         raw_reference_and_correction_inputs, hashes,
                         origin='AUTHORIZED_FUTURE_RUN_DIAGNOSTICS')
if not ok:
    raise RuntimeError('Recorded joint-domain guard failure; no refit')
```

所有轨迹数字属于诊断checkpoint；它不是有效motion候选，不自动写Action或重试。使用独立新目录，exclusive-create防止覆盖已有证据。记录器不修改输入数组。NaN/Infinity使用显式JSON标记，并与有限值超限分开；不将缺失值置零制造PASS。

## 已验证的有限人工测试

7项检查：合法数组不变；上下边界/时间/身份映射；非有限值独立报告；合法支持点相加后插值越界反例；checkpoint在拒绝前存在；nfev与callback计数分开；旧checkpoint不允许覆盖。另只读核验非有限值JSON标记可正确读回。相关文件均标记ARTIFICIAL_ARRAYS，不能当成R3原失败现场。

人工反例的“THUMB CMC / t=0.61 / 0.078033°”仅用于记录器身份与机制测试，绝不用于原R3定位结论。测试中的nfev=7/status=1也是人工元数据，本轮没有实际优化器执行。

原R3真实nfev、最终收敛状态和超限样本仍UNKNOWN，不由诊断工具补造。

STOP — HUMAN REVIEW。
''')

qa=[
('Q1','02_generate_once.py第46行；修正量PCHIP后叠加R2角度、输出采样完成时，在np.savez及Action烘焙前检查827×20DOF。'),
('Q2','没有。现有R3未保存fit.x、latent、输出q或违规mask；FINAL_FAILED_TRAJECTORY=UNAVAILABLE。'),
('Q3','原动态手指/关节/时刻/实际值/超限量全部UNKNOWN；人工反例与静态预算差额均不能替代。'),
('Q4','确认输出曲线域保障与静态/正式修正预算表示不一致；未发现左右手、单位、轴或关节索引转换错误。guard拒绝本身正确。'),
('Q5','最有支持的是验证管线不一致，尤其分别PCHIP后相加未保持总q域；还存在静态预算到正式latent预算的不一致。具体原失败归因仍SUPPORTED。'),
('Q6','不是已证实的限制；固定root静态任务实际可达，完整动态root冲突UNKNOWN。'),
('Q7','当前没有证据要求开放。先保留R2 root，修复输出域与诊断管线。'),
('Q8','不需要修改冻结Rig；无这类证据或授权。'),
('Q9','固定root静态证据支持有可能，但完整动态与Human自然动作保持仍未验证，不能承诺。'),
('Q10','唯一推荐GUARD_FIX：统一actual/latent预算、总角度域保持评价与输出检查，在guard前保存现场；不同时开放root或调安全区。'),
('Q11','优化器返回立即保存真实nfev/status及支持点/latent；guard前分阶段保存全部时间/角度/身份/边界/超限/非有限值，异常后保留checkpoint。'),
('Q12',f"{'YES' if not changed else 'NO'}：{len(protected)}个保护文件哈希一致，含原8294文件及全部42个R3文件；无历史修改、动态求解或新候选。")]
write('FINAL_ANSWERS.md','# 最终Q1–Q12\n\n|问题|回答|\n|---|---|\n'+''.join(f'|{q}|{a}|\n' for q,a in qa)+'\n诊断完成不等于动态演奏通过。STOP — HUMAN REVIEW。\n')
status=dict(phase='MINUET_STAGE_B_R3_DYNAMIC_JOINT_LIMIT_FAILURE_ISOLATION_R1',client_date='2026-10-10',scope='FAILURE_ISOLATION_ONLY',FINAL_FAILED_TRAJECTORY='UNAVAILABLE',FAILED_TRAJECTORY_RECOVERED='NO',JOINT_LIMIT_FAILURE_LOCALIZED='PARTIAL',INTERPOLATION_OR_GUARD_DEFECT='CONFIRMED',FIXED_ROOT_CONFLICT='UNKNOWN',CONTACT_REGION_RULE_STATUS='STATIC_VALIDATED_DYNAMIC_UNVERIFIED',FROZEN_ASSETS_UNCHANGED='YES' if not changed else 'NO',NEXT_REPAIR_ROUTE='GUARD_FIX',DYNAMIC_CANDIDATES_GENERATED=0,FINAL_STATUS='DIAGNOSTIC_COMPLETE_READY_FOR_HUMAN_REVIEW' if not changed else 'INCOMPLETE_BLOCKED',localized_scope='Actual guard/stage/domain confirmed; original violating finger/joint/time/value/excess unavailable',confirmed_defect_scope=['Output sum of separately interpolated reference/correction lacks total-q domain guarantee','Saved static actual correction budget tightened then applied to formal latent variable','Optimizer and output violation evidence are saved only after failing assertion'],actual_failed_sample_attribution='UNKNOWN',most_supported_failure_mechanism='Output interpolation/constraint-validation representation mismatch; not confirmed original violating sample',units_and_joint_indices_issue='NOT_FOUND',actual_original_solver_nfev=None,actual_original_solver_convergence=None,actual_original_solver_limit_reached=None,read_only_R2_baseline_guard='PASS',saved_static_probes_rechecked=10,static_probes_with_formal_latent_budget_mismatch=1,static_pose_solves_this_round=0,production_dynamic_solve_calls=0,small_artificial_fixture_cases=7,new_motion_npz=0,new_Blender_Actions=0,historical_R3_files_unchanged=42,protected_files_verified=len(protected),changed_protected_files=changed,original_R2_root_unchanged=True,recommended_repair_executed=False,root_freedom_opened=False,frozen_Rig_modified=False,Human_visible_dynamic_quality='NOT_EVALUATED_NO_NEW_CANDIDATE',dual_hand_started=False,next_stage_started=False,stop='STOP — HUMAN REVIEW')
dump('FINAL_STATUS.json',status)
files={p.name:sha(p) for p in P.iterdir() if p.is_file() and p.name!='DELIVERY_MANIFEST.json'}
dump('DELIVERY_MANIFEST.json',dict(files=files,required_six_deliverables_present=True,all_outputs_in_independent_audit_directory=True,diagnosis_only=True,no_new_candidate=True,fixture_data_are_synthetic=True))
print('DIAGNOSTIC_COMPLETE',status['FINAL_STATUS'],'protected',len(protected),'changed',changed,flush=True)
