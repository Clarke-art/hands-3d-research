# 17目录后续分批迁移建议

**计划而非迁移授权；实际0/17。** 复用R1文件数/容量/引用统计，没有重新完整盘点。唯一新增测试副本是R2，其他16项没有影子执行证据。新任务/外部打开句柄与native资源状态必须在各批前重新检查。

第一批形成 **1项条件候选：hands_long_context_corridor_ik_bridge_r2**。条件是Human接受“历史字节保持＋独立只读复核入口”这一迁移验收边界，并审查PARTIAL范围；若要求全部原命令和完整Blender/求解原样复现，当前合格名单为 **0项**。此候选尚未获真实迁移批准。

|批次|目录|R1文件数|逻辑MiB|外部源码引用文件数|风险|资格|
|---|---|---:|---:|---:|---|---|
|B1_PILOT|hands_long_context_corridor_ik_bridge_r2|207|56.801|0|MEDIUM_PATH_CONTRACT|R2只读条件候选|
|B2_RECENT_LEAF|hands_long_context_hand_motion_architecture_r1|106|40.119|3|MEDIUM_PATH_CONTRACT|尚未试点|
|B2_RECENT_LEAF|hands_time_coupled_contact_recovery_r1|103|10.495|3|MEDIUM_PATH_CONTRACT|尚未试点|
|B2_RECENT_LEAF|hands_early_hand_preparation_entry_reachability_r1|283|64.893|8|MEDIUM_PATH_CONTRACT|尚未试点|
|B3_FINGERING_AND_GEOMETRY_CLUSTER|hands_sequence_fingering_planning_r1|121|14.882|5|MEDIUM_PATH_CONTRACT|尚未试点|
|B3_FINGERING_AND_GEOMETRY_CLUSTER|hands_c01_g4_e5_skin_safe_bridge_r1|49|13.158|9|MEDIUM_PATH_CONTRACT|尚未试点|
|B3_FINGERING_AND_GEOMETRY_CLUSTER|hands_c01_s1_constrained_solver_feasibility_r1|52|11.835|17|MEDIUM_PATH_CONTRACT|尚未试点|
|B3_FINGERING_AND_GEOMETRY_CLUSTER|hands_c01_anatomy_preparation_audit_r1|84|11.112|17|MEDIUM_PATH_CONTRACT|尚未试点|
|B3_FINGERING_AND_GEOMETRY_CLUSTER|hands_contact_junction_compatibility_r1|128|10.238|15|MEDIUM_PATH_CONTRACT|尚未试点|
|B3_FINGERING_AND_GEOMETRY_CLUSTER|hands_c01_g4_e5_natural_motion_bridge_r2|89|26.059|17|MEDIUM_PATH_CONTRACT|尚未试点|
|B3_FINGERING_AND_GEOMETRY_CLUSTER|hands_skin_collision_static_feasibility_r1|74|17.742|32|HIGH_DEPENDENCY_HUB|尚未试点|
|B3_FINGERING_AND_GEOMETRY_CLUSTER|hands_c01_whole_hand_motion_feasibility_r1|58|12.509|51|HIGH_DEPENDENCY_HUB|尚未试点|
|B4_PACKAGES_AND_RECOVERY|hands_contact_derivative_feasibility_recovery_r1|106|308.869|2|HIGH_NATIVE_OR_PACKAGE|尚未试点|
|B4_PACKAGES_AND_RECOVERY|hands_contact_constrained_trajectory_planning_r1|2540|210.109|12|HIGH_NATIVE_OR_PACKAGE|尚未试点|
|B4_PACKAGES_AND_RECOVERY|hands_contact_state_motion_planner_comparison_r1|6137|222.750|16|HIGH_NATIVE_OR_PACKAGE|尚未试点|
|B4_PACKAGES_AND_RECOVERY|hands_fingering_inference_poc_r1|785|350.956|3|HIGH_NATIVE_OR_PACKAGE|尚未试点|
|B5_CLEANUP_HISTORY|hands_cleanup_audit_r1|34|129.248|0|HIGH_DELETION_LEDGER|尚未试点|

每个源→目标的完整绝对路径及单项目门禁保存在MIGRATION_BATCH_PLAN.json；目标均为hands内部同名目录，不允许root兼容链接或覆盖。B2先从引用较少的近期证据目录增加只读白名单，保持时间耦合局部资格和历史FAIL。B3含C01源指法及共享几何/原生hub，必须同时检查调用方，不能只因文件少就盲搬。B4包含软件包、serialized函数、ONNX及大型恢复记录，需证明包内相对资源/DLL/ABI/来源链，而不运行模型或优化。批次只是优先顺序，可以因未闭合门禁暂缓，不为减少root目录强制跨批移动。

**cleanup为独立高风险项。** 原34文件的锁定Manifest和批准/SUCCESS账本必须保留，原脚本硬编码旧O。先新增只读复核入口，逐项核对锁定Manifest SHA、账本与原库存的关联、已批准精确缺失例外；不运行任何prepare/execute/verify历史程序阶段，不修改账本或旧保护表。本轮只提出这个门禁，尚未测试该入口，因此不列第一批。

各批真实执行前：原源文件稳定基线与写者检查、目标不存在且解析边界合法、所有被读源和调用方的登记路径与原SHA闭合、未知native/dynamic项显式保留、Human批准精确路径范围。批准后才允许使用Windows单一shell/精确LiteralPath移动，迁前后成员/SHA/必要引用检查和路径事件分开记账；失败停止，不删缓存、不清理副本、不抹历史FAIL，不把同盘移动计作磁盘释放。

已证明的机制可以复用于登记读取，**不能依据一项R2影子证明其他16目录安全迁移**。没有发现可据本轮证据永久判为“绝对无法迁移”的目录，但原命令直接兼容未成立，高风险项与源码/执行行为变更需Human另行授权。
