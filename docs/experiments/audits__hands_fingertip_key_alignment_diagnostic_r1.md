# audits/hands_fingertip_key_alignment_diagnostic_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 合法面不是整键AABB：白键由前部宽矩形与后部避让黑键的窄矩形组成，前后分界中性Y约49.421377mm；黑键是实际顶面矩形。矩形包含贴近边界的位置，没有教学用边缘余量要求。例：A4前部X=108.147872～131.236922mm；后部X=113.360283～126.024511mm。相邻白键前部缝宽约0.849430mm。原生成器曾对白键目标加3mm横向/7mm纵向inset、黑键加2/2mm，但那是**单marker生成目标**，不能当作整指皮肤的安全余量。见`EventCoordinator.__init__/target/tasks`（链接见原报告）。

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

> | 事件 | 目标 / MIDI | 指号 | ACTIVE展示时间 s | pad最小侧边余量 mm | HOLD pad横向比例（左0%） | HOLD末端顶点投影面外比例 | 三采样邻黑键顶点深度峰值 mm |

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

## 技术路线

> 设p为真实skin pad，先用原琴键Action的实际旋转绕press_pivot反变换到键的中性坐标；在注册的可奏面矩形并集中选最近面。横向误差为 `1000 × ||p.xy − clip(p.xy, rectangle)||`；垂向gap为 `1000 × (p.z − surface.z)`。面内任意位置横向误差都为零。现沿用的0.03mm是**面外距离容差**，不是离键中心的误差；3mm是gap的绝对上限，允许有限悬空或入面，不是物理接触/压力证明。本轮48采样gap范围**−0.017307～+0.916530mm**。生产/B01实现还要求inside为真，所以并没有利用0.03mm允许在面外通过。

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

## 测试结论

> 核心原因是：原检测测量“固定palmar skin顶点到合法运动键面的距离”，并不验收整根手指的皮肤位置、末端轮廓、入键方向或邻键净空。当前48个活动接触采样全部PASS，与闲置食指深穿黑键、活动中指邻键侵入同时成立。没有证据把这些问题归咎于MIDI键身份或指法串位，也不能把它们都解释为俯视错觉。

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

> 历史计算有两种身份：生成FK以远端骨矩阵变换local_pad_point得到虚拟marker；真实验收读取变形网格V[mesh_vertex]。本轮实际测两者，48采样最大差仅**0.067697mm**，不足以解释数毫米的偏边/穿键，不支持“骨点代替真实pad导致全部错误”的结论。

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

## 失败原因与证据边界

> 核心原因是：原检测测量“固定palmar skin顶点到合法运动键面的距离”，并不验收整根手指的皮肤位置、末端轮廓、入键方向或邻键净空。当前48个活动接触采样全部PASS，与闲置食指深穿黑键、活动中指邻键侵入同时成立。没有证据把这些问题归咎于MIDI键身份或指法串位，也不能把它们都解释为俯视错觉。

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

> E．原因分类：A映射错误**未发现**；B接触目标定义/教学覆盖缺口**确认**；C整指姿态与皮肤宽度造成边缘/黑键关系问题**有几何证据**，但自然度与最理想入键方向仍须Human判断；D非活动指避障不足**确认**；E二维遮挡**同时存在**，但这几处已证明不是仅投影。未对整曲全部遮挡逐一判真伪，未测真实压力接触面积。

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

## 后续建议

> 来源必须分阶段：原A2 `04_diagnostics.py`（链接见原报告） 中工程失败列表曾用横向>2mm及虚拟marker绝对gap>3mm；后续C2 `06_apply_validate.py`（链接见原报告） 明确同时检查marker/skin绝对gap≤3mm、横向<0.03mm；本轮复用的是B01 `blender_support.contact`（链接见原报告） 的实际skin、inside、0.03/3mm口径。不能把后续较严的局部检查追溯写成原C1整曲已获批准的安全合同。

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

> 原角色优先级为ACTIVE→RELEASE→PREPARE→IDLE；PREPARE名义提前180ms，RELEASE最多跟随40ms，会被同指新ACTIVE覆盖。下面列实际优先级后的区间；ACTIVE见上表，其余同指时间为IDLE。这避免把连续同指G4重击的前一ACTIVE误标成下一音PREPARE。

出处：[FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)

## 原报告与关键代码

- [audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md](../research/audits/hands_fingertip_key_alignment_diagnostic_r1/FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/blender_support.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/blender_support.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/check_midi.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/check_midi.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/common.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/common.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/diagnose.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/diagnose.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/make_media.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/make_media.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/ninth_media.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/ninth_media.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/ninth_still.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/ninth_still.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/run_stage.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/run_stage.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/supplement_geometry.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/supplement_geometry.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/verify_media.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/verify_media.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/verify_projection.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/verify_projection.py)
- [audits/hands_fingertip_key_alignment_diagnostic_r1/write_report.py](../../src/legacy/audits/hands_fingertip_key_alignment_diagnostic_r1/write_report.py)

## 输入、输出与大型证据

该目录原始成员 79 项；拟公开身份记录 71 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
