# 17 个目录逐项清单与迁移风险

所有新路径均为拟议，均未执行迁移；每项目标无冲突。用途来自原目录报告与源码。占用以逻辑 MiB 报告；分配量、完整文件 SHA、保护记录另见机器附件。

## hands_c01_anatomy_preparation_audit_r1

原路径：`<HANDS_ROOT>_c01_anatomy_preparation_audit_r1`

拟议路径：`<HANDS_ROOT>\hands_c01_anatomy_preparation_audit_r1`

用途：C01 手型/解剖及 E5 准备审计，B2 静态起点与参考族来源。

占用：84 文件 / 2 目录（含根），11,651,876 bytes，11.112 MiB；分配量 11,814,592 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 84 条/84 条 SHA 一致；引用该目录的保护记录文件 19 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\design_constraints.py:4`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\diagnose_preparation.py:10`，`O.parent/'hands/audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\piano_hand_static_posture_clearance_refinement_r2\SOLVED_STATIC_POSES_R2.json`；应为 `<HANDS_ROOT>\audits\piano_hand_static_posture_clearance_refinement_r2\SOLVED_STATIC_POSES_R2.json`。

- `<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_c01_g4_e5_natural_motion_bridge_r2\solve_endpoint_attempt1.py:9`：`P=json.loads((O/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'));PRE=O.parent/'hands_c01_anatomy_preparation_audit_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_g4_e5_natural_motion_bridge_r2\solve_endpoint.py:9`：`P=json.loads((O/'POLICY_LOCK.json').read_text(encoding='utf-8-sig'));PRE=O.parent/'hands_c01_anatomy_preparation_audit_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_g4_e5_natural_motion_bridge_r2\motion_model.py:8`：`PRE=O.parent/'hands_c01_anatomy_preparation_audit_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\FINAL_RECOMMENDATION.md`。


## hands_c01_g4_e5_natural_motion_bridge_r2

原路径：`<HANDS_ROOT>_c01_g4_e5_natural_motion_bridge_r2`

拟议路径：`<HANDS_ROOT>\hands_c01_g4_e5_natural_motion_bridge_r2`

用途：G4→E5 自然参考族端点和连续候选失败现场。

占用：89 文件 / 2 目录（含根），27,324,414 bytes，26.059 MiB；分配量 27,494,808 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 89 条/89 条 SHA 一致；引用该目录的保护记录文件 17 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_c01_g4_e5_natural_motion_bridge_r2\bake_and_validate.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_c01_g4_e5_natural_motion_bridge_r2\bake_and_validate_initial.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_c01_g4_e5_natural_motion_bridge_r2\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\verify_local_path.py:18`：`tree = ast.parse((O.parent / 'hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate.py').read_text(encoding='utf-8-sig'))`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_contact_junction_compatibility_r1\verify_local_path.py:18`：`tree = ast.parse((O.parent / 'hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate.py').read_text(encoding='utf-8-sig'))`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_contact_junction_compatibility_r1\blender_verify.py:12`：`tree=ast.parse((O.parent/'hands_c01_g4_e5_natural_motion_bridge_r2/bake_and_validate.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='strict'],type_ignores=[]),'strict','exec'))`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_c01_g4_e5_natural_motion_bridge_r2\FINAL_RECOMMENDATION.md`。


## hands_c01_g4_e5_skin_safe_bridge_r1

原路径：`<HANDS_ROOT>_c01_g4_e5_skin_safe_bridge_r1`

拟议路径：`<HANDS_ROOT>\hands_c01_g4_e5_skin_safe_bridge_r1`

用途：G4→E5 面级皮肤安全静态修复与诊断场景。

占用：49 文件 / 2 目录（含根），13,797,687 bytes，13.158 MiB；分配量 13,887,120 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 49 条/49 条 SHA 一致；引用该目录的保护记录文件 25 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_c01_g4_e5_skin_safe_bridge_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_c01_g4_e5_skin_safe_bridge_r1\prepare.py:3`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_c01_g4_e5_skin_safe_bridge_r1\skin_proxy.py:5`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\write_reports.py:6`：`OLD=O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\verify_actual.py:14`：`expected=json.loads((O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1/ENTRY_CONTEXT_READONLY.json').read_text())['original_key_action_hashes']`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\supplement_measurements.py:25`：`old=O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1';reg=json.loads((old/'MINIMAL_PREFLIGHT_REGRESSION.json').read_text());static=O.parent/'hands_skin_collision_static_feasibility_r1';V=np.load(static/'S2_ATTEMPT_1_ACTUAL_SKIN.npz')['vertices'];upper=reg['S2_previous_sampled_mm']/1000+1e-10`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_c01_g4_e5_skin_safe_bridge_r1\FINAL_RECOMMENDATION.md`。


## hands_c01_s1_constrained_solver_feasibility_r1

原路径：`<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1`

拟议路径：`<HANDS_ROOT>\hands_c01_s1_constrained_solver_feasibility_r1`

用途：S1 显式约束求解器可行性、合格静态点及失败尝试。

占用：52 文件 / 2 目录（含根），12,409,703 bytes，11.835 MiB；分配量 12,518,240 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 52 条/52 条 SHA 一致；引用该目录的保护记录文件 23 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\skin_proxy.py:5`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\extract_anatomy.py:8`：`I=u.I;PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\diagnose_preparation.py:8`：`PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1';info=json.loads((PRE/'ACTUAL_VALIDATION_2.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(PRE/'S1_CONSTRAINED_DIAGNOSTIC_R1.blend'),load_ui=False,use_scripts=False)`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\write_reports.py:4`：`O=Path(__file__).resolve().parent;PRE=O.parent/'hands_c01_s1_constrained_solver_feasibility_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\FINAL_RECOMMENDATION.md`。


## hands_c01_whole_hand_motion_feasibility_r1

原路径：`<HANDS_ROOT>_c01_whole_hand_motion_feasibility_r1`

拟议路径：`<HANDS_ROOT>\hands_c01_whole_hand_motion_feasibility_r1`

用途：C01 全手运动实验、原生候选场景、blender_utils 共用依赖。

占用：58 文件 / 3 目录（含根），13,116,646 bytes，12.509 MiB；分配量 13,239,080 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 58 条/58 条 SHA 一致；引用该目录的保护记录文件 43 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_c01_whole_hand_motion_feasibility_r1\blender_preflight.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_c01_whole_hand_motion_feasibility_r1\blender_utils.py:7`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_c01_whole_hand_motion_feasibility_r1\motion_core.py:5`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_c01_g4_e5_skin_safe_bridge_r1\verify_s1_actual.py:5`：`O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'));from geometry_detector import *;import blender_utils as u`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\extract_anatomy.py:6`：`O=Path(__file__).resolve().parent;ROOT=O.parent/'hands';sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\write_reports.py:29`：`piano_performance_poc_r1/performance_core.py'),str(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'),str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1/blender_utils.py')],note='No external IK installed. Frozen geometry/proxy/distance code and data copied into this isolated directory; existing numerical dependencies reused read-only.')`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_c01_whole_hand_motion_feasibility_r1\FINAL_RECOMMENDATION.md`。


## hands_cleanup_audit_r1

原路径：`<HANDS_ROOT>_cleanup_audit_r1`

拟议路径：`<HANDS_ROOT>\hands_cleanup_audit_r1`

用途：已执行的 Hands 历史清理审计、锁定 Manifest、批准与删除账本。

占用：34 文件 / 1 目录（含根），135,526,542 bytes，129.248 MiB；分配量 135,598,856 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：历史审计复核，锁定账本与批准缺失例外。

保护关系：最新 R2 输入保护表 34 条/34 条 SHA 一致；引用该目录的保护记录文件 9 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_cleanup_audit_r1\execution_r1.py:6`，`r'<HANDS_ROOT>_cleanup_audit_r1'`。迁入后实际仍指向 `<HANDS_ROOT>_cleanup_audit_r1`；应为 `<HANDS_ROOT>\hands_cleanup_audit_r1`。


用途来源：`<HANDS_ROOT>_cleanup_audit_r1\FINAL_CLEANUP_REPORT.md`。


## hands_contact_constrained_trajectory_planning_r1

原路径：`<HANDS_ROOT>_contact_constrained_trajectory_planning_r1`

拟议路径：`<HANDS_ROOT>\hands_contact_constrained_trajectory_planning_r1`

用途：接触约束轨迹规划、CasADi 依赖及冻结符号皮肤函数。

占用：2,540 文件 / 287 目录（含根），220,315,554 bytes，210.109 MiB；分配量 225,439,232 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 2540 条/2540 条 SHA 一致；引用该目录的保护记录文件 11 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\skin_proxy.py:5`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1\reproduction\_derivative_r1_run.py:4`：`O=Path(__file__).resolve().parent;P=O.parent/'hands_contact_constrained_trajectory_planning_r1';sys.path.insert(0,str(O));sys.path.insert(0,str(P/'deps'))`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1\reproduction\_derivative_r1_reports.py:3`：`O=Path(r'<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1');P=O.parent/'hands_contact_constrained_trajectory_planning_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1\reproduction\_derivative_r1_prepare.py:4`：`P=O.parent/'hands_contact_constrained_trajectory_planning_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\FINAL_RECOMMENDATION.md`。


## hands_contact_derivative_feasibility_recovery_r1

原路径：`<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1`

拟议路径：`<HANDS_ROOT>\hands_contact_derivative_feasibility_recovery_r1`

用途：接触导数、分支和局部可行性恢复审计及复现依赖。

占用：106 文件 / 4 目录（含根），323,872,669 bytes，308.869 MiB；分配量 324,063,032 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 106 条/106 条 SHA 一致；引用该目录的保护记录文件 12 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1\reproduction\_derivative_r1_direct_prepare.py:2`，`r'<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1'`。迁入后实际仍指向 `<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1`；应为 `<HANDS_ROOT>\hands_contact_derivative_feasibility_recovery_r1`。

- 外部源码 `<HANDS_ROOT>_time_coupled_contact_recovery_r1\prepare_protection.py:3`：`O=Path(__file__).resolve().parent;P=O.parent/'hands_contact_derivative_feasibility_recovery_r1';t=time.monotonic()`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_time_coupled_contact_recovery_r1\audit_timeline.py:5`：`P=O.parent/'hands_contact_derivative_feasibility_recovery_r1';H=O.parent/'hands_contact_constrained_trajectory_planning_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1\FINAL_RECOMMENDATION.md`。


## hands_contact_junction_compatibility_r1

原路径：`<HANDS_ROOT>_contact_junction_compatibility_r1`

拟议路径：`<HANDS_ROOT>\hands_contact_junction_compatibility_r1`

用途：换音边界接触兼容性与共同构型证据。

占用：128 文件 / 3 目录（含根），10,734,939 bytes，10.238 MiB；分配量 10,989,776 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 128 条/128 条 SHA 一致；引用该目录的保护记录文件 12 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_contact_junction_compatibility_r1\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_contact_junction_compatibility_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_contact_junction_compatibility_r1\skin_proxy.py:5`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\symbolic_skin.py:24`：` t=time.perf_counter();f,R=symbolic_model();prev=O.parent/'hands_contact_junction_compatibility_r1';rows=[]`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\summarize_execution.py:13`：`s=read('LOCAL_PATH_ACTUAL_SAMPLES.json');a=[r for r in s if r['id']!='junction_left_limit'];old=O.parent/'hands_contact_junction_compatibility_r1';oldrows=json.loads((old/'LOCAL_PATH_ACTUAL_SAMPLES.json').read_text());match=[min(a,key=lambda r:abs(r['display_time']-o['display_time'])) for o in oldrows];assert all(abs(x['display_time']-y['display_time'])<1e-9 for x,y in zip(oldrows,match));r=r`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\benchmark.py:4`：`O=Path(__file__).resolve().parent;P=O.parent/'hands_contact_junction_compatibility_r1';PRE=O.parent/'hands_contact_state_motion_planner_comparison_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_contact_junction_compatibility_r1\FINAL_RECOMMENDATION.md`。


## hands_contact_state_motion_planner_comparison_r1

原路径：`<HANDS_ROOT>_contact_state_motion_planner_comparison_r1`

拟议路径：`<HANDS_ROOT>\hands_contact_state_motion_planner_comparison_r1`

用途：接触状态/离散规划器比较、原琴键 Action 与 MIDI 基准。

占用：6,137 文件 / 591 目录（含根），233,570,264 bytes，222.750 MiB；分配量 245,108,840 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 6137 条/6137 条 SHA 一致；引用该目录的保护记录文件 13 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_contact_state_motion_planner_comparison_r1\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_contact_state_motion_planner_comparison_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_contact_state_motion_planner_comparison_r1\skin_proxy.py:5`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_contact_constrained_trajectory_planning_r1\verify_local_path.py:15`：`PRE = O.parent / 'hands_contact_state_motion_planner_comparison_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_contact_junction_compatibility_r1\verify_local_path.py:15`：`PRE = O.parent / 'hands_contact_state_motion_planner_comparison_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_contact_junction_compatibility_r1\blender_verify.py:10`：`RAW=D;P=json.loads((O/'POLICY_LOCK.json').read_text());I=json.loads((O/'EXPERIMENT_INPUT.json').read_text());PRE=O.parent/'hands_contact_state_motion_planner_comparison_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_contact_state_motion_planner_comparison_r1\FINAL_RECOMMENDATION.md`。


## hands_early_hand_preparation_entry_reachability_r1

原路径：`<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1`

拟议路径：`<HANDS_ROOT>\hands_early_hand_preparation_entry_reachability_r1`

用途：早期准备及完整入口可达性 R1，250ms 采样前缀与失败轨迹。

占用：283 文件 / 3 目录（含根），68,045,491 bytes，64.893 MiB；分配量 68,610,368 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 283 条/283 条 SHA 一致；引用该目录的保护记录文件 6 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1\record_protection_scope.py:8`，`O.parent/'piano/piano_project_storage_cleanup_audit_r1'`。迁入后实际仍指向 `<HANDS_ROOT>\piano\piano_project_storage_cleanup_audit_r1`；应为 `D:\codex one\3D interactive components\piano\piano_project_storage_cleanup_audit_r1`。

- 外部源码 `<HANDS_ROOT>_long_context_hand_motion_architecture_r1\write_architecture_reports.py:8`：`old=O.parent/'hands_early_hand_preparation_entry_reachability_r1';oldfacts=json.loads((old/'FINAL_FACTS.json').read_text(encoding='utf8'));ep=oldfacts['entry_prefix'];plane=above['projected_whole_digit_clearance']['minimum_surface_above_entity_mm'];remaining=above['event_recovery_bound']['remaining_to_next_event_`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_long_context_hand_motion_architecture_r1\prepare_architecture_experiment.py:4`：`O=Path(__file__).resolve().parent;BASE=O.parent;P=BASE/'hands_early_hand_preparation_entry_reachability_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_long_context_hand_motion_architecture_r1\intent_rig_adapter.py:36`：`('HIGH_LEVEL_CLEARANCE_REQUESTS.json');raw=read('HIGH_LEVEL_INTENT_INSTANCES.json');baseline=read('BASELINE_FAILURE_READONLY_CHECK.json');P=O.parent/'hands_early_hand_preparation_entry_reachability_r1';old=next(r for r in json.loads((P/'ENTRY_ACTUAL_SAMPLES.json').read_text(encoding='utf8')) if r['id']==baseline['worst_failure']['id']);replay=[]`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1\FINAL_RECOMMENDATION.md`。


## hands_fingering_inference_poc_r1

原路径：`<HANDS_ROOT>_fingering_inference_poc_r1`

拟议路径：`<HANDS_ROOT>\hands_fingering_inference_poc_r1`

用途：Lumikey 指法推理、ONNX/运行依赖、原输入绑定。

占用：785 文件 / 298 目录（含根），368,004,388 bytes，350.956 MiB；分配量 369,292,176 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 785 条/785 条 SHA 一致；引用该目录的保护记录文件 11 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- 外部源码 `<HANDS_ROOT>_sequence_fingering_planning_r1\verify_inputs.py:4`：`O=Path(__file__).resolve().parent;OLD=O.parent/'hands_fingering_inference_poc_r1';ROOT=O.parent/'hands'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_sequence_fingering_planning_r1\score_paths.mjs:8`：`const old=path.join(here,'..','hands_fingering_inference_poc_r1');`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_sequence_fingering_planning_r1\run_pianoplayer.py:4`：`O=Path(__file__).resolve().parent;OLD=O.parent/'hands_fingering_inference_poc_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_fingering_inference_poc_r1\FINAL_RECOMMENDATION.md`。


## hands_long_context_corridor_ik_bridge_r2

原路径：`<HANDS_ROOT>_long_context_corridor_ik_bridge_r2`

拟议路径：`<HANDS_ROOT>\hands_long_context_corridor_ik_bridge_r2`

用途：高层走廊→IK R2 的 PARTIAL 结果、导数阻碍与失败曲线。

占用：207 文件 / 4 目录（含根），59,560,325 bytes，56.801 MiB；分配量 59,983,344 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：R2 当前交付及拟议 R3 输入；未发现外部源码直接引用，但本目录父层级依赖已失效预测。

保护关系：最新 R2 输入保护表 0 条/0 条 SHA 一致；引用该目录的保护记录文件 0 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_long_context_corridor_ik_bridge_r2\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_long_context_corridor_ik_bridge_r2\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_long_context_corridor_ik_bridge_r2\record_r2_protection_scope.py:5`，`O.parent/'piano/local_gb_01_execution_safety_patch_r1'`。迁入后实际仍指向 `<HANDS_ROOT>\piano\local_gb_01_execution_safety_patch_r1`；应为 `D:\codex one\3D interactive components\piano\local_gb_01_execution_safety_patch_r1`。


用途来源：`<HANDS_ROOT>_long_context_corridor_ik_bridge_r2\R2_FINAL_RECOMMENDATION.md`。


## hands_long_context_hand_motion_architecture_r1

原路径：`<HANDS_ROOT>_long_context_hand_motion_architecture_r1`

拟议路径：`<HANDS_ROOT>\hands_long_context_hand_motion_architecture_r1`

用途：长上下文架构 A、HandMotionIntent、静态清障与先验来源审计。

占用：106 文件 / 4 目录（含根），42,067,715 bytes，40.119 MiB；分配量 42,281,520 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 106 条/106 条 SHA 一致；引用该目录的保护记录文件 3 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_long_context_hand_motion_architecture_r1\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_long_context_hand_motion_architecture_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_long_context_hand_motion_architecture_r1\skin_proxy.py:5`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_long_context_corridor_ik_bridge_r2\prepare_r2.py:3`：`sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;BASE=O.parent;P=BASE/'hands_long_context_hand_motion_architecture_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_long_context_corridor_ik_bridge_r2\preflight_r2.py:6`：`P=O.parent/'hands_early_hand_preparation_entry_reachability_r1';A=O.parent/'hands_long_context_hand_motion_architecture_r1'`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_long_context_corridor_ik_bridge_r2\corridor_planner.py:23`：` A=O.parent/'hands_long_context_hand_motion_architecture_r1';failure=json.loads((A/'BASELINE_FAILURE_READONLY_CHECK.json').read_text(encoding='utf8'));ob=failure['obstacle']`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_long_context_hand_motion_architecture_r1\FINAL_RECOMMENDATION.md`。


## hands_sequence_fingering_planning_r1

原路径：`<HANDS_ROOT>_sequence_fingering_planning_r1`

拟议路径：`<HANDS_ROOT>\hands_sequence_fingering_planning_r1`

用途：PianoPlayer 序列规划、C01 指法候选及源事件身份绑定。

占用：121 文件 / 12 目录（含根），15,604,450 bytes，14.882 MiB；分配量 15,779,904 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 121 条/121 条 SHA 一致；引用该目录的保护记录文件 40 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_sequence_fingering_planning_r1\verify_inputs.py:4`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_c01_whole_hand_motion_feasibility_r1\prepare_inputs.py:7`：`CAND=O.parent/'hands_sequence_fingering_planning_r1/SEQUENCE_CANDIDATES.json';cs=read(CAND);cand=next(x for x in cs['candidates'] if x['candidate_id']=='C01_PIANOPLAYER')`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_long_context_corridor_ik_bridge_r2\verify_midi.py:6`：`B=json.loads((O.parent/'hands_sequence_fingering_planning_r1/SOURCE_EVENT_BINDINGS.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(B['source_midi'])==B['source_midi_sha256'];assert sha(B['source_timeline'])==B['source_timeline_sha256']`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1\verify_midi.py:6`：`B=json.loads((O.parent/'hands_sequence_fingering_planning_r1/SOURCE_EVENT_BINDINGS.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(B['source_midi'])==B['source_midi_sha256'];assert sha(B['source_timeline'])==B['source_timeline_sha256']`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_sequence_fingering_planning_r1\FINAL_RECOMMENDATION.md`。


## hands_skin_collision_static_feasibility_r1

原路径：`<HANDS_ROOT>_skin_collision_static_feasibility_r1`

拟议路径：`<HANDS_ROOT>\hands_skin_collision_static_feasibility_r1`

用途：真实完整皮肤/键体检测及静态可行性原始模型和几何实现。

占用：74 文件 / 3 目录（含根），18,603,542 bytes，17.742 MiB；分配量 18,766,328 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 74 条/74 条 SHA 一致；引用该目录的保护记录文件 28 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_skin_collision_static_feasibility_r1\complete_results.py:4`，`O.parent/'hands/audits/piano_hand_static_posture_clearance_refinement_r2/SOLVED_STATIC_POSES_R2.json'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\piano_hand_static_posture_clearance_refinement_r2\SOLVED_STATIC_POSES_R2.json`；应为 `<HANDS_ROOT>\audits\piano_hand_static_posture_clearance_refinement_r2\SOLVED_STATIC_POSES_R2.json`。

- `<HANDS_ROOT>_skin_collision_static_feasibility_r1\extract_actual_model.py:7`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_skin_collision_static_feasibility_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- 外部源码 `<HANDS_ROOT>_c01_anatomy_preparation_audit_r1\extract_anatomy.py:73`：`static=O.parent/'hands_skin_collision_static_feasibility_r1';F=json.loads((static/'STATIC_POSE_FEASIBILITY.json').read_text());test=F['tests'][1];info=next(a for a in test['attempts'] if a['scene']==test['selected_scene'])`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\supplement_measurements.py:25`：`old=O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1';reg=json.loads((old/'MINIMAL_PREFLIGHT_REGRESSION.json').read_text());static=O.parent/'hands_skin_collision_static_feasibility_r1';V=np.load(static/'S2_ATTEMPT_1_ACTUAL_SKIN.npz')['vertices'];upper=reg['S2_previous_sampled_mm']/1000+1e-10`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_c01_s1_constrained_solver_feasibility_r1\solve_s1_attempt1.py:15`：`tree=ast.parse((O.parent/'hands_skin_collision_static_feasibility_r1/solve_static_skin.py').read_text(encoding='utf-8-sig'))`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_skin_collision_static_feasibility_r1\FINAL_RECOMMENDATION.md`。


## hands_time_coupled_contact_recovery_r1

原路径：`<HANDS_ROOT>_time_coupled_contact_recovery_r1`

拟议路径：`<HANDS_ROOT>\hands_time_coupled_contact_recovery_r1`

用途：时间耦合接触恢复，2.083ms 局部诊断证据及外部入口限制。

占用：103 文件 / 3 目录（含根），11,004,962 bytes，10.495 MiB；分配量 11,196,360 bytes。无 reparse、无检测到硬链接、目标无冲突。

使用状态：未观察到本目录相关运行进程；当前唯一 active Hands 聊天为本纠偏任务。保留作用：后续技术输入/历史复现源码引用仍存在。

保护关系：最新 R2 输入保护表 103 条/103 条 SHA 一致；引用该目录的保护记录文件 10 个。当前目录全部文件本轮 before/after SHA 一致。

决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。

具体阻碍：

- 现有源码包含整体迁入后仍失效的父目录假设或绝对路径；不修改原源码无法证明复核可用

- 存在外部源码的历史复现/后续输入引用；调用方路径与保护绑定尚未迁移闭合

- 历史 R2 全目录保护表按原绝对路径保存；不能覆写旧表或把迁移缺失升级为源内容变化/重置历史 FAIL


路径证据（完整行号索引在 JSON，以下为代表）：

- `<HANDS_ROOT>_time_coupled_contact_recovery_r1\extract_anatomy.py:6`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- `<HANDS_ROOT>_time_coupled_contact_recovery_r1\geometry_detector.py:8`，`O.parent/'hands/audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py'`。迁入后实际仍指向 `<HANDS_ROOT>\hands\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`；应为 `<HANDS_ROOT>\audits\minuet_stage_c_r6_whole_phrase_spatial_planning\whole_phrase_model.py`。

- `<HANDS_ROOT>_time_coupled_contact_recovery_r1\skin_proxy.py:5`，`O.parent/'hands'`。迁入后实际仍指向 `<HANDS_ROOT>\hands`；应为 `<HANDS_ROOT>`。

- 外部源码 `<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1\write_deliverables.py:11`：`]['path'],source_scene_sha256=before[policy['source_action_scene']['path']],frozen_right_native_sha256=native,source_skin_sha256=before[str(O.parent/'hands_time_coupled_contact_recovery_r1/SKIN_MODEL.npz')],source_key_table_sha256=before[str(O.parent/'hands_time_coupled_contact_recovery_r1/SKIN_MODEL_META.json')],MIDI_reparsed=True,Action_reevaluated=True,all_original_Action_payloads_match=f['original_actions_all'],all_native_mesh_rig`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1\record_protection_scope.py:5`：`c=read(O/'PROTECTION_CHECK.json');b=read(O/'PROTECTED_FILES_BEFORE.json');a=read(O/'PROTECTED_FILES_AFTER.json');old=read(O.parent/'hands_time_coupled_contact_recovery_r1/PROTECTED_FILES_BEFORE.json')`。这是保留路径的复核/输入线索，不宣称当前正在运行。

- 外部源码 `<HANDS_ROOT>_early_hand_preparation_entry_reachability_r1\preflight.py:9`：`L=json.loads((O.parent/'hands_time_coupled_contact_recovery_r1/CORRECTION_SOLVE_RESULTS.json').read_text(encoding='utf8'))['nodes'][0]`。这是保留路径的复核/输入线索，不宣称当前正在运行。


用途来源：`<HANDS_ROOT>_time_coupled_contact_recovery_r1\FINAL_RECOMMENDATION.md`。

