import sys
sys.dont_write_bytecode=True
import json,hashlib,time
from pathlib import Path
O=Path(__file__).parent;H=O.parents[1];ROOT=H.parent
def rd(n):return json.loads((O/n).read_text(encoding='utf8'))
def save(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def md(n,s):(O/n).write_text(s,encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
rows=rd('MIGRATION_DECISIONS.json');v=rd('VERIFICATION_RESULTS.json');idx=rd('REFERENCE_INDEX.json');effects=rd('STATIC_PATH_IMPACT.json');r3=rd('R3_PATH_PRECHECK.json')
assert v['all_checked_unchanged'] and v['approved_assets_all_same'] and v['historical_records_all_unchanged']
assert len(rows)==17 and not any(r['migrated'] for r in rows)
logical=sum(r['logical_bytes'] for r in rows);allocated=sum(r['allocated_bytes_unique_file_id'] for r in rows);count=sum(r['file_count'] for r in rows)
concurrency={'time_Asia_Shanghai':'2026-10-14','thread_snapshots':['THREAD_SNAPSHOT.json','THREAD_SNAPSHOT_AFTER.json'],'process_snapshots':['PROCESS_SNAPSHOT_BEFORE.json','PROCESS_SNAPSHOT_DURING.json'],'observed_active_hands_threads':['01a13542-438f-7292-b4c5-90dc629884bb (this directory correction task)'],'observed_active_piano_thread':'01a13594-f1b6-7c02-a93b-a6f036d5a0d5','piano_readonly_recent_turn_evidence':{'turn':'01a1379a-9032-7222-9684-f43a79045d6b','task':'LOCAL_GB_01_DEPENDENCY_CLOSURE_R1','observed_status':'inProgress','authorization_scope':'Own isolated dependency-closure plan/test results; prohibits actual cleanup/moving/overwriting source assets'},'R3_named_process_observed':False,'R3_wrong_directory_found':False,'R3_correct_directory_found':False,'legacy_cleanup_pid_368_present':False,'legacy_cleanup_server_final_report':'验收服务结束后关闭','process_observation_limit':'Snapshot evidence, not exhaustive handles/CWD proof. Blender MCP infrastructure exists; no observed Blender application/solver/R3 command for these trees. No other thread was messaged or stopped.'}
save('CONCURRENCY_ASSESSMENT.json',concurrency)
save('R3_OUTPUT_PATH_CORRECTION.json',{'task':'PIANO_CONTACT_EXECUTION_FOUNDATION_R3','required_output_directory':str(H/'hands_contact_execution_foundation_r3'),'obsolete_root_target':str(ROOT/'hands_contact_execution_foundation_r3'),'obsolete_target_exists':False,'correct_target_exists':False,'rule_persisted_in':str(H/'AGENTS.md'),'rule_sha256':sha(H/'AGENTS.md'),'R3_experiment_creation_or_research_authorized_by_this_audit':False,'R3_started':False,'future_precondition':'Before first R3 write, inspect running state and use only required_output_directory. If a wrong-root R3 is discovered later, suspend new writes there and review before any move.'})
hist=[]
for d,n in [('hands_early_hand_preparation_entry_reachability_r1','PROTECTION_SCOPE_AUDIT.json'),('hands_long_context_hand_motion_architecture_r1','PROTECTION_CHECK.json'),('hands_long_context_corridor_ik_bridge_r2','R2_PROTECTION_SCOPE_AUDIT.json')]:
 p=ROOT/d/n;x=json.loads(p.read_text(encoding='utf8'));hist.append({'path':str(p),'sha256':sha(p),'status':x.get('global_protection_status',x.get('status')),'reinterpreted_or_replaced':False})
save('HISTORICAL_PROTECTION_PRESERVATION.json',{'records':hist,'historical85850_global_FAIL_3_changes_15_additions_preserved':True,'historical86148_PASS_preserved':True,'historical86259_global_FAIL_618_concurrent_new_paths_preserved':True,'this_audit_local_unchanged_check_is_not_a_new_global_piano_PASS':True,'historic_cleanup_successful_missing_exceptions_preserved_in_original_ledger':True})
table='\n'.join(f"|{r['name']}|{r['file_count']:,}|{r['logical_bytes']/1024**2:.3f}|{r['allocated_bytes_unique_file_id']/1024**2:.3f}|{r['incoming_potential_runtime_source_count']}|{r['latest_R2_protection_entries']}|待 Human 批准|" for r in rows)
body=f'''# 3D Hands 目录结构纠偏审计 R1

2026-10-14，Asia/Shanghai。**审计与固定约束已落实；迁移 0/17，目录整理未完成，STOP — HUMAN REVIEW。**

Human 要求的根目录规则已写入 `{H/'AGENTS.md'}`。后续 Hands 研发、实验、审计、日志、临时文件只能在 hands 内；本轮所有新增文件亦在 hands 内。R3 唯一输出路径为 `{H/'hands_contact_execution_foundation_r3'}`，未启动 R3 技术研发。

当前 17 个目录都有未闭合的路径或复核风险，按本次要求“确认安全才允许迁移”“存在风险则先报告，不强制移动”保留原位。没有覆盖、删除、修改冻结成果，没有创建根目录符号链接/junction，也没有移动 piano。**不是所有历史 manifest 成员都天然禁止迁移；本次暂缓依据是实际代码路径阻碍及尚未验证的保护/复核映射。**

## 完整盘点

共同原父目录：`{ROOT}`。每项完整原路径、拟议新路径、用途、使用证据和源码行号见 [逐目录明细](DIRECTORY_DETAILS.md)、[CSV](DIRECTORY_INVENTORY.csv)、[机器决策](MIGRATION_DECISIONS.json)。

17 个目录共 **{count:,} 文件，{logical:,} 逻辑 bytes（{logical/1024**3:.6f} GiB）**；Windows FileStandardInfo 报告分配量合计 {allocated:,} bytes（{allocated/1024**3:.6f} GiB）。逻辑体积和分配量分开报告，目录/MFT 元数据未计入。同盘移动不会释放这些内容的磁盘空间。本轮没有压缩、去重或清理。

|目录|文件数|逻辑 MiB|报告分配 MiB|外部源码引用文件数*|R2 旧保护表成员数|决定|
|---|---:|---:|---:|---:|---:|---|
{table}

*引用数是匹配到目录名的可执行源码/配置文件数量，含历史复核和初始化；不是当前运行调用次数，亦不是全部都已证实为直接读取。准确调用位置、字面绝对路径和父层级依赖已单独记录。没有把“无活动进程”解释为“不再使用”。

## 为什么不能直接整体搬入

1. **父层级假设已证实会失效。** 多个脚本以 `O=Path(__file__).resolve().parent`、`ROOT=O.parent/'hands'` 找源码和 `_deps`。即使 17 个目录一起移动，ROOT 仍会变成 `hands\\hands`。R2 的 `verify_midi.py:4` 同样如此；它虽没有外部直接引用，仍不能免除复现检查。
2. **历史审计自身仍有固定路径读取。** `hands_cleanup_audit_r1/execution_r1.py:6` 将 O 固定为旧根目录，69–70 行从 O 读取锁定 Manifest、原库存、分类表和批准账本；74–75 行检查锁定哈希，201、214、218 行继续读取原验证输入。直接移动后这些读取找不到文件。没有为迁移修改这份历史删除程序或重新执行任何清理阶段。
3. **跨目录输入必须同时闭合。** 比如 C01 来源、B2 静态起点、原生场景、符号函数、CasADi/ONNX 依赖和原 Action 比较数据仍在后续源码中被引用。单独搬入会破坏 sibling 路径；仅改文件夹位置不能证明调用方安全。
4. **旧保护表保留原路径语义。** 前次 R2 的保护表覆盖其中 16 个目录的 {sum(r['latest_R2_protection_entries'] for r in rows):,} 文件，当前全部与旧 SHA 一致。R2 自身在那张输入保护表中为 0，是此前自输出排除，不是无保护/可随意移动。207 个 R2 输出本轮全部建立前后 SHA。不能覆写历史表来“消除缺失”；需新增迁移映射及独立路径验证，且保留旧 FAIL/PASS。

[静态路径影响](STATIC_PATH_IMPACT.json) 保存 {len(effects['effects'])} 条有限 AST 规则结果，其中 {sum(not e['equivalent_after_all_17_moved'] for e in effects['effects'])} 条在整体迁入假设下仍不等价；这不是所有动态/原生路径的完整证明。扫描 {len(idx)} 个匹配文件，编码错误 0。没有执行旧求解器、旧审计删除程序、Blender 验证或新技术研发。未知动态路径、外部调用、二进制原生资源关系仍不能被文本扫描排除。

## 活动任务与 R3

前后 Codex 任务快照显示当前 active Hands 聊天是本目录纠偏任务；其余可见 Hands 聊天为 notLoaded。当前另有 active Piano 依赖闭合任务，核对到 `LOCAL_GB_01_DEPENDENCY_CLOSURE_R1`，它的文件未移动、停止或改写。本轮也未向其他聊天发送消息。

进程快照未发现引用这 17 个目录的 R3/求解/渲染命令；历史审计 pid 368 不存在，历史报告记载服务已关闭。进程和任务快照不能排除所有外部动态引用，因此不把它们作为迁移安全的唯一证明。

错误目标 `{ROOT/'hands_contact_execution_foundation_r3'}` 不存在；正确目标也尚未创建。R3 名称的本地引用仅来自本轮新 AGENTS 规则，未发现需移动的 R3 输出。只纠正后续目标路径，未创建实验、未产生技术结果；后续正式启动时仍需再核对当时运行状态。见 [R3 路径登记](R3_OUTPUT_PATH_CORRECTION.json)。

## 迁移记账与内容保护

- [路径映射](PATH_MAPPING.json) 的 17 行均为 **PROPOSED_ONLY**；实际迁移数组为空。各目标路径均无同名冲突。没有冒用“映射已登记”声明迁移完成。
- 17 个原目录的 **{count:,} 文件前后 SHA-256 全部相同**，成员无新增、无缺失；补充有效文件身份也未变化。清理审计 34 文件/{next(r['logical_bytes'] for r in rows if r['name']=='hands_cleanup_audit_r1'):,} bytes 的 Manifest、批准账本和历史报告完整保留。
- 原 hands 中 **19,779 文件**全部建立 before SHA，结束时全部 size/mtime 复核；其中 **{next(g['after_hash_count'] for g in v['groups'] if g['name']=='hands'):,} 个原生/科学/源码后缀文件**另做 after SHA，全部相同。大体积媒体/图像本轮结束时仅复核元数据，不声称它们全量 after SHA。六项已批准原生资产与批准哈希全部一致；正式 MIDI、已有 .blend 内 Rig/Action、源指法绑定未修改。
- 85850 项历史全局 FAIL（3 处并发变化、15 新增）、86148 项历史 PASS、86259 项 R2 全局 FAIL（618 并发新路径）及账本中的获批清理缺失例外原样保留。本轮局部字节一致不重置任何历史结论；亦不声称正在并发写入的 piano 全目录当前全局 PASS。
- 新增范围只有 hands/AGENTS.md 和本审计子目录。目录调整与 R3 科学预算、轨迹状态、优化调用数分开，技术运行数为 0。

原始证据：[before 清单](FILES_BEFORE.json)、[after SHA](FILES_AFTER_HASHES.json)、[验证结果](VERIFICATION_RESULTS.json)、[引用索引](REFERENCE_INDEX.json)、[保护关系](PROTECTION_RELATIONSHIPS.json)、[历史结论保留](HISTORICAL_PROTECTION_PRESERVATION.json)。Windows DirEntry.stat 的 inode/device/nlink 返回 0，原始 before 表这三列不作身份依据；已使用 Path.stat 补充有效身份并独立验证，原始表和问题说明都保留。分配量采用有效身份重新计算，未沿用错误的 0-ID 去重值。

## 留待 Human 审核的具体范围

**17 个目录全列为 PENDING_HUMAN_APPROVAL，尚无可直接执行的安全批次。** 其中 cleanup 审计需先决定只读历史复核入口如何在新路径使用锁定输入；其他实验需决定路径适配是否可在新增副本/适配入口实现，涉及旧源码/冻结合同的改写必须另有明确授权。

可审查的迁移目标和阻碍已逐项提供。后续若批准，应先在 hands 内准备不会重跑求解/清理的路径复核方案，验证正式 hands/piano 根、跨实验来源、输入 SHA 与可访问性；对动态/native 未闭合项继续保护。实际移动时使用精确旧→新路径、拒绝覆盖、迁前实时重查活动任务和文件身份、迁后逐文件 SHA/成员及引用复核，再登记 `PATH_RELOCATION` 事件。旧 manifest、历史源码/FAIL 不覆盖，不创建旧根链接。

## 根目录终检与结束

[ROOT_AFTER.json](ROOT_AFTER.json) 实测根目录仍有 **hands、piano 和原 17 个 hands_* 共 19 项**；`only_hands_and_piano=false`。固定规则已落地，根目录符合性尚未达成。没有把未完成整理伪报为 PASS。

**STOP — HUMAN REVIEW。不自动开始迁移、其他清理或 R3 技术研发。**
'''
md('DIRECTORY_CORRECTION_REPORT.md',body)
details=['# 17 个目录逐项清单与迁移风险\n','所有新路径均为拟议，均未执行迁移；每项目标无冲突。用途来自原目录报告与源码。占用以逻辑 MiB 报告；分配量、完整文件 SHA、保护记录另见机器附件。\n']
for r in rows:
 n=r['name'];details += [f'## {n}\n',f"原路径：`{r['source']}`\n\n拟议路径：`{r['proposed_destination']}`\n\n用途：{r['purpose']}。\n\n占用：{r['file_count']:,} 文件 / {r['directory_count_including_root']} 目录（含根），{r['logical_bytes']:,} bytes，{r['logical_bytes']/1024**2:.3f} MiB；分配量 {r['allocated_bytes_unique_file_id']:,} bytes。无 reparse、无检测到硬链接、目标无冲突。\n\n使用状态：{r['observed_running_task']}。保留作用：{r['retained_use']}。\n\n保护关系：最新 R2 输入保护表 {r['latest_R2_protection_entries']} 条/{r['latest_R2_protected_same_hash']} 条 SHA 一致；引用该目录的保护记录文件 {r['historical_path_bound_protection_record_count']} 个。当前目录全部文件本轮 before/after SHA 一致。\n\n决定：**PENDING_HUMAN_APPROVAL；未迁移；迁后可复现性 NOT_VALIDATED**。\n\n具体阻碍：\n"]
 details += ['- '+t+'\n' for t in r['reasons']]
 details += ['\n路径证据（完整行号索引在 JSON，以下为代表）：\n']
 for e in r['own_blocking_static_path_evidence'][:3]:
  details.append(f"- `{e['source']}:{e['line']}`，`{e['expression']}`。迁入后实际仍指向 `{e['after_all_17_moved_path']}`；应为 `{e['expected_after_mapping']}`。\n")
 for e in r['incoming_runtime_evidence'][:3]:
  example=e['examples'][0] if e['examples'] else {};text=example.get('text','').replace('\n',' ')[:550]
  details.append(f"- 外部源码 `{e['source']}:{example.get('line','?')}`：`{text}`。这是保留路径的复核/输入线索，不宣称当前正在运行。\n")
 details.append('\n用途来源：'+', '.join('`'+p+'`' for p in r['purpose_source_documents'])+'。\n\n')
md('DIRECTORY_DETAILS.md','\n'.join(details))
md('HUMAN_REVIEW.md',f'''# Human 审核 — Hands 目录纠偏 R1

**固定规则已生效，审计完成；实际迁移 0，17 个目录全部暂缓。根目录仍有 19 项，整理未完成。**

全部目录 {count:,} 文件、{logical/1024**3:.6f} GiB 逻辑体积；前后文件 SHA 全部相同，旧清理审计及历史并发 FAIL 均保留。目标均无同名冲突，活动任务快照未发现 Hands R3；另有 Piano 并发任务，未触碰其资产。

直接搬入会破坏 `O.parent/'hands'` → `hands\\hands` 的路径假设。历史 cleanup 的执行脚本也从硬编码旧 O 读取锁定 Manifest/批准账本。相关源码和旧保护表不能为整理目录而擅自改写，所以按本次“存在风险则先报告、不强制移动”停止。

请审阅 [完整报告](DIRECTORY_CORRECTION_REPORT.md) 和 [逐目录来源/目标/风险](DIRECTORY_DETAILS.md)。待决定的是：是否另行授权在 hands 内建立保留旧字节与历史结论的路径适配/复核入口，并在该检查闭合后执行这 17 个精确映射。当前不将这个建议当作已获批准的下一轮。

R3 目标已固定为 `{H/'hands_contact_execution_foundation_r3'}`；没有启动技术研发或新建 R3 实验。

**STOP — HUMAN REVIEW。**
''')
save('AUDIT_INCIDENTS.json',{'resolved_audit_script_issues':[{'issue':'Reference reader misspelled encoding utf8-sig','resolution':'Corrected task-owned script to utf-8-sig; resumed reference phase using already completed before hashes. No source rehash or historical output change.'},{'issue':'Windows DirEntry.stat identity fields unavailable/zero caused invalid allocation dedup in first derived result','resolution':'Original FILES_BEFORE preserved; supplemental valid Path.stat identities, FileStandardInfo allocation and all-directory after hashes collected. Corrected derived space/decisions. Zero-ID result not used for acceptance.'}],'automatic_approval_rejections_this_task':[],'asset_or_history_edits':[],'moves':[]})
save('FINAL_STATUS.json',{'task':'HANDS_DIRECTORY_STRUCTURE_CORRECTION_R1','status':'AUDIT_COMPLETE_MIGRATION_PENDING_HUMAN_REVIEW','directory_rule_persisted':True,'rule_file':str(H/'AGENTS.md'),'R3_required_output':str(H/'hands_contact_execution_foundation_r3'),'R3_started':False,'audited_root_hands_experiment_directories':17,'experiment_files':count,'experiment_logical_bytes':logical,'actual_migrations':0,'pending_Human_approval_directories':17,'root_entries':19,'root_only_hands_piano':False,'source_asset_content_mutations':0,'experiment_before_after_SHA_same':True,'historical_protection_FAIL_preserved':True,'root_relocation_events':[],'symbolic_links_created':[],'piano_mutations':[],'cleanup_or_scientific_execution_calls':0,'stop':'STOP — HUMAN REVIEW','automatic_next_task':False})
deliveries=[]
for p in sorted(O.iterdir()):
 if p.is_file() and p.name!='DELIVERY_MANIFEST.json':deliveries.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
save('DELIVERY_MANIFEST.json',{'entries':deliveries,'AGENTS_sha256':sha(H/'AGENTS.md'),'status':'STOP_HUMAN_REVIEW','scope':'Task-owned audit artifacts only; manifest itself excluded.'})
print(json.dumps({'status':'AUDIT_COMPLETE_MIGRATION_PENDING_HUMAN_REVIEW','report':str(O/'DIRECTORY_CORRECTION_REPORT.md'),'deliveries':len(deliveries),'all17_hash_same':True,'root_only_hands_piano':False},ensure_ascii=False))
