"""Assemble research reports only; no model imports, inference, rig edits or integration."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;E=P/'evidence'
commit=json.loads((E/'pianomotion_tree.json').read_text(encoding='utf8'))['sha']
GH=f'https://github.com/agnJason/PianoMotion10M/blob/{commit}/'
HF='https://huggingface.co/agnJason/PianoMotion_models/'
FE='https://huggingface.co/datasets/rcwang/for_elise/'
def doc(n,x):(P/n).write_text(x,encoding='utf8')
doc('TECHNOLOGY_COMPARISON.md',f'''# 钢琴手部动作技术对照 R1

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

源码提交固定为 `{commit}`；7个关键Python文本通过AST语法检查，**没有import或执行它们**。

|静态证据|可核实结论|
|---|---|
|[infer.py L17–38]({GH}infer.py#L17)|CLI为实验目录/数据根目录/测试模式；读取实验配置并固定两个UP主筛选，不能直接输入任意WAV或本项目指法|
|[datasets/PianoPose.py]({GH}datasets/PianoPose.py)|从测试列表、annotation与audio读数据，16kHz音频/30fps动作；返回音频和双手姿态。当前返回值没有MIDI约束|
|[infer.py L82–115]({GH}infer.py#L82)|读取ckpt的state_dict，强制CUDA，预测96维旋转量及6维双手位置，再交给渲染器；未直接导出Blender Action|
|[models/piano2posi.py L8]({GH}models/piano2posi.py#L8)、[denoise_diffusion.py L15]({GH}models/denoise_diffusion.py#L15)|两文件无条件import mamba_ssm；安装文档的“Optional”与当前代码入口不一致，选Transformer也不能原样忽略此导入|
|[models/mano.py]({GH}models/mano.py)、[datasets/show.py L91–120]({GH}datasets/show.py#L91)|解码为3维translation+3维global orientation+45维非PCA手姿态；左手由右手模型镜像，需核实反射与关节符号|
|[denoise_diffusion.py L499–504]({GH}models/denoise_diffusion.py#L499)|默认采样步数与训练步数一致，当前配置1000步；没有已验证的低步数实时模式|

部署基线：[安装文档]({GH}docs/install.md)指定Python3.10、Torch/torchvision/torchaudio 2.1.2/0.16.2/2.1.2、cu118；[requirements]({GH}requirements.txt)含numpy1.23、librosa0.9.2、smplx/chumpy、nvdiffrast等，部分从Git安装而未锁版本。文档还误写 `requirement.txt`，实际文件是 `requirements.txt`。音频编码器由from_pretrained另行加载，MANO_RIGHT.pkl需单独取得。

HF文件元数据确认存在以下二进制对象；**没有下载或反序列化**，因此state_dict键匹配、完整性和可执行结果仍待验证。

|权重目录|ckpt字节数|约GiB|
|---|---:|---:|
|diffusion_posiguide_hubertbase_mamba2|1,313,128,490|1.22|
|diffusion_posiguide_hubertbase_tf2|1,520,681,914|1.42|
|diffusion_posiguide_hubertlarge_mamba2|2,213,668,834|2.06|
|diffusion_posiguide_hubertlarge_tf2|2,970,320,157|2.77|

来源：[模型文件树]({HF}tree/main)，快照 `evidence/pianomotion_model_tree.json`；模型仓库revision `de146178457a4f4d262f4f4492597d5fdf76dd23`。Base TF包有args.txt、args_posi.txt和ckpt，但音频模型路径仍指向本地checkpoints。是否可完全免训练跑通，不能仅靠文件存在宣布；不需要先下载116小时全数据才做适配实验，但原infer入口依赖数据布局。[配置]({HF}blob/main/diffusion_posiguide_hubertbase_tf2/args_posi.txt)

Windows原生兼容 **未验证**。Mamba官方主要列Linux；Torch CUDA、音频库、MANO与渲染扩展也须分别处理，较可控的未来选择是隔离WSL/Linux或去除无关渲染/无条件导入后的最小导出入口，而非安装到现有Blender Python。[Mamba官方要求](https://github.com/state-spaces/mamba#installation)

本机只读核查：RTX3060，12288MiB显存，驱动610.88，系统Python3.12.1。作者实验卡为3090Ti；最低推理显存和8秒推理耗时未公布/未测。**12GB能否跑Base仍UNKNOWN**，checkpoint体积不能换算实际峰值显存。未安装Torch或CUDA依赖。[官方实验说明](https://github.com/agnJason/PianoMotion10M#models)

## FürElise：可访问少量预览，不等于少量原始关节包

数据revision `ea14b581cbc33d8f2d0aca8e609e3e5c62423e50`。HF树将原数据装在一个 `dataset.zip`，47,013,913,542字节；download_data.sh下载并解压整个包，不支持文档化的单曲关节下载。卡片称约44G，文件树给出约47.01GB，应采用实际字节数做容量估计。[文件树]({FE}tree/main)、[下载脚本]({FE}blob/main/download_data.sh)

已实际检查官网id=100预览：1798帧，音频约29.99s。仅额外读取motion.json头两行，共101,116字节，保存**字段/维度摘要，不保存坐标**。每行是左右各778×3顶点和88个pressed_keys；没有21关节或MANO pose。浏览器短样例可看，原始重定向需要的motion.pkl小包仍未核实可独立取得。[预览](https://for-elise.github.io/static_visualizer/vis.html?id=100)、`SMALL_SAMPLE_ACCESS_CHECK.json`。

原始数据卡列出每手 `joints:N×21×3`、global_translation、global_rotation、pose、shape和verts，59.94fps。pose写成45维PCA coefficients，不能未经实际小样核验就当45维axis-angle读取。[数据卡]({FE})

生成算法与查看器不同：HF公开的Flask/JS仅播放数据，不包含论文的扩散/检索/控制训练完整实现。论文报告扩散训练约1天/两张A5000，逐曲策略训练约1–3天/一张A5000；不适合作为数分钟修复的替代。[论文§5.1](https://arxiv.org/html/2410.05791v1)、[官网发布状态](https://for-elise.github.io/)

## 商业数字教材授权：分层结论

|对象|已核实许可|商业结论|
|---|---|---|
|PianoMotion10M源码|Apache-2.0，[固定LICENSE]({GH}LICENSE)|该源码层可按条款评估使用；不能延伸至下面各层|
|PianoMotion10M ckpt|HF无license元数据、无独立LICENSE；README未明确权重授权|INSUFFICIENT_EVIDENCE；商业或研究运行前取得权利范围，不从源码许可证推断|
|PianoMotion10M数据/benchmark|官网CC BY-NC4.0|当前商业复用BLOCKED；作者需另行授权|
|FürElise数据及HF分发内容|卡片CC BY-NC4.0；预览代码无单独宽松许可已核实|当前商业动作提取/训练/分发不可按开放商用资源处理|
|FürElise生成代码/权重|完整正式发布未核实|BLOCKED，不把查看器代码当生成器|
|Tipiano代码/权重/新增标签|尚未核实发布和独立许可|BLOCKED/INSUFFICIENT_EVIDENCE|
|MANO模型/数据|默认限制非商业研究/教育/艺术，另有商业许可渠道|商用需单独授权；换成自己的Rig并不自动消除生成链使用MANO的授权问题|
|HuBERT base第三方权重|官方卡Apache-2.0|仅该指定版本已核实；其他编码器/Aria/依赖分别核查|
|原演奏视频、录音、曲谱和表演者权利|数据许可证不自动补齐第三方素材权利|教材发布前单独确认；不是因曲子年代久就推断录音可商用|

依据：[PianoMotion版权说明](https://agnjason.github.io/PianoMotion-page/#copyright)、[FürElise许可]({FE}#licensing)、[MANO条款](https://mano.is.tue.mpg.de/license.html)、[HuBERT模型卡](https://huggingface.co/facebook/hubert-base-ls960)、[CC BY-NC正文](https://creativecommons.org/licenses/by-nc/4.0/)。NC不等于所有企业内部研发都自动获准。权重的训练来源/衍生产物权利应向权利人核实，本报告不假设许可证会自动继承或自动消失。

STOP — HUMAN REVIEW。
''')
doc('DEMO_VISUAL_REVIEW.md','''# 官方演示教学观察 R1

本报告是**有限样例/暂停画面观察**，不是对完整数据集、所有速度和全部音符的质量认证。绿色琴键是演示标识，不能仅凭它证明skin真正按下运动键面。没有逐帧公开指法标签的画面，无法认证“哪一指在何时弹了指定音”。

## 实际观察记录

|项目/入口|本轮真实看到的内容|可支持的教学观察|不能下的结论|
|---|---|---|---|
|[Tipiano benchmark](https://tipiano.io/benchmark)，Scales Technical Lv.3（B major），Top|加载了Ground Truth/Tipiano/Auto/S2C四路；Tipiano官方视频id23，直接定位1.995253s与3.997410s，并看了起止姿态|双手随音阶显著沿键盘移动，掌部方向也变化；抽样帧中手指可分辨，有不同弯曲状态，黑键区能看见闲置指靠近。比只有指尖点的演示更适合讨论整手组织|不证明C5(3)→D5(4)→E5(3)的指定交接可行；不证明每一帧中/无名指无交叠；俯视缺少纵向深度，不能认证持键、释放或无穿黑键|
|[PianoMotion官方生成样例](https://agnjason.github.io/PianoMotion-page/)，Generated Hand Motion，sample_out_1|实际加载1920×1088、8.125s视频；记录0s、播放初段与末帧|白色双手有不同指形、掌部方向和位置变化；可以观察生成器确实输出双手姿态|画面没有键盘，无法判断正确键、触键/释放、黑键高度或闲置指碰撞；手形像演奏不等于教学合格|
|[FürElise数据预览id100](https://for-elise.github.io/static_visualizer/vis.html?id=100)，Top，Chopin Sonata No.2|实际加载短段捕获数据；定位音频2.399730s、6.599259s，见左右手分工、整手位移和绿色键|主动/闲置手姿态明显不同；几个暂停点手指轮廓可辨，掌部整体随任务改变，适合作为教师讨论动作参考|这不是直接拍摄的原手视频，也不是生成算法结果；重建/拟合/IK处理后的模型仍可能误差。不能据抽样判定全数据适合照着模仿|

## 图像证据

- Tipiano：`evidence/tipiano_scale_top_02s.png`、`tipiano_scale_top_04s.png`。后者等媒体定位完成后重新截图，避免把seek中的旧解码画面当新时刻。
- PianoMotion：`evidence/pianomotion_generated_initial.png`、`pianomotion_generated_sample.png`（末帧8.125011s）。
- FürElise：`evidence/furelise_capture_top_sample.png`、`furelise_capture_top_06s.png`。

这些是浏览器实际画面截图，没有下载原视频、重渲染动作、换模型或重新制作演示。另一个 `tipiano_scale_top_sample.png` 是较早的末段全屏截图，不能当精确中段证据；以带02s/04s名称和本表的媒体时间为准。

## 重点技能的证据边界

|观察主题|当前能判断什么|仍需补充什么|
|---|---|---|
|中指/无名指交替|Tipiano/捕获样本的指形可辨，尚未取得对应指法和事件标签|带逐指标签的3↔4交接短段；教师标注主动/释放/准备阶段|
|连续上行/下行|Tipiano B大调音阶有可观察的整手移动|不能用当前抽样分别认证全部上行与下行；应查看完整带标签双向序列|
|掌腕协同|起始、中段布局不同，既有横向位移又有掌部朝向变化|真实腕/前臂动力学、动作经济性与教学规范需教师判断|
|闲置指|能看到自然接近及不同弯曲，FürElise id100还有闲置手等待|“自然”是观察意见；不能证明全部闲置指避开实际键体|
|黑键|俯视可看到黑键区及手指组织|需要原侧斜画面/实际接触数据，不能以绿色键作物理证据|
|准备/持键/释放|暂停点可见任务前后手形变化|未完成NOTE_ON/OFF级视觉对应，三阶段正确性UNKNOWN|

## 论文主张与视觉观察分开

Tipiano官网的接触F1、专家评价、手腕增强和生物力学投影是作者报告，不是本轮重测；本轮只见到上述官方样例。FürElise数据卡/论文说明真实捕获及后处理，也不意味着每个数据动作是无瑕疵教师示范。PianoMotion原数据视频展示的是人类参考，与“Generated Hand Motion”是两个栏目，不能把前者的真实自然度算给模型。

官方对照页中四路视频长度不完全一致（id23约8.4–8.57s）；本轮不作其样本精确同步评分。网页0.5×可播放，但本轮主要使用有限静帧定位，不声称完成连续半速/四分之一速教学验收。

## Human方便打开的入口

1. [Tipiano交互对照](https://tipiano.io/benchmark)：选Scales Technical Lv.3，Top，放大Tipiano；不要把Auto栏当指定指法的结果。
2. [Tipiano本轮观察的官方Top视频](https://tipiano.io/video/Tipiano/23/23_Top.mp4)：约2秒和4秒可见整手位置变化。
3. [PianoMotion生成样例](https://agnjason.github.io/PianoMotion-page/static/videos/sample_out_1.mp4)：缺键盘，适合看姿态，不适合验触键。
4. [FürElise捕获数据短样例](https://for-elise.github.io/static_visualizer/vis.html?id=100)：Camera Presets选top；约2.40s、6.60s。
5. [FürElise官网](https://for-elise.github.io/)的Synthesized Results与Overview：本轮未逐段完成这些生成视频的视觉审核，结论UNKNOWN。

STOP — HUMAN REVIEW。
''')
doc('BLENDER_INTEGRATION_FEASIBILITY.md',f'''# 与现有Blender资产的兼容性分析

本轮仅读取必要接口文件与数据结构，没有启动Blender、修改Action、解码MANO资产或生成候选。**可以保留现有Rig、Mesh、权重、88键几何与已批准静态姿态**；可接收外部轨迹不代表无需重定向。

## 已有接口

`audits/midi_driven_dual_hand_piano_performance_poc_r1/performance_core.py` 的 `SETUPS`、`joint_mats`、`fk`、`bounds`：每指三个可驱动关节加MCP横展的4个工程坐标；每手五指。非拇指MCP/PIP/DIP flex范围0–75/95/65°，横展±28°；拇指命名是CMC/MCP/IP而非直接照搬MANO三个名称。真实骨架/轴来自 `RIG_CANONICAL_PROBE_R1.json`。

|21点语义|现有骨架接口|
|---|---|
|wrist|WRIST_R/WRIST_L及其已有root对象；须区分global/root运动与骨骼local旋转|
|食/中/无名/小指MCP/PIP/DIP/tip|对应 DIGIT_MCP/PIP/DIP/TIP_R或_L|
|拇指三个关节与tip|THUMB_CMC/MCP/IP/TIP_R或_L；按语义匹配，不能按数组序号盲拷|
|掌部朝向|由腕及MCP基部共同约束；21点不包含完整掌面或前臂，需要从本Rig几何恢复|

已有动作以 `pose.bones[...].rotation_quaternion` 的骨架local basis烘焙，root另有轨迹。现有事件表包含hand、finger、midi_note、key_index、NOTE_ON/OFF，key_index=MIDI−21。钢琴X沿键盘、Y沿键深、Z向上，白键和F♯5黑键在未按下时键面高度差约15.444mm。源表有真实playable surface分片、键轴与press angle，接触目标必须使用随原Action运动的键面。

## 三种输出的接入难度

|输出|可以怎样用|必要转换与风险|
|---|---|---|
|Tipiano 每手21×3点|作为腕/指尖/中间关节的目标轨迹，拟合现有骨骼|不是现成local rotation；缺少轴向twist信息。原论文的MANO拟合也不是本Rig动作转换器。当前缺源码/权重|
|PianoMotion MANO全局姿态+45维轴角|先恢复语义关节/参考旋转，再转换到本Rig或拟合|[输出渲染代码]({GH}datasets/show.py#L91)在相机/渲染坐标内，左手镜像右模型。不能直接把45个数字填入本Rig旋转或手工改符号|
|FürElise joints与global_rotation|短段参考轨迹可绕开运行MANO网格解码，作为运动先验|数据本身仍受NC许可；21点无完整twist。卡片pose维度/编码有待实际小包核查，优先使用joints而不是猜pose编码|
|FürElise物理策略输出|需要先取得公开实现，再把控制结果转换成现有动画|论文仿真手17 links/27DoF与本Rig不一致；不是直接可接骨架API，现阶段不建议此路线|

## 坐标、旋转与骨长：建议的后续转换合同

以下是**工程设计建议，不是已实现的代码**。

1. 先以几何语义确认单位、轴方向、左右手标识、关节顺序与源键盘尺度，至少用多个键中心及键面标定，禁止凭相机图猜世界坐标。
2. 使用 `p_target = s R p_source + t`，R必须是合法旋转，左右镜像单独记录。Tipiano v1声明X朝演奏者、Y沿键盘、Z为高度；在方向一致的条件下，候选映射可为 `(X_t,Y_t,Z_t)=(Y_s,-X_s,Z_s)`，但必须用实数据确认正向，不能只交换X/Y造成反射。
3. 重定向保留目标Rig的rest骨长和轴，源人手比例不能改变冻结Mesh。单段骨方向能给bend方向，不能唯一给twist；补充掌面朝向、上一帧旋转和当前工程关节域，再得到local basis quaternion。
4. 如果用源旋转，先区分global与relative：`R_child_rel = R_parent_global^-1 R_child_global`，再进行rest轴变换；不能把世界旋转直接作为Blender matrix_basis。MCP多个自由度也须投影到现有工程域。
5. 原NOTE_ON/OFF仍是时间权威。59.94fps与30fps轨迹按真实时间重采样至60/120Hz；不得按相同帧序号直接对齐。保持0.35s视频lead和原琴键/音频Action，用事件边界约束插值，尤其NOTE_OFF后的释放不能继续按持键处理。

## 正确触键、穿指与穿键会不会重新出现？

会有重新出现的风险。来源可包括骨长比例、pad与关节tip的差异、MANO世界系到本Rig local basis转换、左右反射、关节域投影、59.94→60fps插值及滤波。源21点合法也不保证目标skin无相交；原模型中指尖刚好触键，也可能在本Rig中成为悬空或指侧穿黑键。

因此未来小实验应以**现有实际skin、运动键面和原俯视相机**验收，测目标键、pad接触与独立指形，并保留侧斜检查。学习先验应指导整手布局/关节协同，精确MIDI接触约束负责功能；避免最后用大幅局部修正把学到的掌腕协调破坏掉。这是研究推论，不是任何项目已有的无碰撞保证。

## 动态root与冻结资产不是同一件事

保留冻结骨架/网格/静态姿态可以同时在**未来另行授权的派生动作**中验证短段root/腕轨迹变化。上一轮固定root的限制不应被无条件带入新路线，因为本次研究目的正是判断整手协同是否需要改变。不过目前批准的root和左手Action仍为参考资产，本轮无任何变更。

专业指法DESIGN_PROVISIONAL。新实验首先需要教师确认指定3–4–3–4–5是否适合此速度与上下文；本报告不修改指法，也不承诺可以在固定root下完成。

本机Windows、RTX3060 12GiB、系统Python3.12.1已只读核实；推理依赖应将来隔离，不能装进现有Blender运行时。本轮没有环境安装、权重下载或原型接入。

STOP — HUMAN REVIEW。
''')
doc('B02_TECHNICAL_OPTIONS.md','''# B02：最多三条有依据的替代路线

关键序列保持：C5(3)→D5(4)→E5(3)→F♯5(4)→G5(5)，DESIGN_PROVISIONAL。D5结束于视频3.778568s，E5开始于同一交接附近；3.825s中指主动E5、无名指已释放D5并准备F♯5。事件阶段来自既有时间表，不重新审计历史候选。

## 成因应怎样解释

**已知事实**：现有指尖事件及目标映射正确，但关节/skin路径穿插；此前固定root、只改局部关节没有获得足够可见改善。此前表现不能证明指法错误，也不能证明必须采用某一种AI模型。

**工程推论**：同一手形中3指/4指相对位置与目标键次序存在约束。4指先去D5、随后3指去更右的E5，可能需要预先改变手的整体位置、掌部朝向或关节耦合，给4指释放留路径；仅把无名指抬高/外展容易与F♯5准备或邻近D♯5实体冲突。具体平移量、腕旋转方向及动作是否适于教学不能凭两音推断，需要教师演示和几何验证。

**专业待确认**：3–4–3–4–5是否是此曲段/速度/手型的合理教学指法？是否意图换手位？在D5释放到E5进入时，掌腕与两指应怎样协调？不能在本轮把它替换为其他指法，也不能据“看起来奇怪”判它错误。

## 路线对照

|路线|生成阶段如何针对B02|适用前提|主要风险|最小验证|状态|
|---|---|---|---|---|---|
|1. 教师核准短段真实先验＋掌腕/指尖联合重定向|以真实整手位移/掌向及3↔4释放为先验，原MIDI与当前目标键保持；不是只在碰撞后抬某一指|教师先确认候选指法；取得权利清楚且有腕/关节/事件的短样本。FürElise可提供研究参照，自有/另授权样本用于产品路线|换人手比例、腕轨迹和tip/pad差异会重新碰撞；研究数据许可不能自动用于商用|只覆盖约3.25–4.75s五音，先检查源动作与指定指序一致，再在派生副本比较俯视/侧斜触键和释放；不训练全模型|READY_FOR_ISOLATED_POC（实验设计就绪，**样本与教师确认是执行前置条件**）；FürElise未授权商业版BLOCKED|
|2. Tipiano可控级联的指尖锚点→腕→中间关节|从给定指法和键位提前组织整手；时序上下文学习耦合，避免只独立解每指|公开可控推理代码、完整权重/先验、标签与许可；需要本Rig输出适配|官方当前尚未释放可核实代码包；准备动作仍是论文/官网指出的不足；最终拟合可能改变接触|先在官方可控实现上给同一五音/指法，检查其是否真的接受该约束及原生输出，之后才考虑重定向；若未发布就不重写全系统|RESEARCH_ONLY；直接执行BLOCKED|
|3. 真实先验＋MIDI目标的物理联合控制（FürElise思路）|在训练/控制阶段同时约束整手、键实体和任务，物理反馈可排除一部分不可行交互|公开完整算法/模型、仿真域和合法训练数据；如要固定指法，还需明确接口或额外约束|代码未核实开放，原仿真手与本Rig不同，逐曲1–3天策略训练；音乐成功不自动等于教师自然度|第一步仅做发布/许可和仿真输出合同确认；无实现不启动训练，也不以重新制作Hands/Piano为前提|BLOCKED，当前成本不适于最小实验|

技术依据：[Tipiano层级与中间关节方法§4](https://arxiv.org/html/2604.09692v1)、[FürElise捕获/检索/物理控制§3–5](https://arxiv.org/html/2410.05791v1)、[数据结构和许可](https://huggingface.co/datasets/rcwang/for_elise)、[两项目实际官方俯视入口](https://tipiano.io/benchmark)。方案1是基于这些事实的**新验证设计**，不是声称现成检索代码已经提供了这条指定指序。

PianoMotion10M不列为第四条B02路线：当前音频条件没有指定指法/精确键接触的控制接口，直接把其输出替换当前轨迹可能让映射退步。可以将来用作独立风格比较，但要变成指定MIDI/指法生成器属于额外研发，不能把源码公开当作已支持。

## 对路线1的未来验收合同（本轮不执行）

1. 教师确认这一五音指序，指出D5释放、E5进入与F♯5预备的整手关系。若教师不接受，记录并回到指法讨论，不擅自换指。
2. 只用一个合法短段先验，记录源关节、腕、事件/指法、坐标、帧率与许可；没有逐指标签的音阶视频不能代替这份样本。
3. 在独立派生副本保持23音整体事件与原琴键/音频，短段允许教师认可的root/腕协同；本Rig/皮肤/冻结静态姿态不变。这样才真正检验“掌腕自由度”假设。
4. 只生成一次限定窗口实验，并检验当前实际运动键面和skin、关节域、事件边界连续性；相机沿用原俯视，0.5×/0.25×及暂停时两指可辨且不穿插。F♯5预备也必须无黑键嵌入。
5. 若原生先验已正确而重定向失败，可定位为转换问题；若原生先验/指序就不合格，不继续靠末端局部修补扩展范围。

这不是现在的执行授权。STOP — HUMAN REVIEW。
''')
doc('FINAL_RECOMMENDATION.md','''# 最终技术路线建议 R1

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
''')
doc('EVIDENCE_INDEX.md',f'''# 证据索引

核查日2026-10-11；官方来源优先。报告中的结论分成论文/作者描述、静态事实、实际画面、研究推论和UNKNOWN。

|编号|官方来源|本地证据/说明|
|---|---|---|
|T1|https://tipiano.io/|tipiano_live_page_snapshot.txt / tipiano_release_status.png；动态官网，Code+Dataset TBD|
|T2|https://arxiv.org/html/2604.09692v1|§4输入/级联/输出，§5训练与评价；不把网站增强内容当已发布代码|
|T3|https://tipiano.io/benchmark|实际Top样例id23；完整媒体URL写在视觉报告|
|P1|https://github.com/agnJason/PianoMotion10M|源码提交 `{commit}`，pianomotion_tree.json|
|P2|https://huggingface.co/agnJason/PianoMotion_models/tree/main|revision de146178457a4f4d262f4f4492597d5fdf76dd23；info/tree和两份配置，未下载ckpt|
|P3|https://agnjason.github.io/PianoMotion-page/|官方生成与数据视频不同；版权NC说明|
|P4|https://arxiv.org/html/2406.09326v2|方法/附录限制；原数据来源为网络俯视演奏视频|
|F1|https://for-elise.github.io/|Code (To be released)；捕获与生成分支分开|
|F2|https://arxiv.org/html/2410.05791v1|§3捕获/后处理，§4联合生成与控制，§5.1训练成本|
|F3|https://huggingface.co/datasets/rcwang/for_elise|revision ea14b581cbc33d8f2d0aca8e609e3e5c62423e50；数据卡/树/下载脚本/查看器，未获取dataset.zip|
|F4|https://for-elise.github.io/static_visualizer/vis.html?id=100|实际短段截图、metadata；motion.json只读两行结构，坐标未保存|
|L1|https://mano.is.tue.mpg.de/license.html|默认非商业及商业许可渠道，mano_license.html|
|L2|{GH}LICENSE|Apache-2.0仅证明代码层|
|L3|https://creativecommons.org/licenses/by-nc/4.0/|数据NC含义，不能推出商业研发自动获准|
|D1|https://github.com/state-spaces/mamba#installation|Linux要求；当前源码无条件导入Mamba|
|D2|https://huggingface.co/facebook/hubert-base-ls960|第三方音频权重本版本Apache-2.0|

下载记录：SOURCE_FETCH_MANIFEST.json、FOLLOWUP_FETCH_MANIFEST.json；均为小型公共文本/JSON，单项上限512KiB；源码以`.txt`保存而未执行。STATIC_CODE_CHECK.json只做AST语法分析，不是运行成功证据。SMALL_SAMPLE_ACCESS_CHECK.json保存少量预览字段形状，未保存mesh坐标。网页演示由浏览器播放，未下载/另存原视频。

LOCAL_INPUT_HASHES.json记录六个必要接口/时间表/源候选文件的哈希。未重新检查7936个历史文件，未作全项目历史审计。操作写入范围仅本研究目录；选定输入终检见RESEARCH_STATUS.json，不宣称这等于重新认证全部历史资产。
''')
inputs=json.loads((P/'LOCAL_INPUT_HASHES.json').read_text(encoding='utf8'))
changed=[str(f) for f,h in inputs.items() if hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h]
assert not changed
status=dict(task='PIANO_HAND_MOTION_TECHNOLOGY_RESEARCH_R1',checked_date='2026-10-11',reports_created=5,read_only_research=True,models_run=0,weights_downloaded=0,large_datasets_downloaded=0,new_dynamic_candidates=0,actions_or_blends_modified=0,new_dependencies_installed=0,local_reference_hashes_checked=len(inputs),changed_local_references=changed,source_commit=commit,preferred_algorithm='Tipiano controllable cascade; release blocked',preferred_next_experiment='Teacher-confirmed and rights-cleared short real-motion prior plus wrist/contact-aware retargeting',visual_review='Limited official samples/stills only; no full pedagogical approval',human_approval_required_for_next_stage=True,final_status='RESEARCH_COMPLETE / HUMAN_REVIEW',stop='HUMAN REVIEW')
(P/'RESEARCH_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
print('FIVE_REPORTS_CREATED; INPUT_HASHES_UNCHANGED; STOP_HUMAN_REVIEW')
