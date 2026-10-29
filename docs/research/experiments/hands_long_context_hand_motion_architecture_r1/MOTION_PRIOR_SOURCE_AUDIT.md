# 钢琴动作先验源码、资产与许可审计

DESIGN_PROVISIONAL — STOP — HUMAN REVIEW
核查日期：2026-10-13，Asia/Shanghai。原始小型文本、固定提交、SHA256、HTTP错误保存在 sources/SOURCE_INDEX.json；共50条获取记录。未下载大型数据集、模型权重，未运行外部代码、训练或调用付费API。

结论：在本轮核查的候选中，没有同时完成商业许可、本地可运行和冻结Rig适配验证的直接动作先验。确有与钢琴相关的真实观测/重建资产，不能把“未找到产品可用全链”说成世界上不存在数据。数据、源码、权重和第三方人体模型权利分别审查。

|来源|动作性质/格式|源码|数据/权重许可|当前决策|
|---|---|---|---|---|
|FürElise|多视角真实演奏视频重建；59.94Hz双手21点、MANO、同步MIDI的motion.pkl|数据可视化公开；完整生成器官方仍待发布|数据CC BY-NC4.0；生成权重未核实|研究资料；不导入商业产品|
|PianoMotion10M|单目视频估计MANO；JSON左右手/fps，音频与MIDI；加载器30Hz|Apache2.0代码，固定86539e5a16d1|数据NC；HF权重无独立已核验许可|源码可评估，整体产品输入未获资格|
|Tipiano|MIDI＋指法→双手21点；当前官网/论文分阶段版本不同|官网Code+Dataset按钮禁用TBD|公开生成代码、权重、标签许可未取得|方法依据，不能宣称真实后端已接入|
|PianoVAM|Disklavier同步视频/音频/MIDI，MediaPipe估计点与指法标签|ASDF源码已读|仓库README为BY-NC；HF元数据为BY-NC-SA，差异保留；均NC|数据/源码商用不授予|
|PianoMime|视频平面单应性提取指尖/指法；Zarr机器人state212/action184|教程与IK实际已读；README声称MIT但树中未找到项目级LICENSE|演示/派生数据与权重单独授权未核实|技术参考，不作人体完整3D动作资产|
|RoboPianist|MuJoCo仿真机器人、未来MIDI目标|Apache2.0主代码，模型/数据另行|PIG另取且不可在仓库重分发；不属于人体动作数据|复用接口思想，不直接重定向策略|
|SKY-Piano|直接光学120Hz手/身体、同步MIDI、带不可靠/补全标记与伪指法|官网链接仓库经GitHub API与网页均404|只有每模态授权声明，实际动作商业条款未取得|新增重点资料；本轮未取得可接入资产|

FürElise的数据卡说明结构与NC限制，3D来自多视角重建和IK修正，不是直接光学骨架或本Rig控制。21点可以作为未来重定向目标，但不解决指腹/指尖差异、骨长、坐标和twist。[数据卡](https://huggingface.co/datasets/rcwang/for_elise)、[官方采集方法](https://for-elise.github.io/)。

PianoMotion实读infer.py，输入经PianoPose数据加载器组织，预测音频引导MANO姿态并默认CUDA渲染；不是已有的指定C01指法/NOTE_ON/OFF硬约束入口。代码Apache不自动赋予数据或ckpt商用权利。[固定源码](https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/infer.py)、[作者数据许可声明](https://openreview.net/pdf?id=rxVvRBgqmS)、[权重卡](https://huggingface.co/agnJason/PianoMotion_models)。

Tipiano的MIDI/指法层次接口值得参考，官方发布按钮仍禁用；网页React/MIT库说明与算法/模型许可不同。不能用官网效果或21点F1代替真实皮肤接触验收。[官网](https://tipiano.io/)、[论文v1](https://arxiv.org/html/2604.09692v1)。

PianoVAM README明确限制数据及代码；HF卡元数据存在NC-SA与NC的差异，不能用论文正文的CC BY文章许可替代数据许可。也不能把MediaPipe深度当作可靠标定三维骨骼。[仓库许可段](https://github.com/yonghyunk1m/PianoVAM-Code/blob/ae4560fb5971590dd790fcefb14b90611585ddd9/README.md)、[数据卡元数据](https://huggingface.co/api/datasets/PianoVAM/PianoVAM)。

PianoMime真实教程从视频平面提取指尖，当前控制器使用ShadowHand骨架/索引；来源视频、派生数据、checkpoint均需独立授权。MIT声明的正式许可文件缺口保留。[仓库](https://github.com/sNiper-Qian/pianomime/tree/c4abefac8d2941f5a08ca656b12f5e047cab7155)。SKY-Piano包含更合适的直接测量手部数据，但伪指法、不可靠点与指甲marker到指腹的偏差仍要处理；官网所链仓库无法访问，模态商业许可没有证明。[官网](https://joonhyungbae.github.io/skypiano/)、[论文](https://arxiv.org/html/2607.27296v1)。

MANO本体的默认条款为非商业研究，并单列商业许可申请；不能由上层开源代码牌照推断其模型链可商用。本轮未下载MANO模型。[原始条款](https://mano.is.tue.mpg.de/license.html)。NC含义核对官方法律文本：[CC BY-NC4.0](https://creativecommons.org/licenses/by-nc/4.0/legalcode.en)。

当前Rig有20个手指工程坐标＋6根控制，受授权参考族映射；外部21点、MANO45参数或机器人state/action都不能直接拷贝。未来最小资产入口应明确来源授权、双手关节语义、坐标单位/键盘标定、时钟同步、指法可信度及缺失点，再做原骨长/轴/指腹适配，最后走既有88键/自交/接触门禁。未核实许可资产只作资料评估。实际候选的证据类别是PROGRAMMATIC_GEOMETRY_HYPOTHESIS，没有数据推导人体规律，也没有模型生成。
