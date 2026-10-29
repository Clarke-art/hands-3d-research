# 可复用序列指法算法调查 — R1

调查日期2026-10-11，最多三条路线。实际选用PianoPlayer，核心无需新增依赖、无需训练，已对真实23音运行。没有把论文宣称直接当成可执行实现，也没有下载PIG/ThumbSet或大型数据集。

| 路线 | 真实实现、版本及授权 | 权重/训练需求 | MIDI、双手、和弦和重复音 | 序列约束及Lumikey结合成本 | 本轮决定 |
|---|---|---|---|---|---|
| Nakamura/Saito/Yoshii HMM / 高阶Viterbi / chord HMM | 作者页提供SourceCode_v190921.zip，126511字节，SHA256 `e2c15638794a71ab8e4aed0ffaa89d38bf86b56f6c64c602b54531673eeaf26c`；含一至三阶及chord HMM的C++ Viterbi实现和运行入口。压缩包未发现明确LICENSE或授权正文，不能当作商业已授权开源 | param_FHMM1/2/3.txt及param_CHMM1.txt均真实存在，README说明默认使用已训练参数；运行不需训练 | 运行入口接PIG fingering文本，需MIDI身份/时间适配；分别处理双手，chord HMM有和弦聚类。重复音属于概率转移，不保证反复触键轨迹或同指持音占用 | 高阶状态转移及回溯能解有限HMM序列，统计模型不是腕部物理模型。其转移/发射参数不是Lumikey的每指历史状态，不能直接替换为上一轮固定logits；如融合需新适配decoder | 有真实完整源码和参数。当前PATH未发现g++/clang++/cl，不为本实验安装工具链；未执行该模型，未虚构预测 |
| PianoPlayer | 固定git `6fb0e2114d7b21f75c0be5208172e1243a57323e`，pyproject版本3.0.2；LICENSE正文MIT，Copyright 2017 Marco Musy；核心hand.py/models.py实际可导入 | 完整规则与演奏成本算法，不使用预训练权重，也不需训练 | 提供MIDI/MusicXML/PIG读入；核心接受已分手INote。和弦有唯一手指、顺序及跨度规则；重复同音可以使用同指。本轮直接用正式已分手23音，不用自动routing | 每次至多9音的深度优先组合前瞻、保留部分前次结果；不是Beam、DP或全曲最短路径。成本结合每指位置/强度、起音时间、黑键偏好及换位。可先生成候选，再由Lumikey正确条件复评；原生没有ONNX模型评分接口 | **实际隔离运行**，5.637秒，一套完整23音候选，无固定指提示。官方默认和弦0.05秒错开在本轮不采用，真实同起时刻不变 |
| Ramoneda等自回归ArLSTM/ArGNN + Beam Search | PRamoneda/Automatic-Piano-Fingering git `d0d2f433c926be5e89540cbafe38bf43820ad2d2`；LICENSE正文MIT。seq2seq_model.py内decode_with_beam_search真实保留每条路径的LSTM隐藏状态及前指embedding，再扩展并选择beam | 真实models目录有左右ArLSTM各849324字节、ArGNN各2949407字节，不需重新训练原则上可用。没有本轮下载/加载.pth，也不声称已运行 | 源码是PIG/ThumbSet特征与模型实验入口，未确认现成原始MIDI一键接口；左右分模型。GNN图结构表示复音，但未见它在解码时硬保证持音手指唯一。重复音可预测；物理释放仍需另查 | 真正的神经条件序列Beam实现，能输出完整指序，并非并行分类后拼接。PyTorch与图/特征适配成本高于当前已验证ONNX；其隐藏状态不等同Lumikey每指上次状态，不能直接插入Lumikey权重 | 保留为有源码及权重的技术路线；不为这23音安装大型PyTorch环境。训练代码有研究数据依赖，代码MIT不等于权重/训练数据商业清权 |

主来源：[作者HMM页面](https://statpianofingering.github.io/demo.html)、[Statistical Learning and Estimation of Piano Fingering论文](https://arxiv.org/abs/1904.10237)、[PianoPlayer固定源码](https://github.com/marcomusy/pianoplayer/tree/6fb0e2114d7b21f75c0be5208172e1243a57323e)、[PianoPlayer许可证](https://github.com/marcomusy/pianoplayer/blob/6fb0e2114d7b21f75c0be5208172e1243a57323e/LICENSE)、[ArLSTM/ArGNN固定源码](https://github.com/PRamoneda/Automatic-Piano-Fingering/tree/d0d2f433c926be5e89540cbafe38bf43820ad2d2)、[Beam解码器](https://github.com/PRamoneda/Automatic-Piano-Fingering/blob/d0d2f433c926be5e89540cbafe38bf43820ad2d2/nns/seq2seq_model.py)、[自回归指法论文](https://eita-nakamura.github.io/articles/Ramoneda_PianoFingeringFromPartiallyAnnotatedScores_2022.pdf)。原始仓库树、许可证和相关源码快照在evidence。

## 实际适配边界

本轮使用原始Hand.generate，而非重写搜索器。直接构建INote，fingering=0；保留原起点、时长、音高、ID映射及三音同起关系。坐标使用作者keypos(note-name)，因为作者keypos_midi把半音编号乘白键宽度，包含与真实键布局不符的间距；使用其已有音名函数不修改作者源码或音乐。左右都用固定M手型、默认autodepth和默认关闭posture memory，没有手型或深度调参。

PianoPlayer会硬剪枝部分非拇指逆序，但允许拇指穿指/跨拇指方向。因此不能将其剪枝当作所有钢琴技术的通则；合理非拇指换位可能被漏掉。持音占用也未完整进入其演奏成本，我们对本曲的全部真实on/off独立验证。它提供的是低成本候选路线，不是完整生物力学或商业教学解决方案。

本轮已有现成核心可运行，依用户的优先顺序，不再另外开发Beam Search。Lumikey用于候选生成后的条件模型复评，没有宣称实现神经/演奏成本的联合全局搜索。
