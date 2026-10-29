import json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def doc(n,s):(O/n).write_text(s.rstrip()+'\n',encoding='utf8')
b=read('SOURCE_EVENT_BINDINGS.json');cs=read('SEQUENCE_CANDIDATES.json');c=cs['candidates'][0];p=read('PIANOPLAYER_RAW_OUTPUT.json');s=read('CONDITIONAL_MODEL_PATH_SCORES.json');risk=read('WHOLE_SEQUENCE_COST_AND_RISK.json');paths={r['path_name']:r for r in risk['paths']};fingers={r['path_name']:r['fingers'] for r in s['paths']}
rev=read('evidence/pianoplayer_tree.json')['sha'];rr=read('evidence/ramoneda_tree.json')['sha'];archive=O/'evidence/nakamura_source.zip';archsha=hashlib.sha256(archive.read_bytes()).hexdigest()
doc('EXISTING_ALGORITHM_REVIEW.md',f'''# 可复用序列指法算法调查 — R1

调查日期2026-10-11，最多三条路线。实际选用PianoPlayer，核心无需新增依赖、无需训练，已对真实23音运行。没有把论文宣称直接当成可执行实现，也没有下载PIG/ThumbSet或大型数据集。

| 路线 | 真实实现、版本及授权 | 权重/训练需求 | MIDI、双手、和弦和重复音 | 序列约束及Lumikey结合成本 | 本轮决定 |
|---|---|---|---|---|---|
| Nakamura/Saito/Yoshii HMM / 高阶Viterbi / chord HMM | 作者页提供SourceCode_v190921.zip，126511字节，SHA256 `{archsha}`；含一至三阶及chord HMM的C++ Viterbi实现和运行入口。压缩包未发现明确LICENSE或授权正文，不能当作商业已授权开源 | param_FHMM1/2/3.txt及param_CHMM1.txt均真实存在，README说明默认使用已训练参数；运行不需训练 | 运行入口接PIG fingering文本，需MIDI身份/时间适配；分别处理双手，chord HMM有和弦聚类。重复音属于概率转移，不保证反复触键轨迹或同指持音占用 | 高阶状态转移及回溯能解有限HMM序列，统计模型不是腕部物理模型。其转移/发射参数不是Lumikey的每指历史状态，不能直接替换为上一轮固定logits；如融合需新适配decoder | 有真实完整源码和参数。当前PATH未发现g++/clang++/cl，不为本实验安装工具链；未执行该模型，未虚构预测 |
| PianoPlayer | 固定git `{rev}`，pyproject版本3.0.2；LICENSE正文MIT，Copyright 2017 Marco Musy；核心hand.py/models.py实际可导入 | 完整规则与演奏成本算法，不使用预训练权重，也不需训练 | 提供MIDI/MusicXML/PIG读入；核心接受已分手INote。和弦有唯一手指、顺序及跨度规则；重复同音可以使用同指。本轮直接用正式已分手23音，不用自动routing | 每次至多9音的深度优先组合前瞻、保留部分前次结果；不是Beam、DP或全曲最短路径。成本结合每指位置/强度、起音时间、黑键偏好及换位。可先生成候选，再由Lumikey正确条件复评；原生没有ONNX模型评分接口 | **实际隔离运行**，{p['runtime_seconds']:.3f}秒，一套完整23音候选，无固定指提示。官方默认和弦0.05秒错开在本轮不采用，真实同起时刻不变 |
| Ramoneda等自回归ArLSTM/ArGNN + Beam Search | PRamoneda/Automatic-Piano-Fingering git `{rr}`；LICENSE正文MIT。seq2seq_model.py内decode_with_beam_search真实保留每条路径的LSTM隐藏状态及前指embedding，再扩展并选择beam | 真实models目录有左右ArLSTM各849324字节、ArGNN各2949407字节，不需重新训练原则上可用。没有本轮下载/加载.pth，也不声称已运行 | 源码是PIG/ThumbSet特征与模型实验入口，未确认现成原始MIDI一键接口；左右分模型。GNN图结构表示复音，但未见它在解码时硬保证持音手指唯一。重复音可预测；物理释放仍需另查 | 真正的神经条件序列Beam实现，能输出完整指序，并非并行分类后拼接。PyTorch与图/特征适配成本高于当前已验证ONNX；其隐藏状态不等同Lumikey每指上次状态，不能直接插入Lumikey权重 | 保留为有源码及权重的技术路线；不为这23音安装大型PyTorch环境。训练代码有研究数据依赖，代码MIT不等于权重/训练数据商业清权 |

主来源：[作者HMM页面](https://statpianofingering.github.io/demo.html)、[Statistical Learning and Estimation of Piano Fingering论文](https://arxiv.org/abs/1904.10237)、[PianoPlayer固定源码](https://github.com/marcomusy/pianoplayer/tree/{rev})、[PianoPlayer许可证](https://github.com/marcomusy/pianoplayer/blob/{rev}/LICENSE)、[ArLSTM/ArGNN固定源码](https://github.com/PRamoneda/Automatic-Piano-Fingering/tree/{rr})、[Beam解码器](https://github.com/PRamoneda/Automatic-Piano-Fingering/blob/{rr}/nns/seq2seq_model.py)、[自回归指法论文](https://eita-nakamura.github.io/articles/Ramoneda_PianoFingeringFromPartiallyAnnotatedScores_2022.pdf)。原始仓库树、许可证和相关源码快照在evidence。

## 实际适配边界

本轮使用原始Hand.generate，而非重写搜索器。直接构建INote，fingering=0；保留原起点、时长、音高、ID映射及三音同起关系。坐标使用作者keypos(note-name)，因为作者keypos_midi把半音编号乘白键宽度，包含与真实键布局不符的间距；使用其已有音名函数不修改作者源码或音乐。左右都用固定M手型、默认autodepth和默认关闭posture memory，没有手型或深度调参。

PianoPlayer会硬剪枝部分非拇指逆序，但允许拇指穿指/跨拇指方向。因此不能将其剪枝当作所有钢琴技术的通则；合理非拇指换位可能被漏掉。持音占用也未完整进入其演奏成本，我们对本曲的全部真实on/off独立验证。它提供的是低成本候选路线，不是完整生物力学或商业教学解决方案。

本轮已有现成核心可运行，依用户的优先顺序，不再另外开发Beam Search。Lumikey用于候选生成后的条件模型复评，没有宣称实现神经/演奏成本的联合全局搜索。
''')
doc('SEQUENCE_PLANNING_FEASIBILITY.md',f'''# 条件序列评分与本轮规划可行性 — R1

**能够复用Lumikey 0.3.0现有ONNX权重而无需训练。** 已真实取得每音五个完整logits，对旧指法、原贪心和本轮PianoPlayer候选分别按自身历史计算评分。选择的现成规划器是PianoPlayer有限前瞻搜索；本轮没有另写Beam或冒称最优Viterbi。

## 模型依赖与正确评分

固定源码dist/inference.js维护fingerLastMidi[5]、fingerLastTime[5]。选中某指后，它记录当前音高、把对应时间设为负的音符时长；走到下一音时按实际起音差让五指状态老化。下一音的previous tokens因指序而改变。lookahead最多20音，包含未来音高、时间及可选finger hints。前指历史变了，后音的输入与logits必须重算。

公开predictFingerings/predictHandFingerings只返回选定finger，没有现成的beam、top-k序列或返回完整logits接口。但传入的ONNX session.run会返回logits，能够包装记录。固定finger可以改变状态及未来hint；若把整条待评路径一次性全标fixed，则先前音会看到未来答案，不再是仅给定过去的条件评分。本轮不采用这种做法。

score_paths.mjs使用官方predictFingerings和官方状态更新。每条完整路径使用全新内存notes，最初都没有finger；包装session.run记录并执行真实ONNX，然后只为**当前**音设置该路径的finger。官方接口在await run后读取当前finger，并据此更新每指历史；所有未来音始终未知。输入tokens的26个finger_hint逐个验证均为-1。这里的临时finger是已生成路径的评分复放，不是生成阶段提供的目标答案，也未回写任何源文件。

评分为 `NLL = Σᵢ −log softmax(logitsᵢ(该路径此前选指, 已知音乐未来音, 未知未来指法))[fᵢ]`。采用稳定log-sum-exp；未用上一轮贪心logits给替代路径算分。softmax只是模型内部相对评分，未经校准，不是教师正确概率。每路径23次CPU调用，共69次条件评分，不进行超参数调优。

可信性核查：重放原贪心的tokens与上一轮逐音记录完全相同，logits最大差值 **{s['validation']['max_previous_greedy_logit_difference']}**，argmax逐音相同。新候选R07—R15共9音的历史输入与贪心不同，实际logits也变化，原始前缀、tokens、五项概率均保存在CONDITIONAL_MODEL_PATH_SCORES.json。两份score_cpu profile实际provider只有CPUExecutionProvider。

## 规划及模型复评分工

PianoPlayer原生搜索使用近似手指运动成本；Lumikey条件NLL在候选生成后评估。两项保留各自单位，没有任意相加成看似可信的总分。只有一套新候选，没有从大量试探中择优。当前不是以Lumikey概率引导搜索，不能声称得到模型最高概率完整路径或模型/动作成本的联合最优。

| 评估路径 | 条件NLL，越低模型越偏好 | 右手整段近似运动成本 | 左手整段近似运动成本 | 非拇指逆序交接 | 同指持音硬冲突 |
|---|---|---|---|---|---|
| 原DESIGN_PROVISIONAL | {paths['old_design']['model_conditional_nll']:.6f} | {paths['old_design']['native_whole_hand_motion_cost']['R']:.6f} | {paths['old_design']['native_whole_hand_motion_cost']['L']:.6f} | 1 | 0 |
| Lumikey贪心 | {paths['lumikey_greedy']['model_conditional_nll']:.6f} | {paths['lumikey_greedy']['native_whole_hand_motion_cost']['R']:.6f} | {paths['lumikey_greedy']['native_whole_hand_motion_cost']['L']:.6f} | 1 | 0 |
| C01 PianoPlayer | {paths['pianoplayer_sequence']['model_conditional_nll']:.6f} | {paths['pianoplayer_sequence']['native_whole_hand_motion_cost']['R']:.6f} | {paths['pianoplayer_sequence']['native_whole_hand_motion_cost']['L']:.6f} | 0 | 0 |

运动成本直接调用作者Hand.ave_velocity，对右16/左7完整已生成指序重算，单位是作者带权cm/s近似量。不是把重叠前瞻窗口的reported_window_cost相加：窗口成本有重复和尾部复用，不能伪装整段成本。原始窗口成本仍完整保留在PIANOPLAYER_RAW_OUTPUT.json。此成本函数也是候选来源，成本变小不能作为独立教学验证。

## 八项要求的覆盖与限制

1. 模型候选评分：已按路径条件正确计算，作为独立复评；未进入PianoPlayer优化目标。
2. 持音占用：按原tick半开区间[on,off)独立核查同手全部音对，无同指占用不同键；不同手同编号独立。
3. 基本跨度：作者和弦规则、M手型近似跨度及真实键位；左三音约9.429cm低于配置17.22cm。不是冻结3D Hands的实测掌幅或关节可达域。
4. 指序与换指：搜索的skip与运动成本处理，重复音可用同指；本轮不将所有逆序当作禁止，但所选实现确实排除部分非拇指逆序，适用范围有局限。
5. 整手换位：通过作者放松手位的重定位代价近似；保留每次relaxed_anchor_shift_cm诊断。不是掌腕轨迹或实际速度上限。
6. 重复音：保留原OFF与下一ON，同指重按需琴键复位；物理复位未建模。
7. 黑白键：音名键位及每指黑键bfactor参与成本；缺少纵深、手腕旋转和真实触键模拟。
8. 上下文：对完整23音搜索与检查，并读取原MIDI中每手之后9音作为只读准备分析；未将其加入23音预测或评分。末端仍依赖有限前瞻及padding，下一乐句未联合优化。

由此可得到有依据、无已知事件硬冲突的一套技术候选，SEQUENCE_POC_PASS限于本轮门禁。若下一阶段要在任意复音上融合神经分数与更宽动作技术，应另行做每路径状态Beam/DP及占用约束；本轮既没有实现该联合搜索，也没有把简单路径评分当作它。

## 运行与保护

Python3.12.1，无新增pip依赖；作者核心仅用标准库。Node v24.18.0和onnxruntime-node/common 1.23.2均只读复用上轮安装。生成约{p['runtime_seconds']:.3f}秒；三条路径模型评分总运行（含会话加载）约{s['runtime_ms']:.3f}ms。首次Node加载在路径空格URL解码处失败，发生在模型加载前；修正为fileURLToPath后成功，失败日志另存，没有因此修改候选。期间小型源码下载出现TLS EOF，做一次有界重试成功，日志保存。

模型权重未改，原贪心输出及证据未改；保护文件清单前后SHA256核查见PROTECTED_INPUTS_BEFORE/AFTER.json。无动画、训练或新增数据集。Lumikey权重商业授权仍未明确，全部为DESIGN_PROVISIONAL。
''')
risks={
'R00':'5→1下行7半音；原样保留，需正常移位/释放。',
'R01':'1–2–3–4–5上行起点；未见新逆序。',
'R02':'顺序上行1→2；未见硬冲突。',
'R03':'顺序上行2→3；未见硬冲突。',
'R04':'顺序上行3→4；未见硬冲突。',
'R05':'4→5后下行G4；新候选恢复G4拇指。',
'R06':'重复G4采用1→1，减少贪心2→1换指；仍需释放重按。',
'R07':'重点：下一E5改3指，9半音跳进需要较大手位横移。',
'R08':'5→3改变；承接G4(1)并转C5(1)，需移动/回位复核。',
'R09':'B02从拇指起1–2–3–4–5；此前E5(3)→C5(1)为下行。',
'R10':'D5(2)→E5(3)同向，旧4→3逆序不再出现。',
'R11':'E5(3)→F♯5(4)同向，贪心4→2逆序不再出现。',
'R12':'黑键4指进入、接白键G5(5)；纵深触键仍待验证。',
'R13':'G5(5)→G4(1)八度下行；恢复旧指序，仍需整手移动。',
'R14':'G4重复1→1；无换指额外横移，需键复位。',
'R15':'G4(1)之后源下一音C5，下一乐句准备未联合优化。',
'L00':'三音5/3/1，各指唯一，近似9.429cm跨度。',
'L01':'三音和弦中音3指；无同指冲突。',
'L02':'三音和弦高音1指，至tick768共同释放。',
'L03':'A3(4)→B3(3)，未见新增逆序。',
'L04':'B3(3)→C4(2)，保持原指法。',
'L05':'C4(2)→B3(3)，保持原指法。',
'L06':'B3(3)下一乐句A3；只读上下文，不增加本轮预测。'}
rows=sorted(b['bindings'],key=lambda x:(x['source_timeline_note']['hand']!='R',x['note_id']))
table='| 音符ID | 手 | 音名 | MIDI | 原指法 | Lumikey贪心 | C01序列 | 相对原/贪心变化 | 换位及风险 |\n|---|---|---|---|---|---|---|---|---|\n'
for x in rows:
 n=x['source_timeline_note'];id=x['note_id'];old=fingers['old_design'][id];g=fingers['lumikey_greedy'][id];a=fingers['pianoplayer_sequence'][id]
 table+=f"| {id} | {'右' if n['hand']=='R' else '左'} | {n['note_name'].replace('F#','F♯')} | {n['midi_note']} | {old} | {g} | {a} | {'变' if old!=a else '同'}/{'变' if g!=a else '同'} | {risks[id]} |\n"
oldchanges=[id for id in fingers['pianoplayer_sequence'] if fingers['pianoplayer_sequence'][id]!=fingers['old_design'][id]];gchanges=[id for id in fingers['pianoplayer_sequence'] if fingers['pianoplayer_sequence'][id]!=fingers['lumikey_greedy'][id]]
doc('ALL_23_SEQUENCE_COMPARISON.md',f'''# 原指法、贪心与序列候选完整对照 — R1

C01是一次真实PianoPlayer生成的唯一新候选；全部DESIGN_PROVISIONAL。原指法和上一轮贪心仅作为生成后的对照/评分路径，未用于固定搜索答案。新候选相对原指法只改变{len(oldchanges)}音：{'、'.join(oldchanges)}；相对贪心改变{len(gchanges)}音：{'、'.join(gchanges)}。左手全部不变。

{table}

## B02与完整前后衔接

旧五音C5/D5/E5/F♯5/G5为3–4–3–4–5；贪心为2–3–4–2–3；新C01为**1–2–3–4–5**。这是现成搜索器真实输出，不是人为指定的目标序列。D5→E5在tick3072、源3.428568秒处变为2→3；E5→F♯5在tick3264、源3.6428535秒处变为3→4。两处音高/指序方向一致，非拇指逆序不再出现。F♯5(4)→G5(5)顺序衔接；其黑键/白键纵深及皮肤接触没有验证。

完整右手为：**5,1,2,3,4,5,1,1,3,1,2,3,4,5,1,1**。关键上下文不是孤立五音：R07 G4(1)→R08 E5(3)→R09 C5(1)→D5(2)→E5(3)→F♯5(4)→G5(5)→R14 G4(1)→R15 G4(1)。没有将4→3或4→2交叉移到另一处非拇指逆序；但手位移动需求有取舍。

R07→R08仍是9半音上行。改用E5中指后，作者放松手位模型的横向anchor变化约**+6.046cm**，旧/贪心用小指时约**+1.454cm**。两起音间隔428.571ms，前OFF与后ON同tick，不能将整个间隔当作无约束空闲移动时间。该增加约4.592cm是本候选新增的重点动作审查项；它不是实际腕轨迹、物理运动速度或“不可弹”证明。R08→R09为E5(3)下行C5(1)，约+1.026cm放松anchor差；需要配合先前手位移动。

R13→R14从贪心G5(3)→G4(1)改回G5(5)→G4(1)，八度音程不变。放松anchor差由约−10.760cm降到约−6.168cm；仍需整手移动，而非定掌位独立动手指。新候选的最大两处手位审查集中在R07→R08和R13→R14。

## 和弦、重复音及所有持音

左手完整5,3,1,4,3,2,3。L00—L02在源0秒同时按下、tick768（0.857142秒）同时释放；指序5/3/1，各指唯一。用作者真实音名键位估算G3—D4横向9.429cm，低于M配置最大17.22cm；这不是冻结左手资产可达证明。后续A3(4)→B3(3)→C4(2)→B3(3)没有新换指问题。

对23音全部同手音对按原on/off tick核查：0个同指同时占用不同键；仅左三音和弦有3对正时长重叠，三指各异。右手无正时长重叠。不同手相同手指编号不相互排斥。

右手两组G4重复R06→R07、R14→R15均为1→1，相较贪心2→1及1→2不再增加换指手位成本。两组都是先OFF再在同tick ON，起音周期428.571ms。没有强制改音乐或添加休止；同指重复仍需真实抬指、键复位、重新触键。不能由指法表断言琴键物理复位已满足，也不证明换指在教学上一定多余。

## 下一乐句上下文与边界

从同一源MIDI实际读取每手之后9音，保存在SOURCE_EVENT_BINDINGS.json/context；不增加本轮23音预测。下一右音是tick4608的C5，后续D5/C5/B4/A4；下一左音是A3，随后G3等。右末G4(1)→下一C5需要上行5半音与手位准备；左末B3(3)→下一A3下降2半音。没有为这些音指定目标手指，未重编MIDI。

本轮优化/神经评分仅含原四小节，下一乐句尚未联合优化，PianoPlayer尾端还存在前瞻结果复用及重复末音padding。因此本轮通过只适用于23音技术候选；推广完整曲目要重新包含真实后续上下文。它没有证明全曲最优，也没有把尾端“model score不错”当作教学PASS。

原NOTE_ON/OFF、音高、velocity、channel及ID保持，0.35秒展示lead未混入。完整逐音源绑定、三路径条件logits及整段成本/风险见JSON证据。未生成任何动作。
''')
doc('FINAL_RECOMMENDATION.md',f'''# 最终建议 — PIANO_SEQUENCE_FINGERING_PLANNING_R1

**SEQUENCE_POC_PASS（技术候选门禁）**。现成PianoPlayer序列前瞻搜索已真实运行，产生一套完整23音候选，身份/46事件约束通过，没有已知明显持音硬冲突。全部仍为DESIGN_PROVISIONAL，没有钢琴教师认证、掌腕物理可行性证明或商业教材接入授权。

| 问题 | 结论 |
|---|---|
| 1. 有没有真正可复用的序列级开源算法？ | 有。PianoPlayer的MIT核心实际跑通约{p['runtime_seconds']:.3f}秒，无需训练。作者HMM有完整Viterbi和已训练参数，但C++环境及授权未解决；ArLSTM/ArGNN有真实Beam代码与公开权重，未在本轮运行。 |
| 2. 能复用Lumikey权重、无需训练吗？ | 能。三条路径分别用各自此前选指重新计算69次CPU logits；贪心tokens/logits精确复现。没有用贪心概率给替代路径算分，没有训练或修改ONNX。 |
| 3. 相比逐音贪心有实质改善吗？ | 在本轮近似成本与结构上有：右手整段作者成本5.229089→2.902030，非拇指逆序1→0，重复换指减少；神经NLL反而6.328477→7.001293，模型并不更偏爱它。近似成本来自所选算法，不是独立教师评测。 |
| 4. B02有更合理的完整候选吗？ | C01的1–2–3–4–5消除了两套旧路径的局部逆序，完整前后音也已检查，值得Human审阅。它是搜索结果，不是人工锁定答案。 |
| 5. 是否存在新的高风险交接？ | 没有发现新增非拇指逆序或硬冲突；但此前G4(1)→E5(3)比原1→5需要更大手位移动，近似anchor+6.046cm，是新增重点审查项。G5(5)→G4(1)八度下行也仍需整手移动。无法仅凭近似评分判定这些交接已经自然或绝对不可弹。 |
| 6. 是否值得进入3D Hands动作规划？ | 值得在Human认可C01后进入单独、受控的动作规划验证，重点是上行9半音、八度下行、黑键4指及同指重复键复位。当前只交付指法，不自动制作动画或接入正式教材。 |
| 7. 还缺什么条件？ | 教师认可、适合冻结手型的跨度/掌腕轨迹验证、真实释放与复位、完整后续乐句优化、跨曲/复音回归，以及Lumikey权重和训练来源的明确商业授权。 |

C01右手：**5,1,2,3,4,5,1,1,3,1,2,3,4,5,1,1**；左手：**5,3,1,4,3,2,3**。相对原指法只改变R08 5→3、R09 3→1、R10 4→2；左手不变。左三音和弦仍5/3/1，两组G4重复均1→1。

本轮选用的是“现成演奏成本搜索生成＋Lumikey条件复评＋事件/跨度/上下文检查”，不是模型与动作成本的联合Beam或全曲最短路径。真实评分保留分项，未任意混成总分，也未为得到PASS改指。仅保留1套新完整候选，旧/贪心是对照而非额外交付候选。合理穿指仍可能存在，PianoPlayer部分剪枝不应推广成统一禁令。

PianoPlayer代码MIT正文已保存，无训练权重；Lumikey代码有MIT声明但权重/训练数据商业权利仍未明确。HMM原作者源码授权未明确，ArLSTM/ArGNN代码MIT不等于预训练权重及研究数据全部商用清权。本轮是隔离技术实验。

交付：EXISTING_ALGORITHM_REVIEW.md、SEQUENCE_PLANNING_FEASIBILITY.md、SEQUENCE_CANDIDATES.json、ALL_23_SEQUENCE_COMPARISON.md及本报告。额外保留原始PianoPlayer输出、三路径逐音条件logits、CPU profiles、原始源码/许可、真实下一乐句上下文和保护哈希。现有Hands/Piano、旧实验、冻结资产、MIDI、音频、琴键和旧候选未修改。

**STOP — HUMAN REVIEW。** 不进入动画生成，等待Human决定是否继续。
''')
status=dict(task='PIANO_SEQUENCE_FINGERING_PLANNING_R1',status='SEQUENCE_POC_PASS',scope='Technical candidate gate only; finite-horizon native search plus path-conditional neural evaluation, not joint global optimization',candidate_count=1,candidate_ids=['C01_PIANOPLAYER'],authority='DESIGN_PROVISIONAL',known_hard_conflicts=0,teacher_certification=False,physical_feasibility_proven=False,commercial_model_rights='NOT_CLEARED',new_movement_review='R07 G4(1) -> R08 E5(3): increased approximate hand-anchor translation',stop='STOP — HUMAN REVIEW')
(O/'FINAL_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('REPORTS_WRITTEN',status['status'],len(oldchanges),len(gchanges))
