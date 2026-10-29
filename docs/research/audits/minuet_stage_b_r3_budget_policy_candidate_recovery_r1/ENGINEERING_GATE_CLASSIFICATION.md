# 工程门禁与预算分类：WARN_ACCEPTABLE

HARD_ENGINEERING_SAFETY_CONSTRAINT：原总关节工程域及1e-7度检查、原root/时钟/MIDI/指法/键角/音频、实际目标键身份、严重持键失配、危险新穿入、明显运动跳变、冻结资产与保存重开回读一致。全部保持阻断，不因预算复评放宽。

MOTION_PRESERVATION_PREFERENCE：仅当前来源哈希绑定对象的actual_delta相对R2预算偏差。62条采样/14条连续极值保留，依据有限角弧、比例与时段评估，一次分类WARN。没有删除预算检查，没有改求解参数、缩放修正或裁剪角度。

RECOVERY_POLICY.json和POLICY_LOCK.json在任何motion/Blender候选/视频产生前写入。已知更高速度/加速度独立记录WARN，明显可见异常仍然硬阻断。该政策是本轮Human明确授权的追溯复评，原Guard Fix和原R3 FAIL_CLOSED完全保留。

适用范围只有本次source_solver/source_guard SHA所定义的轨迹，不推广为一般容差。政策锁定后不继续调整阈值。若真实回读或视觉预检失败，停止，不重算或修补。
