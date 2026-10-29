# 教学示范审核标准 R1

原则：PEDAGOGICALLY_CORRECT_AND_HUMAN_VISIBLE_FIRST。模式：PEDAGOGICAL_AUDIT_ONLY。

PASS：实际候选指与真实目标键一致；准备、触键、键下沉、持键及释放有相互支持的实际 skin、运动键面和正常尺度画面证据；未发现会误导初学者的可见错误。有限采样 PASS 不等于连续几何证明。

WARN：轻微或教学影响不明的问题；必须说明学习影响与是否需要教师判断。BLOCKING：正常教学、俯视或侧斜视角下，慢放或暂停能把错误指位、穿指、穿键或虚假触键传达给学生；不能因原速不明显降级。UNKNOWN：证据不足，不算 PASS。

本轮直接打开唯一 Lightweight R1 Blend，只评估已保存 Action；23 音 × 6 阶段（准备 -80ms、NOTE_ON、+40ms、持键中点、NOTE_OFF、+60ms）检查实际变形网格。使用已有真实皮肤顶点及其固定 6mm 邻域，对实际键轴旋转后的可奏键面进行核查。局部顶点不是抽象 pad，也不是完整连续表面接触证明；微小正间隙和浅层负间隙不自动阻断。

三视角原视频 SHA256 对照通过，357 帧、60fps、5.95s。音乐时长 5.142852s；video_time = MIDI_source_time + 0.35s。事件时间由原 MIDI 逐事件/tempo map 核实。视频近邻帧可能在 NOTE_ON 前后 8.34ms 内；界面明确显示事件时间与原帧时间，不把近邻帧说成精确事件子帧。

教学结论按音符自己的主动指及交接评定，整段画面的其他缺陷单独列出。三视角切换暂停并保持同一原时间；单播放器避免多播放器时钟漂移。逐帧显示原渲染 PNG，不依赖浏览器 MP4 seek 的帧精度。连续播放速度由浏览器 playbackRate 实现，不生成新中间姿态。

本轮视觉检查是原帧静态/序列检查，并非人类连续观看实验。各速度主观显著性仍需 Human 操作确认；无证据不编写“半速已明显”的观察。指法符合候选，不代表专业最优或适合所有初学者；FINGERING_PROFESSIONAL_APPROVAL = DESIGN_PROVISIONAL。教师需确认跨指、同指重复音、闲置指伸展及左手手型。

冻结资产、MIDI、历史结论不改。工程历史 FAIL_CLOSED / NOT_APPROVED 保留。READY_FOR_HUMAN_PEDAGOGICAL_REVIEW 仅表示审核证据可交付，绝不等于教学通过。最终教学质量 HUMAN_PENDING。
