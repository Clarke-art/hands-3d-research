# LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT

2026-10-09 · DESIGN_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

**LEFT_LITTLE_MOVING_KEY_REACHABILITY_BLOCKED**。唯一候选改善了接触，但新增邻键几何穿入，整体不得通过。STOP — HUMAN REVIEW。

## 因果结论与证据强度
最可能原因为 **A. FIXED_ROOT_REACHABILITY_LIMIT / SUPPORTED**，限定在继承的小指轨迹与工程域。候选保持小指全部关节轨迹不变，仅通过共享掌腕随动和拇指协调，两次D2最大皮肤gap由7.689142降至2.969126mm。这确证掌腕随动对原轨迹的因果作用，但不证明所有固定root关节路径都不可达。
B. FINGER_TRAJECTORY_PLANNING_FAILURE = UNPROVEN。旧轨迹是一次局部有界拟合，没有全局可达性证明；本轮没有另试小指IK。
C. CONSTRAINT_CONFLICT：原失败的全局约束不可兼容仍UNPROVEN；本候选“正确触键与邻键净空未能同时满足”已CONFIRMED。D2原失败在0.735秒已发生，早于D3准备0.830秒，所以拇指重叠不是原失败必需原因。
D. CONTACT_TARGET_OR_EVALUATION_ERROR = NOT_REPRODUCED。实际child mesh顶平面与旧运动键面gap最大差0.000001373mm，键体世界顶点最大差0.000017059mm，关节分解与原轨迹最大差0.00001165°。旧pivot错误已修复，不能把历史实现错误当作当前原因。
小指full-down角度[MCP,PIP,DIP,spread]约[31.5,21.9853,0,24.5]°；工程上界[32,32,20,25]°。在原位置每增加1°，MCP/PIP/DIP的局部z灵敏度分别约−0.4422/−0.1073/+0.0054mm。PIP同时朝键右缘漂移约+0.3582mm/°，指腹距右缘约1.003mm。剩余角度的线性估计约只能再下降1.33mm，且尚未计侧向限制；这是局部导数证据，不是非线性全局下界，也不是人体生理结论。
## 只读阶段记录与唯一实验
CONTACT_PHASE_MEASUREMENTS_R1.json包含185个原轨迹样点及两次D2的九个关键阶段，记录实际键面位置、fixed/skin pad、键法向及世界竖直gap、严格可奏区、关节余量、root矩阵和并发任务。正式pad定义、D2/D3几何、L1/L2姿态均存入STATIC_ANCHOR_PROTECTION_R1.json。root Empty包含原生坐标绑定变换，其translation不是掌腕原点；报告另从native_to_canonical逆变换派生共享腕部原点，约[−220.754,−94.601,45.601]mm。
先锁政策和脚本SHA，随后一次全段有界least_squares；所有皮肤均来自Blender dependency graph，未重建skinning链。锁定root高度[−3.5,0]mm、键盘X轴pitch[−2,0]°、前后[−5,0]mm；三者随原D2 depression quintic变化。只有一个共享root。拇指为旧轨迹到已批准L1准备姿态的有界凸组合，系数随D3键程变化。小指、三个闲置指、右手、键盘事件不变。
最终参数：下降3.500000mm，pitch-0.614045°，前后位移-0.001688mm。一次求解 nfev=18、residual calls=139、cost=109504.902574，无restarts。优化器结束不等于验收通过。
两段重叠[0.950,1.020]、[1.200,1.270]秒均按真实当前键面检查。35ms下沉、70ms回弹及NOTE_ON/OFF未改。原四静态场景没有重新设计；动态重叠处不冒充整手静态姿态。
依赖修复：首次启动在任何求解前因cp312 SciPy不能用于Blender CPython3.13退出；只安装同版本SciPy1.18.1的cp313包至本审计目录，记录于IMPLEMENTATION_REPAIR_R1.json。运动政策、seed、bounds、目标权重与求解参数未改。
## 接触、净空及可见预检
|事件|原最大皮肤gap mm|候选fixed / skin最大gap mm|起音/下沉/持键/回弹|
|---|---:|---:|---|
|n01 / MIDI38|7.689142|2.951690 / 2.969126|PASS|
|n02 / MIDI50|0.999876|1.983441 / 1.983426|PASS|
|n04 / MIDI38|7.689142|2.951690 / 2.969126|PASS|
D2接触仅余约0.031mm工程容差余量，不能据此宣称稳健贴合或自然度已批准。完整候选在180个120Hz及边界样点检查全部3300顶点和88键。没有错误pad落到其他键，但新增122条“时间×键体”深度命中记录；这些不是122个独立缺陷。
E2前键体内出现小指distal皮肤顶点279/1333，最大低于键顶3.083002mm，最短退出键体距离约0.68/0.59mm。F♯2内出现中指distal顶点1294，低于键顶3.405533mm，但最短退出侧面距离仅约0.0056mm。两键实际几何均为8角点矩形体，非仅由不贴合包围盒产生的假阳性。**竖向深度不等于同等厚度的侧向穿模，也不直接等于肉眼显著程度。**
掌腕分区未检出>3mm深穿，最小投影键面gap为−2.983356mm，仍有浅层接触风险。本候选的失败判据是锁定净空屏障，不能被主动pad通过抵消。有限顶点检查不是所有三角面相交的穷尽证明。
连续性：全部硬角度域通过；最大关节速度418.028°/s、加速度34978.812°/s²；root速度167.951mm/s、角速度29.465°/s，均通过事前范围。小指近限位仍每次0.291667秒，未以旧0.05秒门槛单独判失败。三闲置指角度变化0°，但整体下降使中指侧面触碰邻键。
常规顶视、侧斜、合理近景中，小指随整体掌腕下降更接近下沉D2，原明显浮空减轻；仍有接近3mm的残余间隙，未把它描述为贴合无缝。
三闲置指保持原批准曲度，没有新蜷成钩爪；掌腕仅小幅下沉/恢复，逐帧未确认NOTE_ON瞬移或关节支路跳变。整体节奏自然度仍HUMAN_PENDING。
在D2/D3交叠阶段拇指动作仍连贯，未见新的反关节；连续性数值与观察互相支持，但不构成教师或Human批准。
新增E2/F♯2交叠由实际皮肤几何确证。现有三视角没有足够明确的画面证据将这些微小边缘交叠描述为明显新增穿模；尤其F♯2的3.406mm竖向深度不能当作相同的侧向穿入厚度。
即使正常视图不显著，已锁定的邻键净空检查仍失败，因此本候选整体BLOCKED。本次失败不由0.2917秒近限位时长单独触发。
## 保护与交付
重开后四个static core身份一致，左手mesh/rest/weights/corrective不变，右手root/Action/完整core、键体mesh与Action、所有审核相机均与来源一致。最终检查1154份冻结/继承文件，变化0。三个正式手SHA与Grand权威、MIDI、production pointers保持。
新候选与原失败同相机同步，84帧、60fps、1.4秒，原MIDI时间0.400–1.800秒（最后视频样点1.783333秒，数值含1.800端点）。left_d2_d3_d2_reachability_r1.mp4为2304×756；left_before_after_r1.mp4为2304×1512。均静音并完整解码通过。没有重渲染右手。
[审核页](../../../../examples/historical/audits/left_little_finger_moving_key_reachability_r1/review.html) · [唯一候选](../../../artifacts/a948286516f76d065015.md) · [前后完整对照](../../../artifacts/965cb4b664d965aa693d.md)。本轮已触发止损，不启动第二版优化。
## Q1–Q13
|问题|答案|
|---|---|
|Q1|FIXED_ROOT_REACHABILITY_LIMIT — SUPPORTED；在原小指轨迹与工程域下，共享掌位固定是重要限制。未证明固定 root 的全局不可达。|
|Q2|YES — 原小指轨迹完全不变时，随动使两次D2皮肤gap从7.689降至2.969mm。|
|Q3|UNCERTAIN — 原指链的垂直接触可达已获支持，但连同邻键净空的合理动态空间尚未证实。|
|Q4|YES — 本唯一候选出现触键与邻键净空冲突；不是所有规划方案不可兼容的证明。|
|Q5|NO — 独立实际键面与旧计算一致，未复现接触坐标错误。|
|Q6|YES — 一个有界候选，一次求解，无重启、扩域或第二版优化。|
|Q7|YES — 两次D2的起音、下沉、持键、回弹均通过既定接触筛查，皮肤最大2.969mm。|
|Q8|YES — D3所有接触阶段通过，最大1.983mm。|
|Q9|HUMAN_PENDING — 闲置三指曲度保持，掌腕连续；整体自然度不因数值通过而自动批准。|
|Q10|NO — 常规三视角未确认明显新增钩爪/跳变等；但确证新增E2/F♯2几何穿入，整体仍阻断。|
|Q11|NO — 四个原静态场景重开身份均一致，L1/L2批准保持。|
|Q12|NO — 本轮不能证明必须修改正式mesh/rig。|
|Q13|LEFT_LITTLE_MOVING_KEY_REACHABILITY_BLOCKED|

```text
PRIMARY_FAILURE_CAUSE = FIXED_ROOT_REACHABILITY_LIMIT / SUPPORTED
FIXED_ROOT_LIMITATION = YES / ORIGINAL_TRAJECTORY_CONTEXT
LITTLE_FINGER_DYNAMIC_REACHABILITY = CONTACT_SUPPORTED / COMBINED_CLEARANCE_UNPROVEN
ROOT_FOLLOW_THROUGH = ONE_PROBE_EXECUTED / CONTINUOUS / NOT_APPROVED
LEFT_D2_DYNAMIC_CONTACT = PASS_ENGINEERING_SCREEN / MAX_SKIN_GAP_2.969_MM
LEFT_D3_THUMB_CONTACT = PASS_ENGINEERING_SCREEN / MAX_SKIN_GAP_1.983_MM
LEFT_IDLE_FINGERS = APPROVED_CURVES_PRESERVED / NEW_MIDDLE_SIDE_CONTACT
STATIC_ANCHOR_IDENTITY = UNCHANGED / HUMAN_APPROVAL_REMAINS_VALID
HUMAN_VISIBLE_NATURALNESS = HUMAN_PENDING / OVERALL_CANDIDATE_BLOCKED
FINAL_STATUS = LEFT_LITTLE_MOVING_KEY_REACHABILITY_BLOCKED
HAND_BASELINES_UNCHANGED = YES
PIANO_BASELINE_UNCHANGED = YES
STOP — HUMAN REVIEW
```
