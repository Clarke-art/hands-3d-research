# 官方演示教学观察 R1

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
