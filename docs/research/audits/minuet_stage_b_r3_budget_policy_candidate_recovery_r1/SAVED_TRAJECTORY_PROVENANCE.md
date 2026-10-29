# 保存轨迹来源：完整可信，可确定性恢复

唯一来源为Guard Fix轮的SOLVER_RETURN_CHECKPOINT.json与SOLVER_AND_GUARD_DIAGNOSTICS.json，solver nfev=20/status=2/success=True/ftol，原780个actual_delta参数及113支持点齐全。全部源交付manifest与生成锁哈希一致。

用原数值评价器只读重建，与保存827×20总角度逐位相同；actual_delta与reference之差也逐位相同。原R2 motion的root、旋转、键角、时间数组和源MIDI身份核验通过。重建没有调用任何优化器。

本轮恢复的是最新Guard Fix失败输出，绝不把它当作更早R3未保存的失败现场。原所有FAIL_CLOSED记录只读。

恢复采用原拟输出配方：原R2数组复制，仅在原活动窗口内写入保存总q的弧度；窗口外保留原弧度字节。没有缩放、裁剪、改root、改接触目标或手工补姿态。原生Blender动作回读验证仍是后续硬门禁。
