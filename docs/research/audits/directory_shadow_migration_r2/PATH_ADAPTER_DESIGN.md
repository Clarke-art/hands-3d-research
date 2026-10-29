# 最小独立路径适配入口

原207文件的所有字节保持不变。入口由本审计新增 `readonly_path_adapter.py` 和 `run_readonly_validation.py` 构成，原代码、pathlib 和历史Manifest均不修改；也没有root链接、junction、sys.path劫持或导入钩子来偷偷执行旧代码。

配置以正式 `<HANDS_ROOT>` 为明确源码根，用旧保护键作为逻辑身份。只有已登记路径才可解析。R2旧绝对路径和未创建的formal路径都映射到同SHA的物理影子；其他历史输入当前仍位于原位置，以原保护SHA只读访问。未来若其他目录获批迁移，必须新增明确的逻辑→物理登记，不依赖“找不到就猜另一个目录”。

这证明 formal 逻辑位置的独立入口可以读取正确资源；**不是原程序从新位置原样运行成功**，也不是只替换字符串后就宣称复现。旧 `O.parent/'hands'` 表达式仍会产生hands\hands；独立入口绕开该上下文假设，并按历史调用证据读取实际源文件。

报告里的裸日志名先按R2内部相对文件匹配；未登记时仅允许从完整不可变复制Manifest中找到唯一同名文件，实际得到 `logs/candidate_front_bridge_execution.log`。多重匹配或未登记一律失败，不做文件系统通配fallback。

只读运行开始前对251个输入持有拒绝写/删除共享的读句柄。Python audit hook将读操作限定为精确登记文件，只允许写两份本次run结果；阻止额外读取、源/影子/formal写入、历史代码exec、进程启动、删除、rename和root链接等。六项阻断探测使用无副作用哨兵/打开请求，均在实际写或历史代码执行前被拒绝；没有真的运行删除/求解/渲染脚本。审计钩子不是任意native代码的全局沙箱，因此本轮根本不加载这些native库。

运行入口：`python -B -X utf8 "<HANDS_ROOT>\audits\directory_shadow_migration_r2\run_readonly_validation.py" readonly_06`。必须使用新的readonly_NN名，已有run会拒绝覆盖。已实际执行最终readonly_04和readonly_05，两次结果一致。历史文件仅读取，不import；MIDI由新增纯标准库读器解析，NPZ仅ZIP/CRC/NPY数字容器检查，无pickle或数学库加载。

可复用的是登记/精确SHA/逻辑映射/安全读机制。R2-specific复核断言和危险原命令不是通用验证器；其他16目录需自己的增量读白名单及源语义检查。cleanup必须另建只读账本入口，不执行execution_r1.py。
