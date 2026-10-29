# 唯一保存轨迹的确定性恢复：PASS

NEW_SOLVER_CALLS = 0。实际使用Guard Fix轮原SOLVER_RETURN_CHECKPOINT.json和SOLVER_AND_GUARD_DIAGNOSTICS.json；其780参数、113支持点、827×20总角度均未改。逐位重建身份通过，原root/key/time数组完全复用，未缩放、裁剪、改目标或逐音补pose。

只有一份DESIGN_ONLY Blend和一次实际Action烘焙。前两次Blender调用在烘焙前因旧结构核验辅助函数未完整导入停止，没有Action关键帧或保存候选；新目录补齐rename_normalize/re与intrinsic只读依赖后，第三次完成唯一烘焙。没有调用优化器或改变数值轨迹。日志scene.log/scene_recovery.log/scene_verified.log原样保留。这些是核验代码依赖修复，不是第二数值候选。

保存重开皮肤pad对原FK最大差0.000916053mm，真实键几何最大差0.000009321mm；15个骨旋转矩阵覆盖全部20DOF，最大矩阵元素差1.9e-07，root相对R2矩阵差0。四静态core、手结构与88键geometry均不变。

额外身份验证只读重开，不重存候选，SHA保持a4c51e660725335922916c179d65883146eb249848f95793c566d1e2d5ebfe63。三相机位置/方向/尺度与R2最终交付视频相同（俯视沿用已交付0.60尺度）。视频每视角357帧/60fps/5.95秒；音乐本体5.142852秒。原R2视频不重新编辑，新旧解码音频哈希全部相同。

候选路径：<HANDS_ROOT>\audits\minuet_stage_b_r3_budget_policy_candidate_recovery_r1\STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend。Human可审核，但自然度不由本报告代填PASS。
