# RIGHT_HAND_FIRST_WEB_PRODUCT_IMPACT_GO_NO_GO_R1

**FINAL_RECOMMENDATION = KEEP_FROZEN_BASELINE_AND_PROCEED**
**FROZEN_BASELINE_UNCHANGED = YES**

本轮是产品级 Go / No-Go 决策轮，观察而非修复。结论是：当前 frozen Official L1 右手在真实钢琴 motion
中的 first-web F130 类折口，其 Human-visible 产品影响**不足以**支撑推翻 source mesh 或更底层 deformation
architecture，应承认为当前版本的已知限制，冻结右手继续向 LEFT HAND → Three.js / Web → 钢琴产品集成推进。

冻结基线 SHA256 `4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2` 轮前轮后逐字节一致；
本轮写入 `.blend` 数量为 0，未移动 production pointer，未 promotion 新资产，未开始左手，未开始 Web export。

---

## 一、七个必答问题

| # | 问题 | 回答 | 依据 |
|---|---|---|---|
| Q1 | DEFAULT_TEACHING_VIEW 完整 7 秒是否达到明显产品 blocker | **NO** | 主教学视角整手在画面内，虎口折口在该距离不抢夺注意力；7 秒内手型、指序、掌体积均可信 |
| Q2 | NORMAL_ORBIT_VIEW 普通用户是否很容易看到明显不自然 deformation | **NO** | 常规旋转角度下虎口可见较深折痕，但需注视才能察觉，不构成"很容易看到"的破坏性观感 |
| Q3 | REASONABLE_CLOSE_VIEW 是否明显到破坏产品可信度 | **YES** | 正常产品允许的近景下，拇指-食指间深折 + 上方尖角在数帧内清晰可辨，是本轮唯一达到"明显"的问题 |
| Q4 | TRANSIENT 还是 SUSTAINED / REPEATED | **REPEATED** | 非一闪而过：F115 起出现，F127–F168 连续多帧明显，F176 基本恢复，F205 再次出现 |
| Q5 | 当前右手整体 Human-visible 产品质量是否仍可接受 | **YES** | 三视图与 7 秒动作中整体手型、index、thumb、掌体积可信；局部瑕疵未扩散到手部整体 |
| Q6 | foundational rebuild 收益是否明显大于迁移+回归+左手+Web+集成成本 | **NO** | 唯一明显问题局限在 REASONABLE_CLOSE_VIEW；三条 bounded POC 均未证明值得 rebuild |
| Q7 | 最终推荐 | **KEEP_FROZEN_BASELINE_AND_PROCEED** | 承认为已知限制，不推翻 source mesh 或底层 architecture |

Q4 依据真实连续 motion，不只依据 F130 单帧。Q1/Q2 与 Q3 的分歧本身就是本轮的核心产品权衡：
同一缺陷在不同产品观看距离上的判读结论不同，因此它不是"产品不可用"，也不是"根本不存在"。

---

## 二、评估方法与观察条件

### 2.1 观察对象（全部只读）

- 资产：`production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend`
- Action：`PIANOVAM_PHYSICAL_RIGHT_AXIS_CORRECTED_R1`，以 library datablock 追加播放
- Action payload 校验：脚本内 assert 等于 `pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json`
  中已批准的 `b03d02e4f9f4f624c6c3faf1c1c1d53d717eac4770a216d3b1f54af89672cdb0`
- Motion source：PianoVAM v1.2（`INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY`，CC BY-NC-SA 4.0）
- 固定 sample：11.5–18.5 秒 / 7 秒 / 421 observations / 30fps 共 210 帧，本轮未换 sample
- 已批准 corrective 与 driver 自然求值，未做任何强制或新增

### 2.2 禁止事项的执行情况

本轮未修改 mesh、topology、weights、bones、rest pose、corrective、driver、Action、retarget mapping。
未运行 hidden crossing census、normal-dot、R3、true-cap、2127-edge、逐顶点 anatomy proof 或大规模
hidden intersection audit。机器保护只保留 NaN/Inf、gross collapse、tearing、明显 penetration、ZERO restore。

### 2.3 三种产品视图的定义

相机方向逐字复用项目已批准的成熟相机轴，仅改产品级取景距离，不新造夸张或刁钻角度：

| 视图 | 方向来源 | ortho_scale | 中心 | 用途 |
|---|---|---|---|---|
| DEFAULT_TEACHING_VIEW | 已批准 PALMAR_THENAR_CLOSE / PALMAR_FULL 轴 | 0.42 m | 逐帧整手 bbox 中心 | 学生正常观看手部钢琴动作的主教学视角，整手含腕 |
| NORMAL_ORBIT_VIEW | 已批准 FIRST_WEB_OBLIQUE 轴 | 0.22 m | 手心与虎口加权中心 | 用户合理自由旋转到 first-web 可见的角度 |
| REASONABLE_CLOSE_VIEW | 已批准 FIRST_WEB_OBLIQUE 轴 | 0.115 m | 同上 | 正常产品允许的近景检查，非 forensic macro |

取景参数由只读探测 `FRAMING_PROBE_R1.json` 逐帧计算评估后坐标得出：手部 z 向范围 0.223–0.272 m、
x 向 0.123–0.224 m，虎口局部范围 0.024–0.056 m。第一版取景 0.30/0.15/0.075 m 切断了手腕且近景过窄，
已在交付前废弃重取，未作为任何判断依据。

---

## 三、连续 motion 观察结论

### 3.1 缺陷的时间行为（REASONABLE_CLOSE_VIEW）

按 7 秒连续播放与逐帧接触表直接观察，未建立复杂检测器，也不声称毫秒级精度：

- **F110 附近**：该区域表面平滑，无折口。折口不是静态形态缺陷。
- **F115**：折口开始形成，拇指-食指间出现浅折痕。
- **F127–F168**：连续多帧明显，其中 **F130 为本段 peak**，可见拇指-食指间深折加上方尖角；
  **F160 在另一姿态下再次出现深折**，说明它不是单一姿态的偶发结果。
- **F176**：离开该姿态后折口基本消失，表面恢复平滑——**离开后能自然恢复**。
- **F205**：回到张开姿态，折口再次出现，构成反复性证据。

因此 Q4 判定为 **REPEATED**：缺陷随真实钢琴动作反复生灭，持续跨越多个动作区域，而非单帧闪烁。

### 3.2 三视图的判读分歧

- **DEFAULT_TEACHING_VIEW**：整手在画面内，虎口折口在这个观看距离不形成视觉焦点。
- **NORMAL_ORBIT_VIEW**：常规旋转角度能看到虎口折痕，但需要注视才会注意到，不属于"很容易看到"。
- **REASONABLE_CLOSE_VIEW**：折口在正常近景下清晰可辨，是唯一达到"明显"的问题。

### 3.3 整体动作可信度

在同一 7 秒中同时观察整体手型、index、thumb、first-web 与手掌体积：手部整体形态可信，
指序与比例稳定，掌体积无异常膨胀或塌陷，first-web 缺陷没有扩散为手部整体可信度问题。
局部瑕疵存在，但不足以让人感觉"手模型坏掉了"。

---

## 四、机器最低保护（仅必要项）

| 项 | 结果 |
|---|---|
| NaN / Inf | 0（421 observation 全程） |
| gross collapse（collapsed faces） | 0 |
| degenerate edges | 0 |
| ZERO restore | PASS，max 0.000 mm |
| 已批准 corrective / driver | 自然求值，无强制 |
| 本轮写入 .blend | 0 |
| 冻结输入（9 项） | 全部 unchanged |

这些检查只覆盖"是否存在肉眼不可见的灾难性故障"，不构成对 hidden intersections 的证明，
也不用于重新论证已被 Human 关闭的几何裁定。

---

## 五、产品成本进入决策

我们已拥有一个成熟 baseline：Official L1 静态外形 Human-approved、21-bone rig 成熟、
多个代表姿态 Human-approved、real motion retarget 已建立、first-web corrective / driver 已建立，
后续计划镜像左手、Three.js / Web、钢琴产品集成。因此 foundational rebuild 的成本不是零。

| 维度 | 风险等级 | 说明 |
|---|---|---|
| source mesh replacement | HIGH | 需重选 CC0 源并重做全部 Human-approved 外形审核 |
| skin transfer / repaint | HIGH | 现有 21 骨骼权重与已批准 first-web corrective 全部需重新迁移 |
| corrective migration | HIGH | 现有 corrective + driver 需在新拓扑上重建并重新人审 |
| 旧姿态 regression | HIGH | 多个已批准代表姿态需全部重跑并重新批准 |
| motion regression | MEDIUM | retarget mapping 已建立且可复用，但需在新资产上重验 |
| 左手镜像影响 | HIGH | 左手尚未开始；架构级改动会使镜像方案需重新设计 |
| Web export 影响 | MEDIUM | 标准 bone+morph 形式可保留；后置 cage 类方案会显著提高成本 |
| 项目延期风险 | HIGH | 左手、Web、集成三项尚未启动，此时重建将推迟全部后续里程碑 |

这是 LOW / MEDIUM / HIGH 工程风险判断，不含工时数字。

结合既有事实：`FIRST_WEB_DEFORMATION_ARCHITECTURE_REBUILD_ASSESSMENT_R1` 中三条 bounded DESIGN_ONLY POC
（local retopology / helper bone / local cage）均未通过关键帧门槛，`RECOMMENDED_ROUTE = NONE_OF_THREE`。
本轮产品级观察并未提供推翻该结论的新证据。因此 Q6 判定为 NO。

---

## 六、本轮边界与 stop-loss

已遵守：

- 未修改任何正式资产，冻结基线 SHA256 一致
- 未新建 weight / corrective / retopo / helper / cage candidate（各为 0）
- 未新增第四条技术路线，未在评估过程中"顺手修一下"
- 未把 stress-pose GIF、MIDI 或琴键动画当作 performer hand motion；本轮使用既有 421-observation retarget
- 未运行已被禁止的隐形几何审计
- 未移动 production pointer、未 promotion 新资产、未开始左手、未开始 Web export

本轮不是 INSUFFICIENT_PRODUCT_EVIDENCE：完整 7 秒、三种产品视图、逐帧接触表与连续行为证据均已具备，
足以支撑上述产品权衡判断。

---

## 七、交付物

| 文件 | 内容 |
|---|---|
| `RIGHT_HAND_FIRST_WEB_PRODUCT_IMPACT_GO_NO_GO_R1_REPORT.md` | 本报告 |
| `review.html` | Human Review 页面 |
| `product_7s_three_views.mp4` | 三视图同步 7 秒观察（2880×900） |
| `product_7s_default_teaching_view.mp4` | 单视：主教学视角 |
| `product_7s_normal_orbit_view.mp4` | 单视：常规旋转 |
| `product_7s_reasonable_close_view.mp4` | 单视：合理近景 |
| `EVIDENCE_CONTINUOUS_BEHAVIOUR.png` | F130 peak → F176 恢复 → F205 再现 |
| `EVIDENCE_PROBLEM_*.png` | 问题出现 / peak / 另一姿态 peak / 恢复 / 再现 |
| `EVIDENCE_PEAK_F130_THREE_VIEWS.png` | 同一 peak 帧三视图对照 |
| `SHEET_*_Q1..Q7.png` | 三视图逐帧接触表，每视图 7 张共 21 张 |
| `PRODUCT_VIEW_OBSERVATION_R1.json` | 210 帧三视图相机 + 421 observation 最低保护读数 |
| `FRAMING_PROBE_R1.json` | 只读取景探测 |
| `VIDEO_VERIFICATION_R1.json` | 视频时长/帧数核验 |
| `FINAL_ASSET_PROTECTION_R1.json` | 冻结资产与保护输入复核 |

---

**STOP — HUMAN REVIEW**

不自动执行最终推荐，不自动开始左手、Web export 或产品集成，等待 Human 决策。