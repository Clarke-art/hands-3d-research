# 最终技术路线建议 R1

**算法方向优先Tipiano；眼下最小验证优先“教师核准的短段真实动作先验＋掌腕/指尖联合重定向”。当前没有查到一个可直接接入、可控指定指法并已清楚允许商业教材用途的完整开源模型。**

## 六项明确回答

1. **三个项目哪个最值得继续验证？** Tipiano的可控接口目标最符合本项目，应关注其正式发布；立即可观察的动作先验以FürElise捕获数据更有针对性。但FürElise公开数据是NC，产品实验优先取得教师自有或另行授权的短段。PianoMotion10M适合作为可运行代码研究对象，优先级低于以上两者。[Tipiano官方发布状态](https://tipiano.io/)、[FürElise数据卡](https://huggingface.co/datasets/rcwang/for_elise)
2. **有可直接复用的开源模型吗？** PianoMotion10M确实有源码和公开ckpt，不是空壳；但当前推理依赖测试集/CUDA/音频编码器/MANO，缺指定指法硬约束，权重许可不明确，运行也未验证。Tipiano和FürElise未核实完整公开生成实现。因此本项目意义下答案为“没有已验证的即插即用模型”。[PianoMotion源码](https://github.com/agnJason/PianoMotion10M)、[权重树](https://huggingface.co/agnJason/PianoMotion_models/tree/main)
3. **需要真实演奏先验吗？** 强烈建议至少一段教师核准的3↔4交接参考，用于腕/掌布局、闲置指和释放耦合。并非理论上绝对必需，也不需要直接下载整个数据集；它能让最小实验检验真实路径而非继续猜角度。不能仅从MIDI确定唯一正确手腕轨迹。[FürElise数据预览](https://for-elise.github.io/static_visualizer/vis.html?id=100)
4. **能保留现有Rig与冻结资产吗？** 可以。将外部动作作为目标/先验转换到现有骨长、轴、工程域，保留网格/权重/琴键与静态批准姿态。未来派生动作的短段root/腕变化与修改冻结资产不同；转换后仍必须检查真实skin和键体，不能直接拷MANO角度。详见BLENDER_INTEGRATION_FEASIBILITY.md。
5. **下一阶段最小实验是什么？** 教师先确认C5(3)→D5(4)→E5(3)→F♯5(4)→G5(5)，再取得一个带腕/关节/逐指事件且权利清楚的短样本。仅在约3.25–4.75s范围做一次整手协同重定向试验，保留事件与音乐，原俯视相机验收。对照必须分开看原生先验质量和目标Rig重定向损失。此为建议，未执行。
6. **暂时排除什么？** FürElise逐曲RL完整路线因未公开完整代码且训练成本1–3天而排除；Tipiano缺发布包时不自行全面重写/重训；PianoMotion音频模型不能作为指定指法的直接替换。商业阶段排除未获授权的NC动作数据、权利不明的ckpt与默认非商业MANO链，直到权利人明确允许。[FürElise训练说明](https://arxiv.org/html/2410.05791v1)、[MANO许可](https://mano.is.tue.mpg.de/license.html)

## 状态清单

|路线或用途|状态|何时可推进|
|---|---|---|
|教师授权短先验＋现有Rig整手协同小实验|READY_FOR_ISOLATED_POC（设计层）|Human批准、教师确认指法、样本与许可齐备后|
|Tipiano级联方法/官方演示研究|RESEARCH_ONLY|源码、权重、先验与许可正式可核查后再评估执行|
|Tipiano直接模型接入|BLOCKED|当前Code+Dataset仍TBD|
|PianoMotion10M原样Windows推理及B02可控性|INSUFFICIENT_EVIDENCE|隔离适配入口、权重权利、依赖兼容及12GB推理试验均待验证|
|PianoMotion10M静态代码/双手姿态先验研究|RESEARCH_ONLY|仍不能冒称可指定指法或精确触键|
|FürElise捕获样例观察/算法思想|RESEARCH_ONLY|教师筛选；研究目的与许可须相符|
|FürElise完整生成实现|BLOCKED|没有核实正式生成代码/权重，且不是数分钟路线|
|未经另许可将FürElise/PianoMotion数据或MANO链用于商业数字教材|BLOCKED|数据、模型、MANO与第三方素材各层分别澄清|

## 已验证事实、推论和缺口

已验证：官网发布状态、固定源码/配置、四个权重对象的元数据、NC/MANO条款、当前Rig接口、GPU信息，以及报告中列明的实际官方画面。少量预览的两行JSON结构已读取；没有下载权重或47GB数据包。

研究推论：B02可能需要掌腕/整手布局与指序共同规划，固定root的局部后修补可能限制解空间。这不是已证明的唯一成因；教师、源动作和最小几何验证仍是关键。

缺口：Tipiano最新代码/权重/标签许可；PianoMotion ckpt完整运行与许可、原生Windows和12GB显存成本；FürElise原始21关节单曲小包、pose编码/坐标合同、完整生成代码；任何方法对本项目五音指定指法的原生及重定向教学质量。本轮没有通过宣传指标填补这些缺口。

完成了五份中文报告和证据目录。没有安装大型依赖、运行模型、启动训练/求解、修改Action/Blend/冻结资产、改变MIDI/指法或制作新动画视频；未启动第二阶段。

**STOP — HUMAN REVIEW。未经Human明确批准，不进入集成或动作生成。**
