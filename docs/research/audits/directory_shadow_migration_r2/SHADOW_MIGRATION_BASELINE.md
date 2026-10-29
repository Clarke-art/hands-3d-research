# 迁移影子 R2：只读基线

2026-10-14，Asia/Shanghai。复用 R1 清单，未重复17目录完整普查。本轮原目录 `<HANDS_ROOT>_long_context_corridor_ik_bridge_r2`，正式拟目标 `<HANDS_ROOT>\hands_long_context_corridor_ik_bridge_r2` **未创建**。测试位置 `<HANDS_ROOT>\audits\directory_shadow_migration_r2\shadow\hands_long_context_corridor_ik_bridge_r2`。

原 R2 **207 文件 / 4 目录 / 59,560,325 bytes（56.801 MiB）**，成员和每项 SHA 与 R1 完全一致；全部207复制、复制后及结束 SHA 一致。源/影子完整保留，不自动清理。正式Rig/场景未复制，只登记只读来源。

当前任务快照未观察到其他 active Hands 聊天或R2/R3写入进程；Piano聊天仍active，不停止或改写其文件。Restart Manager 返回29，不能声称完整打开句柄枚举。全部207源在哈希/复制时同时持有 FILE_SHARE_READ-only 句柄；任何冲突写者会使建立基线失败。随后207逐项独占只读打开成功；最终 source identity/size/mtime/成员/SHA均一致。句柄证据是有限时间基线，不替代未来迁移即时检查。

实际外部输入44项，详细角色/源码依据/原保护SHA见 `PATH_ADAPTER_REGISTRY_V2.json`，含正式MIDI与timeline、锁定C01、5个原生场景/冻结资源、Rig接口和4个performance_core JSON、原Action比较、B2/早期前缀/安全姿态输入、CasADi符号文件和现有包资源。每项真实读取并按既有保护表或锁定合同核对SHA。

|表达式|旧 R2|正式新位置（仅推导，未创建）|深层影子直接运行的推导|独立入口实际位置|
|---|---|---|---|---|
|`O.parent / "hands"`|`<HANDS_ROOT>`|`<HANDS_ROOT>\hands`|`<HANDS_ROOT>\audits\directory_shadow_migration_r2\shadow\hands`|`<HANDS_ROOT>`|
|`O.parent / "hands_sequence_fingering_planning_r1/SOURCE_EVENT_BINDINGS.json"`|原根下历史目录|hands 内对应目录（尚不存在）|影子父层下对应目录（不存在）|当前原历史输入，只读SHA；将来须显式更新迁移映射|


`verify_midi.py:4` 将 __file__ 的父层级用作项目根；6/25行读取source绑定/指法，26行写回 SOURCE_MIDI_REVALIDATION.json，因此本轮不执行它。`skin_proxy.py` 同样计算 `ROOT=O.parent/'hands'` 并动态提取历史函数；`rig_model.py` 读B2/参考、`coupled_model.py` 加载符号资源、`batch_verify.py` 打开场景并在调用时改内存姿态，均只读取源码，不导入执行。

实际运行输入和历史复核/准备路径已按源码行号分别登记：23个父层级表达式中9个文件表达式通过独立入口实读；14个目录或未展开项只是静态说明。全模块副作用/动态调用清单见 `LEGACY_SOURCE_SAFETY_AUDIT.json`，动态/native未闭合见 `UNVERIFIED_DYNAMIC_NATIVE_DEPENDENCIES.json`。

证据：PILOT_BASELINE.json、SHADOW_COPY_MANIFEST.json、OPEN_RESOURCE_CENSUS.json、EXCLUSIVE_READ_RESOURCE_PROBES.json、LEGACY_PATH_EXPRESSIONS.json、R1_EVIDENCE_BINDINGS.json。
