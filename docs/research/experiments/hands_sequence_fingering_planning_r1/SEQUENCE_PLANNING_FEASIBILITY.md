# 条件序列评分与本轮规划可行性 — R1

**能够复用Lumikey 0.3.0现有ONNX权重而无需训练。** 已真实取得每音五个完整logits，对旧指法、原贪心和本轮PianoPlayer候选分别按自身历史计算评分。选择的现成规划器是PianoPlayer有限前瞻搜索；本轮没有另写Beam或冒称最优Viterbi。

## 模型依赖与正确评分

固定源码dist/inference.js维护fingerLastMidi[5]、fingerLastTime[5]。选中某指后，它记录当前音高、把对应时间设为负的音符时长；走到下一音时按实际起音差让五指状态老化。下一音的previous tokens因指序而改变。lookahead最多20音，包含未来音高、时间及可选finger hints。前指历史变了，后音的输入与logits必须重算。

公开predictFingerings/predictHandFingerings只返回选定finger，没有现成的beam、top-k序列或返回完整logits接口。但传入的ONNX session.run会返回logits，能够包装记录。固定finger可以改变状态及未来hint；若把整条待评路径一次性全标fixed，则先前音会看到未来答案，不再是仅给定过去的条件评分。本轮不采用这种做法。

score_paths.mjs使用官方predictFingerings和官方状态更新。每条完整路径使用全新内存notes，最初都没有finger；包装session.run记录并执行真实ONNX，然后只为**当前**音设置该路径的finger。官方接口在await run后读取当前finger，并据此更新每指历史；所有未来音始终未知。输入tokens的26个finger_hint逐个验证均为-1。这里的临时finger是已生成路径的评分复放，不是生成阶段提供的目标答案，也未回写任何源文件。

评分为 `NLL = Σᵢ −log softmax(logitsᵢ(该路径此前选指, 已知音乐未来音, 未知未来指法))[fᵢ]`。采用稳定log-sum-exp；未用上一轮贪心logits给替代路径算分。softmax只是模型内部相对评分，未经校准，不是教师正确概率。每路径23次CPU调用，共69次条件评分，不进行超参数调优。

可信性核查：重放原贪心的tokens与上一轮逐音记录完全相同，logits最大差值 **0**，argmax逐音相同。新候选R07—R15共9音的历史输入与贪心不同，实际logits也变化，原始前缀、tokens、五项概率均保存在CONDITIONAL_MODEL_PATH_SCORES.json。两份score_cpu profile实际provider只有CPUExecutionProvider。

## 规划及模型复评分工

PianoPlayer原生搜索使用近似手指运动成本；Lumikey条件NLL在候选生成后评估。两项保留各自单位，没有任意相加成看似可信的总分。只有一套新候选，没有从大量试探中择优。当前不是以Lumikey概率引导搜索，不能声称得到模型最高概率完整路径或模型/动作成本的联合最优。

| 评估路径 | 条件NLL，越低模型越偏好 | 右手整段近似运动成本 | 左手整段近似运动成本 | 非拇指逆序交接 | 同指持音硬冲突 |
|---|---|---|---|---|---|
| 原DESIGN_PROVISIONAL | 9.511052 | 3.003804 | 1.957583 | 1 | 0 |
| Lumikey贪心 | 6.328477 | 5.229089 | 1.957583 | 1 | 0 |
| C01 PianoPlayer | 7.001293 | 2.902030 | 1.957583 | 0 | 0 |

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

Python3.12.1，无新增pip依赖；作者核心仅用标准库。Node v24.18.0和onnxruntime-node/common 1.23.2均只读复用上轮安装。生成约5.637秒；三条路径模型评分总运行（含会话加载）约630.570ms。首次Node加载在路径空格URL解码处失败，发生在模型加载前；修正为fileURLToPath后成功，失败日志另存，没有因此修改候选。期间小型源码下载出现TLS EOF，做一次有界重试成功，日志保存。

模型权重未改，原贪心输出及证据未改；保护文件清单前后SHA256核查见PROTECTED_INPUTS_BEFORE/AFTER.json。无动画、训练或新增数据集。Lumikey权重商业授权仍未明确，全部为DESIGN_PROVISIONAL。
