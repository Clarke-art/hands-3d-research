# 影子验证结果

**总体 PARTIAL。只读核心链PASS；未授予完整原脚本/Blender/求解复现PASS。**

最终readonly_04/05各23项检查、251资源实际读取、0历史程序执行，结果指纹均为 `cd8ec8bf2d4ba15f21ed6afdbc93a1b9d286260fd1180206a839322a9b455ed8`。实际运行日志与逐文件读取凭据在READONLY_04.log、READONLY_05.log和runs对应OPERATIONS.json；所有结果文件均可重复核对。

|验收项|结果|实际证据与边界|
|---|---|---|
|影子副本完整性|PASS|207文件、目录成员与源相同，复制和结束SHA全部相同|
|内部路径解析|PASS_VIA_INDEPENDENT_ADAPTER|真实登记文件读取、formal→shadow、明确hands root；未修改 pathlib/源码；原表达式原样仍错误|
|外部输入|PASS_SCOPED_44_FILES / TRANSITIVE_RUNTIME_PARTIAL|正式MIDI、Rig/场景5容器、13 Action记录、历史输入和既有资源逐SHA实读；无原生执行|
|历史保护引用|PASS_PRESERVED_SEMANTICS|旧86259表前后字节/语义一致，历史FAIL与PASS保留；未写新旧globalPASS|
|旧源码完整性|PASS|原207和影子207全SHA一致，原源码没有修改/导入/执行|
|正式Hands/Piano资产|PASS_NO_TASK_WRITES_SCOPED_HASH|44读取输入SHA不变，所有写操作在本审计；不声称并发Piano全目录无变化|
|原始R2目录|PASS_UNMOVED|源成员、SHA、size/mtime/identity一致，formal目标不存在|
|复核适配入口可重复|PASS|最终readonly_04/05各23检查/251实读，语义指纹相同|
|动态与原生依赖|PARTIAL_UNVERIFIED_EXPLICIT|U01–U07全部登记，不冒用完整Blender/求解复现PASS|

已真实执行：原MIDI字节解析及PPQ/tempo/23音46事件逐记录一致；原timeline绑定与C01指法身份；5个源资源SHA和容器前缀；完整皮肤NPZ的CRC/数字头以及88键几何JSON来源一致；13个已记录琴键Action哈希/FCurve记录一致；103个实际皮肤证据CRC与形状；103条历史结果/86失败及未保存源标志；原脚本/7报告交付SHA；86259保护表语义及618并发新增的global FAIL保留；23个报告明确文件引用实际访问。追加上下文检查还核对了start/common/prefix/safe与原输入记录完全一致。

**5个Blend只核对字节，不打开/重算场景。** 2个有BLENDER前缀，3个有Zstandard帧前缀；压缩内容未解码。13个Action检查基于既有受保护记录，不是从当前Blender重新提取。NPZ容器通过也不等于重新计算碰撞。当前历史轨迹仍103样本86失败、连续桥接资格false，迁移路径审计不改变任何运动结论。

23个 O.parent 路径表达式中9个文件表达式有适配实读证据，14个目录/未展开项只是静态说明。矩阵中的PASS仅限所写的读取/记录边界。动态exec、CWD/CLI、native ABI、原生linked资源与其他16目录入口仍未验证，详见U01–U07。

|执行检查|结果|范围|
|---|---|---|
|registry_all_actual_reads_SHA_match|PASS|READ_ONLY_EXECUTED|
|formal_hands_root_resolves|PASS|READ_ONLY_EXECUTED|
|uncorrected_formal_parent_would_be_wrong|PASS|READ_ONLY_EXECUTED|
|pilot_formal_alias_maps_to_immutable_shadow|PASS|READ_ONLY_EXECUTED|
|raw_MIDI_PPQ_tempo|PASS|READ_ONLY_EXECUTED|
|23_notes_46_original_MIDI_bindings|PASS|READ_ONLY_EXECUTED|
|source_timeline_original_bindings|PASS|READ_ONLY_EXECUTED|
|locked_C01_fingers_unchanged|PASS|READ_ONLY_EXECUTED|
|historic_MIDI_revalidation_consistent|PASS|READ_ONLY_EXECUTED|
|frozen_blend_containers_actual_byte_SHA_access|PASS|BYTE_CONTAINER_ONLY_NOT_BLENDER_REEXECUTION_OR_COMPRESSED_NATIVE_PARSE|
|skin_NPZ_CRC_and_header_structure|PASS|READ_ONLY_EXECUTED|
|actual_88_key_geometry_source_matches_skin_metadata|PASS|READ_ONLY_EXECUTED|
|13_existing_key_Action_digest_records_match|PASS|EXISTING_NATIVE_AUDIT_RECORDS_READ_ONLY_NOT_FRESH_ACTION_EXTRACTION|
|serialized_original_Action_FCurves_equal|PASS|RECORD_CONSISTENCY_ONLY|
|historical_103_actual_records_and_86_failures_preserved|PASS|HISTORICAL_RECORD_RECHECK_NOT_GEOMETRY_RECOMPUTE|
|historical_native_Action_source_not_saved_flags|PASS|HISTORICAL_RECORD_RECHECK|
|103_actual_skin_evidence_archives_accessible_CRC|PASS|READ_ONLY_EXECUTED|
|historic_code_SHA_bindings|PASS|READ_ONLY_EXECUTED|
|historic_86259_protection_semantics_unchanged|PASS|HISTORICAL_MANIFEST_CONTENT_NOT_CURRENT_GLOBAL_REHASH|
|seven_original_report_delivery_SHA_bindings|PASS|READ_ONLY_EXECUTED|
|all_23_concrete_report_filename_references_read|PASS|EXPLICIT_CONCRETE_FILENAMES_ONLY_NOT_ARBITRARY_PROSE_LINK_PROOF|
|six_side_effect_or_unlisted_access_denial_probes|PASS|READ_ONLY_EXECUTED|
|original_R2_not_read_by_adapter|PASS|READ_ONLY_EXECUTED|

首次只读run01因审查器错误地假设所有Blend为非压缩头而停止，原保护SHA始终一致；没有修改源文件。v1 run02/03通过22项但一个裸日志名未闭合；增加独立Manifest定位后v2 run04/05通过23项。原运行日志、版本副本和全部失败/较早结果保留，不把实施错误包装成原资产变化。详见AUDIT_IMPLEMENTATION_INCIDENTS.json。
