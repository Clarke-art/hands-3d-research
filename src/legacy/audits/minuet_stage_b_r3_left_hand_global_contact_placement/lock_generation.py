from stage_common import *
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
pol=read(P/'GENERATION_POLICY.json');audit=read(P/'R2_ALL_ACTIVE_PLACEMENT.json');lines=[]
for r in audit['notes']:
    s=r['summary'];mid=r['samples'][len(r['samples'])//2];side='LEFT' if mid['center_to_left_mm']<mid['center_to_right_mm'] else 'RIGHT'
    lines.append(f"|{r['note_id']} {r['note']}|{r['finger']}|{side}|{s['center_min_edge_mm']:.3f}|{s['pad_min_edge_mm']:.3f}|{s['pad_max_width_mm']:.3f}|{s['lateral_drift_mm']:.3f}|")
(P/'ALL_ACTIVE_FINGER_PLACEMENT_AUDIT.md').write_text('''# 全部主动指的R2只读落点诊断

先读取R2保存候选、827个真实Blender回读样本、运动数据、真实运动键面和三视角阶段图。没有重新求解R2。全部7次触键分别核对，三次B3没有合并。

|事件|指号|主要偏向|中心最小键边余量mm|有限指腹P90最小余量mm|指腹最大宽mm|持键横漂mm|
|---|---:|---|---:|---:|---:|---:|
'''+ '\n'.join(lines)+'''

**CONFIRMED**：所有skin pad中心位于目标白键内；6次事件的有限指腹cap的P90横向范围进入键缝一侧，L04已有较充足余量。中心偏向不同方向，不能用整手平移纠正。持键漂移只有约0.09–0.21mm，主要是接触位置选择而非横向滑动。R2规划器的白键范围只是标记中心从左右边内缩3mm；目标中心线软偏好系数0.12，没有指腹尺寸约束。真实白键宽23.089mm，有限指腹宽约8.34–11.28mm，3mm中心余量不足以容纳这些指腹。

**SUPPORTED**：教学和俯视帧可见主动指靠近键缝的轮廓；侧斜视角受到抬起轮廓和遮挡影响。指腹尺寸加上宽松的目标偏好，以及R2各指可达性、关节域与共享掌腕的折衷，是偏边原因。三音和弦的目标受共同root约束，不能把单指标记在键内当作整个指腹安全。

**UNKNOWN**：有限几何cap并非真实软组织接触压力区域；高于键面的轮廓跨缝不能当作真实错键或中心越界。画面投影对每根手指的主观影响仍须Human原速确认。未进行逐顶点forensic或全接触物理证明。

cap选择由冻结皮肤的distal权重和rest-space几何决定，使用distal权重>0.5、离skin pad标记不超过该distal横向P90宽度55%的局部皮肤顶点；完整选点见PAD_PATCHES.json。P05/P95范围与全cap极值分开记录，skin marker是已建立的指腹中心代理。全部持键样本、左右键边距离、完整cap和P90余量见R2_ALL_ACTIVE_PLACEMENT.json。三视角阶段图已进行Agent视觉检查；没有把静态帧检查当作完整实时原速影音观看。

Human最新反馈绑定在HUMAN_AUTHORITY_BIND.json；旧R2 FAIL_CLOSED和所有原报告原样保护。本轮不解决原闲置指张开WARN。
''',encoding='utf8')
(P/'GENERAL_WHITE_KEY_CONTACT_REGION_DESIGN.md').write_text('''# 通用白键内部接触区域

使用实际白键可奏前表面及冻结皮肤局部指腹cap。每次事件的指腹左右不对称extent来自R2整段持键期间的真实键局部几何，不按音名、小节或世界坐标写补丁。

键宽W，指腹最大P90宽P，左右extent为L/R。安全中心区间为[xmin+L+0.12W+0.05P, xmax-R-0.12W-0.05P]。0.12W是可见边缘余量，0.05P是小幅旋转带来的包络保护。目标为当前R2目标投影到该区间后，再向两边平衡余量位置移动25%；保留合理偏左偏右，不要求中心线。实际求解另对整个有限指腹P90范围施加键内软约束。

保留既有事件协调器、主动/准备/释放目标交接和原3D FK；替换本轮局部落点偏好。接触目标是原轨迹pad加几何推导横向修正，原深度与运动键面间隙作为参考，保留原纵向落点。所有主动指共享一个整段修正问题，无音高条件分支，无手工世界坐标表。

root的平移/旋转逐样本严格固定为R2，不是简单整手平移。关节只在原准备/持键/恢复窗口允许修正，窗口外为0。关节范围先从需要的几何位移和FK的mm/度leverage推导，再由10次静态同时可达性结果的每DOF最大实际修正×1.2收紧；原Rig域仍为硬边界。静态测试不保存Action或动态候选。预检目标误差按已取得键边余量的比例评估，不用任意绝对毫米阈值否决。

一次锁定参数见GENERATION_POLICY.json、STATIC_REACHABILITY.json与GENERATION_LOCK.json。正式生成只调用一次least_squares，允许内部正常迭代；生成后不修改参数、不再求解。

这些规则可用于同一手与其他白键事件；尚未验证其他曲目、黑键、跨寄存器大跳或柔性接触的泛化质量。
''',encoding='utf8')
scripts=['stage_common.py','contact_region.py','02_generate_once.py']
dump('GENERATION_LOCK.json',dict(scripts={n:sha(P/n) for n in scripts},policy_sha256=sha(P/'GENERATION_POLICY.json'),timeline_sha256=sha(P/'PERFORMANCE_TIMELINE.json'),pad_patches_sha256=sha(P/'PAD_PATCHES.json'),locked_before_candidate=True,candidate_limit=1,static_preflights=10,root_fixed=True))
print('PREGENERATION_REPORTS_AND_SINGLE_ATTEMPT_LOCK_WRITTEN',flush=True)
