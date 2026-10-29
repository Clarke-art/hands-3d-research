# 最小真人参考依据（摆姿前）

本轮先实际查看两张 Hands 已存真人照片，再提取并实际查看已许可本地 PianoVAM 视频的 4.0s、10.0s 两帧。没有使用 AI 手图作为依据，没有把前轮候选当作自然模板。

1. MusicRadar / Daniel Griffiths 右手五指照片。项目存档 audits/piano_hand_posture_reference_and_static_feasibility_r1/_research/right_source_view.png；来源及署名见同目录 REAL_PIANO_REFERENCE_MANIFEST_R1.md；原图 https://cdn.mos.cms.futurecdn.net/N2M4LgaytGt4Vza8r9eFTB.jpg 。可见各长指弧度不同，关节轮廓连续，拇指在白键前部。它不是当前 G4 持键任务，也不能从此求三维角度、压力或腕高。照片未取得再发布许可，不复制到本轮对外对照图。
2. PiaDOOR 左手八度准备真人照片。项目存档同目录 _research/left_source_view.png；原页 https://piadoor.com/en/piece/2/basic/ 。只参考不同手指弧度可不同，不能把承担中间 E 的手指一概当 IDLE，也不当右手当前任务模板。
3. PianoVAM v1.2 真实演奏本地视频 references/piano_motion/pianovam_sample_r1/Video/2024-03-04_03-46-36.mp4。实际查看本轮提取 REFERENCE_PIANOVAM_4_0.png 与 REFERENCE_PIANOVAM_10_0.png。可观察整手随音位变化、指间距离和曲度并不固定；4.0s 有明显运动模糊，不能测关节角；10.0s 也未用音频/MIDI定位哪一指处于严格 ACTIVE。没有声称看过完整视频或核实它与当前 G4 场景一致。资料为 PianoVAM by Kim et al., ISMIR 2025, https://huggingface.co/datasets/PianoVAM/PianoVAM_v1 ，CC BY-NC-SA 4.0，INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY；本轮仅做定性内部观察，没有复用动作或晋升商业资产。
4. 本轮联网实际读取 Practising the Piano / Preparing to Play Octaves：https://practisingthepiano.com/preparing-to-play-octaves/ 。公开教师说明强调关节支撑、避免外扭和腕部灵活。这里只转移定性观察原则，不把八度练习作为单拇指 G4 的姿态处方。没有访问付费课程。Hoffman 相关页正文未能由本轮工具读取，不作为新增已核查证据。

采用的观察原则：优先连续、不过分钩扣的指根—PIP—DIP轮廓；适度指间距；长指允许不同曲度；避免依靠侧摆极限或指尖强卷来躲障碍；手掌/腕部若需改变，必须同时复核活动触键。没有据照片编造人体关节数值，没有声称取得本任务侧面腕高或完整前臂人体工学标准。所有选定角度均是本模型人工摆姿读数，非人体医学标准。最终自然性由 Human 审核。
