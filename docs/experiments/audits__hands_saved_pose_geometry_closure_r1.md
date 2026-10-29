# audits/hands_saved_pose_geometry_closure_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> 下表深度与 BVH 均指活动小指对**全部非目标键**，峰值及残余相交均在 E5。深度单位 mm；箭头为原 C1 → 保存校正。同刻使用相同网格、键体与诊断口径。

出处：[FINAL_GEOMETRY_CLOSURE.md](../research/audits/hands_saved_pose_geometry_closure_r1/FINAL_GEOMETRY_CLOSURE.md)

> 逐姿态三个维度分别为：**PASS / RESIDUAL / PASS**、**PASS / RESIDUAL / PASS**、**PASS / CLEAR / PASS**。其中 CLEAR 仅限活动小指与非目标键，不能解释为整手历史缺陷清除。

出处：[FINAL_GEOMETRY_CLOSURE.md](../research/audits/hands_saved_pose_geometry_closure_r1/FINAL_GEOMETRY_CLOSURE.md)

## 技术路线

原报告未单独概述路线；以下实现文件与原报告共同界定方法，不能由文件名推断算法成功：

- [analyze_cached_geometry.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/analyze_cached_geometry.py)
- [common.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/common.py)
- [depth_math.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/depth_math.py)
- [depth_math_before_index_fix.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/depth_math_before_index_fix.py)
- [final_protection.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/final_protection.py)

## 测试结论

> ORIGINAL_STATIC_CONTRACT = PASS

出处：[FINAL_GEOMETRY_CLOSURE.md](../research/audits/hands_saved_pose_geometry_closure_r1/FINAL_GEOMETRY_CLOSURE.md)

> NO_NEW_WHOLE_HAND_REGRESSION = PASS

出处：[FINAL_GEOMETRY_CLOSURE.md](../research/audits/hands_saved_pose_geometry_closure_r1/FINAL_GEOMETRY_CLOSURE.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> 6. **足以作为 Human 考虑另行授权一次限定连续重组验证的静态依据**，不是启动授权或连续安全证明。后续仍须独立验证事件之间的接触、全时段几何、角色协调和 Human 自然度，保留微小残余及整手历史缺陷。

出处：[FINAL_GEOMETRY_CLOSURE.md](../research/audits/hands_saved_pose_geometry_closure_r1/FINAL_GEOMETRY_CLOSURE.md)

## 原报告与关键代码

- [audits/hands_saved_pose_geometry_closure_r1/FINAL_GEOMETRY_CLOSURE.md](../research/audits/hands_saved_pose_geometry_closure_r1/FINAL_GEOMETRY_CLOSURE.md)
- [audits/hands_saved_pose_geometry_closure_r1/analyze_cached_geometry.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/analyze_cached_geometry.py)
- [audits/hands_saved_pose_geometry_closure_r1/common.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/common.py)
- [audits/hands_saved_pose_geometry_closure_r1/depth_math.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/depth_math.py)
- [audits/hands_saved_pose_geometry_closure_r1/depth_math_before_index_fix.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/depth_math_before_index_fix.py)
- [audits/hands_saved_pose_geometry_closure_r1/final_protection.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/final_protection.py)
- [audits/hands_saved_pose_geometry_closure_r1/launch_supplement.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/launch_supplement.py)
- [audits/hands_saved_pose_geometry_closure_r1/preflight.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/preflight.py)
- [audits/hands_saved_pose_geometry_closure_r1/preflight_attempt_0.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/preflight_attempt_0.py)
- [audits/hands_saved_pose_geometry_closure_r1/preflight_attempt_1.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/preflight_attempt_1.py)
- [audits/hands_saved_pose_geometry_closure_r1/supplement_blender.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/supplement_blender.py)
- [audits/hands_saved_pose_geometry_closure_r1/verify_certificates.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/verify_certificates.py)
- [audits/hands_saved_pose_geometry_closure_r1/verify_quad_diagonals.py](../../src/legacy/audits/hands_saved_pose_geometry_closure_r1/verify_quad_diagonals.py)

## 输入、输出与大型证据

该目录原始成员 44 项；拟公开身份记录 36 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
