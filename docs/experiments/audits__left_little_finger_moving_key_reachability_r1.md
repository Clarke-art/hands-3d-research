# audits/left_little_finger_moving_key_reachability_r1

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> CONTACT_PHASE_MEASUREMENTS_R1.json包含185个原轨迹样点及两次D2的九个关键阶段，记录实际键面位置、fixed/skin pad、键法向及世界竖直gap、严格可奏区、关节余量、root矩阵和并发任务。正式pad定义、D2/D3几何、L1/L2姿态均存入STATIC_ANCHOR_PROTECTION_R1.json。root Empty包含原生坐标绑定变换，其translation不是掌腕原点；报告另从native_to_canonical逆变换派生共享腕部原点，约[−220.754,−94.601,45.601]mm。

出处：[LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)

> 依赖修复：首次启动在任何求解前因cp312 SciPy不能用于Blender CPython3.13退出；只安装同版本SciPy1.18.1的cp313包至本审计目录，记录于IMPLEMENTATION_REPAIR_R1.json。运动政策、seed、bounds、目标权重与求解参数未改。

出处：[LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)

## 技术路线

> D. CONTACT_TARGET_OR_EVALUATION_ERROR = NOT_REPRODUCED。实际child mesh顶平面与旧运动键面gap最大差0.000001373mm，键体世界顶点最大差0.000017059mm，关节分解与原轨迹最大差0.00001165°。旧pivot错误已修复，不能把历史实现错误当作当前原因。

出处：[LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)

> 最终参数：下降3.500000mm，pitch-0.614045°，前后位移-0.001688mm。一次求解 nfev=18、residual calls=139、cost=109504.902574，无restarts。优化器结束不等于验收通过。

出处：[LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)

## 测试结论

> B. FINGER_TRAJECTORY_PLANNING_FAILURE = UNPROVEN。旧轨迹是一次局部有界拟合，没有全局可达性证明；本轮没有另试小指IK。

出处：[LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)

> 小指full-down角度[MCP,PIP,DIP,spread]约[31.5,21.9853,0,24.5]°；工程上界[32,32,20,25]°。在原位置每增加1°，MCP/PIP/DIP的局部z灵敏度分别约−0.4422/−0.1073/+0.0054mm。PIP同时朝键右缘漂移约+0.3582mm/°，指腹距右缘约1.003mm。剩余角度的线性估计约只能再下降1.33mm，且尚未计侧向限制；这是局部导数证据，不是非线性全局下界，也不是人体生理结论。

出处：[LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)

## 失败原因与证据边界

> 最可能原因为 **A. FIXED_ROOT_REACHABILITY_LIMIT / SUPPORTED**，限定在继承的小指轨迹与工程域。候选保持小指全部关节轨迹不变，仅通过共享掌腕随动和拇指协调，两次D2最大皮肤gap由7.689142降至2.969126mm。这确证掌腕随动对原轨迹的因果作用，但不证明所有固定root关节路径都不可达。

出处：[LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)

> C. CONSTRAINT_CONFLICT：原失败的全局约束不可兼容仍UNPROVEN；本候选“正确触键与邻键净空未能同时满足”已CONFIRMED。D2原失败在0.735秒已发生，早于D3准备0.830秒，所以拇指重叠不是原失败必需原因。

出处：[LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)

## 后续建议

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 原报告与关键代码

- [audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md](../research/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_FINGER_MOVING_KEY_REACHABILITY_R1_REPORT.md)
- [audits/left_little_finger_moving_key_reachability_r1/_deps313/scipy/fft/_duccfft/LICENSE.md](../../environment/OMITTED_SCIPY_RUNTIME.md)
- [audits/left_little_finger_moving_key_reachability_r1/01_readonly_diagnosis.py](../../src/legacy/audits/left_little_finger_moving_key_reachability_r1/01_readonly_diagnosis.py)
- [audits/left_little_finger_moving_key_reachability_r1/02_lock.py](../../src/legacy/audits/left_little_finger_moving_key_reachability_r1/02_lock.py)
- [audits/left_little_finger_moving_key_reachability_r1/03_probe.py](../../src/legacy/audits/left_little_finger_moving_key_reachability_r1/03_probe.py)
- [audits/left_little_finger_moving_key_reachability_r1/04_verify_render.py](../../src/legacy/audits/left_little_finger_moving_key_reachability_r1/04_verify_render.py)
- [audits/left_little_finger_moving_key_reachability_r1/05_measure.py](../../src/legacy/audits/left_little_finger_moving_key_reachability_r1/05_measure.py)
- [audits/left_little_finger_moving_key_reachability_r1/06_media.py](../../src/legacy/audits/left_little_finger_moving_key_reachability_r1/06_media.py)
- [audits/left_little_finger_moving_key_reachability_r1/07_finish.py](../../src/legacy/audits/left_little_finger_moving_key_reachability_r1/07_finish.py)
- [audits/left_little_finger_moving_key_reachability_r1/_deps313/scipy/conftest.py](../../environment/OMITTED_SCIPY_RUNTIME.md)
- [audits/left_little_finger_moving_key_reachability_r1/_deps313/scipy/version.py](../../environment/OMITTED_SCIPY_RUNTIME.md)
- [audits/left_little_finger_moving_key_reachability_r1/_deps313/scipy/_distributor_init.py](../../environment/OMITTED_SCIPY_RUNTIME.md)
- [audits/left_little_finger_moving_key_reachability_r1/_deps313/scipy/__config__.py](../../environment/OMITTED_SCIPY_RUNTIME.md)
- [audits/left_little_finger_moving_key_reachability_r1/_deps313/scipy/__init__.py](../../environment/OMITTED_SCIPY_RUNTIME.md)

## 输入、输出与大型证据

该目录原始成员 1587 项；拟公开身份记录 1535 项。
- `audits/left_little_finger_moving_key_reachability_r1/evaluated_probe.npz` → `hands-research-r1-selected-001.zip` / `payload/audits/left_little_finger_moving_key_reachability_r1/evaluated_probe.npz`
- `audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_MOVING_KEY_PROBE_R1.blend` → `hands-research-r1-selected-001.zip` / `payload/audits/left_little_finger_moving_key_reachability_r1/LEFT_LITTLE_MOVING_KEY_PROBE_R1.blend`
- `audits/left_little_finger_moving_key_reachability_r1/_deps313/scipy/special/tests/data/boost.npz` → `hands-research-r1-selected-001.zip` / `payload/audits/left_little_finger_moving_key_reachability_r1/_deps313/scipy/special/tests/data/boost.npz`

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
