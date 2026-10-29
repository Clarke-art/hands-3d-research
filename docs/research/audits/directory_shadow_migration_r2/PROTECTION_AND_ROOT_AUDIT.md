# 内容保护与根目录审计

源R2原207文件的成员、SHA、size/mtime/文件身份全部保持；影子207成员和SHA保持，未新增字节码或修改冻结源码。44个登记外部输入与既有合同/保护SHA一致，包括5个原生源容器、正式MIDI和指法绑定。R1复用的11份证据/规则SHA不变；3份历史保护状态原文件与R1记录SHA一致。详细逐项证据见PROTECTION_FINAL_RESULTS.json。

历史85850 global FAIL（3并发变化/15新增）、86148 PASS、R2 86259 global FAIL（618并发新路径）原样保留。86259 before/after保护表的原绝对路径语义不改写。当前不重新全量re-hash这些路径，也不宣布并发Piano全目录global PASS；本轮读取/写入足迹与历史全局状态分开。

root开始与结束成员集合完全相同：19项（hands、piano、17个历史hands_*）。added=[]、removed=[]，未观察一级并发变化，无需回滚或归因任何root变化。Piano聊天active，但其内部状态不在本轮全量复验范围；未向它发送消息/停止任务，也未修改其目录或任何原资产。

正式迁移目标 `<HANDS_ROOT>\hands_long_context_corridor_ik_bridge_r2` 不存在；本轮所有新增文件和测试副本在 `<HANDS_ROOT>\audits\directory_shadow_migration_r2`。根目录未创建文件、文件夹、符号链接或junction。影子副本保留，不自动清理。R3正确/错误目标均未创建，运动研发运行数0。

六项安全阻断探测在真正操作前拒绝：未登记读、formal写、源R2写、影子源写、历史路径exec哨兵、root链接。不是实际删除/重写源资产测试。复制/适配器窗口的只读pin和终检保护既有字节；快照/逐项probe不是迁移时的永久锁或完整句柄枚举。

**实际迁移0/17，root尚未只剩hands+piano，整理未完成。**
