# DUAL_HAND_SYNCHRONIZED_REAL_MOTION_VALIDATION_R1

**结论：DUAL_HAND_SYNCHRONIZED_MOTION_VALIDATED。Agent 预检完成，最终 Human Review 待定。**

本轮直接加载已批准左右手 Action，没有重定向、平滑、轴修正、旋转限幅、重建或改变采样。左手 Action 的 Human approval 来自本轮明确指令；旧审计文件保留原样。

| 问题 | 检查 | 结果 |
|---|---|---|
| Q1 | 同 recording / 11.5–18.5 秒 / 421 observations | YES |
| Q2 | RIGHT Action identity match | YES |
| Q3 | LEFT Action identity match | YES |
| Q4 | Blender timeline / half-frame EXACT_SYNC | YES |
| Q5 | CROSS_HAND_CHANNEL_LEAKAGE = 0 | YES |
| Q6 | 完整 7 秒可见时序自然 | YES — Agent 预检；Human 最终审核待定 |
| Q7 | 右手保持已批准 motion 质量 | YES |
| Q8 | 左手保持已批准 motion 质量 | YES |
| Q9 | 双侧 first-web 无新增 blocker | YES |
| Q10 | 新增系统性 jump / flip / handedness error / timeline drift | NO |
| Q11 | LEFT_FINGERTIP_FAST_BEND | PRESENT / DEFERRED |
| Q12 | RIGHT_FINGERTIP_FAST_BEND | PRESENT / DEFERRED |
| Q13 | 最终分类 | A — DUAL_HAND_SYNCHRONIZED_MOTION_VALIDATED |

## 证据与重开验证

[审阅页](../../../../examples/historical/audits/dual_hand_synchronized_real_motion_validation_r1/review.html)提供完整教学视图、左右细节视图、原录影与真实 landmarks 同步对照。三个视频各 210 帧、30 fps、7.000 秒，已完整解码并验证浏览器播放到终点。EARLY / MID / LATE 各三行，未批量复制截图。

双手分别单独运行与合并运行的 421 × 3300 个顶点均数值精确一致；左右 mesh、Armature、Action slot、corrective driver 目标严格独立，无 NLA、跨手约束或错误通道。左手亦与上一轮已批准的全部 421 个保存观测数值精确一致。

独立 validation blend 保存重开后，两套 Action payload 逐项精确匹配。关闭 Action、移除仅审阅用外部 parent、恢复 ZERO 后，mesh、顶点顺序、拓扑/面序、UV、原生 shading、属性、全部权重、modifier、rig/rest/语义、pose、corrective geometry/driver 与正式 baseline 匹配。容器 collection membership、故意附加的 Action 不属于静态产品比较；Blender append 改变的只读 modifier is_override_data 标记单列排除。Action use_fake_user 是容器保留标记，不参与动画 payload；没有改变 key 或 channel 来消除差异。

| 手 | 原批准 Action payload SHA256 = 保存重开 SHA256 |
|---|---|
| R | `b03d02e4f9f4f624c6c3faf1c1c1d53d717eac4770a216d3b1f54af89672cdb0` |
| L | `d3061e8effcb6f7ad0a7759ae0f9aa75a196d295a072e83c617a2c8ce4c29ac8` |

右手 hash 对照原 R2 promotion 中记录的已批准 Action hash；左手此前没有独立 payload digest，因此先核对已批准 source blend 的固定 SHA，再直接读取其完整 Action payload，与 append 和保存重开逐项比较。本轮新记录的左手 digest 不冒充历史已有字段。

## 同步与布局

SOURCE_TIMELINE_PARITY = EXACT。source index 690+i，timestamp 11.5+i/60，双方 Blender frame 1+i/2，i=0..420。所有 64 个 quaternion channels 各含 421 个半帧 key；30 fps 输出使用 i=0,2,...,418。18.5 秒端点保留在 key 211；视频末帧采样 18.4666667 秒并持续至 18.5 秒。没有单手手动时间移位。Physical RIGHT=JSON Left，Physical LEFT=JSON Right，继承已批准映射。

**DUAL_HAND_REVIEW_OFFSETS = DISPLAY_ONLY；NOT PIANO-SPATIALIZED。** 使用两个外部 empty parent 的静态平移，将双手居中并排。产品自身局部 transform、骨骼与 Action 未改。移除显示平移后，保存重开的最大浮点偏差右手 0.0004246830940246582 mm、左手 0.0004209578037261963 mm，低于 0.001 mm 容差。偏移数值见 RENDER_INPUT_R1.json，不能用于产品 root、真实双手距离或钢琴标定。

## 最低检查与可见范围

左右各 421 observations：NaN/Inf、gross collapse、degenerate edge/triangle、gross tearing 阈值触发均为 0；ZERO restore 为 0 mm。阈值明确记录于 MINIMUM_SAFETY_R1.json，仅为粗大异常筛查，不构成人体解剖或隐藏穿插证明。未开启 hidden crossing、normal-dot 或其他历史 forensic 调查。

审阅证据中未见由组合引入的 first-web、thumb、index、palm 或 finger-chain 系统性退化；全观测变形一致性同时说明组合没有增加新变形。左手原指尖 fast bend（约 16.5–17.0 秒）保留 PRESENT / DEFERRED，右手原 fast bend 同样保留 PRESENT / DEFERRED，没有修复或重新调轴。全片播放可核对节奏，但 Agent 的可见预检不等同于最终 Human approval 或逐帧人工无缺陷证明。

右手 corrective 自然范围 [0.0, 0.040610138326883316]，左手为 [0,0]。左手 driver 和 corrective 保持精确，但本片段没有验证其主动范围。

## 许可、隔离和正式资产

PianoVAM v1.2，固定 recording 2024-03-04_03-46-36。Kim Yonghyun、Park Junhyung、Bae Joonhyung、Kim Kirak、Kwon Taegyun、Lerch Alexander、Nam Juhan，ISMIR 2025。来源与原 attribution 保存在 references/piano_motion/pianovam_sample_r1/ATTRIBUTION_AND_USAGE_R1.md。CC BY-NC-SA 4.0；INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY。新增衍生材料只做双手组合、静态审阅布局、验证及视频合成。Action、视频、scene 全部保留在 audit，未 promotion 商业 motion。

没有开展 keyboard installation、contact、root/wrist 世界位置解算、MIDI-to-key、fingering、glTF、Three.js 或正式集成。源 landmarks 为 video-estimated non-metric 2.5D；本轮仅验证两个 skeleton tracks 的同时间轴同步播放，不声称音符、指法、落键或琴键接触正确。

最终 SHA256：

- RIGHT R2：`c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0`
- LEFT R1：`54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7`
- RIGHT R1 fallback：`4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2`

所有受保护输入重新核对，见 FINAL_ASSET_PROTECTION_R1.json。两个正式 pointer 未修改；正式 baseline 保持 ZERO / RSSF，无 PianoVAM runtime dependency。

NEXT_STAGE_READY = PIANO_KEYBOARD_SPATIAL_ANCHOR_AND_CONTACT_VALIDATION。该阶段未启动。

**STOP — HUMAN REVIEW**
