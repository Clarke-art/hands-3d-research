import sys
sys.dont_write_bytecode=True
import json,os,hashlib,time,re,collections
from pathlib import Path
from readonly_path_adapter import PathAdapter
O=Path(__file__).parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
def save(n,x):
 with (O/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def md(n,t):
 with (O/n).open('x',encoding='utf8') as f:f.write(t)
reg=rd(O/'PATH_ADAPTER_REGISTRY_V2.json');A=PathAdapter(reg);ROOT=Path(reg['project_root']);H=Path(reg['hands_root']);S=A.shadow;R1=H/'audits/directory_structure_correction_r1';base=rd(O/'PILOT_BASELINE.json');copy=rd(O/'SHADOW_COPY_MANIFEST.json');runs=[rd(O/f'runs/{n}/RESULTS.json') for n in ['readonly_04','readonly_05']]
assert all(x['status']=='PASS_READ_ONLY_SCOPED_TESTS' for x in runs) and runs[0]['semantic_fingerprint']==runs[1]['semantic_fingerprint']
def scan(r):
 stack=[r];files=[];dirs=[]
 while stack:
  d=stack.pop();dirs.append(str(d.relative_to(r)))
  for e in os.scandir(d):
   p=Path(e.path);s=p.stat(follow_symlinks=False);assert not s.st_file_attributes&0x400,str(p)
   if s.st_file_attributes&0x10:stack.append(p)
   else:files.append(str(p.relative_to(r)))
 return sorted(files),sorted(dirs)
source_members,source_dirs=scan(A.source);shadow_members,shadow_dirs=scan(S);expected=sorted(x['relative'] for x in base['files']);assert source_members==shadow_members==expected and source_dirs==shadow_dirs
protected=[]
for row in base['files']:
 p=Path(row['path']);st=p.stat();h=sha(p);same=h==row['sha256'];identity=(st.st_size,st.st_mtime_ns,st.st_dev,st.st_ino)==(row['bytes'],row['mtime_ns'],row['device'],row['file_id']);shadow_sha=sha(S/row['relative']);assert same and identity and shadow_sha==h,str(p)
 protected.append({'source':str(p),'shadow':str(S/row['relative']),'before_sha256':row['sha256'],'source_after_sha256':h,'shadow_after_sha256':shadow_sha,'source_identity_size_mtime_same':identity,'pass':True})
external=[]
for row in reg['inputs']:
 if Path(row['logical_legacy_path']).is_relative_to(A.source):continue
 p=Path(row['resolved_path']);st=p.stat();h=sha(p);same=h==row['expected_sha256']==row['before_sha256'];assert same and st.st_size==row['bytes'] and st.st_mtime_ns==row['mtime_ns'],str(p)
 external.append({'path':str(p),'before_expected_sha256':row['expected_sha256'],'after_sha256':h,'roles':row['roles'],'unchanged':True})
ev=[]
for x in rd(O/'R1_EVIDENCE_BINDINGS.json'):
 h=sha(x['path']);assert h==x['sha256'];ev.append({'path':x['path'],'sha256':h,'unchanged':True})
historic=[]
for x in rd(R1/'HISTORICAL_PROTECTION_PRESERVATION.json')['records']:
 h=sha(x['path']);assert h==x['sha256'];data=rd(x['path']);historic.append({'path':x['path'],'sha256':h,'status':data.get('global_protection_status',data.get('status')),'unchanged_from_R1':True,'reset_to_PASS':False})
root_after=[p.name for p in sorted(ROOT.iterdir())];root_before=rd(O/'ROOT_BASELINE.json')['members'];assert root_after==root_before;assert not A.formal.exists();assert not (ROOT/'hands_contact_execution_foundation_r3').exists() and not (H/'hands_contact_execution_foundation_r3').exists()
save('FINAL_PROTECTION_OPERATION_WHITELIST.json',{'source_pilot_files':base['files'],'shadow_files':copy['files'],'external_inputs':external,'R1_readonly_evidence':ev,'historical_status_records':historic,'root_operation':'first-level metadata only','mutating_whitelist':'Only task-owned files under this audit; no original tree writes/moves/deletes/links','R3_operations':[]})
save('PROTECTION_FINAL_RESULTS.json',{'original_R2_files':protected,'original_R2_members_same':True,'shadow_members_same':True,'shadow_directories_same':True,'source_R2_all_SHA_same':True,'shadow_all_SHA_same':True,'external_inputs':external,'external_input_files':len(external),'external_input_SHA_all_same':True,'R1_evidence':ev,'historical_records':historic,'source_moves':[],'source_deletions':[],'source_mutations':[],'created_root_links':[],'formal_migration_target_created':False,'piano_mutations_by_this_task':[],'piano_entire_current_state_PASS_claimed':False,'read_native_container_hash_only':True})
save('ROOT_FINAL_AUDIT.json',{'before':root_before,'after':root_after,'same_members':True,'added':sorted(set(root_after)-set(root_before)),'removed':sorted(set(root_before)-set(root_after)),'concurrent_root_change_attribution':[],'no_rollback':True,'only_hands_and_piano':False,'historical_hands_experiment_dirs':17,'actual_migrations':0})
# Actual secondary record consistency checks through the same immutable path adapter.
ctx=A.json(A.pilot('R2_CONTEXT_RAW.json'));anchors=A.json(A.source.parent/'hands_early_hand_preparation_entry_reachability_r1/ANCHOR_REQUESTS.json');prefix=next(x for x in A.json(A.source.parent/'hands_early_hand_preparation_entry_reachability_r1/ENTRY_ACTUAL_SAMPLES.json') if x['id']=='entry_sample_39');safe=next(x for x in A.json(A.source.parent/'hands_long_context_hand_motion_architecture_r1/HIGH_LEVEL_CLEARANCE_ACTUAL.json') if x['id']=='high_level_above')
context_checks={'start_matches_original_anchor':ctx['known_start']==anchors[0],'common_matches_original_anchor':ctx['reference_common']==anchors[1],'prefix_matches_original_actual':ctx['known_prefix_endpoint']=={'time':prefix['display_time'],'latent':prefix['latent'],'state':prefix['state']},'safe_matches_original_actual':ctx['reference_safe']=={'time':safe['display_time'],'latent':safe['latent'],'state':safe['state']}}
assert all(context_checks.values());save('AUXILIARY_CONTEXT_VALIDATION.json',{'checks':context_checks,'reads':A.reads,'scope':'Recorded source binding recheck, no new FK/Blender/trajectory calculation'})
unknowns=[
 {'id':'U01','item':'完整原脚本/命令原样复现','status':'NOT_COMPATIBLE_WITHOUT_ENTRY_ADAPTATION / NOT_EXECUTED','evidence':'verify_midi.py 会写结果且 O.parent 导出错误源目录；其他脚本使用相同层级假设','authorization_needed':'若要求原命令执行，需另行设计/批准安全运行适配，不允许本轮直接执行'},
 {'id':'U02','item':'Blender 原生加载、压缩 .blend 解析、linked resources、驱动/handler、GUI/版本环境','status':'UNKNOWN_NOT_EXECUTED','evidence':'5 个 .blend 内容 SHA 与合同相同；2 个 BLENDER 前缀、3 个 Zstandard 帧前缀，未解压或打开场景','authorization_needed':'另行白名单化原生只读加载验证；不可运行冻结场景脚本或保存源资产'},
 {'id':'U03','item':'NumPy/SciPy/CasADi native loader、DLL 搜索与 ABI、优化器 plugin','status':'UNKNOWN_NOT_EXECUTED','evidence':'已读取当前 declared _deps/deps 的初始化源码与6个 native 文件字节；未导入数学包、未 load CasADi function、未调用优化器','authorization_needed':'单独隔离和无副作用加载验证，不能借路径治理启动求解'},
 {'id':'U04','item':'AST exec/compile 提取函数、CLI、CWD、动态请求命名和现场分支','status':'STATIC_ONLY / PARTIAL_RECORDED_INSTANCE_READ','evidence':'23 个 O.parent 字面表达式，9 个文件表达式实际适配读取，14 个目录/未展开表达式只有静态说明；103个已记录请求文件实际读过不代表任意请求','authorization_needed':'新增有限只读审查器或明确安全切片；不得执行历史初始化'},
 {'id':'U05','item':'项目全部外部输入/报告任意 prose URL/文件与所有保护清单全量当下复验','status':'NOT_CLAIMED','evidence':'251资源是具体白名单，44外部输入；报告23个明确文件名已读；86259保护表仅语义与文件字节核对，不重盘点/重哈希全项目','authorization_needed':'按确切未闭合读取增量补充，不开展完整重复普查'},
 {'id':'U06','item':'全部打开文件/句柄和所有外部任务引用','status':'UNKNOWN_EXHAUSTIVE_ENUMERATION','evidence':'Restart Manager error29；207源文件同时拒绝写/删除共享的复制基线和207逐项独占只读探测通过，任务/进程快照未观察R2 writer','authorization_needed':'真实迁移前即时重查并建立原子/句柄保护；快照不能替代迁移时保护'},
 {'id':'U07','item':'其他16个目录的独立入口、冻结引用映射与 cleanup 锁定账本复核','status':'NOT_EXECUTED_PLAN_ONLY','evidence':'复用R1清单和路径分析；未复制/测试其他目录、未执行execution_r1.py任何阶段','authorization_needed':'每批增量白名单验证，cleanup 必须另证锁定输入/账本读取，绝不重跑删除'}]
save('UNVERIFIED_DYNAMIC_NATIVE_DEPENDENCIES.json',unknowns)
matrix=[
 {'item':'影子副本完整性','result':'PASS','evidence':'207文件、目录成员与源相同，复制和结束SHA全部相同'},
 {'item':'内部路径解析','result':'PASS_VIA_INDEPENDENT_ADAPTER','evidence':'真实登记文件读取、formal→shadow、明确hands root；未修改 pathlib/源码；原表达式原样仍错误'},
 {'item':'外部输入','result':'PASS_SCOPED_44_FILES / TRANSITIVE_RUNTIME_PARTIAL','evidence':'正式MIDI、Rig/场景5容器、13 Action记录、历史输入和既有资源逐SHA实读；无原生执行'},
 {'item':'历史保护引用','result':'PASS_PRESERVED_SEMANTICS','evidence':'旧86259表前后字节/语义一致，历史FAIL与PASS保留；未写新旧globalPASS'},
 {'item':'旧源码完整性','result':'PASS','evidence':'原207和影子207全SHA一致，原源码没有修改/导入/执行'},
 {'item':'正式Hands/Piano资产','result':'PASS_NO_TASK_WRITES_SCOPED_HASH','evidence':'44读取输入SHA不变，所有写操作在本审计；不声称并发Piano全目录无变化'},
 {'item':'原始R2目录','result':'PASS_UNMOVED','evidence':'源成员、SHA、size/mtime/identity一致，formal目标不存在'},
 {'item':'复核适配入口可重复','result':'PASS','evidence':'最终readonly_04/05各23检查/251实读，语义指纹相同'},
 {'item':'动态与原生依赖','result':'PARTIAL_UNVERIFIED_EXPLICIT','evidence':'U01–U07全部登记，不冒用完整Blender/求解复现PASS'}]
save('ACCEPTANCE_MATRIX.json',matrix);save('REPEATABILITY_CHECK.json',{'runs':['readonly_04','readonly_05'],'same_semantic_fingerprint':True,'fingerprint':runs[0]['semantic_fingerprint'],'checks_per_run':23,'resources_per_run':251,'one_additional_context_source_check':context_checks,'original_program_execution_calls':0})
inventory=rd(R1/'DIRECTORY_INVENTORY.json');dependencies={x['name']:x for x in rd(R1/'DEPENDENCY_SUMMARY.json')};groups=[
 ('B1_PILOT',['hands_long_context_corridor_ik_bridge_r2'],'条件候选：已证只读快照＋独立复核入口；Human接受该验收边界后才考虑真实迁移'),
 ('B2_RECENT_LEAF',['hands_long_context_hand_motion_architecture_r1','hands_time_coupled_contact_recovery_r1','hands_early_hand_preparation_entry_reachability_r1'],'低于核心hub的最近证据目录，先增量白名单/自引用/历史FAIL映射，不声称已验证'),
 ('B3_FINGERING_AND_GEOMETRY_CLUSTER',['hands_sequence_fingering_planning_r1','hands_c01_g4_e5_skin_safe_bridge_r1','hands_c01_s1_constrained_solver_feasibility_r1','hands_c01_anatomy_preparation_audit_r1','hands_contact_junction_compatibility_r1','hands_c01_g4_e5_natural_motion_bridge_r2','hands_skin_collision_static_feasibility_r1','hands_c01_whole_hand_motion_feasibility_r1'],'相互引用及高入度核心：联合登记输入/调用方映射，先闭合root假设和原生资源，不逐个盲搬'),
 ('B4_PACKAGES_AND_RECOVERY',['hands_contact_derivative_feasibility_recovery_r1','hands_contact_constrained_trajectory_planning_r1','hands_contact_state_motion_planner_comparison_r1','hands_fingering_inference_poc_r1'],'高风险：依赖包/符号序列化/ONNX/native和大量成员，需包内相对路径/ABI/来源保护专项增量证明'),
 ('B5_CLEANUP_HISTORY',['hands_cleanup_audit_r1'],'单独高风险账本：先独立只读核对锁定Manifest、批准账本、SUCCESS精确缺失例外；不运行历史删除程序')]
plans=[]
for batch,names,rule in groups:
 for n in names:
  x=next(x for x in inventory if x['name']==n);d=dependencies[n]
  plans.append({'batch':batch,'name':n,'source':x['source'],'destination':x['proposed_destination'],'R1_files':x['file_count'],'R1_logical_bytes':x['logical_bytes'],'R1_MiB':x['logical_bytes']/1024**2,'R1_incoming_source_refs':d['incoming_potential_runtime_sources'],'risk':'HIGH_NATIVE_OR_PACKAGE' if batch.startswith('B4') else 'HIGH_DELETION_LEDGER' if batch.startswith('B5') else 'HIGH_DEPENDENCY_HUB' if n in ['hands_c01_whole_hand_motion_feasibility_r1','hands_skin_collision_static_feasibility_r1'] else 'MEDIUM_PATH_CONTRACT','pilot_readonly_validation':'EXECUTED_R2_ONLY' if n==A.source.name else 'NOT_EXECUTED_R1_EVIDENCE_ONLY','candidate_qualification':'CONDITIONAL_READ_ONLY_ARCHIVE_CANDIDATE' if batch.startswith('B1') else 'PLAN_PENDING_INCREMENTAL_CHECKS','rule':rule,'actual_move_authorized':False,'actual_moved':False,'activity_state':'current snapshots no other active Hands chat; no per-file open resource test for non-pilot','protection_requirement':'Never rewrite old manifest/source/FAIL; separate relocation mapping from content hashes','required_gate':'Source immutable baseline, exact adapter input and all referring callers, readable source bindings, no active writer, no collision/overwrite/link, explicit Human approval'})
assert len(plans)==17 and len({x['name'] for x in plans})==17
save('MIGRATION_BATCH_PLAN.json',{'rows':plans,'first_conditional_candidates':[A.source.name],'unconditional_full_reproduction_qualified_candidates':[],'actual_migrations':0,'R1_full_inventory_repeated':False,'capacity_release_claim':0,'no_cleanup_or_cache_deletion':True})
incident={'prepare_01':'Task script used source rather than path receipt key after copying; preserved first log, source stayed pinned, resumed by rehashing all existing shadow files without overwrite','readonly_01':'Byte container check assumed BLENDER prefix for all .blend; three source containers use Zstandard prefix. All SHA had passed. Corrected checker to distinguish byte access from compressed-native parse, no asset edit','registry_refinement':'Restricted optional native checks to actual declared package roots (initial two SciPy paths were unrelated cp313). Kept v1 registry/excluded-path receipt; current v2 uses actual _deps resources','report_log_closure':'v1 runs02/03 passed scoped checks with one unresolved bare log filename; final v2 adds unique immutable-manifest basename lookup, runs04/05 close all23 concrete refs','source_or_shadow_original_content_changed':False,'automatic_approval_rejections':[],'root_compatibility_links_created':[]}
save('AUDIT_IMPLEMENTATION_INCIDENTS.json',incident)
final={'task':'PIANO_HANDS_DIRECTORY_SHADOW_MIGRATION_R2','status':'PARTIAL','read_only_core_chain':'PASS','original_command_full_compatibility':'NOT_EXECUTED_NOT_CERTIFIED','native_Blender_and_math_runtime':'UNKNOWN_NOT_EXECUTED','shadow_files':207,'shadow_bytes':base['logical_bytes'],'external_whitelist_files':44,'checks_final_run':23,'readonly_repeat_fingerprint':runs[0]['semantic_fingerprint'],'first_conditional_migration_candidates':[A.source.name],'unconditional_full_reproduction_candidates':[],'source_frozen_code_edits':0,'original_migrations':'0/17','formal_target_created':False,'root_members_unchanged':True,'root_count':19,'root_only_hands_piano':False,'historical_protection_FAIL_preserved':True,'R3_started':False,'other_directory_shadow_tests':0,'stop':'STOP — HUMAN REVIEW','automatic_next_task':False}
save('FINAL_STATUS.json',final)
path_examples=f'''|表达式|旧 R2|正式新位置（仅推导，未创建）|深层影子直接运行的推导|独立入口实际位置|
|---|---|---|---|---|
|`O.parent / "hands"`|`{A.source.parent/'hands'}`|`{A.formal.parent/'hands'}`|`{S.parent/'hands'}`|`{H}`|
|`O.parent / "hands_sequence_fingering_planning_r1/SOURCE_EVENT_BINDINGS.json"`|原根下历史目录|hands 内对应目录（尚不存在）|影子父层下对应目录（不存在）|当前原历史输入，只读SHA；将来须显式更新迁移映射|
'''
md('SHADOW_MIGRATION_BASELINE.md',f'''# 迁移影子 R2：只读基线

2026-10-14，Asia/Shanghai。复用 R1 清单，未重复17目录完整普查。本轮原目录 `{A.source}`，正式拟目标 `{A.formal}` **未创建**。测试位置 `{S}`。

原 R2 **207 文件 / {base['directory_count']} 目录 / {base['logical_bytes']:,} bytes（{base['logical_bytes']/1024**2:.3f} MiB）**，成员和每项 SHA 与 R1 完全一致；全部207复制、复制后及结束 SHA 一致。源/影子完整保留，不自动清理。正式Rig/场景未复制，只登记只读来源。

当前任务快照未观察到其他 active Hands 聊天或R2/R3写入进程；Piano聊天仍active，不停止或改写其文件。Restart Manager 返回29，不能声称完整打开句柄枚举。全部207源在哈希/复制时同时持有 FILE_SHARE_READ-only 句柄；任何冲突写者会使建立基线失败。随后207逐项独占只读打开成功；最终 source identity/size/mtime/成员/SHA均一致。句柄证据是有限时间基线，不替代未来迁移即时检查。

实际外部输入44项，详细角色/源码依据/原保护SHA见 `PATH_ADAPTER_REGISTRY_V2.json`，含正式MIDI与timeline、锁定C01、5个原生场景/冻结资源、Rig接口和4个performance_core JSON、原Action比较、B2/早期前缀/安全姿态输入、CasADi符号文件和现有包资源。每项真实读取并按既有保护表或锁定合同核对SHA。

{path_examples}

`verify_midi.py:4` 将 __file__ 的父层级用作项目根；6/25行读取source绑定/指法，26行写回 SOURCE_MIDI_REVALIDATION.json，因此本轮不执行它。`skin_proxy.py` 同样计算 `ROOT=O.parent/'hands'` 并动态提取历史函数；`rig_model.py` 读B2/参考、`coupled_model.py` 加载符号资源、`batch_verify.py` 打开场景并在调用时改内存姿态，均只读取源码，不导入执行。

实际运行输入和历史复核/准备路径已按源码行号分别登记：23个父层级表达式中9个文件表达式通过独立入口实读；14个目录或未展开项只是静态说明。全模块副作用/动态调用清单见 `LEGACY_SOURCE_SAFETY_AUDIT.json`，动态/native未闭合见 `UNVERIFIED_DYNAMIC_NATIVE_DEPENDENCIES.json`。

证据：PILOT_BASELINE.json、SHADOW_COPY_MANIFEST.json、OPEN_RESOURCE_CENSUS.json、EXCLUSIVE_READ_RESOURCE_PROBES.json、LEGACY_PATH_EXPRESSIONS.json、R1_EVIDENCE_BINDINGS.json。
''')
md('PATH_ADAPTER_DESIGN.md',f'''# 最小独立路径适配入口

原207文件的所有字节保持不变。入口由本审计新增 `readonly_path_adapter.py` 和 `run_readonly_validation.py` 构成，原代码、pathlib 和历史Manifest均不修改；也没有root链接、junction、sys.path劫持或导入钩子来偷偷执行旧代码。

配置以正式 `{H}` 为明确源码根，用旧保护键作为逻辑身份。只有已登记路径才可解析。R2旧绝对路径和未创建的formal路径都映射到同SHA的物理影子；其他历史输入当前仍位于原位置，以原保护SHA只读访问。未来若其他目录获批迁移，必须新增明确的逻辑→物理登记，不依赖“找不到就猜另一个目录”。

这证明 formal 逻辑位置的独立入口可以读取正确资源；**不是原程序从新位置原样运行成功**，也不是只替换字符串后就宣称复现。旧 `O.parent/'hands'` 表达式仍会产生hands\\hands；独立入口绕开该上下文假设，并按历史调用证据读取实际源文件。

报告里的裸日志名先按R2内部相对文件匹配；未登记时仅允许从完整不可变复制Manifest中找到唯一同名文件，实际得到 `logs/candidate_front_bridge_execution.log`。多重匹配或未登记一律失败，不做文件系统通配fallback。

只读运行开始前对251个输入持有拒绝写/删除共享的读句柄。Python audit hook将读操作限定为精确登记文件，只允许写两份本次run结果；阻止额外读取、源/影子/formal写入、历史代码exec、进程启动、删除、rename和root链接等。六项阻断探测使用无副作用哨兵/打开请求，均在实际写或历史代码执行前被拒绝；没有真的运行删除/求解/渲染脚本。审计钩子不是任意native代码的全局沙箱，因此本轮根本不加载这些native库。

运行入口：`python -B -X utf8 "{O/'run_readonly_validation.py'}" readonly_06`。必须使用新的readonly_NN名，已有run会拒绝覆盖。已实际执行最终readonly_04和readonly_05，两次结果一致。历史文件仅读取，不import；MIDI由新增纯标准库读器解析，NPZ仅ZIP/CRC/NPY数字容器检查，无pickle或数学库加载。

可复用的是登记/精确SHA/逻辑映射/安全读机制。R2-specific复核断言和危险原命令不是通用验证器；其他16目录需自己的增量读白名单及源语义检查。cleanup必须另建只读账本入口，不执行execution_r1.py。
''')
mt='\n'.join(f"|{x['item']}|{x['result']}|{x['evidence']}|" for x in matrix)
ct='\n'.join(f"|{x['name']}|PASS|{x['scope']}|" for x in runs[0]['checks'])
md('SHADOW_VALIDATION_RESULTS.md',f'''# 影子验证结果

**总体 PARTIAL。只读核心链PASS；未授予完整原脚本/Blender/求解复现PASS。**

最终readonly_04/05各23项检查、251资源实际读取、0历史程序执行，结果指纹均为 `{runs[0]['semantic_fingerprint']}`。实际运行日志与逐文件读取凭据在READONLY_04.log、READONLY_05.log和runs对应OPERATIONS.json；所有结果文件均可重复核对。

|验收项|结果|实际证据与边界|
|---|---|---|
{mt}

已真实执行：原MIDI字节解析及PPQ/tempo/23音46事件逐记录一致；原timeline绑定与C01指法身份；5个源资源SHA和容器前缀；完整皮肤NPZ的CRC/数字头以及88键几何JSON来源一致；13个已记录琴键Action哈希/FCurve记录一致；103个实际皮肤证据CRC与形状；103条历史结果/86失败及未保存源标志；原脚本/7报告交付SHA；86259保护表语义及618并发新增的global FAIL保留；23个报告明确文件引用实际访问。追加上下文检查还核对了start/common/prefix/safe与原输入记录完全一致。

**5个Blend只核对字节，不打开/重算场景。** 2个有BLENDER前缀，3个有Zstandard帧前缀；压缩内容未解码。13个Action检查基于既有受保护记录，不是从当前Blender重新提取。NPZ容器通过也不等于重新计算碰撞。当前历史轨迹仍103样本86失败、连续桥接资格false，迁移路径审计不改变任何运动结论。

23个 O.parent 路径表达式中9个文件表达式有适配实读证据，14个目录/未展开项只是静态说明。矩阵中的PASS仅限所写的读取/记录边界。动态exec、CWD/CLI、native ABI、原生linked资源与其他16目录入口仍未验证，详见U01–U07。

|执行检查|结果|范围|
|---|---|---|
{ct}

首次只读run01因审查器错误地假设所有Blend为非压缩头而停止，原保护SHA始终一致；没有修改源文件。v1 run02/03通过22项但一个裸日志名未闭合；增加独立Manifest定位后v2 run04/05通过23项。原运行日志、版本副本和全部失败/较早结果保留，不把实施错误包装成原资产变化。详见AUDIT_IMPLEMENTATION_INCIDENTS.json。
''')
pt='\n'.join(f"|{x['batch']}|{x['name']}|{x['R1_files']}|{x['R1_MiB']:.3f}|{x['R1_incoming_source_refs']}|{x['risk']}|{'R2只读条件候选' if x['batch']=='B1_PILOT' else '尚未试点'}|" for x in plans)
md('MIGRATION_BATCH_PLAN.md',f'''# 17目录后续分批迁移建议

**计划而非迁移授权；实际0/17。** 复用R1文件数/容量/引用统计，没有重新完整盘点。唯一新增测试副本是R2，其他16项没有影子执行证据。新任务/外部打开句柄与native资源状态必须在各批前重新检查。

第一批形成 **1项条件候选：hands_long_context_corridor_ik_bridge_r2**。条件是Human接受“历史字节保持＋独立只读复核入口”这一迁移验收边界，并审查PARTIAL范围；若要求全部原命令和完整Blender/求解原样复现，当前合格名单为 **0项**。此候选尚未获真实迁移批准。

|批次|目录|R1文件数|逻辑MiB|外部源码引用文件数|风险|资格|
|---|---|---:|---:|---:|---|---|
{pt}

每个源→目标的完整绝对路径及单项目门禁保存在MIGRATION_BATCH_PLAN.json；目标均为hands内部同名目录，不允许root兼容链接或覆盖。B2先从引用较少的近期证据目录增加只读白名单，保持时间耦合局部资格和历史FAIL。B3含C01源指法及共享几何/原生hub，必须同时检查调用方，不能只因文件少就盲搬。B4包含软件包、serialized函数、ONNX及大型恢复记录，需证明包内相对资源/DLL/ABI/来源链，而不运行模型或优化。批次只是优先顺序，可以因未闭合门禁暂缓，不为减少root目录强制跨批移动。

**cleanup为独立高风险项。** 原34文件的锁定Manifest和批准/SUCCESS账本必须保留，原脚本硬编码旧O。先新增只读复核入口，逐项核对锁定Manifest SHA、账本与原库存的关联、已批准精确缺失例外；不运行任何prepare/execute/verify历史程序阶段，不修改账本或旧保护表。本轮只提出这个门禁，尚未测试该入口，因此不列第一批。

各批真实执行前：原源文件稳定基线与写者检查、目标不存在且解析边界合法、所有被读源和调用方的登记路径与原SHA闭合、未知native/dynamic项显式保留、Human批准精确路径范围。批准后才允许使用Windows单一shell/精确LiteralPath移动，迁前后成员/SHA/必要引用检查和路径事件分开记账；失败停止，不删缓存、不清理副本、不抹历史FAIL，不把同盘移动计作磁盘释放。

已证明的机制可以复用于登记读取，**不能依据一项R2影子证明其他16目录安全迁移**。没有发现可据本轮证据永久判为“绝对无法迁移”的目录，但原命令直接兼容未成立，高风险项与源码/执行行为变更需Human另行授权。
''')
md('PROTECTION_AND_ROOT_AUDIT.md',f'''# 内容保护与根目录审计

源R2原207文件的成员、SHA、size/mtime/文件身份全部保持；影子207成员和SHA保持，未新增字节码或修改冻结源码。44个登记外部输入与既有合同/保护SHA一致，包括5个原生源容器、正式MIDI和指法绑定。R1复用的11份证据/规则SHA不变；3份历史保护状态原文件与R1记录SHA一致。详细逐项证据见PROTECTION_FINAL_RESULTS.json。

历史85850 global FAIL（3并发变化/15新增）、86148 PASS、R2 86259 global FAIL（618并发新路径）原样保留。86259 before/after保护表的原绝对路径语义不改写。当前不重新全量re-hash这些路径，也不宣布并发Piano全目录global PASS；本轮读取/写入足迹与历史全局状态分开。

root开始与结束成员集合完全相同：19项（hands、piano、17个历史hands_*）。added=[]、removed=[]，未观察一级并发变化，无需回滚或归因任何root变化。Piano聊天active，但其内部状态不在本轮全量复验范围；未向它发送消息/停止任务，也未修改其目录或任何原资产。

正式迁移目标 `{A.formal}` 不存在；本轮所有新增文件和测试副本在 `{O}`。根目录未创建文件、文件夹、符号链接或junction。影子副本保留，不自动清理。R3正确/错误目标均未创建，运动研发运行数0。

六项安全阻断探测在真正操作前拒绝：未登记读、formal写、源R2写、影子源写、历史路径exec哨兵、root链接。不是实际删除/重写源资产测试。复制/适配器窗口的只读pin和终检保护既有字节；快照/逐项probe不是迁移时的永久锁或完整句柄枚举。

**实际迁移0/17，root尚未只剩hands+piano，整理未完成。**
''')
md('FINAL_HUMAN_REVIEW.md',f'''# 最终Human审查：PARTIAL

2026-10-14，Asia/Shanghai。**只读核心路径与历史复核链通过，整体状态PARTIAL；实际迁移0/17。**

207文件影子完整性通过，251资源实读/原SHA一致，其中44外部输入；最终两次23项检查指纹相同。所有原源码、冻结合同、历史FAIL和原R2目录保持不变。正式目标没有创建，root与开始相同19成员，尚未完成目录整理。

**A. R2在新位置能解析核心依赖吗？** 独立入口把formal逻辑路径映射到影子后可以，已真实只读访问正式hands、MIDI、C01、Rig/场景资源、既有数学和历史数据。原O.parent推导若原样运行仍会产生hands\\hands或错误sibling路径，不能直接兼容。

**B. 哪些历史复核已真实通过？** MIDI的23音46事件与tempo/tick身份；C01及timeline绑定；原B2/start/common/早期prefix/safe数据来源；5容器受保护SHA；88键几何来源；13已有Action哈希/FCurve记录；103皮肤证据CRC和103记录/86失败；7报告/源码交付SHA；23报告明确文件引用；旧保护表语义与global FAIL保留。都是只读记录/字节检查，未重算运动。

**C. 哪些只有静态或没有执行证据？** 14个未展开目录表达式、动态exec/import/CLI/CWD、完整native库加载及ABI、Blender场景/linked资源/驱动/handler、原求解命令、其他16个目录与cleanup锁定账本入口。5个Blend的字节读取不是native加载，Action记录匹配不是新提取。

**D. 能不修改冻结源码完成迁移吗？** 已证明保留字节并使用独立只读入口可复核核心资料，不需要改原源码。若Human接受这种历史快照边界，R2可列条件迁移候选；完整原运行命令仍未证明，不能承诺全部流程迁后原样运行。

**E. 可复用到其他16目录吗？** 明确root/逻辑物理映射/精确白名单/SHA/失败闭锁机制是配置驱动，可复用。R2两次实际入口执行支持这一机制；各目录的读断言、动态/native/调用方闭合未验证，不能把它推广成16项PASS。

**F. 有不能安全迁移或需另行授权的项吗？** 现阶段直接原命令搬入不安全，native/package/hub/cleanup账本为高风险。没有证明任何目录永久不可迁移。需要原命令执行、修改历史源码/冻结合同、native验证或任何真实移动时均须Human另行批准，不能本轮扩权解决。

**G. 形成第一批名单了吗？** 1项条件候选：`hands_long_context_corridor_ik_bridge_r2`，限定独立只读历史复核入口；没有无条件完整复现合格项。其余16按5批计划排序，全部待增量检查与审批。

**H. root是否保持开始集合？** 是，19成员完全相同，无新增/移除或一级并发变化，没有回滚其他任务。历史17目录仍在root，正式迁移0/17。

请独立审查 [验证结果](SHADOW_VALIDATION_RESULTS.md)、[适配设计](PATH_ADAPTER_DESIGN.md) 和 [17目录批次](MIGRATION_BATCH_PLAN.md)。源到影子逐文件清单、SHA、真实日志、动态/native缺口和保护终检均已附机器证据。

**STOP — HUMAN REVIEW。等待ChatGPT独立审核和Human批准；不自动迁移、清理影子、启动R3或其他研发。**
''')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and not p.is_relative_to(S) and p.name not in ['DELIVERY_MANIFEST.json','FINALIZE_RUN.log']:
  manifest.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
save('DELIVERY_MANIFEST.json',{'audit_artifacts':manifest,'shadow_copy_manifest':'SHADOW_COPY_MANIFEST.json','shadow_files':207,'source_and_shadow_SHA_all_same':True,'self_excluded':True,'finalize_stdout_log_excluded_while_running':True,'status':'PARTIAL','actual_migrations':'0/17','stop':'STOP — HUMAN REVIEW'})
print('PARTIAL; read-only chain PASS; source/shadow207 and external44 SHA unchanged; 0/17 migrations; root unchanged19; STOP — HUMAN REVIEW',flush=True)
