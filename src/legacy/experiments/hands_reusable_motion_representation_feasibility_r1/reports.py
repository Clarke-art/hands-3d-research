"""Close the experiment at the failed specified-source gate. No primitive
extraction, retarget, correction, candidate generation or new geometry solve.
"""
from support import *
sys.path.insert(0,str(OLD/'_deps'))
from persistence import atomic_json,load_record
import numpy as np
P=read(O/'POLICY.json');I=read(O/'INPUT_BINDINGS.json');gate=read(O/'SOURCE_QUALIFICATION_GATE.json');audit=read(O/'SOURCE_GEOMETRY_AUDIT.json')
assert gate['SOURCE_QUALIFICATION_GATE']=='FAIL' and gate['stop_before_extraction']
assert sha(O/'POLICY.json')==read(O/'POLICY_LOCK.json')['policy_sha256']
raw,rawmeta=load_record('SOURCE_AUDIT_SAMPLES.npz')
assert rawmeta['record_type']=='READ_ONLY_SOURCE_QUALIFICATION_SAMPLES_NOT_A_PRIMITIVE'
assert raw['vertices'].shape==(len(raw['times']),3300,3)
def collision_ranges(rows):
 groups=[];current=[]
 for r in rows:
  if not r['core']:continue
  hit=any(r['finger_skin_pairs'].values())
  if hit:current.append(r['time'])
  elif current:groups.append([current[0],current[-1],len(current)]);current=[]
 if current:groups.append([current[0],current[-1],len(current)])
 return groups
ranges=collision_ranges(audit['rows'])
fingerpeak=max(audit['finger_witnesses'],key=lambda r:sum(x['count'] for x in r['examples']))
keys=[dict(time=r['time'],**h) for r in audit['key_witnesses'] for h in r['hits']]
key_peak=max(keys,key=lambda x:x['depth_mm'])
source_contacts=gate['contacts'];old_cost=read(ROOT/'experiments/hands_p3_temporal_wrist_coordination_r2/COMPUTE_LEDGER.json')
source_span=P['source_core_sec'];context_span=P['source_window_sec']
atomic_json('SOURCE_REJECTION_WITNESSES.json',dict(source_contact_summary=source_contacts,core_skin_collision_observed_ranges=ranges,source_peak_finger_witness=fingerpeak,source_peak_non_owned_key_witness=key_peak,source_event_roles_and_context_checked=True,all_values_from_actual_source_not_a_proxy=True,ROI_comparison_note='Current five strong-weight digit regions include proximal/middle/distal. Historic distal-only counts are not directly comparable.'))
visuals=[ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/witness_108.jpg',C1/'phase_sheet_overhead.jpg']
for p in visuals:p.read_bytes()
atomic_json('VISUAL_SOURCE_NOTE.json',dict(inspected_images=[dict(path=str(p),sha256=sha(p)) for p in visuals],historical_witness_time_sec=1.8,interpretation='witness_108 top row is original R1/C1 reference; bottom R2 and its red marks are not the donor. Overhead C1 phase sheet establishes overall hand appearance, not local skin safety.',fresh_human_source_approval=False,overall_human_approval_not_local_waiver=True,new_images=0,new_videos=0))
ledger=read(O/'COMPUTE_LEDGER.json');numerical_before_reports=ledger['used_seconds'];source_seconds=next(s['elapsed_seconds'] for s in ledger['stages'] if s['name']=='source_audit')
protect();before=read(O/'PROTECTED_BEFORE.json');after={p:sha(p) for p in before};changes=[p for p in before if before[p]!=after[p]];assert not changes
atomic_json('PROTECTION_CHECK.json',dict(referenced_files_checked=len(before),all_unchanged=True,changed=changes,before=before,after=after,independent_piano_access=False,frozen_Rig_skin_C1_MIDI_fingering_Actions_unchanged=True,historical_concurrent_FAIL='Retained; this narrow source SHA check does not supersede it',external_motion_sources_used=0,PianoVAM_data_used=False,path_migration=0,new_Actions=0,new_blends=0,new_videos=0))
def report(name,text):(O/name).write_text(text.strip()+'\n',encoding='utf8')
range_text='；'.join(f'{a:.9f}–{b:.9f}秒，{count}个命中样本' for a,b,count in ranges)
source_table='\n'.join(f"| {r['event']} {r['note']}／{r['finger']} | {r['samples']} | {r['contact_failures']} | {r['horizontal_max_mm']:.3f} | {r['gap_min_mm']:.3f}–{r['gap_max_mm']:.3f} |" for r in source_contacts)
report('MOTION_PRIMITIVE_DESIGN.md',f'''
# 动作原语来源与表示

**来源资格FAIL；本轮停在Task 1，没有提取可用于适配的自然动作原语。** 原始运动读回成功与可复用动作提取成功是两件事。

先读取Hands AGENTS.md。唯一指定来源为原C1的R04 C5(4)→R05 D5(5)，唯一预定目标为R12 F♯5(4)→R13 G5(5)。没有因来源失败改选另一段。原C1整体原速自然度有Human认可，但其局部缺陷没有获准，来源并无单独的清障验收。[INPUT_BINDINGS.json](INPUT_BINDINGS.json)保留验收原文和事件身份。

正式MIDI与C1事件表重新核对源前后R03–R06及目标前后R11–R14，音高、指法、channel、velocity、ON/OFF tick及展示时间一致。来源R04为1.4214275–1.6357130秒，R05为1.6357130–2.0642840秒；预定目标分别3.9928535–4.2071390及4.2071390–4.6357100秒。两组均4→5且OFF/ON相接，但这不证明几何或闲置指任务等价。目标的既有C1关节轨迹没有被用作生成答案。

来源资格检查覆盖{context_span[0]:.7f}–{context_span[1]:.7f}秒的原运动，含前一音B4中指释放、C5无名指持键、D5小指准备／持键及后一音G4拇指准备。239个240Hz＋准确阶段时刻，仅采样原C1真实Rig/skin和键Action，没有制作新动作。核心R04–R05有168个样本，活动pad接触全部满足既有门槛；但有62个中指—无名指真实skin相交样本，以及161个非目标键侵入样本。该完整整手协调不是合格来源。

本轮只预选一种表示，因来源门禁失败**未实现、未拟合或导出原语曲线**：事件相位＋目标键坐标系下的共享掌腕相对残差＋RSSF自然手型的五指相对姿态曲线。拟定接口应接收事件ON/OFF、ACTIVE/RELEASING/PREPARING/IDLE角色、键面／pivot／按键角、原始手型和边界姿态；音名与事件编号只作为实验选择信息，不作为算法规则。原A2的FK/LBS、采样及PCHIP可作为现有基础，但接口可表达不等于已经验证复用。

如果以后另行授权合格来源，来源曲线才提供相位、协调变化、相对腕运动及速度特征；目标真实键几何负责重建坐标与时间；局部IK只能登记必要对齐增量。三者须分别留证，不能直接平移世界关键帧或复制目标C1轨迹。本轮三类生成参数均未产生，故不存在“源曲线／几何／IK贡献占比”。

指定4→5的两根手指不能脱离其余三指与进入／退出上下文，不能删除来源中穿插的闲置中指轨迹后宣布原语通过。历史画面`witness_108.jpg`上排为原R1/C1参照，下排R2及红圈不当作本轮来源证据；整体俯视phase sheet仅支持整体观感，不能覆盖局部skin缺陷。[VISUAL_SOURCE_NOTE.json](VISUAL_SOURCE_NOTE.json)。

只使用已有C1/A2数据，没有PianoVAM或其他外部动作数据。复用边界：来源资格的几何证据成立；新键位适配、其他手指组合、速度范围和动作库覆盖率均未测试。

**STOP — HUMAN REVIEW**
''')
report('RETARGET_AND_GEOMETRY_VALIDATION.md',f'''
# 适配与真实几何核查

**FAIL发生在指定来源资格门禁；没有目标适配或实际新动态候选。** 此报告记录的是原C1来源的真实时间采样，不把来源核查冒充目标动态验证。

独立后台Blender5.1.2只读原C1批准Blend。真实native Rig/skin身份与冻结登记一致；88键组件未按压几何与登记表最大差{audit['registered_key_rest_geometry_parity_mm']:.8f}mm，运动键体最大差{audit['moving_key_geometry_parity_mm']:.8f}mm。源键Action原样求值，未按固定静止平面判断触键。

| 源活动音／指 | 真实pad样本 | 接触FAIL数 | 横向最大mm | 垂向gap范围mm |
|---|---:|---:|---:|---|
{source_table}

接触沿真实moving-key表面，横向≤0.03mm、垂向绝对间隙≤3mm。上述是实际skin指腹标记门槛，通过不等于整片指腹／整手无碰撞。

五指十对强权重皮肤ROI做真实BVH面相交；所有88键实际mesh做BVH与凸键体内部深度核对，并检查整手顶点，包括掌根／共享指蹼的键体风险。它们不是骨点或保守包络重叠。ROI没有覆盖全部共享皮肤的指间交叉，因此无命中不能作全手连续无碰撞证明，但已取得的实际相交反例足以拒绝来源。

核心窗口内相交观测分段：{range_text}。首个1.4214275秒样本中，无名指ACTIVE C5，中指RELEASING B4；较晚1.6666667秒为小指ACTIVE D5、无名指RELEASING、中指IDLE。峰值在{fingerpeak['time']:.7f}秒，为中指—无名指{sum(x['count'] for x in fingerpeak['examples'])}对面相交，此时两指均IDLE、小指仍ACTIVE D5。不能因为主换音角色为4→5就忽略第三指／闲置指缺陷。

核心非目标键侵入见证：{key_peak['time']:.7f}秒，{key_peak['digit']}的真实顶点{key_peak['vertex']}进入{key_peak['key']}，深度{key_peak['depth_mm']:.6f}mm，并有{key_peak.get('skin_key_triangle_pairs',0)}对真实skin／键面相交。它超过既有0.5mm非目标键阈值，不属于活动指的目标键触压许可。总计161个核心时刻有至少一处侵入；计数是命中样本，不是独立穿模事件或概率。

当前ROI包含近／中／远指区域；历史较窄远端ROI的碰撞对数不可直接做改善率比较。239点是有限240Hz与准确阶段点，观测区间不是精确连续碰撞起止。[SOURCE_GEOMETRY_AUDIT.json](SOURCE_GEOMETRY_AUDIT.json)含全部行，[SOURCE_REJECTION_WITNESSES.json](SOURCE_REJECTION_WITNESSES.json)含具体面、顶点、角色和世界坐标，[SOURCE_AUDIT_SAMPLES.npz](SOURCE_AUDIT_SAMPLES.npz)为原源数据核查样本，明确不是原语或新动作文件。

按Task 1止损：原语提取0、目标生成0、局部IK0、姿态修补0、动态候选0、候选真实Rig验证0。没有尝试参数化适配、目标接触校正或空间校正，所以不能将失败原因写成“黑键适配不可达”或“时间衔接失败”。不制作任何新旧成品视频。

来源真实复核进程{source_seconds:.3f}秒；准备＋源核查为{numerical_before_reports:.3f}秒，含报告闭合的最终累计见[COMPUTE_LEDGER.json](COMPUTE_LEDGER.json)，总上限120秒。数值优化调用0。此成本说明来源筛选可以低成本止损，不能证明完整复用生成＋动态验收优于旧高维优化，因为本轮没有生成动作。

冻结源文件及其Action没有写入；独立piano未访问。所有证据只在本目录。历史并发保护FAIL保留。

**STOP — HUMAN REVIEW**
''')
report('FINAL_HUMAN_REVIEW.md',f'''
# 最终Human审核

**HANDS_REUSABLE_MOTION_REPRESENTATION_FEASIBILITY_R1 — FAIL。**

失败根因是**预先指定的来源不具备整手安全资格**：C5无名指与D5小指的活动pad接触可靠，但中指／无名指释放和闲置动作真实穿插，并有非目标黑键侵入。整体自然观感认可不能将该片段直接升级为已清障原语。按用户止损规则停在Task 1，未改选来源或继续适配目标。

| 通用性等级 | 本轮证据 |
|---|---|
| A 动作提取成功 | 原C1原始数据采样成功；**合格自然原语提取未实施**，来源门禁FAIL。 |
| B 动作参数化成功 | NOT_TESTED；只预选一种接口表示，没有更换键位生成新动作。 |
| C 触键适配成功 | NOT_TESTED；来源168个活动pad样本PASS，目标适配没有运行。 |
| D 整手安全成功 | 来源FAIL；目标没有候选，不能报告改善／回退或合格。 |
| E 复用潜力成立 | UNKNOWN；本轮证明需先筛掉含碰撞的源协调模式，没有取得一次跨事件复用证据。 |

| 最终问题 | 答复 |
|---|---|
| 1 是否从C1提取可复用自然原语？ | **没有。** 保存的是原来源审核数组，不是合格原语；事件编号没有变成通用动作规则。 |
| 2 不同键位上生成合法连续动作？ | **没有测试。** 目标F♯5→G5没有开始适配，不以源4→5角色相同推断合法。 |
| 3 保持接触和自然姿态？ | 源活动指接触通过；源整手协调有真实缺陷，目标自然度与接触UNKNOWN。 |
| 4 避免或减少真实手指穿模？ | **未取得改善证据。** 原源核心62个时刻相交，峰62对；没有新动作可以比较。 |
| 5 相比旧高维优化有成本优势？ | **完整路线UNKNOWN。** 本轮来源核查{source_seconds:.3f}秒、优化0，可提前止损；没有生成＋验收成本，不能与P3求解77.704秒直接宣称加速比。 |
| 6 值得扩展其他手指组合？ | **当前不建议直接扩展或建设动作库。** 缺少本次跨事件成功证据；应先在独立授权下取得并清楚验收一个全手安全、角色完整的来源，再检验单次复用。 |
| 7 通用整手避障机制有技术依据？ | 冻结FK/LBS与真实skin／键体检查具备筛查依据；**通用低成本避障生成／校正能力未验证**，本轮没有新避障引擎。 |
| 8 继续修补还是换路线？ | **停止修补本次指定来源和本轮适配。** 不能把含穿插的闲置协调整段继承，再不断添加专用补丁。来源资格问题不证明事件相位＋相对动作表示不可行，也不支持立即重建动画引擎；下一步若获Human授权，应先闭合真正合格的来源契约，而非扩大动作库或恢复P3／B02求解。 |

只检查一个指定来源、锁定一个未执行目标；没有换样本、第二动作、P3优化、B02局部门户、CasADi/IPOPT、PianoVAM数据或其他MIDI测试。新Action、Blend、视频、动态候选全部0。没有运行候选Blender动态验收，只有源动作资格检查，二者明确区分。

{len(before)}项引用关键源文件前后SHA一致，原C1、MIDI、正式指法、冻结Rig/skin与琴键Action只读；独立piano未访问，历史并发保护FAIL不撤销。[PROTECTION_CHECK.json](PROTECTION_CHECK.json)。含报告的累计预算见[COMPUTE_LEDGER.json](COMPUTE_LEDGER.json)，不超过120秒。

交付：[MOTION_PRIMITIVE_DESIGN.md](MOTION_PRIMITIVE_DESIGN.md)、[RETARGET_AND_GEOMETRY_VALIDATION.md](RETARGET_AND_GEOMETRY_VALIDATION.md)、[SOURCE_QUALIFICATION_GATE.json](SOURCE_QUALIFICATION_GATE.json)。

**HANDS_REUSABLE_MOTION_REPRESENTATION_FEASIBILITY_R1**  
**FAIL — SOURCE_QUALIFICATION_GATE**  
**STOP — HUMAN REVIEW**

等待ChatGPT独立审核及Human授权。不自动提取另一来源、适配第二目标、开发动作库或进入正式动画生产。
''')
atomic_json('FINAL_STATUS.json',dict(task='HANDS_REUSABLE_MOTION_REPRESENTATION_FEASIBILITY_R1',status='FAIL',failure_stage='SOURCE_QUALIFICATION_GATE',failure_cause='Actual source skin intersections and non-owned key intrusion despite reliable active pad contact',source_raw_sampling_success=True,A_valid_motion_primitive_extraction='NOT_RUN_SOURCE_REJECTED',B_parameterized_retarget='NOT_TESTED',C_target_contact='NOT_TESTED',D_source_whole_hand_safety='FAIL',E_reuse_potential='UNKNOWN',representation_implementations=0,source_count=1,locked_target_count=1,targets_executed=0,local_IK_calls=0,optimization_calls=0,new_dynamic_candidates=0,new_actions=0,new_blends=0,new_videos=0,source_replacement_attempts=0,general_motion_reuse_impossibility_claim=False,next_stage_started=False,stop='STOP — HUMAN REVIEW'))
print('THREE_REPORTS_COMPLETE; source gate FAIL; no primitive, retarget or candidate. Protected',len(before),'sources unchanged.')
