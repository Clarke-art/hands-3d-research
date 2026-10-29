# 钢琴手部动作技术对照 R1

核查日期：2026-10-11。原则：PEDAGOGICALLY_CORRECT_AND_HUMAN_VISIBLE_FIRST。研究为静态源码、官方演示与接口分析；**没有实际运行任何模型**。READY_FOR_ISOLATED_POC 表示可以提出有边界的验证实验，不代表已经通过部署或商业授权。

## 主要对照

|项目|真实公开状态|输入控制|输出/动作组织|教学观察与局限|当前用途与状态|
|---|---|---|---|---|---|
|Tipiano|论文可读、在线演示可用；当前官网 Code+Dataset (TBD)，未核实可下载训练/推理源码或权重|论文的可控模式用MIDI和逐帧指法；官网另有自动指法模式，两者不能混同|指尖→轨迹→手腕→中间关节；每手21个3D点，渲染还需拟合|实际音阶俯视可看见掌部整体移位及分立指形；未证明指定B02、全部黑键和释放正确|目标匹配最强的算法参考：RESEARCH_ONLY；直接模型集成：BLOCKED（发布缺口）|
|PianoMotion10M|固定提交源码可获取；HF确有4套ckpt及配置；不是只有空仓库|当前infer调用音频，不接收指定指法/NOTE_ON/OFF硬约束|双手MANO全姿态与全局位置；音频位置预测器引导扩散|已观察生成样例仅有白色双手，缺键盘，无法检查虚假触键/穿黑键|可适配研究代码：RESEARCH_ONLY；直接满足本项目教学要求：INSUFFICIENT_EVIDENCE|
|FürElise|公开原始动作数据和预览代码；官网生成算法仍 To be released，没有核实完整生成权重|数据自带同步MIDI；论文生成方法用MIDI，未查到固定指定指法的公开API|真实捕获分支有双手21关节、MANO参数及顶点；生成分支另有物理控制|实际捕获样本的独立手形与整手移位可见；重建数据也需教师筛选|动作先验/研究参照：RESEARCH_ONLY；完整生成实现及未授权商用：BLOCKED|

官网与论文入口：[Tipiano](https://tipiano.io/)、[Tipiano v1](https://arxiv.org/html/2604.09692v1)、[PianoMotion10M源码](https://github.com/agnJason/PianoMotion10M)、[FürElise官网](https://for-elise.github.io/)。实际截图和不确定项见 DEMO_VISUAL_REVIEW.md。

## Tipiano：最贴近需求，但没有可核实的部署包

论文v1输入显式MIDI/指法，先锚定指尖，再学习手腕和中间关节；按键时的轴向mask不等于最终skin接触证明。报告F1取中间阶段，随后全姿态处理和MANO渲染拟合仍可能引入误差。因此不能用F1=0.910替代本项目的暂停、穿指和真实键面验收。[论文§4、§5](https://arxiv.org/html/2604.09692v1)

**版本注意**：当前官网把指法来源算入五阶段，并介绍手腕动态增强及生物力学投影；arXiv目前可核查v1是四阶段运动级联。官网信息是作者当前描述，不是已检查到的实现。Code+Dataset按钮仍TBD，证据保存为 `evidence/tipiano_live_page_snapshot.txt` 与 `tipiano_release_status.png`。[当前官网](https://tipiano.io/)

Python/PyTorch版本、推理API、checkpoint大小、最小显存、推理时间、Windows支持、发布代码/权重/新增指法标签的许可证均 **UNKNOWN**。论文报告A6000 48GB训练，不可把训练卡显存当成推理最低要求；无现成权重时复现会涉及训练，超出下一次最小验证的合理范围。[论文§5.1](https://arxiv.org/html/2604.09692v1)

## PianoMotion10M：源码与权重实有，端到端执行未验证

源码提交固定为 `86539e5a16d10ba462005f1f2bd9d72459ac2000`；7个关键Python文本通过AST语法检查，**没有import或执行它们**。

|静态证据|可核实结论|
|---|---|
|[infer.py L17–38](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/infer.py#L17)|CLI为实验目录/数据根目录/测试模式；读取实验配置并固定两个UP主筛选，不能直接输入任意WAV或本项目指法|
|[datasets/PianoPose.py](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/datasets/PianoPose.py)|从测试列表、annotation与audio读数据，16kHz音频/30fps动作；返回音频和双手姿态。当前返回值没有MIDI约束|
|[infer.py L82–115](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/infer.py#L82)|读取ckpt的state_dict，强制CUDA，预测96维旋转量及6维双手位置，再交给渲染器；未直接导出Blender Action|
|[models/piano2posi.py L8](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/models/piano2posi.py#L8)、[denoise_diffusion.py L15](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/models/denoise_diffusion.py#L15)|两文件无条件import mamba_ssm；安装文档的“Optional”与当前代码入口不一致，选Transformer也不能原样忽略此导入|
|[models/mano.py](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/models/mano.py)、[datasets/show.py L91–120](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/datasets/show.py#L91)|解码为3维translation+3维global orientation+45维非PCA手姿态；左手由右手模型镜像，需核实反射与关节符号|
|[denoise_diffusion.py L499–504](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/models/denoise_diffusion.py#L499)|默认采样步数与训练步数一致，当前配置1000步；没有已验证的低步数实时模式|

部署基线：[安装文档](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/docs/install.md)指定Python3.10、Torch/torchvision/torchaudio 2.1.2/0.16.2/2.1.2、cu118；[requirements](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/requirements.txt)含numpy1.23、librosa0.9.2、smplx/chumpy、nvdiffrast等，部分从Git安装而未锁版本。文档还误写 `requirement.txt`，实际文件是 `requirements.txt`。音频编码器由from_pretrained另行加载，MANO_RIGHT.pkl需单独取得。

HF文件元数据确认存在以下二进制对象；**没有下载或反序列化**，因此state_dict键匹配、完整性和可执行结果仍待验证。

|权重目录|ckpt字节数|约GiB|
|---|---:|---:|
|diffusion_posiguide_hubertbase_mamba2|1,313,128,490|1.22|
|diffusion_posiguide_hubertbase_tf2|1,520,681,914|1.42|
|diffusion_posiguide_hubertlarge_mamba2|2,213,668,834|2.06|
|diffusion_posiguide_hubertlarge_tf2|2,970,320,157|2.77|

来源：[模型文件树](https://huggingface.co/agnJason/PianoMotion_models/tree/main)，快照 `evidence/pianomotion_model_tree.json`；模型仓库revision `de146178457a4f4d262f4f4492597d5fdf76dd23`。Base TF包有args.txt、args_posi.txt和ckpt，但音频模型路径仍指向本地checkpoints。是否可完全免训练跑通，不能仅靠文件存在宣布；不需要先下载116小时全数据才做适配实验，但原infer入口依赖数据布局。[配置](https://huggingface.co/agnJason/PianoMotion_models/blob/main/diffusion_posiguide_hubertbase_tf2/args_posi.txt)

Windows原生兼容 **未验证**。Mamba官方主要列Linux；Torch CUDA、音频库、MANO与渲染扩展也须分别处理，较可控的未来选择是隔离WSL/Linux或去除无关渲染/无条件导入后的最小导出入口，而非安装到现有Blender Python。[Mamba官方要求](https://github.com/state-spaces/mamba#installation)

本机只读核查：RTX3060，12288MiB显存，驱动610.88，系统Python3.12.1。作者实验卡为3090Ti；最低推理显存和8秒推理耗时未公布/未测。**12GB能否跑Base仍UNKNOWN**，checkpoint体积不能换算实际峰值显存。未安装Torch或CUDA依赖。[官方实验说明](https://github.com/agnJason/PianoMotion10M#models)

## FürElise：可访问少量预览，不等于少量原始关节包

数据revision `ea14b581cbc33d8f2d0aca8e609e3e5c62423e50`。HF树将原数据装在一个 `dataset.zip`，47,013,913,542字节；download_data.sh下载并解压整个包，不支持文档化的单曲关节下载。卡片称约44G，文件树给出约47.01GB，应采用实际字节数做容量估计。[文件树](https://huggingface.co/datasets/rcwang/for_elise/tree/main)、[下载脚本](https://huggingface.co/datasets/rcwang/for_elise/blob/main/download_data.sh)

已实际检查官网id=100预览：1798帧，音频约29.99s。仅额外读取motion.json头两行，共101,116字节，保存**字段/维度摘要，不保存坐标**。每行是左右各778×3顶点和88个pressed_keys；没有21关节或MANO pose。浏览器短样例可看，原始重定向需要的motion.pkl小包仍未核实可独立取得。[预览](https://for-elise.github.io/static_visualizer/vis.html?id=100)、`SMALL_SAMPLE_ACCESS_CHECK.json`。

原始数据卡列出每手 `joints:N×21×3`、global_translation、global_rotation、pose、shape和verts，59.94fps。pose写成45维PCA coefficients，不能未经实际小样核验就当45维axis-angle读取。[数据卡](https://huggingface.co/datasets/rcwang/for_elise/)

生成算法与查看器不同：HF公开的Flask/JS仅播放数据，不包含论文的扩散/检索/控制训练完整实现。论文报告扩散训练约1天/两张A5000，逐曲策略训练约1–3天/一张A5000；不适合作为数分钟修复的替代。[论文§5.1](https://arxiv.org/html/2410.05791v1)、[官网发布状态](https://for-elise.github.io/)

## 商业数字教材授权：分层结论

|对象|已核实许可|商业结论|
|---|---|---|
|PianoMotion10M源码|Apache-2.0，[固定LICENSE](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/LICENSE)|该源码层可按条款评估使用；不能延伸至下面各层|
|PianoMotion10M ckpt|HF无license元数据、无独立LICENSE；README未明确权重授权|INSUFFICIENT_EVIDENCE；商业或研究运行前取得权利范围，不从源码许可证推断|
|PianoMotion10M数据/benchmark|官网CC BY-NC4.0|当前商业复用BLOCKED；作者需另行授权|
|FürElise数据及HF分发内容|卡片CC BY-NC4.0；预览代码无单独宽松许可已核实|当前商业动作提取/训练/分发不可按开放商用资源处理|
|FürElise生成代码/权重|完整正式发布未核实|BLOCKED，不把查看器代码当生成器|
|Tipiano代码/权重/新增标签|尚未核实发布和独立许可|BLOCKED/INSUFFICIENT_EVIDENCE|
|MANO模型/数据|默认限制非商业研究/教育/艺术，另有商业许可渠道|商用需单独授权；换成自己的Rig并不自动消除生成链使用MANO的授权问题|
|HuBERT base第三方权重|官方卡Apache-2.0|仅该指定版本已核实；其他编码器/Aria/依赖分别核查|
|原演奏视频、录音、曲谱和表演者权利|数据许可证不自动补齐第三方素材权利|教材发布前单独确认；不是因曲子年代久就推断录音可商用|

依据：[PianoMotion版权说明](https://agnjason.github.io/PianoMotion-page/#copyright)、[FürElise许可](https://huggingface.co/datasets/rcwang/for_elise/#licensing)、[MANO条款](https://mano.is.tue.mpg.de/license.html)、[HuBERT模型卡](https://huggingface.co/facebook/hubert-base-ls960)、[CC BY-NC正文](https://creativecommons.org/licenses/by-nc/4.0/)。NC不等于所有企业内部研发都自动获准。权重的训练来源/衍生产物权利应向权利人核实，本报告不假设许可证会自动继承或自动消失。

STOP — HUMAN REVIEW。
