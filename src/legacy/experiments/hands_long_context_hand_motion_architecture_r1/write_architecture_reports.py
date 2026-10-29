import sys,json,hashlib,math,datetime,collections
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;D=O/'sources'
def rd(n):return json.loads((O/n).read_text(encoding='utf8'))
def js(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def md(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf8')
audit=rd('BASELINE_FAILURE_READONLY_CHECK.json');facts=rd('REAL_RIG_CLEARANCE_FEASIBILITY.json');budget=rd('NUMERICAL_BUDGET.json');protection=rd('PROTECTION_CHECK.json');assert protection['status']=='PASS';above=next(r for r in facts['candidates'] if r['candidate_id']=='high_level_above');front=next(r for r in facts['candidates'] if r['candidate_id']=='high_level_front');assert above['actual_ALL_GATES'] and not front['actual_ALL_GATES'];facts['numerical_budget']=budget;js('REAL_RIG_CLEARANCE_FEASIBILITY.json',facts)
old=O.parent/'hands_early_hand_preparation_entry_reachability_r1';oldfacts=json.loads((old/'FINAL_FACTS.json').read_text(encoding='utf8'));ep=oldfacts['entry_prefix'];plane=above['projected_whole_digit_clearance']['minimum_surface_above_entity_mm'];remaining=above['event_recovery_bound']['remaining_to_next_event_seconds'];minimum=above['event_recovery_bound']['old_common_boundary_minimum_latent_or_joint_seconds'];junction=above['intent']['active_contact_modes'][0]['display_interval'][1];deadline=junction-minimum
sourceindex=json.loads((D/'SOURCE_INDEX.json').read_text(encoding='utf8'));source_map={r['file']:r for r in sourceindex if r['status']=='FETCHED'}
repo=lambda file:json.loads((D/file).read_text(encoding='utf8'))['sha']
pm_sha=repo('pianomotion_commit_verified.json');mime_sha=repo('pianomime_commit.json');robo_sha=repo('robopianist_commit.json');vam_sha=repo('pianovam_commit.json')
sources=[
dict(name='FürElise',class_='REAL_HUMAN_VIDEO_OBSERVATION_AND_3D_RECONSTRUCTION',code='Public visualizer/data scripts; full motion generator still not public on official page',data='59.94Hz motion.pkl: bilateral21x3 joints, MANO/global transforms, synchronized MIDI',code_license='Full generation code not available',data_license='CC BY-NC4.0 VERIFIED',weights_license='UNVERIFIED_NOT_FETCHED',commercial_ready=False,rig_adapter_executed=False,source='https://huggingface.co/datasets/rcwang/for_elise',files=['furelise_card.txt','furelise_tree.txt']),
dict(name='PianoMotion10M',class_='MONOCULAR_VIDEO_ESTIMATED_MANO_AND_GENERATIVE_MODEL',code='Fixed master '+pm_sha+'; infer.py/PianoPose.py/show.py inspected',data='JSON left/right MANO pose arrays with fps, audio and MIDI; loader resamples30Hz; no inspected hard assigned-fingering input',code_license='Apache2.0 VERIFIED LICENSE',data_license='CC BY-NC4.0 VERIFIED author statement in ICLR paper',weights_license='HF card has no licence metadata or licence sibling; UNVERIFIED',commercial_ready=False,rig_adapter_executed=False,source='https://github.com/agnJason/PianoMotion10M',files=['pianomotion__LICENSE','pianomotion__infer.py','pianomotion__datasets_PianoPose.py','pianomotion__datasets_show.py','pianomotion_model_metadata.txt','pianomotion_paper.txt']),
dict(name='Tipiano',class_='PAPER_AND_OFFICIAL_DEMO_OF_MIDI_FINGERING_CONDITIONED_GENERATOR',code='Official bundle has disabled Code+Dataset(TBD); no generation source/weights obtained',data='Paper outputs bilateral21-joint positions, annotations built on FürElise; raw annotation rights unverified',code_license='UNVERIFIED_UI_LIB_LICENSE_IS_NOT_MODEL_LICENSE',data_license='Annotation rights unverified; underlying FürElise NC',weights_license='UNVERIFIED_NOT_AVAILABLE',commercial_ready=False,rig_adapter_executed=False,source='https://tipiano.io/',files=['tipiano_official_bundle.txt','tipiano_paper.txt']),
dict(name='PianoVAM',class_='REAL_AUDIO_MIDI_VIDEO_WITH_ESTIMATED_LANDMARKS_AND_FINGERING',code='Fixed '+vam_sha+' README/ASDF inspected',data='Synchronized video/audio/MIDI, MediaPipe hand landmarks, fingering labels; not calibrated optical skeletal mocap',code_license='README states CC BY-NC4.0',data_license='Official README CC BY-NC4.0; HF metadata CC BY-NC-SA4.0; conflict preserved, both NC',weights_license='No actual transferable motion-generator weights verified',commercial_ready=False,rig_adapter_executed=False,source='https://github.com/yonghyunk1m/PianoVAM-Code',files=['pianovam__README.md','pianovam__FingeringDetection_ASDF.py','pianovam_dataset_metadata.json']),
dict(name='PianoMime',class_='VIDEO_DEMONSTRATION_TO_ROBOT_POLICY',code='Fixed '+mime_sha+' tutorial, IK controller and zarr headers inspected',data='Tutorial homography/fingertip/fingering extraction; high-level Zarr state212/action184 robot arrays, not our human26 controls',code_license='README claims MIT; no repository-level LICENSE found in recursive tree; robot asset LICENSE separate',data_license='Downloaded YouTube/source demonstration and bundled derived data terms not independently cleared',weights_license='Linked checkpoints, no separately verified grant',commercial_ready=False,rig_adapter_executed=False,source='https://github.com/sNiper-Qian/pianomime',files=['pianomime_tree.json','pianomime__README.md','pianomime__tutorial_data_preprocessing.ipynb','pianomime__robopianist_controller_ik_controller.py','pianomime__dataset_hl.zarr_data_state_.zarray','pianomime__dataset_hl.zarr_data_action_.zarray']),
dict(name='RoboPianist',class_='SIMULATED_ROBOT_CONTROL_BENCHMARK_NOT_HUMAN_MOTION_DATA',code='Fixed '+robo_sha+' lookahead/goal/MIDI fields inspected; Apache2.0',data='MuJoCo ShadowHand action/state; PIG must be obtained separately under its own terms',code_license='Apache2.0 VERIFIED; hand/MIDI assets separate',data_license='No human motion prior; PIG redistributability restricted',weights_license='No frozen human Rig policy compatibility demonstrated',commercial_ready=False,rig_adapter_executed=False,source='https://github.com/google-research/robopianist',files=['robopianist__LICENSE','robopianist__robopianist_suite_tasks_piano_with_shadow_hands.py','robopianist__docs_dataset.md']),
dict(name='SKY-Piano',class_='DIRECT_OPTICAL_HUMAN_MOCAP_WITH_PSEUDO_FINGERING',code='Official linked github/joonhyungbae/skypiano returned404 via web and GitHubAPI',data='Paper/official site:120Hz hand/body motion, flagged/imputed streams, MIDI and pseudo fingerings',code_license='UNVERIFIED_REPO_NOT_ACCESSIBLE',data_license='Official site only states per-modality terms; concrete motion commercial grant not obtained',weights_license='UNVERIFIED',commercial_ready=False,rig_adapter_executed=False,source='https://joonhyungbae.github.io/skypiano/',files=['skypiano_official_bundle.txt','skypiano_paper.txt'])]
js('MOTION_PRIOR_AUDIT_FACTS.json',dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',as_of_Asia_Shanghai='2026-10-13',sources=sources,commercially_cleared_and_local_frozen_Rig_adapted_prior_found=False,metadata_source_index='sources/SOURCE_INDEX.json',large_datasets_or_weights_downloaded=False,external_source_executed=False,model_training=False,paid_API_calls=False,our_candidate_evidence_class='PROGRAMMATIC_GEOMETRY_HYPOTHESIS_NOT_HUMAN_MEASURED_RULE',licence_rule='Code/data/weights/third-party models and recording rights checked separately; no scope inherited by naming or repo badges'))
phaseplan=dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',status='LOOKAHEAD_REQUIREMENTS_AND_PROPOSED_PHASE_GRAPH_ONLY',context=audit['lookahead_context'],known_start=dict(time=2.527855,status='ACTUAL_B2_VALIDATED'),earlier_state_provenance='R06 to R07 is still unvalidated; only original MIDI events used, no earlier posture accepted',geometry_constraint=dict(obstacle_key_index=audit['obstacle']['key_index'],prepare_digit=audit['dominant_digit']['finger'],region='Whole preparing-digit skin over actual entity top + clearance; actual static example proved it exists'),phases=['KEEP_EXISTING_HOLD_CONTACT','RAISE_BEFORE_OBSTACLE_ENTRY','TRANSVERSE_THE_SLICE_IN_VERIFIED_CLEARANCE_REGION','BEGIN_DESCENT_BEFORE_CONTACT_DEADLINE','CONNECT_TO_ORIGINAL_CONTACT_REGION_SET'],measured_old_collision_entry_time=ep['first_sampled_failure_time'],representative_safe_raised_state_time=audit['worst_failure']['time'],remaining_seconds=remaining,fixed_old_common_recovery_minimum_seconds=minimum,fixed_old_common_descent_must_start_by=deadline,fixed_target_lateness_seconds=minimum-remaining,lower_bound_not_global_feasibility_proof=True,alternative_contact_regions='May adjust natural boundary; must revalidate full contact/geometry/time, not old-vector lock',planner_output='Time-labelled clearance corridors, entry/exit phase deadlines, natural-family reachable-region requests and uncertain flags; no new whole trajectory executed')
js('LOOKAHEAD_PHASE_REQUIREMENTS.json',phaseplan)
md('BASELINE_FAILURE_AND_PLANNING_REQUIREMENTS.md',f'''
# 失败基线与可执行规划需求

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

本轮只读重算85条原始Blender记录（78规则/边界/风险样本+7补采样），确认45条失败；未重跑旧求解。B2从2.527855s开始，40个通过点覆盖至2.777855s，腕移15.418873mm；中指到E5距离27.667432→16.331513mm。首个失败2.778896666667s，错误区侵入0.254667086mm。最大失败在2.869521666667s，为3.872185949mm。E5在2.928717666667s和2.936009333333s接触失败。原数据及SHA见 BASELINE_FAILURE_READONLY_CHECK.json；250ms前缀仍是有限采样证据，不是连续无碰撞定理。

D#5是实际键表index54、GP_V11D_KEY_075，静止未按键；实体piece0的界限为X197.839949–209.114201mm、Y49.421377–114.286933mm、Z约0–15.444180mm。不是虚构的单一平面。最严重记录有42对键面交叉，35个原三角见证；所涉及皮肤均主要加权到MIDDLE_DIP_R，即中指远端指节皮肤。支持平面最近分布为前面20、左侧9、顶面6；指腹、侧面和远端皮肤整体进入前上缘/侧面实体，并非仅一个tip目标点失准。全部35个材料点、骨权重和原始坐标已保存，可核对具体三角和实体面。

|失败模式|真实证据|必须新增的高层输出|
|---|---|---|
|中指路线进入黑键前上缘|同一合法参考族中，屈指/横移产生3.872mm侵入|整指皮肤的三维清障走廊，不能仅约束pad到目标距离|
|掌腕与屈指顺序不协调|延后屈曲诊断与旧联合候选都有后半段碰撞|抬指、横移、下降分阶段的空间意图，明确哪阶段可改变哪些自由控制|
|端点集合不能决定途中路线|B2、共同边界与旧局部各自合格；中间不合格|候选走廊和连边资格，失败时返回实际障碍/面/指/时刻|
|临事件前缺恢复时间|新上方姿态虽然安全，回旧共同构型下界超时|为下降和接触恢复预留时间，使用后续音符事件回推阶段截止|
|原表示控制有限|非拇指受lambda参考族，准备中指由alpha控制|显式Rig能力/可达域，拒绝不可表达的意图；不暗中扩关节域|
|关节/接触点与整体皮肤不同|35个远端面见证；真实全皮肤验收仍必要|低层执行原接触合同，最终全部88键与指间面检验|
|潜在更早准备入口未知|R06 2.064284s、R07 2.492855s只读上下文|早期状态标UNVERIFIED，不能把更早音乐时间当作已知可行锚点|

两种几何假设均来自实体空间：前方绕行要求暴露低皮肤位于黑键前界之外；上方通道要求整指投影皮肤高于实体顶面+0.5mm。0.5mm是本实验的清障请求，不是改写0.25mm侵入门禁或人体规律。前方适配失败，上方真实静态通过；见 REAL_RIG_CLEARANCE_FEASIBILITY.json。本轮没有证实横向或掌姿通道，不将它们列作已可行路线。

上方候选整指最小投影净空{plane:.6f}mm，原G4持键合法。但在2.869521666667s离E5 ON只剩{remaining*1000:.6f}ms，固定旧共同构型最短latent/关节时间{minimum*1000:.6f}ms，至少超出{(minimum-remaining)*1000:.6f}ms。若采用这个固定恢复目标，下降必须不晚于{deadline:.12f}s开始。这个限制只排除该固定连接，不证明所有接触边界、指法或人体动作不可能。具体信息表明需要提前安排“抬指→过障碍→下降”，而非在最严重失败点才抬指。

原C01指法不变。未来反馈给指法规划的成本应包含持键可达域、清障通道存在性、最晚下降时刻、关节域饱和与接触转换失败。只有多种合法走廊/边界在受控验证中反复产生可信冲突，才提交另一个指法候选供Human选择；预算内一次失败不直接修改指法。
''')
md('LONG_CONTEXT_PLANNER_COMPARISON.md',f'''
# 长上下文规划与三类架构比较

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

推荐下一阶段主方案A：几何与事件驱动的长上下文手位规划，输出通用HandMotionIntent，由现有接触IK执行。程序化候选没有使用人体动作数据；它的依据是冻结键实体、真实失败见证和授权Rig空间，视觉自然度仍需Human检查。

|高层规划方法|输出与执行依据|本轮状态|下一步成本/限制|
|---|---|---|---|
|事件—手位—清障阶段图|按多音符事件建立HOLD/准备/过障碍/下降节点，边携带可达域、截止和实际失败证据|需求与阶段图已输出，已有两种真实Rig空间原语|中等；必须验证走廊连边，不能用静态点代替图可达|
|实体引导的有限空间走廊|在键表局部坐标输出整指上方/前方半空间和margin；转成低层FK/接触请求|两种意图已执行，同一严重失败时刻上方PASS、前方FAIL|低到中等；当前只接右手指定准备指，未实现连续跟踪|
|仅扩大窗口的多时刻优化|把未来事件直接塞入更多IK/CasADi节点|旧7节点真实失败已读，本轮没有重复|Jacobians昂贵、分支不稳定、缺清障路线决策；保留作低层执行器|
|采样式整Rig空间搜索|从contact-mode图中搜索可达连边|仅设计，未安装或运行新框架|变量与碰撞成本高；不以玩具骨链替代冻结皮肤|

|运动生成架构|主要职责|实现/计算成本（工程估计）|资产与许可|通用性与维护|
|---|---|---|---|---|
|A 长上下文规划|多音符手位/朝向区域、持键下闲指准备、黑白键走廊、接触集合、阶段时限|中等；离线阶段选择＋小型接触IK，避免盲目大联合搜索|直接复用当前资产；不需新增外部训练数据|事件级可扩展；维护几何意图、Rig能力与失败反馈接口|
|B 真实动作先验优先|提供自然腕指协调参考，再重定向与触键修正|高；数据清理、坐标/骨长/左右/指腹重定向，模型依赖或训练另计|当前核查源无“商用许可＋本地运行＋本Rig适配”全链通过|自然度潜力高，版本/许可/数据漂移维护成本高|
|C 高层＋先验＋接触IK|高层管路线时序，先验给趋势，IK守接触与碰撞|最高；两种接口、先验冲突处理和可追溯验收|未来可能最完整；目前缺已合法适配先验|架构可预留，但本轮不主推实施三套模块|

本轮新信息：同一中指控制族存在整指上方通道，故障碍不等于绝对不可达；仍必须提前回收这个自由度。阶段图应从原MIDI的多个未来事件回推下降时限，同时记录原R06→R07状态未知。LOOKAHEAD_PHASE_REQUIREMENTS.json保存B2已知锚点、风险进入时间和固定旧边界的恢复下界。本轮没有从G4之前启动真实运动，也没有把新增上下文字段宣称为完整长上下文规划器。

前方方案的根Y绕行改变了拇指投影接触特征，3次法向运输没有恢复合法整体接触，并导致C5/D5/E5侵入；保留FAIL，不再修它。上方方案保留掌腕姿态与原持键，准备指使用当前参考族最大伸展，原35个远端材料点相对实体移出；结果与约束来源记录完整。

合同分离已实际执行：HAND_MOTION_INTENT_CONTRACT_CHECKS.json中的序列化意图→intent_rig_adapter.py→冻结全FK/蒙皮控制，输出与此前Blender验收状态逐元素差0。没有调用成熟外部生成器，也没有把此有限原语适配器宣传为完整商品级规划器。

框架依据：RoboPianist源码提供明确的秒/步look-ahead和未来目标字段，可借鉴事件接口，但其仿真机器人与训练策略不能直接填入当前人手Rig。[官方任务源码](https://github.com/google-research/robopianist/blob/{robo_sha}/robopianist/suite/tasks/piano_with_shadow_hands.py)。自然先验路线的接触修正分工也得到FürElise方法的启发，但本轮未使用其数据或运行其策略。[官方方法](https://for-elise.github.io/)。
''')
md('MOTION_PRIOR_SOURCE_AUDIT.md',f'''
# 钢琴动作先验源码、资产与许可审计

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW
核查日期：2026-10-13，Asia/Shanghai。原始小型文本、固定提交、SHA256、HTTP错误保存在 sources/SOURCE_INDEX.json；共{len(sourceindex)}条获取记录。未下载大型数据集、模型权重，未运行外部代码、训练或调用付费API。

结论：在本轮核查的候选中，没有同时完成商业许可、本地可运行和冻结Rig适配验证的直接动作先验。确有与钢琴相关的真实观测/重建资产，不能把“未找到产品可用全链”说成世界上不存在数据。数据、源码、权重和第三方人体模型权利分别审查。

|来源|动作性质/格式|源码|数据/权重许可|当前决策|
|---|---|---|---|---|
|FürElise|多视角真实演奏视频重建；59.94Hz双手21点、MANO、同步MIDI的motion.pkl|数据可视化公开；完整生成器官方仍待发布|数据CC BY-NC4.0；生成权重未核实|研究资料；不导入商业产品|
|PianoMotion10M|单目视频估计MANO；JSON左右手/fps，音频与MIDI；加载器30Hz|Apache2.0代码，固定{pm_sha[:12]}|数据NC；HF权重无独立已核验许可|源码可评估，整体产品输入未获资格|
|Tipiano|MIDI＋指法→双手21点；当前官网/论文分阶段版本不同|官网Code+Dataset按钮禁用TBD|公开生成代码、权重、标签许可未取得|方法依据，不能宣称真实后端已接入|
|PianoVAM|Disklavier同步视频/音频/MIDI，MediaPipe估计点与指法标签|ASDF源码已读|仓库README为BY-NC；HF元数据为BY-NC-SA，差异保留；均NC|数据/源码商用不授予|
|PianoMime|视频平面单应性提取指尖/指法；Zarr机器人state212/action184|教程与IK实际已读；README声称MIT但树中未找到项目级LICENSE|演示/派生数据与权重单独授权未核实|技术参考，不作人体完整3D动作资产|
|RoboPianist|MuJoCo仿真机器人、未来MIDI目标|Apache2.0主代码，模型/数据另行|PIG另取且不可在仓库重分发；不属于人体动作数据|复用接口思想，不直接重定向策略|
|SKY-Piano|直接光学120Hz手/身体、同步MIDI、带不可靠/补全标记与伪指法|官网链接仓库经GitHub API与网页均404|只有每模态授权声明，实际动作商业条款未取得|新增重点资料；本轮未取得可接入资产|

FürElise的数据卡说明结构与NC限制，3D来自多视角重建和IK修正，不是直接光学骨架或本Rig控制。21点可以作为未来重定向目标，但不解决指腹/指尖差异、骨长、坐标和twist。[数据卡](https://huggingface.co/datasets/rcwang/for_elise)、[官方采集方法](https://for-elise.github.io/)。

PianoMotion实读infer.py，输入经PianoPose数据加载器组织，预测音频引导MANO姿态并默认CUDA渲染；不是已有的指定C01指法/NOTE_ON/OFF硬约束入口。代码Apache不自动赋予数据或ckpt商用权利。[固定源码](https://github.com/agnJason/PianoMotion10M/blob/{pm_sha}/infer.py)、[作者数据许可声明](https://openreview.net/pdf?id=rxVvRBgqmS)、[权重卡](https://huggingface.co/agnJason/PianoMotion_models)。

Tipiano的MIDI/指法层次接口值得参考，官方发布按钮仍禁用；网页React/MIT库说明与算法/模型许可不同。不能用官网效果或21点F1代替真实皮肤接触验收。[官网](https://tipiano.io/)、[论文v1](https://arxiv.org/html/2604.09692v1)。

PianoVAM README明确限制数据及代码；HF卡元数据存在NC-SA与NC的差异，不能用论文正文的CC BY文章许可替代数据许可。也不能把MediaPipe深度当作可靠标定三维骨骼。[仓库许可段](https://github.com/yonghyunk1m/PianoVAM-Code/blob/{vam_sha}/README.md)、[数据卡元数据](https://huggingface.co/api/datasets/PianoVAM/PianoVAM)。

PianoMime真实教程从视频平面提取指尖，当前控制器使用ShadowHand骨架/索引；来源视频、派生数据、checkpoint均需独立授权。MIT声明的正式许可文件缺口保留。[仓库](https://github.com/sNiper-Qian/pianomime/tree/{mime_sha})。SKY-Piano包含更合适的直接测量手部数据，但伪指法、不可靠点与指甲marker到指腹的偏差仍要处理；官网所链仓库无法访问，模态商业许可没有证明。[官网](https://joonhyungbae.github.io/skypiano/)、[论文](https://arxiv.org/html/2607.27296v1)。

MANO本体的默认条款为非商业研究，并单列商业许可申请；不能由上层开源代码牌照推断其模型链可商用。本轮未下载MANO模型。[原始条款](https://mano.is.tue.mpg.de/license.html)。NC含义核对官方法律文本：[CC BY-NC4.0](https://creativecommons.org/licenses/by-nc/4.0/legalcode.en)。

当前Rig有20个手指工程坐标＋6根控制，受授权参考族映射；外部21点、MANO45参数或机器人state/action都不能直接拷贝。未来最小资产入口应明确来源授权、双手关节语义、坐标单位/键盘标定、时钟同步、指法可信度及缺失点，再做原骨长/轴/指腹适配，最后走既有88键/自交/接触门禁。未核实许可资产只作资料评估。实际候选的证据类别是PROGRAMMATIC_GEOMETRY_HYPOTHESIS，没有数据推导人体规律，也没有模型生成。
''')
md('PRODUCT_ARCHITECTURE_DECISION.md',f'''
# 产品架构决策：A，长上下文规划优先

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

本轮找到比反复局部IK更有产品推进价值的架构分工，并有足够证据支持下一轮受控接口验证：长上下文决定手位区域、整指避障路线与清障/下降时限，接触IK把意图落到冻结Rig，真实Blender拒绝失接触、穿模和越域。动作先验入口预留，但目前不以未获许可或未接通的模型作为主依赖。

|必须回答的问题|决定与证据|
|---|---|
|只依赖当前局部CasADi/IK还有独立生成产品的价值吗|没有新的连续产品资格证据；作为低层接触执行/修正器保留，不再独自承担清障路线与时序选择|
|长上下文能给D#5清障新信息吗|能：实体上方通道真实存在，同时安全姿态到旧接触边界有115.490ms恢复下界，必须比风险末端更早安排下降|
|是否找到真正可用动作先验|存在钢琴观测/重建资料；本轮没有“商业许可＋本地运行＋本Rig重定向”全链通过的源|
|没有数据时能否先程序化规划|可以：从真实实体和授权可达域构造有限空间意图；一个静态整指上方候选已通过，但不能声称人体实测自然运动|
|保留哪些资产|原MIDI/C01/Action、冻结Rig/FK/蒙皮、实际88键、接触状态、批准参考族、静态IK/稀疏运动AD与真实几何验收|
|下一最小里程碑|一个多音符look-ahead实例输出清障走廊与进入/退出截止，低层在已知持键起点下完成受控走廊衔接并真实验收|
|何时反馈到指法或再次调整|多个合法走廊/边界持续出现有证据的时序或接触冲突、或者授权参考域无法表达清障；提交成本与失败见证，Human再选另指法或参考资产|

真实接口结果：两种语义不同的空间意图，前方FAIL，上方静态PASS。上方整指投影净空{plane:.6f}mm，原G4接触通过，目标侵入{above['target_depth_mm']:.9f}mm、错误区0、非相邻指面交叉0；完整FK/蒙皮与Blender误差{above['full_skin_FK_parity_max_mm']:.9f}mm。序列化意图重新适配的控制/状态与已验收候选差0。该证据足够支持走廊→接触IK衔接实验，不足以报告完整入口可达或自然连续演奏。

该上方状态保持在最严重风险时刻只能证明空间原语；离下一事件51.904ms，回旧共同构型至少115.490ms，固定恢复目标已冲突。因此下一轮应先安排“抬指—过障碍—按时下降”的阶段图，必要时调整目标接触集合，不能再从碰撞末端才修alpha或增加旧25ms/2ms节点。R06→R07未验证，早期上下文不能假冒已知入口。

下一轮仅建议一项：在原源时序、C01和已知B2锚点下，选一个多音符上下文的清障准备阶段，将高层整指半空间/走廊与阶段时限正式编译到现有接触约束接口；完成一条受控进入/退出走廊的有限连接，测真实连续位置/速率、G4保持与全部88键。验收必须区分走廊连接、未来下降可行性与完整E5入口；若截止不满足则返回FAIL和成本，不加第三/第四轮局部补丁。这个任务需Human另行授权，本轮不执行完整25ms、428.571ms、B02、23音或整曲。

工程估计：A需要维护一个事件/接触阶段图、几何区域与Rig能力接口，沿用已有依赖，本轮数值适配记账{budget['total_seconds']:.6f}s，优化器调用0；不能用这个静态运行量推算未来长窗口生产速度。B需合法数据、标定、重定向与可能的GPU/软件隔离；C再增加两者的冲突解析。当前先做A最小闭环，有合法短段自然先验后才评估混合升级，不同时实现三套方案。

通用性边界：JSON合同不含音名/特定事件ID；连续音、同指重复、换指/手位、黑键、和弦、双手6类原MIDI合同检查通过，5类违规被拒绝。真实适配仅执行右手当前指定准备指，左手、和弦执行、连续走廊跟踪及先验重定向尚未实现；未声称任意合法MIDI已生成自然双手动作。
''')
gates=dict(CONCURRENT_PROTECTION_ATTRIBUTION_VERIFIED=True,BASELINE_FAILURE_REPRODUCED_OR_READONLY_VERIFIED='READONLY_VERIFIED_NO_OLD_SOLVER_RERUN',LONG_CONTEXT_PLANNING_ARCHITECTURE_REVIEWED=True,MOTION_PRIOR_EVIDENCE_VERIFIED='PASS_SOURCE_EVIDENCE_ONLY_NO_FROZEN_RIG_PRIOR_ADAPTATION',MOTION_PRIOR_LICENSE_VERIFIED='PARTIAL_RESTRICTIONS_VERIFIED_NO_COMMERCIALLY_CLEARED_COMPLETE_PRIOR',GENERIC_HAND_MOTION_INTENT_DEFINED=True,REAL_RIG_HIGH_LEVEL_ADAPTER_EXECUTED=True,D_SHARP_5_CLEARANCE_CANDIDATE_VALIDATED='PASS_ONE_STATIC_CANDIDATE_ONLY',CONTINUOUS_ENTRY_STILL_UNVERIFIED=True,PRODUCT_ARCHITECTURE_SELECTED='A_LONG_CONTEXT_PLANNING_FIRST',FAIL_CLOSED=True)
js('FINAL_GATES.json',dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',gates=gates,original_fingering_changed=False,old_global_protection_FAIL_preserved=True,current_protection_status='PASS',current_protected_count=protection['before_count'],real_high_level_candidates=2,prior_full_motions_imported=0,full_continuous_piano_performance_PASS=False))
gate_text='\n'.join('|'+k+'|'+str(v)+'|' for k,v in gates.items())
md('FINAL_RECOMMENDATION.md',f'''
# 最终建议：A，长上下文手位规划优先

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW

**已找到更有产品化推进价值的架构与真实接口证据：以多音符时序和实际几何决定清障/下降阶段，再由现有接触IK执行。** 推荐下一阶段只实施A。动作先验的入口保留，但当前核查资料没有完整商用与冻结Rig适配资格；本轮未运行任何外部人体生成器、训练或导入动作数据。

原失败只读核实：2.527855–2.777855s的40样本前缀通过，腕移15.419mm；2.778896666667s起中指远端皮肤进入D#5，最深3.872186mm，85条中45失败，E5后续接触失效。全部原始数据、实体/三角/材料见证与源码SHA保持可追溯，没有重跑旧局部IK或扩大旧2ms/25ms片段。

本轮两种高层意图：
- 前方绕行：G4接触失败，最大其他键侵入{front['wrong_region_depth_mm']:.6f}mm，保留FAIL。
- 上方清障：在同一2.869521666667s风险时刻通过全部原门禁；整指对实体顶面的最小投影净空{plane:.6f}mm，错误区域侵入0，目标侵入{above['target_depth_mm']:.6f}mm，指面自交0。指法、MIDI、琴键Action、Rig和自然参考族不变。

这不是完整入口PASS。新状态到旧共同边界的必要恢复时间{minimum*1000:.3f}ms，剩余仅{remaining*1000:.3f}ms；固定边界连接冲突，其他边界集合未被排除。由此得到明确高层需求：抬指和过障碍须更早完成，给下降/触键留足真实时间，不在碰撞末端才求解。R06→R07仍未验证，Human自然度仍待审，任何未经验证的早期入口不可当锚点。

HandMotionIntent已定义，6类原MIDI事件合同检查和5类拒绝检查通过。独立适配器实际读取序列化意图，生成与真实Blender验收控制/全状态相同的候选，差0。真实执行范围仅右手指定准备指的两个空间原语；双手/和弦、连续跟踪、通用先验重定向不授予执行PASS。下一轮最小任务是高层清障走廊与接触IK的一项受控衔接，携带多音符上下文、下降截止和失败反馈；不是再增加旧局部节点/毫秒/迭代。

|最终门禁|结果|
|---|---|
{gate_text}

并发保护归因：3处历史变化和15个新增都确认属于另一聊天获授权的Piano存储审计，记ATTRIBUTED_CONCURRENT_CHANGE，未恢复或覆盖。上一轮85850项扩展保护FAIL仍保留。本轮独立当前{protection['before_count']}项SHA256前后完全一致，新增/删除/变化0；这两个时间窗口分别记录，不能以本轮PASS追改历史FAIL。

新数值适配保守记账{budget['total_seconds']:.6f}s，优化器0次，最多两种高层候选；含一次输入加载启动错误及修复、同两个状态的序列化接口重放。未制作正式Action、Blend、视频、批量渲染或整曲求解。八项交付齐全，停止待Human审核，不自动开始完整25ms、428.571ms、B02、23音双手动画或数字教材生产。
''')
# Add the current-window result without rewriting the prior FAIL.
p=O/'PROTECTION_CONCURRENCY_AUDIT.md';text=p.read_text(encoding='utf8');text+='\n本轮新保护窗口独立重算结果：'+str(protection['before_count'])+'项前后SHA256一致，变化/新增/删除均0，当前窗口PASS。此结果不改变上一轮85850项扩展保护FAIL。完整清单与原始核验见 PROTECTED_FILES_BEFORE.json、PROTECTED_FILES_AFTER.json、PROTECTION_CHECK.json。\n';p.write_text(text,encoding='utf8')
required=['PROTECTION_CONCURRENCY_AUDIT.md','BASELINE_FAILURE_AND_PLANNING_REQUIREMENTS.md','LONG_CONTEXT_PLANNER_COMPARISON.md','MOTION_PRIOR_SOURCE_AUDIT.md','HAND_MOTION_INTENT_CONTRACT.json','REAL_RIG_CLEARANCE_FEASIBILITY.json','PRODUCT_ARCHITECTURE_DECISION.md','FINAL_RECOMMENDATION.md']
assert all((O/n).is_file() for n in required);assert rd('POLICY_LOCK.json')['no_more_solves'];assert budget['under_budget'];assert not any(O.glob('*.blend'))
js('DELIVERY_CHECK.json',dict(status='COMPLETE_DESIGN_PROVISIONAL_STOP_HUMAN_REVIEW',main_architecture='A',required_deliverables={n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in required},current_protection_PASS=True,protected_count=protection['before_count'],historical_expanded_protection_FAIL_preserved=True,candidate_count=2,static_candidate_PASS_count=1,continuous_entry_PASS=False,new_numerical_wall_seconds=budget['total_seconds'],nonlinear_optimizer_calls=0,formal_Action_created=False))
print('ARCHITECTURE_DELIVERY_COMPLETE',required,'budget',budget['total_seconds'],flush=True)
