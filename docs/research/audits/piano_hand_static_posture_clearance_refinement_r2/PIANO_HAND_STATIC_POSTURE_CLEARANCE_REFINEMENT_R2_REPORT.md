# PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT

2026-10-09 · DESIGN_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

**FINAL_STATUS = STATIC_POSTURE_CLEARANCE_READY_FOR_HUMAN_REVIEW**。一个新R2候选中四姿态主动接触/准备与有限净空筛查通过；匹配正常视角显示左手三闲置指更弯曲、收拢且掌腕更低，右手原D#5/G#5邻键风险已去除。**这是Agent候选资格，Human_approval=false**；未把上一轮失败直接改成批准，也未证明动态演奏或生理张力。

## 继承与一次固定政策

继承R1完整blend、政策、结果、网格/权重、键盘、固定pads及12原视角，不重跑R1、不搜索参考、不改材质。Human纠正权威完整保存：LEFT_NATURALNESS=NOT_APPROVED、RIGHT_NEIGHBOR_CLEARANCE=FAIL、FOUR_POSE_HUMAN_APPROVAL=NOT_GRANTED。

R2事前政策 [STATIC_REFINEMENT_POLICY_R2.json](../../../../examples/historical/audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_REFINEMENT_POLICY_R2.json) SHA `f8941e6da289d4aba5f45bc952b77e5612734a210ea8aea351351ebfe4a81af5`；脚本SHA与政策同时在结果前锁定。左手非统一曲度和向内base spread、共同掌位更低；右手root/朝向/五指联合调整，食指/无名指在白键较前区域准备。没有左手三闲置指home-key IK，没有只抬高两指。

净空目标从R1少数低顶点代理改为冻结权重对完整3300顶点的预测与矩形键体距离，覆盖先前漏检指侧点；保存后实测仍独立检查全部88键。数值范围/权重执行前确定，未放宽；左/右各一次确定初始化联合两姿态求解，分别68 / 38 evaluations收敛。无restart、sweep、第二候选或连续Action。

## 接触保持与触点变化

容差原封不动：vertical≤3mm、horizontal≤2mm，且严格在实际可奏区域；固定pad和实际皮肤点分别检查。F#5静置高差15.444mm、前端49.421mm继承。没有重建或修改键盘。

|姿态|任务|固定pad gap R1→R2|R2皮肤gap|水平误差|结果|
|---|---|---|---:|---:|---|
|L1|小指D2|0.586→0.523mm|0.541mm|0|PASS|
|L2|拇指D3|1.556→0.579mm|0.578mm|0|PASS|
|R1|五指准备|无主动触点|准备区/高度通过|按实际可奏面|PASS_SCREEN|
|R2|中指F#5|0.497→0.498mm|0.507mm|0|PASS|

主动触点R2−R1位移XYZ（mm）：L1约[+0.001,-2.199,-0.063]；L2[+10.297,-5.660,-0.977]；R2[+0.595,-6.749,+0.001]。这是在允许键面中选择新触点，不是改琴键或marker。完整固定/皮肤坐标与五指变化见 [BASELINE_CANDIDATE_COMPARISON_R2.json](../../../../examples/historical/audits/piano_hand_static_posture_clearance_refinement_r2/BASELINE_CANDIDATE_COMPARISON_R2.json)。

## 左手三闲置指与掌腕

同相机顶视三指更收拢；侧斜与近景曲度较R1更明显，未见统一钩爪或指尖蜷向掌心。Index/Middle/Ring增量约[8,11,5]、[8.67,13.43,6.86]、[8.56,11.81,5.96]°，分别使用不同基部收拢旋转；这些是RSSF-relative工程增量，不是照片反推的标准人体角度。

闲置指相邻pad空间距R1约38.435/32.691mm，R2约30.027/25.958mm。间距只是几何佐证，自然性来自匹配正常画面的Agent预审，最终由Human判断。共同root高度70→45.6mm，pitch约-6.79→+4.16°；正常侧视掌腕更低，没有高抬整手换净空。

L1/L2 root仍相差0mm/0°，三闲置指形态一致，两个端点主动/准备成立。Thumb MCP饱和从25°减到约17.68°；但L2 thumb IP18°、L1 little MCP32°及spread25°、左roll-6°仍在边界，**没有声称端点紧张全部消除**。边界风险保留给Human，不当成生理极限或新技术阻断。静态共同配置为候选级通过，动态转换未生成/未验证。

## 右手邻键与全局净空

两右姿态D#5旧命中1顶点（3.666mm）、G#5旧命中2顶点（5.619mm）均变为0。保存后全部3300顶点对全部88键部件的>3mm有限筛查：四姿态总命中、掌部、腕部、各指与非目标pad接触均0。没有新增邻键命中。

相同正常近景显示食指/无名指与黑键边缘有了空间；调整包含root/朝向/曲度/准备前后位置，未仅孤立抬指。中指接触点前移且保持F#顶面接触。右手root约[223.68,-124.34,42.22]mm，yaw/pitch/roll约[-7.07,4.40,6.0]°；两姿态root不换位，其他四指几乎不变。

筛查归零不是完整三角碰撞认证；本轮不做hidden geometry forensic。正常三视图未见新明显穿键、悬空、反关节、钩爪或掌部异常。材质和分面显示与R1保持相同，本轮不升级皮肤质感。

## 唯一候选、匹配证据与保护

[STATIC_POSTURE_REFINED_CANDIDATE_R2.blend](../../../artifacts/24c4b9c015ccdb5f87d2.md) 直接打开R1候选后，只改root与现有骨骼旋转，并另存R2。88键对象/顶点/三角面、材质、相机世界矩阵/orthographic尺度/裁剪及渲染尺寸原样继承。四场景frame1，Action数0。保存重新打开后FK最大差<0.000463mm、pad-skin最大漂移<0.036mm，完整intrinsic identity neutral检查均匹配。

[review.html](../../../artifacts/0de25ff5ecf78d4e720f.md) 四姿态/三视角均可切换，左右并排R1 baseline与R2 candidate，同视角同尺度；原R1全部未获Human批准。本轮12个必要新视角加3张有价值合成对照：[左手](../../../artifacts/1978a1f0a66fea109b5c.md)、[右手](../../../artifacts/03415788480fec94fb92.md)、[侧面](../../../artifacts/71a347e422b038d5d5ac.md)。R1原图复用，无旧轮重渲染、无AI/外部图片、无视频。

最终保护 **659 个冻结/继承输入**变化0；三份正式手SHA、钢琴权威、production pointers、旧R1候选/政策/图、MIDI/指法/音频均未改。没有mesh/rest/weights/corrective/driver/helperbone更新或Web集成。详情 [FINAL_ASSET_PROTECTION_R2.json](../../../../examples/historical/audits/piano_hand_static_posture_clearance_refinement_r2/FINAL_ASSET_PROTECTION_R2.json)。

## Q1–Q13（Agent候选预审，非Human批准）

|编号|问题|答案|依据|
|---|---|---|---|
|Q1|唯一 R2 静态候选建立|**YES**|一个新blend，四静态场景；一次政策/初始化，R1未重跑。|
|Q2|L1 小指 D2 接触保持|**YES**|固定0.523mm / 皮肤0.541mm，正确可奏区域。|
|Q3|L2 拇指 D3 接触保持|**YES**|固定/皮肤约0.579mm，正确可奏区域。|
|Q4|左手三闲置指比 R1 明显自然|**YES**|相同视角下收拢且曲度更明显；Agent相对预审，不代替Human批准。|
|Q5|左手掌腕比 R1 更放松合理|**YES**|root z70→45.6mm、掌位更低；正常视角无压键。生理张力未测。|
|Q6|L1/L2 共享合理八度手型|**YES**|候选级：同一root、相同三闲置指形态，端点接触/准备成立；动态未证。|
|Q7|右手五指准备自然|**YES**|候选级正常图未见新钩爪/异常伸指；五指协调调整，非孤立抬指。|
|Q8|R2 中指 F#5 接触保持|**YES**|固定0.498mm / 皮肤0.507mm，正确黑键可奏面。|
|Q9|原 D#5/G#5 干扰解决|**YES**|两右姿态原1/2顶点深度筛查→0；正常对照无明显邻键吞入。|
|Q10|出现新明显钩爪/穿键/悬空/反关节/掌部异常|**NO**|12正常视角预审未见；全部键体>3mm筛查0。|
|Q11|仍有明显 Human-visible blocker|**NO**|Agent匹配视角预审未见；部分端点边界饱和仍供Human审查。|
|Q12|必须修改正式 hand mesh/rig 的证据|**NO**|旋转/root修正已得到候选；无硬几何不可达证明。|
|Q13|最终状态|**STATIC_POSTURE_CLEARANCE_READY_FOR_HUMAN_REVIEW**|这是候选资格，未自动Human-approved。|

## 停止状态

```text
LEFT_L1_STATUS = PASS_CANDIDATE
LEFT_L2_STATUS = PASS_CANDIDATE
LEFT_IDLE_FINGER_NATURALNESS = IMPROVED_CANDIDATE / HUMAN_PENDING
LEFT_OCTAVE_SHARED_POSTURE = PASS_CANDIDATE / HUMAN_PENDING
RIGHT_R1_STATUS = PASS_CANDIDATE
RIGHT_R2_STATUS = PASS_CANDIDATE
RIGHT_DSHARP_CLEARANCE = PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK
RIGHT_GSHARP_CLEARANCE = PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK
PALM_WRIST_CLEARANCE = PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK
NEW_HUMAN_VISIBLE_DEFECT = NO_OBVIOUS_DEFECT_IN_AGENT_PRECHECK
FINAL_STATUS = STATIC_POSTURE_CLEARANCE_READY_FOR_HUMAN_REVIEW
HAND_BASELINES_UNCHANGED = YES
PIANO_BASELINE_UNCHANGED = YES
STOP = HUMAN REVIEW
```

**STOP — HUMAN REVIEW**。未自动进入完整动态演奏生成。Human可继续拒绝自然度；本轮不再调政策或生成第二候选。
