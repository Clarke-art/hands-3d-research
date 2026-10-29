# RIGHT_HAND_LBS_VS_DQS_REAL_MOTION_AB_R1

预分类：**DQS_WORSE**。当前步骤结束于 **STOP — HUMAN REVIEW**。此结论为代理的普通实体视图判断，四项 Human 答案未填写，PRODUCTION_PROMOTION = NO。

DQS 在部分动作帧明显减轻 LBS 的小阶梯凹折，但 F130 仍有大的角状折口，虎口桥面更鼓起，形成更宽且突出的片状折边。按本轮“明显 first-web distortion / 更差”的分类规则，优先归 DQS_WORSE。局部变平的收益已保留在下面的逐帧说明中；不能据此认定 DQS 完全无效，也不能认定 LBS 体积损失是唯一或主要根因。纯 Preserve Volume 开关没有使这段动作达到自然可接受程度。

冻结基线实际读取：LBS，ArmatureModifier.use_deform_preserve_volume = False；SHA256 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`。仅从该基线创建独立测试，再从 axis-corrected test 追加原 Action，未重新 retarget。上一轮失败候选未加载。新增 corrective = 0。

A_LBS / B_DQS 的对象变换完全一致，mesh / UV / 顶点索引 / weights / materials / Key datablock / approved driver 均共享或逐项一致。Rest armature datablock 共享，两份 pose rig 使用同一个 Action。B 的 Armature target 绑定到其等价 rig；归一化 target 身份后，全部 modifier RNA 设置和顺序只差 Preserve Volume。驱动目标保留原 A rig，未改 driver：所有 421 个观察点和六个姿态均逐骨确认 A/B pose matrices 完全一致，因此共享 corrective 的自然求值对 A/B 相同。测试中不应独立改变其中一份 pose rig。Blender 中两份测试对象位于同一位置，单独查看时可用 Outliner 隐藏另一份 mesh；审核渲染从各自 evaluated mesh 生成。

Shape keys 在原 modifier stack 前求值，modifier 未新增、未应用、未重排。原批准 corrective `FIRST_WEB_OPPOSITION_CREASE_R1` 自然求值；关键帧数值见 KEYFRAME_LBS_VS_DQS_R1.json，全部观测点见 APPROVED_CORRECTIVE_NATURAL_VALUES_R1.json。

|关键帧|DQS 普通可见检查|
|---|---|
|F130|DQS 减少小阶梯，但残留较大的角状折口，桥面鼓起并形成更宽、突出的片状折边；仍为明显 blocker。|
|F76|阶梯凹口减轻，桥面更饱满；仍有深沟及 upper-web 尖薄折边。|
|F205|部分凹折变平，斜视仍有角状峰和折沟；未达到自然可接受。|
|F31|桥面稍平顺；斜视深沟与尖折仍在。|
|F61|低缺陷对照基本保持，只有轻微形状和 shading 差异。|

帧时序：Ff 对应 observation index 2×(f−1)，源 frame 690+2×(f−1)，源时间 11.5+(f−1)/30 秒。Action 端点 F211 与半帧保留不变。视频 F1–F210 / 30fps，时长精确 7.000 秒，两组左右并排 LEFT=LBS、RIGHT=DQS。421 观测点全部用于最低安全检查，未删 key、改 smoothing 或时间。

六个旧姿态 ZERO、INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L1/L2/L3，代理初判保留可接受外形。CMC_OPP_30 / FULL_OPP_L3 的 crease 稍尖，留待 Human 判断。ZERO A/B 最大位置差 0.000358326 mm，为浮点求值量级，四个 ZERO 视图无明显外形变化；两组恢复到各自 ZERO 的误差均为 0 mm。

最低机器安全：两组 421 个观测点 + 六姿态 NaN/Inf = 0、collapsed face = 0、degenerate edge = 0、ZERO restore = PASS。普通实体视图 gross visible tearing = 0（代理检查，非 hidden forensic 证明）。未执行 volume integral、strain/crossing/normal-dot census、R3、true-cap、2127 edges 或 Stage6 重验。DQS_NEW_VISIBLE_DEFECT_COUNT = 1 表示一个问题类型：更加突出的片状虎口折边，不表示异常帧计数。指尖问题仍 DEFERRED。

渲染相机使用之前从 unchanged BEFORE motion 得到的相机记录；没有加载失败候选。A/B 每帧使用相同相机与 framing。使用统一 Workbench 中性实体材质、display-only smooth shading、无 cavity、shadow intensity 0；材质与网格资产本身未更改。关键帧有 frontal first-web close、palmar/thenar close、oblique、palmar context；每姿态有 palmar full、thenar close、dorsal full、first-web close。

交付：review.html；两视角同步对照视频；40 张关键帧、48 张旧姿态、840 张完整动作 matched renders；独立 test blend 与脚本、数据验证。基线与源数据 SHA256 前后保持不变。

Human review：

1. DQS / Preserve Volume 是否明显改善真实 motion 的虎口深折？YES / NO
2. DQS 下完整 7 秒虎口是否已自然可接受？YES / NO
3. DQS 是否引入新的明显鼓包、扭曲或旧姿态回退？NO / YES
4. 是否值得把右手产品 deformation 从 LBS 改为 DQS 继续验证？YES / NO

按照请求在此停止。不推广、修改正式基线或尝试 hybrid。若 Human 确认此路线无价值，后续 architecture rebuild assessment 需要新的独立任务；本轮不执行。
