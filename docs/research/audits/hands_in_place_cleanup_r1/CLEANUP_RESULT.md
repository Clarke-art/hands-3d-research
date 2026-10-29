# Hands 原地瘦身结果

2026-10-14。**HANDS_IN_PLACE_CLEANUP_R1 — STOP — HUMAN REVIEW。**

|项目|结果|
|---|---:|
|清理前原有内容|11.985924 GiB（12,869,787,435 bytes）|
|实际删除文件|126|
|删除逻辑大小|0.278880 GiB|
|**实际删除释放的文件分配空间**|**0.279202 GiB（299,790,728 bytes）**|
|清理后原有内容|11.707043 GiB（12,570,342,206 bytes）|
|删除阶段D盘可用空间实测差|+0.279125 GiB|
|未执行/删除拒绝|0|

释放量按每个删除文件的 Windows FileStandardInfo.AllocationSize 实测累计：全部为单硬链接、无reparse，独占句柄核对fileID/size/SHA后精确删除，关闭句柄确认路径消失。逻辑大小、文件分配量和D盘总可用空间差独立报告；总可用空间受其他进程影响，不能全部归因本轮。没有同盘迁移、压缩或把副本体积算作释放量。清理前后原有内容总量不含本轮极小审计输出，审计占用在最终实测中另列。

实际清理：{'PYTHON_REGENERABLE_CACHE': 11, 'NPM_DOWNLOAD_CACHE': 102, 'NON_HOST_NATIVE_BUILD': 13}。11个Python缓存均保留对应.py源码；npm _cacache不承担运行/历史复核作用，最大下载缓存的44/44内容与完整已安装包逐SHA相同，保留npm日志、源码、license和package-lock。宿主Node已核实win32/x64，binding.js仅加载process.platform/process.arch目录，删除darwin、linux和win32/arm64的非本机打包原生产物；Windows x64五个原生运行文件原SHA保留。未来换OS/CPU需重新安装供应方包；未删除模型、指法或R3数学/几何数据。

删除前明细 `DELETE_PLAN.csv`，实际逐项句柄删除结果 `DELETE_EXECUTION.csv`。没有运行任何历史删除程序。所有原目录保持，包括空缓存/非本机目录；17个手动迁入目录没有再次移动。

保护：10,813项原生/科学数据、原始源码、冻结合同、Human授权及历史账本在删除前后聚合SHA一致；六项已批准Rig/动画/姿态资产与批准SHA一致；所有剩余文件的size/mtime/identity不变，成员缺失严格等于删除明细。旧Manifest和历史保护FAIL内容未改写，不以本次删除重置全局资格。保护机器结果见 `PROTECTION_CHECK.json`。

## 保留的大体积内容

|目录|逻辑GiB|
|---|---:|
|production_spec\stage5_production_rig|1.223|
|audits\minuet_stage_c_lightweight_animation_poc_r1|1.195|
|audits\piano_pedagogical_motion_refinement_r1|1.194|
|production_spec\stage6_deformation|0.788|
|audits\first_web_real_motion_deformation_fix_r1|0.541|
|audits\right_hand_lbs_vs_dqs_real_motion_ab_r1|0.445|
|audits\pianovam_single_sample_right_hand_retarget_r1|0.425|
|audits\official_l1_product_rebase_feasibility_r1|0.315|

最大文件：

- `hands_contact_derivative_feasibility_recovery_r1\PRUNED_J.casadi`：140.30 MiB
- `hands_contact_derivative_feasibility_recovery_r1\ORIGINAL_G.casadi`：133.42 MiB
- `audits\minuet_stage_c_r2_local_finger_overlap_refinement\BASELINE_REFERENCE.npz`：93.24 MiB
- `production_spec\stage5_production_rig\joint_surface_rest_zero_bind_revalidation_after_palmar_donor_restoration_r1\CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json`：72.29 MiB
- `production_spec\stage5_production_rig\joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1\CLEAN_REOPEN_NATIVE_PAYLOADS_R1.json`：72.28 MiB
- `audits\dual_hand_synchronized_real_motion_validation_r1\evaluated_dual_motion.npz`：66.75 MiB
- `production_spec\stage5_production_rig\geometry_propagation_after_palmar_donor_restoration_r1\PALMAR_STAGE5_BEFORE_SAVE_PAYLOADS_R1.json`：63.91 MiB
- `production_spec\stage5_production_rig\geometry_propagation_after_donor_transfer_r1\STAGE5_BEFORE_SAVE_PROPAGATION_PAYLOADS_R1.json`：63.89 MiB

7.02 GiB左右PNG中包括仍被教学页面使用的逐帧资源及Human/失败复核截图，未删除；大型NPZ、CasADi函数与冻结原生payload承担轨迹/算法/失败复核，未知用途不继续深挖。许可证源ZIP保留原来源；3.06MiB的.blend1与现有.blend字节/大小不同，非已证冗余，保留。影子R2的207文件虽有权威原副本，但仍被独立复核入口和登记表直接引用，承担该轮实际执行证据，保留。未为腾空间改路径、改源码或清退历史证据。

手动迁移造成的明显问题仅登记：部分旧绝对路径仍指向上级hands_*；`O.parent/'hands'`在已迁入位置会指向hands\hands。没有开展兼容研发或修改冻结源码，历史迁移与本轮删除分别记账。

**piano完全未参与本轮操作：未列举、扫描、读取、修改、删除或移动其文件。** 所有文件扫描/删除目标均在hands，遇reparse立即拒绝；卷空间查询仅以hands路径进行。没有创建备份或新影子，没有启动Blender、优化、动画、R3或其他研发。


## 最终容量实测

清理后hands含本轮审计输出约 **11.707195 GiB**；本轮审计约158.9 KiB，共30,914文件。精确原内容前后差严格等于299,445,229 bytes删除逻辑量；报告/明细占用已单独计入，未建立备份或新影子。
