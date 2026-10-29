import json,hashlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
O=Path(__file__).resolve().parent
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def doc(n,s):(O/n).write_text(s.rstrip()+'\n',encoding='utf8')
v=read('OUTPUT_VALIDATION_AND_FEASIBILITY.json');rt=read('INFERENCE_RUNTIME_RECEIPT.json');b=read('SOURCE_EVENT_BINDINGS.json');p=read('evidence/MODEL_PROVENANCE.json');npm=read('NPM_PACKAGE_METADATA.json')
rows=sorted(v['rows'],key=lambda n:(n['hand']!='R',n['note_id']))
risks={
'R00':'与G4构成7半音下行；原指法不变，需释放及手位协调。',
'R01':'5→1下行衔接；未见事件冲突，动态触键仍待复核。',
'R02':'1→2上行；未见事件冲突。',
'R03':'2→3上行；未见事件冲突。',
'R04':'3→4上行；未见事件冲突。',
'R05':'4→5后转向低G4；下一音改用2指，需更积极手位移动。',
'R06':'5→2下行7半音、接G4换指2→1；需手位与重复触键复核。',
'R07':'G4重复换指2→1；随后向E5跃进9半音，需手位移动。',
'R08':'G4→E5上行9半音；两音不重叠，不宜假定固定掌位可达。',
'R09':'B02起点改2指；此前5→2下行，后续2→3顺序上行。',
'R10':'D5(3)→E5(4)顺序上行；旧4→3局部逆序消失。',
'R11':'重点风险：E5(4)→F♯5(2)上行全音却从4回到2，需换位。',
'R12':'承接4→2逆序换位；黑键F♯5触键深度及手掌横移未验证。',
'R13':'2→3上行半音后G5(3)→G4(1)下行八度；需整手换位。',
'R14':'承接八度下行3→1；接G4换指1→2，需释放/重按。',
'R15':'G4重复换指1→2；无事件重叠，未证明键复位或教学必要性。',
'L00':'和弦低G3用5指；与3/1不同指，7半音总跨度无明显事件冲突。',
'L01':'和弦中B3用3指；三指各异，未见事件冲突。',
'L02':'和弦高D4用1指；同持857.142ms，后转A3(4)需整手协调。',
'L03':'左手A3(4)→B3(3)自然方向；未见事件冲突。',
'L04':'B3(3)→C4(2)自然方向；未见事件冲突。',
'L05':'C4(2)→B3(3)自然方向；未见事件冲突。',
'L06':'与前音相接、无同手重叠；未见事件冲突。'}
table='| 音符ID | 左/右手 | 音名 | MIDI | 原指法 | AI预测指法 | 是否变化 | 风险判断 |\n|---|---|---|---|---|---|---|---|\n'
table+='\n'.join(f"| {r['note_id']} | {'右' if r['hand']=='R' else '左'} | {r['note_name'].replace('F#','F♯')} | {r['midi']} | {r['old_finger']} | {r['ai_finger']} | {'是' if r['changed'] else '否'} | {risks[r['note_id']]} |" for r in rows)
changed='、'.join(f"{r['note_id']} {r['old_finger']}→{r['ai_finger']}" for r in rows if r['changed'])
doc('ALL_23_FINGERING_COMPARISON.md',f'''# 23音逐音对照 — R1

综合结论：INFERENCE_PARTIAL。模型执行、输出结构与源事件一致性均PASS；B02存在明显非拇指逆序换位风险，基本动作可行性尚未通过。此处的PARTIAL不是模型运行失败，也不是已经证明该指序绝对不可弹。全部预测为DESIGN_PROVISIONAL。

旧指法只从正式时间轴读取并用于推理后的对照。实际输入文件MODEL_INPUT_UNCONSTRAINED.json没有finger字段；逐次ONNX输入的26个finger_hint均为-1。仅执行一次predictFingerings，内部左7次、右16次ONNX调用，没有筛选或人工改指。

{table}

右手变化7/16：{changed}。左手0/7变化；总计7/23变化、16/23相同。相同不构成钢琴教师认证。

## 输入与输出一致性

SOURCE_EVENT_BINDINGS.json绑定现有PERFORMANCE_TIMELINE.json和真实anna-magdalena-04.mid。R00—R15、L00—L06逐音匹配源track、channel、pitch、velocity、on/off tick、消息序号和释放类型；范围为起点tick<4608的23个音及其对应46条消息。tick4608的下一小节NOTE_ON不纳入。源的NOTE_ON velocity=0按释放语义处理，没有把其误认作新的按键音。

模型时间严格使用source_on_sec×1000；时长使用(source_off_sec−source_on_sec)×1000。0.35秒展示lead没有进入输入；保留原JSON浮点值，不额外量化。音乐源时长5.142852秒。返回数组按time/pitch重排是官方API行为，通过完整五字段(left/note/time/duration/velocity)一对一绑定ID，未把新排序当作丢失身份，也未向直接返回数组追加ID。所有23个音的这五项属性精确一致。

## 基本可行性检查

- 同手同时按下：仅左手G3/B3/D4三音和弦，指序5/3/1，三个不同手指。总跨度7半音；G3→B3跨4半音、B3→D4跨3半音，未见明显反向指序。
- 同指重叠不同琴键：0对。用源tick的半开区间[on,off)计算；所有同手正时长重叠为左和弦的3对，手指均不同。右手没有正时长重叠。不同手同指编号不构成冲突。
- 连续上行：B02的D5(3)→E5(4)顺序较直接；但E5(4)→F♯5(2)音高上行全音、指序反向，不能固定手位直接映射。它需要额外抬指/横移或其他教师认可的换位策略。
- 大跨度：R00→R01下行7半音5→1；R05→R06下行7半音5→2；R07→R08上行9半音1→5；R13→R14下行12半音3→1。后两处尤其需要整手移动。它们均不要求同时持住两键，不能把旋律距离直接当成静态手掌跨度，也不能由无重叠推定动画可达。
- 重复G4：R06→R07预测2→1，R14→R15预测1→2；两对间隔均约428.571ms，前OFF与后ON在同tick。模型选择了换指，没有输入层冲突；仍需先释放、琴键复位、再触键。MIDI没有定义键的物理复位轨迹。换指是候选选择，不能断言本曲必须换指。
- 黑白键协调：唯一右手黑键R12 F♯5用2指，随后G5用3指。黑键2指本身不是明显错误；风险来自此前E5用4指并向右转2指，以及指尖深度与掌位的配合。

没有对模型做修正，也没有新增动作。以上是发现明显冲突和换位需求的工程检查，不是教师认证或3D动作可执行性证明。结构检查、完整转换、logits和CPU运行证据见OUTPUT_VALIDATION_AND_FEASIBILITY.json、RAW_ONNX_LOGITS_AND_TOKENS.json及profile文件。
''')
b02=[r for r in rows if r['note_id'] in [f'R{i:02}' for i in range(9,14)]]
btable='| ID | 音名 | ON tick | OFF tick | 源ON秒 | 源OFF秒 | 旧指 | AI指 |\n|---|---|---|---|---|---|---|---|\n'+'\n'.join(f"| {r['note_id']} | {r['note_name'].replace('F#','F♯')} | {r['on_tick']} | {r['off_tick']} | {r['source_on_sec']:.7f} | {r['source_off_sec']:.7f} | {r['old_finger']} | {r['ai_finger']} |" for r in b02)
doc('B02_FINGERING_ANALYSIS.md',f'''# B02指法分析 — R1

真实无固定指法输出：C5(2)→D5(3)→E5(4)→F♯5(2)→G5(3)，即2–3–4–2–3。旧序列为3–4–3–4–5。五音全部改变；原始返回值保持不动。

{btable}

## D5→E5交接

R10 D5结束、R11 E5开始均在tick3072，源时间3.428568秒（展示时间加0.35才是3.778568秒）。无正时长重叠、无额外休止。模型将旧无名指D5(4)→中指E5(3)改为中指D5(3)→无名指E5(4)。音高和手指顺序同向，从事件层面消除了原交接处4→3的非拇指逆序。因此，这个局部交接是值得教师进一步验证的新候选。

这是指序层面的推论，没有新动画、皮肤穿透验证或教师结论。不能声称已解决原B02中指/无名指交叉；不能由改变手指就推出原冻结Rig必然可达。

## 风险移到E5→F♯5

R11 E5用4指，R12 F♯5用2指；tick3264、源时间3.6428535秒处相接。两次起音相距约214.2855ms，释放到下一按键的空白间隔为0。音高上行2半音（全音），却从无名指回到食指，构成明显非拇指逆序换位风险。若保持原掌位，不能把这一序列当作自然五指顺序上行。可能需要提前释放、手掌向右横移、抬指及黑键纵深调整；本模型仅给出finger，未给出如何完成这些动作。

没有同指同时占据不同键，也没有证明它生理上绝对不可演奏；它的风险属于动作策略未定义及教学自然度存疑。不能把D5→E5改善局部描述成整个五音问题解决，更不能自动改成1–2–3–4–5来获得PASS。

F♯5(2)→G5(3)在音高及指序方向上相符，但建立在前一步重新布置手位成功的前提上。后续G5(3)→G4(1)是下行八度，也需要整手移动；旧G5(5)→G4(1)与新序列不是同一个手位需求。

## 判断

B02产生了独立的新候选，D5→E5局部更值得验证；整个2–3–4–2–3没有足够依据被判定优于旧序列或可直接用于教学。综合为INFERENCE_PARTIAL，运行与身份检查PASS、指法质量待审。全部为DESIGN_PROVISIONAL。保留唯一原始输出，STOP — HUMAN REVIEW。
''')
rev=p['release_git_revision'];started=datetime.fromisoformat(rt['started_utc'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).isoformat()
weights='| 手 | 文件 | 字节 | SHA256 |\n|---|---|---|---|\n'+'\n'.join(f"| {w['hand']} | {Path(w['file']).name} | {w['bytes']} | `{w['sha256']}` |" for w in p['weights'])
doc('MODEL_RUNTIME_AND_LICENSE.md',f'''# 真实运行、模型身份与授权 — R1

采集及执行日期：2026-10-11，Asia/Shanghai。唯一正式推理起始：{started}。

## 发布身份

实查npm latest为@lumikey/piano-fingering-model **0.3.0**，发布时间2026-01-28T22:33:13.962Z。发布gitHead：`{rev}`，对应2026-01-28提交Bump version to 0.3.0。npm发布记录列出0.1.0和0.3.0，不将未发布版本当作已安装版本。完整元数据、tarball integrity、npm provenance原始记录（未作签名验证）与依赖锁文件保存在NPM_PACKAGE_METADATA.json、evidence/NPM_ATTESTATIONS.json、package-lock.json。没有重新训练或重新导出权重。

来源：[npm注册表](https://registry.npmjs.org/@lumikey%2fpiano-fingering-model)、[固定发布版本package.json](https://github.com/lumikey/piano-fingering-model/blob/{rev}/js/package.json)、[官方Node说明](https://github.com/lumikey/piano-fingering-model/blob/{rev}/js/README.md)。

{weights}

两文件均来自安装包models目录，与发布gitHead中的js/models同名ONNX文件逐字节一致。核对过程及完整证据保存于collect_provenance.py和evidence/MODEL_PROVENANCE.json。仓库另有左右手.pt文件，但本轮不需要下载或运行PyTorch权重。export_onnx.py描述的来源为各手FingeringTransformer checkpoint，tokens输入[1,26,5]、logits输出5项、opset17；本次CPU会话实际输入输出名称均为tokens/logits。权重训练细节与质量不能由文件哈希推出。

## 环境与执行

| 项目 | 实测值 |
|---|---|
| 系统 | {rt['os']} / {rt['platform']} / {rt['arch']} |
| CPU | {rt['cpu']}，{rt['logical_cpu_count']}逻辑CPU |
| Node | {rt['node']} |
| npm | 11.16.0 |
| ONNX运行时 | onnxruntime-node 1.23.2；onnxruntime-common 1.23.2 |
| MIDI适配 | 已有Python 3.12.1 + 现有只读mido 1.3.3；不是Python模型推理 |
| 模型加载耗时 | {rt['model_load_ms']:.4f} ms，左右会话合计墙钟 |
| 正式predictFingerings耗时 | {rt['predict_ms']:.4f} ms，23音，含token构建/顺序ONNX调用/logits记录 |
| 加载+预测 | {rt['model_load_ms']+rt['predict_ms']:.4f} ms；不包含安装、导入、文件输出和后续审查 |
| 次数 | predictFingerings 1次，内部左7/右16，共23次session.run；未做重复候选或择优 |
| 运行异常 | exception=null；清理无异常；全部logits有限、argmax与1—5返回一致 |
| 加速器 | 仅CPUExecutionProvider；未安装PyTorch/CUDA |

infer_once.mjs先导入onnxruntime-node注册backend，再使用官方loadModels()与predictFingerings(notes, models)。loadModels()没有会话选项参数，因此脚本临时给其共享InferenceSession.create工厂补充executionProviders=['cpu']和profiling选项，加载后立即还原工厂。未编辑包源码、tokens算法或权重。session.run外包装仅记录输入、logits及耗时，原返回值不改。RAW_MODEL_PREDICTIONS.json直接保存官方返回数组，无人工指法或追加ID；身份在单独检查文件中绑定。

两份ONNX profile均实际出现且只出现CPUExecutionProvider。INFERENCE_RUNTIME_RECEIPT.json记录真实时间；OUTPUT_VALIDATION_AND_FEASIBILITY.json记录profile文件名/哈希，RAW_ONNX_LOGITS_AND_TOKENS.json保留逐音直接logits和输入tokens。profiling开启使这里的146ms不能被当作关闭诊断后的稳态性能基准。

安装注意：npm包包含多平台本地二进制，初次下载约8分钟；INSTALL.log保留全记录。npm自动选择了公共接口1.30.0而运行时依赖1.23.2，正式推理前主动将公共接口固定为1.23.2，使官方包与Node backend共用同一工厂；对齐约34秒，期间npm请求曾报ETIMEDOUT，但最终成功。随后离线缓存核查426ms，无新增下载。未经历失败的正式模型调用。boolean依赖弃用警告保留；npm默认没有执行待批准的onnxruntime-node postinstall，Windows CPU二进制已随包提供且实测可运行，无需额外授权脚本或CUDA下载。

复现需在本隔离目录使用锁文件，执行adapt_source.py后再执行infer_once.mjs。推理脚本使用wx保存结果并检测已有RAW_MODEL_PREDICTIONS.json，阻止意外覆盖或重复正式候选；请勿在当前交付上再次运行。所有新增文件仅写在实验目录，现有Hands/Piano工作区、静态姿态、MIDI/音频、Action及候选动画未修改。

## 代码、权重、训练数据商业授权

| 对象 | 已核实证据 | 商业教材状态 |
|---|---|---|
| Lumikey npm/JS代码 | npm元数据及js/package.json声明MIT。但安装包、固定发布仓库树和当前main树均未发现LICENSE/COPYING/NOTICE或许可证正文；GitHub仓库license字段为null | 记录为MIT声明；完整授权证据仍不足。不能给整个仓库、训练代码或商业教材组件作已清权结论 |
| 左右ONNX与.pt权重 | 公开可下载，ONNX包含在npm包中；未发现单独权重许可证、model card或明确商业权重授权。没有证明MIT声明究竟覆盖全部权重/上游权利 | NOT_CLEARED；本轮实测不等于正式商业教材授权 |
| 训练数据来源 | 固定版本train.py把基础数据称Flowkey，并可拼接PIG及scale npz；公开仓库包含这些文件。未提供发布权重实际训练清单或完整来源/授权链 | NOT_CLEARED；不推断上游网站、PIG或生成音阶数据可用于商业权重/教材 |
| ONNX Runtime | 安装包元数据及微软源码声明MIT；本轮未审核全部运行时第三方授权。它是运行环境，不能替代Lumikey权重授权 | 可与模型权重权利分别评估；不能据此替权重清权 |

许可证检索为完整非截断发布树及当前main树，相关路径均为空；它证明本次公开发布未提供这些文件，不能证明作者永远未授予其他授权。源码依据：[训练入口](https://github.com/lumikey/piano-fingering-model/blob/{rev}/python/train.py)、[权重导出入口](https://github.com/lumikey/piano-fingering-model/blob/{rev}/python/export_onnx.py)。完整原始证据在evidence目录。正式商用前需要权利人明确确认代码/权重范围与训练数据链，并保存可追溯授权。本轮结论为隔离技术POC，不将该模型作为已获商业许可的教学组件。
''')
doc('FINAL_RECOMMENDATION.md',f'''# 最终建议 — 自动钢琴指法实测 R1

**INFERENCE_PARTIAL**。真实预训练CPU推理成功；23音身份、46消息、时间和输出结构全部PASS。由于B02的E5(4)→F♯5(2)有明显非拇指逆序换位风险，不能将结果视作已具备基本动作可行性或教学认可。没有判定它绝对不可弹；风险没有通过动作策略或教师审阅解决。全部预测仍为DESIGN_PROVISIONAL。

| 必答问题 | 实测结论 |
|---|---|
| 预训练模型是否真正运行成功？ | 是。0.3.0发布ONNX在CPU实际运行，两份profile证明CPUExecutionProvider，全部23音有真实logits和1—5输出。 |
| 是否无需重新训练便能预测23音？ | 是。没有训练、重导出或固定指法约束。16右/7左全部预测，约{rt['predict_ms']:.3f}ms；加载约{rt['model_load_ms']:.3f}ms。 |
| 哪些指法与旧版不同？ | {changed}；左手全部相同。完整23行见ALL_23_FINGERING_COMPARISON.md。 |
| B02是否产生更值得验证的候选？ | 产生2–3–4–2–3。D5→E5的3→4比旧4→3在局部顺序上更直接，值得验证；E5→F♯5的新4→2将风险转移到下一交接，整段尚不能认定更优。 |
| 左手和弦有没有明显冲突？ | G3/B3/D4仍为5/3/1，三指各异，7半音总跨度；未见同指同手同时多键冲突。 |
| 右手重复音有没有明显冲突？ | 两对G4分别2→1和1→2，源OFF/ON同tick，无正时长重叠。没有事件层冲突，但换指必要性、释放及键复位仍需复核。 |
| 模型是否适合不同MIDI曲目？ | 接口支持已分手的21—108音域MIDI序列，轻量CPU部署可扩展。只测了这一首四小节，跨曲目正确率、和弦密度、重叠持音及速度鲁棒性未实测；不支持据此宣称广泛教学适用，更不承担自动分手。 |
| 是否值得接入下一阶段3D Hands动作规划？ | 值得作为研究用途候选生成器保留；先对唯一候选作教师审阅并确认授权。当前不建议将未经筛查的finger直接驱动正式3D Hands，不能直接接入商业教材。后续验证必须另行授权。 |

技术接入成本较低：秒转毫秒、已有分手、两份约501KB ONNX、固定Node依赖即可运行。质量限制来自逐音贪心argmax和有限上下文：每音使用每指上次状态及最多20个后续音，没有显式和弦手指唯一约束、全局生物力学求解或整手轨迹。源码将仍持键与刚释放的负/零时间信息压到同一零边界，并不保证重叠可行性。其他曲目仍需要独立的冲突检测与人工复核。四小节末端缺少后续乐句上下文，本次结果不应外推为完整曲目的最优指法。

本轮输出保留原样，没有为PASS改指。7音变化不是正确率；与旧版相同的16音也不是专业认证。没有覆盖旧指法、修改冻结资产或生成动画。代码声明MIT但缺少正文，权重及训练来源商业权利未明确，详见MODEL_RUNTIME_AND_LICENSE.md。

## 交付与证据

1. SOURCE_EVENT_BINDINGS.json：原23音身份、真实MIDI on/off消息、正式时间轴原条目与无约束输入对应。
2. RAW_MODEL_PREDICTIONS.json：唯一正式调用的直接返回数组。
3. ALL_23_FINGERING_COMPARISON.md：全部23行及重叠/和弦/重复音/跨度/黑白键检查。
4. B02_FINGERING_ANALYSIS.md：D5→E5与新E5→F♯5风险。
5. MODEL_RUNTIME_AND_LICENSE.md：发布身份、权重SHA256、运行环境、实测耗时和授权边界。
6. FINAL_RECOMMENDATION.md：本报告。

额外证据包括MODEL_INPUT_UNCONSTRAINED.json、RAW_ONNX_LOGITS_AND_TOKENS.json、INFERENCE_RUNTIME_RECEIPT.json、OUTPUT_VALIDATION_AND_FEASIBILITY.json、两份CPU profile、锁文件、安装/执行日志及evidence快照。源MIDI及时间轴前后SHA256一致。没有重新审计历史几何或动作资产。

**STOP — HUMAN REVIEW。** 本轮完成后停止，不进入动画生成、动作重定向、B01/B02/B03求解或新候选制作。
''')
status=dict(task='PIANO_AUTOMATIC_FINGERING_INFERENCE_POC_R1',overall_status='INFERENCE_PARTIAL',execution_status='PASS',output_identity_status='PASS',fingering_quality='DESIGN_PROVISIONAL',reason='B02 E5(4) to F#5(2) non-thumb ascending direction reversal requires unvalidated repositioning; not proven impossible',commercial_status='NOT_CLEARED',official_predict_calls=1,changed_ids=v['changed_ids'],same_finger_overlap_conflicts=0,stop='STOP — HUMAN REVIEW')
(O/'FINAL_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(status,ensure_ascii=False))

